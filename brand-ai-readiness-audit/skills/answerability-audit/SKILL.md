---
name: answerability-audit
description: >-
  QUOTE stage of the brand-ai-readiness-audit marketplace. Analyzes a
  collected evidence bundle for content that cannot be quoted once
  retrieved: passages that fail standalone comprehension when pulled out of
  the page, no explicit statement of what the organization is, key facts
  absent or vague, abstract claims where concrete ones are needed, missing
  answer-shaped pages such as FAQ, pricing or comparison, unanswered buyer
  questions, answers buried below preamble, and inconsistent naming. Emits
  candidate QUOTE findings with evidence and severity. Invoked by
  audit-orchestrator as one stage of a full audit; it reads the evidence
  bundle and never fetches anything itself.
license: MIT
compatibility: >-
  Requires Python 3.9+ (standard library only). Reads a completed evidence
  bundle produced by site-evidence-collector. No network access needed or used.
allowed-tools: Bash Read Grep
metadata:
  marketplace: brand-ai-readiness-audit
  role: analysis
  mechanism: quote
  stage: "4"
  version: "0.1.0"
---

# Answerability Audit (QUOTE)

**The question this stage answers: Can a machine lift a clear, self-contained fact?**

The distinctly generative-search concern, and the one conventional SEO tooling does not measure at all. A page can be reachable, readable and perfectly marked up and still never be quoted.

The mechanism is **chunk-level retrieval**. A passage is pulled out of the page and handed to a model without its surroundings. A paragraph reading *"It starts at GBP 29 per month"* is useless the moment it is separated from the heading that named the product — and that separation is the normal case, not an edge case.

## Inputs

A completed evidence bundle. This skill **never fetches anything** — all network
I/O belongs to `site-evidence-collector`. Everything below is a pure
function of the bundle, so the same bundle always produces the same findings.

| Artifact | Used for |
|---|---|
| `pages/*/chunks.json` -> `chunks[].signals` | QUOTE-001 (precomputed) |
| `pages/*/chunks.json` -> `heading_path` | QUOTE-001 context weighting |
| `pages/*/extracted.json` -> `text` | QUOTE-002/003/004/008 |
| `MANIFEST.json` -> `pages`, `sitemaps` | QUOTE-005 page-type coverage |
| `pages/*/extracted.json` -> `title`, `headings` | QUOTE-010/011 |

## Procedure

### 1. Run the deterministic checks

```bash
python scripts/check_answerability.py <bundle-path> --out quote-candidates.json
```

The script computes the four deterministic checks (QUOTE-001, 005, 009, 010) in
full and emits the precomputed signals for the eight model-judged checks
(QUOTE-002, 003, 004, 006, 007, 008, 011, 012) with `determinism: "model-judged"`
for the agent to finish per the steps below. It reads only the bundle, does no
network I/O, and produces byte-identical output on repeated runs.

### 2. Read the registry before trusting any candidate

`references/checks.yaml` holds all 12 checks. **The
`false_positive_guards` are binding, not advisory.** Re-read the guards for each
`check_id` before emitting, and drop any candidate whose guard condition holds.

Implement mechanically-evaluable guards in the script. Guards needing context
the script does not have are applied by you, here.

### 3. The model-judged ceiling applies hardest here

This skill carries the highest proportion of model-judged checks in the marketplace, so false-positive gate 3 binds with full force: **no check here may emit `critical`** without a deterministic finding corroborating it, and every model-judged finding needs a `verification` step a human can actually perform to disagree with us.

The collector precomputes the deterministic half of QUOTE-001 in `chunks.json`: `names_subject`, `leading_pronoun`, `bare_numbers`, `has_date`, `deictic_terms`. **The script counts; the model judges.** Weigh `heading_path` before counting a chunk as failing — a chunk opening with *"It"* directly under a heading naming the product usually travels fine, because the heading path travels with it.

**Never re-chunk the page.** Identical chunking across runs and across skills is what makes these findings reproducible at all.

Prefer lower confidence over a confident guess. A wrong QUOTE finding is the easiest kind for a reader to spot and dismiss.

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
`mechanism: "quote"` and `category: "discoverability"`. Return them to the
orchestrator; it assigns final ids, applies the scope and confidence modifiers,
and resolves supersession.

Do not apply the severity modifiers yourself — emit the base level from the
registry's `severity_rule`. Applying them twice inflates severities.

## Bundled resources

| Path | Purpose |
|---|---|
| `references/checks.yaml` | All 12 checks: severity rules, evidence templates, FP guards |
| `references/fixes/self-contained-writing.md` | Writing passages that survive retrieval |
| `references/fixes/answer-shaped-content.md` | FAQ, pricing, comparison page patterns |
| `scripts/check_answerability.py` | Deterministic QUOTE checks, stdlib only |
