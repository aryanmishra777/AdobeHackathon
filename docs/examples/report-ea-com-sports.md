# AI-Readiness Audit — https://www.ea.com/sports

ea.com is open to AI retrieval by policy and slow to it by enforcement: every agent gets the page, forty-two seconds later, and the English sitemap hands a crawler 2021 sale pages that still say 'Save up to 50%' before it hands over FC 26.

| | Grade | Score |
|---|---|---|
| **Discoverability** — can AI assistants find, trust and cite you? | B | 75/100 |
| **Engagement** — do visitors who arrive stay? | A | 98/100 |

**12 findings:** 0 critical · 0 high · 5 medium · 7 low
Audited 2026-09-13T05:35:54Z · 25 pages sampled

## Which assistants can reach you

| Assistant | Status | What we measured |
|---|---|---|
| ChatGPT | **reachable** | ChatGPT-User was served the full page; OAI-SearchBot is permitted by robots.txt but was not probed |
| Claude | **reachable** | Claude-User was served the full page; Claude-SearchBot is permitted by robots.txt but was not probed |
| Perplexity | **reachable** | PerplexityBot was served the full page; Perplexity-User is permitted by robots.txt but was not probed |
| Google AI Overviews / Gemini | **reachable** | Googlebot was served the full page |
| Microsoft Copilot | **partial** | Bingbot is permitted by robots.txt, but no request was made under that agent name, so whether the edge serves it is unverified |

## Fix these first

1. **Find the bot-management rule that holds unrecognised clients for 42 s and exempt the retrieval agents robots.txt already allows** — The only finding that changes how much of ea.com an AI crawler can reach. robots.txt says GPTBot, ClaudeBot and PerplexityBot are welcome; the edge makes each of their fetches cost 42 seconds after a burst. Either exempt them or declare the delay. *(fixes F-003; effort: M)*
2. **Redirect the ended-sale pages and rebuild the locale sitemaps from live pages with lastmod** — Two findings, one fix: the pages whose titles advertise a sale that ended in 2021 are the same pages the sitemap offers first. Redirect them and regenerate the sitemap. *(fixes F-005, F-012, F-002; effort: S)*
3. **Give every page an h1 and stop escaping the markup inside tile headings** — Template-level: one change to the ea-tile and page components fixes 19 of 25 sampled pages. *(fixes F-004; effort: S)*

## Findings

### Can assistants get in?

#### F-002 · The English sitemap lists retired campaign pages, a form-confirmation page and a URL that redirects  `medium`

**What we found.** sitemap-en-au.xml (3,868 URLs, no lastmod on any entry) was read in the order it lists pages, and 7 of the first 20 URLs it offered are pages with nothing to index: the five ended-sale pages above (23-64 words of page-specific text each, most of it 'Origin Deals / Xbox Deals' link labels), https://www.ea.com/en-au/newsletter/double-opt-in-success ('Your email subscription has been confirmed.' -- 10 words, a system page that should never be in a sitemap), and https://www.ea.com/en-au/eaplay2018/june-10-recap, which 301s to /en-au/ea-play. The sitemap is the site's own statement of what deserves a crawler's time; here a crawler spending its budget on it gets a 2021 thank-you note before it gets FC 26.

**Why it matters.** A crawler that follows the sitemap in order spends its per-site budget where the sitemap points it. On a site whose edge allows about two fetches a minute to unrecognised clients, every wasted slot is a real page unfetched.

**Fix.** Regenerate the locale sitemaps from live, indexable pages and add lastmod
- Exclude campaign pages past their end date, redirecting URLs and system pages (newsletter confirmations, opt-in results) from sitemap generation
- Emit <lastmod> from the page's dateModified so crawlers can prioritise the 2026 pages over the 2017 ones
- Order entries by freshness or by section importance rather than by creation date

**Check it yourself.** `Open https://www.ea.com/sitemap-en-au.xml and fetch its first twenty <loc> entries; count the ones that redirect or carry under 100 words of their own text`

#### F-003 · The edge holds every response to a non-browser client for about 42 seconds  `medium`

**What we found.** Median time to first byte across the 25 sampled pages was 42,928 ms (range 42,415-128,806 ms), and robots.txt, the sitemap index and every user-agent probe took the same 42 s. This is not network distance: curl from the same machine, same user-agent string, fetched https://www.ea.com/ with a first byte in 0.7 s while Python's HTTP client waited 42 s, and headless Chromium announcing the audit's user-agent got an HTTP/2 protocol reset on all six render attempts. The edge classifies clients by their TLS and protocol fingerprint and holds or drops the ones it does not recognise as browsers. Two caveats the reader needs: the hold appeared only after the audit's earlier crawl of about fifty requests in the preceding hour (the first pass fetched 25 pages in under two minutes), so this is rate-triggered, not unconditional; and every named AI agent on the probe list was served the full page (status 200, ~113 KB) once the wait was over, so nothing is refused -- it is delayed to the point where a crawler with a per-site time budget gives up. A retrieval agent fetching one page for one user gets that page; a crawler building an index of ea.com from a non-browser stack gets about two pages a minute.

**Why it matters.** Crawlers allocate a time budget per site. A 42-second hold per response turns a 25-page sample into an 18-minute job and a full-site crawl into something no scheduler will finish; the pages that never get fetched are the ones an assistant can never cite.

**Fix.** Decide, and document, what the edge does with non-browser clients that identify themselves
- Find the bot-management rule that applies a delay/tarpit action to unrecognised TLS fingerprints after a request-rate threshold, and check whether the allow-list covers the retrieval agents robots.txt permits (GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot, Claude-SearchBot)
- If the hold is intended for those agents, say so in robots.txt with a Crawl-delay or a Disallow so the decision is visible; if not, exempt verified AI-agent networks from the rate action the way Googlebot's are exempted
- Re-test from a plain HTTP client after a burst of requests and confirm first-byte time stays under 2 s

**Check it yourself.** `Compare: curl -s -o /dev/null -w '%{time_starttransfer}\n' -A 'Mozilla/5.0 (compatible; BrandAIReadinessAudit/1.0)' https://www.ea.com/  against  python -c "import time,urllib.request as r;t=time.time();r.urlopen(r.Request('https://www.ea.com/',headers={'User-Agent':'Mozilla/5.0 (compatible; BrandAIReadinessAudit/1.0)'}));print(time.time()-t)"  after a burst of ~50 requests from the second client`

#### F-008 · AI training crawlers are blocked (informational)  `low`

**What we found.** robots.txt disallows the training-corpus crawlers Bytespider, cohere-ai, meta-externalagent. This does not affect whether assistants can find and cite the site today -- it affects whether its content contributes to future model training.

**Why it matters.** Blocking training crawlers is a legitimate choice with no effect on present-day citability; the only risk is blocking retrieval agents by accident alongside them.

**Fix.** Confirm this opt-out is intentional, then leave it in place
- Verify the block matches the organisation's stated policy
- If the intent was only to opt out of training, confirm that retrieval agents are still allowed

**Check it yourself.** `curl -s https://www.ea.com/robots.txt and read the User-agent groups for Bytespider, cohere-ai, meta-externalagent`

### Can they read the page?

#### F-004 · Heading structure does not describe the page  `medium`

**What we found.** 19 of 25 sampled pages break the heading hierarchy: 11 have no <h1> at all (the sale, gamescom, game-card and game-franchise pages open on an <h2> or an <h3>) and 10 skip levels. On https://www.ea.com/careers 12 of the 23 headings are published with their markup escaped -- the HTML literally reads <h3>&lt;b&gt;EA Studios&lt;/b&gt;</h3>, so a non-rendering reader sees the heading '<b>EA Studios</b>' -- and the site's component (ea-tile title-text="&lt;b&gt;...") unescapes it only in the browser.

**Why it matters.** Headings define chunk boundaries during semantic retrieval; consistent hierarchy ensures snippets retain their parent topic context.

**Fix.** Structure content with hierarchical heading tags
- Ensure every page has exactly one distinct <h1> summarizing its subject
- Follow sequential descending levels (h1 -> h2 -> h3) without skipping intermediate ranks
- Avoid using heading tags merely for visual styling

**Check it yourself.** `curl -s http://www.ea.com/about | grep -oE '<h[1-6]'`

#### F-009 · Informational images lack alternative text  `low`

**What we found.** 3 of 224 images across 3 sampled pages have no alt attribute (the Bejeweled franchise page, its news page and /sports). Low.

**Why it matters.** Alternative text allows visual content to be indexed and cited by multimodal and text retrieval engines.

**Fix.** Add alt attributes to informative images and mark decorative images empty
- Inspect images with missing alt attributes across content templates
- Provide descriptive alt text for diagrams, product photos, and informative figures
- Set alt="" explicitly on purely decorative icons, spacers, and background graphics

**Check it yourself.** `curl -s https://www.ea.com/en-au/games/bejeweled | grep -c '<img' and compare with the alt count`

### Can they parse facts out?

#### F-001 · No breadcrumb markup or navigation  `medium`

**What we found.** 20 of 25 sampled pages declare no BreadcrumbList and show no breadcrumb trail; the franchise pages (/en-au/games/bejeweled/bejeweled-stars) sit three levels deep with nothing on the page saying so.

**Why it matters.** Breadcrumbs state the hierarchical context of deep pages, helping AI agents understand where facts sit in relation to parent topics.

**Fix.** Add BreadcrumbList structured data and navigation trail
- Render breadcrumb navigation linking parent category paths
- Add BreadcrumbList JSON-LD markup indicating hierarchy position

**Check it yourself.** `Open https://www.ea.com/en-au/games/ssx and look for a breadcrumb trail`

#### F-006 · Titles and meta descriptions are missing, duplicated or conflicting  `low`

**What we found.** https://www.ea.com/en-au/game-cards and https://www.ea.com/en-au/game-cards-nz share the title 'EA Game Cards' with no country or region in it, so a search result or a citation cannot tell the Australian and New Zealand pages apart. Two pages; low. Observed on 3 of 25 sampled pages: https://www.ea.com/en-au/game-cards, https://www.ea.com/en-au/game-cards-nz, https://www.ea.com/en-au/gamescom.

**Why it matters.** Duplicated titles cause search engines to treat pages as identical variants.

**Fix.** Make page titles distinct and unique
- Ensure every URL template generates a distinct title naming the specific page subject

**Check it yourself.** `curl -s https://www.ea.com/en-au/game-cards | grep -i '<title>'`

### Can they quote a clear fact?

#### F-007 · Passages do not make sense when retrieved on their own  `low`

**What we found.** 4 of 74 assessed passages on 2 of 25 pages open with 'We' or 'Our' and never say who: 'We are among the largest video game development organizations, with over 8,000 game makers' under the careers heading 'EA Studios', and 'Our Legal team delivers practical risk-management solutions'. Five per cent is a residual; low.

**Why it matters.** Retrieval hands a single chunk to the model with no heading and no neighbouring text. A chunk that does not name its own subject cannot be quoted as an answer, because the assistant cannot say what it is about.

**Fix.** Rewrite passages so each names its subject in its first sentence
- Identify chunks that open with 'It', 'They', 'This' or a bare figure on https://www.ea.com/en-au/about/building-healthy-communities and the other affected pages
- Replace the opening pronoun with the product or brand name
- Bind every number to what it counts (currency, unit, period)
- Remove positional references ('above', 'below', 'as mentioned')

**Check it yourself.** `Open https://www.ea.com/en-au/about/building-healthy-communities, read only the passage under "Positive Play Charter" with nothing above it, and ask which product or plan it describes.`

### Will they trust and repeat it?

#### F-005 · Five ended-sale pages still advertise the sale in their title and headline while the body says it is over  `medium`

**What we found.** https://www.ea.com/en-au/black-friday/microsoft is titled 'Microsoft Black Friday Sales & Deals - Official EA Site', its headline reads 'Save up to 50%*', and the only paragraph on the page says 'Thank You for Joining us for Black Friday. We hope you are having fun playing our games and we'll see you next year for Black Friday.' The holiday-sale, publisher-sale, spring-sale and infinite-gaming pages are the same shape ('Save big* on top titles' over 'THANK YOU FOR JOINING US FOR THE HOLIDAY SALE'). Each is indexable, listed in sitemap-en-au.xml, and last modified between 2020 and 2022. A machine that reads the title and h1 -- which is what a search snippet and an assistant's citation do -- reports a live EA sale on Xbox; the page's own body says there is none. The Australian cash-card page (https://www.ea.com/en-au/game-cards-nz, modified 2017) presents Origin as 'EA's gaming service for buying and playing amazing games' while every page's navigation lists 'The EA app'; confirm which is current.

**Why it matters.** An assistant asked 'is there an EA sale on Xbox' can retrieve a page whose title and headline say yes. The site's own body text says no. That is a wrong answer with a citation to ea.com under it.

**Fix.** Retire or redirect ended-campaign pages; never leave a sale headline over a thank-you note
- 301 each ended sale page to /en-au/deals (or the live sale) and drop it from sitemap-en-au.xml
- Where a campaign page must stay, change its title and headline to the past tense the body already uses, and add noindex
- Give the cash-card page a current description of where codes are redeemed (the EA app) or redirect it to the live help article

**Check it yourself.** `Fetch https://www.ea.com/en-au/holiday-sale/microsoft and compare the <title> and first heading with the paragraph that follows them`

#### F-012 · Page content states facts that are no longer true  `low`

**What we found.** https://www.ea.com/en-au/games/bejeweled/bejeweled-stars is dated May 10, 2016 and says Bejeweled Stars 'is available now from EA and PopCap Games as a free download on the App Store and Google Play'. The game is still listed on both stores, so the claim is probably true; the risk is the ten-year-old page being quoted as news. Low; the retired-sale pages below are the real instance of this check.

**Why it matters.** Content that asserts a stale fact as current is discounted once a consumer catches one error, and the doubt spreads to the rest of the page.

**Fix.** Re-confirm the claim and stamp when it was last checked
- Verify the offering, version or event referenced is still current
- State the current fact, or add an explicit 'as of <date>'
- Move the page's visible date forward to when you confirmed it

**Check it yourself.** `Check whether the offering or event this passage describes is still current, then update the date`

### Do visitors who arrive stay?

#### F-010 · Images without dimensions risk layout shift  `low`

**What we found.** On https://www.ea.com/sports the first three images declare neither width nor height, and 97 of 97 images site-wide are the same; the ea-image component sizes them in the browser. Layout shift as they load is the cost.

**Why it matters.** An image with no reserved space pushes content down when it loads, and a visitor who was about to click the thing that moved is a visitor who mis-clicks and leaves.

**Fix.** Declare width and height (or aspect-ratio) on every content image
- Add width and height attributes matching the image's intrinsic size
- Or set aspect-ratio in CSS on the image container
- Prioritise images in the first screen, where a shift is most jarring

**Check it yourself.** `curl -s <page> | grep -c '<img' and compare with the count carrying a width attribute`

#### F-011 · Third-party scripts dominate the page  `low`

**What we found.** Every one of the 20 pages checked loads the same three third-party scripts render-blocking in the <head>: the Web Components polyfill loader from unpkg.com, Masonry 4.2.2 from cdnjs.cloudflare.com, and the SoundCloud player API from w.soundcloud.com. EA's own component library (pl.ea.com) is first-party and is not counted. Three is not 'many', and the polyfill is what makes the site's custom elements work at all; low, and reported because all three could be self-hosted and deferred. Observed on 20 of 20 sampled pages: https://www.ea.com/sports, https://www.ea.com/en-au/games/ssx, https://www.ea.com/en-au/games/bejeweled....

**Why it matters.** Render-blocking third-party code holds up the visitor's first view for a payload that adds nothing to the page they came for.

**Fix.** Load third-party scripts without blocking render
- Add async or defer to every third-party <script>
- Load tag managers and chat widgets after first paint
- Keep analytics -- just stop it blocking the critical path

**Check it yourself.** `Open the network panel on https://www.ea.com/sports and sort by domain`

## Worth doing even though nothing is broken

- **Publish an llms.txt pointing at the site's key facts** — GET https://www.ea.com/llms.txt returned 404. This is an emerging convention rather than an established requirement, but it costs almost nothing and forces a useful exercise: naming the handful of pages carrying the facts most worth quoting.
- **Publish one canonical Organization entity with a stable @id and link every page to it** — Organization markup is repeated across multiple pages without a stable identifier. One authoritative entity with a stable identifier lets a consumer resolve every page to the same organisation instead of inferring that connection from repeated names.
- **Show an honest update date on pages that change** — 5 of 25 sampled content pages carry no visible published or updated date, though the site's content reads as current. A truthful update date lets a consumer prefer the page over an older competing source.

## What this audit did not cover

- The edge held every response to the audit's HTTP client for about 42 seconds once it had seen roughly fifty requests in the preceding hour. The default 120-second budget produced zero pages; this run used a 1,500-second budget, took 764 seconds, and fetched 25 pages. The collector now fetches the origin variants and the user-agent probes together and caps the sitemap and probe phases at a share of the budget so the page sample always gets the rest.
- None of the six render attempts succeeded: headless Chromium announcing the audit's user-agent received an HTTP/2 protocol reset from the edge. Every render-dependent conclusion is inferred from the raw HTML, which on this site carries the page text (the components enhance server-rendered fallbacks), so READ-001 does not appear and is not expected to.
- The sample is the /sports hub, the home page, /about, /careers, /brand-partnerships and the first twenty entries of sitemap-en-au.xml, which is ordered by creation date and so led with 2016-2021 pages (franchise pages for SSX, Ultima and Bejeweled; ended sales; event recaps). The sitemap index lists 35 locale sitemaps; under the hold only the seed locale's first was read. Site-wide claims are stated against these 25 pages, which are not the site's newest.
- The 'Official EA Site' title suffix on twelve pages was treated as a tagline, not a second organisation name; the analyzer was corrected during this audit, as were the third-party-script classification (pl.ea.com is EA's own domain), the interface-state reading of 'the current item' and 'currently disabled', the click-opened careers modal, and the words-per-section count that included the site's menus. Each correction carries a regression test.
- The 24 model-judged checks were considered against the registry; those emitted and the reason each other one was not are in run.agent_review.
- The engagement axis grades usability proxies. Engagement itself is measured from visitor behaviour -- dwell time, return visits, scroll, clicks -- and a site audit has no visitor to observe.
- Whether an assistant retrieves anything at all for a given question is decided inside the engine and cannot be inferred from the site.
- Citation share is redistributive: it moves when competing pages (store listings, wikis, news) change, even if this site does not. We audited one candidate, never the pool.
- Which engine is asking changes the outcome; the reachability table is the only engine-specific fact a site crawl can settle, and here every engine's agents were served.
- 8 checks did not run; each has its reason in report.json under coverage.checks_skipped: STAY-016, TRUST-006, TRUST-007, TRUST-009, TRUST-010, TRUST-012, TRUST-013, TRUST-014
- Whether an assistant retrieves anything at all, what third-party sources say, which competitors share the retrieval pool, and how each engine reranks are all outside a single-site crawl.
