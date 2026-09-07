---
name: crawl-access-audit
description: >-
  REACH stage of the brand-ai-readiness-audit marketplace. Analyzes a collected
  evidence bundle for the reasons a machine cannot get into a site at all:
  robots.txt resolved per AI crawler with the retrieval-versus-training
  distinction, CDN and WAF blocking of bot user-agents regardless of robots.txt,
  missing or invalid sitemaps, noindex and nosnippet directives that suppress
  indexing or quoting, canonical and redirect errors, duplicate origins, broken
  internal links, orphaned pages, TLS problems and crawl-rate limits. Emits
  candidate REACH findings with evidence and severity. Invoked by
  audit-orchestrator as one stage of a full audit; it reads the evidence bundle
  and never fetches anything itself.
license: MIT
compatibility: >-
  Requires Python 3.9+ (standard library only). Reads a completed evidence
  bundle produced by site-evidence-collector. No network access needed or used.
allowed-tools: Bash Read Grep
metadata:
  marketplace: brand-ai-readiness-audit
  role: analysis
  mechanism: reach
  stage: "1"
  version: "0.1.0"
---

# Crawl & Access Audit (REACH)

**The question this stage answers: can a machine get in at all?**

This is the first gate in the chain from the Round-2 appendix — the crawler has
to be let in, then be able to read the page, then be able to pick out a fact. A
failure here makes every later stage moot, which is why REACH findings supersede
their downstream symptoms rather than sitting alongside them.

## Inputs

A completed evidence bundle. This skill **never fetches anything** — all network
I/O belongs to `site-evidence-collector`. Everything below is a pure function of
the bundle, so the same bundle always produces the same findings.

| Artifact | Used for |
|---|---|
| `MANIFEST.json` → `robots.agent_matrix` | REACH-002/003/004 |
| `robots.txt.raw`, `robots_fetch.json` | REACH-001 |
| `ua_probe.json` | REACH-005 |
| `MANIFEST.json` → `sitemaps` | REACH-006/007/013 |
| `MANIFEST.json` → `run.origin_variants` | REACH-011/014 |
| `pages/*/extracted.json`, `pages/*/response.headers.json` | REACH-008/009/010/018 |
| `pages/*/request.json` | REACH-012/015 |

## Procedure

### 1. Run the deterministic checks

```bash
python scripts/check_access.py <bundle-path> --out reach-candidates.json
```

Every REACH check is deterministic — reachability is measurable, so there is no
reason for a model to guess at it. The script emits candidate findings against
`../audit-orchestrator/references/finding.schema.json`.

### 2. Read the registry before trusting any candidate

`references/checks.yaml` holds all 18 checks with their severity rules and
`false_positive_guards`. **The guards are binding.** Re-read the guards for each
`check_id` the script emitted and drop any candidate whose guard condition holds.

The script implements the guards it can evaluate mechanically. Several require
context it does not have — whether a host is a staging environment, whether a
cross-domain canonical is intentional syndication, whether a page is paywalled.
Those are yours to apply.

### 3. Apply the retrieval-versus-training distinction

This is the most important judgment in this skill, and the one most audit tools
get wrong.

| Agent purpose | Blocked means | Report as |
|---|---|---|
| `retrieval` (`ChatGPT-User`, `Claude-User`, `Perplexity-User`) | The brand cannot appear in answers to questions asked right now | **REACH-002 — a genuine defect** |
| `search-index` (`OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`, `Googlebot`, `Bingbot`) | Removed from the pool assistants draw sources from | **REACH-002 / REACH-004 — a defect** |
| `training` (`GPTBot`, `Google-Extended`, `CCBot`, `Applebot-Extended`, `meta-externalagent`) | Content will not train future models. **No effect on today's answers.** | **REACH-003 — informational, `low`, never framed as an error** |

Two errors to never make:

- Telling a publisher their deliberate `GPTBot` block is a bug. Many organisations
  block training crawlers after legal review. Calling that a `critical` defect
  discredits every other finding in the report.
- Claiming `Google-Extended` affects Google Search or AI Overviews ranking. It
  does not — it is a Gemini training opt-out only.

### 4. Check what robots.txt cannot tell you

A permissive `robots.txt` does not mean a crawler can actually fetch. CDNs and
WAFs routinely serve `403`, a CAPTCHA, or a JS challenge to any non-browser
user-agent. This is invisible to every tool that only parses `robots.txt`, and it
is common.

`ua_probe.json` is the evidence. A `200` that returns a challenge page is a block
in every way that matters — trust `challenge_detected`, not the status code.

### 5. Write the findings

Each candidate needs, beyond what the script fills in:

- **`evidence`** quantified and specific. Not "robots.txt blocks AI crawlers" but
  "robots.txt disallows `ChatGPT-User` and `Claude-User` from `/`, so neither can
  fetch any page when a user asks about the brand."
- **`suggested_action.code`** tailored to this site. Use the site's real paths and
  the agent tokens actually blocked. A snippet containing `YOUR_DOMAIN` will be
  pasted into production verbatim by someone.
- **`verification`** as one command the reader can run. `references/checks.yaml`
  gives the template per check.

Use the fix templates in `references/fixes/` as a starting point, then edit them
against the bundle. They are starting points, not output.

### 6. Add proactive recommendations

From the `proactive` block of `references/checks.yaml`. Note especially that
**REACH-016 (`llms.txt`) must never be emitted as a finding** — it is an emerging
convention with no guaranteed consumer, so it belongs in
`proactive_recommendations` framed as forward-looking.

## Output

A JSON array of candidate findings, each conforming to the shared finding
schema, with `mechanism: "reach"` and `category: "discoverability"`. Return them
to the orchestrator; it assigns final ids, applies scope and confidence
modifiers, and resolves supersession against later stages.

Do not compute final severity yourself beyond the base level in the registry's
`severity_rule` — the orchestrator owns the modifiers, and applying them twice
produces inflated severities.

## Bundled resources

| Path | Purpose |
|---|---|
| `references/checks.yaml` | All 18 checks: severity rules, evidence templates, FP guards |
| `references/fixes/robots-ai-agents.md` | robots.txt stanzas for AI crawler access |
| `references/fixes/cdn-bot-blocking.md` | Unblocking bots at Cloudflare / Akamai / AWS WAF |
| `references/fixes/sitemap.md` | Sitemap structure and declaration |
| `references/fixes/indexability.md` | noindex, nosnippet, X-Robots-Tag, hreflang |
| `references/fixes/canonical-redirects.md` | Canonicals, origin consolidation, TLS |
| `references/fixes/broken-links.md` | Broken internal links |
| `references/fixes/performance.md` | Crawl-rate and TTFB |
| `scripts/check_access.py` | All deterministic REACH checks, stdlib only |
