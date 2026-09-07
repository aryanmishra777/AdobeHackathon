# Fix: canonicals, origin consolidation and TLS

## One origin

A site should answer on exactly one origin and redirect the rest to it.

```
http://example.com/*      -> 301 -> https://www.example.com/*
https://example.com/*     -> 301 -> https://www.example.com/*
http://www.example.com/*  -> 301 -> https://www.example.com/*
```

Redirect to the **matching path**, not the home page. A blanket redirect to `/`
destroys every deep link the site has earned, which is a larger loss than the
duplication it fixes.

Chains cost crawl budget and lose signal at each hop. Redirect once, directly to
the final URL.

## Canonicals

Self-referential on every page, absolute, on the canonical host:

```html
<link rel="canonical" href="https://www.example.com/pricing" />
```

- A canonical is a hint, not a directive. It does not substitute for a redirect
  when both URLs genuinely serve.
- Never point a canonical at a URL that redirects, 404s, or is `noindex`ed.
- Cross-domain canonicals are legitimate for syndicated content and wrong
  everywhere else. Confirm intent before recommending a change.
- One canonical per page. Two conflicting tags cause both to be ignored.

## Faceted and parameterised URLs

Filter and sort combinations multiply URLs quickly. Point every variant's
canonical at the unfiltered category URL. Keep pagination canonical to itself
rather than to page 1.

## TLS

- Serve valid, non-expired certificates covering every host form in use.
- Fix mixed content: an `https` page loading `http` subresources is degraded for
  users and can fail to render for a crawler.
- Include both `www` and apex in the certificate if both resolve.
