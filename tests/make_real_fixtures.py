#!/usr/bin/env python3
"""Trim real pages from an evidence bundle into tests/fixtures/real/.

Dev tooling -- outside the submission.

Every extractor defect found so far came from a real page the synthetic
fixtures never imitated: an <svg><title> after </head>, an <h3> inside every
product <a>, repeated robots meta tags, a Cloudflare token inside a shell, a
merch placeholder where a price belongs. This keeps a handful of those pages
as regression fixtures, trimmed so they stay small and carry no executable
code: every <script> is dropped except application/ld+json, every <style> is
dropped, and a comment records where and when the page was captured.

    python tests/make_real_fixtures.py .audit/www.nike.in/run-01 p019 nike-product
    python tests/make_real_fixtures.py .audit/www.adidas.co.in/run-01 robots.txt.raw adidas-block-page

The second argument is a page id (pages/<id>/raw.html) or a file inside the
bundle. Refreshing a fixture is a matter of re-running the line for it.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fixtures", "real")

KEEP_SCRIPT = re.compile(r'<script\b[^>]*type\s*=\s*["\']?application/ld\+json', re.I)


def trim(html: str) -> str:
    def drop_script(m):
        return m.group(0) if KEEP_SCRIPT.match(m.group(0)) else ""
    html = re.sub(r"<script\b.*?</script>", drop_script, html, flags=re.S | re.I)
    html = re.sub(r"<style\b.*?</style>", "", html, flags=re.S | re.I)
    html = re.sub(r"<noscript>\s*<img[^>]*>\s*</noscript>", "", html, flags=re.S | re.I)
    return html


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 3:
        print(__doc__)
        return 2
    bundle, what, name = argv
    if os.path.isfile(os.path.join(bundle, what)):
        src = os.path.join(bundle, what)
        url = json.load(io.open(os.path.join(bundle, "run.json"), encoding="utf-8")).get("origin", "?")
    else:
        src = os.path.join(bundle, "pages", what, "raw.html")
        req = json.load(io.open(os.path.join(bundle, "pages", what, "request.json"), encoding="utf-8"))
        url = req.get("final_url") or req.get("url") or "?"
    run = json.load(io.open(os.path.join(bundle, "run.json"), encoding="utf-8"))
    html = io.open(src, encoding="utf-8", errors="replace").read()
    trimmed = trim(html)
    header = (f"<!-- fixture: {name}\n     source: {url}\n     captured: {run.get('started_at')}\n"
              f"     trimmed by tests/make_real_fixtures.py on {time.strftime('%Y-%m-%d')}: "
              f"scripts (except JSON-LD) and styles removed; {len(html):,} -> {len(trimmed):,} bytes -->\n")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".html")
    io.open(path, "w", encoding="utf-8", newline="\n").write(header + trimmed)
    print(f"{path}  {len(trimmed):,} bytes  <- {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
