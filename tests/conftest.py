"""Shared fixtures.

`bare_install` builds a directory of shadow packages that raise
ModuleNotFoundError for every optional extra and returns an environment with
it first on PYTHONPATH. Run a script under that environment and it sees a
bare Python install whatever this machine has installed -- the path a
grader's sandbox takes.
"""
from __future__ import annotations

import os

import pytest

OPTIONAL_EXTRAS = ["playwright", "bs4", "brotli", "zstandard", "trafilatura", "protego",
                   "pysbd", "dateparser", "phonenumbers", "ftfy", "tldextract", "rapidfuzz",
                   "json5", "langdetect"]


@pytest.fixture(scope="session")
def bare_install(tmp_path_factory):
    root = tmp_path_factory.mktemp("nodeps")
    for name in OPTIONAL_EXTRAS:
        pkg = root / name
        pkg.mkdir()
        (pkg / "__init__.py").write_text(
            f'raise ModuleNotFoundError("simulated absence of {name}")\n', encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root) + os.pathsep + env.get("PYTHONPATH", "")
    return env
