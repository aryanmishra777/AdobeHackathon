# platform.claude.com Documentation (Part 15 of 35)

## Available models

Source: https://platform.claude.com/llms-full.txt#available-models-2

The following models are available on Claude Platform on AWS:

| Model             | Model ID          |
| ----------------- | ----------------- |
| Claude Fable 5.1  | claude-fable-5-1  |
| Claude Fable 5    | claude-fable-5    |
| Claude Opus 5     | claude-opus-5     |
| Claude Opus 4.8   | claude-opus-4-8   |
| Claude Opus 4.7   | claude-opus-4-7   |
| Claude Opus 4.6   | claude-opus-4-6   |
| Claude Sonnet 5   | claude-sonnet-5   |
| Claude Sonnet 4.6 | claude-sonnet-4-6 |
| Claude Opus 4.5   | claude-opus-4-5   |
| Claude Sonnet 4.5 | claude-sonnet-4-5 |
| Claude Haiku 4.5  | claude-haiku-4-5  |

Model IDs are identical to the first-party Claude API. There are no Bedrock-style ARNs or `anthropic.` prefixes.

New models typically launch on Claude Platform on AWS the same day as the first-party Claude API.

<Tip>
  Upgrading to a newer Claude model? In Claude Code, run `/claude-api migrate` to apply model ID swaps and breaking parameter changes across your codebase. The skill detects which cloud platform your code targets and adjusts model ID formats and feature changes for that platform. See [Migrating to a newer Claude model](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill#migrating-to-a-newer-claude-model).
</Tip>


## Making requests

Source: https://platform.claude.com/llms-full.txt#making-requests

Claude Platform on AWS uses the same API endpoints as the first-party Claude API. The differences are the base URL, the authentication method, and a required `anthropic-workspace-id` header that identifies which [workspace](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#workspaces) the request targets.

Before running these examples, complete the steps in [Before making API calls](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#before-making-api-calls).

<CodeGroup>
  ```bash cURL
  # Replace us-west-2 with your AWS region in both the URL and --aws-sigv4
  # Omit the x-amz-security-token header if you use long-term IAM user credentials
  curl "https://aws-external-anthropic.us-west-2.api.aws/v1/messages" \
    --aws-sigv4 "aws:amz:us-west-2:aws-external-anthropic" \
    --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
    -H "x-amz-security-token: $AWS_SESSION_TOKEN" \
    -H "content-type: application/json" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-workspace-id: $ANTHROPIC_AWS_WORKSPACE_ID" \
    -d '{
      "model": "claude-sonnet-5",
      "max_tokens": 1024,
      "messages": [
        {"role": "user", "content": "Hello!"}
      ]
    }'

bash CLI
  # Replace us-west-2 with your AWS region
  # ant reads ANTHROPIC_API_KEY and sends it as x-api-key. Generate a key in the
  # AWS Console (see API key authentication).
  export ANTHROPIC_API_KEY="YOUR_AWS_API_KEY"

  ant messages create \
    --base-url https://aws-external-anthropic.us-west-2.api.aws \
    --workspace-id "$ANTHROPIC_AWS_WORKSPACE_ID" \
    --model claude-sonnet-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello!"}' \
    --transform content

python Python
  from anthropic import AnthropicAWS

  client = AnthropicAWS()

  message = client.messages.create(
      model="claude-sonnet-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello!"}],
  )
  print(message)

typescript TypeScript
  import AnthropicAws from "@anthropic-ai/aws-sdk";

  const client = new AnthropicAws();

  const message = await client.messages.create({
    model: "claude-sonnet-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello!" }]
  });
  console.log(message);

csharp C#
  using Anthropic;
  using Anthropic.Aws;

  var client = new AnthropicAwsClient();

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeSonnet5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello!" }]
  });

  Console.WriteLine(message);

go Go
  client, err := anthropicaws.NewClient(context.Background(), anthropicaws.ClientConfig{})
  if err != nil {
  	panic(err)
  }

  message, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeSonnet5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello!")),
  	},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Println(message)

java Java
  import com.anthropic.aws.backends.AwsBackend;
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.builder()
          .backend(AwsBackend.fromEnv())
          .build();

      Message message = client.messages().create(
          MessageCreateParams.builder()
              .model(Model.CLAUDE_SONNET_5)
              .maxTokens(1024)
              .addUserMessage("Hello!")
              .build()
      );

      IO.println(message);
  }

php PHP
  use Anthropic\Aws\Client;

  $client = new Client();

  $message = $client->messages->create(
      model: 'claude-sonnet-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello!']],
  );

  echo $message;

ruby Ruby
  require "anthropic"

  client = Anthropic::AWSClient.new

  message = client.messages.create(
    model: "claude-sonnet-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello!" }]
  )

  puts message
  ```
</CodeGroup>

The client reads `AWS_REGION` (or `AWS_DEFAULT_REGION`) and `ANTHROPIC_AWS_WORKSPACE_ID` from the environment. You can override either by passing `aws_region` / `awsRegion` or `workspace_id` / `workspaceId` to the constructor. Both region and workspace ID are required. The constructor raises an error if either cannot be resolved.

<Note>
  The `x-amz-security-token` header (cURL) is only required for temporary credentials such as IAM roles, SSO, or STS. Omit it when using long-term IAM user credentials. The SDK clients handle this automatically based on the credential source.
</Note>

The `--aws-sigv4` value follows the format `aws:amz:<region>:<service>`. The SigV4 service name is `aws-external-anthropic`, and the region must match the region in your endpoint URL. A mismatch in either produces a generic signature-rejection error rather than a specific diagnostic.

### Context window

Context-window sizes on Claude Platform on AWS are identical to the first-party Claude API. See [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) for per-model limits.


## Feature support

Source: https://platform.claude.com/llms-full.txt#feature-support-6

Claude Platform on AWS uses Claude API endpoints directly, which means you get full feature parity with the first-party Claude API (except where noted in the [feature limitations](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#features-not-supported)):

* **Feature access:** Because Anthropic operates both platforms, most new features and beta headers become available on Claude Platform on AWS without a separate integration step. See [feature limitations](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#features-not-supported) for exceptions.
* **Beta features:** Pass the standard `anthropic-beta` header to access beta features, just as you would with the Claude API.
* **Agent Skills:** Use pre-built and custom [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) with the same `container.skills` parameter as the Claude API. All pre-built Skills (PowerPoint, Excel, Word, PDF) work out of the box.
* **Code execution:** Run code in Anthropic's managed sandbox using the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool).
* **Tool use:** Computer use and all other [tool use capabilities](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) are available.
* **Extended thinking:** Enable extended thinking with the same parameters as the Claude API.
* **Streaming:** Full SSE streaming support for real-time responses.
* **Batch processing:** Submit batch requests for high-throughput workloads.
* **Prompt caching:** Cache tools, system prompts, and message history to reduce latency and cost. All prompt caching capabilities (5-minute TTL, 1-hour TTL, and automatic caching) are available.
* **Files API:** Upload and reference files across requests.
* **Customer-managed encryption keys (CMEK):** [CMEK](https://platform.claude.com/docs/en/manage-claude/cmek) is available with [AWS KMS](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms) keys only. Google Cloud KMS and Azure Key Vault keys cannot be registered. The key must be a single-region KMS key in the same AWS account and region as the workspace it is attached to, and its key policy must grant access to the `aws-external-anthropic.amazonaws.com` service principal; see [Set up CMEK on Claude Platform on AWS](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms#claude-platform-on-aws). Register and attach keys in the [Claude Console](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#using-the-claude-console); the external key endpoints are also available, authorized through [IAM actions](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#encryption-keys). There is no separate validation step: the key is implicitly validated when you attach it to a workspace (the attach call performs an encrypt/decrypt round), so a key policy problem surfaces at attach time rather than at registration.
* **Compliance API:** The [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) is available. Access is authorized through the AWS IAM [`ListComplianceActivities` action](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#compliance).

See the [comparison table](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#claude-platform-on-aws-vs-amazon-bedrock) for feature-availability differences from Amazon Bedrock.

### Claude Managed Agents

[Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) is available on Claude Platform on AWS, including [agents](https://platform.claude.com/docs/en/managed-agents/agent-setup), [environments](https://platform.claude.com/docs/en/managed-agents/environments), [sessions](https://platform.claude.com/docs/en/managed-agents/sessions), [credential vaults](https://platform.claude.com/docs/en/managed-agents/vaults), [memory stores](https://platform.claude.com/docs/en/managed-agents/memory), [webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks), [multiagent orchestration](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration), and [self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes).

Session behavior on Claude Platform on AWS differs from first-party Claude Managed Agents in two ways:

* **Autonomous-session reauthentication:** A session can run autonomously, without any [user events](https://platform.claude.com/docs/en/managed-agents/reference#event-types), for up to 6 hours. After 6 hours, the session requires reauthentication before it continues. To reauthenticate, send any user-role event to the session (see [Events and streaming](https://platform.claude.com/docs/en/managed-agents/events-and-streaming)). First-party Claude Managed Agents has no autonomous-session runtime limit.
* **[Memory stores on self-hosted environments](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores):** A session that runs on a self-hosted environment cannot attach memory stores; a session that includes one is rejected at creation. Sessions on cloud environments attach memory stores as usual. On first-party Claude Managed Agents, sessions on both cloud and self-hosted environments can attach memory stores.

### Features not supported

The following capabilities are not currently available on Claude Platform on AWS:

* **HIPAA readiness:** Anthropic's HIPAA-ready program is not available. See [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
* **Computer use and browser use toolsets:** `computer_toolset_20260801` and `browser_toolset_20260801` are not currently available on Claude Platform on AWS. The beta [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#earlier-tool-versions) tool versions remain available.

- **Admin API:** Workspace endpoints (create, get, list, update, and archive on `/v1/organizations/workspaces`) and external key endpoints (register, get, list, update, and delete on `/v1/organizations/external_keys`, for [CMEK](https://platform.claude.com/docs/en/manage-claude/cmek); keys are validated when attached to a workspace rather than through a validate endpoint) are available. Other Admin API endpoints (organization members, workspace members, invites, API keys, usage reports, cost reports, and rate limit reports) are not currently available. View usage and cost data in the [Claude Console](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#using-the-claude-console) instead. AWS IAM manages organization membership.
- **Workspace member management:** Adding or removing users from individual workspaces is not available. AWS IAM policies on workspace ARNs control access.
- **Claude Code workspace and Analytics API:** The Claude Code workspace with automatic rate limits is not available. Claude Code usage appears in the general usage view rather than a dedicated screen.
- **OAuth authentication:** Not supported. Use SigV4 or API key authentication.
- **Fast mode:** Not available on Claude Platform on AWS.
- **OpenAI-compatible API endpoints:** Not available on Claude Platform on AWS.
- **MCP tunnels:** Only MCP servers exposed over the public internet are supported.


## Data residency

Source: https://platform.claude.com/llms-full.txt#data-residency

Claude Platform on AWS supports the following inference geographies:

* **US:** Inference stays within US data centers. A 1.1x pricing multiplier applies.
* **Global:** Inference can route to any Anthropic-operated data center worldwide. Standard pricing applies.

<Note>
  The AWS region your workspace is bound to controls which gateway endpoint you call and where AWS-side resources (IAM, CloudTrail, billing) are scoped. It does not pin where model inference runs. To pin inference to a specific geography, set `inference_geo` on each request or configure a workspace default.
</Note>

Set the inference geography per request with the `inference_geo` parameter:

<Note>
  The `inference_geo` parameter is supported on Claude 4.6 and later models. Requests with `inference_geo` on Claude Opus 4.5, Claude Sonnet 4.5, or Claude Haiku 4.5 return a 400 error. See [Data residency](https://platform.claude.com/docs/en/manage-claude/data-residency) for model availability details.
</Note>

<CodeGroup>
  ```bash cURL
  # Replace us-west-2 with your AWS region in both the URL and --aws-sigv4
  # Omit the x-amz-security-token header if you use long-term IAM user credentials
  curl "https://aws-external-anthropic.us-west-2.api.aws/v1/messages" \
    --aws-sigv4 "aws:amz:us-west-2:aws-external-anthropic" \
    --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
    -H "x-amz-security-token: $AWS_SESSION_TOKEN" \
    -H "content-type: application/json" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-workspace-id: $ANTHROPIC_AWS_WORKSPACE_ID" \
    -d '{
      "model": "claude-sonnet-5",
      "max_tokens": 1024,
      "inference_geo": "us",
      "messages": [
        {"role": "user", "content": "Hello!"}
      ]
    }'

bash CLI
  # Replace us-west-2 with your AWS region
  # ant reads ANTHROPIC_API_KEY and sends it as x-api-key. Generate a key in the
  # AWS Console (see API key authentication).
  export ANTHROPIC_API_KEY="YOUR_AWS_API_KEY"

  ant messages create \
    --base-url https://aws-external-anthropic.us-west-2.api.aws \
    --workspace-id "$ANTHROPIC_AWS_WORKSPACE_ID" \
    --model claude-sonnet-5 \
    --max-tokens 1024 \
    --inference-geo us \
    --message '{role: user, content: "Hello!"}' \
    --transform content

python Python
  from anthropic import AnthropicAWS

  client = AnthropicAWS()
  message = client.messages.create(
      model="claude-sonnet-5",
      max_tokens=1024,
      inference_geo="us",
      messages=[{"role": "user", "content": "Hello!"}],
  )
  print(message)

typescript TypeScript
  import AnthropicAws from "@anthropic-ai/aws-sdk";
  const client = new AnthropicAws();
  const message = await client.messages.create({
    model: "claude-sonnet-5",
    max_tokens: 1024,
    inference_geo: "us",
    messages: [{ role: "user", content: "Hello!" }]
  });
  console.log(message);

csharp C#
  using Anthropic;
  using Anthropic.Aws;

  var client = new AnthropicAwsClient();

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeSonnet5,
      MaxTokens = 1024,
      InferenceGeo = "us",
      Messages = [new() { Role = Role.User, Content = "Hello!" }]
  });

  Console.WriteLine(message);

go Go
  client, err := anthropicaws.NewClient(context.Background(), anthropicaws.ClientConfig{})
  if err != nil {
  	panic(err)
  }

  message, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  	Model:        anthropic.ModelClaudeSonnet5,
  	MaxTokens:    1024,
  	InferenceGeo: anthropic.String("us"),
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello!")),
  	},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Println(message)

java Java
  import com.anthropic.aws.backends.AwsBackend;
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.builder()
          .backend(AwsBackend.fromEnv())
          .build();

      Message message = client.messages().create(
          MessageCreateParams.builder()
              .model(Model.CLAUDE_SONNET_5)
              .maxTokens(1024)
              .inferenceGeo("us")
              .addUserMessage("Hello!")
              .build()
      );

      IO.println(message);
  }

php PHP
  use Anthropic\Aws\Client;

  $client = new Client();

  $message = $client->messages->create(
      model: 'claude-sonnet-5',
      maxTokens: 1024,
      inferenceGeo: 'us',
      messages: [['role' => 'user', 'content' => 'Hello!']],
  );

  echo $message;

ruby Ruby
  require "anthropic"

  client = Anthropic::AWSClient.new

  message = client.messages.create(
    model: "claude-sonnet-5",
    max_tokens: 1024,
    inference_geo: "us",
    messages: [{ role: "user", content: "Hello!" }]
  )

  puts message
  ```
</CodeGroup>

If you omit `inference_geo`, the request uses the workspace's `default_inference_geo` if one is configured, otherwise `global`.

Workspace-level inference geography controls (`allowed_inference_geos` and `default_inference_geo`) are also available on Claude Platform on AWS. See [Workspace-level restrictions](https://platform.claude.com/docs/en/manage-claude/data-residency#workspace-level-restrictions).


## Workspaces

Source: https://platform.claude.com/llms-full.txt#workspaces

Inference and resource requests on Claude Platform on AWS target a workspace. You pass the workspace's ID in the `anthropic-workspace-id` header on these API calls. Workspace IDs use the tagged format `wrkspc_` followed by an alphanumeric identifier (for example, `wrkspc_01AbCdEf23GhIj`). See [Obtain your workspace ID](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#obtain-your-workspace-id) if you don't have it yet.

### Workspace scoping

Workspaces are bound to a single AWS region. A workspace created in `us-west-2` can only be accessed through the `us-west-2` endpoint. Usage, quotas, cost, files, batches, and Skills all roll up per workspace, giving you per-region breakdowns in the Claude Console.

Workspaces also serve as the primary IAM resource for Claude Platform on AWS. You grant or deny access to specific workspaces through AWS IAM policies using the workspace ARN. The ARN's resource segment is the same `wrkspc_`-prefixed ID you pass in the `anthropic-workspace-id` header:

```text wrap
arn:aws:aws-external-anthropic:{region}:{account-id}:workspace/{workspace-id}

text wrap
arn:aws:aws-external-anthropic:us-west-2:123456789012:workspace/wrkspc_01AbCdEf23GhIj
```

See [IAM policies](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#iam-policies) for policy examples.

### Managing workspaces

Create additional workspaces, rename a workspace, or archive a workspace from the AWS Console **Workspaces** page or with the [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api) workspace endpoints. A new workspace is bound to the AWS region of the endpoint you call to create it (see [Workspace scoping](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#workspace-scoping)). With the Admin role, you can also create, rename, and archive workspaces from the Claude Console **Workspaces** page.


## Using the Claude Console

Source: https://platform.claude.com/llms-full.txt#using-the-claude-console

Claude Platform on AWS uses the standard Claude Console at [platform.claude.com](https://platform.claude.com). When you sign in from the AWS Console, an **Account managed by AWS** indicator appears in the bottom-left of the Claude Console sidebar and the Console scopes to your Claude Platform on AWS organization. It provides usage analytics, cost breakdowns, rate limit visibility, workspace management, and pages for managing files, Agent Skills, batch jobs, and Claude Managed Agents resources (agents, sessions, environments, credential vaults, memory stores, and webhooks).

### Signing in

Access to the Claude Console is federated through AWS IAM. See [Set up your account](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#set-up-your-account) for the full first-time sign-in flow. In short:

1. Assume an IAM role with the `aws-external-anthropic:AssumeConsole` permission. See [IAM actions for Claude Platform on AWS](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#console-access).
2. Navigate to the Claude Platform on AWS page in the [AWS Console](https://console.aws.amazon.com/).
3. Choose **Open Claude Console**. The AWS Console issues a JWT and redirects you to `platform.claude.com`.
4. On first sign-in, you're prompted for an email address. Enter your work email. The platform provisions your Claude Console user just-in-time.

Two Claude Console roles are available: **Admin** and **Developer**. The Admin role grants access to all Claude Console pages and settings available for Claude Platform on AWS. The Developer role grants read access to usage, cost, rate limit, and workspace information. Contact your Anthropic account representative to assign the Admin or Developer role to a principal.

### Available pages

The **Through AWS gateway** column indicates whether the page reads and writes data through the AWS gateway (and is therefore governed by [IAM actions](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions)). Pages marked **No** read organization-level metadata directly from Anthropic and bypass IAM action checks.

| Page                  | Available     | Through AWS gateway       | Notes                                                                                                                                                                                                                                                           |
| --------------------- | ------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usage**             | Yes           | No                        | View token usage by model, workspace, and dimension. Data can take a few minutes to appear after a request.                                                                                                                                                     |
| **Cost**              | Yes           | No                        | View cost breakdowns by model and workspace. AWS Cost Explorer shows the aggregated [Claude Consumption Unit (CCU)](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#billing) line item.                                            |
| **Rate limits**       | Yes           | No                        | View rate limits (read-only). Tier increases go through your Anthropic account representative; see [Rate limits and quotas](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#rate-limits-and-quotas).                               |
| **Workspaces**        | Yes           | Yes (except spend limits) | View per-region workspaces. With the Admin role, you can also create, rename, and archive workspaces, and set per-workspace [spend limits](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#spend-limits).                          |
| **Encryption keys**   | Yes           | Yes                       | Under **Settings → Encryption keys**, register AWS KMS keys for [CMEK](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms#claude-platform-on-aws) (Admin role). Attach a registered key to a workspace from that workspace's **Security** settings. |
| **Files**             | Yes           | Yes                       | View and manage uploaded files.                                                                                                                                                                                                                                 |
| **Skills**            | Yes           | Yes                       | View and manage Agent Skills.                                                                                                                                                                                                                                   |
| **Batches**           | Yes           | Yes                       | View and manage batch processing jobs.                                                                                                                                                                                                                          |
| **Agents**            | Yes           | Yes                       | View and manage agent definitions.                                                                                                                                                                                                                              |
| **Sessions**          | Yes           | Yes                       | View agent sessions and event history.                                                                                                                                                                                                                          |
| **Environments**      | Yes           | Yes                       | View and manage cloud sandbox configurations for sessions.                                                                                                                                                                                                      |
| **Credential vaults** | Yes           | Yes                       | View and manage credential vaults for session authentication.                                                                                                                                                                                                   |
| **Memory stores**     | Yes           | Yes                       | View and manage persistent agent memory.                                                                                                                                                                                                                        |
| **Webhooks**          | Yes           | Yes                       | View and manage webhook endpoints under **Settings → Webhooks**.                                                                                                                                                                                                |
| **API keys**          | No            | N/A                       | Manage API keys in the AWS Console (**Claude Platform on AWS → API keys**). See [API key authentication](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#api-key-authentication).                                                  |
| **Members**           | No            | N/A                       | Not applicable. AWS IAM manages access.                                                                                                                                                                                                                         |
| **Billing**           | Yes (limited) | No                        | Set an organization monthly spend limit; see [Spend limits](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#spend-limits). AWS Marketplace manages invoicing. View cost breakdowns on the Cost page.                               |
| **Claude Code**       | No            | N/A                       | View Claude Code usage on the Usage page.                                                                                                                                                                                                                       |

### Switching organizations

The Claude Console does not support organization switching for Claude Platform on AWS. To access a different organization, sign out and reauthenticate through the AWS Console using the IAM role for that organization's AWS account.


## Rate limits and quotas

Source: https://platform.claude.com/llms-full.txt#rate-limits-and-quotas

Organizations on Claude Platform on AWS are placed on the Start tier. Anthropic manages rate limits directly, not through AWS quota systems.

Organizations on Claude Platform on AWS do not move between usage tiers automatically. Usage-based tier advancement applies to first-party Claude API organizations, not to organizations billed through AWS Marketplace. The self-service **Request rate limit increase** flow in the Claude Console is also not available: the Rate limits page directs you to your Anthropic account representative instead.

To request higher limits, contact your Anthropic account representative or [Anthropic support](https://support.claude.com). Include the following in your request:

* The models you need raised
* Peak input tokens per minute and output tokens per minute for each model (not daily totals)
* The approximate share of your input that is cached or repeated context (cache reads don't count toward input-token limits for most models; see [cache-aware ITPM](https://platform.claude.com/docs/en/api/rate-limits#cache-aware-itpm))

Usage tiers are fixed steps: each tier pairs rate limits with a [monthly spend cap](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#spend-limits), and moving to a higher tier raises both. For tier details and per-model limits, see [Rate limits](https://platform.claude.com/docs/en/api/rate-limits).


## Billing

Source: https://platform.claude.com/llms-full.txt#billing-2

Claude Platform on AWS bills through [AWS Marketplace](https://aws.amazon.com/marketplace). Usage is denominated in Claude Consumption Units (CCUs), metered hourly, and invoiced monthly in arrears on your AWS bill. CCUs are not prepaid credits. There is no CCU balance or commitment.

For the CCU price, conversion mechanics, discount application, and per-model token rates, see [Claude Platform on AWS pricing](https://platform.claude.com/docs/en/about-claude/pricing#claude-platform-on-aws-pricing).

### Spend limits

The Start, Build, and Scale usage tiers each carry a monthly spend cap; see the [per-tier spend caps](https://platform.claude.com/docs/en/api/rate-limits#spend-limits) for current values. When your organization's usage for the calendar month reaches its tier's cap, API requests fail with the [spend-cap error](https://platform.claude.com/docs/en/api/rate-limits#reaching-your-spend-cap) until 00:00 UTC on the first day of the next month, and retrying sooner doesn't succeed. The spend cap and rate limits belong to the same tier. To raise the cap, or to restore access after reaching it, request a tier increase through your Anthropic account representative or [Anthropic support](https://support.claude.com) (see [Rate limits and quotas](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#rate-limits-and-quotas)).

You can also set your own monthly spend limits below the cap, after adding at least one recipient under **Email recipients** on the Billing page:

* **Organization spend limit:** Go to [Settings > Billing](https://platform.claude.com/settings/billing) in the [Claude Console](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#using-the-claude-console) to set a monthly spend limit.
* **Workspace spend limits:** Select a workspace under [Settings > Workspaces](https://platform.claude.com/settings/workspaces) and open its **Spend limits** page.

When usage reaches a limit you set, requests fail with HTTP 400 (see the [spend limit error](https://platform.claude.com/docs/en/api/rate-limits#setting-your-own-spend-limit)) until 00:00 UTC on the first day of the next month, or until you raise or remove the limit.

Spend is calculated at list prices and can take about 2 hours to reflect recent usage, so usage can exceed the cap or a limit before requests start failing. The overshoot is billed. When the tier cap or an organization spend limit stops your requests, an email notice goes to the recipients listed under **Email recipients** on the Billing page. Role-based recipients, such as all admins, aren't available on Claude Platform on AWS. The tier-cap notice also goes to the email address used at AWS Marketplace sign-up.


## Monitoring and logging

Source: https://platform.claude.com/llms-full.txt#monitoring-and-logging-3

AWS CloudTrail can capture all requests to Claude Platform on AWS. Workspace, external key, compliance, vault, and webhook operations are logged as Management events by default. Inference, batch, file, skill, model, user profile, and Claude Managed Agents operations (other than vaults and webhooks) are classified as Data events and require explicit data event logging configuration, which incurs additional CloudTrail charges. See the [IAM actions reference](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#route-to-action-mapping) for the full event type classification and the [AWS CloudTrail documentation](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/) for configuration details.

### Request IDs

Each response includes two request IDs in the response headers:

* **AWS request ID (`x-amzn-requestid`):** The primary ID, indexed in CloudTrail. Use this when investigating requests through AWS tooling or when contacting AWS support.
* **Anthropic request ID (`request-id`):** The secondary ID. Use this when contacting Anthropic support.

<CodeGroup>
  ```bash cURL
  # Replace us-west-2 with your AWS region in both the URL and --aws-sigv4
  # -i includes the response headers in the output
  # Omit the x-amz-security-token header if you use long-term IAM user credentials
  curl -i "https://aws-external-anthropic.us-west-2.api.aws/v1/messages" \
    --aws-sigv4 "aws:amz:us-west-2:aws-external-anthropic" \
    --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
    -H "x-amz-security-token: $AWS_SESSION_TOKEN" \
    -H "content-type: application/json" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-workspace-id: $ANTHROPIC_AWS_WORKSPACE_ID" \
    -d '{
      "model": "claude-sonnet-5",
      "max_tokens": 1024,
      "messages": [
        {"role": "user", "content": "Hello!"}
      ]
    }'

bash CLI
  # The ant CLI's output formats print the response body, not response headers.
  # To read x-amzn-requestid, use the cURL example (-i) or an SDK example.

python Python
  from anthropic import AnthropicAWS

  client = AnthropicAWS()

  response = client.messages.with_raw_response.create(
      model="claude-sonnet-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello!"}],
  )

  print(response.headers.get("x-amzn-requestid"))  # AWS request ID
  print(response.headers.get("request-id"))  # Anthropic request ID

  message = response.parse()
  print(message.content)

typescript TypeScript
  import AnthropicAws from "@anthropic-ai/aws-sdk";

  const client = new AnthropicAws();

  const { data: message, response } = await client.messages
    .create({
      model: "claude-sonnet-5",
      max_tokens: 1024,
      messages: [{ role: "user", content: "Hello!" }]
    })
    .withResponse();

  console.log(response.headers.get("x-amzn-requestid")); // AWS request ID
  console.log(response.headers.get("request-id")); // Anthropic request ID
  console.log(message.content);

csharp C#
  using Anthropic;
  using Anthropic.Aws;

  var client = new AnthropicAwsClient();

  var response = await client.WithRawResponse.Messages.Create(new()
  {
      Model = Model.ClaudeSonnet5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello!" }]
  });

  Console.WriteLine(response.Headers.GetValues("x-amzn-requestid").First()); // AWS request ID
  Console.WriteLine(response.Headers.GetValues("request-id").First()); // Anthropic request ID
  Console.WriteLine(response.Value.Content);

go Go
  client, err := anthropicaws.NewClient(context.Background(), anthropicaws.ClientConfig{})
  if err != nil {
  	panic(err)
  }

  var response *http.Response
  message, err := client.Messages.New(
  	context.Background(),
  	anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeSonnet5,
  		MaxTokens: 1024,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hello!")),
  		},
  	},
  	option.WithResponseInto(&response),
  )
  if err != nil {
  	panic(err)
  }

  fmt.Println(response.Header.Get("x-amzn-requestid")) // AWS request ID
  fmt.Println(response.Header.Get("request-id"))       // Anthropic request ID
  fmt.Println(message.Content)

java Java
  import com.anthropic.aws.backends.AwsBackend;
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.http.HttpResponseFor;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.builder()
          .backend(AwsBackend.fromEnv())
          .build();

      HttpResponseFor<Message> response = client.messages().withRawResponse().create(
          MessageCreateParams.builder()
              .model(Model.CLAUDE_SONNET_5)
              .maxTokens(1024)
              .addUserMessage("Hello!")
              .build()
      );

      IO.println(response.headers().values("x-amzn-requestid").get(0)); // AWS request ID
      IO.println(response.requestId().orElse(null)); // Anthropic request ID
      IO.println(response.parse().content());
  }

php PHP
  use Anthropic\Aws\Client;

  $client = new Client();

  $response = $client->messages->raw->create(
      model: 'claude-sonnet-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello!']],
  );

  echo $response->getHeaderLine('x-amzn-requestid') . "\n"; // AWS request ID
  echo $response->getHeaderLine('request-id') . "\n"; // Anthropic request ID
  echo $response->parse()->content;

ruby Ruby
  # Accessing raw response headers is not currently supported in the Ruby SDK.
  # To inspect the x-amzn-requestid header, use one of the other SDK examples.
  ```
</CodeGroup>

Anthropic recommends logging your activity on at least a 30-day rolling basis to understand usage patterns and investigate issues.

<Note>
  AWS CloudTrail is configured within your AWS account. Enabling logging does not provide AWS or Anthropic access to your content beyond what is necessary for billing and service operation.
</Note>


## Migrating from Amazon Bedrock

Source: https://platform.claude.com/llms-full.txt#migrating-from-amazon-bedrock

If you currently use Claude on Bedrock, migrating to Claude Platform on AWS requires changes throughout your integration. SigV4 signing remains supported, but the signing context, base URL, API format, model IDs, SDK client and package, streaming format, request headers, and region availability all change. Claude Platform on AWS also provisions a new Anthropic organization. The following table summarizes the differences.

### What changes

The migration delta depends on which Bedrock integration you're coming from. The following table shows both the [current Bedrock integration](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) (Messages API at `bedrock-mantle.{region}.api.aws`) and the [legacy InvokeModel integration](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy).

| Aspect                     | From [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) | From [Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy) | To Claude Platform on AWS                                                                                                                                                                                                                                          |
| -------------------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Base URL**               | `bedrock-mantle.{region}.api.aws`                                                                               | `bedrock-runtime.{region}.amazonaws.com`                                                                                            | `aws-external-anthropic.{region}.api.aws`                                                                                                                                                                                                                          |
| **API format**             | Messages API at `/anthropic/v1/messages`                                                                        | Bedrock Converse / InvokeModel                                                                                                      | Claude API (`/v1/{endpoint}`)                                                                                                                                                                                                                                      |
| **Model IDs**              | anthropic.claude-haiku-4-5                                                                                      | anthropic.claude-haiku-4-5-20251001-v1:0(with a `us.` or `global.` inference profile prefix)                                        | claude-haiku-4-5                                                                                                                                                                                                                                                   |
| **SDK client**             | `AnthropicBedrockMantle`                                                                                        | `AnthropicBedrock` / Bedrock SDK                                                                                                    | Platform-specific client (see [Install an SDK](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#install-an-sdk)), in beta                                                                                                              |
| **SDK package**            | `anthropic[bedrock]`, `@anthropic-ai/bedrock-sdk`, and others                                                   | `anthropic[bedrock]`, `@anthropic-ai/bedrock-sdk`, or AWS SDK                                                                       | `anthropic[aws]`, `@anthropic-ai/aws-sdk`, and others (see [Install an SDK](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#install-an-sdk))                                                                                          |
| **SigV4 service name**     | `bedrock-mantle`                                                                                                | `bedrock`                                                                                                                           | `aws-external-anthropic`                                                                                                                                                                                                                                           |
| **Streaming format**       | SSE                                                                                                             | AWS EventStream                                                                                                                     | SSE (same as Claude API)                                                                                                                                                                                                                                           |
| **Workspace header**       | Not applicable                                                                                                  | Not applicable                                                                                                                      | `anthropic-workspace-id` required                                                                                                                                                                                                                                  |
| **Region availability**    | See [Amazon Bedrock regions](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-regions.html)         | See [Amazon Bedrock regions](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-regions.html)                             | All AWS commercial regions                                                                                                                                                                                                                                         |
| **Anthropic organization** | None required                                                                                                   | None required                                                                                                                       | New organization created at sign-up. Existing organizations can't be converted (see [Moving from an existing Anthropic organization](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#moving-from-an-existing-anthropic-organization)) |

If you're on the current Bedrock integration, the request body format is already the Messages API. The changes are the base URL, SigV4 service name, model IDs, and adding the `anthropic-workspace-id` header. If you're on the legacy InvokeModel or Converse API, you'll also rewrite the request and response shapes to the Messages API format. See [Claude on Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy) for the request-shape mapping.

### What you gain

* Typically same-day access to new models and features (see [feature limitations](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#features-not-supported))
* Agent Skills for document generation (PowerPoint, Excel, Word, PDF)
* Code execution in Anthropic's managed sandbox
* Beta features through the `anthropic-beta` header (see [feature limitations](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#features-not-supported))
* Claude Console for quota visibility and usage analytics
* Direct Anthropic support
* API key authentication as an alternative to SigV4 (see [API key authentication](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#api-key-authentication))

### What stays the same

* AWS IAM authentication (SigV4)
* AWS as the invoicing party. The billing channel changes from native AWS service to AWS Marketplace (see [Commercial considerations](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#commercial-considerations)).
* AWS commitment retirement

### Migration pitfalls

<Warning>
  **Enable outbound web identity federation first.** If your AWS account has not previously used Claude Platform on AWS, you must [enable outbound web identity federation](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#enable-outbound-web-identity-federation) once per account before making requests. Without this step, all requests fail with a federation error (see [Enable outbound web identity federation](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#enable-outbound-web-identity-federation) for the exact error and remediation). This step is not required for Bedrock.
</Warning>

<Warning>
  **Zero Data Retention (ZDR) is opt-in on Claude Platform on AWS.** On Bedrock, AWS is the data processor and Anthropic does not retain inference inputs or outputs. Anthropic's ZDR program does not apply there. On Claude Platform on AWS, Anthropic processes inference data as an independent data processor, and ZDR follows the first-party Claude API model: it is available on request through your Anthropic account representative. Confirm ZDR enrollment before migrating production workloads that depend on data-retention guarantees.
</Warning>

### Commercial considerations

* **Anthropic terms of service:** Using Claude Platform on AWS requires accepting Anthropic's Commercial Terms of Service and Usage Policy. If your organization hasn't already accepted these (for example, if you've only used Claude through Bedrock), you're prompted during account setup. See [Set up your account](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#set-up-your-account).
* **Discounts and private offers:** Negotiated discounts and AWS Marketplace private offers don't transfer automatically between Bedrock and Claude Platform on AWS. Work with your Anthropic account representative to set up commercial terms for Claude Platform on AWS.


## IAM policies

Source: https://platform.claude.com/llms-full.txt#iam-policies

Claude Platform on AWS integrates with AWS IAM for access control. You grant or deny access to specific API actions on specific workspaces using standard IAM policy syntax.

The SigV4 service name and IAM action namespace is `aws-external-anthropic`. Actions follow the pattern `aws-external-anthropic:<Action>` (for example, `aws-external-anthropic:CreateInference`).

### Example: deny batch inference

The following policy allows real-time inference while blocking batch processing:

The `GetBatchInference` action authorizes both the batch metadata route and the batch results route. Denying it blocks both reads. For a Deny-only policy suitable for ZDR-sensitive workloads, see [Feature lockdown for a ZDR-sensitive workspace](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#feature-lockdown-for-a-zdr-sensitive-workspace).

<Note>
  `ListWorkspaces` is account-scoped, so it appears in a separate Allow statement with `"Resource": "*"`. Specifying a workspace ARN on an account-scoped action has no effect (see [Provisioning automation](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#provisioning-automation)).

  This policy assumes AWS SigV4 authentication. If the principal authenticates with an API key, also add `aws-external-anthropic:CallWithBearerToken` to the `"Resource": "*"` Allow statement. `CallWithBearerToken` is a route-less authentication-layer action that does not bind to a workspace ARN. See [Per-customer workspace isolation](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#per-customer-workspace-isolation) for the two-statement pattern.
</Note>

### Managed policies

AWS provides five managed policies (`AnthropicFullAccess`, `AnthropicReadOnlyAccess`, `AnthropicInferenceAccess`, `AnthropicLimitedAccess`, and `AnthropicSelfHostedEnvironmentAccess`) for common access patterns. For the actions each policy grants, the complete list of IAM actions, the route-to-action mapping, and additional policy examples, see [IAM actions for Claude Platform on AWS](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#managed-policies).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-67

<CardGroup cols={2}>
  <Card title="Features overview" icon="stack" href="https://platform.claude.com/docs/en/build-with-claude/overview">
    Explore Claude's advanced features and capabilities.
  </Card>

  <Card title="Pricing" icon="chart" href="https://platform.claude.com/docs/en/about-claude/pricing#claude-platform-on-aws-pricing">
    Learn about Claude Platform on AWS pricing and Claude Consumption Unit rates.
  </Card>

  <Card title="Model deprecations" icon="arrow-clockwise" href="https://platform.claude.com/docs/en/about-claude/model-deprecations">
    As safer and more capable models launch, Anthropic regularly retires older ones. See all API deprecations, along with recommended replacements.
  </Card>
</CardGroup>


## Additional resources

Source: https://platform.claude.com/llms-full.txt#additional-resources-4

<CardGroup cols={2}>
  <Card title="Claude Console" icon="browser" href="https://platform.claude.com">
    View usage, cost, and workspaces in the Claude Console. Sign in through the AWS Console.
  </Card>

  <Card title="Claude in Amazon Bedrock" icon="cloud" href="https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock">
    Use AWS-operated Claude if you need AWS as the sole data processor.
  </Card>

  <Card title="AWS Marketplace" icon="coins" href="https://aws.amazon.com/marketplace">
    Manage your AWS Marketplace subscription and billing.
  </Card>
</CardGroup>


## Managed Agents

Source: https://platform.claude.com/llms-full.txt#managed-agents

### First steps

---
title: Claude Managed Agents overview
url: https://platform.claude.com/docs/en/managed-agents/overview
description: Pre-built, configurable agent harness that runs in managed infrastructure. Best for long-running tasks and asynchronous work.
---

Anthropic offers two ways to build with Claude, each suited to different use cases:

|                | Messages API                                | Claude Managed Agents                                                     |
| -------------- | ------------------------------------------- | ------------------------------------------------------------------------- |
| **What it is** | Direct model prompting access               | Pre-built, configurable agent harness that runs in managed infrastructure |
| **Best for**   | Custom agent loops and fine-grained control | Long-running tasks and asynchronous work                                  |

Claude Managed Agents provides the harness and infrastructure for running Claude as an autonomous agent. Instead of building your own agent loop, tool execution, and runtime, you get a fully managed environment where Claude can read files, run commands, browse the web, and run code securely. The harness supports built-in prompt caching, compaction, and other performance optimizations for high-quality, efficient agent outputs. To build your own agent loop with direct model access instead, see [Using the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages).

<Note>
  Claude Managed Agents is also available on Claude Platform on AWS, with some differences in feature availability and session behavior. See [Claude Managed Agents](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#claude-managed-agents) in the Claude Platform on AWS guide.
</Note>

<CardGroup cols={3}>
  <Card title="Quickstart" icon="play" href="https://platform.claude.com/docs/en/managed-agents/quickstart">
    Create your first agent session
  </Card>

  <Card title="Start a session" icon="code-brackets" href="https://platform.claude.com/docs/en/managed-agents/sessions">
    Create a session and send your first event
  </Card>

  <Card title="Reference" icon="book" href="https://platform.claude.com/docs/en/managed-agents/reference">
    Event types, rate limits, CLI flags, and other lookup tables
  </Card>
</CardGroup>


## Core concepts

Source: https://platform.claude.com/llms-full.txt#core-concepts-2

Claude Managed Agents is built around four concepts:

| Concept         | Description                                                                                                                   |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Agent**       | The model, system prompt, tools, MCP servers, and skills                                                                      |
| **Environment** | Configuration for where sessions run: an Anthropic-managed cloud sandbox, or a self-hosted sandbox on your own infrastructure |
| **Session**     | A running agent instance within an environment, performing a specific task and generating outputs                             |
| **Events**      | Messages exchanged between your application and the agent (user turns, tool results, status updates)                          |


## How it works

Source: https://platform.claude.com/llms-full.txt#how-it-works-8

<Steps>
  <Step title="Create an agent">
    Define the model, system prompt, tools, MCP servers, and skills. Create the agent once and reference it by ID across sessions.
  </Step>

  <Step title="Create an environment">
    Configure where the agent runs: a cloud sandbox, or a [self-hosted sandbox](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) on your own infrastructure.
  </Step>

  <Step title="Start a session">
    Launch a session that references your agent and environment configuration.
  </Step>

  <Step title="Send events and stream responses">
    Send user messages as events. Claude autonomously runs tools and streams back results through server-sent events (SSE). Event history is persisted server-side and can be fetched in full.
  </Step>

  <Step title="Steer or interrupt">
    Send additional user events to guide the agent mid-execution, or interrupt it to change direction.
  </Step>
</Steps>


## When to use Claude Managed Agents

Source: https://platform.claude.com/llms-full.txt#when-to-use-claude-managed-agents

Claude Managed Agents is best for workloads that need:

* **Long-running execution:** Tasks that run for minutes or hours with multiple tool calls
* **Cloud infrastructure:** Secure sandboxes with pre-installed packages and network access
* **Self-hosted execution:** Sandboxes on infrastructure you control for compliance or data-residency requirements
* **Minimal infrastructure:** No need to build your own agent loop, sandbox, or tool execution layer
* **Stateful sessions:** Persistent filesystems and conversation history across multiple interactions
* **Scheduled execution:** Recurring agent runs on a cron schedule through [scheduled deployments](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments)


## Supported tools

Source: https://platform.claude.com/llms-full.txt#supported-tools

Claude Managed Agents gives Claude access to a set of built-in tools:

* **Bash:** Run shell commands in the sandbox
* **File operations:** Read, write, edit, glob, and grep files in the sandbox
* **Web search and fetch:** Search the web and retrieve content from URLs, optionally restricted to an allowlist or blocklist of domains
* **MCP servers:** Connect to external tool providers

See [Tools](https://platform.claude.com/docs/en/managed-agents/tools) for the full list and configuration options.


## Beta access

Source: https://platform.claude.com/llms-full.txt#beta-access

<Note>
  Claude Managed Agents is in beta. All Managed Agents endpoints require the `managed-agents-2026-04-01` beta header. The SDK sets the beta header automatically. Behaviors may be refined between releases to improve outputs.
</Note>

To get started, you need:

1. A [Claude API key](https://platform.claude.com/settings/keys)
2. The `managed-agents-2026-04-01` beta header on all requests
3. Access to Claude Managed Agents (enabled by default for all API accounts)

Within the beta, [MCP tunnels](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview) and [dreaming](https://platform.claude.com/docs/en/managed-agents/dreams) are in a more limited research preview. [Request access](https://claude.com/form/claude-managed-agents) to enable them.

Claude Managed Agents is stateful by design: sessions are long-running, resume cleanly after pauses, and store conversation history, sandbox state, and outputs server-side. Because of this, Managed Agents is not currently eligible for [Zero Data Retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#zero-data-retention-zdr-scope) or HIPAA Business Associate Agreement (BAA) coverage. You retain control over this data: you can [delete sessions](https://platform.claude.com/docs/en/managed-agents/session-operations#deleting-a-session), and separately delete any [files](https://platform.claude.com/docs/en/build-with-claude/files#delete-a-file) you uploaded, at any time through the API. For eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility).

See [Rate limits](https://platform.claude.com/docs/en/managed-agents/reference#rate-limits) and [Branding guidelines](https://platform.claude.com/docs/en/managed-agents/reference#branding-guidelines) in the reference.


---
title: Get started with Claude Managed Agents
url: https://platform.claude.com/docs/en/managed-agents/quickstart
description: Create your first autonomous agent.
---

This guide walks you through creating an agent, setting up an environment, starting a session, and streaming agent responses.

<Tip>
  **Prefer an interactive walkthrough?** Run `/claude-api managed-agents-onboard` in the latest version of [Claude Code](https://claude.com/product/claude-code) for a guided setup and interactive question-answering.
</Tip>


## Core concepts

Source: https://platform.claude.com/llms-full.txt#core-concepts-3

| Concept         | Description                                                                                                                   |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Agent**       | The model, system prompt, tools, MCP servers, and skills                                                                      |
| **Environment** | Configuration for where sessions run: an Anthropic-managed cloud sandbox, or a self-hosted sandbox on your own infrastructure |
| **Session**     | A running agent instance within an environment, performing a specific task and generating outputs                             |
| **Events**      | Messages exchanged between your application and the agent (user turns, tool results, status updates)                          |


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-8

* A [Claude Console account](https://platform.claude.com)
* An [API key](https://platform.claude.com/settings/keys)


## Install the CLI

Source: https://platform.claude.com/llms-full.txt#install-the-cli

<Tabs>
  <Tab title="Homebrew (macOS)">

</Tab>

  <Tab title="curl (Linux/WSL)">
    For Linux environments, download the release binary directly.

You can find all releases on the [GitHub releases page](https://github.com/anthropics/anthropic-cli/releases).
  </Tab>

  <Tab title="Go">
    You can also install the CLI from source using `go install`. Requires Go 1.25 or later.

The binary is placed in `$(go env GOPATH)/bin`. Add it to your `PATH` if it isn't already:

</Tab>
</Tabs>

Check the installation:


## Install the SDK

Source: https://platform.claude.com/llms-full.txt#install-the-sdk

<Tabs>
  <Tab title="Python">

</Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="Java">
    ```groovy Gradle
    implementation("com.anthropic:anthropic-java:2.60.0")

bash
    go get github.com/anthropics/anthropic-sdk-go

bash
    dotnet add package Anthropic

bash
    bundle add anthropic

bash
    composer require "anthropic-ai/sdk" "guzzlehttp/guzzle:^7"

bash
export ANTHROPIC_API_KEY="your-api-key-here"
```


## Create your first session

Source: https://platform.claude.com/llms-full.txt#create-your-first-session

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>

<Steps>
  <Step title="Create an agent">
    Create an agent that defines the model, system prompt, and available tools.

    <CodeGroup defaultLanguage="CLI">
      ```bash cURL
      set -euo pipefail

      agent=$(
        curl -sS --fail-with-body https://api.anthropic.com/v1/agents \
          -H "x-api-key: $ANTHROPIC_API_KEY" \
          -H "anthropic-version: 2023-06-01" \
          -H "anthropic-beta: managed-agents-2026-04-01" \
          -H "content-type: application/json" \
          -d @- <<'EOF'
      {
        "name": "Coding Assistant",
        "model": "claude-opus-5",
        "system": "You are a helpful coding assistant. Write clean, well-documented code.",
        "tools": [
          {"type": "agent_toolset_20260401"}
        ]
      }
      EOF
      )

      AGENT_ID=$(jq -er '.id' <<<"$agent")
      AGENT_VERSION=$(jq -er '.version' <<<"$agent")

      echo "Agent ID: $AGENT_ID, version: $AGENT_VERSION"

bash CLI
        AGENT_ID=$(ant beta:agents create --transform id --raw-output < coding-assistant.agent.yaml)

        echo "Agent ID: $AGENT_ID"

yaml
          name: Coding Assistant
          model:
            id: claude-opus-5
          system: You are a helpful coding assistant. Write clean, well-documented code.
          tools:
            - type: agent_toolset_20260401

python Python
      from anthropic import Anthropic

      client = Anthropic()

      agent = client.beta.agents.create(
          name="Coding Assistant",
          model="claude-opus-5",
          system="You are a helpful coding assistant. Write clean, well-documented code.",
          tools=[
              {"type": "agent_toolset_20260401"},
          ],
      )

      print(f"Agent ID: {agent.id}, version: {agent.version}")

typescript TypeScript
      import Anthropic from "@anthropic-ai/sdk";

      const client = new Anthropic();

      const agent = await client.beta.agents.create({
        name: "Coding Assistant",
        model: "claude-opus-5",
        system: "You are a helpful coding assistant. Write clean, well-documented code.",
        tools: [
          { type: "agent_toolset_20260401" },
        ],
      });

      console.log(`Agent ID: ${agent.id}, version: ${agent.version}`);

csharp C#
      using Anthropic;
      using Anthropic.Models.Beta.Agents;
      using Anthropic.Models.Beta.Environments;
      using Anthropic.Models.Beta.Sessions;
      using Anthropic.Models.Beta.Sessions.Events;

      var client = new AnthropicClient();

      var agent = await client.Beta.Agents.Create(new()
      {
          Name = "Coding Assistant",
          Model = BetaManagedAgentsModel.ClaudeOpus5,
          System = "You are a helpful coding assistant. Write clean, well-documented code.",
          Tools =
          [
              new BetaManagedAgentsAgentToolset20260401Params
              {
                  Type = "agent_toolset_20260401",
              },
          ],
      });

      Console.WriteLine($"Agent ID: {agent.ID}, version: {agent.Version}");

go Go
      package main

      import (
      	"context"
      	"fmt"

      	"github.com/anthropics/anthropic-sdk-go"
      )

      func main() {
      	client := anthropic.NewClient()
      	ctx := context.Background()

      	agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
      		Name: "Coding Assistant",
      		Model: anthropic.BetaManagedAgentsModelConfigParams{
      			ID: anthropic.BetaManagedAgentsModelClaudeOpus5,
      		},
      		System: anthropic.String("You are a helpful coding assistant. Write clean, well-documented code."),
      		Tools: []anthropic.BetaAgentNewParamsToolUnion{{
      			OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
      				Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
      			},
      		}},
      	})
      	if err != nil {
      		panic(err)
      	}

      	fmt.Printf("Agent ID: %s, version: %d\n", agent.ID, agent.Version)

java Java
      import com.anthropic.client.okhttp.AnthropicOkHttpClient;
      import com.anthropic.models.beta.agents.AgentCreateParams;
      import com.anthropic.models.beta.agents.BetaManagedAgentsAgentToolset20260401Params;
      import com.anthropic.models.beta.agents.BetaManagedAgentsModel;
      import com.anthropic.models.beta.environments.BetaCloudConfigParams;
      import com.anthropic.models.beta.environments.BetaUnrestrictedNetwork;
      import com.anthropic.models.beta.environments.EnvironmentCreateParams;
      import com.anthropic.models.beta.sessions.SessionCreateParams;
      import com.anthropic.models.beta.sessions.events.BetaManagedAgentsStreamSessionEvents;
      import com.anthropic.models.beta.sessions.events.BetaManagedAgentsUserMessageEventParams;
      import com.anthropic.models.beta.sessions.events.EventSendParams;

      void main() {
          var client = AnthropicOkHttpClient.fromEnv();

          var agent = client.beta().agents().create(AgentCreateParams.builder()
              .name("Coding Assistant")
              .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
              .system("You are a helpful coding assistant. Write clean, well-documented code.")
              .addTool(BetaManagedAgentsAgentToolset20260401Params.builder()
                  .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
                  .build())
              .build());

          IO.println("Agent ID: " + agent.id() + ", version: " + agent.version());

php PHP
      use Anthropic\Client;

      $client = new Client();

      $agent = $client->beta->agents->create(
          name: 'Coding Assistant',
          model: 'claude-opus-5',
          system: 'You are a helpful coding assistant. Write clean, well-documented code.',
          tools: [
              ['type' => 'agent_toolset_20260401'],
          ],
      );

      echo "Agent ID: {$agent->id}, version: {$agent->version}\n";

ruby Ruby
      require "anthropic"

      client = Anthropic::Client.new

      agent = client.beta.agents.create(
        name: "Coding Assistant",
        model: "claude-opus-5",
        system_: "You are a helpful coding assistant. Write clean, well-documented code.",
        tools: [{type: "agent_toolset_20260401"}]
      )

      puts "Agent ID: #{agent.id}, version: #{agent.version}"

bash cURL
      environment=$(
        curl -sS --fail-with-body https://api.anthropic.com/v1/environments \
          -H "x-api-key: $ANTHROPIC_API_KEY" \
          -H "anthropic-version: 2023-06-01" \
          -H "anthropic-beta: managed-agents-2026-04-01" \
          -H "content-type: application/json" \
          -d @- <<'EOF'
      {
        "name": "quickstart-env",
        "config": {
          "type": "cloud",
          "networking": {"type": "unrestricted"}
        }
      }
      EOF
      )

      ENVIRONMENT_ID=$(jq -er '.id' <<<"$environment")

      echo "Environment ID: $ENVIRONMENT_ID"

bash CLI
        ENVIRONMENT_ID=$(ant beta:environments create --transform id --raw-output < quickstart.environment.yaml)

        echo "Environment ID: $ENVIRONMENT_ID"

yaml
          name: quickstart-env
          config:
            type: cloud
            networking:
              type: unrestricted

python Python
      environment = client.beta.environments.create(
          name="quickstart-env",
          config={
              "type": "cloud",
              "networking": {"type": "unrestricted"},
          },
      )

      print(f"Environment ID: {environment.id}")

typescript TypeScript
      const environment = await client.beta.environments.create({
        name: "quickstart-env",
        config: {
          type: "cloud",
          networking: { type: "unrestricted" },
        },
      });

      console.log(`Environment ID: ${environment.id}`);

csharp C#
      var environment = await client.Beta.Environments.Create(new()
      {
          Name = "quickstart-env",
          Config = new BetaCloudConfigParams { Networking = new BetaUnrestrictedNetwork() },
      });

      Console.WriteLine($"Environment ID: {environment.ID}");

go Go
      environment, err := client.Beta.Environments.New(ctx, anthropic.BetaEnvironmentNewParams{
      	Name: "quickstart-env",
      	Config: anthropic.BetaEnvironmentNewParamsConfigUnion{
      		OfCloud: &anthropic.BetaCloudConfigParams{
      			Networking: anthropic.BetaCloudConfigParamsNetworkingUnion{
      				OfUnrestricted: &anthropic.BetaUnrestrictedNetworkParam{},
      			},
      		},
      	},
      })
      if err != nil {
      	panic(err)
      }

      fmt.Printf("Environment ID: %s\n", environment.ID)

java Java
      var environment = client.beta().environments().create(EnvironmentCreateParams.builder()
          .name("quickstart-env")
          .config(BetaCloudConfigParams.builder()
              .networking(BetaUnrestrictedNetwork.builder().build())
              .build())
          .build());

      IO.println("Environment ID: " + environment.id());

php PHP
      $environment = $client->beta->environments->create(
          name: 'quickstart-env',
          config: ['type' => 'cloud', 'networking' => ['type' => 'unrestricted']],
      );

      echo "Environment ID: {$environment->id}\n";

ruby Ruby
      environment = client.beta.environments.create(
        name: "quickstart-env",
        config: {type: "cloud", networking: {type: "unrestricted"}}
      )

      puts "Environment ID: #{environment.id}"

bash cURL
      session=$(
        curl -sS --fail-with-body https://api.anthropic.com/v1/sessions \
          -H "x-api-key: $ANTHROPIC_API_KEY" \
          -H "anthropic-version: 2023-06-01" \
          -H "anthropic-beta: managed-agents-2026-04-01" \
          -H "content-type: application/json" \
          -d @- <<EOF
      {
        "agent": "$AGENT_ID",
        "environment_id": "$ENVIRONMENT_ID",
        "title": "Quickstart session"
      }
      EOF
      )

      SESSION_ID=$(jq -er '.id' <<<"$session")

      echo "Session ID: $SESSION_ID"

bash CLI
      SESSION_ID=$(ant beta:sessions create \
        --agent "$AGENT_ID" \
        --environment-id "$ENVIRONMENT_ID" \
        --title "Quickstart session" \
        --transform id --raw-output)

      echo "Session ID: $SESSION_ID"

python Python
      session = client.beta.sessions.create(
          agent=agent.id,
          environment_id=environment.id,
          title="Quickstart session",
      )

      print(f"Session ID: {session.id}")

typescript TypeScript
      const session = await client.beta.sessions.create({
        agent: agent.id,
        environment_id: environment.id,
        title: "Quickstart session",
      });

      console.log(`Session ID: ${session.id}`);

csharp C#
      var session = await client.Beta.Sessions.Create(new()
      {
          Agent = agent.ID,
          EnvironmentID = environment.ID,
          Title = "Quickstart session",
      });

      Console.WriteLine($"Session ID: {session.ID}");

go Go
      session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
      	Agent:         anthropic.BetaSessionNewParamsAgentUnion{OfString: anthropic.String(agent.ID)},
      	EnvironmentID: environment.ID,
      	Title:         anthropic.String("Quickstart session"),
      })
      if err != nil {
      	panic(err)
      }

      fmt.Printf("Session ID: %s\n", session.ID)

java Java
      var session = client.beta().sessions().create(SessionCreateParams.builder()
          .agent(agent.id())
          .environmentId(environment.id())
          .title("Quickstart session")
          .build());

      IO.println("Session ID: " + session.id());

php PHP
      $session = $client->beta->sessions->create(
          agent: $agent->id,
          environmentID: $environment->id,
          title: 'Quickstart session',
      );

      echo "Session ID: {$session->id}\n";

ruby Ruby
      session = client.beta.sessions.create(
        agent: agent.id,
        environment_id: environment.id,
        title: "Quickstart session"
      )

      puts "Session ID: #{session.id}"

bash cURL
      # This workflow does not translate well to a one-off shell command.
      # Use one of the SDK examples in this code group instead.

bash CLI
      # This workflow does not translate well to a one-off shell command.
      # Use one of the SDK examples in this code group instead.

python Python
      with client.beta.sessions.events.stream(session.id) as stream:
          # Send the user message after the stream opens
          client.beta.sessions.events.send(
              session.id,
              events=[
                  {
                      "type": "user.message",
                      "content": [
                          {
                              "type": "text",
                              "text": "Create a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt",
                          },
                      ],
                  },
              ],
          )

          # Process streaming events
          for event in stream:
              match event.type:
                  case "agent.message":
                      for block in event.content:
                          print(block.text, end="")
                  case "agent.tool_use":
                      print(f"\n[Using tool: {event.name}]")
                  case "session.status_idle":
                      print("\n\nAgent finished.")
                      break

typescript TypeScript
      const stream = await client.beta.sessions.events.stream(session.id);

      // Send the user message after the stream opens
      await client.beta.sessions.events.send(session.id, {
        events: [
          {
            type: "user.message",
            content: [
              {
                type: "text",
                text: "Create a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt",
              },
            ],
          },
        ],
      });

      // Process streaming events
      for await (const event of stream) {
        if (event.type === "agent.message") {
          for (const block of event.content) {
            process.stdout.write(block.text);
          }
        } else if (event.type === "agent.tool_use") {
          console.log(`\n[Using tool: ${event.name}]`);
        } else if (event.type === "session.status_idle") {
          console.log("\n\nAgent finished.");
          break;
        }
      }

csharp C#
      var stream = client.Beta.Sessions.Events.StreamStreaming(session.ID);

      // Send the user message after the stream opens
      await client.Beta.Sessions.Events.Send(session.ID, new()
      {
          Events =
          [
              new BetaManagedAgentsUserMessageEventParams
              {
                  Type = "user.message",
                  Content =
                  [
                      new BetaManagedAgentsTextBlock
                      {
                          Type = "text",
                          Text = "Create a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt",
                      },
                  ],
              },
          ],
      });

      // Process streaming events
      await foreach (var ev in stream)
      {
          if (ev.Value is BetaManagedAgentsAgentMessageEvent message)
          {
              foreach (var block in message.Content)
              {
                  Console.Write(block.Text);
              }
          }
          else if (ev.Value is BetaManagedAgentsAgentToolUseEvent toolUse)
          {
              Console.WriteLine($"\n[Using tool: {toolUse.Name}]");
          }
          else if (ev.Value is BetaManagedAgentsSessionStatusIdleEvent)
          {
              Console.WriteLine("\n\nAgent finished.");
              break;
          }
      }

go Go
      	stream := client.Beta.Sessions.Events.StreamEvents(ctx, session.ID, anthropic.BetaSessionEventStreamParams{})
      	defer stream.Close()

      	// Send the user message after the stream opens
      	_, err = client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
      		Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
      			OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
      				Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
      				Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{{
      					OfText: &anthropic.BetaManagedAgentsTextBlockParam{
      						Type: anthropic.BetaManagedAgentsTextBlockTypeText,
      						Text: "Create a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt",
      					},
      				}},
      			},
      		}},
      	})
      	if err != nil {
      		panic(err)
      	}

      	// Process streaming events
      loop:
      	for stream.Next() {
      		switch event := stream.Current().AsAny().(type) {
      		case anthropic.BetaManagedAgentsAgentMessageEvent:
      			for _, block := range event.Content {
      				fmt.Print(block.Text)
      			}
      		case anthropic.BetaManagedAgentsAgentToolUseEvent:
      			fmt.Printf("\n[Using tool: %s]\n", event.Name)
      		case anthropic.BetaManagedAgentsSessionStatusIdleEvent:
      			fmt.Print("\n\nAgent finished.\n")
      			break loop
      		}
      	}
      	if err := stream.Err(); err != nil {
      		panic(err)
      	}

java Java
      try (var stream = client.beta().sessions().events().streamStreaming(session.id())) {
          // Send the user message after the stream opens
          client.beta().sessions().events().send(session.id(), EventSendParams.builder()
              .addEvent(BetaManagedAgentsUserMessageEventParams.builder()
                  .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
                  .addTextContent("Create a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt")
                  .build())
              .build());

          // Process streaming events
          for (var event : (Iterable<BetaManagedAgentsStreamSessionEvents>) stream.stream()::iterator) {
              if (event.isAgentMessage()) {
                  event.asAgentMessage().content().forEach(block -> block.text().ifPresent(textBlock -> IO.print(textBlock.text())));
              } else if (event.isAgentToolUse()) {
                  IO.println("\n[Using tool: " + event.asAgentToolUse().name() + "]");
              } else if (event.isSessionStatusIdle()) {
                  IO.println("\n\nAgent finished.");
                  break;
              }
          }
      }

php PHP
      $stream = $client->beta->sessions->events->streamStream($session->id);

      // Send the user message after the stream opens
      $client->beta->sessions->events->send(
          $session->id,
          events: [
              [
                  'type' => 'user.message',
                  'content' => [
                      ['type' => 'text', 'text' => 'Create a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt'],
                  ],
              ],
          ],
      );

      // Process streaming events
      foreach ($stream as $event) {
          match ($event->type) {
              'agent.message' => print(implode('', array_map(fn($block) => $block->text, $event->content))),
              'agent.tool_use' => print("\n[Using tool: {$event->name}]\n"),
              'session.status_idle' => print("\n\nAgent finished.\n"),
              default => null,
          };
          if ($event->type === 'session.status_idle') {
              break;
          }
      }

ruby Ruby
      stream = client.beta.sessions.events.stream_events(session.id)

      # Send the user message after the stream opens
      client.beta.sessions.events.send_(
        session.id,
        events: [{
          type: "user.message",
          content: [{type: "text", text: "Create a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt"}]
        }]
      )

      # Process streaming events
      stream.each do |event|
        case event.type
        in :"agent.message"
          event.content.each { print it.text }
        in :"agent.tool_use"
          puts "\n[Using tool: #{event.name}]"
        in :"session.status_idle"
          puts "\n\nAgent finished."
          break
        else
          # ignore other event types
        end
      end

text wrap
    I'll create a Python script that generates the first 20 Fibonacci numbers and saves them to a file.
    [Using tool: write]
    [Using tool: bash]
    The script ran successfully. Let me verify the output file.
    [Using tool: bash]
    fibonacci.txt contains the first 20 Fibonacci numbers (0 through 4181).

    Agent finished.
    ```
  </Step>
</Steps>


## What's happening

Source: https://platform.claude.com/llms-full.txt#what-s-happening

When you send a user event, Claude Managed Agents:

1. **Provisions a sandbox:** Your environment configuration determines how it's built.
2. **Runs the agent loop:** Claude determines which tools to use based on your message.
3. **Runs tools:** File writes, bash commands, and other tool calls run inside the sandbox.
4. **Streams events:** You receive real-time updates as the agent works.
5. **Goes idle:** The agent emits a `session.status_idle` event when it has nothing more to do.


## Build a complete app

Source: https://platform.claude.com/llms-full.txt#build-a-complete-app

Each of these quickstarts pairs Claude Managed Agents with a popular chat framework to make a complete, runnable application. In each one, the framework renders the chat surface while a managed session runs the agent loop server-side: the session holds the transcript, runs tools in a sandbox, and streams events that the front end renders.

<CardGroup cols={3}>
  <Card title="Chat SDK" icon="github-logo" href="https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/chat-sdk">
    A research analyst in a browser chat built with Vercel's Chat SDK. Each conversation is one persistent session that streams its reply while a live feed shows the tool calls. Swapping the Chat SDK adapter moves the same handler to Slack, Teams, Discord, or WhatsApp.
  </Card>

  <Card title="assistant-ui" icon="github-logo" href="https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/assistant-ui">
    A spreadsheet analyst in a chat built from assistant-ui primitives. Sessions are the thread list, one reducer turns the session event log into messages and tool cards, and each bash command renders an inline Allow/Deny gate before it runs.
  </Card>

  <Card title="CopilotKit (AG-UI)" icon="github-logo" href="https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/copilot-kit-ag-ui">
    A personal finance assistant in a CopilotKit chat. The AG-UI adapter for Claude Managed Agents maps each chat thread to a managed session and streams replies token by token, and custom tools render interactive charts inline in the conversation.
  </Card>
</CardGroup>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-68

<CardGroup cols={2}>
  <Card title="Define your agent" icon="brain" href="https://platform.claude.com/docs/en/managed-agents/agent-setup">
    Create reusable, versioned agent configurations
  </Card>

  <Card title="Configure environments" icon="settings" href="https://platform.claude.com/docs/en/managed-agents/environments">
    Customize networking and sandbox settings
  </Card>

  <Card title="Agent tools" icon="tool" href="https://platform.claude.com/docs/en/managed-agents/tools">
    Enable specific tools for your agent
  </Card>

  <Card title="Session event stream" icon="lightning" href="https://platform.claude.com/docs/en/managed-agents/events-and-streaming">
    Handle events and steer the agent mid-execution
  </Card>

  <Card title="Scheduled deployments" icon="arrows-clockwise" href="https://platform.claude.com/docs/en/managed-agents/scheduled-deployments">
    Run your agent on a recurring cron schedule
  </Card>

  <Card title="Knowledge wiki quickstart" icon="github-logo" href="https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/knowledge-wiki">
    Distill a document corpus once into a knowledge wiki, then answer repeated questions from it at a fraction of the cost
  </Card>
</CardGroup>


---
title: Build in Console
url: https://platform.claude.com/docs/en/managed-agents/onboarding
description: Create, test, and iterate on agents visually in Console, then run them from your code with the API.
---

[Console](https://platform.claude.com/workspaces/default/agent-quickstart/) provides a visual interface for creating and configuring agents. It lets you iterate on configuration interactively before writing code.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## How to build an agent

Source: https://platform.claude.com/llms-full.txt#how-to-build-an-agent

The [visual interface](https://platform.claude.com/workspaces/default/agent-quickstart/) walks you through each field of an agent definition:

* **Model and system prompt:** Pick a model and write the system prompt in a full-width editor.
* **MCP servers:** Add remote MCP servers by URL and authenticate your agent to take action on your behalf.
* **Tools:** Extend your agent's capabilities using a pre-built agent toolset and MCP tools.
* **Skills:** Attach Anthropic or custom skills from your organization's library.

As you configure, Console shows the equivalent API request so you can copy it into your code once you're satisfied.


## Testing an agent

Source: https://platform.claude.com/llms-full.txt#testing-an-agent

Console includes an inline session runner. After configuring your agent, you can start a test session directly, send messages, and watch the event stream without leaving the page. This is the fastest way to check that your system prompt and tool selection produce the behavior you expect.


## From Console to your codebase

Source: https://platform.claude.com/llms-full.txt#from-console-to-your-codebase

Once your agent works as expected:

1. Copy the agent ID and [environment ID](https://platform.claude.com/docs/en/managed-agents/environments) from Console.
2. Reference them in your code when [creating sessions](https://platform.claude.com/docs/en/managed-agents/sessions):

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  session=$(curl -fsSL https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d '{
      "agent": "agent_01J8XkN5uT3vHpLqRfWdY2",
      "environment_id": "env_01K2mPsT7hNwR4jXuLvCqD8",
      "title": "My first session"
    }')

bash CLI
  ant beta:sessions create \
    --agent agent_01J8XkN5uT3vHpLqRfWdY2 \
    --environment-id env_01K2mPsT7hNwR4jXuLvCqD8 \
    --title "My first session"

python Python
  session = client.beta.sessions.create(
      agent="agent_01J8XkN5uT3vHpLqRfWdY2",
      environment_id="env_01K2mPsT7hNwR4jXuLvCqD8",
      title="My first session",
  )

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: "agent_01J8XkN5uT3vHpLqRfWdY2",
    environment_id: "env_01K2mPsT7hNwR4jXuLvCqD8",
    title: "My first session"
  });

csharp C#
  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = "agent_01J8XkN5uT3vHpLqRfWdY2",
      EnvironmentID = "env_01K2mPsT7hNwR4jXuLvCqD8",
      Title = "My first session",
  });

go Go
  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfString: anthropic.String("agent_01J8XkN5uT3vHpLqRfWdY2"),
  	},
  	EnvironmentID: "env_01K2mPsT7hNwR4jXuLvCqD8",
  	Title:         anthropic.String("My first session"),
  })
  if err != nil {
  	panic(err)
  }

java Java
  var session = client.beta().sessions().create(
      SessionCreateParams.builder()
          .agent("agent_01J8XkN5uT3vHpLqRfWdY2")
          .environmentId("env_01K2mPsT7hNwR4jXuLvCqD8")
          .title("My first session")
          .build()
  );

php PHP
  $session = $client->beta->sessions->create(
      agent: 'agent_01J8XkN5uT3vHpLqRfWdY2',
      environmentID: 'env_01K2mPsT7hNwR4jXuLvCqD8',
      title: 'My first session',
  );

ruby Ruby
  session = client.beta.sessions.create(
    agent: "agent_01J8XkN5uT3vHpLqRfWdY2",
    environment_id: "env_01K2mPsT7hNwR4jXuLvCqD8",
    title: "My first session"
  )
  ```
</CodeGroup>


---
title: Migration
url: https://platform.claude.com/docs/en/managed-agents/migration
description: Move an existing agent built on the Messages API or the Claude Agent SDK to Claude Managed Agents.
---

Claude Managed Agents replaces your hand-written agent loop with managed infrastructure. This page covers what changes when you migrate from a custom loop built on the [Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) or from the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview).

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## From a Messages API agent loop

Source: https://platform.claude.com/llms-full.txt#from-a-messages-api-agent-loop

If you built an agent by calling `messages.create` in a `while` loop, running tool calls yourself, and appending results to the conversation history, most of that code goes away.

### What you stop managing

| Before                                                                                           | After                                                                                                                      |
| ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| You maintain the conversation history array and pass it back on every turn.                      | The session stores history server-side. Send events, receive events.                                                       |
| You iterate `tool_use` content blocks, run each tool, and loop back with `tool_result` messages. | Pre-built tools run inside the sandbox automatically. You only handle custom tools through `agent.custom_tool_use` events. |
| You provision your own sandbox for running agent-generated code.                                 | The session sandbox handles code execution, file operations, and bash.                                                     |
| You decide when the loop is done.                                                                | The session emits `session.status_idle` when the agent has nothing more to do.                                             |

### Code comparison

**Before** (Messages API loop, simplified):

<CodeGroup>
  ```python Python
  messages = [{"role": "user", "content": task}]
  while True:
      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          messages=messages,
          tools=tools,
      )
      messages.append({"role": "assistant", "content": response.content})
      if response.stop_reason == "end_turn":
          break
      for block in response.content:
          if block.type == "tool_use":
              result = execute_tool(block.name, block.input)
              messages.append(
                  {
                      "role": "user",
                      "content": [
                          {
                              "type": "tool_result",
                              "tool_use_id": block.id,
                              "content": result,
                          }
                      ],
                  }
              )

typescript TypeScript
  const messages: Anthropic.MessageParam[] = [{ role: "user", content: task }];
  while (true) {
    const response = await client.messages.create({
      model: "claude-opus-5",
      max_tokens: 1024,
      messages,
      tools
    });
    messages.push({ role: "assistant", content: response.content });
    if (response.stop_reason === "end_turn") {
      break;
    }
    for (const block of response.content) {
      if (block.type === "tool_use") {
        const result = executeTool(block.name, block.input);
        messages.push({
          role: "user",
          content: [
            {
              type: "tool_result",
              tool_use_id: block.id,
              content: result
            }
          ]
        });
      }
    }
  }

csharp C#
  List<MessageParam> messages = [new() { Role = Role.User, Content = task }];
  while (true)
  {
      var response = await client.Messages.Create(new()
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages = messages,
          Tools = tools,
      });
      messages.Add(new()
      {
          Role = Role.Assistant,
          Content = new([.. response.Content.Select(block => new ContentBlockParam(block.Json))]),
      });
      if (response.StopReason == StopReason.EndTurn)
      {
          break;
      }
      foreach (var block in response.Content)
      {
          if (block.Value is ToolUseBlock toolUse)
          {
              var result = ExecuteTool(toolUse.Name, toolUse.Input);
              messages.Add(new()
              {
                  Role = Role.User,
                  Content = new([new ToolResultBlockParam { ToolUseID = toolUse.ID, Content = result }]),
              });
          }
      }
  }

go Go
  messages := []anthropic.MessageParam{
  	anthropic.NewUserMessage(anthropic.NewTextBlock(task)),
  }
  for {
  	response, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 1024,
  		Messages:  messages,
  		Tools:     tools,
  	})
  	if err != nil {
  		log.Fatal(err)
  	}
  	messages = append(messages, response.ToParam())
  	if response.StopReason == anthropic.StopReasonEndTurn {
  		break
  	}
  	for _, block := range response.Content {
  		if toolUse, ok := block.AsAny().(anthropic.ToolUseBlock); ok {
  			result := executeTool(toolUse.Name, toolUse.Input)
  			messages = append(messages, anthropic.NewUserMessage(
  				anthropic.NewToolResultBlock(toolUse.ID, result, false),
  			))
  		}
  	}
  }

java Java
  var messages = new ArrayList<MessageParam>();
  messages.add(MessageParam.builder()
      .role(MessageParam.Role.USER)
      .content(task)
      .build());
  while (true) {
      var response = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .messages(messages)
          .tools(tools)
          .build());
      messages.add(response.toParam());
      if (StopReason.END_TURN.equals(response.stopReason().orElse(null))) {
          break;
      }
      for (var block : response.content()) {
          block.toolUse().ifPresent(toolUse -> {
              var result = executeTool(toolUse.name(), toolUse._input());
              messages.add(MessageParam.builder()
                  .role(MessageParam.Role.USER)
                  .contentOfBlockParams(List.of(
                      ContentBlockParam.ofToolResult(ToolResultBlockParam.builder()
                          .toolUseId(toolUse.id())
                          .content(result)
                          .build())))
                  .build());
          });
      }
  }

php PHP
  $messages = [['role' => 'user', 'content' => $task]];
  while (true) {
      $response = $client->messages->create(
          model: 'claude-opus-5',
          maxTokens: 1024,
          messages: $messages,
          tools: $tools,
      );
      $messages[] = ['role' => 'assistant', 'content' => $response->content];
      if ($response->stopReason === 'end_turn') {
          break;
      }
      foreach ($response->content as $block) {
          if ($block->type === 'tool_use') {
              $result = executeTool($block->name, $block->input);
              $messages[] = [
                  'role' => 'user',
                  'content' => [
                      [
                          'type' => 'tool_result',
                          'tool_use_id' => $block->id,
                          'content' => $result,
                      ],
                  ],
              ];
          }
      }
  }

ruby Ruby
  messages = [{ role: "user", content: task }]
  loop do
    response = client.messages.create(
      model: "claude-opus-5",
      max_tokens: 1024,
      messages: messages,
      tools: tools
    )
    messages << { role: "assistant", content: response.content }
    break if response.stop_reason == :end_turn
    response.content.each do |block|
      next unless block.type == :tool_use
      result = execute_tool(block.name, block.input)
      messages << {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: block.id,
            content: result
          }
        ]
      }
    end
  end

bash cURL
  agent=$(
    curl --fail-with-body -sS "https://api.anthropic.com/v1/agents?beta=true" \
      -H "x-api-key: ${ANTHROPIC_API_KEY}" \
      -H "anthropic-version: 2023-06-01" \
      -H "anthropic-beta: managed-agents-2026-04-01" \
      --json '{
        "name": "Task Runner",
        "model": "claude-opus-5",
        "tools": [{"type": "agent_toolset_20260401"}]
      }'
  )
  agent_id=$(jq -r '.id' <<< "${agent}")

  session_id=$(
    curl --fail-with-body -sS "https://api.anthropic.com/v1/sessions?beta=true" \
      -H "x-api-key: ${ANTHROPIC_API_KEY}" \
      -H "anthropic-version: 2023-06-01" \
      -H "anthropic-beta: managed-agents-2026-04-01" \
      --json "$(jq -n --argjson a "${agent}" --arg env "${environment_id}" \
        '{agent: {type: "agent", id: $a.id, version: $a.version}, environment_id: $env}')" \
    | jq -r '.id'
  )

  # Open the SSE stream in the background, then send the user message.
  stream_log=$(mktemp)
  curl --fail-with-body -sS -N \
    "https://api.anthropic.com/v1/sessions/${session_id}/events/stream?beta=true" \
    -H "x-api-key: ${ANTHROPIC_API_KEY}" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    > "${stream_log}" &
  stream_pid=$!

  curl --fail-with-body -sS \
    "https://api.anthropic.com/v1/sessions/${session_id}/events?beta=true" \
    -H "x-api-key: ${ANTHROPIC_API_KEY}" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    --json "$(jq -n --arg text "${task}" \
      '{events: [{type: "user.message", content: [{type: "text", text: $text}]}]}')" \
    > /dev/null

  # Wait for the session to go idle. grep exits at the first match, and
  # reading via process substitution means the shell doesn't wait for
  # tail (a foreground `tail -f | grep -m1` pipeline would hang: tail
  # only dies on its next write, which never comes once the stream is idle).
  grep -m1 '"session.status_idle"' <(tail -f -n +1 "${stream_log}") > /dev/null

  kill "${stream_pid}" 2>/dev/null || true

bash CLI
    { read -r _ agent_id; read -r _ agent_version; } < <(ant beta:agents create \
      --transform '{id,version}' --format yaml < task-runner.agent.yaml)

    session_id=$(ant beta:sessions create \
      --agent "{type: agent, id: $agent_id, version: $agent_version}" \
      --environment-id "$environment_id" \
      --transform id --raw-output)

    # Open the stream first, then send the user message
    exec {stream}< <(ant beta:sessions:events stream \
      --session-id "$session_id" \
      --transform type --raw-output)

    ant beta:sessions:events send \
      --session-id "$session_id" \
      --event "{type: user.message, content: [{type: text, text: \"$task\"}]}" \
    > /dev/null

    # Wait for the session to go idle (grep exits at the first match)
    grep -m1 -x 'session.status_idle' <&"$stream" > /dev/null
    exec {stream}<&-

yaml
      name: Task Runner
      model: claude-opus-5
      tools:
        - type: agent_toolset_20260401

python Python
  agent = client.beta.agents.create(
      name="Task Runner",
      model="claude-opus-5",
      tools=[{"type": "agent_toolset_20260401"}],
  )

  session = client.beta.sessions.create(
      agent={"type": "agent", "id": agent.id, "version": agent.version},
      environment_id=environment.id,
  )

  with client.beta.sessions.events.stream(session.id) as stream:
      client.beta.sessions.events.send(
          session.id,
          events=[{"type": "user.message", "content": [{"type": "text", "text": task}]}],
      )
      for event in stream:
          if event.type == "session.status_idle":
              break

typescript TypeScript
  const agent = await client.beta.agents.create({
    name: "Task Runner",
    model: "claude-opus-5",
    tools: [{ type: "agent_toolset_20260401" }]
  });

  const session = await client.beta.sessions.create({
    agent: { type: "agent", id: agent.id, version: agent.version },
    environment_id: environment.id
  });

  const stream = await client.beta.sessions.events.stream(session.id);

  await client.beta.sessions.events.send(session.id, {
    events: [
      {
        type: "user.message",
        content: [{ type: "text", text: task }]
      }
    ]
  });

  for await (const event of stream) {
    if (event.type === "session.status_idle") {
      break;
    }
  }

csharp C#
  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "Task Runner",
      Model = BetaManagedAgentsModel.ClaudeOpus5,
      Tools =
      [
          new BetaManagedAgentsAgentToolset20260401Params
          {
              Type = "agent_toolset_20260401",
          },
      ],
  });

  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = new BetaManagedAgentsAgentParams
      {
          Type = "agent",
          ID = agent.ID,
          Version = agent.Version,
      },
      EnvironmentID = environment.ID,
  });

  var stream = client.Beta.Sessions.Events.StreamStreaming(session.ID);

  await client.Beta.Sessions.Events.Send(session.ID, new()
  {
      Events =
      [
          new BetaManagedAgentsUserMessageEventParams
          {
              Type = "user.message",
              Content = [new BetaManagedAgentsTextBlock { Type = "text", Text = task }],
          },
      ],
  });

  await foreach (var streamEvent in stream)
  {
      if (streamEvent.Value is BetaManagedAgentsSessionStatusIdleEvent)
      {
          break;
      }
  }

go Go
  	agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  		Name: "Task Runner",
  		Model: anthropic.BetaManagedAgentsModelConfigParams{
  			ID: anthropic.BetaManagedAgentsModelClaudeOpus5,
  		},
  		Tools: []anthropic.BetaAgentNewParamsToolUnion{{
  			OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  				Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  			},
  		}},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  		Agent: anthropic.BetaSessionNewParamsAgentUnion{
  			OfBetaManagedAgentsAgents: &anthropic.BetaManagedAgentsAgentParams{
  				Type:    anthropic.BetaManagedAgentsAgentParamsTypeAgent,
  				ID:      agent.ID,
  				Version: anthropic.Int(agent.Version),
  			},
  		},
  		EnvironmentID: environment.ID,
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	stream := client.Beta.Sessions.Events.StreamEvents(ctx, session.ID, anthropic.BetaSessionEventStreamParams{})
  	defer stream.Close()

  	_, err = client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  		Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  			OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
  				Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
  				Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{{
  					OfText: &anthropic.BetaManagedAgentsTextBlockParam{
  						Type: anthropic.BetaManagedAgentsTextBlockTypeText,
  						Text: task,
  					},
  				}},
  			},
  		}},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	for stream.Next() {
  		event := stream.Current()
  		if event.Type == "session.status_idle" {
  			break
  		}
  	}
  	if err := stream.Err(); err != nil {
  		log.Fatal(err)
  	}

java Java
      var agent = client.beta().agents().create(
          AgentCreateParams.builder()
              .name("Task Runner")
              .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
              .addTool(
                  BetaManagedAgentsAgentToolset20260401Params.builder()
                      .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
                      .build()
              )
              .build()
      );

      var session = client.beta().sessions().create(
          SessionCreateParams.builder()
              .agent(
                  BetaManagedAgentsAgentParams.builder()
                      .type(BetaManagedAgentsAgentParams.Type.AGENT)
                      .id(agent.id())
                      .version(agent.version())
                      .build()
              )
              .environmentId(environment.id())
              .build()
      );

      try (var stream = client.beta().sessions().events().streamStreaming(session.id())) {
          client.beta().sessions().events().send(
              session.id(),
              EventSendParams.builder()
                  .addEvent(
                      BetaManagedAgentsUserMessageEventParams.builder()
                          .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
                          .addTextContent(task)
                          .build()
                  )
                  .build()
          );
          stream.stream()
              .takeWhile(event -> !event.isSessionStatusIdle())
              .forEach(_ -> {});
      }

php PHP
  $agent = $client->beta->agents->create(
      name: 'Task Runner',
      model: 'claude-opus-5',
      tools: [
          BetaManagedAgentsAgentToolset20260401Params::with(
              type: 'agent_toolset_20260401',
          ),
      ],
  );

  $session = $client->beta->sessions->create(
      agent: BetaManagedAgentsAgentParams::with(
          type: 'agent',
          id: $agent->id,
          version: $agent->version,
      ),
      environmentID: $environment->id,
  );

  $stream = $client->beta->sessions->events->streamStream($session->id);

  $client->beta->sessions->events->send(
      $session->id,
      events: [
          [
              'type' => 'user.message',
              'content' => [['type' => 'text', 'text' => $task]],
          ],
      ],
  );

  foreach ($stream as $event) {
      if ($event->type === 'session.status_idle') {
          break;
      }
  }

ruby Ruby
  agent = client.beta.agents.create(
    name: "Task Runner",
    model: "claude-opus-5",
    tools: [{type: "agent_toolset_20260401"}]
  )

  session = client.beta.sessions.create(
    agent: {type: "agent", id: agent.id, version: agent.version},
    environment_id: environment.id
  )

  stream = client.beta.sessions.events.stream_events(session.id)
  client.beta.sessions.events.send_(
    session.id,
    events: [{type: "user.message", content: [{type: "text", text: task}]}]
  )
  stream.each do
    break if it.type == :"session.status_idle"
  end
  ```
</CodeGroup>

### What you still control

* **System prompt and model:** Same fields, now on the agent definition.
* **Custom tools:** Still declared with JSON Schema. Execution moves from inline handling to responding to `agent.custom_tool_use` events. See [Session event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming).
* **Web search and web fetch settings:** Same `allowed_domains`, `blocked_domains`, `max_content_tokens`, and `user_location` fields, now set once on the `web_search` and `web_fetch` entries of the agent toolset's `configs` array instead of on every request. The `max_uses`, `citations`, and `cache_control` fields are not available. See [Restrict web search and web fetch domains](https://platform.claude.com/docs/en/managed-agents/tools#restrict-web-search-and-web-fetch-domains).
* **Context:** You can still inject context through the system prompt, [file resources](https://platform.claude.com/docs/en/managed-agents/files), or [skills](https://platform.claude.com/docs/en/managed-agents/skills).


## From the Claude Agent SDK

Source: https://platform.claude.com/llms-full.txt#from-the-claude-agent-sdk

If you built with the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview), you're already working with agents, tools, and sessions as concepts. The difference is where they run: the SDK runs in a process you operate, while Managed Agents runs in Anthropic's infrastructure. Most of the migration is mapping SDK configuration objects to their API-side equivalents.

### What changes

| Agent SDK                                                       | Managed Agents                                                                                                                                                                                                                                                                |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ClaudeAgentOptions(...)` constructed per run                   | `client.beta.agents.create(...)` once; the Agent is persisted and versioned server-side. See [Agent setup](https://platform.claude.com/docs/en/managed-agents/agent-setup).                                                                                                   |
| `async with ClaudeSDKClient(...)` or `query(...)`               | `client.beta.sessions.create(...)` then send and receive [events](https://platform.claude.com/docs/en/managed-agents/events-and-streaming).                                                                                                                                   |
| `@tool`-decorated functions dispatched automatically by the SDK | Declare as `{"type": "custom", ...}` on the Agent; your client handles `agent.custom_tool_use` events and replies with `user.custom_tool_result`. See [Tools](https://platform.claude.com/docs/en/managed-agents/tools).                                                      |
| Built-in tools run in your process against your filesystem      | `{"type": "agent_toolset_20260401"}` runs the same tools inside the session sandbox against `/workspace`.                                                                                                                                                                     |
| `cwd`, `add_dirs` point at local paths                          | Upload or mount [files](https://platform.claude.com/docs/en/managed-agents/files) as session resources.                                                                                                                                                                       |
| `system_prompt` and the `CLAUDE.md` hierarchy                   | A single `system` string on the Agent. Each update that changes the agent produces a new server-side version; pin sessions to a specific version to promote or roll back without a deploy. See [Agent setup](https://platform.claude.com/docs/en/managed-agents/agent-setup). |
| `mcp_servers` configured and authenticated in one place         | Declare servers on the Agent; provide credentials through a [Vault](https://platform.claude.com/docs/en/managed-agents/vaults) on the Session.                                                                                                                                |
| `permission_mode`, `can_use_tool`                               | Per-tool [`permission_policy`](https://platform.claude.com/docs/en/managed-agents/permission-policies); send `user.tool_confirmation` events for `always_ask` tools.                                                                                                          |

### Code comparison

**Before** (Agent SDK):

<CodeGroup exclude="shell, csharp, go, java, php, ruby">
  ```python Python
  from claude_agent_sdk import (
      ClaudeAgentOptions,
      ClaudeSDKClient,
      create_sdk_mcp_server,
      tool,
  )


  @tool("get_weather", "Get the current weather for a city.", {"city": str})
  async def get_weather(args: dict) -> dict:
      return {"content": [{"type": "text", "text": f"{args['city']}: 18°C, clear"}]}


  options = ClaudeAgentOptions(
      model="claude-opus-5",
      system_prompt="You are a concise weather assistant.",
      mcp_servers={
          "weather": create_sdk_mcp_server("weather", "1.0", tools=[get_weather])
      },
  )

  async with ClaudeSDKClient(options=options) as agent:
      await agent.query("What's the weather in Tokyo?")
      async for msg in agent.receive_response():
          print(msg)

typescript TypeScript
  import { createSdkMcpServer, query, tool } from "@anthropic-ai/claude-agent-sdk";
  import { z } from "zod";

  const getWeather = tool(
    "get_weather",
    "Get the current weather for a city.",
    { city: z.string() },
    async (args) => ({
      content: [{ type: "text", text: `${args.city}: 18°C, clear` }]
    })
  );

  for await (const message of query({
    prompt: "What's the weather in Tokyo?",
    options: {
      model: "claude-opus-5",
      systemPrompt: "You are a concise weather assistant.",
      mcpServers: {
        weather: createSdkMcpServer({ name: "weather", version: "1.0", tools: [getWeather] })
      }
    }
  })) {
    console.log(message);
  }

python Python
  from anthropic import Anthropic

  client = Anthropic()

  agent = client.beta.agents.create(
      name="weather-agent",
      model="claude-opus-5",
      system="You are a concise weather assistant.",
      tools=[
          {
              "type": "custom",
              "name": "get_weather",
              "description": "Get the current weather for a city.",
              "input_schema": {
                  "type": "object",
                  "properties": {"city": {"type": "string"}},
                  "required": ["city"],
              },
          }
      ],
  )
  environment = client.beta.environments.create(
      name="weather-env",
      config={"type": "cloud", "networking": {"type": "unrestricted"}},
  )

  session = client.beta.sessions.create(
      agent={"type": "agent", "id": agent.id, "version": agent.version},
      environment_id=environment.id,
  )


  def get_weather(city: str) -> str:
      return f"{city}: 18°C, clear"


  with client.beta.sessions.events.stream(session.id) as stream:
      client.beta.sessions.events.send(
          session.id,
          events=[
              {
                  "type": "user.message",
                  "content": [{"type": "text", "text": "What's the weather in Tokyo?"}],
              }
          ],
      )
      for event in stream:
          if event.type == "agent.message":
              print(
                  "".join(block.text for block in event.content if block.type == "text")
              )
          elif event.type == "agent.custom_tool_use":
              result = get_weather(**event.input)
              client.beta.sessions.events.send(
                  session.id,
                  events=[
                      {
                          "type": "user.custom_tool_result",
                          "custom_tool_use_id": event.id,
                          "content": [{"type": "text", "text": result}],
                      }
                  ],
              )
          elif (
              event.type == "session.status_idle"
              and event.stop_reason
              and event.stop_reason.type == "end_turn"
          ):
              break

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";

  const client = new Anthropic();

  const agent = await client.beta.agents.create({
    name: "weather-agent",
    model: "claude-opus-5",
    system: "You are a concise weather assistant.",
    tools: [
      {
        type: "custom",
        name: "get_weather",
        description: "Get the current weather for a city.",
        input_schema: {
          type: "object",
          properties: { city: { type: "string" } },
          required: ["city"]
        }
      }
    ]
  });
  const environment = await client.beta.environments.create({
    name: "weather-env",
    config: { type: "cloud", networking: { type: "unrestricted" } }
  });

  const session = await client.beta.sessions.create({
    agent: { type: "agent", id: agent.id, version: agent.version },
    environment_id: environment.id
  });

  function getWeather({ city }: Record<string, unknown>): string {
    return `${city}: 18°C, clear`;
  }

  const stream = await client.beta.sessions.events.stream(session.id);

  await client.beta.sessions.events.send(session.id, {
    events: [
      {
        type: "user.message",
        content: [{ type: "text", text: "What's the weather in Tokyo?" }]
      }
    ]
  });

  for await (const event of stream) {
    if (event.type === "agent.message") {
      for (const block of event.content) {
        if (block.type === "text") {
          console.log(block.text);
        }
      }
    } else if (event.type === "agent.custom_tool_use") {
      const result = getWeather(event.input);
      await client.beta.sessions.events.send(session.id, {
        events: [
          {
            type: "user.custom_tool_result",
            custom_tool_use_id: event.id,
            content: [{ type: "text", text: result }]
          }
        ]
      });
    } else if (event.type === "session.status_idle" && event.stop_reason?.type === "end_turn") {
      break;
    }
  }

csharp C#
  using System.Text.Json;

  using Anthropic.Models.Beta.Agents;
  using Anthropic.Models.Beta.Environments;
  using Anthropic.Models.Beta.Sessions;
  using Anthropic.Models.Beta.Sessions.Events;

  AnthropicClient client = new();

  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "weather-agent",
      Model = BetaManagedAgentsModel.ClaudeOpus5,
      System = "You are a concise weather assistant.",
      Tools =
      [
          new BetaManagedAgentsCustomToolParams
          {
              Type = "custom",
              Name = "get_weather",
              Description = "Get the current weather for a city.",
              InputSchema = new()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["city"] = JsonSerializer.SerializeToElement(new { type = "string" }),
                  },
                  Required = ["city"],
              },
          },
      ],
  });
  var environment = await client.Beta.Environments.Create(new()
  {
      Name = "weather-env",
      Config = new BetaCloudConfigParams
      {
          Networking = new BetaUnrestrictedNetwork(),
      },
  });

  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = new BetaManagedAgentsAgentParams
      {
          Type = "agent",
          ID = agent.ID,
          Version = agent.Version,
      },
      EnvironmentID = environment.ID,
  });

  static string GetWeather(string city) => $"{city}: 18°C, clear";

  using var stream = await client.Beta.Sessions.Events.WithRawResponse.StreamStreaming(session.ID);

  await client.Beta.Sessions.Events.Send(session.ID, new()
  {
      Events =
      [
          new BetaManagedAgentsUserMessageEventParams
          {
              Type = "user.message",
              Content = [new BetaManagedAgentsTextBlock { Type = "text", Text = "What's the weather in Tokyo?" }],
          },
      ],
  });

  await foreach (var streamEvent in stream.Enumerate())
  {
      if (streamEvent.Value is BetaManagedAgentsAgentMessageEvent message)
      {
          Console.WriteLine(string.Concat(message.Content.Select(block => block.Text)));
      }
      else if (streamEvent.Value is BetaManagedAgentsAgentCustomToolUseEvent toolUse)
      {
          var result = GetWeather(toolUse.Input["city"].GetString()!);
          await client.Beta.Sessions.Events.Send(session.ID, new()
          {
              Events =
              [
                  new BetaManagedAgentsUserCustomToolResultEventParams
                  {
                      Type = "user.custom_tool_result",
                      CustomToolUseID = toolUse.ID,
                      Content =
                      [
                          new BetaManagedAgentsTextBlock
                          {
                              Type = "text",
                              Text = result,
                          },
                      ],
                  },
              ],
          });
      }
      else if (streamEvent.Value is BetaManagedAgentsSessionStatusIdleEvent idle
          && idle.StopReason?.Value is BetaManagedAgentsSessionEndTurn)
      {
          break;
      }
  }

go Go
  client := anthropic.NewClient()
  ctx := context.Background()

  agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name: "weather-agent",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID: anthropic.BetaManagedAgentsModelClaudeOpus5,
  	},
  	System: anthropic.String("You are a concise weather assistant."),
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{{
  		OfCustom: &anthropic.BetaManagedAgentsCustomToolParams{
  			Type:        anthropic.BetaManagedAgentsCustomToolParamsTypeCustom,
  			Name:        "get_weather",
  			Description: "Get the current weather for a city.",
  			InputSchema: anthropic.BetaManagedAgentsCustomToolInputSchemaParam{
  				Properties: map[string]any{
  					"city": map[string]any{"type": "string"},
  				},
  				Required: []string{"city"},
  			},
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }
  environment, err := client.Beta.Environments.New(ctx, anthropic.BetaEnvironmentNewParams{
  	Name: "weather-env",
  	Config: anthropic.BetaEnvironmentNewParamsConfigUnion{
  		OfCloud: &anthropic.BetaCloudConfigParams{
  			Networking: anthropic.BetaCloudConfigParamsNetworkingUnion{
  				OfUnrestricted: &anthropic.BetaUnrestrictedNetworkParam{},
  			},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfBetaManagedAgentsAgents: &anthropic.BetaManagedAgentsAgentParams{
  			Type:    anthropic.BetaManagedAgentsAgentParamsTypeAgent,
  			ID:      agent.ID,
  			Version: anthropic.Int(agent.Version),
  		},
  	},
  	EnvironmentID: environment.ID,
  })
  if err != nil {
  	panic(err)
  }

  getWeather := func(city string) string {
  	return fmt.Sprintf("%s: 18°C, clear", city)
  }

  stream := client.Beta.Sessions.Events.StreamEvents(ctx, session.ID, anthropic.BetaSessionEventStreamParams{})
  defer stream.Close()

  _, err = client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  	Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  		OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
  			Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
  			Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{{
  				OfText: &anthropic.BetaManagedAgentsTextBlockParam{
  					Type: anthropic.BetaManagedAgentsTextBlockTypeText,
  					Text: "What's the weather in Tokyo?",
  				},
  			}},
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }

  loop:
  for stream.Next() {
  	event := stream.Current()
  	switch event.Type {
  	case "agent.message":
  		for _, block := range event.AsAgentMessage().Content {
  			if block.Type == "text" {
  				fmt.Println(block.Text)
  			}
  		}
  	case "agent.custom_tool_use":
  		toolUse := event.AsAgentCustomToolUse()
  		result := getWeather(toolUse.Input["city"].(string))
  		if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  			Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  				OfUserCustomToolResult: &anthropic.BetaManagedAgentsUserCustomToolResultEventParams{
  					Type:            anthropic.BetaManagedAgentsUserCustomToolResultEventParamsTypeUserCustomToolResult,
  					CustomToolUseID: toolUse.ID,
  					Content: []anthropic.BetaManagedAgentsUserCustomToolResultEventParamsContentUnion{{
  						OfText: &anthropic.BetaManagedAgentsTextBlockParam{
  							Type: anthropic.BetaManagedAgentsTextBlockTypeText,
  							Text: result,
  						},
  					}},
  				},
  			}},
  		}); err != nil {
  			panic(err)
  		}
  	case "session.status_idle":
  		idle := event.AsSessionStatusIdle()
  		if _, ok := idle.StopReason.AsAny().(anthropic.BetaManagedAgentsSessionEndTurn); ok {
  			break loop
  		}
  	}
  }
  if err := stream.Err(); err != nil {
  	panic(err)
  }

java Java
  import java.util.Map;
  import java.util.function.Function;

  import com.anthropic.models.beta.agents.AgentCreateParams;
  import com.anthropic.models.beta.agents.BetaManagedAgentsCustomToolInputSchema;
  import com.anthropic.models.beta.agents.BetaManagedAgentsCustomToolParams;
  import com.anthropic.models.beta.agents.BetaManagedAgentsModel;
  import com.anthropic.models.beta.environments.BetaCloudConfigParams;
  import com.anthropic.models.beta.environments.BetaUnrestrictedNetwork;
  import com.anthropic.models.beta.environments.EnvironmentCreateParams;
  import com.anthropic.models.beta.sessions.BetaManagedAgentsAgentParams;
  import com.anthropic.models.beta.sessions.SessionCreateParams;
  import com.anthropic.models.beta.sessions.events.BetaManagedAgentsStreamSessionEvents;
  import com.anthropic.models.beta.sessions.events.BetaManagedAgentsUserCustomToolResultEventParams;
  import com.anthropic.models.beta.sessions.events.BetaManagedAgentsUserMessageEventParams;
  import com.anthropic.models.beta.sessions.events.EventSendParams;

  var client = AnthropicOkHttpClient.fromEnv();

  var agent = client.beta().agents().create(AgentCreateParams.builder()
      .name("weather-agent")
      .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
      .system("You are a concise weather assistant.")
      .addTool(BetaManagedAgentsCustomToolParams.builder()
          .type(BetaManagedAgentsCustomToolParams.Type.CUSTOM)
          .name("get_weather")
          .description("Get the current weather for a city.")
          .inputSchema(BetaManagedAgentsCustomToolInputSchema.builder()
              .properties(BetaManagedAgentsCustomToolInputSchema.Properties.builder()
                  .putAdditionalProperty("city", JsonValue.from(Map.of("type", "string")))
                  .build())
              .addRequired("city")
              .build())
          .build())
      .build());
  var environment = client.beta().environments().create(EnvironmentCreateParams.builder()
      .name("weather-env")
      .config(BetaCloudConfigParams.builder()
          .networking(BetaUnrestrictedNetwork.builder().build())
          .build())
      .build());

  var session = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(BetaManagedAgentsAgentParams.builder()
          .type(BetaManagedAgentsAgentParams.Type.AGENT)
          .id(agent.id())
          .version(agent.version())
          .build())
      .environmentId(environment.id())
      .build());

  Function<String, String> getWeather = city -> city + ": 18°C, clear";

  try (var stream = client.beta().sessions().events().streamStreaming(session.id())) {
      client.beta().sessions().events().send(
          session.id(),
          EventSendParams.builder()
              .addEvent(BetaManagedAgentsUserMessageEventParams.builder()
                  .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
                  .addTextContent("What's the weather in Tokyo?")
                  .build())
              .build());

      for (var event : (Iterable<BetaManagedAgentsStreamSessionEvents>) stream.stream()::iterator) {
          if (event.isAgentMessage()) {
              for (var block : event.asAgentMessage().content()) {
                  block.text().ifPresent(textBlock -> IO.println(textBlock.text()));
              }
          } else if (event.isAgentCustomToolUse()) {
              var toolUse = event.asAgentCustomToolUse();
              var city = toolUse.input()._additionalProperties().get("city").asStringOrThrow();
              var result = getWeather.apply(city);
              client.beta().sessions().events().send(
                  session.id(),
                  EventSendParams.builder()
                      .addEvent(BetaManagedAgentsUserCustomToolResultEventParams.builder()
                          .type(BetaManagedAgentsUserCustomToolResultEventParams.Type.USER_CUSTOM_TOOL_RESULT)
                          .customToolUseId(toolUse.id())
                          .addTextContent(result)
                          .build())
                      .build());
          } else if (event.isSessionStatusIdle()
              && event.asSessionStatusIdle().stopReason().isEndTurn()) {
              break;
          }
      }
  }

php PHP
  use Anthropic\Client;
  use Anthropic\Beta\Agents\BetaManagedAgentsCustomToolInputSchema;
  use Anthropic\Beta\Agents\BetaManagedAgentsCustomToolParams;
  use Anthropic\Beta\Sessions\BetaManagedAgentsAgentParams;

  $client = new Client();

  $agent = $client->beta->agents->create(
      name: 'weather-agent',
      model: 'claude-opus-5',
      system: 'You are a concise weather assistant.',
      tools: [
          BetaManagedAgentsCustomToolParams::with(
              type: 'custom',
              name: 'get_weather',
              description: 'Get the current weather for a city.',
              inputSchema: BetaManagedAgentsCustomToolInputSchema::with(
                  properties: ['city' => ['type' => 'string']],
                  required: ['city'],
              ),
          ),
      ],
  );
  $environment = $client->beta->environments->create(
      name: 'weather-env',
      config: ['type' => 'cloud', 'networking' => ['type' => 'unrestricted']],
  );

  $session = $client->beta->sessions->create(
      agent: BetaManagedAgentsAgentParams::with(
          type: 'agent',
          id: $agent->id,
          version: $agent->version,
      ),
      environmentID: $environment->id,
  );

  function getWeather(string $city): string
  {
      return "{$city}: 18°C, clear";
  }

  $stream = $client->beta->sessions->events->streamStream($session->id);

  $client->beta->sessions->events->send(
      $session->id,
      events: [
          [
              'type' => 'user.message',
              'content' => [['type' => 'text', 'text' => "What's the weather in Tokyo?"]],
          ],
      ],
  );

  foreach ($stream as $event) {
      if ($event->type === 'agent.message') {
          foreach ($event->content as $block) {
              if ($block->type === 'text') {
                  echo $block->text . "\n";
              }
          }
      } elseif ($event->type === 'agent.custom_tool_use') {
          $result = getWeather($event->input['city']);
          $client->beta->sessions->events->send(
              $session->id,
              events: [
                  [
                      'type' => 'user.custom_tool_result',
                      'custom_tool_use_id' => $event->id,
                      'content' => [['type' => 'text', 'text' => $result]],
                  ],
              ],
          );
      } elseif ($event->type === 'session.status_idle' && $event->stopReason?->type === 'end_turn') {
          break;
      }
  }
  $stream->close();

ruby Ruby
  require "anthropic"

  client = Anthropic::Client.new

  agent = client.beta.agents.create(
    name: "weather-agent",
    model: "claude-opus-5",
    system_: "You are a concise weather assistant.",
    tools: [
      {
        type: "custom",
        name: "get_weather",
        description: "Get the current weather for a city.",
        input_schema: {
          type: "object",
          properties: {city: {type: "string"}},
          required: ["city"]
        }
      }
    ]
  )
  environment = client.beta.environments.create(
    name: "weather-env",
    config: {type: "cloud", networking: {type: "unrestricted"}}
  )

  session = client.beta.sessions.create(
    agent: {type: "agent", id: agent.id, version: agent.version},
    environment_id: environment.id
  )

  def get_weather(city)
    "#{city}: 18°C, clear"
  end

  stream = client.beta.sessions.events.stream_events(session.id)
  client.beta.sessions.events.send_(
    session.id,
    events: [{type: "user.message", content: [{type: "text", text: "What's the weather in Tokyo?"}]}]
  )

  stream.each do |event|
    case event.type
    when :"agent.message"
      event.content.each do |block|
        puts block.text if block.type == :text
      end
    when :"agent.custom_tool_use"
      result = get_weather(event.input[:city])
      client.beta.sessions.events.send_(
        session.id,
        events: [
          {
            type: "user.custom_tool_result",
            custom_tool_use_id: event.id,
            content: [{type: "text", text: result}]
          }
        ]
      )
    when :"session.status_idle"
      break if event.stop_reason&.type == :end_turn
    end
  end
  ```
</CodeGroup>

The Agent and Environment are created once and reused across sessions. The tool function still runs in your process; the difference is that you read the `agent.custom_tool_use` event and send the result explicitly instead of the SDK dispatching it for you.

### Features that move to your client

The tradeoff for Anthropic running the agent loop is that a few things the SDK handled automatically become your client's responsibility.

| SDK feature                        | Managed Agents approach                                                                                                                                       |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Plan mode                          | Run a planning-only session first, then a second session to run the plan.                                                                                     |
| Output styles, slash commands      | Apply in your client before sending `user.message` or after receiving `agent.message`.                                                                        |
| `PreToolUse` / `PostToolUse` hooks | Your client already sees every `agent.custom_tool_use` event before responding; put the logic there. For built-in tools, use `permission_policy: always_ask`. |
| `max_turns`                        | Count turns client-side.                                                                                                                                      |


## Migration checklist

Source: https://platform.claude.com/llms-full.txt#migration-checklist

1. [Create an environment](https://platform.claude.com/docs/en/managed-agents/environments) with the networking and runtimes your agent needs.
2. Port your system prompt and tool selection to an [agent definition](https://platform.claude.com/docs/en/managed-agents/agent-setup).
3. Replace your loop with [`sessions.create`](https://platform.claude.com/docs/en/managed-agents/sessions) and [`sessions.events.stream`](https://platform.claude.com/docs/en/managed-agents/events-and-streaming).
4. For any local files the agent reads, upload them through the [Files API](https://platform.claude.com/docs/en/managed-agents/files) and mount them as `resources`.
5. For any custom tool handlers, move execution into your event loop as responses to `agent.custom_tool_use` events.
6. Verify with a test session before pointing production traffic at the new flow.


## Migrating between model versions

Source: https://platform.claude.com/llms-full.txt#migrating-between-model-versions

When a new Claude model is released, migrating a Claude Managed Agents integration is typically a one-field change: update `model` on your [agent definition](https://platform.claude.com/docs/en/managed-agents/agent-setup) and the change takes effect on the next session you create.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl -sS --fail-with-body "https://api.anthropic.com/v1/agents/$AGENT_ID?beta=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    --json "$(jq -n --argjson version "$AGENT_VERSION" '{version: $version, model: "claude-opus-5"}')"

bash CLI
    ant beta:agents update --agent-id "$AGENT_ID" < agent.yaml

yaml
      name: Task Runner
      model: claude-opus-5
      system: You are a task automation agent. Complete the task you are given end to end.
      tools:
        - type: agent_toolset_20260401

python Python
  client.beta.agents.update(
      agent.id,
      version=agent.version,
      model="claude-opus-5",
  )

typescript TypeScript
  await client.beta.agents.update(agent.id, {
    version: agent.version,
    model: "claude-opus-5"
  });

csharp C#
  await client.Beta.Agents.Update(agent.ID, new()
  {
      Version = agent.Version,
      Model = BetaManagedAgentsModel.ClaudeOpus5,
  });

go Go
  _, err = client.Beta.Agents.Update(ctx, agent.ID, anthropic.BetaAgentUpdateParams{
  	Version: agent.Version,
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID: anthropic.BetaManagedAgentsModelClaudeOpus5,
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().agents().update(
      agent.id(),
      AgentUpdateParams.builder()
          .version(agent.version())
          .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
          .build()
  );

php PHP
  $client->beta->agents->update(
      $agent->id,
      version: $agent->version,
      model: 'claude-opus-5',
  );

ruby Ruby
  client.beta.agents.update(
    agent.id,
    version: agent.version,
    model: "claude-opus-5"
  )
  ```
</CodeGroup>

Most model-level behavior changes documented in the [Messages API migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide) do not require action on your side:

* **Request parameter changes** (`max_tokens` defaults, `thinking` configuration) are handled by the Claude Managed Agents runtime. These fields are not exposed on the agent definition.
* **Assistant message prefilling** does not exist in the event-based session model, so its removal on newer models is a no-op.
* **Tool argument JSON escaping** is parsed by the runtime before you receive `agent.custom_tool_use` events. You see structured data, not raw strings.

The behavior descriptions in the Messages API guide (what the model does differently) still apply. The migration steps (how to change your request code) do not.


### Define your agent

---
title: Define your agent
url: https://platform.claude.com/docs/en/managed-agents/agent-setup
description: Create a reusable, versioned agent configuration.
---

An agent is a reusable, versioned configuration that defines persona and capabilities. It bundles the model, system prompt, tools, MCP servers, and skills that shape how Claude behaves during a session.

Create the agent once as a reusable resource and reference it by ID each time you [start a session](https://platform.claude.com/docs/en/managed-agents/sessions). Agents are versioned and easier to manage across many sessions.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Agent configuration fields

Source: https://platform.claude.com/llms-full.txt#agent-configuration-fields

| Field         | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`        | Required. A human-readable name for the agent.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `model`       | Required. The Claude [model](https://platform.claude.com/docs/en/models/overview) that powers the agent. Accepts a model ID string or an object, for example `{"id": "claude-opus-5"}`. Claude 4.5 and later models are supported. The object form also accepts `speed`, `effort`, and `inference_geo` fields; see the tips under [Create an agent](https://platform.claude.com/docs/en/managed-agents/agent-setup#create-an-agent), [Effort levels](https://platform.claude.com/docs/en/build-with-claude/effort#effort-levels), and [Pin the inference geo](https://platform.claude.com/docs/en/managed-agents/agent-setup#pin-the-inference-geo). |
| `system`      | A [system prompt](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#give-claude-a-role) that defines the agent's behavior and persona. The system prompt is distinct from [user messages](https://platform.claude.com/docs/en/managed-agents/reference#event-types), which should describe the work to be done.                                                                                                                                                                                                                                                                               |
| `tools`       | The tools available to the agent. Combines [pre-built agent tools](https://platform.claude.com/docs/en/managed-agents/tools), [MCP tools](https://platform.claude.com/docs/en/managed-agents/mcp-connector), and [custom tools](https://platform.claude.com/docs/en/managed-agents/tools#custom-tools).                                                                                                                                                                                                                                                                                                                                              |
| `mcp_servers` | [MCP servers](https://platform.claude.com/docs/en/managed-agents/mcp-connector) that provide standardized third-party capabilities.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `skills`      | [Skills](https://platform.claude.com/docs/en/managed-agents/skills) that supply domain-specific context with progressive disclosure.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `multiagent`  | A coordinator declaration listing the agents this agent can delegate to. See [Multiagent orchestration](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration).                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `description` | A description of what the agent does.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `metadata`    | Arbitrary key-value pairs for your own tracking.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

You can also override `model`, `system`, `tools`, `mcp_servers`, and `skills` for a single session without changing the agent. An `effort` level set inside a per-session `model` override isn't applied, and because the override replaces the agent's `model` object in full, a session created with a `model` override runs at the model's default effort level; to run at a specific effort level, set `effort` on the agent and don't override `model` for that session. See [Override agent configuration for a session](https://platform.claude.com/docs/en/managed-agents/sessions#override-agent-configuration-for-a-session).


## Create an agent

Source: https://platform.claude.com/llms-full.txt#create-an-agent

The following example defines a coding agent that uses Claude Opus 5 with access to the pre-built agent toolset. The toolset lets the agent write code, read files, search the web, and more. See the [agent tools reference](https://platform.claude.com/docs/en/managed-agents/tools) for the full list of supported tools.

The examples use curl, the `ant` CLI, or one of the SDKs. If you haven't set one up, the [quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart#install-the-cli) covers installation and client setup.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  agent=$(curl -fsSL https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d '{
      "name": "Coding Assistant",
      "model": "claude-opus-5",
      "system": "You are a helpful coding agent.",
      "tools": [{"type": "agent_toolset_20260401"}]
    }')

  AGENT_ID=$(jq -r '.id' <<< "$agent")
  AGENT_VERSION=$(jq -r '.version' <<< "$agent")

bash CLI
    agent=$(ant beta:agents create --format json < coding-assistant.agent.yaml)

    AGENT_ID=$(jq -r '.id' <<< "$agent")

yaml
      name: Coding Assistant
      model:
        id: claude-opus-5
      system: You are a helpful coding agent.
      tools:
        - type: agent_toolset_20260401

python Python
  agent = client.beta.agents.create(
      name="Coding Assistant",
      model="claude-opus-5",
      system="You are a helpful coding agent.",
      tools=[
          {"type": "agent_toolset_20260401"},
      ],
  )

typescript TypeScript
  const agent = await client.beta.agents.create({
    name: "Coding Assistant",
    model: "claude-opus-5",
    system: "You are a helpful coding agent.",
    tools: [{ type: "agent_toolset_20260401" }],
  });

csharp C#
  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "Coding Assistant",
      Model = BetaManagedAgentsModel.ClaudeOpus5,
      System = "You are a helpful coding agent.",
      Tools =
      [
          new BetaManagedAgentsAgentToolset20260401Params
          {
              Type = "agent_toolset_20260401",
          },
      ],
  });

go Go
  agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name: "Coding Assistant",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID: anthropic.BetaManagedAgentsModelClaudeOpus5,
  	},
  	System: anthropic.String("You are a helpful coding agent."),
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{{
  		OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  			Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }

java Java
  var agent = client.beta().agents().create(
      AgentCreateParams.builder()
          .name("Coding Assistant")
          .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
          .system("You are a helpful coding agent.")
          .addTool(
              BetaManagedAgentsAgentToolset20260401Params.builder()
                  .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
                  .build()
          )
          .build()
  );

php PHP
  $agent = $client->beta->agents->create(
      name: 'Coding Assistant',
      model: 'claude-opus-5',
      system: 'You are a helpful coding agent.',
      tools: [
          BetaManagedAgentsAgentToolset20260401Params::with(
              type: 'agent_toolset_20260401',
          ),
      ],
  );

ruby Ruby
  agent = client.beta.agents.create(
    name: "Coding Assistant",
    model: "claude-opus-5",
    system_: "You are a helpful coding agent.",
    tools: [{type: "agent_toolset_20260401"}]
  )

json
{
  "id": "agent_01HqR2k7vXbZ9mNpL3wYcT8f",
  "type": "agent",
  "name": "Coding Assistant",
  "model": {
    "id": "claude-opus-5",
    "effort": { "type": "high" },
    "speed": "standard"
  },
  "system": "You are a helpful coding agent.",
  "description": null,
  "tools": [
    {
      "type": "agent_toolset_20260401",
      "default_config": {
        "permission_policy": { "type": "always_allow" }
      }
    }
  ],
  "skills": [],
  "mcp_servers": [],
  "multiagent": null,
  "metadata": {},
  "version": 1,
  "created_at": "2026-04-03T18:24:10.412Z",
  "updated_at": "2026-04-03T18:24:10.412Z",
  "archived_at": null
}

bash cURL
  agent=$(curl -fsSL https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d '{
      "name": "Geo-pinned assistant",
      "model": {"id": "claude-opus-5", "inference_geo": "us"},
      "system": "You are a helpful assistant."
    }')

  echo "Inference geo: $(jq -r '.model.inference_geo' <<< "$agent")"

bash CLI
    agent=$(ant beta:agents create --format json < geo-pinned.agent.yaml)

    echo "Inference geo: $(jq -r '.model.inference_geo' <<< "$agent")"

yaml
      name: Geo-pinned assistant
      model:
        id: claude-opus-5
        inference_geo: us
      system: You are a helpful assistant.

python Python
  agent = client.beta.agents.create(
      name="Geo-pinned assistant",
      model={
          "id": "claude-opus-5",
          "inference_geo": "us",
      },
      system="You are a helpful assistant.",
  )

  print(f"Inference geo: {agent.model.inference_geo}")

typescript TypeScript
  const agent = await client.beta.agents.create({
    name: "Geo-pinned assistant",
    model: { id: "claude-opus-5", inference_geo: "us" },
    system: "You are a helpful assistant.",
  });

  console.log(`Inference geo: ${agent.model.inference_geo}`);

csharp C#
  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "Geo-pinned assistant",
      Model = new BetaManagedAgentsModelConfigParams
      {
          ID = BetaManagedAgentsModel.ClaudeOpus5,
          InferenceGeo = "us",
      },
      System = "You are a helpful assistant.",
  });

  Console.WriteLine($"Inference geo: {agent.Model.InferenceGeo}");

go Go
  agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name: "Geo-pinned assistant",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID:           anthropic.BetaManagedAgentsModelClaudeOpus5,
  		InferenceGeo: anthropic.String("us"),
  	},
  	System: anthropic.String("You are a helpful assistant."),
  })
  if err != nil {
  	panic(err)
  }

  fmt.Printf("Inference geo: %s\n", agent.Model.InferenceGeo)

java Java
  var agent = client.beta().agents().create(
      AgentCreateParams.builder()
          .name("Geo-pinned assistant")
          .model(
              BetaManagedAgentsModelConfigParams.builder()
                  .id(BetaManagedAgentsModel.CLAUDE_OPUS_5)
                  .inferenceGeo("us")
                  .build()
          )
          .system("You are a helpful assistant.")
          .build()
  );

  IO.println("Inference geo: " + agent.model().inferenceGeo().orElseThrow());

php PHP
  $agent = $client->beta->agents->create(
      name: 'Geo-pinned assistant',
      model: BetaManagedAgentsModelConfigParams::with(
          id: 'claude-opus-5',
          inferenceGeo: 'us',
      ),
      system: 'You are a helpful assistant.',
  );

  echo "Inference geo: {$agent->model->inferenceGeo}\n";

ruby Ruby
  agent = client.beta.agents.create(
    name: "Geo-pinned assistant",
    model: {id: "claude-opus-5", inference_geo: "us"},
    system_: "You are a helpful assistant."
  )

  puts "Inference geo: #{agent.model.inference_geo}"
  ```
</CodeGroup>

An `inference_geo` pin is validated against the workspace's [`allowed_inference_geos`](https://platform.claude.com/docs/en/manage-claude/data-residency#workspace-level-restrictions) when the agent is saved, when a session is created from it, and on every turn the session serves. If the workspace allowlist narrows so a pin is no longer allowed, new sessions can't be created from the agent and running sessions refuse further turns; pins are never exempted, because workspaces rely on them for compliance and data residency.

Setting `inference_geo` on a model that doesn't support geographic inference pinning returns a 400 error; see [Model availability](https://platform.claude.com/docs/en/manage-claude/data-residency#model-availability) for the models that do. In a `multiagent` configuration, the coordinator's pin and every roster member's must all be set to the same value or all be unset; see [Multiagent orchestration](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration). To change or clear the pin later, update the agent's `model` object; supplying `model` without `inference_geo` clears it, as described under [Update semantics](https://platform.claude.com/docs/en/managed-agents/agent-setup#update-semantics).


## Update an agent

Source: https://platform.claude.com/llms-full.txt#update-an-agent

Updating an agent generates a new version when the configuration changes. The `version` field is optional: supply it for optimistic concurrency (a mismatch returns a 409), or omit it to apply the update unconditionally (last write wins). Updates to archived agents are rejected.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  updated_agent=$(curl -fsSL "https://api.anthropic.com/v1/agents/$AGENT_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "version": $AGENT_VERSION,
    "system": "You are a helpful coding agent. Always write tests."
  }
  EOF
  )

  echo "New version: $(jq -r '.version' <<< "$updated_agent")"

bash CLI
    ant beta:agents update --agent-id "$AGENT_ID" < coding-assistant.agent.yaml

yaml
      name: Coding Assistant
      model:
        id: claude-opus-5
      system: You are a helpful coding agent. Always write tests.
      tools:
        - type: agent_toolset_20260401

python Python
  updated_agent = client.beta.agents.update(
      agent.id,
      version=agent.version,
      system="You are a helpful coding agent. Always write tests.",
  )

  print(f"New version: {updated_agent.version}")

typescript TypeScript
  const updatedAgent = await client.beta.agents.update(agent.id, {
    version: agent.version,
    system: "You are a helpful coding agent. Always write tests.",
  });

  console.log(`New version: ${updatedAgent.version}`);

csharp C#
  var updatedAgent = await client.Beta.Agents.Update(agent.ID, new()
  {
      Version = agent.Version,
      System = "You are a helpful coding agent. Always write tests.",
  });

  Console.WriteLine($"New version: {updatedAgent.Version}");

go Go
  updatedAgent, err := client.Beta.Agents.Update(ctx, agent.ID, anthropic.BetaAgentUpdateParams{
  	Version: anthropic.Int(agent.Version),
  	System:  anthropic.String("You are a helpful coding agent. Always write tests."),
  })
  if err != nil {
  	panic(err)
  }

  fmt.Printf("New version: %d\n", updatedAgent.Version)

java Java
  var updatedAgent = client.beta().agents().update(
      agent.id(),
      AgentUpdateParams.builder()
          .version(agent.version())
          .system("You are a helpful coding agent. Always write tests.")
          .build()
  );

  IO.println("New version: " + updatedAgent.version());

php PHP
  $updatedAgent = $client->beta->agents->update(
      $agent->id,
      version: $agent->version,
      system: 'You are a helpful coding agent. Always write tests.',
  );

  echo "New version: {$updatedAgent->version}\n";

ruby Ruby
  updated_agent = client.beta.agents.update(
    agent.id,
    version: agent.version,
    system_: "You are a helpful coding agent. Always write tests."
  )

  puts "New version: #{updated_agent.version}"

bash cURL
  updated_agent=$(curl -fsSL "https://api.anthropic.com/v1/agents/$AGENT_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d '{
      "description": "Writes and reviews code."
    }')

  echo "New version: $(jq -r '.version' <<< "$updated_agent")"
  ```
</CodeGroup>

### Update semantics

* **`version`** is optional and must be at least 1 when supplied. When supplied, the request returns a 409 if it doesn't match the agent's current version, even when the fields you send already match the stored values; re-read the agent and retry. When omitted, the update applies unconditionally and the most recent update silently replaces any concurrent one, with no error to either caller. Supplying `version` is the recommended default for interactive callers, and omitting it fits declarative apply loops, such as a CI job that syncs checked-in agent definitions, where the loop owns the agent.

* **Omitted fields are preserved.** You only need to include the fields you want to change.

* **Scalar fields** (`model`, `system`, `name`, `description`) are replaced with the new value. `system` and `description` can be cleared by passing `null`. `model` and `name` are mandatory and cannot be cleared. Within a `model` object you supply, `effort` is the sole exception: if the model `id` is unchanged, omitting `effort` leaves the stored effort level unchanged. If you change the model `id`, an omitted `effort` resets to the new model's default. Other `model` fields are replaced along with the object: supplying `model` without `inference_geo` clears the agent's inference geo pin.

* **Array fields** (`tools`, `mcp_servers`, `skills`) are fully replaced by the new array. To clear an array field entirely, pass `null` or an empty array.

* **`multiagent`** is replaced as a whole, including its `agents` roster. Pass `null` to clear it.

* **Metadata** is merged at the key level. Keys you provide are added or updated. Keys you omit are preserved. To delete a specific key, set its value to `null`.

* **No-op detection.** If the update produces no change relative to the current version, no new version is created and the existing version is returned.

* **Coordinator rosters are not updated.** Coordinators that reference this agent in their `multiagent.agents` roster keep the version that was pinned when the coordinator was created or last updated, even if the reference omits `version`. To delegate to the new version, [update the coordinator](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration#configure-the-coordinator) so its roster references it.


## Agent lifecycle

Source: https://platform.claude.com/llms-full.txt#agent-lifecycle

| Operation         | Behavior                                                                                            |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| **Update**        | Generates a new agent version when the configuration changes.                                       |
| **List versions** | Returns the full version history so you can track changes over time.                                |
| **Archive**       | Makes the agent read-only. New sessions cannot reference it, but existing sessions continue to run. |

### List versions

Fetch the full version history to track how an agent has changed over time. Results are paginated, and the SDK examples fetch every page automatically.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl -fsSL "https://api.anthropic.com/v1/agents/$AGENT_ID/versions" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    | jq -r '.data[] | "Version \(.version): \(.updated_at)"'

bash CLI
  ant beta:agents:versions list --agent-id "$AGENT_ID"

python Python
  for version in client.beta.agents.versions.list(agent.id):
      print(f"Version {version.version}: {version.updated_at.isoformat()}")

typescript TypeScript
  for await (const version of client.beta.agents.versions.list(agent.id)) {
    console.log(`Version ${version.version}: ${version.updated_at}`);
  }

csharp C#
  var versions = await client.Beta.Agents.Versions.List(agent.ID);
  await foreach (var version in versions.Paginate())
  {
      Console.WriteLine($"Version {version.Version}: {version.UpdatedAt:O}");
  }

go Go
  iter := client.Beta.Agents.Versions.ListAutoPaging(ctx, agent.ID, anthropic.BetaAgentVersionListParams{})
  for iter.Next() {
  	version := iter.Current()
  	fmt.Printf("Version %d: %s\n", version.Version, version.UpdatedAt.Format(time.RFC3339))
  }
  if err := iter.Err(); err != nil {
  	panic(err)
  }

java Java
  for (var version : client.beta().agents().versions().list(agent.id()).autoPager()) {
      IO.println("Version " + version.version() + ": " + version.updatedAt());
  }

php PHP
  foreach ($client->beta->agents->versions->list($agent->id)->pagingEachItem() as $version) {
      echo "Version {$version->version}: {$version->updatedAt->format(DateTimeInterface::ATOM)}\n";
  }

ruby Ruby
  client.beta.agents.versions.list(agent.id).auto_paging_each do |agent_version|
    puts "Version #{agent_version.version}: #{agent_version.updated_at.iso8601}"
  end

bash cURL
  archived=$(curl -fsSL -X POST "https://api.anthropic.com/v1/agents/$AGENT_ID/archive" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01")

  echo "Archived at: $(jq -r '.archived_at' <<< "$archived")"

bash CLI
  ant beta:agents archive --agent-id "$AGENT_ID"

python Python
  archived = client.beta.agents.archive(agent.id)

  print(f"Archived at: {archived.archived_at.isoformat()}")

typescript TypeScript
  const archived = await client.beta.agents.archive(agent.id);
  console.log(`Archived at: ${archived.archived_at}`);

csharp C#
  var archived = await client.Beta.Agents.Archive(agent.ID);
  Console.WriteLine($"Archived at: {archived.ArchivedAt:O}");

go Go
  archived, err := client.Beta.Agents.Archive(ctx, agent.ID, anthropic.BetaAgentArchiveParams{})
  if err != nil {
  	panic(err)
  }
  fmt.Printf("Archived at: %s\n", archived.ArchivedAt.Format(time.RFC3339))

java Java
  var archived = client.beta().agents().archive(agent.id());
  IO.println("Archived at: " + archived.archivedAt().orElseThrow());

php PHP
  $archived = $client->beta->agents->archive($agent->id);

  echo "Archived at: {$archived->archivedAt->format(DateTimeInterface::ATOM)}\n";

ruby Ruby
  archived = client.beta.agents.archive(agent.id)
  puts "Archived at: #{archived.archived_at.iso8601}"
  ```
</CodeGroup>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-69

<CardGroup cols={2}>
  <Card title="Tools" icon="tool" href="https://platform.claude.com/docs/en/managed-agents/tools">
    Configure tools available to your agent.
  </Card>

  <Card title="Skills" icon="graduation-cap" href="https://platform.claude.com/docs/en/managed-agents/skills">
    Attach reusable, filesystem-based expertise to your agent for domain-specific workflows.
  </Card>

  <Card title="Start a session" icon="play" href="https://platform.claude.com/docs/en/managed-agents/sessions">
    Create a session to run your agent and begin executing tasks.
  </Card>

  <Card title="Reference" icon="book" href="https://platform.claude.com/docs/en/managed-agents/reference">
    Event types, self-hosted worker CLI flags, supported MCP server types, rate limits, and branding guidelines for Claude Managed Agents.
  </Card>
</CardGroup>


---
title: MCP connector
url: https://platform.claude.com/docs/en/managed-agents/mcp-connector
description: Connect MCP servers to your agents for access to external tools and data sources.
---

Claude Managed Agents supports connecting [Model Context Protocol (MCP)](https://modelcontextprotocol.io) servers to your agents. This gives the agent access to external tools, data sources, and services through a standardized protocol.

MCP configuration is split across two steps:

1. **Agent creation** declares which MCP servers the agent connects to, by name and URL.
2. **Session creation** supplies authentication for those servers by referencing a pre-registered vault (see [Authenticate with vaults](https://platform.claude.com/docs/en/managed-agents/vaults)).

This separation keeps secrets out of reusable agent definitions while letting each session authenticate with its own credentials.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Declare MCP servers on the agent

Source: https://platform.claude.com/llms-full.txt#declare-mcp-servers-on-the-agent

Specify MCP servers in the `mcp_servers` array when creating an agent. Each server needs a `type`, a unique `name`, and a `url`. No authentication tokens are provided at this stage.

Each declared server also needs a matching `mcp_toolset` entry in the `tools` array. The toolset's `mcp_server_name` must match the server's `name`.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  agent_response=$(curl -sS --fail-with-body https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<'EOF'
  {
    "name": "GitHub Assistant",
    "model": "claude-opus-5",
    "mcp_servers": [
      {
        "type": "url",
        "name": "github",
        "url": "https://api.githubcopilot.com/mcp/"
      }
    ],
    "tools": [
      {"type": "agent_toolset_20260401"},
      {"type": "mcp_toolset", "mcp_server_name": "github"}
    ]
  }
  EOF
  )
  agent_id=$(jq -r '.id' <<<"$agent_response")

bash CLI
    AGENT_ID=$(ant beta:agents create --transform id --raw-output < github-assistant.agent.yaml)

yaml
      name: GitHub Assistant
      model:
        id: claude-opus-5
      mcp_servers:
        - type: url
          name: github
          url: https://api.githubcopilot.com/mcp/
      tools:
        - type: agent_toolset_20260401
        - type: mcp_toolset
          mcp_server_name: github

python Python
  agent = client.beta.agents.create(
      name="GitHub Assistant",
      model="claude-opus-5",
      mcp_servers=[
          {
              "type": "url",
              "name": "github",
              "url": "https://api.githubcopilot.com/mcp/",
          },
      ],
      tools=[
          {"type": "agent_toolset_20260401"},
          {"type": "mcp_toolset", "mcp_server_name": "github"},
      ],
  )

typescript TypeScript
  const agent = await client.beta.agents.create({
    name: "GitHub Assistant",
    model: "claude-opus-5",
    mcp_servers: [
      {
        type: "url",
        name: "github",
        url: "https://api.githubcopilot.com/mcp/",
      },
    ],
    tools: [
      { type: "agent_toolset_20260401" },
      { type: "mcp_toolset", mcp_server_name: "github" },
    ],
  });

csharp C#
  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "GitHub Assistant",
      Model = BetaManagedAgentsModel.ClaudeOpus5,
      McpServers =
      [
          new() { Type = "url", Name = "github", Url = "https://api.githubcopilot.com/mcp/" },
      ],
      Tools =
      [
          new BetaManagedAgentsAgentToolset20260401Params
          {
              Type = "agent_toolset_20260401",
          },
          new BetaManagedAgentsMcpToolsetParams { Type = "mcp_toolset", McpServerName = "github" },
      ],
  });

go Go
  agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name: "GitHub Assistant",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID: anthropic.BetaManagedAgentsModelClaudeOpus5,
  	},
  	MCPServers: []anthropic.BetaManagedAgentsURLMCPServerParams{{
  		Type: anthropic.BetaManagedAgentsURLMCPServerParamsTypeURL,
  		Name: "github",
  		URL:  "https://api.githubcopilot.com/mcp/",
  	}},
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{
  		{
  			OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  				Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  			},
  		},
  		{
  			OfMCPToolset: &anthropic.BetaManagedAgentsMCPToolsetParams{
  				Type:          anthropic.BetaManagedAgentsMCPToolsetParamsTypeMCPToolset,
  				MCPServerName: "github",
  			},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  var agent = client.beta().agents().create(
      AgentCreateParams.builder()
          .name("GitHub Assistant")
          .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
          .addMcpServer(
              BetaManagedAgentsUrlMcpServerParams.builder()
                  .type(BetaManagedAgentsUrlMcpServerParams.Type.URL)
                  .name("github")
                  .url("https://api.githubcopilot.com/mcp/")
                  .build()
          )
          .addTool(
              BetaManagedAgentsAgentToolset20260401Params.builder()
                  .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
                  .build()
          )
          .addTool(
              BetaManagedAgentsMcpToolsetParams.builder()
                  .type(BetaManagedAgentsMcpToolsetParams.Type.MCP_TOOLSET)
                  .mcpServerName("github")
                  .build()
          )
          .build()
  );

php PHP
  $agent = $client->beta->agents->create(
      name: 'GitHub Assistant',
      model: 'claude-opus-5',
      mcpServers: [
          BetaManagedAgentsURLMCPServerParams::with(
              type: 'url',
              name: 'github',
              url: 'https://api.githubcopilot.com/mcp/',
          ),
      ],
      tools: [
          BetaManagedAgentsAgentToolset20260401Params::with(
              type: 'agent_toolset_20260401',
          ),
          BetaManagedAgentsMCPToolsetParams::with(
              type: 'mcp_toolset',
              mcpServerName: 'github',
          ),
      ],
  );

ruby Ruby
  agent = client.beta.agents.create(
    name: "GitHub Assistant",
    model: "claude-opus-5",
    mcp_servers: [
      {
        type: "url",
        name: "github",
        url: "https://api.githubcopilot.com/mcp/"
      }
    ],
    tools: [
      {type: "agent_toolset_20260401"},
      {type: "mcp_toolset", mcp_server_name: "github"}
    ]
  )
  ```
</CodeGroup>

<Tip>
  The MCP toolset defaults to a permission policy of `always_ask`, which requires user approval before each tool call. See [permission policies](https://platform.claude.com/docs/en/managed-agents/permission-policies) to configure this behavior.
</Tip>

### `mcp_servers` field reference

Each entry in the `mcp_servers` array defines one connection.

| Field  | Description                                                                                                                                                                                                                                                             |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type` | Required. Must be `"url"`.                                                                                                                                                                                                                                              |
| `name` | Required. A unique name for this server within the agent (1–255 characters). Used as the `mcp_server_name` in the `tools` array and surfaced on MCP tool events in the [session event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming). |
| `url`  | Required. The endpoint of the remote MCP server (up to 2,048 characters). See [Supported MCP server types](https://platform.claude.com/docs/en/managed-agents/reference#supported-mcp-server-types) for transport requirements.                                         |

Constraints:

* An agent can declare up to 20 MCP servers. Server names must be unique within the array.
* Every `mcp_servers` entry must be referenced by an `mcp_toolset` in the `tools` array, and every `mcp_toolset` must reference a declared server. The API rejects agent definitions with unreferenced servers or dangling toolsets.


## Configure which MCP tools are available

Source: https://platform.claude.com/llms-full.txt#configure-which-mcp-tools-are-available

The `mcp_toolset` entry supports a `default_config` object and a `configs` array, applied to the tools the MCP server exposes. Each `configs` entry accepts only `name`, `enabled`, and `permission_policy`. Unlike entries in the built-in agent toolset, MCP tool entries do not take a `type` field, and the [web settings](https://platform.claude.com/docs/en/managed-agents/tools#restrict-web-search-and-web-fetch-domains) available on `web_search` and `web_fetch` do not apply to MCP tools. The `name` in each `configs` entry is the bare tool name as reported by the server.

By default all tools exposed by the MCP server are enabled. To enable only specific tools, set `default_config.enabled` to `false` and explicitly enable the tools you want:

This pattern is useful when a server exposes many tools but the agent only needs a few, or when you want tools added by the server operator to stay off until you review them.

To disable specific tools while keeping the rest enabled, omit `default_config` and set `enabled: false` on individual entries:

See [configuring the toolset](https://platform.claude.com/docs/en/managed-agents/tools#configuring-the-toolset) for the general `default_config` / `configs` pattern, and [MCP toolset permissions](https://platform.claude.com/docs/en/managed-agents/permission-policies#mcp-toolset-permissions) for setting `permission_policy` on MCP tools and handling confirmation requests.

### MCP tool output handling

When an MCP tool output exceeds 100,000 characters (about 25,000 tokens), it is automatically written to a file in the sandbox. The model receives a truncated preview with the file path and can read the full content from there.


## Provide authentication at session creation

Source: https://platform.claude.com/llms-full.txt#provide-authentication-at-session-creation

When starting a session, pass `vault_ids` to provide credentials for your MCP servers. Vaults are collections of credentials that you register once and reference by ID. See [Authenticate with vaults](https://platform.claude.com/docs/en/managed-agents/vaults) for how to create vaults and manage credentials.

<CodeGroup>
  ```bash cURL
  session_response=$(curl -sS --fail-with-body https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "agent": "$agent_id",
    "environment_id": "$environment_id",
    "vault_ids": ["$vault_id"]
  }
  EOF
  )
  session_id=$(jq -r '.id' <<<"$session_response")

bash CLI
  SESSION_ID=$(ant beta:sessions create \
    --agent "$AGENT_ID" \
    --environment-id "$ENVIRONMENT_ID" \
    --vault-id "$VAULT_ID" \
    --transform id --raw-output)

python Python
  session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
      vault_ids=[vault.id],
  )

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id,
    vault_ids: [vault.id],
  });

csharp C#
  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = agent.ID,
      EnvironmentID = environment.ID,
      VaultIds = [vault.ID],
  });

go Go
  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent:         anthropic.BetaSessionNewParamsAgentUnion{OfString: anthropic.String(agent.ID)},
  	EnvironmentID: environment.ID,
  	VaultIDs:      []string{vault.ID},
  })
  if err != nil {
  	panic(err)
  }

java Java
  var session = client.beta().sessions().create(
      SessionCreateParams.builder()
          .agent(agent.id())
          .environmentId(environment.id())
          .addVaultId(vault.id())
          .build()
  );

php PHP
  $session = $client->beta->sessions->create(
      agent: $agent->id,
      environmentID: $environment->id,
      vaultIDs: [$vault->id],
  );

ruby Ruby
  session = client.beta.sessions.create(
    agent: agent.id,
    environment_id: environment.id,
    vault_ids: [vault.id]
  )
  ```
</CodeGroup>

Credentials are matched by URL, so the vault must contain a credential whose `mcp_server_url` refers to the same server as the `url` declared in `mcp_servers`. Both URLs are normalized before matching (scheme and host lowercased, default ports and trailing slashes stripped), so differences in host casing, a default port, or a trailing slash don't prevent a match; a different path, subdomain, or non-default port does. If none matches, the connection is attempted unauthenticated. See [Add a credential](https://platform.claude.com/docs/en/managed-agents/vaults#add-a-credential) for the `static_bearer` and `mcp_oauth` credential types.

### Handle connection and authentication failures

Session creation does not validate MCP connectivity or credentials. If an MCP server is unreachable or rejects the supplied credential, the session still starts and interaction remains possible. A [`session.error`](https://platform.claude.com/docs/en/managed-agents/events-and-streaming) event is emitted with the `mcp_server_name` of the affected server and a `retry_status`:

| Error type                        | Meaning                                                                                                                                                                                                      |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `mcp_connection_failed_error`     | The MCP server could not be reached (network error, timeout, or non-authentication HTTP failure).                                                                                                            |
| `mcp_authentication_failed_error` | Authentication with the MCP server failed: the server rejected the credential from the attached vault, required authentication when no matching credential was configured, or an OAuth token refresh failed. |

You can decide whether to block further interaction on this error, trigger a credential rotation, or let the session continue without the affected server's tools. The connection is retried on the next `session.status_idle` to `session.status_running` transition.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-70

<CardGroup cols={2}>
  <Card title="Permission policies" icon="check" href="https://platform.claude.com/docs/en/managed-agents/permission-policies">
    Control when agent and MCP tools run.
  </Card>

  <Card title="Session event stream" icon="lightning" href="https://platform.claude.com/docs/en/managed-agents/events-and-streaming">
    Send events, stream responses, and interrupt or redirect your session mid-execution.
  </Card>

  <Card title="Supported MCP server types" icon="book" href="https://platform.claude.com/docs/en/managed-agents/reference#supported-mcp-server-types">
    Transport requirements for remote MCP servers.
  </Card>
</CardGroup>


---
title: Permission policies
url: https://platform.claude.com/docs/en/managed-agents/permission-policies
description: Control when agent and MCP tools execute.
---

Permission policies control whether server-executed tools (the pre-built agent toolset and MCP toolset) run automatically or wait for your approval. Custom tools are executed by your application and controlled by you, so they are not governed by permission policies.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Permission policy types

Source: https://platform.claude.com/llms-full.txt#permission-policy-types

| Policy         | Behavior                                                                                                                                                                                                                             |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `always_allow` | The tool executes automatically with no confirmation.                                                                                                                                                                                |
| `always_ask`   | The session pauses and waits for your approval before executing. See [Respond to confirmation requests](https://platform.claude.com/docs/en/managed-agents/permission-policies#respond-to-confirmation-requests) for the event flow. |

Each toolset kind has its own default: the agent toolset defaults to `always_allow`, and MCP toolsets default to `always_ask`.

A permission policy controls when an enabled tool runs. To remove a tool from the agent entirely, disable it instead. See [Disabling specific tools](https://platform.claude.com/docs/en/managed-agents/tools#disabling-specific-tools).


## Set a policy for a toolset

Source: https://platform.claude.com/llms-full.txt#set-a-policy-for-a-toolset

You set permission policies in the agent's `tools` configuration when you create the agent, and you can change them later by [updating the agent](https://platform.claude.com/docs/en/managed-agents/agent-setup#update-an-agent). Running sessions keep the toolset configuration they were created with. Updates apply to sessions created afterward.

### Agent toolset permissions

When creating an agent, you can apply a policy to every tool in `agent_toolset_20260401` using `default_config.permission_policy`:

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  agent=$(curl -fsSL https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d '{
      "name": "Coding Assistant",
      "model": "claude-opus-5",
      "tools": [
        {
          "type": "agent_toolset_20260401",
          "default_config": {
            "permission_policy": {"type": "always_ask"}
          }
        }
      ]
    }')

bash CLI
    ant beta:agents create < agent.yaml

yaml
      name: Coding Assistant
      model: claude-opus-5
      tools:
        - type: agent_toolset_20260401
          default_config:
            permission_policy:
              type: always_ask

python Python
  agent = client.beta.agents.create(
      name="Coding Assistant",
      model="claude-opus-5",
      tools=[
          {
              "type": "agent_toolset_20260401",
              "default_config": {
                  "permission_policy": {"type": "always_ask"},
              },
          },
      ],
  )

typescript TypeScript
  const agent = await client.beta.agents.create({
    name: "Coding Assistant",
    model: "claude-opus-5",
    tools: [
      {
        type: "agent_toolset_20260401",
        default_config: {
          permission_policy: { type: "always_ask" }
        }
      }
    ]
  });

csharp C#
  using Anthropic.Models.Beta.Agents;

  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "Coding Assistant",
      Model = BetaManagedAgentsModel.ClaudeOpus5,
      Tools =
      [
          new BetaManagedAgentsAgentToolset20260401Params
          {
              Type = BetaManagedAgentsAgentToolset20260401ParamsType.AgentToolset20260401,
              DefaultConfig = new()
              {
                  PermissionPolicy = new BetaManagedAgentsAlwaysAskPolicy { Type = "always_ask" },
              },
          },
      ],
  });

go Go
  agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name: "Coding Assistant",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID: "claude-opus-5",
  	},
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{{
  		OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  			Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  			DefaultConfig: anthropic.BetaManagedAgentsAgentToolsetDefaultConfigParams{
  				PermissionPolicy: anthropic.BetaManagedAgentsAgentToolsetDefaultConfigParamsPermissionPolicyUnion{
  					OfAlwaysAsk: &anthropic.BetaManagedAgentsAlwaysAskPolicyParam{
  						Type: anthropic.BetaManagedAgentsAlwaysAskPolicyTypeAlwaysAsk,
  					},
  				},
  			},
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }
  _ = agent

java Java
  import com.anthropic.models.beta.agents.*;

  var agent = client.beta().agents().create(
      AgentCreateParams.builder()
          .name("Coding Assistant")
          .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
          .addTool(
              BetaManagedAgentsAgentToolset20260401Params.builder()
                  .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
                  .defaultConfig(
                      BetaManagedAgentsAgentToolsetDefaultConfigParams.builder()
                          .permissionPolicy(
                              BetaManagedAgentsAlwaysAskPolicy.builder()
                                  .type(BetaManagedAgentsAlwaysAskPolicy.Type.ALWAYS_ASK)
                                  .build()
                          )
                          .build()
                  )
                  .build()
          )
          .build()
  );

php PHP
  use Anthropic\Beta\Agents\BetaManagedAgentsAgentToolset20260401Params;
  use Anthropic\Beta\Agents\BetaManagedAgentsAgentToolsetDefaultConfigParams;
  use Anthropic\Beta\Agents\BetaManagedAgentsAlwaysAskPolicy;

  $agent = $client->beta->agents->create(
      name: 'Coding Assistant',
      model: 'claude-opus-5',
      tools: [
          BetaManagedAgentsAgentToolset20260401Params::with(
              type: 'agent_toolset_20260401',
              defaultConfig: BetaManagedAgentsAgentToolsetDefaultConfigParams::with(
                  permissionPolicy: BetaManagedAgentsAlwaysAskPolicy::with(type: 'always_ask'),
              ),
          ),
      ],
  );

ruby Ruby
  agent = client.beta.agents.create(
    name: "Coding Assistant",
    model: "claude-opus-5",
    tools: [
      {
        type: "agent_toolset_20260401",
        default_config: {
          permission_policy: {type: "always_ask"}
        }
      }
    ]
  )

bash cURL
  agent=$(curl -fsSL https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d '{
      "name": "Dev Assistant",
      "model": "claude-opus-5",
      "mcp_servers": [
        {"type": "url", "name": "github", "url": "https://mcp.example.com/github"}
      ],
      "tools": [
        {"type": "agent_toolset_20260401"},
        {
          "type": "mcp_toolset",
          "mcp_server_name": "github",
          "default_config": {
            "permission_policy": {"type": "always_allow"}
          }
        }
      ]
    }')

bash CLI
    ant beta:agents create < agent.yaml

yaml
      name: Dev Assistant
      model: claude-opus-5
      mcp_servers:
        - type: url
          name: github
          url: https://mcp.example.com/github
      tools:
        - type: agent_toolset_20260401
        - type: mcp_toolset
          mcp_server_name: github
          default_config:
            permission_policy:
              type: always_allow

python Python
  agent = client.beta.agents.create(
      name="Dev Assistant",
      model="claude-opus-5",
      mcp_servers=[
          {"type": "url", "name": "github", "url": "https://mcp.example.com/github"},
      ],
      tools=[
          {"type": "agent_toolset_20260401"},
          {
              "type": "mcp_toolset",
              "mcp_server_name": "github",
              "default_config": {
                  "permission_policy": {"type": "always_allow"},
              },
          },
      ],
  )

typescript TypeScript
  const agent = await client.beta.agents.create({
    name: "Dev Assistant",
    model: "claude-opus-5",
    mcp_servers: [{ type: "url", name: "github", url: "https://mcp.example.com/github" }],
    tools: [
      { type: "agent_toolset_20260401" },
      {
        type: "mcp_toolset",
        mcp_server_name: "github",
        default_config: {
          permission_policy: { type: "always_allow" }
        }
      }
    ]
  });

csharp C#
  using Anthropic.Models.Beta.Agents;

  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "Dev Assistant",
      Model = BetaManagedAgentsModel.ClaudeOpus5,
      McpServers =
      [
          new()
          {
              Type = BetaManagedAgentsUrlMcpServerParamsType.Url,
              Name = "github",
              Url = "https://mcp.example.com/github",
          },
      ],
      Tools =
      [
          new BetaManagedAgentsAgentToolset20260401Params
          {
              Type = BetaManagedAgentsAgentToolset20260401ParamsType.AgentToolset20260401,
          },
          new BetaManagedAgentsMcpToolsetParams
          {
              Type = BetaManagedAgentsMcpToolsetParamsType.McpToolset,
              McpServerName = "github",
              DefaultConfig = new()
              {
                  PermissionPolicy = new BetaManagedAgentsAlwaysAllowPolicy { Type = "always_allow" },
              },
          },
      ],
  });

go Go
  agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name: "Dev Assistant",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID: "claude-opus-5",
  	},
  	MCPServers: []anthropic.BetaManagedAgentsURLMCPServerParams{{
  		Type: anthropic.BetaManagedAgentsURLMCPServerParamsTypeURL,
  		Name: "github",
  		URL:  "https://mcp.example.com/github",
  	}},
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{
  		{
  			OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  				Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  			},
  		},
  		{
  			OfMCPToolset: &anthropic.BetaManagedAgentsMCPToolsetParams{
  				Type:          anthropic.BetaManagedAgentsMCPToolsetParamsTypeMCPToolset,
  				MCPServerName: "github",
  				DefaultConfig: anthropic.BetaManagedAgentsMCPToolsetDefaultConfigParams{
  					PermissionPolicy: anthropic.BetaManagedAgentsMCPToolsetDefaultConfigParamsPermissionPolicyUnion{
  						OfAlwaysAllow: &anthropic.BetaManagedAgentsAlwaysAllowPolicyParam{
  							Type: anthropic.BetaManagedAgentsAlwaysAllowPolicyTypeAlwaysAllow,
  						},
  					},
  				},
  			},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }
  _ = agent

java Java
  import com.anthropic.models.beta.agents.*;

  var agent = client.beta().agents().create(
      AgentCreateParams.builder()
          .name("Dev Assistant")
          .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
          .addMcpServer(
              BetaManagedAgentsUrlMcpServerParams.builder()
                  .type(BetaManagedAgentsUrlMcpServerParams.Type.URL)
                  .name("github")
                  .url("https://mcp.example.com/github")
                  .build()
          )
          .addTool(
              BetaManagedAgentsAgentToolset20260401Params.builder()
                  .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
                  .build()
          )
          .addTool(
              BetaManagedAgentsMcpToolsetParams.builder()
                  .type(BetaManagedAgentsMcpToolsetParams.Type.MCP_TOOLSET)
                  .mcpServerName("github")
                  .defaultConfig(
                      BetaManagedAgentsMcpToolsetDefaultConfigParams.builder()
                          .permissionPolicy(
                              BetaManagedAgentsAlwaysAllowPolicy.builder()
                                  .type(BetaManagedAgentsAlwaysAllowPolicy.Type.ALWAYS_ALLOW)
                                  .build()
                          )
                          .build()
                  )
                  .build()
          )
          .build()
  );

php PHP
  use Anthropic\Beta\Agents\BetaManagedAgentsAgentToolset20260401Params;
  use Anthropic\Beta\Agents\BetaManagedAgentsAlwaysAllowPolicy;
  use Anthropic\Beta\Agents\BetaManagedAgentsMCPToolsetDefaultConfigParams;
  use Anthropic\Beta\Agents\BetaManagedAgentsMCPToolsetParams;
  use Anthropic\Beta\Agents\BetaManagedAgentsURLMCPServerParams;

  $agent = $client->beta->agents->create(
      name: 'Dev Assistant',
      model: 'claude-opus-5',
      mcpServers: [
          BetaManagedAgentsURLMCPServerParams::with(
              type: 'url',
              name: 'github',
              url: 'https://mcp.example.com/github',
          ),
      ],
      tools: [
          BetaManagedAgentsAgentToolset20260401Params::with(
              type: 'agent_toolset_20260401',
          ),
          BetaManagedAgentsMCPToolsetParams::with(
              type: 'mcp_toolset',
              mcpServerName: 'github',
              defaultConfig: BetaManagedAgentsMCPToolsetDefaultConfigParams::with(
                  permissionPolicy: BetaManagedAgentsAlwaysAllowPolicy::with(type: 'always_allow'),
              ),
          ),
      ],
  );

ruby Ruby
  agent = client.beta.agents.create(
    name: "Dev Assistant",
    model: "claude-opus-5",
    mcp_servers: [
      {type: "url", name: "github", url: "https://mcp.example.com/github"}
    ],
    tools: [
      {type: "agent_toolset_20260401"},
      {
        type: "mcp_toolset",
        mcp_server_name: "github",
        default_config: {
          permission_policy: {type: "always_allow"}
        }
      }
    ]
  )
  ```
</CodeGroup>


## Override an individual tool policy

Source: https://platform.claude.com/llms-full.txt#override-an-individual-tool-policy

Use the `configs` array to override the default for individual tools. The `name` values for the agent toolset are listed in [Available tools](https://platform.claude.com/docs/en/managed-agents/tools#available-tools). This example allows the full agent toolset by default but requires confirmation before any bash command runs:

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  tools='[
    {
      "type": "agent_toolset_20260401",
      "default_config": {
        "permission_policy": {"type": "always_allow"}
      },
      "configs": [
        {
          "name": "bash",
          "permission_policy": {"type": "always_ask"}
        }
      ]
    }
  ]'

bash CLI
  ant beta:agents create <<'YAML'
  name: Coding Assistant
  model: claude-opus-5
  tools:
    - type: agent_toolset_20260401
      default_config:
        permission_policy:
          type: always_allow
      configs:
        - name: bash
          permission_policy:
            type: always_ask
  YAML

python Python
  tools = [
      {
          "type": "agent_toolset_20260401",
          "default_config": {
              "permission_policy": {"type": "always_allow"},
          },
          "configs": [
              {
                  "name": "bash",
                  "permission_policy": {"type": "always_ask"},
              },
          ],
      },
  ]

typescript TypeScript
  const tools = [
    {
      type: "agent_toolset_20260401",
      default_config: {
        permission_policy: { type: "always_allow" }
      },
      configs: [
        {
          name: "bash",
          permission_policy: { type: "always_ask" }
        }
      ]
    }
  ] satisfies Anthropic.Beta.AgentCreateParams["tools"];

csharp C#
  using Anthropic.Models.Beta.Agents;
  using Tool = Anthropic.Models.Beta.Agents.Tool;

  Tool[] tools =
  [
      new BetaManagedAgentsAgentToolset20260401Params
      {
          Type = BetaManagedAgentsAgentToolset20260401ParamsType.AgentToolset20260401,
          DefaultConfig = new()
          {
              PermissionPolicy = new BetaManagedAgentsAlwaysAllowPolicy { Type = "always_allow" },
          },
          Configs =
          [
              new BetaManagedAgentsBashToolConfigParams
              {
                  PermissionPolicy = new BetaManagedAgentsAlwaysAskPolicy { Type = "always_ask" },
              },
          ],
      },
  ];

go Go
  tools := []anthropic.BetaAgentNewParamsToolUnion{{
  	OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  		Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  		DefaultConfig: anthropic.BetaManagedAgentsAgentToolsetDefaultConfigParams{
  			PermissionPolicy: anthropic.BetaManagedAgentsAgentToolsetDefaultConfigParamsPermissionPolicyUnion{
  				OfAlwaysAllow: &anthropic.BetaManagedAgentsAlwaysAllowPolicyParam{
  					Type: anthropic.BetaManagedAgentsAlwaysAllowPolicyTypeAlwaysAllow,
  				},
  			},
  		},
  		Configs: []anthropic.BetaManagedAgentsAgentToolConfigParamsUnion{{
  			OfBash: &anthropic.BetaManagedAgentsBashToolConfigParams{
  				PermissionPolicy: anthropic.BetaManagedAgentsBashToolConfigParamsPermissionPolicyUnion{
  					OfAlwaysAsk: &anthropic.BetaManagedAgentsAlwaysAskPolicyParam{
  						Type: anthropic.BetaManagedAgentsAlwaysAskPolicyTypeAlwaysAsk,
  					},
  				},
  			},
  		}},
  	},
  }}
  _ = tools

java Java
  import com.anthropic.models.beta.agents.*;
  import java.util.List;

  var tools = List.of(
      AgentCreateParams.Tool.ofAgentToolset20260401(
          BetaManagedAgentsAgentToolset20260401Params.builder()
              .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
              .defaultConfig(
                  BetaManagedAgentsAgentToolsetDefaultConfigParams.builder()
                      .permissionPolicy(
                          BetaManagedAgentsAlwaysAllowPolicy.builder()
                              .type(BetaManagedAgentsAlwaysAllowPolicy.Type.ALWAYS_ALLOW)
                              .build()
                      )
                      .build()
              )
              .addConfig(
                  BetaManagedAgentsBashToolConfigParams.builder()
                      .permissionPolicy(
                          BetaManagedAgentsAlwaysAskPolicy.builder()
                              .type(BetaManagedAgentsAlwaysAskPolicy.Type.ALWAYS_ASK)
                              .build()
                      )
                      .build()
              )
              .build()
      )
  );

php PHP
  use Anthropic\Beta\Agents\BetaManagedAgentsBashToolConfigParams;
  use Anthropic\Beta\Agents\BetaManagedAgentsAgentToolset20260401Params;
  use Anthropic\Beta\Agents\BetaManagedAgentsAgentToolsetDefaultConfigParams;
  use Anthropic\Beta\Agents\BetaManagedAgentsAlwaysAllowPolicy;
  use Anthropic\Beta\Agents\BetaManagedAgentsAlwaysAskPolicy;

  $tools = [
      BetaManagedAgentsAgentToolset20260401Params::with(
          type: 'agent_toolset_20260401',
          defaultConfig: BetaManagedAgentsAgentToolsetDefaultConfigParams::with(
              permissionPolicy: BetaManagedAgentsAlwaysAllowPolicy::with(type: 'always_allow'),
          ),
          configs: [
              BetaManagedAgentsBashToolConfigParams::with(
                  permissionPolicy: BetaManagedAgentsAlwaysAskPolicy::with(type: 'always_ask'),
              ),
          ],
      ),
  ];

ruby Ruby
  tools = [
    {
      type: "agent_toolset_20260401",
      default_config: {
        permission_policy: {type: "always_allow"}
      },
      configs: [
        {
          name: "bash",
          permission_policy: {type: "always_ask"}
        }
      ]
    }
  ]
  ```
</CodeGroup>

Pass this `tools` configuration in the agent create request (the CLI tab shows the complete command). MCP toolsets support the same per-tool overrides, with `name` set to the tool name reported by the MCP server. See [Configure which MCP tools are available](https://platform.claude.com/docs/en/managed-agents/mcp-connector#configure-which-mcp-tools-are-available).


## Respond to confirmation requests

Source: https://platform.claude.com/llms-full.txt#respond-to-confirmation-requests

When the agent invokes a tool with an `always_ask` policy:

1. The session emits an `agent.tool_use` or `agent.mcp_tool_use` event.
2. The session pauses with a `session.status_idle` event whose `stop_reason.type` is `requires_action`. The blocking event IDs are in the `stop_reason.event_ids` array. The session waits indefinitely for a response.
3. Send a `user.tool_confirmation` event for each blocking event, passing the event ID in the `tool_use_id` parameter. Set `result` to `"allow"` or `"deny"`. Use `deny_message` to explain a denial. You can send several confirmations in a single `events` request.
4. Once all blocking events are resolved, the session transitions back to `running`. Allowed tools execute. Denied tools do not run, and the agent receives a tool result saying the call was rejected, including your `deny_message`.

In the following examples, the tool-use event IDs come from the `stop_reason.event_ids` array of the `session.status_idle` event. Learn more about receiving events in the [Session event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#integrating-events) guide, or [subscribe to webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks) to be notified when a session pauses for input.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  # Allow the tool to execute
  curl -fsSL "https://api.anthropic.com/v1/sessions/$SESSION_ID/events" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d '{
      "events": [
        {
          "type": "user.tool_confirmation",
          "tool_use_id": "'$AGENT_TOOL_USE_EVENT_ID'",
          "result": "allow"
        }
      ]
    }'

  # Or deny it with an explanation
  curl -fsSL "https://api.anthropic.com/v1/sessions/$SESSION_ID/events" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d '{
      "events": [
        {
          "type": "user.tool_confirmation",
          "tool_use_id": "'$MCP_TOOL_USE_EVENT_ID'",
          "result": "deny",
          "deny_message": "Don'\''t create issues in the production project. Use the staging project."
        }
      ]
    }'

bash CLI
  # Allow the tool to execute
  ant beta:sessions:events send \
    --session-id "$SESSION_ID" \
    --event "{type: user.tool_confirmation, tool_use_id: $AGENT_TOOL_USE_EVENT_ID, result: allow}"

  # Or deny it with an explanation
  ant beta:sessions:events send \
    --session-id "$SESSION_ID" \
    --event "{type: user.tool_confirmation, tool_use_id: $MCP_TOOL_USE_EVENT_ID, result: deny,
      deny_message: Don't create issues in the production project. Use the staging project.}"

python Python
  # Allow the tool to execute
  client.beta.sessions.events.send(
      session.id,
      events=[
          {
              "type": "user.tool_confirmation",
              "tool_use_id": agent_tool_use_event.id,
              "result": "allow",
          },
      ],
  )

  # Or deny it with an explanation
  client.beta.sessions.events.send(
      session.id,
      events=[
          {
              "type": "user.tool_confirmation",
              "tool_use_id": mcp_tool_use_event.id,
              "result": "deny",
              "deny_message": "Don't create issues in the production project. Use the staging project.",
          },
      ],
  )

typescript TypeScript
  // Allow the tool to execute
  await client.beta.sessions.events.send(session.id, {
    events: [
      {
        type: "user.tool_confirmation",
        tool_use_id: agent_tool_use_event.id,
        result: "allow"
      }
    ]
  });

  // Or deny it with an explanation
  await client.beta.sessions.events.send(session.id, {
    events: [
      {
        type: "user.tool_confirmation",
        tool_use_id: mcp_tool_use_event.id,
        result: "deny",
        deny_message: "Don't create issues in the production project. Use the staging project."
      }
    ]
  });

csharp C#
  // Allow the tool to execute
  await client.Beta.Sessions.Events.Send(session.ID, new()
  {
      Events =
      [
          new BetaManagedAgentsUserToolConfirmationEventParams
          {
              Type = BetaManagedAgentsUserToolConfirmationEventParamsType.UserToolConfirmation,
              ToolUseID = agentToolUseEvent.ID,
              Result = "allow",
          },
      ],
  });

  // Or deny it with an explanation
  await client.Beta.Sessions.Events.Send(session.ID, new()
  {
      Events =
      [
          new BetaManagedAgentsUserToolConfirmationEventParams
          {
              Type = BetaManagedAgentsUserToolConfirmationEventParamsType.UserToolConfirmation,
              ToolUseID = mcpToolUseEvent.ID,
              Result = "deny",
              DenyMessage = "Don't create issues in the production project. Use the staging project.",
          },
      ],
  });

go Go
  // Allow the tool to execute
  _, err = client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  	Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  		OfUserToolConfirmation: &anthropic.BetaManagedAgentsUserToolConfirmationEventParams{
  			Type:      anthropic.BetaManagedAgentsUserToolConfirmationEventParamsTypeUserToolConfirmation,
  			ToolUseID: agentToolUseEvent.ID,
  			Result:    anthropic.BetaManagedAgentsUserToolConfirmationEventParamsResultAllow,
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }

  // Or deny it with an explanation
  _, err = client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  	Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  		OfUserToolConfirmation: &anthropic.BetaManagedAgentsUserToolConfirmationEventParams{
  			Type:        anthropic.BetaManagedAgentsUserToolConfirmationEventParamsTypeUserToolConfirmation,
  			ToolUseID:   mcpToolUseEvent.ID,
  			Result:      anthropic.BetaManagedAgentsUserToolConfirmationEventParamsResultDeny,
  			DenyMessage: anthropic.String("Don't create issues in the production project. Use the staging project."),
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }

java Java
  // Allow the tool to execute
  client.beta().sessions().events().send(
      session.id(),
      EventSendParams.builder()
          .addEvent(
              BetaManagedAgentsUserToolConfirmationEventParams.builder()
                  .type(BetaManagedAgentsUserToolConfirmationEventParams.Type.USER_TOOL_CONFIRMATION)
                  .toolUseId(agentToolUseEvent.id())
                  .result(BetaManagedAgentsUserToolConfirmationEventParams.Result.ALLOW)
                  .build()
          )
          .build()
  );

  // Or deny it with an explanation
  client.beta().sessions().events().send(
      session.id(),
      EventSendParams.builder()
          .addEvent(
              BetaManagedAgentsUserToolConfirmationEventParams.builder()
                  .type(BetaManagedAgentsUserToolConfirmationEventParams.Type.USER_TOOL_CONFIRMATION)
                  .toolUseId(mcpToolUseEvent.id())
                  .result(BetaManagedAgentsUserToolConfirmationEventParams.Result.DENY)
                  .denyMessage("Don't create issues in the production project. Use the staging project.")
                  .build()
          )
          .build()
  );

php PHP
  use Anthropic\Beta\Sessions\Events\ManagedAgentsUserToolConfirmationEventParams;

  // Allow the tool to execute
  $client->beta->sessions->events->send(
      $session->id,
      events: [
          ManagedAgentsUserToolConfirmationEventParams::with(
              type: 'user.tool_confirmation',
              toolUseID: $agentToolUseEvent->id,
              result: 'allow',
          ),
      ],
  );

  // Or deny it with an explanation
  $client->beta->sessions->events->send(
      $session->id,
      events: [
          ManagedAgentsUserToolConfirmationEventParams::with(
              type: 'user.tool_confirmation',
              toolUseID: $mcpToolUseEvent->id,
              result: 'deny',
              denyMessage: "Don't create issues in the production project. Use the staging project.",
          ),
      ],
  );

ruby Ruby
  # Allow the tool to execute
  client.beta.sessions.events.send_(
    session.id,
    events: [
      {
        type: "user.tool_confirmation",
        tool_use_id: agent_tool_use_event.id,
        result: "allow"
      }
    ]
  )

  # Or deny it with an explanation
  client.beta.sessions.events.send_(
    session.id,
    events: [
      {
        type: "user.tool_confirmation",
        tool_use_id: mcp_tool_use_event.id,
        result: "deny",
        deny_message: "Don't create issues in the production project. Use the staging project."
      }
    ]
  )
  ```
</CodeGroup>


## Custom tools

Source: https://platform.claude.com/llms-full.txt#custom-tools

Permission policies do not apply to custom tools. When the agent invokes a custom tool, your application receives an `agent.custom_tool_use` event and is responsible for deciding whether to execute it before sending back a `user.custom_tool_result`. See [Session event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#handling-custom-tool-calls) for the full flow.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-71

<CardGroup cols={2}>
  <Card title="Skills" icon="books" href="https://platform.claude.com/docs/en/managed-agents/skills">
    Attach reusable, filesystem-based expertise to your agent for domain-specific workflows.
  </Card>

  <Card title="Session event stream" icon="lightning" href="https://platform.claude.com/docs/en/managed-agents/events-and-streaming">
    Send events, stream responses, and interrupt or redirect your session mid-execution.
  </Card>
</CardGroup>


---
title: Skills
url: https://platform.claude.com/docs/en/managed-agents/skills
description: Attach pre-built or custom skills to an agent in Claude Managed Agents to give it reusable, filesystem-based expertise for domain-specific workflows.
---

Skills are reusable, filesystem-based resources that give your agent domain-specific expertise: workflows, context, and best practices that turn a general-purpose agent into a specialist. Each skill you add incurs a modest cost on the session's context window, adding instructions and metadata that help the model use the skill. Learn more in the [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) overview.

Skills reach your agent in two ways: attach them through the agent's `skills` array, or [load them from a GitHub repository](https://platform.claude.com/docs/en/managed-agents/skills#load-skills-from-a-github-repository) mounted on the session. Attached skills come in two types. All skills work the same way: your agent invokes them automatically when they are relevant to the task.

* **Pre-built Anthropic skills:** Common document tasks such as PowerPoint, Excel, Word, and PDF handling (`pptx`, `xlsx`, `docx`, `pdf`).
* **Custom skills:** Skills you author and upload to your workspace.

To learn how to author custom skills, see [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) and [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). To upload a custom skill to your workspace, see [Create a custom skill](https://platform.claude.com/docs/en/managed-agents/skills#create-a-custom-skill).

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Create a custom skill

Source: https://platform.claude.com/llms-full.txt#create-a-custom-skill

A custom skill is a directory containing a `SKILL.md` file plus any supporting files, uploaded to your workspace as a zip archive or as individual files. Creating the skill returns the `skill_*` ID you reference when attaching it to an agent. Anthropic pre-built skills are already available in every workspace and don't require this step. To use only pre-built skills, skip to [Attach skills to an agent](https://platform.claude.com/docs/en/managed-agents/skills#attach-skills-to-an-agent).

These examples omit the optional `display_name` field, so the skill's display name is derived from the `name` field in `SKILL.md`. An explicit `display_name` can be up to 255 characters and doesn't need to be unique within your workspace.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl -X POST "https://api.anthropic.com/v1/skills" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -F "files[]=@example_skill.zip"

bash CLI
  ant skills create --file example_skill.zip

python Python
  import anthropic
  from anthropic.lib import files_from_dir

  client = anthropic.Anthropic()

  skill = client.skills.create(
      files=files_from_dir("example_skill"),
  )

  print(f"Created skill: {skill.id}")
  print(f"Latest version: {skill.latest_version_id}")

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";
  import { toFile } from "@anthropic-ai/sdk";
  import fs from "node:fs";

  const client = new Anthropic();

  const skill = await client.skills.create({
    files: [await toFile(fs.createReadStream("example_skill.zip"), "example_skill.zip")]
  });

  console.log(`Created skill: ${skill.id}`);
  console.log(`Latest version: ${skill.latest_version_id}`);

csharp C#
  using System.IO;
  using Anthropic;
  using Anthropic.Models.Skills;

  AnthropicClient client = new();

  var parameters = new SkillCreateParams
  {
      Files = [
          new FileStream("example_skill.zip", FileMode.Open, FileAccess.Read)
      ],
  };

  var skill = await client.Skills.Create(parameters);

  Console.WriteLine($"Created skill: {skill.ID}");
  Console.WriteLine($"Latest version: {skill.LatestVersionID}");

go Go
  package main

  import (
  	"context"
  	"fmt"
  	"io"
  	"log"
  	"os"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  func main() {
  	client := anthropic.NewClient()

  	zipFile, err := os.Open("example_skill.zip")
  	if err != nil {
  		log.Fatal(err)
  	}
  	defer zipFile.Close()

  	skill, err := client.Skills.New(context.TODO(), anthropic.SkillNewParams{
  		Files: []io.Reader{zipFile},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	fmt.Printf("Created skill: %s\n", skill.ID)
  	fmt.Printf("Latest version: %s\n", skill.LatestVersionID)
  }

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.MultipartField;
  import com.anthropic.models.skills.Skill;
  import com.anthropic.models.skills.SkillCreateParams;
  import java.io.IOException;
  import java.io.InputStream;
  import java.nio.file.Files;
  import java.nio.file.Path;

  void main() throws IOException {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      SkillCreateParams params = SkillCreateParams.builder()
          .addFile(MultipartField.<InputStream>builder()
              .value(Files.newInputStream(Path.of("example_skill.zip")))
              .filename("example_skill.zip")
              .contentType("application/zip")
              .build())
          .build();

      Skill skill = client.skills().create(params);

      IO.println("Created skill: " + skill.id());
      IO.println("Latest version: " + skill.latestVersionId());
  }

php PHP
  use Anthropic\Client;
  use Anthropic\Core\FileParam;

  $client = new Client();

  $skill = $client->skills->create(
      files: [
          FileParam::fromResource(fopen('example_skill.zip', 'r')),
      ],
  );

  echo "Created skill: {$skill->id}\n";
  echo "Latest version: {$skill->latestVersionID}\n";

ruby Ruby
  require "anthropic"

  client = Anthropic::Client.new

  skill = client.skills.create(
    files: [
      File.open("example_skill.zip", "rb")
    ]
  )

  puts "Created skill: #{skill.id}"
  puts "Latest version: #{skill.latest_version_id}"
  ```
</CodeGroup>

To list, retrieve, delete, and version custom skills, see [Managing custom skills](https://platform.claude.com/docs/en/build-with-claude/skills-guide#managing-custom-skills). For the full request and response schemas, see the [Create Skill API reference](https://platform.claude.com/docs/en/api/skills/create). Skill bundles upload directly to the Skills API rather than through the [Files API](https://platform.claude.com/docs/en/build-with-claude/files).
