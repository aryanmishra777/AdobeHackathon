#!/usr/bin/env python3
"""Serve each fixture site locally and collect an evidence bundle from it.

Dev tooling -- outside the submission.

Analysis skills are pure functions over a bundle, so the test layer needs
bundles, not live sites. This serves each fixture on its own port, runs the real
collector against it, and stores the result in tests/bundles/<name>/.

Regenerate whenever a fixture or the collector changes:

    python tests/make_bundles.py
    python tests/make_bundles.py --only clean
"""

from __future__ import annotations

import argparse
import functools
import http.server
import io
import json
import os
import shutil
import socketserver
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FIXTURES = os.path.join(HERE, "fixtures")
BUNDLES = os.path.join(HERE, "bundles")
COLLECT = os.path.join(REPO, "brand-ai-readiness-audit", "skills",
                       "site-evidence-collector", "scripts", "collect.py")

sys.path.insert(0, HERE)
from make_fixtures import FIXTURES as FIXTURE_SPEC  # noqa: E402


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class ReusableServer(socketserver.TCPServer):
    allow_reuse_address = True


def serve(directory: str, port: int):
    handler = functools.partial(QuietHandler, directory=directory)
    httpd = ReusableServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def collect(name: str, port: int) -> bool:
    out = os.path.join(BUNDLES, name)
    if os.path.isdir(out):
        shutil.rmtree(out)
    proc = subprocess.run(
        [sys.executable, COLLECT, f"http://localhost:{port}",
         "--out", out,
         "--max-pages", "10",
         "--budget", "60",
         "--delay", "0",          # a local fixture needs no politeness delay
         "--timeout", "5",
         # The fixture bundles are the stdlib path of record: the same on a
         # machine with Playwright installed and on a bare one. The renderer
         # is exercised separately by tests/test_real_pages.py when present.
         "--renderer", "none"],
        capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        return False
    return True


def summarize(name: str) -> str:
    path = os.path.join(BUNDLES, name, "MANIFEST.json")
    try:
        m = json.load(io.open(path, encoding="utf-8"))
    except Exception as exc:
        return f"unreadable ({exc})"
    ok = sum(1 for p in m.get("pages", []) if p.get("status") == 200)
    blocked = [t for t, e in (m.get("robots", {}).get("agent_matrix") or {}).items()
               if e.get("root_allowed") is False]
    return (f"{ok} pages, {len(m.get('sitemaps') or [])} sitemap(s), "
            f"{len(blocked)} agent(s) blocked, stopped={m['coverage'].get('stopped_reason')}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="regenerate a single fixture's bundle")
    args = ap.parse_args(argv)

    if not os.path.isdir(FIXTURES):
        print("error: no fixtures. Run: python tests/make_fixtures.py", file=sys.stderr)
        return 2

    os.makedirs(BUNDLES, exist_ok=True)
    targets = {k: v for k, v in FIXTURE_SPEC.items()
               if not args.only or k == args.only}
    if not targets:
        print(f"error: unknown fixture {args.only!r}", file=sys.stderr)
        return 2

    failures = 0
    for name, (_fn, port, desc) in targets.items():
        directory = os.path.join(FIXTURES, name)
        if not os.path.isdir(directory):
            print(f"{name:24} SKIP (no fixture directory)")
            continue
        httpd = serve(directory, port)
        try:
            time.sleep(0.2)
            ok = collect(name, port)
        finally:
            httpd.shutdown()
            httpd.server_close()
        if ok:
            print(f"{name:24} OK   {summarize(name)}")
        else:
            print(f"{name:24} FAIL")
            failures += 1

    print(f"\nbundles in {BUNDLES}")
    if failures:
        print(f"{failures} fixture(s) failed to collect", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
