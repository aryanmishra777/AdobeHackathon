# platform.claude.com Documentation (Part 4 of 35)

## Make changes without editing the prefix

Source: https://platform.claude.com/llms-full.txt#make-changes-without-editing-the-prefix

Each common prefix edit has a replacement that gives the model the same information and leaves earlier bytes unchanged, so later thinking stays valid. Find the edit your code makes today in the first column:

| Instead of                                                                              | Use                                                                                                                                                                                                                                                                                                            | Beta header                                             |
| --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Rebuilding the top-level `system` prompt                                                | A [mid-conversation system message](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#new-instructions)                                                                                                                                                                                 | None                                                    |
| Injecting a reminder and deleting it on the next request                                | A [turn-scoped system message](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#per-turn-reminders) (`clear_at: "next_user_message"`)                                                                                                                                                  | `mid-conversation-system-clear-at-2026-08-21`           |
| Adding or removing entries in `tools`                                                   | [`tool_addition` and `tool_removal` blocks](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#tool-changes)                                                                                                                                                                             | `mid-conversation-tool-changes-2026-07-01`              |
| Changing top-level `output_config.effort` (restarts the cache, doesn't affect thinking) | A [per-message `output_config`](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#effort-changes)                                                                                                                                                                                       | `mid-conversation-output-config-2026-07-01`             |
| Dropping or summarizing old turns on the client                                         | Server-side [compaction or context editing](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#server-side-trimming), or [client-side compaction](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#custom-compaction-on-the-client) that keeps no stale thinking | `compact-2026-01-12` or `context-management-2025-06-27` |
| An image or document URL whose bytes change between requests                            | A [`file_id` from the Files API](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#files-by-id), or base64                                                                                                                                                                              | None                                                    |

All of these assume you [send assistant turns back exactly as returned](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#append-assistant-turns-exactly-as-returned). To use several betas in one request, combine the values in one `anthropic-beta` header. The same names apply on Amazon Bedrock and Google Cloud (see [Beta headers](https://platform.claude.com/docs/en/api/beta-headers)):

```text wrap
anthropic-beta: thinking-binding-controls-2026-08-01,mid-conversation-system-clear-at-2026-08-21,mid-conversation-tool-changes-2026-07-01

json
{
  "role": "system",
  "content": "The user switched the workspace to read-only mode. Do not write files until told otherwise."
}

json
[
  { "role": "user", "content": "Fix the failing test." },
  {
    "role": "assistant",
    "content": [
      { "type": "thinking", "thinking": "", "signature": "..." },
      {
        "type": "tool_use",
        "id": "toolu_01",
        "name": "read_file",
        "input": { "path": "tests/test_auth.py" }
      }
    ]
  },
  {
    "role": "user",
    "content": [{ "type": "tool_result", "tool_use_id": "toolu_01", "content": "..." }]
  },
  {
    "role": "system",
    "clear_at": "next_user_message",
    "content": "Request every independent read in one turn."
  },
  {
    "role": "assistant",
    "content": [
      { "type": "thinking", "thinking": "", "signature": "..." },
      {
        "type": "tool_use",
        "id": "toolu_02",
        "name": "read_file",
        "input": { "path": "src/auth.py" }
      }
    ]
  },
  {
    "role": "user",
    "content": [{ "type": "tool_result", "tool_use_id": "toolu_02", "content": "..." }]
  },
  {
    "role": "system",
    "clear_at": "next_user_message",
    "content": "Request every independent read in one turn."
  }
]

json
{
  "role": "system",
  "content": [
    { "type": "tool_removal", "tool": { "type": "tool_reference", "name": "delete_branch" } },
    { "type": "text", "text": "Branch deletion is disabled for the rest of this session." }
  ]
}

json
{
  "role": "system",
  "content": [
    { "type": "tool_addition", "tool": { "type": "tool_reference", "name": "deploy" } },
    { "type": "text", "text": "Authentication succeeded. Deployment is now available." }
  ]
}

json
{ "role": "system", "content": [], "output_config": { "effort": "low" } }

json
[
  {
    "role": "user",
    "content": "<summary of the session so far>\n\n<the next instruction>"
  }
]

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: thinking-binding-controls-2026-08-01" \
    -d "{
      \"model\": \"claude-fable-5-1\",
      \"max_tokens\": 16000,
      \"thinking\": {
        \"type\": \"adaptive\",
        \"block_binding\": { \"prefix_mismatch_behavior\": \"drop_block\" }
      },
      \"messages\": $COMPACTED_MESSAGES
    }"

bash CLI
  ant beta:messages create --beta thinking-binding-controls-2026-08-01 <<YAML
  model: claude-fable-5-1
  max_tokens: 16000
  thinking:
    type: adaptive
    block_binding:
      prefix_mismatch_behavior: drop_block
  messages: $COMPACTED_MESSAGES
  YAML

python Python
  client = anthropic.Anthropic()

  # compacted_messages: the summary message, then the kept turns as returned
  response = client.beta.messages.create(
      model="claude-fable-5-1",
      max_tokens=16000,
      thinking={
          "type": "adaptive",
          "block_binding": {"prefix_mismatch_behavior": "drop_block"},
      },
      messages=compacted_messages,
      betas=["thinking-binding-controls-2026-08-01"],
  )

  print(response.input_transformations)

typescript TypeScript
  const client = new Anthropic();

  // compactedMessages: the summary message, then the kept turns as returned
  const response = await client.beta.messages.create({
    model: "claude-fable-5-1",
    max_tokens: 16000,
    thinking: {
      type: "adaptive",
      block_binding: { prefix_mismatch_behavior: "drop_block" }
    },
    messages: compactedMessages,
    betas: ["thinking-binding-controls-2026-08-01"]
  });

  console.log(response.input_transformations);

csharp C#
  AnthropicClient client = new();

  // compactedMessages: the summary message, then the kept turns as returned
  var response = await client.Beta.Messages.Create(
      new()
      {
          Model = "claude-fable-5-1",
          MaxTokens = 16000,
          Thinking = new BetaThinkingConfigAdaptive
          {
              BlockBinding = new()
              {
                  PrefixMismatchBehavior = BetaThinkingPrefixMismatchBehavior.DropBlock,
              },
          },
          Messages = compactedMessages,
          Betas = [AnthropicBeta.ThinkingBindingControls2026_08_01],
      }
  );

  Console.WriteLine(response.InputTransformations?.Count ?? 0);

go Go
  client := anthropic.NewClient()

  // compactedMessages: the summary message, then the kept turns as returned
  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     "claude-fable-5-1",
  	MaxTokens: 16000,
  	Thinking: anthropic.BetaThinkingConfigParamUnion{
  		OfAdaptive: &anthropic.BetaThinkingConfigAdaptiveParam{
  			BlockBinding: anthropic.BetaThinkingBlockBindingParam{
  				PrefixMismatchBehavior: anthropic.BetaThinkingPrefixMismatchBehaviorDropBlock,
  			},
  		},
  	},
  	Messages: compactedMessages,
  	Betas:    []anthropic.AnthropicBeta{anthropic.AnthropicBetaThinkingBindingControls2026_08_01},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(len(response.InputTransformations))

java Java
  import com.anthropic.models.beta.AnthropicBeta;
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.BetaThinkingBlockBinding;
  import com.anthropic.models.beta.messages.BetaThinkingConfigAdaptive;
  import com.anthropic.models.beta.messages.BetaThinkingPrefixMismatchBehavior;
  import com.anthropic.models.beta.messages.MessageCreateParams;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      // compactedMessages: the summary message, then the kept turns as returned
      MessageCreateParams params = MessageCreateParams.builder()
          .model("claude-fable-5-1")
          .maxTokens(16000L)
          .thinking(BetaThinkingConfigAdaptive.builder()
              .blockBinding(BetaThinkingBlockBinding.builder()
                  .prefixMismatchBehavior(BetaThinkingPrefixMismatchBehavior.DROP_BLOCK)
                  .build())
              .build())
          .messages(compactedMessages)
          .addBeta(AnthropicBeta.THINKING_BINDING_CONTROLS_2026_08_01)
          .build();

      BetaMessage response = client.beta().messages().create(params);

      IO.println(response.inputTransformations());
  }

php PHP
  use Anthropic\Beta\AnthropicBeta;
  use Anthropic\Beta\Messages\BetaThinkingBlockBinding;
  use Anthropic\Beta\Messages\BetaThinkingConfigAdaptive;
  use Anthropic\Beta\Messages\BetaThinkingPrefixMismatchBehavior;
  use Anthropic\Client;

  $client = new Client();

  // $compactedMessages: the summary message, then the kept turns as returned
  $response = $client->beta->messages->create(
      model: 'claude-fable-5-1',
      maxTokens: 16000,
      thinking: BetaThinkingConfigAdaptive::with(
          blockBinding: BetaThinkingBlockBinding::with(
              prefixMismatchBehavior: BetaThinkingPrefixMismatchBehavior::DROP_BLOCK,
          ),
      ),
      messages: $compactedMessages,
      betas: [AnthropicBeta::THINKING_BINDING_CONTROLS_2026_08_01],
  );

  var_dump($response->inputTransformations);

ruby Ruby
  client = Anthropic::Client.new

  # compacted_messages: the summary message, then the kept turns as returned
  response = client.beta.messages.create(
    model: "claude-fable-5-1",
    max_tokens: 16_000,
    thinking: {
      type: "adaptive",
      block_binding: {prefix_mismatch_behavior: "drop_block"}
    },
    messages: compacted_messages,
    betas: [Anthropic::AnthropicBeta::THINKING_BINDING_CONTROLS_2026_08_01]
  )

  puts response.input_transformations

json
{
  "input_transformations": [
    {
      "type": "thinking_dropped",
      "path": "messages.2.content.0",
      "reason": "prefix_binding_mismatch"
    },
    {
      "type": "thinking_dropped",
      "path": "messages.4.content.0",
      "reason": "prefix_binding_mismatch"
    }
  ]
}
```

Keep sending `"drop_block"` on later requests for as long as those two turns stay in the history. Thinking the model produces from this request onward follows the summary and stays valid. If you'd rather not depend on the beta header, the alternative is to strip the `thinking` and `redacted_thinking` blocks from the kept assistant turns yourself when you build the compacted history.

#### Patterns that don't work with preserved thinking

* **Background compaction.** Building the summary off the critical path and swapping it in a few requests later breaks the rule the same way keep-tail does, with a delay: every assistant turn produced while the summary was being built carries thinking that predates the swap, and it all fails the moment the summary lands. If you need it, treat the swap like keep-tail and send `"drop_block"` from the swap onward. Otherwise compact synchronously.
* **Cutting turns out of the middle.** Removing individual turns invalidates every thinking block after them, and no compaction scheme avoids that. If you were cutting a turn to change an instruction, append a [mid-conversation system message](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#new-instructions) instead. To remove old tool results or old thinking selectively, use server-side [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing).
* **Compacting in the middle of a tool round.** Don't compact between an assistant turn's `tool_use` and the `tool_result` that answers it. Send that assistant turn back with its thinking intact so the model finishes the round with its reasoning. See [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks).

### Reference files by ID, not by a URL whose content changes

For an `image` or `document` block with a `url` source, the check covers the fetched bytes, not the URL string. A URL whose content changes invalidates later thinking: a "latest screenshot" endpoint, or a document someone edits between turns. A rotating signed URL for the same file doesn't. For content you reference across turns, upload it once with the [Files API](https://platform.claude.com/docs/en/build-with-claude/files) and use the `file_id`, or send base64.


## FAQ

Source: https://platform.claude.com/llms-full.txt#faq-3

<AccordionGroup>
  <Accordion title="Do I need a new account to test preserved thinking?">
    No. Send the `thinking-binding-controls-2026-08-01` beta header and set `thinking.block_binding.prefix_mismatch_behavior`. Setting the field opts that request into enforcement regardless of account age. `"error"` rejects an edited history with the same 400 a new account gets, and `"drop_block"` lets the request through and lists what was dropped in `input_transformations`. See [Check whether your code edits the prefix](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#how-to-tell-whether-your-integration-is-impacted).
  </Accordion>

  <Accordion title="If anything before a thinking block changes, even one tool description, is the conversation unusable?">
    No. What fails is the thinking already in the history after the point you changed, and you choose what happens to it. With `prefix_mismatch_behavior: "drop_block"`, the API drops those blocks and the request succeeds: the model answers that turn without that reasoning, and the prompt cache restarts at the edit. With the default `"error"`, the API rejects the request with a 400 until you undo the edit or resend with `"drop_block"`. See [What the API does with an invalid block](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#mismatch-behavior). [What counts as an edit](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#what-counts-as-an-edit) lists which changes matter.
  </Accordion>

  <Accordion title="Does changing effort or other thinking settings between requests invalidate earlier thinking?">
    No. `output_config.effort`, `max_tokens`, and the `thinking` configuration aren't part of the checked prefix, which covers only `system`, `tools`, and `messages`. A top-level effort change invalidates most of the prompt cache. On Claude Fable 5.1, a [per-message effort](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#effort-changes) change keeps the prompt cache and is used as the new effort level until changed again.
  </Accordion>

  <Accordion title="My tool list changes mid-session. How do I avoid invalidating the conversation?">
    Don't edit `tools`. Declare the full set at session start, mark tools that aren't available yet with `defer_loading: true`, and offer or withdraw them with `tool_addition` and `tool_removal` blocks. If you learn a tool's schema only mid-session, such as from an MCP server discovered at runtime, you can still append it to `tools` with `defer_loading: true` and offer it the same way. That's safe because an unreferenced deferred tool isn't part of the prefix. The `role: "system"` messages that carry these blocks join the prefix for later thinking, so don't move, reword, or delete them afterward. See [Add or remove tools with `tool_addition` and `tool_removal`](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#tool-changes).
  </Accordion>

  <Accordion title="I compact by summarizing older turns and keeping recent turns verbatim. Does that still work?">
    Not if the kept turns still carry their thinking: those blocks were produced against the history you replaced, so they fail the check. Strip `thinking` and `redacted_thinking` blocks from the turns you carry across and keep their `text` and `tool_use` blocks, or send `prefix_mismatch_behavior: "drop_block"` and let the API drop them. Simple compaction leaves no thinking behind to fail and is the recommended approach: one summary message plus the next user turn, with no earlier turns replayed. Server-side [compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) and [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) don't count as edits. See [Compact on the client](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#custom-compaction-on-the-client).
  </Accordion>

  <Accordion title="How do I handle instruction files such as AGENTS.md or CLAUDE.md that change mid-session?">
    Load them once at session start and keep the top-level `system` prompt and `tools` fixed. When a file changes, append the new version at that point in `messages` instead of editing the original. Use a [mid-conversation system message](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages) for instructions that come from you as the operator. For file text you treat as untrusted, which shouldn't carry system-prompt authority, put the content in the next `user` turn instead. See [Add instructions with a mid-conversation system message](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#new-instructions) and [Limitations](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#limitations).
  </Accordion>

  <Accordion title="Can I resume a saved session later, after a restart or the next day?">
    Yes. A resumed session is an ordinary follow-up request: `system`, `tools`, and the earlier `messages` must match what you last sent byte-for-byte. Persist exactly what you sent and received, and replay that: the rendered system prompt, the tool definitions, and each assistant turn as returned. Don't re-render from inputs that might have changed since, such as the date, an updated instruction file, or a new tool version. Anything new goes in an appended message. See [Send assistant turns back exactly as returned](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#append-assistant-turns-exactly-as-returned).
  </Accordion>

  <Accordion title="My harness can route a turn to a non-Claude model. Do those turns invalidate Claude's earlier thinking?">
    No, provided they're appended after the existing history and nothing earlier changes: an assistant message without thinking blocks is an appended message like any other. Send the other model's output as `text` and `tool_use` content.
  </Accordion>

  <Accordion title="Can I carry a conversation's reasoning into a new conversation?">
    Not into a different conversation. A thinking block is usable only when it follows the exact `system`, `tools`, and `messages` it was produced from. A branch that replays that history unchanged up to the fork point keeps its thinking. A conversation that starts from anything else can't use it, so start that conversation from a summary of the task state, as in [simple compaction](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#custom-compaction-on-the-client): the goal, decisions made, files and results so far, and the next step.
  </Accordion>
</AccordionGroup>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-18

<CardGroup cols={2}>
  <Card title="Troubleshooting thinking" icon="hammer" href="https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting">
    Diagnose and fix the most common thinking failures: configuration 400 errors, empty or missing thinking blocks, max\_tokens stops, and cache misses.
  </Card>

  <Card title="Mid-conversation system messages and tool changes" icon="messages" href="https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages">
    Change system instructions or tool availability partway through a conversation without invalidating the cached prefix that came before them.
  </Card>

  <Card title="Compaction" icon="stack" href="https://platform.claude.com/docs/en/build-with-claude/compaction">
    Server-side context compaction for managing long conversations that approach context window limits.
  </Card>

  <Card title="Prompt caching" icon="database" href="https://platform.claude.com/docs/en/build-with-claude/prompt-caching">
    Cache prompt prefixes with `cache_control` to cut costs and latency, using automatic caching or explicit breakpoints with 5-minute or 1-hour TTLs.
  </Card>
</CardGroup>


---
title: Steering thinking
url: https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost
description: Steer how often and how deeply Claude thinks with effort levels, system prompt guidance, and per-message steering, and understand thinking's cost and pricing.
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

Claude's thinking is adaptive: the model evaluates each request and decides for itself whether to think and how much. You set an intent, optionally specify the effort, and the model allocates reasoning where it judges reasoning will help.

This makes thinking a strong fit for workloads that mix trivial and complex requests, and for long-horizon agentic workflows where the right amount of reasoning varies from step to step.

To learn how to turn thinking on, how to read thinking output, and about [thinking output on Claude Fable 5 and Claude Mythos 5](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-output-on-claude-fable-5-and-claude-mythos-5), see the [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) overview. This page covers how Claude decides when to think, how to steer that decision, and the caching, cost, and pricing mechanics that follow from it.


## How Claude decides when to think

Source: https://platform.claude.com/llms-full.txt#how-claude-decides-when-to-think

Thinking is optional for the model. On each request, Claude weighs the complexity of the input and decides whether deeper reasoning would improve the answer. A simple factual question may get a direct response with no thinking block at all; a multistep math problem or a tricky debugging task triggers deeper reasoning.

The decision happens per request. The same conversation can contain turns with and without thinking, and a turn where Claude chose not to think contains no thinking block. Don't build application logic that assumes every assistant turn starts with one.

The primary control over this decision is the [effort](https://platform.claude.com/docs/en/build-with-claude/effort) parameter, which acts as soft guidance for how willing Claude should be to think and how deeply; see [Effort levels](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#effort-levels) on this page for what each level does.

If you want Claude to think less often, lower the effort level before reaching for prompt-based steering.

Thinking also interleaves with tool use automatically: Claude can think between tool calls, reflecting on each tool result before deciding what to do next ([interleaved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#interleaved-thinking)). You don't need a beta header or any additional configuration for this.

For the full picture of how the thinking configuration and the effort parameter interact, see [Thinking and effort](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-effort).


## Steering how often Claude thinks

Source: https://platform.claude.com/llms-full.txt#steering-how-often-claude-thinks

Whether Claude thinks on a given turn is promptable. Effort sets the overall posture, but you can also shape the decision directly with natural-language guidance, either globally in the system prompt or per message from the user turn.

Use the two levers together in this order:

1. Set the effort level that matches your workload's default balance of quality and latency.
2. Add prompt guidance only if Claude's triggering still doesn't match your needs at that level.

For broader prompting guidance with thinking, see [leverage thinking and interleaved thinking capabilities](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#leverage-thinking-and-interleaved-thinking-capabilities).

### Effort levels

Effort is the primary steering lever for thinking. Each level sets a different default for how often Claude thinks and how deeply:

| Effort level     | Thinking behavior                                                                    |
| ---------------- | ------------------------------------------------------------------------------------ |
| `max`            | Claude always thinks with no constraints on thinking depth.                          |
| `xhigh`          | Claude always thinks deeply with extended exploration.                               |
| `high` (default) | Claude almost always thinks. Provides deep reasoning on complex tasks.               |
| `medium`         | Claude uses moderate thinking. May skip thinking for simple queries.                 |
| `low`            | Claude minimizes thinking. Skips thinking for simple tasks where speed matters most. |

This table describes how each level changes thinking behavior. For guidance on which level to choose for a given workload, including per-model recommendations, see [When to adjust the effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort#when-to-adjust-the-effort-parameter) on the effort page.

Effort is set at `output_config.effort`, not inside the `thinking` object; for full per-language examples, see [Effort](https://platform.claude.com/docs/en/build-with-claude/effort#basic-usage).

Level availability varies by model; the [effort availability table](https://platform.claude.com/docs/en/build-with-claude/effort#effort-levels) on the effort page is the authority for which levels each model supports.

### System prompt guidance

System prompt guidance shifts Claude's thinking threshold for every request in the conversation. If Claude is thinking more often than your workload needs, add guidance like this to your system prompt:

```text wrap
Extended thinking adds latency and should only be used when it
will meaningfully improve answer quality, typically for problems
that require multistep reasoning. When in doubt, respond directly.

text wrap
This task involves multistep reasoning. Think carefully before responding.
```

Steering effectiveness can be sensitive to exact wording. If one phrasing doesn't produce the behavior you want, try a more direct variant.

### Per-message steering

You can also steer thinking on a per-message basis from the user turn, independently of the system prompt. Appending `"Please think hard before responding."` to a user message encourages Claude to think on that turn; `"Answer directly without deliberating."` suppresses it.

Per-message steering is useful when only some requests in a conversation warrant extended reasoning. An agent harness, for example, can append the encouraging phrase on planning steps and the suppressing phrase on routine confirmations, without touching the system prompt or changing any request parameters between turns.

### Verify steering on your workload

Prompt-based steering changes model behavior, so treat it like any other prompt change: measure before you ship. Run a representative sample of your traffic with and without the guidance, and compare how often thinking triggers (the presence of thinking blocks in responses), output token usage, latency, and answer quality on the cases that matter to you.

<Warning>
  Steering Claude to think less often may reduce quality on tasks that benefit from reasoning. Lowering the [effort](https://platform.claude.com/docs/en/build-with-claude/effort) level is usually the better first lever, since it is a calibrated control rather than a wording-sensitive instruction. Measure the impact on your specific workloads before deploying prompt-based tuning to production.
</Warning>


## Mechanics

Source: https://platform.claude.com/llms-full.txt#mechanics

Three mechanics follow from Claude managing its own thinking: turn validation, prompt caching, and how you bound cost.

### Turn validation

Assistant turns don't need to start with a thinking block. (Models using a legacy manual thinking budget enforce that the final assistant turn of a thinking-enabled request begins with one; see [Turn structure in manual mode](https://platform.claude.com/docs/en/build-with-claude/extended-thinking#turn-structure-in-manual-mode).)

For multi-turn applications, this means you can pass back conversation history in whatever shape you have it:

* Assistant turns where Claude chose not to think are valid history as-is.
* You can resume a conversation that began without thinking, or that used a different thinking configuration, without rewriting its history.
* History assembled from mixed sources doesn't need thinking blocks reinserted at the start of each assistant turn to pass validation.

The relaxation is about validation, not about what you should send. When you have thinking blocks, pass them back unmodified, particularly during tool use, where they carry the reasoning behind Claude's tool calls. See the [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) overview for the full rules.

### Prompt caching

Consecutive requests that keep the same thinking configuration and effort level preserve prompt caching; see [Thinking and prompt caching](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-prompt-caching) for the full rules. The resolved effort value is rendered into the prompt, so changing it between requests invalidates cache breakpoints, just as changing the legacy [`budget_tokens`](https://platform.claude.com/docs/en/build-with-claude/extended-thinking#extended-thinking-with-prompt-caching) parameter does on models that use it. Setting `effort` explicitly to the model's default is equivalent to omitting it and does not break the cache.

The practical consequence: pick a thinking configuration and an effort level per conversation and keep them. If some turns need more or less thinking, steer with [per-message prompting](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#tuning-thinking-behavior): guidance appended to the newest user message leaves earlier cache breakpoints intact, where a configuration or effort change does not.

The following example demonstrates the invalidation with a multi-turn script you can run yourself:

<Accordion title="Effort changes invalidate the prompt cache">
  <Tabs>
    <Tab title="cURL">
      <Note>
        This workflow doesn't translate well to a one-off shell command. See the SDK tabs for the multi-turn pattern; per-turn HTTP requests follow the examples on the [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) page.
      </Note>
    </Tab>

    <Tab title="CLI">
      <Note>
        This workflow doesn't translate well to a one-off shell command. See the SDK tabs for the multi-turn pattern; per-turn CLI invocations follow the examples on the [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) page.
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

  Here is the output of the script (you may see slightly different numbers):

  ```text Output wrap
  First request - establishing cache
  First response usage: { cache_creation_input_tokens: 3546, cache_read_input_tokens: 0, input_tokens: 15, output_tokens: 1033 }

  Second request - same configuration (cache hit expected)
  Second response usage: { cache_creation_input_tokens: 0, cache_read_input_tokens: 3546, input_tokens: 1062, output_tokens: 1630 }

  Third request - different effort level (cache miss expected)
  Third response usage: { cache_creation_input_tokens: 3546, cache_read_input_tokens: 0, input_tokens: 2706, output_tokens: 1468 }
  ```

  With the cache breakpoint in the messages array, changing effort from the default `high` to `medium` invalidates it: the third request shows `cache_creation_input_tokens=3546` and `cache_read_input_tokens=0` where the second showed a full cache read.
</Accordion>

### Cost control

You don't set a thinking token budget. Two controls bound cost:

* `max_tokens` is a hard cap on total output for the request, thinking and response text combined. Claude never generates past it. In a tool-use loop, each request in the turn has its own `max_tokens`, so it doesn't bound the whole turn's spend.
* `effort` is soft guidance on how much of that output Claude allocates to thinking. It shapes behavior but doesn't guarantee a token count.

Because thinking counts toward `max_tokens`, set it high enough to leave room for both the reasoning and the answer. A `max_tokens` sized for a response with no thinking is often too small once Claude starts thinking on hard requests.

At `high` effort and above, Claude may think extensively and is more likely to exhaust the budget. If you see [`stop_reason: "max_tokens"`](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#stopped-at-max-tokens) in responses, you have two remedies:

* Raise `max_tokens` to give the model more room for thinking plus the answer.
* Lower the effort level so Claude thinks less and leaves more of the budget for response text.

Which one is right depends on whether the truncated responses needed the reasoning. If quality on those requests matters, raise the cap; if they were over-thought, lower the effort.


## Pricing

Source: https://platform.claude.com/llms-full.txt#pricing-4

Thinking incurs charges for:

* Tokens Claude uses while thinking (billed as output tokens)
* Thinking blocks from prior assistant turns that remain in context, per the [preservation default](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-block-preservation-by-model): all turns by default on keep-all models, only the last turn elsewhere (billed as input tokens)
* Standard text output tokens

<Note>
  When thinking is active, a specialized system prompt is automatically included to support this feature.
</Note>

What you're billed for is the same regardless of the `display` setting; only what you see changes:

|                             | `display: "summarized"`                              | `display: "omitted"`                                 |
| --------------------------- | ---------------------------------------------------- | ---------------------------------------------------- |
| **Input tokens**            | Tokens in your original request                      | Same as summarized                                   |
| **Output tokens (billed)**  | The full thinking tokens Claude generated internally | Same as summarized                                   |
| **Output tokens (visible)** | The summarized thinking text                         | Zero thinking tokens (the `thinking` field is empty) |
| **Summary generation**      | No charge                                            | Not applicable                                       |

<Warning>
  The billed output token count does **not** match the visible token count in the response. You are billed for the full thinking process, not the thinking content visible in the response.
</Warning>

To see how many billed output tokens were spent on internal reasoning, read `usage.output_tokens_details.thinking_tokens` in the response. This value reflects the raw reasoning the model generated (not the summarized text returned in the body) and is always less than or equal to `output_tokens`. Subtract it from `output_tokens` to approximate the non-reasoning portion of the output. When streaming, this breakdown appears only on the final `message_delta` event.

`output_tokens` remains the inclusive, authoritative total used for billing. `output_tokens_details` is a read-only breakdown for observability. For complete pricing information including base rates, cache writes, cache hits, and output tokens, see [Pricing](https://platform.claude.com/docs/en/about-claude/pricing).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-19

<CardGroup cols={3}>
  <Card title="Thinking" icon="brain" href="https://platform.claude.com/docs/en/build-with-claude/thinking">
    Turn thinking on, read thinking output, and check per-model support.
  </Card>

  <Card title="Thinking in tool and multi-turn workflows" icon="wrench" href="https://platform.claude.com/docs/en/build-with-claude/thinking-tool-workflows">
    Preserve thinking blocks across tool calls and manage thinking in multi-turn conversations.
  </Card>

  <Card title="Effort" icon="sliders" href="https://platform.claude.com/docs/en/build-with-claude/effort">
    Control how much thinking and output Claude allocates per request.
  </Card>
</CardGroup>


---
title: Thinking
url: https://platform.claude.com/docs/en/build-with-claude/thinking
description: "Understand how Claude's thinking works: turn it on, read thinking output, steer thinking depth with effort, and use thinking with tools, caching, and streaming."
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

A model that answers in a single pass has to get everything right on the first try: no scratch work, no checking, no changing course halfway through. For a proof, a tricky bug, or a long agentic task, the first approach is often not the best one.

Thinking removes that constraint. When thinking is active, Claude works through the problem in its own words before answering: it restates what is being asked, tries approaches, checks intermediate results, and abandons paths that do not hold up. That reasoning arrives in `thinking` content blocks ahead of the response, and Claude draws on it to produce the final answer. This is why thinking improves performance on complex tasks like math, coding, analysis, and long-running agentic work, where the quality of the answer depends on intermediate work that would otherwise be compressed into the response itself or skipped.

Thinking has a cost: the tokens Claude spends reasoning are billed as output tokens, even when the thinking text isn't returned to you, and they count toward `max_tokens` alongside the response text. This page covers how thinking behaves across the API surface: turning it on, reading its output, and managing its interactions with tools, streaming, caching, and the context window.


## How thinking works

Source: https://platform.claude.com/llms-full.txt#how-thinking-works

![Diagram of how thinking works: Claude evaluates the request and decides whether to think; with tool use, thinking can recur between tool calls; one response returns thinking blocks, then text blocks](https://platform.claude.com/docs/images/how-thinking-works.svg)

Whether Claude thinks on a given request, and how deeply, depends on your thinking configuration and the complexity of the request.

Here is what thinking looks like in a response: one or more `thinking` content blocks arrive before the `text` blocks. The thinking block is still generated content, like the `text` block that follows it, but it is separated from the canonical response. Each thinking block also carries a `signature` field, an encrypted copy of the full reasoning that you pass back unchanged in multi-turn and tool-use conversations (see [Thinking encryption](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-encryption)):

You don't always see this text, and what you see is never the raw chain of thought: the text in a thinking block is a [summary of Claude's reasoning](https://platform.claude.com/docs/en/build-with-claude/thinking#summarized-thinking). The `display` field on the thinking configuration controls whether that summary is returned at all: `"summarized"` returns it, while `"omitted"`, the default on many models, returns thinking blocks with an empty `thinking` field. Either way the block is billed the same and passed back the same in multi-turn conversations. See [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display) for per-model defaults and details.

If Claude uses tools, thinking can also appear between tool calls. See [Thinking with tool use](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-with-tool-use). For the full response format, see the [Messages API reference](https://platform.claude.com/docs/en/api/messages/create).


## Configuring thinking

Source: https://platform.claude.com/llms-full.txt#configuring-thinking

On most models, thinking is on by default or one parameter away. Which configuration each model accepts, and what it defaults to, is listed in the [per-model configuration table](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#supported-models) on the Troubleshooting page.

On Claude Opus 5, Claude Sonnet 5, Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, and Claude Mythos Preview, thinking is already on and needs no configuration. `display` defaults to `"omitted"` on these models, so the thinking text is hidden until you opt in. Opt in with `thinking: {"type": "adaptive", "display": "summarized"}`, which is exactly the following request with the [model string](https://platform.claude.com/docs/en/models/overview) swapped.

On Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, and Claude Sonnet 4.6, thinking is off until you set `thinking: {type: "adaptive"}`, which lets Claude decide when and how deeply to think based on the request. The following examples do that, set `display: "summarized"` so the thinking text is visible, and use a roomy `max_tokens`:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-4-8",
      "max_tokens": 16000,
      "thinking": {
        "type": "adaptive",
        "display": "summarized"
      },
      "messages": [
        {
          "role": "user",
          "content": "What is the greatest common divisor of 1071 and 462?"
        }
      ]
    }'

bash CLI
  ant messages create \
    --model claude-opus-4-8 \
    --max-tokens 16000 \
    --thinking '{type: adaptive, display: summarized}' \
    --message '{role: user, content: "What is the greatest common divisor of 1071 and 462?"}' \
    --transform content \
    --format yaml

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-4-8",
      max_tokens=16000,
      thinking={"type": "adaptive", "display": "summarized"},
      messages=[
          {
              "role": "user",
              "content": "What is the greatest common divisor of 1071 and 462?",
          }
      ],
  )

  for block in response.content:
      if block.type == "thinking":
          print(f"\nThinking: {block.thinking}")
      elif block.type == "text":
          print(f"\nResponse: {block.text}")

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-4-8",
    max_tokens: 16000,
    thinking: {
      type: "adaptive",
      display: "summarized"
    },
    messages: [
      {
        role: "user",
        content: "What is the greatest common divisor of 1071 and 462?"
      }
    ]
  });

  for (const block of response.content) {
    if (block.type === "thinking") {
      console.log(`\nThinking: ${block.thinking}`);
    } else if (block.type === "text") {
      console.log(`\nResponse: ${block.text}`);
    }
  }

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus4_8,
      MaxTokens = 16000,
      Thinking = new ThinkingConfigAdaptive { Display = Display.Summarized },
      Messages = [
          new() {
              Role = Role.User,
              Content = "What is the greatest common divisor of 1071 and 462?"
          }
      ]
  };

  var message = await client.Messages.Create(parameters);

  foreach (var block in message.Content)
  {
      if (block.TryPickThinking(out ThinkingBlock? thinking))
      {
          Console.WriteLine($"\nThinking: {thinking.Thinking}");
      }
      else if (block.TryPickText(out TextBlock? text))
      {
          Console.WriteLine($"\nResponse: {text.Text}");
      }
  }

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus4_8,
  	MaxTokens: 16000,
  	Thinking: anthropic.ThinkingConfigParamUnion{
  		OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{
  			Display: anthropic.ThinkingConfigAdaptiveDisplaySummarized,
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What is the greatest common divisor of 1071 and 462?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  for _, block := range response.Content {
  	switch v := block.AsAny().(type) {
  	case anthropic.ThinkingBlock:
  		fmt.Printf("\nThinking: %s", v.Thinking)
  	case anthropic.TextBlock:
  		fmt.Printf("\nResponse: %s", v.Text)
  	}
  }

java Java
  import com.anthropic.models.messages.ThinkingConfigAdaptive;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_4_8)
          .maxTokens(16000L)
          .thinking(ThinkingConfigAdaptive.builder()
              .display(ThinkingConfigAdaptive.Display.SUMMARIZED)
              .build())
          .addUserMessage("What is the greatest common divisor of 1071 and 462?")
          .build();

      Message response = client.messages().create(params);

      response.content().forEach(block -> {
          block.thinking().ifPresent(thinkingBlock ->
              IO.println("\nThinking: " + thinkingBlock.thinking())
          );
          block.text().ifPresent(textBlock ->
              IO.println("\nResponse: " + textBlock.text())
          );
      });
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 16000,
      messages: [
          [
              'role' => 'user',
              'content' => 'What is the greatest common divisor of 1071 and 462?'
          ]
      ],
      model: 'claude-opus-4-8',
      thinking: ['type' => 'adaptive', 'display' => 'summarized'],
  );

  foreach ($message->content as $block) {
      if ($block->type === 'thinking') {
          echo "\nThinking: " . $block->thinking;
      } elseif ($block->type === 'text') {
          echo "\nResponse: " . $block->text;
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-4-8",
    max_tokens: 16000,
    thinking: {
      type: "adaptive",
      display: "summarized"
    },
    messages: [
      {
        role: "user",
        content: "What is the greatest common divisor of 1071 and 462?"
      }
    ]
  )

  message.content.each do |block|
    case block.type
    when :thinking
      puts "\nThinking: #{block.thinking}"
    when :text
      puts "\nResponse: #{block.text}"
    end
  end

text Output wrap
Thinking: Use Euclidean algorithm.
1071 = 2*462 + 147
462 = 3*147 + 21
147 = 7*21 + 0
GCD = 21

Response: ## Finding GCD of 1071 and 462

I'll use the **Euclidean algorithm**, repeatedly dividing and taking remainders...

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-sonnet-5",
      "max_tokens": 4096,
      "thinking": {"type": "disabled"},
      "messages": [
        {
          "role": "user",
          "content": "Summarize this article in one sentence."
        }
      ]
    }'

bash CLI
  ant messages create \
    --model claude-sonnet-5 \
    --max-tokens 4096 \
    --thinking '{type: disabled}' \
    --message '{role: user, content: "Summarize this article in one sentence."}'

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-sonnet-5",
      max_tokens=4096,
      thinking={"type": "disabled"},
      messages=[{"role": "user", "content": "Summarize this article in one sentence."}],
  )

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-sonnet-5",
    max_tokens: 4096,
    thinking: { type: "disabled" },
    messages: [{ role: "user", content: "Summarize this article in one sentence." }]
  });

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeSonnet5,
      MaxTokens = 4096,
      Thinking = new ThinkingConfigDisabled(),
      Messages = [
          new() {
              Role = Role.User,
              Content = "Summarize this article in one sentence."
          }
      ]
  };

  var message = await client.Messages.Create(parameters);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeSonnet5,
  	MaxTokens: 4096,
  	Thinking: anthropic.ThinkingConfigParamUnion{
  		OfDisabled: &anthropic.ThinkingConfigDisabledParam{},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Summarize this article in one sentence.")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

java Java
  import com.anthropic.models.messages.ThinkingConfigDisabled;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_SONNET_5)
          .maxTokens(4096L)
          .thinking(ThinkingConfigDisabled.builder().build())
          .addUserMessage("Summarize this article in one sentence.")
          .build();

      Message response = client.messages().create(params);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          [
              'role' => 'user',
              'content' => 'Summarize this article in one sentence.'
          ]
      ],
      model: 'claude-sonnet-5',
      thinking: ['type' => 'disabled'],
  );

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-sonnet-5",
    max_tokens: 4096,
    thinking: { type: "disabled" },
    messages: [
      {
        role: "user",
        content: "Summarize this article in one sentence."
      }
    ]
  )
  ```
</CodeGroup>

Claude Opus 5 also has thinking on by default and accepts `thinking: {type: "disabled"}` at [effort](https://platform.claude.com/docs/en/build-with-claude/effort) `high` or below. At `xhigh` or `max` effort, thinking cannot be turned off: requests that combine `thinking: {type: "disabled"}` with those effort levels return a 400 error. This restriction applies to Claude Opus 5 and later models and is enforced on each request. With thinking disabled, Claude Opus 5 can occasionally emit tool calls as plain text or include internal XML tags in its visible output. See [Running with thinking disabled](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#running-with-thinking-disabled) for prompting mitigations.

Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, and Claude Mythos Preview reject `thinking: {type: "disabled"}`. Thinking can't be turned off on these models.

If your model supports only extended thinking (see the [per-model configuration table](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#supported-models)), configure it with `type: "enabled"` and a `budget_tokens` value instead. The [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) page covers that configuration. And if any thinking configuration comes back with a 400 error, [Troubleshooting thinking](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting) matches each error message to its fix.


## Reading thinking output

Source: https://platform.claude.com/llms-full.txt#reading-thinking-output

### Controlling thinking display

The `display` field on the thinking configuration controls how thinking content is returned in API responses. `display` works in both modes: set it alongside `type: "adaptive"` or `type: "enabled"`. It accepts these values:

* `"summarized"`: thinking blocks contain [summarized thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#summarized-thinking) text, a readable summary of Claude's reasoning. This is the default on Claude Opus 4.6, Claude Sonnet 4.6, and earlier models.
* `"omitted"`: thinking blocks are returned with an empty `thinking` field. The `signature` field still carries the encrypted full thinking for multi-turn continuity (see [Thinking encryption](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-encryption)). This is the default on Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, Claude Opus 5, Claude Sonnet 5, Claude Opus 4.8, Claude Opus 4.7, and [Claude Mythos Preview](https://anthropic.com/glasswing).
* `"updates"` (beta): reasoning blocks are returned with an empty `thinking` field, as with `"omitted"`, and the short [progress updates](https://platform.claude.com/docs/en/build-with-claude/thinking#progress-updates) some models write between tool calls come back as readable text. Requires the beta header `thinking-display-updates-2026-08-18`.

Set `display: "omitted"` when your application doesn't surface thinking content to users. The primary benefit is faster time-to-first-text-token when streaming: the server skips streaming thinking tokens entirely and delivers only the signature, so the final text response begins streaming sooner.

With `display: "omitted"`, the response contains `thinking` blocks with an empty `thinking` field:

```json Output
{
  "content": [
    {
      "type": "thinking",
      "thinking": "",
      "signature": "EosnCkYICxIMMb3LzNrMu..."
    },
    {
      "type": "text",
      "text": "The answer is 12,231."
    }
  ]
}

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-4-8",
      "max_tokens": 16000,
      "stream": true,
      "thinking": {
        "type": "adaptive",
        "display": "summarized"
      },
      "messages": [
        {
          "role": "user",
          "content": "What is the greatest common divisor of 1071 and 462?"
        }
      ]
    }'

bash CLI
  ant messages create \
    --model claude-opus-4-8 \
    --max-tokens 16000 \
    --thinking '{type: adaptive, display: summarized}' \
    --message '{role: user, content: "What is the greatest common divisor of 1071 and 462?"}' \
    --stream \
    --format jsonl

python Python
  client = anthropic.Anthropic()

  with client.messages.stream(
      model="claude-opus-4-8",
      max_tokens=16000,
      thinking={"type": "adaptive", "display": "summarized"},
      messages=[
          {
              "role": "user",
              "content": "What is the greatest common divisor of 1071 and 462?",
          }
      ],
  ) as stream:
      for event in stream:
          if event.type == "content_block_start":
              print(f"\nStarting {event.content_block.type} block...")
          elif event.type == "content_block_delta":
              if event.delta.type == "thinking_delta":
                  print(event.delta.thinking, end="", flush=True)
              elif event.delta.type == "text_delta":
                  print(event.delta.text, end="", flush=True)

typescript TypeScript
  const client = new Anthropic();

  const stream = client.messages.stream({
    model: "claude-opus-4-8",
    max_tokens: 16000,
    thinking: { type: "adaptive", display: "summarized" },
    messages: [{ role: "user", content: "What is the greatest common divisor of 1071 and 462?" }]
  });

  for await (const event of stream) {
    if (event.type === "content_block_start") {
      console.log(`\nStarting ${event.content_block.type} block...`);
    } else if (event.type === "content_block_delta") {
      if (event.delta.type === "thinking_delta") {
        process.stdout.write(event.delta.thinking);
      } else if (event.delta.type === "text_delta") {
        process.stdout.write(event.delta.text);
      }
    }
  }

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus4_8,
      MaxTokens = 16000,
      Thinking = new ThinkingConfigAdaptive { Display = Display.Summarized },
      Messages = [new() { Role = Role.User, Content = "What is the greatest common divisor of 1071 and 462?" }]
  };

  await foreach (var rawEvent in client.Messages.CreateStreaming(parameters))
  {
      if (rawEvent.TryPickContentBlockStart(out var start))
      {
          Console.WriteLine($"\nStarting {start.ContentBlock.Type} block...");
      }
      else if (rawEvent.TryPickContentBlockDelta(out var delta))
      {
          if (delta.Delta.TryPickThinking(out var thinkingDelta))
          {
              Console.Write(thinkingDelta.Thinking);
          }
          else if (delta.Delta.TryPickText(out var textDelta))
          {
              Console.Write(textDelta.Text);
          }
      }
  }

go Go
  client := anthropic.NewClient()

  stream := client.Messages.NewStreaming(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus4_8,
  	MaxTokens: 16000,
  	Thinking: anthropic.ThinkingConfigParamUnion{
  		OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{
  			Display: anthropic.ThinkingConfigAdaptiveDisplaySummarized,
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What is the greatest common divisor of 1071 and 462?")),
  	},
  })

  for stream.Next() {
  	event := stream.Current()
  	switch eventVariant := event.AsAny().(type) {
  	case anthropic.ContentBlockStartEvent:
  		fmt.Printf("\nStarting %s block...\n", eventVariant.ContentBlock.Type)
  	case anthropic.ContentBlockDeltaEvent:
  		switch deltaVariant := eventVariant.Delta.AsAny().(type) {
  		case anthropic.ThinkingDelta:
  			fmt.Print(deltaVariant.Thinking)
  		case anthropic.TextDelta:
  			fmt.Print(deltaVariant.Text)
  		}
  	}
  }
  if err := stream.Err(); err != nil {
  	log.Fatal(err)
  }

java Java
  import com.anthropic.models.messages.ThinkingConfigAdaptive;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_4_8)
          .maxTokens(16000L)
          .thinking(ThinkingConfigAdaptive.builder()
              .display(ThinkingConfigAdaptive.Display.SUMMARIZED)
              .build())
          .addUserMessage("What is the greatest common divisor of 1071 and 462?")
          .build();

      try (var streamResponse = client.messages().createStreaming(params)) {
          streamResponse.stream().forEach(event -> {
              if (event.contentBlockStart().isPresent()) {
                  var startEvent = event.contentBlockStart().get();
                  var block = startEvent.contentBlock();
                  if (block.isThinking()) {
                      IO.println("\nStarting thinking block...");
                  } else if (block.isText()) {
                      IO.println("\nStarting text block...");
                  }
              } else if (event.contentBlockDelta().isPresent()) {
                  var deltaEvent = event.contentBlockDelta().get();
                  deltaEvent.delta().thinking().ifPresent(td ->
                      IO.print(td.thinking())
                  );
                  deltaEvent.delta().text().ifPresent(td ->
                      IO.print(td.text())
                  );
              }
          });
      }
  }

php PHP
  $client = new Client();

  $stream = $client->messages->createStream(
      maxTokens: 16000,
      messages: [
          ['role' => 'user', 'content' => 'What is the greatest common divisor of 1071 and 462?']
      ],
      model: 'claude-opus-4-8',
      thinking: ['type' => 'adaptive', 'display' => 'summarized'],
  );

  foreach ($stream as $event) {
      if ($event->type === 'content_block_start') {
          echo "\nStarting {$event->contentBlock->type} block...\n";
      } elseif ($event->type === 'content_block_delta') {
          if ($event->delta->type === 'thinking_delta') {
              echo $event->delta->thinking;
          } elseif ($event->delta->type === 'text_delta') {
              echo $event->delta->text;
          }
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  stream = client.messages.stream(
    model: "claude-opus-4-8",
    max_tokens: 16000,
    thinking: { type: "adaptive", display: "summarized" },
    messages: [
      { role: "user", content: "What is the greatest common divisor of 1071 and 462?" }
    ]
  )

  stream.each do |event|
    case event
    when Anthropic::Streaming::ThinkingEvent
      print event.thinking
    when Anthropic::Streaming::TextEvent
      print event.text
    end
  end

sse Output
  event: message_start
  data: {"type": "message_start", "message": {"id": "msg_01...", "type": "message", "role": "assistant", "content": [], "model": "claude-opus-4-8", "stop_reason": null, "stop_sequence": null}}

  event: content_block_start
  data: {"type": "content_block_start", "index": 0, "content_block": {"type": "thinking", "thinking": "", "signature": ""}}

  event: content_block_delta
  data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "I need to find the GCD of 1071 and 462 using the Euclidean algorithm.\n\n1071 = 2 × 462 + 147"}}

  event: content_block_delta
  data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "\n462 = 3 × 147 + 21\n147 = 7 × 21 + 0\n\nSo GCD(1071, 462) = 21"}}

  // Additional thinking deltas...

  event: content_block_delta
  data: {"type": "content_block_delta", "index": 0, "delta": {"type": "signature_delta", "signature": "EqQBCgIYAhIM1gbcDa9GJwZA2b..."}}

  event: content_block_stop
  data: {"type": "content_block_stop", "index": 0}

  event: content_block_start
  data: {"type": "content_block_start", "index": 1, "content_block": {"type": "text", "text": ""}}

  event: content_block_delta
  data: {"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": "The greatest common divisor of 1071 and 462 is **21**."}}

  // Additional text deltas...

  event: content_block_stop
  data: {"type": "content_block_stop", "index": 1}

  event: message_delta
  data: {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": null}}

  event: message_stop
  data: {"type": "message_stop"}

sse Output
event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"thinking","thinking":"","signature":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"signature_delta","signature":"EosnCkYICxIMMb3LzNrMu..."}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}

event: content_block_start
data: {"type":"content_block_start","index":1,"content_block":{"type":"text","text":""}}

sse Output
event: content_block_start
data: {"type":"content_block_start","index":1,"content_block":{"type":"thinking","thinking":"","signature":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"thinking_delta","thinking":"Confirmed the retry path never refreshes the expired token. Editing auth.py to add the refresh call."}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,"delta":{"type":"signature_delta","signature":"Es8CCkYICxIM..."}}

event: content_block_stop
data: {"type":"content_block_stop","index":1}

event: content_block_start
data: {"type":"content_block_start","index":2,"content_block":{"type":"tool_use","id":"toolu_01D7FLrfh4GYq7yT1ULFeyMV","name":"edit_file","input":{}}}
```

Under `"updates"`, treat a block as a progress update as soon as one of its `thinking_delta` events carries non-empty text.

<Note>
  When using streaming with thinking enabled, you might notice that text sometimes arrives in larger chunks alternating with smaller, token-by-token delivery. This is expected behavior, especially for thinking content.

  The streaming system processes content in batches, which can delay and group streaming events into this "chunky" delivery pattern.
</Note>

For general streaming mechanics, see [Streaming Messages](https://platform.claude.com/docs/en/build-with-claude/streaming).


## Thinking and effort

Source: https://platform.claude.com/llms-full.txt#thinking-and-effort

The `thinking` parameter controls whether Claude thinks in [thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking) before answering; the `effort` parameter controls how much work Claude puts into the whole response, which in adaptive mode includes how often and how deeply it thinks. Don't pass `adaptive` as an `effort` value: `adaptive` is a thinking mode, not an effort level.

To learn what each effort level does to thinking behavior, see the [per-level thinking behavior table](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#effort-levels) on the [Steering thinking](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost) page. The [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) page documents the parameter itself, including which levels each model supports. On Claude Opus 4.5, the only extended-thinking-only model that supports effort, effort composes with `budget_tokens`. See [Budget rules and tuning](https://platform.claude.com/docs/en/build-with-claude/extended-thinking#budget-rules-and-tuning).

With the two controls separated this way, pick the one that matches your goal:

* **Lower cost or latency on a thinking-enabled workload:** lower `effort` first. It scales the whole response down, thinking included.
* **Claude is thinking too rarely or too shallowly:** raise `effort`, or see [Steering how often Claude thinks](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#tuning-thinking-behavior) on the steering page.
* **You need thinking fully off:** use `thinking: {type: "disabled"}` on models that allow it (see the [per-model configuration table](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#supported-models)).
* **You need a hard ceiling on spend:** use `max_tokens`. Effort is soft guidance. `max_tokens` is a strict limit.


## Thinking with tool use

Source: https://platform.claude.com/llms-full.txt#thinking-with-tool-use

Thinking works alongside [tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview), letting Claude reason through tool selection and process tool results. Two constraints apply:

1. **Tool choice limitation (manual mode):** tool use with manual extended thinking (`thinking: {type: "enabled"}`) only supports `tool_choice: {"type": "auto"}` (the default) or `tool_choice: {"type": "none"}`. Using `tool_choice: {"type": "any"}` or `tool_choice: {"type": "tool", "name": "..."}` results in an error because these options force tool use, which is incompatible with manual extended thinking. Adaptive thinking, including on models where thinking is on by default, supports forced tool use, except on Claude Fable 5.1 and Claude Mythos 5.1 (see [Response prefill and forced tool use](https://platform.claude.com/docs/en/build-with-claude/thinking#limits-and-feature-compatibility)).
2. **Preserving thinking blocks:** when you return tool results, you must pass the thinking blocks from the assistant message back to the API, complete and unmodified. See [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks).

**A tool-use loop is one assistant turn.** From the model's perspective, an assistant turn doesn't complete until Claude finishes its full response, which may include multiple tool calls and results. This whole sequence is a single assistant turn:

```text wrap
User: "What's the weather in Paris?"
Assistant: [thinking] + [tool_use: get_weather]
User: [tool_result: "20°C, sunny"]
Assistant: [text: "The weather in Paris is 20°C and sunny"]

text wrap
User: "What's the weather?"
Assistant: [tool_use] (thinking disabled)
User: [tool_result]
Assistant: [text: "It's sunny"]
User: "What about tomorrow?"
Assistant: [thinking] + [text: "..."] (thinking enabled - new turn)

json
{
  "model": "claude-fable-5-1",
  "max_tokens": 16000,
  "thinking": { "type": "adaptive", "display": "updates" },
  "tools": [
    {
      "name": "edit_file",
      "description": "Replace the contents of a file in the repository.",
      "input_schema": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "content": { "type": "string" }
        },
        "required": ["path", "content"]
      }
    }
  ],
  "messages": [
    {
      "role": "user",
      "content": "The login test fails after an hour of uptime. Find out why and fix it."
    }
  ]
}

json Output
{
  "content": [
    {
      "type": "thinking",
      "thinking": "",
      "signature": "EqMBCkYICxIM..."
    },
    {
      "type": "thinking",
      "thinking": "Confirmed the retry path never refreshes the expired token. Editing auth.py to add the refresh call.",
      "signature": "Es8CCkYICxIM..."
    },
    {
      "type": "tool_use",
      "id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
      "name": "edit_file",
      "input": { "path": "auth.py", "content": "..." }
    }
  ]
}
```

Keep the following in mind when working with progress updates:

* Pass progress-update blocks back unchanged with the rest of the assistant turn, like any other `thinking` block.
* The text you receive is a summary of the progress update, normally a sentence or two. Don't rely on its length. The progress update counts toward `usage.output_tokens` at its full length, not the summary's.
* A progress-update block can come back with an empty `thinking` field under any `display` value. Render nothing for an empty block. Under `"updates"` it looks the same as an empty reasoning block and needs no separate handling.
* When a response stops on `max_tokens`, `model_context_window_exceeded`, or `stop_sequence` soon after a tool call or tool result, its last block can be a progress-update block standing in for the work the model hadn't finished. Under `"updates"` and `"summarized"` its text is exactly `This part of the response was interrupted before it finished.` and you can show it like any other update. Under `"omitted"` it's empty. To continue, pass the assistant turn back unchanged and append a new `user` message (with a `tool_result` for each `tool_use` block in that turn).
* When [streaming](https://platform.claude.com/docs/en/build-with-claude/thinking#streaming-thinking), expect a pause of several seconds before a progress-update block opens. See the `"updates"` trace in [Streaming thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#streaming-thinking).
* These models write fewer progress updates at higher [effort](https://platform.claude.com/docs/en/build-with-claude/effort) and in long tool chains. If your interface depends on them, see [Ask for user-facing progress updates](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#ask-for-user-facing-progress-updates).

### Thinking block preservation by model

Whether thinking blocks from previous assistant turns stay in context by default depends on the model:

* **Keep all prior turns:** Claude Opus 4.5 and later Opus models, Claude Sonnet 4.6 and later Sonnet models, Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, and Claude Mythos Preview.
* **Keep the last turn only:** earlier Opus and Sonnet models, and all Haiku models through Claude Haiku 4.5. When you pass older thinking blocks back, the API strips them automatically. You don't need to remove them yourself.

Preservation brings two benefits:

* **Cache optimization:** preserved thinking blocks enable cache hits during tool use, as they are passed back with tool results and cached incrementally across the assistant turn, resulting in token savings in multistep workflows.
* **No intelligence impact:** preserving thinking blocks has no negative effect on model performance.

The tradeoff is context usage: long conversations consume more context space on keep-all models, because retained thinking blocks count as input like any other conversation history (see [Thinking and the context window](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-the-context-window)). The behavior is automatic in both regimes. No code changes or beta headers are required, and you should keep passing complete, unmodified thinking blocks back as described in [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks). To override the default in either direction, use [thinking block clearing](https://platform.claude.com/docs/en/build-with-claude/context-editing#thinking-block-clearing).

**Switching models mid-conversation.** Keep passing thinking blocks back unchanged when you switch models, for example after a [classifier refusal fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback). A thinking block is readable only by the model that produced it or a newer one, and the API ignores or drops the blocks the target model can't read. On Claude Fable 5.1 and Claude Mythos 5.1 the direction matters: they read every earlier model's thinking blocks and no earlier model reads theirs, so switching up to them keeps the conversation's reasoning and switching down drops it (see [Preserved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-for-model) for the exact list and for how dropped blocks are billed and reported). Strip prior `thinking` and `redacted_thinking` blocks yourself only to save input tokens on models that ignore rather than drop them, and never when redeeming a [fallback credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit), which requires the body unchanged.


## Preserved thinking

Source: https://platform.claude.com/llms-full.txt#preserved-thinking

[Preserved thinking](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking) decides whether the model can use a thinking block that you send back from an earlier turn. Starting with Claude Fable 5.1, the API checks the `signature` of every `thinking` or `redacted_thinking` block in a request for two things:

* **The model that produced it.** A model reads its own thinking blocks and those of earlier models, never those of a newer model. Claude Fable 5.1 reads blocks from Claude Opus 5, but Claude Opus 5 can't read blocks from Claude Fable 5.1. The API drops a block the current model can't read, without an error and without billing it. See [Switching models mid-conversation](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#switching-models).
* **Everything sent before it.** A block stays valid only while the top-level `system` prompt, the `tools`, and the messages before it are unchanged. If any of them changes, that block and every later thinking block are invalid, and the API rejects the request with a 400 error or drops the invalid blocks, whichever you choose. See [Keeping the prefix unchanged](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#prefix-check).

The model check applies to every account. The API enforces the prefix check by default for accounts created on or after August 31, 2026, 00:00 UTC. On older accounts it enforces the check only on requests that set `thinking.block_binding.prefix_mismatch_behavior`. Later models will enforce it for all accounts, so make your integration append-only now.

To keep thinking valid, send every assistant turn back exactly as you received it and add new messages only at the end of `messages`. If your code builds the `messages` array itself, the Preserved thinking page covers:

* [What counts as an edit](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#what-counts-as-an-edit), and [how to check whether your code makes one](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#how-to-tell-whether-your-integration-is-impacted).
* [The API feature that replaces each common edit](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#replace-prefix-edits): mid-conversation system messages for new instructions and per-turn reminders, `tool_addition` and `tool_removal` blocks for tool changes, per-message `output_config` for effort changes, and server-side compaction and context editing for trimming.
* [Client-side compaction](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#custom-compaction-on-the-client): which patterns keep thinking valid and which don't.
* [The `thinking-binding-controls-2026-08-01` beta header](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#preserved-thinking-controls). It adds an `input_transformations` array to every response that lists the blocks the API dropped, and a `block_binding.prefix_mismatch_behavior` field on the thinking configuration that accepts `"error"` or `"drop_block"`.


## Thinking and prompt caching

Source: https://platform.claude.com/llms-full.txt#thinking-and-prompt-caching

[Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) interacts with thinking in a few specific ways. The following rules apply in both thinking modes.

**Configuration changes invalidate caching.** The thinking configuration and the resolved [`effort`](https://platform.claude.com/docs/en/build-with-claude/effort) level are rendered into the prompt itself, so changing any of them starts a new cache prefix. Switching between `adaptive`, `enabled`, and `disabled`, changing `budget_tokens`, and changing the effort value all invalidate cache breakpoints: message-level breakpoints always miss, and tool and system-prompt breakpoints can miss too, depending on where the model renders the configuration. Treat any thinking or top-level effort change as starting the cache over. On models that support [per-message effort](https://platform.claude.com/docs/en/build-with-claude/effort#change-effort-mid-conversation-beta), an effort change carried in a `role: "system"` message inside `messages` leaves the cached prefix intact. Consecutive requests that keep the same configuration preserve the cache, and setting a parameter explicitly to its default value is equivalent to omitting it. A thinking block the API drops under either [preserved-thinking condition](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-thinking) changes the cached prefix from that block's position onward. Blocks passed back unchanged keep the cache intact. A worked demonstration with usage output is on the [Steering thinking](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#prompt-caching) page.

**Thinking blocks are cached with tool results.** During a tool-use loop, caching occurs when you make a follow-up request that includes tool results. At that point the previous conversation history, including its thinking blocks, can be cached, and those cached thinking blocks count as input tokens in your usage metrics when read from the cache. This occurs automatically, even without explicit `cache_control` markers, and behaves the same for regular and interleaved thinking. The tradeoff: thinking blocks you never see again in responses still contribute to input token usage when read from cache.

**Whether prior blocks are in context at all is per-model.** The [preservation default](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-block-preservation-by-model) governs this. On keep-all models, previous turns' thinking blocks stay cached and in context. On last-turn-only models, once you send a user message that isn't a tool result, all previous thinking blocks are stripped from context. On those models, a conversation like this:

```text wrap
User: ["What's the weather in Paris?"],
Assistant: [thinking_block_1] + [tool_use block 1],
User: [tool_result_1, cache=True],
Assistant: [thinking_block_2] + [text block 2],
User: [Text response, cache=True]

text wrap
User: ["What's the weather in Paris?"],
Assistant: [tool_use block 1],
User: [tool_result_1, cache=True],
Assistant: [text block 2],
User: [Text response, cache=True]
```

On keep-all models, the same request keeps `thinking_block_1` and `thinking_block_2` in context and in the cache.

**Degradation strips thinking from the cacheable history.** If thinking becomes disabled mid-turn and you pass thinking content in the current tool-use turn, the thinking content is stripped and thinking remains disabled for that request (see [graceful degradation](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-with-tool-use)). [Interleaved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#interleaved-thinking) amplifies cache invalidation effects, because thinking blocks can occur between multiple tool calls.

<Tip>
  Thinking-heavy tasks often take longer than the default 5-minute cache lifetime to complete. Consider the [1-hour cache duration](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#1-hour-cache-duration) to maintain cache hits across longer thinking sessions and multistep workflows.
</Tip>


## Thinking and the context window

Source: https://platform.claude.com/llms-full.txt#thinking-and-the-context-window

`max_tokens`, which includes all thinking Claude generates in the current turn, is enforced as a strict limit. On Claude 4.5 models and newer, if input tokens plus `max_tokens` exceeds the context window size, the API accepts the request. If generation then reaches the context window limit, it stops with `stop_reason: "model_context_window_exceeded"` instead of returning an error. On earlier models, the API returns a validation error instead. See [Handling stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons).

How thinking counts against the window depends on when it was generated:

* **Current-turn thinking** always counts toward `max_tokens`, is billed as output tokens, and occupies context window space for the turn that generated it.
* **Prior-turn thinking** depends on the [preservation default](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-block-preservation-by-model). On [models that keep all prior turns](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-block-preservation-by-model), previous thinking blocks remain in context, count toward the window, and are billed as input tokens like the rest of the conversation history. On models that keep only the last turn, the API strips older thinking blocks automatically when you pass them back, so they don't consume window space or input tokens.

In practice:

* On keep-all models, budget your context window as if thinking were ordinary conversation history, because it is. Long agentic sessions accumulate thinking in context. Use [thinking block clearing](https://platform.claude.com/docs/en/build-with-claude/context-editing#thinking-block-clearing) if you need to reclaim space.
* On last-turn-only models, thinking is a per-turn cost only: each turn's thinking counts against that turn's `max_tokens` and then drops out of the window.

The following diagrams illustrate the last-turn-only (stripping) regime. The first shows a multi-turn conversation: each turn's thinking block is generated in the output but not carried into later turns' input.

![Diagram of thinking on a model that strips previous thinking blocks: each turn's thinking block is generated in the output and not carried into later turns' input](https://platform.claude.com/docs/images/context-window-thinking.svg)

The second shows the same regime with tool use: thinking stays in context alongside its tool result for the duration of the assistant turn, then drops out on the next user turn.

![Diagram of thinking with tool use on a model that strips previous thinking blocks: thinking is kept with its tool result, then dropped on the next user turn](https://platform.claude.com/docs/images/context-window-thinking-tools.svg)

Use the [token counting API](https://platform.claude.com/docs/en/build-with-claude/token-counting) to get accurate counts for your specific use case, especially for multi-turn conversations that include thinking.


## Thinking encryption

Source: https://platform.claude.com/llms-full.txt#thinking-encryption

Full thinking content is encrypted and returned in the `signature` field on each thinking block. The API uses the signature to verify that thinking blocks were generated by Claude when you pass them back.

Keep the following in mind when working with signatures:

* It is only strictly necessary to send back thinking blocks when [using tools with thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-with-tool-use). Otherwise you can omit thinking blocks from previous turns. If you do pass them back, whether the API keeps or strips them depends on the model (see [Thinking block preservation by model](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-block-preservation-by-model)). Use [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) to configure this.
* When sending back thinking blocks, pass everything back exactly as you received it, for consistency and to avoid potential issues.
* When [streaming responses](https://platform.claude.com/docs/en/build-with-claude/thinking#streaming-thinking), the signature arrives as a `signature_delta` inside a `content_block_delta` event just before the `content_block_stop` event.
* `signature` values are significantly longer in Claude 4 and later models than in previous models.
* The `signature` field is opaque: don't interpret or parse it.
* `signature` values are compatible across platforms (the Claude API, [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), and [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)). Values generated on one platform work on another.


## Redacted thinking blocks

Source: https://platform.claude.com/llms-full.txt#redacted-thinking-blocks

In addition to regular `thinking` blocks, the API may return `redacted_thinking` blocks when portions of Claude's reasoning are safety-redacted. A `redacted_thinking` block contains encrypted thinking content in a `data` field, with no readable text:

The `data` field is opaque and encrypted. Like the `signature` field on regular thinking blocks, pass `redacted_thinking` blocks back to the API unchanged when continuing a multi-turn conversation with [tools](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-with-tool-use).

<Tip>
  If your code filters content blocks by type (for example, `block.type == "thinking"`) when round-tripping responses with tool use, also include `redacted_thinking` blocks. Filtering on `block.type == "thinking"` alone silently drops `redacted_thinking` blocks and breaks the multi-turn protocol described in [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks).
</Tip>

<Note>
  `redacted_thinking` blocks are a distinct content block type returned when thinking is safety-redacted. This is separate from the [`display: "omitted"`](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display) option, which returns regular `thinking` blocks with an empty `thinking` field.
</Note>


## Limits and feature compatibility

Source: https://platform.claude.com/llms-full.txt#limits-and-feature-compatibility

### Sampling parameters

On Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, Claude Mythos Preview, Claude Opus 5, Claude Opus 4.8, Claude Opus 4.7, and Claude Sonnet 5, non-default `temperature`, `top_p`, or `top_k` values return a 400 error on every request, regardless of whether thinking is used. On older models, the restriction applies only while thinking is on: `temperature` and `top_k` are incompatible with thinking, and `top_p` is allowed at values between 0.95 and 1.

### Response prefill and forced tool use

You can't prefill the assistant response while thinking is on. Forced tool use (`tool_choice: {"type": "any"}` or `{"type": "tool", ...}`) is incompatible with manual extended thinking but works with adaptive thinking. The exceptions are Claude Fable 5.1 and Claude Mythos 5.1, which reject forced tool use on every request with a 400 error. On those models, use `tool_choice: {"type": "auto"}` with [strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) or [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) instead. See [Thinking with tool use](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-with-tool-use).

### Output limits

Each model accepts `max_tokens` up to the ceiling listed here. On the [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing#extended-output-beta), the `output-300k-2026-03-24` [beta header](https://platform.claude.com/docs/en/api/beta-headers) raises that ceiling for the models with a batches ceiling listed.

| Model                 | Max output tokens | Batches beta ceiling |
| --------------------- | ----------------- | -------------------- |
| Claude Fable 5.1      | 128k              | —                    |
| Claude Mythos 5.1     | 128k              | —                    |
| Claude Fable 5        | 128k              | —                    |
| Claude Mythos 5       | 128k              | —                    |
| Claude Mythos Preview | 128k              | Not available        |
| Claude Opus 5         | 128k              | 300k                 |
| Claude Opus 4.8       | 128k              | 300k                 |
| Claude Opus 4.7       | 128k              | 300k                 |
| Claude Sonnet 5       | 128k              | 300k                 |
| Claude Opus 4.6       | 128k              | 300k                 |
| Claude Sonnet 4.6     | 128k              | 300k                 |
| Claude Haiku 4.5      | 64k               | Not available        |
| Claude Sonnet 4.5     | 64k               | Not available        |
| Claude Opus 4.5       | 64k               | Not available        |

See the [models overview](https://platform.claude.com/docs/en/models/overview) for limits on legacy models.

### Long requests

The SDKs require streaming when `max_tokens` is greater than 21,333, to avoid HTTP timeouts on long-running requests. This is a client-side validation, not an API restriction. If you don't need to process events incrementally, use `.stream()` with `.get_final_message()` (Python) or `.finalMessage()` (TypeScript) to get the complete `Message` object without handling individual events. See [Streaming Messages](https://platform.claude.com/docs/en/build-with-claude/streaming#get-the-final-message-without-handling-events). Expect longer response times when thinking is active, because generating thinking blocks adds processing time. For workloads that push thinking above roughly 32k tokens per request, use [batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing) to avoid networking issues: such requests can run long enough to hit system timeouts and open connection limits.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-20

<CardGroup cols={2}>
  <Card title="Steering thinking" icon="compass" href="https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost">
    Steer how often and how deeply Claude thinks with effort levels, system prompt guidance, and per-message steering, and understand thinking's cost and pricing.
  </Card>

  <Card title="Thinking in tool and multi-turn workflows" icon="wrench" href="https://platform.claude.com/docs/en/build-with-claude/thinking-tool-workflows">
    Walk through a complete two-turn tool-use round trip that preserves thinking blocks correctly, and see how interleaved thinking changes the flow.
  </Card>

  <Card title="Preserved thinking" icon="stack" href="https://platform.claude.com/docs/en/build-with-claude/preserved-thinking">
    Find out whether your Messages API integration edits conversation history, and replace each edit with the API feature that keeps earlier thinking blocks valid.
  </Card>

  <Card title="Troubleshooting thinking" icon="hammer" href="https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting">
    Diagnose and fix the most common thinking failures: configuration 400 errors, empty or missing thinking blocks, max\_tokens stops, and cache misses.
  </Card>

  <Card title="Effort" icon="sliders" href="https://platform.claude.com/docs/en/build-with-claude/effort">
    Control how many tokens Claude uses when responding with the effort parameter, trading off between response thoroughness and token efficiency.
  </Card>
</CardGroup>


---
title: Thinking in tool and multi-turn workflows
url: https://platform.claude.com/docs/en/build-with-claude/thinking-tool-workflows
description: Walk through a complete two-turn tool-use round trip that preserves thinking blocks correctly, and see how interleaved thinking changes the flow.
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

This page walks through a complete two-turn tool-use round trip with thinking enabled: Claude thinks, requests a tool call, receives the result, and finishes its answer, with the thinking blocks handled correctly at every step. The full rules live on the [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) page, in [Thinking with tool use](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-with-tool-use) and [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks); this page shows those rules applied in runnable code.


## The rules this walkthrough applies

Source: https://platform.claude.com/llms-full.txt#the-rules-this-walkthrough-applies

Each link leads to the full statement on the Thinking page:

* [Limit tool choice to `auto` or `none` in manual mode](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-with-tool-use): `tool_choice` options that force tool use return an error with manual extended thinking (`thinking: {type: "enabled"}`); adaptive thinking supports forced tool use.
* [Keep one thinking configuration per assistant turn](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-with-tool-use): a tool-use loop is one assistant turn, so change the configuration only between turns.
* [Pass thinking blocks back complete and unmodified](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks): when you return a tool result, the thinking blocks from the assistant message must come back with it.
* [Echo the assistant message exactly as received](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks): rebuilding the message or filtering out `redacted_thinking` blocks triggers a 400 error.

The samples use adaptive thinking; on models that support only extended thinking, substitute `thinking: {type: "enabled", budget_tokens: N}`. The round-trip rules are identical.


## Walk through a two-turn tool-use round trip

Source: https://platform.claude.com/llms-full.txt#walk-through-a-two-turn-tool-use-round-trip

The example defines a `get_weather` tool, lets Claude think and request a tool call, then returns the tool result along with the assistant turn echoed exactly as received, thinking block included.

<Steps>
  <Step title="Make the first request with a tool available">
    Send a request with adaptive thinking enabled and the tool defined. Apart from the `thinking` parameter, this is a standard [tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) request:

    <CodeGroup>
      ```bash CLI
      ant messages create --transform content <<'YAML'
      model: claude-opus-4-8
      max_tokens: 16000
      thinking:
        type: adaptive
      tools:
        - name: get_weather
          description: Get current weather for a location
          input_schema:
            type: object
            properties:
              location:
                type: string
                description: City name
            required:
              - location
      messages:
        - role: user
          content: "What's the weather in Paris?"
      YAML

python Python

      client = anthropic.Anthropic()

      weather_tool = {
          "name": "get_weather",
          "description": "Get current weather for a location",
          "input_schema": {
              "type": "object",
              "properties": {"location": {"type": "string", "description": "City name"}},
              "required": ["location"],
          },
      }

      # First request - Claude responds with thinking and tool request
      response = client.messages.create(
          model="claude-opus-4-8",
          max_tokens=16000,
          thinking={"type": "adaptive"},
          tools=[weather_tool],
          messages=[{"role": "user", "content": "What's the weather in Paris?"}],
      )
      print(response)

typescript TypeScript
      const client = new Anthropic();

      const weatherTool: Anthropic.Tool = {
        name: "get_weather",
        description: "Get current weather for a location",
        input_schema: {
          type: "object",
          properties: {
            location: { type: "string", description: "City name" }
          },
          required: ["location"]
        }
      };

      // First request - Claude responds with thinking and tool request
      const response = await client.messages.create({
        model: "claude-opus-4-8",
        max_tokens: 16000,
        thinking: {
          type: "adaptive"
        },
        tools: [weatherTool],
        messages: [{ role: "user", content: "What's the weather in Paris?" }]
      });
      console.log(response);

csharp C#
      AnthropicClient client = new();

      var weatherTool = new ToolUnion(new Tool()
      {
          Name = "get_weather",
          Description = "Get current weather for a location",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["location"] = JsonSerializer.SerializeToElement(new { type = "string", description = "City name" }),
              },
              Required = ["location"],
          },
      });

      var parameters = new MessageCreateParams
      {
          Model = Model.ClaudeOpus4_8,
          MaxTokens = 16000,
          Thinking = new ThinkingConfigAdaptive(),
          Tools = [weatherTool],
          Messages = [new() { Role = Role.User, Content = "What's the weather in Paris?" }]
      };

      var message = await client.Messages.Create(parameters);
      Console.WriteLine(message);

go Go
      client := anthropic.NewClient()

      weatherTool := anthropic.ToolUnionParam{
      	OfTool: &anthropic.ToolParam{
      		Name:        "get_weather",
      		Description: anthropic.String("Get current weather for a location"),
      		InputSchema: anthropic.ToolInputSchemaParam{
      			Properties: map[string]any{
      				"location": map[string]any{
      					"type":        "string",
      					"description": "City name",
      				},
      			},
      			Required: []string{"location"},
      		},
      	},
      }

      response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
      	Model:     anthropic.ModelClaudeOpus4_8,
      	MaxTokens: 16000,
      	Thinking: anthropic.ThinkingConfigParamUnion{
      		OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{},
      	},
      	Tools: []anthropic.ToolUnionParam{weatherTool},
      	Messages: []anthropic.MessageParam{
      		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather in Paris?")),
      	},
      })
      if err != nil {
      	log.Fatal(err)
      }
      fmt.Println(response)

java Java
      import com.anthropic.models.messages.ThinkingConfigAdaptive;
      // ...
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          MessageCreateParams params = MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_4_8)
              .maxTokens(16000L)
              .thinking(ThinkingConfigAdaptive.builder().build())
              .addTool(Tool.builder()
                  .name("get_weather")
                  .description("Get current weather for a location")
                  .inputSchema(Tool.InputSchema.builder()
                      .properties(JsonValue.from(Map.of(
                          "location", Map.of("type", "string", "description", "City name")
                      )))
                      .required(List.of("location"))
                      .build())
                  .build())
              .addUserMessage("What's the weather in Paris?")
              .build();

          Message response = client.messages().create(params);
          IO.println(response);

php PHP
      $client = new Client();

      $weatherTool = [
          'name' => 'get_weather',
          'description' => 'Get current weather for a location',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'location' => ['type' => 'string', 'description' => 'City name']
              ],
              'required' => ['location']
          ]
      ];

      $message = $client->messages->create(
          maxTokens: 16000,
          messages: [
              ['role' => 'user', 'content' => "What's the weather in Paris?"]
          ],
          model: 'claude-opus-4-8',
          thinking: ['type' => 'adaptive'],
          tools: [$weatherTool],
      );
      echo $message;

ruby Ruby
      client = Anthropic::Client.new

      weather_tool = {
        name: "get_weather",
        description: "Get current weather for a location",
        input_schema: {
          type: "object",
          properties: {
            location: { type: "string", description: "City name" }
          },
          required: ["location"]
        }
      }

      message = client.messages.create(
        model: "claude-opus-4-8",
        max_tokens: 16000,
        thinking: {
          type: "adaptive"
        },
        tools: [weather_tool],
        messages: [
          { role: "user", content: "What's the weather in Paris?" }
        ]
      )
      puts message

json Output
    {
      "content": [
        {
          "type": "thinking",
          "thinking": "The user wants to know the current weather in Paris. I have access to a function `get_weather`...",
          "signature": "BDaL4VrbR2Oj0hO4XpJxT28J5T...."
        },
        {
          "type": "text",
          "text": "I can help you get the current weather information for Paris. Let me check that for you"
        },
        {
          "type": "tool_use",
          "id": "toolu_01CswdEQBMshySk6Y9DFKrfq",
          "name": "get_weather",
          "input": {
            "location": "Paris"
          }
        }
      ]
    }

bash CLI
      # First turn: write the assistant content array (thinking and tool_use
      # blocks, signatures intact) to a file. Routing model-generated text
      # through a file keeps it out of shell-expansion position later.
      ant messages create --transform content --format jsonl \
        > assistant_content.json <<'YAML'
      model: claude-opus-4-8
      max_tokens: 16000
      thinking:
        type: adaptive
      tools:
        - name: get_weather
          description: Get current weather for a location
          input_schema:
            type: object
            properties:
              location:
                type: string
                description: City name
            required: [location]
      messages:
        - role: user
          content: What's the weather in Paris?
      YAML

      # Second turn: jq fills the two null placeholders from the captured file,
      # so the blocks return verbatim as the assistant message. The thinking
      # block MUST accompany the tool_use block. The quoted delimiter keeps the
      # shell from expanding anything in the body.
      jq --slurpfile blocks assistant_content.json '
        .messages[1].content = $blocks[0] |
        .messages[2].content[0].tool_use_id =
          ($blocks[0][] | select(.type == "tool_use") | .id)
      ' <<'JSON' | ant messages create
      {
        "model": "claude-opus-4-8",
        "max_tokens": 16000,
        "thinking": {"type": "adaptive"},
        "tools": [{
          "name": "get_weather",
          "description": "Get current weather for a location",
          "input_schema": {
            "type": "object",
            "properties": {
              "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
          }
        }],
        "messages": [
          {"role": "user", "content": "What's the weather in Paris?"},
          {"role": "assistant", "content": null},
          {"role": "user", "content": [{
            "type": "tool_result",
            "tool_use_id": null,
            "content": "Current temperature: 88°F"
          }]}
        ]
      }
      JSON

python Python

      client = anthropic.Anthropic()
      weather_tool = {
          "name": "get_weather",
          "description": "Get current weather for a location",
          "input_schema": {
              "type": "object",
              "properties": {"location": {"type": "string", "description": "City name"}},
              "required": ["location"],
          },
      }
      response = client.messages.create(
          model="claude-opus-4-8",
          max_tokens=16000,
          thinking={"type": "adaptive"},
          tools=[weather_tool],
          messages=[{"role": "user", "content": "What's the weather in Paris?"}],
      )
      # Extract the tool use block to get its ID for the tool result
      tool_use_block = next(block for block in response.content if block.type == "tool_use")

      # Call your actual weather API, here is where your actual API call would go
      # Let's pretend this is what we get back
      weather_data = {"temperature": 88}

      # Second request - Include the assistant turn and the tool result
      continuation = client.messages.create(
          model="claude-opus-4-8",
          max_tokens=16000,
          thinking={"type": "adaptive"},
          tools=[weather_tool],
          messages=[
              {"role": "user", "content": "What's the weather in Paris?"},
              # Echo the assistant content exactly as received. When a thinking
              # block is present, it must accompany the tool_use block.
              {"role": "assistant", "content": response.content},
              {
                  "role": "user",
                  "content": [
                      {
                          "type": "tool_result",
                          "tool_use_id": tool_use_block.id,
                          "content": f"Current temperature: {weather_data['temperature']}°F",
                      }
                  ],
              },
          ],
      )
      print(continuation)

typescript TypeScript
      const client = new Anthropic();

      const weatherTool: Anthropic.Tool = {
        name: "get_weather",
        description: "Get current weather for a location",
        input_schema: {
          type: "object",
          properties: {
            location: { type: "string", description: "City name" }
          },
          required: ["location"]
        }
      };

      const response = await client.messages.create({
        model: "claude-opus-4-8",
        max_tokens: 16000,
        thinking: {
          type: "adaptive"
        },
        tools: [weatherTool],
        messages: [{ role: "user", content: "What's the weather in Paris?" }]
      });

      // Extract the tool use block to get its ID for the tool result
      const toolUseBlock = response.content.find(
        (block): block is Anthropic.ToolUseBlock => block.type === "tool_use"
      );

      // Call your actual weather API, here is where your actual API call would go
      // Let's pretend this is what we get back
      const weatherData = { temperature: 88 };

      if (toolUseBlock) {
        // Second request - Include the assistant turn and the tool result
        const continuation = await client.messages.create({
          model: "claude-opus-4-8",
          max_tokens: 16000,
          thinking: {
            type: "adaptive"
          },
          tools: [weatherTool],
          messages: [
            { role: "user", content: "What's the weather in Paris?" },
            // Echo the assistant content exactly as received. When a thinking
            // block is present, it must accompany the tool_use block.
            { role: "assistant", content: response.content },
            {
              role: "user",
              content: [
                {
                  type: "tool_result" as const,
                  tool_use_id: toolUseBlock.id,
                  content: `Current temperature: ${weatherData.temperature}°F`
                }
              ]
            }
          ]
        });
        console.log(continuation);
      }

csharp C#
      AnthropicClient client = new();

      var weatherTool = new ToolUnion(new Tool()
      {
          Name = "get_weather",
          Description = "Get current weather for a location",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["location"] = JsonSerializer.SerializeToElement(new { type = "string", description = "City name" }),
              },
              Required = ["location"],
          },
      });

      var parameters = new MessageCreateParams
      {
          Model = Model.ClaudeOpus4_8,
          MaxTokens = 16000,
          Thinking = new ThinkingConfigAdaptive(),
          Tools = [weatherTool],
          Messages = [
              new() { Role = Role.User, Content = "What's the weather in Paris?" }
          ]
      };

      var response = await client.Messages.Create(parameters);

      // Extract the tool_use block to get its ID for the tool result
      ToolUseBlock? toolUseBlock = null;
      foreach (var block in response.Content)
      {
          if (block.TryPickToolUse(out var toolUse))
          {
              toolUseBlock = toolUse;
              break;
          }
      }

      var weatherData = new { temperature = 88 };

      // Build continuation with tool result
      var continuationParams = new MessageCreateParams
      {
          Model = Model.ClaudeOpus4_8,
          MaxTokens = 16000,
          Thinking = new ThinkingConfigAdaptive(),
          Tools = [weatherTool],
          Messages = [
              new() { Role = Role.User, Content = "What's the weather in Paris?" },
              // response.Content includes the thinking blocks; passing them back is required
              new() { Role = Role.Assistant, Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList() },
              new() { Role = Role.User, Content = new MessageParamContent(new List<ContentBlockParam>
              {
                  new ContentBlockParam(new ToolResultBlockParam()
                  {
                      ToolUseID = toolUseBlock?.ID ?? "",
                      Content = $"Current temperature: {weatherData.temperature}°F"
                  })
              })}
          ]
      };

      var continuation = await client.Messages.Create(continuationParams);
      Console.WriteLine(continuation);

go Go
      client := anthropic.NewClient()

      weatherTool := anthropic.ToolUnionParam{
      	OfTool: &anthropic.ToolParam{
      		Name:        "get_weather",
      		Description: anthropic.String("Get current weather for a location"),
      		InputSchema: anthropic.ToolInputSchemaParam{
      			Properties: map[string]any{
      				"location": map[string]any{
      					"type":        "string",
      					"description": "City name",
      				},
      			},
      			Required: []string{"location"},
      		},
      	},
      }

      response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
      	Model:     anthropic.ModelClaudeOpus4_8,
      	MaxTokens: 16000,
      	Thinking: anthropic.ThinkingConfigParamUnion{
      		OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{},
      	},
      	Tools: []anthropic.ToolUnionParam{weatherTool},
      	Messages: []anthropic.MessageParam{
      		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather in Paris?")),
      	},
      })
      if err != nil {
      	log.Fatal(err)
      }

      var toolUseBlock anthropic.ToolUseBlock
      for _, block := range response.Content {
      	if v, ok := block.AsAny().(anthropic.ToolUseBlock); ok {
      		toolUseBlock = v
      		break
      	}
      }

      weatherData := map[string]int{"temperature": 88}

      continuation, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
      	Model:     anthropic.ModelClaudeOpus4_8,
      	MaxTokens: 16000,
      	Thinking: anthropic.ThinkingConfigParamUnion{
      		OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{},
      	},
      	Tools: []anthropic.ToolUnionParam{weatherTool},
      	Messages: []anthropic.MessageParam{
      		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather in Paris?")),
      		response.ToParam(),
      		anthropic.NewUserMessage(
      			anthropic.NewToolResultBlock(toolUseBlock.ID, fmt.Sprintf("Current temperature: %d°F", weatherData["temperature"]), false),
      		),
      	},
      })
      if err != nil {
      	log.Fatal(err)
      }

      fmt.Println(continuation)

java Java
      import com.anthropic.models.messages.ThinkingConfigAdaptive;
      // ...

      void main() {
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          Tool weatherTool = Tool.builder()
              .name("get_weather")
              .description("Get current weather for a location")
              .inputSchema(Tool.InputSchema.builder()
                  .properties(JsonValue.from(Map.of(
                      "location", Map.of("type", "string", "description", "City name")
                  )))
                  .required(List.of("location"))
                  .build())
              .build();

          MessageCreateParams initialParams = MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_4_8)
              .maxTokens(16000L)
              .thinking(ThinkingConfigAdaptive.builder().build())
              .addTool(weatherTool)
              .addUserMessage("What's the weather in Paris?")
              .build();

          Message response = client.messages().create(initialParams);

          ToolUseBlock toolUseBlock = null;
          for (var block : response.content()) {
              if (block.toolUse().isPresent()) {
                  toolUseBlock = block.toolUse().get();
                  break;
              }
          }

          int temperature = 88;

          // Second request: echo the assistant turn as received, then the tool result
          MessageCreateParams continuationParams = MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_4_8)
              .maxTokens(16000L)
              .thinking(ThinkingConfigAdaptive.builder().build())
              .addTool(weatherTool)
              .addUserMessage("What's the weather in Paris?")
              .addMessage(response)
              .addUserMessageOfBlockParams(List.of(
                  ContentBlockParam.ofToolResult(
                      ToolResultBlockParam.builder()
                          .toolUseId(toolUseBlock.id())
                          .content("Current temperature: " + temperature + "°F")
                          .build()
                  )
              ))
              .build();

          Message continuation = client.messages().create(continuationParams);
          IO.println(continuation);
      }

php PHP
      $client = new Client();

      $weatherTool = [
          'name' => 'get_weather',
          'description' => 'Get current weather for a location',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'location' => [
                      'type' => 'string',
                      'description' => 'City name'
                  ]
              ],
              'required' => ['location']
          ]
      ];

      $response = $client->messages->create(
          maxTokens: 16000,
          messages: [
              ['role' => 'user', 'content' => "What's the weather in Paris?"]
          ],
          model: 'claude-opus-4-8',
          thinking: ['type' => 'adaptive'],
          tools: [$weatherTool],
      );

      $toolUseBlock = null;
      foreach ($response->content as $block) {
          if ($block->type === 'tool_use') {
              $toolUseBlock = $block;
              break;
          }
      }

      $weatherData = ['temperature' => 88];

      $continuation = $client->messages->create(
          maxTokens: 16000,
          messages: [
              ['role' => 'user', 'content' => "What's the weather in Paris?"],
              ['role' => 'assistant', 'content' => $response->content],
              ['role' => 'user', 'content' => [
                  [
                      'type' => 'tool_result',
                      'tool_use_id' => $toolUseBlock->id,
                      'content' => "Current temperature: {$weatherData['temperature']}°F"
                  ]
              ]]
          ],
          model: 'claude-opus-4-8',
          thinking: ['type' => 'adaptive'],
          tools: [$weatherTool],
      );

      echo $continuation;

ruby Ruby
      client = Anthropic::Client.new

      weather_tool = {
        name: "get_weather",
        description: "Get current weather for a location",
        input_schema: {
          type: "object",
          properties: {
            location: { type: "string", description: "City name" }
          },
          required: ["location"]
        }
      }

      response = client.messages.create(
        model: "claude-opus-4-8",
        max_tokens: 16000,
        thinking: {
          type: "adaptive"
        },
        tools: [weather_tool],
        messages: [
          { role: "user", content: "What's the weather in Paris?" }
        ]
      )

      tool_use_block = response.content.find { |block| block.type == :tool_use }

      raise "No tool_use block found" unless tool_use_block

      weather_data = { temperature: 88 }

      continuation = client.messages.create(
        model: "claude-opus-4-8",
        max_tokens: 16000,
        thinking: {
          type: "adaptive"
        },
        tools: [weather_tool],
        messages: [
          { role: "user", content: "What's the weather in Paris?" },
          { role: "assistant", content: response.content },
          { role: "user", content: [
            {
              type: "tool_result",
              tool_use_id: tool_use_block.id,
              content: "Current temperature: #{weather_data[:temperature]}°F"
            }
          ] }
        ]
      )

      puts continuation

json Output
    {
      "content": [
        {
          "type": "text",
          "text": "Currently in Paris, the temperature is 88°F (31°C)"
        }
      ]
    }
    ```
  </Step>
</Steps>


## How interleaved thinking changes the flow

Source: https://platform.claude.com/llms-full.txt#how-interleaved-thinking-changes-the-flow

Interleaved thinking lets Claude think between tool calls, reasoning about each tool result before acting on it. The concept and per-model availability are covered in [Interleaved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#interleaved-thinking) on the Thinking page; interleaving changes where thinking blocks appear, not whether tool calls can chain. The following comparison shows what interleaved thinking changes in a two-tool workflow:

<AccordionGroup>
  <Accordion title="Tool use without interleaved thinking">
    Without interleaved thinking, Claude thinks once at the start of the assistant turn. Subsequent responses after tool results continue without new thinking blocks.

</Accordion>

  <Accordion title="Tool use with interleaved thinking">
    With interleaved thinking enabled, Claude can think after receiving each tool result, allowing it to reason about intermediate results before continuing.

</Accordion>
</AccordionGroup>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-21

<CardGroup cols={3}>
  <Card title="Thinking" icon="brain" href="https://platform.claude.com/docs/en/build-with-claude/thinking">
    The overview: turn thinking on, read thinking output, and review the full rules for tool use, caching, and streaming.
  </Card>

  <Card title="Steering thinking" icon="compass" href="https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost">
    Steer how often and how deeply Claude thinks with effort levels and prompt-based guidance.
  </Card>

  <Card title="Extended thinking" icon="clock" href="https://platform.claude.com/docs/en/build-with-claude/extended-thinking">
    Manual thinking budgets on older models: `budget_tokens` mechanics and migration to adaptive.
  </Card>
</CardGroup>


---
title: Troubleshooting thinking
url: https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting
description: "Diagnose and fix the most common thinking failures: configuration 400 errors, empty or missing thinking blocks, max_tokens stops, and cache misses."
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

This page covers the most common failures when configuring thinking or round-tripping thinking blocks (sending returned thinking blocks back in later requests). The first section maps each model to its supported thinking configurations and the ones it rejects; the sections after it each start from a symptom you observe, so you can match an error message or unexpected response directly to its cause and fix. To learn how thinking works, see the [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) overview.


## Thinking support, defaults, and rejected configurations by model

Source: https://platform.claude.com/llms-full.txt#thinking-support-defaults-and-rejected-configurations-by-model

Most thinking configuration errors are a mismatch between the `thinking.type` value in the request and what the model supports. On most models, thinking runs as `thinking: {type: "adaptive"}`, and many have it on by default. Some earlier models instead use [extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking), a legacy manual mode configured as `thinking: {type: "enabled", budget_tokens: N}`.

Extended thinking (`thinking.type: "enabled"` with `budget_tokens`) is deprecated on the Claude 4.6 models (requests using it still succeed). Claude 4.7 and later models do not support it and reject requests that use it, returning a 400 error. On Claude 4.5 and earlier models that support thinking, extended thinking is the only available thinking mode. Claude Mythos Preview supports both modes. Where both modes are available, use [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) instead.

The table lists what each model supports, what it defaults to, and which `thinking.type` values it rejects with a 400 error; any value not listed as rejected is accepted.

| Model                 | Thinking types                   | Default   | Rejected with 400          |
| --------------------- | -------------------------------- | --------- | -------------------------- |
| Claude Fable 5.1      | Adaptive only                    | Always on | `"enabled"`, `"disabled"`  |
| Claude Mythos 5.1     | Adaptive only                    | Always on | `"enabled"`, `"disabled"`  |
| Claude Fable 5        | Adaptive only                    | Always on | `"enabled"`, `"disabled"`  |
| Claude Mythos 5       | Adaptive only                    | Always on | `"enabled"`, `"disabled"`  |
| Claude Mythos Preview | Adaptive, extended               | Always on | `"disabled"`               |
| Claude Opus 5         | Adaptive only                    | On        | `"enabled"`, `"disabled"`2 |
| Claude Opus 4.8       | Adaptive only                    | Off       | `"enabled"`                |
| Claude Opus 4.7       | Adaptive only                    | Off       | `"enabled"`                |
| Claude Sonnet 5       | Adaptive only                    | On        | `"enabled"`                |
| Claude Opus 4.6       | Adaptive, extended (deprecated)1 | Off       | None                       |
| Claude Sonnet 4.6     | Adaptive, extended (deprecated)1 | Off       | None                       |
| Claude Opus 4.5       | Extended only                    | Off       | `"adaptive"`               |
| Claude Haiku 4.5      | Extended only                    | Off       | `"adaptive"`               |
| Claude Sonnet 4.5     | Extended only                    | Off       | `"adaptive"`               |

*1 `enabled` and `budget_tokens` still work on these models but are deprecated; use adaptive thinking instead.*\
*2 Claude Opus 5 accepts `"disabled"` at [effort](https://platform.claude.com/docs/en/build-with-claude/effort) `high` or below; combining it with effort `xhigh` or `max` returns a 400 error. This restriction applies to Claude Opus 5 and later models and is enforced on each request.*

Models marked `Always on` cannot turn thinking off. Models marked `On` default to thinking but accept `thinking: {type: "disabled"}`.

Earlier Claude 4 models (Claude Opus 4.1, Claude Sonnet 4, and Claude Opus 4) support extended thinking only. See [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations) for their availability. Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, and Claude Mythos 5 are not available under [zero data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements) unless expressly authorized by Anthropic.


## A 400 error says `"thinking.type.enabled"` is not supported

Source: https://platform.claude.com/llms-full.txt#a-400-error-says-thinking-type-enabled-is-not-supported

The request fails with a 400 error whose message reads:

```text wrap
"thinking.type.enabled" is not supported for this model. Use "thinking.type.adaptive" and "output_config.effort" to control thinking behavior.
```

This happens because the model you requested has removed extended thinking (see the [per-model configuration table](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#rejected-configurations)).

Switch the request to `thinking: {type: "adaptive"}` and steer thinking depth with `effort` instead of `budget_tokens`. [Migrating to adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking#migrating-to-adaptive-thinking) walks through the conversion.


## A 400 error says `"thinking.type.disabled"` is not supported

Source: https://platform.claude.com/llms-full.txt#a-400-error-says-thinking-type-disabled-is-not-supported

The request fails with a 400 error whose message reads:

```text wrap
"thinking.type.disabled" is not supported for this model. Thinking defaults to adaptive mode when not specified; use "thinking.type.enabled" with "budget_tokens" for extended thinking.
```

This happens on models where thinking is always on: Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, and Claude Mythos Preview reject `"disabled"`. All of these except Claude Mythos Preview also reject the error text's suggested `"thinking.type.enabled"`.

Omit the `thinking` parameter; these models think without any configuration. If your goal was to keep thinking text out of responses, use `display: "omitted"` instead of disabling thinking; see [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display).

A 400 error on `"disabled"` can also occur on Claude Opus 5, which accepts `thinking: {type: "disabled"}` only at [effort](https://platform.claude.com/docs/en/build-with-claude/effort) `high` or below: combining it with effort `xhigh` or `max` is rejected. Lower the effort level, or leave thinking on.


## A 400 error says adaptive thinking is not supported

Source: https://platform.claude.com/llms-full.txt#a-400-error-says-adaptive-thinking-is-not-supported

The request fails with a 400 error whose message reads:

```text wrap
adaptive thinking is not supported on this model
```

This happens because the model supports only extended thinking (see the [per-model configuration table](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#rejected-configurations)).

Use `thinking: {type: "enabled", budget_tokens: N}` instead; see [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) for the configuration.


## A 400 error says thinking blocks cannot be modified

Source: https://platform.claude.com/llms-full.txt#a-400-error-says-thinking-blocks-cannot-be-modified

A request that returns tool results fails with a 400 `invalid_request_error` whose message contains:

```text wrap
`thinking` or `redacted_thinking` blocks in the latest assistant message cannot be modified
```

In multi-turn and tool-use conversations you send previous assistant messages, including their `thinking` and `redacted_thinking` blocks, back to the API, and the API verifies they arrive unmodified. This error happens when the assistant message you send back differs from the one the API returned, most often because your code filters content blocks by type and drops `redacted_thinking` blocks, or rebuilds the assistant message instead of echoing it.

Echo the assistant turn back verbatim, thinking blocks included. See [Preserving thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks) for the rules, and the worked round trip in [Thinking in tool and multi-turn workflows](https://platform.claude.com/docs/en/build-with-claude/thinking-tool-workflows#two-turn-tool-use-round-trip) for correct code in every SDK.


## A 400 error says a thinking block signature is invalid

Source: https://platform.claude.com/llms-full.txt#a-400-error-says-a-thinking-block-signature-is-invalid

A request to Claude Fable 5.1 that replays earlier thinking blocks fails with a 400 `invalid_request_error` whose message reads:

```text wrap
messages.{i}.content.{j}: Invalid `signature` in `thinking` block. The block is bound to a different conversation. Remove the block, or set `thinking.block_binding.prefix_mismatch_behavior` to "drop_block".
```

If the request didn't send the `thinking-binding-controls-2026-08-01` beta header, the message adds ``That setting requires the `thinking-binding-controls-2026-08-01` value in the `anthropic-beta` header.`` The message can also end with a sentence naming the first message that changed. If the message has no reason clause at all, the block's content was modified. See [A 400 error says thinking blocks cannot be modified](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#error-thinking-blocks-modified).

On Claude Fable 5.1, the API accepts a replayed thinking block [only while the `system` prompt, `tools`, and messages that preceded it are unchanged](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-in-conversation). The error means something earlier in the conversation changed between requests: an edited, reordered, or removed turn, a per-turn reminder that was injected and later removed, a rebuilt `system` prompt or `tools` array, or client-side compaction that kept recent turns and their thinking verbatim. The check is enforced for new accounts created on or after August 31, 2026, and for any request that sets `thinking.block_binding.prefix_mismatch_behavior`. Server-side [compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) and [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) never trigger it.

To fix it, keep the history append-only: pass earlier turns back exactly as sent and received, add instructions with a [mid-conversation system message](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages) instead of editing `system` or `tools`, and let server-side [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) or [compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) do any trimming. Retrying the same request body doesn't clear the error. To continue this request without the invalidated reasoning, send the `thinking-binding-controls-2026-08-01` beta header and set `thinking.block_binding.prefix_mismatch_behavior` to `"drop_block"`. Alternatively, strip every `thinking` and `redacted_thinking` block from the history (at minimum the named block and every one after it, in that turn and all later turns), leave each turn's other blocks in place, and retry once.

A block from a model the target model can't read never produces this error: the API drops it and, under the beta header, reports it in `input_transformations`.


## The thinking field is empty in the response

Source: https://platform.claude.com/llms-full.txt#the-thinking-field-is-empty-in-the-response

The response contains `thinking` blocks, but their `thinking` field is an empty string and only the `signature` field is populated.

This happens because `display` defaults to `"omitted"` on newer models, which returns thinking blocks without their text.

Set `display: "summarized"` in your thinking configuration to receive the summarized thinking text. See [Controlling thinking display](https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display) for the defaults per model. If you only want the short status lines some models write between tool calls, and not the reasoning, set `display: "updates"` (beta) instead. See [Progress updates between tool calls](https://platform.claude.com/docs/en/build-with-claude/thinking#progress-updates).


## No thinking block appears on some turns

Source: https://platform.claude.com/llms-full.txt#no-thinking-block-appears-on-some-turns

Some responses contain no `thinking` block at all, even though thinking is configured.

This is normal in adaptive mode: Claude skips thinking on requests it judges simple enough to answer directly.

If you want thinking more often or more deeply, raise `effort` or steer with prompting; see [Steering how often Claude thinks](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#tuning-thinking-behavior).


## Tool calls or XML tags appear in the text output

Source: https://platform.claude.com/llms-full.txt#tool-calls-or-xml-tags-appear-in-the-text-output

A response occasionally writes a tool call into its text instead of emitting a `tool_use` block, or includes `<thinking>` or other internal XML tags in its visible text. A leaked tool call never runs, and in agentic loops the leaked text stays in the conversation history, so later turns are affected as well.

This happens on Claude Opus 5 when thinking is disabled, most commonly on tool-heavy workloads such as search. System-prompt rules instructing the model not to think or not to reason increase the tag leakage.

Re-enable thinking (the default) and use lower `effort` levels to control token cost instead. If your integration must keep thinking disabled, apply the prompting mitigations in [Running with thinking disabled](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5#running-with-thinking-disabled).


## The response stops with `stop_reason: "max_tokens"`

Source: https://platform.claude.com/llms-full.txt#the-response-stops-with-stop-reason-max-tokens

The response ends with `stop_reason: "max_tokens"`, often with a truncated or missing text block.

This happens because thinking tokens count toward `max_tokens`, so a long thinking pass can consume the budget before the text response completes.

Raise `max_tokens` to leave room for both thinking and text, or lower `effort` so Claude spends less on thinking; see [Cost control](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#cost-control) and [Thinking and the context window](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-the-context-window).


## Cache hits drop after changing thinking settings

Source: https://platform.claude.com/llms-full.txt#cache-hits-drop-after-changing-thinking-settings

`cache_read_input_tokens` falls to zero on requests that previously hit the cache.

This happens because the thinking configuration and the effort level (or its default) are part of the cached prompt prefix, so changing any of them starts a new prefix: switching thinking modes, changing the effort value, and changing `budget_tokens` all invalidate message cache breakpoints, and can invalidate tool and system-prompt breakpoints too, depending on where the model renders the configuration.

Keep the thinking configuration and effort level constant across requests that share a conversation; setting a parameter explicitly to its default is equivalent to omitting it and does not invalidate. See [Thinking and prompt caching](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-prompt-caching).


## Setting effort does not change thinking

Source: https://platform.claude.com/llms-full.txt#setting-effort-does-not-change-thinking

You change `effort` but thinking frequency or depth stays the same.

This happens because effort is the primary thinking lever only in adaptive mode. On extended-thinking-only models, thinking depth is set by `budget_tokens` instead.

Adjust `budget_tokens` on those models, or check which mode your model runs in; see [Thinking and effort](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-effort). On Claude Opus 4.5, the one extended-thinking-only model that supports effort, effort composes with the budget; see [Budget rules and tuning](https://platform.claude.com/docs/en/build-with-claude/extended-thinking#budget-rules-and-tuning).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-22

<CardGroup cols={3}>
  <Card title="Thinking" icon="brain" href="https://platform.claude.com/docs/en/build-with-claude/thinking">
    The overview: what thinking is, how to configure it, and how it interacts with tools, caching, and streaming.
  </Card>

  <Card title="Errors" icon="book" href="https://platform.claude.com/docs/en/api/errors">
    The full error reference, including the thinking configuration 400s with their exact server messages.
  </Card>

  <Card title="Migrating to adaptive thinking" icon="arrow-right" href="https://platform.claude.com/docs/en/build-with-claude/extended-thinking#migrating-to-adaptive-thinking">
    Convert `budget_tokens` requests to adaptive thinking with effort.
  </Card>
</CardGroup>


### Tools

---
title: Tool use with Claude
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
description: Connect Claude to external tools and APIs. See where tools execute, when Claude calls them, and which tool fits your task.
---

Tool use (also called function calling) lets Claude call functions that you define or that Anthropic provides. Claude determines when to call a tool based on the user's request and the tool's description. It then returns a structured call that your application executes (client tools) or that Anthropic executes (server tools).

Here's a minimal example using a server tool, the [Web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool), which Anthropic executes for you:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "tools": [{"type": "web_search_20260209", "name": "web_search"}],
      "messages": [{"role": "user", "content": "What'\''s the latest on the Mars rover?"}]
    }'

bash CLI
  ant messages create --transform content --format yaml \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --tool '{type: web_search_20260209, name: web_search}' \
    --message '{role: user, content: "What is the latest on the Mars rover?"}'

python Python
  client = anthropic.Anthropic()
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[{"type": "web_search_20260209", "name": "web_search"}],
      messages=[{"role": "user", "content": "What's the latest on the Mars rover?"}],
  )
  print(response.content)

typescript TypeScript
  const client = new Anthropic();
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [{ type: "web_search_20260209", name: "web_search" }],
    messages: [{ role: "user", content: "What's the latest on the Mars rover?" }]
  });
  console.log(response.content);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = [new ToolUnion(new WebSearchTool20260209())],
      Messages = [new() { Role = Role.User, Content = "What's the latest on the Mars rover?" }]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message.Content);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{
  		{OfWebSearchTool20260209: &anthropic.WebSearchTool20260209Param{}},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the latest on the Mars rover?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.Content)

java Java
  import com.anthropic.models.messages.WebSearchTool20260209;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addTool(WebSearchTool20260209.builder().build())
          .addUserMessage("What's the latest on the Mars rover?")
          .build();

      Message response = client.messages().create(params);
      IO.println(response.content());
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: [
          ['type' => 'web_search_20260209', 'name' => 'web_search'],
      ],
      messages: [
          ['role' => 'user', 'content' => "What's the latest on the Mars rover?"],
      ],
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [{ type: "web_search_20260209", name: "web_search" }],
    messages: [{ role: "user", content: "What's the latest on the Mars rover?" }]
  )
  puts message.content
  ```
</CodeGroup>

Claude runs the search on Anthropic's infrastructure and returns the cited results in the same response. To have Claude call a function that you define, pass a tool with an `input_schema`, then execute the call when Claude returns a `tool_use` block. [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview#how-tool-use-works) shows that round trip end to end. Learn more about [defining tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) and [handling tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls).


## How tool use works

Source: https://platform.claude.com/llms-full.txt#how-tool-use-works

Tools differ primarily by where the code executes. **Client tools** (including user-defined tools and tools with Anthropic-defined schemas, such as `bash` and `text_editor`) run in your application. Claude responds with `stop_reason: "tool_use"` and one or more `tool_use` blocks. Your code executes the operation and sends back a `tool_result`. **Server tools** (such as `web_search`, `web_fetch`, `code_execution`, and `tool_search`) run on Anthropic's infrastructure: you see the results directly without handling execution, unless Claude calls the tool in the same group of parallel tool calls as one of your client tools (see [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#tool-use)).

Here's that round trip in full for a client tool. The first request defines a `get_weather` tool, and Claude answers the question by calling it: the response carries a `tool_use` block, your code runs the lookup, and a second request sends the result back in a `tool_result` block so Claude can reply with the answer.

<CodeGroup>
  ```bash cURL
  # Claude replies with a tool_use block naming the tool and its arguments.
  TOOLS='[
    {
      "name": "get_weather",
      "description": "Get the current weather for a given location.",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {"type": "string", "description": "City and state, e.g. San Francisco, CA"}
        },
        "required": ["location"]
      }
    }
  ]'
  USER_MSG="What's the weather in San Francisco?"
  RESPONSE=$(curl -s https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "$(jq -n --argjson tools "$TOOLS" --arg msg "$USER_MSG" '{
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: $tools,
      # Ask for at most one tool call per turn.
      tool_choice: {type: "auto", disable_parallel_tool_use: true},
      messages: [{role: "user", content: $msg}]
    }')")
  TOOL_USE=$(echo "$RESPONSE" | jq '.content[] | select(.type == "tool_use")')
  echo "Claude called $(echo "$TOOL_USE" | jq -r '.name') with $(echo "$TOOL_USE" | jq -c '.input')"

  # Run the tool, then send the result back in a tool_result block.
  # Claude uses the result to answer the original question.
  WEATHER="15 degrees Celsius, partly cloudy"
  curl -s https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "$(jq -n \
      --argjson tools "$TOOLS" \
      --arg msg "$USER_MSG" \
      --argjson assistant "$(echo "$RESPONSE" | jq '.content')" \
      --arg tool_use_id "$(echo "$TOOL_USE" | jq -r '.id')" \
      --arg weather "$WEATHER" \
      '{
        model: "claude-opus-5",
        max_tokens: 1024,
        tools: $tools,
        tool_choice: {type: "auto", disable_parallel_tool_use: true},
        messages: [
          {role: "user", content: $msg},
          {role: "assistant", content: $assistant},
          {role: "user", content: [
            {type: "tool_result", tool_use_id: $tool_use_id, content: $weather}
          ]}
        ]
      }')"

bash CLI
  # ant reads the request body as YAML on stdin; jq carries the conversation
  # state into the second request.
  USER_MSG="What's the weather in San Francisco?"
  MESSAGES=$(jq -n --arg msg "$USER_MSG" '[{role: "user", content: $msg}]')
  call_api() {
    {
      cat <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  # Ask for at most one tool call per turn.
  tool_choice: {type: auto, disable_parallel_tool_use: true}
  tools:
    - name: get_weather
      description: Get the current weather for a given location.
      input_schema:
        type: object
        properties:
          location: {type: string, description: "City and state, e.g. San Francisco, CA"}
        required: [location]
  YAML
      printf 'messages: %s\n' "$MESSAGES"
    } | ant messages create --format json
  }

  # Claude replies with a tool_use block naming the tool and its arguments.
  RESPONSE=$(call_api)
  TOOL_USE=$(jq '.content[] | select(.type == "tool_use")' <<<"$RESPONSE")
  echo "Claude called $(jq -r '.name' <<<"$TOOL_USE") with $(jq -c '.input' <<<"$TOOL_USE")"

  # Run the tool, then send the result back in a tool_result block.
  WEATHER="15 degrees Celsius, partly cloudy"
  MESSAGES=$(jq \
    --argjson assistant "$(jq '.content' <<<"$RESPONSE")" \
    --arg tool_use_id "$(jq -r '.id' <<<"$TOOL_USE")" \
    --arg weather "$WEATHER" \
    '. + [
      {role: "assistant", content: $assistant},
      {role: "user", content: [
        {type: "tool_result", tool_use_id: $tool_use_id, content: $weather}
      ]}
    ]' <<<"$MESSAGES")

  # Claude uses the result to answer the original question.
  call_api

python Python
  client = anthropic.Anthropic()

  tools = [
      {
          "name": "get_weather",
          "description": "Get the current weather for a given location.",
          "input_schema": {
              "type": "object",
              "properties": {
                  "location": {
                      "type": "string",
                      "description": "City and state, e.g. San Francisco, CA",
                  }
              },
              "required": ["location"],
          },
      }
  ]
  messages = [{"role": "user", "content": "What's the weather in San Francisco?"}]

  # Claude replies with a tool_use block naming the tool and its arguments.
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=tools,
      # Ask for at most one tool call per turn.
      tool_choice={"type": "auto", "disable_parallel_tool_use": True},
      messages=messages,
  )
  tool_use = next(block for block in response.content if block.type == "tool_use")
  print(f"Claude called {tool_use.name} with {json.dumps(tool_use.input)}")

  # Run the tool, then send the result back in a tool_result block.
  weather = "15 degrees Celsius, partly cloudy"  # your weather lookup goes here
  messages += [
      {"role": "assistant", "content": response.content},
      {
          "role": "user",
          "content": [
              {"type": "tool_result", "tool_use_id": tool_use.id, "content": weather}
          ],
      },
  ]
  followup = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=tools,
      tool_choice={"type": "auto", "disable_parallel_tool_use": True},
      messages=messages,
  )

  # Claude uses the result to answer the original question.
  final_text = next(block for block in followup.content if block.type == "text")
  print(final_text.text)

typescript TypeScript
  const client = new Anthropic();

  const tools: Anthropic.Tool[] = [
    {
      name: "get_weather",
      description: "Get the current weather for a given location.",
      input_schema: {
        type: "object",
        properties: {
          location: { type: "string", description: "City and state, e.g. San Francisco, CA" }
        },
        required: ["location"]
      }
    }
  ];
  const messages: Anthropic.MessageParam[] = [
    { role: "user", content: "What's the weather in San Francisco?" }
  ];

  // Claude replies with a tool_use block naming the tool and its arguments.
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools,
    // Ask for at most one tool call per turn.
    tool_choice: { type: "auto", disable_parallel_tool_use: true },
    messages
  });
  const toolUse = response.content.find(
    (block): block is Anthropic.ToolUseBlock => block.type === "tool_use"
  )!;
  console.log(`Claude called ${toolUse.name} with ${JSON.stringify(toolUse.input)}`);

  // Run the tool, then send the result back in a tool_result block.
  const weather = "15 degrees Celsius, partly cloudy"; // your weather lookup goes here
  messages.push(
    { role: "assistant", content: response.content },
    {
      role: "user",
      content: [{ type: "tool_result", tool_use_id: toolUse.id, content: weather }]
    }
  );
  const followup = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools,
    tool_choice: { type: "auto", disable_parallel_tool_use: true },
    messages
  });

  // Claude uses the result to answer the original question.
  const finalText = followup.content.find(
    (block): block is Anthropic.TextBlock => block.type === "text"
  )!;
  console.log(finalText.text);

csharp C#
  AnthropicClient client = new();

  List<ToolUnion> tools =
  [
      new ToolUnion(new Tool()
      {
          Name = "get_weather",
          Description = "Get the current weather for a given location.",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["location"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "string",
                      description = "City and state, e.g. San Francisco, CA",
                  }),
              },
              Required = ["location"],
          },
      }),
  ];

  // Ask for at most one tool call per turn.
  var toolChoice = new ToolChoice(new ToolChoiceAuto { DisableParallelToolUse = true });

  const string userPrompt = "What's the weather in San Francisco?";

  // Claude replies with a tool_use block naming the tool and its arguments.
  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = tools,
      ToolChoice = toolChoice,
      Messages = [new() { Role = Role.User, Content = userPrompt }],
  });
  ToolUseBlock? toolUse = null;
  foreach (var block in response.Content)
  {
      if (block.TryPickToolUse(out var picked))
      {
          toolUse = picked;
          break;
      }
  }
  Console.WriteLine($"Claude called {toolUse!.Name} with {JsonSerializer.Serialize(toolUse.Input)}");

  // Run the tool, then send the result back in a tool_result block.
  var weather = "15 degrees Celsius, partly cloudy";
  List<ContentBlockParam> toolResults =
  [
      new ContentBlockParam(new ToolResultBlockParam()
      {
          ToolUseID = toolUse.ID,
          Content = weather,
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

  // Claude uses the result to answer the original question.
  foreach (var block in followup.Content)
  {
      if (block.TryPickText(out var text))
      {
          Console.WriteLine(text.Text);
      }
  }

go Go
  client := anthropic.NewClient()
  ctx := context.Background()

  tools := []anthropic.ToolUnionParam{
  	{OfTool: &anthropic.ToolParam{
  		Name:        "get_weather",
  		Description: anthropic.String("Get the current weather for a given location."),
  		InputSchema: anthropic.ToolInputSchemaParam{
  			Properties: map[string]any{
  				"location": map[string]any{
  					"type":        "string",
  					"description": "City and state, e.g. San Francisco, CA",
  				},
  			},
  			Required: []string{"location"},
  		},
  	}},
  }
  // Ask for at most one tool call per turn.
  toolChoice := anthropic.ToolChoiceUnionParam{
  	OfAuto: &anthropic.ToolChoiceAutoParam{DisableParallelToolUse: anthropic.Bool(true)},
  }
  messages := []anthropic.MessageParam{
  	anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather in San Francisco?")),
  }

  // Claude replies with a tool_use block naming the tool and its arguments.
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
  var toolUse anthropic.ContentBlockUnion
  for _, block := range response.Content {
  	if block.Type == "tool_use" {
  		toolUse = block
  		break
  	}
  }
  fmt.Printf("Claude called %s with %s\n", toolUse.Name, string(toolUse.Input))

  // Run the tool, then send the result back in a tool_result block.
  weather := "15 degrees Celsius, partly cloudy"
  var assistantContent []anthropic.ContentBlockParamUnion
  for _, block := range response.Content {
  	assistantContent = append(assistantContent, block.ToParam())
  }
  messages = append(messages,
  	anthropic.NewAssistantMessage(assistantContent...),
  	anthropic.NewUserMessage(anthropic.NewToolResultBlock(toolUse.ID, weather, false)),
  )
  followup, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  	Model:      anthropic.ModelClaudeOpus5,
  	MaxTokens:  1024,
  	Tools:      tools,
  	ToolChoice: toolChoice,
  	Messages:   messages,
  })
  if err != nil {
  	log.Fatal(err)
  }

  // Claude uses the result to answer the original question.
  for _, block := range followup.Content {
  	if block.Type == "text" {
  		fmt.Println(block.Text)
  	}
  }

java Java
  import com.anthropic.core.JsonValue;
  import com.anthropic.models.messages.ContentBlockParam;
  // ...
  import com.anthropic.models.messages.Tool;
  import com.anthropic.models.messages.Tool.InputSchema;
  import com.anthropic.models.messages.ToolChoiceAuto;
  import com.anthropic.models.messages.ToolResultBlockParam;
  import com.anthropic.models.messages.ToolUseBlock;
  // ...

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      Tool weatherTool = Tool.builder()
          .name("get_weather")
          .description("Get the current weather for a given location.")
          .inputSchema(InputSchema.builder()
              .properties(JsonValue.from(Map.of(
                  "location", Map.of(
                      "type", "string",
                      "description", "City and state, e.g. San Francisco, CA"
                  )
              )))
              .required(List.of("location"))
              .build())
          .build();

      // Ask for at most one tool call per turn.
      ToolChoiceAuto toolChoice = ToolChoiceAuto.builder()
          .disableParallelToolUse(true)
          .build();

      String userPrompt = "What's the weather in San Francisco?";

      // Claude replies with a tool_use block naming the tool and its arguments.
      Message response = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addTool(weatherTool)
          .toolChoice(toolChoice)
          .addUserMessage(userPrompt)
          .build());
      ToolUseBlock toolUse = response.content().stream()
          .flatMap(block -> block.toolUse().stream())
          .findFirst()
          .orElseThrow();
      IO.println("Claude called " + toolUse.name() + " with " + toolUse._input());

      // Run the tool, then send the result back in a tool_result block.
      String weather = "15 degrees Celsius, partly cloudy";
      Message followup = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addTool(weatherTool)
          .toolChoice(toolChoice)
          .addUserMessage(userPrompt)
          .addMessage(response)
          .addUserMessageOfBlockParams(List.of(ContentBlockParam.ofToolResult(
              ToolResultBlockParam.builder()
                  .toolUseId(toolUse.id())
                  .content(weather)
                  .build())))
          .build());

      // Claude uses the result to answer the original question.
      followup.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  use Anthropic\Messages\ToolChoiceAuto;

  $client = new Client();

  $tools = [
      [
          'name' => 'get_weather',
          'description' => 'Get the current weather for a given location.',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'location' => [
                      'type' => 'string',
                      'description' => 'City and state, e.g. San Francisco, CA',
                  ],
              ],
              'required' => ['location'],
          ],
      ],
  ];
  $userMessage = ['role' => 'user', 'content' => "What's the weather in San Francisco?"];

  // Ask for at most one tool call per turn.
  $toolChoice = ToolChoiceAuto::with(disableParallelToolUse: true);

  // Claude replies with a tool_use block naming the tool and its arguments.
  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: $tools,
      toolChoice: $toolChoice,
      messages: [$userMessage],
  );
  $toolUse = null;
  foreach ($response->content as $block) {
      if ($block->type === 'tool_use') {
          $toolUse = $block;
          break;
      }
  }
  printf("Claude called %s with %s\n", $toolUse->name, json_encode($toolUse->input));

  // Run the tool, then send the result back in a tool_result block.
  $weather = '15 degrees Celsius, partly cloudy';
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
                      'content' => $weather,
                  ],
              ],
          ],
      ],
  );

  // Claude uses the result to answer the original question.
  foreach ($followup->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, "\n";
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  tools = [
    {
      name: "get_weather",
      description: "Get the current weather for a given location.",
      input_schema: {
        type: "object",
        properties: {
          location: {type: "string", description: "City and state, e.g. San Francisco, CA"}
        },
        required: ["location"]
      }
    }
  ]
  messages = [{role: "user", content: "What's the weather in San Francisco?"}]

  # Claude replies with a tool_use block naming the tool and its arguments.
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: tools,
    # Ask for at most one tool call per turn.
    tool_choice: {type: "auto", disable_parallel_tool_use: true},
    messages: messages
  )
  tool_use = response.content.find { |block| block.type == :tool_use }
  puts "Claude called #{tool_use.name} with #{JSON.generate(tool_use.input)}"

  # Run the tool, then send the result back in a tool_result block.
  weather = "15 degrees Celsius, partly cloudy"
  messages += [
    {role: "assistant", content: response.content},
    {
      role: "user",
      content: [
        {type: "tool_result", tool_use_id: tool_use.id, content: weather}
      ]
    }
  ]
  followup = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: tools,
    tool_choice: {type: "auto", disable_parallel_tool_use: true},
    messages: messages
  )

  # Claude uses the result to answer the original question.
  final_text = followup.content.find { |block| block.type == :text }
  puts final_text.text

text Output wrap
Claude called get_weather with {"location": "San Francisco, CA"}
The current weather in San Francisco is 15 degrees Celsius with partly cloudy skies.
```

[Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) covers each step in detail, including result formatting and error signaling; [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use) covers responses that call several tools at once. To skip writing this round trip yourself, use [Tool Runner](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner): the SDKs execute your tools and send the results back automatically.

For the full conceptual model including the agentic loop and when to choose each approach, see [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works).

To connect to Model Context Protocol (MCP) servers, see the [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector). To build your own MCP client, see the Model Context Protocol guide to [building an MCP client](https://modelcontextprotocol.io/docs/develop/build-client).


## When Claude uses tools

Source: https://platform.claude.com/llms-full.txt#when-claude-uses-tools

With the default `tool_choice` of `{"type": "auto"}`, Claude determines on each turn whether to call a tool or respond directly. It calls a tool when the request maps to that tool's described capability and the answer isn't already in context. It responds directly for stable knowledge, creative tasks, and conversational turns.

This boundary is steerable through your system prompt. If Claude isn't calling tools when you expect, a light instruction such as `"Use the tools to investigate before responding."` increases tool use. A stronger form such as `"Always call a tool first before responding."` pushes further. Conversely, `"Use your judgment about whether to call a tool or respond directly."` keeps triggering behavior conservative.

To require a tool call rather than rely on prompting, set [`tool_choice`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools#forcing-tool-use).

<Tip>
  **Guarantee schema conformance with strict tool use**

  Add `strict: true` to your custom tool definitions to ensure Claude's tool calls always match your schema exactly. See [Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use).
</Tip>

Each server tool's page describes its own trigger boundary in more detail.

<Accordion title="When required parameters are missing">
  If the user's prompt doesn't include enough information to fill all the required parameters for a tool, Claude Opus is much more likely to recognize that a parameter is missing and ask for it. Claude Sonnet might ask, especially when prompted to think before outputting a tool request. But it might also infer a reasonable value.

  For example, given a `get_weather` tool that requires a `location` parameter, if you ask Claude "What's the weather?" without specifying a location, Claude (particularly Claude Sonnet) might guess values you didn't supply:

  ```json JSON
  {
    "type": "tool_use",
    "id": "toolu_01A09q90qw90lq917835lq9",
    "name": "get_weather",
    "input": { "location": "New York, NY", "unit": "fahrenheit" }
  }
  ```

  This behavior is not guaranteed, especially for more ambiguous prompts and for less capable models.
</Accordion>


## Choose a tool

Source: https://platform.claude.com/llms-full.txt#choose-a-tool

For `type` strings, versions, and beta headers, see [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference).

### Your own tools

For tools you define, you write the schema and your application executes each call.

<CardGroup cols={2}>
  <Card title="Define tools" icon="hammer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools">
    Specify tool schemas, write descriptions, and control when Claude calls your tools.
  </Card>

  <Card title="Handle tool calls" icon="arrows-left-right" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls">
    Parse `tool_use` blocks, format `tool_result` responses, and handle errors.
  </Card>
</CardGroup>

### Anthropic-schema client tools

Anthropic publishes the schema and trains Claude on it. Your application still executes each call and returns the `tool_result`.

<CardGroup cols={2}>
  <Card title="Memory tool" icon="brain" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool">
    Store and retrieve information across conversations in files you control.
  </Card>

  <Card title="Bash tool" icon="terminal" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool">
    Run shell commands in a persistent session that maintains state.
  </Card>

  <Card title="Text editor tool" icon="edit" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool">
    View and modify text files to debug, fix, and improve code.
  </Card>

  <Card title="Computer use tool" icon="computer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool">
    Take screenshots and control the mouse and keyboard in a desktop environment.
  </Card>

  <Card title="Browser use tool" icon="browser" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool">
    Navigate, read, and interact with webpages in your own browser environment.
  </Card>
</CardGroup>

### Server tools

Server tools run on Anthropic's infrastructure, with no handler code in your application. See [Server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools) for the mechanics they share.

<CardGroup cols={2}>
  <Card title="Web search tool" icon="magnifying-glass" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool">
    Search the web for information beyond the knowledge cutoff, with cited sources.
  </Card>

  <Card title="Web fetch tool" icon="download" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool">
    Retrieve the full content of specified web pages and PDF documents.
  </Card>

  <Card title="Code execution tool" icon="code" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool">
    Run Python and bash code in a sandboxed container to analyze data and generate files.
  </Card>

  <Card title="Advisor tool" icon="lightbulb" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool">
    Let a faster executor model consult a higher-intelligence advisor model mid-generation.
  </Card>

  <Card title="Tool search tool" icon="library" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool">
    Work with thousands of tools by discovering and loading them on demand.
  </Card>

  <Card title="MCP connector" icon="link" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-connector">
    Connect to remote MCP servers from the Messages API without a separate MCP client.
  </Card>
</CardGroup>

<Note>
  [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) provides a built-in toolset that Claude uses autonomously within a session. For that toolset and the Managed Agents way to add custom tools, see its [Tools](https://platform.claude.com/docs/en/managed-agents/tools) page.
</Note>


## Pricing

Source: https://platform.claude.com/llms-full.txt#pricing-5

Tool use requests are priced based on:

1. The total number of input tokens sent to the model (including in the `tools` parameter)
2. The number of output tokens generated
3. For server-side tools, additional usage-based pricing (for example, web search charges per search performed)

Client-side tools are priced the same as any other Claude API request, although server-side tools can incur additional charges based on their specific usage.

The additional tokens from tool use come from:

* The `tools` parameter in API requests (tool names, descriptions, and schemas)
* `tool_use` content blocks in API requests and responses
* `tool_result` content blocks in API requests

When you use `tools`, the API also automatically includes a special system prompt for the model that enables tool use. The number of tool use tokens required for each model is listed in the following table (excluding the additional tokens listed earlier). Note that the table assumes at least 1 tool is provided. If no `tools` are provided, then a tool choice of `none` uses 0 additional system prompt tokens.

| Model                                                                                                                                 | Tool choice                    | Tool use system prompt token count |
| ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ | ---------------------------------- |
| Claude Opus 5                                                                                                                         | `auto`, `none`***`any`, `tool` | 286 tokens***406 tokens            |
| Claude Opus 4.8                                                                                                                       | `auto`, `none`***`any`, `tool` | 290 tokens***410 tokens            |
| Claude Opus 4.7                                                                                                                       | `auto`, `none`***`any`, `tool` | 675 tokens***804 tokens            |
| Claude Opus 4.6                                                                                                                       | `auto`, `none`***`any`, `tool` | 497 tokens***589 tokens            |
| Claude Opus 4.5                                                                                                                       | `auto`, `none`***`any`, `tool` | 496 tokens***588 tokens            |
| Claude Opus 4.1 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations))  | `auto`, `none`***`any`, `tool` | 313 tokens***315 tokens            |
| Claude Opus 4 ([retired, except on Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations))                | `auto`, `none`***`any`, `tool` | 313 tokens***315 tokens            |
| Claude Sonnet 5                                                                                                                       | `auto`, `none`***`any`, `tool` | 354 tokens***474 tokens            |
| Claude Sonnet 4.6                                                                                                                     | `auto`, `none`***`any`, `tool` | 497 tokens***589 tokens            |
| Claude Sonnet 4.5                                                                                                                     | `auto`, `none`***`any`, `tool` | 496 tokens***588 tokens            |
| Claude Sonnet 4 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations))  | `auto`, `none`***`any`, `tool` | 313 tokens***315 tokens            |
| Claude Haiku 4.5                                                                                                                      | `auto`, `none`***`any`, `tool` | 496 tokens***588 tokens            |
| Claude Haiku 3.5 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)) | `auto`, `none`***`any`, `tool` | 264 tokens***355 tokens            |

These token counts are added to your normal input and output tokens to calculate the total cost of a request.

See the [Models overview](https://platform.claude.com/docs/en/models/overview#latest-models-comparison) table for current per-model prices.

When you send a tool use prompt, like any other API request, the response includes both input and output token counts in the reported `usage` metrics.

Some server tools add usage-based charges on top of tokens: see [Web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool#usage-and-pricing) and [Code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#usage-and-pricing) for their rates.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-23

<CardGroup cols={3}>
  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works" title="How tool use works" icon="compass">
    Understand the tool use loop, where tools execute, and when to use tools instead of prose.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent" title="Tutorial: Build a tool-using agent" icon="graduation-cap">
    A guided walkthrough from a single tool call to a production-ready agentic loop.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference" title="Tool reference" icon="book">
    Directory of Anthropic-provided tools and reference for optional tool definition properties.
  </Card>
</CardGroup>


---
title: Advisor tool
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool
description: Pair a faster executor model with a higher-intelligence advisor model that provides strategic guidance mid-generation.
---

The advisor tool lets a faster, lower-cost **executor model** consult a higher-intelligence **advisor model** mid-generation for strategic guidance. The advisor reads the full conversation, produces a plan or course correction, and the executor continues with the task.

This pattern fits long-horizon agentic workloads (coding agents, computer use, multistep research pipelines) where most turns are mechanical but having an excellent plan is crucial. You get close to advisor-solo quality while the bulk of token generation happens at executor-model rates. For measured results, including how the benefit shrinks as the executor's own capability approaches the advisor's, see [Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence).

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>


## When to use it

Source: https://platform.claude.com/llms-full.txt#when-to-use-it

The advisor fits these configurations:

* **You currently use Sonnet on complex tasks:** Add a higher-tier advisor. Opus keeps total cost similar or lower; Claude Fable 5.1 maximizes the quality lift.
* **You currently use Haiku and want a step up in intelligence:** Add an Opus or Fable advisor. Expect higher cost than Haiku alone, but lower than switching the executor to a larger model.

Results are task-dependent. Evaluate on your own workload.

The advisor is a weaker fit for single-turn Q\&A (nothing to plan), pure pass-through model pickers where your users already choose their own cost and quality tradeoff, or workloads where every turn genuinely requires the advisor model's full capability.


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start

<Note>
  The advisor tool is in beta. Include the beta header `advisor-tool-2026-03-01` in your requests.
</Note>

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: advisor-tool-2026-03-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-sonnet-5",
      "max_tokens": 4096,
      "tools": [
        {
          "type": "advisor_20260301",
          "name": "advisor",
          "model": "claude-opus-5"
        }
      ],
      "messages": [{
        "role": "user",
        "content": "Build a concurrent worker pool in Go with graceful shutdown."
      }]
    }'

bash CLI
  ant beta:messages create --beta advisor-tool-2026-03-01 <<'YAML'
  model: claude-sonnet-5
  max_tokens: 4096
  tools:
    - type: advisor_20260301
      name: advisor
      model: claude-opus-5
  messages:
    - role: user
      content: Build a concurrent worker pool in Go with graceful shutdown.
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.beta.messages.create(
      model="claude-sonnet-5",
      max_tokens=4096,
      betas=["advisor-tool-2026-03-01"],
      tools=[
          {
              "type": "advisor_20260301",
              "name": "advisor",
              "model": "claude-opus-5",
          }
      ],
      messages=[
          {
              "role": "user",
              "content": "Build a concurrent worker pool in Go with graceful shutdown.",
          }
      ],
  )

  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.beta.messages.create({
    model: "claude-sonnet-5",
    max_tokens: 4096,
    betas: ["advisor-tool-2026-03-01"],
    tools: [
      {
        type: "advisor_20260301",
        name: "advisor",
        model: "claude-opus-5"
      }
    ],
    messages: [
      {
        role: "user",
        content: "Build a concurrent worker pool in Go with graceful shutdown."
      }
    ]
  });

  console.log(response);

csharp C#
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  var client = new AnthropicClient();

  var parameters = new MessageCreateParams
  {
      Model = Messages::Model.ClaudeSonnet5,
      MaxTokens = 4096,
      Tools = new BetaToolUnion[]
      {
          new BetaAdvisorTool20260301
          {
              Model = Messages::Model.ClaudeOpus5
          }
      },
      Messages =
      [
          new BetaMessageParam
          {
              Role = Role.User,
              Content = "Build a concurrent worker pool in Go with graceful shutdown."
          }
      ],
      Betas = ["advisor-tool-2026-03-01"]
  };

  var response = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeSonnet5,
  	MaxTokens: 4096,
  	Tools: []anthropic.BetaToolUnionParam{
  		{OfAdvisorTool20260301: &anthropic.BetaAdvisorTool20260301Param{
  			Model: anthropic.ModelClaudeOpus5,
  		}},
  	},
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Build a concurrent worker pool in Go with graceful shutdown.")),
  	},
  	Betas: []anthropic.AnthropicBeta{
  		anthropic.AnthropicBetaAdvisorTool2026_03_01,
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaAdvisorTool20260301;
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_SONNET_5)
          .maxTokens(4096L)
          .addTool(BetaAdvisorTool20260301.builder()
              .model(Model.CLAUDE_OPUS_5)
              .build())
          .addUserMessage("Build a concurrent worker pool in Go with graceful shutdown.")
          .addBeta("advisor-tool-2026-03-01")
          .build();

      BetaMessage response = client.beta().messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      maxTokens: 4096,
      messages: [
          [
              'role' => 'user',
              'content' => 'Build a concurrent worker pool in Go with graceful shutdown.',
          ],
      ],
      model: 'claude-sonnet-5',
      tools: [
          [
              'type' => 'advisor_20260301',
              'name' => 'advisor',
              'model' => 'claude-opus-5',
          ],
      ],
      betas: ['advisor-tool-2026-03-01'],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-sonnet-5",
    max_tokens: 4096,
    tools: [
      {
        type: "advisor_20260301",
        name: "advisor",
        model: "claude-opus-5"
      }
    ],
    messages: [
      {
        role: "user",
        content: "Build a concurrent worker pool in Go with graceful shutdown."
      }
    ],
    betas: ["advisor-tool-2026-03-01"]
  )

  puts response
  ```
</CodeGroup>

The response `content` includes an `advisor_tool_result` block carrying the advisor's guidance. With `claude-opus-5` as the advisor, as in this quick start, the block's `content` field is an `advisor_redacted_result` variant (encrypted; the executor reads it server-side, but your client does not). To see the advice text directly in your response, use `claude-opus-4-8` as the advisor model instead, which returns the plaintext `advisor_result` variant. See [Result variants](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#result-variants) for both shapes side by side and which advisor models return which, and [Model compatibility](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#model-compatibility) for the full list of valid pairs.


## How it works

Source: https://platform.claude.com/llms-full.txt#how-it-works-2

When you add the advisor tool to your `tools` array, the executor model determines when to call it, like any other tool. When the executor calls the advisor:

1. The executor emits a [`server_tool_use`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools) block with `name: "advisor"` and an empty `input`. The executor signals timing, and the server supplies context.
2. Anthropic runs a separate inference pass on the advisor model server-side. The advisor runs under its own Anthropic-supplied system prompt and receives the executor's full transcript as quoted context in its input. That transcript includes your system prompt, the tool definitions, the prior turns and tool results, and the text the executor has produced so far in this turn.
3. The advisor's response returns to the executor as an `advisor_tool_result` block.
4. The executor continues generating, informed by the advice.

All of this occurs inside a single `/v1/messages` request, with no extra round trips on your side. The exception is a turn that pauses mid-call, which you resume with a follow-up request (see [Resuming a paused turn](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#resuming-a-paused-turn)).

The advisor itself runs without tools and without context management. Its thinking blocks are dropped before the result returns. Only the advice text reaches the executor.


## Tool parameters

Source: https://platform.claude.com/llms-full.txt#tool-parameters

| Parameter    | Type           | Default                    | Description                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------ | -------------- | -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`       | string         | *required*                 | Must be `"advisor_20260301"`.                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `name`       | string         | *required*                 | Must be `"advisor"`.                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `model`      | string         | *required*                 | The advisor model ID, such as claude-opus-5. Billed at this model's rates for the sub-inference.                                                                                                                                                                                                                                                                                                                                                         |
| `max_uses`   | integer        | unlimited                  | Maximum number of advisor calls allowed in a single request. Once the executor reaches this cap, further advisor calls return an `advisor_tool_result_error` with `error_code: "max_uses_exceeded"` and the executor continues without further advice. This is a per-request cap, not a per-conversation cap. See [Cost control](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#cost-control) for conversation-level limits. |
| `max_tokens` | integer        | advisor model's output cap | Caps the advisor's total output (thinking plus text) per call. Minimum 1024. See [Capping advisor output](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#capping-advisor-output).                                                                                                                                                                                                                                            |
| `caching`    | object \| null | `null` (off)               | Enables [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) for the advisor's own transcript across calls within a conversation. See [Advisor prompt caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#advisor-prompt-caching).                                                                                                                                                     |

The `caching` object has the shape `{"type": "ephemeral", "ttl": "5m" | "1h"}`. Unlike `cache_control` on content blocks, this is not a breakpoint marker. It is an on/off switch. The server determines where cache boundaries go.

The advisor tool also accepts the generic properties available on any tool definition: `cache_control`, `allowed_callers`, `defer_loading`, and `strict` (covered in [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)). See the [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#tool-definition-properties) for their semantics.


## Response structure

Source: https://platform.claude.com/llms-full.txt#response-structure-2

### Successful advisor call

When the advisor is called, a `server_tool_use` block is followed by an `advisor_tool_result` block in the assistant's content. The following example shows the plaintext `advisor_result` variant returned by a Claude Opus 4.8 advisor. The [Quick start](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#quick-start) uses Claude Opus 5, which returns the encrypted `advisor_redacted_result` variant instead; see [Result variants](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#result-variants) for both shapes side by side.

The `server_tool_use.input` is always empty. The server constructs the advisor's view from the full transcript automatically. Nothing the executor puts in `input` reaches the advisor.

### Result variants

The `advisor_tool_result.content` field is a discriminated union. For successful calls, the variant depends on the advisor model:

| Variant                   | Fields                             | Returned when                                                       |
| ------------------------- | ---------------------------------- | ------------------------------------------------------------------- |
| `advisor_result`          | `text`, `stop_reason`              | The advisor model returns plaintext (for example, Claude Opus 4.8). |
| `advisor_redacted_result` | `encrypted_content`, `stop_reason` | The advisor model returns encrypted output.                         |

<Note>
  Claude Fable 5.1, Claude Mythos 5.1, Claude Opus 5, Claude Fable 5, and Claude Mythos 5 advisors return the encrypted `advisor_redacted_result`. Every other advisor model in the [compatibility table](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#model-compatibility) returns the plaintext `advisor_result`. To read the advice text in your own responses, use an advisor that returns plaintext, such as `claude-opus-4-8`, where your executor's row in the [compatibility table](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#model-compatibility) lists one. Claude Fable 5.1, Claude Mythos 5.1, Claude Opus 5, Claude Fable 5, and Claude Mythos 5 executors pair only with advisors that return the encrypted form, so on those executors the advice text isn't readable in the response.
</Note>

Here is the same request sent twice, identical except for the advisor `model` in the tool definition, showing both variants.

With `"model": "claude-opus-4-8"`, the advice is plaintext:

With `"model": "claude-opus-5"`, the advice is encrypted:

Both result variants carry a `stop_reason` field when you set [`max_tokens`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#capping-advisor-output) on the tool definition, and omit it when you do not. It holds the advisor sub-call's stop reason, typically `"end_turn"`, or `"max_tokens"` when the cap is hit. The values match the top-level Messages API [`stop_reason`](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons).

With `advisor_result`, the `text` field contains human-readable advice. With `advisor_redacted_result`, the `encrypted_content` field contains an opaque blob that you cannot read. On the next turn, the server decrypts it and renders the plaintext into the executor's prompt.

In both cases, round-trip the content verbatim on subsequent turns. If you switch advisor models mid-conversation, branch on `content.type` to handle both shapes.

### Error results

If the advisor call fails, the result carries an error:

The executor sees the error and continues without further advice. The request itself does not fail.

| `error_code`              | Meaning                                                                                                                         |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `max_uses_exceeded`       | The request reached the `max_uses` cap set on the tool definition. Further advisor calls in the same request return this error. |
| `too_many_requests`       | The advisor sub-inference was rate-limited.                                                                                     |
| `overloaded`              | The advisor sub-inference hit capacity limits.                                                                                  |
| `prompt_too_long`         | The transcript exceeded the advisor model's context window.                                                                     |
| `execution_time_exceeded` | The advisor sub-inference timed out.                                                                                            |
| `model_not_found`         | The configured advisor model is not available.                                                                                  |
| `unavailable`             | Any other advisor failure.                                                                                                      |

Advisor rate limits draw from the same per-model bucket as direct calls to the advisor model. A rate limit on the advisor appears as `too_many_requests` inside the tool result. A rate limit on the executor fails the whole request with HTTP 429.


## Multi-turn conversations

Source: https://platform.claude.com/llms-full.txt#multi-turn-conversations

Pass the full assistant content, including `advisor_tool_result` blocks, back to the API on subsequent turns. Round-trip the result blocks verbatim: with a Claude Opus 5 advisor the result block's `content` is the encrypted `advisor_redacted_result` variant, and the server decrypts it and renders the advice into the executor's prompt on the next turn (see [Result variants](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#result-variants)). The mechanics are identical for any advisor model.

<CodeGroup exclude="shell">
  ```python Python
  client = anthropic.Anthropic()

  tools = [
      {
          "type": "advisor_20260301",
          "name": "advisor",
          "model": "claude-opus-5",
      }
  ]

  messages = [
      {
          "role": "user",
          "content": "Build a concurrent worker pool in Go with graceful shutdown.",
      }
  ]

  response = client.beta.messages.create(
      model="claude-sonnet-5",
      max_tokens=1024,
      betas=["advisor-tool-2026-03-01"],
      tools=tools,
      messages=messages,
  )

  # Append the full response content, including any advisor_tool_result blocks
  messages.append({"role": "assistant", "content": response.content})

  # Continue the conversation
  messages.append({"role": "user", "content": "Now add a max-in-flight limit of 10."})

  response = client.beta.messages.create(
      model="claude-sonnet-5",
      max_tokens=1024,
      betas=["advisor-tool-2026-03-01"],
      tools=tools,
      messages=messages,
  )

typescript TypeScript
  const client = new Anthropic();

  const tools: Anthropic.Beta.Messages.BetaToolUnion[] = [
    {
      type: "advisor_20260301",
      name: "advisor",
      model: "claude-opus-5"
    }
  ];

  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [
    {
      role: "user",
      content: "Build a concurrent worker pool in Go with graceful shutdown."
    }
  ];

  const response = await client.beta.messages.create({
    model: "claude-sonnet-5",
    max_tokens: 1024,
    betas: ["advisor-tool-2026-03-01"],
    tools,
    messages
  });

  // Append the full response content, including any advisor_tool_result blocks
  messages.push({ role: "assistant", content: response.content });

  // Continue the conversation
  messages.push({ role: "user", content: "Now add a max-in-flight limit of 10." });

  const followUp = await client.beta.messages.create({
    model: "claude-sonnet-5",
    max_tokens: 1024,
    betas: ["advisor-tool-2026-03-01"],
    tools,
    messages
  });

csharp C#
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  var client = new AnthropicClient();

  var tools = new BetaToolUnion[]
  {
      new BetaAdvisorTool20260301 { Model = Messages::Model.ClaudeOpus5 }
  };

  var messages = new List<BetaMessageParam>
  {
      new() { Role = Role.User, Content = "Build a concurrent worker pool in Go with graceful shutdown." }
  };

  var response = await client.Beta.Messages.Create(new MessageCreateParams
  {
      Model = Messages::Model.ClaudeSonnet5,
      MaxTokens = 1024,
      Tools = tools,
      Messages = messages,
      Betas = ["advisor-tool-2026-03-01"]
  });

  // Append the full response content, including any advisor_tool_result blocks
  messages.Add(new BetaMessageParam
  {
      Role = Role.Assistant,
      Content = response.Content.Select(block => new BetaContentBlockParam(block.Json)).ToList()
  });

  // Continue the conversation
  messages.Add(new BetaMessageParam { Role = Role.User, Content = "Now add a max-in-flight limit of 10." });

  var followUp = await client.Beta.Messages.Create(new MessageCreateParams
  {
      Model = Messages::Model.ClaudeSonnet5,
      MaxTokens = 1024,
      Tools = tools,
      Messages = messages,
      Betas = ["advisor-tool-2026-03-01"]
  });

go Go
  client := anthropic.NewClient()

  tools := []anthropic.BetaToolUnionParam{
  	{OfAdvisorTool20260301: &anthropic.BetaAdvisorTool20260301Param{
  		Model: anthropic.ModelClaudeOpus5,
  	}},
  }

  messages := []anthropic.BetaMessageParam{
  	anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Build a concurrent worker pool in Go with graceful shutdown.")),
  }

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeSonnet5,
  	MaxTokens: 1024,
  	Tools:     tools,
  	Messages:  messages,
  	Betas: []anthropic.AnthropicBeta{
  		anthropic.AnthropicBetaAdvisorTool2026_03_01,
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  // Append the full response content, including any advisor_tool_result blocks.
  // BetaMessage.ToParam drops advisor result content as of anthropic-sdk-go
  // v1.61.0, so re-parse each response block's raw JSON into a param block instead.
  assistantContent := make([]anthropic.BetaContentBlockParamUnion, len(response.Content))
  for i, block := range response.Content {
  	if err := json.Unmarshal([]byte(block.RawJSON()), &assistantContent[i]); err != nil {
  		log.Fatal(err)
  	}
  }
  messages = append(messages, anthropic.BetaMessageParam{
  	Role:    anthropic.BetaMessageParamRoleAssistant,
  	Content: assistantContent,
  })

  // Continue the conversation
  messages = append(messages, anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Now add a max-in-flight limit of 10.")))

  response, err = client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeSonnet5,
  	MaxTokens: 1024,
  	Tools:     tools,
  	Messages:  messages,
  	Betas: []anthropic.AnthropicBeta{
  		anthropic.AnthropicBetaAdvisorTool2026_03_01,
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

java Java
  import com.anthropic.models.beta.messages.BetaAdvisorTool20260301;
  import com.anthropic.models.beta.messages.BetaContentBlock;
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.BetaMessageParam;
  import com.anthropic.models.beta.messages.BetaToolUnion;
  import com.anthropic.models.beta.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      List<BetaToolUnion> tools = List.of(
          BetaToolUnion.ofAdvisorTool20260301(
              BetaAdvisorTool20260301.builder().model(Model.CLAUDE_OPUS_5).build()));

      List<BetaMessageParam> messages = new ArrayList<>();
      messages.add(BetaMessageParam.builder()
          .role(BetaMessageParam.Role.USER)
          .content("Build a concurrent worker pool in Go with graceful shutdown.")
          .build());

      BetaMessage response = client.beta().messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_SONNET_5)
          .maxTokens(1024L)
          .tools(tools)
          .messages(messages)
          .addBeta("advisor-tool-2026-03-01")
          .build());

      // Append the full response content, including any advisor_tool_result blocks
      messages.add(BetaMessageParam.builder()
          .role(BetaMessageParam.Role.ASSISTANT)
          .contentOfBetaContentBlockParams(
              response.content().stream().map(BetaContentBlock::toParam).toList())
          .build());

      // Continue the conversation
      messages.add(BetaMessageParam.builder()
          .role(BetaMessageParam.Role.USER)
          .content("Now add a max-in-flight limit of 10.")
          .build());

      BetaMessage followUp = client.beta().messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_SONNET_5)
          .maxTokens(1024L)
          .tools(tools)
          .messages(messages)
          .addBeta("advisor-tool-2026-03-01")
          .build());
  }

php PHP
  $client = new Client();

  $tools = [
      [
          'type' => 'advisor_20260301',
          'name' => 'advisor',
          'model' => 'claude-opus-5',
      ],
  ];

  $messages = [
      [
          'role' => 'user',
          'content' => 'Build a concurrent worker pool in Go with graceful shutdown.',
      ],
  ];

  $response = $client->beta->messages->create(
      maxTokens: 1024,
      messages: $messages,
      model: 'claude-sonnet-5',
      tools: $tools,
      betas: ['advisor-tool-2026-03-01'],
  );

  // Append the full response content, including any advisor_tool_result blocks
  $messages[] = ['role' => 'assistant', 'content' => $response->content];

  // Continue the conversation
  $messages[] = ['role' => 'user', 'content' => 'Now add a max-in-flight limit of 10.'];

  $response = $client->beta->messages->create(
      maxTokens: 1024,
      messages: $messages,
      model: 'claude-sonnet-5',
      tools: $tools,
      betas: ['advisor-tool-2026-03-01'],
  );

ruby Ruby
  client = Anthropic::Client.new

  tools = [
    {
      type: "advisor_20260301",
      name: "advisor",
      model: "claude-opus-5"
    }
  ]

  messages = [
    {
      role: "user",
      content: "Build a concurrent worker pool in Go with graceful shutdown."
    }
  ]

  response = client.beta.messages.create(
    model: "claude-sonnet-5",
    max_tokens: 1024,
    tools: tools,
    messages: messages,
    betas: ["advisor-tool-2026-03-01"]
  )

  # Append the full response content, including any advisor_tool_result blocks
  messages << { role: "assistant", content: response.content }

  # Continue the conversation
  messages << { role: "user", content: "Now add a max-in-flight limit of 10." }

  response = client.beta.messages.create(
    model: "claude-sonnet-5",
    max_tokens: 1024,
    tools: tools,
    messages: messages,
    betas: ["advisor-tool-2026-03-01"]
  )

python Python
  client = anthropic.Anthropic()

  NUDGE_TURN = 2  # inject before this assistant turn if no advisor call yet
  NUDGE_TEXT = (
      "You have not consulted the advisor yet. If the task has a non-obvious "
      "design decision or a failure mode you haven't ruled out, call advisor "
      "now before committing to an approach."
  )
  MAX_TURNS = 10  # agent loop cap


  def run_your_tools(content):
      # Replace with your tool dispatch. Returns one tool_result block per tool_use block.
      return [
          {
              "type": "tool_result",
              "tool_use_id": block.id,
              "content": "Replace with your tool output.",
          }
          for block in content
          if block.type == "tool_use"
      ]


  tools = [
      {"type": "advisor_20260301", "name": "advisor", "model": "claude-opus-5"},
      # ... your other tools
  ]
  task = "Build a concurrent worker pool in Go with graceful shutdown."
  messages = [{"role": "user", "content": task}]
  advisor_called = False

  for turn in range(1, MAX_TURNS + 1):
      response = client.beta.messages.create(
          model="claude-haiku-4-5",
          max_tokens=4096,
          betas=["advisor-tool-2026-03-01"],
          tools=tools,
          messages=messages,
      )
      messages.append({"role": "assistant", "content": response.content})
      advisor_called = advisor_called or any(
          block.type == "server_tool_use" and block.name == "advisor"
          for block in response.content
      )
      if response.stop_reason == "end_turn":
          break
      if response.stop_reason == "pause_turn":
          continue  # server tool pending; re-send to let the API complete it

      results = run_your_tools(response.content)  # list of tool_result blocks
      if results:
          messages.append({"role": "user", "content": results})
      # Skip this if your system prompt already tells the model to call sparingly.
      if turn == NUDGE_TURN - 1 and not advisor_called:
          messages.append({"role": "user", "content": NUDGE_TEXT})

typescript TypeScript
  const client = new Anthropic();

  const NUDGE_TURN = 2; // inject before this assistant turn if no advisor call yet
  const NUDGE_TEXT =
    "You have not consulted the advisor yet. If the task has a non-obvious " +
    "design decision or a failure mode you haven't ruled out, call advisor " +
    "now before committing to an approach.";
  const MAX_TURNS = 10; // agent loop cap

  function runYourTools(
    content: Anthropic.Beta.Messages.BetaContentBlock[]
  ): Anthropic.Beta.Messages.BetaToolResultBlockParam[] {
    // Replace with your tool dispatch. Returns one tool_result block per tool_use block.
    return content
      .filter((block) => block.type === "tool_use")
      .map((block) => ({
        type: "tool_result" as const,
        tool_use_id: block.id,
        content: "Replace with your tool output."
      }));
  }

  const tools: Anthropic.Beta.Messages.BetaToolUnion[] = [
    { type: "advisor_20260301", name: "advisor", model: "claude-opus-5" }
    // ... your other tools
  ];
  const task = "Build a concurrent worker pool in Go with graceful shutdown.";
  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [{ role: "user", content: task }];
  let advisorCalled = false;

  for (let turn = 1; turn <= MAX_TURNS; turn++) {
    const response = await client.beta.messages.create({
      model: "claude-haiku-4-5",
      max_tokens: 4096,
      betas: ["advisor-tool-2026-03-01"],
      tools,
      messages
    });
    messages.push({ role: "assistant", content: response.content });
    advisorCalled =
      advisorCalled ||
      response.content.some(
        (block) => block.type === "server_tool_use" && block.name === "advisor"
      );
    if (response.stop_reason === "end_turn") {
      break;
    }
    if (response.stop_reason === "pause_turn") {
      continue; // server tool pending; re-send to let the API complete it
    }

    const results = runYourTools(response.content); // list of tool_result blocks
    if (results.length > 0) {
      messages.push({ role: "user", content: results });
    }
    // Skip this if your system prompt already tells the model to call sparingly.
    if (turn === NUDGE_TURN - 1 && !advisorCalled) {
      messages.push({ role: "user", content: NUDGE_TEXT });
    }
  }

csharp C#
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  var client = new AnthropicClient();

  const int NudgeTurn = 2; // inject before this assistant turn if no advisor call yet
  const string NudgeText =
      "You have not consulted the advisor yet. If the task has a non-obvious "
      + "design decision or a failure mode you haven't ruled out, call advisor "
      + "now before committing to an approach.";
  const int MaxTurns = 10; // agent loop cap

  // Replace with your tool dispatch. Returns one tool_result block per tool_use block.
  List<BetaContentBlockParam> RunYourTools(IReadOnlyList<BetaContentBlock> content)
  {
      List<BetaContentBlockParam> results = [];
      foreach (var block in content)
      {
          if (block.TryPickToolUse(out var toolUse))
          {
              results.Add(new BetaToolResultBlockParam
              {
                  ToolUseID = toolUse.ID,
                  Content = "Replace with your tool output."
              });
          }
      }
      return results;
  }

  var tools = new BetaToolUnion[]
  {
      new BetaAdvisorTool20260301 { Model = Messages::Model.ClaudeOpus5 }
      // ... your other tools
  };
  var task = "Build a concurrent worker pool in Go with graceful shutdown.";
  var messages = new List<BetaMessageParam> { new() { Role = Role.User, Content = task } };
  var advisorCalled = false;

  for (var turn = 1; turn <= MaxTurns; turn++)
  {
      var response = await client.Beta.Messages.Create(new MessageCreateParams
      {
          Model = Messages::Model.ClaudeHaiku4_5,
          MaxTokens = 4096,
          Tools = tools,
          Messages = messages,
          Betas = ["advisor-tool-2026-03-01"]
      });
      messages.Add(new BetaMessageParam
      {
          Role = Role.Assistant,
          Content = response.Content.Select(block => new BetaContentBlockParam(block.Json)).ToList()
      });
      advisorCalled =
          advisorCalled
          || response.Content.Any(block =>
              block.TryPickServerToolUse(out var serverToolUse)
              && serverToolUse.Name.Value() == Name.Advisor
          );
      if (response.StopReason == BetaStopReason.EndTurn)
      {
          break;
      }
      if (response.StopReason == BetaStopReason.PauseTurn)
      {
          continue; // server tool pending; re-send to let the API complete it
      }

      var results = RunYourTools(response.Content); // list of tool_result blocks
      if (results.Count > 0)
      {
          messages.Add(new BetaMessageParam { Role = Role.User, Content = results });
      }
      // Skip this if your system prompt already tells the model to call sparingly.
      if (turn == NudgeTurn - 1 && !advisorCalled)
      {
          messages.Add(new BetaMessageParam { Role = Role.User, Content = NudgeText });
      }
  }

go Go
  const (
  	nudgeTurn = 2 // inject before this assistant turn if no advisor call yet
  	nudgeText = "You have not consulted the advisor yet. If the task has a non-obvious " +
  		"design decision or a failure mode you haven't ruled out, call advisor " +
  		"now before committing to an approach."
  	maxTurns = 10 // agent loop cap
  )

  // Replace with your tool dispatch. Returns one tool_result block per tool_use block.
  func runYourTools(content []anthropic.BetaContentBlockUnion) []anthropic.BetaContentBlockParamUnion {
  	var results []anthropic.BetaContentBlockParamUnion
  	for _, block := range content {
  		if block.Type == "tool_use" {
  			results = append(results, anthropic.NewBetaToolResultBlock(block.ID, "Replace with your tool output.", false))
  		}
  	}
  	return results
  }

  func main() {
  	client := anthropic.NewClient()

  	tools := []anthropic.BetaToolUnionParam{
  		{OfAdvisorTool20260301: &anthropic.BetaAdvisorTool20260301Param{
  			Model: anthropic.ModelClaudeOpus5,
  		}},
  		// ... your other tools
  	}
  	task := "Build a concurrent worker pool in Go with graceful shutdown."
  	messages := []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock(task)),
  	}
  	advisorCalled := false

  	for turn := 1; turn <= maxTurns; turn++ {
  		response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  			Model:     anthropic.ModelClaudeHaiku4_5,
  			MaxTokens: 4096,
  			Tools:     tools,
  			Messages:  messages,
  			Betas: []anthropic.AnthropicBeta{
  				anthropic.AnthropicBetaAdvisorTool2026_03_01,
  			},
  		})
  		if err != nil {
  			log.Fatal(err)
  		}

  		// Append the full response content, including any advisor_tool_result blocks.
  		// BetaMessage.ToParam drops advisor result content as of anthropic-sdk-go
  		// v1.61.0, so re-parse each response block's raw JSON into a param block instead.
  		assistantContent := make([]anthropic.BetaContentBlockParamUnion, len(response.Content))
  		for i, block := range response.Content {
  			if err := json.Unmarshal([]byte(block.RawJSON()), &assistantContent[i]); err != nil {
  				log.Fatal(err)
  			}
  		}
  		messages = append(messages, anthropic.BetaMessageParam{
  			Role:    anthropic.BetaMessageParamRoleAssistant,
  			Content: assistantContent,
  		})

  		for _, block := range response.Content {
  			if block.Type == "server_tool_use" && block.Name == "advisor" {
  				advisorCalled = true
  			}
  		}
  		if response.StopReason == anthropic.BetaStopReasonEndTurn {
  			break
  		}
  		if response.StopReason == anthropic.BetaStopReasonPauseTurn {
  			continue // server tool pending; re-send to let the API complete it
  		}

  		results := runYourTools(response.Content) // list of tool_result blocks
  		if len(results) > 0 {
  			messages = append(messages, anthropic.BetaMessageParam{
  				Role:    anthropic.BetaMessageParamRoleUser,
  				Content: results,
  			})
  		}
  		// Skip this if your system prompt already tells the model to call sparingly.
  		if turn == nudgeTurn-1 && !advisorCalled {
  			messages = append(messages, anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock(nudgeText)))
  		}
  	}
  }

java Java
  import com.anthropic.models.beta.messages.BetaAdvisorTool20260301;
  import com.anthropic.models.beta.messages.BetaContentBlock;
  import com.anthropic.models.beta.messages.BetaContentBlockParam;
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.BetaMessageParam;
  import com.anthropic.models.beta.messages.BetaServerToolUseBlock;
  import com.anthropic.models.beta.messages.BetaStopReason;
  import com.anthropic.models.beta.messages.BetaToolResultBlockParam;
  import com.anthropic.models.beta.messages.BetaToolUnion;
  import com.anthropic.models.beta.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;

  static final int NUDGE_TURN = 2; // inject before this assistant turn if no advisor call yet
  static final String NUDGE_TEXT =
      "You have not consulted the advisor yet. If the task has a non-obvious "
          + "design decision or a failure mode you haven't ruled out, call advisor "
          + "now before committing to an approach.";
  static final int MAX_TURNS = 10; // agent loop cap

  // Replace with your tool dispatch. Returns one tool_result block per tool_use block.
  List<BetaContentBlockParam> runYourTools(List<BetaContentBlock> content) {
      List<BetaContentBlockParam> results = new ArrayList<>();
      for (BetaContentBlock block : content) {
          if (block.isToolUse()) {
              results.add(BetaContentBlockParam.ofToolResult(
                  BetaToolResultBlockParam.builder()
                      .toolUseId(block.asToolUse().id())
                      .content("Replace with your tool output.")
                      .build()));
          }
      }
      return results;
  }

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      List<BetaToolUnion> tools = List.of(
          BetaToolUnion.ofAdvisorTool20260301(
              BetaAdvisorTool20260301.builder().model(Model.CLAUDE_OPUS_5).build())
          // ... your other tools
      );
      String task = "Build a concurrent worker pool in Go with graceful shutdown.";
      List<BetaMessageParam> messages = new ArrayList<>();
      messages.add(BetaMessageParam.builder()
          .role(BetaMessageParam.Role.USER)
          .content(task)
          .build());
      boolean advisorCalled = false;

      for (int turn = 1; turn <= MAX_TURNS; turn++) {
          BetaMessage response = client.beta().messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_HAIKU_4_5)
              .maxTokens(4096L)
              .tools(tools)
              .messages(messages)
              .addBeta("advisor-tool-2026-03-01")
              .build());
          messages.add(BetaMessageParam.builder()
              .role(BetaMessageParam.Role.ASSISTANT)
              .contentOfBetaContentBlockParams(
                  response.content().stream().map(BetaContentBlock::toParam).toList())
              .build());
          advisorCalled = advisorCalled
              || response.content().stream().anyMatch(block ->
                  block.isServerToolUse()
                      && block.asServerToolUse().name().equals(BetaServerToolUseBlock.Name.ADVISOR));
          BetaStopReason stopReason = response.stopReason().orElse(null);
          if (BetaStopReason.END_TURN.equals(stopReason)) {
              break;
          }
          if (BetaStopReason.PAUSE_TURN.equals(stopReason)) {
              continue; // server tool pending; re-send to let the API complete it
          }

          List<BetaContentBlockParam> results = runYourTools(response.content()); // list of tool_result blocks
          if (!results.isEmpty()) {
              messages.add(BetaMessageParam.builder()
                  .role(BetaMessageParam.Role.USER)
                  .contentOfBetaContentBlockParams(results)
                  .build());
          }
          // Skip this if your system prompt already tells the model to call sparingly.
          if (turn == NUDGE_TURN - 1 && !advisorCalled) {
              messages.add(BetaMessageParam.builder()
                  .role(BetaMessageParam.Role.USER)
                  .content(NUDGE_TEXT)
                  .build());
          }
      }
  }

php PHP
  $client = new Client();

  const NUDGE_TURN = 2; // inject before this assistant turn if no advisor call yet
  const NUDGE_TEXT = "You have not consulted the advisor yet. If the task has a non-obvious "
      . "design decision or a failure mode you haven't ruled out, call advisor "
      . "now before committing to an approach.";
  const MAX_TURNS = 10; // agent loop cap

  // Replace with your tool dispatch. Returns one tool_result block per tool_use block.
  function runYourTools(array $content): array
  {
      $results = [];
      foreach ($content as $block) {
          if ($block->type === 'tool_use') {
              $results[] = [
                  'type' => 'tool_result',
                  'tool_use_id' => $block->id,
                  'content' => 'Replace with your tool output.',
              ];
          }
      }
      return $results;
  }

  $tools = [
      ['type' => 'advisor_20260301', 'name' => 'advisor', 'model' => 'claude-opus-5'],
      // ... your other tools
  ];
  $task = 'Build a concurrent worker pool in Go with graceful shutdown.';
  $messages = [['role' => 'user', 'content' => $task]];
  $advisorCalled = false;

  for ($turn = 1; $turn <= MAX_TURNS; $turn++) {
      $response = $client->beta->messages->create(
          maxTokens: 4096,
          messages: $messages,
          model: 'claude-haiku-4-5',
          tools: $tools,
          betas: ['advisor-tool-2026-03-01'],
      );
      $messages[] = ['role' => 'assistant', 'content' => $response->content];
      foreach ($response->content as $block) {
          if ($block->type === 'server_tool_use' && $block->name === 'advisor') {
              $advisorCalled = true;
          }
      }
      if ($response->stopReason === 'end_turn') {
          break;
      }
      if ($response->stopReason === 'pause_turn') {
          continue; // server tool pending; re-send to let the API complete it
      }

      $results = runYourTools($response->content); // list of tool_result blocks
      if ($results !== []) {
          $messages[] = ['role' => 'user', 'content' => $results];
      }
      // Skip this if your system prompt already tells the model to call sparingly.
      if ($turn === NUDGE_TURN - 1 && !$advisorCalled) {
          $messages[] = ['role' => 'user', 'content' => NUDGE_TEXT];
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  NUDGE_TURN = 2 # inject before this assistant turn if no advisor call yet
  NUDGE_TEXT =
    "You have not consulted the advisor yet. If the task has a non-obvious " \
    "design decision or a failure mode you haven't ruled out, call advisor " \
    "now before committing to an approach."
  MAX_TURNS = 10 # agent loop cap

  # Replace with your tool dispatch. Returns one tool_result block per tool_use block.
  def run_your_tools(content)
    content.filter_map do |block|
      next unless block.type == :tool_use
      { type: "tool_result", tool_use_id: block.id, content: "Replace with your tool output." }
    end
  end

  tools = [
    { type: "advisor_20260301", name: "advisor", model: "claude-opus-5" }
    # ... your other tools
  ]
  task = "Build a concurrent worker pool in Go with graceful shutdown."
  messages = [{ role: "user", content: task }]
  advisor_called = false

  (1..MAX_TURNS).each do |turn|
    response = client.beta.messages.create(
      model: "claude-haiku-4-5",
      max_tokens: 4096,
      tools: tools,
      messages: messages,
      betas: ["advisor-tool-2026-03-01"]
    )
    messages << { role: "assistant", content: response.content }
    advisor_called ||= response.content.any? do |block|
      block.type == :server_tool_use && block.name == :advisor
    end
    break if response.stop_reason == :end_turn
    next if response.stop_reason == :pause_turn # server tool pending; re-send to let the API complete it

    results = run_your_tools(response.content) # list of tool_result blocks
    messages << { role: "user", content: results } unless results.empty?
    # Skip this if your system prompt already tells the model to call sparingly.
    messages << { role: "user", content: NUDGE_TEXT } if turn == NUDGE_TURN - 1 && !advisor_called
  end
  ```
</CodeGroup>

Append the nudge as its own user message after the tool results rather than as a sibling block in the same message. Consecutive user messages are valid. In Anthropic's testing on Haiku and Sonnet executors they behaved equivalently to a sibling block. The separate-message shape also keeps the reminder clearly distinct from tool output.

**Trade-offs:** The nudge raises the call rate, which can push trivially simple tasks into an unnecessary consult. If your workload mixes simple and complex tasks, consider raising `NUDGE_TURN` to 3 so two-turn tasks complete before the nudge fires, or gate the nudge on a task-complexity signal you already compute. If your system prompt already contains restraint language ("reserve the advisor for genuine uncertainty"), skip the nudge entirely, because the two instructions conflict.

The plain-text nudge is highly salient on Haiku and Sonnet executors: 74 percent (Sonnet) to 98 percent (Haiku) of nudged attempts in Anthropic's testing called the advisor immediately at turn 2. If that lands before your executor has read the problem or gathered context, the resulting advisor call is low-context and can displace a better-timed later call. Measure your executor's baseline first-call turn before adding the nudge. If the executor already calls the advisor reliably and its first call typically lands at turn N, set `NUDGE_TURN` greater than N. In Anthropic's testing, a turn-2 nudge on workloads where the baseline first call was turn 7 or later correlated with a 3 to 4 percentage-point task-performance drop. On a browse workload where the baseline call rate was 86 percent, the same nudge raised engagement with no task-performance cost.

To force a consult on a specific request instead of nudging, set `tool_choice` to `{"type": "tool", "name": "advisor"}`, subject to the constraints in [Forcing tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools#forcing-tool-use). Forcing tool use cannot be combined with manual extended thinking (`thinking: {type: "enabled"}`): the API returns a `400 invalid_request_error` if you enable both. Adaptive thinking supports forced tool use. Claude Fable 5.1 and Claude Mythos 5.1 executors reject `tool_choice` types `tool` and `any`, so use the prompt nudge on those models instead.


## Streaming

Source: https://platform.claude.com/llms-full.txt#streaming

The advisor sub-inference does not stream. The executor's stream pauses while the advisor runs; then the full result arrives in a single event.

The `server_tool_use` block with `name: "advisor"` signals that an advisor call is starting. The pause begins when that block closes (`content_block_stop`). During the pause, the stream is quiet except for standard SSE `ping` keepalives emitted roughly every 30 seconds. Short advisor calls might show no pings.

When the advisor finishes, the `advisor_tool_result` arrives fully formed in a single `content_block_start` event (no deltas). Executor output then resumes streaming.

A `message_delta` event follows with the updated `usage.iterations` array reflecting the advisor's token counts.


## Usage and billing

Source: https://platform.claude.com/llms-full.txt#usage-and-billing

Advisor calls run as a separate sub-inference billed at the advisor model's rates. Usage is reported in the `usage.iterations[]` array:

Top-level `usage` fields reflect executor tokens only. Advisor tokens are not rolled into the top-level totals because they are billed at a different rate. Iterations with `type: "advisor_message"` are billed at the advisor model's rates, and iterations with `type: "message"` are billed at the executor model's rates.

Every top-level `usage` field is the sum of that field across all executor iterations, including `input_tokens`, `output_tokens`, and `cache_read_input_tokens`. Because each executor iteration re-sends the growing conversation, later iterations' inputs include earlier iterations' output, so summed `input_tokens` exceeds the size of any single prompt. Use `usage.iterations` for a full per-iteration breakdown when building cost-tracking logic.

Advisor output is typically 400 to 700 text tokens, or 1,400 to 1,800 tokens total including thinking. The cost savings come from the advisor not generating your full final output. The executor does that at its lower rate.

The top-level `max_tokens` applies to executor output only. It does not bound advisor sub-inference tokens. To cap advisor output directly, set [`max_tokens` on the tool definition](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#capping-advisor-output). The advisor's tokens also do not draw from any [task budget](https://platform.claude.com/docs/en/build-with-claude/task-budgets) applied to the executor.

[Priority Tier](https://platform.claude.com/docs/en/api/service-tiers) applies to each model independently. A Priority Tier commitment on the executor model does not extend to the advisor. Advisor calls run at Priority Tier only if your organization also holds a commitment on the advisor model.
