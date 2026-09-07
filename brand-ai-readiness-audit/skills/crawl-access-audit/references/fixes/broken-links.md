# Fix: broken internal links

## Priority order

1. **Links in primary navigation.** Followed from every page, so they cost the
   most crawl budget and the most user trust.
2. **Links from high-traffic pages.**
3. **Body-copy links elsewhere.**

## Fixing

- Point the link at the current URL. Editing the link beats adding a redirect.
- Where the destination genuinely moved and still receives traffic, add a `301`
  and update the links anyway.
- Where the destination is gone for good, remove the link and return `410` if
  the URL is still requested. `410` tells crawlers to stop asking; `404` invites
  them to keep trying.
- Never resolve a broken link by redirecting it to the home page. That is a soft
  404 — it returns 200 for content that does not exist, which is worse than the
  error it replaces because nothing can detect it automatically.

## Distinguishing causes

A `403` returned to a crawler user-agent is bot blocking, not a broken link.
Check the user-agent probe before attributing it here, or the fix gets applied
in entirely the wrong place.
