# Fix: orientation

A visitor decides in a second or two whether they are in the right place. If the
top of the page does not tell them, and nothing tells them what to do or where
to go next, they leave.

Covers `STAY-001` (top of page says nothing), `STAY-003` (no clear next action),
`STAY-004` (dead-end pages), `STAY-005` (no sense of location), `STAY-011`
(unbroken walls of text), `STAY-012` (form friction), `STAY-013` (accessibility
basics), `STAY-015` (related content not linked).

## Say what this is, in the first line

Open every key page with one sentence: **what it is, for whom.** Not "Excellence,
delivered" -- "Small-batch coffee subscriptions, delivered across the UK."
The same sentence is the identity line an assistant quotes and the meta
description. Put it before any imagery-only hero.

## Give one clear next action

Each page should want one thing from the visitor. Make that one action a
prominent button; make everything else a text link. A page with six equal
buttons has no primary action, and a conversion page with none is a dead-end.
Editorial, docs and legal pages are exempt.

## End pages somewhere, not nowhere

Every content page needs 2-3 in-content links to where a visitor would go next --
from a feature page to pricing, from an article to related articles. These are
links in the body, not the header nav; global navigation is not a next step.
Contact, thank-you and legal pages are legitimate endpoints.

## Show where they are

On any site more than two levels deep, render a breadcrumb (`Home / Section /
Page`) at the top of deep pages and mirror it as `BreadcrumbList` JSON-LD. A
visitor who lands deep from a search or an AI link needs to see the section to
trust the page and explore sideways.

## Break up long pages

Add a descriptive subheading every 200-300 words; pull key points into short
lists; front-load each section with its conclusion. This is structural density
only -- it is not a judgement about typography or visual design.

## Keep first-touch forms short

A top-of-funnel form should ask for the fewest fields that work, often just an
email. Every required field is a reason to abandon. Checkout, account and
application forms legitimately need more -- move those after the visitor has
committed.

## Do the accessibility minimum

Give every input a `<label for>` or `aria-label`; wrap regions in `<header>`,
`<nav>`, `<main>`, `<footer>`. Then run a real accessibility audit -- these
mechanical checks are the floor, not the ceiling.

## Link related content

On a content site every page is an entry point. End each with an editorially
chosen "related" block of 3-5 links, in the HTML rather than injected
client-side.
