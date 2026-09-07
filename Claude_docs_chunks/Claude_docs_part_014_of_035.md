# platform.claude.com Documentation (Part 14 of 35)

## Tunnel won't connect

Source: https://platform.claude.com/llms-full.txt#tunnel-won-t-connect

Check the cloudflared logs first. Common causes:

* The `TUNNEL_TOKEN` is missing, expired, or copied incorrectly.
* A firewall is blocking outbound TCP/UDP on port 7844 to the tunnel edge.

cloudflared may also log warnings about UDP receive buffer sizes; this is a QUIC tuning hint, not an error.


## Certificate errors

Source: https://platform.claude.com/llms-full.txt#certificate-errors

When Anthropic rejects the proxy's certificate during inner TLS, the proxy logs `tls handshake failed`. Verify that:

* The server certificate has not expired.
* The certificate's Subject Alternative Name matches `*.<tunnel-domain>`.
* The signing CA is registered with Anthropic for this tunnel.

See the [certificate requirements](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference#certificate-requirements) for the full validation rules.


## Upstream IP validation

Source: https://platform.claude.com/llms-full.txt#upstream-ip-validation

For SSRF protection, the proxy only dials addresses in the RFC1918 private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) by default. Only IPv4 is supported for the proxy-to-upstream connection. (The cloudflared-to-edge egress range in [Network requirements](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#network-requirements) is a different hop.)

If the proxy logs `IP validation failed: <ip> is not a private address`, the upstream hostname resolved outside that set. On Kubernetes, some managed distributions allocate the Service CIDR outside RFC1918; if `kubectl get svc kubernetes -n default -o jsonpath='{.spec.clusterIP}'` returns an address outside the private ranges, look up your cluster's Service CIDR and add it.

If the address is legitimate, add the narrowest covering CIDR to `upstream.allowed_ips`. Setting `allowed_ips` **replaces** the RFC1918 default rather than extending it, so include the private ranges your other upstream MCP servers use:

```yaml config/mcp-proxy.yaml
upstream:
  allowed_ips:
    - 10.0.0.0/8
    - 172.16.0.0/12
    - 192.168.0.0/16
    - 127.0.0.0/8       # loopback, for local testing only
```

<Warning>
  Avoid `0.0.0.0/0` outside of local testing; it disables SSRF protection entirely.
</Warning>


### Claude on cloud platforms

---
title: Claude in Amazon Bedrock (Opus 4.7 and later)
url: https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock
description: Access Claude models through Amazon Bedrock with AWS-native authentication, billing, and security boundaries.
---

This guide walks you through setting up and making API calls to Claude in Amazon Bedrock. Claude in Amazon Bedrock runs on AWS-managed infrastructure with zero operator access (Anthropic personnel have no access to the inference infrastructure), letting you build sensitive applications entirely inside the AWS security boundary while using the same Messages API shape you use with Anthropic's first-party API.

<Note>
  This page covers Claude in Amazon Bedrock, which serves Claude through the Messages API at `/anthropic/v1/messages` on AWS-managed infrastructure. The previous Amazon Bedrock integration (the `InvokeModel` and `Converse` APIs with ARN-versioned model identifiers) remains available and is documented at [Claude on Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy). For an Anthropic-operated alternative on AWS with AWS Marketplace billing and typically same-day feature access, see [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws).
</Note>


## Access

Source: https://platform.claude.com/llms-full.txt#access

Amazon Bedrock sets access criteria for each Claude model individually. Claude Fable 5.1, Claude Fable 5, Claude Opus 4.8, Claude Sonnet 5, Claude Opus 4.7, and Claude Haiku 4.5 are open to all Amazon Bedrock customers. For any other model's current criteria, check [Amazon Bedrock model access](https://console.aws.amazon.com/bedrock/home#/modelaccess) in the AWS console. Claude Mythos Preview requires an invitation through [Project Glasswing](https://anthropic.com/glasswing). For region availability, see [Regions](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock#regions).


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-6

Before you begin, ensure you have:

* An AWS account with [Amazon Bedrock model access](https://console.aws.amazon.com/bedrock/home#/modelaccess) enabled for the Claude models you intend to use.
* The [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) installed and configured (optional, for credential management).

Claude Mythos Preview additionally requires a dedicated AWS account that has been allowlisted by the Bedrock Marketplace team. Your Anthropic account executive can submit your account ID for allowlisting (typically processed within 24 hours), and AWS sends a welcome email once it's complete.


## Authentication

Source: https://platform.claude.com/llms-full.txt#authentication-2

Claude in Amazon Bedrock supports three authentication paths. Choose the one that best fits your security requirements.

### Bedrock service role (recommended)

Use a Bedrock service role with AWS-managed keys for the most secure, long-lived access:

<Steps>
  <Step title="Admin: provision the service role">
    An AWS administrator provisions a Bedrock service role and grants developers `iam:PassRole` permission on the service role ARN.
  </Step>

  <Step title="Developer: pass the role">
    When calling the API, Bedrock assumes the service role on your behalf. See the [Amazon Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-mantle.html) for how to associate the role with your requests.
  </Step>
</Steps>

### IAM assumed roles

For identity-federated access with a 12-hour maximum session:

<Steps>
  <Step title="Admin: configure the IAM role">
    Create an IAM role scoped to your Claude models. The trust policy names your identity provider (SAML, OIDC, or AWS Identity Center). The permissions policy grants `bedrock-mantle:CreateInference` only on the allowed model ARNs.
  </Step>

  <Step title="Developer: authenticate and assume">
    Authenticate through your corporate identity provider, then assume the IAM role. AWS STS issues temporary credentials that the SDK or CLI uses to sign requests.
  </Step>
</Steps>

### Bearer tokens

For short-term access without IAM roles (12-hour maximum, least preferred):

<Steps>
  <Step title="Admin: restrict token types">
    Block long-term keys by attaching a policy that denies `bedrock:CallWithBearerToken` unless the `bedrock:BearerTokenType` condition matches a short-term token.
  </Step>

  <Step title="Developer: mint a token">
    Use the `aws-bedrock-token-generator` CLI to mint a bearer token. Pass it in the `x-api-key` header on each request.
  </Step>
</Steps>


## Install an SDK

Source: https://platform.claude.com/llms-full.txt#install-an-sdk

Anthropic's [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) support Claude in Amazon Bedrock through a Bedrock-specific package or module.

<Tabs>
  <Tab title="Python">

</Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="C#">

</Tab>

  <Tab title="Go">

</Tab>

  <Tab title="Java">
    <Tabs>
      <Tab title="Gradle">

</Tab>

      <Tab title="Maven">

</Tab>
    </Tabs>
  </Tab>

  <Tab title="PHP">

</Tab>

  <Tab title="Ruby">

</Tab>
</Tabs>


## Making your first request

Source: https://platform.claude.com/llms-full.txt#making-your-first-request

The endpoint follows the pattern `https://bedrock-mantle.{region}.api.aws/anthropic/v1/messages`. Unlike the `InvokeModel`-based integration, this endpoint uses standard SSE streaming and the same request body shape as Anthropic's first-party API.

The SDK resolves credentials and region using the standard AWS precedence: constructor arguments, then environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_REGION`), then the AWS config file and credential chain (SSO, assumed roles, ECS task role, IMDS).

<Tabs>
  <Tab title="cURL">

</Tab>

  <Tab title="CLI">
    The `ant` CLI does not support Amazon Bedrock. Use either cURL or an SDK.
  </Tab>

  <Tab title="Python">

</Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="C#">

</Tab>

  <Tab title="Go">

</Tab>

  <Tab title="Java">

</Tab>

  <Tab title="PHP">

</Tab>

  <Tab title="Ruby">

</Tab>
</Tabs>

<Tip>
  You can also use the standard `Anthropic` client: set `base_url` to `https://bedrock-mantle.{region}.api.aws/anthropic` and pass your bearer token as `api_key`. This path supports bearer-token authentication only. SigV4 signing requires the dedicated client.
</Tip>


## Supported models

Source: https://platform.claude.com/llms-full.txt#supported-models-5

Model IDs in Claude in Amazon Bedrock carry an `anthropic.` provider prefix. Model capabilities and behaviors are documented on the [Models overview](https://platform.claude.com/docs/en/models/overview) page.

| Model                 | Model ID                        | Access                                                                                              |
| --------------------- | ------------------------------- | --------------------------------------------------------------------------------------------------- |
| Claude Fable 5.1      | anthropic.claude-fable-5-1      | Open                                                                                                |
| Claude Fable 5        | anthropic.claude-fable-5        | Open                                                                                                |
| Claude Opus 5         | anthropic.claude-opus-5         | See [Access](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock#access) |
| Claude Opus 4.8       | anthropic.claude-opus-4-8       | Open                                                                                                |
| Claude Opus 4.7       | anthropic.claude-opus-4-7       | Open                                                                                                |
| Claude Sonnet 5       | `anthropic.claude-sonnet-5`     | Open                                                                                                |
| Claude Haiku 4.5      | anthropic.claude-haiku-4-5      | Open                                                                                                |
| Claude Mythos Preview | anthropic.claude-mythos-preview | Invitation only ([Project Glasswing](https://anthropic.com/glasswing))                              |

Use Claude Code 2.1.255 or later with Claude Fable 5.1 on Amazon Bedrock; run `claude update` to upgrade.

<Tip>
  Upgrading to a newer Claude model? In Claude Code, run `/claude-api migrate` to apply model ID swaps and breaking parameter changes across your codebase. The skill detects which cloud platform your code targets and adjusts model ID formats and feature changes for that platform. See [Migrating to a newer Claude model](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill#migrating-to-a-newer-claude-model).
</Tip>


## Feature support

Source: https://platform.claude.com/llms-full.txt#feature-support-2

For the full feature list with Amazon Bedrock availability, see [Features overview](https://platform.claude.com/docs/en/build-with-claude/overview).

### Supported feature highlights

* [Messages API](https://platform.claude.com/docs/en/api/messages/create) (`/anthropic/v1/messages`)
* [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
* [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)
* [Tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview), including the [Bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool), [Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool), [Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool), and [Text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)
* [Citations](https://platform.claude.com/docs/en/build-with-claude/citations)

### Features not supported

* [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
* Input sources (URL sources for images and documents, Files API)
* Server-side tools (code execution, web search, web fetch, advisor)
* Agent infrastructure (Agent Skills, MCP connector, programmatic tool calling)
* API endpoints (Message Batches, Models, Admin, Compliance, Usage and Cost)
* Claude Managed Agents
* Server-side fallback (the [`fallbacks` parameter](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#server-side-fallback); use the [client-side fallback pattern](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#client-side-fallback) instead)
* [Computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) toolsets (`computer_toolset_20260801` and `browser_toolset_20260801` are not currently available on Amazon Bedrock; the beta computer use tool versions remain available)


## Regions

Source: https://platform.claude.com/llms-full.txt#regions

Claude in Amazon Bedrock is available in the following AWS regions. Amazon Bedrock offers two endpoint types:

* **Global:** dynamic routing across all available regions for maximum availability. No pricing premium.
* **Regional:** the endpoint resolves to the single AWS region you specify, for data-residency requirements. Regional endpoints carry a 10% pricing premium over global endpoints. To route across multiple regions within a geography, use an [inference profile](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) (US, EU, JP, or AU). Regions marked **In-region only** in the table support direct single-region routing without an inference profile.

The global endpoint is available for Claude Fable 5.1, Claude Fable 5, Claude Opus 5, Claude Opus 4.8, Claude Opus 4.7, Claude Sonnet 5, and Claude Haiku 4.5. For Claude Fable 5.1, regional endpoints are currently available in `us-east-1` only. Claude Mythos Preview is regional only and is available in `us-east-1`.

| AWS region       | Location                  | Endpoint types             |
| ---------------- | ------------------------- | -------------------------- |
| `af-south-1`     | Africa (Cape Town)        | Global                     |
| `ap-northeast-1` | Asia Pacific (Tokyo)      | Global, JP, In-region only |
| `ap-northeast-2` | Asia Pacific (Seoul)      | Global                     |
| `ap-northeast-3` | Asia Pacific (Osaka)      | Global, JP                 |
| `ap-south-1`     | Asia Pacific (Mumbai)     | Global                     |
| `ap-south-2`     | Asia Pacific (Hyderabad)  | Global                     |
| `ap-southeast-1` | Asia Pacific (Singapore)  | Global                     |
| `ap-southeast-2` | Asia Pacific (Sydney)     | Global, AU                 |
| `ap-southeast-3` | Asia Pacific (Jakarta)    | Global                     |
| `ap-southeast-4` | Asia Pacific (Melbourne)  | Global, AU, In-region only |
| `ca-central-1`   | Canada (Central)          | Global, US                 |
| `ca-west-1`      | Canada West (Calgary)     | Global                     |
| `eu-central-1`   | Europe (Frankfurt)        | Global, EU                 |
| `eu-central-2`   | Europe (Zurich)           | Global, EU                 |
| `eu-north-1`     | Europe (Stockholm)        | Global, EU, In-region only |
| `eu-south-1`     | Europe (Milan)            | Global, EU                 |
| `eu-south-2`     | Europe (Spain)            | Global, EU                 |
| `eu-west-1`      | Europe (Ireland)          | Global, EU, In-region only |
| `eu-west-2`      | Europe (London)           | Global, EU                 |
| `eu-west-3`      | Europe (Paris)            | Global, EU                 |
| `il-central-1`   | Israel (Tel Aviv)         | Global                     |
| `me-central-1`   | Middle East (UAE)         | Global                     |
| `sa-east-1`      | South America (São Paulo) | Global                     |
| `us-east-1`      | US East (N. Virginia)     | Global, US, In-region only |
| `us-east-2`      | US East (Ohio)            | Global, US, In-region only |
| `us-west-1`      | US West (N. California)   | Global, US                 |
| `us-west-2`      | US West (Oregon)          | Global, US, In-region only |


## Quotas

Source: https://platform.claude.com/llms-full.txt#quotas

Default quota is 2 million input tokens per minute (TPM). You can request up to 5 million input TPM and 500,000 output TPM without additional Anthropic approval. AWS enforces requests-per-minute (RPM) limits on the Bedrock side; contact AWS support for RPM adjustments.


## Data retention

Source: https://platform.claude.com/llms-full.txt#data-retention-12

Data handling for this offering is governed by Amazon Bedrock. For details, see [Data protection in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html).


## Monitoring and logging

Source: https://platform.claude.com/llms-full.txt#monitoring-and-logging

Claude in Amazon Bedrock emits logs to both CloudWatch and CloudTrail. Anthropic recommends retaining activity logs on at least a 30-day rolling basis to understand usage patterns and investigate potential issues.


## Support

Source: https://platform.claude.com/llms-full.txt#support-2

For support, contact **[bedrock-ant-eap@amazon.com](mailto:bedrock-ant-eap@amazon.com)**. Include your AWS account ID and the `request-id` from any failed API responses.

<Note>
  **Claude Mythos Preview** is a research preview model available to invited customers on Amazon Bedrock. For more information, see [Project Glasswing](https://anthropic.com/glasswing).
</Note>


---
title: Claude in Microsoft Foundry
url: https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry
description: Access Claude models through Microsoft Foundry with Azure-native endpoints and authentication.
---

This guide shows you how to set up and make API calls to Claude in Microsoft Foundry using one of Anthropic's client SDKs or direct HTTP requests. When you access Claude in Microsoft Foundry, you are billed for Claude usage in the Azure Marketplace. You can use Claude models including Claude Fable 5.1, Claude Opus 5, Claude Opus 4.8, and Claude Sonnet 5, and features such as the [1M-token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows), while managing costs through your Azure subscription.

Claude is available in Global Standard and US Data Zone Standard deployment types in Foundry resources, billed in Claude Consumption Units through the Azure Marketplace. Visit [Claude in Microsoft Foundry pricing](https://platform.claude.com/docs/en/about-claude/pricing#claude-in-microsoft-foundry-pricing) for details.


## Hosting options

Source: https://platform.claude.com/llms-full.txt#hosting-options

Claude models in Microsoft Foundry are available in two hosting options. You choose the hosting option when you configure the deployment.

|                      | Hosted on Azure                                            | Hosted on Anthropic                                                                                                                                                                              |
| -------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Where inference runs | Anthropic-operated service running on Azure infrastructure | Anthropic-operated service running on Anthropic infrastructure                                                                                                                                   |
| Model availability   | The latest models in the Opus, Sonnet, and Haiku families  | All Claude models available on Microsoft Foundry                                                                                                                                                 |
| Deployment types     | Global Standard, US Data Zone Standard                     | Global Standard                                                                                                                                                                                  |
| Recommended for      | Most workloads                                             | [Access to features or models not yet hosted on Azure](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#additional-features-not-supported-when-hosted-on-azure) |

<Note>
  Anthropic acts as an independent processor for Microsoft. Customers using Claude through Microsoft Foundry are subject to Anthropic's data use terms. For deployments hosted on Azure, prompts and completions remain within Azure. Only usage metadata and content flagged by Anthropic's safety systems egress to Anthropic. Anthropic continues to provide its safety and data commitments.
</Note>


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-7

Before you begin, ensure you have:

* An active Azure subscription
* Access to the [Foundry portal](https://ai.azure.com/)
* The [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed (required for the Entra ID cURL example, optional otherwise)
* An Azure RBAC role that allows you to use the resource, such as **Foundry User** (formerly Azure AI User) or **Cognitive Services User**


## Install an SDK

Source: https://platform.claude.com/llms-full.txt#install-an-sdk-2

Anthropic's [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) support Foundry through a platform-specific package or client class. The examples on this page also show requests with cURL and the ant CLI. To set up the CLI, see [CLI quickstart](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/quickstart).

<Note>
  Foundry is supported by the C#, Java, PHP, Python, and TypeScript SDKs. Foundry is not currently available in the Go and Ruby SDKs.
</Note>

<Tabs>
  <Tab title="Python">

</Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="C#">

</Tab>

  <Tab title="Go">

</Tab>

  <Tab title="Java">
    <Tabs>
      <Tab title="Gradle">

</Tab>

      <Tab title="Maven">

</Tab>
    </Tabs>
  </Tab>

  <Tab title="PHP">

</Tab>

  <Tab title="Ruby">

</Tab>
</Tabs>


## Provisioning

Source: https://platform.claude.com/llms-full.txt#provisioning

Foundry uses a two-level hierarchy: **resources** contain your security and billing configuration, while **deployments** are the model instances you call through the API. You'll first create a Foundry resource, then create one or more Claude deployments within it.

### Provisioning Foundry resources

Create a Foundry resource, which is required to use and manage services in Azure. You can follow these instructions to create a [Foundry resource](https://learn.microsoft.com/en-us/azure/ai-services/multi-service-resource?pivots=azportal#create-a-new-azure-ai-foundry-resource). Alternatively, you can start by creating a [Foundry project](https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects), which involves creating a Foundry resource.

To provision your resource:

1. Navigate to the [Foundry portal](https://ai.azure.com/).
2. Create a new Foundry resource or select an existing one.
3. Configure access management using Azure-issued API keys or Entra ID (formerly Azure Active Directory) for role-based access control.
4. Optionally configure the resource to be part of a private network (Azure Virtual Network) to restrict network access to your resource.
5. Note your resource name. You'll use this as `{resource}` in API endpoints (for example, `https://{resource}.services.ai.azure.com/anthropic/v1/*`).

### Creating Foundry deployments

After creating your resource, deploy a Claude model to make it available for API calls. These steps describe the new Foundry portal (the **New Foundry** toggle is on):

1. Sign in to the Foundry portal. From the portal homepage, select **Discover** in the upper-right navigation, then **Models** in the left pane to open the model catalog.

2. Search for and select a Claude model (for example, claude-opus-5). Each model appears once in the catalog regardless of how many hosting options it supports.

3. On the model card, select **Deploy**, then **Custom settings** to open the deployment settings pane. If you choose **Default settings** instead, the deployment is automatically configured as Hosted on Azure for models available in both hosting options.

4. On your first Claude deployment, review the Azure Marketplace terms, select an industry, and select **Agree and Proceed** to accept the terms and subscribe to the Azure Marketplace offer.

5. Configure the deployment:

   * **Deployment name:** Defaults to the model ID, but you can customize it (for example, `my-claude-deployment`). The deployment name cannot be changed after creation.
   * **Region scope:** Select Global, or for models hosted on Azure, Data Zone. Selecting Data Zone creates a US Data Zone Standard deployment, which keeps inference within the United States and is equivalent to setting [`inference_geo: "us"`](https://platform.claude.com/docs/en/manage-claude/data-residency#inference-geo) on the Claude API.
   * **Model version:** Expand **Model version settings** and select a version from the **Model version** dropdown menu. Each [hosting option](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#hosting-options) is listed as a separate model version, labeled with its hosting option (for example, version 1 for Hosted on Anthropic, version 2 for Hosted on Azure).

6. Select **Deploy** and wait for provisioning to complete.

7. Once deployed, select **Build** in the upper-right navigation, then **Models** in the left pane, and open your deployment. The **Details** tab shows the **Target URI** (your endpoint URL) and **Key** (your API key).

If the **New Foundry** toggle is off, you are in the classic portal layout. There, open **Model catalog** in the left pane to find and deploy a model, and open **Models + endpoints** (under **My assets**) to view your deployments and their endpoint details.

<Note>
  The deployment name you choose becomes the value you pass in the `model` parameter of your API requests. You can create multiple deployments of the same model with different names to manage separate configurations or rate limits.
</Note>


## Authentication

Source: https://platform.claude.com/llms-full.txt#authentication-3

Claude in Microsoft Foundry supports two authentication methods: API keys and Entra ID tokens. Both methods use Azure-hosted endpoints in the format `https://{resource}.services.ai.azure.com/anthropic/v1/*`.

### API key authentication

After provisioning your Foundry Claude resource, you can obtain an API key from the Foundry portal:

1. In the Foundry portal, select **Build** in the upper-right navigation, then **Models** in the left pane.
2. Open your Claude deployment and select the **Details** tab.
3. Copy the **Key** value (and note the **Target URI** for your endpoint).
4. Use either the `api-key` or `x-api-key` header in your requests, or provide it to the SDK.

The Foundry SDKs require an API key and either a resource name or base URL. The C#, Java, PHP, Python, and TypeScript SDKs automatically read these from the following environment variables if they are defined:

* `ANTHROPIC_FOUNDRY_API_KEY` - Your API key
* `ANTHROPIC_FOUNDRY_RESOURCE` - Your resource name (for example, `example-resource`)
* `ANTHROPIC_FOUNDRY_BASE_URL` - Alternative to resource name: the full base URL (for example, `https://example-resource.services.ai.azure.com/anthropic/`). The C# SDK does not read this variable: it always constructs the base URL from the resource name.

<Note>
  The `resource` and `base_url` parameters are mutually exclusive. Provide either the resource name (which the SDK uses to construct the URL as `https://{resource}.services.ai.azure.com/anthropic/`) or the full base URL directly.
</Note>

**Example using API key:**

<CodeGroup>
  ```bash cURL
  curl https://{resource}.services.ai.azure.com/anthropic/v1/messages \
    -H "content-type: application/json" \
    -H "api-key: YOUR_AZURE_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [
        {"role": "user", "content": "Hello!"}
      ]
    }'

bash CLI
  # ant reads ANTHROPIC_API_KEY and sends it as x-api-key, which Foundry accepts
  export ANTHROPIC_API_KEY="YOUR_AZURE_API_KEY"

  ant messages create \
    --base-url https://example-resource.services.ai.azure.com/anthropic \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello!"}' \
    --transform content

python Python
  import os
  from anthropic import AnthropicFoundry

  client = AnthropicFoundry(
      api_key=os.environ.get("ANTHROPIC_FOUNDRY_API_KEY"),
      resource="example-resource",  # your resource name
  )

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello!"}],
  )
  print(message.content)

typescript TypeScript
  import AnthropicFoundry from "@anthropic-ai/foundry-sdk";

  const client = new AnthropicFoundry({
    apiKey: process.env.ANTHROPIC_FOUNDRY_API_KEY,
    resource: "example-resource" // your resource name
  });

  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello!" }]
  });
  console.log(message.content);

csharp C#
  using Anthropic.Foundry;
  using Anthropic.Models.Messages;

  var client = new AnthropicFoundryClient(
      new AnthropicFoundryApiKeyCredentials(
          Environment.GetEnvironmentVariable("ANTHROPIC_FOUNDRY_API_KEY")!,
          "example-resource"
      )
  );

  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello!" }],
  });

  Console.WriteLine(
      string.Join("", response.Content
          .Select(block => block.Value)
          .OfType<TextBlock>()
          .Select(textBlock => textBlock.Text)));

go Go
  // The Go SDK does not yet support Foundry natively. This example uses the
  // standard Go SDK as a workaround. WithoutEnvironmentDefaults keeps the
  // client from also reading ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN from
  // the environment and sending a Claude API credential to your Foundry
  // endpoint. Features that Foundry does not support fail server-side rather
  // than client-side. For full Foundry support, use the C#, Java, PHP,
  // Python, or TypeScript SDKs.
  package main

  import (
  	"context"
  	"fmt"
  	"os"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/option"
  )

  func main() {
  	client := anthropic.NewClient(
  		option.WithoutEnvironmentDefaults(),
  		option.WithBaseURL("https://example-resource.services.ai.azure.com/anthropic"),
  		option.WithAPIKey(os.Getenv("ANTHROPIC_FOUNDRY_API_KEY")),
  	)

  	message, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  		Model:     "claude-opus-5",
  		MaxTokens: 1024,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hello!")),
  		},
  	})
  	if err != nil {
  		panic(err)
  	}
  	fmt.Println(message.Content)
  }

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.foundry.backends.FoundryBackend;
  import com.anthropic.models.messages.MessageCreateParams;

  void main() {
      // Requires env vars: ANTHROPIC_FOUNDRY_API_KEY, ANTHROPIC_FOUNDRY_RESOURCE
      AnthropicClient client = AnthropicOkHttpClient.builder()
          .backend(FoundryBackend.fromEnv())
          .build();

      MessageCreateParams params = MessageCreateParams.builder()
          .model("claude-opus-5")
          .maxTokens(1024)
          .addUserMessage("Hello!")
          .build();

      client.messages().create(params).content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  use Anthropic\Foundry;

  $client = Foundry\Client::withCredentials(
      apiKey: getenv('ANTHROPIC_FOUNDRY_API_KEY'),
      baseUrl: 'https://example-resource.services.ai.azure.com/anthropic',
  );

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => 'Hello!']
      ],
      model: 'claude-opus-5',
  );
  echo array_find($message->content, fn ($block) => $block->type === 'text')->text;

ruby Ruby
  # The Ruby SDK does not yet support Foundry natively. This example uses the
  # standard Ruby SDK as a workaround. Pass credentials explicitly: without
  # them, the client falls back to the ANTHROPIC_API_KEY or
  # ANTHROPIC_AUTH_TOKEN environment variables and could send a Claude API
  # credential to your Foundry endpoint. Features that Foundry
  # does not support fail server-side rather than client-side. For full
  # Foundry support, use the C#, Java, PHP, Python, or TypeScript SDKs.
  require "anthropic"

  client = Anthropic::Client.new(
    base_url: "https://example-resource.services.ai.azure.com/anthropic",
    api_key: ENV.fetch("ANTHROPIC_FOUNDRY_API_KEY")
  )

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello!"}]
  )

  puts message.content.find { it.type == :text }.text

bash cURL
  # Get Microsoft Entra ID token
  ACCESS_TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)

  # Make request with token. Replace {resource} with your resource name
  curl https://{resource}.services.ai.azure.com/anthropic/v1/messages \
    -H "content-type: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [
        {"role": "user", "content": "Hello!"}
      ]
    }'

bash CLI
  # The ant CLI can send a bearer token with --auth-token, but a set
  # ANTHROPIC_API_KEY environment variable takes precedence over it (the CLI
  # prints only a console notice), so your request could authenticate with
  # the wrong credential. For the Entra ID flow, use the cURL example or one
  # of the SDK examples instead.

python Python
  from anthropic import AnthropicFoundry
  from azure.identity import DefaultAzureCredential, get_bearer_token_provider

  # Get Microsoft Entra ID token using token provider pattern
  token_provider = get_bearer_token_provider(
      DefaultAzureCredential(), "https://ai.azure.com/.default"
  )

  # Create client with Entra ID authentication
  client = AnthropicFoundry(
      resource="example-resource",  # your resource name
      azure_ad_token_provider=token_provider,  # Use token provider for Entra ID auth
  )

  # Make request
  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello!"}],
  )
  print(message.content)

typescript TypeScript
  import AnthropicFoundry from "@anthropic-ai/foundry-sdk";
  import { DefaultAzureCredential, getBearerTokenProvider } from "@azure/identity";

  // Get Entra ID token using token provider pattern
  const credential = new DefaultAzureCredential();
  const tokenProvider = getBearerTokenProvider(credential, "https://ai.azure.com/.default");

  // Create client with Entra ID authentication
  const client = new AnthropicFoundry({
    resource: "example-resource", // your resource name
    azureADTokenProvider: tokenProvider // Use token provider for Entra ID auth
  });

  // Make request
  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello!" }]
  });
  console.log(message.content);

csharp C#
  using Anthropic.Foundry;
  using Anthropic.Models.Messages;
  using Azure.Identity;

  var client = new AnthropicFoundryClient(
      new AnthropicFoundryIdentityTokenCredentials(
          new DefaultAzureCredential(),
          "example-resource"
      )
  );

  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello!" }],
  });

  Console.WriteLine(
      string.Join("", response.Content
          .Select(block => block.Value)
          .OfType<TextBlock>()
          .Select(textBlock => textBlock.Text)));

go Go
  // The Go SDK does not yet support Foundry natively. This example uses the
  // standard Go SDK as a workaround, with a static Entra ID token: automatic
  // token refresh is not built in, so your application must refresh tokens
  // itself (they typically expire after 1 hour). WithoutEnvironmentDefaults
  // keeps the client from also reading ANTHROPIC_API_KEY or
  // ANTHROPIC_AUTH_TOKEN from the environment and sending a Claude API
  // credential to your Foundry endpoint. For full Foundry support, use the
  // C#, Java, PHP, Python, or TypeScript SDKs.
  package main

  import (
  	"context"
  	"fmt"
  	"os"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/option"
  )

  func main() {
  	// Obtain an Entra ID access token, for example using the Azure CLI:
  	//   az account get-access-token --resource https://ai.azure.com \
  	//     --query accessToken -o tsv
  	client := anthropic.NewClient(
  		option.WithoutEnvironmentDefaults(),
  		option.WithBaseURL("https://example-resource.services.ai.azure.com/anthropic"),
  		option.WithAuthToken(os.Getenv("AZURE_ACCESS_TOKEN")),
  	)

  	message, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  		Model:     "claude-opus-5",
  		MaxTokens: 1024,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hello!")),
  		},
  	})
  	if err != nil {
  		panic(err)
  	}
  	fmt.Println(message.Content)
  }

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.foundry.backends.FoundryBackend;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.azure.identity.AuthenticationUtil;
  import com.azure.identity.DefaultAzureCredentialBuilder;
  import java.util.function.Supplier;

  void main() {
      Supplier<String> bearerTokenSupplier = AuthenticationUtil.getBearerTokenSupplier(
          new DefaultAzureCredentialBuilder().build(),
          "https://ai.azure.com/.default"
      );

      AnthropicClient client = AnthropicOkHttpClient.builder()
          .backend(FoundryBackend.builder()
              .bearerTokenSupplier(bearerTokenSupplier)
              .resource("example-resource")
              .build())
          .build();

      MessageCreateParams params = MessageCreateParams.builder()
          .model("claude-opus-5")
          .maxTokens(1024)
          .addUserMessage("Hello!")
          .build();

      client.messages().create(params).content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  use Anthropic\Foundry;

  // Obtain an Entra ID access token, for example using the Azure CLI:
  //   az account get-access-token --resource https://ai.azure.com \
  //     --query accessToken -o tsv
  $token = getenv('AZURE_ACCESS_TOKEN');

  $client = Foundry\Client::withCredentials(
      authToken: $token,
      baseUrl: 'https://example-resource.services.ai.azure.com/anthropic',
  );

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => 'Hello!']
      ],
      model: 'claude-opus-5',
  );
  echo array_find($message->content, fn ($block) => $block->type === 'text')->text;

ruby Ruby
  # The Ruby SDK does not yet support Foundry natively. This example uses the
  # standard Ruby SDK as a workaround, with a static Entra ID token: automatic
  # token refresh is not built in, so your application must refresh tokens
  # itself (they typically expire after 1 hour). Pass credentials explicitly:
  # without them, the client falls back to the ANTHROPIC_API_KEY or
  # ANTHROPIC_AUTH_TOKEN environment variables. For full Foundry support, use
  # the C#, Java, PHP, Python, or TypeScript SDKs.
  require "anthropic"

  # Obtain an Entra ID access token, for example using the Azure CLI:
  #   az account get-access-token --resource https://ai.azure.com \
  #     --query accessToken -o tsv
  client = Anthropic::Client.new(
    base_url: "https://example-resource.services.ai.azure.com/anthropic",
    auth_token: ENV.fetch("AZURE_ACCESS_TOKEN")
  )

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello!"}]
  )

  puts message.content.find { it.type == :text }.text
  ```
</CodeGroup>


## Correlation request IDs

Source: https://platform.claude.com/llms-full.txt#correlation-request-ids

Foundry includes request identifiers in HTTP response headers for debugging and tracing. When contacting support, provide both the `request-id` and `apim-request-id` (Azure API Management) values to help teams quickly locate and investigate your request across both Anthropic and Azure systems.


## Feature support

Source: https://platform.claude.com/llms-full.txt#feature-support-3

Claude in Microsoft Foundry supports most Claude features. You can find all the features currently supported in [Features overview](https://platform.claude.com/docs/en/build-with-claude/overview).

### Context window

Claude Fable 5.1, Claude Fable 5, Claude Opus 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, and Claude Sonnet 4.6 have a [1M-token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) on Microsoft Foundry. Other Claude models, including Claude Sonnet 4.5, have a 200k-token context window.

### Claude features not supported for Claude in Microsoft Foundry

* Admin API
* Advisor tool
* Claude Managed Agents
* Compliance API
* Models API
* Message Batches API
* Server-side fallback (the [`fallbacks` parameter](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#server-side-fallback); use the [client-side fallback pattern](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#client-side-fallback) instead)
* [Computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) toolsets (`computer_toolset_20260801` and `browser_toolset_20260801` are not currently available on Microsoft Foundry; the beta computer use tool versions remain available)

### Additional features not supported when hosted on Azure

The following features are available for deployments hosted on Anthropic but are not supported for deployments hosted on Azure:

* [Code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)
* [Web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) and [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) tool versions later than `web_search_20250305` and `web_fetch_20250910`. Deployments hosted on Azure support only these basic versions, so dynamic filtering, response inclusion, and cache bypass are not available.
* [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
* [Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)
* [Files API](https://platform.claude.com/docs/en/build-with-claude/files)

Requests that use these features against a deployment hosted on Azure return a `400 Bad Request` error by design. Claude Code detects deployments hosted on Azure and automatically adapts its feature set.


## API responses

Source: https://platform.claude.com/llms-full.txt#api-responses

API responses from Claude in Microsoft Foundry follow the standard [Claude API response format](https://platform.claude.com/docs/en/api/messages/create). This includes the `usage` object in response bodies, which provides detailed token consumption information for your requests. The `usage` object is consistent across all platforms (Claude API, Amazon Bedrock, Claude Platform on AWS, Foundry, and Google Cloud).

For details on response headers specific to Foundry, see [Correlation request IDs](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#correlation-request-ids).


## API model IDs and deployments

Source: https://platform.claude.com/llms-full.txt#api-model-ids-and-deployments

Lifecycle terms (Deprecated, Retired) are defined in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations). Microsoft Foundry follows the Claude API lifecycle schedule.

The following Claude models are available through Foundry:

| Model             | Default deployment name | Hosted on Azure | Hosted on Anthropic |
| ----------------- | ----------------------- | --------------- | ------------------- |
| Claude Fable 5.1  | claude-fable-5-1        |                 | ✓                   |
| Claude Fable 5    | claude-fable-5          |                 | ✓                   |
| Claude Opus 5     | claude-opus-5           | ✓               | ✓                   |
| Claude Opus 4.8   | claude-opus-4-8         | ✓               | ✓                   |
| Claude Opus 4.7   | claude-opus-4-7         |                 | ✓                   |
| Claude Opus 4.6   | claude-opus-4-6         |                 | ✓                   |
| Claude Opus 4.5   | claude-opus-4-5         |                 | ✓                   |
| Claude Sonnet 5   | claude-sonnet-5         | ✓               | ✓                   |
| Claude Sonnet 4.6 | claude-sonnet-4-6       |                 | ✓                   |
| Claude Sonnet 4.5 | claude-sonnet-4-5       |                 | ✓                   |
| Claude Haiku 4.5  | claude-haiku-4-5        | ✓               | ✓                   |

By default, deployment names match the model IDs shown in the preceding table. However, you can create custom deployments with different names in the Foundry portal to manage different configurations, versions, or rate limits. Use the deployment name (not necessarily the model ID) in your API requests.

<Info>
  [Claude Mythos Preview](https://anthropic.com/glasswing) is a research preview available to invited customers on Microsoft Foundry.
</Info>

<Tip>
  Upgrading to a newer Claude model? In Claude Code, run `/claude-api migrate` to apply model ID swaps and breaking parameter changes across your codebase. The skill detects which cloud platform your code targets and adjusts model ID formats and feature changes for that platform. See [Migrating to a newer Claude model](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill#migrating-to-a-newer-claude-model).
</Tip>


## Billing

Source: https://platform.claude.com/llms-full.txt#billing

Claude in Microsoft Foundry bills through the [Azure Marketplace](https://azuremarketplace.microsoft.com/). Usage is denominated in Claude Consumption Units (CCUs), metered hourly, and invoiced monthly in arrears on your Azure bill. CCUs are not prepaid credits. There is no CCU balance or commitment.

For the CCU price, conversion mechanics, and per-model token rates, see [Claude in Microsoft Foundry pricing](https://platform.claude.com/docs/en/about-claude/pricing#claude-in-microsoft-foundry-pricing).


## Migrating between hosting options

Source: https://platform.claude.com/llms-full.txt#migrating-between-hosting-options

To move an existing deployment from one hosting option to the other:

1. Create a new deployment of the model's other hosting version (Hosted on Azure or Hosted on Anthropic). This can be in the same Foundry resource, or a new one.
2. Update your application to pass the new deployment name in the `model` parameter.
3. Delete the old deployment once traffic has moved.

If the new deployment is in the same Foundry resource, your endpoint URL and authentication are unchanged. If you created a new resource, update your application's endpoint and credentials to point to it.


## Monitoring and logging

Source: https://platform.claude.com/llms-full.txt#monitoring-and-logging-2

Azure provides monitoring and logging for your Claude usage through standard Azure patterns:

* **Azure Monitor:** Track API usage, latency, and error rates
* **Azure Log Analytics:** Query and analyze request/response logs
* **Cost Management:** Monitor and forecast costs associated with Claude usage

Anthropic recommends logging your activity on at least a 30-day rolling basis to understand usage patterns and investigate any potential issues.

<Note>
  Azure's logging services are configured within your Azure subscription. Enabling logging does not provide Microsoft or Anthropic access to your content beyond what's necessary for billing and service operation.
</Note>


## Troubleshooting

Source: https://platform.claude.com/llms-full.txt#troubleshooting-3

### Authentication errors

**Error:** `401 Unauthorized` or `Invalid API key`

* **Solution:** Verify your API key is correct. You can find it in the Foundry portal on your deployment's **Details** tab (under **Build** > **Models**).
* **Solution:** If using Microsoft Entra ID, ensure your access token is valid and hasn't expired. Tokens typically expire after 1 hour.

**Error:** `403 Forbidden`

* **Solution:** Your Azure account may lack the necessary permissions. Ensure you have the appropriate Azure RBAC role assigned (for example, **Foundry User** (formerly Azure AI User) or **Cognitive Services User**).

### Rate limiting

**Error:** `429 Too Many Requests`

* **Solution:** You've exceeded your rate limit. Implement exponential backoff and retry logic in your application.
* **Solution:** Consider requesting rate limit increases through the Azure portal or Azure support.

#### Rate limit headers

Foundry does not include Anthropic's standard rate limit headers (`anthropic-ratelimit-tokens-limit`, `anthropic-ratelimit-tokens-remaining`, `anthropic-ratelimit-tokens-reset`, `anthropic-ratelimit-input-tokens-limit`, `anthropic-ratelimit-input-tokens-remaining`, `anthropic-ratelimit-input-tokens-reset`, `anthropic-ratelimit-output-tokens-limit`, `anthropic-ratelimit-output-tokens-remaining`, and `anthropic-ratelimit-output-tokens-reset`) in responses. Manage rate limiting through Azure's monitoring tools instead.

### Model and deployment errors

**Error:** `Model not found` or `Deployment not found`

* **Solution:** Verify you're using the correct deployment name. If you haven't created a custom deployment, use the default model ID (for example, claude-opus-5).
* **Solution:** Ensure the model/deployment is available in your Azure region.

**Error:** `Invalid model parameter`

* **Solution:** The model parameter should contain your deployment name, which can be customized in the Foundry portal. Verify the deployment exists and is properly configured.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-66

<CardGroup cols={2}>
  <Card title="Features overview" icon="stack" href="https://platform.claude.com/docs/en/build-with-claude/overview">
    Explore Claude's advanced features and capabilities.
  </Card>

  <Card title="Pricing" icon="chart" href="https://platform.claude.com/docs/en/about-claude/pricing#claude-in-microsoft-foundry-pricing">
    Learn about Anthropic's pricing structure for models and features.
  </Card>

  <Card title="Model deprecations" icon="arrow-clockwise" href="https://platform.claude.com/docs/en/about-claude/model-deprecations">
    As safer and more capable models launch, Anthropic regularly retires older ones. See all API deprecations, along with recommended replacements.
  </Card>
</CardGroup>


## Additional resources

Source: https://platform.claude.com/llms-full.txt#additional-resources

<CardGroup cols={2}>
  <Card title="Foundry model catalog" icon="grid" href="https://ai.azure.com/catalog/publishers/anthropic">
    Browse Anthropic models in the Foundry catalog.
  </Card>

  <Card title="Azure AI Foundry pricing" icon="calculator" href="https://azure.microsoft.com/en-us/pricing/details/ai-foundry/#pricing">
    View Microsoft's pricing details for Azure AI Foundry.
  </Card>

  <Card title="Model pricing" icon="table" href="https://platform.claude.com/docs/en/about-claude/pricing#model-pricing">
    View Anthropic's per-model pricing details.
  </Card>

  <Card title="Azure portal" icon="cloud" href="https://portal.azure.com/">
    Manage your Azure resources.
  </Card>
</CardGroup>


---
title: Claude on Amazon Bedrock (Opus 4.6 and earlier)
url: https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy
description: The legacy Amazon Bedrock integration for Claude models, using InvokeModel and Converse APIs with ARN-versioned model identifiers.
---

<Note>
  This page covers the legacy Amazon Bedrock integration: the `InvokeModel` and `Converse` APIs with ARN-versioned model identifiers and AWS event-stream encoding. For models available on the Messages-API Bedrock endpoint, see [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), which uses the Messages API at `/anthropic/v1/messages` with SSE streaming. For an Anthropic-operated alternative with AWS Marketplace billing and typically same-day feature access, see [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws). Existing Bedrock users can follow the [migration guide](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#migrating-from-amazon-bedrock).
</Note>

Calling Claude through Bedrock slightly differs from how you would call Claude on the Claude API directly. This guide walks you through completing an API call to Claude on Bedrock using one of Anthropic's [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview).

Note that this guide assumes you have already signed up for an [AWS account](https://portal.aws.amazon.com/billing/signup) and configured programmatic access.


## Install and configure the AWS CLI

Source: https://platform.claude.com/llms-full.txt#install-and-configure-the-aws-cli

1. [Install a version of the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) at or newer than version `2.13.23`.
2. Configure your AWS credentials using the AWS configure command (see [Configure the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)) or find your credentials by navigating to "Command line or programmatic access" within your AWS dashboard and following the directions in the modal window.
3. Verify that your credentials are working:

```bash AWS CLI
aws sts get-caller-identity
```


## Install an SDK for accessing Bedrock

Source: https://platform.claude.com/llms-full.txt#install-an-sdk-for-accessing-bedrock

Anthropic's [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) support Bedrock. You can also use an AWS SDK like `boto3` directly.

<Tabs>
  <Tab title="Python">

</Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="C#">

</Tab>

  <Tab title="Go">

</Tab>

  <Tab title="Java">
    <CodeGroup>
      ```groovy Gradle
      implementation("com.anthropic:anthropic-java-bedrock:2.60.0")

xml Maven
      <dependency>
          <groupId>com.anthropic</groupId>
          <artifactId>anthropic-java-bedrock</artifactId>
          <version>2.60.0</version>
      </dependency>

java Java
      import com.anthropic.client.AnthropicClient;
      import com.anthropic.client.okhttp.AnthropicOkHttpClient;
      import com.anthropic.bedrock.backends.BedrockBackend;
      import com.anthropic.models.messages.MessageCreateParams;
      import com.anthropic.models.messages.Message;
      import com.anthropic.models.messages.Model;

      public class BasicMessage {
          public static void main(String[] args) {
              AnthropicClient client = AnthropicOkHttpClient.builder()
                  .backend(BedrockBackend.fromEnv())
                  .build();

              MessageCreateParams params = MessageCreateParams.builder()
                  .model(Model.CLAUDE_OPUS_4_6)
                  .maxTokens(1024L)
                  .addUserMessage("What is the capital of France?")
                  .build();

              Message response = client.messages().create(params);
              response.content().stream()
                  .flatMap(block -> block.text().stream())
                  .forEach(textBlock -> System.out.println(textBlock.text()));
          }
      }

bash
    composer require anthropic-ai/sdk aws/aws-sdk-php

bash
    # Gemfile
    gem "anthropic"
    gem "aws-sdk-bedrockruntime"

bash
    pip install "boto3>=1.28.59"
    ```
  </Tab>
</Tabs>


## Accessing Bedrock

Source: https://platform.claude.com/llms-full.txt#accessing-bedrock

### Subscribe to Anthropic models

Go to the [AWS Console > Bedrock > Model Access](https://console.aws.amazon.com/bedrock/home?region=us-west-2#/modelaccess) and request access to Anthropic models. Note that Anthropic model availability varies by region. See [AWS documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) for latest information.

#### API model IDs

<Note>
  Claude Fable 5.1, Claude Fable 5, Claude Opus 5, Claude Sonnet 5, Claude Opus 4.8, and Claude Opus 4.7 are reachable through `InvokeModel` on `bedrock-runtime`. These requests are served by the same infrastructure as the [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) endpoint. For the native Messages API request shape and full feature parity, use that page. These models are omitted from the model table on this page because they do not have ARN-versioned model IDs.
</Note>

Lifecycle terms (Deprecated, Retired) are defined in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations). Lifecycle dates on partner-operated platforms are set by the partner and can differ from the Claude API schedule. For the current retirement date of any model on Amazon Bedrock, see [Amazon Bedrock's model lifecycle page](https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html).

AWS offers newer Claude models through [cross-region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) rather than on-demand throughput. For these models, a request that passes the base model ID fails with an HTTP 400 error like the following:

```text wrap
Invocation of model ID anthropic.claude-sonnet-4-5-20250929-v1:0 with on-demand throughput isn't supported. Retry your request with the ID or ARN of an inference profile that contains this model.

bash AWS CLI
  aws bedrock list-foundation-models --region=us-west-2 --by-provider anthropic --query "modelSummaries[*].modelId"

python Boto3 (Python)
  import boto3

  bedrock = boto3.client(service_name="bedrock")
  response = bedrock.list_foundation_models(byProvider="anthropic")

  for summary in response["modelSummaries"]:
      print(summary["modelId"])

typescript TypeScript
  import { BedrockClient, ListFoundationModelsCommand } from "@aws-sdk/client-bedrock";

  const client = new BedrockClient({ region: "us-west-2" });

  const command = new ListFoundationModelsCommand({ byProvider: "anthropic" });
  const response = await client.send(command);

  if (response.modelSummaries) {
    for (const summary of response.modelSummaries) {
      console.log(summary.modelId);
    }
  }

csharp C#
  using Amazon;
  using Amazon.Bedrock;
  using Amazon.Bedrock.Model;

  var client = new AmazonBedrockClient(RegionEndpoint.USWest2);

  var request = new ListFoundationModelsRequest
  {
      ByProvider = "anthropic"
  };

  var response = await client.ListFoundationModelsAsync(request);

  foreach (var summary in response.ModelSummaries)
  {
      Console.WriteLine(summary.ModelId);
  }

go Go
  import (
  	"context"
  	"fmt"
  	"log"

  	"github.com/aws/aws-sdk-go-v2/config"
  	"github.com/aws/aws-sdk-go-v2/service/bedrock"
  )
  // ...
  	cfg, err := config.LoadDefaultConfig(context.TODO(), config.WithRegion("us-west-2"))
  	if err != nil {
  		log.Fatal(err)
  	}

  	client := bedrock.NewFromConfig(cfg)

  	byProvider := "anthropic"
  	response, err := client.ListFoundationModels(context.TODO(), &bedrock.ListFoundationModelsInput{
  		ByProvider: &byProvider,
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	for _, summary := range response.ModelSummaries {
  		fmt.Println(*summary.ModelId)
  	}

java Java
  import software.amazon.awssdk.regions.Region;
  import software.amazon.awssdk.services.bedrock.BedrockClient;
  import software.amazon.awssdk.services.bedrock.model.ListFoundationModelsRequest;
  import software.amazon.awssdk.services.bedrock.model.ListFoundationModelsResponse;
  import software.amazon.awssdk.services.bedrock.model.FoundationModelSummary;

  public class ListAnthropicModels {
      public static void main(String[] args) {
          BedrockClient client = BedrockClient.builder()
              .region(Region.US_WEST_2)
              .build();

          ListFoundationModelsRequest request = ListFoundationModelsRequest.builder()
              .byProvider("anthropic")
              .build();

          ListFoundationModelsResponse response = client.listFoundationModels(request);

          for (FoundationModelSummary summary : response.modelSummaries()) {
              System.out.println(summary.modelId());
          }

          client.close();
      }
  }

php PHP
  <?php

  use Aws\Bedrock\BedrockClient;

  $client = new BedrockClient([
      'region' => 'us-west-2',
      'version' => 'latest'
  ]);

  $result = $client->listFoundationModels([
      'byProvider' => 'anthropic'
  ]);

  foreach ($result['modelSummaries'] as $summary) {
      echo $summary['modelId'] . PHP_EOL;
  }

ruby Ruby
  require "aws-sdk-bedrock"

  client = Aws::Bedrock::Client.new(region: "us-west-2")

  response = client.list_foundation_models({
    by_provider: "anthropic"
  })

  response.model_summaries.each do |summary|
    puts summary.model_id
  end

python
    from anthropic import AnthropicBedrock

    client = AnthropicBedrock(
        # Authenticate by either providing the keys below or use the default AWS credential providers, such as
        # using ~/.aws/credentials or the "AWS_SECRET_ACCESS_KEY" and "AWS_ACCESS_KEY_ID" environment variables.
        aws_access_key="<access key>",
        aws_secret_key="<secret key>",
        # Temporary credentials can be used with aws_session_token.
        # Read more at https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html.
        aws_session_token="<session_token>",
        # aws_region changes the aws region to which the request is made. If it is not provided, the SDK reads
        # AWS_REGION / AWS_DEFAULT_REGION, then the region configured for your boto3 session or AWS profile
        # (including ~/.aws/config), and raises ValueError if no region can be resolved.
        aws_region="us-west-2",
    )

    message = client.messages.create(
        model="global.anthropic.claude-opus-4-6-v1",
        max_tokens=256,
        messages=[{"role": "user", "content": "Hello, world"}],
    )
    print(message.content)

typescript
    import AnthropicBedrock from "@anthropic-ai/bedrock-sdk";

    const client = new AnthropicBedrock({
      // Authenticate by either providing the keys below or use
      // the default AWS credential providers, such as
      // ~/.aws/credentials or the "AWS_SECRET_ACCESS_KEY" and
      // "AWS_ACCESS_KEY_ID" environment variables.
      awsAccessKey: "<access key>",
      awsSecretKey: "<secret key>",

      // Temporary credentials can be used with awsSessionToken.
      // Read more at https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html.
      awsSessionToken: "<session_token>",

      // awsRegion changes the aws region to which the request
      // is made. By default, the SDK reads AWS_REGION, and if
      // that's not present, defaults to us-east-1. Note that
      // the SDK does not read ~/.aws/config for the region.
      awsRegion: "us-west-2"
    });

    const message = await client.messages.create({
      model: "global.anthropic.claude-opus-4-6-v1",
      max_tokens: 256,
      messages: [{ role: "user", content: "Hello, world" }]
    });
    console.log(message);

csharp
    using Anthropic.Bedrock;
    using Anthropic.Models.Messages;

    AnthropicBedrockClient client = new(
        await AnthropicBedrockCredentialsHelper.FromEnv()
        ?? throw new InvalidOperationException("AWS credentials not configured.")
    );

    var response = await client.Messages.Create(new MessageCreateParams
    {
        Model = "global.anthropic.claude-opus-4-6-v1",
        MaxTokens = 256,
        Messages = [new() { Role = Role.User, Content = "Hello, world" }],
    });

    Console.WriteLine(
        string.Join("", response.Content
            .Select(block => block.Value)
            .OfType<TextBlock>()
            .Select(textBlock => textBlock.Text)));

go
    import (
    	"context"
    	"fmt"

    	"github.com/anthropics/anthropic-sdk-go"
    	"github.com/anthropics/anthropic-sdk-go/bedrock"
    )
    // ...
    	// Uses default AWS credential provider chain
    	client := anthropic.NewClient(
    		bedrock.WithLoadDefaultConfig(context.Background()),
    	)

    	message, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
    		Model:     "global.anthropic.claude-opus-4-6-v1",
    		MaxTokens: 256,
    		Messages: []anthropic.MessageParam{
    			anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, world")),
    		},
    	})
    	if err != nil {
    		panic(err)
    	}
    	fmt.Println(message.Content)

java
    import com.anthropic.bedrock.backends.BedrockBackend;
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.models.messages.Message;
    import com.anthropic.models.messages.MessageCreateParams;

    public class BedrockExample {

      public static void main(String[] args) {
        // Uses default AWS credential provider chain
        AnthropicClient client = AnthropicOkHttpClient.builder()
          .backend(BedrockBackend.fromEnv())
          .build();

        Message message = client
          .messages()
          .create(
            MessageCreateParams.builder()
              .model("global.anthropic.claude-opus-4-6-v1")
              .maxTokens(256)
              .addUserMessage("Hello, world")
              .build()
          );

        System.out.println(message.content());
      }
    }

php
    <?php

    use Anthropic\Bedrock;

    $client = Bedrock\Client::withCredentials(
        accessKeyId: getenv("AWS_ACCESS_KEY_ID"),
        secretAccessKey: getenv("AWS_SECRET_ACCESS_KEY"),
        region: 'us-west-2',
        securityToken: getenv("AWS_SESSION_TOKEN"),
    );

    $message = $client->messages->create(
        maxTokens: 256,
        messages: [
            ['role' => 'user', 'content' => 'Hello, world']
        ],
        model: 'global.anthropic.claude-opus-4-6-v1',
    );
    echo $message->content[0]->text;

ruby
    require "anthropic"

    client = Anthropic::BedrockClient.new

    message = client.messages.create(
      model: "global.anthropic.claude-opus-4-6-v1",
      max_tokens: 256,
      messages: [{role: "user", content: "Hello, world"}]
    )

    puts message.content.first.text

python
    import boto3
    import json

    bedrock = boto3.client(service_name="bedrock-runtime")
    body = json.dumps(
        {
            "max_tokens": 256,
            "messages": [{"role": "user", "content": "Hello, world"}],
            "anthropic_version": "bedrock-2023-05-31",
        }
    )

    response = bedrock.invoke_model(
        body=body, modelId="global.anthropic.claude-opus-4-6-v1"
    )

    response_body = json.loads(response.get("body").read())
    print(response_body.get("content"))

python
    from anthropic import AnthropicBedrock

    client = AnthropicBedrock(
        api_key="your-bearer-token",
        aws_region="us-west-2",
    )

    message = client.messages.create(
        model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(message.content)

typescript
    import AnthropicBedrock from "@anthropic-ai/bedrock-sdk";

    const client = new AnthropicBedrock({
      apiKey: "your-bearer-token",
      awsRegion: "us-west-2"
    });

    const message = await client.messages.create({
      model: "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
      max_tokens: 1024,
      messages: [{ role: "user", content: "Hello!" }]
    });
    console.log(message);

csharp
    using Anthropic.Bedrock;
    using Anthropic.Models.Messages;

    var client = new AnthropicBedrockClient(
        new AnthropicBedrockApiTokenCredentials
        {
            BearerToken = "your-bearer-token",
            Region = "us-west-2",
        }
    );

    var response = await client.Messages.Create(new MessageCreateParams
    {
        Model = "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        MaxTokens = 1024,
        Messages = [new() { Role = Role.User, Content = "Hello!" }],
    });

go
    import (
    	"context"
    	"fmt"

    	"github.com/anthropics/anthropic-sdk-go"
    	"github.com/anthropics/anthropic-sdk-go/bedrock"
    	"github.com/aws/aws-sdk-go-v2/aws"
    )
    // ...
    	cfg := aws.Config{
    		Region:                  "us-west-2",
    		BearerAuthTokenProvider: bedrock.NewStaticBearerTokenProvider("your-bearer-token"),
    	}
    	client := anthropic.NewClient(
    		bedrock.WithConfig(cfg),
    	)

    	message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
    		Model:     "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    		MaxTokens: 1024,
    		Messages: []anthropic.MessageParam{
    			anthropic.NewUserMessage(anthropic.NewTextBlock("Hello!")),
    		},
    	})
    	if err != nil {
    		panic(err)
    	}
    	fmt.Println(message.Content[0].Text)

java
    import com.anthropic.bedrock.backends.BedrockBackend;
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.models.messages.MessageCreateParams;

    // Option 1: Set AWS_BEARER_TOKEN_BEDROCK environment variable and use fromEnv()
    AnthropicClient client = AnthropicOkHttpClient.builder()
      .backend(BedrockBackend.fromEnv())
      .build();

    // Option 2: Provide the token programmatically
    client = AnthropicOkHttpClient.builder()
      .backend(BedrockBackend.builder()
        .apiKey("your-bearer-token")
        .build())
      .build();

    MessageCreateParams params = MessageCreateParams.builder()
      .model("us.anthropic.claude-sonnet-4-5-20250929-v1:0")
      .maxTokens(1024)
      .addUserMessage("Hello!")
      .build();

    client.messages().create(params).content().stream()
      .flatMap(block -> block.text().stream())
      .forEach(textBlock -> System.out.println(textBlock.text()));

php
    <?php

    use Anthropic\Bedrock;

    $client = Bedrock\Client::withApiKey('your-bearer-token', 'us-west-2');

    $message = $client->messages->create(
        maxTokens: 1024,
        messages: [
            ['role' => 'user', 'content' => 'Hello!']
        ],
        model: 'us.anthropic.claude-sonnet-4-5-20250929-v1:0',
    );
    echo $message->content[0]->text;

ruby
    require "anthropic"

    client = Anthropic::BedrockClient.new(
      api_key: "your-bearer-token",
      aws_region: "us-west-2"
    )

    message = client.messages.create(
      model: "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
      max_tokens: 1024,
      messages: [{role: "user", content: "Hello!"}]
    )
    puts message.content.first.text
    ```
  </Tab>
</Tabs>


## Activity logging

Source: https://platform.claude.com/llms-full.txt#activity-logging

Bedrock provides an [invocation logging service](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) that allows you to log the prompts and completions associated with your usage.

Anthropic recommends that you log your activity on at least a 30-day rolling basis to understand your activity and investigate any potential misuse.

<Note>
  Turning on this service does not give AWS or Anthropic any access to your content.
</Note>


## Feature support

Source: https://platform.claude.com/llms-full.txt#feature-support-4

For the full feature list with Amazon Bedrock availability, see [Features overview](https://platform.claude.com/docs/en/build-with-claude/overview).

### Supported feature highlights

* [Messages API](https://platform.claude.com/docs/en/api/messages/create)
* [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
* [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)
* [Tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview), including the [Bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool), [Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool), [Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool), and [Text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)
* [Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
* [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)

### Features not supported

* Input sources (URL sources for images and documents, Files API)
* Server-side tools (code execution, web search, web fetch, advisor)
* Agent infrastructure (Agent Skills, MCP connector, programmatic tool calling)
* API endpoints (Message Batches, Models, Admin, Compliance, Usage and Cost)
* Claude Managed Agents
* Server-side fallback (the [`fallbacks` parameter](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#server-side-fallback); use the [client-side fallback pattern](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#client-side-fallback) instead)
* Automatic prompt caching (the [top-level `cache_control` field](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#automatic-caching); use [explicit cache breakpoints](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#explicit-cache-breakpoints) instead)
* [Computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) toolsets (`computer_toolset_20260801` and `browser_toolset_20260801` are not currently available on Amazon Bedrock; the beta computer use tool versions remain available)

### PDF support on Bedrock

PDF support is available on Bedrock through both the Converse API and InvokeModel API. For detailed information about PDF processing capabilities and limitations, see [Amazon Bedrock PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support#amazon-bedrock-pdf-support).

**Important considerations for Converse API users:**

* Visual PDF analysis (charts, images, layouts) requires citations to be enabled
* Without citations, only basic text extraction is available
* For full control without forced citations, use the InvokeModel API

### Mid-conversation system messages on Bedrock

[Mid-conversation system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages) are available through the InvokeModel API for Claude Fable 5.1, Claude Fable 5, Claude Opus 5, and Claude Opus 4.8. As described in the note under [API model IDs](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy#api-model-ids), these requests are served by the same infrastructure as the [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) endpoint. No beta header is required. This feature is not available on Claude Sonnet 5. Use the top-level `system` field instead. It is not available for the ARN-versioned models in the model table on this page.

**For Converse API users:** the Converse API accepts system instructions through its top-level [`system` parameter](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html). To add system instructions mid-conversation, use the InvokeModel API.

### Context window

Claude Fable 5.1, Claude Fable 5, Claude Opus 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, and Claude Sonnet 4.6 have a [1M-token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) on Amazon Bedrock. Other Claude models, including Sonnet 4.5 and Sonnet 4 (deprecated), have a 200k-token context window.

Bedrock limits request payloads to 20 MB. When sending large documents or many images, you may reach this limit before the token limit.


## Global versus regional endpoints

Source: https://platform.claude.com/llms-full.txt#global-versus-regional-endpoints

Starting with **Claude Sonnet 4.5 and all future models**, Bedrock offers two endpoint types:

* **Global endpoints:** Dynamic routing for maximum availability
* **Regional endpoints:** Guaranteed data routing through specific geographic regions

Regional endpoints include a 10% pricing premium over global endpoints.

<Note>
  This applies to Claude Sonnet 4.5 and future models only. Older models (Claude Sonnet 4 (deprecated) and earlier) maintain their existing pricing structures.
</Note>

### When to use each option

**Global endpoints (recommended):**

* Provide maximum availability and uptime
* Dynamically route requests to regions with available capacity
* No pricing premium
* Best for applications where data residency is flexible

**Regional endpoints (CRIS):**

* Route traffic through specific geographic regions
* Required for data residency and compliance requirements
* Available for US, EU, Japan, and Asia-Pacific
* 10% pricing premium reflects infrastructure costs for dedicated regional capacity

### Implementation

**Using global endpoints (default for Opus 4.6, Sonnet 4.6, and Sonnet 4.5):**

The model IDs for Claude Opus 4.6, Sonnet 4.6, and Sonnet 4.5 already include the `global.` prefix:

<Tabs>
  <Tab title="cURL">
    <Note>
      Calling the `InvokeModel` API with AWS credentials requires SigV4 request signing, which the SDKs in the other tabs handle automatically. For a Bedrock endpoint you can call with a self-contained cURL command, see [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock#making-your-first-request).
    </Note>
  </Tab>

  <Tab title="CLI">
    <Note>
      The `ant` CLI does not support Amazon Bedrock. Use one of the SDK examples instead.
    </Note>
  </Tab>

  <Tab title="Python">

</Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="C#">

</Tab>

  <Tab title="Go">

</Tab>

  <Tab title="Java">

</Tab>

  <Tab title="PHP">

</Tab>

  <Tab title="Ruby">

</Tab>
</Tabs>

**Using regional endpoints (CRIS):**

To use regional endpoints, replace the `global.` prefix with a regional prefix such as `us.`:

<Tabs>
  <Tab title="cURL">
    <Note>
      Calling the `InvokeModel` API with AWS credentials requires SigV4 request signing, which the SDKs in the other tabs handle automatically. For a Bedrock endpoint you can call with a self-contained cURL command, see [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock#making-your-first-request).
    </Note>
  </Tab>

  <Tab title="CLI">
    <Note>
      The `ant` CLI does not support Amazon Bedrock. Use one of the SDK examples instead.
    </Note>
  </Tab>

  <Tab title="Python">

</Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="C#">

</Tab>

  <Tab title="Go">

</Tab>

  <Tab title="Java">

</Tab>

  <Tab title="PHP">

</Tab>

  <Tab title="Ruby">

</Tab>
</Tabs>

<Note>
  **Claude Mythos Preview** is a research preview model available to invited customers on Amazon Bedrock. For more information, see [Project Glasswing](https://anthropic.com/glasswing).
</Note>


## Additional resources

Source: https://platform.claude.com/llms-full.txt#additional-resources-2

* **Bedrock pricing:** [Amazon Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/)
* **AWS pricing documentation:** [Bedrock pricing guide](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-pricing.html)
* **AWS blog post:** [Introducing Claude Sonnet 4.5 in Amazon Bedrock](https://aws.amazon.com/blogs/aws/introducing-claude-sonnet-4-5-in-amazon-bedrock-anthropics-most-intelligent-model-best-for-coding-and-complex-agents/)
* **Anthropic pricing details:** [Cloud platform pricing](https://platform.claude.com/docs/en/about-claude/pricing#cloud-platform-pricing)


---
title: Claude on Google Cloud
url: https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai
description: Anthropic's Claude models are available through [Google Cloud's Agent Platform](https://cloud.google.com/vertex-ai).
---

The API for accessing Claude on Google Cloud's Agent Platform is nearly identical to the [Messages API](https://platform.claude.com/docs/en/api/messages/create), with two key differences in request format:

* On Agent Platform, `model` is not passed in the request body. Instead, it is specified in the Google Cloud endpoint URL.
* On Agent Platform, `anthropic_version` is passed in the request body (rather than as a header), and must be set to the value `vertex-2023-10-16`.

Agent Platform is also supported by Anthropic's official [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview). This guide walks you through making a request to Claude on Agent Platform using one of Anthropic's client SDKs.

Note that this guide assumes you already have a Google Cloud project that is able to use Agent Platform. See [Anthropic Claude models on Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude) for more information on the setup required and a full walkthrough.


## Install an SDK for accessing Agent Platform

Source: https://platform.claude.com/llms-full.txt#install-an-sdk-for-accessing-agent-platform

First, install Anthropic's [client SDK](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) for your language of choice.

<Tabs>
  <Tab title="Python">

</Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="C#">

</Tab>

  <Tab title="Go">

</Tab>

  <Tab title="Java">
    <CodeGroup exclude="shell, python, typescript, csharp, go, php, ruby">
      ```groovy Gradle
      implementation("com.anthropic:anthropic-java:2.60.0")
      implementation("com.anthropic:anthropic-java-vertex:2.60.0")

xml Maven
      <dependency>
          <groupId>com.anthropic</groupId>
          <artifactId>anthropic-java</artifactId>
          <version>2.60.0</version>
      </dependency>
      <dependency>
          <groupId>com.anthropic</groupId>
          <artifactId>anthropic-java-vertex</artifactId>
          <version>2.60.0</version>
      </dependency>

java Java
      import com.anthropic.client.AnthropicClient;
      import com.anthropic.client.okhttp.AnthropicOkHttpClient;
      import com.anthropic.models.messages.Message;
      import com.anthropic.models.messages.MessageCreateParams;
      import com.anthropic.models.messages.Model;
      import com.anthropic.vertex.backends.VertexBackend;

      void main() {
          AnthropicClient client = AnthropicOkHttpClient.builder()
              .backend(VertexBackend.fromEnv())
              .build();

          MessageCreateParams params = MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024L)
              .addUserMessage("What is the capital of France?")
              .build();

          Message response = client.messages().create(params);
          response.content().stream()
              .flatMap(block -> block.text().stream())
              .forEach(textBlock -> IO.println(textBlock.text()));
      }

bash
    composer require anthropic-ai/sdk google/auth

bash
    # Gemfile
    gem "anthropic"
    gem "googleauth"
    ```
  </Tab>
</Tabs>


## Accessing Agent Platform

Source: https://platform.claude.com/llms-full.txt#accessing-agent-platform

### Model availability

Note that Anthropic model availability varies by region. Search for "Claude" in the [Model Garden](https://cloud.google.com/model-garden) or go to [Anthropic Claude models](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude) for the latest information.

#### API model IDs

Lifecycle terms (Deprecated, Retired) are defined in [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations). Lifecycle dates on partner-operated platforms are set by the partner and can differ from the Claude API schedule. For the current retirement date of any model on Agent Platform, see [Google Cloud's documentation for Claude models on Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude).

| Model                        | Agent Platform API model ID |
| ---------------------------- | --------------------------- |
| Claude Fable 5.1             | claude-fable-5-1            |
| Claude Fable 5               | claude-fable-5              |
| Claude Opus 5                | claude-opus-5               |
| Claude Opus 4.8              | claude-opus-4-8             |
| Claude Opus 4.7              | claude-opus-4-7             |
| Claude Opus 4.6              | claude-opus-4-6             |
| Claude Sonnet 5              | `claude-sonnet-5`           |
| Claude Sonnet 4.6            | claude-sonnet-4-6           |
| Claude Sonnet 4.5            | claude-sonnet-4-5\@20250929 |
| Claude Sonnet 4 Deprecated.  | claude-sonnet-4\@20250514   |
| Claude Sonnet 3.7 Retired.   | claude-3-7-sonnet\@20250219 |
| Claude Opus 4.5              | claude-opus-4-5\@20251101   |
| Claude Opus 4.1 Deprecated.  | claude-opus-4-1\@20250805   |
| Claude Opus 4 Deprecated.    | claude-opus-4\@20250514     |
| Claude Haiku 4.5             | claude-haiku-4-5\@20251001  |
| Claude Haiku 3.5 Deprecated. | claude-3-5-haiku\@20241022  |

<Tip>
  Upgrading to a newer Claude model? In Claude Code, run `/claude-api migrate` to apply model ID swaps and breaking parameter changes across your codebase. The skill detects which cloud platform your code targets and adjusts model ID formats and feature changes for that platform. See [Migrating to a newer Claude model](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill#migrating-to-a-newer-claude-model).
</Tip>

### Making requests

Before running requests you might need to run `gcloud auth application-default login` to authenticate with Google Cloud.

The following examples show how to generate text from Claude on Agent Platform:

<CodeGroup>
  ```bash cURL
  MODEL_ID=claude-opus-5
  PROJECT_ID=MY_PROJECT_ID

  curl https://aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/global/publishers/anthropic/models/${MODEL_ID}:rawPredict \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    -d '{
      "anthropic_version": "vertex-2023-10-16",
      "messages": [{"role": "user", "content": "Hey Claude!"}],
      "max_tokens": 100
    }'

bash CLI
  # The ant CLI does not support Agent Platform.

python Python
  from anthropic import AnthropicVertex

  project_id = "MY_PROJECT_ID"
  region = "global"

  client = AnthropicVertex(project_id=project_id, region=region)

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=100,
      messages=[
          {
              "role": "user",
              "content": "Hey Claude!",
          }
      ],
  )
  print(message)

typescript TypeScript
  import { AnthropicVertex } from "@anthropic-ai/vertex-sdk";

  const projectId = "MY_PROJECT_ID";
  const region = "global";

  // Goes through the standard `google-auth-library` flow.
  const client = new AnthropicVertex({
    projectId,
    region
  });

  const result = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 100,
    messages: [
      {
        role: "user",
        content: "Hey Claude!"
      }
    ]
  });
  console.log(JSON.stringify(result, null, 2));

csharp C#
  using Anthropic.Models.Messages;
  using Anthropic.Vertex;

  var projectId = "MY_PROJECT_ID";
  var region = "global";

  var client = new AnthropicVertexClient(new AnthropicVertexCredentials(region, projectId));

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 100,
      Messages = [new() { Role = Role.User, Content = "Hey Claude!" }]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  import (
  	"context"
  	"fmt"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/vertex"
  )
  // ...
  	// Uses default Google Cloud credentials
  	client := anthropic.NewClient(
  		vertex.WithGoogleAuth(context.Background(), "global", "MY_PROJECT_ID"),
  	)

  	message, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 100,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hey Claude!")),
  		},
  	})
  	if err != nil {
  		panic(err)
  	}
  	fmt.Printf("%+v\n", message)

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;
  import com.anthropic.vertex.backends.VertexBackend;

  void main() {
      // Uses default Google Cloud credentials
      AnthropicClient client = AnthropicOkHttpClient.builder()
          .backend(VertexBackend.fromEnv())
          .build();

      Message message = client
          .messages()
          .create(
              MessageCreateParams.builder()
                  .model(Model.CLAUDE_OPUS_5)
                  .maxTokens(100)
                  .addUserMessage("Hey Claude!")
                  .build()
          );

      IO.println(message);
  }

php PHP
  <?php

  use Anthropic\Vertex;

  $client = Vertex\Client::fromEnvironment(
      location: 'global',
      projectId: 'MY_PROJECT_ID',
  );

  $message = $client->messages->create(
      maxTokens: 100,
      messages: [
          ['role' => 'user', 'content' => 'Hey Claude!']
      ],
      model: 'claude-opus-5',
  );
  $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
  echo $textBlock->text;

ruby Ruby
  require "anthropic"

  client = Anthropic::VertexClient.new(
    region: "global",
    project_id: "MY_PROJECT_ID"
  )

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 100,
    messages: [{role: "user", content: "Hey Claude!"}]
  )

  puts message.content.find { it.type == :text }.text
  ```
</CodeGroup>

See the [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) and the official [Agent Platform docs](https://cloud.google.com/vertex-ai/docs) for more details.

Claude is also available through [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), and [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry).


## Data retention

Source: https://platform.claude.com/llms-full.txt#data-retention-13

Data handling for this offering is governed by Google Cloud. For details, see [Agent Platform and zero data retention](https://cloud.google.com/vertex-ai/generative-ai/docs/data-governance).


## Activity logging

Source: https://platform.claude.com/llms-full.txt#activity-logging-2

Agent Platform provides a [request-response logging service](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/request-response-logging) that allows you to log the prompts and completions associated with your usage.

Anthropic recommends that you log your activity on at least a 30-day rolling basis to understand your activity and investigate any potential misuse.

<Note>
  Turning on this service does not give Google or Anthropic any access to your content.
</Note>


## Feature support

Source: https://platform.claude.com/llms-full.txt#feature-support-5

For the full feature list with Google Cloud availability, see [Features overview](https://platform.claude.com/docs/en/build-with-claude/overview).

### Supported feature highlights

* [Messages API](https://platform.claude.com/docs/en/api/messages/create)
* [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
* [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)
* [Tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview), including the [Bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool), [Browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool), [Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool), [Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool), and [Text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)
* [Web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)
* [Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
* [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)

### Features not supported

* Input sources (URL sources for images and documents, Files API)
* Server-side tools (code execution, web fetch, advisor)
* Agent infrastructure (Agent Skills, MCP connector, programmatic tool calling)
* API endpoints (Message Batches, Models, Admin, Compliance, Usage and Cost)
* Claude Managed Agents
* Server-side fallback (the [`fallbacks` parameter](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#server-side-fallback); use the [client-side fallback pattern](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#client-side-fallback) instead)

### Context window

Claude Fable 5.1, Claude Fable 5, Claude Opus 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, and Claude Sonnet 4.6 have a [1M-token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) on Agent Platform. Other Claude models, including Sonnet 4.5 and Sonnet 4 (deprecated), have a 200k-token context window.

Agent Platform limits request payloads to 30 MB. When sending large documents or many images, you might reach this limit before the token limit.


## Global, multi-region, and regional endpoints

Source: https://platform.claude.com/llms-full.txt#global-multi-region-and-regional-endpoints

Agent Platform offers three endpoint types:

* **Global endpoints:** Dynamic routing for maximum availability
* **Multi-region endpoints:** Dynamic routing within a geographic area (for example, the United States or the European Union) for data residency with high availability
* **Regional endpoints:** Guaranteed data routing through specific geographic regions

Regional and multi-region endpoints include a 10% pricing premium over global endpoints.

<Note>
  This applies to Claude Sonnet 4.5 and future models only. Older models (Claude Sonnet 4 (deprecated), Opus 4 (deprecated), and earlier) maintain their existing pricing structures.
</Note>

### When to use each option

**Global endpoints (recommended):**

* Provide maximum availability and uptime
* Dynamically route requests to regions with available capacity
* No pricing premium
* Best for applications where data residency is flexible
* Only supports pay-as-you-go traffic (provisioned throughput requires regional endpoints)

**Multi-region endpoints:**

* Dynamically route requests across regions within a geographic area (currently `us` and `eu`)
* Useful when you need data residency within a broad geography but want higher availability than a single region
* 10% pricing premium over global endpoints
* Only supports pay-as-you-go traffic (provisioned throughput requires regional endpoints)

**Regional endpoints:**

* Route traffic through specific geographic regions
* Required for single-region data residency, strict compliance mandates, or provisioned throughput
* Support both pay-as-you-go and provisioned throughput
* 10% pricing premium reflects infrastructure costs for dedicated regional capacity

### Implementation

**Using global endpoints (recommended):**

Set the `region` parameter to `"global"` when initializing the client:

<CodeGroup>
  ```bash cURL
  MODEL_ID=claude-opus-5
  PROJECT_ID=MY_PROJECT_ID

  curl https://aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/global/publishers/anthropic/models/${MODEL_ID}:rawPredict \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    -d '{
      "anthropic_version": "vertex-2023-10-16",
      "messages": [{"role": "user", "content": "Hey Claude!"}],
      "max_tokens": 100
    }'

bash CLI
  # The ant CLI does not support Agent Platform.

python Python
  from anthropic import AnthropicVertex

  project_id = "MY_PROJECT_ID"
  region = "global"

  client = AnthropicVertex(project_id=project_id, region=region)

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=100,
      messages=[
          {
              "role": "user",
              "content": "Hey Claude!",
          }
      ],
  )
  print(message)

typescript TypeScript
  import { AnthropicVertex } from "@anthropic-ai/vertex-sdk";

  const projectId = "MY_PROJECT_ID";
  const region = "global";

  const client = new AnthropicVertex({
    projectId,
    region
  });

  const result = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 100,
    messages: [
      {
        role: "user",
        content: "Hey Claude!"
      }
    ]
  });
  console.log(JSON.stringify(result, null, 2));

csharp C#
  using Anthropic.Models.Messages;
  using Anthropic.Vertex;

  var projectId = "MY_PROJECT_ID";
  var region = "global";

  var client = new AnthropicVertexClient(new AnthropicVertexCredentials(region, projectId));

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 100,
      Messages = [new() { Role = Role.User, Content = "Hey Claude!" }]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  import (
  	"context"
  	"fmt"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/vertex"
  )
  // ...
  	// Uses default Google Cloud credentials
  	client := anthropic.NewClient(
  		vertex.WithGoogleAuth(context.Background(), "global", "MY_PROJECT_ID"),
  	)

  	message, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 100,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hey Claude!")),
  		},
  	})
  	if err != nil {
  		panic(err)
  	}
  	fmt.Printf("%+v\n", message)

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;
  import com.anthropic.vertex.backends.VertexBackend;
  import com.google.auth.oauth2.GoogleCredentials;

  void main() throws Exception {
      // Uses default Google Cloud credentials
      AnthropicClient client = AnthropicOkHttpClient.builder()
          .backend(
              VertexBackend.builder()
                  .googleCredentials(GoogleCredentials.getApplicationDefault())
                  .region("global")
                  .project("MY_PROJECT_ID")
                  .build()
          )
          .build();

      var message = client
          .messages()
          .create(
              MessageCreateParams.builder()
                  .model(Model.CLAUDE_OPUS_5)
                  .maxTokens(100)
                  .addUserMessage("Hey Claude!")
                  .build()
          );

      IO.println(message);
  }

php PHP
  <?php

  use Anthropic\Vertex;

  $client = Vertex\Client::fromEnvironment(
      location: 'global',
      projectId: 'MY_PROJECT_ID',
  );

  $message = $client->messages->create(
      maxTokens: 100,
      messages: [
          ['role' => 'user', 'content' => 'Hey Claude!']
      ],
      model: 'claude-opus-5',
  );

  $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
  echo $textBlock->text;

ruby Ruby
  require "anthropic"

  client = Anthropic::VertexClient.new(
    region: "global",
    project_id: "MY_PROJECT_ID"
  )

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 100,
    messages: [{role: "user", content: "Hey Claude!"}]
  )

  puts message.content.find { it.type == :text }.text

bash cURL
  MODEL_ID=claude-opus-5
  LOCATION=us # Multi-region identifier: "us" or "eu"
  PROJECT_ID=MY_PROJECT_ID

  curl https://aiplatform.${LOCATION}.rep.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/anthropic/models/${MODEL_ID}:rawPredict \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    -d '{
      "anthropic_version": "vertex-2023-10-16",
      "messages": [{"role": "user", "content": "Hey Claude!"}],
      "max_tokens": 100
    }'

bash CLI
  # The ant CLI does not support Agent Platform.

python Python
  from anthropic import AnthropicVertex

  project_id = "MY_PROJECT_ID"
  region = "us"  # Multi-region identifier: "us" or "eu"

  client = AnthropicVertex(project_id=project_id, region=region)

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=100,
      messages=[
          {
              "role": "user",
              "content": "Hey Claude!",
          }
      ],
  )
  print(message)

typescript TypeScript
  import { AnthropicVertex } from "@anthropic-ai/vertex-sdk";

  const projectId = "MY_PROJECT_ID";
  const region = "us"; // Multi-region identifier: "us" or "eu"

  const client = new AnthropicVertex({
    projectId,
    region
  });

  const result = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 100,
    messages: [
      {
        role: "user",
        content: "Hey Claude!"
      }
    ]
  });
  console.log(JSON.stringify(result, null, 2));

csharp C#
  using Anthropic.Models.Messages;
  using Anthropic.Vertex;

  var projectId = "MY_PROJECT_ID";
  var region = "us"; // Multi-region identifier: "us" or "eu"

  var client = new AnthropicVertexClient(new AnthropicVertexCredentials(region, projectId));

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 100,
      Messages = [new() { Role = Role.User, Content = "Hey Claude!" }]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  import (
  	"context"
  	"fmt"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/vertex"
  )
  // ...
  	// Multi-region identifier: "us" or "eu"
  	client := anthropic.NewClient(
  		vertex.WithGoogleAuth(context.Background(), "us", "MY_PROJECT_ID"),
  	)

  	message, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 100,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hey Claude!")),
  		},
  	})
  	if err != nil {
  		panic(err)
  	}
  	fmt.Printf("%+v\n", message)

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;
  import com.anthropic.vertex.backends.VertexBackend;
  import com.google.auth.oauth2.GoogleCredentials;

  void main() throws Exception {
      // Multi-region identifier: "us" or "eu"
      AnthropicClient client = AnthropicOkHttpClient.builder()
          .backend(
              VertexBackend.builder()
                  .googleCredentials(GoogleCredentials.getApplicationDefault())
                  .region("us")
                  .project("MY_PROJECT_ID")
                  .build()
          )
          .build();

      var message = client
          .messages()
          .create(
              MessageCreateParams.builder()
                  .model(Model.CLAUDE_OPUS_5)
                  .maxTokens(100)
                  .addUserMessage("Hey Claude!")
                  .build()
          );

      IO.println(message);
  }

php PHP
  <?php

  use Anthropic\Vertex;

  $client = Vertex\Client::fromEnvironment(
      location: 'us', // Multi-region identifier: "us" or "eu"
      projectId: 'MY_PROJECT_ID',
  );

  $message = $client->messages->create(
      maxTokens: 100,
      messages: [
          ['role' => 'user', 'content' => 'Hey Claude!']
      ],
      model: 'claude-opus-5',
  );
  $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
  echo $textBlock->text;

ruby Ruby
  require "anthropic"

  client = Anthropic::VertexClient.new(
    region: "us", # Multi-region identifier: "us" or "eu"
    project_id: "MY_PROJECT_ID"
  )

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 100,
    messages: [{role: "user", content: "Hey Claude!"}]
  )

  puts message.content.find { it.type == :text }.text

bash cURL
  # Specific regional endpoints support Claude Sonnet 4.6 and earlier; newer models use the global or multi-region endpoints
  MODEL_ID=claude-sonnet-4-6
  LOCATION=us-east5 # Specify a specific region
  PROJECT_ID=MY_PROJECT_ID

  curl https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/anthropic/models/${MODEL_ID}:rawPredict \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    -d '{
      "anthropic_version": "vertex-2023-10-16",
      "messages": [{"role": "user", "content": "Hey Claude!"}],
      "max_tokens": 100
    }'

bash CLI
  # The ant CLI does not support Agent Platform.

python Python
  from anthropic import AnthropicVertex

  project_id = "MY_PROJECT_ID"
  region = "us-east5"  # Specify a specific region

  client = AnthropicVertex(project_id=project_id, region=region)

  message = client.messages.create(
      # Specific regional endpoints support Claude Sonnet 4.6 and earlier; newer models use the global or multi-region endpoints
      model="claude-sonnet-4-6",
      max_tokens=100,
      messages=[
          {
              "role": "user",
              "content": "Hey Claude!",
          }
      ],
  )
  print(message)

typescript TypeScript
  import { AnthropicVertex } from "@anthropic-ai/vertex-sdk";

  const projectId = "MY_PROJECT_ID";
  const region = "us-east5"; // Specify a specific region

  const client = new AnthropicVertex({
    projectId,
    region
  });

  const result = await client.messages.create({
    // Specific regional endpoints support Claude Sonnet 4.6 and earlier; newer models use the global or multi-region endpoints
    model: "claude-sonnet-4-6",
    max_tokens: 100,
    messages: [
      {
        role: "user",
        content: "Hey Claude!"
      }
    ]
  });
  console.log(JSON.stringify(result, null, 2));

csharp C#
  using Anthropic.Models.Messages;
  using Anthropic.Vertex;

  var projectId = "MY_PROJECT_ID";
  var region = "us-east5"; // Specify a specific region

  var client = new AnthropicVertexClient(new AnthropicVertexCredentials(region, projectId));

  var parameters = new MessageCreateParams
  {
      // Specific regional endpoints support Claude Sonnet 4.6 and earlier; newer models use the global or multi-region endpoints
      Model = Model.ClaudeSonnet4_6,
      MaxTokens = 100,
      Messages = [new() { Role = Role.User, Content = "Hey Claude!" }]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  import (
  	"context"
  	"fmt"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/vertex"
  )
  // ...
  	// Specify a specific region
  	client := anthropic.NewClient(
  		vertex.WithGoogleAuth(context.Background(), "us-east5", "MY_PROJECT_ID"),
  	)

  	message, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  		// Specific regional endpoints support Claude Sonnet 4.6 and earlier; newer models use the global or multi-region endpoints
  		Model:     anthropic.ModelClaudeSonnet4_6,
  		MaxTokens: 100,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hey Claude!")),
  		},
  	})
  	if err != nil {
  		panic(err)
  	}
  	fmt.Printf("%+v\n", message)

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;
  import com.anthropic.vertex.backends.VertexBackend;
  import com.google.auth.oauth2.GoogleCredentials;

  void main() throws Exception {
      // Uses default Google Cloud credentials with specific region
      AnthropicClient client = AnthropicOkHttpClient.builder()
          .backend(
              VertexBackend.builder()
                  .googleCredentials(GoogleCredentials.getApplicationDefault())
                  .region("us-east5") // Specify a specific region
                  .project("MY_PROJECT_ID")
                  .build()
          )
          .build();

      var message = client
          .messages()
          .create(
              MessageCreateParams.builder()
                  // Specific regional endpoints support Claude Sonnet 4.6 and earlier; newer models use the global or multi-region endpoints
                  .model(Model.CLAUDE_SONNET_4_6)
                  .maxTokens(100)
                  .addUserMessage("Hey Claude!")
                  .build()
          );

      IO.println(message);
  }

php PHP
  <?php

  use Anthropic\Vertex;

  $client = Vertex\Client::fromEnvironment(
      location: 'us-east5',
      projectId: 'MY_PROJECT_ID',
  );

  $message = $client->messages->create(
      maxTokens: 100,
      messages: [
          ['role' => 'user', 'content' => 'Hey Claude!']
      ],
      // Specific regional endpoints support Claude Sonnet 4.6 and earlier; newer models use the global or multi-region endpoints
      model: 'claude-sonnet-4-6',
  );
  echo $message->content[0]->text;

ruby Ruby
  require "anthropic"

  client = Anthropic::VertexClient.new(
    region: "us-east5", # Specify a specific region
    project_id: "MY_PROJECT_ID"
  )

  message = client.messages.create(
    # Specific regional endpoints support Claude Sonnet 4.6 and earlier; newer models use the global or multi-region endpoints
    model: "claude-sonnet-4-6",
    max_tokens: 100,
    messages: [{role: "user", content: "Hey Claude!"}]
  )

  puts message.content.first.text
  ```
</CodeGroup>

<Note>
  Claude Mythos Preview is a research preview available to invited customers on Agent Platform. For more information, see [Project Glasswing](https://anthropic.com/glasswing).
</Note>


## Additional resources

Source: https://platform.claude.com/llms-full.txt#additional-resources-3

* **Agent Platform pricing:** [Generative AI pricing on cloud.google.com](https://cloud.google.com/vertex-ai/generative-ai/pricing)
* **Claude models documentation:** [Claude on Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude)
* **Google blog post:** [Global endpoint for Claude models](https://cloud.google.com/blog/products/ai-machine-learning/global-endpoint-for-claude-models-generally-available-on-vertex-ai)
* **Anthropic pricing details:** [Cloud platform pricing](https://platform.claude.com/docs/en/about-claude/pricing#cloud-platform-pricing)


---
title: Claude Platform on AWS
url: https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws
description: Access Claude's full platform capabilities through AWS with Anthropic-managed infrastructure.
---

Claude Platform on AWS gives you the full Anthropic platform experience, including the Messages API, Agent Skills, code execution, and beta features, accessible through your AWS account. Unlike [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), where AWS operates the inference stack, Anthropic operates Claude Platform on AWS. AWS provides the authentication layer (SigV4 or API key), IAM-based access control, and billing integration through AWS Marketplace.

<Note>
  The Anthropic SDKs support Claude Platform on AWS.
</Note>


## How the platform integration works

Source: https://platform.claude.com/llms-full.txt#how-the-platform-integration-works

Claude models run on Anthropic-managed infrastructure. This is a commercial integration for billing and access through AWS. Anthropic is the data processor for inference inputs and outputs. AWS processes billing and identity metadata under the marketplace model. Customers using Claude through Claude Platform on AWS are subject to Anthropic's [data use terms](https://www.anthropic.com/legal).

Claude Platform on AWS has the following operational characteristics: data might not reside in AWS, inference might route to Anthropic's primary cloud, and subservices might change without notice. Set the [`inference_geo`](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#data-residency) parameter per request to pin inference to a specific geography.

Claude Platform on AWS follows the same data retention policy as the first-party Claude API. Zero Data Retention (ZDR) is available on request. Contact your Anthropic account representative to enable it for your organization.


## Claude Platform on AWS versus Amazon Bedrock

Source: https://platform.claude.com/llms-full.txt#claude-platform-on-aws-versus-amazon-bedrock

Both offerings let you use Claude through AWS, but they differ in architecture, API surface, and feature availability.

| Aspect                       | Claude Platform on AWS                                                                                                                                                      | [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) | [Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy) |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Who operates the stack**   | Anthropic                                                                                                                                                                   | AWS                                                                                                        | AWS                                                                                                                            |
| **API surface**              | Claude API (`/v1/{endpoint}`)                                                                                                                                               | Messages API at `/anthropic/v1/messages`                                                                   | Bedrock Converse / InvokeModel                                                                                                 |
| **Feature availability**     | Typically same-day as Claude API (see [feature limitations](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#features-not-supported))           | Per Amazon Bedrock release schedule                                                                        | Per Amazon Bedrock release schedule                                                                                            |
| **Agent Skills**             | Available (beta)                                                                                                                                                            | Not available (requires code execution)                                                                    | Not available                                                                                                                  |
| **Beta features**            | Pass through with `anthropic-beta` headers (see [feature limitations](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#features-not-supported)) | `anthropic-beta` header not supported                                                                      | `anthropic-beta` header not supported                                                                                          |
| **Authentication**           | AWS IAM / SigV4 or API key                                                                                                                                                  | AWS IAM / SigV4                                                                                            | AWS IAM / SigV4 or bearer token                                                                                                |
| **Billing**                  | AWS Marketplace                                                                                                                                                             | AWS (native service)                                                                                       | AWS (native service)                                                                                                           |
| **Base URL**                 | `aws-external-anthropic.{region}.api.aws`                                                                                                                                   | `bedrock-mantle.{region}.api.aws`                                                                          | `bedrock-runtime.{region}.amazonaws.com`                                                                                       |
| **SDK client**               | Platform-specific client class (for example, `AnthropicAWS` in Python), in beta                                                                                             | `AnthropicBedrockMantle`                                                                                   | `AnthropicBedrock` / Bedrock SDK                                                                                               |
| **Console**                  | Claude Console (`platform.claude.com`, access through the AWS Console)                                                                                                      | Bedrock Console                                                                                            | Bedrock Console                                                                                                                |
| **Rate limits and quotas**   | Managed by Anthropic                                                                                                                                                        | Managed by AWS                                                                                             | Managed by AWS                                                                                                                 |
| **Inference data processor** | Anthropic                                                                                                                                                                   | AWS                                                                                                        | AWS                                                                                                                            |

If you need AWS-operated Claude, see [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock). Claude Platform on AWS uses a separate capacity pool from both the first-party Claude API and Amazon Bedrock. You can run workloads on more than one platform and fail over between them.

[AWS PrivateLink](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html) is supported for connecting your VPC to the Claude Platform on AWS endpoint.

**When to choose Bedrock:** Organizations in regulated industries that require FedRAMP High, IL4, IL5, or HIPAA-ready compliance, or that need AWS to be the sole data processor, should use [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock). Bedrock runs entirely on AWS-controlled infrastructure with AWS as the operating party.

**Which offering are you using?** Claude is available through several distinct products:

* **Claude Platform on AWS** (this page): The Claude API platform billed through AWS Marketplace. Managed in the [Claude Console](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#using-the-claude-console) and the AWS Console.
* **[Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock):** An AWS-native service. Managed in the Amazon Bedrock console and billed as AWS service usage.
* **Claude Enterprise procured through AWS Marketplace:** A [claude.ai](https://claude.ai) plan (the Claude chat product), not an API platform. Managed at claude.ai, and its account and migration behavior differ from what this page describes. See the [Claude Help Center](https://support.claude.com).
* **Direct Anthropic accounts:** The first-party Claude API and claude.ai plans billed by Anthropic. Managed in the Claude Console and at claude.ai.


## Set up your account

Source: https://platform.claude.com/llms-full.txt#set-up-your-account

Setting up Claude Platform on AWS happens in four phases: sign up on the AWS Console service page, complete your Anthropic organization setup, note your workspace ID, and sign in to the Claude Console.

<Note>
  Signing up through the AWS Console provisions a new Anthropic organization tied to your AWS account. This organization is separate from any existing organizations your company has with Anthropic, including Claude Enterprise organizations procured through AWS Marketplace. API keys, workspaces, and Claude Console settings from a first-party Anthropic organization don't carry over.

  If you have an existing Amazon Bedrock private offer, contact your Anthropic or AWS account representative before signing up so your discount applies from your first request. Discounts cannot be applied retroactively to usage incurred before your private offer is accepted. See [Private offers](https://platform.claude.com/docs/en/about-claude/pricing#private-offers).
</Note>

<Steps>
  <Step title="Sign up in the AWS Console">
    1. Open the [AWS Console](https://console.aws.amazon.com/) and navigate to the **Claude Platform on AWS** service page.
    2. Choose **Sign up**.
    3. On the Sign-up page, review the terms (Anthropic's End User License Agreement, the AWS Privacy Notice, and the AWS Customer Agreement) and select the agreement checkbox.
    4. Choose **Continue**.

    The page shows a **Sign-up in progress** banner. Stay on the page. Sign-up takes a few minutes while AWS handles the AWS Marketplace subscription for you, then redirects you automatically.

    If your organization has a private offer from Anthropic, the Console looks it up and prompts you to accept it in AWS Marketplace. See [Private offers](https://platform.claude.com/docs/en/about-claude/pricing#private-offers) for details.

    <Note>
      If you use Claude Platform on AWS, your content (such as prompts and completions) is processed by Anthropic outside of AWS. See Anthropic's [data use policies](https://www.anthropic.com/legal) for details on how content and metadata are processed and stored.
    </Note>
  </Step>

  <Step title="Set up your Anthropic organization">
    After sign-up completes, you're redirected to `platform.claude.com/partner-signup`.

    1. Enter the email address of your organization's owner and choose **Get started**.
    2. Check that email inbox for a setup link and follow it. If your browser shows a **Signed in as a different account** page, choose **Log out and continue**.
    3. Complete the organization details form (organization name, entity type, country, intended use) and choose **Complete setup**.

    Completing setup creates your Anthropic organization and accepts Anthropic's Commercial Terms of Service and Usage Policy. The AWS Console service page now shows a left navigation with **Home**, **API keys**, **Quickstart**, and **Workspaces**.
  </Step>

  <Step title="Create your workspace and note its ID">
    After you complete setup, the AWS Console prompts you to create a workspace. See [Workspaces](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#workspaces) for details on region binding, IAM resource scoping, and creating additional workspaces.

    Find the workspace ID under **Workspaces** on the AWS Console **Claude Platform on AWS** service page or in the [Claude Console](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#using-the-claude-console). Workspace IDs use the format `wrkspc_` followed by an alphanumeric identifier.
  </Step>

  <Step title="Sign in to the Claude Console">
    Access to the Claude Console is federated through AWS IAM:

    1. Assume an IAM role with the `aws-external-anthropic:AssumeConsole` permission. See [IAM actions for Claude Platform on AWS](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#console-access).
    2. From the **Claude Platform on AWS** service page, choose **Open Claude Console**. The AWS Console issues a JWT and redirects you to `platform.claude.com`.
    3. On first sign-in, you're prompted for an email address. Enter your work email. The platform provisions your Claude Console user just-in-time.

    When you're signed in through the AWS Console, the Claude Console scopes to your Claude Platform on AWS organization. An **Account managed by AWS** indicator appears in the bottom-left of the Claude Console sidebar.
  </Step>
</Steps>

### Moving from an existing Anthropic organization

Signing up for Claude Platform on AWS always provisions a new Anthropic organization tied to your AWS account. There is no in-place conversion: an existing organization, such as a first-party Claude API organization, can't become a Claude Platform on AWS organization.

Plan a move from an existing organization as a cutover to a new one:

* **Create the new organization first.** Sign up through the AWS Console (see [Set up your account](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#set-up-your-account)). If your move involves a private offer, complete sign-up before the offer is accepted: discounts apply from acceptance, not retroactively. See [Private offers](https://platform.claude.com/docs/en/about-claude/pricing#private-offers).
* **Recreate access and configuration.** API keys, workspaces, and Claude Console settings don't carry over from an existing organization. Create workspaces in the new organization and switch your applications to [Claude Platform on AWS authentication](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#authentication).
* **Update your integration.** Claude Platform on AWS serves the Claude API (`/v1/{endpoint}`), so request and response shapes are unchanged from the first-party Claude API. What changes is the base URL, the authentication method, and the required `anthropic-workspace-id` header; see [Making requests](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#making-requests). Some platform features differ; see [Features not supported](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#features-not-supported).
* **Cut over on your own schedule.** The new organization is independent of your existing one, and both can serve traffic in parallel. There's no need for a hard cutover: shift workloads gradually until all of your traffic is on the new organization.

Once the new organization is running, the differences are concentrated in billing and authentication, which are handled through AWS:

* **Billing** moves to AWS Marketplace: usage is billed in Claude Consumption Units rather than prepaid credits (see [Billing](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#billing)), and you set spend limits on the Billing page (see [Spend limits](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#spend-limits)). During the transition, billing stays separate: the existing organization continues to be billed as it is today.
* **Authentication and access** move to AWS: requests authenticate with AWS credentials or with API keys generated in the AWS Console, not the Claude Console (see [Authentication](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#authentication)). Organization membership is managed through AWS IAM rather than the Claude Console (see [Available pages](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#available-pages)), and Anthropic's client SDKs provide platform-specific client classes (see [Install an SDK](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#install-an-sdk)).
* **Day-to-day API usage** works the way it does on the first-party Claude API, except where noted in the [feature limitations](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#features-not-supported). Before shifting production traffic, check your rate limits: new organizations are placed on the Start tier, and limit increases go through your Anthropic account representative (see [Rate limits and quotas](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#rate-limits-and-quotas)).

For Claude Enterprise (claude.ai) organizations, which behave differently, see the [offering comparison](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#claude-platform-on-aws-vs-amazon-bedrock).

### Troubleshooting account setup

* **"Sign-up failed: Failed to enable OutboundWebIdentityFederation":** If you see this banner on first submit, choose **Continue** again. The IAM enablement can take a moment to take effect.
* **No progress indicator during sign-up:** Sign-up takes a few minutes. The page shows a static **Sign-up in progress** banner without a progress bar while AWS provisions your account.
* **"Signed in as a different account" after following the setup link:** Choose **Log out and continue**. The page reauthenticates you with the email address you entered.
* **"Not found" message during sign-in:** This message might appear briefly during redirect. You can dismiss it.
* **Usage page shows no data after your first API call:** Usage data can take a few minutes to appear in the Claude Console.
* **"Outbound web identity federation is disabled" on your first API call:** Enable federation once per account. See [Enable outbound web identity federation](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#enable-outbound-web-identity-federation).


## Before making API calls

Source: https://platform.claude.com/llms-full.txt#before-making-api-calls

Ensure you have:

1. An active AWS account with a subscription to Claude Platform on AWS (see [Set up your account](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#set-up-your-account))
2. The [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) installed and configured
3. **Outbound web identity federation enabled** on your AWS account, a one-time setup step (see [Enable outbound web identity federation](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#enable-outbound-web-identity-federation))
4. Your workspace ID (see [Obtain your workspace ID](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#obtain-your-workspace-id))
5. IAM permission to call the API: the `aws-external-anthropic:CreateInference` action on your workspace, plus `aws-external-anthropic:CallWithBearerToken` if you authenticate with an API key (see [IAM policies](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#iam-policies))

### Enable outbound web identity federation

The Claude Platform on AWS gateway calls `sts:GetWebIdentityToken` server-side to mint a JWT it forwards to Anthropic. This STS capability is **disabled by default** on every AWS account. Enable it once per account:

```bash CLI
aws iam enable-outbound-web-identity-federation

bash CLI
aws iam get-outbound-web-identity-federation-info

bash CLI
export ANTHROPIC_AWS_WORKSPACE_ID='wrkspc_01AbCdEf23GhIj'
export AWS_REGION='us-west-2'  # Your workspace's AWS region
```

The region is required. The SDK client raises an error if no region is set. Pass `aws_region`/`awsRegion` to the constructor, or set `AWS_REGION` (or `AWS_DEFAULT_REGION`). All AWS commercial regions are supported.


## Authentication

Source: https://platform.claude.com/llms-full.txt#authentication-4

Claude Platform on AWS supports two authentication methods: AWS IAM with Signature Version 4 (SigV4) request signing (primary) and API key authentication. Both use the same base URL and request format.

### SigV4 authentication

SigV4 is the enterprise-native path and integrates with your existing AWS IAM policies, roles, and auditing. Configure AWS credentials using any method supported by the [AWS default credential provider chain](https://docs.aws.amazon.com/sdkref/latest/guide/standardized-credentials.html):

* Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`)
* Shared credentials file (`~/.aws/credentials`)
* Shared config file (`~/.aws/config`) including SSO and `credential_process`
* Web identity (`AWS_WEB_IDENTITY_TOKEN_FILE` and `AWS_ROLE_ARN`) for IRSA and GitHub Actions
* ECS container credentials
* EC2 instance metadata service (IMDS)

Verify that your credentials are working:

```bash CLI
aws sts get-caller-identity

python Python
  from token_generator_for_aws_external_anthropic import TokenGenerator
  from anthropic import AnthropicAWS

  token = TokenGenerator(region="us-west-2").get_token()

  client = AnthropicAWS(api_key=token, aws_region="us-west-2")

typescript TypeScript
  import { getTokenProvider } from "@aws/token-generator-for-aws-external-anthropic";
  import AnthropicAws from "@anthropic-ai/aws-sdk";

  const tokenProvider = getTokenProvider({ region: "us-west-2" });
  const token = await tokenProvider();

  const client = new AnthropicAws({ apiKey: token, awsRegion: "us-west-2" });

java Java
  import software.amazon.awsexternalanthropic.TokenGenerator;
  import software.amazon.awssdk.regions.Region;
  import com.anthropic.aws.backends.AwsBackend;
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;

  void main() {
      String token = TokenGenerator.builder().region(Region.US_WEST_2).build().getToken();

      AnthropicClient client = AnthropicOkHttpClient.builder()
          .backend(AwsBackend.builder()
              .apiKey(token)
              .region(Region.US_WEST_2)
              .workspaceId(System.getenv("ANTHROPIC_AWS_WORKSPACE_ID"))
              .build())
          .build();
  }
  ```
</CodeGroup>

If you can generate the token locally, your process already has SigV4 credentials, and SigV4 authentication is usually the simpler choice. Use short-term keys when the process making API calls is separate from the process that holds AWS credentials.

The SDK does not refresh short-term keys automatically. When a token expires, generate a new one and construct a new client. The principal that uses the token still needs the `aws-external-anthropic:CallWithBearerToken` IAM action.

### Credential precedence

The platform-specific client resolves authentication in the following order. Argument names vary by language convention: TypeScript and PHP use camelCase as shown, Python and Ruby use snake\_case, Go uses PascalCase with capitalized acronyms, and C# and Java use the language's property or builder idioms.

1. `apiKey` constructor argument → `x-api-key` header
2. `awsAccessKey` + `awsSecretAccessKey` constructor arguments → AWS SigV4
3. `awsProfile` constructor argument → AWS SigV4 with named profile
4. `ANTHROPIC_AWS_API_KEY` environment variable → `x-api-key` header
5. Default AWS credential provider chain → AWS SigV4

### Region resolution

The client reads `AWS_REGION` from the environment if `aws_region`/`awsRegion` is not passed to the constructor, falling back to `AWS_DEFAULT_REGION` for compatibility with the standard AWS SDKs. Region is required and there is no default: the `AnthropicAWS`/`AnthropicAws` client raises an error if neither the constructor argument nor an environment variable is set.


## Install an SDK

Source: https://platform.claude.com/llms-full.txt#install-an-sdk-3

Anthropic's [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) support Claude Platform on AWS. Each SDK provides a platform-specific client class that handles SigV4 signing, region-based base URL construction, and the `anthropic-workspace-id` header.

<Tabs>
  <Tab title="Python">

<Tip>
      On macOS with Homebrew Python or other externally managed Python environments, `pip install` can fail with a PEP 668 `externally-managed-environment` error. Create and activate a virtual environment first: `python3 -m venv .venv && source .venv/bin/activate`.
    </Tip>
  </Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="C#">

</Tab>

  <Tab title="Go">

</Tab>

  <Tab title="Java">
    ```kotlin Gradle
    implementation("com.anthropic:anthropic-java-aws:2.60.0")

xml Maven
    <dependency>
      <groupId>com.anthropic</groupId>
      <artifactId>anthropic-java-aws</artifactId>
      <version>2.60.0</version>
    </dependency>

bash
    composer require anthropic-ai/sdk aws/aws-sdk-php

bash
    gem install anthropic aws-sdk-core
    ```
  </Tab>
</Tabs>

<Note>
  SDK clients for Claude Platform on AWS are in beta.
</Note>
