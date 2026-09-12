"""The optional extras: present, they add evidence; absent, nothing changes.

Dev tooling -- outside the submission.

Each library gets a test that runs when it imports (skips otherwise) and the
whole set gets shadow tests that run the real scripts with every extra
shadowed by a ModuleNotFoundError stub, asserting the stdlib path is taken.
"""
from __future__ import annotations

import datetime
import gzip
import importlib
import io
import json
import os
import re
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REAL = os.path.join(HERE, "fixtures", "real")
SKILLS = os.path.join(REPO, "brand-ai-readiness-audit", "skills")
COLLECT_DIR = os.path.join(SKILLS, "site-evidence-collector", "scripts")
COLLECT = os.path.join(COLLECT_DIR, "collect.py")
CHECK_TRUST = os.path.join(SKILLS, "freshness-corroboration-audit", "scripts", "check_trust.py")
CHECK_ACCESS = os.path.join(SKILLS, "crawl-access-audit", "scripts", "check_access.py")
CHECK_RENDER = os.path.join(SKILLS, "render-extractability-audit", "scripts", "check_render.py")
CHECK_PARSE = os.path.join(SKILLS, "structured-data-audit", "scripts", "check_structured_data.py")
CHECK_QUOTE = os.path.join(SKILLS, "answerability-audit", "scripts", "check_answerability.py")


def _mod(directory, name):
    if directory not in sys.path:
        sys.path.insert(0, directory)
    return importlib.import_module(name)


def fixture(name):
    path = os.path.join(REAL, name + ".html")
    if not os.path.isfile(path):
        pytest.skip(f"real fixture {name!r} missing")
    return io.open(path, encoding="utf-8").read()


# --------------------------------------------------------------------------
# present: each library at its one hook
# --------------------------------------------------------------------------

def test_brotli_body_is_decoded_when_the_library_is_present():
    brotli = pytest.importorskip("brotli")
    collect = _mod(COLLECT_DIR, "collect")
    raw = brotli.compress("<html><body>hello brotli</body></html>".encode())
    body = collect._decode_body(raw, {"Content-Encoding": "br", "Content-Type": "text/html; charset=utf-8"})
    assert "hello brotli" in body
    assert any(k[0] == "brotli" for k in collect._EXTRAS_NOTED)


def test_dateparser_finds_the_nike_offer_expiry():
    pytest.importorskip("dateparser")
    collect = _mod(COLLECT_DIR, "collect")
    html = ("<html><head><title>Nike Welcome Offer T&C</title></head><body><p>Nike App Exclusive Offer. "
            "The offer is valid till 7th September, 2026 11:59 PM. Non-transferable.</p></body></html>")
    ex = collect.extract_page("p", "https://www.nike.in/cp/app-offer-tnc", html, "https://www.nike.in")
    parsed = [d for d in ex["dates"] if d["source"] == "visible-text-parsed"]
    assert parsed and parsed[0]["iso"] == "2026-09-07", ex["dates"]


def test_trust_005_reports_an_expired_offer_from_the_parsed_date():
    trust = _mod(os.path.dirname(CHECK_TRUST), "check_trust")
    ex = {"dates": [{"value": "7th September, 2026 11:59 PM", "iso": "2026-09-07", "source": "visible-text-parsed"}]}
    text = "The offer is valid till 7th September, 2026 11:59 PM. One use per user."
    assert trust._expired_validity(ex, text, datetime.date(2026, 9, 12))[1] == "2026-09-07"
    assert trust._expired_validity(ex, text, datetime.date(2026, 9, 1)) == ()


def test_phonenumbers_rejects_size_runs_and_year_ranges():
    pytest.importorskip("phonenumbers")
    trust = _mod(os.path.dirname(CHECK_TRUST), "check_trust")
    b = type("B", (), {"site": "www.nike.in"})()
    found = trust._phone_candidates("Sizes 28 30 32 34 36 38. Call +91 98765 43210 or 022-6918-1920. "
                                    "He worked there (2007-2010) and through 2019-2020.", b)
    assert "+91 98765 43210" in found and "022-6918-1920" in found
    assert not any("28 30" in f or "2007" in f or "2019" in f for f in found), found
    b_fr = type("B", (), {"site": "www.adobe.com"})()
    assert any("8471200" in f for f in trust._phone_candidates("Paris office Tel: +33 18 8471200", b_fr))


def test_pysbd_sentences_keep_abbreviations_together():
    pytest.importorskip("pysbd")
    trust = _mod(os.path.dirname(CHECK_TRUST), "check_trust")
    sents = trust._sentences("Nike, Inc. is based in the U.S. It sells shoes, e.g. running shoes.")
    assert sents == ["Nike, Inc. is based in the U.S.", "It sells shoes, e.g. running shoes."]


def test_ftfy_flags_mojibake_and_passes_clean_text():
    pytest.importorskip("ftfy")
    render = _mod(os.path.dirname(CHECK_RENDER), "check_render")
    assert render._looks_mojibake("Nike Air Max Plus VII 'Kylian MbappÃ©' running shoes")
    assert not render._looks_mojibake("Nike Air Max Plus VII 'Kylian Mbappé' running shoes")


def test_tldextract_makes_bare_and_www_one_site_and_keeps_other_domains_apart():
    pytest.importorskip("tldextract")
    access = _mod(os.path.dirname(CHECK_ACCESS), "check_access")
    assert access._same_site("crunchyroll.com", "www.crunchyroll.com")
    assert access._same_site("shop.example.co.uk", "www.example.co.uk")
    assert not access._same_site("www.nykaa.com", "www.nike.in")


def test_rapidfuzz_agrees_on_office_locations_versus_offices():
    rf = pytest.importorskip("rapidfuzz")
    assert rf.fuzz.WRatio("office locations", "offices") >= 70
    assert rf.fuzz.WRatio("adobe acrobat standard", "simple tools. powerful pdfs.") < 70
    assert rf.fuzz.WRatio("leaders", "louise pentland") < 70
    src = open(CHECK_PARSE, encoding="utf-8").read()
    assert "WRatio(substantive_title, clean_h1) >= 70" in src


def test_json5_recovers_the_boat_json_ld_and_parse_ok_stays_false():
    pytest.importorskip("json5")
    collect = _mod(COLLECT_DIR, "collect")
    ex = collect.extract_page("p", "https://www.boat-lifestyle.com/products/nirvana-uno",
                              fixture("boat-product-trailing-comma"), "https://www.boat-lifestyle.com")
    blocks = [b for b in ex["jsonld"] if not b["parsed_ok"]]
    assert blocks and blocks[0].get("parsed_with") == "json5"
    assert isinstance(blocks[0]["value"], dict) and "@graph" in blocks[0]["value"]


def test_trafilatura_cleans_prose_but_never_replaces_product_or_category_text():
    pytest.importorskip("trafilatura")
    collect = _mod(COLLECT_DIR, "collect")
    wiki = os.path.join(REPO, ".audit", "en.wikipedia.org-assassins-creed", "run-01", "pages", "p000", "raw.html")
    if os.path.isfile(wiki):
        ex = collect.extract_page("p", "https://en.wikipedia.org/wiki/Assassin's_Creed",
                                  io.open(wiki, encoding="utf-8").read(), "https://en.wikipedia.org")
        ch = collect.chunk_page(ex)
        assert ch["chunk_source"] == "trafilatura"
        assert "[1" not in (ex["text"]["main_clean"] or "")
    for name, url in (("nike-product", "https://www.nike.in/nike-24-7-men-s-shoes/p/27763425"),
                      ("nike-category-noindex", "https://www.nike.in/don-t-lose-your-cool/c/111353")):
        ex = collect.extract_page("p", url, fixture(name), "https://www.nike.in")
        assert collect.chunk_page(ex)["chunk_source"] == "stdlib"


def test_protego_agrees_with_our_parser_on_nike_and_the_stricter_answer_wins(tmp_path):
    pytest.importorskip("protego")
    import argparse
    collect = _mod(COLLECT_DIR, "collect")
    robots = "User-agent: *\nDisallow: /*?root=\nDisallow: /cart\n"
    args = argparse.Namespace(target="https://x.test/", out=str(tmp_path), max_pages=5, timeout=10.0,
                              budget=60.0, concurrency=8, delay=0.0, include=[], exclude=[],
                              renderer="none", render_pages=0, no_probe=True)
    c = collect.Collector(args)
    groups, _, _ = collect.parse_robots(robots)
    _, c.our_group = collect.match_group(groups, "BrandAIReadinessAudit")
    from protego import Protego
    c.protego = Protego.parse(robots)
    assert c.allowed("https://x.test/shoes")
    assert not c.allowed("https://x.test/shoes?root=nav")
    assert not c.allowed("https://x.test/cart")
    # a disagreement takes the stricter reading and is recorded
    c.our_group = None            # our parser now allows everything
    assert not c.allowed("https://x.test/cart")
    assert c.robots_disagreements and "/cart" in c.robots_disagreements[0]


# --------------------------------------------------------------------------
# absent: the stdlib path, through the real scripts
# --------------------------------------------------------------------------

def run(env, *args):
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          encoding="utf-8", env=env)


def test_scripts_take_the_stdlib_path_on_a_bare_install(bare_install):
    probe = ("import sys; sys.path.insert(0, %r); import collect; "
             "print(collect._optional('trafilatura'), collect._optional('dateparser'), "
             "collect._optional('protego'), collect._optional('brotli'))") % COLLECT_DIR
    proc = run(bare_install, "-c", probe)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.split() == ["None", "None", "None", "None"]


def test_bare_install_extracts_and_chunks_from_stdlib(bare_install):
    nike = os.path.join(REAL, "nike-product.html")
    if not os.path.isfile(nike):
        pytest.skip("real fixture missing")
    probe = ("import sys, io, json; sys.path.insert(0, %r); import collect; "
             "html = io.open(%r, encoding='utf-8').read(); "
             "ex = collect.extract_page('p', 'https://www.nike.in/nike-24-7-men-s-shoes/p/27763425', html, 'https://www.nike.in'); "
             "ch = collect.chunk_page(ex); "
             "print(json.dumps({'source': ch['chunk_source'], 'clean': ex['text']['main_clean'], "
             "'parsed': [d for d in ex['dates'] if d['source'] == 'visible-text-parsed'], "
             "'extras': collect._extras_report()}))") % (COLLECT_DIR, nike)
    proc = run(bare_install, "-c", probe)
    assert proc.returncode == 0, proc.stderr
    doc = json.loads(proc.stdout)
    assert doc == {"source": "stdlib", "clean": None, "parsed": [], "extras": []}


def test_bare_install_analyzers_run_on_the_fixture_bundles(bare_install):
    bundle = os.path.join(HERE, "bundles", "clean")
    if not os.path.isdir(bundle):
        pytest.skip("bundle not built")
    for script in (CHECK_ACCESS, CHECK_RENDER, CHECK_PARSE, CHECK_QUOTE, CHECK_TRUST):
        proc = run(bare_install, script, bundle, "--stdout")
        assert proc.returncode == 0, (script, proc.stderr)
        json.loads(proc.stdout)


def test_validator_only_allows_the_declared_extras_behind_guards():
    src = open(os.path.join(REPO, "tools", "validate.py"), encoding="utf-8").read()
    for name in ("trafilatura", "protego", "dateparser", "phonenumbers", "ftfy", "tldextract",
                 "rapidfuzz", "json5", "langdetect", "brotli", "zstandard", "pysbd"):
        assert f'"{name}"' in src
    proc = subprocess.run([sys.executable, os.path.join(REPO, "tools", "validate.py"), "--quiet"],
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stdout + proc.stderr
