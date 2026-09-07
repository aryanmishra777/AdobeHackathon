# platform.claude.com Documentation (Part 21 of 35)

## Working with the API

Source: https://platform.claude.com/llms-full.txt#working-with-the-api

**Pagination cursors are bound to the query that issued them.** On the cost and usage endpoints, do not change query parameters mid-sequence: if you change `products[]`, `group_by[]`, `order_by`, the date range, or any filter and pass an old cursor, the request returns a 400 error. To change parameters, restart from the first page without a cursor.

**List parameters use bracket notation.** Repeat the parameter for each value, for example `products[]=chat&products[]=claude_code`.

**Amount fields are decimal strings in cents.** Currency amounts are returned as decimal strings such as `"41280.000000"` (which represents $412.80). To convert to dollars, parse as a decimal and divide by 100. Avoid binary floating-point parsing for values that may exceed several million dollars.

**Rate limits apply at the organization level**, not per key, with a default of 60 requests per minute across all endpoints in this API. If that is not sufficient for your use case, contact your Anthropic account team to discuss adjusting the limit.


## Versioning

Source: https://platform.claude.com/llms-full.txt#versioning-2

Send the `anthropic-version` header on every request; see [API versions](https://platform.claude.com/docs/en/api/versioning) for the available versions.


## Known limitations

Source: https://platform.claude.com/llms-full.txt#known-limitations

If your organization uses Claude Code through Amazon Bedrock, the Claude Enterprise Analytics API does not return Claude Code activity for that usage.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-88

<CardGroup cols={2}>
  <Card title="Claude Code Analytics API" href="https://platform.claude.com/docs/en/manage-claude/claude-code-analytics-api">
    Track Claude Code sessions, code changes, and tool usage with an Admin API key.
  </Card>

  <Card title="Usage and Cost API" href="https://platform.claude.com/docs/en/manage-claude/usage-cost-api">
    Track API token usage and costs for your organization.
  </Card>

  <Card title="Claude Enterprise Analytics API reference" href="https://platform.claude.com/docs/en/api/admin/analytics">
    Endpoint reference for engagement, adoption, and cost data.
  </Card>

  <Card title="Set up the Compliance API" href="https://platform.claude.com/docs/en/manage-claude/compliance-api-access">
    Audit and compliance data uses its own key types.
  </Card>
</CardGroup>


---
title: Claude Code Analytics API
url: https://platform.claude.com/docs/en/manage-claude/claude-code-analytics-api
description: Programmatically access your organization's Claude Code usage analytics and productivity metrics with the Claude Code Analytics Admin API.
---

<Tip>
  **The Admin API is unavailable for individual accounts.** To collaborate with teammates and add members, set up your organization in **Console → Settings → Organization**.
</Tip>

The Claude Code Analytics Admin API provides programmatic access to daily aggregated usage metrics for Claude Code users, enabling organizations to analyze developer productivity and build custom dashboards. This API provides more detail than the basic [Analytics dashboard](https://platform.claude.com/claude-code) without the complexity of the OpenTelemetry integration.

This API enables you to better monitor, analyze, and optimize your Claude Code adoption:

* **Developer productivity analysis:** Track sessions, lines of code added/removed, commits, and pull requests created using Claude Code
* **Tool usage metrics:** Monitor acceptance and rejection rates for different Claude Code tools (Edit, MultiEdit, Write, NotebookEdit)
* **Cost analysis:** View estimated costs and token usage broken down by Claude model
* **Custom reporting:** Export data to build executive dashboards and reports for management teams
* **Usage justification:** Provide metrics to justify and expand Claude Code adoption internally

<Check>
  **Admin API credentials required.** These endpoints are part of the Admin API. You can access them using an [Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys), an OAuth token with the `org:admin` scope, or a personal or service account key that isn't scoped to a workspace; workspace API keys don't work. See [Authentication](https://platform.claude.com/docs/en/manage-claude/admin-api#authentication) for details.
</Check>

<Note>
  **Claude Platform on AWS:** The Claude Code Analytics API is not currently available. View Claude Code usage on the **Usage** page in the Claude Console instead.
</Note>

<Note>
  **Claude Enterprise organizations:** Claude Code activity for claude.ai users is reported by the Claude Enterprise Analytics API, which uses an Analytics API key instead of an Admin API key. See [Analytics APIs](https://platform.claude.com/docs/en/manage-claude/analytics-api) to find which API and key type your organization needs.
</Note>


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-12

Get your organization's Claude Code analytics for a specific day:

```bash cURL
curl "https://api.anthropic.com/v1/organizations/usage_report/claude_code?\
starting_at=2025-09-08&\
limit=20" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

text wrap
  User-Agent: YourApp/1.0.0 (https://yourapp.com)
  ```
</Tip>


## Claude Code Analytics API

Source: https://platform.claude.com/llms-full.txt#claude-code-analytics-api

Track Claude Code usage, productivity metrics, and developer activity across your organization with the `/v1/organizations/usage_report/claude_code` endpoint.

### Key concepts

* **Daily aggregation:** Returns metrics for a single day specified by the `starting_at` parameter
* **User-level data:** Each record represents one user's activity for the specified day
* **Productivity metrics:** Track sessions, lines of code, commits, pull requests, and tool usage
* **Token and cost data:** Monitor usage and estimated costs broken down by Claude model
* **Cursor-based pagination:** Handle large datasets with stable pagination using opaque cursors
* **Data freshness:** Metrics are available with up to 1-hour delay for consistency

For complete parameter details and response schemas, see the [Claude Code Analytics API reference](https://platform.claude.com/docs/en/api/admin/usage_report/retrieve_claude_code).

### Basic examples

#### Get analytics for a specific day

```bash cURL
curl "https://api.anthropic.com/v1/organizations/usage_report/claude_code?\
starting_at=2025-09-08" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

bash cURL
# First request
curl "https://api.anthropic.com/v1/organizations/usage_report/claude_code?\
starting_at=2025-09-08&\
limit=20" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Subsequent request using cursor from response
curl "https://api.anthropic.com/v1/organizations/usage_report/claude_code?\
starting_at=2025-09-08&\
page=page_MjAyNS0wNS0xNFQwMDowMDowMFo=" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

json
{
  "data": [
    {
      "date": "2025-09-08T00:00:00Z",
      "actor": {
        "type": "user_actor",
        "email_address": "developer@company.com"
      },
      "organization_id": "dc9f6c26-b22c-4831-8d01-0446bada88f1",
      "customer_type": "api",
      "terminal_type": "vscode",
      "core_metrics": {
        "num_sessions": 5,
        "lines_of_code": {
          "added": 1543,
          "removed": 892
        },
        "commits_by_claude_code": 12,
        "pull_requests_by_claude_code": 2
      },
      "tool_actions": {
        "edit_tool": {
          "accepted": 45,
          "rejected": 5
        },
        "multi_edit_tool": {
          "accepted": 12,
          "rejected": 2
        },
        "write_tool": {
          "accepted": 8,
          "rejected": 1
        },
        "notebook_edit_tool": {
          "accepted": 3,
          "rejected": 0
        }
      },
      "model_breakdown": [
        {
          "model": "claude-opus-5",
          "tokens": {
            "input": 100000,
            "output": 35000,
            "cache_read": 10000,
            "cache_creation": 5000
          },
          "estimated_cost": {
            "currency": "USD",
            "amount": 141
          }
        }
      ]
    }
  ],
  "has_more": false,
  "next_page": null
}
```


## Pagination

Source: https://platform.claude.com/llms-full.txt#pagination-2

The API supports cursor-based pagination for organizations with large numbers of users:

1. Make your initial request with optional `limit` parameter.
2. If `has_more` is `true` in the response, use the `next_page` value in your next request.
3. Continue until `has_more` is `false`.

The cursor encodes the position of the last record and ensures stable pagination even as new data arrives. Each pagination session maintains a consistent data boundary to ensure you don't miss or duplicate records.


## Common use cases

Source: https://platform.claude.com/llms-full.txt#common-use-cases-3

* **Executive dashboards:** Create high-level reports showing Claude Code impact on development velocity
* **AI tool comparison:** Export metrics to compare Claude Code with other AI coding tools such as Copilot and Cursor
* **Developer productivity analysis:** Track individual and team productivity metrics over time
* **Cost tracking and allocation:** Monitor spending patterns and allocate costs by team or project
* **Adoption monitoring:** Identify which teams and users are getting the most value from Claude Code
* **ROI justification:** Provide concrete metrics to justify and expand Claude Code adoption internally


## Frequently asked questions

Source: https://platform.claude.com/llms-full.txt#frequently-asked-questions-2

### How fresh is the analytics data?

Claude Code analytics data typically appears within 1 hour of user activity completion. To ensure consistent pagination results, only data older than 1 hour is included in responses.

### Can I get real-time metrics?

No, this API provides daily aggregated metrics only. For real-time monitoring, consider using the [OpenTelemetry integration](https://code.claude.com/docs/en/monitoring-usage).

### How are users identified in the data?

Users are identified through the `actor` field in two ways:

* **`user_actor`:** Contains `email_address` for users who authenticate through OAuth (most common)
* **`api_actor`:** Contains `api_key_name` for users who authenticate with an API key

The `customer_type` field indicates whether the usage is from `api` customers (pay-as-you-go API) or `subscription` customers (Pro/Team plans).

### What's the data retention period?

Historical Claude Code analytics data is retained and accessible through the API. There is no specified deletion period for this data.

### Which Claude Code deployments are supported?

This API only tracks Claude Code usage on the Claude API. Usage through [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), [Claude on Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), or [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) is not included.

### What does it cost to use this API?

The Claude Code Analytics API is free to use for all organizations with access to the Admin API.

### How do I calculate tool acceptance rates?

Tool acceptance rate = `accepted / (accepted + rejected)` for each tool type. For example, if the edit tool shows 45 accepted and 5 rejected, the acceptance rate is 90%.

### What time zone is used for the date parameter?

All dates are in UTC. The `starting_at` parameter should be in YYYY-MM-DD format and represents UTC midnight for that day.


## See also

Source: https://platform.claude.com/llms-full.txt#see-also-7

The Claude Code Analytics API helps you understand and optimize your team's development workflow. Learn more about related features:

* [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api)
* [Admin API reference](https://platform.claude.com/docs/en/api/admin)
* [Claude Code Analytics dashboard](https://platform.claude.com/claude-code)
* [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api) - Track API usage across all Anthropic services
* [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) - Retrieve audit and activity data
* [Identity and access management](https://code.claude.com/docs/en/iam)
* [Monitoring usage with OpenTelemetry](https://code.claude.com/docs/en/monitoring-usage) for custom metrics and alerting


---
title: Rate Limits API
url: https://platform.claude.com/docs/en/manage-claude/rate-limits-api
description: Programmatically query your organization's API rate limits with the Rate Limits API.
---

<Tip>
  **The Admin API is unavailable for individual accounts.** To collaborate with teammates and add members, set up your organization in **Console → Settings → Organization**.
</Tip>

The Rate Limits API provides programmatic access to the rate limits configured for your organization and its workspaces. This is the same information shown on the [Rate limits](https://platform.claude.com/settings/limits) page in the Claude Console.

Use this API to:

* **Keep gateways and proxies in sync:** Read your current limits at startup and on a schedule instead of hardcoding values that drift when Anthropic adjusts them.
* **Power internal alerting:** Compare usage data from the [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api) against your configured limits.
* **Audit workspace configuration:** Verify that workspace overrides match what your provisioning automation expects.

<Check>
  **Admin API credentials required.** These endpoints are part of the Admin API. You can access them using an [Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys), an OAuth token with the `org:admin` scope, or a personal or service account key that isn't scoped to a workspace; workspace API keys don't work. See [Authentication](https://platform.claude.com/docs/en/manage-claude/admin-api#authentication) for details.
</Check>


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-13

List the rate limits configured for your organization:

```bash cURL
curl "https://api.anthropic.com/v1/organizations/rate_limits" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```


## Organization rate limits

Source: https://platform.claude.com/llms-full.txt#organization-rate-limits

The `/v1/organizations/rate_limits` endpoint returns the rate limits applied at the organization level for the Messages API and its supporting resources. Limits for other products, such as [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview), are not included.

### Key concepts

* **Rate limit groups:** Each entry in the response represents one rate limit group. Model rate limits are grouped so that several model versions share a single set of limits, and other groups cover resources such as the Message Batches API, the Files API, the Token Counting API, agent skills, and the web search tool.
* **`group_type`:** Identifies which category of limits the entry covers. See [Filtering by group type](https://platform.claude.com/docs/en/manage-claude/rate-limits-api#filtering-by-group-type) for the list of values.
* **`models` list:** For `model_group` entries, the `models` field lists every model ID and alias that counts against that group's limits. Use this list to look up which group any model string falls under. For other group types, `models` is `null`.
* **`limits` list:** Each group carries a list of `{type, value}` pairs. The `type` field identifies the limiter (such as `requests_per_minute`, `input_tokens_per_minute`, or `output_tokens_per_minute`) and `value` is the configured limit. See [Rate limits](https://platform.claude.com/docs/en/api/rate-limits) for how each limiter is measured and enforced.

For complete parameter details and response schemas, see the [Organization Rate Limits API reference](https://platform.claude.com/docs/en/api/admin/rate_limits/list).

### List all organization rate limits

```bash cURL
curl "https://api.anthropic.com/v1/organizations/rate_limits" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

json
{
  "data": [
    {
      "type": "rate_limit",
      "group_type": "model_group",
      "models": ["claude-opus-5"],
      "limits": [
        { "type": "requests_per_minute", "value": 4000 },
        { "type": "input_tokens_per_minute", "value": 10000000 },
        { "type": "output_tokens_per_minute", "value": 800000 }
      ]
    },
    {
      "type": "rate_limit",
      "group_type": "model_group",
      "models": [
        "claude-opus-4-5",
        "claude-opus-4-5-20251101",
        "claude-opus-4-6",
        "claude-opus-4-7",
        "claude-opus-4-8"
      ],
      "limits": [
        { "type": "requests_per_minute", "value": 4000 },
        { "type": "input_tokens_per_minute", "value": 10000000 },
        { "type": "output_tokens_per_minute", "value": 800000 }
      ]
    },
    {
      "type": "rate_limit",
      "group_type": "batch",
      "models": null,
      "limits": [{ "type": "enqueued_batch_requests", "value": 500000 }]
    }
  ],
  "next_page": null
}

bash cURL
curl "https://api.anthropic.com/v1/organizations/rate_limits?model=claude-opus-5" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

If the model string doesn't match any group, the endpoint returns a 404 error. The `model` parameter is supported on the organization endpoint only; the workspace endpoint doesn't accept it.


## Workspace rate limits

Source: https://platform.claude.com/llms-full.txt#workspace-rate-limits

The `/v1/organizations/workspaces/{workspace_id}/rate_limits` endpoint returns the rate limit overrides configured for a single workspace.

The response only includes overrides, so anything missing from it is inherited from the organization:

* A group that is absent from `data` has no workspace override at all. The workspace inherits the organization-level limits for that group (it is not unlimited).
* Within a group that is present, a limiter type that is absent from `limits[]` has no workspace override for that limiter. The workspace inherits the organization value for it.
* For each limiter that is present, `org_limit` is the organization-level value for the same limiter, or `null` if the organization has no configured limit for that limiter type.

For complete parameter details and response schemas, see the [Workspace Rate Limits API reference](https://platform.claude.com/docs/en/api/admin/workspaces/rate_limits/list).

<Tip>
  To retrieve your organization's workspace IDs, use the [List Workspaces](https://platform.claude.com/docs/en/api/admin/workspaces/list) endpoint, or find them in the [Claude Console](https://platform.claude.com/settings/workspaces). The default workspace cannot have rate limit overrides, so it has no entry on this endpoint; use the organization endpoint to read its limits.
</Tip>

```bash cURL
curl "https://api.anthropic.com/v1/organizations/workspaces/wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ/rate_limits" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

json
{
  "data": [
    {
      "type": "workspace_rate_limit",
      "group_type": "model_group",
      "models": ["claude-opus-5"],
      "limits": [
        { "type": "requests_per_minute", "value": 1000, "org_limit": 4000 },
        { "type": "input_tokens_per_minute", "value": 500000, "org_limit": 10000000 }
      ]
    },
    {
      "type": "workspace_rate_limit",
      "group_type": "model_group",
      "models": [
        "claude-opus-4-5",
        "claude-opus-4-5-20251101",
        "claude-opus-4-6",
        "claude-opus-4-7",
        "claude-opus-4-8"
      ],
      "limits": [
        { "type": "requests_per_minute", "value": 1000, "org_limit": 4000 },
        { "type": "input_tokens_per_minute", "value": 500000, "org_limit": 10000000 }
      ]
    }
  ],
  "next_page": null
}
```


## Filtering by group type

Source: https://platform.claude.com/llms-full.txt#filtering-by-group-type

Both endpoints accept an optional `group_type` query parameter that restricts the response to a single category:

```bash cURL
curl "https://api.anthropic.com/v1/organizations/rate_limits?group_type=batch" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

Valid values are `model_group`, `batch`, `token_count`, `files`, `skills`, and `web_search`.


## Pagination

Source: https://platform.claude.com/llms-full.txt#pagination-3

Both endpoints accept a `page` query parameter and return a `next_page` field. Responses are currently always a single page, so `next_page` is `null`. Loop on `next_page` so your client paginates correctly without changes when the response grows.


## Frequently asked questions

Source: https://platform.claude.com/llms-full.txt#frequently-asked-questions-3

### Which model strings appear in the `models` list?

Every model ID and alias that counts against the group, including dated IDs (such as `claude-sonnet-4-5-20250929`) and undated aliases (such as `claude-sonnet-4-5`). Look up any model string you pass to the Messages API and you'll find it in exactly one `model_group` entry.

### What does it mean if a group is missing from the workspace response?

The workspace has no override for that group and inherits the organization-level limit. Query the organization endpoint to see the inherited values.

### Can I update rate limits with this API?

No. To set workspace rate limits, open the workspace in the [Claude Console](https://platform.claude.com/settings/workspaces) and use the **Rate limits** tab.


## See also

Source: https://platform.claude.com/llms-full.txt#see-also-8

* [Rate limits](https://platform.claude.com/docs/en/api/rate-limits)
* [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api)
* [Admin API reference](https://platform.claude.com/docs/en/api/admin)
* [Workspaces](https://platform.claude.com/docs/en/manage-claude/workspaces)
* [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api)


---
title: Spend Limits API
url: https://platform.claude.com/docs/en/manage-claude/spend-limits-api
description: Set a spend limit on each Claude Enterprise member, see where each member's spend limit is inherited from, and review or act on members' requests for a higher limit.
---

The Spend Limits API lets you set a spend limit on each Claude Enterprise member, see where each member's spend limit is inherited from, and review or act on members' requests for a higher limit.

For per-user and time-bucketed usage and cost *reporting*, see [Analytics APIs](https://platform.claude.com/docs/en/manage-claude/analytics-api).

<Check>
  **Scoped Admin API key required**

  These endpoints require an Admin API key with the `read:spend_limits` scope (for `GET` endpoints) or the `write:spend_limits` scope (for `POST` and `DELETE` endpoints). See [Create an Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys#create-a-key-for-a-claude-enterprise-organization) for where your primary owner creates one and which scopes to select. Pass the key in the `x-api-key` header on every request, together with the [`anthropic-version`](https://platform.claude.com/docs/en/api/versioning) header.
</Check>

<Note>
  The Spend Limits API is available to Claude Enterprise organizations only. It is not available to Claude Platform (Claude Console) organizations.
</Note>


## Overview

Source: https://platform.claude.com/llms-full.txt#overview-6

The API exposes eight endpoints across two resources:

| Resource                          | Endpoints                                                                                                                                                                                                                                             | Use for                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Spend limits**                  | `GET /v1/organizations/spend_limits/effective` `GET /v1/organizations/spend_limits/{spend_limit_id}` `POST /v1/organizations/spend_limits` `DELETE /v1/organizations/spend_limits/{spend_limit_id}`                                                   | Read each member's effective spend limit and period-to-date spend; set or clear a per-user override.              |
| **Spend limit increase requests** | `GET /v1/organizations/spend_limit_increase_requests` `GET /v1/organizations/spend_limit_increase_requests/{id}` `POST /v1/organizations/spend_limit_increase_requests/{id}/approve` `POST /v1/organizations/spend_limit_increase_requests/{id}/deny` | List members' requests for a higher spend limit, with the context needed to decide; approve or deny each request. |

Use the **spend limits** endpoints to answer "what spend limit applies to each member, where does it come from, and how close are they to it?" and to set a per-user override. Use the **spend limit increase requests** endpoints to work the queue of member-submitted requests.


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-17

* Your organization must be on a Claude Enterprise plan.
* Usage credits must be turned on for your organization. Your primary owner can turn them on in claude.ai billing settings.


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-14

List every member's effective monthly spend limit and period-to-date spend:

```bash cURL
curl "https://api.anthropic.com/v1/organizations/spend_limits/effective?limit=20" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --header "anthropic-version: 2023-06-01"
```


## Key concepts

Source: https://platform.claude.com/llms-full.txt#key-concepts-3

### The spend limit hierarchy

An **effective spend limit** applies to each member's spend, resolved from a hierarchy of scope levels. When a member has no per-user override, they inherit the spend limit configured for their group (if your organization uses group-based limits), their seat tier, or the organization-wide default. A group spend limit is a per-member default: each member inheriting it is gated against their own spend, not a pooled group budget.

Reading `GET /v1/organizations/spend_limits/effective` returns every current member with their resolved effective spend limit, where that limit was resolved from (`source`), and their period-to-date spend. Setting a per-user override with `POST /v1/organizations/spend_limits` pins a member to a specific spend limit regardless of what they would otherwise inherit. Deleting the override returns them to the inherited spend limit (or leaves them unlimited if none exists).

The `source` field on each member's row tells you which level their spend limit resolved from: `user` (a per-user override), `seat_tier`, `rbac_group`, or `organization`. Treat scope types as an open set; fall through on unknown values rather than failing.

### Period

`period` is the recurring window over which the spend limit is enforced and spend resets. A spend limit is identified by its `(scope, period)` pair. Currently `monthly` is the only supported period; monthly spend resets at 00:00 UTC on the first of each calendar month. Treat `period` as an open set.

### Amounts and currency

All monetary values are strings in **minor units of the organization's billing currency** (cents, for USD). For example, `"50000"` represents 500.00 USD. Parse as a decimal and divide by 100 to display dollars; avoid binary floating-point for large values.

`amount` is **nullable**. In a member's effective row, `null` means **unlimited** (no spend limit) and `"0"` means the member cannot use Claude beyond their plan's included usage. On a configured spend-limit row (as returned by `GET /v1/organizations/spend_limits/{id}`), `null` only means no numeric spend limit is set; read the member's effective row to distinguish unlimited from included-usage-only.

`period_to_date_spend` is the member's spend accrued since the start of the current `period`, in the same minor-unit format; it may include a fractional part (for example, `"41280.125"`). It may read as `"0"` if the spend reading is temporarily unavailable; treat it as informational, not transactional.

### Increase request lifecycle

A **spend limit increase request** is created when a member clicks **Request more usage** in claude.ai. Requests are not created through this API. A request's `status` is one of:

| Status     | Meaning                                                                                                                                                                                                                                  |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pending`  | Awaiting admin action. The request normally carries a live `spend_summary` so you can see the member's current effective spend limit and period-to-date spend while deciding; `spend_summary` may be `null` if it could not be computed. |
| `approved` | The request was resolved with approval: either an admin approved it explicitly, another admin action raised the member's spend limit, or Anthropic support raised a spend limit on the organization's behalf. `spend_summary` is `null`. |
| `denied`   | An admin declined. `spend_summary` is `null`. claude.ai hides that member's request button for 30 days from `resolved_at`; an admin can still raise the member's spend limit directly at any time.                                       |

Both `approved` and `denied` are terminal. A member has at most one `pending` request at a time.

Approving with `POST /v1/organizations/spend_limit_increase_requests/{id}/approve` writes the same per-user spend limit row that `POST /v1/organizations/spend_limits` writes. Setting a spend limit directly does **not** transition a pending request; use the approve endpoint to resolve a request.

By default, Anthropic emails the member when their request is approved or denied. Pass `suppress_notification: true` on approve or deny to suppress that email (for example, when your own system notifies the member).


## Versioning

Source: https://platform.claude.com/llms-full.txt#versioning-3

Send the `anthropic-version` header on every request; see [API versions](https://platform.claude.com/docs/en/api/versioning) for the available versions.


## Rate limiting

Source: https://platform.claude.com/llms-full.txt#rate-limiting

All eight endpoints share a single per-organization limit of **60 requests per minute**. Requests over the limit return **429 Too Many Requests**.


## Pagination

Source: https://platform.claude.com/llms-full.txt#pagination-4

`GET /v1/organizations/spend_limits/effective` and `GET /v1/organizations/spend_limit_increase_requests` are paginated with an **opaque cursor**. The first request returns up to `limit` rows plus a `next_page` cursor; pass that cursor unchanged as the `page` parameter on the next request, and repeat until `next_page` is `null`.

**Do not change query parameters mid-sequence.** Cursors are bound to the filters that issued them. If you change `user_ids[]`, `period[]`, `status[]`, or `actor_ids[]` and pass an old cursor, you'll get a 400 with *"cursor does not match current query parameters"*. Start a new sequence from the first page instead.


## Serializing list parameters

Source: https://platform.claude.com/llms-full.txt#serializing-list-parameters

List parameters use bracket notation: repeat the parameter name with `[]` for each value.

```text wrap
user_ids[]=user_01AbCdEfGh&user_ids[]=user_01JkLmNoPq
```


## Error responses

Source: https://platform.claude.com/llms-full.txt#error-responses-2

Error responses follow the standard shape documented in [Errors](https://platform.claude.com/docs/en/api/errors). Quote the `request_id` from the response body when contacting support.


## Spend limits

Source: https://platform.claude.com/llms-full.txt#spend-limits

### List each member's effective spend limit

`GET /v1/organizations/spend_limits/effective` returns one row per current member, reflecting each member's effective spend limit, its `source` in the scope hierarchy, and their `period_to_date_spend`. Requires the `read:spend_limits` scope.

For complete parameter details and response schemas, see [List effective spend limits](https://platform.claude.com/docs/en/api/admin/spend_limits/list_effective) in the API reference.

```bash cURL
curl "https://api.anthropic.com/v1/organizations/spend_limits/effective?limit=20" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --header "anthropic-version: 2023-06-01"

json
{
  "data": [
    {
      "scope": { "type": "user", "user_id": "user_01AbCdEfGh" },
      "actor": {
        "type": "user_actor",
        "user_id": "user_01AbCdEfGh",
        "name": "Jane Smith",
        "email_address": "jane@example.com",
        "deleted": false
      },
      "amount": "50000",
      "currency": "USD",
      "period": "monthly",
      "source": { "type": "seat_tier", "seat_tier": "enterprise_standard" },
      "spend_limit_id": "spl_01XyZaBcDeFgHiJkLmNoPq",
      "period_to_date_spend": "31402.5"
    }
  ],
  "next_page": "page_..."
}

bash cURL
curl "https://api.anthropic.com/v1/organizations/spend_limits/spl_01AbCdEfGhIjKlMnOpQrSt" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --header "anthropic-version: 2023-06-01"

bash cURL
curl --request POST "https://api.anthropic.com/v1/organizations/spend_limits" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --data '{"scope": {"type": "user", "user_id": "user_01AbCdEfGh"}, "amount": "75000"}'

json
{
  "type": "spend_limit",
  "id": "spl_01RsTuVwXyZaBcDeFgHiJk",
  "created_at": "2026-05-11T10:02:44Z",
  "updated_at": "2026-05-11T10:02:44Z",
  "scope": { "type": "user", "user_id": "user_01AbCdEfGh" },
  "amount": "75000",
  "currency": "USD",
  "period": "monthly"
}

bash cURL
curl --request DELETE "https://api.anthropic.com/v1/organizations/spend_limits/spl_01RsTuVwXyZaBcDeFgHiJk" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --header "anthropic-version: 2023-06-01"
```


## Spend limit increase requests

Source: https://platform.claude.com/llms-full.txt#spend-limit-increase-requests

### List increase requests

`GET /v1/organizations/spend_limit_increase_requests` lists requests, most recent first. Filter by `status[]` (`pending`, `approved`, `denied`) and `actor_ids[]`. The list excludes requests whose requester is no longer a member of the organization. Requires the `read:spend_limits` scope.

For complete parameter details and response schemas, see [List spend limit increase requests](https://platform.claude.com/docs/en/api/admin/spend_limits/increase_requests/list) in the API reference.

```bash cURL
curl --globoff "https://api.anthropic.com/v1/organizations/spend_limit_increase_requests?status[]=pending&limit=50" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --header "anthropic-version: 2023-06-01"

bash cURL
curl "https://api.anthropic.com/v1/organizations/spend_limit_increase_requests/slir_01AbCdEfGhIjKlMnOpQrSt" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --header "anthropic-version: 2023-06-01"

bash cURL
curl --request POST "https://api.anthropic.com/v1/organizations/spend_limit_increase_requests/slir_01AbCdEfGhIjKlMnOpQrSt/approve" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --data '{"amount": "75000", "suppress_notification": true}'

bash cURL
curl --request POST "https://api.anthropic.com/v1/organizations/spend_limit_increase_requests/slir_01AbCdEfGhIjKlMnOpQrSt/deny" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --data '{"suppress_notification": true}'
```


## Example workflows

Source: https://platform.claude.com/llms-full.txt#example-workflows-2

Some of these workflows combine the Spend Limits API with the [Analytics APIs](https://platform.claude.com/docs/en/manage-claude/analytics-api) cost endpoints. The Analytics cost endpoints are designed for organization-wide spend reporting across a date range. `GET /spend_limits/effective` returns the cap that currently applies to each member. Start a sweep with Analytics to discover which members to look at, then read their current caps with `/effective`.

Spend Limits endpoints require the `spend_limits` scopes and Analytics cost endpoints require `read:analytics`; see [Analytics APIs](https://platform.claude.com/docs/en/manage-claude/analytics-api) for how to provision access. All monetary values on both are decimal strings in minor units (cents). Both APIs paginate with an opaque cursor. Set an explicit `limit` and page through `next_page` until it's `null` to cover the whole organization.

### Automate the increase-request review flow

Run a scheduled job that fetches pending requests, applies your organization's approval policy, and resolves each one.

1. List pending requests:

   ```bash cURL
   curl --globoff "https://api.anthropic.com/v1/organizations/spend_limit_increase_requests?status[]=pending&limit=100" \
     --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
     --header "anthropic-version: 2023-06-01"

bash cURL
   curl --request POST "https://api.anthropic.com/v1/organizations/spend_limit_increase_requests/{id}/approve" \
     --header "content-type: application/json" \
     --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --data '{"amount": "75000", "suppress_notification": true}'

bash cURL
   curl "https://api.anthropic.com/v1/organizations/analytics/user_cost_report?starting_at=2026-06-01T00:00:00Z&limit=1000" \
     --header "x-api-key: $ANALYTICS_API_KEY" \
     --header "anthropic-version: 2023-06-01"

bash cURL
   curl --globoff "https://api.anthropic.com/v1/organizations/spend_limits/effective?user_ids[]=user_01Ab...&user_ids[]=user_01Cd...&limit=100" \
     --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
     --header "anthropic-version: 2023-06-01"

bash cURL
   curl "https://api.anthropic.com/v1/organizations/analytics/user_cost_report?starting_at=2026-06-09T00:00:00Z&ending_at=2026-06-23T00:00:00Z&bucket_width=1d&limit=1000" \
     --header "x-api-key: $ANALYTICS_API_KEY" \
     --header "anthropic-version: 2023-06-01"

bash cURL
   curl --globoff "https://api.anthropic.com/v1/organizations/spend_limits/effective?user_ids[]=user_01AbCdEfGh&period[]=monthly" \
     --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
     --header "anthropic-version: 2023-06-01"

bash cURL
   curl --request POST "https://api.anthropic.com/v1/organizations/spend_limits" \
     --header "content-type: application/json" \
     --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --data '{"scope": {"type": "user", "user_id": "user_01AbCdEfGh"}, "amount": "500000", "period": "monthly"}'

bash cURL
   curl --request POST "https://api.anthropic.com/v1/organizations/rbac_groups/rbac_group_01UvWxYzAbCdEfGhIjKlMn/members" \
     --header "content-type: application/json" \
     --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --data '{"user_id": "user_01AbCdEfGh"}'
   ```

   See [User management](https://platform.claude.com/docs/en/manage-claude/user-management#groups) for the group endpoints.

4. When your incident system marks the incident closed, roll both changes back: restore the spend limit you recorded in step 1 (or delete the override with `DELETE /v1/organizations/spend_limits/{spend_limit_id}` if the member had none), and remove the member from the group with `DELETE /v1/organizations/rbac_groups/{group_id}/members/{user_id}`.


## Frequently asked questions

Source: https://platform.claude.com/llms-full.txt#frequently-asked-questions-4

### Does setting a spend limit directly resolve a member's pending increase request?

No. `POST /v1/organizations/spend_limits` writes the override but leaves the pending request untouched. Use `POST /v1/organizations/spend_limit_increase_requests/{id}/approve` to resolve the request and write the override in one call.

### What happens when I delete a per-user override?

The member falls back to whatever they'd inherit from the hierarchy: their group, seat-tier, or organization default. If no default exists at any level, the member is unlimited.

### Can I set a seat-tier or organization-wide default through this API?

No. Only per-user overrides can be written through this API. Seat-tier, group, and organization-level defaults are configured in claude.ai Organization settings.

### Why does `period_to_date_spend` sometimes read as `"0"` for an active member?

The spend reading can be temporarily unavailable, in which case the field reads `"0"` rather than erroring. Treat it as informational.


## See also

Source: https://platform.claude.com/llms-full.txt#see-also-9

<CardGroup cols={2}>
  <Card title="Spend Limits API reference" href="https://platform.claude.com/docs/en/api/admin/spend_limits">
    Generated request and response schemas for every Spend Limits API endpoint.
  </Card>

  <Card title="Spend Limit Increase Requests API reference" href="https://platform.claude.com/docs/en/api/admin/spend_limits/increase_requests">
    Generated request and response schemas for the increase-request endpoints.
  </Card>

  <Card title="Analytics APIs" href="https://platform.claude.com/docs/en/manage-claude/analytics-api">
    Per-user and time-bucketed usage and cost reporting for Claude Enterprise.
  </Card>
</CardGroup>


---
title: Usage and Cost API
url: https://platform.claude.com/docs/en/manage-claude/usage-cost-api
description: Programmatically access your organization's API usage and cost data with the Usage & Cost Admin API.
---

<Tip>
  **The Admin API is unavailable for individual accounts.** To collaborate with teammates and add members, set up your organization in **Console → Settings → Organization**.
</Tip>

The Usage & Cost Admin API provides programmatic and granular access to historical API usage and cost data for your organization. This data is similar to the information available in the [Usage](https://platform.claude.com/usage) and [Cost](https://platform.claude.com/cost) pages of the Claude Console.

This API enables you to better monitor, analyze, and optimize your Claude implementations:

* **Accurate usage tracking:** Get precise token counts and usage patterns instead of relying solely on response token counting
* **Cost reconciliation:** Match internal records with Anthropic billing for finance and accounting teams
* **Product performance and improvement:** Monitor product performance while measuring if changes to the system have improved it, or set up alerting
* **[Rate limit](https://platform.claude.com/docs/en/api/rate-limits) optimization:** Optimize features like [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) or specific prompts to make the most of your allocated capacity.
* **Advanced analysis:** Perform deeper data analysis than what's available in Console

<Check>
  **Admin API credentials required.** These endpoints are part of the Admin API. You can access them using an [Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys), an OAuth token with the `org:admin` scope, or a personal or service account key that isn't scoped to a workspace; workspace API keys don't work. See [Authentication](https://platform.claude.com/docs/en/manage-claude/admin-api#authentication) for details.
</Check>

Claude Enterprise organizations use an Analytics API key with a different API instead; see [Which API do you need?](https://platform.claude.com/docs/en/manage-claude/usage-cost-api#which-api-do-you-need).

<Note>
  **Claude Platform on AWS:** The programmatic Usage and Cost API endpoints are not currently available. View usage and cost data on the **Usage** and **Cost** pages in the Claude Console instead.
</Note>


## Which API do you need?

Source: https://platform.claude.com/llms-full.txt#which-api-do-you-need-2

Anthropic provides cost and usage reporting through two APIs, depending on which Claude product your organization manages:

| Your organization                | API                                                                                                                     | Key type                                                                                                                                           |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Console (Claude Platform) | The Usage and Cost Admin API described on this page                                                                     | Admin API key (`sk-ant-admin01-...`) or another [Admin API credential](https://platform.claude.com/docs/en/manage-claude/admin-api#authentication) |
| Claude Enterprise (claude.ai)    | The [Claude Enterprise Analytics API](https://platform.claude.com/docs/en/api/admin/analytics) cost and usage endpoints | Analytics API key                                                                                                                                  |

Claude Enterprise parent organizations do not appear in Claude Console and carry no Admin API keys, so for them the Analytics API key is the only path to this data. See [Analytics APIs](https://platform.claude.com/docs/en/manage-claude/analytics-api) for how to create each key type and which plans the Claude Enterprise cost data applies to.


## Partner solutions

Source: https://platform.claude.com/llms-full.txt#partner-solutions

Leading observability platforms offer ready-to-use integrations for monitoring your Claude API usage and cost, without writing custom code. These integrations provide dashboards, alerting, and analytics to help you manage your API usage effectively.

<CardGroup cols={3}>
  <Card title="CloudZero" icon="chart" href="https://docs.cloudzero.com/docs/connections-anthropic">
    Cloud intelligence platform for tracking and forecasting costs
  </Card>

  <Card title="Datadog" icon="chart" href="https://docs.datadoghq.com/integrations/anthropic/">
    LLM Observability with automatic tracing and monitoring
  </Card>

  <Card title="Grafana Cloud" icon="chart" href="https://grafana.com/docs/grafana-cloud/monitor-infrastructure/integrations/integration-reference/integration-anthropic/">
    Agentless integration for easy LLM observability with out-of-the-box dashboards and alerts
  </Card>

  <Card title="Harness" icon="chart" href="https://developer.harness.io/docs/cloud-cost-management/provider-integrations/ai-providers/anthropic/">
    FinOps platform for cloud and AI cost management
  </Card>

  <Card title="Honeycomb" icon="polygon" href="https://docs.honeycomb.io/integrations/anthropic-usage-monitoring/">
    Advanced querying and visualization through OpenTelemetry
  </Card>

  <Card title="Vantage" icon="chart" href="https://docs.vantage.sh/connecting_anthropic">
    FinOps platform for LLM cost & usage observability
  </Card>
</CardGroup>


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-15

Get your organization's daily usage for the last 7 days:

```bash cURL
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-08T00:00:00Z&\
ending_at=2025-01-15T00:00:00Z&\
bucket_width=1d" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

text wrap
  User-Agent: YourApp/1.0.0 (https://yourapp.com)
  ```
</Tip>


## Usage API

Source: https://platform.claude.com/llms-full.txt#usage-api

Track token consumption across your organization with detailed breakdowns by model, workspace, and service tier with the `/v1/organizations/usage_report/messages` endpoint.

### Key concepts

* **Time buckets:** Aggregate usage data in fixed intervals (`1m`, `1h`, or `1d`)
* **Token tracking:** Measure uncached input, cached input, cache creation, and output tokens
* **Filtering & grouping:** Filter by API key, workspace, model, service tier, context window, [data residency](https://platform.claude.com/docs/en/manage-claude/data-residency), or speed (beta), and group results by these dimensions
* **Server tool usage:** Track usage of server-side tools such as web search

For complete parameter details and response schemas, see the [Usage API reference](https://platform.claude.com/docs/en/api/admin-api/usage-cost/get-messages-usage-report).

### Basic examples

#### Daily usage by model

```bash cURL
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-08T00:00:00Z&\
group_by[]=model&\
bucket_width=1d" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

bash cURL
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-15T00:00:00Z&\
ending_at=2025-01-15T23:59:59Z&\
models[]=claude-opus-5&\
service_tiers[]=batch&\
context_window[]=0-200k&\
bucket_width=1h" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

bash cURL
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-08T00:00:00Z&\
api_key_ids[]=apikey_01Rj2N8SVvo6BePZj99NhmiT&\
api_key_ids[]=apikey_01ABC123DEF456GHI789JKL&\
workspace_ids[]=wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ&\
workspace_ids[]=wrkspc_01XYZ789ABC123DEF456MNO&\
bucket_width=1d" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

bash cURL
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2026-02-01T00:00:00Z&\
ending_at=2026-02-08T00:00:00Z&\
group_by[]=inference_geo&\
group_by[]=model&\
bucket_width=1d" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

bash cURL
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2026-02-01T00:00:00Z&\
ending_at=2026-02-08T00:00:00Z&\
inference_geos[]=us&\
group_by[]=model&\
bucket_width=1d" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

bash cURL
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2026-02-01T00:00:00Z&\
ending_at=2026-02-08T00:00:00Z&\
group_by[]=speed&\
group_by[]=model&\
bucket_width=1d" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: fast-mode-2026-02-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

bash cURL
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2026-02-01T00:00:00Z&\
ending_at=2026-02-08T00:00:00Z&\
speeds[]=fast&\
group_by[]=model&\
bucket_width=1d" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: fast-mode-2026-02-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

<Note>
  Both the `speeds[]` filter and the `speed` group\_by value require the `fast-mode-2026-02-01` beta header.
</Note>

### Time granularity limits

| Granularity | Default limit | Maximum limit | Use case               |
| ----------- | ------------- | ------------- | ---------------------- |
| `1m`        | 60 buckets    | 1,440 buckets | Real-time monitoring   |
| `1h`        | 24 buckets    | 168 buckets   | Daily patterns         |
| `1d`        | 7 buckets     | 31 buckets    | Weekly/monthly reports |


## Cost API

Source: https://platform.claude.com/llms-full.txt#cost-api

Retrieve service-level cost breakdowns in USD with the `/v1/organizations/cost_report` endpoint.

### Key concepts

* **Currency:** All costs in USD, reported as decimal strings in lowest units (cents)
* **Cost types:** Track token usage, web search, and code execution costs
* **Grouping:** Group costs by workspace or description for detailed breakdowns. When grouping by `description`, responses include parsed fields such as `model` and `inference_geo`
* **Time buckets:** Daily granularity only (`1d`)

For complete parameter details and response schemas, see the [Cost API reference](https://platform.claude.com/docs/en/api/admin-api/usage-cost/get-cost-report).

<Warning>
  Priority Tier costs use a different billing model and are not included in the cost endpoint. Track Priority Tier usage through the usage endpoint instead.
</Warning>

### Basic example

```bash cURL
curl "https://api.anthropic.com/v1/organizations/cost_report?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-31T00:00:00Z&\
group_by[]=workspace_id&\
group_by[]=description" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"
```


## Pagination

Source: https://platform.claude.com/llms-full.txt#pagination-5

Both endpoints support pagination for large datasets:

1. Make your initial request.
2. If `has_more` is `true`, use the `next_page` value in your next request.
3. Continue until `has_more` is `false`.

```bash cURL
# First request
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-31T00:00:00Z&\
limit=7" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Response includes: "has_more": true, "next_page": "page_xyz..."

# Next request with pagination
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-31T00:00:00Z&\
limit=7&\
page=page_xyz..." \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"
```


## Common use cases

Source: https://platform.claude.com/llms-full.txt#common-use-cases-4

Explore detailed implementations in [Claude Cookbook](https://platform.claude.com/cookbook):

* **Daily usage reports:** Track token consumption trends
* **Cost attribution:** Allocate expenses by workspace for chargebacks
* **Cache efficiency:** Measure and optimize prompt caching
* **Budget monitoring:** Set up alerts for spending thresholds
* **CSV export:** Generate reports for finance teams


## Frequently asked questions

Source: https://platform.claude.com/llms-full.txt#frequently-asked-questions-5

### How fresh is the data?

Usage and cost data typically appears within 5 minutes of API request completion, though delays may occasionally be longer.

### What's the recommended polling frequency?

The API supports polling once per minute for sustained use. For short bursts (for example, downloading paginated data), more frequent polling is acceptable. Cache results for dashboards that need frequent updates.

### How do I track code execution usage?

Code execution costs appear in the cost endpoint grouped under `Code Execution Usage` in the description field. Code execution is not included in the usage endpoint.

### How do I track Priority Tier usage?

Filter or group by `service_tier` in the usage endpoint and look for the `priority` value. Priority Tier costs are not available in the cost endpoint.

### What happens with playground usage?

API usage from playground in the Claude Console (and from the legacy Workbench before it) is not associated with an API key, so `api_key_id` will be `null` even when grouping by that dimension.

### How is the default workspace represented?

Usage and costs attributed to the default workspace have a `null` value for `workspace_id`.

### How do I get per-user cost breakdowns for Claude Code?

Use the [Claude Code Analytics API](https://platform.claude.com/docs/en/manage-claude/claude-code-analytics-api), which provides per-user estimated costs and productivity metrics without the performance limitations of breaking down costs by many API keys. For general API usage with many keys, use the [Usage API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api#usage-api) to track token consumption as a cost proxy.


## See also

Source: https://platform.claude.com/llms-full.txt#see-also-10

Use the Usage and Cost APIs to deliver a better experience for your users, manage costs, and preserve your rate limit. Learn more about some of these other features:

* [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api)
* [Admin API reference](https://platform.claude.com/docs/en/api/admin)
* [Analytics APIs](https://platform.claude.com/docs/en/manage-claude/analytics-api) - Which analytics API and key type your organization needs
* [Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
* [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) - Optimize costs with caching
* [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing) - 50% discount on batch requests
* [Rate limits](https://platform.claude.com/docs/en/api/rate-limits) - Understand usage tiers
* [Rate Limits API](https://platform.claude.com/docs/en/manage-claude/rate-limits-api) - Read your configured rate limits
* [Data residency](https://platform.claude.com/docs/en/manage-claude/data-residency) - Control inference geography


### Data & compliance

---
title: Access Transparency
url: https://platform.claude.com/docs/en/manage-claude/access-transparency
description: Receive an audit record of human access to your organization's data by Anthropic personnel through the Compliance API.
---

Learn how Access Transparency creates a record of human access to your organization's data by Anthropic personnel, what it covers, and how to receive events through the Compliance API.

<Note>
  When Access Transparency is enabled for your organization:

  * Each human view of your retained data (see [covered content](https://platform.claude.com/docs/en/manage-claude/access-transparency#what-access-transparency-covers)) by an Anthropic employee writes an `anthropic_access` activity to your [Compliance API Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed).
  * Access occurs only for safety review or incident response. See [Reason codes](https://platform.claude.com/docs/en/manage-claude/access-transparency#reason-codes).

  Access Transparency is available to eligible customers on request and is not self-serve. For eligibility, refer to your contract terms or contact your Anthropic account representative.
</Note>


## How Access Transparency works

Source: https://platform.claude.com/llms-full.txt#how-access-transparency-works

Anthropic personnel access customer content only under defined conditions. Access Transparency is designed to make such access visible to you. The design rests on the following principles:

* **Human access happens only under a published reason code.**
* **Human views of your covered content are recorded.** Anthropic's internal tooling that can reach your covered content is instrumented to emit an event on each view.
* **Events represent human access, not automated processing.** Anthropic's automated safety systems process your content in a secured pipeline with no interactive human access; that processing does not generate `anthropic_access` events. The one event automated processing can initiate is a `cmek_preserve` preservation record (see [CMEK content preservation](https://platform.claude.com/docs/en/manage-claude/access-transparency#cmek-content-preservation)).
* **Events arrive on your existing feed.** Activities are accessible through your [Compliance API Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed). Existing credentials, audit, export, and SIEM integrations for the Compliance API will still apply.


## What Access Transparency covers

Source: https://platform.claude.com/llms-full.txt#what-access-transparency-covers

* **Covered content:** Access Transparency covers prompt and response content sent through the Claude Messages API or Claude Code sessions. Anthropic's [general ZDR documentation](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) and [ZDR for Claude Code documentation](https://code.claude.com/docs/en/zero-data-retention) explain which APIs and features are covered by ZDR. The same APIs and features are covered by Access Transparency.
* **Manual views by Anthropic personnel:** Manual views of your covered content by Anthropic reviewers generate events.


## What Access Transparency does not cover

Source: https://platform.claude.com/llms-full.txt#what-access-transparency-does-not-cover

* **Automated processing:** Model serving, safety classifiers, and abuse-detection pipelines process your content as part of normal operation and do not generate `anthropic_access` events. Preservation initiated by automated processing does generate a `cmek_preserve` event (see [CMEK content preservation](https://platform.claude.com/docs/en/manage-claude/access-transparency#cmek-content-preservation)).
* **Your own organization's activity:** Your API calls, admin actions, and Compliance API reads are covered by standard [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) event types.
* **Claude for Enterprise and Claude Apps:** claude.ai Enterprise seats, Claude for Work, Cowork, and Claude in Chrome are not covered.
* **Claude consumer products:** Claude Free, Pro, or Max plans.
* **Partner-operated platforms:** Amazon Bedrock and Google Cloud; refer to those platforms' transparency controls.
* **Anything ZDR does not cover:** Products that are not covered by ZDR (for example, the Files API, Anthropic-hosted stateful applications, and the Batch API) are not covered by Access Transparency. See [ZDR documentation](https://code.claude.com/docs/en/zero-data-retention#what-zdr-does-not-cover) for additional details.


## Getting started

Source: https://platform.claude.com/llms-full.txt#getting-started-2

To enable Access Transparency:

<Steps>
  <Step title="Request Access Transparency">
    Contact your Anthropic account representative.
  </Step>

  <Step title="Anthropic reviews eligibility">
    Anthropic confirms your organization meets the eligibility criteria and enables the capability at the organization level.
  </Step>

  <Step title="Receive events through the Compliance API">
    `anthropic_access` activities appear in your existing Activity Feed under your existing Compliance Access Key; no new endpoint or credentials are required.
  </Step>
</Steps>

Access Transparency is enabled at the organization level and covers all workspaces. Per-workspace enrollment is not currently available.


## Receiving Access Transparency events

Source: https://platform.claude.com/llms-full.txt#receiving-access-transparency-events

Access Transparency events are delivered as the `anthropic_access` activity type on the Compliance API Activity Feed. Filter with `activity_types[]`:

Pagination, date-range filtering (`created_at.gte` / `.lt`), and the response envelope (`has_more`, `first_id`, `last_id`) are shared with the rest of the Activity Feed. See [Query the Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed).

Each `anthropic_access` activity carries the standard Activity fields plus the following:

| Field                     | Type            | Description                                                                                                                                                      |
| ------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                      | string          | Unique identifier for this activity                                                                                                                              |
| `accessed_at`             | RFC 3339 string | When the access occurred. Might be earlier than when the activity becomes visible in your feed                                                                   |
| `created_at`              | RFC 3339 string | When the activity became visible in your feed                                                                                                                    |
| `actor`                   | object          | Always `{ "type": "anthropic_actor", "email_address": null }`. Individual employee identity is not disclosed                                                     |
| `accessor_department`     | string          | The Anthropic team that performed the access (for example, `Safeguards`)                                                                                         |
| `reason_code`             | enum            | See [Reason codes](https://platform.claude.com/docs/en/manage-claude/access-transparency#reason-codes)                                                           |
| `resource_details.type`   | enum            | A resource type, currently only `message`. Extensible for future resource types                                                                                  |
| `resource_details.id`     | string or null  | Identifier of the content accessed                                                                                                                               |
| `resource_details.parent` | string or null  | Identifier of the content's parent, for example the conversation ID containing a message. Currently `null` or omitted until resources with parents are supported |
| `organization_id`         | string          | The organization the content belongs to. Tagged ID format (`org_...`)                                                                                            |
| `organization_uuid`       | string          | The organization the content belongs to. UUID format                                                                                                             |
| `workspace_id`            | string or null  | The workspace the content belongs to                                                                                                                             |

Example JSON message:


## CMEK content preservation

Source: https://platform.claude.com/llms-full.txt#cmek-content-preservation

In rare cases, Anthropic preserves specific content beyond the standard retention window (for example, when a safety review confirms severely harmful content that must be retained for an ongoing investigation). Preservation is itself a logged, customer-visible action:

* **A preservation event is written to your feed.** When content is preserved, an event with type `cmek_preserve` is written to your Compliance API Activity Feed. Preservation events carry the same fields as an `anthropic_access` event; only the event type differs, so a parser that handles one handles both. See [Reason codes](https://platform.claude.com/docs/en/manage-claude/access-transparency#reason-codes).
* **A preservation event is written regardless of how the preservation was initiated.** Preservation ordinarily follows human review of the content, but the event is written whether the preservation was initiated by a human reviewer or by an automated safety pipeline: the record reflects that your content's retention state changed, independent of who changed it.
* **For CMEK organizations, preservation is a visible key movement.** Preserved content is re-encrypted outside your customer-managed key so that the investigation can continue independent of your key. The preservation event is your record that this occurred. All other retained content remains under your key.

Filter for preservation events the same way as access events:

Example JSON message:

For preservation events, `accessed_at` records when the content was preserved.


## Reason codes

Source: https://platform.claude.com/llms-full.txt#reason-codes

The set of reason codes is closed. Anthropic will update this page in the event it introduces a new code.

| Code                             | Meaning                                                                        |
| -------------------------------- | ------------------------------------------------------------------------------ |
| `safety_review`                  | Content was viewed as part of a usage-policy or safety investigation           |
| `incident_response`              | Content was viewed while investigating an incident affecting your organization |
| `policy_violation_investigation` | Content was preserved during a Trust and Safety policy-violation investigation |
| `csae_report`                    | Content was preserved as evidence for a child safety (CSAE) report             |


## Surface eligibility

Source: https://platform.claude.com/llms-full.txt#surface-eligibility

The following table lists which surfaces are covered by Access Transparency. Coverage means human access to content from that surface generates `anthropic_access` events.

| Surface                                         | Covered | Details                                                                                                    |
| ----------------------------------------------- | ------- | ---------------------------------------------------------------------------------------------------------- |
| Claude API (`api.anthropic.com`)                | Yes     | Prompts, completions, and data directly embedded in the API inputs                                         |
| Claude Code (using an API key)                  | Yes     | API traffic from Claude Code is covered as Claude API traffic                                              |
| Claude Platform on AWS                          | Yes     | Claude Platform on AWS generates Access Transparency events within the Compliance API (not AWS CloudTrail) |
| Claude API (`api.anthropic.com`) (Batch, Files) | No      | The Claude API Batch and Files APIs are not covered, just like they are not covered by ZDR                 |
| Claude for Enterprise (claude.ai seats)         | No      | Not covered                                                                                                |
| Claude for Work                                 | No      | Not covered                                                                                                |
| Claude Free, Pro, Max                           | No      | Consumer plans are not eligible                                                                            |
| Playground (Claude Console)                     | No      | Not covered                                                                                                |
| Microsoft Foundry                               | No      | Not available                                                                                              |
| Amazon Bedrock, Google Cloud                    | No      | Partner-operated platforms; refer to those platforms' transparency controls                                |


## Limitations and exclusions

Source: https://platform.claude.com/llms-full.txt#limitations-and-exclusions

### Coverage timing

Access Transparency applies from the time it is enabled for your organization. Content already in your retention window at enablement might also generate events when accessed, but Anthropic does not guarantee coverage for content written before enablement. Treat your enablement date as the start of reliable coverage. There might be a delay of up to two hours between enabling Access Transparency and your content being covered.

### Notification timing

`anthropic_access` and `cmek_preserve` events are delivered to your Compliance API feed within two business days of the access or preservation they record. This feed should not be treated as a real-time alerting channel, and the `accessed_at` timestamp reflects when the access occurred, which might be up to two business days before the activity becomes visible in your feed. The `created_at` field reflects the time that the event became visible.

### Automated processing does not generate access events

`anthropic_access` events record human access only. Anthropic's automated safety systems and classifiers continue to process your content as part of normal operation, and that processing does not generate `anthropic_access` events. The one event automated processing can initiate is a `cmek_preserve` preservation record (see [CMEK content preservation](https://platform.claude.com/docs/en/manage-claude/access-transparency#cmek-content-preservation)). An empty feed means no human at Anthropic has viewed your content; it does not mean your content was not processed by automated systems.

### Access Transparency does not change what Anthropic can access

Access Transparency records access; it does not grant or restrict it. The purposes for which Anthropic personnel may access your content are governed by your agreement with Anthropic and the [Usage Policies](https://www.anthropic.com/legal/aup), and are the same regardless of whether Access Transparency is enabled.

### CMEK key-use logs are not a per-read record

For organizations that also enable CMEK, your cloud KMS audit log (CloudTrail, Cloud Audit Logs, or Azure Monitor) records Anthropic's use of your key. Because keys are cached for short periods during operation, an individual human read does not necessarily produce a distinct KMS decryption entry. Use the Access Transparency feed as the per-access record; your KMS log independently confirms key usage patterns.


## Frequently asked questions

Source: https://platform.claude.com/llms-full.txt#frequently-asked-questions-6

<AccordionGroup>
  <Accordion title="How do I know if my organization has Access Transparency enabled?">
    Contact your Anthropic account representative.
  </Accordion>

  <Accordion title="Will I see an event each time a safety classifier runs on my traffic?">
    No. Automated processing does not generate `anthropic_access` events; you will see an `anthropic_access` event only if a human reviewer subsequently views the content. Separately, a `cmek_preserve` event is written when content is preserved, whether the preservation was initiated by a human reviewer or an automated safety pipeline.
  </Accordion>

  <Accordion title="We are a platform that serves Claude to our own end users. Can we enable Access Transparency?">
    Access Transparency is not available for platform deployments. Contact your Anthropic account representative to discuss your use case.
  </Accordion>

  <Accordion title="Will I see events for access that happened before we enrolled, or for our older data?">
    Access Transparency is not guaranteed to be retroactive. It covers human access to content written to the Claude API on or after your enrollment date. You might see events for access to content that was written before enrollment.
  </Accordion>

  <Accordion title="How soon after an access will I see the event?">
    Within two business days of the access. Configure any SIEM alerting or scheduled exports with a matching lookback window rather than assuming real-time arrival.
  </Accordion>

  <Accordion title="How do I know which request an anthropic_access event refers to?">
    Use the `resource_details.id` field. It contains the same message ID (`msg_...`) that the [Messages API](https://platform.claude.com/docs/en/api/messages/create) returns in the `id` field of every response body. To make this useful, log `id` in your own systems alongside your internal metadata, such as the application, end user, or conversation that produced the request. When an event arrives, join its `resource_details.id` against your logs to identify exactly which request was viewed.
  </Accordion>

  <Accordion title="Can I enable Access Transparency for a single workspace?">
    Access Transparency is enabled at the organization level and covers all workspaces.
  </Accordion>

  <Accordion title="How does Access Transparency relate to CMEK?">
    They are independent. With CMEK, safety preservation outside your key emits a separate `cmek_preserve` event on the same feed. See [CMEK content preservation](https://platform.claude.com/docs/en/manage-claude/access-transparency#cmek-content-preservation) and [CMEK](https://platform.claude.com/docs/en/manage-claude/cmek).
  </Accordion>

  <Accordion title="How do I request Access Transparency?">
    Contact your Anthropic account representative.
  </Accordion>
</AccordionGroup>
