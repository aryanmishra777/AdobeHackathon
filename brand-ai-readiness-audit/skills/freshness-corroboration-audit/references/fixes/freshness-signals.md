# Fix: freshness signals

A consumer choosing between two sources prefers the one that is current and can
show it. The signal only helps while it stays honest -- a `lastmod` that changes
on every build teaches the reader to ignore it, which is worse than having none.

Covers `TRUST-001` (no visible date), `TRUST-002` (past its cadence),
`TRUST-003` (dishonest `lastmod`), `TRUST-004` (stale year stamps),
`TRUST-005` (facts stated as current that no longer are).

## Show a real published / updated date

On pages whose value depends on recency -- articles, changelogs, pricing,
anything with a "current" claim -- put a machine-readable date in the markup and
a human-readable one on the page:

```html
<p>Published <time datetime="2026-02-14">14 February 2026</time>.
   Last updated <time datetime="2026-08-30">30 August 2026</time>.</p>
```

and in JSON-LD:

```json
{ "@type": "Article",
  "datePublished": "2026-02-14",
  "dateModified": "2026-08-30" }
```

Evergreen pages -- about, contact, legal, a stable product page -- do not need a
visible date and are often cleaner without one. Add dates where recency is part
of the value, not everywhere.

## Keep the update date truthful

`dateModified` and sitemap `<lastmod>` must move only when the content a reader
cares about actually changed. If your build stamps every URL with the deploy
date, the field is noise:

- Derive `lastmod` from the content's own revision history (the CMS entry's
  updated-at, the file's git commit date), not from the build.
- A template or navigation change is not a content change. Do not bump `lastmod`
  for it.
- It is fine for most URLs to have old `lastmod` values. A sitemap where every
  URL shares one very recent date is the tell that the field is meaningless.

```xml
<url>
  <loc>https://example.com/pricing</loc>
  <lastmod>2026-08-28</lastmod>   <!-- the day pricing actually changed -->
</url>
```

## Fix stale stamps and stale claims

- **Copyright year:** render it from the current year in the template
  (`&copy; {{ now.year }} …`) so it can never lag.
- **Year in a title** ("2023 guide") is correct for genuinely dated content and
  wrong on a page presented as current guidance -- either date the page honestly
  or drop the year from the title and refresh the body.
- **"Available now", "coming soon", "this year":** tie these to the page's own
  date. A 2019-dated page that says "available now" needs the claim re-checked
  and the date updated, or an explicit "as of <date>".
- Past event dates presented as upcoming, superseded version numbers, and
  "coming in <year>" where the year has passed are all the same fix: state the
  current fact and stamp when you last confirmed it.
