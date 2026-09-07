# Fix: crawl rate and time to first byte

## Reading the measurement honestly

An audit's timing is one measurement from one location, including network
latency between the auditing machine and the server. It is directional, not
authoritative. Never report slow TTFB above `medium` on timing alone, and say in
the evidence that the figure is one-shot.

Use the median across sampled pages, never the maximum — a single slow page
among fast ones is noise.

## What matters for crawling

Crawlers allocate a time budget per site rather than a page count. Halving
response time roughly doubles the pages fetched per visit and shortens the delay
before a change is noticed.

## Usual causes, in the order worth checking

1. **No edge caching of anonymous HTML.** The most common and most fixable.
2. **Uncached database queries** on template render.
3. **Synchronous third-party calls** during server render.
4. **Cold serverless starts** on low-traffic routes.
5. **Origin far from the audience** with no CDN in front.

## Crawl-delay

```
User-agent: *
Crawl-delay: 1
```

Honoured inconsistently and ignored by Googlebot. A high `Crawl-delay` reduces
how much of the site gets fetched, so recommend it only when the server is
genuinely struggling — and frame it as a stopgap while response time is fixed.
