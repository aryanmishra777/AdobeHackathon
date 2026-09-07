#!/usr/bin/env python3
"""Run the marketplace across the benchmark corpus and score the quadrant chart.

Dev tooling -- outside the submission. Requires PyYAML.

Three modes, matching the three-layer test strategy:

    python bench/run.py --live            # pinned 8-site smoke subset (dev loop)
    python bench/run.py --live --all      # all 40 sites (pre-submission)
    python bench/run.py --replay          # snapshotted bundles, deterministic
    python bench/run.py --snapshot        # refresh snapshots from live sites

Live sites drift, so `--live` results are a drift-tolerant scoreboard, never
assertions. Hard assertions belong in tests/ against local fixtures.

The output that matters is the quadrant chart: the good-SEO/poor-GEO row must
score materially worse on discoverability than good-SEO/good-GEO. Those are the
sites a conventional SEO tool passes clean. If we pass them too, the marketplace
has failed at the thing it exists to do.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import time
from urllib.parse import urlparse

try:
    import yaml
except ImportError:
    print("error: PyYAML required. pip install -r tools/requirements-dev.txt",
          file=sys.stderr)
    raise SystemExit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SKILLS = os.path.join(REPO, "brand-ai-readiness-audit", "skills")
SNAPSHOTS = os.path.join(HERE, "snapshots")
SCOREBOARD = os.path.join(HERE, "scoreboard")
CORPUS = os.path.join(HERE, "corpus.yaml")

COLLECT = os.path.join(SKILLS, "site-evidence-collector", "scripts", "collect.py")
MERGE = os.path.join(SKILLS, "audit-orchestrator", "scripts", "merge_findings.py")

# Only complete skills participate. Scaffold skills join as their scripts land.
ANALYZERS = [
    ("crawl-access-audit", "check_access.py"),
    ("render-extractability-audit", "check_render.py"),
    ("structured-data-audit", "check_structured_data.py"),
    ("answerability-audit", "check_answerability.py"),
    ("freshness-corroboration-audit", "check_trust.py"),
    ("engagement-audit", "check_engagement.py"),
]

QUADRANTS = [("good", "good"), ("good", "poor"), ("poor", "good"), ("poor", "poor")]

PREFIX_FOR = {
    "crawl-access-audit": "REACH",
    "render-extractability-audit": "READ",
    "structured-data-audit": "PARSE",
    "answerability-audit": "QUOTE",
    "freshness-corroboration-audit": "TRUST",
    "engagement-audit": "STAY",
}


def load_corpus(only_smoke: bool):
    doc = yaml.safe_load(io.open(CORPUS, encoding="utf-8"))
    sites = [s for s in (doc.get("sites") or []) if s.get("url")]
    if only_smoke:
        sites = [s for s in sites if s.get("smoke")]
    return sites


def slug(url: str) -> str:
    return urlparse(url).netloc.replace(":", "_") or url.replace("/", "_")


def available_analyzers():
    out = []
    for skill, script in ANALYZERS:
        path = os.path.join(SKILLS, skill, "scripts", script)
        if os.path.exists(path):
            out.append((skill, path))
    return out


def collect_live(site: dict, out_dir: str, max_pages: int, budget: int) -> bool:
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    proc = subprocess.run(
        [sys.executable, COLLECT, site["url"], "--out", out_dir,
         "--max-pages", str(max_pages), "--budget", str(budget),
         "--delay", "0.5", "--timeout", "10"],
        capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"    collect failed: {proc.stderr.strip()[:200]}", file=sys.stderr)
        return False
    return True


def analyze(bundle: str, tmp: str) -> tuple[list[dict], list[str]]:
    candidates, ran = [], []
    for skill, script in available_analyzers():
        out = os.path.join(tmp, f"{skill}.json")
        proc = subprocess.run([sys.executable, script, bundle, "--out", out],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"    {skill} failed: {proc.stderr.strip()[:160]}", file=sys.stderr)
            continue
        ran.append(skill)
        with io.open(out, encoding="utf-8") as fh:
            candidates.extend(json.load(fh).get("findings") or [])
    return candidates, ran


def merge(candidates: list[dict], pages: int, tmp: str) -> dict:
    if not candidates:
        return {"findings": [], "summary": {"total_findings": 0, "critical": 0,
                                            "high": 0, "medium": 0, "low": 0},
                "scorecard_input": {"discoverability": {"score": 100, "grade": "A"},
                                    "engagement": {"score": 100, "grade": "A"}}}
    src = os.path.join(tmp, "_all.json")
    with io.open(src, "w", encoding="utf-8") as fh:
        json.dump(candidates, fh)
    proc = subprocess.run([sys.executable, MERGE, src, "--pages-sampled", str(pages),
                           "--stdout"], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout)


def audit_one(site: dict, bundle: str, tmp: str) -> dict:
    manifest_path = os.path.join(bundle, "MANIFEST.json")
    if not os.path.exists(manifest_path):
        return {"url": site["url"], "error": "no bundle"}
    with io.open(manifest_path, encoding="utf-8") as fh:
        m = json.load(fh)
    pages = sum(1 for p in m.get("pages", []) if p.get("status") == 200)

    started = time.time()
    candidates, ran = analyze(bundle, tmp)
    merged = merge(candidates, pages, tmp)
    elapsed = time.time() - started

    fired = {f["check_id"] for f in merged["findings"]}
    expected = set(site.get("expect_findings") or [])
    forbidden = set(site.get("expect_absent") or [])

    # Only hold a check accountable when its owning skill actually ran. Counting
    # PARSE-001 as "missed" while structured-data-audit is still a scaffold buries
    # the real regressions under noise that is not a regression at all.
    live_prefixes = {PREFIX_FOR[s] for s in ran if s in PREFIX_FOR}
    expected = {c for c in expected if c.split("-")[0] in live_prefixes}
    forbidden = {c for c in forbidden if c.split("-")[0] in live_prefixes}
    not_yet = sorted(c for c in (site.get("expect_findings") or [])
                     if c.split("-")[0] not in live_prefixes)

    sc = merged["scorecard_input"]

    return {
        "url": site["url"], "seo": site.get("seo"), "geo": site.get("geo"),
        "engagement": site.get("engagement"), "site_type": site.get("site_type"),
        "pages": pages,
        "discoverability": sc["discoverability"]["score"],
        "disc_grade": sc["discoverability"]["grade"],
        "engagement_score": sc["engagement"]["score"],
        "eng_grade": sc["engagement"]["grade"],
        "summary": merged["summary"],
        "skills_run": ran,
        "misses": sorted(expected - fired),
        "not_yet_implemented": not_yet,
        "false_positives": sorted(forbidden & fired),
        "seconds": round(elapsed, 1),
        "findings": [{"check_id": f["check_id"], "severity": f["severity"],
                      "title": f["title"]} for f in merged["findings"]],
    }


def quadrant_chart(results: list[dict]) -> str:
    lines = ["", "QUADRANT CHART -- mean discoverability score by SEO x GEO", ""]
    lines.append(f"  {'quadrant':26} {'n':>3}  {'disc':>5}  {'eng':>5}  note")
    lines.append("  " + "-" * 66)
    means = {}
    for seo, geo in QUADRANTS:
        rows = [r for r in results
                if r.get("seo") == seo and r.get("geo") == geo and "error" not in r]
        label = f"SEO {seo:4} / GEO {geo:4}"
        if not rows:
            lines.append(f"  {label:26} {0:>3}  {'--':>5}  {'--':>5}  not yet populated")
            continue
        d = sum(r["discoverability"] for r in rows) / len(rows)
        e = sum(r["engagement_score"] for r in rows) / len(rows)
        means[(seo, geo)] = d
        note = ""
        if (seo, geo) == ("good", "poor"):
            note = "<-- must score WORSE than good/good"
        lines.append(f"  {label:26} {len(rows):>3}  {d:>5.0f}  {e:>5.0f}  {note}")

    gg, gp = means.get(("good", "good")), means.get(("good", "poor"))
    lines.append("")
    if gg is None or gp is None:
        lines.append("  VERDICT: not enough corpus coverage to evaluate the thesis yet.")
    elif gp < gg - 10:
        lines.append(f"  VERDICT: PASS -- good-SEO/poor-GEO scores {gg - gp:.0f} points "
                     f"below good-SEO/good-GEO.")
        lines.append("           The marketplace separates GEO failure from SEO health.")
    else:
        lines.append(f"  VERDICT: FAIL -- good-SEO/poor-GEO ({gp:.0f}) is not materially "
                     f"below good-SEO/good-GEO ({gg:.0f}).")
        lines.append("           These are sites an SEO linter passes clean. So do we.")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live", action="store_true",
                      help="crawl live sites (pinned smoke subset unless --all)")
    mode.add_argument("--replay", action="store_true",
                      help="reuse snapshotted bundles; deterministic")
    mode.add_argument("--snapshot", action="store_true",
                      help="refresh snapshots from live sites")
    ap.add_argument("--all", action="store_true",
                    help="with --live, run the whole corpus instead of the smoke subset")
    ap.add_argument("--max-pages", type=int, default=15)
    ap.add_argument("--budget", type=int, default=100)
    args = ap.parse_args(argv)

    only_smoke = args.live and not args.all
    sites = load_corpus(only_smoke)
    if not sites:
        print("error: corpus has no matching sites. Populate bench/corpus.yaml.",
              file=sys.stderr)
        return 2

    avail = available_analyzers()
    print(f"analyzers available: {len(avail)}/{len(ANALYZERS)} "
          f"({', '.join(s for s, _ in avail)})")
    print(f"sites: {len(sites)}" + (" (pinned smoke subset)" if only_smoke else ""))
    print()

    os.makedirs(SNAPSHOTS, exist_ok=True)
    os.makedirs(SCOREBOARD, exist_ok=True)
    tmp = os.path.join(SCOREBOARD, "_tmp")
    os.makedirs(tmp, exist_ok=True)

    results = []
    for i, site in enumerate(sites, 1):
        name = slug(site["url"])
        bundle = os.path.join(SNAPSHOTS, name)
        print(f"[{i}/{len(sites)}] {site['url']}")

        if args.live or args.snapshot:
            if not collect_live(site, bundle, args.max_pages, args.budget):
                results.append({"url": site["url"], "error": "collect failed",
                                "seo": site.get("seo"), "geo": site.get("geo")})
                continue
        elif not os.path.isdir(bundle):
            print("    no snapshot; run --snapshot first")
            results.append({"url": site["url"], "error": "no snapshot",
                            "seo": site.get("seo"), "geo": site.get("geo")})
            continue

        if args.snapshot:
            print("    snapshot written")
            continue

        try:
            r = audit_one(site, bundle, tmp)
        except Exception as exc:
            r = {"url": site["url"], "error": f"{type(exc).__name__}: {exc}",
                 "seo": site.get("seo"), "geo": site.get("geo")}
        results.append(r)

        if "error" in r:
            print(f"    ERROR {r['error']}")
            continue
        s = r["summary"]
        print(f"    disc {r['discoverability']:>3}/{r['disc_grade']}  "
              f"eng {r['engagement_score']:>3}/{r['eng_grade']}  "
              f"{s['total_findings']} findings "
              f"(c{s['critical']} h{s['high']} m{s['medium']} l{s['low']})  "
              f"{r['pages']}p {r['seconds']}s")
        if r["misses"]:
            print(f"    MISSED   {', '.join(r['misses'])}")
        if r["false_positives"]:
            print(f"    FALSE +  {', '.join(r['false_positives'])}")
        if r["seconds"] > 300:
            print("    OVER BUDGET: exceeded the 5-minute audit ceiling")

    if args.snapshot:
        print(f"\nsnapshots refreshed in {SNAPSHOTS}")
        return 0

    chart = quadrant_chart(results)
    print(chart)

    graded = [r for r in results if "error" not in r]
    total_fp = sum(len(r["false_positives"]) for r in graded)
    total_miss = sum(len(r["misses"]) for r in graded)
    slowest = max((r["seconds"] for r in graded), default=0)
    print()
    print(f"  audited        {len(graded)}/{len(results)}")
    print(f"  false positives {total_fp}")
    print(f"  misses          {total_miss}")
    pending = sorted({c for r in graded for c in r.get("not_yet_implemented") or []})
    if pending:
        print(f"  not yet checked {len(pending)} check(s) whose skill is still a "
              f"scaffold: {', '.join(pending)}")
    print(f"  slowest         {slowest:.0f}s (ceiling 300s)")

    out = os.path.join(SCOREBOARD, "latest.json")
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"mode": "live" if args.live else "replay",
                   "results": results}, fh, indent=2)
    with io.open(os.path.join(SCOREBOARD, "latest.txt"), "w",
                 encoding="utf-8", newline="\n") as fh:
        fh.write(chart + "\n")
    print(f"\nscoreboard -> {out}")

    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if total_fp else 0


if __name__ == "__main__":
    sys.exit(main())
