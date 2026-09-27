#!/usr/bin/env python3
"""Measure VIDEO-SCRIPT.md against the Round 4 per-part caps.

The first draft ran 5:43 of narration against a 5:00 cap -- before a pause, a
keystroke, or a second of watching the agent work. Guessing does not work.

This does not grade the script against an assumed speaking pace. It reports the
pace the script *requires*, which is the number that actually decides whether
you can deliver it:

    python round4/check_timing.py

Part 1 has a hard 3:00 cap, so its word count fixes a minimum pace. Part 2 has a
2:00 cap shared between narration and watching the run, so what matters there is
how much time the narration leaves over.

Spoken text is every blockquote line.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "VIDEO-SCRIPT.md")
PART1_CAP, PART2_CAP = 180.0, 120.0
# Above this the script is too long to deliver deliberately, whatever the maths.
COMFORT_CEILING_WPM = 120.0


def beats(text: str):
    part, name, buf, part_at, out = None, None, [], None, []
    for line in text.splitlines():
        if line.startswith("## Part 1"):
            part = 1
        elif line.startswith("## Part 2"):
            part = 2
        elif line.startswith("## "):
            part = None
        if line.startswith("### "):
            if name:
                out.append((part_at, name, buf))
            name, buf, part_at = line[4:].strip(), [], part
        elif line.startswith("> ") and name:
            buf.append(line[2:])
    if name:
        out.append((part_at, name, buf))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wpm", type=float, default=None,
                    help="check against a specific pace instead of reporting the required one")
    args = ap.parse_args()

    text = io.open(SCRIPT, encoding="utf-8").read()
    words = {1: 0, 2: 0}
    rows = []
    for part, name, lines in beats(text):
        n = len(re.sub(r"[`*_\[\]]", "", " ".join(lines)).split())
        # A "Spare" beat is a line held back for the case where delivery runs
        # early. Counting it would inflate the pace the script demands.
        spare = name.lower().startswith("spare")
        if part in words and not spare:
            words[part] += n
        label = name.split("·")[-1].strip() if "·" in name else name
        rows.append((part, n, "(spare) " + label if spare else label))

    required = words[1] / PART1_CAP * 60 if words[1] else 0.0
    pace = args.wpm or required

    print()
    for part, n, label in rows:
        print(f"   part {part}   {n:4d} w   {n / pace * 60:5.1f}s   {label[:50]}")

    p1 = words[1] / pace * 60
    p2 = words[2] / pace * 60
    print()
    print(f"  part 1   {words[1]:4d} words — fills the 3:00 cap at {required:.0f} wpm")
    print(f"  part 2   {words[2]:4d} words — {p2:.0f}s of narration at that pace, "
          f"leaving {PART2_CAP - p2:.0f}s of the 2:00 to watch the run")
    print(f"  total    {words[1] + words[2]:4d} words — {(p1 + p2) / 60:.2f} min of speech")
    print()

    if required > COMFORT_CEILING_WPM:
        print(f"  TOO LONG: part 1 needs {required:.0f} wpm, which is a rush. Cut it.")
        print("  Beats marked [cut if long] go first.")
        return 1
    if p2 > PART2_CAP - 30:
        print(f"  TIGHT: part 2 leaves only {PART2_CAP - p2:.0f}s to show the run. "
              "Trim the drill-in narration.")
        return 1
    print(f"  OK at {pace:.0f} wpm — deliberate, and well under conversational speed (130-150).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
