# platform.claude.com Documentation (Part 13 of 35)

## Batch requests

Source: https://platform.claude.com/llms-full.txt#batch-requests-6

You can include `mcp_servers` in [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing) requests. MCP tool calls through the Batches API are priced the same as those in regular Messages API requests.


## Data retention

Source: https://platform.claude.com/llms-full.txt#data-retention-11

The MCP connector is not covered by ZDR arrangements. Data exchanged with MCP servers, including tool definitions and execution results, is retained according to Anthropic's standard data retention policy.

For ZDR eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).


## Migration guide

Source: https://platform.claude.com/llms-full.txt#migration-guide

If you're using the deprecated `mcp-client-2025-04-04` beta header, follow this guide to migrate to the new version.

### Key changes

1. **New beta header:** Change from `mcp-client-2025-04-04` to `mcp-client-2025-11-20`
2. **Tool configuration moved:** Tool configuration now lives in the `tools` array as MCPToolset objects, not in the MCP server definition
3. **More flexible configuration:** New pattern supports allowlisting, denylisting, and per-tool configuration

### Migration steps

**Before (deprecated):**

**After (current):**

### Common migration patterns

| Old pattern                                 | New pattern                                                                             |
| ------------------------------------------- | --------------------------------------------------------------------------------------- |
| No `tool_configuration` (all tools enabled) | MCPToolset with no `default_config` or `configs`                                        |
| `tool_configuration.enabled: false`         | MCPToolset with `default_config.enabled: false`                                         |
| `tool_configuration.allowed_tools: [...]`   | MCPToolset with `default_config.enabled: false` and specific tools enabled in `configs` |


## Deprecated version: mcp-client-2025-04-04

Source: https://platform.claude.com/llms-full.txt#deprecated-version-mcp-client-2025-04-04

<Note type="warning">
  This version is deprecated. Migrate to `mcp-client-2025-11-20` using the preceding [migration guide](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector#migration-guide).
</Note>

The previous version of the MCP connector included tool configuration directly in the MCP server definition:

### Deprecated field descriptions

| Property                           | Type    | Description                                                        |
| ---------------------------------- | ------- | ------------------------------------------------------------------ |
| `tool_configuration`               | object  | **Deprecated:** Use MCPToolset in the `tools` array instead        |
| `tool_configuration.enabled`       | boolean | **Deprecated:** Use `default_config.enabled` in MCPToolset         |
| `tool_configuration.allowed_tools` | array   | **Deprecated:** Use allowlist pattern with `configs` in MCPToolset |


---
title: Remote MCP servers
url: https://platform.claude.com/docs/en/agents-and-tools/remote-mcp-servers
description: Connect Claude to third-party remote MCP servers through the MCP connector API. Browse example servers and review the steps to connect.
---

Several companies have deployed remote MCP servers that developers can connect to by using the Anthropic MCP connector API. These servers expand the capabilities available to developers and end users by providing remote access to various services and tools through the MCP protocol.

<Note>
  The remote MCP servers listed below are third-party services designed to work with the Claude API. These servers are not owned, operated, or endorsed by Anthropic. Users should only connect to remote MCP servers they trust and should review each server's security practices and terms before connecting.
</Note>


## Connecting to remote MCP servers

Source: https://platform.claude.com/llms-full.txt#connecting-to-remote-mcp-servers

To connect to a remote MCP server:

1. Review the documentation for the specific server you want to use.
2. Ensure you have the necessary authentication credentials.
3. Follow the server-specific connection instructions provided by each company.

For more information about using remote MCP servers with the Claude API, see [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector).

<Note>
  Once connected, remote MCP tools follow the same triggering behavior as any other tool. See [When Claude uses MCP tools](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector#when-claude-uses-mcp-tools).
</Note>


## Remote MCP server examples

Source: https://platform.claude.com/llms-full.txt#remote-mcp-server-examples

<MCPServersTable platform="mcpConnector" />

<Note>
  **Looking for more?** [Find hundreds more MCP servers on GitHub](https://github.com/modelcontextprotocol/servers).
</Note>


### MCP > MCP tunnels

---
title: MCP tunnels
url: https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview
description: Securely connect Claude to MCP servers running in your private network without opening inbound ports or exposing services to the public internet.
---

MCP tunnels let you connect Claude to Model Context Protocol (MCP) servers that run inside your private network. Traffic flows over an outbound-only connection, so you don't need to open inbound firewall ports, expose services to the public internet, or allowlist Anthropic's IP ranges on your origin.

<Note>
  MCP tunnels are in research preview. [Request access](https://claude.com/form/claude-managed-agents) to try them. They are provided "as-is" without any uptime, support, or continuity commitment, and they depend on a third-party network provider (Cloudflare) that makes no availability commitment for the underlying transport. Anthropic may modify or discontinue MCP tunnels at any time.
</Note>

For Zero Data Retention and HIPAA BAA eligibility, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility).


## How it works

Source: https://platform.claude.com/llms-full.txt#how-it-works-7

The [tunnel stack](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) is two components that run inside your network:

* **[cloudflared](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components):** Cloudflare's open-source tunnel connector. It initiates outbound-only connections to the [tunnel edge](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) and carries encrypted traffic from Anthropic to your proxy.
* **[Proxy](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components):** Anthropic's routing component. It terminates [inner TLS](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components), validates that upstream IPs fall within an allowed range, and routes each request to the correct [upstream MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) based on hostname.

Each MCP server you expose gets a hostname under your tunnel domain (for example, `docs.<your-tunnel-domain>`). You attach these hostnames to a Managed Agent session in the Claude Console, or pass them to the Messages API through the [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector).


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-4

Before deploying, make sure you have:

* A deployment target: a Kubernetes cluster, or a VM with Docker and Docker Compose.

* A tunnel. Create one in the Claude Console (see [Create a tunnel](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#create-a-tunnel)) or through the API; the Helm chart's setup hook can also create one for you during install.

* A way for your stack to authenticate to the Tunnels API. Choose one:

  * **[Programmatic access](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#credential-provisioning) (recommended).** Set up [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) when you create the tunnel. Your stack mints short-lived API tokens from your identity provider, fetches the tunnel token, and generates and registers a CA certificate automatically. Requires permission to manage federation rules, a registered OIDC issuer, and a federation rule with the `workspace:manage_tunnels` scope.
  * **[Manual](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#credential-provisioning).** Supply static credentials yourself: the tunnel token from the Console and a server certificate signed by a CA you register there. See [Get the connection details](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#get-the-connection-details) and [Add a CA certificate](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#add-a-ca-certificate).

* One or more MCP servers running in your private network. See [Remote MCP servers](https://platform.claude.com/docs/en/agents-and-tools/remote-mcp-servers) for examples.

* Outbound connectivity as listed under [Network requirements](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#network-requirements).

### Network requirements

| Component       | Destination                                          | Port / protocol  | Used during                     |
| --------------- | ---------------------------------------------------- | ---------------- | ------------------------------- |
| Setup component | `api.anthropic.com`                                  | 443 TCP          | Provisioning and token rotation |
| cloudflared     | Tunnel edge (`198.41.192.0/19`, `2606:4700:a0::/44`) | 7844 TCP and UDP | Runtime                         |
| Proxy           | Your upstream MCP servers                            | As configured    | Runtime                         |


## Security model

Source: https://platform.claude.com/llms-full.txt#security-model

### Security layers

Three independent layers protect every request:

| Layer                                                                       | Protects against                                                         |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Outer mTLS between Anthropic and the transport provider, with IP validation | Unauthorized clients reaching the tunnel                                 |
| Inner TLS from Anthropic's back end to your proxy                           | Payload inspection by the transport provider or any network intermediary |
| OAuth on each MCP server                                                    | Unauthorized use of MCP tools by authenticated tunnel traffic            |

The tunnel transport runs on Cloudflare's network. Because the proxy terminates inner TLS using a certificate that only you hold, Cloudflare cannot read request or response payloads. Anthropic does not connect to a tunnel until a CA certificate is registered, so payloads are always encrypted when they cross Cloudflare's network. Cloudflare does receive connection metadata; see [What the transport provider can observe](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#what-the-transport-provider-can-observe).

### Shared responsibility model

| Anthropic handles                                                         | Your organization handles                                                                                                                      |
| ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Tunnel access control                                                     | All content and traffic that transits your tunnel, and compliance with applicable third-party acceptable-use policies (including Cloudflare's) |
| Validating your CA certificate before connecting to your proxy            | Adherence to the deployment guidance on these pages                                                                                            |
| Ensuring Claude only sends requests to tunnels owned by your organization | Securing tunnel tokens and TLS private keys                                                                                                    |
|                                                                           | Managing the server certificate and renewing it before it expires                                                                              |
|                                                                           | Configuring OAuth on each MCP server                                                                                                           |
|                                                                           | Restricting network access for the proxy and MCP servers                                                                                       |
|                                                                           | Notifying Anthropic if you suspect a breach                                                                                                    |

<Warning>
  If an attacker obtains your tunnel token **and** one of your TLS private keys, they could impersonate your proxy and read MCP request payloads. Treat both as high-value secrets. See [MCP tunnels security](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/security) for hardening guidance.
</Warning>

### What the transport provider can observe

Cloudflare provides the outbound transport. It cannot read MCP request or response payloads, but it does receive the following connection metadata:

* the egress IP address of the host running cloudflared
* a cloudflared host fingerprint
* connection timing and byte-volume
* the `*.tunnel.anthropic.com` subdomain assigned to your tunnel

Anthropic's agreement with Cloudflare restricts Cloudflare's use of this telemetry. Cloudflare acts as a subprocessor for this research preview.


## Deploy a tunnel

Source: https://platform.claude.com/llms-full.txt#deploy-a-tunnel

If you're new to MCP tunnels, start with the quickstart to get a working tunnel locally before configuring a production deployment.

<CardGroup cols={2}>
  <Card title="Quickstart" icon="rocket" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/quickstart">
    The shortest path to a working tunnel: Docker Compose with a sample MCP server.
  </Card>

  <Card title="Deploy with Helm" icon="stack" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-helm">
    Install on a Kubernetes cluster using the Anthropic Helm chart.
  </Card>

  <Card title="Deploy with Docker Compose" icon="cube" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose">
    Install on a VM using Docker Compose.
  </Card>
</CardGroup>

Choosing between them:

* **Deployment target**

  * **Helm** when deploying to Kubernetes.
  * **Docker Compose** for a single host or local testing.

* **Authentication for setup**

  * **Programmatic access** (through Workload Identity Federation) when you have an OIDC identity provider such as a Kubernetes cluster, cloud IAM, or SPIFFE.
  * **Manual credentials** when you don't, or when you're testing.


## Use the tunneled MCP servers

Source: https://platform.claude.com/llms-full.txt#use-the-tunneled-mcp-servers

Once your tunnel is active (it has an active CA certificate and your tunnel stack is connected), the upstream MCP servers are reachable from Claude Managed Agents and the Messages API.

<Note>
  MCP tunnels created through the Console are not available as connectors in claude.ai.
</Note>

In both cases, the tunnel carries encrypted traffic to your MCP server but does not authenticate to it. If the upstream MCP server requires its own authentication (OAuth, bearer token), supply it the same way you would for any other MCP server; it is independent of the tunnel.

### Managed Agents (Console)

1. In **Managed Agents > Sessions**, create a session and choose **Create new agent** so you can edit the MCP server list.
2. Click **+ MCP Server** and open the dropdown. Tunnels in the session's workspace that have at least one active certificate appear at the top of the list, above the public connector catalog.
3. Select the tunnel and supply the **Subdomain** that your proxy routes to a specific MCP server, and the **Path** the upstream MCP server expects. The **Resolves to** line shows the exact URL.

### Messages API

Pass the upstream MCP server's URL in the `mcp_servers` array, the same way as any other remote MCP server. The request body and `anthropic-beta` header follow the standard [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector) format; only the `url` is tunnel-specific. The following example uses the MCP connector's `mcp-client` beta header, which is separate from the `mcp-tunnels` beta used by the [Tunnels API](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference). Make the request in the workspace the tunnel was created in by using an API key for that workspace or, if your key has access to multiple workspaces, by setting the [`anthropic-workspace-id` header](https://platform.claude.com/docs/en/manage-claude/authentication#select-a-workspace) to that workspace.

The URL's host is `<subdomain>.<your-tunnel-domain>`. The path depends on your upstream MCP server, not the tunnel: FastMCP's `streamable-http` transport serves at `/mcp`, and other servers may use `/` or a custom path (check the server's documentation). The proxy forwards the path untouched.

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: mcp-client-2025-11-20" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1000,
      "messages": [{"role": "user", "content": "Use the hello tool to greet tunnel."}],
      "mcp_servers": [
        {
          "type": "url",
          "url": "https://echo.YOUR_TUNNEL_DOMAIN_HERE/mcp",
          "name": "echo"
        }
      ],
      "tools": [{"type": "mcp_toolset", "mcp_server_name": "echo"}]
    }'

bash CLI
  ant beta:messages create --beta mcp-client-2025-11-20 <<'YAML'
  model: claude-opus-5
  max_tokens: 1000
  messages:
    - role: user
      content: Use the hello tool to greet tunnel.
  mcp_servers:
    - type: url
      url: https://echo.YOUR_TUNNEL_DOMAIN_HERE/mcp
      name: echo
  tools:
    - type: mcp_toolset
      mcp_server_name: echo
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=1000,
      messages=[{"role": "user", "content": "Use the hello tool to greet tunnel."}],
      mcp_servers=[
          {
              "type": "url",
              "url": "https://echo.YOUR_TUNNEL_DOMAIN_HERE/mcp",
              "name": "echo",
          }
      ],
      tools=[{"type": "mcp_toolset", "mcp_server_name": "echo"}],
      betas=["mcp-client-2025-11-20"],
  )

  print(response)

typescript TypeScript
  const anthropic = new Anthropic();

  const response = await anthropic.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 1000,
    messages: [
      {
        role: "user",
        content: "Use the hello tool to greet tunnel."
      }
    ],
    mcp_servers: [
      {
        type: "url",
        url: "https://echo.YOUR_TUNNEL_DOMAIN_HERE/mcp",
        name: "echo"
      }
    ],
    tools: [
      {
        type: "mcp_toolset",
        mcp_server_name: "echo"
      }
    ],
    betas: ["mcp-client-2025-11-20"]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Messages::Model.ClaudeOpus5,
      MaxTokens = 1000,
      Messages = new List<BetaMessageParam>
      {
          new() { Role = Role.User, Content = "Use the hello tool to greet tunnel." }
      },
      McpServers = new List<BetaRequestMcpServerUrlDefinition>
      {
          new()
          {
              Url = "https://echo.YOUR_TUNNEL_DOMAIN_HERE/mcp",
              Name = "echo"
          }
      },
      Tools = new List<BetaToolUnion>
      {
          new BetaMcpToolset("echo")
      },
      Betas = ["mcp-client-2025-11-20"]
  };

  var message = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1000,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Use the hello tool to greet tunnel.")),
  	},
  	MCPServers: []anthropic.BetaRequestMCPServerURLDefinitionParam{
  		{
  			URL:  "https://echo.YOUR_TUNNEL_DOMAIN_HERE/mcp",
  			Name: "echo",
  		},
  	},
  	Tools: []anthropic.BetaToolUnionParam{
  		{OfMCPToolset: &anthropic.BetaMCPToolsetParam{
  			MCPServerName: "echo",
  		}},
  	},
  	Betas: []anthropic.AnthropicBeta{
  		anthropic.AnthropicBetaMCPClient2025_11_20,
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaMcpToolset;
  // ...
  import com.anthropic.models.beta.messages.BetaRequestMcpServerUrlDefinition;
  // ...

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1000L)
          .addUserMessage("Use the hello tool to greet tunnel.")
          .addMcpServer(BetaRequestMcpServerUrlDefinition.builder()
              .url("https://echo.YOUR_TUNNEL_DOMAIN_HERE/mcp")
              .name("echo")
              .build())
          .addTool(BetaMcpToolset.builder()
              .mcpServerName("echo")
              .build())
          .addBeta("mcp-client-2025-11-20")
          .build();

      BetaMessage response = client.beta().messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->beta->messages->create(
      maxTokens: 1000,
      messages: [
          ['role' => 'user', 'content' => 'Use the hello tool to greet tunnel.']
      ],
      model: 'claude-opus-5',
      mcpServers: [
          [
              'type' => 'url',
              'url' => 'https://echo.YOUR_TUNNEL_DOMAIN_HERE/mcp',
              'name' => 'echo',
          ],
      ],
      tools: [
          [
              'type' => 'mcp_toolset',
              'mcpServerName' => 'echo',
          ],
      ],
      betas: ['mcp-client-2025-11-20'],
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 1000,
    messages: [
      { role: "user", content: "Use the hello tool to greet tunnel." }
    ],
    mcp_servers: [
      {
        type: "url",
        url: "https://echo.YOUR_TUNNEL_DOMAIN_HERE/mcp",
        name: "echo"
      }
    ],
    tools: [
      {
        type: "mcp_toolset",
        mcp_server_name: "echo"
      }
    ],
    betas: ["mcp-client-2025-11-20"]
  )

  puts response
  ```
</CodeGroup>

For authenticating to the upstream MCP server (`authorization_token`) and other `mcp_servers` options, see [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-61

<CardGroup cols={2}>
  <Card title="Security" icon="lock" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/security">
    Hardening guidance, credential rotation, and breach response.
  </Card>

  <Card title="Troubleshooting" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/troubleshooting">
    Diagnose connectivity, TLS, and routing issues.
  </Card>

  <Card title="Reference" icon="book" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference">
    Proxy config fields, the Tunnels API, certificate requirements, and the setup component.
  </Card>

  <Card title="MCP connector" icon="link" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-connector">
    Use tunneled servers from the Messages API.
  </Card>
</CardGroup>


---
title: MCP tunnels quickstart
url: https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/quickstart
description: Connect Claude to a private MCP server using a local Docker Compose deployment.
---

<Note>
  MCP tunnels are in research preview. [Request access](https://claude.com/form/claude-managed-agents) to try them.
</Note>

This quickstart takes you from zero to Claude calling a private MCP server through a tunnel. It uses Docker Compose with [manual](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#credential-provisioning) credential provisioning, which is the shortest path for local testing. For production deployments, see [Deploy with Helm](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-helm) or [Deploy with Docker Compose](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose).


## What you'll build

Source: https://platform.claude.com/llms-full.txt#what-you-ll-build

A two-container [tunnel stack](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) (the [proxy](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) and [cloudflared](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components)) plus a sample MCP server running alongside it. When everything is running, the sample server is reachable from Claude at `https://echo.<your-tunnel-domain>/mcp` even though nothing is listening on a public port.


## What you need

Source: https://platform.claude.com/llms-full.txt#what-you-need

* [Docker and Docker Compose](https://docs.docker.com/get-docker/) on a machine with outbound internet access.
* A role in the [Claude Console](https://platform.claude.com) that can manage MCP tunnels. See the [Console guide prerequisites](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#prerequisites).
* [OpenSSL](https://openssl-library.org/source/) 1.1.1 or later. Preinstalled on macOS and most Linux distributions; on Windows, install it separately (the `openssl` binary must be on your `PATH`).

<Steps>
  <Step title="Create a tunnel">
    In the Claude Console sidebar, go to **Manage > MCP tunnels** and click **New tunnel**. Give it a name. Leave **Set up programmatic access** off; this quickstart uses manual credential provisioning.

    After it's created, open the tunnel. Copy two values from the **Connection** section:

    * **Domain** (looks like `abcd1234.tunnel.anthropic.com`)
    * **Token** (click the eye icon, then copy)
  </Step>

  <Step title="Set up the deployment directory">
    <Tabs>
      <Tab title="macOS / Linux">

</Tab>

      <Tab title="Windows (PowerShell)">

</Tab>
    </Tabs>
  </Step>

  <Step title="Generate a CA and server certificate">
    The proxy terminates [inner TLS](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) using a certificate signed by a CA you control. Generate both:

    <Tabs>
      <Tab title="macOS / Linux">

</Tab>

      <Tab title="Windows (PowerShell)">

</Tab>
    </Tabs>

    Back in the Console, on the tunnel detail page, click **Add certificate** and upload `data/ca.crt` (or paste its contents). The tunnel status flips to **Active**.
  </Step>

  <Step title="Write the sample MCP server">
    <Tabs>
      <Tab title="macOS / Linux">

</Tab>

      <Tab title="Windows (PowerShell)">

</Tab>
    </Tabs>
  </Step>

  <Step title="Write the proxy config and compose file">
    <Tabs>
      <Tab title="macOS / Linux">

</Tab>

      <Tab title="Windows (PowerShell)">

</Tab>
    </Tabs>
  </Step>

  <Step title="Start it">
    <Tabs>
      <Tab title="macOS / Linux">

</Tab>

      <Tab title="Windows (PowerShell)">

</Tab>
    </Tabs>

    You should see one `route configured` line for `echo` and four `Registered tunnel connection` lines. The containers take a few seconds to start; rerun the log commands if they come back empty.
  </Step>

  <Step title="Call it from Claude">
    In the Console, go to **Managed Agents > Sessions** and create a session. In the agent picker choose **Create new agent**, give the agent a name, and keep the pre-filled model. Click **+ MCP Server**, select your tunnel, set **Subdomain** to `echo` and **Path** to `mcp`. Then ask:

    > Use the hello tool to greet tunnel.

    You should see a tool call followed by its result.
  </Step>
</Steps>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-62

The tunnel is verified end to end. To swap in your own MCP server, add it to `docker-compose.yaml` (or run it on the same Docker network), add a route for it in `config/mcp-proxy.yaml`, then restart the proxy (`docker compose restart mcp-proxy`).

For production deployments:

<CardGroup cols={2}>
  <Card title="Deploy with Docker Compose" icon="cube" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose">
    Hardened single-host deployment, with or without programmatic access.
  </Card>

  <Card title="Deploy with Helm" icon="stack" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-helm">
    Kubernetes deployment with automatic credential management.
  </Card>
</CardGroup>


---
title: Architecture and components
url: https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts
description: Canonical names for the parts of an MCP tunnel deployment, the two credential-provisioning modes, and the connection model.
---

<Note>
  MCP tunnels are in research preview. [Request access](https://claude.com/form/claude-managed-agents) to try them.
</Note>

This page defines the terms used throughout the [MCP tunnels](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview) documentation. Several components appear under different names in configuration files, container images, and prose; the following tables give one canonical name for each and list the aliases you may encounter.


## Components

Source: https://platform.claude.com/llms-full.txt#components

| Term                    | Definition                                                                                                                                                                                                                                                                                                              | Also appears as                                                                                                                                                                                  |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Tunnel stack**        | The two containers you run inside your network to attach to a tunnel: the proxy and cloudflared. One stack serves one tunnel and can be replicated across hosts for availability. With programmatic access, the setup component runs alongside the stack to provision credentials.                                      | the stack, the MCP tunnel stack, the tunnel deployment, your deployment                                                                                                                          |
| **Proxy**               | Anthropic's routing component. Terminates inner TLS, validates that upstream IPs fall within an allowed range, and routes each request to an upstream MCP server based on hostname.                                                                                                                                     | `mcp-proxy` (image name, Compose service name, and Helm container name), `mcp-gateway` (container-internal config path `/etc/mcp-gateway/config.yaml` and Helm `gateway.config.*` values prefix) |
| **cloudflared**         | Cloudflare's open-source tunnel connector. Initiates the outbound-only connections from your network to the tunnel edge and carries encrypted traffic between the edge and the proxy. Not related to a Managed Agent.                                                                                                   | the outbound connector, the tunnel connector                                                                                                                                                     |
| **Setup component**     | The `setup` binary, shipped inside the `mcp-proxy` image. With programmatic access it authenticates over Workload Identity Federation, fetches the tunnel token, generates a CA and server certificate, and registers the CA with Anthropic. Also provides `renew-cert`.                                                | setup Job (the Helm pre-install hook), `setup` service (the Compose profile), setup hook, setup binary, setup CLI                                                                                |
| **Tunnel edge**         | The Cloudflare edge servers that cloudflared dials out to (IP ranges `198.41.192.0/19` and `2606:4700:a0::/44`, port 7844 TCP and UDP). The tunnel that runs over them is provisioned and controlled by Anthropic; Cloudflare operates the underlying network.                                                          | the edge, the Anthropic-operated tunnel edge                                                                                                                                                     |
| **Inner TLS**           | A second TLS handshake carried inside the tunnel's plaintext WebSocket stream, between Anthropic's backend and your proxy. The proxy presents a server certificate signed by a CA you registered on the tunnel. Because only you hold the private key, the transport provider cannot read request or response payloads. | the inner TLS handshake                                                                                                                                                                          |
| **Upstream MCP server** | An MCP server running in your private network that the proxy routes to. Each upstream is exposed as one subdomain under your tunnel domain.                                                                                                                                                                             | upstream, routed MCP server, tunneled MCP server                                                                                                                                                 |


## Credential provisioning

Source: https://platform.claude.com/llms-full.txt#credential-provisioning

The tunnel stack needs two credentials at runtime: the **tunnel token**, which authenticates cloudflared's outbound connection, and a **server certificate** signed by a CA registered on the tunnel, which the proxy presents during the inner TLS handshake. There are two ways to supply them, presented throughout this guide as a pair of tabs.

| Mode                    | How credentials reach the stack                                                                                                                                                                                                                                                                                                                                                           | Helm chart name                                   | Tab label                       |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | ------------------------------- |
| **Programmatic access** | The setup component authenticates to the Tunnels API through [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation), fetches the tunnel token, generates a CA and server certificate locally, and registers the CA. No long-lived secret is copied by hand. Requires a federation rule with the `workspace:manage_tunnels` scope. | Managed mode (`setup.enabled: true`, the default) | **With programmatic access**    |
| **Manual**              | You copy the tunnel token from the Claude Console, generate a CA and server certificate yourself (for example with `openssl`), register the CA in the Console, and supply the token and certificate to the stack as secrets. No setup component runs.                                                                                                                                     | External mode (`setup.enabled: false`)            | **Without programmatic access** |

These modes are also referred to as **the programmatic flow** and **the manual flow** in the deploy guides.


## Connection model

Source: https://platform.claude.com/llms-full.txt#connection-model

Two directions are at work in a tunnel, and they point opposite ways:

* **Connection direction:** cloudflared dials **outbound** from your network to the tunnel edge. Your firewall sees only egress on port 7844; no inbound port is opened.
* **Request direction:** once that connection is established, MCP requests travel **from Anthropic toward your network** over it, through cloudflared to the proxy, and on to the upstream MCP server.

The phrase "outbound-only" describes the connection, not the requests carried over it.

Inner TLS spans Anthropic's backend and your proxy. cloudflared and the tunnel edge sit between them on the wire but see only ciphertext; the proxy is the first place inside your network where MCP request payloads are readable.


## See also

Source: https://platform.claude.com/llms-full.txt#see-also-2

* [MCP tunnels](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview) for the security model and shared-responsibility table.
* [MCP tunnels reference](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference) for proxy configuration fields, certificate requirements, and the setup component.


---
title: Deploy MCP tunnels with Docker Compose
url: https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose
description: Install the MCP tunnel stack on a VM using Docker Compose.
---

<Note>
  MCP tunnels are in research preview. [Request access](https://claude.com/form/claude-managed-agents) to try them.
</Note>

This guide deploys the [tunnel stack](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) as hardened containers on a single host. The same configuration can be replicated across multiple hosts for availability.


## Before you begin

Source: https://platform.claude.com/llms-full.txt#before-you-begin-2

You need:

* **A tunnel.** With programmatic access, the [setup component](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) creates one for you when you don't supply a tunnel ID; to attach to an existing tunnel instead, [create it in the Console](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#create-a-tunnel) and record the tunnel ID (`tnl_...`). Manual provisioning always starts from a Console-created tunnel.

* **A way for the host to authenticate to the Tunnels API.**

  * **Programmatic access (recommended).** Turn on **Set up programmatic access** when creating the tunnel (or create the federation rule directly under **Settings > Workload identity** if you're letting the setup component create the tunnel) so the setup component can authenticate through Workload Identity Federation. Record the federation rule ID (`fdrl_...`) and your organization ID.
  * **Manual.** Skip programmatic access. You'll [get the tunnel token from the Console](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#get-the-connection-details), generate a CA and server certificate yourself, and [register the CA in the Console](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#add-a-ca-certificate).

* **A host with Docker and Docker Compose** installed. The manual flow also requires `openssl` (1.1.1 or later).

* **Outbound network connectivity** from the host to `api.anthropic.com` (443 TCP) and the [tunnel edge](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) (7844 TCP and UDP). See the full [network requirements](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#network-requirements).

* **One or more MCP servers** running and reachable from the host on the addresses you'll configure under `routes`. If you don't have one yet, [use the sample server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose#optional-use-a-sample-mcp-server).


## Optional: Use a sample MCP server

Source: https://platform.claude.com/llms-full.txt#optional-use-a-sample-mcp-server

If you don't have an MCP server available for testing, use this minimal one:

The following Install steps `cd` into `mcp-tunnel/` and note where to add the corresponding service and route.


## Install

Source: https://platform.claude.com/llms-full.txt#install

This guide provides one reference approach using Docker Compose. You are responsible for adapting it to meet your organization's security requirements.

<Tabs>
  <Tab title="With programmatic access">
    This path requires the host to have an OIDC identity provider (such as a cloud VM metadata server or SPIFFE). If it doesn't, use the **Without programmatic access** tab instead.

    The setup component uses Workload Identity Federation to fetch the tunnel token, generate a CA and server certificate, and register the CA with Anthropic.

    <Steps>
      <Step title="Prepare the deployment directory">

The containers run as the non-root UID `65532` and need write access to `data/`.
      </Step>

      <Step title="Write docker-compose.yaml">
        The compose file pins images by SHA-256 digest, runs every container as non-root with a read-only filesystem, drops all Linux capabilities, and disables privilege escalation.

If you're using the [sample MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose#optional-use-a-sample-mcp-server), append it as a service:

</Step>

      <Step title="Provision the tunnel">
        Set the identifiers. Leave `TUNNEL_ID` unset to have the setup component create a tunnel; set it to attach to an existing tunnel from the [Console](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#create-a-tunnel):

If your federation rule is scoped to a workspace other than your organization's default, also set `ANTHROPIC_WORKSPACE_ID=wrkspc_...`; the setup component uses the default workspace otherwise. An auto-created tunnel is created in that workspace.

        Set `ANTHROPIC_IDENTITY_TOKEN` to an OIDC JWT from this host's identity provider. Follow the [WIF guide for your provider](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#identity-providers) to register the issuer, set the rule's subject, and mint the token; the rule's audience must match the audience you request when minting.

        Run the setup component:

`setup init` is idempotent over `data/`: re-running it reuses the tunnel ID and CA already stored there and never creates a second tunnel. A new CA is generated and registered only when `data/` is empty or `TUNNEL_ID` has changed; in that case the cap of two active certificates applies, so revoke one in the Console first if both slots are filled.

        See [Setup component authentication failures](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/troubleshooting#setup-component-authentication-failures) if it errors.

        Retrieve your tunnel domain and export it for later steps:

<Note>
          Workload Identity Federation tokens are short-lived (1 hour by default) and expire automatically; there is nothing to revoke after setup completes.
        </Note>
      </Step>

      <Step title="Write the proxy config">
        `tunnel_domain` is **required**: the [proxy](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) uses it to strip the domain suffix from incoming hostnames before looking up the subdomain in `routes`. `routes` is a flat map from subdomain to upstream URL, not a list.

The `echo:` route targets the [sample MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose#optional-use-a-sample-mcp-server); replace it with (or add) your own routes. See the [proxy configuration](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference#proxy-configuration) reference for all available fields.
      </Step>

      <Step title="Start the deployment">

</Step>
    </Steps>
  </Tab>

  <Tab title="Without programmatic access">
    Use this flow if you didn't turn on **Set up programmatic access**, or for local development and testing. There is no `setup` service.

    <Steps>
      <Step title="Get the tunnel token and domain from the Console">
        On the tunnel detail page, copy the **Domain** (it has the form `abcd1234.tunnel.anthropic.com`), then click the eye icon next to **Token** to fetch the tunnel token and use the copy icon to copy it.

        Set both as shell variables for the rest of the guide:

</Step>

      <Step title="Scaffold and generate certificates">

The proxy listens on `:8080` over plain WebSocket; the [inner TLS](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) handshake happens **inside** that WebSocket stream using these certificates. Anthropic verifies the inner handshake against the CA you register in the Console. The server certificate's Subject Alternative Name (SAN) must include `*.<tunnel-domain>` per the [certificate requirements](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference#certificate-requirements).

</Step>

      <Step title="Register the CA certificate in the Console">
        On the tunnel detail page, scroll to the **Certificates** section and click **Add certificate**. Upload `data/ca.crt` directly with **Choose file** (the modal accepts `.pem`, `.crt`, and `.cer`), or paste its contents:

The tunnel's status flips to **Active** once a certificate is registered. See [Add a CA certificate](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#add-a-ca-certificate).
      </Step>

      <Step title="Write the proxy config">
        `tunnel_domain` is **required**: the proxy uses it to strip the domain suffix from incoming hostnames before looking up the subdomain in `routes`. `routes` is a flat map from subdomain to upstream URL, not a list.

The `echo:` route targets the [sample MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose#optional-use-a-sample-mcp-server); replace it with (or add) your own routes. See the [proxy configuration](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference#proxy-configuration) reference for all available fields.
      </Step>

      <Step title="Write docker-compose.yaml">
        The `network_mode: "service:mcp-proxy"` setting places [cloudflared](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) in the proxy's network namespace so that `localhost:8080` inside the cloudflared container reaches the proxy. The `--url http://localhost:8080` flag gives cloudflared its forwarding target; without that flag, cloudflared has no route for incoming requests and returns a 503.

If you're using the [sample MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose#optional-use-a-sample-mcp-server), append it as a service:

</Step>

      <Step title="Start the deployment">

</Step>
    </Steps>
  </Tab>
</Tabs>

The compose file reads `TUNNEL_TOKEN` from the host environment with no default, so the export must be repeated in every fresh shell and after a reboot.

For a multi-VM deployment, copy the `mcp-tunnel/` directory to each host, set `TUNNEL_TOKEN`, and run `docker compose up -d`. In the programmatic flow `TUNNEL_TOKEN` is `$(sudo cat data/tunnel-token)`; in the manual flow it's the value you copied from the Console. The same tunnel token and certificates work across all replicas.


## Verify the deployment

Source: https://platform.claude.com/llms-full.txt#verify-the-deployment

Verify end to end by calling an [upstream MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) from Anthropic's side: see [Use the tunneled MCP servers](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#use-the-tunneled-mcp-servers). With the [sample MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose#optional-use-a-sample-mcp-server), the routed URL is `https://echo.<your-tunnel-domain>/mcp`. If verification fails, see [Troubleshooting](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/troubleshooting).


## Upgrades

Source: https://platform.claude.com/llms-full.txt#upgrades

Run the commands in this section from inside the `mcp-tunnel/` deployment directory.

### Rotate the tunnel token

With programmatic access, increment `--token-version` in the `setup` service command, set the Workload Identity Federation identifiers, mint a fresh OIDC JWT, and re-run the setup component:

The `--token-version` argument is edited in `docker-compose.yaml` rather than passed on the command line so the new value persists for future runs of the setup component. The setup component authenticates with Workload Identity Federation; there is no API token to revoke.

Without programmatic access, click **Rotate token** on the tunnel detail page in the Console, then update the `TUNNEL_TOKEN` environment variable on each host and restart cloudflared (`docker compose up -d cloudflared`).

<Warning>
  Clicking **Rotate token** invalidates the current token immediately. Between that moment and updating `TUNNEL_TOKEN` on every host and restarting cloudflared, any host whose cloudflared restarts (crash, host reboot) cannot reconnect. Update each host promptly after rotating.
</Warning>

### Certificate renewal

You're responsible for monitoring expiry and renewing the server certificate before it expires.

With programmatic access:

The CLI arguments replace the `setup` service's `command` (the `init` arguments) but keep its `entrypoint`, so this runs `/setup renew-cert --output=dir:/data`.

<Tip>
  Pass `--renew-before=720h` to make the command a no-op when more than 30 days of validity remain. This makes it safe to run on a fixed schedule.
</Tip>

Without programmatic access, sign a new server certificate with your existing CA (the CA registered in the Console doesn't change) and replace `data/tls.crt`. Set `TUNNEL_DOMAIN` first if you're running this from a fresh shell.

In either flow the proxy polls `tls.cert_file` and reloads it automatically, so no restart is required.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-63

<CardGroup cols={2}>
  <Card title="Use the tunneled MCP servers" icon="link" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#use-the-tunneled-mcp-servers">
    Attach an upstream MCP server to a Managed Agent or the Messages API.
  </Card>

  <Card title="Security" icon="lock" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/security">
    Hardening guidance, credential rotation, and breach response.
  </Card>

  <Card title="Troubleshooting" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/troubleshooting">
    Diagnose connectivity, TLS, and routing issues.
  </Card>
</CardGroup>


---
title: Deploy MCP tunnels with Helm
url: https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-helm
description: Install the tunnel stack on a Kubernetes cluster using the Anthropic Helm chart.
---

<Note>
  MCP tunnels are in research preview. [Request access](https://claude.com/form/claude-managed-agents) to try them.
</Note>

The Anthropic Helm chart installs the [tunnel stack](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) as a single Deployment and attaches it to your tunnel: one the chart's setup hook creates for you, or an existing tunnel you created in the [Console](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#create-a-tunnel).


## Before you begin

Source: https://platform.claude.com/llms-full.txt#before-you-begin-3

You need:

* **A tunnel.** With programmatic access, the chart's setup hook creates one for you when you don't supply a tunnel ID; to attach to an existing tunnel instead, [create it in the Console](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#create-a-tunnel) and record the tunnel ID (`tnl_...`). Manual provisioning always starts from a Console-created tunnel; you'll also need its tunnel token and tunnel domain.

* **A way for the chart to authenticate to the Tunnels API.**

  * **[Programmatic access](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#credential-provisioning) (recommended).** The [setup component](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) authenticates through Workload Identity Federation, fetches the tunnel token, generates a CA, registers it with Anthropic, and stores everything in a Secret. You'll need a federation rule scoped to `workspace:manage_tunnels`.
  * **[Manual](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#credential-provisioning).** Skip programmatic access. You'll [get the tunnel token from the Console](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#get-the-connection-details), generate a CA and server certificate yourself, [register the CA in the Console](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#add-a-ca-certificate), and supply the credentials to the cluster as Secrets.

* **A Kubernetes cluster** you can deploy to with `helm` and `kubectl`. The **Without programmatic access** tab also uses `openssl` (1.1.1 or later).

* **Outbound network connectivity** from the cluster to `api.anthropic.com` (443 TCP) and the [tunnel edge](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) (7844 TCP and UDP). See the full [network requirements](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#network-requirements).

* **One or more MCP servers** running and reachable from the cluster on the addresses you'll configure under `gateway.config.routes`. If you don't have one yet, [use the sample server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-helm#optional-use-a-sample-mcp-server).


## Optional: Use a sample MCP server

Source: https://platform.claude.com/llms-full.txt#optional-use-a-sample-mcp-server-2

If you don't have an MCP server available for testing, use this minimal one:

The Install steps that follow note where to add the corresponding route.


## Install

Source: https://platform.claude.com/llms-full.txt#install-2

<Tabs>
  <Tab title="With programmatic access">
    The setup component exchanges the cluster's projected ServiceAccount token through your federation rule, fetches the tunnel token, generates a CA and server certificate, and registers the CA with Anthropic. A daily CronJob renews the server certificate as needed, so you don't handle any secrets by hand.

    <Steps>
      <Step title="Set up Workload Identity Federation for the cluster">
        Follow [Use WIF with Kubernetes](https://platform.claude.com/docs/en/manage-claude/wif-providers/kubernetes) to register your cluster's OIDC issuer and create a federation rule. The setup component runs under its own ServiceAccount in the release namespace; the exact name follows Helm's `fullname` convention, so for any release name other than `mcp-tunnel`, run `helm template <release> ... | grep -A2 'kind: ServiceAccount'` to confirm it before creating the rule. The rest of this guide assumes release name `mcp-tunnel` in namespace `mcp-tunnel`, where the ServiceAccount is `mcp-tunnel-setup`.

        | Field    | Value                                                |
        | -------- | ---------------------------------------------------- |
        | Subject  | `system:serviceaccount:mcp-tunnel:mcp-tunnel-setup`  |
        | Audience | `api.anthropic.com` (the chart's default; no scheme) |
        | Scope    | `workspace:manage_tunnels`                           |

        <Note>
          The chart's default audience is `api.anthropic.com` with no scheme, but the Console's federation-rule form suggests `https://api.anthropic.com`. The two must match byte-for-byte or authentication fails. Either set the rule's audience to `api.anthropic.com`, or set `api.wif.audience` in `values.yaml` to `https://api.anthropic.com`.
        </Note>

        If the tunnel is in a workspace other than the organization's default, also add the rule's service account as a member of that workspace under **Settings > Workspaces** (the Tunnels API authorizes against the service account's workspace memberships).

        Note the rule's ID (`fdrl_...`); you'll set it as `api.wif.federationRuleId`.

        <Note>
          The daily certificate-renewal CronJob uses a separate ServiceAccount (also derived from the Helm `fullname`) but does not call the Tunnels API; it renews the certificate locally and only needs Kubernetes RBAC, which the chart grants. The federation rule does not need to cover it.
        </Note>
      </Step>

      <Step title="Fetch the default values">

</Step>

      <Step title="Configure tunnel attachment and routes">
        Edit `values.yaml` and set the `api.wif.*` keys with the federation rule ID and organization ID, plus a `routes` entry for each [upstream MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components):

        ```yaml values.yaml
        api:
          wif:
            federationRuleId: "fdrl_..."
            organizationId: "00000000-0000-0000-0000-000000000000"
            # Set when the tunnel is in a non-default workspace and the
            # rule's service account is a member of that workspace.
            # workspaceId: "wrkspc_..."

        tunnel:
          # Leave empty to have the setup hook create a tunnel during install.
          # Set to attach to an existing tunnel from the Console.
          id: ""
          # Increment to rotate the tunnel token on the next upgrade.
          # See the "Rotate the tunnel token" section.
          tokenVersion: "1"

        gateway:
          config:
            routes:
              docs: http://docs-mcp.internal:8080
              search: http://search-mcp.internal:8080

bash
        helm template mcp-tunnel \
          oci://us-docker.pkg.dev/anthropic-public-registry/charts/mcp-tunnel \
          --version 2.0.2 \
          -n mcp-tunnel \
          -f values.yaml > rendered.yaml

bash
        helm install mcp-tunnel \
          oci://us-docker.pkg.dev/anthropic-public-registry/charts/mcp-tunnel \
          --version 2.0.2 \
          --namespace mcp-tunnel --create-namespace \
          -f values.yaml

bash
        kubectl -n mcp-tunnel get secret mcp-tunnel \
          -o jsonpath='{.data.tunnel-domain}' | base64 -d

bash
        export TUNNEL_DOMAIN=YOUR_TUNNEL_DOMAIN_HERE
        mkdir -p mcp-tunnel/data
        cd mcp-tunnel

        # Self-signed CA. Explicit extensions so it satisfies the certificate
        # requirements regardless of distro openssl.cnf defaults.
        openssl req -x509 -newkey rsa:2048 -nodes \
          -keyout data/ca.key -out data/ca.crt \
          -days 3650 -subj "/CN=mcp-tunnel-ca" \
          -addext "basicConstraints=critical,CA:TRUE" \
          -addext "keyUsage=critical,keyCertSign,cRLSign" \
          -addext "subjectKeyIdentifier=hash"

        # Extension file for the server certificate. Using -extfile (instead of
        # -copy_extensions, which is OpenSSL 3.0+ only) keeps this working on
        # OpenSSL 1.1.x.
        cat > data/tls.ext <<EOF
        subjectAltName = DNS:${TUNNEL_DOMAIN},DNS:*.${TUNNEL_DOMAIN}
        authorityKeyIdentifier = keyid,issuer
        extendedKeyUsage = serverAuth
        EOF

        # Server certificate signed by the CA
        openssl req -newkey rsa:2048 -nodes \
          -keyout data/tls.key -out /tmp/server.csr \
          -subj "/CN=${TUNNEL_DOMAIN}"
        openssl x509 -req -in /tmp/server.csr \
          -CA data/ca.crt -CAkey data/ca.key -CAcreateserial \
          -out data/tls.crt -days 90 \
          -extfile data/tls.ext

bash
        kubectl create namespace mcp-tunnel --dry-run=client -o yaml | kubectl apply -f -
        kubectl -n mcp-tunnel create secret generic mcp-tunnel-token \
          --from-literal=tunnel-token='eyJ...'
        kubectl -n mcp-tunnel create secret generic mcp-tunnel-cert \
          --from-file=tls.crt=data/tls.crt \
          --from-file=tls.key=data/tls.key

bash
        helm show values \
          oci://us-docker.pkg.dev/anthropic-public-registry/charts/mcp-tunnel \
          --version 2.0.2 > values.yaml

yaml values.yaml
        setup:
          enabled: false

        external:
          tunnelTokenSecretName: mcp-tunnel-token   # must contain key: tunnel-token
          serverCertSecretName: mcp-tunnel-cert     # must contain keys: tls.crt, tls.key

        gateway:
          config:
            # Required when setup.enabled is false. Replace the placeholder with
            # the $TUNNEL_DOMAIN value you exported earlier. When setup.enabled
            # is true the chart injects this from the Secret as a -tunnel-domain
            # flag instead.
            tunnel_domain: YOUR_TUNNEL_DOMAIN_HERE
            routes:
              docs: http://docs-mcp.internal:8080
              search: http://search-mcp.internal:8080

bash
        helm template mcp-tunnel \
          oci://us-docker.pkg.dev/anthropic-public-registry/charts/mcp-tunnel \
          --version 2.0.2 \
          -n mcp-tunnel \
          -f values.yaml > rendered.yaml

bash
        helm install mcp-tunnel \
          oci://us-docker.pkg.dev/anthropic-public-registry/charts/mcp-tunnel \
          --version 2.0.2 \
          --namespace mcp-tunnel --create-namespace \
          -f values.yaml
        ```
      </Step>
    </Steps>
  </Tab>
</Tabs>


## Verify the deployment

Source: https://platform.claude.com/llms-full.txt#verify-the-deployment-2

Verify end to end from Anthropic's side: use `https://<route>.<your-tunnel-domain>/<path>` in a Managed Agent session or a Messages API request, where `<route>` is a key from `gateway.config.routes` and `<path>` is whatever the upstream MCP server serves at. With the [sample MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-helm#optional-use-a-sample-mcp-server), that's `https://echo.<your-tunnel-domain>/mcp`. See [Use the tunneled MCP servers](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#use-the-tunneled-mcp-servers) for the request shapes.

If that fails, check the pod logs (`kubectl -n mcp-tunnel logs deploy/mcp-tunnel -c mcp-proxy` and `-c cloudflared`) and consult [Troubleshooting](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/troubleshooting).


## Optional configuration

Source: https://platform.claude.com/llms-full.txt#optional-configuration

### Restrict egress with NetworkPolicy

Ingress to the proxy pod is denied by default (`networkPolicy.ingress.enabled: true`). To additionally restrict pod egress, set `networkPolicy.egress.enabled: true` and populate `networkPolicy.egress.mcpServers` with pod label selectors or CIDR ranges that cover your upstream MCP servers. Egress from cloudflared to the tunnel edge is allowed separately through `networkPolicy.egress.cloudflaredEgressCIDRs`.

### Tune the proxy

Fields under `gateway.config.*` pass through to the proxy configuration file. Common adjustments include `upstream.allowed_ips`, `log_level`, and `upstream.tls`. See the [proxy configuration](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference#proxy-configuration) reference for the full field list. The chart always sets `listen_addr`, `tls.cert_file`, and `tls.key_file`; setting them in `gateway.config` has no effect.

### Supply your own OIDC token

By default the chart projects a Kubernetes ServiceAccount token for the setup component. To use a token from a different identity provider (such as [SPIFFE](https://platform.claude.com/docs/en/manage-claude/wif-providers/spiffe), Vault, or a cloud-SDK sidecar), mount it with `setup.extraVolumes` and `setup.extraVolumeMounts`. Then point `api.wif.tokenFile` at the mount path. The chart sets `ANTHROPIC_IDENTITY_TOKEN_FILE` to that path, and the setup component reads the token from there.


## Upgrades

Source: https://platform.claude.com/llms-full.txt#upgrades-2

Always pass `--version` to `helm upgrade` so you don't pull a newer chart unexpectedly.

### Upgrade from chart 1.x

Chart 2.0.0 moves the tunnel ID from `api.wif.tunnelId` to `tunnel.id`. Before upgrading, edit your `values.yaml`: move the `tnl_...` value to `tunnel.id` and remove `api.wif.tunnelId`. Leaving `tunnel.id` unset is safe (the setup component reuses the tunnel ID already stored in the `mcp-tunnel` Secret on re-run), but the explicit move keeps your `values.yaml` accurate. Also update your federation rule's scope from `org:manage_tunnels` to `workspace:manage_tunnels` in the Console.

### Change configuration

For routine changes such as routes, replica count, or NetworkPolicy:

<Warning>
  Maintain a complete `values.yaml` rather than relying on `--reuse-values`. Helm's deep-merge behavior can silently fail to remove deleted routes.
</Warning>

### Rotate the tunnel token

With programmatic access, increment `tunnel.tokenVersion` in `values.yaml` and upgrade with `--set setup.force=true`. The setup component only re-runs on upgrades when forced:

The setup component authenticates with Workload Identity Federation; there is no API token to revoke.

Without programmatic access, click **Rotate token** on the tunnel detail page in the Console, then update the `mcp-tunnel-token` Secret:

<Warning>
  Clicking **Rotate token** invalidates the current token immediately. Until the Secret is updated and the rollout completes, any pod that restarts with the old token (eviction, node drain, OOM) cannot reconnect. Update the Secret promptly after rotating; for stricter availability requirements, use programmatic access so the chart handles the rotation atomically.
</Warning>

### Certificate renewal

The chart provides automation, but you remain responsible for monitoring expiry and confirming renewal completes.

With programmatic access, certificate renewal is automatic. The chart deploys a CronJob (named after the Helm `fullname`, suffixed `-cert-renew`) that runs `setup renew-cert` daily (at `serverCert.cronSchedule`, default `0 0 * * *` UTC). The job is a no-op unless the certificate is within `serverCert.renewBefore` of expiry (default 30 days). Renewal is local: the job signs a fresh certificate with the CA already stored in the Secret, makes no API calls, and only needs the Kubernetes RBAC the chart grants. The proxy hot-reloads the certificate from the Secret mount, so no Deployment restart is needed.

Without programmatic access there is no CronJob. From inside the `mcp-tunnel/` directory you kept after install, sign a fresh server certificate with the existing CA (do not regenerate the CA):

The proxy hot-reloads the certificate from the Secret mount.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-64

<CardGroup cols={2}>
  <Card title="Use the tunneled MCP servers" icon="link" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#use-the-tunneled-mcp-servers">
    Attach an upstream MCP server to a Managed Agent or the Messages API.
  </Card>

  <Card title="Security" icon="lock" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/security">
    Hardening guidance, credential rotation, and breach response.
  </Card>

  <Card title="Troubleshooting" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/troubleshooting">
    Diagnose connectivity, TLS, and routing issues.
  </Card>
</CardGroup>


---
title: Manage tunnels in the Console
url: https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console
description: Create tunnels, register CA certificates, retrieve the tunnel token, and attach tunneled MCP servers to agents from the Claude Console.
---

<Note>
  MCP tunnels are in research preview. [Request access](https://claude.com/form/claude-managed-agents) to try them.
</Note>

This page covers the Console side of an MCP tunnels deployment: creating a tunnel, registering your CA certificate, retrieving the tunnel token, and attaching the [upstream MCP servers](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) to an agent. [Deploy MCP tunnels with Helm](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-helm) and [Deploy MCP tunnels with Docker Compose](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose) cover running the [tunnel stack](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) inside your network.


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-5

* **One or more MCP servers** running in your private network. The tunnel routes traffic to them; it does not host them. See [Remote MCP servers](https://platform.claude.com/docs/en/agents-and-tools/remote-mcp-servers) for examples you can deploy.

* **A Console role with the Manage tunnels permission**, so you can create and archive tunnels, rotate the token, and manage certificates. Organization admins and owners have it by default; custom roles and per-account grants can also include it. Roles without it have read-only access to the **MCP tunnels** page and tunnel details.

* **A way for your stack to authenticate to the Tunnels API.** Choose one:

  * **[Programmatic access](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#credential-provisioning) (recommended).** Set up [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) during tunnel creation so your stack mints short-lived API tokens from your identity provider, fetches the tunnel token, and generates and registers a CA certificate automatically. Requires permission to manage federation rules, a registered OIDC issuer, and a federation rule with the `workspace:manage_tunnels` scope.
  * **[Manual](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#credential-provisioning).** Skip programmatic access. After creating the tunnel, [get the tunnel token](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#get-the-connection-details), generate and [register a CA certificate](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#add-a-ca-certificate) yourself, and supply the token and your server certificate to your tunnel stack as secrets.


## Create a tunnel

Source: https://platform.claude.com/llms-full.txt#create-a-tunnel

<Steps>
  <Step title="Open the MCP tunnels page">
    In the Console sidebar, go to **Manage > MCP tunnels**. Tunnels are workspace-scoped; the new tunnel belongs to the workspace currently selected in the Console, so switch workspaces first if you want it elsewhere.
  </Step>

  <Step title="Name the tunnel">
    Click **New tunnel** and enter a name in the **Create tunnel** dialog. The name is required and identifies the tunnel in the list, on the detail page, and in the agent MCP server picker. A domain of the form `abcd1234.tunnel.anthropic.com` is assigned automatically.
  </Step>

  <Step title="Optionally set up programmatic access">
    If your role can manage federation rules, a **Set up programmatic access** toggle appears (off by default). If not, the Console shows a notice in its place and your tunnel stack uses the manual flow instead. The rest of the create flow is the same either way.

    Programmatic access relies on [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation); read that page first if federation issuers, rules, and service accounts are unfamiliar. To turn the toggle on you need:

    1. **A registered OIDC issuer** for the identity provider your stack presents tokens from (such as a Kubernetes cluster, AWS IAM, Google Cloud, or GitHub Actions). Register one under **Settings > Workload identity > Issuers** if your organization doesn't have one.
    2. **A federation rule with the `workspace:manage_tunnels` scope.** Turning on the toggle reveals a **Federation rule** picker. Choose an existing rule with that scope, or click **Create federation rule** to create one inline.
    3. **The rule's service account added to this workspace.** The Tunnels API authorizes against the service account's workspace memberships. If you're creating the tunnel in a workspace other than the organization's default, add the service account under **Settings > Workspaces** and pass the workspace ID at deploy time (`api.wif.workspaceId` for Helm, `ANTHROPIC_WORKSPACE_ID` for Compose).

    Skipping this step is fully supported; both deploy guides have a **Without programmatic access** tab.
  </Step>

  <Step title="Create the tunnel">
    Click **Create tunnel**. The Console provisions the tunnel and opens the detail page.
  </Step>

  <Step title="Record the deployment identifiers">
    Both deploy paths need:

    * The **tunnel ID** (`tnl_...`), shown on the tunnel detail page.
    * The **tunnel domain** (`abcd1234.tunnel.anthropic.com`), shown on the tunnel detail page. Used as the proxy's `tunnel_domain` and in the server certificate's SAN.

    What else you need depends on the [credential-provisioning mode](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#credential-provisioning):

    | With programmatic access                                                                                                                                                   | Without programmatic access                                                                                                                                                                                                                         |
    | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | The **federation rule ID** (`fdrl_...`) of the rule you selected. The rule is org-level, not stored on the tunnel; find it under **Settings > Workload identity > Rules**. | The **tunnel token**, revealed with the eye icon next to **Token** on the detail page. Treat it as a secret. See [Get the connection details](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#get-the-connection-details). |
    | The **organization ID** (a UUID), shown under **Settings > Organization**.                                                                                                 | A **CA certificate** that you generate and [register on the tunnel](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#add-a-ca-certificate).                                                                                 |

    With programmatic access, your stack fetches the tunnel token through the Tunnels API, generates the CA and server certificate locally (the private key never leaves your environment), and registers only the CA's public certificate with Anthropic. You're still responsible for securing the private keys and renewing the server certificate before it expires.
  </Step>
</Steps>

Your organization can have up to 10 active tunnels. Creating a tunnel does not establish any connectivity; that happens once your stack dials in with the tunnel token and a CA certificate is registered.


## Get the connection details

Source: https://platform.claude.com/llms-full.txt#get-the-connection-details

Open the tunnel. The detail page shows a **Connection** section with the domain and token and a **Certificates** section.

| Field      | Description                                                                                                                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Domain** | Copy the assigned `abcd1234.tunnel.anthropic.com` value. Your proxy's routes are subdomains of this domain.                                                                                                         |
| **Token**  | Click the eye icon (**Show token**) to fetch the tunnel token, then use the copy icon to copy it into your tunnel stack's secret store. Click **Rotate token** to invalidate the current token and issue a new one. |

<Note>
  Every reveal and rotation is recorded in your organization's [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) activity log. Rotation does not sever cloudflared connections that are already established, so you can rotate, redeploy with the new value, and let the old connections drain.
</Note>


## Add a CA certificate

Source: https://platform.claude.com/llms-full.txt#add-a-ca-certificate

Anthropic verifies [inner TLS](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) to your [proxy](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) against the CA certificates you register on the tunnel. A tunnel with no active certificates cannot accept connections, and does not appear in the agent MCP server picker until one is registered.

<Steps>
  <Step title="Find the Certificates section">
    On the tunnel's detail page, scroll to the **Certificates** section and click **Add certificate**.
  </Step>

  <Step title="Provide the certificate">
    Click **Choose file** to select a `.pem`, `.crt`, or `.cer` file, drag the file onto the text area, or paste the PEM block directly. The modal rejects private-key material and content that isn't a `-----BEGIN CERTIFICATE-----` block. The file must be 8 kB or smaller.
  </Step>

  <Step title="Add the certificate">
    Click **Add certificate**. The fingerprint and expiry appear in the certificate list, and the slot count on the section header increments.
  </Step>
</Steps>

A tunnel holds up to two active certificates so you can rotate without downtime: register the new certificate alongside the old one, redeploy your proxy with the new key pair, confirm traffic is flowing, then click **Revoke** on the old certificate's row. Revoked certificates remain visible in the list with a **Revoked** badge.


## Deploy the tunnel stack

Source: https://platform.claude.com/llms-full.txt#deploy-the-tunnel-stack

The tunnel exists in the Console, but no traffic flows until the tunnel stack is running inside your network and dialed in with the tunnel token. Follow one of the deploy guides:

<CardGroup cols={2}>
  <Card title="Deploy with Docker Compose" icon="cube" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-compose">
    Run the tunnel stack on a single host. Both programmatic-access and manual flows.
  </Card>

  <Card title="Deploy with Helm" icon="stack" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-helm">
    Run the tunnel stack on a Kubernetes cluster. Both programmatic-access and manual flows.
  </Card>
</CardGroup>


## Use the tunnel in an agent

Source: https://platform.claude.com/llms-full.txt#use-the-tunnel-in-an-agent

Once your stack is running and has one or more MCP servers configured, attach an upstream MCP server to a Managed Agent session. To call the same servers from the Messages API instead, see [Use the tunneled MCP servers](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#use-the-tunneled-mcp-servers).

<Note>
  The picker only shows tunnels with at least one active certificate. A tunnel that still shows **Needs certificate** in the **MCP tunnels** list does not appear in the dropdown; register a CA certificate first. The picker is also workspace-scoped: it lists tunnels in the same workspace as the session, not other workspaces.
</Note>

<Steps>
  <Step title="Open the New session modal">
    Go to **Managed Agents > Sessions** and click **New session**.
  </Step>

  <Step title="Define an inline agent">
    In the agent picker, choose **Create new agent** so you can edit the MCP server list directly.
  </Step>

  <Step title="Add the MCP server">
    Click **+ MCP Server** and open the dropdown. Tunnels created in the current workspace appear at the top of the list, above the public connector catalog. Select the tunnel that fronts the server you want to reach.
  </Step>

  <Step title="Supply the routing">
    The card shows two optional fields: **Subdomain** (prefixed to the tunnel domain) and **Path** (appended after it). Fill in one or both, depending on how your proxy's routes are configured. The **Resolves to** line shows the full MCP server URL that the agent connects to.
  </Step>
</Steps>

<Note>
  The tunnel carries traffic; it does not authenticate to the upstream MCP server. Configure OAuth or bearer auth on the MCP server the same way as for any other MCP server.
</Note>


## Archive a tunnel

Source: https://platform.claude.com/llms-full.txt#archive-a-tunnel

Archiving immediately stops the tunnel from accepting connections and is permanent.

In the **MCP tunnels** list, open the row menu for the tunnel and choose **Archive**. Archived tunnels remain visible when you filter the list by **Archived** or **All**.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-65

<CardGroup cols={2}>
  <Card title="Deploy with Helm" icon="stack" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/deploy-helm">
    Install on a Kubernetes cluster using the Anthropic Helm chart.
  </Card>

  <Card title="Security" icon="lock" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/security">
    Hardening guidance, credential rotation, and breach response.
  </Card>
</CardGroup>


---
title: MCP tunnels reference
url: https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference
description: Proxy configuration fields, the Tunnels REST API, certificate requirements, and the setup component.
---

<Note>
  MCP tunnels are in research preview. [Request access](https://claude.com/form/claude-managed-agents) to try them.
</Note>


## Proxy configuration

Source: https://platform.claude.com/llms-full.txt#proxy-configuration

The [proxy](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) reads its configuration from `/etc/mcp-gateway/config.yaml` (Compose) or the rendered ConfigMap (Helm, populated from `gateway.config.*`).

| Field                             | Description                                                                                                                                                                                                     | Default                                         |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `listen_addr`                     | Address and port to listen on.                                                                                                                                                                                  | Required                                        |
| `log_level`                       | Logging verbosity: `debug`, `info`, `warn`, or `error`.                                                                                                                                                         | `info`                                          |
| `shutdown_timeout`                | How long to wait for in-flight requests during graceful shutdown.                                                                                                                                               | `30s`                                           |
| `tunnel_domain`                   | Base domain assigned to the tunnel. When set, route lookup strips this suffix from incoming hostnames so `routes` keys can be bare subdomains (`wiki`). When empty, `routes` keys must be exact full hostnames. | Required when `routes` keys are bare subdomains |
| `tls.cert_file`                   | Path to the server TLS certificate.                                                                                                                                                                             | Required                                        |
| `tls.key_file`                    | Path to the server TLS private key.                                                                                                                                                                             | Required                                        |
| `routes`                          | Map of subdomain or full hostname to upstream URL. See [Route matching](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference#route-matching).                                             | Required                                        |
| `upstream.allowed_ips`            | IPv4 CIDR ranges or single addresses the proxy is permitted to connect to. Mutually exclusive with `disable_ip_validation`.                                                                                     | RFC1918 private ranges                          |
| `upstream.disable_ip_validation`  | Disable upstream IP validation entirely. Mutually exclusive with `allowed_ips`.                                                                                                                                 | `false`                                         |
| `upstream.tls.ca_file`            | CA bundle for validating upstream TLS.                                                                                                                                                                          | None                                            |
| `upstream.tls.include_system_cas` | Also trust the system CA bundle for upstream TLS.                                                                                                                                                               | `false`                                         |

For `https://` upstream routes, set at least one of `upstream.tls.ca_file` or `upstream.tls.include_system_cas`; otherwise the proxy has no trust anchor for the upstream certificate.

### Route matching

`routes` is a flat string map (`map[string]string`), not a list. The proxy looks up the incoming hostname by exact match first, then by stripping the `tunnel_domain` suffix and matching the remaining subdomain. The match considers only the hostname; the request path and query string are forwarded to the [upstream MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) unchanged.

Each upstream value must be exactly `scheme://host:port`. The port is mandatory. Including a path is rejected at config load with `invalid upstream (must be scheme://host:port)`.


## Tunnels API

Source: https://platform.claude.com/llms-full.txt#tunnels-api

The Tunnels REST API lives at `/v1/tunnels` and supports creating, listing, and archiving tunnels, registering CA certificates, and revealing or rotating the tunnel token. See the [Tunnels API reference](https://platform.claude.com/docs/en/api/beta/tunnels/list) for all endpoints, request and response schemas, and examples.

<Note>
  The previous Admin API surface at `/v1/organizations/tunnels` (beta header `mcp-tunnels-2026-05-19`, scope `org:manage_tunnels`) continues to work during a migration window and remains documented in the [Admin API reference](https://platform.claude.com/docs/en/api/admin/mcp_tunnels) with a deprecation notice. To migrate, update the path to `/v1/tunnels`, the beta header to `mcp-tunnels-2026-06-22`, and your WIF token scope to `workspace:manage_tunnels`.
</Note>

<Warning>
  All MCP tunnels endpoints require a bearer token with the `workspace:manage_tunnels` scope obtained through [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation). Admin API keys are not accepted.
</Warning>

Required headers on every request:

| Header              | Value                                      |
| ------------------- | ------------------------------------------ |
| `Authorization`     | `Bearer <token>` (the WIF-exchanged token) |
| `anthropic-version` | `2023-06-01`                               |
| `anthropic-beta`    | `mcp-tunnels-2026-06-22`                   |


## Certificate requirements

Source: https://platform.claude.com/llms-full.txt#certificate-requirements

The [setup component](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) generates compliant certificates automatically. These requirements apply only if you issue certificates through your own PKI.

### CA certificate

Upload with `POST /v1/tunnels/{tunnel_id}/certificates`. A tunnel can hold up to two active CA certificates at a time, which allows zero-downtime rotation.

* PEM-encoded, single certificate, up to 8 kB.
* `BasicConstraints` extension present with `CA:TRUE`, marked critical.
* `SubjectKeyIdentifier` extension present.
* `KeyUsage` includes `keyCertSign`.
* Within its validity period.
* RSA 2048-bit or larger, or ECDSA P-256 or larger, with a SHA-256 or stronger signature.

### Server certificate

Presented by the proxy during [inner TLS](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components).

* Signed directly by a registered CA (no intermediates).
* `AuthorityKeyIdentifier` extension present and matching the CA's `SubjectKeyIdentifier`.
* Subject Alternative Name includes a DNS name matching `<route>.<tunnel-domain>`. A wildcard `*.<tunnel-domain>` covers all routes.
* If the `ExtendedKeyUsage` extension is present, it includes `serverAuth`.
* Within its validity period.
* RSA 2048-bit or larger, or ECDSA P-256 or larger, with a SHA-256 or stronger signature.

The setup component generates an ECDSA P-256 CA with five-year validity and an RSA 4096-bit server certificate with a wildcard SAN and 90-day validity.


## Setup component

Source: https://platform.claude.com/llms-full.txt#setup-component

The setup component ships inside the `mcp-proxy` image as the `setup` binary. Run it with `docker compose run --rm setup <subcommand>` (Compose) or rely on the chart's hooks and CronJobs (Helm).

### `setup init`

Attaches to an existing tunnel (or creates one when no tunnel ID is supplied), then generates a CA and server certificate, registers the CA, retrieves the tunnel token, and writes all outputs to the destination.

| Flag              | Description                                                                                                                                                           | Default                                                                                      |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `--api-url`       | Claude API base URL. Also read from `API_URL`.                                                                                                                        | Required                                                                                     |
| `--tunnel-id`     | Tunnel ID to attach to (`tnl_...`). Also read from `TUNNEL_ID`. When omitted, a new tunnel is created; a tunnel ID already stored in the output is reused on re-runs. | None (create a tunnel)                                                                       |
| `--output`        | Output destination: `dir:/path` or `k8s-secret:NAME`. The Helm chart passes `k8s-secret:<release>`.                                                                   | `k8s-secret:mcp-tunnel` (auto-detected when running in a Kubernetes pod; required otherwise) |
| `--cert-duration` | Server certificate validity period.                                                                                                                                   | `2160h` (90 days)                                                                            |
| `--token-version` | Change-detection string. A new value triggers token rotation on re-run. The Helm chart and the Compose example both pass `1` as the initial value.                    | None                                                                                         |

The command authenticates through [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation). It reads `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`, `ANTHROPIC_WORKSPACE_ID` (optional), and exactly one of `ANTHROPIC_IDENTITY_TOKEN_FILE` or `ANTHROPIC_IDENTITY_TOKEN`. See the [WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference) for the current semantics of these variables; the setup component derives the service account from the federation rule, so it does not require `ANTHROPIC_SERVICE_ACCOUNT_ID` separately.

### `setup renew-cert`

Issues a new server certificate signed by the stored CA. Makes no API calls.

| Flag              | Description                                                                                         | Default                                                                                      |
| ----------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `--output`        | Output destination: `dir:/path` or `k8s-secret:NAME`. The Helm chart passes `k8s-secret:<release>`. | `k8s-secret:mcp-tunnel` (auto-detected when running in a Kubernetes pod; required otherwise) |
| `--cert-duration` | New certificate validity period.                                                                    | `2160h` (90 days)                                                                            |
| `--renew-before`  | Skip renewal if the existing certificate has more than this duration remaining.                     | `0` (always renew)                                                                           |

Setting `--renew-before=720h` makes the command a no-op when more than 30 days of validity remain, so it's safe to run on a fixed schedule.


---
title: MCP tunnels security
url: https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/security
description: Hardening guidance, credential rotation, breach response, and teardown for MCP tunnel deployments.
---

<Note>
  MCP tunnels are in research preview. [Request access](https://claude.com/form/claude-managed-agents) to try them.
</Note>

The tunnel architecture provides strong defaults (outbound-only connectivity, end-to-end encryption, and IP validation), but the overall security of your [tunnel stack](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) also depends on how you configure and operate it. This page covers recommended hardening, breach response, and how to decommission a tunnel.


## Best practices

Source: https://platform.claude.com/llms-full.txt#best-practices-8

* **Require OAuth on every MCP server.** Configure each [upstream MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) to require OAuth as described in the [MCP authorization spec](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization). OAuth provides defense in depth on top of the tunnel's transport authentication and enables user-level authorization at the data layer.
* **Enable SSO for your organization.** Tunnels, federation rules, and service accounts are managed in the Claude Console. SSO enforces your identity provider's session controls on the admins who can change them.
* **Restrict `upstream.allowed_ips`.** Use the smallest CIDR ranges that cover your MCP servers. This is the [proxy](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components)'s primary SSRF defense.
* **Monitor logs.** Alert on warnings, errors, and unusual traffic patterns from the tunnel stack.
* **Rotate credentials.** Rotate the server certificate and tunnel token on a regular schedule, and immediately if you suspect compromise.
* **Keep images updated.** Track new proxy releases and pin images by SHA-256 digest.
* **Limit network reach.** The proxy and [cloudflared](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) should only be able to reach the destinations listed in the [network requirements](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#network-requirements). Use NetworkPolicy (Kubernetes) or host firewall rules (Compose).
* **Limit MCP server scope.** Each server should expose only the tools and data required for its purpose.
* **Protect credentials at rest.** Apply your organization's secrets-management practices to private keys and tunnel tokens.


## Respond to a suspected breach

Source: https://platform.claude.com/llms-full.txt#respond-to-a-suspected-breach

If you believe your tunnel token, TLS keys, or proxy host has been compromised:

<Steps>
  <Step title="Stop the tunnel stack">
    <Tabs>
      <Tab title="Helm">

</Tab>

      <Tab title="Docker Compose">

</Tab>
    </Tabs>
  </Step>

  <Step title="Detach the upstream MCP servers">
    Remove the upstream MCP servers from any Managed Agent sessions that use them, and stop passing their URLs in the `mcp_servers` block of Messages API requests.
  </Step>

  <Step title="Archive the tunnel">
    Archiving invalidates the tunnel token and detaches the domain. In the Console, [archive the tunnel](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#archive-a-tunnel) from the **MCP tunnels** list. To archive over the API instead, see [Archive a tunnel](https://platform.claude.com/docs/en/api/beta/tunnels/archive).
  </Step>

  <Step title="Contact Anthropic">
    Report the suspected compromise to Anthropic support.
  </Step>

  <Step title="Rotate downstream credentials">
    Re-provision a fresh tunnel and rotate any OAuth tokens that the affected MCP servers issued.
  </Step>

  <Step title="Review logs before restoring service">
    Inspect proxy, cloudflared, and MCP server logs for the window of suspected compromise before bringing the new tunnel online.
  </Step>
</Steps>


## Tear down a tunnel

Source: https://platform.claude.com/llms-full.txt#tear-down-a-tunnel

Follow these steps to decommission a tunnel and remove all stored credentials.

<Steps>
  <Step title="Stop the tunnel stack">
    <Tabs>
      <Tab title="Helm">

</Tab>

      <Tab title="Docker Compose">

</Tab>
    </Tabs>
  </Step>

  <Step title="Archive the tunnel">
    In the Console, [archive the tunnel](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/console#archive-a-tunnel) from the **MCP tunnels** list.
  </Step>

  <Step title="Remove stored credentials">
    <Tabs>
      <Tab title="Helm">
        With programmatic access, the setup component created a single Secret named after the release. Without programmatic access, you created `mcp-tunnel-token` and `mcp-tunnel-cert` yourself. Delete whichever apply:

</Tab>

      <Tab title="Docker Compose">
        Private keys and certificates live in `data/`. The tunnel token lives in `data/tunnel-token` (programmatic flow) or in your shell environment (manual flow). The `config/` directory and `docker-compose.yaml` contain no secrets; keep them if you plan to re-provision, or remove them as well.

</Tab>
    </Tabs>
  </Step>
</Steps>


---
title: Troubleshoot MCP tunnels
url: https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/troubleshooting
description: Diagnose connectivity, TLS, IP validation, and OAuth routing issues in a tunnel stack.
---

<Note>
  MCP tunnels are in research preview. [Request access](https://claude.com/form/claude-managed-agents) to try them.
</Note>

A request through the tunnel can fail at one of three layers; diagnose them in order: the outbound connection to the [tunnel edge](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components), the [inner TLS](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) from Anthropic to your [proxy](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components), then routing and IP validation toward the [upstream MCP server](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components).


## Quick reference

Source: https://platform.claude.com/llms-full.txt#quick-reference-2

| Symptom                                                                                                                                                        | Cause                                                                                               | Fix                                                                                                                                                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tunnel doesn't appear in the agent **+ MCP Server** picker                                                                                                     | The picker only lists tunnels in the session's workspace that have at least one active certificate. | Register a CA certificate, or open the session in the workspace the tunnel was created in.                                                                            |
| Caller sees HTTP 500; [cloudflared](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) logs `No ingress rules were defined` | cloudflared has no local target.                                                                    | Add `--url http://localhost:8080` and `network_mode: "service:mcp-proxy"` to the cloudflared service.                                                                 |
| Proxy logs `no route for host`                                                                                                                                 | `tunnel_domain` doesn't match the assigned domain, or `config.yaml` was edited without restarting.  | Set `tunnel_domain` to the exact domain shown on the tunnel detail page, then restart the proxy (`docker compose restart mcp-proxy`).                                 |
| Proxy logs `IP validation failed: <ip> is not a private address`                                                                                               | Upstream MCP server resolves outside RFC1918.                                                       | See [Upstream IP validation](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/troubleshooting#upstream-ip-validation).                                |
| Proxy exits with `cannot unmarshal !!seq into map[string]string`                                                                                               | `routes` is a YAML list.                                                                            | Use `routes: { name: http://host:port }`.                                                                                                                             |
| Proxy exits with `open /data/tls.key: permission denied`                                                                                                       | The key is `0600`; the proxy container runs non-root.                                               | `chmod 644 data/tls.key`.                                                                                                                                             |
| `curl https://<proxy>:8080` fails with `wrong version number`                                                                                                  | Expected; the listener is plaintext WebSocket. TLS happens inside the WS stream.                    | Verify through a [Managed Agent or the Messages API](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview#use-the-tunneled-mcp-servers) instead. |

The following sections cover failures that need more than a one-line fix.


## OAuth fails behind a source-IP allowlist

Source: https://platform.claude.com/llms-full.txt#oauth-fails-behind-a-source-ip-allowlist

OAuth flows fail when your authorization server's source-IP allowlist blocks Anthropic's backend from reaching `/token`, `/register`, and the discovery endpoints. If you'd rather not allowlist Anthropic's egress ranges, you can route the backend-to-backend OAuth calls through the tunnel while keeping the browser-facing `/authorize` endpoint on your existing public hostname.

<Steps>
  <Step title="Add a proxy route for the authorization server">

Restart the proxy after editing `routes` (`docker compose restart mcp-proxy`, or `helm upgrade`).
  </Step>

  <Step title="Serve split-endpoint discovery metadata">
    Your authorization server's `/.well-known/oauth-authorization-server` response should point `authorization_endpoint` at your existing allowlisted hostname and everything else at the tunnel:

</Step>

  <Step title="Point the MCP server at the tunnel issuer">
    Your MCP server's `/.well-known/oauth-protected-resource` response should reference the tunnel hostname as its authorization server:

</Step>
</Steps>

With this configuration, the user's browser hits `/authorize` on your existing hostname (which your allowlist already permits), while Anthropic's backend reaches `/token`, `/register`, and the discovery documents through the tunnel.


## Setup component authentication failures

Source: https://platform.claude.com/llms-full.txt#setup-component-authentication-failures

The [setup component](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/concepts#components) (Helm Job or Compose `setup` service) authenticates to the Tunnels API by exchanging an OIDC JWT through your federation rule. When the exchange fails, see [Troubleshoot a failed exchange](https://platform.claude.com/docs/en/manage-claude/wif-reference#troubleshoot-a-failed-exchange) in the Workload Identity Federation reference; the failure modes (subject, audience, issuer, JWKS, lifetime) are the same.

Tunnels-specific causes:

* The chart's default audience is `api.anthropic.com` (no scheme). If your rule's audience is `https://api.anthropic.com`, set `api.wif.audience` to match.
* A `403` from the Tunnels API after a successful exchange means the rule's scope doesn't include `workspace:manage_tunnels`, or the rule's service account isn't a member of the tunnel's workspace. Set the scope and add the service account to the workspace.

On Helm, the setup component runs as a pre-install hook Job. On failure, the Job is left behind for inspection (`kubectl logs job/mcp-tunnel-setup -n mcp-tunnel`). Helm doesn't manage hook resources, so delete it before retrying:
