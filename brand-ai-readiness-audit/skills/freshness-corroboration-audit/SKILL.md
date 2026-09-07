---
name: freshness-corroboration-audit
description: >-
  TRUST stage of the brand-ai-readiness-audit marketplace. Analyzes a
  collected evidence bundle for reasons a machine would discount or
  misattribute the facts it extracted: undated or stale content, sitemap
  lastmod dates that are not truthful, claims corroborated by no independent
  source, a brand name that collides with better-known entities with nothing
  to disambiguate it, missing identity anchors and profile links,
  inconsistent contact details, and unattributed factual claims. On-site
  freshness checks always run; off-site corroboration runs only when a
  search tool is available and is recorded as skipped otherwise. Invoked by
  audit-orchestrator as one stage of a full audit.
license: MIT
compatibility: >-
  Requires Python 3.9+ (standard library only). Reads a completed evidence
  bundle produced by site-evidence-collector. Off-site corroboration checks additionally require a web
  search or fetch tool, and are skipped and recorded when none is
  available.
allowed-tools: Bash Read Grep WebSearch WebFetch
metadata:
  marketplace: brand-ai-readiness-audit
  role: analysis
  mechanism: trust
  stage: "5"
  version: "0.1.0"
---

# Freshness Corroboration Audit (TRUST)

**The question this stage answers: Will a machine believe and repeat the fact?**

Two mechanisms from the Round-2 appendix sit behind this stage.

**Recency.** Consumers prefer content that is current and demonstrably so — and they discount signals that have been shown to be unreliable, which is why a dishonest `lastmod` is worse than no `lastmod`.

**Agreement.** A claim repeated consistently across independent sources is far more likely to be believed than one that lives in exactly one place. Its mirror is mistaken identity: when several things share a name, a system mixes them up unless something distinguishes them.

## Inputs

A completed evidence bundle. This skill **never fetches anything** — all network
I/O belongs to `site-evidence-collector`.  The one exception is the optional off-site
lookup described in step 3. Everything below is a pure
function of the bundle, so the same bundle always produces the same findings.

| Artifact | Used for |
|---|---|
| `pages/*/extracted.json` -> `dates` (with provenance) | TRUST-001/002/004/005 |
| `MANIFEST.json` -> `sitemaps[].entries[].lastmod` | TRUST-003 |
| `pages/*/extracted.json` -> `text` | TRUST-005/006/008/015 |
| `pages/*/extracted.json` -> `links`, `jsonld` | TRUST-010/011/014 |
| `external/` (optional) | TRUST-006/007/009/012/013 |

## Procedure

### 1. Run the deterministic checks

```bash
python scripts/check_trust.py <bundle-path> --out trust-candidates.json
```

> **Status: not yet implemented.** The check registry in
> `references/checks.yaml` is complete and frozen — all 15 checks are
> specified with severity rules, evidence templates and false-positive guards.
> `scripts/check_trust.py` is the remaining work. See
> `docs/todo/freshness-corroboration-audit.md` for the work packet, and use
> `../crawl-access-audit/scripts/check_access.py` as the reference
> implementation to copy structurally.

### 2. Read the registry before trusting any candidate

`references/checks.yaml` holds all 15 checks. **The
`false_positive_guards` are binding, not advisory.** Re-read the guards for each
`check_id` before emitting, and drop any candidate whose guard condition holds.

Implement mechanically-evaluable guards in the script. Guards needing context
the script does not have are applied by you, here.

### 3. Degrade honestly when there is no search tool

This is the only analysis skill with an optional off-site component.

**Always run:** TRUST-001..005, 008, 010 (on-site half), 011, 014, 015.

**Need a web search or fetch tool:** TRUST-006, 007, 009, 012, 013. When no such tool is available, or `skip_offsite` is set, **skip them and record each `check_id` in `coverage.checks_skipped`** with the reason.

Absence of a lookup is never evidence of absence. A report that says "we did not check corroboration" is honest; one that silently omits it reads as "we checked and it was fine", which is a lie by omission.

Two hard rules for the off-site checks:

- **Uncorroborated is not untrue.** Never imply a claim is false because no independent source repeats it. Conflating the two is defamatory.
- **Name collision is not the site's fault.** The finding is always the absence of disambiguation on the site, never the name. Never recommend rebranding, and never recommend soliciting reviews.

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
`mechanism: "trust"` and `category: "discoverability"`. Return them to the
orchestrator; it assigns final ids, applies the scope and confidence modifiers,
and resolves supersession.

Do not apply the severity modifiers yourself — emit the base level from the
registry's `severity_rule`. Applying them twice inflates severities.

## Bundled resources

| Path | Purpose |
|---|---|
| `references/checks.yaml` | All 15 checks: severity rules, evidence templates, FP guards |
| `references/fixes/freshness-signals.md` | Dates, lastmod honesty, update cadence |
| `references/fixes/corroboration.md` | Seeding facts where machines check |
| `references/fixes/entity-disambiguation.md` | Identity sentences, sameAs, anchors |
| `scripts/check_trust.py` | Deterministic TRUST checks, stdlib only |
