<!--
A real report, produced the way the marketplace is meant to be used: an agent
following audit-orchestrator/SKILL.md -- collect once, profile the site,
dispatch six skills, finish the model-judged checks against the bundle, review
every candidate against the registry guards, merge, score, plan, emit, validate.

Target: https://www.nike.in, 12 September 2026, 25 pages at the default budget
(home, help centre, 7 category pages, 14 product pages). Everything here was
retrieved read-only at that moment; live sites change.

What the agent overrode, all recorded in report.json under run.agent_review:
dropped nine STAY-006 candidates (filter state does reach the URL -- the site's
own links carry ?f=), a TRUST-010 that had read trouser sizes as phone numbers,
a READ-013 "consent wall" that was an empty React shell, and a REACH-013 whose
"orphans" were sitemap index files. Added PARSE-004 (Product markup with a
template description and the product line as the brand), TRUST-010 (Nike, Inc.'s
US contact point on a store sold by Nykaa Fashion), READ-011 (fabric, care and
sizing only in the hydration script), TRUST-005 (an app-offer banner whose terms
expired five days earlier) and STAY-016 (0.0-star badges on every featured tile).
Off-site checks ran with two web searches. The first crawl of this site also
exposed four collector defects, since fixed and tested; the report reflects the
corrected bundle.
-->

# AI-Readiness Audit — https://www.nike.in

nike.in sells legibly -- every product page carries a price a machine can read -- but the pages that answer 'who runs this store, how do returns work, how fast is delivery' are either invisible to crawlers or attributed to nykaa.com.

| | Grade | Score |
|---|---|---|
| **Discoverability** — can AI assistants find, trust and cite you? | C | 70/100 |
| **Engagement** — do visitors who arrive stay? | A | 93/100 |

**19 findings:** 0 critical · 1 high · 13 medium · 5 low
Audited 2026-09-12T14:30:29Z · 25 pages sampled

## Which assistants can reach you

| Assistant | Status | What we measured |
|---|---|---|
| ChatGPT | **partial** | unverified: the edge returned 403 to ChatGPT-User, but it returned 403 to the browser baseline as well, so the refusal cannot be attributed to the agent name; robots.txt permits it |
| Claude | **partial** | unverified: the edge returned 403 to Claude-User, but it returned 403 to the browser baseline as well, so the refusal cannot be attributed to the agent name; robots.txt permits it |
| Perplexity | **partial** | unverified: the edge returned 403 to PerplexityBot, but it returned 403 to the browser baseline as well, so the refusal cannot be attributed to the agent name; robots.txt permits it |
| Google AI Overviews / Gemini | **partial** | unverified: the edge returned 403 to Googlebot, but it returned 403 to the browser baseline as well, so the refusal cannot be attributed to the agent name; robots.txt permits it |
| Microsoft Copilot | **partial** | Bingbot is permitted by robots.txt, but no request was made under that agent name, so whether the edge serves it is unverified |

## Fix these first

1. **Server-render /help-center and point its canonical at nike.in, not nykaa.com** — One page, three findings, and it is the page every buyer question resolves to. Today its HTML is an empty <div id="app"> with a canonical to http://www.nykaa.com/help-center, so an assistant asked about nike.in's returns or delivery either finds nothing or cites Nykaa. Server-rendering the FAQ text and fixing one <link> tag makes the whole policy class quotable. *(fixes F-001, F-008, F-006; effort: M)*
2. **Remove the conflicting noindex from the three campaign collection pages and stop emitting duplicate robots meta tags** — Nike 24.7 and 'Don't Lose Your Cool' are the home-page hero campaigns, and their collection pages carry noindex,nofollow twice and index,follow once. The most restrictive wins. The hydration state shows an empty CMS title on exactly these pages, so filling the record likely clears it; deduplicating the tag prevents the next one. *(fixes F-007; effort: S)*
3. **State who operates nike.in in one visible sentence, and give the site-wide Organization block the Indian store's contact point** — A machine reading this site sees Nike, Inc. of Beaverton with a US 1-800 number in markup and 'Sold By Nykaa Fashion Ltd' in the page. The press already reports the arrangement; the site should say it once, in text and in JSON-LD, so the two organisations resolve to one store with one support line. *(fixes F-005, F-014; effort: S)*
4. **Give category pages their own titles and Product markup its real description, brand and colour** — Two template edits. Seven category pages share one generic title today; the h1 already holds the right name. Fifteen Product blocks describe themselves with a sales slogan and name the product line as the brand, while the real copy, colour and style code sit unmarked on the same page. *(fixes F-003, F-002; effort: S)*
5. **Render the product-details panel and size chart into the HTML instead of only the hydration script** — Material, care, fit and sizing are the facts a shopper asks an assistant to compare, and on 13 of 14 product pages they exist only as escaped JSON inside a <script>. The page already has the data; it needs to be emitted as markup, collapsed by CSS. *(fixes F-009; effort: M)*

## Findings

### Can assistants get in?

#### F-001 · Canonical tags point to a different domain  `high`

**What we found.** https://www.nike.in/help-center declares <link rel="canonical" href="http://www.nykaa.com/help-center"> -- a different registrable domain, and over plain http. The page is the site's only FAQ-shaped page (shipping, returns, payments) and is linked from the header of every sampled page. Any engine that honours the canonical attributes it to nykaa.com and drops nike.in's copy from its index, so a question about nike.in's return policy is answered from Nykaa's page or not at all.

**Why it matters.** A cross-domain canonical tells indexes to credit the other domain, so this site accumulates none of the authority that would make it a preferred source.

**Fix.** Point canonicals at this domain unless syndication is intended
- Set the canonical on /help-center to https://www.nike.in/help-center (the help-center template appears to be shared with nykaa.com and inherits its canonical)
- Grep every shared template for 'nykaa.com' in <link rel="canonical"> and og:url

**Check it yourself.** `curl -s https://www.nike.in/help-center | grep -i 'rel="canonical"'`

#### F-007 · Content pages are excluded from search indexes  `medium`

**What we found.** 3 of 25 sampled pages carry <meta name="robots" content="noindex, nofollow"> (twice, via react-helmet) followed by a third tag saying "index, follow": https://www.nike.in/nike-24-7/c/113240, https://www.nike.in/don-t-lose-your-cool/c/111353 and https://www.nike.in/looks-of-jordan/c/98712. Crawlers combine conflicting directives and honour the most restrictive, so these pages are excluded. All three are campaign collection pages linked from the home-page hero (Nike 24.7 and 'Don't Lose Your Cool' are this season's lead stories), and the same three pages carry an empty CMS title (the hydration state shows metaData: {title: "", noindex: true, nofollow: true}), which suggests the noindex is a default for unfilled metadata rather than a decision.

**Why it matters.** A noindexed page is absent from the index assistants query, so it cannot be surfaced regardless of how well written it is.

**Fix.** Remove noindex from content pages
- In the category CMS record for c/113240, c/111353 and c/98712, fill the SEO title and set the index flag; confirm the noindex default is intended only for empty records
- Emit exactly one <meta name="robots"> per page -- remove the react-helmet duplicate so index and noindex can never both appear
- Re-fetch each page and check that only 'index, follow' remains

**Check it yourself.** `curl -s https://www.nike.in/nike-24-7/c/113240 | grep -o '<meta[^>]*name="robots"[^>]*>'`

### Can they read the page?

#### F-008 · Page content is missing from the HTML a crawler receives  `medium`

**What we found.** https://www.nike.in/help-center returns a 35 KB document whose <body> is <div id="app"></div><div id="portal-root"></div> plus six scripts: zero words of body text, no <noscript> fallback, no <title>. This is the one page on the site that answers shipping, delivery-time, return and payment questions, and every other sampled page links to it under 'Know More'. The 24 other sampled pages are server-rendered. (Inferred from raw-HTML signals; no browser renderer was available.)

**Why it matters.** Retrieval crawlers do not execute JavaScript before extracting content; server-rendering ensures facts are readable upon fetch.

**Fix.** Server-render /help-center so its answers exist in the HTML
- Configure server-side rendering (SSR) or static pre-rendering (SSG) for content routes
- Ensure headings, copy, and commercial specifications exist directly in the initial HTML response
- Verify with curl that visible text is present in the response from https://www.nike.in/help-center

**Check it yourself.** `curl -s https://www.nike.in/help-center | wc -w, then compare with the page in a browser`

#### F-009 · Product details, fabric composition and the size chart exist only in the JavaScript state  `medium`

**What we found.** On 13 of the 14 sampled product pages the 'View Product Details' control has no panel text in the HTML. The fabric composition ('51% polyester/25% modal/15% cotton/9% elastane'), care ('Machine wash'), features ('A signature locker loop on the back collar'), the attribute table (Fit: Loose, Neckline: Crew Neck, Nike Material: Nike ImpossiblySoft, Nike Technology: Dri-FIT) and the size chart (chest 33.5-36 in for size S ...) are present only as escaped strings inside the hydration <script>, never as markup. Words like 'polyester' and 'cotton' appear 5 times in each page's source and 0 times in its extractable text. Name, price, the two-sentence copy, colour, style code and country of origin are in the HTML, so the primary content is readable; the facts a buyer compares on -- material, fit, care, sizing -- are not. No renderer was available to confirm the panel renders on click, hence medium confidence.

**Why it matters.** A retriever indexes the HTML text it receives; a fact that exists only in a JSON blob inside a script is invisible to it. Material, fit and sizing are exactly the facts a shopper asks an assistant to compare.

**Fix.** Render the product-details panel and size chart into the HTML, collapsed by CSS
- Server-render pdp_sections (Product details, Pack contains, size_data) inside the page as a <details>/<summary> or a hidden <section>, and let the existing control toggle visibility
- Add the composition, care and fit lines to the Product JSON-LD as material and additionalProperty so they are extractable twice over
- Confirm with curl that 'polyester' appears outside <script> on an apparel page

**Check it yourself.** `Fetch https://www.nike.in/nike-24-7-impossiblysoft-men-s-dri-fit-crew/p/24852262, strip every <script> block, and grep for 'polyester' (expect 0 hits); then open the page, click 'View Product Details' and read the composition line`

#### F-015 · A JavaScript-dependent page offers no noscript fallback  `low`

**What we found.** 1 client-rendered pages contain no substantive noscript fallback content.

**Why it matters.** A substantive noscript block provides baseline text when crawlers or user agents do not run script engines.

**Fix.** Provide accessible noscript fallback or implement SSR
- Add a <noscript> element containing core identity, navigation, and page text summary
- Migrate client-only routes to server-side rendering as the permanent architectural solution

**Check it yourself.** `curl -s https://www.nike.in/help-center | grep -c '<noscript'`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-016 · Heading structure does not describe the page  `low`

**What we found.** 8 of 24 pages exhibit heading hierarchy breaks: 8 skip heading levels.

**Why it matters.** Headings define chunk boundaries during semantic retrieval; consistent hierarchy ensures snippets retain their parent topic context.

**Fix.** Structure content with hierarchical heading tags
- Ensure every page has exactly one distinct <h1> summarizing its subject
- Follow sequential descending levels (h1 -> h2 -> h3) without skipping intermediate ranks
- Avoid using heading tags merely for visual styling

**Check it yourself.** `curl -s https://www.nike.in/ | grep -oE '<h[1-6]'`

#### F-017 · The page uses no semantic landmarks  `low`

**What we found.** 1 pages contain no <main>, <article> or <nav> element or equivalent ARIA landmark role.

**Why it matters.** Semantic landmarks allow content extractors to reliably strip repetitive navigation and isolate primary body text.

**Fix.** Add HTML5 landmark elements to template layouts
- Wrap the primary page content in a <main> landmark element
- Wrap navigation menus in <nav> and header sections in <header>
- Use <article> for standalone self-contained posts or documentation entries

**Check it yourself.** `curl -s https://www.nike.in/help-center | grep -cE '<(main|article|nav|header|footer)'`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-018 · Corrupted character encoding (mojibake) in page text  `low`

**What we found.** 1 pages contain corrupted encoding sequences (mojibake) in visible text.

**Why it matters.** Mojibake garbles entity names and breaks word tokenization in retrieval models.

**Fix.** Fix encoding pipeline to output clean UTF-8 text
- Ensure source files and database connections use UTF-8 encoding
- Verify HTTP responses declare Content-Type: text/html; charset=utf-8

**Check it yourself.** `curl -sI https://www.nike.in/nike-sportswear/c/93992?transaction_id=82e42e5e9bffe0a7d2d175ffb322f48b | grep -i content-type`

### Can they parse facts out?

#### F-002 · Product markup carries a template description and the product line as the brand  `medium`

**What we found.** All 15 Product entities across the 14 sampled product pages have name, sku, image and a complete Offer (INR price, availability, condition) -- the required set is present. But 'description' is the same template on every one: 'Shop for genuine {name} online at best prices on Nike India with great offers', which repeats the name and states no fact, while the visible page carries the real copy ('springy cushioning and a seamless lining'), the colour ('Black|Anthracite'), the style code (IR0447-001) and the country of origin. 'brand.name' is the product line -- 'Nike 24.7', 'Nike 24.7 ImpossiblySoft', 'Nike 24.7 PerfectStretch' -- not 'Nike', so an entity extractor sees four brands. No color, material, size, gtin or aggregateRating is declared.

**Why it matters.** The Offer already lets a machine extract price and stock. The description and brand are the fields it would quote when describing the product, and today they yield a sales slogan and a brand that does not exist.

**Fix.** Fill Product.description from the product copy and set brand to Nike
- Map Product.description to the product's own copy block (the text under 'View Product Details'), not the SEO template
- Set brand to {"@type": "Brand", "name": "Nike"} and put the line name (24.7, ImpossiblySoft) in the name or a 'model' property
- Add color, material and countryOfOrigin from the fields already on the page; add size via hasVariant or an offers array when the size grid is known server-side

**Check it yourself.** `curl -s https://www.nike.in/nike-24-7-men-s-shoes/p/27763425 | grep -o '"description": "[^"]*"' and compare with the copy on the page`

#### F-003 · Titles and meta descriptions are missing, duplicated or conflicting  `medium`

**What we found.** 1 of 25 pages have no title tag: https://www.nike.in/help-center. Observed on 8 of 25 sampled pages: https://www.nike.in/help-center, https://www.nike.in/air-max/c/94031?transaction_id=10d8894a4395c0f00943db977f12cb44, https://www.nike.in/don-t-lose-your-cool/c/111353....

**Why it matters.** The title tag is the principal label used by indexers and AI agents to understand the topic of a page.

**Fix.** Add descriptive title tags to all pages
- Add unique, relevant <title> elements to page templates

**Check it yourself.** `curl -s https://www.nike.in/help-center | grep -i '<title>'`

#### F-004 · No breadcrumb markup or navigation  `medium`

**What we found.** 23 of 25 pages declare no BreadcrumbList and show no breadcrumb navigation.

**Why it matters.** Breadcrumbs state the hierarchical context of deep pages, helping AI agents understand where facts sit in relation to parent topics.

**Fix.** Add BreadcrumbList structured data and navigation trail
- Render breadcrumb navigation linking parent category paths
- Add BreadcrumbList JSON-LD markup indicating hierarchy position

**Check it yourself.** `Open https://www.nike.in/cp/app-offer-tnc and look for a breadcrumb trail`

### Can they quote a clear fact?

#### F-005 · The site never states plainly what the organization is  `medium`

**What we found.** No sampled page carries a sentence saying what nike.in is. The nearest is a nav label on the home page, 'Nike Official Online Store India', and the meta/JSON-LD line 'Nike - Official Online Store for Athletic Shoes, Clothing & Sports Gear'. Meanwhile the Corporation block on every page describes Nike, Inc. of Beaverton, Oregon, while all 14 product pages state 'Sold By Nykaa Fashion Ltd'. Independent coverage (Inc42, Indian Retailer, Feb 2026) reports that Nike handed nike.in's operation to Nykaa; the site itself never says so. A machine asked 'is nike.in the official Nike store, and who runs it?' finds two organisations and no sentence joining them. Severity lowered from the registry's 'high' because Nike itself needs no introduction; the store does.

**Why it matters.** An assistant asked 'what is Nike?' quotes the sentence on the page that answers it. With no such sentence it infers one, or names a competitor whose identity line was explicit.

**Fix.** State in one visible sentence what nike.in is and who operates it
- Add to the home-page footer and the help centre: 'Nike.in is Nike's official online store for India, operated by Nykaa Fashion Ltd, which sells and ships every order.'
- Repeat the sentence as the Corporation/Organization 'description' in JSON-LD so the markup and the page agree

**Check it yourself.** `Open https://www.nike.in/ and https://www.nike.in/cp/terms-conditions and look for one sentence naming the store, its operator and its country`

#### F-006 · Common buyer questions have no answer on the site  `medium`

**What we found.** Of the questions a buyer on an Indian apparel store asks, the sample answers two as fragments and the rest not at all. Product pages carry the labels '14-day return and size exchange' and 'Free delivery available', each followed by a 'Know More' link into /help-center -- which is a JavaScript shell with no text (READ-001). No sampled page states delivery time, accepted payment methods or cash on delivery, how an exchange works, or how authenticity is guaranteed. Independent press already states 'free shipping on all orders, free exchanges, 2-day delivery in metros'; the site's own crawlable text does not. Sampled pages only: an answer may exist on an unsampled page.

**Why it matters.** Assistants match a user's question to a passage phrased like an answer to it. Without Q&A content there is nothing to match, so the brand is absent from those answers.

**Fix.** Answer the handful of questions buyers actually ask, one per heading
- List the 5-8 questions sales and support field most often
- Answer each in 40-80 words under its own question-phrased heading
- Repeat enough of the question in the answer that it stands alone

**Check it yourself.** `curl -s https://www.nike.in/help-center | grep -c 'delivery' (expect 0); then open the page in a browser and count the answers`

*Downstream of READ-001 — fixing that may resolve this.*

### Will they trust and repeat it?

#### F-013 · Every page advertises an app offer whose own terms say it expired five days ago  `medium`

**What we found.** All 25 sampled pages open with the banner 'Enjoy 15% Off On The Nike App. Use: APP15 Download Now T&Cs'. The linked terms page, https://www.nike.in/cp/app-offer-tnc, states 'The offer is valid till 7th September, 2026 11:59 PM'. The crawl ran on 12 September 2026. The banner presents the offer as current; confirm whether the offer was extended and the terms page is stale, or the offer ended and the banner is stale. Either way the two pages contradict each other today, and a machine that quotes the discount will quote one that its own source says is over.

**Why it matters.** Freshness is judged from internal consistency when no dates are shown. A site-wide claim contradicted by its own terms page is the clearest possible signal that the content is not maintained.

**Fix.** Tie the promo banner to the offer's end date so both retire together
- Update the T&C validity date if the offer was extended; otherwise remove the APP15 banner from the site-wide header
- Give the banner component an end-date field read from the same record as the T&C, so a banner cannot outlive its terms

**Check it yourself.** `curl -s https://www.nike.in/cp/app-offer-tnc | grep -o 'valid till[^.]*' and compare with today's date and the banner on the home page`

#### F-014 · Structured data gives Nike, Inc.'s US contact details for a store sold by Nykaa Fashion  `medium`

**What we found.** Every sampled page embeds a Corporation block for 'Nike, Inc.' at One Bowerman Drive, Beaverton, Oregon with contactPoint telephone +1-800-806-6453 and email support@nike.com. The visible seller on all 14 product pages is 'Nykaa Fashion Ltd', and the visible importer is 'Nike India Private Limited'. No Indian customer-care number or email appears in any sampled page's text (the help centre is a JS shell). A machine extracting 'how to contact nike.in support' returns Nike's US consumer line, which does not handle Indian orders.

**Why it matters.** Contact facts are among the most literally repeated by assistants. When the only machine-readable contact point on the site belongs to a different organisation in a different country, the repeated fact is wrong.

**Fix.** Give the site-wide Organization block the Indian store's own contact point
- Replace the Corporation contactPoint with the nike.in customer-care number and email that the help centre actually publishes, areaServed 'IN'
- Model the relationship explicitly: Organization 'Nike.in' with parentOrganization Nike, Inc. and a 'seller'/'provider' of Nykaa Fashion Ltd, so the markup matches the vendor details on the page

**Check it yourself.** `curl -s https://www.nike.in/ | grep -o '"telephone": "[^"]*"' then compare with the seller named under 'Vendor details' on any product page`

### Do visitors who arrive stay?

#### F-010 · Images without dimensions risk layout shift  `medium`

**What we found.** On https://www.nike.in/, 2 of the first 3 images (the best available proxy for above-the-fold) declare neither width nor height; 35 of 367 images site-wide lack dimensions. Reserving no space for them risks layout shift as they load.

**Why it matters.** An image with no reserved space pushes content down when it loads, and a visitor who was about to click the thing that moved is a visitor who mis-clicks and leaves.

**Fix.** Declare width and height (or aspect-ratio) on every content image
- Add width and height attributes matching the image's intrinsic size
- Or set aspect-ratio in CSS on the image container
- Prioritise images in the first screen, where a shift is most jarring

**Check it yourself.** `curl -s <page> | grep -c '<img' and compare with the count carrying a width attribute`

#### F-011 · Accessibility basics are missing  `medium`

**What we found.** Limited mechanical check (not a full accessibility audit): 28 form input(s) across 7 page(s) have no associated <label>, aria-label or title; 1 page(s) use no landmark elements (<main>, <nav>, <header>, <footer>).

**Why it matters.** Unlabelled fields and missing landmarks make the page unusable with a screen reader or keyboard, and those visitors leave immediately.

**Fix.** Fix the mechanical accessibility basics
- Give every input a <label for> (or an aria-label)
- Wrap the page regions in <header>, <nav>, <main>, <footer>
- Then run a full accessibility audit -- this check only covers the mechanical minimum

**Check it yourself.** `Tab through https://www.nike.in/air-max/c/94031?transaction_id=10d8894a4395c0f00943db977f12cb44 using only the keyboard`

#### F-012 · Every featured product on the home page shows an empty rating, 0.0 (0)  `medium`

**What we found.** The home page renders a rating widget on all 24 featured product tiles, and every one reads '★ 0.0 (0)' -- Giannis Freak 8, Air Jordan Mule SE, Pegasus 42 and the rest. The product pages' configuration has ratingReviewEnabled: false and reviews: {data: []}, so the widget can never fill. A zero-star, zero-review badge next to the season's lead products reads as 'nobody has bought this' at the moment a visitor decides whether to click. The product pages themselves do carry trust signals near 'Add to Bag' -- 14-day returns, free delivery, the named seller -- so this is confined to the tiles.

**Why it matters.** Do not add reviews the store does not collect; stop displaying the absence of them as a score. An empty rating is a trust signal pointing the wrong way at the point of decision.

**Fix.** Hide the rating badge on tiles when the review count is zero
- In the product-tile component, render the star/count element only when count > 0
- If reviews stay disabled site-wide (ratingReviewEnabled: false), remove the element from the tile template entirely rather than showing an empty one

**Check it yourself.** `Open https://www.nike.in/ and count the product tiles showing 0.0 (0)`

#### F-019 · The viewport is fixed-width or blocks zoom  `low`

**What we found.** 10 sampled page(s) set a zoom-disabled viewport.

**Why it matters.** A fixed-width viewport forces horizontal scrolling on phones; disabling zoom locks out anyone who needs to enlarge text.

**Fix.** Use a responsive, zoomable viewport
- Set content="width=device-width, initial-scale=1"
- Remove user-scalable=no and maximum-scale=1

**Check it yourself.** `curl -s https://www.nike.in/ | grep -i 'name="viewport"'`

## Worth doing even though nothing is broken

- **Publish an llms.txt pointing at the site's key facts** — GET https://www.nike.in/llms.txt returned 404. This is an emerging convention rather than an established requirement, but it costs almost nothing and forces a useful exercise: naming the handful of pages carrying the facts most worth quoting.
- **Phrase section headings as the questions people actually ask** — 0 of 351 headings across 24 sampled pages are phrased as a question. Assistants answer questions, and a heading that states the question makes the passage beneath it an answer to retrieve rather than prose to summarise. This is a recommendation, not a defect: whether a query reaches the site at all is decided inside the engine and cannot be measured from here.
- **Show an honest update date on pages that change** — 24 of 24 sampled content pages carry no visible published or updated date, though the site's content reads as current. A truthful update date lets a consumer prefer the page over an older competing source.
- **Confirm in Akamai Bot Manager that AI retrieval agents are allowed, and verify with the vendor's bot report** — The probe could not settle it: the edge returned 403 to ChatGPT-User, Claude-User, PerplexityBot and a plain Chrome UA alike, while serving the audit's own UA. robots.txt allows everything except search, checkout and filter URLs, so policy and enforcement may disagree without anyone having decided.
- **Fetch the second level of the sitemap index so products are discoverable without crawling** — /sitemap-v2/sitemap-index.xml points to sitemap-categories-index.xml and sitemap-products-index.xml, which in turn point to sitemap-categories-1.xml and sitemap-products-1.xml. A two-level index is valid, but this audit's collector (and some fetchers) stop at one level and saw zero page URLs. Flattening to one index that lists the leaf sitemaps directly removes the extra hop.

## What this audit did not cover

- No browser renderer was available, so JavaScript dependency is inferred from raw HTML rather than measured.
- The user-agent probe is inconclusive: Akamai Bot Manager returned 403 to a plain Chrome UA and to every AI-agent name, while serving the audit's own UA. Whether genuine retrieval agents from their published IP ranges are admitted cannot be measured from outside those networks; the engine table says 'partial / unverified' for that reason, and no REACH-005 finding is made.
- The sample is 25 of 375 discovered URLs: the home page, the help centre, one offer-terms page, 7 category pages and 14 product pages from the Nike 24.7 line. 37 URLs carrying ?root=, ?ptype= or ?f= were skipped because robots.txt disallows them. No terms, privacy, store-locator or Jordan product page was sampled.
- The sitemap index nests two levels deep and the collector follows one, so sitemap entries contributed nothing to page selection and TRUST-003 (lastmod honesty) had nothing to test.
- The engagement axis grades usability proxies. Engagement is measured from visitor behaviour -- dwell time, return visits, scroll, clicks -- and a site audit has no visitor to observe.
- The fifteen model-judged checks the scripts leave to the agent (QUOTE-003/004/007/008/011/012, STAY-001/002/016, TRUST-005/015, READ-004/006/011, PARSE-012) were completed by reading each analyzer's registry and inspecting the bundle; three fired and the judgment for each of the others is recorded in run.agent_review.
- Off-site corroboration (TRUST-006/007/009/012/013) was completed by the agent with a web search tool, two queries, on 2026-09-12; results are recorded in run.agent_review and are model-judged.
- Whether an assistant retrieves anything at all for a given question is decided inside the engine and cannot be inferred from the site.
- For product questions assistants cite marketplaces, reviews and press at least as often as the brand's own domain; the corpus that decides the answer is mostly not this site.
- Citation share is redistributive: it moves when competing pages (nike.com/in, Nykaa Fashion, Myntra, Ajio) change, even if this site does not. We audited one candidate, never the pool.
- Which engine is asking changes the outcome; the reachability table is the only engine-specific fact a site crawl can settle, and here it could not settle it.
- 2 checks did not run; each has its reason in report.json under coverage.checks_skipped: TRUST-002, TRUST-014
- Whether an assistant retrieves anything at all, what third-party sources say, which competitors share the retrieval pool, and how each engine reranks are all outside a single-site crawl.
