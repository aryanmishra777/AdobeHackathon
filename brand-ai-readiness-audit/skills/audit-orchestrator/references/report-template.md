# Human-readable report template

`report.json` is the contract; `report.md` is what a person actually reads.
Same content, ordered for a reader who has ten minutes and is not an expert.

Write for the person who has to get budget to fix this. Lead with the verdict,
not the methodology.

---

## Shape

```markdown
# AI-Readiness Audit — {site}

{verdict line from the scorecard}

| | Grade | Score |
|---|---|---|
| **Discoverability** — can AI assistants find, trust and cite you? | {A–F} | {n}/100 |
| **Engagement** — do visitors who arrive stay? | {A–F} | {n}/100 |

**{n} findings:** {c} critical · {h} high · {m} medium · {l} low
Audited {audited_at} · {pages_sampled} pages sampled{, coverage caveat if incomplete}

## Fix these first

1. **{action}** — {why_first} *(fixes {F-00x, F-00y}; effort: {S/M/L})*
2. …
3. …

## Findings

### Can assistants get in? (reach)
### Can they read the page? (read)
### Can they parse facts out? (parse)
### Can they quote a clear fact? (quote)
### Will they trust and repeat it? (trust)
### Do visitors who arrive stay? (stay)

<!-- omit any section with no findings; never print an empty heading -->

#### F-003 · {title}  `high`

**What we found.** {evidence}

**Why it matters.** {impact_rationale}

**Fix.** {summary}

1. {step}
2. {step}

```{lang}
{code}
```

**Check it yourself.** {verification}

*Scope: {n}/{m} pages · Confidence: {high/medium/low}*

## Worth doing anyway

<!-- proactive_recommendations: improvements where we found no defect -->

- **{title}** — {rationale} → {suggested_action.summary}

## What we checked, and what we didn't

<!-- coverage: pages sampled, skipped, limitations, checks_skipped -->
```

---

## Rules

- **Omit empty sections.** A heading with nothing under it reads as an error.
- **Group by mechanism, order by severity within each group.** The mechanism
  headings are phrased as questions because that is how a non-expert navigates.
- **Every finding shows its evidence before its fix.** The reader must be able
  to verify the problem is real before being asked to spend money on it.
- **Code blocks are tailored, not templated.** Use the site's real brand name,
  real URLs, real prices from the bundle. A snippet with `YOUR_COMPANY_NAME` in
  it will be pasted verbatim into production by someone.
- **State scope and confidence on every finding**, in small text at the end. A
  reader who disagrees needs to know we checked 12 pages, not the whole site.
- **Never pad.** If the site has three findings, the report is short. A short
  honest report beats a long one with filler, and padding is exactly what the
  false-positive gates exist to prevent.
- **The coverage section is not optional.** "What we didn't check" is what
  separates an audit from an assertion.
