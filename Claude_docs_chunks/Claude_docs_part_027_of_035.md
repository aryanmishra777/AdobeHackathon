# platform.claude.com Documentation (Part 27 of 35)

## Breaking changes

Source: https://platform.claude.com/llms-full.txt#breaking-changes

### Forced tool use is not supported

Claude Fable 5.1 and Claude Mythos 5.1 don't support forced tool use. `tool_choice` set to `{"type": "any"}` or `{"type": "tool", "name": "..."}` returns a 400 `invalid_request_error`:

```text wrap
tool_choice: type "tool" and "any" are not supported for this model.
```

`tool_choice: {"type": "auto"}` (the default) and `{"type": "none"}` are unchanged. The same validation applies to the [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) endpoint.

Thinking is always on for these models, and a forced tool call would skip it. The model would write its working-out into the tool arguments instead, which lowers argument quality. For schema-valid JSON, keep `tool_choice: {"type": "auto"}` and set `strict: true` with [strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use), or move the schema to [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs). To make the model call a tool rather than reply in text, state in the prompt when the tool applies (for example, "Use the `get_weather` tool to answer"). Claude Fable 5.1 follows explicit tool instructions reliably.

### Earlier models can't read Claude Fable 5.1 thinking blocks

Every thinking block records which model produced it, and it's preserved in one direction only: Claude Fable 5.1 reads earlier models' thinking blocks, and no earlier model reads Claude Fable 5.1's. A conversation that moves onto Claude Fable 5.1 (from Claude Opus 5, Claude Fable 5, or any earlier Claude model) keeps its reasoning. A conversation that moves from Claude Fable 5.1 to any of those models loses it for the turns that run there.

When a request carries a block the target model can't read (a router or fallback that switches models mid-conversation, for example), the API drops the block before the model sees it. Dropped blocks don't count toward `input_tokens` and aren't billed. With the `thinking-binding-controls-2026-08-01` beta header, the drop is reported in a top-level `input_transformations` array. Without it, the drop is silent. See [Preserved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-for-model).

### Editing earlier turns invalidates thinking blocks

Modifying anything before a Claude Fable 5.1 thinking block (the `system` prompt, the `tools`, or an earlier message) results in an error on the next request, or in the block being dropped if you opt into that. Claude Mythos 5.1 doesn't run this check. Claude Code, claude.ai, [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview), and the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) keep that prefix intact for you. If your code builds the `messages` array itself, check it before you migrate: [Preserved thinking](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking) walks through the check and each fix. The check is enforced for new accounts created on or after August 31, 2026. For accounts created earlier, the API records the mismatch but acts on it only when the request sets `thinking.block_binding.prefix_mismatch_behavior`.

These patterns invalidate every later thinking block:

* Editing, reordering, or removing an earlier turn while keeping later ones.
* Injecting per-request text into an earlier turn (a reminder or status line) that you remove on the next request.
* Rebuilding the top-level `system` prompt or `tools` array between requests in the same conversation.
* An image or document URL that serves different bytes on a later request (the check covers the bytes, not the URL, so a rotating signed URL for the same file is fine).

These keep later blocks valid: removing a leading run of thinking blocks (oldest first), letting server-side compaction or context editing trim the history, moving `cache_control` markers, and changing `effort` between requests. Removing a thinking block from anywhere other than the start of the run invalidates every thinking block after it.

Where the check is enforced, a request that replays an invalidated block is rejected with a 400 whose message says `The block is bound to a different conversation`. To drop the block and continue instead, send the `thinking-binding-controls-2026-08-01` beta header with `thinking.block_binding.prefix_mismatch_behavior: "drop_block"`. The drop is reported in `input_transformations` with `reason: "prefix_binding_mismatch"`.

To keep thinking valid across a long session, treat the conversation as append-only. Add instructions with a [mid-conversation system message](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages) ([turn-scoped](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1#turn-scoped-system-messages-beta) if it should apply to one turn only) and change tools with [mid-conversation tool changes](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#mid-conversation-tool-changes) rather than editing `system` or `tools`. Trim context with server-side [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) or [compaction](https://platform.claude.com/docs/en/build-with-claude/compaction), which don't count as edits. These patterns also keep the [prompt cache](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) warm. To find out whether your integration edits history, run a session with `prefix_mismatch_behavior: "drop_block"` and log `input_transformations`: the [migration guide](https://platform.claude.com/docs/en/models/fable-5-1/migration-guide#fable-5-1-preserved-thinking) has the three-step check. See [Preserved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-in-conversation) for the full rules.


## New features

Source: https://platform.claude.com/llms-full.txt#new-features

### Change effort mid-conversation (beta)

On Claude Fable 5.1 you can change the [effort](https://platform.claude.com/docs/en/build-with-claude/effort) level mid-conversation without invalidating the prompt cache. Raise it for a hard step and lower it for routine ones. Per-message effort is in beta: include the `mid-conversation-output-config-2026-07-01` beta header. Claude Fable 5.1, Claude Mythos 5.1, and Claude Opus 5 support it on the Claude API.

<CodeGroup>
  ```bash cURL
  # Effort-only system message: the new level takes effect from the next user turn.
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: mid-conversation-output-config-2026-07-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-fable-5-1",
      "max_tokens": 4096,
      "output_config": {"effort": "high"},
      "messages": [
        {"role": "user", "content": "Plan a migration from SQLite to PostgreSQL in three short steps."},
        {"role": "assistant", "content": "1. Export the SQLite data. 2. Create the PostgreSQL schema. 3. Import the data and verify row counts."},
        {"role": "system", "content": [], "output_config": {"effort": "low"}},
        {"role": "user", "content": "Summarize the plan in one sentence."}
      ]
    }'

bash CLI
  ant beta:messages create --beta mid-conversation-output-config-2026-07-01 \
    --transform 'content.#(type=="text").text' --raw-output <<'YAML'
  model: claude-fable-5-1
  max_tokens: 4096
  output_config:
    effort: high
  messages:
    - role: user
      content: Plan a migration from SQLite to PostgreSQL in three short steps.
    - role: assistant
      content: "1. Export the SQLite data. 2. Create the PostgreSQL schema. 3. Import the data and verify row counts."
    # Effort-only system message: the new level takes effect from the next user turn.
    - role: system
      content: []
      output_config:
        effort: low
    - role: user
      content: Summarize the plan in one sentence.
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.beta.messages.create(
      model="claude-fable-5-1",
      max_tokens=4096,
      output_config={"effort": "high"},
      messages=[
          {
              "role": "user",
              "content": "Plan a migration from SQLite to PostgreSQL in three short steps.",
          },
          {
              "role": "assistant",
              "content": "1. Export the SQLite data. 2. Create the PostgreSQL schema. 3. Import the data and verify row counts.",
          },
          # Effort-only system message: the new level takes effect from the next user turn.
          {"role": "system", "content": [], "output_config": {"effort": "low"}},
          {"role": "user", "content": "Summarize the plan in one sentence."},
      ],
      betas=["mid-conversation-output-config-2026-07-01"],
  )

  for block in response.content:
      if block.type == "text":
          print(block.text)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.beta.messages.create({
    model: "claude-fable-5-1",
    max_tokens: 4096,
    output_config: { effort: "high" },
    messages: [
      {
        role: "user",
        content: "Plan a migration from SQLite to PostgreSQL in three short steps."
      },
      {
        role: "assistant",
        content:
          "1. Export the SQLite data. 2. Create the PostgreSQL schema. 3. Import the data and verify row counts."
      },
      // Effort-only system message: the new level takes effect from the next user turn.
      { role: "system", content: [], output_config: { effort: "low" } },
      { role: "user", content: "Summarize the plan in one sentence." }
    ],
    betas: ["mid-conversation-output-config-2026-07-01"]
  });

  for (const block of response.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

csharp C#
  using Anthropic.Models.Beta;
  using Anthropic.Models.Beta.Messages;

  AnthropicClient client = new();

  var response = await client.Beta.Messages.Create(new MessageCreateParams
  {
      Model = "claude-fable-5-1",
      MaxTokens = 4096,
      OutputConfig = new() { Effort = Effort.High },
      Messages =
      [
          new() { Role = Role.User, Content = "Plan a migration from SQLite to PostgreSQL in three short steps." },
          new() { Role = Role.Assistant, Content = "1. Export the SQLite data. 2. Create the PostgreSQL schema. 3. Import the data and verify row counts." },
          // Effort-only system message: the new level takes effect from the next user turn.
          new()
          {
              Role = Role.System,
              Content = new([]),
              OutputConfig = new() { Effort = BetaSystemMessageOutputConfigEffort.Low },
          },
          new() { Role = Role.User, Content = "Summarize the plan in one sentence." },
      ],
      Betas = [AnthropicBeta.MidConversationOutputConfig2026_07_01],
  });

  foreach (var block in response.Content)
  {
      if (block.TryPickText(out var textBlock))
      {
          Console.WriteLine(textBlock.Text);
      }
  }

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.Background(), anthropic.BetaMessageNewParams{
  	Model:     "claude-fable-5-1",
  	MaxTokens: 4096,
  	OutputConfig: anthropic.BetaOutputConfigParam{
  		Effort: anthropic.BetaOutputConfigEffortHigh,
  	},
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Plan a migration from SQLite to PostgreSQL in three short steps.")),
  		{
  			Role:    anthropic.BetaMessageParamRoleAssistant,
  			Content: []anthropic.BetaContentBlockParamUnion{anthropic.NewBetaTextBlock("1. Export the SQLite data. 2. Create the PostgreSQL schema. 3. Import the data and verify row counts.")},
  		},
  		// Effort-only system message: the new level takes effect from the next user turn.
  		anthropic.NewBetaSystemMessage(anthropic.BetaSystemMessageOutputConfigParam{
  			Effort: anthropic.BetaSystemMessageOutputConfigEffortLow,
  		}),
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Summarize the plan in one sentence.")),
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaMidConversationOutputConfig2026_07_01},
  })
  if err != nil {
  	log.Fatal(err)
  }

  for _, block := range response.Content {
  	if textBlock, ok := block.AsAny().(anthropic.BetaTextBlock); ok {
  		fmt.Println(textBlock.Text)
  	}
  }

java Java
  import com.anthropic.models.beta.AnthropicBeta;
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.BetaMessageParam;
  import com.anthropic.models.beta.messages.BetaOutputConfig;
  import com.anthropic.models.beta.messages.BetaSystemMessageOutputConfig;
  import com.anthropic.models.beta.messages.MessageCreateParams;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model("claude-fable-5-1")
          .maxTokens(4096L)
          .addBeta(AnthropicBeta.MID_CONVERSATION_OUTPUT_CONFIG_2026_07_01)
          .outputConfig(BetaOutputConfig.builder()
              .effort(BetaOutputConfig.Effort.HIGH)
              .build())
          .addUserMessage("Plan a migration from SQLite to PostgreSQL in three short steps.")
          .addAssistantMessage("1. Export the SQLite data. 2. Create the PostgreSQL schema. 3. Import the data and verify row counts.")
          // Effort-only system message: the new level takes effect from the next user turn.
          .addMessage(BetaMessageParam.builder()
              .role(BetaMessageParam.Role.SYSTEM)
              .contentOfBetaContentBlockParams(List.of())
              .outputConfig(BetaSystemMessageOutputConfig.builder()
                  .effort(BetaSystemMessageOutputConfig.Effort.LOW)
                  .build())
              .build())
          .addUserMessage("Summarize the plan in one sentence.")
          .build();

      BetaMessage response = client.beta().messages().create(params);
      response.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  use Anthropic\Beta\AnthropicBeta;
  use Anthropic\Beta\Messages\BetaMessageParam;
  use Anthropic\Beta\Messages\BetaOutputConfig;
  use Anthropic\Beta\Messages\BetaSystemMessageOutputConfig;
  use Anthropic\Client;

  $client = new Client();

  $response = $client->beta->messages->create(
      model: 'claude-fable-5-1',
      maxTokens: 4096,
      outputConfig: BetaOutputConfig::with(effort: 'high'),
      messages: [
          BetaMessageParam::with(role: 'user', content: 'Plan a migration from SQLite to PostgreSQL in three short steps.'),
          BetaMessageParam::with(role: 'assistant', content: '1. Export the SQLite data. 2. Create the PostgreSQL schema. 3. Import the data and verify row counts.'),
          // Effort-only system message: the new level takes effect from the next user turn.
          BetaMessageParam::with(
              role: 'system',
              content: [],
              outputConfig: BetaSystemMessageOutputConfig::with(effort: 'low'),
          ),
          BetaMessageParam::with(role: 'user', content: 'Summarize the plan in one sentence.'),
      ],
      betas: [AnthropicBeta::MID_CONVERSATION_OUTPUT_CONFIG_2026_07_01],
  );

  foreach ($response->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, PHP_EOL;
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-fable-5-1",
    max_tokens: 4096,
    output_config: {effort: :high},
    messages: [
      {role: "user", content: "Plan a migration from SQLite to PostgreSQL in three short steps."},
      {role: "assistant", content: "1. Export the SQLite data. 2. Create the PostgreSQL schema. 3. Import the data and verify row counts."},
      # Effort-only system message: the new level takes effect from the next user turn.
      {role: "system", content: [], output_config: {effort: :low}},
      {role: "user", content: "Summarize the plan in one sentence."}
    ],
    betas: [Anthropic::AnthropicBeta::MID_CONVERSATION_OUTPUT_CONFIG_2026_07_01]
  )

  response.content.each do |block|
    puts block.text if block.type == :text
  end

json
{
  "role": "system",
  "clear_at": "next_user_message",
  "content": "Results have landed in your inbox. Check it before running more code."
}
```

### Progress updates between tool calls (beta)

Like Claude Fable 5, Claude Fable 5.1 writes short progress updates between tool calls on what it found and what it will do next, though fewer of them (see [Changed from Claude Fable 5](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1#changed-from-claude-fable-5)). Each update arrives as its own `thinking` block immediately before the tool call. Under the default `thinking.display` of `"omitted"` those blocks come back empty, like reasoning, so a long agentic turn can look silent to your users. What's new is the `display: "updates"` option: set it with the `thinking-display-updates-2026-08-18` beta header to receive the progress updates as text while reasoning stays hidden. Any `thinking` block with non-empty text is then a status line you can show the user. `"summarized"` returns them too, mixed with summarized reasoning. See [Progress updates between tool calls](https://platform.claude.com/docs/en/build-with-claude/thinking#progress-updates).

### Content provenance

Text generated by Claude Fable 5.1 and Claude Mythos 5.1 carries Anthropic's statistical text watermark on every platform where the model is available. Supported image, video, and audio files Claude produces (through the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool), for example) carry signed [C2PA](https://c2pa.org/) Content Credentials when you retrieve them through the [Files API](https://platform.claude.com/docs/en/build-with-claude/files) on the Claude API.

The watermark doesn't change the meaning, quality, or readability of the output. It adds no tokens or hidden characters, carries no information about you or your organization, and needs no changes to your requests or responses. For background, see [How Claude marks AI-generated content](https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content) and [How Claude's text watermark works](https://www.anthropic.com/news/claude-text-watermark).


## Behavior differences

Source: https://platform.claude.com/llms-full.txt#behavior-differences

### Changed from Claude Fable 5

Claude Fable 5.1 differs from Claude Fable 5 in several ways that show up without any code change. Each has a prompting fix in [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1):

* **Parallel tool calling is more variable.** Claude Fable 5.1 may issue one tool call per turn where Claude Fable 5 batched several. This shows up in long agent loops where the next independent reads are only implied: custom coding agents, bash-and-editor harnesses, computer use. The extra turns cost tokens, round trips, and wall-clock time but don't reduce answer quality. Requests naming several things to fetch still run in parallel. Add the one-line batching instruction from [Batch independent tool calls in agent loops](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#batch-independent-tool-calls-in-agent-loops).
* **Fewer progress updates during long tool runs.** The model writes less user-facing text between tool calls, especially at higher effort. Set `thinking.display` to `"updates"` (beta) to receive the [progress updates](https://platform.claude.com/docs/en/build-with-claude/thinking#progress-updates) it does write, and remove any prompt line that tells it to hold findings for the final response. If your UI depends on narration, ask explicitly for an opening line, periodic updates, and a closing recap. See [Ask for user-facing progress updates](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#ask-for-user-facing-progress-updates).
* **Answers from memory more often at `low` effort.** At the lowest effort level the model calls a search or retrieval tool less often. Raise effort for turns that need fresh information, including [mid-conversation](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1#change-effort-mid-conversation-beta), or add the verification nudge from [Search triggering at low effort](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#search-triggering-at-low-effort).
* **Denser prose in places.** In some cases its prose is denser than Claude Fable 5's, with longer sentences and fewer paragraph breaks. See [Writing density](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#writing-density).
* **Less formatting in chat.** The model uses bold, headers, and lists less than earlier Claude models, so anti-formatting rules written for those models can suppress structure the content needs. See [Formatting in chat](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#formatting-in-chat).
* **Unmarked quotations in summaries.** When summarizing documents, the model is more likely to reproduce passages of the source without marking them as quotations. See [Quoting retrieved sources](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#quoting-retrieved-sources).
* **Whole-file rewrites for small changes.** When editing text files, the model is more likely to rewrite the entire file than make a targeted edit. The result is usually the same, but the rewrite costs more output tokens and time. See [Prefer targeted edits over whole-file rewrites](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#prefer-targeted-edits-over-whole-file-rewrites).

### Unchanged from Claude Fable 5

These Messages API behaviors carry over from Claude Fable 5 unchanged:

* Adaptive thinking is always on. `thinking: {"type": "enabled"}` with `budget_tokens` and `thinking: {"type": "disabled"}` both return a 400 error. Omit `thinking` or send `{"type": "adaptive"}`.
* `thinking.display` defaults to `"omitted"`. `"summarized"` is available, and the raw chain of thought is never returned.
* Reasoning between tool calls appears in thinking blocks rather than text, and [interleaved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#interleaved-thinking) is automatic with no beta header.
* Prefilling the assistant response returns a 400 error.
* Non-default `temperature`, `top_p`, or `top_k` values return a 400 error.
* The minimum cacheable prompt length is 512 tokens.
* [Mid-conversation system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages) and tool changes are supported.


## Capability improvements

Source: https://platform.claude.com/llms-full.txt#capability-improvements-3

Claude Fable 5.1 improves on Claude Fable 5, and the gap is widest at higher [effort](https://platform.claude.com/docs/en/build-with-claude/effort) levels. The gains concentrate in six areas:

* **Agentic coding over long sessions**, including multi-file features, large refactors and migrations, debugging, and code review across sessions that run for hours.
* **Knowledge work with documents, spreadsheets, and slides**, taking an analysis from a first question to a finished document, live-formula spreadsheet, or slide deck built from a blank page.
* **Research and search**, with higher accuracy on multistep web research and deep-research tasks that follow up on what they find.
* **Vision**, reading dense charts, filings, and tables nested in PDFs, including with crop-and-zoom tools on charts.
* **Long-context work**, reasoning over and connecting details across the full [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows).
* **Computer use**, operating a browser and desktop applications more reliably and recovering from failed steps.

Multilingual performance is on par with Claude Fable 5.


## Refusals, fallback, and billing

Source: https://platform.claude.com/llms-full.txt#refusals-fallback-and-billing

Claude Fable 5.1 includes safety classifiers covering the same `stop_details` categories as Claude Fable 5, and everything in [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) applies. It can return `stop_reason: "refusal"`, so handle refusals and configure fallback.

* **Refusals:** a declined request returns HTTP 200 with `stop_reason: "refusal"` and a [`stop_details`](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#refusal-response) object naming the policy area that fired.
* **Fallback:** retry a refused request on another model with [server-side fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#server-side-fallback), the [SDK middleware](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#client-side-fallback), or your own retry. `fallbacks: "default"` (beta) retries a declined request on the model Anthropic recommends for that category. The permitted fallback targets for Claude Fable 5.1 are Claude Opus 4.8 and Claude Opus 5.
* **Billing:** you aren't billed for a refusal that arrives before any output, and, for Claude Fable 5.1, [fallback credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit) refunds the prompt-cache cost of switching models.


## Pricing

Source: https://platform.claude.com/llms-full.txt#pricing-10

Claude Fable 5.1 and Claude Mythos 5.1 are priced the same as Claude Fable 5, except for cache reads (prices in USD):

| Base input | 5m cache writes | 1h cache writes | Cache reads  | Output     |
| ---------- | --------------- | --------------- | ------------ | ---------- |
| $10 / MTok | $12.50 / MTok   | $20 / MTok      | $0.25 / MTok | $50 / MTok |

Cache reads (hits and refreshes) cost 0.025 times the base input price on these models, compared with 0.1 on other Claude models. Long agentic sessions that re-read a cached prefix pay a quarter of the Claude Fable 5 rate. Cache writes and the [512-token minimum cacheable prompt length](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#cache-limitations) are unchanged.

[Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing) is $5 USD per million input tokens and $25 USD per million output tokens. See [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) for data residency and tool pricing.


## Availability

Source: https://platform.claude.com/llms-full.txt#availability-2

Claude Fable 5.1 is available on:

* **Claude API:** all customers, as `claude-fable-5-1`.
* **AWS:** [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), as `anthropic.claude-fable-5-1`, and [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), as `claude-fable-5-1`.
* **Google Cloud:** [Claude on Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), as `claude-fable-5-1`.
* **Microsoft Foundry:** [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), on Anthropic infrastructure.

Claude Mythos 5.1 is offered only to approved customers in [Project Glasswing](https://anthropic.com/glasswing). For access, contact your Anthropic, AWS, or Google Cloud account team.

Claude Fable 5.1 and Claude Mythos 5.1 carry 30-day data retention and aren't available under zero data retention unless expressly authorized by Anthropic. Both are [Covered Models](https://support.claude.com/en/articles/15425695), like Claude Fable 5 and Claude Mythos 5. See [Model-specific data retention requirements](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements).


## Migrate from Claude Fable 5

Source: https://platform.claude.com/llms-full.txt#migrate-from-claude-fable-5

To migrate from Claude Fable 5, update your model ID:

<CodeGroup exclude="shell">
  ```python Python
  model = "claude-fable-5"  # Before
  model = "claude-fable-5-1"  # After

typescript TypeScript
  let model = "claude-fable-5"; // Before
  model = "claude-fable-5-1"; // After

csharp C#
  var model = "claude-fable-5"; // Before
  model = "claude-fable-5-1"; // After

go Go
  model := "claude-fable-5"  // Before
  model = "claude-fable-5-1" // After

java Java
  String model = "claude-fable-5"; // Before
  model = "claude-fable-5-1"; // After

php PHP
  $model = 'claude-fable-5'; // Before
  $model = 'claude-fable-5-1'; // After

ruby Ruby
  model = "claude-fable-5" # Before
  model = "claude-fable-5-1" # After
  ```
</CodeGroup>

Then review these items:

1. Remove any `tool_choice` of type `any` or `tool`. Move schema enforcement to [strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) with `tool_choice: {"type": "auto"}` or to [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
2. Pass thinking blocks back unchanged and keep the history append-only. If your code builds the `messages` array itself, run the [history-editing check](https://platform.claude.com/docs/en/models/fable-5-1/migration-guide#fable-5-1-preserved-thinking): move per-turn reminders you currently inject and delete to [turn-scoped system messages](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1#turn-scoped-system-messages-beta), move `system` and `tools` changes to mid-conversation system messages, trim context server-side or strip thinking blocks from turns you carry across a client-side summary, then pick a production [`prefix_mismatch_behavior`](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-thinking-controls) and monitor `input_transformations`.
3. Re-tune effort from the default (`high`), and consider [changing it mid-conversation](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1#change-effort-mid-conversation-beta) instead of holding one level for the whole session.
4. In agent loops, watch for one tool call per turn where Claude Fable 5 batched several, and add the per-turn note from [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1).
5. Re-run your evals. Refusal handling, fallback, fallback credit, and token counts carry over unchanged. Cache reads cost less (see [Pricing](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1#pricing)), and default behavior differs in the ways listed under [Changed from Claude Fable 5](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1#changed-from-claude-fable-5).

See the [migration guide](https://platform.claude.com/docs/en/models/fable-5-1/migration-guide) for step-by-step instructions, including from Claude Opus 5 and earlier models.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-103

<CardGroup cols={3}>
  <Card title="Models overview" icon="arrow-right" href="https://platform.claude.com/docs/en/models/overview">
    Specs and pricing for every current Claude model.
  </Card>

  <Card title="Migration guide" icon="code" href="https://platform.claude.com/docs/en/models/fable-5-1/migration-guide">
    Migrating from Claude Fable 5, Claude Opus 5, and earlier models.
  </Card>

  <Card title="Prompting Claude Fable 5.1" icon="terminal" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1">
    Prompting patterns specific to Claude Fable 5.1.
  </Card>
</CardGroup>


### Models > Claude Opus 5

---
title: Claude Opus 5
url: https://platform.claude.com/docs/en/models/opus-5/overview
description: "Claude Opus 5 at a glance: what it's for, model IDs on every platform, context window, output limits, pricing, availability, and the guides and resources for building with it."
---

**Latest.** Released July 24, 2026.

For complex agentic coding and enterprise work

Model ID: `claude-opus-5`

Context window: 1M tokens · Max output: 128K tokens · Input pricing: $5 / MTok · Output pricing: $25 / MTok

[Announcement](https://www.anthropic.com/news/claude-opus-5) · [What’s new](https://platform.claude.com/docs/en/models/opus-5/whats-new-opus-5) · [Migration guide](https://platform.claude.com/docs/en/models/opus-5/migration-guide)


## Overview

Source: https://platform.claude.com/llms-full.txt#overview-8

Claude Opus 5 is a step-change improvement over Claude Opus 4.8, with the largest gains in deep reasoning, agentic and long-horizon tasks, and test-time compute scaling. This page summarizes everything new in Claude Opus 5, including mid-conversation tool changes and two breaking changes for code running on Claude Opus 4.8: thinking is on by default, and thinking can be disabled only at effort `high` or below.

[What's new in Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/whats-new-opus-5)


## How it compares

Source: https://platform.claude.com/llms-full.txt#how-it-compares-2

| Model                                                                             | Context | Max output | Price / MTok | Latency  | Thinking             | Default effort | Knowledge cutoff |
| :-------------------------------------------------------------------------------- | :------ | :--------- | :----------- | :------- | :------------------- | :------------- | :--------------- |
| [Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/overview) | 1M      | 128K       | $10 / $50    | Slower   | Adaptive (always on) | `high`         | Jun 2026         |
| **Claude Opus 5** (this model)                                                    | 1M      | 128K       | $5 / $25     | Moderate | Adaptive             | `high`         | May 2026         |
| [Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/overview)   | 1M      | 128K       | $2 / $10     | Fast     | Adaptive             | `high`         | Jan 2026         |
| [Claude Haiku 4.5](https://platform.claude.com/docs/en/models/haiku-4-5/overview) | 200K    | 64K        | $1 / $5      | Fastest  | Extended             | —              | Feb 2025         |

* **Context:** 1M tokens is roughly 555k words or 2.5M Unicode characters on the current tokenizer (introduced with Claude Opus 4.7); models before it fit about 750k words in 1M tokens. 200k tokens is roughly 150k words.
* **Max output:** Synchronous Messages API limit. On the Message Batches API, Claude Opus 5, Claude Sonnet 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, and Claude Sonnet 4.6 support up to 300k output tokens with the output-300k-2026-03-24 beta header.
* **Price / MTok:** Input / output, base price per million tokens. Batch API requests are 50% off; prompt caching reads cost 10% of the base input price (2.5% on Claude Fable 5.1 and Claude Mythos 5.1). See Pricing for the full list.
* **Latency:** Comparative latency, relative to the current lineup, as published in the models overview. Actual latency depends on prompt length, output length, and thinking effort.
* **Thinking:** Adaptive thinking lets the model decide how much to think, steered by effort. Extended thinking is the manual budget\_tokens mode on earlier models.
* **Default effort:** The effort parameter’s default on the Claude API. Models without a value don’t support the parameter.
* **Knowledge cutoff:** Reliable knowledge cutoff: the date through which the model’s knowledge is most extensive and reliable.


## Specifications

Source: https://platform.claude.com/llms-full.txt#specifications-2

### Model IDs

| Platform                                                                                               | Model ID                  |
| :----------------------------------------------------------------------------------------------------- | :------------------------ |
| Claude API                                                                                             | `claude-opus-5`           |
| [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)       | `anthropic.claude-opus-5` |
| [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)              | `claude-opus-5`           |
| [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry) | `claude-opus-5`           |

### Pricing

| Feature                                                                                | Value                                                               |
| :------------------------------------------------------------------------------------- | :------------------------------------------------------------------ |
| Input                                                                                  | $5 / MTok                                                           |
| Output                                                                                 | $25 / MTok                                                          |
| [5m cache write](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | $6.25 / MTok                                                        |
| [1h cache write](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | $10 / MTok                                                          |
| [Cache read](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)     | $0.50 / MTok                                                        |
| [Batch API](https://platform.claude.com/docs/en/build-with-claude/batch-processing)    | 50% discount on input and output                                    |
| Full price list                                                                        | [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) |

### Capabilities

| Feature                                                                                                                     | Value                  |
| :-------------------------------------------------------------------------------------------------------------------------- | :--------------------- |
| [Context window](https://platform.claude.com/docs/en/build-with-claude/context-windows)                                     | 1M tokens              |
| Max output                                                                                                                  | 128K tokens            |
| [Max output (Batch API, beta)](https://platform.claude.com/docs/en/build-with-claude/batch-processing#extended-output-beta) | 300K tokens            |
| [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)                                                  | Adaptive               |
| [Default effort](https://platform.claude.com/docs/en/build-with-claude/effort)                                              | `high`                 |
| Comparative latency                                                                                                         | Moderate               |
| Input → output                                                                                                              | Text and images → text |
| Reliable knowledge cutoff                                                                                                   | May 2026               |
| Training data cutoff                                                                                                        | May 2026               |

### Availability

| Feature                                                                       | Value                                                                                                                                                                                                                                                                                                           |
| :---------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Status](https://platform.claude.com/docs/en/about-claude/model-deprecations) | Active (latest)                                                                                                                                                                                                                                                                                                 |
| Released                                                                      | July 24, 2026                                                                                                                                                                                                                                                                                                   |
| Retirement                                                                    | Not sooner than July 24, 2027                                                                                                                                                                                                                                                                                   |
| Platforms                                                                     | Claude API, [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry) |


## Good to know

Source: https://platform.claude.com/llms-full.txt#good-to-know

* On the [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing#extended-output-beta), Claude Opus 5 supports up to 300k output tokens with the `output-300k-2026-03-24` beta header.
* The minimum cacheable prompt length is 512 tokens. See [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#cache-limitations).
* Query limits and capabilities programmatically with the [Models API](https://platform.claude.com/docs/en/api/models/list).


## Resources

Source: https://platform.claude.com/llms-full.txt#resources-2

<CardGroup cols={3}>
  <Card title="Prompting Claude Opus 5" icon="lightbulb" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5">
    Model-specific prompting guidance.
  </Card>

  <Card title="Effort" icon="sliders" href="https://platform.claude.com/docs/en/build-with-claude/effort">
    Effort defaults to `high` on Claude Opus 5 and matters more than on earlier models. Choose a level per workload.
  </Card>

  <Card title="Adaptive thinking" icon="brain" href="https://platform.claude.com/docs/en/build-with-claude/thinking">
    On by default. Disabling thinking requires effort `high` or below.
  </Card>

  <Card title="Fast mode" icon="lightning" href="https://platform.claude.com/docs/en/build-with-claude/fast-mode">
    Lower-latency Claude Opus 5 on the Claude API (research preview), priced separately.
  </Card>
</CardGroup>


## Reference

Source: https://platform.claude.com/llms-full.txt#reference-3

<CardGroup cols={3}>
  <Card title="System prompt" icon="text" href="https://platform.claude.com/docs/en/release-notes/system-prompts#claude-opus-5">
    The system prompt Claude Opus 5 uses on claude.ai and the Claude apps.
  </Card>

  <Card title="System card" icon="file" href="https://www.anthropic.com/claude-opus-5-system-card">
    Safety evaluations and deployment decisions for Claude Opus 5.
  </Card>

  <Card title="Pricing" icon="coins" href="https://platform.claude.com/docs/en/about-claude/pricing">
    Full price list, including batch discounts and prompt caching rates.
  </Card>

  <Card title="Model IDs and versioning" icon="fingerprint" href="https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions">
    How model IDs, aliases, and pinned snapshots work.
  </Card>

  <Card title="Model deprecations" icon="clock" href="https://platform.claude.com/docs/en/about-claude/model-deprecations">
    Lifecycle status and retirement commitments for every Claude model.
  </Card>
</CardGroup>


---
title: Migrating to Claude Opus 5
url: https://platform.claude.com/docs/en/models/opus-5/migration-guide
description: "Migrate to Claude Opus 5 from earlier Claude models: model IDs, breaking changes, recommended changes, and migration checklists."
---

<Note>
  This guide covers migrating [Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) code. If you use [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview), no changes beyond updating the model name are required.
</Note>

<Tip>
  **Automate your migration with the Claude API skill.** In Claude Code, run `/claude-api migrate` to invoke the bundled [Claude API skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill#migrating-to-a-newer-claude-model). It works for any current Claude model as the target:

  ```text wrap
  /claude-api migrate this project to claude-opus-5
  ```

  The skill applies the model ID swap and, as needed, breaking parameter changes, prefill replacement, and effort calibration for your target model across your code base, then produces a checklist of items to verify manually. It asks you to confirm the migration scope (entire working directory, a subdirectory, or a specific file list) before editing any files. The skill also detects Amazon Bedrock and Claude Platform on AWS clients and adjusts model ID formats and feature changes for those platforms.
</Tip>

Claude Opus 5 is a step-change improvement over Claude Opus 4.8, strong on deep reasoning, agentic and long-horizon tasks, and test-time compute scaling. For behavioral differences and model-specific prompting patterns, see [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5).

Claude Opus 5 is a drop-in upgrade for Claude Opus 4.8 at the same pricing of $5 USD per million input tokens and $25 USD per million output tokens; see [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing). There are two breaking changes for code already running on Claude Opus 4.8, covered under [Breaking changes](https://platform.claude.com/docs/en/models/opus-5/migration-guide#breaking-changes). Claude Opus 5 supports the same set of features as Claude Opus 4.8, including the [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) (the default, with no beta header), [128k max output tokens](https://platform.claude.com/docs/en/models/overview), [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking), [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing), the [Files API](https://platform.claude.com/docs/en/build-with-claude/files), [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support), [vision](https://platform.claude.com/docs/en/build-with-claude/vision), and server-side and client-side [tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview), with two exceptions: [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) is not available on Claude Opus 5, and [Priority Tier](https://platform.claude.com/docs/en/api/service-tiers#supported-models) is not supported on Claude Opus 5. See each tool page for model availability.


## Migrating to Claude Opus 5 from Claude Opus 4.8

Source: https://platform.claude.com/llms-full.txt#migrating-to-claude-opus-5-from-claude-opus-4-8

<Note>
  This section covers the delta from Claude Opus 4.8 only. If your code is on Claude Opus 4.7 or earlier, use these sections instead: [Migrating to Claude Opus 5 from Claude Opus 4.7](https://platform.claude.com/docs/en/models/opus-5/migration-guide#migrating-from-claude-opus-47) or [Migrating to Claude Opus 5 from Claude Opus 4.6 and earlier Opus models](https://platform.claude.com/docs/en/models/opus-5/migration-guide#migrating-from-claude-opus-46). They include this delta plus the breaking changes from earlier models (sampling parameters rejected, manual extended thinking rejected, prefill removed, new tokenizer).
</Note>

### Update your model name

`claude-opus-5` is a fixed model ID with no date suffix, the same scheme as `claude-opus-4-8` and `claude-sonnet-5`.

### Breaking changes

1. **Thinking on by default:** On Claude Opus 4.8, requests without a `thinking` field run without thinking; on Claude Opus 5, the same requests run with [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking). `max_tokens` remains a hard limit on total output, thinking plus response text, so revisit it for workloads that ran without thinking on Claude Opus 4.8. Thinking tokens are billed as output tokens even when the thinking text is not returned to you, so although per-token pricing is unchanged, a workload that ran without thinking on Claude Opus 4.8 can produce more output tokens per request on Claude Opus 5; see [Cost control](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#cost-control). To preserve the old behavior, pass `thinking: {type: "disabled"}`, subject to the effort cap in the next item; note that with thinking disabled the model can occasionally emit tool calls as plain text or include internal XML tags in its visible output, so prefer lower effort levels with thinking enabled where you can, and see [Running with thinking disabled](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#running-with-thinking-disabled) for mitigations where you can't.

   The response shape changes with it. With thinking on, a response can begin with one or more `thinking` blocks before the first `text` block, and because `thinking.display` defaults to `"omitted"` on Claude Opus 5, those blocks arrive with an empty `thinking` field alongside their `signature`. Code that reads the reply by position, such as `content[0].text` or a stream handler that treats the first `content_block_start` event as text, breaks on these responses. Select content blocks by their `type` field instead: read `text` from the blocks whose `type` is `"text"`, and branch on the block type when handling stream events. To receive readable thinking summaries instead of an empty `thinking` field, set `display: "summarized"`; see [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display).

   If you run a tool-use loop, pass the `thinking` blocks from each assistant response back to the API complete and unmodified when you return tool results, including blocks whose `thinking` field is empty. Echo the assistant message as received rather than filtering its content blocks by type or rebuilding it: the API rejects edited, reordered, or partially dropped thinking blocks with a 400 error. See [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks).

2. **Disabling thinking is capped at `high` effort:** You can still turn thinking off with `thinking: {type: "disabled"}`, but only at an [effort](https://platform.claude.com/docs/en/build-with-claude/effort) level of `high` or below. A request that combines `thinking: {type: "disabled"}` with effort `xhigh` or `max` returns a 400 error. Claude Opus 4.8 accepts this combination, so audit requests that disable thinking before you migrate.

   The check is enforced on each request: every request's effort and thinking configuration is validated independently, so a request that raises effort to `xhigh` or `max` while thinking is disabled is rejected even if earlier requests in the conversation were accepted.

   Before (accepted on Claude Opus 4.8, rejected on Claude Opus 5):

After (Claude Opus 5), either remove the `thinking` field to re-enable thinking:

or keep thinking disabled and lower the effort:

### Recommended changes

These are not required but will improve your experience:

1. **Test `max` effort for capability-critical work:** Claude Opus 5 supports the full set of [effort levels](https://platform.claude.com/docs/en/build-with-claude/effort) (`low`, `medium`, `high`, `xhigh`, `max`). Where maximum capability matters more than token spend, test `max` effort. It can deliver gains on the most demanding tasks but may show diminishing returns from increased token usage and can be prone to overthinking on simpler ones. If you run at `xhigh` or `max` effort, set a large `max_tokens` so the model has room to think and act; start at 64k tokens and tune from there.

2. **Consider automatic fallbacks:** Claude Opus 5 ships with cybersecurity safety classifiers whose cyber-category refusals can fall back to Claude Opus 4.8. To re-run refused requests on another model automatically, consider the `fallbacks` parameter with the `"default"` mode (`fallbacks: "default"`), which selects a recommended fallback model based on the refusal category instead of a hand-maintained model list. Server-side fallback is in beta; the `"default"` mode requires the `server-side-fallback-2026-07-01` beta header. See [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback).

3. **Cache shorter prompts:** The minimum cacheable prompt length on Claude Opus 5 is 512 tokens, down from 1,024 tokens on Claude Opus 4.8. Prompts that were too short to cache on Claude Opus 4.8 can now create cache entries, with no code changes required. See [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#cache-limitations) for per-model minimums.

4. **Change tools mid-conversation (beta):** You can add or remove tools between turns of a conversation without invalidating [prompt cache](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) hits on earlier turns. Send the beta header `mid-conversation-tool-changes-2026-07-01`. This is useful for agentic workloads that expose tools progressively or retire them as a task advances; without it, a changed tool list invalidates the cached prefix.

5. **Re-tune length and verbosity prompts:** Default visible responses and written deliverables run longer on Claude Opus 5 than on Claude Opus 4.8, and lowering effort reduces thinking volume without reliably shortening the visible response. Prompt explicitly for conciseness or a target length instead. See [Response length and verbosity](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#response-length-and-verbosity) and [Written deliverable length](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#written-deliverable-length).

6. **Remove carried-over verification instructions and constrain scope:** Claude Opus 5 verifies its own work without being told to, so remove explicit verification or self-check instructions carried over from prompts tuned for earlier models; leaving them in causes over-verification. For narrow tasks, constrain the task scope explicitly. In multi-agent frameworks, give explicit guidance on which scenarios warrant delegation or cap the number of subagents, because Claude Opus 5 delegates more readily than earlier models. See [Task scope and over-verification](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#task-scope-and-over-verification) and [Controlling subagent spawning](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#controlling-subagent-spawning).

### Migration checklist

* Update the model name from `claude-opus-4-8` to `claude-opus-5`.
* Review workloads that ran without a `thinking` field: they run with thinking on Claude Opus 5. Revisit `max_tokens`, which remains a hard limit on total output (thinking plus response text), or pass `thinking: {type: "disabled"}` at effort `high` or below to preserve the old behavior. If you disable thinking, review [Running with thinking disabled](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#running-with-thinking-disabled) for the output artifacts that can appear and their prompting mitigations.
* Update response parsing that reads content by position, such as `content[0].text` or a stream handler that assumes the first content block is text: with thinking on, `thinking` blocks arrive before `text` blocks. Select content blocks by `type` instead.
* If you run a tool-use loop, pass `thinking` blocks back complete and unmodified when you return tool results; modified blocks return a 400 error. See [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks).
* Verify any code that parses the `thinking` field treats it as display text only. `thinking.display` defaults to `"omitted"` on Claude Opus 5, the same as on Claude Opus 4.8, so thinking blocks arrive with an empty `thinking` field; set `display: "summarized"` to receive readable summaries. See [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display).
* Audit requests that disable thinking: `thinking: {type: "disabled"}` with effort `xhigh` or `max` returns a 400 error, enforced on each request. Re-enable thinking or lower the effort to `high` or below.
* Re-evaluate your `effort` setting: run a fresh [effort](https://platform.claude.com/docs/en/build-with-claude/effort) sweep on your own evals rather than carrying over a setting tuned for an earlier model. `low` and `medium` effort are worth testing as cost and latency controls, and test `max` effort where maximum capability matters more than token spend. If you run at `xhigh` or `max` effort, raise `max_tokens` to at least 64k as a starting point.
* Review prompts near the caching minimum: prompts of 512 tokens or more can now create cache entries, down from 1,024 tokens on Claude Opus 4.8.
* Handle `stop_reason: "refusal"`, and consider `fallbacks: "default"` (beta) to re-run refused requests on a recommended fallback model automatically.
* If your organization has a [Priority Tier](https://platform.claude.com/docs/en/api/service-tiers#supported-models) commitment, plan capacity separately: Priority Tier is not supported on Claude Opus 5, while Claude Opus 4.8 keeps it.
* For agentic workloads, consider [task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets) (beta) and mid-conversation tool changes (beta).
* Re-tune length and verbosity prompts: default visible responses and written deliverables run longer on Claude Opus 5, and lowering effort reduces thinking volume without reliably shortening the visible response. Prompt explicitly for conciseness or a target length. See [Response length and verbosity](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#response-length-and-verbosity) and [Written deliverable length](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#written-deliverable-length).
* Remove verification and self-check instructions carried over from prompts tuned for earlier models (they cause over-verification on Claude Opus 5), constrain task scope explicitly for narrow tasks, and in multi-agent frameworks steer or cap subagent delegation. See [Task scope and over-verification](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#task-scope-and-over-verification) and [Controlling subagent spawning](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#controlling-subagent-spawning).
* Re-baseline cost and latency on your own workloads. Per-token pricing is unchanged from Claude Opus 4.8, but thinking tokens are billed as output tokens, so workloads that ran without thinking can produce more output tokens per request.


## Migrating to Claude Opus 5 from Claude Opus 4.7

Source: https://platform.claude.com/llms-full.txt#migrating-to-claude-opus-5-from-claude-opus-4-7

Claude Opus 5 should have strong out-of-the-box performance on existing Claude Opus 4.7 prompts and evals, at the same pricing of $5 USD per million input tokens and $25 USD per million output tokens. It supports the same set of features as Claude Opus 4.7, including the [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows), [128k max output tokens](https://platform.claude.com/docs/en/models/overview), [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking), [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing), the [Files API](https://platform.claude.com/docs/en/build-with-claude/files), [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support), [vision](https://platform.claude.com/docs/en/build-with-claude/vision), and server-side and client-side [tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview), with two exceptions: [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) is not available on Claude Opus 5, and [Priority Tier](https://platform.claude.com/docs/en/api/service-tiers#supported-models) is not supported on Claude Opus 5. It also adds [mid-conversation system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages) and publicly documents [refusal stop details](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#refusal-response). On the Claude API and Google Cloud, Claude Opus 5 also supports [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) as the stable `computer_toolset_20260801` toolset and the [browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) for tasks inside webpages, neither of which Claude Opus 4.7 supports; existing integrations on the earlier `computer_20251124` version continue to work unchanged on both models. To upgrade an existing integration, see [Migrate from `computer_20251124`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#migrate-from-computer-20251124).

<Note>
  If your code is on Claude Opus 4.6 or earlier, use [Migrating to Claude Opus 5 from Claude Opus 4.6 and earlier Opus models](https://platform.claude.com/docs/en/models/opus-5/migration-guide#migrating-from-claude-opus-46) instead. That section includes breaking changes (sampling parameters rejected, manual extended thinking rejected, new tokenizer) that the upgrade from Claude Opus 4.7 alone does not cover.
</Note>

### Update your model name

### Breaking changes

1. **Thinking on by default:** On Claude Opus 4.7, requests without a `thinking` field run without thinking; on Claude Opus 5, the same requests run with [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking). `max_tokens` remains a hard limit on total output, thinking plus response text, so revisit it for workloads that ran without thinking on Claude Opus 4.7. Thinking tokens are billed as output tokens even when the thinking text is not returned to you, so although per-token pricing is unchanged, a workload that ran without thinking on Claude Opus 4.7 can produce more output tokens per request on Claude Opus 5; see [Cost control](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#cost-control). To preserve the old behavior, pass `thinking: {type: "disabled"}`, subject to the effort cap in the next item; note that with thinking disabled the model can occasionally emit tool calls as plain text or include internal XML tags in its visible output, so prefer lower effort levels with thinking enabled where you can, and see [Running with thinking disabled](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#running-with-thinking-disabled) for mitigations where you can't.

   The response shape changes with it. With thinking on, a response can begin with one or more `thinking` blocks before the first `text` block, and because `thinking.display` defaults to `"omitted"` on Claude Opus 5, those blocks arrive with an empty `thinking` field alongside their `signature`. Code that reads the reply by position, such as `content[0].text` or a stream handler that treats the first `content_block_start` event as text, breaks on these responses. Select content blocks by their `type` field instead: read `text` from the blocks whose `type` is `"text"`, and branch on the block type when handling stream events. To receive readable thinking summaries instead of an empty `thinking` field, set `display: "summarized"`; see [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display).

   If you run a tool-use loop, pass the `thinking` blocks from each assistant response back to the API complete and unmodified when you return tool results, including blocks whose `thinking` field is empty. Echo the assistant message as received rather than filtering its content blocks by type or rebuilding it: the API rejects edited, reordered, or partially dropped thinking blocks with a 400 error. See [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks).

2. **Disabling thinking is capped at `high` effort:** You can turn thinking off with `thinking: {type: "disabled"}`, but only at an [effort](https://platform.claude.com/docs/en/build-with-claude/effort) level of `high` or below. A request that combines `thinking: {type: "disabled"}` with effort `xhigh` or `max` returns a 400 error. Claude Opus 4.7 accepts this combination, so audit requests that disable thinking before you migrate.

   The check is enforced on each request: every request's effort and thinking configuration is validated independently, so a request that raises effort to `xhigh` or `max` while thinking is disabled is rejected even if earlier requests in the conversation were accepted.

   Before (accepted on Claude Opus 4.7, rejected on Claude Opus 5):

After (Claude Opus 5), either remove the `thinking` field to run with thinking:

or keep thinking disabled and lower the effort:

### What changed

The following items are not breaking changes; they describe behavior differences worth checking after you swap the model ID.

1. **Sampling parameters (unchanged):** Setting `temperature`, `top_p`, or `top_k` to a non-default value returns a 400 error on Claude Opus 5, the same as on Claude Opus 4.7. Most SDKs still define these fields for compatibility with earlier models, so code that sets them type-checks even though the API rejects the request. The Python SDK (v1.0 and later) does not define them, and passing them raises a `TypeError`. If you removed these parameters when migrating to Opus 4.7, no further changes are needed.

2. **Effort default is `high`:** The [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) default on Claude Opus 5 is `high` on the Claude API and Claude Code. If you already set effort explicitly, your setting is unchanged.

3. **Effort levels recalibrated:** The token allocation behind each effort level changes on Claude Opus 5 compared to Claude Opus 4.7, and Claude Opus 5 supports the full set of effort levels (`low`, `medium`, `high`, `xhigh`, `max`). Run a fresh effort sweep on your own evals rather than carrying over a setting tuned for Claude Opus 4.7. `low` and `medium` effort are worth testing as cost and latency controls, and test `max` effort where maximum capability matters more than token spend. If you run at `xhigh` or `max` effort, set a large `max_tokens` so the model has room to think and act; start at 64k tokens and tune from there. See [Effort](https://platform.claude.com/docs/en/build-with-claude/effort).

4. **1M context window is the default:** Claude Opus 5 serves the full 1M token [context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) by default with no beta header and no long-context premium. If your client passes a context-window beta header for compatibility with older models, you can remove it on Claude Opus 5.

5. **Mid-conversation system messages:** Claude Opus 5 accepts `role: "system"` messages immediately after a user turn in the `messages` array (subject to [placement rules](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#limitations)). Use the top-level `system` field for instructions that apply from the start. Claude Opus 4.7 rejects `role: "system"` in `messages` with a 400 error. If you maintain code paths that rebuild the full message history to update instructions, you can simplify them and preserve [prompt cache](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) hits on earlier turns.

6. **Refusal stop details:** The `stop_details` object on refusal responses (available since Claude Opus 4.7) is now publicly documented. When the model declines a request, it identifies the category of refusal, in addition to the existing `refusal` stop reason. No beta header is required, and there is no opt-out. See [Handling stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons).

7. **Lower prompt caching minimum:** The minimum cacheable prompt length on Claude Opus 5 is 512 tokens, lower than on Claude Opus 4.7. Prompts that were too short to cache on Claude Opus 4.7 can now create cache entries, with no code changes required. See [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#cache-limitations) for per-model minimums.

8. **Fast mode:** Claude Opus 5 supports [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) (research preview); fast mode is not available on Claude Opus 4.7, where requests with `speed: "fast"` return an error. The `speed: "fast"` parameter and `fast-mode-2026-02-01` beta header work unchanged on Claude Opus 5.

### Recommended changes

These are not required but will improve your experience:

1. **Consider automatic fallbacks:** Claude Opus 5 ships with cybersecurity safety classifiers whose cyber-category refusals can fall back to Claude Opus 4.8. To re-run refused requests on another model automatically, consider the `fallbacks` parameter with the `"default"` mode (`fallbacks: "default"`), which selects a recommended fallback model based on the refusal category instead of a hand-maintained model list. Server-side fallback is in beta; the `"default"` mode requires the `server-side-fallback-2026-07-01` beta header. See [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback).

2. **Change tools mid-conversation (beta):** You can add or remove tools between turns of a conversation without invalidating [prompt cache](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) hits on earlier turns. Send the beta header `mid-conversation-tool-changes-2026-07-01`. This is useful for agentic workloads that expose tools progressively or retire them as a task advances; without it, a changed tool list invalidates the cached prefix.

3. **Re-tune length and verbosity prompts:** Default visible responses and written deliverables run longer on Claude Opus 5 than on earlier Opus models, and lowering effort reduces thinking volume without reliably shortening the visible response. Prompt explicitly for conciseness or a target length instead. See [Response length and verbosity](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#response-length-and-verbosity) and [Written deliverable length](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#written-deliverable-length).

4. **Remove carried-over verification instructions and constrain scope:** Claude Opus 5 verifies its own work without being told to, so remove explicit verification or self-check instructions carried over from prompts tuned for earlier models; leaving them in causes over-verification. For narrow tasks, constrain the task scope explicitly. In multi-agent frameworks, give explicit guidance on which scenarios warrant delegation or cap the number of subagents, because Claude Opus 5 delegates more readily than earlier models. See [Task scope and over-verification](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#task-scope-and-over-verification) and [Controlling subagent spawning](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#controlling-subagent-spawning).

### Migration checklist

* Update model name from `claude-opus-4-7` to `claude-opus-5` (or update aliases).
* Review workloads that ran without a `thinking` field: they run with thinking on Claude Opus 5. Revisit `max_tokens`, which remains a hard limit on total output (thinking plus response text), or pass `thinking: {type: "disabled"}` at effort `high` or below to preserve the old behavior. If you disable thinking, review [Running with thinking disabled](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#running-with-thinking-disabled) for the output artifacts that can appear and their prompting mitigations.
* Update response parsing that reads content by position, such as `content[0].text` or a stream handler that assumes the first content block is text: with thinking on, `thinking` blocks arrive before `text` blocks. Select content blocks by `type` instead.
* If you run a tool-use loop, pass `thinking` blocks back complete and unmodified when you return tool results; modified blocks return a 400 error. See [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks).
* Verify any code that parses the `thinking` field treats it as display text only. `thinking.display` defaults to `"omitted"` on Claude Opus 5, the same as on Claude Opus 4.7, so thinking blocks arrive with an empty `thinking` field; set `display: "summarized"` to receive readable summaries. See [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display).
* Audit requests that disable thinking: `thinking: {type: "disabled"}` with effort `xhigh` or `max` returns a 400 error, enforced on each request. Re-enable thinking or lower the effort to `high` or below.
* If you removed sampling parameters during the Opus 4.7 migration, no action is needed. If you re-added them with a 400-retry path, remove that retry path.
* Re-evaluate your `effort` setting: run a fresh [effort](https://platform.claude.com/docs/en/build-with-claude/effort) sweep on your own evals rather than carrying over a setting tuned for Claude Opus 4.7. Test `low` and `medium` effort as cost and latency controls, and `max` effort where maximum capability matters more than token spend. If you run at `xhigh` or `max` effort, raise `max_tokens` to at least 64k as a starting point.
* Remove any context-window beta header. The 1M context window is the default on the Claude API, Amazon Bedrock, Google Cloud, and Microsoft Foundry.
* If you rebuild conversation history to update instructions, consider switching to a mid-conversation system message to preserve prompt cache hits.
* Verify your stop-reason handling reads `stop_details` on refusals (available since Claude Opus 4.7; now publicly documented), and consider `fallbacks: "default"` (beta) to re-run refused requests on a recommended fallback model automatically.
* Review prompts near the caching minimum: prompts of 512 tokens or more can now create cache entries.
* If you use [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool), plan an alternative: it is not available on Claude Opus 5.
* If your organization has a [Priority Tier](https://platform.claude.com/docs/en/api/service-tiers#supported-models) commitment, note that Priority Tier is not supported on Claude Opus 5.
* If you used fast mode on Claude Opus 4.7, no request changes are needed beyond the model ID: `speed: "fast"` and the `fast-mode-2026-02-01` beta header work unchanged on Claude Opus 5.
* For agentic workloads, consider [task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets) (beta) and mid-conversation tool changes (beta).
* Re-tune length and verbosity prompts, and remove verification and self-check instructions carried over from prompts tuned for earlier models.
* Re-baseline cost and latency at your chosen effort level. Per-token pricing is unchanged from Claude Opus 4.7, but thinking tokens are billed as output tokens, so workloads that ran without thinking can produce more output tokens per request.


## Migrating to Claude Opus 5 from Claude Opus 4.6 and earlier Opus models

Source: https://platform.claude.com/llms-full.txt#migrating-to-claude-opus-5-from-claude-opus-4-6-and-earlier-opus-models

Claude Opus 5 should have strong out-of-the-box performance on existing Claude Opus 4.6 prompts and evals at the same pricing, but there are a handful of behavioral and API changes worth knowing about as you migrate. Most of these changes took effect in Claude Opus 4.7; two more, thinking on by default and an effort cap on disabling thinking, take effect on Claude Opus 5. All of them are covered in this section, so it is complete for code coming straight from Claude Opus 4.6. Claude Opus 5 supports the same set of features as Claude Opus 4.6, including:

* [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) at standard API pricing with no long-context premium
* [128k max output tokens](https://platform.claude.com/docs/en/models/overview)
* [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)
* [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
* [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
* [Files API](https://platform.claude.com/docs/en/build-with-claude/files)
* [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support)
* [Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
* Server-side and client-side [tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) ([bash](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool), [code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool), [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool), [text editor](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool), [web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool), [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector), [memory](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool))

Two exceptions: [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) is not available on Claude Opus 5, and [Priority Tier](https://platform.claude.com/docs/en/api/service-tiers#supported-models) is not supported on Claude Opus 5. On the Claude API and Google Cloud, Claude Opus 5 also supports [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) as the stable `computer_toolset_20260801` toolset and the [browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) for tasks inside webpages, neither of which Claude Opus 4.6 or earlier Opus models support; existing integrations on the earlier `computer_20251124` version continue to work unchanged on Claude Opus 5. To upgrade an existing integration, see [Migrate from `computer_20251124`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#migrate-from-computer-20251124).

### Update your model name

### Breaking changes

1. **Extended thinking removed:** `thinking: {type: "enabled", budget_tokens: N}` is no longer supported on Claude Opus 4.7 or later models and returns a 400 error. Switch to [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) (`thinking: {type: "adaptive"}`) and use the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) to control thinking depth. On Claude Opus 5, adaptive thinking is **on by default**: `thinking: {type: "adaptive"}` is valid and equivalent to omitting the `thinking` field entirely (see the next item).

   Before (Claude Opus 4.6):

   <CodeGroup>
     ```bash cURL
     curl https://api.anthropic.com/v1/messages \
       -H "x-api-key: $ANTHROPIC_API_KEY" \
       -H "anthropic-version: 2023-06-01" \
       -H "content-type: application/json" \
       -d '{
         "model": "claude-opus-4-6",
         "max_tokens": 16000,
         "thinking": {
           "type": "enabled",
           "budget_tokens": 10000
         },
         "messages": [
           {
             "role": "user",
             "content": "..."
           }
         ]
       }'

bash CLI
     ant messages create <<'YAML'
     model: claude-opus-4-6
     max_tokens: 16000
     thinking:
       type: enabled
       budget_tokens: 10000
     messages:
       - role: user
         content: "..."
     YAML

python Python
     client.messages.create(
         model="claude-opus-4-6",
         max_tokens=16000,
         thinking={"type": "enabled", "budget_tokens": 10000},
         messages=[{"role": "user", "content": "..."}],
     )

typescript TypeScript
     await client.messages.create({
       model: "claude-opus-4-6",
       max_tokens: 16000,
       thinking: { type: "enabled", budget_tokens: 10000 },
       messages: [{ role: "user", content: "..." }]
     });

csharp C#
     using Anthropic;
     using Anthropic.Models.Messages;

     AnthropicClient client = new();

     var parameters = new MessageCreateParams
     {
         Model = "claude-opus-4-6",
         MaxTokens = 16000,
         Thinking = new ThinkingConfigEnabled(budgetTokens: 10000),
         Messages = [new() { Role = Role.User, Content = "..." }]
     };

     var response = await client.Messages.Create(parameters);
     Console.WriteLine(response);

go Go
     client := anthropic.NewClient()

     response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
     	Model:     "claude-opus-4-6",
     	MaxTokens: 16000,
     	Thinking:  anthropic.ThinkingConfigParamOfEnabled(10000),
     	Messages: []anthropic.MessageParam{
     		anthropic.NewUserMessage(anthropic.NewTextBlock("...")),
     	},
     })
     if err != nil {
     	log.Fatal(err)
     }
     fmt.Println(response)

java Java
     AnthropicClient client = AnthropicOkHttpClient.fromEnv();

     MessageCreateParams params = MessageCreateParams.builder()
         .model("claude-opus-4-6")
         .maxTokens(16000L)
         .enabledThinking(10000L)
         .addUserMessage("...")
         .build();

     Message response = client.messages().create(params);
     IO.println(response);

php PHP
     $client = new Client();

     $message = $client->messages->create(
         maxTokens: 16000,
         messages: [['role' => 'user', 'content' => '...']],
         model: 'claude-opus-4-6',
         thinking: ['type' => 'enabled', 'budget_tokens' => 10000],
     );

ruby Ruby
     client = Anthropic::Client.new

     message = client.messages.create(
       model: "claude-opus-4-6",
       max_tokens: 16000,
       thinking: {
         type: "enabled",
         budget_tokens: 10000
       },
       messages: [
         { role: "user", content: "..." }
       ]
     )

bash cURL
     curl https://api.anthropic.com/v1/messages \
       -H "x-api-key: $ANTHROPIC_API_KEY" \
       -H "anthropic-version: 2023-06-01" \
       -H "content-type: application/json" \
       -d '{
         "model": "claude-opus-5",
         "max_tokens": 16000,
         "thinking": {
           "type": "adaptive"
         },
         "output_config": {
           "effort": "high"
         },
         "messages": [
           {
             "role": "user",
             "content": "..."
           }
         ]
       }'

bash CLI
     ant messages create <<'YAML'
     model: claude-opus-5
     max_tokens: 16000
     thinking:
       type: adaptive
     output_config:
       effort: high
     messages:
       - role: user
         content: "..."
     YAML

python Python
     client.messages.create(
         model="claude-opus-5",
         max_tokens=16000,
         thinking={"type": "adaptive"},
         output_config={"effort": "high"},  # or "max", "xhigh", "medium", "low"
         messages=[{"role": "user", "content": "..."}],
     )

typescript TypeScript
     await client.messages.create({
       model: "claude-opus-5",
       max_tokens: 16000,
       thinking: { type: "adaptive" },
       output_config: { effort: "high" }, // or "max", "xhigh", "medium", "low"
       messages: [{ role: "user", content: "..." }]
     });

csharp C#
     using Anthropic;
     using Anthropic.Models.Messages;

     AnthropicClient client = new();

     var parameters = new MessageCreateParams
     {
         Model = "claude-opus-5",
         MaxTokens = 16000,
         Thinking = new ThinkingConfigAdaptive(),
         OutputConfig = new OutputConfig { Effort = Effort.High }, // or Max, Xhigh, Medium, Low
         Messages = [new() { Role = Role.User, Content = "..." }]
     };

     var response = await client.Messages.Create(parameters);
     Console.WriteLine(response);

go Go
     client := anthropic.NewClient()

     response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
     	Model:     "claude-opus-5",
     	MaxTokens: 16000,
     	Thinking: anthropic.ThinkingConfigParamUnion{
     		OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{},
     	},
     	OutputConfig: anthropic.OutputConfigParam{
     		Effort: anthropic.OutputConfigEffortHigh, // or Max, Xhigh, Medium, Low
     	},
     	Messages: []anthropic.MessageParam{
     		anthropic.NewUserMessage(anthropic.NewTextBlock("...")),
     	},
     })
     if err != nil {
     	log.Fatal(err)
     }
     fmt.Println(response)

java Java
     AnthropicClient client = AnthropicOkHttpClient.fromEnv();

     MessageCreateParams params = MessageCreateParams.builder()
         .model("claude-opus-5")
         .maxTokens(16000L)
         .thinking(ThinkingConfigAdaptive.builder().build())
         .outputConfig(OutputConfig.builder()
             .effort(OutputConfig.Effort.HIGH) // or MAX, XHIGH, MEDIUM, LOW
             .build())
         .addUserMessage("...")
         .build();

     Message response = client.messages().create(params);
     IO.println(response);

php PHP
     $client = new Client();

     $message = $client->messages->create(
         maxTokens: 16000,
         messages: [['role' => 'user', 'content' => '...']],
         model: 'claude-opus-5',
         thinking: ['type' => 'adaptive'],
         outputConfig: ['effort' => 'high'], // or 'max', 'xhigh', 'medium', 'low'
     );

ruby Ruby
     client = Anthropic::Client.new

     message = client.messages.create(
       model: "claude-opus-5",
       max_tokens: 16000,
       thinking: {
         type: "adaptive"
       },
       output_config: {
         effort: "high" # or "max", "xhigh", "medium", "low"
       },
       messages: [
         { role: "user", content: "..." }
       ]
     )

python Python
     thinking = {
         "type": "adaptive",
         "display": "summarized",
     }

typescript TypeScript
     const thinking = {
       type: "adaptive",
       display: "summarized"
     };

csharp C#
     var thinking = new ThinkingConfigAdaptive { Display = Display.Summarized };

go Go
     thinking := anthropic.ThinkingConfigParamUnion{
     	OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{
     		Display: anthropic.ThinkingConfigAdaptiveDisplaySummarized,
     	},
     }

java Java
     ThinkingConfigAdaptive thinking = ThinkingConfigAdaptive.builder()
         .display(ThinkingConfigAdaptive.Display.SUMMARIZED)
         .build();

php PHP
     $thinking = ['type' => 'adaptive', 'display' => 'summarized'];

ruby Ruby
     thinking = {
       type: "adaptive",
       display: "summarized"
     }

python Python
     output_config = {
         "effort": "high",
         "task_budget": {"type": "tokens", "total": 128000},
     }

typescript TypeScript
     const output_config = {
       effort: "high",
       task_budget: { type: "tokens", total: 128000 }
     };

csharp C#
     var outputConfig = new BetaOutputConfig
     {
         Effort = Effort.High,
         TaskBudget = new BetaTokenTaskBudget
         {
             Total = 128000,
         },
     };

go Go
     outputConfig := anthropic.BetaOutputConfigParam{
     	Effort: anthropic.BetaOutputConfigEffortHigh,
     	TaskBudget: anthropic.BetaTokenTaskBudgetParam{
     		Total: 128000,
     	},
     }

java Java
     BetaOutputConfig outputConfig = BetaOutputConfig.builder()
         .effort(BetaOutputConfig.Effort.HIGH)
         .taskBudget(BetaTokenTaskBudget.builder()
             .total(128000L)
             .build())
         .build();

php PHP
     $outputConfig = [
         'effort' => 'high',
         'taskBudget' => [
             'type' => 'tokens',
             'total' => 128000,
         ],
     ];

ruby Ruby
     output_config = {
       effort: :high,
       task_budget: {
         type: :tokens,
         total: 128_000
       }
     }

python
# Opus migration
model = "claude-opus-4-5"  # Before
model = "claude-opus-5"  # After

bash cURL
     curl -sS https://api.anthropic.com/v1/messages \
       -H "content-type: application/json" \
       -H "x-api-key: $ANTHROPIC_API_KEY" \
       -H "anthropic-version: 2023-06-01" \
       -d '{
         "model": "claude-opus-5",
         "max_tokens": 16000,
         "thinking": {"type": "adaptive"},
         "output_config": {"effort": "high"},
         "messages": [{"role": "user", "content": "Your prompt here"}]
       }'

python Before
     response = client.beta.messages.create(
         model="claude-opus-4-5",
         max_tokens=16000,
         thinking={"type": "enabled", "budget_tokens": 32000},
         betas=["interleaved-thinking-2025-05-14"],
         messages=[{"role": "user", "content": "Your prompt here"}],
     )

python After
     response = client.messages.create(
         model="claude-opus-5",
         max_tokens=16000,
         thinking={"type": "adaptive"},
         output_config={"effort": "high"},
         messages=[{"role": "user", "content": "Your prompt here"}],
     )

bash CLI
     ant messages create <<'YAML'
     model: claude-opus-5
     max_tokens: 16000
     thinking:
       type: adaptive
     output_config:
       effort: high
     messages:
       - role: user
         content: Your prompt here
     YAML

typescript TypeScript
     const client = new Anthropic();

     const response = await client.messages.create({
       model: "claude-opus-5",
       max_tokens: 16000,
       thinking: { type: "adaptive" },
       output_config: { effort: "high" },
       messages: [{ role: "user", content: "Your prompt here" }]
     });

csharp C#
     using Anthropic;
     using Anthropic.Models.Messages;

     AnthropicClient client = new();

     var parameters = new MessageCreateParams
     {
         Model = Model.ClaudeOpus5,
         MaxTokens = 16000,
         Thinking = new ThinkingConfigAdaptive(),
         OutputConfig = new OutputConfig { Effort = Effort.High },
         Messages = [new() { Role = Role.User, Content = "Your prompt here" }]
     };

     var response = await client.Messages.Create(parameters);
     Console.WriteLine(response);

go Go
     client := anthropic.NewClient()

     response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
     	Model:     anthropic.ModelClaudeOpus5,
     	MaxTokens: 16000,
     	Thinking: anthropic.ThinkingConfigParamUnion{
     		OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{},
     	},
     	OutputConfig: anthropic.OutputConfigParam{
     		Effort: anthropic.OutputConfigEffortHigh,
     	},
     	Messages: []anthropic.MessageParam{
     		anthropic.NewUserMessage(anthropic.NewTextBlock("Your prompt here")),
     	},
     })
     if err != nil {
     	log.Fatal(err)
     }
     fmt.Println(response)

java Java
     import com.anthropic.models.messages.OutputConfig;
     import com.anthropic.models.messages.ThinkingConfigAdaptive;
     // ...
     public class AdaptiveThinkingExample {
         public static void main(String[] args) {
             AnthropicClient client = AnthropicOkHttpClient.fromEnv();

             MessageCreateParams params = MessageCreateParams.builder()
                 .model(Model.CLAUDE_OPUS_5)
                 .maxTokens(16000L)
                 .thinking(ThinkingConfigAdaptive.builder().build())
                 .outputConfig(OutputConfig.builder()
                     .effort(OutputConfig.Effort.HIGH)
                     .build())
                 .addUserMessage("Your prompt here")
                 .build();

             Message response = client.messages().create(params);
             System.out.println(response);
         }
     }

php PHP
     $client = new Client();

     $response = $client->messages->create(
         maxTokens: 16000,
         messages: [['role' => 'user', 'content' => 'Your prompt here']],
         model: 'claude-opus-5',
         thinking: ['type' => 'adaptive'],
         outputConfig: ['effort' => 'high'],
     );

ruby Ruby
     client = Anthropic::Client.new

     response = client.messages.create(
       model: "claude-opus-5",
       max_tokens: 16000,
       thinking: { type: "adaptive" },
       output_config: { effort: "high" },
       messages: [{ role: "user", content: "Your prompt here" }]
     )

python
# From Opus 4.1
model = "claude-opus-4-1-20250805"  # Before
model = "claude-opus-5"  # After

# From Sonnet 3.7
model = "claude-3-7-sonnet-20250219"  # Before
model = "claude-opus-5"  # After

python Python
     # Before - This will error in Claude 4+ models
     response = client.messages.create(
         model="claude-3-7-sonnet-20250219",
         temperature=0.7,
         top_p=0.9,  # Non-default sampling params return 400 on Opus 4.7
         # ...
     )

     # After
     response = client.messages.create(
         model="claude-opus-5",
         # ...
     )

typescript TypeScript
     // Before - This will error in Claude 4+ models
     await client.messages.create({
       model: "claude-3-7-sonnet-20250219",
       temperature: 0.7,
       top_p: 0.9 // Non-default sampling params return 400 on Opus 4.7
       // ...
     });

     // After
     await client.messages.create({
       model: "claude-opus-5"
       // ...
     });

csharp C#
     // Before - This will error in Claude 4+ models
     await client.Messages.Create(new MessageCreateParams
     {
         Model = "claude-3-7-sonnet-20250219",
         Temperature = 0.7,
         TopP = 0.9, // Non-default sampling params return 400 on Opus 4.7
         // ...
     });

     // After
     await client.Messages.Create(new MessageCreateParams
     {
         Model = "claude-opus-5",
         // ...
     });

go Go
     // Before - This will error in Claude 4+ models
     client.Messages.New(ctx, anthropic.MessageNewParams{
     	Model:       "claude-3-7-sonnet-20250219",
     	Temperature: anthropic.Float(0.7),
     	TopP:        anthropic.Float(0.9), // Non-default sampling params return 400 on Opus 4.7
     	// ...
     })

     // After
     client.Messages.New(ctx, anthropic.MessageNewParams{
     	Model: "claude-opus-5",
     	// ...
     })

java Java
     // Before - This will error in Claude 4+ models
     client.messages().create(MessageCreateParams.builder()
         .model("claude-3-7-sonnet-20250219")
         .temperature(0.7)
         .topP(0.9) // Non-default sampling params return 400 on Opus 4.7
         // ...
         .build());

     // After
     client.messages().create(MessageCreateParams.builder()
         .model("claude-opus-5")
         // ...
         .build());

php PHP
     // Before - This will error in Claude 4+ models
     $client->messages->create(
         model: 'claude-3-7-sonnet-20250219',
         temperature: 0.7,
         topP: 0.9, // Non-default sampling params return 400 on Opus 4.7
         // ...
     );

     // After
     $client->messages->create(
         model: 'claude-opus-5',
         // ...
     );

ruby Ruby
     # Before - This will error in Claude 4+ models
     client.messages.create(
       model: "claude-3-7-sonnet-20250219",
       temperature: 0.7,
       top_p: 0.9, # Non-default sampling params return 400 on Opus 4.7
       # ...
     )

     # After
     client.messages.create(
       model: "claude-opus-5",
       # ...
     )

python Python
     # Before
     tools = [{"type": "text_editor_20250124", "name": "str_replace_editor"}]

     # After
     tools = [{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}]

typescript TypeScript
     // Before
     const legacyTools = [{ type: "text_editor_20250124", name: "str_replace_editor" }];

     // After
     const tools = [{ type: "text_editor_20250728", name: "str_replace_based_edit_tool" }];

csharp C#
     var parameters = new MessageCreateParams
     {
         // Before: {"type": "text_editor_20250124", "name": "str_replace_editor"}
         // After:
         Tools = [new ToolTextEditor20250728()],
         // ...
     };

go Go
     params := anthropic.MessageNewParams{
     	// Before: {"type": "text_editor_20250124", "name": "str_replace_editor"}
     	// After:
     	Tools: []anthropic.ToolUnionParam{
     		{OfTextEditor20250728: &anthropic.ToolTextEditor20250728Param{}},
     	},
     	// ...
     }

java Java
     MessageCreateParams params = MessageCreateParams.builder()
         // Before: {"type": "text_editor_20250124", "name": "str_replace_editor"}
         // After:
         .addTool(ToolTextEditor20250728.builder().build())
         // ...
         .build();

php PHP
     $message = $client->messages->create(
         // Before: ['type' => 'text_editor_20250124', 'name' => 'str_replace_editor']
         // After:
         tools: [new ToolTextEditor20250728()],
         // ...
     );

ruby Ruby
     # Before
     legacy_tools = [{type: "text_editor_20250124", name: "str_replace_editor"}]

     # After
     tools = [{type: "text_editor_20250728", name: "str_replace_based_edit_tool"}]

python Python
     response = client.messages.create(...)

     if response.stop_reason == "refusal":
         # Handle refusal appropriately
         pass

typescript TypeScript
     const response = await client.messages.create(/* ... */);

     if (response.stop_reason === "refusal") {
       // Handle refusal appropriately
     }

csharp C#
     var response = await client.Messages.Create(...);

     if (response.StopReason?.Value() == StopReason.Refusal)
     {
         // Handle refusal appropriately
     }

go Go
     response, _ := client.Messages.New(ctx, params) // your existing request

     if response.StopReason == anthropic.StopReasonRefusal {
     	// Handle refusal appropriately
     }

java Java
     Message response = client.messages().create(...);

     StopReason reason = response.stopReason().orElse(StopReason.END_TURN);
     if (reason.equals(StopReason.REFUSAL)) {
         // Handle refusal appropriately
     }

php PHP
     $response = $client->messages->create(...);

     if ($response->stopReason === 'refusal') {
         // Handle refusal appropriately
     }

ruby Ruby
     response = client.messages.create(...)

     if response.stop_reason == :refusal
       # Handle refusal appropriately
     end

python Python
     response = client.messages.create(...)

     if response.stop_reason == "model_context_window_exceeded":
         # Handle context window limit appropriately
         pass

typescript TypeScript
     const response = await client.messages.create(/* ... */);

     if (response.stop_reason === "model_context_window_exceeded") {
       // Handle context window limit appropriately
     }

csharp C#
     var response = await client.Messages.Create(...);

     if (response.StopReason?.Raw() == "model_context_window_exceeded")
     {
         // Handle context window limit appropriately
     }

go Go
     response, _ := client.Messages.New(ctx, params) // your existing request

     if response.StopReason == "model_context_window_exceeded" {
     	// Handle context window limit appropriately
     }

java Java
     Message response = client.messages().create(...);

     StopReason reason = response.stopReason().orElse(StopReason.END_TURN);
     if (reason.equals(StopReason.of("model_context_window_exceeded"))) {
         // Handle context window limit appropriately
     }

php PHP
     $response = $client->messages->create(...);

     if ($response->stopReason === 'model_context_window_exceeded') {
         // Handle context window limit appropriately
     }

ruby Ruby
     response = client.messages.create(...)

     if response.stop_reason == :model_context_window_exceeded
       # Handle context window limit appropriately
     end
     ```
   </CodeGroup>

5. **Verify tool parameter handling (trailing newlines)**

   Claude 4.5+ models preserve trailing newlines in tool call string parameters that were previously stripped. If your tools rely on exact string matching against tool call parameters, verify your logic handles trailing newlines correctly.

6. **Update your prompts for behavioral changes**

   Claude 4+ models have a more concise, direct communication style and require explicit direction. Review [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) for optimization guidance.

#### Additional recommended changes

* **Remove legacy beta headers:** Remove `token-efficient-tools-2025-02-19` and `output-128k-2025-02-19`. All Claude 4+ models have built-in token-efficient tool use and these headers have no effect.

### Migration checklist (from Claude Opus 4.5 or earlier)

* Update model ID to `claude-opus-5`
* Apply all of the [breaking changes for migrating from Claude Opus 4.6](https://platform.claude.com/docs/en/models/opus-5/migration-guide#opus-46-breaking-changes) (extended thinking removed, thinking on by default, effort cap on disabling thinking, sampling parameters removed, thinking display omitted by default, updated tokenization)
* **BREAKING:** Remove assistant message prefills (returns 400 error); use structured outputs or `output_config.format` instead
* **BREAKING on Opus 4.7:** Replace `thinking: {type: "enabled", budget_tokens: N}` with `thinking: {type: "adaptive"}` plus the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) (returns 400 on Opus 4.7)
* Verify tool call JSON parsing uses a standard JSON parser
* Remove `effort-2025-11-24` beta header (the effort parameter does not require it)
* Remove `fine-grained-tool-streaming-2025-05-14` beta header
* Remove `interleaved-thinking-2025-05-14` beta header (adaptive thinking enables interleaved thinking automatically)
* Migrate `output_format` to `output_config.format` (if applicable)
* If migrating from Claude 4.1 or earlier: remove `temperature`, `top_p`, and `top_k` (non-default values return 400 on Opus 4.7)
* If migrating from Claude 4.1 or earlier: update tool versions (`text_editor_20250728`, `code_execution_20260521`)
* If migrating from Claude 4.1 or earlier: handle `refusal` stop reason
* If migrating from Claude 4.1 or earlier: handle `model_context_window_exceeded` stop reason
* If migrating from Claude 4.1 or earlier: verify tool string parameter handling for trailing newlines
* If migrating from Claude 4.1 or earlier: remove legacy beta headers (`token-efficient-tools-2025-02-19`, `output-128k-2025-02-19`)
* Review and update prompts following [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
* Test in development environment before production deployment


## Migrating to Claude Opus 5 from Claude Sonnet 5

Source: https://platform.claude.com/llms-full.txt#migrating-to-claude-opus-5-from-claude-sonnet-5

Claude Opus 5 and Claude Sonnet 5 share the same API surface: both run with [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) on by default, both default the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) to `high` on the Claude API and Claude Code, both serve a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) by default with [128k max output tokens](https://platform.claude.com/docs/en/models/overview), and neither supports [Priority Tier](https://platform.claude.com/docs/en/api/service-tiers#supported-models). Manual extended thinking and non-default sampling parameters return a 400 error on both models, as does assistant prefill.

### Update your model name

### What changed

1. **Pricing:** Claude Opus 5 is priced at $5 USD per million input tokens and $25 USD per million output tokens. Claude Sonnet 5 is priced at $2/$10 USD per million input/output tokens. See [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing) for complete pricing.

2. **Disabling thinking is capped at `high` effort:** On Claude Sonnet 5, `thinking: {type: "disabled"}` is accepted at any effort level. On Claude Opus 5, it is accepted only at an [effort](https://platform.claude.com/docs/en/build-with-claude/effort) level of `high` or below; a request that combines `thinking: {type: "disabled"}` with effort `xhigh` or `max` returns a 400 error, enforced on each request. Audit requests that disable thinking before you migrate.

3. **Mid-conversation system messages:** Claude Opus 5 accepts `role: "system"` messages immediately after a user turn in the `messages` array (subject to [placement rules](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#limitations)). This feature is not available on Claude Sonnet 5. If you maintain code paths that rebuild the full message history to update instructions, you can simplify them and preserve [prompt cache](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) hits on earlier turns.

4. **Web fetch is not available:** The [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) tool is available on Claude Sonnet 5 but not on Claude Opus 5.

### Migration checklist

* Update the model name from `claude-sonnet-5` to `claude-opus-5`.
* Audit requests that disable thinking: `thinking: {type: "disabled"}` with effort `xhigh` or `max` returns a 400 error on Claude Opus 5. Re-enable thinking or lower the effort to `high` or below.
* If you use [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool), plan an alternative: it is not available on Claude Opus 5.
* Re-run [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) against Claude Opus 5 rather than reusing counts measured against Claude Sonnet 5, and re-baseline cost and latency on your own workloads; per-token pricing differs.


---
title: What's new in Claude Opus 5
url: https://platform.claude.com/docs/en/models/opus-5/whats-new-opus-5
description: Overview of new features and behavior changes in Claude Opus 5.
---

Claude Opus 5 is a step-change improvement over Claude Opus 4.8, with the largest gains in deep reasoning, agentic and long-horizon tasks, and test-time compute scaling. This page summarizes everything new in Claude Opus 5, including mid-conversation tool changes and two breaking changes for code running on Claude Opus 4.8: thinking is on by default, and thinking can be disabled only at effort `high` or below.


## New model

Source: https://platform.claude.com/llms-full.txt#new-model

| Model         | API model ID    | Description                                    |
| ------------- | --------------- | ---------------------------------------------- |
| Claude Opus 5 | `claude-opus-5` | For complex agentic coding and enterprise work |

Claude Opus 5 has a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) (1M tokens is both the default and the maximum; there is no smaller context variant), 128k max output tokens, and [thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) on by default. [Priority Tier](https://platform.claude.com/docs/en/api/service-tiers#supported-models) is not supported on Claude Opus 5.

For complete pricing and specs, see the [models overview](https://platform.claude.com/docs/en/models/overview).


## New features

Source: https://platform.claude.com/llms-full.txt#new-features-2

### Mid-conversation tool changes (beta)

You can add or remove tools between turns of a conversation while preserving the prompt cache, instead of resending a fixed tool list for the life of a session. Mid-conversation tool changes are in beta: include the `mid-conversation-tool-changes-2026-07-01` beta header in your requests. See [Mid-conversation tool changes](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#mid-conversation-tool-changes) for usage.

### Default fallbacks mode

The `fallbacks` parameter supports a new `"default"` mode, which applies Anthropic's recommended fallback models by refusal category instead of a model list you maintain yourself. The entire `fallbacks` parameter is in beta. Use the `server-side-fallback-2026-07-01` beta header, which supports both the `"default"` mode and explicit model lists (the earlier `server-side-fallback-2026-06-01` header accepts only explicit lists). See [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback).

### Lower prompt cache minimum

The minimum cacheable prompt length on Claude Opus 5 is 512 tokens, down from 1,024 tokens on Claude Opus 4.8. Prompts that were too short to cache on Claude Opus 4.8 can now create cache entries with no code changes. See [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#cache-limitations) for per-model minimums.

### Fast mode

[Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) (research preview) is available for Claude Opus 5 on the Claude API only; it is not currently available on Amazon Bedrock, Claude Platform on AWS, Google Cloud, or Microsoft Foundry. Fast mode for Claude Opus 5 is priced at $10 USD per million input tokens and $50 USD per million output tokens. See [Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) for access, supported models, and pricing.


## Behavior changes

Source: https://platform.claude.com/llms-full.txt#behavior-changes

### Thinking on by default

On Claude Opus 4.8, requests run without thinking unless you set `thinking: {"type": "adaptive"}`. On Claude Opus 5, the same requests run with [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) on by default: the model decides when and how much to think on each turn, and the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) is the control for thinking depth. The wire value is unchanged; `thinking: {"type": "adaptive"}` remains valid and equivalent to the default.

This is a breaking change for code that ran without thinking on Claude Opus 4.8. A response can begin with one or more `thinking` blocks before the first `text` block, returned with an empty `thinking` field at the default `display: "omitted"`, so code that reads `content[0].text` or treats the first streamed content block as text must select content blocks by their `type` field instead. Tool-use loops must pass `thinking` blocks back complete and unmodified with their tool results; see [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks).

Thinking tokens are billed as output tokens and count toward `max_tokens`, a hard limit on total output (thinking plus response text), so revisit `max_tokens` and re-baseline cost for workloads that ran without thinking on Claude Opus 4.8.

The API keeps the option to disable thinking, subject to the [effort restriction](https://platform.claude.com/docs/en/models/opus-5/whats-new-opus-5#disabling-thinking-requires-effort-high-or-below) on disabling it.

### Effort matters more

Claude Opus 5 converts additional [effort](https://platform.claude.com/docs/en/build-with-claude/effort) into better results more reliably than any earlier Opus model, so the effort level you choose carries more weight. The full ladder is available: `low`, `medium`, `high`, `xhigh`, and `max`, with `max` as the top tier for the deepest possible reasoning. Start at the default, `high`, and adjust in either direction based on your evals: step down where quality holds to save tokens and latency, or step up for the most demanding work. When running at `xhigh` or `max` effort, set a large `max_tokens` so the model has room to think and act across subagents and tool calls.

This request turns effort all the way up to `max`:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 64000,
      "stream": true,
      "output_config": {
        "effort": "max"
      },
      "messages": [
        {
          "role": "user",
          "content": "Explain why the sum of two even numbers is always even."
        }
      ]
    }'

bash CLI
  # 64k max_tokens can run past the non-streaming time limit; stream the events.
  ant messages create --stream --format jsonl <<'YAML'
  model: claude-opus-5
  max_tokens: 64000
  output_config:
    effort: max
  messages:
    - role: user
      content: Explain why the sum of two even numbers is always even.
  YAML

python Python
  client = anthropic.Anthropic()

  with client.messages.stream(
      model="claude-opus-5",
      max_tokens=64000,
      output_config={"effort": "max"},
      messages=[
          {
              "role": "user",
              "content": "Explain why the sum of two even numbers is always even.",
          }
      ],
  ) as stream:
      response = stream.get_final_message()

  print(response)

typescript TypeScript
  const client = new Anthropic();

  const stream = client.messages.stream({
    model: "claude-opus-5",
    max_tokens: 64000,
    output_config: {
      effort: "max"
    },
    messages: [
      {
        role: "user",
        content: "Explain why the sum of two even numbers is always even."
      }
    ]
  });

  const response = await stream.finalMessage();
  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 64000,
      OutputConfig = new OutputConfig
      {
          Effort = Effort.Max
      },
      Messages = [new() { Role = Role.User, Content = "Explain why the sum of two even numbers is always even." }]
  };

  var response = await client.Messages.CreateStreaming(parameters).Aggregate();
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  stream := client.Messages.NewStreaming(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 64000,
  	OutputConfig: anthropic.OutputConfigParam{
  		Effort: anthropic.OutputConfigEffortMax,
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Explain why the sum of two even numbers is always even.")),
  	},
  })

  response := anthropic.Message{}
  for stream.Next() {
  	event := stream.Current()
  	if err := response.Accumulate(event); err != nil {
  		log.Fatal(err)
  	}
  }
  if err := stream.Err(); err != nil {
  	log.Fatal(err)
  }

  fmt.Println(response)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(64000L)
      .outputConfig(OutputConfig.builder()
          .effort(OutputConfig.Effort.MAX)
          .build())
      .addUserMessage("Explain why the sum of two even numbers is always even.")
      .build();

  MessageAccumulator accumulator = MessageAccumulator.create();
  try (var streamResponse = client.messages().createStreaming(params)) {
      streamResponse.stream().forEach(accumulator::accumulate);
  }

  Message response = accumulator.message();
  IO.println(response);

php PHP
  $client = new Client();

  $stream = $client->messages->createStream(
      maxTokens: 64000,
      messages: [
          ['role' => 'user', 'content' => 'Explain why the sum of two even numbers is always even.']
      ],
      model: Model::CLAUDE_OPUS_5,
      outputConfig: ['effort' => Effort::MAX],
  );

  $accumulator = MessageAccumulator::forMessages();
  foreach ($stream as $event) {
      $accumulator->accumulate($event);
  }

  echo $accumulator->message();

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.stream(
    model: Anthropic::Model::CLAUDE_OPUS_5,
    max_tokens: 64000,
    output_config: {
      effort: :max
    },
    messages: [
      { role: "user", content: "Explain why the sum of two even numbers is always even." }
    ]
  ).accumulated_message

  puts response
  ```
</CodeGroup>

Thinking is [on by default](https://platform.claude.com/docs/en/models/opus-5/whats-new-opus-5#thinking-on-by-default) on Claude Opus 5, so no `thinking` field is needed.

### Disabling thinking requires effort `high` or below

On Claude Opus 5, `thinking: {"type": "disabled"}` is accepted only when the effort level is `high` or below. Setting `thinking: {"type": "disabled"}` with effort `xhigh` or `max` returns a 400 error. This rule is enforced on every request to Claude Opus 5 and later models. It is a breaking change from Claude Opus 4.8, where disabling thinking was independent of the effort level. If your Claude Opus 4.8 requests disable thinking at effort `xhigh` or `max`, either keep thinking disabled and set effort to `high` or below, or keep the effort level and remove the `thinking` field.

With thinking disabled, Claude Opus 5 can occasionally write a tool call into its text output instead of emitting a `tool_use` block, or include internal XML tags in its visible response. Where possible, keep thinking enabled and control token cost with lower effort levels; for integrations that must keep thinking disabled, see [Running with thinking disabled](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#running-with-thinking-disabled) for prompting mitigations.

### Model behavior differences

Beyond these API changes, Claude Opus 5 behaves differently from Claude Opus 4.8 in ways you may notice without changing any code. Default user-facing responses and written deliverables run longer. In agentic sessions, the model narrates its progress to the user more often. In multi-agent frameworks, it delegates to subagents more readily. It also verifies its own work without being told to, so remove verification instructions carried over from earlier models ("include a final verification step," "use a subagent to verify"); they cause over-verification on Claude Opus 5. For prompting patterns that tune each of these behaviors, see [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5).


## Capability improvements

Source: https://platform.claude.com/llms-full.txt#capability-improvements-4

Compared with Claude Opus 4.8, Claude Opus 5 is a step-change improvement rather than an incremental one, and it delivers frontier intelligence at half the cost of [Claude Fable 5](https://platform.claude.com/docs/en/models/fable-5/introducing-claude-fable-5-and-claude-mythos-5). The largest gains are in:

* **Deep reasoning**, sustaining multistep analysis across long problem chains.
* **Agentic coding and long-horizon tasks**, staying on task across extended tool-use loops and completing multi-file features, larger refactors, and end-to-end feature work without leaving stubs or placeholders.
* **Test-time compute scaling**, converting additional effort (up to the `max` level) into better results.
* **Efficiency at lower effort levels**, with `low` and `medium` [effort](https://platform.claude.com/docs/en/build-with-claude/effort) producing strong quality at a fraction of the tokens and latency of higher settings.
* **Code review and bug-finding**, surfacing real bugs at a high rate per pass with few false positives, and staying accurate at lower effort levels.
* **Vision**, understanding charts, documents, and diagrams and replicating UI and frontend visuals, strongest when given tools to iteratively analyze, crop, and verify its work.
* **Long-context work**, with a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) as both the default and the maximum, and consistent instruction following, tool calling, and reasoning throughout the window.
* **Office and document tasks**, generating and editing complex multi-sheet spreadsheets with non-trivial formulas, and producing well-structured slide decks.
* **Multi-agent coordination**, running teams of subagents with effective writer-verifier patterns and few cases of agents overwriting each other's work.

For the prompting patterns that get the most out of these capabilities, see [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#capability-improvements).


## Pricing

Source: https://platform.claude.com/llms-full.txt#pricing-11

Claude Opus 5 is priced at $5 USD per million input tokens and $25 USD per million output tokens, unchanged from Claude Opus 4.8. Because thinking is on by default and thinking tokens are billed as output tokens, a workload that ran without thinking on Claude Opus 4.8 can produce more output tokens per request at the same per-token rates; see [Cost control](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#cost-control).

See [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) for complete pricing, including batch processing, prompt caching, and fast mode rates.


## Availability

Source: https://platform.claude.com/llms-full.txt#availability-3

Claude Opus 5 is available on:

* **Claude API:** available to all customers, as `claude-opus-5`.
* **AWS:** available through [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), as `anthropic.claude-opus-5`, and through [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws). On Amazon Bedrock, Claude Opus 5 is also reachable through the `InvokeModel` API on `bedrock-runtime`, served by the same infrastructure; the [Claude on Amazon Bedrock (legacy)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy) integration does not include it in its ARN-versioned model ID table.
* **Google Cloud:** available through [Claude on Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), as `claude-opus-5`.
* **Microsoft Foundry:** available through [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry).

Claude Opus 4.8 remains available on all of these platforms.


## Migration guide

Source: https://platform.claude.com/llms-full.txt#migration-guide-2

To migrate from Claude Opus 4.8, update your model ID:

<CodeGroup exclude="shell">
  ```python Python
  model = "claude-opus-4-8"  # Before
  model = "claude-opus-5"  # After

typescript TypeScript
  let model = "claude-opus-4-8"; // Before
  model = "claude-opus-5"; // After

csharp C#
  var model = Model.ClaudeOpus4_8; // Before
  model = Model.ClaudeOpus5; // After

go Go
  model := anthropic.ModelClaudeOpus4_8 // Before
  model = anthropic.ModelClaudeOpus5    // After

java Java
  Model model = Model.CLAUDE_OPUS_4_8; // Before
  model = Model.CLAUDE_OPUS_5; // After

php PHP
  $model = Model::CLAUDE_OPUS_4_8; // Before
  $model = Model::CLAUDE_OPUS_5; // After

ruby Ruby
  model = Anthropic::Model::CLAUDE_OPUS_4_8 # Before
  model = Anthropic::Model::CLAUDE_OPUS_5 # After
  ```
</CodeGroup>

Then review the two breaking changes under [Behavior changes](https://platform.claude.com/docs/en/models/opus-5/whats-new-opus-5#behavior-changes): thinking is on by default (responses can begin with `thinking` blocks, so select content blocks by `type`), and disabling thinking with effort `xhigh` or `max` returns a 400 error. See the [migration guide](https://platform.claude.com/docs/en/models/opus-5/migration-guide#migrating-from-claude-opus-4-8-to-claude-opus-5) for step-by-step instructions and the full checklist.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-104

<CardGroup cols={3}>
  <Card title="Models overview" icon="arrow-right" href="https://platform.claude.com/docs/en/models/overview">
    Complete specs and pricing for all current Claude models.
  </Card>

  <Card title="Prompting Claude Opus 5" icon="terminal" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5">
    Behavioral differences and prompting patterns specific to Claude Opus 5.
  </Card>

  <Card title="Effort" icon="gauge" href="https://platform.claude.com/docs/en/build-with-claude/effort">
    Control how many tokens Claude uses when responding, from low to max.
  </Card>

  <Card title="Thinking" icon="brain" href="https://platform.claude.com/docs/en/build-with-claude/thinking">
    How thinking works when it's on by default, and when it can be disabled.
  </Card>

  <Card title="Task budgets" icon="database" href="https://platform.claude.com/docs/en/build-with-claude/task-budgets">
    Give Claude an advisory token budget to pace its work against.
  </Card>

  <Card title="Migration guide" icon="code" href="https://platform.claude.com/docs/en/about-claude/models/migration-guide">
    Guide for migrating to the latest Claude models from previous Claude versions.
  </Card>

  <Card title="Fast mode" icon="bolt" href="https://platform.claude.com/docs/en/build-with-claude/fast-mode">
    Get higher output tokens per second from Claude Opus models at premium pricing.
  </Card>
</CardGroup>


### Models > Claude Sonnet 5

---
title: Claude Sonnet 5
url: https://platform.claude.com/docs/en/models/sonnet-5/overview
description: "Claude Sonnet 5 at a glance: what it's for, model IDs on every platform, context window, output limits, pricing, availability, and the guides and resources for building with it."
---

**Latest.** Released June 30, 2026.

The best combination of speed and intelligence

Model ID: `claude-sonnet-5`

Context window: 1M tokens · Max output: 128K tokens · Input pricing: $2 / MTok · Output pricing: $10 / MTok

[Announcement](https://www.anthropic.com/news/claude-sonnet-5) · [What’s new](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5) · [Migration guide](https://platform.claude.com/docs/en/models/sonnet-5/migration-guide)


## Overview

Source: https://platform.claude.com/llms-full.txt#overview-9

Claude Sonnet 5 is the next generation of Anthropic's Sonnet model family. It is a drop-in upgrade for Claude Sonnet 4.6 with three behavior changes: [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) is on by default, manual extended thinking now returns a 400 error (it was deprecated on Claude Sonnet 4.6), and setting sampling parameters (`temperature`, `top_p`, `top_k`) to non-default values returns a 400 error. This page summarizes everything new at launch, including a new tokenizer.

[What's new in Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5)


## How it compares

Source: https://platform.claude.com/llms-full.txt#how-it-compares-3

| Model                                                                             | Context | Max output | Price / MTok | Latency  | Thinking             | Default effort | Knowledge cutoff |
| :-------------------------------------------------------------------------------- | :------ | :--------- | :----------- | :------- | :------------------- | :------------- | :--------------- |
| [Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/overview) | 1M      | 128K       | $10 / $50    | Slower   | Adaptive (always on) | `high`         | Jun 2026         |
| [Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/overview)       | 1M      | 128K       | $5 / $25     | Moderate | Adaptive             | `high`         | May 2026         |
| **Claude Sonnet 5** (this model)                                                  | 1M      | 128K       | $2 / $10     | Fast     | Adaptive             | `high`         | Jan 2026         |
| [Claude Haiku 4.5](https://platform.claude.com/docs/en/models/haiku-4-5/overview) | 200K    | 64K        | $1 / $5      | Fastest  | Extended             | —              | Feb 2025         |

* **Context:** 1M tokens is roughly 555k words or 2.5M Unicode characters on the current tokenizer (introduced with Claude Opus 4.7); models before it fit about 750k words in 1M tokens. 200k tokens is roughly 150k words.
* **Max output:** Synchronous Messages API limit. On the Message Batches API, Claude Opus 5, Claude Sonnet 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, and Claude Sonnet 4.6 support up to 300k output tokens with the output-300k-2026-03-24 beta header.
* **Price / MTok:** Input / output, base price per million tokens. Batch API requests are 50% off; prompt caching reads cost 10% of the base input price (2.5% on Claude Fable 5.1 and Claude Mythos 5.1). See Pricing for the full list.
* **Latency:** Comparative latency, relative to the current lineup, as published in the models overview. Actual latency depends on prompt length, output length, and thinking effort.
* **Thinking:** Adaptive thinking lets the model decide how much to think, steered by effort. Extended thinking is the manual budget\_tokens mode on earlier models.
* **Default effort:** The effort parameter’s default on the Claude API. Models without a value don’t support the parameter.
* **Knowledge cutoff:** Reliable knowledge cutoff: the date through which the model’s knowledge is most extensive and reliable.


## Specifications

Source: https://platform.claude.com/llms-full.txt#specifications-3

### Model IDs

| Platform                                                                                               | Model ID                    |
| :----------------------------------------------------------------------------------------------------- | :-------------------------- |
| Claude API                                                                                             | `claude-sonnet-5`           |
| [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)       | `anthropic.claude-sonnet-5` |
| [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)              | `claude-sonnet-5`           |
| [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry) | `claude-sonnet-5`           |
| [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) | `claude-sonnet-5`           |

### Pricing

| Feature                                                                                | Value                                                               |
| :------------------------------------------------------------------------------------- | :------------------------------------------------------------------ |
| Input                                                                                  | $2 / MTok                                                           |
| Output                                                                                 | $10 / MTok                                                          |
| [5m cache write](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | $2.50 / MTok                                                        |
| [1h cache write](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | $4 / MTok                                                           |
| [Cache read](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)     | $0.20 / MTok                                                        |
| [Batch API](https://platform.claude.com/docs/en/build-with-claude/batch-processing)    | 50% discount on input and output                                    |
| Full price list                                                                        | [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) |

### Capabilities

| Feature                                                                                                                     | Value                  |
| :-------------------------------------------------------------------------------------------------------------------------- | :--------------------- |
| [Context window](https://platform.claude.com/docs/en/build-with-claude/context-windows)                                     | 1M tokens              |
| Max output                                                                                                                  | 128K tokens            |
| [Max output (Batch API, beta)](https://platform.claude.com/docs/en/build-with-claude/batch-processing#extended-output-beta) | 300K tokens            |
| [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)                                                  | Adaptive               |
| [Default effort](https://platform.claude.com/docs/en/build-with-claude/effort)                                              | `high`                 |
| Comparative latency                                                                                                         | Fast                   |
| Input → output                                                                                                              | Text and images → text |
| Reliable knowledge cutoff                                                                                                   | Jan 2026               |
| Training data cutoff                                                                                                        | Jan 2026               |

### Availability

| Feature                                                                       | Value                                                                                                                                                                                                                                                                                                                                                                                                                   |
| :---------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Status](https://platform.claude.com/docs/en/about-claude/model-deprecations) | Active (latest)                                                                                                                                                                                                                                                                                                                                                                                                         |
| Released                                                                      | June 30, 2026                                                                                                                                                                                                                                                                                                                                                                                                           |
| Retirement                                                                    | Not sooner than June 30, 2027                                                                                                                                                                                                                                                                                                                                                                                           |
| Platforms                                                                     | Claude API, [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) |


## Good to know

Source: https://platform.claude.com/llms-full.txt#good-to-know-2

* On the [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing#extended-output-beta), Claude Sonnet 5 supports up to 300k output tokens with the `output-300k-2026-03-24` beta header.
* Setting `temperature`, `top_p`, or `top_k` to non-default values returns a 400 error. See [What's new in Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5#sampling-parameters-not-accepted).
* Query limits and capabilities programmatically with the [Models API](https://platform.claude.com/docs/en/api/models/list).


## Resources

Source: https://platform.claude.com/llms-full.txt#resources-3

<CardGroup cols={3}>
  <Card title="Prompting Claude Sonnet 5" icon="lightbulb" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5">
    Model-specific prompting guidance.
  </Card>

  <Card title="Adaptive thinking" icon="brain" href="https://platform.claude.com/docs/en/build-with-claude/thinking">
    On by default on Claude Sonnet 5. Steer depth with `effort`.
  </Card>

  <Card title="Effort" icon="sliders" href="https://platform.claude.com/docs/en/build-with-claude/effort">
    Effort defaults to `high` on the Claude API and Claude Code. Choose a level per workload.
  </Card>

  <Card title="Context windows" icon="stack" href="https://platform.claude.com/docs/en/build-with-claude/context-windows">
    1M tokens by default. How the window is counted and managed.
  </Card>
</CardGroup>


## Reference

Source: https://platform.claude.com/llms-full.txt#reference-4

<CardGroup cols={3}>
  <Card title="System card" icon="file" href="https://www.anthropic.com/claude-sonnet-5-system-card">
    Safety evaluations and deployment decisions for Claude Sonnet 5.
  </Card>

  <Card title="Pricing" icon="coins" href="https://platform.claude.com/docs/en/about-claude/pricing">
    Full price list, including batch discounts and prompt caching rates.
  </Card>

  <Card title="Model IDs and versioning" icon="fingerprint" href="https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions">
    How model IDs, aliases, and pinned snapshots work.
  </Card>

  <Card title="Model deprecations" icon="clock" href="https://platform.claude.com/docs/en/about-claude/model-deprecations">
    Lifecycle status and retirement commitments for every Claude model.
  </Card>
</CardGroup>


---
title: Migrating to Claude Sonnet 5
url: https://platform.claude.com/docs/en/models/sonnet-5/migration-guide
description: "Migrate to Claude Sonnet 5 from earlier Claude models: model IDs, breaking changes, and migration checklists."
---

<Note>
  This guide covers migrating [Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) code. If you use [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview), no changes beyond updating the model name are required.
</Note>

<Tip>
  **Automate your migration with the Claude API skill.** In Claude Code, run `/claude-api migrate` to invoke the bundled [Claude API skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill#migrating-to-a-newer-claude-model). It works for any current Claude model as the target:

  ```text wrap
  /claude-api migrate this project to claude-sonnet-5
  ```

  The skill applies the model ID swap and, as needed, breaking parameter changes, prefill replacement, and effort calibration for your target model across your code base, then produces a checklist of items to verify manually. It asks you to confirm the migration scope (entire working directory, a subdirectory, or a specific file list) before editing any files. The skill also detects Amazon Bedrock and Claude Platform on AWS clients and adjusts model ID formats and feature changes for those platforms.
</Tip>

Claude Sonnet 5 offers the best combination of speed and intelligence in the Claude model family. It builds on Claude Sonnet 4.6.

Claude Sonnet 5 is a drop-in upgrade for Claude Sonnet 4.6, priced at $2/$10 USD per million input/output tokens; see [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) for details. There are two breaking API changes for code already running on Claude Sonnet 4.6. First, [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) is on by default and manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) returns a 400 error, so requests that ran without thinking can now return `thinking` blocks before the first `text` block and code that reads content by position must select content blocks by `type`. Second, sampling parameters (`temperature`, `top_p`, `top_k`) set to non-default values return a 400 error. Use adaptive thinking with the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) to control thinking depth. Claude Sonnet 5 supports the same set of features as Claude Sonnet 4.6, including the [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows), [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking), [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing), the [Files API](https://platform.claude.com/docs/en/build-with-claude/files), [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support), [vision](https://platform.claude.com/docs/en/build-with-claude/vision), and the full set of server-side and client-side [tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview). On the Claude API and Google Cloud, Claude Sonnet 5 also supports [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) as the stable `computer_toolset_20260801` toolset and the [browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) for tasks inside webpages, neither of which Claude Sonnet 4.6 supports; existing integrations on the earlier `computer_20251124` version continue to work unchanged on both models. To upgrade an existing integration, see [Migrate from `computer_20251124`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#migrate-from-computer-20251124). [Priority Tier](https://platform.claude.com/docs/en/api/service-tiers#supported-models) is not available on Claude Sonnet 5. Claude Sonnet 5 also uses a new tokenizer.


## Migrating to Claude Sonnet 5 from Claude Sonnet 4.6

Source: https://platform.claude.com/llms-full.txt#migrating-to-claude-sonnet-5-from-claude-sonnet-4-6

<Note>
  If your code is on Claude Sonnet 4.5 or earlier, also apply [Migrating to Claude Sonnet 5 from Claude Sonnet 4.5 and earlier Sonnet models](https://platform.claude.com/docs/en/models/sonnet-5/migration-guide#migrating-from-sonnet-45). Those steps include breaking changes (assistant message prefilling rejected, tool parameter JSON escaping differences) that this section alone does not cover.
</Note>

### Update your model name

### What changed

Items 4 and 5 in the following list are breaking changes. `max_tokens` remains a hard limit on total output (thinking plus response text), so revisit it for workloads that ran without thinking on Claude Sonnet 4.6.

1. **New tokenizer:** Claude Sonnet 5 uses a new tokenizer. The same input text produces approximately 30% more tokens than on Claude Sonnet 4.6. The exact increase depends on the content. Requests, responses, and streaming events keep the same shape, and no code changes are required, but anything you measure or budget in tokens shifts: `usage` fields and [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) results for the same text are higher, the 1M token context window holds less text, and a `max_tokens` limit tuned for Claude Sonnet 4.6 may truncate equivalent output. Per-token pricing is lower ($2/$10 USD versus Claude Sonnet 4.6's $3/$15 USD per million input/output tokens), but the cost of an equivalent request does not drop in direct proportion. Re-run token counting against Claude Sonnet 5 rather than reusing counts measured against earlier models.

2. **128k max output tokens (unchanged):** Claude Sonnet 5 supports up to 128k output tokens, the same as Claude Sonnet 4.6. Existing `max_tokens` values remain valid. Account for the new tokenizer when sizing them.

3. **Assistant message prefilling (unchanged):** Prefilling the assistant message returns a `400` error on Claude Sonnet 5, the same as on Claude Sonnet 4.6. If you removed prefill when migrating to Claude Sonnet 4.6, no further changes are needed. Use [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), system prompt instructions, or `output_config.format` instead.

4. **Adaptive thinking on by default:** On Claude Sonnet 4.6, requests without a `thinking` field run without thinking; on Claude Sonnet 5, the same requests run with [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking). To turn thinking off, pass `thinking: {type: "disabled"}`. Manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) is not supported and returns a 400 error. Use the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) (default `high`) to control thinking depth.

   With thinking on, a response can begin with one or more `thinking` blocks before the first `text` block, returned with an empty `thinking` field at the default `display: "omitted"`. Code that reads the reply by position, such as `content[0].text` or a stream handler that treats the first content block as text, must select content blocks by their `type` field instead, and tool-use loops must pass `thinking` blocks back complete and unmodified with their tool results (see [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks)). Thinking tokens are billed as output tokens even when the thinking text is not returned. If you used thinking on Claude Sonnet 4.6 and display the returned thinking text, note that `thinking.display` defaulted to `"summarized"` there and defaults to `"omitted"` on Claude Sonnet 5; set `display: "summarized"`, as the following example does, to keep receiving readable summaries (see [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display)).

   <Tabs>
     <Tab title="Claude Sonnet 5">
       <Note>
         Adaptive thinking is on by default for Claude Sonnet 5. The `thinking` field is shown explicitly here to set `display: "summarized"`; if you omit `thinking`, Claude Sonnet 5 omits thinking content from the response by default. For per-model defaults, see [Configurations each model rejects](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#rejected-configurations).
       </Note>

       <CodeGroup>
         ```bash cURL
         curl https://api.anthropic.com/v1/messages \
           -H "x-api-key: $ANTHROPIC_API_KEY" \
           -H "anthropic-version: 2023-06-01" \
           -H "content-type: application/json" \
           -d '{
             "model": "claude-sonnet-5",
             "max_tokens": 16000,
             "thinking": {
               "type": "adaptive",
               "display": "summarized"
             },
             "output_config": {
               "effort": "high"
             },
             "messages": [
               {
                 "role": "user",
                 "content": "Are there an infinite number of prime numbers such that n mod 4 == 3?"
               }
             ]
           }'

bash CLI
         ant messages create --transform content --format yaml <<'YAML'
         model: claude-sonnet-5
         max_tokens: 16000
         thinking:
           type: adaptive
           display: summarized
         output_config:
           effort: high
         messages:
           - role: user
             content: Are there an infinite number of prime numbers such that n mod 4 == 3?
         YAML

python Python
         client = anthropic.Anthropic()

         response = client.messages.create(
             model="claude-sonnet-5",
             max_tokens=16000,
             thinking={"type": "adaptive", "display": "summarized"},
             output_config={"effort": "high"},
             messages=[
                 {
                     "role": "user",
                     "content": "Are there an infinite number of prime numbers such that n mod 4 == 3?",
                 }
             ],
         )

         # The response contains summarized thinking blocks and text blocks
         for block in response.content:
             match block.type:
                 case "thinking":
                     print(f"\nThinking summary: {block.thinking}")
                 case "text":
                     print(f"\nResponse: {block.text}")

typescript TypeScript
         const client = new Anthropic();

         const response = await client.messages.create({
           model: "claude-sonnet-5",
           max_tokens: 16000,
           thinking: {
             type: "adaptive",
             display: "summarized"
           },
           output_config: {
             effort: "high"
           },
           messages: [
             {
               role: "user",
               content: "Are there an infinite number of prime numbers such that n mod 4 == 3?"
             }
           ]
         });

         // The response contains summarized thinking blocks and text blocks
         for (const block of response.content) {
           if (block.type === "thinking") {
             console.log(`\nThinking summary: ${block.thinking}`);
           } else if (block.type === "text") {
             console.log(`\nResponse: ${block.text}`);
           }
         }

csharp C#
         AnthropicClient client = new();

         var response = await client.Messages.Create(new()
         {
             Model = Model.ClaudeSonnet5,
             MaxTokens = 16000,
             Thinking = new ThinkingConfigAdaptive { Display = Display.Summarized },
             OutputConfig = new OutputConfig { Effort = Effort.High },
             Messages =
             [
                 new()
                 {
                     Role = Role.User,
                     Content = "Are there an infinite number of prime numbers such that n mod 4 == 3?",
                 },
             ],
         });

         // The response contains summarized thinking blocks and text blocks
         foreach (var block in response.Content)
         {
             if (block.TryPickThinking(out var thinking))
             {
                 Console.WriteLine($"\nThinking summary: {thinking.Thinking}");
             }
             else if (block.TryPickText(out var text))
             {
                 Console.WriteLine($"\nResponse: {text.Text}");
             }
         }

go Go
         client := anthropic.NewClient()

         response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
         	Model:     anthropic.ModelClaudeSonnet5,
         	MaxTokens: 16000,
         	Thinking: anthropic.ThinkingConfigParamUnion{
         		OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{
         			Display: anthropic.ThinkingConfigAdaptiveDisplaySummarized,
         		},
         	},
         	OutputConfig: anthropic.OutputConfigParam{
         		Effort: anthropic.OutputConfigEffortHigh,
         	},
         	Messages: []anthropic.MessageParam{
         		anthropic.NewUserMessage(anthropic.NewTextBlock("Are there an infinite number of prime numbers such that n mod 4 == 3?")),
         	},
         })
         if err != nil {
         	log.Fatal(err)
         }

         // The response contains summarized thinking blocks and text blocks
         for _, block := range response.Content {
         	switch block := block.AsAny().(type) {
         	case anthropic.ThinkingBlock:
         		fmt.Printf("\nThinking summary: %s", block.Thinking)
         	case anthropic.TextBlock:
         		fmt.Printf("\nResponse: %s", block.Text)
         	}
         }

java Java
         import com.anthropic.client.okhttp.AnthropicOkHttpClient;
         import com.anthropic.models.messages.MessageCreateParams;
         import com.anthropic.models.messages.Model;
         import com.anthropic.models.messages.OutputConfig;
         import com.anthropic.models.messages.ThinkingConfigAdaptive;

         void main() {
             var client = AnthropicOkHttpClient.fromEnv();

             var params = MessageCreateParams.builder()
                 .model(Model.CLAUDE_SONNET_5)
                 .maxTokens(16_000)
                 .thinking(ThinkingConfigAdaptive.builder()
                     .display(ThinkingConfigAdaptive.Display.SUMMARIZED)
                     .build())
                 .outputConfig(OutputConfig.builder()
                     .effort(OutputConfig.Effort.HIGH)
                     .build())
                 .addUserMessage("Are there an infinite number of prime numbers such that n mod 4 == 3?")
                 .build();

             var response = client.messages().create(params);

             // The response contains summarized thinking blocks and text blocks
             for (var block : response.content()) {
                 block.thinking().ifPresent(thinkingBlock ->
                     IO.println("\nThinking summary: " + thinkingBlock.thinking())
                 );
                 block.text().ifPresent(textBlock ->
                     IO.println("\nResponse: " + textBlock.text())
                 );
             }
         }

php PHP
         $client = new Client();

         $response = $client->messages->create(
             model: 'claude-sonnet-5',
             maxTokens: 16000,
             thinking: ['type' => 'adaptive', 'display' => 'summarized'],
             outputConfig: ['effort' => 'high'],
             messages: [
                 [
                     'role' => 'user',
                     'content' => 'Are there an infinite number of prime numbers such that n mod 4 == 3?',
                 ],
             ],
         );

         // The response contains summarized thinking blocks and text blocks
         foreach ($response->content as $block) {
             echo match ($block->type) {
                 'thinking' => "\nThinking summary: {$block->thinking}",
                 'text' => "\nResponse: {$block->text}",
                 default => '',
             };
         }

ruby Ruby
         client = Anthropic::Client.new

         response = client.messages.create(
           model: "claude-sonnet-5",
           max_tokens: 16_000,
           thinking: {type: :adaptive, display: :summarized},
           output_config: {effort: :high},
           messages: [
             {
               role: :user,
               content: "Are there an infinite number of prime numbers such that n mod 4 == 3?"
             }
           ]
         )

         # The response contains summarized thinking blocks and text blocks
         response.content.each do |block|
           case block
           in {type: :thinking, thinking:}
             puts "\nThinking summary: #{thinking}"
           in {type: :text, text:}
             puts "\nResponse: #{text}"
           else
           end
         end

bash cURL
         curl https://api.anthropic.com/v1/messages \
           -H "x-api-key: $ANTHROPIC_API_KEY" \
           -H "anthropic-version: 2023-06-01" \
           -H "content-type: application/json" \
           -d '{
             "model": "claude-sonnet-4-6",
             "max_tokens": 16000,
             "thinking": {
               "type": "enabled",
               "budget_tokens": 10000
             },
             "messages": [
               {
                 "role": "user",
                 "content": "Are there an infinite number of prime numbers such that n mod 4 == 3?"
               }
             ]
           }'

bash CLI
         ant messages create \
           --transform content --format yaml <<'YAML'
         model: claude-sonnet-4-6
         max_tokens: 16000
         thinking:
           type: enabled
           budget_tokens: 10000
         messages:
           - role: user
             content: Are there an infinite number of prime numbers such that n mod 4 == 3?
         YAML

python Python
         client = anthropic.Anthropic()

         response = client.messages.create(
             model="claude-sonnet-4-6",
             max_tokens=16000,
             thinking={"type": "enabled", "budget_tokens": 10000},
             messages=[
                 {
                     "role": "user",
                     "content": "Are there an infinite number of prime numbers such that n mod 4 == 3?",
                 }
             ],
         )

         # The response contains summarized thinking blocks and text blocks
         for block in response.content:
             match block.type:
                 case "thinking":
                     print(f"\nThinking summary: {block.thinking}")
                 case "text":
                     print(f"\nResponse: {block.text}")

typescript TypeScript
         const client = new Anthropic();

         const response = await client.messages.create({
           model: "claude-sonnet-4-6",
           max_tokens: 16000,
           thinking: {
             type: "enabled",
             budget_tokens: 10000,
           },
           messages: [
             {
               role: "user",
               content: "Are there an infinite number of prime numbers such that n mod 4 == 3?",
             },
           ],
         });

         // The response contains summarized thinking blocks and text blocks
         for (const block of response.content) {
           if (block.type === "thinking") {
             console.log(`\nThinking summary: ${block.thinking}`);
           } else if (block.type === "text") {
             console.log(`\nResponse: ${block.text}`);
           }
         }

csharp C#
         AnthropicClient client = new();

         var response = await client.Messages.Create(new()
         {
             Model = Model.ClaudeSonnet4_6,
             MaxTokens = 16000,
             Thinking = new ThinkingConfigEnabled(budgetTokens: 10000),
             Messages =
             [
                 new()
                 {
                     Role = Role.User,
                     Content = "Are there an infinite number of prime numbers such that n mod 4 == 3?",
                 },
             ],
         });

         // The response contains summarized thinking blocks and text blocks
         foreach (var block in response.Content)
         {
             if (block.TryPickThinking(out var thinking))
             {
                 Console.WriteLine($"\nThinking summary: {thinking.Thinking}");
             }
             else if (block.TryPickText(out var text))
             {
                 Console.WriteLine($"\nResponse: {text.Text}");
             }
         }

go Go
         client := anthropic.NewClient()

         response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
         	Model:     anthropic.ModelClaudeSonnet4_6,
         	MaxTokens: 16000,
         	Thinking:  anthropic.ThinkingConfigParamOfEnabled(10000),
         	Messages: []anthropic.MessageParam{
         		anthropic.NewUserMessage(anthropic.NewTextBlock("Are there an infinite number of prime numbers such that n mod 4 == 3?")),
         	},
         })
         if err != nil {
         	log.Fatal(err)
         }

         // The response contains summarized thinking blocks and text blocks
         for _, block := range response.Content {
         	switch block := block.AsAny().(type) {
         	case anthropic.ThinkingBlock:
         		fmt.Printf("\nThinking summary: %s", block.Thinking)
         	case anthropic.TextBlock:
         		fmt.Printf("\nResponse: %s", block.Text)
         	}
         }

java Java
         import com.anthropic.client.okhttp.AnthropicOkHttpClient;
         import com.anthropic.models.messages.MessageCreateParams;
         import com.anthropic.models.messages.Model;

         void main() {
             var client = AnthropicOkHttpClient.fromEnv();

             var params = MessageCreateParams.builder()
                 .model(Model.CLAUDE_SONNET_4_6)
                 .maxTokens(16_000)
                 .enabledThinking(10_000)
                 .addUserMessage("Are there an infinite number of prime numbers such that n mod 4 == 3?")
                 .build();

             var response = client.messages().create(params);

             // The response contains summarized thinking blocks and text blocks
             for (var block : response.content()) {
                 block.thinking().ifPresent(thinkingBlock ->
                     IO.println("\nThinking summary: " + thinkingBlock.thinking())
                 );
                 block.text().ifPresent(textBlock ->
                     IO.println("\nResponse: " + textBlock.text())
                 );
             }
         }

php PHP
         $client = new Client();

         $response = $client->messages->create(
             model: 'claude-sonnet-4-6',
             maxTokens: 16000,
             thinking: ['type' => 'enabled', 'budget_tokens' => 10000],
             messages: [
                 [
                     'role' => 'user',
                     'content' => 'Are there an infinite number of prime numbers such that n mod 4 == 3?',
                 ],
             ],
         );

         // The response contains summarized thinking blocks and text blocks
         foreach ($response->content as $block) {
             echo match ($block->type) {
                 'thinking' => "\nThinking summary: {$block->thinking}",
                 'text' => "\nResponse: {$block->text}",
                 default => '',
             };
         }

ruby Ruby
         client = Anthropic::Client.new

         response = client.messages.create(
           model: "claude-sonnet-4-6",
           max_tokens: 16_000,
           thinking: {
             type: :enabled,
             budget_tokens: 10_000
           },
           messages: [
             {
               role: :user,
               content: "Are there an infinite number of prime numbers such that n mod 4 == 3?"
             }
           ]
         )

         # The response contains summarized thinking blocks and text blocks
         response.content.each do |block|
           case block
           in {type: :thinking, thinking:}
             puts "\nThinking summary: #{thinking}"
           in {type: :text, text:}
             puts "\nResponse: #{text}"
           else
           end
         end
         ```
       </CodeGroup>
     </Tab>
   </Tabs>

5. **Sampling parameters removed:** Sampling parameters (`temperature`, `top_p`, `top_k`) set to a non-default value are not accepted and return a 400 error.

6. **Cybersecurity safeguards:** Claude Sonnet 5 is the first Sonnet-tier model with real-time cybersecurity safeguards. Requests that involve prohibited or high-risk cybersecurity topics may be refused. Refusals return as a successful HTTP 200 response with `stop_reason: "refusal"`, not an error. See [Real-time cyber safeguards on Claude Opus and Sonnet](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet) for what the safeguards block and how legitimate security work can apply to the Cyber Verification Program.

### Migration checklist

* Update model name from `claude-sonnet-4-6` to `claude-sonnet-5`.
* Re-run [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) against Claude Sonnet 5. The new tokenizer produces approximately 30% more tokens for the same text, which can change per-request cost even though per-token pricing is lower. The exact increase depends on the content and workload shape.
* Revisit `max_tokens` limits sized close to your expected output length, and raise them up to the 128k maximum (unchanged from Claude Sonnet 4.6) where useful.
* Remove `thinking: {type: "enabled", budget_tokens: N}` configuration (returns a 400 error). Adaptive thinking is on by default; pass `{type: "disabled"}` to turn it off, or use the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) to control depth.
* Update response parsing that reads content by position, such as `content[0].text`: with thinking on, `thinking` blocks arrive before `text` blocks. Select content blocks by `type` instead, and pass `thinking` blocks back unmodified in tool-use loops; modified blocks return a 400 error.
* Verify any code that parses the `thinking` field treats it as display text only. `thinking.display` defaults to `"omitted"` on Claude Sonnet 5 (it defaulted to `"summarized"` on Claude Sonnet 4.6), so thinking blocks arrive with an empty `thinking` field; set `display: "summarized"` to receive readable summaries. See [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display).
* Remove `temperature`, `top_p`, and `top_k` parameters set to non-default values (they return a 400 error on Claude Sonnet 5).
* Add handling for `stop_reason: "refusal"` if your workload may touch cybersecurity topics.
* Re-baseline cost on your typical workload before production deployment.
* Review `max_tokens` for workloads that previously ran without thinking.


## Migrating to Claude Sonnet 5 from Claude Sonnet 4.5 and earlier Sonnet models

Source: https://platform.claude.com/llms-full.txt#migrating-to-claude-sonnet-5-from-claude-sonnet-4-5-and-earlier-sonnet-models

If you are migrating from Claude Sonnet 4.5 or an earlier Sonnet model directly to Claude Sonnet 5, apply the [Migrating to Claude Sonnet 5 from Claude Sonnet 4.6](https://platform.claude.com/docs/en/models/sonnet-5/migration-guide#migrating-from-claude-sonnet-4-6-to-claude-sonnet-5) changes plus the changes in this section.

<Warning>
  Claude Sonnet 5 defaults to an effort level of `high`, in contrast to Sonnet 4.5 which had no effort parameter. Consider adjusting the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) as you migrate. If not explicitly set, you may experience higher latency with the default effort level.
</Warning>

### Breaking changes

#### When migrating from Sonnet 4.5

1. **Prefilling assistant messages is no longer supported**

   <Warning>
     This is a breaking change when migrating from Sonnet 4.5 or earlier.
   </Warning>

   Prefilling assistant messages returns a `400` error on Claude Sonnet 4.6 and later models, including Claude Sonnet 5. Use [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), system prompt instructions, or `output_config.format` instead.

   **Common prefill use cases and migrations:**

   * **Controlling output formatting** (forcing JSON/YAML output): Use [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) or tools with enum fields for classification tasks.

   * **Eliminating preambles** (removing "Here is..." phrases): Add direct instructions in the system prompt: "Respond directly without preamble. Do not start with phrases like 'Here is...', 'Based on...', etc."

   * **Avoiding bad refusals:** Claude is much better at appropriate refusals now. Clear prompting in the user message without prefill should be sufficient.

   * **Continuations** (resuming interrupted responses): Move the continuation to the user message: "Your previous response was interrupted and ended with `[previous_response]`. Continue from where you left off."

   * **Context hydration / role consistency** (refreshing context in long conversations): Inject what were previously prefilled-assistant reminders into the user turn instead.

2. **Tool parameter JSON escaping may differ**

   <Warning>
     This is a breaking change when migrating from Sonnet 4.5 or earlier.
   </Warning>

   JSON string escaping in tool parameters may differ from previous models. Standard JSON parsers handle this automatically, but custom string-based parsing may need updates.

**Extended thinking changes:** `budget_tokens` configurations from Claude Sonnet 4.5 (`thinking: {type: "enabled", budget_tokens: N}`) are not supported on Claude Sonnet 5 and return a 400 error. Adaptive thinking is on by default, so most workloads need no `thinking` configuration at all; use the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) to control thinking depth. If you ran Claude Sonnet 4.5 without extended thinking, pass `thinking: {type: "disabled"}` to preserve that behavior.

#### When migrating from Claude 3.x

3. **Remove sampling parameters**

   <Warning>
     This is a breaking change when migrating from Claude 3.x models.
   </Warning>

   Sampling parameters (`temperature`, `top_p`, `top_k`) set to a non-default value return a 400 error on Claude Sonnet 5. Remove them from requests, and use prompting to guide the model's behavior instead.

4. **Update tool versions**

   <Warning>
     This is a breaking change when migrating from Claude 3.x models.
   </Warning>

   Update to the latest tool versions (`text_editor_20250728`, `code_execution_20260521`). Remove any code using the `undo_edit` command.

5. **Handle the `refusal` stop reason**

   Update your application to [handle `refusal` stop reasons](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals).

6. **Update your prompts for behavioral changes**

   Claude 4 models have a more concise, direct communication style. Review [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) for optimization guidance.


## Migrating to Claude Sonnet 5 from Claude Haiku 4.5

Source: https://platform.claude.com/llms-full.txt#migrating-to-claude-sonnet-5-from-claude-haiku-4-5

Claude Haiku 4.5 and Claude Sonnet 5 differ more at the API level than adjacent models within one class: Claude Haiku 4.5 uses manual [extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) (off by default), a 200k token context window, and up to 64k output tokens, while Claude Sonnet 5 runs with [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) on by default, serves a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) by default, and supports up to [128k output tokens](https://platform.claude.com/docs/en/models/overview).

### Update your model name

### What changed

1. **Thinking configuration:** Claude Haiku 4.5 supports manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) and rejects `thinking: {type: "adaptive"}`. On Claude Sonnet 5, the support is reversed: adaptive thinking is on by default, and manual extended thinking returns a 400 error. Remove `thinking: {type: "enabled", budget_tokens: N}` configurations and rely on the default, or pass `thinking: {type: "disabled"}` to turn thinking off. `budget_tokens` has no direct replacement; use the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) to control thinking depth. Effort is not available on Claude Haiku 4.5 and defaults to `high` on Claude Sonnet 5.

   The response shape changes for both kinds of Claude Haiku 4.5 request. Requests that ran without extended thinking can now return one or more `thinking` blocks before the first `text` block, so code that reads the reply by position, such as `content[0].text`, must select content blocks by their `type` field instead, and tool-use loops must pass `thinking` blocks back complete and unmodified with their tool results (see [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks)). Requests that used extended thinking keep receiving `thinking` blocks, but `thinking.display` defaults to `"omitted"` on Claude Sonnet 5 rather than `"summarized"`, so those blocks arrive with an empty `thinking` field; set `display: "summarized"` to keep receiving readable summaries (see [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display)). Thinking tokens are billed as output tokens even when the thinking text is not returned.

2. **Sampling parameters removed:** `temperature` and `top_p` work on Claude Haiku 4.5 (one at a time, not both). On Claude Sonnet 5, setting `temperature`, `top_p`, or `top_k` to a non-default value returns a 400 error. Remove these parameters and use prompting to guide the model's behavior.

3. **Assistant prefill removed:** Prefilling the assistant message works on Claude Haiku 4.5 but returns a 400 error on Claude Sonnet 5. Use [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), system prompt instructions, or `output_config.format` instead.

4. **Larger context window and output:** Claude Sonnet 5 serves a 1M token context window by default, up from 200k tokens on Claude Haiku 4.5, and supports up to 128k output tokens, up from 64k. Claude Sonnet 5 also uses a different tokenizer, so re-run [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) rather than reusing counts measured against Claude Haiku 4.5.

5. **Pricing:** Claude Haiku 4.5 is priced at $1/$5 USD per million input/output tokens. Claude Sonnet 5 is priced at $2/$10 USD per million input/output tokens. See [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing).

6. **Cybersecurity safeguards:** Claude Sonnet 5 has real-time cybersecurity safeguards. Requests that involve prohibited or high-risk cybersecurity topics may be refused, returned as a successful HTTP 200 response with `stop_reason: "refusal"`. See [Real-time cyber safeguards on Claude Opus and Sonnet](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet) for what the safeguards block and how legitimate security work can apply to the Cyber Verification Program.

### Migration checklist

* Update the model name from `claude-haiku-4-5-20251001` (or the `claude-haiku-4-5` alias) to `claude-sonnet-5`.
* Remove `thinking: {type: "enabled", budget_tokens: N}` configuration (returns a 400 error). Adaptive thinking is on by default; pass `thinking: {type: "disabled"}` to preserve no-thinking behavior, and revisit `max_tokens` for workloads that ran without thinking.
* Update response parsing that reads content by position, such as `content[0].text`: with thinking on, `thinking` blocks arrive before `text` blocks. Select content blocks by `type` instead, and pass `thinking` blocks back unmodified in tool-use loops; modified blocks return a 400 error.
* If your UI displays thinking content, set `display: "summarized"`. `thinking.display` defaults to `"omitted"` on Claude Sonnet 5, so thinking blocks otherwise arrive with an empty `thinking` field. See [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display).
* Use the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) (default `high`) to control thinking depth and token spend; it is not available on Claude Haiku 4.5, so no existing setting carries over.
* Remove `temperature` and `top_p` settings (non-default values return a 400 error on Claude Sonnet 5).
* Remove any assistant-message prefills (they return a 400 error on Claude Sonnet 5).
* Re-run [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) against Claude Sonnet 5, and revisit `max_tokens` limits, which you can raise up to the 128k maximum.
* Add handling for `stop_reason: "refusal"` if your workload may touch cybersecurity topics.
* Re-baseline cost on your typical workload before production deployment; per-token pricing differs.


---
title: What's new in Claude Sonnet 5
url: https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5
description: Overview of new features and behavior changes in Claude Sonnet 5.
---

Claude Sonnet 5 is the next generation of Anthropic's Sonnet model family. It is a drop-in upgrade for Claude Sonnet 4.6 with three behavior changes: [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) is on by default, manual extended thinking now returns a 400 error (it was deprecated on Claude Sonnet 4.6), and setting sampling parameters (`temperature`, `top_p`, `top_k`) to non-default values returns a 400 error. This page summarizes everything new at launch, including a new tokenizer.


## New model

Source: https://platform.claude.com/llms-full.txt#new-model-2

| Model           | API model ID      | Description                                    |
| --------------- | ----------------- | ---------------------------------------------- |
| Claude Sonnet 5 | `claude-sonnet-5` | The best combination of speed and intelligence |

Claude Sonnet 5 supports the [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) by default (1M tokens is both the default and the maximum; there is no smaller context variant), 128k max output tokens, [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking), and the same set of tools and platform features as Claude Sonnet 4.6, except [Priority Tier](https://platform.claude.com/docs/en/api/service-tiers#supported-models), which is not available on Claude Sonnet 5. On the Claude API and Google Cloud, Claude Sonnet 5 also supports the [browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) and the stable `computer_toolset_20260801` version of the [computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool), neither of which Claude Sonnet 4.6 supports; the earlier `computer_20251124` version is still accepted on both models. To upgrade an existing integration, see [Migrate from `computer_20251124`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#migrate-from-computer-20251124).

For complete pricing and specs, see the [models overview](https://platform.claude.com/docs/en/models/overview).


## Behavior changes

Source: https://platform.claude.com/llms-full.txt#behavior-changes-2

### Adaptive thinking on by default

On Claude Sonnet 4.6, requests without a `thinking` field run without thinking. On Claude Sonnet 5, the same requests run with [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking). To turn thinking off, pass `thinking: {type: "disabled"}`. Because `max_tokens` is a hard limit on total output (thinking plus response text), revisit it for workloads that ran without thinking on Claude Sonnet 4.6.

### Sampling parameters not accepted

Setting `temperature`, `top_p`, or `top_k` to a non-default value returns a 400 error. Remove these parameters when migrating; the default value (or omitting the parameter) is accepted. Use system-prompt instructions to guide model behavior. This is new for Sonnet-class models; the same constraint was previously introduced on Claude Opus 4.7.

### Manual extended thinking removed

Manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) was deprecated on Claude Sonnet 4.6; on Claude Sonnet 5 it is removed and returns a 400 error, the same as on Claude Opus 4.8 and Claude Opus 4.7. Use adaptive thinking with the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) instead.

<CodeGroup exclude="shell">
  ```python Python
  # Not supported on Claude Sonnet 5 (returns 400)
  thinking = {"type": "enabled", "budget_tokens": 32000}

  # Use this instead
  thinking = {"type": "adaptive"}

typescript TypeScript
  // Not supported on Claude Sonnet 5 (returns 400)
  const legacyThinking = { type: "enabled", budget_tokens: 32000 };

  // Use this instead
  const thinking = { type: "adaptive" };

csharp C#
  // Not supported on Claude Sonnet 5 (returns 400)
  var legacyThinking = new ThinkingConfigEnabled(budgetTokens: 32000);

  // Use this instead
  var thinking = new ThinkingConfigAdaptive();

go Go
  // Not supported on Claude Sonnet 5 (returns 400)
  legacyThinking := anthropic.ThinkingConfigParamUnion{
  	OfEnabled: &anthropic.ThinkingConfigEnabledParam{BudgetTokens: 32000},
  }

  // Use this instead
  thinking := anthropic.ThinkingConfigParamUnion{
  	OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{},
  }

java Java
  // Not supported on Claude Sonnet 5 (returns 400)
  var legacyThinking = ThinkingConfigEnabled.builder().budgetTokens(32_000L).build();

  // Use this instead
  var thinking = ThinkingConfigAdaptive.builder().build();

php PHP
  // Not supported on Claude Sonnet 5 (returns 400)
  $thinking = ['type' => 'enabled', 'budget_tokens' => 32000];

  // Use this instead
  $thinking = ['type' => 'adaptive'];

ruby Ruby
  # Not supported on Claude Sonnet 5 (returns 400)
  legacy_thinking = {type: "enabled", budget_tokens: 32_000}

  # Use this instead
  thinking = {type: "adaptive"}
  ```
</CodeGroup>


## New tokenizer

Source: https://platform.claude.com/llms-full.txt#new-tokenizer

Claude Sonnet 5 uses a new tokenizer. The same input text produces approximately 30% more tokens than on Claude Sonnet 4.6. The exact increase depends on the content. This is not an API change: requests, responses, and streaming events keep the same shape, and no code changes are required.

The change affects anything you measure or budget in tokens:

* **Token counts:** `usage` fields and [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) results for the same text are higher than on Claude Sonnet 4.6. Don't reuse counts measured against earlier models; recount against Claude Sonnet 5.
* **Context window capacity in text terms:** the context window is 1M tokens, but each token covers less text on average, so the same window holds less text than on Claude Sonnet 4.6.
* **`max_tokens` budgets:** an output limit tuned for Claude Sonnet 4.6 may truncate equivalent output on Claude Sonnet 5. Revisit limits sized close to your expected output length.
* **Per-request cost:** per-token pricing is lower than Claude Sonnet 4.6's (see [Pricing](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5#pricing)), but because the same text produces more tokens, the cost of an equivalent request does not drop in direct proportion.


## API constraints inherited from Claude Sonnet 4.6

Source: https://platform.claude.com/llms-full.txt#api-constraints-inherited-from-claude-sonnet-4-6

<Note>
  This constraint is unchanged from Claude Sonnet 4.6. Aside from the three [behavior changes](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5#behavior-changes) (see [Migration guide](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5#migration-guide)), code that already runs on Claude Sonnet 4.6 needs no other changes.
</Note>

### Assistant message prefilling not supported

Prefilling the assistant message returns a `400` error, unchanged from Claude Sonnet 4.6. Use [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), system prompt instructions, or `output_config.format` instead.


## Capability improvements

Source: https://platform.claude.com/llms-full.txt#capability-improvements-5

Claude Sonnet 5 is a capability upgrade over Claude Sonnet 4.6 at a lower price. It is also an option for workloads that need more capability than Claude Sonnet 4.6 provides without moving to an Opus-class model.

The largest gains over Claude Sonnet 4.6 are in coding and agentic tasks. For benchmark results, see [Anthropic's Transparency Hub](https://www.anthropic.com/transparency).


## Cybersecurity safeguards

Source: https://platform.claude.com/llms-full.txt#cybersecurity-safeguards

Claude Sonnet 5 is the first Sonnet-tier model with real-time cybersecurity safeguards. Requests that involve prohibited or high-risk cybersecurity topics may be refused. Refusals return as a successful HTTP 200 response with `stop_reason: "refusal"`, not an error. See [Real-time cyber safeguards on Claude Opus and Sonnet](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet) for what the safeguards block and how legitimate security work can apply to the Cyber Verification Program.


## Pricing

Source: https://platform.claude.com/llms-full.txt#pricing-12

Claude Sonnet 5 is priced at $2 per million input tokens and $10 per million output tokens, lower per-token pricing than Claude Sonnet 4.6's $3/$15. Because the [new tokenizer](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5#new-tokenizer) produces approximately 30% more tokens for the same text, the cost of an equivalent request does not drop in direct proportion to the per-token prices when comparing with Claude Sonnet 4.6. The exact difference depends on the content and workload shape.

See [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) for complete pricing, including batch processing and prompt caching rates.


## Availability

Source: https://platform.claude.com/llms-full.txt#availability-4

At launch, Claude Sonnet 5 is available on:

* **Claude API:** available to all customers.
* **AWS:** available through [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) and [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws). On Amazon Bedrock, Claude Sonnet 5 is also reachable through the `InvokeModel` API, served by the same infrastructure as Claude in Amazon Bedrock. The legacy [Claude on Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy) integration does not include Claude Sonnet 5.
* **Google Cloud:** available through [Claude on Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai).
* **Microsoft Foundry:** available through [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry).

Claude Sonnet 5 supports [zero data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) for organizations with ZDR agreements.


## Migration guide

Source: https://platform.claude.com/llms-full.txt#migration-guide-3

Claude Sonnet 5 is a drop-in replacement for Claude Sonnet 4.6. Update your model ID:

<CodeGroup exclude="shell">
  ```python Python
  model = "claude-sonnet-4-6"  # Before
  model = "claude-sonnet-5"  # After

typescript TypeScript
  const legacyModel = "claude-sonnet-4-6"; // Before
  const model = "claude-sonnet-5"; // After

csharp C#
  var legacyModel = Model.ClaudeSonnet4_6; // Before
  var model = Model.ClaudeSonnet5; // After

go Go
  // Before
  legacyModel := anthropic.ModelClaudeSonnet4_6
  // After
  model := anthropic.ModelClaudeSonnet5

java Java
  var legacyModel = Model.CLAUDE_SONNET_4_6; // Before
  var model = Model.CLAUDE_SONNET_5; // After

php PHP
  $model = 'claude-sonnet-4-6'; // Before
  $model = 'claude-sonnet-5'; // After

ruby Ruby
  legacy_model = "claude-sonnet-4-6" # Before
  model = "claude-sonnet-5" # After
  ```
</CodeGroup>

Then review the following:

1. **Token budgets and counts:** the [new tokenizer](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5#new-tokenizer) produces approximately 30% more tokens for the same text. The exact increase depends on the content and workload shape. Recount prompts with [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting), and revisit `max_tokens` limits sized close to your expected output length.
2. **Extended thinking:** if you still set `budget_tokens`, migrate to [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking). Manual extended thinking (`thinking: {type: "enabled"}`) is not supported and returns a 400 error.
3. **Sampling parameters:** requests that set sampling parameters (`temperature`, `top_p`, `top_k`) to a non-default value return a 400 error; remove them when migrating. Tool definitions and response shapes are unchanged, and assistant message prefilling was already unsupported on Claude Sonnet 4.6.

See [Migrating to Claude Sonnet 5 from Claude Sonnet 4.6](https://platform.claude.com/docs/en/models/sonnet-5/migration-guide#migrating-from-claude-sonnet-4-6-to-claude-sonnet-5) for details.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-105

<CardGroup>
  <Card title="Models overview" icon="arrow-right" href="https://platform.claude.com/docs/en/models/overview">
    Complete specs and pricing for all current Claude models.
  </Card>

  <Card title="Token counting" icon="database" href="https://platform.claude.com/docs/en/build-with-claude/token-counting">
    Measure your prompts under the new tokenizer before you migrate.
  </Card>

  <Card title="Adaptive thinking" icon="brain" href="https://platform.claude.com/docs/en/build-with-claude/thinking">
    The recommended thinking-on mode on Claude Sonnet 5.
  </Card>

  <Card title="Context windows" icon="sliders" href="https://platform.claude.com/docs/en/build-with-claude/context-windows">
    How the 1M token context window works.
  </Card>

  <Card title="Pricing" icon="shield" href="https://platform.claude.com/docs/en/about-claude/pricing">
    Complete pricing, including batch processing and prompt caching rates.
  </Card>
</CardGroup>


### Models > Claude Haiku 4.5

---
title: Claude Haiku 4.5
url: https://platform.claude.com/docs/en/models/haiku-4-5/overview
description: "Claude Haiku 4.5 at a glance: what it's for, model IDs on every platform, context window, output limits, pricing, availability, and the guides and resources for building with it."
---

**Latest.** Released October 15, 2025.

The fastest model with near-frontier intelligence

Model ID: `claude-haiku-4-5-20251001`

Context window: 200K tokens · Max output: 64K tokens · Input pricing: $1 / MTok · Output pricing: $5 / MTok

[Announcement](https://www.anthropic.com/news/claude-haiku-4-5) · [Migration guide](https://platform.claude.com/docs/en/models/haiku-4-5/migration-guide)


## How it compares

Source: https://platform.claude.com/llms-full.txt#how-it-compares-4

| Model                                                                             | Context | Max output | Price / MTok | Latency  | Thinking             | Default effort | Knowledge cutoff |
| :-------------------------------------------------------------------------------- | :------ | :--------- | :----------- | :------- | :------------------- | :------------- | :--------------- |
| [Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/overview) | 1M      | 128K       | $10 / $50    | Slower   | Adaptive (always on) | `high`         | Jun 2026         |
| [Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/overview)       | 1M      | 128K       | $5 / $25     | Moderate | Adaptive             | `high`         | May 2026         |
| [Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/overview)   | 1M      | 128K       | $2 / $10     | Fast     | Adaptive             | `high`         | Jan 2026         |
| **Claude Haiku 4.5** (this model)                                                 | 200K    | 64K        | $1 / $5      | Fastest  | Extended             | —              | Feb 2025         |

* **Context:** 1M tokens is roughly 555k words or 2.5M Unicode characters on the current tokenizer (introduced with Claude Opus 4.7); models before it fit about 750k words in 1M tokens. 200k tokens is roughly 150k words.
* **Max output:** Synchronous Messages API limit. On the Message Batches API, Claude Opus 5, Claude Sonnet 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, and Claude Sonnet 4.6 support up to 300k output tokens with the output-300k-2026-03-24 beta header.
* **Price / MTok:** Input / output, base price per million tokens. Batch API requests are 50% off; prompt caching reads cost 10% of the base input price (2.5% on Claude Fable 5.1 and Claude Mythos 5.1). See Pricing for the full list.
* **Latency:** Comparative latency, relative to the current lineup, as published in the models overview. Actual latency depends on prompt length, output length, and thinking effort.
* **Thinking:** Adaptive thinking lets the model decide how much to think, steered by effort. Extended thinking is the manual budget\_tokens mode on earlier models.
* **Default effort:** The effort parameter’s default on the Claude API. Models without a value don’t support the parameter.
* **Knowledge cutoff:** Reliable knowledge cutoff: the date through which the model’s knowledge is most extensive and reliable.


## Specifications

Source: https://platform.claude.com/llms-full.txt#specifications-4

### Model IDs

| Platform                                                                                                              | Model ID                                   |
| :-------------------------------------------------------------------------------------------------------------------- | :----------------------------------------- |
| Claude API                                                                                                            | `claude-haiku-4-5-20251001`                |
| Claude API alias                                                                                                      | `claude-haiku-4-5`                         |
| [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)                      | `anthropic.claude-haiku-4-5`               |
| [Amazon Bedrock (InvokeModel)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy) | `anthropic.claude-haiku-4-5-20251001-v1:0` |
| [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)                             | `claude-haiku-4-5@20251001`                |
| [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry)                | `claude-haiku-4-5`                         |
| [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)                | `claude-haiku-4-5`                         |

### Pricing

| Feature                                                                                | Value                                                               |
| :------------------------------------------------------------------------------------- | :------------------------------------------------------------------ |
| Input                                                                                  | $1 / MTok                                                           |
| Output                                                                                 | $5 / MTok                                                           |
| [5m cache write](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | $1.25 / MTok                                                        |
| [1h cache write](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | $2 / MTok                                                           |
| [Cache read](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)     | $0.10 / MTok                                                        |
| [Batch API](https://platform.claude.com/docs/en/build-with-claude/batch-processing)    | 50% discount on input and output                                    |
| Full price list                                                                        | [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) |

### Capabilities

| Feature                                                                                 | Value                  |
| :-------------------------------------------------------------------------------------- | :--------------------- |
| [Context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) | 200K tokens            |
| Max output                                                                              | 64K tokens             |
| [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)              | Extended               |
| [Default effort](https://platform.claude.com/docs/en/build-with-claude/effort)          | Not supported          |
| Comparative latency                                                                     | Fastest                |
| Input → output                                                                          | Text and images → text |
| Reliable knowledge cutoff                                                               | Feb 2025               |
| Training data cutoff                                                                    | Jul 2025               |

### Availability

| Feature                                                                       | Value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| :---------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Status](https://platform.claude.com/docs/en/about-claude/model-deprecations) | Active (latest)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Released                                                                      | October 15, 2025                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Retirement                                                                    | Not sooner than October 15, 2026                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Platforms                                                                     | Claude API, [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Amazon Bedrock (InvokeModel)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy), [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) |


## Good to know

Source: https://platform.claude.com/llms-full.txt#good-to-know-3

* `claude-haiku-4-5` is a convenience alias that resolves to the pinned snapshot `claude-haiku-4-5-20251001`. See [Model IDs and versioning](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions).
* Claude Haiku 4.5 uses manual extended thinking (`thinking.type: "enabled"`), not adaptive thinking.
* Query limits and capabilities programmatically with the [Models API](https://platform.claude.com/docs/en/api/models/list).


## Resources

Source: https://platform.claude.com/llms-full.txt#resources-4

<CardGroup cols={3}>
  <Card title="Extended thinking" icon="brain" href="https://platform.claude.com/docs/en/build-with-claude/extended-thinking">
    Claude Haiku 4.5 supports manual extended thinking with `budget_tokens`.
  </Card>

  <Card title="Choosing a model" icon="scales" href="https://platform.claude.com/docs/en/about-claude/models/choosing-a-model">
    When to start efficiency-first with Haiku and when to reach for a larger model.
  </Card>

  <Card title="Reduce latency" icon="gauge" href="https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency">
    Techniques that pair well with the fastest model in the lineup.
  </Card>
</CardGroup>
