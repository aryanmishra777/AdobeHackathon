# Fix: indexability and snippet directives

Two separate permissions, frequently confused:

- **Indexing** decides whether the page can be found at all.
- **Snippets** decide whether its text may be reproduced in an answer.

A page can be perfectly indexed and still useless as a source because snippets
are suppressed. That is `REACH-009`, and it is the more insidious of the two
because nothing about the page looks wrong.

## Where directives come from

Both the meta tag and the HTTP header apply, and **the header is invisible in
page source** — it is frequently the cause of a mystery `noindex`.

```html
<meta name="robots" content="index, follow, max-snippet:-1">
```

```
X-Robots-Tag: index, follow, max-snippet:-1
```

Always check both:

```bash
curl -s https://example.com/page | grep -i 'name="robots"'
curl -sI https://example.com/page | grep -i 'x-robots-tag'
```

## Values that matter

| Directive | Effect |
|---|---|
| `noindex` | Excluded from the index. Cannot be retrieved or cited. |
| `nosnippet` | Indexed, but **no text may be reproduced**. Fatal for citability. |
| `max-snippet:0` | Equivalent to `nosnippet`. |
| `max-snippet:-1` | No length limit. What a citable page wants. |
| `noarchive` | No cached copy. Minor. |
| `nofollow` | Links on the page are not followed. Rarely wanted site-wide. |

## Where noindex is correct

Never report these as defects: cart, checkout, account, login, internal search
results, tag and filter archives, pagination beyond page 1, thank-you and
order-confirmation pages, staging and preview URLs.

## Paywalled content

Do not recommend removing `nosnippet` from paywalled articles outright. Use a
small positive `max-snippet` so a citable summary is permitted, and declare the
paywall so assistants can represent it honestly:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "isAccessibleForFree": false,
  "hasPart": {
    "@type": "WebPageElement",
    "isAccessibleForFree": false,
    "cssSelector": ".paywalled-body"
  }
}
</script>
```

## hreflang

Only relevant when the site genuinely serves multiple locales. Annotations must
be reciprocal: if `/en/` points at `/de/`, `/de/` must point back. Include a
self-reference and an `x-default`.

```html
<link rel="alternate" hreflang="en-gb" href="https://example.com/en-gb/page" />
<link rel="alternate" hreflang="de-de" href="https://example.com/de-de/page" />
<link rel="alternate" hreflang="x-default" href="https://example.com/page" />
```
