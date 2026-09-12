#!/usr/bin/env python3
"""PARSE checks: can a machine parse specific facts out of the page?

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
    python check_structured_data.py <bundle> --out parse-candidates.json
    python check_structured_data.py <bundle> --stdout
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import unicodedata
from urllib.parse import urlparse

MECHANISM = "parse"

# Optional libraries (requirements-optional.txt at the marketplace root):
# imported behind a guard at the call site, cached here, never required.
_OPTIONAL: dict = {}


def _optional(name: str):
    if name not in _OPTIONAL:
        try:
            import importlib
            _OPTIONAL[name] = importlib.import_module(name)
        except Exception:
            _OPTIONAL[name] = None
    return _OPTIONAL[name]
CATEGORY = "discoverability"

GENERIC_TYPES = {
    "webpage", "website", "breadcrumblist", "organization",
    "itempage", "aboutpage", "contactpage"
}

COMMERCIAL_PAGE_TYPES = {"product", "pricing", "category"}

CURRENCY_SYMBOLS = {
    "£": "GBP",
    "$": "USD",
    "€": "EUR",
    "¥": "JPY",
    "₹": "INR",
    "C$": "CAD",
    "A$": "AUD",
}


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
        self._site_type: str | None = None

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
        """Pages that were actually fetched with status 200."""
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

    @property
    def site_profile(self) -> str:
        """Classify site profile from bundle evidence per site-profiles.md."""
        if self._site_type is not None:
            return self._site_type

        # 1. Check explicit run metadata
        explicit = self.run.get("site_profile") or self.manifest.get("site_profile")
        if isinstance(explicit, dict) and explicit.get("site_type"):
            self._site_type = explicit["site_type"]
            return self._site_type
        if isinstance(explicit, str) and explicit:
            self._site_type = explicit
            return self._site_type

        # 2. Inspect signals across sampled pages deterministically
        types_seen: set[str] = set()
        paths: list[str] = []
        has_pricing = False
        has_docs = False
        has_cart = False
        article_count = 0

        for p in self.ok_pages:
            url = p.get("url") or ""
            path = urlparse(url).path.lower()
            paths.append(path)
            if any(c in path for c in ("/cart", "/checkout", "/basket")):
                has_cart = True
            if any(pr in path for pr in ("/pricing", "/plans")):
                has_pricing = True
            if "/docs" in path or "/reference" in path or "/api" in path:
                has_docs = True

            ext = self.extracted(p["page_id"])
            for block in ext.get("jsonld") or []:
                if block.get("parsed_ok"):
                    for t in _extract_types(block.get("value")):
                        types_seen.add(t.lower())

            pt = p.get("page_type")
            if pt == "article" or "article" in types_seen or "newsarticle" in types_seen:
                article_count += 1

        if "product" in types_seen or has_cart or any("/product" in path or "/shop" in path for path in paths):
            self._site_type = "ecommerce"
        elif "softwareapplication" in types_seen or (has_pricing and has_docs):
            self._site_type = "saas"
        elif "localbusiness" in types_seen:
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


# --------------------------------------------------------------------------
# Helpers copied verbatim from crawl-access-audit/scripts/check_access.py
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
# JSON-LD & normalization helpers
# --------------------------------------------------------------------------

def _root_entities(value) -> list[dict]:
    """Return top-level entity dictionaries from a JSON-LD block."""
    if isinstance(value, dict):
        if "@graph" in value and isinstance(value["@graph"], list):
            return [x for x in value["@graph"] if isinstance(x, dict)]
        return [value]
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    return []


def _extract_types(node) -> list[str]:
    """Recursively collect all @type strings from a JSON-LD structure."""
    out = []
    if isinstance(node, dict):
        t = node.get("@type")
        if isinstance(t, str):
            out.append(t)
        elif isinstance(t, list):
            out.extend(x for x in t if isinstance(x, str))
        for v in node.values():
            out.extend(_extract_types(v))
    elif isinstance(node, list):
        for item in node:
            out.extend(_extract_types(item))
    return out


def _build_id_graph(nodes: list[dict]) -> dict[str, dict]:
    """Index all entities with an @id URI to resolve graph inheritance."""
    graph: dict[str, dict] = {}

    def _walk(obj):
        if isinstance(obj, dict):
            obj_id = obj.get("@id")
            if isinstance(obj_id, str) and obj_id:
                graph[obj_id] = obj
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    for n in nodes:
        _walk(n)
    return graph


def _resolve_property(entity: dict, prop: str, graph: dict[str, dict]):
    """Fetch property value directly or via referenced @id entity."""
    if prop in entity and entity[prop] is not None:
        return entity[prop]
    ref = entity.get("@id")
    if isinstance(ref, str) and ref in graph:
        target = graph[ref]
        if prop in target and target[prop] is not None:
            return target[prop]
    return None


def _clean_text(s: str) -> str:
    """Normalize unicode, whitespace, and HTML entities."""
    if not s:
        return ""
    text = html.unescape(s)
    text = unicodedata.normalize("NFKD", text)
    return " ".join(text.split())


def _normalize_currency(curr: str) -> str:
    curr = curr.strip().upper()
    return CURRENCY_SYMBOLS.get(curr, curr)


def _parse_price_amount(val) -> float | None:
    """Parse numeric price safely."""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        cleaned = re.sub(r"[^\d.]", "", val.replace(",", ""))
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_parse_001(b: Bundle) -> list[dict]:
    """The site publishes no structured data at all."""
    pages = b.ok_pages
    if not pages:
        return []

    pages_with_markup = []
    for page in pages:
        ext = b.extracted(page["page_id"])
        has_jsonld = bool(ext.get("jsonld"))
        has_microdata = bool(ext.get("microdata"))
        has_rdfa = bool(ext.get("rdfa"))
        if has_jsonld or has_microdata or has_rdfa:
            pages_with_markup.append(page)

    if pages_with_markup:
        return []

    # Guard: READ-001 supersession is handled by the orchestrator.
    # Severity rule gated by site profile.
    profile = b.site_profile
    if profile in ("ecommerce", "saas", "local-business", "media-publisher", "marketplace"):
        severity = "high"
    elif profile in ("docs", "nonprofit-gov"):
        severity = "medium"
    elif profile == "portfolio-brochure":
        severity = "low"
    else:
        severity = "medium"

    m = len(pages)
    evidence = f"0 of {m} sampled pages contain any JSON-LD, microdata or RDFa."
    refs = ["MANIFEST.json"] + [f"pages/{p['page_id']}/extracted.json" for p in pages[:5]]

    return [finding(
        "PARSE-001", "The site publishes no structured data at all", severity,
        evidence, refs,
        pages=[p["url"] for p in pages],
        counts={"pages_without_markup": m, "sampled": m},
        verification=f"curl -s {b.origin}/ | grep -c 'application/ld+json'",
        scope="site-wide", checked=m,
        action=act(
            "Add schema.org JSON-LD structured data to key templates",
            severity,
            ["Define a canonical Organization entity for the brand",
             "Add page-specific structured data (Product, Article, FAQPage)",
             "Validate with schema validator before deploying"],
            "M",
            "Structured data gives AI assistants unambiguous facts rather than "
            "forcing them to infer details from unstructured page prose.",
            owner="engineering"))]


def check_parse_002(b: Bundle) -> list[dict]:
    """Structured data is present but does not parse."""
    pages = b.ok_pages
    if not pages:
        return []

    total_blocks = 0
    failing_blocks: list[tuple[dict, str]] = []

    for page in pages:
        ext = b.extracted(page["page_id"])
        blocks = ext.get("jsonld") or []
        total_blocks += len(blocks)
        for block in blocks:
            if not block.get("parsed_ok") or block.get("parse_error"):
                err = str(block.get("parse_error") or "JSON syntax error")
                failing_blocks.append((page, err))

    if not failing_blocks:
        return []

    n = len(failing_blocks)
    affected_pages = sorted({p["url"] for p, _ in failing_blocks})
    affected_pids = sorted({p["page_id"] for p, _ in failing_blocks})

    # Quote actual parser errors verbatim per binding guard
    err_samples = sorted({err for _, err in failing_blocks})
    err_str = "; ".join(err_samples[:3])
    evidence = f"{n} of {total_blocks} JSON-LD blocks fail to parse: {err_str}."

    refs = [f"pages/{pid}/extracted.json" for pid in affected_pids[:5]]

    return [finding(
        "PARSE-002", "Structured data is present but does not parse", "high",
        evidence, refs,
        pages=affected_pages,
        counts={"failing_blocks": n, "total_blocks": total_blocks},
        verification=f"Extract the ld+json block from {affected_pages[0]} and run it through any JSON validator",
        scope="site-wide" if len(affected_pages) >= 3 else "page",
        checked=len(pages),
        action=act(
            "Fix JSON-LD template escaping and syntax errors", "high",
            ["Inspect the template rendering application/ld+json blocks",
             "Ensure quotes and special characters in dynamic fields are properly escaped",
             "Validate all JSON-LD blocks with a strict JSON linter"],
            "S",
            "Broken JSON-LD markup is silently discarded by parsers, paying the engineering "
            "cost of structured data without receiving any of the machine-readability benefit.",
            owner="engineering"))]


def check_parse_003(b: Bundle) -> list[dict]:
    """Structured data uses the wrong type for the page."""
    pages = b.ok_pages
    if not pages:
        return []

    # Map of page types to legitimate page-specific types
    expected_types = {
        "product": {"product", "individualproduct", "productmodel", "productgroup"},
        "category": {"collectionpage", "offercatalog", "itemlist", "categorycodeset"},
        "article": {"article", "newsarticle", "blogposting", "techarticle", "report"},
        "docs": {"techarticle", "apireference", "softwaresourcecode", "howto", "article"},
        "faq": {"faqpage", "qapage"},
        "pricing": {"pricespecification", "offer", "product", "softwareapplication", "service", "aggregateoffer"},
    }

    mismatched = []
    for page in pages:
        ptype = page.get("page_type")
        # Guard: page_type is heuristic. When 'other' or absent, skip this check
        if not ptype or ptype in ("other", "home", "about", "contact", "legal"):
            continue

        allowed_specific = expected_types.get(ptype)
        if not allowed_specific:
            continue

        ext = b.extracted(page["page_id"])
        root_types = []
        for block in ext.get("jsonld") or []:
            if not block.get("parsed_ok"):
                continue
            for ent in _root_entities(block.get("value")):
                raw_t = ent.get("@type")
                if isinstance(raw_t, str):
                    root_types.append(raw_t)
                elif isinstance(raw_t, list):
                    root_types.extend(x for x in raw_t if isinstance(x, str))

        if not root_types:
            continue

        root_types_lower = {t.lower() for t in root_types}
        has_expected = bool(root_types_lower & allowed_specific)
        if has_expected:
            continue

        # Guard: WebPage, WebSite, BreadcrumbList and Organization presence alone is NOT an error
        non_generic = [t for t in root_types if t.lower() not in GENERIC_TYPES]
        if not non_generic:
            continue

        # If a non-generic root type is declared that contradicts the expected type:
        mismatched.append((page, ptype, sorted(set(non_generic))))

    if not mismatched:
        return []

    out = []
    commercial_pages = [m for m in mismatched if m[1] in COMMERCIAL_PAGE_TYPES]
    non_commercial_pages = [m for m in mismatched if m[1] not in COMMERCIAL_PAGE_TYPES]

    for subset, is_commercial in ((commercial_pages, True), (non_commercial_pages, False)):
        if not subset:
            continue
        severity = "high" if is_commercial else "medium"
        affected_urls = [p["url"] for p, _, _ in subset]
        p0, pt0, types0 = subset[0]

        evidence = f"{p0['url']} is a {pt0} page but declares only @type {', '.join(types0)}."
        if len(subset) > 1:
            evidence += f" ({len(subset)} pages similarly mismarked)."

        refs = [f"pages/{p['page_id']}/extracted.json" for p, _, _ in subset[:5]]

        out.append(finding(
            "PARSE-003", "Structured data uses the wrong type for the page", severity,
            evidence, refs,
            pages=affected_urls,
            counts={"mismarked_pages": len(subset)},
            verification=f"Compare the @type on {p0['url']} with what the page is actually about",
            scope="page" if len(affected_urls) < 3 else "section",
            checked=len(pages),
            action=act(
                f"Update schema @type to match {pt0} content", severity,
                [f"Replace conflicting @type with correct schema.org entity ({', '.join(sorted(expected_types[pt0])[:2])})",
                 "Retain Organization or WebSite as linked parent entities via @id"],
                "S",
                "Declaring the wrong type causes AI assistants to miscategorize page content "
                "or ignore key facts that belong to the appropriate schema entity.",
                owner="engineering")))

    return out


def check_parse_004(b: Bundle) -> list[dict]:
    """Structured data omits properties consumers need."""
    pages = b.ok_pages
    if not pages:
        return []

    # Build entity graph for @id inheritance
    all_blocks = []
    for p in pages:
        ext = b.extracted(p["page_id"])
        for blk in ext.get("jsonld") or []:
            if blk.get("parsed_ok") and isinstance(blk.get("value"), (dict, list)):
                all_blocks.append(blk["value"])
    graph = _build_id_graph(all_blocks)

    missing_required = []

    for page in pages:
        ext = b.extracted(page["page_id"])
        for blk in ext.get("jsonld") or []:
            if not blk.get("parsed_ok"):
                continue

            def _inspect(node):
                if not isinstance(node, dict):
                    return
                raw_type = node.get("@type")
                types = [raw_type] if isinstance(raw_type, str) else (raw_type if isinstance(raw_type, list) else [])
                types_lower = {t.lower() for t in types if isinstance(t, str)}

                # Product checks
                if "product" in types_lower:
                    name = _resolve_property(node, "name", graph)
                    offers = _resolve_property(node, "offers", graph)
                    missing = []
                    if not name:
                        missing.append("name")
                    if not offers:
                        missing.append("offers")
                    if missing:
                        missing_required.append((page, "Product", missing))

                # Article checks
                if any(a in types_lower for a in ("article", "newsarticle", "blogposting")):
                    headline = _resolve_property(node, "headline", graph) or _resolve_property(node, "name", graph)
                    if not headline:
                        missing_required.append((page, "Article", ["headline"]))

                # LocalBusiness checks
                if "localbusiness" in types_lower:
                    name = _resolve_property(node, "name", graph)
                    address = _resolve_property(node, "address", graph)
                    missing = []
                    if not name:
                        missing.append("name")
                    if not address:
                        missing.append("address")
                    if missing:
                        missing_required.append((page, "LocalBusiness", missing))

                for v in node.values():
                    if isinstance(v, dict):
                        _inspect(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                _inspect(item)

            _inspect(blk.get("value"))

    if not missing_required:
        return []

    # Group by entity type
    by_type: dict[str, list[tuple[dict, list[str]]]] = {}
    for page, etype, props in missing_required:
        by_type.setdefault(etype, []).append((page, props))

    out = []
    for etype, occurrences in sorted(by_type.items()):
        affected_pages = sorted({p["url"] for p, _ in occurrences})
        affected_pids = sorted({p["page_id"] for p, _ in occurrences})
        all_props = sorted({prop for _, props in occurrences for prop in props})
        p0 = occurrences[0][0]

        evidence = (f"{len(occurrences)} {etype} entities omit {', '.join(all_props)}: "
                    f"e.g. on {p0['url']}.")
        refs = [f"pages/{pid}/extracted.json" for pid in affected_pids[:5]]

        out.append(finding(
            "PARSE-004", "Structured data omits properties consumers need", "high",
            evidence, refs,
            pages=affected_pages,
            counts={"omitting_entities": len(occurrences)},
            verification=f"Inspect the {etype} block on {p0['url']} for the {all_props[0]} field",
            scope="site-wide" if len(affected_pages) >= 3 else "page",
            checked=len(pages),
            action=act(
                f"Populate required properties on {etype} entities", "high",
                [f"Add missing required fields ({', '.join(all_props)}) to {etype} markup",
                 "Inherit common fields via @id references where shared across pages"],
                "S",
                f"Consumers require complete schema records; omitting {all_props[0]} prevents "
                "assistants from resolving specific facts and pricing.",
                owner="engineering")))

    return out


def check_parse_005(b: Bundle) -> list[dict]:
    """The organization entity has no sameAs links."""
    pages = b.ok_pages
    if not pages:
        return []

    missing_pages = []
    for page in pages:
        ext = b.extracted(page["page_id"])
        for blk in ext.get("jsonld") or []:
            if not blk.get("parsed_ok"):
                continue

            def _check_org(node):
                if isinstance(node, dict):
                    t = node.get("@type")
                    types = [t] if isinstance(t, str) else (t if isinstance(t, list) else [])
                    if any(isinstance(x, str) and x.lower() in ("organization", "localbusiness", "corporation") for x in types):
                        same_as = node.get("sameAs")
                        if not same_as or (isinstance(same_as, list) and len(same_as) == 0):
                            missing_pages.append(page)
                    for v in node.values():
                        if isinstance(v, (dict, list)):
                            _check_org(v)
                elif isinstance(node, list):
                    for item in node:
                        _check_org(item)

            _check_org(blk.get("value"))

    if not missing_pages:
        return []

    affected_pages = sorted({p["url"] for p in missing_pages})
    affected_pids = sorted({p["page_id"] for p in missing_pages})
    first_url = affected_pages[0]

    return [finding(
        "PARSE-005", "The organization entity has no sameAs links", "medium",
        f"The Organization entity on {first_url} declares no sameAs array.",
        [f"pages/{pid}/extracted.json" for pid in affected_pids[:5]],
        pages=affected_pages,
        counts={"pages_without_sameas": len(affected_pages)},
        verification=f"Inspect the Organization block on {first_url} for sameAs",
        scope="site-wide" if len(affected_pages) >= 3 else "page",
        checked=len(pages),
        action=act(
            "Add verified sameAs links to the Organization schema", "medium",
            ["Add a sameAs array linking to Wikidata, LinkedIn, and official profiles",
             "Ensure links point only to genuinely controlled brand properties"],
            "S",
            "sameAs is the primary machine-readable bridge between the website and external "
            "knowledge graphs, establishing entity confidence for AI assistants.",
            code='{\n  "@type": "Organization",\n  "sameAs": [\n    "https://www.linkedin.com/company/your-brand",\n    "https://www.wikidata.org/wiki/Q000000"\n  ]\n}\n',
            owner="marketing"))]


def check_parse_006(b: Bundle) -> list[dict]:
    """Entities are not linked into a stable graph."""
    pages = b.ok_pages
    if len(pages) < 2:
        return []

    orgs_by_page: list[tuple[dict, dict]] = []
    for page in pages:
        ext = b.extracted(page["page_id"])
        for blk in ext.get("jsonld") or []:
            if not blk.get("parsed_ok"):
                continue

            def _find_org(node):
                if isinstance(node, dict):
                    t = node.get("@type")
                    types = [t] if isinstance(t, str) else (t if isinstance(t, list) else [])
                    if any(isinstance(x, str) and x.lower() == "organization" for x in types):
                        orgs_by_page.append((page, node))
                    for v in node.values():
                        if isinstance(v, (dict, list)):
                            _find_org(v)
                elif isinstance(node, list):
                    for item in node:
                        _find_org(item)

            _find_org(blk.get("value"))

    if len(orgs_by_page) < 2:
        return []

    # Guard: Repeating an Organization block per page is common and harmless in isolation.
    # Report only when it has no @id AND is combined with inconsistent values across pages.
    no_id_pages = [(p, org) for p, org in orgs_by_page if not org.get("@id")]
    if len(no_id_pages) < 2:
        return []

    # Compare key values across no_id instances
    names = {str(org.get("name") or "").strip().lower() for _, org in no_id_pages}
    urls = {str(org.get("url") or "").strip().lower() for _, org in no_id_pages}

    is_inconsistent = len(names) > 1 or len(urls) > 1
    if not is_inconsistent:
        # Harmless repetition: leave for proactive recommendation PARSE-P01
        return []

    affected_urls = sorted({p["url"] for p, _ in no_id_pages})
    affected_pids = sorted({p["page_id"] for p, _ in no_id_pages})

    return [finding(
        "PARSE-006", "Entities are not linked into a stable graph", "medium",
        f"{len(affected_urls)} pages each declare a separate Organization entity with no @id and conflicting values.",
        [f"pages/{pid}/extracted.json" for pid in affected_pids[:5]],
        pages=affected_urls,
        counts={"conflicting_pages": len(affected_urls)},
        verification=f"Compare the Organization blocks across two pages on the site ({affected_urls[0]} and {affected_urls[1]})",
        scope="site-wide",
        checked=len(pages),
        action=act(
            "Consolidate Organization into a canonical entity with a stable @id", "medium",
            ["Assign a canonical @id URI such as https://example.com/#organization",
             "Reference this @id across other pages instead of redefining conflicting values"],
            "S",
            "A disconnected entity graph forces consumers to guess whether repeated mentions "
            "belong to the same company, eroding trust in the brand's knowledge presence.",
            owner="engineering"))]


def check_parse_007(b: Bundle) -> list[dict]:
    """Structured data contradicts the visible page."""
    pages = b.ok_pages
    if not pages:
        return []

    findings_out = []

    for page in pages:
        ext = b.extracted(page["page_id"])
        text_obj = ext.get("text") or {}
        main_text = _clean_text(text_obj.get("main") or text_obj.get("full") or "")
        if not main_text:
            continue

        jsonld_blocks = ext.get("jsonld") or []
        checked_offers: set[int] = set()

        for blk in jsonld_blocks:
            if not blk.get("parsed_ok"):
                continue

            def _check_node(node, parent=None):
                if not isinstance(node, dict):
                    return

                raw_type = node.get("@type")
                types = [raw_type] if isinstance(raw_type, str) else (raw_type if isinstance(raw_type, list) else [])
                types_lower = {t.lower() for t in types if isinstance(t, str)}

                # 1. Product price check on Offer / AggregateOffer nodes
                if "offer" in types_lower or "aggregateoffer" in types_lower:
                    off_id = id(node)
                    if off_id not in checked_offers:
                        checked_offers.add(off_id)
                        off = node
                        price_val = off.get("price")
                        curr_val = off.get("priceCurrency") or ""
                        low_price = off.get("lowPrice")
                        high_price = off.get("highPrice")

                        num_price = _parse_price_amount(price_val)
                        num_low = _parse_price_amount(low_price)
                        num_high = _parse_price_amount(high_price)

                        # Match against visible numbers near product/plan name if available
                        prod_name = str(node.get("name") or (parent.get("name") if isinstance(parent, dict) else "") or "").strip()
                        target_text = main_text
                        if prod_name:
                            name_clean = _clean_text(prod_name).lower()
                            idx = target_text.lower().find(name_clean[:20])
                            if idx != -1:
                                target_text = target_text[idx:idx + 300]

                        # Extract visible prices from target text
                        found_prices = re.findall(r"(?:GBP|USD|EUR|£|\$|€)\s*(\d+(?:\.\d{2})?)|(\d+(?:\.\d{2})?)\s*(?:GBP|USD|EUR)", target_text)
                        vis_nums = []
                        for m1, m2 in found_prices:
                            val_str = m1 or m2
                            p = _parse_price_amount(val_str)
                            if p is not None:
                                vis_nums.append(p)

                        if vis_nums and num_price is not None:
                            # Guard: check lowPrice/highPrice range consistency
                            is_in_range = False
                            if num_low is not None and num_high is not None:
                                is_in_range = any(num_low <= v <= num_high for v in vis_nums)
                            elif num_low is not None:
                                is_in_range = any(v >= num_low for v in vis_nums)
                            elif num_price in vis_nums:
                                is_in_range = True

                            if not is_in_range:
                                # Direct contradiction found!
                                vis_display = f"{vis_nums[0]:.2f}" if vis_nums[0] != int(vis_nums[0]) else str(int(vis_nums[0]))
                                mk_display = f"{num_price:.2f}" if num_price != int(num_price) else str(int(num_price))
                                curr_disp = _normalize_currency(curr_val)

                                evidence = (f"{page['url']} marks up price as {mk_display} {curr_disp} "
                                            f"but the page text states {curr_disp} {vis_display}.")
                                findings_out.append(finding(
                                    "PARSE-007", "Structured data contradicts the visible page", "high",
                                    evidence, [f"pages/{page['page_id']}/extracted.json"],
                                    pages=[page["url"]],
                                    counts={"markup_price": num_price, "visible_price": vis_nums[0]},
                                    verification=f"Compare the price in the ld+json block on {page['url']} with the visible page",
                                    scope="page",
                                    checked=len(pages),
                                    action=act(
                                        "Align structured data pricing with visible page text", "high",
                                        ["Update the JSON-LD price or Offer properties to match displayed pricing",
                                         "If pricing varies, use AggregateOffer with lowPrice and highPrice"],
                                        "S",
                                        "Contradictions between markup and visible text cause LLMs and search engines "
                                        "to mistrust and discount the site's factual claims entirely.",
                                        owner="engineering")))

                # 2. Founding date / year check on Organization
                if "organization" in types_lower:
                    fdate = node.get("foundingDate")
                    if isinstance(fdate, (str, int)):
                        fyear = str(fdate)[:4]
                        # Look for "founded in YYYY" in text
                        found_match = re.search(r"founded(?:\s+in)?\s+(\d{4})", main_text, re.IGNORECASE)
                        if found_match:
                            vis_year = found_match.group(1)
                            if fyear != vis_year:
                                evidence = f"{page['url']} marks up foundingDate as {fdate} but the page text states {vis_year}."
                                findings_out.append(finding(
                                    "PARSE-007", "Structured data contradicts the visible page", "high",
                                    evidence, [f"pages/{page['page_id']}/extracted.json"],
                                    pages=[page["url"]],
                                    counts={"markup_founding_year": int(fyear), "visible_founding_year": int(vis_year)},
                                    verification=f"Compare the foundingDate in the ld+json block on {page['url']} with the visible page",
                                    scope="page",
                                    checked=len(pages),
                                    action=act(
                                        "Correct organization founding date in structured data", "high",
                                        [f"Update foundingDate to match visible year ({vis_year})"],
                                        "S",
                                        "Inconsistent facts between schema and page copy damage entity authority.",
                                        owner="engineering")))

                for v in node.values():
                    if isinstance(v, dict):
                        _check_node(v, parent=node)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                _check_node(item, parent=node)

            _check_node(blk.get("value"))

    return findings_out


def check_parse_008(b: Bundle) -> list[dict]:
    """Marked-up content does not appear on the page."""
    pages = b.ok_pages
    if not pages:
        return []

    findings_out = []

    for page in pages:
        ext = b.extracted(page["page_id"])
        # Guard: Do not fire when READ-001 or READ-011 fires (client-side JS rendering / hydration payload)
        signals = ext.get("render_signals") or {}
        if signals.get("app_shell_selectors") or (signals.get("hydration_payload_bytes") or 0) > 40000:
            continue

        text_obj = ext.get("text") or {}
        full_text = (text_obj.get("full") or "").lower()

        jsonld_blocks = ext.get("jsonld") or []
        for blk in jsonld_blocks:
            if not blk.get("parsed_ok"):
                continue

            def _check_hidden(node):
                if not isinstance(node, dict):
                    return

                t = node.get("@type")
                types = [t] if isinstance(t, str) else (t if isinstance(t, list) else [])
                types_lower = {x.lower() for x in types if isinstance(x, str)}

                # AggregateRating check
                if "aggregaterating" in types_lower:
                    rval = str(node.get("ratingValue") or "")
                    rcount = str(node.get("reviewCount") or node.get("ratingCount") or "")
                    has_rating = rval and rval in full_text
                    has_count = rcount and rcount in full_text
                    if not has_rating and not has_count and (rval or rcount):
                        # Guard: AggregateRating from 3rd party widget reported at medium
                        evidence = (f"{page['url']} declares AggregateRating (ratingValue: {rval}, "
                                    f"reviewCount: {rcount}) whose content appears nowhere in the page text.")
                        findings_out.append(finding(
                            "PARSE-008", "Marked-up content does not appear on the page", "medium",
                            evidence, [f"pages/{page['page_id']}/extracted.json"],
                            pages=[page["url"]],
                            verification=f"Search {page['url']} for the text marked up in the AggregateRating block",
                            scope="page",
                            checked=len(pages),
                            action=act(
                                "Surface marked-up ratings as visible text on the page", "medium",
                                ["Display the review count and score visibly near product/service summaries",
                                 "Do not rely solely on an asynchronous widget for core credibility numbers"],
                                "S",
                                "Markup describing content visitors cannot see risks manual search penalties "
                                "and consumer distrust.",
                                owner="engineering")))

                # Review check
                if "review" in types_lower:
                    body = str(node.get("reviewBody") or "").strip()
                    if body and len(body) > 20 and body.lower() not in full_text:
                        evidence = (f"{page['url']} declares Review entities ({body[:40]}...) "
                                    f"whose content appears nowhere in the page text.")
                        findings_out.append(finding(
                            "PARSE-008", "Marked-up content does not appear on the page", "high",
                            evidence, [f"pages/{page['page_id']}/extracted.json"],
                            pages=[page["url"]],
                            verification=f"Search {page['url']} for the text marked up in the Review block",
                            scope="page",
                            checked=len(pages),
                            action=act(
                                "Remove invisible reviews or display review copy on page", "high",
                                ["Display the customer review text on the page or remove the schema snippet"],
                                "S",
                                "Marking up reviews that are not readable on the page violates schema guidelines.",
                                owner="content")))

                for v in node.values():
                    if isinstance(v, dict):
                        _check_hidden(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                _check_hidden(item)

            _check_hidden(blk.get("value"))

    return findings_out


def check_parse_009(b: Bundle) -> list[dict]:
    """Conflicting or duplicated markup formats."""
    pages = b.ok_pages
    if not pages:
        return []

    findings_out = []

    for page in pages:
        ext = b.extracted(page["page_id"])
        jsonld_blocks = ext.get("jsonld") or []
        microdata_blocks = ext.get("microdata") or []

        if not jsonld_blocks or not microdata_blocks:
            continue

        # Extract parsed JSON-LD entity summaries
        j_entities: dict[str, dict] = {}
        for blk in jsonld_blocks:
            if not blk.get("parsed_ok"):
                continue
            val = blk.get("value")
            if isinstance(val, dict):
                t = val.get("@type")
                if isinstance(t, str):
                    j_entities[t.lower()] = val

        # Compare with microdata entities
        for m in microdata_blocks:
            if not isinstance(m, dict):
                continue
            mtype = str(m.get("type") or m.get("@type") or "").split("/")[-1].lower()
            if mtype in j_entities:
                j_obj = j_entities[mtype]
                # Compare fields like name, price
                j_name = str(j_obj.get("name") or "").strip().lower()
                m_name = str(m.get("name") or "").strip().lower()
                if j_name and m_name and j_name != m_name:
                    evidence = (f"{page['url']} declares {mtype} in both JSON-LD and microdata "
                                f"with differing name ({j_name} vs {m_name}).")
                    findings_out.append(finding(
                        "PARSE-009", "Conflicting or duplicated markup formats", "medium",
                        evidence, [f"pages/{page['page_id']}/extracted.json"],
                        pages=[page["url"]],
                        verification=f"Compare the two markup blocks on {page['url']}",
                        scope="page",
                        checked=len(pages),
                        action=act(
                            "Consolidate structured data into a single JSON-LD format", "medium",
                            ["Remove legacy Microdata attributes from HTML tags",
                             "Maintain JSON-LD as the sole source of structured data"],
                            "S",
                            "Conflicting markup formats create ambiguity for crawlers about which "
                            "value represents current canonical truth.",
                            owner="engineering")))

    return findings_out


def check_parse_010(b: Bundle) -> list[dict]:
    """Titles and meta descriptions are missing, duplicated or conflicting."""
    pages = b.ok_pages
    if not pages:
        return []

    findings_out = []
    titles_by_url: dict[str, str] = {}
    h1_by_url: dict[str, str] = {}
    meta_desc_by_url: dict[str, str] = {}

    missing_titles = []
    missing_descs = []

    for page in pages:
        url = page["url"]
        ext = b.extracted(page["page_id"])
        raw_title = ext.get("title") or ""
        titles_by_url[url] = raw_title
        if not raw_title.strip():
            missing_titles.append(page)

        meta = ext.get("meta") or {}
        desc = meta.get("description") or ""
        meta_desc_by_url[url] = desc
        if not desc.strip():
            missing_descs.append(page)

        headings = ext.get("headings") or []
        h1s = [h.get("text", "") for h in headings if h.get("level") == 1]
        h1_by_url[url] = h1s[0] if h1s else ""

    # 1. Missing titles
    if missing_titles:
        evidence = f"{len(missing_titles)} of {len(pages)} pages have no title tag: {', '.join(p['url'] for p in missing_titles[:3])}."
        findings_out.append(finding(
            "PARSE-010", "Titles and meta descriptions are missing, duplicated or conflicting", "medium",
            evidence, [f"pages/{p['page_id']}/extracted.json" for p in missing_titles[:5]],
            pages=[p["url"] for p in missing_titles],
            counts={"missing_titles": len(missing_titles), "sampled": len(pages)},
            verification=f"curl -s {missing_titles[0]['url']} | grep -i '<title>'",
            scope="site-wide" if len(missing_titles) >= 3 else "page",
            checked=len(pages),
            action=act(
                "Add descriptive title tags to all pages", "medium",
                ["Add unique, relevant <title> elements to page templates"],
                "S",
                "The title tag is the principal label used by indexers and AI agents "
                "to understand the topic of a page.",
                owner="seo")))

    # 2. Duplicate titles
    title_groups: dict[str, list[str]] = {}
    for url, t in titles_by_url.items():
        if t.strip():
            title_groups.setdefault(t.strip().lower(), []).append(url)

    dup_groups = {t: urls for t, urls in title_groups.items() if len(urls) > 1}
    if dup_groups:
        total_dup_pages = sorted({u for urls in dup_groups.values() for u in urls})
        sample_title = next(iter(dup_groups.keys()))
        evidence = (f"{len(total_dup_pages)} of {len(pages)} pages share duplicate titles: "
                    f"e.g. {len(dup_groups[sample_title])} pages share '{sample_title[:40]}'.")
        findings_out.append(finding(
            "PARSE-010", "Titles and meta descriptions are missing, duplicated or conflicting", "medium",
            evidence, ["MANIFEST.json"],
            pages=total_dup_pages,
            counts={"duplicated_title_pages": len(total_dup_pages), "sampled": len(pages)},
            verification=f"curl -s {total_dup_pages[0]} | grep -i '<title>'",
            scope="site-wide" if len(total_dup_pages) >= 3 else "section",
            checked=len(pages),
            action=act(
                "Make page titles distinct and unique", "medium",
                ["Ensure every URL template generates a distinct title naming the specific page subject"],
                "S",
                "Duplicated titles cause search engines to treat pages as identical variants.",
                owner="seo")))

    # 3. Substantive conflict between title and h1
    # Guard: A title with a brand suffix that the h1 omits is normal, not a conflict.
    conflicting_h1 = []
    for page in pages:
        url = page["url"]
        t = titles_by_url.get(url, "")
        h1 = h1_by_url.get(url, "")
        if not t or not h1:
            continue

        # Titles carry the brand on either side of the separator: "Buying
        # Guide | Adobe" or "Adobe PDF Print Engine - Buying Guide". Taking the
        # first segment read the second pattern as a conflict on twelve of
        # adobe.com's pages. Use whichever segment agrees with the h1 best.
        clean_h1 = h1.strip().lower()
        segments = [seg.strip().lower() for seg in re.split(r"\s+[|\-—]\s+", t) if seg.strip()]
        h1_words = set(re.findall(r"\w+", clean_h1))
        substantive_title = max(
            segments or [t.strip().lower()],
            key=lambda seg: len(set(re.findall(r"\w+", seg)) & h1_words))

        # If one is contained in the other, they describe the same subject
        if substantive_title in clean_h1 or clean_h1 in substantive_title:
            continue
        # With rapidfuzz present, "Office locations" and "Offices" agree (WRatio
        # 83) while a slogan h1 does not (25); without it the token-overlap rule below.
        rf = _optional("rapidfuzz")
        if rf is not None:
            try:
                if rf.fuzz.WRatio(substantive_title, clean_h1) >= 70:
                    continue
            except Exception:
                pass

        # Acronym expansions (e.g. FAQ -> frequently asked questions)
        acronyms = {
            "faq": ["frequently", "asked", "questions"],
            "faqs": ["frequently", "asked", "questions"],
            "q&a": ["questions", "answers"],
        }
        is_acronym = False
        for acr, words in acronyms.items():
            if acr in substantive_title and all(w in clean_h1 for w in words):
                is_acronym = True
            elif acr in clean_h1 and all(w in substantive_title for w in words):
                is_acronym = True
        if is_acronym:
            continue

        # Token overlap check
        t_tokens = set(re.findall(r"\w+", substantive_title))
        h1_tokens = set(re.findall(r"\w+", clean_h1))
        # Remove common stop words
        stops = {"and", "the", "of", "in", "for", "to", "a", "an", "our", "with", "us"}
        t_core = t_tokens - stops
        h1_core = h1_tokens - stops

        if t_core and h1_core and not (t_core & h1_core):
            # Completely different topics
            conflicting_h1.append((page, substantive_title, clean_h1))

    if conflicting_h1:
        affected_urls = [p["url"] for p, _, _ in conflicting_h1]
        p0, t0, h0 = conflicting_h1[0]
        evidence = (f"{len(conflicting_h1)} of {len(pages)} pages have conflicting title and h1: "
                    f"{p0['url']} title is '{t0[:40]}' but h1 is '{h0[:40]}'.")
        findings_out.append(finding(
            "PARSE-010", "Titles and meta descriptions are missing, duplicated or conflicting", "medium",
            evidence, [f"pages/{p['page_id']}/extracted.json" for p, _, _ in conflicting_h1[:5]],
            pages=affected_urls,
            counts={"conflicting_pages": len(conflicting_h1), "sampled": len(pages)},
            verification=f"curl -s {affected_urls[0]} | grep -E '<title>|<h1'",
            scope="page" if len(affected_urls) < 3 else "section",
            checked=len(pages),
            action=act(
                "Align page title with primary h1 heading", "medium",
                ["Align the title tag with the visible h1 subject matter"],
                "S",
                "When title and h1 contradict each other, search indexers struggle to identify "
                "the true focus of the page.",
                owner="content")))

    return findings_out


def check_parse_011(b: Bundle) -> list[dict]:
    """Social metadata is missing or contradicts the page."""
    pages = b.ok_pages
    if not pages:
        return []

    missing_og = []
    conflicting_og = []

    for page in pages:
        ext = b.extracted(page["page_id"])
        meta = ext.get("meta") or {}
        og_title = meta.get("og:title")
        og_desc = meta.get("og:description")
        page_title = ext.get("title") or ""
        meta_desc = meta.get("description") or ""

        if not og_title or not og_desc:
            missing_og.append(page)
            continue

        # Check for direct contradiction between og:title and page title
        sub_page_title = re.split(r"\s+[|\-—]\s+", page_title)[0].strip().lower()
        sub_og_title = re.split(r"\s+[|\-—]\s+", og_title)[0].strip().lower()

        p_tokens = set(re.findall(r"\w+", sub_page_title)) - {"and", "the", "for", "to", "in", "of"}
        og_tokens = set(re.findall(r"\w+", sub_og_title)) - {"and", "the", "for", "to", "in", "of"}

        if p_tokens and og_tokens and not (p_tokens & og_tokens):
            conflicting_og.append((page, og_title, page_title))

    out = []
    if conflicting_og:
        affected_urls = [p["url"] for p, _, _ in conflicting_og]
        p0, og0, t0 = conflicting_og[0]
        evidence = (f"{len(conflicting_og)} pages declare og:title contradicting page title: "
                    f"{p0['url']} og:title is '{og0[:40]}' but title is '{t0[:40]}'.")
        out.append(finding(
            "PARSE-011", "Social metadata is missing or contradicts the page", "medium",
            evidence, [f"pages/{p['page_id']}/extracted.json" for p, _, _ in conflicting_og[:5]],
            pages=affected_urls,
            counts={"conflicting_og_pages": len(conflicting_og)},
            verification=f"curl -s {affected_urls[0]} | grep -i 'og:title'",
            scope="page" if len(affected_urls) < 3 else "section",
            checked=len(pages),
            action=act(
                "Align og:title tags with page titles", "medium",
                ["Update OpenGraph tags to accurately reflect the page title and summary"],
                "S",
                "Contradictions between social metadata and HTML tags cause preview cards "
                "and assistant summaries to display conflicting snippets.",
                owner="marketing")))

    # Missing og metadata (low severity per rule)
    if missing_og and len(missing_og) == len(pages) and len(pages) >= 3:
        affected_urls = [p["url"] for p in missing_og]
        evidence = f"{len(missing_og)} of {len(pages)} pages omit og:title or og:description tags."
        out.append(finding(
            "PARSE-011", "Social metadata is missing or contradicts the page", "low",
            evidence, [f"pages/{p['page_id']}/extracted.json" for p in missing_og[:5]],
            pages=affected_urls,
            counts={"missing_og_pages": len(missing_og), "sampled": len(pages)},
            verification=f"curl -s {affected_urls[0]} | grep -i 'og:'",
            scope="site-wide",
            checked=len(pages),
            action=act(
                "Add OpenGraph social metadata tags to templates", "low",
                ["Add og:title, og:description, and og:image tags in page head"],
                "S",
                "OpenGraph metadata ensures clean link previews across messaging and AI platforms.",
                owner="marketing")))

    return out


def check_parse_012(b: Bundle) -> list[dict]:
    """Q&A or step-by-step content is not marked up as such."""
    pages = b.ok_pages
    if not pages:
        return []

    qa_candidates = []
    question_regex = re.compile(r"\b(how|what|why|where|when|can\s+i|is\s+there)\b|\?$", re.IGNORECASE)

    for page in pages:
        ext = b.extracted(page["page_id"])
        # Check if already has FAQPage or HowTo
        declared = []
        for blk in ext.get("jsonld") or []:
            if blk.get("parsed_ok"):
                declared.extend(_extract_types(blk.get("value")))
        declared_lower = {t.lower() for t in declared}
        if "faqpage" in declared_lower or "howto" in declared_lower or "qapage" in declared_lower:
            continue

        headings = ext.get("headings") or []
        question_headings = [h.get("text", "") for h in headings if question_regex.search(h.get("text", ""))]

        pt = page.get("page_type")
        # A page is Q&A-shaped when it says so (page_type faq, or /faq in the
        # URL) or when questions dominate its structure. Three question-shaped
        # headings on an ordinary page is editorial style -- curl.se's home and
        # a dozen news explainers fired on that -- and FAQPage markup on an
        # article would be wrong. asana.com/research/faq with twelve is the
        # real case, and it still fires.
        url_says_faq = bool(re.search(r"/faqs?(/|$|\?)|/help/|/support/|/questions",
                                      page.get("final_url") or page.get("url") or "", re.I))
        total_heads = max(1, len(ext.get("headings") or []))
        dominated = (len(question_headings) >= 6
                     and len(question_headings) / total_heads >= 0.5)
        if pt == "faq" or url_says_faq or dominated:
            qa_candidates.append((page, len(question_headings), question_headings))

    if not qa_candidates:
        return []

    p0, n0, _ = qa_candidates[0]
    affected_urls = [p["url"] for p, _, _ in qa_candidates]
    evidence = f"{p0['url']} contains {n0} question-shaped headings with answers but declares no FAQPage entity."

    # Guard: model-judged detection, must NEVER emit critical
    return [finding(
        "PARSE-012", "Q&A or step-by-step content is not marked up as such", "medium",
        evidence, [f"pages/{p['page_id']}/extracted.json" for p, _, _ in qa_candidates[:5]],
        pages=affected_urls,
        counts={"qa_pages_without_markup": len(qa_candidates)},
        determinism="model-judged",
        confidence="medium",
        verification=f"Read {p0['url']} and confirm the content is genuinely Q&A",
        scope="page" if len(affected_urls) < 3 else "section",
        checked=len(pages),
        action=act(
            "Add FAQPage schema markup to Q&A content", "medium",
            ["Mark up question headings and accepted answers with schema.org/FAQPage",
             "Ensure questions represent genuine user inquiries rather than marketing copy"],
            "S",
            "Marking up Q&A content as FAQPage gives retrieval pipelines direct question-answer "
            "pairs to cite in conversational responses.",
            owner="content"))]


def check_parse_013(b: Bundle) -> list[dict]:
    """No breadcrumb markup or navigation."""
    pages = b.ok_pages
    total_pages = max(len(pages), b.coverage.get("pages_discovered", 0))

    # Binding guard: A flat site of under ~20 pages does not need breadcrumbs. Gate on depth.
    if total_pages < 20:
        return []

    # Check maximum path depth
    depths = [len([seg for seg in urlparse(p["url"]).path.strip("/").split("/") if seg]) for p in pages]
    max_depth = max(depths) if depths else 0
    if max_depth < 2:
        return []

    missing = []
    for page in pages:
        # Guard: a breadcrumb shows where a page sits beneath its ancestors. The
        # home page has none, and a top-level page (about, contact, legal) sits
        # directly under home, so there is nothing to show. vox.com carried
        # BreadcrumbList on all 22 of its articles and was reported for the
        # three pages that could not sensibly have one.
        if page.get("page_type") in ("home", "about", "contact", "legal"):
            continue
        depth = len([seg for seg in urlparse(page["url"]).path.strip("/").split("/") if seg])
        if depth < 2:
            continue
        ext = b.extracted(page["page_id"])
        declared = []
        for blk in ext.get("jsonld") or []:
            if blk.get("parsed_ok"):
                declared.extend(_extract_types(blk.get("value")))
        if any(t.lower() == "breadcrumblist" for t in declared):
            continue

        # Also check visible breadcrumb navigation links
        links = ext.get("links") or []
        has_nav_breadcrumb = any(l.get("rel") == "breadcrumb" or "breadcrumb" in (l.get("text") or "").lower() for l in links)
        if not has_nav_breadcrumb:
            missing.append(page)

    # Guard: one or two stray pages are not "no breadcrumb markup". Require a
    # real share of the sample before making a claim about the site.
    if len(missing) < 3 or len(missing) < 0.15 * len(pages):
        return []

    if not missing:
        return []

    severity = "medium" if max_depth >= 3 else "low"
    affected_urls = [p["url"] for p in missing]
    evidence = f"{len(missing)} of {len(pages)} pages declare no BreadcrumbList and show no breadcrumb navigation."

    return [finding(
        "PARSE-013", "No breadcrumb markup or navigation", severity,
        evidence, [f"pages/{p['page_id']}/extracted.json" for p in missing[:5]],
        pages=affected_urls,
        counts={"pages_without_breadcrumbs": len(missing), "sampled": len(pages)},
        verification=f"Open {affected_urls[0]} and look for a breadcrumb trail",
        scope="site-wide" if len(missing) >= 3 else "page",
        checked=len(pages),
        action=act(
            "Add BreadcrumbList structured data and navigation trail", severity,
            ["Render breadcrumb navigation linking parent category paths",
             "Add BreadcrumbList JSON-LD markup indicating hierarchy position"],
            "S",
            "Breadcrumbs state the hierarchical context of deep pages, helping AI agents "
            "understand where facts sit in relation to parent topics.",
            owner="engineering"))]


def check_parse_014(b: Bundle) -> list[dict]:
    """Editorial content declares no author or publisher."""
    profile = b.site_profile
    # Binding guard: applies only to media-publisher, saas, nonprofit-gov
    if profile not in ("media-publisher", "saas", "nonprofit-gov"):
        return []

    pages = b.ok_pages
    # Binding guard: applies only to genuinely editorial pages
    article_pages = [p for p in pages if p.get("page_type") == "article" or "/blog/" in (p.get("url") or "")]
    if not article_pages:
        return []

    missing = []
    for page in article_pages:
        ext = b.extracted(page["page_id"])
        meta = ext.get("meta") or {}
        has_meta_author = bool(meta.get("author") or meta.get("article:author"))
        has_meta_pub = bool(meta.get("publisher") or meta.get("article:publisher"))

        has_schema_author = False
        has_schema_pub = False

        for blk in ext.get("jsonld") or []:
            if not blk.get("parsed_ok"):
                continue

            def _check_author(node):
                nonlocal has_schema_author, has_schema_pub
                if isinstance(node, dict):
                    t = node.get("@type")
                    types = [t] if isinstance(t, str) else (t if isinstance(t, list) else [])
                    if any(isinstance(x, str) and "article" in x.lower() for x in types):
                        if node.get("author"):
                            has_schema_author = True
                        if node.get("publisher"):
                            has_schema_pub = True
                    for v in node.values():
                        if isinstance(v, (dict, list)):
                            _check_author(v)
                elif isinstance(node, list):
                    for item in node:
                        _check_author(item)

            _check_author(blk.get("value"))

        has_author = has_meta_author or has_schema_author
        has_publisher = has_meta_pub or has_schema_pub

        # Binding guard: corporate byline (author = Organization) is legitimate. Report only complete absence.
        if not has_author and not has_publisher:
            missing.append(page)

    if not missing:
        return []

    affected_urls = [p["url"] for p in missing]
    evidence = f"{len(missing)} of {len(article_pages)} article pages declare no author or publisher."

    return [finding(
        "PARSE-014", "Editorial content declares no author or publisher", "medium",
        evidence, [f"pages/{p['page_id']}/extracted.json" for p in missing[:5]],
        pages=affected_urls,
        counts={"unattributed_articles": len(missing), "sampled_articles": len(article_pages)},
        verification=f"Inspect the Article block on {affected_urls[0]} for author and publisher",
        scope="section" if len(affected_urls) < len(pages) else "site-wide",
        checked=len(article_pages),
        action=act(
            "Add author and publisher attribution to editorial articles", "medium",
            ["Add author (Person or Organization) and publisher fields to Article JSON-LD",
             "Include rel=author and meta author tags in the article header"],
            "S",
            "Explicit authorship and publisher attribution are critical trust signals for "
            "AI citation models evaluating source credibility.",
            owner="content"))]


# --------------------------------------------------------------------------
# Proactive recommendations
# --------------------------------------------------------------------------

def proactive(b: Bundle) -> list[dict]:
    """Improvements worth making where no defect was found."""
    out = []
    pages = b.ok_pages
    if not pages:
        return out

    # PARSE-P01: Organization markup exists but is redefined per page
    org_nodes = []
    for page in pages:
        ext = b.extracted(page["page_id"])
        for blk in ext.get("jsonld") or []:
            if blk.get("parsed_ok"):
                for t in _extract_types(blk.get("value")):
                    if t.lower() == "organization":
                        org_nodes.append(blk.get("value"))

    if len(org_nodes) >= 2:
        has_consistent_id = all(isinstance(n, dict) and n.get("@id") for n in org_nodes if isinstance(n, dict))
        if not has_consistent_id:
            out.append({
                "id": "P-000",
                "title": "Publish one canonical Organization entity with a stable @id and link every page to it",
                "category": CATEGORY,
                "mechanism": MECHANISM,
                "rationale": (
                    "Organization markup is repeated across multiple pages without a stable identifier. "
                    "One authoritative entity with a stable identifier lets a consumer resolve every page "
                    "to the same organisation instead of inferring that connection from repeated names."
                ),
                "suggested_action": act(
                    "Assign a canonical @id URI to the Organization entity", "low",
                    ["Add an @id such as https://example.com/#organization to the main Organization block",
                     "Reference this @id in publisher, author, and brand properties on other pages"],
                    "S",
                    "Provides consumers an unambiguous anchor uniting all brand entities into a single graph.",
                    code='{\n  "@context": "https://schema.org",\n  "@type": "Organization",\n  "@id": "https://example.com/#organization",\n  "name": "Your Brand Name"\n}\n',
                    owner="engineering"),
            })

    # PARSE-P02: Mark up the facts buyers ask about, not merely the page type
    has_commercial = any(p.get("page_type") in ("product", "pricing") for p in pages)
    has_offers = False
    for p in pages:
        ext = b.extracted(p["page_id"])
        for blk in ext.get("jsonld") or []:
            if blk.get("parsed_ok"):
                types = {t.lower() for t in _extract_types(blk.get("value"))}
                if "offer" in types or "pricespecification" in types:
                    has_offers = True

    if has_commercial and not has_offers:
        out.append({
            "id": "P-000",
            "title": "Mark up the facts buyers ask about, not merely the page type",
            "category": CATEGORY,
            "mechanism": MECHANISM,
            "rationale": (
                "WebPage markup states that a page exists. Price, availability, location, hours "
                "and eligibility are the facts an assistant is asked for, and each one marked up "
                "is one more question the site can answer directly."
            ),
            "suggested_action": act(
                "Add Offer and pricing structured data to commercial templates", "low",
                ["Add Offer or AggregateOffer entities to pricing and catalog pages",
                 "Mark up price, priceCurrency, and availability"],
                "S",
                "Machine-readable pricing and availability enable assistants to directly answer "
                "purchase inquiries without extracting approximate numbers from prose.",
                owner="engineering"),
        })

    return out


# --------------------------------------------------------------------------
# Registry & Driver
# --------------------------------------------------------------------------

CHECKS = [
    check_parse_001,
    check_parse_002,
    check_parse_003,
    check_parse_004,
    check_parse_005,
    check_parse_006,
    check_parse_007,
    check_parse_008,
    check_parse_009,
    check_parse_010,
    check_parse_011,
    check_parse_012,
    check_parse_013,
    check_parse_014,
]

NOT_YET_IMPLEMENTED: list[str] = []


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
            # One broken check must never lose the other thirteen.
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
        "skill": "structured-data-audit",
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
        print(f"{len(kept)} PARSE candidates -> {args.out}", file=sys.stderr)
        for f in kept:
            print(f"  {f['check_id']:11} {f['severity']:8} {f['title']}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
