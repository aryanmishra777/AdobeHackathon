# Fix: JSON-LD Templates & Syntax

Use this guide when structured data is absent, broken, conflicting with visible text, or describing unrendered content.

## Priority Order

1. **Resolve contradictions between markup and visible text (PARSE-007).** An explicit disagreement between machine-readable data and human-readable text destroys model confidence across the entire domain.
2. **Correct invalid syntax (PARSE-002).** Unescaped quotation marks or missing commas inside `<script type="application/ld+json">` cause parsers to discard the entire block silently.
3. **Publish essential structured data (PARSE-001).** Implement schema markup for primary entities.
4. **Remove or surface unrendered marked-up content (PARSE-008).** Keep markup strictly aligned with visible content.

## Common Syntax Pitfalls

- **CMS Template Quote Escaping:** Ensure server-side templating engines escape string variables (e.g. product descriptions, organization names) using `json_encode` or equivalent rather than raw string interpolation.
- **Trailing Commas:** Standard JSON disallows trailing commas in arrays and objects. Validate with `json.loads` or an automated CI step.
- **Multiple Formats:** If migrating from Microdata to JSON-LD, remove duplicate Microdata tags once JSON-LD is in place to prevent conflicting values (PARSE-009).

## Base Templates

### Product & Offer (Commercial Pages)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Single Origin Colombian Roast",
  "description": "Medium roast whole bean coffee with notes of caramel and red apple.",
  "image": "https://example.com/images/colombian-roast.jpg",
  "offers": {
    "@type": "Offer",
    "price": "18.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://example.com/products/colombian-roast"
  }
}
</script>
```

### Organization (Canonical Entity)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.com/#organization",
  "name": "Northwind Coffee Roasters",
  "url": "https://example.com/",
  "logo": "https://example.com/logo.png",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "14 Kirkgate",
    "addressLocality": "Leeds",
    "postalCode": "LS1 6BY",
    "addressCountry": "GB"
  },
  "sameAs": [
    "https://www.linkedin.com/company/northwind-coffee-roasters",
    "https://www.wikidata.org/wiki/Q000000"
  ]
}
</script>
```

### Article (Editorial Content)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Understanding Specialty Coffee Processing Methods",
  "datePublished": "2026-08-15T09:00:00Z",
  "dateModified": "2026-08-20T14:30:00Z",
  "author": {
    "@type": "Person",
    "name": "Jane Doe"
  },
  "publisher": {
    "@type": "Organization",
    "@id": "https://example.com/#organization"
  }
}
</script>
```

## Aligning Markup with Visible Page Text

- **Price consistency:** The marked-up `price` must match the visible selling price. If variable pricing exists, use `AggregateOffer` with `lowPrice` and `highPrice`.
- **Availability:** Ensure `availability` reflects the displayed stock status.
- **Entities rendered:** Never mark up hidden review arrays or fake aggregate ratings if visitors cannot read them on the page.

