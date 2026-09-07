# Fix: the CDN blocks bots that robots.txt allows

The failure mode robots-only audits never see. `robots.txt` states policy; the
CDN enforces access. When they disagree, the CDN wins.

## Confirming it

```bash
curl -s -o /dev/null -w 'browser: %{http_code}\n' \
  -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' https://example.com/

curl -s -o /dev/null -w 'ChatGPT-User: %{http_code}\n' \
  -A 'Mozilla/5.0 (compatible; ChatGPT-User/1.0)' https://example.com/
```

A `200` is not sufficient evidence of success. A challenge page returns 200 and
contains no content:

```bash
curl -s -A 'Mozilla/5.0 (compatible; ClaudeBot/1.0)' https://example.com/ \
  | grep -icE 'just a moment|checking your browser|cf_chl|captcha|enable javascript'
```

## By provider

**Cloudflare.** Bot Fight Mode and Super Bot Fight Mode challenge non-browser
user-agents indiscriminately, AI crawlers included. Disable Bot Fight Mode, or
add a WAF custom rule that skips bot protection for the agents you want:

```
(http.user_agent contains "ChatGPT-User") or
(http.user_agent contains "OAI-SearchBot") or
(http.user_agent contains "Claude-User") or
(http.user_agent contains "Claude-SearchBot") or
(http.user_agent contains "PerplexityBot")
-> Skip: All remaining custom rules, Bot Fight Mode
```

Cloudflare also ships an "AI Scrapers and Crawlers" managed rule that blocks
these by default on some plans. Check it before concluding the config is clean.

**AWS WAF.** `AWSManagedRulesBotControlRuleSet` categorises AI crawlers as
non-browser traffic. Add a scope-down statement, or an allow rule matching the
user-agent strings ahead of the managed group.

**Akamai Bot Manager.** AI crawlers usually land in an uncategorised bucket that
inherits the default deny action. Move them to a category whose action is Allow.

**Fastly / custom VCL.** Look for user-agent allowlists that predate these
crawlers. The fix is to add the tokens, not to loosen the allowlist.

## Rate limiting

Rate limits are legitimate. If crawlers receive `429` rather than `403`, the fix
is a higher threshold for verified crawlers, not removing the limit. Note that
an audit's own probe can trigger a limit — report a 429-only result at medium
confidence and say the probe may have caused it.

## Verifying the fix

Re-run the curl commands and confirm a 200 whose body contains the main content,
not merely a 200.
