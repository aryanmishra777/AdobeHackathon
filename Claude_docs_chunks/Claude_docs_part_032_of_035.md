# platform.claude.com Documentation (Part 32 of 35)

## Streaming

Source: https://platform.claude.com/llms-full.txt#streaming-10

The SDK provides support for streaming responses using Server-Sent Events (SSE).

Streaming requires an HTTP client that returns the response body incrementally. When Guzzle is the discovered PSR-18 client, the SDK configures it for streaming automatically. With a buffering client, the `foreach` loop yields every event at once when the response completes instead of incrementally; if you observe that symptom, install Guzzle or supply a streaming-capable PSR-18 client through the `streamingTransporter` request option:


## Error handling

Source: https://platform.claude.com/llms-full.txt#error-handling-8

When the library is unable to connect to the API, or if the API returns a non-success status code (that is, a 4xx or 5xx response), a subclass of `Anthropic\Core\Exceptions\APIException` is thrown:

Error codes are as follows:

| Cause            | Error Type                     |
| ---------------- | ------------------------------ |
| HTTP 400         | `BadRequestException`          |
| HTTP 401         | `AuthenticationException`      |
| HTTP 403         | `PermissionDeniedException`    |
| HTTP 404         | `NotFoundException`            |
| HTTP 409         | `ConflictException`            |
| HTTP 422         | `UnprocessableEntityException` |
| HTTP 429         | `RateLimitException`           |
| HTTP >= 500      | `InternalServerException`      |
| Other HTTP error | `APIStatusException`           |
| Timeout          | `APITimeoutException`          |
| Network error    | `APIConnectionException`       |


## Retries

Source: https://platform.claude.com/llms-full.txt#retries-4

Certain errors are automatically retried two times by default, with a short exponential backoff.

Connection errors (for example, because of a network connectivity problem), 408 Request Timeout, 409 Conflict, 429 Rate Limit, >=500 Internal errors, and timeouts are all retried by default.

You can use the `maxRetries` option to configure or disable this:


## Pagination

Source: https://platform.claude.com/llms-full.txt#pagination-9

List methods in the Claude API are paginated.

This library provides auto-paginating iterators with each list response, so you do not have to request successive pages manually:


## Advanced usage

Source: https://platform.claude.com/llms-full.txt#advanced-usage-6

### Undocumented properties

You can send undocumented parameters to any endpoint, and read undocumented response properties, as follows:

<Note>
  The `extra*` parameters of the same name override the documented parameters.
</Note>

### Undocumented request parameters

If you want to explicitly send an extra parameter, you can do so with the `extraQueryParams`, `extraBodyParams`, and `extraHeaders` options under `RequestOptions::with()` when making a request, as seen in the preceding example.

### Undocumented endpoints

To make requests to undocumented endpoints while retaining the benefit of authentication, retries, and other client features, you can make requests using `client->request`, as follows:


## Platform integrations

Source: https://platform.claude.com/llms-full.txt#platform-integrations-4

<Note>
  For detailed platform setup guides with code examples, see:

  * [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)
  * [Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy)
  * [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)
  * [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)
  * [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry)
</Note>

The PHP SDK supports the following platforms:

* **Agent Platform:** `Anthropic\Vertex\Client`. Use `::fromEnvironment()`.
* **Bedrock:** `Anthropic\Bedrock\MantleClient`. Use `new MantleClient(awsRegion: ...)`.
* **Bedrock (legacy):** `Anthropic\Bedrock\Client`. Use `::fromEnvironment()` or `::withCredentials()`.
* **Claude Platform on AWS:** `Anthropic\Aws\Client` (requires `aws/aws-sdk-php` as a soft dependency). Use `new Anthropic\Aws\Client(workspaceId: ...)` or set `ANTHROPIC_AWS_WORKSPACE_ID`. Available in beta.
* **Foundry:** `Anthropic\Foundry\Client`. Use `::withCredentials()`.

Use `MantleClient` for new projects; `Anthropic\Bedrock\Client` remains for existing applications using the Bedrock `InvokeModel` API.


## Semantic versioning

Source: https://platform.claude.com/llms-full.txt#semantic-versioning-4

This package follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions. As the library is in initial development and has a major version of `0`, APIs might change at any time.

This package considers improvements to the (non-runtime) PHPDoc type definitions to be non-breaking changes.


## Additional resources

Source: https://platform.claude.com/llms-full.txt#additional-resources-8

* [GitHub repository](https://github.com/anthropics/anthropic-sdk-php)
* [Packagist](https://packagist.org/packages/anthropic-ai/sdk)
* [API reference](https://platform.claude.com/docs/en/api/overview)
* [Streaming Messages](https://platform.claude.com/docs/en/build-with-claude/streaming)


---
title: Python SDK
url: https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python
description: Install and configure the Anthropic Python SDK with sync and async client support
---

The Anthropic Python SDK provides convenient access to the Claude API from Python applications. It supports both synchronous and asynchronous operations, streaming, and integrations with Amazon Bedrock, Claude Platform on AWS, Google Cloud, and Microsoft Foundry.

<Info>
  For API feature documentation with code examples, see the [API reference](https://platform.claude.com/docs/en/api/overview). This page covers Python-specific SDK features and configuration.
</Info>


## Installation

Source: https://platform.claude.com/llms-full.txt#installation-6

For platform-specific integrations or improved async performance, install with extras:


## Requirements

Source: https://platform.claude.com/llms-full.txt#requirements-5

Python 3.10 or later is required. If you are upgrading from a 0.x release of the SDK, see the [v1 migration guide](https://github.com/anthropics/anthropic-sdk-python/blob/main/MIGRATION.md) for the list of breaking changes.


## Usage

Source: https://platform.claude.com/llms-full.txt#usage-5

<Tip>
  Consider using [python-dotenv](https://pypi.org/project/python-dotenv/) to add `ANTHROPIC_API_KEY="my-anthropic-api-key"` to your `.env` file so that your API key isn't stored in source control.
</Tip>

For authentication options including Workload Identity Federation, see [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication). If your API key is a [personal or service account key](https://platform.claude.com/docs/en/manage-claude/authentication#key-types) with access to multiple workspaces, set the workspace ID in the `anthropic-workspace-id` request header; [Select a workspace](https://platform.claude.com/docs/en/manage-claude/authentication#select-a-workspace) shows the per-request option for this SDK.


## Async usage

Source: https://platform.claude.com/llms-full.txt#async-usage-2

### Using aiohttp for better concurrency

For improved async performance, you can use the `aiohttp` HTTP backend instead of the default `httpx2`:


## Streaming responses

Source: https://platform.claude.com/llms-full.txt#streaming-responses

The SDK provides support for streaming responses using Server-Sent Events (SSE).

The async client uses the exact same interface:

### Streaming helpers

The SDK also provides streaming helpers that use context managers and provide access to the accumulated text and the final message:

Streaming with `client.messages.stream(...)` exposes various helpers including accumulation and SDK-specific events.

Alternatively, you can use `client.messages.create(..., stream=True)` which only returns an iterable of the events in the stream and uses less memory (it doesn't build up a final message object for you).


## Token counting

Source: https://platform.claude.com/llms-full.txt#token-counting-2

You can see the exact usage for a given request through the `usage` response property:

You can also count tokens before making a request:


## Tool use

Source: https://platform.claude.com/llms-full.txt#tool-use-3

This SDK provides support for tool use, also known as function calling. For more details, see [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).

### Tool helpers

The SDK provides helpers for defining and running tools as pure Python functions. The `@beta_tool` decorator generates the tool schema from the function signature and docstring:

On every iteration, an API request is made. If the response includes a call to one of the given tools, the tool is automatically called, and the result is returned directly to the model in the next iteration.


## Message batches

Source: https://platform.claude.com/llms-full.txt#message-batches-2

This SDK provides support for [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing) under `client.messages.batches`.

### Creating a batch

Message Batches takes an array of requests, where each object has a `custom_id` identifier and the same request `params` as the standard Messages API:

### Getting results from a batch

Once a Message Batch has been processed, indicated by `.processing_status == 'ended'`, you can access the results with `.batches.results()`:


## File uploads

Source: https://platform.claude.com/llms-full.txt#file-uploads-3

Request parameters that correspond to file uploads can be passed in many different forms:

* A `PathLike` object (for example, `pathlib.Path`)
* A tuple of `(filename, content, content_type)`
* A `BinaryIO` file-like object

The async client uses the exact same interface. If you pass a `PathLike` instance, the file contents are read asynchronously automatically.


## Handling errors

Source: https://platform.claude.com/llms-full.txt#handling-errors

When the library is unable to connect to the API, or if the API returns a non-success status code (that is, 4xx or 5xx response), a subclass of `APIError` is raised:

Error codes are as follows:

| Status code | Error type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 409         | `ConflictError`            |
| 422         | `UnprocessableEntityError` |
| 429         | `RateLimitError`           |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |


## Request IDs

Source: https://platform.claude.com/llms-full.txt#request-ids-2

> For more information on debugging requests, see [Request ID](https://platform.claude.com/docs/en/api/errors#request-id).

All object responses in the SDK provide a `_request_id` property which is added from the `request-id` response header so that you can quickly log failing requests and report them back to Anthropic.

<Note>
  Unlike other properties that use an `_` prefix, the `_request_id` property is public. Unless documented otherwise, all other `_` prefix properties, methods, and modules are private.
</Note>


## Retries

Source: https://platform.claude.com/llms-full.txt#retries-5

Certain errors are automatically retried 2 times by default, with a short exponential backoff. Connection errors (for example, because of a network connectivity problem), 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the `max_retries` option to configure or disable this:


## Timeouts

Source: https://platform.claude.com/llms-full.txt#timeouts-4

By default requests time out after 10 minutes. You can configure this with a `timeout` option, which accepts a float or an `httpx2.Timeout` object:

On timeout, the SDK throws an `APITimeoutError`.

Note that requests that time out are [retried twice by default](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python#retries).


## Long requests

Source: https://platform.claude.com/llms-full.txt#long-requests-3

<Warning>
  Consider using the streaming [Messages API](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python#streaming-responses) for longer running requests.
</Warning>

Avoid setting a large `max_tokens` value without using streaming. Some networks may drop idle connections after a certain period of time, which can cause the request to fail or [timeout](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python#timeouts) without receiving a response from Anthropic.

The SDK will throw a `ValueError` if a non-streaming request is expected to take longer than approximately 10 minutes. Passing `stream=True` or overriding the `timeout` option at the client or request level disables this error.

An expected request latency longer than the [timeout](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python#timeouts) for a non-streaming request will result in the client terminating the connection and retrying without receiving a response.

The SDK sets a [TCP socket keep-alive](https://tldp.org/HOWTO/TCP-Keepalive-HOWTO/overview.html) option to reduce the impact of idle connection timeouts on some networks. This can be overridden by passing a custom `http_client` option to the client.


## Auto-pagination

Source: https://platform.claude.com/llms-full.txt#auto-pagination

List methods in the Claude API are paginated. You can use the `for` syntax to iterate through items across all pages:

For async iteration:

Alternatively, you can use the `.has_next_page()`, `.next_page_info()`, or `.get_next_page()` methods for more granular control working with pages:

Or work directly with the returned data:


## Default headers

Source: https://platform.claude.com/llms-full.txt#default-headers

The SDK automatically sends the `anthropic-version` header set to `2023-06-01`.

If you need to, you can override it by setting default headers on the client object or per-request.

<Warning>
  Overriding default headers may result in incorrect types and other unexpected or undefined behavior in the SDK.
</Warning>


## Type system

Source: https://platform.claude.com/llms-full.txt#type-system-2

### Request parameters

Nested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev) which also have helper methods for things like serializing back into JSON ([`v1`](https://docs.pydantic.dev/1.10/usage/models/), [`v2`](https://docs.pydantic.dev/latest/concepts/serialization/)).

Typed requests and responses provide autocomplete and documentation within your editor. If you'd like to see type errors in VS Code to help catch bugs earlier, set `python.analysis.typeCheckingMode` to `basic`.

### Response models

To convert a Pydantic model to a dictionary, use the helper methods:

### Handling null vs missing fields

In responses, you can distinguish between fields that are explicitly `null` versus fields that were not returned (missing):


## Advanced usage

Source: https://platform.claude.com/llms-full.txt#advanced-usage-7

### Accessing raw response data (for example, headers)

The "raw" `Response` returned by `httpx2` can be accessed through the `.with_raw_response` property on the client. This is useful for accessing response headers or other metadata:

These methods return an `APIResponse` object. On the async client they return an `AsyncAPIResponse`, and `.parse()`, `.read()`, `.text()`, and `.json()` must be awaited.

### Streaming response body

The `.with_raw_response` approach eagerly reads the full response body when you make the request. To stream the response body instead, use `.with_streaming_response`, which requires a context manager and only reads the response body once you call `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()`, or `.parse()`. In the async client, these are async methods.

The context manager is required so that the response will reliably be closed.

### Logging

The SDK uses the standard library `logging` module.

You can enable logging by setting the environment variable `ANTHROPIC_LOG` to `debug` or `info`:

### Making custom/undocumented requests

This library is typed for convenient access to the documented API. If you need to access undocumented endpoints, params, or response properties, the library can still be used.

#### Undocumented endpoints

To make requests to undocumented endpoints, you can use `client.get`, `client.post`, and other HTTP verbs. Options on the client, such as retries, are respected when making these requests.

#### Undocumented request params

If you want to explicitly send an extra parameter, you can do so with the `extra_query`, `extra_body`, and `extra_headers` request options.

<Warning>
  The `extra_` parameters override documented parameters of the same name. For security reasons, ensure these methods are only used with trusted input data.
</Warning>

#### Undocumented response properties

To access undocumented response properties, you can access the extra fields like `response.unknown_prop`. You can also get all extra fields on the Pydantic model as a dict with `response.model_extra`.

### Configuring the HTTP client

The SDK sends requests with [httpx2](https://httpx2.pydantic.dev), an API-compatible fork of `httpx`. To customize the HTTP client, including proxies and transports, pass your own [httpx2 client](https://httpx2.pydantic.dev/api/#client) as `http_client`:

You can also customize the client on a per-request basis by using `with_options()`:

<Note>
  Use `DefaultHttpxClient` and `DefaultAsyncHttpxClient` instead of raw `httpx2.Client` and `httpx2.AsyncClient` to ensure the SDK's default configuration (such as timeouts and connection limits) is preserved. The `http_client` argument must be an `httpx2` client. Passing a client from the separate `httpx` package raises a `TypeError`.
</Note>

Tracing and mocking tools that patch `httpx` itself, such as OpenTelemetry's `HTTPXClientInstrumentor`, Sentry's `httpx` integration, `respx`, or `pytest-httpx`, do not see the SDK's requests by default. To use them, call `httpx2.alias_httpx()` once at startup, before anything imports `httpx`. This makes `import httpx` resolve to `httpx2` for the whole process.

### Managing HTTP resources

By default the library closes underlying HTTP connections whenever the client is [garbage collected](https://docs.python.org/3/reference/datamodel.html#object.__del__). You can manually close the client using the `.close()` method if desired, or with a context manager that closes when exiting.


## Beta features

Source: https://platform.claude.com/llms-full.txt#beta-features-2

Beta features are available before general release to get early feedback and test new functionality. You can check the availability of all of Claude's capabilities and tools in the [build with Claude overview](https://platform.claude.com/docs/en/build-with-claude/overview).

You can access most beta API features through the `beta` property of the client. To enable a particular beta feature, you need to add the appropriate [beta header](https://platform.claude.com/docs/en/api/beta-headers) to the `betas` field when creating a message.

For example, to enable [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing):


## Platform integrations

Source: https://platform.claude.com/llms-full.txt#platform-integrations-5

<Note>
  For detailed platform setup guides with code examples, see:

  * [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)
  * [Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy)
  * [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)
  * [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)
  * [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry)
</Note>

All five client classes are included in the base `anthropic` package:

| Provider                         | Client                                         | Extra dependencies                 |
| -------------------------------- | ---------------------------------------------- | ---------------------------------- |
| Agent Platform                   | `from anthropic import AnthropicVertex`        | `pip install "anthropic[vertex]"`  |
| Bedrock                          | `from anthropic import AnthropicBedrockMantle` | `pip install "anthropic[bedrock]"` |
| Bedrock (`bedrock-runtime` path) | `from anthropic import AnthropicBedrock`       | `pip install "anthropic[bedrock]"` |
| Claude Platform on AWS           | `from anthropic import AnthropicAWS`           | `pip install "anthropic[aws]"`     |
| Foundry                          | `from anthropic import AnthropicFoundry`       | None                               |

The `AnthropicAWS` client is in beta. Pass `workspace_id` to the constructor or set the `ANTHROPIC_AWS_WORKSPACE_ID` environment variable.

Use `AnthropicBedrockMantle` for new projects; `AnthropicBedrock` remains for existing applications using the Bedrock `InvokeModel` API.


## Semantic versioning

Source: https://platform.claude.com/llms-full.txt#semantic-versioning-5

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backward-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use.
3. Changes that aren't expected to impact the vast majority of users in practice.

### Determining the installed version

If you've upgraded to the latest version but aren't seeing new features you were expecting, your Python environment is likely still using an older version. You can determine the version being used at runtime with:


## Additional resources

Source: https://platform.claude.com/llms-full.txt#additional-resources-9

* [GitHub repository](https://github.com/anthropics/anthropic-sdk-python)
* [API reference](https://platform.claude.com/docs/en/api/overview)
* [Streaming Messages](https://platform.claude.com/docs/en/build-with-claude/streaming)
* [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)


---
title: Ruby SDK
url: https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/ruby
description: Install and configure the Anthropic Ruby SDK with Sorbet types, streaming helpers, and connection pooling
---

The Anthropic Ruby library provides convenient access to the Claude API from any Ruby 3.2.0+ application. It ships with comprehensive types and docstrings in Yard, RBS, and RBI. The standard library's `net/http` is used as the HTTP transport, with connection pooling through the `connection_pool` gem.

<Info>
  For API feature documentation with code examples, see the [API reference](https://platform.claude.com/docs/en/api/overview). This page covers Ruby-specific SDK features and configuration.
</Info>


## Installation

Source: https://platform.claude.com/llms-full.txt#installation-7

Add the gem to your application's `Gemfile` with Bundler:


## Requirements

Source: https://platform.claude.com/llms-full.txt#requirements-6

Ruby 3.2.0 or higher.


## Usage

Source: https://platform.claude.com/llms-full.txt#usage-6

For authentication options including Workload Identity Federation, see [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication). If your API key is a [personal or service account key](https://platform.claude.com/docs/en/manage-claude/authentication#key-types) with access to multiple workspaces, set the workspace ID in the `anthropic-workspace-id` request header; [Select a workspace](https://platform.claude.com/docs/en/manage-claude/authentication#select-a-workspace) shows the per-request option for this SDK.


## Streaming

Source: https://platform.claude.com/llms-full.txt#streaming-11

The SDK provides support for streaming responses using Server-Sent Events (SSE).

### Streaming helpers

This library provides several conveniences for streaming messages, for example:

Streaming with `anthropic.messages.stream(...)` exposes various helpers including accumulation and SDK-specific events.


## Input schema and tool calling

Source: https://platform.claude.com/llms-full.txt#input-schema-and-tool-calling

The SDK provides helper mechanisms to define structured data classes for tools and let Claude automatically execute them. For detailed documentation on tool use patterns including the tool runner, see [Tool Runner (SDK)](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner).


## Structured outputs

Source: https://platform.claude.com/llms-full.txt#structured-outputs-2

For complete structured outputs documentation including Ruby examples, see [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).


## Handling errors

Source: https://platform.claude.com/llms-full.txt#handling-errors-2

When the library is unable to connect to the API, or if the API returns a non-success status code (that is, 4xx or 5xx response), a subclass of `Anthropic::Errors::APIError` is raised:

Error codes are as follows:

| Cause            | Error Type                 |
| ---------------- | -------------------------- |
| HTTP 400         | `BadRequestError`          |
| HTTP 401         | `AuthenticationError`      |
| HTTP 403         | `PermissionDeniedError`    |
| HTTP 404         | `NotFoundError`            |
| HTTP 409         | `ConflictError`            |
| HTTP 422         | `UnprocessableEntityError` |
| HTTP 429         | `RateLimitError`           |
| HTTP >= 500      | `InternalServerError`      |
| Other HTTP error | `APIStatusError`           |
| Timeout          | `APITimeoutError`          |
| Network error    | `APIConnectionError`       |


## Retries

Source: https://platform.claude.com/llms-full.txt#retries-6

Certain errors will be automatically retried 2 times by default, with a short exponential backoff.

Connection errors (for example, because of a network connectivity problem), 408 Request Timeout, 409 Conflict, 429 Rate Limit, >=500 Internal errors, and timeouts are all retried by default.

You can use the `max_retries` option to configure or disable this:


## Timeouts

Source: https://platform.claude.com/llms-full.txt#timeouts-5

By default, requests time out after 10 minutes. You can use the `timeout` option to configure this:

On timeout, `Anthropic::Errors::APITimeoutError` is raised.

Note that requests that time out are retried by default.


## Pagination

Source: https://platform.claude.com/llms-full.txt#pagination-10

List methods in the Claude API are paginated.

This library provides auto-paginating iterators with each list response, so you do not have to request successive pages manually:

Alternatively, you can use the `#next_page?` and `#next_page` methods for more granular control working with pages.


## File uploads

Source: https://platform.claude.com/llms-full.txt#file-uploads-4

Request parameters that correspond to file uploads can be passed as raw contents, a [`Pathname`](https://rubyapi.org/3.2/o/pathname) instance, [`StringIO`](https://rubyapi.org/3.2/o/stringio), or more.

Note that you can also pass a raw `IO` descriptor, but this disables retries, as the library can't be sure if the descriptor is a file or pipe (which cannot be rewound).


## Sorbet

Source: https://platform.claude.com/llms-full.txt#sorbet

This library provides comprehensive [RBI](https://sorbet.org/docs/rbi) definitions, and has no dependency on sorbet-runtime.

You can provide typesafe request parameters like so:

Or, equivalently:

### Enums

Since this library does not depend on `sorbet-runtime`, it cannot provide [`T::Enum`](https://sorbet.org/docs/tenum) instances. Instead, the SDK provides "tagged symbols", which is always a primitive at runtime:

Enum parameters have a "relaxed" type, so you can either pass in enum constants or their literal value:


## BaseModel

Source: https://platform.claude.com/llms-full.txt#basemodel

All parameter and response objects inherit from `Anthropic::Internal::Type::BaseModel`, which provides several conveniences, including:

1. All fields, including unknown ones, are accessible with `obj[:prop]` syntax, and can be destructured with `obj => {prop: prop}` or pattern-matching syntax.

2. Structural equivalence for equality; if two API calls return the same values, comparing the responses with == will return true.

3. Both instances and the classes themselves can be pretty-printed.

4. Helpers such as `#to_h`, `#deep_to_h`, `#to_json`, and `#to_yaml`.


## Concurrency and connection pooling

Source: https://platform.claude.com/llms-full.txt#concurrency-and-connection-pooling

The `Anthropic::Client` instances are threadsafe, but are only fork-safe when there are no in-flight HTTP requests.

Each instance of `Anthropic::Client` has its own HTTP connection pool with a default size of 99. As such, the recommendation is to create the client once per application in most settings.

When all available connections from the pool are checked out, requests wait for a new connection to become available, with queue time counting toward the request timeout.

Unless otherwise specified, other classes in the SDK do not have locks protecting their underlying data structure.


## Making custom or undocumented requests

Source: https://platform.claude.com/llms-full.txt#making-custom-or-undocumented-requests

### Undocumented properties

You can send undocumented parameters to any endpoint, and read undocumented response properties, like so:

<Warning>
  The `extra_` parameters of the same name override the documented parameters. For security reasons, ensure these methods are only used with trusted input data.
</Warning>

### Undocumented request params

If you want to explicitly send an extra param, you can do so with the `extra_query`, `extra_body`, and `extra_headers` under the `request_options:` parameter when making a request, as seen in the examples above.

### Undocumented endpoints

To make requests to undocumented endpoints while retaining the benefit of auth, retries, and so on, you can make requests using `anthropic.request`, like so:


## Platform integrations

Source: https://platform.claude.com/llms-full.txt#platform-integrations-6

<Note>
  For detailed platform setup guides with code examples, see:

  * [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)
  * [Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy)
  * [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)
  * [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)
</Note>

The Ruby SDK supports the following platforms:

* **Agent Platform:** `Anthropic::VertexClient`. Requires the `googleauth` gem.
* **Bedrock:** `Anthropic::BedrockMantleClient`, or `Anthropic::BedrockClient` for the `bedrock-runtime` path. `Anthropic::BedrockMantleClient` requires the `aws-sdk-core` gem; `Anthropic::BedrockClient` requires the `aws-sdk-bedrockruntime` gem.
* **Claude Platform on AWS:** Part of the main `anthropic` gem (requires the `aws-sdk-core` gem). Provides `Anthropic::AWSClient`. Pass `workspace_id:` to the constructor or set the `ANTHROPIC_AWS_WORKSPACE_ID` environment variable (see [Workspaces](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#workspaces)). Available in beta.
* **Foundry:** Not currently supported in the Ruby SDK. See [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry) for supported SDKs.

Use `Anthropic::BedrockMantleClient` for new projects; `Anthropic::BedrockClient` remains for existing applications using the Bedrock `InvokeModel` API.


## Semantic versioning

Source: https://platform.claude.com/llms-full.txt#semantic-versioning-6

This package follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions.

This package considers improvements to the (non-runtime) `*.rbi` and `*.rbs` type definitions to be non-breaking changes.


## Additional resources

Source: https://platform.claude.com/llms-full.txt#additional-resources-10

* [GitHub repository](https://github.com/anthropics/anthropic-sdk-ruby)
* [YARD documentation](https://gemdocs.org/gems/anthropic)
* [API reference](https://platform.claude.com/docs/en/api/overview)
* [Streaming Messages](https://platform.claude.com/docs/en/build-with-claude/streaming)


---
title: SDK middleware
url: https://platform.claude.com/docs/en/cli-sdks-libraries/middleware
description: Intercept and modify requests and responses in the Anthropic SDKs.
---

The Anthropic SDKs provide a middleware (or interceptor) hook that lets you run code before a request is sent and after the response is received. Use middleware for cross-cutting concerns such as logging, custom retries, request annotation, and refusal fallback handling.

Each middleware can inspect or replace the request before calling `next()`, and the response after `next()` returns.


## Registering middleware

Source: https://platform.claude.com/llms-full.txt#registering-middleware

Each middleware is a function that receives the outgoing request and a `next` callable. Call `next` to forward the request to the rest of the chain (or directly to the SDK core if this is the last middleware), and return its response. Anything before the `next` call runs on the way out; anything after runs on the way back.

<CodeGroup exclude="shell">
  ```python Python
  def logging_middleware(request: APIRequest, call_next: CallNext) -> APIResponse[Any]:
      # Before the request
      print(f"-> {request.method} {request.url}")

      # Forward the request to the rest of the chain
      response = call_next(request)

      # After the request
      print(f"<- {response.status_code}")

      return response


  client = Anthropic(middleware=[logging_middleware])

typescript TypeScript
  import type { Middleware } from "@anthropic-ai/sdk";

  const loggingMiddleware: Middleware = async (request, next, ctx) => {
    // Before the request
    ctx.logger.debug("->", request.method, request.url);

    // Forward the request to the rest of the chain
    const response = await next(request);

    // After the request
    ctx.logger.debug("<-", response.status, request.url);

    return response;
  };

  const client = new Anthropic({ middleware: [loggingMiddleware] });

csharp C#
  AnthropicClient client = new()
  {
      Handlers =
      [
          Handler.Create(async (request, next, cancellationToken) =>
          {
              // Before the request
              Console.WriteLine($"Sending {request.Method} {request.RequestUri}");

              // Forward the request to the next handler
              var response = await next(request, cancellationToken);

              // After the request
              Console.WriteLine($"Received {(int)response.StatusCode}");

              return response;
          }),
      ],
  };

go Go
  client := anthropic.NewClient(
  	option.WithMiddleware(func(req *http.Request, next option.MiddlewareNext) (*http.Response, error) {
  		// Before the request
  		start := time.Now()
  		slog.Info("sending request", "method", req.Method, "url", req.URL)

  		// Forward the request to the rest of the chain
  		res, err := next(req)
  		if err != nil {
  			return nil, err
  		}

  		// After the request
  		slog.Info("received response", "status", res.StatusCode, "duration", time.Since(start))

  		return res, nil
  	}),
  )

java Java
  AnthropicClient client = AnthropicOkHttpClient.builder()
      .fromEnv()
      .addInterceptor(Interceptor.syncOnly((nextClient, request, requestOptions) -> {
          // Before the request
          IO.println(request.method() + " /" + String.join("/", request.pathSegments()));

          // Forward the request to the next handler
          HttpResponse response = nextClient.execute(request, requestOptions);

          // After the request
          IO.println(response.statusCode());

          return response;
      }))
      .build();

php PHP
  $loggingMiddleware = function (RequestInterface $request, callable $next): ResponseInterface {
      // Before the request
      error_log("-> {$request->getMethod()} {$request->getUri()}");

      // Forward the request to the rest of the chain
      $response = $next($request);

      // After the request
      error_log("<- {$response->getStatusCode()}");

      return $response;
  };

  $client = new Client(requestOptions: ['middleware' => [$loggingMiddleware]]);

ruby Ruby
  logging_middleware = lambda do |request, call_next|
    # Before the request
    puts "-> #{request.method.upcase} #{request.url}"

    # Forward the request to the rest of the chain
    response = call_next.call(request)

    # After the request
    puts "<- #{response.status}"

    response
  end

  client = Anthropic::Client.new(middleware: [logging_middleware])
  ```
</CodeGroup>


## Middleware ordering

Source: https://platform.claude.com/llms-full.txt#middleware-ordering

When you register multiple middleware, they apply in the order given: the first middleware's "before" code runs first, and its "after" code runs last. Middleware registered on the client runs before middleware passed as a per-request option.

In the Go SDK, repeated `option.WithMiddleware` calls concatenate (client first, then method). In the other SDKs, pass an array; later entries wrap inner.
