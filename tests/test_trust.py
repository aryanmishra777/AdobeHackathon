"""Deterministic tests for the TRUST stage (freshness-corroboration-audit).

Dev tooling -- outside the submission.

Layer 1, same shape as test_marketplace.py / test_answerability.py: run the real
check script over the local fixture bundles and assert on the candidates it
emits. `clean` is the false-positive tripwire; `stale-content` is the positive
control for dead content and a dishonest sitemap `lastmod`.

    python tests/make_fixtures.py && python tests/make_bundles.py
    python -m pytest tests/ -k trust -v
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
CHECK_TRUST = os.path.join(REPO, "brand-ai-readiness-audit", "skills",
                           "freshness-corroboration-audit", "scripts", "check_trust.py")
MERGE = os.path.join(REPO, "brand-ai-readiness-audit", "skills", "audit-orchestrator",
                     "scripts", "merge_findings.py")

ALL_FIXTURES = ["clean", "js-shell", "blocked-crawlers", "contradictory-markup",
                "stale-content", "unquotable-chunks", "low-engagement"]

REQUIRED = ["id", "check_id", "title", "severity", "confidence", "determinism",
            "category", "mechanism", "evidence", "evidence_detail",
            "affected_scope", "verification", "suggested_action"]

# checks.yaml meta.offsite_checks minus the two that run on-site (008, 010).
PURE_OFFSITE = {"TRUST-006", "TRUST-007", "TRUST-009", "TRUST-012", "TRUST-013"}


def bundle(name: str) -> str:
    path = os.path.join(BUNDLES, name)
    if not os.path.isdir(path):
        pytest.skip(f"bundle {name!r} not built; run tests/make_bundles.py")
    return path


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, encoding="utf-8")


def trust_output(name: str) -> dict:
    proc = run(CHECK_TRUST, bundle(name), "--stdout")
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def trust_findings(name: str) -> list:
    return trust_output(name)["findings"]


# --------------------------------------------------------------------------
# The false-positive tripwire
# --------------------------------------------------------------------------

def test_trust_clean_site_produces_no_serious_findings():
    serious = [f for f in trust_findings("clean")
               if f["severity"] in ("critical", "high")]
    assert not serious, (
        "TRUST checks fired on the clean fixture: "
        + "; ".join(f"{f['check_id']} ({f['severity']}) {f['title']}" for f in serious))


def test_trust_clean_site_produces_no_findings_at_all():
    found = trust_findings("clean")
    assert found == [], "; ".join(f"{f['check_id']} {f['title']}" for f in found)


# --------------------------------------------------------------------------
# stale-content positive control
# --------------------------------------------------------------------------

def test_trust_003_fires_on_stale_content():
    """Every sitemap URL carries one very recent lastmod while the home page's
    own content is dated 2019."""
    ids = {f["check_id"] for f in trust_findings("stale-content")}
    assert "TRUST-003" in ids, "stale-content must produce a TRUST-003 candidate"


def test_trust_003_is_evidenced_and_deterministic():
    f = next(x for x in trust_findings("stale-content") if x["check_id"] == "TRUST-003")
    assert f["determinism"] == "deterministic"
    assert f["severity"] != "critical"
    assert f["evidence"].strip().lower() != f["title"].strip().lower()
    assert any(ch.isdigit() for ch in f["evidence"])
    c = f["evidence_detail"]["counts"]
    assert c["urls_sharing_lastmod"] >= 3
    assert c["contradicting_pages"] >= 1


def test_trust_staleness_signals_fire_on_stale_content():
    """The fixture also carries a 2019 copyright and a 'current ... available
    now' claim on a 2019-dated page."""
    ids = {f["check_id"] for f in trust_findings("stale-content")}
    assert "TRUST-004" in ids, "stale copyright year must produce TRUST-004"
    assert "TRUST-005" in ids, "stale 'current' claim must produce TRUST-005"


def test_trust_stale_content_findings_survive_the_merge_below_critical():
    cand = os.path.join(HERE, "_trust_cand.json")
    try:
        assert run(CHECK_TRUST, bundle("stale-content"), "--out", cand).returncode == 0
        merged = run(MERGE, cand, "--pages-sampled", "5", "--stdout")
        assert merged.returncode == 0, merged.stderr
        doc = json.loads(merged.stdout)
        got = {f["check_id"] for f in doc["findings"]}
        assert "TRUST-003" in got
        for f in doc["findings"]:
            assert f["severity"] != "critical"
    finally:
        if os.path.exists(cand):
            os.remove(cand)


# --------------------------------------------------------------------------
# Honest degradation without a search tool
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_trust_offsite_checks_are_recorded_as_skipped_not_silent(name):
    """No fixture bundle carries an external/ block, so every purely off-site
    check must appear in checks_skipped with a reason -- never silently omitted."""
    out = trust_output(name)
    skipped = {s["check_id"] for s in out["checks_skipped"]}
    for cid in PURE_OFFSITE:
        assert cid in skipped, f"{name}: {cid} was not recorded as skipped"
    for s in out["checks_skipped"]:
        assert len(s["reason"]) > 10 and "evidence of absence" in s["reason"].lower() \
            or "lookup" in s["reason"].lower() or "tool" in s["reason"].lower() \
            or "profile" in s["reason"].lower() or "threshold" in s["reason"].lower() \
            or "not tested" in s["reason"].lower() or "content" in s["reason"].lower()


def test_trust_offsite_findings_never_emitted_without_a_tool():
    for name in ALL_FIXTURES:
        for f in trust_findings(name):
            assert f["check_id"] not in PURE_OFFSITE, (
                f"{name}: {f['check_id']} emitted a finding with no search tool")


# --------------------------------------------------------------------------
# Contract
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_trust_candidates_are_deterministic(name):
    a = run(CHECK_TRUST, bundle(name), "--stdout")
    b = run(CHECK_TRUST, bundle(name), "--stdout")
    assert a.returncode == 0 and b.returncode == 0, a.stderr + b.stderr
    assert a.stdout == b.stdout, f"{name}: two runs over one bundle disagreed"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_trust_findings_cite_resolvable_evidence(name):
    root = bundle(name)
    for f in trust_findings(name):
        refs = f["evidence_detail"]["artifact_refs"]
        assert refs, f"{f['check_id']} cites no artifact"
        for ref in refs:
            assert os.path.exists(os.path.join(root, ref.replace("/", os.sep))), (
                f"{f['check_id']} cites missing {ref}")


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_trust_findings_have_the_schema_fields(name):
    for f in trust_findings(name):
        for key in REQUIRED:
            assert key in f, f"{f.get('check_id')} missing {key!r}"
        assert f["mechanism"] == "trust" and f["category"] == "discoverability"
        assert len(f["evidence"]) >= 20 and len(f["verification"]) >= 15
        assert f["evidence"].strip().lower() != f["title"].strip().lower()
        action = f["suggested_action"]
        for key in ("summary", "priority", "steps", "effort", "impact_rationale"):
            assert key in action, f"{f['check_id']}.suggested_action missing {key!r}"
        assert action["steps"]


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_trust_model_judged_findings_are_never_critical(name):
    for f in trust_findings(name):
        if f["determinism"] == "model-judged":
            assert f["severity"] != "critical", f"{f['check_id']} is model-judged and critical"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_trust_fix_snippets_are_tailored_not_templated(name):
    for f in trust_findings(name):
        code = f["suggested_action"].get("code") or ""
        for placeholder in ("YOUR_", "<your ", "REPLACE_ME", "XXX", "TODO"):
            assert placeholder.lower() not in code.lower(), (
                f"{f['check_id']} ships an untailored snippet containing {placeholder!r}")


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_trust_proactive_recommendations_are_well_formed(name):
    for pr in trust_output(name)["proactive_recommendations"]:
        assert set(pr).issubset(
            {"id", "title", "category", "mechanism", "rationale", "suggested_action"})
        assert pr["id"].startswith("P-") and pr["id"][2:].isdigit()
        assert 10 <= len(pr["title"]) <= 120 and len(pr["rationale"]) >= 20
        assert pr["suggested_action"]["steps"]


def test_trust_all_registry_checks_are_implemented_or_listed():
    assert trust_output("clean")["checks_not_implemented"] == []


def test_trust_never_calls_a_claim_untrue():
    """Binding guard: uncorroborated is not untrue. No TRUST finding may assert a
    claim is false; the language must stay 'confirm this is still accurate'."""
    for name in ALL_FIXTURES:
        for f in trust_findings(name):
            blob = (f["evidence"] + " " + f["suggested_action"]["summary"] + " "
                    + f["suggested_action"]["impact_rationale"]).lower()
            for phrase in ("is false", "is untrue", "is a lie", "fabricated",
                           "is discontinued", "does not exist"):
                assert phrase not in blob, f"{name}/{f['check_id']} asserts falsehood: {phrase!r}"
