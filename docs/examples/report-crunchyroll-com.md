<!--
A real report of a single-page application behind a bot wall:
https://www.crunchyroll.com (seeded from /discover, which redirects to /),
12 September 2026, 25 pages. Retrieved read-only; live sites change.

Two critical findings and thirteen symptoms. REACH-005: Cloudflare challenges
every AI-crawler name while robots.txt names none of them; two control
requests -- an unknown name served, Bytespider refused -- show the rule keys on
crawler names. READ-001: the home page is an empty #root and the 21 browse
routes are one byte-identical 281 KB document carrying 99 words of chrome and
'update your web browser'. The agent promoted READ-001 to site-wide (the script
had 3 pages because the chrome cleared its word threshold), marked the thirteen
title/heading/breadcrumb/navigation findings as symptoms superseded by it, and
dropped 21 STAY-007 candidates raised on the app shell's loading overlay, a
READ-013 consent wall that was the empty shell, and a QUOTE-002 that had missed
the footer's own identity sentence. Each of those script misfires has since
been fixed and is covered by a test; the collector now sends the two control
names itself and renders a six-page sample when Playwright is installed.
-->

# AI-Readiness Audit — https://www.crunchyroll.com/

Crunchyroll is invisible to AI assistants twice over: Cloudflare challenges every AI-crawler name at the door, and anything that gets in is handed an empty app shell that says 'update your web browser' -- not one series, episode or plan is in the HTML.

| | Grade | Score |
|---|---|---|
| **Discoverability** — can AI assistants find, trust and cite you? | F | 23/100 |
| **Engagement** — do visitors who arrive stay? | A | 97/100 |

**16 findings:** 2 critical · 0 high · 8 medium · 6 low
Audited 2026-09-12T18:46:06Z · 25 pages sampled

## Which assistants can reach you

| Assistant | Status | What we measured |
|---|---|---|
| ChatGPT | **blocked** | the edge returns 403 to ChatGPT-User even though robots.txt permits it |
| Claude | **blocked** | the edge returns 403 to Claude-User even though robots.txt permits it |
| Perplexity | **blocked** | the edge returns 403 to PerplexityBot even though robots.txt permits it |
| Google AI Overviews / Gemini | **blocked** | the edge returns 403 to Googlebot even though robots.txt permits it |
| Microsoft Copilot | **partial** | Bingbot is permitted by robots.txt, but no request was made under that agent name, so whether the edge serves it is unverified |

## Fix these first

1. **Allow the AI retrieval agents through Cloudflare's bot rule and say so in robots.txt** — A settings change, and nothing else can be assessed until it is made. Training crawlers can stay blocked -- that is a licensing choice -- but ChatGPT-User, Claude-User and PerplexityBot fetch a page because a user asked about Crunchyroll, and today they get a JavaScript challenge. *(fixes F-001; effort: S)*
2. **Server-render the public catalogue and plan pages with per-route titles and TVSeries/TVEpisode markup** — The whole site is one shell to a machine. Pre-rendering the browse, series and plan routes puts the catalogue in the HTML and clears the twelve symptom findings beneath this one -- identical titles, no h1, no breadcrumbs, no in-content links. *(fixes F-002; effort: L)*
3. **Point the Anime Awards canonical at the www host** — One tag; the bare host it names redirects back to www. *(fixes F-011; effort: S)*

## Findings

### Can assistants get in?

#### F-001 · The server blocks AI crawlers even though robots.txt allows them  `critical`

**What we found.** https://www.crunchyroll.com/discover returns 200 (8,687 bytes) with a browser user-agent, but ChatGPT-User, Claude-User, ClaudeBot, GPTBot, PerplexityBot and Googlebot each receive a 403 Cloudflare JavaScript challenge ('Just a moment...', __cf_chl). robots.txt (39 lines) names none of these agents, so the block is a bot-management rule, not policy. Two control requests settle what kind: an unknown name, 'SomeRandomBot', is served the page (200), while Bytespider -- an AI crawler that cannot be verified by IP -- and plain curl are challenged. The rule keys on the user-agent name, which is how Cloudflare's AI-bot block behaves, rather than on impersonation of a verified bot. Whether the operator exempted verified retrieval agents by IP range cannot be seen from outside those ranges.

**Why it matters.** robots.txt states policy but the CDN enforces access. A crawler that is permitted in robots.txt and blocked at the edge never reaches the content, and nothing in the page can compensate.

**Fix.** Allow AI crawler user-agents through bot management
- In Cloudflare, open Security > Bots and check the 'Block AI bots' setting; if the intent is to refuse training crawlers only, switch to blocking unverified bots and allow the retrieval agents (ChatGPT-User, OAI-SearchBot, Claude-User, Claude-SearchBot, PerplexityBot, Perplexity-User)
- State the decision in robots.txt so policy and enforcement agree: Disallow GPTBot, ClaudeBot and CCBot if training is unwanted; leave retrieval agents allowed
- Re-test: curl -s -o /dev/null -w '%{http_code}' -A 'ChatGPT-User' https://www.crunchyroll.com/ should return 200, not 403

**Check it yourself.** `curl -s -o /dev/null -w '%{http_code}' -A 'ChatGPT-User' https://www.crunchyroll.com/ and compare with a browser user-agent`

#### F-011 · Canonical tags point to a different domain  `low`

**What we found.** https://www.crunchyroll.com/animeawards declares <link rel="canonical" href="https://crunchyroll.com/animeawards/"> -- the bare host, which 301-redirects to www. Same registrable domain, so no authority leaves the site, but the canonical names a URL that does not serve the page directly.

**Why it matters.** A cross-domain canonical tells indexes to credit the other domain, so this site accumulates none of the authority that would make it a preferred source.

**Fix.** Point canonicals at this domain unless syndication is intended
- Confirm whether the content is syndicated from the other domain deliberately
- If not, set a self-referential canonical on each page

**Check it yourself.** `curl -s https://www.crunchyroll.com/animeawards | grep -i 'rel="canonical"'`

### Can they read the page?

#### F-002 · Every sampled page is the application shell; the catalogue exists only after JavaScript runs  `critical`

**What we found.** All 25 sampled pages are client-rendered shells. The home page (and /discover, which 301s to it) is an 8,687-byte document with an empty <div id="root"> and 0 words. The 21 browse pages (/videos/popular, /videos/action, /simulcasts/seasons/summer-2026 ...) are one identical 281,222-byte document: the same 99 words of header and footer chrome, the same title, the same '7-Day Free Trial' heading, and a body-level message reading 'Update your web browser! Oh no! It looks like you're using a web browser we don't support!' -- the HTML tells any non-JavaScript client that it cannot be served. /games and /animeawards are Gatsby pages with 0 words. Not one series, episode, genre listing, plan or price appears in any page's HTML; there is no JSON-LD except a VideoGame block on /games. A retriever that does not execute JavaScript learns nothing about what Crunchyroll streams from any URL in the sample. (Inferred from raw-HTML signals; no renderer was available.)

**Why it matters.** Reading is stage two of the chain. A machine that gets in and finds an empty shell has nothing to parse, quote or trust; every other finding in this report is a symptom of this one.

**Fix.** Server-render the browse, series and plan pages, or ship a static HTML rendition for non-browser clients
- Pre-render the public catalogue routes (/videos/*, /simulcasts/*, /series/*, /watch/*) to HTML at build or edge time, with the title, synopsis, episode list and JSON-LD (TVSeries, TVEpisode, VideoObject) in the document
- Serve the pre-rendered HTML to every client, not only to a detected crawler list -- the edge already blocks the crawler names it would key on
- Give each route its own <title>, <h1> and description; today 21 routes share one title
- Keep the 'update your browser' message inside <noscript> rather than the visible body

**Check it yourself.** `curl -s https://www.crunchyroll.com/ | wc -w, then compare with the page in a browser`

#### F-005 · Heading structure does not describe the page  `medium`

**What we found.** 21 of 21 pages exhibit heading hierarchy breaks: 21 have no <h1>.

**Why it matters.** Headings define chunk boundaries during semantic retrieval; consistent hierarchy ensures snippets retain their parent topic context.

**Fix.** Structure content with hierarchical heading tags
- Ensure every page has exactly one distinct <h1> summarizing its subject
- Follow sequential descending levels (h1 -> h2 -> h3) without skipping intermediate ranks
- Avoid using heading tags merely for visual styling

**Check it yourself.** `curl -s https://www.crunchyroll.com/simulcasts/seasons/spring-2026 | grep -oE '<h[1-6]'`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-006 · Character encoding or language is undeclared  `medium`

**What we found.** 0 pages declare no charset in headers or meta; 23 pages declare no lang attribute.

**Why it matters.** Explicit declarations ensure language identification models process content accurately without misinterpreting characters.

**Fix.** Declare UTF-8 charset and document language
- Add <meta charset="utf-8"> as the first child of <head>
- Add lang="en" (or appropriate language code) to the <html> tag
- Include charset=utf-8 in the server Content-Type response header

**Check it yourself.** `curl -sI https://www.crunchyroll.com/videos/popular | grep -i content-type`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-012 · A JavaScript-dependent page offers no noscript fallback  `low`

**What we found.** 4 client-rendered pages contain no substantive noscript fallback content.

**Why it matters.** A substantive noscript block provides baseline text when crawlers or user agents do not run script engines.

**Fix.** Provide accessible noscript fallback or implement SSR
- Add a <noscript> element containing core identity, navigation, and page text summary
- Migrate client-only routes to server-side rendering as the permanent architectural solution

**Check it yourself.** `curl -s https://www.crunchyroll.com/ | grep -c '<noscript'`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-013 · The page uses no semantic landmarks  `low`

**What we found.** 4 pages contain no <main>, <article> or <nav> element or equivalent ARIA landmark role.

**Why it matters.** Semantic landmarks allow content extractors to reliably strip repetitive navigation and isolate primary body text.

**Fix.** Add HTML5 landmark elements to template layouts
- Wrap the primary page content in a <main> landmark element
- Wrap navigation menus in <nav> and header sections in <header>
- Use <article> for standalone self-contained posts or documentation entries

**Check it yourself.** `curl -s https://www.crunchyroll.com/ | grep -cE '<(main|article|nav|header|footer)'`

*Downstream of READ-001 — fixing that may resolve this.*

### Can they parse facts out?

#### F-003 · Titles and meta descriptions are missing, duplicated or conflicting  `medium`

**What we found.** 23 of 25 pages share duplicate titles: e.g. 2 pages share 'crunchyroll'.

**Why it matters.** Duplicated titles cause search engines to treat pages as identical variants.

**Fix.** Make page titles distinct and unique
- Ensure every URL template generates a distinct title naming the specific page subject

**Check it yourself.** `curl -s https://www.crunchyroll.com/ | grep -i '<title>'`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-004 · No breadcrumb markup or navigation  `medium`

**What we found.** 21 of 25 pages declare no BreadcrumbList and show no breadcrumb navigation.

**Why it matters.** Breadcrumbs state the hierarchical context of deep pages, helping AI agents understand where facts sit in relation to parent topics.

**Fix.** Add BreadcrumbList structured data and navigation trail
- Render breadcrumb navigation linking parent category paths
- Add BreadcrumbList JSON-LD markup indicating hierarchy position

**Check it yourself.** `Open https://www.crunchyroll.com/videos/popular and look for a breadcrumb trail`

*Downstream of READ-001 — fixing that may resolve this.*

### Do visitors who arrive stay?

#### F-007 · Pages do not continue the conversation visitors arrive from  `medium`

**What we found.** All 25 sampled pages are broad entry points (home/about/category); no FAQ, pricing, product or article page exists for an assistant to link a visitor straight to. The home page opens with "".

**Why it matters.** A visitor arriving from an AI answer already holds a specific question. Landing them on a page that restarts from the top loses them even though every upstream stage worked.

**Fix.** Build a deep-linkable page for each question the site's content implies
- List the specific questions your category's buyers ask (from sales and support), not a generic list
- Give each its own URL with the answer in the first screen
- These are the pages an assistant cites and the pages a referred visitor should land on

**Check it yourself.** `Ask an assistant about something this site covers, follow the link it gives, and see whether that page answers the question you asked`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-008 · No clear next action  `medium`

**What we found.** https://www.crunchyroll.com/ is a home page with no in-content link, no form and no call-to-action text -- nothing tells the visitor what to do next.

**Why it matters.** A conversion page with no action is a dead-end even when the content is persuasive.

**Fix.** Add one primary call to action to this page
- Decide the one step this page should drive (start trial, contact sales, view a plan)
- Add it as a prominent button in the first screen
- Link it to the page that completes that step

**Check it yourself.** `Open https://www.crunchyroll.com/ and identify the single action it wants from you`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-009 · Pages dead-end with nowhere to go next  `medium`

**What we found.** 4 of 25 content pages carry no in-content internal link beyond global navigation: https://www.crunchyroll.com/, https://www.crunchyroll.com/animeawards, https://www.crunchyroll.com/games, https://www.crunchyroll.com/welcome.

**Why it matters.** A visitor who finishes a page with no onward link in front of them leaves rather than hunting the navigation for what to read next.

**Fix.** End each page with a relevant onward link in the content
- Add 2-3 contextual links in the body or a 'next' block -- to the pricing page from a feature page, to related articles from a post
- These are in-content links, not the header nav
- The home page especially must lead somewhere specific

**Check it yourself.** `Read to the end of https://www.crunchyroll.com/ and look for a next step`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-010 · Visitors cannot tell where they are in the site  `medium`

**What we found.** 3 of 3 sampled pages at URL depth 3 or greater show no breadcrumb or section navigation in the HTML.

**Why it matters.** A visitor who lands deep from a search or an AI link needs to see where they are to trust the page and to explore sideways rather than bounce.

**Fix.** Add a breadcrumb trail to pages more than two levels deep
- Render a breadcrumb (Home / Section / Page) at the top of deep pages
- Mirror it as BreadcrumbList JSON-LD
- Keep the current section highlighted in the primary nav

**Check it yourself.** `Open https://www.crunchyroll.com/simulcasts/seasons/spring-2026 directly and try to identify which section it belongs to`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-014 · Images without dimensions risk layout shift  `low`

**What we found.** On https://www.crunchyroll.com/videos/popular, 3 of the first 3 images (the best available proxy for above-the-fold) declare neither width nor height; 126 of 126 images site-wide lack dimensions. Reserving no space for them risks layout shift as they load.

**Why it matters.** An image with no reserved space pushes content down when it loads, and a visitor who was about to click the thing that moved is a visitor who mis-clicks and leaves.

**Fix.** Declare width and height (or aspect-ratio) on every content image
- Add width and height attributes matching the image's intrinsic size
- Or set aspect-ratio in CSS on the image container
- Prioritise images in the first screen, where a shift is most jarring

**Check it yourself.** `curl -s <page> | grep -c '<img' and compare with the count carrying a width attribute`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-015 · The viewport is fixed-width or blocks zoom  `low`

**What we found.** 2 sampled page(s) set a zoom-disabled viewport.

**Why it matters.** A fixed-width viewport forces horizontal scrolling on phones; disabling zoom locks out anyone who needs to enlarge text.

**Fix.** Use a responsive, zoomable viewport
- Set content="width=device-width, initial-scale=1"
- Remove user-scalable=no and maximum-scale=1

**Check it yourself.** `curl -s https://www.crunchyroll.com/ | grep -i 'name="viewport"'`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-016 · Accessibility basics are missing  `low`

**What we found.** Limited mechanical check (not a full accessibility audit): 4 page(s) use no landmark elements (<main>, <nav>, <header>, <footer>).

**Why it matters.** Unlabelled fields and missing landmarks make the page unusable with a screen reader or keyboard, and those visitors leave immediately.

**Fix.** Fix the mechanical accessibility basics
- Give every input a <label for> (or an aria-label)
- Wrap the page regions in <header>, <nav>, <main>, <footer>
- Then run a full accessibility audit -- this check only covers the mechanical minimum

**Check it yourself.** `Tab through https://www.crunchyroll.com/ using only the keyboard`

*Downstream of READ-001 — fixing that may resolve this.*

## Worth doing even though nothing is broken

- **Publish an llms.txt pointing at the site's key facts** — GET https://www.crunchyroll.com/llms.txt returned 404. This is an emerging convention rather than an established requirement, but it costs almost nothing and forces a useful exercise: naming the handful of pages carrying the facts most worth quoting.
- **Server-render the pages that carry commercial facts** — Rendering strategy can be chosen per route. Pricing, product and about pages carry the facts worth quoting and benefit most; an authenticated dashboard does not need to change at all.
- **Build a landing page for each question assistants are likely to cite** — The 25 sampled pages include no FAQ, pricing, product or article page -- nothing question-shaped for a referred visitor to land on directly.
- **Check whether the news section is server-rendered, and sample it next** — The sitemap index lists news sitemaps in eleven locales (sitemaps/news/en-US/latest.xml and others) that this sample never reached, because the 25 slots went to the browse routes. If the news articles are static HTML they are the one part of the site a machine can read today, and the place to put the plan and catalogue facts until the app routes are rendered.

## What this audit did not cover

- No browser renderer was available, so JavaScript dependency is inferred from raw HTML rather than measured. The shell verdict rests on 21 routes returning one identical 281,222-byte document and the home page an empty #root; a renderer would show the catalogue a visitor sees, and would not change what a non-rendering client receives.
- The sample is 25 of 391 discovered URLs: the home page, 21 browse routes from sitemaps/videos.xml and sitemaps/simulcasts.xml, /games, /animeawards and /welcome. No /series/, /watch/, plan, news or help page was sampled; the news section (eleven locale sitemaps) may be server-rendered and was not examined.
- The user-agent probe ran from one address. Cloudflare challenged every AI-crawler name and served an unknown bot name; a verified-bot IP exemption, if configured, cannot be observed from outside those ranges.
- Thirteen findings are symptoms of READ-001 and are kept at reduced weight; the twelve model-judged checks that need page content are recorded as skipped, not clean.
- Off-site corroboration (TRUST-007/009/012/013) was completed with one web search on 2026-09-13 and is model-judged; TRUST-006 is moot because the HTML makes no claim.
- The engagement axis grades usability proxies measured on the served HTML, which here is the application shell; engagement itself is measured from visitor behaviour, which a site audit cannot see.
- Whether an assistant retrieves anything at all for a given question is decided inside the engine; here retrieval fails at the edge before the site's content matters.
- For 'is Crunchyroll worth it' and 'what does Crunchyroll cost' assistants cite reviewers (CableTV.com, evoca.tv) because the site's HTML carries neither answer.
- Citation share is redistributive: it moves when competing pages change, even if this site does not. We audited one candidate, never the pool.
- 14 checks did not run; each has its reason in report.json under coverage.checks_skipped: PARSE-012, QUOTE-003, QUOTE-004, QUOTE-006, QUOTE-007, QUOTE-008, QUOTE-011, QUOTE-012, READ-004, READ-011, STAY-016, TRUST-002 and 2 more
- Whether an assistant retrieves anything at all, what third-party sources say, which competitors share the retrieval pool, and how each engine reranks are all outside a single-site crawl.
