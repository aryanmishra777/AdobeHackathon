---
name: site-evidence-collector
description: >-
  Acquisition stage of the brand-ai-readiness-audit marketplace. Performs one
  polite, robots-respecting, budget-bounded read-only crawl of a website and
  writes a normalized evidence bundle to disk: robots.txt and its resolved
  per-AI-agent access matrix, sitemaps, a bot-versus-browser user-agent probe,
  and for each sampled page the raw HTML, response headers, redirect chain, a
  normalized page model, and retrieval-style content chunks. Invoked by
  audit-orchestrator before any analysis skill runs. This is the only skill in
  the marketplace permitted to touch the network; every analysis skill reads the
  bundle it produces and never re-fetches. Extracts what is on the page and
  never judges what it means.
license: MIT
compatibility: >-
  Requires Python 3.9+ (standard library only) and outbound HTTPS access to the
  audited site. No browser or rendering engine is required; when the host agent
  provides one, pass --renderer to capture rendered HTML alongside raw HTML.
allowed-tools: Bash Read Write
metadata:
  marketplace: brand-ai-readiness-audit
  role: collector
  stage: "0"
  version: "0.1.0"
---

# Site Evidence Collector

Acquisition for the `brand-ai-readiness-audit` marketplace. One crawl, one
bundle, six analyses.

## Why this is a separate skill

Two reasons, both structural:

- **Politeness and determinism.** If six analysis skills each fetched what they
  needed, the audited site would take six times the load and every skill could
  observe a different version of the page. One crawl means one consistent
  snapshot and one place where every rate limit, timeout and `robots.txt` rule
  is enforced and auditable.
- **Separation of observation from judgment.** This skill records *what is on
  the page*. It never decides what that means. `render_signals` reports that
  `#root` is empty and that a 400 KB hydration payload is present; whether that
  constitutes a defect is `render-extractability-audit`'s call. Keeping the two
  apart is what makes the analysis skills pure functions over a fixed input, and
  therefore testable against fixtures.

## Guardrails

These are hard constraints, not defaults:

- **Read-only.** `GET` and `HEAD` only. Never `POST`, never submit a form, never
  follow a logout or delete link, never authenticate.
- **Respect `robots.txt`** for our own crawl, using the same resolution rules
  described in `references/ai-user-agents.md`. Skipped URLs are recorded in
  `coverage.skipped` with reason `robots-disallow`, never silently dropped.
- **One documented exception:** the user-agent probe re-fetches a *single URL
  that robots.txt already allows* under several agent strings. It requests no
  new resource and adds at most a handful of requests.
- **Budgets are ceilings.** 25 pages, 8 concurrent, 10 s per request, 120 s
  total fetch, 3 MB per page, 0.5 s politeness delay. Never raise concurrency
  above 8. Honour `Crawl-delay` when it exceeds our own delay.
- **Stay on-origin.** Never crawl a different registrable domain. Subdomains are
  out of scope unless explicitly passed.
- **Never crawl obvious non-content:** `/cart`, `/checkout`, `/account`,
  `/login`, `/logout`, `/admin`, `/wp-admin`, `?add-to-cart=`, calendar and
  faceted-filter URL patterns.

## Inputs

| Argument | Default | Meaning |
|---|---|---|
| `target` | required | URL or bare domain |
| `--out` | `.audit/<domain>/<run-id>` | Bundle root |
| `--max-pages` | 25 | Page ceiling |
| `--timeout` | 10 | Per-request seconds |
| `--budget` | 120 | Total fetch seconds |
| `--concurrency` | 8 | Max parallel requests (hard cap 8) |
| `--delay` | 0.5 | Politeness delay in seconds |
| `--include` / `--exclude` | none | Path prefix filters |
| `--renderer` | none | Command receiving a URL and printing rendered HTML |
| `--no-probe` | off | Skip the user-agent probe |

## Procedure

Run the bundled script; it performs all of the below deterministically.

```bash
python scripts/collect.py https://example.com --out .audit/example.com/run-01
```

1. **Resolve the origin.** Try all four scheme/host forms, record status and
   redirect target for each in `run.origin_variants`, and adopt the form the
   site itself redirects to. A site answering on all four without redirecting is
   recorded as-is; `crawl-access-audit` decides whether that is a defect.

2. **Fetch `robots.txt` and `llms.txt`.** Preserve `robots.txt` verbatim in
   `robots.txt.raw`. Parse into groups, then resolve the full `agent_matrix` for
   every token in `references/ai-user-agents.md`, tagging each with its
   `purpose`. Record parse errors rather than silently tolerating them.

3. **Fetch sitemaps.** From `robots.txt` declarations plus `/sitemap.xml`.
   Follow one level of sitemap-index nesting. Preserve `lastmod` verbatim —
   `TRUST-003` needs to test whether the claim is honest, which is impossible if
   the value has been normalized.

4. **Select pages deterministically.** Home page first, then sitemap entries in
   file order, then breadth-first from the home page with URLs sorted
   lexicographically, until the budget is reached. No randomness, no
   time-dependent ordering: the same site yields the same sample.

5. **Fetch pages** with bounded concurrency and the politeness delay. Record the
   full redirect chain, headers, timings and transfer size.

6. **Extract the normalized page model** (`extracted.json`) — parse each page
   exactly once. Title, meta, canonical, hreflang, headings in document order,
   link graph, image inventory (distinguishing an absent `alt` attribute from an
   explicit empty one), script inventory, verbatim JSON-LD blocks with their
   parse status, main-text extraction, word counts, text-to-markup ratio,
   `<noscript>` content, render signals, forms, and every date found with its
   provenance.

7. **Chunk each page** (`chunks.json`) the way a retrieval pipeline would: on
   heading boundaries, ~320 words target. Attach the deterministic signals
   `answerability-audit` needs — whether the chunk names its subject, opens with
   an unresolved pronoun, contains bare numbers, uses deictic terms like "above"
   or "the following". The script counts; the model judges.

8. **Run the user-agent probe.** One already-allowed URL, fetched with a browser
   UA as baseline and with each bot token. Compare status, byte size and
   challenge signatures.

9. **Write `MANIFEST.json`** and `coverage.json`, including `stopped_reason` and
   every skipped URL with its reason.

## Output

A bundle conforming to `references/evidence-bundle.schema.json`:

```
.audit/<domain>/<run-id>/
  MANIFEST.json  run.json  robots.txt.raw  robots_fetch.json
  sitemaps/*.xml  ua_probe.json  coverage.json
  pages/<page-id>/
    request.json  response.headers.json  raw.html
    rendered.html   (only when --renderer was supplied)
    extracted.json  chunks.json
```

Verify before handing off:

```bash
python scripts/validate_bundle.py .audit/example.com/run-01
```

## Failure modes

Report these in `coverage.stopped_reason`; none of them is an audit error, and
several are the most severe possible finding:

| Situation | Behaviour |
|---|---|
| DNS failure, connection refused | Write a bundle containing only `run.json` and `coverage.json` with `stopped_reason: dns-failure`. The orchestrator reports it as a `critical` finding. |
| `robots.txt` disallows everything for our UA | Fetch nothing beyond `robots.txt`; `stopped_reason: site-blocked`. Still run the probe. This is a finding, not a failure. |
| Every page 403s | Record statuses and challenge signatures. The probe is the evidence. |
| Time budget exhausted | Stop cleanly, `complete: false`, keep what was collected. |
| Non-HTML content type | Skip with reason `non-html`; record the type. |
| Page exceeds 3 MB | Truncate, record actual size, flag in the page record. |

Never abort the whole run because one page failed. A partial bundle honestly
labelled is far more useful than no bundle.

## Bundled resources

| Path | Purpose |
|---|---|
| `references/evidence-bundle.schema.json` | The frozen bundle contract |
| `references/ai-user-agents.md` | Agent tokens, purpose taxonomy, robots resolution rules |
| `scripts/collect.py` | The crawler and extractor, stdlib only |
| `scripts/validate_bundle.py` | Bundle conformance check |
