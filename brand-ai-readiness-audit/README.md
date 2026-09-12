# Brand AI-Readiness Audit

An Agent Skill Marketplace that audits any website for **why AI assistants fail
to find, trust and cite it**, and **why the visitors who do arrive fail to
engage** — then reports evidence-backed findings with prioritized, mechanism-
sound fixes.

Recommend-only. No skill in this marketplace ever modifies the audited site.

```bash
# The entrypoint is what you invoke.
"Audit example.com for AI discoverability and engagement"
```

---

## How the marketplace is composed

The Agent Skills spec has no skill-calls-skill primitive: skills are activated by
the host agent from their `description`. So composition works in two layers.

**Baseline, portable everywhere.** `audit-orchestrator/SKILL.md` carries a
subskill registry — each sibling skill's concern, path, inputs, outputs and skip
conditions — mirrored machine-readably in `references/subskills.json`. The
orchestrator reads `../<skill>/SKILL.md` and follows it, in order.

**Optional accelerant.** Where the host supports parallel subagent dispatch, the
six analysis skills fan out over the same evidence bundle. Order never changes
the result.

Only the orchestrator's `description` reads as "audit a website". The other seven
are phrased as components, so a plain *"audit example.com"* activates the
entrypoint and nothing else.

### The decomposition follows the mechanism, not convenience

A page is only citable if a chain of things all succeed. Each skill owns exactly
one link, so a finding always names the stage that actually failed:

```
                  ┌─────────────────────────┐
   a website ───► │ site-evidence-collector │  ONE polite crawl → evidence bundle
                  └───────────┬─────────────┘  (the only skill touching the network)
                              │
        ┌─────────────────────┴──────────────────────┐
        │        all six read the same bundle        │
        ▼                                            ▼
  ┌───────────────────── discoverability ──────────────────┐  ┌── engagement ──┐
  │  REACH  → can a machine get in?                        │  │  STAY          │
  │  READ   → can it read what's there?                    │  │  → does the    │
  │  PARSE  → can it parse a specific fact out?            │  │    visitor who │
  │  QUOTE  → can it lift a clear, standalone fact?        │  │    arrives     │
  │  TRUST  → will it believe and repeat that fact?        │  │    stay?       │
  └────────────────────────────┬───────────────────────────┘  └────────┬───────┘
                               └───────────────┬───────────────────────┘
                                               ▼
                                    ┌─────────────────────┐
                                    │  audit-orchestrator │  merge → severity →
                                    └──────────┬──────────┘  FP gates → report
                                               ▼
                                   report.json  +  report.md
```

An earlier-stage failure makes later stages moot, so the orchestrator marks the
symptoms `superseded_by` their root cause rather than reporting them as peers. A
site whose content is entirely browser-rendered would otherwise trip "no
structured data" and "no extractable facts" too — three findings, one fix.

## The skills

| Skill | Concern | What it answers |
|---|---|---|
| **`audit-orchestrator`** *(entrypoint)* | compose | Profiles the site, dispatches every analysis skill, merges and de-duplicates findings, applies the severity model and false-positive gates, emits the report |
| `site-evidence-collector` | acquire | Performs one polite, robots-respecting, budget-bounded crawl and writes a normalized evidence bundle. **The only skill that touches the network.** Extracts what is on the page; never judges |
| `crawl-access-audit` | **reach** | robots.txt resolved per AI crawler, CDN bot-blocking, sitemaps, indexability, canonicals, redirects, broken links |
| `render-extractability-audit` | **read** | Content assembled in the browser and absent from the HTML, facts locked in images or PDFs, consent walls, semantic structure |
| `structured-data-audit` | **parse** | schema.org coverage and validity, required properties by type, entity graph, markup that contradicts the visible page |
| `answerability-audit` | **quote** | Chunk-level retrieval simulation, explicit identity statements, key-fact extractability, buyer-question coverage |
| `freshness-corroboration-audit` | **trust** | Date honesty and staleness, off-site corroboration of claims, brand entity ambiguity, identity anchors |
| `engagement-audit` | **stay** | Above-the-fold orientation, AI-referral landing continuity, context retention, friction, interstitials, performance proxies |

## Why acquisition is its own skill

Two structural reasons, both of which show up in the output quality:

- **Politeness and determinism.** If six analysis skills each fetched what they
  needed, the audited site would take six times the load and every skill could
  observe a different version of a page. One crawl means one consistent snapshot
  and one auditable place where every rate limit, timeout and `robots.txt` rule
  is enforced.
- **Observation separated from judgment.** The collector records that `#root` is
  empty and a 400 KB hydration payload is present. Whether that is a *defect* is
  `render-extractability-audit`'s call. This makes every analysis skill a pure
  function over a fixed input — reproducible, and testable against fixtures.

## What makes the findings trustworthy

**91 checks**, each specified in its skill's `references/checks.yaml` with a
severity rule, an evidence template, a verification step, and binding
`false_positive_guards`.

Severity is computed, never chosen by feel: a base level from how hard the
mechanism is blocked, then a scope modifier, then a confidence modifier. Every
finding carries `confidence`, `determinism` (`deterministic` or `model-judged`),
its `evidence_detail.artifact_refs`, and a `verification` step the reader can run
to disagree with us.

Six gates run before anything is emitted — the full rules are in
`skills/audit-orchestrator/references/false-positive-gates.md`:

1. **Applicability** — never report missing `Product` markup on a site that sells
   nothing.
2. **Evidence resolves** — a finding that cannot cite its own artifact is
   deleted, not downgraded.
3. **Model-judged ceiling** — a judgment call may not be `critical` without
   deterministic corroboration.
4. **Per-check guards** — written by whoever already met the site pattern that
   fools that check.
5. **Sample size** — no site-wide claim from fewer than 3 sampled pages.
6. **Intentionality** — a deliberate choice is not a defect.

That last gate carries the distinction most audit tools get wrong:

> Blocking **training** crawlers (`GPTBot`, `Google-Extended`, `CCBot`) is a
> legitimate business decision, frequently taken after legal review, and is
> reported as informational.
> Blocking **retrieval** agents (`ChatGPT-User`, `Claude-User`, `PerplexityBot`)
> removes the brand from live answers, and is reported as a defect.

Telling a publisher their deliberate training opt-out is a `critical` bug
discredits every other finding in the report. A missed finding costs one rubric
point; a confident false positive costs the reader's trust in the whole
document.

## The report

`report.json` is the contract; `report.md` is the same content ordered for a
human who has ten minutes. Beyond the required floor (`site`, `audited_at`,
counts-by-severity `summary`, and findings carrying `id`/`title`/`severity`/
`evidence`/`suggested_action`) it adds:

- **`scorecard`** — discoverability × engagement grades and a one-line verdict.
- **`site_profile`** — detected site type, which gates which checks even apply.
- **`coverage`** — pages sampled, what was skipped and why, and which checks
  never ran. This is what separates "we checked and it was fine" from "we never
  checked", and it is not optional.
- **`proactive_recommendations`** — improvements where no defect was found, kept
  out of the severity counts because they are not problems.
- **`priority_plan`** — the ordered "do these first" list, grouping findings that
  share one fix.

Determinism: findings are sorted by content and renumbered `F-001…`, so the same
bundle always yields byte-identical output.

## Running it

```bash
# 1. Collect evidence once
python skills/site-evidence-collector/scripts/collect.py https://example.com \
    --out .audit/example.com/run-01
python skills/site-evidence-collector/scripts/validate_bundle.py .audit/example.com/run-01

# 2. Run the analysis stages over that bundle
python skills/crawl-access-audit/scripts/check_access.py .audit/example.com/run-01 \
    --out reach.json

# 3. Merge, score and validate
python skills/audit-orchestrator/scripts/merge_findings.py reach.json \
    --pages-sampled 25 --out merged.json
python skills/audit-orchestrator/scripts/validate_report.py report.json \
    --bundle .audit/example.com/run-01
```

Normally you do none of this by hand — the entrypoint skill drives it.

## Requirements and guardrails

**Python 3.9+, standard library only, with optional extras.** No `pip install`,
no Node, no browser is *required*: a check that always runs beats a stronger check
that cannot, so every script runs on a bare install and every check has a
documented fallback. Two extras, declared in `requirements-optional.txt`, turn
inferences into measurements when they happen to be present:

- **Playwright** — the collector auto-detects it (`--renderer auto`, the
  default) and renders a sample of pages after the crawl (`--render-pages 6`:
  the seed page plus the thinnest ones). The READ stage then reports a measured
  raw-versus-rendered delta for those pages and says which pages were inferred.
  `--renderer none` disables it; any other value is a command that prints
  rendered HTML for a URL.
- **BeautifulSoup** — the collector cross-checks its own extraction against a
  tree parser and writes `pages/<id>/extract_diff.json` only where they
  disagree. The stdlib parser stays the record.

A sandbox without either gets exactly the stdlib behaviour, and the bundle says
so (`run.json#renderer.available`, `coverage.json#extractor_disagreements`).

- Read-only: `GET` and `HEAD` only. Never authenticates, never submits a form.
- Respects `robots.txt`, including for its own crawl.
- Budgets: 25 pages, 8 concurrent, 10 s per request, 120 s total, politeness
  delay throughout.
- Typical audit completes well inside 5 minutes.

## Build status

`marketplace.json` marks each skill `complete` or `scaffold`. Scaffold skills
have a frozen `SKILL.md` and a complete check registry, with the check script
still to be written; every skill is agentskills.io-valid either way.

```bash
python ../tools/validate.py          # spec, contracts, stdlib rule, determinism
python ../tools/validate.py --strict # TODOs become failures
```

| Complete | Scaffold |
|---|---|
| `audit-orchestrator`, `site-evidence-collector`, `crawl-access-audit` | the five remaining analysis skills |

## License

MIT.
