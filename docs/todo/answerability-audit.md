# Work packet: `answerability-audit`

**Owner:** Mayank · **Order:** #1 of your queue · **Mechanism:** `quote` (QUOTE)
**Status:** registry frozen, script not yet written

---

## What you are building

`brand-ai-readiness-audit/skills/answerability-audit/scripts/check_answerability.py`

A stdlib-only Python script that reads a completed evidence bundle and emits
candidate findings as JSON. It performs **no network I/O** — every result is a
pure function of the bundle, so the same bundle always yields the same findings.

### Why this stage matters

This is the distinctly generative-search concern and the one conventional SEO tooling does not measure at all. Retrieval happens at CHUNK level: a passage is pulled out of the page and handed to a model without its surroundings. QUOTE-001 is our strongest differentiator — no competing audit tool checks whether a paragraph survives that separation.

---

## Before you write anything

Read these four, in order. They are frozen contracts; if one seems wrong, raise
it rather than working around it.

1. `brand-ai-readiness-audit/skills/answerability-audit/references/checks.yaml`
   — your 12 checks, fully specified. **This is your spec.**
2. `brand-ai-readiness-audit/skills/audit-orchestrator/references/finding.schema.json`
   — the exact output shape.
3. `brand-ai-readiness-audit/skills/site-evidence-collector/references/evidence-bundle.schema.json`
   — your input.
4. `brand-ai-readiness-audit/skills/crawl-access-audit/scripts/check_access.py`
   — **the reference implementation. Copy its structure.**

## The shape to copy

```python
class Bundle:            # thin accessor, loads MANIFEST.json + lazy per-page docs
    ...

def check_quote_001(b: Bundle) -> list[dict]:
    """One function per check, named check_<id>."""
    ...

CHECKS = [check_quote_001, ...]   # driver runs each in a try/except
```

Rules the reference implementation follows and yours must too:

- **One function per check**, named `check_<id>`, returning zero or more candidates.
- **Every candidate cites `artifact_refs` that actually exist** in the bundle.
  The driver drops any candidate whose refs do not resolve — false-positive gate 2.
- **False-positive guards live next to the logic that would trip them**, as code
  where mechanical and as an explicit comment where they need human judgment.
- **Emit the BASE severity only.** The orchestrator owns the scope and confidence
  modifiers; applying them twice inflates every severity in the report.
- **One broken check must never lose the others.** The driver wraps each in
  `try/except` and warns.
- Use the `finding()` and `act()` helpers — copy them verbatim.

## Your checks

| Deterministic | Model-judged |
|---|---|
| QUOTE-001, 005, 009, 010 | QUOTE-002, 003, 004, 006, 007, 008, 011, 012 |

Deterministic checks are computed entirely in the script. Model-judged checks
emit their signals from the script and are finished by the agent following
`SKILL.md`; set `determinism: "model-judged"` on those and remember they may
never be `critical` without deterministic corroboration.

**Start with:** QUOTE-001 (signals are precomputed, so this is mostly aggregation logic)

### The one that will take longest

**QUOTE-001.** The collector already computed `names_subject`, `leading_pronoun`, `bare_numbers`, `has_date` and `deictic_terms` per chunk. Your job is aggregation and thresholds, not re-analysis.

Weigh `heading_path` before counting a chunk as failing: a chunk opening with *"It"* directly under a heading naming the product usually travels fine, because the heading path travels with the chunk. Exclude chunks under ~25 words — list items and table rows legitimately lack a subject.

**Never re-chunk the page.** Identical chunking across runs and across skills is the only thing making these findings reproducible.

---

## Gotchas that will otherwise cost you a false positive

1. This skill has the highest proportion of model-judged checks in the marketplace, so the model-judged ceiling binds hardest here: NOTHING in this skill may emit `critical` without deterministic corroboration.

2. For QUOTE-006, derive the question set from the site's OWN category and offering. A generic list of twenty hypothetical questions manufactures findings and is exactly the padding the rubric penalises.

3. Enterprise software withholding pricing behind a sales conversation is a strategy, not an omission. Report at most `low` and recommend stating the MODEL (per seat, annual contract, from GBP X) rather than the number.

4. Absence in our sample is not absence from the site. Check `coverage.skipped` before claiming a fact is missing anywhere.

---

## Definition of done

```bash
# 1. The marketplace still validates, with your TODOs gone
python tools/validate.py

# 2. Your fixtures behave
python -m pytest tests/ -k quote

# 3. Determinism: the same bundle twice, byte-identical
python brand-ai-readiness-audit/skills/answerability-audit/scripts/check_answerability.py tests/bundles/clean --out /tmp/a.json
python brand-ai-readiness-audit/skills/answerability-audit/scripts/check_answerability.py tests/bundles/clean --out /tmp/b.json
diff /tmp/a.json /tmp/b.json          # must be empty

# 4. The clean fixture stays clean -- this is the false-positive tripwire
python brand-ai-readiness-audit/skills/answerability-audit/scripts/check_answerability.py tests/bundles/clean --stdout \
  | python -c "import json,sys; f=json.load(sys.stdin)['findings']; \
      bad=[x for x in f if x['severity'] in ('critical','high')]; \
      print('FAIL', bad) if bad else print('OK: no critical/high on clean site')"
```

Also required before you call it done:

- [ ] Every check in `checks.yaml` is either implemented or listed in
      `NOT_YET_IMPLEMENTED` with a reason.
- [ ] Fix templates written for every `fix_ref` your checks cite.
- [ ] `python tools/validate.py --strict` passes for your skill.
- [ ] No non-stdlib imports (validate.py enforces this).
- [ ] No `datetime.now()`, no `time.time()`, no unseeded `random` — findings must
      be reproducible.

---

## Paste-ready prompt for your coding agent

Copy everything below into Claude Code, Copilot or Antigravity from the repo root.

````text
You are implementing one skill in an Agent Skill Marketplace that audits websites
for AI discoverability and on-site engagement. The repo is a scaffold: contracts
are frozen, three skills are complete, and mine is not yet written.

Implement: brand-ai-readiness-audit/skills/answerability-audit/scripts/check_answerability.py

READ FIRST, in this order, and treat them as frozen specs:
  1. brand-ai-readiness-audit/skills/answerability-audit/references/checks.yaml
     -- my 12 checks, each with a severity_rule, evidence_template,
        verification step and BINDING false_positive_guards
  2. brand-ai-readiness-audit/skills/audit-orchestrator/references/finding.schema.json
     -- the exact output shape
  3. brand-ai-readiness-audit/skills/site-evidence-collector/references/evidence-bundle.schema.json
     -- the input I read
  4. brand-ai-readiness-audit/skills/crawl-access-audit/scripts/check_access.py
     -- THE REFERENCE IMPLEMENTATION. Mirror its structure exactly: a Bundle
        accessor class, one check_<id> function per check, the finding() and
        act() helpers copied verbatim, a CHECKS list, and a driver that wraps
        each check in try/except and drops candidates whose artifact_refs do
        not resolve.

HARD CONSTRAINTS:
  - Python 3.9+, STANDARD LIBRARY ONLY. No requests, no bs4, no yaml, nothing
    that needs pip. This ships inside the submission and must run on a bare
    Python install.
  - No network I/O of any kind. Read the bundle from disk, nothing else.
  - Fully deterministic: no datetime.now(), no time.time(), no unseeded random,
    no iteration over an unsorted set. The same bundle must produce byte-identical
    output every run.
  - Emit BASE severity only, straight from each check's severity_rule. The
    orchestrator applies scope and confidence modifiers; doing it here too
    double-counts and inflates every severity.
  - Every finding must cite evidence_detail.artifact_refs that really exist in
    the bundle, and an `evidence` string that STATES WHAT WAS OBSERVED with
    numbers -- never a restatement of the title.
  - The false_positive_guards in checks.yaml are BINDING. Implement every guard
    that can be evaluated mechanically as actual code, and leave an explicit
    comment for each guard that needs agent judgment at report time.
  - Checks marked `detection: model-judged` must set determinism "model-judged"
    and must never emit severity "critical".

MECHANISM CONTEXT:
  This is the distinctly generative-search concern and the one conventional SEO tooling does not measure at all. Retrieval happens at CHUNK level: a passage is pulled out of the page and handed to a model without its surroundings. QUOTE-001 is our strongest differentiator — no competing audit tool checks whether a paragraph survives that separation.

THE CHECK MOST LIKELY TO PRODUCE FALSE POSITIVES:
  QUOTE-001. The collector already computed names_subject, leading_pronoun, bare_numbers, has_date and deictic_terms per chunk. Your job is aggregation and thresholds, not re-analysis.

  Weigh heading_path before counting a chunk as failing: a chunk opening with *"It"* directly under a heading naming the product usually travels fine, because the heading path travels with the chunk. Exclude chunks under ~25 words — list items and table rows legitimately lack a subject.

  Never re-chunk the page. Identical chunking across runs and across skills is the only thing making these findings reproducible.

WORK IN THIS ORDER:
  QUOTE-001 (signals are precomputed, so this is mostly aggregation logic)
  ... then the remaining checks in checks.yaml order.

VERIFY BEFORE YOU FINISH:
  python tools/validate.py
  python -m pytest tests/ -k quote
  Run the script twice on the same bundle and diff -- must be identical.
  Run it on tests/bundles/clean -- must produce ZERO critical or high findings.

A missed finding costs one rubric point. A confident false positive costs the
reader's trust in the entire report. When the evidence does not clearly support
a claim, lower confidence or drop the finding.
````
