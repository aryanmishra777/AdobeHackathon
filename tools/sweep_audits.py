#!/usr/bin/env python3
"""Audit every snapshot end to end and collect what the bench does not.

    python tools/sweep_audits.py                 # every bench/snapshots/*
    python tools/sweep_audits.py --only vox,bbc  # substring filter

The bench answers "did the expected checks fire?". This answers the questions
that only surface when a full report is assembled for a real site:

  * does report.json validate against its own schema, for every site?
  * did any analyzer crash, and on what?
  * which model-judged candidates were raised, so a person can triage them in
    bulk -- that review is where a quarter of vox.com's candidates were dropped
  * which checks fire on one or two pages under a site-level title?
  * which findings' evidence still contains a placeholder or a template token?

It reuses tools/run_audit.py per site, so it exercises exactly the path a
scripts-only run takes, then aggregates. Output: .audit/sweep/<site>/ per site
and .audit/sweep/SUMMARY.md for the person.
"""
from __future__ import annotations

import argparse
import collections
import glob
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SNAPSHOTS = os.path.join(REPO, "bench", "snapshots")
RUN_AUDIT = os.path.join(HERE, "run_audit.py")
VALIDATE = os.path.join(REPO, "brand-ai-readiness-audit", "skills", "audit-orchestrator",
                        "scripts", "validate_report.py")

PLACEHOLDER = re.compile(r"\{[a-z_]+\}|<[a-z_ ]+>|TODO|FIXME|lorem ipsum|example\.com", re.I)
SITE_LEVEL_WORDS = re.compile(r"\b(the site|site-wide|every page|all pages|no page|nowhere)\b", re.I)


def run(*args):
    return subprocess.run([sys.executable, *args], capture_output=True,
                          text=True, encoding="utf-8")


def audit_one(snapshot: str, out_dir: str) -> dict:
    name = os.path.basename(snapshot)
    manifest = json.load(io.open(os.path.join(snapshot, "MANIFEST.json"), encoding="utf-8"))
    origin = (manifest.get("run") or {}).get("origin") or f"https://{name}"
    started = time.time()
    proc = run(RUN_AUDIT, origin, "--bundle", snapshot, "--out", out_dir)
    elapsed = round(time.time() - started, 1)
    row = {"site": name, "seconds": elapsed, "rc": proc.returncode,
           "analyzer_failures": re.findall(r"^\s+(\S+) FAILED: (.*)$", proc.stderr, re.M)}
    report_path = os.path.join(out_dir, "report.json")
    if not os.path.exists(report_path):
        row["error"] = (proc.stderr or "")[-400:]
        return row
    v = run(VALIDATE, report_path)
    row["valid"] = v.returncode == 0
    row["validation"] = [l for l in (v.stdout + v.stderr).splitlines()
                         if l.startswith(("error", "warning"))]
    rep = json.load(io.open(report_path, encoding="utf-8"))
    row["summary"] = rep.get("summary")
    row["scorecard"] = {k: (v_.get("score"), v_.get("grade"))
                        for k, v_ in (rep.get("scorecard") or {}).items() if isinstance(v_, dict)}
    row["pages"] = (rep.get("coverage") or {}).get("pages_sampled")
    row["findings"] = [{
        "id": f.get("id"), "check_id": f.get("check_id"), "severity": f.get("severity"),
        "confidence": f.get("confidence"), "determinism": f.get("determinism"),
        "title": f.get("title"), "evidence": (f.get("evidence") or "")[:300],
        "pages_affected": len((f.get("evidence_detail") or {}).get("pages_affected") or []),
        "scope": (f.get("affected_scope") or {}).get("scope"),
    } for f in rep.get("findings") or []]
    return row


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", default="", help="comma-separated substrings of site names")
    ap.add_argument("--out", default=os.path.join(REPO, ".audit", "sweep"))
    args = ap.parse_args(argv)

    snaps = sorted(d for d in glob.glob(os.path.join(SNAPSHOTS, "*"))
                   if os.path.exists(os.path.join(d, "MANIFEST.json")))
    if args.only:
        keys = [k.strip() for k in args.only.split(",") if k.strip()]
        snaps = [d for d in snaps if any(k in os.path.basename(d) for k in keys)]
    os.makedirs(args.out, exist_ok=True)

    rows = []
    for i, snap in enumerate(snaps, 1):
        name = os.path.basename(snap)
        print(f"[{i}/{len(snaps)}] {name}", file=sys.stderr, flush=True)
        row = audit_one(snap, os.path.join(args.out, name))
        rows.append(row)
        status = ("ERROR " + row["error"][:60]) if "error" in row else (
            f"{'valid' if row.get('valid') else 'INVALID'}  "
            f"{(row.get('summary') or {}).get('total_findings', '?')} findings  "
            f"{row['seconds']}s")
        print(f"    {status}", file=sys.stderr, flush=True)

    io.open(os.path.join(args.out, "sweep.json"), "w", encoding="utf-8").write(
        json.dumps(rows, indent=1, ensure_ascii=False))

    # ---- aggregate -------------------------------------------------------
    invalid = [r for r in rows if not r.get("valid")]
    crashed = [r for r in rows if r.get("analyzer_failures") or "error" in r]
    by_check = collections.Counter()
    sev_by_check = collections.defaultdict(collections.Counter)
    model_judged = []
    thin_site_level = []
    placeholders = []
    for r in rows:
        for f in r.get("findings") or []:
            by_check[f["check_id"]] += 1
            sev_by_check[f["check_id"]][f["severity"]] += 1
            if f.get("determinism") == "model-judged":
                model_judged.append((r["site"], f))
            if f["pages_affected"] <= 2 and (r.get("pages") or 0) >= 10 \
                    and SITE_LEVEL_WORDS.search(f["title"] or ""):
                thin_site_level.append((r["site"], f))
            if PLACEHOLDER.search(f["evidence"] or ""):
                placeholders.append((r["site"], f))

    lines = ["# Sweep summary", "",
             f"sites audited: {len(rows)}   valid reports: {len(rows) - len(invalid)}   "
             f"invalid: {len(invalid)}   crashes: {len(crashed)}", ""]
    if invalid:
        lines += ["## Reports that fail their own schema", ""]
        for r in invalid:
            lines.append(f"- **{r['site']}**")
            for l in (r.get("validation") or [])[:6]:
                lines.append(f"  - {l}")
        lines.append("")
    if crashed:
        lines += ["## Analyzer crashes", ""]
        for r in crashed:
            for skill, msg in r.get("analyzer_failures") or []:
                lines.append(f"- {r['site']} / {skill}: {msg[:160]}")
            if "error" in r:
                lines.append(f"- {r['site']}: {r['error'][:160]}")
        lines.append("")
    lines += ["## Checks by frequency (post-merge)", "",
              "| check | sites | severity split |", "|---|---|---|"]
    for cid, n in by_check.most_common():
        lines.append(f"| {cid} | {n} | {dict(sev_by_check[cid])} |")
    lines.append("")
    if thin_site_level:
        lines += ["## Site-level titles resting on one or two pages", "",
                  "A title that says 'the site' or 'no page' over <=2 affected pages in a "
                  "sample of >=10 overclaims. Either the check needs a floor or the title "
                  "needs to name the page.", ""]
        seen = collections.Counter(f["check_id"] for _, f in thin_site_level)
        for cid, n in seen.most_common():
            ex = next(f for s, f in thin_site_level if f["check_id"] == cid)
            lines.append(f"- **{cid}** x{n} -- \"{ex['title']}\"")
        lines.append("")
    if placeholders:
        lines += ["## Evidence containing a placeholder or template token", ""]
        for site, f in placeholders[:20]:
            lines.append(f"- {site} {f['check_id']}: {f['evidence'][:120]}")
        lines.append("")
    lines += [f"## Model-judged candidates to triage ({len(model_judged)})", "",
              "Grouped by check. These are the ones an agent must confirm or drop; "
              "on vox.com the agent dropped 5 of 7.", ""]
    grouped = collections.defaultdict(list)
    for site, f in model_judged:
        grouped[f["check_id"]].append((site, f))
    for cid, items in sorted(grouped.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"### {cid} ({len(items)})")
        for site, f in items[:6]:
            lines.append(f"- {site} `{f['severity']}/{f['confidence']}` -- {f['evidence'][:170]}")
        if len(items) > 6:
            lines.append(f"- ... and {len(items) - 6} more")
        lines.append("")
    io.open(os.path.join(args.out, "SUMMARY.md"), "w", encoding="utf-8", newline="\n").write(
        "\n".join(lines))
    print(f"\nsummary -> {os.path.join(args.out, 'SUMMARY.md')}", file=sys.stderr)
    return 1 if invalid or crashed else 0


if __name__ == "__main__":
    raise SystemExit(main())
