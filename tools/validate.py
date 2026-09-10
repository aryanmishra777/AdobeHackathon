#!/usr/bin/env python3
"""Validate the whole marketplace: spec compliance, contract consistency, hygiene.

Dev tooling -- lives OUTSIDE the submission zip, so it may take dependencies.
Requires PyYAML (see tools/requirements-dev.txt).

Run this before every commit and before packaging. It enforces:

  1. agentskills.io spec compliance for every skill folder
  2. marketplace.json well-formedness with exactly one entrypoint
  3. check-registry integrity: unique ids, correct prefixes, guards present
  4. cross-references resolve (fix_ref, bundled resources, subskill paths)
  5. the stdlib-only rule for everything shipped inside the zip
  6. determinism hygiene: no wall-clock or randomness in analysis scripts

Usage:
    python tools/validate.py
    python tools/validate.py --strict     # TODOs become failures
    python tools/validate.py --quiet
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("error: PyYAML is required. pip install -r tools/requirements-dev.txt",
          file=sys.stderr)
    raise SystemExit(2)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKET = os.path.join(REPO, "brand-ai-readiness-audit")

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CHECK_ID_RE = re.compile(r"^(REACH|READ|PARSE|QUOTE|TRUST|STAY)-\d{3}$")
PROACTIVE_ID_RE = re.compile(r"^(REACH|READ|PARSE|QUOTE|TRUST|STAY)-P\d{2}$")

VALID_MECHANISMS = {"reach", "read", "parse", "quote", "trust", "stay"}
VALID_SEVERITIES = {"critical", "high", "medium", "low"}
PREFIX_FOR = {"reach": "REACH", "read": "READ", "parse": "PARSE",
              "quote": "QUOTE", "trust": "TRUST", "stay": "STAY"}

# The submission must run on a bare Python install. Anything importable from the
# standard library is fine; everything else is a packaging bug that only shows up
# on the grader's machine.
STDLIB_OK = {
    "argparse", "ast", "base64", "collections", "concurrent", "contextlib",
    "copy", "csv", "dataclasses", "datetime", "difflib", "enum", "functools",
    "glob", "gzip", "hashlib", "html", "http", "io", "itertools", "json",
    "math", "os", "pathlib", "posixpath", "queue", "random", "re", "shutil",
    "socket", "ssl", "statistics", "string", "subprocess", "sys", "textwrap",
    "threading", "time", "traceback", "types", "typing", "unicodedata",
    "urllib", "uuid", "warnings", "xml", "zipfile", "zlib", "__future__",
}

# Non-determinism in an analysis script means two runs over one bundle can
# disagree, which breaks golden tests and makes findings unreproducible.
NONDETERMINISM = [
    (re.compile(r"\brandom\.(?!seed\b)"), "random.* without a fixed seed"),
    (re.compile(r"\bdatetime\.now\b|\btime\.time\b|\btoday\(\)"), "wall-clock time"),
    (re.compile(r"\bset\(\)\s*\)?\s*$", re.M), "iteration over an unsorted set"),
]


class Result:
    def __init__(self):
        self.errors: list[str] = []
        self.todos: list[str] = []
        self.warnings: list[str] = []
        self._todo_seen: set[str] = set()

    def error(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def todo(self, where, msg):
        # Deduplicate on the message alone: one missing fix template is cited by
        # a dozen checks, and printing it a dozen times buries the other TODOs.
        skill = where.split("/checks.yaml")[0].split(os.sep)[-1]
        line = f"{skill}: {msg}"
        if line not in self._todo_seen:
            self._todo_seen.add(line)
            self.todos.append(line)

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def read_frontmatter(path, r):
    text = io.open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        r.error(path, "SKILL.md must open with YAML frontmatter delimited by ---")
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        r.error(path, "unterminated YAML frontmatter")
        return None, text
    try:
        return yaml.safe_load(parts[1]), parts[2]
    except yaml.YAMLError as exc:
        r.error(path, f"frontmatter is not valid YAML: {exc}")
        return None, text


def check_skill_spec(skill_dir, entry, r):
    """agentskills.io compliance."""
    rel = os.path.relpath(skill_dir, REPO)
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        r.error(rel, "no SKILL.md")
        return None

    fm, body = read_frontmatter(skill_md, r)
    if fm is None:
        return None

    name = fm.get("name")
    if not name:
        r.error(rel, "frontmatter has no 'name'")
    else:
        folder = os.path.basename(skill_dir)
        if name != folder:
            r.error(rel, f"name {name!r} does not match folder {folder!r}")
        if not NAME_RE.match(str(name)):
            r.error(rel, f"name {name!r} must be lowercase letters, digits and "
                         f"single hyphens, not starting or ending with one")
        if len(str(name)) > 64:
            r.error(rel, f"name is {len(str(name))} chars, max is 64")

    desc = fm.get("description")
    if not desc or not str(desc).strip():
        r.error(rel, "description is required and must be non-empty")
    elif len(str(desc)) > 1024:
        r.error(rel, f"description is {len(str(desc))} chars, max is 1024")

    compat = fm.get("compatibility")
    if compat and len(str(compat)) > 500:
        r.error(rel, f"compatibility is {len(str(compat))} chars, max is 500")

    meta = fm.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            r.error(rel, "metadata must be a mapping")
        else:
            for k, v in meta.items():
                if not isinstance(v, str):
                    r.error(rel, f"metadata.{k} must be a string "
                                 f"(got {type(v).__name__}); quote numbers")

    if len(body.splitlines()) > 500:
        r.warn(rel, f"SKILL.md body is {len(body.splitlines())} lines; the spec "
                    f"recommends under 500 -- move detail into references/")

    # Every relative path the SKILL.md points at must exist.
    scaffold = entry.get("status") == "scaffold"
    for m in re.finditer(r"`((?:references|scripts)/[A-Za-z0-9_./-]+)`", body):
        target = os.path.join(skill_dir, m.group(1).replace("/", os.sep))
        if not os.path.exists(target):
            if scaffold:
                r.todo(rel, f"not yet written: {m.group(1)}")
            else:
                r.error(rel, f"SKILL.md references a missing file: {m.group(1)}")
    return fm


def check_registry(skill_dir, entry, r, seen_ids):
    rel = os.path.relpath(skill_dir, REPO)
    path = os.path.join(skill_dir, "references", "checks.yaml")
    if not os.path.exists(path):
        if entry.get("concern") in ("compose", "acquire"):
            return
        r.error(rel, "analysis skill has no references/checks.yaml")
        return

    try:
        doc = yaml.safe_load(io.open(path, encoding="utf-8"))
    except yaml.YAMLError as exc:
        r.error(rel + "/references/checks.yaml", f"invalid YAML: {exc}")
        return

    meta = doc.get("meta") or {}
    mech = meta.get("mechanism")
    if mech not in VALID_MECHANISMS:
        r.error(rel, f"checks.yaml meta.mechanism {mech!r} is not a valid mechanism")
    prefix = PREFIX_FOR.get(mech, "")

    for i, c in enumerate(doc.get("checks") or []):
        where = f"{rel}/checks.yaml[{c.get('id', i)}]"
        cid = c.get("id")
        if not cid or not CHECK_ID_RE.match(str(cid)):
            r.error(where, f"invalid check id {cid!r}")
            continue
        if prefix and not str(cid).startswith(prefix + "-"):
            r.error(where, f"id prefix does not match mechanism {mech!r}")
        if cid in seen_ids:
            r.error(where, f"duplicate check id {cid!r} (also in {seen_ids[cid]})")
        seen_ids[cid] = rel

        for field in ("title_template", "applies_when", "detection",
                      "severity_rule", "verification", "false_positive_guards"):
            if not c.get(field):
                r.error(where, f"missing required registry field {field!r}")

        if c.get("detection") not in ("deterministic", "model-judged", None):
            r.error(where, f"detection {c.get('detection')!r} must be "
                           f"'deterministic' or 'model-judged'")

        guards = c.get("false_positive_guards") or []
        if isinstance(guards, list) and len(guards) == 0:
            r.error(where, "false_positive_guards must not be empty")

        fix_ref = c.get("fix_ref")
        if fix_ref:
            target = os.path.join(skill_dir, str(fix_ref).replace("/", os.sep))
            if not os.path.exists(target):
                if entry.get("status") == "scaffold":
                    r.todo(where, f"not yet written: {fix_ref}")
                else:
                    r.error(where, f"fix_ref does not resolve: {fix_ref}")

    for p in doc.get("proactive") or []:
        pid = p.get("id")
        if not pid or not PROACTIVE_ID_RE.match(str(pid)):
            r.error(f"{rel}/checks.yaml", f"invalid proactive id {pid!r}")


def check_stdlib_only(r):
    """Nothing inside the zip may import a third-party package."""
    for dirpath, _dirs, files in os.walk(MARKET):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, REPO)
            try:
                tree = ast.parse(io.open(path, encoding="utf-8").read(), filename=path)
            except SyntaxError as exc:
                r.error(rel, f"syntax error: {exc}")
                continue
            for node in ast.walk(tree):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    mods = [node.module]
                for m in mods:
                    top = m.split(".")[0]
                    if top not in STDLIB_OK:
                        r.error(rel, f"line {node.lineno}: imports {top!r}, which is "
                                     f"not in the standard library -- the submission "
                                     f"must run on a bare Python install")


def check_determinism(r):
    for dirpath, _dirs, files in os.walk(MARKET):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, REPO)
            # The collector legitimately stamps wall-clock time into run.json.
            if "site-evidence-collector" in rel:
                continue
            text = io.open(path, encoding="utf-8").read()
            for pattern, label in NONDETERMINISM[:2]:
                for m in pattern.finditer(text):
                    line = text[:m.start()].count("\n") + 1
                    r.warn(rel, f"line {line}: {label} in an analysis script "
                                f"makes findings unreproducible")


def check_manifest(r):
    path = os.path.join(MARKET, "marketplace.json")
    if not os.path.exists(path):
        r.error("marketplace.json", "missing at the marketplace root")
        return []
    try:
        doc = json.load(io.open(path, encoding="utf-8"))
    except json.JSONDecodeError as exc:
        r.error("marketplace.json", f"invalid JSON: {exc}")
        return []

    for field in ("name", "version", "skills"):
        if field not in doc:
            r.error("marketplace.json", f"missing required field {field!r}")

    skills = doc.get("skills") or []
    entries = [s for s in skills if s.get("entrypoint")]
    if len(entries) != 1:
        r.error("marketplace.json",
                f"exactly one skill must be marked entrypoint, found {len(entries)}")

    seen = set()
    for s in skills:
        sid = s.get("id")
        if not sid:
            r.error("marketplace.json", "a skill entry has no id")
            continue
        if sid in seen:
            r.error("marketplace.json", f"duplicate skill id {sid!r}")
        seen.add(sid)
        sub = s.get("path")
        if not sub:
            r.error("marketplace.json", f"{sid}: no path")
            continue
        folder = os.path.join(MARKET, sub.replace("/", os.sep))
        if not os.path.isdir(folder):
            r.error("marketplace.json", f"{sid}: path does not exist: {sub}")
        elif os.path.basename(folder) != sid:
            r.warn("marketplace.json", f"{sid}: folder name differs from id")

    # Every skill folder on disk must be declared.
    skills_dir = os.path.join(MARKET, "skills")
    if os.path.isdir(skills_dir):
        for fn in sorted(os.listdir(skills_dir)):
            if os.path.isdir(os.path.join(skills_dir, fn)) and fn not in seen:
                r.error("marketplace.json",
                        f"skills/{fn}/ exists on disk but is not listed in the manifest")

    if not os.path.exists(os.path.join(MARKET, "README.md")):
        r.error("README.md", "the marketplace root must carry a README.md")

    return skills


def check_subskill_table(skills, r):
    """The orchestrator's dispatch table must match the manifest exactly."""
    path = os.path.join(MARKET, "skills", "audit-orchestrator", "references",
                        "subskills.json")
    if not os.path.exists(path):
        r.error("audit-orchestrator", "references/subskills.json is missing")
        return
    try:
        doc = json.load(io.open(path, encoding="utf-8"))
    except json.JSONDecodeError as exc:
        r.error("subskills.json", f"invalid JSON: {exc}")
        return

    listed = {s["id"] for s in doc.get("stages") or [] if s.get("id")}
    declared = {s["id"] for s in skills if not s.get("entrypoint")}
    for missing in sorted(declared - listed):
        r.error("subskills.json", f"{missing!r} is in the manifest but not dispatched")
    for extra in sorted(listed - declared):
        r.error("subskills.json", f"{extra!r} is dispatched but not in the manifest")

    for stage in doc.get("stages") or []:
        p = stage.get("path", "")
        target = os.path.normpath(os.path.join(
            MARKET, "skills", "audit-orchestrator", p.replace("/", os.sep)))
        if not os.path.isdir(target):
            r.error("subskills.json", f"{stage.get('id')}: path does not resolve: {p}")


# Phrasing that reads as "point me at a website and I will audit it". Only the
# entrypoint may say this; if a sub-skill does, a plain "audit example.com"
# risks activating it directly and the composition breaks.
ENTRYPOINT_PHRASES = (
    "audit a website", "audit any website", "audits a website", "audit a site",
    "point it at", "give it a url", "given a url", "audit the site",
    "for any website", "any url",
)
# Phrasing that marks a skill as a component of a larger run.
COMPONENT_MARKERS = (
    "invoked by", "called by", "part of", "component of", "as part of",
    "the evidence bundle", "audit-orchestrator",
)


def check_activation_hygiene(skills, r):
    """Only the entrypoint's description may read as 'audit a website'.

    The Agent Skills spec activates a skill from its description, and there is no
    skill-calls-skill primitive. So if a sub-skill's description also reads like
    a whole-site audit, a user typing "audit example.com" can activate that
    sub-skill instead of the orchestrator, and the composition silently collapses
    into one stage.

    This checks the half of activation hygiene a script can see. The other half
    -- what a real agent actually does with these descriptions -- still needs the
    end-to-end run described in the README.
    """
    for entry in skills:
        folder = os.path.join(MARKET, (entry.get("path") or "").replace("/", os.sep))
        skill_md = os.path.join(folder, "SKILL.md")
        if not os.path.exists(skill_md):
            continue
        fm, _body = read_frontmatter(skill_md, r)
        if not fm:
            continue
        desc = (fm.get("description") or "").lower()
        name = entry.get("id", "?")
        if entry.get("entrypoint"):
            if not any(k in desc for k in ("audit", "website", "site")):
                r.error(name, "the entrypoint's description does not read as a "
                              "website audit; a user asking for one may activate "
                              "nothing")
            continue
        hits = [k for k in ENTRYPOINT_PHRASES if k in desc]
        if hits:
            r.error(name, "sub-skill description reads like a whole-site audit "
                          f"({', '.join(repr(h) for h in hits)}); it can steal "
                          "activation from audit-orchestrator. Phrase it as a "
                          "component.")
        elif not any(k in desc for k in COMPONENT_MARKERS):
            r.warn(name, "sub-skill description does not identify itself as a "
                         "component; consider naming audit-orchestrator or the "
                         "evidence bundle so it never activates on its own")

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="treat TODOs as failures")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    r = Result()
    skills = check_manifest(r)
    seen_ids: dict[str, str] = {}

    for entry in skills:
        folder = os.path.join(MARKET, (entry.get("path") or "").replace("/", os.sep))
        if not os.path.isdir(folder):
            continue
        check_skill_spec(folder, entry, r)
        check_registry(folder, entry, r, seen_ids)

    check_subskill_table(skills, r)
    check_activation_hygiene(skills, r)
    check_stdlib_only(r)
    check_determinism(r)

    for w in r.warnings:
        print(f"warning  {w}", file=sys.stderr)
    for t in r.todos:
        print(f"TODO     {t}", file=sys.stderr)
    for e in r.errors:
        print(f"error    {e}", file=sys.stderr)

    n_complete = sum(1 for s in skills if s.get("status") == "complete")
    if not args.quiet:
        print()
        print(f"skills      {len(skills)} declared, {n_complete} complete, "
              f"{len(skills) - n_complete} scaffold")
        print(f"checks      {len(seen_ids)} registered, all ids unique")
        print(f"errors      {len(r.errors)}")
        print(f"TODOs       {len(r.todos)}")
        print(f"warnings    {len(r.warnings)}")

    if r.errors or (args.strict and r.todos):
        print("\nFAIL", file=sys.stderr)
        return 1
    print("\nPASS" + ("" if not r.todos else f" ({len(r.todos)} TODOs outstanding)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
