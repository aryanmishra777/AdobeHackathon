# platform.claude.com Documentation (Part 6 of 35)

## How computer use works

Source: https://platform.claude.com/llms-full.txt#how-computer-use-works

<Steps>
  <Step title="Provide Claude with the computer use tool and a user prompt" icon="tool">
    * Add the computer use toolset (and optionally other tools) to the `tools` array of your API request.
    * Include a user prompt that requires desktop interaction, for example, "Save a picture of a cat to my desktop."
  </Step>

  <Step title="Claude responds with member tool calls" icon="wrench">
    * Claude assesses whether acting on the desktop can help with the user's query.
    * If so, Claude responds with one or more member `tool_use` blocks, such as `screenshot`, `left_click`, or `type`, each carrying `"toolset_name": "computer"`. A response with several of these blocks is a [batch action](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#batch-actions).
    * The API response has a `stop_reason` of `tool_use`, signaling a tool use request.
  </Step>

  <Step title="Run the calls in order and return results" icon="computer">
    * Iterate over every `tool_use` block in the response, in order. For each one, dispatch on the member `name` together with `toolset_name`, and perform that action with the block's `input` on your container or virtual machine.
    * Continue the conversation with a new `user` message that contains one `tool_result` block per `tool_use` block, matched by `tool_use_id` and each echoing `"toolset_name": "computer"`. Return an image for `screenshot` and `zoom`; a short text such as `OK` is enough for the other actions.
    * If an action fails, return `is_error: true` for that block and answer the rest of the batch as described in [Batch actions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#batch-actions).
  </Step>

  <Step title="Claude continues until the task is complete" icon="arrows-clockwise">
    * Claude analyzes the tool results to determine if more actions are needed or the task has been completed.
    * If Claude determines more actions are needed, it responds with another `tool_use` `stop_reason` and you should return to step 3.
    * Otherwise, it returns a text response to the user.
  </Step>
</Steps>

The repetition of steps 3 and 4 without user input is referred to as the "agent loop" (that is, Claude responding with a tool use request and your application responding to Claude with the results of evaluating that request).

### Batch actions

Claude can plan a short sequence of actions, such as click, type, and then take a screenshot, and return them together in one response. This is called a batch action; it uses the same response shape as [parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use) with one difference: you run the blocks in order rather than concurrently.

A response with a three-action batch looks like this:

Return one `tool_result` block for each `tool_use` block, matched by `tool_use_id`, all in the next `user` message. Every result for a member tool must carry `"toolset_name": "computer"`; a result that omits it, or that names a different toolset than its `tool_use` block, is rejected. Only `screenshot` and `zoom` results need an image; for the other members, a short text acknowledgment such as `OK` is enough (`cursor_position` returns the coordinates as text):

**Run blocks in order and stop at the first failure.** Later actions in a batch usually depend on earlier ones: the `type` in this example enters text into whatever the preceding click focused. Run the blocks sequentially in the order they appear in `content`, and if one fails, don't run the rest. Every `tool_use` block still needs a `tool_result`, so answer the batch as follows:

* For each action that succeeded, return its normal result.
* For the action that failed, return `is_error: true` with a text description of what went wrong.
* For every later action in the batch, return `is_error: true` with exactly this text (the browser use tool uses its own [halt text](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#batch-actions)):

Claude then sees which actions succeeded, which one failed, and which were skipped, and replans on its next turn. A request that leaves any `tool_use` block in the batch unanswered is rejected with an `invalid_request_error`, so an agent loop that reads only the first block fails on its next call. If your application asks a human to confirm consequential actions, make that check before each block runs, because a batch can complete a multistep action within one turn.

Claude typically finishes a batch with `screenshot` so it can observe the outcome before deciding what to do next. When a batch doesn't end with one, your application can attach a screenshot as an extra `image` block on the last result in the batch so that Claude always sees the current state of the screen, which saves a round trip compared with waiting for Claude to ask. You can also prompt Claude to end every batch with a screenshot (see [Optimize model performance with prompting](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#optimize-model-performance-with-prompting)).

### The computing environment

Computer use requires a sandboxed computing environment where Claude can safely interact with applications and the web. This environment includes:

1. **Virtual display:** A virtual X11 display server (using Xvfb) that renders the desktop interface Claude will see through screenshots and control with mouse/keyboard actions.

2. **Desktop environment:** A lightweight UI with window manager (Mutter) and panel (Tint2) running on Linux, which provides a consistent graphical interface for Claude to interact with.

3. **Applications:** Pre-installed Linux applications such as Firefox, LibreOffice, text editors, and file managers that Claude can use to complete tasks.

4. **Tool implementations:** Integration code that translates Claude's abstract tool requests (such as "move mouse" or "take screenshot") into actual operations in the virtual environment.

5. **Agent loop:** A program that handles communication between Claude and the environment, sending Claude's actions to the environment and returning the results (screenshots, command outputs) back to Claude.

When you use computer use, Claude doesn't directly connect to this environment. Instead, your application:

1. Receives Claude's tool use requests
2. Translates them into actions in your computing environment
3. Captures the results (such as screenshots and command outputs)
4. Returns these results to Claude

For security and isolation, the reference implementation runs all of this inside a Docker container with appropriate port mappings for viewing and interacting with the environment.

***


## How to implement computer use

Source: https://platform.claude.com/llms-full.txt#how-to-implement-computer-use

Upgrading an existing `computer_20251124` integration? Start with [Migrate from `computer_20251124`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#migrate-from-computer-20251124); the rest of this section applies to both new and migrated integrations.

<Tip>
  The [computer use reference implementation](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) is a complete working example: a [containerized environment](https://github.com/anthropics/anthropic-quickstarts/blob/main/computer-use-demo/Dockerfile) suitable for computer use, implementations of [the computer use tools](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo/computer_use_demo/tools), an [agent loop](https://github.com/anthropics/anthropic-quickstarts/blob/main/computer-use-demo/computer_use_demo/loop.py) that calls the Claude API and runs the tools, and a web interface for the container, loop, and tools.
</Tip>

### Understand the agent loop

The core of computer use is the "agent loop": a cycle where Claude requests tool actions, your application runs them, and returns results to Claude. The loop uses the client you created in the [Quick start](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#quick-start), a `tools` array that declares only the computer use toolset, and the tool-call processing helper under [Implement the computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#implement-the-computer-use-tool). If you also declare other tools, such as the Quick start's bash and text editor tools, dispatch their `tool_use` blocks in the same pass; the helper answers only computer use member calls, and the loop treats a turn with no answered calls as finished. Here's a simplified example:

<CodeGroup exclude="shell">
  ```python Python
  def sampling_loop(model: str, messages: list[MessageParam], max_iterations: int = 10):
      """
      Run the computer-use agent loop until Claude stops requesting tools
      or the iteration limit is reached.
      """
      for _ in range(max_iterations):
          response = client.messages.create(
              model=model,
              max_tokens=4096,
              messages=messages,
              tools=TOOLS,
          )

          # Add Claude's response to the conversation history
          messages.append({"role": "assistant", "content": response.content})

          # Run the actions Claude requested, in order, and collect the results
          tool_results = process_tool_calls(response)
          if not tool_results:
              return messages  # No more tool use; task complete

          # Send every result back to Claude in a single user message
          messages.append({"role": "user", "content": tool_results})

      return messages

typescript TypeScript
  async function samplingLoop(
    model: string,
    messages: Anthropic.MessageParam[],
    maxIterations = 10,
  ): Promise<Anthropic.MessageParam[]> {
    // Run the computer-use agent loop until Claude stops requesting tools
    // or the iteration limit is reached.
    for (let i = 0; i < maxIterations; i++) {
      const response = await client.messages.create({
        model,
        max_tokens: 4096,
        messages,
        tools,
      });

      // Add Claude's response to the conversation history
      messages.push({ role: "assistant", content: response.content });

      // Run any tools Claude requested and collect results
      const toolResults = processToolCalls(response);
      if (toolResults.length === 0) {
        return messages; // No more tool use; task complete
      }

      // Send tool results back to Claude for the next iteration
      messages.push({ role: "user", content: toolResults });
    }

    return messages;
  }

csharp C#
  async Task<List<MessageParam>> SamplingLoop(
      Model model,
      List<MessageParam> messages,
      int maxIterations = 10
  )
  {
      // Run the computer-use agent loop until Claude stops requesting tools
      // or the iteration limit is reached.
      for (var i = 0; i < maxIterations; i++)
      {
          var response = await client.Messages.Create(
              new MessageCreateParams
              {
                  Model = model,
                  MaxTokens = 4096,
                  Messages = messages,
                  Tools = tools,
              }
          );

          // Add Claude's response to the conversation history
          messages.Add(
              new()
              {
                  Role = Role.Assistant,
                  Content = response
                      .Content.Select(block => new ContentBlockParam(block.Json))
                      .ToList(),
              }
          );

          // Run any tools Claude requested and collect results
          var toolResults = ProcessToolCalls(response);
          if (toolResults.Count == 0)
          {
              return messages; // No more tool use; task complete
          }

          // Send tool results back to Claude for the next iteration
          messages.Add(new() { Role = Role.User, Content = toolResults });
      }

      return messages;
  }

go Go
  // samplingLoop runs the computer-use agent loop until Claude stops
  // requesting tools or the iteration limit is reached.
  func samplingLoop(ctx context.Context, model anthropic.Model, messages []anthropic.MessageParam, maxIterations int) ([]anthropic.MessageParam, error) {
  	for range maxIterations {
  		response, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  			Model:     model,
  			MaxTokens: 4096,
  			Messages:  messages,
  			Tools:     tools,
  		})
  		if err != nil {
  			return nil, err
  		}

  		// Add Claude's response to the conversation history
  		messages = append(messages, response.ToParam())

  		// Run the actions Claude requested, in order, and collect the results
  		toolResults := processToolCalls(response)
  		if len(toolResults) == 0 {
  			return messages, nil // No more tool use; task complete
  		}

  		// Send every result back to Claude in a single user message
  		messages = append(messages, anthropic.NewUserMessage(toolResults...))
  	}
  	return messages, nil
  }

java Java
  /**
   * Run the computer-use agent loop until Claude stops requesting tools
   * or the iteration limit is reached.
   */
  List<MessageParam> samplingLoop(Model model, List<MessageParam> messages, int maxIterations) {
      for (int i = 0; i < maxIterations; i++) {
          Message response = client.messages().create(MessageCreateParams.builder()
                  .model(model)
                  .maxTokens(4096)
                  .messages(messages)
                  .addTool(COMPUTER_TOOLSET)
                  .build());

          // Add Claude's response to the conversation history
          messages.add(MessageParam.builder()
                  .role(MessageParam.Role.ASSISTANT)
                  .contentOfBlockParams(response.content().stream().map(ContentBlock::toParam).toList())
                  .build());

          // Run any tools Claude requested and collect results
          List<ContentBlockParam> toolResults = processToolCalls(response);
          if (toolResults.isEmpty()) {
              return messages; // No more tool use; task complete
          }

          // Send tool results back to Claude for the next iteration
          messages.add(MessageParam.builder()
                  .role(MessageParam.Role.USER)
                  .contentOfBlockParams(toolResults)
                  .build());
      }
      return messages;
  }

php PHP
  /**
   * Run the computer-use agent loop until Claude stops requesting tools
   * or the iteration limit is reached.
   */
  function samplingLoop(string $model, array $messages, int $maxIterations = 10): array
  {
      global $client, $tools;

      for ($i = 0; $i < $maxIterations; $i++) {
          $response = $client->messages->create(
              model: $model,
              maxTokens: 4096,
              messages: $messages,
              tools: $tools,
          );

          // Add Claude's response to the conversation history
          $messages[] = MessageParam::with(role: Role::ASSISTANT, content: $response->content);

          // Run any tools Claude requested and collect results
          $toolResults = processToolCalls($response);
          if ($toolResults === []) {
              return $messages; // No more tool use; task complete
          }

          // Send tool results back to Claude for the next iteration
          $messages[] = MessageParam::with(role: Role::USER, content: $toolResults);
      }

      return $messages;
  }

ruby Ruby
  # Run the computer-use agent loop until Claude stops requesting tools
  # or the iteration limit is reached.
  def sampling_loop(model, messages, max_iterations: 10)
    max_iterations.times do
      response = CLIENT.messages.create(
        model: model,
        max_tokens: 4096,
        messages: messages,
        tools: TOOLS
      )

      # Add Claude's response to the conversation history
      messages << { role: "assistant", content: response.content }

      # Run the actions Claude requested, in order, and collect the results
      tool_results = process_tool_calls(response)
      return messages if tool_results.empty? # No more tool use; task complete

      # Send every result back to Claude in a single user message
      messages << { role: "user", content: tool_results }
    end

    messages
  end

json
  {
    "type": "tool_use",
    "id": "toolu_01Qg8m3XqC5aRy7tD2eS4jUg",
    "name": "left_click",
    "toolset_name": "computer",
    "input": { "coordinate": [500, 300], "text": "shift" }
  }

json
  {
    "type": "tool_use",
    "id": "toolu_01Ed6j9VnA3yPw5rB8cQ2gSe",
    "name": "left_click_drag",
    "toolset_name": "computer",
    "input": {
      "start_coordinate": [200, 300],
      "coordinate": [600, 300]
    }
  }

json
  {
    "type": "tool_use",
    "id": "toolu_01Yc5h8UmZ2xNv4qA7bP9fRd",
    "name": "scroll",
    "toolset_name": "computer",
    "input": {
      "coordinate": [500, 400],
      "scroll_direction": "down",
      "scroll_amount": 3
    }
  }

json
  {
    "type": "tool_use",
    "id": "toolu_01Sb4g7TkY9wLu3pX6zM8eQc",
    "name": "key",
    "toolset_name": "computer",
    "input": { "text": "Tab", "repeat": 4 }
  }

json
  {
    "type": "tool_use",
    "id": "toolu_01Kf7k2WpB4zQx6sC9dR3hTf",
    "name": "zoom",
    "toolset_name": "computer",
    "input": { "region": [100, 200, 400, 350] }
  }

json
  {
    "type": "tool_use",
    "id": "toolu_01Ekh3vqB6yTs2mNc4Rw8pLd",
    "name": "cursor_position",
    "toolset_name": "computer",
    "input": {}
  }

json
{
  "type": "computer_toolset_20260801",
  "configs": {
    "zoom": { "enabled": false }
  },
  "cache_control": { "type": "ephemeral" }
}

python Python
      # Placeholder image data; a real executor captures the screen and returns the PNG bytes
      PLACEHOLDER_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="


      def capture_screenshot() -> list[ImageBlockParam]:
          # screenshot answers with an image block rather than text: return the result content list
          return [
              {
                  "type": "image",
                  "source": {"type": "base64", "media_type": "image/png", "data": PLACEHOLDER_PNG},
              }
          ]


      def click(coordinate=None):
          if coordinate is None:
              return "clicked at current cursor"
          x, y = coordinate
          return f"clicked at ({x}, {y})"


      def type_text(text):
          return f"typed: {text}"


      def handle_computer_action(name, tool_input):
          if name == "screenshot":
              return capture_screenshot()
          elif name == "left_click":
              # coordinate is optional; without it, click where the cursor already is
              return click(tool_input.get("coordinate"))
          elif name == "type":
              return type_text(tool_input["text"])
          # Handle other actions as needed
          raise ValueError(f"Unknown or unimplemented member: {name}")

typescript TypeScript
      // Placeholder image data; a real executor captures the screen as PNG bytes
      const PLACEHOLDER_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

      function captureScreenshot(): Anthropic.ImageBlockParam[] {
        // screenshot answers with an image block rather than text
        return [
          {
            type: "image",
            source: {
              type: "base64",
              media_type: "image/png",
              data: PLACEHOLDER_PNG,
            },
          },
        ];
      }

      function clickAt(x: number, y: number): string {
        return `clicked at (${x}, ${y})`;
      }

      function clickAtCursor(): string {
        return "clicked at the current cursor position";
      }

      function typeText(text: string): string {
        return `typed: ${text}`;
      }

      function handleComputerAction(
        action: string,
        input: unknown,
      ): string | Anthropic.ImageBlockParam[] {
        const params: object =
          typeof input === "object" && input !== null ? input : {};
        if (action === "screenshot") {
          return captureScreenshot();
        } else if (action === "left_click") {
          // coordinate is optional on the toolset; without one, click at the cursor
          if ("coordinate" in params && Array.isArray(params.coordinate)) {
            const [x, y] = params.coordinate;
            return clickAt(x, y);
          }
          return clickAtCursor();
        } else if (action === "type" && "text" in params) {
          return typeText(String(params.text));
        }
        // Handle other actions as needed
        throw new Error(`Unknown or unimplemented member: ${action}`);
      }

csharp C#
      // Placeholder image data; a real executor captures the screen and returns the PNG bytes
      const string PlaceholderPng = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

      // screenshot answers with an image block rather than text: return the result content list
      List<Block> CaptureScreenshot() =>
          [
              new ImageBlockParam(
                  new Base64ImageSource { Data = PlaceholderPng, MediaType = MediaType.ImagePng }
              ),
          ];

      string ClickAt(int x, int y) => $"clicked at ({x}, {y})";

      string ClickAtCursor() => "clicked at the current cursor position";

      string TypeText(string text) => $"typed: {text}";

      ToolResultBlockParamContent HandleComputerAction(
          string action,
          IReadOnlyDictionary<string, JsonElement> input
      ) =>
          action switch
          {
              "screenshot" => CaptureScreenshot(),
              // coordinate is optional on click members; without it, click where the cursor is
              "left_click" when input.TryGetValue("coordinate", out var xy) => ClickAt(
                  xy[0].GetInt32(),
                  xy[1].GetInt32()
              ),
              "left_click" => ClickAtCursor(),
              "type" => TypeText(input["text"].GetString()!),
              // Handle other actions as needed
              _ => throw new NotSupportedException($"Unknown or unimplemented member: {action}"),
          };

go Go
      // placeholderPNG stands in for a real capture: an executor returns the
      // screen as base64-encoded PNG data.
      const placeholderPNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

      // captureScreenshot returns an image block rather than text.
      func captureScreenshot() []anthropic.ToolResultBlockParamContentUnion {
      	return []anthropic.ToolResultBlockParamContentUnion{{
      		OfImage: &anthropic.ImageBlockParam{
      			Source: anthropic.ImageBlockParamSourceUnion{
      				OfBase64: &anthropic.Base64ImageSourceParam{
      					MediaType: anthropic.Base64ImageSourceMediaTypeImagePNG,
      					Data:      placeholderPNG,
      				},
      			},
      		},
      	}}
      }

      // textContent wraps text as tool_result content.
      func textContent(text string) []anthropic.ToolResultBlockParamContentUnion {
      	return []anthropic.ToolResultBlockParamContentUnion{
      		{OfText: &anthropic.TextBlockParam{Text: text}},
      	}
      }

      func clickAt(x, y int) string {
      	return fmt.Sprintf("clicked at (%d, %d)", x, y)
      }

      func clickAtCursor() string {
      	return "clicked at the current cursor position"
      }

      func typeText(text string) string {
      	return fmt.Sprintf("typed: %s", text)
      }

      func handleComputerAction(action string, params map[string]any) ([]anthropic.ToolResultBlockParamContentUnion, error) {
      	switch action {
      	case "screenshot":
      		return captureScreenshot(), nil
      	case "left_click":
      		// coordinate is optional; without it, click where the cursor already is
      		coord, ok := params["coordinate"].([]any)
      		if !ok {
      			return textContent(clickAtCursor()), nil
      		}
      		if len(coord) == 2 {
      			x, xok := coord[0].(float64)
      			y, yok := coord[1].(float64)
      			if xok && yok {
      				return textContent(clickAt(int(x), int(y))), nil
      			}
      		}
      	case "type":
      		if text, ok := params["text"].(string); ok {
      			return textContent(typeText(text)), nil
      		}
      	// Handle other actions as needed
      	default:
      		return nil, fmt.Errorf("unknown or unimplemented member: %s", action)
      	}
      	// Reached when a member's input is missing a field or a field has the wrong type
      	return nil, fmt.Errorf("invalid input for %s", action)
      }

java Java
      /** Placeholder pixels; a real executor captures the screen and base64-encodes the PNG. */
      static final String PLACEHOLDER_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

      ToolResultBlockParam.Content captureScreenshot() {
          ImageBlockParam image = ImageBlockParam.builder()
                  .source(Base64ImageSource.builder()
                          .mediaType(Base64ImageSource.MediaType.IMAGE_PNG)
                          .data(PLACEHOLDER_PNG)
                          .build())
                  .build();
          return ToolResultBlockParam.Content.ofBlocks(
                  List.of(ToolResultBlockParam.Content.Block.ofImage(image)));
      }

      String clickAt(long x, long y) {
          return "clicked at (" + x + ", " + y + ")";
      }

      String clickAtCursor() {
          return "clicked at current cursor";
      }

      String typeText(String text) {
          return "typed: " + text;
      }

      /** Runs one computer toolset member; {@code action} is the tool_use block's name. */
      ToolResultBlockParam.Content handleComputerAction(String action, Map<String, JsonValue> input) {
          if (action.equals("screenshot")) {
              return captureScreenshot(); // the one member here that answers with an image block
          }
          String output = switch (action) {
              case "left_click" -> {
                  JsonValue coordinate = input.get("coordinate"); // optional on the toolset
                  if (coordinate == null) {
                      yield clickAtCursor();
                  }
                  List<JsonValue> point = (List<JsonValue>) coordinate.asArray().get();
                  long x = ((Number) point.get(0).asNumber().get()).longValue();
                  long y = ((Number) point.get(1).asNumber().get()).longValue();
                  yield clickAt(x, y);
              }
              case "type" -> typeText(input.get("text").asStringOrThrow());
              // Handle other actions as needed
              default -> throw new UnsupportedOperationException("Unknown or unimplemented member: " + action);
          };
          return ToolResultBlockParam.Content.ofString(output);
      }

php PHP
      // Stand-in for real PNG bytes; a real executor captures the screen
      const PLACEHOLDER_PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';

      function captureScreenshot(): array
      {
          // screenshot answers with an image block rather than text, so return the result content list
          $image = [
              'type' => 'image',
              'source' => ['type' => 'base64', 'media_type' => 'image/png', 'data' => PLACEHOLDER_PNG],
          ];

          return [$image];
      }

      function clickAt(?array $coordinate): string
      {
          // left_click may omit coordinate, in which case the click lands where the cursor already is
          if ($coordinate === null) {
              return 'clicked at current cursor';
          }
          [$x, $y] = $coordinate;

          return "clicked at ({$x}, {$y})";
      }

      function typeText(string $text): string
      {
          return "typed: {$text}";
      }

      function handleComputerAction(string $name, array $input): string|array
      {
          return match ($name) {
              'screenshot' => captureScreenshot(),
              'left_click' => clickAt($input['coordinate'] ?? null),
              'type' => typeText($input['text']),
              // Handle other actions as needed
              default => throw new RuntimeException("Unknown or unimplemented member: {$name}"),
          };
      }

ruby Ruby
      # Stand-in image data; a real executor captures the screen as a PNG.
      PLACEHOLDER_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

      # screenshot answers with an image block rather than text
      def capture_screenshot
        [
          {
            type: "image",
            source: { type: "base64", media_type: "image/png", data: PLACEHOLDER_PNG }
          }
        ]
      end

      def click(coordinate = nil)
        return "clicked at current cursor" if coordinate.nil?

        x, y = coordinate
        "clicked at (#{x}, #{y})"
      end

      def type_text(text)
        "typed: #{text}"
      end

      def handle_computer_action(name, input)
        case name
        when "screenshot"
          capture_screenshot
        when "left_click"
          # coordinate is optional; without it, click where the cursor already is
          click(input[:coordinate])
        when "type"
          type_text(input[:text])
        # Handle other actions as needed
        else
          raise ArgumentError, "Unknown or unimplemented member: #{name}"
        end
      end

python Python
      NOT_EXECUTED = "Not executed: an earlier computer action in this turn failed."


      def process_tool_calls(response: Message) -> list[ToolResultBlockParam]:
          """
          Run the computer actions in Claude's response in order and answer each
          one. After the first failure the rest are skipped, because Claude planned
          them assuming the earlier actions succeeded.
          """
          tool_results: list[ToolResultBlockParam] = []
          failed = False
          for block in response.content:
              # Only the computer toolset is declared; route other tools here if you add them
              if block.type != "tool_use" or block.toolset_name != "computer":
                  continue
              result: ToolResultBlockParam = {
                  "type": "tool_result",
                  "tool_use_id": block.id,
                  "toolset_name": "computer",
              }
              if failed:
                  result["content"] = NOT_EXECUTED
                  result["is_error"] = True
              else:
                  try:
                      # A string, or a list of content blocks such as the screenshot image
                      result["content"] = handle_computer_action(block.name, block.input)
                  except Exception as err:
                      result["content"] = f"Error: {err}"
                      result["is_error"] = True
                      failed = True
              tool_results.append(result)
          return tool_results

typescript TypeScript
      const HALT_TEXT =
        "Not executed: an earlier computer action in this turn failed.";

      function computerResult(
        toolUseId: string,
        content: string | Anthropic.ImageBlockParam[],
        isError?: boolean,
      ): Anthropic.ToolResultBlockParam {
        return {
          type: "tool_result",
          tool_use_id: toolUseId,
          toolset_name: "computer",
          content,
          is_error: isError,
        };
      }

      function processToolCalls(
        response: Anthropic.Message,
      ): Anthropic.ToolResultBlockParam[] {
        const toolResults: Anthropic.ToolResultBlockParam[] = [];
        let failed = false;
        for (const block of response.content) {
          if (block.type !== "tool_use") {
            continue;
          }
          if (block.toolset_name !== "computer") {
            // This example declares only the computer toolset; route other tools
            // here if you add them.
            continue;
          }
          if (failed) {
            // A batch stops at its first failure; answer later actions unexecuted
            toolResults.push(computerResult(block.id, HALT_TEXT, true));
            continue;
          }
          try {
            // A string, or the image block list that screenshot returns
            const result = handleComputerAction(block.name, block.input);
            toolResults.push(computerResult(block.id, result));
          } catch (error) {
            failed = true;
            const message = error instanceof Error ? error.message : String(error);
            toolResults.push(computerResult(block.id, `Error: ${message}`, true));
          }
        }
        return toolResults;
      }

csharp C#
      const string HaltText = "Not executed: an earlier computer action in this turn failed.";

      List<ContentBlockParam> ProcessToolCalls(Message response)
      {
          List<ContentBlockParam> toolResults = [];
          var failed = false;
          foreach (var block in response.Content)
          {
              if (!block.TryPickToolUse(out var toolUse))
              {
                  continue;
              }

              if (toolUse.ToolsetName != "computer")
              {
                  // This example declares only the computer toolset; route other tools
                  // here if you add them.
                  continue;
              }

              if (failed)
              {
                  // A batch stops at its first failure; answer later actions without running them
                  toolResults.Add(
                      new ToolResultBlockParam(toolUse.ID)
                      {
                          Content = HaltText,
                          IsError = true,
                          ToolsetName = "computer",
                      }
                  );
                  continue;
              }

              try
              {
                  // A string, or the image block list that screenshot returns
                  var result = HandleComputerAction(toolUse.Name, toolUse.Input);
                  toolResults.Add(
                      new ToolResultBlockParam(toolUse.ID) { Content = result, ToolsetName = "computer" }
                  );
              }
              catch (Exception e)
              {
                  failed = true;
                  toolResults.Add(
                      new ToolResultBlockParam(toolUse.ID)
                      {
                          Content = $"Error: {e.Message}",
                          IsError = true,
                          ToolsetName = "computer",
                      }
                  );
              }
          }
          return toolResults;
      }

go Go
      const notExecuted = "Not executed: an earlier computer action in this turn failed."

      // computerToolResult builds the result for one computer action. Unlike an
      // ordinary tool result, it must echo the toolset name.
      func computerToolResult(toolUseID string, content []anthropic.ToolResultBlockParamContentUnion, isError bool) anthropic.ContentBlockParamUnion {
      	result := anthropic.ToolResultBlockParam{
      		ToolUseID:   toolUseID,
      		ToolsetName: anthropic.String("computer"),
      		Content:     content,
      	}
      	if isError {
      		result.IsError = anthropic.Bool(true)
      	}
      	return anthropic.ContentBlockParamUnion{OfToolResult: &result}
      }

      // processToolCalls runs the computer actions in Claude's response in order and
      // builds one tool_result per tool_use block. After the first failure it skips
      // the rest: Claude planned them assuming the earlier actions succeeded.
      func processToolCalls(response *anthropic.Message) []anthropic.ContentBlockParamUnion {
      	var toolResults []anthropic.ContentBlockParamUnion
      	failed := false
      	for _, block := range response.Content {
      		switch variant := block.AsAny().(type) {
      		case anthropic.ToolUseBlock:
      			// This example declares only the computer toolset; route other tools here if you add them.
      			if variant.ToolsetName != "computer" {
      				continue
      			}
      			if failed {
      				toolResults = append(toolResults, computerToolResult(variant.ID, textContent(notExecuted), true))
      				continue
      			}
      			var input map[string]any
      			var content []anthropic.ToolResultBlockParamContentUnion
      			err := json.Unmarshal(variant.Input, &input)
      			if err == nil {
      				// Text, or the image block that screenshot returns
      				content, err = handleComputerAction(variant.Name, input)
      			}
      			if err != nil {
      				failed = true
      				content = textContent("Error: " + err.Error())
      			}
      			toolResults = append(toolResults, computerToolResult(variant.ID, content, err != nil))
      		}
      	}
      	return toolResults
      }

java Java
      /** The exact text the toolset contract prescribes for member calls skipped after a failure. */
      static final String HALT_TEXT = "Not executed: an earlier computer action in this turn failed.";

      /** Every result answering a computer toolset member echoes toolset_name. */
      ToolResultBlockParam.Builder computerResult(ToolUseBlock toolUse) {
          return ToolResultBlockParam.builder()
                  .toolUseId(toolUse.id())
                  .toolsetName("computer");
      }

      /**
       * Run the computer actions in Claude's response in order and build one
       * tool_result per tool_use block. After the first failure, skip the rest:
       * Claude planned them assuming the earlier actions succeeded.
       */
      List<ContentBlockParam> processToolCalls(Message response) {
          List<ContentBlockParam> toolResults = new ArrayList<>();
          boolean failed = false;
          for (ContentBlock block : response.content()) {
              // This example declares only the computer toolset; route other tools here if you add them.
              if (!block.isToolUse() || !block.asToolUse().toolsetName().equals(Optional.of("computer"))) {
                  continue;
              }
              ToolUseBlock toolUse = block.asToolUse();
              ToolResultBlockParam result;
              if (failed) {
                  result = computerResult(toolUse).content(HALT_TEXT).isError(true).build();
              } else {
                  try {
                      Map<String, JsonValue> input =
                              (Map<String, JsonValue>) toolUse._input().asObject().get();
                      // A string, or the image block that screenshot returns
                      ToolResultBlockParam.Content output = handleComputerAction(toolUse.name(), input);
                      result = computerResult(toolUse).content(output).build();
                  } catch (RuntimeException e) {
                      failed = true;
                      result = computerResult(toolUse).content("Error: " + e.getMessage()).isError(true).build();
                  }
              }
              toolResults.add(ContentBlockParam.ofToolResult(result));
          }
          return toolResults;
      }

php PHP
      const HALT_TEXT = 'Not executed: an earlier computer action in this turn failed.';

      function processToolCalls(Message $response): array
      {
          $toolResults = [];
          $failed = false;
          foreach ($response->content as $block) {
              // This example declares only the computer toolset; route other tools here if you add them.
              if (!($block instanceof ToolUseBlock) || $block->toolsetName !== 'computer') {
                  continue;
              }
              $result = ['type' => 'tool_result', 'tool_use_id' => $block->id, 'toolset_name' => 'computer'];
              if ($failed) {
                  // A batch stops at its first failure; the remaining actions are answered without running
                  $toolResults[] = [...$result, 'content' => HALT_TEXT, 'is_error' => true];
                  continue;
              }
              try {
                  // A string, or the image block list that screenshot returns
                  $toolResults[] = [...$result, 'content' => handleComputerAction($block->name, $block->input)];
              } catch (Throwable $e) {
                  $failed = true;
                  $toolResults[] = [...$result, 'content' => 'Error: ' . $e->getMessage(), 'is_error' => true];
              }
          }

          return $toolResults;
      }

ruby Ruby
      NOT_EXECUTED = "Not executed: an earlier computer action in this turn failed."

      # Run the computer actions in Claude's response in order and build one
      # tool_result per tool_use block. After the first failure, skip the rest:
      # Claude planned them assuming the earlier actions succeeded.
      def process_tool_calls(response)
        tool_results = []
        failed = false
        response.content.each do |block|
          # This example declares only the computer toolset; route other tools here
          # if you add them.
          next unless block.type == :tool_use && block.toolset_name == "computer"

          result = { type: "tool_result", tool_use_id: block.id, toolset_name: "computer" }
          if failed
            result.update(content: NOT_EXECUTED, is_error: true)
          else
            begin
              # A String, or the image content blocks that screenshot returns
              result[:content] = handle_computer_action(block.name, block.input)
            rescue => e
              result.update(content: "Error: #{e.message}", is_error: true)
              failed = true
            end
          end
          tool_results << result
        end
        tool_results
      end

json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "toolset_name": "computer",
      "content": "Error: Failed to capture screenshot. Display may be locked or unavailable.",
      "is_error": true
    }
  ]
}

python Python
  import math

  screen_width, screen_height = 1512, 982


  def get_scale_factor(width, height):
      """Calculate scale factor to meet API constraints."""
      long_edge = max(width, height)
      total_pixels = width * height

      long_edge_scale = 1568 / long_edge
      total_pixels_scale = math.sqrt(1_150_000 / total_pixels)

      return min(1.0, long_edge_scale, total_pixels_scale)


  # When capturing screenshot
  scale = get_scale_factor(screen_width, screen_height)
  scaled_width = int(screen_width * scale)
  scaled_height = int(screen_height * scale)

  # Resize image to scaled dimensions before sending to Claude
  screenshot = capture_and_resize(scaled_width, scaled_height)


  # When handling Claude's coordinates, scale them back up
  def execute_click(x, y):
      screen_x = x / scale
      screen_y = y / scale
      perform_click(screen_x, screen_y)

typescript TypeScript
  const screenWidth = 1512;
  const screenHeight = 982;
  const MAX_LONG_EDGE = 1568;
  const MAX_PIXELS = 1_150_000;

  function getScaleFactor(width: number, height: number): number {
    const longEdge = Math.max(width, height);
    const totalPixels = width * height;

    const longEdgeScale = MAX_LONG_EDGE / longEdge;
    const totalPixelsScale = Math.sqrt(MAX_PIXELS / totalPixels);

    return Math.min(1.0, longEdgeScale, totalPixelsScale);
  }

  // When capturing screenshot
  const scale = getScaleFactor(screenWidth, screenHeight);
  const scaledWidth = Math.floor(screenWidth * scale);
  const scaledHeight = Math.floor(screenHeight * scale);

  // Resize image to scaled dimensions before sending to Claude
  const screenshot = captureAndResize(scaledWidth, scaledHeight);

  // When handling Claude's coordinates, scale them back up
  function executeClick(x: number, y: number): void {
    const screenX = x / scale;
    const screenY = y / scale;
    performClick(screenX, screenY);
  }

csharp C#
  int screenWidth = 1512, screenHeight = 982;

  double GetScaleFactor(int width, int height)
  {
      // Calculate scale factor to meet API constraints.
      int longEdge = Math.Max(width, height);
      int totalPixels = width * height;

      double longEdgeScale = 1568.0 / longEdge;
      double totalPixelsScale = Math.Sqrt(1_150_000.0 / totalPixels);

      return Math.Min(1.0, Math.Min(longEdgeScale, totalPixelsScale));
  }

  // When capturing screenshot
  double scale = GetScaleFactor(screenWidth, screenHeight);
  int scaledWidth = (int)(screenWidth * scale);
  int scaledHeight = (int)(screenHeight * scale);

  // Resize image to scaled dimensions before sending to Claude
  var screenshot = CaptureAndResize(scaledWidth, scaledHeight);

  // When handling Claude's coordinates, scale them back up
  void ExecuteClick(int x, int y)
  {
      double screenX = x / scale;
      double screenY = y / scale;
      PerformClick(screenX, screenY);
  }

go Go
  func getScaleFactor(width, height int) float64 {
  	longest := float64(max(width, height))
  	area := float64(width * height)
  	return min(1.0, 1568/longest, math.Sqrt(1_150_000/area))
  }

  // ...
  	screenWidth, screenHeight := 1512, 982

  	// When capturing screenshot
  	scale := getScaleFactor(screenWidth, screenHeight)
  	scaledWidth := int(float64(screenWidth) * scale)
  	scaledHeight := int(float64(screenHeight) * scale)

  	// Resize image to scaled dimensions before sending to Claude
  	screenshot := captureAndResize(scaledWidth, scaledHeight)

  	// When handling Claude's coordinates, scale them back up
  	executeClick := func(x, y int) {
  		performClick(float64(x)/scale, float64(y)/scale)
  	}

java Java
  static double getScaleFactor(int width, int height) {
      return Math.min(
          1.0,
          Math.min(
              1568.0 / Math.max(width, height),
              Math.sqrt(1_150_000.0 / (width * height))
          )
      );
  }

  void main() {
      int screenWidth = 1512, screenHeight = 982;

      // When capturing screenshot
      double scale = getScaleFactor(screenWidth, screenHeight);
      int scaledWidth = (int)(screenWidth * scale);
      int scaledHeight = (int)(screenHeight * scale);

      // Resize image to scaled dimensions before sending to Claude
      var screenshot = captureAndResize(scaledWidth, scaledHeight);

      // When handling Claude's coordinates, scale them back up
      BiConsumer<Integer, Integer> executeClick =
          (x, y) -> performClick(x / scale, y / scale);
  // ...
  }

php PHP
  function getScaleFactor(int $width, int $height): float
  {
      return min(
          1.0,
          1568 / max($width, $height),
          sqrt(1_150_000 / ($width * $height)),
      );
  }

  $screenWidth = 1512;
  $screenHeight = 982;

  // When capturing screenshot
  $scale = getScaleFactor($screenWidth, $screenHeight);
  $scaledWidth = (int)($screenWidth * $scale);
  $scaledHeight = (int)($screenHeight * $scale);

  // Resize image to scaled dimensions before sending to Claude
  $screenshot = captureAndResize($scaledWidth, $scaledHeight);

  // When handling Claude's coordinates, scale them back up
  $executeClick = fn(int $x, int $y) => performClick($x / $scale, $y / $scale);

ruby Ruby
  def get_scale_factor(width, height)
    [1.0, 1568.0 / [width, height].max, Math.sqrt(1_150_000.0 / (width * height))].min
  end

  screen_width, screen_height = 1512, 982

  # When capturing screenshot
  scale = get_scale_factor(screen_width, screen_height)
  scaled_width = (screen_width * scale).to_i
  scaled_height = (screen_height * scale).to_i

  # Resize image to scaled dimensions before sending to Claude
  screenshot = capture_and_resize(scaled_width, scaled_height)

  # When handling Claude's coordinates, scale them back up
  execute_click = ->(x, y) { perform_click(x / scale, y / scale) }

python Python
      def click_and_wait(x, y, wait_time=0.5):
          click_at(x, y)
          time.sleep(wait_time)  # Allow UI to update

typescript TypeScript
      async function clickAndWait(x: number, y: number, waitMs = 500): Promise<void> {
        clickAt(x, y);
        await setTimeout(waitMs); // Allow UI to update
      }

csharp C#
      static void ClickAndWait(int x, int y, double waitSeconds = 0.5)
      {
          ClickAt(x, y);
          Thread.Sleep(TimeSpan.FromSeconds(waitSeconds));  // Allow UI to update
      }

go Go
      func clickAndWaitFor(x, y int, wait time.Duration) {
      	clickAt(x, y)
      	time.Sleep(wait) // Allow UI to update
      }

      func clickAndWait(x, y int) {
      	clickAndWaitFor(x, y, 500*time.Millisecond)
      }

java Java
      void clickAndWait(int x, int y) throws InterruptedException {
          clickAndWait(x, y, 500);
      }

      void clickAndWait(int x, int y, long waitTimeMillis) throws InterruptedException {
          clickAt(x, y);
          Thread.sleep(waitTimeMillis);  // Allow UI to update
      }

php PHP
      function clickAndWait(int $x, int $y, float $waitSeconds = 0.5): void
      {
          clickAt($x, $y);
          usleep((int) ($waitSeconds * 1_000_000));  // Allow UI to update
      }

ruby Ruby
      def click_and_wait(x, y, wait_time: 0.5)
        click_at(x, y)
        sleep(wait_time) # Allow UI to update
      end

python Python
      display_width, display_height = 1024, 768


      def validate_action(action_type, params):
          if action_type == "left_click" and "coordinate" in params:
              x, y = params["coordinate"]
              if not (0 <= x < display_width and 0 <= y < display_height):
                  return False, "Coordinates out of bounds"
          return True, None

typescript TypeScript
      const displayWidth = 1024;
      const displayHeight = 768;

      interface ActionParams {
        coordinate?: [number, number];
      }

      function validateAction(actionType: string, params: ActionParams): [boolean, string | null] {
        if (actionType === "left_click" && params.coordinate) {
          const [x, y] = params.coordinate;
          if (!(x >= 0 && x < displayWidth && y >= 0 && y < displayHeight)) {
            return [false, "Coordinates out of bounds"];
          }
        }
        return [true, null];
      }

csharp C#
      const int DisplayWidth = 1024;
      const int DisplayHeight = 768;
      // ...
      static (bool IsValid, string? Error) ValidateAction(string actionType, IReadOnlyDictionary<string, JsonElement> parameters)
      {
          if (actionType == "left_click" && parameters.TryGetValue("coordinate", out JsonElement coordinate))
          {
              int x = coordinate[0].GetInt32();
              int y = coordinate[1].GetInt32();
              if (x is < 0 or >= DisplayWidth || y is < 0 or >= DisplayHeight)
              {
                  return (false, "Coordinates out of bounds");
              }
          }
          return (true, null);
      }

go Go
      const (
      	displayWidth  = 1024
      	displayHeight = 768
      )

      func validateAction(actionType string, params map[string]any) (bool, string) {
      	raw, hasCoordinate := params["coordinate"]
      	if actionType == "left_click" && hasCoordinate {
      		coord, ok := raw.([]any)
      		if !ok || len(coord) != 2 {
      			return false, "Invalid coordinate"
      		}
      		x, y := int(coord[0].(float64)), int(coord[1].(float64))
      		if !(0 <= x && x < displayWidth && 0 <= y && y < displayHeight) {
      			return false, "Coordinates out of bounds"
      		}
      	}
      	return true, ""
      }

java Java
      static final int DISPLAY_WIDTH = 1024;
      static final int DISPLAY_HEIGHT = 768;

      record Validation(boolean valid, String error) {}

      Validation validateAction(String actionType, Map<String, JsonValue> params) {
          if (actionType.equals("left_click") && params.containsKey("coordinate")) {
              List<JsonValue> coord = (List<JsonValue>) params.get("coordinate").asArray().get();
              long x = ((Number) coord.get(0).asNumber().get()).longValue();
              long y = ((Number) coord.get(1).asNumber().get()).longValue();
              if (!(0 <= x && x < DISPLAY_WIDTH && 0 <= y && y < DISPLAY_HEIGHT)) {
                  return new Validation(false, "Coordinates out of bounds");
              }
          }
          return new Validation(true, null);
      }

php PHP
      const DISPLAY_WIDTH = 1024;
      const DISPLAY_HEIGHT = 768;

      /** @return array{bool, ?string} */
      function validateAction(string $actionType, array $params): array
      {
          if ($actionType === 'left_click' && isset($params['coordinate'])) {
              [$x, $y] = $params['coordinate'];
              if (!(0 <= $x && $x < DISPLAY_WIDTH && 0 <= $y && $y < DISPLAY_HEIGHT)) {
                  return [false, 'Coordinates out of bounds'];
              }
          }
          return [true, null];
      }

ruby Ruby
      DISPLAY_WIDTH = 1024
      DISPLAY_HEIGHT = 768

      def validate_action(action_type, params)
        if action_type == "left_click" && params.key?(:coordinate)
          x, y = params[:coordinate]
          unless (0...DISPLAY_WIDTH).cover?(x) && (0...DISPLAY_HEIGHT).cover?(y)
            return [false, "Coordinates out of bounds"]
          end
        end
        [true, nil]
      end

python Python
      import logging


      def log_action(action_type, params, result):
          logging.info(f"Action: {action_type}, Params: {params}, Result: {result}")

typescript TypeScript
      function logAction(actionType: string, params: unknown, result: unknown): void {
        console.error(
          `Action: ${actionType}, Params: ${JSON.stringify(params)}, Result: ${JSON.stringify(
            result
          )}`
        );
      }

csharp C#
      static void LogAction(string actionType, object? parameters, object? result)
      {
          Console.Error.WriteLine($"Action: {actionType}, Params: {parameters}, Result: {result}");
      }

go Go
      func logAction(actionType string, params map[string]any, result any) {
      	log.Printf("Action: %s, Params: %v, Result: %v", actionType, params, result)
      }

java Java
      import static java.lang.System.Logger.Level.INFO;

      static final System.Logger LOGGER = System.getLogger("computer-use");

      void logAction(String actionType, Object params, Object result) {
          LOGGER.log(INFO, "Action: {0}, Params: {1}, Result: {2}", actionType, params, result);
      }

php PHP
      function logAction(string $actionType, array $params, mixed $result): void
      {
          error_log(sprintf(
              'Action: %s, Params: %s, Result: %s',
              $actionType,
              json_encode($params),
              json_encode($result),
          ));
      }

ruby Ruby
      require "logger"

      LOGGER = Logger.new($stderr)

      def log_action(action_type, params, result)
        LOGGER.info("Action: #{action_type}, Params: #{params}, Result: #{result}")
      end
      ```
    </CodeGroup>
  </Accordion>
</AccordionGroup>

***


## Migrate from `computer_20251124`

Source: https://platform.claude.com/llms-full.txt#migrate-from-computer-20251124

Upgrading from `computer_20251124` to the toolset is optional: the models listed for `computer_20251124` under [Earlier tool versions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#earlier-tool-versions) keep accepting it with its beta header, so an existing integration keeps working until you change it. To upgrade, make the following changes together:

1. **Remove the beta header.** Drop `anthropic-beta: computer-use-2025-11-24` from your requests. In the SDKs, remove the `betas` parameter and call the Messages API through the standard client rather than the beta namespace.
2. **Change the `tools` entry.** Set `type` to `computer_toolset_20260801` and delete `name`, `display_width_px`, `display_height_px`, `display_number`, and `enable_zoom`. The toolset rejects each of these fields.
3. **Choose whether to keep zoom enabled.** Zoom is enabled by default on the toolset, whereas `enable_zoom` defaults to `false`. If your environment doesn't implement zoom, add `"configs": {"zoom": {"enabled": false}}` to keep the previous behavior; otherwise implement it (see [Available actions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#available-actions)).
4. **Handle every block in a turn.** Update your agent loop to iterate over every `tool_use` block in a response rather than reading only the first, and to dispatch on the block's `name` together with `toolset_name` instead of on `input.action`. Member inputs no longer contain an `action` field; the remaining fields are unchanged.
5. **Run blocks in order and use the halt text.** Run the blocks sequentially, stop at the first failure, and answer the remaining blocks with `Not executed: an earlier computer action in this turn failed.` as described in [Batch actions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#batch-actions). If your loop can't run batches yet, [Tool parameters](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#tool-parameters) explains how to limit Claude to one action per turn.
6. **Echo `toolset_name` on results.** Add `"toolset_name": "computer"` to every `tool_result` that answers a member call. Results may contain only `text` and `image` content.
7. **Support `repeat` on `key`.** The `key` member accepts an optional `repeat` count from 1 to 100. A handler that ignores unrecognized fields would press the key once, so make your `key` handler honor `repeat`.
8. **Resize screenshots yourself.** The toolset rejects a screenshot or zoom image that exceeds the model's image limits instead of downscaling it. Resize before returning the image and keep scaling coordinates as described in [Size screenshots to fit image limits](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#handle-coordinate-scaling-for-higher-resolutions).
9. **Remove unsupported options.** Move any `defer_loading` from the entry into `configs`, with the same value on every enabled member. The other options not supported on toolset entries are listed under [Client toolsets](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets).

This is the `tools` entry before the change, sent with the `anthropic-beta: computer-use-2025-11-24` header:

This is the `tools` entry after the change, sent with no beta header. The `configs` object keeps zoom off to match the earlier entry, which doesn't set `enable_zoom`; omit `configs` entirely to accept the default and let Claude zoom:

The following pair shows a `tool_use` block before and after the change. The action name moves from `input.action` to `name`, and the block gains `toolset_name`:


## Earlier tool versions

Source: https://platform.claude.com/llms-full.txt#earlier-tool-versions

Two earlier versions of the computer use tool remain available in beta for existing integrations, for models that don't support the toolset, and on platforms where the toolset isn't currently available. Each requires its [beta header](https://platform.claude.com/docs/en/api/beta-headers) on every request, and their parameters are documented in the [beta Messages API reference](https://platform.claude.com/docs/en/api/beta/messages/create). In the SDKs, pass the header through the `betas` parameter and use the beta namespace; only the computer use tool needs the header, not the bash or text editor tools in the same request.

| Tool version        | Beta header               | Use with                                                                                                                                                                                                                                                                                                                                                                                                                                    | Parameters                                                                    |
| ------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `computer_20251124` | `computer-use-2025-11-24` | Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, Claude Opus 5, Claude Sonnet 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 4.6, and Claude Opus 4.5                                                                                                                                                                                                                                             | [API reference](https://platform.claude.com/docs/en/api/beta/messages/create) |
| `computer_20250124` | `computer-use-2025-01-24` | Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.1 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)), Claude Sonnet 4 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)), and Claude Opus 4 ([retired, except on Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)) | [API reference](https://platform.claude.com/docs/en/api/beta/messages/create) |

***


## Limitations

Source: https://platform.claude.com/llms-full.txt#limitations-4

1. **Latency:** The current computer use latency for human-AI interactions might be too slow compared to regular human-directed computer actions. Focus on use cases where speed isn't critical (for example, background information gathering, automated software testing) in trusted environments.
2. **Computer vision accuracy and reliability:** Claude might make mistakes or hallucinate when outputting specific coordinates while generating actions. Claude's [summarized thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#summarized-thinking) output can help you understand the model's reasoning and identify potential issues; set `display: "summarized"` on the thinking configuration, because the models that support the toolset omit thinking text by default.
3. **Tool selection accuracy and reliability:** Claude might make mistakes or hallucinate when selecting tools while generating actions or take unexpected actions to solve problems. Additionally, reliability might be lower when interacting with niche applications or multiple applications at once. Prompt the model carefully when requesting complex tasks.
4. **Scrolling reliability:** The scroll action supports direction control (up, down, left, right) and a specified amount. In applications where scrolling doesn't take effect, keyboard alternatives such as Page Down can help.
5. **Spreadsheet interaction:** Use the fine-grained mouse control actions (`left_mouse_down`, `left_mouse_up`) and modifier-key combinations to select individual cells. Complex spreadsheet operations might still require multiple attempts.
6. **Account creation and content generation on social and communications platforms:** Although Claude visits websites, its ability to create accounts, generate and share content, or otherwise engage in human impersonation across social media websites and platforms is limited.
7. **Vulnerabilities:** Jailbreaks and prompt injection can affect computer use as they can any frontier AI system, including through instructions embedded in webpages or images; apply the precautions in [Security considerations](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#security-considerations).
8. **Inappropriate or illegal actions:** Under Anthropic's Terms of Service, you must not employ computer use to violate any laws or the Acceptable Use Policy.

Always carefully review and verify Claude's computer use actions and logs. Do not use Claude for tasks requiring perfect precision or sensitive user information without human oversight.


## Data retention

Source: https://platform.claude.com/llms-full.txt#data-retention-4

Computer use is a client-side tool. All screenshots, mouse actions, keyboard inputs, and any files involved in a session are captured and stored in your environment, not by Anthropic. Anthropic processes the screenshot images and action requests in real time as part of the API call. Retention for those API requests is governed by [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).

Because your application controls where and how computer use data is stored, computer use is ZDR eligible. For ZDR eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).


## Pricing

Source: https://platform.claude.com/llms-full.txt#pricing-7

Computer use follows the standard [tool use pricing](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview#pricing). When using the computer use tool:

**Toolset definition overhead:** Declaring `computer_toolset_20260801` with its default members adds about 4,500 input tokens to a request (about 4,520 on Claude Fable 5, Claude Mythos 5, Claude Opus 5, and Claude Opus 4.8, and about 4,590 on Claude Sonnet 5), which covers the member tool definitions and the tool use system prompt. Disabling `zoom` with `configs` removes about 410 of those tokens. The exact count for a request is reported in the response `usage`, and you can estimate it in advance with the [token counting endpoint](https://platform.claude.com/docs/en/build-with-claude/token-counting).

**Earlier tool versions:** The following figures apply to the `computer_20251124` and `computer_20250124` tool versions, not to `computer_toolset_20260801`:

* System prompt overhead: 466–499 tokens added to the system prompt
* Tool definition: about 735 input tokens per tool definition (measured with `computer_20250124`)

**Additional token consumption:**

* Screenshot and zoom images returned in tool results, billed as image input (see [Vision pricing](https://platform.claude.com/docs/en/build-with-claude/vision#evaluate-image-size))
* Tool execution results returned to Claude

<Note>
  If you're also using bash or text editor tools alongside computer use, those tools have their own token costs as documented in their respective pages.
</Note>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-28

<CardGroup cols={2}>
  <Card title="Troubleshooting tool use" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/troubleshooting-tool-use">
    Fix the most common tool-use errors with symptom-to-fix diagnostic tables.
  </Card>

  <Card title="Reference implementation" icon="github-logo" href="https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo">
    Get started with the complete Docker-based implementation
  </Card>

  <Card title="Tool use with Claude" icon="tool" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview">
    Connect Claude to external tools and APIs. See where tools execute, when Claude calls them, and which tool fits your task.
  </Card>

  <Card title="Best practices in detail" icon="book" href="https://claude.com/blog/best-practices-for-computer-and-browser-use-with-claude">
    Benchmarked recommendations for resolution, thinking effort, and context management
  </Card>

  <Card title="Browser use tool" icon="browser" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool">
    Let Claude navigate, read, and interact with webpages in your own browser environment, for tasks that stay inside the browser.
  </Card>
</CardGroup>


---
title: Define tools
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools
description: Specify tool schemas, write effective descriptions, and control when Claude calls your tools.
---


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-2

* Familiarity with the [tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
* A Claude API key and a working SDK or cURL setup

<Tip>
  If using Claude with tool use and thinking, see [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) for more information.
</Tip>


## Specifying client tools

Source: https://platform.claude.com/llms-full.txt#specifying-client-tools

Client tools are specified in the `tools` top-level parameter of the API request. Anthropic-schema client tools, such as the bash and text editor tools, are declared by a date-versioned `type`; see each tool's page, linked from the [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference), for the fields it accepts. The computer use and browser use tools are [client toolsets](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets): a single entry with no `name` that declares a fixed set of member tools. A user-defined tool definition includes:

| Parameter        | Description                                                                                                                                                                                                                            |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`           | The name of the tool. Must match the regex `^[a-zA-Z0-9_-]{1,64}$`.                                                                                                                                                                    |
| `description`    | A detailed plaintext description of what the tool does, when it should be used, and how it behaves.                                                                                                                                    |
| `input_schema`   | A [JSON Schema](https://json-schema.org/) object defining the expected parameters for the tool.                                                                                                                                        |
| `input_examples` | (Optional) An array of example input objects to help Claude understand how to use the tool. See [Providing tool use examples](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools#providing-tool-use-examples). |

For the full set of optional properties available on any single tool definition, including `cache_control`, `strict`, `defer_loading`, and `allowed_callers`, see the [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#tool-definition-properties). A client toolset entry accepts `cache_control` and `allowed_callers` on the entry and sets `defer_loading` per member; see [Client toolsets](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets).

<Accordion title="Example simple tool definition">
  ```json JSON
  {
    "name": "get_weather",
    "description": "Get the current weather in a given location",
    "input_schema": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "The city and state, e.g. San Francisco, CA"
        },
        "unit": {
          "type": "string",
          "enum": ["celsius", "fahrenheit"],
          "description": "The unit of temperature, either 'celsius' or 'fahrenheit'"
        }
      },
      "required": ["location"]
    }
  }

text wrap
In this environment you have access to a set of tools you can use to answer the user's question.
{{ FORMATTING INSTRUCTIONS }}
String and scalar parameters should be specified as is, while lists and objects should use JSON format. Note that spaces for string values are not stripped. The output is not expected to be valid XML and is parsed with regular expressions.
Here are the functions available in JSONSchema format:
{{ TOOL DEFINITIONS IN JSON SCHEMA }}
{{ USER SYSTEM PROMPT }}
{{ TOOL CONFIGURATION }}

json JSON
    {
      "name": "get_stock_price",
      "description": "Retrieves the current stock price for a given ticker symbol. The ticker symbol must be a valid symbol for a publicly traded company on a major US stock exchange like NYSE or NASDAQ. The tool will return the latest trade price in USD. It should be used when the user asks about the current or most recent price of a specific stock. It will not provide any other information about the stock or company.",
      "input_schema": {
        "type": "object",
        "properties": {
          "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
          }
        },
        "required": ["ticker"]
      }
    }

json JSON
    {
      "name": "get_stock_price",
      "description": "Gets the stock price for a ticker.",
      "input_schema": {
        "type": "object",
        "properties": {
          "ticker": {
            "type": "string"
          }
        },
        "required": ["ticker"]
      }
    }
    ```
  </Accordion>
</AccordionGroup>

The good description clearly explains what the tool does, when to use it, what data it returns, and what the `ticker` parameter means. The poor description is too brief and leaves Claude with many open questions about the tool's behavior and usage.

<Tip>
  For deeper guidance on tool design (consolidation, naming, and response shaping), see [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents).
</Tip>


## Providing tool use examples

Source: https://platform.claude.com/llms-full.txt#providing-tool-use-examples

You can provide concrete examples of valid tool inputs to help Claude understand how to use your tools more effectively. This is particularly useful for complex tools with nested objects, optional parameters, or format-sensitive inputs.

### Basic usage

Add an optional `input_examples` field to your tool definition with an array of example input objects. Each example must be valid according to the tool's `input_schema`:

<CodeGroup>
  ```bash cURL
  curl -sS https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d @- <<'EOF'
  {
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "tools": [
      {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "description": "The unit of temperature"
            }
          },
          "required": ["location"]
        },
        "input_examples": [
          {"location": "San Francisco, CA", "unit": "fahrenheit"},
          {"location": "Tokyo, Japan", "unit": "celsius"},
          {"location": "New York, NY"}
        ]
      }
    ],
    "messages": [
      {"role": "user", "content": "What's the weather like in San Francisco?"}
    ]
  }
  EOF

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tools:
    - name: get_weather
      description: Get the current weather in a given location
      input_schema:
        type: object
        properties:
          location:
            type: string
            description: The city and state, e.g. San Francisco, CA
          unit:
            type: string
            enum: [celsius, fahrenheit]
            description: The unit of temperature
        required: [location]
      input_examples:
        - location: San Francisco, CA
          unit: fahrenheit
        - location: Tokyo, Japan
          unit: celsius
        - location: New York, NY  # 'unit' is optional
  messages:
    - role: user
      content: What's the weather like in San Francisco?
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[
          {
              "name": "get_weather",
              "description": "Get the current weather in a given location",
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
                          "description": "The unit of temperature",
                      },
                  },
                  "required": ["location"],
              },
              "input_examples": [
                  {"location": "San Francisco, CA", "unit": "fahrenheit"},
                  {"location": "Tokyo, Japan", "unit": "celsius"},
                  {
                      "location": "New York, NY"  # 'unit' is optional
                  },
              ],
          }
      ],
      messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}],
  )

  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        name: "get_weather",
        description: "Get the current weather in a given location",
        input_schema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA"
            },
            unit: {
              type: "string",
              enum: ["celsius", "fahrenheit"],
              description: "The unit of temperature"
            }
          },
          required: ["location"]
        },
        input_examples: [
          {
            location: "San Francisco, CA",
            unit: "fahrenheit"
          },
          {
            location: "Tokyo, Japan",
            unit: "celsius"
          },
          {
            location: "New York, NY"
            // Demonstrates that 'unit' is optional
          }
        ]
      }
    ],
    messages: [{ role: "user", content: "What's the weather like in San Francisco?" }]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = [
          new ToolUnion(new Tool()
          {
              Name = "get_weather",
              Description = "Get the current weather in a given location",
              InputSchema = new InputSchema()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["location"] = JsonSerializer.SerializeToElement(new { type = "string", description = "The city and state, e.g. San Francisco, CA" }),
                      ["unit"] = JsonSerializer.SerializeToElement(new { type = "string", @enum = new[] { "celsius", "fahrenheit" }, description = "The unit of temperature" }),
                  },
                  Required = ["location"],
              },
              InputExamples =
              [
                  new Dictionary<string, JsonElement>()
                  {
                      { "location", JsonSerializer.SerializeToElement("San Francisco, CA") },
                      { "unit", JsonSerializer.SerializeToElement("fahrenheit") },
                  },
                  new Dictionary<string, JsonElement>()
                  {
                      { "location", JsonSerializer.SerializeToElement("Tokyo, Japan") },
                      { "unit", JsonSerializer.SerializeToElement("celsius") },
                  },
                  new Dictionary<string, JsonElement>()
                  {
                      { "location", JsonSerializer.SerializeToElement("New York, NY") },
                  },
              ],
          }),
      ],
      Messages = [
          new() { Role = Role.User, Content = "What's the weather like in San Francisco?" }
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{
  		{OfTool: &anthropic.ToolParam{
  			Name:        "get_weather",
  			Description: anthropic.String("Get the current weather in a given location"),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"location": map[string]any{
  						"type":        "string",
  						"description": "The city and state, e.g. San Francisco, CA",
  					},
  					"unit": map[string]any{
  						"type":        "string",
  						"enum":        []string{"celsius", "fahrenheit"},
  						"description": "The unit of temperature",
  					},
  				},
  				Required: []string{"location"},
  			},
  			InputExamples: []map[string]any{
  				{
  					"location": "San Francisco, CA",
  					"unit":     "fahrenheit",
  				},
  				{
  					"location": "Tokyo, Japan",
  					"unit":     "celsius",
  				},
  				{
  					"location": "New York, NY",
  					// Demonstrates that 'unit' is optional
  				},
  			},
  		}},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather like in San Francisco?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  import com.anthropic.models.messages.Tool;
  import com.anthropic.models.messages.Tool.InputSchema;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addTool(Tool.builder()
              .name("get_weather")
              .description("Get the current weather in a given location")
              .inputSchema(InputSchema.builder()
                  .properties(JsonValue.from(Map.of(
                      "location", Map.of(
                          "type", "string",
                          "description", "The city and state, e.g. San Francisco, CA"
                      ),
                      "unit", Map.of(
                          "type", "string",
                          "enum", List.of("celsius", "fahrenheit"),
                          "description", "The unit of temperature"
                      )
                  )))
                  .required(List.of("location"))
                  .build())
              .putAdditionalProperty("input_examples", JsonValue.from(List.of(
                  Map.of(
                      "location", "San Francisco, CA",
                      "unit", "fahrenheit"
                  ),
                  Map.of(
                      "location", "Tokyo, Japan",
                      "unit", "celsius"
                  ),
                  Map.of(
                      "location", "New York, NY"
                  )
              )))
              .build())
          .addUserMessage("What's the weather like in San Francisco?")
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

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
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'location' => [
                          'type' => 'string',
                          'description' => 'The city and state, e.g. San Francisco, CA'
                      ],
                      'unit' => [
                          'type' => 'string',
                          'enum' => ['celsius', 'fahrenheit'],
                          'description' => 'The unit of temperature'
                      ]
                  ],
                  'required' => ['location']
              ],
              'input_examples' => [
                  [
                      'location' => 'San Francisco, CA',
                      'unit' => 'fahrenheit'
                  ],
                  [
                      'location' => 'Tokyo, Japan',
                      'unit' => 'celsius'
                  ],
                  [
                      'location' => 'New York, NY'
                  ]
              ]
          ]
      ],
  );

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        name: "get_weather",
        description: "Get the current weather in a given location",
        input_schema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA"
            },
            unit: {
              type: "string",
              enum: ["celsius", "fahrenheit"],
              description: "The unit of temperature"
            }
          },
          required: ["location"]
        },
        input_examples: [
          {
            location: "San Francisco, CA",
            unit: "fahrenheit"
          },
          {
            location: "Tokyo, Japan",
            unit: "celsius"
          },
          {
            location: "New York, NY"
          }
        ]
      }
    ],
    messages: [
      { role: "user", content: "What's the weather like in San Francisco?" }
    ]
  )
  puts message
  ```
</CodeGroup>

Examples are included in the prompt alongside your tool schema, showing Claude concrete patterns for well-formed tool calls. This helps Claude understand when to include optional parameters, what formats to use, and how to structure complex inputs.

### Requirements and limitations

* **Schema validation** - Each example must be valid according to the tool's `input_schema`. Invalid examples return a 400 error
* **Not supported for server-side tools or client toolsets** - Input examples work on user-defined and Anthropic-schema client tools other than the [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) toolsets, but not on server tools such as web search or code execution
* **Token cost** - Examples add to prompt tokens: \~20–50 tokens for simple examples, \~100–200 tokens for complex nested objects


## Controlling Claude's output

Source: https://platform.claude.com/llms-full.txt#controlling-claude-s-output

### Forcing tool use

In some cases, you may want Claude to use a specific tool to answer the user's question, even if Claude would otherwise answer directly without calling a tool. You can do this by specifying the tool in the `tool_choice` field of the request.

Not every model and setting supports forced tool use. Where it isn't supported, `tool_choice: {"type": "any"}` and `tool_choice: {"type": "tool", "name": "..."}` fail, while `tool_choice: {"type": "auto"}` (the default) and `tool_choice: {"type": "none"}` still work:

| Model or setting                                                                                                                    | Restriction                                                                                                         | What to use instead                                                                                                                                                                                                                                                                                                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Manual [extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) (`thinking: {type: "enabled"}`) | `any` and `tool` are not supported and result in an error                                                           | `auto` or `none`. [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking), including on models where thinking is on by default such as Claude Opus 5, supports forced tool use                                                                                                                                                                         |
| Claude Fable 5.1 and [Claude Mythos 5.1](https://anthropic.com/glasswing)                                                           | `any` and `tool` return a [400 error](https://platform.claude.com/docs/en/api/errors#forced-tool-use-not-supported) | `auto` with [strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) to guarantee schema-valid tool inputs, or [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) when you need a response in a fixed JSON shape. Prompting still influences which tool `auto` picks. `none` is also supported |

On models that support it, the highlighted lines are the only difference from a standard tool use request:

<CodeGroup>
  ```bash cURL
  curl -sS https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d @- <<'EOF'
  {
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "tools": [
      {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            }
          },
          "required": ["location"]
        }
      }
    ],
    "tool_choice": {"type": "tool", "name": "get_weather"},
    "messages": [
      {"role": "user", "content": "What's the weather like in San Francisco?"}
    ]
  }
  EOF

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tools:
    - name: get_weather
      description: Get the current weather in a given location
      input_schema:
        type: object
        properties:
          location:
            type: string
            description: The city and state, e.g. San Francisco, CA
        required: [location]
  tool_choice:
    type: tool
    name: get_weather
  messages:
    - role: user
      content: What's the weather like in San Francisco?
  YAML

python Python
  client = anthropic.Anthropic()

  tools = [
      {
          "name": "get_weather",
          "description": "Get the current weather in a given location",
          "input_schema": {
              "type": "object",
              "properties": {
                  "location": {
                      "type": "string",
                      "description": "The city and state, e.g. San Francisco, CA",
                  }
              },
              "required": ["location"],
          },
      }
  ]

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=tools,
      tool_choice={"type": "tool", "name": "get_weather"},
      messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}],
  )

  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        name: "get_weather",
        description: "Get the current weather in a given location",
        input_schema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA"
            }
          },
          required: ["location"]
        }
      }
    ],
    tool_choice: { type: "tool", name: "get_weather" },
    messages: [{ role: "user", content: "What's the weather like in San Francisco?" }]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = [
          new ToolUnion(new Tool()
          {
              Name = "get_weather",
              Description = "Get the current weather in a given location",
              InputSchema = new InputSchema()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["location"] = JsonSerializer.SerializeToElement(new { type = "string", description = "The city and state, e.g. San Francisco, CA" }),
                  },
                  Required = ["location"],
              },
          }),
      ],
      ToolChoice = new ToolChoiceTool { Name = "get_weather" },
      Messages = [
          new() { Role = Role.User, Content = "What's the weather like in San Francisco?" }
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{
  		{OfTool: &anthropic.ToolParam{
  			Name:        "get_weather",
  			Description: anthropic.String("Get the current weather in a given location"),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"location": map[string]any{
  						"type":        "string",
  						"description": "The city and state, e.g. San Francisco, CA",
  					},
  				},
  				Required: []string{"location"},
  			},
  		}},
  	},
  	ToolChoice: anthropic.ToolChoiceUnionParam{OfTool: &anthropic.ToolChoiceToolParam{Name: "get_weather"}},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather like in San Francisco?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  import com.anthropic.models.messages.Tool;
  import com.anthropic.models.messages.Tool.InputSchema;
  import com.anthropic.models.messages.ToolChoice;
  import com.anthropic.models.messages.ToolChoiceTool;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addTool(Tool.builder()
              .name("get_weather")
              .description("Get the current weather in a given location")
              .inputSchema(InputSchema.builder()
                  .properties(JsonValue.from(Map.of(
                      "location", Map.of(
                          "type", "string",
                          "description", "The city and state, e.g. San Francisco, CA"
                      )
                  )))
                  .required(List.of("location"))
                  .build())
              .build())
          .toolChoice(ToolChoice.ofTool(ToolChoiceTool.builder()
              .name("get_weather")
              .build()))
          .addUserMessage("What's the weather like in San Francisco?")
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => "What's the weather like in San Francisco?"]
      ],
      model: 'claude-opus-5',
      toolChoice: ['type' => 'tool', 'name' => 'get_weather'],
      tools: [
          [
              'name' => 'get_weather',
              'description' => 'Get the current weather in a given location',
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'location' => [
                          'type' => 'string',
                          'description' => 'The city and state, e.g. San Francisco, CA'
                      ]
                  ],
                  'required' => ['location']
              ]
          ]
      ],
  );

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        name: "get_weather",
        description: "Get the current weather in a given location",
        input_schema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA"
            }
          },
          required: ["location"]
        }
      }
    ],
    tool_choice: { type: "tool", name: "get_weather" },
    messages: [
      { role: "user", content: "What's the weather like in San Francisco?" }
    ]
  )
  puts message

json JSON
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "I'll help you check the current weather and time in San Francisco."
    },
    {
      "type": "tool_use",
      "id": "toolu_01A09q90qw90lq917835lq9",
      "name": "get_weather",
      "input": { "location": "San Francisco, CA" }
    }
  ]
}
```

This natural response style helps users understand what Claude is doing and creates a more conversational interaction. You can guide the style and content of these responses through your system prompts and by providing `<examples>` in your prompts.

It's important to note that Claude may use various phrasings and approaches when explaining its actions. Your code should treat these responses like any other assistant-generated text, and not rely on specific formatting conventions.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-29

<CardGroup>
  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls" title="Handle tool calls">
    Parse tool\_use blocks and format tool\_result responses.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner" title="Tool Runner (SDK)">
    Let the SDK handle the agentic loop automatically.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference" title="Tool reference">
    Directory of Anthropic-provided tools and optional properties.
  </Card>
</CardGroup>


---
title: Handle tool calls
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls
description: Parse tool_use blocks, format tool_result responses, and handle errors with is_error.
---

This page covers the tool-call lifecycle: reading `tool_use` blocks from Claude's response, formatting `tool_result` blocks in your reply, and signaling errors. For the SDK abstraction that handles this automatically, see [Tool Runner](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner).

<Note>
  **Simpler with Tool Runner:** The manual tool handling described on this page is automatically managed by [Tool Runner](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner). Use this page when you need custom control over tool execution.
</Note>

Claude's response differs based on whether it uses a [client or server tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview#how-tool-use-works).


## Handling results from client tools

Source: https://platform.claude.com/llms-full.txt#handling-results-from-client-tools

The response will have a `stop_reason` of `tool_use` and one or more `tool_use` content blocks that include:

* `id`: A unique identifier for this particular tool use block. This will be used to match up the tool results later.
* `name`: The name of the tool being used.
* `input`: An object containing the input being passed to the tool, conforming to the tool's `input_schema`.

A `tool_use` block for a member of the [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) or [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) toolset also carries a `toolset_name` field (`"computer"` or `"browser"`). Its `name` is the member tool Claude is calling, such as `screenshot` or `navigate`, so dispatch those blocks on both fields.

<Accordion title="Example API response with a `tool_use` content block">
  ```json JSON
  {
    "id": "msg_01Aq9w938a90dw8q",
    "model": "claude-opus-5",
    "stop_reason": "tool_use",
    "role": "assistant",
    "content": [
      {
        "type": "text",
        "text": "I'll check the current weather in San Francisco for you."
      },
      {
        "type": "tool_use",
        "id": "toolu_01A09q90qw90lq917835lq9",
        "name": "get_weather",
        "input": { "location": "San Francisco, CA", "unit": "celsius" }
      }
    ]
  }

json
  {
    "role": "user",
    "content": [
      { "type": "text", "text": "Here are the results:" }, // ❌ Text before tool_result
      { "type": "tool_result", "tool_use_id": "toolu_01" /* ... */ }
    ]
  }

json
  {
    "role": "user",
    "content": [
      { "type": "tool_result", "tool_use_id": "toolu_01" /* ... */ },
      { "type": "text", "text": "What should I do next?" } // ✅ Text after tool_result
    ]
  }

json JSON
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
          "content": "15 degrees"
        }
      ]
    }

json JSON
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
          "content": [
            { "type": "text", "text": "15 degrees" },
            {
              "type": "image",
              "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": "/9j/4AAQSkZJRg..."
              }
            }
          ]
        }
      ]
    }

json JSON
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9"
        }
      ]
    }

json JSON
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
          "content": [
            { "type": "text", "text": "The weather is" },
            {
              "type": "document",
              "source": {
                "type": "text",
                "media_type": "text/plain",
                "data": "15 degrees"
              }
            }
          ]
        }
      ]
    }
    ```
  </Accordion>
</AccordionGroup>

After receiving the tool result, Claude will use that information to continue generating a response to the original user prompt.


## Handling results from server tools

Source: https://platform.claude.com/llms-full.txt#handling-results-from-server-tools

Claude executes the tool internally and incorporates the results directly into its response without requiring additional user interaction.

<Note>
  A response can contain both a client `tool_use` block and a `server_tool_use` block that has no result block. That server tool call is not finished yet, and its result block arrives in a later response. Reply with a user message that contains only the `tool_result` blocks for the client tools and keep the same `tools` array; for a server tool Claude called directly, the API runs it on that request and the next response starts with its result block. See [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#tool-use).
</Note>

<Tip>
  **Differences from other APIs**

  Unlike APIs that separate tool use or use special roles like `tool` or `function`, the Claude API integrates tools directly into the `user` and `assistant` message structure.

  Messages contain arrays of `text`, `image`, `tool_use`, and `tool_result` blocks. `user` messages include client content and `tool_result`, while `assistant` messages contain AI-generated content and `tool_use`.
</Tip>


## Handling errors with is\_error

Source: https://platform.claude.com/llms-full.txt#handling-errors-with-is-error

There are a few different types of errors that can occur when using tools with Claude:

<AccordionGroup>
  <Accordion title="Tool execution error">
    If the tool itself throws an error during execution (for example, a network error when fetching weather data), you can return the error message in the `content` along with `"is_error": true`:

    ```json JSON
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
          "content": "ConnectionError: the weather service API is not available (HTTP 500)",
          "is_error": true
        }
      ]
    }

json JSON
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
          "content": "Error: Missing required 'location' parameter",
          "is_error": true
        }
      ]
    }
    ```

    If a tool request is invalid or missing parameters, Claude will retry 2-3 times with corrections before apologizing to the user.

    <Tip>
      To eliminate invalid tool calls entirely, use [strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) with `strict: true` on your tool definitions. This guarantees that tool inputs will always match your schema exactly, preventing missing parameters and type mismatches.
    </Tip>
  </Accordion>

  <Accordion title="Server tool errors">
    When server tools encounter errors (for example, network issues with Web Search), Claude will transparently handle these errors and attempt to provide an alternative response or explanation to the user. Unlike client tools, you do not need to handle `is_error` results for server tools.

    For web search specifically, possible error codes include:

    * `too_many_requests`: Rate limit exceeded
    * `invalid_input`: Invalid search query parameter
    * `max_uses_exceeded`: Maximum web search tool uses exceeded
    * `query_too_long`: Query exceeds maximum length
    * `unavailable`: An internal error occurred
  </Accordion>
</AccordionGroup>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-30

<CardGroup cols={3}>
  <Card title="Parallel tool use" icon="grid" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use">
    Handle responses where Claude calls several tools in a single turn.
  </Card>

  <Card title="Tool Runner (SDK)" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner">
    Let the SDK manage the `tool_use` loop, result formatting, and retries for you.
  </Card>

  <Card title="Define tools" icon="hammer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools">
    Write schemas and descriptions that steer Claude toward the right tool.
  </Card>
</CardGroup>


---
title: How tool use works
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works
description: Understand the tool use loop, where tools execute, and when to use tools instead of prose.
---

This page explains the concepts behind tool use: where tools run, how the agentic loop works, and when tool use is the right approach. For hands-on guidance, start with the [Build a tool-using agent](https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent) tutorial or the [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) guide.


## The tool-use contract

Source: https://platform.claude.com/llms-full.txt#the-tool-use-contract

Tool use is a contract between your application and the model. You specify what operations are available and what shape their inputs and outputs take; Claude determines when and how to call them. The model never executes anything on its own. It emits a structured request, your code (or Anthropic's servers) runs the operation, and the result flows back into the conversation.

This contract makes the model behave less like a text generator and more like a function you call. Engineers with classical API experience can integrate tool use the same way they would any other typed interface: define the schema, handle the callback, return a result. The difference is that the caller on the other side is a language model choosing which function to call based on the conversation.


## Where tools run

Source: https://platform.claude.com/llms-full.txt#where-tools-run

The primary axis along which tools differ is where the code executes. Every tool falls into one of three buckets, and the bucket determines what your application is responsible for.

### User-defined tools (client-executed)

You write the schema, you execute the code, you return the results. This is the most common case: the vast majority of tool-use traffic is [user-defined tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) calling into application-specific logic.

When Claude calls one of your tools, the API response contains a `tool_use` block with the tool name and a JSON object of arguments. Your application extracts those arguments, runs the operation (a database query, an HTTP call, a file write, whatever the tool does), and sends the output back in a `tool_result` block on the next request. Claude never sees your implementation; it only sees the schema you provided and the result you returned.

### Anthropic-schema tools (client-executed)

For a handful of common operations (managing scratchpad memory, running shell commands, editing files, controlling a desktop or a browser), Anthropic publishes the tool schema and your application handles execution. The tools in this category are [`memory`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool), [`bash`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool), [`text_editor`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool), [`computer`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool), and [`browser`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool).

The execution model is identical to user-defined tools: the response contains a `tool_use` block, your code runs the operation, and you send back a `tool_result`. The reason to use an Anthropic-schema tool instead of defining your own equivalent is that these schemas are trained-in. Claude has been optimized on thousands of successful trajectories that use these exact tool signatures, so it calls them more reliably and recovers from errors more gracefully than it would with a custom tool that does the same thing. The schema is the interface the model already expects.

### Server-executed tools

For [`web_search`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool), [`web_fetch`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool), [`code_execution`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool), and [`tool_search`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool), Anthropic runs the code. You enable the tool in your request and the server handles everything else. You never construct a `tool_result` block for these tools. When a turn calls only [server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools), the server-side loop executes the operation and feeds the output back to the model before the response reaches you, unless the loop stops before it finishes, most often because it pauses.

The response you receive contains `server_tool_use` blocks showing what ran and what came back. In the common case, execution is already complete by the time you see them, and your application's job is to enable the tool and read the final answer rather than to participate in the execution loop; the main exceptions are a paused loop ([`pause_turn`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works#the-server-side-loop)) and a turn that also calls a client tool.


## The agentic loop (client tools)

Source: https://platform.claude.com/llms-full.txt#the-agentic-loop-client-tools

Client-executed tools (both user-defined and Anthropic-schema) require your application to drive a loop. The model can't run your code, so every tool call is a round trip: the model asks, you execute, you report back, the model continues.

The canonical shape is a `while` loop keyed on `stop_reason`:

1. Send a request with your `tools` array and the user message.
2. Claude responds with `stop_reason: "tool_use"` and one or more `tool_use` blocks.
3. Execute each tool. Format the outputs as `tool_result` blocks.
4. Send a new request containing the original messages, the assistant's response, and a user message with the `tool_result` blocks.
5. Repeat from step 2 while `stop_reason` is `"tool_use"`.

In practice this reads as: while `stop_reason == "tool_use"`, execute the tools and continue the conversation. The loop exits on any other stop reason (`"end_turn"`, `"max_tokens"`, `"stop_sequence"`, or `"refusal"`), which means Claude has either produced a final answer or stopped for another reason that your application should handle.

For the mechanics of building requests, handling parallel tool calls, and formatting results, see [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls).


## The server-side loop

Source: https://platform.claude.com/llms-full.txt#the-server-side-loop

Server-executed tools run their own loop inside Anthropic's infrastructure. A single request from your application might trigger several web searches or code executions before a response comes back. The model searches, reads results, determines whether to search again, and iterates until it has what it needs, all without your application participating.

This internal loop has an iteration limit. If the model is still iterating when it hits the cap, the response comes back with `stop_reason: "pause_turn"` instead of `"end_turn"`. A paused turn means the work isn't finished; re-send the conversation (including the paused response) to let the model continue where it left off. See [Server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools) for the continuation pattern.

The loop also hands control back to you before a server tool runs if Claude calls that server tool and a client tool in the same group of parallel tool calls. The response then comes back with `stop_reason: "tool_use"` and a `server_tool_use` block that has no result block yet; the API runs it after you return the client tool results. See [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#tool-use) for the exact contract.


## When to use tools (and when not to)

Source: https://platform.claude.com/llms-full.txt#when-to-use-tools-and-when-not-to

Tool use fits when the task requires something the model can't do from text alone:

* **Actions with side effects.** Sending an email, writing a file, updating a record. The model can describe these actions, but only a tool can perform them.
* **Fresh or external data.** Current prices, today's weather, the contents of a database. Anything outside the training data or specific to your system needs a tool to fetch it.
* **Structured, guaranteed-shape outputs.** When you need a JSON object with specific fields rather than prose that happens to contain the information, a tool schema enforces the shape.
* **Calling into existing systems.** Databases, internal APIs, filesystems. Tool use is the bridge between natural-language requests and the systems that fulfill them.

A clear sign that you should be using tools: if you're writing a regex to extract a decision from model output, that decision should have been a tool call. Parsing free-form text to recover structured intent is a sign the structure belongs in the schema.

Tool use doesn't fit when:

* The model can answer from training alone. Summarization, translation, and general-knowledge questions don't need a tool round trip.
* The interaction is one-shot Q\&A with no side effects. If there's nothing to execute, there's nothing for a tool to do.
* Tool-calling latency would dominate a trivial response. Every tool call is at least one extra round trip; for lightweight tasks the overhead can exceed the work.


## Choosing between approaches

Source: https://platform.claude.com/llms-full.txt#choosing-between-approaches

| Approach                      | When to use it                                                            | What to expect                                                                        | Learn more                                                                                     |
| ----------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| User-defined client tools     | Custom business logic, internal APIs, proprietary data                    | You handle execution and the agentic loop                                             | [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)     |
| Anthropic-schema client tools | Standard dev operations (bash, file editing, desktop and browser control) | You handle execution; Claude calls the tool reliably because the schema is trained-in | [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference) |
| Server-executed tools         | Web search, code sandbox, web fetch                                       | Anthropic handles execution; you read the results instead of producing them           | [Server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools)     |


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-31

<CardGroup>
  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent" title="Tutorial: Build a tool-using agent">
    Build an agent step by step from a single tool call to production.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools" title="Define tools">
    Schema specification, descriptions, and `tool_choice`.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference" title="Tool reference">
    Directory of Anthropic-provided tools.
  </Card>
</CardGroup>


---
title: Memory tool
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool
description: Let Claude store and retrieve information across conversations by implementing the memory tool's file operations in your application.
---

The memory tool lets Claude store and retrieve information across conversations in a directory of memory files. Claude can create, read, update, and delete files that persist between sessions, building up knowledge over time without keeping everything in the context window.

Memory supports just-in-time context retrieval. Rather than loading all relevant information up front, an agent records what it learns in memory files and reads them back on demand. This keeps the active context focused on the current task, which matters for long-running sessions that would otherwise overwhelm the context window. See [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) for the broader pattern.

The memory tool operates client-side: Claude requests file operations, and your application executes them. You control where and how the data is stored through your own infrastructure.

<Note>
  Reach out through the [feedback form](https://forms.gle/YXC2EKGMhjN1c4L88) to share your feedback on this feature.
</Note>

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>


## Use cases

Source: https://platform.claude.com/llms-full.txt#use-cases-2

* Maintain project context across multiple agent sessions
* Apply lessons from past interactions, decisions, and feedback to new tasks
* Build up a knowledge base over time


## How it works

Source: https://platform.claude.com/llms-full.txt#how-it-works-4

When the memory tool is enabled, Claude automatically checks its memory directory before starting a task. As it works, Claude stores what it learns in files under `/memories` and reads them back in later conversations to continue earlier work.

Because the memory tool is client-side, Claude only requests memory operations. Your application executes each request against storage you control and returns the result in a `tool_result` block (see [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)). The `/memories` path is a prefix that your handler maps onto real storage, such as a per-user directory or keys in a database. Memory lives entirely in your application. A later conversation continues from the same memory when it sends the same `tools` entry and your handler serves the same store. For security, restrict all memory operations to the `/memories` directory (see [Path traversal protection](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool#path-traversal-protection)).

### Example: How memory tool calls work

A typical interaction looks like this:

**1. User request:**

```text wrap
"Help me respond to this customer service ticket."

text wrap
"I'll help you respond to the customer service ticket. Let me check my memory for any previous context."

json
{
  "type": "tool_use",
  "id": "toolu_01C4D5E6F7G8H9I0J1K2L3M4",
  "name": "memory",
  "input": {
    "command": "view",
    "path": "/memories"
  }
}

json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01C4D5E6F7G8H9I0J1K2L3M4",
  "content": "Here're the files and directories up to 2 levels deep in /memories, excluding hidden items and node_modules:\n4.0K\t/memories\n1.5K\t/memories/customer_service_guidelines.xml\n2.0K\t/memories/refund_policies.xml"
}

json
{
  "type": "tool_use",
  "id": "toolu_01D5E6F7G8H9I0J1K2L3M4N5",
  "name": "memory",
  "input": {
    "command": "view",
    "path": "/memories/customer_service_guidelines.xml"
  }
}

json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01D5E6F7G8H9I0J1K2L3M4N5",
  "content": "Here's the content of /memories/customer_service_guidelines.xml with line numbers:\n     1\t<guidelines>\n     2\t<addressing_customers>\n     3\t- Always address customers by their first name\n     4\t- Use empathetic language\n..."
}

text wrap
"Based on your customer service guidelines, I can help you craft a response. Please share the ticket details..."
```

The memory tool is available on all Claude 4 and later models. For the full list of Anthropic-provided tools, see the [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference).


## Getting started

Source: https://platform.claude.com/llms-full.txt#getting-started

Using the memory tool takes two steps:

1. Add the memory tool to your request. The `tools` entry `{"type": "memory_20250818", "name": "memory"}` is the entire configuration: the `name` must be `memory`, and you don't define an input schema for an Anthropic-provided tool.
2. Implement a client-side handler for each memory command. Your handler must reject paths outside `/memories`, so read [Path traversal protection](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool#path-traversal-protection) before you write it.


## Basic usage

Source: https://platform.claude.com/llms-full.txt#basic-usage-2

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
          "content": "Help me respond to this customer service ticket."
        }
      ],
      "tools": [{
        "type": "memory_20250818",
        "name": "memory"
      }]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 2048
  tools:
    - type: memory_20250818
      name: memory
  messages:
    - role: user
      content: Help me respond to this customer service ticket.
  YAML

python Python
  client = anthropic.Anthropic()

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=2048,
      messages=[
          {
              "role": "user",
              "content": "Help me respond to this customer service ticket.",
          }
      ],
      tools=[{"type": "memory_20250818", "name": "memory"}],
  )

  print(message)

typescript TypeScript
  const anthropic = new Anthropic();

  const message = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 2048,
    messages: [
      {
        role: "user",
        content: "Help me respond to this customer service ticket."
      }
    ],
    tools: [{ type: "memory_20250818", name: "memory" }]
  });

  console.log(message);

csharp C#
  var client = new AnthropicClient();

  var message = await client.Messages.Create(
      new()
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 2048,
          Messages =
          [
              new()
              {
                  Role = Role.User,
                  Content = "Help me respond to this customer service ticket.",
              },
          ],
          Tools = [new MemoryTool20250818()],
      }
  );

  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 2048,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Help me respond to this customer service ticket.")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfMemoryTool20250818: &anthropic.MemoryTool20250818Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(message)

java Java
  import com.anthropic.models.messages.MemoryTool20250818;
  // ...
    AnthropicClient client = AnthropicOkHttpClient.fromEnv();

    MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(2048L)
      .addTool(MemoryTool20250818.builder().build())
      .addUserMessage("Help me respond to this customer service ticket.")
      .build();

    Message message = client.messages().create(params);
    IO.println(message);

php PHP
  $client = new Client();

  $message = $client->messages->create(
      model: Model::CLAUDE_OPUS_5,
      maxTokens: 2048,
      messages: [
          [
              'role' => 'user',
              'content' => 'Help me respond to this customer service ticket.',
          ],
      ],
      tools: [new MemoryTool20250818],
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: Anthropic::Model::CLAUDE_OPUS_5,
    max_tokens: 2048,
    messages: [
      {
        role: "user",
        content: "Help me respond to this customer service ticket."
      }
    ],
    tools: [
      {
        type: "memory_20250818",
        name: "memory"
      }
    ]
  )
  puts message
  ```
</CodeGroup>


## Implement the memory handler

Source: https://platform.claude.com/llms-full.txt#implement-the-memory-handler

Claude's reply to a request like the previous one ends with a `tool_use` block that requests a memory operation, such as `view /memories`. Your application executes the operation and returns the result in a `tool_result` block, then sends the conversation back so Claude can continue: the standard [tool-use loop](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls).

Four SDKs provide memory tool helpers that handle the tool interface and the loop. Subclass `BetaAbstractMemoryTool` (Python and C#), use `betaMemoryTool` (TypeScript), or implement `BetaMemoryToolHandler` (Java) to back memory with your own storage, such as files on disk, a database, cloud storage, or encrypted files. Python and TypeScript also ship a ready-made local-filesystem implementation, `BetaLocalFilesystemMemoryTool`. The helper and tool-runner surfaces live in each SDK's beta namespace even though the memory tool itself doesn't require a beta header. The Go and Ruby SDKs have no memory helper, so those examples run the tool-use loop themselves, and PHP wraps your handler closure in its generic `BetaRunnableTool`. All three use an in-memory store that you replace with your own storage.

<CodeGroup exclude="shell">
  ```python Python
  import anthropic
  from anthropic.tools import BetaLocalFilesystemMemoryTool

  client = anthropic.Anthropic()
  memory = BetaLocalFilesystemMemoryTool(base_path="./memory")

  runner = client.beta.messages.tool_runner(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": "Remember that customer Acme Corp prefers email follow-ups.",
          }
      ],
      tools=[memory],
  )

  final_message = runner.until_done()
  print(final_message.content)

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";
  import { betaMemoryTool } from "@anthropic-ai/sdk/helpers/beta/memory";
  import { BetaLocalFilesystemMemoryTool } from "@anthropic-ai/sdk/tools/memory/node";

  const client = new Anthropic();

  const backend = await BetaLocalFilesystemMemoryTool.init("./memory");
  const memory = betaMemoryTool(backend); // or pass your own handlers object

  const runner = client.beta.messages.toolRunner({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: "Remember that customer Acme Corp prefers email follow-ups."
      }
    ],
    tools: [memory],
    max_iterations: 10
  });

  const finalMessage = await runner;
  console.log(finalMessage.content);

csharp C#
  using Anthropic;
  using Anthropic.Helpers.Beta;
  using Anthropic.Models.Beta.Messages;

  var client = new AnthropicClient();

  // Your subclass of BetaAbstractMemoryTool
  var memory = new FilesystemMemoryTool("./memories");

  var runner = client.Beta.Messages.ToolRunner(
      new MessageCreateParams
      {
          Model = Anthropic.Models.Messages.Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages =
          [
              new()
              {
                  Role = Role.User,
                  Content = "Remember that customer Acme Corp prefers email follow-ups.",
              },
          ],
      },
      [memory],
      maxIterations: 10
  );

  var finalMessage = await runner.RunUntilDoneAsync();
  Console.WriteLine(finalMessage);

go Go
  package main

  import (
  	"context"
  	"encoding/json"
  	"fmt"
  	"log"
  	"slices"
  	"sort"
  	"strings"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  // An in-memory store that maps memory file paths to their contents.
  // Use your own storage in production.
  var store = map[string]string{}

  type memoryCommand struct {
  	Command    string `json:"command"`
  	Path       string `json:"path"`
  	FileText   string `json:"file_text"`
  	OldStr     string `json:"old_str"`
  	NewStr     string `json:"new_str"`
  	InsertLine int    `json:"insert_line"`
  	InsertText string `json:"insert_text"`
  	OldPath    string `json:"old_path"`
  	NewPath    string `json:"new_path"`
  }

  func executeMemory(raw json.RawMessage) string {
  	var cmd memoryCommand
  	if err := json.Unmarshal(raw, &cmd); err != nil {
  		return "Error: invalid memory command"
  	}
  	switch cmd.Command {
  	case "view":
  		if content, ok := store[cmd.Path]; ok {
  			lines := strings.Split(strings.TrimSuffix(content, "\n"), "\n")
  			for i, line := range lines {
  				lines[i] = fmt.Sprintf("%6d\t%s", i+1, line)
  			}
  			return fmt.Sprintf("Here's the content of %s with line numbers:\n%s", cmd.Path, strings.Join(lines, "\n"))
  		}
  		if cmd.Path == "/memories" {
  			listing := []string{"1.0K\t/memories"}
  			for path := range store {
  				listing = append(listing, "1.0K\t"+path)
  			}
  			sort.Strings(listing[1:])
  			return fmt.Sprintf("Here're the files and directories up to 2 levels deep in %s, excluding hidden items and node_modules:\n%s", cmd.Path, strings.Join(listing, "\n"))
  		}
  		return fmt.Sprintf("The path %s does not exist. Please provide a valid path.", cmd.Path)
  	case "create":
  		store[cmd.Path] = cmd.FileText
  		return "File created successfully at: " + cmd.Path
  	case "str_replace":
  		content, ok := store[cmd.Path]
  		if !ok || !strings.Contains(content, cmd.OldStr) {
  			return fmt.Sprintf("No replacement was performed, old_str `%s` did not appear verbatim in %s.", cmd.OldStr, cmd.Path)
  		}
  		store[cmd.Path] = strings.Replace(content, cmd.OldStr, cmd.NewStr, 1)
  		return "The memory file has been edited."
  	case "insert":
  		content, ok := store[cmd.Path]
  		if !ok {
  			return fmt.Sprintf("Error: The path %s does not exist", cmd.Path)
  		}
  		lines := strings.Split(content, "\n")
  		if cmd.InsertLine < 0 || cmd.InsertLine > len(lines) {
  			return fmt.Sprintf("Error: Invalid `insert_line` parameter: %d. It should be within the range of lines of the file: [0, %d]", cmd.InsertLine, len(lines))
  		}
  		lines = slices.Insert(lines, cmd.InsertLine, strings.TrimSuffix(cmd.InsertText, "\n"))
  		store[cmd.Path] = strings.Join(lines, "\n")
  		return fmt.Sprintf("The file %s has been edited.", cmd.Path)
  	case "delete":
  		if _, ok := store[cmd.Path]; !ok {
  			return fmt.Sprintf("Error: The path %s does not exist", cmd.Path)
  		}
  		delete(store, cmd.Path)
  		return "Successfully deleted " + cmd.Path
  	case "rename":
  		if _, ok := store[cmd.OldPath]; !ok {
  			return fmt.Sprintf("Error: The path %s does not exist", cmd.OldPath)
  		}
  		if _, ok := store[cmd.NewPath]; ok {
  			return fmt.Sprintf("Error: The destination %s already exists", cmd.NewPath)
  		}
  		store[cmd.NewPath] = store[cmd.OldPath]
  		delete(store, cmd.OldPath)
  		return fmt.Sprintf("Successfully renamed %s to %s", cmd.OldPath, cmd.NewPath)
  	default:
  		return "Error: unknown command " + cmd.Command
  	}
  }

  func main() {
  	client := anthropic.NewClient()
  	tools := []anthropic.ToolUnionParam{{OfMemoryTool20250818: &anthropic.MemoryTool20250818Param{}}}
  	messages := []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Remember that customer Acme Corp prefers email follow-ups.")),
  	}

  	for {
  		message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  			Model:     anthropic.ModelClaudeOpus5,
  			MaxTokens: 1024,
  			Messages:  messages,
  			Tools:     tools,
  		})
  		if err != nil {
  			log.Fatal(err)
  		}
  		if message.StopReason != anthropic.StopReasonToolUse {
  			for _, block := range message.Content {
  				if block.Type == "text" {
  					fmt.Println(block.Text)
  				}
  			}
  			break
  		}
  		results := []anthropic.ContentBlockParamUnion{}
  		for _, block := range message.Content {
  			if block.Type == "tool_use" {
  				results = append(results, anthropic.NewToolResultBlock(block.ID, executeMemory(block.Input), false))
  			}
  		}
  		messages = append(messages, message.ToParam(), anthropic.NewUserMessage(results...))
  	}
  }

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.helpers.BetaMemoryToolHandler;
  import com.anthropic.helpers.BetaToolRunner;
  import com.anthropic.models.beta.messages.BetaMemoryTool20250818;
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.MessageCreateParams; // beta package, not models.messages
  import com.anthropic.models.beta.messages.ToolRunnerCreateParams;
  import com.anthropic.models.messages.Model;
  import java.nio.file.Path;

  void main() {
    AnthropicClient client = AnthropicOkHttpClient.fromEnv();

    // Your BetaMemoryToolHandler implementation of the six memory commands
    BetaMemoryToolHandler handler = new FileSystemMemoryToolHandler(Path.of("memories"));

    MessageCreateParams createParams = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024L)
      .addTool(BetaMemoryTool20250818.builder().build())
      .addUserMessage("Remember that customer Acme Corp prefers email follow-ups.")
      .build();

    ToolRunnerCreateParams runnerParams = ToolRunnerCreateParams.builder()
      .betaMemoryToolHandler(handler)
      .initialMessageParams(createParams)
      .maxIterations(10)
      .build();

    BetaToolRunner runner = client.beta().messages().toolRunner(runnerParams);
    for (BetaMessage message : runner) {
      IO.println(message);
    }
  }

php PHP
  <?php

  use Anthropic\Beta\Messages\BetaMemoryTool20250818;
  use Anthropic\Client;
  use Anthropic\Lib\Tools\BetaRunnableTool;
  use Anthropic\Messages\Model;

  $client = new Client();

  // An in-memory store that maps memory file paths to their contents.
  // Use your own storage in production.
  $store = [];

  $memory = new BetaRunnableTool(
      definition: new BetaMemoryTool20250818,
      run: function (array $input) use (&$store): string {
          $path = $input['path'] ?? '';
          switch ($input['command']) {
              case 'view':
                  if (isset($store[$path])) {
                      $numbered = [];
                      foreach (explode("\n", preg_replace('/\n\z/', '', $store[$path])) as $i => $line) {
                          $numbered[] = sprintf("%6d\t%s", $i + 1, $line);
                      }
                      return "Here's the content of {$path} with line numbers:\n" . implode("\n", $numbered);
                  }
                  if ($path === '/memories') {
                      $listing = ["1.0K\t/memories"];
                      foreach (array_keys($store) as $stored) {
                          $listing[] = "1.0K\t{$stored}";
                      }
                      return "Here're the files and directories up to 2 levels deep in {$path}, excluding hidden items and node_modules:\n" . implode("\n", $listing);
                  }
                  return "The path {$path} does not exist. Please provide a valid path.";
              case 'create':
                  $store[$path] = $input['file_text'];
                  return "File created successfully at: {$path}";
              case 'str_replace':
                  $position = strpos($store[$path] ?? '', $input['old_str']);
                  if ($position === false) {
                      return "No replacement was performed, old_str `{$input['old_str']}` did not appear verbatim in {$path}.";
                  }
                  $store[$path] = substr_replace($store[$path], $input['new_str'] ?? '', $position, strlen($input['old_str']));
                  return 'The memory file has been edited.';
              case 'insert':
                  if (!isset($store[$path])) {
                      return "Error: The path {$path} does not exist";
                  }
                  $lines = explode("\n", $store[$path]);
                  if ($input['insert_line'] < 0 || $input['insert_line'] > count($lines)) {
                      return "Error: Invalid `insert_line` parameter: {$input['insert_line']}. It should be within the range of lines of the file: [0, " . count($lines) . "]";
                  }
                  array_splice($lines, $input['insert_line'], 0, [preg_replace('/\n\z/', '', $input['insert_text'])]);
                  $store[$path] = implode("\n", $lines);
                  return "The file {$path} has been edited.";
              case 'delete':
                  if (!isset($store[$path])) {
                      return "Error: The path {$path} does not exist";
                  }
                  unset($store[$path]);
                  return "Successfully deleted {$path}";
              case 'rename':
                  if (!isset($store[$input['old_path']])) {
                      return "Error: The path {$input['old_path']} does not exist";
                  }
                  if (isset($store[$input['new_path']])) {
                      return "Error: The destination {$input['new_path']} already exists";
                  }
                  $store[$input['new_path']] = $store[$input['old_path']];
                  unset($store[$input['old_path']]);
                  return "Successfully renamed {$input['old_path']} to {$input['new_path']}";
              default:
                  return "Error: unknown command {$input['command']}";
          }
      },
  );

  $runner = $client->beta->messages->toolRunner(
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Remember that customer Acme Corp prefers email follow-ups.']],
      model: Model::CLAUDE_OPUS_5,
      tools: [$memory],
      maxIterations: 10,
  );

  $finalMessage = $runner->runUntilDone();
  print_r($finalMessage->content);

ruby Ruby
  require "anthropic"

  client = Anthropic::Client.new
  TOOLS = [{type: "memory_20250818", name: "memory"}].freeze

  # An in-memory store that maps memory file paths to their contents.
  # Use your own storage in production.
  STORE = {}

  def execute_memory(input)
    path = input[:path]
    case input[:command]
    when "view"
      if STORE.key?(path)
        lines = STORE[path].chomp.split("\n", -1)
        lines = [""] if lines.empty?
        numbered = lines.each_with_index.map { |line, i| format("%6d\t%s", i + 1, line) }
        "Here's the content of #{path} with line numbers:\n#{numbered.join("\n")}"
      elsif path == "/memories"
        listing = ["1.0K\t/memories"] + STORE.keys.map { |stored| "1.0K\t#{stored}" }
        "Here're the files and directories up to 2 levels deep in #{path}, excluding hidden items and node_modules:\n#{listing.join("\n")}"
      else
        "The path #{path} does not exist. Please provide a valid path."
      end
    when "create"
      STORE[path] = input[:file_text]
      "File created successfully at: #{path}"
    when "str_replace"
      unless STORE.key?(path) && STORE[path].include?(input[:old_str])
        return "No replacement was performed, old_str `#{input[:old_str]}` did not appear verbatim in #{path}."
      end
      STORE[path] = STORE[path].sub(input[:old_str]) { input[:new_str].to_s }
      "The memory file has been edited."
    when "insert"
      return "Error: The path #{path} does not exist" unless STORE.key?(path)
      lines = STORE[path].split("\n", -1)
      lines = [""] if lines.empty?
      if input[:insert_line] < 0 || input[:insert_line] > lines.length
        return "Error: Invalid `insert_line` parameter: #{input[:insert_line]}. It should be within the range of lines of the file: [0, #{lines.length}]"
      end
      lines.insert(input[:insert_line], input[:insert_text].chomp)
      STORE[path] = lines.join("\n")
      "The file #{path} has been edited."
    when "delete"
      return "Error: The path #{path} does not exist" unless STORE.key?(path)
      STORE.delete(path)
      "Successfully deleted #{path}"
    when "rename"
      return "Error: The path #{input[:old_path]} does not exist" unless STORE.key?(input[:old_path])
      return "Error: The destination #{input[:new_path]} already exists" if STORE.key?(input[:new_path])
      STORE[input[:new_path]] = STORE.delete(input[:old_path])
      "Successfully renamed #{input[:old_path]} to #{input[:new_path]}"
    else
      "Error: unknown command #{input[:command]}"
    end
  end

  messages = [{role: "user", content: "Remember that customer Acme Corp prefers email follow-ups."}]
  loop do
    message = client.messages.create(
      model: Anthropic::Model::CLAUDE_OPUS_5,
      max_tokens: 1024,
      messages: messages,
      tools: TOOLS
    )
    unless message.stop_reason == :tool_use
      puts message.content
      break
    end
    tool_results = message.content.filter_map do |block|
      next unless block.type == :tool_use
      {type: "tool_result", tool_use_id: block.id, content: execute_memory(block.input)}
    end
    messages << {role: "assistant", content: message.content} << {role: "user", content: tool_results}
  end
  ```
</CodeGroup>

The in-memory stores in the Go, PHP, and Ruby examples keep them self-contained: each one dispatches on the `command` field in the `tool_use` block's `input` and returns the strings described under [Tool commands](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool#tool-commands). A production handler also needs the [path validation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool#path-traversal-protection) these demonstration stores skip. For the SDKs' own complete examples, see:

* Python: [examples/memory/basic.py](https://github.com/anthropics/anthropic-sdk-python/blob/main/examples/memory/basic.py)
* TypeScript: [examples/tools-helpers-memory.ts](https://github.com/anthropics/anthropic-sdk-typescript/blob/main/examples/tools-helpers-memory.ts)
* C#: [MemoryToolExample](https://github.com/anthropics/anthropic-sdk-csharp/tree/main/examples/MemoryToolExample)
* Java: [BetaMemoryToolExample.java](https://github.com/anthropics/anthropic-sdk-java/blob/main/anthropic-java-example/src/main/java/com/anthropic/example/BetaMemoryToolExample.java)


## Tool commands

Source: https://platform.claude.com/llms-full.txt#tool-commands

Your client-side implementation must handle the following commands. These specifications describe the recommended behaviors and return strings: Claude reads whatever text your tool result contains, so you can return different strings if your application needs to.

### view

Shows directory contents or file contents with optional line ranges:

`view_range` is optional and applies to text-file views: `[start_line, end_line]` returns those lines, and `[start_line, -1]` returns everything from `start_line` to the end of the file.

#### Return values

**For directories:** Return a listing that shows files and directories with their sizes:

* Lists files up to 2 levels deep
* Shows human-readable sizes (for example, `5.5K`, `1.2M`)
* Excludes hidden items (files starting with `.`) and `node_modules`
* Uses a tab character between the size and the path

The first `view` of `/memories` on an empty store is not an error. The SDKs' local-filesystem memory tools (`BetaLocalFilesystemMemoryTool`) create the memory root before Claude's first call and return the listing header followed by a single size-and-path line for the empty directory itself.

**For files:** Return file contents with a header and line numbers:

```text wrap
Here's the content of {path} with line numbers:
{line_numbers}{tab}{content}

text
Here's the content of /memories/notes.txt with line numbers:
     1	Hello World
     2	This is line two
    10	Line ten
   100	Line one hundred

json
{
  "command": "create",
  "path": "/memories/notes.txt",
  "file_text": "Meeting notes:\n- Discussed project timeline\n- Next steps defined\n"
}

json
{
  "command": "str_replace",
  "path": "/memories/preferences.txt",
  "old_str": "Favorite color: blue",
  "new_str": "Favorite color: green"
}

json
{
  "command": "insert",
  "path": "/memories/todo.txt",
  "insert_line": 2,
  "insert_text": "- Review memory tool documentation\n"
}

json
{
  "command": "delete",
  "path": "/memories/old_file.txt"
}

json
{
  "command": "rename",
  "old_path": "/memories/draft.txt",
  "new_path": "/memories/final.txt"
}
```

#### Return values

* **Success:** `"Successfully renamed {old_path} to {new_path}"`

#### Error handling

* **Source does not exist:** `"Error: The path {old_path} does not exist"`
* **Destination already exists:** Return an error (do not overwrite): `"Error: The destination {new_path} already exists"`

#### Directory handling

Renames the directory. The tool description tells Claude it cannot rename the `/memories` directory itself, so reject a `rename` whose `old_path` is the memory root.


## Prompting guidance

Source: https://platform.claude.com/llms-full.txt#prompting-guidance

When the memory tool is present in your request's `tools`, the API automatically adds this instruction to the system prompt. You don't need to send it yourself:

```text wrap
IMPORTANT: ALWAYS VIEW YOUR MEMORY DIRECTORY BEFORE DOING ANYTHING ELSE.
MEMORY PROTOCOL:
1. Use the `view` command of your `memory` tool to check for earlier progress.
2. ... (work on the task) ...
   - As you make progress, record status / progress / thoughts etc in your memory.
ASSUME INTERRUPTION: Your context window might be reset at any moment, so you risk losing any progress that is not recorded in your memory directory.

text wrap
Note: when editing your memory folder, always try to keep its content up-to-date, coherent and organized. You can rename or delete files that are no longer relevant. Do not create new files unless necessary.
```

You can also guide what Claude writes to memory. For example: "Only write down information relevant to \<topic> in your memory system."


## Security considerations

Source: https://platform.claude.com/llms-full.txt#security-considerations-3

Your application executes every file operation Claude requests, so these safeguards are your responsibility:

### Sensitive information

Claude usually refuses to write sensitive information to memory files. For stronger guarantees, add validation that strips sensitive data before your handler writes the file.

### File storage size

Track memory file sizes and cap how large a file can grow. Consider capping how many characters the `view` command returns, and let Claude page through the rest with `view_range`.

### Memory expiration

Periodically delete memory files that haven't been accessed in a long time.

### Path traversal protection

<Warning>
  A malicious path such as `/memories/../../secrets.env` can reach files outside the `/memories` directory. Your implementation must validate every path in every command to prevent directory traversal attacks.
</Warning>

Consider these safeguards:

* Validate that all paths start with `/memories`
* Resolve paths to their canonical form and verify they remain within the memory directory
* Reject paths containing sequences such as `../`, `..\\`, or other traversal patterns
* Watch for URL-encoded traversal sequences (`%2e%2e%2f`)
* Use your language's built-in path security utilities (for example, Python's `pathlib.Path.resolve()` and `relative_to()`)


## Error handling

Source: https://platform.claude.com/llms-full.txt#error-handling

The memory tool uses similar error-handling patterns to the [text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool#handle-errors). Each command's error messages are listed under [Tool commands](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool#tool-commands). To return an error to Claude, set `is_error` to `true` on the tool result and put the message in `content`:


## Context editing integration

Source: https://platform.claude.com/llms-full.txt#context-editing-integration

The memory tool pairs with context editing to manage long-running conversations. For details, see [Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing).


## Using with compaction

Source: https://platform.claude.com/llms-full.txt#using-with-compaction

The memory tool can also be paired with [compaction](https://platform.claude.com/docs/en/build-with-claude/compaction), which summarizes older conversation context server-side. Context editing clears specific tool results on the client. Compaction automatically summarizes the whole conversation on the server when the conversation approaches the context window limit.

For long-running agents, consider using both: compaction keeps the active context small without client-side bookkeeping, and memory preserves the information that must survive summarization.


## Multisession software development pattern

Source: https://platform.claude.com/llms-full.txt#multisession-software-development-pattern

For software projects that span multiple agent sessions, set up memory files deliberately instead of writing them ad hoc as work progresses. The following pattern turns memory into a recovery mechanism: each new session resumes from the state the last one recorded.

### How the pattern works

1. **Initializer session:** The first session sets up the memory files before any substantive work begins. This includes a progress log (tracking what has been done and what comes next), a feature checklist (defining the scope of work), and a reference to any startup or initialization script the project needs.

2. **Subsequent sessions:** Each new session opens by reading those memory files. This restores the project state without re-exploring the code base or retracing earlier decisions.

3. **End-of-session update:** Before a session ends, it updates the progress log with what was completed and what remains. This ensures the next session has an accurate starting point.

### Key principle

Work on one feature at a time. Mark a feature complete only after end-to-end verification confirms it works, not when the code is written. This keeps the progress log accurate from session to session.

<Tip>
  For a detailed case study of this pattern in practice, including the initializer script, progress file structure, and git-based recovery, see [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).
</Tip>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-32

<CardGroup cols={2}>
  <Card title="Bash tool" icon="terminal" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool">
    Execute shell commands in a persistent bash session.
  </Card>

  <Card title="Context editing" icon="edit" href="https://platform.claude.com/docs/en/build-with-claude/context-editing">
    Automatically manage conversation context as it grows with context editing.
  </Card>

  <Card title="Compaction" icon="stack" href="https://platform.claude.com/docs/en/build-with-claude/compaction">
    Server-side context compaction for managing long conversations that approach context window limits.
  </Card>

  <Card title="Tool reference" icon="book" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference">
    Directory of Anthropic-provided tools and reference for optional tool definition properties.
  </Card>
</CardGroup>


---
title: Parallel tool use
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use
description: Enable, format, and disable parallel tool calls, with message-history guidance and troubleshooting.
---

By default, Claude may call multiple tools in a single response. This page covers how to run those calls, how to format the message history so parallelism keeps working, and how to disable parallel tool use when you need to. For the single-call flow, see [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls).


## Execution semantics

Source: https://platform.claude.com/llms-full.txt#execution-semantics

When Claude calls tools, the response has a `stop_reason` of `tool_use` and can contain several `tool_use` blocks in a single assistant turn. How you run those calls is your decision. The API doesn't prescribe an execution order: you can run the calls concurrently (`Promise.all`, `asyncio.gather`), sequentially in the order they appear, or in any combination that suits your tools.

Choose the strategy based on what your tools do. Independent, read-only operations are usually safe to run in parallel for lower latency. Tools with side effects, shared state, or ordering requirements might be better run sequentially.

Whichever strategy you use, return one `tool_result` for each `tool_use` block, all together in the next user message. Match each result to its call with `tool_use_id`, and put every `tool_result` block before any text content in that message. See [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) for the full formatting rules. If you choose not to run a particular call (for example, because you ran the batch sequentially and an earlier call failed), still return a `tool_result` for it with `is_error: true` and a brief explanation.

The [computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#batch-actions) and the [browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#batch-actions) are stricter. When Claude returns several of their member tool calls in one turn (a batch action), run them sequentially in the order they appear and stop at the first failure; each tool defines the exact text to return for the calls you skip.


## Test parallel tool calls

Source: https://platform.claude.com/llms-full.txt#test-parallel-tool-calls

<Note>
  **Use the Tool Runner for most applications:** the SDK [Tool Runner](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner) handles responses with multiple tool calls and formats the results for you, so you don't write this handling yourself. Use the manual pattern on this page when you need direct control over how the calls run, such as custom batching, ordering, or error handling.
</Note>

The following script sends a request that should trigger parallel tool calls, verifies the response contains them, and formats the tool results so parallelism keeps working. Run it with `ANTHROPIC_API_KEY` set in your environment:

<CodeGroup>
  ```bash cURL
  # This end-to-end test flow doesn't translate well to a one-off shell command.
  # See the SDK tabs for the full flow. The underlying HTTP request is a standard
  # tool use request with multiple tools defined.

bash CLI
  # This end-to-end test flow doesn't translate well to a one-off shell command.
  # See the SDK tabs for the full flow.

python Python
  client = Anthropic()

  # Define tools
  tools = [
      {
          "name": "get_weather",
          "description": "Get the current weather in a given location",
          "input_schema": {
              "type": "object",
              "properties": {
                  "location": {
                      "type": "string",
                      "description": "The city and state, e.g. San Francisco, CA",
                  }
              },
              "required": ["location"],
          },
      },
      {
          "name": "get_time",
          "description": "Get the current time in a given timezone",
          "input_schema": {
              "type": "object",
              "properties": {
                  "timezone": {
                      "type": "string",
                      "description": "The timezone, e.g. America/New_York",
                  }
              },
              "required": ["timezone"],
          },
      },
  ]

  # Test conversation with parallel tool calls
  messages = [
      {
          "role": "user",
          "content": "What's the weather in SF and NYC, and what time is it there?",
      }
  ]

  # Make initial request
  print("Requesting parallel tool calls...")
  response = client.messages.create(
      model="claude-opus-5", max_tokens=1024, messages=messages, tools=tools
  )

  # Check for parallel tool calls
  tool_uses = [block for block in response.content if block.type == "tool_use"]
  print(f"\n✓ Claude made {len(tool_uses)} tool calls")

  if len(tool_uses) > 1:
      print("✓ Parallel tool calls detected!")
      for tool in tool_uses:
          print(f"  - {tool.name}: {tool.input}")
  else:
      print("✗ No parallel tool calls detected")

  # Simulate tool execution and format results correctly
  tool_results = []
  for tool_use in tool_uses:
      if tool_use.name == "get_weather":
          if "San Francisco" in str(tool_use.input):
              result = "San Francisco: 68°F, partly cloudy"
          else:
              result = "New York: 45°F, clear skies"
      else:  # get_time
          if "Los_Angeles" in str(tool_use.input):
              result = "2:30 PM PST"
          else:
              result = "5:30 PM EST"

      tool_results.append(
          {"type": "tool_result", "tool_use_id": tool_use.id, "content": result}
      )

  # Continue conversation with tool results
  messages.extend(
      [
          {"role": "assistant", "content": response.content},
          {"role": "user", "content": tool_results},  # All results in one message!
      ]
  )

  # Get final response
  print("\nGetting final response...")
  final_response = client.messages.create(
      model="claude-opus-5", max_tokens=1024, messages=messages, tools=tools
  )

  final_text = next(
      block.text for block in final_response.content if block.type == "text"
  )
  print(f"\nClaude's response:\n{final_text}")

  # Verify formatting
  print("\n--- Verification ---")
  print(f"✓ Tool results sent in single user message: {len(tool_results)} results")
  print("✓ No text before tool results in content array")
  print("✓ Conversation formatted correctly for future parallel tool use")

typescript TypeScript
  const client = new Anthropic();

  // Define tools
  const tools: Anthropic.Tool[] = [
    {
      name: "get_weather",
      description: "Get the current weather in a given location",
      input_schema: {
        type: "object" as const,
        properties: {
          location: {
            type: "string",
            description: "The city and state, e.g. San Francisco, CA"
          }
        },
        required: ["location"]
      }
    },
    {
      name: "get_time",
      description: "Get the current time in a given timezone",
      input_schema: {
        type: "object" as const,
        properties: {
          timezone: {
            type: "string",
            description: "The timezone, e.g. America/New_York"
          }
        },
        required: ["timezone"]
      }
    }
  ];

  // Make initial request
  console.log("Requesting parallel tool calls...");
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: "What's the weather in SF and NYC, and what time is it there?"
      }
    ],
    tools: tools
  });

  // Check for parallel tool calls
  const toolUses = response.content.filter((block) => block.type === "tool_use");
  console.log(`\n✓ Claude made ${toolUses.length} tool calls`);

  if (toolUses.length > 1) {
    console.log("✓ Parallel tool calls detected!");
    for (const tool of toolUses) {
      if (tool.type === "tool_use") {
        console.log(`  - ${tool.name}: ${JSON.stringify(tool.input)}`);
      }
    }
  } else {
    console.log("✗ No parallel tool calls detected");
  }

  // Simulate tool execution and format results correctly
  const toolResults: Anthropic.ToolResultBlockParam[] = toolUses
    .filter((block): block is Anthropic.ToolUseBlock => block.type === "tool_use")
    .map((toolUse) => {
      const input = toolUse.input as Record<string, string>;
      let result: string;
      if (toolUse.name === "get_weather") {
        result = input.location?.includes("San Francisco")
          ? "San Francisco: 68F, partly cloudy"
          : "New York: 45F, clear skies";
      } else {
        result = input.timezone?.includes("Los_Angeles") ? "2:30 PM PST" : "5:30 PM EST";
      }

      return {
        type: "tool_result" as const,
        tool_use_id: toolUse.id,
        content: result
      };
    });

  // Get final response with correct formatting
  console.log("\nGetting final response...");
  const finalResponse = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: "What's the weather in SF and NYC, and what time is it there?"
      },
      { role: "assistant", content: response.content },
      { role: "user", content: toolResults }
    ],
    tools: tools
  });

  for (const block of finalResponse.content) {
    if (block.type === "text") {
      console.log(`\nClaude's response:\n${block.text}`);
    }
  }

  // Verify formatting
  console.log("\n--- Verification ---");
  console.log(`✓ Tool results sent in single user message: ${toolResults.length} results`);
  console.log("✓ No text before tool results in content array");
  console.log("✓ Conversation formatted correctly for future parallel tool use");

csharp C#
  AnthropicClient client = new();

  var tools = new List<ToolUnion>
  {
      new ToolUnion(new Tool()
      {
          Name = "get_weather",
          Description = "Get the current weather in a given location",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["location"] = JsonSerializer.SerializeToElement(new { type = "string", description = "The city and state, e.g. San Francisco, CA" }),
              },
              Required = ["location"],
          },
      }),
      new ToolUnion(new Tool()
      {
          Name = "get_time",
          Description = "Get the current time in a given timezone",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["timezone"] = JsonSerializer.SerializeToElement(new { type = "string", description = "The timezone, e.g. America/New_York" }),
              },
              Required = ["timezone"],
          },
      }),
  };

  Console.WriteLine("Requesting parallel tool calls...");
  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "What's the weather in SF and NYC, and what time is it there?" }],
      Tools = tools
  };

  var response = await client.Messages.Create(parameters);

  var toolUses = new List<ToolUseBlock>();
  foreach (var block in response.Content)
  {
      if (block.TryPickToolUse(out var toolUse))
      {
          toolUses.Add(toolUse);
      }
  }
  Console.WriteLine($"\n✓ Claude made {toolUses.Count} tool calls");

  if (toolUses.Count > 1)
  {
      Console.WriteLine("✓ Parallel tool calls detected!");
      foreach (var tool in toolUses)
      {
          Console.WriteLine($"  - {tool.Name}: {JsonSerializer.Serialize(tool.Input)}");
      }
  }
  else
  {
      Console.WriteLine("✗ No parallel tool calls detected");
  }

  var toolResults = new List<ContentBlockParam>();
  foreach (var toolUse in toolUses)
  {
      string result;
      if (toolUse.Name == "get_weather")
      {
          result = JsonSerializer.Serialize(toolUse.Input).Contains("San Francisco")
              ? "San Francisco: 68°F, partly cloudy"
              : "New York: 45°F, clear skies";
      }
      else
      {
          result = JsonSerializer.Serialize(toolUse.Input).Contains("Los_Angeles")
              ? "2:30 PM PST"
              : "5:30 PM EST";
      }

      toolResults.Add(new ContentBlockParam(new ToolResultBlockParam()
      {
          ToolUseID = toolUse.ID,
          Content = result,
      }));
  }

  Console.WriteLine("\nGetting final response...");
  var finalParameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [
          new() { Role = Role.User, Content = "What's the weather in SF and NYC, and what time is it there?" },
          new() { Role = Role.Assistant, Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList() },
          new() { Role = Role.User, Content = new MessageParamContent(toolResults) }
      ],
      Tools = tools
  };

  var finalResponse = await client.Messages.Create(finalParameters);
  var text = finalResponse.Content.Select(b => b.Value).OfType<TextBlock>().FirstOrDefault();
  Console.WriteLine($"\nClaude's response:\n{text?.Text}");

  Console.WriteLine("\n--- Verification ---");
  Console.WriteLine($"✓ Tool results sent in single user message: {toolResults.Count} results");
  Console.WriteLine("✓ No text before tool results in content array");
  Console.WriteLine("✓ Conversation formatted correctly for future parallel tool use");

go Go
  client := anthropic.NewClient()

  tools := []anthropic.ToolUnionParam{
  	{OfTool: &anthropic.ToolParam{
  		Name:        "get_weather",
  		Description: anthropic.String("Get the current weather in a given location"),
  		InputSchema: anthropic.ToolInputSchemaParam{
  			Properties: map[string]any{
  				"location": map[string]any{
  					"type":        "string",
  					"description": "The city and state, e.g. San Francisco, CA",
  				},
  			},
  			Required: []string{"location"},
  		},
  	}},
  	{OfTool: &anthropic.ToolParam{
  		Name:        "get_time",
  		Description: anthropic.String("Get the current time in a given timezone"),
  		InputSchema: anthropic.ToolInputSchemaParam{
  			Properties: map[string]any{
  				"timezone": map[string]any{
  					"type":        "string",
  					"description": "The timezone, e.g. America/New_York",
  				},
  			},
  			Required: []string{"timezone"},
  		},
  	}},
  }

  fmt.Println("Requesting parallel tool calls...")
  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather in SF and NYC, and what time is it there?")),
  	},
  	Tools: tools,
  })
  if err != nil {
  	log.Fatal(err)
  }

  // Find tool use blocks using type switch
  type toolUseInfo struct {
  	ID    string
  	Name  string
  	Input json.RawMessage
  }
  var toolUses []toolUseInfo
  for _, block := range response.Content {
  	switch variant := block.AsAny().(type) {
  	case anthropic.ToolUseBlock:
  		toolUses = append(toolUses, toolUseInfo{
  			ID:    variant.ID,
  			Name:  variant.Name,
  			Input: variant.Input,
  		})
  	}
  }

  fmt.Printf("\n✓ Claude made %d tool calls\n", len(toolUses))

  if len(toolUses) > 1 {
  	fmt.Println("✓ Parallel tool calls detected!")
  	for _, tool := range toolUses {
  		fmt.Printf("  - %s: %s\n", tool.Name, string(tool.Input))
  	}
  } else {
  	fmt.Println("✗ No parallel tool calls detected")
  }

  // Build tool results
  var toolResults []anthropic.ContentBlockParamUnion
  for _, toolUse := range toolUses {
  	var result string
  	inputStr := string(toolUse.Input)

  	if toolUse.Name == "get_weather" {
  		if strings.Contains(inputStr, "San Francisco") {
  			result = "San Francisco: 68°F, partly cloudy"
  		} else {
  			result = "New York: 45°F, clear skies"
  		}
  	} else {
  		if strings.Contains(inputStr, "Los_Angeles") {
  			result = "2:30 PM PST"
  		} else {
  			result = "5:30 PM EST"
  		}
  	}

  	toolResults = append(toolResults, anthropic.NewToolResultBlock(toolUse.ID, result, false))
  }

  fmt.Println("\nGetting final response...")
  finalResponse, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather in SF and NYC, and what time is it there?")),
  		response.ToParam(),
  		anthropic.NewUserMessage(toolResults...),
  	},
  	Tools: tools,
  })
  if err != nil {
  	log.Fatal(err)
  }

  var finalText string
  for _, block := range finalResponse.Content {
  	if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  		finalText = textBlock.Text
  		break
  	}
  }

  fmt.Printf("\nClaude's response:\n%s\n", finalText)

  fmt.Println("\n--- Verification ---")
  fmt.Printf("✓ Tool results sent in single user message: %d results\n", len(toolResults))
  fmt.Println("✓ No text before tool results in content array")
  fmt.Println("✓ Conversation formatted correctly for future parallel tool use")

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  Tool weatherTool = Tool.builder()
      .name("get_weather")
      .description("Get the current weather in a given location")
      .inputSchema(InputSchema.builder()
          .properties(JsonValue.from(Map.of(
              "location", Map.of(
                  "type", "string",
                  "description", "The city and state, e.g. San Francisco, CA"
              )
          )))
          .putAdditionalProperty("required", JsonValue.from(List.of("location")))
          .build())
      .build();

  Tool timeTool = Tool.builder()
      .name("get_time")
      .description("Get the current time in a given timezone")
      .inputSchema(InputSchema.builder()
          .properties(JsonValue.from(Map.of(
              "timezone", Map.of(
                  "type", "string",
                  "description", "The timezone, e.g. America/New_York"
              )
          )))
          .putAdditionalProperty("required", JsonValue.from(List.of("timezone")))
          .build())
      .build();

  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024L)
      .addTool(weatherTool)
      .addTool(timeTool)
      .addUserMessage("What's the weather in SF and NYC, and what time is it there?")
      .build();

  IO.println("Requesting parallel tool calls...");
  Message response = client.messages().create(params);

  List<ToolUseBlock> toolUses = new ArrayList<>();
  for (ContentBlock block : response.content()) {
      if (block.toolUse().isPresent()) {
          toolUses.add(block.toolUse().get());
      }
  }

  IO.println("\n✓ Claude made " + toolUses.size() + " tool calls");

  if (toolUses.size() > 1) {
      IO.println("✓ Parallel tool calls detected!");
      for (ToolUseBlock tool : toolUses) {
          IO.println("  - " + tool.name() + ": " + tool._input());
      }
  } else {
      IO.println("✗ No parallel tool calls detected");
  }

  List<ContentBlockParam> toolResults = new ArrayList<>();
  for (ToolUseBlock toolUse : toolUses) {
      String result;
      if (toolUse.name().equals("get_weather")) {
          String location = toolUse._input().toString();
          result = location.contains("San Francisco")
              ? "San Francisco: 68°F, partly cloudy"
              : "New York: 45°F, clear skies";
      } else {
          String timezone = toolUse._input().toString();
          result = timezone.contains("Los_Angeles")
              ? "2:30 PM PST"
              : "5:30 PM EST";
      }
      toolResults.add(ContentBlockParam.ofToolResult(
          ToolResultBlockParam.builder()
              .toolUseId(toolUse.id())
              .content(result)
              .build()
      ));
  }

  IO.println("\nGetting final response...");
  MessageCreateParams finalParams = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024L)
      .addTool(weatherTool)
      .addTool(timeTool)
      .addUserMessage("What's the weather in SF and NYC, and what time is it there?")
      .addMessage(response)
      .addUserMessageOfBlockParams(toolResults)
      .build();

  Message finalResponse = client.messages().create(finalParams);
  finalResponse.content().stream()
      .flatMap(block -> block.text().stream())
      .forEach(textBlock -> IO.println("\nClaude's response:\n" + textBlock.text()));

  IO.println("\n--- Verification ---");
  IO.println("✓ Tool results sent in single user message: " + toolResults.size() + " results");
  IO.println("✓ No text before tool results in content array");
  IO.println("✓ Conversation formatted correctly for future parallel tool use");

php PHP
  $client = new Client();

  $tools = [
      [
          'name' => 'get_weather',
          'description' => 'Get the current weather in a given location',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'location' => [
                      'type' => 'string',
                      'description' => 'The city and state, e.g. San Francisco, CA'
                  ]
              ],
              'required' => ['location']
          ]
      ],
      [
          'name' => 'get_time',
          'description' => 'Get the current time in a given timezone',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'timezone' => [
                      'type' => 'string',
                      'description' => 'The timezone, e.g. America/New_York'
                  ]
              ],
              'required' => ['timezone']
          ]
      ]
  ];

  echo "Requesting parallel tool calls...\n";
  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => "What's the weather in SF and NYC, and what time is it there?"]
      ],
      model: 'claude-opus-5',
      tools: $tools,
  );

  $toolUses = array_filter($response->content, fn($block) => $block->type === 'tool_use');
  echo "\n✓ Claude made " . count($toolUses) . " tool calls\n";

  if (count($toolUses) > 1) {
      echo "✓ Parallel tool calls detected!\n";
      foreach ($toolUses as $tool) {
          echo "  - {$tool->name}: " . json_encode($tool->input) . "\n";
      }
  } else {
      echo "✗ No parallel tool calls detected\n";
  }

  $toolResults = [];
  foreach ($toolUses as $toolUse) {
      if ($toolUse->name === 'get_weather') {
          $result = str_contains(json_encode($toolUse->input), 'San Francisco')
              ? 'San Francisco: 68°F, partly cloudy'
              : 'New York: 45°F, clear skies';
      } else {
          $result = str_contains(json_encode($toolUse->input), 'Los_Angeles')
              ? '2:30 PM PST'
              : '5:30 PM EST';
      }

      $toolResults[] = [
          'type' => 'tool_result',
          'tool_use_id' => $toolUse->id,
          'content' => $result
      ];
  }

  echo "\nGetting final response...\n";
  $finalResponse = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => "What's the weather in SF and NYC, and what time is it there?"],
          ['role' => 'assistant', 'content' => $response->content],
          ['role' => 'user', 'content' => $toolResults]
      ],
      model: 'claude-opus-5',
      tools: $tools,
  );

  $textBlock = array_find($finalResponse->content, static fn ($block): bool => $block->type === 'text');
  echo "\nClaude's response:\n{$textBlock->text}\n";

  echo "\n--- Verification ---\n";
  echo "✓ Tool results sent in single user message: " . count($toolResults) . " results\n";
  echo "✓ No text before tool results in content array\n";
  echo "✓ Conversation formatted correctly for future parallel tool use\n";

ruby Ruby
  client = Anthropic::Client.new

  tools = [
    {
      name: "get_weather",
      description: "Get the current weather in a given location",
      input_schema: {
        type: "object",
        properties: {
          location: {
            type: "string",
            description: "The city and state, e.g. San Francisco, CA"
          }
        },
        required: ["location"]
      }
    },
    {
      name: "get_time",
      description: "Get the current time in a given timezone",
      input_schema: {
        type: "object",
        properties: {
          timezone: {
            type: "string",
            description: "The timezone, e.g. America/New_York"
          }
        },
        required: ["timezone"]
      }
    }
  ]

  puts "Requesting parallel tool calls..."
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      { role: "user", content: "What's the weather in SF and NYC, and what time is it there?" }
    ],
    tools: tools
  )

  tool_uses = response.content.select { |block| block.type == :tool_use }
  puts "\n✓ Claude made #{tool_uses.length} tool calls"

  if tool_uses.length > 1
    puts "✓ Parallel tool calls detected!"
    tool_uses.each do |tool|
      puts "  - #{tool.name}: #{tool.input}"
    end
  else
    puts "✗ No parallel tool calls detected"
  end

  tool_results = tool_uses.map do |tool_use|
    result = if tool_use.name == "get_weather"
      location = tool_use.input[:location].to_s
      location.include?("San Francisco") ? "San Francisco: 68°F, partly cloudy" : "New York: 45°F, clear skies"
    else
      timezone = tool_use.input[:timezone].to_s
      timezone.include?("Los_Angeles") ? "2:30 PM PST" : "5:30 PM EST"
    end

    {
      type: "tool_result",
      tool_use_id: tool_use.id,
      content: result
    }
  end

  puts "\nGetting final response..."
  final_response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      { role: "user", content: "What's the weather in SF and NYC, and what time is it there?" },
      { role: "assistant", content: response.content },
      { role: "user", content: tool_results }
    ],
    tools: tools
  )

  final_text = final_response.content.find { |block| block.type == :text }
  puts "\nClaude's response:\n#{final_text.text}"

  puts "\n--- Verification ---"
  puts "✓ Tool results sent in single user message: #{tool_results.length} results"
  puts "✓ No text before tool results in content array"
  puts "✓ Conversation formatted correctly for future parallel tool use"
  ```
</CodeGroup>

The summary lines at the end restate the two formatting rules that keep parallelism working: every tool result returns in a single user message, and no text content appears before the tool results in that message.


## Maximizing parallel tool use

Source: https://platform.claude.com/llms-full.txt#maximizing-parallel-tool-use

Claude 4 and later models make parallel tool calls by default when a request benefits from multiple tools. For all models, you can increase the likelihood of parallel tool calls with targeted prompting:

<AccordionGroup>
  <Accordion title="System prompts for parallel tool use">
    For Claude 4 and later models, add this to your system prompt:

    ```text wrap
    For maximum efficiency, whenever you need to perform multiple independent operations, invoke all relevant tools simultaneously rather than sequentially.

text wrap
    <use_parallel_tool_calls>
    For maximum efficiency, whenever you perform multiple independent operations, invoke all relevant tools simultaneously rather than sequentially. Prioritize calling tools in parallel whenever possible. For example, when reading 3 files, run 3 tool calls in parallel to read all 3 files into context at the same time. When running multiple read-only commands like `ls` or `list_dir`, always run all of the commands in parallel. Err on the side of maximizing parallel tool calls rather than running too many tools sequentially.
    </use_parallel_tool_calls>

text wrap
    Instead of:
    "What's the weather in Paris? Also check London."

    Use:
    "Check the weather in Paris and London simultaneously."

    Or be explicit:
    "Please use parallel tool calls to get the weather for Paris, London, and Tokyo at the same time."
    ```
  </Accordion>
</AccordionGroup>

<Note>
  **Claude Fable 5.1 in long agent loops**

  Claude Fable 5.1 may issue fewer parallel tool calls than earlier models, most noticeably in long agent loops where the next reads are only implied (custom coding agents, bash and text editor harnesses, computer use). Standard function calling is unaffected. For the batching instruction to add and where to put it, see [Batch independent tool calls in agent loops](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#batch-independent-tool-calls-in-agent-loops).
</Note>


## Disable parallel tool use

Source: https://platform.claude.com/llms-full.txt#disable-parallel-tool-use

Parallel tool use is on by default. To turn it off, set `disable_parallel_tool_use: true` inside the [`tool_choice`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools#forcing-tool-use) object. It is not a top-level request parameter. The effect depends on the `tool_choice` type.

### At most one tool call

When `tool_choice` type is `auto` (the default), setting `disable_parallel_tool_use: true` means Claude calls at most one tool per response. Claude can still answer in plain text without calling any tool. The highlighted lines are the only change from a standard tool use request:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "tools": [{
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            }
          },
          "required": ["location"]
        }
      }],
      "tool_choice": {"type": "auto", "disable_parallel_tool_use": true},
      "messages": [
        {"role": "user", "content": "What is the weather in San Francisco and New York?"}
      ]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tools:
    - name: get_weather
      description: Get the current weather in a given location
      input_schema:
        type: object
        properties:
          location:
            type: string
            description: The city and state, e.g. San Francisco, CA
        required: [location]
  tool_choice:
    type: auto
    disable_parallel_tool_use: true
  messages:
    - role: user
      content: What is the weather in San Francisco and New York?
  YAML

python Python
  client = Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[
          {
              "name": "get_weather",
              "description": "Get the current weather in a given location",
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "location": {
                          "type": "string",
                          "description": "The city and state, e.g. San Francisco, CA",
                      }
                  },
                  "required": ["location"],
              },
          }
      ],
      tool_choice={"type": "auto", "disable_parallel_tool_use": True},
      messages=[
          {
              "role": "user",
              "content": "What is the weather in San Francisco and New York?",
          }
      ],
  )
  print(response.content)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        name: "get_weather",
        description: "Get the current weather in a given location",
        input_schema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA"
            }
          },
          required: ["location"]
        }
      }
    ],
    tool_choice: { type: "auto", disable_parallel_tool_use: true },
    messages: [{ role: "user", content: "What is the weather in San Francisco and New York?" }]
  });
  console.log(response.content);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = [
          new ToolUnion(new Tool()
          {
              Name = "get_weather",
              Description = "Get the current weather in a given location",
              InputSchema = new InputSchema()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["location"] = JsonSerializer.SerializeToElement(new { type = "string", description = "The city and state, e.g. San Francisco, CA" }),
                  },
                  Required = ["location"],
              },
          }),
      ],
      ToolChoice = new ToolChoiceAuto { DisableParallelToolUse = true },
      Messages = [new() { Role = Role.User, Content = "What is the weather in San Francisco and New York?" }]
  };

  var response = await client.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{
  		{OfTool: &anthropic.ToolParam{
  			Name:        "get_weather",
  			Description: anthropic.String("Get the current weather in a given location"),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"location": map[string]any{
  						"type":        "string",
  						"description": "The city and state, e.g. San Francisco, CA",
  					},
  				},
  				Required: []string{"location"},
  			},
  		}},
  	},
  	ToolChoice: anthropic.ToolChoiceUnionParam{
  		OfAuto: &anthropic.ToolChoiceAutoParam{
  			DisableParallelToolUse: anthropic.Bool(true),
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What is the weather in San Francisco and New York?")),
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
                  )
              )
          )
      )
      .putAdditionalProperty("required", JsonValue.from(List.of("location")))
      .build();

  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024L)
      .addTool(
          Tool.builder()
              .name("get_weather")
              .description("Get the current weather in a given location")
              .inputSchema(schema)
              .build()
      )
      .toolChoice(ToolChoiceAuto.builder().disableParallelToolUse(true).build())
      .addUserMessage("What is the weather in San Francisco and New York?")
      .build();

  Message response = client.messages().create(params);
  IO.println(response.content());

php PHP
  $client = new Client();

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => 'What is the weather in San Francisco and New York?']
      ],
      model: 'claude-opus-5',
      toolChoice: ['type' => 'auto', 'disableParallelToolUse' => true],
      tools: [
          [
              'name' => 'get_weather',
              'description' => 'Get the current weather in a given location',
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'location' => [
                          'type' => 'string',
                          'description' => 'The city and state, e.g. San Francisco, CA'
                      ]
                  ],
                  'required' => ['location']
              ]
          ]
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
        name: "get_weather",
        description: "Get the current weather in a given location",
        input_schema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA"
            }
          },
          required: ["location"]
        }
      }
    ],
    tool_choice: { type: "auto", disable_parallel_tool_use: true },
    messages: [
      { role: "user", content: "What is the weather in San Francisco and New York?" }
    ]
  )
  puts response.content

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "tools": [{
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            }
          },
          "required": ["location"]
        }
      }],
      "tool_choice": {"type": "any", "disable_parallel_tool_use": true},
      "messages": [
        {"role": "user", "content": "What is the weather in San Francisco and New York?"}
      ]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tools:
    - name: get_weather
      description: Get the current weather in a given location
      input_schema:
        type: object
        properties:
          location:
            type: string
            description: The city and state, e.g. San Francisco, CA
        required: [location]
  tool_choice:
    type: any
    disable_parallel_tool_use: true
  messages:
    - role: user
      content: What is the weather in San Francisco and New York?
  YAML

python Python
  client = Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[
          {
              "name": "get_weather",
              "description": "Get the current weather in a given location",
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "location": {
                          "type": "string",
                          "description": "The city and state, e.g. San Francisco, CA",
                      }
                  },
                  "required": ["location"],
              },
          }
      ],
      tool_choice={"type": "any", "disable_parallel_tool_use": True},
      messages=[
          {
              "role": "user",
              "content": "What is the weather in San Francisco and New York?",
          }
      ],
  )
  print(response.content)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        name: "get_weather",
        description: "Get the current weather in a given location",
        input_schema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA"
            }
          },
          required: ["location"]
        }
      }
    ],
    tool_choice: { type: "any", disable_parallel_tool_use: true },
    messages: [{ role: "user", content: "What is the weather in San Francisco and New York?" }]
  });
  console.log(response.content);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = [
          new ToolUnion(new Tool()
          {
              Name = "get_weather",
              Description = "Get the current weather in a given location",
              InputSchema = new InputSchema()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["location"] = JsonSerializer.SerializeToElement(new { type = "string", description = "The city and state, e.g. San Francisco, CA" }),
                  },
                  Required = ["location"],
              },
          }),
      ],
      ToolChoice = new ToolChoiceAny { DisableParallelToolUse = true },
      Messages = [new() { Role = Role.User, Content = "What is the weather in San Francisco and New York?" }]
  };

  var response = await client.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{
  		{OfTool: &anthropic.ToolParam{
  			Name:        "get_weather",
  			Description: anthropic.String("Get the current weather in a given location"),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"location": map[string]any{
  						"type":        "string",
  						"description": "The city and state, e.g. San Francisco, CA",
  					},
  				},
  				Required: []string{"location"},
  			},
  		}},
  	},
  	ToolChoice: anthropic.ToolChoiceUnionParam{
  		OfAny: &anthropic.ToolChoiceAnyParam{
  			DisableParallelToolUse: anthropic.Bool(true),
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What is the weather in San Francisco and New York?")),
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
                  )
              )
          )
      )
      .putAdditionalProperty("required", JsonValue.from(List.of("location")))
      .build();

  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024L)
      .addTool(
          Tool.builder()
              .name("get_weather")
              .description("Get the current weather in a given location")
              .inputSchema(schema)
              .build()
      )
      .toolChoice(ToolChoiceAny.builder().disableParallelToolUse(true).build())
      .addUserMessage("What is the weather in San Francisco and New York?")
      .build();

  Message response = client.messages().create(params);
  IO.println(response.content());

php PHP
  $client = new Client();

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => 'What is the weather in San Francisco and New York?']
      ],
      model: 'claude-opus-5',
      toolChoice: ['type' => 'any', 'disableParallelToolUse' => true],
      tools: [
          [
              'name' => 'get_weather',
              'description' => 'Get the current weather in a given location',
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'location' => [
                          'type' => 'string',
                          'description' => 'The city and state, e.g. San Francisco, CA'
                      ]
                  ],
                  'required' => ['location']
              ]
          ]
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
        name: "get_weather",
        description: "Get the current weather in a given location",
        input_schema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA"
            }
          },
          required: ["location"]
        }
      }
    ],
    tool_choice: { type: "any", disable_parallel_tool_use: true },
    messages: [
      { role: "user", content: "What is the weather in San Francisco and New York?" }
    ]
  )
  puts response.content
  ```
</CodeGroup>


## Troubleshooting

Source: https://platform.claude.com/llms-full.txt#troubleshooting

If Claude isn't making parallel tool calls when expected, check these common issues:

**1. Incorrect tool result formatting**

The most common issue is formatting tool results incorrectly in the conversation history. This "teaches" Claude to avoid parallel calls.

Specifically for parallel tool use:

* **Wrong:** a separate user message for each tool result
* **Correct:** all tool results together in a single user message

See [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) for other formatting rules.

**2. Weak prompting**

Default prompting might not be sufficient. Use the stronger system prompt from [Maximizing parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use#maximizing-parallel-tool-use).

**3. Measuring parallel tool usage**

To verify parallel tool calls are working:

<CodeGroup>
  ```bash cURL
  # Measuring parallel tool use is client-side analysis of responses you've already
  # collected, so it doesn't translate to a one-off shell command. See the SDK tabs.

bash CLI
  # Measuring parallel tool use is client-side analysis of responses you've already
  # collected, so it doesn't translate to a one-off shell command. See the SDK tabs.

python Python
  messages = []  # Message objects returned by client.messages.create across your run

  tool_call_messages = [
      msg for msg in messages if any(block.type == "tool_use" for block in msg.content)
  ]
  total_tool_calls = sum(
      len([block for block in msg.content if block.type == "tool_use"])
      for msg in tool_call_messages
  )
  avg_tools_per_message = (
      total_tool_calls / len(tool_call_messages) if tool_call_messages else 0.0
  )
  print(f"Average tools per message: {avg_tools_per_message}")
  # Should be > 1.0 if parallel calls are working

typescript TypeScript
  const messages: Anthropic.Message[] = []; // Message objects returned by client.messages.create across your run

  const toolCallMessages = messages.filter((message) =>
    message.content.some((block) => block.type === "tool_use")
  );
  const totalToolCalls = toolCallMessages.reduce(
    (sum, message) => sum + message.content.filter((block) => block.type === "tool_use").length,
    0
  );
  const avgToolsPerMessage =
    toolCallMessages.length > 0 ? totalToolCalls / toolCallMessages.length : 0;
  console.log(`Average tools per message: ${avgToolsPerMessage}`);
  // Should be > 1.0 if parallel calls are working

csharp C#
  List<Message> messages = []; // Message objects returned by client.Messages.Create across your run

  var toolCallMessages = messages
      .Where(message => message.Content.Any(block => block.TryPickToolUse(out _)))
      .ToList();
  var totalToolCalls = toolCallMessages
      .Sum(message => message.Content.Count(block => block.TryPickToolUse(out _)));
  var avgToolsPerMessage = toolCallMessages.Count > 0 ? (double)totalToolCalls / toolCallMessages.Count : 0.0;
  Console.WriteLine($"Average tools per message: {avgToolsPerMessage}");
  // Should be > 1.0 if parallel calls are working

go Go
  var messages []anthropic.Message // Message values returned by client.Messages.New across your run

  toolCallMessageCount := 0
  totalToolCalls := 0
  for _, message := range messages {
  	callsInMessage := 0
  	for _, block := range message.Content {
  		if block.Type == "tool_use" {
  			callsInMessage++
  		}
  	}
  	if callsInMessage > 0 {
  		toolCallMessageCount++
  		totalToolCalls += callsInMessage
  	}
  }

  avgToolsPerMessage := 0.0
  if toolCallMessageCount > 0 {
  	avgToolsPerMessage = float64(totalToolCalls) / float64(toolCallMessageCount)
  }
  fmt.Println("Average tools per message:", avgToolsPerMessage)
  // Should be > 1.0 if parallel calls are working

java Java
  List<Message> messages = List.of(); // Message objects returned by client.messages().create() across your run

  List<Message> toolCallMessages = messages.stream()
      .filter(message -> message.content().stream().anyMatch(ContentBlock::isToolUse))
      .toList();
  long totalToolCalls = toolCallMessages.stream()
      .mapToLong(message -> message.content().stream().filter(ContentBlock::isToolUse).count())
      .sum();
  double avgToolsPerMessage = toolCallMessages.isEmpty() ? 0.0 : (double) totalToolCalls / toolCallMessages.size();
  IO.println("Average tools per message: " + avgToolsPerMessage);
  // Should be > 1.0 if parallel calls are working

php PHP
  // $messages: Message objects returned by $client->messages->create() across your run
  $messages = [];

  $toolCallMessages = array_values(array_filter(
      $messages,
      fn ($message) => count(array_filter($message->content, fn ($block) => $block->type === 'tool_use')) > 0
  ));
  $totalToolCalls = array_sum(array_map(
      fn ($message) => count(array_filter($message->content, fn ($block) => $block->type === 'tool_use')),
      $toolCallMessages
  ));
  $avgToolsPerMessage = count($toolCallMessages) > 0 ? $totalToolCalls / count($toolCallMessages) : 0.0;
  echo "Average tools per message: {$avgToolsPerMessage}\n";
  // Should be > 1.0 if parallel calls are working

ruby Ruby
  messages = [] # Message objects returned by client.messages.create across your run

  tool_call_messages = messages.select { |message| message.content.any? { |block| block.type == :tool_use } }
  total_tool_calls = tool_call_messages.sum { |message| message.content.count { |block| block.type == :tool_use } }
  avg_tools_per_message = tool_call_messages.empty? ? 0.0 : total_tool_calls.to_f / tool_call_messages.size
  puts "Average tools per message: #{avg_tools_per_message}"
  # Should be > 1.0 if parallel calls are working
  ```
</CodeGroup>

**4. Calls in a batch appear to depend on each other**

Execution order is your choice. If your tools have ordering dependencies, running the batch sequentially and stopping on the first failure is a valid strategy (and the required one for the [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#batch-actions) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#batch-actions) tools): return `is_error: true` for any call you didn't run. If you run in parallel and a call fails because its prerequisite hadn't completed, return `is_error: true` with the natural error message. Claude will reissue the call on the next turn. To reduce dependent calls appearing together, add this to your system prompt: "Only batch tool calls that are independent of each other."


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-33

<CardGroup cols={3}>
  <Card title="Tool Runner (SDK)" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner">
    Use the SDK's Tool Runner abstraction to handle the agentic loop, error wrapping, and type safety automatically.
  </Card>

  <Card title="Handle tool calls" icon="arrows-left-right" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls">
    Parse tool\_use blocks, format tool\_result responses, and handle errors with is\_error.
  </Card>

  <Card title="Define tools" icon="hammer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools">
    Specify tool schemas, write effective descriptions, and control when Claude calls your tools.
  </Card>
</CardGroup>


---
title: Server tools
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools
description: "Work with Anthropic-executed tools: server_tool_use blocks, pause_turn continuation, mixed server and client tool turns, and domain filtering."
---

Server-executed tools share these mechanics: the `server_tool_use` block, `pause_turn` continuation, turns that mix server and client tools, Zero Data Retention (ZDR) eligibility, and domain filtering. For individual tools, see the [tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference).


## The server\_tool\_use block

Source: https://platform.claude.com/llms-full.txt#the-server-tool-use-block

The `server_tool_use` block appears in Claude's response when a server-executed tool runs. Its `id` field uses the `srvtoolu_` prefix to distinguish it from client tool calls:

The API executes the tool internally. You see the call and its result in the response, but you don't handle execution. Unlike client `tool_use` blocks, you don't need to respond with a `tool_result`. The tool's result block (for example, `web_search_tool_result` for web search) follows the `server_tool_use` block in the same assistant turn, paired by `tool_use_id`. If Claude calls one of your client tools at the same time, the `server_tool_use` block appears without its result, and the response ends with `stop_reason: "tool_use"`. The API runs the tool when you return the client `tool_result` blocks in your next request.


## The server-side loop and pause\_turn

Source: https://platform.claude.com/llms-full.txt#the-server-side-loop-and-pause-turn

When using server tools such as web search, the API executes tool calls in a server-side agentic loop. On a long-running turn, the API might pause that loop and return a `pause_turn` stop reason.

Here's how to handle the `pause_turn` stop reason:

<CodeGroup>
  ```bash cURL
  # Initial request. If "stop_reason" in the response is "pause_turn", continue
  # the turn by re-sending the request with the assistant content appended to messages.
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
          "content": "Search for comprehensive information about quantum computing breakthroughs in 2025"
        }
      ],
      "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}]
    }'

bash CLI
  # Initial request. If "stop_reason" in the output is "pause_turn", re-run with
  # the assistant content appended to messages (see the SDK tabs).
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tools:
    - {type: web_search_20250305, name: web_search, max_uses: 10}
  messages:
    - {role: user, content: "Search for comprehensive information about quantum computing breakthroughs in 2025"}
  YAML

python Python
  client = anthropic.Anthropic()

  # Initial request with web search
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": "Search for comprehensive information about quantum computing breakthroughs in 2025",
          }
      ],
      tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
  )

  # Check if the response has pause_turn stop reason
  if response.stop_reason == "pause_turn":
      # Continue the conversation with the paused content
      messages = [
          {
              "role": "user",
              "content": "Search for comprehensive information about quantum computing breakthroughs in 2025",
          },
          {"role": "assistant", "content": response.content},
      ]

      # Send the continuation request
      continuation = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          messages=messages,
          tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
      )

      print(continuation)
  else:
      print(response)

typescript TypeScript
  const client = new Anthropic();

  // Initial request with web search
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content:
          "Search for comprehensive information about quantum computing breakthroughs in 2025"
      }
    ],
    tools: [
      {
        type: "web_search_20250305",
        name: "web_search",
        max_uses: 10
      }
    ]
  });

  // Check if the response has pause_turn stop reason
  if (response.stop_reason === "pause_turn") {
    // Continue the conversation with the paused content
    const messages: Anthropic.MessageParam[] = [
      {
        role: "user",
        content:
          "Search for comprehensive information about quantum computing breakthroughs in 2025"
      },
      { role: "assistant", content: response.content }
    ];

    // Send the continuation request
    const continuation = await client.messages.create({
      model: "claude-opus-5",
      max_tokens: 1024,
      messages,
      tools: [
        {
          type: "web_search_20250305",
          name: "web_search",
          max_uses: 10
        }
      ]
    });

    console.log(continuation);
  } else {
    console.log(response);
  }

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [
          new() {
              Role = Role.User,
              Content = "Search for comprehensive information about quantum computing breakthroughs in 2025"
          }
      ],
      Tools = [new ToolUnion(new WebSearchTool20250305 { MaxUses = 10 })]
  };

  var response = await client.Messages.Create(parameters);

  if (response.StopReason?.Value() == StopReason.PauseTurn)
  {
      // Continue the conversation with the paused content
      var continuationParams = new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages = [
              new() {
                  Role = Role.User,
                  Content = "Search for comprehensive information about quantum computing breakthroughs in 2025"
              },
              new() {
                  Role = Role.Assistant,
                  Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList()
              }
          ],
          Tools = [new ToolUnion(new WebSearchTool20250305 { MaxUses = 10 })]
      };

      var continuation = await client.Messages.Create(continuationParams);
      Console.WriteLine(continuation);
  }
  else
  {
      Console.WriteLine(response);
  }

go Go
  client := anthropic.NewClient()

  webSearchTool := []anthropic.ToolUnionParam{
  	{OfWebSearchTool20250305: &anthropic.WebSearchTool20250305Param{
  		MaxUses: anthropic.Int(10),
  	}},
  }

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Search for comprehensive information about quantum computing breakthroughs in 2025")),
  	},
  	Tools: webSearchTool,
  })
  if err != nil {
  	log.Fatal(err)
  }

  if response.StopReason == anthropic.StopReasonPauseTurn {
  	// Pass the paused response back as-is so Claude can continue the turn
  	continuation, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 1024,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Search for comprehensive information about quantum computing breakthroughs in 2025")),
  			response.ToParam(),
  		},
  		Tools: webSearchTool,
  	})
  	if err != nil {
  		log.Fatal(err)
  	}
  	fmt.Println(continuation)
  } else {
  	fmt.Println(response)
  }

java Java
  import com.anthropic.models.messages.StopReason;
  import com.anthropic.models.messages.WebSearchTool20250305;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addUserMessage("Search for comprehensive information about quantum computing breakthroughs in 2025")
          .addTool(WebSearchTool20250305.builder()
              .maxUses(10L)
              .build())
          .build();

      Message response = client.messages().create(params);

      if (response.stopReason().isPresent()
              && response.stopReason().get().equals(StopReason.PAUSE_TURN)) {
          MessageCreateParams continuationParams = MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024L)
              .addUserMessage("Search for comprehensive information about quantum computing breakthroughs in 2025")
              .addMessage(response)
              .addTool(WebSearchTool20250305.builder()
                  .maxUses(10L)
                  .build())
              .build();

          Message continuation = client.messages().create(continuationParams);
          IO.println(continuation);
      } else {
          IO.println(response);
      }
  }

php PHP
  $client = new Client();

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => 'Search for comprehensive information about quantum computing breakthroughs in 2025'
          ]
      ],
      model: 'claude-opus-5',
      tools: [
          [
              'type' => 'web_search_20250305',
              'name' => 'web_search',
              'max_uses' => 10
          ]
      ],
  );

  if ($response->stopReason === 'pause_turn') {
      $messages = [
          [
              'role' => 'user',
              'content' => 'Search for comprehensive information about quantum computing breakthroughs in 2025'
          ],
          [
              'role' => 'assistant',
              'content' => $response->content
          ]
      ];

      $continuation = $client->messages->create(
          maxTokens: 1024,
          messages: $messages,
          model: 'claude-opus-5',
          tools: [
              [
                  'type' => 'web_search_20250305',
                  'name' => 'web_search',
                  'max_uses' => 10
              ]
          ],
      );

      echo $continuation;
  } else {
      echo $response;
  }

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content:
          "Search for comprehensive information about quantum computing breakthroughs in 2025"
      }
    ],
    tools: [
      {
        type: "web_search_20250305",
        name: "web_search",
        max_uses: 10
      }
    ]
  )

  if response.stop_reason == :pause_turn
    messages = [
      {
        role: "user",
        content: "Search for comprehensive information about quantum computing breakthroughs in 2025"
      },
      {
        role: "assistant",
        content: response.content
      }
    ]

    continuation = client.messages.create(
      model: "claude-opus-5",
      max_tokens: 1024,
      messages: messages,
      tools: [
        {
          type: "web_search_20250305",
          name: "web_search",
          max_uses: 10
        }
      ]
    )

    puts continuation
  else
    puts response
  end
  ```
</CodeGroup>

When handling `pause_turn`:

* **Continue the conversation:** Pass the paused response back as-is in a subsequent request to let Claude continue its turn.
* **Preserve tool state:** Include the same tools in the continuation request. A paused turn can end with a `server_tool_use` block whose tool has not run yet, and the API returns a validation error if that tool is missing from the continuation.
* **Repeat as needed:** A continued turn can pause again. Check `stop_reason` on each response and continue until you get a different stop reason, capping the number of continuations as you would any retry loop.

For the other `stop_reason` values and general handling patterns, see [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons).


## Mixing server tools and client tools in one turn

Source: https://platform.claude.com/llms-full.txt#mixing-server-tools-and-client-tools-in-one-turn

Claude can call a server tool and a client tool in the same group of parallel tool calls, for example, `web_fetch` together with a user-defined tool. A client tool is any tool that your code executes and that produces a `tool_use` block, whether it is user-defined or an Anthropic-schema client tool such as the [Bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool). When that happens, the API does not run the server tool. It returns immediately so that you can run the client tool first:

* `stop_reason` is `"tool_use"`, not `"pause_turn"`.
* `content` contains the `server_tool_use` block and the client `tool_use` block, but no result block for the server tool: that call is not finished.
* There is no other marker. Detect the state by looking for a `server_tool_use` block whose `id` has no matching result block in the response. An `mcp_tool_use` block from the [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector) behaves the same way. Server tool calls that already have their result block in the same response are complete and need nothing from you.

<Note>
  With [programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling), the same response shape means something different. The client `tool_use` block comes from code that is running in the `code_execution` tool rather than from Claude directly, and its `caller` field names the `code_execution` block that called it. That code has already started: it is paused waiting for your `tool_result` blocks, and sending them resumes the execution instead of starting a deferred tool. The `code_execution` block's own result block arrives once the code finishes, which can take more than one round of tool results. The follow-up user message itself is the same in both cases; with programmatic tool calling, also pass back the `id` from the response's `container` field, as that page shows.
</Note>

To continue the turn, run the client tools and send a user message whose content is only the `tool_result` blocks, one for each `tool_use` block in that response. Keep the same `tools` array: a resume request that no longer defines the waiting server tool fails with a 400 whose message ends ``but no `web_fetch` tool was provided``.

The API attaches your results to the still-open assistant turn, runs the deferred server tool (for paused code execution, resumes it), and then lets Claude continue. For a server tool Claude called directly, the next response begins with the result block that answers the previous response's `server_tool_use` `id`, followed by the newly generated content and a fresh `stop_reason`:

A `server_tool_use` block and its result block pair up by `tool_use_id`, not by position: in this flow they arrive in two different responses, and the `server_tool_use` block is not repeated in the second one. On later requests, keep the whole exchange in your `messages` array in order: the first response as an `assistant` message, the `tool_result` user message, and then the next response as another `assistant` message, the same way you accumulate any other tool-use exchange.

<Warning>
  The follow-up user message must contain nothing except `tool_result` blocks. A block added after the results, such as text, tells the API that the assistant turn is over. For a server tool Claude called directly, that leaves the turn with an unresolved server tool call, and the request fails with a 400 `invalid_request_error`:

  ```text wrap
  `web_fetch` tool use with id `srvtoolu_01HxbWnMRmbWyMfUtJKC45rA` was found without a corresponding `web_fetch_tool_result` block

text wrap
  `tool_use` ids were found without `tool_result` blocks immediately after: toolu_01PjgRJLbXrXEMZwDNYLnBqk. Each `tool_use` block must have a corresponding `tool_result` block in the next message.

bash cURL
  # If "stop_reason" is "tool_use" and a server_tool_use block has no matching
  # result block, that call is not finished. Run the client tools, then POST
  # again with one more user message containing only their tool_result blocks
  # and the same tools array (see the SDK tabs).
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
          "content": "Summarize https://example.com/article and run uname -a to tell me what system this is on."
        }
      ],
      "tools": [
        {"type": "web_fetch_20250910", "name": "web_fetch", "max_uses": 5},
        {
          "name": "run_command",
          "description": "Run a shell command on this computer and return its output.",
          "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string", "description": "The command to run"}},
            "required": ["command"]
          }
        }
      ]
    }'

bash CLI
  # If "stop_reason" is "tool_use" and a server_tool_use block has no matching
  # result block, run the client tools and re-run with a user message of only
  # their tool_result blocks appended (see the SDK tabs).
  ant messages create <<'YAML'
  model: claude-opus-4-8
  max_tokens: 1024
  messages:
    - role: user
      content: "Summarize https://example.com/article and run uname -a to tell me what system this is on."
  tools:
    - {type: web_fetch_20250910, name: web_fetch, max_uses: 5}
    - name: run_command
      description: Run a shell command on this computer and return its output.
      input_schema:
        type: object
        properties:
          command: {type: string, description: The command to run}
        required: [command]
  YAML

python Python
  client = anthropic.Anthropic()

  tools = [
      {"type": "web_fetch_20250910", "name": "web_fetch", "max_uses": 5},
      {
          "name": "run_command",
          "description": "Run a shell command on this computer and return its output.",
          "input_schema": {
              "type": "object",
              "properties": {
                  "command": {"type": "string", "description": "The command to run"}
              },
              "required": ["command"],
          },
      },
  ]
  messages = [
      {
          "role": "user",
          "content": "Summarize https://example.com/article and run uname -a to tell me what system this is on.",
      }
  ]

  response = client.messages.create(
      model="claude-opus-4-8", max_tokens=1024, tools=tools, messages=messages
  )

  tool_results = [
      {
          "type": "tool_result",
          "tool_use_id": block.id,
          # Run your tool here. This example returns a fixed string.
          "content": "Linux demo-host 6.8.0-52-generic x86_64 GNU/Linux",
      }
      for block in response.content
      if block.type == "tool_use"
  ]

  if response.stop_reason == "tool_use" and tool_results:
      # A server_tool_use block with no result block in this response is not finished; its result arrives in a later response.
      # Send back only the client tool_result blocks, with the same tools.
      continuation = client.messages.create(
          model="claude-opus-4-8",
          max_tokens=1024,
          tools=tools,
          messages=[
              *messages,
              {"role": "assistant", "content": response.content},
              {"role": "user", "content": tool_results},
          ],
      )
      # If a web_fetch was deferred, it runs on this request and its
      # web_fetch_tool_result is the first block of continuation.content.
      print(continuation)
  else:
      print(response)

typescript TypeScript
  const client = new Anthropic();

  const webFetchTool = {
    type: "web_fetch_20250910",
    name: "web_fetch",
    max_uses: 5
  } as const;
  const runCommandTool: Anthropic.Tool = {
    name: "run_command",
    description: "Run a shell command on this computer and return its output.",
    input_schema: {
      type: "object" as const,
      properties: {
        command: { type: "string", description: "The command to run" }
      },
      required: ["command"]
    }
  };
  const messages: Anthropic.MessageParam[] = [
    {
      role: "user",
      content:
        "Summarize https://example.com/article and run uname -a to tell me what system this is on."
    }
  ];

  const response = await client.messages.create({
    model: "claude-opus-4-8",
    max_tokens: 1024,
    tools: [webFetchTool, runCommandTool],
    messages
  });

  const toolResults: Anthropic.ToolResultBlockParam[] = [];
  for (const block of response.content) {
    if (block.type === "tool_use") {
      toolResults.push({
        type: "tool_result",
        tool_use_id: block.id,
        // Run your tool here. This example returns a fixed string.
        content: "Linux demo-host 6.8.0-52-generic x86_64 GNU/Linux"
      });
    }
  }

  if (response.stop_reason === "tool_use" && toolResults.length > 0) {
    // A server_tool_use block with no result block in this response is not finished; its result arrives in a later response.
    // Send back only the client tool_result blocks, with the same tools.
    const continuation = await client.messages.create({
      model: "claude-opus-4-8",
      max_tokens: 1024,
      tools: [webFetchTool, runCommandTool],
      messages: [
        ...messages,
        { role: "assistant", content: response.content },
        { role: "user", content: toolResults }
      ]
    });
    // If a web_fetch was deferred, it runs on this request and its
    // web_fetch_tool_result is the first block of continuation.content.
    console.log(continuation);
  } else {
    console.log(response);
  }

csharp C#
  AnthropicClient client = new();

  List<ToolUnion> tools =
  [
      new ToolUnion(new WebFetchTool20250910() { MaxUses = 5 }),
      new ToolUnion(new Tool()
      {
          Name = "run_command",
          Description = "Run a shell command on this computer and return its output.",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["command"] = JsonSerializer.SerializeToElement(
                      new { type = "string", description = "The command to run" }
                  ),
              },
              Required = ["command"],
          },
      }),
  ];
  MessageParam userMessage = new()
  {
      Role = Role.User,
      Content = "Summarize https://example.com/article and run uname -a to tell me what system this is on."
  };

  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus4_8,
      MaxTokens = 1024,
      Tools = tools,
      Messages = [userMessage]
  });

  var toolResults = new List<ContentBlockParam>();
  foreach (var block in response.Content)
  {
      if (block.TryPickToolUse(out var toolUse))
      {
          toolResults.Add(new ContentBlockParam(new ToolResultBlockParam()
          {
              ToolUseID = toolUse.ID,
              // Run your tool here. This example returns a fixed string.
              Content = "Linux demo-host 6.8.0-52-generic x86_64 GNU/Linux",
          }));
      }
  }

  if (response.StopReason?.Value() == StopReason.ToolUse && toolResults.Count > 0)
  {
      // A server_tool_use block with no result block in this response is not finished; its result arrives in a later response.
      // Send back only the client tool_result blocks, with the same tools.
      var continuation = await client.Messages.Create(new MessageCreateParams
      {
          Model = Model.ClaudeOpus4_8,
          MaxTokens = 1024,
          Tools = tools,
          Messages =
          [
              userMessage,
              new()
              {
                  Role = Role.Assistant,
                  Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList()
              },
              new() { Role = Role.User, Content = new MessageParamContent(toolResults) }
          ]
      });
      // If a web_fetch was deferred, it runs on this request and its
      // web_fetch_tool_result is the first block of continuation.Content.
      Console.WriteLine(continuation);
  }
  else
  {
      Console.WriteLine(response);
  }

go Go
  client := anthropic.NewClient()

  tools := []anthropic.ToolUnionParam{
  	{OfWebFetchTool20250910: &anthropic.WebFetchTool20250910Param{
  		MaxUses: anthropic.Int(5),
  	}},
  	{OfTool: &anthropic.ToolParam{
  		Name:        "run_command",
  		Description: anthropic.String("Run a shell command on this computer and return its output."),
  		InputSchema: anthropic.ToolInputSchemaParam{
  			Properties: map[string]any{
  				"command": map[string]any{
  					"type":        "string",
  					"description": "The command to run",
  				},
  			},
  			Required: []string{"command"},
  		},
  	}},
  }
  userMessage := anthropic.NewUserMessage(anthropic.NewTextBlock("Summarize https://example.com/article and run uname -a to tell me what system this is on."))

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus4_8,
  	MaxTokens: 1024,
  	Tools:     tools,
  	Messages:  []anthropic.MessageParam{userMessage},
  })
  if err != nil {
  	log.Fatal(err)
  }

  var toolResults []anthropic.ContentBlockParamUnion
  for _, block := range response.Content {
  	if toolUse, ok := block.AsAny().(anthropic.ToolUseBlock); ok {
  		// Run your tool here. This example returns a fixed string.
  		output := "Linux demo-host 6.8.0-52-generic x86_64 GNU/Linux"
  		toolResults = append(toolResults, anthropic.NewToolResultBlock(toolUse.ID, output, false))
  	}
  }

  if response.StopReason == anthropic.StopReasonToolUse && len(toolResults) > 0 {
  	// A server_tool_use block with no result block in this response is not finished; its result arrives in a later response.
  	// Send back only the client tool_result blocks, with the same tools.
  	continuation, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus4_8,
  		MaxTokens: 1024,
  		Tools:     tools,
  		Messages: []anthropic.MessageParam{
  			userMessage,
  			response.ToParam(),
  			anthropic.NewUserMessage(toolResults...),
  		},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}
  	// If a web_fetch was deferred, it runs on this request and its
  	// web_fetch_tool_result is the first block of continuation.Content.
  	fmt.Println(continuation)
  } else {
  	fmt.Println(response)
  }

java Java
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      Tool runCommandTool = Tool.builder()
          .name("run_command")
          .description("Run a shell command on this computer and return its output.")
          .inputSchema(Tool.InputSchema.builder()
              .properties(JsonValue.from(Map.of(
                  "command", Map.of("type", "string", "description", "The command to run")
              )))
              .putAdditionalProperty("required", JsonValue.from(List.of("command")))
              .build())
          .build();
      String prompt = "Summarize https://example.com/article and run uname -a to tell me what system this is on.";

      Message response = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_4_8)
          .maxTokens(1024L)
          .addTool(WebFetchTool20250910.builder().maxUses(5L).build())
          .addTool(runCommandTool)
          .addUserMessage(prompt)
          .build());

      List<ContentBlockParam> toolResults = new ArrayList<>();
      for (ContentBlock block : response.content()) {
          block.toolUse().ifPresent(toolUse -> toolResults.add(ContentBlockParam.ofToolResult(
              ToolResultBlockParam.builder()
                  .toolUseId(toolUse.id())
                  // Run your tool here. This example returns a fixed string.
                  .content("Linux demo-host 6.8.0-52-generic x86_64 GNU/Linux")
                  .build()
          )));
      }

      boolean isToolUse = response.stopReason()
          .map(StopReason.TOOL_USE::equals)
          .orElse(false);
      if (isToolUse && !toolResults.isEmpty()) {
          // A server_tool_use block with no result block in this response is not finished; its result arrives in a later response.
          // Send back only the client tool_result blocks, with the same tools.
          Message continuation = client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_4_8)
              .maxTokens(1024L)
              .addTool(WebFetchTool20250910.builder().maxUses(5L).build())
              .addTool(runCommandTool)
              .addUserMessage(prompt)
              .addMessage(response)
              .addUserMessageOfBlockParams(toolResults)
              .build());
          // If a web_fetch was deferred, it runs on this request and its
          // web_fetch_tool_result is the first block of continuation.content().
          IO.println(continuation);
      } else {
          IO.println(response);
      }
  }

php PHP
  $client = new Client();

  $tools = [
      ['type' => 'web_fetch_20250910', 'name' => 'web_fetch', 'max_uses' => 5],
      [
          'name' => 'run_command',
          'description' => 'Run a shell command on this computer and return its output.',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'command' => ['type' => 'string', 'description' => 'The command to run']
              ],
              'required' => ['command']
          ]
      ]
  ];
  $userMessage = ['role' => 'user', 'content' => 'Summarize https://example.com/article and run uname -a to tell me what system this is on.'];

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [$userMessage],
      model: 'claude-opus-4-8',
      tools: $tools,
  );

  $toolResults = [];
  foreach ($response->content as $block) {
      if ($block->type === 'tool_use') {
          $toolResults[] = [
              'type' => 'tool_result',
              'tool_use_id' => $block->id,
              // Run your tool here. This example returns a fixed string.
              'content' => 'Linux demo-host 6.8.0-52-generic x86_64 GNU/Linux'
          ];
      }
  }

  if ($response->stopReason === 'tool_use' && count($toolResults) > 0) {
      // A server_tool_use block with no result block in this response is not finished; its result arrives in a later response.
      // Send back only the client tool_result blocks, with the same tools.
      $continuation = $client->messages->create(
          maxTokens: 1024,
          messages: [
              $userMessage,
              ['role' => 'assistant', 'content' => $response->content],
              ['role' => 'user', 'content' => $toolResults],
          ],
          model: 'claude-opus-4-8',
          tools: $tools,
      );
      // If a web_fetch was deferred, it runs on this request and its
      // web_fetch_tool_result is the first block of $continuation->content.
      echo $continuation;
  } else {
      echo $response;
  }

ruby Ruby
  client = Anthropic::Client.new

  tools = [
    { type: "web_fetch_20250910", name: "web_fetch", max_uses: 5 },
    {
      name: "run_command",
      description: "Run a shell command on this computer and return its output.",
      input_schema: {
        type: "object",
        properties: {
          command: { type: "string", description: "The command to run" }
        },
        required: ["command"]
      }
    }
  ]
  user_message = {
    role: "user",
    content: "Summarize https://example.com/article and run uname -a to tell me what system this is on."
  }

  response = client.messages.create(
    model: "claude-opus-4-8",
    max_tokens: 1024,
    tools: tools,
    messages: [user_message]
  )

  tool_results = []
  response.content.each do |block|
    next unless block.type == :tool_use

    tool_results << {
      type: "tool_result",
      tool_use_id: block.id,
      # Run your tool here. This example returns a fixed string.
      content: "Linux demo-host 6.8.0-52-generic x86_64 GNU/Linux"
    }
  end

  if response.stop_reason == :tool_use && !tool_results.empty?
    # A server_tool_use block with no result block in this response is not finished; its result arrives in a later response.
    # Send back only the client tool_result blocks, with the same tools.
    continuation = client.messages.create(
      model: "claude-opus-4-8",
      max_tokens: 1024,
      tools: tools,
      messages: [
        user_message,
        { role: "assistant", content: response.content },
        { role: "user", content: tool_results }
      ]
    )
    # If a web_fetch was deferred, it runs on this request and its
    # web_fetch_tool_result is the first block of continuation.content.
    puts continuation
  else
    puts response
  end
  ```
</CodeGroup>

This code is also correct when Claude does not mix the two kinds of call. A turn with only client `tool_use` blocks takes the same continuation path, and a turn with only server tool calls needs no client `tool_result` blocks from you: its result blocks are normally already present, and one that comes back suspended, such as a [`pause_turn` response](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#the-server-side-loop-and-pause-turn), is re-sent as-is instead.


## ZDR and allowed\_callers

Source: https://platform.claude.com/llms-full.txt#zdr-and-allowed-callers

The basic versions of web search (`web_search_20250305`) and web fetch (`web_fetch_20250910`) are eligible for [Zero Data Retention (ZDR)](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).

The `_20260209` and later versions with dynamic filtering are **not** ZDR-eligible by default because dynamic filtering relies on code execution internally.

To use a `_20260209` or later server tool with ZDR, disable dynamic filtering by setting `"allowed_callers": ["direct"]` on the tool:

This restricts the tool to direct invocation only, bypassing the internal code execution step.

`allowed_callers` controls how a tool can be invoked: directly by Claude (`"direct"`), from inside a code execution container (for example, `"code_execution_20260120"`), or both. The `_20260209` versions of the web tools default to the code execution caller only; earlier versions default to `["direct"]`. On models that don't support programmatic tool calling, these versions require `allowed_callers: ["direct"]`; without it the API returns a validation error that says to set it.

<Note>
  Even when web fetch is used in a ZDR-eligible configuration, website publishers might retain any parameters passed to the URL if Claude fetches content from their site.
</Note>


## Domain filtering

Source: https://platform.claude.com/llms-full.txt#domain-filtering

Server tools that access the web accept `allowed_domains` and `blocked_domains` parameters to control which domains Claude can reach. Both are fields on the tool object:

When using domain filters:

* Domains should not include the HTTP/HTTPS scheme (use `example.com` instead of `https://example.com`).
* Subdomains are automatically included (`example.com` covers `docs.example.com`).
* Specific subdomains restrict results to only that subdomain (`docs.example.com` returns only results from that subdomain, not from `example.com` or `api.example.com`).
* Subpaths are supported for web search and match anything after the path (`example.com/blog` matches `example.com/blog/post-1`).
* Web fetch matches on the domain only: an entry that includes a path never matches a web fetch URL.
* You can use either `allowed_domains` or `blocked_domains`, but not both in the same request.

**Wildcard support:**

* Wildcards (`*`) are not allowed in the domain itself, only in the path after it.
* Valid: `example.com/*`, `example.com/*/articles`
* Invalid: `*.example.com`, `ex*.com`

Invalid domain formats are rejected at request time with a 400 `invalid_request_error`.

<Note>
  Request-level domain restrictions work together with any organization-level domain restrictions configured in Claude Console. Request-level `allowed_domains` must be a subset of the organization-level allowed list; entries outside it cause the API to return a validation error. A request-level allowed list that includes a domain your organization blocks is rejected with a `400` error that names the conflicting entries.
</Note>

<Warning>
  Unicode characters in domain names can bypass domain filters through homograph attacks: `аmazon.com` (with a Cyrillic `а`) looks identical to `amazon.com` but is a different domain. Use ASCII-only domain names in allow and block lists, and audit existing entries for non-ASCII characters.
</Warning>

[Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) uses the same `allowed_domains` and `blocked_domains` fields on the `web_search` and `web_fetch` entries of the agent toolset. On Managed Agents, each list holds at most 64 entries, domains listed for `web_fetch` cannot include a path, and fields specific to the Messages API tools, such as `max_uses`, `citations`, and `cache_control`, are not available. See [Restrict web search and web fetch domains](https://platform.claude.com/docs/en/managed-agents/tools#restrict-web-search-and-web-fetch-domains) for the full rules.

Organization-level web search and web fetch settings in the Claude Console apply to Messages API requests only; they do not apply to Managed Agents sessions, which use only the per-tool lists on the agent toolset.


## Dynamic filtering with code execution

Source: https://platform.claude.com/llms-full.txt#dynamic-filtering-with-code-execution

The `_20260209` and later versions of web search and web fetch use code execution internally to apply dynamic filters against search results.

<Note>
  You don't need to add a `code_execution` tool for these versions: when dynamic filtering runs, the API provisions code execution for the request automatically, and both tools share a single execution container. If you do include one, use `code_execution_20260120` or later; the API rejects older code execution versions alongside these web tool versions.
</Note>


## Streaming server-tool events

Source: https://platform.claude.com/llms-full.txt#streaming-server-tool-events

Server-tool events stream as part of the normal server-sent events (SSE) flow. A `server_tool_use` block that Claude calls directly streams like a client `tool_use` block: a `content_block_start` event followed by `input_json_delta` events. The result block arrives complete in a single `content_block_start` event, with no deltas.

See [Streaming](https://platform.claude.com/docs/en/build-with-claude/streaming) for the full event reference. Individual tool pages document tool-specific event names where they differ.
