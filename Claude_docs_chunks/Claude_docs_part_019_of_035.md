# platform.claude.com Documentation (Part 19 of 35)

## Workspace roles and permissions

Source: https://platform.claude.com/llms-full.txt#workspace-roles-and-permissions

Members can have different roles in each workspace, allowing fine-grained access control.

| Role                        | Permissions                                                                                     |
| --------------------------- | ----------------------------------------------------------------------------------------------- |
| Workspace User              | Use playground only                                                                             |
| Workspace Limited Developer | Create and manage API keys, use the API. Cannot access session tracing views or download files. |
| Workspace Developer         | Create and manage API keys, use the API                                                         |
| Workspace Admin             | Full control over workspace settings and members                                                |
| Workspace Billing           | View workspace billing information (inherited from organization billing role)                   |

### Role inheritance

* **Organization admins** automatically receive Workspace Admin access to all workspaces
* **Organization billing members** automatically receive Workspace Billing access to all workspaces
* **Organization users and developers** must be explicitly added to each workspace
* **Service accounts** are added to workspaces from the service account's page in [Settings → Service accounts](https://platform.claude.com/settings/service-accounts) or from the workspace's **Service accounts** tab

<Note>
  The Workspace Billing role cannot be manually assigned. It's inherited from having the organization billing role.
</Note>


## Managing workspaces

Source: https://platform.claude.com/llms-full.txt#managing-workspaces

<Note>
  Only organization admins can create workspaces. Organization users and developers must be added to workspaces by an admin.
</Note>

### Using the Console

Create and manage workspaces in the [Claude Console](https://platform.claude.com/settings/workspaces).

#### Create a workspace

<Steps>
  <Step title="Open workspace settings">
    In the Claude Console, go to **Settings > Workspaces**.
  </Step>

  <Step title="Create a workspace">
    Click **Create workspace**.
  </Step>

  <Step title="Configure the workspace">
    Enter a workspace name and select a color for visual identification.
  </Step>

  <Step title="Create the workspace">
    Click **Create** to finalize.
  </Step>
</Steps>

<Tip>
  To switch between workspaces in the Console, use the **Workspaces** selector in the top-left corner.
</Tip>

#### Edit workspace details

To modify a workspace's name or color:

1. Select the workspace from the list.
2. Click the ellipsis menu (**...**) and choose **Edit details**.
3. Update the name or color and save your changes.

<Note>
  The Default Workspace cannot be renamed or deleted.
</Note>

#### Add members to a workspace

1. Navigate to the workspace's **Members** tab.
2. Click **Add to Workspace**.
3. Select an organization member and assign them a [workspace role](https://platform.claude.com/docs/en/manage-claude/workspaces#workspace-roles-and-permissions).
4. Confirm the addition.

To remove a member, click the trash icon next to their name.

<Note>
  Organization admins and billing members cannot be removed from workspaces while they hold those organization roles.
</Note>

#### Set workspace limits

Each workspace's settings split these across two tabs:

* **Rate limits:** On the **Rate limits** tab, set limits per model tier for requests per minute, input tokens, or output tokens
* **Spend limits:** On the **Spend limits** tab, cap monthly spending and configure alerts when spending reaches certain thresholds

#### Archive a workspace

To archive a workspace, click the ellipsis menu (**...**) and select **Archive**. Archiving:

* Preserves historical data for reporting
* Deactivates the workspace and archives every API key created for it
* Cannot be undone

<Warning>
  Archiving a workspace archives every API key created for that workspace within seconds (they remain listed in the Admin API as archived), and multi-workspace keys can no longer act in it. This action cannot be undone. If you archive the [Claude Code workspace](https://platform.claude.com/docs/en/manage-claude/workspaces#claude-code-workspace), members of your organization can no longer sign in to Claude Code through Console billing.
</Warning>

### Using the Admin API

Programmatically manage workspaces using the [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api).

<Note>
  Admin API endpoints accept an [Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys), an `org:admin` OAuth token, or a personal or service account key that isn't scoped to a specific workspace. Workspace keys don't work there. See [Authentication](https://platform.claude.com/docs/en/manage-claude/admin-api#authentication).
</Note>

```bash cURL
# Create a workspace
curl -X POST "https://api.anthropic.com/v1/organizations/workspaces" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -d '{"name": "Production"}'

# List workspaces
curl "https://api.anthropic.com/v1/organizations/workspaces?limit=10&include_archived=false" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Archive a workspace
curl -X POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/archive" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"

bash cURL
# Add a member to a workspace
curl -X POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -d '{
    "user_id": "user_xxx",
    "workspace_role": "workspace_developer"
  }'

# Update a member's role
curl -X POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -d '{"workspace_role": "workspace_admin"}'

# Remove a member from a workspace
curl -X DELETE "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

For complete parameter details, see the [Workspace Members API reference](https://platform.claude.com/docs/en/api/admin/workspaces/members/retrieve).


## API keys and resource scoping

Source: https://platform.claude.com/llms-full.txt#api-keys-and-resource-scoping

Every request runs in exactly one workspace and can only access resources within that workspace. Which workspace depends on the [key type](https://platform.claude.com/docs/en/manage-claude/authentication#key-types):

* A **workspace key** (a legacy key without an owner) belongs to the workspace it was created in and always runs there.
* A **personal key** or **service account key** acts as its user or service account. A single-workspace key always runs in the workspace chosen when it was created. A multi-workspace key runs in the workspace named by each request's `anthropic-workspace-id` header. Accounts must have access to the workspace to use it.

Resources scoped to workspaces include:

* **Files** created through the [Files API](https://platform.claude.com/docs/en/build-with-claude/files)
* **Message Batches** created through the [Batch API](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
* **Skills** created through the [Skills API](https://platform.claude.com/docs/en/build-with-claude/skills-guide)

Some resources are managed differently:

* **[MCP tunnels](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview)** are managed with a `workspace:manage_tunnels` OAuth token obtained through [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation), not an API key. Tunnels are created in a workspace, and the Console **MCP tunnels** list and the Managed Agent server picker show tunnels in the current workspace only; the cap of 10 active tunnels applies organization-wide. Tunnel management requires a role with tunnel management permissions; organization developers can view but not change them.
* **Workspaces** themselves and **organization members** are managed at the organization level through the [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api), using an Admin API key, an `org:admin` OAuth token, or a personal or service account key that isn't scoped to a specific workspace.

To look up your organization's workspace IDs, call the [List Workspaces](https://platform.claude.com/docs/en/api/admin/workspaces/list) endpoint or find them in the [Claude Console](https://platform.claude.com/settings/workspaces).

<Note>
  [Prompt caches](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) are also isolated per workspace on the Claude API, [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), and [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry). On Amazon Bedrock and Google Cloud, prompt caches are isolated per organization.
</Note>


## Identify the workspace behind an API response

Source: https://platform.claude.com/llms-full.txt#identify-the-workspace-behind-an-api-response

Claude API responses include an `anthropic-workspace-id` header alongside the `request-id` and `anthropic-organization-id` [response headers](https://platform.claude.com/docs/en/api/overview#response-headers). Its value is the `wrkspc_`-prefixed ID of the workspace that the request's API key or access token resolved to, including when that workspace is the Default Workspace. For example, a successful response includes headers like these:

The header is absent when the credential doesn't resolve to a workspace (for example, on Admin API requests) or when the request fails before authentication completes, such as a 401 error.

The following examples send a Messages API request and print the workspace ID from the response headers:

<CodeGroup>
  ```bash cURL
  # -D - prints the response headers; -o /dev/null discards the body
  curl -sS -D - -o /dev/null https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello, Claude"}]
    }' | grep -i '^anthropic-workspace-id'

bash CLI
  # --debug prints the HTTP response, including the Anthropic-Workspace-Id
  # header, to stderr; > /dev/null hides the JSON body on stdout
  ant --debug messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello, Claude"}' > /dev/null

python Python
  client = anthropic.Anthropic()

  response = client.messages.with_raw_response.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
  )
  workspace_id = response.headers.get("anthropic-workspace-id")
  print(f"Workspace ID: {workspace_id}")

typescript TypeScript
  const client = new Anthropic();

  const { response } = await client.messages
    .create({
      model: "claude-opus-5",
      max_tokens: 1024,
      messages: [{ role: "user", content: "Hello, Claude" }]
    })
    .withResponse();
  console.log("Workspace ID:", response.headers.get("anthropic-workspace-id"));

csharp C#
  AnthropicClient client = new();

  using var response = await client.WithRawResponse.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello, Claude" }]
  });
  var workspaceId = response.GetHeaderValues("anthropic-workspace-id").First();
  Console.WriteLine($"Workspace ID: {workspaceId}");

go Go
  client := anthropic.NewClient()

  var response *http.Response
  _, err := client.Messages.New(
  	context.Background(),
  	anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 1024,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, Claude")),
  		},
  	},
  	option.WithResponseInto(&response),
  )
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println("Workspace ID:", response.Header.Get("anthropic-workspace-id"))

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.http.HttpResponseFor;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      HttpResponseFor<Message> response = client.messages().withRawResponse().create(
          MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024)
              .addUserMessage("Hello, Claude")
              .build()
      );

      String workspaceId = response.headers().values("anthropic-workspace-id").getFirst();
      IO.println("Workspace ID: " + workspaceId);
  }

php PHP
  $client = new Client();

  $response = $client->messages->raw->create([
      'model' => Model::CLAUDE_OPUS_5,
      'maxTokens' => 1024,
      'messages' => [['role' => 'user', 'content' => 'Hello, Claude']],
  ]);
  echo 'Workspace ID: ' . $response->getHeaderLine('anthropic-workspace-id') . "\n";

ruby Ruby
  client = Anthropic::Client.new

  # Read response headers in per-request middleware, which receives the
  # raw HTTP response before the SDK parses it
  workspace_id = nil
  read_workspace_id = lambda do |request, call_next|
    response = call_next.call(request)
    # Keys in response.headers are lowercase
    workspace_id = response.headers["anthropic-workspace-id"]
    response
  end

  client.messages.create(
    model: Anthropic::Model::CLAUDE_OPUS_5,
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }],
    request_options: { middleware: [read_workspace_id] }
  )
  puts "Workspace ID: #{workspace_id}"

text Output wrap
Workspace ID: wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ
```

The same accessors read the header from other Claude API endpoints too, including the [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) APIs. For example, read `anthropic-workspace-id` from the response that [creates a session](https://platform.claude.com/docs/en/managed-agents/sessions) to record which workspace the session belongs to.

With the workspace ID from a response, you can:

* Confirm which workspace's usage, cost, and [rate limits](https://platform.claude.com/docs/en/api/rate-limits) the request counted toward
* Match it against the `workspace_id` field in [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api) reports and on [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api) objects such as API keys (both report `null` for the Default Workspace, as API keys also do for all-workspaces keys; an API key's `scope` field tells the two apart and, for a key bound to one workspace, carries that workspace's real ID)
* Check whether it's your Default Workspace's ID by passing it to [Get Workspace](https://platform.claude.com/docs/en/api/admin/workspaces/retrieve) with an [Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys): the Default Workspace comes back with `"name": "Default"`, even though [List Workspaces](https://platform.claude.com/docs/en/api/admin/workspaces/list) omits it
* Open that workspace in the [Console](https://platform.claude.com/settings/workspaces) to find the request's resources, such as sessions, files, message batches, and skills


## Workspace limits

Source: https://platform.claude.com/llms-full.txt#workspace-limits

You can set custom spend and rate limits for each workspace to protect against overuse and ensure fair resource distribution.

### Setting workspace limits

You can set workspace limits lower than (but not higher than) your organization's limits:

* **Spend limits:** Cap monthly spending for a workspace. Set these on the workspace's **Spend limits** settings tab in the [Claude Console](https://platform.claude.com/settings/workspaces).
* **Rate limits:** Limit requests per minute, input tokens per minute, or output tokens per minute. Set these on the workspace's **Rate limits** settings tab in the [Claude Console](https://platform.claude.com/settings/workspaces).

<Note>
  - You cannot set limits on the Default Workspace
  - If not set, workspace limits match the organization's limits
  - Organization-wide limits always apply, even if workspace limits add up to more
</Note>

For detailed information on rate limits and how they work, see [Rate limits](https://platform.claude.com/docs/en/api/rate-limits). You can also read your current organization and workspace rate limits programmatically with the [Rate Limits API](https://platform.claude.com/docs/en/manage-claude/rate-limits-api).


## Usage and cost tracking

Source: https://platform.claude.com/llms-full.txt#usage-and-cost-tracking

Track usage and costs by workspace using the [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api):

```bash cURL
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-08T00:00:00Z&\
workspace_ids[]=wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ&\
group_by[]=workspace_id&\
bucket_width=1d" \
  -H "anthropic-version: 2023-06-01" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

Usage and costs attributed to the Default Workspace have a `null` value for `workspace_id`.


## Common use cases

Source: https://platform.claude.com/llms-full.txt#common-use-cases-2

### Environment separation

Create separate workspaces for development, staging, and production:

| Workspace   | Purpose                                            |
| ----------- | -------------------------------------------------- |
| Development | Testing and experimentation with lower rate limits |
| Staging     | Pre-production testing with production-like limits |
| Production  | Live traffic with full rate limits and monitoring  |

### Team or department isolation

Assign workspaces to different teams for cost allocation and access control:

* **Engineering team** with developer access
* **Data science team** with their own API keys
* **Support team** with limited access for customer tools

### Project-based organization

Create workspaces for specific projects or products to track usage and costs separately.


## Best practices

Source: https://platform.claude.com/llms-full.txt#best-practices-10

<Steps>
  <Step title="Plan your workspace structure">
    Consider how you'll organize workspaces before creating them. Think about billing, access control, and usage tracking needs.
  </Step>

  <Step title="Use meaningful names">
    Name workspaces clearly to indicate their purpose (for example, "Production - Customer Chatbot" or "Dev - Internal Tools").
  </Step>

  <Step title="Set appropriate limits">
    Configure spend and rate limits to prevent unexpected costs and ensure fair resource distribution.
  </Step>

  <Step title="Audit access regularly">
    Review workspace membership periodically to ensure only appropriate users have access.
  </Step>

  <Step title="Monitor usage">
    Use the [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api) to track workspace-level consumption.
  </Step>
</Steps>


## FAQ

Source: https://platform.claude.com/llms-full.txt#faq-8

<AccordionGroup>
  <Accordion title="What's the Default Workspace?">
    Every organization has a "Default Workspace" that cannot be renamed, archived, or deleted. Like every workspace, it has a `wrkspc_` ID: the API returns it in the [`anthropic-workspace-id` response header](https://platform.claude.com/docs/en/manage-claude/workspaces#identify-the-workspace-behind-an-api-response), and you can pass it to [Get Workspace](https://platform.claude.com/docs/en/api/admin/workspaces/retrieve) and [Update Workspace](https://platform.claude.com/docs/en/api/admin/workspaces/update). It has no member list of its own, because access to it follows each member's organization role. It doesn't appear in [List Workspaces](https://platform.claude.com/docs/en/api/admin/workspaces/list) results, and API keys, usage reports, and cost reports that belong to it show `null` for `workspace_id`, as do all-workspaces API keys; an API key's `scope` field tells the two apart and, for a key that belongs to the Default Workspace, carries its real ID.
  </Accordion>

  <Accordion title="What's the Claude Code workspace?">
    Anthropic creates the Claude Code workspace automatically the first time a member of your organization signs in to Claude Code with their Console account. It isolates Claude Code's API keys, usage, and rate limits from your other workloads. See [Claude Code workspace](https://platform.claude.com/docs/en/manage-claude/workspaces#claude-code-workspace) for details.
  </Accordion>

  <Accordion title="Are there limits on workspaces?">
    Yes. Each organization can have up to 100 workspaces by default, and archived workspaces don't count toward this limit. If you need more, contact your account team.
  </Accordion>

  <Accordion title="How do organization roles affect workspace access?">
    Organization admins automatically get the Workspace Admin role in all workspaces. Organization billing members automatically get the Workspace Billing role. Organization users and developers must be manually added to each workspace.
  </Accordion>

  <Accordion title="Which roles can be assigned in workspaces?">
    Organization users and developers can be assigned Workspace Admin, Workspace Developer, Workspace Limited Developer, or Workspace User roles. The Workspace Billing role cannot be manually assigned; it's inherited from having the organization `billing` role.
  </Accordion>

  <Accordion title="Can organization admin or billing members' workspace roles be changed?">
    Organization admins and billing members cannot have their workspace roles changed or be removed from workspaces while they hold those organization roles (with one exception: billing members can be upgraded to a Workspace Admin role). For everyone else covered by this constraint, change their organization role first to change their workspace access.
  </Accordion>

  <Accordion title="What happens to workspace access when organization roles change?">
    If an organization admin or billing member is demoted to user or developer, they lose access to all workspaces except ones where they were manually assigned roles. When users are promoted to admin or billing roles, they gain automatic access to all workspaces.
  </Accordion>

  <Accordion title="What happens to API keys when a user is removed from a workspace?">
    Behavior depends on the [key type](https://platform.claude.com/docs/en/manage-claude/authentication#key-types).

    A personal or service account key stops working in a workspace shortly after its user or service account is removed from it. A service account key keeps working even if the user who created it is removed. Workspace API keys continue to work. In the [Claude Code workspace](https://platform.claude.com/docs/en/manage-claude/workspaces#claude-code-workspace), each key is bound to the member who created it and stops working when that member is removed.

    Personal keys are archived when their user is removed from the organization. If the user is re-invited, they need to create new keys; archived keys are not restored.
  </Accordion>
</AccordionGroup>


## See also

Source: https://platform.claude.com/llms-full.txt#see-also-4

* [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api)
* [Admin API reference](https://platform.claude.com/docs/en/api/admin)
* [Rate limits](https://platform.claude.com/docs/en/api/rate-limits)
* [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api)


### Authentication

---
title: App Attest for iOS and macOS apps
url: https://platform.claude.com/docs/en/manage-claude/app-attest
description: Let genuine installations of your iOS or macOS app call the Claude API without shipping an API key or running a proxy, using Apple's App Attest service.
---

App Attest authenticates iOS and macOS apps that call the Claude API directly from the device, with usage billed to your workspace. This page explains how App Attest works, how to register your app in the Claude Console, and how to revoke an app integration.

Apps use App Attest through the [Claude for Foundation Models](https://github.com/anthropics/ClaudeForFoundationModels) Swift package, which is in beta: it requires the OS 27 betas, and APIs might change during the beta. For the Swift configuration, see [Apple Foundation Models](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/apple-foundation-models#app-attest-production).


## How App Attest works

Source: https://platform.claude.com/llms-full.txt#how-app-attest-works

Each installation of your app uses Apple's [App Attest](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity) service to prove that it is a genuine, unmodified build of the app you registered. Anthropic then issues the device a short-lived access token that bills usage to your workspace. The app ships no API key, and there is no proxy for you to operate.

App Attest authentication is available only when your app calls the Claude API directly. It is not available through Amazon Bedrock, Google Cloud, or Microsoft Foundry.

The first time your app uses Claude on a device, the app requests a challenge from Anthropic, attests the device with Apple's `DCAppAttestService`, and exchanges the verified attestation for an access token. The Claude for Foundation Models package runs this flow automatically and requests new tokens as they expire; there is no attestation code for you to write.

Tokens are scoped to your workspace, expire after one hour, and authorize only [Messages API](https://platform.claude.com/docs/en/api/messages/create) calls. They carry no end-user identity: App Attest identifies your app, not the person using it, so handle any per-user logic in your app.


## Set up App Attest

Source: https://platform.claude.com/llms-full.txt#set-up-app-attest

<Note>
  App Attest requires a physical device. The Simulator, and hardware without a Secure Enclave, cannot perform App Attest. While developing in the Simulator, authenticate with an [API key](https://platform.claude.com/docs/en/manage-claude/authentication#api-keys) instead.
</Note>

To set up App Attest, you need your Apple Developer Team ID and the admin, owner, or primary owner role in your organization. Configure your Xcode project and register your app in the [Claude Console](https://platform.claude.com/):

1. In Xcode, add the **App Attest** capability to your app target under **Signing & Capabilities**.
2. In your workspace's settings in the Claude Console, open **App integrations**.
3. Click **Create app integration** and enter a name, your Apple Developer Team ID, and one or more bundle IDs (up to 32).
4. Copy the client ID (`clid_...`) from the integration's **Overview** tab and pass it to your app's Claude configuration.


## Revoke an app integration

Source: https://platform.claude.com/llms-full.txt#revoke-an-app-integration

To stop a compromised or retired app, revoke its integration: in your workspace's settings in the Claude Console, open **App integrations**, select the integration, and click **Revoke**, then confirm. Revoking an integration revokes its outstanding tokens, and its registered devices can no longer request new ones. Revocation is permanent, so create a new app integration to restore access.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-79

<CardGroup cols={2}>
  <Card title="Apple Foundation Models" icon="code" href="https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/apple-foundation-models#app-attest-production">
    Configure App Attest in the Claude for Foundation Models Swift package
  </Card>

  <Card title="Authentication" icon="lock" href="https://platform.claude.com/docs/en/manage-claude/authentication">
    Compare API keys, Workload Identity Federation, and App Attest
  </Card>
</CardGroup>


---
title: Create an Admin API key
url: https://platform.claude.com/docs/en/manage-claude/admin-api-keys
description: Create an Admin API key for your Claude Console or Claude Enterprise organization.
---

An Admin API key authenticates every API in the **Admin** section of this guide: the [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api), [Analytics APIs](https://platform.claude.com/docs/en/manage-claude/analytics-api), [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api), [Spend Limits API](https://platform.claude.com/docs/en/manage-claude/spend-limits-api), [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api), and [Rate Limits API](https://platform.claude.com/docs/en/manage-claude/rate-limits-api). You do not need a separate key for each API. The one exception is the Admin API's service-account, federation-issuer, and federation-rule endpoints, which accept only an OAuth bearer token with the `org:admin` scope. See [Obtain an OAuth bearer token](https://platform.claude.com/docs/en/manage-claude/admin-api#oauth-bearer-token).

Where you create the key depends on which Claude product your organization uses.


## Which key do you need?

Source: https://platform.claude.com/llms-full.txt#which-key-do-you-need

| Your organization                                           | Create the key in                                                                         | Key prefix           | Who can create it                                                                                                                                                                          | Works with                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Claude Console** (Claude Platform, `platform.claude.com`) | [Claude Console > Settings > Admin keys](https://platform.claude.com/settings/admin-keys) | `sk-ant-admin01-...` | Organization members with the **admin** role                                                                                                                                               | [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api), [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api), [Rate Limits API](https://platform.claude.com/docs/en/manage-claude/rate-limits-api), [Claude Code Analytics API](https://platform.claude.com/docs/en/manage-claude/claude-code-analytics-api), and the Compliance API [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed)                                                                                             |
| **Claude Enterprise** (`claude.ai`)                         | [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access)    | `sk-ant-api01-...`   | The parent organization's **primary owner** (all linked organizations). An **organization owner** can create one carrying Compliance API scopes only, restricted to their own organization | [User management](https://platform.claude.com/docs/en/manage-claude/user-management) (the Admin API's member, invite, and group endpoints), [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api), [Claude Enterprise Analytics API](https://platform.claude.com/docs/en/manage-claude/analytics-api), and [Spend Limits API](https://platform.claude.com/docs/en/manage-claude/spend-limits-api), according to the [scopes](https://platform.claude.com/docs/en/manage-claude/admin-api-keys#choose-scopes-for-a-claude-enterprise-key) you select |

A key created in one organization cannot be used to manage a different organization. If your company uses both Claude Console and Claude Enterprise, create one key in each.


## Create a key for a Claude Console organization

Source: https://platform.claude.com/llms-full.txt#create-a-key-for-a-claude-console-organization

<Steps>
  <Step title="Sign in as an organization admin">
    Only organization members with the **admin** role can create Admin API keys. See [Organization roles and permissions](https://platform.claude.com/docs/en/manage-claude/admin-api#organization-roles-and-permissions).
  </Step>

  <Step title="Open Admin keys settings">
    Go to [Claude Console > Settings > Admin keys](https://platform.claude.com/settings/admin-keys).
  </Step>

  <Step title="Create the key">
    Click **Create key**, give it a name, choose a [key expiration](https://platform.claude.com/docs/en/manage-claude/authentication#key-expiration), and click **Create**. Claude Console keys do not have selectable scopes; every key carries full access to all endpoints that accept Admin API keys (the service-account and federation endpoints noted at the top of this page do not accept Admin API keys).
  </Step>

  <Step title="Copy and store the secret">
    Copy the displayed secret (starting with `sk-ant-admin01-`) and store it in your secrets manager. The full secret is shown only once.
  </Step>
</Steps>


## Create a key for a Claude Enterprise organization

Source: https://platform.claude.com/llms-full.txt#create-a-key-for-a-claude-enterprise-organization

<Steps>
  <Step title="Sign in as the primary owner or an organization owner">
    The **primary owner** of the Claude Enterprise parent organization can create a key that can access every linked organization, or one restricted to a single organization. An **organization owner** can create a key with Compliance API scopes only, restricted to their own organization.
  </Step>

  <Step title="Open API settings">
    Go to [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access) and find the **Keys** section.
  </Step>

  <Step title="Click + Create key">
    Name the key and select the scopes you need from the [scopes table](https://platform.claude.com/docs/en/manage-claude/admin-api-keys#choose-scopes-for-a-claude-enterprise-key). The primary owner can combine scopes from different APIs (for example, `read:analytics` and `read:spend_limits`) on a single key.
  </Step>

  <Step title="Copy and store the secret">
    Copy the displayed secret (starting with `sk-ant-api01-`) and store it in your secrets manager. The full secret is shown only once.
  </Step>
</Steps>


## Choose scopes for a Claude Enterprise key

Source: https://platform.claude.com/llms-full.txt#choose-scopes-for-a-claude-enterprise-key

When you create a Claude Enterprise key, select every scope that the APIs you plan to call require. Scopes are fixed at creation; to add a scope later, create a new key.

| To call...                                                                                                                                                                                                                                                                                                                                                                                                             | Select these scopes           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| Admin API [user management](https://platform.claude.com/docs/en/manage-claude/user-management): list and look up members and invites; read custom roles and their permissions                                                                                                                                                                                                                                          | `read:members`                |
| Admin API [user management](https://platform.claude.com/docs/en/manage-claude/user-management): change member roles, remove members, create and withdraw invites                                                                                                                                                                                                                                                       | `write:members`               |
| Admin API [user management](https://platform.claude.com/docs/en/manage-claude/user-management): read groups and their members                                                                                                                                                                                                                                                                                          | `read:rbac_groups`            |
| Admin API [user management](https://platform.claude.com/docs/en/manage-claude/user-management): create, rename, and delete groups; add and remove group members; assign groups on invite creation                                                                                                                                                                                                                      | `write:rbac_groups`           |
| [Spend Limits API](https://platform.claude.com/docs/en/manage-claude/spend-limits-api): read members' effective spend limits and increase requests                                                                                                                                                                                                                                                                     | `read:spend_limits`           |
| [Spend Limits API](https://platform.claude.com/docs/en/manage-claude/spend-limits-api): set or clear per-user spend limits; approve or deny increase requests                                                                                                                                                                                                                                                          | `write:spend_limits`          |
| [Claude Enterprise Analytics API](https://platform.claude.com/docs/en/manage-claude/analytics-api): engagement, adoption, cost, and usage reports                                                                                                                                                                                                                                                                      | `read:analytics`              |
| [Compliance API Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed): organization-wide activity events                                                                                                                                                                                                                                                                          | `read:compliance_activities`  |
| [Compliance API chat, file, and project endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-content-data) and [Compliance API session endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-sessions): read chats, files, projects, session transcripts, and [organization users](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#list-organization-users) | `read:compliance_user_data`   |
| [Compliance API chat, file, and project endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-content-data): delete chats, files, and projects                                                                                                                                                                                                                                                       | `delete:compliance_user_data` |
| [Compliance API organization endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-org-data): read organization metadata and effective settings                                                                                                                                                                                                                                                      | `read:compliance_org_data`    |
| Admin API [user management](https://platform.claude.com/docs/en/manage-claude/user-management) read endpoints and every Compliance API read endpoint, with a single read-only scope (for security-audit integrations; does not include the Spend Limits or Analytics APIs)                                                                                                                                             | `read:org_audit`              |

The Compliance and Analytics APIs must be enabled for your organization before keys with those scopes can be used. See [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#set-up-the-compliance-api) and [Get access to the Claude Enterprise Analytics API](https://platform.claude.com/docs/en/manage-claude/analytics-api#get-access-to-the-claude-enterprise-analytics-api).


## Use the key

Source: https://platform.claude.com/llms-full.txt#use-the-key

Pass the key in the `x-api-key` header on every request. See each API's documentation for complete request examples.

A call that exceeds the key's scopes returns `403 Forbidden` with a message listing the scopes the key has and the scopes the endpoint needs.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-80

<CardGroup cols={2}>
  <Card title="Admin API" href="https://platform.claude.com/docs/en/manage-claude/admin-api">
    Manage organization members, workspaces, and API keys.
  </Card>

  <Card title="Spend Limits API" href="https://platform.claude.com/docs/en/manage-claude/spend-limits-api">
    Set per-member spend limits and review increase requests for your Claude Enterprise organization.
  </Card>

  <Card title="Analytics APIs" href="https://platform.claude.com/docs/en/manage-claude/analytics-api">
    Report on Claude Code productivity or Claude Enterprise engagement and adoption.
  </Card>

  <Card title="Compliance API" href="https://platform.claude.com/docs/en/manage-claude/compliance-api">
    Audit activity and retrieve or delete user content across your organization.
  </Card>
</CardGroup>


---
title: Manage WIF with the Admin API
url: https://platform.claude.com/docs/en/manage-claude/wif-admin-api
description: Create and manage Workload Identity Federation service accounts, issuers, and rules programmatically for infrastructure-as-code and CI workflows.
---

The Admin API lets you create and manage [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) resources programmatically: service accounts, federation issuers, and federation rules. Use it to keep your federation configuration in infrastructure as code, provision it from CI, and reproduce it across organizations instead of clicking through the Claude Console. These endpoints share the `/v1/organizations` path prefix with the rest of the [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api).


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-9

Every request on this page authenticates with an OAuth bearer token that carries the `org:admin` scope. The scope is granted only to organization members with the admin, owner, or primary owner role, and it grants access to the whole organization: any workspace binding is ignored. There are two ways to obtain a token, and they carry different permissions: a token from your own login acts as a user, whereas a federated token acts as a service account and cannot perform every operation on this page.

### Interactive (your terminal)

Log in with the [`ant` CLI](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/quickstart) under a dedicated profile, requesting the `org:admin` scope (see [Admin access](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/authentication#admin-access)), then export the bearer token:

```bash CLI
ant auth login --profile admin --scope "org:admin"
export ANTHROPIC_AUTH_TOKEN=$(ant auth print-credentials --profile admin --access-token)
```

Interactive tokens are short-lived; if requests start returning 401, re-run the export command (it refreshes the token automatically).

### Workload (CI and automation)

Create a federation rule with `oauth_scope: org:admin` that targets a service account whose `organization_role` is `admin`. The rule itself must be created in the Claude Console: granting a workload organization-admin access is a deliberate human action, not something automation can bootstrap for itself. The next section walks through this once-per-organization setup.


## Bootstrap a workload to manage WIF

Source: https://platform.claude.com/llms-full.txt#bootstrap-a-workload-to-manage-wif

One Console-created rule is enough to put the rest of your federation configuration under infrastructure as code: grant a single trusted workload the `org:admin` scope, and let that workload manage federation issuers and every workspace-scoped federation rule through this API.

<Steps>
  <Step title="Create the org:admin rule in the Console">
    In the Claude Console, go to **Settings → Workload identity** and select **Connect workload** to create one federation rule for your automation workload, for example a GitHub Actions workflow in your infrastructure repository. Under **Advanced rule options**, set the rule's OAuth scope to `org:admin`: the wizard then creates the new service account with the Admin organization role (or asks you to pick an existing admin service account as the target).

    <Warning>
      Match the rule to one exact workload identity, not a broad pattern. `subject_prefix` is an exact match unless it ends in `*`. For GitHub Actions, pin the subject to a protected branch, such as `repo:my-org/my-repo:ref:refs/heads/main`. A trailing wildcard such as `repo:my-org/my-repo:*` also matches `pull_request` runs, including runs triggered from forks, so anyone who could open a pull request against the repository could mint an `org:admin` token. See [Restrict which workflows can authenticate](https://platform.claude.com/docs/en/manage-claude/wif-providers/github-actions#restrict-which-workflows-can-authenticate).
    </Warning>
  </Step>

  <Step title="Exchange the workload's identity token">
    At runtime, the workload exchanges the JWT from its identity provider for a short-lived `org:admin` bearer token using the same [token exchange](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#authenticate-from-your-workload) as any other federated workload.
  </Step>

  <Step title="Manage issuers and workspace-scoped rules through the API">
    With the minted token in `ANTHROPIC_AUTH_TOKEN`, the workload creates and manages your federation configuration using the endpoints on this page.
  </Step>
</Steps>

For the operations a workload-minted token can and cannot perform, see [Permissions and constraints](https://platform.claude.com/docs/en/manage-claude/wif-admin-api#permissions-and-constraints). If you already created issuers, service accounts, or rules with the **Connect workload** wizard, list them with the following endpoints and import them into your infrastructure-as-code state instead of recreating them.


## Authentication

Source: https://platform.claude.com/llms-full.txt#authentication-6

All endpoints live under `https://api.anthropic.com/v1/organizations/`. Every request to the federation and service-account endpoints needs the API version header and the bearer token:

```bash cURL
curl --fail-with-body -sS "https://api.anthropic.com/v1/organizations/service_accounts" \
  -H "anthropic-version: 2023-06-01" \
  -H "authorization: Bearer $ANTHROPIC_AUTH_TOKEN"
```

Admin API keys are not accepted on these endpoints; the Admin API page's `x-api-key` examples do not apply here.


## Service accounts

Source: https://platform.claude.com/llms-full.txt#service-accounts

A [service account](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#service-accounts) (`svac_...`) is the non-human identity that a federated token acts as. Set `organization_role` to `developer`.

```bash cURL
# Create a service account
curl --fail-with-body -sS "https://api.anthropic.com/v1/organizations/service_accounts" \
  -H "anthropic-version: 2023-06-01" \
  -H "authorization: Bearer $ANTHROPIC_AUTH_TOKEN" \
  -H "content-type: application/json" \
  -d '{
    "name": "inference-worker",
    "organization_role": "developer"
  }'

# List service accounts
curl --fail-with-body -sS "https://api.anthropic.com/v1/organizations/service_accounts?limit=20" \
  -H "anthropic-version: 2023-06-01" \
  -H "authorization: Bearer $ANTHROPIC_AUTH_TOKEN"

# Archive a service account
curl --fail-with-body -sS -X POST "https://api.anthropic.com/v1/organizations/service_accounts/svac_.../archive" \
  -H "anthropic-version: 2023-06-01" \
  -H "authorization: Bearer $ANTHROPIC_AUTH_TOKEN"

json
{
  "id": "svac_...",
  "name": "inference-worker",
  "organization_role": "developer",
  "created_at": "...",
  "type": "service_account",
  "...": "..."
}
```

To read or update a single service account, use `GET` and `POST` on `/v1/organizations/service_accounts/{service_account_id}`. A service account must be a member of a workspace before federated tokens can act in it. Every service account has an implicit membership in your organization's default workspace; add explicit memberships for other workspaces with `GET`, `POST`, and `DELETE` on `/v1/organizations/service_accounts/{service_account_id}/workspaces`, where `DELETE` targets `.../workspaces/{workspace_id}`.

For complete parameter details and response schemas, see the [Service accounts API reference](https://platform.claude.com/docs/en/api/admin/service_accounts).


## Federation issuers

Source: https://platform.claude.com/llms-full.txt#federation-issuers

A [federation issuer](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#federation-issuers) (`fdis_...`) registers an OIDC identity provider with your organization. The `jwks` field is a discriminated union that controls how Anthropic fetches the provider's signing keys:

| `jwks` value                             | When to use                                                                       |
| ---------------------------------------- | --------------------------------------------------------------------------------- |
| `{"type": "discovery"}`                  | The provider serves `/.well-known/openid-configuration` at the issuer URL.        |
| `{"type": "explicit_url", "url": "..."}` | Point at a JWKS endpoint directly.                                                |
| `{"type": "inline", "keys": [...]}`      | Upload the key set for providers that are not reachable from the public internet. |

```bash cURL
# Register an issuer (GitHub Actions, with JWKS discovery)
curl --fail-with-body -sS "https://api.anthropic.com/v1/organizations/federation_issuers" \
  -H "anthropic-version: 2023-06-01" \
  -H "authorization: Bearer $ANTHROPIC_AUTH_TOKEN" \
  -H "content-type: application/json" \
  -d '{
    "name": "github-actions",
    "issuer_url": "https://token.actions.githubusercontent.com",
    "jwks": {"type": "discovery"}
  }'

# List issuers
curl --fail-with-body -sS "https://api.anthropic.com/v1/organizations/federation_issuers?limit=20" \
  -H "anthropic-version: 2023-06-01" \
  -H "authorization: Bearer $ANTHROPIC_AUTH_TOKEN"

# Archive an issuer
curl --fail-with-body -sS -X POST "https://api.anthropic.com/v1/organizations/federation_issuers/fdis_.../archive" \
  -H "anthropic-version: 2023-06-01" \
  -H "authorization: Bearer $ANTHROPIC_AUTH_TOKEN"
```

To read or update a single issuer, use `GET` and `POST` on `/v1/organizations/federation_issuers/{issuer_id}`. An OAuth caller cannot update an issuer that backs a rule whose `oauth_scope` is anything other than `workspace:developer` or `workspace:inference`; see [Permissions and constraints](https://platform.claude.com/docs/en/manage-claude/wif-admin-api#permissions-and-constraints).

For complete parameter details and response schemas, see the [Federation issuers API reference](https://platform.claude.com/docs/en/api/admin/federation_issuers).


## Federation rules

Source: https://platform.claude.com/llms-full.txt#federation-rules

A [federation rule](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#federation-rules) (`fdrl_...`) binds an issuer to a service account: JWTs from the issuer that satisfy the rule's match conditions can mint tokens that act as the rule's target. The `workspace_id` in the create request enables the rule in that workspace at creation; add more workspaces later through the `/federation_rules/{rule_id}/workspaces` sub-resource. Either `workspace_id` or `applies_to_all_workspaces: true` is required on create.

```bash cURL
# Create a rule (GitHub Actions deploys from the main branch)
curl --fail-with-body -sS "https://api.anthropic.com/v1/organizations/federation_rules" \
  -H "anthropic-version: 2023-06-01" \
  -H "authorization: Bearer $ANTHROPIC_AUTH_TOKEN" \
  -H "content-type: application/json" \
  -d '{
    "name": "gha-deploy",
    "issuer_id": "fdis_...",
    "match": {
      "subject_prefix": "repo:my-org/my-repo:ref:refs/heads/main",
      "claims": {"repository_owner": "my-org"}
    },
    "target": {
      "type": "service_account",
      "service_account_id": "svac_..."
    },
    "workspace_id": "wrkspc_...",
    "oauth_scope": "workspace:developer",
    "token_lifetime_seconds": 600
  }'

# List rules, optionally filtered by issuer
curl --fail-with-body -sS "https://api.anthropic.com/v1/organizations/federation_rules?issuer_id=fdis_..." \
  -H "anthropic-version: 2023-06-01" \
  -H "authorization: Bearer $ANTHROPIC_AUTH_TOKEN"

# Archive a rule
curl --fail-with-body -sS -X POST "https://api.anthropic.com/v1/organizations/federation_rules/fdrl_.../archive" \
  -H "anthropic-version: 2023-06-01" \
  -H "authorization: Bearer $ANTHROPIC_AUTH_TOKEN"

json
{
  "data": [{ "id": "fdrl_...", "name": "gha-deploy", "...": "..." }],
  "next_page": "..."
}
```

To read or update a single rule, use `GET` and `POST` on `/v1/organizations/federation_rules/{rule_id}`. To manage the workspaces a rule can mint tokens in, use `GET` and `POST` on `/v1/organizations/federation_rules/{rule_id}/workspaces`, and `DELETE` on `/v1/organizations/federation_rules/{rule_id}/workspaces/{workspace_id}`.

For complete parameter details and response schemas, see the [Federation rules API reference](https://platform.claude.com/docs/en/api/admin/federation_rules).


## Permissions and constraints

Source: https://platform.claude.com/llms-full.txt#permissions-and-constraints

<Note>
  * OAuth-authenticated callers can only create or modify rules whose `oauth_scope` is `workspace:developer` or `workspace:inference`. To create or modify a rule with any other scope (such as `org:admin` or `workspace:manage_tunnels`), use the Console.
  * An OAuth caller cannot update a federation issuer that backs a rule whose `oauth_scope` is anything other than `workspace:developer` or `workspace:inference` (such as `org:admin` or `workspace:manage_tunnels`). Consider registering a dedicated issuer for the bootstrap rule so the issuers behind workspace-scoped rules stay updatable through the API.
  * Admin API keys are not accepted on these endpoints, for reads or writes; use an `org:admin` OAuth token.
</Note>

A rule with `oauth_scope: org:admin` must target a service account whose `organization_role` is `admin`. Resource names must match `^[a-z0-9-]+$`, be 1 to 255 characters, and be unique within an organization for each resource type; for the full field-level constraints, see [Validation rules](https://platform.claude.com/docs/en/manage-claude/wif-reference#validation-rules).


## Pagination and archiving

Source: https://platform.claude.com/llms-full.txt#pagination-and-archiving

The service-account, federation-issuer, and federation-rule list endpoints accept `limit` (1 to 100, default 20) and a `page` cursor taken from the previous response. Pass the response's `next_page` value as the `page` query parameter on the next request. The rule-workspaces sub-resource list returns the full set without pagination. Archived resources are hidden from lists by default; pass `include_archived=true` to include them.

Archiving is a soft delete and is idempotent: archiving an already-archived resource succeeds. Archiving an issuer or a service account returns `400` while a live federation rule still references it; archive the rule first.


## See also

Source: https://platform.claude.com/llms-full.txt#see-also-5

* [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation): concepts and the Console setup walkthrough
* [WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference): environment variables, validation rules, OAuth scopes, and error codes
* [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api): the rest of the organization management surface
* [Admin API reference](https://platform.claude.com/docs/en/api/admin): generated request and response schemas for every Admin API endpoint


---
title: WIF reference
url: https://platform.claude.com/docs/en/manage-claude/wif-reference
description: Environment variables, validation rules, profile configuration, and error reference for Workload Identity Federation.
---

This page collects the configuration surfaces, validation constraints, and error mappings for [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation). For setup walkthroughs, see the [provider guides](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#identity-providers).


## Token exchange request

Source: https://platform.claude.com/llms-full.txt#token-exchange-request

`POST /v1/oauth/token` accepts a JSON body using the [RFC 7523](https://www.rfc-editor.org/rfc/rfc7523) `jwt-bearer` grant. The SDKs build this request for you from the [environment variables](https://platform.claude.com/docs/en/manage-claude/wif-reference#environment-variables); the cURL examples on each provider guide show the raw body.

| Field                | Required    | Description                                                                                                                                                                                                                                                                   |
| -------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `grant_type`         | Yes         | Always `urn:ietf:params:oauth:grant-type:jwt-bearer`.                                                                                                                                                                                                                         |
| `assertion`          | Yes         | The OIDC JWT issued by your identity provider.                                                                                                                                                                                                                                |
| `federation_rule_id` | Yes         | Tagged ID (`fdrl_...`) of the federation rule to evaluate.                                                                                                                                                                                                                    |
| `organization_id`    | Yes         | UUID of your Anthropic organization.                                                                                                                                                                                                                                          |
| `service_account_id` | Yes         | Tagged ID (`svac_...`) of the target service account.                                                                                                                                                                                                                         |
| `workspace_id`       | Conditional | Tagged ID (`wrkspc_...`) of the workspace to scope the minted token to, or the literal `default` for the organization's default workspace. Required when the rule is enabled for more than one workspace. When omitted, the server selects the rule's sole enabled workspace. |


## Token exchange response

Source: https://platform.claude.com/llms-full.txt#token-exchange-response

`POST /v1/oauth/token` returns a standard OAuth 2.0 token response ([RFC 6749 §5.1](https://www.rfc-editor.org/rfc/rfc6749#section-5.1)):

| Field          | Type    | Description                                                                                               |
| -------------- | ------- | --------------------------------------------------------------------------------------------------------- |
| `access_token` | string  | The short-lived Anthropic token, prefixed `sk-ant-oat01-...`. Pass it as `Authorization: Bearer <token>`. |
| `token_type`   | string  | Always `Bearer`.                                                                                          |
| `expires_in`   | integer | Seconds until the token expires.                                                                          |
| `scope`        | string  | The OAuth scope granted by the matched rule.                                                              |


## Environment variables

Source: https://platform.claude.com/llms-full.txt#environment-variables

The SDK reads these variables to perform a federated token exchange with no constructor arguments.

| Variable                        | Required                         | Description                                                                                                                                                                                                                                                                                                                         | Example                                |
| ------------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| `ANTHROPIC_FEDERATION_RULE_ID`  | Yes                              | Tagged ID of the federation rule to evaluate.                                                                                                                                                                                                                                                                                       | `fdrl_...`                             |
| `ANTHROPIC_ORGANIZATION_ID`     | Yes                              | UUID of your Anthropic organization. Find it in the Claude Console under **Settings > Organization**.                                                                                                                                                                                                                               | `00000000-0000-0000-0000-000000000000` |
| `ANTHROPIC_IDENTITY_TOKEN_FILE` | One of `_TOKEN_FILE` or `_TOKEN` | Filesystem path to the JWT issued by your identity provider (IdP). The SDK re-reads this file on every exchange so that projected tokens that rotate on disk are always current.                                                                                                                                                    | `/var/run/secrets/anthropic.com/token` |
| `ANTHROPIC_IDENTITY_TOKEN`      | One of `_TOKEN_FILE` or `_TOKEN` | The literal JWT as a string. Use when your platform injects the token as an environment variable rather than a file.                                                                                                                                                                                                                | `eyJhbGciOiJSUzI1NiIs...`              |
| `ANTHROPIC_SERVICE_ACCOUNT_ID`  | Yes                              | Tagged ID of the target Anthropic service account that the issued access token acts as.                                                                                                                                                                                                                                             | `svac_...`                             |
| `ANTHROPIC_WORKSPACE_ID`        | Conditional                      | Tagged ID of the workspace to scope the minted token to, or the literal `default`. Required when the federation rule is enabled for more than one workspace; optional when the rule is bound to a single workspace. The minted token is scoped to this workspace at exchange time, so switching workspaces requires a new exchange. | `wrkspc_...`                           |
| `ANTHROPIC_PROFILE`             | No                               | Name of a [configuration profile](https://platform.claude.com/docs/en/manage-claude/wif-reference#profile-configuration-file) to load. Takes precedence over the federation environment variables in this table.                                                                                                                    | `staging-profile`                      |

The direct environment-variable federation path activates only when `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`, `ANTHROPIC_SERVICE_ACCOUNT_ID`, and one of `ANTHROPIC_IDENTITY_TOKEN_FILE` or `ANTHROPIC_IDENTITY_TOKEN` are all set. `ANTHROPIC_WORKSPACE_ID` is read alongside but does not gate activation.

<Warning>
  A variable that is set to an empty string still occupies its slot in the credential precedence chain. If `ANTHROPIC_API_KEY=""` is exported, the SDK selects the API-key path with an empty key rather than falling through to federation. Unset unused credential variables rather than blanking them.
</Warning>

### Credential precedence

The SDK resolves credentials in this order. The first source that yields a credential wins.

| Order | Source                                                           | Notes                                                                                                                              |
| ----- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Constructor argument (`api_key=`, `auth_token=`, `credentials=`) | Always overrides everything else.                                                                                                  |
| 2     | `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN`                    | Shadows federation entirely. Unset these when migrating from API keys.                                                             |
| 3     | `ANTHROPIC_PROFILE`                                              | Loads `<config_dir>/configs/<name>.json`. A missing named profile is an error, not a fall-through.                                 |
| 4     | Federation environment variables                                 | `ANTHROPIC_FEDERATION_RULE_ID` + `ANTHROPIC_ORGANIZATION_ID` + `ANTHROPIC_SERVICE_ACCOUNT_ID` + `ANTHROPIC_IDENTITY_TOKEN[_FILE]`. |
| 5     | Active profile                                                   | Resolved from `<config_dir>/active_config`, falling back to a profile named `default`.                                             |

When a profile is loaded, environment variables fill any fields the profile omits but never override fields the profile sets explicitly. For example, `ANTHROPIC_WORKSPACE_ID` fills `workspace_id` only when the active profile does not set it.


## Profile configuration file

Source: https://platform.claude.com/llms-full.txt#profile-configuration-file

A profile is a named configuration file that the SDK and the `ant` CLI both read. Profiles let you ship federation parameters with your container image or switch between environments without changing code.

### Configuration directory

The SDK locates the configuration directory in this order:

1. `$ANTHROPIC_CONFIG_DIR`
2. `~/.config/anthropic` on Linux and macOS
3. `%APPDATA%\Anthropic` on Windows

### Active profile

The active profile name resolves in this order:

1. `$ANTHROPIC_PROFILE`
2. The contents of `<config_dir>/active_config` (a one-line file written by `ant profile activate <name>`)
3. The literal name `default`

Claude Code and the Claude Agent SDK honor this same resolution order, so a federation profile configured here also authenticates those tools without additional setup.

### File layout

| Path                                      | Contents                                                                                         | Sensitivity                                       |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------- |
| `<config_dir>/configs/<profile>.json`     | `version`, the `authentication` block, `organization_id`, `workspace_id`, and `base_url`.        | Non-secret. Safe to commit or bake into an image. |
| `<config_dir>/credentials/<profile>.json` | `version`, the cached `access_token`, `expires_at`, and (for interactive login) `refresh_token`. | Secret. Written by the SDK with mode `0600`.      |

Both the config file and the credentials file carry a top-level string `version` field in `major.minor` format (currently `"1.0"`). The SDK writes this field automatically so future releases can detect and migrate older formats; omit it when authoring a config by hand and the SDK treats the file as the current version.

### Federation profile example

```json configs/production.json
{
  "version": "1.0",
  "authentication": {
    "type": "oidc_federation",
    "federation_rule_id": "fdrl_...",
    "service_account_id": "svac_...",
    "identity_token": {
      "source": "file",
      "path": "/var/run/secrets/anthropic.com/token"
    }
  },
  "organization_id": "00000000-0000-0000-0000-000000000000",
  "workspace_id": "wrkspc_...",
  "base_url": "https://api.anthropic.com"
}
```

If `authentication.identity_token` is omitted, the SDK falls back to `ANTHROPIC_IDENTITY_TOKEN_FILE` or `ANTHROPIC_IDENTITY_TOKEN` from the environment.


## OAuth scopes

Source: https://platform.claude.com/llms-full.txt#oauth-scopes

The `oauth_scope` you set on a federation rule determines which Claude API endpoints the minted access token can call.

| Scope                      | Grants access to                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `workspace:developer`      | All non-administrative Claude API endpoints in the rule's workspace: [Messages](https://platform.claude.com/docs/en/api/messages) (including streaming and token counting), [Models](https://platform.claude.com/docs/en/api/models-list), [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) and their sessions, [Files](https://platform.claude.com/docs/en/build-with-claude/files), and [Skills](https://platform.claude.com/docs/en/build-with-claude/skills-guide). This matches the access a workspace API key in the same workspace has. |
| `workspace:inference`      | The inference endpoints in the rule's workspace: [Messages](https://platform.claude.com/docs/en/api/messages) (including streaming and token counting), [Models](https://platform.claude.com/docs/en/api/models-list), and the [OpenAI-compatible chat endpoint](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk). Use this for workloads that only need to call Claude and never need to manage Files, Skills, or other resources.                                                                                                             |
| `workspace:manage_tunnels` | The [MCP tunnels API](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference#tunnels-api): create, list, and get tunnels, register and archive CA certificates, reveal and rotate the tunnel token, and archive tunnels. The Console's create-tunnel modal window locks this scope when you create a rule from it.                                                                                                                                                                                                                                      |
| `org:admin`                | Full access to the [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api) (organization members, invites, workspaces, API keys, and the rest). An OAuth `org:admin` token can only create or modify rules scoped to `workspace:developer` or `workspace:inference`, and cannot update an issuer that backs a rule with any other scope; see the [constraints](https://platform.claude.com/docs/en/manage-claude/wif-admin-api#permissions-and-constraints).                                                                                               |

A request to an endpoint outside the token's scope returns HTTP 403. Finer-grained scopes (per resource, or read versus write) are not currently available.

### Permission boundaries

A federation rule's `oauth_scope` is a ceiling: the minted token can never exceed it. The target service account's `organization_role` (`developer` or `admin`) determines which scopes are grantable, so a rule that grants `org:admin` must target a service account with `organization_role=admin`. Effective permissions are the intersection of the rule's scope and the service account's role.

| Rule `oauth_scope`    | Service account `organization_role` | Effective permissions                                                                                                                                                                                                                         |
| --------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `workspace:developer` | `admin`                             | Claude API access in the rule's workspace only. The scope caps the token below the role.                                                                                                                                                      |
| `org:admin`           | `admin`                             | Full Admin API access (organization members, invites, workspaces, API keys, and the rest), minus the OAuth-caller carve-outs; see [constraints](https://platform.claude.com/docs/en/manage-claude/wif-admin-api#permissions-and-constraints). |


## Validation rules

Source: https://platform.claude.com/llms-full.txt#validation-rules-2

Anthropic enforces these constraints when you create or update issuers and rules, and when verifying an incoming JWT at exchange time.

For complete parameter details and response schemas, see the [Service accounts API reference](https://platform.claude.com/docs/en/api/admin/service_accounts), [Federation issuers API reference](https://platform.claude.com/docs/en/api/admin/federation_issuers), and [Federation rules API reference](https://platform.claude.com/docs/en/api/admin/federation_rules).

### Resource fields

| Field                                    | Constraint                                                                                                                                                                                                                                                                                 |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Issuer, rule, and service account `name` | Must match `^[a-z0-9-]+$`, length 1 to 255 characters.                                                                                                                                                                                                                                     |
| `workspace_id`                           | Required on create unless `applies_to_all_workspaces` is true. The workspace (`wrkspc_...`) whose quota, billing, and rate limits apply to tokens minted under this rule. Must be a workspace in the same organization, and the target service account must be a member of that workspace. |
| `applies_to_all_workspaces`              | Boolean. Set `true` to enable the rule in every workspace in the organization instead of naming one; either this or `workspace_id` is required on create.                                                                                                                                  |
| `token_lifetime_seconds`                 | Integer between `60` and `86400` (1 minute to 24 hours). Default `3600`. Values outside this range are rejected at request time. See [Token lifetime and refresh](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#token-lifetime-and-refresh).              |

### URL fields

The `issuer_url`, `jwks.discovery_base`, and `jwks.url` fields are validated:

| Constraint | Detail                                                                                                                   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------ |
| Scheme     | Must be `https`.                                                                                                         |
| Port       | Must be `443` (explicit or default).                                                                                     |
| Host       | Must be a public DNS hostname for your OIDC provider. Must resolve to public IP addresses; IP literals are not accepted. |

URL validation failures return `400 invalid_request_error` with the field name as a prefix on the error message (for example, `issuer_url: url must use https scheme`).

<Note>
  URL constraints apply only to URLs that Anthropic dials. In `explicit_url` and `inline` JWKS modes, and in `discovery` mode when `jwks.discovery_base` is set, the `issuer_url` is compared against the JWT `iss` claim as a string and is never fetched, so it may reference an internal hostname or non-standard port.
</Note>

### JWT verification

| Constraint        | Detail                                                                                                                                                                                                                                                                                                                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Maximum size      | The `assertion` JWT must be at most 16 KiB.                                                                                                                                                                                                                                                                                                                                                      |
| Signing algorithm | Only asymmetric algorithms (RSA and ECDSA families: ES256, ES384, ES512, RS256, RS384, RS512, PS256, PS384, PS512) are accepted. HMAC (`HS256`, `HS384`, `HS512`) and `none` are rejected.                                                                                                                                                                                                       |
| Key ID            | The JWT header must carry a `kid` that matches a key in the issuer's JWKS. Tokens without `kid` are rejected.                                                                                                                                                                                                                                                                                    |
| Required claims   | `sub` must be present. `iat` must be present and not in the future. `exp` must be present and in the future.                                                                                                                                                                                                                                                                                     |
| Single use        | An assertion that carries a `jti` claim can be exchanged only once per issuer: repeating an exchange with the same `jti` is rejected as a replay. The issuer's `check_jti` field (enabled by default) controls this check; assertions without a `jti` claim are not subject to it. See the [Federation issuers API reference](https://platform.claude.com/docs/en/api/admin/federation_issuers). |
| Maximum lifetime  | The token's lifetime (`exp` minus `iat`) must not exceed the issuer's configured maximum (1 hour by default, configurable for each issuer in the Claude Console).                                                                                                                                                                                                                                |
| Clock skew        | A 30-second leeway is applied to `exp`, `nbf`, and `iat`.                                                                                                                                                                                                                                                                                                                                        |


## Rule matching semantics

Source: https://platform.claude.com/llms-full.txt#rule-matching-semantics

A federation rule's `match` block determines whether an incoming JWT is accepted. All populated fields are evaluated with AND semantics: the JWT must satisfy every populated matcher. At least one of `subject_prefix`, `claims`, or `condition` must be set; a `match` block that contains only `audience` (or no matchers at all) is rejected. This guards against rules that would accept every token from an issuer.

| Matcher          | Type                 | Semantics                                                                                                                                                                                                 |
| ---------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `subject_prefix` | string               | Exact match against the JWT `sub` claim. A trailing `*` makes it a prefix match (the `sub` value must begin with the characters before the `*`). Case-sensitive.                                          |
| `audience`       | string               | The JWT `aud` claim must contain this exact string. When `aud` is an array, any element matching exactly satisfies the check.                                                                             |
| `claims`         | map\<string, string> | Each key is a top-level claim name and each value is the required exact string value. For nested, numeric, boolean, or complex claims like lists and maps, use `condition` with a CEL expression instead. |
| `condition`      | string (CEL)         | A [CEL](https://cel.dev/) expression that must evaluate to `true`.                                                                                                                                        |

### CEL evaluation environment

The `condition` expression has access to a single variable:

| Variable | Type | Contents                                                                      |
| -------- | ---- | ----------------------------------------------------------------------------- |
| `claims` | map  | The full decoded JWT claim set. Nested objects are accessible as nested maps. |

Example:

```text wrap
claims.sub.startsWith("repo:acme-corp/") && claims.ref in ["refs/heads/main", "refs/heads/release"]
```

<Warning>
  CEL conditions are security boundaries. An expression that evaluates to `true` for more inputs than intended grants broader access than intended. Prefer the static matchers when they express your constraint.
</Warning>


## Errors

Source: https://platform.claude.com/llms-full.txt#errors-2

### Token exchange errors

`POST /v1/oauth/token` returns errors in the standard [API error shape](https://platform.claude.com/docs/en/api/errors). The SDK wraps exchange failures in a typed `FederationExchangeError` (or language equivalent) that exposes the HTTP status, the response body, and the `request_id`.

| Status | Error                   | Cause                                                                                                                                                                   | Resolution                                                                                                                                                                                                                                                                                                                    |
| ------ | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 400    | `invalid_request_error` | `federation_rule_id` is malformed or a required request field is missing.                                                                                               | Verify the `fdrl_` ID and that the request body includes all required fields.                                                                                                                                                                                                                                                 |
| 400    | `invalid_request_error` | `workspace_id` is present but is not a well-formed `wrkspc_...` ID or the literal `default`.                                                                            | Fix the `workspace_id` value; the response message names the expected format.                                                                                                                                                                                                                                                 |
| 401    | `authentication_error`  | The JWT `iss` claim does not equal the registered `issuer_url` exactly.                                                                                                 | Compare byte-for-byte, including trailing slashes and scheme: `jq -rR 'split(".")[1] \| gsub("-";"+") \| gsub("_";"/") \| @base64d \| fromjson \| .iss' <<< "$JWT"`.                                                                                                                                                          |
| 401    | `authentication_error`  | JWKS fetch failed, JWKS is stale, or the JWT was signed with a key not in the JWKS.                                                                                     | For `inline` mode, update the issuer with the rotated keys. For `discovery` and `explicit_url`, confirm the JWKS endpoint is reachable on port 443; if the issuer recently rotated its signing key, see [Key rotation and caching](https://platform.claude.com/docs/en/manage-claude/wif-reference#key-rotation-and-caching). |
| 401    | `authentication_error`  | The JWT `exp` claim is in the past (beyond the 30-second skew window).                                                                                                  | Confirm your identity provider is projecting a fresh token and the SDK is re-reading the token file.                                                                                                                                                                                                                          |
| 401    | `authentication_error`  | The JWT was verified but its claims do not satisfy the rule's `match` block.                                                                                            | Decode the JWT and compare each claim against the rule. `subject_prefix` is case-sensitive. `audience` requires an exact element match.                                                                                                                                                                                       |
| 401    | `authentication_error`  | The `federation_rule_id` does not exist, is archived, or the JWT is not authorized for it (consolidated to prevent enumeration).                                        | Confirm the rule ID in the Claude Console and that the rule has not been archived.                                                                                                                                                                                                                                            |
| 401    | `authentication_error`  | The federation rule is enabled for more than one workspace and the request omits `workspace_id`. The authentication history entry shows reason `workspace_id_required`. | Set `ANTHROPIC_WORKSPACE_ID` (or the `workspace_id` body field on a raw request) to the `wrkspc_...` ID you want the token scoped to. See [Token exchange request](https://platform.claude.com/docs/en/manage-claude/wif-reference#token-exchange-request).                                                                   |

Every assertion denial returns the same opaque `401` `authentication_error` with the fixed message `Authentication failed`, regardless of which check failed; a distinguishable error would let a caller probe rule configuration. The deny reason is recorded on the attempt's entry in the [authentication history](https://platform.claude.com/settings/workload-identity-federation?tab=history), for example `match_subject_prefix` when the `sub` claim fails the rule's `subject_prefix`, or `workspace_id_required` when the rule spans multiple workspaces and the request names none. Requests rejected before the rule's organization is corroborated (the `400 invalid_request_error` family above) leave no history entry; their response messages name the problem directly. A `401` with no matching history entry usually means the `federation_rule_id` itself was not recognized.

### Common SDK-side failures

| Symptom                                                      | Cause                                                                                                                                                                       | Resolution                                                                                                                           |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| SDK reports "no credentials" instead of exchanging           | One of `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`, `ANTHROPIC_SERVICE_ACCOUNT_ID`, or `ANTHROPIC_IDENTITY_TOKEN[_FILE]` is unset and no profile is active. | Set all four variables, or configure a profile.                                                                                      |
| SDK authenticates with an API key instead of federating      | `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` is set and wins precedence.                                                                                                   | Unset the key or token variable.                                                                                                     |
| `FileNotFoundError` on first request                         | The path in `ANTHROPIC_IDENTITY_TOKEN_FILE` does not exist. The SDK opens the file lazily at exchange time.                                                                 | Confirm the projected-token volume is mounted and the path matches.                                                                  |
| Token exchange succeeds but a Claude API request returns 403 | The minted token's scope does not grant access to that endpoint.                                                                                                            | Check the rule's `oauth_scope` against [OAuth scopes](https://platform.claude.com/docs/en/manage-claude/wif-reference#oauth-scopes). |
| Authentication fails with empty credential                   | A credential environment variable is exported but set to an empty string. Empty values still win their precedence slot.                                                     | Unset the variable with `unset VAR` rather than `VAR=""`.                                                                            |


## Troubleshoot a failed exchange

Source: https://platform.claude.com/llms-full.txt#troubleshoot-a-failed-exchange

A `401` `authentication_error` response is intentionally opaque and its message is always `Authentication failed`; the deny reason is recorded in the authentication history, not in the response.

<Tip>
  Start with the [authentication history page](https://platform.claude.com/settings/workload-identity-federation?tab=history) in the Claude Console. Recent exchange attempts surface the issuer and rule that were evaluated, the JWT claims that were inspected, and which validation step failed, which usually short-circuits the following checks.
</Tip>

One common opaque failure is a replayed assertion: an assertion that carries a `jti` claim can be [exchanged only once](https://platform.claude.com/docs/en/manage-claude/wif-reference#jwt-verification), so a workload that re-sends the same JWT (a retry loop, or a refresh that re-reads an unrotated token) is rejected on the second exchange. The authentication history page shows these attempts with the reason `jti_reused`; the fix is to mint a fresh assertion for each exchange.

If you still need to debug from the JWT itself, work through these checks in order:

<Steps>
  <Step title="Decode the JWT">
    Decode the assertion you sent so you can compare each claim against your issuer and rule configuration:

    ```bash cURL
    jq -rR 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson' <<< "$JWT"
    ```
  </Step>

  <Step title="Check iss matches the issuer">
    The decoded `iss` claim must equal the registered `issuer_url` byte for byte, including scheme, port, and any trailing slash. A mismatch on a single character fails verification.
  </Step>

  <Step title="Check aud matches the rule">
    The decoded `aud` claim must contain the rule's `audience` value as an exact match. When `aud` is an array, one element must match exactly.
  </Step>

  <Step title="Check sub and each claims entry">
    Compare `sub` against the rule's `subject_prefix` (case-sensitive; a trailing `*` is a prefix match, anything else is exact). Compare every key in the rule's `claims` map against the same-named top-level claim.
  </Step>

  <Step title="Check exp, nbf, and iat">
    `exp` must be in the future and `nbf`/`iat` must be in the past, within the 30-second skew window. If the workload host's clock has drifted, an otherwise valid token is rejected.
  </Step>

  <Step title="Check JWKS reachability">
    For `discovery` mode, fetch `<jwks.discovery_base or issuer_url>/.well-known/openid-configuration` over public HTTPS on port 443 and confirm `jwks_uri` resolves. For `explicit_url`, fetch the JWKS URL directly. For `inline`, confirm the issuer's signing key has not rotated since you registered the keys.

    If the issuer rotated its signing key and immediately started signing with it, exchanges can fail for up to a minute while Anthropic's JWKS cache refreshes. See [Key rotation and caching](https://platform.claude.com/docs/en/manage-claude/wif-reference#key-rotation-and-caching).
  </Step>
</Steps>


## JWKS source modes

Source: https://platform.claude.com/llms-full.txt#jwks-source-modes

When you register a federation issuer, the `jwks` field controls how Anthropic obtains the public keys used to verify JWT signatures from that issuer. It is a discriminated union keyed on `type`:

| `jwks.type`           | `jwks` shape                                                                                                                                       | Behavior                                                                                                                                                                                               | Use when                                                                                                                                                        |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `discovery` (default) | `{ "type": "discovery", "discovery_base": "https://..." }` (`discovery_base` is optional; set it when the discovery URL differs from `issuer_url`) | Anthropic fetches `<discovery_base or issuer_url>/.well-known/openid-configuration`, reads `jwks_uri` from the discovery document, and fetches the JWKS from there.                                    | Your IdP serves a standard OIDC discovery document on the public internet. Most managed providers (EKS, GKE, Cloud Run, GitHub Actions, Entra ID) support this. |
| `explicit_url`        | `{ "type": "explicit_url", "url": "https://..." }`                                                                                                 | Anthropic fetches the JWKS directly from `url`. The `issuer_url` is used only for string comparison against the JWT `iss` claim and is never dialed.                                                   | Your IdP does not serve a discovery document, or discovery is internal-only but the JWKS is publicly reachable.                                                 |
| `inline`              | `{ "type": "inline", "keys": [...] }`                                                                                                              | You supply the array of JWK objects inline (the `keys` array from the JWKS document, not the wrapper object). Anthropic makes no outbound request. The `issuer_url` is used only for `iss` comparison. | Air-gapped environments, self-managed Kubernetes clusters with cluster-internal issuer URLs, or when you want explicit control over key rotation.               |

The discriminated union makes the companion fields mutually exclusive by construction. Both `discovery` and `explicit_url` also accept an optional `ca_cert_pem` string for issuers that serve TLS from a private CA.

### Key rotation and caching

In `discovery` and `explicit_url` modes, Anthropic caches the fetched JWKS. If your identity provider publishes a new signing key and immediately starts signing tokens with it, exchanges that present those tokens may fail with a signature error for up to 1 minute while the cache refreshes.

To avoid this window, publish a new signing key in the JWKS at least 15 minutes before your identity provider starts signing tokens with it, and keep the superseded key in the JWKS until tokens it signed have expired. Managed identity providers typically follow this discipline on their own. If you operate your own issuer (a self-managed Kubernetes cluster, a SPIRE OIDC discovery provider, or an Okta custom authorization server with a configured rotation cadence), confirm that your rotation policy publishes new keys ahead of first use.

<Warning>
  In `inline` mode there is no automatic key refresh. When your identity provider rotates its signing keys, you must update the issuer configuration with the new JWKS or all token exchanges will fail signature verification.
</Warning>


---
title: Workload Identity Federation
url: https://platform.claude.com/docs/en/manage-claude/workload-identity-federation
description: Authenticate workloads to the Claude API with short-lived identity tokens from your own identity provider instead of long-lived static API keys.
---

Workload Identity Federation (WIF) lets your workloads authenticate to the Claude API with short-lived OpenID Connect (OIDC) tokens instead of long-lived `sk-ant-...` API keys. The tokens come from an identity provider (IdP) you already operate: AWS IAM, Google Cloud, or any standards-compliant OIDC issuer such as GitHub Actions, Kubernetes, SPIFFE, Microsoft Entra ID, or Okta.

Your workload presents a signed JWT from your identity provider. Anthropic validates it against trust rules you configure in the Claude Console and returns a short-lived Anthropic access token bound to a service account in your organization. There are no static secrets to mint, store in CI, rotate, or leak.

Workload Identity Federation strengthens your security posture by replacing static API keys with tokens that expire in minutes rather than never. It is not a complete security story on its own: federated authentication is only as strong as the upstream identity provider that signs the JWT. Pair Workload Identity Federation with the controls your IdP already supports (workload identity binding, conditional access, audit logging) for defense in depth.


## Concepts

Source: https://platform.claude.com/llms-full.txt#concepts

You configure three resources in the Claude Console before any workload can federate. Together they express "tokens signed by issuer X, with claims that look like Y, may act as service account Z."

### Service accounts

A **service account** (`svac_...`) is a named, non-human identity inside your Anthropic organization. It is the principal that a [service account key](https://platform.claude.com/docs/en/manage-claude/authentication#key-types) or a federated token acts as. Service accounts live at the organization level and become active in a workspace when you add them as members of that workspace. At exchange time, Anthropic checks that the federation rule's workspace matches one of the service account's workspace memberships; the minted token then follows that workspace's rate limits and usage attribution, the same as an API key. Unlike a human user, a service account has no email, no password, and no Console login. Every service account is implicitly a member of your organization's default workspace; add explicit memberships for any other workspace it should act in. To let an all-workspaces service account key act in a workspace, add the service account to that workspace.

The key distinction versus a workspace API key: a workspace API key *is* a credential, while a service account *has* credentials. You can more easily audit which workloads acted as which service account.

### Federation issuers

A **federation issuer** (`fdis_...`) registers an OIDC identity provider with your organization. Registering an issuer tells Anthropic "JWTs signed by this provider may assert workload identity for my org."

An issuer has two pieces of configuration:

* **Issuer URL:** The exact `iss` claim value that appears in the provider's JWTs, for example `https://token.actions.githubusercontent.com` or `https://oidc.eks.us-west-2.amazonaws.com/id/EXAMPLE`.
* **JWKS source:** How Anthropic fetches the public keys to verify JWT signatures. Use `discovery` (the default) for any provider that serves `/.well-known/openid-configuration` at its issuer URL. Use `explicit_url` to point at a JWKS endpoint directly, or `inline` to upload the key set for issuers that are not reachable from the public internet (for example, a private Kubernetes cluster).

Issuer and JWKS URLs must be `https`, on port 443, and use a public DNS hostname that resolves to public IP addresses; IP literals are not accepted. These constraints apply only to URLs Anthropic fetches; in `explicit_url` and `inline` modes the `issuer_url` is compared as a string and may reference an internal hostname.

You typically register one issuer per environment: your production EKS cluster, your staging cluster, and GitHub Actions are three separate issuers.

### Federation rules

A **federation rule** (`fdrl_...`) is the bridge between an issuer and a service account: "when a JWT from issuer X has claims that look like Y, mint a token for service account Z with scope S."

A rule defines match conditions, a target, and the authorization scope and token lifetime that apply when the rule matches:

* **Match:** The conditions an incoming JWT must satisfy. You can match on a `subject_prefix` (for example, `system:serviceaccount:prod:worker`, or with a trailing `*` for a prefix match), an exact `audience`, a map of exact claim values, a [CEL](https://cel.dev/) `condition` expression for complex logic, or any combination. At least one of `subject_prefix`, `claims`, or `condition` must be set, and all configured matchers must pass for the JWT to be accepted.
* **Target:** The service account the matched JWT maps to.
* **Authorization:** The OAuth `scope` granted on the minted token. The default is `workspace:developer`, which grants the same access as a workspace API key. Some products lock the scope when you create a rule from their flow; for example, the [MCP tunnels](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview) create-tunnel modal creates rules scoped to `workspace:manage_tunnels`. See [OAuth scopes](https://platform.claude.com/docs/en/manage-claude/wif-reference#oauth-scopes). The rule also sets `token_lifetime_seconds` (60 to 86400, default 3600).

A single issuer can have many rules: one per team, namespace, or permission level. Rules are evaluated by ID: the client specifies which rule to use in the exchange request, and Anthropic verifies the JWT satisfies that rule's match criteria. There is no implicit rule search.


## How it works

Source: https://platform.claude.com/llms-full.txt#how-it-works-11

1. **Your IdP issues a JWT to the workload.** On most platforms this is ambient: a Kubernetes projected service-account token, the Google Cloud metadata server, Azure IMDS, or the GitHub Actions OIDC endpoint. The JWT's `iss` claim identifies the provider, and its `sub` and other claims identify the specific workload.
2. **The SDK exchanges the JWT for an Anthropic access token.** The SDK posts the JWT to `POST /v1/oauth/token` using the [RFC 7523](https://www.rfc-editor.org/rfc/rfc7523) `jwt-bearer` grant. Anthropic verifies the JWT against the issuer's JWKS and the federation rule's match conditions, then returns a short-lived `sk-ant-oat01-...` token that acts on behalf of the rule's target service account.
3. **The SDK sends the token on every request and refreshes it before it expires.** Your application code constructs the client with no `api_key` and calls the API as usual. The SDK re-runs the exchange before the token expires.


## Set up federation

Source: https://platform.claude.com/llms-full.txt#set-up-federation

You need the admin, owner, or primary owner role in your Anthropic organization, an OIDC-capable identity provider with a reachable JWKS endpoint (or a JWKS document you can paste, for air-gapped clusters), and a workload that can obtain an identity token from that provider.

The **Connect workload** wizard creates all three resources (the issuer, the service account, and the federation rule) in one guided flow, then verifies the connection end to end.

<Steps>
  <Step title="Open Connect workload">
    In the Claude Console, go to **Settings → Workload identity** and select **Connect workload**.
  </Step>

  <Step title="Choose your provider">
    Select the tile for your identity provider: GitHub Actions, AWS, Google Cloud, Microsoft Entra ID, or Kubernetes. Each tile prefills the issuer URL pattern and the match fields that provider's JWTs support. For any other standards-compliant provider (such as SPIFFE or Okta), select **Custom OIDC**.
  </Step>

  <Step title="Fill in the guided fields">
    The wizard walks you through the provider-specific fields: the issuer configuration, the match conditions for incoming JWTs, and names for the service account and federation rule it creates. The wizard prefills `oauth_scope=workspace:developer` and `token_lifetime_seconds=600` (the API default when `token_lifetime_seconds` is omitted is 3600); adjust these if your workload needs a different scope or lifetime.
  </Step>

  <Step title="Verify the issuer">
    Optionally select **Verify issuer** to dry-run the issuer configuration before anything is created. Verification confirms Anthropic can fetch and parse the JWKS from the URLs you entered, which catches reachability and configuration mistakes early.
  </Step>

  <Step title="Test the connection">
    The wizard creates the issuer, service account, and federation rule, then listens for a successful token exchange for 15 minutes. Trigger an exchange from your workload within that window (see [Authenticate from your workload](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#authenticate-from-your-workload)) to confirm the setup works. If the window elapses, the resources persist; you can re-run the test from the federation rule's detail page. Note the rule's ID (`fdrl_...`) and the service account ID (`svac_...`) the wizard creates: your workload passes both, along with your organization ID (and your workspace ID when the rule covers more than one workspace), in every token-exchange request.
  </Step>
</Steps>

To manage these resources programmatically, see [Manage WIF with the Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api) for the curl walkthrough, or see the [Service accounts API reference](https://platform.claude.com/docs/en/api/admin/service_accounts), [Federation issuers API reference](https://platform.claude.com/docs/en/api/admin/federation_issuers), and [Federation rules API reference](https://platform.claude.com/docs/en/api/admin/federation_rules) for complete parameter details and response schemas.


## Authenticate from your workload

Source: https://platform.claude.com/llms-full.txt#authenticate-from-your-workload

With federation configured, your workload exchanges its IdP-issued JWT for an Anthropic token at runtime. The SDKs handle the exchange and refresh loop for you. The cURL tab shows the underlying HTTP exchange for shell scripts, debugging, or languages without SDK support.

### Construct the SDK client

You can construct the client with explicit credentials or with no arguments. With no arguments, the SDK resolves credentials from environment variables or the active profile, as described under [Credential precedence](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#credential-precedence). The zero-argument form is the recommended pattern for production workloads: ship the same container image everywhere and inject `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`, `ANTHROPIC_SERVICE_ACCOUNT_ID`, `ANTHROPIC_WORKSPACE_ID`, and `ANTHROPIC_IDENTITY_TOKEN_FILE` per environment.

<CodeGroup>
  ```bash cURL
  # 1. Acquire your IdP's JWT (platform-specific; see the per-provider guides).
  JWT=$(cat /var/run/secrets/anthropic.com/token)

  # 2. Exchange it for a short-lived Anthropic access token.
  RESPONSE=$(curl -sS https://api.anthropic.com/v1/oauth/token \
    -H "content-type: application/json" \
    -d @- <<JSON
  {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": "$JWT",
    "federation_rule_id": "fdrl_...",
    "organization_id": "00000000-0000-0000-0000-000000000000",
    "service_account_id": "svac_...",
    "workspace_id": "wrkspc_..."
  }
  JSON
  )

  ACCESS_TOKEN=$(jq -r .access_token <<<"$RESPONSE")
  EXPIRES_IN=$(jq -r .expires_in <<<"$RESPONSE")  # seconds; re-exchange before this elapses

  # 3. Call the API with the access token in the Authorization: Bearer header.
  curl -sS https://api.anthropic.com/v1/messages \
    -H "authorization: Bearer $ACCESS_TOKEN" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d @- <<'JSON' | jq -r '.content[] | select(.type == "text") | .text'
  {
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello, Claude"}]
  }
  JSON

python Python
  from anthropic import Anthropic, WorkloadIdentityCredentials, IdentityTokenFile

  client = Anthropic(
      credentials=WorkloadIdentityCredentials(
          identity_token_provider=IdentityTokenFile(
              "/var/run/secrets/anthropic.com/token"
          ),
          federation_rule_id="fdrl_...",
          organization_id="00000000-0000-0000-0000-000000000000",
          service_account_id="svac_...",
          workspace_id="wrkspc_...",
      ),
  )

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
  )
  print(next(block.text for block in message.content if block.type == "text"))

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";
  import { oidcFederationProvider } from "@anthropic-ai/sdk/lib/credentials/oidc-federation";
  import { identityTokenFromFile } from "@anthropic-ai/sdk/lib/credentials/identity-token";

  const client = new Anthropic({
    credentials: oidcFederationProvider({
      identityTokenProvider: identityTokenFromFile("/var/run/secrets/anthropic.com/token"),
      federationRuleId: "fdrl_...",
      organizationId: "00000000-0000-0000-0000-000000000000",
      serviceAccountId: "svac_...",
      workspaceId: "wrkspc_...",
      baseURL: "https://api.anthropic.com",
      fetch
    })
  });

  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }]
  });
  for (const block of message.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

go Go
  client := anthropic.NewClient(
  	option.WithFederationTokenProvider(
  		option.IdentityTokenFile("/var/run/secrets/anthropic.com/token"),
  		option.FederationOptions{
  			FederationRuleID: "fdrl_...",
  			OrganizationID:   "00000000-0000-0000-0000-000000000000",
  			ServiceAccountID: "svac_...",
  			WorkspaceID:      "wrkspc_...",
  		},
  	),
  )

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, Claude")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  for _, block := range message.Content {
  	if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  		fmt.Println(textBlock.Text)
  		break
  	}
  }

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.config.AuthenticationConfig;
  import com.anthropic.config.AuthenticationType;
  import com.anthropic.config.IdentityTokenConfig;
  import com.anthropic.config.InMemoryProfileConfigProvider;
  import com.anthropic.config.ProfileConfig;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.builder()
              .fromEnv()
              .configurationProvider(InMemoryProfileConfigProvider.of(ProfileConfig.builder()
                      .organizationId("00000000-0000-0000-0000-000000000000")
                      .workspaceId("wrkspc_...")
                      .authentication(AuthenticationConfig.builder()
                              .type(AuthenticationType.OIDC_FEDERATION)
                              .federationRuleId("fdrl_...")
                              .serviceAccountId("svac_...")
                              .identityToken(IdentityTokenConfig.builder()
                                      .source("file")
                                      .path("/var/run/secrets/anthropic.com/token")
                                      .build())
                              .build())
                      .build()))
              .build();

      var message = client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024)
              .addUserMessage("Hello, Claude")
              .build());

      IO.println(message.content());
  }

csharp C#
  using Anthropic.Credentials;
  // ...

  var credentials = new WorkloadIdentityCredentials(new WorkloadIdentityOptions
  {
      FederationRuleId = "fdrl_...",
      OrganizationId = "00000000-0000-0000-0000-000000000000",
      ServiceAccountId = "svac_...",
      WorkspaceId = "wrkspc_...",
      IdentityTokenProvider = new FileIdentityTokenProvider("/var/run/secrets/anthropic.com/token"),
  });
  using var client = new AnthropicClient(new ClientOptions { Credentials = credentials });

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello, Claude" }],
  });
  foreach (var block in message.Content)
  {
      if (block.Value is TextBlock textBlock)
      {
          Console.WriteLine(textBlock.Text);
      }
  }

php PHP
  use Anthropic\Client;
  use Anthropic\Lib\Credentials\CredentialResult;
  use Anthropic\Lib\Credentials\IdentityTokenFile;
  use Anthropic\Lib\Credentials\TokenCache;
  use Anthropic\Lib\Credentials\WorkloadIdentityCredentials;

  $client = new Client(credentials: new CredentialResult(
      provider: new TokenCache(
          new WorkloadIdentityCredentials(
              identityProvider: new IdentityTokenFile('/var/run/secrets/anthropic.com/token'),
              federationRuleId: 'fdrl_...',
              organizationId: '00000000-0000-0000-0000-000000000000',
              serviceAccountId: 'svac_...',
              workspaceId: 'wrkspc_...',
          ),
      ),
  ));

  $message = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
  );

  $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
  echo $textBlock->text . PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new(
    credentials: Anthropic::Credentials::WorkloadIdentity.new(
      identity_token_provider: Anthropic::Credentials::IdentityTokenFile.new(
        "/var/run/secrets/anthropic.com/token"
      ),
      federation_rule_id: "fdrl_...",
      organization_id: "00000000-0000-0000-0000-000000000000",
      service_account_id: "svac_...",
      workspace_id: "wrkspc_..."
    )
  )

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}]
  )

  puts message.content.find { it.type == :text }.text
  ```
</CodeGroup>

The token-exchange response follows [RFC 6749 §5.1](https://www.rfc-editor.org/rfc/rfc6749#section-5.1). See [Token exchange response](https://platform.claude.com/docs/en/manage-claude/wif-reference#token-exchange-response) for the field reference.


## Credential precedence

Source: https://platform.claude.com/llms-full.txt#credential-precedence

Every SDK resolves credentials in the same five-tier order: constructor arguments, then `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN`, then an explicit `ANTHROPIC_PROFILE`, then the federation environment variables, then the implicit active profile. The first source that yields a credential wins.

<Warning>
  `ANTHROPIC_API_KEY` sits above the federation tiers, so a leftover key in the environment silently shadows federation. When migrating a workload from API keys to Workload Identity Federation, confirm `ANTHROPIC_API_KEY` is unset everywhere that workload runs (container env, CI secrets, shell profiles). The CLI's [`ant auth status`](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/authentication#check-authentication-status) command reports which source won.
</Warning>

For the full precedence table, the per-tier semantics, and the profile file schema, see [Credential precedence in the WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference#credential-precedence).


## Migrate from API keys

Source: https://platform.claude.com/llms-full.txt#migrate-from-api-keys

To switch an existing workload from a static API key to federation without downtime:

1. **Configure federation in parallel.** Complete the [setup walkthrough](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#set-up-federation) and confirm the federation rule matches your workload's token. Leave the existing `ANTHROPIC_API_KEY` in place for now.
2. **Smoke-test which credential wins.** Run `ant auth status` from inside the workload (or inspect SDK debug logs). Because `ANTHROPIC_API_KEY` sits above the federation tiers in the precedence chain, the API key still wins at this stage.
3. **Unset `ANTHROPIC_API_KEY` everywhere it is injected.** Remove it from CI secrets, container environment, and shell profiles (see the preceding warning). Re-run `ant auth status` and confirm the federation source is now selected.
4. **Delete the API key.** Once the workload is running on the federated token, delete the key in the Claude Console under **Settings → API keys**.


## Token lifetime and refresh

Source: https://platform.claude.com/llms-full.txt#token-lifetime-and-refresh

The minted Anthropic token's lifetime is the lesser of (a) the rule's `token_lifetime_seconds` (default 3,600 seconds) and (b) twice the remaining lifetime of the IdP JWT you presented. The result is never less than 60 seconds. The second bound prevents an Anthropic token from outliving the upstream identity it was derived from by more than a small margin.

The SDKs cache the token and refresh it on a two-tier schedule modeled on `botocore`:

* **Advisory refresh** at expiry minus 120 seconds. The SDK attempts a new exchange. If the token endpoint is unreachable, the SDK continues serving the cached token, which is still valid for roughly 90 more seconds.
* **Mandatory refresh** at expiry minus 30 seconds. A failed exchange at this point raises an error. The cached token is too close to expiry to be safe.

Because the SDK re-reads `ANTHROPIC_IDENTITY_TOKEN_FILE` on every exchange, it transparently picks up rotated projected tokens (Kubernetes service-account tokens, for example, rotate well before their `exp`).

By default, identity tokens that carry a `jti` claim are single-use: each exchange must present a JWT that has not been exchanged before, and re-presenting one fails with the reason `jti_reused` on the [authentication history page](https://platform.claude.com/settings/workload-identity-federation?tab=history). If your workload fetches its own tokens from your identity provider, mint a fresh JWT for each exchange instead of reusing a cached one (retry loops are the common culprit). The same applies to a token read from `ANTHROPIC_IDENTITY_TOKEN_FILE`: the SDK re-reads the file on every exchange, so the file must hold a new token before each refresh. A refresh that re-reads an unrotated token, or a restarted process that re-presents a token it already exchanged, is rejected the same way. Rotating the token well within the minted token's lifetime keeps the file ahead of the refresh schedule; if your token source cannot rotate that often, you can disable `check_jti` for that issuer as a last resort (this removes replay protection for every rule on the issuer). See [JWT verification](https://platform.claude.com/docs/en/manage-claude/wif-reference#jwt-verification) for details.


## Identity providers

Source: https://platform.claude.com/llms-full.txt#identity-providers

Each guide covers where the JWT comes from on that platform, what its claims look like, and the issuer and rule configuration to register.

<CardGroup cols={3}>
  <Card title="AWS" icon="cloud" href="https://platform.claude.com/docs/en/manage-claude/wif-providers/aws">
    STS web identity tokens, or EKS IRSA projected tokens.
  </Card>

  <Card title="Google Cloud" icon="cloud" href="https://platform.claude.com/docs/en/manage-claude/wif-providers/gcp">
    Google-signed identity tokens from the metadata server.
  </Card>

  <Card title="Microsoft Entra ID" icon="cloud" href="https://platform.claude.com/docs/en/manage-claude/wif-providers/azure">
    Managed Identity (IMDS) and Entra Workload ID on AKS.
  </Card>

  <Card title="GitHub Actions" icon="github-logo" href="https://platform.claude.com/docs/en/manage-claude/wif-providers/github-actions">
    Keyless CI authentication with the Actions OIDC token.
  </Card>

  <Card title="Kubernetes" icon="cube" href="https://platform.claude.com/docs/en/manage-claude/wif-providers/kubernetes">
    Self-managed and on-premises clusters using projected service-account tokens.
  </Card>

  <Card title="SPIFFE" icon="fingerprint" href="https://platform.claude.com/docs/en/manage-claude/wif-providers/spiffe">
    Workloads with SPIFFE JWT-SVIDs from SPIRE or another conformant issuer.
  </Card>

  <Card title="Okta" icon="lock" href="https://platform.claude.com/docs/en/manage-claude/wif-providers/okta">
    Okta service applications using client-credentials flow.
  </Card>
</CardGroup>


## See also

Source: https://platform.claude.com/llms-full.txt#see-also-6

* [Manage WIF with the Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api): create issuers, service accounts, and rules from infrastructure as code
* [WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference): environment variables, profile file schema, validation rules, and error codes
* [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication): all authentication options across the Anthropic SDKs
* [Admin API reference](https://platform.claude.com/docs/en/api/admin): generated request and response schemas for every Admin API endpoint


### Authentication > Identity providers

---
title: Use WIF with AWS
url: https://platform.claude.com/docs/en/manage-claude/wif-providers/aws
description: Authenticate AWS workloads on Lambda, EC2, ECS, or EKS to the Claude API with Workload Identity Federation and STS-issued identity tokens.
---

AWS workloads can authenticate to the Claude API without static API keys by exchanging an AWS-signed OIDC identity token. The recommended path calls the AWS STS [`GetWebIdentityToken`](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetWebIdentityToken.html) API, which works anywhere the workload has AWS credentials: Lambda, EC2, ECS, and EKS. EKS workloads can alternatively use the [Kubernetes projected-token path](https://platform.claude.com/docs/en/manage-claude/wif-providers/aws#use-eks-projected-service-account-tokens), which has fewer configuration steps but only works inside a pod.

This guide shows both paths. For the underlying concepts (service accounts, federation issuers, and federation rules), see [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation).


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-10

* Familiarity with [WIF concepts](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#concepts): service accounts, federation issuers, and federation rules.
* An AWS workload (EKS pod, ECS task, Lambda function, or EC2 instance) with an attached IAM role.
* The `aws` CLI or an AWS SDK available in the workload.
* Permission to create service accounts, federation issuers, and federation rules in the Claude Console for your Anthropic organization.


## Use STS web identity tokens (recommended)

Source: https://platform.claude.com/llms-full.txt#use-sts-web-identity-tokens-recommended

The AWS STS `GetWebIdentityToken` API returns an OIDC token signed by AWS that asserts the caller's IAM identity. Because it uses the workload's ambient AWS credentials, the same integration covers Lambda, EC2, ECS, and EKS.

### Configure AWS

<Steps>
  <Step title="Enable outbound web identity federation for the account">
    This is an account-level flag, off by default. In the AWS console, open **IAM**, choose **Account settings**, and enable **Outbound web identity federation**. To enable it programmatically:

If this is not enabled, calls to `GetWebIdentityToken` fail with `OutboundWebIdentityFederationDisabledException`.
  </Step>

  <Step title="Grant the workload's IAM role permission to call the API">
    Attach this policy to the IAM role that your Lambda function, EC2 instance, or ECS task runs as:

</Step>

  <Step title="Find your account's STS issuer URL">
    After enabling outbound federation, the **IAM > Account settings** page shows a **Get Token Issuer URL** field with a value of the form `https://<uuid>.tokens.sts.global.api.aws`. This URL is unique to your AWS account; copy it for the next step. To retrieve it programmatically:

</Step>
</Steps>

### Configure Anthropic

In the Claude Console, open **Settings → Workload identity**, click **Connect workload**, and select the **AWS** tile. The wizard walks you through registering the issuer, creating a service account, and creating a federation rule.

The wizard creates these resources for you. Use the following values whether you enter them in the wizard or send them to the [Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api):

**Federation issuer:** Register the per-account STS issuer URL you copied in the prior step. It exposes a public JWKS endpoint, so use discovery mode.

**Federation rule:** Match the audience you pass to `GetWebIdentityToken` and the calling role's IAM role ARN in the `sub` claim. The `sub` value is the IAM role ARN of the workload that called the API, in the form `arn:aws:iam::<account>:role/<role-name>`. The token also carries an `https://sts.amazonaws.com/` claim with `aws_account`, `org_id`, `principal_id`, and any `request_tags` you passed; you can match on those with the rule's `claims` map or a CEL `condition` for finer control.

Be as specific as the workload allows. Match the exact role ARN, and only broaden `subject_prefix` (for example, to `arn:aws:iam::123456789012:role/*`) if multiple IAM roles should map to the same Anthropic service account.

### Acquire and use the token

Call `GetWebIdentityToken` with `https://api.anthropic.com` as the audience, then pass the result to the SDK's federation credentials. The token provider is a callable, so the SDK re-invokes STS on each refresh.

<Note>
  `GetWebIdentityToken` is available only on regional STS endpoints. If you receive `'STS' object has no attribute 'get_web_identity_token'` or a similar error, pin your STS client to a region (for example, `boto3.client("sts", region_name="us-east-1")`) and ensure your AWS SDK is recent enough to include the API.
</Note>

<CodeGroup>
  ```bash cURL
  JWT=$(aws sts get-web-identity-token \
    --region us-east-1 \
    --audience "https://api.anthropic.com" \
    --signing-algorithm RS256 \
    --duration-seconds 900 \
    --query WebIdentityToken --output text)

  RESPONSE=$(curl -sS https://api.anthropic.com/v1/oauth/token \
    -H "content-type: application/json" \
    --data @- <<JSON
  {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": "$JWT",
    "federation_rule_id": "$ANTHROPIC_FEDERATION_RULE_ID",
    "organization_id": "$ANTHROPIC_ORGANIZATION_ID",
    "service_account_id": "$ANTHROPIC_SERVICE_ACCOUNT_ID",
    "workspace_id": "$ANTHROPIC_WORKSPACE_ID"
  }
  JSON
  )

  ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r .access_token)

  curl https://api.anthropic.com/v1/messages \
    -H "authorization: Bearer $ACCESS_TOKEN" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello from AWS"}]
    }' | jq -r '.content[] | select(.type == "text") | .text'

python Python
  import os

  import anthropic
  import boto3
  from anthropic import WorkloadIdentityCredentials


  def get_sts_web_identity_token() -> str:
      sts = boto3.client("sts", region_name="us-east-1")
      resp = sts.get_web_identity_token(
          Audience=["https://api.anthropic.com"],
          SigningAlgorithm="RS256",
          DurationSeconds=900,
      )
      return resp["WebIdentityToken"]


  client = anthropic.Anthropic(
      credentials=WorkloadIdentityCredentials(
          identity_token_provider=get_sts_web_identity_token,
          federation_rule_id=os.environ["ANTHROPIC_FEDERATION_RULE_ID"],
          organization_id=os.environ["ANTHROPIC_ORGANIZATION_ID"],
          service_account_id=os.environ["ANTHROPIC_SERVICE_ACCOUNT_ID"],
          workspace_id=os.environ.get("ANTHROPIC_WORKSPACE_ID"),
      ),
  )

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello from AWS"}],
  )
  print(next(block.text for block in message.content if block.type == "text"))

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";
  import { oidcFederationProvider } from "@anthropic-ai/sdk/lib/credentials/oidc-federation";
  import { STSClient, GetWebIdentityTokenCommand } from "@aws-sdk/client-sts";

  const sts = new STSClient({ region: "us-east-1" });

  async function getStsWebIdentityToken(): Promise<string> {
    const out = await sts.send(
      new GetWebIdentityTokenCommand({
        Audience: ["https://api.anthropic.com"],
        SigningAlgorithm: "RS256",
        DurationSeconds: 900
      })
    );
    return out.WebIdentityToken!;
  }

  const client = new Anthropic({
    credentials: oidcFederationProvider({
      identityTokenProvider: getStsWebIdentityToken,
      federationRuleId: process.env.ANTHROPIC_FEDERATION_RULE_ID!,
      organizationId: process.env.ANTHROPIC_ORGANIZATION_ID!,
      serviceAccountId: process.env.ANTHROPIC_SERVICE_ACCOUNT_ID,
      workspaceId: process.env.ANTHROPIC_WORKSPACE_ID,
      baseURL: "https://api.anthropic.com",
      fetch
    })
  });

  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello from AWS" }]
  });
  for (const block of message.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

go Go
  ctx := context.TODO()
  cfg, err := config.LoadDefaultConfig(ctx, config.WithRegion("us-east-1"))
  if err != nil {
  	panic(err)
  }
  stsClient := sts.NewFromConfig(cfg)

  getStsToken := option.IdentityTokenFunc(func(ctx context.Context) (string, error) {
  	out, err := stsClient.GetWebIdentityToken(ctx, &sts.GetWebIdentityTokenInput{
  		Audience:         []string{"https://api.anthropic.com"},
  		SigningAlgorithm: "RS256",
  		DurationSeconds:  aws.Int32(900),
  	})
  	if err != nil {
  		return "", err
  	}
  	return *out.WebIdentityToken, nil
  })

  client := anthropic.NewClient(
  	option.WithFederationTokenProvider(getStsToken, option.FederationOptions{
  		FederationRuleID: os.Getenv("ANTHROPIC_FEDERATION_RULE_ID"),
  		OrganizationID:   os.Getenv("ANTHROPIC_ORGANIZATION_ID"),
  		ServiceAccountID: os.Getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"),
  		WorkspaceID:      os.Getenv("ANTHROPIC_WORKSPACE_ID"),
  	}),
  )

  message, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello from AWS")),
  	},
  })
  if err != nil {
  	panic(err)
  }
  for _, block := range message.Content {
  	if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  		fmt.Println(textBlock.Text)
  		break
  	}
  }

java Java
  StsClient sts = StsClient.builder().region(Region.US_EAST_1).build();

  IdentityTokenProvider getStsToken = () -> sts.getWebIdentityToken(
                  GetWebIdentityTokenRequest.builder()
                          .audience("https://api.anthropic.com")
                          .signingAlgorithm("RS256")
                          .durationSeconds(900)
                          .build())
          .webIdentityToken();

  AnthropicClient client = AnthropicOkHttpClient.builder()
          .federationTokenProvider(
                  getStsToken,
                  System.getenv("ANTHROPIC_FEDERATION_RULE_ID"),
                  System.getenv("ANTHROPIC_ORGANIZATION_ID"),
                  System.getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"))
          .build();

  var message = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .addUserMessage("Hello from AWS")
          .build());

  IO.println(message.content());

csharp C#
  using Amazon.SecurityToken;
  using Amazon.SecurityToken.Model;
  // ...
  using Anthropic.Credentials;
  // ...

  var credentials = new WorkloadIdentityCredentials(new WorkloadIdentityOptions
  {
      FederationRuleId = Environment.GetEnvironmentVariable("ANTHROPIC_FEDERATION_RULE_ID")!,
      OrganizationId = Environment.GetEnvironmentVariable("ANTHROPIC_ORGANIZATION_ID"),
      ServiceAccountId = Environment.GetEnvironmentVariable("ANTHROPIC_SERVICE_ACCOUNT_ID"),
      WorkspaceId = Environment.GetEnvironmentVariable("ANTHROPIC_WORKSPACE_ID"),
      IdentityTokenProvider = new StsTokenProvider(),
  });
  using var client = new AnthropicClient(new ClientOptions { Credentials = credentials });

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello from AWS" }],
  });
  foreach (var block in message.Content)
  {
      if (block.Value is TextBlock textBlock)
      {
          Console.WriteLine(textBlock.Text);
      }
  }

  class StsTokenProvider : IIdentityTokenProvider
  {
      private readonly AmazonSecurityTokenServiceClient _sts = new(Amazon.RegionEndpoint.USEast1);

      public async Task<string> GetIdentityTokenAsync(CancellationToken ct = default)
      {
          var resp = await _sts.GetWebIdentityTokenAsync(new GetWebIdentityTokenRequest
          {
              Audience = ["https://api.anthropic.com"],
              SigningAlgorithm = "RS256",
              DurationSeconds = 900,
          }, ct);
          return resp.WebIdentityToken;
      }
  }

bash CLI
  TOKEN_FILE=$(mktemp)
  aws sts get-web-identity-token \
    --region us-east-1 \
    --audience "https://api.anthropic.com" \
    --signing-algorithm RS256 \
    --duration-seconds 900 \
    --query WebIdentityToken --output text > "$TOKEN_FILE"

  export ANTHROPIC_IDENTITY_TOKEN_FILE="$TOKEN_FILE"
  # ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID, and
  # ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID are read from the environment
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello from AWS"}'

php PHP
  use Anthropic\Client;
  use Anthropic\Credentials\WorkloadIdentityCredentials;
  use Aws\Sts\StsClient;

  $sts = new StsClient(['region' => 'us-east-1', 'version' => 'latest']);
  $client = new Client(credentials: new WorkloadIdentityCredentials(
      identityTokenProvider: fn() => $sts->getWebIdentityToken([
          'Audience' => ['https://api.anthropic.com'],
          'SigningAlgorithm' => 'RS256',
          'DurationSeconds' => 900,
      ])['WebIdentityToken'],
      federationRuleId: getenv('ANTHROPIC_FEDERATION_RULE_ID'),
      organizationId: getenv('ANTHROPIC_ORGANIZATION_ID'),
      serviceAccountId: getenv('ANTHROPIC_SERVICE_ACCOUNT_ID'),
      workspaceId: getenv('ANTHROPIC_WORKSPACE_ID') ?: null,
  ));

  $message = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello from AWS']],
  );
  $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
  echo $textBlock->text, PHP_EOL;

ruby Ruby
  require "anthropic"
  require "aws-sdk-sts"

  sts = Aws::STS::Client.new(region: "us-east-1")
  client = Anthropic::Client.new(
    credentials: Anthropic::WorkloadIdentityCredentials.new(
      identity_token_provider: -> {
        sts.get_web_identity_token(
          audience: ["https://api.anthropic.com"],
          signing_algorithm: "RS256",
          duration_seconds: 900,
        ).web_identity_token
      },
      federation_rule_id: ENV.fetch("ANTHROPIC_FEDERATION_RULE_ID"),
      organization_id: ENV.fetch("ANTHROPIC_ORGANIZATION_ID"),
      service_account_id: ENV.fetch("ANTHROPIC_SERVICE_ACCOUNT_ID"),
      workspace_id: ENV["ANTHROPIC_WORKSPACE_ID"],
    ),
  )

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello from AWS"}]
  )
  puts message.content.find { it.type == :text }.text

bash cURL
JWT=$(aws sts get-web-identity-token \
  --region us-east-1 \
  --audience "https://api.anthropic.com" \
  --signing-algorithm RS256 \
  --duration-seconds 900 \
  --query WebIdentityToken --output text)

curl -sS https://api.anthropic.com/v1/oauth/token \
  -H "content-type: application/json" \
  -d "{
    \"grant_type\": \"urn:ietf:params:oauth:grant-type:jwt-bearer\",
    \"assertion\": \"$JWT\",
    \"federation_rule_id\": \"fdrl_...\",
    \"organization_id\": \"00000000-0000-0000-0000-000000000000\",
    \"service_account_id\": \"svac_...\",
    \"workspace_id\": \"wrkspc_...\"
  }" | jq
```

A successful exchange returns an `access_token` beginning with `sk-ant-oat01-` and an `expires_in` value in seconds. If the exchange fails with the opaque `401` `authentication_error` response (message `Authentication failed`), check the [authentication history page](https://platform.claude.com/settings/workload-identity-federation?tab=history) for the deny reason and see [Troubleshoot a failed exchange](https://platform.claude.com/docs/en/manage-claude/wif-reference#troubleshoot-a-failed-exchange); the most common AWS-side cause is an `iss` mismatch (the per-account STS issuer URL must match the registered `issuer_url` exactly).
