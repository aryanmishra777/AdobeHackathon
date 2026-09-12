#!/usr/bin/env python3
"""Crawl the candidate pool and write bench/corpus.yaml with MEASURED labels.

Dev tooling -- outside the submission. Requires PyYAML.

The GEO axis is the one people get wrong by intuition, so this does not ask for
an opinion. It runs the real collector against each candidate and scores the
mechanisms that actually determine whether an assistant can cite a site:

    retrieval crawlers blocked in robots.txt      -40   REACH-002
    CDN/WAF blocks or challenges bot user-agents  -40   REACH-005
    main content absent from the HTML             -30   READ-001
    no structured data on any sampled page        -15   PARSE-001
    passages fail standalone comprehension        -12   QUOTE-001
    no sitemap                                     -5   REACH-006
    no canonical tags                              -5   REACH-010

    geo = good when the score is >= 70, else poor.

Those weights mirror the severity rubric: the two that make a site *unreachable*
dominate, because no amount of on-page quality survives them.

The engagement tier is scored from viewport, in-content linking, page weight and
render-blocking scripts -- static proxies only, never presented as Core Web
Vitals.

    python bench/build_corpus.py                # crawl everything, write corpus
    python bench/build_corpus.py --limit 5      # try a few first
    python bench/build_corpus.py --reuse        # re-score existing snapshots
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import statistics
import subprocess
import sys
import time
from urllib.parse import urlparse

try:
    import yaml
except ImportError:
    print("error: PyYAML required. pip install -r tools/requirements-dev.txt",
          file=sys.stderr)
    raise SystemExit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SNAPSHOTS = os.path.join(HERE, "snapshots")
COLLECT = os.path.join(REPO, "brand-ai-readiness-audit", "skills",
                       "site-evidence-collector", "scripts", "collect.py")

RETRIEVAL = {"retrieval", "search-index"}
GEO_GOOD_THRESHOLD = 70


def slug(url: str) -> str:
    return urlparse(url).netloc.replace(":", "_")


def collect(url: str, out: str, pages: int, budget: int) -> bool:
    # Crawl into a scratch directory and swap it in only on success, so a
    # site that refuses us today does not erase the snapshot we already had.
    fresh = out + ".new"
    if os.path.isdir(fresh):
        shutil.rmtree(fresh)
    proc = subprocess.run(
        [sys.executable, COLLECT, url, "--out", fresh,
         "--max-pages", str(pages), "--budget", str(budget),
         "--delay", "0.5", "--timeout", "12"],
        capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0 or not os.path.isfile(os.path.join(fresh, "MANIFEST.json")):
        shutil.rmtree(fresh, ignore_errors=True)
        return False
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.replace(fresh, out)
    return True


def load(path):
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def measure(bundle: str) -> dict | None:
    """Everything below is read from the bundle. Nothing here is a guess."""
    m = load(os.path.join(bundle, "MANIFEST.json"))
    if not m:
        return None

    pages = [p for p in m.get("pages", []) if p.get("status") == 200]
    all_pages = m.get("pages") or []
    matrix = m.get("robots", {}).get("agent_matrix") or {}

    blocked_retrieval = sorted(
        t for t, e in matrix.items()
        if e.get("purpose") in RETRIEVAL and e.get("root_allowed") is False)
    blocked_training = sorted(
        t for t, e in matrix.items()
        if e.get("purpose") == "training" and e.get("root_allowed") is False)

    probe = m.get("ua_probe") or {}
    baseline = probe.get("baseline") or {}
    base_bytes = baseline.get("bytes") or 0
    # REACH-005 is about DIFFERENTIAL treatment: a browser is served the page
    # and a bot is not. When the browser baseline is itself blocked or
    # challenged, nothing differential has been observed -- the site is refusing
    # us, not refusing bots -- and the check correctly stays silent. Expecting it
    # anyway records the false-positive guard doing its job as a miss, which is
    # how ft.com and quora.com arrived as misses while behaving exactly right.
    baseline_blocked = bool(baseline.get("challenge_detected")) or         baseline.get("status") in (401, 403, 429) or not baseline.get("status")

    challenged, degraded = [], []
    for token, res in (probe.get("agents") or {}).items():
        if baseline_blocked:
            continue  # no browser-versus-bot contrast to draw
        if matrix.get(token, {}).get("root_allowed") is False:
            continue  # robots already states this; not a CDN block
        if res.get("challenge_detected") or res.get("status") in (401, 403, 429):
            challenged.append(f"{token}:{res.get('status')}"
                              + ("/challenge" if res.get("challenge_detected") else ""))
        elif (res.get("status") == 200 and base_bytes
              and (res.get("bytes") or 0) / base_bytes < 0.5):
            # A 200 carrying a fraction of the body is soft-blocking: the crawler
            # is served a stripped page while browsers get the real one.
            pct = round((res.get("bytes") or 0) / base_bytes * 100)
            degraded.append(f"{token}:{pct}%-of-baseline")

    words, jsonld_pages, canonical_pages, viewport_pages = [], 0, 0, 0
    shells, blocking, weights, inlinks, chunk_fail, chunk_total = 0, [], [], [], 0, 0
    titled, described, h1_pages = 0, 0, 0

    for p in pages:
        ex = load(os.path.join(bundle, "pages", p["page_id"], "extracted.json"))
        if not ex:
            continue
        words.append(ex["text"].get("main_word_count") or 0)
        if any(b.get("parsed_ok") for b in ex.get("jsonld") or []):
            jsonld_pages += 1
        if ex.get("canonical"):
            canonical_pages += 1
        if (ex.get("meta") or {}).get("viewport"):
            viewport_pages += 1
        if (ex.get("title") or "").strip():
            titled += 1
        if ((ex.get("meta") or {}).get("description") or "").strip():
            described += 1
        if any(h.get("level") == 1 for h in ex.get("headings") or []):
            h1_pages += 1
        rs = ex.get("render_signals") or {}
        if rs.get("app_shell_selectors") or rs.get("hydration_payload_bytes"):
            shells += 1
        blocking.append(sum(1 for s in ex.get("scripts") or [] if s.get("blocking")))
        weights.append((ex.get("timing") or {}).get("transfer_bytes") or 0)
        inlinks.append(sum(1 for l in ex.get("links") or []
                           if l.get("internal") and not l.get("in_nav")))

        ch = load(os.path.join(bundle, "pages", p["page_id"], "chunks.json")) or {}
        for c in ch.get("chunks") or []:
            if c.get("word_count", 0) < 25:
                continue
            chunk_total += 1
            sig = c.get("signals") or {}
            if not sig.get("names_subject") and (sig.get("leading_pronoun")
                                                 or sig.get("bare_numbers")):
                chunk_fail += 1

    n = len(pages)

    # A site that returned no pages is not automatically unusable. Three very
    # different situations hide behind pages == 0, and only one is a dead end:
    #
    #   browser served, crawlers refused  -> the strongest GEO-poor evidence
    #                                        there is; this IS the finding
    #   everything refused, browser too   -> inconclusive. Our address or agent
    #                                        may be blocked wholesale, so we
    #                                        must not claim a site defect
    #   nothing resolved at all           -> genuinely unusable
    outcome = "measured"
    if n == 0:
        browser_ok = baseline.get("status") == 200
        refused = [p for p in all_pages
                   if p.get("status") in (401, 403, 429)]
        if browser_ok and (challenged or refused):
            outcome = "crawler-refused"
        elif baseline.get("status") in (401, 403, 429) or not baseline.get("status"):
            outcome = "inconclusive"
        else:
            outcome = "unusable"

    med_words = statistics.median(words) if words else 0
    chunk_rate = (chunk_fail / chunk_total) if chunk_total else 0.0
    sitemaps = [s for s in m.get("sitemaps") or []
                if s.get("kind") in ("index", "urlset")]

    # --- the GEO score -------------------------------------------------
    score, reasons = 100, []
    if blocked_retrieval:
        score -= 40
        reasons.append(f"robots.txt blocks {len(blocked_retrieval)} retrieval/search "
                       f"crawler(s) ({', '.join(blocked_retrieval[:3])})")
    if challenged:
        score -= 40
        reasons.append(f"bot user-agents are blocked or challenged at the edge "
                       f"({', '.join(challenged[:3])}) despite robots.txt permitting them")
    elif degraded:
        score -= 30
        reasons.append(f"crawlers are served a stripped page while browsers get the "
                       f"full one ({', '.join(degraded[:3])})")
    # Thin raw HTML is the signal; an app-shell mount only strengthens it. Some
    # client-rendered sites use no recognisable mount id at all, so requiring one
    # let a site returning a single word of body text score as healthy.
    if n and med_words < 40:
        score -= 30
        detail = (f" with an app-shell mount on {shells} of them"
                  if shells else " with no server-rendered body content")
        reasons.append(f"median {int(med_words)} words of body text in the raw HTML "
                       f"across {n} pages{detail}")
    elif n and med_words < 120 and shells / n >= 0.5:
        score -= 30
        reasons.append(f"median {int(med_words)} words of body text in raw HTML across "
                       f"{n} pages with an app-shell mount on {shells}")
    elif n and med_words < 120:
        score -= 15
        reasons.append(f"only {int(med_words)} median words of body text in the raw HTML")
    if n and jsonld_pages == 0:
        score -= 15
        reasons.append(f"no parseable structured data on any of {n} sampled pages")
    if chunk_rate > 0.4:
        score -= 12
        reasons.append(f"{chunk_fail}/{chunk_total} passages neither name their subject "
                       f"nor resolve their opening reference")
    if not sitemaps:
        score -= 5
        reasons.append("no reachable XML sitemap")
    if n and canonical_pages == 0:
        score -= 5
        reasons.append("no canonical tags on any sampled page")
    if outcome == "crawler-refused":
        score = 0
        reasons = [f"the site returns {baseline.get('status')} to a browser "
                   f"user-agent but refuses every crawler request "
                   f"({', '.join(challenged[:4]) or 'all sampled pages 403/401'}), "
                   f"so no page of it can be fetched, read or cited"]
    elif outcome == "inconclusive":
        reasons = [f"inconclusive: the site refused our browser probe as well "
                   f"(baseline {baseline.get('status')}), so we cannot separate "
                   f"a site-level block from our own address being filtered"]
    score = max(0, score)

    # --- engagement tier (static proxies only) --------------------------
    med_block = statistics.median(blocking) if blocking else 0
    med_weight = statistics.median(weights) if weights else 0
    med_inlinks = statistics.median(inlinks) if inlinks else 0
    eng = 100
    if n and viewport_pages < n:
        eng -= 30
    if med_block > 6:
        eng -= 15
    if med_weight > 1_500_000:
        eng -= 15
    if med_inlinks < 3:
        eng -= 15
    if med_words < 120:
        eng -= 20
    tier = "high" if eng >= 80 else ("moderate" if eng >= 55 else "low")

    # --- technical-SEO proxies -----------------------------------------
    # We cannot observe ranking, so this measures the technical hygiene a
    # conventional SEO audit checks. That is the honest comparison to draw:
    # the money quadrant is a site that passes THIS and still fails GEO.
    # Deduct in PROPORTION to what is missing, not in full for any imperfection.
    # A flat penalty makes the score depend on how many pages we sampled: at 5
    # pages bbc.co.uk scored 100, and at 20 pages the same site scored 40, with
    # 16/20 canonicals, 19/20 titles and 18/20 h1s -- hygiene most sites would
    # envy, scored as though it had none. A label that moves with sample size is
    # not a measurement.
    seo_score, seo_reasons = 100.0, []

    def shortfall(covered: int, weight: int, label: str) -> None:
        """Penalise the fraction missing, ignoring a small tail.

        Real sites legitimately have a few pages without a meta description.
        The first 10% is free; beyond that the deduction scales to the gap.
        """
        nonlocal seo_score
        if not n or covered >= n:
            return
        missing = 1.0 - (covered / float(n))
        if missing <= 0.10:
            return
        seo_score -= weight * missing
        seo_reasons.append(f"{label} on only {covered}/{n} pages")

    if not sitemaps:
        seo_score -= 25
        seo_reasons.append("no XML sitemap")
    shortfall(canonical_pages, 20, "canonical tags")
    shortfall(titled, 20, "page titles")
    shortfall(described, 10, "meta descriptions")
    shortfall(h1_pages, 10, "an h1")
    if med_inlinks < 3:
        seo_score -= 10
        seo_reasons.append("sparse in-content internal linking")
    if m.get("robots", {}).get("status") != 200:
        seo_score -= 5
        seo_reasons.append("no robots.txt")
    if outcome in ("crawler-refused", "inconclusive"):
        seo_score, seo_reasons = None, []
    else:
        seo_score = int(round(max(0.0, seo_score)))

    return {
        "pages": n,
        "outcome": outcome,
        "geo_score": score,
        "geo": "good" if score >= GEO_GOOD_THRESHOLD else "poor",
        "reasons": reasons,
        "engagement": tier,
        "seo_score": seo_score,
        "seo_reasons": seo_reasons,
        "blocked_retrieval": blocked_retrieval,
        "blocked_training": blocked_training,
        "challenged": challenged,
        "degraded": degraded,
        "median_words": int(med_words),
        "app_shell_pages": shells,
        "jsonld_pages": jsonld_pages,
        "canonical_pages": canonical_pages,
        "sitemaps": len(sitemaps),
        "chunk_fail": chunk_fail,
        "chunk_total": chunk_total,
        "baseline_status": baseline.get("status"),
        "stopped": (m.get("coverage") or {}).get("stopped_reason"),
    }


def expectations(mm: dict) -> tuple[list[str], list[str]]:
    """check_ids we expect to fire, and ones that firing would be a false
    positive. Derived from the same measurements, so they stay honest."""
    fire, absent = [], []
    if mm["blocked_retrieval"]:
        fire.append("REACH-002")
    else:
        absent.append("REACH-002")
    if mm["blocked_training"]:
        fire.append("REACH-003")
    if mm["challenged"] or mm["degraded"]:
        fire.append("REACH-005")
    else:
        absent.append("REACH-005")
    if not mm["sitemaps"]:
        fire.append("REACH-006")
    # Site-wide scope needs >=3 sampled pages (false-positive gate 5), so a
    # one-page bundle legitimately produces no REACH-010. Expecting it there
    # would record the gate working correctly as a miss.
    if mm["pages"] >= 3 and mm["canonical_pages"] == 0:
        fire.append("REACH-010")
    if mm["pages"] and mm["app_shell_pages"] / mm["pages"] >= 0.5 and mm["median_words"] < 120:
        fire.append("READ-001")
    elif mm["median_words"] > 400:
        absent.append("READ-001")
    if mm["pages"] and mm["jsonld_pages"] == 0:
        fire.append("PARSE-001")
    elif mm["jsonld_pages"] == mm["pages"] and mm["pages"]:
        absent.append("PARSE-001")
    return sorted(set(fire)), sorted(set(absent))


def note(cand: dict, mm: dict, disagrees: bool) -> str:
    bits = [f"Measured {time.strftime('%Y-%m-%d')} from a {mm['pages']}-page crawl "
            f"(GEO score {mm['geo_score']}/100)."]
    if mm["reasons"]:
        bits.append("Mechanisms found: " + "; ".join(mm["reasons"]) + ".")
    else:
        bits.append("No blocking mechanism found: crawlers permitted, content "
                    f"server-rendered ({mm['median_words']} median words), "
                    f"structured data on {mm['jsonld_pages']}/{mm['pages']} pages.")
    if mm["blocked_training"]:
        bits.append(f"Blocks training crawlers ({', '.join(mm['blocked_training'][:4])}) "
                    "-- a deliberate opt-out, not a defect.")
    if disagrees:
        bits.append("NOTE: prior expected the opposite GEO label; the measurement "
                    "governs. Worth a manual look.")
    return " ".join(bits)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--reuse", action="store_true",
                    help="re-score existing snapshots without crawling")
    ap.add_argument("--pages", type=int, default=6)
    ap.add_argument("--budget", type=int, default=50)
    ap.add_argument("--out", default=os.path.join(HERE, "corpus.yaml"))
    args = ap.parse_args(argv)

    doc = yaml.safe_load(io.open(os.path.join(HERE, "candidates.yaml"), encoding="utf-8"))
    cands = doc["candidates"][:args.limit] if args.limit else doc["candidates"]
    os.makedirs(SNAPSHOTS, exist_ok=True)

    rows, excluded = [], []
    for i, c in enumerate(cands, 1):
        name = slug(c["url"])
        bundle = os.path.join(SNAPSHOTS, name)
        print(f"[{i}/{len(cands)}] {c['url']}", flush=True)
        if not args.reuse:
            if not collect(c["url"], bundle, args.pages, args.budget):
                print("    collect failed", flush=True)
                continue
        mm = measure(bundle)
        if not mm or mm["outcome"] == "unusable":
            print(f"    unusable (stopped={mm['stopped'] if mm else 'n/a'})", flush=True)
            continue
        if mm["outcome"] == "inconclusive":
            # Our own address may be filtered. Recording this as a site defect
            # would be exactly the confident false positive the rubric punishes.
            print(f"    INCONCLUSIVE browser probe also refused "
                  f"({mm['baseline_status']}); excluded", flush=True)
            excluded.append((c["url"], "browser probe refused; cannot separate a "
                                       "site block from our address being filtered"))
            continue
        rows.append((c, mm))
        flag = ""
        if mm["outcome"] == "crawler-refused":
            flag = " [SERVES BROWSERS, REFUSES CRAWLERS]"
        elif mm["blocked_retrieval"]:
            flag = " [robots blocks retrieval]"
        elif mm["challenged"]:
            flag = " [edge blocks bots]"
        elif "READ-001" in expectations(mm)[0]:
            flag = " [client-rendered]"
        seo = mm["seo_score"]
        print(f"    geo={mm['geo']:4} geo_score={mm['geo_score']:3} "
              f"seo_score={seo if seo is not None else '--':>3} "
              f"eng={mm['engagement']:8} {mm['pages']}p "
              f"words={mm['median_words']}{flag}", flush=True)

    def seo_label(c, mm):
        """Measured technical-SEO hygiene where we could measure it, otherwise
        the prior. A crawler-refused site yields no pages to measure, and those
        are precisely the well-ranked brands the money quadrant is made of."""
        if mm.get("seo_score") is None:
            return c["seo_prior"]
        return "good" if mm["seo_score"] >= 70 else "poor"

    # Pin the smoke subset: 2 per quadrant, chosen deterministically.
    by_quad = {}
    for c, mm in rows:
        by_quad.setdefault((seo_label(c, mm), mm["geo"]), []).append((c, mm))
    smoke = set()
    for key, group in by_quad.items():
        for c, _mm in sorted(group, key=lambda t: t[0]["url"])[:2]:
            smoke.add(c["url"])

    counts = {}
    entries = []
    for c, mm in rows:
        seo = seo_label(c, mm)
        counts[(seo, mm["geo"])] = counts.get((seo, mm["geo"]), 0) + 1
        fire, absent = expectations(mm)
        e = {"url": c["url"], "seo": seo, "geo": mm["geo"],
             "engagement": mm["engagement"], "site_type": c["site_type"],
             "vertical": c["vertical"], "smoke": c["url"] in smoke,
             "geo_score": mm["geo_score"]}
        if mm.get("seo_score") is not None:
            e["seo_score"] = mm["seo_score"]
        else:
            e["seo_source"] = "prior (site refuses crawlers; nothing to measure)"
        e["measurement"] = mm["outcome"]
        e["notes"] = note(c, mm, False)
        if fire:
            e["expect_findings"] = fire
        if absent:
            e["expect_absent"] = absent
        entries.append(e)

    entries.sort(key=lambda e: (e["seo"], e["geo"], e["url"]))
    body = HEADER + "\nsites:\n\n" + "\n".join(
        "  - " + yaml.dump(e, sort_keys=False, allow_unicode=True,
                           default_flow_style=False, width=74, indent=2)
        .replace("\n", "\n    ").rstrip() + "\n"
        for e in entries)
    if excluded:
        body += ("\n# Excluded, and why. Recorded rather than dropped silently:\n"
                 "# an unexplained gap in the corpus reads as a gap in coverage.\n")
        for url, why in excluded:
            body += "#   " + url + "\n#     " + why + "\n"

    with io.open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)

    print("\nquadrant coverage:")
    for seo in ("good", "poor"):
        for geo in ("good", "poor"):
            print(f"  SEO {seo:4} / GEO {geo:4}  {counts.get((seo, geo), 0):>3}")
    if excluded:
        print("")
        print("excluded as inconclusive: %d" % len(excluded))
        for _url, _why in excluded:
            print("  " + _url)
    print(f"\nsmoke subset: {len(smoke)} sites")
    print(f"wrote {len(rows)} entries -> {args.out}")
    return 0


HEADER = """# Live benchmark corpus -- SEO x GEO test matrix
#
# NOT part of the submission. This is the field-research artifact the handout
# asks for. None of these sites are graded; they exist to prove the marketplace
# generalizes and, critically, that it is not merely an SEO linter.
#
# GENERATED by bench/build_corpus.py from bench/candidates.yaml. Do not hand-edit
# `geo`, `geo_score` or `notes` -- regenerate instead, so every label stays
# traceable to a measurement:
#
#     python bench/build_corpus.py            # re-crawl and re-score
#     python bench/build_corpus.py --reuse    # re-score existing snapshots
#
# `geo` is MEASURED, not assumed. bench/build_corpus.py scores the mechanisms
# that actually decide whether an assistant can cite a site -- retrieval crawlers
# blocked, edge bot-blocking, content missing from the HTML, no structured data,
# passages that collapse when retrieved alone -- and labels `good` at >= 70.
#
# `seo` is also MEASURED, from technical-SEO hygiene: sitemap, canonicals,
# titles, meta descriptions, h1s, internal linking, robots.txt. We cannot observe
# ranking, so this is the honest comparison to draw -- the money quadrant is a
# site that passes conventional technical SEO and still fails GEO. The one
# exception is a site that refuses crawlers entirely: it yields no pages to
# measure, so `seo` falls back to the prior and `seo_source` records that.
#
# `measurement` records how the row was obtained:
#   measured          normal crawl
#   crawler-refused   served browsers, refused every crawler -- the block IS the
#                     finding, so the row is kept rather than discarded
#
#            GEO good              GEO poor
#          +---------------------+---------------------------+
# SEO good | control             | *** THE MONEY QUADRANT *** |
#          | should score well   | ranks well, invisible to   |
#          | on both axes        | assistants. An SEO tool    |
#          |                     | passes these clean.        |
#          |                     | WE MUST NOT.               |
#          +---------------------+---------------------------+
# SEO poor | strong content,     | should score poorly, and   |
#          | weak technical SEO  | our findings should name   |
#          |                     | the mechanism              |
#          +---------------------+---------------------------+
#
# `expect_findings` / `expect_absent` are drift-tolerant smoke signals derived
# from the same measurements, never hard assertions -- live sites change under
# us. Hard assertions belong in tests/ against local fixtures.
"""


if __name__ == "__main__":
    sys.exit(main())
