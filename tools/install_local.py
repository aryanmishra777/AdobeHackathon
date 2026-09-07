#!/usr/bin/env python3
"""Install the marketplace's skills where a local agent will discover them.

Dev tooling -- outside the submission.

Needed for the end-to-end check that matters most: does a real agent, given a
plain "audit example.com", activate the ORCHESTRATOR and nothing else, then
dispatch the rest? That only gets tested by installing the skills and asking.

    python tools/install_local.py                 # copy into .claude/skills/
    python tools/install_local.py --target agents # .agents/skills/ (cross-client)
    python tools/install_local.py --link          # symlink instead of copy
    python tools/install_local.py --uninstall

--link is what you want while iterating: edits to the repo take effect with no
reinstall. It needs Developer Mode or an elevated shell on Windows.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(REPO, "brand-ai-readiness-audit", "skills")

TARGETS = {
    "claude": os.path.join(".claude", "skills"),
    "agents": os.path.join(".agents", "skills"),
}


def skill_names() -> list[str]:
    return sorted(d for d in os.listdir(SOURCE)
                  if os.path.isfile(os.path.join(SOURCE, d, "SKILL.md")))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", choices=sorted(TARGETS), default="claude")
    ap.add_argument("--scope", choices=["user", "project"], default="user",
                    help="user: ~/  project: the repo root")
    ap.add_argument("--link", action="store_true", help="symlink instead of copy")
    ap.add_argument("--uninstall", action="store_true")
    args = ap.parse_args(argv)

    base = os.path.expanduser("~") if args.scope == "user" else REPO
    dest_root = os.path.join(base, TARGETS[args.target])

    names = skill_names()
    if not names:
        print(f"error: no skills found under {SOURCE}", file=sys.stderr)
        return 2

    if args.uninstall:
        removed = 0
        for name in names:
            dest = os.path.join(dest_root, name)
            if os.path.islink(dest):
                os.unlink(dest)
                removed += 1
            elif os.path.isdir(dest):
                shutil.rmtree(dest)
                removed += 1
        print(f"removed {removed} skill(s) from {dest_root}")
        return 0

    os.makedirs(dest_root, exist_ok=True)
    for name in names:
        src = os.path.join(SOURCE, name)
        dest = os.path.join(dest_root, name)
        if os.path.islink(dest):
            os.unlink(dest)
        elif os.path.isdir(dest):
            shutil.rmtree(dest)
        if args.link:
            try:
                os.symlink(src, dest, target_is_directory=True)
            except OSError as exc:
                print(f"error: symlink failed ({exc}).", file=sys.stderr)
                print("On Windows this needs Developer Mode or an elevated shell. "
                      "Re-run without --link to copy instead.", file=sys.stderr)
                return 1
        else:
            shutil.copytree(src, dest,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        print(f"  {'link' if args.link else 'copy'}  {name}")

    print(f"\n{len(names)} skills installed to {dest_root}")
    print("\nNow verify composition in a FRESH agent session:")
    print('  1. ask: "audit example.com for AI discoverability and engagement"')
    print("  2. confirm audit-orchestrator activates -- and that a sub-skill does NOT")
    print("     activate on its own (their descriptions are written to prevent it)")
    print("  3. confirm it dispatches the analysis stages and emits report.json")
    print("     plus report.md, and that validate_report.py passes on the result")
    return 0


if __name__ == "__main__":
    sys.exit(main())
