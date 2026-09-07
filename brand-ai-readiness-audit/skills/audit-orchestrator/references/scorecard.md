# Scorecard

Two axes, matching the two halves of the problem: **discoverability** (why AI
assistants don't find, trust or cite the brand) and **engagement** (why visitors
who arrive don't stay).

The scorecard is derived from findings and is never the primary output. It
exists so a non-expert can see where they stand in one glance and repeat one
sentence to their team. Never let a good score bury a `critical` finding.

## Scoring

Each axis starts at 100. Every finding in that `category` deducts:

| Severity | Base deduction |
|---|---|
| `critical` | 35 |
| `high` | 15 |
| `medium` | 6 |
| `low` | 2 |

Scope multiplier applied to the deduction:

| Scope | Multiplier |
|---|---|
| `site-wide` | 1.0 |
| `section` | 0.6 |
| `page` | 0.3 |

Confidence multiplier:

| Confidence | Multiplier |
|---|---|
| `high` | 1.0 |
| `medium` | 0.8 |
| `low` | 0.5 |

Findings marked `superseded_by` deduct at **0.25×** — the root cause already
carries the damage, and counting symptoms at full weight would double-punish one
underlying defect.

`proactive_recommendations` never deduct. They are not defects.

Floor at 0, round to the nearest integer.

## Grades

| Score | Grade | Reading |
|---|---|---|
| 90–100 | A | Machine-ready. Nothing structural in the way. |
| 75–89 | B | Sound, with specific gaps worth closing. |
| 55–74 | C | Reachable but materially handicapped. |
| 35–54 | D | Substantially invisible or substantially frictional. |
| 0–34 | F | Effectively absent from AI answers, or effectively unusable on arrival. |

Any `critical` finding caps the affected axis at **D (max 54)** regardless of
the arithmetic. A site with one hard block and otherwise flawless hygiene is not
a B — the block is the whole story.

## Verdict line

One sentence, under 400 characters, naming the single biggest reason the site
underperforms and what changes if it is fixed. Written for a marketing lead, not
an engineer.

Good:

> Assistants can reach the site but see an empty page: all product copy is
> rendered in the browser, so 0 of 12 product pages expose their name, price or
> description to a crawler. Server-rendering those pages is the one change that
> unlocks everything else in this report.

Bad — no mechanism, no specifics, unactionable:

> The site has several SEO issues affecting AI visibility and could benefit from
> structured data improvements and better content optimization.

Rules:

- Name the mechanism, not the category.
- Quote one number from the evidence.
- State what the top fix unlocks.
- Never hedge with "may", "could potentially", "it appears that" when the
  evidence is deterministic. Hedge only where `confidence` is genuinely low, and
  then say why.

## Relationship to the SEO × GEO test matrix

The development bench (`bench/corpus.yaml`) labels sites on a **SEO × GEO** 2×2.
That is a *test-design* axis, not a reporting axis: its purpose is to prove the
marketplace catches sites that conventional SEO tooling passes clean.

The report uses discoverability × engagement because those are the two halves
the audit is actually asked about. Do not emit SEO/GEO quadrant labels in the
report — a site owner cannot act on a quadrant.
