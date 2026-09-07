# False-positive gates

Every candidate finding passes all six gates or it does not ship. Run them in
order; the cheap gates come first.

The asymmetry that motivates this file: **a missed finding costs one rubric
point; a confident false positive costs the reader's trust in every other
finding in the report.** A site owner who finds one obviously-wrong `critical`
stops reading. Optimize accordingly.

---

## Gate 1 — Applicability

*Is this check meaningful for this kind of site?*

Drop the finding if `site_profile.site_type` is not in the check's
`applies_when`. Consult `site-profiles.md` for the gating table.

Canonical mistakes this gate prevents:

- Missing `Product`/`Offer` markup on a site that sells nothing.
- Missing `LocalBusiness` hours and address on a pure-SaaS or media site.
- "No pricing page" on a docs site, a nonprofit, or an enterprise brand that
  deliberately gates pricing behind sales contact.
- "Thin content" on a legal, contact, or login page — those are supposed to be
  short.
- "No author markup" on a brochure site with no editorial content.

When `site_profile.confidence` is `low`, prefer the **more permissive** gate:
skip the check and record it in `coverage.checks_skipped` rather than guessing.
A check recorded as skipped is honest; a check fired on a misidentified site
type is a false positive.

---

## Gate 2 — Evidence resolves

*Can the finding point at its own proof?*

Require `evidence_detail.artifact_refs` to be non-empty **and** every ref to
exist in the bundle. Verify the refs actually resolve — do not trust that a
plausible-looking path was written.

A finding that cannot cite its evidence is **deleted, not downgraded.** There is
no confidence level appropriate to a claim with no support.

Also require that `evidence` states an observation, not a restatement of the
title. "No structured data was found" is a title. "Crawled 12 product pages;
0/12 contain any `application/ld+json` block" is evidence.

---

## Gate 3 — Model-judged ceiling

*Is a judgment call masquerading as a measurement?*

A finding with `determinism: model-judged` may not carry `severity: critical`
unless a `deterministic` finding on the same page or scope corroborates it. Cap
at `high`.

Additionally, for any model-judged finding, `verification` must give a step a
human can actually perform to disagree with us. If the finding cannot be
falsified by a human in one step, it is an opinion and belongs in
`proactive_recommendations`, not `findings`.

---

## Gate 4 — Per-check guards

*Did the check author already know about this trap?*

Every entry in a `checks.yaml` carries `false_positive_guards`. They are
binding, not advisory. Re-read the guards for the emitting `check_id` before
shipping the finding.

If a guard's condition holds, drop the finding — even when everything else looks
convincing. The guard was written by someone who had already seen the site
pattern that fools this check.

---

## Gate 5 — Sample size

*Are we generalizing from too little?*

- `scope: "site-wide"` requires **≥3 pages checked** and **≥60% affected**.
- `scope: "section"` requires ≥2 pages in that section.
- With fewer than 3 pages in the whole bundle, no finding may claim `site-wide`
  at all; demote to `page` scope and record the limitation in
  `coverage.limitations`.

Absence of evidence is not evidence of absence. If the crawl never reached the
product section, the report says "not sampled", never "no product markup".
Cross-check `coverage.skipped` before claiming anything is missing site-wide.

---

## Gate 6 — Intentionality

*Could a competent team have chosen this deliberately?*

Apply the intentionality table in `severity-rubric.md` (step 5). Summary of the
distinctions that matter most:

| Looks like a defect | Actually |
|---|---|
| Blocking `GPTBot` / `Google-Extended` / `CCBot` | Training opt-out — a business decision. Informational only. |
| Blocking `ChatGPT-User` / `Claude-User` / `PerplexityBot` | Genuine defect: removes the brand from live answers. |
| `noindex` on cart, checkout, account, search, filter pages | Correct practice. Never report. |
| Paywalled article body | Legitimate. Report only the missing `isAccessibleForFree` declaration. |
| Short contact or legal page | Correct. Not thin content. |
| No `Product` schema on a services business | Correct. Not a gap. |
| `nofollow` on user-generated or sponsored links | Correct practice. |
| Deliberately minimal brochure site with no blog | A choice, not staleness. Judge freshness against what the site claims to be, not against a publisher's cadence. |

When the honest answer is "plausibly deliberate", either drop the finding or
emit it at `low`, framed as a trade-off with its cost stated — never as an
error.

---

## After the gates

Findings that survive are ordered and numbered per step 8 of the orchestrator
procedure. Findings dropped at gates 1 or 5 for **coverage** reasons (not
applicability) should be recorded in `coverage.checks_skipped`, so the reader
can tell "we checked and it was fine" apart from "we never checked".

That distinction is most of what makes an audit report trustworthy.
