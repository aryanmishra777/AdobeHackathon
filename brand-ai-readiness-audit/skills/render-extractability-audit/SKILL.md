---
name: render-extractability-audit
description: >-
  READ stage of the brand-ai-readiness-audit marketplace. Analyzes a
  collected evidence bundle for content a machine cannot read even though a
  person can: main content assembled in the browser and absent from the HTML
  a crawler receives, facts locked in images, PDFs or video without
  transcripts, content behind tabs, consent walls or login gates, text
  rendered in canvas or text-less SVG, missing alt text, broken heading
  hierarchy and non-semantic markup. Emits candidate READ findings with
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
  mechanism: read
  stage: "2"
  version: "0.1.0"
---

# Render Extractability Audit (READ)

**The question this stage answers: Can a machine read what is on the page?**

The second gate in the chain: the crawler was let in, but does the response it received actually contain the facts a person sees on screen?

**READ-001 is the highest-value check in the marketplace.** A site whose content is assembled in the browser looks perfect to its owner and is empty to every crawler that does not execute JavaScript. It is also a root cause: it supersedes most PARSE and QUOTE findings on the same pages, because those are symptoms of it rather than independent defects.

## Inputs

A completed evidence bundle. This skill **never fetches anything** — all network
I/O belongs to `site-evidence-collector`. Everything below is a pure
function of the bundle, so the same bundle always produces the same findings.

| Artifact | Used for |
|---|---|
| `pages/*/extracted.json` -> `render_signals` | READ-001/002/011 |
| `pages/*/extracted.json` -> `text` | READ-001/003 |
| `pages/*/rendered.html` (when a renderer was available) | READ-001 ground truth |
| `pages/*/extracted.json` -> `images` | READ-004/008 |
| `pages/*/extracted.json` -> `iframes`, `noscript` | READ-006/007 |
| `pages/*/raw.html` | READ-010/011/013/015 |

## Procedure

### 1. Run the deterministic checks

```bash
python scripts/check_render.py <bundle-path> --out read-candidates.json
```

> **Status: not yet implemented.** The check registry in
> `references/checks.yaml` is complete and frozen — all 16 checks are
> specified with severity rules, evidence templates and false-positive guards.
> `scripts/check_render.py` is the remaining work. See
> `docs/todo/render-extractability-audit.md` for the work packet, and use
> `../crawl-access-audit/scripts/check_access.py` as the reference
> implementation to copy structurally.

### 2. Read the registry before trusting any candidate

`references/checks.yaml` holds all 16 checks. **The
`false_positive_guards` are binding, not advisory.** Re-read the guards for each
`check_id` before emitting, and drop any candidate whose guard condition holds.

Implement mechanically-evaluable guards in the script. Guards needing context
the script does not have are applied by you, here.

### 3. Inference versus measurement

When `run.renderer.available` is `true`, `rendered.html` is ground truth and a raw-versus-rendered delta is a measurement. Report it as such.

When no renderer was available — the common case, and the one a grader's machine will hit — READ-001 is an **inference** from raw-HTML signals. In that case:

- cap `confidence` at `medium`
- say in the evidence that the gap was inferred, not measured
- add a note to `coverage.limitations`

Never require the combination of signals to be present and then report as if you had rendered the page. The signals must co-occur before firing: an empty mount point or framework marker, **and** low `main_word_count`, **and** either a hydration payload or a very low text-to-markup ratio. A framework marker alone proves nothing — a Next.js page with 1200 words of server-rendered text is completely fine.

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
`mechanism: "read"` and `category: "discoverability"`. Return them to the
orchestrator; it assigns final ids, applies the scope and confidence modifiers,
and resolves supersession.

Do not apply the severity modifiers yourself — emit the base level from the
registry's `severity_rule`. Applying them twice inflates severities.

## Bundled resources

| Path | Purpose |
|---|---|
| `references/checks.yaml` | All 16 checks: severity rules, evidence templates, FP guards |
| `references/fixes/js-rendering.md` | Server-side rendering, prerendering, hydration |
| `references/fixes/non-text-content.md` | Images, PDFs, video, canvas and SVG |
| `references/fixes/semantic-html.md` | Headings, landmarks, alt text, encoding |
| `references/fixes/consent-walls.md` | Consent gates and login walls |
| `scripts/check_render.py` | Deterministic READ checks, stdlib only |
