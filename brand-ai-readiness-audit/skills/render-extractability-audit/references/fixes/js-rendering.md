# Fix: JavaScript Rendering & Client-Side Hydration

Starting points, not output. Edit against the bundle before putting any of this
in a report — a snippet with a placeholder left in it will be pasted into
production verbatim by someone.

## The core problem

AI assistants, web crawlers, and retrieval systems typically fetch raw HTML over
HTTP without running an interactive browser rendering engine (or run headless
browsers on strict time/resource budgets). If primary content — product specs,
pricing tables, documentation, articles — exists only in JavaScript hydration
payloads or client-rendered templates, crawlers see an empty shell.

## Server-Side Rendering (SSR) and Static Generation (SSG)

Configure your framework to render the main text and headings into the initial
HTML response.

### Next.js (App Router)
By default, React Server Components (RSC) render on the server into HTML:
```tsx
// app/pricing/page.tsx
export default async function PricingPage() {
  const plans = await getPricingPlans();
  return (
    <main>
      <h1>Subscription Plans</h1>
      {plans.map((p) => (
        <section key={p.id}>
          <h2>{p.name} — ${p.price}/month</h2>
          <p>{p.description}</p>
        </section>
      ))}
    </main>
  );
}
```

### Static Pre-rendering
For marketing, docs, and public articles, pre-render pages at build time so the
full HTML is served directly by the CDN edge:
- Next.js: `generateStaticParams()` or `output: 'export'`
- Nuxt: `nuxi generate` or `routeRules: { '/**': { prerender: true } }`
- Astro: Static by default (`output: 'static'`)

## Noscript fallback as secondary mitigation

While SSR is the primary solution, provide a substantive `<noscript>` fallback
when server rendering cannot be applied immediately:

```html
<noscript>
  <div class="noscript-content">
    <h1>Acme Analytics Platform</h1>
    <p>Acme Analytics provides real-time streaming data ingestion, SQL querying, and ML pipeline orchestration.</p>
    <h2>Pricing & Plans</h2>
    <p>Starter: $49/mo. Team: $199/mo. Enterprise: Custom pricing.</p>
  </div>
</noscript>
```

> [!NOTE]
> A `<noscript>` tag that only says "Please enable JavaScript" provides zero
> content for retrieval and is treated as absent.

## Tab and Accordion Content

Render all tab and accordion panels directly into the initial DOM, toggling
visibility with CSS rather than fetching on click:

```html
<div class="accordion-item">
  <button class="accordion-header" aria-expanded="false" aria-controls="panel-faq-1">
    How does data synchronization work?
  </button>
  <div id="panel-faq-1" class="accordion-panel" hidden>
    <p>Data sync runs every 5 minutes via bi-directional webhook replication.</p>
  </div>
</div>
```
CSS:
```css
.accordion-panel[hidden] {
  display: none;
}
```

## Pagination URLs for Infinite Scroll

Ensure listings that load more items via infinite scroll or JavaScript buttons
also expose crawlable standard anchor links:

```html
<nav class="pagination" aria-label="Pagination">
  <a href="/products?page=2" rel="next">Next Page (Page 2)</a>
</nav>
```

## Third-Party Widgets & Iframes

Iframes (such as reviews or booking widgets) isolate content from the parent
page. Mirror key aggregate facts directly into the host HTML as visible text
and structured data:

```html
<div class="reviews-summary">
  <p>Rated <strong>4.8 / 5</strong> based on <strong>1,240 verified customer reviews</strong>.</p>
</div>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Acme Core",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "1240"
  }
}
</script>
```

