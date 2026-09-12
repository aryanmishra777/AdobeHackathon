# Round 3 — Brand AI-Readiness Audit Marketplace

> **Status: the base repository is built.** Contracts frozen, collector,
> orchestrator and the reference implementation complete, 91 checks specified,
> 57 tests passing, corpus measured. What remains is five check scripts, tracked
> in [`TODO.md`](TODO.md) and detailed in `docs/todo/`. Sections below are kept
> as written where they are still the spec, and marked **DONE** where they
> describe work that has landed.

## Context

Adobe University Hackathon 2026, Round 3 (`6a8ffdf33590a_round3-handout-updated.pdf`). We must ship an **Agent Skill Marketplace** — a `marketplace.json` manifest plus N agentskills.io-compliant skill folders with exactly one entrypoint — that, pointed at any unseen website, audits it for **AI discoverability** (why assistants don't find/cite the brand) and **on-site engagement** (why arriving visitors don't stay), then emits one structured report of findings + prioritized suggested actions. Recommend-only, robots-respecting, <5 min per site, ≤50 MB zip.

Grading is on **the marketplace itself**, not any report it produces: detection accuracy (evidence-backed, few false positives), fix quality (mechanism-sound, specific), composition quality (real separation of concerns, not padding), proactive recommendations, and generalization to unseen sites.

**This plan builds the base repository, not the finished submission.** Aryan does R&D, contracts, and unblocking; Lakshay and Mayank do the implementation against frozen contracts and detailed TODO packets (written as paste-ready prompts for Copilot / Antigravity / Claude Code). So the priority order was: **freeze the contracts → build one worked vertical slice → generate the work packets.** All three are done.

### Environment constraints (verified on this machine)

Python 3.14, **no node/npm**, and of the relevant packages only `lxml` is installed — no `requests`, `bs4`, `playwright`. A grader's machine will look like this.

**The stdlib boundary applies to the submission only.** Everything under `brand-ai-readiness-audit/scripts/` is stdlib-only Python (`urllib.request`, `html.parser`, `json`, `re`, `xml.etree`, `gzip`, `concurrent.futures`) — zero third-party imports inside the zip, enforced by `tools/validate.py`. A check that always runs beats a stronger check that can't.

Dev tooling outside the zip (`tools/`, `bench/`, `tests/`) may take dependencies; see `tools/requirements-dev.txt`. The handout places no format restriction on `references/` or `scripts/` ("any structure is fine as long as the rules below hold"), so **check registries are YAML** — they are read by the agent and by humans, both of which handle YAML natively, and comments plus multi-line severity rules matter when hand-authoring 107 entries. No submission script ever parses YAML: scripts take signals in and emit JSON out.

---

## Architecture — **DONE**

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

## Contracts — **FROZEN.** Do not change these without telling Lakshay and Mayank

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

## Severity, determinism, and false-positive control — **DONE**

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

## Checks — **DONE as specification, 13 of 91 implemented**

All 91 are fully specified in the six `checks.yaml` registries, plus 16
`proactive` entries (`*-P01…`) for recommendations where no defect was found —
107 registry entries in total. `crawl-access-audit` implements 13 of its 18; the
other five skills are scripts-pending. Counts below are exact, not estimates.

| Skill | Checks · owner | Representative / novel checks |
|---|---|---|
| `crawl-access-audit` | 18 · 13 done | REACH-002 AI retrieval agents disallowed · REACH-003 training-crawler blocks (informational, **not** a defect) · REACH-005 CDN 403s bot UAs despite robots allow · REACH-009 `nosnippet`/`max-snippet:0` suppressing quotable text · REACH-016 `llms.txt` absent (proactive only) |
| `render-extractability-audit` | 16 · Lakshay | READ-001 main content absent from raw HTML · READ-004 key facts locked in images (pricing/menu/specs) · READ-011 content behind tabs/accordions not in DOM · READ-013 content behind consent wall (blocks bots *and* visitors) |
| `structured-data-audit` | 14 · Lakshay | PARSE-004 missing required properties per `@type` · PARSE-006 no stable `@id` entity graph · **PARSE-007 structured data contradicts visible text** · PARSE-008 marked-up content not visible on page |
| `answerability-audit` | 12 · Mayank | **QUOTE-001 chunk fails standalone comprehension** (unresolved pronouns, orphaned numbers — "it starts at $29" is unusable when retrieved alone) · QUOTE-002 no explicit identity sentence · QUOTE-005 no answer-shaped pages (FAQ/comparison/pricing) · QUOTE-006 buyer-question coverage gap |
| `freshness-corroboration-audit` | 15 · Mayank | TRUST-003 dishonest sitemap `lastmod` · **TRUST-006 claim corroboration ledger** (which claims appear nowhere off-site) · TRUST-007 brand-name entity collision · TRUST-008 no disambiguating identity sentence · TRUST-009 missing identity anchors (Wikidata/LinkedIn/directories) |
| `engagement-audit` | 16 · Mayank | STAY-001 above-the-fold doesn't answer "am I in the right place" · **STAY-002 AI-referral landing mismatch** (page restarts the conversation instead of continuing it) · STAY-006 context loss (search discards query, filters reset on back) · STAY-008 CWV proxies from static analysis |

The four differentiators approved for v1 — chunk-level retrieval simulation, the purpose-split crawler access matrix + live UA probe, contradiction detection + corroboration ledger, and question-answerability + AI-referral landing quality — are all in the table above.

---

## Repository layout — **DONE**

```
<repo root>/
  README.md                     landing page: repo map, the 8 skills, status table
  TODO.md                       who builds what, in what order; index into docs/todo/
  PLAN.md                       this file
  brand-ai-readiness-audit/     <- THE SUBMISSION (only this gets zipped)
    marketplace.json
    README.md                   what each skill does, how the entrypoint composes them
    skills/                     8 folders
  bench/                        candidates.yaml, corpus.yaml, build_corpus.py, run.py,
                                snapshots/ (gitignored, ~179 MB), scoreboard/
  tests/                        fixtures/, golden/, bundles/ (gitignored),
                                make_fixtures.py, make_bundles.py, test_marketplace.py
  tools/                        validate.py, package.py, install_local.py,
                                requirements-dev.txt
  docs/                         ROLES.md, CONTRIBUTING.md, todo/<skill>.md
  research/                     Round-2 field notes, quadrant rationale (empty so far)
```

Pushed to `github.com/aryanmishra777/AdobeHackathon`. `bench/snapshots/`,
`tests/bundles/` and `dist/` are gitignored — all three are regenerable, and
snapshots alone are larger than everything tracked put together.

`bench/build_corpus.py` is the piece this plan did not originally anticipate:
corpus labels are **measured by crawling each candidate**, never asserted by
hand. That is what makes the quadrant chart evidence instead of an opinion.

`tools/package.py` validates, then zips `brand-ai-readiness-audit/` alone.

Assumptions: `license: MIT` on every skill; `compatibility:` declared where network access is needed; `allowed-tools:` declared per skill.

---

## Test strategy (three layers) — **DONE**

**Layer 1 — local fixtures** — **DONE.** (`tests/fixtures/`, hard assertions + golden reports.) **7** tiny hand-written HTML sites: six with deliberately injected defects, one per mechanism (`js-shell`, `blocked-crawlers`, `contradictory-markup`, `stale-content`, `unquotable-chunks`, `low-engagement`), plus **`clean`, which must produce zero critical and zero high findings** — the false-positive tripwire. Each is served on its own port and crawled by the real collector, so the bundles under test are the same shape as a live run. 57 assertions in `tests/test_marketplace.py`, all passing.

**Layer 2 — corpus replay** — **DONE, and bigger than planned.** (`bench/`.) The original target was 40 hand-labelled sites. What shipped is **85 candidates in `candidates.yaml`, crawled by `build_corpus.py` into 64 measured entries in `corpus.yaml`**, every quadrant at or above the 10-site requirement:

```
                        n    disc
SEO good / GEO good    24     66
SEO good / GEO poor    14     51   <- the money quadrant
SEO poor / GEO good    17     57
SEO poor / GEO poor     9     44
```

The change that matters: **both axes are measured, never asserted.** GEO comes from the blocking mechanism actually observed (robots disallow, edge 403/429/challenge, soft-block serving crawlers a stripped page, content absent from raw HTML, no structured data, passages failing standalone comprehension); SEO from technical hygiene (sitemap, canonicals, titles, descriptions, h1, internal linking). Hand-editing a label makes it stop being evidence. Entries carry the score and the derivation:

```yaml
  - url: https://asana.com
    seo: good
    geo: good
    engagement: moderate
    site_type: saas
    vertical: productivity
    smoke: true          # member of the pinned 8-site live dev subset
    geo_score: 70
    seo_score: 80
    measurement: measured        # measured | crawler-refused | inconclusive
    notes: 'Measured 2026-09-06 from a 5-page crawl (GEO score 70/100).
      Mechanisms found: median 59 words of body text in raw HTML across 5
      pages with an app-shell mount on 5.'
    expect_findings: [READ-001]
    expect_absent: [REACH-005]
```

**Ten further sites are recorded as `inconclusive` and excluded from the chart**, with the reason written into `corpus.yaml` as a comment. They refused our *browser* probe too, so we cannot separate a site-level block from our own address being filtered. Claiming a defect there would be exactly the confident false positive the rubric punishes. Retry them from a different network before drawing a conclusion.

Snapshot each site's evidence bundle once (gzipped, ≤8 pages/site, gitignored, `--refresh` to re-pull) and replay deterministically. Real-world messiness without the rot.

**Live sites drift, and corpus entries are therefore smoke signals, not assertions.** Between two runs a day apart, `apnews.com` began blocking retrieval crawlers and `gymshark.com` went from 1 word of body text to 1743. Hard assertions live in Layer 1, against fixtures that cannot move.

**Layer 3 — live bench** (`bench/run.py --live`). Runs the marketplace against live sites. Drift-tolerant scoreboard, not assertions. Two modes:

- **Dev loop (default): a fixed 8-site subset.** Marked `smoke: true` in `corpus.yaml` — **2 per SEO×GEO quadrant**, collectively covering all three engagement tiers. The set is pinned, not sampled, so runs stay comparable across days and across teammates. This is what anyone runs while iterating; ~8 sites × <5 min is a tolerable inner loop.
- **Full run (pre-submission): the whole corpus.** `bench/run.py --replay` — 64 sites. Rigorous quadrant coverage, run before packaging and after any change to the collector, severity model, or orchestrator merge logic. The runner scores misses and false positives **only for skills that are actually implemented**; checks belonging to a scaffold skill are reported separately as "not yet checked" rather than counted against us.

**The money chart:** the good-SEO/poor-GEO quadrant must score *poorly* on discoverability — sites a conventional SEO linter would pass clean. That single result is the evidence that we built a GEO auditor and not an SEO checker.

---

## Build order — **tasks 0-9 complete**

| # | Task | Owner | Output | State |
|---|---|---|---|---|
| 0 | Write this plan to `PLAN.md` at the project root as the team's shared reference | Aryan | Teammates read the same spec we do | done |
| 1 | Repo skeleton, `marketplace.json`, 8 SKILL.md frontmatter stubs, `tools/validate.py` | Aryan | `validate.py` green on empty skills | done |
| 2 | **Freeze contracts** — evidence-bundle, finding, report schemas + severity rubric | Aryan | Nothing else starts until this lands | done |
| 3 | **Author the full check registry** across the 6 analysis skills | Aryan | 91 checks + 16 proactive entries; the parallelization key | done |
| 4 | `site-evidence-collector` complete — crawl, robots, UA probe, normalized extraction, budgets | Aryan | Real bundles on disk | done |
| 5 | `audit-orchestrator` complete — site-type detection, subskill registry, merge/dedupe/severity/FP-suppression, `report.json` + `report.md` | Aryan | End-to-end run with one analysis skill | done |
| 6 | `crawl-access-audit` — **the worked reference implementation** | Aryan | The pattern teammates copy; 13 of 18 checks | done |
| 7 | Fixture suite + golden reports + clean-site tripwire | Aryan | 7 fixtures, 57 assertions, `pytest` green | done |
| 8 | `bench/` corpus, runner, snapshot/replay, scoreboard | Aryan | 85 candidates → 64 measured entries; quadrant chart PASS (16-point gap) | done |
| 9 | TODO packets — 5 remaining skills, each with contract refs, exact check IDs, acceptance criteria, target fixture, and a paste-ready agent prompt | Aryan | `docs/todo/*.md` + `TODO.md` index | done |
| 10 | Lakshay: `render-extractability` + `structured-data` · Mayank: `answerability` + `freshness-corroboration` + `engagement` | Teammates | 5 check scripts + their fix templates | **open** |

Tasks 0-9 were the scaffold and are finished. Task 10 is three parallel tracks
with nothing blocking anything, because the contracts are frozen.

### What changed from the original plan

Worth recording, because each was a correction forced by evidence rather than a
change of mind:

- **Task 7 and 8 were planned for a partner and done by Aryan.** No impact
  beyond who typed them.
- **The corpus grew from 40 hand-labelled sites to 76 crawled candidates**, and
  labels became measurements. See Layer 2 above.
- **Sample diversity needed fixing.** Lexicographic BFS is deterministic but
  samples one directory deeply — a live crawl of `python.org` put all 8 pages
  under `/about/`. `Collector._diversify()` now ranks frontier candidates by how
  many pages their section has already contributed, so sections are visited
  round-robin.
- **Severity gates needed two exemptions.** Site-level findings (no sitemap, no
  `llms.txt`) have no `pages_affected`, so the sample-size gate was demoting
  them; they now carry a site-level artifact exemption. And site-wide scope
  escalation was inflating them a level, including one check whose registry
  guard explicitly forbids escalation — hence `severity_locked` on the finding
  schema.
- **Soft-blocking turned out to matter more than hard refusal.** `khanacademy.org`
  serves 227 KB to a browser and to `ChatGPT-User`, but **3 KB to `GPTBot`,
  `ClaudeBot`, `PerplexityBot` and `Googlebot`**. Counting only 401/403/429/
  challenge would have missed it. The corpus labeller now flags a `degraded`
  response at under 50% of the browser baseline.
- **Sites that refuse our crawler are the most valuable data, not garbage.**
  Eleven were nearly discarded as unusable before the `outcome` classification
  split them into `measured` / `crawler-refused` / `inconclusive` / `unusable`.

---

## Verification

Every step below is wired and currently green, except #7, which needs a human in
a fresh agent session.

1. **Spec compliance** — `python tools/validate.py`: `marketplace.json` well-formed with exactly one entrypoint; every `SKILL.md` has valid frontmatter (`name` ≤64 chars, lowercase/hyphen only, matches folder; non-empty `description` ≤1024); every referenced path resolves; no duplicate check IDs; every check ID a SKILL.md cites exists in a registry. It distinguishes an **error** from a **TODO**, so a scaffold skill reports as outstanding work rather than as a failure. → `PASS (23 TODOs outstanding)`; the 23 are task 10.
2. **No forbidden imports** — `tools/validate.py` walks the AST of every shipped script against an allowed-stdlib set, rather than grepping. → clean.
3. **Fixtures** — `python -m pytest tests/ -q`. Defect fixtures produce their expected check IDs; **the clean fixture produces zero critical/high**. → `57 passed`.
4. **Determinism** — run the same fixture twice, `diff` the reports; must be byte-identical. Asserted in `test_analysis_is_deterministic`.
5. **Replay bench** — `python bench/run.py --replay`, review scoreboard for misses and FP candidates against `expect_findings` / `expect_absent`.
6. **Live bench** — `python bench/run.py --live` (pinned 8-site smoke subset, 2 per quadrant) during development; `--replay` across the full 64 before submission. Confirm every site completes under 5 minutes and the good-SEO/poor-GEO quadrant scores poorly on discoverability. → latest full run: **64/64 audited, 0 false positives, 0 misses**, slowest site 118s, money quadrant 16 points below the control.
7. **Real agent end-to-end** — `python tools/install_local.py` to drop the skills into `.claude/skills/`, start a fresh Claude Code session, ask *"audit example.com"*, and confirm the **orchestrator alone** activates (not a sub-skill), dispatches the others, and emits a schema-valid `report.json` + readable `report.md`. **Re-run this after task 10 lands** — activation hygiene is the one property no script can check.
8. **Package** — `python tools/package.py`, confirm the zip contains only the marketplace root and is well under 50 MB. → `39 files, 0.14 MB, manifest matches. OK: ready to submit.`

### The one result that matters

The good-SEO/poor-GEO quadrant scores **51** against the control's **66**. Those
fourteen sites are ones a conventional SEO linter passes clean — perfect sitemaps
and canonicals while the edge returns 429 to `ClaudeBot` or robots.txt disallows
the retrieval crawlers outright. That gap is the evidence
that this is a GEO auditor and not an SEO checker, and it is the single number to
re-check after any change to the collector or the severity model.
