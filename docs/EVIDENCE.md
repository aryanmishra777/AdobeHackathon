# What the evidence supports, and what it does not

Every threshold in this marketplace should be traceable to a measurement or
labelled as a judgment call. This file is that ledger. It exists so that a
finding can answer the question *"why is that the number?"* with something
better than "it seemed right".

Sources are the GEO literature collected in the team's NotebookLM knowledge base
and the PDFs under `7th Sem/SEO/GEO/`.

**Every figure on this page has now been checked against the source PDF text**
(10 September 2026). Where a paper is quoting someone else rather than reporting
its own measurement, that is stated — the distinction decides how strongly we may
phrase a finding.

Primary sources, by arXiv/SSRN id:

| id | Paper |
|---|---|
| `2311.09735` | Aggarwal et al., *GEO: Generative Engine Optimization* |
| `2603.29979` | Yu et al., *Structural Feature Engineering for GEO* (GEO-SFE) |
| `2603.20213` | Yuan et al., *AgenticGEO* |
| `2607.14035` | Martinez, *Optimizing Visibility in Generative Engines: A Critical Survey* |
| `2509.08919` | Chen et al., *GEO: How to Dominate AI Search* |
| `ssrn-6815500` | Kargaev, *SEEN Framework* |
| `2307.03172` | Liu et al., *Lost in the Middle* (cited by GEO-SFE, not in our corpus) |

---

## Measured citation drivers, ranked by evidence strength

| Factor | Effect | Evidence | Our check |
|---|---|---|---|
| Verbatim quotations | **+41% PAWC** (19.3 → 27.2); +22% on live Perplexity | Controlled, GEO-bench 10k queries | `QUOTE-P06` |
| Cite external sources | **+30-40% PAWC**; **+115% for rank-5 pages** | Controlled, same benchmark | `QUOTE-P06` |
| Statistics, prices, dates in text | **+30-40% PAWC**; +37% subjective on Perplexity | Controlled | `QUOTE-P07` |
| Tables and lists (`F_d` 0.25-0.35) | **+17.3% citation rate**, p<0.001, d=0.64; +43% extraction accuracy | Controlled, 200 docs × 6 engines | `READ-P03` |
| Answer in first 30% of DOM | **44.2% of ChatGPT citations** originate there | Observational industry study; the SEEN paper that reports it calls it "industry research and correlational" and warns the safe reading is *not* that moving text up guarantees citations | `QUOTE-P08` |
| Emphasis density (`E_d` 0.05-0.10) | Sentence-initial bold carries **2.0× attention weight** | Controlled ablation | `READ-P04` |
| Readability / fluency | **+15-30% PAWC** | Controlled | `QUOTE-P09` |
| Heading hierarchy (depth 3-5) | Feature weight 0.25-0.45; removing it costs **9% of top-20 retrieval** | Controlled  | `READ-009` |
| Keyword stuffing | **−8.3% PAWC**, −10% on Perplexity | Controlled, rejected | deliberately none |

**Retrieval chunk window: 150-300 words.** GEO-SFE adopts `L_p ∈ [150, 300]` as a
design principle, attributing the ~31% mid-passage attention degradation above
300 words and the ~23% citation-probability loss below 150 to *Lost in the
Middle* (`2307.03172`) rather than measuring them itself. What GEO-SFE does
measure is the structural intervention as a whole: **+17.3% citation rate,
n=200 articles × 6 engines, p<0.001, Cohen's d=0.64** — verified verbatim in the
paper, including the per-architecture breakdown (+19.2% search-then-synthesize,
+19.7% integrated, +14.0% iterative).

`site-evidence-collector` targets **225 words, hard cap 300**
(`CHUNK_TARGET_WORDS`). Previously 320/512, chosen by feel — past the cliff. A
well-sourced design principle is not a measured optimum, but it beats a guess.

### How our numbers map to the paper's

`format_density` implements the paper's `F_d = Σ n_i / N_total` over list, table
and code **elements** — containers, not items. Counting `<li>` and `<tr>` instead
made one twenty-item list score twenty and put the ratio on a different scale
from the published 0.25-0.35 band; a code review caught the inflated values and
reading the definition confirmed why. Structural elements inside `nav`, `header`,
`footer` and `aside` are excluded, because the word count they are measured
against comes from main content only — otherwise a large navigation menu reads as
a well-structured page.

`first_answer_offset` is measured in the reading flow (words into the extracted
text), not in raw markup. Measured in markup it is mostly a function of how much
inline script and JSON-LD a page ships.

Both are approximations of someone else's operationalisation, and neither has
been calibrated against the paper's own corpus. They are good enough to rank
pages against each other and to justify a recommendation; they are not
interchangeable with the paper's measurements.

### Why these ship as recommendations, not findings

All six are `proactive_recommendations`, never `findings`. The effect sizes are
real, but C-SEO Bench found only **3 of 54** method-domain combinations
significant, so the optimal edit is instance-dependent. "This page has no table"
is not a defect, and emitting it as one would be exactly the confident false
positive the rest of this marketplace exists to avoid. The collector counts the
structure (`extracted.json#structure`); the skills recommend against it.

The unmeasurable engine-side factors are handled the same way: `QUOTE-P04`
(question-shaped headings) stands in for search activation and `QUOTE-P05`
(comparison content) for the competing candidate pool. Neither can be measured
from one site, so neither is ever phrased as a defect.

One factor is now genuinely measured rather than proxied: **engine-specific
reachability**. `crawl-access-audit` emits `engine_reachability`, a per-assistant
verdict derived from the per-agent robots resolution and the user-agent probe.

## Claims we may not make

**Structured data does not have a measured citation effect.** Across 45 reviewed
studies there is no controlled ablation showing JSON-LD produces a significant
lift in retrieval or citation share. It is a normative recommendation, universally
repeated and unmeasured. `structured-data-audit` still earns its place — broken
or contradictory markup is a real, provable defect, and machine-readability is a
genuine benefit — but its findings describe **what a machine cannot extract**,
never a citation, ranking or traffic gain. The registry carries this warning in
its header.

**"Up to 40% more visibility" is routinely misquoted.** It is a relative gain in
Position-Adjusted Word Count inside a simulator where five documents were already
injected into the context window. It is not 40% more traffic, clicks, or
discovery.

**Body-only rewrites can lose citations outright.** SAGEO Arena (171,003
documents, 2,700 queries): GEO rewrites of body text produced
**−9% top-20 retrieval, −16% reranking presence, −6% net citations**, because
body semantics drifted away from headings and embeddings (reported in
`2607.14035`, which stresses that structure must be evaluated stage by stage
rather than "treated as a universal talisman"). *Every content fix we
emit must say: keep headings and title aligned with the change.* A fix that
improves downstream citability while destroying upstream retrieval is a net loss
we caused.

**One-size-fits-all recipes mostly fail.** C-SEO Bench: across two tasks, six
domains, ~1,900 queries and 16,360 documents, **only 3 of 54 method-domain
combinations are significant** (verified in `2607.14035`). Optimal edits are instance-dependent.
Findings should be phrased conditionally — what is absent and what that prevents
— not as "do X for +Y%".

**Referral gains are not causally established.** The strongest pro-GEO traffic
result (5.7× ChatGPT referrals) had untreated pages on the same site growing 3.5×
anyway; the isolated multiplier was 1.82 [1.31, 2.54] with a placebo test at
**p = 0.16**. The authors call it suggestive. So do we.

## Third-party support for the thesis

Independent evidence that GEO and SEO are different problems — which is what this
whole marketplace asserts:

- URL-level **Jaccard overlap of 0.11-0.18** between Google SERP and AI engines
- **53% of AI-Overview cited domains do not appear in the organic top 10**, and
  27% are absent from the top 100 (Kirsten et al., via `2607.14035`)
- **27.1% of URLs engines retrieve are inaccessible** — independent justification
  for putting REACH first in the chain
- Run-to-run citation stability is only **0.34-0.42 Jaccard over 45 days**, so
  ~7-8 repetitions are needed for a stable estimate. This is why `bench/` entries
  are drift-tolerant smoke signals and hard assertions live in `tests/`.

## Engagement: what happens after a citation

Grounds `engagement-audit`, and `STAY-002` in particular.

- **CTR falls 15% → 8%** when a Google AI summary is present; **26% zero-click**
  (Pew, 900 adults, 68,879 real searches)
- **−15% daily traffic** to English Wikipedia articles exposed to AI Overviews
  (causal, staggered rollout)
- Position-one organic CTR **28% → 19%**; zero-click above 58%
- Visitors arriving from an assistant are **mid-funnel** — pre-persuaded, seeking
  to verify a specific recommendation, not to begin research
- The landing page must work as a **justification asset**: pros/cons, comparison
  tables, explicit value claims, high in the DOM
- **Lifecycle gaps get substituted.** No post-purchase or troubleshooting content
  means the assistant cites a competitor for that leg of the journey

## What a site-only crawl cannot detect

Stating our own ceiling, because a tool that hides its blind spots is not
trustworthy. These belong in `coverage.limitations` on every report.

| Factor | Why it matters | Detectable here? |
|---|---|---|
| Search activation probability | **57.8% of ChatGPT runs never search the web at all**; AI Overviews fire on 13.7% of trending queries (64.7% for question-form). A perfectly optimised site is invisible if the query never triggers retrieval. | **No** — engine-side query routing |
| Earned-media dominance | For niche brand queries ChatGPT cites **95.1% third-party, 4.9% brand-owned**. The decisive corpus is off-site. | **No** — needs external crawl |
| Competitor pool density | Citation share is redistributive: when rivals optimise, your share moves even if your page is unchanged. | **No** — needs the candidate pool |
| Engine-specific routing | ChatGPT cites 0% social on niche brand queries; Perplexity cites YouTube heavily; Gemini is up to 54% brand-friendly. A tactic that wins on one loses on another. | **No** — proprietary |
| RAG context position | Where the page lands inside the context window drives selection. | **Partial** — DOM position yes, context rank no |
| Image caption semantics | Multimodal RAG retrieves visual semantics; captions carry extractable meaning. | **Yes** — and we don't check it yet |
| Off-site retrieval boosters | Commercial GEO distributes content on Reddit, Wikipedia and forums to steer retrieval. | **No** — operates elsewhere |

Five of seven are outside any site crawl. That is not a defect in the tool; it is
the honest boundary of what auditing one website can tell you, and saying so is
worth more than a confident number.
