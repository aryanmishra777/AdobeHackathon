#!/usr/bin/env python3
"""Validate an audit report against the marketplace contract.

Standard library only -- this ships inside the submission and must run on a
bare Python 3.9+ install with no pip step.

We deliberately do not depend on a JSON Schema library. This implements the
subset of the schema the report actually uses (required keys, enums, types,
patterns, ranges, nesting) plus the cross-field invariants a schema cannot
express -- severity counts matching the findings array, ids being sequential
and correctly ordered, artifact refs resolving against the bundle.

Usage:
    python validate_report.py report.json
    python validate_report.py report.json --bundle .audit/example.com/run-01
    python validate_report.py report.json --quiet

Exit codes:
    0  valid
    1  invalid (errors printed to stderr)
    2  could not read or parse the report
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime

SEVERITIES = ("critical", "high", "medium", "low")
CONFIDENCES = ("high", "medium", "low")
DETERMINISM = ("deterministic", "model-judged")
CATEGORIES = ("discoverability", "engagement")
MECHANISMS = ("reach", "read", "parse", "quote", "trust", "stay")
SCOPES = ("site-wide", "section", "page")
EFFORTS = ("S", "M", "L")
GRADES = ("A", "B", "C", "D", "F")

CHECK_ID_RE = re.compile(r"^(REACH|READ|PARSE|QUOTE|TRUST|STAY)-\d{3}$")
FINDING_ID_RE = re.compile(r"^F-\d{3,}$")
PROACTIVE_ID_RE = re.compile(r"^P-\d{3,}$")

SEVERITY_ORDER = {s: i for i, s in enumerate(SEVERITIES)}

# See merge_findings.SITE_LEVEL_ARTIFACTS. Kept in sync deliberately rather than
# shared, because each script must run standalone from inside its own skill.
SITE_LEVEL_ARTIFACTS = ("robots.txt.raw", "robots_fetch.json", "MANIFEST.json",
                        "ua_probe.json", "coverage.json", "run.json", "sitemaps/")


def _is_site_level(finding: dict) -> bool:
    detail = finding.get("evidence_detail") or {}
    if detail.get("pages_affected"):
        return False
    refs = detail.get("artifact_refs") or []
    return any(str(r).startswith(SITE_LEVEL_ARTIFACTS) for r in refs)


class Report:
    """Accumulates errors and warnings with dotted paths for context."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, path: str, msg: str) -> None:
        self.errors.append(f"{path}: {msg}")

    def warn(self, path: str, msg: str) -> None:
        self.warnings.append(f"{path}: {msg}")


def _req(obj, key, path, rep, types=None, enum=None, pattern=None,
         minlen=None, minimum=None, maximum=None):
    """Check a required key, then validate it. Returns the value or None."""
    if not isinstance(obj, dict) or key not in obj:
        rep.error(path, f"missing required key '{key}'")
        return None
    return _opt(obj, key, path, rep, types, enum, pattern, minlen, minimum, maximum)


def _opt(obj, key, path, rep, types=None, enum=None, pattern=None,
         minlen=None, minimum=None, maximum=None):
    """Validate an optional key if present. Returns the value or None."""
    if not isinstance(obj, dict) or key not in obj:
        return None
    val = obj[key]
    where = f"{path}.{key}"
    if types is not None and not isinstance(val, types):
        names = types if isinstance(types, tuple) else (types,)
        rep.error(where, f"expected {'/'.join(t.__name__ for t in names)}, got {type(val).__name__}")
        return val
    if enum is not None and val not in enum:
        rep.error(where, f"must be one of {list(enum)}, got {val!r}")
    if pattern is not None and isinstance(val, str) and not pattern.match(val):
        rep.error(where, f"{val!r} does not match {pattern.pattern}")
    if minlen is not None and hasattr(val, "__len__") and len(val) < minlen:
        rep.error(where, f"length {len(val)} is below minimum {minlen}")
    if minimum is not None and isinstance(val, (int, float)) and val < minimum:
        rep.error(where, f"{val} is below minimum {minimum}")
    if maximum is not None and isinstance(val, (int, float)) and val > maximum:
        rep.error(where, f"{val} exceeds maximum {maximum}")
    return val


def validate_suggested_action(sa, path, rep) -> None:
    if not isinstance(sa, dict):
        rep.error(path, "suggested_action must be an object")
        return
    _req(sa, "summary", path, rep, types=str, minlen=10)
    _req(sa, "priority", path, rep, enum=SEVERITIES)
    _req(sa, "effort", path, rep, enum=EFFORTS)
    _req(sa, "impact_rationale", path, rep, types=str, minlen=20)
    steps = _req(sa, "steps", path, rep, types=list, minlen=1)
    if isinstance(steps, list):
        for i, s in enumerate(steps):
            if not isinstance(s, str) or not s.strip():
                rep.error(f"{path}.steps[{i}]", "each step must be a non-empty string")
    code = sa.get("code")
    if isinstance(code, str) and code.strip():
        # A templated placeholder shipped to a site owner will be pasted verbatim.
        for placeholder in ("YOUR_", "example.com/REPLACE", "TODO", "<your ", "XXX"):
            if placeholder.lower() in code.lower():
                rep.warn(f"{path}.code",
                         f"contains placeholder {placeholder!r}; tailor snippets to the audited site")
                break


def validate_finding(f, idx, rep, seen_ids, bundle_files) -> dict:
    path = f"findings[{idx}]"
    if not isinstance(f, dict):
        rep.error(path, "finding must be an object")
        return {}

    fid = _req(f, "id", path, rep, types=str, pattern=FINDING_ID_RE)
    if fid is not None:
        if fid in seen_ids:
            rep.error(f"{path}.id", f"duplicate finding id {fid!r}")
        seen_ids.add(fid)

    _req(f, "check_id", path, rep, types=str, pattern=CHECK_ID_RE)
    _req(f, "title", path, rep, types=str, minlen=10)
    sev = _req(f, "severity", path, rep, enum=SEVERITIES)
    conf = _req(f, "confidence", path, rep, enum=CONFIDENCES)
    det = _req(f, "determinism", path, rep, enum=DETERMINISM)
    _req(f, "category", path, rep, enum=CATEGORIES)
    _req(f, "mechanism", path, rep, enum=MECHANISMS)
    evidence = _req(f, "evidence", path, rep, types=str, minlen=20)
    _req(f, "verification", path, rep, types=str, minlen=15)

    title = f.get("title")
    if isinstance(evidence, str) and isinstance(title, str):
        if evidence.strip().lower() == title.strip().lower():
            rep.error(f"{path}.evidence",
                      "evidence restates the title; it must state what was observed")

    # Gate 3: the model-judged ceiling.
    if det == "model-judged" and sev == "critical":
        rep.error(path,
                  "a model-judged finding may not be 'critical' "
                  "(false-positive gate 3); cap at 'high'")

    detail = _req(f, "evidence_detail", path, rep, types=dict)
    if isinstance(detail, dict):
        refs = _req(detail, "artifact_refs", f"{path}.evidence_detail", rep,
                    types=list, minlen=1)
        # Gate 2: a finding that cannot cite its evidence is deleted, not downgraded.
        if isinstance(refs, list) and bundle_files is not None:
            for r in refs:
                if isinstance(r, str) and r not in bundle_files:
                    rep.error(f"{path}.evidence_detail.artifact_refs",
                              f"{r!r} does not resolve in the bundle")

    scope_obj = _req(f, "affected_scope", path, rep, types=dict)
    if isinstance(scope_obj, dict):
        sp = f"{path}.affected_scope"
        checked = _req(scope_obj, "pages_checked", sp, rep, types=int, minimum=0)
        affected = _req(scope_obj, "pages_affected", sp, rep, types=int, minimum=0)
        scope = _req(scope_obj, "scope", sp, rep, enum=SCOPES)
        if isinstance(checked, int) and isinstance(affected, int):
            if affected > checked:
                rep.error(sp, f"pages_affected ({affected}) exceeds pages_checked ({checked})")
            # Gate 5: sample size. Exempt findings evidenced by a site-level
            # artifact -- those are not generalizations from a page sample.
            if scope == "site-wide" and not _is_site_level(f):
                if checked < 3:
                    rep.error(sp, f"site-wide scope requires >=3 pages checked, got {checked}")
                elif checked and affected / checked < 0.6:
                    rep.error(sp,
                              f"site-wide scope requires >=60% affected, "
                              f"got {affected}/{checked}")
            elif scope == "site-wide" and _is_site_level(f) and affected:
                rep.error(sp, "a site-level finding must not also claim affected pages; "
                              "list them and let the sample-size gate apply")
        if scope == "section" and not scope_obj.get("section"):
            rep.warn(sp, "scope is 'section' but no section path is given")

    sa = _req(f, "suggested_action", path, rep, types=dict)
    if sa is not None:
        validate_suggested_action(sa, f"{path}.suggested_action", rep)

    return {"id": fid, "severity": sev, "check_id": f.get("check_id"),
            "confidence": conf, "scope": (scope_obj or {}).get("scope")}


def validate_report(doc, bundle_files, rep) -> None:
    if not isinstance(doc, dict):
        rep.error("$", "report must be a JSON object")
        return

    _req(doc, "site", "$", rep, types=str, minlen=1)
    audited = _req(doc, "audited_at", "$", rep, types=str)
    if isinstance(audited, str):
        try:
            datetime.fromisoformat(audited.replace("Z", "+00:00"))
        except ValueError:
            rep.error("$.audited_at", f"{audited!r} is not ISO-8601")

    findings = _req(doc, "findings", "$", rep, types=list)
    if findings is None:
        findings = []

    seen_ids: set[str] = set()
    summaries = [validate_finding(f, i, rep, seen_ids, bundle_files)
                 for i, f in enumerate(findings)]

    summary = _req(doc, "summary", "$", rep, types=dict)
    if isinstance(summary, dict):
        counts = {s: 0 for s in SEVERITIES}
        for s in summaries:
            if s.get("severity") in counts:
                counts[s["severity"]] += 1
        _req(summary, "total_findings", "$.summary", rep, types=int, minimum=0)
        for sev in SEVERITIES:
            _req(summary, sev, "$.summary", rep, types=int, minimum=0)
        if summary.get("total_findings") is not None:
            if summary["total_findings"] != len(findings):
                rep.error("$.summary.total_findings",
                          f"says {summary['total_findings']}, findings array has {len(findings)}")
        for sev in SEVERITIES:
            if summary.get(sev) is not None and summary[sev] != counts[sev]:
                rep.error(f"$.summary.{sev}",
                          f"says {summary[sev]}, findings contain {counts[sev]}")

    # Determinism: ids must be sequential and match the documented sort order.
    ids = [s["id"] for s in summaries if s.get("id")]
    expected = [f"F-{i:03d}" for i in range(1, len(ids) + 1)]
    if ids != expected:
        rep.error("$.findings", "ids must be sequential from F-001 in report order")

    keyed = [(SEVERITY_ORDER.get(s.get("severity"), 99), s.get("check_id") or "")
             for s in summaries]
    if keyed != sorted(keyed):
        rep.error("$.findings",
                  "findings must be sorted by severity (critical->low) then check_id; "
                  "unsorted output breaks run-to-run determinism")

    scorecard = _opt(doc, "scorecard", "$", rep, types=dict)
    if isinstance(scorecard, dict):
        crit_by_cat = {"discoverability": False, "engagement": False}
        for f in findings:
            if isinstance(f, dict) and f.get("severity") == "critical":
                cat = f.get("category")
                if cat in crit_by_cat:
                    crit_by_cat[cat] = True
        for axis in ("discoverability", "engagement"):
            ax = _req(scorecard, axis, "$.scorecard", rep, types=dict)
            if isinstance(ax, dict):
                if ax.get("grade") == "not assessed":
                    # An axis nobody measured: null score, a reason, and no
                    # critical-cap logic -- there is nothing to cap.
                    if ax.get("score") is not None:
                        rep.error(f"$.scorecard.{axis}.score",
                                  "a 'not assessed' axis must carry score null, "
                                  f"got {ax.get('score')!r}")
                    _req(ax, "reason", f"$.scorecard.{axis}", rep, types=str, minlen=10)
                    _req(ax, "headline", f"$.scorecard.{axis}", rep, types=str, minlen=10)
                    continue
                score = _req(ax, "score", f"$.scorecard.{axis}", rep,
                             types=int, minimum=0, maximum=100)
                _req(ax, "grade", f"$.scorecard.{axis}", rep, enum=GRADES)
                _req(ax, "headline", f"$.scorecard.{axis}", rep, types=str, minlen=10)
                # A critical finding caps its axis at D.
                if crit_by_cat[axis] and isinstance(score, int) and score > 54:
                    rep.error(f"$.scorecard.{axis}.score",
                              f"a critical {axis} finding caps this axis at 54, got {score}")
        _req(scorecard, "verdict", "$.scorecard", rep, types=str, minlen=20)

    coverage = _opt(doc, "coverage", "$", rep, types=dict)
    if isinstance(coverage, dict):
        complete = _req(coverage, "complete", "$.coverage", rep, types=bool)
        _req(coverage, "pages_sampled", "$.coverage", rep, types=int, minimum=0)
        if complete is False and not coverage.get("limitations"):
            rep.error("$.coverage.limitations",
                      "coverage is incomplete but no limitations are recorded; "
                      "a partial crawl must not read as a clean bill of health")

    proactive = _opt(doc, "proactive_recommendations", "$", rep, types=list)
    if isinstance(proactive, list):
        for i, p in enumerate(proactive):
            pp = f"proactive_recommendations[{i}]"
            if not isinstance(p, dict):
                rep.error(pp, "must be an object")
                continue
            _req(p, "id", pp, rep, types=str, pattern=PROACTIVE_ID_RE)
            _req(p, "title", pp, rep, types=str, minlen=10)
            _req(p, "rationale", pp, rep, types=str, minlen=20)
            sa = _req(p, "suggested_action", pp, rep, types=dict)
            if sa is not None:
                validate_suggested_action(sa, f"{pp}.suggested_action", rep)

    plan = _opt(doc, "priority_plan", "$", rep, types=list)
    if isinstance(plan, list):
        known = {s["id"] for s in summaries if s.get("id")}
        for i, item in enumerate(plan):
            ip = f"priority_plan[{i}]"
            if not isinstance(item, dict):
                rep.error(ip, "must be an object")
                continue
            _req(item, "rank", ip, rep, types=int, minimum=1)
            _req(item, "action", ip, rep, types=str, minlen=10)
            _req(item, "why_first", ip, rep, types=str, minlen=20)
            fids = _req(item, "finding_ids", ip, rep, types=list, minlen=1)
            if isinstance(fids, list):
                for fid in fids:
                    if fid not in known:
                        rep.error(f"{ip}.finding_ids",
                                  f"{fid!r} is not a finding in this report")
        ranks = [i.get("rank") for i in plan if isinstance(i, dict)]
        if ranks != list(range(1, len(ranks) + 1)):
            rep.error("$.priority_plan", "ranks must be sequential from 1 in array order")

    # Both halves of the problem must be represented in the audit.
    cats = {f.get("category") for f in findings if isinstance(f, dict)}
    skipped = set()
    if isinstance(coverage, dict):
        for entry in coverage.get("checks_skipped") or []:
            if isinstance(entry, dict) and isinstance(entry.get("check_id"), str):
                skipped.add(entry["check_id"][:5])
    if findings and "engagement" not in cats and "STAY-" not in skipped:
        rep.warn("$.findings",
                 "no engagement findings and none recorded as skipped; "
                 "engagement-audit may not have run")


def collect_bundle_files(bundle_root: str) -> set[str] | None:
    if not bundle_root:
        return None
    if not os.path.isdir(bundle_root):
        print(f"warning: bundle path {bundle_root!r} is not a directory; "
              f"skipping artifact_refs resolution", file=sys.stderr)
        return None
    found = set()
    for dirpath, _dirnames, filenames in os.walk(bundle_root):
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), bundle_root)
            found.add(rel.replace(os.sep, "/"))
    return found


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", help="path to report.json")
    ap.add_argument("--bundle", default="",
                    help="evidence bundle root, to verify evidence_detail.artifact_refs resolve")
    ap.add_argument("--quiet", action="store_true", help="print nothing on success")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args(argv)

    try:
        with open(args.report, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except FileNotFoundError:
        print(f"error: no such file: {args.report}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: {args.report} is not valid JSON: {exc}", file=sys.stderr)
        return 2

    rep = Report()
    validate_report(doc, collect_bundle_files(args.bundle), rep)

    for w in rep.warnings:
        print(f"warning  {w}", file=sys.stderr)
    for e in rep.errors:
        print(f"error    {e}", file=sys.stderr)

    if rep.errors or (args.strict and rep.warnings):
        n = len(rep.errors) + (len(rep.warnings) if args.strict else 0)
        print(f"\nFAIL: {args.report} ({n} problem{'s' if n != 1 else ''})", file=sys.stderr)
        return 1

    if not args.quiet:
        n = len(doc.get("findings", []))
        extra = f", {len(rep.warnings)} warning(s)" if rep.warnings else ""
        print(f"OK: {args.report} is a valid audit report ({n} findings{extra})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
