#!/usr/bin/env python3
"""QUOTE checks: can a machine lift a clear, self-contained fact out of this page?

Standard library only -- ships inside the submission and must run on a bare
Python 3.9+ install.

Reads a completed evidence bundle and emits candidate findings against
../audit-orchestrator/references/finding.schema.json. Performs no network I/O:
every result is a pure function of the bundle, so the same bundle always yields
byte-identical findings.

Structure mirrors ../crawl-access-audit/scripts/check_access.py (the reference
implementation):

  * load the bundle once, into a small accessor object
  * one function per check, named check_quote_<nnn>, returning zero or more
    candidates
  * every candidate cites artifact_refs that actually exist in the bundle
  * false-positive guards live next to the logic that would trip them, as code
    where mechanical and as an explicit comment where they need agent judgment
    at report time
  * base severity only -- the orchestrator owns scope and confidence modifiers
  * deterministic checks compute their verdict here; model-judged checks emit
    the precomputed signals with determinism "model-judged" and are finished by
    the agent following SKILL.md. A model-judged candidate is never "critical".

Usage:
    python check_answerability.py <bundle> --out quote-candidates.json
    python check_answerability.py <bundle> --stdout
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from urllib.parse import urlparse

MECHANISM = "quote"
CATEGORY = "discoverability"

# A chunk shorter than this legitimately lacks a subject -- list items and table
# rows lean on the structure around them (QUOTE-001 guard, binding).
MIN_CHUNK_WORDS = 25
# Below this a page has no real content to assess; the root cause is rendering,
# and READ-001 supersession handles it (QUOTE-001 guard, binding). The gate is
# graduated the way check_render.py's is: unambiguous below MIN_PAGE_WORDS, and
# up to MAYBE_SHELL_WORDS only when the client-render signals are overwhelming
# (a big hydration payload behind an empty mount and near-zero text ratio). A
# page of nav-and-footer chrome lands near 60 words, so a hard 50 both missed
# real shells and, occasionally, excluded a terse-but-real page.
MIN_PAGE_WORDS = 50
MAYBE_SHELL_WORDS = 120
SHELL_HYDRATION_BYTES = 10000
SHELL_TEXT_RATIO = 0.05
# A lone stray figure is noise; several unbound figures in one chunk is a real
# "what does 29 refer to" problem.
BARE_NUMBER_TRIGGER = 3

STOPWORDS = {
    "the", "and", "for", "with", "our", "your", "you", "that", "this", "from",
    "are", "was", "how", "why", "what", "where", "when", "who", "new", "page",
    "home", "about", "contact", "faq", "faqs", "pricing", "plans", "welcome",
    "index", "site", "official", "best", "top", "learn", "more", "info",
    "information", "company", "inc", "ltd", "llc", "plc", "gmbh", "corp",
    "limited", "menu", "search", "toggle", "navigation", "skip",
}

# Titles that say nothing about what the page answers. "Home", "About" and
# "Contact" are conventional and understood -- they are deliberately absent here
# (QUOTE-011 guard, binding).
GENERIC_TITLES = {
    "home", "welcome", "untitled", "untitled document", "page", "index",
    "new page", "document", "start", "main", "default", "webpage",
}

ORG_JSONLD_TYPES = {
    "organization", "corporation", "localbusiness", "onlinestore", "store",
    "ngo", "governmentorganization", "educationalorganization",
    "professionalservice", "ltdifpo", "brand", "newsmediaorganization",
    "medicalorganization", "sportsorganization", "researchorganization",
    "onlinebusiness", "consortium", "library", "airline", "website",
}
# Organizations named inside these properties are other organizations: the
# parent, the subsidiaries, the sponsor. nytimes.com lists The Athletic,
# Wirecutter and NYT Cooking as subOrganization and was named "The Athletic".
ORG_JSONLD_OTHER_PARTY = {
    "suborganization", "parentorganization", "memberof", "sponsor", "funder",
    "affiliation", "worksfor", "seller", "provider", "manufacturer",
}

# Fact classes a buyer asks about (QUOTE-003). Each maps to a detector over the
# combined visible text / links / forms of the sampled content pages.
PRICE_RE = re.compile(
    r"(?:[$£€₹]\s?\d|\b(?:GBP|USD|EUR|AUD|CAD)\s?\d|\bfrom\s+\d[\d,]*\b"
    r"|\b\d[\d,]*\s?(?:/|per\s)\s?(?:mo|month|year|yr|seat|user|day)\b"
    r"|\bfree\b|\bno\s+cost\b)", re.I)
PHONE_RE = re.compile(r"(?:\btel:|\+?\d[\d\s().-]{7,}\d)")
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
POSTCODE_RE = re.compile(
    r"\b(?:[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}"          # UK
    r"|\d{5}(?:-\d{4})?"                                 # US ZIP
    r"|\d{1,4}\s+[A-Z][a-z]+\s+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Way|Blvd))\b")
HOURS_RE = re.compile(
    r"\b(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*\b[^.]{0,40}?"
    r"\b(?:\d{1,2}(?::\d{2})?\s?(?:am|pm)|\d{1,2}:\d{2})\b", re.I)
DELIVERY_RE = re.compile(
    r"\b(?:delivery|shipping|ships?\s+to|dispatch|next[-\s]day|free\s+returns?)\b", re.I)

# Spec-like measured values (QUOTE-009).
SPEC_VALUE_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s?(?:GB|TB|MB|KB|mm|cm|kg|mg|ml|Hz|kHz|GHz|MHz|W|kW|V|mAh|"
    r"Wh|px|dpi|ppi|fps|nm|bit|cores?|inch|in)\b")

# Camel/StudlyCase proprietary-looking product tokens (QUOTE-008).
PROPRIETARY_RE = re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+){1,3}(?:™|®)?\b")
CATEGORY_NOUN_RE = re.compile(
    r"\b(platform|service|software|tool|toolkit|app|application|product|suite|"
    r"agency|studio|company|firm|system|framework|marketplace|network|library|"
    r"plugin|extension|dashboard|api)\b", re.I)

SUMMARY_HINT_RE = re.compile(
    r"\b(summary|tl;?dr|key\s+takeaways?|in\s+short|at\s+a\s+glance|overview)\b", re.I)

TITLE_SPLIT_RE = re.compile(r"\s+[|–—·•]\s+|\s+-\s+|(?<=\S):\s+")
# Title text that names nothing. who.int's <title> is "Home" on 10 of 20
# pages; rfc-editor.org's is "Expand sidebar" on all 20 -- a button label.
GENERIC_NAME_RE = re.compile(
    r"^(home|homepage|home page|index|welcome|untitled|default|document|page|"
    r"loading|menu|news|blog|notes|archive|archives|expand sidebar|skip to "
    r"(?:main )?content|login|log in|sign in)$", re.I)


def _host_label(host: str) -> str:
    """The registrable label a reader would call the site: 'openbsd' for
    www.openbsd.org, 'tuhs' for www.tuhs.org, '9p' for 9p.io."""
    parts = [x for x in (host or "").lower().split(".") if x]
    if parts and parts[0] == "www":
        parts = parts[1:]
    if len(parts) >= 3 and parts[-2] in ("co", "com", "org", "net", "ac", "gov", "edu"):
        parts = parts[:-1]
    return parts[-2] if len(parts) >= 2 else (parts[0] if parts else "")


def _unspace_letters(name: str) -> str:
    """'T E X T F I L E S' -> 'TEXTFILES'."""
    toks = name.split()
    if len(toks) >= 4 and all(len(t) == 1 for t in toks):
        return "".join(toks)
    return name
SENT_VERB = (r"(?:is|are|was|were|provides?|offers?|helps?|builds?|makes?|"
             r"delivers?|sells?|operates?|creates?|designs?|specialise|"
             r"specialize|manufactures?|runs?|powers?)")


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
        self.origin = self.run.get("origin") or ""
        self.site = urlparse(self.origin).netloc or self.origin
        self._extracted: dict = {}
        self._chunks: dict = {}
        self._raw: dict = {}
        self._brand_phrases = None
        self._brand_terms = None
        # Checks that could not run for lack of the signal they need -- recorded
        # so the report can tell "checked and fine" from "never checked"
        # (false-positive-gates.md: that distinction is most of what makes an
        # audit trustworthy). The orchestrator folds this into
        # coverage.checks_skipped.
        self.checks_skipped: list = []

    def skip_check(self, check_id: str, reason: str) -> None:
        entry = {"check_id": check_id, "reason": reason}
        if entry not in self.checks_skipped:
            self.checks_skipped.append(entry)

    def _json(self, rel: str):
        path = os.path.join(self.root, rel.replace("/", os.sep))
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def exists(self, rel: str) -> bool:
        return os.path.exists(os.path.join(self.root, rel.replace("/", os.sep)))

    @property
    def ok_pages(self) -> list:
        """Pages that were actually fetched with a 200. Non-200 entries stay in
        the manifest for other mechanisms but carry no content to assess here."""
        return [p for p in self.pages if p.get("status") == 200]

    def extracted(self, page_id: str) -> dict:
        if page_id not in self._extracted:
            self._extracted[page_id] = self._json(f"pages/{page_id}/extracted.json") or {}
        return self._extracted[page_id]

    def chunks(self, page_id: str) -> list:
        if page_id not in self._chunks:
            doc = self._json(f"pages/{page_id}/chunks.json") or {}
            self._chunks[page_id] = doc.get("chunks") or []
        return self._chunks[page_id]

    def raw_html(self, page_id: str) -> str:
        if page_id not in self._raw:
            path = os.path.join(self.root, "pages", page_id, "raw.html")
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    self._raw[page_id] = fh.read()
            except FileNotFoundError:
                self._raw[page_id] = ""
        return self._raw[page_id]

    # -- derived --------------------------------------------------------------
    def main_word_count(self, page_id: str) -> int:
        txt = (self.extracted(page_id).get("text") or {})
        return txt.get("main_word_count") or txt.get("word_count") or 0

    def looks_like_shell(self, page_id: str) -> bool:
        """True when the page carries no assessable content: either almost no
        main text, or a middling amount of it behind unmistakable client-render
        signals (a large hydration payload, an empty framework mount, a
        near-zero text-to-markup ratio). Kept deliberately conservative -- a
        long server-rendered page is never a shell however much JS it ships."""
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
        """200 pages with enough main-content text to be worth assessing. Pages
        that look like a client-render shell are almost always a rendering
        problem (READ-001); supersession attributes them to that root cause,
        not to QUOTE."""
        return [p for p in self.ok_pages
                if not self.looks_like_shell(p["page_id"])
                and self.chunks(p["page_id"])]

    def page_text(self, page_id: str) -> str:
        txt = (self.extracted(page_id).get("text") or {})
        return txt.get("full") or txt.get("main") or ""

    @property
    def brand_phrases(self) -> list:
        """Full brand / organisation strings, most authoritative first.

        schema.org Organization names and og:site_name are authoritative: a
        single occurrence is enough, because the site is declaring its own name.
        The recurring <title> segment is only a fallback for sites that publish
        neither -- it depends on titles being 'Page | Brand' shaped, which many
        are not."""
        if self._brand_phrases is not None:
            return self._brand_phrases
        # Count every candidate by the number of PAGES that carry it. A name
        # the site declares (Organization JSON-LD, og:site_name) is weighted
        # above a title segment, but it still has to recur: one page's
        # og:site_name must never outvote seventeen consistent titles. That
        # exact failure named curl.se's brand "GitHub" from a single bug-tracker
        # page that redirected there.
        declared: Counter = Counter()
        titled: Counter = Counter()
        on_home: set = set()
        for p in self.ok_pages:
            ex = self.extracted(p["page_id"])
            page_names: set = set()
            title_segs: set = set()
            for block in ex.get("jsonld") or []:
                if block.get("parsed_ok"):
                    page_names |= {n.strip() for n in _jsonld_org_names(block.get("value")) if n}
            meta = ex.get("meta") or {}
            for key in ("og:site_name", "application-name", "apple-mobile-web-app-title"):
                if meta.get(key):
                    page_names.add(str(meta[key]).strip())
            for n in page_names:
                declared[n] += 1
            for seg in TITLE_SPLIT_RE.split(ex.get("title") or ""):
                seg = _unspace_letters(seg.strip())
                if len(seg) >= 3 and not GENERIC_NAME_RE.match(seg):
                    titled[seg] += 1
                    title_segs.add(seg)
            if p.get("page_type") == "home":
                on_home |= page_names | title_segs

        # "Stripe logo" is what 18 of stripe.com's <title>s literally say --
        # the logo's alt text leaking into the title. Strip that class of
        # suffix so the candidate merges with the declared name.
        def _clean(name: str) -> str:
            return re.sub(r"\s+(logo|icon|homepage|home page|home|official site)$",
                          "", name.strip(), flags=re.I).strip() or name.strip()
        declared = Counter({_clean(k): v for k, v in declared.items()
                            if not GENERIC_NAME_RE.match(_clean(k))})
        titled = Counter({_clean(k): v for k, v in titled.items()})
        on_home = {_clean(k) for k in on_home}

        n_pages = max(1, len(self.ok_pages))
        label = _host_label(self.site)
        scored: dict = {}
        for name, c in declared.items():
            scored[name] = scored.get(name, 0.0) + c * 2.0   # self-declared: weight 2
        for name, c in titled.items():
            if c >= max(2, n_pages // 3) or name in on_home:
                scored[name] = scored.get(name, 0.0) + c * 1.0
        # Two anchors outrank recurrence. The home page is the site's own
        # statement of identity: nytimes.com sampled seven Athletic pages, each
        # declaring og:site_name "The Athletic", and the home title lost 14 to
        # 4. And a name that contains the host label ("OpenBSD" on openbsd.org,
        # "TEXTFILES" on textfiles.com) is the name a reader would use.
        for name in list(scored):
            if name in on_home:
                scored[name] += n_pages
            if label and len(label) >= 3 and label in _norm_name(name).replace(" ", ""):
                scored[name] += n_pages
        ranked = sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))

        seen, res = set(), []
        for name, _score in ranked:
            key = _norm_name(name)
            if key and key not in seen:
                seen.add(key)
                res.append(name)
        self._brand_phrases = res
        return res

    @property
    def brand_terms(self) -> set:
        """Lowercased subject vocabulary: tokens from the brand phrases (always),
        plus capitalised tokens that recur across a strong majority of page
        titles and headings. Used to decide whether a chunk (or its
        heading_path) names its own subject.

        This is not a re-chunking and not a re-derivation of the chunk signals --
        it is the 'weigh heading_path' step the QUOTE-001 guard makes binding."""
        if self._brand_terms is not None:
            return self._brand_terms
        terms: set = set()
        for phrase in self.brand_phrases:
            for tok in re.findall(r"[a-z][a-z0-9&.\-]{2,}", phrase.lower()):
                if tok not in STOPWORDS:
                    terms.add(tok)
        per_page = []
        for p in self.ok_pages:
            ex = self.extracted(p["page_id"])
            toks = set()
            sources = [ex.get("title") or ""]
            sources += [h.get("text", "") for h in (ex.get("headings") or [])]
            for src in sources:
                for tok in re.findall(r"\b[A-Z][A-Za-z0-9&.\-]{2,}\b", src):
                    tl = tok.lower()
                    if tl not in STOPWORDS:
                        toks.add(tl)
            per_page.append(toks)
        counter: Counter = Counter()
        for toks in per_page:
            counter.update(toks)
        n = len(per_page)
        # ceil(0.6 * n) without importing math; never below 2.
        threshold = max(2, -(-3 * n // 5))
        terms |= {t for t, c in counter.items() if c >= threshold}
        self._brand_terms = terms
        return terms

    @property
    def brand_display(self) -> str:
        if self.brand_phrases:
            return self.brand_phrases[0]
        # No declared or recurring name. Prefer the host label as the titles
        # spell it ("OpenBSD" from "OpenBSD: Artwork"); never an alphabetical
        # pair of recurring capitalised words ("Notes Openbsd", "Archive
        # Archives", "Plan").
        label = _host_label(self.site)
        if label and label in self.brand_terms:
            for p in self.ok_pages:
                ex = self.extracted(p["page_id"])
                for src in [ex.get("title") or ""] + [h.get("text", "") for h in (ex.get("headings") or [])]:
                    m = re.search(r"\b" + re.escape(label) + r"\b", src, re.I)
                    if m:
                        return m.group(0)
        return self.site or "the organisation"

    def sitemap_locs(self) -> list:
        locs = []
        for sm in self.sitemaps:
            for entry in sm.get("entries") or []:
                if entry.get("loc"):
                    locs.append(entry["loc"])
        return locs


# --------------------------------------------------------------------------
# helpers (finding() and act() are copied verbatim from the reference impl)
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


def _norm_name(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\b(ltd|inc|llc|plc|gmbh|co|corp|corporation|limited|company)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _jsonld_org_names(node) -> list:
    out = []
    if isinstance(node, dict):
        t = node.get("@type")
        types = [t] if isinstance(t, str) else (t if isinstance(t, list) else [])
        if any(isinstance(x, str) and x.lower() in ORG_JSONLD_TYPES for x in types):
            name = node.get("name")
            if isinstance(name, str) and name.strip():
                out.append(name.strip())
        for k, v in node.items():
            if str(k).lower() in ORG_JSONLD_OTHER_PARTY:
                continue
            out.extend(_jsonld_org_names(v))
    elif isinstance(node, list):
        for item in node:
            out.extend(_jsonld_org_names(item))
    return out


def _has_term(haystack: str, terms: set) -> bool:
    low = haystack.lower()
    return any(re.search(r"\b" + re.escape(t) + r"\b", low) for t in terms)


def _page_url(p: dict) -> str:
    return p.get("url") or p.get("final_url") or ""


def _first_screen(text: str, n: int = 220) -> str:
    return re.sub(r"\s+", " ", text[:n]).strip()


# --------------------------------------------------------------------------
# checks -- checks.yaml order
# --------------------------------------------------------------------------

def _chunk_resolves_subject(chunk: dict, terms: set) -> bool:
    """True when the chunk names its subject on its own OR its heading_path does
    -- the heading path travels with the chunk into the retriever, so a chunk
    opening 'It' under a heading naming the product is fine (QUOTE-001 guard)."""
    if _has_term(chunk.get("text", ""), terms):
        return True
    return _has_term(" ".join(chunk.get("heading_path") or []), terms)


def _chunk_fails_standalone(chunk: dict, terms: set) -> bool:
    sig = chunk.get("signals") or {}
    if (chunk.get("word_count") or 0) < MIN_CHUNK_WORDS:
        return False  # guard: short list items / table rows legitimately lack a subject
    if not (chunk.get("heading_path") or []):
        return False  # guard: only assess chunks with a real heading_path
    if _chunk_resolves_subject(chunk, terms):
        return False  # guard: weigh heading_path before counting a chunk as failing
    trigger = (sig.get("leading_pronoun")
               or len(sig.get("deictic_terms") or []) >= 1
               or (sig.get("bare_numbers") or 0) >= BARE_NUMBER_TRIGGER)
    return bool(trigger)


def check_quote_001(b: Bundle) -> list:
    """Passages do not make sense when retrieved on their own. Deterministic:
    aggregate the precomputed chunk signals; never re-chunk the page."""
    terms = b.brand_terms
    # Guard: without any subject vocabulary we cannot tell a failing chunk from a
    # fine one, and guessing here is the exact false positive this check is warned
    # about. Record that we could not assess, rather than generalise from nothing
    # or leave the reader unable to tell "checked, fine" from "never checked".
    if not terms:
        b.skip_check("QUOTE-001", "no brand or subject vocabulary could be "
                     "derived from titles, headings or schema.org; standalone "
                     "comprehension needs a subject to test each chunk against")
        return []

    content_pages = b.content_pages
    if not content_pages:
        # No assessable content: the root cause is rendering (READ-001), and
        # supersession attributes it there.
        b.skip_check("QUOTE-001", "no sampled page carries assessable main "
                     "content (all pages read as empty or as client-render "
                     "shells); see READ-001")
        return []

    assessed = 0
    failing = []  # (page, chunk)
    for p in content_pages:
        for ch in b.chunks(p["page_id"]):
            if (ch.get("word_count") or 0) < MIN_CHUNK_WORDS or not (ch.get("heading_path") or []):
                continue
            assessed += 1
            if _chunk_fails_standalone(ch, terms):
                failing.append((p, ch))

    n, m = len(failing), assessed
    if n == 0:
        return []
    # Guard: a single failing chunk is not a finding -- unless it carries a figure
    # a buyer would actually ask about, in which case one is enough.
    if n == 1 and (failing[0][1].get("signals") or {}).get("bare_numbers", 0) < 1:
        return []

    pages_hit_ids = sorted({p["page_id"] for p, _ in failing})
    pages_hit_urls = sorted({_page_url(p) for p, _ in failing})
    ex_page, ex_chunk = failing[0]
    heading = (ex_chunk.get("heading_path") or ["(no heading)"])[-1]
    excerpt = re.sub(r"\s+", " ", ex_chunk.get("text", "")).strip()[:400]

    ratio = n / m if m else 0.0
    crawl_partial = bool(b.coverage.get("skipped")) or \
        b.coverage.get("stopped_reason") not in ("completed", None)

    if len(pages_hit_urls) >= 2 and n >= 3 and ratio >= 0.30 and not crawl_partial:
        # A large share of chunks across several pages fail. Base severity high.
        # Scope is capped at 'section' on purpose: the orchestrator promotes a
        # site-wide 'high' to 'critical', and this check's registry rule forbids
        # critical outright ("never critical -- see the model-judged ceiling").
        severity, scope = "high", "section"
    else:
        # Confined to one page, a small share, or a crawl that did not complete
        # (a broad pattern cannot be claimed from a partial sample) -> medium.
        severity = "medium"
        scope = "section" if len(pages_hit_urls) >= 2 else "page"

    brand = b.brand_display
    lead = re.match(r"^(It|They|This|These|Those|We|Our|Its|Their)\b", excerpt)
    if lead:
        after = brand + excerpt[lead.end():]
    else:
        # No opening pronoun to swap -- prepend the subject so the first
        # sentence names it.
        after = "{}: {}".format(brand, excerpt[0].lower() + excerpt[1:])
    # If the passage carries a number but no currency marker at all, the figure
    # is unbound -- flag that in the sketch too, it is the second half of what
    # makes the chunk unquotable.
    unbound_figure = bool(re.search(r"\d", excerpt)) and not re.search(
        r"[$£€₹]|\b(?:GBP|USD|EUR|AUD|CAD|INR)\b", excerpt)
    note = (" Bind each figure to a currency and period (e.g. \"GBP 29 per "
            "month\")." if unbound_figure else "")
    code = ('<!-- {url} -- the passage under "{h}" as a retriever receives it, '
            'with nothing above it -->\n'
            '<!-- before: no subject named, opening reference unresolved -->\n'
            '<p>{before}</p>\n\n'
            '<!-- after: first sentence names the subject.{note} -->\n'
            '<p>{after}</p>').format(url=_page_url(ex_page), h=heading,
                                     before=excerpt, after=after, note=note)

    evidence = (
        '{n} of {m} assessed content chunks (>= {w} words, under a heading) '
        'neither name their subject nor resolve their opening reference; '
        '{p} of {cp} content page(s) affected{partial}. Example under "{h}" on '
        '{u}: "{ex}"'
    ).format(n=n, m=m, w=MIN_CHUNK_WORDS, p=len(pages_hit_urls),
             cp=len(content_pages),
             partial=" (crawl did not complete)" if crawl_partial else "",
             h=heading, u=_page_url(ex_page), ex=excerpt[:200])

    refs = [f"pages/{pid}/chunks.json" for pid in pages_hit_ids]
    refs.append(f"pages/{ex_page['page_id']}/extracted.json")

    return [finding(
        "QUOTE-001",
        "Passages do not make sense when retrieved on their own",
        severity, evidence, refs,
        pages=pages_hit_urls,
        counts={"failing_chunks": n, "assessed_chunks": m,
                "pages_affected": len(pages_hit_urls)},
        confidence="medium",
        determinism="deterministic",
        verification=(
            'Open {u}, read only the passage under "{h}" with nothing above it, '
            'and ask which product or plan it describes.'
        ).format(u=_page_url(ex_page), h=heading),
        excerpt=excerpt,
        scope=scope, checked=len(content_pages),
        action=act(
            "Rewrite passages so each names its subject in its first sentence",
            "medium" if severity == "medium" else "high",
            ["Identify chunks that open with 'It', 'They', 'This' or a bare figure "
             "on {} and the other affected pages".format(_page_url(ex_page)),
             "Replace the opening pronoun with the product or brand name",
             "Bind every number to what it counts (currency, unit, period)",
             "Remove positional references ('above', 'below', 'as mentioned')"],
            "M",
            "Retrieval hands a single chunk to the model with no heading and no "
            "neighbouring text. A chunk that does not name its own subject cannot "
            "be quoted as an answer, because the assistant cannot say what it is "
            "about.",
            code=code, owner="content"))]


def check_quote_002(b: Bundle) -> list:
    """The site never states plainly what the organization is. Model-judged:
    the script checks for an explicit identity sentence; the agent judges
    whether what exists is quotable enough."""
    content_pages = b.content_pages
    if not content_pages:
        return []

    # The subject of an identity sentence may be the declared name, the host
    # label or the bare domain: "lighttpd is a secure, fast web server" on a
    # site whose title suffix is "lighty news".
    phrases = list(b.brand_phrases)
    label = _host_label(b.site)
    for extra in ([label] if len(label) >= 3 else []) + [re.sub(r"^www\.", "", b.site or "")]:
        if extra and extra.lower() not in {ph.lower() for ph in phrases}:
            phrases.append(extra)
    patterns = [re.compile(r"\b" + re.escape(ph) + r"\b\s+" + SENT_VERB + r"\b", re.I)
                for ph in phrases]
    patterns.append(re.compile(
        r"\bwe(?:'re| are)\s+(?:a|an|the)\b|\bour\s+(?:company|team|firm|agency|"
        r"studio|platform|service|business)\s+" + SENT_VERB, re.I))

    for p in content_pages:
        text = b.page_text(p["page_id"])
        if any(pat.search(text) for pat in patterns):
            return []  # an explicit identity statement exists somewhere in the sample

    home = next((p for p in content_pages if p.get("page_type") == "home"), content_pages[0])
    home_excerpt = _first_screen(b.page_text(home["page_id"]))
    brand = b.brand_display

    code = None
    desc = (b.extracted(home["page_id"]).get("meta") or {}).get("description")
    if desc and desc.strip():
        d = desc.strip().rstrip(".")
        if not re.match(r"\s*" + re.escape(brand), d, re.I):
            d = "{} is {}".format(brand, d[0].lower() + d[1:])
        code = "<p>{}.</p>".format(d)

    # Guard (agent): a well-known brand needs less explanation, but a machine
    # resolving an ambiguous name does not know that -- report anyway and lower
    # severity when the brand is clearly established.
    # Guard (agent): accept any explicit, quotable statement of identity, not a
    # literal template. Only report when none exists anywhere in the sample.
    return [finding(
        "QUOTE-002",
        "The site never states plainly what the organization is",
        "high",
        ('No sampled page carries an explicit "{b} is a ..." identity sentence '
         'across {k} content page(s) checked. The home page opens: "{ex}"'
         ).format(b=brand, k=len(content_pages), ex=home_excerpt),
        ["MANIFEST.json", f"pages/{home['page_id']}/extracted.json"],
        pages=[],
        counts={"content_pages_checked": len(content_pages)},
        confidence="low",
        determinism="model-judged",
        verification=("Read the first screen of {u} and try to write one sentence "
                      "saying what the organisation does; confirm no such sentence "
                      "already appears on any sampled page."
                      ).format(u=_page_url(home)),
        excerpt=home_excerpt,
        scope="site-wide", checked=len(content_pages),
        action=act(
            "Add one explicit identity sentence to the top of the home page",
            "high",
            ["Write one sentence of the form '{b} is a <category> that <does what> "
             "for <whom>'".format(b=brand),
             "Place it as the first paragraph after the H1 on the home page",
             "Repeat the same sentence in the meta description and any llms.txt"],
            "S",
            "An assistant asked 'what is {b}?' quotes the sentence on the page that "
            "answers it. With no such sentence it infers one, or names a competitor "
            "whose identity line was explicit.".format(b=brand),
            code=code, owner="content"))]


def check_quote_003(b: Bundle) -> list:
    """Facts buyers ask about are absent or unextractable. Model-judged and
    gated conservatively: the bundle carries no site_profile, so applicability
    (gate 1) and the enterprise-pricing carve-out are the agent's to apply."""
    content_pages = b.content_pages
    if not content_pages:
        return []  # no extractable content anywhere -> READ-001, not this check

    # A contact page is legitimately short, so scan every fetched page (not just
    # the ones over the content-word threshold) for the contact signal.
    joined = []
    has_form_on_contactish = False
    for p in b.ok_pages:
        joined.append(b.page_text(p["page_id"]))
        ex = b.extracted(p["page_id"])
        for lk in ex.get("links") or []:
            joined.append(lk.get("href") or "")
        joined.append(b.raw_html(p["page_id"]))
        if p.get("page_type") in ("contact", "about", "home") and (ex.get("forms") or []):
            has_form_on_contactish = True
    blob = "\n".join(joined)

    classes = {
        "price": bool(PRICE_RE.search(blob)),
        "contact": bool(PHONE_RE.search(blob) or EMAIL_RE.search(blob) or has_form_on_contactish),
        "location": bool(POSTCODE_RE.search(blob)),
        "hours": bool(HOURS_RE.search(blob)),
        "delivery": bool(DELIVERY_RE.search(blob)),
    }
    absent = sorted(k for k, present in classes.items() if not present)

    # Only fire on the class every commercial site needs regardless of category:
    # a way to make contact, on a sampled page where it belongs. Everything else
    # is too category-dependent to assert without a site_profile.
    contactish_sampled = any(p.get("page_type") in ("contact", "about", "home")
                             for p in content_pages)
    if classes["contact"] or not contactish_sampled:
        return []

    # Guard (agent): gate by site_profile AND by what the business plausibly
    # publishes. Enterprise software withholding pricing behind sales is a
    # strategy -- report price at most 'low' and recommend stating the model.
    # Guard (agent): absence in our SAMPLE is not absence from the SITE -- check
    # coverage.skipped and confirm a page where the fact belongs was fetched.
    # Guard (agent): a fact locked in an image is READ-004, not this.
    skipped = len(b.coverage.get("skipped") or [])
    return [finding(
        "QUOTE-003",
        "Facts buyers ask about are absent or unextractable",
        "medium",
        ("No sampled page states a contact method (phone, email or enquiry form) "
         "as extractable text; {k} content page(s) checked, {s} URL(s) skipped "
         "during collection. Other fact classes not found in the sample: {a}."
         ).format(k=len(content_pages), s=skipped,
                  a=", ".join(x for x in absent if x != "contact") or "none"),
        ["MANIFEST.json", "coverage.json"],
        pages=[],
        counts={"content_pages_checked": len(content_pages),
                "fact_classes_absent": len(absent), "urls_skipped": skipped},
        confidence="low",
        determinism="model-judged",
        verification=("Search {o} for a phone number, email address or contact form "
                      "and try to select it as text.").format(o=b.origin),
        scope="site-wide", checked=len(content_pages),
        action=act(
            "State the facts a buyer asks about as plain, selectable text",
            "medium",
            ["Add a contact method (email, phone or an enquiry form) as text on the "
             "contact and home pages, not inside an image",
             "State each core fact class the business publishes -- price model, "
             "location, hours, delivery -- as a short sentence or a list item",
             "Keep the values in HTML text so they survive being copied"],
            "M",
            "An assistant answering 'how do I contact them?' needs a string it can "
            "lift. If the only phone number is baked into a header image, the "
            "answer it gives omits the brand or guesses.",
            owner="content"))]


def check_quote_004(b: Bundle) -> list:
    """Claims are abstract where they need to be concrete. Model-judged, never
    above medium: a quality observation, not a mechanism failure."""
    out = []
    for p in b.content_pages:
        if p.get("page_type") not in ("pricing", "product", "about"):
            continue  # guard: only where the page's PURPOSE is to convey facts
        ex = b.extracted(p["page_id"])
        text = (ex.get("text") or {}).get("main") or ""
        words = len(text.split())
        if words < 80:
            continue
        figures = len(re.findall(r"\d[\d,]*(?:\.\d+)?", text))
        dates = len(ex.get("dates") or [])
        # Named entities that are actual verifiable facts: proper nouns that are
        # not sentence-initial common words and not the brand's own name -- a
        # page repeating its own brand ten times has named nothing checkable.
        named = {t for t in re.findall(r"\b[A-Z][a-z]{2,}\b", text)
                 if t.lower() not in STOPWORDS and t.lower() not in b.brand_terms} - {
            "The", "This", "That", "These", "Those", "Their", "There", "Then",
            "They", "When", "Where", "What", "Which", "While", "With", "Your",
            "You", "Our", "We", "It", "Its", "But", "And", "For", "Not", "All",
            "Every", "Each", "Some", "Many", "Most", "More", "Here", "Now"}
        # Clear the page only if it carries a real figure, a date, or a cluster
        # of distinct external entities.
        if figures or dates or len(named) >= 4:
            continue
        excerpt = _first_screen(text, 200)
        out.append(finding(
            "QUOTE-004",
            "Claims are abstract where they need to be concrete",
            "medium",
            ("{u} is a {t} page of {w} words with no figures, no dates and fewer "
             "than 4 distinct external named entities in its main content. It "
             "opens: \"{ex}\""
             ).format(u=_page_url(p), t=p.get("page_type"), w=words, ex=excerpt),
            [f"pages/{p['page_id']}/extracted.json"],
            pages=[_page_url(p)],
            counts={"words": words, "figures": 0, "named_entities": len(named)},
            confidence="low",
            determinism="model-judged",
            verification=("Read {u} and list the specific verifiable facts it "
                          "states -- prices, names, dates, quantities."
                          ).format(u=_page_url(p)),
            excerpt=excerpt,
            scope="page", checked=len(b.content_pages),
            action=act(
                "Replace abstract claims with the specific facts behind them",
                "medium",
                ["List the concrete facts this page should convey (price, capacity, "
                 "founding year, headcount, locations)",
                 "Work each into the copy in place of the general claim it supports",
                 "Keep at least one verifiable figure in the first paragraph"],
                "M",
                "A retriever ranks and quotes passages that answer a question. A "
                "paragraph with no figure, name or date answers none, so the page "
                "is passed over even when it is on topic.",
                owner="content")))
    return out



def _looks_commercial(b) -> bool:
    """Does the sample show a site that sells or serves, rather than publishes?

    QUOTE-005 and QUOTE-006 are gated to ecommerce, saas, local-business and
    marketplace by references/site-profiles.md, and the bundle carries no site
    profile. Without this inference they fired on 62 of 85 corpus sites --
    Wikipedia, curl, CTAN, a personal blog -- for lacking a pricing page. The
    agent applies gate 1 properly; this is the script's conservative half.
    """
    types = {p.get("page_type") for p in b.ok_pages}
    if types & {"product", "category", "pricing"}:
        return True
    hints = re.compile(r"/(shop|store|products?|collections?|pricing|plans|"
                       r"checkout|cart|basket|book|booking|services?|menu|locations?|"
                       r"dp|b|p|sku|item)(/|$)", re.I)
    urls = [_page_url(p) for p in b.ok_pages] + b.sitemap_locs()
    if sum(1 for u in urls if hints.search(u)) >= 2:
        return True
    # A cart or checkout link anywhere in the sampled navigation settles it:
    # chewy.com's twenty sampled pages were all customer-care and membership,
    # never a product, but every one of them links to the cart.
    cart = re.compile(r"/(cart|checkout|basket|bag)(/|$|\?)", re.I)
    for p in b.ok_pages[:10]:
        for l in (b.extracted(p["page_id"]).get("links") or []):
            if l.get("internal") and cart.search(l.get("href") or ""):
                return True
    # A site that is mostly articles or docs is a publisher, whatever else it does.
    n = max(1, len(b.ok_pages))
    editorial = sum(1 for p in b.ok_pages if p.get("page_type") in ("article", "docs"))
    return editorial / n < 0.5 and any(
        re.search(r"(buy|order|subscribe|sign up|get started|free trial|shop now|"
                  r"free shipping|in stock|request a (demo|quote)|add to (cart|basket)|"
                  r"book now)",
                  (b.extracted(p["page_id"]).get("text") or {}).get("main") or "", re.I)
        for p in b.ok_pages[:10])


def check_quote_005(b: Bundle) -> list:
    """The site has none of the page types assistants cite most. Deterministic
    over the sampled page types plus the sitemap."""
    # Guard (agent): applies_when ecommerce/saas/local-business/marketplace only,
    # and never to docs or portfolio-brochure sites -- gate 1 is the agent's.
    if not _looks_commercial(b):
        return []  # gate 1: a publisher or docs site is not expected to sell
    wanted_types = {"faq", "pricing"}
    have_types = {p.get("page_type") for p in b.ok_pages}
    if wanted_types & have_types:
        return []

    url_re = re.compile(r"/(faq|faqs|pricing|plans|price|compare|comparison|"
                        r"how-it-works|how-we-work|vs-|-vs-)", re.I)
    all_urls = [_page_url(p) for p in b.ok_pages] + b.sitemap_locs()
    if any(url_re.search(u) for u in all_urls):
        return []

    sampled = len(b.ok_pages)
    sm_count = sum(len(sm.get("entries") or []) for sm in b.sitemaps)
    return [finding(
        "QUOTE-005",
        "The site has none of the page types assistants cite most",
        "medium",
        ("Neither the {sm} sitemap URL(s) nor the {n} sampled pages include an "
         "FAQ, pricing, comparison or how-it-works page."
         ).format(sm=sm_count, n=sampled),
        ["MANIFEST.json"],
        pages=[],
        counts={"sampled_pages": sampled, "sitemap_urls": sm_count},
        confidence="medium",
        determinism="deterministic",
        verification=("Search the navigation of {o} and its sitemap for an FAQ or "
                      "pricing page.").format(o=b.origin),
        scope="site-wide", checked=sampled,
        action=act(
            "Add the answer-shaped page type that matches how buyers ask",
            "medium",
            ["Add an FAQ built from the questions sales and support actually receive",
             "Add a pricing page that states the structure even if exact figures "
             "are withheld",
             "Link both from primary navigation and list them in the sitemap"],
            "M",
            "FAQ, pricing and comparison pages are made of self-contained passages "
            "-- one question, one answer -- which is the unit a retriever quotes. "
            "A site without them offers nothing shaped like an answer.",
            owner="content"))]


def check_quote_006(b: Bundle) -> list:
    """Common buyer questions have no answer on the site. Model-judged. Only
    emitted when there is no FAQ and no pricing page at all -- enumerating
    hypothetical questions is the padding the rubric penalises, so the concrete
    question set is derived by the agent from the site's own category."""
    if not _looks_commercial(b):
        return []  # gate 1: "buyer questions" presuppose something to buy
    have_types = {p.get("page_type") for p in b.ok_pages}
    if {"faq", "pricing"} & have_types:
        return []
    url_re = re.compile(r"/(faq|faqs|pricing|plans|price)", re.I)
    if any(url_re.search(u) for u in [_page_url(p) for p in b.ok_pages] + b.sitemap_locs()):
        return []
    content_pages = b.content_pages
    if not content_pages:
        return []

    # Guard (agent): derive a handful of genuinely central questions from the
    # site's OWN offering, not a generic list. Cap confidence at medium -- the
    # sample is partial and an answer may sit on an unsampled page.
    return [finding(
        "QUOTE-006",
        "Common buyer questions have no answer on the site",
        "medium",
        ("Across {k} sampled content page(s) there is no FAQ section and no "
         "question-and-answer content; the questions a buyer in this category "
         "asks have no retrievable answer in the sample."
         ).format(k=len(content_pages)),
        ["MANIFEST.json"],
        pages=[],
        counts={"content_pages_checked": len(content_pages)},
        confidence="low",
        determinism="model-judged",
        verification=("Pick the three questions a buyer in this category asks most "
                      "and search {o} for a self-contained answer to each."
                      ).format(o=b.origin),
        scope="site-wide", checked=len(content_pages),
        action=act(
            "Answer the handful of questions buyers actually ask, one per heading",
            "medium",
            ["List the 5-8 questions sales and support field most often",
             "Answer each in 40-80 words under its own question-phrased heading",
             "Repeat enough of the question in the answer that it stands alone"],
            "M",
            "Assistants match a user's question to a passage phrased like an "
            "answer to it. Without Q&A content there is nothing to match, so the "
            "brand is absent from those answers.",
            owner="content"))]


def check_quote_007(b: Bundle) -> list:
    """Answers are buried below long preamble. Model-judged, never above medium.
    Deterministic precursor: how far into an answer-purpose page the first
    figure appears."""
    out = []
    for p in b.content_pages:
        if p.get("page_type") not in ("pricing", "faq", "product"):
            continue  # guard: apply only to pages whose purpose is to answer directly
        chunks = b.chunks(p["page_id"])
        if not chunks:
            continue
        preamble = 0
        hit_index = None
        for i, ch in enumerate(chunks):
            sig = ch.get("signals") or {}
            if (sig.get("bare_numbers") or 0) > 0 or PRICE_RE.search(ch.get("text", "")):
                hit_index = i
                break
            preamble += ch.get("word_count") or 0
        if hit_index is None or preamble <= 150:
            continue
        preamble_headings = ", ".join(
            x for ch in chunks[:hit_index] for x in (ch.get("heading_path") or [])
        ) or "(intro)"
        out.append(finding(
            "QUOTE-007",
            "Answers are buried below long preamble",
            "medium",
            ("On {u} the first figure appears about {n} words in, after {c} "
             "chunk(s) of preamble under headings: {h}."
             ).format(u=_page_url(p), n=preamble, c=hit_index, h=preamble_headings),
            [f"pages/{p['page_id']}/chunks.json"],
            pages=[_page_url(p)],
            counts={"preamble_words": preamble, "preamble_chunks": hit_index},
            confidence="low",
            determinism="model-judged",
            verification=("Open {u} and count how far you scroll before reaching "
                          "the first price or figure.").format(u=_page_url(p)),
            scope="page", checked=len(b.content_pages),
            action=act(
                "Lead the page with the fact it exists to convey",
                "medium",
                ["Move the first price or key figure into the opening paragraph",
                 "Keep the narrative context, but after the answer, not before it"],
                "S",
                "A retriever that grabs the first chunk of an answer page should "
                "get the answer. Preamble in that slot means the quoted passage "
                "carries context instead of the fact.",
                owner="content")))
    return out


def check_quote_008(b: Bundle) -> list:
    """A proprietary term stands in for the category and is never unpacked.
    Model-judged, low. Deliberately narrow: it fires only when a coined name is
    the declared subject of the page (in the title or an h1), is used several
    times in the body, the page carries no plain category word at all, and no
    sentence anywhere defines the term. That is the one shape the guard allows
    -- 'a proprietary name REPLACES a category term entirely'."""
    out = []
    brand_norms = {_norm_name(x) for x in b.brand_phrases}
    for p in b.content_pages:
        if p.get("page_type") == "docs":
            continue  # guard: docs for existing users may assume the vocabulary
        ex = b.extracted(p["page_id"])
        text = (ex.get("text") or {}).get("main") or ""
        if CATEGORY_NOUN_RE.search(text):
            continue  # something on the page connects the product to what it is

        declared = (ex.get("title") or "") + " " + " ".join(
            h.get("text", "") for h in ex.get("headings") or [] if h.get("level") in (1, 2))
        candidates = {m.group(0) for m in PROPRIETARY_RE.finditer(declared)
                      if m.group(0).lower() not in b.brand_terms
                      and _norm_name(m.group(0)) not in brand_norms}

        undefined = []
        for term in sorted(candidates):
            body_uses = len(re.findall(r"\b" + re.escape(term) + r"\b", text))
            if body_uses < 3:
                continue
            # Does any sentence actually explain the term?
            defined = re.search(
                re.escape(term) + r"\s*(?:,|--|—|:|\bis\b|\bare\b|\blets\b|"
                r"\bhelps\b|\ballows\b|\bmeans\b|\bstands for\b)", text)
            if not defined:
                undefined.append((term, body_uses))
        if not undefined:
            continue

        terms = [t for t, _ in undefined]
        out.append(finding(
            "QUOTE-008",
            "Domain terms are used without being defined",
            "low",
            ("{u} presents {terms} as its subject (in the title or a heading), "
             "uses {n}+ times in the body, carries no plain category word "
             "(platform, service, tool, ...) and never defines the term."
             ).format(u=_page_url(p), terms=", ".join(terms[:4]),
                      n=min(c for _, c in undefined)),
            [f"pages/{p['page_id']}/extracted.json"],
            pages=[_page_url(p)],
            counts={"undefined_terms": len(undefined)},
            confidence="low",
            determinism="model-judged",
            verification=("Read {u} as someone new to the category and list the "
                          "terms you could not follow.").format(u=_page_url(p)),
            scope="page", checked=len(b.content_pages),
            action=act(
                "Pair each proprietary term with the plain category word once",
                "low",
                ["On first use, write '<ProprietaryName>, our <category> for <task>,'",
                 "Keep the searchable category word in the title and first paragraph"],
                "S",
                "A reader -- and a retriever -- who has never met the proprietary "
                "name has no way to connect the page to the category being searched "
                "for, so the page is never retrieved for that category.",
                owner="content")))
    return out


def check_quote_009(b: Bundle) -> list:
    """Specifications are prose or images rather than structured text.
    Deterministic: measured values in prose on a product page with no table or
    description list in the raw HTML."""
    # Guard (agent): applies_when ecommerce/saas/marketplace only (gate 1).
    out = []
    for p in b.ok_pages:
        if p.get("page_type") != "product":
            continue  # guard: prose is fine when the page is not a spec page
        text = (b.extracted(p["page_id"]).get("text") or {}).get("main") or ""
        values = SPEC_VALUE_RE.findall(text)
        if len(values) < 6:
            continue
        raw = b.raw_html(p["page_id"]).lower()
        if "<table" in raw or "<dl" in raw or raw.count("<li") >= 6:
            continue
        # Guard (agent): specs locked in an image are READ-004, not this.
        out.append(finding(
            "QUOTE-009",
            "Specifications are prose or images rather than structured text",
            "medium",
            ("{u} presents {n} specification values ({sample}) as running prose "
             "with no <table>, <dl> or list in the HTML."
             ).format(u=_page_url(p), n=len(values),
                      sample=", ".join(sorted(set(values))[:5])),
            [f"pages/{p['page_id']}/extracted.json", f"pages/{p['page_id']}/raw.html"],
            pages=[_page_url(p)],
            counts={"spec_values": len(values)},
            confidence="medium",
            determinism="deterministic",
            verification=("Try to select the specification table from {u} as text."
                          ).format(u=_page_url(p)),
            scope="page", checked=len(b.ok_pages),
            action=act(
                "Move the specification values into a table or description list",
                "medium",
                ["Put each attribute/value pair in a <tr> or a <dt>/<dd>",
                 "Keep the prose description, but let the table carry the numbers"],
                "M",
                "A retriever can lift a table row verbatim as an answer to 'what is "
                "the capacity of X'. The same value inside a sentence of six other "
                "numbers cannot be extracted cleanly.",
                owner="engineering")))
    return out


def check_quote_010(b: Bundle) -> list:
    """The brand or product is named inconsistently. Deterministic: compare
    normalised brand names from titles, og:site_name and schema.org -- not H1s,
    which carry the page topic rather than the entity name."""
    names = Counter()
    for p in b.ok_pages:
        ex = b.extracted(p["page_id"])
        for block in ex.get("jsonld") or []:
            if block.get("parsed_ok"):
                for nm in _jsonld_org_names(block.get("value")):
                    names[_norm_name(nm)] += 1
        og = (ex.get("meta") or {}).get("og:site_name")
        if og:
            names[_norm_name(og)] += 1
    # the recurring title segment is the brand candidate from titles
    seg_counter = Counter()
    for p in b.ok_pages:
        for seg in TITLE_SPLIT_RE.split(b.extracted(p["page_id"]).get("title") or ""):
            seg = seg.strip()
            if len(seg) >= 3:
                seg_counter[seg] += 1
    for seg, c in seg_counter.items():
        if c >= 2:
            names[_norm_name(seg)] += c

    distinct = sorted({n for n in names if n})
    # Guard: capitalisation, punctuation and legal suffixes already normalised.
    # Guard: a short form alongside a full form is normal usage -- drop any name
    # that is a whitespace-delimited substring of another.
    surviving = [n for n in distinct
                 if not any(n != other and (n in other or other in n)
                            for other in distinct)]
    if len(surviving) < 2:
        return []

    pages_with = sorted({_page_url(p) for p in b.ok_pages
                         if b.extracted(p["page_id"]).get("title")})
    return [finding(
        "QUOTE-010",
        "The brand or product is named inconsistently",
        "medium",
        ("The organisation appears under {n} materially different names across "
         "{k} sampled pages: {names}."
         ).format(n=len(surviving), k=len(pages_with),
                  names=", ".join('"%s"' % s for s in surviving)),
        ["MANIFEST.json"],
        pages=pages_with,
        counts={"name_variants": len(surviving)},
        confidence="medium",
        determinism="deterministic",
        verification=("Compare the brand name in the <title>, og:site_name and "
                      "schema.org markup across {o}'s pages."
                      ).format(o=b.origin),
        scope="site-wide" if len(pages_with) >= 3 else "section",
        checked=len(b.ok_pages),
        action=act(
            "Pick one canonical name for the entity and use it everywhere",
            "medium",
            ["Choose the canonical brand name",
             "Use it verbatim in every <title>, the og:site_name and schema.org name",
             "A short form is fine in body copy as long as the full form appears too"],
            "S",
            "An assistant treats two unlinked names as two entities and splits the "
            "evidence for each. One consistent name lets all the signal accrue to "
            "one entity it can cite.",
            owner="seo"))]


def check_quote_011(b: Bundle) -> list:
    """Titles and headings do not say what the page answers. Model-judged.
    PARSE-010 covers missing and duplicated titles mechanically -- this is
    descriptiveness only."""
    generic = []
    for p in b.content_pages:
        ex = b.extracted(p["page_id"])
        title = (ex.get("title") or "").strip()
        if not title:
            continue  # missing titles are PARSE-010, not this check
        core = title
        for seg in TITLE_SPLIT_RE.split(title):
            seg = seg.strip()
            if seg and _norm_name(seg) not in {_norm_name(x) for x in b.brand_phrases}:
                core = seg
                break
        norm = _norm_name(core)
        # Guard: 'Home', 'About' and 'Contact' are conventional -- never report.
        if p.get("page_type") in ("home", "about", "contact"):
            continue
        if norm in GENERIC_TITLES:
            generic.append((p, title))

    if len(generic) < 2:
        return []
    checked = len(b.content_pages)
    return [finding(
        "QUOTE-011",
        "Titles and headings do not say what the page answers",
        "medium",
        ("{n} of {m} content pages carry a non-descriptive title: {ex}."
         ).format(n=len(generic), m=checked,
                  ex="; ".join('%s -> "%s"' % (_page_url(p), t)
                               for p, t in generic[:4])),
        ["MANIFEST.json"] + [f"pages/{p['page_id']}/extracted.json"
                             for p, _ in generic[:5]],
        pages=[_page_url(p) for p, _ in generic],
        counts={"generic_titles": len(generic), "content_pages": checked},
        confidence="low",
        determinism="model-judged",
        verification=("Read only the <title> and <h1> of {u} and say what the page "
                      "contains.").format(u=_page_url(generic[0][0])),
        scope="section" if len(generic) < checked else "site-wide",
        checked=checked,
        action=act(
            "Rewrite each title to name what the page answers",
            "medium",
            ["Replace generic titles ('Welcome', 'Page') with a specific phrase",
             "Include the subject and the question the page answers",
             "Keep the brand as a suffix after a separator"],
            "S",
            "Titles and H1s are the highest-weight text a retriever reads. A "
            "generic one gives it nothing to match a query against, so the page "
            "is not retrieved even when its body would answer.",
            owner="content"))]


def check_quote_012(b: Bundle) -> list:
    """Long pages carry no summary a machine can lift. The guard is binding:
    prefer a proactive recommendation over a finding. Handled in proactive()."""
    # Guard: reporting a missing summary as a defect on every long page inflates
    # the count. Emitted as a proactive recommendation instead -- see proactive().
    return []


CHECKS = [
    check_quote_001, check_quote_002, check_quote_003, check_quote_004,
    check_quote_005, check_quote_006, check_quote_007, check_quote_008,
    check_quote_009, check_quote_010, check_quote_011, check_quote_012,
]

# Every QUOTE check in references/checks.yaml is implemented above: the four
# deterministic checks compute their verdict here, the eight model-judged checks
# emit the precomputed signals for the agent to finish per SKILL.md.
NOT_YET_IMPLEMENTED: list = []


def proactive(b: Bundle, findings: list) -> list:
    """Improvements worth making where no defect was found. Each must cite
    something actually observed in the bundle. `findings` is what the checks
    already produced, so we do not re-run them here."""
    out = []
    content_pages = b.content_pages
    fired = {f.get("check_id") for f in findings}
    ran_001 = "QUOTE-001" in fired
    ran_002 = "QUOTE-002" in fired

    # QUOTE-P01 -- gate: always, when QUOTE-001/002 did not reach threshold.
    if content_pages and not ran_001 and not ran_002:
        assessed = sum(1 for p in content_pages for ch in b.chunks(p["page_id"])
                       if (ch.get("word_count") or 0) >= MIN_CHUNK_WORDS
                       and (ch.get("heading_path") or []))
        out.append({
            "id": "P-000",  # QUOTE-P01; orchestrator assigns the real id
            "title": "Open each key page with one self-contained sentence naming the subject",
            "category": CATEGORY,
            "mechanism": MECHANISM,
            "rationale": (
                "{a} content chunks across {p} sampled pages passed the standalone "
                "check, but retrieval still pulls each passage away from its page. "
                "A first sentence that names the subject explicitly is what makes a "
                "chunk survive that separation, and it costs one line per page."
            ).format(a=assessed, p=len(content_pages)),
            "suggested_action": act(
                "Add a subject-naming first sentence to each key page",
                "low",
                ["On the home, pricing, product and about pages, make the first "
                 "sentence name the brand or product explicitly",
                 "Avoid opening those pages with 'It', 'This' or 'We'"],
                "S",
                "A named subject in the opening sentence keeps the first retrieved "
                "chunk quotable without its surrounding page.",
                owner="content"),
        })

    # QUOTE-P02 -- gate: no FAQ page exists.
    have_types = {p.get("page_type") for p in b.ok_pages}
    faq_urls = [u for u in [_page_url(p) for p in b.ok_pages] + b.sitemap_locs()
                if re.search(r"/faq", u, re.I)]
    if "faq" not in have_types and not faq_urls:
        out.append({
            "id": "P-000",  # QUOTE-P02; orchestrator assigns the real id
            "title": "Add an FAQ answering the questions sales and support actually receive",
            "category": CATEGORY,
            "mechanism": MECHANISM,
            "rationale": (
                "No FAQ page appears among the {n} sampled pages or in the sitemap. "
                "Question-and-answer pairs match how people phrase queries to "
                "assistants, and each answer is a self-contained passage that can "
                "be quoted whole."
            ).format(n=len(b.ok_pages)),
            "suggested_action": act(
                "Publish an FAQ from real sales and support questions",
                "low",
                ["Collect the questions support and sales answer most often",
                 "Write one self-contained answer per question, 40-80 words",
                 "Phrase each heading as the question a customer would type"],
                "M",
                "Each Q&A pair is already shaped like the passage a retriever "
                "quotes, so an FAQ converts existing support knowledge directly "
                "into citable answers.",
                owner="content"),
        })

    # QUOTE-P03 -- gate: no pricing information of any kind is published.
    any_price = any(PRICE_RE.search(b.page_text(p["page_id"])) for p in content_pages)
    price_urls = [u for u in [_page_url(p) for p in b.ok_pages] + b.sitemap_locs()
                  if re.search(r"/(pricing|plans|price)", u, re.I)]
    if content_pages and not any_price and "pricing" not in have_types and not price_urls:
        out.append({
            "id": "P-000",  # QUOTE-P03; orchestrator assigns the real id
            "title": "State pricing structure even where exact figures are withheld",
            "category": CATEGORY,
            "mechanism": MECHANISM,
            "rationale": (
                "No price, plan or 'from GBP X' statement was found on any of the "
                "{n} sampled content pages, and no pricing page exists. 'Per seat, "
                "annual contract, from GBP X' is quotable and answers the question "
                "a buyer actually asks, without publishing a rate card."
            ).format(n=len(content_pages)),
            "suggested_action": act(
                "Publish the pricing model, even without exact numbers",
                "low",
                ["State the billing unit (per seat, per month, per order)",
                 "State a floor ('from GBP X') if any figure can be shared",
                 "Put it on a /pricing page linked from primary navigation"],
                "S",
                "Saying nothing about price leaves an assistant to infer a number "
                "or to recommend a competitor whose pricing model was explicit.",
                owner="marketing"),
        })

    # QUOTE-012 -- long page with no liftable summary (proactive by binding guard).
    for p in content_pages:
        ex = b.extracted(p["page_id"])
        words = (ex.get("text") or {}).get("word_count") or 0
        if words < 900:
            continue
        headings = " ".join(h.get("text", "") for h in ex.get("headings") or [])
        chunks = b.chunks(p["page_id"])
        first_wc = chunks[0].get("word_count") if chunks else 0
        if SUMMARY_HINT_RE.search(headings) or (first_wc and first_wc <= 120):
            continue
        out.append({
            "id": "P-000",  # QUOTE-012 (proactive per binding guard); orchestrator assigns the real id
            "title": "Add a liftable summary to the top of long pages",
            "category": CATEGORY,
            "mechanism": MECHANISM,
            "rationale": (
                "{u} runs to {w} words with no summary, key-takeaways or TL;DR "
                "block near the top. A 2-3 sentence summary is the block most "
                "likely to be retrieved and quoted whole."
            ).format(u=_page_url(p), w=words),
            "suggested_action": act(
                "Add a 2-3 sentence summary block after the H1",
                "low",
                ["Write a 2-3 sentence summary or a short 'key takeaways' list",
                 "Place it directly after the H1, before the body",
                 "State the page's conclusion, not its topic"],
                "S",
                "The summary block sits where a retriever grabs its first chunk, "
                "so it becomes the passage quoted for the whole page.",
                owner="content"),
        })
        break  # one is enough to make the point

    # QUOTE-P04 -- gate: few headings are phrased as the question a user asks.
    # Addresses a factor no site crawl can measure: whether the engine retrieves
    # at all. Question-form queries trigger AI Overviews far more often than the
    # average query, so content shaped as an answer to a stated question is more
    # likely to be pulled into a generative answer in the first place. We cannot
    # observe activation; we can observe whether the site is shaped for it.
    if content_pages:
        heads, question_heads = 0, 0
        for page in content_pages:
            for h in (b.extracted(page["page_id"]).get("headings") or []):
                text = (h.get("text") or "").strip()
                if not text:
                    continue
                heads += 1
                if text.endswith("?") or re.match(
                        r"^(how|what|why|when|where|which|who|can|do|does|is|are)",
                        text, re.I):
                    question_heads += 1
        if heads >= 8 and question_heads <= max(1, heads // 12):
            out.append({
                "id": "P-000",  # QUOTE-P04
                "title": "Phrase section headings as the questions people actually ask",
                "category": CATEGORY,
                "mechanism": MECHANISM,
                "rationale": (
                    "{q} of {h} headings across {p} sampled pages are phrased as a "
                    "question. Assistants answer questions, and a heading that "
                    "states the question makes the passage beneath it an answer to "
                    "retrieve rather than prose to summarise. This is a "
                    "recommendation, not a defect: whether a query reaches the "
                    "site at all is decided inside the engine and cannot be "
                    "measured from here."
                ).format(q=question_heads, h=heads, p=len(content_pages)),
                "suggested_action": act(
                    "Rewrite key section headings into question form",
                    "low",
                    ["Take the questions sales and support are actually asked",
                     "Make each one a heading, with the answer in the first "
                     "sentence beneath it",
                     "Keep the declarative heading as a subheading where the "
                     "question form reads awkwardly"],
                    "S",
                    "A question heading with its answer directly beneath is the "
                    "shape a retrieval system can lift whole.",
                    owner="content"),
            })

    # QUOTE-P05 -- gate: no comparison or alternatives content anywhere.
    # Addresses a second unmeasurable factor: the competing candidate pool.
    # Citation share is relative -- a page is chosen against the others retrieved
    # for the same query. We cannot see that pool, but a site with no comparison
    # content never enters the comparison queries where the pool forms.
    all_urls = [_page_url(p) for p in b.ok_pages] + b.sitemap_locs()
    comparison = [u for u in all_urls
                  if re.search(r"(compare|comparison|alternative|vs-|-vs-|/vs/|best-)",
                               u, re.I)]
    if content_pages and not comparison:
        out.append({
            "id": "P-000",  # QUOTE-P05
            "title": "Publish the comparison the buyer is already making",
            "category": CATEGORY,
            "mechanism": MECHANISM,
            "rationale": (
                "No sampled or advertised URL looks like comparison content "
                "across {n} URLs examined. Buyers ask assistants to compare and "
                "shortlist, and the answer is assembled from whatever sources "
                "were retrieved together. A site with nothing comparison-shaped "
                "is rarely among them. Which competitors share that pool is not "
                "observable from this site, so this is a recommendation rather "
                "than a finding."
            ).format(n=len(all_urls)),
            "suggested_action": act(
                "Add honest comparison and alternatives pages",
                "low",
                ["Write a page per realistic alternative, naming it plainly",
                 "State where the alternative is the better choice -- one-sided "
                 "comparisons read as marketing and get discounted",
                 "Put the decision criteria in a table so they can be lifted "
                 "as a unit"],
                "M",
                "Comparison pages are what put a brand into the shortlist an "
                "assistant assembles, which is where mid-funnel buyers arrive.",
                owner="content"),
        })

    # QUOTE-P06 / P07 / P08 -- the three strongest measured citation drivers in
    # the literature, emitted as recommendations rather than defects. Aggarwal
    # et al. (arXiv:2311.09735) measure +41% PAWC from adding quotations and
    # +30-40% from citing sources and adding statistics, on GEO-bench. Those are
    # relative gains inside a simulator with five documents pre-injected into
    # context -- not a promise of traffic -- and the absence of a quotation is
    # not a defect in any page. Recommend; never flag.
    struct = [(p_, b.extracted(p_["page_id"]).get("structure") or {})
              for p_ in content_pages]
    struct = [(p_, st) for p_, st in struct if st]

    if struct:
        quoting = sum(1 for _, st in struct if (st.get("quotation_markers") or 0) > 0)
        struct_pages = [p_ for p_, _ in struct]
        outbound = 0
        for page in struct_pages:
            links = b.extracted(page["page_id"]).get("links") or []
            if any(l.get("href") and not l.get("internal") for l in links):
                outbound += 1
        if quoting == 0 and outbound <= len(struct) // 3:
            out.append({
                "id": "P-000",  # QUOTE-P06
                "title": "Quote and attribute the sources behind your claims",
                "category": CATEGORY,
                "mechanism": MECHANISM,
                "rationale": (
                    "None of the {n} sampled content pages contain a quotation "
                    "element, and {o} carry an outbound reference. Adding "
                    "quotations and cited sources are the two largest measured "
                    "effects in the GEO literature (+41% and +30-40% relative "
                    "visibility on the GEO-bench simulator). The measurement is "
                    "a relative gain inside a fixed context window rather than a "
                    "traffic promise, and the effect was largest for pages that "
                    "were not already ranking first."
                ).format(n=len(struct), o=outbound),
                "suggested_action": act(
                    "Attribute the claims that carry weight",
                    "low",
                    ["Where a page asserts an industry fact, quote the source "
                     "and link it",
                     "Use blockquote or q so the quotation is structurally "
                     "marked, not just typographic quotes",
                     "Attribute to a named source -- an unattributed quotation "
                     "adds nothing"],
                    "M",
                    "A quoted, attributed claim can be repeated by an assistant "
                    "with its provenance intact, which is what makes it safe to "
                    "repeat at all.",
                    owner="content"),
            })

        numeric = 0
        for page in struct_pages:
            body = ((b.extracted(page["page_id"]).get("text") or {}).get("main") or "")
            # Currency, percentages and measured quantities with units. A bare
            # 3+ digit run matches years and phone numbers, which are not the
            # quantitative evidence the literature measures.
            figures = re.findall(
                r"(?<![\w.])(?:[$£€₹]\s?\d[\d,]*(?:\.\d+)?"
                r"|\d[\d,]*(?:\.\d+)?\s?%"
                r"|\d[\d,]*(?:\.\d+)?\s?(?:x|hrs?|hours?|mins?|minutes?|days?|"
                r"weeks?|months?|years?|kg|lbs?|gb|tb|mb|ms|km|mi|users?|"
                r"customers?|seats?))", body, re.I)
            if len(figures) >= 3:
                numeric += 1
        if struct and numeric <= len(struct) // 4:
            out.append({
                "id": "P-000",  # QUOTE-P07
                "title": "Put numbers on the claims that have them",
                "category": CATEGORY,
                "mechanism": MECHANISM,
                "rationale": (
                    "Only {k} of {n} sampled content pages carry three or more "
                    "concrete figures. Quantitative statements are among the "
                    "strongest measured citation drivers (+30-40% relative "
                    "visibility), and they are also what a buyer asked an "
                    "assistant to compare. Qualitative superlatives are not "
                    "quotable as evidence."
                ).format(k=numeric, n=len(struct)),
                "suggested_action": act(
                    "Replace superlatives with figures",
                    "low",
                    ["Give prices, capacities, durations, guarantees and "
                     "measured results as numbers with units",
                     "Attach each figure to its subject in the same sentence, "
                     "so it survives being retrieved alone",
                     "Where an exact figure cannot be published, give the range "
                     "or the basis"],
                    "M",
                    "A number with its subject and unit attached is the smallest "
                    "unit an assistant can lift and still be correct.",
                    owner="content"),
            })

        offsets = [st.get("first_answer_offset") for _, st in struct
                   if st.get("first_answer_offset") is not None]
        if offsets:
            median_off = sorted(offsets)[len(offsets) // 2]
            if median_off > 0.30:
                out.append({
                    "id": "P-000",  # QUOTE-P08
                    "title": "Answer in the opening third of the page",
                    "category": CATEGORY,
                    "mechanism": MECHANISM,
                    "rationale": (
                        "The first substantial paragraph begins at a median "
                        "{o:.0%} through the document across {n} sampled pages. "
                        "One industry measurement found 44.2% of ChatGPT "
                        "citations came from the first 30% of a page. That study "
                        "is correlational, and the honest reading is not that "
                        "moving text upward guarantees citation -- it is that "
                        "where the answer sits is measurable and currently late."
                    ).format(o=median_off, n=len(offsets)),
                    "suggested_action": act(
                        "Lead with the answer, then elaborate",
                        "low",
                        ["Open each page with a short paragraph that answers the "
                         "question the page exists to answer",
                         "Move preamble, brand narrative and navigation copy "
                         "below that",
                         "Keep the detail -- this is about order, not length"],
                        "M",
                        "Retrieval reads the opening of a document first and "
                        "attends to it most; an answer that arrives late may not "
                        "be reached at all.",
                        owner="content"),
                })

    # QUOTE-P09 -- sentence length as a readability proxy. Aggarwal et al.
    # measure +15-30% relative visibility from fluency optimisation. Rather than
    # approximate Flesch-Kincaid with a guessed syllable counter, we report the
    # term that dominates every readability formula and can be counted exactly:
    # sentence length. Named for what it is, so nobody mistakes it for a grade.
    if content_pages:
        lengths = []
        for page in content_pages:
            body = ((b.extracted(page["page_id"]).get("text") or {}).get("main") or "")
            for sentence in re.split(r"(?<=[.!?])\s+", body):
                words = sentence.split()
                if len(words) >= 3:
                    lengths.append(len(words))
        if len(lengths) >= 25:
            lengths.sort()
            median_len = lengths[len(lengths) // 2]
            long_share = sum(1 for l in lengths if l > 30) / float(len(lengths))
            if median_len > 25 or long_share > 0.25:
                out.append({
                    "id": "P-000",  # QUOTE-P09
                    "title": "Shorten the sentences that carry the facts",
                    "category": CATEGORY,
                    "mechanism": MECHANISM,
                    "rationale": (
                        "Median sentence length across {n} sentences on {p} "
                        "sampled pages is {m} words, and {s:.0%} run past 30. "
                        "Simplifying language measured +15-30% relative "
                        "visibility on the GEO-bench simulator. This counts "
                        "sentence length, the term that dominates every "
                        "readability formula -- it is not a reading-grade score "
                        "and should not be reported as one."
                    ).format(n=len(lengths), p=len(content_pages), m=median_len,
                             s=long_share),
                    "suggested_action": act(
                        "Split the long sentences on fact-bearing pages",
                        "low",
                        ["Break sentences carrying more than one claim into one "
                         "sentence per claim",
                         "Put the claim before the qualification, not after it",
                         "Leave narrative and brand copy alone -- this matters "
                         "where facts live"],
                        "M",
                        "One claim per sentence survives being retrieved alone; "
                        "a claim buried in a subordinate clause does not.",
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

    # Content-dependent checks that never got a page to look at: record them so
    # the report distinguishes "checked, fine" from "never checked".
    if not b.content_pages:
        for cid in ("QUOTE-002", "QUOTE-004", "QUOTE-006", "QUOTE-007",
                    "QUOTE-008", "QUOTE-011"):
            b.skip_check(cid, "no sampled page carries assessable main content; "
                         "the rendering root cause is READ-001")

    # Drop any candidate whose refs do not resolve (false-positive gate 2),
    # rather than handing the orchestrator work we can do here.
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

    result = {"skill": "answerability-audit", "mechanism": MECHANISM,
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
        print(f"{len(kept)} QUOTE candidates -> {args.out}", file=sys.stderr)
        for f in kept:
            print(f"  {f['check_id']:11} {f['severity']:8} {f['title']}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
