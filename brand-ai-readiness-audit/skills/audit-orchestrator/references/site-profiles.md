# Site profiles and check gating

The site profile is the cheapest false-positive defense in the marketplace.
Classify once, then let the profile decide which checks are even meaningful.

## Detection

Classify from the evidence bundle only. Signals, in descending weight:

| Profile | Decisive signals |
|---|---|
| `ecommerce` | `Product`/`Offer` JSON-LD; cart or checkout URLs; price patterns on listing pages; `/products/`, `/shop/`, `/collections/`; Shopify/WooCommerce/Magento markers |
| `saas` | `/pricing` with recurring-interval language (per month/seat/user); `/docs` plus `/blog`; signup and login CTAs; `SoftwareApplication` markup |
| `local-business` | `LocalBusiness` markup; address and opening hours in the footer; embedded map; `tel:` links; service-area or single-location language |
| `media-publisher` | `Article`/`NewsArticle` markup; bylines and datelines; dense dated archive; category taxonomy; high article-to-page ratio |
| `docs` | `/docs`, `/reference`, `/api`; sidebar nav with deep hierarchy; code blocks on most pages; version selector |
| `portfolio-brochure` | Under ~20 pages; no commerce, no pricing, no editorial cadence; about/work/contact triad |
| `marketplace` | Many seller or listing entities; faceted search; per-listing `Offer` with distinct sellers |
| `nonprofit-gov` | `.org`/`.gov`/`.edu`; donate, programs, policy sections; `NGO`/`GovernmentOrganization` markup |

Record `site_type`, `confidence`, and the `evidence` sentence naming the signals
used. Mixed sites are common — a SaaS with a large blog is still `saas`; choose
the profile matching the site's **primary commercial purpose**, and note the
secondary character in `evidence` so section-scoped checks still apply.

Set `confidence: low` and prefer `unknown` when signals conflict or the sample
is under 5 pages. `unknown` runs only the universal checks.

## Gating table

`always` = runs on every profile. Otherwise the check runs only on the listed
profiles.

| Check family | Gate |
|---|---|
| All `REACH-*` | `always` — reachability is universal |
| All `READ-*` | `always` — readability is universal |
| `PARSE-001`, `PARSE-002`, `PARSE-003`, `PARSE-010`, `PARSE-011` | `always` |
| `Product`/`Offer` requirements | `ecommerce`, `marketplace` |
| `LocalBusiness`, hours, address, geo | `local-business` |
| `Article`, author, `dateModified`, publisher | `media-publisher`, plus `/blog/` sections on any profile |
| `SoftwareApplication`, pricing markup | `saas` |
| `FAQPage`, `HowTo` | `always`, but only where the page content is genuinely Q&A or stepwise |
| `BreadcrumbList` | `always` except `portfolio-brochure` under 20 pages |
| `QUOTE-005` "no answer-shaped pages" | `ecommerce`, `saas`, `local-business`, `marketplace` — never `docs` or `portfolio-brochure` |
| `QUOTE-006` buyer-question coverage | `ecommerce`, `saas`, `local-business`, `marketplace`, `nonprofit-gov` |
| `TRUST-002` staleness | Threshold varies by profile — see below |
| `TRUST-009` identity anchors | `always`, but the expected anchor set differs by profile |
| `STAY-012` form friction | Only where a form exists |
| `STAY-016` trust signals near conversion | `ecommerce`, `saas`, `local-business`, `marketplace`, `nonprofit-gov` |

## Staleness thresholds (`TRUST-002`)

Judge freshness against what the site claims to be. A brochure site that has
been stable for two years is not stale; a news site silent for three months is.

| Profile | Content considered stale after |
|---|---|
| `media-publisher` | 30 days with no new dated content |
| `saas` | 180 days on `/blog`, `/changelog`, or `/pricing` |
| `ecommerce` | 90 days with no catalogue or availability change |
| `docs` | 365 days, and only where a version or API is referenced |
| `local-business` | 365 days; hours and address changes matter far more than cadence |
| `portfolio-brochure` | Do not report cadence staleness at all; report only demonstrably outdated facts |
| `nonprofit-gov` | 365 days on programs and policy pages |

## Page types

Each page in the bundle carries a `page_type`. Several checks are page-type
gated rather than site gated — `QUOTE-003` key-fact extraction expects different
facts on a pricing page than a contact page, and thin-content checks must never
fire on `legal` or `contact`.

When `page_type` is `other` and the check depends on it, skip and record in
`coverage.checks_skipped` rather than assuming.
