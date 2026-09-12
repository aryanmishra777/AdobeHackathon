---
name: structured-data-audit
description: >-
  PARSE stage of the brand-ai-readiness-audit marketplace. Analyzes a
  collected evidence bundle for structured-data problems that stop a machine
  turning prose into specific facts: absent or unparseable JSON-LD, wrong
  schema.org types for the page, missing required properties, an unlinked
  entity graph, absent sameAs identity links, markup that contradicts the
  visible page, markup describing content that is not there, and missing or
  conflicting titles and metadata. Emits candidate PARSE findings with
  evidence and severity. Invoked by audit-orchestrator as one stage of a
  full audit; it reads the evidence bundle and never fetches anything
  itself.
license: MIT
compatibility: >-
  Requires Python 3.9+ (standard library only). Reads a completed evidence
  bundle produced by site-evidence-collector. No network access needed or used.
allowed-tools: Bash Read Grep
metadata:
  marketplace: brand-ai-readiness-audit
  role: analysis
  mechanism: parse
  stage: "3"
  version: "0.1.0"
---

# Structured Data Audit (PARSE)

**The question this stage answers: Can a machine parse a specific fact out of the page?**

The third gate: the crawler got in and can read the text. Structured data is how a machine moves from *there is prose here* to *the price is GBP 29 and it is in stock*.

**PARSE-007 is the check that matters most here** — markup that contradicts the visible page. A source that disagrees with itself is worse than one with no markup at all, because a consumer that notices the conflict discounts the whole site rather than the single field.

## Inputs

A completed evidence bundle. This skill **never fetches anything** — all network
I/O belongs to `site-evidence-collector`. Everything below is a pure
function of the bundle, so the same bundle always produces the same findings.

| Artifact | Used for |
|---|---|
| `pages/*/extracted.json` -> `jsonld` (raw + parsed + parse_error) | PARSE-001..009 |
| `pages/*/extracted.json` -> `microdata`, `rdfa` | PARSE-001/009 |
| `pages/*/extracted.json` -> `text` | PARSE-007/008 conflict detection |
| `pages/*/extracted.json` -> `title`, `meta`, `headings` | PARSE-010/011 |
| `MANIFEST.json` -> `pages[].page_type` | PARSE-003/012/014 gating |

## Procedure

### 1. Run the deterministic checks

```bash
python scripts/check_structured_data.py <bundle-path> --out parse-candidates.json
```


### 2. Read the registry before trusting any candidate

`references/checks.yaml` holds all 14 checks. **The
`false_positive_guards` are binding, not advisory.** Re-read the guards for each
`check_id` before emitting, and drop any candidate whose guard condition holds.

Implement mechanically-evaluable guards in the script. Guards needing context
the script does not have are applied by you, here.

### 3. Gate every requirement by site profile

The canonical false positive in this whole marketplace is reporting missing `Product` markup on a site that sells nothing. Before asserting any property is required, check `site_profile.site_type` against the gating table in `../audit-orchestrator/references/site-profiles.md` and the per-type requirements in `references/fixes/schema-requirements.md`.

Two further traps:

- **Required versus recommended.** Reporting a merely recommended property as required inflates the finding count with work nobody needs to do.
- **Graph inheritance.** A property may be supplied through an `@id` reference to another entity. Resolve the graph before declaring anything missing.

Note that the collector stores each JSON-LD block's raw text alongside its parsed value, so *absent* and *present but malformed* stay distinguishable. They are different findings with different fixes.

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
`mechanism: "parse"` and `category: "discoverability"`. Return them to the
orchestrator; it assigns final ids, applies the scope and confidence modifiers,
and resolves supersession.

Do not apply the severity modifiers yourself — emit the base level from the
registry's `severity_rule`. Applying them twice inflates severities.

## Bundled resources

| Path | Purpose |
|---|---|
| `references/checks.yaml` | All 14 checks: severity rules, evidence templates, FP guards |
| `references/fixes/jsonld-templates.md` | Copy-pasteable JSON-LD per entity type |
| `references/fixes/schema-requirements.md` | Required vs recommended properties by type |
| `references/fixes/entity-graph.md` | @id, sameAs and a stable entity graph |
| `references/fixes/page-metadata.md` | Titles, descriptions, OpenGraph |
| `scripts/check_structured_data.py` | Deterministic PARSE checks, stdlib only |
