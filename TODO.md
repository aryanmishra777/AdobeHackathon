# TODO — who builds what, in what order

The detailed instructions live in **[`docs/todo/`](docs/todo/)**, one packet per
skill. Each packet is self-contained: your spec, your input, the shape to copy,
the traps specific to your mechanism, a definition of done you can run as
commands, and a **paste-ready prompt** for Claude Code / Copilot / Antigravity at
the bottom.

This file is just the index. Read your packet, not this.

---

## The queue

### Lakshay

| # | Packet | Skill | Checks | Write |
|---|---|---|---|---|
| 1 | [`render-extractability-audit.md`](docs/todo/render-extractability-audit.md) | READ | 16 | `scripts/check_render.py` + `references/fixes/` |
| 2 | [`structured-data-audit.md`](docs/todo/structured-data-audit.md) | PARSE | 14 | `scripts/check_structured_data.py` + `references/fixes/` |

Start with **READ-001** — does the page's content actually appear in the HTML a
crawler receives, or is it assembled in the browser? Highest-value check in the
marketplace, and the one that supersedes most PARSE and QUOTE findings on the
same pages. Then READ-008 and READ-009 (both nearly free), then READ-013.

### Mayank

| # | Packet | Skill | Checks | Write |
|---|---|---|---|---|
| 1 | [`answerability-audit.md`](docs/todo/answerability-audit.md) | QUOTE | 12 | `scripts/check_answerability.py` + `references/fixes/` |
| 2 | [`freshness-corroboration-audit.md`](docs/todo/freshness-corroboration-audit.md) | TRUST | 15 | `scripts/check_trust.py` + `references/fixes/` |
| 3 | [`engagement-audit.md`](docs/todo/engagement-audit.md) | STAY | 16 | `scripts/check_engagement.py` + `references/fixes/` |

Start with **QUOTE-001**. The collector already computed the per-passage signals
for you in `chunks.json` (`names_subject`, `leading_pronoun`, `bare_numbers`,
`deictic_terms`) — your job is aggregation and thresholds, not analysis.

### Aryan

Not implementing the five skills. Owns the contracts, the corpus, and
false-positive hunting. See [`docs/ROLES.md`](docs/ROLES.md).

Nothing blocks anything: contracts are frozen, so all three tracks run in
parallel from day one.

---

## What "scaffold" means

Every skill you own is already half-built:

```
skills/<your-skill>/
  SKILL.md                    DONE  - frontmatter, procedure, what to watch for
  references/checks.yaml      DONE  - all your checks, fully specified
  scripts/                    EMPTY - THIS IS YOUR JOB
  references/fixes/           EMPTY - and these
```

There is **no design work left**. Every check already has its ID, severity rule,
required evidence, human verification step, and the mistakes that would make it a
false positive. You are translating a finished specification into Python.

---

## Setup, once

```bash
pip install -r tools/requirements-dev.txt

python tests/make_fixtures.py     # build the local test websites
python tests/make_bundles.py      # crawl them into evidence bundles

python -m pytest tests/ -q        # expect: 57 passed
python tools/validate.py          # expect: PASS (23 TODOs outstanding)
```

Those 23 TODOs are the work in this file. As you land checks, the count drops.

---

## Definition of done, per skill

- [ ] every check in your `checks.yaml` is implemented, or listed in
      `NOT_YET_IMPLEMENTED` with a reason
- [ ] a fix template exists for every `fix_ref` your checks cite
- [ ] `python tools/validate.py --strict` passes
- [ ] your target fixture fires the check it is supposed to fire
- [ ] `tests/bundles/clean` produces **zero** critical or high findings from you
      — this is the false-positive tripwire and it is the one that matters most
- [ ] running your script twice on one bundle is byte-identical
- [ ] `marketplace.json` status flipped from `scaffold` to `complete`

## Target fixtures

Each defect fixture exists to make one check fire. `clean` exists to make
**nothing** fire.

| Fixture | Must fire |
|---|---|
| `tests/bundles/js-shell` | READ-001 |
| `tests/bundles/contradictory-markup` | PARSE-007 |
| `tests/bundles/unquotable-chunks` | QUOTE-001 |
| `tests/bundles/stale-content` | TRUST-001 / TRUST-003 |
| `tests/bundles/low-engagement` | STAY-004 / STAY-009 |
| `tests/bundles/blocked-crawlers` | REACH-002 (done) |
| `tests/bundles/clean` | **nothing at high or critical** |

---

## The rules you cannot break

Full list in [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md). The ones that bite:

1. **Recommend-only.** Nothing in this marketplace ever modifies an audited site.
2. **No network I/O outside `site-evidence-collector`.** Your script is a pure
   function of the bundle.
3. **stdlib-only Python inside the zip.** No `requests`, no `bs4`, no PyYAML.
   `tools/validate.py` walks the AST and will fail you.
4. **Emit base severity only.** The orchestrator owns scope and confidence
   modifiers; applying them twice inflates every severity in the report.
5. **Never renumber a published check ID.** Retire it and add a new one.
6. **Don't touch the schemas.** `finding.schema.json`, `report.schema.json`,
   `evidence-bundle.schema.json` — if one seems wrong, that is a contract change
   and it goes to Aryan. Adding `false_positive_guards` to your own registry is
   the one part of the contract meant to keep growing.
