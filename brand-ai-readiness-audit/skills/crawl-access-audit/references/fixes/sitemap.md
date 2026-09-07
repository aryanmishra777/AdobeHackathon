# Fix: XML sitemaps

## Minimum viable sitemap

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2026-09-01</lastmod>
  </url>
  <url>
    <loc>https://example.com/pricing</loc>
    <lastmod>2026-08-14</lastmod>
  </url>
</urlset>
```

Declare it in `robots.txt`:

```
Sitemap: https://example.com/sitemap.xml
```

## Rules

- **List canonical URLs only.** Never list a URL that redirects, 404s, is
  `noindex`ed, or whose `rel=canonical` points elsewhere. Each tells a crawler
  the site's own index of itself is unreliable.
- **`lastmod` must be true.** A sitemap that stamps today's date on every URL at
  every build is worse than one with no `lastmod` at all: crawlers learn the
  signal is meaningless and discount it. That is `TRUST-003`.
- Split above 50,000 URLs or 50 MB uncompressed, using a sitemap index.
- Absolute URLs, canonical host, canonical scheme.
- `changefreq` and `priority` are largely ignored. Omitting them is fine.

## Sitemap index

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://example.com/sitemap-pages.xml</loc></sitemap>
  <sitemap><loc>https://example.com/sitemap-products.xml</loc></sitemap>
</sitemapindex>
```

## Orphan pages

A sitemap is a discovery aid, not a substitute for internal links. A URL that
appears only in the sitemap and is linked from nowhere signals low importance.
Fix orphaning by linking the page from somewhere relevant, not by listing it
again.
