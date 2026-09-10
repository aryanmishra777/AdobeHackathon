# Fix: writing passages that survive retrieval

Retrieval pulls one passage out of the page and hands it to a model with none of
its surroundings — no heading above it, no paragraph before it, no page title.
A passage that only makes sense in place is a passage that never gets quoted.

This is the failure mode `QUOTE-001`, `QUOTE-002`, `QUOTE-004`, `QUOTE-008` and
`QUOTE-010` all describe from different angles. The fixes below are cheap: they
cost one clause per paragraph, not a rewrite.

## The rule

**Every paragraph names its own subject in its own first sentence.**

A reader who is dropped into the middle of the page — which is exactly what a
retrieval pipeline does — must be able to tell what the paragraph is about
without scrolling up.

## Before and after

| Retrieved alone, this fails | Because | Rewrite |
|---|---|---|
| "It starts at 29 a month and includes delivery." | "It" has no referent; 29 has no currency or unit; no subject | "The Explorer plan starts at GBP 29 per month and includes UK delivery." |
| "They also let you pick the grind." | "They" unresolved; no product named | "The Roaster plan also lets you choose the grind." |
| "As mentioned above, this is the one most people choose." | "above" and "this" break the moment the chunk is separated | "The Explorer plan is the most popular option." |
| "See the table below for the full breakdown." | "below" points at nothing once retrieved | "The plan comparison covers price, weight and grind options." |

## Concrete moves

1. **Replace opening pronouns with the noun.** `It`, `They`, `This`, `We`, `Our`
   at the start of a paragraph are the highest-value fixes. Name the product,
   the plan, the company.
2. **Bind every number to what it counts.** `29` becomes `GBP 29 per month`.
   `500` becomes `500g per delivery`. A bare figure in a retrieved chunk is a
   figure an assistant will not repeat, because it cannot say what it measures.
3. **Delete positional references.** `above`, `below`, `the following`,
   `as mentioned`, `see the section on…` all assume the reader can see the rest
   of the page. Replace with the thing itself, or with a stable cross-reference
   ("the plan comparison", not "the table below").
4. **State identity once per page, near the top.** One sentence of the form
   *"[Brand] is a [category] that [does what] for [whom]."* This is the sentence
   an assistant quotes when someone asks "what is [Brand]?" — if it is not on the
   page, the assistant guesses or picks a competitor who wrote theirs.
5. **Use one name for one thing.** Pick the brand or product name and use it
   verbatim in the title, the H1 and the body. A short form alongside the full
   form is fine; two unrelated-looking names for the same product is not.

## Where this does not apply

- Short list items and table rows legitimately lack a subject — the surrounding
  structure carries it. Do not pad them with the product name.
- Long-form editorial that deliberately builds an argument does not need every
  paragraph to stand alone. Apply the rule to pages whose job is to answer
  something: pricing, product, about, FAQ.
