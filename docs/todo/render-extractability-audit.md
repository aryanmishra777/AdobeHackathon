# Work packet: `render-extractability-audit`

**Owner:** Lakshay · **Order:** #1 of your queue · **Mechanism:** `read` (READ)
**Status:** registry frozen, script not yet written

---

## What you are building

`brand-ai-readiness-audit/skills/render-extractability-audit/scripts/check_render.py`

A stdlib-only Python script that reads a completed evidence bundle and emits
candidate findings as JSON. It performs **no network I/O** — every result is a
pure function of the bundle, so the same bundle always yields the same findings.

### Why this stage matters

READ-001 is the single highest-value check in the marketplace. A site whose content is assembled in the browser looks perfect to its owner and is empty to every crawler that does not run JavaScript. It is also the root cause that supersedes most PARSE and QUOTE findings on the same pages, so getting its threshold right changes the shape of the whole report.

---

## Before you write anything

Read these four, in order. They are frozen contracts; if one seems wrong, raise
it rather than working around it.

1. `brand-ai-readiness-audit/skills/render-extractability-audit/references/checks.yaml`
   — your 16 checks, fully specified. **This is your spec.**
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

def check_read_001(b: Bundle) -> list[dict]:
    """One function per check, named check_<id>."""
    ...

CHECKS = [check_read_001, ...]   # driver runs each in a try/except
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
| READ-001, 002, 003, 005, 007, 008, 009, 010, 012, 013, 014, 015, 016 | READ-004, 006, 011 |

Deterministic checks are computed entirely in the script. Model-judged checks
emit their signals from the script and are finished by the agent following
`SKILL.md`; set `determinism: "model-judged"` on those and remember they may
never be `critical` without deterministic corroboration.

**Start with:** READ-001, then READ-008 and READ-009 (both trivial), then READ-013

### The one that will take longest

**READ-001.** Do not fire on any single signal. Require the combination: an empty app-shell mount OR a framework marker, AND a low `main_word_count`, AND either a hydration payload or a very low text-to-markup ratio. A Next.js page with 1200 words of server-rendered text is completely fine and firing on it is an embarrassing false positive.

When `run.renderer.available` is false — the normal case — this is an **inference**, not a measurement. Set `confidence` to `medium`, say so in the evidence string, and add a note to `coverage.limitations`.

---

## Gotchas that will otherwise cost you a false positive

1. `alt=None` means the attribute is absent; `alt=""` means an explicit decorative image and is CORRECT. Counting the second as a defect is the classic READ-008 false positive, and the bundle preserves the distinction precisely so you can avoid it.

2. Skip pages where `request.json#truncated` is true — we cut the body off, so a low word count says nothing about the site.

3. Most accordions and tabs render all panels into the DOM and hide them with CSS. That is fine. READ-011 fires only when the panel text is genuinely absent from the HTML.

---

## Definition of done

```bash
# 1. The marketplace still validates, with your TODOs gone
python tools/validate.py

# 2. Your fixtures behave
python -m pytest tests/ -k read

# 3. Determinism: the same bundle twice, byte-identical
python brand-ai-readiness-audit/skills/render-extractability-audit/scripts/check_render.py tests/bundles/clean --out /tmp/a.json
python brand-ai-readiness-audit/skills/render-extractability-audit/scripts/check_render.py tests/bundles/clean --out /tmp/b.json
diff /tmp/a.json /tmp/b.json          # must be empty

# 4. The clean fixture stays clean -- this is the false-positive tripwire
python brand-ai-readiness-audit/skills/render-extractability-audit/scripts/check_render.py tests/bundles/clean --stdout \
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

Implement: brand-ai-readiness-audit/skills/render-extractability-audit/scripts/check_render.py

READ FIRST, in this order, and treat them as frozen specs:
  1. brand-ai-readiness-audit/skills/render-extractability-audit/references/checks.yaml
     -- my 16 checks, each with a severity_rule, evidence_template,
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
  READ-001 is the single highest-value check in the marketplace. A site whose content is assembled in the browser looks perfect to its owner and is empty to every crawler that does not run JavaScript. It is also the root cause that supersedes most PARSE and QUOTE findings on the same pages, so getting its threshold right changes the shape of the whole report.

THE CHECK MOST LIKELY TO PRODUCE FALSE POSITIVES:
  READ-001. Do not fire on any single signal. Require the combination: an empty app-shell mount OR a framework marker, AND a low main_word_count, AND either a hydration payload or a very low text-to-markup ratio. A Next.js page with 1200 words of server-rendered text is completely fine and firing on it is an embarrassing false positive.

  When run.renderer.available is false — the normal case — this is an inference, not a measurement. Set confidence to medium, say so in the evidence string, and add a note to coverage.limitations.

WORK IN THIS ORDER:
  READ-001, then READ-008 and READ-009 (both trivial), then READ-013
  ... then the remaining checks in checks.yaml order.

VERIFY BEFORE YOU FINISH:
  python tools/validate.py
  python -m pytest tests/ -k read
  Run the script twice on the same bundle and diff -- must be identical.
  Run it on tests/bundles/clean -- must produce ZERO critical or high findings.

A missed finding costs one rubric point. A confident false positive costs the
reader's trust in the entire report. When the evidence does not clearly support
a claim, lower confidence or drop the finding.
````
