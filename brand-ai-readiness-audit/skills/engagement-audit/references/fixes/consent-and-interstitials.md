# Fix: overlays that block on arrival

An interstitial on entry -- a modal, a newsletter pop-up, a consent wall that
covers the page -- costs the visitor an action before they have decided the page
is worth one. Many resolve that by leaving.

Covers `STAY-007`. We can only see overlays present in the **initial HTML**;
delayed pop-ups are invisible to this check.

## Serve the content, then layer the notice on top

The full page should render first. A required notice sits *over* served content,
not *instead of* it:

- Do not block scrolling or hide the main content behind the overlay.
- Keep the page readable and the primary action reachable while the notice is up.
- If the content is genuinely withheld until consent, that is a `READ-013`
  problem (a crawler and a first-time visitor both see nothing) and it is fixed
  there -- by serving the content and layering consent on top.

## Legally-required consent notices are not defects

Do not recommend removing a GDPR/CCPA banner. Recommend:

- Making it an overlay on fully-served content, not a wall.
- Defaulting to the least data collection, with a clear single "accept
  necessary" path.
- Not re-showing it on every page load once a choice is made.

## Promotional modals

Newsletter and discount modals on first view are the avoidable case. Move them
to an exit-intent trigger, a scroll-depth trigger, or an inline block in the
content. Never fire one before the visitor has seen the page.
