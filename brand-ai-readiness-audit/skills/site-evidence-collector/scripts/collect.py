#!/usr/bin/env python3
"""Collect a normalized evidence bundle for one website.

Standard library only -- this ships inside the submission and must run on a bare
Python 3.9+ install.

One polite, robots-respecting, budget-bounded, read-only crawl. Writes the
bundle described by references/evidence-bundle.schema.json. Records what is on
each page; never decides what it means.

Usage:
    python collect.py https://example.com
    python collect.py example.com --out .audit/example.com/run-01 --max-pages 25
    python collect.py example.com --renderer "node render.js"   # optional
"""

from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import io
import json
import os
import re
import subprocess
import sys
import time
import zlib
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib import request, error
from urllib.parse import urljoin, urlparse, urlunparse, urldefrag

COLLECTOR_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0"

BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
# We identify ourselves honestly. A site that wishes to exclude us can.
AUDIT_UA = ("Mozilla/5.0 (compatible; BrandAIReadinessAudit/0.1; "
            "+read-only site audit; respects robots.txt)")

# Purpose taxonomy -- see references/ai-user-agents.md. The retrieval/training
# split is the marketplace's most important false-positive guard.
AI_AGENTS = {
    "ChatGPT-User": "retrieval",
    "OAI-SearchBot": "search-index",
    "GPTBot": "training",
    "Claude-User": "retrieval",
    "Claude-SearchBot": "search-index",
    "ClaudeBot": "mixed",
    "anthropic-ai": "training",
    "PerplexityBot": "search-index",
    "Perplexity-User": "retrieval",
    "Googlebot": "search-index",
    "Google-Extended": "training",
    "Bingbot": "search-index",
    "Amazonbot": "mixed",
    "Applebot": "search-index",
    "Applebot-Extended": "training",
    "meta-externalagent": "training",
    "CCBot": "training",
    "Bytespider": "training",
    "cohere-ai": "training",
    "Diffbot": "mixed",
    "omgilibot": "training",
    "YouBot": "search-index",
}

# Agents worth probing live. Keep short: each is an extra request.
PROBE_AGENTS = ["GPTBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
                "PerplexityBot", "Googlebot"]

CHALLENGE_SIGNATURES = [
    "cf-browser-verification", "just a moment...", "checking your browser",
    "attention required! | cloudflare", "__cf_chl", "access denied",
    "request unsuccessful. incapsula", "pardon our interruption",
    "perimeterx", "datadome", "enable javascript and cookies to continue",
]

SKIP_PATH_PATTERNS = re.compile(
    r"/(cart|checkout|account|login|logout|signin|signout|register|admin|"
    r"wp-admin|wp-login|my-account|basket|order|payment)(/|$|\?)", re.I)
SKIP_QUERY_PATTERNS = re.compile(
    r"(add-to-cart|remove_item|replytocom|share=|print=|sessionid|utm_)", re.I)

NON_HTML_EXT = re.compile(
    r"\.(pdf|zip|gz|tar|rar|7z|exe|dmg|pkg|mp4|mp3|avi|mov|wmv|webm|wav|"
    r"jpg|jpeg|png|gif|svg|webp|ico|bmp|tiff|css|js|json|xml|rss|atom|"
    r"doc|docx|xls|xlsx|ppt|pptx|csv|woff|woff2|ttf|eot)$", re.I)

APP_SHELL_IDS = ["root", "app", "__next", "__nuxt", "application", "main-app",
                 "svelte", "q-app", "ember-app"]
FRAMEWORK_MARKERS = [
    ("__NEXT_DATA__", "next.js"), ("__NUXT__", "nuxt"),
    ("data-reactroot", "react"), ("ng-version", "angular"),
    ("data-vue-", "vue"), ("__remixContext", "remix"),
    ("__sveltekit", "sveltekit"), ("wp-content", "wordpress"),
    ("Shopify.theme", "shopify"), ("__gatsby", "gatsby"),
]

DATE_RE = re.compile(
    r"\b(20\d{2}-\d{2}-\d{2}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+20\d{2}"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+20\d{2})\b", re.I)
COPYRIGHT_RE = re.compile(r"(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–]\s*)?(\d{4})", re.I)

PRONOUN_START_RE = re.compile(r"^\s*(it|they|this|these|those|we|he|she|its|their|our)\b", re.I)
DEICTIC_RE = re.compile(
    r"\b(above|below|the following|as mentioned|as described|previously|"
    r"see also|here|this page|the former|the latter)\b", re.I)
BARE_NUMBER_RE = re.compile(r"(?<![\w.])(?:[$£€₹]\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*(?:\.\d+)?%?)")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# --------------------------------------------------------------------------
# robots.txt
# --------------------------------------------------------------------------

class RobotsGroup:
    __slots__ = ("user_agents", "allow", "disallow", "crawl_delay")

    def __init__(self):
        self.user_agents: list[str] = []
        self.allow: list[str] = []
        self.disallow: list[str] = []
        self.crawl_delay = None


def parse_robots(text: str):
    """Parse robots.txt into ordered groups. Blank lines and comments end a
    group's agent list per the de-facto standard; consecutive User-agent lines
    share one group."""
    groups: list[RobotsGroup] = []
    sitemaps: list[str] = []
    errors: list[str] = []
    current = None
    expecting_agents = False

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            errors.append(f"line {lineno}: no ':' separator: {raw.strip()[:80]!r}")
            continue
        field, _, value = line.partition(":")
        field = field.strip().lower()
        value = value.strip()

        if field == "user-agent":
            if current is None or not expecting_agents:
                current = RobotsGroup()
                groups.append(current)
                expecting_agents = True
            current.user_agents.append(value)
        elif field in ("allow", "disallow"):
            if current is None:
                errors.append(f"line {lineno}: {field} before any user-agent")
                continue
            expecting_agents = False
            getattr(current, field).append(value)
        elif field == "crawl-delay":
            if current is not None:
                expecting_agents = False
                try:
                    current.crawl_delay = float(value)
                except ValueError:
                    errors.append(f"line {lineno}: non-numeric crawl-delay {value!r}")
        elif field == "sitemap":
            sitemaps.append(value)
        # Unknown fields are ignored by design, not an error.

    return groups, sitemaps, errors


def _pattern_to_regex(pattern: str) -> re.Pattern:
    out = []
    for ch in pattern:
        if ch == "*":
            out.append(".*")
        elif ch == "$":
            out.append("$")
        else:
            out.append(re.escape(ch))
    return re.compile("^" + "".join(out))


def match_group(groups: list[RobotsGroup], token: str):
    """Most specific matching group wins; only one group applies. Returns
    (index, group) or (None, None)."""
    token_l = token.lower()
    best = None
    best_len = -1
    for i, g in enumerate(groups):
        for ua in g.user_agents:
            ua_l = ua.strip().lower()
            if ua_l == "*":
                if best_len < 0:
                    best, best_len = (i, g), 0
            elif ua_l and (token_l == ua_l or token_l.startswith(ua_l)):
                if len(ua_l) > best_len:
                    best, best_len = (i, g), len(ua_l)
    return best if best else (None, None)


def robots_allows(group: RobotsGroup | None, path: str) -> bool:
    """Longest matching pattern wins; Allow wins ties. No group means allowed."""
    if group is None:
        return True
    best_len, best_allow = -1, True
    for pattern in group.disallow:
        if pattern == "":
            continue  # 'Disallow:' with empty value means allow all
        if _pattern_to_regex(pattern).match(path) and len(pattern) > best_len:
            best_len, best_allow = len(pattern), False
    for pattern in group.allow:
        if not pattern:
            continue
        if _pattern_to_regex(pattern).match(path) and len(pattern) >= best_len:
            best_len, best_allow = len(pattern), True
    return best_allow


# --------------------------------------------------------------------------
# fetching
# --------------------------------------------------------------------------

class Fetched:
    __slots__ = ("url", "final_url", "status", "headers", "body", "redirects",
                 "ttfb_ms", "total_ms", "error", "truncated")

    def __init__(self, **kw):
        for s in self.__slots__:
            setattr(self, s, kw.get(s))


class _Redirects(request.HTTPRedirectHandler):
    def __init__(self):
        self.chain: list[dict] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({"from": req.full_url, "to": newurl, "status": code})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url: str, ua: str = AUDIT_UA, timeout: float = 10.0,
          max_bytes: int = 3_000_000, method: str = "GET") -> Fetched:
    handler = _Redirects()
    opener = request.build_opener(handler)
    req = request.Request(url, method=method, headers={
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    })
    started = time.perf_counter()
    try:
        with opener.open(req, timeout=timeout) as resp:
            ttfb = (time.perf_counter() - started) * 1000.0
            raw = resp.read(max_bytes + 1)
            truncated = len(raw) > max_bytes
            raw = raw[:max_bytes]
            body = _decode_body(raw, resp.headers)
            return Fetched(url=url, final_url=resp.geturl(), status=resp.status,
                           headers=dict(resp.headers.items()), body=body,
                           redirects=handler.chain,
                           ttfb_ms=round(ttfb, 1),
                           total_ms=round((time.perf_counter() - started) * 1000.0, 1),
                           error=None, truncated=truncated)
    except error.HTTPError as exc:
        # An HTTP error is data, not a failure: 403 to a bot UA is the finding.
        try:
            raw = exc.read(max_bytes)
            body = _decode_body(raw, exc.headers)
        except Exception:
            body = ""
        return Fetched(url=url, final_url=url, status=exc.code,
                       headers=dict(exc.headers.items()) if exc.headers else {},
                       body=body, redirects=handler.chain, ttfb_ms=None,
                       total_ms=round((time.perf_counter() - started) * 1000.0, 1),
                       error=None, truncated=False)
    except Exception as exc:
        return Fetched(url=url, final_url=url, status=None, headers={}, body="",
                       redirects=handler.chain, ttfb_ms=None,
                       total_ms=round((time.perf_counter() - started) * 1000.0, 1),
                       error=f"{type(exc).__name__}: {exc}", truncated=False)


def _decode_body(raw: bytes, headers) -> str:
    enc = (headers.get("Content-Encoding") or "").lower()
    try:
        if "gzip" in enc:
            raw = gzip.decompress(raw)
        elif "deflate" in enc:
            raw = zlib.decompress(raw, -zlib.MAX_WBITS)
    except Exception:
        pass  # truncated compressed body; fall through with what we have
    charset = None
    ctype = headers.get("Content-Type") or ""
    if "charset=" in ctype:
        charset = ctype.split("charset=", 1)[1].split(";")[0].strip().strip('"')
    if not charset:
        head = raw[:2048].decode("ascii", "ignore")
        m = re.search(r'charset=["\']?([\w-]+)', head, re.I)
        if m:
            charset = m.group(1)
    for cand in filter(None, [charset, "utf-8", "cp1252", "latin-1"]):
        try:
            return raw.decode(cand)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", "replace")


# --------------------------------------------------------------------------
# HTML parsing -> normalized page model
# --------------------------------------------------------------------------

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
NON_TEXT = {"script", "style", "template", "svg", "canvas", "noscript"}
BOILERPLATE = {"nav", "header", "footer", "aside"}


class PageParser(HTMLParser):
    """Single pass over the document producing everything the analysis skills
    need, so no skill ever re-parses HTML differently from another."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self.meta: dict[str, str] = {}
        self.canonical = None
        self.hreflang: list[dict] = []
        self.headings: list[dict] = []
        self.links: list[dict] = []
        self.images: list[dict] = []
        self.scripts: list[dict] = []
        self.stylesheets: list[str] = []
        self.iframes: list[str] = []
        self.jsonld_raw: list[str] = []
        self.noscript: list[str] = []
        self.forms: list[dict] = []
        self.lang = None
        self.charset = None
        self.app_shell: list[str] = []
        self.element_count = 0
        self.time_datetimes: list[str] = []

        self._stack: list[str] = []
        self._text_parts: list[str] = []       # all text
        self._main_parts: list[str] = []       # text outside boilerplate
        self._capture: list[str] | None = None  # active capture buffer
        self._capture_tag = None
        self._boilerplate_depth = 0
        self._current_heading = None
        self._current_link = None
        self._current_form = None
        self._mounts: dict[str, int] = {}      # candidate app-shell -> text len at open
        self._mount_stack: list[tuple[str, int]] = []

    # -- helpers -----------------------------------------------------------
    def _attr(self, attrs, name):
        for k, v in attrs:
            if k.lower() == name:
                return v
        return None

    def _in_boilerplate(self) -> bool:
        return self._boilerplate_depth > 0

    def _emit_text(self, text: str) -> None:
        if not text.strip():
            return
        self._text_parts.append(text)
        if not self._in_boilerplate():
            self._main_parts.append(text)

    # -- handlers ----------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self.element_count += 1
        if tag not in VOID:
            self._stack.append(tag)

        if tag in BOILERPLATE:
            self._boilerplate_depth += 1

        if tag == "html":
            self.lang = self._attr(attrs, "lang")
        elif tag == "meta":
            charset = self._attr(attrs, "charset")
            if charset:
                self.charset = charset
            key = self._attr(attrs, "name") or self._attr(attrs, "property") \
                or self._attr(attrs, "http-equiv")
            content = self._attr(attrs, "content")
            if key and content is not None:
                self.meta[key.lower()] = content
        elif tag == "title":
            self._capture, self._capture_tag = [], "title"
        elif tag == "link":
            rel = (self._attr(attrs, "rel") or "").lower()
            href = self._attr(attrs, "href")
            if not href:
                pass
            elif "canonical" in rel:
                self.canonical = href
            elif "alternate" in rel and self._attr(attrs, "hreflang"):
                self.hreflang.append({"lang": self._attr(attrs, "hreflang"), "href": href})
            elif "stylesheet" in rel:
                self.stylesheets.append(href)
        elif tag == "script":
            stype = (self._attr(attrs, "type") or "").lower()
            src = self._attr(attrs, "src")
            if stype == "application/ld+json":
                self._capture, self._capture_tag = [], "ld+json"
            else:
                self.scripts.append({
                    "src": src,
                    "inline_bytes": None if src else 0,
                    "async": self._attr(attrs, "async") is not None,
                    "defer": self._attr(attrs, "defer") is not None,
                    "third_party": False,   # resolved later against the origin
                    "blocking": bool(src) and self._attr(attrs, "async") is None
                                and self._attr(attrs, "defer") is None,
                })
                if not src:
                    self._capture, self._capture_tag = [], "script"
        elif tag == "noscript":
            self._capture, self._capture_tag = [], "noscript"
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._current_heading = {"level": int(tag[1]), "text": ""}
            self._capture, self._capture_tag = [], "heading"
        elif tag == "a":
            href = self._attr(attrs, "href")
            if href:
                self._current_link = {
                    "href": href, "text": "",
                    "rel": self._attr(attrs, "rel") or "",
                    "in_nav": self._in_boilerplate(),
                }
                self._capture, self._capture_tag = [], "link"
        elif tag == "img":
            src = self._attr(attrs, "src") or self._attr(attrs, "data-src") or ""
            self.images.append({
                "src": src,
                # None means the attribute is absent; "" means explicitly decorative.
                "alt": self._attr(attrs, "alt"),
                "width": _to_int(self._attr(attrs, "width")),
                "height": _to_int(self._attr(attrs, "height")),
                "loading": self._attr(attrs, "loading"),
                "bytes": None,
            })
        elif tag == "iframe":
            src = self._attr(attrs, "src")
            if src:
                self.iframes.append(src)
        elif tag == "time":
            dt = self._attr(attrs, "datetime")
            if dt:
                self.time_datetimes.append(dt)
        elif tag == "form":
            self._current_form = {
                "action": self._attr(attrs, "action"),
                "method": (self._attr(attrs, "method") or "get").lower(),
                "field_count": 0, "required_count": 0,
            }
        elif tag in ("input", "select", "textarea") and self._current_form is not None:
            itype = (self._attr(attrs, "type") or "").lower()
            if itype not in ("hidden", "submit", "button", "image", "reset"):
                self._current_form["field_count"] += 1
                if self._attr(attrs, "required") is not None:
                    self._current_form["required_count"] += 1

        # Track candidate app-shell mount points: an element whose id looks like
        # a framework root and which turns out to contain (almost) no text.
        el_id = (self._attr(attrs, "id") or "").lower()
        if el_id and el_id in APP_SHELL_IDS:
            self._mount_stack.append((el_id, len("".join(self._text_parts))))
        if self._attr(attrs, "data-reactroot") is not None:
            self._mount_stack.append(("data-reactroot", len("".join(self._text_parts))))

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in BOILERPLATE and self._boilerplate_depth > 0:
            self._boilerplate_depth -= 1

        if self._capture is not None:
            text = "".join(self._capture).strip()
            ct = self._capture_tag
            if ct == "title" and tag == "title":
                self.title = text
                self._capture = None
            elif ct == "ld+json" and tag == "script":
                self.jsonld_raw.append(text)
                self._capture = None
            elif ct == "script" and tag == "script":
                if self.scripts and self.scripts[-1]["src"] is None:
                    self.scripts[-1]["inline_bytes"] = len(text)
                self._capture = None
            elif ct == "noscript" and tag == "noscript":
                if text:
                    self.noscript.append(text)
                self._capture = None
            elif ct == "heading" and tag.startswith("h") and len(tag) == 2:
                if self._current_heading is not None:
                    self._current_heading["text"] = _collapse(text)
                    if self._current_heading["text"]:
                        self.headings.append(self._current_heading)
                    self._emit_text(text)
                self._current_heading = None
                self._capture = None
            elif ct == "link" and tag == "a":
                if self._current_link is not None:
                    self._current_link["text"] = _collapse(text)
                    self.links.append(self._current_link)
                    self._emit_text(text)
                self._current_link = None
                self._capture = None

        if tag == "form" and self._current_form is not None:
            self.forms.append(self._current_form)
            self._current_form = None

        if self._mount_stack:
            name, text_len_at_open = self._mount_stack[-1]
            # Close the mount when its element closes; heuristically, any close
            # tag after we opened it and text grew negligibly.
            if tag in ("div", "main", "section", "app-root", "body"):
                grown = len("".join(self._text_parts)) - text_len_at_open
                if grown < 200:
                    self.app_shell.append(name)
                self._mount_stack.pop()

        if self._stack and tag in self._stack:
            while self._stack:
                if self._stack.pop() == tag:
                    break

    def handle_data(self, data):
        if self._capture is not None:
            self._capture.append(data)
            return
        if self._stack and self._stack[-1] in NON_TEXT:
            return
        self._emit_text(data)

    # -- results -----------------------------------------------------------
    @property
    def full_text(self) -> str:
        return _collapse(" ".join(self._text_parts))

    @property
    def main_text(self) -> str:
        return _collapse(" ".join(self._main_parts))


def _collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _to_int(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def extract_page(page_id: str, url: str, html: str, origin: str) -> dict:
    """Build the normalized page model. Observation only -- no judgment."""
    parser = PageParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:
        # Malformed markup is common; keep whatever parsed.
        parser.meta.setdefault("_parse_error", f"{type(exc).__name__}: {exc}")

    origin_host = urlparse(origin).netloc.lower()

    links = []
    for link in parser.links:
        href = link["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute = urljoin(url, href)
        host = urlparse(absolute).netloc.lower()
        links.append({**link, "href": absolute,
                      "internal": host == origin_host or host == ""})

    for s in parser.scripts:
        if s["src"]:
            s["src"] = urljoin(url, s["src"])
            s["third_party"] = urlparse(s["src"]).netloc.lower() != origin_host

    images = [{**img, "src": urljoin(url, img["src"]) if img["src"] else ""}
              for img in parser.images]

    jsonld = []
    for raw in parser.jsonld_raw:
        entry = {"raw": raw, "parsed_ok": False, "parse_error": None, "value": None}
        try:
            entry["value"] = json.loads(raw)
            entry["parsed_ok"] = True
        except json.JSONDecodeError as exc:
            entry["parse_error"] = str(exc)
        jsonld.append(entry)

    full_text = parser.full_text
    main_text = parser.main_text
    markup_len = max(len(html), 1)

    dates = []
    for dt in parser.time_datetimes:
        dates.append({"value": dt, "iso": _norm_date(dt), "source": "time-element",
                      "field": None})
    for key in ("article:published_time", "article:modified_time", "date",
                "last-modified", "og:updated_time", "datepublished", "datemodified"):
        if key in parser.meta:
            dates.append({"value": parser.meta[key], "iso": _norm_date(parser.meta[key]),
                          "source": "meta", "field": key})
    for entry in jsonld:
        if entry["parsed_ok"]:
            for field, val in _walk_dates(entry["value"]):
                dates.append({"value": str(val), "iso": _norm_date(str(val)),
                              "source": "jsonld", "field": field})
    for m in DATE_RE.finditer(full_text[:20000]):
        dates.append({"value": m.group(0), "iso": _norm_date(m.group(0)),
                      "source": "visible-text", "field": None})
    for m in COPYRIGHT_RE.finditer(full_text):
        dates.append({"value": m.group(0), "iso": f"{m.group(1)}-01-01",
                      "source": "copyright", "field": None})

    hydration = None
    for marker in ("__NEXT_DATA__", "__NUXT__", "__remixContext", "__sveltekit"):
        idx = html.find(marker)
        if idx >= 0:
            end = html.find("</script>", idx)
            hydration = (end - idx) if end > idx else None
            break

    frameworks = sorted({name for marker, name in FRAMEWORK_MARKERS if marker in html})

    return {
        "page_id": page_id,
        "url": url,
        "lang": parser.lang,
        "charset": parser.charset,
        "title": parser.title,
        "meta": parser.meta,
        "canonical": urljoin(url, parser.canonical) if parser.canonical else None,
        "hreflang": parser.hreflang,
        "headings": parser.headings,
        "links": links,
        "images": images,
        "scripts": parser.scripts,
        "stylesheets": [urljoin(url, s) for s in parser.stylesheets],
        "iframes": [urljoin(url, s) for s in parser.iframes],
        "jsonld": jsonld,
        "microdata": [],   # itemscope extraction: see TODO in structured-data-audit
        "rdfa": [],
        "text": {
            "main": main_text[:200000],
            "full": full_text[:200000],
            "word_count": len(full_text.split()),
            "main_word_count": len(main_text.split()),
            "text_to_markup_ratio": round(len(full_text) / markup_len, 4),
        },
        "noscript": parser.noscript,
        "render_signals": {
            "app_shell_selectors": sorted(set(parser.app_shell)),
            "framework_markers": frameworks,
            "hydration_payload_bytes": hydration,
            "body_element_count": parser.element_count,
        },
        "forms": parser.forms,
        "dates": dates,
        "timing": {},
    }


def _walk_dates(node, prefix=""):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and "date" in k.lower():
                yield (k, v)
            else:
                yield from _walk_dates(v, k)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_dates(item, prefix)


def _norm_date(value: str):
    value = (value or "").strip()
    m = re.search(r"(20\d{2})-(\d{2})-(\d{2})", value)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


# --------------------------------------------------------------------------
# chunking
# --------------------------------------------------------------------------

def chunk_page(extracted: dict, target_words: int = 320, max_words: int = 512) -> dict:
    """Split the page the way a retrieval pipeline would: on heading boundaries,
    with a target window. Attach the deterministic signals answerability-audit
    reasons over. The script counts; the model judges."""
    text = extracted["text"]["main"] or extracted["text"]["full"]
    headings = [h["text"] for h in extracted.get("headings", []) if h.get("text")]

    segments: list[tuple[list[str], str]] = []
    if headings:
        pattern = "|".join(re.escape(h) for h in headings[:80])
        parts = re.split(f"({pattern})", text)
        path: list[str] = []
        buffer = parts[0] if parts else text
        if buffer.strip():
            segments.append(([], buffer))
        i = 1
        while i < len(parts) - 1:
            heading, body = parts[i], parts[i + 1]
            path = [heading]
            segments.append((list(path), body))
            i += 2
    else:
        segments.append(([], text))

    chunks = []
    for path, body in segments:
        words = body.split()
        if not words:
            continue
        step = max_words if len(words) <= max_words else target_words
        for start in range(0, len(words), step):
            piece = " ".join(words[start:start + step])
            if len(piece.split()) < 15:
                continue
            chunks.append({
                "chunk_id": f"c{len(chunks):03d}",
                "heading_path": path,
                "text": piece,
                "word_count": len(piece.split()),
                "signals": _chunk_signals(piece, extracted),
            })

    return {
        "page_id": extracted["page_id"],
        "strategy": f"heading-boundary, target {target_words} words, max {max_words}, no overlap",
        "chunks": chunks,
    }


def _chunk_signals(text: str, extracted: dict) -> dict:
    subject_terms = set()
    title = extracted.get("title") or ""
    for token in re.findall(r"\b[A-Z][A-Za-z0-9&.-]{2,}\b", title):
        if token.lower() not in ("the", "and", "for", "with", "home"):
            subject_terms.add(token.lower())
    for h in extracted.get("headings", [])[:3]:
        for token in re.findall(r"\b[A-Z][A-Za-z0-9&.-]{2,}\b", h.get("text", "")):
            subject_terms.add(token.lower())

    lower = text.lower()
    names_subject = any(t in lower for t in subject_terms) if subject_terms else False

    bare = 0
    for m in BARE_NUMBER_RE.finditer(text):
        window = text[max(0, m.start() - 40):m.start()]
        # A number is "bare" when nothing nearby says what it counts.
        if not re.search(r"\b(price|cost|from|starting|plan|per|only|just|save|"
                         r"discount|fee|rate|year|month|day|hour|user|seat)\b",
                         window, re.I):
            bare += 1

    return {
        "names_subject": names_subject,
        "leading_pronoun": bool(PRONOUN_START_RE.match(text)),
        "bare_numbers": bare,
        "has_date": bool(DATE_RE.search(text)),
        "deictic_terms": sorted({m.group(0).lower() for m in DEICTIC_RE.finditer(text)}),
    }


# --------------------------------------------------------------------------
# sitemaps
# --------------------------------------------------------------------------

def parse_sitemap(text: str):
    """Return (kind, entries, errors). lastmod is preserved verbatim -- TRUST-003
    tests whether the claim is honest, which is impossible once normalized."""
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(text.strip())
    except ET.ParseError as exc:
        return "invalid", [], [f"XML parse error: {exc}"]

    tag = root.tag.split("}")[-1]
    entries = []
    if tag == "sitemapindex":
        for sm in root:
            loc = sm.find("{*}loc")
            if loc is None:
                loc = sm.find("loc")
            if loc is not None and loc.text:
                entries.append({"loc": loc.text.strip(), "lastmod": None,
                                "changefreq": None, "priority": None})
        return "index", entries, []
    if tag == "urlset":
        for url_el in root:
            def get(name):
                el = url_el.find("{*}" + name)
                if el is None:
                    el = url_el.find(name)
                return el.text.strip() if el is not None and el.text else None
            loc = get("loc")
            if loc:
                pr = get("priority")
                entries.append({
                    "loc": loc,
                    "lastmod": get("lastmod"),
                    "changefreq": get("changefreq"),
                    "priority": float(pr) if pr and _is_float(pr) else None,
                })
        return "urlset", entries, []
    return "invalid", [], [f"unexpected root element {tag!r}"]


def _is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# --------------------------------------------------------------------------
# URL helpers
# --------------------------------------------------------------------------

def normalize_url(url: str) -> str:
    url, _ = urldefrag(url)
    parsed = urlparse(url)
    path = parsed.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path,
                       "", parsed.query, ""))


def crawlable(url: str, origin: str, include, exclude) -> tuple[bool, str]:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False, "out-of-scope"
    if parsed.netloc.lower() != urlparse(origin).netloc.lower():
        return False, "out-of-scope"
    if NON_HTML_EXT.search(parsed.path):
        return False, "non-html"
    if SKIP_PATH_PATTERNS.search(parsed.path) or SKIP_QUERY_PATTERNS.search(parsed.query or ""):
        return False, "out-of-scope"
    if include and not any(parsed.path.startswith(p) for p in include):
        return False, "out-of-scope"
    if exclude and any(parsed.path.startswith(p) for p in exclude):
        return False, "out-of-scope"
    return True, ""


def classify_page_type(url: str, extracted: dict | None) -> str:
    path = urlparse(url).path.lower().rstrip("/")
    if path in ("", "/"):
        return "home"
    rules = [
        (r"/(product|item|p|sku)s?/", "product"),
        (r"/(category|collection|shop|catalog)s?/", "category"),
        (r"/(blog|news|article|post|story|insight)s?/", "article"),
        (r"/(doc|documentation|guide|reference|api|manual)s?/", "docs"),
        (r"/(pricing|plans|price)", "pricing"),
        (r"/(about|company|team|who-we-are|our-story)", "about"),
        (r"/(contact|support|help-?desk|get-in-touch)", "contact"),
        (r"/(faq|faqs|questions|q-and-a)", "faq"),
        (r"/(privacy|terms|legal|cookie|gdpr|imprint|disclaimer)", "legal"),
    ]
    for pattern, label in rules:
        if re.search(pattern, path):
            return label
    if extracted:
        types = set()
        for block in extracted.get("jsonld", []):
            if block.get("parsed_ok"):
                types |= {t.lower() for t in _collect_types(block["value"])}
        if "product" in types:
            return "product"
        if types & {"article", "newsarticle", "blogposting"}:
            return "article"
        if "faqpage" in types:
            return "faq"
    return "other"


def _collect_types(node):
    out = []
    if isinstance(node, dict):
        t = node.get("@type")
        if isinstance(t, str):
            out.append(t)
        elif isinstance(t, list):
            out.extend(x for x in t if isinstance(x, str))
        for v in node.values():
            out.extend(_collect_types(v))
    elif isinstance(node, list):
        for item in node:
            out.extend(_collect_types(item))
    return out


# --------------------------------------------------------------------------
# collection
# --------------------------------------------------------------------------

class Collector:
    def __init__(self, args):
        self.args = args
        self.out = args.out
        self.started = time.time()
        self.skipped: list[dict] = []
        self.pages: list[dict] = []
        self.robots_groups: list[RobotsGroup] = []
        self.our_group = None
        self.delay = max(args.delay, 0.0)

    # -- budget ------------------------------------------------------------
    def time_left(self) -> float:
        return self.args.budget - (time.time() - self.started)

    def skip(self, url: str, reason: str) -> None:
        self.skipped.append({"url": url, "reason": reason})

    # -- origin ------------------------------------------------------------
    def resolve_origin(self, target: str):
        if "://" not in target:
            target = "https://" + target
        host = urlparse(target).netloc or urlparse(target).path
        host = host.split("/")[0]
        bare = host[4:] if host.startswith("www.") else host
        scheme = urlparse(target).scheme or "https"
        # Try the form the caller actually supplied first. Some sites serve the
        # apex and the www host differently -- one 403s or 404s while the other
        # is fine -- so silently adopting the apex can make a healthy site look
        # unreachable.
        supplied = f"{scheme}://{host}"
        variants = {supplied: None}
        for candidate in ("https://" + bare, "https://www." + bare,
                          "http://" + bare, "http://www." + bare):
            variants.setdefault(candidate, None)
        results = {}
        chosen = None
        for candidate in list(variants):
            if self.time_left() <= 0:
                break
            r = fetch(candidate + "/", timeout=min(self.args.timeout, 8))
            results[candidate] = {
                "status": r.status,
                "redirects_to": r.final_url if r.final_url and
                normalize_url(r.final_url) != normalize_url(candidate + "/") else None,
            }
            if chosen is None and r.status and 200 <= r.status < 400:
                final = urlparse(r.final_url or candidate)
                chosen = f"{final.scheme}://{final.netloc}"
        return (chosen or "https://" + bare), results

    # -- robots ------------------------------------------------------------
    def load_robots(self, origin: str) -> dict:
        r = fetch(origin + "/robots.txt", timeout=self.args.timeout)
        _write(os.path.join(self.out, "robots.txt.raw"), r.body or "")
        _write_json(os.path.join(self.out, "robots_fetch.json"), {
            "url": r.url, "status": r.status, "final_url": r.final_url,
            "headers": r.headers, "error": r.error,
        })

        info = {"fetched": r.status is not None, "status": r.status,
                "parse_errors": [], "groups": [], "sitemap_urls": [],
                "agent_matrix": {}, "llms_txt": {}}

        if r.status == 200 and r.body:
            groups, sitemaps, errors = parse_robots(r.body)
            self.robots_groups = groups
            info["parse_errors"] = errors
            info["sitemap_urls"] = [urljoin(origin, s) for s in sitemaps]
            info["groups"] = [{"user_agents": g.user_agents, "allow": g.allow,
                               "disallow": g.disallow, "crawl_delay": g.crawl_delay}
                              for g in groups]
            for token, purpose in AI_AGENTS.items():
                idx, group = match_group(groups, token)
                blocked = []
                if group:
                    blocked = [d for d in group.disallow if d]
                info["agent_matrix"][token] = {
                    "root_allowed": robots_allows(group, "/"),
                    "purpose": purpose,
                    "matched_group": idx,
                    "blocked_paths": blocked,
                }
            _, self.our_group = match_group(groups, "BrandAIReadinessAudit")
            if self.our_group and self.our_group.crawl_delay:
                self.delay = max(self.delay, self.our_group.crawl_delay)
        elif r.status is not None and 500 <= r.status < 600:
            # A 5xx robots.txt means "unknown", not "allowed". Back off.
            info["parse_errors"].append(
                f"robots.txt returned {r.status}; treating as unknown and crawling "
                f"conservatively")

        llms = fetch(origin + "/llms.txt", timeout=min(self.args.timeout, 6))
        info["llms_txt"] = {"present": llms.status == 200,
                            "status": llms.status,
                            "bytes": len(llms.body or "") if llms.status == 200 else None}
        return info

    def allowed(self, url: str) -> bool:
        return robots_allows(self.our_group, urlparse(url).path or "/")

    # -- sitemaps ----------------------------------------------------------
    def load_sitemaps(self, origin: str, declared: list[str]) -> list[dict]:
        os.makedirs(os.path.join(self.out, "sitemaps"), exist_ok=True)
        queue = list(dict.fromkeys(declared + [origin + "/sitemap.xml"]))
        seen, out, depth = set(), [], 0
        while queue and depth < 2 and len(out) < 6 and self.time_left() > 5:
            nxt = []
            for url in queue:
                if url in seen or len(out) >= 6:
                    continue
                seen.add(url)
                r = fetch(url, timeout=self.args.timeout)
                record = {"url": url, "status": r.status, "kind": "unreachable",
                          "parse_errors": [], "entry_count": 0, "entries": []}
                if r.status == 200 and r.body:
                    kind, entries, errors = parse_sitemap(r.body)
                    record.update(kind=kind, parse_errors=errors,
                                  entry_count=len(entries), entries=entries[:500])
                    _write(os.path.join(self.out, "sitemaps",
                                        f"sitemap-{len(out):02d}.xml"), r.body[:2_000_000])
                    if kind == "index":
                        nxt.extend(e["loc"] for e in entries[:5])
                out.append(record)
            queue, depth = nxt, depth + 1
        return out

    # -- probe -------------------------------------------------------------
    def ua_probe(self, url: str) -> dict:
        baseline = fetch(url, ua=BROWSER_UA, timeout=self.args.timeout)
        result = {"url": url, "baseline": _probe_result(baseline, BROWSER_UA), "agents": {}}
        for token in PROBE_AGENTS:
            if self.time_left() <= 5:
                break
            time.sleep(self.delay)
            r = fetch(url, ua=f"Mozilla/5.0 (compatible; {token}/1.0)",
                      timeout=self.args.timeout)
            result["agents"][token] = _probe_result(r, token)
        return result

    # -- pages -------------------------------------------------------------
    def select_and_fetch(self, origin: str, sitemaps: list[dict]) -> None:
        home = origin + "/"
        queue: list[tuple[str, str]] = [(normalize_url(home), "home")]
        queued = {normalize_url(home)}

        for sm in sitemaps:
            for entry in sm.get("entries", []):
                loc = entry.get("loc")
                if not loc:
                    continue
                url = normalize_url(loc)
                ok, reason = crawlable(url, origin, self.args.include, self.args.exclude)
                if not ok:
                    continue
                if url not in queued:
                    queued.add(url)
                    queue.append((url, "sitemap-priority"))

        fetched = 0
        discovered = len(queued)
        index = 0
        while index < len(queue) and fetched < self.args.max_pages:
            if self.time_left() <= 3:
                self.stopped = "time-budget"
                return
            batch = []
            while index < len(queue) and len(batch) < self.args.concurrency \
                    and fetched + len(batch) < self.args.max_pages:
                url, role = queue[index]
                index += 1
                if not self.allowed(url):
                    self.skip(url, "robots-disallow")
                    continue
                batch.append((url, role))
            if not batch:
                continue

            with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as pool:
                futures = {pool.submit(fetch, url, AUDIT_UA, self.args.timeout,
                                       self.args.max_bytes): (url, role)
                           for url, role in batch}
                for fut in concurrent.futures.as_completed(futures):
                    url, role = futures[fut]
                    try:
                        r = fut.result()
                    except Exception as exc:
                        self.skip(url, "http-error")
                        continue
                    saved = self.save_page(r, url, role, origin)
                    if saved is None:
                        continue
                    fetched += 1
                    if role != "sitemap-priority" or len(queue) < self.args.max_pages * 3:
                        for link in saved.get("_links", []):
                            nu = normalize_url(link)
                            if nu in queued:
                                continue
                            ok, reason = crawlable(nu, origin, self.args.include,
                                                   self.args.exclude)
                            if not ok:
                                continue
                            queued.add(nu)
                            queue.append((nu, "crawl-discovered"))
                            discovered += 1
            # Reorder the frontier to spread the sample across the site rather
            # than exhausting one directory. Deterministic: no randomness, and
            # the same site always yields the same sample.
            queue[index:] = self._diversify(queue[index:])
            time.sleep(self.delay)

        self.discovered = discovered
        self.stopped = "max-pages" if fetched >= self.args.max_pages else "completed"

    @staticmethod
    def _segment(url: str) -> str:
        parts = [p for p in urlparse(url).path.split("/") if p]
        return parts[0] if parts else ""

    def _diversify(self, frontier: list) -> list:
        """Order the frontier so each site section is sampled before any section
        is sampled deeply.

        Lexicographic breadth-first is deterministic but pathological: on a site
        whose first directory is large, the entire page budget is spent inside
        it and the audit generalizes from an unrepresentative slice. Here each
        candidate is ranked by how many pages that section has already
        contributed, so sections are visited round-robin. Ties break on role
        then URL, so the result is still a pure function of the input.
        """
        taken = {}
        for page in self.pages:
            seg = self._segment(page.get("url", ""))
            taken[seg] = taken.get(seg, 0) + 1

        seen_in_frontier = {}
        ranked = []
        for url, role in frontier:
            seg = self._segment(url)
            position = seen_in_frontier.get(seg, 0)
            seen_in_frontier[seg] = position + 1
            role_rank = 0 if role == "sitemap-priority" else 1
            ranked.append(((taken.get(seg, 0) + position), role_rank, url, (url, role)))
        ranked.sort(key=lambda t: (t[0], t[1], t[2]))
        return [item for _, _, _, item in ranked]

    def save_page(self, r: Fetched, url: str, role: str, origin: str):
        if r.error:
            self.skip(url, "timeout" if "timeout" in r.error.lower() else "http-error")
            return None
        ctype = (r.headers.get("Content-Type") or "").lower()
        if r.status and r.status >= 400:
            self.skip(url, "http-error")
            # Still record the status for REACH-012 (broken internal links).
            self.pages.append({"page_id": f"p{len(self.pages):03d}", "url": url,
                               "final_url": r.final_url, "status": r.status,
                               "role": role, "page_type": "other",
                               "content_type": ctype, "bytes": len(r.body or "")})
            return None
        if ctype and "html" not in ctype and "xml" not in ctype:
            self.skip(url, "non-html")
            return None

        page_id = f"p{len(self.pages):03d}"
        pdir = os.path.join(self.out, "pages", page_id)
        os.makedirs(pdir, exist_ok=True)

        _write(os.path.join(pdir, "raw.html"), r.body or "")
        _write_json(os.path.join(pdir, "request.json"), {
            "url": url, "final_url": r.final_url, "status": r.status,
            "redirect_chain": r.redirects or [],
            "timing": {"ttfb_ms": r.ttfb_ms, "total_ms": r.total_ms,
                       "transfer_bytes": len(r.body or "")},
            "truncated": r.truncated,
        })
        _write_json(os.path.join(pdir, "response.headers.json"), r.headers)

        extracted = extract_page(page_id, r.final_url or url, r.body or "", origin)
        extracted["timing"] = {"ttfb_ms": r.ttfb_ms, "total_ms": r.total_ms,
                               "transfer_bytes": len(r.body or "")}

        if self.args.renderer:
            rendered = self.render(url)
            if rendered:
                _write(os.path.join(pdir, "rendered.html"), rendered)

        _write_json(os.path.join(pdir, "extracted.json"), extracted)
        _write_json(os.path.join(pdir, "chunks.json"), chunk_page(extracted))

        record = {"page_id": page_id, "url": url, "final_url": r.final_url,
                  "status": r.status, "role": role,
                  "page_type": classify_page_type(r.final_url or url, extracted),
                  "content_type": ctype, "bytes": len(r.body or "")}
        self.pages.append(record)
        return {**record, "_links": [l["href"] for l in extracted["links"] if l["internal"]]}

    def render(self, url: str):
        try:
            proc = subprocess.run(self.args.renderer.split() + [url],
                                  capture_output=True, text=True,
                                  timeout=self.args.timeout * 3)
            return proc.stdout if proc.returncode == 0 else None
        except Exception:
            return None

    # -- driver ------------------------------------------------------------
    def run(self) -> int:
        os.makedirs(self.out, exist_ok=True)
        self.stopped = "completed"
        self.discovered = 0

        origin, variants = self.resolve_origin(self.args.target)
        reachable = any(v.get("status") for v in variants.values())

        run_doc = {
            "target": self.args.target, "origin": origin,
            "origin_variants": variants,
            "started_at": now_iso(), "finished_at": None,
            "collector_version": COLLECTOR_VERSION,
            "renderer": {"available": bool(self.args.renderer),
                         "name": self.args.renderer or None},
            "budget": {
                "max_pages": self.args.max_pages,
                "max_concurrency": self.args.concurrency,
                "request_timeout_s": self.args.timeout,
                "total_fetch_budget_s": self.args.budget,
                "politeness_delay_s": self.args.delay,
                "max_bytes_per_page": self.args.max_bytes,
            },
        }

        if not reachable:
            self.stopped = "dns-failure"
            robots_info = {"fetched": False, "status": None, "parse_errors": [],
                           "groups": [], "sitemap_urls": [], "agent_matrix": {},
                           "llms_txt": {}}
            sitemaps, probe = [], {}
        else:
            robots_info = self.load_robots(origin)
            sitemaps = self.load_sitemaps(origin, robots_info.get("sitemap_urls", []))
            probe = {} if self.args.no_probe else self.ua_probe(origin + "/")
            if self.allowed(origin + "/"):
                self.select_and_fetch(origin, sitemaps)
            else:
                self.stopped = "site-blocked"
                self.skip(origin + "/", "robots-disallow")

        run_doc["finished_at"] = now_iso()
        _write_json(os.path.join(self.out, "run.json"), run_doc)
        _write_json(os.path.join(self.out, "ua_probe.json"), probe)

        coverage = {
            "pages_discovered": max(self.discovered, len(self.pages)),
            "pages_fetched": len([p for p in self.pages if p.get("status") == 200]),
            "complete": self.stopped in ("completed",),
            "stopped_reason": self.stopped,
            "skipped": self.skipped,
        }
        _write_json(os.path.join(self.out, "coverage.json"), coverage)

        manifest = {
            "schema_version": SCHEMA_VERSION,
            "run": run_doc,
            "robots": robots_info,
            "sitemaps": sitemaps,
            "ua_probe": probe,
            "pages": self.pages,
            "coverage": coverage,
        }
        _write_json(os.path.join(self.out, "MANIFEST.json"), manifest)

        print(f"bundle: {self.out}", file=sys.stderr)
        print(f"  origin        {origin}", file=sys.stderr)
        print(f"  pages fetched {coverage['pages_fetched']}", file=sys.stderr)
        print(f"  stopped       {self.stopped}", file=sys.stderr)
        print(f"  skipped       {len(self.skipped)}", file=sys.stderr)
        return 0


def _probe_result(r: Fetched, ua: str) -> dict:
    body = (r.body or "").lower()
    return {
        "user_agent": ua,
        "status": r.status,
        "bytes": len(r.body or ""),
        "text_bytes": len(_collapse(re.sub(r"<[^>]+>", " ", r.body or ""))),
        "challenge_detected": any(sig in body for sig in CHALLENGE_SIGNATURES),
        "error": r.error,
    }


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-pages", type=int, default=25)
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--budget", type=float, default=120.0)
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--max-bytes", type=int, default=3_000_000)
    ap.add_argument("--include", action="append", default=[])
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--renderer", default=None,
                    help="command receiving a URL and printing rendered HTML")
    ap.add_argument("--no-probe", action="store_true")
    args = ap.parse_args(argv)

    args.concurrency = max(1, min(args.concurrency, 8))  # hard cap, not a default
    if not args.out:
        host = urlparse(args.target if "://" in args.target
                        else "https://" + args.target).netloc or args.target
        args.out = os.path.join(".audit", host, time.strftime("run-%Y%m%d-%H%M%S"))

    return Collector(args).run()


if __name__ == "__main__":
    sys.exit(main())
