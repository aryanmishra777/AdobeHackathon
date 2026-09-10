# Brand AI-Readiness Audit — Adobe University Hackathon 2026, Round 3

An **Agent Skill Marketplace** that audits any website for *why AI assistants fail
to find, trust and cite it*, and *why the visitors who do arrive fail to engage* —
then emits one structured report of evidence-backed findings with prioritized,
mechanism-sound fixes.

**Recommend-only.** No skill in this marketplace ever modifies the audited site.
Read-only, `GET`/`HEAD` only, robots.txt respected, never authenticates, never
submits a form.

The submission is the `brand-ai-readiness-audit/` directory. Everything else in
this repo is the harness that proves it works.

---

## Repo map

| Path | What it is |
|---|---|
| **`brand-ai-readiness-audit/`** | **THE SUBMISSION.** `marketplace.json` + 8 skills. This is the only directory that gets zipped. |
| `bench/` | 76 real-site candidates → 57 measured corpus entries across the SEO×GEO quadrants, plus the live/replay runner. |
| `tests/` | 7 local fixture sites, the bundles built from them, and 127 pytest assertions. |
| `tools/` | `validate.py`, `package.py`, `install_local.py`. |
| `docs/` | `EVIDENCE.md` (what the literature supports, and what it doesn't), `ROLES.md`, `CONTRIBUTING.md`, `todo/` (5 work packets). |
| `TODO.md` | Who builds what, in what order. Index into `docs/todo/`. |
| `PLAN.md` | The full architecture and build plan. The shared spec. |

## The eight skills

```
audit-orchestrator/            ENTRYPOINT   scope, dispatch, merge, prioritize, emit
site-evidence-collector/       ACQUISITION  the ONLY skill that touches the network
crawl-access-audit/            REACH        can a machine get in?
render-extractability-audit/   READ         can it read what's there?
structured-data-audit/         PARSE        can it parse a specific fact out?
answerability-audit/           QUOTE        can it lift a clear, standalone fact?
freshness-corroboration-audit/ TRUST        will it believe and repeat that fact?
engagement-audit/              STAY         does the visitor who arrives stay?
```

One skill per link in the chain, so a finding always names the stage that
actually failed. All network I/O lives in `site-evidence-collector`: one polite
crawl produces a cached evidence bundle on disk, and the six analysis skills are
pure functions over that bundle. That gives determinism, no re-fetching a site
six times, and every safety guardrail auditable in a single folder.

Everything inside the zip is **stdlib-only Python** — no `requests`, no `bs4`,
no model weights. A check that always runs beats a stronger check that can't.

## Status

| Skill | Owner | State |
|---|---|---|
| `audit-orchestrator` | Aryan | complete |
| `site-evidence-collector` | Aryan | complete |
| `crawl-access-audit` | Aryan | complete — the reference implementation |
| `render-extractability-audit` | Lakshay | complete — 16/16 checks |
| `structured-data-audit` | Lakshay | complete — 14/14 checks |
| `answerability-audit` | Mayank | scaffold |
| `freshness-corroboration-audit` | Mayank | scaffold |
| `engagement-audit` | Mayank | scaffold |

91 checks are specified across the six registries; 43 are implemented. "Scaffold"
means the design is finished and written down — every check has its ID, severity
rule, required evidence, human verification step, and its false-positive guards.
What is left is translating a finished specification into Python. See
[`docs/ROLES.md`](docs/ROLES.md).

## Getting started

```bash
pip install -r tools/requirements-dev.txt   # dev tooling only, never shipped

python tests/make_fixtures.py               # build the local test websites
python tests/make_bundles.py                # crawl them into evidence bundles

python -m pytest tests/ -q                  # expect: 127 passed
python tools/validate.py                    # expect: PASS (13 TODOs outstanding)
python tools/package.py                     # builds dist/ and checks the 50 MB ceiling
```

Then read [`TODO.md`](TODO.md) for your queue, and the packet it points you at in
[`docs/todo/`](docs/todo/) — each one ends in a paste-ready prompt for Claude
Code / Copilot / Antigravity.

## Why we think this scores

**It is a GEO auditor, not an SEO checker.** The corpus is labelled by
*measurement*, never assertion — GEO from the actual blocking mechanism observed,
SEO from technical hygiene. The result:

```
                        n    disc
SEO good / GEO good    20     75     control — healthy on both axes
SEO good / GEO poor    10     60     the money quadrant
SEO poor / GEO good    14     61     great content, weak technical SEO
SEO poor / GEO poor    13     55     both, and we name the mechanism
```

Good-SEO/poor-GEO scores 15 points below good-SEO/good-GEO. Those ten sites are
ones a conventional SEO linter passes clean: perfect sitemaps and canonicals,
while the edge returns 429 to `ClaudeBot` or robots.txt disallows the retrieval
crawlers outright.

**Independent evidence that these are different problems.** Published audits put
URL-level Jaccard overlap between Google's SERP and AI engines at **0.11-0.18**,
and find **53% of AI-Overview cited domains absent from the organic top 10**. A
site can be optimised for one and invisible to the other, which is the premise
this marketplace is built on. A further **27.1% of the URLs engines retrieve are
inaccessible** — which is why REACH is stage one and not an afterthought.

**Every threshold is traceable.** [`docs/EVIDENCE.md`](docs/EVIDENCE.md) records
what the GEO literature actually measures, with effect sizes and study designs;
what it merely asserts; and which of our numbers are still judgment calls. The
retrieval chunk window is 150-300 words because passages beyond 300 lose ~31% of
attention in their middle segments, not because it looked reasonable. The same
file records what we may *not* claim — notably that structured-data markup has no
controlled evidence of citation lift, so `structured-data-audit` reports what a
machine cannot extract and never promises a ranking or traffic gain.

**We state our own blind spots.** Five of the seven causal factors the literature
identifies are outside any single-site crawl: whether the engine retrieved at all,
what third-party sources say, the competing candidate pool, engine-specific
routing, and off-site content placed to steer retrieval. Every report carries
them in `coverage.limitations`, and an axis with no analyzer is reported as
**not assessed** rather than graded. See
[`audit-boundary.md`](brand-ai-readiness-audit/skills/audit-orchestrator/references/audit-boundary.md).

**False positives are the thing we defend hardest.** Six layered gates, per-check
binding guards, and a clean-fixture tripwire that must produce zero critical and
zero high findings. The sharpest example: blocking `ChatGPT-User` (a *retrieval*
agent, fetching a page because a user asked about you) is a high-severity defect;
blocking `GPTBot` (a *training* crawler) is a legitimate business choice and is
reported as informational only — with a test asserting the words "error",
"defect" and "bug" never appear in that finding.

**Ten corpus sites are excluded as inconclusive**, recorded with reasons rather
than dropped. They refused our browser probe too, so we cannot separate a
site-level block from our own address being filtered. Claiming a defect there
would be exactly the confident false positive the rubric punishes.

## Team

**Aryan** — contracts, collector, orchestrator, the reference implementation,
tooling and the bench. **Lakshay** — READ and PARSE. **Mayank** — QUOTE, TRUST
and STAY.
