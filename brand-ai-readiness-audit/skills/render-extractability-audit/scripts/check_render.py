#!/usr/bin/env python3
"""READ checks: can a machine read what is on the page?

Standard library only -- ships inside the submission.

Reads a completed evidence bundle and emits candidate findings against
../audit-orchestrator/references/finding.schema.json. Performs no network I/O:
every result is a pure function of the bundle, so the same bundle always yields
the same findings.

Mirrors crawl-access-audit/scripts/check_access.py structurally:
  * load the bundle once, into a small accessor object
  * one function per check, named check_<id>, returning zero or more candidates
  * every candidate cites artifact_refs that actually exist in the bundle
  * false-positive guards live next to the logic that would trip them, as code
    where mechanical and as an explicit comment where they need human judgment
  * base severity only -- the orchestrator owns scope and confidence modifiers

Usage:
    python check_render.py <bundle> --out read-candidates.json
    python check_render.py <bundle> --stdout
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import statistics
import sys
import time
from urllib.parse import urlparse

MECHANISM = "read"
CATEGORY = "discoverability"

# Utility paths exempt from content authentication / paywall checks
UTILITY_PATH_HINTS = (
    "/cart", "/checkout", "/account", "/login", "/signin",
    "/register", "/search", "/tag/", "/tags/", "/filter",
    "/wishlist", "/compare", "/basket", "/my-account",
    "/thank-you", "/order-confirmation", "/preview"
)

# Known video/audio embed hostnames
VIDEO_HOST_PATTERNS = (
    "youtube.com", "youtu.be", "vimeo.com", "wistia.com",
    "loom.com", "spotify.com", "soundcloud.com", "dailymotion.com",
    "player.twitch.tv"
)

# Legitimate third-party widget domains that carry no citable facts
LEGITIMATE_IFRAMES = (
    "maps.google.", "google.com/maps", "openstreetmap.org",
    "js.stripe.com", "paypal.com", "recaptcha", "hcaptcha.com",
    "challenges.cloudflare.com", "turnstile"
)

# Review / rating widget domains whose values should be mirrored
REVIEW_WIDGET_DOMAINS = (
    "trustpilot.com", "yotpo.com", "feefo.com", "stamped.io",
    "bazaarvoice.com", "reviews.io", "google.com/reviews",
    "embedsocial.com", "widget.trustoo.io", "birdeye.com"
)

# Consent management platform (CMP) signatures
CONSENT_SIGNATURES = (
    "onetrust", "didomi", "cookiebot", "trustarc", "usercentrics",
    "quantcast", "klaro", "cookie-consent", "consent-banner",
    "termly", "iubenda", "osano"
)

# Mojibake detection patterns (UTF-8 bytes mis-decoded as Latin-1/Windows-1252)
MOJIBAKE_PATTERN = re.compile(
    r"(\ufffd|Ã[\x80-\xbf]|â[\x80-\xbf]{2}|Ã¢|Ã©|Ã¨|Ã¯|Ã§|â€\x9d|â€\x9c|â€™)"
)


class Bundle:
    """Thin accessor over an evidence bundle directory."""

    def __init__(self, root: str):
        self.root = root
        self.manifest = self._json("MANIFEST.json") or {}
        self.run = self.manifest.get("run") or {}
        self.robots = self.manifest.get("robots") or {}
        self.sitemaps = self.manifest.get("sitemaps") or []
        self.probe = self.manifest.get("ua_probe") or {}
        self.coverage = self.manifest.get("coverage") or {}
        self.pages = self.manifest.get("pages") or []
        self.origin = self.run.get("origin") or ""
        self.site = urlparse(self.origin).netloc or self.origin
        self._extracted: dict[str, dict] = {}
        self._headers: dict[str, dict] = {}
        self._requests: dict[str, dict] = {}
        self._raw_html: dict[str, str] = {}
        self._rendered_html: dict[str, str] = {}

    def _json(self, rel: str):
        path = os.path.join(self.root, rel.replace("/", os.sep))
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _text(self, rel: str) -> str:
        path = os.path.join(self.root, rel.replace("/", os.sep))
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                return fh.read()
        except FileNotFoundError:
            return ""

    def exists(self, rel: str) -> bool:
        return os.path.exists(os.path.join(self.root, rel.replace("/", os.sep)))

    @property
    def ok_pages(self) -> list[dict]:
        """Pages that were actually fetched with 200 OK."""
        return [p for p in self.pages if p.get("status") == 200]

    def extracted(self, page_id: str) -> dict:
        if page_id not in self._extracted:
            self._extracted[page_id] = self._json(f"pages/{page_id}/extracted.json") or {}
        return self._extracted[page_id]

    def headers(self, page_id: str) -> dict:
        if page_id not in self._headers:
            raw = self._json(f"pages/{page_id}/response.headers.json") or {}
            self._headers[page_id] = {k.lower(): v for k, v in raw.items()}
        return self._headers[page_id]

    def request(self, page_id: str) -> dict:
        if page_id not in self._requests:
            self._requests[page_id] = self._json(f"pages/{page_id}/request.json") or {}
        return self._requests[page_id]

    def raw_html(self, page_id: str) -> str:
        if page_id not in self._raw_html:
            self._raw_html[page_id] = self._text(f"pages/{page_id}/raw.html")
        return self._raw_html[page_id]

    def rendered_html(self, page_id: str) -> str:
        if page_id not in self._rendered_html:
            self._rendered_html[page_id] = self._text(f"pages/{page_id}/rendered.html")
        return self._rendered_html[page_id]


def finding(check_id, title, severity, evidence, refs, *, pages=None, counts=None,
            confidence="high", determinism="deterministic", verification="",
            action=None, excerpt=None, scope=None, checked=0):
    pages = pages or []
    return {
        "id": "F-000",  # placeholder; the orchestrator assigns the real id
        "check_id": check_id,
        "title": title,
        "severity": severity,
        "confidence": confidence,
        "determinism": determinism,
        "category": CATEGORY,
        "mechanism": MECHANISM,
        "evidence": evidence,
        "evidence_detail": {
            "pages_affected": pages,
            "counts": counts or {},
            "artifact_refs": refs,
            **({"excerpt": excerpt[:1200]} if excerpt else {}),
        },
        "affected_scope": {
            "pages_checked": checked,
            "pages_affected": len(pages),
            "scope": scope or ("site-wide" if not pages else "page"),
        },
        "verification": verification,
        "suggested_action": action or {},
    }


def act(summary, priority, steps, effort, rationale, code=None, owner=None):
    out = {"summary": summary, "priority": priority, "steps": steps,
           "effort": effort, "impact_rationale": rationale}
    if code:
        out["code"] = code
    if owner:
        out["owner"] = owner
    return out


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

# Framework markers that mean the page is assembled in the browser. The
# collector reports server-rendered platforms in the same list -- "wp-content"
# appears in an asset URL on every WordPress page, and Shopify's Liquid
# templates render on the server -- so reading those as evidence of client
# rendering fires READ-001 on most of the CMS-hosted web.
CLIENT_RENDERED_FRAMEWORKS = frozenset({
    "next.js", "nuxt", "react", "angular", "vue", "remix", "sveltekit", "gatsby",
})

# A page carrying only nav and footer chrome lands near 60 words, so a hard
# "< 50" cliff misses genuinely empty shells by a handful of words. Thin is
# unambiguous below THIN_WORDS; between there and THIN_WORDS_STRONG it only
# counts when the corroborating signal is overwhelming.
THIN_WORDS = 50
# Body text a shell shows to a client that has not run its JavaScript.
NO_JS_MESSAGE_RE = re.compile(
    r"(enable javascript|javascript is (required|disabled)|update your (web )?browser|"
    r"browser we don.t support|please update your browser)")
THIN_WORDS_STRONG = 120
STRONG_PAYLOAD_BYTES = 50_000
STRONG_RATIO = 0.01
WEAK_PAYLOAD_BYTES = 500
WEAK_RATIO = 0.05


# Pages that are an interactive application or a utility, not prose. A puzzle
# game has no article to server-render, so "content is missing from the HTML"
# is true of it and useless. nytimes.com produced a high-severity READ-001 built
# entirely from Wordle, the mini crossword, Spelling Bee, /gift and /newsletters
# while its 14 actual articles carried 267-2007 words each.
NON_CONTENT_PATH_HINTS = (
    "/games", "/game/", "/puzzle", "/crossword", "/wordle", "/quiz",
    "/sudoku", "/tools/", "/calculator", "/login", "/signin", "/register",
    "/account", "/subscribe", "/newsletter", "/gift", "/cart", "/checkout",
    "/search", "/player", "/embed", "/wishlist", "/wish-list", "/favorites",
    "/favourites", "/profile", "/settings", "/preferences",
)
# Whole path segments only: "/edit" is a personalisation page, "/editorial" is
# content.
NON_CONTENT_PATH_SEGMENTS = {"edit", "compare", "saved", "recent", "history"}


def _is_application_page(page: dict) -> bool:
    url = (page.get("final_url") or page.get("url") or "").lower()
    path = urlparse(url).path or "/"
    if any(h in path for h in NON_CONTENT_PATH_HINTS):
        return True
    return any(seg in NON_CONTENT_PATH_SEGMENTS for seg in path.split("/") if seg)


def _render_signals(page: dict, ext: dict) -> dict | None:
    """The client-rendering signals that actually fired, or None.

    Binding guard: never fire on one signal. A mount point or a client-side
    framework marker must coincide with thin body text AND a corroborating
    payload or text-to-markup signal. Callers build evidence strings from the
    returned dict so that no claim is made about a signal that did not fire.
    """
    render_sig = ext.get("render_signals") or {}
    text_obj = ext.get("text") or {}

    shells = list(render_sig.get("app_shell_selectors") or [])
    frameworks = [f for f in (render_sig.get("framework_markers") or [])
                  if f in CLIENT_RENDERED_FRAMEWORKS]
    if not (shells or frameworks):
        return None

    words = text_obj.get("main_word_count") or 0
    payload = render_sig.get("hydration_payload_bytes") or 0
    ratio = text_obj.get("text_to_markup_ratio")
    if ratio is None:
        ratio = 1.0

    strong = payload > STRONG_PAYLOAD_BYTES or ratio < STRONG_RATIO
    if words >= (THIN_WORDS_STRONG if strong else THIN_WORDS):
        return None
    if not (payload > WEAK_PAYLOAD_BYTES or ratio < WEAK_RATIO):
        return None

    return {
        "shells": sorted(shells),
        "frameworks": sorted(frameworks),
        "words": words,
        "payload": payload,
        "ratio": ratio,
    }


def _is_client_rendered(page: dict, ext: dict) -> bool:
    """Boolean form of :func:`_render_signals`, for checks that need only the verdict."""
    return _render_signals(page, ext) is not None


def _describe_signals(sigs: list[dict]) -> str:
    """Phrase only the signals that actually fired, in the order they matter.

    Never assert a hydration payload of zero bytes or a mount point that was
    never detected: a finding whose own evidence sentence is self-refuting is
    worse than no finding at all.
    """
    parts = []
    payloads = [s["payload"] for s in sigs if s["payload"]]
    if payloads:
        parts.append(f"a hydration payload of up to {max(payloads):,} bytes")

    all_shells = sorted({sel for s in sigs for sel in s["shells"]})
    identical = [sel for sel in all_shells if sel.startswith("identical-document-x")]
    if identical:
        n = max(int(sel.rsplit("x", 1)[1]) for sel in identical)
        parts.append(f"one byte-identical document served for {n} different URLs")
    if "no-javascript-message" in all_shells:
        parts.append("a body message telling non-JavaScript clients to update or enable their browser")
    shells = [sel for sel in all_shells
              if not sel.startswith("identical-document-x") and sel != "no-javascript-message"]
    if shells:
        sel = shells[0]
        if not sel.startswith(("#", ".", "[")):
            sel = "#" + sel
        parts.append(f"an empty {sel} mount point")

    frameworks = sorted({f for s in sigs for f in s["frameworks"]})
    if frameworks and not shells:
        parts.append(f"a {'/'.join(frameworks)} client-rendering marker")

    ratios = [s["ratio"] for s in sigs]
    if ratios and min(ratios) < WEAK_RATIO:
        parts.append(f"a text-to-markup ratio of {min(ratios):.4f}")

    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def check_read_001(b: Bundle) -> list[dict]:
    """Page content is missing from the HTML a crawler receives.

    The single highest-value check in the marketplace.
    Binding guards:
      - Never fire on markers or low word count alone. Require combination:
        (empty mount OR framework marker) AND low main_word_count AND
        (hydration payload OR very low text-to-markup ratio).
      - Skip non-200 pages and pages truncated by collector.
      - If renderer is not available, cap confidence at 'medium', state the gap
        was inferred rather than measured, and note in coverage.limitations.
    """
    valid_pages = []
    for page in b.ok_pages:
        # Guard: check request.json#truncated first
        req = b.request(page["page_id"])
        if req.get("truncated"):
            continue
        # Guard: a game, quiz or sign-in form is an application, not an article.
        # It has no prose to render server-side, so its empty body is the
        # correct design rather than a defect.
        if _is_application_page(page):
            continue
        valid_pages.append(page)

    if not valid_pages:
        return []

    renderer_available = bool(b.run.get("renderer", {}).get("available"))

    # A single-page application serves one document for every route. When
    # three or more distinct URLs return byte-identical HTML, that document is
    # the shell whatever selectors it uses: crunchyroll.com returned one
    # 281,222-byte file for 21 browse routes, carrying 99 words of header and
    # footer chrome and a body message telling non-JavaScript clients to
    # update their browser -- and no selector in APP_SHELL_SELECTORS. Both
    # facts count as the mount-point signal; the word and ratio guards still
    # have to agree before anything fires.
    digests = {}
    for page in valid_pages:
        try:
            # Compare the markup, not the scripts: Cloudflare and analytics
            # tags carry a per-request token that makes otherwise identical
            # shells differ by a few bytes.
            markup = re.sub(r"<script\b.*?</script>", "", b.raw_html(page["page_id"]),
                            flags=re.S | re.I)
            digest = hashlib.sha1(markup.encode("utf-8", "replace")).hexdigest()
        except Exception:
            digest = None
        digests.setdefault(digest, []).append(page["page_id"])
    identical = {pid: len(pids) for d, pids in digests.items() if d and len(pids) >= 3 for pid in pids}

    affected = []
    fired = []
    max_payload = 0

    for page in valid_pages:
        pid = page["page_id"]
        ext = b.extracted(pid)
        extra = []
        if pid in identical:
            extra.append(f"identical-document-x{identical[pid]}")
        main_text = ((ext.get("text") or {}).get("main") or "").lower()
        if NO_JS_MESSAGE_RE.search(main_text):
            extra.append("no-javascript-message")
        if extra:
            rs = dict(ext.get("render_signals") or {})
            rs["app_shell_selectors"] = list(rs.get("app_shell_selectors") or []) + extra
            ext = dict(ext, render_signals=rs)

        if renderer_available and b.exists(f"pages/{pid}/rendered.html"):
            # Ground truth measurement when rendered.html is captured
            rendered_text = b.rendered_html(pid)
            raw_text = (ext.get("text") or {}).get("main") or ""
            rendered_words = len(rendered_text.split())
            raw_words = len(raw_text.split())
            if rendered_words >= 100 and raw_words < THIN_WORDS:
                affected.append(page)
        else:
            # Inference from the strict combined signals
            sigs = _render_signals(page, ext)
            if sigs:
                affected.append(page)
                fired.append(sigs)
                max_payload = max(max_payload, sigs["payload"])

    if not affected:
        return []

    n = len(affected)
    m = len(valid_pages)
    ratio = n / m

    # Base severity rule:
    # critical when main content of most sampled pages is absent from raw HTML
    # high when a major section or template is affected
    # medium when only supplementary content is client-rendered
    if ratio >= 0.5 or (m >= 3 and n >= 2 and ratio >= 0.4):
        severity = "critical"
    elif n >= 2:
        severity = "high"
    else:
        severity = "medium"

    thinnest = max((s["words"] for s in fired), default=THIN_WORDS)

    if renderer_available:
        confidence = "high"
        evidence = (
            f"{n} of {m} sampled pages return under {THIN_WORDS} words of body text in "
            f"raw HTML while runtime rendering measured complete content in rendered.html."
        )
    else:
        confidence = "medium"
        detail = _describe_signals(fired)
        evidence = (
            f"{n} of {m} sampled pages return at most {thinnest} words of body text in "
            f"the raw HTML"
            + (f", while carrying {detail}" if detail else "")
            + ". (Inferred from raw-HTML signals; no browser renderer was "
              "available to measure the runtime DOM.)"
        )
        b.coverage.setdefault("limitations", []).append(
            "No renderer available; JS-dependency inferred from raw HTML rather than measured."
        )

    refs = ["MANIFEST.json"]
    for p in affected[:5]:
        refs.append(f"pages/{p['page_id']}/extracted.json")
        if b.exists(f"pages/{p['page_id']}/rendered.html"):
            refs.append(f"pages/{p['page_id']}/rendered.html")

    first_url = affected[0].get("final_url") or affected[0]["url"]
    first_path = urlparse(first_url).path or "/"

    return [finding(
        "READ-001",
        "Page content is missing from the HTML a crawler receives",
        severity,
        evidence,
        refs,
        pages=[p["url"] for p in affected],
        counts={"affected_pages": n, "sampled_pages": m, "max_payload_bytes": max_payload},
        confidence=confidence,
        verification=f"curl -s {b.origin}{first_path} | wc -w, then compare with the page in a browser",
        scope="site-wide" if ratio >= 0.6 and m >= 3 else ("section" if n >= 2 else "page"),
        checked=m,
        action=act(
            "Server-render pages carrying primary content",
            severity,
            [
                "Configure server-side rendering (SSR) or static pre-rendering (SSG) for content routes",
                "Ensure headings, copy, and commercial specifications exist directly in the initial HTML response",
                f"Verify with curl that visible text is present in the response from {b.origin}{first_path}"
            ],
            "L",
            "Retrieval crawlers do not execute JavaScript before extracting content; server-rendering ensures facts are readable upon fetch.",
            owner="engineering"
        )
    )]


def check_read_002(b: Bundle) -> list[dict]:
    """A JavaScript-dependent page offers no noscript fallback.

    Binding guards:
      - Only applies to pages that are actually JS-dependent.
      - A noscript containing only 'Please enable JavaScript' is equivalent to none.
      - Low severity when READ-001 already fires on the same pages.
    """
    js_dependent = []
    for page in b.ok_pages:
        req = b.request(page["page_id"])
        if req.get("truncated"):
            continue
        ext = b.extracted(page["page_id"])
        if _is_client_rendered(page, ext):
            js_dependent.append(page)

    if not js_dependent:
        return []

    no_noscript = []
    for page in js_dependent:
        ext = b.extracted(page["page_id"])
        noscripts = ext.get("noscript") or []
        substantive = False
        for ns in noscripts:
            text = str(ns).strip().lower()
            # Guard: trivial enable-js messages are not substantive content
            words = text.split()
            if len(words) >= 10 and not all(w in ("please", "enable", "javascript", "to", "run", "this", "app", "view", "page", "browser") for w in words):
                substantive = True
                break
        if not substantive:
            no_noscript.append(page)

    if not no_noscript:
        return []

    n = len(no_noscript)
    # Severity rule: "medium; low when READ-001 already fires on the same pages."
    severity = "low"

    refs = [f"pages/{p['page_id']}/extracted.json" for p in no_noscript[:5]]
    first_path = urlparse(no_noscript[0].get("final_url") or no_noscript[0]["url"]).path or "/"

    return [finding(
        "READ-002",
        "A JavaScript-dependent page offers no noscript fallback",
        severity,
        f"{n} client-rendered pages contain no substantive noscript fallback content.",
        refs,
        pages=[p["url"] for p in no_noscript],
        counts={"pages_without_noscript": n, "js_dependent_pages": len(js_dependent)},
        verification=f"curl -s {b.origin}{first_path} | grep -c '<noscript'",
        scope="site-wide" if n >= 3 and n / len(b.ok_pages) >= 0.6 else "section",
        checked=len(b.ok_pages),
        action=act(
            "Provide accessible noscript fallback or implement SSR",
            severity,
            [
                "Add a <noscript> element containing core identity, navigation, and page text summary",
                "Migrate client-only routes to server-side rendering as the permanent architectural solution"
            ],
            "M",
            "A substantive noscript block provides baseline text when crawlers or user agents do not run script engines.",
            code=f"<noscript>\n  <h1>{b.site}</h1>\n  <p>Please visit {b.origin} with JavaScript or view our server-rendered sitemap.</p>\n</noscript>\n",
            owner="engineering"
        )
    )]


def check_read_003(b: Bundle) -> list[dict]:
    """Very little of the page is text a machine can read.

    Binding guards:
      - Weak signal on its own; never report above 'medium'.
      - Never report on a site where READ-001 already explains the ratio.
      - Heavy inline SVG or large CSS depresses ratio without harming extraction.
        Check whether text content is genuinely thin before reporting.
    """
    # Guard: never on a site where READ-001 already explains the ratio
    for page in b.ok_pages:
        req = b.request(page["page_id"])
        if not req.get("truncated") and _is_client_rendered(page, b.extracted(page["page_id"])):
            return []

    ratios = []
    main_word_counts = []
    for page in b.ok_pages:
        req = b.request(page["page_id"])
        if req.get("truncated"):
            continue
        text_obj = b.extracted(page["page_id"]).get("text") or {}
        r = text_obj.get("text_to_markup_ratio")
        w = text_obj.get("main_word_count", 0)
        if isinstance(r, (int, float)):
            ratios.append(r)
            main_word_counts.append(w)

    if len(ratios) < 3:
        return []

    med_ratio = statistics.median(ratios)
    med_words = statistics.median(main_word_counts)

    # Guard: heavy SVG/CSS depresses ratio without harming extraction; require text to be thin
    if med_words >= 150 or med_ratio >= 0.08:
        return []

    severity = "medium" if med_ratio < 0.04 else "low"
    refs = [f"pages/{p['page_id']}/extracted.json" for p in b.ok_pages[:5]]

    return [finding(
        "READ-003",
        "Very little of the page is text a machine can read",
        severity,
        f"Median text-to-markup ratio across {len(ratios)} pages is {med_ratio:.4f} (median main content: {int(med_words)} words).",
        refs,
        counts={"median_text_to_markup_ratio": round(med_ratio, 4), "pages_sampled": len(ratios)},
        confidence="medium",
        verification=f"curl -s {b.origin}/ | wc -c and compare with text length",
        scope="site-wide",
        checked=len(b.ok_pages),
        action=act(
            "Increase readable text and streamline page markup",
            severity,
            [
                "Move large inline SVGs and base64 styles into external assets",
                "Ensure core marketing and product statements are present as readable paragraphs rather than UI chrome"
            ],
            "M",
            "A high markup-to-text ratio dilutes keyword density and slows extraction algorithms that prioritize high-information density chunks.",
            owner="engineering"
        )
    )]


def check_read_004(b: Bundle) -> list[dict]:
    """Key facts exist only inside images.

    Detection: model-judged.
    Binding guards:
      - Requires model judgment about image content; base finding on surrounding
        context and cap confidence at 'medium'.
      - Never emit severity 'critical'.
      - Decorative alt='' is valid; alt=null is absent.
      - Logos, hero photos, background images carry no facts.
    """
    affected_pages = []
    image_examples = []

    for page in b.ok_pages:
        pid = page["page_id"]
        ext = b.extracted(pid)
        headings = ext.get("headings") or []
        text_obj = ext.get("text") or {}
        images = ext.get("images") or []

        # Look for fact-bearing contexts
        has_fact_heading = any(
            any(k in h.get("text", "").lower() for k in ("pricing", "plan", "menu", "hours", "spec", "rates", "schedule", "contact"))
            for h in headings
        )
        is_fact_page = page.get("page_type") in ("pricing", "contact")

        if (has_fact_heading or is_fact_page) and text_obj.get("main_word_count", 0) < 60:
            for img in images:
                # Guard: decorative alt="" is correct; count only alt is None
                if img.get("alt") is None:
                    src = img.get("src") or ""
                    low_src = src.lower()
                    # Guard: logos, hero, and background graphics carry no facts
                    if not any(k in low_src for k in ("logo", "hero", "bg", "icon", "banner", "avatar")):
                        affected_pages.append(page)
                        image_examples.append((page["url"], src))
                        break

    if not affected_pages:
        return []

    # Model-judged check: never critical, confidence medium
    severity = "high"
    first_url, first_src = image_examples[0]

    return [finding(
        "READ-004",
        "Key facts exist only inside images",
        severity,
        f"{first_url} presents commercial facts in an image ({first_src}) with no alt attribute, and the page text contains no equivalent statement.",
        [f"pages/{p['page_id']}/extracted.json" for p in affected_pages[:5]],
        pages=[p["url"] for p in affected_pages],
        counts={"affected_pages": len(affected_pages)},
        confidence="medium",
        determinism="model-judged",
        verification=f"Open {first_url} and try to select the facts as text",
        scope="section" if len(affected_pages) > 1 else "page",
        checked=len(b.ok_pages),
        action=act(
            "Transcribe image facts into readable HTML text",
            severity,
            [
                "Add an informative alt attribute describing all data points shown in the image",
                "Duplicate key figures, pricing, or hours into HTML text directly adjacent to the image"
            ],
            "S",
            "Retrieval systems cannot parse text embedded in image bitmaps; visible HTML text makes facts extractable.",
            owner="content"
        )
    )]


def check_read_005(b: Bundle) -> list[dict]:
    """Important content is published only as PDF.

    Binding guards:
      - PDFs are legitimate for forms, brochures, annual reports and datasheets.
        Report only when PDF is the ONLY home of content a visitor expects on a page.
      - Infer importance from link text and context; keep confidence at 'medium'.
    """
    pdf_links = []
    for page in b.ok_pages:
        ext = b.extracted(page["page_id"])
        for link in ext.get("links") or []:
            href = (link.get("href") or "").strip()
            text = (link.get("text") or "").strip().lower()
            if href.lower().endswith(".pdf") and link.get("internal"):
                pdf_links.append((href, text, page))

    if not pdf_links:
        return []

    # Check whether core commercial facts (pricing, specs, menu, terms) are PDF-only
    commercial_terms = ("pricing", "rates", "rate card", "specifications", "specs", "menu", "terms")
    commercial_pdfs = []
    for href, text, page in pdf_links:
        combined = f"{href} {text}".lower()
        if any(term in combined for term in commercial_terms):
            commercial_pdfs.append((href, text, page))

    if not commercial_pdfs:
        return []

    # Check if there is an HTML equivalent page in the bundle
    page_urls_lower = [(p.get("url") or "").lower() for p in b.pages]
    page_types = {p.get("page_type") for p in b.pages}

    uncovered = []
    for href, text, page in commercial_pdfs:
        has_html_page = False
        for term in ("pricing", "menu", "terms"):
            if term in href.lower() or term in text:
                if term in page_types or any(term in u for u in page_urls_lower):
                    has_html_page = True
                    break
        if not has_html_page:
            uncovered.append((href, page))

    if not uncovered:
        return []

    # Severity: high for core commercial facts (pricing/specs); medium otherwise
    severity = "high"
    examples = [href for href, _ in uncovered[:3]]
    affected_pages = sorted(list({p["url"] for _, p in uncovered}))

    refs = ["coverage.json"] + [f"pages/{p['page_id']}/extracted.json" for _, p in uncovered[:4]]

    return [finding(
        "READ-005",
        "Important content is published only as PDF",
        severity,
        f"{len(uncovered)} PDF links carry core commercial facts with no HTML equivalent: {', '.join(examples)}.",
        refs,
        pages=affected_pages,
        counts={"uncovered_pdfs": len(uncovered)},
        confidence="medium",
        verification=f"Search the site for an HTML page covering the same material as {examples[0]}",
        scope="section" if len(affected_pages) > 1 else "page",
        checked=len(b.ok_pages),
        action=act(
            "Publish key PDF content as standard HTML pages",
            severity,
            [
                "Create web page versions for pricing, menu, and product specification documents",
                "Retain the PDF as a downloadable attachment alongside the readable HTML content"
            ],
            "M",
            "Crawlers prioritize HTML over binary documents; HTML pages allow search engines and AI assistants to index and link directly to specific facts.",
            owner="content"
        )
    )]


def check_read_006(b: Bundle) -> list[dict]:
    """Video or audio content has no transcript.

    Detection: model-judged.
    Binding guards:
      - Only report when video carries the content rather than supplements it,
        indicated by low word count (< 100 words).
      - Do not report on media libraries or channel indexes.
      - Never emit severity 'critical'.
    """
    affected = []
    for page in b.ok_pages:
        if page.get("page_type") in ("other", "gallery"):
            continue
        pid = page["page_id"]
        ext = b.extracted(pid)
        text_obj = ext.get("text") or {}
        iframes = ext.get("iframes") or []

        media_iframes = []
        for ifr in iframes:
            if any(host in ifr.lower() for host in VIDEO_HOST_PATTERNS):
                media_iframes.append(ifr)

        if media_iframes and text_obj.get("main_word_count", 0) < 100:
            # Check whether a transcript or text summary heading is present
            headings = [h.get("text", "").lower() for h in ext.get("headings") or []]
            body_text = (text_obj.get("main") or "").lower()
            if not any("transcript" in h or "summary" in h for h in headings) and "transcript" not in body_text:
                affected.append((page, media_iframes[0], text_obj.get("main_word_count", 0)))

    if not affected:
        return []

    severity = "medium"
    first_page, first_provider, words = affected[0]
    provider_name = "YouTube" if "youtu" in first_provider else "video"

    refs = [f"pages/{p['page_id']}/extracted.json" for p, _, _ in affected[:5]]

    return [finding(
        "READ-006",
        "Video or audio content has no transcript",
        severity,
        f"{first_page['url']} embeds {provider_name} media and contains only {words} words of body text with no transcript.",
        refs,
        pages=[p["url"] for p, _, _ in affected],
        counts={"affected_pages": len(affected)},
        confidence="medium",
        determinism="model-judged",
        verification=f"Open {first_page['url']} and look for a transcript or written summary",
        scope="page" if len(affected) == 1 else "section",
        checked=len(b.ok_pages),
        action=act(
            "Publish written transcripts or summaries for multimedia content",
            severity,
            [
                "Add an HTML transcript or summary section directly beneath each video or audio embed",
                "Highlight key statements, data, and answers in the text outline"
            ],
            "M",
            "Audio/video cannot be parsed by standard text retrieval pipelines without speech-to-text transcripts.",
            owner="content"
        )
    )]


def check_read_007(b: Bundle) -> list[dict]:
    """Content is delivered inside an iframe or third-party widget.

    Binding guards:
      - Maps, video players, and payment widgets are legitimate; never report those.
      - Report third-party review widgets at 'medium' and recommend mirroring
        aggregate values as text plus structured data.
    """
    widget_pages = []
    for page in b.ok_pages:
        pid = page["page_id"]
        ext = b.extracted(pid)
        iframes = ext.get("iframes") or []

        detected_hosts = set()
        for ifr in iframes:
            low = ifr.lower()
            if any(legit in low for legit in LEGITIMATE_IFRAMES):
                continue
            if any(vid in low for vid in VIDEO_HOST_PATTERNS):
                continue
            if any(rw in low for rw in REVIEW_WIDGET_DOMAINS) or "widget" in low or "embed" in low:
                host = urlparse(ifr).netloc or ifr[:40]
                detected_hosts.add(host)

        if detected_hosts:
            widget_pages.append((page, sorted(list(detected_hosts))))

    if not widget_pages:
        return []

    severity = "medium"
    first_page, first_hosts = widget_pages[0]
    refs = [f"pages/{p['page_id']}/extracted.json" for p, _ in widget_pages[:5]]

    return [finding(
        "READ-007",
        "Content is delivered inside an iframe or third-party widget",
        severity,
        f"{first_page['url']} loads {len(first_hosts)} iframe(s) from {', '.join(first_hosts)}; iframe content is not part of this page for extraction purposes.",
        refs,
        pages=[p["url"] for p, _ in widget_pages],
        counts={"pages_with_widgets": len(widget_pages)},
        verification=f"curl -s {first_page['url']} and confirm the iframe body text is absent",
        scope="section" if len(widget_pages) > 1 else "page",
        checked=len(b.ok_pages),
        action=act(
            "Mirror third-party widget metrics into page text and structured data",
            severity,
            [
                "Extract aggregate ratings and review counts from the widget provider",
                "Render the rating value and total count into visible HTML text",
                "Add an AggregateRating JSON-LD schema block to the page"
            ],
            "S",
            "Widgets rendered inside iframes do not expose their DOM tree to parent page crawlers; mirroring figures into the host document preserves extractability.",
            owner="engineering"
        )
    )]


def check_read_008(b: Bundle) -> list[dict]:
    """Informational images lack alternative text.

    Binding guards:
      - alt='' is CORRECT for decorative images and must NEVER be counted as a defect.
        Count only alt=null (attribute absent).
      - Icons, spacers, and background images do not need alt text.
        Where most missing-alt images are small or icon-named, lower severity to 'low'.
    """
    total_images = 0
    missing_alt_images = []
    missing_by_page = {}

    for page in b.ok_pages:
        pid = page["page_id"]
        ext = b.extracted(pid)
        for img in ext.get("images") or []:
            total_images += 1
            # Binding guard: alt='' is decorative and correct. Check only alt is None
            if img.get("alt") is None:
                missing_alt_images.append(img)
                missing_by_page.setdefault(page["url"], []).append(img)

    if not missing_alt_images or total_images == 0:
        return []

    # Guard: check if missing images are mostly small or icons
    substantive_missing = 0
    for img in missing_alt_images:
        src = (img.get("src") or "").lower()
        w = img.get("width")
        h = img.get("height")
        is_icon = any(k in src for k in ("icon", "spacer", "bullet", "arrow", "chevron", "badge", "divider"))
        is_small = (w is not None and w <= 32) or (h is not None and h <= 32)
        if not (is_icon or is_small):
            substantive_missing += 1

    ratio = len(missing_alt_images) / total_images
    if substantive_missing >= 3 and ratio >= 0.30:
        severity = "medium"
    else:
        severity = "low"

    p_count = len(missing_by_page)
    affected_urls = sorted(list(missing_by_page.keys()))

    refs = []
    for page in b.ok_pages:
        if page["url"] in missing_by_page and len(refs) < 5:
            refs.append(f"pages/{page['page_id']}/extracted.json")

    return [finding(
        "READ-008",
        "Informational images lack alternative text",
        severity,
        f"{len(missing_alt_images)} of {total_images} images across {p_count} sampled pages have no alt attribute.",
        refs,
        pages=affected_urls,
        counts={
            "missing_alt": len(missing_alt_images),
            "total_images": total_images,
            "substantive_missing": substantive_missing
        },
        verification=f"curl -s {affected_urls[0]} | grep -c '<img' and compare with the alt count",
        scope="site-wide" if p_count >= 3 and p_count / len(b.ok_pages) >= 0.6 else "section",
        checked=len(b.ok_pages),
        action=act(
            "Add alt attributes to informative images and mark decorative images empty",
            severity,
            [
                "Inspect images with missing alt attributes across content templates",
                "Provide descriptive alt text for diagrams, product photos, and informative figures",
                "Set alt=\"\" explicitly on purely decorative icons, spacers, and background graphics"
            ],
            "S",
            "Alternative text allows visual content to be indexed and cited by multimodal and text retrieval engines.",
            owner="content"
        )
    )]


def check_read_009(b: Bundle) -> list[dict]:
    """Heading structure does not describe the page.

    Binding guards:
      - Multiple h1 elements are valid HTML5 in sectioned content. Report only
        when h1s are unrelated, and keep severity at 'low'.
      - A single skipped level is trivial. Require a pattern across pages.
      - Do not report on pages where READ-001 fires.
    """
    eligible_pages = []
    for page in b.ok_pages:
        req = b.request(page["page_id"])
        if req.get("truncated"):
            continue
        ext = b.extracted(page["page_id"])
        # Guard: Do not report on pages where READ-001 fires
        if _is_client_rendered(page, ext):
            continue
        eligible_pages.append(page)

    if not eligible_pages:
        return []

    no_h1 = []
    skipped_levels = []
    multiple_h1 = []

    for page in eligible_pages:
        ext = b.extracted(page["page_id"])
        headings = ext.get("headings") or []
        h1s = [h for h in headings if h.get("level") == 1]

        if not h1s:
            no_h1.append(page)
        elif len(h1s) > 1:
            # Guard: check if h1 texts are clearly distinct/unrelated
            texts = {h.get("text", "").strip() for h in h1s}
            if len(texts) > 1:
                multiple_h1.append(page)

        # Check skipped levels (e.g. h1 followed directly by h3 or h4)
        for i in range(len(headings) - 1):
            curr_lvl = headings[i].get("level", 1)
            next_lvl = headings[i + 1].get("level", 1)
            if next_lvl > curr_lvl + 1:
                skipped_levels.append((page, curr_lvl, next_lvl))
                break

    problems = []
    affected = set()

    if no_h1:
        problems.append(f"{len(no_h1)} have no <h1>")
        for p in no_h1:
            affected.add(p["url"])
    if len(multiple_h1) >= 2:
        problems.append(f"{len(multiple_h1)} have multiple <h1> tags")
        for p in multiple_h1:
            affected.add(p["url"])
    # Guard: require a pattern across pages for skipped levels
    if len(skipped_levels) >= 2:
        problems.append(f"{len(skipped_levels)} skip heading levels")
        for p, _, _ in skipped_levels:
            affected.add(p["url"])

    if not problems:
        return []

    severity = "medium" if len(no_h1) >= 2 or (len(no_h1) + len(multiple_h1) >= 3) else "low"
    sorted_affected = sorted(list(affected))

    refs = []
    for page in eligible_pages:
        if page["url"] in affected and len(refs) < 5:
            refs.append(f"pages/{page['page_id']}/extracted.json")

    return [finding(
        "READ-009",
        "Heading structure does not describe the page",
        severity,
        f"{len(sorted_affected)} of {len(eligible_pages)} pages exhibit heading hierarchy breaks: {'; '.join(problems)}.",
        refs,
        pages=sorted_affected,
        counts={"affected_pages": len(sorted_affected), "sampled_pages": len(eligible_pages)},
        verification=f"curl -s {sorted_affected[0]} | grep -oE '<h[1-6]'",
        scope="site-wide" if len(sorted_affected) / len(eligible_pages) >= 0.6 and len(eligible_pages) >= 3 else "section",
        checked=len(eligible_pages),
        action=act(
            "Structure content with hierarchical heading tags",
            severity,
            [
                "Ensure every page has exactly one distinct <h1> summarizing its subject",
                "Follow sequential descending levels (h1 -> h2 -> h3) without skipping intermediate ranks",
                "Avoid using heading tags merely for visual styling"
            ],
            "S",
            "Headings define chunk boundaries during semantic retrieval; consistent hierarchy ensures snippets retain their parent topic context.",
            owner="content"
        )
    )]


def check_read_010(b: Bundle) -> list[dict]:
    """The page uses no semantic landmarks.

    Binding guards:
      - Non-semantic markup degrades main-content extraction but rarely prevents it.
        Never report above 'medium'.
      - ARIA landmark roles are equivalent to the elements. Check for role='main'
        before reporting a missing <main>.
    """
    affected = []
    for page in b.ok_pages:
        pid = page["page_id"]
        raw = b.raw_html(pid).lower()
        if not raw:
            continue

        has_main = ("<main" in raw) or ('role="main"' in raw) or ("role='main'" in raw)
        has_article = ("<article" in raw) or ('role="article"' in raw) or ("role='article'" in raw)
        has_nav = ("<nav" in raw) or ('role="navigation"' in raw) or ("role='navigation'" in raw)

        if not (has_main or has_article or has_nav):
            affected.append(page)

    if not affected:
        return []

    # Severity rule: "low; medium only when combined with poor heading structure."
    severity = "low"
    refs = [f"pages/{p['page_id']}/raw.html" for p in affected[:5]]
    urls = [p["url"] for p in affected]

    return [finding(
        "READ-010",
        "The page uses no semantic landmarks",
        severity,
        f"{len(affected)} pages contain no <main>, <article> or <nav> element or equivalent ARIA landmark role.",
        refs,
        pages=urls,
        counts={"pages_without_landmarks": len(affected)},
        verification=f"curl -s {urls[0]} | grep -cE '<(main|article|nav|header|footer)'",
        scope="site-wide" if len(affected) / len(b.ok_pages) >= 0.6 and len(b.ok_pages) >= 3 else "section",
        checked=len(b.ok_pages),
        action=act(
            "Add HTML5 landmark elements to template layouts",
            severity,
            [
                "Wrap the primary page content in a <main> landmark element",
                "Wrap navigation menus in <nav> and header sections in <header>",
                "Use <article> for standalone self-contained posts or documentation entries"
            ],
            "S",
            "Semantic landmarks allow content extractors to reliably strip repetitive navigation and isolate primary body text.",
            code="<header>\n  <nav><!-- Navigation --></nav>\n</header>\n<main>\n  <!-- Primary Content -->\n</main>\n",
            owner="engineering"
        )
    )]


def check_read_011(b: Bundle) -> list[dict]:
    """Content behind tabs or accordions is absent from the HTML.

    Detection: model-judged.
    Binding guards:
      - Accordions and tabs that render into the DOM and hide with CSS are FINE.
        Only report when panel text is genuinely absent from the HTML.
      - Set determinism to model-judged and confidence to 'medium'.
    """
    affected = []
    tab_patterns = re.compile(r"""(?:role=['"]tabpanel['"]|class=['"][^'"]*tab-pane[^'"]*['"])[^>]*>(\s*<[^>]+>)*\s*</(?:div|section)>""", re.I)

    for page in b.ok_pages:
        pid = page["page_id"]
        raw = b.raw_html(pid)
        if not raw:
            continue

        has_tab_controls = any(marker in raw for marker in ("role=\"tab\"", "role='tab'", "data-toggle=\"tab\"", "class=\"accordion-header\""))
        if has_tab_controls:
            # Guard: check if panels are empty in raw HTML
            empty_match = tab_patterns.search(raw)
            has_ajax_tab = "data-tab-url" in raw or "data-ajax-tab" in raw
            if empty_match or has_ajax_tab:
                affected.append(page)

    if not affected:
        return []

    severity = "medium"
    urls = [p["url"] for p in affected]
    refs = [f"pages/{p['page_id']}/raw.html" for p in affected[:5]]

    return [finding(
        "READ-011",
        "Content behind tabs or accordions is absent from the HTML",
        severity,
        f"{urls[0]} shows tab or accordion controls whose panel content is not present in the HTML.",
        refs,
        pages=urls,
        counts={"affected_pages": len(affected)},
        confidence="medium",
        determinism="model-judged",
        verification=f"curl -s {urls[0]} and search for the text shown after clicking each tab",
        scope="page" if len(affected) == 1 else "section",
        checked=len(b.ok_pages),
        action=act(
            "Render tab and accordion panels into the DOM and toggle via CSS",
            severity,
            [
                "Render all tabpanel content into initial HTML on server load",
                "Toggle inactive panel visibility with hidden attribute or CSS display:none"
            ],
            "M",
            "When panel text is in the DOM, retrieval crawlers extract the full text regardless of initial visual state.",
            code="<div role=\"tabpanel\" id=\"panel-1\">\n  <p>Full content rendered here, hidden visually until active.</p>\n</div>\n",
            owner="engineering"
        )
    )]


def check_read_012(b: Bundle) -> list[dict]:
    """Paginated content has no crawlable URLs.

    Applies when: ecommerce, media-publisher, marketplace, docs.
    Binding guards:
      - Check for <link rel='next'> and for anchor-based pagination before reporting.
        Many infinite-scroll implementations layer over real URLs, which is correct.
    """
    profile = b.run.get("site_profile") or ""
    catalog_types = {"ecommerce", "media-publisher", "marketplace", "docs"}

    has_catalog_profile = profile in catalog_types
    catalog_pages = [p for p in b.ok_pages if p.get("page_type") in ("category", "product", "docs") or has_catalog_profile]

    if not catalog_pages:
        return []

    affected = []
    for page in catalog_pages:
        pid = page["page_id"]
        raw = b.raw_html(pid)
        ext = b.extracted(pid)

        # Look for infinite scroll or dynamic load more indicators
        has_infinite = any(k in raw.lower() for k in ("infinite-scroll", "load-more", "loadmorebtn", "data-infinite"))
        if has_infinite:
            # Guard: check for crawlable pagination links
            links = ext.get("links") or []
            has_next_link = "<link rel=\"next\"" in raw.lower() or "<link rel='next'" in raw.lower()
            has_page_url = any(
                ("rel" in l and l.get("rel") == "next") or
                ("page=" in (l.get("href") or "").lower() or "?p=" in (l.get("href") or "").lower() or "/page/" in (l.get("href") or "").lower())
                for l in links
            )
            if not (has_next_link or has_page_url):
                affected.append(page)

    if not affected:
        return []

    severity = "medium"
    urls = [p["url"] for p in affected]
    refs = [f"pages/{p['page_id']}/extracted.json" for p in affected[:5]]

    return [finding(
        "READ-012",
        "Paginated content has no crawlable URLs",
        severity,
        f"{urls[0]} loads additional items without exposing paginated URLs.",
        refs,
        pages=urls,
        counts={"affected_pages": len(affected)},
        verification="Disable JavaScript and check whether page 2 of the listing is reachable",
        scope="section" if len(affected) > 1 else "page",
        checked=len(b.ok_pages),
        action=act(
            "Expose standard linked pagination URLs alongside infinite scroll",
            severity,
            [
                "Provide standard <a href=\"?page=2\" rel=\"next\"> links in page markup",
                "Ensure server routes handle direct URL requests for paginated catalog slices"
            ],
            "M",
            "Crawlers discover catalog depth by traversing URL links; infinite scroll without anchor links traps crawlers on page one.",
            code="<nav aria-label=\"Pagination\">\n  <a href=\"/catalog?page=2\" rel=\"next\">Next Page</a>\n</nav>\n",
            owner="engineering"
        )
    )]


def check_read_013(b: Bundle) -> list[dict]:
    """A consent wall or interstitial hides the content.

    Binding guards:
      - A cookie banner overlaying fully-served content is NOT this finding.
        Report only when content itself is absent until consent is given.
      - Legally mandated consent flows are not defects; recommend serving content
        beneath banner.
      - This finding supersedes READ-001, QUOTE-001 and STAY-001 on the same page.
    """
    affected = []
    matched_signature = ""

    # Check ua_probe baseline for challenge or interstitial
    probe_base = b.probe.get("baseline") or {}
    if probe_base.get("challenge_detected"):
        matched_signature = "bot challenge / interstitial"

    for page in b.ok_pages:
        pid = page["page_id"]
        raw = b.raw_html(pid).lower()
        ext = b.extracted(pid)
        text_obj = ext.get("text") or {}
        words = text_obj.get("main_word_count", 0)

        # Check for CMP presence
        cmp_found = None
        for sig in CONSENT_SIGNATURES:
            if sig in raw:
                cmp_found = sig
                break

        # Guard: only report when content itself is absent
        if (cmp_found or matched_signature) and words < 50:
            affected.append((page, cmp_found or matched_signature, words))

    if not affected:
        return []

    first_page, signature, words = affected[0]
    severity = "critical" if words < 20 else "high"
    urls = [p["url"] for p, _, _ in affected]

    refs = []
    if b.exists("ua_probe.json"):
        refs.append("ua_probe.json")
    for p, _, _ in affected[:4]:
        refs.append(f"pages/{p['page_id']}/raw.html")

    return [finding(
        "READ-013",
        "A consent wall or interstitial hides the content",
        severity,
        f"{first_page['url']} returns {words} words of body text and a consent interstitial matching {signature}.",
        refs,
        pages=urls,
        counts={"affected_pages": len(affected), "body_words": words},
        verification=f"curl -s {first_page['url']} | head -c 2000 and check whether article text is present",
        scope="site-wide" if len(affected) / len(b.ok_pages) >= 0.6 and len(b.ok_pages) >= 3 else "section",
        checked=len(b.ok_pages),
        action=act(
            "Serve readable content underneath consent overlays",
            severity,
            [
                "Render body content into the server HTML payload",
                "Display consent dialogs as CSS overlays rather than conditioning HTML generation on prior consent",
                "Ensure verified bot user-agents receive content without interstitial redirection"
            ],
            "M",
            "Crawlers cannot complete interactive consent dialogs; content must be present in the initial response stream.",
            owner="engineering"
        )
    )]


def check_read_014(b: Bundle) -> list[dict]:
    """Public content sits behind a login or paywall.

    Binding guards:
      - A paywall is a business model, not a defect. For deliberately paywalled
        content, report ONLY the absence of isAccessibleForFree / hasPart markup.
      - Never recommend removing authentication from genuinely private areas.
    """
    login_pages = []
    paywall_without_markup = []

    for page in b.ok_pages:
        url_lower = (page.get("url") or "").lower()
        # Guard: skip genuinely private utility areas
        if any(hint in url_lower for hint in UTILITY_PATH_HINTS):
            continue

        pid = page["page_id"]
        ext = b.extracted(pid)
        forms = ext.get("forms") or []
        text_obj = ext.get("text") or {}
        raw = b.raw_html(pid).lower()
        jsonld_blocks = ext.get("jsonld") or []

        # Check for paywall presence. Evidence has to come from what a READER
        # sees, not from the page's scripts: a CMS that ships a `paywall: false`
        # config flag in its JavaScript is not paywalled, and matching the raw
        # HTML called six vox.com articles paywalled on a site with no paywall.
        # Require the wall to be visible in the extracted text, on a page whose
        # body is short enough to be cut off -- or an explicit
        # isAccessibleForFree: false declaration.
        visible = ((text_obj.get("main") or "") + " " + (text_obj.get("full") or "")).lower()
        wall_phrase = any(k in visible for k in (
            "subscribe to continue", "subscribe to read", "subscription required",
            "subscriber-only", "subscribers only", "to continue reading",
            "unlock this article", "this article is for subscribers"))
        declared_paid = any(
            isinstance(jb.get("value"), dict)
            and jb["value"].get("isAccessibleForFree") in (False, "False", "false")
            for jb in jsonld_blocks)
        is_paywalled = declared_paid or (
            wall_phrase and (text_obj.get("main_word_count") or 0) < 250)
        if is_paywalled:
            has_free_markup = False
            for jb in jsonld_blocks:
                val = jb.get("value")
                if isinstance(val, dict) and "isAccessibleForFree" in val:
                    has_free_markup = True
                    break
            if not has_free_markup:
                paywall_without_markup.append(page)

        # Check for login form replacing public content
        has_login_form = any("login" in (f.get("action") or "").lower() or "signin" in (f.get("action") or "").lower() for f in forms)
        if (has_login_form or "please sign in" in raw) and text_obj.get("main_word_count", 0) < 40:
            if page.get("page_type") in ("article", "product", "pricing", "docs"):
                login_pages.append(page)

    out = []
    if login_pages:
        urls = [p["url"] for p in login_pages]
        refs = [f"pages/{p['page_id']}/extracted.json" for p in login_pages[:5]]
        out.append(finding(
            "READ-014",
            "Public content sits behind a login or paywall",
            "high",
            f"{len(login_pages)} pages returned a login form in place of public content.",
            refs,
            pages=urls,
            counts={"login_pages": len(login_pages)},
            verification=f"Open {urls[0]} in a private browser window",
            scope="section" if len(login_pages) > 1 else "page",
            checked=len(b.ok_pages),
            action=act(
                "Make public content accessible without authentication",
                "high",
                [
                    "Verify route access controls for public pages",
                    "Allow unauthenticated reading for marketing and educational content"
                ],
                "S",
                "Content behind mandatory login walls cannot be accessed, parsed, or cited by external AI services.",
                owner="engineering"
            )
        ))

    if paywall_without_markup:
        urls = [p["url"] for p in paywall_without_markup]
        refs = [f"pages/{p['page_id']}/extracted.json" for p in paywall_without_markup[:5]]
        out.append(finding(
            "READ-014",
            "Paywalled content lacks machine-readable paywall declarations",
            "medium",
            f"{len(paywall_without_markup)} paywalled pages declare no isAccessibleForFree schema markup.",
            refs,
            pages=urls,
            counts={"paywall_pages": len(paywall_without_markup)},
            verification=f"curl -s {urls[0]} | grep -i 'isAccessibleForFree'",
            scope="section" if len(paywall_without_markup) > 1 else "page",
            checked=len(b.ok_pages),
            action=act(
                "Add isAccessibleForFree and hasPart schema markup to paywalled pages",
                "medium",
                [
                    "Add schema.org/NewsArticle or CreativeWork with isAccessibleForFree: false",
                    "Specify the CSS selector of the gated portion inside hasPart"
                ],
                "S",
                "Explicit paywall markup tells search engines and assistants that the gate is intentional, allowing them to index and cite lead paragraphs legitimately.",
                code="<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"NewsArticle\",\n  \"isAccessibleForFree\": false,\n  \"hasPart\": {\n    \"@type\": \"WebPageElement\",\n    \"isAccessibleForFree\": false,\n    \"cssSelector\": \".paywall-content\"\n  }\n}\n</script>\n",
                owner="engineering"
            )
        ))

    return out


def check_read_015(b: Bundle) -> list[dict]:
    """Text is rendered in a form machines cannot read.

    Binding guards:
      - SVG containing <text> or <title> elements IS readable. Only report text-less SVG.
      - Charts and diagrams as images are normal.
    """
    affected = []
    canvas_re = re.compile(r"<canvas[^>]*>(\s*<[^>]+>)*\s*</canvas>", re.I)

    for page in b.ok_pages:
        pid = page["page_id"]
        raw = b.raw_html(pid)
        ext = b.extracted(pid)
        text_obj = ext.get("text") or {}

        # Look for canvas elements without fallback text on low-word pages
        if "<canvas" in raw and text_obj.get("main_word_count", 0) < 100:
            if canvas_re.search(raw):
                affected.append((page, "<canvas>"))

    if not affected:
        return []

    severity = "medium"
    first_page, elem = affected[0]
    urls = [p["url"] for p, _ in affected]
    refs = [f"pages/{p['page_id']}/raw.html" for p, _ in affected[:5]]

    return [finding(
        "READ-015",
        "Text is rendered in a form machines cannot read",
        severity,
        f"{first_page['url']} renders {elem} containing no machine-readable fallback text.",
        refs,
        pages=urls,
        counts={"affected_pages": len(affected)},
        verification=f"Try to select and copy the text on {first_page['url']}",
        scope="page" if len(affected) == 1 else "section",
        checked=len(b.ok_pages),
        action=act(
            "Provide accessible HTML text fallbacks for canvas and graphic elements",
            severity,
            [
                "Provide text descriptions and data tables within the <canvas> tag",
                "Ensure graphic diagrams have accompanying data tables in HTML"
            ],
            "M",
            "HTML5 canvas elements draw raster pixels that cannot be parsed by text extractors.",
            code="<canvas id=\"chart\">\n  <p>Q3 Revenue: $4.2M, Growth: 18% YoY.</p>\n</canvas>\n",
            owner="engineering"
        )
    )]


def check_read_016(b: Bundle) -> list[dict]:
    """Character encoding or language is undeclared or wrong.

    Binding guards:
      - A charset in the Content-Type response header is sufficient; meta tag is
        not additionally required. Check headers before reporting.
      - Do not report missing lang as discoverability defect on monolingual English
        site -- keep at 'low' and frame as hygiene.
    """
    no_charset = []
    no_lang = []
    mojibake_pages = []

    for page in b.ok_pages:
        pid = page["page_id"]
        ext = b.extracted(pid)
        hdrs = b.headers(pid)

        # Check charset from meta and Content-Type header
        meta_charset = ext.get("charset")
        ct_header = hdrs.get("content-type", "")
        has_charset = bool(meta_charset) or ("charset=" in ct_header.lower())
        if not has_charset:
            no_charset.append(page)

        # Check lang attribute
        lang = ext.get("lang")
        if not lang or not lang.strip():
            no_lang.append(page)

        # Check for mojibake in visible text
        full_text = (ext.get("text") or {}).get("full") or ""
        if MOJIBAKE_PATTERN.search(full_text):
            mojibake_pages.append(page)

    out = []
    if mojibake_pages:
        urls = [p["url"] for p in mojibake_pages]
        refs = [f"pages/{p['page_id']}/extracted.json" for p in mojibake_pages[:5]]
        out.append(finding(
            "READ-016",
            "Corrupted character encoding (mojibake) in page text",
            "medium",
            f"{len(mojibake_pages)} pages contain corrupted encoding sequences (mojibake) in visible text.",
            refs,
            pages=urls,
            counts={"mojibake_pages": len(mojibake_pages)},
            verification=f"curl -sI {urls[0]} | grep -i content-type",
            scope="section" if len(mojibake_pages) > 1 else "page",
            checked=len(b.ok_pages),
            action=act(
                "Fix encoding pipeline to output clean UTF-8 text",
                "medium",
                [
                    "Ensure source files and database connections use UTF-8 encoding",
                    "Verify HTTP responses declare Content-Type: text/html; charset=utf-8"
                ],
                "S",
                "Mojibake garbles entity names and breaks word tokenization in retrieval models.",
                owner="engineering"
            )
        ))

    if no_charset or no_lang:
        affected_set = {p["url"] for p in (no_charset + no_lang)}
        urls = sorted(list(affected_set))
        first_page = (no_charset or no_lang)[0]
        refs = [f"pages/{p['page_id']}/extracted.json" for p in (no_charset or no_lang)[:5]]

        out.append(finding(
            "READ-016",
            "Character encoding or language is undeclared",
            "low",
            f"{len(no_charset)} pages declare no charset in headers or meta; {len(no_lang)} pages declare no lang attribute.",
            refs,
            pages=urls,
            counts={"no_charset": len(no_charset), "no_lang": len(no_lang)},
            verification=f"curl -sI {first_page['url']} | grep -i content-type",
            scope="site-wide" if len(urls) / len(b.ok_pages) >= 0.6 and len(b.ok_pages) >= 3 else "section",
            checked=len(b.ok_pages),
            action=act(
                "Declare UTF-8 charset and document language",
                "low",
                [
                    "Add <meta charset=\"utf-8\"> as the first child of <head>",
                    "Add lang=\"en\" (or appropriate language code) to the <html> tag",
                    "Include charset=utf-8 in the server Content-Type response header"
                ],
                "S",
                "Explicit declarations ensure language identification models process content accurately without misinterpreting characters.",
                code="<!doctype html>\n<html lang=\"en\">\n<head>\n  <meta charset=\"utf-8\">\n",
                owner="engineering"
            )
        ))

    return out


CHECKS = [
    check_read_001,
    check_read_002,
    check_read_003,
    check_read_004,
    check_read_005,
    check_read_006,
    check_read_007,
    check_read_008,
    check_read_009,
    check_read_010,
    check_read_011,
    check_read_012,
    check_read_013,
    check_read_014,
    check_read_015,
    check_read_016,
]

NOT_YET_IMPLEMENTED = []


def proactive(b: Bundle) -> list[dict]:
    """Proactive recommendations where no defect was found."""
    out = []

    # READ-P01: Pre-render commercial pages
    has_client_signals = False
    for p in b.ok_pages:
        ext = b.extracted(p["page_id"])
        sig = ext.get("render_signals") or {}
        # Only client-rendering frameworks count. Recommending "pre-render your
        # commercial pages" to a WordPress site that already server-renders them
        # is advice that reads as though we never looked.
        if sig.get("app_shell_selectors") or any(
                f in CLIENT_RENDERED_FRAMEWORKS
                for f in (sig.get("framework_markers") or [])):
            has_client_signals = True
            break

    if has_client_signals:
        out.append({
            "id": "P-000",  # READ-P01; orchestrator assigns the real id
            "title": "Server-render the pages that carry commercial facts",
            "category": CATEGORY,
            "mechanism": MECHANISM,
            "rationale": (
                "Rendering strategy can be chosen per route. Pricing, product and "
                "about pages carry the facts worth quoting and benefit most; an "
                "authenticated dashboard does not need to change at all."
            ),
            "suggested_action": act(
                "Pre-render key marketing and commercial routes to static HTML",
                "low",
                [
                    "Configure SSG/SSR for /pricing, /about, and /product pages",
                    "Verify with curl that visible content is present in raw HTML"
                ],
                "M",
                "Ensures citable facts are accessible to crawlers regardless of client runtime.",
                owner="engineering"
            )
        })

    # READ-P02: Mirror widget values
    has_widgets = False
    for p in b.ok_pages:
        ext = b.extracted(p["page_id"])
        for ifr in ext.get("iframes") or []:
            if any(rw in ifr.lower() for rw in REVIEW_WIDGET_DOMAINS):
                has_widgets = True
                break

    if has_widgets:
        out.append({
            "id": "P-000",  # READ-P02; orchestrator assigns the real id
            "title": "Mirror third-party widget values into the page as text",
            "category": CATEGORY,
            "mechanism": MECHANISM,
            "rationale": (
                "Aggregate values rendered by a widget are invisible to extraction. "
                "Writing the rating and review count into the page as text plus "
                "structured data keeps the widget and makes the numbers citable."
            ),
            "suggested_action": act(
                "Expose rating values in visible HTML and AggregateRating schema",
                "low",
                [
                    "Fetch rating scores and review counts during build time",
                    "Render values into the page layout as plain text alongside the widget"
                ],
                "S",
                "Makes review numbers accessible for assistant answers without relying on iframe execution.",
                owner="engineering"
            )
        })

    # READ-P03 / READ-P04 -- structural shape, measured against the GEO
    # literature. These are recommendations and never findings: Yu et al.
    # (arXiv:2603.29979) measure +17.3% citation rate (n=200 x 6 engines,
    # p<0.001, d=0.64) from structural transformation, but C-SEO Bench found
    # only 3 of 54 method-domain combinations significant, so the optimal edit
    # is instance-dependent. "This page has no table" is not a defect.
    structured = [(p_, b.extracted(p_["page_id"]).get("structure") or {})
                  for p_ in b.ok_pages]
    structured = [(p_, st) for p_, st in structured if st]
    if structured:
        fds = [st.get("format_density") or 0.0 for _, st in structured]
        median_fd = sorted(fds)[len(fds) // 2]
        if median_fd < 0.10:
            out.append({
                "id": "P-000",  # READ-P03
                "title": "Put the comparable facts in tables and lists, not paragraphs",
                "category": CATEGORY,
                "mechanism": MECHANISM,
                "rationale": (
                    "Across {n} sampled pages the median proportion of content in "
                    "tables, lists or code is {fd:.2f}. Structured formats are "
                    "reported to extract substantially more accurately than the "
                    "same facts in prose, and structural transformation measured "
                    "+17.3% citation rate across six generative engines. The "
                    "reported working range is roughly 0.25-0.35; above that, "
                    "readability suffers for humans."
                ).format(n=len(structured), fd=median_fd),
                "suggested_action": act(
                    "Move specifications, pricing tiers and step sequences into "
                    "tables and lists",
                    "low",
                    ["Convert any paragraph that enumerates options, steps or "
                     "specifications into a list or table",
                     "Keep one fact per row or item so a single row can be "
                     "lifted without its neighbours",
                     "Leave narrative as prose -- the goal is a mix, not a "
                     "document made entirely of tables"],
                    "M",
                    "A table row is a self-contained fact with its own labels. A "
                    "sentence buried mid-paragraph is not, and has to be "
                    "reconstructed before it can be quoted.",
                    owner="content"),
            })

        eds = [st.get("emphasis_density") or 0.0 for _, st in structured]
        median_ed = sorted(eds)[len(eds) // 2]
        if median_ed < 0.01 and median_fd < 0.25:
            out.append({
                "id": "P-000",  # READ-P04
                "title": "Mark the key terms so the important sentence is visibly the important one",
                "category": CATEGORY,
                "mechanism": MECHANISM,
                "rationale": (
                    "Median emphasis density across {n} sampled pages is {ed:.3f} "
                    "of body words; the range reported as useful is about "
                    "0.05-0.10. Emphasis is a weak signal on its own and this is "
                    "the least-supported item in the structural literature -- "
                    "worth doing while editing for other reasons, not worth a "
                    "dedicated pass."
                ).format(n=len(structured), ed=median_ed),
                "suggested_action": act(
                    "Emphasise the term each section is actually about",
                    "low",
                    ["Bold the subject term in the first sentence of each section",
                     "Do not emphasise whole sentences -- that marks nothing"],
                    "S",
                    "Emphasis marks which words carry the claim, which helps both "
                    "a reader skimming and a model weighting the passage.",
                    owner="content"),
            })

    return out


def main(argv=None) -> int:
    # Windows consoles default to a legacy codepage (cp1252 here), and evidence
    # strings quote real page content -- one arrow, curly quote, em dash or any
    # non-Latin script raises UnicodeEncodeError and aborts the entire audit.
    # The report is JSON and JSON is UTF-8, so say so explicitly.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # pragma: no cover - exotic stdout
        pass

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bundle")
    ap.add_argument("--out", help="write candidates here (default stdout)")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--deadline", type=float, default=None,
                    help="Unix time by which this script must have returned. The "
                         "orchestrator sets it from the audit's hard 270s cap. Checks "
                         "not reached are recorded in checks_cut_by_deadline, never "
                         "silently omitted.")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.bundle):
        print(f"error: {args.bundle!r} is not a bundle directory", file=sys.stderr)
        return 2

    b = Bundle(args.bundle)
    if not b.manifest:
        print(f"error: no readable MANIFEST.json in {args.bundle!r}", file=sys.stderr)
        return 2

    findings: list[dict] = []
    cut_by_deadline: list = []
    for check in CHECKS:
        # The audit has a hard wall-clock cap. A check that has not started by
        # the deadline is skipped and NAMED, so the report says what it did not
        # look at rather than implying a clean result.
        if args.deadline is not None and time.time() >= args.deadline:
            cut_by_deadline.append(check.__name__.replace("check_", "").replace("_", "-").upper())
            continue
        try:
            findings.extend(check(b) or [])
        except Exception as exc:
            # One broken check must never lose the others
            print(f"warning: {check.__name__} failed: {type(exc).__name__}: {exc}",
                  file=sys.stderr)

    # Drop any candidate whose refs do not resolve (false-positive gate 2)
    kept = []
    for f in findings:
        refs = f["evidence_detail"]["artifact_refs"]
        missing = [r for r in refs if not b.exists(r)]
        if missing:
            print(f"warning: dropping {f['check_id']}: unresolved refs {missing}",
                  file=sys.stderr)
            continue
        kept.append(f)

    result = {
        "skill": "render-extractability-audit",
        "mechanism": MECHANISM,
        "bundle": args.bundle,
        "findings": kept,
        "proactive_recommendations": proactive(b),
        "checks_not_implemented": NOT_YET_IMPLEMENTED
    }

    if cut_by_deadline:
        result["checks_cut_by_deadline"] = cut_by_deadline
        print(f"warning: deadline reached; {len(cut_by_deadline)} check(s) not run: "
              f"{', '.join(cut_by_deadline)}", file=sys.stderr)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out and not args.stdout:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
        print(f"{len(kept)} READ candidates -> {args.out}", file=sys.stderr)
        for f in kept:
            print(f"  {f['check_id']:11} {f['severity']:8} {f['title']}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

