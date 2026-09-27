#!/usr/bin/env python3
"""Prove the session is running the SUBMITTED Round 3 marketplace.

Round 4 asks for "one line on wiring": confirm the live run really invokes the
Round 3 entrypoint and not a hardcoded demo. This prints a single fingerprint
over every skill file the harness will load, and the same fingerprint over the
submitted zip, and says whether they match.

    python round4/verify_wiring.py

Outside the submission: this file is not part of the marketplace and the
marketplace never reads it.
"""
from __future__ import annotations

import hashlib
import io
import os
import sys
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP = os.path.join(REPO, "dist", "brand-ai-readiness-audit.zip")
INSTALLED = os.path.expanduser(os.path.join("~", ".claude", "skills"))
SKILLS = ["answerability-audit", "audit-orchestrator", "crawl-access-audit",
          "engagement-audit", "freshness-corroboration-audit",
          "render-extractability-audit", "site-evidence-collector",
          "structured-data-audit"]


def fingerprint_dir(base: str) -> tuple[str, int]:
    """SHA-256 over (relative path, bytes) of every marketplace skill file."""
    h = hashlib.sha256()
    n = 0
    for skill in SKILLS:
        root = os.path.join(base, skill)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
            for f in sorted(filenames):
                p = os.path.join(dirpath, f)
                rel = os.path.relpath(p, base).replace("\\", "/")
                h.update(rel.encode() + b"\0")
                h.update(io.open(p, "rb").read())
                n += 1
    return h.hexdigest(), n


def fingerprint_zip(path: str) -> tuple[str, int]:
    """The same fingerprint over the submitted package's skills/ tree."""
    h = hashlib.sha256()
    n = 0
    with zipfile.ZipFile(path) as z:
        names = [x for x in z.namelist() if not x.endswith("/")]
        for skill in SKILLS:
            prefix = f"brand-ai-readiness-audit/skills/{skill}/"
            for name in sorted(x for x in names if x.startswith(prefix)):
                rel = name[len("brand-ai-readiness-audit/skills/"):]
                h.update(rel.encode() + b"\0")
                h.update(z.read(name))
                n += 1
    return h.hexdigest(), n


def main() -> int:
    if not os.path.isdir(INSTALLED):
        print(f"no skills installed at {INSTALLED}", file=sys.stderr)
        return 2
    live, live_n = fingerprint_dir(INSTALLED)
    print(f"  harness loads : {INSTALLED}")
    print(f"  files         : {live_n}")
    print(f"  fingerprint   : {live}")
    if not os.path.isfile(ZIP):
        print(f"\n  (submitted zip not found at {ZIP} -- cannot compare)")
        return 0
    sub, sub_n = fingerprint_zip(ZIP)
    print(f"\n  submitted zip : {os.path.relpath(ZIP, REPO)}")
    print(f"  files         : {sub_n}")
    print(f"  fingerprint   : {sub}")
    match = live == sub and live_n == sub_n
    print("\n  MATCH: the agent is running the submitted Round 3 marketplace."
          if match else
          "\n  MISMATCH: the installed skills are NOT the submitted engine. Do not record.")
    return 0 if match else 1


if __name__ == "__main__":
    sys.exit(main())
