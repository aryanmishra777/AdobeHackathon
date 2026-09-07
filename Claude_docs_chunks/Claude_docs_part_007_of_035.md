# platform.claude.com Documentation (Part 7 of 35)

## Batch requests

Source: https://platform.claude.com/llms-full.txt#batch-requests-2

All server tools support batch processing. In a batch, the agentic loop runs just as it does for synchronous requests, with a higher per-turn iteration limit. If the loop reaches that limit, the response ends with `stop_reason: "pause_turn"`; you can continue it by submitting a follow-up request with the returned content. See [Server tools and the agentic loop](https://platform.claude.com/docs/en/build-with-claude/batch-processing#server-tools-and-the-agentic-loop) for details.

Common batch workloads include enriching a dataset with information from the web, checking a large set of documents against current sources, and running analysis code over many files.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-34

<CardGroup cols={2}>
  <Card title="Troubleshooting tool use" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/troubleshooting-tool-use">
    Fix the most common tool-use errors with symptom-to-fix diagnostic tables.
  </Card>

  <Card title="Web search tool" icon="magnifying-glass" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool">
    Search the web and cite results.
  </Card>

  <Card title="Web fetch tool" icon="download" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool">
    Fetch and read content from specific URLs to augment Claude's context with live web content.
  </Card>

  <Card title="Code execution tool" icon="terminal" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool">
    Run Python and bash code in a sandboxed container to analyze data, generate files, and iterate on solutions.
  </Card>

  <Card title="Tool search tool" icon="compass" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool">
    Discover and load tools on demand.
  </Card>
</CardGroup>


---
title: Strict tool use
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use
description: Enforce JSON Schema compliance on Claude's tool inputs with grammar-constrained sampling.
---

Setting `strict: true` on a tool definition guarantees Claude's tool inputs match your JSON Schema by constraining the model's token sampling to schema-valid outputs (a technique called grammar-constrained sampling). This page covers why strict mode matters for agents, how to enable it, and common use cases. For the supported JSON Schema subset, see [JSON Schema limitations](https://platform.claude.com/docs/en/build-with-claude/structured-outputs#json-schema-limitations). For non-strict schema guidance, see [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools).

Strict tool use validates tool parameters, ensuring Claude calls your functions with correctly-typed arguments. Use strict tool use when you need to:

* Validate tool parameters
* Build agentic workflows
* Ensure type-safe function calls
* Handle complex tools with nested properties


## Why strict tool use matters for agents

Source: https://platform.claude.com/llms-full.txt#why-strict-tool-use-matters-for-agents

Building reliable agentic systems requires guaranteed schema conformance. Without strict mode, Claude might return incompatible types (`"2"` instead of `2`) or omit required fields, breaking your functions and causing runtime errors.

Strict tool use guarantees type-safe parameters:

* Functions receive correctly-typed arguments every time
* No need to validate and retry tool calls
* Production-ready agents that work consistently at scale

For example, suppose a booking system needs `passengers: int`. Without strict mode, Claude might provide `passengers: "two"` or `passengers: "2"`. With `strict: true`, the response always contains `passengers: 2`.


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-6

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [
        {"role": "user", "content": "What is the weather in San Francisco?"}
      ],
      "tools": [{
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "strict": true,
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"]
            }
          },
          "required": ["location"],
          "additionalProperties": false
        }
      }]
    }'

bash CLI
  ant messages create --transform content <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  messages:
    - role: user
      content: What is the weather in San Francisco?
  tools:
    - name: get_weather
      description: Get the current weather in a given location
      strict: true
      input_schema:
        type: object
        properties:
          location:
            type: string
            description: The city and state, e.g. San Francisco, CA
          unit:
            type: string
            enum: [celsius, fahrenheit]
        required: [location]
        additionalProperties: false
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}],
      tools=[
          {
              "name": "get_weather",
              "description": "Get the current weather in a given location",
              "strict": True,  # Enable strict mode
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "location": {
                          "type": "string",
                          "description": "The city and state, e.g. San Francisco, CA",
                      },
                      "unit": {
                          "type": "string",
                          "enum": ["celsius", "fahrenheit"],
                          "description": "The unit of temperature, either 'celsius' or 'fahrenheit'",
                      },
                  },
                  "required": ["location"],
                  "additionalProperties": False,
              },
          }
      ],
  )
  print(response.content)

typescript TypeScript
  const client = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY
  });

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: "What's the weather like in San Francisco?"
      }
    ],
    tools: [
      {
        name: "get_weather",
        description: "Get the current weather in a given location",
        strict: true, // Enable strict mode
        input_schema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA"
            },
            unit: {
              type: "string",
              enum: ["celsius", "fahrenheit"]
            }
          },
          required: ["location"],
          additionalProperties: false
        }
      }
    ]
  });
  console.log(response.content);

csharp C#
  using System.Text.Json;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "What's the weather like in San Francisco?" }],
      Tools = [
          new ToolUnion(new Tool()
          {
              Name = "get_weather",
              Description = "Get the current weather in a given location",
              Strict = true,
              InputSchema = new InputSchema(new Dictionary<string, JsonElement>
              {
                  ["properties"] = JsonSerializer.SerializeToElement(new Dictionary<string, object>
                  {
                      ["location"] = new { type = "string", description = "The city and state, e.g. San Francisco, CA" },
                      ["unit"] = new { type = "string", @enum = new[] { "celsius", "fahrenheit" } },
                  }),
                  ["required"] = JsonSerializer.SerializeToElement(new[] { "location" }),
                  ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
              }),
          }),
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather like in San Francisco?")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfTool: &anthropic.ToolParam{
  			Name:        "get_weather",
  			Description: anthropic.String("Get the current weather in a given location"),
  			Strict:      anthropic.Bool(true),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"location": map[string]any{
  						"type":        "string",
  						"description": "The city and state, e.g. San Francisco, CA",
  					},
  					"unit": map[string]any{
  						"type": "string",
  						"enum": []string{"celsius", "fahrenheit"},
  					},
  				},
  				Required: []string{"location"},
  				ExtraFields: map[string]any{
  					"additionalProperties": false,
  				},
  			}}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.Content)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  InputSchema schema = InputSchema.builder()
      .properties(
          JsonValue.from(
              Map.of(
                  "location", Map.of(
                      "type", "string",
                      "description", "The city and state, e.g. San Francisco, CA"
                  ),
                  "unit", Map.of(
                      "type", "string",
                      "enum", List.of("celsius", "fahrenheit")
                  )
              )
          )
      )
      .putAdditionalProperty("required", JsonValue.from(List.of("location")))
      .putAdditionalProperty("additionalProperties", JsonValue.from(false))
      .build();

  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024L)
      .addUserMessage("What's the weather like in San Francisco?")
      .addTool(
          Tool.builder()
              .name("get_weather")
              .description("Get the current weather in a given location")
              .strict(true)
              .inputSchema(schema)
              .build()
      )
      .build();

  Message response = client.messages().create(params);
  IO.println(response.content());

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => "What's the weather like in San Francisco?"]
      ],
      model: 'claude-opus-5',
      tools: [
          [
              'name' => 'get_weather',
              'description' => 'Get the current weather in a given location',
              'strict' => true,
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'location' => [
                          'type' => 'string',
                          'description' => 'The city and state, e.g. San Francisco, CA'
                      ],
                      'unit' => [
                          'type' => 'string',
                          'enum' => ['celsius', 'fahrenheit']
                      ]
                  ],
                  'required' => ['location'],
                  'additionalProperties' => false
              ]
          ]
      ],
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      { role: "user", content: "What's the weather like in San Francisco?" }
    ],
    tools: [
      {
        name: "get_weather",
        description: "Get the current weather in a given location",
        strict: true,
        input_schema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA"
            },
            unit: {
              type: "string",
              enum: ["celsius", "fahrenheit"]
            }
          },
          required: ["location"],
          additionalProperties: false
        }
      }
    ]
  )
  puts message.content

json Output
{
  "type": "tool_use",
  "name": "get_weather",
  "input": {
    "location": "San Francisco, CA"
  }
}
```

**Guarantees:**

* Tool `input` strictly follows the `input_schema`
* Tool `name` is always valid (from provided tools or server tools)


## How it works

Source: https://platform.claude.com/llms-full.txt#how-it-works-5

<Steps>
  <Step title="Define your tool schema">
    Create a JSON schema for your tool's `input_schema`. The schema uses standard JSON Schema format with some limitations (see [JSON Schema limitations](https://platform.claude.com/docs/en/build-with-claude/structured-outputs#json-schema-limitations)).
  </Step>

  <Step title="Add strict: true">
    Set `"strict": true` as a top-level property in your tool definition, alongside `name`, `description`, and `input_schema`.
  </Step>

  <Step title="Handle tool calls">
    When Claude uses the tool, the `input` field in the `tool_use` block strictly follows your `input_schema`, and the `name` is always valid.
  </Step>
</Steps>

The [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) toolset entries (`computer_toolset_20260801` and `browser_toolset_20260801`) don't accept `strict: true`; a request that sets it on either entry is rejected.


## Common use cases

Source: https://platform.claude.com/llms-full.txt#common-use-cases

<AccordionGroup>
  <Accordion title="Validated tool inputs">
    Ensure tool parameters exactly match your schema:

    <CodeGroup>
      ```bash cURL
      curl https://api.anthropic.com/v1/messages \
        -H "content-type: application/json" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -d '{
          "model": "claude-opus-5",
          "max_tokens": 1024,
          "messages": [
            {"role": "user", "content": "Search for flights to Tokyo departing June 1, 2026"}
          ],
          "tools": [{
            "name": "search_flights",
            "strict": true,
            "input_schema": {
              "type": "object",
              "properties": {
                "destination": {"type": "string"},
                "departure_date": {"type": "string", "format": "date"},
                "passengers": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
              },
              "required": ["destination", "departure_date"],
              "additionalProperties": false
            }
          }]
        }'

bash CLI
      ant messages create <<'YAML'
      model: claude-opus-5
      max_tokens: 1024
      messages:
        - role: user
          content: Search for flights to Tokyo departing June 1, 2026
      tools:
        - name: search_flights
          strict: true
          input_schema:
            type: object
            properties:
              destination:
                type: string
              departure_date:
                type: string
                format: date
              passengers:
                type: integer
                enum: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            required: [destination, departure_date]
            additionalProperties: false
      YAML

python Python
      client = Anthropic()
      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          messages=[
              {
                  "role": "user",
                  "content": "Search for flights to Tokyo departing June 1, 2026",
              }
          ],
          tools=[
              {
                  "name": "search_flights",
                  "strict": True,
                  "input_schema": {
                      "type": "object",
                      "properties": {
                          "destination": {"type": "string"},
                          "departure_date": {"type": "string", "format": "date"},
                          "passengers": {
                              "type": "integer",
                              "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                          },
                      },
                      "required": ["destination", "departure_date"],
                      "additionalProperties": False,
                  },
              }
          ],
      )

      print(response)

typescript TypeScript
      const client = new Anthropic();

      const searchFlightsTool: Anthropic.Tool = {
        name: "search_flights",
        strict: true,
        input_schema: {
          type: "object",
          properties: {
            destination: { type: "string" },
            departure_date: { type: "string", format: "date" },
            passengers: { type: "integer", enum: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] }
          },
          required: ["destination", "departure_date"],
          additionalProperties: false
        }
      };

      const response = await client.messages.create({
        model: "claude-opus-5",
        max_tokens: 1024,
        messages: [{ role: "user", content: "Search for flights to Tokyo departing June 1, 2026" }],
        tools: [searchFlightsTool]
      });

      console.log(response);

csharp C#
      using System.Text.Json;
      using Anthropic;
      using Anthropic.Models.Messages;

      AnthropicClient client = new();

      var parameters = new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages = [new() { Role = Role.User, Content = "Search for flights to Tokyo departing June 1, 2026" }],
          Tools = [
              new ToolUnion(new Tool()
              {
                  Name = "search_flights",
                  Strict = true,
                  InputSchema = new InputSchema(new Dictionary<string, JsonElement>
                  {
                      ["properties"] = JsonSerializer.SerializeToElement(new Dictionary<string, object>
                      {
                          ["destination"] = new { type = "string" },
                          ["departure_date"] = new { type = "string", format = "date" },
                          ["passengers"] = new { type = "integer", @enum = new[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 } },
                      }),
                      ["required"] = JsonSerializer.SerializeToElement(new[] { "destination", "departure_date" }),
                      ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
                  }),
              }),
          ]
      };

      var message = await client.Messages.Create(parameters);
      Console.WriteLine(message);

go Go
      client := anthropic.NewClient()

      response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
      	Model:     anthropic.ModelClaudeOpus5,
      	MaxTokens: 1024,
      	Messages: []anthropic.MessageParam{
      		anthropic.NewUserMessage(anthropic.NewTextBlock("Search for flights to Tokyo departing June 1, 2026")),
      	},
      	Tools: []anthropic.ToolUnionParam{
      		{OfTool: &anthropic.ToolParam{
      			Name:   "search_flights",
      			Strict: anthropic.Bool(true),
      			InputSchema: anthropic.ToolInputSchemaParam{
      				Properties: map[string]any{
      					"destination": map[string]any{
      						"type": "string",
      					},
      					"departure_date": map[string]any{
      						"type":   "string",
      						"format": "date",
      					},
      					"passengers": map[string]any{
      						"type": "integer",
      						"enum": []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
      					},
      				},
      				Required: []string{"destination", "departure_date"},
      				ExtraFields: map[string]any{
      					"additionalProperties": false,
      				},
      			}}},
      	},
      })
      if err != nil {
      	log.Fatal(err)
      }
      fmt.Println(response.RawJSON())

java Java
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      InputSchema schema = InputSchema.builder()
          .properties(
              JsonValue.from(
                  Map.of(
                      "destination", Map.of("type", "string"),
                      "departure_date", Map.of("type", "string", "format", "date"),
                      "passengers", Map.of(
                          "type", "integer",
                          "enum", List.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                      )
                  )
              )
          )
          .putAdditionalProperty("required", JsonValue.from(List.of("destination", "departure_date")))
          .putAdditionalProperty("additionalProperties", JsonValue.from(false))
          .build();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addUserMessage("Search for flights to Tokyo departing June 1, 2026")
          .addTool(
              Tool.builder()
                  .name("search_flights")
                  .strict(true)
                  .inputSchema(schema)
                  .build()
          )
          .build();

      Message response = client.messages().create(params);
      IO.println(response);

php PHP
      $client = new Client();

      $message = $client->messages->create(
          maxTokens: 1024,
          messages: [
              ['role' => 'user', 'content' => 'Search for flights to Tokyo departing June 1, 2026']
          ],
          model: 'claude-opus-5',
          tools: [
              [
                  'name' => 'search_flights',
                  'strict' => true,
                  'input_schema' => [
                      'type' => 'object',
                      'properties' => [
                          'destination' => ['type' => 'string'],
                          'departure_date' => ['type' => 'string', 'format' => 'date'],
                          'passengers' => [
                              'type' => 'integer',
                              'enum' => [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                          ]
                      ],
                      'required' => ['destination', 'departure_date'],
                      'additionalProperties' => false
                  ]
              ]
          ],
      );

      echo $message;

ruby Ruby
      client = Anthropic::Client.new

      message = client.messages.create(
        model: "claude-opus-5",
        max_tokens: 1024,
        messages: [
          { role: "user", content: "Search for flights to Tokyo departing June 1, 2026" }
        ],
        tools: [
          {
            name: "search_flights",
            strict: true,
            input_schema: {
              type: "object",
              properties: {
                destination: { type: "string" },
                departure_date: { type: "string", format: "date" },
                passengers: {
                  type: "integer",
                  enum: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                }
              },
              required: ["destination", "departure_date"],
              additionalProperties: false
            }
          }
        ]
      )
      puts message

bash cURL
      curl https://api.anthropic.com/v1/messages \
        -H "content-type: application/json" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -d '{
          "model": "claude-opus-5",
          "max_tokens": 1024,
          "messages": [
            {"role": "user", "content": "Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026"}
          ],
          "tools": [
            {
              "name": "search_flights",
              "strict": true,
              "input_schema": {
                "type": "object",
                "properties": {
                  "origin": {"type": "string"},
                  "destination": {"type": "string"},
                  "departure_date": {"type": "string", "format": "date"},
                  "travelers": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6]}
                },
                "required": ["origin", "destination", "departure_date"],
                "additionalProperties": false
              }
            },
            {
              "name": "search_hotels",
              "strict": true,
              "input_schema": {
                "type": "object",
                "properties": {
                  "city": {"type": "string"},
                  "check_in": {"type": "string", "format": "date"},
                  "guests": {"type": "integer", "enum": [1, 2, 3, 4]}
                },
                "required": ["city", "check_in"],
                "additionalProperties": false
              }
            }
          ]
        }'

bash CLI
      ant messages create <<'YAML'
      model: claude-opus-5
      max_tokens: 1024
      messages:
        - role: user
          content: >-
            Help me plan a trip from New York to Paris for 2 people,
            departing June 1, 2026
      tools:
        - name: search_flights
          strict: true
          input_schema:
            type: object
            properties:
              origin: {type: string}
              destination: {type: string}
              departure_date: {type: string, format: date}
              travelers: {type: integer, enum: [1, 2, 3, 4, 5, 6]}
            required: [origin, destination, departure_date]
            additionalProperties: false
        - name: search_hotels
          strict: true
          input_schema:
            type: object
            properties:
              city: {type: string}
              check_in: {type: string, format: date}
              guests: {type: integer, enum: [1, 2, 3, 4]}
            required: [city, check_in]
            additionalProperties: false
      YAML

python Python
      client = Anthropic()
      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          messages=[
              {
                  "role": "user",
                  "content": "Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026",
              }
          ],
          tools=[
              {
                  "name": "search_flights",
                  "strict": True,
                  "input_schema": {
                      "type": "object",
                      "properties": {
                          "origin": {"type": "string"},
                          "destination": {"type": "string"},
                          "departure_date": {"type": "string", "format": "date"},
                          "travelers": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6]},
                      },
                      "required": ["origin", "destination", "departure_date"],
                      "additionalProperties": False,
                  },
              },
              {
                  "name": "search_hotels",
                  "strict": True,
                  "input_schema": {
                      "type": "object",
                      "properties": {
                          "city": {"type": "string"},
                          "check_in": {"type": "string", "format": "date"},
                          "guests": {"type": "integer", "enum": [1, 2, 3, 4]},
                      },
                      "required": ["city", "check_in"],
                      "additionalProperties": False,
                  },
              },
          ],
      )

      print(response)

typescript TypeScript
      const client = new Anthropic();

      const tools: Anthropic.Tool[] = [
        {
          name: "search_flights",
          strict: true,
          input_schema: {
            type: "object",
            properties: {
              origin: { type: "string" },
              destination: { type: "string" },
              departure_date: { type: "string", format: "date" },
              travelers: { type: "integer", enum: [1, 2, 3, 4, 5, 6] }
            },
            required: ["origin", "destination", "departure_date"],
            additionalProperties: false
          }
        },
        {
          name: "search_hotels",
          strict: true,
          input_schema: {
            type: "object",
            properties: {
              city: { type: "string" },
              check_in: { type: "string", format: "date" },
              guests: { type: "integer", enum: [1, 2, 3, 4] }
            },
            required: ["city", "check_in"],
            additionalProperties: false
          }
        }
      ];

      const response = await client.messages.create({
        model: "claude-opus-5",
        max_tokens: 1024,
        messages: [
          {
            role: "user",
            content:
              "Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026"
          }
        ],
        tools: tools
      });

      console.log(response);

csharp C#
      using System.Text.Json;
      using Anthropic;
      using Anthropic.Models.Messages;

      AnthropicClient client = new();

      var parameters = new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages = [new() { Role = Role.User, Content = "Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026" }],
          Tools = [
              new ToolUnion(new Tool()
              {
                  Name = "search_flights",
                  Strict = true,
                  InputSchema = new InputSchema(new Dictionary<string, JsonElement>
                  {
                      ["properties"] = JsonSerializer.SerializeToElement(new Dictionary<string, object>
                      {
                          ["origin"] = new { type = "string" },
                          ["destination"] = new { type = "string" },
                          ["departure_date"] = new { type = "string", format = "date" },
                          ["travelers"] = new { type = "integer", @enum = new[] { 1, 2, 3, 4, 5, 6 } },
                      }),
                      ["required"] = JsonSerializer.SerializeToElement(new[] { "origin", "destination", "departure_date" }),
                      ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
                  }),
              }),
              new ToolUnion(new Tool()
              {
                  Name = "search_hotels",
                  Strict = true,
                  InputSchema = new InputSchema(new Dictionary<string, JsonElement>
                  {
                      ["properties"] = JsonSerializer.SerializeToElement(new Dictionary<string, object>
                      {
                          ["city"] = new { type = "string" },
                          ["check_in"] = new { type = "string", format = "date" },
                          ["guests"] = new { type = "integer", @enum = new[] { 1, 2, 3, 4 } },
                      }),
                      ["required"] = JsonSerializer.SerializeToElement(new[] { "city", "check_in" }),
                      ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
                  }),
              }),
          ]
      };

      var message = await client.Messages.Create(parameters);
      Console.WriteLine(message);

go Go
      client := anthropic.NewClient()

      response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
      	Model:     anthropic.ModelClaudeOpus5,
      	MaxTokens: 1024,
      	Messages: []anthropic.MessageParam{
      		anthropic.NewUserMessage(anthropic.NewTextBlock("Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026")),
      	},
      	Tools: []anthropic.ToolUnionParam{
      		{OfTool: &anthropic.ToolParam{
      			Name:   "search_flights",
      			Strict: anthropic.Bool(true),
      			InputSchema: anthropic.ToolInputSchemaParam{
      				Properties: map[string]any{
      					"origin":         map[string]any{"type": "string"},
      					"destination":    map[string]any{"type": "string"},
      					"departure_date": map[string]any{"type": "string", "format": "date"},
      					"travelers":      map[string]any{"type": "integer", "enum": []int{1, 2, 3, 4, 5, 6}},
      				},
      				Required: []string{"origin", "destination", "departure_date"},
      				ExtraFields: map[string]any{
      					"additionalProperties": false,
      				},
      			}}},
      		{OfTool: &anthropic.ToolParam{
      			Name:   "search_hotels",
      			Strict: anthropic.Bool(true),
      			InputSchema: anthropic.ToolInputSchemaParam{
      				Properties: map[string]any{
      					"city":     map[string]any{"type": "string"},
      					"check_in": map[string]any{"type": "string", "format": "date"},
      					"guests":   map[string]any{"type": "integer", "enum": []int{1, 2, 3, 4}},
      				},
      				Required: []string{"city", "check_in"},
      				ExtraFields: map[string]any{
      					"additionalProperties": false,
      				},
      			}}},
      	},
      })
      if err != nil {
      	log.Fatal(err)
      }
      fmt.Println(response.RawJSON())

java Java
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      InputSchema flightsSchema = InputSchema.builder()
          .properties(
              JsonValue.from(
                  Map.of(
                      "origin", Map.of("type", "string"),
                      "destination", Map.of("type", "string"),
                      "departure_date", Map.of("type", "string", "format", "date"),
                      "travelers", Map.of("type", "integer", "enum", List.of(1, 2, 3, 4, 5, 6))
                  )
              )
          )
          .putAdditionalProperty("required", JsonValue.from(List.of("origin", "destination", "departure_date")))
          .putAdditionalProperty("additionalProperties", JsonValue.from(false))
          .build();

      InputSchema hotelsSchema = InputSchema.builder()
          .properties(
              JsonValue.from(
                  Map.of(
                      "city", Map.of("type", "string"),
                      "check_in", Map.of("type", "string", "format", "date"),
                      "guests", Map.of("type", "integer", "enum", List.of(1, 2, 3, 4))
                  )
              )
          )
          .putAdditionalProperty("required", JsonValue.from(List.of("city", "check_in")))
          .putAdditionalProperty("additionalProperties", JsonValue.from(false))
          .build();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addUserMessage("Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026")
          .addTool(
              Tool.builder()
                  .name("search_flights")
                  .strict(true)
                  .inputSchema(flightsSchema)
                  .build()
          )
          .addTool(
              Tool.builder()
                  .name("search_hotels")
                  .strict(true)
                  .inputSchema(hotelsSchema)
                  .build()
          )
          .build();

      Message response = client.messages().create(params);
      IO.println(response);

php PHP
      $client = new Client();

      $message = $client->messages->create(
          maxTokens: 1024,
          messages: [
              ['role' => 'user', 'content' => 'Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026']
          ],
          model: 'claude-opus-5',
          tools: [
              [
                  'name' => 'search_flights',
                  'strict' => true,
                  'input_schema' => [
                      'type' => 'object',
                      'properties' => [
                          'origin' => ['type' => 'string'],
                          'destination' => ['type' => 'string'],
                          'departure_date' => ['type' => 'string', 'format' => 'date'],
                          'travelers' => ['type' => 'integer', 'enum' => [1, 2, 3, 4, 5, 6]]
                      ],
                      'required' => ['origin', 'destination', 'departure_date'],
                      'additionalProperties' => false
                  ]
              ],
              [
                  'name' => 'search_hotels',
                  'strict' => true,
                  'input_schema' => [
                      'type' => 'object',
                      'properties' => [
                          'city' => ['type' => 'string'],
                          'check_in' => ['type' => 'string', 'format' => 'date'],
                          'guests' => ['type' => 'integer', 'enum' => [1, 2, 3, 4]]
                      ],
                      'required' => ['city', 'check_in'],
                      'additionalProperties' => false
                  ]
              ]
          ],
      );

      echo $message;

ruby Ruby
      client = Anthropic::Client.new

      message = client.messages.create(
        model: "claude-opus-5",
        max_tokens: 1024,
        messages: [
          { role: "user", content: "Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026" }
        ],
        tools: [
          {
            name: "search_flights",
            strict: true,
            input_schema: {
              type: "object",
              properties: {
                origin: { type: "string" },
                destination: { type: "string" },
                departure_date: { type: "string", format: "date" },
                travelers: { type: "integer", enum: [1, 2, 3, 4, 5, 6] }
              },
              required: ["origin", "destination", "departure_date"],
              additionalProperties: false
            }
          },
          {
            name: "search_hotels",
            strict: true,
            input_schema: {
              type: "object",
              properties: {
                city: { type: "string" },
                check_in: { type: "string", format: "date" },
                guests: { type: "integer", enum: [1, 2, 3, 4] }
              },
              required: ["city", "check_in"],
              additionalProperties: false
            }
          }
        ]
      )
      puts message
      ```
    </CodeGroup>
  </Accordion>
</AccordionGroup>


## Data retention

Source: https://platform.claude.com/llms-full.txt#data-retention-5

Strict tool use compiles tool `input_schema` definitions into grammars using the same pipeline as [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs). Tool schemas are temporarily cached for up to 24 hours since last use. Prompts and responses are not retained beyond the API response.

Strict tool use is HIPAA eligible, but **protected health information (PHI) must not be included in tool schema definitions**. The API caches compiled schemas separately from message content, and these cached schemas do not receive the same PHI protections as prompts and responses. Do not include PHI in `input_schema` property names, `enum` values, `const` values, or `pattern` regular expressions. PHI should only appear in message content (prompts and responses), where it is protected under HIPAA safeguards.

For ZDR and HIPAA eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-35

<CardGroup cols={2}>
  <Card title="Web fetch tool" icon="link" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool">
    Fetch and read content from specific URLs to bring live web content into Claude's context.
  </Card>

  <Card title="Tool use with prompt caching" icon="database" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching">
    Cache tool definitions across turns to reduce cost and latency.
  </Card>

  <Card title="Structured outputs" icon="code-brackets" href="https://platform.claude.com/docs/en/build-with-claude/structured-outputs">
    Get validated JSON responses using the same grammar-constrained sampling.
  </Card>

  <Card title="Define tools" icon="hammer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools">
    Specify tool schemas, write effective descriptions, and control when Claude calls your tools.
  </Card>
</CardGroup>


---
title: Text editor tool
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool
description: Give Claude the Anthropic-defined text editor tool to view, create, and edit files, and handle its view, str_replace, create, and insert commands.
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

Claude can use an Anthropic-schema text editor tool to view and modify text files, helping you debug, fix, and improve your code or other text documents. This allows Claude to directly interact with your files, providing hands-on assistance rather than just suggesting changes.

For model support, see the [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference).


## When to use the text editor tool

Source: https://platform.claude.com/llms-full.txt#when-to-use-the-text-editor-tool

Some examples of when to use the text editor tool are:

* **Code debugging:** Have Claude identify and fix bugs in your code, from syntax errors to logic issues.
* **Code refactoring:** Let Claude improve your code structure, readability, and performance through targeted edits.
* **Documentation generation:** Ask Claude to add docstrings, comments, or README files to your code base.
* **Test creation:** Have Claude create unit tests for your code based on its analysis of the implementation.


## Use the text editor tool

Source: https://platform.claude.com/llms-full.txt#use-the-text-editor-tool

Provide the text editor tool (named `str_replace_based_edit_tool`) to Claude using the Messages API.

You can optionally specify a `max_characters` parameter to control truncation when viewing large files.

<Note>
  `max_characters` is only compatible with `text_editor_20250728` and later versions of the text editor tool.
</Note>

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "tools": [
        {
          "type": "text_editor_20250728",
          "name": "str_replace_based_edit_tool",
          "max_characters": 10000
        }
      ],
      "messages": [
        {
          "role": "user",
          "content": "There'\''s a syntax error in my primes.py file. Can you help me fix it?"
        }
      ]
    }'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --tool '{type: text_editor_20250728, name: str_replace_based_edit_tool, max_characters: 10000}' \
    --message '{role: user, content: There is a syntax error in my primes.py file. Can you help me fix it?}'

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[
          {
              "type": "text_editor_20250728",
              "name": "str_replace_based_edit_tool",
              "max_characters": 10000,
          }
      ],
      messages=[
          {
              "role": "user",
              "content": "There's a syntax error in my primes.py file. Can you help me fix it?",
          }
      ],
  )

  print(response)

typescript TypeScript
  const anthropic = new Anthropic();

  const response = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        type: "text_editor_20250728",
        name: "str_replace_based_edit_tool",
        max_characters: 10000
      }
    ],
    messages: [
      {
        role: "user",
        content: "There's a syntax error in my primes.py file. Can you help me fix it?"
      }
    ]
  });

  console.log(response);

csharp C#
  var client = new AnthropicClient();

  var response = await client.Messages.Create(
      new()
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Tools = [new ToolTextEditor20250728 { MaxCharacters = 10000 }],
          Messages =
          [
              new()
              {
                  Role = Role.User,
                  Content = "There's a syntax error in my primes.py file. Can you help me fix it?",
              },
          ],
      }
  );

  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{
  		{OfTextEditor20250728: &anthropic.ToolTextEditor20250728Param{
  			MaxCharacters: anthropic.Int(10000),
  		}},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("There's a syntax error in my primes.py file. Can you help me fix it?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.messages.ToolTextEditor20250728;
  // ...
  void main() {
    AnthropicClient client = AnthropicOkHttpClient.fromEnv();

    ToolTextEditor20250728 editorTool =
      ToolTextEditor20250728.builder()
        .maxCharacters(10000L)
        .build();

    MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024)
      .addTool(editorTool)
      .addUserMessage("There's a syntax error in my primes.py file. Can you help me fix it?")
      .build();

    Message message = client.messages().create(params);
    IO.println(message);
  }

php PHP
  $client = new Client();

  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: [ToolTextEditor20250728::with(maxCharacters: 10000)],
      messages: [
          [
              'role' => 'user',
              'content' => "There's a syntax error in my primes.py file. Can you help me fix it?",
          ],
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        type: "text_editor_20250728",
        name: "str_replace_based_edit_tool",
        max_characters: 10000
      }
    ],
    messages: [
      {
        role: "user",
        content: "There's a syntax error in my primes.py file. Can you help me fix it?"
      }
    ]
  )

  puts response

json
  {
    "type": "tool_use",
    "id": "toolu_01A09q90qw90lq917835lq9",
    "name": "str_replace_based_edit_tool",
    "input": {
      "command": "view",
      "path": "primes.py"
    }
  }

json
  {
    "type": "tool_use",
    "id": "toolu_02B19r91rw91mr917835mr9",
    "name": "str_replace_based_edit_tool",
    "input": {
      "command": "view",
      "path": "src/"
    }
  }

json
  {
    "type": "tool_use",
    "id": "toolu_01A09q90qw90lq917835lq9",
    "name": "str_replace_based_edit_tool",
    "input": {
      "command": "str_replace",
      "path": "primes.py",
      "old_str": "for num in range(2, limit + 1)",
      "new_str": "for num in range(2, limit + 1):"
    }
  }

json
  {
    "type": "tool_use",
    "id": "toolu_01A09q90qw90lq917835lq9",
    "name": "str_replace_based_edit_tool",
    "input": {
      "command": "create",
      "path": "test_primes.py",
      "file_text": "import unittest\nimport primes\n\nclass TestPrimes(unittest.TestCase):\n    def test_is_prime(self):\n        self.assertTrue(primes.is_prime(2))\n        self.assertTrue(primes.is_prime(3))\n        self.assertFalse(primes.is_prime(4))\n\nif __name__ == '__main__':\n    unittest.main()"
    }
  }

json
  {
    "type": "tool_use",
    "id": "toolu_01A09q90qw90lq917835lq9",
    "name": "str_replace_based_edit_tool",
    "input": {
      "command": "insert",
      "path": "primes.py",
      "insert_line": 0,
      "insert_text": "\"\"\"Module for working with prime numbers.\n\nThis module provides functions to check if a number is prime\nand to generate a list of prime numbers up to a given limit.\n\"\"\"\n"
    }
  }

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "tools": [
        {
          "type": "text_editor_20250728",
          "name": "str_replace_based_edit_tool"
        }
      ],
      "messages": [
        {
          "role": "user",
          "content": "There'\''s a syntax error in my primes.py file. Can you help me fix it?"
        }
      ]
    }'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --tool '{type: text_editor_20250728, name: str_replace_based_edit_tool}' \
    --message '{role: user, content: There is a syntax error in my primes.py file. Can you help me fix it?}'

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}],
      messages=[
          {
              "role": "user",
              "content": "There's a syntax error in my primes.py file. Can you help me fix it?",
          }
      ],
  )

  print(response)

typescript TypeScript
  const anthropic = new Anthropic();

  const response = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        type: "text_editor_20250728",
        name: "str_replace_based_edit_tool"
      }
    ],
    messages: [
      {
        role: "user",
        content: "There's a syntax error in my primes.py file. Can you help me fix it?"
      }
    ]
  });

  console.log(response);

csharp C#
  var client = new AnthropicClient();

  var response = await client.Messages.Create(
      new()
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Tools = [new ToolTextEditor20250728()],
          Messages =
          [
              new()
              {
                  Role = Role.User,
                  Content = "There's a syntax error in my primes.py file. Can you help me fix it?",
              },
          ],
      }
  );

  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{
  		{OfTextEditor20250728: &anthropic.ToolTextEditor20250728Param{}},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("There's a syntax error in my primes.py file. Can you help me fix it?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.messages.ToolTextEditor20250728;
  // ...
  void main() {
    AnthropicClient client = AnthropicOkHttpClient.fromEnv();

    ToolTextEditor20250728 editorTool =
      ToolTextEditor20250728.builder().build();

    MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024)
      .addTool(editorTool)
      .addUserMessage("There's a syntax error in my primes.py file. Can you help me fix it?")
      .build();

    Message message = client.messages().create(params);
    IO.println(message);
  }

php PHP
  $client = new Client();

  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: [new ToolTextEditor20250728()],
      messages: [
          [
              'role' => 'user',
              'content' => "There's a syntax error in my primes.py file. Can you help me fix it?",
          ],
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [{type: "text_editor_20250728", name: "str_replace_based_edit_tool"}],
    messages: [
      {
        role: "user",
        content: "There's a syntax error in my primes.py file. Can you help me fix it?"
      }
    ]
  )

  puts response

json Output
{
  "id": "msg_01XAbCDeFgHiJkLmNoPQrStU",
  "model": "claude-opus-5",
  "stop_reason": "tool_use",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "I'll help you fix the syntax error in your primes.py file. First, let me take a look at the file to identify the issue."
    },
    {
      "type": "tool_use",
      "id": "toolu_01AbCdEfGhIjKlMnOpQrStU",
      "name": "str_replace_based_edit_tool",
      "input": {
        "command": "view",
        "path": "primes.py"
      }
    }
  ]
}

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "tools": [
        {
          "type": "text_editor_20250728",
          "name": "str_replace_based_edit_tool"
        }
      ],
      "messages": [
        {
          "role": "user",
          "content": "There'\''s a syntax error in my primes.py file. Can you help me fix it?"
        },
        {
          "role": "assistant",
          "content": [
            {
              "type": "text",
              "text": "I'\''ll help you fix the syntax error in your primes.py file. First, let me take a look at the file to identify the issue."
            },
            {
              "type": "tool_use",
              "id": "toolu_01AbCdEfGhIjKlMnOpQrStU",
              "name": "str_replace_based_edit_tool",
              "input": {
                "command": "view",
                "path": "primes.py"
              }
            }
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "tool_result",
              "tool_use_id": "toolu_01AbCdEfGhIjKlMnOpQrStU",
              "content": "1: def is_prime(n):\n2:     \"\"\"Check if a number is prime.\"\"\"\n3:     if n <= 1:\n4:         return False\n5:     if n <= 3:\n6:         return True\n7:     if n % 2 == 0 or n % 3 == 0:\n8:         return False\n9:     i = 5\n10:     while i * i <= n:\n11:         if n % i == 0 or n % (i + 2) == 0:\n12:             return False\n13:         i += 6\n14:     return True\n15: \n16: def get_primes(limit):\n17:     \"\"\"Generate a list of prime numbers up to the given limit.\"\"\"\n18:     primes = []\n19:     for num in range(2, limit + 1)\n20:         if is_prime(num):\n21:             primes.append(num)\n22:     return primes\n23: \n24: def main():\n25:     \"\"\"Main function to demonstrate prime number generation.\"\"\"\n26:     limit = 100\n27:     prime_list = get_primes(limit)\n28:     print(f\"Prime numbers up to {limit}:\")\n29:     print(prime_list)\n30:     print(f\"Found {len(prime_list)} prime numbers.\")\n31: \n32: if __name__ == \"__main__\":\n33:     main()"
            }
          ]
        }
      ]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tools:
    - type: text_editor_20250728
      name: str_replace_based_edit_tool
  messages:
    - role: user
      content: There's a syntax error in my primes.py file. Can you help me fix it?
    - role: assistant
      content:
        - type: text
          text: >-
            I'll help you fix the syntax error in your primes.py file. First,
            let me take a look at the file to identify the issue.
        - type: tool_use
          id: toolu_01AbCdEfGhIjKlMnOpQrStU
          name: str_replace_based_edit_tool
          input:
            command: view
            path: primes.py
    - role: user
      content:
        - type: tool_result
          tool_use_id: toolu_01AbCdEfGhIjKlMnOpQrStU
          content: |-
            1: def is_prime(n):
            2:     """Check if a number is prime."""
            3:     if n <= 1:
            4:         return False
            5:     if n <= 3:
            6:         return True
            7:     if n % 2 == 0 or n % 3 == 0:
            8:         return False
            9:     i = 5
            10:     while i * i <= n:
            11:         if n % i == 0 or n % (i + 2) == 0:
            12:             return False
            13:         i += 6
            14:     return True
            15:
            16: def get_primes(limit):
            17:     """Generate a list of prime numbers up to the given limit."""
            18:     primes = []
            19:     for num in range(2, limit + 1)
            20:         if is_prime(num):
            21:             primes.append(num)
            22:     return primes
            23:
            24: def main():
            25:     """Main function to demonstrate prime number generation."""
            26:     limit = 100
            27:     prime_list = get_primes(limit)
            28:     print(f"Prime numbers up to {limit}:")
            29:     print(prime_list)
            30:     print(f"Found {len(prime_list)} prime numbers.")
            31:
            32: if __name__ == "__main__":
            33:     main()
  YAML

python Python
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}],
      messages=[
          {
              "role": "user",
              "content": "There's a syntax error in my primes.py file. Can you help me fix it?",
          },
          {
              "role": "assistant",
              "content": [
                  {
                      "type": "text",
                      "text": "I'll help you fix the syntax error in your primes.py file. First, let me take a look at the file to identify the issue.",
                  },
                  {
                      "type": "tool_use",
                      "id": "toolu_01AbCdEfGhIjKlMnOpQrStU",
                      "name": "str_replace_based_edit_tool",
                      "input": {"command": "view", "path": "primes.py"},
                  },
              ],
          },
          {
              "role": "user",
              "content": [
                  {
                      "type": "tool_result",
                      "tool_use_id": "toolu_01AbCdEfGhIjKlMnOpQrStU",
                      "content": '1: def is_prime(n):\n2:     """Check if a number is prime."""\n3:     if n <= 1:\n4:         return False\n5:     if n <= 3:\n6:         return True\n7:     if n % 2 == 0 or n % 3 == 0:\n8:         return False\n9:     i = 5\n10:     while i * i <= n:\n11:         if n % i == 0 or n % (i + 2) == 0:\n12:             return False\n13:         i += 6\n14:     return True\n15: \n16: def get_primes(limit):\n17:     """Generate a list of prime numbers up to the given limit."""\n18:     primes = []\n19:     for num in range(2, limit + 1)\n20:         if is_prime(num):\n21:             primes.append(num)\n22:     return primes\n23: \n24: def main():\n25:     """Main function to demonstrate prime number generation."""\n26:     limit = 100\n27:     prime_list = get_primes(limit)\n28:     print(f"Prime numbers up to {limit}:")\n29:     print(prime_list)\n30:     print(f"Found {len(prime_list)} prime numbers.")\n31: \n32: if __name__ == "__main__":\n33:     main()',
                  }
              ],
          },
      ],
  )

  print(response)

typescript TypeScript
  const anthropic = new Anthropic();

  const response = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        type: "text_editor_20250728",
        name: "str_replace_based_edit_tool"
      }
    ],
    messages: [
      {
        role: "user",
        content: "There's a syntax error in my primes.py file. Can you help me fix it?"
      },
      {
        role: "assistant",
        content: [
          {
            type: "text",
            text: "I'll help you fix the syntax error in your primes.py file. First, let me take a look at the file to identify the issue."
          },
          {
            type: "tool_use",
            id: "toolu_01AbCdEfGhIjKlMnOpQrStU",
            name: "str_replace_based_edit_tool",
            input: {
              command: "view",
              path: "primes.py"
            }
          }
        ]
      },
      {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: "toolu_01AbCdEfGhIjKlMnOpQrStU",
            content:
              '1: def is_prime(n):\n2:     """Check if a number is prime."""\n3:     if n <= 1:\n4:         return False\n5:     if n <= 3:\n6:         return True\n7:     if n % 2 == 0 or n % 3 == 0:\n8:         return False\n9:     i = 5\n10:     while i * i <= n:\n11:         if n % i == 0 or n % (i + 2) == 0:\n12:             return False\n13:         i += 6\n14:     return True\n15: \n16: def get_primes(limit):\n17:     """Generate a list of prime numbers up to the given limit."""\n18:     primes = []\n19:     for num in range(2, limit + 1)\n20:         if is_prime(num):\n21:             primes.append(num)\n22:     return primes\n23: \n24: def main():\n25:     """Main function to demonstrate prime number generation."""\n26:     limit = 100\n27:     prime_list = get_primes(limit)\n28:     print(f"Prime numbers up to {limit}:")\n29:     print(prime_list)\n30:     print(f"Found {len(prime_list)} prime numbers.")\n31: \n32: if __name__ == "__main__":\n33:     main()'
          }
        ]
      }
    ]
  });

  console.log(response);

csharp C#
  var client = new AnthropicClient();

  var response = await client.Messages.Create(
      new()
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Tools = [new ToolTextEditor20250728()],
          Messages =
          [
              new()
              {
                  Role = Role.User,
                  Content = "There's a syntax error in my primes.py file. Can you help me fix it?",
              },
              new()
              {
                  Role = Role.Assistant,
                  Content = new MessageParamContent(new List<ContentBlockParam>
                  {
                      new ContentBlockParam(new TextBlockParam()
                      {
                          Text = "I'll help you fix the syntax error in your primes.py file. First, let me take a look at the file to identify the issue.",
                      }),
                      new ContentBlockParam(new ToolUseBlockParam()
                      {
                          ID = "toolu_01AbCdEfGhIjKlMnOpQrStU",
                          Name = "str_replace_based_edit_tool",
                          Input = new Dictionary<string, JsonElement>
                          {
                              ["command"] = JsonSerializer.SerializeToElement("view"),
                              ["path"] = JsonSerializer.SerializeToElement("primes.py"),
                          },
                      }),
                  }),
              },
              new()
              {
                  Role = Role.User,
                  Content = new MessageParamContent(new List<ContentBlockParam>
                  {
                      new ContentBlockParam(new ToolResultBlockParam()
                      {
                          ToolUseID = "toolu_01AbCdEfGhIjKlMnOpQrStU",
                          Content = "1: def is_prime(n):\n2:     \"\"\"Check if a number is prime.\"\"\"\n3:     if n <= 1:\n4:         return False\n5:     if n <= 3:\n6:         return True\n7:     if n % 2 == 0 or n % 3 == 0:\n8:         return False\n9:     i = 5\n10:     while i * i <= n:\n11:         if n % i == 0 or n % (i + 2) == 0:\n12:             return False\n13:         i += 6\n14:     return True\n15: \n16: def get_primes(limit):\n17:     \"\"\"Generate a list of prime numbers up to the given limit.\"\"\"\n18:     primes = []\n19:     for num in range(2, limit + 1)\n20:         if is_prime(num):\n21:             primes.append(num)\n22:     return primes\n23: \n24: def main():\n25:     \"\"\"Main function to demonstrate prime number generation.\"\"\"\n26:     limit = 100\n27:     prime_list = get_primes(limit)\n28:     print(f\"Prime numbers up to {limit}:\")\n29:     print(prime_list)\n30:     print(f\"Found {len(prime_list)} prime numbers.\")\n31: \n32: if __name__ == \"__main__\":\n33:     main()",
                      }),
                  }),
              },
          ],
      }
  );

  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{
  		{OfTextEditor20250728: &anthropic.ToolTextEditor20250728Param{}},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("There's a syntax error in my primes.py file. Can you help me fix it?")),
  		anthropic.NewAssistantMessage(
  			anthropic.NewTextBlock("I'll help you fix the syntax error in your primes.py file. First, let me take a look at the file to identify the issue."),
  			anthropic.NewToolUseBlock(
  				"toolu_01AbCdEfGhIjKlMnOpQrStU",
  				map[string]any{"command": "view", "path": "primes.py"},
  				"str_replace_based_edit_tool",
  			),
  		),
  		anthropic.NewUserMessage(
  			anthropic.NewToolResultBlock(
  				"toolu_01AbCdEfGhIjKlMnOpQrStU",
  				"1: def is_prime(n):\n2:     \"\"\"Check if a number is prime.\"\"\"\n3:     if n <= 1:\n4:         return False\n5:     if n <= 3:\n6:         return True\n7:     if n % 2 == 0 or n % 3 == 0:\n8:         return False\n9:     i = 5\n10:     while i * i <= n:\n11:         if n % i == 0 or n % (i + 2) == 0:\n12:             return False\n13:         i += 6\n14:     return True\n15: \n16: def get_primes(limit):\n17:     \"\"\"Generate a list of prime numbers up to the given limit.\"\"\"\n18:     primes = []\n19:     for num in range(2, limit + 1)\n20:         if is_prime(num):\n21:             primes.append(num)\n22:     return primes\n23: \n24: def main():\n25:     \"\"\"Main function to demonstrate prime number generation.\"\"\"\n26:     limit = 100\n27:     prime_list = get_primes(limit)\n28:     print(f\"Prime numbers up to {limit}:\")\n29:     print(prime_list)\n30:     print(f\"Found {len(prime_list)} prime numbers.\")\n31: \n32: if __name__ == \"__main__\":\n33:     main()",
  				false,
  			),
  		),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_5)
    .maxTokens(1024)
    .addTool(ToolTextEditor20250728.builder().build())
    .addUserMessage("There's a syntax error in my primes.py file. Can you help me fix it?")
    .addAssistantMessageOfBlockParams(
      List.of(
        ContentBlockParam.ofText(
          TextBlockParam.builder()
            .text("I'll help you fix the syntax error in your primes.py file. First, let me take a look at the file to identify the issue.")
            .build()
        ),
        ContentBlockParam.ofToolUse(
          ToolUseBlockParam.builder()
            .id("toolu_01AbCdEfGhIjKlMnOpQrStU")
            .name("str_replace_based_edit_tool")
            .input(
              ToolUseBlockParam.Input.builder()
                .putAdditionalProperty("command", JsonValue.from("view"))
                .putAdditionalProperty("path", JsonValue.from("primes.py"))
                .build()
            )
            .build()
        )
      )
    )
    .addUserMessageOfBlockParams(
      List.of(
        ContentBlockParam.ofToolResult(
          ToolResultBlockParam.builder()
            .toolUseId("toolu_01AbCdEfGhIjKlMnOpQrStU")
            .content("1: def is_prime(n):\n2:     \"\"\"Check if a number is prime.\"\"\"\n3:     if n <= 1:\n4:         return False\n5:     if n <= 3:\n6:         return True\n7:     if n % 2 == 0 or n % 3 == 0:\n8:         return False\n9:     i = 5\n10:     while i * i <= n:\n11:         if n % i == 0 or n % (i + 2) == 0:\n12:             return False\n13:         i += 6\n14:     return True\n15: \n16: def get_primes(limit):\n17:     \"\"\"Generate a list of prime numbers up to the given limit.\"\"\"\n18:     primes = []\n19:     for num in range(2, limit + 1)\n20:         if is_prime(num):\n21:             primes.append(num)\n22:     return primes\n23: \n24: def main():\n25:     \"\"\"Main function to demonstrate prime number generation.\"\"\"\n26:     limit = 100\n27:     prime_list = get_primes(limit)\n28:     print(f\"Prime numbers up to {limit}:\")\n29:     print(prime_list)\n30:     print(f\"Found {len(prime_list)} prime numbers.\")\n31: \n32: if __name__ == \"__main__\":\n33:     main()")
            .build()
        )
      )
    )
    .build();

  Message message = client.messages().create(params);
  System.out.println(message);

php PHP
  $client = new Client();

  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: [new ToolTextEditor20250728()],
      messages: [
          [
              'role' => 'user',
              'content' => "There's a syntax error in my primes.py file. Can you help me fix it?",
          ],
          [
              'role' => 'assistant',
              'content' => [
                  [
                      'type' => 'text',
                      'text' => "I'll help you fix the syntax error in your primes.py file. First, let me take a look at the file to identify the issue.",
                  ],
                  [
                      'type' => 'tool_use',
                      'id' => 'toolu_01AbCdEfGhIjKlMnOpQrStU',
                      'name' => 'str_replace_based_edit_tool',
                      'input' => ['command' => 'view', 'path' => 'primes.py'],
                  ],
              ],
          ],
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'tool_result',
                      'tool_use_id' => 'toolu_01AbCdEfGhIjKlMnOpQrStU',
                      'content' => "1: def is_prime(n):\n2:     \"\"\"Check if a number is prime.\"\"\"\n3:     if n <= 1:\n4:         return False\n5:     if n <= 3:\n6:         return True\n7:     if n % 2 == 0 or n % 3 == 0:\n8:         return False\n9:     i = 5\n10:     while i * i <= n:\n11:         if n % i == 0 or n % (i + 2) == 0:\n12:             return False\n13:         i += 6\n14:     return True\n15: \n16: def get_primes(limit):\n17:     \"\"\"Generate a list of prime numbers up to the given limit.\"\"\"\n18:     primes = []\n19:     for num in range(2, limit + 1)\n20:         if is_prime(num):\n21:             primes.append(num)\n22:     return primes\n23: \n24: def main():\n25:     \"\"\"Main function to demonstrate prime number generation.\"\"\"\n26:     limit = 100\n27:     prime_list = get_primes(limit)\n28:     print(f\"Prime numbers up to {limit}:\")\n29:     print(prime_list)\n30:     print(f\"Found {len(prime_list)} prime numbers.\")\n31: \n32: if __name__ == \"__main__\":\n33:     main()",
                  ],
              ],
          ],
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [{type: "text_editor_20250728", name: "str_replace_based_edit_tool"}],
    messages: [
      {
        role: "user",
        content: "There's a syntax error in my primes.py file. Can you help me fix it?"
      },
      {
        role: "assistant",
        content: [
          {
            type: "text",
            text: "I'll help you fix the syntax error in your primes.py file. First, let me take a look at the file to identify the issue."
          },
          {
            type: "tool_use",
            id: "toolu_01AbCdEfGhIjKlMnOpQrStU",
            name: "str_replace_based_edit_tool",
            input: {command: "view", path: "primes.py"}
          }
        ]
      },
      {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: "toolu_01AbCdEfGhIjKlMnOpQrStU",
            content: "1: def is_prime(n):\n2:     \"\"\"Check if a number is prime.\"\"\"\n3:     if n <= 1:\n4:         return False\n5:     if n <= 3:\n6:         return True\n7:     if n % 2 == 0 or n % 3 == 0:\n8:         return False\n9:     i = 5\n10:     while i * i <= n:\n11:         if n % i == 0 or n % (i + 2) == 0:\n12:             return False\n13:         i += 6\n14:     return True\n15: \n16: def get_primes(limit):\n17:     \"\"\"Generate a list of prime numbers up to the given limit.\"\"\"\n18:     primes = []\n19:     for num in range(2, limit + 1)\n20:         if is_prime(num):\n21:             primes.append(num)\n22:     return primes\n23: \n24: def main():\n25:     \"\"\"Main function to demonstrate prime number generation.\"\"\"\n26:     limit = 100\n27:     prime_list = get_primes(limit)\n28:     print(f\"Prime numbers up to {limit}:\")\n29:     print(prime_list)\n30:     print(f\"Found {len(prime_list)} prime numbers.\")\n31: \n32: if __name__ == \"__main__\":\n33:     main()"
          }
        ]
      }
    ]
  )

  puts response

json Output
{
  "id": "msg_01VwXyZAbCdEfGhIjKlMnO",
  "model": "claude-opus-5",
  "stop_reason": "tool_use",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "I found the syntax error in your primes.py file. In the `get_primes` function, there is a missing colon (:) at the end of the for loop line. Let me fix that for you."
    },
    {
      "type": "tool_use",
      "id": "toolu_01PqRsTuVwXyZAbCdEfGh",
      "name": "str_replace_based_edit_tool",
      "input": {
        "command": "str_replace",
        "path": "primes.py",
        "old_str": "    for num in range(2, limit + 1)",
        "new_str": "    for num in range(2, limit + 1):"
      }
    }
  ]
}

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "tools": [
        {
          "type": "text_editor_20250728",
          "name": "str_replace_based_edit_tool"
        }
      ],
      "messages": [
        {
          "role": "assistant",
          "content": [
            {
              "type": "text",
              "text": "I found the syntax error in your primes.py file. In the `get_primes` function, there is a missing colon (:) at the end of the for loop line. Let me fix that for you."
            },
            {
              "type": "tool_use",
              "id": "toolu_01PqRsTuVwXyZAbCdEfGh",
              "name": "str_replace_based_edit_tool",
              "input": {
                "command": "str_replace",
                "path": "primes.py",
                "old_str": "    for num in range(2, limit + 1)",
                "new_str": "    for num in range(2, limit + 1):"
              }
            }
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "tool_result",
              "tool_use_id": "toolu_01PqRsTuVwXyZAbCdEfGh",
              "content": "Successfully replaced text at exactly one location."
            }
          ]
        }
      ]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tools:
    - type: text_editor_20250728
      name: str_replace_based_edit_tool
  messages:
    # Previous messages...
    - role: assistant
      content:
        - type: text
          text: >-
            I found the syntax error in your primes.py file. In the `get_primes`
            function, there is a missing colon (:) at the end of the for loop
            line. Let me fix that for you.
        - type: tool_use
          id: toolu_01PqRsTuVwXyZAbCdEfGh
          name: str_replace_based_edit_tool
          input:
            command: str_replace
            path: primes.py
            old_str: "    for num in range(2, limit + 1)"
            new_str: "    for num in range(2, limit + 1):"
    - role: user
      content:
        - type: tool_result
          tool_use_id: toolu_01PqRsTuVwXyZAbCdEfGh
          content: Successfully replaced text at exactly one location.
  YAML

python Python
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}],
      messages=[
          # Previous messages...
          {
              "role": "assistant",
              "content": [
                  {
                      "type": "text",
                      "text": "I found the syntax error in your primes.py file. In the `get_primes` function, there is a missing colon (:) at the end of the for loop line. Let me fix that for you.",
                  },
                  {
                      "type": "tool_use",
                      "id": "toolu_01PqRsTuVwXyZAbCdEfGh",
                      "name": "str_replace_based_edit_tool",
                      "input": {
                          "command": "str_replace",
                          "path": "primes.py",
                          "old_str": "    for num in range(2, limit + 1)",
                          "new_str": "    for num in range(2, limit + 1):",
                      },
                  },
              ],
          },
          {
              "role": "user",
              "content": [
                  {
                      "type": "tool_result",
                      "tool_use_id": "toolu_01PqRsTuVwXyZAbCdEfGh",
                      "content": "Successfully replaced text at exactly one location.",
                  }
              ],
          },
      ],
  )

  print(response)

typescript TypeScript
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        type: "text_editor_20250728",
        name: "str_replace_based_edit_tool"
      }
    ],
    messages: [
      // Previous messages...
      {
        role: "assistant",
        content: [
          {
            type: "text",
            text: "I found the syntax error in your primes.py file. In the `get_primes` function, there is a missing colon (:) at the end of the for loop line. Let me fix that for you."
          },
          {
            type: "tool_use",
            id: "toolu_01PqRsTuVwXyZAbCdEfGh",
            name: "str_replace_based_edit_tool",
            input: {
              command: "str_replace",
              path: "primes.py",
              old_str: "    for num in range(2, limit + 1)",
              new_str: "    for num in range(2, limit + 1):"
            }
          }
        ]
      },
      {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: "toolu_01PqRsTuVwXyZAbCdEfGh",
            content: "Successfully replaced text at exactly one location."
          }
        ]
      }
    ]
  });

  console.log(response);

csharp C#
  var client = new AnthropicClient();

  var response = await client.Messages.Create(
      new()
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Tools = [new ToolTextEditor20250728()],
          Messages =
          [
              // Previous messages...
              new()
              {
                  Role = Role.Assistant,
                  Content = new MessageParamContent(new List<ContentBlockParam>
                  {
                      new ContentBlockParam(new TextBlockParam()
                      {
                          Text = "I found the syntax error in your primes.py file. In the `get_primes` function, there is a missing colon (:) at the end of the for loop line. Let me fix that for you.",
                      }),
                      new ContentBlockParam(new ToolUseBlockParam()
                      {
                          ID = "toolu_01PqRsTuVwXyZAbCdEfGh",
                          Name = "str_replace_based_edit_tool",
                          Input = new Dictionary<string, JsonElement>
                          {
                              ["command"] = JsonSerializer.SerializeToElement("str_replace"),
                              ["path"] = JsonSerializer.SerializeToElement("primes.py"),
                              ["old_str"] = JsonSerializer.SerializeToElement("    for num in range(2, limit + 1)"),
                              ["new_str"] = JsonSerializer.SerializeToElement("    for num in range(2, limit + 1):"),
                          },
                      }),
                  }),
              },
              new()
              {
                  Role = Role.User,
                  Content = new MessageParamContent(new List<ContentBlockParam>
                  {
                      new ContentBlockParam(new ToolResultBlockParam()
                      {
                          ToolUseID = "toolu_01PqRsTuVwXyZAbCdEfGh",
                          Content = "Successfully replaced text at exactly one location.",
                      }),
                  }),
              },
          ],
      }
  );

  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{
  		{OfTextEditor20250728: &anthropic.ToolTextEditor20250728Param{}},
  	},
  	Messages: []anthropic.MessageParam{
  		// Previous messages...
  		anthropic.NewAssistantMessage(
  			anthropic.NewTextBlock("I found the syntax error in your primes.py file. In the `get_primes` function, there is a missing colon (:) at the end of the for loop line. Let me fix that for you."),
  			anthropic.NewToolUseBlock(
  				"toolu_01PqRsTuVwXyZAbCdEfGh",
  				map[string]any{
  					"command": "str_replace",
  					"path":    "primes.py",
  					"old_str": "    for num in range(2, limit + 1)",
  					"new_str": "    for num in range(2, limit + 1):",
  				},
  				"str_replace_based_edit_tool",
  			),
  		),
  		anthropic.NewUserMessage(
  			anthropic.NewToolResultBlock(
  				"toolu_01PqRsTuVwXyZAbCdEfGh",
  				"Successfully replaced text at exactly one location.",
  				false,
  			),
  		),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_5)
    .maxTokens(1024)
    .addTool(ToolTextEditor20250728.builder().build())
    // Previous messages would go here
    .addAssistantMessageOfBlockParams(
      List.of(
        ContentBlockParam.ofText(
          TextBlockParam.builder()
            .text(
              "I found the syntax error in your primes.py file. In the `get_primes` function, there is a missing colon (:) at the end of the for loop line. Let me fix that for you."
            )
            .build()
        ),
        ContentBlockParam.ofToolUse(
          ToolUseBlockParam.builder()
            .id("toolu_01PqRsTuVwXyZAbCdEfGh")
            .name("str_replace_based_edit_tool")
            .input(
              ToolUseBlockParam.Input.builder()
                .putAdditionalProperty("command", JsonValue.from("str_replace"))
                .putAdditionalProperty("path", JsonValue.from("primes.py"))
                .putAdditionalProperty(
                  "old_str",
                  JsonValue.from("    for num in range(2, limit + 1)")
                )
                .putAdditionalProperty(
                  "new_str",
                  JsonValue.from("    for num in range(2, limit + 1):")
                )
                .build()
            )
            .build()
        )
      )
    )
    .addUserMessageOfBlockParams(
      List.of(
        ContentBlockParam.ofToolResult(
          ToolResultBlockParam.builder()
            .toolUseId("toolu_01PqRsTuVwXyZAbCdEfGh")
            .content("Successfully replaced text at exactly one location.")
            .build()
        )
      )
    )
    .build();

  Message message = client.messages().create(params);
  System.out.println(message);

php PHP
  $client = new Client();

  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: [new ToolTextEditor20250728()],
      messages: [
          // Previous messages...
          [
              'role' => 'assistant',
              'content' => [
                  [
                      'type' => 'text',
                      'text' => 'I found the syntax error in your primes.py file. In the `get_primes` function, there is a missing colon (:) at the end of the for loop line. Let me fix that for you.',
                  ],
                  [
                      'type' => 'tool_use',
                      'id' => 'toolu_01PqRsTuVwXyZAbCdEfGh',
                      'name' => 'str_replace_based_edit_tool',
                      'input' => [
                          'command' => 'str_replace',
                          'path' => 'primes.py',
                          'old_str' => '    for num in range(2, limit + 1)',
                          'new_str' => '    for num in range(2, limit + 1):',
                      ],
                  ],
              ],
          ],
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'tool_result',
                      'tool_use_id' => 'toolu_01PqRsTuVwXyZAbCdEfGh',
                      'content' => 'Successfully replaced text at exactly one location.',
                  ],
              ],
          ],
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [{type: "text_editor_20250728", name: "str_replace_based_edit_tool"}],
    messages: [
      # Previous messages...
      {
        role: "assistant",
        content: [
          {
            type: "text",
            text: "I found the syntax error in your primes.py file. In the `get_primes` function, there is a missing colon (:) at the end of the for loop line. Let me fix that for you."
          },
          {
            type: "tool_use",
            id: "toolu_01PqRsTuVwXyZAbCdEfGh",
            name: "str_replace_based_edit_tool",
            input: {
              command: "str_replace",
              path: "primes.py",
              old_str: "    for num in range(2, limit + 1)",
              new_str: "    for num in range(2, limit + 1):"
            }
          }
        ]
      },
      {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: "toolu_01PqRsTuVwXyZAbCdEfGh",
            content: "Successfully replaced text at exactly one location."
          }
        ]
      }
    ]
  )

  puts response

`json Output
{
  "id": "msg_01IjKlMnOpQrStUvWxYzAb",
  "model": "claude-opus-5",
  "stop_reason": "end_turn",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "I've fixed the syntax error in your primes.py file. The issue was in the `get_primes` function at line 19. There was a missing colon (:) at the end of the for loop line.\n\nHere's what I changed:\n\nFrom:\n```python\nfor num in range(2, limit + 1)\n```\n\nTo:\n```python\nfor num in range(2, limit + 1):\n```\n\nIn Python, a colon is required at the end of statements that start a new code block, such as for loops, if statements, function definitions, etc. Without the colon, Python raises a syntax error because it doesn't know where the code block begins.\n\nYour code should now run correctly. The function will properly generate a list of prime numbers up to the specified limit."
    }
  ]
}
````


## Implement the text editor tool

Source: https://platform.claude.com/llms-full.txt#implement-the-text-editor-tool

The text editor tool is implemented as a schema-less tool. When using this tool, you don't need to provide an input schema as with other tools; the schema is built into Claude's model and can't be modified.

The tool type is `type: "text_editor_20250728"` for Claude 4 and later models.

<Steps>
  <Step title="Initialize your editor implementation">
    Create helper functions to handle file operations like reading, writing, and modifying files. Consider implementing backup functionality to recover from mistakes.
  </Step>

  <Step title="Handle editor tool calls">
    Create a function that processes tool calls from Claude based on the command type:

    <CodeGroup exclude="shell">
      ```python Python
      def handle_editor_tool(tool_call):
          input_params = tool_call.input
          command = input_params.get("command", "")
          file_path = input_params.get("path", "")

          if command == "view":
              # Read and return file contents
              pass
          elif command == "str_replace":
              # Replace text in file
              pass
          elif command == "create":
              # Create new file
              pass
          elif command == "insert":
              # Insert text at location
              pass

typescript TypeScript
      function handleEditorTool(toolCall: { input: { command?: string; path?: string } }): void {
        const inputParams = toolCall.input;
        const command = inputParams.command ?? "";
        const filePath = inputParams.path ?? "";

        if (command === "view") {
          // Read and return file contents
        } else if (command === "str_replace") {
          // Replace text in file
        } else if (command === "create") {
          // Create new file
        } else if (command === "insert") {
          // Insert text at location
        }
      }

csharp C#
      static string HandleEditorTool(IReadOnlyDictionary<string, JsonElement> input)
      {
          input.TryGetValue("command", out var commandEl);
          input.TryGetValue("path", out var pathEl);
          var command = commandEl.ValueKind == JsonValueKind.String ? commandEl.GetString() : null;
          var filePath = pathEl.ValueKind == JsonValueKind.String ? pathEl.GetString() : null;

          if (command == "view")
          {
              // Read and return file contents
          }
          else if (command == "str_replace")
          {
              // Replace text in file
          }
          else if (command == "create")
          {
              // Create new file
          }
          else if (command == "insert")
          {
              // Insert text at location
          }
          return "";
      }

go Go
      func handleEditorTool(input map[string]any) string {
      	command, _ := input["command"].(string)
      	filePath, _ := input["path"].(string)
      // ...

      	switch command {
      	case "view":
      		// Read and return file contents
      	case "str_replace":
      		// Replace text in file
      	case "create":
      		// Create new file
      	case "insert":
      		// Insert text at location
      	}
      	return ""
      }

java Java
      static void handleEditorTool(Map<String, Object> input) {
        var command = (String) input.getOrDefault("command", "");
        var filePath = (String) input.getOrDefault("path", "");

        if (command.equals("view")) {
          // Read and return file contents
        } else if (command.equals("str_replace")) {
          // Replace text in file
        } else if (command.equals("create")) {
          // Create new file
        } else if (command.equals("insert")) {
          // Insert text at location
        }
      }

php PHP
      function handle_editor_tool(array $input): string
      {
          $command = $input['command'] ?? '';
          $filePath = $input['path'] ?? '';

          if ($command === 'view') {
              // Read and return file contents
          } elseif ($command === 'str_replace') {
              // Replace text in file
          } elseif ($command === 'create') {
              // Create new file
          } elseif ($command === 'insert') {
              // Insert text at location
          }
          return '';
      }

ruby Ruby
      def handle_editor_tool(input)
        command = input[:command] || ""
        file_path = input[:path] || ""

        case command
        when "view"
          # Read and return file contents
        when "str_replace"
          # Replace text in file
        when "create"
          # Create new file
        when "insert"
          # Insert text at location
        end
      end

python Python
      # Process tool use in Claude's response
      for content in response.content:
          if content.type == "tool_use":
              # Execute the tool based on command
              result = handle_editor_tool(content)

              # Return result to Claude
              tool_result = {
                  "type": "tool_result",
                  "tool_use_id": content.id,
                  "content": result,
              }

typescript TypeScript
      // Process tool use in Claude's response
      for (const block of response.content) {
        if (block.type === "tool_use") {
          // Execute the tool based on command
          const result = handleEditorTool(block);

          // Return result to Claude
          const toolResult = {
            type: "tool_result",
            tool_use_id: block.id,
            content: result
          };
        }
      }

csharp C#
      // Process tool use in Claude's response
      foreach (var block in response.Content)
      {
          if (block.TryPickToolUse(out var toolUse))
          {
              var result = HandleEditorTool(toolUse.Input);
              var toolResult = new ToolResultBlockParam
              {
                  ToolUseID = toolUse.ID,
                  Content = result,
              };
          }
      }

go Go
      // Process tool use in Claude's response
      for _, block := range response.Content {
      	if block.Type == "tool_use" {
      		var input map[string]any
      		if err := json.Unmarshal(block.Input, &input); err != nil {
      			log.Fatal(err)
      		}
      		result := handleEditorTool(input)

      		toolResult := anthropic.NewToolResultBlock(block.ID, result, false)
      // ...
      	}
      }

java Java
      // Process tool use in Claude's response
      for (var block : response.content()) {
        if (block.type().equals("tool_use")) {
          // Execute the tool based on command
          var result = handleEditorTool(block);

          // Return result to Claude
          var toolResult = Map.of(
            "type", "tool_result",
            "tool_use_id", block.id(),
            "content", result
          );
        }
      }

php PHP
      // Process tool use in Claude's response
      foreach ($response->content as $block) {
          if ($block->type === 'tool_use') {
              // Execute the tool based on command
              $result = handle_editor_tool($block->input);

              // Return result to Claude
              $toolResult = [
                  'type' => 'tool_result',
                  'tool_use_id' => $block->id,
                  'content' => $result,
              ];
          }
      }

ruby Ruby
      # Process tool use in Claude's response
      tool_results = response.content.filter_map do |block|
        next unless block.type == :tool_use

        {type: "tool_result", tool_use_id: block.id, content: handle_editor_tool(block.input)}
      end

json
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
          "content": "Error: File not found",
          "is_error": true
        }
      ]
    }

json
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
          "content": "Error: Found 3 matches for replacement text. Please provide more context to make a unique match.",
          "is_error": true
        }
      ]
    }

json
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
          "content": "Error: No match found for replacement. Please check your text and try again.",
          "is_error": true
        }
      ]
    }

json
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
          "content": "Error: Permission denied. Cannot write to file.",
          "is_error": true
        }
      ]
    }

python Python
      def backup_file(file_path):
          """Create a backup of a file before editing."""
          backup_path = f"{file_path}.backup"
          if os.path.exists(file_path):
              with open(file_path, "r") as src, open(backup_path, "w") as dst:
                  dst.write(src.read())

typescript TypeScript
      async function backupFile(filePath: string): Promise<void> {
        const backupPath = `${filePath}.backup`;
        try {
          await access(filePath);
          await copyFile(filePath, backupPath);
        } catch {
          // File does not exist; nothing to back up
        }
      }

csharp C#
      static void BackupFile(string filePath)
      {
          var backupPath = $"{filePath}.backup";
          if (File.Exists(filePath))
          {
              File.Copy(filePath, backupPath, overwrite: true);
          }
      }

go Go
      func backupFile(filePath string) error {
      	backupPath := filePath + ".backup"
      	data, err := os.ReadFile(filePath)
      	if err != nil {
      		if os.IsNotExist(err) {
      			return nil
      		}
      		return err
      	}
      	return os.WriteFile(backupPath, data, 0o644)
      }

java Java
      static void backupFile(String filePath) throws IOException {
        Path source = Path.of(filePath);
        Path backupPath = Path.of(filePath + ".backup");
        if (Files.exists(source)) {
          Files.copy(source, backupPath, StandardCopyOption.REPLACE_EXISTING);
        }
      }

php PHP
      function backup_file(string $filePath): void
      {
          $backupPath = $filePath . '.backup';
          if (file_exists($filePath)) {
              copy($filePath, $backupPath);
          }
      }

ruby Ruby
      def backup_file(file_path)
        backup_path = "#{file_path}.backup"
        FileUtils.cp(file_path, backup_path) if File.exist?(file_path)
      end

python Python
      def safe_replace(file_path, old_text, new_text):
          """Replace text only if there's exactly one match."""
          with open(file_path, "r") as f:
              content = f.read()

          count = content.count(old_text)
          if count == 0:
              return "Error: No match found"
          elif count > 1:
              return f"Error: Found {count} matches"
          else:
              new_content = content.replace(old_text, new_text)
              with open(file_path, "w") as f:
                  f.write(new_content)
              return "Successfully replaced text"

typescript TypeScript
      async function safeReplace(
        filePath: string,
        oldText: string,
        newText: string
      ): Promise<string> {
        const content = await readFile(filePath, "utf8");

        const count = content.split(oldText).length - 1;
        if (count === 0) {
          return "Error: No match found";
        } else if (count > 1) {
          return `Error: Found ${count} matches`;
        } else {
          const newContent = content.replace(oldText, newText);
          await writeFile(filePath, newContent, "utf8");
          return "Successfully replaced text";
        }
      }

csharp C#
      static string SafeReplace(string filePath, string oldText, string newText)
      {
          var content = File.ReadAllText(filePath);

          var count = content.Split(oldText).Length - 1;
          if (count == 0)
          {
              return "Error: No match found";
          }
          else if (count > 1)
          {
              return $"Error: Found {count} matches";
          }
          else
          {
              var newContent = content.Replace(oldText, newText);
              File.WriteAllText(filePath, newContent);
              return "Successfully replaced text";
          }
      }

go Go
      func safeReplace(filePath, oldText, newText string) string {
      	data, err := os.ReadFile(filePath)
      	if err != nil {
      		return fmt.Sprintf("Error: %v", err)
      	}
      	content := string(data)

      	count := strings.Count(content, oldText)
      	if count == 0 {
      		return "Error: No match found"
      	} else if count > 1 {
      		return fmt.Sprintf("Error: Found %d matches", count)
      	}

      	newContent := strings.Replace(content, oldText, newText, 1)
      	if err := os.WriteFile(filePath, []byte(newContent), 0o644); err != nil {
      		return fmt.Sprintf("Error: %v", err)
      	}
      	return "Successfully replaced text"
      }

java Java
      static String safeReplace(String filePath, String oldText, String newText) throws IOException {
        String content = Files.readString(Path.of(filePath));

        int count = content.split(Pattern.quote(oldText), -1).length - 1;
        if (count == 0) {
          return "Error: No match found";
        } else if (count > 1) {
          return "Error: Found " + count + " matches";
        } else {
          String newContent = content.replace(oldText, newText);
          Files.writeString(Path.of(filePath), newContent);
          return "Successfully replaced text";
        }
      }

php PHP
      function safe_replace(string $filePath, string $oldText, string $newText): string
      {
          $content = file_get_contents($filePath);

          $count = substr_count($content, $oldText);
          if ($count === 0) {
              return 'Error: No match found';
          } elseif ($count > 1) {
              return "Error: Found {$count} matches";
          } else {
              $newContent = str_replace($oldText, $newText, $content);
              file_put_contents($filePath, $newContent);
              return 'Successfully replaced text';
          }
      }

ruby Ruby
      def safe_replace(file_path, old_text, new_text)
        content = File.read(file_path)

        count = content.scan(old_text).length
        if count == 0
          "Error: No match found"
        elsif count > 1
          "Error: Found #{count} matches"
        else
          new_content = content.sub(old_text) { new_text }
          File.write(file_path, new_content)
          "Successfully replaced text"
        end
      end

python Python
      def verify_changes(file_path):
          """Run tests or checks after making changes."""
          try:
              # For Python files, check for syntax errors
              if file_path.endswith(".py"):
                  import ast

                  with open(file_path, "r") as f:
                      ast.parse(f.read())
                  return "Syntax check passed"
          except Exception as e:
              return f"Verification failed: {str(e)}"

typescript TypeScript
      function verifyChanges(filePath: string): string {
        try {
          // For Python files, check for syntax errors
          if (filePath.endsWith(".py")) {
            execFileSync("python3", ["-m", "py_compile", filePath]);
            return "Syntax check passed";
          }
          return "No checks defined for this file type";
        } catch (err) {
          return `Verification failed: ${err}`;
        }
      }

csharp C#
      static string VerifyChanges(string filePath)
      {
          try
          {
              // For Python files, check for syntax errors
              if (filePath.EndsWith(".py"))
              {
                  var psi = new ProcessStartInfo("python3")
                  {
                      RedirectStandardError = true,
                  };
                  psi.ArgumentList.Add("-m");
                  psi.ArgumentList.Add("py_compile");
                  psi.ArgumentList.Add(filePath);
                  using var proc = Process.Start(psi)!;
                  proc.WaitForExit();
                  if (proc.ExitCode != 0)
                  {
                      return $"Verification failed: {proc.StandardError.ReadToEnd()}";
                  }
                  return "Syntax check passed";
              }
              return "No checks defined for this file type";
          }
          catch (Exception e)
          {
              return $"Verification failed: {e.Message}";
          }
      }

go Go
      func verifyChanges(filePath string) string {
      	// For Python files, check for syntax errors
      	if strings.HasSuffix(filePath, ".py") {
      		cmd := exec.Command("python3", "-m", "py_compile", filePath)
      		if out, err := cmd.CombinedOutput(); err != nil {
      			return fmt.Sprintf("Verification failed: %v: %s", err, out)
      		}
      		return "Syntax check passed"
      	}
      	return "No checks defined for this file type"
      }

java Java
      static String verifyChanges(String filePath) {
        try {
          // For Python files, check for syntax errors
          if (filePath.endsWith(".py")) {
            Process proc = new ProcessBuilder("python3", "-m", "py_compile", filePath)
              .redirectErrorStream(true)
              .start();
            if (proc.waitFor() != 0) {
              return "Verification failed: " + new String(proc.getInputStream().readAllBytes());
            }
            return "Syntax check passed";
          }
          return "No checks defined for this file type";
        } catch (IOException | InterruptedException e) {
          return "Verification failed: " + e.getMessage();
        }
      }

php PHP
      function verify_changes(string $filePath): string
      {
          // For Python files, check for syntax errors
          if (str_ends_with($filePath, '.py')) {
              exec('python3 -m py_compile ' . escapeshellarg($filePath) . ' 2>&1', $output, $exitCode);
              if ($exitCode !== 0) {
                  return 'Verification failed: ' . implode("\n", $output);
              }
              return 'Syntax check passed';
          }
          return 'No checks defined for this file type';
      }

ruby Ruby
      def verify_changes(file_path)
        # For Python files, check for syntax errors
        if file_path.end_with?(".py")
          if system("python3", "-m", "py_compile", file_path)
            "Syntax check passed"
          else
            "Verification failed: syntax error in #{file_path}"
          end
        else
          "No checks defined for this file type"
        end
      end
      ```
    </CodeGroup>
  </Accordion>
</AccordionGroup>

***


## Pricing and token usage

Source: https://platform.claude.com/llms-full.txt#pricing-and-token-usage

The text editor tool uses the same pricing structure as other tools used with Claude. It follows the standard input and output token pricing based on the Claude model you're using.

In addition to the base tokens, the following additional input tokens are needed for the text editor tool:

| Tool                                | Additional input tokens |
| ----------------------------------- | ----------------------- |
| `text_editor_20250429` (Claude 4.x) | 700 tokens              |

For more detailed information about tool pricing, see [Tool use pricing](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview#pricing).


## Integrate the text editor tool with other tools

Source: https://platform.claude.com/llms-full.txt#integrate-the-text-editor-tool-with-other-tools

You can use the text editor tool alongside other Claude tools. When combining tools, ensure you:

* Match the tool version with the model you're using
* Account for the additional token usage for all tools included in your request


## Change log

Source: https://platform.claude.com/llms-full.txt#change-log

| Date             | Version                | Changes                                                                                                                                                                                                                                                                                                                  |
| ---------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| July 28, 2025    | `text_editor_20250728` | Release of an updated text editor tool that fixes some issues and adds an optional `max_characters` parameter. It is otherwise identical to `text_editor_20250429`.                                                                                                                                                      |
| April 29, 2025   | `text_editor_20250429` | Release of the text editor tool for Claude 4. This version removes the `undo_edit` command but maintains all other capabilities. The tool name has been updated to reflect its str\_replace-based architecture.                                                                                                          |
| March 13, 2025   | `text_editor_20250124` | Introduction of standalone text editor tool documentation. This version is optimized for Claude Sonnet 3.7 but has identical capabilities to the previous version.                                                                                                                                                       |
| October 22, 2024 | `text_editor_20241022` | Initial release of the text editor tool with Claude Sonnet 3.5 (retired; see [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)). Provides capabilities for viewing, creating, and editing files through the `view`, `create`, `str_replace`, `insert`, and `undo_edit` commands. |


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-36

Here are some ideas for how to use the text editor tool in more convenient and powerful ways:

* **Integrate with your development workflow**: Build the text editor tool into your development tools or IDE
* **Create a code review system**: Have Claude review your code and make improvements
* **Build a debugging assistant**: Create a system where Claude can help you diagnose and fix issues in your code
* **Implement file format conversion**: Let Claude help you convert files from one format to another
* **Automate documentation**: Set up workflows for Claude to automatically document your code

The text editor tool enables Claude to work directly with your code base, supporting workflows from debugging to automated documentation.

<CardGroup cols={3}>
  <Card title="Tool use overview" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview">
    Learn how to implement tool workflows for use with Claude.
  </Card>

  <Card title="Bash tool" icon="terminal" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool">
    Execute shell commands with Claude.
  </Card>
</CardGroup>


---
title: Tool runner (SDK)
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner
description: Use the SDK's tool runner to handle the agentic loop, error wrapping, and type safety automatically.
---

The tool runner handles the agentic loop, error wrapping, and type safety so you don't have to. When you need human-in-the-loop approval, custom logging, or conditional execution, use the [manual loop](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) instead.

Instead of manually handling tool calls, tool results, and conversation management, the tool runner automatically:

* Runs tools when Claude calls them
* Handles the request/response cycle
* Manages conversation state
* Provides type safety and validation

<Note>
  The tool runner is in beta and available in the [Python SDK](https://github.com/anthropics/anthropic-sdk-python/blob/main/tools.md), [TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript/blob/main/helpers.md#tool-helpers), [C# SDK](https://github.com/anthropics/anthropic-sdk-csharp/blob/main/examples/ToolRunnerExample/Program.cs), [Go SDK](https://github.com/anthropics/anthropic-sdk-go/blob/main/tools.md), [Java SDK](https://github.com/anthropics/anthropic-sdk-java/blob/main/anthropic-java-example/src/main/java/com/anthropic/example/BetaToolRunnerExample.java), [PHP SDK](https://github.com/anthropics/anthropic-sdk-php/blob/main/examples/beta/beta_tool_runner.php), and [Ruby SDK](https://github.com/anthropics/anthropic-sdk-ruby/blob/main/helpers.md#3-auto-looping-tool-runner-beta).
</Note>


## Basic usage

Source: https://platform.claude.com/llms-full.txt#basic-usage-3

Define tools using the SDK helpers, then use the tool runner to run them.

Depending on the SDK's tool signature, a tool returns its result as a string or as content blocks (text, image, or document blocks), so a tool can return multimodal results. A returned string becomes a single text content block. To return structured data, such as a JSON object or a number, encode it as a string first.

<Tabs>
  <Tab title="Python">
    Use the `@beta_tool` decorator to define tools with type hints and docstrings.

    <Note>
      If you're using the async client, replace `@beta_tool` with `@beta_async_tool` and define the function with `async def`.
    </Note>

The `@beta_tool` decorator inspects the function arguments and docstring to derive the JSON schema for you.
  </Tab>

  <Tab title="TypeScript">
    Use `betaZodTool()` for type-safe tool definitions with Zod validation, or `betaTool()` for JSON Schema-based definitions.

    TypeScript offers two approaches for defining tools:

    **Using Zod (recommended)** - Use `betaZodTool()` for type-safe tool definitions with Zod validation (requires Zod 3.25.0 or higher):

**Using JSON Schema** - Use `betaTool()` for type-safe tool definitions without Zod:

    <Note>
      The input generated by Claude is not validated at runtime. Perform validation inside the `run` function if needed.
    </Note>

</Tab>

  <Tab title="C#">
    Define each tool as a `BetaRunnableTool`, providing a `Definition` with a JSON schema and a `Run` delegate that runs when Claude calls the tool.

</Tab>

  <Tab title="Go">
    Define a tool with `toolrunner.NewBetaToolFromJSONSchema`. The handler's input type is a struct with `jsonschema:` tags. The SDK reflects on it to generate the JSON schema.

The `jsonschema:` struct tags generate the input schema. For example, `CalculateSumInput` becomes:

</Tab>

  <Tab title="Java">
    Define each tool as a class implementing `Supplier<String>`. Annotate the class with `@JsonClassDescription` for the tool description, and each public field with `@JsonPropertyDescription` for parameter descriptions. The SDK derives the JSON schema, tool name (snake-cased class name), and input parsing from the class, and marks the tool with `strict: true` ([strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use)).

The class name `CalculateSum` becomes the tool name `calculate_sum`, and the SDK generates a JSON schema from the annotated fields:

</Tab>

  <Tab title="PHP">
    Define each tool as a `BetaRunnableTool` that pairs the tool's JSON schema definition with a closure that runs it.

</Tab>

  <Tab title="Ruby">
    Use the `Anthropic::BaseTool` class to define tools with typed input schemas.

The `Anthropic::BaseTool` class uses the `doc` method for the tool description and `input_schema` to define the expected parameters. The SDK automatically converts this to the appropriate JSON schema format.
  </Tab>
</Tabs>


## Iterating over the tool runner

Source: https://platform.claude.com/llms-full.txt#iterating-over-the-tool-runner

The tool runner is an iterable that yields messages from Claude. On each iteration, the runner checks whether Claude requested a tool use. If so, it runs the tool and sends the result back to Claude automatically, then yields the next message from Claude to continue your loop.

You can end the loop at any iteration with a `break` statement. The runner loops until Claude returns a message without a tool use, or until it reaches `max_iterations` if you set it.

If you don't need intermediate messages, you can get the final message directly:

<Tabs>
  <Tab title="Python">
    Use `runner.until_done()` to get the final message.

</Tab>

  <Tab title="TypeScript">
    `await` the runner to get the final message.

</Tab>

  <Tab title="C#">
    Use `runner.RunUntilDoneAsync()` to get the final message.

</Tab>

  <Tab title="Go">
    Use `runner.RunToCompletion(ctx)` to get the final message.

</Tab>

  <Tab title="Java">
    The Java SDK has no `until_done()` shortcut. Iterate to exhaustion and keep the last message.

</Tab>

  <Tab title="PHP">
    Use `runUntilDone()` to get the final message.

</Tab>

  <Tab title="Ruby">
    Use `runner.run_until_finished` to get all messages.

</Tab>
</Tabs>


## Advanced usage

Source: https://platform.claude.com/llms-full.txt#advanced-usage-2

Within the loop, you can read each response message and modify the runner's state before the next API call. Each iteration follows this lifecycle:

1. The runner sends a request to the Messages API with its current state.

2. The runner yields the response message to your loop body.

3. Your loop body runs. You can read the message and optionally modify the runner's state.

4. When your loop body returns, the runner checks whether you modified its message history.

   * **If you did not modify message history:** If the message contains tool calls, the runner appends the assistant message and the tool results, then continues. If there are no tool calls, the loop exits.
   * **If you modified message history:** The runner skips its automatic append and uses your state unchanged. See [Taking over message history](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner#taking-over-message-history).

### Taking over message history

By default, the runner manages conversation state for you: after each tool-call turn, it appends the assistant message and any tool results to its own message history. You take over message history when you want to retry a turn (discard the response and resend), inject a follow-up message, or build the tool result yourself.

You take over by modifying the runner's messages from inside the loop body. The exact method depends on the SDK. See the per-language tabs that follow.

When you take over for an iteration, the runner does not append the assistant message or tool results from that turn. You become responsible for keeping the conversation valid: append the assistant message and a tool result yourself (if you want the turn to count), modify state conditionally so the loop can still exit when there are no tool calls, and pass `max_iterations` to bound the loop. All seven SDKs support `max_iterations`.

<Tabs>
  <Tab title="Python">
    Use `generate_tool_call_response()` to inspect or compute the tool result. Calling `append_messages()` inside the loop tells the runner you're managing history yourself, so include the assistant message and tool result in what you append.

To change request parameters such as `max_tokens` without taking over message history, use `set_messages_params()`. The runner still appends the assistant message and tool result automatically.

</Tab>

  <Tab title="TypeScript">
    Use `runner.params` to read the current request parameters and `setMessagesParams()` to replace them. Calling `setMessagesParams()` or `pushMessages()` inside the loop tells the runner you're managing state yourself: the assistant message and tool result from this iteration are dropped, and the next request goes out with your state.

    The following example retries a truncated response with a larger `max_tokens` budget.

</Tab>

  <Tab title="C#">
    Calling `SetParams()` or `PushMessages()` flags state as modified, which causes the runner to skip its auto-append for that turn. The C# runner still runs the matched tools for that turn and discards their auto-built results, so a tool you also run yourself inside the loop body runs twice unless you account for it. When you take over, push the assistant message and a tool result yourself. Otherwise the conversation won't make forward progress. The C# runner always exits when a response has no tool calls, so condition any state mutation on the presence of a `tool_use` block.

</Tab>

  <Tab title="Go">
    The Go runner exposes parameters as a public `Params` field. Modifying `runner.Params` between calls to `NextMessage(ctx)` applies to the next API request. Unlike other SDKs, the Go runner always appends the assistant message and tool results unconditionally. Modifying `Params` does not suppress that step.

</Tab>

  <Tab title="Java">
    Use `runner.params()` to read the current parameters and `runner.setNextParams()` to replace them for the next iteration. When you call `setNextParams()` inside the loop, the runner skips its automatic append. The just-yielded message is discarded, and the next iteration sends your new params unchanged.

    The following example retries a turn that hit the token limit by doubling `max_tokens`. Mutating only on the `max_tokens` branch keeps the loop converging: turns that complete normally fall through, and the runner auto-appends and exits when there are no more tool calls.

</Tab>

  <Tab title="PHP">
    Use `setMessagesParams()` and `pushMessages()` to modify the runner's state, and `getParams()` to read it. Calling either setter inside the loop tells the runner to skip its automatic append, so the conversation continues from your modified state instead.

    The following example doubles `max_tokens` and retries when a response is cut off.

</Tab>

  <Tab title="Ruby">
    Use `next_message` for step-by-step control. By the time `next_message` returns, the assistant message and tool result for that turn are already appended. Use `feed_messages` to inject follow-up messages between turns, and `runner.params.update(...)` to change request parameters in place.

    You take over message history when, from inside an `each_message` or `each_streaming` block, you reassign `runner.params[:messages]` or call `feed_messages`. The following pattern calls `feed_messages` between `next_message` calls, which does not take over.

</Tab>
</Tabs>

### Automatic context management

For long-running agentic tasks, the TypeScript and Ruby tool runners support automatic [compaction](https://platform.claude.com/docs/en/build-with-claude/context-editing#client-side-compaction-sdk), which generates summaries when token usage exceeds a threshold so the conversation can continue beyond context window limits. Both SDKs have deprecated this client-side option in favor of [server-side compaction](https://platform.claude.com/docs/en/build-with-claude/compaction), which works with every SDK's tool runner through the `context_management` request parameter. The Python SDK (v1.0 and later) and the Go, Java, C#, and PHP tool runners don't include client-side compaction.

### Debugging tool execution

When a tool throws an exception, the tool runner catches it and returns the error to Claude as a tool result with `is_error: true`. The tool result carries the exception's message (in Python, its type and message), not the full stack trace.

What the SDK logs is language-specific. The Python SDK logs the full exception, including its stack trace, through the standard `logging` module whenever a tool raises an unhandled exception. The Python, TypeScript, and Java SDKs read the `ANTHROPIC_LOG` environment variable to turn on the SDK's logging, which includes request and response detail:

The Go, Ruby, C#, and PHP SDKs don't read `ANTHROPIC_LOG`. Outside Python, no SDK logs a failed tool: to see why a tool failed, catch and log the exception inside the tool function before returning or rethrowing it.

### Intercepting tool errors

By default, tool errors are passed back to Claude, which can then respond appropriately. However, you might want to detect errors and handle them differently, for example, to stop execution early or implement custom error handling.

In the Python and TypeScript SDKs, use the tool response method (`generate_tool_call_response()` in Python, `generateToolResponse()` in TypeScript) to intercept tool results and check for errors before they're sent to Claude. The other SDKs don't expose that hook. Their tabs describe the closest alternative:

<Tabs>
  <Tab title="Python">

</Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="C#">
    The C# tool runner doesn't expose a hook for inspecting the tool result before it's sent to Claude. To control error content, throw `BetaToolError` from inside the tool body. The runner converts it to a `tool_result` with `is_error: true` and the content you supply.

</Tab>

  <Tab title="Go">
    Intercepting tool errors before they're sent to Claude is not currently supported in the Go SDK. The runner converts an error returned from your handler into a tool result with `is_error: true` internally. To customize the error content, catch the error inside your handler and return a result instead of returning the error.
  </Tab>

  <Tab title="Java">
    Intercepting tool errors before they're sent to Claude is not currently supported in the Java SDK. The runner catches any exception thrown from a tool's `get()` method and converts it into a tool result with `is_error: true` automatically. To control the error content, catch the exception inside your tool and return a custom string.
  </Tab>

  <Tab title="PHP">
    The PHP tool runner does not currently expose tool results before they are appended. Exceptions thrown from a tool's `run` closure are caught and sent to Claude as tool results with `is_error: true` automatically. To inspect or replace error content, use the manual `pushMessages()` pattern shown in [Modifying tool results](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner#modifying-tool-results).
  </Tab>

  <Tab title="Ruby">

</Tab>
</Tabs>

### Modifying tool results

You can modify tool results before they're sent back to Claude. This is useful for adding metadata such as `cache_control` to enable [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) on tool results, or for transforming the tool output.

In the Python and TypeScript SDKs, use the tool response method to get the tool result, then modify it before the runner proceeds. Whether you explicitly append the modified result or mutate it in place depends on the SDK. See the code comments in each tab.

<Tabs>
  <Tab title="Python">

</Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="C#">
    Modifying tool results before they're appended (for example, to add `cache_control`) is not currently supported in the C# SDK. The runner constructs the `tool_result` block internally and provides no hook to alter it.
  </Tab>

  <Tab title="Go">
    The Go runner does not expose a hook to modify the outer `tool_result` block. You can, however, set `cache_control` on the inner content blocks your handler returns.

</Tab>

  <Tab title="Java">
    To set `cache_control` on a tool result, return `BetaToolResultBlockParam.Content` from the tool instead of `String` and set `cacheControl` on the inner text block. The runner does not currently support setting `cache_control` on the outer `tool_result` block.

</Tab>

  <Tab title="PHP">
    The PHP tool runner has no callback to mutate the auto-generated `tool_result` block. To add fields such as `cache_control`, build the tool result yourself and push it. Calling `pushMessages()` skips the runner's auto-append for that turn.

</Tab>

  <Tab title="Ruby">

</Tab>
</Tabs>

<Tip>
  Adding `cache_control` to tool results is particularly useful when tools return large amounts of data (such as document search results) that you want to cache for subsequent API calls. See [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) for more details on caching strategies.
</Tip>


## Streaming

Source: https://platform.claude.com/llms-full.txt#streaming-3

Enable streaming to process each turn's response incrementally. Each iteration yields a stream object that you can iterate for events.

<Tabs>
  <Tab title="Python">
    Set `stream=True` and use `get_final_message()` to get the accumulated message.

</Tab>

  <Tab title="TypeScript">
    Set `stream: true` and use `finalMessage()` to get the accumulated message.

</Tab>

  <Tab title="C#">
    Call `runner.Streaming()` to get a nested async sequence: one inner stream for each API call.

</Tab>

  <Tab title="Go">
    Use `NewToolRunnerStreaming` and iterate `runner.AllStreaming(ctx)`. Each outer iteration yields a stream of events for one API call.

</Tab>

  <Tab title="Java">
    Call `runner.streaming()` to get a stream for each turn. Each `StreamResponse` must be closed after use.

</Tab>

  <Tab title="PHP">
    Streaming is not currently available with the PHP tool runner.
  </Tab>

  <Tab title="Ruby">
    Use `each_streaming` to iterate over streaming events.

</Tab>
</Tabs>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-37

<CardGroup cols={2}>
  <Card title="Strict tool use" icon="check" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use">
    Enforce JSON Schema compliance on Claude's tool inputs with grammar-constrained sampling.
  </Card>

  <Card title="Handle tool calls" icon="arrows-left-right" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls">
    Parse `tool_use` blocks, format `tool_result` responses, and handle errors with `is_error`.
  </Card>

  <Card title="Parallel tool use" icon="grid" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use">
    Enable, format, and disable parallel tool calls, with message-history guidance and troubleshooting.
  </Card>

  <Card title="Define tools" icon="hammer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools">
    Specify tool schemas, write effective descriptions, and control when Claude calls your tools.
  </Card>
</CardGroup>


---
title: Tool search tool
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool
description: Scale to hundreds or thousands of tools by letting Claude search your tool catalog and load only the tools it needs.
---

The tool search tool lets Claude work with hundreds or thousands of tools by discovering and loading them on demand. Instead of loading all tool definitions into the context window up front, Claude searches your tool catalog (including tool names, descriptions, argument names, and argument descriptions) and loads only the tools it needs.

Loading every tool definition up front causes two problems as a tool library grows:

* **Context bloat:** A typical multiserver setup (GitHub, Slack, Sentry, Grafana, and Splunk) can consume \~55k tokens in definitions before Claude does any work. Tool search typically reduces this by over 85 percent, loading only the 3–5 tools Claude needs for a given request.
* **Tool selection accuracy:** Claude's ability to pick the right tool degrades once you exceed 30–50 available tools. Because tool search loads only a focused set of relevant tools on demand, selection accuracy stays high even across thousands of tools.

For the models that support tool search, see [Model compatibility](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#model-compatibility).

<Tip>
  For background on the scaling challenges that tool search solves, see [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use). Tool search's on-demand loading is also an instance of the broader just-in-time retrieval principle described in [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
</Tip>

Tool search runs as a server-side tool, but you can also implement your own client-side tool search. See [Custom tool search implementation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#custom-tool-search-implementation) for details.

<Note>
  Share feedback on this feature through the [feedback form](https://forms.gle/MhcGFFwLxuwnWTkYA).
</Note>

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

<Warning>
  On Amazon Bedrock, server-side tool search is available only through the [InvokeModel API](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-runtime_example_bedrock-runtime_InvokeModel_AnthropicClaude_section.html), not the Converse API.
</Warning>

<Note>
  On [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), server-side tool search works identically to the Claude API. Claude Platform on AWS uses the Anthropic Messages API directly, so there is no InvokeModel or Converse distinction.
</Note>


## Model compatibility

Source: https://platform.claude.com/llms-full.txt#model-compatibility-2

Both tool search variants are available on the following models:

| Model                                          | Tool versions                                                       |
| ---------------------------------------------- | ------------------------------------------------------------------- |
| Claude Fable 5.1 (claude-fable-5-1)            | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |
| Claude Mythos 5.1 (claude-mythos-5-1)          | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |
| Claude Fable 5 (claude-fable-5)                | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |
| Claude Mythos 5 (claude-mythos-5)              | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |
| Claude Opus 5 (claude-opus-5)                  | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |
| Claude Opus 4.8 (claude-opus-4-8)              | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |
| Claude Opus 4.7 (claude-opus-4-7)              | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |
| Claude Opus 4.6 (claude-opus-4-6)              | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |
| Claude Sonnet 4.6 (claude-sonnet-4-6)          | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |
| Claude Opus 4.5 (claude-opus-4-5-20251101)     | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |
| Claude Sonnet 4.5 (claude-sonnet-4-5-20250929) | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |
| Claude Haiku 4.5 (claude-haiku-4-5-20251001)   | `tool_search_tool_regex_20251119`, `tool_search_tool_bm25_20251119` |

Claude Opus 4.1 and earlier models don't support the tool search tool.


## How tool search works

Source: https://platform.claude.com/llms-full.txt#how-tool-search-works

There are two tool search variants:

* **Regex** (`tool_search_tool_regex_20251119`): Claude constructs regex patterns to search for tools.
* **BM25** (`tool_search_tool_bm25_20251119`): Claude uses natural language queries to search for tools.

When you enable the tool search tool:

1. You include a tool search tool (for example, `tool_search_tool_regex_20251119` or `tool_search_tool_bm25_20251119`) in your `tools` list.
2. You provide every tool definition in the `tools` array and set `defer_loading: true` on the tools that shouldn't load up front. At least one tool, normally the tool search tool itself, must stay non-deferred.
3. Initially, Claude's context contains only the tool search tool and any non-deferred tools.
4. When Claude needs additional tools, it searches using a tool search tool.
5. The API runs the search and returns the matching tools as `tool_reference` blocks (up to 5 by default; Claude can set a `limit` in its search input).
6. The API automatically expands these references into full tool definitions.
7. Claude selects from the discovered tools and calls them.


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-7

The following example includes the tool search tool and two deferred tools:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d '{
          "model": "claude-opus-5",
          "max_tokens": 2048,
          "messages": [
              {
                  "role": "user",
                  "content": "What is the weather in San Francisco?"
              }
          ],
          "tools": [
              {
                  "type": "tool_search_tool_regex_20251119",
                  "name": "tool_search_tool_regex"
              },
              {
                  "name": "get_weather",
                  "description": "Get the weather at a specific location",
                  "input_schema": {
                      "type": "object",
                      "properties": {
                          "location": {"type": "string"},
                          "unit": {
                              "type": "string",
                              "enum": ["celsius", "fahrenheit"]
                          }
                      },
                      "required": ["location"]
                  },
                  "defer_loading": true
              },
              {
                  "name": "search_files",
                  "description": "Search through files in the workspace",
                  "input_schema": {
                      "type": "object",
                      "properties": {
                          "query": {"type": "string"},
                          "file_types": {
                              "type": "array",
                              "items": {"type": "string"}
                          }
                      },
                      "required": ["query"]
                  },
                  "defer_loading": true
              }
          ]
      }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 2048
  messages:
    - role: user
      content: What is the weather in San Francisco?
  tools:
    - type: tool_search_tool_regex_20251119
      name: tool_search_tool_regex
    - name: get_weather
      description: Get the weather at a specific location
      input_schema:
        type: object
        properties:
          location:
            type: string
          unit:
            type: string
            enum: [celsius, fahrenheit]
        required: [location]
      defer_loading: true
    - name: search_files
      description: Search through files in the workspace
      input_schema:
        type: object
        properties:
          query:
            type: string
          file_types:
            type: array
            items:
              type: string
        required: [query]
      defer_loading: true
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=2048,
      messages=[{"role": "user", "content": "What is the weather in San Francisco?"}],
      tools=[
          {"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"},
          {
              "name": "get_weather",
              "description": "Get the weather at a specific location",
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "location": {"type": "string"},
                      "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                  },
                  "required": ["location"],
              },
              "defer_loading": True,
          },
          {
              "name": "search_files",
              "description": "Search through files in the workspace",
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "query": {"type": "string"},
                      "file_types": {"type": "array", "items": {"type": "string"}},
                  },
                  "required": ["query"],
              },
              "defer_loading": True,
          },
      ],
  )

  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 2048,
    messages: [
      {
        role: "user",
        content: "What is the weather in San Francisco?"
      }
    ],
    tools: [
      {
        type: "tool_search_tool_regex_20251119",
        name: "tool_search_tool_regex"
      },
      {
        name: "get_weather",
        description: "Get the weather at a specific location",
        input_schema: {
          type: "object" as const,
          properties: {
            location: { type: "string" },
            unit: {
              type: "string",
              enum: ["celsius", "fahrenheit"]
            }
          },
          required: ["location"]
        },
        defer_loading: true
      },
      {
        name: "search_files",
        description: "Search through files in the workspace",
        input_schema: {
          type: "object" as const,
          properties: {
            query: { type: "string" },
            file_types: {
              type: "array",
              items: { type: "string" }
            }
          },
          required: ["query"]
        },
        defer_loading: true
      }
    ]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 2048,
      Messages = [
          new() {
              Role = Role.User,
              Content = "What is the weather in San Francisco?"
          }
      ],
      Tools = [
          new ToolUnion(new ToolSearchToolRegex20251119
          {
              Type = ToolSearchToolRegex20251119Type.ToolSearchToolRegex20251119
          }),
          new ToolUnion(new Tool()
          {
              Name = "get_weather",
              Description = "Get the weather at a specific location",
              InputSchema = new InputSchema()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["location"] = JsonSerializer.SerializeToElement(new { type = "string" }),
                      ["unit"] = JsonSerializer.SerializeToElement(new { type = "string", @enum = new[] { "celsius", "fahrenheit" } }),
                  },
                  Required = ["location"],
              },
              DeferLoading = true,
          }),
          new ToolUnion(new Tool()
          {
              Name = "search_files",
              Description = "Search through files in the workspace",
              InputSchema = new InputSchema()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["query"] = JsonSerializer.SerializeToElement(new { type = "string" }),
                      ["file_types"] = JsonSerializer.SerializeToElement(new { type = "array", items = new { type = "string" } }),
                  },
                  Required = ["query"],
              },
              DeferLoading = true,
          }),
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 2048,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What is the weather in San Francisco?")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfToolSearchToolRegex20251119: &anthropic.ToolSearchToolRegex20251119Param{
  			Type: anthropic.ToolSearchToolRegex20251119TypeToolSearchToolRegex20251119,
  		}},
  		{OfTool: &anthropic.ToolParam{
  			Name:        "get_weather",
  			Description: anthropic.String("Get the weather at a specific location"),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"location": map[string]any{"type": "string"},
  					"unit": map[string]any{
  						"type": "string",
  						"enum": []string{"celsius", "fahrenheit"},
  					},
  				},
  				Required: []string{"location"},
  			},
  			DeferLoading: anthropic.Bool(true),
  		}},
  		{OfTool: &anthropic.ToolParam{
  			Name:        "search_files",
  			Description: anthropic.String("Search through files in the workspace"),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"query":      map[string]any{"type": "string"},
  					"file_types": map[string]any{"type": "array", "items": map[string]any{"type": "string"}},
  				},
  				Required: []string{"query"},
  			},
  			DeferLoading: anthropic.Bool(true),
  		}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  import com.anthropic.models.messages.ToolSearchToolRegex20251119;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      InputSchema weatherSchema = InputSchema.builder()
          .properties(JsonValue.from(Map.of(
              "location", Map.of("type", "string"),
              "unit", Map.of(
                  "type", "string",
                  "enum", List.of("celsius", "fahrenheit")
              )
          )))
          .putAdditionalProperty("required", JsonValue.from(List.of("location")))
          .build();

      InputSchema searchSchema = InputSchema.builder()
          .properties(JsonValue.from(Map.of(
              "query", Map.of("type", "string"),
              "file_types", Map.of(
                  "type", "array",
                  "items", Map.of("type", "string")
              )
          )))
          .putAdditionalProperty("required", JsonValue.from(List.of("query")))
          .build();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(2048L)
          .addUserMessage("What is the weather in San Francisco?")
          .addTool(ToolSearchToolRegex20251119.builder()
              .type(ToolSearchToolRegex20251119.Type.TOOL_SEARCH_TOOL_REGEX_20251119)
              .build())
          .addTool(Tool.builder()
              .name("get_weather")
              .description("Get the weather at a specific location")
              .inputSchema(weatherSchema)
              .deferLoading(true)
              .build())
          .addTool(Tool.builder()
              .name("search_files")
              .description("Search through files in the workspace")
              .inputSchema(searchSchema)
              .deferLoading(true)
              .build())
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 2048,
      messages: [
          ['role' => 'user', 'content' => 'What is the weather in San Francisco?'],
      ],
      model: 'claude-opus-5',
      tools: [
          [
              'type' => 'tool_search_tool_regex_20251119',
              'name' => 'tool_search_tool_regex',
          ],
          [
              'name' => 'get_weather',
              'description' => 'Get the weather at a specific location',
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'location' => ['type' => 'string'],
                      'unit' => [
                          'type' => 'string',
                          'enum' => ['celsius', 'fahrenheit'],
                      ],
                  ],
                  'required' => ['location'],
              ],
              'defer_loading' => true,
          ],
          [
              'name' => 'search_files',
              'description' => 'Search through files in the workspace',
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'query' => ['type' => 'string'],
                      'file_types' => [
                          'type' => 'array',
                          'items' => ['type' => 'string'],
                      ],
                  ],
                  'required' => ['query'],
              ],
              'defer_loading' => true,
          ],
      ],
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 2048,
    messages: [
      { role: "user", content: "What is the weather in San Francisco?" }
    ],
    tools: [
      {
        type: "tool_search_tool_regex_20251119",
        name: "tool_search_tool_regex"
      },
      {
        name: "get_weather",
        description: "Get the weather at a specific location",
        input_schema: {
          type: "object",
          properties: {
            location: { type: "string" },
            unit: {
              type: "string",
              enum: ["celsius", "fahrenheit"]
            }
          },
          required: ["location"]
        },
        defer_loading: true
      },
      {
        name: "search_files",
        description: "Search through files in the workspace",
        input_schema: {
          type: "object",
          properties: {
            query: { type: "string" },
            file_types: {
              type: "array",
              items: { type: "string" }
            }
          },
          required: ["query"]
        },
        defer_loading: true
      }
    ]
  )

  puts message
  ```
</CodeGroup>

Claude searches the catalog, discovers `get_weather`, and calls it. The response ends with `stop_reason: "tool_use"`. Execute the discovered tool and return a `tool_result` as in [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls). [Response format](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#response-format) shows the blocks you get back and what to send next.


## Tool definition

Source: https://platform.claude.com/llms-full.txt#tool-definition-2

The tool search tool has two variants:

```json JSON
{
  "type": "tool_search_tool_regex_20251119",
  "name": "tool_search_tool_regex"
}

json JSON
{
  "type": "tool_search_tool_bm25_20251119",
  "name": "tool_search_tool_bm25"
}

json JSON
{
  "name": "get_weather",
  "description": "Get current weather for a location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": { "type": "string" },
      "unit": { "type": "string", "enum": ["celsius", "fahrenheit"] }
    },
    "required": ["location"]
  },
  "defer_loading": true
}
```

`defer_loading` controls what enters the context window, not what you send in the request:

* You still send every tool's full definition in the `tools` array on every request, including the deferred ones. The API needs them server-side to run the search and expand `tool_reference` blocks.
* Tools without `defer_loading` load into context immediately.
* Tools with `defer_loading: true` load only when Claude discovers them through search.
* Never set `defer_loading: true` on the tool search tool itself.
* Keep your 3–5 most frequently used tools non-deferred so Claude can call them without searching first.

The computer use and browser use toolsets (`computer_toolset_20260801` and `browser_toolset_20260801`) take `defer_loading` per member tool inside the entry's `configs` object, not on the entry itself; a request that sets it at the entry level is rejected. Because a toolset defers and expands as a unit, `defer_loading` must resolve to the same value on every enabled member, and when Claude discovers the toolset through search, every enabled member loads at once. See [Client toolsets](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets) for the `configs` format.

Both tool search variants (`regex` and `bm25`) search tool names, descriptions, argument names, and argument descriptions.

Internally, the API excludes deferred tools from the system-prompt prefix. When Claude discovers a deferred tool through tool search, the API appends a `tool_reference` block inline in the conversation, then expands it into the full tool definition before passing it to Claude. The prefix is untouched, so prompt caching is preserved. The grammar for [strict mode](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) (the rules that constrain tool-call output to match your schemas) builds from the full toolset, so `defer_loading` and strict mode compose without grammar recompilation.


## Response format

Source: https://platform.claude.com/llms-full.txt#response-format-2

When Claude uses the tool search tool, the response includes the following block types:

```json JSON
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "I'll search for tools to help with the weather information."
    },
    {
      "type": "server_tool_use",
      "id": "srvtoolu_01ABC123",
      "name": "tool_search_tool_regex",
      "input": {
        "pattern": "weather",
        "limit": 10
      }
    },
    {
      "type": "tool_search_tool_result",
      "tool_use_id": "srvtoolu_01ABC123",
      "content": {
        "type": "tool_search_tool_search_result",
        "tool_references": [{ "type": "tool_reference", "tool_name": "get_weather" }]
      }
    },
    {
      "type": "text",
      "text": "I found a weather tool. Let me get the weather for San Francisco."
    },
    {
      "type": "tool_use",
      "id": "toolu_01XYZ789",
      "name": "get_weather",
      "input": { "location": "San Francisco", "unit": "fahrenheit" }
    }
  ],
  "stop_reason": "tool_use"
}
```

### Understanding the response

* **`server_tool_use`:** Claude's call to the tool search tool. The search runs on Anthropic's servers. Never return a `tool_result` for its `srvtoolu_...` ID. The `input` holds the search (`pattern` for the regex variant, `query` for BM25) and may include an optional `limit`, an integer from 1 to 10,000 that caps how many matching tools the search returns (default: 5).
* **`tool_search_tool_result`:** the search results, in a nested `tool_search_tool_search_result` object. Keep it in the message history as is.
* **`tool_references`:** an array of `tool_reference` objects pointing to discovered tools. The API expands these for Claude. You never expand them yourself.
* **`tool_use`:** Claude's call to a discovered tool. Execute it and return a `tool_result` exactly as in standard tool use.

The API automatically expands `tool_reference` blocks into full tool definitions before showing them to Claude. You don't need to handle this expansion yourself, as long as you provide all matching tool definitions in the `tools` parameter.

### Continuing the conversation

On the next request, pass the assistant's content back unchanged, including the `server_tool_use` and `tool_search_tool_result` blocks. Add your `tool_result` for the discovered tool in a user message, and send the same `tools` array: the search tool plus every deferred definition. Don't return a `tool_result` for the `srvtoolu_...` ID: the API rejects the request. The API expands `tool_reference` blocks throughout the conversation history, so Claude can reuse discovered tools in later turns without re-searching. A search that matches nothing returns a `tool_search_tool_search_result` with an empty `tool_references` array, not an error.


## MCP integration

Source: https://platform.claude.com/llms-full.txt#mcp-integration

If your tools come from MCP servers through the [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector), you don't set `defer_loading` on individual tool definitions. Instead, set it once on the `mcp_toolset` entry's `default_config` for the whole server, or per tool in its `configs`. See [MCP toolset configuration](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector#mcp-toolset-configuration).


## Custom tool search implementation

Source: https://platform.claude.com/llms-full.txt#custom-tool-search-implementation

You can implement your own tool search logic (for example, using embeddings or semantic search) by returning `tool_reference` blocks from a custom tool. When Claude calls your custom search tool, return a standard `tool_result` with `tool_reference` blocks in the content array:

```json JSON
{
  "type": "tool_result",
  "tool_use_id": "toolu_your_tool_id",
  "content": [{ "type": "tool_reference", "tool_name": "discovered_tool_name" }]
}
```

Every tool referenced must have a corresponding tool definition in the top-level `tools` parameter, normally with `defer_loading: true`. This lets you use search methods the built-in variants don't provide, such as embedding-based retrieval, and the API expands the returned `tool_reference` blocks the same way.

<Note>
  The `tool_search_tool_result` format shown in the [Response format](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#response-format) section is the server-side format used internally by Anthropic's built-in tool search. For custom client-side implementations, always use the standard `tool_result` format with `tool_reference` content blocks as shown in the preceding example.
</Note>

For a complete example using embeddings, see the [tool search with embeddings](https://platform.claude.com/cookbook/tool-use-tool-search-with-embeddings) recipe.


## Error handling

Source: https://platform.claude.com/llms-full.txt#error-handling-2

<Note>
  [Tool use examples](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools#providing-tool-use-examples) work with tool search: when Claude discovers a deferred tool, the API expands its `input_examples` along with its definition.
</Note>

### HTTP errors (400 status)

These errors prevent the API from processing the request:

**All tools deferred:**

**Missing tool definition:**

### Tool result errors (200 status)

When a tool search operation fails during execution, the API returns a 200 response with the error in the body:

```json JSON
{
  "type": "tool_search_tool_result",
  "tool_use_id": "srvtoolu_01ABC123",
  "content": {
    "type": "tool_search_tool_result_error",
    "error_code": "invalid_tool_input",
    "error_message": "Invalid regular expression pattern: missing ) at position 1"
  }
}

json
  {
    "type": "tool_search_tool_regex_20251119",
    "name": "tool_search_tool_regex"
  }

json
  {
    "name": "my_tool",
    "description": "Full description here",
    "input_schema": {
      "type": "object"
    },
    "defer_loading": true
  }
  ```
</Accordion>

<Accordion title="Claude doesn't find expected tools">
  **Cause:** The regex pattern doesn't match the tool's name, description, argument names, or argument descriptions.

  **Debugging steps:**

  1. Check tool name, description, argument names, and argument descriptions. Claude searches all of these fields.
  2. Test your pattern: `import re; re.search(r"your_pattern", "tool_name", re.IGNORECASE)`.
  3. Matching is case-insensitive, so casing differences aren't the problem.
  4. Claude uses broad patterns such as `".*weather.*"`, not exact matches.

  **Tip:** Add common keywords to tool descriptions to improve discoverability.
</Accordion>


## Prompt caching

Source: https://platform.claude.com/llms-full.txt#prompt-caching

To learn how `defer_loading` preserves prompt caching, see [Tool use with prompt caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching).

A tool with `defer_loading: true` can't also carry `cache_control`: the API returns a 400. Put the cache breakpoint on a non-deferred tool.


## Streaming

Source: https://platform.claude.com/llms-full.txt#streaming-4

With streaming enabled, you'll receive tool search events as part of the stream:


## Batch requests

Source: https://platform.claude.com/llms-full.txt#batch-requests-3

You can include the tool search tool in the [Messages Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing).


## Limits and best practices

Source: https://platform.claude.com/llms-full.txt#limits-and-best-practices

### Limits

* **Maximum deferred tools:** 10,000 tools with `defer_loading: true` per request
* **Search results:** each search returns up to 5 matching tools by default; Claude can set `limit` in its search input to any integer from 1 to 10,000
* **Pattern and query length:** maximum 200 characters for regex patterns and 500 characters for BM25 queries
* **Model support:** see [Model compatibility](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#model-compatibility)

### When to use tool search

Use tool search when any of the following apply:

* You have 10 or more tools available.
* Your tool definitions consume more than 10k tokens.
* Tool selection accuracy drops as your toolset grows.
* You aggregate multiple MCP servers (200+ tools).
* Your tool library grows over time.

Standard tool calling, without tool search, is a better fit when you have fewer than 10 tools, every tool is used in every request, or your tool definitions are small (less than 100 tokens total).

### Optimization tips

* Keep your 3–5 most frequently used tools non-deferred.
* Write clear, descriptive tool names and descriptions.
* Use consistent namespacing in tool names: prefix by service or resource (for example, `github_`, `slack_`) so one search matches the whole group.
* Use keywords in descriptions that match how users describe tasks.
* Add a system prompt section describing available tool categories: "You can search for tools to interact with Slack, GitHub, and Jira."
* Monitor which tools Claude discovers to refine your descriptions.


## Usage

Source: https://platform.claude.com/llms-full.txt#usage

Tool search isn't metered as a separate server tool. The response's `usage.server_tool_use` object has no tool search field, and the tool definitions that search loads into context count as input tokens like any other tool definition.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-38

<CardGroup cols={2}>
  <Card title="Memory tool" icon="brain" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool">
    Let Claude store and retrieve information across conversations by implementing the memory tool's file operations in your application.
  </Card>

  <Card title="Tool reference" icon="book" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference">
    Directory of Anthropic-provided tools and reference for optional tool definition properties.
  </Card>

  <Card title="MCP connector" icon="link" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-connector">
    Configure MCP toolsets with deferred loading.
  </Card>

  <Card title="Tool use with prompt caching" icon="bolt" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching">
    Cache tool definitions across turns and understand what invalidates your cache.
  </Card>

  <Card title="Define tools" icon="hammer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools">
    Specify tool schemas, write effective descriptions, and control when Claude calls your tools.
  </Card>
</CardGroup>


---
title: Troubleshooting tool use
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/troubleshooting-tool-use
description: Fix the most common tool-use errors with symptom-to-fix diagnostic tables.
---

Symptom-to-fix tables for the most common tool-use errors. Each fix cross-references the page that owns the feature.


## Claude calls the wrong tool

Source: https://platform.claude.com/llms-full.txt#claude-calls-the-wrong-tool

| Symptom                                    | Likely cause                                 | Fix                                                                                                                                                                                   |
| ------------------------------------------ | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude calls tool A when you wanted tool B | Description ambiguity                        | Sharpen descriptions. Differentiate tools by WHEN to use them, not only WHAT they do. See [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools). |
| Claude never calls your tool               | Tool name collision or overly-generic schema | Check for duplicate names across your tool list. Add `input_examples` to make the intended use concrete.                                                                              |
| Claude calls with wrong parameter types    | Model guessing at ambiguous schema           | Add `strict: true` (if your schema is in the supported subset) or add `input_examples`.                                                                                               |


## Claude invents tool parameters

Source: https://platform.claude.com/llms-full.txt#claude-invents-tool-parameters

| Symptom                                     | Likely cause                              | Fix                                                                                                                                            |
| ------------------------------------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Parameter that doesn't exist in your schema | Model over-generation without strict mode | Add `strict: true` if your schema is in the [supported subset](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use). |
| Parameter values outside your enum          | Missing strict mode or too-large enum     | Shrink the enum or add `input_examples` showing valid choices.                                                                                 |


## Parallel tool calls don't work

Source: https://platform.claude.com/llms-full.txt#parallel-tool-calls-don-t-work

| Symptom                                                       | Likely cause                     | Fix                                                                                                                                                                                 |
| ------------------------------------------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude calls tools sequentially when parallel would be better | Message history formatting       | Send multiple `tool_result` blocks in ONE user message, not one per turn. See [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use). |
| `disable_parallel_tool_use` seems ignored                     | Set too late in the conversation | Must be set on the request that returns `tool_use`. Setting it on a later request has no effect on earlier tool calls.                                                              |


## Cache keeps invalidating

Source: https://platform.claude.com/llms-full.txt#cache-keeps-invalidating

| Symptom                                     | Likely cause                                                                                  | Fix                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Every request is a cache miss               | `tool_choice`, the thinking configuration, or `output_config.effort` varying between requests | Keep `tool_choice` stable or place the `cache_control` breakpoint before the variation point; hold the thinking configuration and effort level constant for the life of a cached conversation. See [Tool use with prompt caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching) and [Thinking and prompt caching](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-prompt-caching). |
| Adding a tool mid-conversation breaks cache | Tool prepended to the tools array                                                             | Use `defer_loading: true` with tool search to append the tool inline instead of modifying the array head.                                                                                                                                                                                                                                                                                                                                                    |


## Errors at request time

Source: https://platform.claude.com/llms-full.txt#errors-at-request-time

| Error                                                                  | Cause                                                                                                                                                                                                                                                                                                                                                                    | Fix                                                                                                                                                                                                                                                                                                                                         |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tool_use ids were found without tool_result blocks immediately after` | Missing `tool_result` for some `tool_use` ids, or `tool_result` is not the first content block in the user message                                                                                                                                                                                                                                                       | Return one `tool_result` for every `tool_use` block in the assistant response. Put `tool_result` blocks before any text. See [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) and [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use). |
| `was found without a corresponding <name>_tool_result block`           | The previous assistant turn has a `server_tool_use` block with no result block (most often, Claude called it alongside a client tool), and either your next user message ended that turn (for example, with text after the `tool_result` blocks) or the resume request no longer defines that server tool (the message then ends with `but no <name> tool was provided`) | Send a user message containing only the `tool_result` blocks for the client `tool_use` ids and keep the same `tools` array. See [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#tool-use).                                                                                          |
| `Unsupported regex feature in pattern field: ...`                      | A `pattern` in a strict tool's `input_schema` uses a regex feature that strict mode can't compile, such as a backreference, a lookaround, a word boundary, or a large `{n,m}` range                                                                                                                                                                                      | Simplify the pattern. Anchored patterns with basic quantifiers, character classes, and groups are supported; see [JSON Schema limitations](https://platform.claude.com/docs/en/build-with-claude/structured-outputs#json-schema-limitations).                                                                                               |
| `All tools have defer_loading: true`                                   | No tools visible to the model                                                                                                                                                                                                                                                                                                                                            | At least one tool must be immediately loaded. The tool search tool itself must never have `defer_loading: true`.                                                                                                                                                                                                                            |


## Error: thinking blocks cannot be modified

Source: https://platform.claude.com/llms-full.txt#error-thinking-blocks-cannot-be-modified

If a request fails with a 400 `invalid_request_error` whose message contains `` `thinking` or `redacted_thinking` blocks in the latest assistant message cannot be modified `` when continuing a conversation after a tool call, your application is altering the assistant's thinking blocks before sending them back. Send the entire assistant message back unchanged, then append your `tool_result`.

See [Thinking blocks cannot be modified](https://platform.claude.com/docs/en/api/errors#thinking-blocks-cannot-be-modified) for the full error and fix steps.


## Claude flags tool results as prompt injection

Source: https://platform.claude.com/llms-full.txt#claude-flags-tool-results-as-prompt-injection

| Symptom                                                                                            | Likely cause                                                               | Fix                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude refuses to act on a tool result, or asks the user to confirm instructions that came from it | Your own instructions are being delivered inside the `tool_result` content | Claude is trained to treat instructions inside tool results as potentially untrusted third-party content. Move your instructions out of the tool result: send them in a `user` turn after the `tool_result` block, or, on supported models, in a [mid-conversation system message](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages). Keep the tool result to just the data. See [Mitigate jailbreaks and prompt injections](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks#indirect-prompt-injection). |


## JSON escaping differences (Opus 4.6+)

Source: https://platform.claude.com/llms-full.txt#json-escaping-differences-opus-4-6

| Symptom                                                  | Cause                                                             | Fix                                                                                            |
| -------------------------------------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| String comparison on tool inputs fails with newer models | Unicode and forward-slash escaping differs between model versions | Parse with `json.loads()` or `JSON.parse()`. Never do raw string matching on serialized input. |


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-39

<CardGroup cols={3}>
  <Card title="Define tools" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools">
    Write schemas and descriptions that steer Claude toward the right tool.
  </Card>

  <Card title="Handle tool calls" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls">
    Execute tools and return results in the required message format.
  </Card>

  <Card title="Tool reference" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference">
    Full directory of Anthropic-provided tools and their version strings.
  </Card>
</CardGroup>


---
title: "Tutorial: Build a tool-using agent"
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent
description: A guided walkthrough from a single tool call to a production-ready agentic loop.
---

This tutorial builds a calendar-management agent in five concentric rings. Each ring is a complete, runnable program that adds exactly one concept to the ring before it. By the end you will have written the agentic loop by hand and then replaced it with the Tool Runner SDK abstraction.

The example tool is `create_calendar_event`. Its schema uses nested objects, arrays, and optional fields, so you will see how Claude handles realistic input shapes rather than a single flat string.

<Note>
  Every ring runs standalone. Copy any ring into a fresh file and it will run without the code from earlier rings.
</Note>


## Ring 1: Single tool, single turn

Source: https://platform.claude.com/llms-full.txt#ring-1-single-tool-single-turn

The smallest possible tool-using program: one tool, one user message, one tool call, one result. The code is heavily commented so you can map each line to the [tool use lifecycle](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works).

The request sends a `tools` array alongside the user message. When Claude determines that a tool call is needed, the response comes back with `stop_reason: "tool_use"` and a `tool_use` content block containing the tool name, a unique `id`, and the structured `input`. Your code runs the tool, then sends the result back in a `tool_result` block whose `tool_use_id` matches the `id` from the call.

<CodeGroup>
  ```bash cURL
  #!/bin/bash
  # Ring 1: Single tool, single turn.

  # Define one tool as a JSON fragment. The input_schema is a JSON Schema
  # object describing the arguments Claude should pass when it calls this
  # tool. This schema includes nested objects (recurrence), arrays
  # (attendees), and optional fields, which is closer to real-world tools
  # than a flat string argument.
  TOOLS='[
    {
      "name": "create_calendar_event",
      "description": "Create a calendar event with attendees and optional recurrence.",
      "input_schema": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "start": {"type": "string", "format": "date-time"},
          "end": {"type": "string", "format": "date-time"},
          "attendees": {
            "type": "array",
            "items": {"type": "string", "format": "email"}
          },
          "recurrence": {
            "type": "object",
            "properties": {
              "frequency": {"enum": ["daily", "weekly", "monthly"]},
              "count": {"type": "integer", "minimum": 1}
            }
          }
        },
        "required": ["title", "start", "end"]
      }
    }
  ]'

  USER_MSG="Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, March 30, 2026 at 10am."

  # Send the user's request along with the tool definition. Claude decides
  # whether to call the tool based on the request and the tool description.
  RESPONSE=$(curl -s https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "$(jq -n \
      --argjson tools "$TOOLS" \
      --arg msg "$USER_MSG" \
      '{
        model: "claude-opus-5",
        max_tokens: 1024,
        tools: $tools,
        tool_choice: {type: "auto", disable_parallel_tool_use: true},
        messages: [{role: "user", content: $msg}]
      }')")

  # When Claude calls a tool, the response has stop_reason "tool_use"
  # and the content array contains a tool_use block alongside any text.
  echo "stop_reason: $(echo "$RESPONSE" | jq -r '.stop_reason')"

  # Find the tool_use block. A response may contain text blocks before the
  # tool_use block, so filter by type rather than assuming position.
  TOOL_USE=$(echo "$RESPONSE" | jq '.content[] | select(.type == "tool_use")')
  TOOL_USE_ID=$(echo "$TOOL_USE" | jq -r '.id')
  echo "Tool: $(echo "$TOOL_USE" | jq -r '.name')"
  echo "Input: $(echo "$TOOL_USE" | jq -c '.input')"

  # Execute the tool. In a real system this would call your calendar API.
  # Here the result is hardcoded to keep the example self-contained.
  RESULT='{"event_id": "evt_123", "status": "created"}'

  # Send the result back. The tool_result block goes in a user message and
  # its tool_use_id must match the id from the tool_use block above. The
  # assistant's previous response is included so Claude has the full history.
  ASSISTANT_CONTENT=$(echo "$RESPONSE" | jq '.content')
  FOLLOWUP=$(curl -s https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "$(jq -n \
      --argjson tools "$TOOLS" \
      --arg msg "$USER_MSG" \
      --argjson assistant "$ASSISTANT_CONTENT" \
      --arg tool_use_id "$TOOL_USE_ID" \
      --arg result "$RESULT" \
      '{
        model: "claude-opus-5",
        max_tokens: 1024,
        tools: $tools,
        tool_choice: {type: "auto", disable_parallel_tool_use: true},
        messages: [
          {role: "user", content: $msg},
          {role: "assistant", content: $assistant},
          {role: "user", content: [
            {type: "tool_result", tool_use_id: $tool_use_id, content: $result}
          ]}
        ]
      }')")

  # With the tool result in hand, Claude produces a final natural-language
  # answer and stop_reason becomes "end_turn".
  echo "stop_reason: $(echo "$FOLLOWUP" | jq -r '.stop_reason')"
  echo "$FOLLOWUP" | jq -r '.content[] | select(.type == "text") | .text'

bash CLI
  #!/usr/bin/env bash
  # Ring 1: Single tool, single turn.
  # Uses jq for cross-turn message-array state — building an agentic loop in shell
  # requires JSON manipulation beyond ant's single-call --transform scope.
  set -euo pipefail

  USER_MSG="Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, March 30, 2026 at 10am."
  MESSAGES=$(jq -n --arg msg "$USER_MSG" '[{role: "user", content: $msg}]')

  # Define one tool. The input_schema is a JSON Schema object describing
  # the arguments Claude should pass when it calls this tool. This schema
  # includes nested objects (recurrence), arrays (attendees), and optional
  # fields, which is closer to real-world tools than a flat string argument.
  call_api() {
    # ant reads the request body as YAML on stdin: no auth headers, no
    # hand-built JSON envelope. The static keys (model, tools, tool_choice)
    # live in a quoted heredoc; the growing messages array is appended as
    # JSON, which YAML accepts as flow syntax.
    {
      cat <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tool_choice: {type: auto, disable_parallel_tool_use: true}
  tools:
    - name: create_calendar_event
      description: Create a calendar event with attendees and optional recurrence.
      input_schema:
        type: object
        properties:
          title: {type: string}
          start: {type: string, format: date-time}
          end: {type: string, format: date-time}
          attendees:
            type: array
            items: {type: string, format: email}
          recurrence:
            type: object
            properties:
              frequency: {enum: [daily, weekly, monthly]}
              count: {type: integer, minimum: 1}
        required: [title, start, end]
  YAML
      printf 'messages: %s\n' "$MESSAGES"
    } | ant messages create --format json
  }

  # Send the user's request along with the tool definition. Claude decides
  # whether to call the tool based on the request and the tool description.
  RESPONSE=$(call_api)

  # When Claude calls a tool, the response has stop_reason "tool_use"
  # and the content array contains a tool_use block alongside any text.
  echo "stop_reason: $(jq -r '.stop_reason' <<<"$RESPONSE")"

  # Find the tool_use block. A response may contain text blocks before the
  # tool_use block, so filter by type rather than assuming position.
  TOOL_USE=$(jq '.content[] | select(.type == "tool_use")' <<<"$RESPONSE")
  TOOL_USE_ID=$(jq -r '.id' <<<"$TOOL_USE")
  echo "Tool: $(jq -r '.name' <<<"$TOOL_USE")"
  echo "Input: $(jq -c '.input' <<<"$TOOL_USE")"

  # Execute the tool. In a real system this would call your calendar API.
  # Here the result is hardcoded to keep the example self-contained.
  RESULT='{"event_id": "evt_123", "status": "created"}'

  # Send the result back. The tool_result block goes in a user message and
  # its tool_use_id must match the id from the tool_use block above. The
  # assistant's previous response is included so Claude has the full history.
  MESSAGES=$(jq \
    --argjson assistant "$(jq '.content' <<<"$RESPONSE")" \
    --arg tool_use_id "$TOOL_USE_ID" \
    --arg result "$RESULT" \
    '. + [
      {role: "assistant", content: $assistant},
      {role: "user", content: [
        {type: "tool_result", tool_use_id: $tool_use_id, content: $result}
      ]}
    ]' <<<"$MESSAGES")

  FOLLOWUP=$(call_api)

  # With the tool result in hand, Claude produces a final natural-language
  # answer and stop_reason becomes "end_turn".
  echo "stop_reason: $(jq -r '.stop_reason' <<<"$FOLLOWUP")"
  jq -r '.content[] | select(.type == "text") | .text' <<<"$FOLLOWUP"

python Python
  # Ring 1: Single tool, single turn.

  import json

  import anthropic

  # Create a client. It reads ANTHROPIC_API_KEY from the environment.
  client = anthropic.Anthropic()

  # Define one tool. The input_schema is a JSON Schema object describing
  # the arguments Claude should pass when it calls this tool. This schema
  # includes nested objects (recurrence), arrays (attendees), and optional
  # fields, which is closer to real-world tools than a flat string argument.
  tools = [
      {
          "name": "create_calendar_event",
          "description": "Create a calendar event with attendees and optional recurrence.",
          "input_schema": {
              "type": "object",
              "properties": {
                  "title": {"type": "string"},
                  "start": {"type": "string", "format": "date-time"},
                  "end": {"type": "string", "format": "date-time"},
                  "attendees": {
                      "type": "array",
                      "items": {"type": "string", "format": "email"},
                  },
                  "recurrence": {
                      "type": "object",
                      "properties": {
                          "frequency": {"enum": ["daily", "weekly", "monthly"]},
                          "count": {"type": "integer", "minimum": 1},
                      },
                  },
              },
              "required": ["title", "start", "end"],
          },
      }
  ]

  # Send the user's request along with the tool definition. Claude decides
  # whether to call the tool based on the request and the tool description.
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=tools,
      tool_choice={"type": "auto", "disable_parallel_tool_use": True},
      messages=[
          {
              "role": "user",
              "content": "Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, March 30, 2026 at 10am.",
          }
      ],
  )

  # When Claude calls a tool, the response has stop_reason "tool_use"
  # and the content array contains a tool_use block alongside any text.
  print(f"stop_reason: {response.stop_reason}")

  # Find the tool_use block. A response may contain text blocks before the
  # tool_use block, so scan the content array rather than assuming position.
  tool_use = next(block for block in response.content if block.type == "tool_use")
  print(f"Tool: {tool_use.name}")
  print(f"Input: {tool_use.input}")

  # Execute the tool. In a real system this would call your calendar API.
  # Here the result is hardcoded to keep the example self-contained.
  result = {"event_id": "evt_123", "status": "created"}

  # Send the result back. The tool_result block goes in a user message and
  # its tool_use_id must match the id from the tool_use block above. The
  # assistant's previous response is included so Claude has the full history.
  followup = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=tools,
      tool_choice={"type": "auto", "disable_parallel_tool_use": True},
      messages=[
          {
              "role": "user",
              "content": "Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, March 30, 2026 at 10am.",
          },
          {"role": "assistant", "content": response.content},
          {
              "role": "user",
              "content": [
                  {
                      "type": "tool_result",
                      "tool_use_id": tool_use.id,
                      "content": json.dumps(result),
                  }
              ],
          },
      ],
  )

  # With the tool result in hand, Claude produces a final natural-language
  # answer and stop_reason becomes "end_turn".
  print(f"stop_reason: {followup.stop_reason}")
  final_text = next(block for block in followup.content if block.type == "text")
  print(final_text.text)

typescript TypeScript
  // Ring 1: Single tool, single turn.

  import Anthropic from "@anthropic-ai/sdk";

  // Create a client. It reads ANTHROPIC_API_KEY from the environment.
  const client = new Anthropic();

  // Define one tool. The input_schema is a JSON Schema object describing
  // the arguments Claude should pass when it calls this tool. This schema
  // includes nested objects (recurrence), arrays (attendees), and optional
  // fields, which is closer to real-world tools than a flat string argument.
  const tools: Anthropic.Tool[] = [
    {
      name: "create_calendar_event",
      description:
        "Create a calendar event with attendees and optional recurrence.",
      input_schema: {
        type: "object",
        properties: {
          title: { type: "string" },
          start: { type: "string", format: "date-time" },
          end: { type: "string", format: "date-time" },
          attendees: {
            type: "array",
            items: { type: "string", format: "email" },
          },
          recurrence: {
            type: "object",
            properties: {
              frequency: { enum: ["daily", "weekly", "monthly"] },
              count: { type: "integer", minimum: 1 },
            },
          },
        },
        required: ["title", "start", "end"],
      },
    },
  ];

  // Send the user's request along with the tool definition. Claude decides
  // whether to call the tool based on the request and the tool description.
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools,
    tool_choice: { type: "auto", disable_parallel_tool_use: true },
    messages: [
      {
        role: "user",
        content:
          "Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, March 30, 2026 at 10am.",
      },
    ],
  });

  // When Claude calls a tool, the response has stop_reason "tool_use"
  // and the content array contains a tool_use block alongside any text.
  console.log(`stop_reason: ${response.stop_reason}`);

  // Find the tool_use block. A response may contain text blocks before the
  // tool_use block, so scan the content array rather than assuming position.
  const toolUse = response.content.find(
    (block): block is Anthropic.ToolUseBlock => block.type === "tool_use",
  )!;
  console.log(`Tool: ${toolUse.name}`);
  console.log(`Input: ${JSON.stringify(toolUse.input)}`);

  // Execute the tool. In a real system this would call your calendar API.
  // Here the result is hardcoded to keep the example self-contained.
  const result = { event_id: "evt_123", status: "created" };

  // Send the result back. The tool_result block goes in a user message and
  // its tool_use_id must match the id from the tool_use block above. The
  // assistant's previous response is included so Claude has the full history.
  const followup = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools,
    tool_choice: { type: "auto", disable_parallel_tool_use: true },
    messages: [
      {
        role: "user",
        content:
          "Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, March 30, 2026 at 10am.",
      },
      { role: "assistant", content: response.content },
      {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: toolUse.id,
            content: JSON.stringify(result),
          },
        ],
      },
    ],
  });

  // With the tool result in hand, Claude produces a final natural-language
  // answer and stop_reason becomes "end_turn".
  console.log(`stop_reason: ${followup.stop_reason}`);
  for (const block of followup.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

csharp C#
  // Ring 1: Single tool, single turn.

  using System;
  using System.Collections.Generic;
  using System.Linq;
  using System.Text.Json;
  using System.Threading.Tasks;
  using Anthropic;
  using Anthropic.Models.Messages;

  // Create a client. It reads ANTHROPIC_API_KEY from the environment.
  AnthropicClient client = new();

  // Define one tool. The input schema is a JSON Schema object describing
  // the arguments Claude should pass when it calls this tool. This schema
  // includes nested objects (recurrence), arrays (attendees), and optional
  // fields, which is closer to real-world tools than a flat string argument.
  List<ToolUnion> tools =
  [
      new ToolUnion(new Tool()
      {
          Name = "create_calendar_event",
          Description = "Create a calendar event with attendees and optional recurrence.",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["title"] = JsonSerializer.SerializeToElement(new { type = "string" }),
                  ["start"] = JsonSerializer.SerializeToElement(new { type = "string", format = "date-time" }),
                  ["end"] = JsonSerializer.SerializeToElement(new { type = "string", format = "date-time" }),
                  ["attendees"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "array",
                      items = new { type = "string", format = "email" },
                  }),
                  ["recurrence"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "object",
                      properties = new
                      {
                          frequency = new { @enum = new[] { "daily", "weekly", "monthly" } },
                          count = new { type = "integer", minimum = 1 },
                      },
                  }),
              },
              Required = ["title", "start", "end"],
          },
      }),
  ];

  // Ask for at most one tool call per turn so the single-turn flow below
  // stays predictable.
  var toolChoice = new ToolChoice(new ToolChoiceAuto { DisableParallelToolUse = true });

  const string userPrompt =
      "Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, March 30, 2026 at 10am.";

  // Send the user's request along with the tool definition. Claude decides
  // whether to call the tool based on the request and the tool description.
  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = tools,
      ToolChoice = toolChoice,
      Messages = [new() { Role = Role.User, Content = userPrompt }],
  });

  // When Claude calls a tool, the response has stop_reason "tool_use"
  // and the content array contains a tool_use block alongside any text.
  Console.WriteLine($"stop_reason: {response.StopReason?.Raw()}");

  // Find the tool_use block. A response may contain text blocks before the
  // tool_use block, so scan the content array rather than assuming position.
  ToolUseBlock? toolUse = null;
  foreach (var block in response.Content)
  {
      if (block.TryPickToolUse(out var picked))
      {
          toolUse = picked;
          break;
      }
  }
  Console.WriteLine($"Tool: {toolUse!.Name}");
  Console.WriteLine($"Input: {JsonSerializer.Serialize(toolUse.Input)}");

  // Execute the tool. In a real system this would call your calendar API.
  // Here the result is hardcoded to keep the example self-contained.
  var result = """{"event_id": "evt_123", "status": "created"}""";

  // Send the result back. The tool_result block goes in a user message and
  // its tool_use_id must match the id from the tool_use block above. The
  // assistant's previous response is included so Claude has the full history.
  List<ContentBlockParam> toolResults =
  [
      new ContentBlockParam(new ToolResultBlockParam()
      {
          ToolUseID = toolUse.ID,
          Content = result,
      }),
  ];

  var followup = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = tools,
      ToolChoice = toolChoice,
      Messages =
      [
          new() { Role = Role.User, Content = userPrompt },
          new() { Role = Role.Assistant, Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList() },
          new() { Role = Role.User, Content = new MessageParamContent(toolResults) },
      ],
  });

  // With the tool result in hand, Claude produces a final natural-language
  // answer and stop_reason becomes "end_turn".
  Console.WriteLine($"stop_reason: {followup.StopReason?.Raw()}");
  foreach (var block in followup.Content)
  {
      if (block.TryPickText(out var text))
      {
          Console.WriteLine(text.Text);
      }
  }

go Go
  // Ring 1: Single tool, single turn.

  package main

  import (
  	"context"
  	"fmt"
  	"log"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  func main() {
  	// Create a client. It reads ANTHROPIC_API_KEY from the environment.
  	client := anthropic.NewClient()
  	ctx := context.Background()

  	// Define one tool. The input schema is a JSON Schema object describing
  	// the arguments Claude should pass when it calls this tool. This schema
  	// includes nested objects (recurrence), arrays (attendees), and optional
  	// fields, which is closer to real-world tools than a flat string argument.
  	tools := []anthropic.ToolUnionParam{
  		{OfTool: &anthropic.ToolParam{
  			Name:        "create_calendar_event",
  			Description: anthropic.String("Create a calendar event with attendees and optional recurrence."),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"title": map[string]any{"type": "string"},
  					"start": map[string]any{"type": "string", "format": "date-time"},
  					"end":   map[string]any{"type": "string", "format": "date-time"},
  					"attendees": map[string]any{
  						"type":  "array",
  						"items": map[string]any{"type": "string", "format": "email"},
  					},
  					"recurrence": map[string]any{
  						"type": "object",
  						"properties": map[string]any{
  							"frequency": map[string]any{"enum": []string{"daily", "weekly", "monthly"}},
  							"count":     map[string]any{"type": "integer", "minimum": 1},
  						},
  					},
  				},
  				Required: []string{"title", "start", "end"},
  			},
  		}},
  	}

  	// Ask for at most one tool call per turn so the single-turn flow below
  	// stays predictable.
  	toolChoice := anthropic.ToolChoiceUnionParam{
  		OfAuto: &anthropic.ToolChoiceAutoParam{DisableParallelToolUse: anthropic.Bool(true)},
  	}

  	userMessage := anthropic.NewUserMessage(anthropic.NewTextBlock(
  		"Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, March 30, 2026 at 10am.",
  	))

  	// Send the user's request along with the tool definition. Claude decides
  	// whether to call the tool based on the request and the tool description.
  	response, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  		Model:      anthropic.ModelClaudeOpus5,
  		MaxTokens:  1024,
  		Tools:      tools,
  		ToolChoice: toolChoice,
  		Messages:   []anthropic.MessageParam{userMessage},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	// When Claude calls a tool, the response has stop_reason "tool_use"
  	// and the content array contains a tool_use block alongside any text.
  	fmt.Printf("stop_reason: %s\n", response.StopReason)

  	// Find the tool_use block. A response may contain text blocks before the
  	// tool_use block, so scan the content array rather than assuming position.
  	var toolUse anthropic.ContentBlockUnion
  	for _, block := range response.Content {
  		if block.Type == "tool_use" {
  			toolUse = block
  			break
  		}
  	}
  	fmt.Printf("Tool: %s\n", toolUse.Name)
  	fmt.Printf("Input: %s\n", string(toolUse.Input))

  	// Execute the tool. In a real system this would call your calendar API.
  	// Here the result is hardcoded to keep the example self-contained.
  	result := `{"event_id": "evt_123", "status": "created"}`

  	// Send the result back. The tool_result block goes in a user message and
  	// its tool_use_id must match the id from the tool_use block above. The
  	// assistant's previous response is included so Claude has the full history.
  	var assistantContent []anthropic.ContentBlockParamUnion
  	for _, block := range response.Content {
  		assistantContent = append(assistantContent, block.ToParam())
  	}

  	followup, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  		Model:      anthropic.ModelClaudeOpus5,
  		MaxTokens:  1024,
  		Tools:      tools,
  		ToolChoice: toolChoice,
  		Messages: []anthropic.MessageParam{
  			userMessage,
  			anthropic.NewAssistantMessage(assistantContent...),
  			anthropic.NewUserMessage(anthropic.NewToolResultBlock(toolUse.ID, result, false)),
  		},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	// With the tool result in hand, Claude produces a final natural-language
  	// answer and stop_reason becomes "end_turn".
  	fmt.Printf("stop_reason: %s\n", followup.StopReason)
  	for _, block := range followup.Content {
  		if block.Type == "text" {
  			fmt.Println(block.Text)
  		}
  	}
  }

java Java
  // Ring 1: Single tool, single turn.

  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.JsonValue;
  import com.anthropic.models.messages.ContentBlockParam;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;
  import com.anthropic.models.messages.Tool;
  import com.anthropic.models.messages.Tool.InputSchema;
  import com.anthropic.models.messages.ToolChoiceAuto;
  import com.anthropic.models.messages.ToolResultBlockParam;
  import com.anthropic.models.messages.ToolUseBlock;
  import java.util.List;
  import java.util.Map;

  void main() {
      // Create a client. It reads ANTHROPIC_API_KEY from the environment.
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      // Define one tool. The input schema is a JSON Schema object describing
      // the arguments Claude should pass when it calls this tool. This schema
      // includes nested objects (recurrence), arrays (attendees), and optional
      // fields, which is closer to real-world tools than a flat string argument.
      Tool calendarTool = Tool.builder()
          .name("create_calendar_event")
          .description("Create a calendar event with attendees and optional recurrence.")
          .inputSchema(InputSchema.builder()
              .properties(JsonValue.from(Map.of(
                  "title", Map.of("type", "string"),
                  "start", Map.of("type", "string", "format", "date-time"),
                  "end", Map.of("type", "string", "format", "date-time"),
                  "attendees", Map.of(
                      "type", "array",
                      "items", Map.of("type", "string", "format", "email")
                  ),
                  "recurrence", Map.of(
                      "type", "object",
                      "properties", Map.of(
                          "frequency", Map.of("enum", List.of("daily", "weekly", "monthly")),
                          "count", Map.of("type", "integer", "minimum", 1)
                      )
                  )
              )))
              .required(List.of("title", "start", "end"))
              .build())
          .build();

      // Ask for at most one tool call per turn so the single-turn flow below
      // stays predictable.
      ToolChoiceAuto toolChoice = ToolChoiceAuto.builder()
          .disableParallelToolUse(true)
          .build();

      String userPrompt =
          "Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, March 30, 2026 at 10am.";

      // Send the user's request along with the tool definition. Claude decides
      // whether to call the tool based on the request and the tool description.
      Message response = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addTool(calendarTool)
          .toolChoice(toolChoice)
          .addUserMessage(userPrompt)
          .build());

      // When Claude calls a tool, the response has stop_reason "tool_use"
      // and the content array contains a tool_use block alongside any text.
      IO.println("stop_reason: " + response.stopReason().orElse(null));

      // Find the tool_use block. A response may contain text blocks before the
      // tool_use block, so scan the content array rather than assuming position.
      ToolUseBlock toolUse = response.content().stream()
          .flatMap(block -> block.toolUse().stream())
          .findFirst()
          .orElseThrow();
      IO.println("Tool: " + toolUse.name());
      IO.println("Input: " + toolUse._input());

      // Execute the tool. In a real system this would call your calendar API.
      // Here the result is hardcoded to keep the example self-contained.
      String result = "{\"event_id\": \"evt_123\", \"status\": \"created\"}";

      // Send the result back. The tool_result block goes in a user message and
      // its tool_use_id must match the id from the tool_use block above. The
      // assistant's previous response is included so Claude has the full history.
      Message followup = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addTool(calendarTool)
          .toolChoice(toolChoice)
          .addUserMessage(userPrompt)
          .addMessage(response)
          .addUserMessageOfBlockParams(List.of(ContentBlockParam.ofToolResult(
              ToolResultBlockParam.builder()
                  .toolUseId(toolUse.id())
                  .content(result)
                  .build())))
          .build());

      // With the tool result in hand, Claude produces a final natural-language
      // answer and stop_reason becomes "end_turn".
      IO.println("stop_reason: " + followup.stopReason().orElse(null));
      followup.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  <?php

  // Ring 1: Single tool, single turn.

  use Anthropic\Client;
  use Anthropic\Messages\ToolChoiceAuto;

  // Create a client. It reads ANTHROPIC_API_KEY from the environment.
  $client = new Client();

  // Define one tool. The input_schema is a JSON Schema object describing
  // the arguments Claude should pass when it calls this tool. This schema
  // includes nested objects (recurrence), arrays (attendees), and optional
  // fields, which is closer to real-world tools than a flat string argument.
  $tools = [
      [
          'name' => 'create_calendar_event',
          'description' => 'Create a calendar event with attendees and optional recurrence.',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'title' => ['type' => 'string'],
                  'start' => ['type' => 'string', 'format' => 'date-time'],
                  'end' => ['type' => 'string', 'format' => 'date-time'],
                  'attendees' => [
                      'type' => 'array',
                      'items' => ['type' => 'string', 'format' => 'email'],
                  ],
                  'recurrence' => [
                      'type' => 'object',
                      'properties' => [
                          'frequency' => ['enum' => ['daily', 'weekly', 'monthly']],
                          'count' => ['type' => 'integer', 'minimum' => 1],
                      ],
                  ],
              ],
              'required' => ['title', 'start', 'end'],
          ],
      ],
  ];

  $userMessage = [
      'role' => 'user',
      'content' => 'Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, March 30, 2026 at 10am.',
  ];

  // Ask for at most one tool call per turn so the single-turn flow below
  // stays predictable.
  $toolChoice = ToolChoiceAuto::with(disableParallelToolUse: true);

  // Send the user's request along with the tool definition. Claude decides
  // whether to call the tool based on the request and the tool description.
  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: $tools,
      toolChoice: $toolChoice,
      messages: [$userMessage],
  );

  // When Claude calls a tool, the response has stop_reason "tool_use"
  // and the content array contains a tool_use block alongside any text.
  printf("stop_reason: %s\n", $response->stopReason);

  // Find the tool_use block. A response may contain text blocks before the
  // tool_use block, so scan the content array rather than assuming position.
  $toolUse = null;
  foreach ($response->content as $block) {
      if ($block->type === 'tool_use') {
          $toolUse = $block;
          break;
      }
  }
  printf("Tool: %s\n", $toolUse->name);
  printf("Input: %s\n", json_encode($toolUse->input));

  // Execute the tool. In a real system this would call your calendar API.
  // Here the result is hardcoded to keep the example self-contained.
  $result = ['event_id' => 'evt_123', 'status' => 'created'];

  // Send the result back. The tool_result block goes in a user message and
  // its tool_use_id must match the id from the tool_use block above. The
  // assistant's previous response is included so Claude has the full history.
  $followup = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: $tools,
      toolChoice: $toolChoice,
      messages: [
          $userMessage,
          ['role' => 'assistant', 'content' => $response->content],
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'tool_result',
                      'tool_use_id' => $toolUse->id,
                      'content' => json_encode($result),
                  ],
              ],
          ],
      ],
  );

  // With the tool result in hand, Claude produces a final natural-language
  // answer and stop_reason becomes "end_turn".
  printf("stop_reason: %s\n", $followup->stopReason);
  foreach ($followup->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, "\n";
      }
  }

ruby Ruby
  # Ring 1: Single tool, single turn.

  require "anthropic"

  # Create a client. It reads ANTHROPIC_API_KEY from the environment.
  client = Anthropic::Client.new

  # Define one tool. The input_schema is a JSON Schema object describing
  # the arguments Claude should pass when it calls this tool. This schema
  # includes nested objects (recurrence), arrays (attendees), and optional
  # fields, which is closer to real-world tools than a flat string argument.
  tools = [
    {
      name: "create_calendar_event",
      description: "Create a calendar event with attendees and optional recurrence.",
      input_schema: {
        type: "object",
        properties: {
          title: {type: "string"},
          start: {type: "string", format: "date-time"},
          end: {type: "string", format: "date-time"},
          attendees: {
            type: "array",
            items: {type: "string", format: "email"}
          },
          recurrence: {
            type: "object",
            properties: {
              frequency: {enum: ["daily", "weekly", "monthly"]},
              count: {type: "integer", minimum: 1}
            }
          }
        },
        required: ["title", "start", "end"]
      }
    }
  ]

  user_message = {
    role: "user",
    content: "Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, March 30, 2026 at 10am."
  }

  # Ask for at most one tool call per turn so the single-turn flow below
  # stays predictable.
  tool_choice = {type: "auto", disable_parallel_tool_use: true}

  # Send the user's request along with the tool definition. Claude decides
  # whether to call the tool based on the request and the tool description.
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: tools,
    tool_choice: tool_choice,
    messages: [user_message]
  )

  # When Claude calls a tool, the response has stop_reason "tool_use"
  # and the content array contains a tool_use block alongside any text.
  puts "stop_reason: #{response.stop_reason}"

  # Find the tool_use block. A response may contain text blocks before the
  # tool_use block, so scan the content array rather than assuming position.
  tool_use = response.content.find { |block| block.type == :tool_use }
  puts "Tool: #{tool_use.name}"
  puts "Input: #{tool_use.input}"

  # Execute the tool. In a real system this would call your calendar API.
  # Here the result is hardcoded to keep the example self-contained.
  result = {event_id: "evt_123", status: "created"}

  # Send the result back. The tool_result block goes in a user message and
  # its tool_use_id must match the id from the tool_use block above. The
  # assistant's previous response is included so Claude has the full history.
  followup = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: tools,
    tool_choice: tool_choice,
    messages: [
      user_message,
      {role: "assistant", content: response.content},
      {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: tool_use.id,
            content: JSON.generate(result)
          }
        ]
      }
    ]
  )

  # With the tool result in hand, Claude produces a final natural-language
  # answer and stop_reason becomes "end_turn".
  puts "stop_reason: #{followup.stop_reason}"
  followup.content.each do |block|
    puts block.text if block.type == :text
  end

text Output wrap
stop_reason: tool_use
Tool: create_calendar_event
Input: {'title': 'Sync', 'start': '2026-03-30T10:00:00', 'end': '2026-03-30T10:30:00', 'attendees': ['alice@example.com', 'bob@example.com']}
stop_reason: end_turn
I've scheduled your 30-minute sync with Alice and Bob for Monday, March 30 at 10am.
```

The first `stop_reason` is `tool_use` because Claude is waiting for the calendar result. After you send the result, the second `stop_reason` is `end_turn` and the content is natural language for the user.


## Ring 2: The agentic loop

Source: https://platform.claude.com/llms-full.txt#ring-2-the-agentic-loop

Ring 1 assumed Claude would call the tool exactly once. Real tasks often need several calls: Claude might create an event, read the confirmation, then create another. The fix is a `while` loop that keeps running tools and feeding results back until `stop_reason` is no longer `"tool_use"`.

The other change is conversation history. Instead of rebuilding the `messages` array from scratch on each request, keep a running list and append to it. Every turn sees the complete prior context.

<CodeGroup>
  ```bash cURL
  #!/bin/bash
  # Ring 2: The agentic loop.

  TOOLS='[
    {
      "name": "create_calendar_event",
      "description": "Create a calendar event with attendees and optional recurrence.",
      "input_schema": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "start": {"type": "string", "format": "date-time"},
          "end": {"type": "string", "format": "date-time"},
          "attendees": {"type": "array", "items": {"type": "string", "format": "email"}},
          "recurrence": {
            "type": "object",
            "properties": {
              "frequency": {"enum": ["daily", "weekly", "monthly"]},
              "count": {"type": "integer", "minimum": 1}
            }
          }
        },
        "required": ["title", "start", "end"]
      }
    }
  ]'

  run_tool() {
    local name="$1"
    local input="$2"
    if [ "$name" = "create_calendar_event" ]; then
      local title=$(echo "$input" | jq -r '.title')
      jq -n --arg title "$title" '{event_id: "evt_123", status: "created", title: $title}'
    else
      echo "{\"error\": \"Unknown tool: $name\"}"
    fi
  }

  # Keep the full conversation history in a JSON array so each turn sees prior context.
  MESSAGES='[{"role": "user", "content": "Schedule a weekly team standup every Monday at 9am for the next 4 weeks. Invite the whole team: alice@example.com, bob@example.com, carol@example.com."}]'

  call_api() {
    curl -s https://api.anthropic.com/v1/messages \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d "$(jq -n --argjson tools "$TOOLS" --argjson messages "$MESSAGES" \
        '{model: "claude-opus-5", max_tokens: 1024, tools: $tools, tool_choice: {type: "auto", disable_parallel_tool_use: true}, messages: $messages}')"
  }

  RESPONSE=$(call_api)

  # Loop until Claude stops asking for tools. Each iteration runs the requested
  # tool, appends the result to history, and asks Claude to continue.
  while [ "$(echo "$RESPONSE" | jq -r '.stop_reason')" = "tool_use" ]; do
    TOOL_USE=$(echo "$RESPONSE" | jq '.content[] | select(.type == "tool_use")')
    TOOL_NAME=$(echo "$TOOL_USE" | jq -r '.name')
    TOOL_INPUT=$(echo "$TOOL_USE" | jq -c '.input')
    TOOL_USE_ID=$(echo "$TOOL_USE" | jq -r '.id')
    RESULT=$(run_tool "$TOOL_NAME" "$TOOL_INPUT")

    ASSISTANT_CONTENT=$(echo "$RESPONSE" | jq '.content')
    MESSAGES=$(echo "$MESSAGES" | jq \
      --argjson assistant "$ASSISTANT_CONTENT" \
      --arg tool_use_id "$TOOL_USE_ID" \
      --arg result "$RESULT" \
      '. + [
        {role: "assistant", content: $assistant},
        {role: "user", content: [{type: "tool_result", tool_use_id: $tool_use_id, content: $result}]}
      ]')

    RESPONSE=$(call_api)
  done

  echo "$RESPONSE" | jq -r '.content[] | select(.type == "text") | .text'

bash CLI
  #!/usr/bin/env bash
  # Ring 2: The agentic loop.
  # Uses jq for cross-turn message-array state — building an agentic loop in shell
  # requires JSON manipulation beyond ant's single-call --transform scope.
  set -euo pipefail

  run_tool() {
    local name="$1" input="$2"
    if [ "$name" = "create_calendar_event" ]; then
      jq -n --arg title "$(jq -r '.title' <<<"$input")" \
        '{event_id: "evt_123", status: "created", title: $title}'
    else
      printf '{"error": "Unknown tool: %s"}' "$name"
    fi
  }

  # Keep the full conversation history in a JSON array so each turn sees
  # prior context.
  MESSAGES='[{"role": "user", "content": "Schedule a weekly team standup every Monday at 9am for the next 4 weeks. Invite the whole team: alice@example.com, bob@example.com, carol@example.com."}]'

  call_api() {
    # ant reads the request body as YAML on stdin: no auth headers, no
    # hand-built JSON envelope. The static keys (model, tools, tool_choice)
    # live in a quoted heredoc; the growing messages array is appended as
    # JSON, which YAML accepts as flow syntax.
    {
      cat <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tool_choice: {type: auto, disable_parallel_tool_use: true}
  tools:
    - name: create_calendar_event
      description: Create a calendar event with attendees and optional recurrence.
      input_schema:
        type: object
        properties:
          title: {type: string}
          start: {type: string, format: date-time}
          end: {type: string, format: date-time}
          attendees:
            type: array
            items: {type: string, format: email}
          recurrence:
            type: object
            properties:
              frequency: {enum: [daily, weekly, monthly]}
              count: {type: integer, minimum: 1}
        required: [title, start, end]
  YAML
      printf 'messages: %s\n' "$MESSAGES"
    } | ant messages create --format json
  }

  RESPONSE=$(call_api)

  # Loop until Claude stops asking for tools. Each iteration runs the
  # requested tool, appends the result to history, and asks Claude to
  # continue.
  while [ "$(jq -r '.stop_reason' <<<"$RESPONSE")" = "tool_use" ]; do
    TOOL_USE=$(jq '.content[] | select(.type == "tool_use")' <<<"$RESPONSE")
    TOOL_NAME=$(jq -r '.name' <<<"$TOOL_USE")
    TOOL_INPUT=$(jq -c '.input' <<<"$TOOL_USE")
    TOOL_USE_ID=$(jq -r '.id' <<<"$TOOL_USE")
    RESULT=$(run_tool "$TOOL_NAME" "$TOOL_INPUT")

    MESSAGES=$(jq \
      --argjson assistant "$(jq '.content' <<<"$RESPONSE")" \
      --arg tool_use_id "$TOOL_USE_ID" \
      --arg result "$RESULT" \
      '. + [
        {role: "assistant", content: $assistant},
        {role: "user", content: [
          {type: "tool_result", tool_use_id: $tool_use_id, content: $result}
        ]}
      ]' <<<"$MESSAGES")

    RESPONSE=$(call_api)
  done

  jq -r '.content[] | select(.type == "text") | .text' <<<"$RESPONSE"

python Python
  # Ring 2: The agentic loop.

  import json

  import anthropic

  client = anthropic.Anthropic()

  tools = [
      {
          "name": "create_calendar_event",
          "description": "Create a calendar event with attendees and optional recurrence.",
          "input_schema": {
              "type": "object",
              "properties": {
                  "title": {"type": "string"},
                  "start": {"type": "string", "format": "date-time"},
                  "end": {"type": "string", "format": "date-time"},
                  "attendees": {
                      "type": "array",
                      "items": {"type": "string", "format": "email"},
                  },
                  "recurrence": {
                      "type": "object",
                      "properties": {
                          "frequency": {"enum": ["daily", "weekly", "monthly"]},
                          "count": {"type": "integer", "minimum": 1},
                      },
                  },
              },
              "required": ["title", "start", "end"],
          },
      }
  ]


  def run_tool(name, tool_input):
      if name == "create_calendar_event":
          return {"event_id": "evt_123", "status": "created", "title": tool_input["title"]}
      return {"error": f"Unknown tool: {name}"}


  # Keep the full conversation history in a list so each turn sees prior context.
  messages = [
      {
          "role": "user",
          "content": "Schedule a weekly team standup every Monday at 9am for the next 4 weeks. Invite the whole team: alice@example.com, bob@example.com, carol@example.com.",
      }
  ]

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=tools,
      tool_choice={"type": "auto", "disable_parallel_tool_use": True},
      messages=messages,
  )

  # Loop until Claude stops asking for tools. Each iteration runs the requested
  # tool, appends the result to history, and asks Claude to continue.
  while response.stop_reason == "tool_use":
      tool_use = next(block for block in response.content if block.type == "tool_use")
      result = run_tool(tool_use.name, tool_use.input)

      messages.append({"role": "assistant", "content": response.content})
      messages.append(
          {
              "role": "user",
              "content": [
                  {
                      "type": "tool_result",
                      "tool_use_id": tool_use.id,
                      "content": json.dumps(result),
                  }
              ],
          }
      )

      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          tools=tools,
          tool_choice={"type": "auto", "disable_parallel_tool_use": True},
          messages=messages,
      )

  final_text = next(block for block in response.content if block.type == "text")
  print(final_text.text)

typescript TypeScript
  // Ring 2: The agentic loop.

  import Anthropic from "@anthropic-ai/sdk";

  const client = new Anthropic();

  const tools: Anthropic.Tool[] = [
    {
      name: "create_calendar_event",
      description:
        "Create a calendar event with attendees and optional recurrence.",
      input_schema: {
        type: "object",
        properties: {
          title: { type: "string" },
          start: { type: "string", format: "date-time" },
          end: { type: "string", format: "date-time" },
          attendees: {
            type: "array",
            items: { type: "string", format: "email" },
          },
          recurrence: {
            type: "object",
            properties: {
              frequency: { enum: ["daily", "weekly", "monthly"] },
              count: { type: "integer", minimum: 1 },
            },
          },
        },
        required: ["title", "start", "end"],
      },
    },
  ];

  function runTool(name: string, input: Record<string, unknown>) {
    if (name === "create_calendar_event") {
      return { event_id: "evt_123", status: "created", title: input.title };
    }
    return { error: `Unknown tool: ${name}` };
  }

  // Keep the full conversation history so each turn sees prior context.
  const messages: Anthropic.MessageParam[] = [
    {
      role: "user",
      content:
        "Schedule a weekly team standup every Monday at 9am for the next 4 weeks. Invite the whole team: alice@example.com, bob@example.com, carol@example.com.",
    },
  ];

  let response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools,
    tool_choice: { type: "auto", disable_parallel_tool_use: true },
    messages,
  });

  // Loop until Claude stops asking for tools. Each iteration runs the requested
  // tool, appends the result to history, and asks Claude to continue.
  while (response.stop_reason === "tool_use") {
    const toolUse = response.content.find(
      (block): block is Anthropic.ToolUseBlock => block.type === "tool_use",
    )!;
    const result = runTool(toolUse.name, toolUse.input as Record<string, unknown>);

    messages.push({ role: "assistant", content: response.content });
    messages.push({
      role: "user",
      content: [
        {
          type: "tool_result",
          tool_use_id: toolUse.id,
          content: JSON.stringify(result),
        },
      ],
    });

    response = await client.messages.create({
      model: "claude-opus-5",
      max_tokens: 1024,
      tools,
      tool_choice: { type: "auto", disable_parallel_tool_use: true },
      messages,
    });
  }

  for (const block of response.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

csharp C#
  // Ring 2: The agentic loop.

  using System;
  using System.Collections.Generic;
  using System.Linq;
  using System.Text.Json;
  using System.Threading.Tasks;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  List<ToolUnion> tools =
  [
      new ToolUnion(new Tool()
      {
          Name = "create_calendar_event",
          Description = "Create a calendar event with attendees and optional recurrence.",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["title"] = JsonSerializer.SerializeToElement(new { type = "string" }),
                  ["start"] = JsonSerializer.SerializeToElement(new { type = "string", format = "date-time" }),
                  ["end"] = JsonSerializer.SerializeToElement(new { type = "string", format = "date-time" }),
                  ["attendees"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "array",
                      items = new { type = "string", format = "email" },
                  }),
                  ["recurrence"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "object",
                      properties = new
                      {
                          frequency = new { @enum = new[] { "daily", "weekly", "monthly" } },
                          count = new { type = "integer", minimum = 1 },
                      },
                  }),
              },
              Required = ["title", "start", "end"],
          },
      }),
  ];

  // Run the requested tool and return its result as a string.
  string RunTool(ToolUseBlock toolUse)
  {
      if (toolUse.Name == "create_calendar_event")
      {
          var title = toolUse.Input.TryGetValue("title", out var t) ? t.GetString() : "";
          return JsonSerializer.Serialize(new { event_id = "evt_123", status = "created", title });
      }
      return JsonSerializer.Serialize(new { error = $"Unknown tool: {toolUse.Name}" });
  }

  var toolChoice = new ToolChoice(new ToolChoiceAuto { DisableParallelToolUse = true });

  // Keep the full conversation history in a list so each turn sees prior context.
  List<MessageParam> messages =
  [
      new()
      {
          Role = Role.User,
          Content = "Schedule a weekly team standup every Monday at 9am for the next 4 weeks. Invite the whole team: alice@example.com, bob@example.com, carol@example.com.",
      },
  ];

  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = tools,
      ToolChoice = toolChoice,
      Messages = messages,
  });

  // Loop until Claude stops asking for tools. Each iteration runs the requested
  // tool, appends the result to history, and asks Claude to continue.
  while (response.StopReason == StopReason.ToolUse)
  {
      ToolUseBlock? toolUse = null;
      foreach (var block in response.Content)
      {
          if (block.TryPickToolUse(out var picked))
          {
              toolUse = picked;
              break;
          }
      }
      var result = RunTool(toolUse!);

      messages.Add(new()
      {
          Role = Role.Assistant,
          Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList(),
      });
      messages.Add(new()
      {
          Role = Role.User,
          Content = new MessageParamContent(
          [
              new ContentBlockParam(new ToolResultBlockParam() { ToolUseID = toolUse!.ID, Content = result }),
          ]),
      });

      response = await client.Messages.Create(new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Tools = tools,
          ToolChoice = toolChoice,
          Messages = messages,
      });
  }

  foreach (var block in response.Content)
  {
      if (block.TryPickText(out var text))
      {
          Console.WriteLine(text.Text);
      }
  }

go Go
  // Ring 2: The agentic loop.

  package main

  import (
  	"context"
  	"encoding/json"
  	"fmt"
  	"log"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  func runTool(name string, input map[string]any) string {
  	if name == "create_calendar_event" {
  		title, _ := input["title"].(string)
  		return fmt.Sprintf(`{"event_id": "evt_123", "status": "created", "title": %q}`, title)
  	}
  	return fmt.Sprintf(`{"error": "Unknown tool: %s"}`, name)
  }

  func main() {
  	client := anthropic.NewClient()
  	ctx := context.Background()

  	tools := []anthropic.ToolUnionParam{
  		{OfTool: &anthropic.ToolParam{
  			Name:        "create_calendar_event",
  			Description: anthropic.String("Create a calendar event with attendees and optional recurrence."),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"title": map[string]any{"type": "string"},
  					"start": map[string]any{"type": "string", "format": "date-time"},
  					"end":   map[string]any{"type": "string", "format": "date-time"},
  					"attendees": map[string]any{
  						"type":  "array",
  						"items": map[string]any{"type": "string", "format": "email"},
  					},
  					"recurrence": map[string]any{
  						"type": "object",
  						"properties": map[string]any{
  							"frequency": map[string]any{"enum": []string{"daily", "weekly", "monthly"}},
  							"count":     map[string]any{"type": "integer", "minimum": 1},
  						},
  					},
  				},
  				Required: []string{"title", "start", "end"},
  			},
  		}},
  	}

  	toolChoice := anthropic.ToolChoiceUnionParam{
  		OfAuto: &anthropic.ToolChoiceAutoParam{DisableParallelToolUse: anthropic.Bool(true)},
  	}

  	// Keep the full conversation history in a slice so each turn sees prior context.
  	messages := []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock(
  			"Schedule a weekly team standup every Monday at 9am for the next 4 weeks. Invite the whole team: alice@example.com, bob@example.com, carol@example.com.",
  		)),
  	}

  	response, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  		Model:      anthropic.ModelClaudeOpus5,
  		MaxTokens:  1024,
  		Tools:      tools,
  		ToolChoice: toolChoice,
  		Messages:   messages,
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	// Loop until Claude stops asking for tools. Each iteration runs the requested
  	// tool, appends the result to history, and asks Claude to continue.
  	for response.StopReason == "tool_use" {
  		var toolUse anthropic.ContentBlockUnion
  		for _, block := range response.Content {
  			if block.Type == "tool_use" {
  				toolUse = block
  				break
  			}
  		}

  		var input map[string]any
  		if err := json.Unmarshal(toolUse.Input, &input); err != nil {
  			log.Fatal(err)
  		}
  		result := runTool(toolUse.Name, input)

  		var assistantContent []anthropic.ContentBlockParamUnion
  		for _, block := range response.Content {
  			assistantContent = append(assistantContent, block.ToParam())
  		}
  		messages = append(messages, anthropic.NewAssistantMessage(assistantContent...))
  		messages = append(messages, anthropic.NewUserMessage(
  			anthropic.NewToolResultBlock(toolUse.ID, result, false),
  		))

  		response, err = client.Messages.New(ctx, anthropic.MessageNewParams{
  			Model:      anthropic.ModelClaudeOpus5,
  			MaxTokens:  1024,
  			Tools:      tools,
  			ToolChoice: toolChoice,
  			Messages:   messages,
  		})
  		if err != nil {
  			log.Fatal(err)
  		}
  	}

  	for _, block := range response.Content {
  		if block.Type == "text" {
  			fmt.Println(block.Text)
  		}
  	}
  }

java Java
  // Ring 2: The agentic loop.

  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.JsonValue;
  import com.anthropic.models.messages.ContentBlockParam;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.MessageParam;
  import com.anthropic.models.messages.Model;
  import com.anthropic.models.messages.StopReason;
  import com.anthropic.models.messages.Tool;
  import com.anthropic.models.messages.Tool.InputSchema;
  import com.anthropic.models.messages.ToolChoiceAuto;
  import com.anthropic.models.messages.ToolResultBlockParam;
  import com.anthropic.models.messages.ToolUseBlock;
  import java.util.ArrayList;
  import java.util.List;
  import java.util.Map;

  String runTool(ToolUseBlock toolUse) {
      // The raw tool input is a JSON object; read fields out of it as a map.
      Map<String, JsonValue> input = (Map<String, JsonValue>) toolUse._input().asObject().get();
      if (toolUse.name().equals("create_calendar_event")) {
          String title = input.containsKey("title") ? input.get("title").asStringOrThrow() : "";
          return "{\"event_id\": \"evt_123\", \"status\": \"created\", \"title\": \"" + title + "\"}";
      }
      return "{\"error\": \"Unknown tool: " + toolUse.name() + "\"}";
  }

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      Tool calendarTool = Tool.builder()
          .name("create_calendar_event")
          .description("Create a calendar event with attendees and optional recurrence.")
          .inputSchema(InputSchema.builder()
              .properties(JsonValue.from(Map.of(
                  "title", Map.of("type", "string"),
                  "start", Map.of("type", "string", "format", "date-time"),
                  "end", Map.of("type", "string", "format", "date-time"),
                  "attendees", Map.of(
                      "type", "array",
                      "items", Map.of("type", "string", "format", "email")
                  ),
                  "recurrence", Map.of(
                      "type", "object",
                      "properties", Map.of(
                          "frequency", Map.of("enum", List.of("daily", "weekly", "monthly")),
                          "count", Map.of("type", "integer", "minimum", 1)
                      )
                  )
              )))
              .required(List.of("title", "start", "end"))
              .build())
          .build();

      ToolChoiceAuto toolChoice = ToolChoiceAuto.builder()
          .disableParallelToolUse(true)
          .build();

      // Keep the full conversation history in a list so each turn sees prior context.
      List<MessageParam> messages = new ArrayList<>();
      messages.add(MessageParam.builder()
          .role(MessageParam.Role.USER)
          .content("Schedule a weekly team standup every Monday at 9am for the next 4 weeks. Invite the whole team: alice@example.com, bob@example.com, carol@example.com.")
          .build());

      Message response = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addTool(calendarTool)
          .toolChoice(toolChoice)
          .messages(messages)
          .build());

      // Loop until Claude stops asking for tools. Each iteration runs the requested
      // tool, appends the result to history, and asks Claude to continue.
      while (response.stopReason().isPresent()
              && response.stopReason().get().equals(StopReason.TOOL_USE)) {
          ToolUseBlock toolUse = response.content().stream()
              .flatMap(block -> block.toolUse().stream())
              .findFirst()
              .orElseThrow();
          String result = runTool(toolUse);

          messages.add(response.toParam());
          messages.add(MessageParam.builder()
              .role(MessageParam.Role.USER)
              .contentOfBlockParams(List.of(ContentBlockParam.ofToolResult(
                  ToolResultBlockParam.builder()
                      .toolUseId(toolUse.id())
                      .content(result)
                      .build())))
              .build());

          response = client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024L)
              .addTool(calendarTool)
              .toolChoice(toolChoice)
              .messages(messages)
              .build());
      }

      response.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  <?php

  // Ring 2: The agentic loop.

  use Anthropic\Client;
  use Anthropic\Messages\ToolChoiceAuto;

  $client = new Client();

  $tools = [
      [
          'name' => 'create_calendar_event',
          'description' => 'Create a calendar event with attendees and optional recurrence.',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'title' => ['type' => 'string'],
                  'start' => ['type' => 'string', 'format' => 'date-time'],
                  'end' => ['type' => 'string', 'format' => 'date-time'],
                  'attendees' => [
                      'type' => 'array',
                      'items' => ['type' => 'string', 'format' => 'email'],
                  ],
                  'recurrence' => [
                      'type' => 'object',
                      'properties' => [
                          'frequency' => ['enum' => ['daily', 'weekly', 'monthly']],
                          'count' => ['type' => 'integer', 'minimum' => 1],
                      ],
                  ],
              ],
              'required' => ['title', 'start', 'end'],
          ],
      ],
  ];

  function runTool(string $name, array $input): string
  {
      if ($name === 'create_calendar_event') {
          return json_encode([
              'event_id' => 'evt_123',
              'status' => 'created',
              'title' => $input['title'],
          ]);
      }

      return json_encode(['error' => "Unknown tool: {$name}"]);
  }

  $toolChoice = ToolChoiceAuto::with(disableParallelToolUse: true);

  // Keep the full conversation history in an array so each turn sees prior context.
  $messages = [
      [
          'role' => 'user',
          'content' => 'Schedule a weekly team standup every Monday at 9am for the next 4 weeks. Invite the whole team: alice@example.com, bob@example.com, carol@example.com.',
      ],
  ];

  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: $tools,
      toolChoice: $toolChoice,
      messages: $messages,
  );

  // Loop until Claude stops asking for tools. Each iteration runs the requested
  // tool, appends the result to history, and asks Claude to continue.
  while ($response->stopReason === 'tool_use') {
      $toolUse = null;
      foreach ($response->content as $block) {
          if ($block->type === 'tool_use') {
              $toolUse = $block;
              break;
          }
      }

      $result = runTool($toolUse->name, $toolUse->input);

      $messages[] = ['role' => 'assistant', 'content' => $response->content];
      $messages[] = [
          'role' => 'user',
          'content' => [
              [
                  'type' => 'tool_result',
                  'tool_use_id' => $toolUse->id,
                  'content' => $result,
              ],
          ],
      ];

      $response = $client->messages->create(
          model: 'claude-opus-5',
          maxTokens: 1024,
          tools: $tools,
          toolChoice: $toolChoice,
          messages: $messages,
      );
  }

  foreach ($response->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, "\n";
      }
  }

ruby Ruby
  # Ring 2: The agentic loop.

  require "anthropic"

  client = Anthropic::Client.new

  tools = [
    {
      name: "create_calendar_event",
      description: "Create a calendar event with attendees and optional recurrence.",
      input_schema: {
        type: "object",
        properties: {
          title: {type: "string"},
          start: {type: "string", format: "date-time"},
          end: {type: "string", format: "date-time"},
          attendees: {
            type: "array",
            items: {type: "string", format: "email"}
          },
          recurrence: {
            type: "object",
            properties: {
              frequency: {enum: ["daily", "weekly", "monthly"]},
              count: {type: "integer", minimum: 1}
            }
          }
        },
        required: ["title", "start", "end"]
      }
    }
  ]

  def run_tool(name, input)
    case name
    when "create_calendar_event"
      JSON.generate({event_id: "evt_123", status: "created", title: input[:title]})
    else
      JSON.generate({error: "Unknown tool: #{name}"})
    end
  end

  tool_choice = {type: "auto", disable_parallel_tool_use: true}

  # Keep the full conversation history in an array so each turn sees prior context.
  messages = [
    {
      role: "user",
      content: "Schedule a weekly team standup every Monday at 9am for the next 4 weeks. Invite the whole team: alice@example.com, bob@example.com, carol@example.com."
    }
  ]

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: tools,
    tool_choice: tool_choice,
    messages: messages
  )

  # Loop until Claude stops asking for tools. Each iteration runs the requested
  # tool, appends the result to history, and asks Claude to continue.
  while response.stop_reason == :tool_use
    tool_use = response.content.find { |block| block.type == :tool_use }
    result = run_tool(tool_use.name, tool_use.input)

    messages << {role: "assistant", content: response.content}
    messages << {
      role: "user",
      content: [
        {
          type: "tool_result",
          tool_use_id: tool_use.id,
          content: result
        }
      ]
    }

    response = client.messages.create(
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: tools,
      tool_choice: tool_choice,
      messages: messages
    )
  end

  response.content.each do |block|
    puts block.text if block.type == :text
  end

text Output wrap
I've set up your weekly team standup for the next 4 Mondays at 9am with Alice, Bob, and Carol invited.
```

The loop might run once or several times depending on how Claude breaks down the task. Your code no longer needs to know in advance.


## Ring 3: Multiple tools, parallel calls

Source: https://platform.claude.com/llms-full.txt#ring-3-multiple-tools-parallel-calls

Agents rarely have just one capability. Add a second tool, `list_calendar_events`, so Claude can check the existing schedule before creating something new.

When Claude has multiple independent tool calls to make, it might return several `tool_use` blocks in a single response. Your loop needs to process all of them and send back all results together in one user message. Iterate over every `tool_use` block in `response.content`, not just the first.

<CodeGroup>
  ```bash cURL
  #!/bin/bash
  # Ring 3: Multiple tools, parallel calls.

  TOOLS='[
    {
      "name": "create_calendar_event",
      "description": "Create a calendar event with attendees and optional recurrence.",
      "input_schema": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "start": {"type": "string", "format": "date-time"},
          "end": {"type": "string", "format": "date-time"},
          "attendees": {"type": "array", "items": {"type": "string", "format": "email"}},
          "recurrence": {
            "type": "object",
            "properties": {
              "frequency": {"enum": ["daily", "weekly", "monthly"]},
              "count": {"type": "integer", "minimum": 1}
            }
          }
        },
        "required": ["title", "start", "end"]
      }
    },
    {
      "name": "list_calendar_events",
      "description": "List all calendar events on a given date.",
      "input_schema": {
        "type": "object",
        "properties": {"date": {"type": "string", "format": "date"}},
        "required": ["date"]
      }
    }
  ]'

  run_tool() {
    case "$1" in
      create_calendar_event)
        jq -n --arg title "$(echo "$2" | jq -r '.title')" '{event_id: "evt_123", status: "created", title: $title}' ;;
      list_calendar_events)
        echo '{"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}' ;;
      *)
        echo "{\"error\": \"Unknown tool: $1\"}" ;;
    esac
  }

  MESSAGES='[{"role": "user", "content": "Check what I have next Monday, then schedule a planning session that avoids any conflicts."}]'

  call_api() {
    curl -s https://api.anthropic.com/v1/messages \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d "$(jq -n --argjson tools "$TOOLS" --argjson messages "$MESSAGES" \
        '{model: "claude-opus-5", max_tokens: 1024, tools: $tools, messages: $messages}')"
  }

  RESPONSE=$(call_api)

  while [ "$(echo "$RESPONSE" | jq -r '.stop_reason')" = "tool_use" ]; do
    # A single response can contain multiple tool_use blocks. Process all of
    # them and return all results together in one user message.
    TOOL_RESULTS='[]'
    while read -r block; do
      NAME=$(echo "$block" | jq -r '.name')
      INPUT=$(echo "$block" | jq -c '.input')
      ID=$(echo "$block" | jq -r '.id')
      RESULT=$(run_tool "$NAME" "$INPUT")
      TOOL_RESULTS=$(echo "$TOOL_RESULTS" | jq --arg id "$ID" --arg result "$RESULT" \
        '. + [{type: "tool_result", tool_use_id: $id, content: $result}]')
    done < <(echo "$RESPONSE" | jq -c '.content[] | select(.type == "tool_use")')

    MESSAGES=$(echo "$MESSAGES" | jq \
      --argjson assistant "$(echo "$RESPONSE" | jq '.content')" \
      --argjson results "$TOOL_RESULTS" \
      '. + [{role: "assistant", content: $assistant}, {role: "user", content: $results}]')

    RESPONSE=$(call_api)
  done

  echo "$RESPONSE" | jq -r '.content[] | select(.type == "text") | .text'

bash CLI
  #!/usr/bin/env bash
  # Ring 3: Multiple tools, parallel calls.
  # Uses jq for cross-turn message-array state — building an agentic loop in shell
  # requires JSON manipulation beyond ant's single-call --transform scope.
  set -euo pipefail

  run_tool() {
    case "$1" in
      create_calendar_event)
        jq -n --arg title "$(jq -r '.title' <<<"$2")" \
          '{event_id: "evt_123", status: "created", title: $title}' ;;
      list_calendar_events)
        echo '{"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}' ;;
      *)
        printf '{"error": "Unknown tool: %s"}' "$1" ;;
    esac
  }

  MESSAGES='[{"role": "user", "content": "Check what I have next Monday, then schedule a planning session that avoids any conflicts."}]'

  call_api() {
    # ant reads the request body as YAML on stdin: no auth headers, no
    # hand-built JSON envelope. The static keys (model, tools) live in a
    # quoted heredoc; the growing messages array is appended as JSON,
    # which YAML accepts as flow syntax.
    {
      cat <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tools:
    - name: create_calendar_event
      description: Create a calendar event with attendees and optional recurrence.
      input_schema:
        type: object
        properties:
          title: {type: string}
          start: {type: string, format: date-time}
          end: {type: string, format: date-time}
          attendees:
            type: array
            items: {type: string, format: email}
          recurrence:
            type: object
            properties:
              frequency: {enum: [daily, weekly, monthly]}
              count: {type: integer, minimum: 1}
        required: [title, start, end]
    - name: list_calendar_events
      description: List all calendar events on a given date.
      input_schema:
        type: object
        properties:
          date: {type: string, format: date}
        required: [date]
  YAML
      printf 'messages: %s\n' "$MESSAGES"
    } | ant messages create --format json
  }

  RESPONSE=$(call_api)

  while [ "$(jq -r '.stop_reason' <<<"$RESPONSE")" = "tool_use" ]; do
    # A single response can contain multiple tool_use blocks. Process all
    # of them and return all results together in one user message.
    TOOL_RESULTS='[]'
    while read -r block; do
      NAME=$(jq -r '.name' <<<"$block")
      INPUT=$(jq -c '.input' <<<"$block")
      ID=$(jq -r '.id' <<<"$block")
      RESULT=$(run_tool "$NAME" "$INPUT")
      TOOL_RESULTS=$(jq --arg id "$ID" --arg result "$RESULT" \
        '. + [{type: "tool_result", tool_use_id: $id, content: $result}]' \
        <<<"$TOOL_RESULTS")
    done < <(jq -c '.content[] | select(.type == "tool_use")' <<<"$RESPONSE")

    MESSAGES=$(jq \
      --argjson assistant "$(jq '.content' <<<"$RESPONSE")" \
      --argjson results "$TOOL_RESULTS" \
      '. + [
        {role: "assistant", content: $assistant},
        {role: "user", content: $results}
      ]' <<<"$MESSAGES")

    RESPONSE=$(call_api)
  done

  jq -r '.content[] | select(.type == "text") | .text' <<<"$RESPONSE"

python Python
  # Ring 3: Multiple tools, parallel calls.

  import json

  import anthropic

  client = anthropic.Anthropic()

  tools = [
      {
          "name": "create_calendar_event",
          "description": "Create a calendar event with attendees and optional recurrence.",
          "input_schema": {
              "type": "object",
              "properties": {
                  "title": {"type": "string"},
                  "start": {"type": "string", "format": "date-time"},
                  "end": {"type": "string", "format": "date-time"},
                  "attendees": {
                      "type": "array",
                      "items": {"type": "string", "format": "email"},
                  },
                  "recurrence": {
                      "type": "object",
                      "properties": {
                          "frequency": {"enum": ["daily", "weekly", "monthly"]},
                          "count": {"type": "integer", "minimum": 1},
                      },
                  },
              },
              "required": ["title", "start", "end"],
          },
      },
      {
          "name": "list_calendar_events",
          "description": "List all calendar events on a given date.",
          "input_schema": {
              "type": "object",
              "properties": {
                  "date": {"type": "string", "format": "date"},
              },
              "required": ["date"],
          },
      },
  ]


  def run_tool(name, tool_input):
      if name == "create_calendar_event":
          return {"event_id": "evt_123", "status": "created", "title": tool_input["title"]}
      if name == "list_calendar_events":
          return {"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}
      return {"error": f"Unknown tool: {name}"}


  messages = [
      {
          "role": "user",
          "content": "Check what I have next Monday, then schedule a planning session that avoids any conflicts.",
      }
  ]

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=tools,
      messages=messages,
  )

  while response.stop_reason == "tool_use":
      # A single response can contain multiple tool_use blocks. Process all of
      # them and return all results together in one user message.
      tool_results = []
      for block in response.content:
          if block.type == "tool_use":
              result = run_tool(block.name, block.input)
              tool_results.append(
                  {
                      "type": "tool_result",
                      "tool_use_id": block.id,
                      "content": json.dumps(result),
                  }
              )

      messages.append({"role": "assistant", "content": response.content})
      messages.append({"role": "user", "content": tool_results})

      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          tools=tools,
          messages=messages,
      )

  final_text = next(block for block in response.content if block.type == "text")
  print(final_text.text)

typescript TypeScript
  // Ring 3: Multiple tools, parallel calls.

  import Anthropic from "@anthropic-ai/sdk";

  const client = new Anthropic();

  const tools: Anthropic.Tool[] = [
    {
      name: "create_calendar_event",
      description:
        "Create a calendar event with attendees and optional recurrence.",
      input_schema: {
        type: "object",
        properties: {
          title: { type: "string" },
          start: { type: "string", format: "date-time" },
          end: { type: "string", format: "date-time" },
          attendees: {
            type: "array",
            items: { type: "string", format: "email" },
          },
          recurrence: {
            type: "object",
            properties: {
              frequency: { enum: ["daily", "weekly", "monthly"] },
              count: { type: "integer", minimum: 1 },
            },
          },
        },
        required: ["title", "start", "end"],
      },
    },
    {
      name: "list_calendar_events",
      description: "List all calendar events on a given date.",
      input_schema: {
        type: "object",
        properties: {
          date: { type: "string", format: "date" },
        },
        required: ["date"],
      },
    },
  ];

  function runTool(name: string, input: Record<string, unknown>) {
    if (name === "create_calendar_event") {
      return { event_id: "evt_123", status: "created", title: input.title };
    }
    if (name === "list_calendar_events") {
      return {
        events: [{ title: "Existing meeting", start: "14:00", end: "15:00" }],
      };
    }
    return { error: `Unknown tool: ${name}` };
  }

  const messages: Anthropic.MessageParam[] = [
    {
      role: "user",
      content:
        "Check what I have next Monday, then schedule a planning session that avoids any conflicts.",
    },
  ];

  let response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools,
    messages,
  });

  while (response.stop_reason === "tool_use") {
    // A single response can contain multiple tool_use blocks. Process all of
    // them and return all results together in one user message.
    const toolResults: Anthropic.ToolResultBlockParam[] = [];
    for (const block of response.content) {
      if (block.type === "tool_use") {
        const result = runTool(block.name, block.input as Record<string, unknown>);
        toolResults.push({
          type: "tool_result",
          tool_use_id: block.id,
          content: JSON.stringify(result),
        });
      }
    }

    messages.push({ role: "assistant", content: response.content });
    messages.push({ role: "user", content: toolResults });

    response = await client.messages.create({
      model: "claude-opus-5",
      max_tokens: 1024,
      tools,
      messages,
    });
  }

  for (const block of response.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

csharp C#
  // Ring 3: Multiple tools, parallel calls.

  using System;
  using System.Collections.Generic;
  using System.Linq;
  using System.Text.Json;
  using System.Threading.Tasks;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  List<ToolUnion> tools =
  [
      new ToolUnion(new Tool()
      {
          Name = "create_calendar_event",
          Description = "Create a calendar event with attendees and optional recurrence.",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["title"] = JsonSerializer.SerializeToElement(new { type = "string" }),
                  ["start"] = JsonSerializer.SerializeToElement(new { type = "string", format = "date-time" }),
                  ["end"] = JsonSerializer.SerializeToElement(new { type = "string", format = "date-time" }),
                  ["attendees"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "array",
                      items = new { type = "string", format = "email" },
                  }),
                  ["recurrence"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "object",
                      properties = new
                      {
                          frequency = new { @enum = new[] { "daily", "weekly", "monthly" } },
                          count = new { type = "integer", minimum = 1 },
                      },
                  }),
              },
              Required = ["title", "start", "end"],
          },
      }),
      new ToolUnion(new Tool()
      {
          Name = "list_calendar_events",
          Description = "List all calendar events on a given date.",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["date"] = JsonSerializer.SerializeToElement(new { type = "string", format = "date" }),
              },
              Required = ["date"],
          },
      }),
  ];

  string RunTool(ToolUseBlock toolUse)
  {
      if (toolUse.Name == "create_calendar_event")
      {
          var title = toolUse.Input.TryGetValue("title", out var t) ? t.GetString() : "";
          return JsonSerializer.Serialize(new { event_id = "evt_123", status = "created", title });
      }
      if (toolUse.Name == "list_calendar_events")
      {
          return """{"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}""";
      }
      return JsonSerializer.Serialize(new { error = $"Unknown tool: {toolUse.Name}" });
  }

  List<MessageParam> messages =
  [
      new()
      {
          Role = Role.User,
          Content = "Check what I have next Monday, then schedule a planning session that avoids any conflicts.",
      },
  ];

  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = tools,
      Messages = messages,
  });

  while (response.StopReason == StopReason.ToolUse)
  {
      // A single response can contain multiple tool_use blocks. Process all of
      // them and return all results together in one user message.
      List<ContentBlockParam> toolResults = [];
      foreach (var block in response.Content)
      {
          if (block.TryPickToolUse(out var toolUse))
          {
              toolResults.Add(new ContentBlockParam(new ToolResultBlockParam()
              {
                  ToolUseID = toolUse.ID,
                  Content = RunTool(toolUse),
              }));
          }
      }

      messages.Add(new()
      {
          Role = Role.Assistant,
          Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList(),
      });
      messages.Add(new() { Role = Role.User, Content = new MessageParamContent(toolResults) });

      response = await client.Messages.Create(new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Tools = tools,
          Messages = messages,
      });
  }

  foreach (var block in response.Content)
  {
      if (block.TryPickText(out var text))
      {
          Console.WriteLine(text.Text);
      }
  }

go Go
  // Ring 3: Multiple tools, parallel calls.

  package main

  import (
  	"context"
  	"encoding/json"
  	"fmt"
  	"log"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  func runTool(name string, input map[string]any) string {
  	if name == "create_calendar_event" {
  		title, _ := input["title"].(string)
  		return fmt.Sprintf(`{"event_id": "evt_123", "status": "created", "title": %q}`, title)
  	}
  	if name == "list_calendar_events" {
  		return `{"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}`
  	}
  	return fmt.Sprintf(`{"error": "Unknown tool: %s"}`, name)
  }

  func main() {
  	client := anthropic.NewClient()
  	ctx := context.Background()

  	tools := []anthropic.ToolUnionParam{
  		{OfTool: &anthropic.ToolParam{
  			Name:        "create_calendar_event",
  			Description: anthropic.String("Create a calendar event with attendees and optional recurrence."),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"title": map[string]any{"type": "string"},
  					"start": map[string]any{"type": "string", "format": "date-time"},
  					"end":   map[string]any{"type": "string", "format": "date-time"},
  					"attendees": map[string]any{
  						"type":  "array",
  						"items": map[string]any{"type": "string", "format": "email"},
  					},
  					"recurrence": map[string]any{
  						"type": "object",
  						"properties": map[string]any{
  							"frequency": map[string]any{"enum": []string{"daily", "weekly", "monthly"}},
  							"count":     map[string]any{"type": "integer", "minimum": 1},
  						},
  					},
  				},
  				Required: []string{"title", "start", "end"},
  			},
  		}},
  		{OfTool: &anthropic.ToolParam{
  			Name:        "list_calendar_events",
  			Description: anthropic.String("List all calendar events on a given date."),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"date": map[string]any{"type": "string", "format": "date"},
  				},
  				Required: []string{"date"},
  			},
  		}},
  	}

  	messages := []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock(
  			"Check what I have next Monday, then schedule a planning session that avoids any conflicts.",
  		)),
  	}

  	response, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 1024,
  		Tools:     tools,
  		Messages:  messages,
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	for response.StopReason == "tool_use" {
  		// A single response can contain multiple tool_use blocks. Process all of
  		// them and return all results together in one user message.
  		var toolResults []anthropic.ContentBlockParamUnion
  		for _, block := range response.Content {
  			if block.Type == "tool_use" {
  				var input map[string]any
  				if err := json.Unmarshal(block.Input, &input); err != nil {
  					log.Fatal(err)
  				}
  				result := runTool(block.Name, input)
  				toolResults = append(toolResults, anthropic.NewToolResultBlock(block.ID, result, false))
  			}
  		}

  		var assistantContent []anthropic.ContentBlockParamUnion
  		for _, block := range response.Content {
  			assistantContent = append(assistantContent, block.ToParam())
  		}
  		messages = append(messages, anthropic.NewAssistantMessage(assistantContent...))
  		messages = append(messages, anthropic.NewUserMessage(toolResults...))

  		response, err = client.Messages.New(ctx, anthropic.MessageNewParams{
  			Model:     anthropic.ModelClaudeOpus5,
  			MaxTokens: 1024,
  			Tools:     tools,
  			Messages:  messages,
  		})
  		if err != nil {
  			log.Fatal(err)
  		}
  	}

  	for _, block := range response.Content {
  		if block.Type == "text" {
  			fmt.Println(block.Text)
  		}
  	}
  }

java Java
  // Ring 3: Multiple tools, parallel calls.

  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.JsonValue;
  import com.anthropic.models.messages.ContentBlock;
  import com.anthropic.models.messages.ContentBlockParam;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.MessageParam;
  import com.anthropic.models.messages.Model;
  import com.anthropic.models.messages.StopReason;
  import com.anthropic.models.messages.Tool;
  import com.anthropic.models.messages.Tool.InputSchema;
  import com.anthropic.models.messages.ToolResultBlockParam;
  import com.anthropic.models.messages.ToolUseBlock;
  import java.util.ArrayList;
  import java.util.List;
  import java.util.Map;

  String runTool(ToolUseBlock toolUse) {
      // The raw tool input is a JSON object; read fields out of it as a map.
      Map<String, JsonValue> input = (Map<String, JsonValue>) toolUse._input().asObject().get();
      if (toolUse.name().equals("create_calendar_event")) {
          String title = input.containsKey("title") ? input.get("title").asStringOrThrow() : "";
          return "{\"event_id\": \"evt_123\", \"status\": \"created\", \"title\": \"" + title + "\"}";
      }
      if (toolUse.name().equals("list_calendar_events")) {
          return "{\"events\": [{\"title\": \"Existing meeting\", \"start\": \"14:00\", \"end\": \"15:00\"}]}";
      }
      return "{\"error\": \"Unknown tool: " + toolUse.name() + "\"}";
  }

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      Tool calendarTool = Tool.builder()
          .name("create_calendar_event")
          .description("Create a calendar event with attendees and optional recurrence.")
          .inputSchema(InputSchema.builder()
              .properties(JsonValue.from(Map.of(
                  "title", Map.of("type", "string"),
                  "start", Map.of("type", "string", "format", "date-time"),
                  "end", Map.of("type", "string", "format", "date-time"),
                  "attendees", Map.of(
                      "type", "array",
                      "items", Map.of("type", "string", "format", "email")
                  ),
                  "recurrence", Map.of(
                      "type", "object",
                      "properties", Map.of(
                          "frequency", Map.of("enum", List.of("daily", "weekly", "monthly")),
                          "count", Map.of("type", "integer", "minimum", 1)
                      )
                  )
              )))
              .required(List.of("title", "start", "end"))
              .build())
          .build();

      Tool listTool = Tool.builder()
          .name("list_calendar_events")
          .description("List all calendar events on a given date.")
          .inputSchema(InputSchema.builder()
              .properties(JsonValue.from(Map.of(
                  "date", Map.of("type", "string", "format", "date")
              )))
              .required(List.of("date"))
              .build())
          .build();

      List<MessageParam> messages = new ArrayList<>();
      messages.add(MessageParam.builder()
          .role(MessageParam.Role.USER)
          .content("Check what I have next Monday, then schedule a planning session that avoids any conflicts.")
          .build());

      Message response = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addTool(calendarTool)
          .addTool(listTool)
          .messages(messages)
          .build());

      while (response.stopReason().isPresent()
              && response.stopReason().get().equals(StopReason.TOOL_USE)) {
          // A single response can contain multiple tool_use blocks. Process all of
          // them and return all results together in one user message.
          List<ContentBlockParam> toolResults = new ArrayList<>();
          for (ContentBlock block : response.content()) {
              if (block.toolUse().isPresent()) {
                  ToolUseBlock toolUse = block.toolUse().get();
                  toolResults.add(ContentBlockParam.ofToolResult(
                      ToolResultBlockParam.builder()
                          .toolUseId(toolUse.id())
                          .content(runTool(toolUse))
                          .build()));
              }
          }

          messages.add(response.toParam());
          messages.add(MessageParam.builder()
              .role(MessageParam.Role.USER)
              .contentOfBlockParams(toolResults)
              .build());

          response = client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024L)
              .addTool(calendarTool)
              .addTool(listTool)
              .messages(messages)
              .build());
      }

      response.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  <?php

  // Ring 3: Multiple tools, parallel calls.

  use Anthropic\Client;

  $client = new Client();

  $tools = [
      [
          'name' => 'create_calendar_event',
          'description' => 'Create a calendar event with attendees and optional recurrence.',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'title' => ['type' => 'string'],
                  'start' => ['type' => 'string', 'format' => 'date-time'],
                  'end' => ['type' => 'string', 'format' => 'date-time'],
                  'attendees' => [
                      'type' => 'array',
                      'items' => ['type' => 'string', 'format' => 'email'],
                  ],
                  'recurrence' => [
                      'type' => 'object',
                      'properties' => [
                          'frequency' => ['enum' => ['daily', 'weekly', 'monthly']],
                          'count' => ['type' => 'integer', 'minimum' => 1],
                      ],
                  ],
              ],
              'required' => ['title', 'start', 'end'],
          ],
      ],
      [
          'name' => 'list_calendar_events',
          'description' => 'List all calendar events on a given date.',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'date' => ['type' => 'string', 'format' => 'date'],
              ],
              'required' => ['date'],
          ],
      ],
  ];

  function runTool(string $name, array $input): string
  {
      if ($name === 'create_calendar_event') {
          return json_encode([
              'event_id' => 'evt_123',
              'status' => 'created',
              'title' => $input['title'],
          ]);
      }
      if ($name === 'list_calendar_events') {
          return json_encode([
              'events' => [['title' => 'Existing meeting', 'start' => '14:00', 'end' => '15:00']],
          ]);
      }

      return json_encode(['error' => "Unknown tool: {$name}"]);
  }

  $messages = [
      [
          'role' => 'user',
          'content' => 'Check what I have next Monday, then schedule a planning session that avoids any conflicts.',
      ],
  ];

  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: $tools,
      messages: $messages,
  );

  while ($response->stopReason === 'tool_use') {
      // A single response can contain multiple tool_use blocks. Process all of
      // them and return all results together in one user message.
      $toolResults = [];
      foreach ($response->content as $block) {
          if ($block->type === 'tool_use') {
              $toolResults[] = [
                  'type' => 'tool_result',
                  'tool_use_id' => $block->id,
                  'content' => runTool($block->name, $block->input),
              ];
          }
      }

      $messages[] = ['role' => 'assistant', 'content' => $response->content];
      $messages[] = ['role' => 'user', 'content' => $toolResults];

      $response = $client->messages->create(
          model: 'claude-opus-5',
          maxTokens: 1024,
          tools: $tools,
          messages: $messages,
      );
  }

  foreach ($response->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, "\n";
      }
  }

ruby Ruby
  # Ring 3: Multiple tools, parallel calls.

  require "anthropic"

  client = Anthropic::Client.new

  tools = [
    {
      name: "create_calendar_event",
      description: "Create a calendar event with attendees and optional recurrence.",
      input_schema: {
        type: "object",
        properties: {
          title: {type: "string"},
          start: {type: "string", format: "date-time"},
          end: {type: "string", format: "date-time"},
          attendees: {
            type: "array",
            items: {type: "string", format: "email"}
          },
          recurrence: {
            type: "object",
            properties: {
              frequency: {enum: ["daily", "weekly", "monthly"]},
              count: {type: "integer", minimum: 1}
            }
          }
        },
        required: ["title", "start", "end"]
      }
    },
    {
      name: "list_calendar_events",
      description: "List all calendar events on a given date.",
      input_schema: {
        type: "object",
        properties: {
          date: {type: "string", format: "date"}
        },
        required: ["date"]
      }
    }
  ]

  def run_tool(name, input)
    case name
    when "create_calendar_event"
      JSON.generate({event_id: "evt_123", status: "created", title: input[:title]})
    when "list_calendar_events"
      JSON.generate({events: [{title: "Existing meeting", start: "14:00", end: "15:00"}]})
    else
      JSON.generate({error: "Unknown tool: #{name}"})
    end
  end

  messages = [
    {
      role: "user",
      content: "Check what I have next Monday, then schedule a planning session that avoids any conflicts."
    }
  ]

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: tools,
    messages: messages
  )

  while response.stop_reason == :tool_use
    # A single response can contain multiple tool_use blocks. Process all of
    # them and return all results together in one user message.
    tool_results = response.content.select { |block| block.type == :tool_use }.map do |tool_use|
      {
        type: "tool_result",
        tool_use_id: tool_use.id,
        content: run_tool(tool_use.name, tool_use.input)
      }
    end

    messages << {role: "assistant", content: response.content}
    messages << {role: "user", content: tool_results}

    response = client.messages.create(
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: tools,
      messages: messages
    )
  end

  response.content.each do |block|
    puts block.text if block.type == :text
  end

text Output wrap
I checked your calendar for next Monday and found an existing meeting from 2pm to 3pm. I've scheduled the planning session for 10am to 11am to avoid the conflict.
```

For more on concurrent execution and ordering guarantees, see [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use).


## Ring 4: Error handling

Source: https://platform.claude.com/llms-full.txt#ring-4-error-handling

Tools fail. A calendar API might reject an event with too many attendees, or a date might be malformed. When a tool raises an error, send the error message back with `is_error: true` instead of crashing. Claude reads the error and can retry with corrected input, ask the user for clarification, or explain the limitation.

<CodeGroup>
  ```bash cURL
  #!/bin/bash
  # Ring 4: Error handling.

  TOOLS='[
    {
      "name": "create_calendar_event",
      "description": "Create a calendar event with attendees and optional recurrence.",
      "input_schema": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "start": {"type": "string", "format": "date-time"},
          "end": {"type": "string", "format": "date-time"},
          "attendees": {"type": "array", "items": {"type": "string", "format": "email"}},
          "recurrence": {
            "type": "object",
            "properties": {
              "frequency": {"enum": ["daily", "weekly", "monthly"]},
              "count": {"type": "integer", "minimum": 1}
            }
          }
        },
        "required": ["title", "start", "end"]
      }
    },
    {
      "name": "list_calendar_events",
      "description": "List all calendar events on a given date.",
      "input_schema": {
        "type": "object",
        "properties": {"date": {"type": "string", "format": "date"}},
        "required": ["date"]
      }
    }
  ]'

  run_tool() {
    case "$1" in
      create_calendar_event)
        local count=$(echo "$2" | jq '.attendees | length // 0')
        if [ "$count" -gt 10 ]; then
          echo "ERROR: Too many attendees (max 10)"
          return 1
        fi
        jq -n --arg title "$(echo "$2" | jq -r '.title')" '{event_id: "evt_123", status: "created", title: $title}' ;;
      list_calendar_events)
        echo '{"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}' ;;
      *)
        echo "ERROR: Unknown tool: $1"
        return 1 ;;
    esac
  }

  EMAILS=$(seq 0 14 | sed 's/.*/user&@example.com/' | paste -sd, -)
  MESSAGES="[{\"role\": \"user\", \"content\": \"Schedule an all-hands with everyone: $EMAILS\"}]"

  call_api() {
    curl -s https://api.anthropic.com/v1/messages \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d "$(jq -n --argjson tools "$TOOLS" --argjson messages "$MESSAGES" \
        '{model: "claude-opus-5", max_tokens: 1024, tools: $tools, messages: $messages}')"
  }

  RESPONSE=$(call_api)

  while [ "$(echo "$RESPONSE" | jq -r '.stop_reason')" = "tool_use" ]; do
    TOOL_RESULTS='[]'
    while read -r block; do
      NAME=$(echo "$block" | jq -r '.name')
      INPUT=$(echo "$block" | jq -c '.input')
      ID=$(echo "$block" | jq -r '.id')
      if OUTPUT=$(run_tool "$NAME" "$INPUT"); then
        TOOL_RESULTS=$(echo "$TOOL_RESULTS" | jq --arg id "$ID" --arg result "$OUTPUT" \
          '. + [{type: "tool_result", tool_use_id: $id, content: $result}]')
      else
        # Signal failure so Claude can retry or ask for clarification.
        TOOL_RESULTS=$(echo "$TOOL_RESULTS" | jq --arg id "$ID" --arg result "$OUTPUT" \
          '. + [{type: "tool_result", tool_use_id: $id, content: $result, is_error: true}]')
      fi
    done < <(echo "$RESPONSE" | jq -c '.content[] | select(.type == "tool_use")')

    MESSAGES=$(echo "$MESSAGES" | jq \
      --argjson assistant "$(echo "$RESPONSE" | jq '.content')" \
      --argjson results "$TOOL_RESULTS" \
      '. + [{role: "assistant", content: $assistant}, {role: "user", content: $results}]')

    RESPONSE=$(call_api)
  done

  echo "$RESPONSE" | jq -r '.content[] | select(.type == "text") | .text'

bash CLI
  #!/usr/bin/env bash
  # Ring 4: Error handling.
  # Uses jq for cross-turn message-array state — building an agentic loop in shell
  # requires JSON manipulation beyond ant's single-call --transform scope.
  set -euo pipefail

  run_tool() {
    case "$1" in
      create_calendar_event)
        local count
        count=$(jq '.attendees | length // 0' <<<"$2")
        if [ "$count" -gt 10 ]; then
          echo "ERROR: Too many attendees (max 10)"
          return 1
        fi
        jq -n --arg title "$(jq -r '.title' <<<"$2")" \
          '{event_id: "evt_123", status: "created", title: $title}' ;;
      list_calendar_events)
        echo '{"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}' ;;
      *)
        echo "ERROR: Unknown tool: $1"
        return 1 ;;
    esac
  }

  EMAILS=$(seq 0 14 | sed 's/.*/user&@example.com/' | paste -sd, -)
  MESSAGES=$(jq -n --arg msg "Schedule an all-hands with everyone: $EMAILS" \
    '[{role: "user", content: $msg}]')

  call_api() {
    # ant reads the request body as YAML on stdin: no auth headers, no
    # hand-built JSON envelope. The static keys (model, tools) live in a
    # quoted heredoc; the growing messages array is appended as JSON,
    # which YAML accepts as flow syntax.
    {
      cat <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tools:
    - name: create_calendar_event
      description: Create a calendar event with attendees and optional recurrence.
      input_schema:
        type: object
        properties:
          title: {type: string}
          start: {type: string, format: date-time}
          end: {type: string, format: date-time}
          attendees:
            type: array
            items: {type: string, format: email}
          recurrence:
            type: object
            properties:
              frequency: {enum: [daily, weekly, monthly]}
              count: {type: integer, minimum: 1}
        required: [title, start, end]
    - name: list_calendar_events
      description: List all calendar events on a given date.
      input_schema:
        type: object
        properties:
          date: {type: string, format: date}
        required: [date]
  YAML
      printf 'messages: %s\n' "$MESSAGES"
    } | ant messages create --format json
  }

  RESPONSE=$(call_api)

  while [ "$(jq -r '.stop_reason' <<<"$RESPONSE")" = "tool_use" ]; do
    TOOL_RESULTS='[]'
    while read -r block; do
      NAME=$(jq -r '.name' <<<"$block")
      INPUT=$(jq -c '.input' <<<"$block")
      ID=$(jq -r '.id' <<<"$block")
      if OUTPUT=$(run_tool "$NAME" "$INPUT"); then
        TOOL_RESULTS=$(jq --arg id "$ID" --arg result "$OUTPUT" \
          '. + [{type: "tool_result", tool_use_id: $id, content: $result}]' \
          <<<"$TOOL_RESULTS")
      else
        # Signal failure so Claude can retry or ask for clarification.
        TOOL_RESULTS=$(jq --arg id "$ID" --arg result "$OUTPUT" \
          '. + [{type: "tool_result", tool_use_id: $id, content: $result, is_error: true}]' \
          <<<"$TOOL_RESULTS")
      fi
    done < <(jq -c '.content[] | select(.type == "tool_use")' <<<"$RESPONSE")

    MESSAGES=$(jq \
      --argjson assistant "$(jq '.content' <<<"$RESPONSE")" \
      --argjson results "$TOOL_RESULTS" \
      '. + [
        {role: "assistant", content: $assistant},
        {role: "user", content: $results}
      ]' <<<"$MESSAGES")

    RESPONSE=$(call_api)
  done

  jq -r '.content[] | select(.type == "text") | .text' <<<"$RESPONSE"

python Python
  # Ring 4: Error handling.

  import json

  import anthropic

  client = anthropic.Anthropic()

  tools = [
      {
          "name": "create_calendar_event",
          "description": "Create a calendar event with attendees and optional recurrence.",
          "input_schema": {
              "type": "object",
              "properties": {
                  "title": {"type": "string"},
                  "start": {"type": "string", "format": "date-time"},
                  "end": {"type": "string", "format": "date-time"},
                  "attendees": {
                      "type": "array",
                      "items": {"type": "string", "format": "email"},
                  },
                  "recurrence": {
                      "type": "object",
                      "properties": {
                          "frequency": {"enum": ["daily", "weekly", "monthly"]},
                          "count": {"type": "integer", "minimum": 1},
                      },
                  },
              },
              "required": ["title", "start", "end"],
          },
      },
      {
          "name": "list_calendar_events",
          "description": "List all calendar events on a given date.",
          "input_schema": {
              "type": "object",
              "properties": {
                  "date": {"type": "string", "format": "date"},
              },
              "required": ["date"],
          },
      },
  ]


  def run_tool(name, tool_input):
      if name == "create_calendar_event":
          if "attendees" in tool_input and len(tool_input["attendees"]) > 10:
              raise ValueError("Too many attendees (max 10)")
          return {"event_id": "evt_123", "status": "created", "title": tool_input["title"]}
      if name == "list_calendar_events":
          return {"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}
      raise ValueError(f"Unknown tool: {name}")


  messages = [
      {
          "role": "user",
          "content": "Schedule an all-hands with everyone: " + ", ".join(f"user{i}@example.com" for i in range(15)),
      }
  ]

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=tools,
      messages=messages,
  )

  while response.stop_reason == "tool_use":
      tool_results = []
      for block in response.content:
          if block.type == "tool_use":
              try:
                  result = run_tool(block.name, block.input)
                  tool_results.append(
                      {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}
                  )
              except Exception as exc:
                  # Signal failure so Claude can retry or ask for clarification.
                  tool_results.append(
                      {
                          "type": "tool_result",
                          "tool_use_id": block.id,
                          "content": str(exc),
                          "is_error": True,
                      }
                  )

      messages.append({"role": "assistant", "content": response.content})
      messages.append({"role": "user", "content": tool_results})

      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          tools=tools,
          messages=messages,
      )

  final_text = next(block for block in response.content if block.type == "text")
  print(final_text.text)

typescript TypeScript
  // Ring 4: Error handling.

  import Anthropic from "@anthropic-ai/sdk";

  const client = new Anthropic();

  const tools: Anthropic.Tool[] = [
    {
      name: "create_calendar_event",
      description:
        "Create a calendar event with attendees and optional recurrence.",
      input_schema: {
        type: "object",
        properties: {
          title: { type: "string" },
          start: { type: "string", format: "date-time" },
          end: { type: "string", format: "date-time" },
          attendees: {
            type: "array",
            items: { type: "string", format: "email" },
          },
          recurrence: {
            type: "object",
            properties: {
              frequency: { enum: ["daily", "weekly", "monthly"] },
              count: { type: "integer", minimum: 1 },
            },
          },
        },
        required: ["title", "start", "end"],
      },
    },
    {
      name: "list_calendar_events",
      description: "List all calendar events on a given date.",
      input_schema: {
        type: "object",
        properties: {
          date: { type: "string", format: "date" },
        },
        required: ["date"],
      },
    },
  ];

  function runTool(name: string, input: Record<string, unknown>) {
    if (name === "create_calendar_event") {
      const attendees = input.attendees as string[] | undefined;
      if (attendees && attendees.length > 10) {
        throw new Error("Too many attendees (max 10)");
      }
      return { event_id: "evt_123", status: "created", title: input.title };
    }
    if (name === "list_calendar_events") {
      return {
        events: [{ title: "Existing meeting", start: "14:00", end: "15:00" }],
      };
    }
    throw new Error(`Unknown tool: ${name}`);
  }

  const emails = Array.from({ length: 15 }, (_, i) => `user${i}@example.com`);
  const messages: Anthropic.MessageParam[] = [
    {
      role: "user",
      content: `Schedule an all-hands with everyone: ${emails.join(", ")}`,
    },
  ];

  let response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools,
    messages,
  });

  while (response.stop_reason === "tool_use") {
    const toolResults: Anthropic.ToolResultBlockParam[] = [];
    for (const block of response.content) {
      if (block.type === "tool_use") {
        try {
          const result = runTool(block.name, block.input as Record<string, unknown>);
          toolResults.push({
            type: "tool_result",
            tool_use_id: block.id,
            content: JSON.stringify(result),
          });
        } catch (err) {
          // Signal failure so Claude can retry or ask for clarification.
          toolResults.push({
            type: "tool_result",
            tool_use_id: block.id,
            content: String(err),
            is_error: true,
          });
        }
      }
    }

    messages.push({ role: "assistant", content: response.content });
    messages.push({ role: "user", content: toolResults });

    response = await client.messages.create({
      model: "claude-opus-5",
      max_tokens: 1024,
      tools,
      messages,
    });
  }

  for (const block of response.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

csharp C#
  // Ring 4: Error handling.

  using System;
  using System.Collections.Generic;
  using System.Linq;
  using System.Text.Json;
  using System.Threading.Tasks;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  List<ToolUnion> tools =
  [
      new ToolUnion(new Tool()
      {
          Name = "create_calendar_event",
          Description = "Create a calendar event with attendees and optional recurrence.",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["title"] = JsonSerializer.SerializeToElement(new { type = "string" }),
                  ["start"] = JsonSerializer.SerializeToElement(new { type = "string", format = "date-time" }),
                  ["end"] = JsonSerializer.SerializeToElement(new { type = "string", format = "date-time" }),
                  ["attendees"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "array",
                      items = new { type = "string", format = "email" },
                  }),
                  ["recurrence"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "object",
                      properties = new
                      {
                          frequency = new { @enum = new[] { "daily", "weekly", "monthly" } },
                          count = new { type = "integer", minimum = 1 },
                      },
                  }),
              },
              Required = ["title", "start", "end"],
          },
      }),
      new ToolUnion(new Tool()
      {
          Name = "list_calendar_events",
          Description = "List all calendar events on a given date.",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["date"] = JsonSerializer.SerializeToElement(new { type = "string", format = "date" }),
              },
              Required = ["date"],
          },
      }),
  ];

  string RunTool(ToolUseBlock toolUse)
  {
      if (toolUse.Name == "create_calendar_event")
      {
          if (toolUse.Input.TryGetValue("attendees", out var attendees) && attendees.GetArrayLength() > 10)
          {
              throw new InvalidOperationException("Too many attendees (max 10)");
          }
          var title = toolUse.Input.TryGetValue("title", out var t) ? t.GetString() : "";
          return JsonSerializer.Serialize(new { event_id = "evt_123", status = "created", title });
      }
      if (toolUse.Name == "list_calendar_events")
      {
          return """{"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}""";
      }
      throw new InvalidOperationException($"Unknown tool: {toolUse.Name}");
  }

  // Build a request that exceeds the tool's attendee limit so the error path runs.
  var emails = string.Join(", ", Enumerable.Range(0, 15).Select(i => $"user{i}@example.com"));

  List<MessageParam> messages =
  [
      new() { Role = Role.User, Content = $"Schedule an all-hands with everyone: {emails}" },
  ];

  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = tools,
      Messages = messages,
  });

  while (response.StopReason == StopReason.ToolUse)
  {
      List<ContentBlockParam> toolResults = [];
      foreach (var block in response.Content)
      {
          if (block.TryPickToolUse(out var toolUse))
          {
              ToolResultBlockParam toolResult;
              try
              {
                  toolResult = new ToolResultBlockParam() { ToolUseID = toolUse.ID, Content = RunTool(toolUse) };
              }
              catch (Exception e)
              {
                  // Signal failure so Claude can retry or ask for clarification.
                  toolResult = new ToolResultBlockParam()
                  {
                      ToolUseID = toolUse.ID,
                      Content = e.Message,
                      IsError = true,
                  };
              }
              toolResults.Add(new ContentBlockParam(toolResult));
          }
      }

      messages.Add(new()
      {
          Role = Role.Assistant,
          Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList(),
      });
      messages.Add(new() { Role = Role.User, Content = new MessageParamContent(toolResults) });

      response = await client.Messages.Create(new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Tools = tools,
          Messages = messages,
      });
  }

  foreach (var block in response.Content)
  {
      if (block.TryPickText(out var text))
      {
          Console.WriteLine(text.Text);
      }
  }

go Go
  // Ring 4: Error handling.

  package main

  import (
  	"context"
  	"encoding/json"
  	"fmt"
  	"log"
  	"strings"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  func runTool(name string, input map[string]any) (string, error) {
  	if name == "create_calendar_event" {
  		if attendees, ok := input["attendees"].([]any); ok && len(attendees) > 10 {
  			return "", fmt.Errorf("too many attendees (max 10)")
  		}
  		title, _ := input["title"].(string)
  		return fmt.Sprintf(`{"event_id": "evt_123", "status": "created", "title": %q}`, title), nil
  	}
  	if name == "list_calendar_events" {
  		return `{"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}`, nil
  	}
  	return "", fmt.Errorf("unknown tool: %s", name)
  }

  func main() {
  	client := anthropic.NewClient()
  	ctx := context.Background()

  	tools := []anthropic.ToolUnionParam{
  		{OfTool: &anthropic.ToolParam{
  			Name:        "create_calendar_event",
  			Description: anthropic.String("Create a calendar event with attendees and optional recurrence."),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"title": map[string]any{"type": "string"},
  					"start": map[string]any{"type": "string", "format": "date-time"},
  					"end":   map[string]any{"type": "string", "format": "date-time"},
  					"attendees": map[string]any{
  						"type":  "array",
  						"items": map[string]any{"type": "string", "format": "email"},
  					},
  					"recurrence": map[string]any{
  						"type": "object",
  						"properties": map[string]any{
  							"frequency": map[string]any{"enum": []string{"daily", "weekly", "monthly"}},
  							"count":     map[string]any{"type": "integer", "minimum": 1},
  						},
  					},
  				},
  				Required: []string{"title", "start", "end"},
  			},
  		}},
  		{OfTool: &anthropic.ToolParam{
  			Name:        "list_calendar_events",
  			Description: anthropic.String("List all calendar events on a given date."),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"date": map[string]any{"type": "string", "format": "date"},
  				},
  				Required: []string{"date"},
  			},
  		}},
  	}

  	// Build a request that exceeds the tool's attendee limit so the error path runs.
  	emails := make([]string, 15)
  	for i := range emails {
  		emails[i] = fmt.Sprintf("user%d@example.com", i)
  	}
  	messages := []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock(
  			"Schedule an all-hands with everyone: " + strings.Join(emails, ", "),
  		)),
  	}

  	response, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 1024,
  		Tools:     tools,
  		Messages:  messages,
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	for response.StopReason == "tool_use" {
  		var toolResults []anthropic.ContentBlockParamUnion
  		for _, block := range response.Content {
  			if block.Type == "tool_use" {
  				var input map[string]any
  				if err := json.Unmarshal(block.Input, &input); err != nil {
  					log.Fatal(err)
  				}
  				result, toolErr := runTool(block.Name, input)
  				if toolErr != nil {
  					// Signal failure so Claude can retry or ask for clarification.
  					toolResults = append(toolResults, anthropic.NewToolResultBlock(block.ID, toolErr.Error(), true))
  				} else {
  					toolResults = append(toolResults, anthropic.NewToolResultBlock(block.ID, result, false))
  				}
  			}
  		}

  		var assistantContent []anthropic.ContentBlockParamUnion
  		for _, block := range response.Content {
  			assistantContent = append(assistantContent, block.ToParam())
  		}
  		messages = append(messages, anthropic.NewAssistantMessage(assistantContent...))
  		messages = append(messages, anthropic.NewUserMessage(toolResults...))

  		response, err = client.Messages.New(ctx, anthropic.MessageNewParams{
  			Model:     anthropic.ModelClaudeOpus5,
  			MaxTokens: 1024,
  			Tools:     tools,
  			Messages:  messages,
  		})
  		if err != nil {
  			log.Fatal(err)
  		}
  	}

  	for _, block := range response.Content {
  		if block.Type == "text" {
  			fmt.Println(block.Text)
  		}
  	}
  }

java Java
  // Ring 4: Error handling.

  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.JsonValue;
  import com.anthropic.models.messages.ContentBlock;
  import com.anthropic.models.messages.ContentBlockParam;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.MessageParam;
  import com.anthropic.models.messages.Model;
  import com.anthropic.models.messages.StopReason;
  import com.anthropic.models.messages.Tool;
  import com.anthropic.models.messages.Tool.InputSchema;
  import com.anthropic.models.messages.ToolResultBlockParam;
  import com.anthropic.models.messages.ToolUseBlock;
  import java.util.ArrayList;
  import java.util.List;
  import java.util.Map;
  import java.util.stream.Collectors;
  import java.util.stream.IntStream;

  String runTool(ToolUseBlock toolUse) {
      // The raw tool input is a JSON object; read fields out of it as a map.
      Map<String, JsonValue> input = (Map<String, JsonValue>) toolUse._input().asObject().get();
      if (toolUse.name().equals("create_calendar_event")) {
          int attendeeCount = input.containsKey("attendees")
              ? ((List<?>) input.get("attendees").asArray().get()).size()
              : 0;
          if (attendeeCount > 10) {
              throw new IllegalArgumentException("Too many attendees (max 10)");
          }
          String title = input.containsKey("title") ? input.get("title").asStringOrThrow() : "";
          return "{\"event_id\": \"evt_123\", \"status\": \"created\", \"title\": \"" + title + "\"}";
      }
      if (toolUse.name().equals("list_calendar_events")) {
          return "{\"events\": [{\"title\": \"Existing meeting\", \"start\": \"14:00\", \"end\": \"15:00\"}]}";
      }
      throw new IllegalArgumentException("Unknown tool: " + toolUse.name());
  }

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      Tool calendarTool = Tool.builder()
          .name("create_calendar_event")
          .description("Create a calendar event with attendees and optional recurrence.")
          .inputSchema(InputSchema.builder()
              .properties(JsonValue.from(Map.of(
                  "title", Map.of("type", "string"),
                  "start", Map.of("type", "string", "format", "date-time"),
                  "end", Map.of("type", "string", "format", "date-time"),
                  "attendees", Map.of(
                      "type", "array",
                      "items", Map.of("type", "string", "format", "email")
                  ),
                  "recurrence", Map.of(
                      "type", "object",
                      "properties", Map.of(
                          "frequency", Map.of("enum", List.of("daily", "weekly", "monthly")),
                          "count", Map.of("type", "integer", "minimum", 1)
                      )
                  )
              )))
              .required(List.of("title", "start", "end"))
              .build())
          .build();

      Tool listTool = Tool.builder()
          .name("list_calendar_events")
          .description("List all calendar events on a given date.")
          .inputSchema(InputSchema.builder()
              .properties(JsonValue.from(Map.of(
                  "date", Map.of("type", "string", "format", "date")
              )))
              .required(List.of("date"))
              .build())
          .build();

      // Build a request that exceeds the tool's attendee limit so the error path runs.
      String emails = IntStream.range(0, 15)
          .mapToObj(i -> "user" + i + "@example.com")
          .collect(Collectors.joining(", "));

      List<MessageParam> messages = new ArrayList<>();
      messages.add(MessageParam.builder()
          .role(MessageParam.Role.USER)
          .content("Schedule an all-hands with everyone: " + emails)
          .build());

      Message response = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addTool(calendarTool)
          .addTool(listTool)
          .messages(messages)
          .build());

      while (response.stopReason().isPresent()
              && response.stopReason().get().equals(StopReason.TOOL_USE)) {
          List<ContentBlockParam> toolResults = new ArrayList<>();
          for (ContentBlock block : response.content()) {
              if (block.toolUse().isPresent()) {
                  ToolUseBlock toolUse = block.toolUse().get();
                  ToolResultBlockParam.Builder resultBuilder = ToolResultBlockParam.builder()
                      .toolUseId(toolUse.id());
                  try {
                      resultBuilder.content(runTool(toolUse));
                  } catch (Exception e) {
                      // Signal failure so Claude can retry or ask for clarification.
                      resultBuilder.content(e.getMessage()).isError(true);
                  }
                  toolResults.add(ContentBlockParam.ofToolResult(resultBuilder.build()));
              }
          }

          messages.add(response.toParam());
          messages.add(MessageParam.builder()
              .role(MessageParam.Role.USER)
              .contentOfBlockParams(toolResults)
              .build());

          response = client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024L)
              .addTool(calendarTool)
              .addTool(listTool)
              .messages(messages)
              .build());
      }

      response.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  <?php

  // Ring 4: Error handling.

  use Anthropic\Client;

  $client = new Client();

  $tools = [
      [
          'name' => 'create_calendar_event',
          'description' => 'Create a calendar event with attendees and optional recurrence.',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'title' => ['type' => 'string'],
                  'start' => ['type' => 'string', 'format' => 'date-time'],
                  'end' => ['type' => 'string', 'format' => 'date-time'],
                  'attendees' => [
                      'type' => 'array',
                      'items' => ['type' => 'string', 'format' => 'email'],
                  ],
                  'recurrence' => [
                      'type' => 'object',
                      'properties' => [
                          'frequency' => ['enum' => ['daily', 'weekly', 'monthly']],
                          'count' => ['type' => 'integer', 'minimum' => 1],
                      ],
                  ],
              ],
              'required' => ['title', 'start', 'end'],
          ],
      ],
      [
          'name' => 'list_calendar_events',
          'description' => 'List all calendar events on a given date.',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'date' => ['type' => 'string', 'format' => 'date'],
              ],
              'required' => ['date'],
          ],
      ],
  ];

  function runTool(string $name, array $input): string
  {
      if ($name === 'create_calendar_event') {
          if (count($input['attendees'] ?? []) > 10) {
              throw new InvalidArgumentException('Too many attendees (max 10)');
          }

          return json_encode([
              'event_id' => 'evt_123',
              'status' => 'created',
              'title' => $input['title'],
          ]);
      }
      if ($name === 'list_calendar_events') {
          return json_encode([
              'events' => [['title' => 'Existing meeting', 'start' => '14:00', 'end' => '15:00']],
          ]);
      }

      throw new InvalidArgumentException("Unknown tool: {$name}");
  }

  // Build a request that exceeds the tool's attendee limit so the error path runs.
  $emails = array_map(fn (int $i): string => "user{$i}@example.com", range(0, 14));
  $messages = [
      [
          'role' => 'user',
          'content' => 'Schedule an all-hands with everyone: ' . implode(', ', $emails),
      ],
  ];

  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: $tools,
      messages: $messages,
  );

  while ($response->stopReason === 'tool_use') {
      $toolResults = [];
      foreach ($response->content as $block) {
          if ($block->type === 'tool_use') {
              try {
                  $toolResults[] = [
                      'type' => 'tool_result',
                      'tool_use_id' => $block->id,
                      'content' => runTool($block->name, $block->input),
                  ];
              } catch (Exception $e) {
                  // Signal failure so Claude can retry or ask for clarification.
                  $toolResults[] = [
                      'type' => 'tool_result',
                      'tool_use_id' => $block->id,
                      'content' => $e->getMessage(),
                      'is_error' => true,
                  ];
              }
          }
      }

      $messages[] = ['role' => 'assistant', 'content' => $response->content];
      $messages[] = ['role' => 'user', 'content' => $toolResults];

      $response = $client->messages->create(
          model: 'claude-opus-5',
          maxTokens: 1024,
          tools: $tools,
          messages: $messages,
      );
  }

  foreach ($response->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, "\n";
      }
  }

ruby Ruby
  # Ring 4: Error handling.

  require "anthropic"

  client = Anthropic::Client.new

  tools = [
    {
      name: "create_calendar_event",
      description: "Create a calendar event with attendees and optional recurrence.",
      input_schema: {
        type: "object",
        properties: {
          title: {type: "string"},
          start: {type: "string", format: "date-time"},
          end: {type: "string", format: "date-time"},
          attendees: {
            type: "array",
            items: {type: "string", format: "email"}
          },
          recurrence: {
            type: "object",
            properties: {
              frequency: {enum: ["daily", "weekly", "monthly"]},
              count: {type: "integer", minimum: 1}
            }
          }
        },
        required: ["title", "start", "end"]
      }
    },
    {
      name: "list_calendar_events",
      description: "List all calendar events on a given date.",
      input_schema: {
        type: "object",
        properties: {
          date: {type: "string", format: "date"}
        },
        required: ["date"]
      }
    }
  ]

  def run_tool(name, input)
    case name
    when "create_calendar_event"
      attendees = input[:attendees]
      raise ArgumentError, "Too many attendees (max 10)" if attendees && attendees.length > 10
      JSON.generate({event_id: "evt_123", status: "created", title: input[:title]})
    when "list_calendar_events"
      JSON.generate({events: [{title: "Existing meeting", start: "14:00", end: "15:00"}]})
    else
      raise ArgumentError, "Unknown tool: #{name}"
    end
  end

  # Build a request that exceeds the tool's attendee limit so the error path runs.
  emails = (0...15).map { |i| "user#{i}@example.com" }
  messages = [
    {
      role: "user",
      content: "Schedule an all-hands with everyone: #{emails.join(", ")}"
    }
  ]

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: tools,
    messages: messages
  )

  while response.stop_reason == :tool_use
    tool_results = response.content.select { |block| block.type == :tool_use }.map do |tool_use|
      begin
        {
          type: "tool_result",
          tool_use_id: tool_use.id,
          content: run_tool(tool_use.name, tool_use.input)
        }
      rescue => e
        # Signal failure so Claude can retry or ask for clarification.
        {
          type: "tool_result",
          tool_use_id: tool_use.id,
          content: e.message,
          is_error: true
        }
      end
    end

    messages << {role: "assistant", content: response.content}
    messages << {role: "user", content: tool_results}

    response = client.messages.create(
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: tools,
      messages: messages
    )
  end

  response.content.each do |block|
    puts block.text if block.type == :text
  end

text Output wrap
I tried to schedule the all-hands but the calendar only allows 10 attendees per event. I can split this into two sessions, or you can let me know which 10 people to prioritize.
```

The `is_error` flag is the only difference from a successful result. Claude sees the flag and the error text, and responds accordingly. See [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) for the full error-handling reference.


## Ring 5: The Tool Runner SDK abstraction

Source: https://platform.claude.com/llms-full.txt#ring-5-the-tool-runner-sdk-abstraction

Rings 2 through 4 wrote the same loop by hand: call the API, check `stop_reason`, run tools, append results, repeat. The Tool Runner does this for you. Define each tool as a function, pass the list to `tool_runner`, and retrieve the final message once the loop completes. Error wrapping, result formatting, and conversation management are handled internally.

Each SDK provides a helper that turns an ordinary function into a runnable tool and derives the input schema from its signature; the tabs below show the idiomatic form for each language.

<Note>
  Tool Runner is available in all seven SDKs: Python, TypeScript, C#, Go, Java, PHP, and Ruby. See [Tool Runner](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner) for the full reference. The cURL and CLI tabs show a note instead of code; keep the Ring 4 loop for curl- or CLI-based scripts.
</Note>

<CodeGroup>
  ```bash cURL
  #!/bin/bash
  # Ring 5: The Tool Runner SDK abstraction.

  # The Tool Runner SDK abstraction is available in all seven SDKs: Python,
  # TypeScript, C#, Go, Java, PHP, and Ruby. There is no equivalent for raw
  # curl requests. Switch to any SDK tab to see Ring 5, or keep the Ring 4
  # loop as your shell implementation.

bash CLI
  #!/usr/bin/env bash
  # Ring 5: The Tool Runner SDK abstraction.
  set -euo pipefail

  # The Tool Runner SDK abstraction is available in all seven SDKs: Python,
  # TypeScript, C#, Go, Java, PHP, and Ruby. The ant CLI exposes the Messages
  # API directly and has no equivalent helper. Switch to any SDK tab to see
  # Ring 5, or keep the Ring 4 loop as your CLI implementation.

python Python
  # Ring 5: The Tool Runner SDK abstraction.

  import json

  import anthropic
  from anthropic import beta_tool

  client = anthropic.Anthropic()


  @beta_tool
  def create_calendar_event(
      title: str,
      start: str,
      end: str,
      attendees: list[str] | None = None,
      recurrence: dict | None = None,
  ) -> str:
      """Create a calendar event with attendees and optional recurrence.

      Args:
          title: Event title.
          start: Start time in ISO 8601 format.
          end: End time in ISO 8601 format.
          attendees: Email addresses to invite.
          recurrence: Dict with 'frequency' (daily, weekly, monthly) and 'count'.
      """
      if attendees and len(attendees) > 10:
          raise ValueError("Too many attendees (max 10)")
      return json.dumps({"event_id": "evt_123", "status": "created", "title": title})


  @beta_tool
  def list_calendar_events(date: str) -> str:
      """List all calendar events on a given date.

      Args:
          date: Date in YYYY-MM-DD format.
      """
      return json.dumps({"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]})


  final_message = client.beta.messages.tool_runner(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[create_calendar_event, list_calendar_events],
      messages=[
          {
              "role": "user",
              "content": "Check what I have next Monday, then schedule a planning session that avoids any conflicts.",
          }
      ],
  ).until_done()

  for block in final_message.content:
      if block.type == "text":
          print(block.text)

typescript TypeScript
  // Ring 5: The Tool Runner SDK abstraction.

  import Anthropic from "@anthropic-ai/sdk";
  import { betaZodTool } from "@anthropic-ai/sdk/helpers/beta/zod";
  import { z } from "zod";

  const client = new Anthropic();

  const createCalendarEvent = betaZodTool({
    name: "create_calendar_event",
    description:
      "Create a calendar event with attendees and optional recurrence.",
    inputSchema: z.object({
      title: z.string(),
      start: z.string().datetime(),
      end: z.string().datetime(),
      attendees: z.array(z.string().email()).optional(),
      recurrence: z
        .object({
          frequency: z.enum(["daily", "weekly", "monthly"]),
          count: z.number().int().min(1),
        })
        .optional(),
    }),
    run: async (input) => {
      if (input.attendees && input.attendees.length > 10) {
        throw new Error("Too many attendees (max 10)");
      }
      return JSON.stringify({
        event_id: "evt_123",
        status: "created",
        title: input.title,
      });
    },
  });

  const listCalendarEvents = betaZodTool({
    name: "list_calendar_events",
    description: "List all calendar events on a given date.",
    inputSchema: z.object({
      date: z.string().date(),
    }),
    run: async () => {
      return JSON.stringify({
        events: [{ title: "Existing meeting", start: "14:00", end: "15:00" }],
      });
    },
  });

  const finalMessage = await client.beta.messages.toolRunner({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [createCalendarEvent, listCalendarEvents],
    messages: [
      {
        role: "user",
        content:
          "Check what I have next Monday, then schedule a planning session that avoids any conflicts.",
      },
    ],
  });

  for (const block of finalMessage.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

csharp C#
  // Ring 5: The Tool Runner SDK abstraction.

  using System;
  using System.Collections.Generic;
  using System.Text.Json;
  using System.Threading.Tasks;
  using Anthropic;
  using Anthropic.Helpers.Beta;
  using Anthropic.Models.Beta.Messages;
  using MessageCreateParams = Anthropic.Models.Beta.Messages.MessageCreateParams;
  using InputSchema = Anthropic.Models.Beta.Messages.InputSchema;
  using Role = Anthropic.Models.Beta.Messages.Role;
  using Model = Anthropic.Models.Messages.Model;

  AnthropicClient client = new();

  // Define each tool as a runnable tool: the definition carries the JSON Schema
  // and the Run callback holds the implementation. Throwing an exception sends
  // the message back to Claude as a tool result with is_error set.
  var createCalendarEvent = new BetaRunnableTool
  {
      Name = "create_calendar_event",
      Definition = new BetaTool
      {
          Name = "create_calendar_event",
          Description = "Create a calendar event with attendees and optional recurrence.",
          InputSchema = new InputSchema
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["title"] = JsonSerializer.SerializeToElement(new { type = "string", description = "Event title" }),
                  ["start"] = JsonSerializer.SerializeToElement(new { type = "string", description = "Start time in ISO 8601 format" }),
                  ["end"] = JsonSerializer.SerializeToElement(new { type = "string", description = "End time in ISO 8601 format" }),
                  ["attendees"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "array",
                      items = new { type = "string" },
                      description = "Email addresses to invite",
                  }),
                  ["recurrence"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "object",
                      properties = new
                      {
                          frequency = new { @enum = new[] { "daily", "weekly", "monthly" } },
                          count = new { type = "integer", minimum = 1 },
                      },
                  }),
              },
              Required = ["title", "start", "end"],
          },
      },
      Run = (toolUse, _) =>
      {
          if (toolUse.Input.TryGetValue("attendees", out var attendees) && attendees.GetArrayLength() > 10)
          {
              throw new InvalidOperationException("Too many attendees (max 10)");
          }
          var title = toolUse.Input.TryGetValue("title", out var t) ? t.GetString() : "";
          return Task.FromResult<BetaToolResultBlockParamContent>(
              JsonSerializer.Serialize(new { event_id = "evt_123", status = "created", title })
          );
      },
  };

  var listCalendarEvents = new BetaRunnableTool
  {
      Name = "list_calendar_events",
      Definition = new BetaTool
      {
          Name = "list_calendar_events",
          Description = "List all calendar events on a given date.",
          InputSchema = new InputSchema
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["date"] = JsonSerializer.SerializeToElement(new { type = "string", description = "Date in YYYY-MM-DD format" }),
              },
              Required = ["date"],
          },
      },
      Run = (toolUse, _) => Task.FromResult<BetaToolResultBlockParamContent>(
          """{"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}"""
      ),
  };

  // The runner calls the API, runs requested tools, and feeds results back
  // until Claude produces a final answer.
  var runner = client.Beta.Messages.ToolRunner(
      new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages =
          [
              new()
              {
                  Role = Role.User,
                  Content = "Check what I have next Monday, then schedule a planning session that avoids any conflicts.",
              },
          ],
      },
      [createCalendarEvent, listCalendarEvents]
  );

  BetaMessage? finalMessage = null;
  await foreach (var message in runner)
  {
      finalMessage = message;
  }

  foreach (var block in finalMessage!.Content)
  {
      if (block.TryPickText(out var text))
      {
          Console.WriteLine(text.Text);
      }
  }

go Go
  // Ring 5: The Tool Runner SDK abstraction.

  package main

  import (
  	"context"
  	"fmt"
  	"log"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/toolrunner"
  )

  // The input structs define each tool's schema. The tool runner generates the
  // JSON Schema from the struct fields and their jsonschema tags.
  type RecurrenceInput struct {
  	Frequency string `json:"frequency,omitempty" jsonschema:"enum=daily,enum=weekly,enum=monthly,description=How often the event repeats"`
  	Count     int    `json:"count,omitempty" jsonschema:"description=Number of occurrences"`
  }

  type CreateCalendarEventInput struct {
  	Title      string           `json:"title" jsonschema:"required,description=Event title"`
  	Start      string           `json:"start" jsonschema:"required,description=Start time in ISO 8601 format"`
  	End        string           `json:"end" jsonschema:"required,description=End time in ISO 8601 format"`
  	Attendees  []string         `json:"attendees,omitempty" jsonschema:"description=Email addresses to invite"`
  	Recurrence *RecurrenceInput `json:"recurrence,omitempty"`
  }

  type ListCalendarEventsInput struct {
  	Date string `json:"date" jsonschema:"required,description=Date in YYYY-MM-DD format"`
  }

  func main() {
  	client := anthropic.NewClient()
  	ctx := context.Background()

  	// Define each tool as a handler function. Returning an error sends the
  	// message back to Claude as a tool result with is_error set.
  	createCalendarEvent, err := toolrunner.NewBetaToolFromJSONSchema(
  		"create_calendar_event",
  		"Create a calendar event with attendees and optional recurrence.",
  		func(ctx context.Context, input CreateCalendarEventInput) (anthropic.BetaToolResultBlockParamContentUnion, error) {
  			if len(input.Attendees) > 10 {
  				return anthropic.BetaToolResultBlockParamContentUnion{}, fmt.Errorf("too many attendees (max 10)")
  			}
  			return anthropic.BetaToolResultBlockParamContentUnion{
  				OfText: &anthropic.BetaTextBlockParam{
  					Text: fmt.Sprintf(`{"event_id": "evt_123", "status": "created", "title": %q}`, input.Title),
  				},
  			}, nil
  		},
  	)
  	if err != nil {
  		log.Fatal(err)
  	}

  	listCalendarEvents, err := toolrunner.NewBetaToolFromJSONSchema(
  		"list_calendar_events",
  		"List all calendar events on a given date.",
  		func(ctx context.Context, input ListCalendarEventsInput) (anthropic.BetaToolResultBlockParamContentUnion, error) {
  			return anthropic.BetaToolResultBlockParamContentUnion{
  				OfText: &anthropic.BetaTextBlockParam{
  					Text: `{"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}`,
  				},
  			}, nil
  		},
  	)
  	if err != nil {
  		log.Fatal(err)
  	}

  	// The runner calls the API, runs requested tools, and feeds results back
  	// until Claude produces a final answer.
  	runner := client.Beta.Messages.NewToolRunner(
  		[]anthropic.BetaTool{createCalendarEvent, listCalendarEvents},
  		anthropic.BetaToolRunnerParams{
  			BetaMessageNewParams: anthropic.BetaMessageNewParams{
  				Model:     anthropic.ModelClaudeOpus5,
  				MaxTokens: 1024,
  				Messages: []anthropic.BetaMessageParam{
  					anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock(
  						"Check what I have next Monday, then schedule a planning session that avoids any conflicts.",
  					)),
  				},
  			},
  		},
  	)

  	var finalMessage *anthropic.BetaMessage
  	for message, err := range runner.All(ctx) {
  		if err != nil {
  			log.Fatal(err)
  		}
  		finalMessage = message
  	}

  	for _, block := range finalMessage.Content {
  		if block.Type == "text" {
  			fmt.Println(block.Text)
  		}
  	}
  }

java Java
  // Ring 5: The Tool Runner SDK abstraction.

  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.helpers.BetaToolRunner;
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;
  import com.fasterxml.jackson.annotation.JsonClassDescription;
  import com.fasterxml.jackson.annotation.JsonPropertyDescription;
  import java.util.List;
  import java.util.function.Supplier;

  // Define each tool as a class: the fields describe the input schema, and the
  // get() method holds the implementation. Throwing an exception sends the
  // message back to Claude as a tool result with is_error set.
  @JsonClassDescription("Create a calendar event with attendees.")
  static class CreateCalendarEvent implements Supplier<String> {
      @JsonPropertyDescription("Event title")
      public String title;

      @JsonPropertyDescription("Start time in ISO 8601 format")
      public String start;

      @JsonPropertyDescription("End time in ISO 8601 format")
      public String end;

      @JsonPropertyDescription("Email addresses to invite")
      public List<String> attendees;

      @Override
      public String get() {
          if (attendees != null && attendees.size() > 10) {
              throw new IllegalArgumentException("Too many attendees (max 10)");
          }
          return "{\"event_id\": \"evt_123\", \"status\": \"created\", \"title\": \"" + title + "\"}";
      }
  }

  @JsonClassDescription("List all calendar events on a given date.")
  static class ListCalendarEvents implements Supplier<String> {
      @JsonPropertyDescription("Date in YYYY-MM-DD format")
      public String date;

      @Override
      public String get() {
          return "{\"events\": [{\"title\": \"Existing meeting\", \"start\": \"14:00\", \"end\": \"15:00\"}]}";
      }
  }

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      // The runner calls the API, runs requested tools, and feeds results back
      // until Claude produces a final answer.
      BetaToolRunner runner = client.beta()
              .messages()
              .toolRunner(MessageCreateParams.builder()
                      .model(Model.CLAUDE_OPUS_5)
                      .maxTokens(1024)
                      .addBeta("structured-outputs-2025-11-13")
                      .addUserMessage("Check what I have next Monday, then schedule a planning session that avoids any conflicts.")
                      .addTool(CreateCalendarEvent.class)
                      .addTool(ListCalendarEvents.class)
                      .build());

      BetaMessage finalMessage = null;
      for (BetaMessage message : runner) {
          finalMessage = message;
      }

      finalMessage.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  <?php

  // Ring 5: The Tool Runner SDK abstraction.

  use Anthropic\Client;
  use Anthropic\Lib\Tools\BetaRunnableTool;
  use Anthropic\Messages\Model;

  $client = new Client();

  // Define each tool as a runnable tool: the definition carries the JSON Schema
  // and the run closure holds the implementation. Throwing an exception sends the
  // message back to Claude as a tool result with is_error set.
  $createCalendarEvent = new BetaRunnableTool(
      definition: [
          'name' => 'create_calendar_event',
          'description' => 'Create a calendar event with attendees and optional recurrence.',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'title' => ['type' => 'string', 'description' => 'Event title'],
                  'start' => ['type' => 'string', 'description' => 'Start time in ISO 8601 format'],
                  'end' => ['type' => 'string', 'description' => 'End time in ISO 8601 format'],
                  'attendees' => [
                      'type' => 'array',
                      'items' => ['type' => 'string'],
                      'description' => 'Email addresses to invite',
                  ],
                  'recurrence' => [
                      'type' => 'object',
                      'properties' => [
                          'frequency' => ['enum' => ['daily', 'weekly', 'monthly']],
                          'count' => ['type' => 'integer', 'minimum' => 1],
                      ],
                  ],
              ],
              'required' => ['title', 'start', 'end'],
          ],
      ],
      run: function (array $input): string {
          if (count($input['attendees'] ?? []) > 10) {
              throw new InvalidArgumentException('Too many attendees (max 10)');
          }

          return json_encode([
              'event_id' => 'evt_123',
              'status' => 'created',
              'title' => $input['title'],
          ]);
      },
  );

  $listCalendarEvents = new BetaRunnableTool(
      definition: [
          'name' => 'list_calendar_events',
          'description' => 'List all calendar events on a given date.',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'date' => ['type' => 'string', 'description' => 'Date in YYYY-MM-DD format'],
              ],
              'required' => ['date'],
          ],
      ],
      run: fn (array $input): string => json_encode([
          'events' => [['title' => 'Existing meeting', 'start' => '14:00', 'end' => '15:00']],
      ]),
  );

  // The runner calls the API, runs requested tools, and feeds results back
  // until Claude produces a final answer.
  $runner = $client->beta->messages->toolRunner(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => 'Check what I have next Monday, then schedule a planning session that avoids any conflicts.',
          ],
      ],
      model: Model::CLAUDE_OPUS_5,
      tools: [$createCalendarEvent, $listCalendarEvents],
  );

  $finalMessage = null;
  foreach ($runner as $message) {
      $finalMessage = $message;
  }

  foreach ($finalMessage->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, "\n";
      }
  }

ruby Ruby
  # Ring 5: The Tool Runner SDK abstraction.

  require "anthropic"

  client = Anthropic::Client.new

  # Define each tool as a class: a typed input model describes the schema, and
  # the call method holds the implementation. Raising an error sends the message
  # back to Claude as a tool result with is_error set.
  class RecurrenceInput < Anthropic::BaseModel
    optional :frequency, Anthropic::InputSchema::EnumOf["daily", "weekly", "monthly"],
             doc: "How often the event repeats"
    optional :count, Integer, doc: "Number of occurrences"
  end

  class CreateCalendarEventInput < Anthropic::BaseModel
    required :title, String, doc: "Event title"
    required :start, String, doc: "Start time in ISO 8601 format"
    required :end, String, doc: "End time in ISO 8601 format"
    optional :attendees, Anthropic::InputSchema::ArrayOf[String], doc: "Email addresses to invite"
    optional :recurrence, RecurrenceInput, doc: "Optional recurrence rule"
  end

  class CreateCalendarEvent < Anthropic::BaseTool
    doc "Create a calendar event with attendees and optional recurrence."
    input_schema CreateCalendarEventInput

    def call(input)
      raise ArgumentError, "Too many attendees (max 10)" if input.attendees && input.attendees.length > 10
      JSON.generate({event_id: "evt_123", status: "created", title: input.title})
    end
  end

  class ListCalendarEventsInput < Anthropic::BaseModel
    required :date, String, doc: "Date in YYYY-MM-DD format"
  end

  class ListCalendarEvents < Anthropic::BaseTool
    doc "List all calendar events on a given date."
    input_schema ListCalendarEventsInput

    def call(input)
      JSON.generate({events: [{title: "Existing meeting", start: "14:00", end: "15:00"}]})
    end
  end

  # The runner calls the API, runs requested tools, and feeds results back
  # until Claude produces a final answer.
  runner = client.beta.messages.tool_runner(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [CreateCalendarEvent.new, ListCalendarEvents.new],
    messages: [
      {
        role: "user",
        content: "Check what I have next Monday, then schedule a planning session that avoids any conflicts."
      }
    ]
  )

  final_message = nil
  runner.each_message { |message| final_message = message }

  final_message.content.each do |block|
    puts block.text if block.type == :text
  end

text Output wrap
I checked your calendar for next Monday and found an existing meeting from 2pm to 3pm. I've scheduled the planning session for 10am to 11am to avoid the conflict.
```

The output is identical to Ring 3. The difference is in the code: roughly half the lines, no manual loop, and the schema lives next to the implementation.


## What you built

Source: https://platform.claude.com/llms-full.txt#what-you-built

You started with a single hardcoded tool call and ended with a production-shaped agent that handles multiple tools, parallel calls, and errors, then collapsed all of that into the Tool Runner. Along the way you saw every piece of the tool-use protocol: `tool_use` blocks, `tool_result` blocks, `tool_use_id` matching, `stop_reason` checking, and `is_error` signaling.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-40

<CardGroup>
  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools" title="Define tools">
    Schema specification and best practices.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner" title="Tool Runner">
    The full SDK abstraction reference.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/troubleshooting-tool-use" title="Troubleshooting">
    Fix common tool-use errors.
  </Card>
</CardGroup>


---
title: Web fetch tool
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool
description: Fetch and read content from specific URLs to augment Claude's context with live web content.
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

The web fetch tool allows Claude to retrieve full content from specified web pages and PDF documents.

The latest web fetch tool version (`web_fetch_20260318`) supports **dynamic filtering**: Claude can write and execute code to filter fetched content before it reaches the context window, keeping only relevant information and discarding the rest. This reduces token consumption while maintaining response quality. Dynamic filtering is available with Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, [Claude Mythos Preview](https://anthropic.com/glasswing), Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, and Claude Sonnet 4.6. `web_fetch_20260318` also adds [response inclusion](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool#response-inclusion) control for agentic workflows. The previous versions (`web_fetch_20260309` for dynamic filtering and [cache bypass](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool#cache-bypass), `web_fetch_20260209` for dynamic filtering only, `web_fetch_20250910` for basic fetch) remain available.

Web fetch (with and without dynamic filtering) is available on the Claude API, [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), and [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry). On Microsoft Foundry, deployments [hosted on Azure](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#additional-features-not-supported-when-hosted-on-azure) support only the basic web fetch tool (`web_fetch_20250910`, without dynamic filtering). Deployments hosted on Anthropic support all versions. Web fetch is not currently available on Amazon Bedrock or Google Cloud.

<Note>
  For [Claude Mythos Preview](https://anthropic.com/glasswing), web fetch is available on the Claude API and Microsoft Foundry. It is not currently available for Mythos Preview on Amazon Bedrock or Google Cloud.
</Note>

<Note>
  Use the [feedback form](https://forms.gle/NhWcgmkcvPCMmPE86) to provide feedback on the quality of the model responses, the API itself, or the quality of the documentation.
</Note>

For Zero Data Retention eligibility and the `allowed_callers` workaround, see [Server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#zdr-and-allowed-callers).

<Warning>
  Enabling the web fetch tool in environments where Claude processes untrusted input alongside sensitive data poses data exfiltration risks. Only use this tool in trusted environments or when handling non-sensitive data.

  To minimize exfiltration risks, Claude cannot fetch URLs that appear only in its own output. Claude can only fetch URLs that have previously appeared in the conversation: URLs in user messages, URLs in client-side tool results (even when a result echoes text that Claude generated), and URLs from previous web search or web fetch results (see [URL validation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool#url-validation)). However, there is still residual risk that you should carefully consider when using this tool.

  If data exfiltration is a concern, consider:

  * Disabling the web fetch tool entirely
  * Using the `max_uses` parameter to limit the number of requests
  * Using the `allowed_domains` parameter to restrict to known safe domains
</Warning>

For model support, see the [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference).
