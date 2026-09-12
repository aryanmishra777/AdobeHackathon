"""Deterministic tests for the STAY stage (engagement-audit).

Dev tooling -- outside the submission.

Layer 1, same shape as the other test modules: run the real check script over
the local fixture bundles and assert on the candidates it emits. `clean` is the
false-positive tripwire; `low-engagement` is the positive control for a page top
that says nothing, a dead-end home, an undimensioned hero image and a missing
viewport.

    python tests/make_fixtures.py && python tests/make_bundles.py
    python -m pytest tests/ -k stay -v
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BUNDLES = os.path.join(HERE, "bundles")
CHECK_STAY = os.path.join(REPO, "brand-ai-readiness-audit", "skills",
                          "engagement-audit", "scripts", "check_engagement.py")
MERGE = os.path.join(REPO, "brand-ai-readiness-audit", "skills", "audit-orchestrator",
                     "scripts", "merge_findings.py")

ALL_FIXTURES = ["clean", "js-shell", "blocked-crawlers", "contradictory-markup",
                "stale-content", "unquotable-chunks", "low-engagement"]

REQUIRED = ["id", "check_id", "title", "severity", "confidence", "determinism",
            "category", "mechanism", "evidence", "evidence_detail",
            "affected_scope", "verification", "suggested_action"]


def bundle(name: str) -> str:
    path = os.path.join(BUNDLES, name)
    if not os.path.isdir(path):
        pytest.skip(f"bundle {name!r} not built; run tests/make_bundles.py")
    return path


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, encoding="utf-8")


def stay_output(name: str) -> dict:
    proc = run(CHECK_STAY, bundle(name), "--stdout")
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def stay_findings(name: str) -> list:
    return stay_output(name)["findings"]


# --------------------------------------------------------------------------
# The false-positive tripwire
# --------------------------------------------------------------------------

def test_stay_clean_site_produces_no_serious_findings():
    serious = [f for f in stay_findings("clean")
               if f["severity"] in ("critical", "high")]
    assert not serious, (
        "STAY checks fired on the clean fixture: "
        + "; ".join(f"{f['check_id']} ({f['severity']}) {f['title']}" for f in serious))


def test_stay_clean_site_produces_no_findings_at_all():
    found = stay_findings("clean")
    assert found == [], "; ".join(f"{f['check_id']} {f['title']}" for f in found)


# --------------------------------------------------------------------------
# low-engagement positive control
# --------------------------------------------------------------------------

def test_stay_004_and_009_fire_on_low_engagement():
    ids = {f["check_id"] for f in stay_findings("low-engagement")}
    assert "STAY-004" in ids, "low-engagement must produce STAY-004 (dead-end pages)"
    assert "STAY-009" in ids, "low-engagement must produce STAY-009 (images without dimensions)"


def test_stay_low_engagement_also_flags_orientation_and_viewport():
    """The fixture's own docstring names STAY-001 and STAY-010."""
    ids = {f["check_id"] for f in stay_findings("low-engagement")}
    assert "STAY-001" in ids, "a hero that says nothing must produce STAY-001"
    assert "STAY-010" in ids, "no viewport tag on the home page must produce STAY-010"


def test_stay_low_engagement_findings_are_evidenced():
    for f in stay_findings("low-engagement"):
        assert f["evidence"].strip().lower() != f["title"].strip().lower()
        assert any(ch.isdigit() for ch in f["evidence"]) or f["check_id"] == "STAY-001"


def test_stay_performance_findings_disclaim_core_web_vitals():
    """The registry is emphatic: static proxies, never CWV. STAY-008/009 must say so."""
    for name in ALL_FIXTURES:
        for f in stay_findings(name):
            if f["check_id"] in ("STAY-008", "STAY-009"):
                low = f["evidence"].lower()
                assert ("proxy" in low or "cannot see" in low or "risk" in low), (
                    f"{name}/{f['check_id']} states a proxy figure without disclaiming it")
            if f["check_id"] in ("STAY-008", "STAY-009", "STAY-014"):
                assert f["severity"] in ("low", "medium"), (
                    f"{f['check_id']} exceeded medium on proxy evidence")


def test_stay_low_engagement_survives_the_merge_below_critical():
    cand = os.path.join(HERE, "_stay_cand.json")
    try:
        assert run(CHECK_STAY, bundle("low-engagement"), "--out", cand).returncode == 0
        merged = run(MERGE, cand, "--pages-sampled", "5", "--stdout")
        assert merged.returncode == 0, merged.stderr
        doc = json.loads(merged.stdout)
        got = {f["check_id"] for f in doc["findings"]}
        assert {"STAY-004", "STAY-009"} <= got
        for f in doc["findings"]:
            assert f["severity"] != "critical"
        # the engagement half must appear in the scorecard
        assert "engagement" in doc["scorecard_input"]
    finally:
        if os.path.exists(cand):
            os.remove(cand)


# --------------------------------------------------------------------------
# Contract
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_stay_candidates_are_deterministic(name):
    a = run(CHECK_STAY, bundle(name), "--stdout")
    b = run(CHECK_STAY, bundle(name), "--stdout")
    assert a.returncode == 0 and b.returncode == 0, a.stderr + b.stderr
    assert a.stdout == b.stdout, f"{name}: two runs over one bundle disagreed"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_stay_findings_are_engagement_category(name):
    """The only skill on the engagement half -- every finding must say so."""
    for f in stay_findings(name):
        assert f["category"] == "engagement", f"{f['check_id']} is not category engagement"
        assert f["mechanism"] == "stay"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_stay_findings_cite_resolvable_evidence(name):
    root = bundle(name)
    for f in stay_findings(name):
        refs = f["evidence_detail"]["artifact_refs"]
        assert refs, f"{f['check_id']} cites no artifact"
        for ref in refs:
            assert os.path.exists(os.path.join(root, ref.replace("/", os.sep))), (
                f"{f['check_id']} cites missing {ref}")


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_stay_findings_have_the_schema_fields(name):
    for f in stay_findings(name):
        for key in REQUIRED:
            assert key in f, f"{f.get('check_id')} missing {key!r}"
        assert len(f["evidence"]) >= 20 and len(f["verification"]) >= 15
        assert f["evidence"].strip().lower() != f["title"].strip().lower()
        action = f["suggested_action"]
        for key in ("summary", "priority", "steps", "effort", "impact_rationale"):
            assert key in action, f"{f['check_id']}.suggested_action missing {key!r}"
        assert action["steps"]


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_stay_model_judged_findings_are_never_critical(name):
    for f in stay_findings(name):
        if f["determinism"] == "model-judged":
            assert f["severity"] != "critical", f"{f['check_id']} is model-judged and critical"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_stay_fix_snippets_are_tailored_not_templated(name):
    for f in stay_findings(name):
        code = f["suggested_action"].get("code") or ""
        for placeholder in ("YOUR_", "<your ", "REPLACE_ME", "XXX", "TODO"):
            assert placeholder.lower() not in code.lower(), (
                f"{f['check_id']} ships an untailored snippet containing {placeholder!r}")


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_stay_proactive_recommendations_are_well_formed(name):
    for pr in stay_output(name)["proactive_recommendations"]:
        assert set(pr).issubset(
            {"id", "title", "category", "mechanism", "rationale", "suggested_action"})
        assert pr["id"].startswith("P-") and pr["id"][2:].isdigit()
        assert pr["category"] == "engagement" and pr["mechanism"] == "stay"
        assert 10 <= len(pr["title"]) <= 120 and len(pr["rationale"]) >= 20


def test_stay_shell_bundle_skips_content_checks_not_silently():
    out = stay_output("js-shell")
    skipped = {s["check_id"] for s in out["checks_skipped"]}
    assert "STAY-001" in skipped and "STAY-004" in skipped
    assert out["findings"] == []


def test_stay_all_registry_checks_are_implemented_or_listed():
    assert stay_output("clean")["checks_not_implemented"] == []


def test_stay_001_first_screen_guards():
    """The re-crawled sweep produced 27 high STAY-001 findings. Reading them:
    jvns.ca's "Hey! I'm Julia. Welcome to my blog." fell outside a two-sentence
    window; lua.org's masthead is a logo image; IKEA's "Welcome to IKEA
    Global" names where you are; khanacademy.org served an error shell; the
    allbirds product pages open with a buy box; the BBC home page is a
    masthead over headlines. None is a hero that says nothing."""
    import importlib
    sys.path.insert(0, os.path.dirname(CHECK_STAY))
    mod = importlib.import_module(os.path.basename(CHECK_STAY)[:-3])

    assert mod.FIRST_SCREEN_ERROR_RE.search("A required part of this site couldn't load.")
    assert mod.FIRST_SCREEN_ERROR_RE.search("Something went wrong. Try again")
    assert not mod.FIRST_SCREEN_ERROR_RE.search("We roast coffee for offices.")
    assert mod.BUY_BOX_RE.search("Added to Cart Spend more to earn free shipping!")
    assert mod.BUY_BOX_RE.search("Trino Tubers $16 Add to bag")
    assert not mod.BUY_BOX_RE.search("Our story begins in a barn.")
    for word in ("accelerator", "operating system", "headlines", "furniture", "scripting"):
        assert mod.ORIENTATION_NOUN_RE.search("an open-source " + word), word
    assert mod.NON_ENGLISH_LANG_RE.match("et-EE") and not mod.NON_ENGLISH_LANG_RE.match("en-GB")


def _stay_module():
    import importlib
    sys.path.insert(0, os.path.dirname(CHECK_STAY))
    return importlib.import_module(os.path.basename(CHECK_STAY)[:-3])


def test_stay_007_ignores_loading_overlays_and_hidden_region_pickers():
    """crunchyroll.com's app shell wraps every route in 'erc-scroll-block-overlay'
    while it loads (21 findings); adobe.com's 'modal dexter-Author-Hide' is the
    footer's 'Choose your region' dialog and a hash-opened video dialog."""
    mod = _stay_module()
    for html in ('<div class="erc-scroll-block-overlay"><div class="loading--9nt-6 erc-app-shell">',
                 '<div class="modal dexter-Author-Hide">Language Navigation Choose your region',
                 '<div class="modal"><div class="dexter-Modal_overlay" data-conf-display="onHashChange" aria-label="Typekit Video" role="dialog">'):
        m = mod.INTERSTITIAL_RE.search(html)
        assert m and mod.NOT_AN_INTERSTITIAL_RE.search(html[max(0, m.start() - 300):m.end() + 600]), html
    real = '<div class="newsletter-signup modal" aria-modal="true">Join our list<form>'
    m = mod.INTERSTITIAL_RE.search(real)
    assert m and not mod.NOT_AN_INTERSTITIAL_RE.search(real)


def test_stay_006_does_not_fire_when_links_already_carry_filter_state():
    """nike.in's header search is a script component with no <form>, and its
    own links carry ?f=gender_filter=...; the check reported nine pages as
    discarding filter state."""
    mod = _stay_module()
    assert mod.STATE_PARAM_RE.search("https://www.nike.in/jordan/c/94294?f=gender_filter%3D5197_")
    assert mod.STATE_PARAM_RE.search("https://a.test/search?q=shoes")
    assert mod.STATE_PARAM_RE.search("https://a.test/list?sort=price&page=2")
    assert not mod.STATE_PARAM_RE.search("https://a.test/about?utm_source=x")



def test_stay_007_ignores_hidden_and_drawer_components():
    """boat-lifestyle.com: id="cart-popup" on every page and a
    'covercase-popup__modal hide' on product pages, neither shown on arrival."""
    mod = _stay_module()
    for html in ('<div id="cart-popup" class="popup">',
                 '<div class="covercase-popup__overlay hide"></div><covercase-modal class="covercase-popup__modal hide">'
                 '<div class="covercase-popup-container">',
                 '<div class="search-popup-container" style=" display: none;">'):
        m = mod.INTERSTITIAL_RE.search(html)
        assert m and mod.NOT_AN_INTERSTITIAL_RE.search(html[max(0, m.start() - 300):m.end() + 600]), html


def test_stay_013_accepts_a_placeholder_as_a_weak_label():
    """Wikipedia's menu search box carries placeholder="Search Wikipedia" and
    nothing else; the mechanical check counted it as unlabelled on 25 pages."""
    mod = _stay_module()
    src = open(CHECK_STAY, encoding="utf-8").read()
    assert 'placeholder="[^"]{3,}"' in src
