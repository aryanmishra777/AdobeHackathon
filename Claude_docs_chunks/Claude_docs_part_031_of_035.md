# platform.claude.com Documentation (Part 31 of 35)

## Requests and responses

Source: https://platform.claude.com/llms-full.txt#requests-and-responses

To send a request to the Claude API, build an instance of a `Params` class and pass it to the corresponding client method. When the response is received, it's deserialized into an instance of a C# class.

For example, `client.Messages.Create` should be called with an instance of `MessageCreateParams`, and it will return an instance of `Task<Message>`.


## Advanced usage

Source: https://platform.claude.com/llms-full.txt#advanced-usage-3

### Binary responses

The SDK defines methods that return binary responses, which are used for API responses that shouldn't necessarily be parsed, like non-JSON data.

These methods return `HttpResponse`:

To save the response content to a file, or any [`Stream`](https://learn.microsoft.com/en-us/dotnet/api/system.io.stream), use the [`CopyToAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.io.stream.copytoasync) method:

### Raw responses

The SDK defines methods that deserialize responses into instances of C# classes. To access response headers, status code, or the raw response body, prefix any HTTP method call on a client or service with `WithRawResponse`:

The raw `HttpResponseMessage` can also be accessed through the `RawMessage` property.

For non-streaming responses, you can deserialize the response into an instance of a C# class if needed:

For streaming responses, you can deserialize the response to an `IAsyncEnumerable` if needed:

### Logging

<Warning>
  All log messages are intended for debugging only. The format and content of log messages may change between releases.
</Warning>

Enable debug logging by setting an environment variable:

### Undocumented API functionality

The SDK is typed for convenient usage of the documented API. However, it also supports working with undocumented or not yet supported parts of the API.


## Platform integrations

Source: https://platform.claude.com/llms-full.txt#platform-integrations

<Note>
  For detailed platform setup guides with code examples, see:

  * [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)
  * [Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy)
  * [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)
  * [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)
  * [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry)
</Note>

The C# SDK supports the following platforms through separate NuGet packages:

* **Agent Platform:** `Anthropic.Vertex`. See [Claude on Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai) for client setup.
* **Bedrock:** `Anthropic.Bedrock`. Use `AnthropicBedrockMantleClient` for the Messages-API Bedrock endpoint, or `AnthropicBedrockClient` (`bedrock-runtime` path). `AnthropicBedrockMantleClient` takes an optional `MantleAwsClientOptions` config object; `AnthropicBedrockClient` accepts `AnthropicBedrockCredentialsHelper.FromEnv()` or explicit credentials.
* **Claude Platform on AWS:** `Anthropic.Aws`. Use `AnthropicAwsClient`; set `WorkspaceId` on the client or the `ANTHROPIC_AWS_WORKSPACE_ID` environment variable (see [Workspaces](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#workspaces)). Available in beta.
* **Foundry:** `Anthropic.Foundry`. Use `AnthropicFoundryClient` with `DefaultAnthropicFoundryCredentials.FromEnv()` or explicit credentials.

Use `AnthropicBedrockMantleClient` for new projects; `AnthropicBedrockClient` remains for existing applications using the Bedrock `InvokeModel` API.


## Semantic versioning

Source: https://platform.claude.com/llms-full.txt#semantic-versioning

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backward-incompatible changes may be released as minor versions:

1. Changes to library internals that are technically public but not intended or documented for external use.
2. Changes that aren't expected to impact the vast majority of users in practice.

Backward-compatibility is taken seriously to ensure you can rely on a smooth upgrade experience.


## Additional resources

Source: https://platform.claude.com/llms-full.txt#additional-resources-5

* [GitHub repository](https://github.com/anthropics/anthropic-sdk-csharp)
* [NuGet package](https://www.nuget.org/packages/Anthropic)
* [API reference](https://platform.claude.com/docs/en/api/overview)
* [Streaming Messages](https://platform.claude.com/docs/en/build-with-claude/streaming)


---
title: Go SDK
url: https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/go
description: Install and configure the Anthropic Go SDK with context-based cancellation and functional options
---

The Anthropic Go library provides convenient access to the Claude API from applications written in Go.

<Info>
  For API feature documentation with code examples, see the [API reference](https://platform.claude.com/docs/en/api/overview). This page covers Go-specific SDK features and configuration.
</Info>


## Installation

Source: https://platform.claude.com/llms-full.txt#installation-3

Install with `go get`:


## Requirements

Source: https://platform.claude.com/llms-full.txt#requirements-2

This library requires Go 1.24+.


## Usage

Source: https://platform.claude.com/llms-full.txt#usage-3

For authentication options including Workload Identity Federation, see [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication). If your API key is a [personal or service account key](https://platform.claude.com/docs/en/manage-claude/authentication#key-types) with access to multiple workspaces, set the workspace ID in the `anthropic-workspace-id` request header; [Select a workspace](https://platform.claude.com/docs/en/manage-claude/authentication#select-a-workspace) shows the per-request option for this SDK.

<AccordionGroup>
  <Accordion title="Conversations">

</Accordion>

  <Accordion title="System prompts">

</Accordion>

  <Accordion title="Streaming">

</Accordion>

  <Accordion title="Tool calling">

</Accordion>
</AccordionGroup>


## Request fields

Source: https://platform.claude.com/llms-full.txt#request-fields

The anthropic library uses the [`omitzero`](https://tip.golang.org/doc/go1.24#encodingjsonpkgencodingjson) semantics from the Go 1.24+ `encoding/json` release for request fields.

Required primitive fields (such as `int64` or `string`) feature the tag `` `json:"...,required"` ``. These fields are always serialized, even their zero values.

Optional primitive types are wrapped in a `param.Opt[T]`. These fields can be set with the provided constructors, such as `anthropic.String(string)` or `anthropic.Int(int64)`.

Any `param.Opt[T]`, map, slice, struct or string enum uses the tag `` `json:"...,omitzero"` ``. Its zero value is considered omitted.

The `param.IsOmitted(any)` function can confirm the presence of any `omitzero` field.

To send `null` instead of a `param.Opt[T]`, use `param.Null[T]()`. To send `null` instead of a struct `T`, use `param.NullStruct[T]()`.

Request structs contain a `.SetExtraFields(map[string]any)` method which can send non-conforming fields in the request body. Extra fields overwrite any struct fields with a matching key.

<Warning>
  For security reasons, only use `SetExtraFields` with trusted data.
</Warning>

To send a custom value instead of a struct, use the generic function `param.Override` (for example, `param.Override[anthropic.FooParams](12)`).

### Request unions

Unions are represented as a struct with fields prefixed by "Of" for each of its variants, only one field can be non-zero. The non-zero field will be serialized.

Subproperties of the union can be accessed through methods on the union struct. These methods return a mutable pointer to the underlying data, if present.

### Deserializing params

<Note>
  `param.SetJSON` requires SDK v1.20.0 or later.
</Note>

Param types (types ending in `Param`, such as `MessageNewParams` or `ToolUnionParam`) are designed for outgoing requests only. They marshal correctly to JSON but do not fully support round-trip deserialization. If you unmarshal raw JSON into a param struct, typed union fields like `OfBashTool20250124` will be nil even when the underlying JSON is valid.

If you need to reconstruct params from raw JSON (for example, from a database, middleware, or a previous request), call `UnmarshalJSON` to populate non-union fields, then use `param.SetJSON` to attach the raw bytes for correct re-serialization:

For this use case, `param.SetJSON` (available since v1.20.0) is preferred over the more general `param.Override[T](any)` because it doesn't require spelling out the type parameter and makes the round-trip intent explicit.


## Response objects

Source: https://platform.claude.com/llms-full.txt#response-objects

All fields in response structs are ordinary value types (not pointers or wrappers). Response structs also include a special `JSON` field containing metadata about each property.

To handle optional data, use the `.Valid()` method on the JSON field. `.Valid()` returns true when the field is present, non-`null`, and was unmarshaled successfully.

If `.Valid()` is false, the corresponding field will be its zero value.

These `.JSON` structs also include an `ExtraFields` map containing any properties in the json response that were not specified in the struct. This can be useful for API features not yet present in the SDK.

### Response unions

In responses, unions are represented by a flattened struct containing all possible fields from each of the object variants. To convert it to a variant use the `.AsFooVariant()` method or the `.AsAny()` method if present.

If a response value union contains primitive values, primitive fields will be alongside the properties but prefixed with `Of` and feature the tag `json:"...,inline"`.


## Error handling

Source: https://platform.claude.com/llms-full.txt#error-handling-6

When the API returns a non-success status code, the SDK returns an error with type `*anthropic.Error`. This contains the `StatusCode`, `*http.Request`, and `*http.Response` values of the request, along with the JSON of the error body (much like other response objects in the SDK). The error also includes the `RequestID` from the response headers, which is useful for troubleshooting with Anthropic support.

To handle errors, use the `errors.As` pattern:

When other errors occur, they are returned unwrapped; for example, if HTTP transport fails, you might receive `*url.Error` wrapping `*net.OpError`.


## Retries

Source: https://platform.claude.com/llms-full.txt#retries-2

Certain errors will be automatically retried 2 times by default, with a short exponential backoff. The SDK retries by default all connection errors, 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 Internal errors.

You can use the `WithMaxRetries` option to configure or disable this:


## Timeouts

Source: https://platform.claude.com/llms-full.txt#timeouts-2

Non-streaming Messages requests time out after 10 minutes by default; other requests have no default timeout. Use context to configure a timeout for a request lifecycle.

Note that if a request is [retried](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/go#retries), the context timeout does not start over. To set a per-retry timeout, use `option.WithRequestTimeout()`.


## Long requests

Source: https://platform.claude.com/llms-full.txt#long-requests

<Warning>
  Consider using the streaming Messages API for longer running requests.
</Warning>

Avoid setting a large `MaxTokens` value without using streaming as some networks may drop idle connections after a certain period of time, which can cause the request to fail or [timeout](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/go#timeouts) without receiving a response from Anthropic.

This SDK will also return an error if a non-streaming request is expected to be above roughly 10 minutes long. Calling `.Messages.NewStreaming()` or [setting a custom timeout](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/go#timeouts) disables this error.


## File uploads

Source: https://platform.claude.com/llms-full.txt#file-uploads

Request parameters that correspond to file uploads in multipart requests are typed as `io.Reader`. The contents of the `io.Reader` will by default be sent as a multipart form part with the file name of "anonymous\_file" and content-type of "application/octet-stream", so the recommended approach is to specify a custom content-type with the `anthropic.File(reader io.Reader, filename string, contentType string)` helper, which wraps any `io.Reader` with the appropriate file name and content type.

The file name and content-type can also be customized by implementing `Name() string` or `ContentType() string` on the run-time type of `io.Reader`. Note that `os.File` implements `Name() string`, so a file returned by `os.Open` will be sent with the file name on disk.


## Pagination

Source: https://platform.claude.com/llms-full.txt#pagination-7

This library provides some conveniences for working with paginated list endpoints.

You can use `.ListAutoPaging()` methods to iterate through items across all pages:

Or you can use simple `.List()` methods to fetch a single page and receive a standard response object with additional helper methods like `.GetNextPage()`:


## RequestOptions

Source: https://platform.claude.com/llms-full.txt#requestoptions

This library uses the functional options pattern. Functions defined in the `option` package return a `RequestOption`, which is a closure that mutates a `RequestConfig`. These options can be supplied to the client or at individual requests. For example:

The request option `option.WithDebugLog(nil)` may be helpful while debugging.

See the [full list of request options](https://pkg.go.dev/github.com/anthropics/anthropic-sdk-go/option).


## HTTP client customization

Source: https://platform.claude.com/llms-full.txt#http-client-customization

For request middleware (`option.WithMiddleware`) and replacing the default `http.Client` (`option.WithHTTPClient`), see [SDK middleware](https://platform.claude.com/docs/en/cli-sdks-libraries/middleware).


## Platform integrations

Source: https://platform.claude.com/llms-full.txt#platform-integrations-2

<Note>
  For detailed platform setup guides with code examples, see:

  * [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)
  * [Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy)
  * [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)
  * [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)
</Note>

The Go SDK supports the following platforms:

* **Agent Platform:** `import "github.com/anthropics/anthropic-sdk-go/vertex"`. Use `vertex.WithGoogleAuth(ctx, region, projectID)` or `vertex.WithCredentials(ctx, region, projectID, creds)`.
* **Bedrock:** `import "github.com/anthropics/anthropic-sdk-go/bedrock"`. Use `bedrock.NewMantleClient` for the Messages-API Bedrock endpoint (streams over SSE), or `bedrock.WithLoadDefaultConfig(ctx)` / `bedrock.WithConfig(cfg)` (`bedrock-runtime` path). Importing the `bedrock` package globally registers a decoder for `application/vnd.amazon.eventstream` with the SDK's streaming layer (through package `init()`). This applies whether you use the `bedrock-runtime` `WithConfig`/`WithLoadDefaultConfig` path or `NewMantleClient`.
* **Claude Platform on AWS:** `import anthropicaws "github.com/anthropics/anthropic-sdk-go/aws"`. Use `anthropicaws.NewClient(ctx, cfg)` with an `anthropicaws.ClientConfig` value to construct a client; set `WorkspaceID` on the config or the `ANTHROPIC_AWS_WORKSPACE_ID` environment variable. The `anthropicaws` import alias avoids a name collision with `github.com/aws/aws-sdk-go-v2/aws` when both are imported. Available in beta.
* **Foundry:** Not currently supported in the Go SDK. See [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry) for supported SDKs.

Use `bedrock.NewMantleClient` for new projects; `bedrock.WithLoadDefaultConfig`/`WithConfig` remain for existing applications using the Bedrock `InvokeModel` API.


## Advanced usage

Source: https://platform.claude.com/llms-full.txt#advanced-usage-4

### Accessing raw response data (for example, response headers)

You can access the raw HTTP response data by using the `option.WithResponseInto()` request option. This is useful when you need to examine response headers, status codes, or other details.

### Making custom/undocumented requests

This library is typed for convenient access to the documented API. If you need to access undocumented endpoints, params, or response properties, the library can still be used.

#### Undocumented endpoints

To make requests to undocumented endpoints, you can use `client.Get`, `client.Post`, and other HTTP verbs. `RequestOptions` on the client, such as retries, will be respected when making these requests.

#### Undocumented request params

To make requests using undocumented parameters, you may use either the `option.WithQuerySet()` or the `option.WithJSONSet()` methods.

#### Undocumented response properties

To access undocumented response properties, you may either access the raw JSON of the response as a string with `result.JSON.RawJSON()`, or get the raw JSON of a particular field on the result with `result.JSON.Foo.Raw()`.

Any fields that are not present on the response struct are saved and can be accessed through `result.JSON.ExtraFields`, which is a `map[string]respjson.Field`.


## Semantic versioning

Source: https://platform.claude.com/llms-full.txt#semantic-versioning-2

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backward-incompatible changes may be released as minor versions:

1. Changes to library internals that are technically public but not intended or documented for external use.
2. Changes that aren't expected to impact the vast majority of users in practice.

Backward-compatibility is taken seriously to ensure you can rely on a smooth upgrade experience.

Your feedback is welcome; open an [issue](https://github.com/anthropics/anthropic-sdk-go/issues) with questions, bugs, or suggestions.


## Additional resources

Source: https://platform.claude.com/llms-full.txt#additional-resources-6

* [GitHub repository](https://github.com/anthropics/anthropic-sdk-go)
* [Go package documentation](https://pkg.go.dev/github.com/anthropics/anthropic-sdk-go)
* [API reference](https://platform.claude.com/docs/en/api/overview)
* [Streaming Messages](https://platform.claude.com/docs/en/build-with-claude/streaming)


---
title: Java SDK
url: https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java
description: Install and configure the Anthropic Java SDK with builder patterns and async support
---

The Anthropic Java SDK provides convenient access to the Claude API from applications written in Java. It uses the builder pattern for creating requests and supports both synchronous and asynchronous operations.

<Info>
  For API feature documentation with code examples, see the [API reference](https://platform.claude.com/docs/en/api/overview). This page covers Java-specific SDK features and configuration.
</Info>


## Installation

Source: https://platform.claude.com/llms-full.txt#installation-4

<Tabs>
  <Tab title="Gradle">

</Tab>

  <Tab title="Maven">

</Tab>
</Tabs>


## Requirements

Source: https://platform.claude.com/llms-full.txt#requirements-3

This library requires Java 8 or later.

<Note>
  The SDK supports Java 8 and later. Code examples in this documentation are written as [JDK 25 compact source files](https://openjdk.org/jeps/512), using a bare `void main()` entry point and `IO.println()` for output. The API calls themselves are identical on every supported JDK; to compile an example on an earlier version, replace `IO.println(...)` with `System.out.println(...)` and place the body inside `public static void main(String[] args)` within a class.
</Note>


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-16


## Client configuration

Source: https://platform.claude.com/llms-full.txt#client-configuration-2

### API key setup

Configure the client using system properties or environment variables:

Or configure manually:

Or use a combination of both approaches:

For authentication options including Workload Identity Federation, see [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication). If your API key is a [personal or service account key](https://platform.claude.com/docs/en/manage-claude/authentication#key-types) with access to multiple workspaces, set the workspace ID in the `anthropic-workspace-id` request header; [Select a workspace](https://platform.claude.com/docs/en/manage-claude/authentication#select-a-workspace) shows the per-request option for this SDK.

### Configuration options

| Setter      | System property       | Environment variable   | Required | Default value                 |
| ----------- | --------------------- | ---------------------- | -------- | ----------------------------- |
| `apiKey`    | `anthropic.apiKey`    | `ANTHROPIC_API_KEY`    | false    | -                             |
| `authToken` | `anthropic.authToken` | `ANTHROPIC_AUTH_TOKEN` | false    | -                             |
| `baseUrl`   | `anthropic.baseUrl`   | `ANTHROPIC_BASE_URL`   | true     | `"https://api.anthropic.com"` |

System properties take precedence over environment variables.

<Tip>
  Don't create more than one client in the same application. Each client has a connection pool and thread pools, which are more efficient to share between requests.
</Tip>

### Modifying configuration

To temporarily use a modified client configuration while reusing the same connection and thread pools, call `withOptions()` on any client or service:

The `withOptions()` method does not affect the original client or service.


## Async usage

Source: https://platform.claude.com/llms-full.txt#async-usage

The default client is synchronous. To switch to asynchronous execution, call the `async()` method:

Or create an asynchronous client from the beginning:

The asynchronous client supports the same options as the synchronous one, except most methods return `CompletableFuture`s.


## Streaming

Source: https://platform.claude.com/llms-full.txt#streaming-9

The SDK defines methods that return response "chunk" streams, where each chunk can be individually processed as soon as it arrives instead of waiting on the full response.

### Synchronous streaming

These streaming methods return `StreamResponse` for synchronous clients:

### Asynchronous streaming

For asynchronous clients, the method returns `AsyncStreamResponse`:

Async streaming uses a dedicated per-client cached thread pool `Executor` to stream without blocking the current thread. To use a different `Executor`:

Or configure the client globally using the `streamHandlerExecutor` method:

### Streaming with message accumulator

A `MessageAccumulator` can record the stream of events in the response as they are processed and accumulate a `Message` object similar to what would have been returned by the non-streaming API.

For a synchronous response, add a `Stream.peek()` call to the stream pipeline to accumulate each event:

For an asynchronous response, add the `MessageAccumulator` to the `subscribe()` call:

A `BetaMessageAccumulator` is also available for the accumulation of a `BetaMessage` object. It is used in the same manner as the `MessageAccumulator`.


## Structured outputs

Source: https://platform.claude.com/llms-full.txt#structured-outputs

For complete structured outputs documentation including Java examples, see [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).


## Tool use

Source: https://platform.claude.com/llms-full.txt#tool-use-2

[Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) lets you integrate external tools and functions directly into the AI model's responses. Instead of producing plain text, the model can output instructions (with parameters) for calling a tool or function when appropriate. You define JSON schemas for tools, and the model uses the schemas to determine when and how to use these tools.

The tool use feature supports a "strict" mode that guarantees that the JSON output from the AI model will conform to the JSON schema you provide in the input parameters.

The SDK can derive a tool and its parameters automatically from the structure of an arbitrary Java class: the class's name (converted to snake case) provides the tool name, and the class's fields define the tool's parameters.

<Note>
  Declare your tool classes as top-level classes or `static` nested classes. This requirement comes from the Jackson Databind library (`com.fasterxml.jackson.databind`), which the SDK uses to deserialize tool inputs into your class instances and cannot instantiate non-static inner classes.
</Note>

### Defining tools with annotations

### Calling tools

When your tool classes are defined, add them to the message parameters using `MessageCreateParams.Builder.addTool(Class<T>)` and then call them if requested to do so in the AI model's response. `BetaToolUseBlock.input(Class<T>)` can be used to parse a tool's parameters in JSON form to an instance of your tool-defining class.

After calling the tool, use `BetaToolResultBlockParam.Builder.contentAsJson(Object)` to pass the tool's result back to the AI model:

### Tool name conversion

Tool names are derived from the camel case tool class names (for example, `GetWeather`) and converted to snake case (for example, `get_weather`). Word boundaries begin where the current character is not the first character, is upper-case, and either the preceding character is lower-case, or the following character is lower-case. For example, `MyJSONParser` becomes `my_json_parser` and `ParseJSON` becomes `parse_json`. This conversion can be overridden using the `@JsonTypeName` annotation.

### Local tool JSON schema validation

You can perform local validation to check that the JSON schema derived from your tool class respects Anthropic's restrictions. Local validation is enabled by default, but it can be disabled:

### Annotating tool classes

You can use annotations to add further information about tools to the JSON schemas:

* `@JsonClassDescription` - Add a description to a tool class detailing when and how to use that tool.
* `@JsonTypeName` - Set the tool name to something other than the simple name of the class converted to snake case.
* `@JsonPropertyDescription` - Add a detailed description to a tool parameter.
* `@JsonIgnore` - Exclude a `public` field or getter method from the generated JSON schema for a tool's parameters.
* `@JsonProperty` - Include a non-`public` field or getter method in the generated JSON schema for a tool's parameters.


## Message batches

Source: https://platform.claude.com/llms-full.txt#message-batches

The SDK provides support for [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing) under the `client.messages().batches()` namespace. See [Pagination](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java#pagination) for how to list and paginate through batches.


## File uploads

Source: https://platform.claude.com/llms-full.txt#file-uploads-2

The SDK defines methods that accept files through the `MultipartField` class:

Or from an `InputStream`:

Or from in-memory bytes:

### Binary responses

The SDK defines methods that return binary responses for API responses that aren't necessarily parsed as JSON:

To save the response content to a file:

Or transfer the response content to any `OutputStream`:


## Error handling

Source: https://platform.claude.com/llms-full.txt#error-handling-7

The SDK throws custom unchecked exception types:

* `AnthropicServiceException` - Base class for HTTP errors.
* `AnthropicIoException` - I/O networking errors.
* `AnthropicRetryableException` - Generic error indicating a failure that could be retried.
* `AnthropicInvalidDataException` - Failure to interpret successfully parsed data (for example, when accessing a property that's supposed to be required, but the API unexpectedly omitted it).
* `AnthropicException` - Base class for all exceptions.

### Status code mapping

| Status | Exception                       |
| ------ | ------------------------------- |
| 400    | `BadRequestException`           |
| 401    | `UnauthorizedException`         |
| 403    | `PermissionDeniedException`     |
| 404    | `NotFoundException`             |
| 422    | `UnprocessableEntityException`  |
| 429    | `RateLimitException`            |
| 5xx    | `InternalServerException`       |
| others | `UnexpectedStatusCodeException` |

`SseException` is thrown for errors encountered during SSE streaming after a successful initial HTTP response.


## Request IDs

Source: https://platform.claude.com/llms-full.txt#request-ids

When using [raw responses](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java#raw-response-access), you can access the `request-id` response header using the `requestId()` method:

This can be used to quickly log failing requests and report them back to Anthropic. For more information on debugging requests, see [Request ID](https://platform.claude.com/docs/en/api/errors#request-id).


## Retries

Source: https://platform.claude.com/llms-full.txt#retries-3

The SDK automatically retries 2 times by default, with a short exponential backoff between requests.

Only the following error types are retried:

* Connection errors (for example, because of a network connectivity problem)
* 408 Request Timeout
* 409 Conflict
* 429 Rate Limit
* 5xx Internal

The API may also explicitly instruct the SDK to retry or not retry a request.

To set a custom number of retries, configure the client using the `maxRetries` method:


## Timeouts

Source: https://platform.claude.com/llms-full.txt#timeouts-3

Requests time out after 10 minutes by default.

However, for methods that accept `maxTokens`, if you specify a large `maxTokens` value and are streaming, then the default timeout will be calculated dynamically using this formula:

This results in a timeout of up to 60 minutes, scaled by the `maxTokens` parameter, unless overridden.

For non-streaming requests, the dynamic timeout scales from a 30 second minimum up to a 10 minute maximum based on `maxTokens`.

To set a custom timeout per-request:

Or configure the default for all method calls at the client level:


## Long requests

Source: https://platform.claude.com/llms-full.txt#long-requests-2

<Warning>
  Consider using [streaming](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java#streaming) for longer running requests.
</Warning>

Avoid setting a large `maxTokens` value without using streaming. Some networks may drop idle connections after a certain period of time, which can cause the request to fail or [timeout](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java#timeouts) without receiving a response from Anthropic. The SDK periodically pings the API to keep the connection alive and reduce the impact of these networks.

The SDK throws an error if a non-streaming request is expected to take longer than 10 minutes. Using a [streaming method](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java#streaming) or [overriding the timeout](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java#timeouts) at the client or request level disables the error.


## Pagination

Source: https://platform.claude.com/llms-full.txt#pagination-8

The SDK provides convenient ways to access paginated results either one page at a time or item-by-item across all pages.

### Auto-pagination

To iterate through all results across all pages, use the `autoPager()` method, which automatically fetches more pages as needed.

When using the asynchronous client, the method returns an `AsyncStreamResponse`:

### Manual pagination

To access individual page items and manually request the next page:


## Type system

Source: https://platform.claude.com/llms-full.txt#type-system

### Immutability and builders

Each class in the SDK has an associated builder for constructing it. Each class is immutable once constructed. If the class has an associated builder, then it has a `toBuilder()` method, which can be used to convert it back to a builder for making a modified copy.

Because each class is immutable, builder modification never affects already built class instances.

### Requests and responses

To send a request to the Claude API, build an instance of some `Params` class and pass it to the corresponding client method. When the response is received, it is deserialized into an instance of a Java class.

For example, `client.messages().create(...)` should be called with an instance of `MessageCreateParams`, and it returns an instance of `Message`.

### Undocumented parameters

To set undocumented parameters, call the `putAdditionalHeader`, `putAdditionalQueryParam`, or `putAdditionalBodyProperty` methods on any `Params` class:

These can be accessed on the built object later using the `_additionalHeaders()`, `_additionalQueryParams()`, and `_additionalBodyProperties()` methods.

<Warning>
  The values passed to these methods overwrite values passed to earlier methods. For security reasons, ensure these methods are only used with trusted input data.
</Warning>

To set undocumented parameters on nested headers, query params, or body classes:

These properties can be accessed on the nested built object later using the `_additionalProperties()` method.

To set a documented parameter or property to an undocumented or not yet supported value, pass a `JsonValue` object to its setter:

### JsonValue creation

The most straightforward way to create a `JsonValue` is using its `from(...)` method:

### Forcibly omitting required parameters

Normally a `Builder` class's `build` method will throw `IllegalStateException` if any required parameter or property is unset. To forcibly omit a required parameter or property, pass `JsonMissing`:

### Response properties

To access undocumented response properties, call the `_additionalProperties()` method:

To access a property's raw JSON value, call its `_` prefixed method:

### Response validation

By default, the SDK does not throw an exception when the API returns a response that doesn't match the expected type. It throws `AnthropicInvalidDataException` only if you directly access the property.

To check that the response is completely well-typed upfront, call `validate()`:

Or configure per-request:

Or configure the default for all method calls at the client level:


## HTTP client customization

Source: https://platform.claude.com/llms-full.txt#http-client-customization-2

### Proxy configuration

### HTTPS / SSL configuration

<Note>
  Most applications should not call these methods, and instead use the system defaults. The defaults include special optimizations that can be lost if the implementations are modified.
</Note>

### Custom HTTP client

The SDK consists of three artifacts:

* `anthropic-java-core` - Contains core SDK logic, does not depend on OkHttp. Exposes `AnthropicClient`, `AnthropicClientAsync`, and their implementation classes, all of which can work with any HTTP client.
* `anthropic-java-client-okhttp` - Depends on OkHttp. Exposes `AnthropicOkHttpClient` and `AnthropicOkHttpClientAsync`.
* `anthropic-java` - Depends on and exposes the APIs of both `anthropic-java-core` and `anthropic-java-client-okhttp`. Does not have its own logic.

This structure allows replacing the SDK's default HTTP client without pulling in unnecessary dependencies.

#### Customized OkHttpClient

<Tip>
  Try the available [network options](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java#retries) before replacing the default client.
</Tip>

To use a customized `OkHttpClient`:

1. Replace your `anthropic-java` dependency with `anthropic-java-core`.
2. Copy `anthropic-java-client-okhttp`'s `OkHttpClient` class into your code and customize it.
3. Construct `AnthropicClientImpl` or `AnthropicClientAsyncImpl` using your customized client.

#### Completely custom HTTP client

To use a completely custom HTTP client:

1. Replace your `anthropic-java` dependency with `anthropic-java-core`.
2. Write a class that implements the `HttpClient` interface.
3. Construct `AnthropicClientImpl` or `AnthropicClientAsyncImpl` using your new client class.


## Platform integrations

Source: https://platform.claude.com/llms-full.txt#platform-integrations-3

<Note>
  For detailed platform setup guides with code examples, see:

  * [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)
  * [Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy)
  * [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)
  * [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)
  * [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry)
</Note>

The Java SDK supports the following platforms through separate dependencies that provide platform-specific `Backend` implementations:

* **Agent Platform:** `com.anthropic:anthropic-java-vertex`: Use `VertexBackend.fromEnv()` or `VertexBackend.builder()`.
* **Bedrock:** `com.anthropic:anthropic-java-bedrock`: Use `BedrockMantleBackend.fromEnv()` or `BedrockMantleBackend.builder()` for the Messages-API Bedrock endpoint, or `BedrockBackend.fromEnv()` / `BedrockBackend.builder()` (`bedrock-runtime` path).
* **Claude Platform on AWS:** `com.anthropic:anthropic-java-aws`: Use `AwsBackend.fromEnv()` (reads `ANTHROPIC_AWS_WORKSPACE_ID` and the AWS default region/credential chain) or `AwsBackend.builder()`. Available in beta.
* **Foundry:** `com.anthropic:anthropic-java-foundry`: Use `FoundryBackend.fromEnv()` or `FoundryBackend.builder()`.

Use `BedrockMantleBackend` for new projects; `BedrockBackend` remains for existing applications using the Bedrock `InvokeModel` API.

Each `Backend` implementation is passed to the client with `.backend()` on `AnthropicOkHttpClient.builder()`. Each cloud backend pulls in its respective cloud-platform SDK classes as transitive dependencies.


## Advanced usage

Source: https://platform.claude.com/llms-full.txt#advanced-usage-5

### Raw response access

To access HTTP headers, status codes, and the raw response body, prefix any HTTP method call with `withRawResponse()`:

You can still deserialize the response into an instance of a Java class if needed:

### Logging

The SDK uses the standard OkHttp logging interceptor.

Enable logging by setting the `ANTHROPIC_LOG` environment variable to `info`:

Or to `debug` for more verbose logging:

<Accordion title="Jackson compatibility">
  The SDK depends on Jackson for JSON serialization/deserialization. It is compatible with version 2.13.4 or higher, but depends on version 2.19.4 by default.

  The SDK throws an exception if it detects an incompatible Jackson version at runtime (for example, if the default version was overridden in your Maven or Gradle config).

  If the SDK threw an exception, but you're certain the version is compatible, then disable the version check using `checkJacksonVersionCompatibility` on `AnthropicOkHttpClient` or `AnthropicOkHttpClientAsync`.

  <Warning>
    There is no guarantee that the SDK works correctly when the Jackson version check is disabled.
  </Warning>

  There are also bugs in older Jackson versions that can affect the SDK. The SDK doesn't work around all Jackson bugs and expects users to upgrade Jackson for those instead.
</Accordion>

<Accordion title="ProGuard/R8 configuration">
  Although the SDK uses reflection, it is still usable with ProGuard and R8 because `anthropic-java-core` is published with a configuration file containing keep rules.

  ProGuard and R8 should automatically detect and use the published rules, but you can also manually copy the keep rules if necessary.
</Accordion>

### Undocumented API functionality

The SDK is typed for convenient usage of the documented API. However, it also supports working with undocumented or not yet supported parts of the API.

#### Undocumented request parameters

To set undocumented request parameters, use the `putAdditionalHeader`, `putAdditionalQueryParam`, or `putAdditionalBodyProperty` methods as described in [Undocumented parameters](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java#undocumented-parameters).

#### Undocumented response properties

To access undocumented response properties, use the `_additionalProperties()` method as described in [Response properties](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java#response-properties).

#### New or unreleased enum values

Enum-like classes in the SDK, such as `Model` and `AnthropicBeta`, are not closed Java `enum` types. Each one provides an `of(String)` factory method that accepts any string, so you can use values that have not been added to the SDK yet, such as a model or beta header released after your SDK version:

Builder methods that take these types often also provide a `String` overload that calls `of(...)` for you:

Prefer the well-typed constants (for example, `Model.CLAUDE_OPUS_5`) so you get autocomplete and deprecation warnings. The `String` overloads and `of(...)` are primarily for setting the field to an undocumented or not yet supported value while waiting for an SDK release that includes it.


## Beta features

Source: https://platform.claude.com/llms-full.txt#beta-features

Beta features are available before general release to get early feedback and test new functionality. You can check the availability of all of Claude's capabilities and tools in the [build with Claude overview](https://platform.claude.com/docs/en/build-with-claude/overview).

You can access most beta API features through the `beta()` method on the client. To enable a particular beta feature, add the appropriate [beta header](https://platform.claude.com/docs/en/api/beta-headers) with `.addBeta()` when building the message params.

For example, to enable [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing):


## Frequently asked questions

Source: https://platform.claude.com/llms-full.txt#frequently-asked-questions-9

<AccordionGroup>
  <Accordion title="Why doesn't the SDK use plain enum classes?">
    Java `enum` classes are not trivially forward compatible. Using them in the SDK could cause runtime exceptions if the API is updated to respond with a new enum value.

    Because these classes are open, you can also construct them with any string value through their `of(String)` factory method. See [New or unreleased enum values](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/java#new-or-unreleased-enum-values) if you need to use a value that isn't in your SDK version yet.
  </Accordion>

  <Accordion title="Why are fields represented using JsonField<T> instead of just plain T?">
    Using `JsonField<T>` enables a few features:

    * Allowing usage of undocumented API functionality
    * Lazily validating the API response against the expected shape
    * Representing absent vs explicitly null values
  </Accordion>

  <Accordion title="Why doesn't the SDK use data classes?">
    It is not backwards compatible to add new fields to a data class, and the SDK avoids introducing a breaking change every time a field is added to a class.
  </Accordion>

  <Accordion title="Why doesn't the SDK use checked exceptions?">
    Checked exceptions are widely considered a mistake in the Java programming language. In fact, they were omitted from Kotlin for this reason.

    Checked exceptions:

    * Are verbose to handle
    * Encourage error handling at the wrong level of abstraction, where nothing can be done about the error
    * Are tedious to propagate because of the function coloring problem
    * Don't play well with lambdas (also because of the function coloring problem)
  </Accordion>
</AccordionGroup>


## Semantic versioning

Source: https://platform.claude.com/llms-full.txt#semantic-versioning-3

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backward-incompatible changes may be released as minor versions:

1. Changes to library internals which are technically public but not intended or documented for external use.
2. Changes that aren't expected to impact the vast majority of users in practice.


## Additional resources

Source: https://platform.claude.com/llms-full.txt#additional-resources-7

* [GitHub repository](https://github.com/anthropics/anthropic-sdk-java)
* [Javadocs](https://javadoc.io/doc/com.anthropic/anthropic-java)
* [API reference](https://platform.claude.com/docs/en/api/overview)
* [Streaming Messages](https://platform.claude.com/docs/en/build-with-claude/streaming)
* [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)


---
title: PHP SDK
url: https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/php
description: Install and configure the Anthropic PHP SDK with value objects and builder patterns
---

The Anthropic PHP library provides convenient access to the Claude API from any PHP 8.1.0+ application.

<Info>
  The PHP SDK is currently in beta. APIs might change between versions.
</Info>

<Info>
  For API feature documentation with code examples, see the [API reference](https://platform.claude.com/docs/en/api/overview). This page covers PHP-specific SDK features and configuration.
</Info>


## Installation

Source: https://platform.claude.com/llms-full.txt#installation-5

The SDK uses [PSR-18](https://www.php-fig.org/psr/psr-18/) for HTTP and discovers any installed PSR-18 client automatically. [Guzzle](https://docs.guzzlephp.org/) is recommended because the SDK configures it for streaming with no additional setup:


## Requirements

Source: https://platform.claude.com/llms-full.txt#requirements-4

PHP 8.1.0 or higher.


## Usage

Source: https://platform.claude.com/llms-full.txt#usage-4

This library uses named parameters to specify optional arguments. Parameters with a default value must be set by name.

For authentication options including Workload Identity Federation, see [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication). If your API key is a [personal or service account key](https://platform.claude.com/docs/en/manage-claude/authentication#key-types) with access to multiple workspaces, set the workspace ID in the `anthropic-workspace-id` request header; [Select a workspace](https://platform.claude.com/docs/en/manage-claude/authentication#select-a-workspace) shows the per-request option for this SDK.


## Value objects

Source: https://platform.claude.com/llms-full.txt#value-objects

It is recommended to use the static `with` constructor `Base64ImageSource::with(data: "U3RhaW5sZXNzIHJvY2tz", ...)` and named parameters to initialize value objects.

However, builders are also provided `(new Base64ImageSource)->withData("U3RhaW5sZXNzIHJvY2tz")`.
