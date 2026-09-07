# Fix: llms.txt

**Emerging convention. Never report its absence as a defect** — it must be a
proactive recommendation, framed as forward-looking. No major assistant is
documented as requiring it today, and overstating it costs credibility that the
rest of the report depends on.

The reason to recommend it anyway is that it is nearly free and forces a useful
exercise: naming the handful of pages carrying the facts most worth quoting.

## Shape

Markdown at `/llms.txt`:

```markdown
# Northwind Coffee Roasters

> Small-batch specialty coffee roaster based in Leeds, United Kingdom,
> shipping across the UK since 2014.

## Key pages

- [Subscriptions](https://example.com/subscriptions): Plans from GBP 29/month,
  including delivery and a rotating single-origin selection.
- [Our roastery](https://example.com/about): Founded 2014, 12 staff, Leeds.
- [Wholesale](https://example.com/wholesale): Terms and minimum order for cafes.
- [Contact](https://example.com/contact): Address, opening hours, phone.

## Facts

- Founded: 2014
- Headquarters: Leeds, United Kingdom
- Ships to: United Kingdom
```

## Rules

- Open with one sentence stating what the organisation is. That sentence is the
  single most quotable thing on the site.
- Link canonical URLs, each with a one-line description of what it answers.
- State facts explicitly rather than implying them.
- Keep it current. A stale `llms.txt` is worse than none, since it presents
  wrong facts in the most machine-legible form on the site.
- It supplements structured data, a sitemap and readable HTML. It replaces none
  of them.
