---
name: audit-orchestrator
description: >-
  Audit a website for the reasons AI assistants fail to find, trust and cite it,
  and the reasons visitors who do arrive fail to engage. Diagnoses crawler
  access blocks, JS-render gaps, missing or contradictory structured data, facts
  locked in non-text, chunks that cannot be quoted standalone, stale or
  uncorroborated claims, brand entity ambiguity, and weak on-site orientation or
  context retention. Produces one report of evidence-backed findings with
  severities plus prioritized, mechanism-sound fixes. Use when asked to audit,
  analyze or review a site or brand for AI discoverability, AI search
  visibility, GEO, AEO (answer engine optimization), LLM citability, AI
  visibility gaps, or on-site engagement, or when asked why a
  brand is missing, misrepresented or ignored by AI assistants. This is the
  entrypoint of the brand-ai-readiness-audit marketplace; it invokes the other
  skills and is the only one that emits the final report.
license: MIT
compatibility: >-
  Requires Python 3.9+ (standard library only) and outbound HTTPS access to the
  audited site. Off-site corroboration additionally uses a web search or fetch
  tool when the host agent provides one, and degrades gracefully when it does not.
allowed-tools: Read Write Bash Glob Grep WebSearch WebFetch
metadata:
  marketplace: brand-ai-readiness-audit
  role: entrypoint
  version: "0.1.0"
---

# Brand AI-Readiness Audit — Orchestrator

Entrypoint for the `brand-ai-readiness-audit` marketplace. Given a site, it
collects evidence once, dispatches six analysis skills over that evidence,
merges their findings under one severity model, strips false positives, and
emits a single report.

## Non-negotiable guardrails

- **Recommend-only.** Never modify the audited site. Never submit a form, log
  in, or send a non-idempotent request. `GET` and `HEAD` only.
- **Respect `robots.txt`** for every fetch. The one documented exception is the
  two-request user-agent probe in `site-evidence-collector`, which re-fetches a
  single already-allowed URL.
- **Never touch authenticated areas**, even when credentials are offered.
- **Hard cap: 270 seconds per site, no exceptions.** The handout's limit is
  five minutes. We stop at 270s so that a slow last request or a slow disk can
  never push a run over it. Enforce it, do not estimate it: take the wall-clock
  time when the audit starts, compute `deadline = start + 270`, and pass
  `--deadline <deadline>` to **every** script you run -- `collect.py` (which
  shrinks its fetch budget to fit) and all six `check_*.py` (which skip any check
  not started by the deadline and list it in `checks_cut_by_deadline`). Give
  collection at most 55% of the cap. Do not start an analysis stage with under
  8 seconds left; record it in `coverage.limitations` as not run instead. A
  mechanism whose analyzer did not run is **not assessed** -- never graded as
  clean.

  Typical runs finish in 12-40s. The cap exists for the site that refuses every
  request and the machine that is slower than ours.
- **Stay inside the fetch budget.** Default ceiling is 25 pages and 120 seconds
  of fetching, with a mandatory politeness delay and never more than 8
  concurrent requests. Every network request the collector makes is capped by
  the time actually remaining, so the wall-clock ceiling is the budget plus at
  most one in-flight request.
- **Report honestly.** If coverage was cut short, say so in `coverage` rather
  than issuing a clean bill of health from a partial crawl.
- **State the boundary of the audit.** Several factors that decide whether an
  assistant cites a site are not properties of the site: whether the engine
  retrieved anything at all, what third-party sources say, which competitors were
  in the same retrieval pool, and which engine was asking. Read
  `references/audit-boundary.md` and put the relevant entries in
  `coverage.limitations` on every report. A grade that silently ignores them
  claims more than was measured.
- **Carry the engine reachability matrix into the report.**
  `crawl-access-audit` emits `engine_reachability`: a per-assistant verdict --
  reachable, partial, degraded or blocked -- measured from the per-agent robots
  resolution and the user-agent probe. Copy it into the report unchanged. It is
  the most legible thing the audit produces ("you are invisible to Perplexity"),
  and the only part of engine-specific behaviour a site crawl can settle. Do not
  let a blocked *training* crawler read as a defect there; the row's `note` says
  why.
- **Run the off-site checks when, and only when, you have a search tool.**
  `freshness-corroboration-audit` skips TRUST-006, 007, 009, 012 and 013 because
  a script cannot see the rest of the web, and records them in
  `checks_skipped`. If your host gives you web search or fetch, complete them
  yourself, then move each from `coverage.checks_skipped` into `findings`:

  | Check | Query to run | Report only when |
  |---|---|---|
  | TRUST-006 | the brand's two or three most specific factual claims, quoted | no independent source repeats a claim the site presents as established |
  | TRUST-007 | the brand name alone | the first page of results is dominated by a different, better-known entity |
  | TRUST-009 | brand name plus the obvious directories for its category | the brand is absent from the registries a machine would consult |
  | TRUST-012 | brand name plus "review" or "vs" | third-party descriptions contradict the site's own positioning |
  | TRUST-013 | brand name in quotes, excluding its own domain | nothing independent exists at all |

  Four rules. Cap at three searches per check and stop early once the answer is
  clear. Never treat an empty result as proof of absence -- a search that found
  nothing is `confidence: low` at most, and for a young or niche brand it is not
  a finding at all. Set `determinism: "model-judged"`, so the ceiling applies.
  And record what you searched in `verification`, so a human can repeat it.

  If you have no search tool, leave them skipped and say so in the report. An
  unrun check is honest; a guessed one is not.
- **Call the engagement axis what it is.** Engagement is measured from
  visitor behaviour -- dwell time, return visits, scroll, clicks -- and a site
  audit has no visitor to observe. `engagement-audit` grades usability proxies
  for it. Say so in the axis headline and in `coverage.limitations`, and never
  let a STAY finding claim a dwell-time, bounce or conversion effect. The
  registry header explains why.
- **Never grade an axis nothing measured.** If no analyzer ran for a mechanism,
  its axis is `"not assessed"`, not a score. Pass `--mechanisms` to
  `scripts/merge_findings.py` listing the mechanisms whose analyzer actually ran,
  and it will do this for you. The same applies when the crawl fetched no page
  at all (a site that answers only in an encoding the collector cannot decode,
  recorded as `undecodable-encoding` in `coverage.skipped`): pass
  `--pages-sampled 0` and engagement is withheld, while discoverability is
  still graded from what REACH measured.

## Inputs

A URL or bare domain. Optional overrides: `max_pages`, `include_paths`,
`exclude_paths`, `site_type` (skip auto-detection), `skip_offsite` (disable
corroboration when no search tool is available).

## Procedure

### 1. Normalize the target

Resolve the domain to a canonical origin: follow `http`→`https` and
`www`/non-`www` redirects and record which form is authoritative. A site that
serves both without redirecting is itself a REACH finding — record it, then use
the sitemap-declared or canonical-declared form as authoritative.

### 2. Collect evidence — once

Follow `../site-evidence-collector/SKILL.md`. It writes an evidence bundle to
`.audit/<domain>/<run-id>/`. Everything downstream reads that bundle.

**Do not let any analysis skill fetch anything.** One crawl, six analyses. This
is what keeps the audit polite, fast, and deterministic.

If collection fails outright (DNS failure, connection refused, whole-site
block), stop and emit a report whose single finding explains the block — that is
the most severe possible discoverability defect, not an audit error.

### 3. Profile the site

Read `references/site-profiles.md` and classify into one of: `ecommerce`,
`saas`, `local-business`, `media-publisher`, `docs`, `portfolio-brochure`,
`marketplace`, `nonprofit-gov`.

The profile gates which checks apply, and is the first and cheapest defense
against false positives: never report missing `Product` markup on a site that
sells nothing, or missing opening hours on a pure-SaaS site. Record the profile
and its evidence in `site_profile`; when confidence is low, say so and prefer
the more permissive gating.

### 4. Dispatch the analysis skills

Each entry in `references/subskills.json` names a skill, its concern, its
inputs, and when to skip it. For each, read `../<skill-id>/SKILL.md` and follow
it against the bundle. They are independent — if the host agent supports
parallel subagent dispatch, fan them out; otherwise run them in listed order.
Order never changes the result.

| Concern | Skill | Question it answers |
|---|---|---|
| reach | `crawl-access-audit` | Can a machine get in? |
| read | `render-extractability-audit` | Can it read what's there? |
| parse | `structured-data-audit` | Can it parse facts out? |
| quote | `answerability-audit` | Can it lift a clear, standalone fact? |
| trust | `freshness-corroboration-audit` | Will it believe and repeat that fact? |
| stay | `engagement-audit` | Does the arriving visitor stay? |

The first five are the discoverability half; `engagement-audit` is the
engagement half. **Both halves must appear in the final report.**

Each returns candidate findings conforming to `references/finding.schema.json`,
plus proactive recommendations.

### 5. Merge

1. **De-duplicate.** Two candidates collide when they share a `check_id` and
   overlapping `affected_scope`. Merge into one, unioning `pages_affected`.
2. **Collapse page-level into site-level.** When one `check_id` fires on ≥60% of
   sampled pages and on ≥3 pages, emit a single site-wide finding rather than N
   page findings. Non-experts cannot act on forty near-identical rows.
3. **Resolve cross-mechanism overlap.** When two findings describe one root
   cause at different stages, keep the earliest-stage one and reference it from
   the later. A site whose content is entirely JS-rendered (READ-001) will also
   trip "no structured data" and "no extractable facts" — reporting all three as
   peers triples the apparent problem count and misdirects the fix. Record the
   suppressed ones in `superseded_by`.

### 6. Score severity

Apply `references/severity-rubric.md`. Severity is computed, never chosen by
feel.

| Severity | Meaning |
|---|---|
| `critical` | Hard-blocks machine access to the site or its core content |
| `high` | Blocks or degrades a whole class of facts, or a major section |
| `medium` | Measurable degradation across sampled pages |
| `low` | Hygiene; marginal effect |

Then escalate one level if `affected_scope.scope` is `site-wide`; de-escalate
one level if `confidence` is `low`.

### 7. Suppress false positives

Run every surviving finding through `references/false-positive-gates.md` and
drop any that fails:

1. **Applicability** — the check is meaningful for this `site_profile`.
2. **Evidence resolves** — `evidence_detail.artifact_refs` is non-empty and
   every ref exists in the bundle. A finding that cannot point at its own
   evidence is deleted, not downgraded.
3. **Model-judged ceiling** — a `determinism: model-judged` finding may not be
   `critical` unless a deterministic finding corroborates it.
4. **Per-check guards** — each registry entry's `false_positive_guards` are
   binding. Re-read them before emitting.
5. **Sample size** — never claim site-wide scope from fewer than 3 sampled pages.
6. **Intentionality** — distinguish a defect from a deliberate choice. Blocking
   *training* crawlers is a legitimate business decision; blocking *retrieval*
   agents removes the brand from answers. Report the first as informational and
   only the second as a defect.

A missed finding costs one rubric point; a confident false positive costs the
reader's trust in the whole report. When genuinely unsure, lower `confidence`
and keep the finding. When the evidence does not support the claim, drop it.

### 8. Order and assign IDs

Sort by `severity` (critical→low), then `check_id`, then the first path in
`affected_scope.pages_affected`. Assign `F-001…` in that order. Sorting is
purely a function of content, so the same site always yields the same IDs.

`scripts/merge_findings.py` performs steps 5, 6 and 8 deterministically.

### 9. Build the scorecard and priority plan

Score `discoverability` and `engagement` 0–100 per `references/scorecard.md`
(each finding deducts by severity and scope, floored at 0), map to a letter
grade, and write a one-line verdict a non-expert can repeat to their team.

Then produce `priority_plan`: the ordered "do these first" list, ranked by
impact ÷ effort, with `why_first` on each entry. Group findings that share a
single fix — one `robots.txt` edit may clear four findings.

### 10. Add proactive recommendations

Findings describe defects. `proactive_recommendations` describe improvements
worth making where no defect was found — the marketplace is explicitly asked for
these. Draw them from each skill's proactive set and keep them specific to what
the evidence shows about *this* site. Generic advice is worth nothing here; a
recommendation that cites something observed in the bundle is worth a lot.

### 11. Emit

Write both:

- **`report.json`** — conforms to `references/report.schema.json`. The contract.
- **`report.md`** — the same content for a human, per
  `references/report-template.md`: verdict, scorecard, top fixes, then findings
  grouped by mechanism with evidence and copy-pasteable snippets.

Run `scripts/validate_report.py report.json` before presenting. If it fails, fix
the report — never present an off-schema report.

Finally, summarize in chat: the verdict line, counts by severity, and the top
three fixes. Link to both files rather than pasting the whole report.

## Output

`report.json` must contain at least `site`, `audited_at`, a counts-by-severity
`summary`, and `findings[]` where each finding has `id`, `title`, `severity`,
`evidence`, and `suggested_action`. This marketplace emits a superset; see
`references/report.schema.json`.

## Bundled resources

| Path | Purpose |
|---|---|
| `references/subskills.json` | Machine-readable dispatch table |
| `references/finding.schema.json` | Finding contract, shared by all skills |
| `references/report.schema.json` | Final report contract |
| `references/severity-rubric.md` | How severity is computed |
| `references/false-positive-gates.md` | The six suppression gates |
| `references/scorecard.md` | Scoring and grading |
| `references/site-profiles.md` | Site-type detection and check gating |
| `references/report-template.md` | Human-readable report shape |
| `scripts/validate_report.py` | Schema validation, stdlib only |
| `scripts/merge_findings.py` | Deterministic merge, sort, and ID assignment |
