# What the evidence supports, and what it does not

Every threshold in this marketplace should be traceable to a measurement or
labelled as a judgment call. This file is that ledger. It exists so that a
finding can answer the question *"why is that the number?"* with something
better than "it seemed right".

Sources are the GEO literature collected in the team's NotebookLM knowledge base
(25 documents, September 2026). Figures below were extracted from that corpus.
**Numbers marked (unverified) have not yet been checked against the source PDF
directly** — do not put them in a submitted report until someone has.

---

## Measured citation drivers, ranked by evidence strength

| Factor | Effect | Evidence | Our check |
|---|---|---|---|
| Verbatim quotations | **+41% PAWC** (19.3 → 27.2); +22% on live Perplexity | Controlled, GEO-bench 10k queries | *none yet* |
| Cite external sources | **+30-40% PAWC**; **+115% for rank-5 pages** | Controlled, same benchmark | *none yet* |
| Statistics, prices, dates in text | **+30-40% PAWC**; +37% subjective on Perplexity | Controlled | *none yet* |
| Tables and lists (`F_d` 0.25-0.35) | **+17.3% citation rate**, p<0.001, d=0.64; +43% extraction accuracy | Controlled, 200 docs × 6 engines (unverified) | *none yet* |
| Answer in first 30% of DOM | **44.2% of ChatGPT citations** originate there | Observational, industry (unverified) | *none yet* |
| Emphasis density (`E_d` 0.05-0.10) | Sentence-initial bold carries **2.0× attention weight** | Controlled ablation (unverified) | *none yet* |
| Readability / fluency | **+15-30% PAWC** | Controlled | *none yet* |
| Heading hierarchy (depth 3-5) | Feature weight 0.25-0.45; removing it costs **9% of top-20 retrieval** | Controlled (unverified) | `READ-009` |
| Keyword stuffing | **−8.3% PAWC**, −10% on Perplexity | Controlled, rejected | deliberately none |

**Retrieval chunk window: 150-300 words.** Beyond 300, middle segments lose ~31%
of attention; below 150, information flow fragments and citation probability
drops ~23%. `site-evidence-collector` targets **225 words, hard cap 300**
(`CHUNK_TARGET_WORDS`), which is the middle of the measured window. It was
320/512 before this was checked — past the degradation cliff.

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
documents, 2,700 queries, unverified): GEO rewrites of body text produced
**−9% top-20 retrieval, −16% reranking presence, −6% net citations**, because
body semantics drifted away from headings and embeddings. *Every content fix we
emit must say: keep headings and title aligned with the change.* A fix that
improves downstream citability while destroying upstream retrieval is a net loss
we caused.

**One-size-fits-all recipes mostly fail.** C-SEO Bench tested 54 method×domain
combinations across ~1,900 queries: **3 were significantly positive, and none in
question-answering tasks** (unverified). Optimal edits are instance-dependent.
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
- **53% of AI-Overview cited domains do not appear in the organic top 10**
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
- Position-one organic CTR **28% → 19%**; zero-click above 58% (unverified)
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
