#!/usr/bin/env python3
"""Run the whole pipeline end to end and write a report.

    python tools/run_audit.py https://example.com --out .audit/example

This is a DEVELOPMENT harness, not the product. The product is the marketplace:
an agent reads `audit-orchestrator/SKILL.md`, follows it, and does the parts that
need judgment. This script does everything a script can do -- collect, run the
six analysers, merge, score, validate, render -- and stops there.

So it deliberately does NOT:

  * complete model-judged checks (READ-004/006/011, PARSE-007, several QUOTE and
    STAY checks). The scripts emit their signals; an agent finishes them. Those
    findings will be missing or thin here.
  * run the off-site checks (TRUST-006/007/009/012/013), which need a search
    tool the orchestrator's SKILL.md tells the agent how to use.
  * detect the site profile, which the orchestrator does before dispatching.

Everything it skips is recorded in the report's `coverage`, so the output never
implies it is a complete audit. Use it to see the shape of a report, to check
the contract end to end, and to catch problems the fixtures cannot.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SKILLS = os.path.join(REPO, "brand-ai-readiness-audit", "skills")

COLLECT = os.path.join(SKILLS, "site-evidence-collector", "scripts", "collect.py")
MERGE = os.path.join(SKILLS, "audit-orchestrator", "scripts", "merge_findings.py")
VALIDATE = os.path.join(SKILLS, "audit-orchestrator", "scripts", "validate_report.py")
SUBSKILLS = os.path.join(SKILLS, "audit-orchestrator", "references", "subskills.json")

# The hard ceiling from the handout is five minutes per site. We stop at 270s
# so that a slow last request or a slow disk can never push a run over it.
AUDIT_CAP_SECONDS = 270.0
# Collection may use up to this share of the cap; the rest is for analysis.
COLLECT_SHARE = 0.55
# Kept back for merge, scoring and rendering, which are fast but not free.
MERGE_RESERVE_SECONDS = 8.0

ANALYZERS = [
    ("reach", "crawl-access-audit", "check_access.py"),
    ("read", "render-extractability-audit", "check_render.py"),
    ("parse", "structured-data-audit", "check_structured_data.py"),
    ("quote", "answerability-audit", "check_answerability.py"),
    ("trust", "freshness-corroboration-audit", "check_trust.py"),
    ("stay", "engagement-audit", "check_engagement.py"),
]

MECHANISM_HEADINGS = [
    ("reach", "Can assistants get in?"),
    ("read", "Can they read the page?"),
    ("parse", "Can they parse facts out?"),
    ("quote", "Can they quote a clear fact?"),
    ("trust", "Will they trust and repeat it?"),
    ("stay", "Do visitors who arrive stay?"),
]


def run(*args, **kw):
    return subprocess.run([sys.executable, *args], capture_output=True,
                          text=True, encoding="utf-8", **kw)


def grade_line(scorecard: dict) -> str:
    d = scorecard.get("discoverability") or {}
    e = scorecard.get("engagement") or {}
    if d.get("score") is None:
        return "Discoverability was not assessed."
    if (d.get("score") or 0) < 55:
        return ("Assistants are substantially blocked from finding, reading or "
                "citing this site.")
    if (d.get("score") or 0) < 75:
        return ("Assistants can reach this site, but several things stop them "
                "quoting it accurately.")
    return "This site is largely readable and quotable by assistants."


def render_markdown(report: dict, engine_rows: list) -> str:
    site = report.get("site") or ""
    sc = report.get("scorecard") or {}
    summary = report.get("summary") or {}
    findings = report.get("findings") or []
    cov = report.get("coverage") or {}

    def cell(axis):
        a = sc.get(axis) or {}
        if a.get("score") is None:
            return "not assessed", "--"
        return a.get("grade", "?"), f"{a.get('score')}/100"

    dg, ds = cell("discoverability")
    eg, es = cell("engagement")

    # The orchestrator writes a verdict in the site's own terms; the score-band
    # line is only a fallback. Rendering the fallback over a written verdict put
    # "Assistants can reach this site" above a table showing three of them
    # blocked.
    verdict = sc.get("verdict") or grade_line(sc)
    out = [f"# AI-Readiness Audit — {site}", "", verdict, "",
           "| | Grade | Score |", "|---|---|---|",
           f"| **Discoverability** — can AI assistants find, trust and cite you? | {dg} | {ds} |",
           f"| **Engagement** — do visitors who arrive stay? | {eg} | {es} |", ""]

    out.append(f"**{summary.get('total_findings', 0)} findings:** "
               f"{summary.get('critical', 0)} critical · {summary.get('high', 0)} high · "
               f"{summary.get('medium', 0)} medium · {summary.get('low', 0)} low")
    out.append(f"Audited {report.get('audited_at', '')} · "
               f"{cov.get('pages_fetched', '?')} pages sampled")
    out.append("")

    if engine_rows:
        out += ["## Which assistants can reach you", "",
                "| Assistant | Status | What we measured |", "|---|---|---|"]
        for r in engine_rows:
            out.append(f"| {r['engine']} | **{r['state']}** | {r['detail']} |")
        out.append("")
        if any(r.get("training_agents_blocked") for r in engine_rows):
            out.append("> Blocked *training* crawlers are listed separately and are "
                       "not a defect: declining to be training data is a "
                       "content-licensing choice, and it does not affect whether "
                       "an assistant can answer a question about you today.")
            out.append("")

    plan = report.get("priority_plan") or []
    if plan:
        out += ["## Fix these first", ""]
        for step in plan[:5]:
            # Field names come from report.schema.json: rank + finding_ids. The
            # first draft of this renderer read a key called `fixes` that the
            # schema does not define, and rendered an empty plan from a valid
            # report -- caught only by assembling one the way the agent does.
            ids = ", ".join(step.get("finding_ids") or [])
            out.append(f"{step.get('rank', '?')}. **{step.get('action')}** — "
                       f"{step.get('why_first', '')}"
                       + (f" *(fixes {ids}; effort: {step.get('effort', '?')})*" if ids else ""))
        out.append("")

    if findings:
        out += ["## Findings", ""]
        for mech, heading in MECHANISM_HEADINGS:
            group = [f for f in findings if f.get("mechanism") == mech]
            if not group:
                continue  # never print an empty heading
            out += [f"### {heading}", ""]
            for f in group:
                out.append(f"#### {f.get('id')} · {f.get('title')}  `{f.get('severity')}`")
                out.append("")
                out.append(f"**What we found.** {f.get('evidence', '')}")
                out.append("")
                act = f.get("suggested_action") or {}
                if act.get("impact_rationale"):
                    out.append(f"**Why it matters.** {act['impact_rationale']}")
                    out.append("")
                if act.get("summary"):
                    out.append(f"**Fix.** {act['summary']}")
                    for step in (act.get("steps") or []):
                        out.append(f"- {step}")
                    out.append("")
                if f.get("verification"):
                    out.append(f"**Check it yourself.** `{f['verification']}`")
                    out.append("")
                if f.get("superseded_by"):
                    out.append(f"*Downstream of {', '.join(f['superseded_by'])} — "
                               f"fixing that may resolve this.*")
                    out.append("")

    pro = report.get("proactive_recommendations") or []
    if pro:
        out += ["## Worth doing even though nothing is broken", ""]
        for p in pro:
            out.append(f"- **{p.get('title')}** — {p.get('rationale', '')}")
        out.append("")

    lim = cov.get("limitations") or []
    skipped = cov.get("checks_skipped") or []
    out += ["## What this audit did not cover", ""]
    for l in lim:
        out.append(f"- {l}")
    if skipped:
        names = sorted({(s.get("check_id") if isinstance(s, dict) else s) for s in skipped})
        # Skips carry their own reasons in report.json; a site that refused every
        # fetch skips 90 checks for want of a page, not for want of a search tool.
        shown = ", ".join(names[:12]) + (f" and {len(names) - 12} more" if len(names) > 12 else "")
        out.append(f"- {len(names)} checks did not run; each has its reason in "
                   f"report.json under coverage.checks_skipped: {shown}")
    out.append("- Whether an assistant retrieves anything at all, what third-party "
               "sources say, which competitors share the retrieval pool, and how "
               "each engine reranks are all outside a single-site crawl.")
    out.append("")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="URL or bare domain")
    ap.add_argument("--out", default=None, help="output directory")
    ap.add_argument("--max-pages", type=int, default=25)
    ap.add_argument("--budget", type=int, default=120)
    ap.add_argument("--bundle", default=None,
                    help="reuse an existing bundle instead of crawling")
    ap.add_argument("--cap", type=float, default=AUDIT_CAP_SECONDS,
                    help="hard wall-clock cap for the whole audit, in seconds")
    args = ap.parse_args(argv)

    # The whole audit -- collect, six analyzers, merge, render -- must finish
    # inside one hard cap, regardless of the site. Every script takes the same
    # absolute deadline and stops on its own; this harness also refuses to start
    # a stage that cannot finish. Whatever was cut is named in coverage.
    t0 = time.time()
    deadline = t0 + args.cap

    def remaining():
        return deadline - time.time()

    out_dir = args.out or os.path.join(REPO, ".audit", "run")
    os.makedirs(out_dir, exist_ok=True)
    bundle = args.bundle or os.path.join(out_dir, "bundle")

    if not args.bundle:
        print(f"collecting {args.target} ...", file=sys.stderr)
        started = time.time()
        # Collection may use at most COLLECT_SHARE of the cap so the analyzers
        # and the merge always have room; the collector shrinks to fit.
        proc = run(COLLECT, args.target, "--out", bundle,
                   "--max-pages", str(args.max_pages), "--budget", str(args.budget),
                   "--deadline", str(t0 + args.cap * COLLECT_SHARE))
        if proc.returncode != 0:
            print(proc.stderr[-2000:], file=sys.stderr)
            return 2
        print(f"  collected in {time.time() - started:.0f}s", file=sys.stderr)

    manifest = json.load(io.open(os.path.join(bundle, "MANIFEST.json"), encoding="utf-8"))
    pages = sum(1 for p in manifest.get("pages", []) if p.get("status") == 200)

    candidates, ran, skipped, engine_rows, proactive = [], [], [], [], []
    cut_stages, cut_checks = [], []
    for mech, skill, script in ANALYZERS:
        path = os.path.join(SKILLS, skill, "scripts", script)
        if remaining() < MERGE_RESERVE_SECONDS:
            cut_stages.append(mech)
            print(f"  {skill:<32} NOT RUN: {remaining():.0f}s left of the "
                  f"{args.cap:.0f}s cap", file=sys.stderr)
            continue
        proc = run(path, bundle, "--stdout",
                   "--deadline", str(deadline - MERGE_RESERVE_SECONDS))
        if proc.returncode != 0:
            print(f"  {skill} FAILED: {proc.stderr.strip()[:200]}", file=sys.stderr)
            continue
        doc = json.loads(proc.stdout or "{}")
        candidates.extend(doc.get("findings") or [])
        proactive.extend(doc.get("proactive_recommendations") or [])
        skipped.extend(doc.get("checks_skipped") or [])
        engine_rows.extend(doc.get("engine_reachability") or [])
        cut_checks.extend(doc.get("checks_cut_by_deadline") or [])
        ran.append(mech)
        print(f"  {skill:<32} {len(doc.get('findings') or [])} findings", file=sys.stderr)

    src = os.path.join(out_dir, "_candidates.json")
    io.open(src, "w", encoding="utf-8").write(json.dumps(candidates, ensure_ascii=False))
    proc = run(MERGE, src, "--pages-sampled", str(pages),
               "--mechanisms", ",".join(ran), "--supersession", SUBSKILLS, "--stdout")
    if proc.returncode != 0:
        print(proc.stderr[-2000:], file=sys.stderr)
        return 2
    merged = json.loads(proc.stdout)

    # The orchestrator writes these in prose; standing in for it, we compose
    # them from what was measured so the report satisfies its own schema.
    sc = merged["scorecard_input"]
    for axis, question in (("discoverability", "find, trust and cite you"),
                           ("engagement", "stay once they arrive")):
        a = sc.get(axis) or {}
        if a.get("score") is None:
            a["headline"] = ("Not assessed -- no analyzer ran for this axis, so "
                             "it is deliberately left ungraded.")
        elif axis == "engagement":
            # Engagement is measured from behaviour and we have no user present,
            # so this axis grades usability proxies for it. Say so in the
            # headline rather than letting the grade imply a measurement.
            a["headline"] = (f"{a['grade']} ({a['score']}/100) on usability "
                             f"proxies for engagement -- orientation, next "
                             f"steps, mobile readiness, load weight. Engagement "
                             f"itself is measured from visitor behaviour, which "
                             f"a site audit cannot see.")
        else:
            a["headline"] = (f"{a['grade']} ({a['score']}/100) for whether people "
                             f"and machines can {question}.")
    sc["verdict"] = grade_line(sc)

    for i, p_ in enumerate(proactive, 1):
        p_["id"] = f"P-{i:03d}"

    report = {
        "schema_version": "1.0",
        "site": (manifest.get("run") or {}).get("origin") or args.target,
        "audited_at": (manifest.get("run") or {}).get("started_at"),
        "summary": merged["summary"],
        "scorecard": merged["scorecard_input"],
        "findings": merged["findings"],
        "proactive_recommendations": proactive,
        "engine_reachability": engine_rows,
        "coverage": {
            "complete": False,
            "pages_sampled": pages,
            "pages_fetched": pages,
            "checks_skipped": skipped,
            "limitations": [
                "No browser renderer was available, so JavaScript dependency is "
                "inferred from raw HTML rather than measured.",
            ] + ([f"The audit's {args.cap:.0f}s wall-clock cap was reached: "
                  f"{len(cut_stages)} analysis stage(s) did not run ({', '.join(cut_stages)}) "
                  f"and {len(cut_checks)} check(s) were cut short "
                  f"({', '.join(cut_checks[:12])}{'...' if len(cut_checks) > 12 else ''}). "
                  f"Their mechanisms are not graded as clean; they were not examined."]
                 if (cut_stages or cut_checks) else []) + [
                "Model-judged checks were not completed: this run was scripts "
                "only, with no agent to finish them.",
                "The engagement axis grades usability proxies. Engagement is "
                "measured from visitor behaviour -- dwell time, return visits, "
                "scroll, clicks -- and a site audit has no visitor to observe.",
            ],
        },
        "run": {"tool": "tools/run_audit.py", "mechanisms_analyzed": ran,
                "wall_clock_seconds": round(time.time() - t0, 1),
                "cap_seconds": args.cap,
                "stages_cut_by_cap": cut_stages, "checks_cut_by_cap": cut_checks},
    }
    io.open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    io.open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8", newline="\n").write(
        render_markdown(report, engine_rows))

    proc = run(VALIDATE, os.path.join(out_dir, "report.json"))
    print(proc.stdout.strip() or proc.stderr.strip(), file=sys.stderr)

    print(f"\nreport.json + report.md -> {out_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
