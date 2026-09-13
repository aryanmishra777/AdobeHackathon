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

## Try it in five minutes

**As a skill (the product).** Install the eight skills where your agent finds
them, then ask for an audit in plain words. The orchestrator activates, crawls
once, dispatches the six analyzers, finishes the model-judged checks, and writes
`report.json` + `report.md` under `.audit/<domain>/`.

```bash
python tools/install_local.py            # copies the skills into .claude/skills/
# then, in Claude Code (or any agent that reads Agent Skills):
#   audit https://github.com/
```

**Scripts only (no agent).** Same crawl, same six analyzers, same merge and
validation; the model-judged checks stay unfinished and the report says so.

```bash
python tools/run_audit.py https://github.com/ --out .audit/github   # ~1-2 min
```

Pure stdlib Python 3.10+; nothing to install. Fourteen optional libraries
(`brand-ai-readiness-audit/requirements-optional.txt`) add evidence when
present — Playwright renders a six-page sample so JS-dependency is measured, not
inferred — and change nothing when absent.

**If a site's edge stalls the crawler** (ea.com held every response for 42 s once
it had seen a burst), the run tells you so and the report says the sample is
thin. Rerun with `--budget 900 --cap 1500` for a full sample; the collector fetches
its probes in parallel and reserves budget for pages, but it cannot make a
42-second response arrive faster.

## What a report looks like

From [`docs/examples/report-github-com.md`](docs/examples/report-github-com.md),
produced by the agent-driven path on 13 September 2026:

> GitHub lets every AI agent in and tells them so in robots.txt and llms.txt;
> what it does not do is tell them what it *is* — there is no entity markup on
> the site, and the h1 on its home page is a slogan.
>
> | | Grade | Score |
> |---|---|---|
> | **Discoverability** — can AI assistants find, trust and cite you? | C | 68/100 |
> | **Engagement** — do visitors who arrive stay? | A | 99/100 |
>
> | Assistant | Status | What we measured |
> |---|---|---|
> | ChatGPT | **reachable** | ChatGPT-User was served the full page |
> | Claude | **reachable** | Claude-User was served the full page |
> | Perplexity | **reachable** | PerplexityBot was served the full page |
>
> 1. **Add an Organization entity to the shared layout and Offer markup to /pricing** — 23 of 25 pages carry no structured data; plan prices are table text, not data.

Every finding carries its evidence, the bundle files it came from, a
copy-pasteable verification command, and a fix with an owner and an effort. What
the audit could not measure is listed under `coverage.limitations`, never
graded as clean.

More worked examples: [nike.in](docs/examples/report-nike-in.md) (an Akamai edge
that challenges browsers but serves declared bots), [adobe.com/in](docs/examples/report-adobe-com-in.md),
[crunchyroll.com](docs/examples/report-crunchyroll-com.md) (a client-rendered app
shell), [ea.com/sports](docs/examples/report-ea-com-sports.md) (the 42-second hold),
[vox.com](docs/examples/report-vox-com.md), and [bbc.co.uk](docs/examples/report-bbc-co-uk.md)
from the scripts-only path.

## Does it measure GEO, or just SEO?

A 64-site corpus, labelled by *measurement* (GEO from the blocking mechanism
actually observed, SEO from technical hygiene), replayed from snapshots:

```
                        n   disc   eng
SEO good / GEO good    24     66     94    control — healthy on both axes
SEO good / GEO poor    14     51     92    the money quadrant
SEO poor / GEO good    17     57     76    great content, weak technical SEO
SEO poor / GEO poor     9     45     83    both, and we name the mechanism
```

Good-SEO/poor-GEO scores 16 points below good-SEO/good-GEO, with zero false
positives and zero misses against the corpus's expected checks. Those fourteen
sites are ones a conventional SEO linter passes clean — perfect sitemaps and
canonicals — while the edge returns 429 to `ClaudeBot` or robots.txt disallows
the retrieval crawlers outright. `python bench/run.py --replay` reproduces the
table.

---

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

Everything inside the zip runs on **stdlib-only Python** — no `requests`, no
model weights. A check that always runs beats a stronger check that can't. Fourteen
*optional* extras (`brand-ai-readiness-audit/requirements-optional.txt`) are
auto-detected and never required -- Playwright renders a six-page sample so the
JS-rendering check becomes a measurement, protego gives the robots.txt guardrail
a second opinion where the stricter answer wins, trafilatura strips boilerplate
before chunking, dateparser and phonenumbers read dates and phone numbers
properly, and so on -- each imported behind a guard at one call site and each
recorded in `run.json#extras` when used. Without them the behaviour is exactly
the stdlib path, which is what the bench and the fixture bundles measure.

## Why we think this scores

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

**Adobe's own product agrees with the decomposition.** Adobe Brand Visibility's
onsite best-practices list — robots.txt and CDN review, a URL Inspector for
blocked pages, freshness, citations to authoritative sources, structured
headers, FAQs, EEAT — is a subset of our 91 checks, each with more depth behind
it. Where it runs prompts against live LLMs and measures traffic, we stop and
say so. See [`docs/ADOBE-BRAND-VISIBILITY.md`](docs/ADOBE-BRAND-VISIBILITY.md).

**False positives are the thing we defend hardest.** Six layered gates, per-check
binding guards, and a clean-fixture tripwire that must produce zero critical and
zero high findings. The sharpest example: blocking `ChatGPT-User` (a *retrieval*
agent, fetching a page because a user asked about you) is a high-severity defect;
blocking `GPTBot` (a *training* crawler) is a legitimate business choice and is
reported as informational only — with a test asserting the words "error",
"defect" and "bug" never appear in that finding.

**Eight candidate sites are excluded as inconclusive**, recorded with reasons
rather than dropped (thirteen more were unusable: too few pages to grade). They refused our browser probe too, so we cannot separate a
site-level block from our own address being filtered. Claiming a defect there
would be exactly the confident false positive the rubric punishes.

## Repo map

| Path | What it is |
|---|---|
| **`brand-ai-readiness-audit/`** | **THE SUBMISSION.** `marketplace.json` + 8 skills. This is the only directory that gets zipped. |
| `bench/` | 85 real-site candidates → 64 measured corpus entries across the SEO×GEO quadrants, plus the live/replay runner. |
| `tests/` | 7 local fixture sites, the bundles built from them, and 825 pytest assertions. |
| `tools/` | `validate.py`, `package.py`, `check_coverage.py`, `run_audit.py`, `sweep_audits.py`, `install_local.py`. |
| `docs/` | `EVIDENCE.md` (what the literature supports, and what it doesn't), `ADOBE-BRAND-VISIBILITY.md` (how our checks map to Adobe's own product), `UNSEEN-SWEEP.md` (the scripts-only pass over fifteen unseen sites), `ROLES.md`, `CONTRIBUTING.md`, `todo/`. |
| `TODO.md` | Who builds what, in what order. Index into `docs/todo/`. |
| `docs/examples/` | Real reports the marketplace produced (nike.in, adobe.com/in, crunchyroll.com, ea.com, github.com, vox.com, bbc.co.uk), kept as worked examples. |
| `PLAN.md` | The full architecture and build plan. The shared spec. |

## Status

| Skill | Owner | State |
|---|---|---|
| `audit-orchestrator` | Aryan | complete |
| `site-evidence-collector` | Aryan | complete |
| `crawl-access-audit` | Aryan | complete — the reference implementation |
| `render-extractability-audit` | Lakshay | complete — 16/16 checks |
| `structured-data-audit` | Lakshay | complete — 14/14 checks |
| `answerability-audit` | Mayank | complete — 12/12 checks |
| `freshness-corroboration-audit` | Mayank | complete — 15/15 checks |
| `engagement-audit` | Mayank | complete — 16/16 checks |

**All 91 checks are implemented**, plus 18 proactive recommendations. Every
check has its ID, severity rule, required evidence, human verification step and
its false-positive guards written down in a registry before it was coded.

`tools/check_coverage.py` guards against the failure that is easy to miss: a
check that runs but never fires. Two once shipped as dead code with every other
gate green. A silent check must now either be fixed or declare `rarity` with a
reason. See [`docs/ROLES.md`](docs/ROLES.md).

## Developing and verifying

```bash
pip install -r tools/requirements-dev.txt   # dev tooling only, never shipped

python tests/make_fixtures.py               # build the local test websites
python tests/make_bundles.py                # crawl them into evidence bundles

python -m pytest tests/ -q                  # expect: 825 passed
python tools/validate.py                    # expect: PASS (0 TODOs)
python tools/package.py                     # builds dist/ and checks the 50 MB ceiling
python tools/check_coverage.py              # find checks that never fire anywhere
python bench/run.py --replay                # the quadrant table above, from snapshots
python tools/sweep_audits.py                # every snapshot end to end, for triage
```

Every real-site audit so far has exposed analyzer misreadings before review —
a footer `<time>2026</time>` read as a dateline, a closed `<dialog>` read as an
interstitial, a `/owner/repo` URL space sampled alphabetically. Each fix carries
a regression test and is checked against the bench before it lands;
[`docs/ROLES.md`](docs/ROLES.md) records the working rules that came out of it,
and [`docs/UNSEEN-SWEEP.md`](docs/UNSEEN-SWEEP.md) records the scripts-only
pass over fifteen sites we had never touched — seven of which refused the
crawler outright, which is now reported as an empty sample rather than a grade.

## Team

**Aryan** — contracts, collector, orchestrator, the reference implementation,
tooling and the bench. **Lakshay** — READ and PARSE. **Mayank** — QUOTE, TRUST
and STAY.
