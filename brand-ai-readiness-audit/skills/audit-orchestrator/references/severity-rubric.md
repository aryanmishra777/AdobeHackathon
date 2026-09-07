# Severity rubric

Severity is **computed**, not chosen. Two auditors applying this file to the
same evidence must land on the same level. If a check's `severity_rule` in a
`checks.yaml` disagrees with this file, this file wins and the registry entry is
a bug.

## Step 1 — base level from blocking-ness

Ask only: *what does this stop a machine from doing?*

| Base | Test | Examples |
|---|---|---|
| `critical` | A machine is **hard-blocked** from the site or its core content. Nothing downstream can succeed. | Retrieval agents disallowed in `robots.txt`; CDN serves 403 or a challenge to bot UAs; site-wide `noindex`; every sampled page's main content absent from raw HTML; DNS/TLS failure |
| `high` | A **whole class of facts** or a **major section** is unavailable or wrong. The site is reachable but the thing a user would ask about is not. | No structured data anywhere on a commerce site; pricing exists only inside images; structured data contradicts the visible page; brand name collides with a better-known entity and nothing disambiguates |
| `medium` | **Measurable degradation** across sampled pages. Facts are extractable but harder to find, trust, or quote than they should be. | Missing `dateModified` on articles; chunks that fail standalone comprehension; no breadcrumbs; thin `alt` coverage on informational images |
| `low` | **Hygiene.** Real but marginal; worth fixing in passing. | Missing `og:image`; a stale copyright year on an otherwise current site; one broken outbound link |

Judge the *mechanism*, not the effort to fix it. A one-line `robots.txt`
mistake that hides the whole site is `critical` even though the fix is trivial;
effort is carried separately in `suggested_action.effort`.

## Step 2 — scope modifier

| Condition | Adjustment |
|---|---|
| `affected_scope.scope == "site-wide"` | **Escalate one level** |
| `affected_scope.scope == "page"` and the page is not the home page or a primary conversion page | **De-escalate one level** |
| `affected_scope.scope == "section"` | No change |

Site-wide requires ≥3 pages checked and ≥60% affected (false-positive gate 5).
Never escalate above `critical` or below `low`.

## Step 3 — confidence modifier

| Condition | Adjustment |
|---|---|
| `confidence == "low"` | **De-escalate one level** |
| `confidence == "medium"` | No change |
| `confidence == "high"` | No change |

Confidence never escalates. It only ever pulls severity down. An auditor who is
unsure does not get to shout.

## Step 4 — the model-judged ceiling

A finding with `determinism: model-judged` **may not be `critical`** unless a
`deterministic` finding on the same page or scope corroborates it. Cap it at
`high` and record the reason in `verification`.

This exists because our judgment-heavy checks — chunk comprehension, identity
clarity, landing-page continuity — are the ones most likely to be wrong, and a
wrong `critical` is the single most expensive error this marketplace can make.

## Step 5 — the intentionality test

Before emitting anything above `low`, ask: **could a competent team have chosen
this on purpose?**

| Observation | Verdict |
|---|---|
| `Disallow` for `GPTBot`, `Google-Extended`, `CCBot`, `Applebot-Extended`, `meta-externalagent` | **Not a defect.** These are training-corpus opt-outs and a legitimate business decision. Report as informational (`low`), and only note the trade-off. |
| `Disallow` for `ChatGPT-User`, `OAI-SearchBot`, `Claude-User`, `Claude-SearchBot`, `PerplexityBot`, `Perplexity-User` | **Defect.** These fetch on behalf of a user asking a question right now. Blocking them removes the brand from live answers. |
| `noindex` on `/cart`, `/checkout`, `/account`, `/search`, tag and filter pages | **Correct practice.** Never report. |
| `noindex` on content, product, or landing pages | **Defect.** |
| Paywall or login gate on a publisher's premium content | **Not a defect** in itself. Report only the absence of a machine-readable `isAccessibleForFree` / `hasPart` declaration, which is what lets an assistant cite the page honestly. |
| Staging, `robots.txt` disallow-all on a subdomain that is clearly not production | **Out of scope.** Note in `coverage.limitations`, do not report. |

When the answer is "yes, plausibly deliberate", either drop the finding or
report it at `low` framed as a trade-off rather than an error. Telling a
publisher that their deliberate AI-training opt-out is a `critical` bug destroys
the credibility of every other finding in the report.

## Priority is not severity

`severity` describes the damage. `suggested_action.priority` describes what to
do first, and additionally weighs effort and unblocking.

- A `high` finding fixable in ten minutes that unblocks four others outranks a
  `critical` requiring a re-platform.
- Default `priority = severity`, then adjust: raise one level when `effort: S`
  or the fix unblocks other findings; lower one level when `effort: L` and a
  cheaper partial mitigation exists.
- Record the reasoning in `priority_plan[].why_first`, never silently.
