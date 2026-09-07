# Work packet: `engagement-audit`

**Owner:** Mayank · **Order:** #3 of your queue · **Mechanism:** `stay` (STAY)
**Status:** registry frozen, script not yet written

---

## What you are building

`brand-ai-readiness-audit/skills/engagement-audit/scripts/check_engagement.py`

A stdlib-only Python script that reads a completed evidence bundle and emits
candidate findings as JSON. It performs **no network I/O** — every result is a
pure function of the bundle, so the same bundle always yields the same findings.

### Why this stage matters

This is the ENTIRE engagement half of the report and must always appear — the handout weights both halves. STAY-002 is where the two halves meet: a visitor arriving from an AI answer already holds context and a specific question, and a landing page that restarts that conversation loses them despite every upstream stage having worked.

---

## Before you write anything

Read these four, in order. They are frozen contracts; if one seems wrong, raise
it rather than working around it.

1. `brand-ai-readiness-audit/skills/engagement-audit/references/checks.yaml`
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

def check_stay_001(b: Bundle) -> list[dict]:
    """One function per check, named check_<id>."""
    ...

CHECKS = [check_stay_001, ...]   # driver runs each in a try/except
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
| STAY-003, 004, 005, 007, 008, 009, 010, 011, 012, 013, 014, 015 | STAY-001, 002, 006, 016 |

Deterministic checks are computed entirely in the script. Model-judged checks
emit their signals from the script and are finished by the agent following
`SKILL.md`; set `determinism: "model-judged"` on those and remember they may
never be `critical` without deterministic corroboration.

**Start with:** STAY-010 (viewport, near-trivial), then STAY-004 and STAY-009

### The one that will take longest

**STAY-002 — AI-referral landing continuity.** Inherently a judgment call and must never be stated as measured fact. Derive the likely arrival questions from the SITE'S OWN content and category; an invented question produces an invented finding.

The finding is that no SPECIFIC page exists to land on — not that the home page is broad. A home page is allowed to be general. Do not report this on docs sites, where deep pages answer specific questions by construction.

---

## Gotchas that will otherwise cost you a false positive

1. Every performance check here is a STATIC PROXY from the HTML. We do not fetch subresources, run JavaScript, or measure anything in a browser. Never present these as Core Web Vitals, never quote an LCP or CLS score, and never exceed `medium` on proxy evidence alone.

2. We cannot see the fold. Approximate from document order and SAY SO.

3. Count in-content links only for STAY-004 — the bundle marks navigation links with `in_nav`, and global navigation is not a next step.

4. Trust signals and related-content modules are often rendered client-side. Check `render_signals` and `iframes` before reporting them absent.

5. STAY-011 is restricted to structural density (words per heading). We cannot assess typography or contrast, and this must never become a critique of the site's visual design.

---

## Definition of done

```bash
# 1. The marketplace still validates, with your TODOs gone
python tools/validate.py

# 2. Your fixtures behave
python -m pytest tests/ -k stay

# 3. Determinism: the same bundle twice, byte-identical
python brand-ai-readiness-audit/skills/engagement-audit/scripts/check_engagement.py tests/bundles/clean --out /tmp/a.json
python brand-ai-readiness-audit/skills/engagement-audit/scripts/check_engagement.py tests/bundles/clean --out /tmp/b.json
diff /tmp/a.json /tmp/b.json          # must be empty

# 4. The clean fixture stays clean -- this is the false-positive tripwire
python brand-ai-readiness-audit/skills/engagement-audit/scripts/check_engagement.py tests/bundles/clean --stdout \
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

Implement: brand-ai-readiness-audit/skills/engagement-audit/scripts/check_engagement.py

READ FIRST, in this order, and treat them as frozen specs:
  1. brand-ai-readiness-audit/skills/engagement-audit/references/checks.yaml
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
  This is the ENTIRE engagement half of the report and must always appear — the handout weights both halves. STAY-002 is where the two halves meet: a visitor arriving from an AI answer already holds context and a specific question, and a landing page that restarts that conversation loses them despite every upstream stage having worked.

THE CHECK MOST LIKELY TO PRODUCE FALSE POSITIVES:
  STAY-002 — AI-referral landing continuity. Inherently a judgment call and must never be stated as measured fact. Derive the likely arrival questions from the SITE'S OWN content and category; an invented question produces an invented finding.

  The finding is that no SPECIFIC page exists to land on — not that the home page is broad. A home page is allowed to be general. Do not report this on docs sites, where deep pages answer specific questions by construction.

WORK IN THIS ORDER:
  STAY-010 (viewport, near-trivial), then STAY-004 and STAY-009
  ... then the remaining checks in checks.yaml order.

VERIFY BEFORE YOU FINISH:
  python tools/validate.py
  python -m pytest tests/ -k stay
  Run the script twice on the same bundle and diff -- must be identical.
  Run it on tests/bundles/clean -- must produce ZERO critical or high findings.

A missed finding costs one rubric point. A confident false positive costs the
reader's trust in the entire report. When the evidence does not clearly support
a claim, lower confidence or drop the finding.
````
