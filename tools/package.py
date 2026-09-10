#!/usr/bin/env python3
"""Validate, then zip the marketplace root for submission.

Dev tooling -- outside the submission.

Packages ONLY brand-ai-readiness-audit/. Everything else in this repo -- tests,
bench, tools, docs, research -- is development scaffolding and must not ship.

    python tools/package.py
    python tools/package.py --out dist/brand-ai-readiness-audit.zip
    python tools/package.py --allow-todos     # package with scaffold skills

By default this refuses to package while TODOs remain, because a scaffold skill
listed in the manifest but missing its check script produces an audit that
silently skips a whole mechanism.
"""

from __future__ import annotations

import argparse
import fnmatch
import io
import json
import os
import subprocess
import sys
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKET = os.path.join(REPO, "brand-ai-readiness-audit")
MAX_MB = 50

EXCLUDE = [
    "*.pyc", "__pycache__/*", "*.pyo", ".DS_Store", "Thumbs.db",
    ".audit/*", "*.log", "*.tmp", ".git/*", ".pytest_cache/*",
]


def excluded(rel: str) -> bool:
    unix = rel.replace(os.sep, "/")
    return any(fnmatch.fnmatch(unix, pat) or fnmatch.fnmatch(os.path.basename(unix), pat)
               for pat in EXCLUDE)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(REPO, "dist",
                                                  "brand-ai-readiness-audit.zip"))
    ap.add_argument("--allow-todos", action="store_true",
                    help="package even though scaffold skills are incomplete")
    ap.add_argument("--skip-validate", action="store_true")
    args = ap.parse_args(argv)

    if not args.skip_validate:
        print("validating...")
        cmd = [sys.executable, os.path.join(REPO, "tools", "validate.py")]
        if not args.allow_todos:
            cmd.append("--strict")
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        sys.stderr.write(proc.stderr)
        print(proc.stdout)
        if proc.returncode != 0:
            print("refusing to package: validation failed.", file=sys.stderr)
            if not args.allow_todos:
                print("A scaffold skill declared in the manifest but missing its "
                      "check script silently skips a whole mechanism at audit "
                      "time. Finish it, or pass --allow-todos deliberately.",
                      file=sys.stderr)
            return 1

    manifest = json.load(io.open(os.path.join(MARKET, "marketplace.json"),
                                 encoding="utf-8"))
    scaffold = [s["id"] for s in manifest["skills"] if s.get("status") == "scaffold"]
    if scaffold and not args.allow_todos:
        print(f"refusing to package: {len(scaffold)} scaffold skill(s): "
              f"{', '.join(scaffold)}", file=sys.stderr)
        return 1
    if scaffold:
        print(f"WARNING packaging with {len(scaffold)} scaffold skill(s): "
              f"{', '.join(scaffold)}")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    root_name = os.path.basename(MARKET)
    count = 0
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(MARKET):
            dirnames[:] = [d for d in sorted(dirnames)
                           if not excluded(os.path.relpath(
                               os.path.join(dirpath, d), MARKET))]
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, MARKET)
                if excluded(rel):
                    continue
                zf.write(full, os.path.join(root_name, rel).replace(os.sep, "/"))
                count += 1

    size_mb = os.path.getsize(args.out) / (1024 * 1024)
    print(f"\n{args.out}")
    print(f"  files   {count}")
    print(f"  size    {size_mb:.2f} MB (ceiling {MAX_MB} MB)")

    with zipfile.ZipFile(args.out) as zf:
        names = zf.namelist()
    required = f"{root_name}/marketplace.json"
    if required not in names:
        print(f"error: {required} is not in the zip", file=sys.stderr)
        return 1
    if f"{root_name}/README.md" not in names:
        print(f"error: {root_name}/README.md is not in the zip", file=sys.stderr)
        return 1
    skills = {n.split("/")[2] for n in names
              if n.startswith(f"{root_name}/skills/") and n.count("/") > 2}
    declared = {s["id"] for s in manifest["skills"]}
    if skills != declared:
        print(f"error: zip skills {sorted(skills)} != manifest {sorted(declared)}",
              file=sys.stderr)
        return 1
    if size_mb > MAX_MB:
        print(f"error: exceeds the {MAX_MB} MB submission ceiling", file=sys.stderr)
        return 1

    print(f"  skills  {len(skills)}, manifest matches")
    print("\nOK: ready to submit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
