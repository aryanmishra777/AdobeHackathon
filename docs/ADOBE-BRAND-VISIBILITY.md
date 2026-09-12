# How this marketplace relates to Adobe Brand Visibility

Adobe ships a product in this space: **Adobe Brand Visibility**, "a generative
AI-first application for Generative Engine Optimization (also called Answer
Engine Optimization)", the evolution of LLM Optimizer combined with Semrush.
Its documentation is at
`experienceleague.adobe.com/en/docs/brand-visibility/using/home`. Read on
12 September 2026. This page records where we overlap, where we go deeper,
and — honestly — what it does that a cold crawl of one site never can.

## Their onsite checklist is a subset of ours

Adobe's *Best practices for LLM optimization* names seven onsite practices.
Every one has a home in our mechanism chain, usually with more depth behind it.

| Adobe Brand Visibility | Ours | What we add |
|---|---|---|
| "Ensure technical accessibility" via robots.txt and CDN review | REACH-002, 003, 005 | Per-agent robots resolution across 22 crawler tokens; the retrieval-vs-training split, so blocking `GPTBot` is informational and blocking `ChatGPT-User` is a defect; a live browser-vs-bot probe that catches soft blocks (khanacademy.org served 227 KB to a browser and 3 KB to `GPTBot`) |
| "URL Inspector to identify blocked or inaccessible pages" | REACH-012, engine reachability matrix | A per-assistant verdict — reachable, partial, degraded, blocked — for ChatGPT, Claude, Perplexity, Google AI Overviews/Gemini and Copilot, from measured data |
| "Update 10-15% of page content regularly" | TRUST-001, 002, 003 | Undated time-sensitive pages; staleness judged against what the site claims to be (a news site silent 30 days is stale, a brochure stable two years is not); sitemap `lastmod` claims tested for honesty |
| "Add citations and references to authoritative sources" | QUOTE-P06, TRUST-015 | The measured effect size: +30-40% relative visibility on GEO-bench (Aggarwal et al.), with the caveat that it is a simulator gain, not a traffic promise |
| "Use structured headers (H1, H2, H3) for better parsing" | READ-009 | And the warning from SAGEO Arena that body-only rewrites which drift from headings cost 9% of retrieval |
| "Add natural-language FAQs based on prompt analysis" | QUOTE-005, QUOTE-P02, PARSE-012 | Gated on whether the site sells anything, so Wikipedia is not told to add a pricing FAQ |
| "Assess brand credibility using EEAT" | TRUST-008, 009, 015 | An unambiguous identity sentence, machine-checked identity anchors, unattributed claims |
| "Brand mentions matter more than link authority" | TRUST-006 corroboration ledger | Which of the site's own claims appear nowhere else — the mechanism behind the mention |

Beyond their list, we also check what a machine can *read* (READ: client-side
rendering, facts locked in images, consent walls) and *parse* (PARSE: 14
structured-data checks), and we grade on-site engagement proxies (STAY),
labelled honestly as proxies.

## What their product does that ours cannot, and why

Adobe Brand Visibility runs prompts against live LLMs and reports **mentions,
citations, sentiment, position and a visibility score**, benchmarks competitors,
and measures **agentic traffic** and **referral traffic** from an analytics
integration. It can also **Optimize at Edge**, applying fixes through the CDN
"without any authoring changes required".

We do none of that, and we say so:

- **No LLM queries.** Whether an assistant mentions the brand is measured by
  asking assistants, at scale, repeatedly. We audit one site, cold, with no
  API. `references/audit-boundary.md` lists this as the first thing a site
  crawl cannot see, and every report carries it in `coverage.limitations`.
- **No analytics.** Agentic and referral traffic need a visitor to observe. Our
  engagement axis grades usability proxies and its headline says so.
- **No deployment.** The Round 3 handout is recommend-only, and we are. Adobe's
  "prescriptive content recommendations" and "opportunities" are what our
  findings and `priority_plan` produce; their "automates optimization fixes" is
  the step we are required not to take.

So the honest positioning: **this marketplace is the URL Inspector and the
Opportunities dashboard, rebuilt to run from a single read-only crawl with no
account, no LLM access and no analytics — and to be explicit about what that
boundary costs.** Adobe's product measures the outcome; ours diagnoses the
mechanism and stops where measurement would start.

## Vocabulary we adopted from it

- *Generative Engine Optimization, also called Answer Engine Optimization* — the
  orchestrator now activates on "AEO" and "AI visibility gaps" as well as "GEO".
- Their named platforms — ChatGPT, Perplexity, Copilot, Gemini, Google AI mode —
  are the rows of our engine reachability matrix, now labelled by the product a
  reader knows rather than the crawler token.
- *Zero-click journeys* — the framing behind our engagement research: a visitor
  who arrives from an AI answer is mid-task and pre-persuaded (STAY-002).

## What this does not change

Nothing in their documentation carries an effect size or a study design. Where
Adobe says "add citations", we cite the paper that measured it and the caveat
that comes with the number. `docs/EVIDENCE.md` remains the ledger; this page is
the map between our checks and the vendor's vocabulary.
