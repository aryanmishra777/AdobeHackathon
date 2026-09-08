# Page Titles, Descriptions & OpenGraph Metadata

Titles, meta descriptions, and OpenGraph tags form the primary summary card for search crawlers, social platforms, and AI retrieval agents.

## Page Titles & Headings (PARSE-010)

- **Substantive Alignment:** The `<title>` tag and primary `<h1>` heading should describe the same core subject matter.
- **Brand Suffixes:** Suffixes like ` | Brand Name` or ` - Company` are standard practice and not a conflict. The substantive portion before the separator should align with the `<h1>`.
- **Uniqueness:** Every indexable page must have a distinct `<title>`. Boilerplate titles repeated across pages cause indexing confusion.
- **Length Guidelines:** Aim for 30–65 characters. Short titles (<10 chars) are ambiguous; overly long titles (>70 chars) get truncated in search previews. Note: length issues alone are informational (`low` severity).

## Meta Descriptions

- **Clear Summaries:** Provide a concise 1–2 sentence summary (100–160 characters) explaining what the page provides.
- **AI Citation Value:** While meta descriptions are not a direct ranking factor, LLMs and assistants frequently use them as an introductory snippet when citing a source.

## Social Metadata & OpenGraph (PARSE-011)

OpenGraph tags (`og:title`, `og:description`, `og:image`, `og:url`) control snippet previews across social platforms and messaging apps.

### Key Rules
- **Consistency:** `og:title` and `og:description` must not contradict the HTML `<title>` or meta `description`.
- **Completeness:** Ensure each canonical page includes basic OpenGraph tags:

```html
<meta property="og:title" content="Northwind Coffee Subscription Pricing">
<meta property="og:description" content="Explore Northwind coffee subscription tiers starting from GBP 29 per month with free UK delivery.">
<meta property="og:url" content="https://example.com/pricing">
<meta property="og:type" content="website">
<meta property="og:image" content="https://example.com/images/pricing-card.jpg">
```

