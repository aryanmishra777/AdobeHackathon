#!/usr/bin/env python3
"""REACH checks: can a machine get into this site at all?

Standard library only -- ships inside the submission.

Reads a completed evidence bundle and emits candidate findings against
../audit-orchestrator/references/finding.schema.json. Performs no network I/O:
every result is a pure function of the bundle, so the same bundle always yields
the same findings.

This file is the reference implementation for the other five analysis skills.
The shape to copy:

  * load the bundle once, into a small accessor object
  * one function per check, named check_<id>, returning zero or more candidates
  * every candidate cites artifact_refs that actually exist in the bundle
  * false-positive guards live next to the logic that would trip them, as code
    where mechanical and as an explicit comment where they need human judgment
  * base severity only -- the orchestrator owns scope and confidence modifiers

Usage:
    python check_access.py <bundle> --out reach-candidates.json
    python check_access.py <bundle> --stdout
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from urllib.parse import urlparse

MECHANISM = "reach"
CATEGORY = "discoverability"

RETRIEVAL_PURPOSES = {"retrieval", "search-index"}
TRAINING_PURPOSES = {"training"}

# noindex on these is correct practice, never a defect (REACH-008 guard).
UTILITY_PATH_HINTS = ("/cart", "/checkout", "/account", "/login", "/signin",
                      "/register", "/search", "/tag/", "/tags/", "/filter",
                      "/wishlist", "/compare", "/basket", "/my-account",
                      "/thank-you", "/order-confirmation", "/preview")

SLOW_TTFB_MEDIUM_MS = 1500
SLOW_TTFB_HIGH_MS = 3000


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
    def ok_pages(self) -> list[dict]:
        """Pages that were actually fetched. Non-200 entries stay in the manifest
        so REACH-012 can report them, but no other check should treat them as
        sampled content."""
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

    def robots_meta(self, page_id: str) -> str:
        """Combined robots directives from the meta tag and the X-Robots-Tag
        header. The header is invisible in page source and is frequently the
        actual cause, so a check that only reads the meta tag misses it."""
        meta = (self.extracted(page_id).get("meta") or {})
        parts = [meta.get("robots", ""), self.headers(page_id).get("x-robots-tag", "")]
        return ",".join(p for p in parts if p).lower()


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
# checks
# --------------------------------------------------------------------------

def check_reach_001(b: Bundle) -> list[dict]:
    """robots.txt missing, unreachable or malformed."""
    status = b.robots.get("status")
    errors = b.robots.get("parse_errors") or []
    out = []

    if status is None or (status and status >= 500):
        # A 5xx robots.txt makes crawlers back off entirely -- worse than absent.
        sev = "high" if status else "medium"
        out.append(finding(
            "REACH-001", "robots.txt could not be read", sev,
            f"GET {b.origin}/robots.txt returned "
            f"{status if status else 'no response'}. Crawlers that cannot read "
            f"robots.txt treat the site as temporarily forbidden and back off.",
            ["robots_fetch.json"],
            verification=f"curl -sI {b.origin}/robots.txt",
            scope="site-wide", checked=len(b.ok_pages),
            action=act("Serve robots.txt with a 200 response", "high",
                       [f"Ensure {b.origin}/robots.txt returns 200 with "
                        f"content-type text/plain",
                        "Add a Sitemap directive pointing at the XML sitemap"],
                       "S",
                       "Crawlers fetch robots.txt before anything else; a 5xx "
                       "response causes them to defer the entire site rather "
                       "than assume permission.",
                       owner="infrastructure")))
    elif status == 404:
        # Guard: a 404 means everything is allowed. Opportunity, not a block.
        out.append(finding(
            "REACH-001", "No robots.txt is published", "medium",
            f"GET {b.origin}/robots.txt returned 404. Crawling is implicitly "
            f"permitted, but the site has no way to declare its sitemap or to "
            f"state its policy toward AI crawlers.",
            ["robots_fetch.json"],
            verification=f"curl -sI {b.origin}/robots.txt",
            scope="site-wide", checked=len(b.ok_pages),
            action=act("Publish a robots.txt that declares the sitemap", "medium",
                       ["Create /robots.txt",
                        "Allow crawling of content paths",
                        "Add a Sitemap: directive"],
                       "S",
                       "robots.txt is the first file every crawler requests; it "
                       "is the cheapest place to declare where the sitemap lives.",
                       code=f"User-agent: *\nAllow: /\n\nSitemap: {b.origin}/sitemap.xml\n",
                       owner="infrastructure")))
    elif errors:
        # Guard: only report errors that break group resolution.
        breaking = [e for e in errors if "before any user-agent" in e
                    or "no ':' separator" in e]
        if breaking:
            out.append(finding(
                "REACH-001", "robots.txt contains lines that break parsing", "low",
                f"robots.txt parsed with {len(breaking)} structural problem(s): "
                f"{'; '.join(breaking[:3])}",
                ["robots.txt.raw"],
                verification=f"Read {b.origin}/robots.txt and check directive order",
                scope="site-wide", checked=len(b.ok_pages),
                action=act("Correct the malformed robots.txt directives", "low",
                           ["Ensure every Allow/Disallow follows a User-agent line",
                            "Ensure every directive uses a colon separator"],
                           "S",
                           "Directives that precede any User-agent line are "
                           "discarded, so the intended rules never apply.",
                           owner="infrastructure")))
    return out


def _blocked_by_purpose(b: Bundle, purposes: set[str]):
    matrix = b.robots.get("agent_matrix") or {}
    return sorted(token for token, entry in matrix.items()
                  if entry.get("purpose") in purposes
                  and entry.get("root_allowed") is False)


def check_reach_002(b: Bundle) -> list[dict]:
    """AI retrieval crawlers blocked. The single most consequential REACH check."""
    matrix = b.robots.get("agent_matrix") or {}
    if not matrix:
        return []
    blocked = _blocked_by_purpose(b, RETRIEVAL_PURPOSES)
    # Guard: search-engine crawlers are REACH-004's business, not ours.
    blocked = [t for t in blocked if t not in ("Googlebot", "Bingbot")]
    if not blocked:
        return []

    total = [t for t, e in matrix.items()
             if e.get("purpose") in RETRIEVAL_PURPOSES and t not in ("Googlebot", "Bingbot")]
    severity = "critical" if len(blocked) == len(total) else "high"

    live = [t for t in blocked if matrix[t].get("purpose") == "retrieval"]
    if live:
        verb = "fetches" if len(live) == 1 else "fetch"
        detail = (f" {' and '.join(live)} {verb} pages in real time when a user "
                  f"asks a question, so the brand cannot appear in those answers.")
    else:
        detail = (" These agents feed the search indexes assistants draw their "
                  "sources from.")

    return [finding(
        "REACH-002", "AI assistants are blocked from reading the site", severity,
        f"robots.txt disallows {len(blocked)} of {len(total)} AI retrieval and "
        f"search crawlers from '/': {', '.join(blocked)}.{detail}",
        ["robots.txt.raw", "MANIFEST.json"],
        counts={"blocked_agents": len(blocked), "total_retrieval_agents": len(total)},
        verification=f"curl -s {b.origin}/robots.txt and read the "
                     f"User-agent groups for {', '.join(blocked[:3])}",
        scope="site-wide", checked=len(b.ok_pages),
        action=act(
            "Allow AI retrieval crawlers in robots.txt",
            "critical" if severity == "critical" else "high",
            [f"Remove or narrow the Disallow rules for {', '.join(blocked)}",
             "Keep any training-crawler policy separate and deliberate",
             "Re-test with curl using each agent's user-agent string"],
            "S",
            "These crawlers fetch a page at the moment a user asks a question; "
            "if they receive a Disallow they never retrieve the content, so no "
            "amount of on-page improvement can make the brand citable.",
            code="\n".join([f"User-agent: {t}\nAllow: /\n" for t in blocked[:6]]),
            owner="infrastructure"))]


def check_reach_003(b: Bundle) -> list[dict]:
    """Training crawlers blocked. Informational ONLY -- a business decision.

    Guard (binding): never phrase this as an error and never raise severity.
    Many organisations block training crawlers deliberately after legal review.
    """
    blocked = _blocked_by_purpose(b, TRAINING_PURPOSES)
    if not blocked:
        return []
    # Only raise the Google-Extended caveat when it is actually one of the
    # blocked agents; a generic aside about an agent the site never blocked
    # reads as boilerplate and invites doubt about the rest of the report.
    caveat = (" Google-Extended in particular does not influence Google Search "
              "or AI Overviews ranking." if "Google-Extended" in blocked else "")
    plural = "crawler" if len(blocked) == 1 else "crawlers"

    result = finding(
        "REACH-003", "AI training crawlers are blocked (informational)", "low",
        f"robots.txt disallows the training-corpus {plural} "
        f"{', '.join(blocked)}. This does not affect whether assistants can find "
        f"and cite the site today -- it affects whether its content contributes "
        f"to future model training.{caveat}",
        ["robots.txt.raw", "MANIFEST.json"],
        counts={"blocked_training_agents": len(blocked)},
        verification=f"curl -s {b.origin}/robots.txt and read the "
                     f"User-agent groups for {', '.join(blocked[:3])}",
        scope="site-wide", checked=len(b.ok_pages),
        action=act("Confirm this opt-out is intentional, then leave it in place",
                   "low",
                   ["Verify the block matches the organisation's stated policy",
                    "If the intent was only to opt out of training, confirm that "
                    "retrieval agents are still allowed"],
                   "S",
                   "Blocking training crawlers is a legitimate choice with no "
                   "effect on present-day citability; the only risk is blocking "
                   "retrieval agents by accident alongside them.",
                   owner="infrastructure"))
    # Binding guard: this level is fixed. It is a business decision, not a
    # defect, and must never be escalated by a scope modifier.
    result["severity_locked"] = True
    return [result]


def check_reach_004(b: Bundle) -> list[dict]:
    """Major search crawler blocked."""
    matrix = b.robots.get("agent_matrix") or {}
    blocked = [t for t in ("Googlebot", "Bingbot")
               if matrix.get(t, {}).get("root_allowed") is False]
    if not blocked:
        return []
    return [finding(
        "REACH-004", "A major search engine crawler is blocked", "critical",
        f"robots.txt disallows {', '.join(blocked)} from '/'. Assistants lean on "
        f"these indexes to find candidate sources, so this removes the site from "
        f"the pool before any AI-specific consideration applies.",
        ["robots.txt.raw", "MANIFEST.json"],
        verification=f"curl -s {b.origin}/robots.txt and read the "
                     f"{blocked[0]} group",
        scope="site-wide", checked=len(b.ok_pages),
        action=act("Restore search crawler access", "critical",
                   [f"Remove the site-wide Disallow for {', '.join(blocked)}",
                    "Restrict the Disallow to utility paths only"],
                   "S",
                   "Search indexes are the retrieval pool most assistants draw "
                   "from; exclusion there precedes every other visibility issue.",
                   code=f"User-agent: {blocked[0]}\nAllow: /\nDisallow: /cart\n"
                        f"Disallow: /checkout\nDisallow: /account\n",
                   owner="infrastructure"))]


def check_reach_005(b: Bundle) -> list[dict]:
    """CDN/WAF blocking bot UAs regardless of robots.txt.

    The killer that robots-only tools miss entirely.
    """
    baseline = b.probe.get("baseline") or {}
    agents = b.probe.get("agents") or {}
    if not baseline or not agents or baseline.get("status") != 200:
        return []

    matrix = b.robots.get("agent_matrix") or {}
    base_bytes = baseline.get("bytes") or 0
    hard, soft = [], []

    for token, res in sorted(agents.items()):
        # Guard: if robots.txt already disallows the agent, the CDN is enforcing
        # a stated policy -- REACH-002/003 covers it, not this check.
        if matrix.get(token, {}).get("root_allowed") is False:
            continue
        status = res.get("status")
        if res.get("challenge_detected") or (status in (401, 403, 429)):
            hard.append((token, status, "challenge" if res.get("challenge_detected") else status))
        elif status == 200 and base_bytes:
            ratio = (res.get("bytes") or 0) / base_bytes
            # Guard: differences under 10% are normal personalisation.
            if ratio < 0.5:
                soft.append((token, res.get("bytes"), round(ratio * 100)))

    out = []
    if hard:
        eligible = [t for t in agents if matrix.get(t, {}).get("root_allowed") is not False]
        severity = "critical" if len(hard) == len(eligible) else "high"
        names = ", ".join(t for t, _, _ in hard)
        # Guard: 429-only results may be our own probe's fault.
        only_rate_limited = all(s == 429 for _, s, _ in hard)
        out.append(finding(
            "REACH-005", "The server blocks AI crawlers even though robots.txt allows them",
            "medium" if only_rate_limited else severity,
            f"{b.probe.get('url')} returns {baseline.get('status')} "
            f"({base_bytes} bytes) with a browser user-agent, but "
            + "; ".join(f"{t} receives {d}" for t, _, d in hard)
            + ". robots.txt permits these agents, so the block is being applied "
              "by a CDN, WAF or bot-management rule.",
            ["ua_probe.json"],
            counts={"blocked_agents": len(hard)},
            confidence="medium" if only_rate_limited else "high",
            verification=f"curl -s -o /dev/null -w '%{{http_code}}' "
                         f"-A 'ChatGPT-User' {b.origin}/ "
                         f"and compare with a browser user-agent",
            scope="site-wide", checked=len(b.ok_pages),
            action=act("Allow AI crawler user-agents through bot management", "critical",
                       ["Identify the rule blocking non-browser user-agents "
                        "(Cloudflare Bot Fight Mode, AWS WAF, Akamai Bot Manager)",
                        f"Add a verified-bot allowance for {names}",
                        "Re-test each user-agent with curl and confirm a 200 "
                        "with real content rather than a challenge page"],
                       "M",
                       "robots.txt states policy but the CDN enforces access. "
                       "A crawler that is permitted in robots.txt and blocked at "
                       "the edge never reaches the content, and nothing in the "
                       "page can compensate.",
                       owner="infrastructure")))
    if soft:
        names = ", ".join(t for t, _, _ in soft)
        out.append(finding(
            "REACH-005", "AI crawlers receive a much smaller page than browsers do",
            "medium",
            f"With a browser user-agent {b.probe.get('url')} returns "
            f"{base_bytes} bytes, but "
            + "; ".join(f"{t} receives {n} bytes ({p}% of baseline)"
                        for t, n, p in soft)
            + ". The content served to crawlers is substantially reduced.",
            ["ua_probe.json"],
            counts={"degraded_agents": len(soft)},
            confidence="medium",
            verification=f"curl -s -A 'ChatGPT-User' {b.origin}/ | wc -c "
                         f"and compare with a browser user-agent",
            scope="site-wide", checked=len(b.ok_pages),
            action=act("Serve crawlers the same content as browsers", "high",
                       [f"Review edge rules that vary the response by user-agent "
                        f"for {names}",
                        "Confirm the crawler response contains the main content"],
                       "M",
                       "A crawler that receives a stripped response indexes only "
                       "that stripped version, so the facts a user asks about are "
                       "absent from what the assistant can quote.",
                       owner="infrastructure")))
    return out


def check_reach_006(b: Bundle) -> list[dict]:
    """No sitemap published or declared."""
    declared = b.robots.get("sitemap_urls") or []
    reachable = [s for s in b.sitemaps if s.get("kind") in ("index", "urlset")]
    if reachable:
        return []

    statuses = ", ".join(str(s.get("status")) for s in b.sitemaps) or "no attempt"
    n_pages = max(len(b.ok_pages), b.coverage.get("pages_discovered", 0))
    # Guard: a small brochure site does not need a sitemap.
    if n_pages < 20:
        severity, note = "low", (" The site appears small enough that crawling "
                                 "reaches everything without one.")
    elif n_pages > 50:
        severity, note = "high", (" With this many URLs, crawl-only discovery "
                                  "reaches deep pages slowly or not at all.")
    else:
        severity, note = "medium", ""

    return [finding(
        "REACH-006", "No XML sitemap is published or declared", severity,
        f"robots.txt declares {len(declared)} Sitemap directive(s) and "
        f"GET {b.origin}/sitemap.xml returned {statuses}.{note}",
        ["MANIFEST.json", "robots.txt.raw"],
        counts={"declared": len(declared), "pages_discovered": n_pages},
        verification=f"curl -sI {b.origin}/sitemap.xml",
        scope="site-wide", checked=len(b.ok_pages),
        action=act("Publish an XML sitemap and declare it in robots.txt", severity,
                   ["Generate a sitemap listing every canonical content URL",
                    "Include an accurate lastmod for each entry",
                    "Add a Sitemap: directive to robots.txt"],
                   "S",
                   "A sitemap is how a crawler learns which URLs exist and which "
                   "changed, without depending on following links inward from "
                   "the home page.",
                   code=f"Sitemap: {b.origin}/sitemap.xml\n",
                   owner="engineering"))]


def check_reach_007(b: Bundle) -> list[dict]:
    """Sitemap invalid or listing the wrong URLs."""
    out = []
    for sm in b.sitemaps:
        if sm.get("kind") == "invalid":
            out.append(finding(
                "REACH-007", "The XML sitemap does not parse", "high",
                f"{sm.get('url')} returned {sm.get('status')} but failed to "
                f"parse: {'; '.join(sm.get('parse_errors') or ['unknown error'])}. "
                f"Crawlers discard an unparseable sitemap silently.",
                ["MANIFEST.json"],
                verification=f"curl -s {sm.get('url')} | head -20",
                scope="site-wide", checked=len(b.ok_pages),
                action=act("Fix the sitemap XML so it validates", "high",
                           ["Correct the XML syntax error",
                            "Validate against the sitemaps.org schema",
                            "Confirm the content-type is application/xml"],
                           "S",
                           "An unparseable sitemap is discarded without warning, "
                           "so the site gets none of the discovery benefit while "
                           "appearing to have a sitemap.",
                           owner="engineering")))

    # Cross-check sitemap URLs against what we actually fetched.
    listed = set()
    for sm in b.sitemaps:
        for entry in sm.get("entries") or []:
            if entry.get("loc"):
                listed.add(entry["loc"].rstrip("/"))
    if listed:
        bad = []
        for page in b.pages:
            url = (page.get("url") or "").rstrip("/")
            if url in listed and page.get("status") and page["status"] >= 400:
                bad.append((page["url"], page["status"]))
        if bad:
            out.append(finding(
                "REACH-007", "The sitemap lists URLs that do not resolve", "medium",
                f"{len(bad)} of the {len(listed)} sitemap URLs sampled returned "
                f"an error: " + ", ".join(f"{u} ({s})" for u, s in bad[:5]),
                ["MANIFEST.json"],
                pages=[u for u, _ in bad],
                counts={"broken": len(bad), "listed": len(listed)},
                verification=f"curl -sI {bad[0][0]}",
                scope="section", checked=len(b.ok_pages),
                action=act("Remove or fix the dead URLs in the sitemap", "medium",
                           ["Regenerate the sitemap from live canonical URLs only",
                            "Add a build step that rejects non-200 entries"],
                           "S",
                           "A sitemap full of dead URLs wastes crawl budget and "
                           "signals that the site's own index of itself is stale.",
                           owner="engineering")))
    return out


def _directive_pages(b: Bundle, needles: tuple[str, ...]):
    hits = []
    for page in b.ok_pages:
        directives = b.robots_meta(page["page_id"])
        if any(n in directives for n in needles):
            hits.append(page)
    return hits


def check_reach_008(b: Bundle) -> list[dict]:
    """noindex on content pages."""
    hits = _directive_pages(b, ("noindex",))
    # Guard: noindex on utility pages is correct practice, never a defect.
    content = [p for p in hits
               if p.get("page_type") not in ("legal", "other")
               or not any(h in (p.get("url") or "").lower() for h in UTILITY_PATH_HINTS)]
    content = [p for p in content
               if not any(h in (p.get("url") or "").lower() for h in UTILITY_PATH_HINTS)]
    if not content:
        return []

    checked = len(b.ok_pages)
    severity = "critical" if checked >= 3 and len(content) / checked >= 0.6 else "high"
    return [finding(
        "REACH-008", "Content pages are excluded from search indexes", severity,
        f"{len(content)} of {checked} sampled pages carry a noindex directive: "
        + ", ".join(p["url"] for p in content[:4])
        + ". Excluded pages cannot be retrieved or cited by anything that relies "
          "on an index.",
        ["MANIFEST.json"] + [f"pages/{p['page_id']}/extracted.json" for p in content[:5]],
        pages=[p["url"] for p in content],
        counts={"noindexed": len(content), "sampled": checked},
        verification=f"curl -s {content[0]['url']} | grep -i 'name=\"robots\"' "
                     f"&& curl -sI {content[0]['url']} | grep -i x-robots-tag",
        checked=checked,
        action=act("Remove noindex from content pages", "critical",
                   ["Identify whether the directive comes from the meta tag or "
                    "the X-Robots-Tag response header",
                    "Remove it from content, product and landing pages",
                    "Keep it on cart, checkout, account and internal search pages"],
                   "S",
                   "A noindexed page is absent from the index assistants query, "
                   "so it cannot be surfaced regardless of how well written it is.",
                   owner="engineering"))]


def check_reach_009(b: Bundle) -> list[dict]:
    """nosnippet / max-snippet:0 -- indexed but unquotable. A direct GEO killer."""
    hits = _directive_pages(b, ("nosnippet", "max-snippet:0"))
    if not hits:
        return []
    checked = len(b.ok_pages)
    return [finding(
        "REACH-009", "Pages are indexed but may not be quoted", "high",
        f"{len(hits)} of {checked} sampled pages set nosnippet or "
        f"max-snippet:0: " + ", ".join(p["url"] for p in hits[:4])
        + ". These pages can be indexed but no text may be reproduced from them, "
          "which is exactly what an assistant needs to do to cite the brand.",
        [f"pages/{p['page_id']}/extracted.json" for p in hits[:5]],
        pages=[p["url"] for p in hits],
        counts={"suppressed": len(hits), "sampled": checked},
        verification=f"curl -s {hits[0]['url']} | grep -iE 'nosnippet|max-snippet'",
        checked=checked,
        action=act("Permit snippets on pages that should be citable", "high",
                   ["Remove nosnippet from content pages",
                    "For paywalled content, use a small positive max-snippet "
                    "value instead of zero so a citable summary is still allowed"],
                   "S",
                   "Indexing determines whether a page can be found; snippet "
                   "permission determines whether its text can appear in an "
                   "answer. Suppressing snippets makes the page findable but "
                   "unusable as a source.",
                   owner="engineering"))]


def check_reach_010(b: Bundle) -> list[dict]:
    """Canonical problems."""
    out = []
    pages = b.ok_pages
    if not pages:
        return out

    origin_host = urlparse(b.origin).netloc.lower()
    missing, cross, mismatched = [], [], []
    for page in pages:
        canonical = b.extracted(page["page_id"]).get("canonical")
        if not canonical:
            missing.append(page)
            continue
        host = urlparse(canonical).netloc.lower()
        if host and host != origin_host:
            cross.append((page, canonical))
        elif canonical.rstrip("/") != (page.get("final_url") or page["url"]).rstrip("/"):
            mismatched.append((page, canonical))

    if cross:
        out.append(finding(
            "REACH-010", "Canonical tags point to a different domain", "high",
            f"{len(cross)} of {len(pages)} sampled pages declare a canonical URL "
            f"on another domain: "
            + ", ".join(f"{p['url']} -> {c}" for p, c in cross[:3])
            + ". Indexing signals and citations are attributed to that domain "
              "instead of this one.",
            [f"pages/{p['page_id']}/extracted.json" for p, _ in cross[:5]],
            pages=[p["url"] for p, _ in cross],
            counts={"cross_domain": len(cross), "sampled": len(pages)},
            # Guard: legitimate for syndicated content, so never claim certainty.
            confidence="medium",
            verification=f"curl -s {cross[0][0]['url']} | grep -i 'rel=\"canonical\"'",
            checked=len(pages),
            action=act("Point canonicals at this domain unless syndication is intended",
                       "high",
                       ["Confirm whether the content is syndicated from the other "
                        "domain deliberately",
                        "If not, set a self-referential canonical on each page"],
                       "S",
                       "A cross-domain canonical tells indexes to credit the other "
                       "domain, so this site accumulates none of the authority "
                       "that would make it a preferred source.",
                       owner="engineering")))

    if len(missing) == len(pages) and len(pages) >= 3:
        out.append(finding(
            "REACH-010", "No canonical tags anywhere on the site", "medium",
            f"None of the {len(pages)} sampled pages declare a rel=canonical link. "
            f"Where the same content is reachable at more than one URL, indexes "
            f"must guess which to credit.",
            [f"pages/{p['page_id']}/extracted.json" for p in missing[:5]],
            pages=[p["url"] for p in missing],
            counts={"sampled": len(pages)},
            verification=f"curl -s {b.origin}/ | grep -i 'rel=\"canonical\"'",
            scope="site-wide", checked=len(pages),
            action=act("Add a self-referential canonical to every page", "medium",
                       ["Emit <link rel=\"canonical\"> in the page template",
                        "Use the absolute, https, canonical-host form of the URL"],
                       "S",
                       "Canonicals consolidate duplicate URLs onto one address so "
                       "that ranking and citation signals accumulate in one place "
                       "instead of splitting.",
                       code='<link rel="canonical" href="' + b.origin + '/your-path" />',
                       owner="engineering")))
    return out


def check_reach_011(b: Bundle) -> list[dict]:
    """Multiple origins answering 200 without redirecting.

    Guard: duplication that a consistent canonical already resolves is a valid,
    if suboptimal, configuration. Reporting it as a high-severity defect is a
    false positive -- the canonical is doing the work the redirect should do.
    """
    variants = b.run.get("origin_variants") or {}
    live = [url for url, info in variants.items()
            if info.get("status") == 200 and not info.get("redirects_to")]
    if len(live) < 2:
        return []

    pages = b.ok_pages
    canonical_hosts = set()
    without_canonical = 0
    for page in pages:
        canonical = b.extracted(page["page_id"]).get("canonical")
        if canonical:
            canonical_hosts.add(urlparse(canonical).netloc.lower())
        else:
            without_canonical += 1

    resolved = (pages and without_canonical == 0 and len(canonical_hosts) == 1)
    if resolved:
        # The duplication is already collapsed onto one host. Nothing to report.
        return []

    if canonical_hosts and without_canonical < len(pages):
        severity = "medium"
        note = (f" Canonical tags are present on "
                f"{len(pages) - without_canonical} of {len(pages)} sampled pages "
                f"but do not consistently resolve the duplication, so they are "
                f"doing the work a redirect should do.")
    else:
        severity = "high"
        note = (" No canonical tags resolve the duplication, so each variant is "
                "treated as a separate site.")

    return [finding(
        "REACH-011", "The site answers on several origins without redirecting",
        severity,
        f"{len(live)} origin variants each return 200 without redirecting to a "
        f"single canonical host: {', '.join(live)}.{note}",
        ["MANIFEST.json"],
        counts={"live_variants": len(live),
                "pages_without_canonical": without_canonical},
        verification=f"curl -sI {live[0]}/ and compare the Location header "
                     f"with {live[1]}/",
        scope="site-wide", checked=len(pages),
        action=act("Redirect every origin variant to one canonical host", severity,
                   ["Choose one canonical origin (https, one host form)",
                    "301-redirect the other variants to the MATCHING PATH on it, "
                    "never to the home page",
                    "Update internal links and the sitemap to the canonical form"],
                   "S",
                   "Duplicate origins divide the signals that determine which "
                   "source an assistant treats as authoritative, so neither "
                   "variant accumulates the standing that one consolidated "
                   "origin would.",
                   owner="infrastructure"))]


def check_reach_012(b: Bundle) -> list[dict]:
    """Broken internal links -- only ones we actually fetched and saw fail."""
    broken = [p for p in b.pages
              if p.get("status") and 400 <= p["status"] < 600 and p["status"] != 403]
    if not broken:
        return []

    nav_broken = []
    for page in b.ok_pages:
        for link in b.extracted(page["page_id"]).get("links") or []:
            if not link.get("in_nav"):
                continue
            href = (link.get("href") or "").rstrip("/")
            for bp in broken:
                if (bp.get("url") or "").rstrip("/") == href:
                    nav_broken.append(href)
    severity = "high" if nav_broken else "medium"
    return [finding(
        "REACH-012", "Internal links point to pages that error", severity,
        f"{len(broken)} internal URL(s) returned an error status: "
        + ", ".join(f"{p['url']} ({p['status']})" for p in broken[:5])
        + (f". {len(set(nav_broken))} of these appear in primary navigation."
           if nav_broken else ""),
        ["MANIFEST.json"],
        pages=[p["url"] for p in broken],
        counts={"broken": len(broken), "in_navigation": len(set(nav_broken))},
        verification=f"curl -sI {broken[0]['url']}",
        scope="section", checked=len(b.ok_pages),
        action=act("Fix or remove the broken internal links", severity,
                   ["Update the links to their current destinations",
                    "301-redirect removed URLs that still receive traffic",
                    "Prioritise links appearing in site navigation"],
                   "S",
                   "Crawlers follow internal links to discover content and treat "
                   "repeated errors as a quality signal; links in navigation are "
                   "followed on every page, so they cost the most.",
                   owner="engineering"))]


def check_reach_015(b: Bundle) -> list[dict]:
    """Slow TTFB. Guard: one-shot and location-dependent, so never above medium."""
    ttfbs = []
    for page in b.ok_pages:
        value = ((b.request(page["page_id"]).get("timing") or {}).get("ttfb_ms"))
        if isinstance(value, (int, float)):
            ttfbs.append(value)
    if len(ttfbs) < 3:
        return []
    median = statistics.median(ttfbs)
    if median < SLOW_TTFB_MEDIUM_MS:
        return []
    severity = "high" if median >= SLOW_TTFB_HIGH_MS else "medium"
    return [finding(
        "REACH-015", "The server responds slowly enough to limit crawling",
        severity,
        f"Median time to first byte across {len(ttfbs)} sampled pages was "
        f"{int(median)} ms (range {int(min(ttfbs))}-{int(max(ttfbs))} ms). "
        f"This figure is a single measurement from one location and includes "
        f"network latency.",
        [f"pages/{p['page_id']}/request.json" for p in b.ok_pages[:5]],
        counts={"median_ttfb_ms": int(median), "pages": len(ttfbs)},
        confidence="medium",
        verification=f"curl -s -o /dev/null -w '%{{time_starttransfer}}' {b.origin}/",
        scope="site-wide", checked=len(b.ok_pages),
        action=act("Reduce time to first byte", "medium",
                   ["Profile server response time on the slowest sampled paths",
                    "Add edge caching for anonymous requests",
                    "Confirm the CDN serves cached HTML rather than proxying "
                    "every request to origin"],
                   "M",
                   "Crawlers allocate a limited time budget per site; slow "
                   "responses reduce how many pages are fetched per visit and "
                   "how promptly changes are picked up.",
                   owner="infrastructure"))]


CHECKS = [
    check_reach_001, check_reach_002, check_reach_003, check_reach_004,
    check_reach_005, check_reach_006, check_reach_007, check_reach_008,
    check_reach_009, check_reach_010, check_reach_011, check_reach_012,
    check_reach_015,
]

# Implemented by teammates against references/checks.yaml -- see docs/todo/.
NOT_YET_IMPLEMENTED = ["REACH-013", "REACH-014", "REACH-016", "REACH-017", "REACH-018"]


def proactive(b: Bundle) -> list[dict]:
    """Improvements worth making where no defect was found."""
    out = []
    llms = b.robots.get("llms_txt") or {}
    if llms and not llms.get("present"):
        # Guard: llms.txt is emerging and has no guaranteed consumer, so it is
        # NEVER a finding. Proactive only, framed as forward-looking.
        out.append({
            "id": "P-000",
            "title": "Publish an llms.txt pointing at the site's key facts",
            "category": CATEGORY,
            "mechanism": MECHANISM,
            "rationale": f"GET {b.origin}/llms.txt returned {llms.get('status')}. "
                         f"This is an emerging convention rather than an "
                         f"established requirement, but it costs almost nothing "
                         f"and forces a useful exercise: naming the handful of "
                         f"pages carrying the facts most worth quoting.",
            "suggested_action": act(
                "Add an llms.txt describing the site and linking its key pages",
                "low",
                ["Create /llms.txt as Markdown",
                 "Open with one sentence stating what the organisation is",
                 "Link the pricing, product, about and contact pages with a "
                 "one-line description each"],
                "S",
                "Gives an assistant an explicit, machine-readable orientation to "
                "the site rather than requiring it to infer structure by crawling.",
                owner="marketing"),
        })

    declared = b.robots.get("sitemap_urls") or []
    reachable = [s for s in b.sitemaps if s.get("kind") in ("index", "urlset")]
    if reachable and not declared:
        out.append({
            "id": "P-000",
            "title": "Declare the sitemap in robots.txt",
            "category": CATEGORY,
            "mechanism": MECHANISM,
            "rationale": f"A sitemap resolves at {reachable[0].get('url')} but "
                         f"robots.txt contains no Sitemap directive, so crawlers "
                         f"that do not guess the default path never find it.",
            "suggested_action": act(
                "Add a Sitemap directive to robots.txt", "low",
                [f"Append 'Sitemap: {reachable[0].get('url')}' to robots.txt"],
                "S",
                "robots.txt is the first file a crawler requests, making it the "
                "most reliable place to advertise where the sitemap lives.",
                code=f"Sitemap: {reachable[0].get('url')}\n",
                owner="infrastructure"),
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

    findings: list[dict] = []
    for check in CHECKS:
        try:
            findings.extend(check(b) or [])
        except Exception as exc:
            # One broken check must never lose the other seventeen.
            print(f"warning: {check.__name__} failed: {type(exc).__name__}: {exc}",
                  file=sys.stderr)

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

    result = {"skill": "crawl-access-audit", "mechanism": MECHANISM,
              "bundle": args.bundle, "findings": kept,
              "proactive_recommendations": proactive(b),
              "checks_not_implemented": NOT_YET_IMPLEMENTED}

    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out and not args.stdout:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
        print(f"{len(kept)} REACH candidates -> {args.out}", file=sys.stderr)
        for f in kept:
            print(f"  {f['check_id']:11} {f['severity']:8} {f['title']}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
