"""Extraction regression tests over real pages.

Dev tooling -- outside the submission.

Every extractor defect found so far came from a real page that the synthetic
fixtures never imitated. tests/fixtures/real/ holds six of those pages,
trimmed by tests/make_real_fixtures.py (scripts other than JSON-LD and all
styles removed; source and capture date in the leading comment). Each test
asserts the fact that was wrong the first time the marketplace met the page.

When BeautifulSoup is installed the collector's cross-check must agree with
the parser on every one of these pages; when it is not, that test skips.
"""
from __future__ import annotations

import hashlib
import importlib
import io
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REAL = os.path.join(HERE, "fixtures", "real")
SKILLS = os.path.join(REPO, "brand-ai-readiness-audit", "skills")
COLLECT_DIR = os.path.join(SKILLS, "site-evidence-collector", "scripts")
RENDER_DIR = os.path.join(SKILLS, "render-extractability-audit", "scripts")
TRUST_DIR = os.path.join(SKILLS, "freshness-corroboration-audit", "scripts")

SOURCES = {
    "nike-product": "https://www.nike.in/nike-24-7-men-s-shoes/p/27763425",
    "nike-category-noindex": "https://www.nike.in/don-t-lose-your-cool/c/111353",
    "adobe-acrobat-pro": "https://www.adobe.com/in/acrobat/acrobat-pro.html",
    "adobe-offices": "https://www.adobe.com/in/about-adobe/contact/offices.html",
    "crunchyroll-shell": "https://www.crunchyroll.com/videos/popular",
    "adidas-block-page": "https://www.adidas.co.in/",
}


def _mod(directory, name):
    if directory not in sys.path:
        sys.path.insert(0, directory)
    return importlib.import_module(name)


def fixture(name: str) -> str:
    path = os.path.join(REAL, name + ".html")
    if not os.path.isfile(path):
        pytest.skip(f"real fixture {name!r} missing; run tests/make_real_fixtures.py")
    return io.open(path, encoding="utf-8").read()


def extract(name: str) -> dict:
    collect = _mod(COLLECT_DIR, "collect")
    url = SOURCES[name]
    origin = re.match(r"https?://[^/]+", url).group(0)
    return collect.extract_page("p000", url, fixture(name), origin)


def test_nike_product_page_title_links_markup_and_type():
    """The first audit read the title as empty (an <svg><title> after </head>
    won) and found no product links (the <h3> inside each <a> dropped it)."""
    collect = _mod(COLLECT_DIR, "collect")
    ex = extract("nike-product")
    assert ex["title"] == "Buy Nike 24.7 Men's Shoes Online | Nike India"
    assert ex["meta"].get("robots") == "index, follow"
    types = {b["value"].get("@type") for b in ex["jsonld"] if b.get("parsed_ok") and isinstance(b["value"], dict)}
    assert "Product" in types
    assert collect.classify_page_type(SOURCES["nike-product"], ex) == "product"
    assert any(h["level"] == 1 for h in ex["headings"])
    assert "Sold By Nykaa Fashion" in ex["text"]["main"]


def test_nike_category_page_keeps_every_robots_directive_and_product_link():
    """Three robots meta tags: noindex,nofollow twice then index,follow. Last
    wins read the page as indexable; the 36 product anchors wrap an <h3>."""
    collect = _mod(COLLECT_DIR, "collect")
    ex = extract("nike-category-noindex")
    robots = ex["meta"].get("robots") or ""
    assert "noindex" in robots and "index, follow" in robots
    assert ex["title"].startswith("Nike – Official Online Store")
    product_links = [l for l in ex["links"] if re.search(r"/p/\d+", l["href"]) and l["internal"]]
    assert len(product_links) >= 30
    assert any("Nike" in l["text"] for l in product_links)
    assert collect.classify_page_type(SOURCES["nike-category-noindex"], ex) == "category"


def test_crunchyroll_shell_is_thin_says_update_your_browser_and_hashes_stably():
    """One 281 KB document served for 21 routes, 99 words of chrome, and a body
    message for non-JavaScript clients. Two copies differing only by a script
    token must hash identically once scripts are stripped."""
    render = _mod(RENDER_DIR, "check_render")
    ex = extract("crunchyroll-shell")
    assert ex["text"]["main_word_count"] < 120
    assert render.NO_JS_MESSAGE_RE.search(ex["text"]["main"].lower())
    html = fixture("crunchyroll-shell")
    a = html + "<script>window.__CF$cv$params={r:'a3a1132e98436ec5'}</script>"
    b = html + "<script>window.__CF$cv$params={r:'a3a1132eea30441e'}</script>"
    strip = lambda h: re.sub(r"<script\b.*?</script>", "", h, flags=re.S | re.I)
    assert hashlib.sha1(strip(a).encode()).hexdigest() == hashlib.sha1(strip(b).encode()).hexdigest()
    assert a != b


def test_adobe_acrobat_page_carries_placeholders_where_the_price_belongs():
    """The India plan page reaches a machine as an authoring document: merch
    placeholders and fragment URLs, and no rupee price anywhere."""
    ex = extract("adobe-acrobat-pro")
    text = ex["text"]["main"]
    assert "{{annual-paid-monthly-plan-geo-ip}}" in text
    assert "mas-field" in text
    assert "₹" not in text
    assert ex["title"] == "Download Adobe Acrobat Pro: Full PDF software | Adobe Acrobat"
    assert ex["lang"] is None   # 22 of 25 /in/ pages declare no lang


def test_adobe_offices_page_is_a_directory_and_size_runs_are_not_phones():
    trust = _mod(TRUST_DIR, "check_trust")
    assert trust._is_directory_page({"url": SOURCES["adobe-offices"]})
    ex = extract("adobe-offices")
    assert ex["text"]["main"].count("Tel:") >= 20
    assert not trust._looks_like_phone("28 30 32 34 36")
    assert trust._looks_like_phone("+33 18 8471200")


def test_adidas_block_page_is_recognised_as_a_challenge():
    collect = _mod(COLLECT_DIR, "collect")
    body = fixture("adidas-block-page").lower()
    assert any(sig in body for sig in collect.CHALLENGE_SIGNATURES)


@pytest.mark.parametrize("name", sorted(SOURCES))
def test_bs4_crosscheck_agrees_with_the_parser(name):
    """A tree parser sees the SVG title and the anchor-wrapped heading at
    once. When it is installed it must find nothing the parser missed."""
    pytest.importorskip("bs4")
    collect = _mod(COLLECT_DIR, "collect")
    html = fixture(name)
    ex = extract(name)
    diff = collect._crosscheck_with_bs4(html, ex, SOURCES[name])
    assert diff is None, diff


def test_linked_heading_keeps_the_heading():
    """boat-lifestyle.com wraps collection titles as <h1><a href>...</a></h1>.
    The <a> replaced the heading capture and the h1 vanished -- found by the
    bs4 cross-check on its first live run, not by a person."""
    collect = _mod(COLLECT_DIR, "collect")
    html = ('<html><body><h1><a href="/collections/speakers">All Speakers</a></h1>'
            '<h2>Read <a href="/m">more here</a> now</h2>'
            '<a href="/p"><h3>Card</h3>Rs 99</a></body></html>')
    ex = collect.extract_page("p", "https://x.test/", html, "https://x.test")
    assert [(h["level"], h["text"]) for h in ex["headings"]] == \
        [(1, "All Speakers"), (2, "Read more here now"), (3, "Card")]
    assert {l["href"] for l in ex["links"]} == {"https://x.test/collections/speakers",
                                               "https://x.test/m", "https://x.test/p"}
    assert ex["text"]["main"].count("Card") == 1   # emitted once, not by heading and link both


def test_chunker_cuts_at_headings_in_order_not_at_every_recurrence():
    """Splitting on every occurrence of every heading string cut Wikipedia's
    first sentence in half: the h1 'Assassin's Creed' recurs in 'Assassin's
    Creed is a historical ...' and the chunk began 'is a historical'."""
    collect = _mod(COLLECT_DIR, "collect")
    text = ("Assassin's Creed Assassin's Creed is a historical action-adventure video game series. "
            + "It sold well. " * 20 + "Development history The first game began as a Prince of Persia "
            "sequel; Assassin's Creed grew from it. " + "More words here. " * 20)
    ex = {"page_id": "p", "url": "https://x.test/", "title": "Assassin's Creed", "text": {"main": text, "full": text},
          "headings": [{"level": 1, "text": "Assassin's Creed"}, {"level": 2, "text": "Development history"}]}
    chunks = collect.chunk_page(ex)["chunks"]
    starts = [c["text"][:40] for c in chunks]
    assert any(s.startswith("Assassin's Creed is a historical") for s in starts), starts
    assert not any(s.startswith("is a historical") for s in starts), starts
    assert not any(s.startswith("grew from it") for s in starts), starts
    assert [c["heading_path"] for c in chunks][-1] == ["Development history"]


def test_chunker_cuts_long_segments_at_sentence_ends():
    collect = _mod(COLLECT_DIR, "collect")
    text = " ".join(f"Sentence number {i} has exactly seven words." for i in range(120))
    ex = {"page_id": "p", "url": "https://x.test/", "title": "Sentences", "text": {"main": text, "full": text},
          "headings": [{"level": 2, "text": "Sentence number 0"}]}
    chunks = collect.chunk_page(ex)["chunks"]
    assert len(chunks) >= 3
    for c in chunks:
        assert c["text"].endswith("."), c["text"][-40:]
        assert c["text"].startswith(("Sentence", "has exactly")), c["text"][:40]


def test_chunk_signals_ignore_years_and_citation_markers_and_credit_the_page_subject():
    """'released in 2007' and '[17] [18]' are not unlabelled figures, and a
    title such as '10th century BC' must yield subject tokens."""
    collect = _mod(COLLECT_DIR, "collect")
    ex = {"title": "10th century BC - Wikipedia", "headings": [{"level": 1, "text": "10th century BC"}]}
    sig = collect._chunk_signals("The 10th century BC saw the reign of David. [17] [18] It began in 1000 BC "
                                 "and ended in 901 BC; some 12 kingdoms rose. As mentioned above it was long.", ex)
    assert sig["names_subject"] is True
    assert sig["bare_numbers"] == 1          # "12 kingdoms"; the years and [17] [18] do not count
    assert sig["deictic_terms"] == []        # "as mentioned above" is not in the first 25 words
    sig2 = collect._chunk_signals("As mentioned above, the pattern held. " + "Filler text. " * 10, ex)
    assert "as mentioned" in sig2["deictic_terms"]


def test_collector_strips_a_bom_before_robots_comments():
    collect = _mod(COLLECT_DIR, "collect")
    groups, sitemaps, errors = collect.parse_robots("﻿# robots.txt for x\nUser-agent: *\nDisallow: /w/\n")
    assert errors == [] and groups


def test_collector_skips_a_page_whose_canonical_names_a_sampled_page(tmp_path):
    """MediaWiki serves /wiki/1004_BC as 200 with the content and canonical of
    /wiki/1000s_BC_(decade); seven of twenty-five slots were one article."""
    import argparse
    collect = _mod(COLLECT_DIR, "collect")
    out = tmp_path / "b"
    (out / "pages").mkdir(parents=True)
    args = argparse.Namespace(target="https://x.test/", out=str(out), max_pages=25, timeout=10.0,
                              budget=120.0, concurrency=8, delay=0.0, include=[], exclude=[],
                              renderer="none", render_pages=0, no_probe=True)
    c = collect.Collector(args)
    body = '<html><head><title>1000s BC (decade)</title><link rel="canonical" href="https://x.test/wiki/1000s_BC"></head><body><p>' + "decade text " * 60 + "</p></body></html>"
    def fetched(url):
        return collect.Fetched(url=url, final_url=url, status=200, headers={"Content-Type": "text/html"},
                               body=body, redirects=[], ttfb_ms=1.0, total_ms=2.0, error=None, truncated=False)
    first = c.save_page(fetched("https://x.test/wiki/1000s_BC"), "https://x.test/wiki/1000s_BC", "home", "https://x.test")
    second = c.save_page(fetched("https://x.test/wiki/1004_BC"), "https://x.test/wiki/1004_BC", "crawl", "https://x.test")
    assert first is not None and second is None
    assert len(c.pages) == 1
    assert any("by canonical" in s["reason"] for s in c.skipped)

