#!/usr/bin/env python3
"""TRUST checks: will a machine believe and repeat the fact it extracted?

Standard library only -- ships inside the submission and must run on a bare
Python 3.9+ install.

Reads a completed evidence bundle and emits candidate findings against
../audit-orchestrator/references/finding.schema.json. Performs no network I/O:
every result is a pure function of the bundle, so the same bundle always yields
byte-identical findings.

Structure mirrors ../crawl-access-audit/scripts/check_access.py (the reference
implementation):

  * load the bundle once, into a small accessor object
  * one function per check, named check_trust_<nnn>, returning zero or more
    candidates
  * every candidate cites artifact_refs that actually exist in the bundle
  * false-positive guards live next to the logic that would trip them, as code
    where mechanical and as an explicit comment where they need agent judgment
  * base severity only -- the orchestrator owns scope and confidence modifiers

This is the only analysis skill with an OPTIONAL off-site component. The on-site
freshness and identity checks always run. The corroboration checks that need a
web search or fetch tool (TRUST-006, 007, 009, 012, 013) are SKIPPED here and
recorded in `checks_skipped`, which the orchestrator folds into
coverage.checks_skipped. Absence of a lookup is never evidence of absence.

Usage:
    python check_trust.py <bundle> --out trust-candidates.json
    python check_trust.py <bundle> --stdout
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time
from collections import Counter
from urllib.parse import urlparse

MECHANISM = "trust"
CATEGORY = "discoverability"

# Checks that cannot run without a web search / fetch tool. This script has none,
# so they are always skipped and recorded (checks.yaml, SKILL.md step 3).
OFFSITE_CHECKS = {
    "TRUST-006": "corroborating the brand's key claims against independent sources",
    "TRUST-007": "searching for the brand name to see what other entities it collides with",
    "TRUST-009": "checking the identity anchors (directories, registries, review sites) for the brand",
    "TRUST-012": "comparing how independent sources describe the organisation with its own positioning",
    "TRUST-013": "searching for independent coverage, reviews or citations of the brand",
}

# Per-profile staleness thresholds, in days (site-profiles.md). Profiles absent
# from this table (portfolio-brochure, unknown) get no cadence judgement at all.
STALENESS_DAYS = {
    "media-publisher": 30,
    "ecommerce": 90,
    "saas": 180,
    "docs": 365,
    "local-business": 365,
    "nonprofit-gov": 365,
}

# extracted.json date provenances that represent a deliberate published/modified
# stamp, as opposed to a founding year, a copyright line, or an incidental date
# mentioned in running text.
STRUCTURED_DATE_META = {
    "article:published_time", "article:modified_time", "datepublished",
    "datemodified", "date", "last-modified", "og:updated_time", "datecreated",
}

# A page below MIN_PAGE_WORDS carries no assessable content. Between there and
# MAYBE_SHELL_WORDS it still counts unless the client-render signals are
# overwhelming (a large hydration payload behind an empty mount, near-zero text
# ratio) -- a terse but real page is not a shell.
MIN_PAGE_WORDS = 25
MAYBE_SHELL_WORDS = 120
SHELL_HYDRATION_BYTES = 10000
SHELL_TEXT_RATIO = 0.05

DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

CATEGORY_NOUN_RE = re.compile(
    r"\b(roaster|roastery|shop|store|studio|agency|company|firm|brand|platform|"
    r"service|software|tool|toolkit|app|application|marketplace|publisher|"
    r"manufacturer|maker|supplier|provider|consultancy|consultant|charity|"
    r"nonprofit|non-profit|foundation|institute|school|university|college|clinic|"
    r"practice|restaurant|cafe|bakery|brewery|distillery|retailer|wholesaler|"
    r"boutique|magazine|newspaper|network|collective|cooperative|co-op|"
    # media, publishing and the generic nouns real About pages actually use.
    # The list above grew from the coffee-roaster fixture; vox.com's "general
    # interest news outlet" matched none of it.
    r"outlet|publication|media|news|site|website|blog|journal|broadcaster|"
    r"organization|organisation|business|group|team|project|library|archive|"
    r"lab|laboratory|initiative|programme|program|association)\b", re.I)
LOCATION_RE = re.compile(
    r"\b(based in|located in|headquartered in|operating (?:from|out of)|"
    r"serving|founded in)\b"
    r"|\b[A-Z][a-zA-Z.\-]+,\s+(?:United Kingdom|United States|USA|U\.S\.|UK|"
    r"England|Scotland|Wales|Northern Ireland|Ireland|Canada|Australia|"
    r"New Zealand|Germany|France|Spain|Italy|Netherlands|India|Singapore)\b")

CURRENCY_LANGUAGE_RE = re.compile(
    r"\b(available now|in stock now|currently available|current(?:ly)?\b|"
    r"this (?:year|season|month|quarter)|latest release|new for 20\d{2}|"
    r"register now|join us|upcoming|available today|out now)\b", re.I)
COMING_YEAR_RE = re.compile(r"\bcoming (?:soon )?in (20\d{2})\b", re.I)

TIME_SENSITIVE_PRICING_RE = re.compile(
    r"\b(as of\b|effective\b|last updated|updated on|current (?:prices?|pricing|"
    r"rates?)|price list|these prices|valid (?:from|through|until)|"
    r"prices? (?:are )?subject to change as of)\b", re.I)

SOCIAL_RE = re.compile(
    r"(linkedin\.com|twitter\.com|(?:^|//|\.)x\.com/|facebook\.com|instagram\.com|"
    r"youtube\.com|youtu\.be|github\.com|gitlab\.com|mastodon|\.social/|bsky\.app|"
    r"threads\.net|tiktok\.com|pinterest\.|wikidata\.org|crunchbase\.com|"
    r"medium\.com/@|substack\.com)", re.I)

STAT_CLAIM_RE = re.compile(
    r"(\b\d{1,3}(?:\.\d+)?\s?%(?!\s*(?:off|discount))"
    r"|\b\d+(?:\.\d+)?x\s+(?:faster|slower|more|less|better|higher|lower|cheaper)\b"
    r"|\b(?:studies|research|surveys?|the data|analysis)\s+(?:show|shows|showed|"
    r"suggest|suggests|found|indicate|indicates|prove|proves)\b"
    r"|\baccording to (?:a|an|the|our) (?:study|survey|report|analysis)\b"
    r"|\b\d{2,}(?:,\d{3})*\+?\s+(?:customers|users|companies|teams|businesses|"
    r"clients|organisations|organizations|members|subscribers)\b)", re.I)
ATTRIBUTION_RE = re.compile(
    r"(source:|sources:|according to|\[\d+\]|\(\d{4}\)|study by|report by|"
    r"\((?:ap|reuters|afp|bloomberg|pti|ani|dpa|efe|upi)\)|"
    r"published in|cite|citation|methodology|our research|our survey|our data|"
    r"we surveyed|we analysed|we analyzed|we measured)", re.I)
OWN_OPS_SUBJECT_RE = re.compile(r"\b(we|our|us)\b", re.I)
WORLD_CLAIM_NOUN_RE = re.compile(
    r"\b(users|customers|market|industry|people|respondents|consumers|shoppers|"
    r"the average|most companies|businesses)\b", re.I)


class Bundle:
    """Thin accessor over an evidence bundle directory."""

    def __init__(self, root: str):
        self.root = root
        self.manifest = self._json("MANIFEST.json") or {}
        self.run = self.manifest.get("run") or {}
        self.robots = self.manifest.get("robots") or {}
        self.sitemaps = self.manifest.get("sitemaps") or []
        self.coverage = self.manifest.get("coverage") or {}
        self.pages = self.manifest.get("pages") or []
        self.external = self.manifest.get("external")
        self.origin = self.run.get("origin") or ""
        self.site = urlparse(self.origin).netloc or self.origin
        self._extracted: dict = {}
        self._brand_phrases = None
        self._site_type = None
        # Checks that could not run for lack of the signal/tool they need. The
        # orchestrator folds this into coverage.checks_skipped so the report can
        # tell "checked, fine" from "never checked".
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

    def page_text(self, page_id: str) -> str:
        txt = (self.extracted(page_id).get("text") or {})
        return txt.get("full") or txt.get("main") or ""

    def main_word_count(self, page_id: str) -> int:
        txt = (self.extracted(page_id).get("text") or {})
        return txt.get("main_word_count") or txt.get("word_count") or 0

    def looks_like_shell(self, page_id: str) -> bool:
        wc = self.main_word_count(page_id)
        if wc < MIN_PAGE_WORDS:
            return True
        if wc >= MAYBE_SHELL_WORDS:
            return False
        ex = self.extracted(page_id)
        rs = ex.get("render_signals") or {}
        ratio = (ex.get("text") or {}).get("text_to_markup_ratio")
        return bool(
            (rs.get("app_shell_selectors") or [])
            and (rs.get("hydration_payload_bytes") or 0) >= SHELL_HYDRATION_BYTES
            and isinstance(ratio, (int, float)) and ratio < SHELL_TEXT_RATIO)

    @property
    def content_pages(self) -> list:
        """200 pages with real main content. A client-render shell's TRUST gaps
        are a rendering problem (READ-001), attributed there by supersession --
        but a terse page is still content."""
        return [p for p in self.ok_pages if not self.looks_like_shell(p["page_id"])]

    # -- reference "now" ---------------------------------------------------
    def _run_date(self):
        m = DATE_RE.search(self.run.get("started_at") or self.run.get("finished_at") or "")
        if m:
            try:
                return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                pass
        # Fall back to the newest date anywhere in the bundle, so the check still
        # has a reference point on a bundle with no run timestamp.
        newest = None
        for p in self.ok_pages:
            for iso in _page_any_dates(self.extracted(p["page_id"])):
                d = _to_date(iso)
                if d and (newest is None or d > newest):
                    newest = d
        for sm in self.sitemaps:
            for e in sm.get("entries") or []:
                d = _to_date(_iso(e.get("lastmod")))
                if d and (newest is None or d > newest):
                    newest = d
        return newest

    @property
    def now_date(self):
        return self._run_date()

    @property
    def now_year(self) -> int:
        d = self.now_date
        return d.year if d else 0

    # -- brand ----------------------------------------------------------------
    @property
    def brand_phrases(self) -> list:
        if self._brand_phrases is not None:
            return self._brand_phrases
        out = []
        for p in self.ok_pages:
            ex = self.extracted(p["page_id"])
            for block in ex.get("jsonld") or []:
                if block.get("parsed_ok"):
                    out.extend(_jsonld_org_names(block.get("value")))
            meta = ex.get("meta") or {}
            for key in ("og:site_name", "application-name"):
                if meta.get(key):
                    out.append(meta[key])
        if not out:
            seg = Counter()
            for p in self.ok_pages:
                for s in re.split(r"\s+[|–—·]\s+|\s+-\s+",
                                  self.extracted(p["page_id"]).get("title") or ""):
                    s = s.strip()
                    if len(s) >= 3:
                        seg[s] += 1
            for s, c in seg.most_common():
                if c >= max(2, len(self.ok_pages) // 3):
                    out.append(s)
                    break
        seen, res = set(), []
        for n in out:
            k = _norm(n)
            if k and k not in seen:
                seen.add(k)
                res.append(n.strip())
        self._brand_phrases = res
        return res

    @property
    def brand_display(self) -> str:
        return self.brand_phrases[0] if self.brand_phrases else (self.site or "the organisation")

    # -- site profile (site-profiles.md) ------------------------------------
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

        types_seen: set = set()
        paths = []
        has_pricing = has_docs = has_cart = False
        article_count = 0
        for p in self.ok_pages:
            path = urlparse(p.get("url") or "").path.lower()
            paths.append(path)
            if any(c in path for c in ("/cart", "/checkout", "/basket")):
                has_cart = True
            if any(pr in path for pr in ("/pricing", "/plans")):
                has_pricing = True
            if "/docs" in path or "/reference" in path or "/api" in path:
                has_docs = True
            ex = self.extracted(p["page_id"])
            for block in ex.get("jsonld") or []:
                if block.get("parsed_ok"):
                    for t in _jsonld_types(block.get("value")):
                        types_seen.add(t.lower())
            if p.get("page_type") == "article":
                article_count += 1
        if "product" in types_seen or has_cart or any(
                "/product" in x or "/shop" in x for x in paths):
            self._site_type = "ecommerce"
        elif "softwareapplication" in types_seen or (has_pricing and has_docs):
            self._site_type = "saas"
        elif "localbusiness" in types_seen or any(
                t.endswith("business") or t in ("restaurant", "store", "cafeorcoffeeshop")
                for t in types_seen):
            self._site_type = "local-business"
        elif article_count >= 2 or "newsarticle" in types_seen:
            self._site_type = "media-publisher"
        elif has_docs:
            self._site_type = "docs"
        elif len(self.ok_pages) < 20 and not has_pricing and not has_cart:
            self._site_type = "portfolio-brochure"
        else:
            self._site_type = "unknown"
        return self._site_type

    def sitemap_entries(self) -> list:
        out = []
        for sm in self.sitemaps:
            for e in sm.get("entries") or []:
                if e.get("loc"):
                    out.append((e["loc"], e.get("lastmod")))
        return out


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
# small date / text helpers
# --------------------------------------------------------------------------

def _iso(value):
    m = DATE_RE.search(value or "")
    return m.group(0) if m else None


def _to_date(iso):
    if not iso:
        return None
    m = DATE_RE.search(iso)
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def _year(value):
    m = YEAR_RE.search(str(value or ""))
    return int(m.group(0)) if m else None


def _norm(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\b(ltd|inc|llc|plc|gmbh|co|corp|corporation|limited|company)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _jsonld_org_names(node) -> list:
    ORG = {"organization", "corporation", "localbusiness", "onlinestore", "store",
           "ngo", "governmentorganization", "educationalorganization",
           "professionalservice", "brand", "restaurant", "cafeorcoffeeshop"}
    out = []
    if isinstance(node, dict):
        t = node.get("@type")
        types = [t] if isinstance(t, str) else (t if isinstance(t, list) else [])
        if any(isinstance(x, str) and x.lower() in ORG for x in types):
            if isinstance(node.get("name"), str) and node["name"].strip():
                out.append(node["name"].strip())
        for v in node.values():
            out.extend(_jsonld_org_names(v))
    elif isinstance(node, list):
        for it in node:
            out.extend(_jsonld_org_names(it))
    return out


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


def _jsonld_has_sameas(node) -> bool:
    if isinstance(node, dict):
        sa = node.get("sameAs")
        if isinstance(sa, str) and sa.strip():
            return True
        if isinstance(sa, list) and any(isinstance(x, str) and x.strip() for x in sa):
            return True
        return any(_jsonld_has_sameas(v) for v in node.values())
    if isinstance(node, list):
        return any(_jsonld_has_sameas(x) for x in node)
    return False


def _page_structured_dates(ex: dict) -> list:
    """Deliberate published/modified stamps only."""
    out = []
    for d in ex.get("dates") or []:
        src = d.get("source")
        fld = (d.get("field") or "").lower()
        iso = d.get("iso") or _iso(d.get("value"))
        if not iso:
            continue
        if src == "time-element":
            out.append(iso)
        elif src == "meta" and fld in STRUCTURED_DATE_META:
            out.append(iso)
        elif src == "jsonld" and any(k in fld for k in ("datepublished", "datemodified", "datecreated")):
            out.append(iso)
    return sorted(out)


def _page_any_dates(ex: dict) -> list:
    """Structured stamps plus visible-text dates. Excludes copyright and
    foundingDate, which say nothing about when the content was written."""
    out = list(_page_structured_dates(ex))
    for d in ex.get("dates") or []:
        if d.get("source") == "visible-text":
            iso = d.get("iso") or _iso(d.get("value"))
            if iso:
                out.append(iso)
    return sorted(out)


def _copyright_years(ex: dict) -> list:
    return sorted({y for y in (_year(d.get("value")) for d in ex.get("dates") or []
                               if d.get("source") == "copyright") if y})


def _sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]


def _page_url(p: dict) -> str:
    return p.get("url") or p.get("final_url") or ""


def _has_brand(text: str, phrases: list) -> bool:
    low = text.lower()
    return any(ph.lower() in low for ph in phrases) or any(
        tok in low for ph in phrases
        for tok in re.findall(r"[a-z][a-z0-9&.\-]{3,}", ph.lower()))


# --------------------------------------------------------------------------
# checks -- checks.yaml order
# --------------------------------------------------------------------------

def check_trust_001(b: Bundle) -> list:
    """Time-sensitive content carries no visible date. Deterministic."""
    articles = [p for p in b.ok_pages if p.get("page_type") == "article"]
    pricing = [p for p in b.ok_pages if p.get("page_type") == "pricing"]

    undated_articles = [p for p in articles
                        if not _page_structured_dates(b.extracted(p["page_id"]))]
    # Guard: evergreen pages are better without a date. A pricing page counts
    # only when it presents itself as time-sensitive ("as of", "current prices",
    # "last updated") -- otherwise "no date on the pricing page" is not a defect.
    undated_pricing = [p for p in pricing
                       if not _page_structured_dates(b.extracted(p["page_id"]))
                       and TIME_SENSITIVE_PRICING_RE.search(b.page_text(p["page_id"]))]

    hits = undated_articles + undated_pricing
    if not hits:
        return []
    considered = len(articles) + len(undated_pricing) or len(hits)
    ptype = "article" if undated_articles and not undated_pricing else (
        "pricing" if undated_pricing and not undated_articles else "article and pricing")
    urls = sorted(_page_url(p) for p in hits)
    return [finding(
        "TRUST-001",
        "Time-sensitive content carries no visible date",
        "medium",
        ("{n} of {m} {t} page(s) show no published or modified date in text, "
         "markup or metadata: {u}."
         ).format(n=len(hits), m=considered, t=ptype, u=", ".join(urls[:4])),
        ["MANIFEST.json"] + [f"pages/{p['page_id']}/extracted.json" for p in hits[:5]],
        pages=urls,
        counts={"undated": len(hits), "considered": considered},
        verification="Open {} and look for a publication or update date".format(urls[0]),
        scope="section" if len(urls) > 1 else "page",
        checked=len(b.ok_pages),
        action=act(
            "Add a machine-readable published and updated date to these pages",
            "medium",
            ["Emit <time datetime> for the publish date, and a second one for the "
             "last update, in the page template",
             "Mirror them as datePublished / dateModified in the page's JSON-LD",
             "Leave evergreen pages (about, contact, legal) undated"],
            "S",
            "A consumer choosing between sources prefers the one that can show it "
            "is current. A page with no date at all cannot compete on recency "
            "even when it is the newer source.",
            code='<p>Published <time datetime="2026-02-14">14 February 2026</time>. '
                 'Last updated <time datetime="2026-08-30">30 August 2026</time>.</p>',
            owner="content"))]


def check_trust_002(b: Bundle) -> list:
    """Content has not been updated within its expected cadence. Deterministic."""
    profile = b.site_profile
    if profile == "portfolio-brochure":
        return []  # binding guard: never report cadence staleness on these
    if profile not in STALENESS_DAYS:
        b.skip_check("TRUST-002", "cadence staleness needs a per-profile threshold; "
                     "the site profile could not be classified as one that has one "
                     "(classified as {!r})".format(profile))
        return []

    now = b.now_date
    if now is None:
        b.skip_check("TRUST-002", "no run timestamp or dated content to establish a "
                     "reference 'now' for a cadence judgement")
        return []

    dated = []
    for p in b.ok_pages:
        dated += _page_any_dates(b.extracted(p["page_id"]))
    # Guard: our sample is partial. Check the sitemap's newest lastmod too before
    # concluding the site has gone quiet.
    sm_dates = [_iso(lm) for _, lm in b.sitemap_entries() if _iso(lm)]
    newest_iso = max(dated + sm_dates) if (dated or sm_dates) else None
    if not newest_iso:
        b.skip_check("TRUST-002", "no dated content and no sitemap lastmod to judge "
                     "cadence against")
        return []
    newest = _to_date(newest_iso)
    age = (now - newest).days
    threshold = STALENESS_DAYS[profile]
    if age <= threshold:
        return []
    severity = "low" if age <= int(threshold * 1.5) else "medium"
    return [finding(
        "TRUST-002",
        "Content has not been updated within its expected cadence",
        severity,
        ("The most recent dated content found is {d} ({age} days old); the {p} "
         "threshold is {thr} days, so it is {over} days past."
         ).format(d=newest_iso, age=age, p=profile, thr=threshold, over=age - threshold),
        ["MANIFEST.json"],
        counts={"newest_days_old": age, "threshold_days": threshold},
        confidence="medium",
        verification="Check the newest post date on the blog or news index",
        scope="site-wide", checked=len(b.ok_pages),
        action=act(
            "Publish or refresh dated content on the expected cadence",
            severity,
            ["Identify the pages that should change ({} blog / changelog / "
             "catalogue)".format(profile),
             "Update them and move dateModified only where the content actually "
             "changed",
             "If the pace is deliberate, say so on the page rather than leaving it "
             "looking abandoned"],
            "M",
            "Consumers discount content that looks stale. Past the category's "
            "expected cadence, an assistant treats a fresher competing source as "
            "the safer citation.",
            owner="content"))]


def check_trust_003(b: Bundle) -> list:
    """Sitemap lastmod dates are not truthful. Deterministic. The dishonest
    signal is worse than an absent one, because it teaches consumers to ignore
    lastmod everywhere."""
    entries = [(loc.rstrip("/"), _iso(lm)) for loc, lm in b.sitemap_entries() if _iso(lm)]
    if len(entries) < 3:
        return []  # guard: need a clear pattern, not a handful

    isos = [iso for _, iso in entries]
    top_iso, top_n = Counter(isos).most_common(1)[0]
    # Guard: require most or all URLs sharing one lastmod.
    if top_n / len(entries) < 0.8:
        return []
    now = b.now_date
    top_date = _to_date(top_iso)
    # Guard: a shared OLD lastmod is not "stamped on every build". It has to be
    # recent relative to the crawl for the "changes every deploy" reading.
    if now is None or (now - top_date).days > 60:
        return []

    loc_lastmod = {loc: iso for loc, iso in entries}
    contradictions = []
    for p in b.ok_pages:
        url = _page_url(p).rstrip("/")
        if loc_lastmod.get(url) != top_iso:
            continue
        own = _page_any_dates(b.extracted(p["page_id"]))
        if not own:
            continue  # guard: only compare where the page states a date of its own
        newest_own = _to_date(max(own))
        if (top_date - newest_own).days >= 180:
            contradictions.append((_page_url(p), max(own)))
    if not contradictions:
        return []  # pattern alone, nothing contradicting it -> could be a real publish

    urls = sorted(u for u, _ in contradictions)
    example_url, example_date = sorted(contradictions)[0]
    return [finding(
        "TRUST-003",
        "Sitemap lastmod dates are not truthful",
        "medium",
        ("{n} of {m} sitemap URLs claim lastmod {top} (within {gap} days of the "
         "crawl), while {c} sampled page(s) show their own content dated as far "
         "back as {old}. Example: {u} is stamped {top} but its content is dated "
         "{ed}."
         ).format(n=top_n, m=len(entries), top=top_iso,
                  gap=(now - top_date).days, c=len(contradictions),
                  old=min(d for _, d in contradictions), u=example_url, ed=example_date),
        ["MANIFEST.json"] + [f"pages/{p['page_id']}/extracted.json"
                             for p in b.ok_pages
                             if _page_url(p) in urls][:5],
        pages=urls,
        counts={"urls_sharing_lastmod": top_n, "sitemap_urls": len(entries),
                "contradicting_pages": len(contradictions)},
        verification=("Compare the sitemap lastmod for {} with the date shown on "
                      "the page itself").format(example_url),
        scope="site-wide" if len(urls) >= 3 else ("section" if len(urls) > 1 else "page"),
        checked=len(b.ok_pages),
        action=act(
            "Derive lastmod from real content revisions, not the build date",
            "medium",
            ["Stop stamping every URL with the deploy date",
             "Set <lastmod> from the CMS updated-at or the file's git commit date",
             "It is fine for most URLs to carry old lastmod values -- that is the "
             "honest state of a site that changes slowly"],
            "S",
            "A lastmod that moves on every build carries no information, and a "
            "consumer that learns to ignore it here discounts it site-wide -- "
            "which is worse than never having published it.",
            code="<url>\n  <loc>{}/pricing</loc>\n  <lastmod>2026-08-28</lastmod>\n"
                 "</url>".format(b.origin or "https://example.com"),
            owner="engineering"))]


def check_trust_004(b: Bundle) -> list:
    """Stale year stamps contradict current content. Deterministic."""
    ref_year = b.now_year
    if not ref_year:
        return []
    stale_copyright = []
    for p in b.ok_pages:
        for y in _copyright_years(b.extracted(p["page_id"])):
            if ref_year - y >= 2:
                stale_copyright.append((_page_url(p), y))
                break
    titled_years = []
    for p in b.ok_pages:
        title = b.extracted(p["page_id"]).get("title") or ""
        y = _year(title)
        # Guard: a year in a title is correct for genuinely dated content. Only
        # flag where the page is not itself dated (so it reads as current).
        if y and ref_year - y >= 1 and not _page_structured_dates(b.extracted(p["page_id"])):
            titled_years.append((_page_url(p), y, title.strip()))

    if not stale_copyright and not titled_years:
        return []
    severity = "medium" if titled_years else "low"
    parts = []
    if stale_copyright:
        parts.append("the copyright year reads {} on {} while the crawl ran in {}".format(
            ", ".join(sorted({str(y) for _, y in stale_copyright})),
            ", ".join(sorted({u for u, _ in stale_copyright})[:3]), ref_year))
    if titled_years:
        parts.append("{} page title(s) reference {}".format(
            len(titled_years), ", ".join(sorted({str(y) for _, y, _ in titled_years}))))
    pages = sorted({u for u, _ in stale_copyright} | {u for u, _, _ in titled_years})
    return [finding(
        "TRUST-004",
        "Stale year stamps contradict current content",
        severity,
        (parts[0][0].upper() + parts[0][1:] + ("; " + parts[1] if len(parts) > 1 else "") + "."),
        ["MANIFEST.json"] + [f"pages/{p['page_id']}/extracted.json"
                             for p in b.ok_pages if _page_url(p) in pages][:5],
        pages=pages,
        counts={"stale_copyright_pages": len(stale_copyright),
                "titles_with_old_year": len(titled_years)},
        confidence="medium",
        verification="Read the footer of {}".format(pages[0]),
        scope="section" if len(pages) > 1 else "page",
        checked=len(b.ok_pages),
        action=act(
            "Render year stamps from the current date and refresh dated titles",
            severity,
            ["Render the footer copyright year from the server's current year, not "
             "a hard-coded literal",
             "For a title like '2023 guide' on a page presented as current, either "
             "date the page honestly or drop the year and refresh the body"],
            "S",
            "A visibly stale year is a cheap negative signal on its own and a "
            "corroborating one when other staleness evidence is present.",
            owner="content"))]


def check_trust_005(b: Bundle) -> list:
    """Page content states facts that are no longer true. Model-judged: the
    script flags an internal date/claim contradiction; the agent confirms it.
    Never asserts a product is discontinued."""
    ref_year = b.now_year
    out = []
    for p in b.content_pages:
        ex = b.extracted(p["page_id"])
        text = b.page_text(p["page_id"])
        reasons = []
        # Guard: a dated article is anchored by its date. A 2017 piece that is
        # clearly dated 2017 and says "this year" is internally consistent --
        # the reader and the machine both see the date -- and archived
        # reporting is not required to be rewritten. The contradiction this
        # check exists for is a page that presents itself as CURRENT (pricing,
        # product, about, home) while carrying stale time-relative claims.
        # vox.com produced three false positives on correctly dated archives.
        if p.get("page_type") == "article" and any(
                d.get("source") in ("time-element", "visible-text", "jsonld")
                for d in (ex.get("dates") or [])):
            continue
        if ref_year and CURRENCY_LANGUAGE_RE.search(text):
            # The page's date is when it was last published or modified, which
            # is the MOST RECENT structured date it declares -- not the oldest
            # year its prose happens to mention. Taking min() dated Wikipedia's
            # About page to 2001 and a blog's about-me to 2004 off "founded in"
            # sentences, then called both stale. Prefer structured sources;
            # fall back to visible text only when there is nothing better, and
            # even then take the latest.
            structured = [_year(d.get("value")) for d in ex.get("dates") or []
                          if d.get("source") in ("jsonld", "time-element", "meta")]
            structured = [y for y in structured if y]
            if structured:
                page_year = max(structured)
            else:
                visible = [_year(d.get("value")) for d in ex.get("dates") or []
                           if d.get("source") == "visible-text"]
                visible = [y for y in visible if y]
                page_year = max(visible) if visible else None
            if page_year and ref_year - page_year >= 2:
                m = CURRENCY_LANGUAGE_RE.search(text)
                reasons.append('the page is dated {} but presents "{}" as current'.format(
                    page_year, m.group(0).strip()))
        cm = COMING_YEAR_RE.search(text)
        if cm and ref_year and int(cm.group(1)) < ref_year:
            reasons.append('"{}" refers to a year that has already passed'.format(
                cm.group(0).strip()))
        if not reasons:
            continue
        excerpt = ""
        sm = CURRENCY_LANGUAGE_RE.search(text) or COMING_YEAR_RE.search(text)
        if sm:
            start = max(0, sm.start() - 100)
            excerpt = re.sub(r"\s+", " ", text[start:sm.end() + 100]).strip()
        out.append(finding(
            "TRUST-005",
            "Page content states facts that are no longer true",
            "medium",
            ("{u} presents time-sensitive information as current when it may not "
             "be: {r}. Excerpt: \"{ex}\""
             ).format(u=_page_url(p), r="; ".join(reasons), ex=excerpt[:200]),
            [f"pages/{p['page_id']}/extracted.json"],
            pages=[_page_url(p)],
            counts={"signals": len(reasons)},
            confidence="low",
            determinism="model-judged",
            verification=("Check whether the offering or event this passage "
                          "describes is still current, then update the date"),
            excerpt=excerpt,
            scope="page", checked=len(b.content_pages),
            action=act(
                "Re-confirm the claim and stamp when it was last checked",
                "medium",
                ["Verify the offering, version or event referenced is still current",
                 "State the current fact, or add an explicit 'as of <date>'",
                 "Move the page's visible date forward to when you confirmed it"],
                "S",
                "Content that asserts a stale fact as current is discounted once a "
                "consumer catches one error, and the doubt spreads to the rest of "
                "the page.",
                owner="content")))
    return out


def _skip_offsite(b: Bundle, check_id: str) -> list:
    b.skip_check(check_id, OFFSITE_CHECKS[check_id] +
                 " requires a web search or fetch tool; none is available to this "
                 "script and the bundle carries no external/ block. Absence of a "
                 "lookup is not evidence of absence.")
    return []


def check_trust_006(b: Bundle) -> list:
    """Key claims appear nowhere else on the web. Off-site -> skipped here."""
    return _skip_offsite(b, "TRUST-006")


def check_trust_007(b: Bundle) -> list:
    """The brand name collides with better-known entities. Off-site -> skipped."""
    return _skip_offsite(b, "TRUST-007")


def check_trust_008(b: Bundle) -> list:
    """No sentence identifies the organization unambiguously. Model-judged,
    on-site (runs even when the off-site checks are skipped)."""
    phrases = b.brand_phrases
    if not phrases or not b.content_pages:
        b.skip_check("TRUST-008", "could not run: no brand name resolved from the "
                     "bundle, or no page carries assessable content")
        return []
    for p in b.content_pages:
        for sent in _sentences(b.page_text(p["page_id"])):
            if (_has_brand(sent, phrases) and CATEGORY_NOUN_RE.search(sent)
                    and LOCATION_RE.search(sent)):
                return []  # an unambiguous identity sentence exists
    # Guard: an Organization's JSON-LD `description` is an identity sentence in
    # the one place a machine reads first. vox.com carries "Vox is a general
    # interest news outlet founded in 2014 with a focus on explanatory
    # journalism" in NewsMediaOrganization markup on its home page; checking
    # only visible prose called that site unidentified.
    for p in b.content_pages:
        for block in (b.extracted(p["page_id"]).get("jsonld") or []):
            val = block.get("value") if isinstance(block, dict) else None
            if not isinstance(val, dict):
                continue
            if "Organization" not in str(val.get("@type", "")):
                continue
            desc = str(val.get("description") or "")
            if _has_brand(desc, phrases) and CATEGORY_NOUN_RE.search(desc):
                return []  # identity stated in machine-readable markup
    home = next((p for p in b.content_pages if p.get("page_type") == "home"),
               b.content_pages[0])
    excerpt = re.sub(r"\s+", " ", b.page_text(home["page_id"])[:220]).strip()
    # Guard (agent): overlaps QUOTE-002. That check asks whether the site says
    # what it does; this one asks whether it does so in a way that distinguishes
    # it from similarly-named entities. Report one or the other, not both.
    return [finding(
        "TRUST-008",
        "No sentence identifies the organization unambiguously",
        "medium",
        ("No sampled page pairs the brand name with a category and a location in "
         "one sentence. The home page opens: \"{ex}\""
         ).format(ex=excerpt),
        ["MANIFEST.json", f"pages/{home['page_id']}/extracted.json"],
        counts={"content_pages_checked": len(b.content_pages)},
        confidence="low",
        determinism="model-judged",
        verification=("Search the site for a sentence naming what the company is "
                      "and where it is based"),
        excerpt=excerpt,
        scope="site-wide", checked=len(b.content_pages),
        action=act(
            "Add one sentence pairing the brand with its category and location",
            "medium",
            ["Write '{} is a <specific category> based in <city, country>, "
             "<one distinguishing fact>.'".format(b.brand_display),
             "Place it in the first screen of the home page and in the meta "
             "description",
             "Mirror the location in Organization JSON-LD (address) and sameAs"],
            "S",
            "When several entities share a name, the resolver binds to whichever "
            "one gives it an explicit category and place. Without that sentence "
            "the brand is indistinguishable from its namesakes.",
            owner="content"))]


def check_trust_009(b: Bundle) -> list:
    """The brand is absent from the sources machines check. Off-site -> skipped."""
    return _skip_offsite(b, "TRUST-009")


def check_trust_010(b: Bundle) -> list:
    """Name, address or phone details are inconsistent. Deterministic on-site
    half; the off-site comparison needs a tool."""
    if b.site_profile not in ("local-business", "ecommerce", "nonprofit-gov"):
        b.skip_check("TRUST-010", "NAP consistency applies to local-business, "
                     "ecommerce and nonprofit-gov sites; this site's profile is "
                     "{!r}".format(b.site_profile))
        return []

    phones, postcodes = {}, {}
    for p in b.ok_pages:
        text = b.page_text(p["page_id"])
        for m in re.findall(r"\+?\d[\d()\-\s]{7,}\d", text):
            key = re.sub(r"\D", "", m)[-10:]
            phones.setdefault(key, set()).add(_page_url(p))
        for m in re.findall(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b", text):
            postcodes.setdefault(re.sub(r"\s", "", m).upper(), set()).add(_page_url(p))

    problems = []
    if len(phones) > 1:
        problems.append(("phone number", sorted(phones)))
    if len(postcodes) > 1:
        problems.append(("postcode", sorted(postcodes)))
    if not problems:
        b.skip_check("TRUST-010", "off-site half only: on-site name/address/phone "
                     "details are internally consistent; comparison with external "
                     "listings needs a web lookup")
        return []

    field, variants = problems[0]
    return [finding(
        "TRUST-010",
        "Name, address or phone details are inconsistent",
        "medium",
        ("{f} appears as {v} across {n} sampled pages."
         ).format(f=field, v=", ".join(variants[:4]), n=len(b.ok_pages)),
        ["MANIFEST.json"],
        counts={"variants": len(variants)},
        confidence="medium",
        verification="Compare the address in the footer with the one on the contact page",
        scope="site-wide", checked=len(b.ok_pages),
        action=act(
            "Publish one canonical name, address and phone and use it everywhere",
            "medium",
            ["Pick the canonical NAP and put it in the footer template",
             "Match it exactly in Organization / LocalBusiness JSON-LD",
             "Update every directory and map listing to the same values"],
            "S",
            "A machine cross-checking the brand against directory data treats "
            "mismatched contact details as two entities, or as a sign the record "
            "is unmaintained.",
            owner="content"))]


def check_trust_011(b: Bundle) -> list:
    """Official profiles are not linked from the site. Deterministic on-site."""
    if not b.content_pages:
        b.skip_check("TRUST-011", "no page carries assessable content to check for "
                     "profile links")
        return []
    linked = same_as = False
    for p in b.ok_pages:
        ex = b.extracted(p["page_id"])
        for lk in ex.get("links") or []:
            if SOCIAL_RE.search(lk.get("href") or ""):
                linked = True
        for block in ex.get("jsonld") or []:
            if block.get("parsed_ok") and _jsonld_has_sameas(block.get("value")):
                same_as = True
    if linked or same_as:
        return []

    # Guard: "no profiles at all" is a proactive recommendation, not a defect.
    # We cannot tell from the bundle whether profiles exist and are merely
    # unlinked -- that needs a lookup -- so this stays low and says so.
    home = b.content_pages[0]
    return [finding(
        "TRUST-011",
        "Official profiles are not linked from the site",
        "low",
        ("Across {n} sampled pages the site links no LinkedIn, Wikidata, GitHub "
         "or other official profile and declares no sameAs entries in JSON-LD."
         ).format(n=len(b.ok_pages)),
        ["MANIFEST.json", f"pages/{home['page_id']}/extracted.json"],
        counts={"pages_checked": len(b.ok_pages)},
        confidence="medium",
        verification="Look for social or profile links in the footer of {}".format(
            _page_url(home)),
        scope="site-wide", checked=len(b.ok_pages),
        action=act(
            "Link the official profiles that exist and declare them in sameAs",
            "low",
            ["Add footer links to the organisation's real LinkedIn, Wikidata and "
             "any industry-directory pages",
             "List the same URLs in Organization JSON-LD sameAs",
             "If no profiles exist at all, treat creating them as optional -- but "
             "still declare any register or directory entry that does"],
            "S",
            "sameAs and profile links give an entity resolver a graph to walk, "
            "which is how it confirms the site and the off-site records describe "
            "one organisation.",
            owner="content"))]


def check_trust_012(b: Bundle) -> list:
    """Off-site descriptions contradict the site's positioning. Off-site -> skipped."""
    return _skip_offsite(b, "TRUST-012")


def check_trust_013(b: Bundle) -> list:
    """No independent coverage or reviews exist. Off-site -> skipped."""
    return _skip_offsite(b, "TRUST-013")


def check_trust_014(b: Bundle) -> list:
    """Outbound links point to dead or moved sources. Deterministic, but only
    over links the collector actually tested."""
    origin_host = urlparse(b.origin).netloc.lower()
    tested_bad = []
    for s in b.coverage.get("skipped") or []:
        url = s.get("url", "")
        host = urlparse(url).netloc.lower()
        external = host and host != origin_host and not host.endswith("." + origin_host)
        if external and s.get("reason") in ("http-error", "timeout"):
            tested_bad.append(url)
    if not tested_bad:
        # Guard: the collector does not fetch external URLs by default, so there
        # is nothing tested to report. Record that, do not infer breakage from
        # URL shape.
        b.skip_check("TRUST-014", "outbound link health was not tested: the "
                     "collector does not fetch external URLs")
        return []
    return [finding(
        "TRUST-014",
        "Outbound links point to dead or moved sources",
        "low",
        ("{n} outbound link(s) the collector fetched returned an error: {ex}."
         ).format(n=len(tested_bad), ex=", ".join(sorted(tested_bad)[:5])),
        ["coverage.json", "MANIFEST.json"],
        counts={"broken_outbound": len(tested_bad)},
        confidence="medium",
        verification="curl -sI {}".format(sorted(tested_bad)[0]),
        scope="section", checked=len(b.ok_pages),
        action=act(
            "Repair or replace the dead outbound citations",
            "low",
            ["Update links whose target moved to the new URL",
             "Replace a permanently gone source, or remove the claim it supported",
             "Verify a 403 in a browser before treating the link as dead"],
            "S",
            "Links that back factual claims are themselves a trust signal, and a "
            "dead one weakens the claim it was meant to support.",
            owner="content"))]


def check_trust_015(b: Bundle) -> list:
    """Factual claims carry no attribution. Model-judged."""
    if not b.content_pages:
        b.skip_check("TRUST-015", "no page carries assessable content to check for "
                     "unattributed claims")
        return []
    out = []
    for p in b.content_pages:
        # Guard: an index page lists titles; it does not make claims. danluu.com's
        # home page was reported for "95%-ile isn't that good" -- a post title in
        # its archive list. Claims live on the pages themselves.
        if p.get("page_type") in ("home", "category"):
            continue
        flagged = []
        for sent in _sentences((b.extracted(p["page_id"]).get("text") or {}).get("main") or ""):
            # Guard: a "sentence" of 60+ words with no terminator is a nav list,
            # a table or a post index, not a claim. Wikipedia's front page and
            # danluu.com's post list each arrived as one such run containing a
            # percentage somewhere, and the excerpt showed its unrelated start.
            if len(sent.split()) > 60:
                continue
            if not STAT_CLAIM_RE.search(sent):
                continue
            if ATTRIBUTION_RE.search(sent):
                continue
            # Guard: a claim about the company's own operations needs no external
            # source. Only a claim about the wider world does.
            if OWN_OPS_SUBJECT_RE.search(sent) and not WORLD_CLAIM_NOUN_RE.search(sent):
                continue
            flagged.append(sent.strip())
        if not flagged:
            continue
        excerpt = re.sub(r"\s+", " ", flagged[0])[:200]
        out.append(finding(
            "TRUST-015",
            "Factual claims carry no attribution",
            "low",
            ("{u} states {n} statistic or research claim(s) with no source, author "
             "or methodology. Example: \"{ex}\""
             ).format(u=_page_url(p), n=len(flagged), ex=excerpt),
            [f"pages/{p['page_id']}/extracted.json"],
            pages=[_page_url(p)],
            counts={"unattributed_claims": len(flagged)},
            confidence="low",
            determinism="model-judged",
            verification="Read {} and look for a source next to the claim".format(_page_url(p)),
            excerpt=excerpt,
            scope="page", checked=len(b.content_pages),
            action=act(
                "Put a source next to every claim about the wider world",
                "low",
                ["Link the study, name the customer, or add a short methodology "
                 "note beside each statistic",
                 "Claims about your own operations do not need an external source"],
                "S",
                "An unsourced statistic is discounted by a reader deciding what to "
                "repeat; a cited one can be carried into an answer with the "
                "citation attached.",
                owner="content")))
    return out


CHECKS = [
    check_trust_001, check_trust_002, check_trust_003, check_trust_004,
    check_trust_005, check_trust_006, check_trust_007, check_trust_008,
    check_trust_009, check_trust_010, check_trust_011, check_trust_012,
    check_trust_013, check_trust_014, check_trust_015,
]

# Every TRUST check in references/checks.yaml is implemented above. The five
# purely off-site checks record themselves as skipped when (as here) no web
# search or fetch tool is available.
NOT_YET_IMPLEMENTED: list = []


def proactive(b: Bundle, findings: list) -> list:
    """Improvements worth making where no defect was found. Each cites something
    observed in the bundle."""
    out = []
    fired = {f.get("check_id") for f in findings}
    phrases = b.brand_phrases
    content = b.content_pages

    # TRUST-P01 -- one disambiguating sentence. Only when TRUST-008 did not fire
    # and no page already has the brand+category+location sentence.
    if content and "TRUST-008" not in fired:
        has_identity = any(
            _has_brand(s, phrases) and CATEGORY_NOUN_RE.search(s) and LOCATION_RE.search(s)
            for p in content for s in _sentences(b.page_text(p["page_id"])))
        if phrases and not has_identity:
            out.append({
                "id": "P-000",  # TRUST-P01
                "title": "Add one sentence pairing the brand with its category and location",
                "category": CATEGORY, "mechanism": MECHANISM,
                "rationale": ("No sampled page states '{} is a <category> based in "
                              "<place>' in a single sentence. That one line is the "
                              "cheapest identity anchor a machine resolving an "
                              "ambiguous name can bind to."
                              ).format(b.brand_display),
                "suggested_action": act(
                    "Add a brand + category + location identity sentence",
                    "low",
                    ["Write it as the first paragraph of the home page",
                     "Repeat it verbatim in the meta description"],
                    "S",
                    "An explicit category and place is what lets an entity "
                    "resolver tell this organisation from its namesakes.",
                    owner="content"),
            })

    # TRUST-P03 -- show an update date where content is current but undated.
    undated = [p for p in content
               if not _page_structured_dates(b.extracted(p["page_id"]))
               and p.get("page_type") not in ("legal", "contact", "about")]
    if content and "TRUST-001" not in fired and "TRUST-002" not in fired and len(undated) >= 2:
        out.append({
            "id": "P-000",  # TRUST-P03
            "title": "Show an honest update date on pages that change",
            "category": CATEGORY, "mechanism": MECHANISM,
            "rationale": ("{n} of {m} sampled content pages carry no visible "
                          "published or updated date, though the site's content "
                          "reads as current. A truthful update date lets a "
                          "consumer prefer the page over an older competing source."
                          ).format(n=len(undated), m=len(content)),
            "suggested_action": act(
                "Add a visible, machine-readable update date to pages that change",
                "low",
                ["Emit <time datetime> plus dateModified in the page template",
                 "Move it only when the content actually changes, so it stays "
                 "trustworthy"],
                "S",
                "Recency only helps while the date is honest; a real one earns the "
                "preference a stale competitor cannot.",
                owner="content"),
        })

    # TRUST-P02 -- seed citable facts. Only meaningful once corroboration has
    # actually been checked; here it is skipped, so this stays a note tied to
    # that skip rather than a claim about the footprint.
    if any(s["check_id"] == "TRUST-006" for s in b.checks_skipped):
        out.append({
            "id": "P-000",  # TRUST-P02
            "title": "Publish facts worth citing so independent sources repeat them",
            "category": CATEGORY, "mechanism": MECHANISM,
            "rationale": ("Off-site corroboration was not checked in this run (no "
                          "search tool), but agreement across independent sources "
                          "is what makes a claim repeatable. Original data or "
                          "benchmarks give other sites a reason to state {}'s "
                          "facts in their own words."
                          ).format(b.brand_display),
            "suggested_action": act(
                "Publish original data, benchmarks or a facts page others can cite",
                "low",
                ["Pick the load-bearing facts (founding year, scale, location) and "
                 "state them identically on-site and in structured data",
                 "Publish something original -- a survey, a benchmark, a "
                 "methodology page -- that others have reason to reference"],
                "M",
                "Corroboration the site does not control is the durable kind, and "
                "it only forms around facts worth restating.",
                owner="marketing"),
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
    ap.add_argument("--skip-offsite", action="store_true",
                    help="explicitly skip the off-site corroboration checks "
                         "(they are skipped anyway when no lookup tool is present)")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.bundle):
        print(f"error: {args.bundle!r} is not a bundle directory", file=sys.stderr)
        return 2

    b = Bundle(args.bundle)
    if not b.manifest:
        print(f"error: no readable MANIFEST.json in {args.bundle!r}", file=sys.stderr)
        return 2

    findings: list = []
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
            # One broken check must never lose the others.
            print(f"warning: {check.__name__} failed: {type(exc).__name__}: {exc}",
                  file=sys.stderr)

    # Drop any candidate whose refs do not resolve (false-positive gate 2).
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

    result = {"skill": "freshness-corroboration-audit", "mechanism": MECHANISM,
              "bundle": args.bundle, "findings": kept,
              "proactive_recommendations": proactive_recs,
              "checks_skipped": b.checks_skipped,
              "checks_not_implemented": NOT_YET_IMPLEMENTED}

    if cut_by_deadline:
        result["checks_cut_by_deadline"] = cut_by_deadline
        print(f"warning: deadline reached; {len(cut_by_deadline)} check(s) not run: "
              f"{', '.join(cut_by_deadline)}", file=sys.stderr)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out and not args.stdout:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
        print(f"{len(kept)} TRUST candidates -> {args.out}", file=sys.stderr)
        for f in kept:
            print(f"  {f['check_id']:11} {f['severity']:8} {f['title']}", file=sys.stderr)
        for s in b.checks_skipped:
            print(f"  skipped {s['check_id']}: {s['reason'][:70]}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
