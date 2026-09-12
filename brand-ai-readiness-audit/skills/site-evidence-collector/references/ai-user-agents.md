# AI and search crawler user agents

The distinction this file encodes is the single most important false-positive
guard in the marketplace, and the one most audit tools get wrong.

**Blocking a training crawler is a business decision. Blocking a retrieval agent
removes the brand from live answers.** A publisher who deliberately opted out of
model training has not made a mistake, and telling them they have destroys the
credibility of the whole report. A brand that has accidentally blocked
`ChatGPT-User` has made a serious and usually unintentional mistake.

Always report the second. Never report the first as a defect.

## Purpose taxonomy

| Purpose | What it means | If blocked |
|---|---|---|
| `retrieval` | Fetches a page *right now* because a user asked a question this second. The content may be quoted in the answer. | **Defect.** The brand cannot appear in live AI answers. |
| `search-index` | Builds the search index that assistants query when they need sources. | **Defect.** Removes the brand from the retrieval pool. |
| `training` | Collects a corpus for future model training. No effect on today's answers. | **Not a defect.** Legitimate opt-out; report informationally at most. |
| `mixed` | Serves more than one purpose, or the operator has not clearly separated them. | Report as a trade-off, at `low`, and name both consequences. |

## The agents

| User-agent token | Operator | Purpose | Notes |
|---|---|---|---|
| `ChatGPT-User` | OpenAI | `retrieval` | Fetches when a user or a GPT follows a link during a conversation. |
| `OAI-SearchBot` | OpenAI | `search-index` | Builds the index behind ChatGPT search surfacing. |
| `GPTBot` | OpenAI | `training` | Corpus collection. Blocking is a common, deliberate choice. |
| `Claude-User` | Anthropic | `retrieval` | Fetches on behalf of a user's request in-conversation. |
| `Claude-SearchBot` | Anthropic | `search-index` | Indexes for search results surfaced to users. |
| `ClaudeBot` | Anthropic | `mixed` | Historically corpus-oriented; treat as `mixed` and name both effects. |
| `anthropic-ai` | Anthropic | `training` | Legacy token; still seen in the wild. |
| `PerplexityBot` | Perplexity | `search-index` | Builds Perplexity's index. |
| `Perplexity-User` | Perplexity | `retrieval` | Live fetch during a user's query. |
| `Googlebot` | Google | `search-index` | Blocking this is catastrophic and almost always accidental. |
| `Google-Extended` | Google | `training` | Gemini training opt-out **only**. Does **not** affect Google Search or AI Overviews ranking. Frequently misreported — do not. |
| `Bingbot` | Microsoft | `search-index` | Feeds Bing, and thereby several assistants. |
| `Amazonbot` | Amazon | `mixed` | Alexa and related surfaces. |
| `Applebot` | Apple | `search-index` | Siri and Spotlight. |
| `Applebot-Extended` | Apple | `training` | Apple Intelligence training opt-out only. |
| `meta-externalagent` | Meta | `training` | Meta AI corpus collection. |
| `CCBot` | Common Crawl | `training` | Feeds many downstream training corpora. |
| `Bytespider` | ByteDance | `training` | Widely blocked for crawl-aggressiveness reasons. |
| `cohere-ai` | Cohere | `training` | |
| `Diffbot` | Diffbot | `mixed` | Knowledge-graph extraction. |
| `omgili` / `omgilibot` | Webz.io | `training` | Data resale. |
| `Timpibot` | Timpi | `training` | |
| `YouBot` | You.com | `search-index` | |

## Resolution rules

`robots.txt` matching is token-based and case-insensitive. When resolving
whether an agent may fetch a path:

1. Find the group whose `User-agent` **most specifically** matches the token.
   An exact token match beats `*`. Only one group applies — directives do **not**
   accumulate across groups.
2. Within that group, the **longest matching path pattern** wins, regardless of
   whether it is `Allow` or `Disallow`.
3. On an exact tie in length, `Allow` wins.
4. `Disallow:` with an empty value means allow everything.
5. A missing or 4xx `robots.txt` means everything is allowed. A 5xx means the
   crawler should back off — treat as "unknown", not as "allowed", and record it
   as a finding in its own right.
6. `$` anchors the end of a path; `*` is a wildcard. Both are widely supported.

Record the resolved outcome for every token above in
`robots.agent_matrix`, along with which group matched, so `crawl-access-audit`
can cite the exact rule rather than re-deriving it.

## Beyond robots.txt

A permissive `robots.txt` does not mean a crawler can actually fetch. CDNs and
WAFs routinely serve `403`, a CAPTCHA, or a JS challenge to any request whose
user-agent is not a mainstream browser — regardless of what `robots.txt` says.
This is invisible to every audit tool that only parses `robots.txt`, and it is
common.

That is what `ua_probe.json` exists to catch: fetch one already-allowed URL with
a browser user-agent and again with each bot token, then compare status codes,
body sizes, and challenge signatures. A `200` that returns a challenge page is a
block in every way that matters.

The probe also sends two **control** names after the agents, recorded under
`ua_probe.json#controls`, so an analyzer can say what a refusal keys on without
anyone re-testing by hand:

- `BrandAIReadinessAudit-Control` — a name no rule lists. Served while the AI
  agents are refused means the rule keys on crawler names.
- `Bytespider` — an AI crawler no edge can verify by IP address. Refused while
  the unknown name is served means an AI-bot block by name (crunchyroll.com);
  served, with every *known* name refused or stalled, means impersonation
  defence on verified-bot names, which genuine agents pass from their published
  ranges and this probe cannot (adobe.com). `crawl-access-audit` withholds
  REACH-005 in that second case.

Challenge signatures worth matching in the body: `cf-browser-verification`,
`Just a moment...`, `Checking your browser`, `Attention Required! | Cloudflare`,
`__cf_chl`, `Access Denied`, `Request unsuccessful. Incapsula`, `Pardon Our
Interruption`, `perimeterx`, `datadome`.
