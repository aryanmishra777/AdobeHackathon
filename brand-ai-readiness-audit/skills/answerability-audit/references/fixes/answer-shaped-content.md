# Fix: answer-shaped content

An assistant answering a user's question needs a passage it can lift whole: a
self-contained unit that states one fact or answers one question without
depending on the rest of the page. Pages built as marketing narrative rarely
contain one. Pages built as questions-and-answers are made of nothing else.

This addresses `QUOTE-003`, `QUOTE-005`, `QUOTE-006`, `QUOTE-007`, `QUOTE-009`,
`QUOTE-011` and `QUOTE-012`.

## Add the page types assistants cite most

If the site has none of these, add the one that matches how buyers ask:

- **FAQ.** One question per heading, phrased the way a customer would type it.
  One self-contained answer per question, 40–80 words, repeating enough of the
  question that the answer stands alone. Source the questions from the support
  inbox and sales calls, not from a keyword tool.
- **Pricing.** State the structure even if exact figures are withheld:
  "per seat, billed annually, from GBP X". Saying nothing leaves an assistant to
  infer a number or to recommend a competitor who published theirs.
- **How it works / comparison.** A short, factual walkthrough or a comparison
  table. Both chunk cleanly because each row or step is independent.

## Put the answer first

The fact a page exists to convey belongs in the first screen, not after four
paragraphs of context. If a pricing page opens with brand philosophy and states
a number only halfway down, move the number up. Lead with the answer; follow
with the detail. A retrieval pipeline that grabs the first chunk should get the
point of the page.

## Make specifications structured

Comparable attributes — dimensions, weights, capacities, plan limits — belong in
a `<table>` or a `<dl>`, not in prose and not baked into an image. Structured
markup is extractable verbatim; a sentence listing six numbers is not, and an
image of a spec sheet is invisible (that case is `READ-004`, fix it there).

```html
<table>
  <caption>Plan comparison</caption>
  <thead><tr><th>Plan</th><th>Price</th><th>Coffee per month</th><th>Grind choice</th></tr></thead>
  <tbody>
    <tr><td>Explorer</td><td>GBP 29/month</td><td>250 g</td><td>No</td></tr>
    <tr><td>Roaster</td><td>GBP 49/month</td><td>500 g</td><td>Yes</td></tr>
  </tbody>
</table>
```

## Give long pages a summary a machine can lift

A page over ~900 words earns a 2–3 sentence summary or a "key takeaways" list
near the top. It is the block most likely to be retrieved and quoted, and it
costs three sentences. Treat this as an opportunity, not a defect — a missing
summary is not a bug on every long page.

## Write descriptive titles and headings

The `<title>` and `<h1>` should say what the page answers. "Pricing —
[Brand] coffee subscriptions from GBP 29/month" beats "Pricing". "Home",
"About" and "Contact" are conventional and understood — leave those alone.

## Gate every recommendation on what the business actually is

Do not tell a services firm it needs `Product` markup, a docs site it needs a
pricing page, or an enterprise brand that gates pricing behind sales that it has
an omission. When absence is plausibly deliberate, recommend stating the
*structure* of the missing fact rather than the fact itself, and keep it low
priority.
