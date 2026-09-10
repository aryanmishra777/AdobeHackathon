---
name: engagement-audit
description: >-
  STAY stage of the brand-ai-readiness-audit marketplace, covering the
  on-site engagement half of the audit. Analyzes a collected evidence bundle
  for reasons visitors leave: a page top that never says what this is,
  landing pages that restart the conversation a visitor arrived from instead
  of continuing it, no clear next action, dead-end pages, weak orientation
  and lost search or filter context, interstitials on entry, page-weight and
  layout-shift risks, missing mobile viewport, form friction, accessibility
  basics and absent trust signals. Emits candidate STAY findings with
  evidence and severity. Invoked by audit-orchestrator as one stage of a
  full audit.
license: MIT
compatibility: >-
  Requires Python 3.9+ (standard library only). Reads a completed evidence
  bundle produced by site-evidence-collector. No network access needed or used.
allowed-tools: Bash Read Grep
metadata:
  marketplace: brand-ai-readiness-audit
  role: analysis
  mechanism: stay
  stage: "6"
  version: "0.1.0"
---

# Engagement Audit (STAY)

**The question this stage answers: Does the visitor who arrives actually stay?**

The entire second half of the problem, and it **must always appear in the report**. Everything upstream is about getting found and cited; this stage is about the seconds after someone clicks through.

**STAY-002 is where the two halves meet.** A visitor arriving from an AI answer is not a cold search visitor: they already hold context and a specific question the assistant partly answered. If the landing page restarts that conversation from scratch — a generic home page, a hero unrelated to the query — they bounce despite every upstream stage having worked. That is the *no context retention* failure from the Round-2 appendix.

## Inputs

A completed evidence bundle. This skill **never fetches anything** — all network
I/O belongs to `site-evidence-collector`. Everything below is a pure
function of the bundle, so the same bundle always produces the same findings.

| Artifact | Used for |
|---|---|
| `pages/*/extracted.json` -> `headings`, `text` | STAY-001/011 |
| `pages/*/extracted.json` -> `links` (with `in_nav`) | STAY-003/004/005/015 |
| `pages/*/extracted.json` -> `forms` | STAY-006/012/013 |
| `pages/*/extracted.json` -> `scripts`, `images`, `meta` | STAY-008/009/010/014 |
| `pages/*/request.json` -> `timing` | STAY-008 |

## Procedure

### 1. Run the deterministic checks

```bash
python scripts/check_engagement.py <bundle-path> --out stay-candidates.json
```

The script computes the deterministic checks (STAY-003, 004, 005, 007, 008, 009,
010, 011, 012, 013, 014) in full and emits the precomputed signals for the
model-judged checks (STAY-001, 002, 006, 016) with `determinism: "model-judged"`.
STAY-015 and STAY-016 record themselves in `checks_skipped` when the site profile
is outside their `applies_when` set; the orchestrator folds that into
`coverage.checks_skipped`. Every performance figure is a static proxy from the
HTML, never a Core Web Vitals score. It reads only the bundle, does no network
I/O, and produces byte-identical output on repeated runs.

### 2. Read the registry before trusting any candidate

`references/checks.yaml` holds all 16 checks. **The
`false_positive_guards` are binding, not advisory.** Re-read the guards for each
`check_id` before emitting, and drop any candidate whose guard condition holds.

Implement mechanically-evaluable guards in the script. Guards needing context
the script does not have are applied by you, here.

### 3. Performance figures are proxies, not measurements

Every performance check here is a **static proxy derived from the HTML**. We count render-blocking scripts, images without dimensions and the page's own transfer size. We do not fetch subresources, execute JavaScript, or measure anything in a browser.

So: never present these as Core Web Vitals, never quote an LCP or CLS score, and never exceed `medium` severity on proxy evidence alone. Say plainly in the evidence that the figures are static proxies.

The same restraint applies to layout: we cannot see the fold, typography, contrast or visual prominence. Approximate the fold from document order and say so. STAY-011 is restricted to structural density — words per heading — and must never become a critique of the site's visual design.

### 4. Write the findings

Beyond what the script fills in, each candidate needs:

- **`evidence`** quantified and specific, stating what was observed rather than
  restating the title.
- **`suggested_action.code`** tailored to this site, using real values from the
  bundle. A snippet containing a placeholder will be pasted into production
  verbatim by someone.
- **`verification`** as one step the reader can perform to disagree with us.

Fix templates in `references/fixes/` are starting points, not output.

### 5. Add proactive recommendations

From the `proactive` block of `references/checks.yaml`. These describe
improvements worth making where no defect was found, and must cite something
actually observed in the bundle — generic advice is worth nothing here.

## Output

A JSON array of candidate findings conforming to
`../audit-orchestrator/references/finding.schema.json`, each with
`mechanism: "stay"` and `category: "engagement"`. Return them to the
orchestrator; it assigns final ids, applies the scope and confidence modifiers,
and resolves supersession.

Do not apply the severity modifiers yourself — emit the base level from the
registry's `severity_rule`. Applying them twice inflates severities.

## Bundled resources

| Path | Purpose |
|---|---|
| `references/checks.yaml` | All 16 checks: severity rules, evidence templates, FP guards |
| `references/fixes/orientation.md` | Above-the-fold clarity, CTAs, navigation |
| `references/fixes/ai-referral-landing.md` | Continuing the conversation a visitor arrives with |
| `references/fixes/context-retention.md` | URL-carried search and filter state |
| `references/fixes/consent-and-interstitials.md` | Overlays that block on arrival |
| `references/fixes/performance-proxies.md` | Page weight, viewport, layout shift |
| `scripts/check_engagement.py` | Deterministic STAY checks, stdlib only |
