#!/usr/bin/env python3
"""Optional renderer for the collector: print a page's HTML after JavaScript ran.

    python render_playwright.py --check          # exit 0 iff Playwright + Chromium exist
    python render_playwright.py https://x.test/  # print rendered HTML to stdout

This file is stdlib at import time; `playwright` is imported only when asked
for, so the collector can call `--check` on any machine and learn whether a
renderer exists without a hard dependency. Without it every check that reads
`rendered.html` falls back to inference from the raw HTML, which is the
behaviour documented in render-extractability-audit/SKILL.md.

Politeness: the page is fetched under the audit's own declared user-agent,
image/media/font requests are aborted so a render costs the site one document
plus its scripts and stylesheets, and one URL is rendered per process so the
collector's subprocess timeout remains the budget's authority.
"""
from __future__ import annotations

import sys

# Kept in step with collect.py: the renderer announces itself the same way.
AUDIT_UA = ("Mozilla/5.0 (compatible; BrandAIReadinessAudit/0.1; "
            "+read-only site audit; respects robots.txt)")
BLOCKED_RESOURCE_TYPES = {"image", "media", "font"}
GOTO_TIMEOUT_MS = 8000
SETTLE_TIMEOUT_MS = 4000


def check() -> int:
    """0 when Playwright imports and a Chromium executable is installed."""
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except Exception as exc:  # ImportError, or a broken install
        print(f"playwright unavailable: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            version = browser.version
            browser.close()
    except Exception as exc:
        print(f"chromium unavailable: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(f"playwright-chromium {version}")
    return 0


def render(url: str) -> int:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        print(f"playwright unavailable: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(user_agent=AUDIT_UA, java_script_enabled=True)
            page = context.new_page()
            page.route("**/*", lambda route: route.abort()
                       if route.request.resource_type in BLOCKED_RESOURCE_TYPES
                       else route.continue_())
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=GOTO_TIMEOUT_MS)
            except Exception as exc:
                print(f"goto failed: {type(exc).__name__}: {exc}", file=sys.stderr)
                return 1
            try:
                page.wait_for_load_state("networkidle", timeout=SETTLE_TIMEOUT_MS)
            except Exception:
                pass  # a chatty page never idles; what has rendered by now is the answer
            html = page.content()
        finally:
            browser.close()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.write(html)
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--check":
        return check()
    return render(argv[0])


if __name__ == "__main__":
    sys.exit(main())
