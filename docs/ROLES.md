# Who does what

Three people, one frozen set of contracts. **Every skill folder has exactly one
owner**, so nobody edits the same file and there are no merge conflicts.

| Person | Owns | State |
|---|---|---|
| **Aryan** | `audit-orchestrator`, `site-evidence-collector`, `crawl-access-audit`, all contracts, all tooling, the bench | done and tested |
| **Lakshay** | `render-extractability-audit` (READ), `structured-data-audit` (PARSE) | needs its check script |
| **Mayank** | `answerability-audit` (QUOTE), `freshness-corroboration-audit` (TRUST), `engagement-audit` (STAY) | needs its check script |

Lakshay gets the two script-heavy, mostly-deterministic mechanisms: parsing HTML
and validating markup. Mayank gets the three judgment-heavy ones, where the hard
part is restraint rather than parsing.

---

## What "scaffold" actually means

Every skill you own is already **half-built**. Concretely, this exists:

```
skills/<your-skill>/
  SKILL.md                    DONE  - frontmatter, procedure, what to watch for
  references/checks.yaml      DONE  - all your checks, fully specified
  scripts/                    EMPTY - THIS IS YOUR JOB
  references/fixes/           EMPTY - and these
```

So there is **no design work left**. Every check you must implement is already
written down with its ID, its severity rule, what evidence it must cite, how a
human verifies it, and the mistakes that would make it a false positive. You are
translating a finished specification into Python.

**Your job is exactly two things:**

1. Write `scripts/check_<something>.py` — reads a folder of JSON, writes a list
   of findings as JSON. No network, no HTML parsing (already done for you), no
   web framework.
2. Write the fix templates in `references/fixes/` — short Markdown files
   explaining how to fix each problem, with copy-pasteable snippets.

That is it. When both are done and the tests pass, you flip your skill's
`status` in `marketplace.json` from `scaffold` to `complete`.

---

## Day one: get it running (10 minutes)

```bash
git clone <repo> && cd <repo>
pip install -r tools/requirements-dev.txt

# Build the local test websites and crawl them into "evidence bundles"
python tests/make_fixtures.py
python tests/make_bundles.py

# Confirm everything currently passes
python -m pytest tests/ -q          # expect: 57 passed
python tools/validate.py            # expect: PASS (23 TODOs outstanding)
```

If those three commands work, you are set up. The 23 TODOs are your work and
Mayank's.

## Day one: understand the shape (30 minutes)

Do these in order. Do not skip #3 — it is the whole job in one file.

1. **Look at an input.** Open `tests/bundles/clean/MANIFEST.json`, then
   `tests/bundles/clean/pages/p000/extracted.json`. This is what your script
   reads. Notice that the HTML is already parsed for you: headings, links,
   images, scripts, JSON-LD and text are all extracted into plain JSON.

2. **Look at an output.** Run this and read the result:
   ```bash
   python brand-ai-readiness-audit/skills/crawl-access-audit/scripts/check_access.py \
       tests/bundles/blocked-crawlers --stdout
   ```
   That is the exact shape your script must produce.

3. **Read the reference implementation.**
   `brand-ai-readiness-audit/skills/crawl-access-audit/scripts/check_access.py`.
   **Copy its structure exactly.** A `Bundle` class that loads files, one
   `check_*` function per check, the `finding()` and `act()` helpers copied
   verbatim, a `CHECKS` list, and a `main()` that runs them all.

4. **Read your spec.** `skills/<your-skill>/references/checks.yaml`. Each entry
   is one function you have to write.

5. **Read your work packet.** `docs/todo/<your-skill>.md` — it names which check
   to start with, which one will take longest, the traps specific to your
   mechanism, and a paste-ready prompt for Claude Code / Copilot / Antigravity.

---

## Lakshay — your queue

**1. `render-extractability-audit` (16 checks).** Start with `READ-001`: does the
page's content actually appear in the HTML a crawler receives, or is it assembled
in the browser? This is the highest-value check in the whole marketplace.

- Target fixture: `tests/bundles/js-shell` — `READ-001` must fire there.
- Tripwire: `tests/bundles/clean` — nothing of yours may fire at high or critical.
- Then `READ-008` and `READ-009` (both nearly free), then `READ-013`.

**2. `structured-data-audit` (14 checks).** Start with `PARSE-001` and
`PARSE-002` — both are almost free from the bundle. The one that matters is
`PARSE-007`: markup that contradicts what the page visibly says.

- Target fixture: `tests/bundles/contradictory-markup` — `PARSE-007` must fire.

## Mayank — your queue

**1. `answerability-audit` (12 checks).** Start with `QUOTE-001`. The collector
already computed the per-passage signals for you in `chunks.json`
(`names_subject`, `leading_pronoun`, `bare_numbers`, `deictic_terms`) — your job
is aggregation and thresholds, not analysis.

- Target fixture: `tests/bundles/unquotable-chunks` — `QUOTE-001` must fire.

**2. `freshness-corroboration-audit` (15 checks).** Start with `TRUST-001` and
`TRUST-004` — dates are already extracted with their provenance. Then
`TRUST-003` (a sitemap claiming every page changed today while the content is
from 2019).

- Target fixture: `tests/bundles/stale-content`.
- Checks needing a web search (`TRUST-006/007/009/012/013`) are **skipped** when
  no search tool exists — record them in `coverage.checks_skipped`, never
  silently omit them.

**3. `engagement-audit` (16 checks).** Start with `STAY-010` (is there a viewport
meta tag — near-trivial), then `STAY-004` and `STAY-009`.

- Target fixture: `tests/bundles/low-engagement`.

## Aryan — R&D and unblocking

Not implementing the five skills. The job:

- **Own the contracts.** If Lakshay or Mayank hits a case the evidence bundle
  cannot express, that is a contract change and it is yours. Change it once,
  regenerate bundles, tell both.
- **Grow the corpus.** 85 candidates crawled, **64 usable**, every quadrant at or
  above the 10-site target, and the thesis passing: good-SEO/poor-GEO scores 16
  points below good-SEO/good-GEO. Both axes are *measured*, never asserted — GEO
  from the blocking mechanisms, SEO from technical hygiene. To extend it, add
  URLs to `bench/candidates.yaml` and re-run `python bench/build_corpus.py`.
  **Never hand-edit a label**, or it stops being evidence.

  ```
  SEO good / GEO good   24    disc 65
  SEO good / GEO poor   14    disc 49   <-- the money quadrant
  SEO poor / GEO good   17    disc 57
  SEO poor / GEO poor    9    disc 43
  ```

  Eight sites are excluded as **inconclusive**: they refused our browser probe too,
  so we cannot separate a site-level block from our own address being filtered.
  Recording that is the point — claiming a defect there would be exactly the
  confident false positive the rubric punishes. Retry them from a different
  network before drawing any conclusion.

  Live sites drift. Between two runs a day apart, apnews.com began blocking
  retrieval crawlers and gymshark.com went from 1 word of body text to 1743.
  That is why corpus entries are smoke signals and hard assertions live in
  `tests/` against local fixtures.
- **Hunt false positives.** Run `python bench/run.py --live`, read what fired,
  and ask of every finding: *could a competent team have chosen this
  deliberately?* Every "yes" becomes a new `false_positive_guard`.
- **Review against the registry, not against taste.** A finding that contradicts
  its own `checks.yaml` entry is a bug in one of the two; decide which.

---

## What you may not change

Talk to Aryan first. Everything downstream assumes these, and a silent change
breaks the other two people's work:

- `skills/audit-orchestrator/references/finding.schema.json`
- `skills/audit-orchestrator/references/report.schema.json`
- `skills/site-evidence-collector/references/evidence-bundle.schema.json`
- **Check IDs in your own `checks.yaml`.** Never renumber a published ID; retire
  it and add a new one.

You *are* expected to add `false_positive_guards` to your registry as you find
them. That is the one part of the contract meant to keep growing.

## Done means

- [ ] every check in your `checks.yaml` is implemented, or listed in
      `NOT_YET_IMPLEMENTED` with a reason
- [ ] a fix template exists for every `fix_ref` your checks cite
- [ ] `python tools/validate.py --strict` passes
- [ ] your target fixture fires the check it is supposed to fire
- [ ] `tests/bundles/clean` produces **zero** critical or high findings from you
- [ ] running your script twice on one bundle is byte-identical
- [ ] `marketplace.json` status flipped to `complete`

## Order of work

Nothing blocks anything. Contracts are frozen, so all three tracks run in
parallel from day one.

```
contracts frozen  ──┬──►  Lakshay:  READ ──► PARSE
    (done)          │
                    ├──►  Mayank:   QUOTE ──► TRUST ──► STAY
                    │
                    └──►  Aryan:    corpus + false-positive hunting
                                          │
                                          ▼
                              all six analyzers land
                                          ▼
                    python bench/run.py --live --all
                    python tools/package.py
```
