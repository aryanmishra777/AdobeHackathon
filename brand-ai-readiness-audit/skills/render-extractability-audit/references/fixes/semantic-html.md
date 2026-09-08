# Fix: Semantic HTML, Headings, Landmarks & Encoding

Starting points, not output. Edit against the bundle before putting any of this
in a report — a snippet with a placeholder left in it will be pasted into
production verbatim by someone.

## The core problem

AI models and retrieval parsers rely on semantic markup to understand content
boundaries, main topics, and structural relationships. Div-soup architectures,
missing `<main>` landmarks, broken heading sequences, and undeclared character
encodings degrade parser accuracy and chunk segmentation.

## Heading Structure

Every page should present an orderly, hierarchical outline that describes its
content:

1. **Exactly one `<h1>` per page**: Naming the primary topic or purpose of the page.
2. **Logical nesting without skipping levels**: Follow `<h1>` with `<h2>`, and
   `<h2>` with `<h3>`. Never jump directly from `<h1>` to `<h3>` or `<h4>`.
3. **Descriptive, informative text**: Use headings that summarize the following section.

```html
<!-- Correct hierarchy -->
<main>
  <h1>Enterprise Cloud Security</h1>
  <section>
    <h2>Zero-Trust Architecture</h2>
    <p>Details about zero-trust network access...</p>
    <h3>Identity Verification</h3>
    <p>Multi-factor authentication protocols...</p>
  </section>
  <section>
    <h2>Compliance & Auditing</h2>
    <p>SOC 2 Type II and ISO 27001 certifications...</p>
  </section>
</main>
```

## HTML5 Semantic Landmarks & ARIA Roles

Retriever algorithms use `<main>`, `<article>`, and `<nav>` to strip chrome
(navigation bars, sidebars, cookie notices) and isolate genuine body text:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Acme Software</title>
</head>
<body>
  <header>
    <nav aria-label="Primary">
      <a href="/">Home</a>
      <a href="/pricing">Pricing</a>
    </nav>
  </header>

  <main>
    <article>
      <h1>Announcing Acme 2.0</h1>
      <p>Today we are releasing our new high-throughput analytics engine...</p>
    </article>
  </main>

  <footer>
    <p>&copy; 2026 Acme Corp. All rights reserved.</p>
  </footer>
</body>
</html>
```

## Character Encoding and Language Declarations

A missing or mismatched charset causes mojibake (garbled characters) that
destroys entity recognition and tokenization:

1. **Declare charset in HTTP header and HTML `<head>`**:
   - HTTP Response Header: `Content-Type: text/html; charset=utf-8`
   - HTML: `<meta charset="utf-8">` as the first element in `<head>`.
2. **Declare language on `<html>`**:
   - `<html lang="en">` (or appropriate BCP 47 language code).

