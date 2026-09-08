# Connecting Entities into a Stable Graph

Isolated entities declared across disconnected pages force AI retrieval engines to guess whether mentions refer to the same brand or separate entities. Connecting them into an integrated entity graph establishes definitive corporate identity.

## Stable `@id` Identifiers (PARSE-006)

Entities should declare a globally unique `@id` URI rooted at the site's canonical origin:

- **Organization:** `https://example.com/#organization`
- **WebSite:** `https://example.com/#website`
- **Primary Product:** `https://example.com/products/item#product`

### Single Authoritative Definition

Instead of redefining the `Organization` on every page with varying properties, define the canonical entity once or reference its `@id`:

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "https://example.com/#website",
  "url": "https://example.com/",
  "name": "Northwind Coffee Roasters",
  "publisher": {
    "@id": "https://example.com/#organization"
  }
}
```

On individual article or product pages:

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Northwind Explorer Subscription",
  "brand": {
    "@id": "https://example.com/#organization"
  }
}
```

## Authoritative `sameAs` Links (PARSE-005)

The `sameAs` array bridges the on-site entity to verified knowledge graphs and external identity profiles.

### Good Practice
Point `sameAs` at authoritative, controlled, or encyclopedia resources:
- Wikidata entity: `https://www.wikidata.org/wiki/Q...`
- LinkedIn company page: `https://www.linkedin.com/company/...`
- Official social accounts (X/Twitter, YouTube, Crunchbase)
- Wikipedia page (if one exists)

### Binding Guards
- Never invent placeholder `sameAs` links.
- Only include profiles that the organization genuinely owns or is described by.
- Do not list internal site URLs in `sameAs`.

