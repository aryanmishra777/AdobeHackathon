"""Deterministic tests for the QUOTE stage (answerability-audit).

Dev tooling -- outside the submission.

Layer 1, same shape as test_marketplace.py: run the real check script over the
local fixture bundles and assert on the candidates it emits. The clean fixture
is the false-positive tripwire; the unquotable-chunks fixture is the positive
control for QUOTE-001.

    python tests/make_fixtures.py && python tests/make_bundles.py
    python -m pytest tests/ -k quote -v
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
CHECK_QUOTE = os.path.join(REPO, "brand-ai-readiness-audit", "skills",
                           "answerability-audit", "scripts", "check_answerability.py")
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
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


def quote_output(name: str) -> dict:
    proc = run(CHECK_QUOTE, bundle(name), "--stdout")
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def quote_findings(name: str) -> list:
    return quote_output(name)["findings"]


# --------------------------------------------------------------------------
# The false-positive tripwire
# --------------------------------------------------------------------------

def test_quote_clean_site_produces_no_serious_findings():
    serious = [f for f in quote_findings("clean")
               if f["severity"] in ("critical", "high")]
    assert not serious, (
        "QUOTE checks fired on the clean fixture: "
        + "; ".join(f"{f['check_id']} ({f['severity']}) {f['title']}" for f in serious))


def test_quote_clean_site_produces_no_findings_at_all():
    """The clean fixture names its subject in every passage, states its identity
    explicitly, publishes price/contact/hours and uses one consistent name.
    Nothing in the QUOTE registry should have anything to say about it."""
    found = quote_findings("clean")
    assert found == [], "; ".join(f"{f['check_id']} {f['title']}" for f in found)


# --------------------------------------------------------------------------
# QUOTE-001 positive control
# --------------------------------------------------------------------------

def test_quote_001_fires_on_unquotable_chunks():
    ids = {f["check_id"] for f in quote_findings("unquotable-chunks")}
    assert "QUOTE-001" in ids, "unquotable-chunks must produce a QUOTE-001 candidate"


def test_quote_001_is_deterministic_not_critical_and_evidenced():
    f = next(x for x in quote_findings("unquotable-chunks") if x["check_id"] == "QUOTE-001")
    assert f["determinism"] == "deterministic"
    assert f["severity"] in ("medium", "high")  # never critical -- severity_rule
    assert f["severity"] != "critical"
    c = f["evidence_detail"]["counts"]
    assert c["failing_chunks"] >= 2 and c["assessed_chunks"] >= c["failing_chunks"]
    # evidence states an observation with numbers, not a restatement of the title
    assert f["evidence"].strip().lower() != f["title"].strip().lower()
    assert any(ch.isdigit() for ch in f["evidence"])
    assert "pricing.html" in " ".join(f["evidence_detail"]["pages_affected"])


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_quote_001_scope_never_site_wide(name):
    """The orchestrator promotes a site-wide 'high' to 'critical'. QUOTE-001's
    registry rule forbids critical, so the check must cap its own scope at
    'section' -- verify it never emits site-wide."""
    for f in quote_findings(name):
        if f["check_id"] == "QUOTE-001":
            assert f["affected_scope"]["scope"] in ("page", "section"), (
                f"QUOTE-001 emitted scope {f['affected_scope']['scope']!r}; "
                f"a site-wide high would be promoted to critical by the merge")


def test_quote_001_stays_below_critical_through_the_merge():
    """End to end: even a broad QUOTE-001 must not come out of merge_findings.py
    as critical."""
    cand = os.path.join(HERE, "_q001_merge.json")
    try:
        assert run(CHECK_QUOTE, bundle("unquotable-chunks"), "--out", cand).returncode == 0
        merged = run(MERGE, cand, "--pages-sampled", "5", "--stdout")
        assert merged.returncode == 0, merged.stderr
        for f in json.loads(merged.stdout)["findings"]:
            if f["check_id"] == "QUOTE-001":
                assert f["severity"] != "critical"
    finally:
        if os.path.exists(cand):
            os.remove(cand)


def test_quote_shell_pages_record_a_skip_not_silence():
    """js-shell has no assessable content. The content-dependent QUOTE checks
    must be recorded as skipped, so the report can tell 'checked, fine' from
    'never checked' (false-positive-gates.md)."""
    out = quote_output("js-shell")
    skipped = {s["check_id"] for s in out["checks_skipped"]}
    assert "QUOTE-001" in skipped
    assert out["findings"] == []
    for s in out["checks_skipped"]:
        assert s["reason"] and isinstance(s["reason"], str)


def test_quote_clean_site_skips_nothing():
    """A fully-formed site leaves every check able to run."""
    assert quote_output("clean")["checks_skipped"] == []


def test_quote_001_never_rechunks_only_reads_precomputed_signals():
    """QUOTE-001 must be a pure function of chunks.json. Two runs -> identical."""
    a = run(CHECK_QUOTE, bundle("unquotable-chunks"), "--stdout")
    b = run(CHECK_QUOTE, bundle("unquotable-chunks"), "--stdout")
    assert a.returncode == 0 and b.returncode == 0
    assert a.stdout == b.stdout


# --------------------------------------------------------------------------
# Contract: every candidate resolves, fits the schema, respects the ceiling
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_quote_candidates_are_deterministic(name):
    a = run(CHECK_QUOTE, bundle(name), "--stdout")
    b = run(CHECK_QUOTE, bundle(name), "--stdout")
    assert a.returncode == 0 and b.returncode == 0, a.stderr + b.stderr
    assert a.stdout == b.stdout, f"{name}: two runs over one bundle disagreed"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_quote_findings_cite_resolvable_evidence(name):
    root = bundle(name)
    for f in quote_findings(name):
        refs = f["evidence_detail"]["artifact_refs"]
        assert refs, f"{f['check_id']} cites no artifact"
        for ref in refs:
            assert os.path.exists(os.path.join(root, ref.replace("/", os.sep))), (
                f"{f['check_id']} cites missing {ref}")


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_quote_findings_have_the_schema_fields(name):
    for f in quote_findings(name):
        for key in REQUIRED:
            assert key in f, f"{f.get('check_id')} missing {key!r}"
        assert f["mechanism"] == "quote" and f["category"] == "discoverability"
        assert len(f["evidence"]) >= 20 and len(f["verification"]) >= 15
        assert f["evidence"].strip().lower() != f["title"].strip().lower()
        action = f["suggested_action"]
        for key in ("summary", "priority", "steps", "effort", "impact_rationale"):
            assert key in action, f"{f['check_id']}.suggested_action missing {key!r}"
        assert action["steps"]


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_quote_model_judged_findings_are_never_critical(name):
    """False-positive gate 3 -- binds hardest in this skill."""
    for f in quote_findings(name):
        if f["determinism"] == "model-judged":
            assert f["severity"] != "critical", f"{f['check_id']} is model-judged and critical"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_quote_fix_snippets_are_tailored_not_templated(name):
    for f in quote_findings(name):
        code = f["suggested_action"].get("code") or ""
        for placeholder in ("YOUR_", "<your ", "REPLACE_ME", "XXX", "TODO"):
            assert placeholder.lower() not in code.lower(), (
                f"{f['check_id']} ships an untailored snippet containing {placeholder!r}")


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_quote_proactive_recommendations_are_well_formed(name):
    for pr in quote_output(name)["proactive_recommendations"]:
        assert set(pr).issubset(
            {"id", "title", "category", "mechanism", "rationale", "suggested_action"})
        assert pr["id"].startswith("P-") and pr["id"][2:].isdigit()
        assert 10 <= len(pr["title"]) <= 120 and len(pr["rationale"]) >= 20
        assert pr["suggested_action"]["steps"]


def test_quote_all_registry_checks_are_implemented_or_listed():
    """Every QUOTE-nnn in checks.yaml is either implemented or named in
    NOT_YET_IMPLEMENTED with the reason visible in the module."""
    out = quote_output("clean")
    assert out["checks_not_implemented"] == [], (
        "all 12 QUOTE checks are implemented; nothing should be outstanding")


# --------------------------------------------------------------------------
# End to end through the orchestrator merge
# --------------------------------------------------------------------------

def test_quote_candidates_survive_the_merge():
    cand = os.path.join(HERE, "_quote_cand.json")
    try:
        proc = run(CHECK_QUOTE, bundle("unquotable-chunks"), "--out", cand)
        assert proc.returncode == 0, proc.stderr
        merged = run(MERGE, cand, "--pages-sampled", "5", "--stdout")
        assert merged.returncode == 0, merged.stderr
        doc = json.loads(merged.stdout)
        q = [f for f in doc["findings"] if f["check_id"] == "QUOTE-001"]
        assert q, "QUOTE-001 candidate was dropped by the merge"
        assert q[0]["severity"] in ("medium", "high")
        assert q[0]["id"].startswith("F-")
    finally:
        if os.path.exists(cand):
            os.remove(cand)
