# Schema Requirements by Site Profile & Page Type

Structured data requirements are gated strictly by site profile and page type. Demanding e-commerce markup on a SaaS platform or local opening hours on a digital publisher generates noisy false positives.

## Site Profile Gating

| Site Profile | Expected Page-Specific Entities | Never Expect |
|---|---|---|
| `ecommerce` | `Product`, `Offer`, `AggregateOffer`, `ItemList` | `APIReference`, `TechArticle` |
| `saas` | `SoftwareApplication`, `PriceSpecification`, `FAQPage` | `OpeningHoursSpecification`, physical `PostalAddress` on every product |
| `local-business` | `LocalBusiness`, `PostalAddress`, `OpeningHoursSpecification`, `GeoCoordinates` | `SoftwareSourceCode`, complex multi-seller catalogs |
| `media-publisher` | `NewsArticle`, `Article`, `author`, `publisher` | `Product`, transactional checkout markup |
| `docs` | `TechArticle`, `SoftwareSourceCode`, `APIReference` | `LocalBusiness`, `Offer` |
| `portfolio-brochure`| `Organization`, `Person`, `ContactPage` | `Product`, `BreadcrumbList` (when under 20 pages) |
| `marketplace` | `Product`, `Offer` (per seller), `AggregateRating` | Single-tenant local business hours |
| `nonprofit-gov` | `NGO`, `GovernmentOrganization`, `Article`, `Event` | Transactional e-commerce products |

## Required vs. Recommended Properties

### `Product`
- **Required:** `name`, `offers` (an `Offer` or `AggregateOffer` containing `price` and `priceCurrency`, or `priceSpecification`).
- **Recommended:** `image`, `description`, `sku`, `brand`.

### `Article` / `NewsArticle` / `BlogPosting`
- **Required:** `headline`.
- **Required for editorial credibility (PARSE-014):** `author` (Person or Organization), `publisher` (Organization).
- **Recommended:** `datePublished`, `dateModified`, `image`.

### `LocalBusiness`
- **Required:** `name`, `address` (`PostalAddress` with street, locality, postal code, country).
- **Recommended:** `telephone`, `openingHoursSpecification`, `geo`.

### `Organization`
- **Required:** `name`, `url`.
- **Recommended:** `logo`, `address`, `sameAs` (authoritative profiles).

### `FAQPage`
- **Required:** `mainEntity` array of `Question` entities, each with an `acceptedAnswer` (`Answer` entity with `text`).
- **Guideline:** Only mark up genuine Q&A blocks. Do not convert marketing prose or bullet points into FAQs.

### `BreadcrumbList`
- **Required:** `itemListElement` array of `ListItem` entities, each with `position`, `name`, and `item` (URL).
- **Hierarchy Gate:** Required only on deep sites (>20 pages with directory depth >= 2). Flat brochure sites do not require breadcrumbs.

