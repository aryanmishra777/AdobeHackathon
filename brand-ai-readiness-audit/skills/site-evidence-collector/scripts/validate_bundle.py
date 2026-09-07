#!/usr/bin/env python3
"""Validate an evidence bundle against the collector contract.

Standard library only -- ships inside the submission.

Run this after collection and before any analysis skill reads the bundle. An
analysis skill that codes against the contract will misbehave in confusing ways
if the bundle silently drifts from it, so failing loudly here is much cheaper
than debugging a wrong finding later.

Usage:
    python validate_bundle.py .audit/example.com/run-01
    python validate_bundle.py .audit/example.com/run-01 --quiet

Exit codes: 0 valid, 1 invalid, 2 unreadable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REQUIRED_TOP = ["schema_version", "run", "pages", "robots", "coverage"]
PAGE_DOCS = ["request.json", "response.headers.json", "raw.html",
             "extracted.json", "chunks.json"]
EXTRACTED_REQUIRED = ["page_id", "url", "title", "headings", "links", "images",
                      "scripts", "jsonld", "text"]
SKIP_REASONS = {"robots-disallow", "budget-exceeded", "timeout", "http-error",
                "non-html", "duplicate", "out-of-scope"}
PURPOSES = {"retrieval", "training", "search-index", "mixed"}
STOPPED = {"completed", "max-pages", "time-budget", "site-blocked",
           "dns-failure", "error"}


def load(path, errors, label):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        errors.append(f"{label}: missing file {path}")
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON in {path}: {exc}")
    return None


def validate(root: str):
    errors: list[str] = []
    warnings: list[str] = []

    if not os.path.isdir(root):
        return [f"bundle root {root!r} is not a directory"], []

    manifest = load(os.path.join(root, "MANIFEST.json"), errors, "MANIFEST.json")
    if manifest is None:
        return errors, warnings

    for key in REQUIRED_TOP:
        if key not in manifest:
            errors.append(f"MANIFEST.json: missing required key {key!r}")

    if manifest.get("schema_version") != "1.0":
        errors.append(f"MANIFEST.json: schema_version must be '1.0', "
                      f"got {manifest.get('schema_version')!r}")

    run = manifest.get("run") or {}
    for key in ("target", "origin", "started_at", "collector_version", "budget"):
        if key not in run:
            errors.append(f"run: missing {key!r}")
    budget = run.get("budget") or {}
    if budget.get("max_concurrency", 0) > 8:
        errors.append(f"run.budget.max_concurrency is {budget['max_concurrency']}; "
                      f"the guardrail caps it at 8")

    coverage = manifest.get("coverage") or {}
    for key in ("pages_discovered", "pages_fetched", "complete"):
        if key not in coverage:
            errors.append(f"coverage: missing {key!r}")
    if coverage.get("stopped_reason") not in STOPPED | {None}:
        errors.append(f"coverage.stopped_reason {coverage.get('stopped_reason')!r} "
                      f"is not a known reason")
    for entry in coverage.get("skipped") or []:
        if entry.get("reason") not in SKIP_REASONS:
            errors.append(f"coverage.skipped: unknown reason {entry.get('reason')!r} "
                          f"for {entry.get('url')}")

    robots = manifest.get("robots") or {}
    if "fetched" not in robots:
        errors.append("robots: missing 'fetched'")
    matrix = robots.get("agent_matrix") or {}
    if robots.get("status") == 200 and not matrix:
        errors.append("robots: status 200 but agent_matrix is empty; "
                      "crawl-access-audit cannot resolve per-agent access")
    for token, entry in matrix.items():
        if "root_allowed" not in entry:
            errors.append(f"robots.agent_matrix[{token}]: missing 'root_allowed'")
        if entry.get("purpose") not in PURPOSES:
            errors.append(f"robots.agent_matrix[{token}]: purpose "
                          f"{entry.get('purpose')!r} is not in {sorted(PURPOSES)}; "
                          f"the retrieval/training split is a required guard")

    pages = manifest.get("pages") or []
    seen_ids, seen_urls = set(), set()
    for i, page in enumerate(pages):
        label = f"pages[{i}]"
        pid = page.get("page_id")
        if not pid:
            errors.append(f"{label}: missing page_id")
            continue
        if pid in seen_ids:
            errors.append(f"{label}: duplicate page_id {pid!r}")
        seen_ids.add(pid)
        url = page.get("url")
        if url in seen_urls:
            warnings.append(f"{label}: duplicate url {url!r}")
        seen_urls.add(url)

        # Only successfully fetched pages carry documents. Non-200 entries are
        # deliberately retained so REACH can report broken internal links.
        if page.get("status") != 200:
            continue

        pdir = os.path.join(root, "pages", pid)
        if not os.path.isdir(pdir):
            errors.append(f"{label}: status 200 but no directory pages/{pid}/")
            continue
        for doc in PAGE_DOCS:
            if not os.path.exists(os.path.join(pdir, doc)):
                errors.append(f"{label}: missing pages/{pid}/{doc}")

        extracted = load(os.path.join(pdir, "extracted.json"), errors,
                         f"pages/{pid}/extracted.json")
        if isinstance(extracted, dict):
            for key in EXTRACTED_REQUIRED:
                if key not in extracted:
                    errors.append(f"pages/{pid}/extracted.json: missing {key!r}")
            if extracted.get("page_id") != pid:
                errors.append(f"pages/{pid}/extracted.json: page_id mismatch "
                              f"({extracted.get('page_id')!r})")
            for j, img in enumerate(extracted.get("images") or []):
                if "alt" not in img:
                    errors.append(f"pages/{pid}/extracted.json: images[{j}] omits "
                                  f"'alt'; absent and empty alt must stay distinct")
            for j, block in enumerate(extracted.get("jsonld") or []):
                if "raw" not in block or "parsed_ok" not in block:
                    errors.append(f"pages/{pid}/extracted.json: jsonld[{j}] must "
                                  f"carry both 'raw' and 'parsed_ok'")
            text = extracted.get("text") or {}
            for key in ("main", "word_count"):
                if key not in text:
                    errors.append(f"pages/{pid}/extracted.json: text.{key} missing")

        chunks_doc = load(os.path.join(pdir, "chunks.json"), errors,
                          f"pages/{pid}/chunks.json")
        if isinstance(chunks_doc, dict):
            for j, chunk in enumerate(chunks_doc.get("chunks") or []):
                for key in ("chunk_id", "text", "word_count"):
                    if key not in chunk:
                        errors.append(f"pages/{pid}/chunks.json: chunks[{j}] "
                                      f"missing {key!r}")
                signals = chunk.get("signals") or {}
                for key in ("names_subject", "leading_pronoun", "bare_numbers"):
                    if key not in signals:
                        errors.append(f"pages/{pid}/chunks.json: chunks[{j}].signals "
                                      f"missing {key!r}; answerability-audit "
                                      f"depends on it")

    fetched = sum(1 for p in pages if p.get("status") == 200)
    if coverage.get("pages_fetched") not in (None, fetched):
        errors.append(f"coverage.pages_fetched says {coverage['pages_fetched']}, "
                      f"manifest lists {fetched} pages with status 200")

    if fetched == 0 and coverage.get("stopped_reason") == "completed":
        errors.append("no pages fetched but stopped_reason is 'completed'; "
                      "a bundle with no pages must name the reason")

    if fetched and fetched < 3:
        warnings.append(f"only {fetched} pages fetched; no finding may claim "
                        f"site-wide scope (false-positive gate 5)")

    if not os.path.exists(os.path.join(root, "robots.txt.raw")):
        warnings.append("robots.txt.raw absent; findings cannot quote it verbatim")

    return errors, warnings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bundle")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args(argv)

    try:
        errors, warnings = validate(args.bundle)
    except Exception as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    for w in warnings:
        print(f"warning  {w}", file=sys.stderr)
    for e in errors:
        print(f"error    {e}", file=sys.stderr)

    if errors or (args.strict and warnings):
        print(f"\nFAIL: {args.bundle}", file=sys.stderr)
        return 1
    if not args.quiet:
        extra = f", {len(warnings)} warning(s)" if warnings else ""
        print(f"OK: {args.bundle} is a valid evidence bundle{extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
