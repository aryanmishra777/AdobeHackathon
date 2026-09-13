# The unseen-site sweep — 13 September 2026

Every site we audited by hand (nike, adidas, adobe, crunchyroll, sony,
Wikipedia, EA, GitHub) exposed five to ten analyzer misreadings before review,
and the count was not falling. So the scripts-only path — what a judge runs —
was pointed at fifteen sites we had never touched, chosen for shapes the corpus
lacked: a university, a marketplace, a German fashion store, an Indian car maker,
an Indian food app, an Indian bank, an Indian government portal, a hospital
chain, a one-page bakery, a travel platform, a documentation site, a French
newspaper, a Shopify brand, a hotel chain and a design SaaS.

    python tools/run_audit.py <site> --out .audit/unseen/<host>

## What the first pass found

Seven of the fifteen refused, challenged or timed out every fetch from the
audit's address. The reports graded them **83–100 on discoverability from an
empty sample**, called etsy.com "small enough that crawling reaches
everything", and counted bombas.com's 429 to our own start URL as a broken
internal link. canva.com and lemonde.fr answered every URL with a 50-word
"Unsupported client" / "Client Challenge" stub, served with 200 to the audit's
user-agent only; the analyzers wrote forty findings about the stub.

On the sites that were sampled: docs.python.org's `Copyright 2001-2026` read
as twenty-five years stale; its table of contents had eighteen calls to action
because "6.16. Evaluation order" contains "order"; airbnb.com's title tagline
became a second brand name and its canonicals to airbnb.co.in (a country
edition) were a high; mit.edu's "MIT" beside "Massachusetts Institute of
Technology" was an inconsistency; "Holiday rentals in North Myrtle Beach"
named no offering; hdfcbank.com's Current Account was a stale claim about the
present; airbnb's gzipped sitemap index was "unparseable"; and three sites
between 2.4 and 3 s of first-byte time from India were each "too slow".

## What changed

* **The crawl records what it got.** `coverage.sample` is `pages`, or one of
  `refused`, `challenged`, `timed-out`, `unresolved`, `empty`. Challenge and
  unsupported-client stubs are recognised by signature and size, skipped, and
  counted; the crawl stops once twelve arrive with fewer than five pages.
  Timeouts are no longer labelled DNS failures.
* **An empty sample is reported as one.** Only `crawl-access-audit` runs; it
  emits the single finding that explains what happened — a verified block of
  named agents (REACH-005, from the probe), an unknown-crawler rule that spares
  the named agents (informational), an address-level refusal that hit the
  browser baseline too (confidence low, never called an AI block), connections
  that time out, a host that does not resolve. Both axes are **not assessed**.
* **Sitemaps:** gzipped bodies are decompressed whatever the headers say (two
  layers, for airbnb); an HTML page at `/sitemap.xml` is named as one; an
  unparseable sitemap is REACH-007's finding alone.
* **Analyzers:** copyright ranges end this year; "order" is a call to action
  only as "order now"; taglines of six words or more are not brand names and
  an initialism is its expansion; a canonical to a sister edition of the brand
  is low and locked; "Current Account" is a product; listings ("rentals",
  "homes", "flights") name an offering; an empty page is READ's finding, not
  STAY-001's; REACH-015 reports 1.5–3 s at low with low confidence, since one
  ocean explains it; site-wide identity claims need three content pages.

## Second pass

Same fifteen sites, fresh crawls. The seven unsampled sites now carry one
locked finding each and no grades. canva.com and lemonde.fr stop after sixteen
and fifteen stubs (61 s and 41 s instead of a full budget) and report the
unknown-crawler rule as informational, since every named AI agent was served.
On the eight sampled sites the findings that remain are the ones a reader can
verify by opening the page: airbnb.com's edge challenging every named AI agent
while serving a browser (critical), hdfcbank.com's rates in 52 PDFs, zalando's
consent wall on twelve pages, tartinebakery.com's four-word JavaScript shell,
docs.python.org with no structured data.

Bench replay after the changes: 0 false positives, 0 misses, good-SEO/poor-GEO
16 points below good-SEO/good-GEO.

## What is still true

The per-site misreading count on a fresh shape is now two or three, down from
five to ten, and the mistakes left are judgment calls (is a 2001 copyright line
on a page that says "last updated 2026" a finding? we say low) rather than
misreadings. A site that refuses the audit's address gets an honest empty
report; it does not get an audit. That is the boundary, and the report says so.
