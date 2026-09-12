"""Optional libraries: present, they add evidence; absent, nothing changes.

Standard library only at import time. Every third-party import happens inside
`available()`, behind a try/except, and is cached per process. A script asks

    if extras.available("dateparser"):
        import dateparser  # guarded again at the call site for the validator

and records what it used with `extras.record(bundle_dir, ...)`, which lands in
run.json#extras so a report can say "dates parsed by dateparser 1.4, main text
by trafilatura 2.2". The stdlib path is the record on every machine; these are
the reasons a machine with the extras installed audits better, and the bundle
says so.

Declared in requirements-optional.txt at the marketplace root and allowed by
tools/validate.py only behind a guard.
"""
from __future__ import annotations

import importlib
import io
import json
import os

# module name -> distribution name, where they differ
DISTRIBUTIONS = {"brotli": "Brotli", "zstandard": "zstandard", "trafilatura": "trafilatura",
                 "protego": "Protego", "pysbd": "pysbd", "dateparser": "dateparser",
                 "phonenumbers": "phonenumbers", "ftfy": "ftfy", "tldextract": "tldextract",
                 "rapidfuzz": "rapidfuzz", "json5": "json5", "langdetect": "langdetect",
                 "bs4": "beautifulsoup4", "playwright": "playwright"}

_cache: dict = {}


def available(name: str) -> bool:
    """True when `name` imports. Cached; never raises."""
    if name not in _cache:
        try:
            importlib.import_module(name)
            _cache[name] = True
        except Exception:
            _cache[name] = False
    return _cache[name]


def version(name: str):
    try:
        from importlib import metadata
        return metadata.version(DISTRIBUTIONS.get(name, name))
    except Exception:
        return None


def record(bundle_dir: str, name: str, used_for: str) -> None:
    """Append {name, version, used_for} to <bundle>/run.json#extras, once per
    (name, used_for). Silent on any failure: recording is never worth a crash."""
    path = os.path.join(bundle_dir, "run.json")
    try:
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        entries = doc.setdefault("extras", [])
        if any(e.get("name") == name and e.get("used_for") == used_for for e in entries):
            return
        entries.append({"name": name, "version": version(name), "used_for": used_for})
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    except Exception:
        return


def used(bundle_dir: str) -> list:
    """What run.json says was used, for analyzers and the report."""
    try:
        with io.open(os.path.join(bundle_dir, "run.json"), encoding="utf-8") as fh:
            return json.load(fh).get("extras") or []
    except Exception:
        return []
