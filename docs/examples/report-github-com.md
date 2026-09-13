# AI-Readiness Audit — https://github.com/

GitHub lets every AI agent in and tells them so in robots.txt and llms.txt; what it does not do is tell them what it is -- there is no entity markup on the site, and the h1 on its home page is a slogan.

| | Grade | Score |
|---|---|---|
| **Discoverability** — can AI assistants find, trust and cite you? | C | 68/100 |
| **Engagement** — do visitors who arrive stay? | A | 99/100 |

**11 findings:** 0 critical · 1 high · 3 medium · 7 low
Audited 2026-09-13T07:49:55Z · 25 pages sampled

## Which assistants can reach you

| Assistant | Status | What we measured |
|---|---|---|
| ChatGPT | **reachable** | ChatGPT-User was served the full page; OAI-SearchBot is permitted by robots.txt but was not probed |
| Claude | **reachable** | Claude-User was served the full page; Claude-SearchBot is permitted by robots.txt but was not probed |
| Perplexity | **reachable** | PerplexityBot was served the full page; Perplexity-User is permitted by robots.txt but was not probed |
| Google AI Overviews / Gemini | **reachable** | Googlebot was served the full page |
| Microsoft Copilot | **partial** | Bingbot is permitted by robots.txt, but no request was made under that agent name, so whether the edge serves it is unverified |

## Fix these first

1. **Add an Organization entity to the shared layout and Offer markup to /pricing** — One template change gives every page a machine-readable statement of who publishes it, and one page's markup makes plan prices liftable as data instead of table text. Nothing else on the site is in the way of an assistant; this is what is missing. *(fixes F-001; effort: M)*
2. **Give the seven hub pages an h1 that names the page, and date /pricing** — The home page's h1 should say GitHub; /pricing should say when its prices were last changed. Both are copy edits. *(fixes F-002, F-004; effort: S)*
3. **Publish a marketing-section sitemap with lastmod and declare it in robots.txt** — Eighty pages, generated at deploy; the cheapest way to tell a crawler which of them changed. *(fixes F-003; effort: S)*

## Findings

### Can assistants get in?

#### F-003 · No XML sitemap is published or declared  `medium`

**What we found.** robots.txt declares no Sitemap directive; GET https://github.com/sitemap.xml returns 406 Not Acceptable (the path falls into the /<user> route space and is not a sitemap), and the /sitemap the footer links to is an HTML directory for people, not an XML file a crawler consumes. Medium rather than the registry's high for a large site: every marketing page audited here is one click from the home page's navigation (74 crawlable links), so crawl-only discovery of this section is complete, and the deep sections a sitemap would have to enumerate are user repositories, which no sitemap could list. What a sitemap would add is lastmod -- a machine's only cheap way to learn that /pricing or /features changed.

**Why it matters.** A sitemap is how a crawler learns which URLs exist and which changed, without depending on following links inward from the home page.

**Fix.** Publish a small XML sitemap for the marketing section and declare it in robots.txt
- Generate a sitemap of the ~80 marketing, solutions, resources and about pages with <lastmod> from each page's last deploy
- Serve it at a path outside the /<user> route space (for example /sitemaps/marketing.xml) and add Sitemap: to robots.txt
- Leave repositories out of it; the API and the trending/topics pages are the discovery path for those

**Check it yourself.** `curl -sI https://github.com/sitemap.xml`

#### F-007 · AI training crawlers are blocked (informational)  `low`

**What we found.** robots.txt disallows the training-corpus crawler Bytespider. This does not affect whether assistants can find and cite the site today -- it affects whether its content contributes to future model training.

**Why it matters.** Blocking training crawlers is a legitimate choice with no effect on present-day citability; the only risk is blocking retrieval agents by accident alongside them.

**Fix.** Confirm this opt-out is intentional, then leave it in place
- Verify the block matches the organisation's stated policy
- If the intent was only to opt out of training, confirm that retrieval agents are still allowed

**Check it yourself.** `curl -s https://github.com/robots.txt and read the User-agent groups for Bytespider`

### Can they read the page?

#### F-008 · Heading structure does not describe the page  `low`

**What we found.** https://github.com/marketplace and https://github.com/partners skip a heading level (an h1 followed by an h3). Two of 25 pages; the rest are well formed.

**Why it matters.** Headings define chunk boundaries during semantic retrieval; consistent hierarchy ensures snippets retain their parent topic context.

**Fix.** Structure content with hierarchical heading tags
- Ensure every page has exactly one distinct <h1> summarizing its subject
- Follow sequential descending levels (h1 -> h2 -> h3) without skipping intermediate ranks
- Avoid using heading tags merely for visual styling

**Check it yourself.** `curl -s https://github.com/marketplace | grep -oE '<h[1-6]'`

### Can they parse facts out?

#### F-001 · The marketing site publishes no entity markup: no Organization, WebSite, SoftwareApplication or Offer anywhere  `high`

**What we found.** 23 of 25 sampled pages carry no JSON-LD, microdata or RDFa at all; the only structured data in the sample is a FAQPage block on /education and on /services. There is no Organization entity naming GitHub, Inc. with a logo, sameAs links or a stable @id; no WebSite; no SoftwareApplication or Product/Offer on /pricing, /features or /enterprise; no BreadcrumbList. Every fact a machine would want to lift -- what GitHub is, who owns it, what the plans cost -- exists only as prose and HTML tables. The registry's PARSE-001 is defined as none at all, which two FAQ blocks technically avert; the condition it describes holds for every entity that matters.

**Why it matters.** An entity resolver identifies an organisation from markup that names it consistently across pages; without one, GitHub the site is a bag of prose that competes with GitHub the Wikipedia article for the right to describe GitHub. Plan prices as Offer data are the difference between an assistant quoting the number and paraphrasing it.

**Fix.** Publish one Organization entity site-wide and SoftwareApplication/Offer markup on the plan and product pages
- Add an Organization block (name, legalName, url, logo, sameAs to Wikipedia/Wikidata/LinkedIn/X, @id https://github.com/#organization) to the shared layout, and a WebSite block on the home page
- Mark /pricing up as SoftwareApplication with one Offer per plan (name, price, priceCurrency, billingIncrement) so plan prices are liftable as data
- Add BreadcrumbList on the /solutions, /features and /resources trees, and Article markup with datePublished on /customer-stories/* and /newsroom items

**Check it yourself.** `curl -s https://github.com/pricing | grep -c 'application/ld+json'  (expect 0); then the same on https://github.com/ and https://github.com/about`

#### F-002 · Titles and meta descriptions are missing, duplicated or conflicting  `medium`

**What we found.** On 7 of 25 pages the <title> describes the page and the <h1> is a slogan that does not: the home page is titled 'GitHub · Change is constant. GitHub keeps you ahead.' with h1 'The future of building happens together'; /features is 'GitHub Features' over 'The tools you need to build what you want'; /about is 'About GitHub' over 'Let's build from here'; /mcp, /partners, /sponsors and /education follow the pattern. A machine reading the h1 as the page's subject -- which retrievers and snippet builders do -- learns nothing from it on the seven pages that introduce the company.

**Why it matters.** When title and h1 contradict each other, search indexers struggle to identify the true focus of the page.

**Fix.** Align page title with primary h1 heading
- Align the title tag with the visible h1 subject matter

**Check it yourself.** `curl -s https://github.com/ | grep -E '<title>|<h1'`

#### F-005 · Social metadata is missing or contradicts the page  `low`

**What we found.** /topics, /trending and /collections carry the generic og:title 'Build software better, together' while their titles say 'Topics on GitHub', 'Trending repositories on GitHub today' and 'Collections'. A social card or a link preview for any of the three shows the slogan instead of the page. Three explore pages; low.

**Why it matters.** Contradictions between social metadata and HTML tags cause preview cards and assistant summaries to display conflicting snippets.

**Fix.** Align og:title tags with page titles
- Update OpenGraph tags to accurately reflect the page title and summary

**Check it yourself.** `curl -s https://github.com/topics | grep -i 'og:title'`

### Can they quote a clear fact?

#### F-006 · Passages do not make sense when retrieved on their own  `low`

**What we found.** 3 of 148 assessed passages on 2 of 25 pages point at the page around them instead of standing alone: 'Take Minecraft further with some of the projects below' and 'Made in Africa ... here' on /collections. Two per cent; low. Repository descriptions on /trending each sit under the repository's own name and are not counted.

**Why it matters.** Retrieval hands a single chunk to the model with no heading and no neighbouring text. A chunk that does not name its own subject cannot be quoted as an answer, because the assistant cannot say what it is about.

**Fix.** Rewrite passages so each names its subject in its first sentence
- Identify chunks that open with 'It', 'They', 'This' or a bare figure on https://github.com/trending and the other affected pages
- Replace the opening pronoun with the product or brand name
- Bind every number to what it counts (currency, unit, period)
- Remove positional references ('above', 'below', 'as mentioned')

**Check it yourself.** `Open https://github.com/trending, read only the passage under "Trending" with nothing above it, and ask which product or plan it describes.`

### Will they trust and repeat it?

#### F-004 · Time-sensitive content carries no visible date  `medium`

**What we found.** https://github.com/pricing shows no published or modified date in text, markup or metadata. It is the one page whose facts change on a schedule -- plan names, seat prices, Copilot inclusions -- and a machine quoting '$4 per user/month' from it cannot say when that was true. The other 24 sampled pages are evergreen and are not counted.

**Why it matters.** A consumer choosing between sources prefers the one that can show it is current. A page with no date at all cannot compete on recency even when it is the newer source.

**Fix.** Add a machine-readable published and updated date to these pages
- Emit <time datetime> for the publish date, and a second one for the last update, in the page template
- Mirror them as datePublished / dateModified in the page's JSON-LD
- Leave evergreen pages (about, contact, legal) undated

**Check it yourself.** `Open https://github.com/pricing and look for a publication or update date`

#### F-011 · Factual claims carry no attribution  `low`

**What we found.** https://github.com/trust-center states 'Fix security vulnerabilities 7x faster than the industry average with GitHub Advanced Security' with no source, sample or methodology. The claims about GitHub's own scale ('225M+ Developers', '90% of the Fortune 100') are the company counting itself and are not counted here; a comparison against an industry average is a claim about the world.

**Why it matters.** An unsourced statistic is discounted by a reader deciding what to repeat; a cited one can be carried into an answer with the citation attached.

**Fix.** Put a source next to every claim about the wider world
- Link the study, name the customer, or add a short methodology note beside each statistic
- Claims about your own operations do not need an external source

**Check it yourself.** `Read https://github.com/trust-center and look for a source next to the claim`

### Do visitors who arrive stay?

#### F-009 · Images without dimensions risk layout shift  `low`

**What we found.** On https://github.com/marketplace, 3 of the first 3 images (the best available proxy for above-the-fold) declare neither width nor height; 174 of 352 images site-wide lack dimensions. Reserving no space for them risks layout shift as they load.

**Why it matters.** An image with no reserved space pushes content down when it loads, and a visitor who was about to click the thing that moved is a visitor who mis-clicks and leaves.

**Fix.** Declare width and height (or aspect-ratio) on every content image
- Add width and height attributes matching the image's intrinsic size
- Or set aspect-ratio in CSS on the image container
- Prioritise images in the first screen, where a shift is most jarring

**Check it yourself.** `curl -s <page> | grep -c '<img' and compare with the count carrying a width attribute`

#### F-010 · Accessibility basics are missing  `low`

**What we found.** One form input on https://github.com/services has no <label>, aria-label or title (a limited mechanical check, not an accessibility audit). Low.

**Why it matters.** Unlabelled fields and missing landmarks make the page unusable with a screen reader or keyboard, and those visitors leave immediately.

**Fix.** Fix the mechanical accessibility basics
- Give every input a <label for> (or an aria-label)
- Wrap the page regions in <header>, <nav>, <main>, <footer>
- Then run a full accessibility audit -- this check only covers the mechanical minimum

**Check it yourself.** `Tab through https://github.com/services using only the keyboard`

## Worth doing even though nothing is broken

- **Mark up the facts buyers ask about, not merely the page type** — WebPage markup states that a page exists. Price, availability, location, hours and eligibility are the facts an assistant is asked for, and each one marked up is one more question the site can answer directly.
- **Add a liftable summary to the top of long pages** — https://github.com/trending runs to 2097 words with no summary, key-takeaways or TL;DR block near the top. A 2-3 sentence summary is the block most likely to be retrieved and quoted whole.
- **Publish facts worth citing so independent sources repeat them** — Off-site corroboration was not checked in this run (no search tool), but agreement across independent sources is what makes a claim repeatable. Original data or benchmarks give other sites a reason to state GitHub's facts in their own words.

## What this audit did not cover

- The sample is github.com's marketing and explore site: the home page and the first 24 sections its navigation links to (/features, /enterprise, /solutions, /pricing, /security, /about ...). Repositories, issues and user content -- the bulk of github.com's URL space -- were not sampled; robots.txt's rules for them (commits, blame, tree and forks disallowed for every crawler) are read from the file, not tested.
- All six render attempts succeeded and none gained content over the raw HTML: the marketing site is server-rendered. READ-001 does not appear because there is nothing for it to find.
- A first crawl sampled seven /collections/* pages and eight repositories before /pricing; four analyzer candidates from it (no pricing page, no buyer answers, 'Collection' as a second brand name, twelve undated 'articles') were artefacts of that sample and of the collector's footer-date and hidden-text handling. The collector and the analyzers were corrected during this audit -- section ranking, the hidden attribute, <template> subtrees, the copyright-year dateline, first-party subdomains, popover and closed-details modals -- each with a regression test; the report is from the corrected run.
- The 24 model-judged checks were considered against the registry; those emitted and the reason each other one was not are in run.agent_review.
- The engagement axis grades usability proxies. Engagement itself is measured from visitor behaviour -- dwell time, return visits, scroll, clicks -- and a site audit has no visitor to observe.
- Whether an assistant retrieves anything at all for a given question is decided inside the engine and cannot be inferred from the site.
- Citation share is redistributive: it moves when competing pages (Wikipedia, docs.github.com, developer blogs) change, even if this site does not. We audited one candidate, never the pool.
- Which engine is asking changes the outcome; the reachability table is the only engine-specific fact a site crawl can settle, and here every engine's agents were served and are named in robots.txt.
- 7 checks did not run; each has its reason in report.json under coverage.checks_skipped: TRUST-006, TRUST-007, TRUST-009, TRUST-010, TRUST-012, TRUST-013, TRUST-014
- Whether an assistant retrieves anything at all, what third-party sources say, which competitors share the retrieval pool, and how each engine reranks are all outside a single-site crawl.
