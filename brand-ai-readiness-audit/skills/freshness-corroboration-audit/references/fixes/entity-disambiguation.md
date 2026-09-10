# Fix: entity disambiguation

When several things share a name, a machine mixes them up unless something on
the page distinguishes them. The problem is never the name itself and the fix is
never a rebrand -- it is giving the resolver an explicit anchor to bind to.

Covers `TRUST-007` (name collides with better-known entities),
`TRUST-008` (no unambiguous identity sentence), `TRUST-011` (official profiles
not linked).

## Write one disambiguating sentence

Put a sentence of this shape in the first screen of the home page and in the
`<meta name="description">`:

> **[Brand] is a [specific category] based in [city, country], [one distinguishing fact].**

For example: *"Northwind Coffee Roasters is a small-batch specialty coffee
roaster based in Leeds, United Kingdom, shipping across the UK since 2014."*

It names the category (so the brand is not confused with a same-named band or
town), the location (the strongest disambiguator there is), and one fact only
this entity has. This overlaps the "say what you do" identity sentence -- if you
already have that, the job here is to make sure it also carries the location and
a distinguishing detail.

## Link and declare the official profiles

Give the resolver a graph to walk:

```json
{ "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Northwind Coffee Roasters",
  "url": "https://example.com/",
  "sameAs": [
    "https://www.linkedin.com/company/northwind-coffee-roasters",
    "https://www.wikidata.org/wiki/Q00000000",
    "https://www.instagram.com/northwindcoffee"
  ]
}
```

- Every profile in `sameAs` should also be a real link in the site footer.
- List only profiles that exist and are yours. If the organisation keeps no
  social presence at all, that is a choice -- treat "create some" as an optional
  recommendation, not a defect, but still declare whatever anchors do exist
  (Wikidata, a company register entry, an industry directory).
- Keep the name identical across every profile and every mention on the site.

## What not to do

- Do not rename the company to avoid a collision.
- Do not claim `sameAs` links to profiles you do not control.
- Do not create a Wikipedia article to manufacture an anchor -- Wikidata is the
  machine-readable one that matters and has no notability bar.
