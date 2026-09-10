#!/usr/bin/env python3
"""Find checks that never fire.

The tests, the validator and the bench all stayed green while two checks were
dead code: REACH-014 raised an exception that main() swallowed, and REACH-013
read a manifest key that does not exist. Neither produced a single finding on
any site, and nothing noticed, because every gate we had asks "did anything go
wrong?" rather than "did this check ever do anything?".

This asks the second question. It runs every analysis skill over every bundle it
can find and reports which registered check IDs never appeared in a finding.

A check that never fires is not automatically broken -- some detect genuinely
rare conditions. So a registry entry may declare itself rare:

    - id: PARSE-002
      rarity: rare
      rarity_reason: "Fires only on structured data that fails to parse."

Declaring rarity is a claim someone made on purpose, which is the point: the
alternative is silence, and silence is what let the dead checks through.

    python tools/check_coverage.py              # report
    python tools/check_coverage.py --strict     # non-zero exit on undeclared

Exit codes: 0 clean, 1 undeclared silent checks, 2 could not run.
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MARKET = os.path.join(REPO, "brand-ai-readiness-audit")
SKILLS = os.path.join(MARKET, "skills")

ANALYZERS = [
    ("crawl-access-audit", "check_access.py"),
    ("render-extractability-audit", "check_render.py"),
    ("structured-data-audit", "check_structured_data.py"),
    ("answerability-audit", "check_answerability.py"),
    ("freshness-corroboration-audit", "check_trust.py"),
    ("engagement-audit", "check_engagement.py"),
]


def registry_entries() -> dict:
    """Every registered check id -> its declared rarity, if any."""
    out = {}
    for path in sorted(glob.glob(os.path.join(SKILLS, "*", "references", "checks.yaml"))):
        text = io.open(path, encoding="utf-8").read()
        for m in re.finditer(r"^\s*- id: ([A-Z]+-\d+)\n(.*?)(?=^\s*- id: |\Z)",
                             text, re.M | re.S):
            cid, block = m.group(1), m.group(2)
            rarity = re.search(r"^\s*rarity:\s*(\S+)", block, re.M)
            reason = re.search(r"^\s*rarity_reason:\s*[\"']?(.+?)[\"']?\s*$", block, re.M)
            out[cid] = {
                "rarity": rarity.group(1) if rarity else None,
                "reason": reason.group(1) if reason else None,
                "skill": os.path.basename(os.path.dirname(os.path.dirname(path))),
                "proactive_only": "proactive recommendation only" in block
                                  or "never a defect" in block,
            }
    return out


def bundles() -> list:
    found = []
    for pattern in (os.path.join(REPO, "bench", "snapshots", "*"),
                    os.path.join(REPO, "tests", "bundles", "*")):
        for d in sorted(glob.glob(pattern)):
            if os.path.exists(os.path.join(d, "MANIFEST.json")):
                found.append(d)
    return found


def run_all(paths: list, verbose: bool) -> tuple:
    fired, skipped, crashed = {}, {}, []
    for i, bundle in enumerate(paths, 1):
        if verbose:
            print(f"  [{i}/{len(paths)}] {os.path.basename(bundle)}", file=sys.stderr)
        for skill, script in ANALYZERS:
            path = os.path.join(SKILLS, skill, "scripts", script)
            if not os.path.exists(path):
                continue
            proc = subprocess.run([sys.executable, path, bundle, "--stdout"],
                                  capture_output=True, text=True, encoding="utf-8")
            if proc.returncode != 0:
                crashed.append((os.path.basename(bundle), skill,
                                (proc.stderr or "").strip().splitlines()[-1:]))
                continue
            try:
                doc = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                crashed.append((os.path.basename(bundle), skill, ["unparseable stdout"]))
                continue
            items = doc if isinstance(doc, list) else doc.get("findings") or []
            for f in items:
                cid = f.get("check_id")
                if cid:
                    fired[cid] = fired.get(cid, 0) + 1
            if isinstance(doc, dict):
                for entry in doc.get("checks_skipped") or []:
                    cid = entry.get("check_id") if isinstance(entry, dict) else entry
                    if cid:
                        skipped[cid] = skipped.get(cid, 0) + 1
                for cid in doc.get("checks_not_implemented") or []:
                    skipped[cid] = skipped.get(cid, 0) + 1
    return fired, skipped, crashed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero when a check is silent and undeclared")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    paths = bundles()
    if not paths:
        print("error: no bundles. Run tests/make_bundles.py or bench/run.py --snapshot.",
              file=sys.stderr)
        return 2

    registry = registry_entries()
    fired, skipped, crashed = run_all(paths, verbose=not args.quiet)

    silent = sorted(c for c in registry if c not in fired)
    undeclared = [c for c in silent
                  if not registry[c]["rarity"]
                  and not registry[c]["proactive_only"]
                  and c not in skipped]
    declared = [c for c in silent if c not in undeclared]

    print()
    print(f"bundles     {len(paths)}")
    print(f"registered  {len(registry)}")
    print(f"fired       {len(fired)}")
    print(f"silent      {len(silent)}  ({len(declared)} declared, "
          f"{len(undeclared)} undeclared)")

    if crashed:
        print(f"\nCRASHED ({len(crashed)}) -- a check that raises is a check that "
              f"cannot fire:")
        for bundle, skill, tail in crashed[:12]:
            print(f"  {bundle:<26} {skill:<30} {' '.join(tail)[:70]}")

    if declared:
        print("\nsilent, but declared:")
        for c in declared:
            why = (registry[c]["reason"] or
                   ("proactive only" if registry[c]["proactive_only"] else
                    "skipped at runtime" if c in skipped else "declared rare"))
            print(f"  {c:<12} {why[:80]}")

    if undeclared:
        print(f"\nSILENT AND UNDECLARED ({len(undeclared)}) -- each is either dead "
              f"code or a rarity nobody wrote down:")
        for c in undeclared:
            print(f"  {c:<12} {registry[c]['skill']}")
        print("\n  Fix the dead ones. For the genuinely rare, add to the registry:")
        print("    rarity: rare")
        print('    rarity_reason: "..."')

    if undeclared and args.strict:
        return 1
    if crashed:
        return 1
    print("\nOK" if not undeclared else "\nreport only (use --strict to fail)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
