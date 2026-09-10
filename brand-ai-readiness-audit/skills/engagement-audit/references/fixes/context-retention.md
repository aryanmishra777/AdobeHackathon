# Fix: URL-carried search and filter state

When a visitor searches or filters to exactly what they want and the result set
does not appear in the URL, that state cannot be bookmarked, shared, linked to,
or recovered with the back button. The visitor who did the work to narrow things
down loses it, and abandons the task.

Covers `STAY-006` and `STAY-P02`.

*This is inferred from form markup and URL patterns -- JavaScript is not
executed -- so treat it as a strong hint, not a measurement.*

## Put the query in the URL

- Set the search form to `method="GET"`. The query then lands in the URL as
  `?q=...` with no extra code.
- If search is JS-driven, push the query into the URL with
  `history.pushState` / the History API on each search.

```html
<form action="/search" method="get" role="search">
  <input type="search" name="q" aria-label="Search the site">
  <button type="submit">Search</button>
</form>
```

## Reflect every active filter as a parameter

Each facet a visitor toggles should map to a query parameter:
`/shop?category=beans&roast=medium&sort=price`. Read the parameters back on load
so the URL fully reconstructs the view.

## Make the filtered URL a real page

A URL that reconstructs a meaningful result set should be:

- **Indexable** -- a canonical, crawlable page for combinations worth ranking.
- **Shareable** -- opening it in a fresh tab shows the same results.
- **Stable** -- the back button returns to the previous result set, not the
  unfiltered page.

Turning each meaningful combination into its own page also means each one can be
discovered on its own, which serves the discoverability half of the audit too.
