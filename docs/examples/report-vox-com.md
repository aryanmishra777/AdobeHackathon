<!--
A real report, produced the way the marketplace is meant to be used: an agent
following audit-orchestrator/SKILL.md step by step -- collect once, profile the
site, dispatch six skills, review the model-judged candidates against the
registry guards, merge, score, plan, emit, validate.

Target: https://www.vox.com, 12 September 2026, 25 pages at the default budget.
Everything here is derived from publicly fetchable data, retrieved read-only at
that moment. Live sites change; treat it as an illustration of shape and tone.

The agent's own review dropped three candidates the scripts had raised and
recorded why in report.json under run.agent_review. That review is the part no
script does, and it is where a quarter of the false positives were caught.

Off-site corroboration was not run: the session had no web search tool exposed
to the audit. The coverage section says so.
-->

# AI-Readiness Audit — https://www.vox.com

Vox is readable and well-structured, but robots.txt makes it invisible to ChatGPT, Claude and Perplexity users -- one line to change.

| | Grade | Score |
|---|---|---|
| **Discoverability** — can AI assistants find, trust and cite you? | C | 60/100 |
| **Engagement** — do visitors who arrive stay? | A | 94/100 |

**14 findings:** 0 critical · 1 high · 8 medium · 5 low
Audited 2026-09-12T09:40:27Z · 25 pages sampled

## Which assistants can reach you

| Assistant | Status | What we measured |
|---|---|---|
| ChatGPT | **blocked** | robots.txt disallows ChatGPT-User |
| Claude | **blocked** | robots.txt disallows Claude-User, Claude-SearchBot |
| Perplexity | **blocked** | robots.txt disallows Perplexity-User, PerplexityBot |
| Google AI | **reachable** | Googlebot was served the full page |
| Bing / Copilot | **partial** | Bingbot is permitted by robots.txt, but no request was made under that agent name, so whether the edge serves it is unverified |

> Blocked *training* crawlers are listed separately and are not a defect: declining to be training data is a content-licensing choice, and it does not affect whether an assistant can answer a question about you today.

## Fix these first

1. **Allow ChatGPT-User, OAI-SearchBot, Claude-User, Claude-SearchBot, PerplexityBot and Perplexity-User in robots.txt** — It is the only high-severity finding and a one-line change. Blocking the retrieval agents means a reader asking ChatGPT, Claude or Perplexity about a Vox story gets an answer sourced from someone else. Training crawlers (GPTBot, ClaudeBot) can stay blocked -- that is a separate, legitimate licensing choice. *(fixes F-001; effort: S)*
2. **Add sameAs links to the NewsMediaOrganization entity** — Vox is an ambiguous name -- a Spanish political party and an amplifier brand share it. One JSON-LD edit linking Wikipedia, Wikidata and the social profiles resolves it for every machine at once. *(fixes F-002, F-006; effort: S)*
3. **Give every article a unique meta description and consistent og: tags** — Template-level fix covering two findings across the sample; the article body already carries the facts, the metadata just does not summarise them. *(fixes F-003, F-004; effort: S)*
4. **Open each article with a sentence that names its subject** — Retrieval pulls a passage away from its headline. The first sentence of a Vox explainer often assumes the headline was read; one subject-naming sentence per piece makes the lead chunk quotable alone. *(fixes F-005, F-008; effort: M)*
5. **Remove the entry interstitial or defer it until the second page view** — A visitor arriving from an assistant is mid-task; an interstitial on arrival is the first thing they see instead of the answer they came for. *(fixes F-009; effort: S)*

## Findings

### Can assistants get in?

#### F-001 · AI assistants are blocked from reading the site  `high`

**What we found.** robots.txt disallows 6 of 8 AI retrieval and search crawlers from '/': ChatGPT-User, Claude-SearchBot, Claude-User, Perplexity-User, PerplexityBot, YouBot. ChatGPT-User and Claude-User and Perplexity-User fetch pages in real time when a user asks a question, so the brand cannot appear in those answers.

**Why it matters.** These crawlers fetch a page at the moment a user asks a question; if they receive a Disallow they never retrieve the content, so no amount of on-page improvement can make the brand citable.

**Fix.** Allow AI retrieval crawlers in robots.txt
- Remove or narrow the Disallow rules for ChatGPT-User, Claude-SearchBot, Claude-User, Perplexity-User, PerplexityBot, YouBot
- Keep any training-crawler policy separate and deliberate
- Re-test with curl using each agent's user-agent string

**Check it yourself.** `curl -s https://www.vox.com/robots.txt and read the User-agent groups for ChatGPT-User, Claude-SearchBot, Claude-User`

#### F-007 · Sitemap pages that nothing links to  `medium`

**What we found.** 434 URL(s) listed in the sitemap are reached by no internal link on any of the 25 pages sampled: https://www.vox.com/sitemaps/entries/2026/9, https://www.vox.com/sitemaps/entries/2026/8, https://www.vox.com/sitemaps/entries/2026/7.... Because the crawl sampled only part of the site, these may be linked from a page we did not fetch -- treat this as a list to check rather than a confirmed set of orphans.

**Why it matters.** A sitemap entry tells a crawler a URL exists; an internal link tells it the page matters and gives it context. Pages with neither a link nor an inbound path are fetched last and weighted least.

**Fix.** Link the advertised pages from somewhere a crawler walks
- Confirm each URL above is genuinely meant to be public
- Add a link from a hub, category or navigation page within three clicks of the home page
- Drop from the sitemap anything that is deliberately unlinked, so the sitemap stops advertising it

**Check it yourself.** `Search the site's navigation and body copy for a link to https://www.vox.com/sitemaps/entries/2026/9`

#### F-010 · AI training crawlers are blocked (informational)  `low`

**What we found.** robots.txt disallows the training-corpus crawlers Applebot-Extended, Bytespider, CCBot, Google-Extended, anthropic-ai, cohere-ai, meta-externalagent, omgilibot. This does not affect whether assistants can find and cite the site today -- it affects whether its content contributes to future model training. Google-Extended in particular does not influence Google Search or AI Overviews ranking.

**Why it matters.** Blocking training crawlers is a legitimate choice with no effect on present-day citability; the only risk is blocking retrieval agents by accident alongside them.

**Fix.** Confirm this opt-out is intentional, then leave it in place
- Verify the block matches the organisation's stated policy
- If the intent was only to opt out of training, confirm that retrieval agents are still allowed

**Check it yourself.** `curl -s https://www.vox.com/robots.txt and read the User-agent groups for Applebot-Extended, Bytespider, CCBot`

### Can they read the page?

#### F-008 · Heading structure does not describe the page  `medium`

**What we found.** 8 of 25 pages exhibit heading hierarchy breaks: 2 have no <h1>; 6 skip heading levels.

**Why it matters.** Headings define chunk boundaries during semantic retrieval; consistent hierarchy ensures snippets retain their parent topic context.

**Fix.** Structure content with hierarchical heading tags
- Ensure every page has exactly one distinct <h1> summarizing its subject
- Follow sequential descending levels (h1 -> h2 -> h3) without skipping intermediate ranks
- Avoid using heading tags merely for visual styling

**Check it yourself.** `curl -s https://www.vox.com/ | grep -oE '<h[1-6]'`

#### F-011 · Content is delivered inside an iframe or third-party widget  `low`

**What we found.** https://www.vox.com/21523212/crossword-puzzles-free-daily-printable loads 1 iframe(s) from cdn3.amuselabs.com; iframe content is not part of this page for extraction purposes.

**Why it matters.** Widgets rendered inside iframes do not expose their DOM tree to parent page crawlers; mirroring figures into the host document preserves extractability.

**Fix.** Mirror third-party widget metrics into page text and structured data
- Extract aggregate ratings and review counts from the widget provider
- Render the rating value and total count into visible HTML text
- Add an AggregateRating JSON-LD schema block to the page

**Check it yourself.** `curl -s https://www.vox.com/21523212/crossword-puzzles-free-daily-printable and confirm the iframe body text is absent`

### Can they parse facts out?

#### F-002 · The organization entity has no sameAs links  `medium`

**What we found.** The Organization entity on https://www.vox.com/2017/7/26/15993716/solar-eclipse-2017 declares no sameAs array.

**Why it matters.** sameAs is the primary machine-readable bridge between the website and external knowledge graphs, establishing entity confidence for AI assistants.

**Fix.** Add verified sameAs links to the Organization schema
- Add a sameAs array linking to Wikidata, LinkedIn, and official profiles
- Ensure links point only to genuinely controlled brand properties

**Check it yourself.** `Inspect the Organization block on https://www.vox.com/2017/7/26/15993716/solar-eclipse-2017 for sameAs`

#### F-003 · Titles and meta descriptions are missing, duplicated or conflicting  `medium`

**What we found.** 25 of 25 pages share duplicate titles: e.g. 25 pages share 'tiktok'. Observed on 25 of 25 sampled pages: https://www.vox.com/, https://www.vox.com/2017/7/26/15993716/solar-eclipse-2017, https://www.vox.com/2018/12/7/18113237/ethics-and-guidelines-at-vox-com....

**Why it matters.** Duplicated titles cause search engines to treat pages as identical variants.

**Fix.** Make page titles distinct and unique
- Ensure every URL template generates a distinct title naming the specific page subject

**Check it yourself.** `curl -s https://www.vox.com/ | grep -i '<title>'`

#### F-004 · Social metadata is missing or contradicts the page  `medium`

**What we found.** 25 pages declare og:title contradicting page title: https://www.vox.com/today-explained-newsletter/502504/republican-convention-affordability og:title is 'The one problem Trump can’t afford' but title is 'TikTok'.

**Why it matters.** Contradictions between social metadata and HTML tags cause preview cards and assistant summaries to display conflicting snippets.

**Fix.** Align og:title tags with page titles
- Update OpenGraph tags to accurately reflect the page title and summary

**Check it yourself.** `curl -s https://www.vox.com/today-explained-newsletter/502504/republican-convention-affordability | grep -i 'og:title'`

### Can they quote a clear fact?

#### F-005 · Passages do not make sense when retrieved on their own  `medium`

**What we found.** 44 of 325 assessed content chunks (>= 25 words, under a heading) neither name their subject nor resolve their opening reference; 19 of 25 content page(s) affected (crawl did not complete). Example under "The Logoff" on https://www.vox.com/the-logoff-newsletter-trump/502573/jimmy-kimmel-james-talarico-interview-abc-fcc-trump: ", a daily newsletter that helps you stay informed about the Trump administration without letting political news take over your life. Subscribe here . Welcome to"

**Why it matters.** Retrieval hands a single chunk to the model with no heading and no neighbouring text. A chunk that does not name its own subject cannot be quoted as an answer, because the assistant cannot say what it is about.

**Fix.** Rewrite passages so each names its subject in its first sentence
- Identify chunks that open with 'It', 'They', 'This' or a bare figure on https://www.vox.com/the-logoff-newsletter-trump/502573/jimmy-kimmel-james-talarico-interview-abc-fcc-trump and the other affected pages
- Replace the opening pronoun with the product or brand name
- Bind every number to what it counts (currency, unit, period)
- Remove positional references ('above', 'below', 'as mentioned')

**Check it yourself.** `Open https://www.vox.com/the-logoff-newsletter-trump/502573/jimmy-kimmel-james-talarico-interview-abc-fcc-trump, read only the passage under "The Logoff" with nothing above it, and ask which product or plan it describes.`

#### F-006 · The brand or product is named inconsistently  `medium`

**What we found.** The organisation appears under 2 materially different names across 25 sampled pages: "tiktok", "vox".

**Why it matters.** An assistant treats two unlinked names as two entities and splits the evidence for each. One consistent name lets all the signal accrue to one entity it can cite.

**Fix.** Pick one canonical name for the entity and use it everywhere
- Choose the canonical brand name
- Use it verbatim in every <title>, the og:site_name and schema.org name
- A short form is fine in body copy as long as the full form appears too

**Check it yourself.** `Compare the brand name in the <title>, og:site_name and schema.org markup across https://www.vox.com's pages.`

### Will they trust and repeat it?

#### F-014 · Factual claims carry no attribution  `low`

**What we found.** https://www.vox.com/politics/502567/trump-iran-gas-prices-republican-midterm-convention states 1 statistic or research claim(s) with no source, author or methodology. Example: "But political science research suggests that economic trends in the runup to Election Day can shift votes at the margin."

**Why it matters.** An unsourced statistic is discounted by a reader deciding what to repeat; a cited one can be carried into an answer with the citation attached.

**Fix.** Put a source next to every claim about the wider world
- Link the study, name the customer, or add a short methodology note beside each statistic
- Claims about your own operations do not need an external source

**Check it yourself.** `Read https://www.vox.com/politics/502567/trump-iran-gas-prices-republican-midterm-convention and look for a source next to the claim`

### Do visitors who arrive stay?

#### F-009 · An interstitial blocks the page on arrival  `medium`

**What we found.** https://www.vox.com/good-medicine-newsletter/502460/depression-anxiety-symptoms-treatment-doctor-questions includes a modal or overlay in the initial HTML (aria-modal="true"). Content of 16015 characters is served on the page beneath it. Observed on 9 of 9 sampled pages: https://www.vox.com/good-medicine-newsletter/502460/depression-anxiety-symptoms-treatment-doctor-questions, https://www.vox.com/america-actually/502596/trump-midterms-strategy-republicans-convention-vance, https://www.vox.com/politics/502567/trump-iran-gas-prices-republican-midterm-convention....

**Why it matters.** An overlay on entry costs the visitor an action before they have decided the page is worth one.

**Fix.** Serve the content behind the overlay, not instead of it
- Render the full page first; layer the notice on top
- For a required consent notice, keep it but do not block scroll or hide the main content
- Do not trigger newsletter or promo modals on first view

**Check it yourself.** `Open https://www.vox.com/good-medicine-newsletter/502460/depression-anxiety-symptoms-treatment-doctor-questions in a private window and note what appears before the content`

#### F-012 · Images without dimensions risk layout shift  `low`

**What we found.** On https://www.vox.com/good-medicine-newsletter/502460/depression-anxiety-symptoms-treatment-doctor-questions, 3 of the first 3 images (the best available proxy for above-the-fold) declare neither width nor height; 197 of 207 images site-wide lack dimensions. Reserving no space for them risks layout shift as they load.

**Why it matters.** An image with no reserved space pushes content down when it loads, and a visitor who was about to click the thing that moved is a visitor who mis-clicks and leaves.

**Fix.** Declare width and height (or aspect-ratio) on every content image
- Add width and height attributes matching the image's intrinsic size
- Or set aspect-ratio in CSS on the image container
- Prioritise images in the first screen, where a shift is most jarring

**Check it yourself.** `curl -s <page> | grep -c '<img' and compare with the count carrying a width attribute`

#### F-013 · Content is hard to read  `low`

**What we found.** https://www.vox.com/health/501565/lindsay-clancy-trial-postpartum-depression-psychosis runs 2649 words with 6 subheading(s) -- about 441 words per section. Long unbroken text is skimmed and abandoned. (Structural density only; typography and contrast are not assessed.). Observed on 2 of 9 sampled pages: https://www.vox.com/health/501565/lindsay-clancy-trial-postpartum-depression-psychosis, https://www.vox.com/policy/502386/inconceivable-kids-fertility-reproduction-ivf-families-parenthood.

**Why it matters.** A wall of text with no landmarks is skimmed for an exit, not read; subheadings give a scanner reasons to stay.

**Fix.** Break long pages into scannable sections
- Add a descriptive subheading every 200-300 words
- Pull key points into short lists
- Front-load each section with its conclusion

**Check it yourself.** `Scroll https://www.vox.com/health/501565/lindsay-clancy-trial-postpartum-depression-psychosis and look for structure breaking up the text`

## Worth doing even though nothing is broken

- **Publish an llms.txt pointing at the site's key facts** — GET https://www.vox.com/llms.txt returned 404. This is an emerging convention rather than an established requirement, but it costs almost nothing and forces a useful exercise: naming the handful of pages carrying the facts most worth quoting.
- **Server-render the pages that carry commercial facts** — Rendering strategy can be chosen per route. Pricing, product and about pages carry the facts worth quoting and benefit most; an authenticated dashboard does not need to change at all.
- **Mark the key terms so the important sentence is visibly the important one** — Median emphasis density across 25 sampled pages is 0.004 of body words; the range reported as useful is about 0.05-0.10. Emphasis is a weak signal on its own and this is the least-supported item in the structural literature -- worth doing while editing for other reasons, not worth a dedicated pass.
- **Publish one canonical Organization entity with a stable @id and link every page to it** — Organization markup is repeated across multiple pages without a stable identifier. One authoritative entity with a stable identifier lets a consumer resolve every page to the same organisation instead of inferring that connection from repeated names.
- **Add an FAQ answering the questions sales and support actually receive** — No FAQ page appears among the 25 sampled pages or in the sitemap. Question-and-answer pairs match how people phrase queries to assistants, and each answer is a self-contained passage that can be quoted whole.
- **Phrase section headings as the questions people actually ask** — 6 of 187 headings across 25 sampled pages are phrased as a question. Assistants answer questions, and a heading that states the question makes the passage beneath it an answer to retrieve rather than prose to summarise. This is a recommendation, not a defect: whether a query reaches the site at all is decided inside the engine and cannot be measured from here.
- **Publish facts worth citing so independent sources repeat them** — Off-site corroboration was not checked in this run (no search tool), but agreement across independent sources is what makes a claim repeatable. Original data or benchmarks give other sites a reason to state Vox's facts in their own words.
- **Carry search and filter state in the URL** — A search or filter control was seen in the sampled HTML. Reflecting its state in the URL makes each result set linkable, shareable and reachable with the back button.
- **State the answer above the fold, then elaborate below it** — Across 9 sampled pages the entry points open with a heading or hero rather than a one-line answer. Leading with the answer serves both halves of the audit at once.

## What this audit did not cover

- No browser renderer was available, so JavaScript dependency is inferred from raw HTML rather than measured.
- The engagement axis grades usability proxies. Engagement is measured from visitor behaviour -- dwell time, return visits, scroll, clicks -- and a site audit has no visitor to observe.
- Off-site corroboration (TRUST-006/007/009/012/013) was not run: this session had no web search tool available to the audit, so whether third parties repeat Vox's claims, and whether the name resolves to Vox Media in search, remains unverified.
- Whether an assistant retrieves anything at all for a given question is decided inside the engine (roughly 58% of ChatGPT runs answer without searching) and cannot be inferred from the site.
- For niche queries assistants cite third-party sources far more than the brand's own domain; the corpus that decides the answer is mostly not this site.
- Citation share is redistributive: it moves when competing pages change, even if this site does not. We audited one candidate, never the pool.
- Which engine is asking changes the outcome; the reachability table above is the only engine-specific fact a site crawl can settle.
- 8 checks were skipped because they need a web search this run did not have: STAY-016, TRUST-006, TRUST-007, TRUST-009, TRUST-010, TRUST-012, TRUST-013, TRUST-014
- Whether an assistant retrieves anything at all, what third-party sources say, which competitors share the retrieval pool, and how each engine reranks are all outside a single-site crawl.
