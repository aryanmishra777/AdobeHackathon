# Fix: Non-Text Content (Images, PDFs, Video, Canvas, SVG)

Starting points, not output. Edit against the bundle before putting any of this
in a report — a snippet with a placeholder left in it will be pasted into
production verbatim by someone.

## The core problem

AI assistants and crawlers cannot reliably read pixels or binary media files.
When critical facts — pricing plans, menus, opening hours, technical specs, or
product features — are embedded exclusively inside images, PDFs, videos, or
HTML5 canvas elements without text alternatives, the site becomes invisible to
retrieval and synthesis.

## Images and Alternative Text

### Decorative vs Informative Images
- **Decorative images**: Use `alt=""`. This explicitly indicates the image
  contains no informative text.
- **Informational images**: Provide concise, descriptive text that conveys the
  facts shown in the visual.
- **Absent alt (`alt=null`)**: When the attribute is missing entirely, crawlers
  cannot determine whether the image is decorative or vital.

```html
<!-- Correct: Decorative graphic -->
<img src="/assets/hero-pattern.svg" alt="" role="presentation" />

<!-- Correct: Informative graphic with data points -->
<img src="/assets/pricing-tiers.png"
     alt="Pricing tiers comparison: Starter plan $29/mo with 5 users; Pro plan $79/mo with 25 users." />
```

### Critical Facts Must Live in HTML Text
Never rely solely on an image for business-critical data (menus, pricing tables,
hours, address, or specifications). Always accompany images with readable HTML
text:

```html
<section id="pricing">
  <h2>Pricing Overview</h2>
  <!-- Text version guaranteed to be extractable -->
  <div class="pricing-summary">
    <p>Standard Subscription: $49/month. Includes unlimited ingestion and 24/7 support.</p>
  </div>
  <img src="/images/pricing-chart.png" alt="Detailed comparison table of Standard vs Enterprise features" />
</section>
```

## PDF-Only Content

If core commercial facts (rate cards, menus, specifications, terms) live only
in downloadable PDF files, search bots and assistants cannot index them as part
of the page:

1. Create a native HTML page for the content (e.g. `/pricing` or `/specifications`).
2. Offer the PDF download as an additional convenience or printable option alongside the HTML text.

## Video and Audio Transcripts

When media embeds carry the primary message of a page:
1. Provide a written transcript or executive summary directly beneath the player.
2. Include key timestamps and quotes that answer common visitor questions.

```html
<figure>
  <iframe src="https://www.youtube-nocookie.com/embed/example" title="Product Demo Video"></iframe>
  <figcaption>
    <h3>Video Transcript Summary</h3>
    <p>In this video, Acme demonstrates the new query planner. Key highlights include 3x faster joins and native vector indexing.</p>
  </figcaption>
</figure>
```

## HTML5 Canvas and SVG Content

- **Canvas**: An HTML5 `<canvas>` element contains pixels, not text. Always
  provide accessible fallback text within the `<canvas>` tags or an adjacent table.
- **SVG**: Ensure SVGs carry `<title>`, `<desc>`, and actual `<text>` elements
  instead of converted path glyphs.

```html
<svg viewBox="0 0 100 100" role="img" aria-labelledby="chart-title">
  <title id="chart-title">Quarterly Revenue Growth</title>
  <text x="10" y="20">Q1: $1.2M</text>
  <text x="10" y="40">Q2: $1.5M</text>
</svg>
```

