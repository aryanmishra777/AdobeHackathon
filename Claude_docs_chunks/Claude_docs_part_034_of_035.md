# platform.claude.com Documentation (Part 34 of 35)

## Request and response format

Source: https://platform.claude.com/llms-full.txt#request-and-response-format

### Request size limits

| Endpoint                                                                                      | Maximum request size |
| --------------------------------------------------------------------------------------------- | -------------------- |
| Messages, Token Counting                                                                      | 32 MB                |
| [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing) | 256 MB               |
| [Files API](https://platform.claude.com/docs/en/build-with-claude/files)                      | 500 MB               |
| Sessions, Agents, Environments                                                                | 32 MB                |

If you exceed these limits, you'll receive a 413 `request_too_large` error.

<Note>
  Partner-operated platforms have their own request size limits: Bedrock limits requests to 20 MB, and Google Cloud limits requests to 30 MB. Claude Platform on AWS uses the same limits as the direct Claude API. Consult your platform's documentation for current values.
</Note>

### Response headers

The Claude API includes the following headers in its responses:

| Header                      | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `request-id`                | A globally unique identifier for the request, such as `req_018EeWyXxfu5pfWkrYcMdjWG`. Include it when you contact support about a specific request. See [Request ID](https://platform.claude.com/docs/en/api/errors#request-id).                                                                                                                                                                                                                                                                                                                                                        |
| `anthropic-organization-id` | The ID of the organization that the API key or access token used in the request belongs to.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `anthropic-workspace-id`    | The `wrkspc_`-prefixed ID of the [workspace](https://platform.claude.com/docs/en/manage-claude/workspaces) that the API key or access token resolved to, such as `wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ`, including when that is your organization's Default Workspace. Absent when the credential doesn't resolve to a workspace (for example, on Admin API requests) or the request fails before authentication completes. See [Identify the workspace behind an API response](https://platform.claude.com/docs/en/manage-claude/workspaces#identify-the-workspace-behind-an-api-response). |

For the rate limit headers, see [Response headers](https://platform.claude.com/docs/en/api/rate-limits#response-headers) in Rate limits. For examples that read a response header by name with each SDK, see [Identify the workspace behind an API response](https://platform.claude.com/docs/en/manage-claude/workspaces#identify-the-workspace-behind-an-api-response).

<Note>
  Claude Platform on AWS adds an AWS request ID (`x-amzn-requestid`) alongside the standard `request-id` header. See [Request IDs](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#request-ids) for the dual-ID handling pattern.
</Note>


## Pagination

Source: https://platform.claude.com/llms-full.txt#pagination-11

List endpoints return results in pages. Most newer list endpoints use the `page` and `next_page` cursor scheme described in this section. Some use a different scheme; see the note at the end of this section. Use the `limit` query parameter to control the page size and the `page` query parameter to fetch an adjacent page. Each response includes a `data` array alongside cursor fields for navigating between pages.

| Name        | Location        | Description                                                                                                                                                                             |
| ----------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `limit`     | Query parameter | Maximum number of items to return per page.                                                                                                                                             |
| `page`      | Query parameter | Opaque cursor from a previous response. Pass a `next_page` or `prev_page` value here to fetch the adjacent page.                                                                        |
| `order`     | Query parameter | Sort direction for the results (`asc` or `desc`), on list endpoints that support sorting. A `page` cursor is only valid with the `order` it was created with.                           |
| `next_page` | Response field  | Cursor for the next page, or `null` if there are no more results.                                                                                                                       |
| `prev_page` | Response field  | Cursor for the previous page on endpoints that support backward pagination (currently `GET /v1/sessions`), or `null` if you are on the first page. Other list endpoints omit the field. |

To go back a page, pass `prev_page` as the `page` parameter. `prev_page` is `null` when you're on the first page. Not all list endpoints support `prev_page`. Only `GET /v1/sessions` returns `prev_page`; on list endpoints that do not support backward pagination, the field is absent from the response rather than `null`. For a request walkthrough, see [Listing sessions](https://platform.claude.com/docs/en/managed-agents/session-operations#listing-sessions).

Every SDK provides an auto-paginating iterator that follows `next_page` for you. In Python and TypeScript, you get it by iterating the list result directly. The other SDKs provide the iterator through a separate method. SDK auto-pagination is forward-only; to go back a page, read `prev_page` from the response and pass it back as the `page` parameter yourself. See [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) for language-specific details.

<Note>
  Some list endpoints use a different cursor scheme. The [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing), the [Models API](https://platform.claude.com/docs/en/api/models/list), and several [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api) endpoints take `after_id` and `before_id` query parameters instead of `page`. Their responses return `has_more`, `first_id`, and `last_id` instead of `next_page`. See the reference page for each endpoint for its exact pagination fields.
</Note>


## Rate limits and availability

Source: https://platform.claude.com/llms-full.txt#rate-limits-and-availability

### Rate limits

The API enforces rate limits and spend limits to prevent misuse and manage capacity. Limits are organized into usage tiers; your organization is placed on a tier automatically and can move to a higher tier over time. Each tier has:

* **Spend limits**: Maximum monthly cost for API usage
* **Rate limits**: Maximum number of requests per minute (RPM) and tokens per minute (TPM)

You can view your rate limits on the [Rate limits](https://platform.claude.com/settings/limits) page and your spend limits on the [Billing](https://platform.claude.com/settings/billing) page in the Console. For higher rate limits or a higher monthly spend cap, use **Request rate limit increase** on the Rate limits page.

For detailed information about limits, tiers, and the token bucket algorithm used for rate limiting, see [Rate limits](https://platform.claude.com/docs/en/api/rate-limits).

### Availability

The Claude API is available in [many countries and regions](https://platform.claude.com/docs/en/api/supported-regions) worldwide. Check the supported regions page to confirm availability in your location.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-112

<CardGroup cols={2}>
  <Card title="Messages API reference" icon="book" href="https://platform.claude.com/docs/en/api/messages/create">
    Complete API specification for direct model interactions
  </Card>

  <Card title="Claude Managed Agents reference" icon="brain" href="https://platform.claude.com/docs/en/managed-agents/sessions">
    Agents, Sessions, and Environments endpoints
  </Card>

  <Card title="Client SDKs" icon="code" href="https://platform.claude.com/docs/en/cli-sdks-libraries/overview">
    Python, TypeScript, C#, Go, Java, PHP, and Ruby
  </Card>

  <Card title="Rate limits" icon="gauge" href="https://platform.claude.com/docs/en/api/rate-limits">
    Usage tiers, requesting higher limits, and the token bucket algorithm
  </Card>
</CardGroup>


---
title: Beta headers
url: https://platform.claude.com/docs/en/api/beta-headers
description: Access experimental features before they become part of the standard API with the `anthropic-beta` header or the SDKs' `betas` parameter.
---

Beta headers allow you to access experimental features and new model capabilities before they become part of the standard API.

<Info>
  Each [client SDK](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) exposes a `beta` namespace for calling the API with beta features enabled.
</Info>


## How to use beta headers

Source: https://platform.claude.com/llms-full.txt#how-to-use-beta-headers

To access beta features, include the `anthropic-beta` header in your API requests:

Each feature's documentation states the exact beta name to send. The [API overview](https://platform.claude.com/docs/en/api/overview) lists the APIs currently in beta.

The following examples show the same request with cURL, the `ant` CLI, and the SDKs, using the [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) beta as the example. The SDKs take beta names in the `betas` parameter and send the `anthropic-beta` header for you:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: context-management-2025-06-27" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [
        {"role": "user", "content": "Hello, Claude"}
      ]
    }'

bash CLI
  ant beta:messages create \
    --beta context-management-2025-06-27 \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello, Claude"}'

python Python
  client = Anthropic()

  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
      betas=["context-management-2025-06-27"],
  )

  print(response.content)

typescript TypeScript
  const client = new Anthropic();

  const msg = await client.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }],
    betas: ["context-management-2025-06-27"]
  });

  console.log(msg.content);

csharp C#
  var client = new AnthropicClient();

  var message = await client.Beta.Messages.Create(
      new MessageCreateParams
      {
          Model = "claude-opus-5",
          MaxTokens = 1024,
          Messages = [new() { Role = Role.User, Content = "Hello, Claude" }],
          Betas = ["context-management-2025-06-27"],
      }
  );

  Console.WriteLine(string.Join("\n", message.Content));

go Go
  client := anthropic.NewClient()

  message, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude")),
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaContextManagement2025_06_27},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Printf("%+v\n", message.Content)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_5)
    .maxTokens(1024)
    .addUserMessage("Hello, Claude")
    .addBeta(AnthropicBeta.CONTEXT_MANAGEMENT_2025_06_27)
    .build();

  BetaMessage message = client.beta().messages().create(params);
  System.out.println(message.content());

php PHP
  $client = new Client();

  $message = $client->beta->messages->create(
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
      model: 'claude-opus-5',
      betas: ['context-management-2025-06-27'],
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}],
    betas: ["context-management-2025-06-27"]
  )

  puts(message.content)

http
anthropic-beta: feature1,feature2,feature3
```

When using an SDK, list each feature in the `betas` parameter (for example, `betas=["feature1", "feature2"]`). With the CLI, pass a single `--beta` flag with the feature names separated by commas (for example, `--beta feature1,feature2`). Avoid repeating the flag: currently only the first flag's value takes effect.

### Endpoint-specific headers

Some beta APIs are scoped to specific endpoints and require a feature-specific beta header on every request:

| Endpoints                                        | Beta header                 |
| ------------------------------------------------ | --------------------------- |
| `/v1/agents`, `/v1/sessions`, `/v1/environments` | `managed-agents-2026-04-01` |
| `/v1/tunnels`                                    | `mcp-tunnels-2026-06-22`    |
| `/v1/memory_stores` and sub-resources            | `agent-memory-2026-07-22`   |

The SDKs' `beta` namespaces add these headers automatically. Add them yourself only when making raw HTTP requests. See the [Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview), [Using agent memory](https://platform.claude.com/docs/en/managed-agents/memory), and the [MCP tunnels reference](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/reference#tunnels-api) for details.

Endpoint-specific headers that apply to the same endpoint aren't always combinable. On memory store endpoints, `agent-memory-2026-07-22` replaces `managed-agents-2026-04-01`: sending both on the same request returns a `400` error. The client SDKs send the correct header for each endpoint automatically.

### Version naming conventions

Beta feature names typically follow the pattern `feature-name-YYYY-MM-DD`, where the date indicates when the beta was released. Always use the exact beta feature name as documented.


## Error handling

Source: https://platform.claude.com/llms-full.txt#error-handling-10

If you use an invalid beta name, or a beta your organization doesn't have access to, you'll receive a `400` error response:

```json Output
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "Unexpected value(s) `invalid-beta-name` for the `anthropic-beta` header. Please consult our documentation at platform.claude.com/docs or try again without the header."
  },
  "request_id": "req_011CcnGfC9fELffo2EALu4Wd"
}
```


## Getting help

Source: https://platform.claude.com/llms-full.txt#getting-help

For updates to beta features, see the [release notes](https://platform.claude.com/docs/en/release-notes/overview). For help with production issues, contact [support](https://support.claude.com/).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-113

<CardGroup cols={2}>
  <Card title="Errors" icon="info" href="https://platform.claude.com/docs/en/api/errors">
    Understand the HTTP status codes, error response shape, and request IDs the Claude API returns, and handle errors with the SDKs' typed exceptions.
  </Card>

  <Card title="API overview" icon="compass" href="https://platform.claude.com/docs/en/api/overview">
    Explore the Claude API's features, including the APIs currently in beta.
  </Card>
</CardGroup>


---
title: Claude API errors
url: https://platform.claude.com/docs/en/api/errors
description: Understand the HTTP status codes, error response shape, and request IDs the Claude API returns, and handle errors with the SDKs' typed exceptions.
---


## HTTP errors

Source: https://platform.claude.com/llms-full.txt#http-errors

The API follows a predictable HTTP error code format:

* 400 - `invalid_request_error`: There was an issue with the format or content of your request. This error type may also be used for other 4XX status codes not listed in this section. The API also returns a 400 when usage reaches an organization or workspace [spend limit you set](https://platform.claude.com/docs/en/api/rate-limits#setting-your-own-spend-limit), except limits on the [Claude Code workspace](https://platform.claude.com/docs/en/manage-claude/workspaces#claude-code-workspace), which can return a 429 instead.

* 401 - `authentication_error`: There's an issue with your API key (for example, it's malformed, revoked, or expired; see [Key expiration](https://platform.claude.com/docs/en/manage-claude/authentication#key-expiration)). On Claude Platform on AWS, this can also indicate a problem with your AWS credentials or SigV4 signature.

* 402 - `billing_error`: There's an issue with your billing or payment information. Check your payment details in the [Claude Console](https://platform.claude.com), or in AWS Marketplace if you're using Claude Platform on AWS.

* 403 - `permission_error`: Your API key does not have permission to use the specified resource. Check your organization's access and workspace settings in the [Claude Console](https://platform.claude.com).

* 404 - `not_found_error`: The requested resource was not found. Check the endpoint path and any resource IDs in the request URL.

* 409 - `conflict_error`: The request conflicts with the current state of a resource. For example, the resource was modified concurrently, or a value that must be unique is already in use. Resolve the conflict, then retry the request.

* 413 - `request_too_large`: Request exceeds the maximum allowed number of bytes. See [Request size limits](https://platform.claude.com/docs/en/api/errors#request-size-limits) for per-endpoint maximums.

* 429 - `rate_limit_error`: Your organization has hit a [rate limit](https://platform.claude.com/docs/en/api/rate-limits), reached its usage tier's monthly spend cap, or reached a spend limit on the Claude Code workspace. A tier spend-cap 429 has no `retry-after` header and keeps failing until access resumes; see [Reaching your spend cap](https://platform.claude.com/docs/en/api/rate-limits#reaching-your-spend-cap) for how to recognize it.

* 500 - `api_error`: An unexpected error has occurred internal to Anthropic's systems. Retry the request with exponential backoff; if the error persists, contact support with the [request ID](https://platform.claude.com/docs/en/api/errors#request-id).

* 504 - `timeout_error`: The request timed out while processing. Consider using the [streaming Messages API](https://platform.claude.com/docs/en/build-with-claude/streaming) for long-running requests. See [Long requests](https://platform.claude.com/docs/en/api/errors#long-requests) for more options.

* 529 - `overloaded_error`: The API is temporarily overloaded.

  <Warning>
    529 errors can occur when the API experiences high traffic across all users.

    In rare cases, if your organization has a sharp increase in usage, you might see 429 errors because of acceleration limits on the API. To avoid hitting acceleration limits, ramp up your traffic gradually and maintain consistent usage patterns.
  </Warning>

The official SDKs automatically retry transient failures (such as connection errors, rate limits, and 5xx server errors) with exponential backoff, twice by default, honoring the `retry-after` header when present. Each SDK client accepts a maximum-retries option to configure or disable this behavior.

When receiving a [streaming](https://platform.claude.com/docs/en/build-with-claude/streaming) response over server-sent events (SSE), an error can occur after the API returns a 200 response. In that case, error handling doesn't follow these standard mechanisms. See [Error events](https://platform.claude.com/docs/en/build-with-claude/streaming#error-events) for the shape of mid-stream errors.


## Request size limits

Source: https://platform.claude.com/llms-full.txt#request-size-limits

The API enforces request size limits:

| Endpoint type                                                                       | Maximum request size |
| ----------------------------------------------------------------------------------- | -------------------- |
| Messages API                                                                        | 32 MB                |
| Token Counting API                                                                  | 32 MB                |
| [Batch API](https://platform.claude.com/docs/en/build-with-claude/batch-processing) | 256 MB               |
| [Files API](https://platform.claude.com/docs/en/build-with-claude/files)            | 500 MB               |

If you exceed these limits, you'll receive a 413 `request_too_large` error. On the direct Claude API, Cloudflare returns this error before the request reaches the API servers.


## Error shapes

Source: https://platform.claude.com/llms-full.txt#error-shapes

The API always returns errors as JSON, with a top-level `error` object that always includes a `type` and `message` value. The response also includes a `request_id` field for easier tracking and debugging. For example:

```json JSON
{
  "type": "error",
  "error": {
    "type": "not_found_error",
    "message": "The requested resource could not be found."
  },
  "request_id": "req_011CSHoEeqs5C35K2UUqR7Fy"
}
```

In accordance with the [versioning](https://platform.claude.com/docs/en/api/versioning) policy, the values within these objects may expand, and it is possible that the `type` values will grow over time.


## SDK error types

Source: https://platform.claude.com/llms-full.txt#sdk-error-types

The official SDKs raise typed exceptions for these errors instead of returning raw JSON, and the class names and namespaces differ by language. For example, a 404 surfaces as `anthropic.NotFoundError` in Python, `Anthropic::Errors::NotFoundError` in Ruby, `com.anthropic.errors.NotFoundException` in Java, and as a single `*anthropic.Error` value (branch on `StatusCode`) in Go. Catch the SDK's typed classes rather than string-matching error messages, handling the most specific classes first. Each SDK page documents its full exception hierarchy:

* [Python](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python#handling-errors) · [TypeScript](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/typescript#handling-errors) · [C#](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/csharp#error-handling) · [Go](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/go#error-handling) · [Java](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java#error-handling) · [PHP](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/php#error-handling) · [Ruby](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/ruby#handling-errors)


## Request ID

Source: https://platform.claude.com/llms-full.txt#request-id

Every API response includes a unique `request-id` header. This header contains a value such as `req_018EeWyXxfu5pfWkrYcMdjWG`. The same identifier appears as the `request_id` field in [error response bodies](https://platform.claude.com/docs/en/api/errors#error-shapes). When contacting support about a specific request, include this ID to help quickly resolve your issue.

On [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), responses include two request IDs: the AWS request ID (`x-amzn-requestid`, primary, indexed in CloudTrail) and the Anthropic request ID (`request-id`, secondary). Use the AWS request ID for CloudTrail lookups and the Anthropic request ID for Anthropic support tickets.

The Python and TypeScript SDKs expose the request ID as a `_request_id` property on top-level response objects. The C#, Go, Java, and PHP SDKs expose it through their raw-response accessors, and the Ruby SDK through [middleware](https://platform.claude.com/docs/en/cli-sdks-libraries/middleware). The same mechanisms, along with `with_raw_response` in Python and `.withResponse()` in TypeScript, read any other [response header](https://platform.claude.com/docs/en/api/overview#response-headers) too, such as `anthropic-organization-id` and [`anthropic-workspace-id`](https://platform.claude.com/docs/en/manage-claude/workspaces#identify-the-workspace-behind-an-api-response). On Claude Platform on AWS, use the raw-response accessor to read the AWS request ID (`x-amzn-requestid`) as well:

<CodeGroup>
  ```bash cURL
  # Print the response headers (including request-id); discard the body
  curl -sS -D - -o /dev/null https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-sonnet-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello, Claude"}]
    }'

bash CLI
  # The request-id header is printed to stderr with --debug:
  ant --debug messages create \
    --model claude-sonnet-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello, Claude"}'

python Python
  client = anthropic.Anthropic()

  message = client.messages.create(
      model="claude-sonnet-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
  )
  print(f"Request ID: {message._request_id}")

typescript TypeScript
  const client = new Anthropic();

  const message = await client.messages.create({
    model: "claude-sonnet-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }]
  });
  console.log("Request ID:", message._request_id);

csharp C#
  AnthropicClient client = new();

  using var response = await client.WithRawResponse.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeSonnet5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello, Claude" }]
  });
  Console.WriteLine($"Request ID: {response.RequestID}");

go Go
  client := anthropic.NewClient()

  var response *http.Response
  _, err := client.Messages.New(
  	context.Background(),
  	anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeSonnet5,
  		MaxTokens: 1024,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, Claude")),
  		},
  	},
  	option.WithResponseInto(&response),
  )
  if err != nil {
  	panic(err)
  }

  fmt.Println("Request ID:", response.Header.Get("request-id"))

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
              .model(Model.CLAUDE_SONNET_5)
              .maxTokens(1024)
              .addUserMessage("Hello, Claude")
              .build()
      );

      IO.println("Request ID: " + response.requestId().orElse(null));
  }

php PHP
  $client = new Client();

  $response = $client->messages->raw->create([
      'model' => 'claude-sonnet-5',
      'maxTokens' => 1024,
      'messages' => [['role' => 'user', 'content' => 'Hello, Claude']],
  ]);
  echo 'Request ID: ' . $response->getHeaderLine('request-id') . "\n";

ruby Ruby
  client = Anthropic::Client.new

  # Read response headers in per-request middleware, which receives the
  # raw HTTP response before the SDK parses it
  request_id = nil
  read_request_id = lambda do |request, call_next|
    response = call_next.call(request)
    # Keys in response.headers are lowercase
    request_id = response.headers["request-id"]
    response
  end

  client.messages.create(
    model: Anthropic::Model::CLAUDE_SONNET_5,
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }],
    request_options: { middleware: [read_request_id] }
  )
  puts "Request ID: #{request_id}"

python Python (Claude Platform on AWS)
  from anthropic import AnthropicAWS

  client = AnthropicAWS(aws_region="us-west-2")

  response = client.messages.with_raw_response.create(
      model="claude-opus-4-8",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
  )
  print(f"AWS request ID: {response.headers.get('x-amzn-requestid')}")
  message = response.parse()
  print(f"Anthropic request ID: {message._request_id}")

typescript TypeScript (Claude Platform on AWS)
  import AnthropicAws from "@anthropic-ai/aws-sdk";

  const client = new AnthropicAws({ awsRegion: "us-west-2" });

  const { response: raw, request_id } = await client.messages
    .create({
      model: "claude-opus-4-8",
      max_tokens: 1024,
      messages: [{ role: "user", content: "Hello, Claude" }]
    })
    .withResponse();
  console.log("AWS request ID:", raw.headers.get("x-amzn-requestid"));
  console.log("Anthropic request ID:", request_id);
  ```
</CodeGroup>

For Claude Platform on AWS request-ID examples in other languages, see [Request IDs](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#request-ids).


## Long requests

Source: https://platform.claude.com/llms-full.txt#long-requests-5

<Warning>
  Consider using the [streaming Messages API](https://platform.claude.com/docs/en/build-with-claude/streaming) or [Message Batches API](https://platform.claude.com/docs/en/api/messages/batches/create) for long-running requests, especially those over 10 minutes.
</Warning>

Avoid setting a large `max_tokens` value without using the [streaming Messages API](https://platform.claude.com/docs/en/build-with-claude/streaming) or [Message Batches API](https://platform.claude.com/docs/en/api/messages/batches/create):

* Some networks may drop idle connections after a variable period of time, which can cause the request to fail or time out without receiving a response from Anthropic.
* Networks differ in reliability. The [Message Batches API](https://platform.claude.com/docs/en/api/messages/batches/create) can help you manage the risk of network issues by allowing you to poll for results rather than requiring an uninterrupted network connection.

If you are building a direct API integration, setting a [TCP socket keep-alive](https://tldp.org/HOWTO/TCP-Keepalive-HOWTO/programming.html) can reduce the impact of idle connection timeouts on some networks.

The [SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) validate that your non-streaming Messages API requests are not expected to exceed a 10-minute timeout. They also set a socket option for TCP keep-alive.

If you don't need to process events incrementally, the SDKs can consume the stream for you and return the complete `Message` object, identical to what a non-streaming call returns:

<CodeGroup>
  ```bash cURL
  # Raw SSE output requires handling events; there is no single-command way
  # to accumulate the final message with curl. Use the SDK examples instead.

bash CLI
  # The CLI streams events; --format jsonl emits one event per line
  ant messages create --stream --format jsonl <<'YAML'
  model: claude-sonnet-5
  max_tokens: 128000
  messages:
    - role: user
      content: Write a detailed analysis...
  YAML

python Python
  client = anthropic.Anthropic()

  with client.messages.stream(
      max_tokens=128000,
      messages=[{"role": "user", "content": "Write a detailed analysis..."}],
      model="claude-sonnet-5",
  ) as stream:
      message = stream.get_final_message()

  print(next(block.text for block in message.content if block.type == "text"))

typescript TypeScript
  const client = new Anthropic();

  const stream = client.messages.stream({
    max_tokens: 128000,
    messages: [{ role: "user", content: "Write a detailed analysis..." }],
    model: "claude-sonnet-5"
  });

  const message = await stream.finalMessage();
  const textBlock = message.content.find((block) => block.type === "text");
  if (textBlock && textBlock.type === "text") {
    console.log(textBlock.text);
  }

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeSonnet5,
      MaxTokens = 128000,
      Messages = [new() { Role = Role.User, Content = "Write a detailed analysis..." }]
  };

  var message = await client.Messages.CreateStreaming(parameters).Aggregate();
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  stream := client.Messages.NewStreaming(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeSonnet5,
  	MaxTokens: 128000,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Write a detailed analysis...")),
  	},
  })

  message := anthropic.Message{}
  for stream.Next() {
  	event := stream.Current()
  	if err := message.Accumulate(event); err != nil {
  		log.Fatal(err)
  	}
  }
  if err := stream.Err(); err != nil {
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
  import com.anthropic.helpers.MessageAccumulator;
  import com.anthropic.models.messages.ContentBlock;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_SONNET_5)
          .maxTokens(128000L)
          .addUserMessage("Write a detailed analysis...")
          .build();

      MessageAccumulator accumulator = MessageAccumulator.create();
      try (var streamResponse = client.messages().createStreaming(params)) {
          streamResponse.stream().forEach(accumulator::accumulate);
      }

      Message message = accumulator.message();
      message.content().stream()
              .filter(ContentBlock::isText)
              .findFirst()
              .flatMap(ContentBlock::text)
              .ifPresent(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  use Anthropic\Lib\Streaming\MessageAccumulator;

  $client = new Client();

  $stream = $client->messages->createStream(
      model: 'claude-sonnet-5',
      maxTokens: 128000,
      messages: [['role' => 'user', 'content' => 'Write a detailed analysis...']],
  );

  $accumulator = MessageAccumulator::forMessages();
  foreach ($stream as $event) {
      $accumulator->accumulate($event);
  }

  echo array_find($accumulator->message()->content, static fn ($block): bool => $block->type === 'text')->text;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.stream(
    model: "claude-sonnet-5",
    max_tokens: 128000,
    messages: [{ role: "user", content: "Write a detailed analysis..." }]
  ).accumulated_message

  puts message.content.find { it.type == :text }.text
  ```
</CodeGroup>

See [Streaming Messages](https://platform.claude.com/docs/en/build-with-claude/streaming#get-the-final-message-without-handling-events) for more details.


## Common validation errors

Source: https://platform.claude.com/llms-full.txt#common-validation-errors

### Prefill not supported

Claude 4.6 and later models and [Claude Mythos Preview](https://anthropic.com/glasswing) do not support prefilling assistant messages. Sending a request with a prefilled last assistant message to any of these models returns a 400 `invalid_request_error`:

Use [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) on models that support it, system prompt instructions, or [`output_config.format`](https://platform.claude.com/docs/en/build-with-claude/structured-outputs#json-outputs) instead.

### Thinking blocks cannot be modified

If the most recent assistant message contains `thinking` or `redacted_thinking` blocks that were edited, reordered, filtered out, or reconstructed before being sent back to the API, the request returns a 400 `invalid_request_error`. The error message starts with the position of the offending block (for example, `messages.1.content.0`) and contains:

```text wrap
`thinking` or `redacted_thinking` blocks in the latest assistant message cannot be modified. These blocks must remain as they were in the original response.

text wrap
"thinking.type.enabled" is not supported for this model. Use "thinking.type.adaptive" and "output_config.effort" to control thinking behavior.

text wrap
adaptive thinking is not supported on this model

text wrap
"thinking.type.disabled" is not supported for this model. Thinking defaults to adaptive mode when not specified; use "thinking.type.enabled" with "budget_tokens" for extended thinking.

text wrap
tool_choice: type "tool" and "any" are not supported for this model.

text wrap
messages.{i}.content.{j}: Invalid `signature` in `thinking` block. The block is bound to a different conversation. Remove the block, or set `thinking.block_binding.prefix_mismatch_behavior` to "drop_block".

text wrap
block_binding: Extra inputs are not permitted
```

Add the header, or remove the field.

### Outbound web identity federation disabled (Claude Platform on AWS)

If every request to [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) returns `"Outbound web identity federation is disabled for your account"`, run `aws iam enable-outbound-web-identity-federation` once per AWS account. See [Enable outbound web identity federation](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#enable-outbound-web-identity-federation) for details.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-114

<CardGroup cols={3}>
  <Card title="Troubleshooting thinking" icon="wrench" href="https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting">
    Symptom-first fixes for thinking configuration 400 errors, empty thinking blocks, and `max_tokens` stops.
  </Card>

  <Card title="Rate limits" icon="gauge" href="https://platform.claude.com/docs/en/api/rate-limits">
    To mitigate misuse and manage capacity on the API, limits are in place on how much an organization can use the Claude API.
  </Card>

  <Card title="Streaming messages" icon="lightning" href="https://platform.claude.com/docs/en/build-with-claude/streaming">
    Stream Messages API responses incrementally with server-sent events, including text, tool use, and extended thinking deltas.
  </Card>
</CardGroup>


### Support & configuration

---
title: IAM actions for Claude Platform on AWS
url: https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions
description: IAM action reference for controlling access to Claude Platform on AWS through AWS policies.
---

Claude Platform on AWS uses AWS IAM for access control. Every API route maps to an IAM action in the `aws-external-anthropic` namespace. This page lists all actions, the routes each action authorizes, and the managed policies available for common access patterns. For platform setup and authentication, see [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws).


## Service details

Source: https://platform.claude.com/llms-full.txt#service-details

| Attribute              | Value                    |
| ---------------------- | ------------------------ |
| **IAM service prefix** | `aws-external-anthropic` |
| **Resource types**     | `workspace`              |

Workspace ARN format:

```text wrap
arn:aws:aws-external-anthropic:{region}:{account-id}:workspace/{workspace-id}
```

The ARN region is always populated and matches the region the workspace is bound to. The resource segment is the tagged workspace ID (`wrkspc_...`), the same value you pass in the `anthropic-workspace-id` header.


## Actions

Source: https://platform.claude.com/llms-full.txt#actions

The service defines 71 actions. Actions follow the AWS `VerbNoun` convention and use verb discipline so that `Get*` and `List*` wildcards produce a clean read-only boundary.

### Inference

| Action            | Routes authorized                |
| ----------------- | -------------------------------- |
| `CreateInference` | `POST /v1/messages`              |
| `CountTokens`     | `POST /v1/messages/count_tokens` |

### Batch processing

| Action                 | Routes authorized                                                       |
| ---------------------- | ----------------------------------------------------------------------- |
| `CreateBatchInference` | `POST /v1/messages/batches`                                             |
| `GetBatchInference`    | `GET /v1/messages/batches/{id}` `GET /v1/messages/batches/{id}/results` |
| `ListBatchInferences`  | `GET /v1/messages/batches`                                              |
| `CancelBatchInference` | `POST /v1/messages/batches/{id}/cancel`                                 |
| `DeleteBatchInference` | `DELETE /v1/messages/batches/{id}`                                      |

<Note>
  `GetBatchInference` authorizes both reading batch metadata and downloading batch results. The `AnthropicReadOnlyAccess`, `AnthropicInferenceAccess`, and `AnthropicLimitedAccess` policies' `Get*` wildcards include this action.
</Note>

### Models

| Action       | Routes authorized     |
| ------------ | --------------------- |
| `GetModel`   | `GET /v1/models/{id}` |
| `ListModels` | `GET /v1/models`      |

### Files

| Action       | Routes authorized                                 |
| ------------ | ------------------------------------------------- |
| `CreateFile` | `POST /v1/files`                                  |
| `GetFile`    | `GET /v1/files/{id}` `GET /v1/files/{id}/content` |
| `ListFiles`  | `GET /v1/files`                                   |
| `DeleteFile` | `DELETE /v1/files/{id}`                           |

<Note>
  `GetFile` authorizes both metadata and content download. A principal with read-only access can download file bytes, not just list files.
</Note>

### Skills

| Action        | Routes authorized                                                                                                                              |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `CreateSkill` | `POST /v1/skills`                                                                                                                              |
| `GetSkill`    | `GET /v1/skills/{id}` `GET /v1/skills/{id}/versions` `GET /v1/skills/{id}/versions/{version}` `GET /v1/skills/{id}/versions/{version}/content` |
| `ListSkills`  | `GET /v1/skills`                                                                                                                               |
| `UpdateSkill` | `POST /v1/skills/{id}/versions` `DELETE /v1/skills/{id}/versions/{version}`                                                                    |
| `DeleteSkill` | `DELETE /v1/skills/{id}`                                                                                                                       |

<Note>
  `GetSkill` authorizes both skill metadata and skill-content download. A principal with read-only access can download skill bytes, not just list skills.
</Note>

<Note>
  Creating or deleting an individual skill version maps to `UpdateSkill`, not `CreateSkill` or `DeleteSkill`. A policy that denies `aws-external-anthropic:Delete*` still allows version deletion, and a policy that denies `aws-external-anthropic:Create*` still allows version creation. Deny `UpdateSkill` and `CreateSkill` as well if you need to prevent any skill mutation.
</Note>

### Agents

| Action         | Routes authorized                                    |
| -------------- | ---------------------------------------------------- |
| `CreateAgent`  | `POST /v1/agents`                                    |
| `GetAgent`     | `GET /v1/agents/{id}` `GET /v1/agents/{id}/versions` |
| `ListAgents`   | `GET /v1/agents`                                     |
| `UpdateAgent`  | `POST /v1/agents/{id}`                               |
| `ArchiveAgent` | `POST /v1/agents/{id}/archive`                       |

<Note>
  Agents support only archive, not hard delete. A policy that denies `aws-external-anthropic:Delete*` does not block `ArchiveAgent`. Deny `ArchiveAgent`, `UpdateAgent`, and `CreateAgent` if you need to prevent any agent mutation.
</Note>

### Sessions

| Action           | Routes authorized                                                                                                                                                             |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CreateSession`  | `POST /v1/sessions`                                                                                                                                                           |
| `GetSession`     | `GET /v1/sessions/{id}` `GET /v1/sessions/{id}/events` `GET /v1/sessions/{id}/events/stream` `GET /v1/sessions/{id}/resources` `GET /v1/sessions/{id}/resources/{id}`         |
| `ListSessions`   | `GET /v1/sessions`                                                                                                                                                            |
| `UpdateSession`  | `POST /v1/sessions/{id}` `POST /v1/sessions/{id}/events` `POST /v1/sessions/{id}/resources` `POST /v1/sessions/{id}/resources/{id}` `DELETE /v1/sessions/{id}/resources/{id}` |
| `ArchiveSession` | `POST /v1/sessions/{id}/archive`                                                                                                                                              |
| `DeleteSession`  | `DELETE /v1/sessions/{id}`                                                                                                                                                    |

<Note>
  `GetSession` authorizes reading session metadata, the full event stream (conversation history), and session resources. The `AnthropicReadOnlyAccess`, `AnthropicInferenceAccess`, and `AnthropicLimitedAccess` policies' `Get*` wildcards include this action.
</Note>

<Note>
  Creating, updating, or deleting an individual session sub-resource (events or session resources) maps to `UpdateSession`, not `CreateSession` or `DeleteSession`. A policy that denies `aws-external-anthropic:Delete*` still allows sub-resource deletion, and a policy that denies `aws-external-anthropic:Create*` still allows sub-resource creation. Deny `UpdateSession`, `CreateSession`, and `ArchiveSession` as well if you need to prevent any session mutation.
</Note>

### Environments

| Action                   | Routes authorized                                                                                                                                                                                                                        |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CreateEnvironment`      | `POST /v1/environments`                                                                                                                                                                                                                  |
| `GetEnvironment`         | `GET /v1/environments/{id}` `GET /v1/environments/{id}/work` `GET /v1/environments/{id}/work/{work_id}` `GET /v1/environments/{id}/work/stats`                                                                                           |
| `ListEnvironments`       | `GET /v1/environments`                                                                                                                                                                                                                   |
| `UpdateEnvironment`      | `POST /v1/environments/{id}`                                                                                                                                                                                                             |
| `ArchiveEnvironment`     | `POST /v1/environments/{id}/archive`                                                                                                                                                                                                     |
| `DeleteEnvironment`      | `DELETE /v1/environments/{id}`                                                                                                                                                                                                           |
| `ProcessEnvironmentWork` | `GET /v1/environments/{id}/work/poll` `POST /v1/environments/{id}/work/{work_id}` `POST /v1/environments/{id}/work/{work_id}/ack` `POST /v1/environments/{id}/work/{work_id}/heartbeat` `POST /v1/environments/{id}/work/{work_id}/stop` |

<Note>
  A policy that denies `aws-external-anthropic:Delete*` does not block `ArchiveEnvironment`. `ProcessEnvironmentWork` is not matched by `Create*`, `Update*`, `Delete*`, or `Archive*` wildcards. Deny `ArchiveEnvironment`, `UpdateEnvironment`, `CreateEnvironment`, and `ProcessEnvironmentWork` as well if you need to prevent any environment mutation.
</Note>

<Note>
  `ProcessEnvironmentWork` authorizes a [self-hosted sandbox](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) worker to poll for, acknowledge, heartbeat, stop, and post results on environment work items. Grant it only to principals that run self-hosted environment workers. The `AnthropicSelfHostedEnvironmentAccess` managed policy includes this action.
</Note>

### Vaults

| Action         | Routes authorized                                                                                                                                                                           |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CreateVault`  | `POST /v1/vaults`                                                                                                                                                                           |
| `GetVault`     | `GET /v1/vaults/{id}` `GET /v1/vaults/{id}/credentials` `GET /v1/vaults/{id}/credentials/{id}`                                                                                              |
| `ListVaults`   | `GET /v1/vaults`                                                                                                                                                                            |
| `UpdateVault`  | `POST /v1/vaults/{id}` `POST /v1/vaults/{id}/credentials` `POST /v1/vaults/{id}/credentials/{id}` `POST /v1/vaults/{id}/credentials/{id}/archive` `DELETE /v1/vaults/{id}/credentials/{id}` |
| `ArchiveVault` | `POST /v1/vaults/{id}/archive`                                                                                                                                                              |
| `DeleteVault`  | `DELETE /v1/vaults/{id}`                                                                                                                                                                    |

<Note>
  Creating, updating, archiving, or deleting an individual vault credential maps to `UpdateVault`. Reading a credential maps to `GetVault`. Vault credential secrets are not exposed: secret fields are write-only and are never returned by `GetVault` (see [Authenticate with vaults](https://platform.claude.com/docs/en/managed-agents/vaults)). A policy that denies `aws-external-anthropic:Delete*` still allows credential deletion, and a policy that denies `aws-external-anthropic:Create*` still allows credential creation. Deny `UpdateVault`, `CreateVault`, and `ArchiveVault` as well if you need to prevent any vault mutation.
</Note>

### Memory stores

| Action               | Routes authorized                                                                                                                                                                                                        |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `CreateMemoryStore`  | `POST /v1/memory_stores`                                                                                                                                                                                                 |
| `GetMemoryStore`     | `GET /v1/memory_stores/{id}` `GET /v1/memory_stores/{id}/memories` `GET /v1/memory_stores/{id}/memories/{id}` `GET /v1/memory_stores/{id}/memory_versions` `GET /v1/memory_stores/{id}/memory_versions/{id}`             |
| `ListMemoryStores`   | `GET /v1/memory_stores`                                                                                                                                                                                                  |
| `UpdateMemoryStore`  | `POST /v1/memory_stores/{id}` `POST /v1/memory_stores/{id}/memories` `POST /v1/memory_stores/{id}/memories/{id}` `DELETE /v1/memory_stores/{id}/memories/{id}` `POST /v1/memory_stores/{id}/memory_versions/{id}/redact` |
| `ArchiveMemoryStore` | `POST /v1/memory_stores/{id}/archive`                                                                                                                                                                                    |
| `DeleteMemoryStore`  | `DELETE /v1/memory_stores/{id}`                                                                                                                                                                                          |

<Note>
  `GetMemoryStore` authorizes reading store metadata, all memories, and memory version history. The `AnthropicReadOnlyAccess`, `AnthropicInferenceAccess`, and `AnthropicLimitedAccess` policies' `Get*` wildcards include this action.
</Note>

<Note>
  Creating, updating, or deleting an individual memory and redacting a memory version both map to `UpdateMemoryStore`, not `CreateMemoryStore` or `DeleteMemoryStore`. A policy that denies `aws-external-anthropic:Delete*` still allows individual-memory deletion and memory-version redaction, and a policy that denies `aws-external-anthropic:Create*` still allows individual-memory creation. Deny `UpdateMemoryStore`, `CreateMemoryStore`, and `ArchiveMemoryStore` as well if you need to prevent any memory-store mutation.
</Note>

### Webhooks

| Action                | Routes authorized                                  |
| --------------------- | -------------------------------------------------- |
| `CreateWebhook`       | `POST /v1/webhooks`                                |
| `GetWebhook`          | `GET /v1/webhooks/{id}`                            |
| `ListWebhooks`        | `GET /v1/webhooks`                                 |
| `UpdateWebhook`       | `POST /v1/webhooks/{id}`                           |
| `DeleteWebhook`       | `DELETE /v1/webhooks/{id}`                         |
| `RotateWebhookSecret` | `POST /v1/webhooks/{id}/regenerate_signing_secret` |

<Note>
  Webhook signing secrets are write-only. `GetWebhook` returns webhook metadata only; it does not return the signing secret.
</Note>

<Note>
  `RotateWebhookSecret` is not matched by `aws-external-anthropic:Create*`, `Update*`, or `Delete*` wildcards. A policy that denies those patterns still allows secret rotation. Deny `RotateWebhookSecret`, `UpdateWebhook`, `CreateWebhook`, and `DeleteWebhook` if you need to prevent any webhook mutation.
</Note>

### User profiles

| Action              | Routes authorized             |
| ------------------- | ----------------------------- |
| `CreateUserProfile` | `POST /v1/user_profiles`      |
| `GetUserProfile`    | `GET /v1/user_profiles/{id}`  |
| `ListUserProfiles`  | `GET /v1/user_profiles`       |
| `UpdateUserProfile` | `POST /v1/user_profiles/{id}` |

<Warning>
  IAM action matching is case-insensitive. The wildcard `aws-external-anthropic:*File` matches `CreateFile`, `GetFile`, and `DeleteFile`, but does not match `ListFiles` (which ends in "files", not "file"). It also over-matches `CreateUserProfile`, `GetUserProfile`, and `UpdateUserProfile` because "Profile" ends in "file". If you intend to grant or deny only Files API actions, enumerate them explicitly (`CreateFile`, `GetFile`, `ListFiles`, `DeleteFile`) rather than using a `*File` suffix pattern.
</Warning>

### Workspaces

| Action             | Routes authorized                                |
| ------------------ | ------------------------------------------------ |
| `CreateWorkspace`  | `POST /v1/organizations/workspaces`              |
| `GetWorkspace`     | `GET /v1/organizations/workspaces/{id}`          |
| `ListWorkspaces`   | `GET /v1/organizations/workspaces`               |
| `UpdateWorkspace`  | `POST /v1/organizations/workspaces/{id}`         |
| `ArchiveWorkspace` | `POST /v1/organizations/workspaces/{id}/archive` |

<Note>
  Workspaces support only archive, not hard delete. A policy that denies `aws-external-anthropic:Delete*` does not block `ArchiveWorkspace`. Deny `ArchiveWorkspace`, `UpdateWorkspace`, and `CreateWorkspace` if you need to prevent any workspace mutation.
</Note>

### Encryption keys

| Action        | Routes authorized                             |
| ------------- | --------------------------------------------- |
| `RegisterKey` | `POST /v1/organizations/external_keys`        |
| `GetKey`      | `GET /v1/organizations/external_keys/{id}`    |
| `ListKeys`    | `GET /v1/organizations/external_keys`         |
| `UpdateKey`   | `POST /v1/organizations/external_keys/{id}`   |
| `DisableKey`  | `DELETE /v1/organizations/external_keys/{id}` |

<Note>
  These actions manage your organization's [customer-managed encryption key (CMEK)](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms#claude-platform-on-aws) registrations, the record of which AWS KMS key ARNs are registered. They do not create, change, or disable the keys in AWS KMS. `DisableKey` removes a registration and is rejected while any workspace still uses the key. `RegisterKey` and `DisableKey` are not matched by `Create*`, `Update*`, or `Delete*` wildcards; deny `RegisterKey`, `UpdateKey`, and `DisableKey` if you need to prevent any change to key registrations. In these routes, `{id}` is the URL-encoded KMS key ARN. Attaching a registered key to a workspace is a workspace operation, authorized by `CreateWorkspace` or `UpdateWorkspace`; the principal that attaches a key also needs `kms:DescribeKey`, `kms:Encrypt`, and `kms:Decrypt` on that key (see the [prerequisites](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms#claude-platform-on-aws)). External key actions are account-scoped: specifying a workspace ARN on them has no effect; use `Resource: "*"`.
</Note>

### Compliance

| Action                     | Routes authorized               |
| -------------------------- | ------------------------------- |
| `ListComplianceActivities` | `GET /v1/compliance/activities` |

<Note>
  `ListComplianceActivities` authorizes reading the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed), the organization-wide audit log that includes access transparency events. The route returns an error until the Compliance API is [enabled for your organization](https://platform.claude.com/docs/en/manage-claude/compliance-api-access); enablement is on request through your Anthropic account team. The `AnthropicReadOnlyAccess`, `AnthropicInferenceAccess`, and `AnthropicLimitedAccess` policies' `List*` wildcards include this action.
</Note>

<Note>
  `ListComplianceActivities` is account-scoped, like `ListWorkspaces`. Specifying a workspace ARN on this action has no effect; use `Resource: "*"`.
</Note>

### Authentication

| Action                | Routes authorized |
| --------------------- | ----------------- |
| `CallWithBearerToken` | (none)            |

`CallWithBearerToken` is an authentication-layer permission that authorizes a principal to authenticate through an API key (bearer token) rather than AWS SigV4. It does not map to a route. Grant it alongside the route-mapped actions you want the API key holder to perform.

### Console access

| Action          | Routes authorized |
| --------------- | ----------------- |
| `AssumeConsole` | (none)            |

`AssumeConsole` authorizes a principal to open the Claude Console for a Claude Platform on AWS workspace through the AWS Console federation flow. It does not map to a route. Grant it to principals who should be able to click **Open Claude Console** on the Claude Platform on AWS service page in the AWS Console. The Claude Console role (Admin or Developer) is assigned separately by your Anthropic account representative; it is not derived from the principal's IAM permissions. See [Using the Claude Console](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#using-the-claude-console) for the sign-in flow and role descriptions.


## Route-to-action mapping

Source: https://platform.claude.com/llms-full.txt#route-to-action-mapping

The following table lists every route on Claude Platform on AWS and the IAM action required to call it. Each IAM action also authorizes requests that use the `anthropic-beta` header; beta variants of a route do not require a separate IAM action. CloudTrail classifies each action as either a Data event (high-volume, data-plane operations) or a Management event (control-plane operations). Vault and webhook actions are classified as Management events because they hold secrets (vault credentials and webhook signing secrets) and benefit from default-on audit logging. Workspace, external key, and compliance actions are also classified as Management events because they are organization-scoped control-plane operations. All other actions, including inference, batch, model, file, skill, user profile, and the remaining Claude Managed Agents actions, are classified as Data events.

| Method   | Route                                                | IAM action                 | CloudTrail event type |
| -------- | ---------------------------------------------------- | -------------------------- | --------------------- |
| `POST`   | `/v1/messages`                                       | `CreateInference`          | Data                  |
| `POST`   | `/v1/messages/count_tokens`                          | `CountTokens`              | Data                  |
| `POST`   | `/v1/messages/batches`                               | `CreateBatchInference`     | Data                  |
| `GET`    | `/v1/messages/batches`                               | `ListBatchInferences`      | Data                  |
| `GET`    | `/v1/messages/batches/{id}`                          | `GetBatchInference`        | Data                  |
| `GET`    | `/v1/messages/batches/{id}/results`                  | `GetBatchInference`        | Data                  |
| `POST`   | `/v1/messages/batches/{id}/cancel`                   | `CancelBatchInference`     | Data                  |
| `DELETE` | `/v1/messages/batches/{id}`                          | `DeleteBatchInference`     | Data                  |
| `GET`    | `/v1/models`                                         | `ListModels`               | Data                  |
| `GET`    | `/v1/models/{id}`                                    | `GetModel`                 | Data                  |
| `POST`   | `/v1/files`                                          | `CreateFile`               | Data                  |
| `GET`    | `/v1/files`                                          | `ListFiles`                | Data                  |
| `GET`    | `/v1/files/{id}`                                     | `GetFile`                  | Data                  |
| `GET`    | `/v1/files/{id}/content`                             | `GetFile`                  | Data                  |
| `DELETE` | `/v1/files/{id}`                                     | `DeleteFile`               | Data                  |
| `POST`   | `/v1/skills`                                         | `CreateSkill`              | Data                  |
| `GET`    | `/v1/skills`                                         | `ListSkills`               | Data                  |
| `GET`    | `/v1/skills/{id}`                                    | `GetSkill`                 | Data                  |
| `DELETE` | `/v1/skills/{id}`                                    | `DeleteSkill`              | Data                  |
| `POST`   | `/v1/skills/{id}/versions`                           | `UpdateSkill`              | Data                  |
| `GET`    | `/v1/skills/{id}/versions`                           | `GetSkill`                 | Data                  |
| `GET`    | `/v1/skills/{id}/versions/{version}`                 | `GetSkill`                 | Data                  |
| `GET`    | `/v1/skills/{id}/versions/{version}/content`         | `GetSkill`                 | Data                  |
| `DELETE` | `/v1/skills/{id}/versions/{version}`                 | `UpdateSkill`              | Data                  |
| `POST`   | `/v1/user_profiles`                                  | `CreateUserProfile`        | Data                  |
| `GET`    | `/v1/user_profiles`                                  | `ListUserProfiles`         | Data                  |
| `GET`    | `/v1/user_profiles/{id}`                             | `GetUserProfile`           | Data                  |
| `POST`   | `/v1/user_profiles/{id}`                             | `UpdateUserProfile`        | Data                  |
| `POST`   | `/v1/organizations/workspaces`                       | `CreateWorkspace`          | Management            |
| `GET`    | `/v1/organizations/workspaces`                       | `ListWorkspaces`           | Management            |
| `GET`    | `/v1/organizations/workspaces/{id}`                  | `GetWorkspace`             | Management            |
| `POST`   | `/v1/organizations/workspaces/{id}`                  | `UpdateWorkspace`          | Management            |
| `POST`   | `/v1/organizations/workspaces/{id}/archive`          | `ArchiveWorkspace`         | Management            |
| `POST`   | `/v1/organizations/external_keys`                    | `RegisterKey`              | Management            |
| `GET`    | `/v1/organizations/external_keys`                    | `ListKeys`                 | Management            |
| `GET`    | `/v1/organizations/external_keys/{id}`               | `GetKey`                   | Management            |
| `POST`   | `/v1/organizations/external_keys/{id}`               | `UpdateKey`                | Management            |
| `DELETE` | `/v1/organizations/external_keys/{id}`               | `DisableKey`               | Management            |
| `GET`    | `/v1/compliance/activities`                          | `ListComplianceActivities` | Management            |
| `POST`   | `/v1/agents`                                         | `CreateAgent`              | Data                  |
| `GET`    | `/v1/agents`                                         | `ListAgents`               | Data                  |
| `GET`    | `/v1/agents/{id}`                                    | `GetAgent`                 | Data                  |
| `POST`   | `/v1/agents/{id}`                                    | `UpdateAgent`              | Data                  |
| `POST`   | `/v1/agents/{id}/archive`                            | `ArchiveAgent`             | Data                  |
| `GET`    | `/v1/agents/{id}/versions`                           | `GetAgent`                 | Data                  |
| `POST`   | `/v1/sessions`                                       | `CreateSession`            | Data                  |
| `GET`    | `/v1/sessions`                                       | `ListSessions`             | Data                  |
| `GET`    | `/v1/sessions/{id}`                                  | `GetSession`               | Data                  |
| `POST`   | `/v1/sessions/{id}`                                  | `UpdateSession`            | Data                  |
| `POST`   | `/v1/sessions/{id}/archive`                          | `ArchiveSession`           | Data                  |
| `DELETE` | `/v1/sessions/{id}`                                  | `DeleteSession`            | Data                  |
| `GET`    | `/v1/sessions/{id}/events`                           | `GetSession`               | Data                  |
| `POST`   | `/v1/sessions/{id}/events`                           | `UpdateSession`            | Data                  |
| `GET`    | `/v1/sessions/{id}/events/stream`                    | `GetSession`               | Data                  |
| `GET`    | `/v1/sessions/{id}/resources`                        | `GetSession`               | Data                  |
| `GET`    | `/v1/sessions/{id}/resources/{id}`                   | `GetSession`               | Data                  |
| `POST`   | `/v1/sessions/{id}/resources`                        | `UpdateSession`            | Data                  |
| `POST`   | `/v1/sessions/{id}/resources/{id}`                   | `UpdateSession`            | Data                  |
| `DELETE` | `/v1/sessions/{id}/resources/{id}`                   | `UpdateSession`            | Data                  |
| `POST`   | `/v1/environments`                                   | `CreateEnvironment`        | Data                  |
| `GET`    | `/v1/environments`                                   | `ListEnvironments`         | Data                  |
| `GET`    | `/v1/environments/{id}`                              | `GetEnvironment`           | Data                  |
| `POST`   | `/v1/environments/{id}`                              | `UpdateEnvironment`        | Data                  |
| `POST`   | `/v1/environments/{id}/archive`                      | `ArchiveEnvironment`       | Data                  |
| `DELETE` | `/v1/environments/{id}`                              | `DeleteEnvironment`        | Data                  |
| `GET`    | `/v1/environments/{id}/work`                         | `GetEnvironment`           | Data                  |
| `GET`    | `/v1/environments/{id}/work/poll`                    | `ProcessEnvironmentWork`   | Data                  |
| `GET`    | `/v1/environments/{id}/work/{work_id}`               | `GetEnvironment`           | Data                  |
| `GET`    | `/v1/environments/{id}/work/stats`                   | `GetEnvironment`           | Data                  |
| `POST`   | `/v1/environments/{id}/work/{work_id}`               | `ProcessEnvironmentWork`   | Data                  |
| `POST`   | `/v1/environments/{id}/work/{work_id}/ack`           | `ProcessEnvironmentWork`   | Data                  |
| `POST`   | `/v1/environments/{id}/work/{work_id}/heartbeat`     | `ProcessEnvironmentWork`   | Data                  |
| `POST`   | `/v1/environments/{id}/work/{work_id}/stop`          | `ProcessEnvironmentWork`   | Data                  |
| `POST`   | `/v1/vaults`                                         | `CreateVault`              | Management            |
| `GET`    | `/v1/vaults`                                         | `ListVaults`               | Management            |
| `GET`    | `/v1/vaults/{id}`                                    | `GetVault`                 | Management            |
| `POST`   | `/v1/vaults/{id}`                                    | `UpdateVault`              | Management            |
| `POST`   | `/v1/vaults/{id}/archive`                            | `ArchiveVault`             | Management            |
| `DELETE` | `/v1/vaults/{id}`                                    | `DeleteVault`              | Management            |
| `GET`    | `/v1/vaults/{id}/credentials`                        | `GetVault`                 | Management            |
| `POST`   | `/v1/vaults/{id}/credentials`                        | `UpdateVault`              | Management            |
| `GET`    | `/v1/vaults/{id}/credentials/{id}`                   | `GetVault`                 | Management            |
| `POST`   | `/v1/vaults/{id}/credentials/{id}`                   | `UpdateVault`              | Management            |
| `POST`   | `/v1/vaults/{id}/credentials/{id}/archive`           | `UpdateVault`              | Management            |
| `DELETE` | `/v1/vaults/{id}/credentials/{id}`                   | `UpdateVault`              | Management            |
| `POST`   | `/v1/memory_stores`                                  | `CreateMemoryStore`        | Data                  |
| `GET`    | `/v1/memory_stores`                                  | `ListMemoryStores`         | Data                  |
| `GET`    | `/v1/memory_stores/{id}`                             | `GetMemoryStore`           | Data                  |
| `POST`   | `/v1/memory_stores/{id}`                             | `UpdateMemoryStore`        | Data                  |
| `POST`   | `/v1/memory_stores/{id}/archive`                     | `ArchiveMemoryStore`       | Data                  |
| `DELETE` | `/v1/memory_stores/{id}`                             | `DeleteMemoryStore`        | Data                  |
| `POST`   | `/v1/memory_stores/{id}/memories`                    | `UpdateMemoryStore`        | Data                  |
| `GET`    | `/v1/memory_stores/{id}/memories`                    | `GetMemoryStore`           | Data                  |
| `GET`    | `/v1/memory_stores/{id}/memories/{id}`               | `GetMemoryStore`           | Data                  |
| `POST`   | `/v1/memory_stores/{id}/memories/{id}`               | `UpdateMemoryStore`        | Data                  |
| `DELETE` | `/v1/memory_stores/{id}/memories/{id}`               | `UpdateMemoryStore`        | Data                  |
| `GET`    | `/v1/memory_stores/{id}/memory_versions`             | `GetMemoryStore`           | Data                  |
| `GET`    | `/v1/memory_stores/{id}/memory_versions/{id}`        | `GetMemoryStore`           | Data                  |
| `POST`   | `/v1/memory_stores/{id}/memory_versions/{id}/redact` | `UpdateMemoryStore`        | Data                  |
| `GET`    | `/v1/webhooks`                                       | `ListWebhooks`             | Management            |
| `GET`    | `/v1/webhooks/{id}`                                  | `GetWebhook`               | Management            |
| `POST`   | `/v1/webhooks`                                       | `CreateWebhook`            | Management            |
| `POST`   | `/v1/webhooks/{id}`                                  | `UpdateWebhook`            | Management            |
| `DELETE` | `/v1/webhooks/{id}`                                  | `DeleteWebhook`            | Management            |
| `POST`   | `/v1/webhooks/{id}/regenerate_signing_secret`        | `RotateWebhookSecret`      | Management            |

Routes not in this table are not available on Claude Platform on AWS. The gateway denies any route not listed here by default.

<Note>
  Workspace and external key routes are the only Admin API routes available on Claude Platform on AWS. You can also create, update, or archive workspaces in the AWS Console or, with the Admin role, in the Claude Console. Encryption keys can also be registered and attached in the Claude Console.
</Note>


## Managed policies

Source: https://platform.claude.com/llms-full.txt#managed-policies

AWS provides five managed policies for Claude Platform on AWS. All managed policies apply to `Resource: "*"`.

| Policy                                 | Grants                                                                                                                                                                             |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AnthropicFullAccess`                  | `aws-external-anthropic:*`                                                                                                                                                         |
| `AnthropicReadOnlyAccess`              | `Get*`, `List*`, `CallWithBearerToken`                                                                                                                                             |
| `AnthropicInferenceAccess`             | `Get*`, `List*`, `CreateInference`, `CreateBatchInference`, `CancelBatchInference`, `DeleteBatchInference`, `CountTokens`, `CallWithBearerToken`                                   |
| `AnthropicLimitedAccess`               | All `AnthropicInferenceAccess` actions, plus all Claude Managed Agents actions (agents, sessions, environments, vaults, memory stores, webhooks, and self-hosted environment work) |
| `AnthropicSelfHostedEnvironmentAccess` | `GetEnvironment`, `ProcessEnvironmentWork`, `GetSession`, `UpdateSession`, `GetSkill`, `CallWithBearerToken`                                                                       |

`AnthropicInferenceAccess` is the narrowest managed policy sufficient to run inference. It covers both synchronous and batch inference and, through the `Get*` and `List*` wildcards, grants read access to every API resource in the namespace, including Claude Managed Agents (CMA) resources (agents, sessions, environments, vaults, memory stores, and webhooks). This includes file content download through `GetFile` (see the [Files](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#files) note), skill content download through `GetSkill` (see the [Skills](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#skills) note), and memory contents through `GetMemoryStore`. Vault credential secrets and webhook signing secrets are not exposed: those fields are write-only and are never returned by `GetVault` or `GetWebhook` (see [Authenticate with vaults](https://platform.claude.com/docs/en/managed-agents/vaults)). `AnthropicInferenceAccess` does not grant file creation or deletion, skill management, user profile management, workspace mutation, encryption key management, or any Claude Managed Agents write action (create, update, archive, delete, process, or rotate). To exclude CMA reads, replace `AnthropicInferenceAccess` with a custom policy that enumerates only the specific non-CMA actions you need.

<Note>
  `AnthropicReadOnlyAccess`, `AnthropicInferenceAccess`, and `AnthropicLimitedAccess` all carry the `Get*` and `List*` wildcards, which grant read access to all content in the workspace: file bytes, skill content, batch results, session conversation history, and memory contents. The wildcards also grant `GetKey` and `ListKeys`, which read the organization's registered encryption key configurations (key ARNs and metadata, never key material). The `List*` wildcard also grants `ListComplianceActivities`, which reads the organization's compliance [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) once the Compliance API is enabled for the organization (see [Compliance](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#compliance)). Vault credential secrets and webhook signing secrets are not exposed; those fields are write-only and are never returned by `GetVault` or `GetWebhook`. If your principal should not read existing content, use a custom policy that enumerates only the actions you need.
</Note>

`AnthropicLimitedAccess` includes all Claude Managed Agents actions in addition to inference actions.

`AnthropicSelfHostedEnvironmentAccess` is the narrowest managed policy sufficient to run a [self-hosted sandbox](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) worker. Attach it to the principal your environment worker authenticates as.

`AssumeConsole` is not included in `AnthropicReadOnlyAccess`, `AnthropicInferenceAccess`, `AnthropicLimitedAccess`, or `AnthropicSelfHostedEnvironmentAccess`. Principals who need Claude Console access require either `AnthropicFullAccess` or a custom policy that grants `aws-external-anthropic:AssumeConsole`. See [Console access](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#console-access).

<Note>
  `CreateInference` and `CreateBatchInference` are separate actions. Denying one does not block the other. If you intend to prevent all model calls, deny both.
</Note>


## Example policies

Source: https://platform.claude.com/llms-full.txt#example-policies

### Synchronous inference on a single workspace

Grants the minimal permissions for an IAM principal that runs inference against one production workspace:

<Note>
  `ListWorkspaces` is account-scoped (see [Provisioning automation](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#provisioning-automation)). If your service account needs to enumerate workspaces, add a separate `Allow` statement for `ListWorkspaces` with `Resource: "*"`.

  This policy assumes AWS SigV4 authentication. If the principal authenticates with an API key, add a separate `Allow` statement for `aws-external-anthropic:CallWithBearerToken` with `Resource: "*"`. `CallWithBearerToken` is a route-less action that does not bind to a workspace ARN. See [Per-customer workspace isolation](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#per-customer-workspace-isolation) for the two-statement pattern.
</Note>

### Per-customer workspace isolation

Restricts a role to a single workspace:

<Note>
  The `aws-external-anthropic:*` wildcard in the first statement includes account-scoped actions (`CreateWorkspace`, `ListWorkspaces`, `ListComplianceActivities`, and the external key actions) that the workspace ARN constraint silently filters out. This is consistent with the "isolation" intent (the role cannot create workspaces, enumerate workspaces, manage encryption key registrations, or read the compliance Activity Feed; it can still attach an already-registered key to its own workspace through `UpdateWorkspace`), but the policy contains permissions that have no effect. See [Provisioning automation](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#provisioning-automation) for the account-scoped pattern.

  `CallWithBearerToken` and `AssumeConsole` are route-less actions that do not bind to a workspace ARN. The second statement grants them on `Resource: "*"` so the role can authenticate with an API key and open the Claude Console. Omit this statement if the role uses SigV4 only and does not need Claude Console access.
</Note>

### Feature lockdown for a ZDR-sensitive workspace

Blocks batch processing and file upload on a specific workspace while leaving synchronous inference available. Useful when a workspace handles [Zero Data Retention (ZDR)](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) data that must not persist server-side. Attach this policy alongside an Allow policy such as `AnthropicInferenceAccess` or the [single-workspace example](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#synchronous-inference-on-a-single-workspace); on its own, a Deny-only policy grants no permissions:

<Note>
  This deny blocks creation only. Other file and batch actions are not denied unless you list them as well. For a complete lockdown where the workspace must never hold files or batches, also deny `aws-external-anthropic:GetFile`, `aws-external-anthropic:ListFiles`, `aws-external-anthropic:DeleteFile`, `aws-external-anthropic:GetBatchInference`, `aws-external-anthropic:ListBatchInferences`, `aws-external-anthropic:CancelBatchInference`, and `aws-external-anthropic:DeleteBatchInference`.
</Note>

### Provisioning automation

<Note>
  Besides the Admin API, you can create, update, or archive workspaces in the AWS Console or, with the Admin role, in the Claude Console.
</Note>

Grants a CI/CD role the actions needed to create and manage workspaces, without any inference permissions:

`CreateWorkspace` and `ListWorkspaces` are account-scoped operations. Specifying a workspace ARN on these actions has no effect; use `Resource: "*"`.


## See also

Source: https://platform.claude.com/llms-full.txt#see-also-11

* [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) for setup, authentication, and platform overview
* [AWS IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html) for IAM policy syntax and evaluation logic
* [AWS CloudTrail User Guide](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/) for audit logging configuration


---
title: IP addresses
url: https://platform.claude.com/docs/en/api/ip-addresses
description: Anthropic services use fixed IP addresses for both inbound and outbound connections. You can use these addresses to configure your firewall rules for secure access to the Claude API and Console. These addresses will not change without notice.
---

<Note>
  **[Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws):** The inbound endpoint (`aws-external-anthropic.{region}.api.aws`) resolves to AWS IP ranges. Outbound tool calls (MCP connector, web search, and web fetch) originate from the Anthropic ranges listed on this page. See the [AWS IP address ranges](https://docs.aws.amazon.com/vpc/latest/userguide/aws-ip-ranges.html) for inbound allowlisting.
</Note>


## Inbound IP addresses

Source: https://platform.claude.com/llms-full.txt#inbound-ip-addresses

These are the IP addresses where Anthropic services receive incoming connections.

### IPv4

`160.79.104.0/23`

### IPv6

`2607:6bc0::/48`


## Outbound IP addresses

Source: https://platform.claude.com/llms-full.txt#outbound-ip-addresses

These are the stable IP addresses that Anthropic uses for outbound requests (for example, when making MCP tool calls to external servers).

### IPv4

`160.79.104.0/21`

### Phased out IP addresses

The following IP addresses are no longer in use by Anthropic. If you have previously allowlisted these addresses, you should remove them from your firewall rules.

```text wrap
34.162.46.92/32
34.162.102.82/32
34.162.136.91/32
34.162.142.92/32
34.162.183.95/32
```


---
title: Rate limits
url: https://platform.claude.com/docs/en/api/rate-limits
description: To mitigate misuse and manage capacity on the API, limits are in place on how much an organization can use the Claude API.
---

<Note>
  **[Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws):** The rate limits on this page apply to Claude Platform on AWS, but billing and limit management differ. Billing is through AWS Marketplace (not Anthropic credit purchases). Organizations on Claude Platform on AWS are placed on the Start tier and do not move between usage tiers automatically. To request higher limits, contact your Anthropic account representative or [Anthropic support](https://support.claude.com); the **Request rate limit increase** flow is not available. Per-workspace rate limit configuration and [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) are not available on Claude Platform on AWS. For details, see [Rate limits and quotas on Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#rate-limits-and-quotas).
</Note>

There are two types of limits:

1. **Spend limits** set a maximum monthly cost an organization can incur for API usage.
2. **Rate limits** set the maximum number of API requests an organization can make over a defined period of time.

The API enforces service-configured limits at the organization level, but you may also set user-configurable limits for your organization's workspaces.


## About rate limits

Source: https://platform.claude.com/llms-full.txt#about-rate-limits

* Limits are designed to prevent API abuse, while minimizing impact on common customer usage patterns.
* Limits are defined by **usage tier**. Organizations are placed on a tier automatically based on usage history and account standing and can move to a higher tier over time as they use the API.
* New organizations and organizations with limited usage history may start in the Evaluation tier, with limits below the standard limits shown on this page while account history is established. These starting limits are part of how Anthropic prevents fraud and abuse, and they increase automatically as your organization builds usage history.
* Limits are set at the organization level. You can see your organization's tier and current limits on the [Rate limits](https://platform.claude.com/settings/limits) page in the [Claude Console](https://platform.claude.com/).
* You might hit rate limits over shorter time intervals. For instance, a rate of 60 requests per minute (RPM) might be enforced as 1 request per second. Short bursts of requests can exceed the limit and trigger rate limit errors.
* The following limits are the standard limits for each tier. If you need higher limits, see [Requesting higher limits](https://platform.claude.com/docs/en/api/rate-limits#requesting-higher-limits).
* The API uses the [token bucket algorithm](https://en.wikipedia.org/wiki/Token_bucket) to do rate limiting. This means that your capacity is continuously replenished up to your maximum limit, rather than being reset at fixed intervals.
* All limits described here represent maximum allowed usage, not guaranteed minimums. These limits are intended to reduce unintentional overspend and ensure fair distribution of resources among users.


## Spend limits

Source: https://platform.claude.com/llms-full.txt#spend-limits-2

<Note>
  **[Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws):** The same monthly spend caps apply, and requests stop at the cap in the same way. Billing and tier increases work differently; see [Spend limits on Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#spend-limits).
</Note>

Each of the Start, Build, and Scale tiers carries a monthly spend cap, which is the maximum your organization can spend on the API each calendar month. You can view your organization's monthly spend cap and set your own limit on the [Billing](https://platform.claude.com/settings/billing) page.

| Usage tier | Monthly spend cap |
| ---------- | ----------------- |
| Start      | $500 USD          |
| Build      | $1,000 USD        |
| Scale      | $200,000 USD      |

Organizations on the Custom tier have no monthly spend cap; limits are arranged with their account team.

### Reaching your spend cap

Once you reach your tier's spend cap, API usage pauses until 00:00 UTC on the first day of the next month, unless you request a higher limit sooner. While usage is paused, API requests return HTTP 429:

* The error type is `rate_limit_error`, the same as for a rate limit, but the response has no `retry-after` header. Retrying, including the SDKs' automatic retries, fails until access resumes.
* On the Messages API, `error.details.error_code` is `enforced_spend_limit_reached`. Use it to tell this response apart from a rate limit.
* Moving to a higher tier restores access; see [Requesting higher limits](https://platform.claude.com/docs/en/api/rate-limits#requesting-higher-limits).

### Setting your own spend limit

You can also set your own spend limit below your tier's cap to control costs:

<Steps>
  <Step title="Navigate to the Billing page">
    Go to [Settings > Billing](https://platform.claude.com/settings/billing) in the Claude Console.
  </Step>

  <Step title="Open the spend limit editor">
    In the **Spend limits** section, click **Adjust limit** (or **Set limit** if no limit is currently set).
  </Step>

  <Step title="Adjust your spend limit">
    Enter a new value. Your spend limit cannot exceed your current tier's cap.
  </Step>
</Steps>

When usage reaches a spend limit you set, requests return HTTP 400 with error type `invalid_request_error`. The message begins `You have reached your specified API usage limits`, or `You have reached your specified workspace API usage limits` for a workspace limit, and states when access resumes. Raise or remove the limit to restore access sooner.

Limits on the [Claude Code workspace](https://platform.claude.com/docs/en/manage-claude/workspaces#claude-code-workspace) are checked separately: Claude Code requests over that workspace's limit can instead receive a 429 that carries a `retry-after` header.


## Rate limits

Source: https://platform.claude.com/llms-full.txt#rate-limits-6

The rate limits for the Messages API are measured in requests per minute (RPM), input tokens per minute (ITPM), and output tokens per minute (OTPM) for each model class. If you exceed any of the rate limits you will get a [429 error](https://platform.claude.com/docs/en/api/errors) describing which rate limit was exceeded, along with a `retry-after` header indicating how long to wait.

<Note>
  You might also encounter 429 errors because of acceleration limits on the API if your organization has a sharp increase in usage. To avoid hitting acceleration limits, ramp up your traffic gradually and maintain consistent usage patterns.
</Note>

### Cache-aware ITPM

Many API providers use a combined "tokens per minute" (TPM) limit that may include all tokens, both cached and uncached, input and output. **For most Claude models, only uncached input tokens count toward your ITPM rate limits.** This is a key advantage that makes the rate limits effectively higher than they might initially appear.

ITPM rate limits are estimated at the beginning of each request, and the estimate is adjusted during the request to reflect the actual number of input tokens used.

Here's what counts toward ITPM:

* `input_tokens` (tokens after the last cache breakpoint) ✓ **Count toward ITPM**
* `cache_creation_input_tokens` (tokens being written to cache) ✓ **Count toward ITPM**
* `cache_read_input_tokens` (tokens read from cache) ✗ **Do NOT count toward ITPM** for most models

<Note>
  The `input_tokens` field only represents tokens that appear **after your last cache breakpoint**, not all input tokens in your request. To calculate total input tokens:

  ```text wrap
  total_input_tokens = cache_read_input_tokens + cache_creation_input_tokens + input_tokens
  ```

  This means when you have cached content, `input_tokens` will typically be much smaller than your total input. For example, with a 200k token cached document and a 50 token user question, you'd see `input_tokens: 50` even though the total input is 200,050 tokens.

  For rate limit purposes on most models, only `input_tokens` + `cache_creation_input_tokens` count toward your ITPM limit, making [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) an effective way to increase your effective throughput.
</Note>

**Example:** With a 2,000,000 ITPM limit and an 80% cache hit rate, you could effectively process 10,000,000 total input tokens per minute (2M uncached + 8M cached), because cached tokens don't count toward your rate limit.

<Note>
  Claude Haiku 3.5 (marked with footnote 4 in the following rate limit tables) also counts `cache_read_input_tokens` toward ITPM rate limits.

  For all other models, cached input tokens do not count toward rate limits and are billed at the [cache read rate](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing), a fraction of the base input price. This means you can achieve significantly higher effective throughput by using [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).
</Note>

To make the most of your rate limits, cache repeated content such as system instructions and prompts, large context documents, tool definitions, and conversation history; see [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) for guidance. With effective caching, you can substantially increase your actual throughput without raising your rate limits. Monitor your cache hit rate on the [Usage page](https://platform.claude.com/usage) to tune your caching strategy.

OTPM rate limits are evaluated in real time as output tokens are produced, counting only the actual tokens generated. The `max_tokens` parameter does not factor into OTPM rate limit calculations, so there is no rate limit downside to setting a higher `max_tokens` value.

Rate limits are applied separately for each model; therefore you can use different models up to their respective limits simultaneously. You can check your current rate limits and behavior on the [Rate limits](https://platform.claude.com/settings/limits) page in the Claude Console, or read the configured limits programmatically with the [Rate Limits API](https://platform.claude.com/docs/en/manage-claude/rate-limits-api).

<Note>
  Rate limits are currently shared across all `inference_geo` values. Requests with `inference_geo: "us"` and `inference_geo: "global"` draw from the same rate limit pool.
</Note>

<Tabs>
  <Tab title="Start tier">
    | Model                                                                                                                                 | Maximum requests per minute (RPM) | Maximum input tokens per minute (ITPM) | Maximum output tokens per minute (OTPM) |
    | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | -------------------------------------- | --------------------------------------- |
    | Claude Fable 5.x1                                                                                                                     | 1,000                             | 500,000                                | 100,000                                 |
    | Claude Opus 5                                                                                                                         | 1,000                             | 2,000,000                              | 400,000                                 |
    | Claude Opus 4.x2                                                                                                                      | 1,000                             | 2,000,000                              | 400,000                                 |
    | Claude Sonnet 5                                                                                                                       | 1,000                             | 2,000,000                              | 400,000                                 |
    | Claude Sonnet 4.x3                                                                                                                    | 1,000                             | 2,000,000                              | 400,000                                 |
    | Claude Haiku 4.5                                                                                                                      | 1,000                             | 2,000,000                              | 400,000                                 |
    | Claude Haiku 3.5 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)) | 1,000                             | 100,0004                               | 20,000                                  |
  </Tab>

  <Tab title="Build tier">
    | Model                                                                                                                                 | Maximum requests per minute (RPM) | Maximum input tokens per minute (ITPM) | Maximum output tokens per minute (OTPM) |
    | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | -------------------------------------- | --------------------------------------- |
    | Claude Fable 5.x1                                                                                                                     | 2,000                             | 1,500,000                              | 300,000                                 |
    | Claude Opus 5                                                                                                                         | 5,000                             | 5,000,000                              | 1,000,000                               |
    | Claude Opus 4.x2                                                                                                                      | 5,000                             | 5,000,000                              | 1,000,000                               |
    | Claude Sonnet 5                                                                                                                       | 5,000                             | 5,000,000                              | 1,000,000                               |
    | Claude Sonnet 4.x3                                                                                                                    | 5,000                             | 5,000,000                              | 1,000,000                               |
    | Claude Haiku 4.5                                                                                                                      | 5,000                             | 5,000,000                              | 1,000,000                               |
    | Claude Haiku 3.5 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)) | 2,000                             | 200,0004                               | 40,000                                  |
  </Tab>

  <Tab title="Scale tier">
    | Model                                                                                                                                 | Maximum requests per minute (RPM) | Maximum input tokens per minute (ITPM) | Maximum output tokens per minute (OTPM) |
    | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | -------------------------------------- | --------------------------------------- |
    | Claude Fable 5.x1                                                                                                                     | 4,000                             | 4,000,000                              | 800,000                                 |
    | Claude Opus 5                                                                                                                         | 10,000                            | 10,000,000                             | 2,000,000                               |
    | Claude Opus 4.x2                                                                                                                      | 10,000                            | 10,000,000                             | 2,000,000                               |
    | Claude Sonnet 5                                                                                                                       | 10,000                            | 10,000,000                             | 2,000,000                               |
    | Claude Sonnet 4.x3                                                                                                                    | 10,000                            | 10,000,000                             | 2,000,000                               |
    | Claude Haiku 4.5                                                                                                                      | 10,000                            | 10,000,000                             | 2,000,000                               |
    | Claude Haiku 3.5 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)) | 4,000                             | 400,0004                               | 80,000                                  |
  </Tab>

  <Tab title="Custom tier">
    If you need limits higher than the Scale tier, contact sales through the [Rate limits](https://platform.claude.com/settings/limits) page in the Claude Console.
  </Tab>
</Tabs>

*1 Fable rate limit is a total limit that applies to combined traffic across Claude Fable 5.1 and Claude Fable 5. Claude Mythos 5.1 and Claude Mythos 5 share a separate combined limit on the same terms.*

*2 Opus rate limit is a total limit that applies to combined traffic across Claude Opus 4.8, Opus 4.7, Opus 4.6, and Opus 4.5. Claude Opus 5 has a separate rate limit and is not part of this combined bucket.*

*3 Sonnet 4.x rate limit is a total limit that applies to combined traffic across Sonnet 4.6 and Sonnet 4.5. Claude Sonnet 5 has a separate rate limit and is not part of this combined bucket.*

*4 Limit counts `cache_read_input_tokens` toward ITPM usage.*

### Message Batches API

The Message Batches API has its own set of rate limits which are shared across all models. These include a requests per minute (RPM) limit to all API endpoints and a limit on the number of batch requests that can be in the processing queue at the same time. A "batch request" here refers to part of a Message Batch. You may create a Message Batch containing thousands of batch requests, each of which count toward this limit. A batch request is considered part of the processing queue when it has yet to be successfully processed by the model.

<Tabs>
  <Tab title="Start tier">
    | Maximum requests per minute (RPM) | Maximum batch requests in processing queue | Maximum batch requests per batch |
    | --------------------------------- | ------------------------------------------ | -------------------------------- |
    | 1,000                             | 200,000                                    | 100,000                          |
  </Tab>

  <Tab title="Build tier">
    | Maximum requests per minute (RPM) | Maximum batch requests in processing queue | Maximum batch requests per batch |
    | --------------------------------- | ------------------------------------------ | -------------------------------- |
    | 2,000                             | 300,000                                    | 100,000                          |
  </Tab>

  <Tab title="Scale tier">
    | Maximum requests per minute (RPM) | Maximum batch requests in processing queue | Maximum batch requests per batch |
    | --------------------------------- | ------------------------------------------ | -------------------------------- |
    | 4,000                             | 500,000                                    | 100,000                          |
  </Tab>

  <Tab title="Custom tier">
    If you need limits higher than the Scale tier, contact sales through the [Rate limits](https://platform.claude.com/settings/limits) page in the Claude Console.
  </Tab>
</Tabs>

### Managed Agents

[Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) endpoints are rate-limited per organization. These limits are separate from the Messages API rate limits above.

| Operation                                                          | Limit                     |
| ------------------------------------------------------------------ | ------------------------- |
| Create endpoints (for example, agents, sessions, and environments) | 300 requests per minute   |
| Read endpoints (for example, retrieve, list, and stream)           | 1,200 requests per minute |

### Files API

[Files API](https://platform.claude.com/docs/en/build-with-claude/files) requests have their own per-organization limit, shared across upload, list, retrieve, download, and delete operations and separate from the Messages API limits described earlier on this page. See [Files API rate limits](https://platform.claude.com/docs/en/build-with-claude/files#rate-limits) for the current value.

### Fast mode rate limits

When using [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) (research preview) with `speed: "fast"` on Claude Opus 5 or Opus 4.8, dedicated rate limits apply that are separate from standard Opus rate limits. When fast mode rate limits are exceeded, the API returns a `429` error with a `retry-after` header. Fast mode is not available on Claude Opus 4.7 (requests return an error) or Claude Opus 4.6 (requests to `claude-opus-4-6` with `speed: "fast"` run at standard speed). See [Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode#supported-models).

The response includes `anthropic-fast-*` headers that indicate your fast mode rate limit status. See [Fast mode rate limits](https://platform.claude.com/docs/en/build-with-claude/fast-mode#rate-limits) for details on these headers.

### Monitoring your rate limits in the Console

You can monitor your rate limit usage on the [Usage](https://platform.claude.com/usage) page of the [Claude Console](https://platform.claude.com/).

In addition to providing token and request charts, the Usage page provides two separate rate limit charts. Use these charts to see what headroom you have to grow, identify when you may be hitting peak use, understand what rate limits to request, and learn how to improve your caching rates. The charts visualize a number of metrics for a given rate limit (for example, per model):

* The **Rate Limit - Input Tokens** chart includes:

  * Hourly maximum uncached input tokens per minute
  * Your current input tokens per minute rate limit
  * The cache rate for your input tokens (that is, the percentage of input tokens read from the cache)

* The **Rate Limit - Output Tokens** chart includes:

  * Hourly maximum output tokens per minute
  * Your current output tokens per minute rate limit


## Requesting higher limits

Source: https://platform.claude.com/llms-full.txt#requesting-higher-limits

To request higher rate limits or a higher monthly spend cap, use **Request rate limit increase** on the [Rate limits](https://platform.claude.com/settings/limits) page. Anthropic support can also raise limits; for urgent needs, contact [Anthropic support](https://support.claude.com).

<Note>
  **[Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws):** The **Request rate limit increase** flow is not available. Contact your Anthropic account representative or [Anthropic support](https://support.claude.com), and include the models you need raised, your peak input and output tokens per minute for each model, and roughly what share of your input is cached or repeated context. See [Rate limits and quotas on Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#rate-limits-and-quotas).
</Note>


## Setting lower limits for Workspaces

Source: https://platform.claude.com/llms-full.txt#setting-lower-limits-for-workspaces

For more about workspaces, see [Workspaces](https://platform.claude.com/docs/en/manage-claude/workspaces).

To protect Workspaces in your Organization from potential overuse, you can set custom spend and rate limits per Workspace.

Example: If your Organization's limit is 40,000 input tokens per minute and 8,000 output tokens per minute, you might limit one Workspace to 30,000 input tokens per minute. This protects other Workspaces from potential overuse and ensures a more equitable distribution of resources across your Organization. The remaining unused tokens per minute (or more, if that Workspace doesn't use the limit) are then available for other Workspaces to use.

Note:

* You can't set limits on the default Workspace.
* If not set, Workspace limits match the Organization's limit.
* Workspace limits are set per limiter type (such as requests per minute, input tokens per minute, or output tokens per minute).
* Organization-wide limits always apply, even if Workspace limits add up to more.

To read your current organization and workspace rate limits programmatically, use the [Rate Limits API](https://platform.claude.com/docs/en/manage-claude/rate-limits-api).


## Response headers

Source: https://platform.claude.com/llms-full.txt#response-headers

The API response includes headers that show you the rate limit enforced, current usage, and when the limit will be reset.

The following headers are returned:

| Header                                        | Description                                                                                                                                                                                                                             |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `retry-after`                                 | The number of seconds to wait until you can retry the request. Earlier retries will fail. Not sent with the spend-cap 429 (see [Reaching your spend cap](https://platform.claude.com/docs/en/api/rate-limits#reaching-your-spend-cap)). |
| `anthropic-ratelimit-requests-limit`          | The maximum number of requests allowed within any rate limit period.                                                                                                                                                                    |
| `anthropic-ratelimit-requests-remaining`      | The number of requests remaining before being rate limited.                                                                                                                                                                             |
| `anthropic-ratelimit-requests-reset`          | The time when the request rate limit will be fully replenished, provided in RFC 3339 format.                                                                                                                                            |
| `anthropic-ratelimit-tokens-limit`            | The maximum number of tokens allowed within any rate limit period.                                                                                                                                                                      |
| `anthropic-ratelimit-tokens-remaining`        | The number of tokens remaining (rounded to the nearest thousand) before being rate limited.                                                                                                                                             |
| `anthropic-ratelimit-tokens-reset`            | The time when the token rate limit will be fully replenished, provided in RFC 3339 format.                                                                                                                                              |
| `anthropic-ratelimit-input-tokens-limit`      | The maximum number of input tokens allowed within any rate limit period.                                                                                                                                                                |
| `anthropic-ratelimit-input-tokens-remaining`  | The number of input tokens remaining (rounded to the nearest thousand) before being rate limited.                                                                                                                                       |
| `anthropic-ratelimit-input-tokens-reset`      | The time when the input token rate limit will be fully replenished, provided in RFC 3339 format.                                                                                                                                        |
| `anthropic-ratelimit-output-tokens-limit`     | The maximum number of output tokens allowed within any rate limit period.                                                                                                                                                               |
| `anthropic-ratelimit-output-tokens-remaining` | The number of output tokens remaining (rounded to the nearest thousand) before being rate limited.                                                                                                                                      |
| `anthropic-ratelimit-output-tokens-reset`     | The time when the output token rate limit will be fully replenished, provided in RFC 3339 format.                                                                                                                                       |
| `anthropic-priority-input-tokens-limit`       | The maximum number of Priority Tier input tokens allowed within any rate limit period. (Priority Tier only)                                                                                                                             |
| `anthropic-priority-input-tokens-remaining`   | The number of Priority Tier input tokens remaining (rounded to the nearest thousand) before being rate limited. (Priority Tier only)                                                                                                    |
| `anthropic-priority-input-tokens-reset`       | The time when the Priority Tier input token rate limit will be fully replenished, provided in RFC 3339 format. (Priority Tier only)                                                                                                     |
| `anthropic-priority-output-tokens-limit`      | The maximum number of Priority Tier output tokens allowed within any rate limit period. (Priority Tier only)                                                                                                                            |
| `anthropic-priority-output-tokens-remaining`  | The number of Priority Tier output tokens remaining (rounded to the nearest thousand) before being rate limited. (Priority Tier only)                                                                                                   |
| `anthropic-priority-output-tokens-reset`      | The time when the Priority Tier output token rate limit will be fully replenished, provided in RFC 3339 format. (Priority Tier only)                                                                                                    |

The `anthropic-ratelimit-tokens-*` headers display the values for the most restrictive limit currently in effect. For instance, if you have exceeded the Workspace per-minute token limit, the headers will contain the Workspace per-minute token rate limit values. If Workspace limits do not apply, the headers will return the total tokens remaining, where total is the sum of input and output tokens. This approach ensures that you have visibility into the most relevant constraint on your current API usage. To see which Workspace a request counted against, read the `anthropic-workspace-id` [response header](https://platform.claude.com/docs/en/api/overview#response-headers), which carries the ID of the Workspace that your API key or access token resolved to.


---
title: Service tiers
url: https://platform.claude.com/docs/en/api/service-tiers
description: Different tiers of service allow you to balance availability, performance, and predictable costs based on your application's needs.
---

<Warning>
  Priority Tier capacity commitments are no longer available for purchase. Organizations with an existing commitment can continue to use Priority Tier through their contract end date, and this page remains available as a reference for them. If you need guaranteed capacity, [contact sales](https://claude.com/contact-sales).
</Warning>

Anthropic offers three service tiers:

* **Priority Tier:** Available only to organizations with an existing capacity commitment
* **Standard:** Default tier for both piloting and scaling everyday use cases
* **Batch:** Best for asynchronous workflows that can wait or benefit from being outside your normal capacity


## Standard tier

Source: https://platform.claude.com/llms-full.txt#standard-tier

The standard tier is the default service tier for all API requests. The API prioritizes these requests alongside all other requests with best-effort availability.


## Priority Tier

Source: https://platform.claude.com/llms-full.txt#priority-tier

The API prioritizes requests in this tier over all other requests. This prioritization helps minimize ["server overloaded" errors](https://platform.claude.com/docs/en/api/errors#http-errors), even during peak times.

For more information, see [Existing Priority Tier commitments](https://platform.claude.com/docs/en/api/service-tiers#existing-priority-tier-commitments).


## How requests get assigned tiers

Source: https://platform.claude.com/llms-full.txt#how-requests-get-assigned-tiers

When handling a request, Anthropic decides to assign a request to Priority Tier in the following scenarios:

* Your organization has sufficient Priority Tier capacity **input** tokens per minute
* Your organization has sufficient Priority Tier capacity **output** tokens per minute

Anthropic counts usage against Priority Tier capacity as follows:

**Input tokens**

* Cache reads as 0.1 tokens per token read from the cache
* Cache writes as 1.25 tokens per token written to the cache with a 5 minute TTL
* Cache writes as 2.00 tokens per token written to the cache with a 1 hour TTL
* For [US-only inference](https://platform.claude.com/docs/en/manage-claude/data-residency) (`inference_geo: "us"`) requests on Claude 4.6 and later models, input tokens are 1.1 tokens per token
* All other input tokens are 1 token per token

**Output tokens**

* For [US-only inference](https://platform.claude.com/docs/en/manage-claude/data-residency) (`inference_geo: "us"`) requests on Claude 4.6 and later models, output tokens are 1.1 tokens per token
* All other output tokens are 1 token per token

Otherwise, requests proceed at standard tier.

<Note>
  These burndown rates reflect the relative pricing of each token type. For example, US-only inference is priced at 1.1x on Claude 4.6 and later models, so each token consumed with `inference_geo: "us"` draws down 1.1 tokens from your Priority Tier capacity.
</Note>

<Note>
  Requests assigned Priority Tier pull from both the Priority Tier capacity and the regular rate limits. If servicing the request would exceed the rate limits, the request is declined.
</Note>


## Using service tiers

Source: https://platform.claude.com/llms-full.txt#using-service-tiers

You can control which service tiers can be used for a request by setting the `service_tier` parameter:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-4-8",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello, Claude!"}],
      "service_tier": "auto"
    }'

bash CLI
  ant messages create --transform usage.service_tier --raw-output <<'YAML'
  model: claude-opus-4-8
  max_tokens: 1024
  messages:
    - role: user
      content: Hello, Claude!
  service_tier: auto  # Automatically use Priority Tier when available, fallback to standard
  YAML

python Python
  client = anthropic.Anthropic()

  message = client.messages.create(
      model="claude-opus-4-8",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude!"}],
      service_tier="auto",  # Automatically use Priority Tier when available, fallback to standard
  )
  print(message.usage.service_tier)

typescript TypeScript
  const client = new Anthropic();

  const message = await client.messages.create({
    model: "claude-opus-4-8",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude!" }],
    service_tier: "auto" // Automatically use Priority Tier when available, fallback to standard
  });
  console.log(message.usage.service_tier);

csharp C#
  AnthropicClient client = new();

  var message = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus4_8,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello, Claude!" }],
      ServiceTier = ServiceTier.Auto, // Automatically use Priority Tier when available, fallback to standard
  });
  Console.WriteLine(message.Usage.ServiceTier);

go Go
  client := anthropic.NewClient()

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus4_8,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, Claude!")),
  	},
  	// Automatically use Priority Tier when available, fallback to standard
  	ServiceTier: anthropic.MessageNewParamsServiceTierAuto,
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(message.Usage.ServiceTier)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_4_8)
      .maxTokens(1024L)
      .addUserMessage("Hello, Claude!")
      // Automatically use Priority Tier when available, fallback to standard
      .serviceTier(MessageCreateParams.ServiceTier.AUTO)
      .build();

  Message message = client.messages().create(params);
  IO.println(message.usage().serviceTier().orElseThrow());

php PHP
  $client = new Client();

  $message = $client->messages->create(
      model: 'claude-opus-4-8',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude!']],
      serviceTier: 'auto', // Automatically use Priority Tier when available, fallback to standard
  );
  echo $message->usage->serviceTier;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-4-8",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude!" }],
    service_tier: :auto # Automatically use Priority Tier when available, fallback to standard
  )
  puts(message.usage.service_tier)

json
{
  "usage": {
    "input_tokens": 410,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0,
    "output_tokens": 585,
    "service_tier": "priority"
  }
}

text wrap
anthropic-priority-input-tokens-limit: 10000
anthropic-priority-input-tokens-remaining: 9618
anthropic-priority-input-tokens-reset: 2025-01-12T23:11:59Z
anthropic-priority-output-tokens-limit: 10000
anthropic-priority-output-tokens-remaining: 6000
anthropic-priority-output-tokens-reset: 2025-01-12T23:12:21Z
```

You can use the presence of these headers to detect if your request was eligible for Priority Tier, even if it was over the limit.


## Existing Priority Tier commitments

Source: https://platform.claude.com/llms-full.txt#existing-priority-tier-commitments

A Priority Tier commitment consists of:

* A number of input tokens per minute
* A number of output tokens per minute
* A commitment duration (1, 3, 6, or 12 months)
* A specific model version

Priority Tier targets 99.5% uptime with prioritized computational resources. Requests beyond your committed capacity automatically fall back to standard tier.

### Supported models

Priority Tier is supported on all available Claude models except Claude Fable 5.1, Claude Mythos 5.1, Claude Mythos 5, [Claude Mythos Preview](https://anthropic.com/glasswing), Claude Opus 5, and Claude Sonnet 5.

Check the [Models overview](https://platform.claude.com/docs/en/models/overview) for more details on available models.


---
title: Supported regions
url: https://platform.claude.com/docs/en/api/supported-regions
description: "Here are the countries, regions, and territories we can currently support access from:"
---

* Albania
* Algeria
* Andorra
* Angola
* Antigua and Barbuda
* Argentina
* Armenia
* Australia
* Austria
* Azerbaijan
* Bahamas
* Bahrain
* Bangladesh
* Barbados
* Belgium
* Belize
* Benin
* Bhutan
* Bolivia
* Bosnia and Herzegovina
* Botswana
* Brazil
* Brunei
* Bulgaria
* Burkina Faso
* Burundi
* Cabo Verde
* Cambodia
* Cameroon
* Canada
* Chad
* Chile
* Colombia
* Comoros
* Congo, Republic of the
* Costa Rica
* Côte d'Ivoire
* Croatia
* Cyprus
* Czechia (Czech Republic)
* Denmark
* Djibouti
* Dominica
* Dominican Republic
* Ecuador
* Egypt
* El Salvador
* Equatorial Guinea
* Estonia
* Eswatini
* Fiji
* Finland
* France
* Gabon
* Gambia
* Georgia
* Germany
* Ghana
* Greece
* Grenada
* Guatemala
* Guinea
* Guinea-Bissau
* Guyana
* Haiti
* Holy See (Vatican City)
* Honduras
* Hungary
* Iceland
* India
* Indonesia
* Iraq
* Ireland
* Israel
* Italy
* Jamaica
* Japan
* Jordan
* Kazakhstan
* Kenya
* Kiribati
* Kuwait
* Kyrgyzstan
* Laos
* Latvia
* Lebanon
* Lesotho
* Liberia
* Liechtenstein
* Lithuania
* Luxembourg
* Madagascar
* Malawi
* Malaysia
* Maldives
* Malta
* Marshall Islands
* Mauritania
* Mauritius
* Mexico
* Micronesia
* Moldova
* Monaco
* Mongolia
* Montenegro
* Morocco
* Mozambique
* Namibia
* Nauru
* Nepal
* Netherlands
* New Zealand
* Niger
* Nigeria
* North Macedonia
* Norway
* Oman
* Pakistan
* Palau
* Palestine
* Panama
* Papua New Guinea
* Paraguay
* Peru
* Philippines
* Poland
* Portugal
* Qatar
* Romania
* Rwanda
* Saint Kitts and Nevis
* Saint Lucia
* Saint Vincent and the Grenadines
* Samoa
* San Marino
* Sao Tome and Principe
* Saudi Arabia
* Senegal
* Serbia
* Seychelles
* Sierra Leone
* Singapore
* Slovakia
* Slovenia
* Solomon Islands
* South Africa
* South Korea
* Spain
* Sri Lanka
* Suriname
* Sweden
* Switzerland
* Taiwan
* Tajikistan
* Tanzania
* Thailand
* Timor-Leste, Democratic Republic of
* Togo
* Tonga
* Trinidad and Tobago
* Tunisia
* Turkey
* Turkmenistan
* Tuvalu
* Uganda
* Ukraine (except Crimea, Donetsk, and Luhansk regions)
* United Arab Emirates
* United Kingdom
* United States of America
* Uruguay
* Uzbekistan
* Vanuatu
* Vietnam
* Zambia
* Zimbabwe


---
title: Versions
url: https://platform.claude.com/docs/en/api/versioning
description: "When making API requests, you must send an `anthropic-version` request header. For example, `anthropic-version: 2023-06-01`. If you are using the [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview), this is handled for you automatically."
---

For any given version with the Messages API, Anthropic preserves:

* Existing input parameters
* Existing output parameters

However, Anthropic may do the following:

* Add additional optional inputs
* Add additional values to the output
* Change conditions for specific error types
* Add new variants to enum-like output values (for example, streaming event types)

Generally, if you are using the API as documented in this reference, Anthropic will not break your usage.


## Version history

Source: https://platform.claude.com/llms-full.txt#version-history

Anthropic recommends using the latest API version whenever possible. Previous versions are considered deprecated and may be unavailable for new users.

* `2023-06-01`

  * New format for [streaming](https://platform.claude.com/docs/en/build-with-claude/streaming) server-sent events (SSE):

    * Completions are incremental. For example, `" Hello"`, `" my"`, `" name"`, `" is"`, `" Claude." `instead of `" Hello"`, `" Hello my"`, `" Hello my name"`, `" Hello my name is"`, `" Hello my name is Claude."`.
    * All events are [named events](https://developer.mozilla.org/en-US/Web/API/Server-sent%5Fevents/Using%5Fserver-sent%5Fevents#named%5Fevents), rather than [data-only events](https://developer.mozilla.org/en-US/Web/API/Server-sent%5Fevents/Using%5Fserver-sent%5Fevents#data-only%5Fmessages).
    * Removed unnecessary `data: [DONE]` event.

  * Removed legacy `exception` and `truncated` values in responses.

* `2023-01-01`: Initial release.


### Claude Code

---
title: Trigger a routine through the API
url: https://platform.claude.com/docs/en/api/claude-code/routines-fire
description: Start a Claude Code routine session on demand by sending an authenticated POST request.
---

<Warning>
  This is an experimental API. Request and response shapes, rate limits, and token semantics might change. Breaking changes ship behind new dated beta header versions, and the two previous header versions continue to work so that callers have time to migrate.
</Warning>

[Claude Code](https://code.claude.com/docs) is Anthropic's agentic coding tool. [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) runs Claude Code sessions on Anthropic-managed cloud infrastructure at claude.ai/code, and a [routine](https://code.claude.com/docs/en/routines) is a saved configuration there: a prompt, one or more repositories, and connectors, packaged so it can run unattended on a schedule, in response to GitHub events, or when called over HTTP.

This endpoint is the HTTP entry point. POSTing to it starts a new run of an existing routine and returns the resulting session ID and URL. Typical callers are alerting systems, CI pipelines, and internal tools that need to start a Claude Code session programmatically.

Calling this endpoint requires a claude.ai account on a Pro, Max, Team, or Enterprise plan with [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) enabled. Authenticate with a per-routine bearer token created in the Claude Code web UI rather than a Claude API key.


## Differences from the Claude Platform

Source: https://platform.claude.com/llms-full.txt#differences-from-the-claude-platform

The routine fire endpoint belongs to the Claude Code product surface, which differs from the Claude Platform APIs and SDKs in a few ways:

| Aspect         | This endpoint                                                                                                                               | Claude Platform APIs                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Authentication | `Authorization: Bearer` with a per-routine token (`sk-ant-oat01-...`) created at [claude.ai/code/routines](https://claude.ai/code/routines) | `x-api-key` with a Claude API key from Claude Console                                           |
| Token scope    | One routine only; no read access                                                                                                            | Workspace-level                                                                                 |
| SDK support    | None                                                                                                                                        | Available in all [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) |
| Billing        | Claude Code subscription usage on claude.ai                                                                                                 | Claude Platform usage                                                                           |
| Path namespace | `/v1/claude_code/...`                                                                                                                       | `/v1/...`                                                                                       |
| Stability      | Experimental; requires `anthropic-beta: experimental-cc-routine-2026-04-01`                                                                 | Stable or standard beta                                                                         |


## Before you begin

Source: https://platform.claude.com/llms-full.txt#before-you-begin-6

To call this endpoint, you need:

1. A routine created at [claude.ai/code/routines](https://claude.ai/code/routines).
2. A bearer token generated for that routine: open the routine for editing, click **Add another trigger** under **Select a trigger**, choose **API**, then click **Generate token** in the modal window. The token is shown once and cannot be retrieved later.

See [Add an API trigger](https://code.claude.com/docs/en/routines#add-an-api-trigger) in the Claude Code documentation for the full setup walkthrough.


## Trigger a routine

Source: https://platform.claude.com/llms-full.txt#trigger-a-routine

Every request must include the `anthropic-beta: experimental-cc-routine-2026-04-01` header. Requests without it return `400 invalid_request_error`.

The Claude Code web UI provides the full URL alongside the token when you add an API trigger, so most integrations store both as secrets and call the endpoint directly. The following examples show a shell call and a GitHub Actions step that triggers the routine on CI failure.

```bash cURL
curl -X POST https://api.anthropic.com/v1/claude_code/routines/$ROUTINE_ID/fire \
  -H "Authorization: Bearer $ROUTINE_TOKEN" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sentry alert SEN-4521 fired in prod. Stack trace attached."}'

yaml GitHub Actions
- if: failure()
  env:
    ROUTINE_FIRE_URL: ${{ secrets.ROUTINE_FIRE_URL }}
    ROUTINE_FIRE_TOKEN: ${{ secrets.ROUTINE_FIRE_TOKEN }}
  run: |
    curl -X POST "$ROUTINE_FIRE_URL" \
      -H "Authorization: Bearer $ROUTINE_FIRE_TOKEN" \
      -H "anthropic-version: 2023-06-01" \
      -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
      -H "Content-Type: application/json" \
      -d "{\"text\": \"CI failed: $GITHUB_WORKFLOW run $GITHUB_RUN_ID on $GITHUB_REF\"}"

json
{
  "type": "routine_fire",
  "claude_code_session_id": "session_01HJKLMNOPQRSTUVWXYZ",
  "claude_code_session_url": "https://claude.ai/code/session_01HJKLMNOPQRSTUVWXYZ"
}

json
{
  "type": "error",
  "error": {
    "type": "not_found_error",
    "message": "<string>"
  }
}
```

| HTTP status | Error type              | Cause                                                                                                                                                                                                         |
| ----------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 400         | `invalid_request_error` | Missing or invalid `anthropic-beta` header, `text` exceeds 65,536 characters, or the routine is paused (see [Edit and control routines](https://code.claude.com/docs/en/routines#edit-and-control-routines)). |
| 401         | `authentication_error`  | No bearer token in the `Authorization` header, or the token does not match this routine.                                                                                                                      |
| 403         | `permission_error`      | The account or organization does not have access to this endpoint.                                                                                                                                            |
| 404         | `not_found_error`       | The routine does not exist.                                                                                                                                                                                   |
| 429         | `rate_limit_error`      | The account's routine run limit or usage limit has been reached. The response includes a `Retry-After` header indicating when the window resets.                                                              |
| 500         | `api_error`             | An unexpected server error. Retry with exponential backoff; if the error persists, contact support with the request ID.                                                                                       |
| 503         | `overloaded_error`      | The service is temporarily overloaded. Retry after a short delay. The Claude Platform returns 529 for this error type; this endpoint returns 503.                                                             |


## Authentication

Source: https://platform.claude.com/llms-full.txt#authentication-10

The bearer token is scoped to a single routine. A compromised token can only trigger that routine; it grants no read access, no access to other routines, and no access to account data.

Generate and revoke tokens from the routine's API trigger settings at [claude.ai/code/routines](https://claude.ai/code/routines). There is no public API for token management. Generating a new token revokes the previous one.


## Idempotency

Source: https://platform.claude.com/llms-full.txt#idempotency

Each successful request creates a new session. There is no idempotency key. If a webhook caller retries, the endpoint creates multiple sessions.


## Rate limits

Source: https://platform.claude.com/llms-full.txt#rate-limits-7

Routine runs count against a per-account daily allowance that varies by plan, and the resulting sessions draw down the same Claude Code subscription usage as interactive sessions. When either limit is reached, the endpoint returns `429 rate_limit_error` with a `Retry-After` header. Organizations with extra usage enabled continue past the included allowance on metered overage.

View your remaining daily runs at [claude.ai/code/routines](https://claude.ai/code/routines). To learn how routine usage interacts with subscription limits and extra usage billing, see [Usage and limits](https://code.claude.com/docs/en/routines#usage-and-limits) in the Claude Code documentation.


## SDK support

Source: https://platform.claude.com/llms-full.txt#sdk-support

This endpoint is not in the Anthropic SDKs. Its token model differs from API key authentication, and typical callers such as CI jobs and alerting webhooks send the request directly.


## See also

Source: https://platform.claude.com/llms-full.txt#see-also-12

* [Automate work with routines](https://code.claude.com/docs/en/routines) in the Claude Code documentation
* [Beta headers](https://platform.claude.com/docs/en/api/beta-headers)
* [Errors](https://platform.claude.com/docs/en/api/errors)


## Claude API skill

Source: https://platform.claude.com/llms-full.txt#claude-api-skill

---
title: Claude API skill
url: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill
description: An open-source Agent Skill that provides Claude with up-to-date API reference material, SDK documentation, and best practices for building applications with the Claude API and Claude Managed Agents.
---

The `claude-api` skill is an open-source [Agent Skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) that provides Claude with detailed, up-to-date reference material for building applications on two Anthropic surfaces:

* **Messages API:** The primary surface for single requests, streaming chat, tool use, batch processing, prompt caching, structured outputs, and custom agent loops.
* **Claude Managed Agents (beta):** An Anthropic-hosted surface for server-managed stateful agents with Anthropic-hosted tool execution, persistent agent configs, and per-session sandboxes.

It covers eight programming languages for both the Messages API and Managed Agents: Python, TypeScript, C#, Go, Java, PHP, Ruby, and cURL.

The skill comes bundled with [Claude Code](https://code.claude.com/docs/en/overview) and is also available in the open-source [Anthropic skills repository](https://github.com/anthropics/skills), where you can install it in any environment that supports Agent Skills.

The skill uses [progressive disclosure](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work) to keep context efficient: Claude loads only the documentation relevant to your project's language, surface (Messages API or Managed Agents), and the specific task at hand (tool use, streaming, batches, and so on), rather than loading everything at once.


## What the skill provides

Source: https://platform.claude.com/llms-full.txt#what-the-skill-provides

When triggered, the skill equips Claude with:

**For the Messages API:**

* **Language-specific SDK documentation:** Installation, quick start, common patterns, and error handling for your project's language
* **Tool use guidance:** Language-specific examples and [conceptual foundations](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) for function calling, including the beta tool runner where available
* **Streaming patterns:** Implementation details for building chat UIs and handling incremental display
* **Batch processing:** Offline batch processing at 50% cost
* **Prompt caching:** Prefix-stability design, breakpoint placement, and silent-invalidator audit
* **Model migration:** Step-by-step guidance for migrating to newer Claude models (including the breaking changes and behavior shifts on [Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/migration-guide#migrating-from-claude-opus-4-8-to-claude-opus-5) and [Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/migration-guide))
* **Current model information:** Model IDs, context window sizes, and pricing
* **Common pitfalls:** Detailed guidance on avoiding frequent mistakes when integrating with the API

**For Managed Agents (beta):**

* **Onboarding flow:** An interview-driven walkthrough for setting up a new Managed Agent from scratch, available through the `/claude-api managed-agents-onboard` subcommand
* **Language-specific Managed Agents docs:** Creating persistent agents, starting sessions, streaming events, and handling tool confirmations for Python, TypeScript, C#, Go, Java, PHP, Ruby, and cURL
* **Client patterns:** Lossless stream reconnect, `processed_at` queued/processed gate, interrupt handling, file-mount gotchas, and credential handling
* **Deployment constraints:** Managed Agents is available on the Claude API and [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) only (not on Amazon Bedrock, Google Cloud, or Microsoft Foundry). The skill routes other deployments to the Messages API and tool use instead.


## When the skill activates

Source: https://platform.claude.com/llms-full.txt#when-the-skill-activates

The skill activates in two ways:

**Automatic activation** occurs when:

* Your code imports an Anthropic SDK (`anthropic` for Python, `@anthropic-ai/sdk` for TypeScript/JavaScript)
* You ask Claude to help build, debug, or optimize something with the Claude API, an Anthropic SDK, or Managed Agents
* You add, modify, or tune a Claude feature in a file (prompt caching, adaptive thinking, compaction, tool use, batch, files, citations, memory) or a model reference

**Manual invocation** by typing `/claude-api` (with optional subcommand or prose) in any environment where the skill is installed.

The skill does not activate for general programming tasks, ML/data-science work, or code that imports other AI SDKs (such as OpenAI).


## Supported languages

Source: https://platform.claude.com/llms-full.txt#supported-languages

The skill detects your project's language automatically by examining project files (for example, `requirements.txt` for Python, `tsconfig.json` for TypeScript, `go.mod` for Go) and loads the appropriate documentation.

| Language   | Messages API SDK | Tool runner | Managed Agents |
| ---------- | ---------------- | ----------- | -------------- |
| Python     | Yes              | Yes (beta)  | Yes (beta)     |
| TypeScript | Yes              | Yes (beta)  | Yes (beta)     |
| C#         | Yes              | Yes (beta)  | Yes (beta)     |
| Go         | Yes              | Yes (beta)  | Yes (beta)     |
| Java       | Yes              | Yes (beta)  | Yes (beta)     |
| PHP        | Yes              | Yes (beta)  | Yes (beta)     |
| Ruby       | Yes              | Yes (beta)  | Yes (beta)     |
| cURL       | Yes              | N/A         | Yes (beta)     |

If your project uses multiple languages, Claude asks which one applies. For unsupported languages (Rust, Swift, C++), the skill provides cURL/raw HTTP examples.


## How to use the skill

Source: https://platform.claude.com/llms-full.txt#how-to-use-the-skill

### In Claude Code (bundled)

The skill ships with [Claude Code](https://code.claude.com/docs/en/overview) and requires no installation. When you ask Claude to help build something with the Claude API, or when your project already imports an Anthropic SDK, the skill activates automatically.

You can also invoke it directly:

```text wrap
/claude-api

bash
npx skills add https://github.com/anthropics/skills --skill claude-api

text wrap
/plugin marketplace add anthropics/skills
/plugin install claude-api@anthropic-agent-skills
```


## Migrating to a newer Claude model

Source: https://platform.claude.com/llms-full.txt#migrating-to-a-newer-claude-model

The Claude API skill can perform Claude model migrations across a code base. Invoke it directly with `/claude-api migrate`:

```text wrap
/claude-api migrate this project to claude-opus-5

text wrap
/claude-api migrate everything under src/ to claude-opus-5
/claude-api migrate apps/api.py and apps/worker.py to claude-opus-5
```

When the scope is ambiguous (for example, a bare `/claude-api migrate to claude-opus-5`), the skill asks you to choose between the entire working directory, a specific subdirectory, or an explicit file list before editing any files. This applies to both Messages API and Managed Agents callers.

The skill handles:

* **Model ID swaps**, including typed SDK constants (`Model.CLAUDE_OPUS_4_8` → `Model.CLAUDE_OPUS_5`) across all supported languages, and classifies each file as a caller, a model definer, or an opaque string reference before editing
* **Cloud platform detection**, preserving platform-specific model ID formats (for example, the `anthropic.` prefix on Amazon Bedrock) and skipping changes for features that are unavailable on partner-operated platforms
* **Breaking parameter changes**, such as removing `temperature`, `top_p`, and `top_k` for Claude Opus 4.8 and Claude Opus 4.7, and converting `thinking: {type: "enabled", budget_tokens: N}` to `thinking: {type: "adaptive"}`
* **Prefill replacement**, converting assistant-message prefill patterns to [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) where applicable
* **Beta header cleanup**, removing beta headers that the target model doesn't require (for example, `effort-2025-11-24`, `fine-grained-tool-streaming-2025-05-14`, `interleaved-thinking-2025-05-14`) and switching back from `client.beta.messages.create` to `client.messages.create`
* **Effort calibration**, recommending an `output_config.effort` starting point for the target model (for example, the default `high` on Claude Opus 5, and `xhigh` for coding and agentic use cases on Claude Opus 4.8 and Claude Opus 4.7)
* **Prompt-behavior tuning**, flagging length-control, tool-triggering, subagent, and instruction-following prompts that may behave differently on the target model
* **Silent default handling**, opting back into thinking summarization (`thinking.display: "summarized"`) when reasoning is surfaced to users on Claude Opus 4.8 and Claude Opus 4.7
* **Refusal fallback configuration**, adding `stop_reason: "refusal"` handling before reading response content and setting up a [fallback retry path](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) when the target is Claude Fable 5.1, Claude Fable 5, or Claude Opus 5 (the server-side `fallbacks` parameter, typically in its `"default"` mode, the SDK refusal-fallback middleware, or a fallback-credit retry), and updating fallback code written against earlier preview shapes

As it edits, the skill explains each change and its motivation inline. On completion, it produces a checklist of items that require manual verification (typically integration tests, length-control prompt tuning, and cost/rate-limit re-baselining).

For the full list of model-specific changes the skill applies, see [Migrating to Claude Opus 5 from Claude Opus 4.8](https://platform.claude.com/docs/en/models/opus-5/migration-guide#migrating-from-claude-opus-4-8-to-claude-opus-5) and [Migrating to Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/migration-guide).
