# platform.claude.com Documentation (Part 35 of 35)

## Setting up a Managed Agent

Source: https://platform.claude.com/llms-full.txt#setting-up-a-managed-agent

To scaffold a new Managed Agent from scratch, invoke the `managed-agents-onboard` subcommand:

```text wrap
/claude-api managed-agents-onboard
```

The skill runs an interview that walks you through the Managed Agents mental model (Agent configs versus Sessions), templates an agent config, configures environments and tools, sets up the session loop, and emits runnable code for your language. The skill also covers the mandatory **Agent (once) → Session (every run)** flow: `model`, `system`, and `tools` live on the agent, never on the session, and agents should be created once and referenced by ID.

Managed Agents requires the `managed-agents-2026-04-01` beta header, which the SDK sets automatically for all `client.beta.agents.*`, `client.beta.environments.*`, `client.beta.sessions.*`, and `client.beta.vaults.*` calls.


## Example usage

Source: https://platform.claude.com/llms-full.txt#example-usage

Here are examples of tasks the skill helps Claude handle:

**Building a chat application:**

```text wrap
Build a streaming chat UI with the Claude API in TypeScript

text wrap
/claude-api migrate this codebase to claude-opus-5 and re-tune effort

text wrap
/claude-api managed-agents-onboard
```

In each case, the skill loads the relevant language-specific documentation and guides Claude through the implementation using current API patterns and best practices.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-115

<CardGroup cols={2}>
  <Card title="Agent Skills overview" icon="graduation-cap" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview">
    Learn about how Agent Skills work and the progressive disclosure model
  </Card>

  <Card title="Client SDKs" icon="code" href="https://platform.claude.com/docs/en/cli-sdks-libraries/overview">
    Browse the official Anthropic SDKs for all supported languages
  </Card>

  <Card title="Skills repository" icon="github-logo" href="https://github.com/anthropics/skills">
    Explore the public Anthropic skills repository on GitHub
  </Card>
</CardGroup>


## Release notes

Source: https://platform.claude.com/llms-full.txt#release-notes

---
title: Claude Platform release notes
url: https://platform.claude.com/docs/en/release-notes/overview
description: Updates to the Claude Platform, including the Claude API, client SDKs, and the Claude Console.
---

The Claude Platform release notes list changes to the Claude API, the client SDKs, and the Claude Console, newest first.

<Tip>
  For release notes on Claude Apps, see the [Release notes for Claude Apps in the Claude Help Center](https://support.claude.com/en/articles/12138966-release-notes).

  For updates to Claude Code, see the [complete CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) in the `claude-code` repository.
</Tip>

### September 3, 2026

* Version 1.30.0 of the `ant` CLI adds `ant apply`, which creates and updates agents, environments, skills, memory stores, and deployments from files in your repository. Describe each resource in a file, run `ant apply`, and approve the plan it prints. Commit the `claude-lock.json` lockfile it writes so that later runs, on your machine or in CI, update the same resources instead of creating new ones. See [Manage resources as code with ant apply](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/apply).

### September 1, 2026

* We've launched **Claude Fable 5.1** (`claude-fable-5-1`), the successor to Claude Fable 5 for long-running agentic coding, knowledge work, and research, alongside **Claude Mythos 5.1** (`claude-mythos-5-1`) for Project Glasswing participants. Both models support a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) by default, 128k max output tokens, and always-on [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking), at $10 / $50 USD per MTok, the same as Claude Fable 5, with cache reads cut to $0.25 per MTok. Claude Fable 5.1 is available on the Claude API, [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), [Claude on Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), and [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry). See [What's new in Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1) for capabilities, API changes, and migration guidance.
* Prompt cache reads on Claude Fable 5.1 and Claude Mythos 5.1 cost $0.25 USD per million tokens: 0.025x the base input price, compared with 0.1x on other models. Cache writes are unchanged. See [Prompt caching pricing](https://platform.claude.com/docs/en/about-claude/pricing#prompt-caching).
* On Claude Fable 5.1 and Claude Mythos 5.1, `tool_choice` types `any` and `tool` aren't supported and return a 400 error. `auto` and `none` are unchanged. To guarantee schema-conformant tool inputs, use [strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) or [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
* Thinking blocks produced by Claude Fable 5.1 and Claude Mythos 5.1 are preserved only for the model that produced them or a newer one: earlier models can't read them, and the API drops one replayed to an earlier model. Claude Fable 5.1 accepts thinking blocks from Claude Opus 5, Claude Fable 5, Claude Mythos 5, and earlier Claude models. On Claude Fable 5.1, the API also [checks that nothing before a block has changed](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-in-conversation): for new accounts created on or after August 31, 2026, replaying one after the `system` prompt, `tools`, or an earlier message changed returns a 400 error. With the `thinking-binding-controls-2026-08-01` beta header, dropped blocks are reported in an `input_transformations` response field, and `thinking.block_binding.prefix_mismatch_behavior` chooses between rejecting and dropping blocks whose history changed. See [Preserved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-thinking).
* Per-message effort changes are in beta on Claude Fable 5.1, Claude Mythos 5.1, and Claude Opus 5 on the Claude API. Add a `role: "system"` message with `output_config.effort` inside `messages` to change effort for later turns while preserving the prompt cache. Include the `mid-conversation-output-config-2026-07-01` beta header in your requests. See [Per-message effort](https://platform.claude.com/docs/en/build-with-claude/effort#change-effort-mid-conversation-beta).
* [Turn-scoped system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#turn-scoped-system-messages) are in beta (`mid-conversation-system-clear-at-2026-08-21` header). Set `clear_at: "next_user_message"` on a mid-conversation `role: "system"` message and it renders for the current turn only, then stays in the history at no token cost. Per-turn reminders don't accumulate and don't invalidate the prompt cache or later thinking blocks.
* `thinking.display` accepts a third value, `"updates"`, in beta (`thinking-display-updates-2026-08-18` header). Reasoning comes back with an empty `thinking` field, as under `"omitted"`, and the short progress updates that Claude Fable 5.1, Claude Mythos 5.1, and Claude Fable 5 write between tool calls come back as text, at most one `thinking` block before a tool call. See [Progress updates between tool calls](https://platform.claude.com/docs/en/build-with-claude/thinking#progress-updates).
* Text generated by Claude Fable 5.1 and Claude Mythos 5.1 carries Anthropic's text watermark, and supported image, video, and audio files that Claude produces through the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) carry C2PA Content Credentials when you retrieve them through the [Files API](https://platform.claude.com/docs/en/build-with-claude/files) on the Claude API. Marking requires no changes to your requests or response handling.
* Like Claude Fable 5, both models require 30-day data retention and aren't available under zero data retention unless expressly authorized by Anthropic. See [Model-specific data retention requirements](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements).
* The guides for the Claude Enterprise endpoints of the [Admin API](https://platform.claude.com/docs/en/api/admin) ([user management](https://platform.claude.com/docs/en/manage-claude/user-management) and [spend limits](https://platform.claude.com/docs/en/manage-claude/spend-limits-api)), the [Claude Enterprise Analytics API](https://platform.claude.com/docs/en/manage-claude/analytics-api), and the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) now show the `anthropic-version` header; send it on every request to these endpoints, as in the rest of the Claude API. See [API versions](https://platform.claude.com/docs/en/api/versioning).

### August 27, 2026

* You can now create **personal keys** and **service account keys** in the Claude Console. They act as you or as a [service account](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#service-accounts), with the same permissions, and stop working when the linked account is removed from an organization. This lets organization admins more easily track usage for each account, and ensure key usage is legitimate. These API keys can be scoped to a specific workspace or [work on admin endpoints and across any workspace](https://platform.claude.com/docs/en/manage-claude/authentication#select-a-workspace) the account has access to. Workspace API keys remain supported as a legacy option. See [API keys](https://platform.claude.com/docs/en/manage-claude/authentication#api-keys) for more information.

### August 26, 2026

* The [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) session endpoints are out of beta for Cowork and Claude Code sessions. See [Retrieve session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions).
* The [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) local session endpoints now also return transcripts of Claude Science sessions (`product_surface` value `claude_science`) and Claude for Microsoft 365 sessions in Excel, PowerPoint, Word, and Outlook (`product_surface` values beginning with `office_agents`), in beta for Claude Enterprise organizations, with your existing Compliance Access Key and the `read:compliance_user_data` scope. See [Sessions on users' machines](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions).

### August 20, 2026

* We've released **v1.0 of the [Python SDK](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python)**. The SDK's HTTP layer moves from `httpx` to [httpx2](https://httpx2.pydantic.dev), a maintained, API-compatible fork: build custom `http_client`, `Timeout`, and transport objects from `httpx2` (the `DefaultHttpxClient` helpers are unchanged), and call `httpx2.alias_httpx()` at startup if you rely on tracing or mocking libraries that patch `httpx`. v1.0 requires Python 3.10 or later and removes long-deprecated surface, including the legacy Text Completions API, the `temperature`, `top_p`, and `top_k` parameters on Messages methods, and the tool runner's client-side `compaction_control`. On the async client, `.with_raw_response` results now need `await response.parse()`, and `AnthropicBedrock` now raises an error when no AWS region is configured instead of defaulting to `us-east-1`. See the [v1 migration guide](https://github.com/anthropics/anthropic-sdk-python/blob/main/MIGRATION.md) for every change with before-and-after snippets.
* The [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) toolsets (`computer_toolset_20260801` and `browser_toolset_20260801`) are now available on [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai) for Claude Fable 5, Claude Mythos 5, Claude Opus 5, Claude Sonnet 5, and Claude Opus 4.8. Requests use the same `tools` entries as on the Claude API.

### August 19, 2026

* The [computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) is out of beta on the Claude API as the `computer_toolset_20260801` toolset: no beta header, batch actions (several actions in one turn), `zoom` enabled by default, and per-member configuration through `configs`. Earlier beta versions remain available. Upgrading an existing integration changes the request shape and tool handling; see [Migrate from `computer_20251124`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#migrate-from-computer-20251124).
* We've launched the [browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) (`browser_toolset_20260801`), a client toolset for driving a browser that your application hosts. It works inside a browser viewport rather than a whole desktop, reading the page itself (its accessibility tree, elements, forms, and tabs) and adding element references, form input, tab management, download reporting, and opt-in file upload on top of screenshot-and-click control.
* Both toolsets are available for Claude Fable 5, Claude Mythos 5, Claude Opus 5, Claude Sonnet 5, and Claude Opus 4.8 on the Claude API.
* The [Files API](https://platform.claude.com/docs/en/build-with-claude/files) is out of beta on the Claude API. Requests to the `/v1/files` endpoints, and Messages API requests that reference an uploaded file, no longer require the `files-api-2025-04-14` beta header. Requests sent without the header use the current response format: [file expiration](https://platform.claude.com/docs/en/build-with-claude/files#file-expiration) (set `expires_in_seconds` when you upload a file; file objects report `expires_at`), and `page` and `next_page` [pagination](https://platform.claude.com/docs/en/api/overview#pagination) plus an `ids[]` filter when you [list files](https://platform.claude.com/docs/en/build-with-claude/files#list-files). `/v1/files` requests that still send the beta header keep working and return the previous response format.
* [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) and the Skills API (`/v1/skills`) are out of beta on the Claude API. Requests no longer require the `skills-2025-10-02` beta header, including Messages API requests that load Skills through the `container` parameter. Requests that still send the header continue to work unchanged. See [Using Agent Skills with the API](https://platform.claude.com/docs/en/build-with-claude/skills-guide).
* The [Admin API](https://platform.claude.com/docs/en/api/admin) user-management endpoints for **Claude Enterprise** (claude.ai) organizations (members, invites, groups, and custom roles) are out of beta. The `anthropic-beta: ce-user-management-2026-07-13` header is no longer required on group and custom-role requests; requests that still send it are accepted unchanged. See [User management](https://platform.claude.com/docs/en/manage-claude/user-management).
* You can now restrict which sites a Claude Managed Agents agent's `web_search` and `web_fetch` tools can reach. Set `allowed_domains` or `blocked_domains` on the tool's entry in the `agent_toolset_20260401` `configs` array; `web_fetch` also accepts `max_content_tokens` and `web_search` accepts `user_location`. Each `configs` entry is identified by its `name` and typed by an optional `type`, and requests that pass only `name`, `enabled`, and `permission_policy` continue to work; in the typed SDKs, `configs` entries become per-tool types. See [Restrict web search and web fetch domains](https://platform.claude.com/docs/en/managed-agents/tools#restrict-web-search-and-web-fetch-domains).
* Claude Managed Agents sessions that run in a [self-hosted sandbox](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) can now attach [memory stores](https://platform.claude.com/docs/en/managed-agents/memory). The Python, TypeScript, and Go SDK workers download each attached store into the sandbox at its `mount_path` and sync the agent's changes back to the store. See [Use memory stores](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores).
* The session viewer in the Claude Console has been redesigned with a timeline minimap, a transcript grouped by model request, and an Inspector panel for session details and cost, raw events, per-tool statistics, mounted resources, and per-thread activity. See [Console observability](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#console-observability).

### August 18, 2026

* Workbench is now [**playground**](https://platform.claude.com/playground) in the Claude Console. Playground supports every Messages API parameter and includes templates that demonstrate API features such as code execution and web search. It shows the full SDK request and the API response for each run, to help you understand the API and build with it. For more, see the [Claude Help Center](https://support.claude.com/en/articles/8606378-how-do-i-use-playground) or try it at [platform.claude.com/playground](https://platform.claude.com/playground).

### August 11, 2026

* The [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) now returns transcripts of Cowork and Claude Code sessions that run on your users' machines, in beta for Claude Enterprise organizations. `GET /v1/compliance/apps/sessions/local` lists sessions across your organization, `GET /v1/compliance/apps/sessions/local/{session_id}` retrieves one session's metadata, and `GET /v1/compliance/apps/sessions/local/{session_id}/messages` returns its transcript, all with your existing Compliance Access Key and the `read:compliance_user_data` scope. See [Sessions on users' machines](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions).
* We've added the `anthropic-workspace-id` response header to the Claude API. It carries the `wrkspc_`-prefixed ID of the workspace that the request's API key or access token resolved to, including your organization's Default Workspace. See [Identify the workspace behind an API response](https://platform.claude.com/docs/en/manage-claude/workspaces#identify-the-workspace-behind-an-api-response).

### August 10, 2026

* The introductory pricing for **Claude Sonnet 5** ($2 / $10 per MTok) is now the standard price: the previously scheduled increase to $3 / $15 per MTok on September 1, 2026 will not occur. See [Pricing](https://platform.claude.com/docs/en/about-claude/pricing).

### August 7, 2026

* You can now set a budget on a Claude Managed Agents session: a hard cap on the session's spend, priced at public list rates. A session that reaches its budget pauses with the `budget_reached` stop reason instead of starting new model requests; changing or removing the budget resumes it. Deployments accept the same budget and apply it to each session they start. See [Session budgets](https://platform.claude.com/docs/en/managed-agents/budgets).
* You can now give a Claude Managed Agents session an advisor: a model at least as capable as the agent's own that the session's primary thread can consult mid-turn for strategic guidance. Configure it as a `{"type": "advisor"}` entry in the agent's multiagent roster, naming the `model` to consult. See [Give the session an advisor](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration#give-the-session-an-advisor).
* You can now control where model inference runs for a Claude Managed Agents agent. Set `inference_geo` inside the `model` object when you [create the agent](https://platform.claude.com/docs/en/managed-agents/agent-setup#pin-the-inference-geo), or [override it for a single session](https://platform.claude.com/docs/en/managed-agents/sessions#pin-the-inference-geo-for-a-session). See [Data residency](https://platform.claude.com/docs/en/manage-claude/data-residency) for the available geos and pricing.
* Claude Managed Agents sessions can now [load skills from a GitHub repository](https://platform.claude.com/docs/en/managed-agents/skills#load-skills-from-a-github-repository). When a session [mounts a repository](https://platform.claude.com/docs/en/managed-agents/github), any skills in its root `.claude/skills` directory are discovered automatically at session start and available to the agent for that session.

### August 5, 2026

* **Inference hooks** are now in beta for Claude Enterprise organizations. Point Claude at your organization's AI security server, and each governed prompt across claude.ai, Cowork, and Claude Code is held for the server's allow or deny verdict before inference proceeds. Requests are signed, failure handling is configurable, and every denial is recorded in the compliance [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed). See [Inference hooks](https://platform.claude.com/docs/en/manage-claude/inference-hooks).
* We've retired the Claude Opus 4.1 model (`claude-opus-4-1-20250805`). All requests to this model on the Claude API will now return an error. We recommend upgrading to [Claude Opus 5](https://platform.claude.com/docs/en/models/overview#latest-models-comparison). Researchers can request ongoing access through the [External Researcher Access Program](https://support.claude.com/en/articles/9125743-what-is-the-external-researcher-access-program).

### August 3, 2026

* The [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) now returns transcripts of Cowork sessions started on claude.ai web or mobile, in beta for Claude Enterprise organizations. `GET /v1/compliance/apps/sessions/remote` lists sessions and `GET /v1/compliance/apps/sessions/remote/{session_id}/messages` returns one session's transcript, using your existing Compliance Access Key with the `read:compliance_user_data` scope. See [Sessions in the cloud](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-remote-sessions).

### August 1, 2026

* [Dreams](https://platform.claude.com/docs/en/managed-agents/dreams) (research preview) now supports Claude Opus 5. See [Supported models](https://platform.claude.com/docs/en/managed-agents/dreams#limits).

### July 24, 2026

* We've launched **Claude Opus 5** (`claude-opus-5`), a step-change improvement over Claude Opus 4.8. Claude Opus 5 supports a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) (both the default and the maximum), 128k max output tokens, and [thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) on by default, at $5 / $25 USD per MTok, the same pricing as Claude Opus 4.8. It's available on the Claude API, [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), [Claude on Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), and [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry). See [What's new in Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/whats-new-opus-5) for new features, behavior changes, and migration guidance, and the [models overview](https://platform.claude.com/docs/en/models/overview) for complete specs.
* On Claude Opus 5, disabling thinking is allowed only at effort `high` or below: `thinking: {"type": "disabled"}` with effort `xhigh` or `max` returns a 400 error, a breaking change from Claude Opus 4.8. See [What's new in Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/whats-new-opus-5#behavior-changes).
* [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) is the primary control for steering Claude Opus 5: the model supports the full ladder (`low`, `medium`, `high`, `xhigh`, `max`), with `max` for capability-critical work.
* Mid-conversation tool changes are now in beta on Claude Fable 5, Claude Mythos 5, Claude Opus 4.8, and Claude Opus 5: add or remove tools between turns of a conversation while preserving the prompt cache. Include the `mid-conversation-tool-changes-2026-07-01` beta header in your requests.
* The `fallbacks` parameter now supports a `"default"` mode, which applies Anthropic's recommended fallback models by refusal category. Server-side fallback is in beta, and the `"default"` mode requires the `server-side-fallback-2026-07-01` beta header. See [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback).
* We've removed [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) for Claude Opus 4.7. Requests to `claude-opus-4-7` with `speed: "fast"` now return an error; unlike Claude Opus 4.6, they do not fall back to standard speed. Claude Opus 4.7 itself remains available at standard speed. To continue using fast mode, migrate to [Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/migration-guide#migrating-from-claude-opus-47) or Claude Opus 4.8. Read more in [Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode#supported-models).

### July 22, 2026

* You can now set an `effort` level on a Claude Managed Agents agent's model configuration. Pass `effort` inside the `model` object when you [create the agent](https://platform.claude.com/docs/en/managed-agents/agent-setup#create-an-agent). See [Effort levels](https://platform.claude.com/docs/en/build-with-claude/effort#effort-levels) for what each level does.
* Webhooks for Claude Managed Agents now cover the environment and memory store lifecycle: four `environment.*` event types and three `memory_store.*` event types. You can react to environment and memory store lifecycle changes without polling. See the Environment events and Memory store events tabs in [Subscribe to webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks#supported-event-types).
* When creating a Claude Managed Agents session, you can now [seed it with initial events](https://platform.claude.com/docs/en/managed-agents/sessions#seed-the-session-with-initial-events). Pass `initial_events` on `POST /v1/sessions` with up to 50 `user.message` and `user.define_outcome` events. A non-empty list starts the agent loop in the same call, so you don't need a separate send-events request to start work.
* The `version` field is now optional when [updating a Claude Managed Agents agent](https://platform.claude.com/docs/en/managed-agents/agent-setup#update-an-agent). Supply it for optimistic concurrency (a mismatch returns a 409 error), or omit it to apply the update unconditionally. See [Update semantics](https://platform.claude.com/docs/en/managed-agents/agent-setup#update-semantics).
* Claude Managed Agents session thread event streams now support [event deltas](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#event-deltas). `GET /v1/sessions/{session_id}/threads/{thread_id}/stream` accepts the same `event_deltas[]` query parameter as the session-level stream, so you can preview a subagent's text as the model generates it. A connection previews only the thread it's reading. See [Preview session thread events](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#preview-session-thread-events).

### July 17, 2026

* The legacy **Workbench** ([platform.claude.com/workbench](https://platform.claude.com/workbench)) in the Claude Console is being sunset with access ending on August 17, 2026. Saved prompts, variables, and evals are not supported in the updated [Workbench](https://platform.claude.com/playground). You can export any data you want to keep from the banner and under your **Organizational Settings**. For more, see [How do I use the Workbench?](https://support.claude.com/en/articles/8606378-how-do-i-use-the-workbench) in the Claude Help Center.
* The experimental prompt tools APIs for generating, improving, and templatizing prompts (`/v1/experimental/generate_prompt`, `/v1/experimental/improve_prompt`, and `/v1/experimental/templatize_prompt`) are being retired along with the Workbench on August 17, 2026. After removal, requests to these endpoints will return an error.

### July 15, 2026

* [Mid-conversation system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages) are available on Claude Fable 5, Claude Mythos 5, and Claude Opus 4.8, on the Claude API, [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), and [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai). No beta header is required. This corrects earlier availability notes.

### July 14, 2026

* You can now manage the people in your **Claude Enterprise** (claude.ai) organization with the [Admin API](https://platform.claude.com/docs/en/api/admin), in beta for all Claude Enterprise organizations: list members and look them up by email address, change a member's role, remove members, send and withdraw invites, manage groups and their membership, and read custom roles. Group and custom-role requests require the `anthropic-beta: ce-user-management-2026-07-13` beta header; member and invite requests take no beta header. An Admin API key with the `read:org_audit` scope can also call every user-management `GET` endpoint. See [User management](https://platform.claude.com/docs/en/manage-claude/user-management).

### July 10, 2026

* [Dreams](https://platform.claude.com/docs/en/managed-agents/dreams) (research preview) now supports Claude Fable 5 and Claude Sonnet 5. See [Supported models](https://platform.claude.com/docs/en/managed-agents/dreams#limits).
* We've expanded the [Access Transparency](https://platform.claude.com/docs/en/manage-claude/access-transparency) documentation of `cmek_preserve` events with a filter example, an example event payload, and two preservation reason codes (`policy_violation_investigation`, `csae_report`). The documentation now also clarifies that a preservation event is written whether the preservation was initiated by a human reviewer or an automated safety pipeline. See [CMEK content preservation](https://platform.claude.com/docs/en/manage-claude/access-transparency#cmek-content-preservation).

### July 8, 2026

* You can now set an expiration when you create an API key or an Admin API key in the [Claude Console](https://platform.claude.com/settings/keys). Choose a preset, a custom duration, or **Never**. For keys with a lifetime of at least 7 days, Anthropic emails the creator before expiration. Existing keys are unaffected. The Admin API reports each key's expiration in the [`expires_at`](https://platform.claude.com/docs/en/api/admin/api_keys/list) field. See [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication#key-expiration).

### July 2, 2026

* We've added the `agent-memory-2026-07-22` beta header, which changes how [listing memories](https://platform.claude.com/docs/en/managed-agents/memory#list-memories) (`GET /v1/memory_stores/{memory_store_id}/memories`) behaves: results are returned in a stable, server-defined order and the `order_by` and `order` parameters are ignored; `depth` accepts only `0`, `1`, or being omitted (other values return a `400` error); and `path_prefix` must end with `/` and matches whole path segments instead of a substring. Page cursors issued without the header aren't valid with it, so restart from the first page when you adopt it. On memory store endpoints, `agent-memory-2026-07-22` replaces `managed-agents-2026-04-01`; sending both returns a `400` error. On July 22, 2026, the `managed-agents-2026-04-01` header adopts the same list behavior. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
* The Python (0.116.0), TypeScript (0.110.0), Go (1.56.0), Java (2.48.0), Ruby (1.55.0), PHP (0.36.0), C# (12.35.0), and CLI (1.16.0) SDKs now send `agent-memory-2026-07-22` on all memory store calls instead of `managed-agents-2026-04-01`. If your code passes `betas` explicitly on memory store calls, replace `managed-agents-2026-04-01` with `agent-memory-2026-07-22` there rather than adding a second value.

### July 1, 2026

* We've restored access to Claude Fable 5 and Claude Mythos 5. See [our statement](https://www.anthropic.com/news/redeploying-fable-5) for more information.

### June 30, 2026

* We've launched **Claude Sonnet 5** (`claude-sonnet-5`), the next generation of our Sonnet model family, at introductory pricing of $2 / $10 per MTok (made the standard price on August 10, 2026). Claude Sonnet 5 supports a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows), 128k max output tokens, and the same set of tools and platform features as Claude Sonnet 4.6, except [Priority Tier](https://platform.claude.com/docs/en/api/service-tiers#supported-models), which is not available on Claude Sonnet 5. Three behavior changes apply when migrating: [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) is now on by default; manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) is removed and returns a 400 error (it was deprecated on Sonnet 4.6); and setting sampling parameters (`temperature`, `top_p`, `top_k`) to non-default values returns a 400 error. Claude Sonnet 5 also uses a new tokenizer that produces approximately 30% more tokens for the same text. The exact increase depends on the content and workload shape. See [What's new in Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5) for details and migration guidance. For behavioral differences and model-specific prompting patterns, see [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5).
* Claude Managed Agents session event streams now support [event deltas](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#event-deltas). Opt in with the `event_deltas[]` query parameter on `GET /v1/sessions/{session_id}/events/stream`. The `event_start` and `event_delta` events preview an agent message's text as it's generated, before the complete `agent.message` event arrives.
* [Listing sessions](https://platform.claude.com/docs/en/managed-agents/session-operations#listing-sessions) for Claude Managed Agents now supports backward pagination. `GET /v1/sessions` returns a `prev_page` cursor alongside `next_page`; pass it as the `page` parameter to return to the previous page. See [Pagination](https://platform.claude.com/docs/en/api/overview#pagination).
* When creating a Claude Managed Agents session, you can now [override the agent's configuration for that session](https://platform.claude.com/docs/en/managed-agents/sessions#override-agent-configuration-for-a-session). Pass `agent` with `type: "agent_with_overrides"` to replace the model, system prompt, tools, MCP servers, or skills for a single session. The agent itself is unchanged.
* Claude Managed Agents vaults now support an `injection_location` setting on [environment variable credentials](https://platform.claude.com/docs/en/managed-agents/vaults#add-a-credential) (the Environment variable tab). It controls whether the credential's value is substituted, at egress, into the agent's outbound request headers, the request body, or both.
* Webhooks for Claude Managed Agents now cover the agent, deployment, and deployment run lifecycle. You can react to a newly published agent version, a paused deployment, or a failed scheduled run without polling. See the Agent events, Deployment events, and Deployment run events tabs in [Subscribe to webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks#supported-event-types).

### June 29, 2026

* We've removed [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) for Claude Opus 4.6. Requests to `claude-opus-4-6` with `speed: "fast"` no longer run at fast speed or premium pricing: they run at standard speed, are billed at standard rates, and do not return an error. The response's `usage.speed` field reports the speed used. To continue using fast mode, migrate to [Claude Opus 4.8](https://platform.claude.com/docs/en/about-claude/models/migration-guide). Read more in [Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode#supported-models).

### June 26, 2026

* We've raised [rate limits](https://platform.claude.com/docs/en/api/rate-limits) across the Claude API. Claude Sonnet and Claude Haiku rate limits now match Claude Opus at every usage tier, and usage tiers have been consolidated into three: Start, Build, and Scale. Most organizations move to a higher tier, no organization receives lower limits than before, and no action is required. You can view your tier and current limits in the [Claude Console](https://platform.claude.com/settings/limits).

### June 25, 2026

* We've deprecated [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) for Claude Opus 4.7, with removal on July 24, 2026. After removal, requests to `claude-opus-4-7` with `speed: "fast"` will return an error. Migrate to fast mode for Claude Opus 4.8. Read more in [Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode#supported-models).

### June 22, 2026

* **MCP tunnels** (research preview): the management API moved from `/v1/organizations/tunnels` on the Admin API to `/v1/tunnels` on the Claude API. The new surface uses the `anthropic-beta: mcp-tunnels-2026-06-22` header and the `workspace:manage_tunnels` WIF scope. The previous surface remains available during a migration window. See the [Tunnels API reference](https://platform.claude.com/docs/en/api/beta/tunnels).

### June 18, 2026

* The Python, TypeScript, Go, Java, Ruby, PHP, and C# SDKs now include support for `code_execution_20260120`, the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) version that adds REPL state persistence and is the minimum version for [programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling). To adopt it, set the tool's `type` to `code_execution_20260120`; no beta header is required. It's available on Claude Fable 5, Claude Mythos 5, Claude Opus 4.5 and newer, and Claude Sonnet 4.5 and newer; see the code execution tool's [Compatibility](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#compatibility) section.

### June 15, 2026

* We've retired the Claude Sonnet 4 model (`claude-sonnet-4-20250514`) and the Claude Opus 4 model (`claude-opus-4-20250514`). All requests to these models on the Claude API will now return an error. We recommend upgrading to [Claude Sonnet 4.6](https://platform.claude.com/docs/en/models/overview#latest-models-comparison) and [Claude Opus 4.8](https://platform.claude.com/docs/en/models/overview#latest-models-comparison) respectively. Researchers can request ongoing access through the [External Researcher Access Program](https://support.claude.com/en/articles/9125743-what-is-the-external-researcher-access-program).

### June 11, 2026

* The [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) now supports `code_execution_20260521`, which discloses the 90-second per-cell execution time limit in the tool description so Claude can budget long-running cells. No beta header is required.
* The [web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) and [web fetch tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) now support `web_search_20260318` and `web_fetch_20260318`, adding a `response_inclusion` parameter to drop consumed result blocks from the API response for agentic workflows. No beta header is required.

### June 10, 2026

* The `GET /v1/environments/{id}/work` endpoint, which lists pending work for a [self-hosted sandbox](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes), is now available on [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws). See [IAM actions for Claude Platform on AWS](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions) for the `GetEnvironment` action that authorizes it.

### June 9, 2026

* We've launched **Claude Fable 5** (`claude-fable-5`), our most capable widely released model, alongside **Claude Mythos 5** (`claude-mythos-5`) for Project Glasswing participants. Both models support a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) by default, 128k max output tokens, and always-on [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking). See [Introducing Claude Fable 5 and Claude Mythos 5](https://platform.claude.com/docs/en/models/fable-5/introducing-claude-fable-5-and-claude-mythos-5) for capabilities, API changes, and availability.
* Claude Fable 5 and Claude Mythos 5 use the tokenizer introduced with Claude Opus 4.7. Compared to models before Claude Opus 4.7, the same text produces roughly 30% more tokens. The exact increase depends on the content and workload shape. Use the [token counting API](https://platform.claude.com/docs/en/build-with-claude/token-counting#token-counts-on-claude-fable-5) with `model: "claude-fable-5"` to measure your prompts under the new tokenizer.
* Claude Fable 5 runs safety classifiers on requests and during response generation. When a classifier declines a request, the Messages API returns `stop_reason: "refusal"`. You are not billed for a request refused before any output is generated. An opt-in `fallbacks` parameter (in beta on the Claude API and Claude Platform on AWS; not supported on the Message Batches API) re-runs refused requests on another model, billed at the fallback model's rates. See [Handling stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons).
* The [`stop_details.category`](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#refusal-response) field on refusal responses now includes `"reasoning_extraction"` on Claude Fable 5, returned when a request is blocked under Anthropic's Terms of Service restrictions on reverse engineering or duplicating model outputs. The existing `"cyber"` and `"bio"` categories are unchanged. No beta header is required.
* On Claude Fable 5 and Claude Mythos 5, [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) is the only thinking mode: `thinking: {"type": "disabled"}` is not supported, and manual extended thinking budgets and assistant prefill are not supported (both return a 400 error). See [Migrating from Claude Mythos Preview to Claude Mythos 5](https://platform.claude.com/docs/en/models/fable-5/migration-guide#migrating-from-claude-mythos-preview).
* On Claude Fable 5 and Claude Mythos 5, `thinking.display` defaults to `"omitted"`, the same as Claude Opus 4.8, Claude Opus 4.7, and Claude Mythos Preview; set `display: "summarized"` to receive readable thinking summaries. The raw chain of thought is never returned; pass thinking blocks back unchanged in multi-turn conversations on the same model. See [Thinking output on Claude Fable 5 and Claude Mythos 5](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-output-on-claude-fable-5-and-claude-mythos-5).
* Claude Fable 5 requires 30-day data retention and is not available under zero data retention. See [Model-specific data retention requirements](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements).
* Claude Managed Agents now supports [scheduled deployments](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments), letting you run sessions on a cron schedule without managing your own scheduler.
* Claude Managed Agents vaults now support [environment variable credentials](https://platform.claude.com/docs/en/managed-agents/vaults#add-a-credential), so you can securely inject secrets into the agent's sandbox for CLIs, SDKs, and other services that authenticate through environment variables.
* The [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) (`GET /v1/compliance/activities`) is now available on [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws). See [IAM actions for Claude Platform on AWS](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#compliance) for the `ListComplianceActivities` action that authorizes it.
* The `session.thread_*` webhook events now include a `session_thread_id` field identifying the multiagent thread that triggered the event.
* We've released a [Swift package](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/apple-foundation-models) in beta that adds Claude as a server-side `LanguageModel` in Apple's Foundation Models framework. Call Claude through the same `LanguageModelSession` API as Apple's on-device model on iOS 27, macOS 27, visionOS 27, and watchOS 27 (beta).

### June 5, 2026

* We announced the deprecation of the Claude Opus 4.1 model (`claude-opus-4-1-20250805`), with retirement on the Claude API scheduled for August 5, 2026. We recommend migrating to [Claude Opus 4.8](https://platform.claude.com/docs/en/about-claude/models/migration-guide). Read more in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).

### June 2, 2026

* The [advisor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) now supports a `max_tokens` parameter to cap the advisor model's output per call, reducing latency and output token cost for workloads that don't need full-length advisor responses. Set `tools[].max_tokens` on the advisor tool definition; see [Capping advisor output](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#capping-advisor-output).
* On the Claude API, you are no longer billed for a request when it returns `stop_reason: "refusal"` without Claude having generated any output. See [Streaming refusals](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals) for detecting and handling refusals.

### May 29, 2026

* Claude Managed Agents [webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks), [multiagent orchestration](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration), and [self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) are now available on [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws). See [IAM actions for Claude Platform on AWS](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions) for the new IAM actions and the `AnthropicSelfHostedEnvironmentAccess` managed policy.

### May 28, 2026

* We've launched **Claude Opus 4.8** (claude-opus-4-8), our most capable widely released model. Claude Opus 4.8 supports a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) by default on the Claude API, Amazon Bedrock, Google Cloud, and Microsoft Foundry, 128k max output tokens, and the same set of tools and platform features as Claude Opus 4.7. See the [migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide) for baseline settings, features, and migration guidance.
* We've launched [mid-conversation system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages). On Claude Opus 4.8, you can send `role: "system"` messages after a user turn (subject to [placement rules](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#limitations)) in the `messages` array, preserving prompt cache hits when instructions change during a long-running session. No beta header is required.
* The [`stop_details`](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#refusal-response) field on refusal responses is now publicly documented; it returns a `category` (`cyber`, `bio`, or `null`) and a human-readable `explanation`, so your application can route different classes of refusal to the right next step. No beta header is required.
* On Claude Opus 4.8, the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) defaults to `high` across all surfaces, including Claude Code and the Messages API.
* On Claude Opus 4.8, the minimum cacheable prompt length for [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) is 1,024 tokens, lower than on Claude Opus 4.7.
* With [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) enabled, Claude Opus 4.8 triggers reasoning only when a turn needs it, reducing wasted thinking tokens compared to Claude Opus 4.7 at the same effort level.
* Claude Opus 4.8 supports [high-resolution image input](https://platform.claude.com/docs/en/build-with-claude/vision#high-resolution-image-support-on-claude-opus-4-7) (up to 2576 pixels on the long edge), same as Claude Opus 4.7.
* [Task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets) now support Claude Opus 4.8.
* The [advisor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) now supports Claude Opus 4.8.
* [Computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) now supports Claude Opus 4.8.
* [Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) for Claude Opus 4.8 is available as a research preview on the Claude API only.
* Setting the sampling parameters `temperature`, `top_p`, or `top_k` to a non-default value returns a 400 error on Claude Opus 4.8, same as on Claude Opus 4.7. See the [migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide) for details.
* In Claude Code, we've expanded Auto mode to more users for long-running tasks. See the [Claude Code documentation](https://code.claude.com/docs).
* In Claude Code, Max plan users now default to [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) on Claude Opus 4.8. See the [Claude Code documentation](https://code.claude.com/docs).
* In Claude Code, Workflows are available as a research preview, letting you define and run multistep agentic plans. See the [Claude Code documentation](https://code.claude.com/docs).
* We've deprecated [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) for Claude Opus 4.6, with removal approximately 30 days after launch. Migrate to fast mode for Claude Opus 4.8 or Claude Opus 4.7. Read more in [Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode#supported-models).
* For updates to claude.ai, Cowork, Claude for Microsoft 365, and other Claude apps in this release, see the [release notes for Claude Apps](https://support.claude.com/en/articles/12138966-release-notes).

### May 27, 2026

* The Messages API response now includes [`usage.output_tokens_details.thinking_tokens`](https://platform.claude.com/docs/en/build-with-claude/extended-thinking#budget-rules-and-tuning), reporting how many of the billed output tokens were extended thinking. When streaming, the breakdown appears only on the final `message_delta` event. No beta header is required.

### May 19, 2026

* [MCP tunnels](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview) is now available as a research preview, so you can connect to MCP servers in your private network.
* Self-hosted sandboxes are now available for Claude Managed Agents, as an alternative to running tool execution in Anthropic's infrastructure. See [Self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes).
* With Claude Managed Agents, you can now update the agent's MCP server and tool configurations associated with an active session.
* With Claude Managed Agents, large outputs from `agent_toolset` and MCP tools exceeding 100K characters (about 25K tokens) are now automatically spilled to a file in the sandbox. The model receives a truncated preview with the file path and can read the full content from there.

### May 18, 2026

* The [web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) now returns richer SEC filing data, making it easier to ground financial research agents, earnings analysis, and due-diligence workflows in primary sources with citations.

### May 13, 2026

* We've launched [cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics) in public beta. Pass `diagnostics.previous_message_id` on a Messages request and the API reports a `cache_miss_reason` explaining where the prompt cache prefix diverged from the previous turn. Include the `cache-diagnosis-2026-04-07` beta header in your requests.

### May 12, 2026

* [Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) (research preview) now supports Claude Opus 4.7. Set `speed: "fast"` with `model: "claude-opus-4-7"` and the `fast-mode-2026-02-01` beta header for significantly faster output token generation at premium pricing. Pricing, rate limits, and access are the same as for Opus 4.6 fast mode; interested customers should join the [waitlist](https://claude.com/fast-mode).

### May 11, 2026

* We've launched **Claude Platform on AWS**, bringing the Claude API to Anthropic-managed infrastructure accessible through AWS, with AWS billing and IAM authentication. Access the full Messages API, Files API, Message Batches API, Claude Managed Agents, Agent Skills, code execution, and tool use through native AWS endpoints. Learn more in [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws).

### May 6, 2026

* [Multiagent orchestration](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration) and [Outcomes](https://platform.claude.com/docs/en/managed-agents/define-outcomes) are now in public beta under the standard `managed-agents-2026-04-01` beta header.
* Claude Managed Agents vault credential background refresh is now supported for `mcp_oauth` credentials. See [Authenticate with vaults](https://platform.claude.com/docs/en/managed-agents/vaults).
* Webhooks for Claude Managed Agents are now supported. Webhook event types include session and vault lifecycle events. See [Subscribe to webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks).
* Additional filtering and sorting options are now supported for Claude Managed Agents. Sessions can be filtered by status, and events can be filtered by type. Events can now be filtered by creation time.
* [Dreams](https://platform.claude.com/docs/en/managed-agents/dreams) for Claude Managed Agents are now available as a research preview. A dream reads an existing memory store alongside past session transcripts and produces a reorganized output memory store with duplicates merged, stale entries replaced, and new insights surfaced. Dream endpoints are gated by the `dreaming-2026-04-21` beta header. [Request access](https://claude.com/form/claude-managed-agents) to try it.

### May 4, 2026

* We've launched [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation). Authenticate workloads to the Claude API with short-lived OIDC tokens from your own identity provider (AWS IAM, Google Cloud, GitHub Actions, Kubernetes, Microsoft Entra ID, Okta, SPIFFE, and more) instead of long-lived static API keys. Configure issuers and federation rules in the Claude Console, and the SDK handles token exchange and refresh automatically. See [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication).

### April 30, 2026

* We've retired the 1M token context window beta (`context-1m-2025-08-07`) for Claude Sonnet 4.5 and Claude Sonnet 4. The beta header now has no effect on these models, and requests exceeding the standard 200k-token context window return an error. To use the 1M context window, migrate to [Claude Sonnet 4.6](https://platform.claude.com/docs/en/models/overview#latest-models-comparison) or [Claude Opus 4.6](https://platform.claude.com/docs/en/models/overview#latest-models-comparison), where it's included at standard pricing with no beta header required.

### April 29, 2026

* We've released the [Claude API skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill), an open-source [Agent Skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) that gives Claude up-to-date reference material for building on the Messages API and Claude Managed Agents across 8 languages. The skill is bundled with Claude Code and available in the [Anthropic skills repository](https://github.com/anthropics/skills/tree/main/skills/claude-api).

### April 24, 2026

* We've released the [Rate Limits API](https://platform.claude.com/docs/en/manage-claude/rate-limits-api), allowing administrators to programmatically query the rate limits configured for their organization and workspaces.

### April 23, 2026

* Memory for Claude Managed Agents is now in public beta under the standard `managed-agents-2026-04-01` header. See [Using agent memory](https://platform.claude.com/docs/en/managed-agents/memory) for the full integration guide.

### April 20, 2026

* We've retired the Claude Haiku 3 model (`claude-3-haiku-20240307`). All requests to this model will now return an error. We recommend upgrading to [Claude Haiku 4.5](https://platform.claude.com/docs/en/models/overview#latest-models-comparison).

### April 16, 2026

* We've launched [Claude Opus 4.7](https://www.anthropic.com/news/claude-opus-4-7), our most capable widely released model for complex reasoning and agentic coding, at the same $5 / $25 per MTok pricing as Opus 4.6. See [What's new in Claude Opus 4.7](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7) for capability improvements, new features, and the updated tokenizer. Opus 4.7 includes API breaking changes versus Opus 4.6; see the [migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide) before upgrading.
* [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) is now open to all Amazon Bedrock customers. Claude Opus 4.7 and Claude Haiku 4.5 are available self-serve from the Bedrock console through the Messages API endpoint at `/anthropic/v1/messages`, in 27 AWS regions with global and regional endpoints.
* We've launched [task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets) in beta on Claude Opus 4.7. Give Claude an advisory token budget for a full agentic loop (thinking, tool calls, tool results, and output) and the model sees a running countdown, using it to prioritize work and finish gracefully as the budget is consumed. Include the `task-budgets-2026-03-13` beta header in your requests.
* Claude Opus 4.7 supports [high-resolution image input](https://platform.claude.com/docs/en/build-with-claude/vision#high-resolution-image-support-on-claude-opus-4-7), raising the maximum image resolution from 1568 to 2576 pixels on the long edge for improved performance on computer use, screenshot understanding, and document analysis. High-resolution support is automatic and requires no beta header; images may use up to approximately 3x more image tokens than on prior models.
* We've added the `xhigh` [effort](https://platform.claude.com/docs/en/build-with-claude/effort) level on Claude Opus 4.7. `xhigh` sits between `high` and `max` and is tuned for long-running agentic and coding tasks (over 30 minutes) with token budgets in the millions. No beta header is required.

### April 14, 2026

* We announced the deprecation of the Claude Sonnet 4 model (`claude-sonnet-4-20250514`) and the Claude Opus 4 model (`claude-opus-4-20250514`), with retirement on the Claude API scheduled for June 15, 2026. We recommend migrating to [Claude Sonnet 4.6](https://platform.claude.com/docs/en/models/overview#latest-models-comparison) and [Claude Opus 4.8](https://platform.claude.com/docs/en/about-claude/models/migration-guide) respectively. Read more in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).

### April 9, 2026

* We've launched the [advisor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) in public beta. Pair a faster executor model with a higher-intelligence advisor model that provides strategic guidance mid-generation, so long-horizon agentic workloads get close to advisor-solo quality while the bulk of token generation happens at executor-model rates. Include the beta header `advisor-tool-2026-03-01` in your requests.

### April 8, 2026

* We've launched **Claude Managed Agents** in public beta, a fully managed agent harness for running Claude as an autonomous agent with secure sandboxing, built-in tools, and server-sent event streaming. Create agents, configure containers, and run sessions through the API. All endpoints require the `managed-agents-2026-04-01` beta header. Learn more in [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview).
* We've launched the **`ant` CLI**, a command-line client for the Claude API that enables faster interaction with the Claude API, native integration with Claude Code, and versioning of API resources in YAML files. Learn more in the [CLI quickstart](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/quickstart).

### April 7, 2026

* We announced [Claude Mythos Preview](https://anthropic.com/glasswing) is available as a gated research preview for defensive cybersecurity work as part of [Project Glasswing](https://anthropic.com/glasswing). Access is invitation-only.
* The [Messages API](https://platform.claude.com/docs/en/api/messages) is now available on Amazon Bedrock as a research preview. The new Claude in Amazon Bedrock endpoint at `/anthropic/v1/messages` uses the same request shape as the first-party Claude API and runs on AWS-managed infrastructure with zero operator access. Available in `us-east-1`; contact your Anthropic account executive to request access. Learn more in [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock).

### March 30, 2026

* We've raised the `max_tokens` cap to 300k on the [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing#extended-output-beta) for Claude Opus 4.6 and Sonnet 4.6. Include the `output-300k-2026-03-24` beta header to generate longer single-turn outputs for long-form content, structured data, and large code generation tasks.
* We're retiring the 1M token context window beta for Claude Sonnet 4.5 and Claude Sonnet 4 on **April 30, 2026**. After that date, the `context-1m-2025-08-07` beta header will have no effect on these models, and requests that exceed the standard 200k-token context window will return an error. To continue using 1M context windows, migrate to [Claude Sonnet 4.6](https://platform.claude.com/docs/en/models/overview#latest-models-comparison) or [Claude Opus 4.6](https://platform.claude.com/docs/en/models/overview#latest-models-comparison), which support the full 1M token context window at standard pricing with no beta header required.

### March 18, 2026

* We've added model capability fields to the [Models API](https://platform.claude.com/docs/en/api/models/list). `GET /v1/models` and `GET /v1/models/{model_id}` now return `max_input_tokens`, `max_tokens`, and a `capabilities` object. Query the API to discover what each model supports.

### March 16, 2026

* We've launched the `display` field for extended thinking, letting you omit thinking content from responses for faster streaming. Set `thinking.display: "omitted"` to receive thinking blocks with an empty `thinking` field and the `signature` preserved for multi-turn continuity. Billing is unchanged. Learn more in [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display).

### March 13, 2026

* The [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) is out of beta for Claude Opus 4.6 and Sonnet 4.6, at standard pricing. Requests over 200k tokens work automatically for these models with no beta header required. The 1M token context window remains in beta for Claude Sonnet 4.5 and Sonnet 4.
* We've removed the dedicated 1M rate limits for all supported models. Your standard account limits now apply across every context length.
* We've raised the media limit from 100 to 600 images or PDF pages per request when using the 1M token context window.

### February 19, 2026

* We've launched **automatic caching** for the Messages API. Add a single `cache_control` field to your request body and the system automatically caches the last cacheable block, moving the cache point forward as conversations grow. No manual breakpoint management required. Works alongside existing block-level cache control for fine-grained optimization. Available on the Claude API and Microsoft Foundry (preview). Learn more in [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#automatic-caching).
* We've retired the Claude Sonnet 3.7 model (`claude-3-7-sonnet-20250219`) and the Claude Haiku 3.5 model (`claude-3-5-haiku-20241022`). All requests to Claude Sonnet 3.7 will now return an error. Requests to Claude Haiku 3.5 on the Claude API will now return an error; it remains available on Amazon Bedrock and Google Cloud. We recommend upgrading to [Claude Sonnet 4.6](https://platform.claude.com/docs/en/models/overview#latest-models-comparison) and [Claude Haiku 4.5](https://platform.claude.com/docs/en/models/overview#latest-models-comparison) respectively. Researchers can request ongoing access through the [External Researcher Access Program](https://support.claude.com/en/articles/9125743-what-is-the-external-researcher-access-program).
* We announced the deprecation of the Claude Haiku 3 model (`claude-3-haiku-20240307`), with retirement scheduled for April 20, 2026. We recommend migrating to [Claude Haiku 4.5](https://platform.claude.com/docs/en/models/overview#latest-models-comparison). Read more in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).

### February 17, 2026

* We've launched [Claude Sonnet 4.6](https://www.anthropic.com/news/claude-sonnet-4-6), our latest balanced model combining speed and intelligence for everyday tasks. Sonnet 4.6 delivers improved agentic search performance while consuming fewer tokens. Sonnet 4.6 supports [extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) and a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) (beta). See [Models & Pricing](https://platform.claude.com/docs/en/about-claude/models) for details.
* API [code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) is now **free when used with web search or web fetch**. Sandboxed code execution improves model capability and token efficiency. See the [pricing details](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#usage-and-pricing) for standalone usage.
* The [web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) and [programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling) are available with no beta header required. Web search and web fetch now support [dynamic filtering](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool#dynamic-filtering), which uses code execution to filter results before they reach the context window for better performance and reduced token cost.
* The [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool), [web fetch tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool), [tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool), [tool use examples](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools#providing-tool-use-examples), and [memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) no longer require a beta header.

### February 7, 2026

* We've launched [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) in research preview for Opus 4.6, providing significantly faster output token generation through the `speed` parameter. Fast mode is up to 2.5x as fast at premium pricing. Interested customers should join the [waitlist](https://claude.com/fast-mode).

### February 5, 2026

* We've launched [Claude Opus 4.6](https://www.anthropic.com/news/claude-opus-4-6), our most intelligent model for complex agentic tasks and long-horizon work. Opus 4.6 recommends [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) (`thinking: {type: "adaptive"}`); manual thinking (`type: "enabled"` with `budget_tokens`) is deprecated. Opus 4.6 does not support prefilling assistant messages. Learn more in [What's new in Claude 4.6](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6).
* The [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) no longer requires a beta header and now supports Claude Opus 4.6. Effort replaces `budget_tokens` for controlling thinking depth on new models.
* We've launched the [compaction API](https://platform.claude.com/docs/en/build-with-claude/compaction) in beta, providing server-side context summarization for effectively infinite conversations. Available on Opus 4.6.
* We've introduced [data residency controls](https://platform.claude.com/docs/en/manage-claude/data-residency), allowing you to specify where model inference runs with the `inference_geo` parameter. US-only inference is available at 1.1x pricing for models released after February 1, 2026.
* The [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) is now available in beta for Claude Opus 4.6, in addition to Sonnet 4.5 and Sonnet 4. [Long context pricing](https://platform.claude.com/docs/en/about-claude/pricing#long-context-pricing) applies to requests exceeding 200k input tokens.
* [Fine-grained tool streaming](https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming) no longer requires a beta header on any model or platform.

### January 29, 2026

* [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) are out of beta on the Claude API for Claude Sonnet 4.5, Claude Opus 4.5, and Claude Haiku 4.5. This release includes expanded schema support, improved grammar compilation latency, and a simplified integration path with no beta header required. The `output_format` parameter has moved to `output_config.format`. Existing beta users can continue using the beta header during the transition period. Structured outputs remain in public beta on Amazon Bedrock and Microsoft Foundry.

### January 12, 2026

* `console.anthropic.com` now redirects to `platform.claude.com`. The Claude Console has moved to its new home as part of our Claude brand consolidation. Existing bookmarks and links will continue working through an automatic redirect. For more details, see the [September 16, 2025 announcement](https://platform.claude.com/docs/en/release-notes/overview#september-16-2025).

### January 5, 2026

* We've retired the Claude Opus 3 model (`claude-3-opus-20240229`). All requests to this model will now return an error. We recommend upgrading to [Claude Opus 4.5](https://platform.claude.com/docs/en/models/overview#latest-models-comparison), which offers significantly improved intelligence at a third of the cost. Researchers can request ongoing access to Claude Opus 3 on the API through the [External Researcher Access Program](https://support.claude.com/en/articles/9125743-what-is-the-external-researcher-access-program).

### December 19, 2025

* We announced the deprecation of the Claude Haiku 3.5 model. Read more in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).

### December 4, 2025

* [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) now supports Claude Haiku 4.5.

### November 24, 2025

* We've launched [Claude Opus 4.5](https://www.anthropic.com/news/claude-opus-4-5), our most intelligent model combining maximum capability with practical performance. Ideal for complex specialized tasks, professional software engineering, and advanced agents. Features step-change improvements in vision, coding, and computer use at a more accessible price point than previous Opus models. Learn more in [Models overview](https://platform.claude.com/docs/en/about-claude/models).
* We've launched [programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling) in public beta, allowing Claude to call tools from within code execution to reduce latency and token usage in multi-tool workflows.
* We've launched the [tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) in public beta, enabling Claude to dynamically discover and load tools on-demand from large tool catalogs.
* We've launched the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) in public beta for Claude Opus 4.5, allowing you to control token usage by trading off between response thoroughness and efficiency.
* We've added [client-side compaction](https://platform.claude.com/docs/en/build-with-claude/context-editing#client-side-compaction-sdk) to our Python and TypeScript SDKs, automatically managing conversation context through summarization when using `tool_runner`.

### November 21, 2025

* Search result content blocks are now available on Amazon Bedrock with no beta header required. Learn more in [Search results](https://platform.claude.com/docs/en/build-with-claude/search-results).

### November 19, 2025

* We've launched a **new documentation platform** at [platform.claude.com/docs](https://platform.claude.com/docs). Our documentation now lives side by side with the Claude Console, providing a unified developer experience. The previous docs site at docs.claude.com will redirect to the new location.

### November 18, 2025

* We've launched **Claude in Microsoft Foundry**, bringing Claude models to Azure customers with Azure billing and OAuth authentication. Access the full Messages API including extended thinking, prompt caching (5-minute and 1-hour), PDF support, Files API, Agent Skills, and tool use. Learn more in [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry).

### November 14, 2025

* We've launched [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) in public beta, providing guaranteed schema conformance for Claude's responses. Use JSON outputs for structured data responses or strict tool use for validated tool inputs. Available for Claude Sonnet 4.5 and Claude Opus 4.1. To enable, use the beta header `structured-outputs-2025-11-13`.

### October 28, 2025

* We announced the deprecation of the Claude Sonnet 3.7 model. Read more in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).
* We've retired the Claude Sonnet 3.5 models. All requests to these models will now return an error.
* We've expanded context editing with thinking block clearing (`clear_thinking_20251015`), enabling automatic management of thinking blocks. Learn more in [Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing).

### October 16, 2025

* We've launched [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) (`skills-2025-10-02` beta), a new way to extend Claude's capabilities. Skills are organized folders of instructions, scripts, and resources that Claude loads dynamically to perform specialized tasks. The initial release includes:

  * **Anthropic-managed Skills**: Pre-built Skills for working with PowerPoint (.pptx), Excel (.xlsx), Word (.docx), and PDF files
  * **Custom Skills**: Upload your own Skills through the Skills API (`/v1/skills` endpoints) to package domain expertise and organizational workflows
  * Skills require the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) to be enabled
  * Learn more in [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) and [API reference](https://platform.claude.com/docs/en/api/skills/create)

### October 15, 2025

* We've launched [Claude Haiku 4.5](https://www.anthropic.com/news/claude-haiku-4-5), our fastest and most intelligent Haiku model with near-frontier performance. Ideal for real-time applications, high-volume processing, and cost-sensitive deployments requiring strong reasoning. Learn more in [Models overview](https://platform.claude.com/docs/en/about-claude/models).

### September 29, 2025

* We've launched [Claude Sonnet 4.5](https://www.anthropic.com/news/claude-sonnet-4-5), our best model for complex agents and coding, with the highest intelligence across most tasks. Learn more in the [models overview](https://platform.claude.com/docs/en/models/overview).
* We've introduced [global endpoint pricing](https://platform.claude.com/docs/en/about-claude/pricing#cloud-platform-pricing) for Amazon Bedrock and Vertex AI. The Claude API (1P) pricing is unaffected.
* We've introduced a new stop reason `model_context_window_exceeded` that allows you to request the maximum possible tokens without calculating input size. Learn more in [Handling stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons).
* We've launched the memory tool in beta, enabling Claude to store and consult information across conversations. Learn more in [Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool).
* We've launched context editing in beta, providing strategies to automatically manage conversation context. The initial release supports clearing older tool results and calls when approaching token limits. Learn more in [Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing).

### September 17, 2025

* We've launched tool helpers in beta for the Python and TypeScript SDKs, simplifying tool creation and execution with type-safe input validation and a tool runner for automated tool handling in conversations. For details, see the documentation for [the Python SDK](https://github.com/anthropics/anthropic-sdk-python/blob/main/tools.md) and [the TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript/blob/main/helpers.md#tool-helpers).

### September 16, 2025

* We've unified our developer offerings under the Claude brand. You should see updated naming and URLs across our platform and documentation, but **our developer interfaces will remain the same**. Here are some notable changes:

  * Claude Console ([console.anthropic.com](https://console.anthropic.com)) → Claude Console ([platform.claude.com](https://platform.claude.com)). The console will be available at both URLs until January 12, 2026. After that date, [console.anthropic.com](https://console.anthropic.com) will automatically redirect to [platform.claude.com](https://platform.claude.com).
  * Anthropic Docs ([docs.anthropic.com](https://docs.anthropic.com)) → Claude Docs ([docs.claude.com](https://docs.claude.com))
  * Anthropic Help Center ([support.anthropic.com](https://support.anthropic.com)) → Claude Help Center ([support.claude.com](https://support.claude.com))
  * API endpoints, headers, environment variables, and SDKs remain the same. Your existing integrations will continue working without any changes.

### September 10, 2025

* We've launched the web fetch tool in beta, allowing Claude to retrieve full content from specified web pages and PDF documents. Learn more in [Web fetch tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool).
* We've launched the [Claude Code Analytics API](https://platform.claude.com/docs/en/manage-claude/claude-code-analytics-api), enabling organizations to programmatically access daily aggregated usage metrics for Claude Code, including productivity metrics, tool usage statistics, and cost data.

### September 8, 2025

* We launched a beta version of the [C# SDK](https://github.com/anthropics/anthropic-sdk-csharp).

### September 5, 2025

* We've launched [rate limit charts](https://platform.claude.com/docs/en/api/rate-limits#monitoring-your-rate-limits-in-the-console) in the Console [Usage](https://console.anthropic.com/settings/usage) page, allowing you to monitor your API rate limit usage and caching rates over time.

### September 3, 2025

* We've launched support for citable documents in client-side tool results. Learn more in [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls).

### September 2, 2025

* We've launched v2 of the [Code Execution Tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) in public beta, replacing the original Python-only tool with Bash command execution and direct file manipulation capabilities, including writing code in other languages.

### August 27, 2025

* We launched a beta version of the [PHP SDK](https://github.com/anthropics/anthropic-sdk-php).

### August 26, 2025

* We've increased rate limits on the [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) for Claude Sonnet 4 on the Claude API.
* The 1M token context window is now available on Vertex AI. For more information, see [Claude on Vertex AI](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai).

### August 19, 2025

* Request IDs are now included directly in error response bodies alongside the existing `request-id` header. Learn more in [Errors](https://platform.claude.com/docs/en/api/errors#error-shapes).

### August 18, 2025

* We've released the [Usage & Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api), allowing administrators to programmatically monitor their organization's usage and cost data.
* We've added a new endpoint to the Admin API for retrieving organization information. For details, see the [Organization Info Admin API reference](https://platform.claude.com/docs/en/api/admin-api/organization/get-me).

### August 13, 2025

* We announced the deprecation of the Claude Sonnet 3.5 models (`claude-3-5-sonnet-20240620` and `claude-3-5-sonnet-20241022`). These models will be retired on October 28, 2025. We recommend migrating to Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) for improved performance and capabilities. Read more in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).
* The 1-hour cache duration for prompt caching no longer requires a beta header. Learn more in [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#1-hour-cache-duration).

### August 12, 2025

* We've launched beta support for a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) in Claude Sonnet 4 on the Claude API and Amazon Bedrock.

### August 11, 2025

* Some customers might encounter 429 (`rate_limit_error`) [errors](https://platform.claude.com/docs/en/api/errors) following a sharp increase in API usage due to acceleration limits on the API. Previously, 529 (`overloaded_error`) errors would occur in similar scenarios.

### August 8, 2025

* Search result content blocks are out of beta on the Claude API and Vertex AI. This feature enables natural citations for RAG applications with proper source attribution. The beta header `search-results-2025-06-09` is no longer required. Learn more in [Search results](https://platform.claude.com/docs/en/build-with-claude/search-results).

### August 5, 2025

* We've launched [Claude Opus 4.1](https://www.anthropic.com/news/claude-opus-4-1), an incremental update to Claude Opus 4 with enhanced capabilities and performance improvements.\* Learn more in [Models overview](https://platform.claude.com/docs/en/about-claude/models).

*\*Opus 4.1 does not allow both `temperature` and `top_p` parameters to be specified. Please use only one.*

### July 28, 2025

* We've released `text_editor_20250728`, an updated text editor tool that fixes some issues from the previous versions and adds an optional `max_characters` parameter that allows you to control the truncation length when viewing large files.

### July 24, 2025

* We've increased [rate limits](https://platform.claude.com/docs/en/api/rate-limits) for Claude Opus 4 on the Claude API to give you more capacity to build and scale with Claude. For customers with [usage tier 1-4 rate limits](https://platform.claude.com/docs/en/api/rate-limits#rate-limits), these changes apply immediately to your account - no action needed.

### July 21, 2025

* We've retired the Claude 2.0, Claude 2.1, and Claude Sonnet 3 models. All requests to these models will now return an error. Read more in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).

### July 17, 2025

* We've increased [rate limits](https://platform.claude.com/docs/en/api/rate-limits) for Claude Sonnet 4 on the Claude API to give you more capacity to build and scale with Claude. For customers with [usage tier 1-4 rate limits](https://platform.claude.com/docs/en/api/rate-limits#rate-limits), these changes apply immediately to your account - no action needed.

### July 3, 2025

* We've launched search result content blocks in beta, enabling natural citations for RAG applications. Tools can now return search results with proper source attribution, and Claude will automatically cite these sources in its responses - matching the citation quality of web search. This eliminates the need for document workarounds in custom knowledge base applications. Learn more in [Search results](https://platform.claude.com/docs/en/build-with-claude/search-results). To enable this feature, use the beta header `search-results-2025-06-09`.

### June 30, 2025

* We announced the deprecation of the Claude Opus 3 model. Read more in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).

### June 23, 2025

* Console users with the Developer role can now access the [Cost](https://console.anthropic.com/settings/cost) page. Previously, the Developer role allowed access to the [Usage](https://console.anthropic.com/settings/usage) page, but not the Cost page.

### June 11, 2025

* We've launched [fine-grained tool streaming](https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming) in public beta, a feature that enables Claude to stream tool use parameters without buffering / JSON validation. To enable fine-grained tool streaming, use the [beta header](https://platform.claude.com/docs/en/api/beta-headers) `fine-grained-tool-streaming-2025-05-14`.

### May 22, 2025

* We've launched [Claude Opus 4 and Claude Sonnet 4](https://www.anthropic.com/news/claude-4), our latest models with extended thinking capabilities. Learn more in [Models overview](https://platform.claude.com/docs/en/about-claude/models).
* The default behavior of [extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) in Claude 4 models returns a summary of Claude's full thinking process, with the full thinking encrypted and returned in the `signature` field of `thinking` block output.
* We've launched [interleaved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#interleaved-thinking) in public beta, a feature that enables Claude to think in between tool calls. To enable interleaved thinking, use the [beta header](https://platform.claude.com/docs/en/api/beta-headers) `interleaved-thinking-2025-05-14`.
* We've launched the [Files API](https://platform.claude.com/docs/en/build-with-claude/files) in public beta, enabling you to upload files and reference them in the Messages API and code execution tool.
* We've launched the [Code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) in public beta, a tool that enables Claude to execute Python code in a secure, sandboxed environment.
* We've launched the [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector) in public beta, a feature that allows you to connect to remote MCP servers directly from the Messages API.
* To increase answer quality and decrease tool errors, we've changed the default value for the `top_p` [nucleus sampling](https://en.wikipedia.org/wiki/Top-p_sampling) parameter in the Messages API from 0.999 to 0.99 for all models. To revert this change, set `top_p` to 0.999. Additionally, when extended thinking is enabled, you can now set `top_p` to values between 0.95 and 1.
* Our [Go SDK](https://github.com/anthropics/anthropic-sdk-go) has moved from beta to its first stable release.
* We've included minute and hour level granularity to the [Usage](https://console.anthropic.com/settings/usage) page of Console alongside 429 error rates on the Usage page.

### May 21, 2025

* Our [Ruby SDK](https://github.com/anthropics/anthropic-sdk-ruby) has moved from beta to its first stable release.

### May 7, 2025

* We've launched a web search tool in the API, allowing Claude to access up-to-date information from the web. Learn more in [Web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool).

### May 1, 2025

* Cache control must now be specified directly in the parent `content` block of `tool_result` and `document.source`. For backwards compatibility, if cache control is detected on the last block in `tool_result.content` or `document.source.content`, it will be automatically applied to the parent block instead. Cache control on any other blocks within `tool_result.content` and `document.source.content` will result in a validation error.

### April 9th, 2025

* We launched a beta version of the [Ruby SDK](https://github.com/anthropics/anthropic-sdk-ruby).

### March 31st, 2025

* Our [Java SDK](https://github.com/anthropics/anthropic-sdk-java) has moved from beta to its first stable release.
* We've moved our [Go SDK](https://github.com/anthropics/anthropic-sdk-go) from alpha to beta.

### February 27th, 2025

* We've added URL source blocks for images and PDFs in the Messages API. You can now reference images and PDFs directly through a URL instead of having to base64-encode them. Learn more in [Vision](https://platform.claude.com/docs/en/build-with-claude/vision) and [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support).
* We've added support for a `none` option to the `tool_choice` parameter in the Messages API that prevents Claude from calling any tools. Additionally, you're no longer required to provide any `tools` when including `tool_use` and `tool_result` blocks.
* We've launched an OpenAI-compatible API endpoint, allowing you to test Claude models by changing just your API key, base URL, and model name in existing OpenAI integrations. This compatibility layer supports core chat completions functionality. Learn more in [OpenAI SDK compatibility](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk).

### February 24th, 2025

* We've launched [Claude Sonnet 3.7](https://www.anthropic.com/news/claude-3-7-sonnet), our most intelligent model yet. Claude Sonnet 3.7 can produce near-instant responses or show its extended thinking step-by-step. One model, two ways to think. Learn more about all Claude models in [Models overview](https://platform.claude.com/docs/en/about-claude/models).

* We've added vision support to Claude Haiku 3.5, enabling the model to analyze and understand images.

* We've released a token-efficient tool use implementation, improving overall performance when using tools with Claude. Learn more in [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).

* We've changed the default temperature in the [Console](https://console.anthropic.com/workbench) for new prompts from 0 to 1 for consistency with the default temperature in the API. Existing saved prompts are unchanged.

* We've released updated versions of our tools that decouple the text edit and bash tools from the computer use system prompt:

  * `bash_20250124`: Same functionality as previous version but is independent from computer use. Does not require a beta header.
  * `text_editor_20250124`: Same functionality as previous version but is independent from computer use. Does not require a beta header.
  * `computer_20250124`: Updated computer use tool with new command options including "hold\_key", "left\_mouse\_down", "left\_mouse\_up", "scroll", "triple\_click", and "wait". This tool requires the "computer-use-2025-01-24" anthropic-beta header. Learn more in [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).

### February 10th, 2025

* We've added the `anthropic-organization-id` response header to all API responses. This header provides the organization ID associated with the API key used in the request.

### January 31st, 2025

* We've moved our [Java SDK](https://github.com/anthropics/anthropic-sdk-java) from alpha to beta.

### January 23rd, 2025

* We've launched citations capability in the API, allowing Claude to provide source attribution for information. Learn more in [Citations](https://platform.claude.com/docs/en/build-with-claude/citations).
* We've added support for plain text documents and custom content documents in the Messages API.

### January 21st, 2025

* We announced the deprecation of the Claude 2, Claude 2.1, and Claude Sonnet 3 models. Read more in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).

### January 15th, 2025

* We've updated [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) to be easier to use. Now, when you set a cache breakpoint, we'll automatically read from your longest previously cached prefix.
* You can now put words in Claude's mouth when using tools.

### January 10th, 2025

* We've optimized support for [prompt caching in the Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing#using-prompt-caching-with-message-batches) to improve cache hit rate.

### December 19th, 2024

* We've added support for a [delete endpoint](https://platform.claude.com/docs/en/api/deleting-message-batches) in the Message Batches API.

### December 17th, 2024

The following features are now available in the Claude API without a beta header:

* [Models API](https://platform.claude.com/docs/en/api/models/list): Query available models, validate model IDs, and resolve [model aliases](https://platform.claude.com/docs/en/models/overview) to their canonical model IDs.
* [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing): Process large batches of messages asynchronously at 50% of the standard API cost.
* [Token counting API](https://platform.claude.com/docs/en/build-with-claude/token-counting): Calculate token counts for Messages before sending them to Claude.
* [Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching): Reduce costs by up to 90% and latency by up to 80% by caching and reusing prompt content.
* [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support): Process PDFs to analyze both text and visual content within documents.

We also released new official SDKs:

* [Java SDK](https://github.com/anthropics/anthropic-sdk-java) (alpha)
* [Go SDK](https://github.com/anthropics/anthropic-sdk-go) (alpha)

### December 4th, 2024

* We've added the ability to group by API key on the [Usage](https://console.anthropic.com/settings/usage) and [Cost](https://console.anthropic.com/settings/cost) pages of the [Developer Console](https://console.anthropic.com).
* We've added two new **Last used at** and **Cost** columns and the ability to sort by any column on the [API keys](https://console.anthropic.com/settings/keys) page of the [Developer Console](https://console.anthropic.com).

### November 21st, 2024

* We've released the [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api), allowing users to programmatically manage their organization's resources.

### November 20th, 2024

* We've updated our rate limits for the Messages API. We've replaced the tokens per minute rate limit with new input and output tokens per minute rate limits. Read more in [Rate limits](https://platform.claude.com/docs/en/api/rate-limits).
* We've added support for [tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) in the [Workbench](https://console.anthropic.com/workbench).

### November 13th, 2024

* We've added PDF support for all Claude Sonnet 3.5 models. Read more in [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support).

### November 6th, 2024

* We've retired the Claude 1 and Instant models. Read more in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).

### November 4th, 2024

* [Claude Haiku 3.5](https://www.anthropic.com/claude/haiku) is now available on the Claude API as a text-only model.

### November 1st, 2024

* We've added PDF support for use with the new Claude Sonnet 3.5. Read more in [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support).
* We've also added token counting, which allows you to determine the total number of tokens in a Message prior to sending it to Claude. Read more in [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting).

### October 22nd, 2024

* We've added Anthropic-defined computer use tools to our API for use with the new Claude Sonnet 3.5. Read more in [Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool).
* Claude Sonnet 3.5, our most intelligent model yet, just got an upgrade and is now available on the Claude API. Read more in the [Claude Sonnet documentation](https://www.anthropic.com/claude/sonnet).

### October 8th, 2024

* The Message Batches API is now available in beta. Process large batches of queries asynchronously in the Claude API for 50% less cost. Read more in [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing).
* We've loosened restrictions on the ordering of `user`/`assistant` turns in our Messages API. Consecutive `user`/`assistant` messages will be combined into a single message instead of erroring, and we no longer require the first input message to be a `user` message.
* We've deprecated the Build and Scale plans in favor of a standard feature suite (formerly referred to as Build), along with additional features that are available through sales. Read more in our [API pricing information](https://claude.com/platform/api).

### October 3rd, 2024

* We've added the ability to disable parallel tool use in the API. Set `disable_parallel_tool_use: true` in the `tool_choice` field to ensure that Claude uses at most one tool. Read more in [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use).

### September 10th, 2024

* We've added Workspaces to the [Developer Console](https://console.anthropic.com). Workspaces allow you to set custom spend or rate limits, group API keys, track usage by project, and control access with user roles. Read more in our [blog post](https://www.anthropic.com/news/workspaces).

### September 4th, 2024

* We announced the deprecation of the Claude 1 models. Read more in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).

### August 22nd, 2024

* We've added support for usage of the SDK in browsers by returning CORS headers in the API responses. Set `dangerouslyAllowBrowser: true` in the SDK instantiation to enable this feature.

### August 19th, 2024

* 8,192-token outputs on Claude Sonnet 3.5 are out of beta and no longer require the `max-tokens-3-5-sonnet-2024-07-15` header.

### August 14th, 2024

* [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) is now available as a beta feature in the Claude API. Cache and re-use prompts to reduce latency by up to 80% and costs by up to 90%.

### July 15th, 2024

* Generate outputs up to 8,192 tokens in length from Claude Sonnet 3.5 with the new `anthropic-beta: max-tokens-3-5-sonnet-2024-07-15` header.

### July 9th, 2024

* Automatically generate test cases for your prompts using Claude in the [Developer Console](https://console.anthropic.com).
* Compare the outputs from different prompts side by side in the new output comparison mode in the [Developer Console](https://console.anthropic.com).

### June 27th, 2024

* View API usage and billing broken down by dollar amount, token count, and API keys in the new [Usage](https://console.anthropic.com/settings/usage) and [Cost](https://console.anthropic.com/settings/cost) tabs in the [Developer Console](https://console.anthropic.com).
* View your current API rate limits in the new [Rate Limits](https://console.anthropic.com/settings/limits) tab in the [Developer Console](https://console.anthropic.com).

### June 20th, 2024

* [Claude Sonnet 3.5](https://www.anthropic.com/news/claude-3-5-sonnet), our most intelligent model yet, is now available across the Claude API, Amazon Bedrock, and Vertex AI.

### May 30th, 2024

* [Tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) is out of beta across the Claude API, Amazon Bedrock, and Vertex AI, with no beta header required.

### May 10th, 2024

* Our prompt generator tool is now available in the [Developer Console](https://console.anthropic.com). Prompt Generator makes it easy to guide Claude to generate a high-quality prompts tailored to your specific tasks. Read more in our [blog post](https://www.anthropic.com/news/prompt-generator).


## API Reference

Source: https://platform.claude.com/llms-full.txt#api-reference-2

### Public API

---
title: Acknowledge Work
url: https://platform.claude.com/docs/en/api/beta/environments/work/ack
---


## Acknowledge Work

Source: https://platform.claude.com/llms-full.txt#acknowledge-work

**post** `/v1/environments/{environment_id}/work/{work_id}/ack`

Note: these endpoints are called automatically by the pre-built environment worker provided in the SDKs and CLI, for orchestrating sessions with self-hosted sandbox environments. They are included here as a reference; you do not need to invoke them directly.

Acknowledge receipt of a work item, transitioning it from 'queued' to 'starting' and removing it from the queue.

### Path Parameters

- `environment_id: string`

- `work_id: string`

### Header Parameters

- `"anthropic-beta": optional array of AnthropicBeta`

  Optional header to specify the beta version(s) you want to use.

  - `string`

  - `"message-batches-2024-09-24" or "prompt-caching-2024-07-31" or "computer-use-2024-10-22" or 41 more`

    - `"message-batches-2024-09-24"`

    - `"prompt-caching-2024-07-31"`

    - `"computer-use-2024-10-22"`

    - `"computer-use-2025-01-24"`

    - `"pdfs-2024-09-25"`

    - `"token-counting-2024-11-01"`

    - `"token-efficient-tools-2025-02-19"`

    - `"output-128k-2025-02-19"`

    - `"files-api-2025-04-14"`

    - `"mcp-client-2025-04-04"`

    - `"mcp-client-2025-11-20"`

    - `"dev-full-thinking-2025-05-14"`

    - `"interleaved-thinking-2025-05-14"`

    - `"code-execution-2025-05-22"`

    - `"extended-cache-ttl-2025-04-11"`

    - `"context-1m-2025-08-07"`

    - `"context-management-2025-06-27"`

    - `"model-context-window-exceeded-2025-08-26"`

    - `"skills-2025-10-02"`

    - `"fast-mode-2026-02-01"`

    - `"output-300k-2026-03-24"`

    - `"user-profiles-2026-03-24"`

    - `"user-profiles-2026-08-18"`

    - `"advisor-tool-2026-03-01"`

    - `"managed-agents-2026-04-01"`

    - `"cache-diagnosis-2026-04-07"`

    - `"dreaming-2026-04-21"`

    - `"thinking-token-count-2026-05-13"`

    - `"server-side-fallback-2026-06-01"`

    - `"server-side-fallback-2026-07-01"`

    - `"fallback-credit-2026-06-01"`

    - `"fallback-credit-2026-07-01"`

    - `"agent-memory-2026-07-22"`

    - `"mid-conversation-tool-changes-2026-07-01"`

    - `"compact-2026-01-12"`

    - `"computer-use-2025-11-24"`

    - `"mcp-tunnels-2026-06-22"`

    - `"structured-outputs-2025-11-13"`

    - `"task-budgets-2026-03-13"`

    - `"thinking-display-updates-2026-08-18"`

    - `"ce-user-management-2026-07-13"`

    - `"mid-conversation-output-config-2026-07-01"`

    - `"thinking-binding-controls-2026-08-01"`

    - `"mid-conversation-system-clear-at-2026-08-21"`

### Returns

- `BetaSelfHostedWork object { id, acknowledged_at, created_at, 10 more }`

  Work resource representing a unit of work in a self-hosted environment.

  Work items are queued when sessions are created or when long-dormant sessions
  receive new messages. The environment worker polls for work to execute in a
  self-hosted sandbox.

  - `id: string`

    Work identifier (e.g., 'work_...')

  - `acknowledged_at: string or null`

    RFC 3339 timestamp when the work item was acknowledged and assigned to a self-hosted sandbox

  - `created_at: string`

    RFC 3339 timestamp when work was created

  - `data: BetaSessionWorkData`

    The actual work to be performed

    - `id: string`

      Session identifier (e.g., 'session_...')

    - `type: "session"`

      Type of work data

      - `"session"`

  - `environment_id: string`

    Environment identifier this work belongs to (e.g., `env_...`)

  - `latest_heartbeat_at: string or null`

    RFC 3339 timestamp of the most recent heartbeat

  - `metadata: map[string]`

    User-provided metadata key-value pairs associated with this work item

  - `secret: string or null`

    Credential payload used by the environment worker to execute this work item. May be populated when polling for work; null on all other retrieval paths.

  - `started_at: string or null`

    RFC 3339 timestamp when work execution started

  - `state: "queued" or "starting" or "active" or 2 more`

    Current state of the work item

    - `"queued"`

    - `"starting"`

    - `"active"`

    - `"stopping"`

    - `"stopped"`

  - `stop_requested_at: string or null`

    RFC 3339 timestamp when stop was requested

  - `stopped_at: string or null`

    RFC 3339 timestamp when work execution stopped

  - `type: "work"`

    The type of object (always 'work')

    - `"work"`

### Example

#### Response

---
title: Activities
url: https://platform.claude.com/docs/en/api/compliance/activities
---

# Activities


## Query compliance activities

Source: https://platform.claude.com/llms-full.txt#query-compliance-activities

**get** `/v1/compliance/activities`

List compliance activities for the authenticated tenant.

The tenant is the caller's parent organization, or — for an organization
with no parent — the organization itself. Returns a paginated list of
compliance activities that can be filtered by various criteria.

### Query Parameters

- `activity_types: optional array of "abuse_decision_received" or "account_deleted" or "admin_api_key_created" or 480 more`

  Filter activities by type. See the response `data` schema for the additional fields each type returns. Cannot be combined with `exclude_activity_types[]`.

  - `"abuse_decision_received"`

    An external anti-abuse service reported a consequential decision about a sign-in or sign-up attempt.

  - `"account_deleted"`

    User-initiated self-service account deletion.

  - `"admin_api_key_created"`

    An admin API key was created.

  - `"admin_api_key_deleted"`

    An admin API key was deleted.

  - `"admin_api_key_updated"`

    An admin API key was updated (renamed or activated/deactivated).

  - `"admin_connector_request_resolved"`

    Admin approved or dismissed pending member requests to enable an MCP connector.

  - `"admin_request_created"`

    Admin request created by an org member (seat upgrade, limit increase, join org, end-user invite).

  - `"age_verified"`

    User age was verified.

  - `"anonymous_mobile_login_attempted"`

    Anonymous mobile login was attempted.

  - `"api_key_created"`

    Activity logged when a new API key is created.

  - `"audit_log_export_accessed"`

    Audit log export file was accessed/downloaded via signed URL.

  - `"audit_log_export_started"`

    Audit log export was initiated.

  - `"billing_emails_updated"`

    The organization's billing email recipients were updated.

  - `"ccr_agent_created"`

    A Claude Code agent was created.

  - `"ccr_agent_deleted"`

    A Claude Code agent was deleted.

  - `"ccr_agent_proxy_credential_created"`

    A Claude Code agent proxy credential was created. Credentials hold the secrets the agent proxy injects into requests Claude Code sessions send to approved external services; each credential belongs to an agent proxy profile. Audit events carry only credential names and settings, never the secret material itself.

  - `"ccr_agent_proxy_credential_deleted"`

    A Claude Code agent proxy credential was deleted. Its secret material was removed and can no longer be sent to any host.

  - `"ccr_agent_proxy_credential_rotated"`

    A Claude Code agent proxy credential's secret material was replaced. The replacement keeps the same name, profile, and allowed hosts under a new credential identifier, and everything that referenced the old credential now uses the replacement.

  - `"ccr_agent_proxy_credential_updated"`

    A Claude Code agent proxy credential's settings were updated. Only the display name and the allowed host patterns can be updated; the secret material can only be replaced through a rotation.

  - `"ccr_agent_proxy_destination_deleted"`

    An agent proxy destination was deleted.

  - `"ccr_agent_proxy_network_events_listed"`

    A Claude Code network activity export was accessed for the given hour.

  - `"ccr_agent_proxy_profile_bound"`

    A Claude Code agent proxy profile was bound to a scope, applying its policy to Claude Code sessions in that scope.

  - `"ccr_agent_proxy_profile_created"`

    A Claude Code agent proxy profile was created. Agent proxy profiles are named, reusable bundles of access policy that administrators bind to parts of the organization.

  - `"ccr_agent_proxy_profile_deleted"`

    A Claude Code agent proxy profile was deleted, removing its policy from everything it was bound to.

  - `"ccr_agent_proxy_profile_unbound"`

    A Claude Code agent proxy profile was unbound from a scope, removing its policy from Claude Code sessions in that scope.

  - `"ccr_agent_proxy_profile_updated"`

    A Claude Code agent proxy profile's configuration was updated.

  - `"ccr_agent_proxy_provisioning_credential_rejected"`

    An organization owner rejected a credential that a teammate submitted via an agent proxy provisioning link: the credential and its disabled rule were deleted and the link was revoked. The actor is the owner; the submitter is recorded for attribution.

  - `"ccr_agent_proxy_provisioning_link_enabled"`

    An organization owner enabled a credential that a teammate submitted via an agent proxy provisioning link: the disabled rule created at submission was switched to enforce, so the credential now takes traffic. The actor is the owner; the submitter is the actor on the prior ccr_agent_proxy_provisioning_link_submitted event.

  - `"ccr_agent_proxy_provisioning_link_generated"`

    An organization owner generated a one-time agent proxy credential provisioning link so a teammate can submit a credential into the target agent proxy profile without holding the owner role.

  - `"ccr_agent_proxy_provisioning_link_revoked"`

    An organization owner revoked an unfilled agent proxy provisioning link.

  - `"ccr_agent_proxy_provisioning_link_submitted"`

    A teammate submitted a credential via an agent proxy provisioning link. The credential and a disabled rule are created; the credential takes traffic only after an organization owner enables the submitted credential. This event records the link-mediated lifecycle; the credential itself additionally emits ccr_agent_proxy_credential_created.

  - `"ccr_agent_proxy_rule_deleted"`

    An agent proxy rule was deleted.

  - `"ccr_agent_slack_access_scope_created"`

    A Claude Code agent was granted access to read or write in an additional Slack channel beyond the one it is assigned to.

  - `"ccr_agent_slack_access_scope_deleted"`

    A Claude Code agent's access to an additional Slack channel was revoked.

  - `"ccr_agent_slack_binding_created"`

    A Claude Code agent was assigned to a Slack channel or workspace as its dedicated agent.

  - `"ccr_agent_slack_binding_deleted"`

    A Claude Code agent's assignment to a Slack channel or workspace was removed.

  - `"ccr_agent_updated"`

    A Claude Code agent's configuration was updated. Also emitted with updated_fields ["is_virtual"] alone when an auto-provisioned agent is promoted to a configured one, whether by an update request targeting it or by binding an agent proxy profile to it.

  - `"ccr_role_channel_assignment_deleted"`

    CcrRoleChannelAssignmentDeleted is emitted when an org owner/admin removes an RBAC role's channel assignment row (the role reverts to granting zero channels).

  - `"ccr_role_channel_assignment_updated"`

    CcrRoleChannelAssignmentUpdated is emitted when an org owner/admin sets or replaces the list of Slack channels an RBAC role's holders may configure via the delegated Claude-in-Slack channel-manage surface.

  - `"ccr_session_created"`

    A Claude Code session was created. A session is one coding interaction with Claude.

  - `"ccr_session_deleted"`

    A Claude Code session was deleted.

  - `"ccr_session_updated"`

    A Claude Code session's settings were updated.

  - `"claude_artifact_access_failed"`

    An attempt to access an artifact failed.

  - `"claude_artifact_commented"`

    Comment activity on a published artifact: a comment was added, a thread's resolved state was changed, or a thread was deleted. The actor is the user who performed the action; the comment text itself is stored with the artifact and is not part of this record.

  - `"claude_artifact_comments_viewed"`

    An artifact's comments were viewed.

  - `"claude_artifact_created"`

    An artifact was created.

  - `"claude_artifact_duplicated"`

    A user duplicated an artifact they could view into a new artifact that they own. The actor is the user who created the copy; the source artifact is not modified.

  - `"claude_artifact_published"`

    A new version of an artifact was published — for an artifact created in a chat this is the action that made it publicly viewable; for an artifact created outside a chat it is recorded on every save, including saves of private artifacts, and changes to who can access the artifact are recorded separately as claude_artifact_sharing_updated.

  - `"claude_artifact_sharing_updated"`

    An artifact's sharing settings were updated.

  - `"claude_artifact_viewed"`

    An artifact was viewed.

  - `"claude_chat_access_failed"`

    A user was denied access to a Claude.ai chat conversation.

  - `"claude_chat_created"`

    User created a chat.

  - `"claude_chat_deleted"`

    A user deleted a Claude.ai chat conversation.

  - `"claude_chat_deletion_failed"`

    A request to delete a Claude.ai chat conversation failed.

  - `"claude_chat_settings_updated"`

    User updated the settings for a conversation.

  - `"claude_chat_snapshot_created"`

    User created/shared a chat snapshot.

  - `"claude_chat_snapshot_deleted"`

    User deleted/unshared a chat snapshot.

  - `"claude_chat_snapshot_viewed"`

    User viewed a chat snapshot (authenticated or public/unauthenticated).

  - `"claude_chat_sync_source_created"`

    A sync source was connected for syncing external content into Claude chats.

  - `"claude_chat_sync_source_deleted"`

    A sync source was disconnected from Claude chats.

  - `"claude_chat_sync_source_updated"`

    A Claude chat sync source's configuration was updated.

  - `"claude_chat_updated"`

    User updated the chat metadata (e.g name, model).

  - `"claude_chat_viewed"`

    A user viewed a Claude.ai chat conversation.

  - `"claude_code_credential_revoked"`

    A Claude Code credential (runner pool key, runner token, or session token) was revoked. The credential itself is never recorded.

  - `"claude_code_review_config_updated"`

    Claude Code Review configuration was enabled/disabled for an org.

  - `"claude_code_review_repository_added"`

    A repository was added to org-level Claude Code Review configuration.

  - `"claude_code_review_repository_removed"`

    A repository was removed from org-level Claude Code Review configuration.

  - `"claude_code_review_repository_updated"`

    A Claude Code Review repository configuration was updated.

  - `"claude_code_runner_deleted"`

    A self-hosted runner was forcibly removed from its pool. Sessions assigned to the runner were returned to the pool queue, unless a session had already been requeued repeatedly, in which case it was marked stuck instead of being requeued again.

  - `"claude_code_runner_pool_created"`

    A self-hosted runner pool for Claude Code was created.

  - `"claude_code_runner_pool_deleted"`

    A self-hosted runner pool was deleted.

  - `"claude_code_runner_pool_secret_minted"`

    A registration key for a self-hosted runner pool was minted. Runners present this key to join the pool. The key itself is never recorded.

  - `"claude_code_runner_pool_session_queue_updated"`

    An admin changed a session's position in its self-hosted runner pool's queue: requeued it onto a different runner, dismissed it from the queue, or re-admitted it for another runner provisioning attempt.

  - `"claude_code_runner_pool_updated"`

    A self-hosted runner pool's settings were updated.

  - `"claude_code_security_center_config_updated"`

    Claude Code Security Center scanning was enabled/disabled for an org.

  - `"claude_code_security_scan_cancelled"`

    In-flight Claude Code Security scans were cancelled for a project.

  - `"claude_code_security_scan_created"`

    A Claude Code Security scan was started.

  - `"claude_code_security_scan_project_member_updated"`

    A person's access to a Claude Code Security scan project was granted, changed, or revoked.

  - `"claude_code_security_scan_project_updated"`

    A Claude Code Security scan project was archived, unarchived, created, or migrated to a new product experience.

  - `"claude_code_security_scan_project_visibility_updated"`

    A Claude Code Security scan project was shared with the organization or made private.

  - `"claude_code_security_scan_run_updated"`

    A single Claude Code Security scan run was archived, unarchived, or resumed after a billing pause.

  - `"claude_code_security_scan_schedule_deleted"`

    A recurring scan schedule was deleted for a Claude Code Security project.

  - `"claude_code_security_scan_schedule_updated"`

    A recurring scan schedule was set or replaced for a Claude Code Security project.

  - `"claude_code_security_vulnerability_fix_session_created"`

    A Claude Code remediation session was created for a Claude Code Security vulnerability finding.

  - `"claude_code_security_vulnerability_updated"`

    A Claude Code Security vulnerability finding was dismissed, restored, marked fixed, or reopened.

  - `"claude_code_security_webhook_created"`

    A Claude Code Security outbound webhook was created.

  - `"claude_code_security_webhook_deleted"`

    A Claude Code Security outbound webhook was deleted.

  - `"claude_code_security_webhook_secret_updated"`

    The HMAC signing secret for a Claude Code Security webhook was rotated.

  - `"claude_code_security_webhook_updated"`

    A Claude Code Security outbound webhook was updated.

  - `"claude_code_team_memory_acl_updated"`

    An RBAC group was added to or removed from the Claude Code team-memory ACL.

  - `"claude_code_team_memory_updated"`

    Claude Code team memory shared with the organization was updated.

  - `"claude_code_team_onboarding_guide_updated"`

    A Claude Code team onboarding guide was created, updated, or deleted.

  - `"claude_code_user_marketplaces_updated"`

    A user's Claude Code plugin marketplace selections were updated on Anthropic servers.

  - `"claude_code_user_memory_updated"`

    A user's synced private Claude Code memory was updated or deleted on Anthropic servers.

  - `"claude_code_user_plugins_updated"`

    A user's Claude Code plugin selections — which plugins are installed and enabled — were updated on Anthropic servers.

  - `"claude_code_user_settings_updated"`

    A user's synced Claude Code settings were updated or deleted on Anthropic servers.

  - `"claude_command_created"`

    Command was created.

  - `"claude_command_deleted"`

    Command was deleted.

  - `"claude_command_replaced"`

    Command was replaced.

  - `"claude_enterprise_upgrade_credit_updated"`

    An organization admin cancelled, or turned back on, the monthly usage credit the organization receives for upgrading from the Team plan to the Enterprise plan, together with the recurring monthly charge that accompanies it.

  - `"claude_file_access_failed"`

    A user was denied access to a file in Claude.ai.

  - `"claude_file_deleted"`

    A file was deleted.

  - `"claude_file_exported"`

    A file was exported from Claude to an external storage destination.

  - `"claude_file_uploaded"`

    A file was uploaded.

  - `"claude_file_viewed"`

    A user viewed a file in Claude.ai.

  - `"claude_gdrive_integration_created"`

    A Google Drive integration was enabled for the organization.

  - `"claude_gdrive_integration_deleted"`

    A Google Drive integration was disabled for the organization.

  - `"claude_gdrive_integration_updated"`

    A Google Drive integration's configuration was updated.

  - `"claude_github_integration_created"`

    A GitHub integration was enabled for the organization.

  - `"claude_github_integration_deleted"`

    A GitHub integration was disabled for the organization.

  - `"claude_github_integration_updated"`

    A GitHub integration's configuration was updated.

  - `"claude_organization_settings_updated"`

    Organization settings were updated.

  - `"claude_plugin_created"`

    Plugin was created.

  - `"claude_plugin_deleted"`

    Plugin was deleted.

  - `"claude_plugin_disabled"`

    User disabled a plugin for their account.

  - `"claude_plugin_enabled"`

    User enabled a plugin for their account.

  - `"claude_plugin_replaced"`

    Plugin was replaced.

  - `"claude_plugin_updated"`

    Plugin was updated.

  - `"claude_project_archived"`

    A Claude project was archived.

  - `"claude_project_created"`

    A Claude project was created.

  - `"claude_project_deleted"`

    A Claude project was deleted.

  - `"claude_project_document_access_failed"`

    An attempt to access a document in a Claude project failed.

  - `"claude_project_document_bulk_deletion_audit_truncated"`

    A bulk request to delete documents from a Claude project failed with more documents requested than were individually recorded in the audit log.

  - `"claude_project_document_deleted"`

    A document was deleted from a Claude project.

  - `"claude_project_document_deletion_failed"`

    A request to delete a document from a Claude project failed.

  - `"claude_project_document_updated"`

    The content of a document in a Claude project was replaced in place.

  - `"claude_project_document_uploaded"`

    A document was uploaded to a Claude project.

  - `"claude_project_document_viewed"`

    A document in a Claude project was viewed.

  - `"claude_project_file_access_failed"`

    An attempt to access a file in a Claude project failed.

  - `"claude_project_file_bulk_deletion_audit_truncated"`

    A bulk request to delete files from a Claude project failed with more files requested than were individually recorded in the audit log.

  - `"claude_project_file_deleted"`

    A file was deleted from a Claude project.

  - `"claude_project_file_deletion_failed"`

    A request to delete a file from a Claude project failed.

  - `"claude_project_file_uploaded"`

    A file was uploaded to a Claude project.

  - `"claude_project_reported"`

    A Claude project was reported.

  - `"claude_project_sharing_updated"`

    A Claude project's sharing settings were updated.

  - `"claude_project_sync_source_created"`

    A sync source was connected to a Claude project's knowledge base.

  - `"claude_project_sync_source_deleted"`

    A sync source was disconnected from a Claude project's knowledge base.

  - `"claude_project_sync_source_updated"`

    A Claude project sync source's configuration was updated.

  - `"claude_project_viewed"`

    A Claude project was viewed.

  - `"claude_published_artifact_deleted"`

    A published artifact was deleted or unpublished — by its creator, by an organization admin, or by Anthropic (for example, when it was removed for a policy violation).

  - `"claude_pubsec_identity_configured"`

    SAML IdP configuration updated for a public sector organization.

  - `"claude_skill_created"`

    Skill was created.

  - `"claude_skill_deleted"`

    Skill was deleted.

  - `"claude_skill_disabled"`

    User disabled a skill for their account.

  - `"claude_skill_enabled"`

    User enabled a skill for their account.

  - `"claude_skill_replaced"`

    Skill was replaced.

  - `"claude_user_role_updated"`

    A user's role within the organization was changed, or the user was added to or removed from the organization.

  - `"claude_user_seat_tier_updated"`

    An organization member's seat tier was changed. A null `previous_seat_tier` means the member previously had no seat assigned; a null `current_seat_tier` means the seat was removed.

  - `"claude_user_settings_updated"`

    User updated their personal settings.

  - `"cli_plugin_exec_policy_updated"`

    Admin set or cleared the per-op permission ceiling for a plugin CLI.

  - `"compliance_api_accessed"`

    Logging event auto-generated for each compliance API request.

  - `"cowork_session_updated"`

    A Cowork session was updated.

  - `"design_project_artifact_published"`

    A Claude Design project's content was published as a claude.ai artifact, making a snapshot of one of its files viewable outside the project's sharing settings.

  - `"design_project_created"`

    A Claude Design project was created.

  - `"design_project_deleted"`

    A Claude Design project was deleted.

  - `"design_project_member_added"`

    A member was granted access to a Claude Design project.

  - `"design_project_member_removed"`

    A member's access to a Claude Design project was revoked.

  - `"design_project_member_role_updated"`

    A Claude Design project member's role was changed.

  - `"design_project_published"`

    A Claude Design template or design system was published, making it discoverable by everyone in its organization.

  - `"design_project_sharing_updated"`

    A Claude Design project's link-sharing settings were changed — who the project's link works for, and what people opening it through the link may do. Access granted to individual members is reported separately (see design_project_member_added).

  - `"design_project_unpublished"`

    A Claude Design template or design system was unpublished, removing it from its organization's shared gallery.

  - `"design_project_updated"`

    A Claude Design project's metadata was updated.

  - `"design_project_version_restored"`

    A Claude Design project's working tree was rolled back to a previously saved version, replacing its current files with that version's files.

  - `"design_project_viewed"`

    A Claude Design project's content was read. The surface field records which kind of read — a project open, a full-content read, a single-file read, a saved-version read, or an export request. The actor is the reader.

    This activity type is retired: project content reads are no longer
    recorded. Events of this type may still appear in feeds for reads that
    occurred while it was active.

  - `"desktop_extension_allowlisted"`

    A desktop extension was added to an org's allowlist.

  - `"desktop_extension_blocklisted"`

    A desktop extension was added to the global blocklist.

  - `"desktop_extension_deleted"`

    A desktop extension was deleted, either globally by an admin or org-scoped by an org owner.

  - `"desktop_extension_removed_from_allowlist"`

    A desktop extension was removed from an org's allowlist.

  - `"desktop_extension_unblocked"`

    A desktop extension was removed from the global blocklist.

  - `"desktop_extension_uploaded"`

    A desktop extension was uploaded, either globally by an admin or org-scoped by an org owner.

  - `"desktop_extension_version_uploaded"`

    A new version of an existing org-owned desktop extension was uploaded.

  - `"domain_claim_initiated"`

    Domain capture claim initiated over personal accounts on verified domains.

  - `"end_user_invite_requested"`

    Non-admin member submitted an invite request for a new org member.

  - `"extra_usage_billing_enabled"`

    Usage credit billing was enabled for an organization.

  - `"extra_usage_credit_granted"`

    A promotional usage credit grant was claimed.

  - `"extra_usage_spend_limit_created"`

    Usage credit spend limit was created.

  - `"extra_usage_spend_limit_deleted"`

    Usage credit spend limit was deleted.

  - `"extra_usage_spend_limit_increase_request_approved"`

    A usage credit spend limit increase request was approved.

  - `"extra_usage_spend_limit_increase_request_denied"`

    A usage credit spend limit increase request was denied.

  - `"extra_usage_spend_limit_updated"`

    Usage credit spend limit was updated.

  - `"ghe_configuration_created"`

    Admin created a GHE configuration.

  - `"ghe_configuration_deleted"`

    Admin deleted a GHE configuration.

  - `"ghe_configuration_updated"`

    Admin updated a GHE configuration. Previous/new field pairs are recorded only for settings that changed in the update; secret credentials are never recorded, only whether they were replaced.

  - `"ghe_user_connected"`

    User connected to a GHE instance.

  - `"ghe_user_disconnected"`

    User disconnected from a GHE instance.

  - `"ghe_webhook_signature_invalid"`

    Webhook signature validation failed.

  - `"github_token_import"`

    A user attempted to import a personal GitHub access token for use with Claude Code. The `result` field indicates the outcome of the import (imported, rejected, or failed).

  - `"group_created"`

    A group was created (RBAC admin or SCIM provisioning).

  - `"group_deleted"`

    A group was deleted (RBAC admin or SCIM provisioning).

  - `"group_list_viewed"`

    Admin viewed the list of RBAC groups.

  - `"group_member_added"`

    One or more members were added to a group.

  - `"group_member_addition_failed"`

    A request to add members to a group failed. Some of the requested members may have been added before the failure.

  - `"group_member_list_viewed"`

    Admin viewed the members of an RBAC group.

  - `"group_member_removal_failed"`

    A request to remove members from a group failed. Some of the requested members may have been removed before the failure.

  - `"group_member_removed"`

    One or more members were removed from a group.

  - `"group_project_shares_revoked"`

    An RBAC group's project shares in one organization were revoked in bulk.

  - `"group_skill_shares_revoked"`

    An RBAC group's skill shares in one organization were revoked in bulk.

  - `"group_updated"`

    A group was updated (RBAC admin or SCIM provisioning).

  - `"group_viewed"`

    A group was viewed.

  - `"group_visibility_updated"`

    An RBAC group's visibility policy was updated.

  - `"inference_hooks_circuit_breaker_tripped"`

    The organization's Inference hooks circuit breaker tripped automatically: calls to the organization's Inference hooks endpoint crossed a failure threshold, and inspection was suspended to protect live traffic. While tripped, requests are handled according to the organization's failure handling setting — allowed through uninspected (fail open) or rejected (fail closed) — and no per-request Inference hooks activities are recorded. The tripped state persists until an administrator re-enables Inference hooks inspection (or explicitly resets the circuit breaker).

  - `"inference_hooks_config_deleted"`

    Inference hooks configuration was removed for the
    organization.

  - `"inference_hooks_config_updated"`

    Inference hooks configuration was created or updated for the
    organization.

  - `"inference_hooks_request_denied"`

    Inference hooks inspection denied a request. The request was blocked and no model response was produced.

  - `"inference_hooks_request_failed_open"`

    A request proceeded without Inference hooks inspection because a verdict could not be obtained and the organization's Inference hooks configuration is set to fail open.

  - `"inference_hooks_signing_secret_generated"`

    A request signing secret was generated for the organization's
    Inference hooks configuration.

  - `"integration_user_connected"`

    User connected to an integration.

  - `"integration_user_disconnected"`

    User disconnected from an integration.

  - `"invoice_collection_method_updated"`

    Invoice collection method was changed.

  - `"lti_launch_initiated"`

    LTI launch was initiated.

  - `"lti_launch_success"`

    LTI launch completed successfully.

  - `"lti_platform_created"`

    Anthropic staff created an LTI platform integration on behalf of an org.

  - `"lti_platform_updated"`

    Anthropic staff updated an LTI platform integration on behalf of an org.

  - `"magic_link_login_failed"`

    A magic link sign-in attempt failed.

  - `"magic_link_login_initiated"`

    A user requested a magic link sign-in email.

  - `"magic_link_login_succeeded"`

    A user successfully signed in with a magic link email.

  - `"managed_organization_setup_completed"`

    Managed (AWS Marketplace) organization setup was completed.

  - `"marketplace_created"`

    Admin created an organization marketplace.

  - `"marketplace_deleted"`

    Admin deleted an organization marketplace.

  - `"marketplace_updated"`

    Admin updated an organization marketplace.

  - `"marketplace_webhook_deleted"`

    Admin removed the GitHub push webhook for a marketplace.

  - `"marketplace_webhook_provisioned"`

    Admin provisioned a GitHub push webhook for a marketplace.

  - `"mcp_directory_server_published"`

    The organization published its approved MCP directory listing.

  - `"mcp_server_created"`

    An MCP server was added to the organization.

  - `"mcp_server_deleted"`

    An MCP server was removed from the organization.

  - `"mcp_server_managed_auth_token_exchanged"`

    A user attempted to obtain an access token for an MCP server via enterprise managed authorization. This event reports the outcomes of attempted token exchanges. Repeated failures with the same cause may be reported once until the cause changes, and requests denied by organization policy before a token exchange is attempted are not reported, with the exception of the "connector_scope_not_granted" failures described under error_type.

  - `"mcp_server_managed_auth_updated"`

    An MCP server's enterprise managed authorization settings were set, changed, or cleared, including when they were supplied while the server was being added or edited. Fields without a "previous_" prefix describe the settings after the change and are null when the server has no managed authorization settings afterwards; "previous_" fields describe the settings before the change and are null when the server had none before (always the case for a newly added server).

  - `"mcp_server_updated"`

    An MCP server's configuration was updated.

  - `"mcp_tool_policy_updated"`

    The permission restriction for an MCP tool was set or cleared.

  - `"org_analytics_api_capability_updated"`

    Organization analytics_api capability was enabled or disabled.

  - `"org_bulk_delete_initiated"`

    Organization bulk deletion was initiated.

  - `"org_capability_grant_added"`

    A capability grant was added to a workspace or role.

  - `"org_capability_grant_removed"`

    A capability grant was removed from a workspace or role.

  - `"org_claude_code_data_sharing_disabled"`

    Organization Claude Code data sharing was disabled.

  - `"org_claude_code_data_sharing_enabled"`

    Organization Claude Code data sharing was enabled.

  - `"org_claude_code_desktop_disabled"`

    Organization Claude Code Desktop was disabled.

  - `"org_claude_code_desktop_enabled"`

    Organization Claude Code Desktop was enabled.

  - `"org_claude_code_zero_data_retention_disabled"`

    A primary owner disabled zero data retention for Claude Code, so Claude
    Code content is retained according to the organization's data retention
    settings.

  - `"org_compliance_api_settings_updated"`

    Organization compliance API settings were updated.

  - `"org_connector_domain_guard_updated"`

    Enterprise admin changed whether connectors are restricted to verified domains.

  - `"org_cowork_act_without_asking_mode_disabled"`

    The "Act without asking" mode in Cowork was disabled for the organization, so members can no longer let Claude act without asking for approval.

  - `"org_cowork_act_without_asking_mode_enabled"`

    The "Act without asking" mode in Cowork was enabled for the organization, allowing members to let Claude act without asking for approval.

  - `"org_cowork_agent_disabled"`

    Organization Cowork Agent was disabled.

  - `"org_cowork_agent_enabled"`

    Organization Cowork Agent was enabled.

  - `"org_cowork_auto_mode_disabled"`

    The "Auto" permission mode in Cowork was disabled for the organization, so members can no longer let Claude approve its own actions after a safety check.

  - `"org_cowork_auto_mode_enabled"`

    The "Auto" permission mode in Cowork was enabled for the organization, allowing members to let Claude approve its own actions after a safety check.

  - `"org_cowork_disabled"`

    Organization cowork was disabled.

  - `"org_cowork_enabled"`

    Organization cowork was enabled.

  - `"org_cowork_mcp_always_allow_disabled"`

    The "Always allow" option for connector tools in Cowork was disabled for the organization, so each use of a connector tool that can make changes requires approval. Read-only connector tools are not affected by this setting.

  - `"org_cowork_mcp_always_allow_enabled"`

    The "Always allow" option for connector tools in Cowork was enabled for the organization, letting members approve a connector tool that can make changes once and allow its later uses automatically. Read-only connector tools are not affected by this setting.

  - `"org_cowork_otlp_settings_updated"`

    The organization's Cowork OpenTelemetry monitoring export settings were updated.

  - `"org_cowork_remote_disabled"`

    Running Cowork in the cloud was disabled for the organization, so members can no longer run Cowork sessions in Anthropic-hosted remote environments.

  - `"org_cowork_remote_enabled"`

    Running Cowork in the cloud was enabled for the organization, allowing members to run Cowork sessions in Anthropic-hosted remote environments.

  - `"org_creation_blocked"`

    Organization creation was blocked.

  - `"org_data_export_accessed"`

    Organization data export file was accessed/downloaded via signed URL.

  - `"org_data_export_completed"`

    Organization data export was completed.

  - `"org_data_export_started"`

    Organization data export was started.

  - `"org_data_residency_updated"`

    The organization's inference data residency settings were updated.

  - `"org_deleted_via_bulk"`

    Organization was deleted via bulk operation.

  - `"org_deletion_requested"`

    Organization deletion was requested.

  - `"org_directory_resync_completed"`

    Organization directory resync completed successfully.

  - `"org_directory_resync_failed"`

    Organization directory resync failed.

  - `"org_directory_resync_started"`

    Organization directory resync was started asynchronously.

  - `"org_directory_sync_activated"`

    Organization directory sync was activated.

  - `"org_directory_sync_add_initiated"`

    Organization directory sync setup was initiated.

  - `"org_directory_sync_deleted"`

    Organization directory sync was deleted.

  - `"org_discoverability_disabled"`

    Admin disabled organization discoverability.

  - `"org_discoverability_enabled"`

    Admin enabled organization discoverability.

  - `"org_discoverability_settings_updated"`

    Admin updated organization discoverability settings.

  - `"org_domain_add_initiated"`

    Organization domain verification was initiated.

  - `"org_domain_removed"`

    Organization domain was removed.

  - `"org_domain_verified"`

    Organization domain was verified.

  - `"org_external_key_created"`

    A CMEK external key config was created.

  - `"org_external_key_deleted"`

    A CMEK external key config was deleted.

  - `"org_external_key_updated"`

    A CMEK external key config was updated.

  - `"org_external_key_validated"`

    A CMEK external key config was validated against the customer's KMS.

  - `"org_hipaa_self_serve_enabled"`

    A primary owner click-accepted the BAA and enabled HIPAA protections
    for the organization via the self-serve flow.

  - `"org_invite_link_disabled"`

    Organization invite link was disabled.

  - `"org_invite_link_generated"`

    Organization invite link was generated.

  - `"org_invite_link_regenerated"`

    Organization invite link was regenerated (previous link invalidated).

  - `"org_invite_viewed"`

    An organization invite was viewed.

  - `"org_invites_listed"`

    Organization invites were listed.

  - `"org_ip_restriction_created"`

    Organization IP restriction was created.

  - `"org_ip_restriction_deleted"`

    Organization IP restriction was deleted.

  - `"org_ip_restriction_updated"`

    Organization IP restriction was updated.

  - `"org_join_proposal_decided"`

    Approve or reject decision on a parent-org join proposal.

  - `"org_join_request_approved"`

    Admin approved a join request.

  - `"org_join_request_created"`

    User requested to join an organization.

  - `"org_join_request_dismissed"`

    Admin dismissed a join request.

  - `"org_join_request_instant_approved"`

    Join request was instantly approved.

  - `"org_join_requests_bulk_dismissed"`

    Admin bulk-dismissed join requests.

  - `"org_magic_link_second_factor_toggled"`

    Organization magic link second factor was toggled.

  - `"org_member_invites_disabled"`

    Admin disabled member invites for the organization.

  - `"org_member_invites_enabled"`

    Admin enabled member invites for the organization.

  - `"org_members_exported"`

    Organization members list was exported as CSV.

  - `"org_model_default_updated"`

    An organization or role default model setting was changed by an administrator.

  - `"org_parent_join_proposal_created"`

    Organization parent join proposal was created.

  - `"org_parent_search_performed"`

    Organization parent search was performed.

  - `"org_sso_add_initiated"`

    Organization SSO setup was initiated.

  - `"org_sso_connection_activated"`

    Organization SSO connection was activated.

  - `"org_sso_connection_deactivated"`

    Organization SSO connection was deactivated.

  - `"org_sso_connection_deleted"`

    Organization SSO connection was deleted.

  - `"org_sso_group_role_mappings_updated"`

    Organization SSO group role mappings were updated.

  - `"org_sso_provisioning_mode_changed"`

    Organization SSO provisioning mode was changed.

  - `"org_sso_scim_welcome_email_toggled"`

    Organization SCIM-provisioned welcome email was toggled.

  - `"org_sso_seat_tier_assignment_toggled"`

    Organization SSO seat tier assignment was toggled.

  - `"org_sso_seat_tier_mappings_updated"`

    Organization SSO seat tier mappings were updated.

  - `"org_sso_toggled"`

    Organization SSO was toggled on or off.

  - `"org_sync_deleting_synchronized_files_started"`

    Organization started deleting synchronized files.

  - `"org_sync_synchronized_files_deleted"`

    Organization synchronized files were deleted.

  - `"org_taint_added"`

    A taint was added to an organization.

  - `"org_taint_removed"`

    A taint was removed from an organization.

  - `"org_user_deleted"`

    User was removed from organization.

  - `"org_user_invite_accepted"`

    Organization user invite was accepted.

  - `"org_user_invite_deleted"`

    Organization user invite was deleted.

  - `"org_user_invite_re_sent"`

    Organization user invite was re-sent.

  - `"org_user_invite_rejected"`

    Organization user invite was rejected.

  - `"org_user_invite_sent"`

    Organization user invite was sent.

  - `"org_user_left"`

    User removed themselves from organization.

  - `"org_user_trusted_devices_revoked"`

    An organization admin revoked a member's trusted devices and signed the member out of all active sessions.

  - `"org_user_viewed"`

    An organization user was viewed.

  - `"org_users_listed"`

    Organization users were listed.

  - `"org_work_across_apps_disabled"`

    The organization's "Let Claude work across apps" setting was turned off.

  - `"org_work_across_apps_enabled"`

    The organization's "Let Claude work across apps" setting was turned on.

  - `"organization_address_updated"`

    The organization's billing or shipping address was updated.

  - `"organization_icon_deleted"`

    Organization's custom icon deleted.

  - `"organization_icon_updated"`

    Organization's custom icon uploaded or replaced.

  - `"owned_projects_access_restored"`

    Access to owned projects was restored.

  - `"payment_method_updated"`

    The organization's default payment method was updated.

  - `"pending_share_created"`

    A pending share of a project or skill was created for an email address that is not yet an organization member.

  - `"pending_share_revoked"`

    A pending share of a project or skill was revoked before the invitee joined the organization.

  - `"phone_code_sent"`

    User requested a phone verification code.

  - `"phone_code_verified"`

    User successfully verified their phone code.

  - `"platform_agent_archived"`

    An agent was archived on the API platform.

  - `"platform_agent_created"`

    An agent was created on the API platform.

  - `"platform_agent_deleted"`

    An agent was deleted from the API platform.

  - `"platform_agent_deployment_archived"`

    An agent deployment was archived on the API platform.

  - `"platform_agent_deployment_created"`

    An agent deployment was created on the API platform.

  - `"platform_agent_deployment_deleted"`

    An agent deployment was deleted from the API platform.

  - `"platform_agent_deployment_paused"`

    An agent deployment was paused on the API platform.

  - `"platform_agent_deployment_run_triggered"`

    An agent deployment was run on demand on the API platform.

  - `"platform_agent_deployment_unpaused"`

    An agent deployment was resumed on the API platform.

  - `"platform_agent_deployment_updated"`

    An agent deployment was updated on the API platform.

  - `"platform_agent_session_archived"`

    An agent session was archived on the API platform.

  - `"platform_agent_session_created"`

    An agent session was created on the API platform.

  - `"platform_agent_session_deleted"`

    An agent session was deleted from the API platform.

  - `"platform_agent_session_resource_added"`

    A resource was attached to an agent session.

  - `"platform_agent_session_resource_deleted"`

    A resource attached to an agent session was removed.

  - `"platform_agent_session_resource_updated"`

    A resource attached to an agent session was updated.

  - `"platform_agent_session_thread_archived"`

    A thread within an agent session was archived.

  - `"platform_agent_session_updated"`

    An agent session was updated on the API platform.

  - `"platform_agent_updated"`

    An agent was updated on the API platform.

  - `"platform_api_key_created"`

    An API key was created.

  - `"platform_api_key_updated"`

    An API key was updated.

  - `"platform_app_attest_authentication"`

    An attested mobile device attempted to exchange an Apple App Attest assertion for Anthropic API credentials.

  - `"platform_billing_upgraded_to_prepaid"`

    The organization's API billing was upgraded to the prepaid plan.

  - `"platform_clearance_workspace_program_request_cleared"`

    A workspace's clearance program assignment was removed.

  - `"platform_clearance_workspace_program_request_set"`

    A workspace's clearance program assignment was created or updated.

  - `"platform_cost_report_viewed"`

    The cost report was viewed.

  - `"platform_dream_archived"`

    A Dream (asynchronous memory-consolidation job) was archived.

  - `"platform_dream_cancelled"`

    A Dream (asynchronous memory-consolidation job) was cancelled before it completed.

  - `"platform_dream_created"`

    A Dream (asynchronous memory-consolidation job) was created.

  - `"platform_federated_authentication"`

    A federated workload identity attempted to exchange an OIDC token for Anthropic API credentials.

  - `"platform_federation_issuer_archived"`

    An OIDC federation issuer was archived.

  - `"platform_federation_issuer_updated"`

    An OIDC federation issuer was updated.

  - `"platform_federation_rule_archived"`

    An OIDC federation rule was archived.

  - `"platform_federation_rule_updated"`

    An OIDC federation rule was updated.

  - `"platform_federation_rule_workspace_added"`

    A federation rule was enabled for a workspace.

  - `"platform_federation_rule_workspace_removed"`

    A federation rule was disabled for a workspace.

  - `"platform_file_content_downloaded"`

    Activity logged when file content is downloaded via GET /v1/files/{file_id}/content.

  - `"platform_file_deleted"`

    Activity logged when a file is deleted via DELETE /v1/files/{file_id}.

  - `"platform_file_uploaded"`

    Activity logged when a file is uploaded via POST /v1/files.

  - `"platform_memory_created"`

    An agent memory document was created.

  - `"platform_memory_deleted"`

    An agent memory document was deleted.

  - `"platform_memory_store_archived"`

    An agent memory store was archived. Archived stores reject new memory writes and cannot be attached to new sessions; deletion and redaction remain permitted for privacy scrubbing.

  - `"platform_memory_store_created"`

    An agent memory store was created.

  - `"platform_memory_store_deleted"`

    An agent memory store was deleted. Memory content removal may complete asynchronously for very large stores.

  - `"platform_memory_store_updated"`

    An agent memory store's name, description, or metadata was updated.

  - `"platform_memory_updated"`

    An agent memory document's content or path was updated.

  - `"platform_memory_version_redacted"`

    A historical version of an agent memory document was redacted. Redaction scrubs the stored content of a specific version while preserving the version's existence in the history.

  - `"platform_oauth_app_created"`

    An OAuth app was created.

  - `"platform_oauth_app_revoked"`

    An OAuth app was revoked.

  - `"platform_oauth_app_updated"`

    An OAuth app was updated.

  - `"platform_plugin_directory_submission_created"`

    A plugin directory submission was created on the API platform. A plugin directory submission is a request to list a plugin in the public plugin directory.

  - `"platform_plugin_directory_submission_deleted"`

    A plugin directory submission was deleted on the API platform.

  - `"platform_plugin_directory_submission_updated"`

    A plugin directory submission was updated on the API platform.

  - `"platform_service_account_archived"`

    A service account was archived.

  - `"platform_service_account_updated"`

    A service account was updated.

  - `"platform_service_account_workspace_member_added"`

    A service account was added as a member of a workspace.

  - `"platform_service_account_workspace_member_removed"`

    A service account was removed from a workspace.

  - `"platform_service_account_workspace_member_updated"`

    A service account's workspace membership role was updated.

  - `"platform_signing_key_created"`

    Activity logged when a new request-signing key is registered for the org.

  - `"platform_signing_key_deleted"`

    Activity logged when a signing key is permanently deleted.

  - `"platform_signing_key_rotated"`

    Activity logged when an in-memory signing key is rotated.

  - `"platform_skill_version_created"`

    Activity logged when a skill version is created via POST /v1/skills/{skill_id}/versions.

  - `"platform_skill_version_deleted"`

    Activity logged when a skill version is deleted via DELETE /v1/skills/{skill_id}/versions/{version}.

  - `"platform_spend_limit_alert_emails_updated"`

    Spend limit alert email addresses and role targets were updated for an org.

  - `"platform_spend_limit_created"`

    An org-level fixed-dollar spend limit was created.

  - `"platform_spend_limit_deleted"`

    An org-level spend limit was removed.

  - `"platform_spend_limit_updated"`

    An org-level spend limit snooze/ignore state was changed.

  - `"platform_usage_report_claude_code_viewed"`

    The Claude Code usage report was viewed.

  - `"platform_usage_report_messages_viewed"`

    The messages usage report was viewed.

  - `"platform_workspace_archived"`

    A workspace was archived.

  - `"platform_workspace_created"`

    A workspace was created.

  - `"platform_workspace_inference_data_retention_disabled"`

    The zero data retention override was disabled for a workspace.

  - `"platform_workspace_inference_data_retention_enabled"`

    The zero data retention override was enabled for a workspace.

  - `"platform_workspace_member_added"`

    A member was added to a workspace.

  - `"platform_workspace_member_removed"`

    A member was removed from a workspace.

  - `"platform_workspace_member_updated"`

    A workspace member was updated.

  - `"platform_workspace_member_viewed"`

    A workspace member was viewed.

  - `"platform_workspace_members_listed"`

    Workspace members were listed.

  - `"platform_workspace_rate_limit_deleted"`

    A workspace rate limit was deleted.

  - `"platform_workspace_rate_limit_updated"`

    A workspace rate limit was created or updated.

  - `"platform_workspace_updated"`

    A workspace was updated.

  - `"plugin_installation_preference_updated"`

    An org admin changed the installation preference for a plugin.

  - `"prepaid_auto_recharge_disabled"`

    Auto-recharge was disabled for API prepaid org.

  - `"prepaid_auto_recharge_updated"`

    Auto-recharge settings were updated for API prepaid org.

  - `"prepaid_extra_usage_auto_reload_disabled"`

    Prepaid usage credit auto-reload was disabled.

  - `"prepaid_extra_usage_auto_reload_enabled"`

    Prepaid usage credit auto-reload was enabled.

  - `"prepaid_extra_usage_auto_reload_settings_updated"`

    Prepaid usage credit auto-reload settings were updated.

  - `"primary_owner_transferred"`

    Primary owner role was transferred to another org member.

  - `"rbac_role_assigned"`

    Admin assigned an RBAC custom role to a principal.

  - `"rbac_role_created"`

    Admin created an RBAC custom role.

  - `"rbac_role_deleted"`

    Admin deleted an RBAC custom role.

  - `"rbac_role_permission_added"`

    Admin added a permission to an RBAC custom role.

    Emitted once per requested permission, including permissions the role
    already had, so a retried request still produces a complete audit record.

  - `"rbac_role_permission_removed"`

    Admin removed a permission from an RBAC custom role.

    Emitted once per requested permission, including permissions the role
    already lacked, so a retried request still produces a complete audit
    record.

  - `"rbac_role_unassigned"`

    Admin unassigned an RBAC custom role from a principal.

  - `"rbac_role_updated"`

    Admin updated an RBAC custom role.

  - `"role_assignment_granted"`

    Role assignment was granted.

  - `"role_assignment_revoked"`

    Role assignment was revoked.

  - `"scim_user_created"`

    A SCIM user was provisioned.

  - `"scim_user_deleted"`

    A SCIM user was deleted.

  - `"scim_user_updated"`

    A SCIM user was updated.

  - `"scoped_api_key_deleted"`

    A scoped API key was deleted.

  - `"scoped_api_key_updated"`

    A scoped API key was renamed or its activation state changed.

  - `"seat_tier_changes_cancelled"`

    Scheduled seat tier downgrades were cancelled.

  - `"seat_tiers_purchased"`

    Seat tiers were purchased or upgraded on a subscription.

  - `"service_created"`

    Activity logged when an org service is explicitly created.

  - `"service_deleted"`

    Activity logged when an org service is deleted.

  - `"service_key_created"`

    Activity logged when a new org service key is created.

  - `"service_key_revoked"`

    Activity logged when an org service key is revoked.

  - `"session_revoked"`

    User revoked a specific session.

  - `"session_share_accessed"`

    Session share was accessed.

  - `"session_share_created"`

    Session share was created.

  - `"session_share_revoked"`

    Session share was revoked.

  - `"slack_workspace_claim_revoked"`

    A Slack workspace or Enterprise Grid organization was disconnected
    from the organization for Claude in Slack.

  - `"slack_workspace_claimed"`

    A Slack workspace or Enterprise Grid organization was connected to
    the organization for Claude in Slack.

  - `"social_login_succeeded"`

    A user successfully signed in with a social identity provider (Google, Apple, or Microsoft).

  - `"sso_login_failed"`

    An SSO sign-in attempt failed.

  - `"sso_login_initiated"`

    A user started an SSO sign-in flow.

  - `"sso_login_succeeded"`

    A user successfully signed in with SSO.

  - `"sso_second_factor_magic_link"`

    SSO second factor magic link was used.

  - `"step_up_authentication_failed"`

    An additional identity check failed.

  - `"step_up_authentication_succeeded"`

    The user completed an additional identity check to confirm a sensitive action.

  - `"step_up_credential_enrolled"`

    A user enrolled a passkey for confirming sensitive actions on their account.

  - `"subscription_cancellation_scheduled"`

    Subscription cancellation was scheduled at end of billing period.

  - `"subscription_quantity_updated"`

    Contracted subscription seat quantity was updated.

  - `"subscription_renewed"`

    A cancelled subscription was renewed.

  - `"subscription_resumed"`

    A scheduled subscription cancellation was reversed.

  - `"subscription_started"`

    A new subscription was created (Team or Enterprise).

  - `"subscription_upgraded"`

    Subscription plan was upgraded (e.g. Team to Enterprise).

  - `"trusted_device_credential_rotated"`

    The identity-verification credential of a trusted device was rotated to a new key.

  - `"trusted_device_enrolled"`

    A device was enrolled as a trusted device for the user's account. Trusted devices can be used to confirm the user's identity for sensitive actions.

  - `"trusted_device_revoked"`

    A trusted device was removed from the user's account.

  - `"tunnel_archived"`

    An MCP tunnel was archived.

  - `"tunnel_certificate_added"`

    An inner-TLS CA certificate was added to a tunnel.

  - `"tunnel_certificate_revoked"`

    An inner-TLS CA certificate was revoked from a tunnel.

  - `"tunnel_created"`

    An MCP tunnel was created.

  - `"tunnel_token_minted"`

    An OAuth bearer token for the tunnel management API was minted.

  - `"tunnel_token_revealed"`

    The Cloudflare connector secret for a tunnel was revealed to the caller.

  - `"tunnel_token_revoked"`

    An OAuth bearer token for the tunnel management API was revoked.

  - `"tunnel_token_rotated"`

    The Cloudflare connector secret for a tunnel was rotated.

    `tunnel_token_id` is the id of the *newly-issued* token. The previous
    token is invalidated by the rotation and its id is not recorded here.

  - `"user_consent_recorded"`

    User granted a consent for a specific entity (e.g. consumer health consent for an MCP server).

  - `"user_consent_revoked"`

    User revoked a previously granted consent for a specific entity.

  - `"user_logged_out"`

    A user signed out of one or all sessions.

  - `"verification_evidence_submitted"`

    Verification evidence was submitted for an organization's verification.

  - `"verification_program_application_created"`

    An organization applied to a verification program.

  - `"workspace_member_spend_limit_created"`

    A per-member or workspace-default Claude Code spend limit was created.

  - `"workspace_member_spend_limit_deleted"`

    A per-member or workspace-default Claude Code spend limit was deleted.

  - `"workspace_member_spend_limit_updated"`

    A per-member Claude Code spend limit amount was updated.

  - `"workspace_spend_limit_alert_emails_updated"`

    Spend limit alert email recipients were updated for a workspace.

  - `"workspace_spend_limit_created"`

    A workspace-level API spend limit was created.

  - `"workspace_spend_limit_deleted"`

    A workspace-level API spend limit was deleted.

- `actor_ids: optional array of string`

  Filter activities by actor IDs (currently only `user_...` IDs are supported). Enumerate IDs via `GET /v1/compliance/organizations/{org_uuid}/users`.

- `after_id: optional string`

  Pagination cursor for retrieving the next page of results. To paginate, pass the `last_id` value from the most recent response. Clients should treat this value as an opaque string and not attempt to parse or interpret its contents, as the format may change without notice.

- `before_id: optional string`

  Pagination cursor for retrieving the previous page of results. To paginate, pass the `first_id` value from the most recent response. Clients should treat this value as an opaque string and not attempt to parse or interpret its contents, as the format may change without notice.

- `created_at: optional object { gt, gte, lt, lte }`

  - `gt: optional string`

    Filter activities created after this time (RFC 3339 format)

  - `gte: optional string`

    Filter activities created at or after this time (RFC 3339 format)

  - `lt: optional string`

    Filter activities created before this time (RFC 3339 format)

  - `lte: optional string`

    Filter activities created at or before this time (RFC 3339 format)

- `exclude_activity_types: optional array of "abuse_decision_received" or "account_deleted" or "admin_api_key_created" or 480 more`

  Exclude activities of these types. Cannot be combined with `activity_types[]`.

  - `"abuse_decision_received"`

    An external anti-abuse service reported a consequential decision about a sign-in or sign-up attempt.

  - `"account_deleted"`

    User-initiated self-service account deletion.

  - `"admin_api_key_created"`

    An admin API key was created.

  - `"admin_api_key_deleted"`

    An admin API key was deleted.

  - `"admin_api_key_updated"`

    An admin API key was updated (renamed or activated/deactivated).

  - `"admin_connector_request_resolved"`

    Admin approved or dismissed pending member requests to enable an MCP connector.

  - `"admin_request_created"`

    Admin request created by an org member (seat upgrade, limit increase, join org, end-user invite).

  - `"age_verified"`

    User age was verified.

  - `"anonymous_mobile_login_attempted"`

    Anonymous mobile login was attempted.

  - `"api_key_created"`

    Activity logged when a new API key is created.

  - `"audit_log_export_accessed"`

    Audit log export file was accessed/downloaded via signed URL.

  - `"audit_log_export_started"`

    Audit log export was initiated.

  - `"billing_emails_updated"`

    The organization's billing email recipients were updated.

  - `"ccr_agent_created"`

    A Claude Code agent was created.

  - `"ccr_agent_deleted"`

    A Claude Code agent was deleted.

  - `"ccr_agent_proxy_credential_created"`

    A Claude Code agent proxy credential was created. Credentials hold the secrets the agent proxy injects into requests Claude Code sessions send to approved external services; each credential belongs to an agent proxy profile. Audit events carry only credential names and settings, never the secret material itself.

  - `"ccr_agent_proxy_credential_deleted"`

    A Claude Code agent proxy credential was deleted. Its secret material was removed and can no longer be sent to any host.

  - `"ccr_agent_proxy_credential_rotated"`

    A Claude Code agent proxy credential's secret material was replaced. The replacement keeps the same name, profile, and allowed hosts under a new credential identifier, and everything that referenced the old credential now uses the replacement.

  - `"ccr_agent_proxy_credential_updated"`

    A Claude Code agent proxy credential's settings were updated. Only the display name and the allowed host patterns can be updated; the secret material can only be replaced through a rotation.

  - `"ccr_agent_proxy_destination_deleted"`

    An agent proxy destination was deleted.

  - `"ccr_agent_proxy_network_events_listed"`

    A Claude Code network activity export was accessed for the given hour.

  - `"ccr_agent_proxy_profile_bound"`

    A Claude Code agent proxy profile was bound to a scope, applying its policy to Claude Code sessions in that scope.

  - `"ccr_agent_proxy_profile_created"`

    A Claude Code agent proxy profile was created. Agent proxy profiles are named, reusable bundles of access policy that administrators bind to parts of the organization.

  - `"ccr_agent_proxy_profile_deleted"`

    A Claude Code agent proxy profile was deleted, removing its policy from everything it was bound to.

  - `"ccr_agent_proxy_profile_unbound"`

    A Claude Code agent proxy profile was unbound from a scope, removing its policy from Claude Code sessions in that scope.

  - `"ccr_agent_proxy_profile_updated"`

    A Claude Code agent proxy profile's configuration was updated.

  - `"ccr_agent_proxy_provisioning_credential_rejected"`

    An organization owner rejected a credential that a teammate submitted via an agent proxy provisioning link: the credential and its disabled rule were deleted and the link was revoked. The actor is the owner; the submitter is recorded for attribution.

  - `"ccr_agent_proxy_provisioning_link_enabled"`

    An organization owner enabled a credential that a teammate submitted via an agent proxy provisioning link: the disabled rule created at submission was switched to enforce, so the credential now takes traffic. The actor is the owner; the submitter is the actor on the prior ccr_agent_proxy_provisioning_link_submitted event.

  - `"ccr_agent_proxy_provisioning_link_generated"`

    An organization owner generated a one-time agent proxy credential provisioning link so a teammate can submit a credential into the target agent proxy profile without holding the owner role.

  - `"ccr_agent_proxy_provisioning_link_revoked"`

    An organization owner revoked an unfilled agent proxy provisioning link.

  - `"ccr_agent_proxy_provisioning_link_submitted"`

    A teammate submitted a credential via an agent proxy provisioning link. The credential and a disabled rule are created; the credential takes traffic only after an organization owner enables the submitted credential. This event records the link-mediated lifecycle; the credential itself additionally emits ccr_agent_proxy_credential_created.

  - `"ccr_agent_proxy_rule_deleted"`

    An agent proxy rule was deleted.

  - `"ccr_agent_slack_access_scope_created"`

    A Claude Code agent was granted access to read or write in an additional Slack channel beyond the one it is assigned to.

  - `"ccr_agent_slack_access_scope_deleted"`

    A Claude Code agent's access to an additional Slack channel was revoked.

  - `"ccr_agent_slack_binding_created"`

    A Claude Code agent was assigned to a Slack channel or workspace as its dedicated agent.

  - `"ccr_agent_slack_binding_deleted"`

    A Claude Code agent's assignment to a Slack channel or workspace was removed.

  - `"ccr_agent_updated"`

    A Claude Code agent's configuration was updated. Also emitted with updated_fields ["is_virtual"] alone when an auto-provisioned agent is promoted to a configured one, whether by an update request targeting it or by binding an agent proxy profile to it.

  - `"ccr_role_channel_assignment_deleted"`

    CcrRoleChannelAssignmentDeleted is emitted when an org owner/admin removes an RBAC role's channel assignment row (the role reverts to granting zero channels).

  - `"ccr_role_channel_assignment_updated"`

    CcrRoleChannelAssignmentUpdated is emitted when an org owner/admin sets or replaces the list of Slack channels an RBAC role's holders may configure via the delegated Claude-in-Slack channel-manage surface.

  - `"ccr_session_created"`

    A Claude Code session was created. A session is one coding interaction with Claude.

  - `"ccr_session_deleted"`

    A Claude Code session was deleted.

  - `"ccr_session_updated"`

    A Claude Code session's settings were updated.

  - `"claude_artifact_access_failed"`

    An attempt to access an artifact failed.

  - `"claude_artifact_commented"`

    Comment activity on a published artifact: a comment was added, a thread's resolved state was changed, or a thread was deleted. The actor is the user who performed the action; the comment text itself is stored with the artifact and is not part of this record.

  - `"claude_artifact_comments_viewed"`

    An artifact's comments were viewed.

  - `"claude_artifact_created"`

    An artifact was created.

  - `"claude_artifact_duplicated"`

    A user duplicated an artifact they could view into a new artifact that they own. The actor is the user who created the copy; the source artifact is not modified.

  - `"claude_artifact_published"`

    A new version of an artifact was published — for an artifact created in a chat this is the action that made it publicly viewable; for an artifact created outside a chat it is recorded on every save, including saves of private artifacts, and changes to who can access the artifact are recorded separately as claude_artifact_sharing_updated.

  - `"claude_artifact_sharing_updated"`

    An artifact's sharing settings were updated.

  - `"claude_artifact_viewed"`

    An artifact was viewed.

  - `"claude_chat_access_failed"`

    A user was denied access to a Claude.ai chat conversation.

  - `"claude_chat_created"`

    User created a chat.

  - `"claude_chat_deleted"`

    A user deleted a Claude.ai chat conversation.

  - `"claude_chat_deletion_failed"`

    A request to delete a Claude.ai chat conversation failed.

  - `"claude_chat_settings_updated"`

    User updated the settings for a conversation.

  - `"claude_chat_snapshot_created"`

    User created/shared a chat snapshot.

  - `"claude_chat_snapshot_deleted"`

    User deleted/unshared a chat snapshot.

  - `"claude_chat_snapshot_viewed"`

    User viewed a chat snapshot (authenticated or public/unauthenticated).

  - `"claude_chat_sync_source_created"`

    A sync source was connected for syncing external content into Claude chats.

  - `"claude_chat_sync_source_deleted"`

    A sync source was disconnected from Claude chats.

  - `"claude_chat_sync_source_updated"`

    A Claude chat sync source's configuration was updated.

  - `"claude_chat_updated"`

    User updated the chat metadata (e.g name, model).

  - `"claude_chat_viewed"`

    A user viewed a Claude.ai chat conversation.

  - `"claude_code_credential_revoked"`

    A Claude Code credential (runner pool key, runner token, or session token) was revoked. The credential itself is never recorded.

  - `"claude_code_review_config_updated"`

    Claude Code Review configuration was enabled/disabled for an org.

  - `"claude_code_review_repository_added"`

    A repository was added to org-level Claude Code Review configuration.

  - `"claude_code_review_repository_removed"`

    A repository was removed from org-level Claude Code Review configuration.

  - `"claude_code_review_repository_updated"`

    A Claude Code Review repository configuration was updated.

  - `"claude_code_runner_deleted"`

    A self-hosted runner was forcibly removed from its pool. Sessions assigned to the runner were returned to the pool queue, unless a session had already been requeued repeatedly, in which case it was marked stuck instead of being requeued again.

  - `"claude_code_runner_pool_created"`

    A self-hosted runner pool for Claude Code was created.

  - `"claude_code_runner_pool_deleted"`

    A self-hosted runner pool was deleted.

  - `"claude_code_runner_pool_secret_minted"`

    A registration key for a self-hosted runner pool was minted. Runners present this key to join the pool. The key itself is never recorded.

  - `"claude_code_runner_pool_session_queue_updated"`

    An admin changed a session's position in its self-hosted runner pool's queue: requeued it onto a different runner, dismissed it from the queue, or re-admitted it for another runner provisioning attempt.

  - `"claude_code_runner_pool_updated"`

    A self-hosted runner pool's settings were updated.

  - `"claude_code_security_center_config_updated"`

    Claude Code Security Center scanning was enabled/disabled for an org.

  - `"claude_code_security_scan_cancelled"`

    In-flight Claude Code Security scans were cancelled for a project.

  - `"claude_code_security_scan_created"`

    A Claude Code Security scan was started.

  - `"claude_code_security_scan_project_member_updated"`

    A person's access to a Claude Code Security scan project was granted, changed, or revoked.

  - `"claude_code_security_scan_project_updated"`

    A Claude Code Security scan project was archived, unarchived, created, or migrated to a new product experience.

  - `"claude_code_security_scan_project_visibility_updated"`

    A Claude Code Security scan project was shared with the organization or made private.

  - `"claude_code_security_scan_run_updated"`

    A single Claude Code Security scan run was archived, unarchived, or resumed after a billing pause.

  - `"claude_code_security_scan_schedule_deleted"`

    A recurring scan schedule was deleted for a Claude Code Security project.

  - `"claude_code_security_scan_schedule_updated"`

    A recurring scan schedule was set or replaced for a Claude Code Security project.

  - `"claude_code_security_vulnerability_fix_session_created"`

    A Claude Code remediation session was created for a Claude Code Security vulnerability finding.

  - `"claude_code_security_vulnerability_updated"`

    A Claude Code Security vulnerability finding was dismissed, restored, marked fixed, or reopened.

  - `"claude_code_security_webhook_created"`

    A Claude Code Security outbound webhook was created.

  - `"claude_code_security_webhook_deleted"`

    A Claude Code Security outbound webhook was deleted.

  - `"claude_code_security_webhook_secret_updated"`

    The HMAC signing secret for a Claude Code Security webhook was rotated.

  - `"claude_code_security_webhook_updated"`

    A Claude Code Security outbound webhook was updated.

  - `"claude_code_team_memory_acl_updated"`

    An RBAC group was added to or removed from the Claude Code team-memory ACL.

  - `"claude_code_team_memory_updated"`

    Claude Code team memory shared with the organization was updated.

  - `"claude_code_team_onboarding_guide_updated"`

    A Claude Code team onboarding guide was created, updated, or deleted.

  - `"claude_code_user_marketplaces_updated"`

    A user's Claude Code plugin marketplace selections were updated on Anthropic servers.

  - `"claude_code_user_memory_updated"`

    A user's synced private Claude Code memory was updated or deleted on Anthropic servers.

  - `"claude_code_user_plugins_updated"`

    A user's Claude Code plugin selections — which plugins are installed and enabled — were updated on Anthropic servers.

  - `"claude_code_user_settings_updated"`

    A user's synced Claude Code settings were updated or deleted on Anthropic servers.

  - `"claude_command_created"`

    Command was created.

  - `"claude_command_deleted"`

    Command was deleted.

  - `"claude_command_replaced"`

    Command was replaced.

  - `"claude_enterprise_upgrade_credit_updated"`

    An organization admin cancelled, or turned back on, the monthly usage credit the organization receives for upgrading from the Team plan to the Enterprise plan, together with the recurring monthly charge that accompanies it.

  - `"claude_file_access_failed"`

    A user was denied access to a file in Claude.ai.

  - `"claude_file_deleted"`

    A file was deleted.

  - `"claude_file_exported"`

    A file was exported from Claude to an external storage destination.

  - `"claude_file_uploaded"`

    A file was uploaded.

  - `"claude_file_viewed"`

    A user viewed a file in Claude.ai.

  - `"claude_gdrive_integration_created"`

    A Google Drive integration was enabled for the organization.

  - `"claude_gdrive_integration_deleted"`

    A Google Drive integration was disabled for the organization.

  - `"claude_gdrive_integration_updated"`

    A Google Drive integration's configuration was updated.

  - `"claude_github_integration_created"`

    A GitHub integration was enabled for the organization.

  - `"claude_github_integration_deleted"`

    A GitHub integration was disabled for the organization.

  - `"claude_github_integration_updated"`

    A GitHub integration's configuration was updated.

  - `"claude_organization_settings_updated"`

    Organization settings were updated.

  - `"claude_plugin_created"`

    Plugin was created.

  - `"claude_plugin_deleted"`

    Plugin was deleted.

  - `"claude_plugin_disabled"`

    User disabled a plugin for their account.

  - `"claude_plugin_enabled"`

    User enabled a plugin for their account.

  - `"claude_plugin_replaced"`

    Plugin was replaced.

  - `"claude_plugin_updated"`

    Plugin was updated.

  - `"claude_project_archived"`

    A Claude project was archived.

  - `"claude_project_created"`

    A Claude project was created.

  - `"claude_project_deleted"`

    A Claude project was deleted.

  - `"claude_project_document_access_failed"`

    An attempt to access a document in a Claude project failed.

  - `"claude_project_document_bulk_deletion_audit_truncated"`

    A bulk request to delete documents from a Claude project failed with more documents requested than were individually recorded in the audit log.

  - `"claude_project_document_deleted"`

    A document was deleted from a Claude project.

  - `"claude_project_document_deletion_failed"`

    A request to delete a document from a Claude project failed.

  - `"claude_project_document_updated"`

    The content of a document in a Claude project was replaced in place.

  - `"claude_project_document_uploaded"`

    A document was uploaded to a Claude project.

  - `"claude_project_document_viewed"`

    A document in a Claude project was viewed.

  - `"claude_project_file_access_failed"`

    An attempt to access a file in a Claude project failed.

  - `"claude_project_file_bulk_deletion_audit_truncated"`

    A bulk request to delete files from a Claude project failed with more files requested than were individually recorded in the audit log.

  - `"claude_project_file_deleted"`

    A file was deleted from a Claude project.

  - `"claude_project_file_deletion_failed"`

    A request to delete a file from a Claude project failed.

  - `"claude_project_file_uploaded"`

    A file was uploaded to a Claude project.

  - `"claude_project_reported"`

    A Claude project was reported.

  - `"claude_project_sharing_updated"`

    A Claude project's sharing settings were updated.

  - `"claude_project_sync_source_created"`

    A sync source was connected to a Claude project's knowledge base.

  - `"claude_project_sync_source_deleted"`

    A sync source was disconnected from a Claude project's knowledge base.

  - `"claude_project_sync_source_updated"`

    A Claude project sync source's configuration was updated.

  - `"claude_project_viewed"`

    A Claude project was viewed.

  - `"claude_published_artifact_deleted"`

    A published artifact was deleted or unpublished — by its creator, by an organization admin, or by Anthropic (for example, when it was removed for a policy violation).

  - `"claude_pubsec_identity_configured"`

    SAML IdP configuration updated for a public sector organization.

  - `"claude_skill_created"`

    Skill was created.

  - `"claude_skill_deleted"`

    Skill was deleted.

  - `"claude_skill_disabled"`

    User disabled a skill for their account.

  - `"claude_skill_enabled"`

    User enabled a skill for their account.

  - `"claude_skill_replaced"`

    Skill was replaced.

  - `"claude_user_role_updated"`

    A user's role within the organization was changed, or the user was added to or removed from the organization.

  - `"claude_user_seat_tier_updated"`

    An organization member's seat tier was changed. A null `previous_seat_tier` means the member previously had no seat assigned; a null `current_seat_tier` means the seat was removed.

  - `"claude_user_settings_updated"`

    User updated their personal settings.

  - `"cli_plugin_exec_policy_updated"`

    Admin set or cleared the per-op permission ceiling for a plugin CLI.

  - `"compliance_api_accessed"`

    Logging event auto-generated for each compliance API request.

  - `"cowork_session_updated"`

    A Cowork session was updated.

  - `"design_project_artifact_published"`

    A Claude Design project's content was published as a claude.ai artifact, making a snapshot of one of its files viewable outside the project's sharing settings.

  - `"design_project_created"`

    A Claude Design project was created.

  - `"design_project_deleted"`

    A Claude Design project was deleted.

  - `"design_project_member_added"`

    A member was granted access to a Claude Design project.

  - `"design_project_member_removed"`

    A member's access to a Claude Design project was revoked.

  - `"design_project_member_role_updated"`

    A Claude Design project member's role was changed.

  - `"design_project_published"`

    A Claude Design template or design system was published, making it discoverable by everyone in its organization.

  - `"design_project_sharing_updated"`

    A Claude Design project's link-sharing settings were changed — who the project's link works for, and what people opening it through the link may do. Access granted to individual members is reported separately (see design_project_member_added).

  - `"design_project_unpublished"`

    A Claude Design template or design system was unpublished, removing it from its organization's shared gallery.

  - `"design_project_updated"`

    A Claude Design project's metadata was updated.

  - `"design_project_version_restored"`

    A Claude Design project's working tree was rolled back to a previously saved version, replacing its current files with that version's files.

  - `"design_project_viewed"`

    A Claude Design project's content was read. The surface field records which kind of read — a project open, a full-content read, a single-file read, a saved-version read, or an export request. The actor is the reader.

    This activity type is retired: project content reads are no longer
    recorded. Events of this type may still appear in feeds for reads that
    occurred while it was active.

  - `"desktop_extension_allowlisted"`

    A desktop extension was added to an org's allowlist.

  - `"desktop_extension_blocklisted"`

    A desktop extension was added to the global blocklist.

  - `"desktop_extension_deleted"`

    A desktop extension was deleted, either globally by an admin or org-scoped by an org owner.

  - `"desktop_extension_removed_from_allowlist"`

    A desktop extension was removed from an org's allowlist.

  - `"desktop_extension_unblocked"`

    A desktop extension was removed from the global blocklist.

  - `"desktop_extension_uploaded"`

    A desktop extension was uploaded, either globally by an admin or org-scoped by an org owner.

  - `"desktop_extension_version_uploaded"`

    A new version of an existing org-owned desktop extension was uploaded.

  - `"domain_claim_initiated"`

    Domain capture claim initiated over personal accounts on verified domains.

  - `"end_user_invite_requested"`

    Non-admin member submitted an invite request for a new org member.

  - `"extra_usage_billing_enabled"`

    Usage credit billing was enabled for an organization.

  - `"extra_usage_credit_granted"`

    A promotional usage credit grant was claimed.

  - `"extra_usage_spend_limit_created"`

    Usage credit spend limit was created.

  - `"extra_usage_spend_limit_deleted"`

    Usage credit spend limit was deleted.

  - `"extra_usage_spend_limit_increase_request_approved"`

    A usage credit spend limit increase request was approved.

  - `"extra_usage_spend_limit_increase_request_denied"`

    A usage credit spend limit increase request was denied.

  - `"extra_usage_spend_limit_updated"`

    Usage credit spend limit was updated.

  - `"ghe_configuration_created"`

    Admin created a GHE configuration.

  - `"ghe_configuration_deleted"`

    Admin deleted a GHE configuration.

  - `"ghe_configuration_updated"`

    Admin updated a GHE configuration. Previous/new field pairs are recorded only for settings that changed in the update; secret credentials are never recorded, only whether they were replaced.

  - `"ghe_user_connected"`

    User connected to a GHE instance.

  - `"ghe_user_disconnected"`

    User disconnected from a GHE instance.

  - `"ghe_webhook_signature_invalid"`

    Webhook signature validation failed.

  - `"github_token_import"`

    A user attempted to import a personal GitHub access token for use with Claude Code. The `result` field indicates the outcome of the import (imported, rejected, or failed).

  - `"group_created"`

    A group was created (RBAC admin or SCIM provisioning).

  - `"group_deleted"`

    A group was deleted (RBAC admin or SCIM provisioning).

  - `"group_list_viewed"`

    Admin viewed the list of RBAC groups.

  - `"group_member_added"`

    One or more members were added to a group.

  - `"group_member_addition_failed"`

    A request to add members to a group failed. Some of the requested members may have been added before the failure.

  - `"group_member_list_viewed"`

    Admin viewed the members of an RBAC group.

  - `"group_member_removal_failed"`

    A request to remove members from a group failed. Some of the requested members may have been removed before the failure.

  - `"group_member_removed"`

    One or more members were removed from a group.

  - `"group_project_shares_revoked"`

    An RBAC group's project shares in one organization were revoked in bulk.

  - `"group_skill_shares_revoked"`

    An RBAC group's skill shares in one organization were revoked in bulk.

  - `"group_updated"`

    A group was updated (RBAC admin or SCIM provisioning).

  - `"group_viewed"`

    A group was viewed.

  - `"group_visibility_updated"`

    An RBAC group's visibility policy was updated.

  - `"inference_hooks_circuit_breaker_tripped"`

    The organization's Inference hooks circuit breaker tripped automatically: calls to the organization's Inference hooks endpoint crossed a failure threshold, and inspection was suspended to protect live traffic. While tripped, requests are handled according to the organization's failure handling setting — allowed through uninspected (fail open) or rejected (fail closed) — and no per-request Inference hooks activities are recorded. The tripped state persists until an administrator re-enables Inference hooks inspection (or explicitly resets the circuit breaker).

  - `"inference_hooks_config_deleted"`

    Inference hooks configuration was removed for the
    organization.

  - `"inference_hooks_config_updated"`

    Inference hooks configuration was created or updated for the
    organization.

  - `"inference_hooks_request_denied"`

    Inference hooks inspection denied a request. The request was blocked and no model response was produced.

  - `"inference_hooks_request_failed_open"`

    A request proceeded without Inference hooks inspection because a verdict could not be obtained and the organization's Inference hooks configuration is set to fail open.

  - `"inference_hooks_signing_secret_generated"`

    A request signing secret was generated for the organization's
    Inference hooks configuration.

  - `"integration_user_connected"`

    User connected to an integration.

  - `"integration_user_disconnected"`

    User disconnected from an integration.

  - `"invoice_collection_method_updated"`

    Invoice collection method was changed.

  - `"lti_launch_initiated"`

    LTI launch was initiated.

  - `"lti_launch_success"`

    LTI launch completed successfully.

  - `"lti_platform_created"`

    Anthropic staff created an LTI platform integration on behalf of an org.

  - `"lti_platform_updated"`

    Anthropic staff updated an LTI platform integration on behalf of an org.

  - `"magic_link_login_failed"`

    A magic link sign-in attempt failed.

  - `"magic_link_login_initiated"`

    A user requested a magic link sign-in email.

  - `"magic_link_login_succeeded"`

    A user successfully signed in with a magic link email.

  - `"managed_organization_setup_completed"`

    Managed (AWS Marketplace) organization setup was completed.

  - `"marketplace_created"`

    Admin created an organization marketplace.

  - `"marketplace_deleted"`

    Admin deleted an organization marketplace.

  - `"marketplace_updated"`

    Admin updated an organization marketplace.

  - `"marketplace_webhook_deleted"`

    Admin removed the GitHub push webhook for a marketplace.

  - `"marketplace_webhook_provisioned"`

    Admin provisioned a GitHub push webhook for a marketplace.

  - `"mcp_directory_server_published"`

    The organization published its approved MCP directory listing.

  - `"mcp_server_created"`

    An MCP server was added to the organization.

  - `"mcp_server_deleted"`

    An MCP server was removed from the organization.

  - `"mcp_server_managed_auth_token_exchanged"`

    A user attempted to obtain an access token for an MCP server via enterprise managed authorization. This event reports the outcomes of attempted token exchanges. Repeated failures with the same cause may be reported once until the cause changes, and requests denied by organization policy before a token exchange is attempted are not reported, with the exception of the "connector_scope_not_granted" failures described under error_type.

  - `"mcp_server_managed_auth_updated"`

    An MCP server's enterprise managed authorization settings were set, changed, or cleared, including when they were supplied while the server was being added or edited. Fields without a "previous_" prefix describe the settings after the change and are null when the server has no managed authorization settings afterwards; "previous_" fields describe the settings before the change and are null when the server had none before (always the case for a newly added server).

  - `"mcp_server_updated"`

    An MCP server's configuration was updated.

  - `"mcp_tool_policy_updated"`

    The permission restriction for an MCP tool was set or cleared.

  - `"org_analytics_api_capability_updated"`

    Organization analytics_api capability was enabled or disabled.

  - `"org_bulk_delete_initiated"`

    Organization bulk deletion was initiated.

  - `"org_capability_grant_added"`

    A capability grant was added to a workspace or role.

  - `"org_capability_grant_removed"`

    A capability grant was removed from a workspace or role.

  - `"org_claude_code_data_sharing_disabled"`

    Organization Claude Code data sharing was disabled.

  - `"org_claude_code_data_sharing_enabled"`

    Organization Claude Code data sharing was enabled.

  - `"org_claude_code_desktop_disabled"`

    Organization Claude Code Desktop was disabled.

  - `"org_claude_code_desktop_enabled"`

    Organization Claude Code Desktop was enabled.

  - `"org_claude_code_zero_data_retention_disabled"`

    A primary owner disabled zero data retention for Claude Code, so Claude
    Code content is retained according to the organization's data retention
    settings.

  - `"org_compliance_api_settings_updated"`

    Organization compliance API settings were updated.

  - `"org_connector_domain_guard_updated"`

    Enterprise admin changed whether connectors are restricted to verified domains.

  - `"org_cowork_act_without_asking_mode_disabled"`

    The "Act without asking" mode in Cowork was disabled for the organization, so members can no longer let Claude act without asking for approval.

  - `"org_cowork_act_without_asking_mode_enabled"`

    The "Act without asking" mode in Cowork was enabled for the organization, allowing members to let Claude act without asking for approval.

  - `"org_cowork_agent_disabled"`

    Organization Cowork Agent was disabled.

  - `"org_cowork_agent_enabled"`

    Organization Cowork Agent was enabled.

  - `"org_cowork_auto_mode_disabled"`

    The "Auto" permission mode in Cowork was disabled for the organization, so members can no longer let Claude approve its own actions after a safety check.

  - `"org_cowork_auto_mode_enabled"`

    The "Auto" permission mode in Cowork was enabled for the organization, allowing members to let Claude approve its own actions after a safety check.

  - `"org_cowork_disabled"`

    Organization cowork was disabled.

  - `"org_cowork_enabled"`

    Organization cowork was enabled.

  - `"org_cowork_mcp_always_allow_disabled"`

    The "Always allow" option for connector tools in Cowork was disabled for the organization, so each use of a connector tool that can make changes requires approval. Read-only connector tools are not affected by this setting.

  - `"org_cowork_mcp_always_allow_enabled"`

    The "Always allow" option for connector tools in Cowork was enabled for the organization, letting members approve a connector tool that can make changes once and allow its later uses automatically. Read-only connector tools are not affected by this setting.

  - `"org_cowork_otlp_settings_updated"`

    The organization's Cowork OpenTelemetry monitoring export settings were updated.

  - `"org_cowork_remote_disabled"`

    Running Cowork in the cloud was disabled for the organization, so members can no longer run Cowork sessions in Anthropic-hosted remote environments.

  - `"org_cowork_remote_enabled"`

    Running Cowork in the cloud was enabled for the organization, allowing members to run Cowork sessions in Anthropic-hosted remote environments.

  - `"org_creation_blocked"`

    Organization creation was blocked.

  - `"org_data_export_accessed"`

    Organization data export file was accessed/downloaded via signed URL.

  - `"org_data_export_completed"`

    Organization data export was completed.

  - `"org_data_export_started"`

    Organization data export was started.

  - `"org_data_residency_updated"`

    The organization's inference data residency settings were updated.

  - `"org_deleted_via_bulk"`

    Organization was deleted via bulk operation.

  - `"org_deletion_requested"`

    Organization deletion was requested.

  - `"org_directory_resync_completed"`

    Organization directory resync completed successfully.

  - `"org_directory_resync_failed"`

    Organization directory resync failed.

  - `"org_directory_resync_started"`

    Organization directory resync was started asynchronously.

  - `"org_directory_sync_activated"`

    Organization directory sync was activated.

  - `"org_directory_sync_add_initiated"`

    Organization directory sync setup was initiated.

  - `"org_directory_sync_deleted"`

    Organization directory sync was deleted.

  - `"org_discoverability_disabled"`

    Admin disabled organization discoverability.

  - `"org_discoverability_enabled"`

    Admin enabled organization discoverability.

  - `"org_discoverability_settings_updated"`

    Admin updated organization discoverability settings.

  - `"org_domain_add_initiated"`

    Organization domain verification was initiated.

  - `"org_domain_removed"`

    Organization domain was removed.

  - `"org_domain_verified"`

    Organization domain was verified.

  - `"org_external_key_created"`

    A CMEK external key config was created.

  - `"org_external_key_deleted"`

    A CMEK external key config was deleted.

  - `"org_external_key_updated"`

    A CMEK external key config was updated.

  - `"org_external_key_validated"`

    A CMEK external key config was validated against the customer's KMS.

  - `"org_hipaa_self_serve_enabled"`

    A primary owner click-accepted the BAA and enabled HIPAA protections
    for the organization via the self-serve flow.

  - `"org_invite_link_disabled"`

    Organization invite link was disabled.

  - `"org_invite_link_generated"`

    Organization invite link was generated.

  - `"org_invite_link_regenerated"`

    Organization invite link was regenerated (previous link invalidated).

  - `"org_invite_viewed"`

    An organization invite was viewed.

  - `"org_invites_listed"`

    Organization invites were listed.

  - `"org_ip_restriction_created"`

    Organization IP restriction was created.

  - `"org_ip_restriction_deleted"`

    Organization IP restriction was deleted.

  - `"org_ip_restriction_updated"`

    Organization IP restriction was updated.

  - `"org_join_proposal_decided"`

    Approve or reject decision on a parent-org join proposal.

  - `"org_join_request_approved"`

    Admin approved a join request.

  - `"org_join_request_created"`

    User requested to join an organization.

  - `"org_join_request_dismissed"`

    Admin dismissed a join request.

  - `"org_join_request_instant_approved"`

    Join request was instantly approved.

  - `"org_join_requests_bulk_dismissed"`

    Admin bulk-dismissed join requests.

  - `"org_magic_link_second_factor_toggled"`

    Organization magic link second factor was toggled.

  - `"org_member_invites_disabled"`

    Admin disabled member invites for the organization.

  - `"org_member_invites_enabled"`

    Admin enabled member invites for the organization.

  - `"org_members_exported"`

    Organization members list was exported as CSV.

  - `"org_model_default_updated"`

    An organization or role default model setting was changed by an administrator.

  - `"org_parent_join_proposal_created"`

    Organization parent join proposal was created.

  - `"org_parent_search_performed"`

    Organization parent search was performed.

  - `"org_sso_add_initiated"`

    Organization SSO setup was initiated.

  - `"org_sso_connection_activated"`

    Organization SSO connection was activated.

  - `"org_sso_connection_deactivated"`

    Organization SSO connection was deactivated.

  - `"org_sso_connection_deleted"`

    Organization SSO connection was deleted.

  - `"org_sso_group_role_mappings_updated"`

    Organization SSO group role mappings were updated.

  - `"org_sso_provisioning_mode_changed"`

    Organization SSO provisioning mode was changed.

  - `"org_sso_scim_welcome_email_toggled"`

    Organization SCIM-provisioned welcome email was toggled.

  - `"org_sso_seat_tier_assignment_toggled"`

    Organization SSO seat tier assignment was toggled.

  - `"org_sso_seat_tier_mappings_updated"`

    Organization SSO seat tier mappings were updated.

  - `"org_sso_toggled"`

    Organization SSO was toggled on or off.

  - `"org_sync_deleting_synchronized_files_started"`

    Organization started deleting synchronized files.

  - `"org_sync_synchronized_files_deleted"`

    Organization synchronized files were deleted.

  - `"org_taint_added"`

    A taint was added to an organization.

  - `"org_taint_removed"`

    A taint was removed from an organization.

  - `"org_user_deleted"`

    User was removed from organization.

  - `"org_user_invite_accepted"`

    Organization user invite was accepted.

  - `"org_user_invite_deleted"`

    Organization user invite was deleted.

  - `"org_user_invite_re_sent"`

    Organization user invite was re-sent.

  - `"org_user_invite_rejected"`

    Organization user invite was rejected.

  - `"org_user_invite_sent"`

    Organization user invite was sent.

  - `"org_user_left"`

    User removed themselves from organization.

  - `"org_user_trusted_devices_revoked"`

    An organization admin revoked a member's trusted devices and signed the member out of all active sessions.

  - `"org_user_viewed"`

    An organization user was viewed.

  - `"org_users_listed"`

    Organization users were listed.

  - `"org_work_across_apps_disabled"`

    The organization's "Let Claude work across apps" setting was turned off.

  - `"org_work_across_apps_enabled"`

    The organization's "Let Claude work across apps" setting was turned on.

  - `"organization_address_updated"`

    The organization's billing or shipping address was updated.

  - `"organization_icon_deleted"`

    Organization's custom icon deleted.

  - `"organization_icon_updated"`

    Organization's custom icon uploaded or replaced.

  - `"owned_projects_access_restored"`

    Access to owned projects was restored.

  - `"payment_method_updated"`

    The organization's default payment method was updated.

  - `"pending_share_created"`

    A pending share of a project or skill was created for an email address that is not yet an organization member.

  - `"pending_share_revoked"`

    A pending share of a project or skill was revoked before the invitee joined the organization.

  - `"phone_code_sent"`

    User requested a phone verification code.

  - `"phone_code_verified"`

    User successfully verified their phone code.

  - `"platform_agent_archived"`

    An agent was archived on the API platform.

  - `"platform_agent_created"`

    An agent was created on the API platform.

  - `"platform_agent_deleted"`

    An agent was deleted from the API platform.

  - `"platform_agent_deployment_archived"`

    An agent deployment was archived on the API platform.

  - `"platform_agent_deployment_created"`

    An agent deployment was created on the API platform.

  - `"platform_agent_deployment_deleted"`

    An agent deployment was deleted from the API platform.

  - `"platform_agent_deployment_paused"`

    An agent deployment was paused on the API platform.

  - `"platform_agent_deployment_run_triggered"`

    An agent deployment was run on demand on the API platform.

  - `"platform_agent_deployment_unpaused"`

    An agent deployment was resumed on the API platform.

  - `"platform_agent_deployment_updated"`

    An agent deployment was updated on the API platform.

  - `"platform_agent_session_archived"`

    An agent session was archived on the API platform.

  - `"platform_agent_session_created"`

    An agent session was created on the API platform.

  - `"platform_agent_session_deleted"`

    An agent session was deleted from the API platform.

  - `"platform_agent_session_resource_added"`

    A resource was attached to an agent session.

  - `"platform_agent_session_resource_deleted"`

    A resource attached to an agent session was removed.

  - `"platform_agent_session_resource_updated"`

    A resource attached to an agent session was updated.

  - `"platform_agent_session_thread_archived"`

    A thread within an agent session was archived.

  - `"platform_agent_session_updated"`

    An agent session was updated on the API platform.

  - `"platform_agent_updated"`

    An agent was updated on the API platform.

  - `"platform_api_key_created"`

    An API key was created.

  - `"platform_api_key_updated"`

    An API key was updated.

  - `"platform_app_attest_authentication"`

    An attested mobile device attempted to exchange an Apple App Attest assertion for Anthropic API credentials.

  - `"platform_billing_upgraded_to_prepaid"`

    The organization's API billing was upgraded to the prepaid plan.

  - `"platform_clearance_workspace_program_request_cleared"`

    A workspace's clearance program assignment was removed.

  - `"platform_clearance_workspace_program_request_set"`

    A workspace's clearance program assignment was created or updated.

  - `"platform_cost_report_viewed"`

    The cost report was viewed.

  - `"platform_dream_archived"`

    A Dream (asynchronous memory-consolidation job) was archived.

  - `"platform_dream_cancelled"`

    A Dream (asynchronous memory-consolidation job) was cancelled before it completed.

  - `"platform_dream_created"`

    A Dream (asynchronous memory-consolidation job) was created.

  - `"platform_federated_authentication"`

    A federated workload identity attempted to exchange an OIDC token for Anthropic API credentials.

  - `"platform_federation_issuer_archived"`

    An OIDC federation issuer was archived.

  - `"platform_federation_issuer_updated"`

    An OIDC federation issuer was updated.

  - `"platform_federation_rule_archived"`

    An OIDC federation rule was archived.

  - `"platform_federation_rule_updated"`

    An OIDC federation rule was updated.

  - `"platform_federation_rule_workspace_added"`

    A federation rule was enabled for a workspace.

  - `"platform_federation_rule_workspace_removed"`

    A federation rule was disabled for a workspace.

  - `"platform_file_content_downloaded"`

    Activity logged when file content is downloaded via GET /v1/files/{file_id}/content.

  - `"platform_file_deleted"`

    Activity logged when a file is deleted via DELETE /v1/files/{file_id}.

  - `"platform_file_uploaded"`

    Activity logged when a file is uploaded via POST /v1/files.

  - `"platform_memory_created"`

    An agent memory document was created.

  - `"platform_memory_deleted"`

    An agent memory document was deleted.

  - `"platform_memory_store_archived"`

    An agent memory store was archived. Archived stores reject new memory writes and cannot be attached to new sessions; deletion and redaction remain permitted for privacy scrubbing.

  - `"platform_memory_store_created"`

    An agent memory store was created.

  - `"platform_memory_store_deleted"`

    An agent memory store was deleted. Memory content removal may complete asynchronously for very large stores.

  - `"platform_memory_store_updated"`

    An agent memory store's name, description, or metadata was updated.

  - `"platform_memory_updated"`

    An agent memory document's content or path was updated.

  - `"platform_memory_version_redacted"`

    A historical version of an agent memory document was redacted. Redaction scrubs the stored content of a specific version while preserving the version's existence in the history.

  - `"platform_oauth_app_created"`

    An OAuth app was created.

  - `"platform_oauth_app_revoked"`

    An OAuth app was revoked.

  - `"platform_oauth_app_updated"`

    An OAuth app was updated.

  - `"platform_plugin_directory_submission_created"`

    A plugin directory submission was created on the API platform. A plugin directory submission is a request to list a plugin in the public plugin directory.

  - `"platform_plugin_directory_submission_deleted"`

    A plugin directory submission was deleted on the API platform.

  - `"platform_plugin_directory_submission_updated"`

    A plugin directory submission was updated on the API platform.

  - `"platform_service_account_archived"`

    A service account was archived.

  - `"platform_service_account_updated"`

    A service account was updated.

  - `"platform_service_account_workspace_member_added"`

    A service account was added as a member of a workspace.

  - `"platform_service_account_workspace_member_removed"`

    A service account was removed from a workspace.

  - `"platform_service_account_workspace_member_updated"`

    A service account's workspace membership role was updated.

  - `"platform_signing_key_created"`

    Activity logged when a new request-signing key is registered for the org.

  - `"platform_signing_key_deleted"`

    Activity logged when a signing key is permanently deleted.

  - `"platform_signing_key_rotated"`

    Activity logged when an in-memory signing key is rotated.

  - `"platform_skill_version_created"`

    Activity logged when a skill version is created via POST /v1/skills/{skill_id}/versions.

  - `"platform_skill_version_deleted"`

    Activity logged when a skill version is deleted via DELETE /v1/skills/{skill_id}/versions/{version}.

  - `"platform_spend_limit_alert_emails_updated"`

    Spend limit alert email addresses and role targets were updated for an org.

  - `"platform_spend_limit_created"`

    An org-level fixed-dollar spend limit was created.

  - `"platform_spend_limit_deleted"`

    An org-level spend limit was removed.

  - `"platform_spend_limit_updated"`

    An org-level spend limit snooze/ignore state was changed.

  - `"platform_usage_report_claude_code_viewed"`

    The Claude Code usage report was viewed.

  - `"platform_usage_report_messages_viewed"`

    The messages usage report was viewed.

  - `"platform_workspace_archived"`

    A workspace was archived.

  - `"platform_workspace_created"`

    A workspace was created.

  - `"platform_workspace_inference_data_retention_disabled"`

    The zero data retention override was disabled for a workspace.

  - `"platform_workspace_inference_data_retention_enabled"`

    The zero data retention override was enabled for a workspace.

  - `"platform_workspace_member_added"`

    A member was added to a workspace.

  - `"platform_workspace_member_removed"`

    A member was removed from a workspace.

  - `"platform_workspace_member_updated"`

    A workspace member was updated.

  - `"platform_workspace_member_viewed"`

    A workspace member was viewed.

  - `"platform_workspace_members_listed"`

    Workspace members were listed.

  - `"platform_workspace_rate_limit_deleted"`

    A workspace rate limit was deleted.

  - `"platform_workspace_rate_limit_updated"`

    A workspace rate limit was created or updated.

  - `"platform_workspace_updated"`

    A workspace was updated.

  - `"plugin_installation_preference_updated"`

    An org admin changed the installation preference for a plugin.

  - `"prepaid_auto_recharge_disabled"`

    Auto-recharge was disabled for API prepaid org.

  - `"prepaid_auto_recharge_updated"`

    Auto-recharge settings were updated for API prepaid org.

  - `"prepaid_extra_usage_auto_reload_disabled"`

    Prepaid usage credit auto-reload was disabled.

  - `"prepaid_extra_usage_auto_reload_enabled"`

    Prepaid usage credit auto-reload was enabled.

  - `"prepaid_extra_usage_auto_reload_settings_updated"`

    Prepaid usage credit auto-reload settings were updated.

  - `"primary_owner_transferred"`

    Primary owner role was transferred to another org member.

  - `"rbac_role_assigned"`

    Admin assigned an RBAC custom role to a principal.

  - `"rbac_role_created"`

    Admin created an RBAC custom role.

  - `"rbac_role_deleted"`

    Admin deleted an RBAC custom role.

  - `"rbac_role_permission_added"`

    Admin added a permission to an RBAC custom role.

    Emitted once per requested permission, including permissions the role
    already had, so a retried request still produces a complete audit record.

  - `"rbac_role_permission_removed"`

    Admin removed a permission from an RBAC custom role.

    Emitted once per requested permission, including permissions the role
    already lacked, so a retried request still produces a complete audit
    record.

  - `"rbac_role_unassigned"`

    Admin unassigned an RBAC custom role from a principal.

  - `"rbac_role_updated"`

    Admin updated an RBAC custom role.

  - `"role_assignment_granted"`

    Role assignment was granted.

  - `"role_assignment_revoked"`

    Role assignment was revoked.

  - `"scim_user_created"`

    A SCIM user was provisioned.

  - `"scim_user_deleted"`

    A SCIM user was deleted.

  - `"scim_user_updated"`

    A SCIM user was updated.

  - `"scoped_api_key_deleted"`

    A scoped API key was deleted.

  - `"scoped_api_key_updated"`

    A scoped API key was renamed or its activation state changed.

  - `"seat_tier_changes_cancelled"`

    Scheduled seat tier downgrades were cancelled.

  - `"seat_tiers_purchased"`

    Seat tiers were purchased or upgraded on a subscription.

  - `"service_created"`

    Activity logged when an org service is explicitly created.

  - `"service_deleted"`

    Activity logged when an org service is deleted.

  - `"service_key_created"`

    Activity logged when a new org service key is created.

  - `"service_key_revoked"`

    Activity logged when an org service key is revoked.

  - `"session_revoked"`

    User revoked a specific session.

  - `"session_share_accessed"`

    Session share was accessed.

  - `"session_share_created"`

    Session share was created.

  - `"session_share_revoked"`

    Session share was revoked.

  - `"slack_workspace_claim_revoked"`

    A Slack workspace or Enterprise Grid organization was disconnected
    from the organization for Claude in Slack.

  - `"slack_workspace_claimed"`

    A Slack workspace or Enterprise Grid organization was connected to
    the organization for Claude in Slack.

  - `"social_login_succeeded"`

    A user successfully signed in with a social identity provider (Google, Apple, or Microsoft).

  - `"sso_login_failed"`

    An SSO sign-in attempt failed.

  - `"sso_login_initiated"`

    A user started an SSO sign-in flow.

  - `"sso_login_succeeded"`

    A user successfully signed in with SSO.

  - `"sso_second_factor_magic_link"`

    SSO second factor magic link was used.

  - `"step_up_authentication_failed"`

    An additional identity check failed.

  - `"step_up_authentication_succeeded"`

    The user completed an additional identity check to confirm a sensitive action.

  - `"step_up_credential_enrolled"`

    A user enrolled a passkey for confirming sensitive actions on their account.

  - `"subscription_cancellation_scheduled"`

    Subscription cancellation was scheduled at end of billing period.

  - `"subscription_quantity_updated"`

    Contracted subscription seat quantity was updated.

  - `"subscription_renewed"`

    A cancelled subscription was renewed.

  - `"subscription_resumed"`

    A scheduled subscription cancellation was reversed.

  - `"subscription_started"`

    A new subscription was created (Team or Enterprise).

  - `"subscription_upgraded"`

    Subscription plan was upgraded (e.g. Team to Enterprise).

  - `"trusted_device_credential_rotated"`

    The identity-verification credential of a trusted device was rotated to a new key.

  - `"trusted_device_enrolled"`

    A device was enrolled as a trusted device for the user's account. Trusted devices can be used to confirm the user's identity for sensitive actions.

  - `"trusted_device_revoked"`

    A trusted device was removed from the user's account.

  - `"tunnel_archived"`

    An MCP tunnel was archived.

  - `"tunnel_certificate_added"`

    An inner-TLS CA certificate was added to a tunnel.

  - `"tunnel_certificate_revoked"`

    An inner-TLS CA certificate was revoked from a tunnel.

  - `"tunnel_created"`

    An MCP tunnel was created.

  - `"tunnel_token_minted"`

    An OAuth bearer token for the tunnel management API was minted.

  - `"tunnel_token_revealed"`

    The Cloudflare connector secret for a tunnel was revealed to the caller.

  - `"tunnel_token_revoked"`

    An OAuth bearer token for the tunnel management API was revoked.

  - `"tunnel_token_rotated"`

    The Cloudflare connector secret for a tunnel was rotated.

    `tunnel_token_id` is the id of the *newly-issued* token. The previous
    token is invalidated by the rotation and its id is not recorded here.

  - `"user_consent_recorded"`

    User granted a consent for a specific entity (e.g. consumer health consent for an MCP server).

  - `"user_consent_revoked"`

    User revoked a previously granted consent for a specific entity.

  - `"user_logged_out"`

    A user signed out of one or all sessions.

  - `"verification_evidence_submitted"`

    Verification evidence was submitted for an organization's verification.

  - `"verification_program_application_created"`

    An organization applied to a verification program.

  - `"workspace_member_spend_limit_created"`

    A per-member or workspace-default Claude Code spend limit was created.

  - `"workspace_member_spend_limit_deleted"`

    A per-member or workspace-default Claude Code spend limit was deleted.

  - `"workspace_member_spend_limit_updated"`

    A per-member Claude Code spend limit amount was updated.

  - `"workspace_spend_limit_alert_emails_updated"`

    Spend limit alert email recipients were updated for a workspace.

  - `"workspace_spend_limit_created"`

    A workspace-level API spend limit was created.

  - `"workspace_spend_limit_deleted"`

    A workspace-level API spend limit was deleted.

- `limit: optional number`

  Maximum results (default: 100, max: 5000)

- `order: optional "asc" or "desc"`

  Sort direction by `created_at`. `desc` (default) returns newest-first; `asc` returns oldest-first for incremental sync. Activities become queryable after a short asynchronous ingestion delay. When using `asc` with `after_id` for incremental sync, late-arriving rows with timestamps behind the cursor will be skipped; consumers that need at-least-once delivery should periodically re-poll an overlap window via `created_at.gte` and deduplicate by `id`. `after_id` and `before_id` are relative to this order.

  - `"asc"`

  - `"desc"`

- `organization_ids: optional array of string`

  Filter activities by organization IDs (accepts `org_...` or organization UUID). Enumerate IDs via `GET /v1/compliance/organizations`.

- `user_ids: optional array of string`

  Alias for `actor_ids[]`, for consistency with other compliance routes. If both are provided, the lists are merged.

### Header Parameters

- `"x-api-key": optional string`

### Returns

- `data: optional array of object { actor, decision, id, 5 more }  or object { actor, id, created_at, 3 more }  or object { actor, admin_api_key_id, scopes, 5 more }  or 480 more`

  List of activity records. Each element's `type` field identifies which activity it is and which additional fields are present.

  - `AbuseDecisionReceived object { actor, decision, id, 5 more }`

    An external anti-abuse service reported a consequential decision about a sign-in or sign-up attempt.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `decision: "blocked" or "unspecified"`

      The decision applied to the session.

      - `"blocked"`

      - `"unspecified"`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `abuse_session_id: optional string or null`

      The anti-abuse service's opaque session identifier for correlation.

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "abuse_decision_received"`

      - `"abuse_decision_received"`

  - `AccountDeleted object { actor, id, created_at, 3 more }`

    User-initiated self-service account deletion.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "account_deleted"`

      - `"account_deleted"`

  - `AdminAPIKeyCreated object { actor, admin_api_key_id, scopes, 5 more }`

    An admin API key was created.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `admin_api_key_id: string`

      Tagged ID of the created admin API key

    - `scopes: array of string`

      Scopes granted to the key (empty for legacy non-scoped admin keys)

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "admin_api_key_created"`

      - `"admin_api_key_created"`

  - `AdminAPIKeyDeleted object { actor, admin_api_key_id, id, 4 more }`

    An admin API key was deleted.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `admin_api_key_id: string`

      Tagged ID of the deleted admin API key

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "admin_api_key_deleted"`

      - `"admin_api_key_deleted"`

  - `AdminAPIKeyUpdated object { actor, admin_api_key_id, updates, 5 more }`

    An admin API key was updated (renamed or activated/deactivated).

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `admin_api_key_id: string`

      Tagged ID of the updated admin API key

    - `updates: array of object { current_value, previous_value, type }`

      - `current_value: string`

      - `previous_value: string`

      - `type: "name" or "status"`

        - `"name"`

        - `"status"`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "admin_api_key_updated"`

      - `"admin_api_key_updated"`

  - `AdminConnectorRequestResolved object { actor, decision, mcp_server_id, 6 more }`

    Admin approved or dismissed pending member requests to enable an MCP connector.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `decision: "approved" or "dismissed" or "unspecified"`

      - `"approved"`

      - `"dismissed"`

      - `"unspecified"`

    - `mcp_server_id: string`

    - `resolved_count: number`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "admin_connector_request_resolved"`

      - `"admin_connector_request_resolved"`

  - `AdminRequestCreated object { actor, request_type, id, 4 more }`

    Admin request created by an org member (seat upgrade, limit increase, join org, end-user invite).

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `request_type: string`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "admin_request_created"`

      - `"admin_request_created"`

  - `AgeVerified object { actor, id, created_at, 3 more }`

    User age was verified.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "age_verified"`

      - `"age_verified"`

  - `AnonymousMobileLoginAttempted object { actor, id, created_at, 3 more }`

    Anonymous mobile login was attempted.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "anonymous_mobile_login_attempted"`

      - `"anonymous_mobile_login_attempted"`

  - `APIKeyCreated object { actor, api_key_id, scopes, 6 more }`

    Activity logged when a new API key is created.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `api_key_id: string`

      The tagged ID of the created API key

    - `scopes: array of string`

      The scopes for this API key

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `restricted_to_organization: optional boolean`

      Whether the key was restricted to the creating organization, rather than granted access across the whole parent organization

    - `type: optional "api_key_created"`

      - `"api_key_created"`

  - `ClaudeArtifactAccessFailed object { actor, id, claude_artifact_id, 6 more }`

    An attempt to access an artifact failed.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `claude_artifact_id: optional string or null`

      The artifact's identifier, when known.

    - `claude_artifact_version_id: optional string or null`

      The version of the artifact the user attempted to access, when known.

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `reason: optional string or null`

      The reason access was denied, when recorded.

    - `type: optional "claude_artifact_access_failed"`

      - `"claude_artifact_access_failed"`

  - `ClaudeArtifactCommented object { actor, claude_artifact_id, comment_action, 8 more }`

    Comment activity on a published artifact: a comment was added, a thread's resolved state was changed, or a thread was deleted. The actor is the user who performed the action; the comment text itself is stored with the artifact and is not part of this record.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `claude_artifact_id: string`

      The artifact's identifier.

    - `comment_action: "activate_thread" or "create_thread" or "deactivate_thread" or 6 more`

      The action recorded: for example a new comment thread, a reply to an existing thread, a thread resolved, reopened, or deleted, a thread's Claude activation granted or revoked, or a comment's text rewritten by its author.

      - `"activate_thread"`

      - `"create_thread"`

      - `"deactivate_thread"`

      - `"delete_thread"`

      - `"edit_comment"`

      - `"reopen"`

      - `"reply"`

      - `"resolve"`

      - `"unspecified"`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `claude_artifact_comment_id: optional string or null`

      The comment's identifier. Present when the activity relates to a specific comment, for example a new comment or an author's edit of one; absent for thread-level actions performed without a comment, such as resolve, reopen, deletion, or an activation change.

    - `claude_artifact_comment_thread_id: optional string or null`

      The comment thread's identifier.

    - `claude_artifact_version_id: optional string or null`

      The artifact version the comment activity applied to, when known.

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "claude_artifact_commented"`

      - `"claude_artifact_commented"`

  - `ClaudeArtifactCommentsViewed object { actor, claude_artifact_id, id, 5 more }`

    An artifact's comments were viewed.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `claude_artifact_id: string`

      The artifact's identifier.

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `claude_artifact_version_id: optional string or null`

      The version of the artifact whose comments were served, when known.

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "claude_artifact_comments_viewed"`

      - `"claude_artifact_comments_viewed"`

  - `ClaudeArtifactCreated object { actor, claude_artifact_id, id, 4 more }`

    An artifact was created.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `claude_artifact_id: string`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "claude_artifact_created"`

      - `"claude_artifact_created"`

  - `ClaudePublishedArtifactDeleted object { actor, claude_published_artifact_id, id, 4 more }`

    A published artifact was deleted or unpublished — by its creator, by an organization admin, or by Anthropic (for example, when it was removed for a policy violation).

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `claude_published_artifact_id: string`

      The published artifact's identifier.

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "claude_published_artifact_deleted"`

      - `"claude_published_artifact_deleted"`

  - `ClaudeArtifactPublished object { actor, artifact_type, claude_published_artifact_id, 9 more }`

    A new version of an artifact was published — for an artifact created in a chat this is the action that made it publicly viewable; for an artifact created outside a chat it is recorded on every save, including saves of private artifacts, and changes to who can access the artifact are recorded separately as claude_artifact_sharing_updated.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `artifact_type: string`

      Artifact type (code, html, react, etc.)

    - `claude_published_artifact_id: string`

      The published artifact's identifier.

    - `title: string`

      Title of the published artifact

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `claude_artifact_version_id: optional string or null`

      The version identifier recorded as live by this publish.

    - `created_at: optional string`

      When this activity occurred.

    - `description: optional string or null`

      Optional gallery-card description supplied at publish time. Same provenance as title (caller-authored, reader-visible).

    - `is_redeploy: optional boolean or null`

      True when the publish updated an existing artifact; false when the publish created the artifact.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "claude_artifact_published"`

      - `"claude_artifact_published"`

  - `ClaudeArtifactSharingUpdated object { actor, audience, claude_artifact_id, 14 more }`

    An artifact's sharing settings were updated.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `audience: array of object { type }  or object { type }  or object { type }`

      Sharing audience for the project. If empty, this it's only visible to the creating user.

      - `ArtifactSharingAudienceOrganization object { type }`

        Sharing audience: visible to the owning organization.

        - `type: optional "organization"`

          - `"organization"`

      - `ArtifactSharingAudienceUsers object { type }`

        Sharing audience: visible to an explicit allowlist of users.

        - `type: optional "users"`

          - `"users"`

      - `ArtifactSharingAudienceAnyoneWithLink object { type }`

        Sharing audience: anyone with the link, including anonymous viewers
        (an artifact shared to the open internet).

        - `type: optional "anyone_with_link"`

          - `"anyone_with_link"`

    - `claude_artifact_id: string`

      The artifact's identifier.

    - `claude_artifact_version_id: string`

      The artifact version's identifier.

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `new_mode: optional string or null`

      The read-axis sharing mode after the change: `owner`, `users`, or `org`.

    - `new_user_count: optional number or null`

      The number of accounts on the explicit read allowlist after the change. Only meaningful when `new_mode` is `users`.

    - `new_write_mode: optional string or null`

      The write-axis sharing mode after the change: `owner`, `users`, or `org`.

    - `new_write_user_count: optional number or null`

      The number of accounts on the explicit write allowlist after the change. Only meaningful when `new_write_mode` is `users`.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `previous_mode: optional string or null`

      The read-axis sharing mode before the change: `owner`, `users`, or `org`.

    - `previous_user_count: optional number or null`

      The number of accounts on the explicit read allowlist before the change. Only meaningful when `previous_mode` is `users`.

    - `previous_write_mode: optional string or null`

      The write-axis sharing mode before the change: `owner`, `users`, or `org`.

    - `previous_write_user_count: optional number or null`

      The number of accounts on the explicit write allowlist before the change. Only meaningful when `previous_write_mode` is `users`.

    - `type: optional "claude_artifact_sharing_updated"`

      - `"claude_artifact_sharing_updated"`

  - `ClaudeArtifactViewed object { actor, claude_artifact_id, id, 5 more }`

    An artifact was viewed.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `claude_artifact_id: string`

      The artifact's identifier.

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `claude_artifact_version_id: optional string or null`

      The version of the artifact the user was served, when known.

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "claude_artifact_viewed"`

      - `"claude_artifact_viewed"`

  - `AuditLogExportAccessed object { actor, id, created_at, 3 more }`

    Audit log export file was accessed/downloaded via signed URL.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `type: optional "audit_log_export_accessed"`

      - `"audit_log_export_accessed"`

  - `AuditLogExportStarted object { actor, id, created_at, 5 more }`

    Audit log export was initiated.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `created_at: optional string`

      When this activity occurred.

    - `from_date: optional string or null`

      Start date of the export range

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `to_date: optional string or null`

      End date of the export range

    - `type: optional "audit_log_export_started"`

      - `"audit_log_export_started"`

  - `BillingEmailsUpdated object { actor, id, cc_email_count, 6 more }`

    The organization's billing email recipients were updated.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string or null`

      - `AttestedDeviceActor object { external_client_id, kid_hash, ip_address, 2 more }`

        An attested mobile device authenticated via Apple App Attest.

        - `external_client_id: string`

        - `kid_hash: string`

        - `ip_address: optional string or null`

        - `type: optional "attested_device_actor"`

          - `"attested_device_actor"`

        - `user_agent: optional string or null`

    - `id: optional string`

      Unique identifier for the activity e.g. 'activity_abcd1234'

    - `cc_email_count: optional number or null`

      Number of 'cc' email recipients.

    - `created_at: optional string`

      When this activity occurred.

    - `organization_id: optional string or null`

      Organization ID this activity is associated with

    - `organization_uuid: optional string or null`

      Organization UUID where the activity occurred. Null when the activity is not tied to an organization (for example, login and logout events or calls to the Compliance API).

    - `primary_email_set: optional boolean or null`

      Whether a primary billing email is configured.

    - `to_email_count: optional number or null`

      Number of 'to' email recipients.

    - `type: optional "billing_emails_updated"`

      - `"billing_emails_updated"`

  - `CcrAgentCreated object { actor, agent_id, default_source_urls_truncated, 11 more }`

    A Claude Code agent was created.

    - `actor: object { api_key_id, ip_address, user_agent, type }  or object { email_address, ip_address, user_agent, 2 more }  or object { ip_address, user_agent, type, unauthenticated_email_address }  or 8 more`

      Automated background processing performed by Anthropic systems, acting
      without a user or customer credential.

      - `APIActor object { api_key_id, ip_address, user_agent, type }`

        - `api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "api_actor"`

          - `"api_actor"`

      - `UserActor object { email_address, ip_address, user_agent, 2 more }`

        - `email_address: string`

        - `ip_address: string`

        - `user_agent: string`

        - `user_id: string`

        - `type: optional "user_actor"`

          - `"user_actor"`

      - `UnauthenticatedUserActor object { ip_address, user_agent, type, unauthenticated_email_address }`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "unauthenticated_user_actor"`

          - `"unauthenticated_user_actor"`

        - `unauthenticated_email_address: optional string or null`

      - `AnthropicActor object { email_address, type }`

        - `email_address: optional string or null`

        - `type: optional "anthropic_actor"`

          - `"anthropic_actor"`

      - `SystemActor object { service, type }`

        Automated background processing performed by Anthropic systems, acting
        without a user or customer credential.

        - `service: optional string or null`

          Name of the automated process that performed the action, when known.

        - `type: optional "system_actor"`

          - `"system_actor"`

      - `AdminAPIKeyActor object { admin_api_key_id, ip_address, user_agent, type }`

        - `admin_api_key_id: string`

        - `ip_address: string`

        - `user_agent: string`

        - `type: optional "admin_api_key_actor"`

          - `"admin_api_key_actor"`

      - `ServiceAccountActor object { ip_address, service_account_id, user_agent, type }`

        - `ip_address: string`

        - `service_account_id: string`

        - `user_agent: string`

        - `type: optional "service_account_actor"`

          - `"service_account_actor"`

      - `ScimDirectorySyncActor object { directory_id, workos_event_id, idp_connection_type, type }`

        - `directory_id: string`

        - `workos_event_id: string`

        - `idp_connection_type: optional string or null`

        - `type: optional "scim_directory_sync_actor"`

          - `"scim_directory_sync_actor"`

      - `FederatedIdentityActor object { issuer, subject, audience, 3 more }`

        A federated external workload authenticated via a verified OIDC token.

        Carries the verified issuer, subject, and audience claims from the
        presented JWT.

        - `issuer: string`

        - `subject: string`

        - `audience: optional array of string`

        - `ip_address: optional string or null`

        - `type: optional "federated_identity_actor"`

          - `"federated_identity_actor"`

        - `user_agent: optional string or null`

      - `FederatedActor object { provider, ip_address, subject, 2 more }`

        An external identity asserted by a trusted provider — a cloud-provider
        gateway or a customer-registered federation issuer — acting without an
        Anthropic-provisioned account or service account.

        - `provider: object { account_id, signed_principal, type }  or object { subscription_id, type }  or object { project_number, type }  or object { issuer, type }`

          Asserting party: the AWS account the organization is bound to.

          - `FederatedActorAwsProvider object { account_id, signed_principal, type }`

            Asserting party: the AWS account the organization is bound to.

            - `account_id: string`

            - `signed_principal: string`

              The AWS-signed ARN of the IAM principal that requested the token.

            - `type: optional "aws"`

              - `"aws"`

          - `FederatedActorAzureProvider object { subscription_id, type }`

            Asserting party: the Azure subscription the organization is bound to.

            - `subscription_id: string`

            - `type: optional "azure"`

              - `"azure"`

          - `FederatedActorGcpProvider object { project_number, type }`

            Asserting party: the GCP project the organization is bound to.

            - `project_number: string`

            - `type: optional "gcp"`

              - `"gcp"`

          - `FederatedActorOidcProvider object { issuer, type }`

            Asserting party: a customer-registered OIDC federation issuer.

            - `issuer: optional string or null`

              The federation issuer's URL. Null when the presented credential failed verification.

            - `type: optional "oidc"`

              - `"oidc"`

        - `ip_address: optional string or null`

        - `subject: optional string or null`

          The provider's verified identifier for the caller; its form depends on the provider.

        - `type: optional "federated_actor"`

          - `"federated_actor"`

        - `user_agent: optional string o
