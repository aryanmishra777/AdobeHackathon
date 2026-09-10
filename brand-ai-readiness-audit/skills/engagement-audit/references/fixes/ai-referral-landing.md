# Fix: continuing the conversation a visitor arrives with

This is where the two halves of the audit meet. A visitor arriving from an AI
answer is not a cold search visitor: they already hold context and a specific
question the assistant partly answered. If the page they land on restarts that
conversation -- a generic home page, a hero unrelated to their question -- they
bounce, and every upstream stage that got the brand cited was wasted.

Covers `STAY-002`. Related to `STAY-001` (orientation) and `STAY-P01`/`P03`.

## Build a page per question, not just a home page

A home page is *allowed* to be general. The problem is when there is no
**specific** page to land on.

1. **Derive the questions from your own content and category.** What do sales and
   support actually get asked? What does a buyer in this category need to know
   before deciding? Do not invent a generic list -- an invented question
   produces an invented page nobody searches for.
2. **Give each question its own URL.** One clear question, one self-contained
   answer, in the first screen. Pricing structure. "Does it work with X."
   "How is this different from Y." Delivery and returns. Eligibility.
3. **Answer above the fold, elaborate below.** The first thing on the page is the
   answer, not a heading and not a hero. Detail, proof and secondary actions
   come after it.

The same page does double duty: it is what an assistant cites *and* where a
referred visitor should land. A site with these pages is discoverable and sticky;
a site without them is neither.

## Make the landing continuous

- The page's `<h1>` should echo the question, so the visitor sees a match.
- Put the direct answer in the opening sentence, then expand.
- Link onward to the natural next step for someone who just got that answer
  (from a "how much" page to "start", from a comparison to the product).

## Do not do this on a docs site

Documentation already answers specific questions by construction -- every
reference page is a deep landing page. `STAY-002` does not apply there.
