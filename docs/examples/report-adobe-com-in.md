<!--
A real report of a country section: https://www.adobe.com/in/, 12 September
2026, 25 pages scoped with --include /in/ (home, 7 Type and PDF Print Engine
product pages, 10 about-adobe pages, 7 Acrobat pages). Retrieved read-only;
live sites change.

What the agent overrode, recorded in run.agent_review: dropped TRUST-010 (the
worldwide office directory is many locations, not inconsistent contact
details), three STAY-007 "interstitials" that were the footer's region picker
and a hash-opened video dialog, STAY-016 on B2B information pages that ask for
no transaction, QUOTE-001 on an address list, and a QUOTE-007 on a product
overview. Added READ-001 at high: the /in home page and the Acrobat plan pages
reach a machine as Edge Delivery authoring documents with fragment URLs, merch
placeholders ('{{annual-paid-monthly-plan-geo-ip}}') and layout tokens where
the content should be, and no rupee price anywhere in the sample -- third-party
sites publish the figure instead. The edge tarpits every known crawler name from
an unverified address, so the engine table says unverified rather than blocked.
-->

# AI-Readiness Audit — https://www.adobe.com/in/

adobe.com/in is readable everywhere except where it sells: the Acrobat plan pages and the home page reach a machine as authoring documents with '{{annual-paid-monthly-plan-geo-ip}}' where the rupee price should be, so the price an assistant quotes comes from a third party.

| | Grade | Score |
|---|---|---|
| **Discoverability** — can AI assistants find, trust and cite you? | B | 75/100 |
| **Engagement** — do visitors who arrive stay? | A | 96/100 |

**10 findings:** 0 critical · 1 high · 5 medium · 4 low
Audited 2026-09-12T18:02:04Z · 25 pages sampled

## Which assistants can reach you

| Assistant | Status | What we measured |
|---|---|---|
| ChatGPT | **partial** | unverified: the edge never answered ChatGPT-User (TimeoutError: The read operation timed out) and never answered the browser baseline either, so the stall cannot be attributed to the agent name; robots.txt permits it |
| Claude | **partial** | unverified: the edge never answered Claude-User (TimeoutError: The read operation timed out) and never answered the browser baseline either, so the stall cannot be attributed to the agent name; robots.txt permits it |
| Perplexity | **partial** | unverified: the edge never answered PerplexityBot (TimeoutError: The read operation timed out) and never answered the browser baseline either, so the stall cannot be attributed to the agent name; robots.txt permits it |
| Google AI Overviews / Gemini | **partial** | unverified: the edge never answered Googlebot (TimeoutError: The read operation timed out) and never answered the browser baseline either, so the stall cannot be attributed to the agent name; robots.txt permits it |
| Microsoft Copilot | **partial** | Bingbot is permitted by robots.txt, but no request was made under that agent name, so whether the edge serves it is unverified |

## Fix these first

1. **Server-render the merch cards and marquee fragments on /in and the Acrobat plan pages, with the INR price in the HTML** — The only high-severity findings and the pages that carry the purchase decision. The URL already encodes the geo (/in/), so the price can be resolved at publish time; today the HTML says '{{annual-paid-monthly-plan-geo-ip}}' and third-party sites publish the ₹944/month figure instead. *(fixes F-001, F-003; effort: M)*
2. **Add breadcrumb navigation with BreadcrumbList markup to the product and Acrobat pages, and point the existing about-page breadcrumbs at the /in/ pages** — Two findings, one template. The about pages already render a trail; it links to the global site and carries no markup. The product pages have none at all. *(fixes F-002, F-006; effort: S)*
3. **Fix the heading outline on the six pages that skip levels or lack an h1, and break the two long pages into sections** — Structural edits to a handful of pages; the OpenType page runs 938 words under no subheading. *(fixes F-004, F-010; effort: S)*
4. **Declare lang="en-IN" on <html>, give the two executive profiles distinct titles, size the OpenType page's images, and add one identity sentence to the India contact page** — Hygiene, each under an hour; lang is missing on 22 of 25 pages of a country site. *(fixes F-005, F-007, F-009, F-008; effort: S)*

## Findings

### Can they read the page?

#### F-001 · The India home page and Acrobat pages ship authoring placeholders where the prices and offers should be  `high`

**What we found.** The HTML served for /in and the five Acrobat plan pages is the Edge Delivery authoring document, decorated in the browser. Its text contains bare fragment URLs in place of content (20 on /in, 6-19 per Acrobat page, e.g. https://main--upp--adobecom.aem.page/homepage/fragments/.../marquee-sub-copy/cc-pro/intro-price), merch placeholders in place of prices ('mas-field: ACOM-DC / Headless / Individual / com / Acrobat Pro Subs CC → prices for Acrobat Pro', 'Both are {{annual-paid-monthly-plan-geo-ip}}'), and layout tokens as prose ('con-block-row-bgcolor #F8F8F8', 'masonry full-width', '(s-body)'). No page in the sample contains a rupee price; the plan-comparison cards are a fragment (dc-shared/fragments/merch-cards/compare-acrobat-plans) loaded at runtime. A retriever therefore gets the copy but not the price, and quotes the placeholder if it quotes anything. Independent pages already state the figure the site withholds (FairSubs, Techjockey: Acrobat Pro India from about ₹944/month billed annually), so an assistant answering 'Acrobat Pro price in India' sources them, not adobe.com. No renderer was available; the finding is about what the HTML carries, which is measured.

**Why it matters.** The price is the fact a buyer asks an assistant for. It is absent from the HTML and present on third-party sites, so the citation goes to them; the placeholders that are present are noise a retriever will index as if it were copy.

**Fix.** Server-render the merch cards and marquee fragments for the /in/ pages, with the INR price in the HTML
- Resolve merch-at-scale (mas) price fields at publish or edge time for the geo the URL already encodes (/in/ is India), so the HTML carries '₹944/month' rather than '{{annual-paid-monthly-plan-geo-ip}}'
- Inline the marquee and merch-card fragments into the served HTML instead of leaving their aem.page URLs as text; keep client decoration for interactivity only
- Strip authoring metadata (mas-field, con-block-row-*, style tokens) from the delivered document
- Add Product/Offer JSON-LD with priceCurrency INR on each plan page so the price is extractable twice

**Check it yourself.** `curl -s https://www.adobe.com/in/acrobat/acrobat-pro.html | grep -o 'mas-field[^<]*\|{{[^}]*}}' and note that no ₹ figure appears; then open the page in a browser and read the price card`

#### F-004 · Heading structure does not describe the page  `medium`

**What we found.** 6 of 25 pages exhibit heading hierarchy breaks: 3 have no <h1>; 3 skip heading levels.

**Why it matters.** Headings define chunk boundaries during semantic retrieval; consistent hierarchy ensures snippets retain their parent topic context.

**Fix.** Structure content with hierarchical heading tags
- Ensure every page has exactly one distinct <h1> summarizing its subject
- Follow sequential descending levels (h1 -> h2 -> h3) without skipping intermediate ranks
- Avoid using heading tags merely for visual styling

**Check it yourself.** `curl -s https://www.adobe.com/in/about-adobe/roc/leaders/prativa-mohapatra.html | grep -oE '<h[1-6]'`

#### F-005 · Character encoding or language is undeclared  `medium`

**What we found.** 0 pages declare no charset in headers or meta; 22 pages declare no lang attribute.

**Why it matters.** Explicit declarations ensure language identification models process content accurately without misinterpreting characters.

**Fix.** Declare UTF-8 charset and document language
- Add <meta charset="utf-8"> as the first child of <head>
- Add lang="en" (or appropriate language code) to the <html> tag
- Include charset=utf-8 in the server Content-Type response header

**Check it yourself.** `curl -sI https://www.adobe.com/in/products/pdfprintengine/buying-guide.html | grep -i content-type`

### Can they parse facts out?

#### F-002 · No breadcrumb markup or navigation  `medium`

**What we found.** 13 of 25 sampled pages -- the PDF Print Engine, Type and Acrobat pages -- declare no BreadcrumbList and render no breadcrumb list. The about-adobe pages do render a <div class="breadcrumbs"> trail (Home > About Adobe > Contact), but its links point at the global pages (https://www.adobe.com/about-adobe.html), not the /in/ ones, and none of the 25 pages carries BreadcrumbList markup.

**Why it matters.** Breadcrumbs state the hierarchical context of deep pages, helping AI agents understand where facts sit in relation to parent topics.

**Fix.** Add BreadcrumbList structured data and navigation trail
- Render breadcrumb navigation linking parent category paths
- Add BreadcrumbList JSON-LD markup indicating hierarchy position

**Check it yourself.** `Open https://www.adobe.com/in/products/pdfprintengine/buying-guide.html and look for a breadcrumb trail`

#### F-007 · Titles and meta descriptions are missing, duplicated or conflicting  `low`

**What we found.** 2 of 25 pages share duplicate titles: e.g. 2 pages share 'leaders'. Observed on 7 of 25 sampled pages: https://www.adobe.com/in/about-adobe/leaders/louise-pentland.html, https://www.adobe.com/in/about-adobe/roc/leaders/prativa-mohapatra.html, https://www.adobe.com/in/about-adobe/contact/offices.html....

**Why it matters.** Duplicated titles cause search engines to treat pages as identical variants.

**Fix.** Make page titles distinct and unique
- Ensure every URL template generates a distinct title naming the specific page subject

**Check it yourself.** `curl -s https://www.adobe.com/in/about-adobe/leaders/louise-pentland.html | grep -i '<title>'`

### Can they quote a clear fact?

#### F-003 · No sampled page states a price for any Adobe plan in India as extractable text  `medium`

**What we found.** Across 25 pages including /in/acrobat.html, acrobat-pro, acrobat-standard, acrobat-studio and the /in home page, there is no rupee figure in the text. Where a price belongs the HTML carries 'prices for Acrobat Pro' and '{{annual-paid-monthly-plan-geo-ip}}'. The pricing page itself (/in/acrobat/pricing.html) was not in the sample; it is built on the same merch-card fragment and should be checked with the same curl.

**Why it matters.** Price is the fact class most central to a plan page; when it is not text, the page cannot answer the question it exists for.

**Fix.** Put the INR price in the HTML of every plan page
- Follows from the READ-001 fix: once the merch card is server-rendered the price is text
- State the plan model in prose as well -- 'Acrobat Pro for individuals is ₹X/month on an annual plan' -- so the fact survives outside the card

**Check it yourself.** `curl -s https://www.adobe.com/in/acrobat/acrobat-pro.html | grep -c '₹' (expect 0)`

*Downstream of READ-001 — fixing that may resolve this.*

#### F-008 · The site never states plainly what the organization is  `low`

**What we found.** None of the 25 sampled pages, including eight under /in/about-adobe/, carries a sentence of the form 'Adobe is a ... company that ...'. The closest are 'Adobe is a member of a number of trade and technology associations worldwide' and the home title 'Adobe: Creative, marketing and document management solutions'. Nothing on the /in/ pages says what Adobe India is (Adobe Systems India Pvt Ltd, Noida and Bengaluru) or how the India site relates to the global one. Severity is low because the brand needs no introduction; reported because a machine resolving the entity still has no sentence to lift.

**Why it matters.** One quotable sentence is what an entity resolver lifts; today it has to infer from a title.

**Fix.** Add one identity sentence to the India about/contact page and the Organization JSON-LD
- On /in/about-adobe/contact.html: 'Adobe is a software company whose Creative Cloud, Document Cloud and Experience Cloud products are sold in India by Adobe Systems India Pvt Ltd, headquartered in Noida.'
- Repeat it as the Organization description in JSON-LD with sameAs to Wikipedia and Wikidata

**Check it yourself.** `Read the first screen of https://www.adobe.com/in and https://www.adobe.com/in/about-adobe/contact.html and try to write one sentence saying what the company is`

*Downstream of READ-001 — fixing that may resolve this.*

### Do visitors who arrive stay?

#### F-006 · Visitors cannot tell where they are in the site  `medium`

**What we found.** 3 of 9 sampled pages at URL depth 3 or greater show no breadcrumb or section navigation in the HTML.

**Why it matters.** A visitor who lands deep from a search or an AI link needs to see where they are to trust the page and to explore sideways rather than bounce.

**Fix.** Add a breadcrumb trail to pages more than two levels deep
- Render a breadcrumb (Home / Section / Page) at the top of deep pages
- Mirror it as BreadcrumbList JSON-LD
- Keep the current section highlighted in the primary nav

**Check it yourself.** `Open https://www.adobe.com/in/products/pdfprintengine/buying-guide.html directly and try to identify which section it belongs to`

#### F-009 · Images without dimensions risk layout shift  `low`

**What we found.** On https://www.adobe.com/in/products/type/opentype.html, 3 of the first 3 images (the best available proxy for above-the-fold) declare neither width nor height; 27 of 265 images site-wide lack dimensions. Reserving no space for them risks layout shift as they load.

**Why it matters.** An image with no reserved space pushes content down when it loads, and a visitor who was about to click the thing that moved is a visitor who mis-clicks and leaves.

**Fix.** Declare width and height (or aspect-ratio) on every content image
- Add width and height attributes matching the image's intrinsic size
- Or set aspect-ratio in CSS on the image container
- Prioritise images in the first screen, where a shift is most jarring

**Check it yourself.** `curl -s <page> | grep -c '<img' and compare with the count carrying a width attribute`

#### F-010 · Content is hard to read  `low`

**What we found.** https://www.adobe.com/in/products/type/opentype.html runs 938 words with 0 subheading(s) -- about 938 words per section. Long unbroken text is skimmed and abandoned. (Structural density only; typography and contrast are not assessed.). Observed on 2 of 25 sampled pages: https://www.adobe.com/in/products/type/opentype.html, https://www.adobe.com/in/products/pdfprintengine/endorsements.html.

**Why it matters.** A wall of text with no landmarks is skimmed for an exit, not read; subheadings give a scanner reasons to stay.

**Fix.** Break long pages into scannable sections
- Add a descriptive subheading every 200-300 words
- Pull key points into short lists
- Front-load each section with its conclusion

**Check it yourself.** `Scroll https://www.adobe.com/in/products/type/opentype.html and look for structure breaking up the text`

## Worth doing even though nothing is broken

- **Mark up the facts buyers ask about, not merely the page type** — WebPage markup states that a page exists. Price, availability, location, hours and eligibility are the facts an assistant is asked for, and each one marked up is one more question the site can answer directly.
- **Add a liftable summary to the top of long pages** — https://www.adobe.com/in/products/type/opentype.html runs to 938 words with no summary, key-takeaways or TL;DR block near the top. A 2-3 sentence summary is the block most likely to be retrieved and quoted whole.
- **Show an honest update date on pages that change** — 14 of 25 sampled content pages carry no visible published or updated date, though the site's content reads as current. A truthful update date lets a consumer prefer the page over an older competing source.
- **Confirm the edge's verified-bot allow-list includes the AI retrieval agents** — The edge never answered ChatGPT-User, Claude-User, PerplexityBot or Googlebot from this address while serving unknown user-agents at once. That is consistent with impersonation defence, not a policy, but only the Bot Manager console can confirm which; robots.txt is silent on every AI agent.
- **Publish an llms.txt for the India site pointing at the plan and pricing pages** — GET https://www.adobe.com/llms.txt was not present. For a site whose prices are geo-resolved, a short file naming the /in/ pricing pages and the plan model gives an assistant a place to start that the sitemap index (nine sitemaps, ninety per-locale children) does not.

## What this audit did not cover

- No browser renderer was available, so JavaScript dependency is inferred from raw HTML rather than measured; the Acrobat pages' placeholders are what the HTML carries, which is measured.
- The user-agent probe is inconclusive: the edge never answered a plain Chrome UA or any named crawler from this address while serving unknown user-agents at once. Whether genuine AI retrieval agents from their published IP ranges are admitted cannot be measured from outside those networks; the engine table says 'partial / unverified' for that reason and no REACH-005 finding is made.
- The audit was scoped to /in/ with --include. The sample is 25 of 1,642 discovered URLs: the /in home page, 7 Adobe Type and PDF Print Engine product pages, 10 about-adobe pages and 7 Acrobat pages. No Creative Cloud, Photoshop, Firefly, Express or Learn page was sampled, and neither was /in/acrobat/pricing.html; the sitemap index lists 1,650 /in/ Creative Cloud pages the round-robin did not reach in 25 slots.
- The 24 model-judged checks were completed by reading each analyzer's registry and inspecting the bundle; three fired (READ-001, QUOTE-003, QUOTE-002) and the judgment for each of the others is recorded in run.agent_review.
- Off-site corroboration (TRUST-006/007/009/012/013) was completed with one web search on 2026-09-12; results are recorded in run.agent_review and are model-judged.
- The engagement axis grades usability proxies. Engagement is measured from visitor behaviour -- dwell time, return visits, scroll, clicks -- and a site audit has no visitor to observe.
- Whether an assistant retrieves anything at all for a given question is decided inside the engine and cannot be inferred from the site.
- For pricing questions assistants cite comparison sites and resellers at least as often as the vendor; here they must, because the vendor's HTML has no price.
- Citation share is redistributive: it moves when competing pages (FairSubs, Techjockey, resellers) change, even if this site does not. We audited one candidate, never the pool.
- Which engine is asking changes the outcome; the reachability table is the only engine-specific fact a site crawl can settle, and here it could not settle it.
- 2 checks did not run; each has its reason in report.json under coverage.checks_skipped: TRUST-002, TRUST-014
- Whether an assistant retrieves anything at all, what third-party sources say, which competitors share the retrieval pool, and how each engine reranks are all outside a single-site crawl.
