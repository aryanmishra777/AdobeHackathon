# Fix: robots.txt and AI crawler access

Starting points, not output. Edit against the bundle before putting any of this
in a report — a snippet with a placeholder left in it will be pasted into
production verbatim by someone.

## The decision to make first

Separate two questions the site owner may never have distinguished:

1. **Should assistants be able to cite us in answers today?** Almost always yes.
   Governed by the retrieval and search-index agents.
2. **Should our content train future models?** A real business decision with
   legal and commercial dimensions. Governed by the training agents.

A site can answer "yes" to the first and "no" to the second. Most sites that
have accidentally removed themselves from AI answers did so by writing one broad
rule intended to answer only the second question.

## Allow retrieval, opt out of training

```
# Assistants fetching a page because a user asked a question right now.
User-agent: ChatGPT-User
User-agent: OAI-SearchBot
User-agent: Claude-User
User-agent: Claude-SearchBot
User-agent: Perplexity-User
User-agent: PerplexityBot
Allow: /
Disallow: /cart
Disallow: /checkout
Disallow: /account

# Training-corpus collection. Remove this group to permit training.
User-agent: GPTBot
User-agent: Google-Extended
User-agent: CCBot
User-agent: Applebot-Extended
User-agent: meta-externalagent
Disallow: /

User-agent: *
Allow: /
Disallow: /cart
Disallow: /checkout
Disallow: /account
Disallow: /search

Sitemap: https://example.com/sitemap.xml
```

## Rules that bite

- **Directives do not accumulate across groups.** A crawler obeys exactly one
  group — the most specific one matching its token. An agent named in its own
  group ignores the `User-agent: *` group entirely, including its `Disallow`
  lines. This is the single most common robots.txt authoring error, and it cuts
  both ways: a narrow group written to allow one agent can silently drop the
  protections the wildcard group was providing.
- **Longest matching path wins**, whether `Allow` or `Disallow`. `Allow` breaks
  an exact-length tie.
- `Disallow:` with an empty value means allow everything.
- `$` anchors the path end; `*` is a wildcard.
- A missing or 404 robots.txt permits everything. A 5xx makes crawlers back off
  from the whole site.

## What not to recommend

- Do not tell a site to unblock `GPTBot`, `Google-Extended`, `CCBot`,
  `Applebot-Extended` or `meta-externalagent` as though the block were a bug.
  State the trade-off and let the owner decide.
- Do not claim `Google-Extended` affects Google Search or AI Overviews ranking.
  It is a Gemini training opt-out only.
- `robots.txt` is not access control. Never suggest it to protect private
  content — that needs authentication.
