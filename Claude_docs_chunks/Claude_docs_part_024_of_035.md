# platform.claude.com Documentation (Part 24 of 35)

## Sessions in the cloud (remote sessions)

Source: https://platform.claude.com/llms-full.txt#sessions-in-the-cloud-remote-sessions

Cowork sessions started on claude.ai web or mobile run in the cloud in Anthropic-managed environments. The Compliance API exposes these remote sessions through two endpoints: `GET /v1/compliance/apps/sessions/remote` lists session metadata, and `GET /v1/compliance/apps/sessions/remote/{session_id}/messages` returns one session's transcript. Both require the `read:compliance_user_data` scope, and both count against the shared Compliance API rate limit plus a second request budget specific to these endpoints; see [429 Too Many Requests](https://platform.claude.com/docs/en/manage-claude/compliance-errors#429-too-many-requests).

The list endpoint defaults to organization-wide scope: leave off `organization_ids[]` to include every claude.ai organization your key can read, or pass up to 500 values to narrow the scope. To scope the list to specific users instead, pass 1–10 `user_ids[]` values (obtain the IDs from [List organization users](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#list-organization-users)); the filter matches the session's owning user, so agent-owned sessions are excluded whenever `user_ids[]` is set. Bound the results in time with `created_at` range parameters (`gte`, `gt`, `lt`, `lte`, in RFC 3339 format). There is no `updated_at` filter. The following request lists sessions created since a given date.

```bash cURL
curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/apps/sessions/remote" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --data-urlencode "created_at.gte=2026-06-01T00:00:00Z" \
  --data-urlencode "limit=100"

json Response
{
  "data": [
    {
      "id": "cse_01WpQrStUvXyZaBcDeFgHjK6",
      "organization_uuid": "91012d09-e48b-438e-a489-1bebfd8fa6f9",
      "user": {
        "id": "user_01XyDMpzjS89pFZXqSFUBDr6",
        "email_address": "user@example.com"
      },
      "agent_id": null,
      "started_by_user": null,
      "status": "active",
      "created_at": "2026-07-01T17:04:05Z",
      "updated_at": "2026-07-01T18:00:41Z",
      "product_surface": "cowork_remote",
      "claude_project_id": "claude_proj_01KGp4eZNug9ri4kE35RSppq"
    },
    {
      "id": "cse_01TkNpRsUvWxYzAbCdEfGhJ4",
      "organization_uuid": "91012d09-e48b-438e-a489-1bebfd8fa6f9",
      "user": null,
      "agent_id": "cagt_01MnPqRsTuVwXyZaBcDeFgH8",
      "started_by_user": {
        "id": "user_01XyDMpzjS89pFZXqSFUBDr6",
        "email_address": "user@example.com"
      },
      "status": "archived",
      "created_at": "2026-06-28T09:15:22Z",
      "updated_at": "2026-06-28T09:47:10Z",
      "product_surface": "cowork_remote",
      "claude_project_id": null
    }
  ],
  "next_page": "page_AAEfMk93cXpYdGxrZXk"
}

bash cURL
session_id="cse_01WpQrStUvXyZaBcDeFgHjK6"

curl --fail-with-body -sS \
  "https://api.anthropic.com/v1/compliance/apps/sessions/remote/$session_id/messages" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01"

json Response
{
  "session": {
    "id": "cse_01WpQrStUvXyZaBcDeFgHjK6",
    "organization_uuid": "91012d09-e48b-438e-a489-1bebfd8fa6f9",
    "user": {
      "id": "user_01XyDMpzjS89pFZXqSFUBDr6",
      "email_address": null
    },
    "agent_id": null,
    "started_by_user": null,
    "status": "active",
    "created_at": "2026-07-01T17:04:05Z",
    "updated_at": "2026-07-01T18:00:41Z",
    "product_surface": "cowork_remote",
    "claude_project_id": null
  },
  "data": [
    {
      "id": "csev_01HjKmNpQrStUvWxYzAbCdE2",
      "role": "user",
      "created_at": "2026-07-01T17:04:05Z",
      "content": [
        {
          "type": "text",
          "text": "Summarize the customer feedback in the attached spreadsheet.",
          "truncated": false
        }
      ],
      "sent_by_user_id": null,
      "content_unavailable": false
    },
    {
      "id": "csev_01BcDeFgHjKmNpQrStUvWxY4",
      "role": "assistant",
      "created_at": "2026-07-01T17:04:06Z",
      "content": [
        {
          "type": "text",
          "text": "I'll start by reading the spreadsheet...",
          "truncated": false
        }
      ],
      "sent_by_user_id": null,
      "content_unavailable": false
    }
  ],
  "next_page": null
}
```

The response embeds a `session` envelope alongside the paginated `data` array. On this endpoint the envelope always has `user.email_address`, `started_by_user`, and `claude_project_id` set to `null`; get those values from the list endpoint instead.

Messages are returned oldest first by default; pass `order=desc` to reverse. Pagination uses the same `page`/`next_page` scheme as the list endpoint, with a `limit` default of 100 and a max of 1,000. A page can end early when the response reaches its size limit, so a page with fewer than `limit` messages does not mean you have reached the end; keep paginating until `next_page` is `null`.

Each message carries a `role` (`user` or `assistant`) and a `content` array of `text`, `tool_use`, and `tool_result` blocks. Message `created_at` values are commit timestamps: consecutive messages can share a timestamp or slightly invert, so preserve the returned order rather than re-sorting by `created_at`. On agent-owned sessions, `sent_by_user_id` records the user who sent a given user message when one is attributable; it is `null` otherwise, including on all assistant messages. When a message's content cannot be returned at all (for example, it exceeds size bounds), the message carries `content_unavailable` set to `true`.

Two parameters cap how many bytes of each tool block are returned: `tool_use_input_max_bytes` and `tool_result_max_bytes`, both defaulting to 10,000 bytes. Pass `-1` for the server maximum (about 1 MiB per string); `0` returns [400 Bad Request](https://platform.claude.com/docs/en/manage-claude/compliance-errors#400-bad-request). A block cut off by either cap carries `"truncated": true`, and a truncated `tool_use` input is no longer valid JSON, so parse tool inputs only from untruncated blocks (or raise the cap and refetch).

The messages endpoint returns [404 Not Found](https://platform.claude.com/docs/en/manage-claude/compliance-errors#404-not-found) for `pending` sessions, sessions that do not exist or have been deleted, and sessions in organizations your key cannot read.


## Retention and deletion

Source: https://platform.claude.com/llms-full.txt#retention-and-deletion

The session endpoints are read-only; local and remote sessions cannot be deleted through the Compliance API. Local session transcripts are retained for 6 years by default, or your organization's custom conversation retention period when a finite one is set, as described under [Sessions on users' machines](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions). Remote session transcripts are retained for 6 years, unless a user deletes the session sooner. The remote session endpoints no longer return a session once a user deletes it, and its transcript is not recoverable through the Compliance API. To learn how these periods sit alongside Anthropic's other retention arrangements, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-97

<CardGroup cols={2}>
  <Card title="Retrieve and delete chats, files, and projects" href="https://platform.claude.com/docs/en/manage-claude/compliance-content-data">
    Access claude.ai chat content, file attachments, and projects with the same Compliance Access Key.
  </Card>

  <Card title="Compliance API FAQ" href="https://platform.claude.com/docs/en/manage-claude/compliance-faq#data-coverage-and-retention">
    A field-by-field summary of what session transcripts include, and other common questions.
  </Card>

  <Card title="Handle Compliance API errors" href="https://platform.claude.com/docs/en/manage-claude/compliance-errors">
    Verbatim error payloads and the fix for each.
  </Card>

  <Card title="API reference" href="https://platform.claude.com/docs/en/api/compliance/apps">
    Endpoint paths, parameters, and response schemas for the Compliance API.
  </Card>
</CardGroup>


---
title: Set up the Compliance API
url: https://platform.claude.com/docs/en/manage-claude/compliance-api-access
description: Enable the Compliance API for your organization, then create a Compliance Access Key (with scoped permissions) or an Admin API key, and learn which to use.
---

<Note>
  Claude Enterprise organizations and eligible standalone Claude Console organizations have self-service access to the Compliance API. This page describes how to enable the Compliance API for your organization and create API keys.
</Note>

<Check>
  **Required role:** organization admin (Claude Console), or primary owner or organization owner (claude.ai).
</Check>

The Compliance API uses two key types, and which one you create depends on which Claude product your organization uses. Primary owners and organization owners create Compliance Access Keys in claude.ai; these keys unlock the full Compliance API. A primary owner's key can cover every organization under the parent organization; an organization owner's key covers their own organization only. Organization admins create Admin API keys in Claude Console; these keys unlock the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) only.


## Which key do you need?

Source: https://platform.claude.com/llms-full.txt#which-key-do-you-need-2

| Key type                                       | Created in                                                                                | Used for                                                                                                                                          | Works with the Compliance API? |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| **Compliance Access Key** (`sk-ant-api01-...`) | [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access)    | Activity Feed, chats, files, projects, sessions (in apps such as Cowork and Claude Code), users, organization metadata, and organization settings | Yes (all endpoints)            |
| **Admin API key** (`sk-ant-admin01-...`)       | [Claude Console > Settings > Admin keys](https://platform.claude.com/settings/admin-keys) | The [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api) and the Compliance API Activity Feed                                 | Activity Feed only             |
| **Analytics API key**                          | [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access)    | The Claude Enterprise Analytics API (see [Analytics APIs](https://platform.claude.com/docs/en/manage-claude/analytics-api))                       | No                             |
| **Claude API key** (`sk-ant-api03-...`)        | [Claude Console > Settings > API keys](https://platform.claude.com/settings/keys)         | Calling Claude models through the [Claude API](https://platform.claude.com/docs/en/api/overview)                                                  | No                             |

A Claude Enterprise tenant has one **parent organization** that centralizes identity, SSO, and SCIM for every workload organization beneath it. These workload organizations are the parent's **linked organizations**.

<Warning>
  **Claude Enterprise parent organizations do not appear in Claude Console (`platform.claude.com`).** The parent carries no workloads, no Claude API keys, and no Admin API keys. Create Compliance Access Keys in claude.ai **Organization settings**, not in Claude Console.
</Warning>


## Set up the Compliance API

Source: https://platform.claude.com/llms-full.txt#set-up-the-compliance-api

Setup is one flow: enable the Compliance API for your organization, then create a Compliance Access Key in claude.ai. A Claude Console organization instead [creates an Admin API key](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#create-an-admin-api-key) after enablement; Admin API keys reach the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) only.

<Warning>
  A Compliance Access Key with `read:compliance_user_data` can read every chat, file, project, and session transcript in every linked organization, including content the primary owner has not seen. A key with `delete:compliance_user_data` can permanently delete chats, files, and projects. Treat Compliance Access Keys like production database credentials: store them in a secrets manager, never in source control or SIEM forwarder configuration.
</Warning>

<Steps>
  <Step title="Enable the Compliance API">
    Where you enable the Compliance API depends on how your organization is set up:

    * **Claude Enterprise organizations:** The primary owner enables the Compliance API at [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access). Enablement happens at the parent organization level and cascades to every linked organization, both claude.ai and Claude Console.
    * **Standalone Claude Console organizations:** An organization admin turns on the **Compliance API** toggle at [Claude Console > Settings > Security](https://platform.claude.com/settings/security). Enablement is self-service for eligible organizations, and the change takes effect immediately. If the **Compliance API** section is not visible, you do not have the admin role, your organization is linked to a parent organization (the Compliance API is enabled from the parent organization instead), or your organization is not eligible for self-service enablement; contact your account team or [Anthropic support](https://support.claude.com) if you are not sure which applies.
    * **Claude Console organizations linked to a parent organization:** There is nothing to turn on in Claude Console. Ask the primary owner of your parent organization to enable the Compliance API in claude.ai, or contact your account team.

    <Warning>
      **Turning the Compliance API off stops activity recording.** An organization admin can turn the Compliance API off at any time with the same **Compliance API** toggle that turns it on. While the Compliance API is off, no activity events are recorded for your organization, so the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) receives no new events. If your organization is enrolled in [Access Transparency](https://platform.claude.com/docs/en/manage-claude/access-transparency), turning the Compliance API off also stops Access Transparency event delivery. Activity that is not recorded while the Compliance API is off cannot be recovered later. Turning the Compliance API back on resumes recording from that point forward; activity that was already recorded is not deleted. For Claude Enterprise organizations, the Compliance API setting in claude.ai also governs transcript capture for [local sessions](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions) (sessions on users' machines): capture starts when the Compliance API is enabled and stops while it is off, and transcript content from sessions that run while it is off is not captured and cannot be recovered later.
    </Warning>

    A standalone Claude Console organization uses Admin API keys rather than Compliance Access Keys: after enablement, skip the remaining steps and [create a new Admin API key](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#create-an-admin-api-key) instead. The remaining steps provision Compliance Access Keys, which are available only to organizations that are part of a Claude Enterprise tenant.
  </Step>

  <Step title="Decide the key's scope">
    A key's access is set when it is created. Decide which organizations the key covers:

    * A key for the **parent organization** can access every organization under the parent organization.
    * A key for a **single organization** can access that organization only.
  </Step>

  <Step title="Sign in with the matching role">
    Sign in to claude.ai. The primary owner of the parent organization can create a key with either scope. An organization owner can create a key restricted to their own organization only.

    If the **API** page described in the next step is not visible, or compliance scopes are unavailable when creating a key, either your role cannot create Compliance Access Keys, or the Compliance API has not been enabled for your organization yet (return to the first step).
  </Step>

  <Step title="Open API settings">
    Go to [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access) and find the **Keys** section.
  </Step>

  <Step title="Create the key">
    Click **Create key**, name the key, and select one or more scopes from the following table. Click **Create**.

    | Scope                         | Grants                                                                                                                                                                                                                    |
    | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `read:compliance_activities`  | Read the Activity Feed. A key covering the parent organization reads events for the parent organization and all linked organizations.                                                                                     |
    | `read:compliance_user_data`   | Read user chats, messages, files, projects, session metadata and transcripts, organization users, and group members                                                                                                       |
    | `delete:compliance_user_data` | Delete user chats, files, and projects                                                                                                                                                                                    |
    | `read:compliance_org_data`    | Read organization metadata (names, types, roles, and groups) and the effective settings in force for organizations under the parent organization. User listings and group membership require `read:compliance_user_data`. |

    Choose the smallest scope set that your integration needs:

    * An audit pipeline that reads the Activity Feed only needs `read:compliance_activities`.
    * An eDiscovery tool that reads chats and files but never deletes them does not need `delete:compliance_user_data`.
    * If your workflow both reads and deletes, use **two keys** with separate scopes so a leaked read key cannot delete data.

    Compliance Access Key scopes are immutable after creation. To change scopes, create a new key with the scopes you want, then delete the old one.
  </Step>

  <Step title="Copy and store the secret">
    Copy the displayed secret key (starting with `sk-ant-api01-`) and store it in your secrets manager. The full secret is displayed only once.
  </Step>

  <Step title="Export the key for the examples in this guide">
    Set the key as an environment variable so the shell samples in this guide can read it:

</Step>
</Steps>


## Create an Admin API key

Source: https://platform.claude.com/llms-full.txt#create-an-admin-api-key

<Note>
  The Compliance API must already be [enabled for your Claude Console organization](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#set-up-the-compliance-api) before an Admin API key can call the Activity Feed.
</Note>

Follow the steps in [Create an Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys#create-a-key-for-a-claude-console-organization), then set the key as an environment variable:

The distinct variable name keeps the Admin API key from overwriting a Compliance Access Key if you provision both. The cURL examples in this guide read the key from `$ANTHROPIC_COMPLIANCE_ACCESS_KEY`; substitute `$ANTHROPIC_ADMIN_KEY` when calling the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) with an Admin API key.

Admin API keys carry the `read:compliance_activities` scope only if the Compliance API was enabled for the organization at the time the key was created; see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#set-up-the-compliance-api). They cannot be granted any other Compliance API scope, so calls to any endpoint other than the Activity Feed return [403 Forbidden](https://platform.claude.com/docs/en/manage-claude/compliance-errors#403-forbidden).

For the same key's role in managing your Claude Console organization, see [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api).


## Check your key's scopes

Source: https://platform.claude.com/llms-full.txt#check-your-key-s-scopes

To inspect the scopes on a key you already have, use one of the following signals.

* **Key prefix.** `sk-ant-admin01-` is an Admin API key (carries `read:compliance_activities` only, subject to the enablement timing in the preceding section). `sk-ant-api01-` is a Compliance Access Key; its scopes are the subset you selected at creation.
* **Settings UI.** Open the **Keys** section in [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access), or the **Admin keys** section in [Claude Console > Settings > Admin keys](https://platform.claude.com/settings/admin-keys), and read the **Scopes** column for the key.
* **Error responses.** A call that exceeds the key's scopes returns a 403 with a message in the format `Missing required scopes. Got: [<scopes the key carries>] Needed: [<scopes the endpoint requires>]`. See [Handle Compliance API errors](https://platform.claude.com/docs/en/manage-claude/compliance-errors#403-forbidden) for the full error catalog.


## Manage and rotate keys

Source: https://platform.claude.com/llms-full.txt#manage-and-rotate-keys

Delete a Compliance Access Key from the same **Keys** table where you created it: go to [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access). Delete an Admin API key from [Claude Console > Settings > Admin keys](https://platform.claude.com/settings/admin-keys).

Deleting a key takes effect on the next request: there is no grace period. Compliance Access Keys do not expire on their own.

To rotate a key without an outage:

1. Create a new key with the same scopes.
2. Update your integration to use the new key.
3. Verify the integration succeeds with the new key.
4. Delete the old key.

Pagination cursors stored before a rotation remain valid: cursors are scoped to the organization, not the key.

If a Compliance Access Key leaks, delete it immediately, audit the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) for `compliance_api_accessed` activities by the compromised key, and rotate any downstream credentials that the leaked key could reach. Pass `activity_types[]=compliance_api_accessed` to scope the query, then in your client, keep the activities whose `actor.type` is `api_actor` and whose `actor.api_key_id` matches the compromised key; see [Understand the Activity object](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed#understand-the-activity-object) for the actor schema.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-98

<CardGroup cols={2}>
  <Card title="Query the Activity Feed" href="https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed">
    Read organization-wide activity events with any key that has `read:compliance_activities`.
  </Card>

  <Card title="Retrieve and delete chats, files, and projects" href="https://platform.claude.com/docs/en/manage-claude/compliance-content-data">
    Use a Compliance Access Key with `read:compliance_user_data` to retrieve claude.ai chats, files, and projects, and `delete:compliance_user_data` to delete them.
  </Card>

  <Card title="Retrieve session transcripts" href="https://platform.claude.com/docs/en/manage-claude/compliance-sessions">
    Use a Compliance Access Key with `read:compliance_user_data` to list the sessions your users run in Claude apps and agents, such as Cowork and Claude Code, and retrieve their transcripts.
  </Card>
</CardGroup>


## Best practices

Source: https://platform.claude.com/llms-full.txt#best-practices-11

### Use cases

---
title: Guides to common use cases
url: https://platform.claude.com/docs/en/about-claude/use-case-guides/overview
description: "Explore production guides for building common Claude use cases: ticket routing, customer support agents, content moderation, and legal summarization."
---

Claude is designed to excel in a variety of tasks. Explore these in-depth production guides to learn how to build common use cases with Claude.

<CardGroup cols={2}>
  <Card title="Ticket routing" icon="headset" href="https://platform.claude.com/docs/en/about-claude/use-case-guides/ticket-routing">
    Best practices for using Claude to classify and route customer support tickets at scale.
  </Card>

  <Card title="Customer support agent" icon="robot" href="https://platform.claude.com/docs/en/about-claude/use-case-guides/customer-support-chat">
    Build intelligent, context-aware chatbots with Claude to enhance customer support interactions.
  </Card>

  <Card title="Content moderation" icon="verified" href="https://platform.claude.com/docs/en/about-claude/use-case-guides/content-moderation">
    Techniques and best practices for using Claude to perform content filtering and general content moderation.
  </Card>

  <Card title="Legal summarization" icon="book" href="https://platform.claude.com/docs/en/about-claude/use-case-guides/legal-summarization">
    Summarize legal documents using Claude to extract key information and expedite research.
  </Card>
</CardGroup>


---
title: Content moderation
url: https://platform.claude.com/docs/en/about-claude/use-case-guides/content-moderation
description: Content moderation is a critical aspect of maintaining a safe, respectful, and productive environment in digital applications. This guide discusses how Claude can be used to moderate content within your digital application.
---

> Visit the [content moderation cookbook](https://platform.claude.com/cookbook/misc-building-moderation-filter) to see an example content moderation implementation using Claude.

<Tip>
  This guide is focused on moderating user-generated content within your application. If you're looking for guidance on moderating interactions with Claude, refer to 

  [Mitigate jailbreaks and prompt injections](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)

  .
</Tip>


## Before building with Claude

Source: https://platform.claude.com/llms-full.txt#before-building-with-claude

### Decide whether to use Claude for content moderation

Here are some key indicators that you should use an LLM like Claude instead of a traditional ML or rules-based approach for content moderation:

<AccordionGroup>
  <Accordion title="You want a cost-effective and rapid implementation">
    Traditional ML methods require significant engineering resources, ML expertise, and infrastructure costs. Human moderation systems incur even higher costs. With Claude, you can have a sophisticated moderation system operational in significantly less time and at a much lower cost.
  </Accordion>

  <Accordion title="You want both semantic understanding and quick decisions">
    Traditional ML approaches, such as bag-of-words models or simple pattern matching, often struggle to understand the tone, intent, and context of the content. While human moderation systems excel at understanding semantic meaning, they require time for content to be reviewed. Claude addresses both needs by combining semantic understanding with the ability to deliver moderation decisions quickly.
  </Accordion>

  <Accordion title="You need consistent policy decisions">
    By leveraging its advanced reasoning capabilities, Claude can interpret and apply complex moderation guidelines uniformly. This consistency helps ensure fair treatment of all content, reducing the risk of inconsistent or biased moderation decisions that can undermine user trust.
  </Accordion>

  <Accordion title="Your moderation policies are likely to change or evolve over time">
    Once a traditional ML approach has been established, changing it is a laborious and data-intensive undertaking. On the other hand, as your product or customer needs evolve, Claude can easily adapt to changes or additions to moderation policies without extensive relabeling of training data.
  </Accordion>

  <Accordion title="You require interpretable reasoning for your moderation decisions">
    If you want to provide users or regulators with clear explanations behind moderation decisions, Claude can generate detailed and coherent justifications. This transparency is important for building trust and ensuring accountability in content moderation practices.
  </Accordion>

  <Accordion title="You need multilingual support without maintaining separate models">
    Traditional ML approaches typically require separate models or extensive translation processes for each supported language. Human moderation requires hiring a workforce fluent in each supported language. Claude’s multilingual capabilities allow it to classify tickets in various languages without the need for separate models or extensive translation processes, streamlining moderation for global customer bases.
  </Accordion>

  <Accordion title="You require multimodal support">
    Claude's multimodal capabilities allow it to analyze and interpret content across both text and images. This makes it a versatile tool for comprehensive content moderation in environments where different media types need to be evaluated together.
  </Accordion>
</AccordionGroup>

<Note>
  All Claude models are trained with built-in safety behaviors. This may result in Claude moderating content deemed particularly dangerous (in line with the 

  [Acceptable Use Policy](https://www.anthropic.com/legal/aup)

  ), regardless of the prompt used. For example, an adult website that wants to allow users to post explicit sexual content may find that Claude still flags explicit content as requiring moderation, even if they specify in their prompt not to moderate explicit sexual content. Consider reviewing the AUP in advance of building a moderation solution.
</Note>

### Generate examples of content to moderate

Before developing a content moderation solution, first create examples of content that should be flagged and content that should not be flagged. Ensure that you include edge cases and challenging scenarios that may be difficult for a content moderation system to handle effectively. Afterward, review your examples to create a well-defined list of moderation categories. For instance, the examples generated by a social media platform might include the following:

<CodeGroup exclude="shell">
  ```python Python
  client = anthropic.Anthropic()

  allowed_user_comments = [
      "This movie was great, I really enjoyed it. The main actor really killed it!",
      "I hate Mondays.",
      "It is a great time to invest in gold!",
  ]

  disallowed_user_comments = [
      "Delete this post now or you better hide. I am coming after you and your family.",
      "Stay away from the 5G cellphones!! They are using 5G to control you.",
      "Congratulations! You have won a $1,000 gift card. Click here to claim your prize!",
  ]

  # Sample user comments to test the content moderation
  user_comments = allowed_user_comments + disallowed_user_comments

  # Categories considered unsafe for content moderation
  unsafe_categories = [
      "Child Exploitation",
      "Conspiracy Theories",
      "Hate",
      "Indiscriminate Weapons",
      "Intellectual Property",
      "Non-Violent Crimes",
      "Privacy",
      "Self-Harm",
      "Sex Crimes",
      "Sexual Content",
      "Specialized Advice",
      "Violent Crimes",
  ]

typescript TypeScript
  const client = new Anthropic();

  const allowedUserComments = [
    "This movie was great, I really enjoyed it. The main actor really killed it!",
    "I hate Mondays.",
    "It is a great time to invest in gold!"
  ];

  const disallowedUserComments = [
    "Delete this post now or you better hide. I am coming after you and your family.",
    "Stay away from the 5G cellphones!! They are using 5G to control you.",
    "Congratulations! You have won a $1,000 gift card. Click here to claim your prize!"
  ];

  // Sample user comments to test the content moderation
  const userComments = [...allowedUserComments, ...disallowedUserComments];

  // Categories considered unsafe for content moderation
  const unsafeCategories = [
    "Child Exploitation",
    "Conspiracy Theories",
    "Hate",
    "Indiscriminate Weapons",
    "Intellectual Property",
    "Non-Violent Crimes",
    "Privacy",
    "Self-Harm",
    "Sex Crimes",
    "Sexual Content",
    "Specialized Advice",
    "Violent Crimes"
  ];

csharp C#
  var client = new AnthropicClient();

  string[] allowedUserComments =
  [
      "This movie was great, I really enjoyed it. The main actor really killed it!",
      "I hate Mondays.",
      "It is a great time to invest in gold!",
  ];

  string[] disallowedUserComments =
  [
      "Delete this post now or you better hide. I am coming after you and your family.",
      "Stay away from the 5G cellphones!! They are using 5G to control you.",
      "Congratulations! You have won a $1,000 gift card. Click here to claim your prize!",
  ];

  // Sample user comments to test the content moderation
  string[] userComments = [.. allowedUserComments, .. disallowedUserComments];

  // Categories considered unsafe for content moderation
  string[] unsafeCategories =
  [
      "Child Exploitation",
      "Conspiracy Theories",
      "Hate",
      "Indiscriminate Weapons",
      "Intellectual Property",
      "Non-Violent Crimes",
      "Privacy",
      "Self-Harm",
      "Sex Crimes",
      "Sexual Content",
      "Specialized Advice",
      "Violent Crimes",
  ];

go Go
  var client = anthropic.NewClient()

  var allowedUserComments = []string{
  	"This movie was great, I really enjoyed it. The main actor really killed it!",
  	"I hate Mondays.",
  	"It is a great time to invest in gold!",
  }

  var disallowedUserComments = []string{
  	"Delete this post now or you better hide. I am coming after you and your family.",
  	"Stay away from the 5G cellphones!! They are using 5G to control you.",
  	"Congratulations! You have won a $1,000 gift card. Click here to claim your prize!",
  }

  // Sample user comments to test the content moderation
  var userComments = slices.Concat(allowedUserComments, disallowedUserComments)

  // Categories considered unsafe for content moderation
  var unsafeCategories = []string{
  	"Child Exploitation",
  	"Conspiracy Theories",
  	"Hate",
  	"Indiscriminate Weapons",
  	"Intellectual Property",
  	"Non-Violent Crimes",
  	"Privacy",
  	"Self-Harm",
  	"Sex Crimes",
  	"Sexual Content",
  	"Specialized Advice",
  	"Violent Crimes",
  }

java Java
  final AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  final List<String> allowedUserComments = List.of(
          "This movie was great, I really enjoyed it. The main actor really killed it!",
          "I hate Mondays.",
          "It is a great time to invest in gold!");

  final List<String> disallowedUserComments = List.of(
          "Delete this post now or you better hide. I am coming after you and your family.",
          "Stay away from the 5G cellphones!! They are using 5G to control you.",
          "Congratulations! You have won a $1,000 gift card. Click here to claim your prize!");

  // Sample user comments to test the content moderation
  final List<String> userComments =
          Stream.concat(allowedUserComments.stream(), disallowedUserComments.stream()).toList();

  // Categories considered unsafe for content moderation
  final List<String> unsafeCategories = List.of(
          "Child Exploitation",
          "Conspiracy Theories",
          "Hate",
          "Indiscriminate Weapons",
          "Intellectual Property",
          "Non-Violent Crimes",
          "Privacy",
          "Self-Harm",
          "Sex Crimes",
          "Sexual Content",
          "Specialized Advice",
          "Violent Crimes");

php PHP
  $client = new Client();

  $allowedUserComments = [
      'This movie was great, I really enjoyed it. The main actor really killed it!',
      'I hate Mondays.',
      'It is a great time to invest in gold!',
  ];

  $disallowedUserComments = [
      'Delete this post now or you better hide. I am coming after you and your family.',
      'Stay away from the 5G cellphones!! They are using 5G to control you.',
      'Congratulations! You have won a $1,000 gift card. Click here to claim your prize!',
  ];

  // Sample user comments to test the content moderation
  $userComments = [...$allowedUserComments, ...$disallowedUserComments];

  // Categories considered unsafe for content moderation
  $unsafeCategories = [
      'Child Exploitation',
      'Conspiracy Theories',
      'Hate',
      'Indiscriminate Weapons',
      'Intellectual Property',
      'Non-Violent Crimes',
      'Privacy',
      'Self-Harm',
      'Sex Crimes',
      'Sexual Content',
      'Specialized Advice',
      'Violent Crimes',
  ];

ruby Ruby
  CLIENT = Anthropic::Client.new

  ALLOWED_USER_COMMENTS = [
    "This movie was great, I really enjoyed it. The main actor really killed it!",
    "I hate Mondays.",
    "It is a great time to invest in gold!"
  ]

  DISALLOWED_USER_COMMENTS = [
    "Delete this post now or you better hide. I am coming after you and your family.",
    "Stay away from the 5G cellphones!! They are using 5G to control you.",
    "Congratulations! You have won a $1,000 gift card. Click here to claim your prize!"
  ]

  # Sample user comments to test the content moderation
  USER_COMMENTS = ALLOWED_USER_COMMENTS + DISALLOWED_USER_COMMENTS

  # Categories considered unsafe for content moderation
  UNSAFE_CATEGORIES = [
    "Child Exploitation",
    "Conspiracy Theories",
    "Hate",
    "Indiscriminate Weapons",
    "Intellectual Property",
    "Non-Violent Crimes",
    "Privacy",
    "Self-Harm",
    "Sex Crimes",
    "Sexual Content",
    "Specialized Advice",
    "Violent Crimes"
  ]
  ```
</CodeGroup>

Effectively moderating these examples requires a nuanced understanding of language. In the comment, `This movie was great, I really enjoyed it. The main actor really killed it!`, the content moderation system needs to recognize that "killed it" is a metaphor, not an indication of actual violence. Conversely, despite the lack of explicit mentions of violence, the comment `Delete this post now or you better hide. I am coming after you and your family.` should be flagged by the content moderation system.

The unsafe categories can be customized to fit your specific needs. For example, if you want to prevent minors from creating content on your website, you could add "Underage Posting" to the categories.

***


## How to moderate content using Claude

Source: https://platform.claude.com/llms-full.txt#how-to-moderate-content-using-claude

### Select the right Claude model

When selecting a model, it’s important to consider the size of your data. If costs are a concern, a smaller model such as Claude Haiku 4.5 is an excellent choice because of its cost-effectiveness. The following is an estimate of the cost to moderate text for a social media platform that receives one billion posts per month:

* **Content size**

  * Posts per month: 1B
  * Characters per post: 100
  * Total characters: 100B

* **Estimated tokens**

  * Input tokens: 28.6B (assuming 1 token per 3.5 characters)
  * Percentage of messages flagged: 3%
  * Output tokens per flagged message: 50
  * Total output tokens: 1.5B

* **Claude Haiku 4.5 estimated cost**

  * Input token cost: 28,600 MTok \* $1.00/MTok = $28,600 USD
  * Output token cost: 1,500 MTok \* $5.00/MTok = $7,500 USD
  * Monthly cost: $28,600 + $7,500 = $36,100 USD

* **Claude Opus 5 estimated cost**

  * Input token cost: 28,600 MTok \* $5.00/MTok = $143,000 USD
  * Output token cost: 1,500 MTok \* $25.00/MTok = $37,500 USD
  * Monthly cost: $143,000 + $37,500 = $180,500 USD

* **Claude Opus 4.8 estimated cost**

  * Input token cost: 28,600 MTok \* $5.00/MTok = $143,000 USD
  * Output token cost: 1,500 MTok \* $25.00/MTok = $37,500 USD
  * Monthly cost: $143,000 + $37,500 = $180,500 USD

<Tip>
  Actual costs may differ from these estimates. These estimates are based on the prompt highlighted in the section on 

  [batch processing](https://platform.claude.com/docs/en/about-claude/use-case-guides/content-moderation#consider-batch-processing)

  . Output tokens can be reduced even further by removing the 

  `explanation`

   field from the response.
</Tip>

### Build a strong prompt

To use Claude for content moderation, Claude must understand the moderation requirements of your application. Start by writing a prompt that allows you to define your moderation needs:

<CodeGroup exclude="shell">
  ```python Python
  def moderate_message(message, unsafe_categories):
      # Convert the unsafe categories into a string, with each category on a new line
      unsafe_category_str = "\n".join(unsafe_categories)

      # Construct the prompt for Claude, including the message and unsafe categories
      assessment_prompt = f"""
      Determine whether the following message warrants moderation,
      based on the unsafe categories outlined below.

      Message:
      <message>{message}</message>

      Unsafe Categories:
      <categories>
      {unsafe_category_str}
      </categories>

      Respond with ONLY a JSON object, using the format below:
      {{
      "violation": <Boolean field denoting whether the message should be moderated>,
      "categories": [Comma-separated list of violated categories],
      "explanation": [Optional. Only include if there is a violation.]
      }}
  Do not include markdown formatting or code fences in your response."""

      # Send the request to Claude for content moderation
      response = client.messages.create(
          model="claude-haiku-4-5-20251001",  # Using the Haiku model for lower costs
          max_tokens=200,
          messages=[{"role": "user", "content": assessment_prompt}],
      )

      # Parse the JSON response from Claude
      text_block = next(block for block in response.content if block.type == "text")
      assessment = json.loads(text_block.text)

      # Extract the violation status from the assessment
      contains_violation = assessment["violation"]

      # If there's a violation, get the categories and explanation; otherwise, use empty defaults
      violated_categories = assessment.get("categories", []) if contains_violation else []
      explanation = assessment.get("explanation") if contains_violation else None

      return contains_violation, violated_categories, explanation


  # Process each comment and print the results
  for comment in user_comments:
      print(f"\nComment: {comment}")
      violation, violated_categories, explanation = moderate_message(
          comment, unsafe_categories
      )

      if violation:
          print(f"Violated Categories: {', '.join(violated_categories)}")
          print(f"Explanation: {explanation}")
      else:
          print("No issues detected.")

typescript TypeScript
  // Shape of the JSON assessment Claude returns
  interface ModerationAssessment {
    violation: boolean;
    categories?: string[];
    explanation?: string;
  }

  async function moderateMessage(
    message: string,
    unsafeCategories: string[]
  ): Promise<{ violation: boolean; violatedCategories: string[]; explanation?: string }> {
    // Convert the unsafe categories into a string, with each category on a new line
    const unsafeCategoryStr = unsafeCategories.join("\n");

    // Construct the prompt for Claude, including the message and unsafe categories
    const assessmentPrompt = `
      Determine whether the following message warrants moderation,
      based on the unsafe categories outlined below.

      Message:
      <message>${message}</message>

      Unsafe Categories:
      <categories>
      ${unsafeCategoryStr}
      </categories>

      Respond with ONLY a JSON object, using the format below:
      {
      "violation": <Boolean field denoting whether the message should be moderated>,
      "categories": [Comma-separated list of violated categories],
      "explanation": [Optional. Only include if there is a violation.]
      }
  Do not include markdown formatting or code fences in your response.`;

    // Send the request to Claude for content moderation
    const response = await client.messages.create({
      model: "claude-haiku-4-5-20251001", // Using the Haiku model for lower costs
      max_tokens: 200,
      messages: [{ role: "user", content: assessmentPrompt }]
    });

    // Parse the JSON response from Claude
    const textBlock = response.content.find((block) => block.type === "text");
    if (!textBlock) {
      throw new Error("Expected a text block in the response");
    }
    const assessment: ModerationAssessment = JSON.parse(textBlock.text);

    // Extract the violation status from the assessment
    const containsViolation = assessment.violation;

    // If there's a violation, get the categories and explanation; otherwise, use empty defaults
    const violatedCategories = containsViolation ? assessment.categories ?? [] : [];
    const explanation = containsViolation ? assessment.explanation : undefined;

    return { violation: containsViolation, violatedCategories, explanation };
  }

  // Process each comment and print the results
  for (const comment of userComments) {
    console.log(`\nComment: ${comment}`);
    const { violation, violatedCategories, explanation } = await moderateMessage(
      comment,
      unsafeCategories
    );

    if (violation) {
      console.log(`Violated Categories: ${violatedCategories.join(", ")}`);
      console.log(`Explanation: ${explanation}`);
    } else {
      console.log("No issues detected.");
    }
  }

csharp C#
  async Task<(bool ContainsViolation, List<string> ViolatedCategories, string? Explanation)> ModerateMessage(
      string message,
      IReadOnlyList<string> categories
  )
  {
      // Convert the unsafe categories into a string, with each category on a new line
      var unsafeCategoryText = string.Join("\n", categories);

      // Construct the prompt for Claude, including the message and unsafe categories
      var assessmentPrompt = $$"""

      Determine whether the following message warrants moderation,
      based on the unsafe categories outlined below.

      Message:
      <message>{{message}}</message>

      Unsafe Categories:
      <categories>
      {{unsafeCategoryText}}
      </categories>

      Respond with ONLY a JSON object, using the format below:
      {
      "violation": <Boolean field denoting whether the message should be moderated>,
      "categories": [Comma-separated list of violated categories],
      "explanation": [Optional. Only include if there is a violation.]
      }
  Do not include markdown formatting or code fences in your response.
  """;

      // Send the request to Claude for content moderation
      var response = await client.Messages.Create(
          new()
          {
              Model = Model.ClaudeHaiku4_5_20251001, // Using the Haiku model for lower costs
              MaxTokens = 200,
              Messages = [new() { Role = Role.User, Content = assessmentPrompt }],
          }
      );

      // Narrow the first content block to a text block, then parse Claude's JSON response
      if (!response.Content[0].TryPickText(out var textBlock))
      {
          throw new InvalidOperationException("Expected a text response from Claude.");
      }
      var assessment = JsonNode.Parse(textBlock.Text)!;

      // Extract the violation status from the assessment
      var containsViolation = assessment["violation"]!.GetValue<bool>();

      // If there's a violation, get the categories and explanation; otherwise, use empty defaults
      List<string> violatedCategories = containsViolation
          ? assessment["categories"]?.AsArray().Select(category => category!.GetValue<string>()).ToList() ?? []
          : [];
      var explanation = containsViolation ? assessment["explanation"]?.GetValue<string>() : null;

      return (containsViolation, violatedCategories, explanation);
  }

  // Process each comment and print the results
  foreach (var comment in userComments)
  {
      Console.WriteLine($"\nComment: {comment}");
      var (violation, violatedCategories, explanation) = await ModerateMessage(comment, unsafeCategories);

      if (violation)
      {
          Console.WriteLine($"Violated Categories: {string.Join(", ", violatedCategories)}");
          Console.WriteLine($"Explanation: {explanation}");
      }
      else
      {
          Console.WriteLine("No issues detected.");
      }
  }

go Go
  func moderateMessage(message string, unsafeCategories []string) (bool, []string, string) {
  	// Convert the unsafe categories into a string, with each category on a new line
  	unsafeCategoryStr := strings.Join(unsafeCategories, "\n")

  	// Construct the prompt for Claude, including the message and unsafe categories
  	assessmentPrompt := fmt.Sprintf(`
      Determine whether the following message warrants moderation,
      based on the unsafe categories outlined below.

      Message:
      <message>%s</message>

      Unsafe Categories:
      <categories>
      %s
      </categories>

      Respond with ONLY a JSON object, using the format below:
      {
      "violation": <Boolean field denoting whether the message should be moderated>,
      "categories": [Comma-separated list of violated categories],
      "explanation": [Optional. Only include if there is a violation.]
      }
  Do not include markdown formatting or code fences in your response.`, message, unsafeCategoryStr)

  	// Send the request to Claude for content moderation
  	response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeHaiku4_5_20251001, // Using the Haiku model for lower costs
  		MaxTokens: 200,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock(assessmentPrompt)),
  		},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	// Narrow the first content block to a text block before reading its text
  	textBlock, ok := response.Content[0].AsAny().(anthropic.TextBlock)
  	if !ok {
  		log.Fatalf("expected a text block, got %q", response.Content[0].Type)
  	}

  	// Parse the JSON response from Claude
  	var assessment struct {
  		Violation   bool     `json:"violation"`
  		Categories  []string `json:"categories"`
  		Explanation string   `json:"explanation"`
  	}
  	if err := json.Unmarshal([]byte(textBlock.Text), &assessment); err != nil {
  		log.Fatal(err)
  	}

  	// If there's a violation, return the categories and explanation; otherwise, use empty defaults
  	if !assessment.Violation {
  		return false, nil, ""
  	}
  	return true, assessment.Categories, assessment.Explanation
  }

  // moderateAllComments processes each comment and prints the results.
  func moderateAllComments() {
  	for _, comment := range userComments {
  		fmt.Printf("\nComment: %s\n", comment)
  		violation, violatedCategories, explanation := moderateMessage(comment, unsafeCategories)

  		if violation {
  			fmt.Printf("Violated Categories: %s\n", strings.Join(violatedCategories, ", "))
  			fmt.Printf("Explanation: %s\n", explanation)
  		} else {
  			fmt.Println("No issues detected.")
  		}
  	}
  }

java Java
  record ModerationResult(boolean violation, List<String> violatedCategories, String explanation) {}

  ModerationResult moderateMessage(String message, List<String> unsafeCategories)
          throws JsonProcessingException {
      // Convert the unsafe categories into a string, with each category on a new line
      String unsafeCategoryStr = String.join("\n", unsafeCategories);

      // Construct the prompt for Claude, including the message and unsafe categories
      String assessmentPrompt = """

              Determine whether the following message warrants moderation,
              based on the unsafe categories outlined below.

              Message:
              <message>%s</message>

              Unsafe Categories:
              <categories>
              %s
              </categories>

              Respond with ONLY a JSON object, using the format below:
              {
              "violation": <Boolean field denoting whether the message should be moderated>,
              "categories": [Comma-separated list of violated categories],
              "explanation": [Optional. Only include if there is a violation.]
              }
          Do not include markdown formatting or code fences in your response."""
              .formatted(message, unsafeCategoryStr);

      // Send the request to Claude for content moderation
      Message response = client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_HAIKU_4_5_20251001) // Using the Haiku model for lower costs
              .maxTokens(200)
              .addUserMessage(assessmentPrompt)
              .build());

      // Parse the JSON response from Claude
      String assessmentJson = response.content().stream()
              .flatMap(contentBlock -> contentBlock.text().stream())
              .findFirst()
              .orElseThrow()
              .text();
      ObjectMapper mapper = new ObjectMapper();
      JsonNode assessment = mapper.readTree(assessmentJson);

      // Extract the violation status from the assessment
      boolean containsViolation = assessment.required("violation").asBoolean();

      // If there's a violation, get the categories and explanation; otherwise, use empty defaults
      List<String> violatedCategories = containsViolation && assessment.has("categories")
              ? mapper.convertValue(assessment.get("categories"), new TypeReference<List<String>>() {})
              : List.of();
      String explanation = containsViolation && assessment.hasNonNull("explanation")
              ? assessment.get("explanation").asText()
              : null;

      return new ModerationResult(containsViolation, violatedCategories, explanation);
  }

  // Process each comment and print the results
  void printModerationResults() throws JsonProcessingException {
      for (String comment : userComments) {
          IO.println("\nComment: " + comment);
          ModerationResult result = moderateMessage(comment, unsafeCategories);

          if (result.violation()) {
              IO.println("Violated Categories: " + String.join(", ", result.violatedCategories()));
              IO.println("Explanation: " + result.explanation());
          } else {
              IO.println("No issues detected.");
          }
      }
  }

php PHP
  $moderateMessage = function (string $message, array $unsafeCategories) use ($client): array {
      // Convert the unsafe categories into a string, with each category on a new line
      $unsafeCategoryStr = implode("\n", $unsafeCategories);

      // Construct the prompt for Claude, including the message and unsafe categories
      $assessmentPrompt = <<<PROMPT

          Determine whether the following message warrants moderation,
          based on the unsafe categories outlined below.

          Message:
          <message>{$message}</message>

          Unsafe Categories:
          <categories>
          {$unsafeCategoryStr}
          </categories>

          Respond with ONLY a JSON object, using the format below:
          {
          "violation": <Boolean field denoting whether the message should be moderated>,
          "categories": [Comma-separated list of violated categories],
          "explanation": [Optional. Only include if there is a violation.]
          }
      Do not include markdown formatting or code fences in your response.
      PROMPT;

      // Send the request to Claude for content moderation
      $response = $client->messages->create(
          model: 'claude-haiku-4-5-20251001', // Using the Haiku model for lower costs
          maxTokens: 200,
          messages: [['role' => 'user', 'content' => $assessmentPrompt]],
      );

      // Parse the JSON response from Claude. The SDK decodes each content block
      // into its concrete class, so find the TextBlock before reading the text.
      $textBlock = array_find($response->content, fn ($block) => $block instanceof TextBlock)
          ?? throw new RuntimeException('Expected a text block in the response.');
      $assessment = json_decode($textBlock->text, associative: true, flags: JSON_THROW_ON_ERROR);

      // Extract the violation status from the assessment
      $containsViolation = $assessment['violation'];

      // If there's a violation, get the categories and explanation; otherwise, use empty defaults
      $violatedCategories = $containsViolation ? ($assessment['categories'] ?? []) : [];
      $explanation = $containsViolation ? ($assessment['explanation'] ?? null) : null;

      return [$containsViolation, $violatedCategories, $explanation];
  };

  // Process each comment and print the results
  foreach ($userComments as $comment) {
      echo "\nComment: {$comment}\n";
      [$violation, $violatedCategories, $explanation] = $moderateMessage($comment, $unsafeCategories);

      if ($violation) {
          echo 'Violated Categories: ' . implode(', ', $violatedCategories) . "\n";
          echo "Explanation: {$explanation}\n";
      } else {
          echo "No issues detected.\n";
      }
  }

ruby Ruby
  def moderate_message(message, unsafe_categories)
    # Convert the unsafe categories into a string, with each category on a new line
    unsafe_category_str = unsafe_categories.join("\n")

    # Construct the prompt for Claude, including the message and unsafe categories
    assessment_prompt = <<~PROMPT.chomp

          Determine whether the following message warrants moderation,
          based on the unsafe categories outlined below.

          Message:
          <message>#{message}</message>

          Unsafe Categories:
          <categories>
          #{unsafe_category_str}
          </categories>

          Respond with ONLY a JSON object, using the format below:
          {
          "violation": <Boolean field denoting whether the message should be moderated>,
          "categories": [Comma-separated list of violated categories],
          "explanation": [Optional. Only include if there is a violation.]
          }
      Do not include markdown formatting or code fences in your response.
    PROMPT

    # Send the request to Claude for content moderation
    response = CLIENT.messages.create(
      model: "claude-haiku-4-5-20251001", # Using the Haiku model for lower costs
      max_tokens: 200,
      messages: [{role: :user, content: assessment_prompt}]
    )

    # Parse the JSON response from Claude
    text_block = response.content.find { it.type == :text }
    assessment = JSON.parse(text_block.text)

    # Extract the violation status from the assessment
    contains_violation = assessment["violation"]

    # If there's a violation, get the categories and explanation; otherwise, use empty defaults
    violated_categories = contains_violation ? assessment.fetch("categories", []) : []
    explanation = contains_violation ? assessment["explanation"] : nil

    [contains_violation, violated_categories, explanation]
  end


  # Process each comment and print the results
  USER_COMMENTS.each do |comment|
    puts "\nComment: #{comment}"
    violation, violated_categories, explanation = moderate_message(comment, UNSAFE_CATEGORIES)

    if violation
      puts "Violated Categories: #{violated_categories.join(", ")}"
      puts "Explanation: #{explanation}"
    else
      puts "No issues detected."
    end
  end

python Python
  def assess_risk_level(message, unsafe_categories):
      # Convert the unsafe categories into a string, with each category on a new line
      unsafe_category_str = "\n".join(unsafe_categories)

      # Construct the prompt for Claude, including the message, unsafe categories, and risk level definitions
      assessment_prompt = f"""
      Assess the risk level of the following message,
      based on the unsafe categories listed below.

  Message:
  <message>{message}</message>

  Unsafe Categories:
  <categories>
  {unsafe_category_str}
  </categories>

  Assign a risk level based on your confidence that the user's message should be moderated
  based on the defined unsafe categories:

  0 - No risk
  1 - Low risk
  2 - Medium risk
  3 - High risk

  Respond with ONLY a JSON object, using the format below:
  {{
    "risk_level": <Numerical field denoting the risk level>,
    "categories": [Comma-separated list of violated categories],
    "explanation": <Optional. Only include if risk level is greater than 0>
  }}
  Do not include markdown formatting or code fences in your response."""

      # Send the request to Claude for risk assessment
      response = client.messages.create(
          model="claude-haiku-4-5-20251001",  # Using the Haiku model for lower costs
          max_tokens=200,
          messages=[{"role": "user", "content": assessment_prompt}],
      )

      # Parse the JSON response from Claude
      text_block = next(block for block in response.content if block.type == "text")
      assessment = json.loads(text_block.text)

      # Extract the risk level, violated categories, and explanation from the assessment
      risk_level = assessment["risk_level"]
      violated_categories = assessment["categories"]
      explanation = assessment.get("explanation")

      return risk_level, violated_categories, explanation


  # Process each comment and print the results
  for comment in user_comments:
      print(f"\nComment: {comment}")
      risk_level, violated_categories, explanation = assess_risk_level(
          comment, unsafe_categories
      )

      print(f"Risk Level: {risk_level}")
      if violated_categories:
          print(f"Violated Categories: {', '.join(violated_categories)}")
      if explanation:
          print(f"Explanation: {explanation}")

typescript TypeScript
  // Shape of the JSON risk assessment Claude returns
  interface RiskAssessment {
    risk_level: number;
    categories: string[];
    explanation?: string;
  }

  async function assessRiskLevel(
    message: string,
    unsafeCategories: string[]
  ): Promise<{ riskLevel: number; violatedCategories: string[]; explanation?: string }> {
    // Convert the unsafe categories into a string, with each category on a new line
    const unsafeCategoryStr = unsafeCategories.join("\n");

    // Construct the prompt for Claude, including the message, unsafe categories, and risk level definitions
    const assessmentPrompt = `
      Assess the risk level of the following message,
      based on the unsafe categories listed below.

  Message:
  <message>${message}</message>

  Unsafe Categories:
  <categories>
  ${unsafeCategoryStr}
  </categories>

  Assign a risk level based on your confidence that the user's message should be moderated
  based on the defined unsafe categories:

  0 - No risk
  1 - Low risk
  2 - Medium risk
  3 - High risk

  Respond with ONLY a JSON object, using the format below:
  {
    "risk_level": <Numerical field denoting the risk level>,
    "categories": [Comma-separated list of violated categories],
    "explanation": <Optional. Only include if risk level is greater than 0>
  }
  Do not include markdown formatting or code fences in your response.`;

    // Send the request to Claude for risk assessment
    const response = await client.messages.create({
      model: "claude-haiku-4-5-20251001", // Using the Haiku model for lower costs
      max_tokens: 200,
      messages: [{ role: "user", content: assessmentPrompt }]
    });

    // Parse the JSON response from Claude
    const textBlock = response.content.find((block) => block.type === "text");
    if (!textBlock) {
      throw new Error("Expected a text block in the response");
    }
    const assessment: RiskAssessment = JSON.parse(textBlock.text);

    // Extract the risk level, violated categories, and explanation from the assessment
    const { risk_level: riskLevel, categories: violatedCategories, explanation } = assessment;

    return { riskLevel, violatedCategories, explanation };
  }

  // Process each comment and print the results
  for (const comment of userComments) {
    console.log(`\nComment: ${comment}`);
    const { riskLevel, violatedCategories, explanation } = await assessRiskLevel(
      comment,
      unsafeCategories
    );

    console.log(`Risk Level: ${riskLevel}`);
    if (violatedCategories.length > 0) {
      console.log(`Violated Categories: ${violatedCategories.join(", ")}`);
    }
    if (explanation) {
      console.log(`Explanation: ${explanation}`);
    }
  }

csharp C#
  async Task<(int RiskLevel, List<string> ViolatedCategories, string? Explanation)> AssessRiskLevel(
      string message,
      IReadOnlyList<string> categories
  )
  {
      // Convert the unsafe categories into a string, with each category on a new line
      var unsafeCategoryText = string.Join("\n", categories);

      // Construct the prompt for Claude, including the message, unsafe categories, and risk level definitions
      var assessmentPrompt = $$"""

      Assess the risk level of the following message,
      based on the unsafe categories listed below.

  Message:
  <message>{{message}}</message>

  Unsafe Categories:
  <categories>
  {{unsafeCategoryText}}
  </categories>

  Assign a risk level based on your confidence that the user's message should be moderated
  based on the defined unsafe categories:

  0 - No risk
  1 - Low risk
  2 - Medium risk
  3 - High risk

  Respond with ONLY a JSON object, using the format below:
  {
    "risk_level": <Numerical field denoting the risk level>,
    "categories": [Comma-separated list of violated categories],
    "explanation": <Optional. Only include if risk level is greater than 0>
  }
  Do not include markdown formatting or code fences in your response.
  """;

      // Send the request to Claude for risk assessment
      var response = await client.Messages.Create(
          new()
          {
              Model = Model.ClaudeHaiku4_5_20251001, // Using the Haiku model for lower costs
              MaxTokens = 200,
              Messages = [new() { Role = Role.User, Content = assessmentPrompt }],
          }
      );

      // Narrow the first content block to a text block, then parse Claude's JSON response
      if (!response.Content[0].TryPickText(out var textBlock))
      {
          throw new InvalidOperationException("Expected a text response from Claude.");
      }
      var assessment = JsonNode.Parse(textBlock.Text)!;

      // Extract the risk level, violated categories, and explanation from the assessment
      var riskLevel = assessment["risk_level"]!.GetValue<int>();
      var violatedCategories = assessment["categories"]!
          .AsArray()
          .Select(category => category!.GetValue<string>())
          .ToList();
      var explanation = assessment["explanation"]?.GetValue<string>();

      return (riskLevel, violatedCategories, explanation);
  }

  // Process each comment and print the results
  foreach (var comment in userComments)
  {
      Console.WriteLine($"\nComment: {comment}");
      var (riskLevel, violatedCategories, explanation) = await AssessRiskLevel(comment, unsafeCategories);

      Console.WriteLine($"Risk Level: {riskLevel}");
      if (violatedCategories.Count > 0)
      {
          Console.WriteLine($"Violated Categories: {string.Join(", ", violatedCategories)}");
      }
      if (!string.IsNullOrEmpty(explanation))
      {
          Console.WriteLine($"Explanation: {explanation}");
      }
  }

go Go
  func assessRiskLevel(message string, unsafeCategories []string) (int, []string, string) {
  	// Convert the unsafe categories into a string, with each category on a new line
  	unsafeCategoryStr := strings.Join(unsafeCategories, "\n")

  	// Construct the prompt for Claude, including the message, unsafe categories, and risk level definitions
  	assessmentPrompt := fmt.Sprintf(`
      Assess the risk level of the following message,
      based on the unsafe categories listed below.

  Message:
  <message>%s</message>

  Unsafe Categories:
  <categories>
  %s
  </categories>

  Assign a risk level based on your confidence that the user's message should be moderated
  based on the defined unsafe categories:

  0 - No risk
  1 - Low risk
  2 - Medium risk
  3 - High risk

  Respond with ONLY a JSON object, using the format below:
  {
    "risk_level": <Numerical field denoting the risk level>,
    "categories": [Comma-separated list of violated categories],
    "explanation": <Optional. Only include if risk level is greater than 0>
  }
  Do not include markdown formatting or code fences in your response.`, message, unsafeCategoryStr)

  	// Send the request to Claude for risk assessment
  	response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeHaiku4_5_20251001, // Using the Haiku model for lower costs
  		MaxTokens: 200,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock(assessmentPrompt)),
  		},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	// Narrow the first content block to a text block before reading its text
  	textBlock, ok := response.Content[0].AsAny().(anthropic.TextBlock)
  	if !ok {
  		log.Fatalf("expected a text block, got %q", response.Content[0].Type)
  	}

  	// Parse the JSON response from Claude
  	var assessment struct {
  		RiskLevel   int      `json:"risk_level"`
  		Categories  []string `json:"categories"`
  		Explanation string   `json:"explanation"`
  	}
  	if err := json.Unmarshal([]byte(textBlock.Text), &assessment); err != nil {
  		log.Fatal(err)
  	}

  	// Return the risk level, violated categories, and explanation from the assessment
  	return assessment.RiskLevel, assessment.Categories, assessment.Explanation
  }

  // assessAllRiskLevels processes each comment and prints the results.
  func assessAllRiskLevels() {
  	for _, comment := range userComments {
  		fmt.Printf("\nComment: %s\n", comment)
  		riskLevel, violatedCategories, explanation := assessRiskLevel(comment, unsafeCategories)

  		fmt.Printf("Risk Level: %d\n", riskLevel)
  		if len(violatedCategories) > 0 {
  			fmt.Printf("Violated Categories: %s\n", strings.Join(violatedCategories, ", "))
  		}
  		if explanation != "" {
  			fmt.Printf("Explanation: %s\n", explanation)
  		}
  	}
  }

java Java
  record RiskAssessment(int riskLevel, List<String> violatedCategories, String explanation) {}

  RiskAssessment assessRiskLevel(String message, List<String> unsafeCategories)
          throws JsonProcessingException {
      // Convert the unsafe categories into a string, with each category on a new line
      String unsafeCategoryStr = String.join("\n", unsafeCategories);

      // Construct the prompt for Claude, including the message, unsafe categories, and risk level definitions
      String assessmentPrompt = """

              Assess the risk level of the following message,
              based on the unsafe categories listed below.

          Message:
          <message>%s</message>

          Unsafe Categories:
          <categories>
          %s
          </categories>

          Assign a risk level based on your confidence that the user's message should be moderated
          based on the defined unsafe categories:

          0 - No risk
          1 - Low risk
          2 - Medium risk
          3 - High risk

          Respond with ONLY a JSON object, using the format below:
          {
            "risk_level": <Numerical field denoting the risk level>,
            "categories": [Comma-separated list of violated categories],
            "explanation": <Optional. Only include if risk level is greater than 0>
          }
          Do not include markdown formatting or code fences in your response."""
              .formatted(message, unsafeCategoryStr);

      // Send the request to Claude for risk assessment
      Message response = client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_HAIKU_4_5_20251001) // Using the Haiku model for lower costs
              .maxTokens(200)
              .addUserMessage(assessmentPrompt)
              .build());

      // Parse the JSON response from Claude
      String assessmentJson = response.content().stream()
              .flatMap(contentBlock -> contentBlock.text().stream())
              .findFirst()
              .orElseThrow()
              .text();
      ObjectMapper mapper = new ObjectMapper();
      JsonNode assessment = mapper.readTree(assessmentJson);

      // Extract the risk level, violated categories, and explanation from the assessment
      int riskLevel = assessment.required("risk_level").asInt();
      JsonNode categoriesNode = assessment.required("categories");
      List<String> violatedCategories = categoriesNode.isNull()
              ? List.of()
              : mapper.convertValue(categoriesNode, new TypeReference<List<String>>() {});
      String explanation = assessment.hasNonNull("explanation")
              ? assessment.get("explanation").asText()
              : null;

      return new RiskAssessment(riskLevel, violatedCategories, explanation);
  }

  // Process each comment and print the results
  void printRiskLevels() throws JsonProcessingException {
      for (String comment : userComments) {
          IO.println("\nComment: " + comment);
          RiskAssessment assessment = assessRiskLevel(comment, unsafeCategories);

          IO.println("Risk Level: " + assessment.riskLevel());
          if (!assessment.violatedCategories().isEmpty()) {
              IO.println("Violated Categories: " + String.join(", ", assessment.violatedCategories()));
          }
          if (assessment.explanation() != null && !assessment.explanation().isEmpty()) {
              IO.println("Explanation: " + assessment.explanation());
          }
      }
  }

php PHP
  $assessRiskLevel = function (string $message, array $unsafeCategories) use ($client): array {
      // Convert the unsafe categories into a string, with each category on a new line
      $unsafeCategoryStr = implode("\n", $unsafeCategories);

      // Construct the prompt for Claude, including the message, unsafe categories, and risk level definitions
      $assessmentPrompt = <<<PROMPT

          Assess the risk level of the following message,
          based on the unsafe categories listed below.

      Message:
      <message>{$message}</message>

      Unsafe Categories:
      <categories>
      {$unsafeCategoryStr}
      </categories>

      Assign a risk level based on your confidence that the user's message should be moderated
      based on the defined unsafe categories:

      0 - No risk
      1 - Low risk
      2 - Medium risk
      3 - High risk

      Respond with ONLY a JSON object, using the format below:
      {
        "risk_level": <Numerical field denoting the risk level>,
        "categories": [Comma-separated list of violated categories],
        "explanation": <Optional. Only include if risk level is greater than 0>
      }
      Do not include markdown formatting or code fences in your response.
      PROMPT;

      // Send the request to Claude for risk assessment
      $response = $client->messages->create(
          model: 'claude-haiku-4-5-20251001', // Using the Haiku model for lower costs
          maxTokens: 200,
          messages: [['role' => 'user', 'content' => $assessmentPrompt]],
      );

      // Parse the JSON response from Claude. The SDK decodes each content block
      // into its concrete class, so find the TextBlock before reading the text.
      $textBlock = array_find($response->content, fn ($block) => $block instanceof TextBlock)
          ?? throw new RuntimeException('Expected a text block in the response.');
      $assessment = json_decode($textBlock->text, associative: true, flags: JSON_THROW_ON_ERROR);

      // Extract the risk level, violated categories, and explanation from the assessment
      $riskLevel = $assessment['risk_level'];
      $violatedCategories = $assessment['categories'];
      $explanation = $assessment['explanation'] ?? null;

      return [$riskLevel, $violatedCategories, $explanation];
  };

  // Process each comment and print the results
  foreach ($userComments as $comment) {
      echo "\nComment: {$comment}\n";
      [$riskLevel, $violatedCategories, $explanation] = $assessRiskLevel($comment, $unsafeCategories);

      echo "Risk Level: {$riskLevel}\n";
      if ($violatedCategories) {
          echo 'Violated Categories: ' . implode(', ', $violatedCategories) . "\n";
      }
      if ($explanation) {
          echo "Explanation: {$explanation}\n";
      }
  }

ruby Ruby
  def assess_risk_level(message, unsafe_categories)
    # Convert the unsafe categories into a string, with each category on a new line
    unsafe_category_str = unsafe_categories.join("\n")

    # Construct the prompt for Claude, including the message, unsafe categories, and risk level definitions
    assessment_prompt = <<~PROMPT.chomp

          Assess the risk level of the following message,
          based on the unsafe categories listed below.

      Message:
      <message>#{message}</message>

      Unsafe Categories:
      <categories>
      #{unsafe_category_str}
      </categories>

      Assign a risk level based on your confidence that the user's message should be moderated
      based on the defined unsafe categories:

      0 - No risk
      1 - Low risk
      2 - Medium risk
      3 - High risk

      Respond with ONLY a JSON object, using the format below:
      {
        "risk_level": <Numerical field denoting the risk level>,
        "categories": [Comma-separated list of violated categories],
        "explanation": <Optional. Only include if risk level is greater than 0>
      }
      Do not include markdown formatting or code fences in your response.
    PROMPT

    # Send the request to Claude for risk assessment
    response = CLIENT.messages.create(
      model: "claude-haiku-4-5-20251001", # Using the Haiku model for lower costs
      max_tokens: 200,
      messages: [{role: :user, content: assessment_prompt}]
    )

    # Parse the JSON response from Claude
    text_block = response.content.find { it.type == :text }
    assessment = JSON.parse(text_block.text)

    # Extract the risk level, violated categories, and explanation from the assessment
    risk_level = assessment["risk_level"]
    violated_categories = assessment["categories"]
    explanation = assessment["explanation"]

    [risk_level, violated_categories, explanation]
  end


  # Process each comment and print the results
  USER_COMMENTS.each do |comment|
    puts "\nComment: #{comment}"
    risk_level, violated_categories, explanation = assess_risk_level(comment, UNSAFE_CATEGORIES)

    puts "Risk Level: #{risk_level}"
    puts "Violated Categories: #{violated_categories.join(", ")}" if violated_categories&.any?
    puts "Explanation: #{explanation}" if explanation
  end
  ```
</CodeGroup>

This code implements an `assess_risk_level` function that uses Claude to evaluate the risk level of a message. The function accepts a message and the unsafe categories as inputs.

Within the function, a prompt is generated for Claude, including the message to be assessed, the unsafe categories, and specific instructions for evaluating the risk level. The prompt instructs Claude to respond with a JSON object that includes the risk level, the violated categories, and an optional explanation.

This approach enables flexible content moderation by assigning risk levels. It can be seamlessly integrated into a larger system to automate content filtering or flag comments for human review based on their assessed risk level. For instance, when running this code, the comment `Delete this post now or you better hide. I am coming after you and your family.` is identified as high risk because of its dangerous threat. Conversely, the comment `Stay away from the 5G cellphones!! They are using 5G to control you.` is categorized as medium risk.

### Deploy your prompt

Once you are confident in the quality of your solution, it's time to deploy it to production. Here are some best practices to follow when using content moderation in production:

1. **Provide clear feedback to users:** When user input is blocked or a response is flagged because of content moderation, provide informative and constructive feedback to help users understand why their message was flagged and how they can rephrase it appropriately. In the earlier coding examples, this is done through the `explanation` field in the Claude response.

2. **Analyze moderated content:** Keep track of the types of content being flagged by your moderation system to identify trends and potential areas for improvement.

3. **Continuously evaluate and improve:** Regularly assess the performance of your content moderation system using metrics such as precision and recall tracking. Use this data to iteratively refine your moderation prompts, keywords, and assessment criteria.

***


## Improve performance

Source: https://platform.claude.com/llms-full.txt#improve-performance

In complex scenarios, it may be helpful to consider additional strategies to improve performance beyond standard [prompt engineering techniques](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview). Here are some advanced strategies:

### Define topics and provide examples

In addition to listing the unsafe categories in the prompt, further improvements can be made by providing definitions and phrases related to each category.

<CodeGroup exclude="shell">
  ```python Python
  # Categories considered unsafe for content moderation, with their definitions
  unsafe_category_definitions = {
      "Child Exploitation": "Content that depicts child nudity or that enables, encourages, excuses, or depicts the sexual abuse of children.",
      "Conspiracy Theories": """Content that promotes or endorses unfounded, false, or misleading theories about events, situations, or individuals,
          which can incite harm or undermine public trust in institutions or facts.""",
      "Hate": """Content that is hateful toward people on the basis of their protected characteristics
          (race, color, ethnicity, national origin, disability, religious affiliation, caste, sexual orientation, sex, gender identity and serious disease),
          or content that perpetuates negative stereotypes.""",
      "Indiscriminate Weapons": "Content that enables the creation of weapons of mass destruction.",
      "Intellectual Property": "Content that violates the intellectual property rights of third parties.",
      "Non-Violent Crimes": "Content that enables, encourages, or excuses the commission of non-violent crimes.",
      "Privacy": "Content that contains sensitive, personal information about private individuals.",
      "Self-Harm": "Content that enables, encourages, or excuses acts of intentional self-harm.",
      "Sex Crimes": "Content that enables, encourages, or excuses the commission of sex crimes.",
      "Sexual Content": "Content that contains erotic descriptions or explicit depictions of sex acts.",
      "Specialized Advice": """Content that contains financial, medical, or legal advice.
          Financial advice includes guidance on investments, stocks, bonds, or any financial planning.""",
      "Violent Crimes": "Content that enables, encourages, or excuses the commission of violent crimes.",
  }


  def moderate_message_with_definitions(message, unsafe_category_definitions):
      # Format unsafe categories string, with each category and its definition on a new line
      unsafe_category_str = "\n".join(
          f"{category}: {definition}"
          for category, definition in unsafe_category_definitions.items()
      )

      # Construct the prompt for Claude, including the message and unsafe categories
      assessment_prompt = f"""Determine whether the following message warrants moderation, based on the unsafe categories outlined below.

  Message:
  <message>{message}</message>

  Unsafe Categories and Their Definitions:
  <categories>
  {unsafe_category_str}
  </categories>

  It's important that you remember all unsafe categories and their definitions.

  Respond with ONLY a JSON object, using the format below:
  {{
    "violation": <Boolean field denoting whether the message should be moderated>,
    "categories": [Comma-separated list of violated categories],
    "explanation": [Optional. Only include if there is a violation.]
  }}
  Do not include markdown formatting or code fences in your response."""

      # Send the request to Claude for content moderation
      response = client.messages.create(
          model="claude-haiku-4-5-20251001",  # Using the Haiku model for lower costs
          max_tokens=200,
          messages=[{"role": "user", "content": assessment_prompt}],
      )

      # Parse the JSON response from Claude
      text_block = next(block for block in response.content if block.type == "text")
      assessment = json.loads(text_block.text)

      # Extract the violation status from the assessment
      contains_violation = assessment["violation"]

      # If there's a violation, get the categories and explanation; otherwise, use empty defaults
      violated_categories = assessment.get("categories", []) if contains_violation else []
      explanation = assessment.get("explanation") if contains_violation else None

      return contains_violation, violated_categories, explanation


  # Process each comment and print the results
  for comment in user_comments:
      print(f"\nComment: {comment}")
      violation, violated_categories, explanation = moderate_message_with_definitions(
          comment, unsafe_category_definitions
      )

      if violation:
          print(f"Violated Categories: {', '.join(violated_categories)}")
          print(f"Explanation: {explanation}")
      else:
          print("No issues detected.")

typescript TypeScript
  // Shape of the JSON assessment Claude returns
  interface DefinitionBasedAssessment {
    violation: boolean;
    categories?: string[];
    explanation?: string;
  }

  // Categories considered unsafe for content moderation, with their definitions
  // (object keys preserve insertion order, so categories render in this order)
  const unsafeCategoryDefinitions: Record<string, string> = {
    "Child Exploitation":
      "Content that depicts child nudity or that enables, encourages, excuses, or depicts the sexual abuse of children.",
    "Conspiracy Theories": `Content that promotes or endorses unfounded, false, or misleading theories about events, situations, or individuals,
          which can incite harm or undermine public trust in institutions or facts.`,
    "Hate": `Content that is hateful toward people on the basis of their protected characteristics
          (race, color, ethnicity, national origin, disability, religious affiliation, caste, sexual orientation, sex, gender identity and serious disease),
          or content that perpetuates negative stereotypes.`,
    "Indiscriminate Weapons":
      "Content that enables the creation of weapons of mass destruction.",
    "Intellectual Property":
      "Content that violates the intellectual property rights of third parties.",
    "Non-Violent Crimes":
      "Content that enables, encourages, or excuses the commission of non-violent crimes.",
    "Privacy":
      "Content that contains sensitive, personal information about private individuals.",
    "Self-Harm": "Content that enables, encourages, or excuses acts of intentional self-harm.",
    "Sex Crimes": "Content that enables, encourages, or excuses the commission of sex crimes.",
    "Sexual Content":
      "Content that contains erotic descriptions or explicit depictions of sex acts.",
    "Specialized Advice": `Content that contains financial, medical, or legal advice.
          Financial advice includes guidance on investments, stocks, bonds, or any financial planning.`,
    "Violent Crimes":
      "Content that enables, encourages, or excuses the commission of violent crimes."
  };

  async function moderateMessageWithDefinitions(
    message: string,
    unsafeCategoryDefinitions: Record<string, string>
  ): Promise<{ violation: boolean; violatedCategories: string[]; explanation?: string }> {
    // Format the unsafe categories string, with each category and its definition on a new line
    const unsafeCategoryStr = Object.entries(unsafeCategoryDefinitions)
      .map(([category, definition]) => `${category}: ${definition}`)
      .join("\n");

    // Construct the prompt for Claude, including the message and unsafe categories
    const assessmentPrompt = `Determine whether the following message warrants moderation, based on the unsafe categories outlined below.

  Message:
  <message>${message}</message>

  Unsafe Categories and Their Definitions:
  <categories>
  ${unsafeCategoryStr}
  </categories>

  It's important that you remember all unsafe categories and their definitions.

  Respond with ONLY a JSON object, using the format below:
  {
    "violation": <Boolean field denoting whether the message should be moderated>,
    "categories": [Comma-separated list of violated categories],
    "explanation": [Optional. Only include if there is a violation.]
  }
  Do not include markdown formatting or code fences in your response.`;

    // Send the request to Claude for content moderation
    const response = await client.messages.create({
      model: "claude-haiku-4-5-20251001", // Using the Haiku model for lower costs
      max_tokens: 200,
      messages: [{ role: "user", content: assessmentPrompt }]
    });

    // Parse the JSON response from Claude
    const textBlock = response.content.find((block) => block.type === "text");
    if (!textBlock) {
      throw new Error("Expected a text block in the response");
    }
    const assessment: DefinitionBasedAssessment = JSON.parse(textBlock.text);

    // Extract the violation status from the assessment
    const containsViolation = assessment.violation;

    // If there's a violation, get the categories and explanation; otherwise, use empty defaults
    const violatedCategories = containsViolation ? assessment.categories ?? [] : [];
    const explanation = containsViolation ? assessment.explanation : undefined;

    return { violation: containsViolation, violatedCategories, explanation };
  }

  // Process each comment and print the results
  for (const comment of userComments) {
    console.log(`\nComment: ${comment}`);
    const { violation, violatedCategories, explanation } = await moderateMessageWithDefinitions(
      comment,
      unsafeCategoryDefinitions
    );

    if (violation) {
      console.log(`Violated Categories: ${violatedCategories.join(", ")}`);
      console.log(`Explanation: ${explanation}`);
    } else {
      console.log("No issues detected.");
    }
  }

csharp C#
  // Categories considered unsafe for content moderation, with their definitions.
  // The entries stay in insertion order, so the rendered prompt lists categories
  // in exactly this order.
  (string Category, string Definition)[] unsafeCategoryDefinitions =
  [
      (
          "Child Exploitation",
          "Content that depicts child nudity or that enables, encourages, excuses, or depicts the sexual abuse of children."
      ),
      (
          "Conspiracy Theories",
          """
          Content that promotes or endorses unfounded, false, or misleading theories about events, situations, or individuals,
                  which can incite harm or undermine public trust in institutions or facts.
          """
      ),
      (
          "Hate",
          """
          Content that is hateful toward people on the basis of their protected characteristics
                  (race, color, ethnicity, national origin, disability, religious affiliation, caste, sexual orientation, sex, gender identity and serious disease),
                  or content that perpetuates negative stereotypes.
          """
      ),
      ("Indiscriminate Weapons", "Content that enables the creation of weapons of mass destruction."),
      ("Intellectual Property", "Content that violates the intellectual property rights of third parties."),
      ("Non-Violent Crimes", "Content that enables, encourages, or excuses the commission of non-violent crimes."),
      ("Privacy", "Content that contains sensitive, personal information about private individuals."),
      ("Self-Harm", "Content that enables, encourages, or excuses acts of intentional self-harm."),
      ("Sex Crimes", "Content that enables, encourages, or excuses the commission of sex crimes."),
      ("Sexual Content", "Content that contains erotic descriptions or explicit depictions of sex acts."),
      (
          "Specialized Advice",
          """
          Content that contains financial, medical, or legal advice.
                  Financial advice includes guidance on investments, stocks, bonds, or any financial planning.
          """
      ),
      ("Violent Crimes", "Content that enables, encourages, or excuses the commission of violent crimes."),
  ];


  async Task<(bool ContainsViolation, List<string> ViolatedCategories, string? Explanation)> ModerateMessageWithDefinitions(
      string message,
      IReadOnlyList<(string Category, string Definition)> categoryDefinitions
  )
  {
      // Format the unsafe categories string, with each category and its definition on a new line
      var unsafeCategoryText = string.Join(
          "\n",
          categoryDefinitions.Select(entry => $"{entry.Category}: {entry.Definition}")
      );

      // Construct the prompt for Claude, including the message and unsafe categories
      var assessmentPrompt = $$"""
  Determine whether the following message warrants moderation, based on the unsafe categories outlined below.

  Message:
  <message>{{message}}</message>

  Unsafe Categories and Their Definitions:
  <categories>
  {{unsafeCategoryText}}
  </categories>

  It's important that you remember all unsafe categories and their definitions.

  Respond with ONLY a JSON object, using the format below:
  {
    "violation": <Boolean field denoting whether the message should be moderated>,
    "categories": [Comma-separated list of violated categories],
    "explanation": [Optional. Only include if there is a violation.]
  }
  Do not include markdown formatting or code fences in your response.
  """;

      // Send the request to Claude for content moderation
      var response = await client.Messages.Create(
          new()
          {
              Model = Model.ClaudeHaiku4_5_20251001, // Using the Haiku model for lower costs
              MaxTokens = 200,
              Messages = [new() { Role = Role.User, Content = assessmentPrompt }],
          }
      );

      // Narrow the first content block to a text block, then parse Claude's JSON response
      if (!response.Content[0].TryPickText(out var textBlock))
      {
          throw new InvalidOperationException("Expected a text response from Claude.");
      }
      var assessment = JsonNode.Parse(textBlock.Text)!;

      // Extract the violation status from the assessment
      var containsViolation = assessment["violation"]!.GetValue<bool>();

      // If there's a violation, get the categories and explanation; otherwise, use empty defaults
      List<string> violatedCategories = containsViolation
          ? assessment["categories"]?.AsArray().Select(category => category!.GetValue<string>()).ToList() ?? []
          : [];
      var explanation = containsViolation ? assessment["explanation"]?.GetValue<string>() : null;

      return (containsViolation, violatedCategories, explanation);
  }

  // Process each comment and print the results
  foreach (var comment in userComments)
  {
      Console.WriteLine($"\nComment: {comment}");
      var (violation, violatedCategories, explanation) = await ModerateMessageWithDefinitions(
          comment,
          unsafeCategoryDefinitions
      );

      if (violation)
      {
          Console.WriteLine($"Violated Categories: {string.Join(", ", violatedCategories)}");
          Console.WriteLine($"Explanation: {explanation}");
      }
      else
      {
          Console.WriteLine("No issues detected.");
      }
  }

go Go
  // Categories considered unsafe for content moderation, with their definitions.
  // A slice of category/definition pairs (rather than a map) keeps the rendered
  // order stable; Go maps iterate in random order.
  type categoryDefinition struct {
  	category   string
  	definition string
  }

  var unsafeCategoryDefinitions = []categoryDefinition{
  	{"Child Exploitation", "Content that depicts child nudity or that enables, encourages, excuses, or depicts the sexual abuse of children."},
  	{"Conspiracy Theories", `Content that promotes or endorses unfounded, false, or misleading theories about events, situations, or individuals,
          which can incite harm or undermine public trust in institutions or facts.`},
  	{"Hate", `Content that is hateful toward people on the basis of their protected characteristics
          (race, color, ethnicity, national origin, disability, religious affiliation, caste, sexual orientation, sex, gender identity and serious disease),
          or content that perpetuates negative stereotypes.`},
  	{"Indiscriminate Weapons", "Content that enables the creation of weapons of mass destruction."},
  	{"Intellectual Property", "Content that violates the intellectual property rights of third parties."},
  	{"Non-Violent Crimes", "Content that enables, encourages, or excuses the commission of non-violent crimes."},
  	{"Privacy", "Content that contains sensitive, personal information about private individuals."},
  	{"Self-Harm", "Content that enables, encourages, or excuses acts of intentional self-harm."},
  	{"Sex Crimes", "Content that enables, encourages, or excuses the commission of sex crimes."},
  	{"Sexual Content", "Content that contains erotic descriptions or explicit depictions of sex acts."},
  	{"Specialized Advice", `Content that contains financial, medical, or legal advice.
          Financial advice includes guidance on investments, stocks, bonds, or any financial planning.`},
  	{"Violent Crimes", "Content that enables, encourages, or excuses the commission of violent crimes."},
  }

  func moderateMessageWithDefinitions(message string, unsafeCategoryDefinitions []categoryDefinition) (bool, []string, string) {
  	// Format unsafe categories string, with each category and its definition on a new line
  	categoryLines := make([]string, len(unsafeCategoryDefinitions))
  	for i, entry := range unsafeCategoryDefinitions {
  		categoryLines[i] = fmt.Sprintf("%s: %s", entry.category, entry.definition)
  	}
  	unsafeCategoryStr := strings.Join(categoryLines, "\n")

  	// Construct the prompt for Claude, including the message and unsafe categories
  	assessmentPrompt := fmt.Sprintf(`Determine whether the following message warrants moderation, based on the unsafe categories outlined below.

  Message:
  <message>%s</message>

  Unsafe Categories and Their Definitions:
  <categories>
  %s
  </categories>

  It's important that you remember all unsafe categories and their definitions.

  Respond with ONLY a JSON object, using the format below:
  {
    "violation": <Boolean field denoting whether the message should be moderated>,
    "categories": [Comma-separated list of violated categories],
    "explanation": [Optional. Only include if there is a violation.]
  }
  Do not include markdown formatting or code fences in your response.`, message, unsafeCategoryStr)

  	// Send the request to Claude for content moderation
  	response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeHaiku4_5_20251001, // Using the Haiku model for lower costs
  		MaxTokens: 200,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock(assessmentPrompt)),
  		},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	// Narrow the first content block to a text block before reading its text
  	textBlock, ok := response.Content[0].AsAny().(anthropic.TextBlock)
  	if !ok {
  		log.Fatalf("expected a text block, got %q", response.Content[0].Type)
  	}

  	// Parse the JSON response from Claude
  	var assessment struct {
  		Violation   bool     `json:"violation"`
  		Categories  []string `json:"categories"`
  		Explanation string   `json:"explanation"`
  	}
  	if err := json.Unmarshal([]byte(textBlock.Text), &assessment); err != nil {
  		log.Fatal(err)
  	}

  	// If there's a violation, return the categories and explanation; otherwise, use empty defaults
  	if !assessment.Violation {
  		return false, nil, ""
  	}
  	return true, assessment.Categories, assessment.Explanation
  }

  // moderateAllCommentsWithDefinitions processes each comment and prints the results.
  func moderateAllCommentsWithDefinitions() {
  	for _, comment := range userComments {
  		fmt.Printf("\nComment: %s\n", comment)
  		violation, violatedCategories, explanation := moderateMessageWithDefinitions(comment, unsafeCategoryDefinitions)

  		if violation {
  			fmt.Printf("Violated Categories: %s\n", strings.Join(violatedCategories, ", "))
  			fmt.Printf("Explanation: %s\n", explanation)
  		} else {
  			fmt.Println("No issues detected.")
  		}
  	}
  }

java Java
  // Categories considered unsafe for content moderation, with their definitions
  record CategoryDefinition(String category, String definition) {}

  final List<CategoryDefinition> unsafeCategoryDefinitions = List.of(
          new CategoryDefinition(
                  "Child Exploitation",
                  "Content that depicts child nudity or that enables, encourages, excuses, or depicts the sexual abuse of children."),
          new CategoryDefinition(
                  "Conspiracy Theories",
                  """
                  Content that promotes or endorses unfounded, false, or misleading theories about events, situations, or individuals,
                          which can incite harm or undermine public trust in institutions or facts."""),
          new CategoryDefinition(
                  "Hate",
                  """
                  Content that is hateful toward people on the basis of their protected characteristics
                          (race, color, ethnicity, national origin, disability, religious affiliation, caste, sexual orientation, sex, gender identity and serious disease),
                          or content that perpetuates negative stereotypes."""),
          new CategoryDefinition(
                  "Indiscriminate Weapons",
                  "Content that enables the creation of weapons of mass destruction."),
          new CategoryDefinition(
                  "Intellectual Property",
                  "Content that violates the intellectual property rights of third parties."),
          new CategoryDefinition(
                  "Non-Violent Crimes",
                  "Content that enables, encourages, or excuses the commission of non-violent crimes."),
          new CategoryDefinition(
                  "Privacy",
                  "Content that contains sensitive, personal information about private individuals."),
          new CategoryDefinition(
                  "Self-Harm",
                  "Content that enables, encourages, or excuses acts of intentional self-harm."),
          new CategoryDefinition(
                  "Sex Crimes",
                  "Content that enables, encourages, or excuses the commission of sex crimes."),
          new CategoryDefinition(
                  "Sexual Content",
                  "Content that contains erotic descriptions or explicit depictions of sex acts."),
          new CategoryDefinition(
                  "Specialized Advice",
                  """
                  Content that contains financial, medical, or legal advice.
                          Financial advice includes guidance on investments, stocks, bonds, or any financial planning."""),
          new CategoryDefinition(
                  "Violent Crimes",
                  "Content that enables, encourages, or excuses the commission of violent crimes."));

  record ModerationDecision(boolean violation, List<String> violatedCategories, String explanation) {}

  ModerationDecision moderateMessageWithDefinitions(
          String message, List<CategoryDefinition> unsafeCategoryDefinitions)
          throws JsonProcessingException {
      // Format unsafe categories string, with each category and its definition on a new line
      String unsafeCategoryStr = unsafeCategoryDefinitions.stream()
              .map(categoryDefinition ->
                      categoryDefinition.category() + ": " + categoryDefinition.definition())
              .collect(Collectors.joining("\n"));

      // Construct the prompt for Claude, including the message and unsafe categories
      String assessmentPrompt = """
          Determine whether the following message warrants moderation, based on the unsafe categories outlined below.

          Message:
          <message>%s</message>

          Unsafe Categories and Their Definitions:
          <categories>
          %s
          </categories>

          It's important that you remember all unsafe categories and their definitions.

          Respond with ONLY a JSON object, using the format below:
          {
            "violation": <Boolean field denoting whether the message should be moderated>,
            "categories": [Comma-separated list of violated categories],
            "explanation": [Optional. Only include if there is a violation.]
          }
          Do not include markdown formatting or code fences in your response."""
              .formatted(message, unsafeCategoryStr);

      // Send the request to Claude for content moderation
      Message response = client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_HAIKU_4_5_20251001) // Using the Haiku model for lower costs
              .maxTokens(200)
              .addUserMessage(assessmentPrompt)
              .build());

      // Parse the JSON response from Claude
      String assessmentJson = response.content().stream()
              .flatMap(contentBlock -> contentBlock.text().stream())
              .findFirst()
              .orElseThrow()
              .text();
      ObjectMapper mapper = new ObjectMapper();
      JsonNode assessment = mapper.readTree(assessmentJson);

      // Extract the violation status from the assessment
      boolean containsViolation = assessment.required("violation").asBoolean();

      // If there's a violation, get the categories and explanation; otherwise, use empty defaults
      List<String> violatedCategories = containsViolation && assessment.has("categories")
              ? mapper.convertValue(assessment.get("categories"), new TypeReference<List<String>>() {})
              : List.of();
      String explanation = containsViolation && assessment.hasNonNull("explanation")
              ? assessment.get("explanation").asText()
              : null;

      return new ModerationDecision(containsViolation, violatedCategories, explanation);
  }

  // Process each comment and print the results
  void printModerationResultsWithDefinitions() throws JsonProcessingException {
      for (String comment : userComments) {
          IO.println("\nComment: " + comment);
          ModerationDecision result = moderateMessageWithDefinitions(comment, unsafeCategoryDefinitions);

          if (result.violation()) {
              IO.println("Violated Categories: " + String.join(", ", result.violatedCategories()));
              IO.println("Explanation: " + result.explanation());
          } else {
              IO.println("No issues detected.");
          }
      }
  }

php PHP
  // Categories considered unsafe for content moderation, with their definitions
  $unsafeCategoryDefinitions = [
      'Child Exploitation' => 'Content that depicts child nudity or that enables, encourages, excuses, or depicts the sexual abuse of children.',
      'Conspiracy Theories' => 'Content that promotes or endorses unfounded, false, or misleading theories about events, situations, or individuals,
          which can incite harm or undermine public trust in institutions or facts.',
      'Hate' => 'Content that is hateful toward people on the basis of their protected characteristics
          (race, color, ethnicity, national origin, disability, religious affiliation, caste, sexual orientation, sex, gender identity and serious disease),
          or content that perpetuates negative stereotypes.',
      'Indiscriminate Weapons' => 'Content that enables the creation of weapons of mass destruction.',
      'Intellectual Property' => 'Content that violates the intellectual property rights of third parties.',
      'Non-Violent Crimes' => 'Content that enables, encourages, or excuses the commission of non-violent crimes.',
      'Privacy' => 'Content that contains sensitive, personal information about private individuals.',
      'Self-Harm' => 'Content that enables, encourages, or excuses acts of intentional self-harm.',
      'Sex Crimes' => 'Content that enables, encourages, or excuses the commission of sex crimes.',
      'Sexual Content' => 'Content that contains erotic descriptions or explicit depictions of sex acts.',
      'Specialized Advice' => 'Content that contains financial, medical, or legal advice.
          Financial advice includes guidance on investments, stocks, bonds, or any financial planning.',
      'Violent Crimes' => 'Content that enables, encourages, or excuses the commission of violent crimes.',
  ];

  $moderateMessageWithDefinitions = function (string $message, array $unsafeCategoryDefinitions) use ($client): array {
      // Format the unsafe categories string, with each category and its definition on a new line
      $categoryLines = [];
      foreach ($unsafeCategoryDefinitions as $category => $definition) {
          $categoryLines[] = "{$category}: {$definition}";
      }
      $unsafeCategoryStr = implode("\n", $categoryLines);

      // Construct the prompt for Claude, including the message and unsafe categories
      $assessmentPrompt = <<<PROMPT
      Determine whether the following message warrants moderation, based on the unsafe categories outlined below.

      Message:
      <message>{$message}</message>

      Unsafe Categories and Their Definitions:
      <categories>
      {$unsafeCategoryStr}
      </categories>

      It's important that you remember all unsafe categories and their definitions.

      Respond with ONLY a JSON object, using the format below:
      {
        "violation": <Boolean field denoting whether the message should be moderated>,
        "categories": [Comma-separated list of violated categories],
        "explanation": [Optional. Only include if there is a violation.]
      }
      Do not include markdown formatting or code fences in your response.
      PROMPT;

      // Send the request to Claude for content moderation
      $response = $client->messages->create(
          model: 'claude-haiku-4-5-20251001', // Using the Haiku model for lower costs
          maxTokens: 200,
          messages: [['role' => 'user', 'content' => $assessmentPrompt]],
      );

      // Parse the JSON response from Claude. The SDK decodes each content block
      // into its concrete class, so find the TextBlock before reading the text.
      $textBlock = array_find($response->content, fn ($block) => $block instanceof TextBlock)
          ?? throw new RuntimeException('Expected a text block in the response.');
      $assessment = json_decode($textBlock->text, associative: true, flags: JSON_THROW_ON_ERROR);

      // Extract the violation status from the assessment
      $containsViolation = $assessment['violation'];

      // If there's a violation, get the categories and explanation; otherwise, use empty defaults
      $violatedCategories = $containsViolation ? ($assessment['categories'] ?? []) : [];
      $explanation = $containsViolation ? ($assessment['explanation'] ?? null) : null;

      return [$containsViolation, $violatedCategories, $explanation];
  };

  // Process each comment and print the results
  foreach ($userComments as $comment) {
      echo "\nComment: {$comment}\n";
      [$violation, $violatedCategories, $explanation] = $moderateMessageWithDefinitions($comment, $unsafeCategoryDefinitions);

      if ($violation) {
          echo 'Violated Categories: ' . implode(', ', $violatedCategories) . "\n";
          echo "Explanation: {$explanation}\n";
      } else {
          echo "No issues detected.\n";
      }
  }

ruby Ruby
  # Categories considered unsafe for content moderation, with their definitions
  UNSAFE_CATEGORY_DEFINITIONS = {
    "Child Exploitation" => "Content that depicts child nudity or that enables, encourages, excuses, or depicts the sexual abuse of children.",
    "Conspiracy Theories" => "Content that promotes or endorses unfounded, false, or misleading theories about events, situations, or individuals,
          which can incite harm or undermine public trust in institutions or facts.",
    "Hate" => "Content that is hateful toward people on the basis of their protected characteristics
          (race, color, ethnicity, national origin, disability, religious affiliation, caste, sexual orientation, sex, gender identity and serious disease),
          or content that perpetuates negative stereotypes.",
    "Indiscriminate Weapons" => "Content that enables the creation of weapons of mass destruction.",
    "Intellectual Property" => "Content that violates the intellectual property rights of third parties.",
    "Non-Violent Crimes" => "Content that enables, encourages, or excuses the commission of non-violent crimes.",
    "Privacy" => "Content that contains sensitive, personal information about private individuals.",
    "Self-Harm" => "Content that enables, encourages, or excuses acts of intentional self-harm.",
    "Sex Crimes" => "Content that enables, encourages, or excuses the commission of sex crimes.",
    "Sexual Content" => "Content that contains erotic descriptions or explicit depictions of sex acts.",
    "Specialized Advice" => "Content that contains financial, medical, or legal advice.
          Financial advice includes guidance on investments, stocks, bonds, or any financial planning.",
    "Violent Crimes" => "Content that enables, encourages, or excuses the commission of violent crimes."
  }


  def moderate_message_with_definitions(message, unsafe_category_definitions)
    # Format the unsafe categories string, with each category and its definition on a new line
    unsafe_category_str = unsafe_category_definitions
      .map { |category, definition| "#{category}: #{definition}" }
      .join("\n")

    # Construct the prompt for Claude, including the message and unsafe categories
    assessment_prompt = <<~PROMPT.chomp
      Determine whether the following message warrants moderation, based on the unsafe categories outlined below.

      Message:
      <message>#{message}</message>

      Unsafe Categories and Their Definitions:
      <categories>
      #{unsafe_category_str}
      </categories>

      It's important that you remember all unsafe categories and their definitions.

      Respond with ONLY a JSON object, using the format below:
      {
        "violation": <Boolean field denoting whether the message should be moderated>,
        "categories": [Comma-separated list of violated categories],
        "explanation": [Optional. Only include if there is a violation.]
      }
      Do not include markdown formatting or code fences in your response.
    PROMPT

    # Send the request to Claude for content moderation
    response = CLIENT.messages.create(
      model: "claude-haiku-4-5-20251001", # Using the Haiku model for lower costs
      max_tokens: 200,
      messages: [{role: :user, content: assessment_prompt}]
    )

    # Parse the JSON response from Claude
    text_block = response.content.find { it.type == :text }
    assessment = JSON.parse(text_block.text)

    # Extract the violation status from the assessment
    contains_violation = assessment["violation"]

    # If there's a violation, get the categories and explanation; otherwise, use empty defaults
    violated_categories = contains_violation ? assessment.fetch("categories", []) : []
    explanation = contains_violation ? assessment["explanation"] : nil

    [contains_violation, violated_categories, explanation]
  end


  # Process each comment and print the results
  USER_COMMENTS.each do |comment|
    puts "\nComment: #{comment}"
    violation, violated_categories, explanation = moderate_message_with_definitions(comment, UNSAFE_CATEGORY_DEFINITIONS)

    if violation
      puts "Violated Categories: #{violated_categories.join(", ")}"
      puts "Explanation: #{explanation}"
    else
      puts "No issues detected."
    end
  end

python Python
  def batch_moderate_messages(messages, unsafe_categories):
      # Convert the unsafe categories into a string, with each category on a new line
      unsafe_category_str = "\n".join(unsafe_categories)

      # Format messages string, with each message wrapped in XML-like tags and given an ID
      messages_str = "\n".join(
          [f"<message id={idx}>{msg}</message>" for idx, msg in enumerate(messages)]
      )

      # Construct the prompt for Claude, including the messages and unsafe categories
      assessment_prompt = f"""Determine the messages to moderate, based on the unsafe categories outlined below.

  Messages:
  <messages>
  {messages_str}
  </messages>

  Unsafe Categories:
  <categories>
  {unsafe_category_str}
  </categories>

  Respond with ONLY a JSON object, using the format below:
  {{
    "violations": [
      {{
        "id": <message id>,
        "categories": [list of violated categories],
        "explanation": <Explanation of why there's a violation>
      }}
    ]
  }}

  Important Notes:
  - Remember to analyze every message for a violation.
  - Select any number of violations that reasonably apply.
  - Do not include markdown formatting or code fences in your response."""

      # Send the request to Claude for content moderation
      response = client.messages.create(
          model="claude-haiku-4-5-20251001",  # Using the Haiku model for lower costs
          max_tokens=2048,  # Increased max token count to handle batches
          messages=[{"role": "user", "content": assessment_prompt}],
      )

      # Parse the JSON response from Claude
      text_block = next(block for block in response.content if block.type == "text")
      assessment = json.loads(text_block.text)
      return assessment


  # Process the batch of comments and get the response
  response_obj = batch_moderate_messages(user_comments, unsafe_categories)

  # Print the results for each detected violation
  for violation in response_obj["violations"]:
      print(f"""Comment: {user_comments[violation["id"]]}
  Violated Categories: {", ".join(violation["categories"])}
  Explanation: {violation["explanation"]}
  """)

typescript TypeScript
  // Shape of the JSON batch assessment Claude returns
  interface BatchAssessment {
    violations: {
      id: number;
      categories: string[];
      explanation: string;
    }[];
  }

  async function batchModerateMessages(
    messages: string[],
    unsafeCategories: string[]
  ): Promise<BatchAssessment> {
    // Convert the unsafe categories into a string, with each category on a new line
    const unsafeCategoryStr = unsafeCategories.join("\n");

    // Format the messages string, with each message wrapped in XML-like tags and given an ID
    const messagesStr = messages
      .map((msg, idx) => `<message id=${idx}>${msg}</message>`)
      .join("\n");

    // Construct the prompt for Claude, including the messages and unsafe categories
    const assessmentPrompt = `Determine the messages to moderate, based on the unsafe categories outlined below.

  Messages:
  <messages>
  ${messagesStr}
  </messages>

  Unsafe Categories:
  <categories>
  ${unsafeCategoryStr}
  </categories>

  Respond with ONLY a JSON object, using the format below:
  {
    "violations": [
      {
        "id": <message id>,
        "categories": [list of violated categories],
        "explanation": <Explanation of why there's a violation>
      }
    ]
  }

  Important Notes:
  - Remember to analyze every message for a violation.
  - Select any number of violations that reasonably apply.
  - Do not include markdown formatting or code fences in your response.`;

    // Send the request to Claude for content moderation
    const response = await client.messages.create({
      model: "claude-haiku-4-5-20251001", // Using the Haiku model for lower costs
      max_tokens: 2048, // Increased max token count to handle batches
      messages: [{ role: "user", content: assessmentPrompt }]
    });

    // Parse the JSON response from Claude
    const textBlock = response.content.find((block) => block.type === "text");
    if (!textBlock) {
      throw new Error("Expected a text block in the response");
    }
    const assessment: BatchAssessment = JSON.parse(textBlock.text);
    return assessment;
  }

  // Process the batch of comments and get the response
  const batchAssessment = await batchModerateMessages(userComments, unsafeCategories);

  // Print the results for each detected violation
  for (const violation of batchAssessment.violations) {
    console.log(`Comment: ${userComments[violation.id]}
  Violated Categories: ${violation.categories.join(", ")}
  Explanation: ${violation.explanation}
  `);
  }

csharp C#
  async Task<JsonNode> BatchModerateMessages(IReadOnlyList<string> messages, IReadOnlyList<string> categories)
  {
      // Convert the unsafe categories into a string, with each category on a new line
      var unsafeCategoryText = string.Join("\n", categories);

      // Format the messages string, with each message wrapped in XML-like tags and given an ID
      var messagesText = string.Join(
          "\n",
          messages.Select((message, index) => $"<message id={index}>{message}</message>")
      );

      // Construct the prompt for Claude, including the messages and unsafe categories
      var assessmentPrompt = $$"""
  Determine the messages to moderate, based on the unsafe categories outlined below.

  Messages:
  <messages>
  {{messagesText}}
  </messages>

  Unsafe Categories:
  <categories>
  {{unsafeCategoryText}}
  </categories>

  Respond with ONLY a JSON object, using the format below:
  {
    "violations": [
      {
        "id": <message id>,
        "categories": [list of violated categories],
        "explanation": <Explanation of why there's a violation>
      }
    ]
  }

  Important Notes:
  - Remember to analyze every message for a violation.
  - Select any number of violations that reasonably apply.
  - Do not include markdown formatting or code fences in your response.
  """;

      // Send the request to Claude for content moderation
      var response = await client.Messages.Create(
          new()
          {
              Model = Model.ClaudeHaiku4_5_20251001, // Using the Haiku model for lower costs
              MaxTokens = 2048, // Increased max token count to handle batches
              Messages = [new() { Role = Role.User, Content = assessmentPrompt }],
          }
      );

      // Narrow the first content block to a text block, then parse Claude's JSON response
      if (!response.Content[0].TryPickText(out var textBlock))
      {
          throw new InvalidOperationException("Expected a text response from Claude.");
      }
      return JsonNode.Parse(textBlock.Text)!;
  }

  // Process the batch of comments and get the response
  var moderationResults = await BatchModerateMessages(userComments, unsafeCategories);

  // Print the results for each detected violation
  foreach (var violation in moderationResults["violations"]!.AsArray())
  {
      var flaggedComment = userComments[violation!["id"]!.GetValue<int>()];
      var violatedCategories = string.Join(
          ", ",
          violation["categories"]!.AsArray().Select(category => category!.GetValue<string>())
      );
      var explanation = violation["explanation"]!.GetValue<string>();

      Console.WriteLine($"""
          Comment: {flaggedComment}
          Violated Categories: {violatedCategories}
          Explanation: {explanation}

          """);
  }

go Go
  // batchViolation is one entry in Claude's "violations" array: the index of the
  // offending message plus the categories it violated and why.
  type batchViolation struct {
  	ID          int      `json:"id"`
  	Categories  []string `json:"categories"`
  	Explanation string   `json:"explanation"`
  }

  func batchModerateMessages(messages []string, unsafeCategories []string) []batchViolation {
  	// Convert the unsafe categories into a string, with each category on a new line
  	unsafeCategoryStr := strings.Join(unsafeCategories, "\n")

  	// Format messages string, with each message wrapped in XML-like tags and given an ID
  	messageLines := make([]string, len(messages))
  	for i, message := range messages {
  		messageLines[i] = fmt.Sprintf("<message id=%d>%s</message>", i, message)
  	}
  	messagesStr := strings.Join(messageLines, "\n")

  	// Construct the prompt for Claude, including the messages and unsafe categories
  	assessmentPrompt := fmt.Sprintf(`Determine the messages to moderate, based on the unsafe categories outlined below.

  Messages:
  <messages>
  %s
  </messages>

  Unsafe Categories:
  <categories>
  %s
  </categories>

  Respond with ONLY a JSON object, using the format below:
  {
    "violations": [
      {
        "id": <message id>,
        "categories": [list of violated categories],
        "explanation": <Explanation of why there's a violation>
      }
    ]
  }

  Important Notes:
  - Remember to analyze every message for a violation.
  - Select any number of violations that reasonably apply.
  - Do not include markdown formatting or code fences in your response.`, messagesStr, unsafeCategoryStr)

  	// Send the request to Claude for content moderation
  	response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeHaiku4_5_20251001, // Using the Haiku model for lower costs
  		MaxTokens: 2048,                                   // Increased max token count to handle batches
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock(assessmentPrompt)),
  		},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	// Narrow the first content block to a text block before reading its text
  	textBlock, ok := response.Content[0].AsAny().(anthropic.TextBlock)
  	if !ok {
  		log.Fatalf("expected a text block, got %q", response.Content[0].Type)
  	}

  	// Parse the JSON response from Claude
  	var assessment struct {
  		Violations []batchViolation `json:"violations"`
  	}
  	if err := json.Unmarshal([]byte(textBlock.Text), &assessment); err != nil {
  		log.Fatal(err)
  	}
  	return assessment.Violations
  }

  // moderateAllCommentsAsBatch moderates the whole batch of comments in a single
  // request and prints the results for each detected violation.
  func moderateAllCommentsAsBatch() {
  	// Process the batch of comments and get the response
  	violations := batchModerateMessages(userComments, unsafeCategories)

  	// Print the results for each detected violation
  	for _, violation := range violations {
  		fmt.Printf(`Comment: %s
  Violated Categories: %s
  Explanation: %s

  `, userComments[violation.ID], strings.Join(violation.Categories, ", "), violation.Explanation)
  	}
  }

java Java
  JsonNode batchModerateMessages(List<String> messages, List<String> unsafeCategories)
          throws JsonProcessingException {
      // Convert the unsafe categories into a string, with each category on a new line
      String unsafeCategoryStr = String.join("\n", unsafeCategories);

      // Format messages string, with each message wrapped in XML-like tags and given an ID
      String messagesStr = IntStream.range(0, messages.size())
              .mapToObj(idx -> "<message id=%d>%s</message>".formatted(idx, messages.get(idx)))
              .collect(Collectors.joining("\n"));

      // Construct the prompt for Claude, including the messages and unsafe categories
      String assessmentPrompt = """
          Determine the messages to moderate, based on the unsafe categories outlined below.

          Messages:
          <messages>
          %s
          </messages>

          Unsafe Categories:
          <categories>
          %s
          </categories>

          Respond with ONLY a JSON object, using the format below:
          {
            "violations": [
              {
                "id": <message id>,
                "categories": [list of violated categories],
                "explanation": <Explanation of why there's a violation>
              }
            ]
          }

          Important Notes:
          - Remember to analyze every message for a violation.
          - Select any number of violations that reasonably apply.
          - Do not include markdown formatting or code fences in your response."""
              .formatted(messagesStr, unsafeCategoryStr);

      // Send the request to Claude for content moderation
      Message response = client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_HAIKU_4_5_20251001) // Using the Haiku model for lower costs
              .maxTokens(2048) // Increased max token count to handle batches
              .addUserMessage(assessmentPrompt)
              .build());

      // Parse the JSON response from Claude
      String assessmentJson = response.content().stream()
              .flatMap(contentBlock -> contentBlock.text().stream())
              .findFirst()
              .orElseThrow()
              .text();
      return new ObjectMapper().readTree(assessmentJson);
  }

  // Process the batch of comments and print the results for each detected violation
  void printBatchViolations() throws JsonProcessingException {
      JsonNode response = batchModerateMessages(userComments, unsafeCategories);

      ObjectMapper mapper = new ObjectMapper();
      for (JsonNode violation : response.required("violations")) {
          List<String> violatedCategories =
                  mapper.convertValue(violation.required("categories"), new TypeReference<List<String>>() {});
          IO.println("""
                  Comment: %s
                  Violated Categories: %s
                  Explanation: %s
                  """.formatted(
                          userComments.get(violation.required("id").asInt()),
                          String.join(", ", violatedCategories),
                          violation.required("explanation").asText()));
      }
  }

php PHP
  $batchModerateMessages = function (array $messages, array $unsafeCategories) use ($client): array {
      // Convert the unsafe categories into a string, with each category on a new line
      $unsafeCategoryStr = implode("\n", $unsafeCategories);

      // Format the messages string, with each message wrapped in XML-like tags and given an ID
      $messageLines = [];
      foreach ($messages as $idx => $msg) {
          $messageLines[] = "<message id={$idx}>{$msg}</message>";
      }
      $messagesStr = implode("\n", $messageLines);

      // Construct the prompt for Claude, including the messages and unsafe categories
      $assessmentPrompt = <<<PROMPT
      Determine the messages to moderate, based on the unsafe categories outlined below.

      Messages:
      <messages>
      {$messagesStr}
      </messages>

      Unsafe Categories:
      <categories>
      {$unsafeCategoryStr}
      </categories>

      Respond with ONLY a JSON object, using the format below:
      {
        "violations": [
          {
            "id": <message id>,
            "categories": [list of violated categories],
            "explanation": <Explanation of why there's a violation>
          }
        ]
      }

      Important Notes:
      - Remember to analyze every message for a violation.
      - Select any number of violations that reasonably apply.
      - Do not include markdown formatting or code fences in your response.
      PROMPT;

      // Send the request to Claude for content moderation
      $response = $client->messages->create(
          model: 'claude-haiku-4-5-20251001', // Using the Haiku model for lower costs
          maxTokens: 2048, // Increased max token count to handle batches
          messages: [['role' => 'user', 'content' => $assessmentPrompt]],
      );

      // Parse the JSON response from Claude. The SDK decodes each content block
      // into its concrete class, so find the TextBlock before reading the text.
      $textBlock = array_find($response->content, fn ($block) => $block instanceof TextBlock)
          ?? throw new RuntimeException('Expected a text block in the response.');

      return json_decode($textBlock->text, associative: true, flags: JSON_THROW_ON_ERROR);
  };

  // Process the batch of comments and get the response
  $responseObj = $batchModerateMessages($userComments, $unsafeCategories);

  // Print the results for each detected violation
  foreach ($responseObj['violations'] as $violation) {
      echo "Comment: {$userComments[$violation['id']]}\n";
      echo 'Violated Categories: ' . implode(', ', $violation['categories']) . "\n";
      echo "Explanation: {$violation['explanation']}\n\n";
  }

ruby Ruby
  def batch_moderate_messages(messages, unsafe_categories)
    # Convert the unsafe categories into a string, with each category on a new line
    unsafe_category_str = unsafe_categories.join("\n")

    # Format the messages string, with each message wrapped in XML-like tags and given an ID
    messages_str = messages
      .map.with_index { |message, index| "<message id=#{index}>#{message}</message>" }
      .join("\n")

    # Construct the prompt for Claude, including the messages and unsafe categories
    assessment_prompt = <<~PROMPT.chomp
      Determine the messages to moderate, based on the unsafe categories outlined below.

      Messages:
      <messages>
      #{messages_str}
      </messages>

      Unsafe Categories:
      <categories>
      #{unsafe_category_str}
      </categories>

      Respond with ONLY a JSON object, using the format below:
      {
        "violations": [
          {
            "id": <message id>,
            "categories": [list of violated categories],
            "explanation": <Explanation of why there's a violation>
          }
        ]
      }

      Important Notes:
      - Remember to analyze every message for a violation.
      - Select any number of violations that reasonably apply.
      - Do not include markdown formatting or code fences in your response.
    PROMPT

    # Send the request to Claude for content moderation
    response = CLIENT.messages.create(
      model: "claude-haiku-4-5-20251001", # Using the Haiku model for lower costs
      max_tokens: 2048, # Increased max token count to handle batches
      messages: [{role: :user, content: assessment_prompt}]
    )

    # Parse the JSON response from Claude
    text_block = response.content.find { it.type == :text }
    JSON.parse(text_block.text)
  end


  # Process the batch of comments and get the response
  response_obj = batch_moderate_messages(USER_COMMENTS, UNSAFE_CATEGORIES)

  # Print the results for each detected violation
  response_obj["violations"].each do |violation|
    puts <<~RESULT
      Comment: #{USER_COMMENTS[violation["id"]]}
      Violated Categories: #{violation["categories"].join(", ")}
      Explanation: #{violation["explanation"]}

    RESULT
  end
  ```
</CodeGroup>

In this example, the `batch_moderate_messages` function handles the moderation of an entire batch of messages with a single Claude API call. Inside the function, a prompt is created that includes the list of messages to evaluate and the unsafe content categories. The prompt directs Claude to return a JSON object listing all messages that contain violations. Each message in the response is identified by its `id`, which corresponds to the message's position in the batch. Keep in mind that finding the optimal batch size for your specific needs may require some experimentation. While larger batch sizes can lower costs, they might also lead to a slight decrease in quality. Additionally, you may need to increase the `max_tokens` parameter in the Claude API call to accommodate longer responses. For details on the maximum number of tokens your chosen model can output, refer to the [model comparison table](https://platform.claude.com/docs/en/models/overview#latest-models-comparison).

<CardGroup cols={2}>
  <Card title="Content moderation cookbook" icon="link" href="https://platform.claude.com/cookbook/misc-building-moderation-filter">
    View a fully implemented code-based example of how to use Claude for content moderation.
  </Card>

  <Card title="Mitigate jailbreaks" icon="link" href="https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks">
    Explore guardrail techniques to moderate interactions with Claude.
  </Card>
</CardGroup>


---
title: Customer support agent
url: https://platform.claude.com/docs/en/about-claude/use-case-guides/customer-support-chat
description: Build a customer support chatbot with Claude that answers product questions, stays on topic, and generates quotes through tool use.
---


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-22

To follow this guide, you need:

* A Claude API key (set as the `ANTHROPIC_API_KEY` environment variable)
* Python 3.10 or later

Install the required packages:


## Before building with Claude

Source: https://platform.claude.com/llms-full.txt#before-building-with-claude-2

### Decide whether to use Claude for support chat

Here are some key indicators that you should employ an LLM like Claude to automate portions of your customer support process:

<AccordionGroup>
  <Accordion title="High volume of repetitive queries">
    Claude excels at handling a large number of similar questions efficiently, freeing up human agents for more complex issues.
  </Accordion>

  <Accordion title="Need for quick information synthesis">
    Claude can quickly retrieve, process, and combine information from vast knowledge bases, while human agents may need time to research or consult multiple sources.
  </Accordion>

  <Accordion title="24/7 availability requirement">
    Claude can provide round-the-clock support without fatigue, whereas staffing human agents for continuous coverage can be costly and challenging.
  </Accordion>

  <Accordion title="Rapid scaling during peak periods">
    Claude can handle sudden increases in query volume without the need for hiring and training additional staff.
  </Accordion>

  <Accordion title="Consistent brand voice">
    You can instruct Claude to consistently represent your brand's tone and values, whereas human agents may vary in their communication styles.
  </Accordion>
</AccordionGroup>

Some considerations for choosing Claude over other LLMs:

* You prioritize natural, nuanced conversation: Claude's sophisticated language understanding allows for more natural, context-aware conversations that feel more human-like than chats with other LLMs.
* You often receive complex and open-ended queries: Claude can handle a wide range of topics and inquiries without generating canned responses or requiring extensive programming of permutations of user utterances.
* You need scalable multilingual support: Claude's multilingual capabilities allow it to engage in conversations in over 200 languages without the need for separate chatbots or extensive translation processes for each supported language.

### Define your ideal chat interaction

Outline an ideal customer interaction to define how and when you expect the customer to interact with Claude. This outline will help to determine the technical requirements of your solution.

Here is an example chat interaction for car insurance customer support:

* **Customer:** Initiates support chat experience
  * **Claude:** Warmly greets customer and initiates conversation

* **Customer:** Asks about insurance for their new electric car
  * **Claude:** Provides relevant information about electric vehicle coverage

* **Customer:** Asks questions related to unique needs for electric vehicle insurances
  * **Claude:** Responds with accurate and informative answers and provides links to the sources

* **Customer:** Asks off-topic questions unrelated to insurance or cars
  * **Claude:** Clarifies it does not discuss unrelated topics and steers the user back to car insurance

* **Customer:** Expresses interest in an insurance quote

  * **Claude:** Ask a set of questions to determine the appropriate quote, adapting to their responses
  * **Claude:** Sends a request to use the quote generation API tool along with necessary information collected from the user
  * **Claude:** Receives the response information from the API tool use, synthesizes the information into a natural response, and presents the provided quote to the user

* **Customer:** Asks follow up questions

  * **Claude:** Answers follow up questions as needed
  * **Claude:** Guides the customer to the next steps in the insurance process and closes out the conversation

<Tip>
  In the real example that you write for your own use case, you might find it useful to write out the actual words in this interaction so that you can also get a sense of the ideal tone, response length, and level of detail you want Claude to have.
</Tip>

### Break the interaction into unique tasks

Customer support chat is a collection of multiple different tasks, from question answering to information retrieval to taking action on requests, wrapped up in a single customer interaction. Before you start building, break down your ideal customer interaction into every task you want Claude to be able to perform. This ensures you can prompt and evaluate Claude for every task, and gives you a good sense of the range of interactions you need to account for when writing test cases.

<Tip>
  Customers sometimes find it helpful to visualize this as an interaction flowchart of possible conversation inflection points depending on user requests.
</Tip>

Here are the key tasks associated with the example insurance interaction:

1. Greeting and general guidance

   * Warmly greet the customer and initiate conversation
   * Provide general information about the company and interaction

2. Product information

   * Provide information about electric vehicle coverage
     <Note>
       This will require that Claude have the necessary information in its context, and might imply that a 

       [RAG integration](https://platform.claude.com/cookbook/capabilities-retrieval-augmented-generation-guide)

        is necessary.
     </Note>
   * Answer questions related to unique electric vehicle insurance needs
   * Answer follow-up questions about the quote or insurance details
   * Offer links to sources when appropriate

3. Conversation management

   * Stay on topic (car insurance)
   * Redirect off-topic questions back to relevant subjects

4. Quote generation

   * Ask appropriate questions to determine quote eligibility
   * Adapt questions based on customer responses
   * Submit collected information to quote generation API
   * Present the provided quote to the customer

### Establish success criteria

Work with your support team to [define success criteria and write detailed evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) with measurable benchmarks and goals.

Here are criteria and benchmarks that can be used to evaluate how successfully Claude performs the defined tasks:

<AccordionGroup>
  <Accordion title="Query comprehension accuracy">
    This metric evaluates how accurately Claude understands customer inquiries across various topics. Measure this by reviewing a sample of conversations and assessing whether Claude has the correct interpretation of customer intent, critical next steps, what successful resolution looks like, and more. Aim for a comprehension accuracy of 95% or higher.
  </Accordion>

  <Accordion title="Response relevance">
    This assesses how well Claude's response addresses the customer's specific question or issue. Evaluate a set of conversations and rate the relevance of each response (using LLM-based grading for scale). Target a relevance score of 90% or above.
  </Accordion>

  <Accordion title="Response accuracy">
    Assess the correctness of general company and product information provided to the user, based on the information provided to Claude in context. Target 100% accuracy in this introductory information.
  </Accordion>

  <Accordion title="Citation provision relevance">
    Track the frequency and relevance of links or sources offered. Target providing relevant sources in 80% of interactions where additional information could be beneficial.
  </Accordion>

  <Accordion title="Topic adherence">
    Measure how well Claude stays on topic, such as the topic of car insurance in the example implementation. Aim for 95% of responses to be directly related to car insurance or the customer's specific query.
  </Accordion>

  <Accordion title="Content generation effectiveness">
    Measure how successful Claude is at determining when to generate informational content and how relevant that content is. For example, in this implementation, you would be determining how well Claude understands when to generate a quote and how accurate that quote is. Target 100% accuracy, as this is vital information for a successful customer interaction.
  </Accordion>

  <Accordion title="Escalation efficiency">
    This measures Claude's ability to recognize when a query needs human intervention and escalate appropriately. Track the percentage of correctly escalated conversations versus those that should have been escalated but weren't. Aim for an escalation accuracy of 95% or higher.
  </Accordion>
</AccordionGroup>

Here are criteria and benchmarks that can be used to evaluate the business impact of employing Claude for support:

<AccordionGroup>
  <Accordion title="Sentiment maintenance">
    This assesses Claude's ability to maintain or improve customer sentiment throughout the conversation. Use sentiment analysis tools to measure sentiment at the beginning and end of each conversation. Aim for maintained or improved sentiment in 90% of interactions.
  </Accordion>

  <Accordion title="Deflection rate">
    The percentage of customer inquiries successfully handled by the chatbot without human intervention. Typically aim for 70-80% deflection rate, depending on the complexity of inquiries.
  </Accordion>

  <Accordion title="Customer satisfaction score">
    A measure of how satisfied customers are with their chatbot interaction. Usually done through post-interaction surveys. Aim for a CSAT score of 4 out of 5 or higher.
  </Accordion>

  <Accordion title="Average handle time">
    The average time it takes for the chatbot to resolve an inquiry. This varies widely based on the complexity of issues, but generally, aim for a lower AHT compared to human agents.
  </Accordion>
</AccordionGroup>


## How to implement Claude as a customer service agent

Source: https://platform.claude.com/llms-full.txt#how-to-implement-claude-as-a-customer-service-agent

### Choose the right Claude model

The choice of model depends on the trade-offs between cost, accuracy, and response time.

For customer support chat, Claude Opus 5 is well suited to balance intelligence, latency, and cost, including the most complex support scenarios that require deep reasoning across long, multi-step conversations. However, for instances where you have conversation flow with multiple prompts including RAG, tool use, or long-context prompts, Claude Haiku 4.5 may be more suitable to optimize for latency.

### Build a strong prompt

Using Claude for customer support requires Claude having enough direction and context to respond appropriately, while having enough flexibility to handle a wide range of customer inquiries.

Start by writing the elements of a strong prompt, beginning with a system prompt. Create a file called `config.py` and add each of the following blocks to it:

<Tip>
  While you may be tempted to put all your information inside a system prompt as a way to separate instructions from the user conversation, Claude actually works best with the bulk of its prompt content written inside the first 

  `User`

   turn (with the only exception being role prompting). Read more at 

  [Giving Claude a role with a system prompt](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#give-claude-a-role)

  .
</Tip>

It's best to break down complex prompts into subsections and write one part at a time. For each task, you might find greater success by following a step-by-step process to define the parts of the prompt Claude would need to do the task well. For this car insurance customer support example, you'll be writing piecemeal all the parts for a prompt starting with the "Greeting and general guidance" task. This also makes debugging your prompt easier as you can more quickly adjust individual parts of the overall prompt.

Then do the same for your car insurance and electric car insurance information.

Now that you have your static content, add at least 4-5 sample "good" interactions to guide Claude's responses. These examples should be representative of your ideal customer interaction and can include elements such as guardrails and tool calls.

You will also want to include any important instructions outlining dos and don'ts for how Claude should interact with the customer. This may draw from brand guardrails or support policies.

Now combine all these sections into a single string to use as your prompt.

### Add dynamic and agentic capabilities with tool use

Claude is capable of taking actions and retrieving information dynamically using client-side tool use functionality. Start by listing any external tools or APIs the prompt should use.

For this example, start with one tool for calculating the quote.

<Tip>
  As a reminder, this tool will not perform the actual calculation, it will just signal to the application that a tool should be used with whatever arguments specified.
</Tip>

Add the model name, the tool definition, and a stub implementation to `config.py`:

### Deploy your prompts

It's hard to know how well your prompt works without deploying it in a test production setting and [running evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests). Build a small application using the prompt, the Anthropic SDK, and Streamlit for a user interface.

In a file called `chatbot.py` (or the equivalent module in your language), set up the ChatBot class, which will encapsulate the interactions with the Anthropic SDK.

The class should have two main methods: one that calls the API to generate a message, and one that processes each incoming user input.

<CodeGroup exclude="shell">
  ```python Python
  # In your chatbot.py, import these from the config.py you wrote above:
  # from config import IDENTITY, TOOLS, MODEL, get_quote
  from anthropic import Anthropic
  from dotenv import load_dotenv

  load_dotenv()


  class ChatBot:
      def __init__(self, session_state):
          self.anthropic = Anthropic()
          self.session_state = session_state

      def generate_message(
          self,
          messages,
          max_tokens,
      ):
          try:
              response = self.anthropic.messages.create(
                  model=MODEL,
                  system=IDENTITY,
                  max_tokens=max_tokens,
                  messages=messages,
                  tools=TOOLS,
              )
              return response
          except Exception as e:
              return {"error": str(e)}

      def process_user_input(self, user_input):
          self.session_state.messages.append({"role": "user", "content": user_input})

          response_message = self.generate_message(
              messages=self.session_state.messages,
              max_tokens=2048,
          )

          if "error" in response_message:
              return f"An error occurred: {response_message['error']}"

          if response_message.content[-1].type == "tool_use":
              tool_use = response_message.content[-1]
              func_name = tool_use.name
              func_params = tool_use.input
              tool_use_id = tool_use.id

              result = self.handle_tool_use(func_name, func_params)
              self.session_state.messages.append(
                  {"role": "assistant", "content": response_message.content}
              )
              self.session_state.messages.append(
                  {
                      "role": "user",
                      "content": [
                          {
                              "type": "tool_result",
                              "tool_use_id": tool_use_id,
                              "content": f"{result}",
                          }
                      ],
                  }
              )

              follow_up_response = self.generate_message(
                  messages=self.session_state.messages,
                  max_tokens=2048,
              )

              if "error" in follow_up_response:
                  return f"An error occurred: {follow_up_response['error']}"

              response_text = next(
                  (block.text for block in follow_up_response.content if block.type == "text"),
                  None,
              )
              if response_text is None:
                  raise Exception("An error occurred: Unexpected response type")
              self.session_state.messages.append(
                  {"role": "assistant", "content": response_text}
              )
              return response_text

          text_block = next(
              (block for block in response_message.content if block.type == "text"), None
          )
          if text_block is not None:
              response_text = text_block.text
              self.session_state.messages.append(
                  {"role": "assistant", "content": response_text}
              )
              return response_text

          raise Exception("An error occurred: Unexpected response type")

      def handle_tool_use(self, func_name, func_params):
          if func_name == "get_quote":
              premium = get_quote(**func_params)
              return f"Quote generated: ${premium:.2f} per month"

          raise Exception("An unexpected tool was used")

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";

  class ChatBot {
    // IDENTITY, MODEL, TOOLS, and getQuote mirror the config.py values defined
    // earlier in this guide (shown in Python).
    readonly anthropic = new Anthropic();
    readonly messages: Anthropic.MessageParam[] = [];

    async generateMessage(
      messages: Anthropic.MessageParam[],
      maxTokens: number
    ): Promise<Anthropic.Message> {
      return this.anthropic.messages.create({
        model: MODEL,
        system: IDENTITY,
        max_tokens: maxTokens,
        messages,
        tools: TOOLS
      });
    }

    async processUserInput(userInput: string): Promise<string> {
      this.messages.push({ role: "user", content: userInput });

      const responseMessage = await this.generateMessage(this.messages, 2048);

      const lastBlock = responseMessage.content.at(-1);
      if (lastBlock?.type === "tool_use") {
        const toolResult = this.handleToolUse(lastBlock.name, lastBlock.input);

        this.messages.push({ role: "assistant", content: responseMessage.content });
        this.messages.push({
          role: "user",
          content: [{ type: "tool_result", tool_use_id: lastBlock.id, content: toolResult }]
        });

        const followUpResponse = await this.generateMessage(this.messages, 2048);

        const followUpBlock = followUpResponse.content.find(
          (block): block is Anthropic.TextBlock => block.type === "text"
        );
        if (!followUpBlock) {
          throw new Error("An error occurred: Unexpected response type");
        }
        this.messages.push({ role: "assistant", content: followUpBlock.text });
        return followUpBlock.text;
      }

      const firstBlock = responseMessage.content.find(
        (block): block is Anthropic.TextBlock => block.type === "text"
      );
      if (firstBlock) {
        this.messages.push({ role: "assistant", content: firstBlock.text });
        return firstBlock.text;
      }

      throw new Error("An error occurred: Unexpected response type");
    }

    handleToolUse(toolName: string, toolInput: unknown): string {
      if (toolName === "get_quote") {
        // The SDK types tool_use.input as unknown; narrow it to the get_quote schema.
        if (
          toolInput === null ||
          typeof toolInput !== "object" ||
          !("make" in toolInput) || typeof toolInput.make !== "string" ||
          !("model" in toolInput) || typeof toolInput.model !== "string" ||
          !("year" in toolInput) || typeof toolInput.year !== "number" ||
          !("mileage" in toolInput) || typeof toolInput.mileage !== "number" ||
          !("driver_age" in toolInput) || typeof toolInput.driver_age !== "number"
        ) {
          throw new Error("An error occurred: Unexpected tool input");
        }
        const { make, model: vehicleModel, year, mileage, driver_age: driverAge } = toolInput;

        const premium = getQuote(make, vehicleModel, year, mileage, driverAge);
        return `Quote generated: $${premium.toFixed(2)} per month`;
      }

      throw new Error("An unexpected tool was used");
    }
  }

csharp C#
  using System.Text.Json;
  using Anthropic;
  using Anthropic.Models.Messages;

  // Config.Model, Config.Identity, Config.Tools, and Config.GetQuote mirror
  // the config.py values defined earlier in this guide (shown in Python).
  public class ChatBot
  {
      private readonly AnthropicClient _anthropic = new();

      public List<MessageParam> Messages { get; } = [];

      public async Task<Message> GenerateMessage(List<MessageParam> messages, long maxTokens) =>
          await _anthropic.Messages.Create(
              new MessageCreateParams
              {
                  Model = Config.Model,
                  System = Config.Identity,
                  MaxTokens = maxTokens,
                  Messages = messages,
                  Tools = Config.Tools,
              }
          );

      public async Task<string> ProcessUserInput(string userInput)
      {
          Messages.Add(new() { Role = Role.User, Content = userInput });

          var responseMessage = await GenerateMessage(Messages, maxTokens: 2048);

          if (responseMessage.Content[^1].TryPickToolUse(out var toolUse))
          {
              var toolResult = HandleToolUse(toolUse.Name, toolUse.Input);

              Messages.Add(new()
              {
                  Role = Role.Assistant,
                  Content = responseMessage.Content
                      .Select(contentBlock => new ContentBlockParam(contentBlock.Json))
                      .ToList(),
              });
              Messages.Add(new()
              {
                  Role = Role.User,
                  Content = new List<ContentBlockParam>
                  {
                      new ToolResultBlockParam { ToolUseID = toolUse.ID, Content = toolResult },
                  },
              });

              var followUpResponse = await GenerateMessage(Messages, maxTokens: 2048);

              foreach (var block in followUpResponse.Content)
              {
                  if (block.TryPickText(out var followUpText))
                  {
                      Messages.Add(new() { Role = Role.Assistant, Content = followUpText.Text });
                      return followUpText.Text;
                  }
              }

              throw new InvalidOperationException("An error occurred: Unexpected response type");
          }

          foreach (var block in responseMessage.Content)
          {
              if (block.TryPickText(out var textBlock))
              {
                  Messages.Add(new() { Role = Role.Assistant, Content = textBlock.Text });
                  return textBlock.Text;
              }
          }

          throw new InvalidOperationException("An error occurred: Unexpected response type");
      }

      public string HandleToolUse(string funcName, IReadOnlyDictionary<string, JsonElement> funcParams)
      {
          if (funcName == "get_quote")
          {
              var premium = Config.GetQuote(
                  funcParams["make"].GetString()!,
                  funcParams["model"].GetString()!,
                  funcParams["year"].GetInt64(),
                  funcParams["mileage"].GetInt64(),
                  funcParams["driver_age"].GetInt64()
              );
              return $"Quote generated: ${premium:F2} per month";
          }

          throw new ArgumentException("An unexpected tool was used");
      }
  }

go Go
  import (
  	"context"
  	"encoding/json"
  	"fmt"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  // ChatBot wraps the Anthropic client and the conversation history. The
  // identity, model, tools, and getQuote values it uses mirror the config.py
  // definitions earlier in this guide (shown in Python).
  type ChatBot struct {
  	client   anthropic.Client
  	messages []anthropic.MessageParam
  }

  func NewChatBot() *ChatBot {
  	return &ChatBot{client: anthropic.NewClient()}
  }

  func (bot *ChatBot) GenerateMessage(ctx context.Context, messages []anthropic.MessageParam, maxTokens int64) (*anthropic.Message, error) {
  	return bot.client.Messages.New(ctx, anthropic.MessageNewParams{
  		Model:     model,
  		System:    []anthropic.TextBlockParam{{Text: identity}},
  		MaxTokens: maxTokens,
  		Messages:  messages,
  		Tools:     tools,
  	})
  }

  func (bot *ChatBot) ProcessUserInput(ctx context.Context, userInput string) (string, error) {
  	bot.messages = append(bot.messages, anthropic.NewUserMessage(anthropic.NewTextBlock(userInput)))

  	response, err := bot.GenerateMessage(ctx, bot.messages, 2048)
  	if err != nil {
  		return "", err
  	}

  	lastBlock := response.Content[len(response.Content)-1]
  	if toolUse, ok := lastBlock.AsAny().(anthropic.ToolUseBlock); ok {
  		result, err := bot.HandleToolUse(toolUse.Name, toolUse.Input)
  		if err != nil {
  			return "", err
  		}

  		bot.messages = append(bot.messages,
  			response.ToParam(),
  			anthropic.NewUserMessage(anthropic.NewToolResultBlock(toolUse.ID, result, false)),
  		)

  		followUp, err := bot.GenerateMessage(ctx, bot.messages, 2048)
  		if err != nil {
  			return "", err
  		}

  		for _, block := range followUp.Content {
  			if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  				bot.messages = append(bot.messages, anthropic.NewAssistantMessage(anthropic.NewTextBlock(textBlock.Text)))
  				return textBlock.Text, nil
  			}
  		}
  		return "", fmt.Errorf("an error occurred: unexpected response type")
  	}

  	for _, block := range response.Content {
  		if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  			bot.messages = append(bot.messages, anthropic.NewAssistantMessage(anthropic.NewTextBlock(textBlock.Text)))
  			return textBlock.Text, nil
  		}
  	}

  	return "", fmt.Errorf("an error occurred: unexpected response type")
  }

  func (bot *ChatBot) HandleToolUse(toolName string, toolInput json.RawMessage) (string, error) {
  	if toolName != "get_quote" {
  		return "", fmt.Errorf("an unexpected tool was used: %s", toolName)
  	}

  	var input struct {
  		Make      string `json:"make"`
  		Model     string `json:"model"`
  		Year      int    `json:"year"`
  		Mileage   int    `json:"mileage"`
  		DriverAge int    `json:"driver_age"`
  	}
  	if err := json.Unmarshal(toolInput, &input); err != nil {
  		return "", err
  	}
  	premium := getQuote(input.Make, input.Model, input.Year, input.Mileage, input.DriverAge)
  	return fmt.Sprintf("Quote generated: $%.2f per month", premium), nil
  }

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.JsonValue;
  import com.anthropic.models.messages.ContentBlock;
  import com.anthropic.models.messages.ContentBlockParam;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.MessageParam;
  import com.anthropic.models.messages.ToolResultBlockParam;
  import com.anthropic.models.messages.ToolUseBlock;

  // IDENTITY, MODEL, TOOLS, and getQuote mirror the config.py values defined
  // earlier in this guide (shown in Python).
  class ChatBot {
      final AnthropicClient anthropic;
      final List<MessageParam> messages;

      ChatBot() {
          // Reads the API key from the ANTHROPIC_API_KEY environment variable
          this.anthropic = AnthropicOkHttpClient.fromEnv();
          this.messages = new ArrayList<>();
      }

      Message generateMessage(List<MessageParam> messages, long maxTokens) {
          return anthropic.messages().create(MessageCreateParams.builder()
                  .model(MODEL)
                  .system(IDENTITY)
                  .maxTokens(maxTokens)
                  .messages(messages)
                  .tools(TOOLS)
                  .build());
      }

      String processUserInput(String userInput) {
          messages.add(MessageParam.builder()
                  .role(MessageParam.Role.USER)
                  .content(userInput)
                  .build());

          Message responseMessage = generateMessage(messages, 2048);

          List<ContentBlock> content = responseMessage.content();
          ContentBlock lastBlock = content.getLast();
          if (lastBlock.isToolUse()) {
              ToolUseBlock toolUse = lastBlock.asToolUse();
              Map<String, JsonValue> toolInput =
                      (Map<String, JsonValue>) toolUse._input().asObject().orElseThrow();
              String result = handleToolUse(toolUse.name(), toolInput);

              messages.add(MessageParam.builder()
                      .role(MessageParam.Role.ASSISTANT)
                      .contentOfBlockParams(content.stream().map(ContentBlock::toParam).toList())
                      .build());
              messages.add(MessageParam.builder()
                      .role(MessageParam.Role.USER)
                      .contentOfBlockParams(List.of(ContentBlockParam.ofToolResult(
                              ToolResultBlockParam.builder()
                                      .toolUseId(toolUse.id())
                                      .content(result)
                                      .build())))
                      .build());

              Message followUpResponse = generateMessage(messages, 2048);

              ContentBlock followUpBlock = followUpResponse.content().stream()
                      .filter(ContentBlock::isText)
                      .findFirst()
                      .orElseThrow(() -> new IllegalStateException("An error occurred: Unexpected response type"));
              String responseText = followUpBlock.asText().text();
              messages.add(MessageParam.builder()
                      .role(MessageParam.Role.ASSISTANT)
                      .content(responseText)
                      .build());
              return responseText;
          } else {
              ContentBlock textBlock = content.stream()
                      .filter(ContentBlock::isText)
                      .findFirst()
                      .orElseThrow(() -> new IllegalStateException("An error occurred: Unexpected response type"));
              String responseText = textBlock.asText().text();
              messages.add(MessageParam.builder()
                      .role(MessageParam.Role.ASSISTANT)
                      .content(responseText)
                      .build());
              return responseText;
          }
      }

      String handleToolUse(String funcName, Map<String, JsonValue> funcParams) {
          return switch (funcName) {
              case "get_quote" -> {
                  double premium = getQuote(
                          funcParams.get("make").asStringOrThrow(),
                          funcParams.get("model").asStringOrThrow(),
                          ((Number) funcParams.get("year").asNumber().orElseThrow()).longValue(),
                          ((Number) funcParams.get("mileage").asNumber().orElseThrow()).longValue(),
                          ((Number) funcParams.get("driver_age").asNumber().orElseThrow()).longValue());
                  yield "Quote generated: $%.2f per month".formatted(premium);
              }
              default -> throw new IllegalArgumentException("An unexpected tool was used");
          };
      }
  }

php PHP
  use Anthropic\Client;
  use Anthropic\Messages\Message;
  use Anthropic\Messages\MessageParam;
  use Anthropic\Messages\TextBlock;
  use Anthropic\Messages\ToolResultBlockParam;
  use Anthropic\Messages\ToolUseBlock;

  class ChatBot
  {
      // MODEL, IDENTITY, TOOLS, and get_quote() mirror the config.py values
      // defined earlier in this guide (shown in Python).

      /** @var list<MessageParam> */
      public private(set) array $messages = [];

      public function __construct(
          private readonly Client $anthropic = new Client(),
      ) {}

      /**
       * @param list<MessageParam> $messages
       */
      public function generateMessage(array $messages, int $maxTokens): Message
      {
          return $this->anthropic->messages->create(
              model: MODEL,
              system: IDENTITY,
              maxTokens: $maxTokens,
              messages: $messages,
              tools: TOOLS,
          );
      }

      public function processUserInput(string $userInput): string
      {
          $this->messages[] = MessageParam::with(role: 'user', content: $userInput);

          $responseMessage = $this->generateMessage($this->messages, maxTokens: 2048);

          $content = $responseMessage->content;
          $lastBlock = array_last($content);

          if ($lastBlock instanceof ToolUseBlock) {
              $toolResult = $this->handleToolUse($lastBlock->name, $lastBlock->input);

              $this->messages[] = MessageParam::with(role: 'assistant', content: $content);
              $this->messages[] = MessageParam::with(
                  role: 'user',
                  content: [
                      ToolResultBlockParam::with(toolUseID: $lastBlock->id, content: $toolResult),
                  ],
              );

              $followUpResponse = $this->generateMessage($this->messages, maxTokens: 2048);

              $firstBlock = array_find(
                  $followUpResponse->content,
                  static fn ($block): bool => $block instanceof TextBlock,
              );
              if (!$firstBlock instanceof TextBlock) {
                  throw new RuntimeException('An error occurred: Unexpected response type');
              }

              $this->messages[] = MessageParam::with(role: 'assistant', content: $firstBlock->text);

              return $firstBlock->text;
          }

          $firstBlock = array_find($content, static fn ($block): bool => $block instanceof TextBlock);
          if ($firstBlock instanceof TextBlock) {
              $this->messages[] = MessageParam::with(role: 'assistant', content: $firstBlock->text);

              return $firstBlock->text;
          }

          throw new RuntimeException('An error occurred: Unexpected response type');
      }

      /**
       * @param array<string, mixed> $funcParams
       */
      private function handleToolUse(string $funcName, array $funcParams): string
      {
          if ($funcName === 'get_quote') {
              $premium = get_quote(...$funcParams);

              return sprintf('Quote generated: $%.2f per month', $premium);
          }

          throw new RuntimeException('An unexpected tool was used');
      }
  }

ruby Ruby
  # IDENTITY, MODEL, TOOLS, and get_quote mirror the config.py values defined
  # earlier in this guide (shown in Python).
  require "anthropic"

  class ChatBot
    attr_reader :messages

    def initialize
      @anthropic = Anthropic::Client.new
      @messages = []
    end

    def generate_message(messages, max_tokens)
      @anthropic.messages.create(
        model: MODEL,
        system_: IDENTITY,
        max_tokens:,
        messages:,
        tools: TOOLS
      )
    end

    def process_user_input(user_input)
      @messages << {role: "user", content: user_input}

      response_message = generate_message(@messages, 2048)

      case response_message.content
      in [*, Anthropic::ToolUseBlock => tool_use]
        result = handle_tool_use(tool_use.name, tool_use.input)
        @messages << {role: "assistant", content: response_message.content}
        @messages << {
          role: "user",
          content: [{type: "tool_result", tool_use_id: tool_use.id, content: result}]
        }

        follow_up_response = generate_message(@messages, 2048)

        case follow_up_response.content
        in [*, Anthropic::TextBlock => text_block, *]
          @messages << {role: "assistant", content: text_block.text}
          text_block.text
        else
          raise "An error occurred: Unexpected response type"
        end
      in [*, Anthropic::TextBlock => text_block, *]
        @messages << {role: "assistant", content: text_block.text}
        text_block.text
      else
        raise "An error occurred: Unexpected response type"
      end
    end

    def handle_tool_use(tool_name, tool_input)
      raise "An unexpected tool was used" unless tool_name == "get_quote"

      premium = get_quote(**tool_input)
      format("Quote generated: $%.2f per month", premium)
    end
  end

python
import streamlit as st
from chatbot import ChatBot
from config import TASK_SPECIFIC_INSTRUCTIONS


def main():
    st.title("Chat with Eva, Acme Insurance Company's Assistant🤖")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "user", "content": TASK_SPECIFIC_INSTRUCTIONS},
            {"role": "assistant", "content": "Understood"},
        ]

    chatbot = ChatBot(st.session_state)

    # Display user and assistant messages skipping the first two
    for message in st.session_state.messages[2:]:
        # ignore tool use blocks
        if isinstance(message["content"], str):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if user_msg := st.chat_input("Type your message here..."):
        st.chat_message("user").markdown(user_msg)

        with st.chat_message("assistant"):
            with st.spinner("Eva is thinking..."):
                response_placeholder = st.empty()
                full_response = chatbot.process_user_input(user_msg)
                response_placeholder.markdown(full_response)


if __name__ == "__main__":
    main()

bash
streamlit run app.py
```

### Evaluate your prompts

Prompting often requires testing and optimization for it to be production ready. To determine the readiness of your solution, evaluate the chatbot performance using a systematic process combining quantitative and qualitative methods. Creating a [strong empirical evaluation](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#build-evaluations) based on your defined success criteria will allow you to optimize your prompts.

### Improve performance

In complex scenarios, it may be helpful to consider additional strategies to improve performance beyond standard [prompt engineering techniques](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) & [guardrail implementation strategies](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations). Here are some common scenarios:

#### Reduce long context latency with RAG

When dealing with large amounts of static and dynamic context, including all information in the prompt can lead to high costs, slower response times, and reaching context window limits. In this scenario, implementing Retrieval Augmented Generation (RAG) techniques can improve performance and efficiency.

By using [embedding models like Voyage](https://platform.claude.com/docs/en/build-with-claude/embeddings) to convert information into vector representations, you can create a more scalable and responsive system. This approach allows for dynamic retrieval of relevant information based on the current query, rather than including all possible context in every prompt.

Implementing RAG for support use cases has been shown to increase accuracy, reduce response times, and reduce API costs in systems with extensive context requirements. See the [RAG recipe](https://platform.claude.com/cookbook/capabilities-retrieval-augmented-generation-guide) for a worked example.

#### Integrate real-time data with tool use

When dealing with queries that require real-time information, such as account balances or policy details, embedding-based RAG approaches are not sufficient. Instead, tool use can enhance your chatbot's ability to provide accurate, real-time responses. For example, you can use tool use to look up customer information, retrieve order details, and cancel orders on behalf of the customer.

This approach, [outlined in the tool use: customer service agent recipe](https://platform.claude.com/cookbook/tool-use-customer-service-agent), lets you integrate live data into Claude's responses and provide a more personalized and efficient customer experience.

#### Strengthen input and output guardrails

When deploying a chatbot, especially in customer service scenarios, it's important to prevent risks associated with misuse, out-of-scope queries, and inappropriate responses. While Claude is inherently resilient to such scenarios, here are additional steps to strengthen your chatbot guardrails:

* [Reduce hallucination](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations): Implement fact-checking mechanisms and [citations](https://platform.claude.com/cookbook/misc-using-citations) to ground responses in provided information.
* Cross-check information: Verify that the agent's responses align with your company's policies and known facts.
* Avoid contractual commitments: Ensure the agent doesn't make promises or enter into agreements it's not authorized to make.
* [Mitigate jailbreaks](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks): Use methods like harmlessness screens and input validation to prevent users from exploiting model vulnerabilities, aiming to generate inappropriate content.
* Avoid mentioning competitors: Implement a competitor mention filter to maintain brand focus and not mention any competitor's products or services.
* [Increase output consistency](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency): Prevent Claude from changing style or going out of character, even during long, complex interactions.
* Remove Personally Identifiable Information (PII): Unless explicitly required and authorized, strip out any PII from responses.

#### Reduce perceived response time with streaming

When dealing with potentially lengthy responses, implementing streaming can improve user engagement and satisfaction. In this scenario, users receive the answer progressively instead of waiting for the entire response to be generated.

Here is how to implement streaming:

1. Use the [Anthropic Streaming API](https://platform.claude.com/docs/en/build-with-claude/streaming) to support streaming responses.
2. Set up your frontend to handle incoming chunks of text.
3. Display each chunk as it arrives, simulating real-time typing.
4. Implement a mechanism to save the full response, allowing users to view it if they navigate away and return.

In some cases, streaming enables the use of more advanced models with higher base latencies, as the progressive display mitigates the impact of longer processing times.

#### Scale your chatbot

As the complexity of your chatbot grows, your application architecture can evolve to match. Before you add further layers to your architecture, consider the following less exhaustive options:

* Ensure that you are making the most out of your prompts and optimizing through prompt engineering. Use the [prompt engineering guides](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) to write the most effective prompts.
* Add additional [tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) to the prompt (which can include [prompt chains](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#chain-complex-prompts)) and see if you can achieve the functionality required.

If your chatbot handles incredibly varied tasks, you may want to consider adding a [separate intent classifier](https://platform.claude.com/cookbook/capabilities-classification-guide) to route the initial customer query. For the existing application, this would involve creating a decision tree that would route customer queries through the classifier and then to specialized conversations (with their own set of tools and system prompts). Note, this method requires an additional call to Claude that can increase latency.

### Integrate Claude into your support workflow

While these examples have focused on Python functions callable within a Streamlit environment, deploying Claude for real-time support chatbot requires an API service.

Here's how you can approach this:

1. Create an API wrapper: Develop a simple API wrapper around your classification function. For example, you can use Flask API or Fast API to wrap your code into a HTTP Service. Your HTTP service could accept the user input and return the Assistant response in its entirety. Thus, your service could have the following characteristics:

   * Server-Sent Events (SSE): SSE allows for real-time streaming of responses from the server to the client. This provides a smooth, interactive experience when working with LLMs.
   * Caching: Implementing caching can improve response times and reduce unnecessary API calls.
   * Context retention: Maintaining context when a user navigates away and returns is important for continuity in conversations.

2. Build a web interface: Implement a user-friendly web UI for interacting with the Claude-powered agent.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-99

<CardGroup cols={2}>
  <Card title="Tool use" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview">
    Give Claude access to your APIs so it can take action on behalf of customers.
  </Card>

  <Card title="Develop tests" icon="check" href="https://platform.claude.com/docs/en/test-and-evaluate/develop-tests">
    Build evaluations to measure your support agent against the success criteria you defined.
  </Card>

  <Card title="Streaming" icon="bolt" href="https://platform.claude.com/docs/en/build-with-claude/streaming">
    Stream responses so customers see answers as they generate.
  </Card>

  <Card title="Prompt engineering" icon="lightbulb" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview">
    Refine your system prompt and examples for better task performance.
  </Card>
</CardGroup>


---
title: Legal summarization
url: https://platform.claude.com/docs/en/about-claude/use-case-guides/legal-summarization
description: This guide walks through how to leverage Claude's advanced natural language processing capabilities to efficiently summarize legal documents, extracting key information and expediting legal research. With Claude, you can streamline the review of contracts, litigation prep, and regulatory work, saving time and ensuring accuracy in your legal processes.
---

> Visit the [summarization cookbook](https://platform.claude.com/cookbook/capabilities-summarization-guide) to see an example legal summarization implementation using Claude.


## Before building with Claude

Source: https://platform.claude.com/llms-full.txt#before-building-with-claude-3

### Decide whether to use Claude for legal summarization

Here are some key indicators that you should employ an LLM such as Claude to summarize legal documents:

<AccordionGroup>
  <Accordion title="You want to review a high volume of documents efficiently and affordably">
    Large-scale document review can be time-consuming and expensive when done manually. Claude can process and summarize vast amounts of legal documents rapidly, significantly reducing the time and cost associated with document review. This capability is particularly valuable for tasks like due diligence, contract analysis, or litigation discovery, where efficiency is crucial.
  </Accordion>

  <Accordion title="You require automated extraction of key metadata">
    Claude can efficiently extract and categorize important metadata from legal documents, such as parties involved, dates, contract terms, or specific clauses. This automated extraction can help organize information, making it easier to search, analyze, and manage large document sets. It's especially useful for contract management, compliance checks, or creating searchable databases of legal information. 
  </Accordion>

  <Accordion title="You want to generate clear, concise, and standardized summaries">
    Claude can generate structured summaries that follow predetermined formats, making it easier for legal professionals to quickly grasp the key points of various documents. These standardized summaries can improve readability, facilitate comparison between documents, and enhance overall comprehension, especially when dealing with complex legal language or technical jargon.
  </Accordion>

  <Accordion title="You need precise citations for your summaries">
    When creating legal summaries, proper attribution and citation are crucial to ensure credibility and compliance with legal standards. Claude can be prompted to include accurate citations for all referenced legal points, making it easier for legal professionals to review and verify the summarized information.
  </Accordion>

  <Accordion title="You want to streamline and expedite your legal research process">
    Claude can assist in legal research by quickly analyzing large volumes of case law, statutes, and legal commentary. It can identify relevant precedents, extract key legal principles, and summarize complex legal arguments. This capability can significantly speed up the research process, allowing legal professionals to focus on higher-level analysis and strategy development.
  </Accordion>
</AccordionGroup>

### Determine the details you want the summarization to extract

There is no single correct summary for any given document. Without clear direction, it can be difficult for Claude to determine which details to include. To achieve optimal results, identify the specific information you want to include in the summary.

For instance, when summarizing a sublease agreement, you might want to extract the following key points:

### Establish success criteria

Evaluating the quality of summaries is a notoriously challenging task. Unlike many other natural language processing tasks, evaluation of summaries often lacks clear-cut, objective metrics. The process can be highly subjective, with different readers valuing different aspects of a summary. Here are criteria you may want to consider when assessing how well Claude performs legal summarization.

<AccordionGroup>
  <Accordion title="Factual correctness">
    The summary should accurately represent the facts, legal concepts, and key points in the document.
  </Accordion>

  <Accordion title="Legal precision">
    Terminology and references to statutes, case law, or regulations must be correct and aligned with legal standards.
  </Accordion>

  <Accordion title="Conciseness">
     The summary should condense the legal document to its essential points without losing important details.
  </Accordion>

  <Accordion title="Consistency">
    If summarizing multiple documents, the LLM should maintain a consistent structure and approach to each summary.
  </Accordion>

  <Accordion title="Readability">
    The text should be clear and easy to understand. If the audience is not legal experts, the summarization should not include legal jargon that could confuse the audience.
  </Accordion>

  <Accordion title="Bias and fairness">
    The summary should present an unbiased and fair depiction of the legal arguments and positions.
  </Accordion>
</AccordionGroup>

See the guide on [establishing success criteria](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) for more information.

***


## How to summarize legal documents using Claude

Source: https://platform.claude.com/llms-full.txt#how-to-summarize-legal-documents-using-claude

### Select the right Claude model

Model accuracy is extremely important when summarizing legal documents. Claude Opus 5 is an excellent choice for use cases such as this where high accuracy is required. If the size and quantity of your documents is large such that costs start to become a concern, you can also try using a smaller model such as Claude Haiku 4.5.

To help estimate these costs, the following is a comparison of the cost to summarize 1,000 sublease agreements using Opus and Haiku models:

* **Content size**

  * Number of agreements: 1,000
  * Characters per agreement: 300,000
  * Total characters: 300M

* **Estimated tokens**

  * Input tokens: 86M (assuming 1 token per 3.5 characters)
  * Output tokens per summary: 350
  * Total output tokens: 350,000

* **Claude Opus 5 estimated cost**

  * Input token cost: 86 MTok \* $5.00/MTok = $430.00 USD
  * Output token cost: 0.35 MTok \* $25.00/MTok = $8.75 USD
  * Total cost: $430.00 + $8.75 = $438.75 USD

* **Claude Opus 4.8 estimated cost**

  * Input token cost: 86 MTok \* $5.00/MTok = $430.00 USD
  * Output token cost: 0.35 MTok \* $25.00/MTok = $8.75 USD
  * Total cost: $430.00 + $8.75 = $438.75 USD

* **Claude Haiku 4.5 estimated cost**

  * Input token cost: 86 MTok \* $1.00/MTok = $86.00 USD
  * Output token cost: 0.35 MTok \* $5.00/MTok = $1.75 USD
  * Total cost: $86.00 + $1.75 = $87.75 USD

<Tip>
  Actual costs may differ from these estimates. These estimates are based on the example highlighted in the 

  [Build a strong prompt](https://platform.claude.com/docs/en/about-claude/use-case-guides/legal-summarization#build-a-strong-prompt)

   section.
</Tip>

### Transform documents into a format that Claude can process

Before you begin summarizing documents, you need to prepare your data. This involves extracting text from PDFs, cleaning the text, and ensuring it's ready to be processed by Claude.

Here is a demonstration of this process on a sample PDF:

In this example, you first download a PDF of a sample sublease agreement used in the [summarization cookbook](https://platform.claude.com/cookbook/capabilities-summarization-guide). This agreement was sourced from a publicly available sublease agreement from the [sec.gov website](https://www.sec.gov/Archives/edgar/data/1045425/000119312507044370/dex1032.htm).

The example uses the pypdf library to extract the contents of the PDF and convert it to text. The text data is then cleaned by removing page numbers and extra whitespace.

### Build a strong prompt

Claude can adapt to various summarization styles. You can change the details of the prompt to guide Claude to be more or less verbose, include more or less technical terminology, or provide a higher- or lower-level summary of the context at hand.

Here’s an example of how to create a prompt that ensures the generated summaries follow a consistent structure when analyzing sublease agreements:

```python Python
# Initialize the Anthropic client
client = anthropic.Anthropic()


def summarize_document(
    text, details_to_extract, model="claude-opus-5", max_tokens=1000
):
    # Format the details to extract to be placed within the prompt's context
    details_to_extract_str = "\n".join(details_to_extract)

    # Prompt the model to summarize the sublease agreement
    prompt = f"""Summarize the following sublease agreement. Focus on these key aspects:

    {details_to_extract_str}

    Provide the summary in bullet points nested within the XML header for each section. For example:

    <parties involved>
    - Sublessor: [Name]
    // Add more details as needed
    </parties involved>

    If any information is not explicitly stated in the document, note it as "Not specified". Do not preamble.

    Sublease agreement text:
    {text}
    """

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system="You are a legal analyst specializing in real estate law, known for highly accurate and detailed summaries of sublease agreements.",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    return next(block.text for block in response.content if block.type == "text")


sublease_summary = summarize_document(document_text, details_to_extract)
print(sublease_summary)
```

This code implements a `summarize_document` function that uses Claude to summarize the contents of a sublease agreement. The function accepts a text string and a list of details to extract as inputs. In this example, the code calls the function with the `document_text` and `details_to_extract` variables that were defined in the previous code snippets.

Within the function, a prompt is generated for Claude, including the document to be summarized, the details to extract, and specific instructions for summarizing the document. The prompt instructs Claude to respond with a summary of each detail to extract nested within XML headers.

Because the code outputs each section of the summary within tags, each section can easily be parsed out as a post-processing step. This approach enables structured summaries that can be adapted for your use case, so that each summary follows the same pattern.

### Evaluate your prompt

Prompting often requires testing and optimization for it to be production ready. To determine the readiness of your solution, evaluate the quality of your summaries using a systematic process combining quantitative and qualitative methods. Creating a [strong empirical evaluation](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#build-evaluations) based on your defined success criteria allows you to optimize your prompts. Here are some metrics you may want to include within your empirical evaluation:

<AccordionGroup>
  <Accordion title="ROUGE scores">
    This measures the overlap between the generated summary and an expert-created reference summary. This metric primarily focuses on recall and is useful for evaluating content coverage.
  </Accordion>

  <Accordion title="BLEU scores">
    Although originally developed for machine translation, this metric can be adapted for summarization tasks. BLEU scores measure the precision of n-gram matches between the generated summary and reference summaries. A higher score indicates that the generated summary contains similar phrases and terminology to the reference summary. 
  </Accordion>

  <Accordion title="Contextual embedding similarity">
    This metric involves creating vector representations (embeddings) of both the generated and reference summaries. The similarity between these embeddings is then calculated, often using cosine similarity. Higher similarity scores indicate that the generated summary captures the semantic meaning and context of the reference summary, even if the exact wording differs.
  </Accordion>

  <Accordion title="LLM-based grading">
    This method involves using an LLM such as Claude to evaluate the quality of generated summaries against a scoring rubric. The rubric can be tailored to your specific needs, assessing key factors such as accuracy, completeness, and coherence. For implementation guidance, see 

    [Tips for LLM-based grading](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#tips-for-llm-based-grading)

    .
  </Accordion>

  <Accordion title="Human evaluation">
    In addition to creating the reference summaries, legal experts can also evaluate the quality of the generated summaries. Although this is expensive and time-consuming at scale, this is often done on a few summaries as a validation check before deploying to production.
  </Accordion>
</AccordionGroup>

### Deploy your prompt

Here are some additional considerations to keep in mind as you deploy your solution to production.

1. **Ensure no liability:** Understand the legal implications of errors in the summaries, which could lead to legal liability for your organization or clients. Provide disclaimers or legal notices clarifying that the summaries are generated by AI and should be reviewed by legal professionals.

2. **Handle diverse document types:** This guide discusses how to extract text from PDFs. In the real world, documents may come in a variety of formats (such as PDFs, Word documents, and text files). Ensure your data extraction pipeline can convert all of the file formats you expect to receive.

3. **Parallelize API calls to Claude:** Long documents with a large number of tokens may require up to a minute for Claude to generate a summary. For large document collections, you may want to send API calls to Claude in parallel so that the summaries can be completed in a reasonable timeframe. Refer to Anthropic’s [rate limits](https://platform.claude.com/docs/en/api/rate-limits#rate-limits) to determine the maximum amount of API calls that can be performed in parallel.

***


## Improve performance

Source: https://platform.claude.com/llms-full.txt#improve-performance-2

In complex scenarios, it may be helpful to consider additional strategies to improve performance beyond standard [prompt engineering techniques](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview). Here are some advanced strategies:

### Perform meta-summarization to summarize long documents

Legal summarization often involves handling long documents or many related documents at once, such that you surpass Claude’s context window. You can use a chunking method known as meta-summarization to handle this use case. This technique involves breaking down documents into smaller, manageable chunks and then processing each chunk separately. You can then combine the summaries of each chunk to create a meta-summary of the entire document.

Here's an example of how to perform meta-summarization:

```python Python
# Initialize the Anthropic client
client = anthropic.Anthropic()


def chunk_text(text, chunk_size=20000):
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def summarize_long_document(
    text, details_to_extract, model="claude-opus-5", max_tokens=1000
):
    # Format the details to extract to be placed within the prompt's context
    details_to_extract_str = "\n".join(details_to_extract)

    # Iterate over chunks and summarize each one
    chunk_summaries = [
        summarize_document(
            chunk, details_to_extract, model=model, max_tokens=max_tokens
        )
        for chunk in chunk_text(text)
    ]

    final_summary_prompt = f"""

    You are looking at the chunked summaries of multiple documents that are all related.
    Combine the following summaries of the document from different truthful sources into a coherent overall summary:

    <chunked_summaries>
    {"".join(chunk_summaries)}
    </chunked_summaries>

    Focus on these key aspects:
    {details_to_extract_str}

    Provide the summary in bullet points nested within the XML header for each section. For example:

    <parties involved>
    - Sublessor: [Name]
    // Add more details as needed
    </parties involved>

    If any information is not explicitly stated in the document, note it as "Not specified". Do not preamble.
    """

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system="You are a legal expert that summarizes notes on one document.",
        messages=[
            {"role": "user", "content": final_summary_prompt},
        ],
    )

    return next(block.text for block in response.content if block.type == "text")


long_summary = summarize_long_document(document_text, details_to_extract)
print(long_summary)
```

The `summarize_long_document` function builds upon the earlier `summarize_document` function by splitting the document into smaller chunks and summarizing each chunk individually.

The code achieves this by applying the `summarize_document` function to each chunk of 20,000 characters within the original document. The individual summaries are then combined, and a final summary is created from these chunk summaries.

Note that the `summarize_long_document` function isn't strictly necessary for the example PDF, as the entire document fits within Claude's context window. However, it becomes essential for documents exceeding Claude's context window or when summarizing multiple related documents together. Regardless, this meta-summarization technique often captures additional important details in the final summary that were missed in the earlier single-summary approach.

### Use summary indexed documents to explore a large collection of documents

Searching a collection of documents with an LLM usually involves retrieval-augmented generation (RAG). However, in scenarios involving large documents or when precise information retrieval is crucial, a basic RAG approach may be insufficient. Summary indexed documents is an advanced RAG approach that provides a more efficient way of ranking documents for retrieval, using less context than traditional RAG methods. In this approach, you first use Claude to generate a concise summary for each document in your corpus, and then use Claude to rank the relevance of each summary to the query being asked. For further details on this approach, including a code-based example, check out the summary indexed documents section in the [summarization cookbook](https://platform.claude.com/cookbook/capabilities-summarization-guide).

### Fine-tune Claude to learn from your dataset

Another advanced technique to improve Claude's ability to generate summaries is fine-tuning. Fine-tuning involves training Claude on a custom dataset that specifically aligns with your legal summarization needs, ensuring that Claude adapts to your use case. Here’s an overview on how to perform fine-tuning:

1. **Identify errors:** Start by collecting instances where Claude’s summaries fall short - this could include missing critical legal details, misunderstanding context, or using inappropriate legal terminology.

2. **Curate a dataset:** Once you've identified these issues, compile a dataset of these problematic examples. This dataset should include the original legal documents alongside your corrected summaries, ensuring that Claude learns the desired behavior.

3. **Perform fine-tuning:** Fine-tuning involves retraining the model on your curated dataset to adjust its weights and parameters. This retraining helps Claude better adapt to the specific requirements of your legal domain, improving its ability to summarize documents according to your standards.

4. **Iterative improvement:** Fine-tuning is not a one-time process. As Claude continues to generate summaries, you can iteratively add new examples where it has underperformed, further refining its capabilities. Over time, this continuous feedback loop will result in a model that is highly specialized for your legal summarization tasks.

<Tip>
  Fine-tuning is currently only available through Amazon Bedrock. Additional details are available in the 

  [AWS launch blog](https://aws.amazon.com/blogs/machine-learning/fine-tune-anthropics-claude-3-haiku-in-amazon-bedrock-to-boost-model-accuracy-and-quality/)

  .
</Tip>

<CardGroup cols={2}>
  <Card title="Summarization cookbook" icon="link" href="https://platform.claude.com/cookbook/capabilities-summarization-guide">
    View a fully implemented code-based example of how to use Claude to summarize contracts.
  </Card>

  <Card title="Citations cookbook" icon="link" href="https://platform.claude.com/cookbook/misc-using-citations">
    Explore the Citations cookbook recipe for guidance on how to ensure accuracy and explainability of information.
  </Card>
</CardGroup>


---
title: Ticket routing
url: https://platform.claude.com/docs/en/about-claude/use-case-guides/ticket-routing
description: This guide walks through how to harness Claude's advanced natural language understanding capabilities to classify customer support tickets at scale based on customer intent, urgency, prioritization, customer profile, and more.
---


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-23

* A Claude API key and the Python SDK installed
* Access to, and familiarity with, your existing support ticketing system
* A sample set of historical support tickets for testing


## Define whether to use Claude for ticket routing

Source: https://platform.claude.com/llms-full.txt#define-whether-to-use-claude-for-ticket-routing

Here are some key indicators that you should use an LLM like Claude instead of traditional ML approaches for your classification task:

<AccordionGroup>
  <Accordion title="You have limited labeled training data available">
    Traditional ML processes require massive labeled datasets. Claude's pre-trained model can effectively classify tickets with just a few dozen labeled examples, significantly reducing data preparation time and costs.
  </Accordion>

  <Accordion title="Your classification categories are likely to change or evolve over time">
    Once a traditional ML approach has been established, changing it is a laborious and data-intensive undertaking. On the other hand, as your product or customer needs evolve, Claude can easily adapt to changes in class definitions or new classes without extensive relabeling of training data.
  </Accordion>

  <Accordion title="You need to handle complex, unstructured text inputs">
    Traditional ML models often struggle with unstructured data and require extensive feature engineering. Claude's advanced language understanding allows for accurate classification based on content and context, rather than relying on strict ontological structures.
  </Accordion>

  <Accordion title="Your classification rules are based on semantic understanding">
    Traditional ML approaches often rely on bag-of-words models or simple pattern matching. Claude excels at understanding and applying underlying rules when classes are defined by conditions rather than examples.
  </Accordion>

  <Accordion title="You require interpretable reasoning for classification decisions">
    Many traditional ML models provide little insight into their decision-making process. Claude can provide human-readable explanations for its classification decisions, building trust in the automation system and facilitating easy adaptation if needed.
  </Accordion>

  <Accordion title="You want to handle edge cases and ambiguous tickets more effectively">
    Traditional ML systems often struggle with outliers and ambiguous inputs, frequently misclassifying them or defaulting to a catch-all category. Claude's natural language processing capabilities allow it to better interpret context and nuance in support tickets, potentially reducing the number of misrouted or unclassified tickets that require manual intervention.
  </Accordion>

  <Accordion title="You need multilingual support without maintaining separate models">
    Traditional ML approaches typically require separate models or extensive translation processes for each supported language. Claude's multilingual capabilities allow it to classify tickets in various languages without the need for separate models or extensive translation processes, streamlining support for global customer bases.
  </Accordion>
</AccordionGroup>

***


## Build and deploy your LLM support workflow

Source: https://platform.claude.com/llms-full.txt#build-and-deploy-your-llm-support-workflow

### Understand your current support approach

Before you automate, it's crucial to understand your existing ticketing system. Start by investigating how your support team currently handles ticket routing.

Consider questions like:

* What criteria are used to determine what SLA/service offering is applied?
* Is ticket routing used to determine which tier of support or product specialist a ticket goes to?
* Are there any automated rules or workflows already in place? In what cases do they fail?
* How are edge cases or ambiguous tickets handled?
* How does the team prioritize tickets?

The more you know about how humans handle certain cases, the better you can work with Claude to do the task.

### Define user intent categories

A well-defined list of user intent categories is crucial for accurate support ticket classification with Claude. Claude’s ability to route tickets effectively within your system is directly proportional to how well-defined your system’s categories are.

Here are some example user intent categories and subcategories.

<AccordionGroup>
  <Accordion title="Technical issue">
    * Hardware problem
    * Software bug
    * Compatibility issue
    * Performance problem
  </Accordion>

  <Accordion title="Account management">
    * Password reset
    * Account access issues
    * Billing inquiries
    * Subscription changes
  </Accordion>

  <Accordion title="Product information">
    * Feature inquiries
    * Product compatibility questions
    * Pricing information
    * Availability inquiries
  </Accordion>

  <Accordion title="User guidance">
    * How-to questions
    * Feature usage assistance
    * Best practices advice
    * Troubleshooting guidance
  </Accordion>

  <Accordion title="Feedback">
    * Bug reports
    * Feature requests
    * General feedback or suggestions
    * Complaints
  </Accordion>

  <Accordion title="Order-related">
    * Order status inquiries
    * Shipping information
    * Returns and exchanges
    * Order modifications
  </Accordion>

  <Accordion title="Service request">
    * Installation assistance
    * Upgrade requests
    * Maintenance scheduling
    * Service cancellation
  </Accordion>

  <Accordion title="Security concerns">
    * Data privacy inquiries
    * Suspicious activity reports
    * Security feature assistance
  </Accordion>

  <Accordion title="Compliance and legal">
    * Regulatory compliance questions
    * Terms of service inquiries
    * Legal documentation requests
  </Accordion>

  <Accordion title="Emergency support">
    * Critical system failures
    * Urgent security issues
    * Time-sensitive problems
  </Accordion>

  <Accordion title="Training and education">
    * Product training requests
    * Documentation inquiries
    * Webinar or workshop information
  </Accordion>

  <Accordion title="Integration and API">
    * Integration assistance
    * API usage questions
    * Third-party compatibility inquiries
  </Accordion>
</AccordionGroup>

In addition to intent, ticket routing and prioritization may also be influenced by other factors such as urgency, customer type, SLAs, or language. Be sure to consider other routing criteria when building your automated routing system.

### Establish success criteria

Work with your support team to [define clear success criteria](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) with measurable benchmarks, thresholds, and goals.

Here are some standard criteria and benchmarks when using LLMs for support ticket routing:

<AccordionGroup>
  <Accordion title="Classification consistency">
    This metric assesses how consistently Claude classifies similar tickets over time. It's crucial for maintaining routing reliability. Measure this by periodically testing the model with a set of standardized inputs and aiming for a consistency rate of 95% or higher.
  </Accordion>

  <Accordion title="Adaptation speed">
    This measures how quickly Claude can adapt to new categories or changing ticket patterns. Test this by introducing new ticket types and measuring the time it takes for the model to achieve satisfactory accuracy (for example, >90%) on these new categories. Aim for adaptation within 50–100 sample tickets.
  </Accordion>

  <Accordion title="Multilingual handling">
    This assesses Claude's ability to accurately route tickets in multiple languages. Measure the routing accuracy across different languages, aiming for no more than a 5–10% drop in accuracy for non-primary languages.
  </Accordion>

  <Accordion title="Edge case handling">
    This evaluates Claude's performance on unusual or complex tickets. Create a test set of edge cases and measure the routing accuracy, aiming for at least 80% accuracy on these challenging inputs.
  </Accordion>

  <Accordion title="Bias mitigation">
    This measures Claude's fairness in routing across different customer demographics. Regularly audit routing decisions for potential biases, aiming for consistent routing accuracy (within 2–3%) across all customer groups.
  </Accordion>

  <Accordion title="Prompt efficiency">
    In situations where minimizing token count is crucial, this criteria assesses how well Claude performs with minimal context. Measure routing accuracy with varying amounts of context provided, aiming for 90%+ accuracy with just the ticket title and a brief description.
  </Accordion>

  <Accordion title="Explainability score">
    This evaluates the quality and relevance of Claude's explanations for its routing decisions. Human raters can score explanations on a scale (for example, 1–5), with the goal of achieving an average score of 4 or higher.
  </Accordion>
</AccordionGroup>

Here are some common success criteria that may be useful regardless of whether an LLM is used:

<AccordionGroup>
  <Accordion title="Routing accuracy">
    Routing accuracy measures how often tickets are correctly assigned to the appropriate team or individual on the first try. This is typically measured as a percentage of correctly routed tickets out of total tickets. Industry benchmarks often aim for 90–95% accuracy, though this can vary based on the complexity of the support structure.
  </Accordion>

  <Accordion title="Time-to-assignment">
    This metric tracks how quickly tickets are assigned after being submitted. Faster assignment times generally lead to quicker resolutions and improved customer satisfaction. Best-in-class systems often achieve average assignment times of under 5 minutes, with many aiming for near-instantaneous routing (which is possible with LLM implementations).
  </Accordion>

  <Accordion title="Rerouting rate">
    The rerouting rate indicates how often tickets need to be reassigned after initial routing. A lower rate suggests more accurate initial routing. Aim for a rerouting rate below 10%, with top-performing systems achieving rates as low as 5% or less.
  </Accordion>

  <Accordion title="First-contact resolution rate">
    This measures the percentage of tickets resolved during the first interaction with the customer. Higher rates indicate efficient routing and well-prepared support teams. Industry benchmarks typically range from 70–75%, with top performers achieving rates of 80% or higher.
  </Accordion>

  <Accordion title="Average handling time">
    Average handling time measures how long it takes to resolve a ticket from start to finish. Efficient routing can significantly reduce this time. Benchmarks vary widely by industry and complexity, but many organizations aim to keep average handling time under 24 hours for non-critical issues.
  </Accordion>

  <Accordion title="Customer satisfaction scores">
    Often measured through post-interaction surveys, these scores reflect overall customer happiness with the support process. Effective routing contributes to higher satisfaction. Aim for CSAT scores of 90% or higher, with top performers often achieving 95%+ satisfaction rates.
  </Accordion>

  <Accordion title="Escalation rate">
    This measures how often tickets need to be escalated to higher tiers of support. Lower escalation rates often indicate more accurate initial routing. Strive for an escalation rate below 20%, with best-in-class systems achieving rates of 10% or less.
  </Accordion>

  <Accordion title="Agent productivity">
    This metric looks at how many tickets agents can handle effectively after implementing the routing solution. Improved routing should increase productivity. Measure this by tracking tickets resolved per agent per day or hour, aiming for a 10–20% improvement after implementing a new routing system.
  </Accordion>

  <Accordion title="Self-service deflection rate">
    This measures the percentage of potential tickets resolved through self-service options before entering the routing system. Higher rates indicate effective pre-routing triage. Aim for a deflection rate of 20–30%, with top performers achieving rates of 40% or higher.
  </Accordion>

  <Accordion title="Cost per ticket">
    This metric calculates the average cost to resolve each support ticket. Efficient routing should help reduce this cost over time. While benchmarks vary widely, many organizations aim to reduce cost per ticket by 10–15% after implementing an improved routing system.
  </Accordion>
</AccordionGroup>

### Choose the right Claude model

The choice of model depends on the trade-offs between cost, accuracy, and response time.

Many customers have found `claude-haiku-4-5-20251001` an ideal model for ticket routing, as it is the fastest and most cost-effective model in the Claude 4 family while still delivering excellent results. If your classification problem requires deep subject matter expertise or a large volume of intent categories, or complex reasoning, you may opt for the [larger Sonnet model](https://platform.claude.com/docs/en/about-claude/models).

### Build a strong prompt

Ticket routing is a type of classification task. Claude analyzes the content of a support ticket and classifies it into predefined categories based on the issue type, urgency, required expertise, or other relevant factors.

Write a ticket classification prompt. The initial prompt should contain the contents of the user request and return both the reasoning and the intent.

<Tip>
  Try the [metaprompt recipe from the Claude Cookbook](https://colab.research.google.com/github/anthropics/claude-cookbooks/blob/main/misc/metaprompt.ipynb) to have Claude write a first draft for you.
</Tip>

Here's an example ticket routing classification prompt:

Here are the key components of this prompt:

* The prompt template is a Python f-string, allowing the `ticket_contents` to be inserted into the `<request>` tags.
* The prompt gives Claude a clearly defined role as a classification system that carefully analyzes the ticket content to determine the customer's core intent and needs.
* The prompt instructs Claude on proper output formatting, in this case to provide its reasoning and analysis inside `<reasoning>` tags, followed by the appropriate classification label inside `<intent>` tags.
* The prompt specifies the valid intent categories: "Support, Feedback, Complaint", "Order Tracking", and "Refund/Exchange".
* The prompt includes a few examples (a.k.a. few-shot prompting) to illustrate how the output should be formatted, which improves accuracy and consistency.

Having Claude split its response into separate XML tag sections lets you use regular expressions to extract the reasoning and intent from the output independently. This lets you create targeted next steps in the ticket routing workflow, such as using only the intent to decide which person to route the ticket to.

### Deploy your prompt

It’s hard to know how well your prompt works without deploying it in a test production setting and [running evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests).

Build the deployment structure. Start by defining the method signature for wrapping the call to Claude. Extend the method you began writing earlier, which takes `ticket_contents` as input, so that it now returns a tuple of `reasoning` and `intent` as output. If you have an existing automation using traditional ML, you'll want to follow that method signature instead.

```python Python
import re

# Create an instance of the Claude API client
client = anthropic.Anthropic()

# Set the default model
DEFAULT_MODEL = "claude-haiku-4-5-20251001"


def classify_support_request(ticket_contents):
    # Define the prompt for the classification task
    classification_prompt = f"""You will be acting as a customer support ticket classification system.
        ...
        ... The reasoning should be enclosed in <reasoning> tags and the intent in <intent> tags. Return only the reasoning and the intent.
        """
    # Send the prompt to the API to classify the support request.
    message = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": classification_prompt}],
        stream=False,
    )
    reasoning_and_intent = message.content[0].text

    # Use Python's regular expressions library to extract `reasoning`.
    reasoning_match = re.search(
        r"<reasoning>(.*?)</reasoning>", reasoning_and_intent, re.DOTALL
    )
    reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

    # Similarly, also extract the `intent`.
    intent_match = re.search(r"<intent>(.*?)</intent>", reasoning_and_intent, re.DOTALL)
    intent = intent_match.group(1).strip() if intent_match else ""

    return reasoning, intent
```

This code:

* Creates a client instance using your API key.
* Defines a `classify_support_request` function that takes a `ticket_contents` string.
* Sends the `ticket_contents` to Claude for classification using the `classification_prompt`.
* Returns the model's `reasoning` and `intent` extracted from the response.

Because the entire reasoning and intent text must be generated before parsing, the example sets `stream=False` (the default).

***


## Evaluate your prompt

Source: https://platform.claude.com/llms-full.txt#evaluate-your-prompt

Prompting often requires testing and optimization for it to be production ready. To determine the readiness of your solution, evaluate performance based on the success criteria and thresholds you established earlier.

To run your evaluation, you need test cases to run it on. The rest of this guide assumes you have already [developed your test cases](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests).

### Build an evaluation function

The example evaluation for this guide measures Claude’s performance along three key metrics:

* Accuracy
* Cost per classification

You may need to assess Claude on other axes depending on what factors that are important to you.

To assess this, first modify the script to add a function that compares the predicted intent with the actual intent and calculates the percentage of correct predictions. Then add cost calculation and time measurement functionality.

```python Python
import re

# Create an instance of the Claude API client
client = anthropic.Anthropic()

# Set the default model
DEFAULT_MODEL = "claude-haiku-4-5-20251001"


def classify_support_request(request, actual_intent):
    # Define the prompt for the classification task
    classification_prompt = f"""You will be acting as a customer support ticket classification system.
        ...
        ...The reasoning should be enclosed in <reasoning> tags and the intent in <intent> tags. Return only the reasoning and the intent.
        """

    message = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": classification_prompt}],
    )
    usage = message.usage  # Get the usage statistics for the API call for how many input and output tokens were used.
    reasoning_and_intent = message.content[0].text

    # Use Python's regular expressions library to extract `reasoning`.
    reasoning_match = re.search(
        r"<reasoning>(.*?)</reasoning>", reasoning_and_intent, re.DOTALL
    )
    reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

    # Similarly, also extract the `intent`.
    intent_match = re.search(r"<intent>(.*?)</intent>", reasoning_and_intent, re.DOTALL)
    intent = intent_match.group(1).strip() if intent_match else ""

    # Check if the model's prediction is correct.
    correct = actual_intent.strip() == intent.strip()

    # Return the reasoning, intent, correct, and usage.
    return reasoning, intent, correct, usage
```

Here is a breakdown of the edits:

* The `classify_support_request` method now takes the `actual_intent` from the test cases and compares it against Claude’s intent classification to assess whether they match.
* The method extracts usage statistics for the API call to calculate cost based on input and output tokens used.

### Run your evaluation

A proper evaluation requires clear thresholds and benchmarks to determine what is a good result. The preceding script returns the runtime values for accuracy, response time, and cost per classification, but you still need clearly established thresholds. For example:

* **Accuracy:** 95% (out of 100 tests)
* **Cost per classification:** 50% reduction on average (across 100 tests) from current routing method

Having these thresholds allows you to quickly and easily tell at scale, and with impartial empiricism, what method is best for you and what changes might need to be made to better fit your requirements.

***


## Improve performance

Source: https://platform.claude.com/llms-full.txt#improve-performance-3

In complex scenarios, it may be helpful to consider additional strategies to improve performance beyond standard [prompt engineering techniques](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) & [guardrail implementation strategies](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations). Here are some common scenarios:

### Use a taxonomic hierarchy for cases with 20+ intent categories

As the number of classes grows, the number of examples required also expands, potentially making the prompt unwieldy. As an alternative, you can consider implementing a hierarchical classification system using a mixture of classifiers.

1. Organize your intents in a taxonomic tree structure.
2. Create a series of classifiers at every level of the tree, enabling a cascading routing approach.

For example, you might have a top-level classifier that broadly categorizes tickets into "Technical Issues," "Billing Questions," and "General Inquiries." Each of these categories can then have its own sub-classifier to further refine the classification.

![Classifier hierarchy routing tickets to Technical Issues, Billing Questions, or General Inquiries, each with a sub-classifier](https://platform.claude.com/docs/images/ticket-hierarchy.png)

* **Pros - greater nuance and accuracy:** You can create different prompts for each parent path, allowing for more targeted and context-specific classification. This can lead to improved accuracy and more nuanced handling of customer requests.

* **Cons - increased latency:** Be advised that multiple classifiers can lead to increased latency, and Anthropic recommends implementing this approach with the fastest model, Haiku.

### Use vector databases and similarity search retrieval to handle highly variable tickets

Despite providing examples being the most effective way to improve performance, if support requests are highly variable, it can be hard to include enough examples in a single prompt.

In this scenario, you could employ a vector database to do similarity searches from a dataset of examples and retrieve the most relevant examples for a given query.

This approach, outlined in detail in the [classification recipe](https://platform.claude.com/cookbook/capabilities-classification-guide), has been shown to improve performance from 71% accuracy to 93% accuracy.

### Account specifically for expected edge cases

Here are some scenarios where Claude may misclassify tickets (there may be others that are unique to your situation). In these scenarios, consider providing explicit instructions or examples in the prompt of how Claude should handle the edge case:

<AccordionGroup>
  <Accordion title="Customers make implicit requests">
    Customers often express needs indirectly. For example, "I've been waiting for my package for over two weeks now" may be an indirect request for order status.

    * **Solution:** Provide Claude with some real customer examples of these kinds of requests, along with what the underlying intent is. You can get even better results if you include a classification rationale for particularly nuanced ticket intents, so that Claude can better generalize the logic to other tickets.
  </Accordion>

  <Accordion title="Claude prioritizes emotion over intent">
    When customers express dissatisfaction, Claude may prioritize addressing the emotion over solving the underlying problem.

    * **Solution:** Provide Claude with directions on when to prioritize customer sentiment or not. It can be something as simple as “Ignore all customer emotions. Focus only on analyzing the intent of the customer’s request and what information the customer might be asking for.”
  </Accordion>

  <Accordion title="Multiple issues cause issue prioritization confusion">
    When customers present multiple issues in a single interaction, Claude may have difficulty identifying the primary concern.

    * **Solution:** Clarify the prioritization of intents so that Claude can better rank the extracted intents and identify the primary concern.
  </Accordion>
</AccordionGroup>

***


## Integrate Claude into your greater support workflow

Source: https://platform.claude.com/llms-full.txt#integrate-claude-into-your-greater-support-workflow

Proper integration requires that you make some decisions regarding how your Claude-based ticket routing script fits into the architecture of your greater ticket routing system. There are two ways you could do this:

* **Push-based:** The support ticket system you’re using (for example, Zendesk) triggers your code by sending a webhook event to your routing service, which then classifies the intent and routes it.
  * This approach is more web-scalable, but needs you to expose a public endpoint.
* **Pull-based:** Your code pulls for the latest tickets based on a given schedule and routes them at pull time.
  * This approach is easier to implement but might make unnecessary calls to the support ticket system when the pull frequency is too high or might be overly slow when the pull frequency is too low.

For either of these approaches, you need to wrap your script in a service. The choice of approach depends on what APIs your support ticketing system provides.

***

<CardGroup cols={2}>
  <Card title="Classification cookbook" icon="link" href="https://platform.claude.com/cookbook/capabilities-classification-guide">
    Visit the classification cookbook for more example code and detailed eval guidance.
  </Card>

  <Card title="Claude Console" icon="link" href="https://platform.claude.com/dashboard">
    Begin building and evaluating your workflow on the Claude Console.
  </Card>
</CardGroup>


### Prompt engineering

---
title: Prompt engineering overview
url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview
description: Learn when prompt engineering is the right solution, and find Claude prompting techniques and interactive tutorials.
---


## Before prompt engineering

Source: https://platform.claude.com/llms-full.txt#before-prompt-engineering

This guide assumes that you have:

1. A clear definition of the success criteria for your use case
2. Some ways to empirically test against those criteria
3. A first draft prompt you want to improve

If not, spend time establishing that first. Check out [Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) for tips and guidance.

<CardGroup cols={2}>
  <Card title="Prompt generator notebook" icon="link" href="https://colab.research.google.com/github/anthropics/claude-cookbooks/blob/main/misc/metaprompt.ipynb">
    Don't have a first draft prompt? Generate one with the metaprompt recipe from the Claude Cookbook.
  </Card>

  <Card title="Prompting best practices" icon="link" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices">
    For model-specific tuning guidance for Claude's latest models, start here.
  </Card>
</CardGroup>

***


## When to prompt engineer

Source: https://platform.claude.com/llms-full.txt#when-to-prompt-engineer

This guide focuses on success criteria that are controllable through prompt engineering. Not every success criteria or failing eval is best solved by prompt engineering. For example, you can sometimes improve latency and cost more easily by selecting a different model.

***


## How to prompt engineer

Source: https://platform.claude.com/llms-full.txt#how-to-prompt-engineer

All prompting techniques (from clarity and examples to XML structuring, role prompting, thinking, and prompt chaining) are covered in [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices). That's the living reference; start there.

For general prompt engineering craft beyond Claude-specific techniques, see the blog post on [best practices for prompt engineering](https://claude.com/blog/best-practices-for-prompt-engineering).

***


## Prompt engineering tutorial

Source: https://platform.claude.com/llms-full.txt#prompt-engineering-tutorial

If you're an interactive learner, you can start with the interactive tutorials instead!

<CardGroup cols={2}>
  <Card title="GitHub prompting tutorial" icon="link" href="https://github.com/anthropics/prompt-eng-interactive-tutorial">
    An example-filled tutorial that covers the prompt engineering concepts found in the docs.
  </Card>

  <Card title="Google Sheets prompting tutorial" icon="link" href="https://docs.google.com/spreadsheets/d/19jzLgRruG9kjUQNKtCg1ZjdD6l6weA6qRXG5zLIAhC8">
    A lighter-weight version of the prompt engineering tutorial, as an interactive spreadsheet.
  </Card>
</CardGroup>


---
title: Prompting best practices
url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
description: Comprehensive guide to prompt engineering techniques for Claude's latest models, covering clarity, examples, XML structuring, thinking, and agentic systems.
---

This is the reference for prompt engineering with current Claude models, including Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, Claude Opus 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, Claude Sonnet 4.6, and Claude Haiku 4.5. The page is organized in three parts:

* **[Model-specific guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#model-specific-guidance)** first: where a single model behaves differently and what to change in your prompt.
* **Techniques for all current models** after that: general principles, output and formatting, tool use, thinking, and agentic systems.
* **Migration considerations** last, for prompts moving from earlier generations.

<Tip>
  For an overview of model capabilities, see the [models overview](https://platform.claude.com/docs/en/models/overview). For Claude Fable 5.1 capabilities and API changes, see [What's new in Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1). For Claude Fable 5 capabilities and API changes, see [Introducing Claude Fable 5 and Claude Mythos 5](https://platform.claude.com/docs/en/models/fable-5/introducing-claude-fable-5-and-claude-mythos-5). For details on what's new in Claude Sonnet 5, see [What's new in Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5). For details on what's new in Claude Opus 5, see [What's new in Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/whats-new-opus-5). For migration guidance, see the [Migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide).
</Tip>


## Model-specific guidance

Source: https://platform.claude.com/llms-full.txt#model-specific-guidance

Each of these models has its own prompting page. Read the one for your model first, then the techniques that follow.

| Model                                  | Guide                                                                                                                             | What's different                                                                                                                                                                                                                                 |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Claude Fable 5.1 and Claude Mythos 5.1 | [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1) | Differences from Claude Fable 5: effort levels, finishing long tasks, user-facing progress updates, passing thinking blocks back unchanged, tool-call batching in agent loops, search triggering at low effort, formatting, and writing density. |
| Claude Fable 5 and Claude Mythos 5     | [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)     | Differences from Claude Opus 4.8: effort levels, instruction following, long-run progress claims, memory systems, and the `reasoning_extraction` refusal category.                                                                               |
| Claude Sonnet 5                        | [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)   | Differences from Claude Sonnet 4.6: response length, effort and thinking-depth calibration, tool use triggering, literal instruction following, and design and frontend defaults.                                                                |
| Claude Opus 5                          | [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)       | Differences from prior Opus models: response length and verbosity, user-facing progress updates, written deliverable length, task scope and over-verification, subagent control, and self-correction.                                            |
| Claude Opus 4.8                        | [Prompting Claude Opus 4.8](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8)   | Response length, effort and thinking-depth calibration, tool use triggering, literal instruction following, subagent control, and design and frontend defaults.                                                                                  |


## General principles

Source: https://platform.claude.com/llms-full.txt#general-principles

The techniques in this section and the sections that follow apply to current Claude models, including Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, and Claude Mythos 5. Where a technique names a specific model, treat it as measured on that model and re-check it against your own evals before applying it to another.

### Be clear and direct

Claude responds well to clear, explicit instructions. Being specific about your desired output can help enhance results. If you want "above and beyond" behavior, explicitly request it rather than relying on the model to infer this from vague prompts.

Think of Claude as a brilliant but new employee who lacks context on your norms and workflows. The more precisely you explain what you want, the better the result.

**Golden rule:** Show your prompt to a colleague with minimal context on the task and ask them to follow it. If they'd be confused, Claude will be too.

* Be specific about the desired output format and constraints.
* Provide instructions as sequential steps using numbered lists or bullet points when the order or completeness of steps matters.

<Accordion title="Example: Creating an analytics dashboard" defaultOpen>
  **Less effective:**

  ```text wrap
  Create an analytics dashboard

text wrap
  Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to create a fully-featured implementation.

text wrap
  NEVER use ellipses

text wrap
  Your response will be read aloud by a text-to-speech engine, so never use ellipses since the text-to-speech engine will not know how to pronounce them.

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "system": "You are a helpful coding assistant specializing in Python.",
      "messages": [
        {"role": "user", "content": "How do I sort a list of dictionaries by key?"}
      ]
    }'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --system "You are a helpful coding assistant specializing in Python." \
    --message '{role: user, content: "How do I sort a list of dictionaries by key?"}'

python Python
  client = anthropic.Anthropic()

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      system="You are a helpful coding assistant specializing in Python.",
      messages=[
          {"role": "user", "content": "How do I sort a list of dictionaries by key?"}
      ],
  )

  print(message.content)

typescript TypeScript
  const client = new Anthropic();

  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    system: "You are a helpful coding assistant specializing in Python.",
    messages: [{ role: "user", content: "How do I sort a list of dictionaries by key?" }]
  });

  console.log(message.content);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      System = "You are a helpful coding assistant specializing in Python.",
      Messages =
      [
          new() { Role = Role.User, Content = "How do I sort a list of dictionaries by key?" }
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	System: []anthropic.TextBlockParam{
  		{Text: "You are a helpful coding assistant specializing in Python."},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("How do I sort a list of dictionaries by key?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(message.Content)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024)
      .system("You are a helpful coding assistant specializing in Python.")
      .addUserMessage("How do I sort a list of dictionaries by key?")
      .build();

  Message message = client.messages().create(params);
  System.out.println(message.content());

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => 'How do I sort a list of dictionaries by key?']
      ],
      model: 'claude-opus-5',
      system: 'You are a helpful coding assistant specializing in Python.',
  );

  echo json_encode($message->content, JSON_PRETTY_PRINT), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    system: "You are a helpful coding assistant specializing in Python.",
    messages: [
      { role: "user", content: "How do I sort a list of dictionaries by key?" }
    ]
  )

  puts message.content

xml
    <documents>
      <document index="1">
        <source>annual_report_2023.pdf</source>
        <document_content>
          {{ANNUAL_REPORT}}
        </document_content>
      </document>
      <document index="2">
        <source>competitor_analysis_q2.xlsx</source>
        <document_content>
          {{COMPETITOR_ANALYSIS}}
        </document_content>
      </document>
    </documents>

    Analyze the annual report and competitor analysis. Identify strategic advantages and recommend Q3 focus areas.

xml
    You are an AI physician's assistant. Your task is to help doctors diagnose possible patient illnesses.

    <documents>
      <document index="1">
        <source>patient_symptoms.txt</source>
        <document_content>
          {{PATIENT_SYMPTOMS}}
        </document_content>
      </document>
      <document index="2">
        <source>patient_records.txt</source>
        <document_content>
          {{PATIENT_RECORDS}}
        </document_content>
      </document>
      <document index="3">
        <source>patient01_appt_history.txt</source>
        <document_content>
          {{PATIENT01_APPOINTMENT_HISTORY}}
        </document_content>
      </document>
    </documents>

    Find quotes from the patient records and appointment history that are relevant to diagnosing the patient's reported symptoms. Place these in <quotes> tags. Then, based on these quotes, list all information that would help the doctor diagnose the patient's symptoms. Place your diagnostic information in <info> tags.

text Sample prompt for model identity wrap
The assistant is Claude, created by Anthropic. The current model is Claude Opus 5.

text Sample prompt for model string wrap
When an LLM is needed, please default to Claude Opus 5 unless the user requests
otherwise. The exact model string for Claude Opus 5 is claude-opus-5.
```


## Output and formatting

Source: https://platform.claude.com/llms-full.txt#output-and-formatting

### Communication style and verbosity

Claude's latest models have a more concise and natural communication style compared to previous models:

* **More direct and grounded:** Provides fact-based progress reports rather than self-celebratory updates
* **More conversational:** Slightly more fluent and colloquial, less machine-like
* **Less verbose:** May skip detailed summaries for efficiency unless prompted otherwise

This means Claude may skip verbal summaries after tool calls, jumping directly to the next action. If you prefer more visibility into its reasoning:

```text Sample prompt wrap
After completing a task that involves tool use, provide a quick summary of the work you've done.

`text Sample prompt to minimize markdown wrap
<avoid_excessive_markdown_and_bullet_points>
When writing reports, documents, technical explanations, analyses, or any long-form
content, write in clear, flowing prose using complete paragraphs and sentences. Use
standard paragraph breaks for organization and reserve markdown primarily for `inline
code`, code blocks (```...```), and simple headings (## and ###). Avoid using **bold**
and *italics*.

DO NOT use ordered lists (1. ...) or unordered lists (*) unless: a) you're presenting
truly discrete items where a list format is the best option, or b) the user explicitly
requests a list or ranking

Instead of listing items with bullets or numbers, incorporate them naturally into
sentences. This guidance applies especially to technical writing. Using prose instead of
excessive formatting will improve user satisfaction. NEVER output a series of overly
short bullet points.

Your goal is readable, flowing text that guides the reader naturally through ideas
rather than fragmenting information into isolated points.
</avoid_excessive_markdown_and_bullet_points>
`

text Sample prompt wrap
Format your response in plain text only. Do not use LaTeX, MathJax, or any markup
notation such as \( \), $, or \frac{}{}. Write all math expressions using standard text
characters (e.g., "/" for division, "*" for multiplication, and "^" for exponents).

text Sample prompt wrap
Create a professional presentation on [topic]. Include thoughtful design elements,
visual hierarchy, and engaging animations where appropriate.
```

### Migrating away from prefilled responses

Starting with Claude 4.6 models and [Claude Mythos Preview](https://anthropic.com/glasswing), prefilled responses (providing a partial assistant message for Claude to continue from) on the last assistant turn are no longer supported. Requests with prefilled assistant messages to these models return a 400 error. Model intelligence and instruction following have advanced such that most use cases of prefill no longer require it. Earlier models continue to support prefills, and adding assistant messages elsewhere in the conversation is not affected.

Here are common prefill scenarios and how to migrate away from them:

<Accordion title="Controlling output formatting">
  Prefills have been used to force specific output formats like JSON/YAML, classification, and similar patterns where the prefill constrains Claude to a particular structure.

  **Migration:** The [Structured Outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) feature is designed specifically to constrain Claude's responses to follow a given schema. Try asking the model to conform to your output structure first, as newer models can reliably match complex schemas when told to, especially if implemented with retries. For classification tasks, use either tools with an enum field containing your valid labels or structured outputs.
</Accordion>

<Accordion title="Eliminating preambles">
  Prefills like `Here is the requested summary:\n` were used to skip introductory text.

  **Migration:** Use direct instructions in the system prompt: "Respond directly without preamble. Do not start with phrases like 'Here is...', 'Based on...', etc." Alternatively, direct the model to output within XML tags, use structured outputs, or use tool calling. If the occasional preamble slips through, strip it in post-processing.
</Accordion>

<Accordion title="Avoiding bad refusals">
  Prefills were used to steer around unnecessary refusals.

  **Migration:** Claude is much better at appropriate refusals now. Clear prompting within the `user` message without prefill should be sufficient.
</Accordion>

<Accordion title="Continuations">
  Prefills were used to continue partial completions, resume interrupted responses, or pick up where a previous generation left off.

  **Migration:** Move the continuation to the user message, and include the final text from the interrupted response: "Your previous response was interrupted and ended with \`\[previous\_response]\`. Continue from where you left off." If this is part of error-handling or incomplete-response-handling and there is no UX penalty, retry the request.
</Accordion>

<Accordion title="Context hydration and role consistency">
  Prefills were used to periodically ensure refreshed or injected context.

  **Migration:** For very long conversations, inject what were previously prefilled-assistant reminders into the user turn. If context hydration is part of a more complex agentic system, consider hydrating through tools (expose or encourage use of tools containing context based on heuristics such as number of turns) or during [context compaction](https://platform.claude.com/docs/en/build-with-claude/compaction).
</Accordion>


## Tool use

Source: https://platform.claude.com/llms-full.txt#tool-use

### Tool usage

Claude's latest models are trained for precise instruction following and benefit from explicit direction to use specific tools. If you say "can you suggest some changes," Claude will sometimes provide suggestions rather than implementing them, even if making changes might be what you intended. To learn how to define tools and troubleshoot tool triggering, see [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).

For Claude to take action, be more explicit:

<Accordion title="Example: Explicit instructions" defaultOpen>
  **Less effective (Claude will only suggest):**

  ```text wrap
  Can you suggest some changes to improve this function?

text wrap
  Change this function to improve its performance.

text wrap
  Make these edits to the authentication flow.

text Sample prompt for proactive action wrap
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's intent is
unclear, infer the most useful likely action and proceed, using tools to discover any
missing details instead of guessing. Try to infer the user's intent about whether a tool
call (e.g., file edit or read) is intended or not, and act accordingly.
</default_to_action>

text Sample prompt for conservative action wrap
<do_not_act_before_instructions>
Do not jump into implementation or change files unless clearly instructed to make
changes. When the user's intent is ambiguous, default to providing information, doing
research, and providing recommendations rather than taking action. Only proceed with
edits, modifications, or implementations when the user explicitly requests them.
</do_not_act_before_instructions>

text Sample prompt for maximum parallel efficiency wrap
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between the tool
calls, make all of the independent tool calls in parallel. Prioritize calling tools
simultaneously whenever the actions can be done in parallel rather than sequentially.
For example, when reading 3 files, run 3 tool calls in parallel to read all 3 files into
context at the same time. Maximize use of parallel tool calls where possible to increase
speed and efficiency. However, if some tool calls depend on previous calls to inform
dependent values like the parameters, do NOT call these tools in parallel and instead
call them sequentially. Never use placeholders or guess missing parameters in tool
calls.
</use_parallel_tool_calls>

text Sample prompt to reduce parallel execution wrap
Execute operations sequentially with brief pauses between each step to ensure stability.
```

On Claude Fable 5.1 in long agent loops, send the parallel-calls instruction as a turn-scoped system message after each round of tool results. See [Batch independent tool calls in agent loops](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#batch-independent-tool-calls-in-agent-loops).


## Thinking and reasoning

Source: https://platform.claude.com/llms-full.txt#thinking-and-reasoning

### Overthinking and excessive thoroughness

Claude Opus 4.6 does more upfront exploration than previous models, especially at higher [`effort`](https://platform.claude.com/docs/en/build-with-claude/effort) settings. This initial work often helps to optimize the final results, but the model may gather extensive context or pursue multiple threads of research without being prompted. If your prompts previously encouraged the model to be more thorough, you should tune that guidance for Claude Opus 4.6:

* **Replace blanket defaults with more targeted instructions.** Instead of "Default to using \[tool]," add guidance like "Use \[tool] when it would enhance your understanding of the problem."
* **Remove over-prompting.** Tools that undertriggered in previous models are likely to trigger appropriately now. Instructions like "If in doubt, use \[tool]" will cause overtriggering.
* **Use effort as a fallback.** If Claude continues to be overly aggressive, use a lower setting for `effort`.

In some cases, Claude Opus 4.6 may think extensively, which can inflate thinking tokens and slow down responses. If this behavior is undesirable, you can add explicit instructions to constrain its reasoning, or you can lower the `effort` setting to reduce overall thinking and token usage.

```text Sample prompt wrap
When you're deciding how to approach a problem, choose an approach and commit to it.
Avoid revisiting decisions unless you encounter new information that directly
contradicts your reasoning. If you're weighing two approaches, pick one and see it
through. You can always course-correct later if the chosen approach fails.

text Example prompt wrap
After receiving tool results, carefully reflect on their quality and determine optimal
next steps before proceeding. Use your thinking to plan and iterate based on this new
information, and then take the best next action.

text Sample prompt wrap
Thinking adds latency and should only be used when it will meaningfully improve
answer quality - typically for problems that require multistep reasoning. When in
doubt, respond directly.

bash cURL
  # Before: extended thinking with a manual budget (older models)
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-sonnet-4-5-20250929",
      "max_tokens": 16000,
      "thinking": {"type": "enabled", "budget_tokens": 10000},
      "messages": [
        {"role": "user", "content": "..."}
      ]
    }'

  # After: adaptive thinking with effort
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-4-8",
      "max_tokens": 16000,
      "thinking": {"type": "adaptive"},
      "output_config": {"effort": "high"},
      "messages": [
        {"role": "user", "content": "..."}
      ]
    }'

bash CLI
  # Before: extended thinking with a manual budget (older models)
  ant messages create <<'YAML'
  model: claude-sonnet-4-5-20250929
  max_tokens: 16000
  thinking:
    type: enabled
    budget_tokens: 10000
  messages:
    - role: user
      content: "..."
  YAML

  # After: adaptive thinking with effort
  ant messages create <<'YAML'
  model: claude-opus-4-8
  max_tokens: 16000
  thinking:
    type: adaptive
  output_config:
    effort: high
  messages:
    - role: user
      content: "..."
  YAML

python Python
  # Before: extended thinking with a manual budget (older models)
  client.messages.create(
      model="claude-sonnet-4-5-20250929",
      max_tokens=16000,
      thinking={"type": "enabled", "budget_tokens": 10000},
      messages=[{"role": "user", "content": "..."}],
  )

  # After: adaptive thinking with effort
  client.messages.create(
      model="claude-opus-4-8",
      max_tokens=16000,
      thinking={"type": "adaptive"},
      output_config={"effort": "high"},
      messages=[{"role": "user", "content": "..."}],
  )

typescript TypeScript
  // Before: extended thinking with a manual budget (older models)
  await client.messages.create({
    model: "claude-sonnet-4-5-20250929",
    max_tokens: 16000,
    thinking: { type: "enabled", budget_tokens: 10000 },
    messages: [{ role: "user", content: "..." }]
  });

  // After: adaptive thinking with effort
  await client.messages.create({
    model: "claude-opus-4-8",
    max_tokens: 16000,
    thinking: { type: "adaptive" },
    output_config: { effort: "high" },
    messages: [{ role: "user", content: "..." }]
  });

csharp C#
  // Before: extended thinking with a manual budget (older models)
  await client.Messages.Create(new MessageCreateParams
  {
      Model = "claude-sonnet-4-5-20250929",
      MaxTokens = 16000,
      Thinking = new ThinkingConfigEnabled(budgetTokens: 10000),
      Messages = [new() { Role = Role.User, Content = "..." }]
  });

  // After: adaptive thinking with effort
  await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus4_8,
      MaxTokens = 16000,
      Thinking = new ThinkingConfigAdaptive(),
      OutputConfig = new OutputConfig { Effort = Effort.High },
      Messages = [new() { Role = Role.User, Content = "..." }]
  });

go Go
  // Before: extended thinking with a manual budget (older models)
  client.Messages.New(ctx, anthropic.MessageNewParams{
  	Model:     "claude-sonnet-4-5-20250929",
  	MaxTokens: 16000,
  	Thinking: anthropic.ThinkingConfigParamUnion{
  		OfEnabled: &anthropic.ThinkingConfigEnabledParam{BudgetTokens: 10000},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("...")),
  	},
  })

  // After: adaptive thinking with effort
  client.Messages.New(ctx, anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus4_8,
  	MaxTokens: 16000,
  	Thinking: anthropic.ThinkingConfigParamUnion{
  		OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{},
  	},
  	OutputConfig: anthropic.OutputConfigParam{
  		Effort: anthropic.OutputConfigEffortHigh,
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("...")),
  	},
  })

java Java
  // Before: extended thinking with a manual budget (older models)
  client.messages().create(MessageCreateParams.builder()
      .model("claude-sonnet-4-5-20250929")
      .maxTokens(16000L)
      .thinking(ThinkingConfigEnabled.builder().budgetTokens(10000L).build())
      .addUserMessage("...")
      .build());

  // After: adaptive thinking with effort
  client.messages().create(MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_4_8)
      .maxTokens(16000L)
      .thinking(ThinkingConfigAdaptive.builder().build())
      .outputConfig(OutputConfig.builder()
          .effort(OutputConfig.Effort.HIGH)
          .build())
      .addUserMessage("...")
      .build());

php PHP
  // Before: extended thinking with a manual budget (older models)
  $client->messages->create(
      model: 'claude-sonnet-4-5-20250929',
      maxTokens: 16000,
      thinking: ['type' => 'enabled', 'budget_tokens' => 10000],
      messages: [['role' => 'user', 'content' => '...']],
  );

  // After: adaptive thinking with effort
  $client->messages->create(
      model: 'claude-opus-4-8',
      maxTokens: 16000,
      thinking: ['type' => 'adaptive'],
      outputConfig: ['effort' => 'high'],
      messages: [['role' => 'user', 'content' => '...']],
  );

ruby Ruby
  # Before: extended thinking with a manual budget (older models)
  client.messages.create(
    model: "claude-sonnet-4-5-20250929",
    max_tokens: 16000,
    thinking: { type: "enabled", budget_tokens: 10000 },
    messages: [{ role: "user", content: "..." }]
  )

  # After: adaptive thinking with effort
  client.messages.create(
    model: "claude-opus-4-8",
    max_tokens: 16000,
    thinking: { type: "adaptive" },
    output_config: { effort: "high" },
    messages: [{ role: "user", content: "..." }]
  )
  ```
</CodeGroup>

If you are not using extended thinking, no changes are required. On Claude Opus 4.6 through Claude Opus 4.8 and Claude Sonnet 4.6, thinking is off when you omit the `thinking` parameter. On Claude Opus 5 and Claude Sonnet 5, thinking is on by default when you omit the `thinking` parameter. On Claude Opus 5, you can disable it only at effort `high` or lower. On Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, and Claude Mythos 5, thinking is always on, regardless of whether you set the `thinking` parameter.

* **Prefer general instructions over prescriptive steps.** A prompt like "think thoroughly" often produces better reasoning than a hand-written step-by-step plan. Claude's reasoning frequently exceeds what a human would prescribe.
* **Multishot examples work with thinking.** Use `<thinking>` tags inside your few-shot examples to show Claude the reasoning pattern. It will generalize that style to its own extended thinking blocks.
* **Manual chain-of-thought (CoT) prompting as a fallback.** When thinking is off, you can still encourage step-by-step reasoning by asking Claude to think through the problem. Use structured tags like `<thinking>` and `<answer>` to cleanly separate reasoning from the final output. On Claude Opus 5, prefer keeping thinking enabled at a lower effort level instead: with thinking disabled, the model can occasionally emit internal XML tags into its visible output, so see [Running with thinking disabled](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#running-with-thinking-disabled) before applying this pattern there.
* **Ask Claude to self-check.** Append something like "Before you finish, verify your answer against \[test criteria]." This catches errors reliably, especially for coding and math. Claude Opus 5 is the exception: it verifies its own work well without explicit instruction, and verification instructions carried over from prompts tuned for earlier models can cause over-verification, adding tokens and latency. When migrating to Claude Opus 5, remove these instructions rather than rewriting them. See [Task scope and over-verification](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#task-scope-and-over-verification).

<Note>
  When extended thinking is disabled, Claude Opus 4.5 is particularly sensitive to the word "think" and its variants. Consider using alternatives like "consider," "evaluate," or "reason through" in those cases.
</Note>

<Info>
  For more information on thinking capabilities, see [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) and [Steering thinking](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost).
</Info>


## Agentic systems

Source: https://platform.claude.com/llms-full.txt#agentic-systems

### Long-horizon reasoning and state tracking

Claude's latest models handle long-horizon reasoning tasks with strong state tracking. Claude maintains orientation across extended sessions by focusing on incremental progress, making steady advances on a few things at a time rather than attempting everything at once. This capability especially emerges over multiple context windows or task iterations, where Claude can work on a complex task, save the state, and continue with a fresh context window.

#### Context awareness and multiwindow workflows

Claude Sonnet 5, Claude Sonnet 4.6, Claude Sonnet 4.5, and Claude Haiku 4.5 feature [context awareness](https://platform.claude.com/docs/en/build-with-claude/context-windows#context-awareness), enabling the model to track its remaining context window (that is, its "token budget") throughout a conversation. This enables Claude to execute tasks and manage context more effectively by understanding how much space it has to work.

**Managing context limits:**

If you are using Claude in an agent harness that compacts context or allows saving context to external files (like in Claude Code), consider adding this information to your prompt so Claude can behave accordingly. Otherwise, Claude may sometimes naturally try to wrap up work as it approaches the context limit. The following is an example prompt:

```text Sample prompt wrap
Your context window will be automatically compacted as it approaches its limit, allowing
you to continue working indefinitely from where you left off. Therefore, do not stop
tasks early due to token budget concerns. As you approach your token budget limit, save
your current progress and state to memory before the context window refreshes. Always be
as persistent and autonomous as possible and complete tasks fully, even if the end of
your budget is approaching. Never artificially stop any task early regardless of the
context remaining.

text Sample prompt wrap
This is a very long task, so it may be beneficial to plan out your work clearly. It's
encouraged to spend your entire output context working on the task - just make sure you
don't run out of context with significant uncommitted work. Continue working
systematically until you have completed this task.

json tests.json
  {
    "tests": [
      { "id": 1, "name": "authentication_flow", "status": "passing" },
      { "id": 2, "name": "user_management", "status": "failing" },
      { "id": 3, "name": "api_endpoints", "status": "not_started" }
    ],
    "total": 200,
    "passing": 150,
    "failing": 25,
    "not_started": 25
  }

text wrap
  // Progress notes (progress.txt)
  Session 3 progress:
  - Fixed authentication token validation
  - Updated user model to handle edge cases
  - Next: investigate user_management test failures (test #2)
  - Note: Do not remove tests as this could lead to missing functionality

text Sample prompt wrap
Consider the reversibility and potential impact of your actions. You are encouraged to
take local, reversible actions like editing files or running tests, but for actions that
are hard to reverse, affect shared systems, or could be destructive, ask the user before
proceeding.

Examples of actions that warrant confirmation:
- Destructive operations: deleting files or branches, dropping database tables, rm -rf
- Hard to reverse operations: git push --force, git reset --hard, amending published commits
- Operations visible to others: pushing code, commenting on PRs/issues, sending
messages, modifying shared infrastructure

When encountering obstacles, do not use destructive actions as a shortcut. For example,
don't bypass safety checks (e.g. --no-verify) or discard unfamiliar files that may be
in-progress work.

text Sample prompt for complex research wrap
Search for this information in a structured way. As you gather data, develop several
competing hypotheses. Track your confidence levels in your progress notes to improve
calibration. Regularly self-critique your approach and plan. Update a hypothesis tree or
research notes file to persist information and provide transparency. Break down this
complex research task systematically.

text Sample prompt for subagent usage wrap
Use subagents when tasks can run in parallel, require isolated context, or involve
independent workstreams that don't need to share state. For simple tasks, sequential
operations, single-file edits, or tasks where you need to maintain context across steps,
work directly rather than delegating.

text Sample prompt wrap
If you create any temporary new files, scripts, or helper files for iteration, clean up
these files by removing them at the end of the task.

text Sample prompt to minimize overengineering wrap
Avoid over-engineering. Only make changes that are directly requested or clearly
necessary. Keep solutions simple and focused:

- Scope: Don't add features, refactor code, or make "improvements" beyond what was
asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need
extra configurability.

- Documentation: Don't add docstrings, comments, or type annotations to code you didn't
change. Only add comments where the logic isn't self-evident.

- Defensive coding: Don't add error handling, fallbacks, or validation for scenarios
that can't happen. Trust internal code and framework guarantees. Only validate at system
boundaries (user input, external APIs).

- Abstractions: Don't create helpers, utilities, or abstractions for one-time
operations. Don't design for hypothetical future requirements. The right amount of
complexity is the minimum needed for the current task.

text Sample prompt wrap
Please write a high-quality, general-purpose solution using the standard tools
available. Do not create helper scripts or workarounds to accomplish the task more
efficiently. Implement a solution that works correctly for all valid inputs, not just
the test cases. Do not hard-code values or create solutions that only work for specific
test inputs. Instead, implement the actual logic that solves the problem generally.

Focus on understanding the problem requirements and implementing the correct algorithm.
Tests are there to verify correctness, not to define the solution. Provide a principled
implementation that follows best practices and software design principles.

If the task is unreasonable or infeasible, or if any of the tests are incorrect, please
inform me rather than working around them. The solution should be robust, maintainable,
and extendable.

text Sample prompt wrap
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a specific file,
you MUST read the file before answering. Make sure to investigate and read relevant
files BEFORE answering questions about the codebase. Never make any claims about code
before investigating unless you are certain of the correct answer - give grounded and
hallucination-free answers.
</investigate_before_answering>
```


## Capability-specific tips

Source: https://platform.claude.com/llms-full.txt#capability-specific-tips

### Improved vision capabilities

Claude Opus 4.5 and Claude Opus 4.6 have improved vision capabilities compared to previous Claude models. They perform better on image processing and data extraction tasks, particularly when there are multiple images present in context. These improvements carry over to computer use, where the models can more reliably interpret screenshots and UI elements. You can also use these models to analyze videos by breaking them up into frames.

One technique that has proven effective to further boost performance is to give Claude a crop tool or [agent skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview). Testing has shown consistent uplift on image evaluations when Claude is able to "zoom" in on relevant regions of an image. Anthropic has created a [recipe for the crop tool](https://platform.claude.com/cookbook/multimodal-crop-tool).

### Frontend design

Claude Opus 4.5 and Claude Opus 4.6 build complex, real-world web applications with strong frontend design. However, without guidance, models can default to generic patterns that create what users call the "AI slop" aesthetic. To create distinctive, creative frontends that surprise and delight:

<Tip>
  For a detailed guide on improving frontend design, see the blog post on [improving frontend design through skills](https://www.claude.com/blog/improving-frontend-design-through-skills).
</Tip>

For frontend design work outside the API, [Claude Design](https://support.claude.com/en/articles/14604416-get-started-with-claude-design) provides a canvas and design tools where Claude generates and iterates on designs interactively.

Here's a system prompt snippet you can use to encourage better frontend design:

```text Sample prompt for frontend aesthetics wrap
<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs. In frontend design, this
creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive
frontends that surprise and delight.

Focus on:
- Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic
fonts like Arial and Inter; opt instead for distinctive choices that elevate the
frontend's aesthetics.
- Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency.
Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw
from IDE themes and cultural aesthetics for inspiration.
- Motion: Use animations for effects and micro-interactions. Prioritize CSS-only
solutions for HTML. Use Motion library for React when available. Focus on high-impact
moments: one well-orchestrated page load with staggered reveals (animation-delay)
creates more delight than scattered micro-interactions.
- Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer
CSS gradients, use geometric patterns, or add contextual effects that match the overall
aesthetic.

Avoid generic AI-generated aesthetics:
- Overused font families (Inter, Roboto, Arial, system fonts)
- Clichéd color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Cookie-cutter design that lacks context-specific character

Interpret creatively and make unexpected choices that feel genuinely designed for the
context. Vary between light and dark themes, different fonts, different aesthetics. You
still tend to converge on common choices (Space Grotesk, for example) across
generations. Avoid this: it is critical that you think outside the box!
</frontend_aesthetics>
```

You can also refer to the [full skill definition](https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md).


## Migration considerations

Source: https://platform.claude.com/llms-full.txt#migration-considerations

When migrating to current Claude models from earlier generations:

1. **Be specific about desired behavior:** Consider describing exactly what you'd like to see in the output.

2. **Frame your instructions with modifiers:** Adding modifiers that encourage Claude to increase the quality and detail of its output can help better shape Claude's performance. For example, instead of "Create an analytics dashboard", use "Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to create a fully-featured implementation."

3. **Request specific features explicitly:** Animations and interactive elements should be requested explicitly when desired.

4. **Update thinking configuration:** Claude 4.6 models use [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) (`thinking: {type: "adaptive"}`) instead of manual thinking with `budget_tokens`. Use the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) to control thinking depth.

5. **Migrate away from prefilled responses:** Prefilled responses on the last assistant turn are no longer supported starting with Claude 4.6 models and Claude Mythos Preview. See [Migrating away from prefilled responses](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#migrating-away-from-prefilled-responses) for detailed guidance on alternatives.

6. **Tune anti-laziness prompting:** If your prompts previously encouraged the model to be more thorough or use tools more aggressively, dial back that guidance. Claude 4.6 models are more proactive and may overtrigger on instructions that were needed for previous models.

7. **Pass thinking blocks back unchanged and keep history append-only:** Append each assistant turn exactly as the API returned it, thinking blocks included. On Claude Fable 5.1, [modifying the conversation before a thinking block](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-in-conversation) results in an error, or in the block being dropped if you opt into that: editing earlier messages, rebuilding `system` or `tools`, or summarizing older turns in place between requests invalidates every later thinking block, so move those changes to mid-conversation system messages and server-side context management. See [Keep the conversation history append-only](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#keep-the-conversation-history-append-only).

For detailed migration steps, see the [Migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide).

### Migrating to Claude Sonnet 5 from Claude Sonnet 4.5 or earlier

See [Migrating to Claude Sonnet 5 from Claude Sonnet 4.5 or earlier](https://platform.claude.com/docs/en/models/sonnet-5/migration-guide#migrating-from-sonnet-45) in the migration guide, which covers the effort default change and the removal of manual extended thinking (`budget_tokens`).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-100

<CardGroup cols={2}>
  <Card title="Prompting Claude Fable 5.1" icon="terminal" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1">
    Behavioral differences and prompting patterns for Claude Fable 5.1, covering effort, task completion, progress updates, thinking blocks, tool-call batching, and writing style.
  </Card>

  <Card title="Prompting Claude Fable 5" icon="terminal" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5">
    Behavioral differences and prompting patterns for Claude Fable 5 and Claude Mythos 5, covering effort, instruction following, long runs, memory, and scaffolding changes.
  </Card>

  <Card title="Prompting Claude Sonnet 5" icon="terminal" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5">
    Behavioral differences and prompting patterns for Claude Sonnet 5, covering effort, adaptive thinking defaults, tool use, and migration from Claude Sonnet 4.6.
  </Card>

  <Card title="Prompting Claude Opus 5" icon="terminal" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5">
    Behavioral differences and prompting patterns for Claude Opus 5, covering response verbosity, agentic narration, task scoping, subagent delegation, and self-correction.
  </Card>

  <Card title="Prompt engineering overview" icon="edit" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview">
    When to use prompt engineering and how to plan your approach before tuning prompts.
  </Card>
</CardGroup>


---
title: Prompting Claude Fable 5
url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
description: Behavioral differences and prompting patterns for Claude Fable 5 and Claude Mythos 5, covering effort, instruction following, long runs, memory, and scaffolding changes.
---

This guide covers the prompting and scaffolding patterns specific to Claude Fable 5 and Claude Mythos 5. For the model's capabilities, API changes, pricing, and availability, see [Introducing Claude Fable 5 and Claude Mythos 5](https://platform.claude.com/docs/en/models/fable-5/introducing-claude-fable-5-and-claude-mythos-5). For techniques that apply across all current Claude models, see [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).

Claude Fable 5 takes on problems that were previously too complex, long-running, or ambiguous for prior models, and is particularly effective at end-to-end work that takes a person hours, days, or weeks to complete. The teams seeing the best outcomes apply Claude Fable 5 to their hardest unsolved problems; testing it only on simpler workloads tends to undersell its capability range. It also performs reliably on more straightforward tasks.

Claude Fable 5 has several behavioral differences from Claude Opus 4.8 that may require prompt or scaffolding updates. Capability improvements at this level are also a good prompt to re-evaluate which instructions, tools, and guardrails are still needed. The patterns below cover the behaviors that most often require tuning.

<Note>
  For API parameter changes specific to Claude Fable 5 and Claude Mythos 5 (adaptive thinking only, summarized-only thinking output, no extended thinking budgets, the `refusal` stop reason and fallback handling), see [Introducing Claude Fable 5 and Claude Mythos 5](https://platform.claude.com/docs/en/models/fable-5/introducing-claude-fable-5-and-claude-mythos-5).

  Claude Fable 5 runs safety classifiers that target offensive cybersecurity techniques (such as building exploits, malware, or attack tooling), biology and life sciences content (such as lab methods or molecular mechanisms), and extraction of the model's summarized thinking. Benign cybersecurity work and beneficial life sciences tasks may also trigger these safeguards. To re-route declined requests automatically, configure [server-side or client-side fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) to Claude Opus 4.8.
</Note>


## Capability improvements

Source: https://platform.claude.com/llms-full.txt#capability-improvements

Compared with Claude Opus 4.8, Claude Fable 5 shows improvement in:

* **Long-horizon autonomy.** Claude Fable 5 sustains productive output over extended periods, completing multiday, goal-directed runs with strong instruction retention across long, complex tasks.
* **First-shot correctness on complex, well-specified problems.** Early testers reported single-pass implementations of systems that previously took days of iteration.
* **Vision.** Claude Fable 5 interprets dense technical images, web applications, and detailed screenshots with substantially higher accuracy, often while using fewer output tokens, and is trained to use bash and crop tools to handle flipped, blurry, or noisy images.
* **Enterprise workflows.** Claude Fable 5 follows instructions, stays in scope, and produces professional-grade output on financial analysis, spreadsheets, slides, and documents.
* **Code review and debugging.** Bug-finding recall (outside the cybersecurity domains the safety classifiers cover) is noticeably higher than Claude Opus 4.8, including search across codebases and repository history.
* **Navigating ambiguity.** Claude Fable 5 performs well when given complex, multithreaded requests and asked to determine next steps.
* **Delegation and collaboration.** Claude Fable 5 is significantly more dependable at dispatching and sustaining parallel subagents, and reliably manages ongoing communication with long-running subagents and peer agents.

Beyond these specific improvements, Claude Fable 5 is generally more capable than prior models on almost all tasks. Claude Fable 5 is not intended for offensive cybersecurity or biology and life sciences work; requests in those domains can return [`stop_reason: "refusal"`](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback).


## Longer turns by default

Source: https://platform.claude.com/llms-full.txt#longer-turns-by-default

Individual requests on hard tasks can run for many minutes at higher [effort](https://platform.claude.com/docs/en/build-with-claude/effort) settings, especially when the task requires gathering context, building, and self-verifying, and autonomous runs can extend for hours. This is one of the largest shifts teams encounter when adjusting to Claude Fable 5. Adjust client timeouts, streaming, and user-facing progress indicators before migrating, and consider restructuring harnesses to check on runs asynchronously, for example through scheduled jobs, rather than blocking. To keep Claude Fable 5 from overplanning when a task is ambiguous:

```text wrap
When you have enough information to act, act. Do not re-derive facts already established in the conversation, re-litigate a decision the user has already made, or narrate options you will not pursue in user-facing messages. If you are weighing a choice, give a recommendation, not an exhaustive survey. This does not apply to thinking blocks.
```


## Consider all effort levels

Source: https://platform.claude.com/llms-full.txt#consider-all-effort-levels

[Effort](https://platform.claude.com/docs/en/build-with-claude/effort) is the primary control for the trade-off between intelligence, latency, and cost on Claude Fable 5. Use `high` as the default for most tasks, with `xhigh` for the most capability-sensitive workloads and `medium` or `low` for routine work. Lower effort settings on Claude Fable 5 still perform well and often exceed `xhigh` performance on prior models. Reduce effort if a task completes but takes longer than necessary, or if you want a quicker, more interactive working style.

On routine work at higher effort, Claude Fable 5 can gather context and deliberate beyond what the task needs. At the same time, higher effort often produces excellent verification behavior, sophisticated reasoning, and the most rigorous output. To prevent unrequested tidying or refactoring at higher effort:

```text wrap
Don't add features, refactor, or introduce abstractions beyond what the task requires. A bug fix doesn't need surrounding cleanup and a one-shot operation usually doesn't need a helper. Don't design for hypothetical future requirements: do the simplest thing that works well. Avoid premature abstraction and half-finished implementations. Don't add error handling, fallbacks, or validation for scenarios that cannot happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). Don't use feature flags or backwards-compatibility shims when you can just change the code.
```


## Strong instruction following

Source: https://platform.claude.com/llms-full.txt#strong-instruction-following

Instruction-following is improved enough that you can steer most behaviors with a brief instruction rather than enumerating each behavior by name. For example, when un-steered, Claude Fable 5 can elaborate beyond what the task needs, especially at higher effort settings: surveying options it won't pursue, explaining root causes at length, producing heavily-structured PR descriptions, or writing comments that narrate what the next line does. A short brevity instruction is as effective as listing each pattern:

```text wrap
Lead with the outcome. Your first sentence after finishing should answer "what happened" or "what did you find": the thing the user would ask for if they said "just give me the TLDR." Supporting detail and reasoning come after. Being readable and being concise are different things, and readability matters more.

The way to keep output short is to be selective about what you include (drop details that don't change what the reader would do next), not to compress the writing into fragments, abbreviations, arrow chains like A → B → fails, or jargon.

text wrap
Pause for the user only when the work genuinely requires them: a destructive or irreversible action, a real scope change, or input that only they can provide. If you hit one of these, ask and end the turn, rather than ending on a promise.
```


## Ground progress claims during long runs

Source: https://platform.claude.com/llms-full.txt#ground-progress-claims-during-long-runs

On long autonomous runs, instruct Claude Fable 5 to audit progress against actual tool results. In Anthropic's testing, this nearly eliminated fabricated status reports even on tasks designed to elicit them:

```text wrap
Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. Report outcomes faithfully: if tests fail, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging.
```


## State the boundaries

Source: https://platform.claude.com/llms-full.txt#state-the-boundaries

Claude Fable 5 can occasionally take unrequested actions (drafting an email when none was asked for, creating defensive git-branch backups). Define explicit constraints on what Claude Fable 5 should and should not do:

```text wrap
When the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report your findings and stop. Don't apply a fix until they ask for one. Before running a command that changes system state (restarts, deletes, config edits), check that the evidence actually supports that specific action. A signal that pattern-matches to a known failure may have a different cause.
```


## Parallel subagents

Source: https://platform.claude.com/llms-full.txt#parallel-subagents

Claude Fable 5 dispatches parallel subagents more readily than prior models. Use subagents frequently, provide explicit guidance about when delegation is appropriate, and prefer asynchronous communication between orchestrator and subagents over blocking until each subagent returns. Long-lived subagents that keep their context across subtasks save time and cost through cache reads and avoid bottlenecking on the slowest subagent.

```text wrap
Delegate independent subtasks to subagents and keep working while they run. Intervene if a subagent goes off track or is missing relevant context.
```


## Construct a memory system

Source: https://platform.claude.com/llms-full.txt#construct-a-memory-system

Claude Fable 5 performs particularly well when it can record lessons from previous runs and reference them. Provide a place to write notes, as simple as a Markdown file:

```text wrap
Store one lesson per file with a one-line summary at the top. Record corrections and confirmed approaches alike, including why they mattered. Don't save what the repo or chat history already records; update an existing note rather than creating a duplicate; delete notes that turn out to be wrong.

text wrap
Reflect on the previous sessions we've had together. Use subagents to identify core themes and lessons, and store them in [X]. Make sure you know to reference [X] for future use.
```


## Rare cases of early stopping

Source: https://platform.claude.com/llms-full.txt#rare-cases-of-early-stopping

Deep into a long session, Claude Fable 5 can occasionally end a turn with a text-only statement of intent ("I'll now run X") without issuing the corresponding tool call, or pause to ask permission when it already has enough to proceed. A "continue" or "go ahead and do it end to end" suffices. To define when pausing is appropriate, pair this with the checkpoint instruction in [Strong instruction following](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5#strong-instruction-following). For autonomous pipelines, add a system reminder:

```text wrap
You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking "Want me to…?" or "Shall I…?" will block the work. For reversible actions that follow from the original request, proceed without asking. Offering follow-ups after the task is done is fine; asking permission after already discussing with the user before doing the work is not. Before ending your turn, check your last paragraph. If it is a plan, an analysis, a question, a list of next steps, or a promise about work you have not done ("I'll…", "let me know when…"), do that work now with tool calls. End your turn only when the task is complete or you are blocked on input only the user can provide.
```


## Rare cases of context-budget concern

Source: https://platform.claude.com/llms-full.txt#rare-cases-of-context-budget-concern

In very long sessions, Claude Fable 5 can occasionally suggest a new session, offer to summarize and hand off, or trim its own work. This is most often triggered when the harness shows a remaining-token countdown to the model. Avoid surfacing explicit context-budget counts where possible. If the harness must show them, a reassurance helps:

```text wrap
You have ample context remaining. Do not stop, summarize, or suggest a new session on account of context limits. Continue the work.
```


## Give the reason, not only the request

Source: https://platform.claude.com/llms-full.txt#give-the-reason-not-only-the-request

Claude Fable 5 tends to perform better when it understands the intent behind a request: context lets it connect the task to relevant information rather than inferring intent on its own. Provide context about why you're asking, especially for long-running agents drawing on multiple workstreams:

```text wrap
I'm working on [the larger task] for [who it's for]. They need [what the output enables]. With that in mind: [request].
```
