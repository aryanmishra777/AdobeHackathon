# Fix: page weight, viewport, layout shift

These findings come from **static proxies read out of the HTML** -- counts of
render-blocking scripts, images without dimensions, the page's own transfer
size, the viewport tag. They are not Core Web Vitals. No LCP, CLS or performance
score was measured, and none should be quoted. Nothing here exceeds `medium` on
proxy evidence alone; a missing viewport tag is the one exception the rule
allows at `high`, because its effect is unambiguous.

Covers `STAY-008` (page weight), `STAY-009` (layout shift risk), `STAY-010`
(mobile viewport), `STAY-014` (third-party scripts).

## Mobile viewport (STAY-010)

Every page needs, in the `<head>`:

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

Without it, phones render the page at roughly 980px and shrink it to fit -- text
is unreadable, taps miss. Do **not** add `user-scalable=no` or
`maximum-scale=1`; disabling zoom locks out anyone who needs to enlarge text.
Mobile is most of the traffic an AI answer sends.

## Reserve space for images (STAY-009)

Declare intrinsic dimensions on every content image so the browser reserves its
space before it loads:

```html
<img src="/hero.jpg" width="1200" height="600" alt="...">
```

Or set `aspect-ratio` in CSS on the container. Prioritise images in the first
screen, where a shift is most disruptive -- a visitor about to click something
that then jumps mis-clicks and leaves. (CSS `aspect-ratio` also reserves space
and is invisible to this check, so treat a flagged image as a *risk*, not a
measured shift.)

## Keep the critical path light (STAY-008, STAY-014)

- Add `defer` or `async` to any script not needed for first paint -- especially
  third-party ones (tag managers, chat, A/B tools). Keep analytics; just stop it
  blocking render.
- Add `loading="lazy"` to below-the-fold images.
- Trim the HTML payload where it carries inlined data or markup bloat.

We do not fetch subresources, so individual script and image byte sizes are
usually unknown -- report counts and the page's own transfer size, nothing more.
