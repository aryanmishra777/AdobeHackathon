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
