# platform.claude.com Documentation (Part 8 of 35)

## How web fetch works

Source: https://platform.claude.com/llms-full.txt#how-web-fetch-works

Web fetch is a [server tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools): the API fetches the content during the request and inserts the results into the conversation. You don't run anything or return a `tool_result`. The exception is when Claude calls web fetch and one of your client tools in the same group of parallel tool calls: the API returns the response with `stop_reason: "tool_use"` before that fetch has run, then runs the fetch when you send back the client `tool_result` blocks. See [Mixing server tools and client tools in one turn](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#mixing-server-tools-and-client-tools-in-one-turn).

When you add the web fetch tool to your API request:

1. Claude determines when to fetch content based on the prompt and available URLs.
2. The API retrieves the full text content from the specified URL.
3. For PDFs, the API returns the content as base64-encoded data and processes it like a directly attached PDF document.
4. Claude analyzes the fetched content and provides a response with optional citations.

<Note>
  The web fetch tool currently does not support websites dynamically rendered with JavaScript. For pages that need a real browser (JavaScript rendering, clicking, or filling forms), consider the [browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool), a client tool where your application drives the browser and returns page text or screenshots to Claude as tool results.
</Note>

### When Claude fetches

Claude fetches when the request points at a specific page or document:

* A URL is provided in the conversation (or a previous tool result)
* The user names a specific resource (a particular article, README, pricing page, or documentation section) without a URL, and the [web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) is also enabled so Claude can locate it first (see [Combined search and fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool#combined-search-and-fetch))

Claude does **not** fetch for general-knowledge or open-ended questions that don't reference a specific page. "Summarize this article: `<url>`" triggers a fetch. "What are best practices for REST API design?" is answered directly.

### Dynamic filtering

Fetching full web pages and PDFs can quickly consume tokens, especially when only specific information is needed from large documents. With `web_fetch_20260209` or later, Claude can write and execute code to filter the fetched content before loading it into context.

This dynamic filtering is particularly useful for:

* Extracting specific sections from long documents
* Processing structured data from web pages
* Filtering relevant information from PDFs
* Reducing token costs when working with large documents

<Note>
  Dynamic filtering runs on the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool), which the API enables automatically for the request. You don't need to add the code execution tool to the `tools` array.
</Note>

To enable dynamic filtering, use `web_fetch_20260209` or any later version. The following examples use `web_fetch_20260318`:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-4-8",
      "max_tokens": 4096,
      "messages": [
        {
          "role": "user",
          "content": "Fetch the content at https://example.com/research-paper and extract the key findings."
        }
      ],
      "tools": [{
        "type": "web_fetch_20260318",
        "name": "web_fetch"
      }]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-4-8
  max_tokens: 4096
  messages:
    - role: user
      content: >-
        Fetch the content at https://example.com/research-paper
        and extract the key findings.
  tools:
    - type: web_fetch_20260318
      name: web_fetch
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-4-8",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": "Fetch the content at https://example.com/research-paper and extract the key findings.",
          }
      ],
      tools=[{"type": "web_fetch_20260318", "name": "web_fetch"}],
  )
  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-4-8",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content:
          "Fetch the content at https://example.com/research-paper and extract the key findings."
      }
    ],
    tools: [{ type: "web_fetch_20260318", name: "web_fetch" }]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus4_8,
      MaxTokens = 4096,
      Messages = [new() { Role = Role.User, Content = "Fetch the content at https://example.com/research-paper and extract the key findings." }],
      Tools = [new ToolUnion(new WebFetchTool20260318())]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus4_8,
  	MaxTokens: 4096,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Fetch the content at https://example.com/research-paper and extract the key findings.")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfWebFetchTool20260318: &anthropic.WebFetchTool20260318Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  import com.anthropic.models.messages.WebFetchTool20260318;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_4_8)
          .maxTokens(4096L)
          .addUserMessage("Fetch the content at https://example.com/research-paper and extract the key findings.")
          .addTool(WebFetchTool20260318.builder().build())
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Fetch the content at https://example.com/research-paper and extract the key findings.']
      ],
      model: 'claude-opus-4-8',
      tools: [[
          'type' => 'web_fetch_20260318',
          'name' => 'web_fetch',
      ]],
  );
  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-4-8",
    max_tokens: 4096,
    messages: [
      { role: "user", content: "Fetch the content at https://example.com/research-paper and extract the key findings." }
    ],
    tools: [{
      type: "web_fetch_20260318",
      name: "web_fetch"
    }]
  )
  puts message
  ```
</CodeGroup>


## How to use web fetch

Source: https://platform.claude.com/llms-full.txt#how-to-use-web-fetch

Provide the web fetch tool in your API request:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-4-8",
      "max_tokens": 1024,
      "messages": [
        {
          "role": "user",
          "content": "Please analyze the content at https://example.com/article"
        }
      ],
      "tools": [{
        "type": "web_fetch_20250910",
        "name": "web_fetch",
        "max_uses": 5
      }]
    }'

bash CLI
  ant messages create \
    --model claude-opus-4-8 \
    --max-tokens 1024 \
    --message '{role: user, content: "Please analyze the content at https://example.com/article"}' \
    --tool '{type: web_fetch_20250910, name: web_fetch, max_uses: 5}'

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-4-8",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": "Please analyze the content at https://example.com/article",
          }
      ],
      tools=[{"type": "web_fetch_20250910", "name": "web_fetch", "max_uses": 5}],
  )
  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-4-8",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: "Please analyze the content at https://example.com/article"
      }
    ],
    tools: [
      {
        type: "web_fetch_20250910",
        name: "web_fetch",
        max_uses: 5
      }
    ]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus4_8,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Please analyze the content at https://example.com/article" }],
      Tools = [new ToolUnion(new WebFetchTool20250910() { MaxUses = 5 })]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus4_8,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Please analyze the content at https://example.com/article")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfWebFetchTool20250910: &anthropic.WebFetchTool20250910Param{
  			MaxUses: anthropic.Int(5),
  		}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  import com.anthropic.models.messages.WebFetchTool20250910;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_4_8)
          .maxTokens(1024L)
          .addUserMessage("Please analyze the content at https://example.com/article")
          .addTool(WebFetchTool20250910.builder()
              .maxUses(5L)
              .build())
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => 'Please analyze the content at https://example.com/article']
      ],
      model: 'claude-opus-4-8',
      tools: [[
          'type' => 'web_fetch_20250910',
          'name' => 'web_fetch',
          'max_uses' => 5,
      ]],
  );
  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-4-8",
    max_tokens: 1024,
    messages: [
      { role: "user", content: "Please analyze the content at https://example.com/article" }
    ],
    tools: [{
      type: "web_fetch_20250910",
      name: "web_fetch",
      max_uses: 5
    }]
  )
  puts message
  ```
</CodeGroup>


## Tool definition

Source: https://platform.claude.com/llms-full.txt#tool-definition-3

The web fetch tool supports the following parameters:

```json JSON
{
  "type": "web_fetch_20250910",
  "name": "web_fetch",

  // Optional: Limit the number of fetches per request
  "max_uses": 10,

  // Optional: Only fetch from these domains
  "allowed_domains": ["example.com", "docs.example.com"],

  // Optional: Never fetch from these domains (cannot be combined with allowed_domains)
  "blocked_domains": ["private.example.com"],

  // Optional: Enable citations for fetched content
  "citations": {
    "enabled": true
  },

  // Optional: Maximum content length in tokens
  "max_content_tokens": 100000
}

json
{
  "tools": [
    {
      "type": "web_fetch_20260309",
      "name": "web_fetch",
      "use_cache": false
    }
  ]
}

json
{
  "tools": [
    {
      "type": "web_fetch_20260318",
      "name": "web_fetch",
      "response_inclusion": "excluded"
    }
  ]
}
```

### Citations

Unlike web search where citations are always enabled, citations are optional for web fetch and disabled by default. Set `"citations": {"enabled": true}` to enable Claude to cite specific passages from fetched documents.

<Note>
  When displaying API outputs directly to end users, include citations to the original source. If you are making modifications to API outputs, including by reprocessing or combining them with your own material before displaying them to end users, display citations as appropriate based on consultation with your legal team.
</Note>


## Response

Source: https://platform.claude.com/llms-full.txt#response

Here's an example response structure:

```json Output
{
  "role": "assistant",
  "content": [
    // 1. Claude's decision to fetch
    {
      "type": "text",
      "text": "I'll fetch the content from the article to analyze it."
    },
    // 2. The fetch request
    {
      "type": "server_tool_use",
      "id": "srvtoolu_01234567890abcdef",
      "name": "web_fetch",
      "input": {
        "url": "https://example.com/article"
      }
    },
    // 3. Fetch results
    {
      "type": "web_fetch_tool_result",
      "tool_use_id": "srvtoolu_01234567890abcdef",
      "content": {
        "type": "web_fetch_result",
        "url": "https://example.com/article",
        "content": {
          "type": "document",
          "source": {
            "type": "text",
            "media_type": "text/plain",
            "data": "Full text content of the article..."
          },
          "title": "Article Title",
          "citations": { "enabled": true }
        },
        "retrieved_at": "2025-08-25T10:30:00Z"
      }
    },
    // 4. Claude's analysis with citations (if enabled)
    {
      "text": "Based on the article, ",
      "type": "text"
    },
    {
      "text": "the main argument presented is that artificial intelligence will transform healthcare",
      "type": "text",
      "citations": [
        {
          "type": "char_location",
          "document_index": 0,
          "document_title": "Article Title",
          "start_char_index": 1234,
          "end_char_index": 1456,
          "cited_text": "Artificial intelligence is poised to revolutionize healthcare delivery..."
        }
      ]
    }
  ],
  "id": "msg_a930390d3a",
  "usage": {
    "input_tokens": 25039,
    "output_tokens": 931,
    "server_tool_use": {
      "web_fetch_requests": 1
    }
  },
  "stop_reason": "end_turn"
}

json Output
{
  "type": "web_fetch_tool_result",
  "tool_use_id": "srvtoolu_02",
  "content": {
    "type": "web_fetch_result",
    "url": "https://example.com/paper.pdf",
    "content": {
      "type": "document",
      "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": "JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmo..."
      },
      "citations": { "enabled": true }
    },
    "retrieved_at": "2025-08-25T10:30:02Z"
  }
}

json Output
{
  "type": "web_fetch_tool_result",
  "tool_use_id": "srvtoolu_a93jad",
  "content": {
    "type": "web_fetch_tool_result_error",
    "error_code": "url_not_accessible"
  }
}
```

These are the possible error codes:

* `invalid_tool_input`: Invalid tool input, such as a malformed URL or a non-HTTP(S) scheme
* `url_too_long`: URL exceeds maximum length (250 characters)
* `url_not_allowed`: URL blocked by domain filtering rules (including your organization's settings) or by Anthropic-side restrictions, such as private addresses and `robots.txt`
* `url_not_in_prior_context`: URL did not appear earlier in the conversation (see [URL validation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool#url-validation))
* `url_not_accessible`: Failed to fetch content (HTTP error)
* `too_many_requests`: Rate limit exceeded
* `unsupported_content_type`: Content type not supported (only text, HTML, and PDF)
* `max_uses_exceeded`: Maximum web fetch tool uses exceeded
* `unavailable`: An internal error occurred


## URL validation

Source: https://platform.claude.com/llms-full.txt#url-validation

For security reasons, the web fetch tool can only fetch URLs that have previously appeared in the conversation context. This includes:

* URLs in user messages
* URLs in client-side tool results
* URLs from previous web search or web fetch results

The tool cannot fetch URLs that appear only in Claude's own output or only in the system prompt. To make a URL from the system prompt fetchable, also include it in a user message. Results of other server-side tools, such as [code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool), the [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector), or [tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool), are not an allowed source either. Client-side tool results are an allowed source even when they echo text that Claude produced (for example, a command that prints its input, or an error message that quotes it).


## Combined search and fetch

Source: https://platform.claude.com/llms-full.txt#combined-search-and-fetch

When both the web search and web fetch tools are enabled, and the user names a specific page or document without providing a URL (for example, "read the README from the anthropics/anthropic-sdk-python repository"), Claude uses web search to locate it, then fetches the result. The following example asks for a search and an analysis in one request:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-4-8",
      "max_tokens": 4096,
      "messages": [
        {
          "role": "user",
          "content": "Find recent articles about quantum computing and analyze the most relevant one in detail"
        }
      ],
      "tools": [
        {
          "type": "web_search_20250305",
          "name": "web_search",
          "max_uses": 3
        },
        {
          "type": "web_fetch_20250910",
          "name": "web_fetch",
          "max_uses": 5,
          "citations": {"enabled": true}
        }
      ]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-4-8
  max_tokens: 4096
  messages:
    - role: user
      content: >-
        Find recent articles about quantum computing
        and analyze the most relevant one in detail
  tools:
    - type: web_search_20250305
      name: web_search
      max_uses: 3
    - type: web_fetch_20250910
      name: web_fetch
      max_uses: 5
      citations:
        enabled: true
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-4-8",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": "Find recent articles about quantum computing and analyze the most relevant one in detail",
          }
      ],
      tools=[
          {"type": "web_search_20250305", "name": "web_search", "max_uses": 3},
          {
              "type": "web_fetch_20250910",
              "name": "web_fetch",
              "max_uses": 5,
              "citations": {"enabled": True},
          },
      ],
  )
  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-4-8",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content:
          "Find recent articles about quantum computing and analyze the most relevant one in detail"
      }
    ],
    tools: [
      { type: "web_search_20250305", name: "web_search", max_uses: 3 },
      {
        type: "web_fetch_20250910",
        name: "web_fetch",
        max_uses: 5,
        citations: { enabled: true }
      }
    ]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus4_8,
      MaxTokens = 4096,
      Messages = [new() { Role = Role.User, Content = "Find recent articles about quantum computing and analyze the most relevant one in detail" }],
      Tools = [
          new ToolUnion(new WebSearchTool20250305() { MaxUses = 3 }),
          new ToolUnion(new WebFetchTool20250910() { MaxUses = 5, Citations = new() { Enabled = true } })
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus4_8,
  	MaxTokens: 4096,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Find recent articles about quantum computing and analyze the most relevant one in detail")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfWebSearchTool20250305: &anthropic.WebSearchTool20250305Param{
  			MaxUses: anthropic.Int(3),
  		}},
  		{OfWebFetchTool20250910: &anthropic.WebFetchTool20250910Param{
  			MaxUses:   anthropic.Int(5),
  			Citations: anthropic.CitationsConfigParam{Enabled: anthropic.Bool(true)},
  		}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  import com.anthropic.models.messages.CitationsConfigParam;
  // ...
  import com.anthropic.models.messages.WebFetchTool20250910;
  import com.anthropic.models.messages.WebSearchTool20250305;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_4_8)
          .maxTokens(4096L)
          .addUserMessage("Find recent articles about quantum computing and analyze the most relevant one in detail")
          .addTool(WebSearchTool20250305.builder()
              .maxUses(3L)
              .build())
          .addTool(WebFetchTool20250910.builder()
              .maxUses(5L)
              .citations(CitationsConfigParam.builder().enabled(true).build())
              .build())
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Find recent articles about quantum computing and analyze the most relevant one in detail']
      ],
      model: 'claude-opus-4-8',
      tools: [
          [
              'type' => 'web_search_20250305',
              'name' => 'web_search',
              'max_uses' => 3,
          ],
          [
              'type' => 'web_fetch_20250910',
              'name' => 'web_fetch',
              'max_uses' => 5,
              'citations' => ['enabled' => true],
          ],
      ],
  );
  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-4-8",
    max_tokens: 4096,
    messages: [
      { role: "user", content: "Find recent articles about quantum computing and analyze the most relevant one in detail" }
    ],
    tools: [
      {
        type: "web_search_20250305",
        name: "web_search",
        max_uses: 3
      },
      {
        type: "web_fetch_20250910",
        name: "web_fetch",
        max_uses: 5,
        citations: { enabled: true }
      }
    ]
  )
  puts message
  ```
</CodeGroup>

In this workflow, Claude:

1. Uses web search to find relevant articles.
2. Selects the most promising results.
3. Uses web fetch to retrieve full content.
4. Provides detailed analysis with citations.


## Prompt caching

Source: https://platform.claude.com/llms-full.txt#prompt-caching-2

To cache tool definitions across turns, see [Tool use with prompt caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching).


## Streaming

Source: https://platform.claude.com/llms-full.txt#streaming-5

With streaming enabled, fetch events are part of the stream with a pause during content retrieval:

```sse Output
event: message_start
data: {"type": "message_start", "message": {"id": "msg_abc123", "type": "message"}}

event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}

// Claude's decision to fetch

event: content_block_start
data: {"type": "content_block_start", "index": 1, "content_block": {"type": "server_tool_use", "id": "srvtoolu_xyz789", "name": "web_fetch"}}

// Fetch URL streamed
event: content_block_delta
data: {"type": "content_block_delta", "index": 1, "delta": {"type": "input_json_delta", "partial_json": "{\"url\":\"https://example.com/article\"}"}}

// Pause while fetch executes

// Fetch results streamed
event: content_block_start
data: {"type": "content_block_start", "index": 2, "content_block": {"type": "web_fetch_tool_result", "tool_use_id": "srvtoolu_xyz789", "content": {"type": "web_fetch_result", "url": "https://example.com/article", "content": {"type": "document", "source": {"type": "text", "media_type": "text/plain", "data": "Article content..."}}}}}

// Claude's response continues...
```


## Batch requests

Source: https://platform.claude.com/llms-full.txt#batch-requests-4

You can include the web fetch tool in the [Messages Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing). Web fetch tool calls through the Messages Batches API are priced the same as those in regular Messages API requests.


## Usage and pricing

Source: https://platform.claude.com/llms-full.txt#usage-and-pricing-2

Web fetch usage has **no additional charges** beyond standard token costs:

The web fetch tool is available on the Claude API at **no additional cost**. You only pay standard token costs for the fetched content that becomes part of your conversation context.

To protect against inadvertently fetching large content that would consume excessive tokens, use the `max_content_tokens` parameter to set appropriate limits based on your use case and budget considerations.

Example token usage for typical content:

* Average web page (10 kB): \~2,500 tokens
* Large documentation page (100 kB): \~25,000 tokens
* Research paper PDF (500 kB): \~125,000 tokens


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-41

<CardGroup>
  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool" title="Code execution tool" icon="code">
    Run Python and bash code in a sandboxed container to analyze data, generate files, and iterate on solutions.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools" title="Server tools" icon="cloud">
    Work with Anthropic-executed tools: server\_tool\_use blocks, pause\_turn continuation, and domain filtering.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference" title="Tool reference" icon="book">
    Directory of Anthropic-provided tools and reference for optional tool definition properties.
  </Card>
</CardGroup>


---
title: Web search tool
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
description: Give Claude access to current web content with cited sources, optional dynamic filtering, and domain controls.
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

The web search tool gives Claude direct access to real-time web content, allowing it to answer questions with up-to-date information beyond its knowledge cutoff. The response includes citations for sources drawn from search results.

With `web_search_20260209` and later versions, Claude can write and run code that filters the search results before they reach the context window (**dynamic filtering**), keeping only relevant information. Dynamic filtering is available with Claude 4.6 and later models and [Claude Mythos Preview](https://anthropic.com/glasswing).

Three versions of the web search tool are available:

* `web_search_20250305`: basic web search
* `web_search_20260209`: adds [dynamic filtering](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool#dynamic-filtering)
* `web_search_20260318`: adds [response inclusion](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool#response-inclusion) control for agentic workflows

The examples on this page use `web_search_20250305` for basic search and `web_search_20260318` for dynamic filtering.

<Note>
  For [Claude Mythos Preview](https://anthropic.com/glasswing), web search is supported on the Claude API, Google Cloud, and Microsoft Foundry. Web search is not available for Mythos Preview on Amazon Bedrock or [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws).
</Note>

For web search's Zero Data Retention eligibility and the related `allowed_callers` configuration, see [Server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#zdr-and-allowed-callers).

For model support, see the [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference).


## How web search works

Source: https://platform.claude.com/llms-full.txt#how-web-search-works

When you add the web search tool to your API request:

1. Claude determines when to search based on the prompt.
2. The API runs the searches and provides Claude with the results. This process can repeat multiple times throughout a single request.
3. At the end of its turn, Claude provides a final response with cited sources.

### When Claude searches

Claude searches when the request depends on information that is current, changing, or outside its training data:

* Recent events, news, or announcements
* Current prices, rates, scores, or statistics
* Information about specific organizations, people, or products that might have changed
* Explicit requests to search or look something up

Claude answers directly without searching when the request draws on stable knowledge:

* Established facts, math, science fundamentals, or coding concepts
* Creative writing or brainstorming
* Analysis of content already provided in the conversation
* Conversational turns and greetings

Triggering is steerable through your system prompt: you can encourage Claude to search more readily or to prefer answering directly. For a hard constraint, use `max_uses` to cap the number of searches for each request.

### Dynamic filtering

With basic web search, every search result is loaded into Claude's context window, and much of that content can be irrelevant to the request. With `web_search_20260209` or later, Claude instead writes and runs code that filters the results first, so only relevant content reaches the context window. This reduces token use on search-heavy requests.

Dynamic filtering runs web search from inside [code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool): on `web_search_20260209` and later, the tool's `allowed_callers` field defaults to `["code_execution_20260120"]`, and when dynamic filtering runs, the API provisions the code execution it needs for the request automatically. You don't need to add the code execution tool to `tools` yourself. There are no additional charges for code execution calls made this way beyond the standard token costs.

To call web search directly, without dynamic filtering, set `allowed_callers: ["direct"]`. Models that don't support programmatic tool calling require this setting. Without it, the API returns a 400 error that tells you to set it.

<Note>
  The web search tool (with and without dynamic filtering) is available on the Claude API, [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), and [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry). On Microsoft Foundry, deployments [hosted on Azure](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#additional-features-not-supported-when-hosted-on-azure) support only the basic web search tool (`web_search_20250305`, without dynamic filtering). Deployments hosted on Anthropic support all versions. On Google Cloud, only the basic web search tool (without dynamic filtering) is available. Web search is not available on Amazon Bedrock.
</Note>

The following examples use `web_search_20260318`:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [
        {
          "role": "user",
          "content": "Search for the current prices of AAPL and GOOGL, then calculate which has a better P/E ratio."
        }
      ],
      "tools": [{
        "type": "web_search_20260318",
        "name": "web_search"
      }]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: >-
        Search for the current prices of AAPL and GOOGL, then calculate
        which has a better P/E ratio.
  tools:
    - type: web_search_20260318
      name: web_search
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": "Search for the current prices of AAPL and GOOGL, then calculate which has a better P/E ratio.",
          }
      ],
      tools=[{"type": "web_search_20260318", "name": "web_search"}],
  )
  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content:
          "Search for the current prices of AAPL and GOOGL, then calculate which has a better P/E ratio."
      }
    ],
    tools: [{ type: "web_search_20260318", name: "web_search" }]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 4096,
      Messages = [new() { Role = Role.User, Content = "Search for the current prices of AAPL and GOOGL, then calculate which has a better P/E ratio." }],
      Tools = [new ToolUnion(new WebSearchTool20260318())]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Search for the current prices of AAPL and GOOGL, then calculate which has a better P/E ratio.")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfWebSearchTool20260318: &anthropic.WebSearchTool20260318Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.messages.WebSearchTool20260318;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .addUserMessage("Search for the current prices of AAPL and GOOGL, then calculate which has a better P/E ratio.")
          .addTool(WebSearchTool20260318.builder().build())
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Search for the current prices of AAPL and GOOGL, then calculate which has a better P/E ratio.'],
      ],
      model: 'claude-opus-5',
      tools: [
          [
              'type' => 'web_search_20260318',
              'name' => 'web_search',
          ],
      ],
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      { role: "user", content: "Search for the current prices of AAPL and GOOGL, then calculate which has a better P/E ratio." }
    ],
    tools: [{
      type: "web_search_20260318",
      name: "web_search"
    }]
  )
  puts message
  ```
</CodeGroup>


## How to use web search

Source: https://platform.claude.com/llms-full.txt#how-to-use-web-search

<Note>
  Web search is enabled for your organization unless an administrator has disabled it in the [Claude Console](https://platform.claude.com/settings/privacy), where they can also restrict which domains it searches. If it's disabled, a request that includes the tool fails with a 400 `invalid_request_error` that says web search is not enabled, rather than an [error code](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool#errors) inside a search result.
</Note>

These organization-level settings in the Claude Console apply to Messages API requests only. [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) sessions use only the per-tool `allowed_domains` and `blocked_domains` lists on the agent toolset; see [Restrict web search and web fetch domains](https://platform.claude.com/docs/en/managed-agents/tools#restrict-web-search-and-web-fetch-domains).

Provide the web search tool in your API request:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [
        {
          "role": "user",
          "content": "What is the weather in NYC?"
        }
      ],
      "tools": [{
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 5
      }]
    }'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: What is the weather in NYC?}' \
    --tool '{type: web_search_20250305, name: web_search, max_uses: 5}'

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "What's the weather in NYC?"}],
      tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
  )
  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: "What's the weather in NYC?"
      }
    ],
    tools: [
      {
        type: "web_search_20250305",
        name: "web_search",
        max_uses: 5
      }
    ]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "What's the weather in NYC?" }],
      Tools = [new ToolUnion(new WebSearchTool20250305() { MaxUses = 5 })]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather in NYC?")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfWebSearchTool20250305: &anthropic.WebSearchTool20250305Param{
  			MaxUses: anthropic.Int(5),
  		}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.messages.WebSearchTool20250305;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addUserMessage("What's the weather in NYC?")
          .addTool(WebSearchTool20250305.builder()
              .maxUses(5L)
              .build())
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => "What's the weather in NYC?"],
      ],
      model: 'claude-opus-5',
      tools: [
          [
              'type' => 'web_search_20250305',
              'name' => 'web_search',
              'max_uses' => 5,
          ],
      ],
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      { role: "user", content: "What's the weather in NYC?" }
    ],
    tools: [{
      type: "web_search_20250305",
      name: "web_search",
      max_uses: 5
    }]
  )
  puts message
  ```
</CodeGroup>


## Tool definition

Source: https://platform.claude.com/llms-full.txt#tool-definition-4

The web search tool supports the following parameters:

```json JSON
{
  "type": "web_search_20250305",
  "name": "web_search",

  // Optional: Limit the number of searches per request
  "max_uses": 5,

  // Optional: Only include results from these domains.
  // Use allowed_domains or blocked_domains, not both.
  "allowed_domains": ["example.com", "trusteddomain.org"],

  // Optional: Never include results from these domains
  "blocked_domains": ["untrustedsource.com"],

  // Optional: Localize search results
  "user_location": {
    "type": "approximate",
    "city": "San Francisco",
    "region": "California",
    "country": "US",
    "timezone": "America/Los_Angeles"
  }
}

json JSON
{
  "tools": [
    {
      "type": "web_search_20260318",
      "name": "web_search",
      "response_inclusion": "excluded"
    }
  ]
}
```


## Response

Source: https://platform.claude.com/llms-full.txt#response-2

Here's an example response structure:

```json Output
{
  "role": "assistant",
  "content": [
    // 1. Claude's decision to search
    {
      "type": "text",
      "text": "I'll search for when Claude Shannon was born."
    },
    // 2. The search query used
    {
      "type": "server_tool_use",
      "id": "srvtoolu_01WYG3ziw53XMcoyKL4XcZmE",
      "name": "web_search",
      "input": {
        "query": "claude shannon birth date"
      }
    },
    // 3. Search results
    {
      "type": "web_search_tool_result",
      "tool_use_id": "srvtoolu_01WYG3ziw53XMcoyKL4XcZmE",
      "content": [
        {
          "type": "web_search_result",
          "url": "https://en.wikipedia.org/wiki/Claude_Shannon",
          "title": "Claude Shannon - Wikipedia",
          "encrypted_content": "EqgfCioIARgBIiQ3YTAwMjY1Mi1mZjM5LTQ1NGUtODgxNC1kNjNjNTk1ZWI3Y...",
          "page_age": "April 30, 2025"
        }
      ]
    },
    {
      "text": "Based on the search results, ",
      "type": "text"
    },
    // 4. Claude's response with citations
    {
      "text": "Claude Shannon was born on April 30, 1916, in Petoskey, Michigan",
      "type": "text",
      "citations": [
        {
          "type": "web_search_result_location",
          "url": "https://en.wikipedia.org/wiki/Claude_Shannon",
          "title": "Claude Shannon - Wikipedia",
          "encrypted_index": "Eo8BCioIAhgBIiQyYjQ0OWJmZi1lNm..",
          "cited_text": "Claude Elwood Shannon (April 30, 1916 – February 24, 2001) was an American mathematician, electrical engineer, computer scientist, cryptographer and i..."
        }
      ]
    }
  ],
  "id": "msg_a930390d3a",
  "usage": {
    "input_tokens": 6039,
    "output_tokens": 931,
    "server_tool_use": {
      "web_search_requests": 1
    }
  },
  "stop_reason": "end_turn"
}

json Output
{
  "type": "web_search_tool_result",
  "tool_use_id": "srvtoolu_a93jad",
  "content": {
    "type": "web_search_tool_result_error",
    "error_code": "max_uses_exceeded"
  }
}
```

On an error, `content` is a single error object rather than a list of result blocks. A search that succeeds but matches no results returns an empty `content` list, not an error.

These are the possible error codes:

* `too_many_requests`: Rate limit exceeded
* `invalid_tool_input`: Invalid search query parameter
* `max_uses_exceeded`: Maximum web search tool uses exceeded
* `query_too_long`: Query exceeds maximum length
* `request_too_large`: The search request is too large, typically because of a long domain filter list
* `unavailable`: An internal error occurred

### `pause_turn` stop reason

The API can pause a long-running search turn and return `stop_reason: "pause_turn"`. To continue, send the paused assistant message back unchanged in a new request.

If Claude calls web search and one of your client tools in the same group of parallel tool calls, the API returns `stop_reason: "tool_use"` instead and does not run the search yet. To continue, return the client tool results, and the API runs the search in the next request. See [Mixing server tools and client tools in one turn](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#mixing-server-tools-and-client-tools-in-one-turn).

For the server-side loop and `pause_turn` handling, see [The server-side loop and pause\_turn](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#the-server-side-loop-and-pause-turn) in the Server tools guide.


## Prompt caching

Source: https://platform.claude.com/llms-full.txt#prompt-caching-3

To cache tool definitions across turns, see [Tool use with prompt caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching).


## Streaming

Source: https://platform.claude.com/llms-full.txt#streaming-6

With streaming enabled, you'll receive search events as part of the stream. There will be a pause while the search runs:

```sse Output
event: message_start
data: {"type": "message_start", "message": {"id": "msg_abc123", "type": "message"}}

event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}

// Claude's decision to search

event: content_block_start
data: {"type": "content_block_start", "index": 1, "content_block": {"type": "server_tool_use", "id": "srvtoolu_xyz789", "name": "web_search"}}

// Search query streamed
event: content_block_delta
data: {"type": "content_block_delta", "index": 1, "delta": {"type": "input_json_delta", "partial_json": "{\"query\":\"latest quantum computing breakthroughs 2025\"}"}}

// Pause while search executes

// Search results streamed
event: content_block_start
data: {"type": "content_block_start", "index": 2, "content_block": {"type": "web_search_tool_result", "tool_use_id": "srvtoolu_xyz789", "content": [{"type": "web_search_result", "title": "Quantum Computing Breakthroughs in 2025", "url": "https://example.com"}]}}

// Claude's response with citations (omitted in this example)
```


## Batch requests

Source: https://platform.claude.com/llms-full.txt#batch-requests-5

You can include the web search tool in the [Messages Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing). Web search tool calls through the Messages Batches API are priced the same as those in regular Messages API requests.

To protect shared capacity, the Batches API throttles web search requests per organization, so large batches with many searches might take longer to complete. You can see your organization's web search rate limit on the [Rate limits](https://platform.claude.com/settings/limits) page in the Claude Console. To request a higher limit, contact sales from that page.


## Usage and pricing

Source: https://platform.claude.com/llms-full.txt#usage-and-pricing-3

Web search usage is charged in addition to token usage:

Web search is available on the Claude API for **$10 per 1,000 searches**, plus standard token costs for search-generated content. Web search results retrieved throughout a conversation are counted as input tokens, in search iterations executed during a single turn and in subsequent conversation turns.

Each web search counts as one use, regardless of the number of results returned. If an error occurs during web search, the web search will not be billed.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-42

<CardGroup cols={3}>
  <Card title="Web fetch tool" icon="link" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool">
    Fetch and read content from specific URLs to augment Claude's context with live web content.
  </Card>

  <Card title="Server tools" icon="tool" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools">
    Work with Anthropic-executed tools: server\_tool\_use blocks, pause\_turn continuation, and domain filtering.
  </Card>

  <Card title="Tool reference" icon="book" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference">
    Directory of Anthropic-provided tools and reference for optional tool definition properties.
  </Card>
</CardGroup>


### Tool infrastructure

---
title: Fine-grained tool streaming
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming
description: Stream tool inputs without server-side JSON buffering for latency-sensitive applications.
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

Fine-grained tool streaming delivers a tool's input to your client as Claude generates it, without server-side buffering or JSON validation. Skipping the buffering step reduces the time to the first fragment of a large parameter, such as a document or a block of code, and the fragments arrive through the same [Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming) events as standard tool use.

<Warning>
  Because the API does not buffer or validate a tool's input before streaming it, you might receive partial or invalid JSON. A response that ends with the [stop reason](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons) `max_tokens` can also cut a parameter off midway. Accumulate the fragments, guard the parse, and see [Handling invalid JSON in tool responses](https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming#handling-invalid-json-in-tool-responses) for how to return unparseable input to Claude.
</Warning>


## How to use fine-grained tool streaming

Source: https://platform.claude.com/llms-full.txt#how-to-use-fine-grained-tool-streaming

All models support fine-grained tool streaming on the Claude API, [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), and [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry). To use it, set `eager_input_streaming` to `true` on any user-defined tool where you want fine-grained streaming enabled, and enable streaming on your request.

The `eager_input_streaming` field is optional. Setting it to `true` turns on fine-grained streaming for that tool, and omitting it gives you standard buffered streaming, in which the API buffers and validates each parameter value before streaming it back. The exception is a request that still sends the legacy `fine-grained-tool-streaming-2025-05-14` beta header, which turns fine-grained streaming on for tools that leave the field unset. The per-tool field replaces that header, and an explicit `false` keeps buffered streaming for a tool even when a request still sends it. The legacy header cannot be combined with a [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) or [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) toolset entry: the API rejects a request that sends both, so remove the header and set `eager_input_streaming` on the user-defined tools that need it. See [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference) for the field definition.

The following example turns on fine-grained streaming for a `make_file` tool and asks Claude for a long poem, so the tool input is large enough to watch it stream in:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 65536,
      "tools": [
        {
          "name": "make_file",
          "description": "Write text to a file",
          "eager_input_streaming": true,
          "input_schema": {
            "type": "object",
            "properties": {
              "filename": {
                "type": "string",
                "description": "The filename to write text to"
              },
              "lines_of_text": {
                "type": "array",
                "description": "An array of lines of text to write to the file"
              }
            },
            "required": ["filename", "lines_of_text"]
          }
        }
      ],
      "messages": [
        {
          "role": "user",
          "content": "Can you write a long poem and make a file called poem.txt?"
        }
      ],
      "stream": true
    }'

bash CLI
  ant messages create --stream --format jsonl <<'YAML' |
  model: claude-opus-5
  max_tokens: 65536
  tools:
    - name: make_file
      description: Write text to a file
      eager_input_streaming: true
      input_schema:
        type: object
        properties:
          filename:
            type: string
            description: The filename to write text to
          lines_of_text:
            type: array
            description: An array of lines of text to write to the file
        required:
          - filename
          - lines_of_text
  messages:
    - role: user
      content: Can you write a long poem and make a file called poem.txt?
  YAML
    jq -rj 'select(.delta.type == "input_json_delta") | .delta.partial_json'

python Python
  client = anthropic.Anthropic()

  with client.messages.stream(
      max_tokens=65536,
      model="claude-opus-5",
      tools=[
          {
              "name": "make_file",
              "description": "Write text to a file",
              "eager_input_streaming": True,
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "filename": {
                          "type": "string",
                          "description": "The filename to write text to",
                      },
                      "lines_of_text": {
                          "type": "array",
                          "description": "An array of lines of text to write to the file",
                      },
                  },
                  "required": ["filename", "lines_of_text"],
              },
          }
      ],
      messages=[
          {
              "role": "user",
              "content": "Can you write a long poem and make a file called poem.txt?",
          }
      ],
  ) as stream:
      for event in stream:
          if event.type == "input_json":
              print(event.partial_json, end="", flush=True)
      final_message = stream.get_final_message()

  print()
  for block in final_message.content:
      if block.type == "tool_use":
          print(f"Complete tool input: {block.input}")

typescript TypeScript
  const client = new Anthropic();

  const stream = client.messages.stream({
    model: "claude-opus-5",
    max_tokens: 65536,
    tools: [
      {
        name: "make_file",
        description: "Write text to a file",
        eager_input_streaming: true,
        input_schema: {
          type: "object",
          properties: {
            filename: {
              type: "string",
              description: "The filename to write text to"
            },
            lines_of_text: {
              type: "array",
              description: "An array of lines of text to write to the file"
            }
          },
          required: ["filename", "lines_of_text"]
        }
      }
    ],
    messages: [
      {
        role: "user",
        content: "Can you write a long poem and make a file called poem.txt?"
      }
    ]
  });

  stream.on("inputJson", (partialJson) => {
    process.stdout.write(partialJson);
  });

  const message = await stream.finalMessage();
  console.log();
  for (const block of message.content) {
    if (block.type === "tool_use") {
      console.log("Complete tool input:", block.input);
    }
  }

csharp C#
  AnthropicClient client = new();

  MessageCreateParams parameters = new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 65536,
      Tools =
      [
          new Tool
          {
              Name = "make_file",
              Description = "Write text to a file",
              EagerInputStreaming = true,
              InputSchema = new InputSchema
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["filename"] = JsonSerializer.SerializeToElement(
                          new { type = "string", description = "The filename to write text to" }
                      ),
                      ["lines_of_text"] = JsonSerializer.SerializeToElement(
                          new { type = "array", description = "An array of lines of text to write to the file" }
                      ),
                  },
                  Required = ["filename", "lines_of_text"],
              },
          },
      ],
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = "Can you write a long poem and make a file called poem.txt?",
          },
      ],
  };

  // The C# example assembles the input itself: content block index -> accumulated JSON
  var toolInputs = new Dictionary<long, StringBuilder>();

  await foreach (var streamEvent in client.Messages.CreateStreaming(parameters))
  {
      if (
          streamEvent.TryPickContentBlockStart(out var start)
          && start.ContentBlock.TryPickToolUse(out _)
      )
      {
          toolInputs[start.Index] = new StringBuilder();
      }
      else if (
          streamEvent.TryPickContentBlockDelta(out var delta)
          && delta.Delta.TryPickInputJson(out var inputJson)
      )
      {
          Console.Write(inputJson.PartialJson);
          toolInputs[delta.Index].Append(inputJson.PartialJson);
      }
  }

  Console.WriteLine();
  foreach (var accumulatedInput in toolInputs.Values)
  {
      Console.WriteLine($"Complete tool input: {accumulatedInput}");
  }

go Go
  client := anthropic.NewClient()

  makeFileTool := anthropic.ToolParam{
  	Name:                "make_file",
  	Description:         anthropic.String("Write text to a file"),
  	EagerInputStreaming: anthropic.Bool(true),
  	InputSchema: anthropic.ToolInputSchemaParam{
  		Properties: map[string]any{
  			"filename": map[string]any{
  				"type":        "string",
  				"description": "The filename to write text to",
  			},
  			"lines_of_text": map[string]any{
  				"type":        "array",
  				"description": "An array of lines of text to write to the file",
  			},
  		},
  		Required: []string{"filename", "lines_of_text"},
  	},
  }

  stream := client.Messages.NewStreaming(context.Background(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 65536,
  	Tools:     []anthropic.ToolUnionParam{{OfTool: &makeFileTool}},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock(
  			"Can you write a long poem and make a file called poem.txt?",
  		)),
  	},
  })

  message := anthropic.Message{}
  for stream.Next() {
  	event := stream.Current()
  	if err := message.Accumulate(event); err != nil {
  		panic(err)
  	}
  	if delta, ok := event.AsAny().(anthropic.ContentBlockDeltaEvent); ok {
  		if inputJSON, ok := delta.Delta.AsAny().(anthropic.InputJSONDelta); ok {
  			fmt.Print(inputJSON.PartialJSON)
  		}
  	}
  }
  if err := stream.Err(); err != nil {
  	panic(err)
  }

  fmt.Println()
  for _, block := range message.Content {
  	if toolUse, ok := block.AsAny().(anthropic.ToolUseBlock); ok {
  		fmt.Printf("Complete tool input: %s\n", toolUse.Input)
  	}
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  Tool makeFileTool = Tool.builder()
      .name("make_file")
      .description("Write text to a file")
      .eagerInputStreaming(true)
      .inputSchema(Tool.InputSchema.builder()
          .properties(Tool.InputSchema.Properties.builder()
              .putAdditionalProperty("filename", JsonValue.from(Map.of(
                  "type", "string",
                  "description", "The filename to write text to")))
              .putAdditionalProperty("lines_of_text", JsonValue.from(Map.of(
                  "type", "array",
                  "description", "An array of lines of text to write to the file")))
              .build())
          .addRequired("filename")
          .addRequired("lines_of_text")
          .build())
      .build();

  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(65536L)
      .addTool(makeFileTool)
      .addUserMessage("Can you write a long poem and make a file called poem.txt?")
      .build();

  MessageAccumulator accumulator = MessageAccumulator.create();

  try (StreamResponse<RawMessageStreamEvent> streamResponse =
          client.messages().createStreaming(params)) {
      streamResponse.stream().forEach(event -> {
          accumulator.accumulate(event);
          if (event.isContentBlockDelta()) {
              var delta = event.asContentBlockDelta().delta();
              if (delta.isInputJson()) {
                  IO.print(delta.asInputJson().partialJson());
              }
          }
      });
  }

  IO.println("");
  accumulator.message().content().forEach(block ->
      block.toolUse().ifPresent(toolUse ->
          IO.println("Complete tool input: " + toolUse._input())));

php PHP
  use Anthropic\Client;
  use Anthropic\Messages\InputJSONDelta;
  use Anthropic\Messages\Model;
  use Anthropic\Messages\RawContentBlockDeltaEvent;
  use Anthropic\Messages\RawContentBlockStartEvent;
  use Anthropic\Messages\ToolUseBlock;

  $client = new Client();

  $stream = $client->messages->createStream(
      maxTokens: 65536,
      model: Model::CLAUDE_OPUS_5,
      tools: [
          [
              'name' => 'make_file',
              'description' => 'Write text to a file',
              'eager_input_streaming' => true,
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'filename' => [
                          'type' => 'string',
                          'description' => 'The filename to write text to',
                      ],
                      'lines_of_text' => [
                          'type' => 'array',
                          'description' => 'An array of lines of text to write to the file',
                      ],
                  ],
                  'required' => ['filename', 'lines_of_text'],
              ],
          ],
      ],
      messages: [
          [
              'role' => 'user',
              'content' => 'Can you write a long poem and make a file called poem.txt?',
          ],
      ],
  );

  // The PHP example assembles the input itself: index => accumulated JSON string
  $toolInputs = [];

  foreach ($stream as $event) {
      if (
          $event instanceof RawContentBlockStartEvent
          && $event->contentBlock instanceof ToolUseBlock
      ) {
          $toolInputs[$event->index] = '';
      } elseif (
          $event instanceof RawContentBlockDeltaEvent
          && $event->delta instanceof InputJSONDelta
      ) {
          echo $event->delta->partialJSON;
          $toolInputs[$event->index] .= $event->delta->partialJSON;
      }
  }

  echo "\n";
  foreach ($toolInputs as $toolInput) {
      echo "Complete tool input: {$toolInput}\n";
  }

ruby Ruby
  client = Anthropic::Client.new

  stream = client.messages.stream(
    model: Anthropic::Models::Model::CLAUDE_OPUS_5,
    max_tokens: 65_536,
    tools: [
      {
        name: "make_file",
        description: "Write text to a file",
        eager_input_streaming: true,
        input_schema: {
          type: "object",
          properties: {
            filename: {
              type: "string",
              description: "The filename to write text to"
            },
            lines_of_text: {
              type: "array",
              description: "An array of lines of text to write to the file"
            }
          },
          required: ["filename", "lines_of_text"]
        }
      }
    ],
    messages: [
      {
        role: "user",
        content: "Can you write a long poem and make a file called poem.txt?"
      }
    ]
  )

  stream.each do |event|
    print event.partial_json if event.is_a?(Anthropic::Streaming::InputJsonEvent)
  end

  puts
  stream.accumulated_message.content.each do |block|
    puts "Complete tool input: #{block.input}" if block.type == :tool_use
  end

text wrap
{"filename": "poem.txt", "lines_of_text": ["The Wanderer's Journey", "", "I.", "", "Beneath the vast and star-strewn sky,", "Where silver moonbeams softly lie,", ...
Complete tool input: {"filename": "poem.txt", "lines_of_text": ["The Wanderer's Journey", ...]}
```

Without `eager_input_streaming`, the API buffers and validates each parameter value before streaming it back, so nothing prints for a large parameter until Claude has finished generating it. With it, fragments start arriving as soon as Claude begins the parameter, and they are typically longer, with fewer mid-word breaks.


## Accumulating tool input deltas

Source: https://platform.claude.com/llms-full.txt#accumulating-tool-input-deltas

The accumulation contract is the same as for standard tool-use streaming, so this section applies with and without `eager_input_streaming`. See [Input JSON delta](https://platform.claude.com/docs/en/build-with-claude/streaming#input-json-delta) in Streaming messages for the event format. Fine-grained tool streaming changes what you can assume about the result: the server streams fragments without validating them, so the accumulated string might not be valid JSON.

When a `tool_use` content block streams, the initial `content_block_start` event contains `input: {}` (an empty object). This is a placeholder. The actual input arrives as a series of `input_json_delta` events, each carrying a `partial_json` string fragment. To assemble the full input, concatenate these fragments and parse the result when the block closes.

Where your SDK provides an accumulator helper (as the Python, TypeScript, Go, Java, and Ruby tabs in the previous example do), it handles this for you. The manual pattern is for SDKs without a helper, or when you want full control over how the input is assembled.

The accumulation contract:

1. On `content_block_start` with `type: "tool_use"`, initialize an empty string: `input_json = ""`
2. For each `content_block_delta` with `type: "input_json_delta"`, append: `input_json += event.delta.partial_json`
3. On `content_block_stop`, parse the accumulated string

Guard the parse, as the following SDK examples do. A response can also stop at `max_tokens` midway through a parameter. Check the [stop reason](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons) and decide whether to retry the request with a higher `max_tokens` or repair the partial input.

The type mismatch between the initial `input: {}` (object) and `partial_json` (string) is by design. The empty object marks the slot in the content array. The delta strings build the real value.

<CodeGroup>
  ```bash cURL
  # Accumulating per-block input deltas needs a programming language; the first
  # example's CLI tab shows the raw fragments with jq. See the SDK tabs.

bash CLI
  # Accumulating per-block input deltas needs a programming language; the first
  # example's CLI tab shows the raw fragments with jq. See the SDK tabs.

python Python
  client = anthropic.Anthropic()

  tool_inputs: dict[int, str] = {}  # index -> accumulated JSON string

  with client.messages.stream(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[
          {
              "name": "get_weather",
              "description": "Get current weather for a city",
              "eager_input_streaming": True,
              "input_schema": {
                  "type": "object",
                  "properties": {"city": {"type": "string"}},
                  "required": ["city"],
              },
          }
      ],
      messages=[{"role": "user", "content": "Weather in Paris?"}],
  ) as stream:
      for event in stream:
          match event.type:
              case "content_block_start" if event.content_block.type == "tool_use":
                  tool_inputs[event.index] = ""
              case "content_block_delta" if event.delta.type == "input_json_delta":
                  tool_inputs[event.index] += event.delta.partial_json
              case "content_block_stop" if event.index in tool_inputs:
                  raw_input = tool_inputs[event.index]
                  try:
                      parsed = json.loads(raw_input)
                  except json.JSONDecodeError:
                      # The accumulated string is not guaranteed to be valid JSON.
                      # See "Handling invalid JSON in tool responses" on this page.
                      print(f"Invalid tool input: {raw_input}")
                  else:
                      print(f"Tool input: {parsed}")

typescript TypeScript
  const client = new Anthropic();

  const toolInputs = new Map<number, string>();

  const stream = client.messages.stream({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        name: "get_weather",
        description: "Get current weather for a city",
        eager_input_streaming: true,
        input_schema: {
          type: "object",
          properties: { city: { type: "string" } },
          required: ["city"]
        }
      }
    ],
    messages: [{ role: "user", content: "Weather in Paris?" }]
  });

  for await (const event of stream) {
    if (event.type === "content_block_start" && event.content_block.type === "tool_use") {
      toolInputs.set(event.index, "");
    } else if (event.type === "content_block_delta" && event.delta.type === "input_json_delta") {
      toolInputs.set(
        event.index,
        (toolInputs.get(event.index) ?? "") + event.delta.partial_json
      );
    } else if (event.type === "content_block_stop" && toolInputs.has(event.index)) {
      const rawInput = toolInputs.get(event.index)!;
      try {
        console.log("Tool input:", JSON.parse(rawInput));
      } catch {
        // The accumulated string is not guaranteed to be valid JSON.
        // See "Handling invalid JSON in tool responses" on this page.
        console.log("Invalid tool input:", rawInput);
      }
    }
  }

csharp C#
  AnthropicClient client = new();

  MessageCreateParams parameters = new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools =
      [
          new Tool
          {
              Name = "get_weather",
              Description = "Get current weather for a city",
              EagerInputStreaming = true,
              InputSchema = new InputSchema
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["city"] = JsonSerializer.SerializeToElement(new { type = "string" }),
                  },
                  Required = ["city"],
              },
          },
      ],
      Messages = [new() { Role = Role.User, Content = "Weather in Paris?" }],
  };

  // Block index -> accumulated JSON fragments
  // This example accumulates the deltas manually to show the raw stream;
  // the SDK's MessageContentAggregator can also accumulate tool input automatically.
  var toolInputs = new Dictionary<long, StringBuilder>();

  await foreach (var streamEvent in client.Messages.CreateStreaming(parameters))
  {
      if (
          streamEvent.TryPickContentBlockStart(out var start)
          && start.ContentBlock.TryPickToolUse(out _)
      )
      {
          toolInputs[start.Index] = new StringBuilder();
      }
      else if (
          streamEvent.TryPickContentBlockDelta(out var delta)
          && delta.Delta.TryPickInputJson(out var inputJson)
      )
      {
          toolInputs[delta.Index].Append(inputJson.PartialJson);
      }
      else if (
          streamEvent.TryPickContentBlockStop(out var stop)
          && toolInputs.TryGetValue(stop.Index, out var accumulated)
      )
      {
          try
          {
              using var parsed = JsonDocument.Parse(accumulated.ToString());
              Console.WriteLine($"Tool input: {parsed.RootElement}");
          }
          catch (JsonException)
          {
              // The accumulated string is not guaranteed to be valid JSON.
              // See "Handling invalid JSON in tool responses" on this page.
              Console.WriteLine($"Invalid tool input: {accumulated}");
          }
      }
  }

go Go
  client := anthropic.NewClient()

  toolInputs := map[int64]string{} // content block index -> accumulated JSON

  stream := client.Messages.NewStreaming(context.Background(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{{
  		OfTool: &anthropic.ToolParam{
  			Name:                "get_weather",
  			Description:         anthropic.String("Get current weather for a city"),
  			EagerInputStreaming: anthropic.Bool(true),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"city": map[string]any{"type": "string"},
  				},
  				Required: []string{"city"},
  			},
  		},
  	}},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Weather in Paris?")),
  	},
  })

  for stream.Next() {
  	switch event := stream.Current().AsAny().(type) {
  	case anthropic.ContentBlockStartEvent:
  		if _, ok := event.ContentBlock.AsAny().(anthropic.ToolUseBlock); ok {
  			toolInputs[event.Index] = ""
  		}
  	case anthropic.ContentBlockDeltaEvent:
  		if delta, ok := event.Delta.AsAny().(anthropic.InputJSONDelta); ok {
  			toolInputs[event.Index] += delta.PartialJSON
  		}
  	case anthropic.ContentBlockStopEvent:
  		if accumulated, ok := toolInputs[event.Index]; ok {
  			var parsed map[string]any
  			if err := json.Unmarshal([]byte(accumulated), &parsed); err != nil {
  				// The accumulated string is not guaranteed to be valid JSON.
  				// See "Handling invalid JSON in tool responses" on this page.
  				fmt.Println("Invalid tool input:", accumulated)
  			} else {
  				fmt.Println("Tool input:", parsed)
  			}
  		}
  	}
  }
  if err := stream.Err(); err != nil {
  	panic(err)
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();
  ObjectMapper objectMapper = new ObjectMapper();

  Tool weatherTool = Tool.builder()
          .name("get_weather")
          .description("Get current weather for a city")
          .eagerInputStreaming(true)
          .inputSchema(Tool.InputSchema.builder()
                  .properties(Tool.InputSchema.Properties.builder()
                          .putAdditionalProperty("city", JsonValue.from(Map.of("type", "string")))
                          .build())
                  .addRequired("city")
                  .build())
          .build();

  MessageCreateParams createParams = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .addTool(weatherTool)
          .addUserMessage("Weather in Paris?")
          .build();

  // Content block index -> accumulated tool input JSON
  Map<Long, StringBuilder> toolInputs = new HashMap<>();

  try (StreamResponse<RawMessageStreamEvent> streamResponse = client.messages().createStreaming(createParams)) {
      var eventIterator = streamResponse.stream().iterator();
      while (eventIterator.hasNext()) {
          RawMessageStreamEvent event = eventIterator.next();
          if (event.isContentBlockStart()) {
              var blockStart = event.asContentBlockStart();
              if (blockStart.contentBlock().isToolUse()) {
                  toolInputs.put(blockStart.index(), new StringBuilder());
              }
          } else if (event.isContentBlockDelta()) {
              var blockDelta = event.asContentBlockDelta();
              if (blockDelta.delta().isInputJson() && toolInputs.containsKey(blockDelta.index())) {
                  toolInputs.get(blockDelta.index()).append(blockDelta.delta().asInputJson().partialJson());
              }
          } else if (event.isContentBlockStop()) {
              var blockStop = event.asContentBlockStop();
              if (toolInputs.containsKey(blockStop.index())) {
                  String accumulated = toolInputs.get(blockStop.index()).toString();
                  try {
                      IO.println("Tool input: " + objectMapper.readTree(accumulated));
                  } catch (JsonProcessingException e) {
                      // The accumulated string is not guaranteed to be valid JSON.
                      // See "Handling invalid JSON in tool responses" on this page.
                      IO.println("Invalid tool input: " + accumulated);
                  }
              }
          }
      }
  }

php PHP
  use Anthropic\Client;
  use Anthropic\Messages\InputJSONDelta;
  use Anthropic\Messages\Model;
  use Anthropic\Messages\RawContentBlockDeltaEvent;
  use Anthropic\Messages\RawContentBlockStartEvent;
  use Anthropic\Messages\RawContentBlockStopEvent;
  use Anthropic\Messages\ToolUseBlock;

  $client = new Client();

  // The PHP SDK does not provide a stream accumulator for tool input;
  // the manual pattern shown here is the supported approach.
  $toolInputs = []; // index => accumulated JSON string

  $stream = $client->messages->createStream(
      maxTokens: 1024,
      model: Model::CLAUDE_OPUS_5,
      tools: [
          [
              'name' => 'get_weather',
              'description' => 'Get current weather for a city',
              'eager_input_streaming' => true,
              'input_schema' => [
                  'type' => 'object',
                  'properties' => ['city' => ['type' => 'string']],
                  'required' => ['city'],
              ],
          ],
      ],
      messages: [['role' => 'user', 'content' => 'Weather in Paris?']],
  );

  foreach ($stream as $event) {
      if (
          $event instanceof RawContentBlockStartEvent
          && $event->contentBlock instanceof ToolUseBlock
      ) {
          $toolInputs[$event->index] = '';
      } elseif (
          $event instanceof RawContentBlockDeltaEvent
          && $event->delta instanceof InputJSONDelta
      ) {
          $toolInputs[$event->index] .= $event->delta->partialJSON;
      } elseif (
          $event instanceof RawContentBlockStopEvent
          && isset($toolInputs[$event->index])
      ) {
          $accumulated = $toolInputs[$event->index];
          try {
              $parsed = json_decode($accumulated, associative: true, flags: JSON_THROW_ON_ERROR);
              echo "Tool input: " . json_encode($parsed) . "\n";
          } catch (JsonException $e) {
              // The accumulated string is not guaranteed to be valid JSON.
              // See "Handling invalid JSON in tool responses" on this page.
              echo "Invalid tool input: {$accumulated}\n";
          }
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  tool_inputs = {} # index -> accumulated JSON string

  stream = client.messages.stream_raw(
    model: Anthropic::Models::Model::CLAUDE_OPUS_5,
    max_tokens: 1024,
    tools: [
      {
        name: "get_weather",
        description: "Get current weather for a city",
        eager_input_streaming: true,
        input_schema: {
          type: "object",
          properties: {city: {type: "string"}},
          required: ["city"]
        }
      }
    ],
    messages: [{role: "user", content: "Weather in Paris?"}]
  )

  stream.each do |event|
    case event
    when Anthropic::Models::RawContentBlockStartEvent
      tool_inputs[event.index] = +"" if event.content_block.type == :tool_use
    when Anthropic::Models::RawContentBlockDeltaEvent
      if event.delta.is_a?(Anthropic::Models::InputJSONDelta)
        tool_inputs[event.index] << event.delta.partial_json
      end
    when Anthropic::Models::RawContentBlockStopEvent
      if tool_inputs.key?(event.index)
        accumulated = tool_inputs[event.index]
        begin
          parsed = JSON.parse(accumulated)
          puts "Tool input: #{parsed}"
        rescue JSON::ParserError
          # The accumulated string is not guaranteed to be valid JSON.
          # See "Handling invalid JSON in tool responses" on this page.
          puts "Invalid tool input: #{accumulated}"
        end
      end
    end
  end
  ```
</CodeGroup>

<Tip>
  Reacting to fragments and assembling them are separate concerns. The first example reacts to each fragment as it arrives and still hands assembly to the SDK in the tabs that use an accumulator helper. Use the manual pattern when you are not using an accumulator helper or when you want full control over assembly.
</Tip>


## Handling invalid JSON in tool responses

Source: https://platform.claude.com/llms-full.txt#handling-invalid-json-in-tool-responses

With fine-grained tool streaming, the accumulated input for a tool call might be invalid or incomplete JSON. When it is, you cannot run the tool, so report the failure back to Claude instead. The `content` of a tool result does not have to be JSON, but wrapping the raw string in a JSON object under a single key makes it unambiguous to Claude that you received invalid JSON, and preserves the original input for debugging:

Return the wrapper, serialized to a string, as the `content` of a [tool result](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls#handling-errors-with-is-error) content block with `is_error` set to `true`:

<Note>
  Build the wrapper with your JSON library rather than by concatenating strings, so quotes and other special characters in the invalid input are escaped correctly.
</Note>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-43

<CardGroup cols={2}>
  <Card title="Context windows" icon="stack" href="https://platform.claude.com/docs/en/build-with-claude/context-windows">
    Understand how the context window works, how extended thinking and tool use count toward it, and how to manage context as conversations grow.
  </Card>

  <Card title="Streaming messages" icon="lightning" href="https://platform.claude.com/docs/en/build-with-claude/streaming">
    Stream Messages API responses incrementally with server-sent events, including text, tool use, and extended thinking deltas.
  </Card>

  <Card title="Handle tool calls" icon="arrows-left-right" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls">
    Parse tool\_use blocks, format tool\_result responses, and handle errors with is\_error.
  </Card>

  <Card title="Tool reference" icon="book" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference">
    Directory of Anthropic-provided tools and reference for optional tool definition properties.
  </Card>
</CardGroup>


---
title: Manage tool context
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/manage-tool-context
description: Choose between tool search, programmatic tool calling, prompt caching, and context editing to manage context bloat.
---

Tool definitions and accumulated `tool_result` blocks consume your context window. Long-running agents with many tools or many turns can exhaust available context before the task is finished. Four approaches address this at different points in the pipeline.


## The four approaches

Source: https://platform.claude.com/llms-full.txt#the-four-approaches

Each approach targets a different source of context pressure. Pick the one that matches where your tokens are going.

| Approach                  | What it reduces                         | When it fits                                                         | Learn more                                                                                                                 |
| ------------------------- | --------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Tool search               | Tool definitions loaded upfront         | Large toolsets (20+ tools) where most tools aren't needed every turn | [Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)                         |
| Programmatic tool calling | `tool_result` roundtrips                | Chains of tool calls that can execute as a single script             | [Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)       |
| Prompt caching            | Token cost of repeated tool definitions | Stable toolsets across many requests                                 | [Tool use with prompt caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching) |
| Context editing           | Old `tool_result` blocks in history     | Long conversations where early results are no longer relevant        | [Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing)                                   |

### Tool search

Tool search keeps tool definitions out of the context window until Claude asks for them. Instead of sending 50 tool schemas upfront, you send a single `tool_search` tool and let Claude discover the rest on demand. This trades a small amount of latency (one extra turn to look up a tool) for a large reduction in baseline context usage.

### Programmatic tool calling

Programmatic tool calling collapses a sequence of tool calls into a single code block that Claude writes and Anthropic's code execution sandbox runs. Rather than five roundtrips of `tool_use` and `tool_result`, Claude emits one script that calls all five functions from within the sandbox. The intermediate results never enter the conversation history.

### Prompt caching

Prompt caching doesn't reduce the number of tokens in context, but it reduces what you pay for them on subsequent requests. If your tool definitions are stable, cache them once and reuse the cached prefix across thousands of requests. This is the right choice when the toolset is large but fixed.

### Context editing

Context editing removes old `tool_result` blocks from the conversation history once they've served their purpose. A long agent loop might produce hundreds of intermediate results that were useful at the time but are now dead weight. Context editing lets you trim them without restarting the conversation.


## Combining approaches

Source: https://platform.claude.com/llms-full.txt#combining-approaches

These approaches compose. A long-running agent might use tool search to keep the toolset lean, prompt caching to amortize the cost of the remaining definitions, and context editing to trim stale results as the conversation grows. Each solves a different part of the problem, so there's no conflict in using them together.

A reasonable starting point for a high-volume agent:

1. Enable prompt caching on your tool definitions from day one. Cache writes carry a 25% markup over base input pricing, which pays back on the second request that hits the cache.
2. Add tool search once your toolset grows past roughly 20 tools or your baseline context usage becomes noticeable.
3. Add context editing once individual conversations start running long enough that early results become irrelevant.
4. Consider programmatic tool calling if you notice repetitive chains of small tool calls that could run as a single batch.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-44

<CardGroup cols={2}>
  <Card title="Tool search tool" icon="magnifying-glass" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool">
    Load tool definitions on demand instead of upfront.
  </Card>

  <Card title="Programmatic tool calling" icon="code" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling">
    Collapse tool-call chains into a single executable script.
  </Card>

  <Card title="Tool use with prompt caching" icon="database" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching">
    Cache tool definitions across requests to cut token costs.
  </Card>

  <Card title="Context editing" icon="scissors" href="https://platform.claude.com/docs/en/build-with-claude/context-editing">
    Trim stale tool results from long-running conversations.
  </Card>
</CardGroup>


---
title: Programmatic tool calling
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling
description: Let Claude call your tools from code in the code execution container, cutting model round trips and token use in multi-tool workflows.
---


## Compatibility

Source: https://platform.claude.com/llms-full.txt#compatibility-8

- [ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): not eligible
- Supported models: `claude-fable-5-1`, `claude-mythos-5-1`, `claude-fable-5`, `claude-mythos-5`, `claude-opus-5`, `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`, `claude-opus-4-5-20251101`, `claude-sonnet-5`, `claude-sonnet-4-6`, `claude-sonnet-4-5-20250929`
- Platforms: Claude API, Claude Platform on AWS, Microsoft Foundry [1]; not available on Amazon Bedrock, Google Cloud
- Programmatic tool calling requires the code execution tool with the `code_execution_20260120` or later [tool version](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#tool-versions).
- Claude Haiku 4.5 accepts the `code_execution_20260120` and later tool versions but doesn't support programmatic tool calling.
1. On [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), programmatic tool calling requires a [Hosted on Anthropic deployment](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#additional-features-not-supported-when-hosted-on-azure).

Programmatic tool calling allows Claude to write code that calls your tools programmatically within a [code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) container, rather than requiring round trips through the model for each tool invocation. This reduces latency for multi-tool workflows and decreases token consumption by allowing Claude to filter or process data before it reaches the model's context window. On agentic search benchmarks like [BrowseComp](https://arxiv.org/abs/2504.12516) and [DeepSearchQA](https://github.com/google-deepmind/deepsearchqa), which test multistep web research and complex information retrieval, adding programmatic tool calling on top of basic search tools improved performance by an average of 11% while using 24% fewer input tokens (see [Improved web search with dynamic filtering](https://claude.com/blog/improved-web-search-with-dynamic-filtering)).

Consider checking budget compliance across 20 employees: the traditional approach requires 20 separate model round-trips, pulling thousands of expense line items into the context along the way. With programmatic tool calling, a single script runs all 20 lookups, filters the results, and returns only the employees who exceeded their limits, shrinking what Claude needs to reason over from hundreds of kilobytes down to a handful of lines.

<Tip>
  For a deeper look at the inference and context costs that programmatic tool calling addresses, see [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use).
</Tip>

Programmatic tool calling requires the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) with tool version `code_execution_20260120` or later.


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-8

Here's an example where Claude programmatically queries a database multiple times and aggregates results. Adding `allowed_callers: ["code_execution_20260120"]` to a tool definition is what makes that tool callable from within code execution (see [The `allowed_callers` field](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#the-allowed-callers-field)):

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --data '{
          "model": "claude-opus-5",
          "max_tokens": 4096,
          "messages": [
              {
                  "role": "user",
                  "content": "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue"
              }
          ],
          "tools": [
              {
                  "type": "code_execution_20260120",
                  "name": "code_execution"
              },
              {
                  "name": "query_database",
                  "description": "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
                  "input_schema": {
                      "type": "object",
                      "properties": {
                          "sql": {
                              "type": "string",
                              "description": "SQL query to execute"
                          }
                      },
                      "required": ["sql"]
                  },
                  "allowed_callers": ["code_execution_20260120"]
              }
          ]
      }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: >-
        Query sales data for the West, East, and Central regions, then
        tell me which region had the highest revenue
  tools:
    - type: code_execution_20260120
      name: code_execution
    - name: query_database
      description: >-
        Execute a SQL query against the sales database. Returns a list
        of rows as JSON objects.
      input_schema:
        type: object
        properties:
          sql:
            type: string
            description: SQL query to execute
        required:
          - sql
      allowed_callers:
        - code_execution_20260120
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue",
          }
      ],
      tools=[
          {"type": "code_execution_20260120", "name": "code_execution"},
          {
              "name": "query_database",
              "description": "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "sql": {"type": "string", "description": "SQL query to execute"}
                  },
                  "required": ["sql"],
              },
              "allowed_callers": ["code_execution_20260120"],
          },
      ],
  )

  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content:
          "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue"
      }
    ],
    tools: [
      {
        type: "code_execution_20260120",
        name: "code_execution"
      },
      {
        name: "query_database",
        description:
          "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
        input_schema: {
          type: "object" as const,
          properties: {
            sql: {
              type: "string",
              description: "SQL query to execute"
            }
          },
          required: ["sql"]
        },
        allowed_callers: ["code_execution_20260120"]
      }
    ]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 4096,
      Messages = [
          new() {
              Role = Role.User,
              Content = "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue"
          }
      ],
      Tools = [
          new CodeExecutionTool20260120(),
          new ToolUnion(new Tool()
          {
              Name = "query_database",
              Description = "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
              InputSchema = new InputSchema()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["sql"] = JsonSerializer.SerializeToElement(new { type = "string", description = "SQL query to execute" }),
                  },
                  Required = ["sql"],
              },
              AllowedCallers = ["code_execution_20260120"]
          }),
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20260120: &anthropic.CodeExecutionTool20260120Param{}},
  		{OfTool: &anthropic.ToolParam{
  			Name:        "query_database",
  			Description: anthropic.String("Execute a SQL query against the sales database. Returns a list of rows as JSON objects."),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"sql": map[string]any{
  						"type":        "string",
  						"description": "SQL query to execute",
  					},
  				},
  				Required: []string{"sql"},
  			},
  			AllowedCallers: []string{"code_execution_20260120"},
  		}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  import com.anthropic.models.messages.CodeExecutionTool20260120;
  // ...

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .addUserMessage("Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue")
          .addTool(CodeExecutionTool20260120.builder().build())
          .addTool(Tool.builder()
              .name("query_database")
              .description("Execute a SQL query against the sales database. Returns a list of rows as JSON objects.")
              .inputSchema(InputSchema.builder()
                  .properties(JsonValue.from(Map.of(
                      "sql", Map.of(
                          "type", "string",
                          "description", "SQL query to execute"
                      )
                  )))
                  .putAdditionalProperty("required", JsonValue.from(List.of("sql")))
                  .build())
              .allowedCallers(List.of(Tool.AllowedCaller.of("code_execution_20260120")))
              .build())
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue'],
      ],
      model: 'claude-opus-5',
      tools: [
          [
              'type' => 'code_execution_20260120',
              'name' => 'code_execution',
          ],
          [
              'name' => 'query_database',
              'description' => 'Execute a SQL query against the sales database. Returns a list of rows as JSON objects.',
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'sql' => [
                          'type' => 'string',
                          'description' => 'SQL query to execute',
                      ],
                  ],
                  'required' => ['sql'],
              ],
              'allowed_callers' => ['code_execution_20260120'],
          ],
      ],
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue"
      }
    ],
    tools: [
      {
        type: "code_execution_20260120",
        name: "code_execution"
      },
      {
        name: "query_database",
        description: "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
        input_schema: {
          type: "object",
          properties: {
            sql: {
              type: "string",
              description: "SQL query to execute"
            }
          },
          required: ["sql"]
        },
        allowed_callers: ["code_execution_20260120"]
      }
    ]
  )

  puts message
  ```
</CodeGroup>

The response stops with `stop_reason: "tool_use"`, a `container` ID, and a `tool_use` block for `query_database` whose `caller` field identifies the code execution run that called it. Return the result as shown in [Step 3 of the example workflow](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#step-3-provide-tool-result) so the code can finish.


## How programmatic tool calling works

Source: https://platform.claude.com/llms-full.txt#how-programmatic-tool-calling-works

When you configure a tool to be callable from code execution and Claude determines that tool is needed:

1. Claude writes Python code that invokes the tool as a function, potentially including multiple tool calls and pre/post-processing logic
2. Claude runs this code in a sandboxed container through code execution
3. When a tool function is called, code execution pauses and the API returns a `tool_use` block
4. You provide the tool result, and code execution continues (intermediate results are not loaded into Claude's context window)
5. Once all code execution completes, Claude receives the final output and continues working on the task

This approach is particularly useful for:

* **Large data processing:** Filter or aggregate tool results before they reach Claude's context
* **Multistep workflows:** Save tokens and latency by calling tools serially or in a loop without sampling Claude in-between tool calls
* **Conditional logic:** Make decisions based on intermediate tool results

<Note>
  Tools that allow a code execution caller are exposed to Claude's code as async Python functions, so Claude can run them in parallel with `asyncio.gather`. Each function takes a single dict of arguments and returns a string: the text of the `tool_result` you send back. Claude's code awaits these functions with top-level `await` and parses results that it needs as structured data, for example `rows = json.loads(await query_database({"sql": "<sql>"}))`.
</Note>


## Core concepts

Source: https://platform.claude.com/llms-full.txt#core-concepts

### The `allowed_callers` field

The `allowed_callers` field specifies which contexts can invoke a tool:

**Possible values:**

* `["direct"]` - Claude is guided to call this tool directly (default if omitted)
* `["code_execution_20260120"]` - Claude is guided to call this tool only from within code execution
* `["direct", "code_execution_20260120"]` - Claude may call this tool directly or from within code execution

Both `"code_execution_20260120"` and `"code_execution_20260521"` are accepted in `allowed_callers` and are interchangeable: a request using either code-execution tool version satisfies tools that list either caller. Response blocks always tag the caller as `code_execution_20260120` regardless of which version the request declared.

<Tip>
  Choose either `["direct"]` or `["code_execution_20260120"]` for each tool rather than enabling both, as this provides clearer guidance to Claude for how best to use the tool.
</Tip>

<Note>
  `allowed_callers` controls how the tool is presented to Claude and is validated against `tool_choice`, but it is not a hard API-level block on direct invocation. Claude is strongly guided to respect it, but your client should still be prepared to handle a direct `tool_use` for any tool it defines. Do not rely on `allowed_callers` as a security boundary.
</Note>

### The `caller` field in responses

Every tool use block includes a `caller` field indicating how it was invoked:

**Direct invocation (traditional tool use):**

**Programmatic invocation:**

The `tool_id` is the `id` of the code execution `server_tool_use` block that made the call, so you can match each programmatic `tool_use` to the code execution run that produced it.

### Container lifecycle

Programmatic tool calling uses the same containers as code execution:

* **Container creation:** A new container is created for each request unless you reuse an existing one
* **Container ID:** Returned in responses in the `container` field, along with an `expires_at` timestamp
* **Reuse:** Pass the container ID back on the next request to keep state. While a programmatic tool call is waiting for your result, the container ID is required on that request, not optional: the API rejects the request without it.
* **Expiration:** `expires_at` tells you how long the container has left. Idle containers are currently reclaimed after about 5 minutes, and no container can be reused more than 30 days after it was created.

<Warning>
  While Claude's code is waiting for a programmatic tool result, the pending call times out after about 4 minutes and raises a `TimeoutError` inside the code. Return each tool result well before the `expires_at` timestamp on the paused response. See [Container expiration during tool call](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#container-expiration-during-tool-call).
</Warning>


## Example workflow

Source: https://platform.claude.com/llms-full.txt#example-workflow

Here's how a complete programmatic tool calling flow works:

### Step 1: Initial request

Send a request with code execution and a tool that allows programmatic calling. To enable programmatic calling, add the `allowed_callers` field to your tool definition.

<Note>
  Provide detailed descriptions of your tool's output format in the tool description. If you specify that the tool returns JSON, Claude attempts to deserialize and process the result in code. The more detail you provide about the output schema, the better Claude can handle the response programmatically.
</Note>

The request shape is identical to the [Quick start](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#quick-start) example: include `code_execution` in your tools list, add `allowed_callers: ["code_execution_20260120"]` to any tool you want Claude to invoke from code, and send your user message. The remaining steps in this workflow use the user message `"Query customer purchase history from the last quarter and identify our top 5 customers by revenue"`.

### Step 2: API response with tool call

Claude writes code that calls your tool. The API pauses and returns:

```json Output
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "I'll query the purchase history and analyze the results."
    },
    {
      "type": "server_tool_use",
      "id": "srvtoolu_abc123",
      "name": "code_execution",
      "input": {
        "code": "import json\n\nrows = json.loads(await query_database({'sql': '<sql>'}))\ntop_customers = sorted(rows, key=lambda x: x['revenue'], reverse=True)[:5]\nprint(f'Top 5 customers: {top_customers}')"
      }
    },
    {
      "type": "tool_use",
      "id": "toolu_def456",
      "name": "query_database",
      "input": { "sql": "<sql>" },
      "caller": {
        "type": "code_execution_20260120",
        "tool_id": "srvtoolu_abc123"
      }
    }
  ],
  "container": {
    "id": "container_xyz789",
    "expires_at": "2026-01-20T14:30:00Z"
  },
  "stop_reason": "tool_use"
}

bash cURL
  curl https://api.anthropic.com/v1/messages \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --data '{
          "model": "claude-opus-5",
          "max_tokens": 4096,
          "container": "container_xyz789",
          "messages": [
              {
                  "role": "user",
                  "content": "Query customer purchase history from the last quarter and identify our top 5 customers by revenue"
              },
              {
                  "role": "assistant",
                  "content": [
                      {
                          "type": "text",
                          "text": "I'\''ll query the purchase history and analyze the results."
                      },
                      {
                          "type": "server_tool_use",
                          "id": "srvtoolu_abc123",
                          "name": "code_execution",
                          "input": {"code": "..."}
                      },
                      {
                          "type": "tool_use",
                          "id": "toolu_def456",
                          "name": "query_database",
                          "input": {"sql": "<sql>"},
                          "caller": {
                              "type": "code_execution_20260120",
                              "tool_id": "srvtoolu_abc123"
                          }
                      }
                  ]
              },
              {
                  "role": "user",
                  "content": [
                      {
                          "type": "tool_result",
                          "tool_use_id": "toolu_def456",
                          "content": "[{\"customer_id\": \"C1\", \"revenue\": 45000}, {\"customer_id\": \"C2\", \"revenue\": 38000}]"
                      }
                  ]
              }
          ],
          "tools": [
              {
                  "type": "code_execution_20260120",
                  "name": "code_execution"
              },
              {
                  "name": "query_database",
                  "description": "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
                  "input_schema": {
                      "type": "object",
                      "properties": {
                          "sql": {
                              "type": "string",
                              "description": "SQL query to execute"
                          }
                      },
                      "required": ["sql"]
                  },
                  "allowed_callers": ["code_execution_20260120"]
              }
          ]
      }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  container: container_xyz789
  messages:
    - role: user
      content: >-
        Query customer purchase history from the last quarter and identify our
        top 5 customers by revenue
    - role: assistant
      content:
        - type: text
          text: I'll query the purchase history and analyze the results.
        - type: server_tool_use
          id: srvtoolu_abc123
          name: code_execution
          input:
            code: "..."
        - type: tool_use
          id: toolu_def456
          name: query_database
          input:
            sql: "<sql>"
          caller:
            type: code_execution_20260120
            tool_id: srvtoolu_abc123
    - role: user
      content:
        - type: tool_result
          tool_use_id: toolu_def456
          content: >-
            [{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2",
            "revenue": 38000}, ...]
  # Same tools array as the original request
  tools:
    - type: code_execution_20260120
      name: code_execution
    - name: query_database
      description: >-
        Execute a SQL query against the sales database. Returns a list
        of rows as JSON objects.
      input_schema:
        type: object
        properties:
          sql:
            type: string
            description: SQL query to execute
        required:
          - sql
      allowed_callers:
        - code_execution_20260120
  YAML

python Python
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container="container_xyz789",  # Reuse the container
      messages=[
          {
              "role": "user",
              "content": "Query customer purchase history from the last quarter and identify our top 5 customers by revenue",
          },
          {
              "role": "assistant",
              "content": [
                  {
                      "type": "text",
                      "text": "I'll query the purchase history and analyze the results.",
                  },
                  {
                      "type": "server_tool_use",
                      "id": "srvtoolu_abc123",
                      "name": "code_execution",
                      "input": {"code": "..."},
                  },
                  {
                      "type": "tool_use",
                      "id": "toolu_def456",
                      "name": "query_database",
                      "input": {"sql": "<sql>"},
                      "caller": {
                          "type": "code_execution_20260120",
                          "tool_id": "srvtoolu_abc123",
                      },
                  },
              ],
          },
          {
              "role": "user",
              "content": [
                  {
                      "type": "tool_result",
                      "tool_use_id": "toolu_def456",
                      "content": '[{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2", "revenue": 38000}, ...]',
                  }
              ],
          },
      ],
      # Same tools array as the original request
      tools=[
          {"type": "code_execution_20260120", "name": "code_execution"},
          {
              "name": "query_database",
              "description": "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "sql": {"type": "string", "description": "SQL query to execute"}
                  },
                  "required": ["sql"],
              },
              "allowed_callers": ["code_execution_20260120"],
          },
      ],
  )

  print(response)

typescript TypeScript
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: "container_xyz789", // Reuse the container
    messages: [
      {
        role: "user",
        content:
          "Query customer purchase history from the last quarter and identify our top 5 customers by revenue"
      },
      {
        role: "assistant",
        content: [
          { type: "text", text: "I'll query the purchase history and analyze the results." },
          {
            type: "server_tool_use",
            id: "srvtoolu_abc123",
            name: "code_execution",
            input: { code: "..." }
          },
          {
            type: "tool_use",
            id: "toolu_def456",
            name: "query_database",
            input: { sql: "<sql>" },
            caller: {
              type: "code_execution_20260120",
              tool_id: "srvtoolu_abc123"
            }
          }
        ]
      },
      {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: "toolu_def456",
            content:
              '[{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2", "revenue": 38000}, ...]'
          }
        ]
      }
    ],
    // Same tools array as the original request
    tools: [
      {
        type: "code_execution_20260120",
        name: "code_execution"
      },
      {
        name: "query_database",
        description:
          "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
        input_schema: {
          type: "object" as const,
          properties: {
            sql: {
              type: "string",
              description: "SQL query to execute"
            }
          },
          required: ["sql"]
        },
        allowed_callers: ["code_execution_20260120"]
      }
    ]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 4096,
      Container = "container_xyz789",
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = "Query customer purchase history from the last quarter and identify our top 5 customers by revenue"
          },
          new()
          {
              Role = Role.Assistant,
              Content = new ContentBlock[]
              {
                  new TextBlock { Text = "I'll query the purchase history and analyze the results." },
                  new ServerToolUseBlock
                  {
                      Id = "srvtoolu_abc123",
                      Name = "code_execution",
                      Input = new { code = "..." }
                  },
                  new ToolUseBlock
                  {
                      Id = "toolu_def456",
                      Name = "query_database",
                      Input = new { sql = "<sql>" },
                      Caller = new ToolCaller
                      {
                          Type = "code_execution_20260120",
                          ToolId = "srvtoolu_abc123"
                      }
                  }
              }
          },
          new()
          {
              Role = Role.User,
              Content = new ContentBlockParam[]
              {
                  new ToolResultBlockParam
                  {
                      ToolUseID = "toolu_def456",
                      Content = "[{\"customer_id\": \"C1\", \"revenue\": 45000}, {\"customer_id\": \"C2\", \"revenue\": 38000}, ...]"
                  }
              }
          }
      ],
      // Same tools array as the original request
      Tools = [
          new CodeExecutionTool20260120(),
          new ToolUnion(new Tool()
          {
              Name = "query_database",
              Description = "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
              InputSchema = new InputSchema()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["sql"] = JsonSerializer.SerializeToElement(new { type = "string", description = "SQL query to execute" }),
                  },
                  Required = ["sql"],
              },
              AllowedCallers = ["code_execution_20260120"]
          }),
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfString: anthropic.String("container_xyz789"),
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Query customer purchase history from the last quarter and identify our top 5 customers by revenue")),
  		{
  			Role: anthropic.MessageParamRoleAssistant,
  			Content: []anthropic.ContentBlockParamUnion{
  				anthropic.NewTextBlock("I'll query the purchase history and analyze the results."),
  				{OfServerToolUse: &anthropic.ServerToolUseBlockParam{
  					ID:    "srvtoolu_abc123",
  					Name:  anthropic.ServerToolUseBlockParamNameCodeExecution,
  					Input: map[string]any{"code": "..."},
  				}},
  				{OfToolUse: &anthropic.ToolUseBlockParam{
  					ID:    "toolu_def456",
  					Name:  "query_database",
  					Input: map[string]any{"sql": "<sql>"},
  					Caller: anthropic.ServerToolUseBlockParamCallerUnion{
  						OfCodeExecution20260120: &anthropic.ServerToolCaller20260120Param{
  							ToolID: "srvtoolu_abc123",
  						},
  					},
  				}},
  			},
  		},
  		{
  			Role: anthropic.MessageParamRoleUser,
  			Content: []anthropic.ContentBlockParamUnion{
  				{OfToolResult: &anthropic.ToolResultBlockParam{
  					ToolUseID: "toolu_def456",
  					Content: []anthropic.ToolResultBlockParamContentUnion{
  						{OfText: &anthropic.TextBlockParam{
  							Text: `[{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2", "revenue": 38000}, ...]`,
  						}},
  					},
  				}},
  			},
  		},
  	},
  	// Same tools array as the original request
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20260120: &anthropic.CodeExecutionTool20260120Param{}},
  		{OfTool: &anthropic.ToolParam{
  			Name:        "query_database",
  			Description: anthropic.String("Execute a SQL query against the sales database. Returns a list of rows as JSON objects."),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"sql": map[string]any{
  						"type":        "string",
  						"description": "SQL query to execute",
  					},
  				},
  				Required: []string{"sql"},
  			},
  			AllowedCallers: []string{"code_execution_20260120"},
  		}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  import com.anthropic.models.messages.CodeExecutionTool20260120;
  // ...

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .container("container_xyz789")
          .addUserMessage("Query customer purchase history from the last quarter and identify our top 5 customers by revenue")
          .addAssistantMessageOfBlockParams(List.of(
              ContentBlockParam.ofText(
                  TextBlockParam.builder()
                      .text("I'll query the purchase history and analyze the results.")
                      .build()),
              ContentBlockParam.ofServerToolUse(
                  ServerToolUseBlockParam.builder()
                      .id("srvtoolu_abc123")
                      .name("code_execution")
                      .input(JsonValue.from(Map.of("code", "...")))
                      .build()),
              ContentBlockParam.ofToolUse(
                  ToolUseBlockParam.builder()
                      .id("toolu_def456")
                      .name("query_database")
                      .input(JsonValue.from(Map.of("sql", "<sql>")))
                      .codeExecution20260120Caller("srvtoolu_abc123")
                      .build())
          ))
          .addUserMessageOfBlockParams(List.of(
              ContentBlockParam.ofToolResult(
                  ToolResultBlockParam.builder()
                      .toolUseId("toolu_def456")
                      .content("[{\"customer_id\": \"C1\", \"revenue\": 45000}, {\"customer_id\": \"C2\", \"revenue\": 38000}, ...]")
                      .build())
          ))
          // Same tools array as the original request
          .addTool(CodeExecutionTool20260120.builder().build())
          .addTool(Tool.builder()
              .name("query_database")
              .description("Execute a SQL query against the sales database. Returns a list of rows as JSON objects.")
              .inputSchema(InputSchema.builder()
                  .properties(JsonValue.from(Map.of(
                      "sql", Map.of(
                          "type", "string",
                          "description", "SQL query to execute"
                      )
                  )))
                  .putAdditionalProperty("required", JsonValue.from(List.of("sql")))
                  .build())
              .allowedCallers(List.of(Tool.AllowedCaller.of("code_execution_20260120")))
              .build())
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          [
              'role' => 'user',
              'content' => 'Query customer purchase history from the last quarter and identify our top 5 customers by revenue',
          ],
          [
              'role' => 'assistant',
              'content' => [
                  [
                      'type' => 'text',
                      'text' => "I'll query the purchase history and analyze the results.",
                  ],
                  [
                      'type' => 'server_tool_use',
                      'id' => 'srvtoolu_abc123',
                      'name' => 'code_execution',
                      'input' => ['code' => '...'],
                  ],
                  [
                      'type' => 'tool_use',
                      'id' => 'toolu_def456',
                      'name' => 'query_database',
                      'input' => ['sql' => '<sql>'],
                      'caller' => [
                          'type' => 'code_execution_20260120',
                          'tool_id' => 'srvtoolu_abc123',
                      ],
                  ],
              ],
          ],
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'tool_result',
                      'tool_use_id' => 'toolu_def456',
                      'content' => '[{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2", "revenue": 38000}, ...]',
                  ],
              ],
          ],
      ],
      model: 'claude-opus-5',
      container: 'container_xyz789',
      // Same tools array as the original request
      tools: [
          [
              'type' => 'code_execution_20260120',
              'name' => 'code_execution',
          ],
          [
              'name' => 'query_database',
              'description' => 'Execute a SQL query against the sales database. Returns a list of rows as JSON objects.',
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'sql' => [
                          'type' => 'string',
                          'description' => 'SQL query to execute',
                      ],
                  ],
                  'required' => ['sql'],
              ],
              'allowed_callers' => ['code_execution_20260120'],
          ],
      ],
  );

  echo $message;

ruby Ruby
  require "anthropic"

  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: "container_xyz789",
    messages: [
      {
        role: "user",
        content: "Query customer purchase history from the last quarter and identify our top 5 customers by revenue"
      },
      {
        role: "assistant",
        content: [
          {
            type: "text",
            text: "I'll query the purchase history and analyze the results."
          },
          {
            type: "server_tool_use",
            id: "srvtoolu_abc123",
            name: "code_execution",
            input: { code: "..." }
          },
          {
            type: "tool_use",
            id: "toolu_def456",
            name: "query_database",
            input: { sql: "<sql>" },
            caller: {
              type: "code_execution_20260120",
              tool_id: "srvtoolu_abc123"
            }
          }
        ]
      },
      {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: "toolu_def456",
            content: '[{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2", "revenue": 38000}, ...]'
          }
        ]
      }
    ],
    # Same tools array as the original request
    tools: [
      {
        type: "code_execution_20260120",
        name: "code_execution"
      },
      {
        name: "query_database",
        description: "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
        input_schema: {
          type: "object",
          properties: {
            sql: {
              type: "string",
              description: "SQL query to execute"
            }
          },
          required: ["sql"]
        },
        allowed_callers: ["code_execution_20260120"]
      }
    ]
  )

  puts message

json Output
{
  "content": [
    {
      "type": "code_execution_tool_result",
      "tool_use_id": "srvtoolu_abc123",
      "content": {
        "type": "code_execution_result",
        "stdout": "Top 5 customers: [{'customer_id': 'C1', 'revenue': 45000}, {'customer_id': 'C2', 'revenue': 38000}, {'customer_id': 'C5', 'revenue': 32000}, {'customer_id': 'C8', 'revenue': 28500}, {'customer_id': 'C3', 'revenue': 24000}]",
        "stderr": "",
        "return_code": 0,
        "content": []
      }
    },
    {
      "type": "text",
      "text": "I've analyzed the purchase history from last quarter. Your top 5 customers generated $167,500 in total revenue, with Customer C1 leading at $45,000."
    }
  ],
  "stop_reason": "end_turn"
}
```


## Advanced patterns

Source: https://platform.claude.com/llms-full.txt#advanced-patterns

### Batch processing with loops

Claude can write code that processes multiple items efficiently:

This pattern:

* Reduces model round-trips from N (one per region) to 1
* Processes large result sets programmatically before returning to Claude
* Saves tokens by only returning aggregated conclusions instead of raw data

### Early termination

Claude can stop processing as soon as success criteria are met:

### Conditional tool selection

### Data filtering


## Response format

Source: https://platform.claude.com/llms-full.txt#response-format-3

### Programmatic tool call

When code execution calls a tool:

### Tool result handling

Your tool result is passed back to the running code:

### Code execution completion

When all tool calls are satisfied and code completes:


## Error handling

Source: https://platform.claude.com/llms-full.txt#error-handling-3

### Common errors

| Error                                      | Where it appears                                                             | Description                                                                    | Solution                                                                                                                         |
| ------------------------------------------ | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| `invalid_tool_input`                       | `error_code` on the `code_execution_tool_result` error block in the response | Invalid parameters were passed to the code execution tool                      | See the [code execution tool errors](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#errors)   |
| `invalid_request_error` (on `tool_choice`) | HTTP 400 error response                                                      | `tool_choice` names a tool whose `allowed_callers` does not include `"direct"` | Either add `"direct"` to that tool's `allowed_callers`, or remove the tool from `tool_choice` and let Claude invoke it from code |

### Container expiration during tool call

If your tool result doesn't arrive within about 4 minutes, the pending call raises a `TimeoutError` inside Claude's running code. Claude sees the error in `stderr` and typically retries the call:

To prevent timeouts:

* Monitor the `expires_at` field in responses
* Implement timeouts for your tool execution
* Consider breaking long operations into smaller chunks

### Tool execution errors

If your tool returns an error:

Claude's code receives this error and can handle it appropriately.


## Constraints and limitations

Source: https://platform.claude.com/llms-full.txt#constraints-and-limitations

### Feature incompatibilities

* **Structured outputs:** Tools with `strict: true` are not supported with programmatic calling
* **Tool choice:** You cannot force programmatic calling of a specific tool through `tool_choice`
* **Parallel tool use:** `disable_parallel_tool_use: true` is not supported with programmatic calling

### Input schema limitations

Custom tools whose `input_schema` contains a recursive `$ref` (a reference cycle, such as a schema that refers to itself) cannot be enabled for programmatic calling. Including a code execution tool version in `allowed_callers` for such a tool causes the request to fail with a `400 invalid_request_error` whose message contains `Circular $ref detected`. The same schema is accepted for direct tool calling.

To work around this, do one of the following:

* Keep the tool direct-only by omitting `allowed_callers` (or setting it to `["direct"]`). Other tools in the same request can still use programmatic calling.
* Remove the cycle from the schema. For example, unroll the recursion to a fixed depth and describe any deeper nesting in the `description` of the innermost level, or replace the recursive property with a plain `{"type": "object"}` whose `description` explains the expected shape.

### Tool restrictions

The following tools cannot be called programmatically:

* Tools provided by an [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)
* The [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) toolsets (`computer_toolset_20260801` and `browser_toolset_20260801`), whose `allowed_callers` field accepts only `"direct"`

### Message formatting restrictions

When responding to programmatic tool calls, there are strict formatting requirements:

**Tool result only responses:** If there are pending programmatic tool calls waiting for results, your response message must contain **only** `tool_result` blocks. You cannot include any text content, even after the tool results.

Invalid - Cannot include text when responding to programmatic tool calls:

Valid - Only tool results when responding to programmatic tool calls:

This restriction only applies when responding to programmatic (code execution) tool calls. For regular client-side tool calls, you can include text content after tool results.

**Text-only tool result content:** The `content` of each `tool_result` that answers a programmatic call must be a string or `text` blocks. Image, document, and other content block types are rejected.

### Rate limits

Programmatic tool calls are subject to the same rate limits as regular tool calls. Each tool call from code execution counts as a separate invocation.

### Validate tool results before use

When implementing user-defined tools that will be called programmatically:

* **Tool results are returned as strings:** They can contain any content, including code snippets or executable commands that may be processed by the execution environment.
* **Validate external tool results:** If your tool returns data from external sources or accepts user input, be aware of code injection risks if the output will be interpreted or executed as code.


## Token efficiency

Source: https://platform.claude.com/llms-full.txt#token-efficiency

Programmatic tool calling reduces token consumption in three ways:

* **Tool results from programmatic calls are not added to Claude's context** - only the final code output is
* **Intermediate processing happens in code** - filtering, aggregation, and other transformations don't consume model tokens
* **Multiple tool calls in one code execution** - reduces overhead compared to separate model turns

For example, calling 10 tools directly uses \~10x the tokens of calling them programmatically and returning a summary.

In Anthropic's internal evaluations on a production Claude model:

* On a 75-tool project-management agent benchmark, enabling programmatic tool calling reduced billed input tokens by roughly 38% with no change in task accuracy.
* On [τ²-bench](https://arxiv.org/abs/2506.07982) (airline, retail, and telecom domains), where each turn makes one or two sequential tool calls, programmatic tool calling left scores unchanged and cost roughly 8% more. Sequential single-call workflows do not benefit.
* Across production API traffic, requests whose `tools` array contains 10 to 49 tool definitions see typical token savings of 20% to 40% with programmatic tool calling enabled.

Actual savings vary with workload shape. See [When to use programmatic calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#when-to-use-programmatic-calling).


## Usage and pricing

Source: https://platform.claude.com/llms-full.txt#usage-and-pricing-4

Programmatic tool calling uses the same pricing as code execution. See the [code execution pricing](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#usage-and-pricing) for details.

<Note>
  Token counting for programmatic tool calls: Tool results from programmatic invocations do not count toward your input/output token usage. Only the final code execution result and Claude's response count.
</Note>


## Best practices

Source: https://platform.claude.com/llms-full.txt#best-practices-6

### Tool design

* **Provide detailed output descriptions:** Because Claude deserializes tool results in code, document the format (JSON structure and field types)
* **Return structured data:** JSON or other machine-readable formats work best for programmatic processing
* **Keep responses concise:** Return only necessary data to minimize processing overhead

### When to use programmatic calling

Programmatic tool calling trades a small fixed overhead (container startup, script generation) for large savings on tool-result tokens and model round-trips. Whether that trade pays off depends on workload shape.

**Strong fit:**

* Fan-out or parallel operations across many items (for example, checking 50 endpoints or looking up 20 records)
* Large tool results that can be filtered, aggregated, or summarized before reaching Claude's context
* Agentic search and retrieval, where iterative querying and result filtering dominate the workflow

**Weak fit:**

* Strictly sequential workflows where each call depends on Claude reasoning over the previous result, because the script cannot skip the model round-trip in that case
* A small number of tool calls with small responses, especially on the first turn of a conversation, where container and script overhead can exceed the savings
* Tools that require immediate user feedback between calls

If you are unsure, measure billed input tokens with and without `allowed_callers` on a representative sample of your traffic before enabling it broadly.

### Performance optimization

* **Reuse containers** when making multiple related requests to maintain state
* **Batch similar operations** in a single code execution when possible


## Troubleshooting

Source: https://platform.claude.com/llms-full.txt#troubleshooting-2

### Common issues

**`invalid_request_error` when setting `tool_choice`**

* `tool_choice` cannot name a tool whose `allowed_callers` omits `"direct"`. Either add `"direct"` to that tool's `allowed_callers`, or remove the tool from `tool_choice` and let Claude invoke it from code.

**Container expiration**

* Respond to each programmatic tool call well before the paused response's `expires_at` timestamp. Claude's code stops waiting for a result after about 4 minutes, and idle containers are currently reclaimed after about 5 minutes.
* Consider implementing faster tool execution

**Tool result not parsed correctly**

* Ensure your tool returns string data that Claude can deserialize
* Provide clear output format documentation in your tool description

### Debugging tips

1. **Log all tool calls and results** to track the flow
2. **Check the `caller` field** to confirm programmatic invocation
3. **Monitor container IDs** to ensure proper reuse
4. **Test tools independently** before enabling programmatic calling


## Why programmatic tool calling works

Source: https://platform.claude.com/llms-full.txt#why-programmatic-tool-calling-works

Claude is trained on large amounts of code, so presenting tools as callable Python functions lets it use that strength:

* **Tool composition:** Chained calls, loops, and conditionals are ordinary Python control flow instead of a series of model round trips
* **Result processing:** Claude's code filters and aggregates large tool outputs, or writes them to files, and only the final output enters the context window
* **Latency:** The model is not re-sampled between the tool calls inside one code execution


## Alternative implementations

Source: https://platform.claude.com/llms-full.txt#alternative-implementations

Programmatic tool calling is a generalizable pattern that can also be implemented on your own infrastructure. Here's how the approaches compare:

### Client-side direct execution

Provide Claude with a code execution tool and describe what functions are available in that environment. When Claude invokes the tool with code, your application executes it locally where those functions are defined.

**Advantages:**

* Minimal re-architecting of your application
* Full control over the environment and instructions

**Disadvantages:**

* Executes untrusted code outside of a sandbox
* Tool invocations can be vectors for code injection

**Use when:** Your application can safely execute arbitrary code, you want the smallest implementation, and Anthropic's managed offering doesn't fit your needs.

### Self-managed sandboxed execution

Same approach from Claude's perspective, but code runs in a sandboxed container with security restrictions (for example, no network egress). If your tools require external resources, you'll need a protocol for executing tool calls outside the sandbox.

**Advantages:**

* Safe programmatic tool calling on your own infrastructure
* Full control over the execution environment

**Disadvantages:**

* Complex to build and maintain
* Requires managing both infrastructure and inter-process communication

**Use when:** Security is critical and Anthropic's managed solution doesn't fit your requirements.

### Anthropic-managed execution

Anthropic's programmatic tool calling is a managed version of sandboxed execution with an opinionated Python environment tuned for Claude. Anthropic handles container management, code execution, and secure tool invocation communication.

**Advantages:**

* Safe and secure by default
* Enabled with a tool definition, with no infrastructure to run
* Environment and instructions optimized for Claude

Consider using Anthropic's managed solution if you're using the Claude API, [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), or [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry). On Microsoft Foundry, programmatic tool calling requires a [Hosted on Anthropic deployment](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#additional-features-not-supported-when-hosted-on-azure).


## Data retention

Source: https://platform.claude.com/llms-full.txt#data-retention-6

Programmatic tool calling is built on the code execution infrastructure and uses the same sandbox containers. Container data, including execution artifacts and outputs, is retained for up to 30 days.

For ZDR eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-45

<CardGroup cols={2}>
  <Card title="Fine-grained tool streaming" icon="bolt" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming">
    Stream tool inputs without server-side JSON buffering for latency-sensitive applications.
  </Card>

  <Card title="Code execution tool" icon="code" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool">
    Run Python and bash code in a sandboxed container to analyze data, generate files, and iterate on solutions.
  </Card>

  <Card title="Tool use with Claude" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview">
    Connect Claude to external tools and APIs. See where tools execute, when Claude calls them, and which tool fits your task.
  </Card>

  <Card title="Define tools" icon="hammer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools">
    Specify tool schemas, write effective descriptions, and control when Claude calls your tools.
  </Card>
</CardGroup>


---
title: Tool combinations
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-combinations
description: Common Anthropic tool pairings for research agents, coding agents, and long-running agents.
---

Anthropic-provided tools are designed to work together. Common agent patterns pair tools that cover complementary stages of a workflow: one tool gathers or discovers, another processes or acts. The combinations below are starting points, not prescriptions. Mix them to fit your task.

Each snippet shows only the `tools` array. See [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) for the full request shape.


## Research agent: web\_search + code\_execution

Source: https://platform.claude.com/llms-full.txt#research-agent-web-search-code-execution

Search finds sources; code execution analyzes and synthesizes. Claude searches for data, then writes Python to process, tabulate, or visualize it. This pairing is a good fit for questions that require both up-to-date information and nontrivial computation over that information, such as "compare this quarter's earnings across the top five cloud providers."

The flow is typically search, then execute, then optionally search again if the first pass surfaced a gap. Code execution runs server-side, so there's no client-side sandbox to manage.


## Coding agent: text\_editor + bash

Source: https://platform.claude.com/llms-full.txt#coding-agent-text-editor-bash

The text editor reads and modifies files; bash runs tests and build commands. This is the canonical software-development loop: inspect the code, make an edit, run the tests, repeat. Both tools are client-executed, so your application controls which files and commands are accessible.

Pair this with a constrained working directory and a command allowlist if the agent operates on untrusted code. See [Text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool) and [Bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool) for the execution contracts.


## Cite-then-fetch: web\_search + web\_fetch

Source: https://platform.claude.com/llms-full.txt#cite-then-fetch-web-search-web-fetch

Search surfaces candidate URLs; fetch retrieves full page content for the relevant ones. This avoids fetching everything upfront. Claude runs a search, inspects the snippets, picks the two or three results that actually look relevant, and fetches only those.

This pairing is useful when the answer lives in long-form content (documentation pages, articles, specifications) that a search snippet can't fully capture. Fetch pulls the complete page so Claude can cite specific passages.


## Long-running agent: memory + any other tools

Source: https://platform.claude.com/llms-full.txt#long-running-agent-memory-any-other-tools

Memory persists state across conversations; the other tools do the work. Add memory to any agent that needs to remember prior sessions, such as a support agent that recalls a customer's earlier issues or a project assistant that tracks decisions made last week.

Add your other tools alongside `memory` in the same array.

Memory is orthogonal to your other tools. It doesn't change how they behave; it gives Claude a place to write down and later retrieve facts that would otherwise be lost when the context window resets. See [Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) for the storage model.


## All-in-one: computer\_use

Source: https://platform.claude.com/llms-full.txt#all-in-one-computer-use

The computer use tool subsumes most others by operating a full desktop. Claude sees screenshots and issues mouse and keyboard actions, which means it can drive any application a human can. Use this when the task requires arbitrary GUI interaction that more specific tools can't reach: legacy software without an API, visual verification steps, or workflows that span multiple desktop apps.

The toolset entry takes no `name` or display dimensions: coordinates are expressed in the pixel space of the screenshots you return, and you can turn individual actions off through the entry's `configs` field.

Computer use is the most general option and also the slowest, because Claude typically needs a fresh screenshot after each batch of actions. Prefer narrower tools when they cover your use case, and reach for computer use when nothing else fits. If the task stays inside a web browser, use the browser agent pattern in the next section. See [Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) for the sandbox setup.


## Browser agent: browser\_use

Source: https://platform.claude.com/llms-full.txt#browser-agent-browser-use

When the whole task happens inside webpages (filling forms, reading page content, working across tabs), the browser use tool is a closer fit than computer use. Your application drives a browser it controls and returns screenshots or page state; Claude calls page-aware member tools such as `read_page`, `find`, `form_input`, and `get_page_text` alongside clicks and typing, so it can act on element references in addition to pixel coordinates.

Like the computer use toolset, the entry takes no `name`, and you turn individual member tools off through its `configs` field. See [Browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) for the execution contract.
