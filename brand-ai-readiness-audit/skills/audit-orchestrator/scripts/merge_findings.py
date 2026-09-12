#!/usr/bin/env python3
"""Merge candidate findings from the analysis skills into the final report body.

Standard library only -- ships inside the submission.

Implements steps 5, 6 and 8 of the orchestrator procedure deterministically, so
that the parts of the audit that should not vary between runs do not vary:

  5. de-duplicate, collapse page-level into site-level, resolve supersession
  6. compute severity (base -> scope -> confidence -> model-judged ceiling)
  8. sort and assign sequential ids

The model still decides *what* to report and writes the prose. This script
decides *how the reported set is shaped*, which is exactly the part that must be
reproducible.

Usage:
    python merge_findings.py candidates.json --out merged.json
    python merge_findings.py c1.json c2.json c3.json --out merged.json
    python merge_findings.py candidates.json --pages-sampled 12 --stdout

Input: a JSON array of candidate findings, or an object with a "findings" key.
Multiple input files are concatenated. Output: an object with "findings",
"summary", "scorecard_input" and "merge_log".
"""

from __future__ import annotations

import argparse
import json
import os
import sys

SEVERITIES = ["critical", "high", "medium", "low"]
SEVERITY_INDEX = {s: i for i, s in enumerate(SEVERITIES)}

BASE_DEDUCTION = {"critical": 35, "high": 15, "medium": 6, "low": 2}
SCOPE_MULTIPLIER = {"site-wide": 1.0, "section": 0.6, "page": 0.3}
CONFIDENCE_MULTIPLIER = {"high": 1.0, "medium": 0.8, "low": 0.5}
SUPERSEDED_MULTIPLIER = 0.25

# Severities that represent a broken mechanism rather than untidiness.
BLOCKING_SEVERITIES = ("critical", "high")
# The most that low + medium findings can subtract from one axis, together.
HYGIENE_DEDUCTION_CAP = 25.0

MECHANISM_ORDER = ["reach", "read", "parse", "quote", "trust", "stay"]

SITE_WIDE_MIN_PAGES = 3
SITE_WIDE_MIN_RATIO = 0.6

# Artifacts that describe the whole origin rather than any particular page. A
# finding evidenced only by these is site-level by nature -- "robots.txt blocks
# every crawler" has no per-page evidence and needs none -- so the sample-size
# gate, which exists to stop generalizing from too few sampled PAGES, does not
# apply to it.
SITE_LEVEL_ARTIFACTS = ("robots.txt.raw", "robots_fetch.json", "MANIFEST.json",
                        "ua_probe.json", "coverage.json", "run.json", "sitemaps/")


def is_site_level(finding: dict) -> bool:
    detail = finding.get("evidence_detail") or {}
    if detail.get("pages_affected"):
        return False  # the claim is derived from sampled pages after all
    refs = detail.get("artifact_refs") or []
    return any(str(r).startswith(SITE_LEVEL_ARTIFACTS) for r in refs)

DEFAULT_SUPERSESSION = [
    {"root_cause": "READ-001",
     "supersedes": ["PARSE-001", "QUOTE-001", "QUOTE-002", "QUOTE-003"],
     "scope": "page"},
    {"root_cause": "REACH-002",
     "supersedes": ["REACH-005", "REACH-006", "REACH-007"],
     "scope": "site"},
    {"root_cause": "REACH-008",
     "supersedes": ["PARSE-001", "PARSE-004"],
     "scope": "page"},
    {"root_cause": "READ-013",
     "supersedes": ["READ-001", "QUOTE-001", "STAY-001"],
     "scope": "page"},
]


def shift(severity: str, steps: int) -> str:
    """Move severity up (negative steps) or down (positive), clamped."""
    idx = SEVERITY_INDEX.get(severity)
    if idx is None:
        return severity
    return SEVERITIES[max(0, min(len(SEVERITIES) - 1, idx + steps))]


def compute_severity(finding: dict, log: list[str]) -> str:
    """Apply the severity rubric. The base level is whatever the analysis skill
    proposed; the modifiers are ours and are not negotiable."""
    sev = finding.get("severity", "medium")
    if sev not in SEVERITY_INDEX:
        log.append(f"{finding.get('check_id')}: unknown severity {sev!r}, treating as medium")
        sev = "medium"

    scope_obj = finding.get("affected_scope") or {}
    scope = scope_obj.get("scope")
    cid = finding.get("check_id", "?")

    # A check may pin its severity when the registry says the level is fixed --
    # REACH-003 (training-crawler opt-out) is informational by definition, and
    # escalating it would contradict a binding false-positive guard.
    if finding.get("severity_locked"):
        return sev

    # Step 2 -- scope modifier.
    #
    # Only applies when site-wide scope was DERIVED from page sampling. For a
    # finding evidenced by a site-level artifact, the registry's severity_rule
    # already reasons about the whole origin -- "no sitemap on a 50+ URL site is
    # high" is the site-wide answer, so escalating it again double-counts and
    # inflates ordinary defects into hard blocks.
    if scope == "site-wide" and not is_site_level(finding):
        # `medium` is DEFINED as "measurable degradation across sampled pages",
        # so breadth is already priced into it -- promoting it again for being
        # site-wide double-counts the same property, and turns the rubric's own
        # example of a medium ("no breadcrumbs") into the severity it reserves
        # for "no structured data anywhere on a commerce site". Breadth still
        # sharpens the bands where it adds something: hygiene seen everywhere is
        # a real degradation, and a whole class of facts missing everywhere is a
        # hard block.
        if sev == "medium":
            log.append(f"{cid}: site-wide, held at medium "
                       f"(breadth is already in the medium definition)")
        else:
            new = shift(sev, -1)
            if new != sev:
                log.append(f"{cid}: escalated {sev} -> {new} (site-wide scope)")
            sev = new
    elif scope == "page" and not is_site_level(finding) and not _is_primary_page(finding):
        new = shift(sev, 1)
        if new != sev:
            log.append(f"{cid}: de-escalated {sev} -> {new} (single non-primary page)")
        sev = new

    # False-positive gate 3: a model-judged finding may never be critical
    # without deterministic corroboration. Enforce it here rather than leaving
    # validate_report to reject the finished report -- merging keeps the worst
    # severity of a group and site-wide scope can escalate, so a model-judged
    # finding can reach critical without any single check asking for it.
    if finding.get("determinism") == "model-judged" and sev == "critical":
        sev = "high"
        log.append(f"{cid}: capped critical -> high (model-judged, gate 3)")

    # Step 3 -- confidence never escalates, only pulls down.
    if finding.get("confidence") == "low":
        new = shift(sev, 1)
        if new != sev:
            log.append(f"{cid}: de-escalated {sev} -> {new} (low confidence)")
        sev = new

    return sev


def _is_primary_page(finding: dict) -> bool:
    """Home and conversion pages are exempt from the single-page de-escalation:
    a defect on the home page is not a minor defect."""
    pages = (finding.get("evidence_detail") or {}).get("pages_affected") or []
    for p in pages:
        path = str(p).rstrip("/")
        tail = path.split("://")[-1]
        if "/" not in tail or tail.endswith(".com") or tail.endswith(".org"):
            return True
        low = path.lower()
        # Help, support and FAQ pages count too: they hold the policy facts
        # (returns, delivery, payment) an assistant is asked for most, so a
        # defect there degrades a whole class of answers, not one page.
        if any(k in low for k in ("/pricing", "/plans", "/contact", "/buy", "/checkout",
                                  "/help", "/support", "/faq")):
            return True
    return False


def apply_model_judged_ceiling(findings: list[dict], log: list[str]) -> None:
    """Gate 3: a model-judged finding may not be critical unless a deterministic
    finding corroborates it on the same scope."""
    deterministic_scopes = set()
    for f in findings:
        if f.get("determinism") == "deterministic":
            for p in (f.get("evidence_detail") or {}).get("pages_affected") or []:
                deterministic_scopes.add(p)
            if (f.get("affected_scope") or {}).get("scope") == "site-wide":
                deterministic_scopes.add("*")

    for f in findings:
        if f.get("determinism") != "model-judged" or f.get("severity") != "critical":
            continue
        pages = (f.get("evidence_detail") or {}).get("pages_affected") or []
        corroborated = "*" in deterministic_scopes or any(p in deterministic_scopes for p in pages)
        if not corroborated:
            f["severity"] = "high"
            log.append(f"{f.get('check_id')}: capped critical -> high "
                       f"(model-judged, no deterministic corroboration)")


def scope_key(finding: dict) -> tuple:
    scope_obj = finding.get("affected_scope") or {}
    pages = (finding.get("evidence_detail") or {}).get("pages_affected") or []
    return (scope_obj.get("scope"), scope_obj.get("section"), tuple(sorted(str(p) for p in pages)))


def dedupe(findings: list[dict], log: list[str]) -> list[dict]:
    """One defect, reported once.

    Candidates collide when they share a check_id AND a title. Page overlap is
    deliberately not required: a check that fires on eleven different pages has
    found one site-wide defect eleven times, not eleven defects, and a report
    that lists "The top of the page does not say what this is" eleven times is
    one nobody will read to the end of.

    Title is part of the key because a single check may legitimately describe
    different problems -- REACH-014 reports an https failure and mixed content
    under one id -- and those must not be folded together.
    """
    by_key: dict[tuple, list[dict]] = {}
    order: list[tuple] = []
    for f in findings:
        key = (f.get("check_id", "?"), f.get("title", ""))
        if key not in by_key:
            order.append(key)
        by_key.setdefault(key, []).append(f)

    merged: list[dict] = []
    for key in order:
        group = by_key[key]
        head = group[0]
        if len(group) > 1:
            for other in group[1:]:
                _absorb(head, other)
            pages = (head.get("evidence_detail") or {}).get("pages_affected") or []
            checked = (head.get("affected_scope") or {}).get("pages_checked") or 0
            if len(pages) > 1:
                shown = ", ".join(str(u) for u in pages[:3])
                head["evidence"] = (
                    (head.get("evidence") or "").rstrip().rstrip(".")
                    + f". Observed on {len(pages)}"
                    + (f" of {checked}" if checked else "")
                    + f" sampled pages: {shown}"
                    + ("..." if len(pages) > 3 else "") + ".")
            log.append(f"{key[0]}: merged {len(group)} candidates into 1 "
                       f"({len(pages)} pages affected)")
        merged.append(head)
    return merged


def _absorb(target: dict, other: dict) -> None:
    """Fold `other` into `target`, unioning evidence and keeping the worse severity."""
    td = target.setdefault("evidence_detail", {})
    od = other.get("evidence_detail") or {}
    for key in ("pages_affected", "artifact_refs"):
        combined = list(td.get(key) or []) + list(od.get(key) or [])
        seen, out = set(), []
        for item in combined:
            if item not in seen:
                seen.add(item)
                out.append(item)
        td[key] = out
    tc = td.setdefault("counts", {})
    for k, v in (od.get("counts") or {}).items():
        if isinstance(v, (int, float)):
            tc[k] = tc.get(k, 0) + v
    if SEVERITY_INDEX.get(other.get("severity"), 9) < SEVERITY_INDEX.get(target.get("severity"), 9):
        target["severity"] = other["severity"]
    ts = target.setdefault("affected_scope", {})
    os_ = other.get("affected_scope") or {}
    ts["pages_affected"] = len(td.get("pages_affected") or []) or \
        max(ts.get("pages_affected", 0), os_.get("pages_affected", 0))
    ts["pages_checked"] = max(ts.get("pages_checked", 0), os_.get("pages_checked", 0))


def collapse_to_site_wide(findings: list[dict], pages_sampled: int, log: list[str]) -> None:
    """When one check fires on >=60% of sampled pages and on >=3 pages, it is one
    site-wide finding, not N page findings. Nobody can act on forty rows."""
    if pages_sampled <= 0:
        return
    for f in findings:
        scope_obj = f.setdefault("affected_scope", {})
        affected = len((f.get("evidence_detail") or {}).get("pages_affected") or []) \
            or scope_obj.get("pages_affected", 0)
        scope_obj.setdefault("pages_checked", pages_sampled)
        checked = scope_obj.get("pages_checked") or pages_sampled
        if scope_obj.get("scope") == "site-wide":
            # Gate 5 constrains generalization from sampled pages. A finding
            # evidenced by a site-level artifact is not a generalization at all.
            if is_site_level(f):
                continue
            if checked < SITE_WIDE_MIN_PAGES or (checked and affected / checked < SITE_WIDE_MIN_RATIO):
                scope_obj["scope"] = "section" if affected > 1 else "page"
                log.append(f"{f.get('check_id')}: demoted site-wide -> {scope_obj['scope']} "
                           f"({affected}/{checked} pages, gate 5)")
            continue
        if (checked >= SITE_WIDE_MIN_PAGES and affected >= SITE_WIDE_MIN_PAGES
                and affected / checked >= SITE_WIDE_MIN_RATIO):
            scope_obj["scope"] = "site-wide"
            log.append(f"{f.get('check_id')}: collapsed to site-wide "
                       f"({affected}/{checked} pages)")


def apply_supersession(findings: list[dict], rules: list[dict], log: list[str]) -> None:
    """A root cause at an earlier stage explains its downstream symptoms. Keep
    both, but mark the symptoms so they stop being counted as peers."""
    present = {}
    for f in findings:
        present.setdefault(f.get("check_id"), []).append(f)

    for rule in rules:
        roots = present.get(rule["root_cause"])
        if not roots:
            continue
        root_pages = set()
        site_wide_root = False
        for r in roots:
            root_pages |= set((r.get("evidence_detail") or {}).get("pages_affected") or [])
            if (r.get("affected_scope") or {}).get("scope") == "site-wide":
                site_wide_root = True
        for victim_id in rule["supersedes"]:
            for v in present.get(victim_id, []):
                v_pages = set((v.get("evidence_detail") or {}).get("pages_affected") or [])
                overlaps = (rule.get("scope") == "site" and site_wide_root) or \
                           bool(v_pages & root_pages) or (site_wide_root and not v_pages)
                if overlaps:
                    marks = v.setdefault("superseded_by", [])
                    if rule["root_cause"] not in marks:
                        marks.append(rule["root_cause"])
                        log.append(f"{victim_id}: superseded by {rule['root_cause']}")
                        # A symptom of a named root cause must not outrank the
                        # independent findings around it. Fixing the root cause
                        # may resolve this one outright, so it reads as noise at
                        # the top of a report. severity_locked still wins: a
                        # check whose registry guard forbids movement does not
                        # move here either.
                        if not v.get("severity_locked"):
                            before = v.get("severity", "low")
                            after = shift(before, 1)
                            if after != before:
                                v["severity"] = after
                                log.append(
                                    f"{victim_id}: de-escalated {before} -> {after} "
                                    f"(symptom of {rule['root_cause']})")


def sort_and_number(findings: list[dict]) -> list[dict]:
    """Sort purely as a function of content, so ids are stable across runs."""
    def key(f):
        pages = sorted(str(p) for p in
                       ((f.get("evidence_detail") or {}).get("pages_affected") or []))
        return (SEVERITY_INDEX.get(f.get("severity"), 99),
                f.get("check_id") or "",
                pages[0] if pages else "")

    ordered = sorted(findings, key=key)
    for i, f in enumerate(ordered, start=1):
        f["id"] = f"F-{i:03d}"
    return ordered


AXIS_MECHANISMS = {
    "discoverability": ("reach", "read", "parse", "quote", "trust"),
    "engagement": ("stay",),
}


def score_axes(findings: list[dict], mechanisms_analyzed=None,
               pages_sampled=None) -> dict:
    """Grade how badly the mechanism chain is broken, not how many nits we counted.

    Blocking findings (critical, high) deduct without limit: they are the ones
    that stop a machine reading or citing the site at all. Hygiene findings (low,
    medium) are summed and then capped, because a long tail of true-but-minor
    observations -- no breadcrumb markup, a missing og:image -- should never add
    up to the same verdict as a robots.txt that turns the retrieval crawlers
    away. Without the cap, simply implementing more checks lowers every score on
    the web and the grades stop discriminating between sites.
    """
    scores = {"discoverability": 100.0, "engagement": 100.0}
    hygiene = {"discoverability": 0.0, "engagement": 0.0}
    has_critical = {"discoverability": False, "engagement": False}
    for f in findings:
        cat = f.get("category")
        if cat not in scores:
            continue
        sev = f.get("severity", "low")
        deduction = BASE_DEDUCTION.get(sev, 0)
        deduction *= SCOPE_MULTIPLIER.get((f.get("affected_scope") or {}).get("scope"), 0.3)
        deduction *= CONFIDENCE_MULTIPLIER.get(f.get("confidence", "high"), 1.0)
        if f.get("superseded_by"):
            deduction *= SUPERSEDED_MULTIPLIER
        if sev in BLOCKING_SEVERITIES:
            scores[cat] -= deduction
        else:
            hygiene[cat] += deduction
        if sev == "critical":
            has_critical[cat] = True

    for cat in scores:
        scores[cat] -= min(hygiene[cat], HYGIENE_DEDUCTION_CAP)

    ran = None if mechanisms_analyzed is None else {m.lower() for m in mechanisms_analyzed}

    out = {}
    for axis, raw in scores.items():
        # No page was fetched: berkshirehathaway.com answers every request
        # with Brotli, which the stdlib cannot decode, so the crawl saw the
        # robots file and nothing else. Grading engagement A from zero pages
        # is the same false confidence as grading an axis nobody analysed.
        # Discoverability is still graded: REACH measured the access layer.
        if pages_sampled == 0 and axis == "engagement":
            out[axis] = {
                "score": None,
                "grade": "not assessed",
                "reason": ("no page was fetched, so nothing on-page was measured; "
                           "the axis is not graded"),
            }
            continue
        # An axis nobody measured must not be graded. Starting every axis at 100
        # and deducting means a mechanism with no analyzer reports a perfect
        # score -- a confident claim about something we never looked at, which
        # is a worse failure than reporting nothing. Silence is the honest
        # output; the report renders it as "not assessed".
        if ran is not None and not (set(AXIS_MECHANISMS.get(axis, ())) & ran):
            out[axis] = {
                "score": None,
                "grade": "not assessed",
                "reason": ("no analyzer ran for this axis (" +
                           ", ".join(AXIS_MECHANISMS.get(axis, ())) +
                           "); it was not measured, so it is not graded"),
            }
            continue
        score = int(round(max(0.0, min(100.0, raw))))
        if has_critical[axis]:
            score = min(score, 54)  # a critical finding caps the axis at D
        out[axis] = {"score": score, "grade": grade_for(score)}
    return out


def grade_for(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 55:
        return "C"
    if score >= 35:
        return "D"
    return "F"


def load_candidates(paths: list[str]) -> list[dict]:
    out: list[dict] = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        items = doc.get("findings", []) if isinstance(doc, dict) else doc
        if not isinstance(items, list):
            raise SystemExit(f"error: {p} must hold a findings array")
        out.extend(x for x in items if isinstance(x, dict))
    return out


def main(argv=None) -> int:
    # Windows consoles default to a legacy codepage (cp1252 here), and evidence
    # strings quote real page content -- one arrow, curly quote, em dash or any
    # non-Latin script raises UnicodeEncodeError and aborts the entire audit.
    # The report is JSON and JSON is UTF-8, so say so explicitly.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # pragma: no cover - exotic stdout
        pass

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="candidate finding JSON files")
    ap.add_argument("--out", help="write merged output here (default: stdout)")
    ap.add_argument("--stdout", action="store_true", help="force output to stdout")
    ap.add_argument("--pages-sampled", type=int, default=None,
                    help="pages in the evidence bundle, for scope collapse. Pass 0 "
                         "when the crawl fetched nothing: on-page axes are then "
                         "'not assessed'. Omitted means unknown, and no axis is "
                         "withheld on that basis.")
    ap.add_argument("--supersession", help="JSON file of supersession rules "
                                           "(defaults to the built-in table)")
    ap.add_argument("--mechanisms", default=None,
                    help="comma-separated mechanisms whose analyzer actually ran "
                         "(reach,read,parse,quote,trust,stay). An axis with no "
                         "mechanism analysed is reported as 'not assessed' rather "
                         "than graded. Omit only when every analyzer ran.")
    args = ap.parse_args(argv)

    findings = load_candidates(args.inputs)
    log: list[str] = []

    rules = DEFAULT_SUPERSESSION
    if args.supersession:
        with open(args.supersession, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        rules = doc.get("supersession_rules", doc) if isinstance(doc, dict) else doc

    findings = dedupe(findings, log)
    collapse_to_site_wide(findings, args.pages_sampled or 0, log)
    for f in findings:
        f["severity"] = compute_severity(f, log)
    apply_model_judged_ceiling(findings, log)
    apply_supersession(findings, rules, log)
    findings = sort_and_number(findings)

    counts = {s: 0 for s in SEVERITIES}
    for f in findings:
        if f.get("severity") in counts:
            counts[f["severity"]] += 1

    by_mechanism = {}
    for f in findings:
        m = f.get("mechanism")
        if m:
            by_mechanism[m] = by_mechanism.get(m, 0) + 1

    result = {
        "findings": findings,
        "summary": {
            "total_findings": len(findings),
            **counts,
            "by_category": {
                "discoverability": sum(1 for f in findings
                                       if f.get("category") == "discoverability"),
                "engagement": sum(1 for f in findings
                                  if f.get("category") == "engagement"),
            },
            "by_mechanism": {m: by_mechanism[m] for m in MECHANISM_ORDER
                             if m in by_mechanism},
        },
        "scorecard_input": score_axes(
            findings,
            [m.strip() for m in args.mechanisms.split(",") if m.strip()]
            if args.mechanisms else None,
            args.pages_sampled),
        "merge_log": log,
    }

    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=False)
    if args.out and not args.stdout:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
        print(f"merged {len(findings)} findings -> {args.out}", file=sys.stderr)
        for line in log:
            print(f"  {line}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
