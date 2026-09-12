# Real-page fixtures

Trimmed snapshots of live pages that broke the extractor or an analyzer the
first time the marketplace met them. Produced by `tests/make_real_fixtures.py`
from an evidence bundle: every `<script>` except `application/ld+json` and every
`<style>` is removed, and the leading HTML comment records the source URL and
capture date. Third-party content, kept only as test input.

| Fixture | What it exercises |
|---|---|
| `nike-product.html` | `<svg><title>` after `</head>` must not override the title; `<h3>` inside `<a>` must not drop the link; Product JSON-LD; page type |
| `nike-category-noindex.html` | three robots meta tags (`noindex,nofollow` ×2 then `index,follow`) must all survive; 36 product anchors; ItemList → category |
| `crunchyroll-shell.html` | an app shell with 99 words of chrome and an "update your browser" message; identical documents hash the same once scripts are stripped |
| `adobe-acrobat-pro.html` | merch placeholders and fragment URLs where the price belongs; no `lang` |
| `adobe-offices.html` | an office directory is many locations, not inconsistent contact details |
| `adidas-block-page.html` | Akamai's failover 403 must register as a challenge |
| `boat-product-trailing-comma.html` | a JSON-LD `@graph` with a trailing comma: strict parse fails (PARSE-002), json5 recovers it when installed |

Refresh one with, for example:

    python tests/make_real_fixtures.py .audit/www.nike.in/run-01 p019 nike-product
