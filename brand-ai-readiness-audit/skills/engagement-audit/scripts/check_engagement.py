#!/usr/bin/env python3
"""STAY checks: does the visitor who arrives actually stay?

Standard library only -- ships inside the submission and must run on a bare
Python 3.9+ install.

Reads a completed evidence bundle and emits candidate findings against
../audit-orchestrator/references/finding.schema.json. Performs no network I/O:
every result is a pure function of the bundle, so the same bundle always yields
byte-identical findings.

This is the ENTIRE engagement half of the report. Every finding here carries
`category: "engagement"` and `mechanism: "stay"`, unlike the five discoverability
skills.

Structure mirrors ../crawl-access-audit/scripts/check_access.py (the reference
implementation): a Bundle accessor, one check_stay_<nnn> per check, the
finding() / act() helpers copied verbatim, a CHECKS list, and a driver that
wraps each check in try/except and drops candidates whose refs do not resolve.

Two standing constraints from the registry:

  * The performance checks (STAY-008, 009, 010, 014) are STATIC PROXIES derived
    from the HTML. They are never Core Web Vitals, never an LCP/CLS score, and
    never exceed 'medium' on proxy evidence alone (viewport absence is the one
    exception the rule allows at 'high').
  * We cannot see the fold. The fold is approximated from document order and the
    evidence says so.

Usage:
    python check_engagement.py <bundle> --out stay-candidates.json
    python check_engagement.py <bundle> --stdout
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.parse import urlparse

MECHANISM = "stay"
CATEGORY = "engagement"

# A page is a client-render shell (READ-001 territory, not a STAY gap) only when
# the render signals are unambiguous: an empty framework mount, a large
# hydration payload and a near-zero text-to-markup ratio. A page that is merely
# thin -- little content but all of it served -- is NOT a shell and is exactly
# what several STAY checks exist to catch.
SHELL_HYDRATION_BYTES = 6000
SHELL_TEXT_RATIO = 0.05

# STAY-004: page types that are legitimate endpoints and need no onward link.
ENDPOINT_PAGE_TYPES = {"contact", "legal", "thank-you", "thankyou"}

# STAY-003 / STAY-001: pages that exist to move a visitor forward.
CONVERSION_PAGE_TYPES = {"home", "pricing", "product", "category", "other"}

CTA_RE = re.compile(
    r"\b(buy|shop|order|add to (?:cart|bag|basket)|checkout|sign up|signup|"
    r"get started|start (?:free|now|your)|try (?:it|for) free|book (?:a|now|your)|"
    r"request (?:a|access|demo)|contact (?:us|sales)|subscribe|download|"
    r"register|join|donate|apply now|get a quote|schedule)\b", re.I)

INTERSTITIAL_RE = re.compile(
    r"(class=\"[^\"]*\b(?:modal|overlay|popup|lightbox|interstitial|"
    r"newsletter-signup|email-capture)\b[^\"]*\""
    r"|id=\"[^\"]*\b(?:cookie|consent|gdpr|modal|popup|paywall)\b[^\"]*\""
    r"|aria-modal=\"true\""
    r"|data-(?:modal|popup|overlay)=)", re.I)
CONSENT_RE = re.compile(r"\b(cookie|consent|gdpr|ccpa|privacy preferences)\b", re.I)

SEARCH_FORM_RE = re.compile(
    r"(<input[^>]+type=\"search\"|role=\"search\"|name=\"(?:q|query|s|search|"
    r"keyword|keywords)\"|<input[^>]+class=\"[^\"]*search)", re.I)

LABELLED_INPUT_ATTR_RE = re.compile(r"\b(aria-label|aria-labelledby)\s*=", re.I)


class Bundle:
    """Thin accessor over an evidence bundle directory."""

    def __init__(self, root: str):
        self.root = root
        self.manifest = self._json("MANIFEST.json") or {}
        self.run = self.manifest.get("run") or {}
        self.sitemaps = self.manifest.get("sitemaps") or []
        self.coverage = self.manifest.get("coverage") or {}
        self.pages = self.manifest.get("pages") or []
        self.origin = self.run.get("origin") or ""
        self.site = urlparse(self.origin).netloc or self.origin
        self._extracted: dict = {}
        self._raw: dict = {}
        self._requests: dict = {}
        self._site_type = None
        self.checks_skipped: list = []

    def _json(self, rel: str):
        path = os.path.join(self.root, rel.replace("/", os.sep))
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def exists(self, rel: str) -> bool:
        return os.path.exists(os.path.join(self.root, rel.replace("/", os.sep)))

    def skip_check(self, check_id: str, reason: str) -> None:
        entry = {"check_id": check_id, "reason": reason}
        if entry not in self.checks_skipped:
            self.checks_skipped.append(entry)

    @property
    def ok_pages(self) -> list:
        return [p for p in self.pages if p.get("status") == 200]

    def extracted(self, page_id: str) -> dict:
        if page_id not in self._extracted:
            self._extracted[page_id] = self._json(f"pages/{page_id}/extracted.json") or {}
        return self._extracted[page_id]

    def raw_html(self, page_id: str) -> str:
        if page_id not in self._raw:
            path = os.path.join(self.root, "pages", page_id, "raw.html")
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    self._raw[page_id] = fh.read()
            except FileNotFoundError:
                self._raw[page_id] = ""
        return self._raw[page_id]

    def request(self, page_id: str) -> dict:
        if page_id not in self._requests:
            self._requests[page_id] = self._json(f"pages/{page_id}/request.json") or {}
        return self._requests[page_id]

    def word_count(self, page_id: str) -> int:
        t = self.extracted(page_id).get("text") or {}
        return t.get("word_count") or t.get("main_word_count") or 0

    def looks_like_shell(self, page_id: str) -> bool:
        ex = self.extracted(page_id)
        rs = ex.get("render_signals") or {}
        ratio = (ex.get("text") or {}).get("text_to_markup_ratio")
        return bool(
            (rs.get("app_shell_selectors") or [])
            and (rs.get("hydration_payload_bytes") or 0) >= SHELL_HYDRATION_BYTES
            and isinstance(ratio, (int, float)) and ratio < SHELL_TEXT_RATIO)

    @property
    def content_pages(self) -> list:
        """200 pages whose content the visitor actually receives. A client-render
        shell's engagement gaps belong to READ-001; a thin-but-served page does
        not and is assessed here."""
        return [p for p in self.ok_pages if not self.looks_like_shell(p["page_id"])]

    @property
    def home(self) -> dict:
        for p in self.ok_pages:
            if p.get("page_type") == "home":
                return p
        for p in self.ok_pages:
            if urlparse(_url(p)).path.rstrip("/") in ("", "/"):
                return p
        return self.ok_pages[0] if self.ok_pages else {}

    def in_content_links(self, page_id: str) -> list:
        return [l for l in (self.extracted(page_id).get("links") or [])
                if l.get("internal") and not l.get("in_nav")]

    @property
    def has_renderer(self) -> bool:
        return bool((self.run.get("renderer") or {}).get("available"))

    @property
    def site_profile(self) -> str:
        if self._site_type is not None:
            return self._site_type
        explicit = self.run.get("site_profile") or self.manifest.get("site_profile")
        if isinstance(explicit, dict) and explicit.get("site_type"):
            self._site_type = explicit["site_type"]
            return self._site_type
        if isinstance(explicit, str) and explicit:
            self._site_type = explicit
            return self._site_type
        types, paths = set(), []
        has_pricing = has_docs = has_cart = False
        article_count = product_pages = 0
        for p in self.ok_pages:
            path = urlparse(_url(p)).path.lower()
            paths.append(path)
            if any(c in path for c in ("/cart", "/checkout", "/basket")):
                has_cart = True
            if any(pr in path for pr in ("/pricing", "/plans")):
                has_pricing = True
            if "/docs" in path or "/reference" in path or "/api" in path:
                has_docs = True
            for block in self.extracted(p["page_id"]).get("jsonld") or []:
                if block.get("parsed_ok"):
                    for t in _jsonld_types(block.get("value")):
                        types.add(t.lower())
            if p.get("page_type") == "article":
                article_count += 1
            if p.get("page_type") == "product":
                product_pages += 1
        # A single Product JSON-LD block on one page is not an ecommerce site;
        # require a cart, product URLs, or several product pages.
        if has_cart or any("/product" in x or "/shop" in x for x in paths) or product_pages >= 2:
            self._site_type = "ecommerce"
        elif "softwareapplication" in types or (has_pricing and has_docs):
            self._site_type = "saas"
        elif "localbusiness" in types or any(t.endswith("business") for t in types):
            self._site_type = "local-business"
        elif article_count >= 2 or "newsarticle" in types:
            self._site_type = "media-publisher"
        elif has_docs:
            self._site_type = "docs"
        elif len(self.ok_pages) < 20 and not has_pricing and not has_cart:
            self._site_type = "portfolio-brochure"
        else:
            self._site_type = "unknown"
        return self._site_type


# --------------------------------------------------------------------------
# helpers -- finding() and act() copied verbatim from the reference impl
# --------------------------------------------------------------------------

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
# small helpers
# --------------------------------------------------------------------------

def _url(p: dict) -> str:
    return p.get("url") or p.get("final_url") or ""


def _url_depth(url: str) -> int:
    segs = [s for s in urlparse(url).path.split("/") if s and s.lower() not in
            ("index.html", "index.htm", "index.php")]
    if segs and re.search(r"\.(html?|php|aspx?)$", segs[-1], re.I):
        segs = segs[:-1]
    return len(segs)


def _first_screen(ex: dict, n: int = 220) -> str:
    heads = ex.get("headings") or []
    first_head = heads[0]["text"] if heads else ""
    body = (ex.get("text") or {}).get("main") or (ex.get("text") or {}).get("full") or ""
    combined = (first_head + " -- " + body) if first_head and not body.startswith(first_head) else body
    return re.sub(r"\s+", " ", combined[:n]).strip()


def _jsonld_types(node) -> list:
    out = []
    if isinstance(node, dict):
        t = node.get("@type")
        if isinstance(t, str):
            out.append(t)
        elif isinstance(t, list):
            out.extend(x for x in t if isinstance(x, str))
        for v in node.values():
            out.extend(_jsonld_types(v))
    elif isinstance(node, list):
        for it in node:
            out.extend(_jsonld_types(it))
    return out


def _images_above_fold(images: list, k: int = 3) -> list:
    """First few images in document order -- our only approximation of the fold."""
    return images[:k]


# --------------------------------------------------------------------------
# checks -- checks.yaml order
# --------------------------------------------------------------------------

def check_stay_001(b: Bundle) -> list:
    """The top of the page does not say what this is. Model-judged: the script
    flags a home/landing page whose first screen names no offering; the agent
    confirms. The fold is approximated from document order."""
    out = []
    landing = [p for p in b.content_pages
               if p.get("page_type") in ("home", "category", "product", "other")]
    for p in landing:
        ex = b.extracted(p["page_id"])
        # Guard: do not fire where the content is missing from OUR view rather
        # than the visitor's -- a shell is already excluded by content_pages.
        heads = [h.get("text", "") for h in ex.get("headings") or []]
        first = " ".join(heads[:1]) + " " + " ".join(
            re.split(r"(?<=[.!?])\s+", (ex.get("text") or {}).get("main") or "")[:2])
        first_l = first.lower()
        # "says what is offered" ~ mentions the brand or a concrete offering noun
        # alongside a verb of provision, OR names a product category.
        names_offering = bool(re.search(
            r"\b(is|are|offers?|provides?|sells?|makes?|builds?|helps?|serves?|"
            r"specialis|specializ)\b", first_l)) and bool(re.search(
            r"\b(coffee|software|platform|service|tool|shop|store|agency|studio|"
            r"consultanc|roaster|product|subscription|course|clinic|firm|app|"
            r"marketplace|solution|company|brand)\b", first_l))
        if names_offering:
            continue
        excerpt = _first_screen(ex)
        severity = "high" if p.get("page_type") == "home" else "medium"
        out.append(finding(
            "STAY-001",
            "The top of the page does not say what this is",
            severity,
            ("Approximating the fold from document order, the first content on {u} "
             "is \"{ex}\", which names no offering or audience."
             ).format(u=_url(p), ex=excerpt),
            ["MANIFEST.json", f"pages/{p['page_id']}/extracted.json",
             f"pages/{p['page_id']}/raw.html"],
            pages=[_url(p)],
            counts={"first_screen_words": len(excerpt.split())},
            confidence="medium",
            determinism="model-judged",
            verification="Load {} and read only what is visible without scrolling".format(_url(p)),
            excerpt=excerpt,
            scope="page", checked=len(b.content_pages),
            action=act(
                "Open the page with one line stating what is offered and to whom",
                severity,
                ["Replace the abstract hero line with '<what it is> for <who>'",
                 "Keep it in the first paragraph, before any imagery-only section",
                 "The same sentence doubles as the meta description and the "
                 "identity line an assistant quotes"],
                "S",
                "A visitor who arrives from an AI answer spends a second deciding "
                "they are in the right place. A hero that says 'Excellence, "
                "delivered' gives them nothing to confirm against, so they leave.",
                owner="content")))
    return out


def check_stay_002(b: Bundle) -> list:
    """Pages do not continue the conversation visitors arrive from. Model-judged,
    confidence at most 'medium'. The signal: the site offers no deep-linkable
    page for the specific questions its own content implies -- only broad entry
    points. A judgment call, never stated as measured fact."""
    if b.site_profile == "docs":
        return []  # guard: docs sites answer specific questions by construction
    content = b.content_pages
    if len(content) < 3:
        return []
    specific_types = {"faq", "pricing", "product", "article", "docs", "comparison"}
    have_specific = [p for p in content if p.get("page_type") in specific_types]
    # Only a signal when essentially every entry point is generic.
    if have_specific:
        return []
    generic = [p for p in content
               if p.get("page_type") in ("home", "about", "category", "other")]
    if len(generic) < len(content):
        return []
    home = b.home
    excerpt = _first_screen(b.extracted(home["page_id"])) if home else ""
    # Guard (agent): derive the likely arrival questions from the SITE'S OWN
    # content and category, not a generic list. The finding is that no SPECIFIC
    # page exists to land on -- not that the home page is broad.
    return [finding(
        "STAY-002",
        "Pages do not continue the conversation visitors arrive from",
        "medium",
        ("All {n} sampled pages are broad entry points (home/about/category); no "
         "FAQ, pricing, product or article page exists for an assistant to link a "
         "visitor straight to. The home page opens with \"{ex}\"."
         ).format(n=len(content), ex=excerpt),
        ["MANIFEST.json"] + ([f"pages/{home['page_id']}/extracted.json"] if home else []),
        counts={"content_pages": len(content), "specific_landing_pages": 0},
        confidence="medium",
        determinism="model-judged",
        verification=("Ask an assistant about something this site covers, follow "
                      "the link it gives, and see whether that page answers the "
                      "question you asked"),
        excerpt=excerpt,
        scope="site-wide", checked=len(content),
        action=act(
            "Build a deep-linkable page for each question the site's content implies",
            "medium",
            ["List the specific questions your category's buyers ask (from sales "
             "and support), not a generic list",
             "Give each its own URL with the answer in the first screen",
             "These are the pages an assistant cites and the pages a referred "
             "visitor should land on"],
            "M",
            "A visitor arriving from an AI answer already holds a specific "
            "question. Landing them on a page that restarts from the top loses "
            "them even though every upstream stage worked.",
            owner="content"))]


def check_stay_003(b: Bundle) -> list:
    """No clear next action. Deterministic, confidence 'medium' -- we see link
    text and position, not visual weight."""
    out = []
    for p in b.content_pages:
        pt = p.get("page_type")
        # Guard: editorial, documentation and legal pages need no CTA.
        if pt in ("article", "docs", "legal", "faq", "about", "contact"):
            continue
        ex = b.extracted(p["page_id"])
        links = ex.get("links") or []
        forms = ex.get("forms") or []
        cta_links = sorted({(l.get("text") or "").strip() for l in links
                            if CTA_RE.search(l.get("text") or "")})
        onward = b.in_content_links(p["page_id"])
        if len(cta_links) >= 6:
            out.append(finding(
                "STAY-003", "No clear next action", "medium",
                ("{u} presents {n} calls to action of similar prominence "
                 "({sample}...), so none reads as the primary one."
                 ).format(u=_url(p), n=len(cta_links), sample=", ".join(cta_links[:4])),
                ["MANIFEST.json", f"pages/{p['page_id']}/extracted.json"],
                pages=[_url(p)],
                counts={"cta_links": len(cta_links)},
                confidence="medium",
                verification="Open {} and identify the single action it wants from you".format(_url(p)),
                scope="page", checked=len(b.content_pages),
                action=act(
                    "Make one action primary and demote the rest",
                    "medium",
                    ["Pick the single action this page exists to drive",
                     "Style it as the one primary button; make the others text links",
                     "Move secondary actions out of the hero"],
                    "S",
                    "A page offering six equal choices makes the visitor choose "
                    "how to proceed, and many resolve that by leaving.",
                    owner="content")))
        elif pt in ("home", "pricing", "product") and not onward and not forms \
                and not any(CTA_RE.search(l.get("text") or "") for l in links):
            out.append(finding(
                "STAY-003", "No clear next action", "medium",
                ("{u} is a {t} page with no in-content link, no form and no "
                 "call-to-action text -- nothing tells the visitor what to do next."
                 ).format(u=_url(p), t=pt),
                ["MANIFEST.json", f"pages/{p['page_id']}/extracted.json"],
                pages=[_url(p)],
                counts={"in_content_links": 0, "forms": 0, "cta_links": 0},
                confidence="medium",
                verification="Open {} and identify the single action it wants from you".format(_url(p)),
                scope="page", checked=len(b.content_pages),
                action=act(
                    "Add one primary call to action to this page",
                    "medium",
                    ["Decide the one step this page should drive (start trial, "
                     "contact sales, view a plan)",
                     "Add it as a prominent button in the first screen",
                     "Link it to the page that completes that step"],
                    "S",
                    "A conversion page with no action is a dead-end even when the "
                    "content is persuasive.",
                    owner="content")))
    return out


def check_stay_004(b: Bundle) -> list:
    """Pages dead-end with nowhere to go next. Deterministic. In-content links
    only -- global navigation is not a next step."""
    assessed = [p for p in b.content_pages
                if p.get("page_type") not in ENDPOINT_PAGE_TYPES]
    if not assessed:
        return []
    dead = [p for p in assessed if len(b.in_content_links(p["page_id"])) == 0]
    if not dead:
        return []
    home = b.home
    home_id = home.get("page_id") if home else None
    home_is_dead = any(p["page_id"] == home_id for p in dead)
    share = len(dead) / len(assessed)

    # Guard: contact / thank-you / legal are legitimate endpoints (excluded
    # above). Fire when the universal entry point itself dead-ends, or when the
    # great majority of content pages do.
    if not (home_is_dead or (len(assessed) >= 4 and share >= 0.85)):
        return []

    urls = sorted(_url(p) for p in dead)
    return [finding(
        "STAY-004",
        "Pages dead-end with nowhere to go next",
        "medium",
        ("{n} of {m} content pages carry no in-content internal link beyond "
         "global navigation: {u}{more}."
         ).format(n=len(dead), m=len(assessed), u=", ".join(urls[:4]),
                  more=", ..." if len(urls) > 4 else ""),
        ["MANIFEST.json"] + [f"pages/{p['page_id']}/extracted.json" for p in dead[:5]],
        pages=urls,
        counts={"dead_end_pages": len(dead), "content_pages": len(assessed)},
        confidence="medium",
        verification="Read to the end of {} and look for a next step".format(urls[0]),
        scope="site-wide" if len(urls) >= 3 else ("section" if len(urls) > 1 else "page"),
        checked=len(b.content_pages),
        action=act(
            "End each page with a relevant onward link in the content",
            "medium",
            ["Add 2-3 contextual links in the body or a 'next' block -- to the "
             "pricing page from a feature page, to related articles from a post",
             "These are in-content links, not the header nav",
             "The home page especially must lead somewhere specific"],
            "S",
            "A visitor who finishes a page with no onward link in front of them "
            "leaves rather than hunting the navigation for what to read next.",
            owner="content"))]


def check_stay_005(b: Bundle) -> list:
    """Visitors cannot tell where they are in the site. Deterministic. Gate on
    actual URL depth -- flat sites need no breadcrumbs."""
    deep = [p for p in b.content_pages if _url_depth(_url(p)) >= 3]
    if len(deep) < 2:
        return []
    def has_orientation(page):
        ex = b.extracted(page["page_id"])
        for block in ex.get("jsonld") or []:
            if block.get("parsed_ok") and "breadcrumblist" in \
                    [t.lower() for t in _jsonld_types(block.get("value"))]:
                return True
        raw = b.raw_html(page["page_id"]).lower()
        return "breadcrumb" in raw or 'aria-label="breadcrumb"' in raw
    missing = [p for p in deep if not has_orientation(p)]
    if not missing:
        return []
    depth = min(_url_depth(_url(p)) for p in missing)
    # Guard (agent): overlaps PARSE-013 (the markup). This reports the
    # visitor-facing orientation gap only.
    return [finding(
        "STAY-005",
        "Visitors cannot tell where they are in the site",
        "medium",
        ("{n} of {m} sampled pages at URL depth {d} or greater show no breadcrumb "
         "or section navigation in the HTML."
         ).format(n=len(missing), m=len(deep), d=depth),
        ["MANIFEST.json"] + [f"pages/{p['page_id']}/raw.html" for p in missing[:5]],
        pages=sorted(_url(p) for p in missing),
        counts={"deep_pages_without_orientation": len(missing), "deep_pages": len(deep)},
        confidence="medium",
        verification=("Open {} directly and try to identify which section it "
                      "belongs to").format(sorted(_url(p) for p in missing)[0]),
        scope="section", checked=len(b.content_pages),
        action=act(
            "Add a breadcrumb trail to pages more than two levels deep",
            "medium",
            ["Render a breadcrumb (Home / Section / Page) at the top of deep pages",
             "Mirror it as BreadcrumbList JSON-LD",
             "Keep the current section highlighted in the primary nav"],
            "S",
            "A visitor who lands deep from a search or an AI link needs to see "
            "where they are to trust the page and to explore sideways rather "
            "than bounce.",
            owner="engineering"))]


def check_stay_006(b: Bundle) -> list:
    """The site discards the context a visitor arrived with. Model-judged /
    inferred (no JS execution). A search or filter whose state is not in the URL
    cannot be linked, shared or returned to."""
    out = []
    for p in b.content_pages:
        raw = b.raw_html(p["page_id"])
        if not SEARCH_FORM_RE.search(raw):
            continue
        # Guard: a form with method=GET already puts state in the URL.
        forms = b.extracted(p["page_id"]).get("forms") or []
        get_form = any((f.get("method") or "get").lower() == "get" for f in forms)
        post_search = re.search(r"<form[^>]+method=\"post\"[^>]*>.*?(?:type=\"search\"|"
                                r"role=\"search\"|name=\"(?:q|query|search)\")",
                                raw, re.I | re.S)
        if get_form and not post_search:
            continue
        mechanism = "search form" if re.search(r"type=\"search\"|role=\"search\"", raw, re.I) \
            else "filter control"
        out.append(finding(
            "STAY-006",
            "The site discards the context a visitor arrived with",
            "medium",
            ("Inferred from markup (JavaScript not executed): {u} carries a {m} "
             "that appears to POST or update in place, so its state does not "
             "reach the URL and a result set cannot be linked or shared."
             ).format(u=_url(p), m=mechanism),
            ["MANIFEST.json", f"pages/{p['page_id']}/raw.html"],
            pages=[_url(p)],
            counts={},
            confidence="medium",
            determinism="model-judged",
            verification=("Run a search or apply a filter on {} and check whether "
                          "the URL changes").format(_url(p)),
            scope="page", checked=len(b.content_pages),
            action=act(
                "Carry search and filter state in the URL",
                "medium",
                ["Set the search form to method=GET so the query lands in the URL",
                 "Reflect each active filter as a query parameter",
                 "Make the filtered URL a real, indexable, shareable page"],
                "M",
                "A visitor who filters to what they want and cannot bookmark or "
                "share it, or loses it on the back button, abandons the task.",
                owner="engineering")))
    return out


def check_stay_007(b: Bundle) -> list:
    """An interstitial blocks the page on arrival. Deterministic -- only overlays
    present in the INITIAL HTML (we cannot see delayed pop-ups)."""
    out = []
    for p in b.content_pages:
        raw = b.raw_html(p["page_id"])
        m = INTERSTITIAL_RE.search(raw)
        if not m:
            continue
        is_consent = bool(CONSENT_RE.search(raw[max(0, m.start() - 200):m.start() + 200]))
        text_len = len((b.extracted(p["page_id"]).get("text") or {}).get("main") or "")
        # Guard: content served beneath the overlay -> STAY finding at most.
        # Content withheld until consent -> READ-013 owns it (we do not escalate).
        overlay_type = "a consent notice" if is_consent else "a modal or overlay"
        # Guard: legally-required consent notices are not defects -- recommend
        # serving content beneath them, do not recommend removal.
        severity = "medium"
        out.append(finding(
            "STAY-007",
            "An interstitial blocks the page on arrival",
            severity,
            ("{u} includes {ot} in the initial HTML ({snippet}). Content of "
             "{tl} characters is served on the page beneath it."
             ).format(u=_url(p), ot=overlay_type,
                      snippet=re.sub(r"\s+", " ", m.group(0))[:80], tl=text_len),
            ["MANIFEST.json", f"pages/{p['page_id']}/raw.html"],
            pages=[_url(p)],
            counts={"main_text_chars": text_len},
            confidence="medium",
            verification=("Open {} in a private window and note what appears "
                          "before the content").format(_url(p)),
            scope="page", checked=len(b.content_pages),
            action=act(
                "Serve the content behind the overlay, not instead of it",
                "medium",
                ["Render the full page first; layer the notice on top",
                 "For a required consent notice, keep it but do not block scroll "
                 "or hide the main content",
                 "Do not trigger newsletter or promo modals on first view"],
                "S",
                "An overlay on entry costs the visitor an action before they have "
                "decided the page is worth one.",
                owner="engineering")))
    return out


def check_stay_008(b: Bundle) -> list:
    """Pages are heavy enough to slow first render. Deterministic STATIC PROXY --
    not Core Web Vitals. Never above 'medium'."""
    heavy = []
    for p in b.content_pages:
        ex = b.extracted(p["page_id"])
        transfer = ((b.request(p["page_id"]).get("timing") or {}).get("transfer_bytes")
                    or (ex.get("timing") or {}).get("transfer_bytes") or 0)
        blocking = [s for s in ex.get("scripts") or [] if s.get("blocking")]
        imgs = ex.get("images") or []
        no_lazy = [i for i in imgs if (i.get("loading") or "").lower() != "lazy"]
        if transfer >= 2_000_000 and len(blocking) >= 3:
            heavy.append((p, transfer, len(blocking), len(no_lazy)))
    if not heavy:
        return []
    p, transfer, nblock, nolazy = heavy[0]
    return [finding(
        "STAY-008",
        "Pages are heavy enough to slow first render",
        "medium",
        ("Static proxy from the HTML (no subresources fetched, no browser "
         "measurement): {u} transfers {kb} KB of HTML with {n} render-blocking "
         "script(s) and {k} image(s) without loading=\"lazy\"."
         ).format(u=_url(p), kb=transfer // 1024, n=nblock, k=nolazy),
        ["MANIFEST.json", f"pages/{p['page_id']}/extracted.json",
         f"pages/{p['page_id']}/request.json"],
        pages=[_url(pp) for pp, *_ in heavy],
        counts={"html_bytes": transfer, "render_blocking_scripts": nblock,
                "images_without_lazy": nolazy},
        confidence="medium",
        verification=("Open {} with the browser network panel and check transfer "
                      "size and blocking requests").format(_url(p)),
        scope="section" if len(heavy) > 1 else "page",
        checked=len(b.content_pages),
        action=act(
            "Cut render-blocking weight from the critical path",
            "medium",
            ["Add defer or async to scripts that are not needed for first paint",
             "Add loading=\"lazy\" to below-the-fold images",
             "Reduce the HTML payload where it carries inlined data or markup bloat"],
            "M",
            "Every render-blocking request delays the moment the visitor sees "
            "content, and the ones who leave before first paint are counted as an "
            "instant bounce.",
            owner="engineering"))]


def check_stay_009(b: Bundle) -> list:
    """Images without dimensions risk layout shift. Deterministic proxy --
    phrase as a risk, not a measured shift (CSS aspect-ratio is invisible to us)."""
    site_imgs = 0
    site_nodim = 0
    worst = None
    for p in b.content_pages:
        imgs = b.extracted(p["page_id"]).get("images") or []
        if not imgs:
            continue
        nodim = [i for i in imgs if i.get("width") is None and i.get("height") is None]
        site_imgs += len(imgs)
        site_nodim += len(nodim)
        # "above the fold" ~ the first few images in document order.
        af = _images_above_fold(imgs)
        af_nodim = [i for i in af if i.get("width") is None and i.get("height") is None]
        if af_nodim and (worst is None or len(af_nodim) > worst[2]):
            worst = (p, len(af), len(af_nodim), len(imgs), len(nodim))
    if site_nodim == 0:
        return []
    # Guard: cap confidence at 'medium' and phrase as a risk. Severity is
    # 'medium' when most of the likely above-the-fold images lack dimensions,
    # 'low' otherwise.
    if worst and worst[2] >= max(1, worst[1] // 2):
        p = worst[0]
        severity = "medium"
        evidence = ("On {u}, {a} of the first {b} images (the best available "
                    "proxy for above-the-fold) declare neither width nor height; "
                    "{c} of {d} images site-wide lack dimensions. Reserving no "
                    "space for them risks layout shift as they load."
                    ).format(u=_url(p), a=worst[2], b=worst[1],
                             c=site_nodim, d=site_imgs)
        pages = [_url(p)]
        refs = ["MANIFEST.json", f"pages/{p['page_id']}/extracted.json"]
    else:
        severity = "low"
        evidence = ("{n} of {m} sampled images declare neither width nor height, "
                    "risking layout shift as they load (CSS aspect-ratio, which we "
                    "cannot see, would also reserve space)."
                    ).format(n=site_nodim, m=site_imgs)
        pages = []
        refs = ["MANIFEST.json"]
    return [finding(
        "STAY-009",
        "Images without dimensions risk layout shift",
        severity, evidence, refs,
        pages=pages,
        counts={"images_without_dimensions": site_nodim, "images_total": site_imgs},
        confidence="medium",
        verification=("curl -s <page> | grep -c '<img' and compare with the count "
                      "carrying a width attribute"),
        scope="page" if pages else "site-wide",
        checked=len(b.content_pages),
        action=act(
            "Declare width and height (or aspect-ratio) on every content image",
            severity,
            ["Add width and height attributes matching the image's intrinsic size",
             "Or set aspect-ratio in CSS on the image container",
             "Prioritise images in the first screen, where a shift is most jarring"],
            "S",
            "An image with no reserved space pushes content down when it loads, "
            "and a visitor who was about to click the thing that moved is a "
            "visitor who mis-clicks and leaves.",
            code='<img src="/hero.jpg" width="1200" height="600" alt="...">',
            owner="engineering"))]


def check_stay_010(b: Bundle) -> list:
    """The site is not usable on mobile. Deterministic. A missing viewport tag is
    strong evidence and the one proxy the rule allows at 'high'; anything richer
    is not visible to us."""
    no_vp, fixed_vp, no_scale = [], [], []
    for p in b.content_pages:
        meta = b.extracted(p["page_id"]).get("meta") or {}
        vp = (meta.get("viewport") or "").lower()
        if not vp:
            no_vp.append(p)
        else:
            if "width=device-width" not in vp and re.search(r"width=\d", vp):
                fixed_vp.append(p)
            if "user-scalable=no" in vp or "maximum-scale=1" in vp.replace(" ", ""):
                no_scale.append(p)
    out = []
    if no_vp:
        checked = len(b.content_pages)
        out.append(finding(
            "STAY-010",
            "The site is not usable on mobile",
            "high",
            ("{n} of {m} sampled pages declare no viewport meta tag, so mobile "
             "browsers render them at desktop width and zoom out."
             ).format(n=len(no_vp), m=checked),
            ["MANIFEST.json"] + [f"pages/{p['page_id']}/extracted.json" for p in no_vp[:5]],
            pages=sorted(_url(p) for p in no_vp),
            counts={"pages_without_viewport": len(no_vp), "sampled": checked},
            verification="curl -s {} | grep -i 'name=\"viewport\"'".format(_url(no_vp[0])),
            scope="site-wide" if len(no_vp) == checked and checked >= 3 else (
                "section" if len(no_vp) > 1 else "page"),
            checked=checked,
            action=act(
                "Add a responsive viewport meta tag to every page",
                "high",
                ["Put the tag in the base template <head>",
                 "Use width=device-width, initial-scale=1",
                 "Do not set user-scalable=no -- it blocks pinch-zoom"],
                "S",
                "Without the tag a phone renders the page at ~980px and shrinks "
                "it to fit; text is unreadable and taps miss, and mobile is most "
                "of the traffic an AI answer sends.",
                code='<meta name="viewport" content="width=device-width, initial-scale=1">',
                owner="engineering")))
    if fixed_vp or no_scale:
        affected = sorted({_url(p) for p in fixed_vp} | {_url(p) for p in no_scale})
        # Guard: user-scalable=no is an accessibility problem worth reporting at 'low'.
        out.append(finding(
            "STAY-010",
            "The viewport is fixed-width or blocks zoom",
            "low" if no_scale and not fixed_vp else "medium",
            ("{n} sampled page(s) set a {what} viewport."
             ).format(n=len(affected),
                      what="fixed-width" if fixed_vp else "zoom-disabled"),
            ["MANIFEST.json"] + [f"pages/{p['page_id']}/extracted.json"
                                 for p in (fixed_vp or no_scale)[:5]],
            pages=affected,
            counts={"fixed_width": len(fixed_vp), "zoom_disabled": len(no_scale)},
            verification="curl -s {} | grep -i 'name=\"viewport\"'".format(affected[0]),
            scope="section" if len(affected) > 1 else "page",
            checked=len(b.content_pages),
            action=act(
                "Use a responsive, zoomable viewport",
                "medium",
                ["Set content=\"width=device-width, initial-scale=1\"",
                 "Remove user-scalable=no and maximum-scale=1"],
                "S",
                "A fixed-width viewport forces horizontal scrolling on phones; "
                "disabling zoom locks out anyone who needs to enlarge text.",
                owner="engineering")))
    return out


def check_stay_011(b: Bundle) -> list:
    """Content is hard to read. Deterministic, restricted to structural density
    (words per heading). We do not assess typography, contrast or reading level."""
    out = []
    for p in b.content_pages:
        ex = b.extracted(p["page_id"])
        words = (ex.get("text") or {}).get("word_count") or 0
        subs = [h for h in ex.get("headings") or [] if h.get("level", 1) >= 2]
        if words < 600:
            continue
        wph = words / max(1, len(subs))
        if len(subs) >= 2 and wph <= 350:
            continue
        severity = "medium" if len(subs) <= 1 else "low"
        out.append(finding(
            "STAY-011",
            "Content is hard to read",
            severity,
            ("{u} runs {w} words with {n} subheading(s) -- about {wph} words per "
             "section. Long unbroken text is skimmed and abandoned. (Structural "
             "density only; typography and contrast are not assessed.)"
             ).format(u=_url(p), w=words, n=len(subs), wph=int(wph)),
            ["MANIFEST.json", f"pages/{p['page_id']}/extracted.json"],
            pages=[_url(p)],
            counts={"words": words, "subheadings": len(subs)},
            confidence="medium",
            verification="Scroll {} and look for structure breaking up the text".format(_url(p)),
            scope="page", checked=len(b.content_pages),
            action=act(
                "Break long pages into scannable sections",
                severity,
                ["Add a descriptive subheading every 200-300 words",
                 "Pull key points into short lists",
                 "Front-load each section with its conclusion"],
                "S",
                "A wall of text with no landmarks is skimmed for an exit, not "
                "read; subheadings give a scanner reasons to stay.",
                owner="content")))
    return out


def check_stay_012(b: Bundle) -> list:
    """Forms ask for more than the visitor is ready to give. Deterministic. Only
    fires where a form exists; checkout / application / account forms
    legitimately need many fields."""
    out = []
    for p in b.content_pages:
        pt = p.get("page_type")
        if pt in ("legal",):
            continue
        for i, f in enumerate(b.extracted(p["page_id"]).get("forms") or []):
            fields = f.get("field_count") or 0
            required = f.get("required_count") or 0
            # Guard: gate on funnel position. A checkout / account / application
            # form needs many fields; a top-of-funnel form (home, landing,
            # contact, pricing, about) does not.
            top_of_funnel = pt in ("home", "pricing", "about", "contact", "other",
                                   "landing", "category", "product")
            action = (f.get("action") or "").lower()
            if any(w in action for w in ("checkout", "payment", "account", "register",
                                         "signup", "apply", "application")):
                continue
            if not top_of_funnel:
                continue
            if required >= 6 or (fields >= 8 and required >= 4):
                out.append(finding(
                    "STAY-012",
                    "Forms ask for more than the visitor is ready to give",
                    "medium",
                    ("The form on {u} has {n} fields, {r} of them required, on a "
                     "{t} page -- more commitment than a first interaction "
                     "usually earns."
                     ).format(u=_url(p), n=fields, r=required, t=pt),
                    ["MANIFEST.json", f"pages/{p['page_id']}/extracted.json"],
                    pages=[_url(p)],
                    counts={"fields": fields, "required": required},
                    confidence="medium",
                    verification="Open {} and count the required fields before submission".format(_url(p)),
                    scope="page", checked=len(b.content_pages),
                    action=act(
                        "Cut the top-of-funnel form to the fewest fields that work",
                        "medium",
                        ["Ask only for what you need to take the next step "
                         "(often just an email)",
                         "Make everything else optional or collect it later",
                         "Move long forms to after the visitor has committed"],
                        "S",
                        "Each required field is a reason to abandon; a first-touch "
                        "form that asks for six loses most of the people who "
                        "started it.",
                        owner="content")))
    return out


def check_stay_013(b: Bundle) -> list:
    """Accessibility basics are missing. Deterministic and LIMITED IN SCOPE --
    not a full accessibility audit. Only the mechanical checks the bundle
    supports: form inputs without a label, and absent landmark elements."""
    unlabelled_total = 0
    pages_hit = []
    no_landmark = []
    for p in b.content_pages:
        raw = b.raw_html(p["page_id"])
        unlabelled = 0
        for m in re.finditer(r"<(input|select|textarea)\b[^>]*>", raw, re.I):
            tag = m.group(0)
            itype = re.search(r'type="([^"]+)"', tag, re.I)
            if itype and itype.group(1).lower() in ("hidden", "submit", "button",
                                                    "image", "reset"):
                continue
            if LABELLED_INPUT_ATTR_RE.search(tag) or re.search(r'\btitle="', tag, re.I):
                continue
            idm = re.search(r'\bid="([^"]+)"', tag, re.I)
            if idm and re.search(r'<label[^>]+for="%s"' % re.escape(idm.group(1)), raw, re.I):
                continue
            # a <label> wrapping the input is also valid; approximate by checking
            # for any <label> in the same form when the field count is small.
            unlabelled += 1
        if unlabelled:
            unlabelled_total += unlabelled
            pages_hit.append((p, unlabelled))
        low = raw.lower()
        if not any(t in low for t in ("<main", "<nav", 'role="main"', 'role="navigation"',
                                      "<header", "<footer")):
            no_landmark.append(p)

    if not pages_hit and not no_landmark:
        return []
    parts = []
    if pages_hit:
        parts.append("{} form input(s) across {} page(s) have no associated "
                     "<label>, aria-label or title".format(unlabelled_total, len(pages_hit)))
    if no_landmark:
        parts.append("{} page(s) use no landmark elements (<main>, <nav>, "
                     "<header>, <footer>)".format(len(no_landmark)))
    pages = sorted({_url(p) for p, _ in pages_hit} | {_url(p) for p in no_landmark})
    return [finding(
        "STAY-013",
        "Accessibility basics are missing",
        "medium" if pages_hit else "low",
        ("Limited mechanical check (not a full accessibility audit): "
         + "; ".join(parts) + "."),
        ["MANIFEST.json"] + [f"pages/{p['page_id']}/raw.html"
                             for p, _ in pages_hit[:3]]
        + [f"pages/{p['page_id']}/raw.html" for p in no_landmark[:2]],
        pages=pages,
        counts={"unlabelled_inputs": unlabelled_total,
                "pages_without_landmarks": len(no_landmark)},
        confidence="medium",
        verification="Tab through {} using only the keyboard".format(pages[0]),
        scope="section" if len(pages) > 1 else "page",
        checked=len(b.content_pages),
        action=act(
            "Fix the mechanical accessibility basics",
            "medium",
            ["Give every input a <label for> (or an aria-label)",
             "Wrap the page regions in <header>, <nav>, <main>, <footer>",
             "Then run a full accessibility audit -- this check only covers the "
             "mechanical minimum"],
            "S",
            "Unlabelled fields and missing landmarks make the page unusable with "
            "a screen reader or keyboard, and those visitors leave immediately.",
            owner="engineering"))]


def check_stay_014(b: Bundle) -> list:
    """Third-party scripts dominate the page. Deterministic. Render-blocking
    third-party scripts only -- analytics and tag managers are near-universal
    and deliberate."""
    out = []
    for p in b.content_pages:
        scripts = b.extracted(p["page_id"]).get("scripts") or []
        blocking_3p = [s for s in scripts if s.get("third_party") and s.get("blocking")]
        if len(blocking_3p) < 3:
            continue
        hosts = sorted({urlparse(s.get("src") or "").netloc for s in blocking_3p
                        if s.get("src")})
        out.append(finding(
            "STAY-014",
            "Third-party scripts dominate the page",
            "medium",
            ("{u} loads {n} third-party scripts render-blocking, from {hosts}."
             ).format(u=_url(p), n=len(blocking_3p), hosts=", ".join(hosts[:4]) or "unknown hosts"),
            ["MANIFEST.json", f"pages/{p['page_id']}/extracted.json"],
            pages=[_url(p)],
            counts={"render_blocking_third_party": len(blocking_3p)},
            confidence="medium",
            verification="Open the network panel on {} and sort by domain".format(_url(p)),
            scope="page", checked=len(b.content_pages),
            action=act(
                "Load third-party scripts without blocking render",
                "medium",
                ["Add async or defer to every third-party <script>",
                 "Load tag managers and chat widgets after first paint",
                 "Keep analytics -- just stop it blocking the critical path"],
                "S",
                "Render-blocking third-party code holds up the visitor's first "
                "view for a payload that adds nothing to the page they came for.",
                owner="engineering")))
    return out


def check_stay_015(b: Bundle) -> list:
    """Related content is not linked. Deterministic. Gated to content-heavy
    profiles where every page is an entry point."""
    if b.site_profile not in ("ecommerce", "media-publisher", "saas", "marketplace", "docs"):
        b.skip_check("STAY-015", "related-content linking applies to ecommerce, "
                     "media-publisher, saas, marketplace and docs sites; this "
                     "site's profile is {!r}".format(b.site_profile))
        return []
    assessed = [p for p in b.content_pages
                if p.get("page_type") in ("article", "product", "docs", "category")]
    if len(assessed) < 3:
        return []
    isolated = []
    for p in assessed:
        # Guard: related-content modules are often client-rendered. If the page
        # shows render signals, do not claim the module is absent.
        rs = b.extracted(p["page_id"]).get("render_signals") or {}
        if rs.get("app_shell_selectors") or (rs.get("hydration_payload_bytes") or 0) > 4000:
            continue
        if len(b.in_content_links(p["page_id"])) == 0:
            isolated.append(p)
    if len(isolated) < max(3, len(assessed) // 2):
        return []
    return [finding(
        "STAY-015",
        "Related content is not linked",
        "medium",
        ("{n} of {m} content pages link to no related content in the body."
         ).format(n=len(isolated), m=len(assessed)),
        ["MANIFEST.json"] + [f"pages/{p['page_id']}/extracted.json" for p in isolated[:5]],
        pages=sorted(_url(p) for p in isolated),
        counts={"isolated_pages": len(isolated), "content_pages": len(assessed)},
        confidence="medium",
        verification="Read to the end of {} and look for related items".format(
            sorted(_url(p) for p in isolated)[0]),
        scope="site-wide" if len(isolated) >= 3 else "section",
        checked=len(b.content_pages),
        action=act(
            "Link related items at the end of each content page",
            "medium",
            ["Add a 'related' block: 3-5 links to adjacent products, posts or docs",
             "Prefer editorially-chosen links over a generic 'popular' widget",
             "Make sure they are in the HTML, not injected client-side"],
            "S",
            "On a content site every page is an entry point, and a page with no "
            "onward link is a single-page visit.",
            owner="content"))]


def check_stay_016(b: Bundle) -> list:
    """No trust signals near the point of decision. Model-judged. Gated to
    profiles with a transaction to trust."""
    if b.site_profile not in ("ecommerce", "saas", "local-business", "marketplace",
                              "nonprofit-gov"):
        b.skip_check("STAY-016", "trust-signals-near-conversion applies to "
                     "ecommerce, saas, local-business, marketplace and "
                     "nonprofit-gov sites; this site's profile is {!r}".format(
                         b.site_profile))
        return []
    conv = [p for p in b.content_pages
            if p.get("page_type") in ("pricing", "product", "category")]
    if not conv:
        return []
    TRUST_TEXT_RE = re.compile(
        r"\b(review|rated|rating|testimonial|guarantee|money-back|refund|"
        r"secure|trusted by|certified|accredited|iso ?\d|\d+ years|warranty|"
        r"as seen in|case study)\b", re.I)
    bare = []
    for p in conv:
        ex = b.extracted(p["page_id"])
        text = (ex.get("text") or {}).get("full") or ""
        # Guard: trust widgets are often third-party iframes we cannot see.
        if ex.get("iframes"):
            continue
        rs = ex.get("render_signals") or {}
        if rs.get("app_shell_selectors"):
            continue
        has_reviews_ld = any(
            t.lower() in ("review", "aggregaterating")
            for block in ex.get("jsonld") or [] if block.get("parsed_ok")
            for t in _jsonld_types(block.get("value")))
        has_contact = any("tel:" in (l.get("href") or "") or "mailto:" in (l.get("href") or "")
                          for l in ex.get("links") or [])
        if TRUST_TEXT_RE.search(text) or has_reviews_ld or has_contact:
            continue
        bare.append(p)
    if not bare:
        return []
    # Guard (agent): recommend surfacing trust signals that genuinely exist,
    # never inventing reviews or credentials.
    return [finding(
        "STAY-016",
        "No trust signals near the point of decision",
        "medium",
        ("{n} of {m} conversion page(s) show no review, rating, guarantee, "
         "contact route or credential in the served HTML: {u}."
         ).format(n=len(bare), m=len(conv), u=", ".join(sorted(_url(p) for p in bare)[:4])),
        ["MANIFEST.json"] + [f"pages/{p['page_id']}/extracted.json" for p in bare[:5]],
        pages=sorted(_url(p) for p in bare),
        counts={"bare_conversion_pages": len(bare), "conversion_pages": len(conv)},
        confidence="medium",
        determinism="model-judged",
        verification="Open {} and look for reasons to trust the transaction".format(
            sorted(_url(p) for p in bare)[0]),
        scope="section" if len(bare) > 1 else "page",
        checked=len(b.content_pages),
        action=act(
            "Surface the trust signals you already have next to the decision",
            "medium",
            ["Place real reviews, ratings or testimonials on the pricing / product page",
             "State the guarantee, return policy or accreditation near the CTA",
             "Show a contact route -- a phone number or a named person",
             "Only surface what genuinely exists; do not manufacture it"],
            "S",
            "At the moment of committing, a visitor looks for a reason to trust "
            "the transaction. A page that offers none loses the cautious majority.",
            owner="content"))]


CHECKS = [
    check_stay_001, check_stay_002, check_stay_003, check_stay_004,
    check_stay_005, check_stay_006, check_stay_007, check_stay_008,
    check_stay_009, check_stay_010, check_stay_011, check_stay_012,
    check_stay_013, check_stay_014, check_stay_015, check_stay_016,
]

# Every STAY check in references/checks.yaml is implemented above. STAY-015 and
# STAY-016 record themselves as skipped when the site profile is outside their
# applies_when set.
NOT_YET_IMPLEMENTED: list = []


def proactive(b: Bundle, findings: list) -> list:
    """Improvements worth making where no defect was found. Each cites something
    observed in the bundle."""
    out = []
    fired = {f.get("check_id") for f in findings}
    content = b.content_pages
    types = {p.get("page_type") for p in b.ok_pages}

    # STAY-P01 -- a landing page per likely arrival question. Gate: no
    # question-shaped page exists to land on.
    if content and not (types & {"faq", "pricing", "product", "article", "comparison"}):
        out.append({
            "id": "P-000",  # STAY-P01
            "title": "Build a landing page for each question assistants are likely to cite",
            "category": CATEGORY, "mechanism": MECHANISM,
            "rationale": ("The {n} sampled pages include no FAQ, pricing, product "
                          "or article page -- nothing question-shaped for a "
                          "referred visitor to land on directly."
                          ).format(n=len(b.ok_pages)),
            "suggested_action": act(
                "Create a deep-linkable page per common buyer question",
                "low",
                ["List the specific questions your category's buyers ask",
                 "Give each its own URL with the answer in the first screen"],
                "M",
                "The page an assistant cites and the page a referred visitor "
                "should land on are the same page; a site without them has "
                "neither.",
                owner="content"),
        })

    # STAY-P02 -- carry search / filter state in the URL. Gate: a search or
    # filter control was seen.
    has_search = any(SEARCH_FORM_RE.search(b.raw_html(p["page_id"])) for p in content)
    if has_search and "STAY-006" not in fired:
        out.append({
            "id": "P-000",  # STAY-P02
            "title": "Carry search and filter state in the URL",
            "category": CATEGORY, "mechanism": MECHANISM,
            "rationale": ("A search or filter control was seen in the sampled "
                          "HTML. Reflecting its state in the URL makes each "
                          "result set linkable, shareable and reachable with the "
                          "back button."),
            "suggested_action": act(
                "Reflect query and filter state in URL parameters",
                "low",
                ["Use method=GET for search; map each filter to a query param",
                 "Make the resulting URLs real, indexable pages"],
                "M",
                "URL-carried state turns each meaningful result combination into "
                "a page that can be discovered and returned to.",
                owner="engineering"),
        })

    # STAY-P03 -- answer above the fold, elaborate below. Gate: always; emit as a
    # forward-looking note when nothing above fired on the entry pages.
    if content and "STAY-001" not in fired and "STAY-002" not in fired:
        out.append({
            "id": "P-000",  # STAY-P03
            "title": "State the answer above the fold, then elaborate below it",
            "category": CATEGORY, "mechanism": MECHANISM,
            "rationale": ("Across {n} sampled pages the entry points open with a "
                          "heading or hero rather than a one-line answer. Leading "
                          "with the answer serves both halves of the audit at "
                          "once."
                          ).format(n=len(content)),
            "suggested_action": act(
                "Put a one-line answer at the very top of each key page",
                "low",
                ["Open the page with the single sentence a visitor needs to "
                 "confirm they are in the right place",
                 "Follow it with the detail, imagery and secondary actions"],
                "S",
                "The visitor sees immediately they are in the right place, and a "
                "retrieval system finds a self-contained answer at the top "
                "instead of after the preamble.",
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
    args = ap.parse_args(argv)

    if not os.path.isdir(args.bundle):
        print(f"error: {args.bundle!r} is not a bundle directory", file=sys.stderr)
        return 2

    b = Bundle(args.bundle)
    if not b.manifest:
        print(f"error: no readable MANIFEST.json in {args.bundle!r}", file=sys.stderr)
        return 2

    findings: list = []
    for check in CHECKS:
        try:
            findings.extend(check(b) or [])
        except Exception as exc:
            # One broken check must never lose the others.
            print(f"warning: {check.__name__} failed: {type(exc).__name__}: {exc}",
                  file=sys.stderr)

    if not b.content_pages:
        already = {s["check_id"] for s in b.checks_skipped}
        for cid in ("STAY-001", "STAY-002", "STAY-003", "STAY-004", "STAY-005",
                    "STAY-006", "STAY-007", "STAY-011", "STAY-012", "STAY-013"):
            if cid not in already:
                b.skip_check(cid, "no sampled page carries served content; the "
                             "rendering root cause is READ-001")

    kept = []
    for f in findings:
        refs = f["evidence_detail"]["artifact_refs"]
        missing = [r for r in refs if not b.exists(r)]
        if missing:
            print(f"warning: dropping {f['check_id']}: unresolved refs {missing}",
                  file=sys.stderr)
            continue
        kept.append(f)

    try:
        proactive_recs = proactive(b, kept)
    except Exception as exc:
        print(f"warning: proactive() failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        proactive_recs = []

    result = {"skill": "engagement-audit", "mechanism": MECHANISM,
              "bundle": args.bundle, "findings": kept,
              "proactive_recommendations": proactive_recs,
              "checks_skipped": b.checks_skipped,
              "checks_not_implemented": NOT_YET_IMPLEMENTED}

    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out and not args.stdout:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
        print(f"{len(kept)} STAY candidates -> {args.out}", file=sys.stderr)
        for f in kept:
            print(f"  {f['check_id']:11} {f['severity']:8} {f['title']}", file=sys.stderr)
        for s in b.checks_skipped:
            print(f"  skipped {s['check_id']}: {s['reason'][:66]}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
