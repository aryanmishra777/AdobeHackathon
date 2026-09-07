# platform.claude.com Documentation (Part 22 of 35)

## Related resources

Source: https://platform.claude.com/llms-full.txt#related-resources

* [Compliance API overview](https://platform.claude.com/docs/en/manage-claude/compliance-api)
* [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed)
* [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)
* [Customer-Managed Encryption Keys (CMEK)](https://platform.claude.com/docs/en/manage-claude/cmek)
* [Claude Code data usage](https://code.claude.com/docs/en/data-usage)
* [Trust Center](https://trust.anthropic.com/resources)


---
title: API and data retention
url: https://platform.claude.com/docs/en/manage-claude/api-and-data-retention
description: Learn about how Anthropic's APIs and associated features retain data, including information about zero data retention (ZDR) and HIPAA-ready API access.
---

This page covers the Claude API (`api.anthropic.com`), Claude Platform on AWS, and [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), where Anthropic is the data processor. On Amazon Bedrock and Google Cloud's Agent Platform, the cloud provider is the data processor; refer to those platforms' data retention and compliance documentation for their equivalent controls.

Anthropic offers two data handling arrangements for the Claude API: [zero data retention (ZDR)](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#zero-data-retention-zdr-scope) and [HIPAA readiness](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#hipaa-readiness). The [feature eligibility table](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility) lists which API features each arrangement covers. For Anthropic's standard retention policies outside these arrangements, see the [commercial data retention policy](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data) and the [consumer data retention policy](https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data).


## How Anthropic approaches data retention

Source: https://platform.claude.com/llms-full.txt#how-anthropic-approaches-data-retention

Different APIs and features have different storage needs. Where a feature does not require storage of customer prompts or responses, it may be eligible for ZDR. Where a feature necessarily requires storage, Anthropic designs for the smallest possible retention footprint under the following commitments:

* Retained data is never used for model training without your express permission.
* Only what is technically necessary for the feature to work is retained. Conversation content (your prompts and Claude's outputs) is not retained by default; the exception is [Covered Models](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements), which require 30-day retention.
* Retained data is purged on the shortest practical time to live (TTL), and Anthropic aims to give customers control over how long data is retained. What is held, and the retention duration where a specific TTL applies, is documented on each feature's page.

Several retention models sit outside the ZDR and HIPAA arrangements described on this page. Data accessible through the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) follows its own retention model. The [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) retains data for 6 years. Chat, file, and project content from claude.ai follows your organization's retention policy set in [claude.ai > Organization settings > Data and privacy](https://claude.ai/admin-settings/data-privacy-controls). [Local session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions) (from sessions on users' machines, in apps such as Cowork and Claude Code) are stored for 6 years by default, or for your organization's custom conversation retention period when a finite one is set (the same claude.ai setting). [Remote session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-remote-sessions) (Cowork in the cloud) are retained for 6 years, unless a user deletes the session sooner. The Compliance API does not capture local sessions for which ZDR is in effect, or any local sessions from organizations with HIPAA readiness enabled.


## Zero data retention (ZDR)

Source: https://platform.claude.com/llms-full.txt#zero-data-retention-zdr

Under a ZDR arrangement, Anthropic does not store customer prompts or responses at rest after the API response is returned. To request ZDR for your organization, contact the [Anthropic sales team](https://claude.com/contact-sales). ZDR is enabled per organization; each new organization requires ZDR to be enabled separately by your account team, and enablement does not automatically extend to other organizations under the same account.

### What ZDR covers

* **Claude Messages and Token Counting APIs:** ZDR applies to these endpoints for eligible features listed in the [feature eligibility table](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility). Features that ride on `/v1/messages` but are marked "No" in the table (such as code execution) are not covered.
* **Claude Code:** ZDR applies when Claude Code is used with API keys from a Commercial organization (an organization under Anthropic's Commercial Terms of Service, as distinct from a consumer Claude account) or through Claude Enterprise with ZDR enabled. If metrics logging is enabled in Claude Code, productivity data such as usage statistics is exempted from ZDR and may be retained. See the [Claude Code ZDR documentation](https://code.claude.com/docs/en/zero-data-retention) for full details.
* **Claude Platform on AWS:** [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) follows the same data retention policy as the first-party Claude API. ZDR is available on request; contact your Anthropic account representative to enable it.

### What ZDR does not cover

* **Claude Console:** Any usage in the Claude Console, including playground.
* **Claude Managed Agents:** Claude Managed Agents is a stateful resource; session transcripts persist until you delete them.
* **Claude consumer products:** Claude Free, Pro, and Max plans, including when customers on those plans use Claude's web, desktop, or mobile apps or Claude Code.
* **Claude Teams and Claude Enterprise product interfaces:** These interfaces are not ZDR-eligible. The exception is Claude Code used through Claude Enterprise with ZDR enabled; see [What ZDR covers](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#what-zdr-covers).
* **Claude for Excel:** Not currently ZDR-eligible.
* **Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, and Claude Mythos 5:** These models require 30-day data retention and are not available under ZDR unless expressly authorized by Anthropic. See [Model-specific data retention requirements](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements).
* **Third-party integrations:** Data processed by third-party websites, tools, or other integrations is not covered, though some may have similar offerings. Review each service's data handling practices.
* **Cross-Origin Resource Sharing (CORS):** CORS is not supported for organizations with ZDR arrangements. To make API calls from browser-based applications, route requests through a backend proxy server. See the [API security guidance](https://platform.claude.com/docs/en/api/overview) for proxy patterns and API-key handling.
* **Flagged content and legal holds:** See [Retention regardless of arrangement](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#retention-regardless-of-arrangement).

<Note>
  For the most up-to-date information on which products and features are ZDR-eligible, refer to your contract terms or contact your Anthropic account representative.
</Note>


## HIPAA readiness

Source: https://platform.claude.com/llms-full.txt#hipaa-readiness

The Claude API supports HIPAA-ready integrations for organizations that handle protected health information (PHI). With a signed BAA and a HIPAA-enabled organization, you can use supported API features to process PHI while supporting your organization's HIPAA compliance. Eligible organizations can review and execute the BAA and enable HIPAA readiness directly from the Claude Console. HIPAA readiness applies a broader set of privacy and security safeguards than ZDR (encryption, access controls, and audit logging that protect PHI throughout its lifecycle) rather than requiring immediate deletion. If your organization handles PHI, HIPAA readiness is the arrangement to use; you do not also need ZDR. See the [feature eligibility table](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility) for which features each arrangement covers.

<Note>
  This page covers HIPAA readiness for the Claude API. For the full HIPAA Implementation Guide covering Claude Enterprise and configuration requirements, see the [Anthropic Trust Center](https://trust.anthropic.com/resources).
</Note>

### What HIPAA readiness covers

* **Claude API:** HIPAA readiness applies to the Claude API (`api.anthropic.com`) for eligible features listed in the [feature eligibility table](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility).

### What HIPAA readiness does not cover

* **Claude consumer products:** Claude Free, Pro, and Max plans.
* **Claude Console:** Usage through the Claude Console interface (enabling HIPAA readiness from Console settings is supported; processing PHI through the Console is not covered).
* **Partner-operated platforms:** Amazon Bedrock and Google Cloud's Agent Platform. Refer to those platforms' compliance documentation.
* **Claude Platform on AWS and Microsoft Foundry:** HIPAA readiness is not available on these platforms.
* **Third-party integrations:** Data processed by external tools or services connected to your application.
* **Claude Code:** Claude Code is not covered under HIPAA readiness.
* **Beta features:** Features in beta are generally not covered under the BAA unless explicitly listed as eligible in the [feature eligibility table](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility).
* **Flagged content and legal holds:** See [Retention regardless of arrangement](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#retention-regardless-of-arrangement).

### PHI handling guidelines

Protected health information (PHI) includes any individually identifiable health information. In the context of the Claude API, PHI typically appears in message content (prompts and Claude's responses), attached files (images, PDFs), and file names or metadata associated with message content. The following fields are not expected to contain PHI under the BAA: workspace names, user information (name, email, phone number), billing data, and support tickets.

When using [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) or tools with `strict: true`, the API compiles JSON schemas into grammars that are cached separately from message content. These cached schemas do not receive the same PHI protections as prompts and responses. **Do not include PHI in JSON schema definitions.** This restriction applies to schema property names, `enum` values, `const` values, and `pattern` regular expressions. Patient-specific information should appear only in message content, where it is protected under HIPAA safeguards.

### HIPAA error handling

Your signed BAA is the official source of truth for which features are covered. The API also enforces these restrictions automatically. When a HIPAA-enabled organization sends a request that includes a non-eligible feature, the API returns a `400` error to prevent accidental use of features not covered by your BAA:

The error message lists the non-eligible features detected in the request; remove them and retry. The phrase "without Zero Data Retention" is the API's own wording and does not change the resolution. Client-side tools whose Details column in the [feature eligibility table](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility) says they are not blocked are accepted but remain outside HIPAA readiness.

### Getting started with HIPAA readiness

There are two ways to set up HIPAA-ready API access. Most organizations can enable it directly in the Claude Console with Anthropic's standard BAA; organizations that require a negotiated BAA should work with their account team.

#### Enable in the Console (standard BAA)

<Steps>
  <Step title="Open your organization's privacy settings">
    In [Claude Console > Settings > Privacy](https://platform.claude.com/settings/privacy), organization admins with the HIPAA management permission see a **HIPAA compliance** card. If your organization is eligible but you don't see the option to enable, ask an organization admin to complete these steps.
  </Step>

  <Step title="Review and execute the BAA">
    Download the Business Associate Agreement and the HIPAA Implementation Guide, then accept the agreement as an authorized legal representative of your organization. Each step becomes available after you download the prior document, and your enablement is bound to the exact BAA version you downloaded.
  </Step>

  <Step title="Enablement takes effect immediately">
    HIPAA readiness controls are applied to your organization as soon as you accept. Once HIPAA readiness is enabled for your organization, the configuration is permanent and cannot be disabled by an administrator. The API automatically enforces feature restrictions, returning an error for requests that use non-eligible features. See [HIPAA error handling](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#hipaa-error-handling) for the error and the client-side tool exception.
  </Step>
</Steps>

#### Contact sales (custom BAA)

If your organization requires a negotiated or custom BAA, or if self-serve enablement isn't available for your organization, contact the [Anthropic sales team](https://claude.com/contact-sales). Anthropic will execute the BAA and enable HIPAA readiness for your organization.

#### Build with eligible features

Whichever path you use, confirm which features are supported in the [feature eligibility table](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility) and review the [PHI handling guidelines](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#phi-handling-guidelines) for features that restrict where PHI can appear. For detailed configuration and compliance requirements, refer to the [HIPAA Implementation Guide](https://trust.anthropic.com/resources).

<Warning>
  HIPAA readiness is enforced at the organization level. If you need both HIPAA-ready and general-purpose API access, use separate organizations for each.
</Warning>


## Model-specific data retention requirements

Source: https://platform.claude.com/llms-full.txt#model-specific-data-retention-requirements

Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, and Claude Mythos 5 are designated Covered Models (see the [Covered Models support article](https://support.claude.com/en/articles/15425695)) and require 30-day data retention; ZDR is therefore not available for any of them unless expressly authorized by Anthropic. On the Claude API, requests to Claude Fable 5 from an organization whose data retention configuration does not meet this requirement return a `400 invalid_request_error`:

The 30-day data retention requirement applies wherever Covered Models are offered. On the Claude API (including Claude Platform on AWS), Anthropic handles retained data. On Amazon Bedrock and Google Cloud's Agent Platform, retained data stays within your cloud provider's environment; review each platform's documentation for enablement steps.

### Enable 30-day retention for a workspace

Organizations with a ZDR arrangement can make these models available in a specific workspace by enabling 30-day retention for that workspace only. Other workspaces in the organization keep zero data retention.

<Steps>
  <Step title="Open the workspace's privacy controls">
    In [Claude Console > Settings > Workspaces](https://platform.claude.com/settings/workspaces), select the workspace and open its **Privacy controls** tab.
  </Step>

  <Step title="Turn on 30-day data retention">
    Enable the 30-day data retention setting for the workspace.
  </Step>

  <Step title="Verify">
    Requests to Covered Models from this workspace now succeed. Workspaces without an override continue to follow the organization default.
  </Step>
</Steps>


## Feature eligibility

Source: https://platform.claude.com/llms-full.txt#feature-eligibility

The following table lists which Claude API features are eligible for ZDR and HIPAA readiness arrangements.

Each eligibility column uses three values:

* **Yes:** The feature is fully eligible under the arrangement. For ZDR, "Yes" also assumes you are using a model that does not require 30-day data retention; [Covered Models](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements) are not available under ZDR regardless of feature eligibility.
* **Yes (qualified):** Your prompts and Claude's outputs are not stored, but a bounded technical artifact (named in the Details column) is retained briefly for the feature to function. See [How Anthropic approaches data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#how-anthropic-approaches-data-retention) for the commitments that govern these features.
* **No:** The feature is not eligible. Under HIPAA readiness, the API blocks requests that include a "No" feature and returns a `400` error, unless the feature's Details column says otherwise. Under ZDR, the API does **not** block these features; using one is a choice to step outside your ZDR arrangement for that specific data, and the feature's own documented retention policy applies. Features marked "No" for ZDR are typically stateful (they store jobs, files, or container state), which is why they cannot be zero-retention.

| Feature                                                                                                                    | Endpoint                                         | ZDR eligible                                            | HIPAA eligible                      | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------- | ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows)                           | `/v1/messages`                                   | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)                                        | `/v1/messages`                                   | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| [Advisor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)                                 | `/v1/messages` (with `advisor` tool)             | <Eligible>Yes</Eligible>                                | <Eligible status="no">No</Eligible> | Advisor model output is returned in the API response; nothing is stored server-side after the response.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| [Agent skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)                                 | `/v1/messages` (with `skills`) / `/v1/skills`    | <Eligible status="no">No</Eligible>                     | <Eligible status="no">No</Eligible> | Skill data retained per standard policy. See [Agent skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#data-retention).                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| [Bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool)                                       | `/v1/messages` (with `bash` tool)                | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            | Client-side tool executed in your environment.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)                                 | `/v1/messages/batches`                           | <Eligible status="no">No</Eligible>                     | <Eligible status="no">No</Eligible> | 29-day retention; async storage required. See [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing#data-retention).                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| [Browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool)                              | `/v1/messages` (with `browser` toolset)          | <Eligible>Yes</Eligible>                                | <Eligible status="no">No</Eligible> | Client-side tool. Anthropic does not run browser actions or retain page content beyond standard API handling. Not covered under HIPAA readiness; requests that include the browser use tool are not blocked. See [Browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#data-retention).                                                                                                                                                                                                                                                                                   |
| [Cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics)                               | `/v1/messages` (with `diagnostics`)              | <Eligible status="qualified">Yes (qualified)</Eligible> | <Eligible status="no">No</Eligible> | Your prompts and Claude's outputs are not stored. A fingerprint of cryptographic hashes and token-count estimates is retained briefly to enable comparison against the next request. See [Cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics#data-retention).                                                                                                                                                                                                                                                                                                            |
| [Citations](https://platform.claude.com/docs/en/build-with-claude/citations)                                               | `/v1/messages`                                   | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)                                       | `/v1/agents`, `/v1/sessions`, `/v1/environments` | <Eligible status="no">No</Eligible>                     | <Eligible status="no">No</Eligible> | Sessions are stateful resources; transcripts persist until you delete them. Applies to all Managed Agents sub-features, including [Self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes).                                                                                                                                                                                                                                                                                                                                                                             |
| [Code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)                        | `/v1/messages` (with `code_execution` tool)      | <Eligible status="no">No</Eligible>                     | <Eligible status="no">No</Eligible> | Container data retained up to 30 days. See [Code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#data-retention).                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| [Computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)                            | `/v1/messages` (with `computer` toolset or tool) | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            | Client-side tool where screenshots and files are captured and stored in your environment, not by Anthropic. See [Computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#data-retention).                                                                                                                                                                                                                                                                                                                                                                                  |
| [Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing)                                   | `/v1/messages` (with `context_management`)       | <Eligible>Yes</Eligible>                                | <Eligible status="no">No</Eligible> | Context edits (tool use clearing and thinking clearing) are applied in real time.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| [Context management (compaction)](https://platform.claude.com/docs/en/build-with-claude/compaction)                        | `/v1/messages` (with `context_management`)       | <Eligible>Yes</Eligible>                                | <Eligible status="no">No</Eligible> | Server-side compaction results are returned and round-tripped statelessly through the API response.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| [Data residency](https://platform.claude.com/docs/en/manage-claude/data-residency)                                         | `/v1/messages` (with `inference_geo`)            | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| [Effort](https://platform.claude.com/docs/en/build-with-claude/effort)                                                     | `/v1/messages` (with `effort`)                   | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| [Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode)                                               | `/v1/messages` (with `speed: "fast"`)            | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            | Same Messages API endpoint with faster inference. ZDR applies regardless of speed setting.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| [Files API](https://platform.claude.com/docs/en/build-with-claude/files)                                                   | `/v1/files`                                      | <Eligible status="no">No</Eligible>                     | <Eligible status="no">No</Eligible> | Files retained until explicitly deleted or they reach their configured expiration. See [Files API](https://platform.claude.com/docs/en/build-with-claude/files#data-retention).                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| [Fine-grained tool streaming](https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming)   | `/v1/messages`                                   | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)                                        | `/v1/messages` (with `mcp_servers`)              | <Eligible status="no">No</Eligible>                     | <Eligible status="no">No</Eligible> | Data retained per standard policy. See [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector#data-retention).                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| [MCP tunnels](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview)                                   | `/v1/tunnels`                                    | <Eligible status="no">No</Eligible>                     | <Eligible status="no">No</Eligible> | Research preview. See [MCP tunnels security](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/security) for the data-flow boundary and subprocessor details.                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| [Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)                                   | `/v1/messages` (with `memory` tool)              | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            | Client-side memory storage where you control data retention.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| [Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages)                                | `/v1/messages`                                   | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            | Standard API calls for generating Claude responses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| [Mid-conversation system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages) | `/v1/messages` (with `role: "system"` messages)  | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            | Request-shape capability of the Messages API; mid-conversation system messages flow through the standard inference path and nothing is stored server-side after the response.                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support)                                           | `/v1/messages`                                   | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            | HIPAA eligibility applies to PDFs sent inline through the Messages API, not through the Files API.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| [Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)       | `/v1/messages` (with `code_execution` tool)      | <Eligible status="no">No</Eligible>                     | <Eligible status="no">No</Eligible> | Built on code execution containers; data retained up to 30 days. See [Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#data-retention).                                                                                                                                                                                                                                                                                                                                                                                                        |
| [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)                                     | `/v1/messages`                                   | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            | Your prompts and Claude's outputs are not stored. KV cache representations and cryptographic hashes are held in memory for the cache TTL and promptly deleted after expiry. See [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#data-retention).                                                                                                                                                                                                                                                                                                                           |
| [Search results](https://platform.claude.com/docs/en/build-with-claude/search-results)                                     | `/v1/messages` (with `search_results` source)    | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)                             | `/v1/messages`                                   | <Eligible status="qualified">Yes (qualified)</Eligible> | <Eligible>Yes</Eligible>            | Your prompts and Claude's outputs are not stored. Only the JSON schema is cached, for up to 24 hours since last use. This also covers [strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) (`strict: true` on tools), which uses the same grammar pipeline. PHI must not be included in JSON schema definitions; see [PHI handling guidelines](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#phi-handling-guidelines). See [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs#data-retention). |
| [Text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)                         | `/v1/messages` (with `text_editor` tool)         | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            | Client-side tool executed in your environment.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)                                                 | `/v1/messages` (with `thinking`)                 | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)                                     | `/v1/messages/count_tokens`                      | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            | Count tokens before sending requests.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| [Tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)                              | `/v1/messages` (with `tool_search` tool)         | <Eligible>Yes</Eligible>                                | <Eligible status="no">No</Eligible> | Server-side tool executed by Anthropic; the tool definitions in the request are searched in memory per call and nothing is stored after the response.                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| [Web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool)                                  | `/v1/messages` (with `web_fetch` tool)           | <Eligible>Yes</Eligible>                                | <Eligible status="no">No</Eligible> | Fetched web content returned in the API response. [Dynamic filtering](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool#dynamic-filtering) is not eligible for ZDR or HIPAA. Website publishers may retain request data (such as fetched URLs and request metadata) according to their own policies.                                                                                                                                                                                                                                                                                  |
| [Web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)                                | `/v1/messages` (with `web_search` tool)          | <Eligible>Yes</Eligible>                                | <Eligible>Yes</Eligible>            | Real-time web search results returned in the API response. [Dynamic filtering](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool#dynamic-filtering) is not eligible for ZDR or HIPAA.                                                                                                                                                                                                                                                                                                                                                                                                |


## Retention regardless of arrangement

Source: https://platform.claude.com/llms-full.txt#retention-regardless-of-arrangement

Even with ZDR or HIPAA arrangements in place, Anthropic may retain data where required by law or where it has been flagged by Anthropic's automated trust and safety systems. As a result, if a chat or session is flagged, Anthropic may retain inputs and outputs for up to 2 years.


## Frequently asked questions

Source: https://platform.claude.com/llms-full.txt#frequently-asked-questions-7

<AccordionGroup>
  <Accordion title="How do I know if my organization has ZDR arrangements?">
    Check your contract terms or contact your Anthropic account representative to confirm whether your organization has ZDR arrangements in place.
  </Accordion>

  <Accordion title="Can I use ZDR-eligible (qualified) features under my ZDR arrangement?">
    Yes. These features retain a minimal, documented set of technical data, not your prompts or Claude's outputs. See the [feature eligibility table](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility) legend for what "Yes (qualified)" means and [How Anthropic approaches data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#how-anthropic-approaches-data-retention) for the commitments that govern these features.
  </Accordion>

  <Accordion title="What happens if I use a feature marked &#x22;No&#x22; under ZDR?">
    Nothing blocks the request. Features marked "No" for ZDR are fundamentally stateful: the Batch API stores your jobs, the Files API stores your files, and code execution runs in persistent containers. Data for these features is retained per the feature's documented policy. Using them is a choice to step outside your ZDR arrangement for that specific data.
  </Accordion>

  <Accordion title="Can I request deletion of data from features that are not ZDR-eligible?">
    Contact your Anthropic account representative to discuss deletion options for non-ZDR features.
  </Accordion>

  <Accordion title="How does HIPAA readiness differ from ZDR?">
    ZDR prevents customer data from being stored at rest after the API response is returned. HIPAA readiness involves a broader set of privacy and security safeguards that protect PHI throughout its lifecycle, including encryption, access controls, and audit logging. Under HIPAA readiness, data can be retained with these safeguards in place rather than requiring immediate deletion. The two arrangements cover different feature sets; see the [feature eligibility table](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility).
  </Accordion>

  <Accordion title="Do I still need ZDR if I have HIPAA readiness?">
    No. HIPAA-ready API access is designed as an alternative to ZDR for organizations handling PHI. With HIPAA readiness enabled, you get access to supported API features while maintaining the privacy and security protections that HIPAA requires.
  </Accordion>

  <Accordion title="What happens if I use a non-eligible feature under HIPAA?">
    The API returns a `400` error with an `invalid_request_error` type, except for the client-side tools whose Details column in the [feature eligibility table](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility) says they are not blocked (those are accepted but remain outside HIPAA readiness). The error message identifies which features are not available. Remove those features from your request and retry. See [HIPAA error handling](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#hipaa-error-handling).
  </Accordion>

  <Accordion title="Can I use the same organization for HIPAA and non-HIPAA workloads?">
    No. HIPAA readiness is enforced at the organization level and automatically blocks non-eligible features (client-side tools noted in the table's Details column are the exception: they are not blocked, but they are still outside HIPAA readiness). Use a separate organization for workloads that do not require HIPAA readiness.
  </Accordion>

  <Accordion title="How do I request HIPAA-ready API access?">
    Eligible organizations can enable HIPAA readiness directly in [Claude Console > Settings > Privacy](https://platform.claude.com/settings/privacy) by reviewing and executing Anthropic's standard BAA; see [Getting started with HIPAA readiness](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#getting-started-with-hipaa-readiness). If your organization requires a negotiated BAA, or self-serve enablement isn't available for your organization, contact the [Anthropic sales team](https://claude.com/contact-sales).
  </Accordion>

  <Accordion title="Does this apply to Amazon Bedrock or Google Cloud?">
    No. The ZDR and HIPAA arrangements described on this page apply to the Claude API, where Anthropic is the data processor. On Bedrock and Google Cloud, the cloud provider is the data processor; refer to those platforms' data retention and compliance policies for their equivalent controls.
  </Accordion>

  <Accordion title="Is Claude Platform on AWS eligible for ZDR or HIPAA readiness?">
    Claude Platform on AWS follows the same data retention policy as the first-party Claude API. ZDR is available on request; contact your Anthropic account representative to enable it. HIPAA readiness is not available on Claude Platform on AWS. See [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) for details.
  </Accordion>

  <Accordion title="Is Claude Code eligible for ZDR?">
    Claude Code is eligible for ZDR through two paths:

    * **API keys:** Claude Code used with pay-as-you-go API keys from a Commercial organization
    * **Claude Enterprise:** Claude Code used through Claude Enterprise with ZDR enabled for the organization

    ZDR is enabled on a per-organization basis. Each new organization requires ZDR to be enabled separately by your account team. ZDR does not automatically apply to new organizations created under the same account.

    Additionally, if you have metrics logging enabled in Claude Code, productivity data (such as usage statistics) is exempted from ZDR and may be retained.

    For full details on ZDR for Claude Code on Claude Enterprise, including disabled features and how to request enablement, see the [Claude Code ZDR documentation](https://code.claude.com/docs/en/zero-data-retention).
  </Accordion>

  <Accordion title="Does Claude for Excel support ZDR?">
    No, Claude for Excel is not currently ZDR-eligible.
  </Accordion>

  <Accordion title="How do I request ZDR?">
    To request a ZDR arrangement, contact the [Anthropic sales team](https://claude.com/contact-sales).
  </Accordion>
</AccordionGroup>


## Related resources

Source: https://platform.claude.com/llms-full.txt#related-resources-2

* [Privacy Policy](https://www.anthropic.com/legal/privacy)
* [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
* [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
* [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
* [Files API reference](https://platform.claude.com/docs/en/api/files/upload)
* [Trust Center](https://trust.anthropic.com/resources)


---
title: Data residency
url: https://platform.claude.com/docs/en/manage-claude/data-residency
description: Manage where model inference runs and where data is stored with geographic controls.
---

Data residency controls let you manage where your data is processed and stored. Two independent settings govern this:

* **Inference geo:** Controls where model inference runs, on a per-request basis. Set through the `inference_geo` API parameter or as a workspace default.
* **Workspace geo:** Controls where data is stored at rest and where endpoint processing (such as image transcoding and code execution) happens. Configured at the workspace level in the [Claude Console](https://platform.claude.com).

<Note>
  [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) supports geographic pinning at the agent level: `inference_geo` on an [agent's model configuration](https://platform.claude.com/docs/en/managed-agents/agent-setup#pin-the-inference-geo) pins the geography that serves model requests for sessions running that agent, with [per-session overrides](https://platform.claude.com/docs/en/managed-agents/sessions#pin-the-inference-geo-for-a-session) at session create. Agents without a pin follow the workspace's default inference geo on each request. Managed Agents also respects the Workspace geo configured in Console, and with [self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes), tool execution and the sandbox filesystem stay on infrastructure you control; the contents of attached [memory stores](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores) remain stored by Anthropic and are copied to your sandbox for the session.
</Note>


## Inference geo

Source: https://platform.claude.com/llms-full.txt#inference-geo

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

The `inference_geo` parameter controls where model inference runs for a specific API request. Add it to any `POST /v1/messages` call.

| Value      | Description                                                                                     |
| ---------- | ----------------------------------------------------------------------------------------------- |
| `"global"` | Default. Inference may run in any available geography for optimal performance and availability. |
| `"us"`     | Inference runs only in US-based infrastructure.                                                 |

### API usage

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "inference_geo": "us",
      "messages": [{
        "role": "user",
        "content": "Summarize the key points of this document."
      }]
    }'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --inference-geo us \
    --message '{role: user, content: "Summarize the key points of this document."}' \
    --transform '{content.#(type=="text").text,usage.inference_geo}' --format yaml

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      inference_geo="us",
      messages=[
          {"role": "user", "content": "Summarize the key points of this document."}
      ],
  )

  for block in response.content:
      if block.type == "text":
          print(block.text)
  # Check where inference actually ran
  print(f"Inference geo: {response.usage.inference_geo}")

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    inference_geo: "us",
    messages: [
      {
        role: "user",
        content: "Summarize the key points of this document."
      }
    ]
  });

  const textBlock = response.content.find(
    (block): block is Anthropic.TextBlock => block.type === "text"
  );
  console.log(textBlock?.text);
  // Check where inference actually ran
  console.log(`Inference geo: ${response.usage.inference_geo}`);

csharp C#
  var client = new AnthropicClient();

  var response = await client.Messages.Create(
      new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          InferenceGeo = "us",
          Messages =
          [
              new() { Role = Role.User, Content = "Summarize the key points of this document." },
          ],
      }
  );

  foreach (var block in response.Content)
  {
      if (block.TryPickText(out var textBlock))
      {
          Console.WriteLine(textBlock.Text);
      }
  }

  // Check where inference actually ran
  Console.WriteLine($"Inference geo: {response.Usage.InferenceGeo}");

go Go
  client := anthropic.NewClient()

  message, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  	Model:        anthropic.ModelClaudeOpus5,
  	MaxTokens:    1024,
  	InferenceGeo: anthropic.String("us"),
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Summarize the key points of this document.")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  for _, block := range message.Content {
  	if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  		fmt.Println(textBlock.Text)
  	}
  }
  // Check where inference actually ran
  fmt.Printf("Inference geo: %s\n", message.Usage.InferenceGeo)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  Message response = client.messages().create(
          MessageCreateParams.builder()
                  .model(Model.CLAUDE_OPUS_5)
                  .maxTokens(1024L)
                  .inferenceGeo("us")
                  .addUserMessage("Summarize the key points of this document.")
                  .build());

  response.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  // Check where inference actually ran
  IO.println("Inference geo: " + response.usage().inferenceGeo().get());

php PHP
  $client = new Client();

  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      inferenceGeo: 'us',
      messages: [
          ['role' => 'user', 'content' => 'Summarize the key points of this document.'],
      ],
  );

  foreach ($response->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, PHP_EOL;
      }
  }
  // Check where inference actually ran
  echo "Inference geo: {$response->usage->inferenceGeo}\n";

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    inference_geo: "us",
    messages: [
      {role: "user", content: "Summarize the key points of this document."}
    ]
  )

  response.content.each do |block|
    puts block.text if block.type == :text
  end
  # Check where inference actually ran
  puts "Inference geo: #{response.usage.inference_geo}"

json Output
{
  "usage": {
    "input_tokens": 25,
    "output_tokens": 150,
    "inference_geo": "us"
  }
}
```

### Model availability

The `inference_geo` parameter is supported on Claude 4.6 and later models. Requests with `inference_geo` on Claude Opus 4.5, Claude Sonnet 4.5, Claude Haiku 4.5, or earlier models return a 400 error.

<Note>
  The `inference_geo` parameter is available on the Claude API (first-party) and [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws). On Amazon Bedrock and Google Cloud, the inference region is determined by the endpoint URL or inference profile, so `inference_geo` is not applicable. On [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), `inference_geo` is likewise not applicable: deployments hosted on Azure can instead use the US Data Zone Standard deployment type, which keeps inference within the United States. The `inference_geo` parameter is also not available through the [OpenAI SDK compatibility endpoint](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk).
</Note>

### Workspace-level restrictions

Workspace settings also support restricting which inference geos are available:

* **`allowed_inference_geos`:** Restricts which geos a workspace can use. If a request specifies an `inference_geo` not in this list, the API returns an error.
* **`default_inference_geo`:** Sets the fallback geo when `inference_geo` is omitted from a request. Individual requests can override this by setting `inference_geo` explicitly.

These settings can be configured through the Console or the [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api) under the `data_residency` field.


## Workspace geo

Source: https://platform.claude.com/llms-full.txt#workspace-geo

Workspace geo is set when you create a workspace and can't be changed afterward. Currently, `"us"` is the only available workspace geo.

To set workspace geo, create a new workspace in the [Console](https://platform.claude.com):

1. Go to **Settings** > **Workspaces**.
2. Create a new workspace.
3. Select the workspace geo.

<Note>
  **Claude Platform on AWS:** Workspace geo is not configurable. Claude Managed Agents sessions on this platform run with an effective Workspace geo of `"us"`, which is currently the only available workspace geo. See [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) for data residency considerations specific to that platform.
</Note>


## Pricing

Source: https://platform.claude.com/llms-full.txt#pricing-9

Data residency pricing varies by model generation:

* **Claude 4.6 and later models:** US-only inference (`inference_geo: "us"`) is priced at 1.1x the standard rate across all token pricing categories (input tokens, output tokens, cache writes, and cache reads).
* **Global routing** (`inference_geo: "global"`): Standard pricing applies.
* **Older models:** Don't support `inference_geo` (see [Model availability](https://platform.claude.com/docs/en/manage-claude/data-residency#model-availability)); standard pricing applies. Requests that include the parameter return a 400 error.

This pricing applies to the Claude API (first-party) and Claude Platform on AWS. On Claude in Microsoft Foundry, the same 1.1x multiplier applies to deployments hosted on Azure that use the US Data Zone Standard deployment type. Partner-operated platforms (Bedrock and Google Cloud) have their own regional pricing. See [Data residency pricing](https://platform.claude.com/docs/en/about-claude/pricing#data-residency-pricing) for details.

The same multiplier applies to [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview): when an agent's [model configuration](https://platform.claude.com/docs/en/managed-agents/agent-setup) pins `inference_geo` to `"us"`, model requests in sessions running that agent are priced at 1.1x the standard rate.

<Note>
  If you have a [Priority Tier](https://platform.claude.com/docs/en/api/service-tiers) commitment, the 1.1x multiplier for US-only inference also affects how tokens are counted against your Priority Tier capacity. Each token consumed with `inference_geo: "us"` draws down 1.1 tokens from your committed TPM, consistent with how other pricing multipliers (such as prompt caching) affect burndown rates.
</Note>


## Batch API support

Source: https://platform.claude.com/llms-full.txt#batch-api-support

The `inference_geo` parameter is supported on the [Batch API](https://platform.claude.com/docs/en/build-with-claude/batch-processing). Each request in a batch can specify its own `inference_geo` value.


## Migration from legacy opt-outs

Source: https://platform.claude.com/llms-full.txt#migration-from-legacy-opt-outs

If your organization previously opted out of global routing to keep inference in the US, your workspace has been automatically configured with `allowed_inference_geos: ["us"]` and `default_inference_geo: "us"`. No code changes are required. Your existing data residency requirements continue to be enforced through the new geo controls.

### What changed

The legacy opt-out was an organization-level setting that restricted all requests to US-based infrastructure. The new data residency controls replace this with two mechanisms:

* **Per-request control:** The `inference_geo` parameter lets you specify `"us"` or `"global"` on each API call, giving you request-level flexibility.
* **Workspace controls:** The `default_inference_geo` and `allowed_inference_geos` settings in the Console let you enforce geo policies across all keys in a workspace.

### What happened to your workspace

Your workspace was migrated automatically:

| Legacy setting                   | New equivalent                                                  |
| -------------------------------- | --------------------------------------------------------------- |
| Global routing opt-out (US only) | `allowed_inference_geos: ["us"]`, `default_inference_geo: "us"` |

All API requests using keys from your workspace continue to run on US-based infrastructure. No action is needed to maintain your current behavior.

### If you want to use global routing

If your data residency requirements have changed and you want to take advantage of global routing for better performance and availability, update your workspace's inference geo settings to include `"global"` in the allowed geos and set `default_inference_geo` to `"global"`. See [Workspace-level restrictions](https://platform.claude.com/docs/en/manage-claude/data-residency#workspace-level-restrictions) for details.

### Pricing impact

Legacy models are unaffected by this migration. For current pricing on newer models, see [Pricing](https://platform.claude.com/docs/en/manage-claude/data-residency#pricing).


## Current limitations

Source: https://platform.claude.com/llms-full.txt#current-limitations-2

* **Shared rate limits:** Rate limits are shared across all geos.
* **Inference geo:** Only `"us"` and `"global"` are available.
* **Workspace geo:** Only `"us"` is currently available. Workspace geo can't be changed after workspace creation.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-89

<CardGroup>
  <Card title="Pricing" icon="dollar-sign" href="https://platform.claude.com/docs/en/about-claude/pricing#data-residency-pricing">
    View data residency pricing details.
  </Card>

  <Card title="Workspaces" icon="building" href="https://platform.claude.com/docs/en/manage-claude/workspaces">
    Learn about workspace configuration.
  </Card>

  <Card title="Usage and Cost API" icon="chart" href="https://platform.claude.com/docs/en/manage-claude/usage-cost-api">
    Track usage and costs by data residency.
  </Card>
</CardGroup>


### Data & compliance > Encryption keys

---
title: Configure AWS KMS for CMEK
url: https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms
description: Use AWS KMS to provide an encryption key for your organization.
---

```bash Configure with the /claude-api skill in Claude Code
claude "/claude-api help me configure a customer-managed encryption key with AWS KMS"
```

This guide walks through configuring an [AWS KMS](https://aws.amazon.com/kms/) key as a [customer-managed encryption key (CMEK)](https://platform.claude.com/docs/en/manage-claude/cmek) for your Anthropic organization.

<Warning>
  Enabling CMEK is permanent. If your KMS key is deleted or disabled, Anthropic cannot recover the data encrypted under it. Review the [warnings and limitations](https://platform.claude.com/docs/en/manage-claude/cmek) before you begin.
</Warning>

<Note>
  **Claude Platform on AWS:** On [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), your key policy grants access to an AWS service principal instead of Anthropic's IAM role, there is no separate validation step, and you register and attach the key in the Claude Console. Follow [Set up CMEK on Claude Platform on AWS](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms#claude-platform-on-aws) on this page instead of the steps in the next sections.
</Note>


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-18

* An AWS account with permissions to create KMS keys and set key policies (`kms:CreateKey` and `kms:PutKeyPolicy`).
* An Anthropic Admin API key for your organization.
* The [AWS CLI](https://aws.amazon.com/cli/) installed and authenticated.


## Amazon Resource Name (ARN) for Anthropic

Source: https://platform.claude.com/llms-full.txt#amazon-resource-name-arn-for-anthropic

To have Anthropic use your encryption key, you must give Anthropic's IAM role a KMS key it can use for encrypting data. The ARN for Anthropic CMEK is:

```text wrap
arn:aws:iam::915198916910:role/anthropic-cmek-client-us
```

<Warning>
  Use only this published ARN. Never trust an identifier provided over email, chat, or any onboarding channel.
</Warning>


## Encryption key setup

Source: https://platform.claude.com/llms-full.txt#encryption-key-setup

<Steps>
  <Step title="Create the KMS key with a cross-account key policy">
    The key policy grants Anthropic's IAM role cross-account access. Three statements are required:

    1. **Account root admin:** the standard KMS pattern. Your account retains full admin control.
    2. **Anthropic encrypt and decrypt:** the `kms:Encrypt` and `kms:Decrypt` actions, which Anthropic uses to encrypt and decrypt the data keys that protect your workspace data (envelope encryption).
    3. **Anthropic describe:** the metadata read Anthropic performs at startup. It is granted separately because `DescribeKey` has no `EncryptionContext` parameter, so an `EncryptionContext` condition on this action would always deny.

Capture `KeyMetadata.Arn` from the output. You need it when you register the key in the next step.

    The `EncryptionContext` condition is recommended but optional. Anthropic always includes your workspace's compartment ID in the encryption context, so ciphertext is cryptographically bound to that compartment regardless. Adding the condition provides defense-in-depth at the IAM layer. To start without it, omit the `Condition` block from the `AllowAnthropicCMEKCrypto` statement and add it later with `kms:PutKeyPolicy`.

    <Note>
      **Finding your compartment ID:** Where to find your compartment ID differs between Claude Platform and Claude Enterprise. See the **Claude Platform** and **Claude Enterprise** tabs under **Register the key with Anthropic**.
    </Note>

    You can also create the key from the AWS Console. Choose a symmetric key with the encrypt and decrypt key usage, a single-region key, and KMS key material origin. The Create-key wizard commits a key policy at its **Review** step: If you add Anthropic's account ID `915198916910` under key usage permissions there, the generated policy grants the whole Anthropic account broader actions (such as `kms:ReEncrypt*` and `kms:GenerateDataKey*`) with no `EncryptionContext` condition, and validation would still succeed against it. To avoid leaving an over-permissive key, finish the wizard with administrative permissions only, then open the key's **Key policy** tab and replace the JSON with the role-scoped policy shown earlier (the three statements scoped to the `anthropic-cmek-client-us` role, with the `EncryptionContext` condition).

    <Frame caption="Configure key: symmetric, encrypt and decrypt, single-region key.">
      ![AWS KMS Create key wizard on the Configure key step, with Symmetric key type, Encrypt and decrypt key usage, and Single-Region key selected.](https://platform.claude.com/docs/images/cmek/aws-configure-key.png)
    </Frame>

    <Frame caption="Add an alias and description for the key.">
      ![AWS KMS Add labels step with an alias of anthropic-cmek and a description of Anthropic CMEK.](https://platform.claude.com/docs/images/cmek/aws-add-labels.png)
    </Frame>

    <Frame caption="Define key administrative permissions (optional). Your account retains full admin control.">
      ![AWS KMS Define key administrative permissions step listing IAM roles that can administer the key.](https://platform.claude.com/docs/images/cmek/aws-admin-permissions.png)
    </Frame>

    <Frame caption="Do not add Anthropic's account ID here. This wizard step produces an over-permissive policy. Leave usage permissions empty and edit the Key policy JSON after creation (see the preceding key policy).">
      ![AWS KMS Define key usage permissions step with Anthropic's account ID entered under Other AWS accounts.](https://platform.claude.com/docs/images/cmek/aws-usage-permissions.png)
    </Frame>
  </Step>
</Steps>


## Register the key with Anthropic

Source: https://platform.claude.com/llms-full.txt#register-the-key-with-anthropic

How you register the key depends on which product you use.

<Tabs>
  <Tab title="Claude Platform">
    <Note>
      **Claude Platform on AWS:** The principal, key policy, and registration flow differ, and there is no separate validation step. Follow [Set up CMEK on Claude Platform on AWS](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms#claude-platform-on-aws) instead of this tab.
    </Note>

    <Note>
      **Finding your compartment ID:** Each workspace has a compartment ID that scopes its CMEK data. Find it in the Claude Console under **Workspace > Security**, under **Encryption key** (the **Compartment ID** field), or read the `compartment_id` field returned by the [Get Workspace](https://platform.claude.com/docs/en/api/admin-api/workspaces/get-workspace) endpoint. Substitute that value for `<compartment-uuid>` in the preceding key policy.

      Key validation always sends the all-zeros compartment UUID (`00000000-0000-0000-0000-000000000000`) as the encryption context, because validation runs before the key is attached to any workspace. Live traffic sends the compartment ID of each attached workspace.

      Any `EncryptionContext` condition must allow the all-zeros value plus the compartment ID of every workspace the key is attached to. Validation also runs again whenever key setup is re-run, so keep the all-zeros entry in place permanently.

      To attach the key to an additional workspace, add that workspace's compartment ID to the condition with `kms:PutKeyPolicy` before attaching.
    </Note>

    <Steps>
      <Step title="Register the key with Anthropic">
        Create an external key configuration through the Admin API.

The response contains the external key ID:

</Step>

      <Step title="Validate the key">
        Trigger an encrypt and decrypt round-trip against your key.

A successful response looks like this:

If validation fails, common causes are:

        * **Encryption context mismatch:** Validation fails while data traffic works (or the reverse) with an opaque `AccessDeniedException` when a `kms:EncryptionContext:anthropic:compartment_uuid` condition allows only one of the two values Anthropic sends. Validation sends the all-zeros UUID (`00000000-0000-0000-0000-000000000000`); live traffic sends the attached workspace's compartment ID. Confirm the condition lists both. To rule the condition out entirely, temporarily remove the `Condition` block from the `AllowAnthropicCMEKCrypto` statement and re-validate.
        * **Resource control policies (RCPs):** If your AWS organization has an RCP that denies KMS operations when `aws:PrincipalOrgID` does not match your org, it blocks Anthropic's cross-account role. The RCP needs a carve-out for this key or for Anthropic's role ARN. Service control policies do not apply here, because they do not evaluate for external principals calling through resource-based policies.
        * **Access granted through IAM instead of the key policy:** Cross-account KMS access must be granted in the key policy itself, not through an IAM policy in your account. Check with `aws kms get-key-policy --key-id <id> --policy-name default`.
        * **Region mismatch:** Confirm the key's region is one Anthropic operates in for the geo tier you configured.
      </Step>

      <Step title="Attach the key to a workspace">
        Once the key is validated, attach it to a new workspace before you send any requests to that workspace. For a workspace that already receives requests, the key can take [up to a day to take effect](https://platform.claude.com/docs/en/manage-claude/cmek#how-it-works).

</Step>
    </Steps>
  </Tab>

  <Tab title="Claude Enterprise">
    In [claude.ai > Organization settings > Data and privacy](https://claude.ai/admin-settings/data-privacy-controls), open **Encryption keys**, then click **Add key**. Choose **AWS** and click **Continue**, then paste the Key ARN from the previous step and click **Add**. Anthropic validates the key with an encrypt and decrypt round-trip. Once it shows as verified, your organization is CMEK-protected from that point forward.

    The key details step of this flow displays your organization's **Compartment ID** with a copy button. Substitute that value for `<compartment-uuid>` in the key policy (see the Create the KMS key step under Encryption key setup); you can open the flow to copy the ID before you create the key. After setup, the ID remains visible on the key under **Encryption keys**.

    On Claude Enterprise, CMEK applies to the whole organization, so there is no separate workspace attach step, and an organization can have only one key.
  </Tab>
</Tabs>


## Set up CMEK on Claude Platform on AWS

Source: https://platform.claude.com/llms-full.txt#set-up-cmek-on-claude-platform-on-aws

On [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), CMEK uses AWS KMS keys only, and setup differs from the preceding sections in these ways:

* **Principal:** Your key policy grants access to the AWS service principal `aws-external-anthropic.amazonaws.com`. Anthropic's IAM role and account ID are not used, so the [ARN for Anthropic](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms#amazon-resource-name-arn-for-anthropic) does not apply.
* **Key requirements:** The key must be a symmetric KMS key with encrypt and decrypt usage, single-region, and in the same AWS account and region as the workspace you attach it to. Cross-account keys are not supported: the key must be in the AWS account that hosts your organization. Multi-region keys (key IDs that begin with `mrk-`) and alias ARNs are rejected when you register the key; use the key ARN.
* **No separate validation step:** Apart from those checks on the key ARN at registration, the key is validated when you attach it to a workspace. The attach call performs an encrypt/decrypt round against the key with that workspace's compartment ID as the encryption context, so a key policy problem surfaces at attach time rather than at registration. Unlike the Claude Platform policy earlier on this page, an `EncryptionContext` condition therefore needs no all-zeros entry.
* **Where you manage keys:** Register and attach keys in the Claude Console, signed in through AWS with the Admin role. The external key endpoints are also available on Claude Platform on AWS, authorized through [IAM actions](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#encryption-keys); there, a key is identified by its KMS key ARN rather than an `ekey_` ID.

<Warning>
  Use only this published service principal name. Never trust an identifier provided over email, chat, or any onboarding channel.
</Warning>

### Prerequisites

* The AWS account that hosts your Claude Platform on AWS organization, with permissions to create KMS keys and set key policies (`kms:CreateKey` and `kms:PutKeyPolicy`).
* The **Admin** role in the Claude Console for Claude Platform on AWS. See [Using the Claude Console](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#using-the-claude-console).
* For the IAM principal you sign in to the Claude Console with: besides `aws-external-anthropic:AssumeConsole`, the [IAM actions](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#encryption-keys) for the operations you perform there, because the Encryption keys page and key attachment go through the AWS gateway. Registering a key is `RegisterKey` (with `ListKeys` and `GetKey` to view registrations), and attaching one is `UpdateWorkspace` or `CreateWorkspace`. The external key actions (and `CreateWorkspace`) are account-scoped, so grant them on `Resource: "*"`; a policy limited to workspace ARNs does not include them.
* For the IAM principal that attaches the key to a workspace (the identity you signed in to the Claude Console with): `kms:DescribeKey`, `kms:Encrypt`, and `kms:Decrypt` on the key. Your principal's access to the key is checked when you attach it, in addition to the service principal's.
* Optional, for the key picker in the Claude Console: `kms:ListKeys` and `kms:DescribeKey` for the principal you sign in with. Without them, paste the key ARN instead.

### Create the KMS key

The key policy has three statements: your account's root admin statement; a statement that lets the Claude Platform on AWS service principal encrypt, decrypt, and generate data keys; and a separate statement for `kms:DescribeKey`. Both service-principal statements carry a recommended `aws:SourceArn` condition: the service calls your key on behalf of a specific workspace and passes that [workspace's ARN](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#service-details) as the source ARN, so the pattern shown limits the grant to workspaces in your own AWS account. `DescribeKey` is granted separately because it has no `EncryptionContext` parameter, so an `EncryptionContext` condition on that action would always deny.

If you plan to use the optional `EncryptionContext` condition shown here, create the workspace first (without a key) and copy its compartment ID from the Claude Console under **Workspace > Security**, under **Encryption key** (the **Compartment ID** field), or from the `compartment_id` field returned by the [Get Workspace](https://platform.claude.com/docs/en/api/admin-api/workspaces/get-workspace) endpoint. Substitute it for `<compartment-uuid>`. Otherwise, delete the `StringEquals` entry from that statement's `Condition` block and keep the `ArnLike` entry.

Capture `KeyMetadata.Arn` from the output. You need it when you register the key.

Both conditions are optional hardening, and they compose. The `aws:SourceArn` condition can be written before any workspace exists; to pin the key to particular workspaces instead of your whole account, list their full workspace ARNs in place of the wildcard pattern, and to start without it, delete the `ArnLike` entry from both service-principal statements (removing a `Condition` block that this leaves empty). The `EncryptionContext` condition is also optional. Every encrypt, decrypt, and data-key call made for a workspace, including the attach-time check, carries that workspace's compartment ID as `anthropic:compartment_uuid`, so the condition lists the compartment ID of each workspace you attach the key to and needs no all-zeros entry. Adding it binds the key to the workspaces you list at the IAM layer as well. Because a compartment ID exists only once its workspace exists, the order is: create the workspace, put its compartment ID in the condition (at key creation, or later with `kms:PutKeyPolicy`), then attach the key. Before attaching the key to each additional workspace, add that workspace's compartment ID the same way. To start without it, delete the `StringEquals` entry from the `AllowClaudePlatformOnAWSCrypto` statement's `Condition` block; if you add it later, include the compartment ID of every workspace the key is already attached to.

You can also create the key from the AWS Console: choose a symmetric key with the encrypt and decrypt key usage, a single-region key, and KMS key material origin, in the workspace's region. Leave key usage permissions empty in the Create-key wizard, then open the key's **Key policy** tab and replace the JSON with the policy shown here.

### Register and attach the key

<Steps>
  <Step title="Register the key">
    In the Claude Console, open **Settings > Encryption keys** and click **Add key**. Enter a display name, then choose the key from the key picker or choose **Enter ARN manually** and paste the key ARN, and click **Add**. The key must be in the AWS account that hosts your organization; cross-account keys are not supported. The picker lists the enabled, customer-managed, symmetric, single-region keys in your account in one of your organization's regions; for a key the picker doesn't list, enter the ARN. It lists keys only if the principal you signed in with can call `kms:ListKeys` and `kms:DescribeKey`.
  </Step>

  <Step title="Attach the key to a workspace">
    Attach the key to a new workspace before you send any requests to that workspace. For a workspace that already receives requests, the key can take [up to a day to take effect](https://platform.claude.com/docs/en/manage-claude/cmek#how-it-works). In the Claude Console, open the workspace and, under **Security**, select the key in **Encryption key**, save, and confirm. You can also select a key when you create a workspace in the Claude Console, but only if your key policy does not yet name specific workspaces (no `EncryptionContext` condition, and the account-wide `aws:SourceArn` pattern rather than individual workspace ARNs), because the workspace's ID and compartment ID are assigned at creation. Once attached, a workspace's key can't be changed.

    This is when the key is validated: the attach call checks your principal's access to the key and performs an encrypt/decrypt round against it with the workspace's compartment ID as the encryption context, so a problem with either the key policy or your principal's permissions surfaces as an error on that call. If the attach fails with a KMS access error, check the following:

    * The key policy names the `aws-external-anthropic.amazonaws.com` service principal and grants `kms:Encrypt`, `kms:Decrypt`, and `kms:GenerateDataKey`, plus `kms:DescribeKey` in a separate statement that has no `EncryptionContext` condition.
    * The `aws:SourceArn` condition matches this workspace's ARN (your account ID, and the workspace if you listed specific ARNs), and any `EncryptionContext` condition includes this workspace's compartment ID.
    * The key is enabled, single-region, and in the same AWS account and region as the workspace.
    * The principal you are signed in as has `kms:DescribeKey`, `kms:Encrypt`, and `kms:Decrypt` on the key.
    * No service control policy or resource control policy in your AWS organization prevents the service principal or your principal from using the key.
    * If the policy looks right and the attach still fails, find the denied `kms:` event in CloudTrail in the key's account (it shows the calling principal and, for cryptographic calls, the encryption context), then retry with the `aws:SourceArn` condition temporarily removed to tell a source-ARN mismatch apart from an encryption-context mismatch. Once the key is attached, whether on that retry or after you correct the encryption context, restore the `ArnLike` entry on both service-principal statements with `kms:PutKeyPolicy`, using the account-wide `aws:SourceArn` pattern or the ARN of every workspace the key is attached to.
  </Step>
</Steps>


## Terraform

Source: https://platform.claude.com/llms-full.txt#terraform

For infrastructure-as-code deployments, the same steps map to the `aws` provider with the `aws_kms_key` and `aws_kms_alias` resources.


---
title: Configure Azure Key Vault for CMEK
url: https://platform.claude.com/docs/en/manage-claude/cmek-azure-key-vault
description: Use Azure Key Vault to provide an encryption key for your organization.
---

```bash Configure with the /claude-api skill in Claude Code
claude "/claude-api help me configure a customer-managed encryption key with Azure Key Vault"
```

This guide walks through configuring an Azure Key Vault key as a [customer-managed encryption key (CMEK)](https://platform.claude.com/docs/en/manage-claude/cmek) for your Anthropic organization.

<Warning>
  Enabling CMEK is permanent. If your Key Vault key is deleted or disabled, Anthropic cannot recover the data encrypted under it. Review the [warnings and limitations](https://platform.claude.com/docs/en/manage-claude/cmek) before you start.
</Warning>


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-19

* An Azure Key Vault with **RBAC authorization enabled** (`enableRbacAuthorization: true`) and **public network access allowed**. Anthropic calls your vault over the public data-plane endpoint; private endpoints are not supported.
* **Purge protection enabled** (`enablePurgeProtection: true`) on the vault. Without it, a deleted key can be permanently purged during the soft-delete retention window, causing irreversible loss of your CMEK-protected data. Purge protection cannot be disabled once enabled.
* Permissions to create keys in the vault and to assign RBAC roles on it.
* Permissions to create service principals in your Entra tenant (`Application Administrator`, `Cloud Application Administrator`, or an equivalent custom role).
* An Anthropic Admin API key for your organization.
* The [`az` CLI](https://learn.microsoft.com/en-us/cli/azure/?view=azure-cli-latest) installed and authenticated.
* **Diagnostic Settings** configured on the vault to route the `AuditEvent` log category to Log Analytics, a storage account, or an event hub. Azure Key Vault does not emit data-plane audit logs (such as `KeyWrap`, `KeyUnwrap`, and `KeyGet`) by default, so without this you get no audit trail for Anthropic's key operations.


## Anthropic app information

Source: https://platform.claude.com/llms-full.txt#anthropic-app-information

To have Anthropic use your encryption key, you must configure an Anthropic multitenant application ID and display name. Those values are:

| Field                          | Value                                  |
| ------------------------------ | -------------------------------------- |
| Multitenant app client ID (US) | `8635ae1a-3e5d-44e8-a4ed-e0f614466f87` |
| App display name               | `anthropic-cmek-client-us`             |

<Warning>
  Use only this published client ID and display name. Never trust an identifier provided over email, chat, or any onboarding channel.
</Warning>


## Encryption key setup

Source: https://platform.claude.com/llms-full.txt#encryption-key-setup-2

<Steps>
  <Step title="Consent to the Anthropic multitenant application">
    This creates a service principal in your Entra tenant for Anthropic's CMEK client application. The application requests no Microsoft Graph permissions; it exists solely as a federation target for Key Vault data-plane access.

From the output, capture the `id` field. This is the service principal's object ID in your tenant, which you use when you assign the RBAC role.

If the service principal already exists in your tenant (from a prior attempt or another integration), `az ad sp create` exits with an "already exists" error. Fetch its object ID instead:

This step has no Portal equivalent. If you do not have the Azure CLI installed locally, open Cloud Shell from the Portal's top navigation bar. After the command succeeds, you can find the service principal's object ID in **Microsoft Entra ID > Enterprise applications** by clearing the default application-type filter and searching for `anthropic-cmek-client-us`.

    <Frame caption="Find the service principal's Object ID on its Entra enterprise application overview.">
      ![Microsoft Entra enterprise application overview for anthropic-cmek-client-us, showing its Application ID and Object ID.](https://platform.claude.com/docs/images/cmek/azure-service-principal.png)
    </Frame>
  </Step>

  <Step title="Create an RSA key in your vault">
    Azure Key Vault does not support symmetric key wrapping, so the key must be RSA (3072-bit or larger) with `wrapKey` and `unwrapKey` in its allowed operations.

For HSM-backed keys, use `--kty RSA-HSM` (requires a Premium-SKU vault). Software-protected RSA keys are acceptable for this integration.

    From the Portal, open your Key Vault, select **Keys**, then **Generate/Import**. Set the key type to RSA and the size to 3072 or larger. To restrict the key to wrap and unwrap only, open the key version, scroll to **Permitted operations**, and uncheck everything except **Wrap Key** and **Unwrap Key**.

    <Frame caption="Create an RSA key sized 3072 or larger.">
      ![Azure Key Vault Create a key page with the Generate option, RSA key type, and 3072 RSA key size selected.](https://platform.claude.com/docs/images/cmek/azure-create-key.png)
    </Frame>

    <Frame caption="Restrict permitted operations to Wrap Key and Unwrap Key.">
      ![Azure Key Vault key version with Permitted operations limited to Wrap Key and Unwrap Key.](https://platform.claude.com/docs/images/cmek/azure-permitted-operations.png)
    </Frame>
  </Step>

  <Step title="Grant the Anthropic service principal access to your key">
    Assign the `Key Vault Crypto User` role to the service principal from the first step, scoped to the **individual key** rather than the whole vault.

The built-in `Key Vault Crypto User` role grants key cryptographic operations (encrypt, decrypt, wrap, unwrap, sign, verify) plus key read on its assigned scope. The `--ops wrapKey unwrapKey` restriction you set on the key in the previous step further narrows which of those operations can succeed against this key, so in practice Anthropic can only wrap and unwrap.

    From the Portal, open the **key** (not the vault), select its **Access control (IAM)** tab, click **Add > Add role assignment**, select **Key Vault Crypto User**, and assign it to the `anthropic-cmek-client-us` service principal.

    <Note>
      **Dedicated vault alternative:** Microsoft recommends a dedicated vault per application with roles assigned at the vault scope. If you provision a vault that holds only this Anthropic CMEK key, you can assign the role at the vault scope instead and the effect is identical. Scope to the individual key when the key lives in a shared vault.
    </Note>

    <Frame caption="Assign Key Vault Crypto User to the Anthropic service principal, scoped to the key.">
      ![Key Vault IAM role assignments showing anthropic-cmek-client-us assigned the Key Vault Crypto User role.](https://platform.claude.com/docs/images/cmek/azure-role-assignment.png)
    </Frame>
  </Step>

  <Step title="Verify your vault configuration">

Confirm that:

    * `rbac` is `true`.
    * `purge` is `true`. If it is `false` or `null`, enable purge protection on the vault before proceeding. Without it, a soft-deleted key can be permanently purged during the retention window, making your CMEK-protected data unrecoverable.
    * `pub` is `"Enabled"`. If it is `"Disabled"`, Anthropic cannot reach the vault over its public data-plane endpoint and validation fails.
    * `net` is `"Allow"`, or, if it is `"Deny"`, that `ipRules` include Anthropic's egress ranges (contact Anthropic for the current list).
    * `uri` is the vault URI you use when you register the key.
    * `tenantId` is the tenant that governs the vault. Use this value as `tenant_id` when you register the key, not the tenant of your currently-active subscription (the two can differ in cross-tenant setups).
  </Step>
</Steps>


## Register the key with Anthropic

Source: https://platform.claude.com/llms-full.txt#register-the-key-with-anthropic-2

How you register the key depends on which product you use.

<Tabs>
  <Tab title="Claude Platform">
    <Steps>
      <Step title="Register the key with Anthropic">
        Create an external key configuration through the Admin API.

The response contains the external key ID:

</Step>

      <Step title="Validate the key">
        Trigger an encrypt and decrypt round-trip against your key. This confirms that Anthropic can authenticate to your tenant and perform wrap and unwrap operations.

A successful response looks like this:

If validation fails, the `error` field describes the problem. Common causes are:

        * **RBAC propagation delay:** role assignments can take a few minutes to take effect. Wait and retry.
        * **Network ACLs blocking Anthropic:** confirm public network access and `ipRules` as described in the verification step.
        * **Conditional access policies on workload identities:** if your tenant has conditional access policies that target service principals, exclude the Anthropic service principal or add Anthropic's egress ranges to the policy's named locations.
      </Step>

      <Step title="Attach the key to a workspace">
        Once the key is validated, attach it to a new workspace before you send any requests to that workspace. For a workspace that already receives requests, the key can take [up to a day to take effect](https://platform.claude.com/docs/en/manage-claude/cmek#how-it-works).

</Step>
    </Steps>
  </Tab>

  <Tab title="Claude Enterprise">
    In [claude.ai > Organization settings > Data and privacy](https://claude.ai/admin-settings/data-privacy-controls), open **Encryption keys**, then click **Add key**. Choose **Azure**, enter the vault URI, key name, and tenant ID from the verification step, and click **Continue**. Anthropic validates the key with an encrypt and decrypt round-trip. Once it shows as verified, your organization is CMEK-protected from that point forward.

    On Claude Enterprise, CMEK applies to the whole organization, so there is no separate workspace attach step, and an organization can have only one key.
  </Tab>
</Tabs>


## Terraform

Source: https://platform.claude.com/llms-full.txt#terraform-2

For infrastructure-as-code deployments, the same steps map to the `azurerm` and `azuread` providers.


---
title: Configure Google Cloud KMS for CMEK
url: https://platform.claude.com/docs/en/manage-claude/cmek-google-cloud-kms
description: Use Google Cloud KMS to provide an encryption key for your organization.
---

```bash Configure with the /claude-api skill in Claude Code
claude "/claude-api help me configure a customer-managed encryption key with Google Cloud KMS"
```

This guide walks through configuring a Google Cloud KMS key as a [customer-managed encryption key (CMEK)](https://platform.claude.com/docs/en/manage-claude/cmek) for your Anthropic organization.

<Warning>
  Enabling CMEK is permanent. If your KMS key is deleted or disabled, Anthropic cannot recover the data encrypted under it. Review the [warnings and limitations](https://platform.claude.com/docs/en/manage-claude/cmek) before you begin.
</Warning>


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-20

* A Google Cloud project with billing enabled.
* The Cloud KMS API enabled (`cloudkms.googleapis.com`).
* Permissions to create KMS key rings and keys, and to set IAM policy on them (`roles/cloudkms.admin` or equivalent).
* An Anthropic Admin API key for your organization.
* The [`gcloud` CLI](https://cloud.google.com/cli) installed and authenticated.
* Cloud KMS **Data Access audit logs** enabled for the project (IAM & Admin > Audit Logs > Cloud Key Management Service, with `DATA_READ` and `DATA_WRITE`). These are off by default; without them, Anthropic's encrypt and decrypt operations produce no entries in Cloud Logging.


## Anthropic service account email

Source: https://platform.claude.com/llms-full.txt#anthropic-service-account-email

To have Anthropic use your encryption key, you must give Anthropic's service account a key it can use for encrypting data. The service account email for Anthropic CMEK is:

```text wrap
anthropic-cmek-client-us@gcp-anthropic-cmek-clients.iam.gserviceaccount.com
```

<Warning>
  Use only this published service account email. Never trust an identifier provided over email, chat, or any onboarding channel.
</Warning>

<Note>
  **Domain restricted sharing:** If your project is under a Google Cloud organization that enforces `constraints/iam.allowedPolicyMemberDomains`, the following IAM bindings are rejected because the Anthropic service account is outside your organization. You need either a project-level carve-out on that constraint, or to add Anthropic's Cloud Identity customer ID (format `C0xxxxxxxx`) to the allowed list. Contact Anthropic for the customer ID if needed.
</Note>


## Encryption key setup

Source: https://platform.claude.com/llms-full.txt#encryption-key-setup-3

<Steps>
  <Step title="Create or choose a key ring">
    Skip this step if you already have a key ring to reuse. Key rings are regional. Choose a single-region US location such as `us-east5` that matches the Anthropic geography you are configuring. Multi-region locations like `us` and `global` are not supported.

</Step>

  <Step title="Create the crypto key">
    Create a symmetric key with the `ENCRYPT_DECRYPT` purpose. Anthropic strongly recommends HSM protection: Cloud KMS HSM keys are FIPS 140-2 Level 3 validated, and the cost delta over software keys is small.

For software protection instead, omit `--protection-level=hsm`. Nothing else in this guide changes.

    You can also create the key from the Google Cloud Console. Open the key ring, click **Create key**, select **Generated key**, set the purpose and algorithm to symmetric encrypt and decrypt, and choose **HSM** under protection level.

    <Frame caption="Create an HSM-protected symmetric encrypt/decrypt key.">
      ![Google Cloud KMS Create key page with HSM protection level and a Symmetric encrypt/decrypt purpose.](https://platform.claude.com/docs/images/cmek/gcp-create-key.png)
    </Frame>
  </Step>

  <Step title="Grant Anthropic's service account access to the key">
    Two key-level IAM bindings are required. Both are scoped to the single crypto key, not project-wide or keyring-wide.

    Encrypt and decrypt, which Anthropic uses to encrypt and decrypt the data keys that protect your workspace data (envelope encryption):

Viewer, for the metadata read (`cryptoKeys.get`) Anthropic performs at startup to validate the key's purpose and algorithm:

From the Console, select the key, open the **Permissions** panel, click **Grant access**, and add the service account with both the Cloud KMS CryptoKey Encrypter/Decrypter and Cloud KMS Viewer roles. Make sure you are on the key's permissions page, not the key ring or project, so the grant is scoped to this key only.

    <Frame caption="Grant the Anthropic service account both roles, scoped to the key.">
      ![Grant access dialog with the Anthropic service account assigned Cloud KMS CryptoKey Encrypter/Decrypter and Viewer roles.](https://platform.claude.com/docs/images/cmek/gcp-grant-access.png)
    </Frame>
  </Step>

  <Step title="Note the full key resource name">
    You pass this to Anthropic when you register the key. The format is:

    ```text wrap
    projects/<your-project-id>/locations/<region>/keyRings/<your-keyring-name>/cryptoKeys/<your-key-name>

bash
    gcloud kms keys describe <your-key-name> \
      --project=<your-project-id> \
      --location=<region> \
      --keyring=<your-keyring-name> \
      --format="value(name)"
    ```

    From the Console, open the key's details page and click **Copy resource name**.

    <Frame caption="Copy the key's full resource name from the actions menu.">
      ![Google Cloud key ring details with the Copy resource name action highlighted in the key's actions menu.](https://platform.claude.com/docs/images/cmek/gcp-copy-resource-name.png)
    </Frame>
  </Step>
</Steps>


## Register the key with Anthropic

Source: https://platform.claude.com/llms-full.txt#register-the-key-with-anthropic-3

How you register the key depends on which product you use.

<Tabs>
  <Tab title="Claude Platform">
    <Steps>
      <Step title="Register the key with Anthropic">
        Create an external key configuration through the Admin API, using the resource name from the Note the full key resource name step under Encryption key setup.

The response contains the external key ID:

</Step>

      <Step title="Validate the key">
        Trigger an encrypt and decrypt round-trip against your key.

A successful response looks like this:

If validation fails, common causes are:

        * **VPC Service Controls:** if a service perimeter protects Cloud KMS in your project, add Anthropic to an access level on the perimeter (or exclude the key's project) so Anthropic can reach the key.
        * **Domain restricted sharing:** the `constraints/iam.allowedPolicyMemberDomains` org policy can strip the Anthropic service account binding (see the earlier note). Confirm the binding is present with `gcloud kms keys get-iam-policy <your-key-name> --project=<your-project-id> --location=<region> --keyring=<your-keyring-name>`.
        * **Disabled or destroyed key version:** confirm the key's primary version is enabled, and not disabled, scheduled for destruction, or destroyed.
      </Step>

      <Step title="Attach the key to a workspace">
        Once the key is validated, attach it to a new workspace before you send any requests to that workspace. For a workspace that already receives requests, the key can take [up to a day to take effect](https://platform.claude.com/docs/en/manage-claude/cmek#how-it-works).

</Step>
    </Steps>
  </Tab>

  <Tab title="Claude Enterprise">
    In [claude.ai > Organization settings > Data and privacy](https://claude.ai/admin-settings/data-privacy-controls), open **Encryption keys**, then click **Add key**. Choose **Google Cloud**, paste the full key resource name from the previous step, and click **Continue**. Anthropic validates the key with an encrypt and decrypt round-trip. Once it shows as verified, your organization is CMEK-protected from that point forward.

    On Claude Enterprise, CMEK applies to the whole organization, so there is no separate workspace attach step, and an organization can have only one key.
  </Tab>
</Tabs>


## Terraform

Source: https://platform.claude.com/llms-full.txt#terraform-3

For infrastructure-as-code deployments, the same steps map to the `google` provider with the `google_kms_key_ring`, `google_kms_crypto_key`, and `google_kms_crypto_key_iam_member` resources.


---
title: Customer-managed encryption keys
url: https://platform.claude.com/docs/en/manage-claude/cmek
description: Encrypt Claude workspace data at rest with a key you control.
---

```bash Learn more with the /claude-api skill in Claude Code
claude "/claude-api tell me about customer-managed encryption keys"
```

A customer-managed encryption key (CMEK) lets you provision an encryption key in your own [AWS KMS](https://aws.amazon.com/kms/), [Google Cloud KMS](https://cloud.google.com/security/products/security-key-management), or [Azure Key Vault](https://azure.microsoft.com/en-us/products/key-vault) and have Anthropic use it to encrypt certain workspace data at rest. You retain full control of the key, including rotation, audit, and revocation, and the key operations Anthropic performs against your key are recorded in your cloud provider's audit logs.

The use of CMEK is optional. Eligible organizations can **opt in** to use customer-managed encryption keys instead of the default encryption that Anthropic provides. To activate CMEK, contact your Anthropic account team.

<Warning>
  **Enabling CMEK is permanent and can cause irreversible data loss**

  Enabling CMEK is permanent. Anthropic keeps no copy of your key, so misconfiguration or key loss can permanently destroy your CMEK-protected data. If you are uncertain about any step, contact your Anthropic representative before applying changes.

  * **Permanent data loss:** If your encryption key is deleted, scheduled for deletion, or has its key material destroyed, Anthropic cannot recover your data.
  * **Identifier verification is mandatory:** Granting key access to an incorrect or spoofed principal can expose your data to an unauthorized party. Always verify the Anthropic identifier against the published production identities in each configuration guide. On Claude Platform on AWS, that identity is the AWS service principal published in the [AWS KMS guide](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms#claude-platform-on-aws). Never trust an identifier provided over email, chat, or any onboarding channel.
</Warning>


## How it works

Source: https://platform.claude.com/llms-full.txt#how-it-works-12

Only Organization Admins (on Claude Platform; the Admin role on Claude Platform on AWS) or Owners and the Primary Owner (on Claude Enterprise) can configure CMEK. On Claude Platform, CMEK is scoped per workspace and configured with the Admin API (on Claude Platform on AWS, in the Claude Console or through the IAM-authorized external key and workspace endpoints). On Claude Enterprise, CMEK is scoped per organization and configured in [claude.ai > Organization settings > Data and privacy](https://claude.ai/admin-settings/data-privacy-controls). On either product, CMEK protects data written after your key takes effect. Existing data (prior chats, files, and sessions) remains encrypted with Anthropic-managed keys and is not re-encrypted under your key.

On Claude Platform, Anthropic recommends attaching your key to a new workspace before you send any requests to that workspace. If you attach a key to a workspace that already receives requests, your key can take up to a day to take effect. Data written before then, like existing data, is encrypted with Anthropic-managed keys and is not re-encrypted.

CMEK configuration events appear in the [Compliance API Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed). The key operations Anthropic performs against your key (such as wrapping and unwrapping data keys) do not appear in the Compliance API; they appear in your cloud provider's audit logs.

Anthropic calls your key management service from its standard public IP range. If you restrict access to your key management service by IP, allow the addresses listed in [IP addresses](https://platform.claude.com/docs/en/api/ip-addresses). On Claude Platform on AWS, don't rely on IP-based restrictions for your key; scope access with the key policy described in the [AWS KMS guide](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms#claude-platform-on-aws) instead.


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-21

* Permissions to create encryption keys and manage key access in the account, project, or subscription that will host the encryption key.
* An Organization Admin role in the Claude Console on Claude Platform (the Admin role on Claude Platform on AWS), or an Owner or Primary Owner role on Claude Enterprise.
* Data retention configuration: CMEK is allowed with [Zero data retention (ZDR)](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) for both Claude Platform and Claude Enterprise.


## Availability and regions

Source: https://platform.claude.com/llms-full.txt#availability-and-regions

Except on Claude Platform on AWS (covered at the end of this section), CMEK is currently available in US regions only, and all encryption operations are processed in US regions. For minimal latency, choose a region close to Anthropic's US infrastructure:

| Provider     | Recommended regions         |
| ------------ | --------------------------- |
| AWS          | `us-east-2`                 |
| Google Cloud | `us-central1`, `us-east5`   |
| Azure        | `northcentralus`, `eastus2` |

On [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), CMEK is available with AWS KMS keys only; Google Cloud KMS and Azure Key Vault keys cannot be registered. These region recommendations do not apply there: the key must be a single-region KMS key in the same AWS account and region as the workspace it is attached to, and its key policy must grant access to an AWS service principal rather than Anthropic's IAM role; see [Set up CMEK on Claude Platform on AWS](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms#claude-platform-on-aws). Register and attach keys in the Claude Console; the external key endpoints are also available on Claude Platform on AWS, authorized through [IAM actions](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#encryption-keys). There is no separate validation step: the key is implicitly validated when you attach it to a workspace (the attach call performs an encrypt/decrypt round), so a key policy problem surfaces at attach time rather than at registration.


## What CMEK protects

Source: https://platform.claude.com/llms-full.txt#what-cmek-protects

What CMEK covers depends on which product you use.

### Encrypted with CMEK key

**Claude Platform**

* Message content, files and attachments (both inline attachments sent with a request and Files API uploads), and MCP and tool configuration.
* [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) data, including agent configurations, environments, webhooks, and sessions and their events.

**Claude Enterprise**

* Chat content, including skills, plugins, and artifacts.
* Chat attachments and project attachments.
* Claude Code on the CLI, including message content.
* Cowork in Claude Desktop.
* Compliance API [local session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions) captured from sessions on users' machines. If your key cannot be used, the messages endpoint returns [503 Service Unavailable](https://platform.claude.com/docs/en/manage-claude/compliance-errors#local-sessions-temporarily-unavailable) instead of transcript content. Session metadata is still listed.
* Office agents.
* Claude in Chrome.

On both products, backups and snapshots inherit the key.

### Disabled or modified

Some features are turned off or substantially modified when CMEK is enabled. This list is not exhaustive; review it with your team before enabling CMEK.

**Claude Platform**

* Playground in the Claude Console is disabled.
* Portions of the Compliance API that return raw content, such as prompts, responses, and files, are disabled.
* Other beta and research preview features might not be covered by CMEK.

**Claude Enterprise**

* Conversation history search is disabled. Conversation titles are encrypted, so searching by title or content returns no results.
* [Project knowledge search](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects) (retrieval-augmented generation, or RAG) is disabled. Project knowledge loads directly into each conversation's context instead of being indexed and searched. As a result, a project can use substantially less knowledge than it could without CMEK. Knowledge beyond what can be loaded is left out of the conversation.
* Certain analytics are degraded: admin analytics for claude.ai skills and connectors (under claude.ai/analytics/usage and through the [Claude Enterprise Analytics API](https://platform.claude.com/docs/en/manage-claude/analytics-api)), Claude smart reports (under claude.ai/analytics/insights), and Claude Code contribution metrics (under claude.ai/analytics/claude-code).
* Audit log exports are disabled.
* Signed URLs for temporary file exchanges are disabled. These back organization data exports in claude.ai and Claude Code Remote file flows such as screenshot updates.

### Encrypted with Anthropic key

These features remain available, but their data is not encrypted under your key. You can disable any feature that is not appropriate for your use case in **Settings**.

**Claude Platform**

* Data that is not at rest (such as cache) and data with a TTL shorter than 24 hours.
* Activity Feed, audit logs, and telemetry network traffic such as OTEL, so customers can maintain compliance even if a key is revoked.
* Claude Managed Agents [vault credential](https://platform.claude.com/docs/en/managed-agents/vaults) values, such as OAuth tokens and client secrets. These are stored under Anthropic-managed encryption, are write-only, and are never returned in API responses.
* [User profiles](https://platform.claude.com/docs/en/api/beta/user_profiles): the `name`, `external_id`, and `metadata` fields are stored under Anthropic-managed encryption, not your key. Do not store sensitive personal data in profile `metadata`.

**Claude Enterprise**

* Claude Code Desktop, Claude Code on the web, and Claude in Slack. Anthropic recommends disabling any of these that are not appropriate for your use case in the admin console.
* Beta and research preview features might not be covered by CMEK and can break in CMEK organizations, for example, Claude Security and Claude Design.
* On-demand data export under **Settings** > **Privacy**.
* [Personal preferences - Instructions for Claude section](https://claude.ai/new#settings/general) and Cowork Global instructions. These are set at the account level and shared across all of a user's organizations.

On both products, account data for users in your organization (such as names, email addresses, and profile pictures) is not encrypted under your key.

### Feature support

The following Claude Platform APIs and tools store data at rest under your key when CMEK is enabled:

| APIs                  | Tools and features                                                                                |
| --------------------- | ------------------------------------------------------------------------------------------------- |
| Messages              | Web search                                                                                        |
| Models                | Web fetch                                                                                         |
| Files                 | Code execution                                                                                    |
| Batch                 | Bash tool                                                                                         |
| Skills                | Text editor tool                                                                                  |
| Claude Managed Agents | MCP connector                                                                                     |
|                       | Structured outputs (not available for Claude Fable or Claude Mythos models in CMEK organizations) |
|                       | Advisor tool                                                                                      |
|                       | Computer use                                                                                      |
|                       | Browser use                                                                                       |
|                       | Context management                                                                                |


## Limited preservation outside your key

Source: https://platform.claude.com/llms-full.txt#limited-preservation-outside-your-key

In three narrow cases, Anthropic may preserve specific records under Anthropic-managed encryption:

* Where Anthropic is required by law to retain records (for example, material reported to NCMEC under 18 U.S.C. § 2258A).
* Exigent risk of serious harm (for example, CBRNE weapons development, offensive cyberattacks, or imminent threats of violence).
* Violations of Section D.4 of Anthropic's [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms) or equivalent terms in a customer's other applicable agreement with Anthropic.

Outside of [CSAM screening](https://support.claude.com/en/articles/9020328-csam-detection-and-reporting), preservation requires a human reviewer's explicit decision and follows Anthropic's [retention policy for commercial data](https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data). For every instance of preservation, a corresponding [Compliance API Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) event is generated with a reason code conveying the purpose of the preservation. See [CMEK content preservation](https://platform.claude.com/docs/en/manage-claude/access-transparency#cmek-content-preservation) for details. Safety screening metadata (records derived from Anthropic's automated safety scans, such as pattern identifiers and match indicators, not conversation content) is retained under Anthropic-managed encryption and remains readable after key revocation.


## Limitations

Source: https://platform.claude.com/llms-full.txt#limitations-9

* **Irreversible action:** Once a key is attached to a workspace, it cannot be detached or swapped. On Claude Platform, attaching a key also locks the workspace's data retention setting: you cannot turn off 30-day data retention for that workspace, and returning to zero data retention requires creating a new workspace and moving your traffic to it. Rotating the key material within the same key (for example, AWS KMS automatic rotation, a Cloud KMS rotation schedule, or an Azure Key Vault rotation policy) is supported transparently and requires no change in Anthropic. Switching to a *different* key requires creating a new workspace with the new key and migrating your data. Revoking or disabling the key makes all CMEK-protected data in that workspace permanently inaccessible, with no backout path.
* **No retroactive encryption:** CMEK only protects data written after your key takes effect (see [How it works](https://platform.claude.com/docs/en/manage-claude/cmek#how-it-works)).
* **Latency:** Operations that wrap or unwrap data keys make a round-trip to your key management service, which can add a small amount of latency to actions that read or write data at rest.
* **Revocation delay:** Key revocation can take up to 1 hour (the cache TTL). Requests already in flight during that window may continue to succeed.
* **KMS costs:** CMEK requires a key in a third-party key management service (AWS KMS, Google Cloud KMS, or Azure Key Vault), which might incur separate charges billed by your KMS provider.
* **Claude Code telemetry behind a gateway:** When Claude Code connects through an LLM gateway or proxy (a custom `ANTHROPIC_BASE_URL`), CMEK does not apply to Claude Code's operational telemetry. To turn this telemetry off, set the `DISABLE_TELEMETRY` environment variable to `1`, as described under [Telemetry services](https://code.claude.com/docs/en/data-usage#telemetry-services) in the Claude Code documentation.


## Configure your provider

Source: https://platform.claude.com/llms-full.txt#configure-your-provider

Follow the guide for the key management service you use.

<CardGroup cols={3}>
  <Card href="https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms" title="AWS KMS">
    Create an AWS KMS key with a key policy that grants Anthropic access, then register it.
  </Card>

  <Card href="https://platform.claude.com/docs/en/manage-claude/cmek-google-cloud-kms" title="Google Cloud KMS">
    Create a Cloud KMS crypto key, grant Anthropic's service account access, then register it.
  </Card>

  <Card href="https://platform.claude.com/docs/en/manage-claude/cmek-azure-key-vault" title="Azure Key Vault">
    Create an RSA key, grant the Anthropic service principal access, then register and validate it.
  </Card>
</CardGroup>


### Data & compliance > Inference hooks

---
title: Configure Inference hooks
url: https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration
description: Allow Inference hooks for your Claude Enterprise organization, connect your AI security server, and control enforcement, failure handling, and rollout.
---

<Note>
  Inference hooks are in beta and available to Claude Enterprise organizations. Configuring them requires the `organization:manage` permission, which the built-in Admin, Owner, and Primary owner roles hold, as does any custom role granted it.
</Note>

Inference hooks send prompts from your organization to an AI security server you choose, and hold each request for an allow or deny verdict before Claude processes it. This page walks through turning the feature on, connecting your server, and controlling enforcement. To learn what Inference hooks are and when to use them, see the [Inference hooks overview](https://platform.claude.com/docs/en/manage-claude/inference-hooks). To build the AI security server itself, see [Develop an Inference hooks integration](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint).


## Before you begin

Source: https://platform.claude.com/llms-full.txt#before-you-begin-5

You need:

* The `organization:manage` permission in claude.ai. The built-in **Admin**, **Owner**, and **Primary owner** roles hold it, as does any custom role it has been granted.
* An AI security server HTTPS endpoint that accepts verdict requests: an `https://` URL on port 443, on a publicly routable host, reachable without redirects. Reverse-tunnel hosts (ngrok and similar tunnel services) are not supported: Anthropic's network policy blocks them. Don't test through a tunnel; host your server on a domain you control. For the full [hosting requirements](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#receive-a-request), and to build the server and verify signed requests, see [Develop an Inference hooks integration](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint).


## Set up Inference hooks

Source: https://platform.claude.com/llms-full.txt#set-up-inference-hooks

There are three enforcement states: **off** (**Enforce verdicts** is off: your AI security server is never contacted and prompts are not inspected), **shadow** (**Enforce verdicts** is on with **Mode** set to **Shadow mode**: your AI security server receives prompts and returns verdicts, and nothing is blocked), and **enforcing** (**Enforce verdicts** is on with **Mode** set to **Allow the request** or **Block the request**: a deny blocks the request). The following steps take a new configuration from off to enforcing.

<Steps>
  <Step title="Allow Inference hooks for your organization">
    Go to claude.ai > **Organization settings** > **Data and privacy** and find the **Inference hooks** section. Turn on **Allow for your organization**.

    Turning this on unlocks the Inference hooks settings page and always forces **Enforce verdicts** off, so allowing the feature never starts inspection by itself: even a configuration that previously had enforcement on stays uninspected until you turn **Enforce verdicts** back on in the final step.
  </Step>

  <Step title="Open the Inference hooks settings page">
    Still in **Data and privacy**, open the **Inference hooks** section to reach the Inference hooks settings page. It lives under Data and privacy rather than as its own entry in the settings nav, so its breadcrumb reads **Data and privacy / Inference hooks**. Until you save an endpoint, the page warns that prompts aren't being inspected yet, and **Enforce verdicts** stays off with a **Requires endpoint** badge.
  </Step>

  <Step title="Configure your endpoint">
    Click **Configure** to open the **Configure endpoint** dialog and fill in:

    * **Endpoint URL:** the `https://` URL that receives verdict requests. Only `https://` URLs are accepted.
    * **Custom request headers:** up to 16 static headers sent with every verdict request so your AI security server can authenticate the caller. Header values are stored encrypted and never shown again; after saving, only the header names are displayed. Because values are write-only, saving any change to the headers requires re-entering every value. Changing the endpoint URL clears all stored header values so your credentials are never sent to a new destination; re-enter them after a URL change. Header names must use standard HTTP token characters with `-` rather than `_`, and must not collide with reserved names (request-framing headers such as `Content-*` and `Host`, proxy and cookie headers, client-address headers such as `X-Forwarded-*`, the `webhook-*` signature headers, and the `X-Anthropic-*` prefix). Values must be printable ASCII.

    The dialog covers only those two fields plus **Test connection**; it doesn't ask about failure handling, which you choose in step 6. Once an endpoint is saved, the button reads **Edit**.
  </Step>

  <Step title="Test the connection">
    Click **Test connection**. Claude sends a synthetic test prompt to the URL and headers currently in the form, not the saved values, so re-enter any stored header values before testing. On success, the result reports whether your AI security server returned an allow or a deny verdict for the test prompt, which surfaces a deny-everything default before you start enforcing.

    Common failure results:

    | Result                 | What to check                                                                                                                                         |
    | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
    | URL rejected           | The URL failed a structural check. Use an `https://` URL on port 443.                                                                                 |
    | Private or internal IP | The host resolves to a private or internal address. Use a publicly routable host.                                                                     |
    | Timeout                | The AI security server did not return a verdict within the timeout.                                                                                   |
    | Transport error        | DNS resolution, the TLS handshake, or the connection failed.                                                                                          |
    | Non-200 status         | The AI security server responded with a status other than 200. Verdicts must come back as HTTP 200; redirects are not followed and count as failures. |
    | Unparseable response   | The AI security server responded, but the body is not a valid verdict.                                                                                |
  </Step>

  <Step title="Save and store your signing secret">
    Save the endpoint configuration. The first save generates your webhook signing secret and reveals it once. Copy it and store it securely before closing the dialog: the secret cannot be retrieved later, only [rotated](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration#rotate-your-signing-secret).

    Your AI security server uses this secret to verify the signature on every request it receives. For the verification procedure, see [Verify the signature](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#verify-the-signature).
  </Step>

  <Step title="Choose failure handling and timeout">
    Under **Failure handling**, set **Mode** to choose what happens while the AI security server is unreachable or verdicts time out:

    * **Block the request:** stop inference when your AI security server can't deliver a verdict (fail closed).
    * **Allow the request:** let the request proceed to the model without inspection (fail open).

    The dropdown's third option, **Shadow mode**, is a rollout tool rather than a failure policy; see [Shadow mode](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration#shadow-mode).

    Then set **Prompt verdict timeout (ms)**: 1 to 10,000ms, with a default of 5,000ms. The budget covers the entire exchange, and a slower verdict counts as an unreachable server, so set the lowest value your server can reliably meet.

    Changes in this section save as you make them. On first save, the defaults are **Allow the request** and 5,000ms.
  </Step>

  <Step title="Choose a rollout percentage">
    Under **Rollout**, set **Requests inspected (%)** to run inspection on a percentage of requests while you bring your AI security server up. The value ranges from 0 to 100: 100 inspects everything, and 0 turns inspection off.

    Each request rolls once for its whole conversation turn, so a single conversation can be partially inspected across turns. Requests outside the sampled percentage proceed without inspection, even when failure handling is set to **Block the request**.
  </Step>

  <Step title="Turn on Enforce verdicts">
    To evaluate verdicts against live traffic without blocking anyone at first, set **Mode** to **Shadow mode** (step 6) before turning on enforcement; see [Shadow mode](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration#shadow-mode).

    Turn on **Enforce verdicts** to gate Claude on your AI security server's verdict for every governed prompt, then confirm in the dialog, which restates your failure handling choice. Allow about a minute for the change to reach every Anthropic server; requests already in flight finish under the old setting. Turning it off stops prompts from being sent to your AI security server, again within about a minute; your configuration is kept.
  </Step>
</Steps>


## Shadow mode

Source: https://platform.claude.com/llms-full.txt#shadow-mode

Shadow mode runs your hook against live traffic without blocking anything. Your AI security server receives governed prompts and returns verdicts exactly as it would when enforcing, but nothing is blocked: every request proceeds to the model, even when your server denies it or can't be reached, and the end user sees nothing. Use it to tune your policy against your organization's real traffic before you start enforcing.

To use shadow mode, set **Mode** to **Shadow mode** under **Failure handling**, then turn on **Enforce verdicts** so prompts flow to your AI security server. While it is active, the settings page shows a **Shadow mode — not blocking** badge. To leave shadow mode, set **Mode** back to **Allow the request** or **Block the request**; verdicts are enforced again once enforcement is on.


## Exclusions

Source: https://platform.claude.com/llms-full.txt#exclusions

Under **Exclusions**, select roles whose members are not covered by Inference hooks: their prompts are never sent to your AI security server. Only custom roles your organization created can be excluded; the built-in roles aren't offered. Pick them in the role selector, whose placeholder reads **Select roles to exclude**, and manage who holds each role from the roles admin page (**Manage roles**); changing exclusions requires identity management permission. The list is empty by default, and with no roles excluded, every governed request is inspected.

Exclusion applies to a user's interactive sessions; traffic authenticated by machine credentials is always inspected. If Claude can't resolve a requester's role membership, the request fails closed with a retryable error rather than proceeding uninspected. Changes to the exclusion list are recorded in the audit trail.


## Custom blocked prompt message

Source: https://platform.claude.com/llms-full.txt#custom-blocked-prompt-message

Under **Custom blocked prompt message**, set custom text of up to 500 characters that is appended to the error an end user sees when your AI security server denies a request (typically who to contact or where to request an exception). The final message is your AI security server's per-request `deny_reason` (when present), a blank line, then this text. With no custom text configured, a built-in default directs the user to contact their administrators; you can also switch the appended message off entirely so the user sees only the `deny_reason`.


## Monitor your AI security server

Source: https://platform.claude.com/llms-full.txt#monitor-your-ai-security-server

The endpoint health area of the Inference hooks settings page shows:

* **Endpoint status:** Healthy, Tripped, Not enforcing, or Not configured before an endpoint is saved.
* **Failures per minute:** webhook failures over the last two minutes, averaged.
* **Block rate:** denials as a share of your AI security server's verdicts, shown while the rollout percentage is below 100.
* **Circuit breaker tripped:** when the breaker last tripped, if it has.
* **Recent errors:** each entry is reduced to a timestamp, an error type, and a one-line reason. Entries never include request content or your endpoint URL.

The panel is best-effort: if Anthropic cannot read the counters it shows zero failures and no errors rather than an error of its own, so a healthy-looking panel is not by itself proof that your AI security server is healthy. **Failures per minute** counts every failure, including the network and DNS errors that never trip the circuit breaker, so it can be high while **Circuit breaker tripped** stays empty.


## Circuit breaker

Source: https://platform.claude.com/llms-full.txt#circuit-breaker

Sustained webhook failures attributable to your AI security server trip the circuit breaker, which stops enforcement: your server is no longer contacted, and your **Failure handling** choice applies to every inspected request. With **Block the request** selected, users in your organization are blocked until the breaker resets. When the breaker trips, administrators are also notified in the claude.ai notification center.

Each trip is also recorded in your organization's [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) as an `inference_hooks_circuit_breaker_tripped` activity, so your security team or vendor can alert on trips from monitoring they already run, such as a SIEM that ingests the feed. One activity is recorded per trip, not one per affected request. Recording requires the Compliance API to be enabled for your organization; see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).

To recover, fix the server, then turn **Enforce verdicts** back on to reset the breaker.

The breaker can also reset on its own. Starting 10 minutes after the trip, Anthropic tests whether your server has recovered: at most about once per minute, one request from your organization's normal traffic is sent to your server for inspection, and that request proceeds for its user whether or not your server answers. If your server responds with a valid verdict, allow or deny, the breaker resets and enforcement resumes. Any other outcome is a webhook failure: the breaker stays tripped and testing continues.

Automatic recovery runs only while your Inference hooks settings are unchanged since the trip. If you change any Inference hooks setting after a trip, including rotating the signing secret, testing stops and the breaker no longer resets on its own; turn **Enforce verdicts** back on when your server is fixed. Automatic recovery applies only to trips: if you turn **Enforce verdicts** off yourself, enforcement stays off until you turn it back on.


## Rotate your signing secret

Source: https://platform.claude.com/llms-full.txt#rotate-your-signing-secret

Click **Rotate secret** under **Request signing** to replace your signing secret. Rotation is an immediate cutover: the new secret is generated and revealed once, the old secret can no longer be retrieved, and no request is ever signed with both secrets, so there is no overlap period to rely on.

Requests signed with the previous secret can still arrive briefly after rotation; [Verify the signature](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#verify-the-signature) covers how your AI security server should handle the switchover.


## Audit trail

Source: https://platform.claude.com/llms-full.txt#audit-trail

Inference hooks activity is recorded in your organization's [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed): configuration changes, denials, circuit breaker trips, and requests that proceeded without inspection under your failure handling setting. While the circuit breaker is tripped, no per-request Inference hooks activities are recorded; the trip activity is the feed's record of that window. Denial records carry identifiers that let you join each denial to the matching record in your own system.


## Turn Inference hooks off

Source: https://platform.claude.com/llms-full.txt#turn-inference-hooks-off

There are two levels of off:

* **Enforce verdicts** off, on the Inference hooks settings page: within about a minute, prompts from your organization stop being sent to your AI security server; requests already in flight finish under the old setting. The settings page stays available, so use this to pause enforcement while you work on your AI security server.
* **Allow for your organization** off, in **Data and privacy** settings: prompts are no longer inspected, and the Inference hooks settings become unavailable until you turn it back on. Your endpoint configuration, custom headers, and signing secret are kept either way; turning it back on forces **Enforce verdicts** off and clears a tripped circuit breaker, so turn enforcement on again when you are ready.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-90

<CardGroup cols={2}>
  <Card title="Develop an Inference hooks integration" href="https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint">
    Build the AI security server: the request and verdict schemas, signature verification, and operational semantics.
  </Card>

  <Card title="Inference hooks overview" href="https://platform.claude.com/docs/en/manage-claude/inference-hooks">
    What Inference hooks are, how the verdict round trip works, and what gets sent to your AI security server.
  </Card>
</CardGroup>


---
title: Develop an Inference hooks integration
url: https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint
description: Build the AI security server that receives signed Inference hooks requests, verifies them, and returns allow or deny verdicts.
---

<Note>
  Inference hooks are in beta and available to Claude Enterprise organizations. Field names, request shapes, and headers may change during the beta.
</Note>

An Inference hooks integration is an AI security server: an HTTPS service that Anthropic calls. For each governed request, your server receives a signed `POST` carrying the conversation transcript and responds with an allow or deny verdict. This page documents the protocol for building that server: the request and verdict schemas, signature verification, and the operational contract.

To turn Inference hooks on and point them at your endpoint, see [Configure Inference hooks](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration). To learn what Inference hooks are and when to use them, see the [Inference hooks overview](https://platform.claude.com/docs/en/manage-claude/inference-hooks).
