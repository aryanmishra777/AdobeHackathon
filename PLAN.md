# Round 3 — Brand AI-Readiness Audit Marketplace: base repo scaffold

## Context

Adobe University Hackathon 2026, Round 3 (`6a8ffdf33590a_round3-handout-updated.pdf`). We must ship an **Agent Skill Marketplace** — a `marketplace.json` manifest plus N agentskills.io-compliant skill folders with exactly one entrypoint — that, pointed at any unseen website, audits it for **AI discoverability** (why assistants don't find/cite the brand) and **on-site engagement** (why arriving visitors don't stay), then emits one structured report of findings + prioritized suggested actions. Recommend-only, robots-respecting, <5 min per site, ≤50 MB zip.

Grading is on **the marketplace itself**, not any report it produces: detection accuracy (evidence-backed, few false positives), fix quality (mechanism-sound, specific), composition quality (real separation of concerns, not padding), proactive recommendations, and generalization to unseen sites.

**This plan builds the base repository, not the finished submission.** Aryan + 1 do R&D, contracts, and unblocking; two teammates do mechanical implementation against frozen contracts and detailed TODO packets (written as paste-ready prompts for Copilot / Antigravity / Claude Code). So the priority order is: **freeze the contracts → build one worked vertical slice → generate the work packets.**

### Environment constraints (verified on this machine)

Python 3.14, **no node/npm**, and of the relevant packages only `lxml` is installed — no `requests`, `bs4`, `playwright`. A grader's machine will look like this.

**The stdlib boundary applies to the submission only.** Everything under `brand-ai-readiness-audit/scripts/` is stdlib-only Python (`urllib.request`, `html.parser`, `json`, `re`, `xml.etree`, `gzip`, `concurrent.futures`) — zero third-party imports inside the zip, enforced by `tools/validate.py`. A check that always runs beats a stronger check that can't.

Dev tooling outside the zip (`tools/`, `bench/`, `tests/`) may take dependencies; see `tools/requirements-dev.txt`. The handout places no format restriction on `references/` or `scripts/` ("any structure is fine as long as the rules below hold"), so **check registries are YAML** — they are read by the agent and by humans, both of which handle YAML natively, and comments plus multi-line severity rules matter when hand-authoring ~90 entries. No submission script ever parses YAML: scripts take signals in and emit JSON out.

---

## Architecture

### Composition mechanic (the thing that's easy to get wrong)

The Agent Skills spec has **no skill-calls-skill primitive**. Skills are activated by the host agent from their `description`. So the entrypoint composes in two layers:

1. **Baseline (portable everywhere):** `audit-orchestrator/SKILL.md` carries a **subskill registry** — each sibling skill's concern, relative path, inputs, outputs, and when to skip it — and instructs the agent to read `../<skill>/SKILL.md` and follow it in sequence. Mirrored machine-readably in `references/subskills.json`.
2. **Optional accelerant:** if the host exposes subagent dispatch, fan the six analysis skills out in parallel over the same evidence bundle. Documented as an optimization, never a requirement.

**Activation hygiene:** only the orchestrator's `description` should read as "audit a website." The seven others must be phrased as components ("Invoked by audit-orchestrator as part of a brand AI-readiness audit; analyzes the evidence bundle for …") so a plain "audit example.com" activates the entrypoint and nothing else.

### 8 skills, mapped 1:1 onto the Round-2 appendix mechanism chain

```
brand-ai-readiness-audit/            <- marketplace root (this is what we zip)
  marketplace.json
  README.md
  skills/
    audit-orchestrator/              ENTRYPOINT   — scope, dispatch, merge, prioritize, emit
    site-evidence-collector/         ACQUISITION  — the ONLY skill that touches the network
    crawl-access-audit/              REACH        — can the machine get in?
    render-extractability-audit/     READ         — can it read what's there?
    structured-data-audit/           PARSE        — can it parse facts out?
    answerability-audit/             QUOTE        — can it lift a clear, standalone fact?
    freshness-corroboration-audit/   TRUST        — will it believe and repeat that fact?
    engagement-audit/                STAY         — does the visitor who arrives stay?
```

Two structural decisions that carry the "genuine separation of concerns" rubric line:

- **All network I/O lives in `site-evidence-collector`.** One polite crawl produces a cached evidence bundle on disk; the six analysis skills are pure functions over that bundle. This gives us determinism, no re-fetching a site six times, and every robots/rate-limit/safety guardrail auditable in a single folder.
- **Collector extracts, analysis skills interpret.** The collector emits a normalized page model ("what is literally on the page" — headings, links, images, scripts, verbatim JSON-LD blocks, text, counts). It never judges. `structured-data-audit` validates and interprets JSON-LD the collector merely captured. This prevents six skills re-parsing HTML six different ways.

---

## Contracts (freeze these first — everything else depends on them)

Source of truth lives inside the skill folders (so each skill stays self-contained and the zip is complete); `tools/validate.py` enforces cross-skill consistency rather than duplicating files.

### 1. Evidence bundle — `site-evidence-collector/references/evidence-bundle.schema.json`

```
.audit/<domain>/<run-id>/
  MANIFEST.json          schema_version, index of all artifacts
  run.json               target, audited_at, config, budgets, collector version
  robots.txt.raw         + fetch metadata
  sitemaps/*.xml
  ua_probe.json          browser-UA vs bot-UA status/body-length diffs
  coverage.json          pages attempted / fetched / skipped + reason
  pages/<page-id>/
    request.json         url, final_url, redirect_chain, timings
    response.headers.json
    raw.html
    rendered.html        OPTIONAL — only when a renderer was available
    extracted.json       normalized page model (see below)
  external/              OPTIONAL — off-site lookups for TRUST
```

`extracted.json` is the workhorse: title, meta, canonical, headings tree, link graph (internal/external/nofollow), image inventory (src/alt/dimensions/bytes), script inventory (blocking/async/third-party), verbatim `jsonld[]` + microdata, main-text extraction, word counts, text-to-markup ratio, app-shell markers, `<noscript>` content.

**Determinism rules:** page selection is home + sitemap-priority + BFS from home, sorted, capped, no randomness. Default budgets: ≤25 pages, 8 concurrent, 10s/request, 120s total fetch. Same site in → same bundle out.

### 2. Finding — `audit-orchestrator/references/finding.schema.json`

Handout requires `id`, `title`, `severity`, `evidence`, `suggested_action`. We ship a superset:

```jsonc
{
  "id": "F-001",                    // sequential in final report
  "check_id": "REACH-002",          // stable registry ID
  "title": "...",
  "severity": "critical|high|medium|low",
  "confidence": "high|medium|low",
  "determinism": "deterministic|model-judged",
  "category": "discoverability|engagement",
  "mechanism": "reach|read|parse|quote|trust|stay",
  "evidence": "Human-readable, quantified. 'Crawled 12 product pages; 0/12 contain schema.org markup.'",
  "evidence_detail": { "pages_affected": [], "counts": {}, "artifact_refs": [] },
  "affected_scope": { "pages_checked": 12, "pages_affected": 12, "scope": "site-wide|section|page" },
  "verification": "How a human re-checks this in one step.",
  "suggested_action": {
    "summary": "...", "priority": "critical|high|medium|low",
    "steps": ["..."], "code": "copy-pasteable snippet",
    "effort": "S|M|L", "impact_rationale": "why this fixes the mechanism"
  }
}
```

### 3. Report — `audit-orchestrator/references/report.schema.json`

Required floor (`site`, `audited_at`, counts-by-severity `summary`, `findings[]`) plus:

- `scorecard` — **discoverability × engagement** grades + one-line verdict. (The SEO×GEO 2×2 is our *test-matrix* axis; the report uses the handout's own axes.)
- `site_profile` — detected site type (ecommerce / SaaS / local business / media / docs / portfolio), primary entity, pages sampled.
- `coverage` — what was sampled, what was skipped and why. Partial audits stay honest instead of silently under-reporting.
- `proactive_recommendations[]` — same `suggested_action` shape, for improvements where no defect was detected. Kept out of `findings[]` because they aren't problems.
- `priority_plan[]` — ranked "do these first" ordering with rationale, for the non-expert reader.

Plus `report.md` — human-readable companion. `report.json` remains the contract.

### 4. Check registry — `<skill>/references/checks.yaml`

Every check pre-specified before implementation. This is the artifact that lets three people work in parallel.

```yaml
- id: REACH-002
  mechanism: reach
  title_template: "AI retrieval crawlers are blocked by robots.txt"
  applies_when: "always"
  inputs: [robots.txt.raw, ua_probe.json]
  detection: deterministic
  severity_rule: "critical if all live-retrieval agents blocked site-wide; high if one major agent; medium if a content section only"
  evidence_template: "robots.txt disallows {agents} on {paths}."
  fix_ref: references/fixes/robots-ai-agents.md
  false_positive_guards:
    - "Google-Extended / CCBot / Applebot-Extended blocks are TRAINING opt-outs — a legitimate business choice, never a defect. Report as informational only."
```

---

## Severity, determinism, and false-positive control

Severity is computed, not vibed: `f(blocking-ness, scope, mechanism stage)`.

| Level | Meaning |
|---|---|
| critical | Hard-blocks machine access to the site or its core content (retrieval agents disallowed, CDN 403s bot UAs, all content JS-only, site-wide noindex) |
| high | Blocks or degrades a whole class of facts or a major section |
| medium | Measurable degradation across sampled pages |
| low | Hygiene / marginal |

Escalate one level when scope is site-wide; de-escalate when confidence is low.

**Six layers of false-positive defense** (the rubric calls this out explicitly):

1. **Applicability gates** — checks run only where meaningful. No "missing Product schema" on a site with no products.
2. **Evidence requirement** — orchestrator drops any finding whose `evidence_detail.artifact_refs` is empty or fails to resolve against the bundle.
3. **Model-judged ceiling** — a `determinism: model-judged` finding can never be `critical` without deterministic corroboration.
4. **Per-check `false_positive_guards`** in the registry, restated in each SKILL.md.
5. **Sample-size gate** — never generalize site-wide from fewer than 3 pages.
6. **Clean-fixture tripwire** in tests — a deliberately well-built fixture site must produce zero critical and zero high findings.

**Determinism:** stable `check_id` + scope-hash → sort by (severity desc, check_id, scope) → renumber `F-001…`. Sorted JSON keys. No timestamps inside findings. Same site → byte-identical report.

---

## Checks to implement (~90, full enumeration lands in the registries)

| Skill | Count | Representative / novel checks |
|---|---|---|
| `crawl-access-audit` | ~18 | REACH-002 AI retrieval agents disallowed · REACH-003 training-crawler blocks (informational, **not** a defect) · REACH-005 CDN 403s bot UAs despite robots allow · REACH-009 `nosnippet`/`max-snippet:0` suppressing quotable text · REACH-016 `llms.txt` absent (proactive only) |
| `render-extractability-audit` | ~16 | READ-001 main content absent from raw HTML · READ-004 key facts locked in images (pricing/menu/specs) · READ-011 content behind tabs/accordions not in DOM · READ-013 content behind consent wall (blocks bots *and* visitors) |
| `structured-data-audit` | ~14 | PARSE-004 missing required properties per `@type` · PARSE-006 no stable `@id` entity graph · **PARSE-007 structured data contradicts visible text** · PARSE-008 marked-up content not visible on page |
| `answerability-audit` | ~12 | **QUOTE-001 chunk fails standalone comprehension** (unresolved pronouns, orphaned numbers — "it starts at $29" is unusable when retrieved alone) · QUOTE-002 no explicit identity sentence · QUOTE-005 no answer-shaped pages (FAQ/comparison/pricing) · QUOTE-006 buyer-question coverage gap |
| `freshness-corroboration-audit` | ~15 | TRUST-003 dishonest sitemap `lastmod` · **TRUST-006 claim corroboration ledger** (which claims appear nowhere off-site) · TRUST-007 brand-name entity collision · TRUST-008 no disambiguating identity sentence · TRUST-009 missing identity anchors (Wikidata/LinkedIn/directories) |
| `engagement-audit` | ~16 | STAY-001 above-the-fold doesn't answer "am I in the right place" · **STAY-002 AI-referral landing mismatch** (page restarts the conversation instead of continuing it) · STAY-006 context loss (search discards query, filters reset on back) · STAY-008 CWV proxies from static analysis |

The four differentiators approved for v1 — chunk-level retrieval simulation, the purpose-split crawler access matrix + live UA probe, contradiction detection + corroboration ledger, and question-answerability + AI-referral landing quality — are all in the table above.

---

## Repository layout

```
<repo root>/
  brand-ai-readiness-audit/     <- THE SUBMISSION (only this gets zipped)
    marketplace.json
    README.md                   what each skill does, how the entrypoint composes them
    skills/                     8 folders
  bench/                        corpus.yaml, run.py, snapshots/ (gitignored), scoreboard/
  tests/                        fixtures/, golden/, test_*.py
  tools/                        validate.py, package.py, run_audit.py, install_local.py
  docs/                         ROLES.md, CONTRIBUTING.md, todo/<skill>.md
  research/                     Round-2 field notes, quadrant rationale
```

`tools/package.py` validates, then zips `brand-ai-readiness-audit/` alone.

Assumptions: `license: MIT` on every skill; `compatibility:` declared where network access is needed; `allowed-tools:` declared per skill.

---

## Test strategy (three layers)

**Layer 1 — local fixtures** (`tests/fixtures/`, hard assertions + golden reports). ~6 tiny hand-written HTML sites with deliberately injected defects, one per mechanism, plus **one clean site that must produce zero critical/high findings** — the false-positive tripwire. Fast, deterministic, runs on every change.

**Layer 2 — corpus replay** (`bench/`). 40 real sites, ≥10 per SEO×GEO quadrant, each labeled with an engagement tier:

```yaml
- url: https://example.com
  seo: good            # good | poor
  geo: poor            # good | poor   <- good-SEO/poor-GEO is the money quadrant
  engagement: moderate # high | moderate | low
  site_type: saas
  notes: "ranks #1 for its category but ships an empty app shell"
  smoke: true          # member of the pinned 8-site live dev subset
  expect_findings: [READ-001]
  expect_absent: [REACH-002]
```

Snapshot each site's evidence bundle once (gzipped, ≤8 pages/site, gitignored, `--refresh` to re-pull) and replay deterministically. Real-world messiness without the rot.

**Layer 3 — live bench** (`bench/run.py --live`). Runs the marketplace against live sites. Drift-tolerant scoreboard, not assertions. Two modes:

- **Dev loop (default): a fixed 8-site subset.** Marked `smoke: true` in `corpus.yaml` — **2 per SEO×GEO quadrant**, collectively covering all three engagement tiers. The set is pinned, not sampled, so runs stay comparable across days and across teammates. This is what anyone runs while iterating; ~8 sites × <5 min is a tolerable inner loop.
- **Full run (pre-submission): all 40.** `bench/run.py --live --all`. Rigorous quadrant coverage, run before packaging and after any change to the collector, severity model, or orchestrator merge logic.

**The money chart:** the good-SEO/poor-GEO quadrant must score *poorly* on discoverability — sites a conventional SEO linter would pass clean. That single result is the evidence that we built a GEO auditor and not an SEO checker.

---

## Build order

| # | Task | Owner | Output |
|---|---|---|---|
| 0 | Write this plan to `PLAN.md` at the project root as the team's shared reference | Aryan | Teammates read the same spec we do |
| 1 | Repo skeleton, `marketplace.json`, 8 SKILL.md frontmatter stubs, `tools/validate.py` | Aryan | `validate.py` green on empty skills |
| 2 | **Freeze contracts** — evidence-bundle, finding, report schemas + severity rubric | Aryan | Nothing else starts until this lands |
| 3 | **Author the full ~90-check registry** across the 6 analysis skills | Aryan | `checks.yaml` per skill; the parallelization key |
| 4 | `site-evidence-collector` complete — crawl, robots, UA probe, normalized extraction, budgets | Aryan | Real bundles on disk |
| 5 | `audit-orchestrator` complete — site-type detection, subskill registry, merge/dedupe/severity/FP-suppression, `report.json` + `report.md` | Aryan | End-to-end run with one analysis skill |
| 6 | `crawl-access-audit` complete — **the worked reference implementation** | Aryan | The pattern teammates copy |
| 7 | Fixture suite + golden reports + clean-site tripwire | partner | `pytest` green |
| 8 | `bench/` corpus (40 sites, 8 flagged `smoke`), runner, snapshot/replay, scoreboard | partner | Quadrant chart |
| 9 | TODO packets — 5 remaining skills, each with contract refs, exact check IDs, acceptance criteria, target fixture, and a paste-ready agent prompt | Aryan | `docs/todo/*.md` |
| 10 | Lakshay: `render-extractability` + `structured-data` · Mayank: `answerability` + `freshness-corroboration` + `engagement` | Teammates | — |

Tasks 1–6 and 9 are this scaffold. 7–8 can run in parallel once contracts (2) land.

---

## Verification

1. **Spec compliance** — `python tools/validate.py`: `marketplace.json` well-formed with exactly one entrypoint; every `SKILL.md` has valid frontmatter (`name` ≤64 chars, lowercase/hyphen only, matches folder; non-empty `description` ≤1024); every referenced path resolves; no duplicate check IDs; every check ID a SKILL.md cites exists in a registry. Optionally cross-check with `skills-ref validate ./skill-folder`.
2. **No forbidden imports** — grep the submission for non-stdlib imports; must be empty.
3. **Fixtures** — `python -m pytest tests/`. Defect fixtures produce their expected check IDs; **the clean fixture produces zero critical/high**.
4. **Determinism** — run the same fixture twice, `diff` the reports; must be byte-identical.
5. **Replay bench** — `python bench/run.py --replay`, review scoreboard for misses and FP candidates against `expect_findings` / `expect_absent`.
6. **Live bench** — `python bench/run.py --live` (pinned 8-site smoke subset, 2 per quadrant) during development; `--live --all` across all 40 before submission. Confirm every site completes under 5 minutes and the good-SEO/poor-GEO quadrant scores poorly on discoverability.
7. **Real agent end-to-end** — `python tools/install_local.py` to drop the skills into `.claude/skills/`, start a fresh Claude Code session, ask *"audit example.com"*, and confirm the **orchestrator alone** activates (not a sub-skill), dispatches the others, and emits a schema-valid `report.json` + readable `report.md`.
8. **Package** — `python tools/package.py`, confirm the zip contains only the marketplace root and is well under 50 MB.
