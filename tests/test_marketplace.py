"""Deterministic tests over the local fixture bundles.

Dev tooling -- outside the submission.

Layer 1 of the three-layer test strategy: hand-built fixture sites with known
defects, plus one clean site that acts as the false-positive tripwire. Fast,
offline, and asserted hard.

    python tests/make_fixtures.py && python tests/make_bundles.py
    python -m pytest tests/ -v

Layers 2 and 3 (corpus replay and the live bench) live in bench/.
"""

from __future__ import annotations

import json
import tempfile
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BUNDLES = os.path.join(HERE, "bundles")
SKILLS = os.path.join(REPO, "brand-ai-readiness-audit", "skills")

CHECK_ACCESS = os.path.join(SKILLS, "crawl-access-audit", "scripts", "check_access.py")
CHECK_RENDER = os.path.join(SKILLS, "render-extractability-audit", "scripts", "check_render.py")
CHECK_PARSE = os.path.join(SKILLS, "structured-data-audit", "scripts", "check_structured_data.py")
VALIDATE_BUNDLE = os.path.join(SKILLS, "site-evidence-collector", "scripts",
                               "validate_bundle.py")
COLLECT = os.path.join(SKILLS, "site-evidence-collector", "scripts", "collect.py")
MERGE = os.path.join(SKILLS, "audit-orchestrator", "scripts", "merge_findings.py")
VALIDATE_REPORT = os.path.join(SKILLS, "audit-orchestrator", "scripts",
                               "validate_report.py")

ALL_FIXTURES = ["clean", "js-shell", "blocked-crawlers", "contradictory-markup",
                "stale-content", "unquotable-chunks", "low-engagement"]


def bundle(name: str) -> str:
    path = os.path.join(BUNDLES, name)
    if not os.path.isdir(path):
        pytest.skip(f"bundle {name!r} not built; run tests/make_bundles.py")
    return path


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, encoding="utf-8")


def reach_findings(name: str) -> list[dict]:
    proc = run(CHECK_ACCESS, bundle(name), "--stdout")
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)["findings"]


def read_findings(name: str) -> list[dict]:
    proc = run(CHECK_RENDER, bundle(name), "--stdout")
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)["findings"]


def parse_findings(name: str) -> list[dict]:
    proc = run(CHECK_PARSE, bundle(name), "--stdout")
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)["findings"]


def manifest(name: str) -> dict:
    with open(os.path.join(bundle(name), "MANIFEST.json"), encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# The bundle contract
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_bundle_is_valid(name):
    proc = run(VALIDATE_BUNDLE, bundle(name), "--quiet")
    assert proc.returncode == 0, proc.stderr


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_bundle_preserves_alt_distinction(name):
    """alt=null (absent) and alt="" (decorative) must stay distinguishable, or
    READ-008 cannot avoid its central false positive."""
    m = manifest(name)
    for page in [p for p in m["pages"] if p.get("status") == 200]:
        path = os.path.join(bundle(name), "pages", page["page_id"], "extracted.json")
        with open(path, encoding="utf-8") as fh:
            for img in json.load(fh).get("images", []):
                assert "alt" in img, f"{page['page_id']} dropped the alt key"


# --------------------------------------------------------------------------
# The false-positive tripwire
# --------------------------------------------------------------------------

def test_clean_site_produces_no_serious_findings():
    """The single most important test in the repo.

    The clean fixture is correct by construction: retrieval agents explicitly
    allowed, sitemap present and honest, canonicals on every page, structured
    data consistent with the visible text, explicit identity sentences, dated
    content, viewport declared. Any check that fires here at critical or high is
    wrong, and would cost the reader's trust in every other finding.
    """
    serious = [f for f in reach_findings("clean")
               if f["severity"] in ("critical", "high")]
    assert not serious, (
        "checks fired on the clean fixture: "
        + "; ".join(f"{f['check_id']} ({f['severity']}) {f['title']}" for f in serious))


def test_clean_site_reports_no_blocked_agents():
    m = manifest("clean")
    blocked = [t for t, e in m["robots"]["agent_matrix"].items()
               if e.get("root_allowed") is False]
    assert blocked == [], f"clean fixture should block nothing, blocks {blocked}"


# --------------------------------------------------------------------------
# The retrieval-versus-training split
# --------------------------------------------------------------------------

def test_blocked_retrieval_agents_are_a_defect():
    ids = {f["check_id"] for f in reach_findings("blocked-crawlers")}
    assert "REACH-002" in ids, "blocking ChatGPT-User must produce REACH-002"


def test_blocked_training_agents_are_informational_only():
    """The distinction the whole marketplace turns on.

    Blocking GPTBot is a business decision taken after legal review at many
    organisations. Reporting it as a defect discredits the report.
    """
    findings = reach_findings("blocked-crawlers")
    trust = [f for f in findings if f["check_id"] == "REACH-003"]
    assert trust, "blocking GPTBot must still be reported, as information"
    assert trust[0]["severity"] == "low", (
        f"REACH-003 must stay 'low', got {trust[0]['severity']}")
    assert trust[0].get("severity_locked") is True, (
        "REACH-003 must be severity_locked so no scope modifier can escalate it")
    text = (trust[0]["evidence"] + trust[0]["suggested_action"]["summary"]).lower()
    for word in ("error", "defect", "bug", "problem", "fix this"):
        assert word not in text, f"REACH-003 must not frame a legal opt-out as a {word!r}"


def test_training_block_survives_the_merge_at_low():
    """Regression: a site-wide scope modifier must not escalate an informational
    finding. This inflated REACH-003 to 'medium' before severity_locked existed.
    """
    proc = run(CHECK_ACCESS, bundle("blocked-crawlers"), "--out", "_t.json")
    assert proc.returncode == 0, proc.stderr
    try:
        merged = run(MERGE, "_t.json", "--pages-sampled", "5", "--stdout")
        assert merged.returncode == 0, merged.stderr
        doc = json.loads(merged.stdout)
        t = [f for f in doc["findings"] if f["check_id"] == "REACH-003"]
        assert t and t[0]["severity"] == "low", (
            f"REACH-003 escalated to {t[0]['severity'] if t else 'missing'}")
    finally:
        if os.path.exists("_t.json"):
            os.remove("_t.json")


# --------------------------------------------------------------------------
# Determinism
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_analysis_is_deterministic(name):
    """The same bundle twice must produce byte-identical findings, or golden
    tests are meaningless and findings are unreproducible."""
    a = run(CHECK_ACCESS, bundle(name), "--stdout")
    b = run(CHECK_ACCESS, bundle(name), "--stdout")
    assert a.returncode == 0 and b.returncode == 0
    assert a.stdout == b.stdout, f"{name}: two runs over one bundle disagreed"


def test_finding_ids_are_content_addressed():
    """Merging the same candidates in a different input order must yield the
    same ids, because ordering is a pure function of content."""
    findings = reach_findings("blocked-crawlers")
    forward = os.path.join(HERE, "_fwd.json")
    reverse = os.path.join(HERE, "_rev.json")
    try:
        with open(forward, "w", encoding="utf-8") as fh:
            json.dump(findings, fh)
        with open(reverse, "w", encoding="utf-8") as fh:
            json.dump(list(reversed(findings)), fh)
        a = run(MERGE, forward, "--pages-sampled", "5", "--stdout")
        b = run(MERGE, reverse, "--pages-sampled", "5", "--stdout")
        assert a.returncode == 0 and b.returncode == 0, a.stderr + b.stderr
        pair_a = [(f["id"], f["check_id"]) for f in json.loads(a.stdout)["findings"]]
        pair_b = [(f["id"], f["check_id"]) for f in json.loads(b.stdout)["findings"]]
        assert pair_a == pair_b, "id assignment depends on input order"
    finally:
        for p in (forward, reverse):
            if os.path.exists(p):
                os.remove(p)


# --------------------------------------------------------------------------
# The finding contract
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_every_finding_cites_resolvable_evidence(name):
    """False-positive gate 2: a finding that cannot point at its own evidence is
    deleted, not downgraded."""
    root = bundle(name)
    for f in reach_findings(name):
        refs = f["evidence_detail"]["artifact_refs"]
        assert refs, f"{f['check_id']} cites no artifact"
        for ref in refs:
            path = os.path.join(root, ref.replace("/", os.sep))
            assert os.path.exists(path), f"{f['check_id']} cites missing {ref}"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_findings_satisfy_the_schema_fields(name):
    required = ["id", "check_id", "title", "severity", "confidence", "determinism",
                "category", "mechanism", "evidence", "evidence_detail",
                "affected_scope", "verification", "suggested_action"]
    for f in reach_findings(name):
        for key in required:
            assert key in f, f"{f.get('check_id')} missing {key!r}"
        assert f["evidence"].strip().lower() != f["title"].strip().lower(), (
            f"{f['check_id']}: evidence restates the title")
        action = f["suggested_action"]
        for key in ("summary", "priority", "steps", "effort", "impact_rationale"):
            assert key in action, f"{f['check_id']}.suggested_action missing {key!r}"
        assert action["steps"], f"{f['check_id']} has no fix steps"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_model_judged_findings_are_never_critical(name):
    """False-positive gate 3."""
    for f in reach_findings(name):
        if f["determinism"] == "model-judged":
            assert f["severity"] != "critical", (
                f"{f['check_id']} is model-judged and critical")


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_fix_snippets_are_tailored_not_templated(name):
    """A snippet containing a placeholder gets pasted into production verbatim."""
    for f in reach_findings(name):
        code = f["suggested_action"].get("code") or ""
        for placeholder in ("YOUR_", "<your ", "REPLACE_ME", "XXX", "TODO"):
            assert placeholder.lower() not in code.lower(), (
                f"{f['check_id']} ships an untailored snippet containing "
                f"{placeholder!r}")


# --------------------------------------------------------------------------
# End to end
# --------------------------------------------------------------------------

def test_pipeline_produces_a_schema_valid_report():
    """collect -> check -> merge -> validate, over a fixture bundle."""
    root = bundle("blocked-crawlers")
    cand = os.path.join(HERE, "_cand.json")
    merged = os.path.join(HERE, "_merged.json")
    report = os.path.join(HERE, "_report.json")
    try:
        assert run(CHECK_ACCESS, root, "--out", cand).returncode == 0
        assert run(MERGE, cand, "--pages-sampled", "5", "--out", merged).returncode == 0

        with open(merged, encoding="utf-8") as fh:
            m = json.load(fh)
        sc = m["scorecard_input"]
        doc = {
            "schema_version": "1.0",
            "site": "localhost",
            "audited_at": "2026-09-06T00:00:00Z",
            "summary": m["summary"],
            "scorecard": {
                "discoverability": {**sc["discoverability"],
                                    "headline": "Retrieval crawlers are blocked."},
                "engagement": {**sc["engagement"],
                               "headline": "Not assessed in this REACH-only test."},
                "verdict": ("robots.txt blocks the crawlers that fetch pages when a "
                            "user asks a question, so the brand cannot appear in "
                            "those answers at all."),
            },
            "coverage": {
                "pages_sampled": 5, "complete": False,
                "limitations": ["REACH-only pipeline test; other stages did not run."],
                "checks_skipped": [{"check_id": "STAY-001",
                                    "reason": "engagement-audit not run in this test"}],
            },
            "findings": m["findings"],
        }
        with open(report, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)

        proc = run(VALIDATE_REPORT, report, "--bundle", root)
        assert proc.returncode == 0, proc.stderr
    finally:
        for p in (cand, merged, report):
            if os.path.exists(p):
                os.remove(p)


def test_marketplace_validates():
    proc = run(os.path.join(REPO, "tools", "validate.py"), "--quiet")
    assert proc.returncode == 0, proc.stdout + proc.stderr


# --------------------------------------------------------------------------
# READ checks
# --------------------------------------------------------------------------

def test_read_clean_site_produces_no_serious_findings():
    """False-positive tripwire for READ checks: clean site must produce ZERO
    critical or high findings."""
    serious = [f for f in read_findings("clean")
               if f["severity"] in ("critical", "high")]
    assert not serious, (
        "READ checks fired on the clean fixture: "
        + "; ".join(f"{f['check_id']} ({f['severity']}) {f['title']}" for f in serious))


def test_read_js_shell_produces_read_001():
    """js-shell fixture must produce READ-001 with critical severity and medium
    confidence when renderer is not available."""
    findings = read_findings("js-shell")
    read_001 = [f for f in findings if f["check_id"] == "READ-001"]
    assert len(read_001) == 1, f"Expected 1 READ-001 finding, got {len(read_001)}"
    f = read_001[0]
    assert f["severity"] == "critical"
    assert f["confidence"] == "medium"
    assert f["determinism"] == "deterministic"
    assert "inferred" in f["evidence"].lower()


def test_read_001_never_cites_a_signal_that_did_not_fire():
    """Evidence must be built from the signals that actually tripped.

    An early version could report "carrying a 0 byte hydration payload and an
    empty #root mount point" -- a payload of zero offered as proof of a payload,
    and a fallback selector presented as a detected one. A finding whose own
    evidence sentence is self-refuting is worse than no finding at all.
    """
    for name in ALL_FIXTURES:
        for f in read_findings(name):
            if f["check_id"] != "READ-001":
                continue
            ev = f["evidence"]
            assert "0 byte" not in ev, f"{name}: cites a zero-byte payload as evidence"
            detected = set()
            for pid in [r.split("/")[1] for r in
                        (f.get("evidence_detail") or {}).get("artifact_refs", [])
                        if r.startswith("pages/")]:
                path = os.path.join(bundle(name), "pages", pid, "extracted.json")
                if not os.path.exists(path):
                    continue
                with open(path, encoding="utf-8") as fh:
                    sig = (json.load(fh).get("render_signals") or {})
                detected |= {x.lstrip("#.") for x in (sig.get("app_shell_selectors") or [])}
            for token in ("#root", "#app", "#__next"):
                if token in ev:
                    assert token.lstrip("#") in detected, (
                        f"{name}: evidence names {token} but no page reported that mount")


def test_read_001_ignores_server_rendered_platform_markers():
    """WordPress and Shopify render on the server.

    The collector reports them in the same `framework_markers` list as Next.js
    and React, because "this is WordPress" is a fact other checks may want. But
    "wp-content" appears in an asset URL on every WordPress page, so treating it
    as evidence of client rendering fires READ-001 across most of the CMS-hosted
    web. This is the chewy.com false positive, pinned.
    """
    from types import SimpleNamespace
    sys.path.insert(0, os.path.dirname(CHECK_RENDER))
    import importlib
    mod = importlib.import_module(os.path.basename(CHECK_RENDER)[:-3])

    shell_only_platform = {
        "text": {"main_word_count": 12, "text_to_markup_ratio": 0.004},
        "render_signals": {"framework_markers": ["wordpress", "shopify"],
                           "app_shell_selectors": [], "hydration_payload_bytes": 0},
    }
    assert mod._render_signals({}, shell_only_platform) is None, (
        "a server-rendered platform marker alone must never satisfy READ-001")

    real_spa = dict(shell_only_platform)
    real_spa["render_signals"] = {"framework_markers": ["next.js"],
                                  "app_shell_selectors": ["__next"],
                                  "hydration_payload_bytes": 108_567}
    assert mod._render_signals({}, real_spa) is not None, (
        "a genuine client-rendered shell must still be detected")


def test_read_001_word_threshold_is_not_a_cliff():
    """A page of nav-and-footer chrome lands near 60 words.

    asana.com served 57-59 words per page with a 108 KB hydration payload, an
    empty #__next mount and a text-to-markup ratio of 0.002 -- three signals
    screaming client-rendered, vetoed by a hard `< 50` constant. Thin is thin
    slightly above 50 when the corroborating signal is overwhelming.
    """
    import importlib
    sys.path.insert(0, os.path.dirname(CHECK_RENDER))
    mod = importlib.import_module(os.path.basename(CHECK_RENDER)[:-3])

    asana_shaped = {
        "text": {"main_word_count": 59, "text_to_markup_ratio": 0.0018},
        "render_signals": {"framework_markers": ["next.js"],
                           "app_shell_selectors": ["__next"],
                           "hydration_payload_bytes": 91_362},
    }
    assert mod._render_signals({}, asana_shaped) is not None, (
        "59 words with a 91 KB payload and ratio 0.0018 is an empty shell")

    # ... but a server-rendered page with real text is never a shell, however
    # much framework machinery it ships. This is the guard that matters most.
    ssr_shaped = {
        "text": {"main_word_count": 1200, "text_to_markup_ratio": 0.08},
        "render_signals": {"framework_markers": ["next.js"],
                           "app_shell_selectors": ["__next"],
                           "hydration_payload_bytes": 250_000},
    }
    assert mod._render_signals({}, ssr_shaped) is None, (
        "1200 words of server-rendered text must never be called an empty shell")


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_read_analysis_is_deterministic(name):
    """The same bundle twice must produce byte-identical READ findings."""
    a = run(CHECK_RENDER, bundle(name), "--stdout")
    b = run(CHECK_RENDER, bundle(name), "--stdout")
    assert a.returncode == 0 and b.returncode == 0
    assert a.stdout == b.stdout, f"{name}: two runs over one bundle disagreed"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_read_every_finding_cites_resolvable_evidence(name):
    """Every READ candidate must cite artifact_refs that exist on disk."""
    root = bundle(name)
    for f in read_findings(name):
        refs = f["evidence_detail"]["artifact_refs"]
        assert refs, f"{f['check_id']} cites no artifact"
        for ref in refs:
            path = os.path.join(root, ref.replace("/", os.sep))
            assert os.path.exists(path), f"{f['check_id']} cites missing {ref}"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_read_findings_satisfy_the_schema_fields(name):
    required = ["id", "check_id", "title", "severity", "confidence", "determinism",
                "category", "mechanism", "evidence", "evidence_detail",
                "affected_scope", "verification", "suggested_action"]
    for f in read_findings(name):
        for key in required:
            assert key in f, f"{f.get('check_id')} missing {key!r}"
        assert f["evidence"].strip().lower() != f["title"].strip().lower(), (
            f"{f['check_id']}: evidence restates the title")
        action = f["suggested_action"]
        for key in ("summary", "priority", "steps", "effort", "impact_rationale"):
            assert key in action, f"{f['check_id']}.suggested_action missing {key!r}"
        assert action["steps"], f"{f['check_id']} has no fix steps"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_read_model_judged_findings_are_never_critical(name):
    """Model-judged READ findings may never be critical."""
    for f in read_findings(name):
        if f["determinism"] == "model-judged":
            assert f["severity"] != "critical", (
                f"{f['check_id']} is model-judged and critical")


# --------------------------------------------------------------------------
# PARSE checks
# --------------------------------------------------------------------------

def test_parse_clean_site_produces_no_serious_findings():
    """False-positive tripwire for PARSE checks: clean site must produce ZERO
    critical or high findings."""
    serious = [f for f in parse_findings("clean")
               if f["severity"] in ("critical", "high")]
    assert not serious, (
        "PARSE checks fired on the clean fixture: "
        + "; ".join(f"{f['check_id']} ({f['severity']}) {f['title']}" for f in serious))


def test_parse_contradictory_markup_produces_parse_007():
    """contradictory-markup fixture must produce PARSE-007 at high severity."""
    findings = parse_findings("contradictory-markup")
    p7 = [f for f in findings if f["check_id"] == "PARSE-007"]
    assert len(p7) == 1, f"Expected 1 PARSE-007 finding, got {len(p7)}"
    assert p7[0]["severity"] == "high"
    assert "price" in p7[0]["evidence"].lower()


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_parse_analysis_is_deterministic(name):
    """The same bundle twice must produce byte-identical PARSE findings."""
    a = run(CHECK_PARSE, bundle(name), "--stdout")
    b = run(CHECK_PARSE, bundle(name), "--stdout")
    assert a.returncode == 0 and b.returncode == 0
    assert a.stdout == b.stdout, f"{name}: two runs over one bundle disagreed"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_parse_every_finding_cites_resolvable_evidence(name):
    """Every PARSE candidate must cite artifact_refs that exist on disk."""
    root = bundle(name)
    for f in parse_findings(name):
        refs = f["evidence_detail"]["artifact_refs"]
        assert refs, f"{f['check_id']} cites no artifact"
        for ref in refs:
            path = os.path.join(root, ref.replace("/", os.sep))
            assert os.path.exists(path), f"{f['check_id']} cites missing {ref}"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_parse_findings_satisfy_the_schema_fields(name):
    required = ["id", "check_id", "title", "severity", "confidence", "determinism",
                "category", "mechanism", "evidence", "evidence_detail",
                "affected_scope", "verification", "suggested_action"]
    for f in parse_findings(name):
        for key in required:
            assert key in f, f"{f.get('check_id')} missing {key!r}"
        assert f["evidence"].strip().lower() != f["title"].strip().lower(), (
            f"{f['check_id']}: evidence restates the title")
        action = f["suggested_action"]
        for key in ("summary", "priority", "steps", "effort", "impact_rationale"):
            assert key in action, f"{f['check_id']}.suggested_action missing {key!r}"
        assert action["steps"], f"{f['check_id']} has no fix steps"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_parse_model_judged_findings_are_never_critical(name):
    """Model-judged PARSE findings may never be critical."""
    for f in parse_findings(name):
        if f["determinism"] == "model-judged":
            assert f["severity"] != "critical", (
                f"{f['check_id']} is model-judged and critical")


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_parse_fix_snippets_are_tailored_not_templated(name):
    """A snippet containing a placeholder gets pasted into production verbatim."""
    for f in parse_findings(name):
        code = f["suggested_action"].get("code") or ""
        for placeholder in ("YOUR_", "<your ", "REPLACE_ME", "XXX", "TODO"):
            assert placeholder.lower() not in code.lower(), (
                f"{f['check_id']} ships an untailored snippet containing {placeholder!r}")




# --------------------------------------------------------------------------
# Encoding: reports are JSON, JSON is UTF-8, and evidence quotes real pages
# --------------------------------------------------------------------------

# merge_findings takes candidate finding files rather than a bundle, so it is
# covered by the end-to-end test below instead of this parametrized one.
ALL_SHIPPED_SCRIPTS = [CHECK_ACCESS, CHECK_RENDER, CHECK_PARSE] + [
    os.path.join(SKILLS, skill, "scripts", script)
    for skill, script in (
        ("answerability-audit", "check_answerability.py"),
        ("freshness-corroboration-audit", "check_trust.py"),
        ("engagement-audit", "check_engagement.py"),
    )
]


@pytest.mark.parametrize("script", ALL_SHIPPED_SCRIPTS)
def test_scripts_write_utf8_to_stdout_on_a_legacy_codepage(script):
    """A non-Latin-1 character in evidence text must not abort the audit.

    Evidence strings quote real page content, so one arrow, curly quote, em
    dash or non-Latin script is routine. Windows consoles default to a legacy
    codepage (cp1252), where `print()` on such a character raises
    UnicodeEncodeError and kills the whole run -- which is what happened to 10
    of 57 corpus sites, python.org among them, over a single U+25BC.

    Forcing the child's IO encoding to cp1252 reproduces a grader's Windows
    machine on any host.
    """
    assert os.path.exists(script), script
    env = dict(os.environ, PYTHONIOENCODING="cp1252")
    proc = subprocess.run([sys.executable, script, bundle("clean"), "--stdout"],
                          capture_output=True, env=env)
    assert proc.returncode == 0, (
        f"{os.path.basename(script)} died under a cp1252 console:\n"
        + proc.stderr.decode("utf-8", "replace")[-1500:])
    assert b"UnicodeEncodeError" not in proc.stderr


def test_reports_survive_non_latin1_evidence_end_to_end():
    """The full pipeline must carry a non-Latin-1 character through the merge."""
    findings = json.loads(run(CHECK_ACCESS, bundle("clean"), "--stdout").stdout)
    items = findings if isinstance(findings, list) else findings.get("findings", [])
    if not items:
        pytest.skip("clean fixture produced no finding to decorate")
    items[0]["evidence"] = "Navigation collapses behind a \u25bc toggle \u2014 caf\u00e9 \u4f60\u597d."

    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "candidates.json")
        with open(src, "w", encoding="utf-8") as fh:
            json.dump(items, fh, ensure_ascii=False)
        env = dict(os.environ, PYTHONIOENCODING="cp1252")
        proc = subprocess.run(
            [sys.executable, MERGE, src, "--pages-sampled", "5", "--stdout"],
            capture_output=True, env=env)
        assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")[-1500:]
        merged = json.loads(proc.stdout.decode("utf-8"))
    text = json.dumps(merged, ensure_ascii=False)
    assert "\u25bc" in text and "caf\u00e9" in text, "characters lost in the merge"


# --------------------------------------------------------------------------
# One defect, reported once
# --------------------------------------------------------------------------

def test_a_check_firing_on_many_pages_becomes_one_finding():
    """Eleven pages failing one check is one defect, not eleven findings.

    An audit of bbc.co.uk produced 39 findings of which 27 came from one skill:
    STAY-001 eleven times and STAY-014 eight times, one per page. The dedupe
    only merged candidates whose page sets OVERLAPPED, and per-page findings
    never overlap. Nobody reads to the end of a report that says the same thing
    eleven times.
    """
    candidates = []
    for i in range(6):
        candidates.append({
            "id": "F-000", "check_id": "STAY-001",
            "title": "The top of the page does not say what this is",
            "severity": "medium", "confidence": "high",
            "determinism": "deterministic", "category": "engagement",
            "mechanism": "stay", "evidence": f"Page {i} opens without orientation.",
            "evidence_detail": {"pages_affected": [f"https://example.com/p{i}"],
                                "counts": {}, "artifact_refs": ["MANIFEST.json"]},
            "affected_scope": {"pages_checked": 6, "pages_affected": 1, "scope": "page"},
            "verification": "Open the page", "suggested_action": {},
        })
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "c.json")
        with open(src, "w", encoding="utf-8") as fh:
            json.dump(candidates, fh)
        proc = run(MERGE, src, "--pages-sampled", "6", "--stdout")
        assert proc.returncode == 0, proc.stderr
        merged = json.loads(proc.stdout)["findings"]

    same = [f for f in merged if f["check_id"] == "STAY-001"]
    assert len(same) == 1, f"6 per-page candidates became {len(same)} findings"
    pages = (same[0].get("evidence_detail") or {}).get("pages_affected") or []
    assert len(pages) == 6, "the merged finding must keep every affected page"
    assert "6" in same[0]["evidence"], (
        "evidence still describes one page; it must restate the real spread")


def test_distinct_titles_under_one_check_id_stay_separate():
    """REACH-014 reports an https failure and mixed content under one id.

    Collapsing purely by check_id would fold two different problems into one
    finding wearing whichever title happened to come first.
    """
    def cand(title, page):
        return {"id": "F-000", "check_id": "REACH-014", "title": title,
                "severity": "medium", "confidence": "high",
                "determinism": "deterministic", "category": "discoverability",
                "mechanism": "reach", "evidence": title,
                "evidence_detail": {"pages_affected": [page], "counts": {},
                                    "artifact_refs": ["run.json"]},
                "affected_scope": {"pages_checked": 2, "pages_affected": 1,
                                   "scope": "page"},
                "verification": "curl", "suggested_action": {}}

    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "c.json")
        with open(src, "w", encoding="utf-8") as fh:
            json.dump([cand("The site did not answer over https", "https://e.com/a"),
                       cand("Secure pages load subresources over plain http",
                            "https://e.com/b")], fh)
        proc = run(MERGE, src, "--pages-sampled", "2", "--stdout")
        assert proc.returncode == 0, proc.stderr
        merged = json.loads(proc.stdout)["findings"]
    titles = {f["title"] for f in merged if f["check_id"] == "REACH-014"}
    assert len(titles) == 2, f"two distinct problems collapsed into {titles}"


def test_model_judged_findings_cannot_reach_critical_through_the_merge():
    """Gate 3 must hold after merging and escalation, not only per check.

    A merge keeps the worst severity of its group and site-wide scope escalates
    a level, so a model-judged finding can arrive at critical without any single
    check having asked for it. That produced a report validate_report rejected.
    """
    cand = {"id": "F-000", "check_id": "PARSE-007",
            "title": "Structured data contradicts the visible page",
            "severity": "high", "confidence": "high",
            "determinism": "model-judged", "category": "discoverability",
            "mechanism": "parse", "evidence": "Price in markup differs from page.",
            "evidence_detail": {"pages_affected": [f"https://e.com/p{i}" for i in range(5)],
                                "counts": {}, "artifact_refs": ["MANIFEST.json"]},
            "affected_scope": {"pages_checked": 5, "pages_affected": 5,
                               "scope": "site-wide"},
            "verification": "Compare", "suggested_action": {}}
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "c.json")
        with open(src, "w", encoding="utf-8") as fh:
            json.dump([cand], fh)
        proc = run(MERGE, src, "--pages-sampled", "5", "--stdout")
        assert proc.returncode == 0, proc.stderr
        merged = json.loads(proc.stdout)["findings"]
    for f in merged:
        if f.get("determinism") == "model-judged":
            assert f["severity"] != "critical", (
                "model-judged finding reached critical through the merge")


def test_read_001_ignores_games_and_utility_pages():
    """A puzzle game has no article to server-render.

    nytimes.com produced a high-severity READ-001 built entirely from Wordle,
    the mini crossword, Spelling Bee, /gift and /newsletters -- six pages with
    0-12 words -- while its fourteen actual articles carried 267 to 2007 words
    each. "Page content is missing from the HTML" was true of those six and
    useless about the site.
    """
    import importlib
    sys.path.insert(0, os.path.dirname(CHECK_RENDER))
    mod = importlib.import_module(os.path.basename(CHECK_RENDER)[:-3])

    for path in ("/games/wordle/index.html", "/crosswords/game/mini",
                 "/puzzles/spelling-bee", "/newsletters", "/gift", "/account"):
        assert mod._is_application_page({"url": "https://example.com" + path}), path
    for path in ("/2026/09/10/world/story.html", "/wirecutter/money/phone",
                 "/athletic/live-blogs/match", "/about"):
        assert not mod._is_application_page({"url": "https://example.com" + path}), path


def test_read_001_treats_personalisation_pages_as_application_pages():
    """gymshark.com's /wishlist and /edit ("Recommended for you") are
    client-rendered by design and carry nothing to server-render. "/edit" must
    match as a whole segment: "/editorial" is content."""
    import importlib
    sys.path.insert(0, os.path.dirname(CHECK_RENDER))
    mod = importlib.import_module(os.path.basename(CHECK_RENDER)[:-3])
    for path in ("/wishlist", "/edit", "/edit/", "/favourites", "/profile/settings"):
        assert mod._is_application_page({"url": "https://example.com" + path}), path
    for path in ("/editorial/standards", "/edited-volumes", "/blog/edit-your-cv"):
        assert not mod._is_application_page({"url": "https://example.com" + path}), path


def test_collector_sniffs_bodies_and_dedupes_redirect_targets():
    """python.org served a 3 MB .tar.xz with no Content-Type and it was stored
    as a page; stripe.com/legal/ssa, /ssa and /legal/connect all redirected to
    two final URLs and five of twenty sampled pages were the same two legal
    documents."""
    import importlib
    sys.path.insert(0, os.path.dirname(COLLECT))
    mod = importlib.import_module(os.path.basename(COLLECT)[:-3])
    assert mod._looks_like_markup("\ufeff\n  <!DOCTYPE html><html>")
    assert mod._looks_like_markup("<html lang=en>")
    assert not mod._looks_like_markup("\xfd7zXZ\x00\x00\x04")
    assert not mod._looks_like_markup("")
    assert mod.NON_HTML_EXT.search("/ftp/python/3.14.7/Python-3.14.7.tar.xz")
    assert mod.NON_HTML_EXT.search("/dl/app.whl") and not mod.NON_HTML_EXT.search("/docs/xz-format")
    assert mod._norm_final("https://stripe.com/in/legal/ssa/") == mod._norm_final("http://www.stripe.com/in/legal/ssa")
    assert mod._norm_final("https://a.com/x?p=1") != mod._norm_final("https://a.com/x?p=2")


def test_merge_does_not_grade_engagement_from_zero_pages(tmp_path):
    """berkshirehathaway.com answers every request with Brotli, which the
    stdlib cannot decode; the crawl saw robots.txt and nothing else, and the
    report graded engagement 100/A. Zero pages is 'not assessed', while
    discoverability -- which REACH did measure -- is still graded."""
    cand = tmp_path / "cand.json"
    cand.write_text(json.dumps([{
        "id": "F-000", "check_id": "REACH-001", "title": "No robots.txt",
        "severity": "medium", "confidence": "high", "determinism": "deterministic",
        "category": "discoverability", "mechanism": "reach",
        "evidence": "GET /robots.txt returned 404.",
        "evidence_detail": {"pages_affected": [], "counts": {}, "artifact_refs": ["robots_fetch.json"]},
        "affected_scope": {"pages_checked": 0, "pages_affected": 0, "scope": "site-wide"},
        "verification": "curl -I https://example.com/robots.txt",
        "suggested_action": {"summary": "Add a robots.txt", "priority": "medium",
                              "steps": ["Publish /robots.txt"], "effort": "S",
                              "impact_rationale": "Declares crawl policy.", "owner": "engineering"},
    }]), encoding="utf-8")
    merged = json.loads(run(MERGE, str(cand), "--pages-sampled", "0", "--stdout").stdout)
    sc = merged["scorecard_input"]
    assert sc["engagement"]["grade"] == "not assessed" and sc["engagement"]["score"] is None
    assert isinstance(sc["discoverability"]["score"], int)
    # Omitting the flag means unknown, and must not withhold an axis.
    merged = json.loads(run(MERGE, str(cand), "--stdout").stdout)
    assert isinstance(merged["scorecard_input"]["engagement"]["score"], int)


def _collect_module():
    import importlib
    sys.path.insert(0, os.path.dirname(COLLECT))
    return importlib.import_module(os.path.basename(COLLECT)[:-3])


def test_collector_robots_matching_includes_the_query_string():
    """nike.in disallows /*?root= and /*?ptype=. The first audit matched robots
    patterns against the bare path and fetched 21 URLs the site had refused."""
    mod = _collect_module()
    groups, _sitemaps, _errors = mod.parse_robots(
        "User-agent: *\nDisallow: /*?root=\nDisallow: /cart\n")
    _, group = mod.match_group(groups, "BrandAIReadinessAudit")
    assert mod.robots_allows(group, "/air-force-1/c/94020")
    assert not mod.robots_allows(group, "/air-force-1/c/94020?root=nav_3&ptype=listing")
    assert not mod.robots_allows(group, "/cart")


def test_collector_document_title_ignores_svg_titles_and_keeps_the_first():
    """Every icon in nike.in's filter panel is <svg><title></title>; last-wins
    reported 21 of 25 pages as having no title at all."""
    mod = _collect_module()
    html = ('<html><head><title>Nike – Official Online Store</title></head><body>'
            '<svg viewBox="0 0 24 24"><title></title><path d="M1 1"/></svg>'
            '<svg><title>Close</title></svg></body></html>')
    ex = mod.extract_page("p", "https://x.test/a", html, "https://x.test")
    assert ex["title"] == "Nike – Official Online Store"


def test_collector_combines_repeated_robots_meta_instead_of_last_wins():
    """nike.in's campaign pages emit noindex,nofollow twice via react-helmet and
    then index,follow once. Crawlers honour the most restrictive; last-wins read
    the page as indexable and REACH-008 never fired."""
    mod = _collect_module()
    html = ('<html><head><meta data-react-helmet="true" name="robots" content="noindex, nofollow"/>'
            '<meta name="robots" content="index, follow"/>'
            '<meta name="description" content="one"/><meta name="description" content="two"/>'
            '</head><body></body></html>')
    ex = mod.extract_page("p", "https://x.test/a", html, "https://x.test")
    assert "noindex" in ex["meta"]["robots"] and "index, follow" in ex["meta"]["robots"]
    assert ex["meta"]["description"] == "two"   # non-robots keys keep last-wins


def test_collector_keeps_links_that_wrap_a_heading():
    """Every product card on nike.in is <a><h3>name</h3>...</a>. The heading
    capture replaced the link capture, so no product URL was ever extracted and
    the crawl never reached a product page."""
    mod = _collect_module()
    html = ('<html><body><a href="/nike-swift/p/27753539"><img src="x.jpg" alt="x"/>'
            '<h3>Nike Swift</h3><span>₹3,295</span></a>'
            '<a href="/plain">Plain</a></body></html>')
    ex = mod.extract_page("p", "https://x.test/c/1", html, "https://x.test")
    hrefs = {l["href"] for l in ex["links"]}
    assert "https://x.test/nike-swift/p/27753539" in hrefs and "https://x.test/plain" in hrefs
    assert [h["text"] for h in ex["headings"]] == ["Nike Swift"]
    assert "Nike Swift" in next(l for l in ex["links"] if l["href"].endswith("27753539"))["text"]


def test_collector_classifies_an_itemlist_page_as_category_not_article():
    """A 50-product listing with an ItemList block, a copyright date and an h1
    passed the article shape rule; PARSE-014 then wanted an author on it."""
    mod = _collect_module()
    ex = {"jsonld": [{"parsed_ok": True, "value": {"@type": "ItemList", "itemListElement": []}}],
          "text": {"main_word_count": 900},
          "dates": [{"source": "meta", "value": "2026"}],
          "headings": [{"level": 1, "text": "Running (50)"}]}
    assert mod.classify_page_type("https://x.test/nike-running/c/94958", ex) == "category"
    ex["jsonld"] = []
    assert mod.classify_page_type("https://x.test/nike-running/c/94958", ex) == "article"


def test_engine_reachability_is_unverified_when_the_browser_baseline_is_refused_too(tmp_path):
    """nike.in's Akamai edge returned 403 to ChatGPT-User, Claude-User and a
    plain Chrome UA alike, while serving the audit's own UA. 'blocked' would be
    a confident false positive; the row must say the probe could not tell."""
    import shutil
    src = bundle("clean")
    dst = tmp_path / "b"
    shutil.copytree(src, dst)
    probe = json.loads((dst / "ua_probe.json").read_text(encoding="utf-8"))
    probe["baseline"].update({"status": 403, "challenge_detected": True, "bytes": 363, "text_bytes": 283})
    for a in probe["agents"].values():
        a.update({"status": 403, "challenge_detected": True, "bytes": 363, "text_bytes": 283})
    (dst / "ua_probe.json").write_text(json.dumps(probe), encoding="utf-8")
    man_path = dst / "MANIFEST.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    man["ua_probe"] = probe
    man_path.write_text(json.dumps(man), encoding="utf-8")
    proc = run(CHECK_ACCESS, str(dst), "--stdout")
    assert proc.returncode == 0, proc.stderr
    doc = json.loads(proc.stdout)
    assert not [f for f in doc["findings"] if f["check_id"] == "REACH-005"]
    rows = {r["engine"]: r for r in doc["engine_reachability"]}
    for name in ("ChatGPT", "Claude", "Perplexity"):
        assert rows[name]["state"] == "partial", rows[name]
        assert "unverified" in rows[name]["detail"] and "baseline" in rows[name]["detail"]


def test_merge_treats_help_and_support_pages_as_primary(tmp_path):
    """A JS-shell /help-center holds every returns and delivery answer on
    nike.in; the single-page de-escalation had made it a 'low'."""
    import importlib
    sys.path.insert(0, os.path.dirname(MERGE))
    mod = importlib.import_module(os.path.basename(MERGE)[:-3])
    assert mod._is_primary_page({"evidence_detail": {"pages_affected": ["https://x.test/help-center"]}})
    assert mod._is_primary_page({"evidence_detail": {"pages_affected": ["https://x.test/faq"]}})
    assert not mod._is_primary_page({"evidence_detail": {"pages_affected": ["https://x.test/blog/one"]}})


def test_collector_seeds_and_probes_from_the_target_path():
    """adobe.com/in/ was audited from the origin root: --include /in/ kept
    every discovered link out and the crawl fetched one page, /."""
    import argparse
    mod = _collect_module()
    args = argparse.Namespace(target="https://www.adobe.com/in/", out=tempfile.mkdtemp(), max_pages=5,
                              timeout=10.0, budget=60.0, concurrency=8, delay=0.5, include=["/in/"],
                              exclude=[], renderer=None, no_probe=True)
    c = mod.Collector(args)
    assert c.start_url("https://www.adobe.com") == "https://www.adobe.com/in"
    args.target = "https://www.adobe.com/"
    assert mod.Collector(args).start_url("https://www.adobe.com") == "https://www.adobe.com/"


def test_collector_diversifies_below_the_include_prefix():
    """Under --include /in/ every URL shares the segment 'in'; keying the
    round-robin on it put 17 of 25 pages inside /in/products/pdfprintengine/."""
    mod = _collect_module()
    seg = mod.Collector._segment
    assert seg("https://a.test/in/products/pdfprintengine/faq.html", ["/in/"]) == "products/pdfprintengine"
    assert seg("https://a.test/in/acrobat/pro.html", ["/in/"]) == "acrobat/pro.html"
    assert seg("https://a.test/in/products/x.html", []) == "in/products"


def test_read_001_recognises_a_byte_identical_shell_and_a_no_javascript_message(tmp_path):
    """crunchyroll.com served one document for 21 browse routes: 99 words of
    header and footer chrome and 'Update your web browser!'. No selector in
    APP_SHELL_SELECTORS matched and the words cleared the thin threshold, so
    READ-001 fired on 3 of 24 pages instead of all of them."""
    import shutil
    src = bundle("clean")
    dst = tmp_path / "b"
    shutil.copytree(src, dst)
    man = json.loads((dst / "MANIFEST.json").read_text(encoding="utf-8"))
    pages = [p for p in man["pages"] if p.get("status") == 200][:3]
    assert len(pages) == 3
    chrome = " ".join(["Browse Popular Simulcasts Release Calendar News Games Help Center"] * 6)
    shell = ("<html><head><title>Site</title></head><body><div id=\"content\">"
             f"<footer>{chrome} Update your web browser! Oh no! It looks like you're using a "
             "web browser we don't support!</footer></div>"
             + "<div class=\"x\"></div>" * 4000 + "</body></html>")
    for i, p in enumerate(pages):
        pdir = dst / "pages" / p["page_id"]
        # a per-request token inside a script must not break the match
        (pdir / "raw.html").write_text(shell + f"<script>window.t='{i}'</script>", encoding="utf-8")
        ex = json.loads((pdir / "extracted.json").read_text(encoding="utf-8"))
        ex["text"] = {"main": chrome + " Update your web browser!", "full": chrome,
                      "main_word_count": 60, "word_count": 60, "text_to_markup_ratio": 0.0005}
        ex["render_signals"] = {"app_shell_selectors": [], "framework_markers": [],
                                "hydration_payload_bytes": None, "body_element_count": 4002}
        (pdir / "extracted.json").write_text(json.dumps(ex), encoding="utf-8")
    proc = run(CHECK_RENDER, str(dst), "--stdout")
    assert proc.returncode == 0, proc.stderr
    f = next((f for f in json.loads(proc.stdout)["findings"] if f["check_id"] == "READ-001"), None)
    assert f is not None
    assert f["affected_scope"]["pages_affected"] >= 3
    assert "byte-identical document served for 3" in f["evidence"]
    assert "non-JavaScript clients" in f["evidence"]


def test_parse_010_accepts_a_brand_prefix_title():
    """'Adobe PDF Print Engine - Buying Guide' over the h1 'Buying guide for
    print service providers' was reported as a conflict twelve times because
    only the first segment of the title was compared."""
    import importlib
    sys.path.insert(0, os.path.dirname(CHECK_PARSE))
    mod = importlib.import_module(os.path.basename(CHECK_PARSE)[:-3])
    src = open(CHECK_PARSE, encoding="utf-8").read()
    assert "key=lambda seg: len(set(re.findall" in src  # the segment that agrees with the h1 wins


def test_reach_013_ignores_sitemap_indexes_and_an_unsampled_sitemap(tmp_path):
    """nike.in's nested index files and adobe.com's 90 per-locale product
    sitemaps were counted as orphaned pages; adobe.com's 1,764-URL section
    with 25 pages sampled produced 1,764 'orphans'."""
    import shutil
    src = bundle("clean")
    dst = tmp_path / "b"
    shutil.copytree(src, dst)
    man_path = dst / "MANIFEST.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    n_pages = sum(1 for p in man["pages"] if p.get("status") == 200)
    urls = [f"https://example.test/never-linked-{i}" for i in range(40)]
    man["sitemaps"] = [
        {"url": "https://example.test/sitemap.xml", "status": 200, "kind": "index", "entry_count": 2,
         "entries": [{"loc": "https://example.test/a.xml"}, {"loc": "https://example.test/b.xml"}]},
        {"url": "https://example.test/a.xml", "status": 200, "kind": "urlset", "entry_count": 40,
         "entries": [{"loc": u} for u in urls]},
    ]
    man_path.write_text(json.dumps(man), encoding="utf-8")
    proc = run(CHECK_ACCESS, str(dst), "--stdout")
    assert proc.returncode == 0, proc.stderr
    hits = [f for f in json.loads(proc.stdout)["findings"] if f["check_id"] == "REACH-013"]
    # either the sample is too small to claim orphans (< 10 pages) or the
    # guard withheld the claim because most of the sitemap went unsampled
    assert not hits or n_pages >= 10 and hits[0]["evidence_detail"]["counts"]["orphan_candidates"] <= 20


def test_engine_row_survives_a_probe_that_never_answered(tmp_path):
    """adobe.com holds the connection open for every known crawler name. The
    probe recorded status None and the engine table dropped the row."""
    import shutil
    src = bundle("clean")
    dst = tmp_path / "b"
    shutil.copytree(src, dst)
    probe = json.loads((dst / "ua_probe.json").read_text(encoding="utf-8"))
    for a in probe["agents"].values():
        a.update({"status": None, "bytes": 0, "text_bytes": 0, "challenge_detected": False,
                  "error": "TimeoutError: The read operation timed out"})
    (dst / "ua_probe.json").write_text(json.dumps(probe), encoding="utf-8")
    man_path = dst / "MANIFEST.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    man["ua_probe"] = probe
    man_path.write_text(json.dumps(man), encoding="utf-8")
    proc = run(CHECK_ACCESS, str(dst), "--stdout")
    rows = {r["engine"]: r for r in json.loads(proc.stdout)["engine_reachability"]}
    assert rows["ChatGPT"]["state"] == "blocked"      # baseline was served, the agent was not
    assert "never answers" in rows["ChatGPT"]["detail"]


# --------------------------------------------------------------------------
# Optional extras: the stdlib path must be untouched when they are absent
# --------------------------------------------------------------------------

def test_renderer_auto_degrades_to_none_when_the_check_fails(monkeypatch):
    """`--renderer auto` on a bare install must resolve to no renderer, not
    an error: the documented common case is no browser at all."""
    import subprocess as sp
    mod = _collect_module()

    class Fail:
        returncode = 2
        stdout = ""
        stderr = "playwright unavailable"

    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: Fail())
    assert mod.Collector._resolve_renderer("auto") == (None, None)
    assert mod.Collector._resolve_renderer("none") == (None, None)
    assert mod.Collector._resolve_renderer("node render.js") == (["node", "render.js"], "node render.js")

    class Ok:
        returncode = 0
        stdout = "playwright-chromium 151\n"
        stderr = ""

    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: Ok())
    cmd, name = mod.Collector._resolve_renderer("auto")
    assert cmd and cmd[-1].endswith("render_playwright.py") and name == "playwright-chromium 151"


def test_render_sample_picks_the_seed_and_the_thinnest_pages(tmp_path):
    """Six renders of twenty-five pages have to go where inference is weakest:
    the seed page and the pages with the least text per byte of markup."""
    import argparse
    mod = _collect_module()
    out = tmp_path / "b"
    (out / "pages").mkdir(parents=True)
    args = argparse.Namespace(target="https://x.test/", out=str(out), max_pages=25, timeout=10.0,
                              budget=120.0, concurrency=8, delay=0.0, include=[], exclude=[],
                              renderer="none", render_pages=3, no_probe=True)
    c = mod.Collector(args)
    words = {"p000": 500, "p001": 20, "p002": 900, "p003": 5, "p004": 300}
    for pid, w in words.items():
        (out / "pages" / pid).mkdir()
        (out / "pages" / pid / "extracted.json").write_text(json.dumps(
            {"text": {"main_word_count": w, "text_to_markup_ratio": w / 10000.0}}), encoding="utf-8")
        c.pages.append({"page_id": pid, "url": f"https://x.test/{pid}", "final_url": f"https://x.test/{pid}", "status": 200})
    c.pages[0]["url"] = c.pages[0]["final_url"] = "https://x.test/"
    rendered = []
    c.renderer_cmd = ["fake"]
    c.render = lambda url: rendered.append(url) or "<html><body>rendered</body></html>"
    c.render_sample("https://x.test/")
    assert rendered == ["https://x.test/", "https://x.test/p003", "https://x.test/p001"]
    assert (out / "pages" / "p003" / "rendered.html").exists()
    assert [p["rendered"] for p in c.pages] == [True, True, False, True, False]


def test_probe_controls_settle_what_a_refusal_keys_on(tmp_path):
    """crunchyroll.com: unknown name served, Bytespider refused -> an AI-bot
    rule by name, confidence high. adobe.com: named agents refused or stalled
    while both controls are served -> impersonation defence, and REACH-005 is
    withheld because genuine agents pass it by IP range."""
    import shutil
    src = bundle("clean")
    for scenario, byte_status, expect_finding, expect_state in (
            ("name-rule", 403, True, "blocked"), ("impersonation", 200, False, "partial")):
        dst = tmp_path / scenario
        shutil.copytree(src, dst)
        probe = json.loads((dst / "ua_probe.json").read_text(encoding="utf-8"))
        for a in probe["agents"].values():
            a.update({"status": 403, "challenge_detected": True, "bytes": 5602, "text_bytes": 900})
        probe["controls"] = {
            "BrandAIReadinessAudit-Control": {"user_agent": "x", "status": 200, "bytes": 8687,
                                               "text_bytes": 2000, "challenge_detected": False, "error": None},
            "Bytespider": {"user_agent": "x", "status": byte_status, "bytes": 5602, "text_bytes": 900,
                           "challenge_detected": byte_status == 403, "error": None},
        }
        (dst / "ua_probe.json").write_text(json.dumps(probe), encoding="utf-8")
        man_path = dst / "MANIFEST.json"
        man = json.loads(man_path.read_text(encoding="utf-8"))
        man["ua_probe"] = probe
        man_path.write_text(json.dumps(man), encoding="utf-8")
        proc = run(CHECK_ACCESS, str(dst), "--stdout")
        assert proc.returncode == 0, proc.stderr
        doc = json.loads(proc.stdout)
        hits = [f for f in doc["findings"] if f["check_id"] == "REACH-005"]
        assert bool(hits) == expect_finding, scenario
        if hits:
            assert hits[0]["confidence"] == "high" and "keys on crawler names" in hits[0]["evidence"]
        rows = {r["engine"]: r for r in doc["engine_reachability"]}
        assert rows["ChatGPT"]["state"] == expect_state, (scenario, rows["ChatGPT"])


def test_read_001_measures_the_delta_when_rendered_html_exists(tmp_path):
    """A shell that carries 99 words of chrome and renders 900 is a measured
    finding at high confidence; the old rule needed raw < 50 words."""
    import shutil
    src = bundle("clean")
    dst = tmp_path / "b"
    shutil.copytree(src, dst)
    run_path = dst / "run.json"
    run_doc = json.loads(run_path.read_text(encoding="utf-8"))
    run_doc["renderer"] = {"available": True, "name": "test", "pages_rendered": 1, "pages_attempted": 1}
    run_path.write_text(json.dumps(run_doc), encoding="utf-8")
    man_path = dst / "MANIFEST.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    man["run"] = run_doc
    man_path.write_text(json.dumps(man), encoding="utf-8")
    page = next(p for p in man["pages"] if p.get("status") == 200)
    pdir = dst / "pages" / page["page_id"]
    ex = json.loads((pdir / "extracted.json").read_text(encoding="utf-8"))
    ex["text"]["main_word_count"] = 60
    ex["text"]["word_count"] = 99     # the whole document, which is what rendered.html is compared to
    (pdir / "extracted.json").write_text(json.dumps(ex), encoding="utf-8")
    (pdir / "rendered.html").write_text("<html><body>" + "word " * 900 + "</body></html>", encoding="utf-8")
    proc = run(CHECK_RENDER, str(dst), "--stdout")
    assert proc.returncode == 0, proc.stderr
    f = next((f for f in json.loads(proc.stdout)["findings"] if f["check_id"] == "READ-001"), None)
    assert f is not None and f["confidence"] == "high"
    assert "99 words of body text in its HTML and 900 after rendering" in f["evidence"]
    assert any(r.endswith("rendered.html") for r in f["evidence_detail"]["artifact_refs"])


def test_validator_allows_declared_extras_only_behind_a_guard(tmp_path):
    """playwright and bs4 may be imported inside the zip only where a bare
    install survives their absence."""
    import importlib
    sys.path.insert(0, os.path.join(REPO, "tools"))
    v = importlib.import_module("validate")
    import ast
    ok = ast.parse("try:\n    import bs4\nexcept ImportError:\n    bs4 = None\n")
    bad = ast.parse("import bs4\n")
    assert v._guarded_import_lines(ok) == {2}
    assert v._guarded_import_lines(bad) == set()
    assert "bs4" in v.OPTIONAL_OK and "playwright" in v.OPTIONAL_OK
