# Fix: Consent Walls, Interstitials & Paywall Declarations

Starting points, not output. Edit against the bundle before putting any of this
in a report — a snippet with a placeholder left in it will be pasted into
production verbatim by someone.

## The core problem

When an entire web page's HTML body is omitted or withheld until a user clicks
"Accept" on a consent modal, automated web crawlers and retrieval agents receive
only the consent text. Furthermore, if public-facing pages require authentication
or hide behind paywalls without declaring machine-readable paywall markup, AI
assistants cannot cite or quote the content legitimately.

## Serving Content Beneath Consent Banners

Legally mandated consent requirements (e.g. GDPR, CCPA) do not require
withholding primary body text from the HTML response:

1. **Deliver the full content in the server HTML**: Render the page content
   normally within `<main>`.
2. **Overlay the consent banner via CSS/DOM**: Display the consent dialog as a
   non-blocking or accessible modal overlay. Do not conditionally render the
   underlying content via client-side JavaScript.
3. **Do not serve challenge pages or 403s to verified crawlers**: Ensure CDN and
   WAF bot-management rules pass recognized AI retrieval agents through to the
   content.

## Paywalls and Machine-Readable Declarations

Paywalls represent a legitimate business model. To enable search engines and AI
assistants to understand and cite paywalled articles accurately:

1. Use schema.org `NewsArticle` or `CreativeWork` with `isAccessibleForFree`:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "mainEntityOfPage": "https://example.com/analysis-2026",
  "headline": "In-Depth Market Analysis 2026",
  "isAccessibleForFree": false,
  "hasPart": {
    "@type": "WebPageElement",
    "isAccessibleForFree": false,
    "cssSelector": ".paywall-content"
  }
}
</script>
```

2. Allow crawl bots to inspect at least the lead paragraph or summary so that the
   subject matter can be indexed and attributed accurately.

