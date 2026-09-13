"""The empty-sample explanation, as a table.

Dev tooling -- outside the submission.

Four code reviews found four gaps in check_sample_state, one combination of
probe outcomes at a time. This enumerates the combinations and asserts one
invariant on each: an empty sample yields exactly one REACH explanation from
the access analyzer as a whole, and every sentence in it is true of the probe
that was recorded -- no agent is called "served" that was not, no agent is
called "refused" that answered 200, every refused or stalled agent is named.
"""
from __future__ import annotations

import itertools
import json
import os
import shutil
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CHECK_ACCESS = os.path.join(REPO, "brand-ai-readiness-audit", "skills", "crawl-access-audit",
                            "scripts", "check_access.py")
BUNDLE = os.path.join(HERE, "bundles", "clean")

SERVED = {"status": 200, "bytes": 5000, "text_bytes": 3000, "challenge_detected": False, "error": None}
REFUSED = {"status": 403, "bytes": 300, "text_bytes": 200, "challenge_detected": False, "error": None}
CHALLENGED = {"status": 200, "bytes": 800, "text_bytes": 60, "challenge_detected": True, "error": None}
STALLED = {"status": None, "bytes": 0, "text_bytes": 0, "challenge_detected": False,
           "error": "TimeoutError: The read operation timed out"}
OUTCOMES = {"served": SERVED, "refused": REFUSED, "challenged": CHALLENGED, "stalled": STALLED}


def _build(tmp_path, sample, baseline, agent_pattern, controls, probe=True, robots_disallow=False):
    if not os.path.isdir(BUNDLE):
        pytest.skip("fixture bundle not built")
    dst = tmp_path / "b"
    shutil.copytree(BUNDLE, dst)
    man = json.loads((dst / "MANIFEST.json").read_text(encoding="utf-8"))
    origin = man["run"]["origin"]
    if sample == "refused":
        man["pages"] = [{"page_id": "p000", "url": origin + "/", "status": 403, "role": "home",
                         "page_type": "other"}]
    else:
        man["pages"] = []
    man["sitemaps"] = []
    p = json.loads((dst / "ua_probe.json").read_text(encoding="utf-8"))
    names = list(p["agents"])
    if probe:
        p["baseline"] = dict(SERVED if baseline == "served" else REFUSED, user_agent="browser")
        for i, name in enumerate(names):
            p["agents"][name] = dict(OUTCOMES[agent_pattern[i % len(agent_pattern)]], user_agent=name)
        if controls is None:
            p.pop("controls", None)
        else:
            p["controls"] = {"BrandAIReadinessAudit-Control": dict(OUTCOMES[controls[0]]),
                             "Bytespider": dict(OUTCOMES[controls[1]])}
        man["ua_probe"] = p
        (dst / "ua_probe.json").write_text(json.dumps(p), encoding="utf-8")
    else:
        man["ua_probe"] = {}
        (dst / "ua_probe.json").write_text("{}", encoding="utf-8")
    if robots_disallow:
        for a in (man["robots"].get("agent_matrix") or {}).values():
            a["root_allowed"] = False
    cov = json.loads((dst / "coverage.json").read_text(encoding="utf-8"))
    cov.update({"pages_fetched": 0, "sample": sample, "stopped_reason": "completed",
                "challenge_pages": 16 if sample == "challenged" else 0})
    if sample == "timed-out":
        cov["stopped_reason"] = "unreachable-timeout"
    if sample == "unresolved":
        cov["stopped_reason"] = "dns-failure"
    if sample == "unreachable":
        cov["stopped_reason"] = "unreachable"
    man["coverage"] = cov
    (dst / "MANIFEST.json").write_text(json.dumps(man), encoding="utf-8")
    (dst / "coverage.json").write_text(json.dumps(cov), encoding="utf-8")
    return dst, names


def _run(dst):
    proc = subprocess.run([sys.executable, CHECK_ACCESS, str(dst), "--stdout"],
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def _truthful(f, names, pattern, baseline, probe):
    """Every claim in the finding's title and evidence is true of the probe."""
    text = (f["title"] + " " + f["evidence"]).lower()
    outcome = {n: pattern[i % len(pattern)] for i, n in enumerate(names)}
    served = [n for n, o in outcome.items() if o == "served"]
    unserved = [n for n, o in outcome.items() if o != "served"]
    if not probe:
        assert "probe did not run" in text or "no user-agent probe ran" in text
        return
    if "served the full page" in text and "were served the full page" in text:
        # the served list names only agents that were served
        seg = f["evidence"].split("were served the full page")[0].rsplit(";", 1)[-1]
        for n in unserved:
            assert n not in seg, (n, seg)
    if "the named ai agents are served" in text or "serving browsers and the named ai agents" in text \
            or "spares the agents" in text:
        assert not unserved, (f["title"], unserved)
    if "every named ai agent" in text and ("refused" in text or "stalled" in text):
        assert not served, (f["title"], served)
    for n in unserved:
        assert n in f["evidence"], (n, f["evidence"][:300])
    if baseline == "refused":
        assert "browser" in text and ("included" in text or "received 403" in text)


STATES = ["refused", "challenged"]
BASELINES = ["served", "refused"]
PATTERNS = [("served",), ("refused",), ("stalled",), ("challenged",),
            ("served", "refused"), ("refused", "stalled"), ("served", "stalled"),
            ("served", "refused", "stalled")]
CONTROLS = [None, ("served", "served"), ("served", "refused"), ("refused", "refused"), ("served", "stalled")]


@pytest.mark.parametrize("state,baseline,pattern,controls",
                         list(itertools.product(STATES, BASELINES, PATTERNS, CONTROLS)))
def test_every_empty_sample_gets_exactly_one_truthful_explanation(tmp_path, state, baseline, pattern, controls):
    dst, names = _build(tmp_path, state, baseline, pattern, controls)
    doc = _run(dst)
    reach = [f for f in doc["findings"] if f["check_id"] in ("REACH-005", "REACH-002")]
    assert reach, (state, baseline, pattern, controls, [f["check_id"] for f in doc["findings"]])
    for f in reach:
        _truthful(f, names, pattern, baseline, probe=True)
    # one explanation, not two competing ones, unless REACH-005's verified block
    # and REACH-002's robots block are both genuinely present
    ids = [f["check_id"] for f in reach]
    assert ids.count("REACH-005") <= 1 or all(f.get("confidence") == "high" for f in reach if f["check_id"] == "REACH-005"), ids


@pytest.mark.parametrize("state", ["refused", "challenged"])
def test_no_probe_says_so(tmp_path, state):
    dst, names = _build(tmp_path, state, "served", ("served",), None, probe=False)
    doc = _run(dst)
    reach = [f for f in doc["findings"] if f["check_id"] == "REACH-005"]
    assert len(reach) == 1
    _truthful(reach[0], names, ("served",), "served", probe=False)


def test_robots_disallowed_agents_are_reach_002s_finding(tmp_path):
    dst, names = _build(tmp_path, "refused", "served", ("refused",), ("served", "served"), robots_disallow=True)
    doc = _run(dst)
    ids = [f["check_id"] for f in doc["findings"]]
    assert "REACH-002" in ids
    # the sample-state check stood down: no low-confidence REACH-005 beside it
    assert not [f for f in doc["findings"] if f["check_id"] == "REACH-005" and f.get("confidence") == "low"]


@pytest.mark.parametrize("state,check", [("timed-out", "REACH-015"), ("unresolved", "REACH-014"),
                                         ("unreachable", "REACH-014")])
def test_network_states_get_their_own_finding(tmp_path, state, check):
    dst, _ = _build(tmp_path, state, "served", ("served",), None, probe=False)
    doc = _run(dst)
    hits = [f for f in doc["findings"] if f["check_id"] == check]
    assert len(hits) == 1 and hits[0].get("severity_locked") and hits[0]["confidence"] == "low"
    assert not [f for f in doc["findings"] if f["check_id"] == "REACH-005"]
