# platform.claude.com Documentation (Part 5 of 35)

## Advisor prompt caching

Source: https://platform.claude.com/llms-full.txt#advisor-prompt-caching

There are two independent caching layers.

### Executor-side caching

The `advisor_tool_result` block is cacheable like any other content block. A `cache_control` breakpoint placed after it on a subsequent turn hits. The executor's prompt always contains the plaintext advice regardless of whether your client received `text` or `encrypted_content`, so caching behavior is identical for both result variants.

### Advisor-side caching

Set `caching` on the tool definition to enable prompt caching for the advisor's own transcript across calls within the same conversation:

<CodeGroup exclude="shell">
  ```python Python
  tools = [
      {
          "type": "advisor_20260301",
          "name": "advisor",
          "model": "claude-opus-5",
          "caching": {"type": "ephemeral", "ttl": "5m"},
      }
  ]

typescript TypeScript
  const tools: Anthropic.Beta.Messages.BetaToolUnion[] = [
    {
      type: "advisor_20260301",
      name: "advisor",
      model: "claude-opus-5",
      caching: { type: "ephemeral", ttl: "5m" }
    }
  ];

csharp C#
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  var tools = new BetaToolUnion[]
  {
      new BetaAdvisorTool20260301
      {
          Model = Messages::Model.ClaudeOpus5,
          Caching = new BetaCacheControlEphemeral { Ttl = Ttl.Ttl5m }
      }
  };

go Go
  tools := []anthropic.BetaToolUnionParam{
  	{OfAdvisorTool20260301: &anthropic.BetaAdvisorTool20260301Param{
  		Model:   anthropic.ModelClaudeOpus5,
  		Caching: anthropic.BetaCacheControlEphemeralParam{TTL: anthropic.BetaCacheControlEphemeralTTLTTL5m},
  	}},
  }

java Java
  import com.anthropic.models.beta.messages.BetaAdvisorTool20260301;
  import com.anthropic.models.beta.messages.BetaCacheControlEphemeral;
  import com.anthropic.models.beta.messages.BetaToolUnion;
  import com.anthropic.models.messages.Model;

  List<BetaToolUnion> tools = List.of(
      BetaToolUnion.ofAdvisorTool20260301(BetaAdvisorTool20260301.builder()
          .model(Model.CLAUDE_OPUS_5)
          .caching(BetaCacheControlEphemeral.builder()
              .ttl(BetaCacheControlEphemeral.Ttl.TTL_5M)
              .build())
          .build()));

php PHP
  $tools = [
      [
          'type' => 'advisor_20260301',
          'name' => 'advisor',
          'model' => 'claude-opus-5',
          'caching' => ['type' => 'ephemeral', 'ttl' => '5m'],
      ],
  ];

ruby Ruby
  tools = [
    {
      type: "advisor_20260301",
      name: "advisor",
      model: "claude-opus-5",
      caching: { type: "ephemeral", ttl: "5m" }
    }
  ]
  ```
</CodeGroup>

The advisor's prompt on the Nth call is the (N-1)th call's prompt with one more segment appended, so the prefix is stable across calls. With `caching` enabled, each advisor call writes a cache entry, and the next call reads up to that point and pays only for the delta. You'll see `cache_read_input_tokens` become non-zero on the second and later `advisor_message` iterations.

**When to enable it:** The cache write costs more than the reads save when the advisor is called two or fewer times per conversation. Caching breaks even at roughly three advisor calls and improves from there. Enable it for long agent loops, and keep it off for short tasks.

**Keep it consistent:** Set `caching` once and leave it for the whole conversation. Toggling it off and on mid-conversation causes cache misses.

<Warning>
  [`clear_thinking`](https://platform.claude.com/docs/en/build-with-claude/context-editing) with a `keep` value other than `"all"` shifts the advisor's quoted transcript each turn, causing advisor-side cache misses. This is a cost degradation only. Advice quality is unaffected. When extended thinking is enabled without explicit `clear_thinking` configuration, the API defaults to `keep: {type: "thinking_turns", value: 1}`, which triggers this behavior (the default on earlier Opus/Sonnet models and all Haiku models, whereas on Opus 4.5+ and Sonnet 4.6+ the default is to keep all turns). Set `keep: "all"` to preserve advisor cache stability.
</Warning>


## Combining with other tools

Source: https://platform.claude.com/llms-full.txt#combining-with-other-tools

The advisor tool composes with other server-side and client-side tools. Add them all to the same `tools` array:

<CodeGroup exclude="shell">
  ```python Python
  tools = [
      {
          "type": "web_search_20250305",
          "name": "web_search",
          "max_uses": 5,
      },
      {
          "type": "advisor_20260301",
          "name": "advisor",
          "model": "claude-opus-5",
      },
      {
          "name": "run_bash",
          "description": "Run a bash command",
          "input_schema": {
              "type": "object",
              "properties": {"command": {"type": "string"}},
          },
      },
  ]

typescript TypeScript
  const tools: Anthropic.Beta.Messages.BetaToolUnion[] = [
    {
      type: "web_search_20250305",
      name: "web_search",
      max_uses: 5
    },
    {
      type: "advisor_20260301",
      name: "advisor",
      model: "claude-opus-5"
    },
    {
      name: "run_bash",
      description: "Run a bash command",
      input_schema: {
        type: "object",
        properties: { command: { type: "string" } }
      }
    }
  ];

csharp C#
  using System.Text.Json;
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  var tools = new BetaToolUnion[]
  {
      new BetaWebSearchTool20250305 { MaxUses = 5 },
      new BetaAdvisorTool20260301 { Model = Messages::Model.ClaudeOpus5 },
      new BetaTool
      {
          Name = "run_bash",
          Description = "Run a bash command",
          InputSchema = new()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["command"] = JsonSerializer.SerializeToElement(new { type = "string" })
              }
          }
      }
  };

go Go
  tools := []anthropic.BetaToolUnionParam{
  	{OfWebSearchTool20250305: &anthropic.BetaWebSearchTool20250305Param{
  		MaxUses: anthropic.Int(5),
  	}},
  	{OfAdvisorTool20260301: &anthropic.BetaAdvisorTool20260301Param{
  		Model: anthropic.ModelClaudeOpus5,
  	}},
  	{OfTool: &anthropic.BetaToolParam{
  		Name:        "run_bash",
  		Description: anthropic.String("Run a bash command"),
  		InputSchema: anthropic.BetaToolInputSchemaParam{
  			Properties: map[string]any{
  				"command": map[string]any{"type": "string"},
  			},
  		},
  	}},
  }

java Java
  import com.anthropic.core.JsonValue;
  import com.anthropic.models.beta.messages.BetaAdvisorTool20260301;
  import com.anthropic.models.beta.messages.BetaTool;
  import com.anthropic.models.beta.messages.BetaToolUnion;
  import com.anthropic.models.beta.messages.BetaWebSearchTool20250305;
  import com.anthropic.models.messages.Model;

  List<BetaToolUnion> tools = List.of(
      BetaToolUnion.ofWebSearchTool20250305(BetaWebSearchTool20250305.builder()
          .maxUses(5L)
          .build()),
      BetaToolUnion.ofAdvisorTool20260301(BetaAdvisorTool20260301.builder()
          .model(Model.CLAUDE_OPUS_5)
          .build()),
      BetaToolUnion.ofBetaTool(BetaTool.builder()
          .name("run_bash")
          .description("Run a bash command")
          .inputSchema(BetaTool.InputSchema.builder()
              .properties(JsonValue.from(Map.of(
                  "command", Map.of("type", "string"))))
              .build())
          .build()));

php PHP
  $tools = [
      [
          'type' => 'web_search_20250305',
          'name' => 'web_search',
          'max_uses' => 5,
      ],
      [
          'type' => 'advisor_20260301',
          'name' => 'advisor',
          'model' => 'claude-opus-5',
      ],
      [
          'name' => 'run_bash',
          'description' => 'Run a bash command',
          'input_schema' => [
              'type' => 'object',
              'properties' => ['command' => ['type' => 'string']],
          ],
      ],
  ];

ruby Ruby
  tools = [
    {
      type: "web_search_20250305",
      name: "web_search",
      max_uses: 5
    },
    {
      type: "advisor_20260301",
      name: "advisor",
      model: "claude-opus-5"
    },
    {
      name: "run_bash",
      description: "Run a bash command",
      input_schema: {
        type: "object",
        properties: { command: { type: "string" } }
      }
    }
  ]
  ```
</CodeGroup>

The executor can search the web, call the advisor, and use your custom tools in the same turn. The advisor's plan can inform which tools the executor reaches for next.

| Feature                                                                                    | Interaction                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing) | Supported. `usage.iterations` is reported per item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)     | Returns the executor's first-iteration input tokens only. For a rough advisor estimate, call `count_tokens` with `model` set to the advisor model and the same messages.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| [Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing)   | `clear_tool_uses` is not fully compatible with advisor tool blocks. With `clear_thinking`, see the earlier caching warning.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `pause_turn`                                                                               | A dangling advisor call ends the response with `stop_reason: "pause_turn"` and a `server_tool_use` block with no result when no client `tool_use` block is awaiting your result in the same turn. The advisor runs on resumption. If the executor also called one of your tools in that turn, the response ends with `stop_reason: "tool_use"` instead, and the pending advisor call runs at the start of your next request, after you send the `tool_result` blocks. See [Resuming a paused turn](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#resuming-a-paused-turn), [Mixing server tools and client tools in one turn](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#mixing-server-tools-and-client-tools-in-one-turn), and [Server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#the-server-side-loop-and-pause-turn). |


## Best practices

Source: https://platform.claude.com/llms-full.txt#best-practices-5

### Prompting for coding and agent tasks

The advisor tool ships with a built-in description that nudges the executor to call it near the start of complex tasks and when it hits difficulty. For research tasks, no additional prompting is typically needed.

On coding and agent tasks, the advisor produces higher intelligence at similar cost when it reduces total tool calls and conversation length. Two timings drive this improvement:

1. An early first advisor call, after a few exploratory reads are in the transcript.
2. For difficult tasks, a final advisor call after file writes and test outputs are in the transcript.

If your agent exposes other planner-like tools (for example, a todo list tool), prompt the model to call the advisor before those tools so the advisor's plan funnels into them. The [suggested system prompt](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#suggested-system-prompt-for-coding-tasks) reinforces the early-call pattern. Add your own funnel-in sentence pointing at whichever planner tools your agent exposes.

#### Suggested system prompt for coding tasks

Without system-prompt steering, the executor tends to under-call the advisor in some domains, particularly coding tasks. For coding tasks where you want consistent advisor timing and around two to three calls for each task, prepend the following blocks to your executor system prompt before any other sentences that mention the advisor.

Timing guidance:

```text wrap
You have access to an `advisor` tool backed by a stronger reviewer model. It takes NO parameters — when you call advisor(), your entire conversation history is automatically forwarded. They see the task, every tool call you've made, every result you've seen.

Call advisor BEFORE substantive work — before writing, before committing to an interpretation, before building on an assumption. If the task requires orientation first (finding files, fetching a source, seeing what's there), do that, then call advisor. Orientation is not substantive work. Writing, editing, and declaring an answer are.

Also call advisor:
- When you believe the task is complete. BEFORE this call, make your deliverable durable: write the file, save the result, commit the change. The advisor call takes time; if the session ends during it, a durable result persists and an unwritten one doesn't.
- When stuck — errors recurring, approach not converging, results that don't fit.
- When considering a change of approach.

On tasks longer than a few steps, call advisor at least once before committing to an approach and once before declaring done. On short reactive tasks where the next action is dictated by tool output you just read, you don't need to keep calling — the advisor adds most of its value on the first call, before the approach crystallizes.

text wrap
Give the advice serious weight. If you follow a step and it fails empirically, or you have primary-source evidence that contradicts a specific claim (the file says X, the paper states Y), adapt. A passing self-test is not evidence the advice is wrong — it's evidence your test doesn't check what the advice is checking.

If you've already retrieved data pointing one way and the advisor points another: don't silently switch. Surface the conflict in one more advisor call — "I found X, you suggest Y, which constraint breaks the tie?" The advisor saw your evidence but may have underweighted it; a reconcile call is cheaper than committing to the wrong branch.

text wrap
Consult a stronger reviewer who sees your full conversation transcript.

No parameters. When you call advisor(), your entire history -- task, every tool call and result, your reasoning -- is automatically forwarded. The advisor sees exactly what you've done.

Call advisor BEFORE substantive work -- before writing, before committing to an interpretation, before building on an assumption. If the task requires orientation first (finding files, fetching a source, seeing what's there), do that, then call advisor. Orientation is not substantive work. Writing, editing, and declaring an answer are.

Also call advisor:
- When you believe the task is complete. BEFORE this call, make your deliverable durable: write the file, save the result, commit the change. The advisor call takes time; if the session ends during it, a durable result persists and an unwritten one doesn't.
- When stuck -- errors recurring, approach not converging, results that don't fit.
- When considering a change of approach.

On tasks longer than a few steps, call advisor at least once before committing to an approach and once before declaring done. On short reactive tasks where the next action is dictated by tool output you just read, you don't need to keep calling -- the advisor adds most of its value on the first call, before the approach crystallizes.

Give the advice serious weight. If you follow a step and it fails empirically, or you have primary-source evidence that contradicts a specific claim (the file says X, the paper states Y), adapt. A passing self-test is not evidence the advice is wrong -- it's evidence your test doesn't check what the advice is checking.

If you've already retrieved data pointing one way and the advisor points another: don't silently switch. Surface the conflict in one more advisor call -- "I found X, you suggest Y, which constraint breaks the tie?" The advisor saw your evidence but may have underweighted it; a reconcile call is cheaper than committing to the wrong branch.

Call advisor for design, architecture, and risk questions where you won't touch a file. If your response would be analysis or a recommendation with no other tool calls, call advisor first -- that judgment call is exactly where a second opinion is highest-value.

Hard rule: your first write_file, edit_file, or state-changing bash call on a task must be preceded by an advisor call in the same or an earlier turn. Read-only orientation commands (ls, cat, grep, find) are not state-changing. This is a checkpoint, not a difficulty judgment. It applies to one-line edits too.

text wrap
Call advisor for design, architecture, and risk questions where you won't touch a file. If your response would be analysis or a recommendation with no other tool calls, call advisor first. That judgment call is exactly where a second opinion is highest-value. (This does not apply to simple factual lookups or arithmetic; those you answer directly.)

Hard rule: your first write_file, edit_file, or state-changing bash call on a task must be preceded by an advisor call in the same or an earlier turn. Read-only orientation commands (ls, cat, grep, find) are not state-changing. This is a checkpoint, not a difficulty judgment. It applies to one-line edits too.

text wrap
(Advisor: please keep your guidance under 80 words — I need a focused starting point, not a comprehensive plan.)

python Python
  tools = [
      {
          "type": "advisor_20260301",
          "name": "advisor",
          "model": "claude-opus-5",
          "max_tokens": 2048,
      }
  ]

typescript TypeScript
  const tools: Anthropic.Beta.Messages.BetaToolUnion[] = [
    {
      type: "advisor_20260301",
      name: "advisor",
      model: "claude-opus-5",
      max_tokens: 2048
    }
  ];

csharp C#
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  var tools = new BetaToolUnion[]
  {
      new BetaAdvisorTool20260301
      {
          Model = Messages::Model.ClaudeOpus5,
          MaxTokens = 2048
      }
  };

go Go
  tools := []anthropic.BetaToolUnionParam{
  	{OfAdvisorTool20260301: &anthropic.BetaAdvisorTool20260301Param{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: anthropic.Int(2048),
  	}},
  }

java Java
  import com.anthropic.models.beta.messages.BetaAdvisorTool20260301;
  import com.anthropic.models.beta.messages.BetaToolUnion;
  import com.anthropic.models.messages.Model;

  List<BetaToolUnion> tools = List.of(
      BetaToolUnion.ofAdvisorTool20260301(BetaAdvisorTool20260301.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(2048L)
          .build()));

php PHP
  $tools = [
      [
          'type' => 'advisor_20260301',
          'name' => 'advisor',
          'model' => 'claude-opus-5',
          'max_tokens' => 2048,
      ],
  ];

ruby Ruby
  tools = [
    {
      type: "advisor_20260301",
      name: "advisor",
      model: "claude-opus-5",
      max_tokens: 2048
    }
  ]

json
{
  "type": "advisor_tool_result",
  "tool_use_id": "srvtoolu_abc123",
  "content": {
    "type": "advisor_redacted_result",
    "encrypted_content": "EqQBCkYIBRgCIiQ3YTAwMjY1Mi1mZjM5LTQ1NGUtODgxNC1kNjNjNTk1ZWI3Y...",
    "stop_reason": "max_tokens"
  }
}
```

Check `output_tokens` on the corresponding `advisor_message` entry in `usage.iterations` to see how close each call came to its cap.

Compared with the [prompt-based approach](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#trimming-advisor-output-length), `max_tokens` is a hard ceiling rather than a soft request. Use `max_tokens` when you need a guaranteed bound for cost or latency. Use the prompt-based approach (or both together) when you want to bias toward brevity without risking a mid-thought cut.

### Pairing with effort settings

For coding tasks, pairing a Sonnet executor at medium [effort](https://platform.claude.com/docs/en/build-with-claude/effort) with an Opus advisor achieves intelligence comparable to Sonnet at default effort, at lower cost. For maximum intelligence, keep the executor at default effort.

### Cost control

* For conversation-level budgets, count advisor calls client-side. When you reach your cap, remove the advisor tool from `tools`; you do not need to strip `advisor_tool_result` blocks from your message history (see the note in [Multi-turn conversations](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#multi-turn-conversations)).
* Enable `caching` only for conversations where you expect three or more advisor calls.


## Model compatibility

Source: https://platform.claude.com/llms-full.txt#model-compatibility

The executor model (the top-level `model` field) and the advisor model (the `model` field inside the tool definition) must form a valid pair. The advisor must be Claude Sonnet 4.6 or a more capable model, and it must be at least as capable as the executor. Models of equal capability (for example, Claude Opus 4.7 and Claude Opus 4.8) can advise each other.

| Executor models                       | Advisor models                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Haiku 4.5 (claude-haiku-4-5)   | Claude Mythos 5.1 (claude-mythos-5-1) Claude Fable 5.1 (claude-fable-5-1) Claude Mythos 5 (claude-mythos-5) Claude Fable 5 (claude-fable-5) Claude Opus 5 (claude-opus-5) Claude Opus 4.8 (claude-opus-4-8) Claude Opus 4.7 (claude-opus-4-7) Claude Opus 4.6 (claude-opus-4-6) Claude Sonnet 5 (claude-sonnet-5) Claude Sonnet 4.6 (claude-sonnet-4-6) |
| Claude Sonnet 4.6 (claude-sonnet-4-6) | Claude Mythos 5.1 (claude-mythos-5-1) Claude Fable 5.1 (claude-fable-5-1) Claude Mythos 5 (claude-mythos-5) Claude Fable 5 (claude-fable-5) Claude Opus 5 (claude-opus-5) Claude Opus 4.8 (claude-opus-4-8) Claude Opus 4.7 (claude-opus-4-7) Claude Opus 4.6 (claude-opus-4-6) Claude Sonnet 5 (claude-sonnet-5) Claude Sonnet 4.6 (claude-sonnet-4-6) |
| Claude Sonnet 5 (claude-sonnet-5)     | Claude Mythos 5.1 (claude-mythos-5-1) Claude Fable 5.1 (claude-fable-5-1) Claude Mythos 5 (claude-mythos-5) Claude Fable 5 (claude-fable-5) Claude Opus 5 (claude-opus-5) Claude Opus 4.8 (claude-opus-4-8) Claude Opus 4.7 (claude-opus-4-7) Claude Sonnet 5 (claude-sonnet-5)                                                                         |
| Claude Opus 4.6 (claude-opus-4-6)     | Claude Mythos 5.1 (claude-mythos-5-1) Claude Fable 5.1 (claude-fable-5-1) Claude Mythos 5 (claude-mythos-5) Claude Fable 5 (claude-fable-5) Claude Opus 5 (claude-opus-5) Claude Opus 4.8 (claude-opus-4-8) Claude Opus 4.7 (claude-opus-4-7) Claude Opus 4.6 (claude-opus-4-6) Claude Sonnet 5 (claude-sonnet-5)                                       |
| Claude Opus 4.7 (claude-opus-4-7)     | Claude Mythos 5.1 (claude-mythos-5-1) Claude Fable 5.1 (claude-fable-5-1) Claude Mythos 5 (claude-mythos-5) Claude Fable 5 (claude-fable-5) Claude Opus 5 (claude-opus-5) Claude Opus 4.8 (claude-opus-4-8) Claude Opus 4.7 (claude-opus-4-7)                                                                                                           |
| Claude Opus 4.8 (claude-opus-4-8)     | Claude Mythos 5.1 (claude-mythos-5-1) Claude Fable 5.1 (claude-fable-5-1) Claude Mythos 5 (claude-mythos-5) Claude Fable 5 (claude-fable-5) Claude Opus 5 (claude-opus-5) Claude Opus 4.8 (claude-opus-4-8) Claude Opus 4.7 (claude-opus-4-7)                                                                                                           |
| Claude Opus 5 (claude-opus-5)         | Claude Mythos 5.1 (claude-mythos-5-1) Claude Fable 5.1 (claude-fable-5-1) Claude Mythos 5 (claude-mythos-5) Claude Fable 5 (claude-fable-5) Claude Opus 5 (claude-opus-5)                                                                                                                                                                               |
| Claude Fable 5 (claude-fable-5)       | Claude Mythos 5.1 (claude-mythos-5-1) Claude Fable 5.1 (claude-fable-5-1) Claude Mythos 5 (claude-mythos-5) Claude Fable 5 (claude-fable-5) Claude Opus 5 (claude-opus-5)                                                                                                                                                                               |
| Claude Mythos 5 (claude-mythos-5)     | Claude Mythos 5.1 (claude-mythos-5-1) Claude Fable 5.1 (claude-fable-5-1) Claude Mythos 5 (claude-mythos-5) Claude Fable 5 (claude-fable-5) Claude Opus 5 (claude-opus-5)                                                                                                                                                                               |
| Claude Fable 5.1 (claude-fable-5-1)   | Claude Mythos 5.1 (claude-mythos-5-1) Claude Fable 5.1 (claude-fable-5-1)                                                                                                                                                                                                                                                                               |
| Claude Mythos 5.1 (claude-mythos-5-1) | Claude Mythos 5.1 (claude-mythos-5-1) Claude Fable 5.1 (claude-fable-5-1)                                                                                                                                                                                                                                                                               |

If you request an invalid pair, the API returns a `400 invalid_request_error` naming the unsupported combination.

### Platform availability

The advisor tool is available in beta on the Claude API and on [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws). It is not currently available on Amazon Bedrock, Google Cloud, or Microsoft Foundry.


## Advisor on Claude Managed Agents

Source: https://platform.claude.com/llms-full.txt#advisor-on-claude-managed-agents

[Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) sessions support an advisor as well, configured as part of the agent rather than as a tool definition: add a `{"type": "advisor", "model": ...}` entry to the agent's multiagent roster, and the session's primary thread can consult that model mid-turn. The roster entry takes no `max_uses`, `max_tokens`, or `caching` options, and advice is delivered as thread events on the session's event stream rather than as `advisor_tool_result` blocks in the response. See [Give the session an advisor](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration#give-the-session-an-advisor).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-24

<CardGroup cols={2}>
  <Card title="Memory tool" icon="brain" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool">
    Store and retrieve information across conversations with a client-side memory directory.
  </Card>

  <Card title="Server tools" icon="tool" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools">
    Work with Anthropic-executed tools: server\_tool\_use blocks, pause\_turn continuation, and domain filtering.
  </Card>

  <Card title="Tool reference" icon="book" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference">
    Directory of Anthropic-provided tools and reference for optional tool definition properties.
  </Card>

  <Card title="Effort" icon="gauge" href="https://platform.claude.com/docs/en/build-with-claude/effort">
    Control how many tokens Claude uses when responding with the effort parameter, trading off between response thoroughness and token efficiency.
  </Card>
</CardGroup>


---
title: Bash tool
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool
description: Let Claude request shell commands that your application runs in a persistent bash session and returns as tool results.
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

The bash tool is a [client tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works): Claude doesn't run commands itself. When you include the tool in a request, Claude replies with a `tool_use` block that names the command to run. Your application runs that command in a bash session it owns and returns the output in a `tool_result` block.

Your application keeps one bash process alive across tool calls, so state persists between commands. The working directory, environment variables, and any files a command creates are still there for the next command.

The current version of the tool is `bash_20250124`. For model support, beta headers, and the earlier version, see [Tool versions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool#tool-versions). For all Anthropic-provided tools, see the [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference).


## Use cases

Source: https://platform.claude.com/llms-full.txt#use-cases

* **Development workflows:** Run build commands, tests, and development tools
* **System automation:** Execute scripts, manage files, automate tasks
* **Data processing:** Process files, run analysis scripts, manage datasets
* **Environment setup:** Install packages, configure environments


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-2

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
          "type": "bash_20250124",
          "name": "bash"
        }
      ],
      "messages": [
        {
          "role": "user",
          "content": "List all Python files in the current directory."
        }
      ]
    }'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --tool '{type: bash_20250124, name: bash}' \
    --message '{role: user, content: List all Python files in the current directory.}'

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[{"type": "bash_20250124", "name": "bash"}],
      messages=[
          {"role": "user", "content": "List all Python files in the current directory."}
      ],
  )

  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [{ type: "bash_20250124", name: "bash" }],
    messages: [
      {
        role: "user",
        content: "List all Python files in the current directory."
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
          Tools = [new ToolBash20250124()],
          Messages =
          [
              new()
              {
                  Role = Role.User,
                  Content = "List all Python files in the current directory.",
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
  		{OfBashTool20250124: &anthropic.ToolBash20250124Param{}},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("List all Python files in the current directory.")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.messages.ToolBash20250124;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      Message response = client.messages().create(
          MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024)
              .addTool(ToolBash20250124.builder().build())
              .addUserMessage("List all Python files in the current directory.")
              .build()
      );

      IO.println(response);
  }

php PHP
  use Anthropic\Messages\ToolBash20250124;

  $client = new Client();

  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      tools: [new ToolBash20250124()],
      messages: [
          ['role' => 'user', 'content' => 'List all Python files in the current directory.'],
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [{type: "bash_20250124", name: "bash"}],
    messages: [
      {role: "user", content: "List all Python files in the current directory."}
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
      "text": "I'll list all Python files in the current directory for you."
    },
    {
      "type": "tool_use",
      "id": "toolu_01A09q90qw90lq917835lq9",
      "name": "bash",
      "input": {
        "command": "ls *.py"
      }
    }
  ]
}
```

Run `input.command` in your bash session and send the output back as a `tool_result`. See [Implement the bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool#implement-the-bash-tool) for the round trip.


## How it works

Source: https://platform.claude.com/llms-full.txt#how-it-works-3

Each tool call is one round trip between Claude and your application:

1. Claude returns a `tool_use` block containing the `command` to run.
2. Your application runs the command in its bash session.
3. Your application returns the command's output, stdout and stderr together, to Claude in a `tool_result` block.
4. Claude either requests another command in the same session or responds with text.

Claude can also return several `tool_use` blocks in one response. Run them in order in the same session and return all of the results in one `user` message. See [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use).

The API is stateless. Nothing about your shell session travels between requests, so your application decides when the session starts, how long it lives, and when to restart it. For the full request and response cycle, see [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls).


## Parameters

Source: https://platform.claude.com/llms-full.txt#parameters

A bash tool definition has two required fields, `type` and `name`, and the `name` must be `bash`. The tool is schema-less: you don't provide an `input_schema`, because the schema is built into Claude's model and can't be modified. The following table lists the input fields Claude sets when it calls the tool.

| Parameter | Required | Description                               |
| --------- | -------- | ----------------------------------------- |
| `command` | Yes\*    | The bash command to run                   |
| `restart` | No       | Set to `true` to restart the bash session |

\*Required unless using `restart`

To handle `restart: true`, kill the shell process, start a new one, and return a `tool_result` that confirms the restart. A restarted session starts clean: the working directory, environment variables, and any running processes are gone.

<Accordion title="Example usage">
  Run a command:

Restart the session:

</Accordion>


## Tool versions

Source: https://platform.claude.com/llms-full.txt#tool-versions

`bash_20250124` is the current version of the tool, and it requires no beta header. Every model from Claude Sonnet 3.7 ([retired](https://platform.claude.com/docs/en/about-claude/model-deprecations)) onward accepts it, including all current Claude models.

The original `bash_20241022` version works only with the October 2024 Claude Sonnet 3.5 model ([retired](https://platform.claude.com/docs/en/about-claude/model-deprecations)). Requests that use it need the `anthropic-beta: computer-use-2024-10-22` header, and the SDKs expose it only in their beta namespaces. New integrations should use `bash_20250124`.


## Example: Multistep automation

Source: https://platform.claude.com/llms-full.txt#example-multistep-automation

Claude can chain commands across tool calls to complete a multistep task:

The session maintains state between commands, so files created in step 2 are available in step 3.


## Implement the bash tool

Source: https://platform.claude.com/llms-full.txt#implement-the-bash-tool

Claude determines which command to run. Your application owns everything else: the shell process, the timeout, and the safety checks. The following steps show a minimal implementation.

<Steps>
  <Step title="Create a persistent bash session">
    Start one long-lived bash process and run every command inside it. Because a pipe to a live process never reports end-of-file, the session prints a unique sentinel line after each command to mark where that command's output ends:

    <CodeGroup exclude="shell">
      ```python Python
      import subprocess
      import uuid


      class BashSession:
          """A bash process that stays alive between commands so state persists."""

          def __init__(self):
              self.process = subprocess.Popen(
                  ["/bin/bash"],
                  stdin=subprocess.PIPE,
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,  # interleave errors with output, in order
                  start_new_session=True,  # own process group: a timeout can kill every child
                  text=True,
              )

          def execute_command(self, command):
              """Run a command in the session and return its output."""
              sentinel = f"__CLAUDE_BASH_DONE_{uuid.uuid4().hex}__"  # unique per call
              self.process.stdin.write(f"{command}\necho {sentinel}\n")
              self.process.stdin.flush()

              output = []
              for line in self.process.stdout:
                  if sentinel in line:  # this command's output is complete
                      break
                  output.append(line)
              return "".join(output)

          def restart(self):
              self.process.kill()
              self.process.wait()
              self.__init__()


      bash_session = BashSession()
      print(bash_session.execute_command("cd /tmp && pwd"))
      print(bash_session.execute_command("pwd"))  # still /tmp: the session kept its state

typescript TypeScript
      import { spawn, type ChildProcessWithoutNullStreams } from "node:child_process";
      import { createInterface, type Interface } from "node:readline";
      import { randomUUID } from "node:crypto";

      // A bash process that stays alive between commands so state persists.
      class BashSession {
        process!: ChildProcessWithoutNullStreams;
        private lines!: Interface;

        constructor() {
          this.start();
        }

        private start(): void {
          this.process = spawn("/bin/bash", {
            detached: true // own process group: a timeout can kill every child
          });
          this.process.stdin.write("exec 2>&1\n"); // interleave errors with output, in order
          this.lines = createInterface({ input: this.process.stdout });
        }

        // Run a command in the session and return its output.
        executeCommand(command: string): Promise<string> {
          const sentinel = `__CLAUDE_BASH_DONE_${randomUUID()}__`; // unique per call
          const output: string[] = [];
          const result = new Promise<string>((resolve) => {
            const onLine = (line: string): void => {
              if (line.includes(sentinel)) {
                // this command's output is complete
                this.lines.off("line", onLine);
                resolve(output.join(""));
              } else {
                output.push(`${line}\n`);
              }
            };
            this.lines.on("line", onLine);
          });
          this.process.stdin.write(`${command}\necho ${sentinel}\n`);
          return result;
        }

        restart(): void {
          this.process.kill("SIGKILL");
          this.lines.close();
          this.start();
        }
      }

      const session = new BashSession();
      console.log(await session.executeCommand("cd /tmp && pwd"));
      console.log(await session.executeCommand("pwd")); // still /tmp: the session kept its state
      session.process.stdin.end(); // closing stdin ends the shell so the script can exit

csharp C#
      using System.Diagnostics;
      using System.Text;

      var session = new BashSession();
      Console.Write(session.ExecuteCommand("cd /tmp && pwd"));
      Console.Write(session.ExecuteCommand("pwd")); // still /tmp: the session kept its state

      // A bash process that stays alive between commands so state persists.
      class BashSession
      {
          public Process Process { get; private set; }

          public BashSession()
          {
              Process = Start();
          }

          static Process Start()
          {
              var process = Process.Start(new ProcessStartInfo("/bin/bash")
              {
                  RedirectStandardInput = true,
                  RedirectStandardOutput = true
              })!;
              process.StandardInput.Write("exec 2>&1\n"); // interleave errors with output, in order
              process.StandardInput.Flush();
              return process;
          }

          // Run a command in the session and return its output.
          public string ExecuteCommand(string command)
          {
              var sentinel = $"__CLAUDE_BASH_DONE_{Guid.NewGuid():N}__"; // unique per call
              Process.StandardInput.Write($"{command}\necho {sentinel}\n");
              Process.StandardInput.Flush();

              var output = new StringBuilder();
              while (Process.StandardOutput.ReadLine() is string line)
              {
                  if (line.Contains(sentinel)) // this command's output is complete
                  {
                      break;
                  }
                  output.Append(line).Append('\n');
              }
              return output.ToString();
          }

          public void Restart()
          {
              Process.Kill(entireProcessTree: true);
              Process.WaitForExit();
              Process = Start();
          }
      }

go Go
      import (
      	"bufio"
      	"crypto/rand"
      	"encoding/hex"
      	"fmt"
      	"io"
      	"log"
      	"os/exec"
      	"strings"
      	"syscall"
      )

      // BashSession is a bash process that stays alive between commands so state persists.
      type BashSession struct {
      	cmd    *exec.Cmd
      	stdin  io.WriteCloser
      	output *bufio.Reader
      }

      func NewBashSession() (*BashSession, error) {
      	cmd := exec.Command("/bin/bash")
      	cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true} // own process group: a timeout can kill every child
      	stdin, err := cmd.StdinPipe()
      	if err != nil {
      		return nil, err
      	}
      	stdout, err := cmd.StdoutPipe()
      	if err != nil {
      		return nil, err
      	}
      	cmd.Stderr = cmd.Stdout // interleave errors with output, in order
      	if err := cmd.Start(); err != nil {
      		return nil, err
      	}
      	return &BashSession{cmd: cmd, stdin: stdin, output: bufio.NewReader(stdout)}, nil
      }

      // ExecuteCommand runs a command in the session and returns its output.
      func (s *BashSession) ExecuteCommand(command string) string {
      	buf := make([]byte, 16)
      	rand.Read(buf)
      	sentinel := fmt.Sprintf("__CLAUDE_BASH_DONE_%s__", hex.EncodeToString(buf)) // unique per call
      	fmt.Fprintf(s.stdin, "%s\necho %s\n", command, sentinel)

      	var output strings.Builder
      	for {
      		line, err := s.output.ReadString('\n')
      		if err != nil || strings.Contains(line, sentinel) { // this command's output is complete
      			break
      		}
      		output.WriteString(line)
      	}
      	return output.String()
      }

      // Restart kills the shell and starts a fresh session in its place.
      func (s *BashSession) Restart() error {
      	s.cmd.Process.Kill()
      	s.cmd.Wait()
      	fresh, err := NewBashSession()
      	if err != nil {
      		return err
      	}
      	*s = *fresh
      	return nil
      }

      func main() {
      	session, err := NewBashSession()
      	if err != nil {
      		log.Fatal(err)
      	}
      	fmt.Print(session.ExecuteCommand("cd /tmp && pwd"))
      	fmt.Print(session.ExecuteCommand("pwd")) // still /tmp: the session kept its state
      }

java Java
      import java.io.BufferedReader;
      import java.io.BufferedWriter;
      import java.io.IOException;
      import java.io.InputStreamReader;
      import java.io.OutputStreamWriter;
      import java.util.UUID;

      // A bash process that stays alive between commands so state persists.
      class BashSession {
          Process process;
          BufferedWriter stdin;
          BufferedReader output;

          BashSession() throws IOException {
              start();
          }

          void start() throws IOException {
              ProcessBuilder builder = new ProcessBuilder("/bin/bash");
              builder.redirectErrorStream(true); // interleave errors with output, in order
              process = builder.start();
              stdin = new BufferedWriter(new OutputStreamWriter(process.getOutputStream()));
              output = new BufferedReader(new InputStreamReader(process.getInputStream()));
          }

          // Run a command in the session and return its output.
          String executeCommand(String command) throws IOException {
              String sentinel = "__CLAUDE_BASH_DONE_" + UUID.randomUUID() + "__"; // unique per call
              stdin.write(command + "\necho " + sentinel + "\n");
              stdin.flush();

              StringBuilder result = new StringBuilder();
              String line;
              while ((line = output.readLine()) != null) {
                  if (line.contains(sentinel)) { // this command's output is complete
                      break;
                  }
                  result.append(line).append("\n");
              }
              return result.toString();
          }

          void restart() throws IOException, InterruptedException {
              process.destroyForcibly();
              process.waitFor();
              start();
          }
      }

      void main() throws Exception {
          BashSession session = new BashSession();
          IO.println(session.executeCommand("cd /tmp && pwd"));
          IO.println(session.executeCommand("pwd")); // still /tmp: the session kept its state
      }

php PHP
      // A bash process that stays alive between commands so state persists.
      class BashSession
      {
          public $process;
          public $stdin;
          public $output;

          public function __construct()
          {
              $this->start();
          }

          private function start(): void
          {
              // setsid gives the shell its own process group: a timeout can kill every child
              $this->process = proc_open(
                  ['setsid', '/bin/bash'],
                  [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['redirect', 1]], // interleave errors with output
                  $pipes
              );
              $this->stdin = $pipes[0];
              $this->output = $pipes[1];
          }

          // Run a command in the session and return its output.
          public function executeCommand(string $command): string
          {
              $sentinel = '__CLAUDE_BASH_DONE_' . bin2hex(random_bytes(16)) . '__'; // unique per call
              fwrite($this->stdin, "{$command}\necho {$sentinel}\n");
              fflush($this->stdin);

              $output = '';
              while (($line = fgets($this->output)) !== false) {
                  if (str_contains($line, $sentinel)) { // this command's output is complete
                      break;
                  }
                  $output .= $line;
              }
              return $output;
          }

          public function restart(): void
          {
              proc_terminate($this->process, 9);
              proc_close($this->process);
              $this->start();
          }
      }

      $session = new BashSession();
      echo $session->executeCommand("cd /tmp && pwd");
      echo $session->executeCommand("pwd"); // still /tmp: the session kept its state

ruby Ruby
      require "open3"
      require "securerandom"

      # A bash process that stays alive between commands so state persists.
      class BashSession
        attr_reader :output, :wait_thread

        def initialize
          start
        end

        # Run a command in the session and return its output.
        def execute_command(command)
          sentinel = "__CLAUDE_BASH_DONE_#{SecureRandom.hex(16)}__" # unique per call
          @stdin.write("#{command}\necho #{sentinel}\n")
          @stdin.flush

          output = +""
          @output.each_line do |line|
            break if line.include?(sentinel) # this command's output is complete

            output << line
          end
          output
        end

        def restart
          Process.kill("KILL", @wait_thread.pid)
          @wait_thread.join
          start
        end

        private

        def start
          # popen2e interleaves errors with output, in order; pgroup gives the shell its
          # own process group so a timeout can kill every child
          @stdin, @output, @wait_thread = Open3.popen2e("/bin/bash", pgroup: true)
        end
      end

      session = BashSession.new
      puts session.execute_command("cd /tmp && pwd")
      puts session.execute_command("pwd") # still /tmp: the session kept its state

python Python
      tool_results = []
      for content in response.content:
          if content.type == "tool_use" and content.name == "bash":
              if content.input.get("restart"):
                  bash_session.restart()
                  result = "Bash session restarted"
              else:
                  command = content.input.get("command")
                  result = bash_session.execute_command(command)

              # One tool_result per tool_use block, all returned in the next user message
              tool_results.append(
                  {"type": "tool_result", "tool_use_id": content.id, "content": result}
              )

typescript TypeScript
      const toolResults: { type: string; tool_use_id: string; content: string }[] = [];
      for (const block of response.content) {
        if (block.type === "tool_use" && block.name === "bash") {
          let result: string;
          if (block.input.restart) {
            bashSession.restart();
            result = "Bash session restarted";
          } else {
            result = await bashSession.executeCommand(block.input.command ?? "");
          }

          // One tool_result per tool_use block, all returned in the next user message
          toolResults.push({ type: "tool_result", tool_use_id: block.id, content: result });
        }
      }

csharp C#
      var toolResults = new List<ToolResultBlockParam>();
      foreach (var block in response.Content)
      {
          if (block.TryPickToolUse(out var toolUse) && toolUse.Name == "bash")
          {
              string result;
              if (toolUse.Input.TryGetValue("restart", out var restart) && restart.GetBoolean())
              {
                  bashSession.Restart();
                  result = "Bash session restarted";
              }
              else
              {
                  var command = toolUse.Input["command"].GetString() ?? "";
                  result = bashSession.ExecuteCommand(command);
              }

              // One tool_result per tool_use block, all returned in the next user message
              toolResults.Add(new ToolResultBlockParam { ToolUseID = toolUse.ID, Content = result });
          }
      }

go Go
      var toolResults []anthropic.ContentBlockParamUnion
      for _, block := range response.Content {
      	if block.Type == "tool_use" && block.Name == "bash" {
      		var input struct {
      			Command string `json:"command"`
      			Restart bool   `json:"restart"`
      		}
      		if err := json.Unmarshal(block.Input, &input); err != nil {
      			log.Fatal(err)
      		}

      		var result string
      		if input.Restart {
      			bashSession.Restart()
      			result = "Bash session restarted"
      		} else {
      			result = bashSession.ExecuteCommand(input.Command)
      		}

      		// One tool_result per tool_use block, all returned in the next user message
      		toolResults = append(toolResults, anthropic.NewToolResultBlock(block.ID, result, false))
      	}
      }

java Java
      List<Map<String, Object>> toolResults = new ArrayList<>();
      for (ContentBlock block : response.content()) {
          if (block.type().equals("tool_use") && block.name().equals("bash")) {
              String result;
              if (Boolean.TRUE.equals(block.input().get("restart"))) {
                  bashSession.restart();
                  result = "Bash session restarted";
              } else {
                  String command = (String) block.input().get("command");
                  result = bashSession.executeCommand(command);
              }

              // One tool_result per tool_use block, all returned in the next user message
              toolResults.add(Map.of("type", "tool_result", "tool_use_id", block.id(), "content", result));
          }
      }

php PHP
      $toolResults = [];
      foreach ($response->content as $block) {
          if ($block->type === 'tool_use' && $block->name === 'bash') {
              if (!empty($block->input['restart'])) {
                  $bashSession->restart();
                  $result = 'Bash session restarted';
              } else {
                  $result = $bashSession->executeCommand($block->input['command']);
              }

              // One tool_result per tool_use block, all returned in the next user message
              $toolResults[] = ['type' => 'tool_result', 'tool_use_id' => $block->id, 'content' => $result];
          }
      }

ruby Ruby
      tool_results = []
      response.content.each do |block|
        next unless block.type == :tool_use && block.name == "bash"

        result =
          if block.input[:restart]
            bash_session.restart
            "Bash session restarted"
          else
            bash_session.execute_command(block.input[:command])
          end

        # One tool_result per tool_use block, all returned in the next user message
        tool_results << {type: "tool_result", tool_use_id: block.id, content: result}
      end

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
              "type": "bash_20250124",
              "name": "bash"
            }
          ],
          "messages": [
            {
              "role": "user",
              "content": "List all Python files in the current directory."
            },
            {
              "role": "assistant",
              "content": [
                {
                  "type": "tool_use",
                  "id": "toolu_01A09q90qw90lq917835lq9",
                  "name": "bash",
                  "input": {
                    "command": "ls *.py"
                  }
                }
              ]
            },
            {
              "role": "user",
              "content": [
                {
                  "type": "tool_result",
                  "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
                  "content": "analysis.py\nprocess_data.py\n"
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
        - type: bash_20250124
          name: bash
      messages:
        - role: user
          content: List all Python files in the current directory.
        - role: assistant
          content:
            - type: tool_use
              id: toolu_01A09q90qw90lq917835lq9
              name: bash
              input:
                command: ls *.py
        - role: user
          content:
            - type: tool_result
              tool_use_id: toolu_01A09q90qw90lq917835lq9
              content: |
                analysis.py
                process_data.py
      YAML

python Python
      client = anthropic.Anthropic()

      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          tools=[{"type": "bash_20250124", "name": "bash"}],
          messages=[
              {"role": "user", "content": "List all Python files in the current directory."},
              {
                  "role": "assistant",
                  "content": [
                      {
                          "type": "tool_use",
                          "id": "toolu_01A09q90qw90lq917835lq9",
                          "name": "bash",
                          "input": {"command": "ls *.py"},
                      }
                  ],
              },
              {
                  "role": "user",
                  "content": [
                      {
                          "type": "tool_result",
                          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
                          "content": "analysis.py\nprocess_data.py\n",
                      }
                  ],
              },
          ],
      )

      print(response.content)

typescript TypeScript
      const client = new Anthropic();

      const response = await client.messages.create({
        model: "claude-opus-5",
        max_tokens: 1024,
        tools: [{ type: "bash_20250124", name: "bash" }],
        messages: [
          {
            role: "user",
            content: "List all Python files in the current directory."
          },
          {
            role: "assistant",
            content: [
              {
                type: "tool_use",
                id: "toolu_01A09q90qw90lq917835lq9",
                name: "bash",
                input: { command: "ls *.py" }
              }
            ]
          },
          {
            role: "user",
            content: [
              {
                type: "tool_result",
                tool_use_id: "toolu_01A09q90qw90lq917835lq9",
                content: "analysis.py\nprocess_data.py\n"
              }
            ]
          }
        ]
      });

      console.log(response.content);

csharp C#
      var client = new AnthropicClient();

      var response = await client.Messages.Create(
          new()
          {
              Model = Model.ClaudeOpus5,
              MaxTokens = 1024,
              Tools = [new ToolBash20250124()],
              Messages =
              [
                  new()
                  {
                      Role = Role.User,
                      Content = "List all Python files in the current directory.",
                  },
                  new()
                  {
                      Role = Role.Assistant,
                      Content = new MessageParamContent(new List<ContentBlockParam>
                      {
                          new ContentBlockParam(new ToolUseBlockParam()
                          {
                              ID = "toolu_01A09q90qw90lq917835lq9",
                              Name = "bash",
                              Input = new Dictionary<string, JsonElement>
                              {
                                  ["command"] = JsonSerializer.SerializeToElement("ls *.py"),
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
                              ToolUseID = "toolu_01A09q90qw90lq917835lq9",
                              Content = "analysis.py\nprocess_data.py\n",
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
      		{OfBashTool20250124: &anthropic.ToolBash20250124Param{}},
      	},
      	Messages: []anthropic.MessageParam{
      		anthropic.NewUserMessage(anthropic.NewTextBlock("List all Python files in the current directory.")),
      		anthropic.NewAssistantMessage(
      			anthropic.NewToolUseBlock(
      				"toolu_01A09q90qw90lq917835lq9",
      				map[string]any{"command": "ls *.py"},
      				"bash",
      			),
      		),
      		anthropic.NewUserMessage(
      			anthropic.NewToolResultBlock(
      				"toolu_01A09q90qw90lq917835lq9",
      				"analysis.py\nprocess_data.py\n",
      				false,
      			),
      		),
      	},
      })
      if err != nil {
      	log.Fatal(err)
      }
      fmt.Println(response.Content)

java Java
      import com.anthropic.core.JsonValue;
      import com.anthropic.models.messages.ContentBlockParam;
      // ...
      import com.anthropic.models.messages.ToolBash20250124;
      import com.anthropic.models.messages.ToolResultBlockParam;
      import com.anthropic.models.messages.ToolUseBlockParam;
      // ...
      void main() {
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          MessageCreateParams params = MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024)
              .addTool(ToolBash20250124.builder().build())
              .addUserMessage("List all Python files in the current directory.")
              .addAssistantMessageOfBlockParams(
                  List.of(
                      ContentBlockParam.ofToolUse(
                          ToolUseBlockParam.builder()
                              .id("toolu_01A09q90qw90lq917835lq9")
                              .name("bash")
                              .input(
                                  ToolUseBlockParam.Input.builder()
                                      .putAdditionalProperty("command", JsonValue.from("ls *.py"))
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
                              .toolUseId("toolu_01A09q90qw90lq917835lq9")
                              .content("analysis.py\nprocess_data.py\n")
                              .build()
                      )
                  )
              )
              .build();

          Message response = client.messages().create(params);
          IO.println(response.content());
      }

php PHP
      use Anthropic\Messages\ToolBash20250124;

      $client = new Client();

      $response = $client->messages->create(
          model: 'claude-opus-5',
          maxTokens: 1024,
          tools: [new ToolBash20250124()],
          messages: [
              ['role' => 'user', 'content' => 'List all Python files in the current directory.'],
              [
                  'role' => 'assistant',
                  'content' => [
                      [
                          'type' => 'tool_use',
                          'id' => 'toolu_01A09q90qw90lq917835lq9',
                          'name' => 'bash',
                          'input' => ['command' => 'ls *.py'],
                      ],
                  ],
              ],
              [
                  'role' => 'user',
                  'content' => [
                      [
                          'type' => 'tool_result',
                          'tool_use_id' => 'toolu_01A09q90qw90lq917835lq9',
                          'content' => "analysis.py\nprocess_data.py\n",
                      ],
                  ],
              ],
          ],
      );

      print_r($response->content);

ruby Ruby
      client = Anthropic::Client.new

      response = client.messages.create(
        model: "claude-opus-5",
        max_tokens: 1024,
        tools: [{type: "bash_20250124", name: "bash"}],
        messages: [
          {role: "user", content: "List all Python files in the current directory."},
          {
            role: "assistant",
            content: [
              {
                type: "tool_use",
                id: "toolu_01A09q90qw90lq917835lq9",
                name: "bash",
                input: {command: "ls *.py"}
              }
            ]
          },
          {
            role: "user",
            content: [
              {
                type: "tool_result",
                tool_use_id: "toolu_01A09q90qw90lq917835lq9",
                content: "analysis.py\nprocess_data.py\n"
              }
            ]
          }
        ]
      )

      puts response.content

python Python
      import shlex

      ALLOWED_COMMANDS = {"ls", "cat", "echo", "pwd", "grep", "find", "wc", "head", "tail"}
      SHELL_OPERATORS = {"&&", "||", "|", ";", "&", ">", "<", ">>"}


      def validate_command(command):
          # Allow only commands from an explicit allowlist
          try:
              tokens = shlex.split(command)
          except ValueError:
              return False, "Could not parse command"

          if not tokens:
              return False, "Empty command"

          executable = tokens[0]
          if executable not in ALLOWED_COMMANDS:
              return False, f"Command '{executable}' is not in the allowlist"

          # Reject shell operators written as separate words
          for token in tokens[1:]:
              if token in SHELL_OPERATORS or token.startswith(("$", "`")):
                  return False, f"Shell operator '{token}' is not allowed"

          return True, None

typescript TypeScript
      const ALLOWED_COMMANDS = new Set([
        "ls",
        "cat",
        "echo",
        "pwd",
        "grep",
        "find",
        "wc",
        "head",
        "tail"
      ]);
      const SHELL_OPERATORS = new Set(["&&", "||", "|", ";", "&", ">", "<", ">>"]);

      function validateCommand(command: string): { ok: boolean; reason?: string } {
        // Split on whitespace: enough for a tripwire check
        const tokens = command.split(/\s+/).filter((token) => token.length > 0);
        if (tokens.length === 0) {
          return { ok: false, reason: "Empty command" };
        }

        // Allow only commands from an explicit allowlist
        const executable = tokens[0];
        if (!ALLOWED_COMMANDS.has(executable)) {
          return { ok: false, reason: `Command '${executable}' is not in the allowlist` };
        }

        // Reject shell operators written as separate words
        for (const token of tokens.slice(1)) {
          const bare = token.replace(/^["']+/, ""); // a quoted token can still smuggle an expansion
          if (SHELL_OPERATORS.has(token) || bare.startsWith("$") || bare.startsWith("`")) {
            return { ok: false, reason: `Shell operator '${token}' is not allowed` };
          }
        }

        return { ok: true };
      }

csharp C#
      var allowedCommands = new HashSet<string>
      {
          "ls", "cat", "echo", "pwd", "grep", "find", "wc", "head", "tail"
      };
      var shellOperators = new HashSet<string> { "&&", "||", "|", ";", "&", ">", "<", ">>" };

      (bool Ok, string? Reason) ValidateCommand(string command)
      {
          // Split on whitespace: enough for a tripwire check
          var tokens = command.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries);
          if (tokens.Length == 0)
          {
              return (false, "Empty command");
          }

          // Allow only commands from an explicit allowlist
          var executable = tokens[0];
          if (!allowedCommands.Contains(executable))
          {
              return (false, $"Command '{executable}' is not in the allowlist");
          }

          // Reject shell operators written as separate words
          foreach (var token in tokens.Skip(1))
          {
              var bare = token.TrimStart('"', '\''); // a quoted token can still smuggle an expansion
              if (shellOperators.Contains(token) || bare.StartsWith('$') || bare.StartsWith('`'))
              {
                  return (false, $"Shell operator '{token}' is not allowed");
              }
          }

          return (true, null);
      }

go Go
      var allowedCommands = map[string]bool{
      	"ls": true, "cat": true, "echo": true, "pwd": true, "grep": true,
      	"find": true, "wc": true, "head": true, "tail": true,
      }

      var shellOperators = map[string]bool{
      	"&&": true, "||": true, "|": true, ";": true, "&": true,
      	">": true, "<": true, ">>": true,
      }

      func validateCommand(command string) (bool, string) {
      	// Split on whitespace: enough for a tripwire check
      	tokens := strings.Fields(command)
      	if len(tokens) == 0 {
      		return false, "Empty command"
      	}

      	// Allow only commands from an explicit allowlist
      	executable := tokens[0]
      	if !allowedCommands[executable] {
      		return false, fmt.Sprintf("Command %q is not in the allowlist", executable)
      	}

      	// Reject shell operators written as separate words
      	for _, token := range tokens[1:] {
      		bare := strings.TrimLeft(token, `"'`) // a quoted token can still smuggle an expansion
      		if shellOperators[token] || strings.HasPrefix(bare, "$") || strings.HasPrefix(bare, "`") {
      			return false, fmt.Sprintf("Shell operator %q is not allowed", token)
      		}
      	}

      	return true, ""
      }

java Java
      import java.util.List;
      import java.util.Set;

      static final Set<String> ALLOWED_COMMANDS =
          Set.of("ls", "cat", "echo", "pwd", "grep", "find", "wc", "head", "tail");
      static final Set<String> SHELL_OPERATORS = Set.of("&&", "||", "|", ";", "&", ">", "<", ">>");

      record Validation(boolean ok, String reason) {}

      Validation validateCommand(String command) {
          // Split on whitespace: enough for a tripwire check
          List<String> tokens = List.of(command.trim().split("\\s+"));
          if (tokens.size() == 1 && tokens.get(0).isEmpty()) {
              return new Validation(false, "Empty command");
          }

          // Allow only commands from an explicit allowlist
          String executable = tokens.get(0);
          if (!ALLOWED_COMMANDS.contains(executable)) {
              return new Validation(false, "Command '" + executable + "' is not in the allowlist");
          }

          // Reject shell operators written as separate words
          for (String token : tokens.subList(1, tokens.size())) {
              String bare = token.replaceFirst("^[\"']+", ""); // a quoted token can still smuggle an expansion
              if (SHELL_OPERATORS.contains(token) || bare.startsWith("$") || bare.startsWith("`")) {
                  return new Validation(false, "Shell operator '" + token + "' is not allowed");
              }
          }

          return new Validation(true, null);
      }

php PHP
      const ALLOWED_COMMANDS = ['ls', 'cat', 'echo', 'pwd', 'grep', 'find', 'wc', 'head', 'tail'];
      const SHELL_OPERATORS = ['&&', '||', '|', ';', '&', '>', '<', '>>'];

      function validateCommand(string $command): array
      {
          // Split on whitespace: enough for a tripwire check
          $tokens = preg_split('/\\s+/', trim($command), -1, PREG_SPLIT_NO_EMPTY);
          if ($tokens === false || $tokens === []) {
              return [false, 'Empty command'];
          }

          // Allow only commands from an explicit allowlist
          $executable = $tokens[0];
          if (!in_array($executable, ALLOWED_COMMANDS, true)) {
              return [false, "Command '{$executable}' is not in the allowlist"];
          }

          // Reject shell operators written as separate words
          foreach (array_slice($tokens, 1) as $token) {
              $bare = ltrim($token, '"\''); // a quoted token can still smuggle an expansion
              if (in_array($token, SHELL_OPERATORS, true) || str_starts_with($bare, '$') || str_starts_with($bare, '`')) {
                  return [false, "Shell operator '{$token}' is not allowed"];
              }
          }

          return [true, null];
      }

ruby Ruby
      require "shellwords"

      ALLOWED_COMMANDS = %w[ls cat echo pwd grep find wc head tail].freeze
      SHELL_OPERATORS = ["&&", "||", "|", ";", "&", ">", "<", ">>"].freeze

      def validate_command(command)
        # Allow only commands from an explicit allowlist
        begin
          tokens = Shellwords.split(command)
        rescue ArgumentError
          return [false, "Could not parse command"]
        end

        return [false, "Empty command"] if tokens.empty?

        executable = tokens[0]
        unless ALLOWED_COMMANDS.include?(executable)
          return [false, "Command '#{executable}' is not in the allowlist"]
        end

        # Reject shell operators written as separate words
        tokens[1..].each do |token|
          if SHELL_OPERATORS.include?(token) || token.start_with?("$", "`")
            return [false, "Shell operator '#{token}' is not allowed"]
          end
        end

        [true, nil]
      end

json
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
          "content": "Error: command did not finish within 30 seconds",
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
          "content": "bash: nonexistentcommand: command not found",
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
          "content": "bash: /root/sensitive-file: Permission denied",
          "is_error": true
        }
      ]
    }

python Python
      import concurrent.futures
      import os
      import signal


      def execute_with_timeout(session, command, timeout=30):
          """Run a command in the session, replacing the session if the command hangs."""
          with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
              future = pool.submit(session.execute_command, command)
              try:
                  return future.result(timeout=timeout)
              except concurrent.futures.TimeoutError:
                  # The group is the shell and every process the command started
                  os.killpg(session.process.pid, signal.SIGKILL)
                  session.restart()
                  return f"Error: command did not finish within {timeout} seconds"

typescript TypeScript
      // Run a command in the session, replacing the session if the command hangs.
      async function executeWithTimeout(
        session: BashSession,
        command: string,
        timeoutMs = 30000
      ): Promise<string> {
        let timer: NodeJS.Timeout | undefined;
        const timedOut = new Promise<never>((_, reject) => {
          timer = setTimeout(() => reject(new Error("timeout")), timeoutMs);
        });
        try {
          return await Promise.race([session.executeCommand(command), timedOut]);
        } catch {
          // The group is the shell and every process the command started
          if (session.process.pid !== undefined) {
            process.kill(-session.process.pid, "SIGKILL");
          }
          session.restart();
          return `Error: command did not finish within ${timeoutMs / 1000} seconds`;
        } finally {
          clearTimeout(timer);
        }
      }

csharp C#
      using System.Diagnostics;

      // Run a command in the session, replacing the session if the command hangs.
      static string ExecuteWithTimeout(BashSession session, string command, int timeoutSeconds = 30)
      {
          var work = Task.Run(() => session.ExecuteCommand(command));
          if (work.Wait(TimeSpan.FromSeconds(timeoutSeconds)))
          {
              return work.Result;
          }

          // Stop the shell and every process it started, then start a fresh session
          session.Process.Kill(entireProcessTree: true);
          session.Restart();
          return $"Error: command did not finish within {timeoutSeconds} seconds";
      }

go Go
      // executeWithTimeout runs a command, replacing the session if the command hangs.
      func executeWithTimeout(session *BashSession, command string, timeoutSeconds int) string {
      	done := make(chan string, 1)
      	go func() { done <- session.ExecuteCommand(command) }()

      	select {
      	case result := <-done:
      		return result
      	case <-time.After(time.Duration(timeoutSeconds) * time.Second):
      		// The group is the shell and every process the command started
      		syscall.Kill(-session.cmd.Process.Pid, syscall.SIGKILL)
      		session.Restart()
      		return fmt.Sprintf("Error: command did not finish within %d seconds", timeoutSeconds)
      	}
      }

java Java
      // Run a command in the session, replacing the session if the command hangs.
      String executeWithTimeout(BashSession session, String command, int timeoutSeconds) throws Exception {
          ExecutorService pool = Executors.newSingleThreadExecutor();
          try {
              Future<String> future = pool.submit(() -> session.executeCommand(command));
              return future.get(timeoutSeconds, TimeUnit.SECONDS);
          } catch (TimeoutException e) {
              // Stop the shell and every process it started, then start a fresh session
              session.process.descendants().forEach(ProcessHandle::destroyForcibly);
              session.process.destroyForcibly();
              session.restart();
              return "Error: command did not finish within " + timeoutSeconds + " seconds";
          } finally {
              pool.shutdownNow();
          }
      }

php PHP
      // Run a command but give up if it does not finish within the deadline. PHP blocks on
      // pipe reads, so the deadline lives inside the read loop: stream_select() waits for
      // readable output before each fgets() so the loop can check the deadline.
      function executeWithTimeout(BashSession $session, string $command, int $timeout = 30): string
      {
          $sentinel = '__CLAUDE_BASH_DONE_' . bin2hex(random_bytes(16)) . '__'; // unique per call
          fwrite($session->stdin, "{$command}\necho {$sentinel}\n");
          fflush($session->stdin);

          $deadline = microtime(true) + $timeout;
          $output = '';
          while (microtime(true) < $deadline) {
              $read = [$session->output];
              $write = null;
              $except = null;
              if (stream_select($read, $write, $except, 1) === 0) {
                  continue; // no output yet; check the deadline again
              }
              $line = fgets($session->output);
              if ($line === false || str_contains($line, $sentinel)) {
                  return $output; // this command's output is complete
              }
              $output .= $line;
          }

          // The group is the shell and every process the command started
          posix_kill(-proc_get_status($session->process)['pid'], 9); // 9 = SIGKILL
          $session->restart();
          return "Error: command did not finish within {$timeout} seconds";
      }

ruby Ruby
      require "timeout"

      # Run a command in the session, replacing the session if the command hangs.
      def execute_with_timeout(session, command, timeout: 30)
        Timeout.timeout(timeout) { session.execute_command(command) }
      rescue Timeout::Error
        # The group is the shell and every process the command started
        Process.kill("KILL", -session.wait_thread.pid)
        session.restart
        "Error: command did not finish within #{timeout} seconds"
      end

python Python
      # Commands run in the same session maintain state
      commands = [
          "cd /tmp",
          "echo 'Hello' > test.txt",
          "cat test.txt",  # The session is still in /tmp
      ]

typescript TypeScript
      // Commands run in the same session maintain state
      const commands = [
        "cd /tmp",
        "echo 'Hello' > test.txt",
        "cat test.txt" // The session is still in /tmp
      ];

csharp C#
      // Commands run in the same session maintain state
      string[] commands =
      [
          "cd /tmp",
          "echo 'Hello' > test.txt",
          "cat test.txt", // The session is still in /tmp
      ];

go Go
      // Commands run in the same session maintain state
      commands := []string{
      	"cd /tmp",
      	"echo 'Hello' > test.txt",
      	"cat test.txt", // The session is still in /tmp
      }

java Java
      // Commands run in the same session maintain state
      List<String> commands = List.of(
          "cd /tmp",
          "echo 'Hello' > test.txt",
          "cat test.txt" // The session is still in /tmp
      );

php PHP
      // Commands run in the same session maintain state
      $commands = [
          'cd /tmp',
          "echo 'Hello' > test.txt",
          'cat test.txt', // The session is still in /tmp
      ];

ruby Ruby
      # Commands run in the same session maintain state
      commands = [
        "cd /tmp",
        "echo 'Hello' > test.txt",
        "cat test.txt" # The session is still in /tmp
      ]

python Python
      def truncate_output(output, max_lines=100):
          lines = output.split("\n")
          if len(lines) > max_lines:
              truncated = "\n".join(lines[:max_lines])
              return f"{truncated}\n\n... Output truncated ({len(lines)} total lines) ..."
          return output

typescript TypeScript
      function truncateOutput(output: string, maxLines = 100): string {
        const lines = output.split("\n");
        if (lines.length > maxLines) {
          const truncated = lines.slice(0, maxLines).join("\n");
          return `${truncated}\n\n... Output truncated (${lines.length} total lines) ...`;
        }
        return output;
      }

csharp C#
      string TruncateOutput(string output, int maxLines = 100)
      {
          var lines = output.Split('\n');
          if (lines.Length > maxLines)
          {
              var truncated = string.Join("\n", lines.Take(maxLines));
              return $"{truncated}\n\n... Output truncated ({lines.Length} total lines) ...";
          }
          return output;
      }

go Go
      func truncateOutput(output string, maxLines int) string {
      	lines := strings.Split(output, "\n")
      	if len(lines) > maxLines {
      		truncated := strings.Join(lines[:maxLines], "\n")
      		return fmt.Sprintf("%s\n\n... Output truncated (%d total lines) ...", truncated, len(lines))
      	}
      	return output
      }

java Java
      String truncateOutput(String output, int maxLines) {
          String[] lines = output.split("\n", -1);
          if (lines.length > maxLines) {
              String truncated = String.join("\n", Arrays.copyOf(lines, maxLines));
              return truncated + "\n\n... Output truncated (" + lines.length + " total lines) ...";
          }
          return output;
      }

php PHP
      function truncateOutput(string $output, int $maxLines = 100): string
      {
          $lines = explode("\n", $output);
          if (count($lines) > $maxLines) {
              $truncated = implode("\n", array_slice($lines, 0, $maxLines));
              return "{$truncated}\n\n... Output truncated (" . count($lines) . ' total lines) ...';
          }
          return $output;
      }

ruby Ruby
      def truncate_output(output, max_lines: 100)
        lines = output.split("\n", -1)
        return output unless lines.length > max_lines

        truncated = lines.first(max_lines).join("\n")
        "#{truncated}\n\n... Output truncated (#{lines.length} total lines) ..."
      end

python Python
      import logging

      logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


      def execute_and_log(session, command):
          """Run a command in the session and keep an audit record of it."""
          logging.info("command=%r", command)
          output = session.execute_command(command)
          logging.info("output=%r", output[:200])  # first 200 characters
          return output

typescript TypeScript
      // Run a command in the session and keep an audit record of it.
      async function executeAndLog(session: BashSession, command: string): Promise<string> {
        console.error(`command=${JSON.stringify(command)}`);
        const output = await session.executeCommand(command);
        console.error(`output=${JSON.stringify(output.slice(0, 200))}`); // first 200 characters
        return output;
      }

csharp C#
      // Run a command in the session and keep an audit record of it.
      static string ExecuteAndLog(BashSession session, string command)
      {
          Console.Error.WriteLine($"command={command}");
          var output = session.ExecuteCommand(command);
          Console.Error.WriteLine($"output={output[..Math.Min(output.Length, 200)]}"); // first 200 characters
          return output;
      }

go Go
      // executeAndLog runs a command in the session and keeps an audit record of it.
      func executeAndLog(session *BashSession, command string) string {
      	log.Printf("command=%q", command)
      	output := session.ExecuteCommand(command)
      	log.Printf("output=%q", output[:min(len(output), 200)]) // first 200 characters
      	return output
      }

java Java
      static final Logger AUDIT = Logger.getLogger("bash-audit");

      // Run a command in the session and keep an audit record of it.
      String executeAndLog(BashSession session, String command) throws IOException {
          AUDIT.info("command=" + command);
          String output = session.executeCommand(command);
          AUDIT.info("output=" + output.substring(0, Math.min(output.length(), 200))); // first 200 characters
          return output;
      }

php PHP
      // Run a command in the session and keep an audit record of it.
      function executeAndLog(BashSession $session, string $command): string
      {
          error_log("command={$command}");
          $output = $session->executeCommand($command);
          error_log('output=' . substr($output, 0, 200)); // first 200 characters
          return $output;
      }

ruby Ruby
      require "logger"

      AUDIT = Logger.new($stderr)

      # Run a command in the session and keep an audit record of it.
      def execute_and_log(session, command)
        AUDIT.info("command=#{command.inspect}")
        output = session.execute_command(command)
        AUDIT.info("output=#{output[0, 200].inspect}") # first 200 characters
        output
      end
      ```
    </CodeGroup>

    The records go to `stderr` by default; point them at a file or your logging pipeline to keep them. Include whatever ties the record to the request in your application, such as the end user and the `tool_use_id`.
  </Accordion>
</AccordionGroup>


## Security

Source: https://platform.claude.com/llms-full.txt#security

<Warning>
  Your application runs whatever command Claude requests. Run the session in an isolated environment, such as a container or a virtual machine, as the least-privileged user that can do the work. Treat every command as untrusted input.
</Warning>

Beyond isolation, add these controls:

* Validate commands before running them, with an allowlist rather than a blocklist. See [Implement the bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool#implement-the-bash-tool).
* Set resource limits on the shell process (CPU, memory, and disk), for example with `ulimit`.
* Log every command and its output so you can audit what ran.
* Redact credentials and other secrets from output before returning it to Claude.


## Pricing

Source: https://platform.claude.com/llms-full.txt#pricing-6

The bash tool definition adds the following input tokens to your request. This is in addition to the per-model [tool use system prompt](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview#pricing) that applies whenever any tool is present.

| Model                                               | Additional input tokens |
| --------------------------------------------------- | ----------------------- |
| Claude Opus 5, Claude Opus 4.8, and Claude Opus 4.7 | 325 tokens              |
| Claude Opus 4.6, Claude Sonnet 4.6, and earlier     | 244 tokens              |

Additional tokens are consumed by:

* Command outputs (stdout/stderr)
* Error messages
* Large file contents

See [tool use pricing](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview#pricing) for complete pricing details.


## Common patterns

Source: https://platform.claude.com/llms-full.txt#common-patterns-2

### Development workflows

* Running tests: `pytest && coverage report`
* Building projects: `npm install && npm run build`
* Git operations: `git status && git add . && git commit -m "message"`

For guidance on using git as a checkpoint-and-recovery mechanism in long-running agent workflows, see [state management best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#state-management-best-practices).

### File operations

* Processing data: `wc -l *.csv && ls -lh *.csv`
* Searching files: `find . -name "*.py" | xargs grep "pattern"`
* Creating backups: `tar -czf backup.tar.gz ./data`

### System tasks

* Checking resources: `df -h && free -m`
* Process management: `ps aux | grep python`
* Environment setup: `export PATH=$PATH:/new/path && echo $PATH`


## Limitations

Source: https://platform.claude.com/llms-full.txt#limitations-2

* **No interactive commands:** The session can't run `vim`, `less`, password prompts, or any command that waits for input on stdin.
* **No GUI applications:** The session is command-line only.
* **Session scope:** Bash session state is client-side. Your application is responsible for maintaining the shell session between turns.
* **Output limits:** The API doesn't truncate tool results (an oversized request is rejected). Truncate large outputs in your application before returning them to Claude.
* **No streaming:** Output reaches Claude only when your application returns the `tool_result` in the next request.


## Combining with other tools

Source: https://platform.claude.com/llms-full.txt#combining-with-other-tools-2

The bash tool pairs well with the [Text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool): Claude edits a file with one tool and requests the command that runs it with the other.

<Note>
  If you're also using the [Code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool), Claude has access to two separate execution environments: your local bash session and Anthropic's sandboxed container. State is not shared between them. See [Using code execution with other execution tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#using-code-execution-with-other-execution-tools) for guidance on prompting Claude to distinguish between environments.
</Note>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-25

<CardGroup cols={2}>
  <Card title="Text editor tool" icon="file" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool">
    View and modify text files to debug, fix, and improve code.
  </Card>

  <Card title="Tool use with Claude" icon="tool" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview">
    Connect Claude to external tools and APIs. See where tools execute, when Claude calls them, and which tool fits your task.
  </Card>
</CardGroup>


---
title: Browser use tool
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool
description: Let Claude navigate, read, and interact with webpages in your own browser environment with the browser use tool.
---


## Compatibility

Source: https://platform.claude.com/llms-full.txt#compatibility-5

- [ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): eligible (excludes [Covered Models](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements))
- Supported models: `claude-fable-5-1`, `claude-mythos-5-1`, `claude-fable-5`, `claude-mythos-5`, `claude-opus-5`, `claude-sonnet-5`, `claude-opus-4-8`
- Platforms: Claude API, Google Cloud; not available on Claude Platform on AWS, Amazon Bedrock, Microsoft Foundry

The browser use tool lets Claude navigate, read, and interact with webpages in a browser that your application runs. It works with the page both through its structure (the accessibility tree, elements, forms, and tabs) and through pixels (screenshots and viewport coordinates), whereas the [computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) works with a whole desktop through screenshots and coordinates alone. It's an Anthropic-defined [client toolset](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets): one `browser_toolset_20260801` entry in your `tools` array gives Claude 27 member tools by default, such as `navigate`, `read_page`, `left_click`, and `screenshot`, plus four more (`javascript_exec`, `file_upload`, `read_console`, and `read_network`) when you [enable them](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#enable-optional-member-tools). Your application runs every call against its own browser automation; nothing runs on Anthropic's side. It isn't currently available in [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/tools). This page says "your application" for the agent loop that calls the Messages API and "your executor" for the part of it that drives the browser and produces tool results.

Choose browser use over computer use when the task stays inside webpages: Claude can read a page's structure, act on an element by reference in addition to by coordinate, set form values directly, and work across tabs, and you don't need to run a desktop. If Claude only needs to read pages you can point it to, or to find sources on the web, the [web fetch tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) and [web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) are lighter still, because they're [server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools) that the API runs for you with no browser to operate. Choose browser use instead when pages build their content with JavaScript or the task means acting on the page rather than only reading it.

With browser use, Claude reads and acts on live webpages, so everything a page supplies is untrusted input and the actions Claude takes can have real effects. See [Security considerations](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#security-considerations) before you deploy.


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-3

The browser use tool is available on the Claude API and [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai): add one entry of type `browser_toolset_20260801`, with no `name`, to the `tools` array of a [Messages API](https://platform.claude.com/docs/en/api/messages/create) request.

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 2048,
      "tools": [
        {
          "type": "browser_toolset_20260801"
        }
      ],
      "messages": [
        {
          "role": "user",
          "content": "Open example.com/docs and tell me how to get started."
        }
      ]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 2048
  tools:
    - type: browser_toolset_20260801
  messages:
    - role: user
      content: Open example.com/docs and tell me how to get started.
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=2048,
      tools=[{"type": "browser_toolset_20260801"}],
      messages=[
          {
              "role": "user",
              "content": "Open example.com/docs and tell me how to get started.",
          }
      ],
  )
  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 2048,
    tools: [{ type: "browser_toolset_20260801" }],
    messages: [
      {
        role: "user",
        content: "Open example.com/docs and tell me how to get started."
      }
    ]
  });

  console.log(response);

csharp C#
  var client = new AnthropicClient();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 2048,
      Tools = [new BrowserToolset20260801()],
      Messages =
      [
          new MessageParam
          {
              Role = Role.User,
              Content = "Open example.com/docs and tell me how to get started.",
          },
      ],
  };

  var response = await client.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 2048,
  	Tools: []anthropic.ToolUnionParam{
  		{OfBrowserToolset20260801: &anthropic.BrowserToolset20260801Param{}},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Open example.com/docs and tell me how to get started.")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  import com.anthropic.models.messages.BrowserToolset20260801;
  // ...

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(2048L)
          .addTool(BrowserToolset20260801.builder().build())
          .addUserMessage("Open example.com/docs and tell me how to get started.")
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $response = $client->messages->create(
      maxTokens: 2048,
      messages: [
          ['role' => 'user', 'content' => 'Open example.com/docs and tell me how to get started.'],
      ],
      model: 'claude-opus-5',
      tools: [
          ['type' => 'browser_toolset_20260801'],
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 2048,
    tools: [
      { type: "browser_toolset_20260801" }
    ],
    messages: [
      {
        role: "user",
        content: "Open example.com/docs and tell me how to get started."
      }
    ]
  )

  puts response

json Output
{
  "id": "msg_01HCDu4XSTLzTAcodEQ58vDo",
  "type": "message",
  "role": "assistant",
  "model": "claude-opus-5",
  "content": [
    {
      "type": "text",
      "text": "I'll open the documentation and read the page to find the getting-started instructions."
    },
    {
      "type": "tool_use",
      "id": "toolu_01NRLabsLyVHZPKxbKvkfSMn",
      "name": "navigate",
      "toolset_name": "browser",
      "input": { "url": "https://example.com/docs" }
    },
    {
      "type": "tool_use",
      "id": "toolu_01UvHU5cDyTZ2vXKf5wCkPqR",
      "name": "read_page",
      "toolset_name": "browser",
      "input": { "filter": "interactive" }
    }
  ],
  "stop_reason": "tool_use",
  "stop_sequence": null
}

json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01NRLabsLyVHZPKxbKvkfSMn",
      "toolset_name": "browser",
      "content": [
        { "type": "text", "text": "Navigated to https://example.com/docs" },
        {
          "type": "browser_state",
          "tabs": [
            {
              "tab_id": "tab-1",
              "title": "Documentation",
              "url": "https://example.com/docs",
              "active": true
            }
          ]
        }
      ]
    },
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01UvHU5cDyTZ2vXKf5wCkPqR",
      "toolset_name": "browser",
      "content": [
        {
          "type": "text",
          "text": "link \"Documentation\" [ref_1]\nlink \"Getting started\" [ref_2]\ntextbox \"Search docs\" [ref_3]\nbutton \"Search\" [ref_4]\nlink \"Pricing\" [ref_5]"
        }
      ]
    }
  ]
}
```

Claude now holds references it can act on, so its next turn can click `ref_2` to open the getting-started page, with no need to locate the link in a screenshot first.


## How browser use works

Source: https://platform.claude.com/llms-full.txt#how-browser-use-works

Browser use runs as an agent loop: Claude returns member tool calls, your executor runs them against the browser, and you return the results until Claude answers in text.

<Steps>
  <Step title="Provide Claude with the browser use tool and a user prompt" icon="tool">
    * Add the `browser_toolset_20260801` entry, and optionally other tools, to your API request.
    * Include a user prompt that calls for working with webpages, for example, "Open example.com/docs and tell me how to get started."
  </Step>

  <Step title="Claude responds with member tool calls" icon="wrench">
    * Claude returns one or more `tool_use` blocks in a single assistant turn; several in one turn form a batch action, for example, `left_click`, then `type`, then `key`.
    * Each block's `name` is the member name, each carries `"toolset_name": "browser"`, and `input` holds only that member's parameters, with no `action` field. The response's `stop_reason` is `tool_use`.
  </Step>

  <Step title="Run the calls in order and return results" icon="browser">
    * Iterate every `tool_use` block in `response.content` (don't assume there's exactly one) and run them sequentially, in the order they appear, because later calls usually depend on earlier ones.
    * Return one `tool_result` per block in a new `user` message, matched by `tool_use_id`, and echo `"toolset_name": "browser"` on each. Every call must be answered or the next request is rejected.
    * If a call fails, return `is_error: true` with a text description for that block, then apply the halt rule in [Batch actions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#batch-actions) to every later block in the turn.
  </Step>

  <Step title="Claude continues until the task is complete" icon="arrows-clockwise">
    * Claude reads the results (page text, accessibility trees, screenshots, tab state) and, if it needs more, returns further member calls, which takes you back to step 3.
    * Otherwise, it returns a text response to the user.
  </Step>
</Steps>

Here's a skeleton of that loop's tool-call step in two parts. First, stub member handlers stand in for your browser automation. Five members (`navigate`, `read_page`, `left_click`, `type`, and `screenshot`) return the text, or for `screenshot` the image block, that becomes the result content, and the dispatcher raises an error for any member it doesn't implement.

<CodeGroup exclude="shell">
  ```python Python
  # Placeholder image data; a real executor captures the viewport and returns the PNG bytes
  PLACEHOLDER_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="


  def navigate(url):
      return f"navigated to {url}"


  def read_page():
      return 'link "Docs" [ref_1]\nbutton "Search" [ref_2]'


  def click(target):
      # A target is an element reference from read_page or find, or a viewport coordinate
      if target["type"] == "ref":
          return f"clicked {target['ref']}"
      return f"clicked at ({target['x']}, {target['y']})"


  def type_text(text):
      return f"typed: {text}"


  def capture_screenshot() -> list[ImageBlockParam]:
      # screenshot answers with an image block rather than text: return the result content list
      return [
          {
              "type": "image",
              "source": {"type": "base64", "media_type": "image/png", "data": PLACEHOLDER_PNG},
          }
      ]


  def handle_browser_action(name, tool_input):
      if name == "navigate":
          return navigate(tool_input["url"])
      elif name == "read_page":
          return read_page()
      elif name == "left_click":
          return click(tool_input["target"])
      elif name == "type":
          return type_text(tool_input["text"])
      elif name == "screenshot":
          return capture_screenshot()
      # Handle other actions as needed
      raise ValueError(f"Unknown or unimplemented member: {name}")

typescript TypeScript
  // Placeholder image data; a real executor captures the viewport as PNG bytes
  const PLACEHOLDER_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

  function navigate(url: string): string {
    return `navigated to ${url}`;
  }

  function readPage(): string {
    return 'link "Docs" [ref_1]\nbutton "Search" [ref_2]';
  }

  function clickElement(ref: string): string {
    return `clicked ${ref}`;
  }

  function clickAt(x: number, y: number): string {
    return `clicked at (${x}, ${y})`;
  }

  function typeText(text: string): string {
    return `typed: ${text}`;
  }

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

  function handleBrowserAction(
    action: string,
    input: unknown,
  ): string | Anthropic.ImageBlockParam[] {
    const params: object =
      typeof input === "object" && input !== null ? input : {};
    if (action === "navigate" && "url" in params) {
      return navigate(String(params.url));
    } else if (action === "read_page") {
      return readPage();
    } else if (action === "left_click" && "target" in params) {
      // target is an element reference from read_page or a viewport coordinate
      const target: object =
        typeof params.target === "object" && params.target !== null
          ? params.target
          : {};
      if ("type" in target && target.type === "ref" && "ref" in target) {
        return clickElement(String(target.ref));
      } else if ("x" in target && "y" in target) {
        return clickAt(Number(target.x), Number(target.y));
      }
    } else if (action === "type" && "text" in params) {
      return typeText(String(params.text));
    } else if (action === "screenshot") {
      return captureScreenshot();
    }
    // Handle other actions as needed
    throw new Error(`Unknown or unimplemented member: ${action}`);
  }

csharp C#
  // Placeholder image data; a real executor captures the viewport and returns the PNG bytes
  const string PlaceholderPng = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

  string Navigate(string url) => $"navigated to {url}";

  string ReadPage() =>
      """
      link "Docs" [ref_1]
      button "Search" [ref_2]
      """;

  string ClickRef(string elementRef) => $"clicked {elementRef}";

  string ClickAt(int x, int y) => $"clicked at ({x}, {y})";

  // target is {"type": "ref", "ref": "ref_1"} or {"type": "coordinate", "x": 640, "y": 380}
  string Click(JsonElement target) =>
      target.GetProperty("type").GetString() == "ref"
          ? ClickRef(target.GetProperty("ref").GetString()!)
          : ClickAt(target.GetProperty("x").GetInt32(), target.GetProperty("y").GetInt32());

  string TypeText(string text) => $"typed: {text}";

  // screenshot answers with an image block rather than text: return the result content list
  List<Block> CaptureScreenshot() =>
      [
          new ImageBlockParam(
              new Base64ImageSource { Data = PlaceholderPng, MediaType = MediaType.ImagePng }
          ),
      ];

  ToolResultBlockParamContent HandleBrowserAction(
      string action,
      IReadOnlyDictionary<string, JsonElement> input
  ) =>
      action switch
      {
          "navigate" => Navigate(input["url"].GetString()!),
          "read_page" => ReadPage(),
          "left_click" => Click(input["target"]),
          "type" => TypeText(input["text"].GetString()!),
          "screenshot" => CaptureScreenshot(),
          // Handle other actions as needed
          _ => throw new NotSupportedException($"Unknown or unimplemented member: {action}"),
      };

go Go
  // placeholderPNG stands in for a real capture: an executor returns the
  // viewport as base64-encoded PNG data.
  const placeholderPNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

  // textContent wraps text as tool_result content.
  func textContent(text string) []anthropic.ToolResultBlockParamContentUnion {
  	return []anthropic.ToolResultBlockParamContentUnion{
  		{OfText: &anthropic.TextBlockParam{Text: text}},
  	}
  }

  func navigate(url string) string {
  	return fmt.Sprintf("navigated to %s", url)
  }

  func readPage() string {
  	return "link \"Docs\" [ref_1]\nbutton \"Search\" [ref_2]"
  }

  func clickRef(ref string) string {
  	return fmt.Sprintf("clicked %s", ref)
  }

  func clickAt(x, y int) string {
  	return fmt.Sprintf("clicked at (%d, %d)", x, y)
  }

  func typeText(text string) string {
  	return fmt.Sprintf("typed: %s", text)
  }

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

  func handleBrowserAction(action string, params map[string]any) ([]anthropic.ToolResultBlockParamContentUnion, error) {
  	switch action {
  	case "navigate":
  		if url, ok := params["url"].(string); ok {
  			return textContent(navigate(url)), nil
  		}
  	case "read_page":
  		return textContent(readPage()), nil
  	case "left_click":
  		// target is either an element reference from read_page or a viewport coordinate
  		target, _ := params["target"].(map[string]any)
  		if ref, ok := target["ref"].(string); ok && target["type"] == "ref" {
  			return textContent(clickRef(ref)), nil
  		}
  		x, xok := target["x"].(float64)
  		y, yok := target["y"].(float64)
  		if xok && yok {
  			return textContent(clickAt(int(x), int(y))), nil
  		}
  	case "type":
  		if text, ok := params["text"].(string); ok {
  			return textContent(typeText(text)), nil
  		}
  	case "screenshot":
  		return captureScreenshot(), nil
  	// Handle other actions as needed
  	default:
  		return nil, fmt.Errorf("unknown or unimplemented member: %s", action)
  	}
  	// Reached when a member's input is missing a field or a field has the wrong type
  	return nil, fmt.Errorf("invalid input for %s", action)
  }

java Java
  /** Placeholder pixels; a real executor captures the viewport and base64-encodes the PNG. */
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

  String navigate(String url) {
      return "navigated to " + url;
  }

  String readPage() {
      return """
              link "Docs" [ref_1]
              button "Search" [ref_2]""";
  }

  String clickRef(String ref) {
      return "clicked " + ref;
  }

  String clickAt(long x, long y) {
      return "clicked at (" + x + ", " + y + ")";
  }

  String typeText(String text) {
      return "typed: " + text;
  }

  /** Runs one browser toolset member; {@code action} is the tool_use block's name. */
  ToolResultBlockParam.Content handleBrowserAction(String action, Map<String, JsonValue> input) {
      if (action.equals("screenshot")) {
          return captureScreenshot(); // the one member here that answers with an image block
      }
      String output = switch (action) {
          case "navigate" -> navigate(input.get("url").asStringOrThrow());
          case "read_page" -> readPage();
          case "left_click" -> {
              // target is {"type": "ref", "ref": "ref_1"} or {"type": "coordinate", "x": 640, "y": 380}
              Map<String, JsonValue> target =
                      (Map<String, JsonValue>) input.get("target").asObject().get();
              if (target.get("type").asStringOrThrow().equals("ref")) {
                  yield clickRef(target.get("ref").asStringOrThrow());
              }
              long x = ((Number) target.get("x").asNumber().get()).longValue();
              long y = ((Number) target.get("y").asNumber().get()).longValue();
              yield clickAt(x, y);
          }
          case "type" -> typeText(input.get("text").asStringOrThrow());
          // Handle other actions as needed
          default -> throw new UnsupportedOperationException("Unknown or unimplemented member: " + action);
      };
      return ToolResultBlockParam.Content.ofString(output);
  }

php PHP
  // Stand-in for real PNG bytes; a real executor captures the viewport
  const PLACEHOLDER_PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';

  function navigateTo(string $url): string
  {
      return "navigated to {$url}";
  }

  function readPage(): string
  {
      return <<<'TEXT'
          link "Docs" [ref_1]
          button "Search" [ref_2]
          TEXT;
  }

  function clickTarget(array $target): string
  {
      // A target is an element reference from read_page or find, or a viewport pixel coordinate
      if ($target['type'] === 'ref') {
          return "clicked {$target['ref']}";
      }

      return "clicked at ({$target['x']}, {$target['y']})";
  }

  function typeText(string $text): string
  {
      return "typed: {$text}";
  }

  function captureScreenshot(): array
  {
      // screenshot answers with an image block rather than text, so return the result content list
      $image = [
          'type' => 'image',
          'source' => ['type' => 'base64', 'media_type' => 'image/png', 'data' => PLACEHOLDER_PNG],
      ];

      return [$image];
  }

  function handleBrowserAction(string $name, array $input): string|array
  {
      return match ($name) {
          'navigate' => navigateTo($input['url']),
          'read_page' => readPage(),
          'left_click' => clickTarget($input['target']),
          'type' => typeText($input['text']),
          'screenshot' => captureScreenshot(),
          // Handle other actions as needed
          default => throw new RuntimeException("Unknown or unimplemented member: {$name}"),
      };
  }

ruby Ruby
  # Stand-in image data; a real executor captures the viewport as a PNG.
  PLACEHOLDER_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

  def navigate(url)
    "navigated to #{url}"
  end

  def read_page
    <<~TREE
      link "Docs" [ref_1]
      button "Search" [ref_2]
    TREE
  end

  def click(target)
    return "clicked #{target[:ref]}" if target[:type] == "ref"

    "clicked at (#{target[:x]}, #{target[:y]})"
  end

  def type_text(text)
    "typed: #{text}"
  end

  def capture_screenshot
    [
      {
        type: "image",
        source: { type: "base64", media_type: "image/png", data: PLACEHOLDER_PNG }
      }
    ]
  end

  def handle_browser_action(name, input)
    case name
    when "navigate"
      navigate(input[:url])
    when "read_page"
      read_page
    when "left_click"
      # target is an element reference (from read_page or find) or a coordinate
      click(input[:target])
    when "type"
      type_text(input[:text])
    when "screenshot"
      capture_screenshot
    # Handle other actions as needed
    else
      raise ArgumentError, "Unknown or unimplemented member: #{name}"
    end
  end

python Python
  NOT_EXECUTED = "Not executed: an earlier action in this turn failed."


  def process_tool_calls(response: Message) -> list[ToolResultBlockParam]:
      """
      Run the browser actions in Claude's response in order and answer each
      one. After the first failure the rest are skipped, because Claude planned
      them assuming the earlier actions succeeded.
      """
      tool_results: list[ToolResultBlockParam] = []
      failed = False
      for block in response.content:
          # Only the browser toolset is declared; route other tools here if you add them
          if block.type != "tool_use" or block.toolset_name != "browser":
              continue
          result: ToolResultBlockParam = {
              "type": "tool_result",
              "tool_use_id": block.id,
              "toolset_name": "browser",
          }
          if failed:
              result["content"] = NOT_EXECUTED
              result["is_error"] = True
          else:
              try:
                  # A string or a list of content blocks; a real executor also adds a
                  # browser_state block to navigation and tab-management results
                  result["content"] = handle_browser_action(block.name, block.input)
              except Exception as err:
                  result["content"] = f"Error: {err}"
                  result["is_error"] = True
                  failed = True
          tool_results.append(result)
      return tool_results

typescript TypeScript
  const HALT_TEXT = "Not executed: an earlier action in this turn failed.";

  function browserResult(
    toolUseId: string,
    content: string | Anthropic.ImageBlockParam[],
    isError?: boolean,
  ): Anthropic.ToolResultBlockParam {
    return {
      type: "tool_result",
      tool_use_id: toolUseId,
      toolset_name: "browser",
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
      if (block.toolset_name !== "browser") {
        // This example declares only the browser toolset; route other tools
        // here if you add them.
        continue;
      }
      if (failed) {
        // A batch stops at its first failure; answer later actions unexecuted
        toolResults.push(browserResult(block.id, HALT_TEXT, true));
        continue;
      }
      try {
        // A string or an image block list; a real executor also adds a
        // browser_state block to navigation and tab-management results
        const result = handleBrowserAction(block.name, block.input);
        toolResults.push(browserResult(block.id, result));
      } catch (error) {
        failed = true;
        const message = error instanceof Error ? error.message : String(error);
        toolResults.push(browserResult(block.id, `Error: ${message}`, true));
      }
    }
    return toolResults;
  }

csharp C#
  const string HaltText = "Not executed: an earlier action in this turn failed.";

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

          if (toolUse.ToolsetName != "browser")
          {
              // This example declares only the browser toolset; route other tools
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
                      ToolsetName = "browser",
                  }
              );
              continue;
          }

          try
          {
              // A string or a list of content blocks; a real executor also adds a
              // browser_state block to navigation and tab-management results
              var result = HandleBrowserAction(toolUse.Name, toolUse.Input);
              toolResults.Add(
                  new ToolResultBlockParam(toolUse.ID) { Content = result, ToolsetName = "browser" }
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
                      ToolsetName = "browser",
                  }
              );
          }
      }
      return toolResults;
  }

go Go
  const notExecuted = "Not executed: an earlier action in this turn failed."

  // browserToolResult builds the result for one browser action. Unlike an
  // ordinary tool result, it must echo the toolset name. A real executor also
  // adds a browser_state block to navigation and tab-management results.
  func browserToolResult(toolUseID string, content []anthropic.ToolResultBlockParamContentUnion, isError bool) anthropic.ContentBlockParamUnion {
  	result := anthropic.ToolResultBlockParam{
  		ToolUseID:   toolUseID,
  		ToolsetName: anthropic.String("browser"),
  		Content:     content,
  	}
  	if isError {
  		result.IsError = anthropic.Bool(true)
  	}
  	return anthropic.ContentBlockParamUnion{OfToolResult: &result}
  }

  // processToolCalls runs the browser actions in Claude's response in order and
  // builds one tool_result per tool_use block. After the first failure it skips
  // the rest: Claude planned them assuming the earlier actions succeeded.
  func processToolCalls(response *anthropic.Message) []anthropic.ContentBlockParamUnion {
  	var toolResults []anthropic.ContentBlockParamUnion
  	failed := false
  	for _, block := range response.Content {
  		switch variant := block.AsAny().(type) {
  		case anthropic.ToolUseBlock:
  			// This example declares only the browser toolset; route other tools here if you add them.
  			if variant.ToolsetName != "browser" {
  				continue
  			}
  			if failed {
  				toolResults = append(toolResults, browserToolResult(variant.ID, textContent(notExecuted), true))
  				continue
  			}
  			var input map[string]any
  			var content []anthropic.ToolResultBlockParamContentUnion
  			err := json.Unmarshal(variant.Input, &input)
  			if err == nil {
  				content, err = handleBrowserAction(variant.Name, input)
  			}
  			if err != nil {
  				failed = true
  				content = textContent("Error: " + err.Error())
  			}
  			toolResults = append(toolResults, browserToolResult(variant.ID, content, err != nil))
  		}
  	}
  	return toolResults
  }

java Java
  /** The exact text the toolset contract prescribes for member calls skipped after a failure. */
  static final String HALT_TEXT = "Not executed: an earlier action in this turn failed.";

  /** Every result answering a browser toolset member echoes toolset_name. */
  ToolResultBlockParam.Builder browserResult(ToolUseBlock toolUse) {
      return ToolResultBlockParam.builder()
              .toolUseId(toolUse.id())
              .toolsetName("browser");
  }

  /**
   * Run the browser actions in Claude's response in order and build one
   * tool_result per tool_use block. After the first failure, skip the rest:
   * Claude planned them assuming the earlier actions succeeded.
   */
  List<ContentBlockParam> processToolCalls(Message response) {
      List<ContentBlockParam> toolResults = new ArrayList<>();
      boolean failed = false;
      for (ContentBlock block : response.content()) {
          // This example declares only the browser toolset; route other tools here if you add them.
          if (!block.isToolUse() || !block.asToolUse().toolsetName().equals(Optional.of("browser"))) {
              continue;
          }
          ToolUseBlock toolUse = block.asToolUse();
          ToolResultBlockParam result;
          if (failed) {
              result = browserResult(toolUse).content(HALT_TEXT).isError(true).build();
          } else {
              try {
                  Map<String, JsonValue> input =
                          (Map<String, JsonValue>) toolUse._input().asObject().get();
                  ToolResultBlockParam.Content output = handleBrowserAction(toolUse.name(), input);
                  // A real executor also adds a browser_state block to navigation and
                  // tab-management results; see "Track tabs with browser_state" on this page.
                  result = browserResult(toolUse).content(output).build();
              } catch (RuntimeException e) {
                  failed = true;
                  result = browserResult(toolUse).content("Error: " + e.getMessage()).isError(true).build();
              }
          }
          toolResults.add(ContentBlockParam.ofToolResult(result));
      }
      return toolResults;
  }

php PHP
  const HALT_TEXT = 'Not executed: an earlier action in this turn failed.';

  function processToolCalls(Message $response): array
  {
      $toolResults = [];
      $failed = false;
      foreach ($response->content as $block) {
          // This example declares only the browser toolset; route other tools here if you add them.
          if (!($block instanceof ToolUseBlock) || $block->toolsetName !== 'browser') {
              continue;
          }
          $result = ['type' => 'tool_result', 'tool_use_id' => $block->id, 'toolset_name' => 'browser'];
          if ($failed) {
              // A batch stops at its first failure; the remaining actions are answered without running
              $toolResults[] = [...$result, 'content' => HALT_TEXT, 'is_error' => true];
              continue;
          }
          try {
              // A real executor also returns a browser_state block on navigation and tab-management results
              $toolResults[] = [...$result, 'content' => handleBrowserAction($block->name, $block->input)];
          } catch (Throwable $e) {
              $failed = true;
              $toolResults[] = [...$result, 'content' => 'Error: ' . $e->getMessage(), 'is_error' => true];
          }
      }

      return $toolResults;
  }

ruby Ruby
  NOT_EXECUTED = "Not executed: an earlier action in this turn failed."

  # Run the browser actions in Claude's response in order and build one
  # tool_result per tool_use block. After the first failure, skip the rest:
  # Claude planned them assuming the earlier actions succeeded.
  def process_tool_calls(response)
    tool_results = []
    failed = false
    response.content.each do |block|
      # This example declares only the browser toolset; route other tools here
      # if you add them.
      next unless block.type == :tool_use && block.toolset_name == "browser"

      result = { type: "tool_result", tool_use_id: block.id, toolset_name: "browser" }
      if failed
        result.update(content: NOT_EXECUTED, is_error: true)
      else
        begin
          # A String, or content blocks for a screenshot. A real executor also adds
          # a browser_state block to navigation and tab-management results.
          result[:content] = handle_browser_action(block.name, block.input)
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
  "role": "assistant",
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
      "name": "left_click",
      "toolset_name": "browser",
      "input": { "target": { "type": "ref", "ref": "ref_3" } }
    },
    {
      "type": "tool_use",
      "id": "toolu_01Ez4kLb1nQ2vXo8sJ9pWm3c",
      "name": "type",
      "toolset_name": "browser",
      "input": { "text": "install" }
    },
    {
      "type": "tool_use",
      "id": "toolu_01FkP8rTz6uYh2mNq4LsXw7v",
      "name": "key",
      "toolset_name": "browser",
      "input": { "text": "Enter" }
    }
  ]
}

text wrap
link "Documentation" [ref_1]
link "Getting started" [ref_2]
textbox "Search docs" [ref_3]
button "Search" [ref_4]
link "Pricing" [ref_5]
```

Claude passes a reference back as a `{"type": "ref", "ref": "ref_2"}` target on a later click, `hover`, `scroll_to`, `form_input`, or `file_upload` call, or as the `ref` parameter on `read_page` to read a subtree. Your executor assigns the references, keeps the mapping from each one to the underlying node (an accessibility-node ID, a stored selector, or equivalent), and acts on that node when a reference comes back.

References are scoped to the tab that produced them and stay valid until that tab navigates or its DOM changes materially. The API can't detect a stale or unknown reference, so when Claude passes a reference your executor no longer recognizes, return an error result such as `Error: ref_3 is stale or not found on the current page. Re-read the page to get fresh references.` Claude then reads the page again. Don't renumber references you've already handed out for a tab until it navigates, because that silently invalidates references Claude still holds.

Claude uses both targeting styles and switches between them based on what the page exposes; your prompt and what your executor returns steer the choice:

* **Prefer references where the page has a usable accessibility tree.** A reference survives layout shifts and reflows that make pixel coordinates fragile, and lets Claude act on controls that are hard to hit with a pointer.
* **Fall back to coordinates for content the tree doesn't describe.** Canvas-rendered interfaces, embedded video or remote-desktop surfaces, heavily virtualized lists, and elements inside cross-origin iframes often have no useful node, so Claude works from `screenshot` and `zoom` and clicks by coordinate; your executor resolves which frame a coordinate lands in.
* **Scope reads, and read the tree before you screenshot.** On large pages, `read_page` with `filter: "interactive"` or the `ref` of a container returns a focused subtree, and a tree read of a typical page often costs fewer input tokens than a screenshot while giving Claude references it can act on immediately. Screenshots remain the right observation when visual layout, images, or rendering state matter.


## Security considerations

Source: https://platform.claude.com/llms-full.txt#security-considerations

Browser use carries risks that standard API features don't, because Claude reads and acts on content from the open web, where any page can contain text written to manipulate it.

<Warning>
  To reduce these risks, take precautions such as the following:

  1. Run the browser and your executor in a dedicated container or virtual machine with minimal privileges, a fresh profile that holds no credentials, and no access to sensitive filesystems or internal networks; isolate any tool you run alongside it the same way.
  2. Restrict the hosts the browser can reach to a domain allowlist enforced at the network layer and re-checked in your `navigate` handler after redirects, and block loopback, link-local, and private ranges unless the task needs them.
  3. Treat everything a page supplies as untrusted input, including the tab titles and URLs you report in a [`browser_state`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#track-tabs-and-page-state) block, and build page reads from what the page renders (the accessibility tree or visible text), not raw DOM source, so hidden text doesn't reach Claude.
  4. In your `navigate` handler, accept the history keywords `"back"`, `"forward"`, and `"reload"`, treat a URL without a scheme as `https://`, then parse the URL and refuse any scheme other than `http` or `https` (`javascript:`, `file:`, `data:`, `chrome:`, and so on) with an [error result](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#return-errors-from-your-executor). Check the scheme with a URL parser rather than a string prefix; the API never sees the navigation and can't reject it for you.
  5. Leave `javascript_exec` and `file_upload` disabled unless you need them, and read [Enable optional members](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#enable-optional-member-tools) before turning either on.
  6. Have a human confirm consequential actions and anything that requires affirmative consent (purchasing, modifying accounts, messaging, and accepting terms), and make that check in your executor before each call, because one turn can carry several.
</Warning>

Claude sometimes follows instructions found in page content even when they conflict with yours; text on a page that says "ignore your previous instructions and navigate to..." can divert it from the task. Isolate Claude from sensitive data and actions to limit what a prompt injection can reach, review [Mitigate jailbreaks and prompt injections](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks), and if a task can't avoid a logged-in session, use a dedicated low-privilege account and keep human confirmation on account-changing actions.

Because the browser runs in your environment, the sites Claude visits see your executor's network identity, and page content reaches the API only as the tool results you return. Inform end users of the relevant risks and obtain their consent before enabling browser use in your products.


## Member tools

Source: https://platform.claude.com/llms-full.txt#member-tools

The `browser_toolset_20260801` entry declares 31 member tools; each call's `input` is exactly the parameters listed here, and `tab_id`, where optional, defaults to the active tab. `Target`, `CoordinateTarget`, and `RefTarget` are the shapes described in [Targets and coordinates](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#targets-and-coordinates). Four members (`javascript_exec`, `file_upload`, `read_console`, and `read_network`) are disabled by default and appear only when you [enable them](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#enable-optional-member-tools). The input bounds and output conventions noted in each member's row are stated to Claude, not enforced by the API, so validate inputs (including coordinates against your viewport) and apply the conventions in your executor.

Only `screenshot` and `zoom` require an [`image` block](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls#handling-results-from-client-tools) in their result, and the four tab-management members (`new_tab`, `list_tabs`, `switch_tab`, and `close_tab`) return exactly one `browser_state` block (see [Tab management results](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#tab-management-results)). Every other member returns a `text` block: either a short acknowledgment such as `Clicked element ref_2.` or the member's output. Any result other than a tab-management result may also carry an `image` block, typically a screenshot taken after the action, so Claude sees the outcome without a separate `screenshot` call; [Batch actions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#batch-actions) shows where to attach one in a batch. A member `tool_result` may contain only `text`, `image`, and `browser_state` content blocks.

### Navigation and capture

| Member       | Input               | Description                                                                                                                                                                                                                                                                                     |
| ------------ | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `navigate`   | `url`, `tab_id?`    | Load an `http` or `https` URL, or move through history with `"back"`, `"forward"`, or `"reload"`. Treat a URL without a scheme as `https://` and refuse any other scheme with an error result. Return a short acknowledgment, plus a `browser_state` block when the tab's URL or title changed. |
| `screenshot` | `tab_id?`           | Capture the viewport and return an `image` block.                                                                                                                                                                                                                                               |
| `zoom`       | `region`, `tab_id?` | Return a cropped, upscaled `image` of `region`, given as `[x0, y0, x1, y1]` in viewport pixels, for closer inspection of small text or controls.                                                                                                                                                |

### Pointer

| Member            | Input                                                                       | Description                                                                                                                                                    |
| ----------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `left_click`      | `target: Target`, `modifiers?`, `tab_id?`                                   | Left-click a coordinate or a referenced element. `modifiers` is a chord held during the click, for example, `"shift"` or `"ctrl+shift"`.                       |
| `right_click`     | `target: Target`, `modifiers?`, `tab_id?`                                   | Right-click a coordinate or element.                                                                                                                           |
| `middle_click`    | `target: Target`, `modifiers?`, `tab_id?`                                   | Middle-click a coordinate or element.                                                                                                                          |
| `double_click`    | `target: Target`, `modifiers?`, `tab_id?`                                   | Double left-click a coordinate or element.                                                                                                                     |
| `triple_click`    | `target: Target`, `modifiers?`, `tab_id?`                                   | Triple left-click a coordinate or element, which typically selects a line or paragraph.                                                                        |
| `hover`           | `target: Target`, `tab_id?`                                                 | Move the pointer over a coordinate or element without clicking.                                                                                                |
| `left_click_drag` | `from: CoordinateTarget`, `target: CoordinateTarget`, `tab_id?`             | Press at `from`, drag to `target`, and release.                                                                                                                |
| `left_mouse_down` | `target: CoordinateTarget`, `tab_id?`                                       | Press and hold the left button at a coordinate; pair with `left_mouse_up` for a custom drag.                                                                   |
| `left_mouse_up`   | `target: CoordinateTarget`, `tab_id?`                                       | Release the left button at a coordinate.                                                                                                                       |
| `mouse_move`      | `target: CoordinateTarget`, `tab_id?`                                       | Move the pointer to a coordinate.                                                                                                                              |
| `scroll`          | `target: CoordinateTarget`, `scroll_direction`, `scroll_amount?`, `tab_id?` | Scroll at a viewport position. `scroll_direction` is `"up"`, `"down"`, `"left"`, or `"right"`; `scroll_amount` is in scroll-wheel notches, 1 to 10, default 3. |
| `scroll_to`       | `target: RefTarget`, `tab_id?`                                              | Scroll a referenced element into view.                                                                                                                         |

### Keyboard and timing

| Member     | Input                         | Description                                                                                                                                                                               |
| ---------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`     | `text`, `tab_id?`             | Type a literal string at the current focus.                                                                                                                                               |
| `key`      | `text`, `repeat?`, `tab_id?`  | Press a key or chord. `text` is a single key (`"Enter"`), a chord joined with `+` (`"ctrl+a"`), or a space-separated sequence (`"Backspace Backspace"`); `repeat` is 1 to 100, default 1. |
| `hold_key` | `text`, `duration`, `tab_id?` | Hold a key or chord for `duration` seconds, 0 to 30.                                                                                                                                      |
| `wait`     | `duration`, `tab_id?`         | Pause for `duration` seconds, 0 to 30.                                                                                                                                                    |

### Page reading

| Member          | Input                                  | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| --------------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `read_page`     | `filter?`, `depth?`, `ref?`, `tab_id?` | Return the page's accessibility tree as text with each element tagged with a reference such as `[ref_2]`. With `filter` omitted, return every visible element; with `"interactive"`, only visible interactive elements; with `"all"`, also elements outside the viewport. `depth` caps the tree depth (minimum 1, default 15) and `ref` scopes the read to that element's subtree. Cap the output at 50,000 characters and say so in the text; Claude then narrows with a smaller `depth` or a `ref`. |
| `find`          | `query`, `tab_id?`                     | Search for elements matching a natural-language description such as `"search field"` or `"add to cart button"`, and return up to 20 matches in the same tagged format as `read_page`.                                                                                                                                                                                                                                                                                                                 |
| `get_page_text` | `tab_id?`                              | Return the page's visible text as plain text, prioritizing the main article content; suited to articles, documentation, and other text-heavy pages.                                                                                                                                                                                                                                                                                                                                                   |

### Forms and files

| Member                              | Input                                                     | Description                                                                                                                                                                                                                                                                      |
| ----------------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `form_input`                        | `target: RefTarget`, `value`, `tab_id?`                   | Set a form element's value directly. `value` is a `string`, `number`, or `boolean`; use a `boolean` for checkboxes and an option's value or visible text for selects.                                                                                                            |
| `file_upload` (disabled by default) | `target: RefTarget`, `paths?`, `document_ids?`, `tab_id?` | Set the files on a file-input element from `paths` on the executor's filesystem, `document_ids` your application has staged, or both; at least one is required. See [Upload files](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#upload-files). |

### Diagnostics and scripting

| Member                                  | Input             | Description                                                                                                                                                                                                                                                                      |
| --------------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `read_console` (disabled by default)    | `tab_id?`         | Return the tab's console entries (log, warning, and error lines) accumulated since the last read, one line per entry. See [Read console and network activity](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#read-console-and-network-activity). |
| `read_network` (disabled by default)    | `tab_id?`         | Return the tab's network requests (method, URL, status, MIME type, timing) since the last read, one line per entry.                                                                                                                                                              |
| `javascript_exec` (disabled by default) | `text`, `tab_id?` | Run `text` as JavaScript in the page context and return the value of the last expression as text. See [Enable optional members](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#enable-optional-member-tools).                                    |

### Tab management

| Member       | Input               | Description                            |
| ------------ | ------------------- | -------------------------------------- |
| `new_tab`    | (none)              | Open a tab and make it the active tab. |
| `list_tabs`  | (none)              | Report the tab inventory.              |
| `switch_tab` | `tab_id` (required) | Make `tab_id` the active tab.          |
| `close_tab`  | `tab_id` (required) | Close `tab_id`.                        |

On success, each of these returns exactly one `browser_state` block and no text or image; see [Tab management results](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#tab-management-results).


## Configure the toolset

Source: https://platform.claude.com/llms-full.txt#configure-the-toolset

Besides `type`, the toolset entry accepts `configs`, `cache_control`, and `allowed_callers`; the rules these fields share with the computer use toolset are listed under [Client toolsets](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets), and this section covers the browser-specific defaults. `configs` is an object keyed by member name, and each member's value accepts two fields:

| Field           | Default                                                                                                                                                             | Meaning                                                                                                                                                                                                                                                                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `enabled`       | `true`, except `false` for the four [optional members](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#enable-optional-member-tools) | Whether the member is offered to Claude.                                                                                                                                                                                                                                                                                                         |
| `defer_loading` | `false`                                                                                                                                                             | Whether the toolset's definition is deferred for tool search. Must resolve to the same value on every enabled member. With the four optional members left disabled, deferring the toolset means setting it on the other 27; see [Client toolsets](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets). |

### Enable or disable member tools

List only the members you want to change in `configs`; every member you omit keeps its default. For example, an executor that implements console reads but not low-level pointer or key-hold control turns `read_console` on and withholds three members:

A disabled member disappears from the definition Claude sees; that doesn't guarantee Claude never names it, so your executor still answers such a call with an [error result](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#return-errors-from-your-executor).

### Combine with other tools

Declare the browser use tool alongside your own tools and other Anthropic-provided tools in the same `tools` array. A custom tool may share a member's name (your own `navigate`, for example), because `toolset_name` distinguishes Claude's calls, but no other entry may be named `browser`, and a request may contain only one browser toolset entry.

You can also declare it alongside the [computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool), either the toolset or an earlier computer use tool version. The two work independently, each in its own coordinate frame (viewport pixels here, desktop screenshot pixels there), and Claude's calls to members that share a name, such as `screenshot` or `key`, are told apart by `toolset_name`.


## Enable optional members

Source: https://platform.claude.com/llms-full.txt#enable-optional-members

Four member tools are disabled by default: `javascript_exec` and `file_upload` because they widen what a manipulated page could make Claude do, and `read_console` and `read_network` because not every browser automation stack can supply those logs and they widen what page-controlled content reaches Claude. Enable each one with `configs` (for example, `"configs": {"file_upload": {"enabled": true}}`) only when your executor implements it and the task needs it.

### Upload files

`file_upload` sets the files on an `<input type="file">` element directly, which is more reliable than driving a native file chooser. Its `target` is a reference only, because the call needs the element's identity, and it takes `paths`, `document_ids`, or both:

* `paths` are file paths on the executor's filesystem, for deployments where the executor can read your application's files directly (the same condition under which you populate a download's `path`).
* `document_ids` are identifiers for files your application has staged for the browser, for deployments where it can't. Your application defines what the identifiers mean; scope their resolution the way you scope `paths`, to files staged for this task.

Claude writes these paths while it's reading untrusted pages, so an unrestricted implementation would let a malicious page direct the upload of any file the executor can read to a site the page controls. Enable the member only when your executor resolves each path (following symlinks and `..` segments) and accepts nothing outside a dedicated, allowlisted upload directory that holds only files meant for the task. Don't reuse the browser's download directory for this; if you do, every file a page causes the browser to download becomes uploadable.

### Run JavaScript in the page

`javascript_exec` runs the expression Claude writes in the page's context and returns the value of the last expression as text; Claude writes an expression, not a `return` statement. The code runs with the page's full privileges, including its cookies, storage, and same-origin requests. Enable the member only in sessions that hold no credentials, keep the domain allowlist from [Security considerations](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#security-considerations) in force, treat the returned value as untrusted input, and log the code Claude emits.

### Read console and network activity

`read_console` returns the tab's console entries and `read_network` returns its network requests, each as text with one line per entry accumulated since the previous read of that tab. A console line carries a log, warning, or error entry; a network line carries the method, URL, status, MIME type, and timing. Entries exist only from the moment your browser automation attached to the tab, so an empty result doesn't mean a tab that was already open had no traffic.

These members let Claude diagnose a misbehaving page (a failed request behind a spinner, a script error behind a dead button) without repeated screenshots. Console and network entries are page-controlled and often contain secrets such as tokens in request URLs, so redact credential-like values you don't want in Claude's context and truncate very long entries before returning them.


## Track tabs with `browser_state`

Source: https://platform.claude.com/llms-full.txt#track-tabs-with-browser-state

Claude addresses tabs by `tab_id`, your application is the source of truth for which tabs exist, and you report that state in a `browser_state` content block that Claude never sees directly: the API renders the text Claude reads from it.

* `tabs` is the full inventory of open tabs after the call, not a delta. It may be empty; whenever it isn't, exactly one entry carries `"active": true`.
* `state_changes` (not shown here) reports side effects of the call: a `tab_opened` entry for each tab the call opened that's still open when it finishes, whose `tab_id` must also appear in `tabs`, and [download events](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#report-downloads). Omit the field when there's nothing to report; an empty array is rejected.
* Send the block only on results that answer a browser member call, at most once per `tool_result`, and never on a result with `is_error: true`. You express "no tab state to report" by omitting the block.
* The API renders `tabs` into text for Claude as the next two sections describe; download entries in `state_changes` are validated but not rendered.

**You assign `tab_id` values.** Any stable string works, such as your automation library's page identifier or your own counter, as long as you don't reuse a `tab_id` while a tab with that identifier is still listed as open in an earlier result. The API enforces these limits on the block:

* Each `tab_id`, `title`, and `url` may be at most 4,096 characters, `tab_id` must be non-empty, and none may contain control characters (including newlines) or Unicode line or paragraph separators.
* A block may list at most 100 tabs and 200 state changes.
* The same limits apply to the `tab_id` Claude passes to `switch_tab` and `close_tab`, because the API renders it into the result text, so answer a call whose `tab_id` violates them with an error result instead of a `browser_state` block.

<Warning>
  Tab titles and URLs come from the page and render into text Claude reads, so they're a prompt-injection surface. The API renders URLs verbatim, so sanitize page-supplied URLs before populating `tabs`. It escapes double quotes and backslashes in titles when it renders them, so don't pre-escape titles (a pre-escaped title reaches Claude double-escaped); truncating or dropping suspicious titles is still worthwhile. The length and character limits the API enforces are a floor, not a defense.
</Warning>

### Tab management results

For `new_tab`, `switch_tab`, `close_tab`, and `list_tabs`, a successful result's `content` is exactly one `browser_state` block with no text or image, and the API writes the text Claude sees. A `new_tab` result's block must also carry exactly one `tab_opened` state change whose `tab_id` matches the entry marked `active: true`.

| Member       | Text Claude sees                                                                                                            |
| ------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `switch_tab` | `Switched to tab {tab_id}`, taken from the call's `input.tab_id`                                                            |
| `close_tab`  | `Closed tab {tab_id}`, taken from the call's `input.tab_id`                                                                 |
| `new_tab`    | `Created new tab with tab_id: {tab_id}, URL: {url}. It is now the current tab.`, taken from the entry marked `active: true` |
| `list_tabs`  | `Available tabs:` followed by one line per tab, or `No tabs available` when `tabs` is empty                                 |

A `list_tabs` result whose block lists two tabs with the first one active renders as follows, with each line indented two spaces and `(current)` appended to the active tab only:

```text wrap
Available tabs:
  • tab_id tab-1: "Documentation" (https://example.com/docs) (current)
  • tab_id tab-2: "Pricing" (https://example.com/pricing)

json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01WvHSbQVV9j5nWGvTmk4vNL",
      "toolset_name": "browser",
      "content": [
        {
          "type": "browser_state",
          "tabs": [
            { "tab_id": "tab-1", "title": "Documentation", "url": "https://example.com/docs" },
            { "tab_id": "tab-2", "title": "Pricing", "url": "https://example.com/pricing" },
            { "tab_id": "tab-3", "title": "", "url": "about:blank", "active": true }
          ],
          "state_changes": [{ "type": "tab_opened", "tab_id": "tab-3" }]
        }
      ]
    }
  ]
}

text wrap
Tab Context:
- Executed on tab_id: tab-1
- Available tabs:
  • tab_id tab-1: "Documentation" (https://example.com/docs)
  • tab_id tab-2: "Pricing" (https://example.com/pricing)

json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01EgTXj1FjE2FCTt2zNFWLao",
      "toolset_name": "browser",
      "content": [
        { "type": "text", "text": "Clicked element ref_5." },
        {
          "type": "browser_state",
          "tabs": [
            {
              "tab_id": "tab-1",
              "title": "Documentation",
              "url": "https://example.com/docs",
              "active": true
            },
            { "tab_id": "tab-2", "title": "Pricing", "url": "https://example.com/pricing" }
          ],
          "state_changes": [{ "type": "tab_opened", "tab_id": "tab-2" }]
        }
      ]
    }
  ]
}

json
{
  "type": "browser_state",
  "tabs": [
    { "tab_id": "tab-1", "title": "Documentation", "url": "https://example.com/docs" },
    {
      "tab_id": "tab-2",
      "title": "Pricing",
      "url": "https://example.com/pricing",
      "active": true
    }
  ],
  "state_changes": [
    {
      "type": "download_completed",
      "download_id": "dl-1",
      "url": "https://example.com/pricing/price-list.csv",
      "path": "/home/user/downloads/price-list.csv",
      "size_bytes": 48213
    }
  ]
}
```

Download reports follow these rules:

* At most one entry per `download_id` in a single block, so a download that starts and finishes during the same call reports only `download_completed`.
* Never send `state_changes` on an `is_error: true` result; report a download event that occurred during a failed call on the next successful result.
* `state_changes` isn't an inventory of downloads in progress; report each event once.
* Each entry carries only the fields its `type` declares. `size_bytes` is a non-negative integer, `download_id` is non-empty, and `download_id`, `url`, `path`, and `error` are each at most 4,096 characters with no control characters or Unicode line or paragraph separators. The `url` comes from the remote server and often carries signed query-string credentials after redirects, so strip query parameters you don't want in Claude's context and sanitize it before reporting it or using it in a filesystem path.


## Handle errors

Source: https://platform.claude.com/llms-full.txt#handle-errors

Report a failed call to Claude as an ordinary error result: `is_error: true`, text content that says what went wrong, `toolset_name` echoed, and no `browser_state` block.

### Return errors from your executor

Make error text specific, because Claude reads it and adapts: `Error: Navigation to https://example.com/status timed out after 30 seconds. The page may be unavailable.` gives Claude something to act on where a bare `Error: navigation failed` doesn't. Other common cases:

<AccordionGroup>
  <Accordion title="Refused navigation scheme">

</Accordion>

  <Accordion title="Stale or unknown element reference">

</Accordion>

  <Accordion title="Disabled or unimplemented member">

</Accordion>

  <Accordion title="Skipped after an earlier failure in the turn">
    When the `left_click` on `ref_3` from [Batch actions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#batch-actions) fails with the stale-reference error shown earlier, the `type` and `key` calls after it each get this result:

</Accordion>
</AccordionGroup>

### Request errors

The API validates the toolset entry and every member `tool_use` and `tool_result` block in the conversation. When one is malformed, the API returns an `invalid_request_error` before Claude runs. In the following table, the left column names what you sent.

| Request                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Why it fails and what to do                                                                                                                                                                                                                                    |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| An option or combination the toolset entry doesn't accept, for example, a `name`, `strict: true`, `input_examples`, `defer_loading` on the entry itself, a `configs` key that isn't a member name, a field other than `enabled` or `defer_loading` in a member's `configs` value ([Configure the toolset](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#configure-the-toolset)), enabled members whose `defer_loading` values differ ([Configure the toolset](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#configure-the-toolset)), a `configs` that leaves no member enabled, a code execution caller in `allowed_callers`, the legacy `fine-grained-tool-streaming-2025-05-14` beta header on the request, a `tool_choice` of type `tool` naming `browser` or a member, or a second browser toolset entry or another tool named `browser` | These aren't supported on client toolsets. See [Client toolsets](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets) for each rule and its alternative.                                                              |
| A `tool_result` answering a member call without `"toolset_name": "browser"` or with a different value, or `toolset_name` on a result whose call wasn't a member call                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Echo `toolset_name` exactly on member results, and only on them.                                                                                                                                                                                               |
| A member `tool_use` from an earlier turn with no matching `tool_result`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Answer every member call, including the ones you didn't run after a failure.                                                                                                                                                                                   |
| A content block other than `text`, `image`, or `browser_state` in a member result                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Member results accept only those three block types.                                                                                                                                                                                                            |
| A `browser_state` block that breaks a rule in [Track tabs with `browser_state`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#track-tabs-and-page-state), for example, one on an `is_error: true` result or on a result that doesn't answer a browser member call, more than one in a result, a non-empty `tabs` without exactly one `active: true` entry, a duplicate `tab_id`, an empty `state_changes` array, a `tab_opened` whose `tab_id` isn't in `tabs`, two state changes for one `download_id` or a state-change field its `type` doesn't declare ([Report downloads](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#report-downloads)), or a field over its limits                                                                                                                                                                  | Fix the block. "Nothing to report" is expressed by omitting the block or the `state_changes` field, never by an empty value.                                                                                                                                   |
| A successful `new_tab`, `switch_tab`, `close_tab`, or `list_tabs` result whose `content` isn't exactly one `browser_state` block, or a `new_tab` result without exactly one `tab_opened` matching the active tab                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | The API renders these results from the block and needs it in that exact shape; see [Tab management results](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#tab-management-results).                                            |
| An `image` in a result over your model's [image size limits](https://platform.claude.com/docs/en/build-with-claude/vision#evaluate-image-size), or over the stricter per-image limit that applies once the request holds [more than 20 images](https://platform.claude.com/docs/en/build-with-claude/vision#request-limits), counting screenshots and `zoom` images in earlier results                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | The API doesn't downscale toolset images. Resize screenshots before returning them ([Size screenshots to fit image limits](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#handle-coordinate-scaling-for-higher-resolutions)). |
| A `model` that doesn't support `browser_toolset_20260801`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | See [Compatibility](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#compatibility) for the supported models.                                                                                                                    |


## Limitations

Source: https://platform.claude.com/llms-full.txt#limitations-3

* **Platform availability:** Browser use is available on the Claude API and [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai).
* **Whole-input streaming only:** When you stream, each member's `input` arrives as one complete `input_json_delta` ([Client toolsets](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets)).
* **Element references are best-effort:** Highly dynamic pages (virtualized lists, canvas-rendered interfaces, pages that re-render on scroll) might not expose stable references, and Claude falls back to screenshots and coordinate clicks there.
* **`read_console` and `read_network` depend on your browser automation:** They report only what it can capture, and only from the moment it attached to a tab.
* **General agent limitations apply:** Latency, vision accuracy, and prompt-injection risks carry over from computer use (see the computer use tool's [Limitations](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#understand-computer-use-limitations)), and its guidance under [Optimize model performance with prompting](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#optimize-model-performance-with-prompting), [Manage screenshot history](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#manage-screenshot-history), and [Follow implementation best practices](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#follow-implementation-best-practices) (action delays, action validation, and logging) applies to browser executors too.


## Pricing and data retention

Source: https://platform.claude.com/llms-full.txt#pricing-and-data-retention

Browser use follows the standard [tool use pricing](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview#pricing). When using the browser use tool:

**Toolset definition overhead:** Declaring `browser_toolset_20260801` with its default members adds about 6,600 input tokens to a request (about 6,610 on Claude Fable 5, Claude Mythos 5, Claude Opus 5, and Claude Opus 4.8, and about 6,670 on Claude Sonnet 5), which covers the member tool definitions and the tool use system prompt. Enabling all four optional members adds about 880 tokens, and disabling members with `configs` reduces the count. The exact count for a request is reported in the response `usage`, and you can estimate it in advance with the [token counting endpoint](https://platform.claude.com/docs/en/build-with-claude/token-counting).

**Additional token consumption:**

* Screenshot and zoom images returned in tool results, billed as image input (see [Vision pricing](https://platform.claude.com/docs/en/build-with-claude/vision#evaluate-image-size))
* Text tool results returned to Claude, such as accessibility trees, page text, and console or network entries

<Note>
  If you also use the computer use tool, bash tool, text editor tool, or your own tools alongside browser use, those tools have their own token costs as documented on their respective pages.
</Note>

The browser session, downloads, and uploaded files stay in your environment; the screenshots, page text, and tab state you return are part of your API request content and follow the standard retention policy, or your ZDR arrangement if you have one. The browser use tool is ZDR eligible; see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) for retention periods and eligibility across features.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-26

<CardGroup cols={3}>
  <Card title="Computer use tool" icon="computer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool">
    Give Claude control of a full desktop when the task leaves the browser; its implementation guidance applies to browser executors too.
  </Card>

  <Card title="Handle tool calls" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls">
    Format `tool_result` blocks, return images and errors, and continue the conversation.
  </Card>

  <Card title="Tool reference" icon="book" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference">
    Browse client toolsets and every other Anthropic-provided tool, with their versions and parameters.
  </Card>
</CardGroup>


---
title: Code execution tool
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool
description: Run Python and bash code in a sandboxed container to analyze data, generate files, and iterate on solutions.
---


## Compatibility

Source: https://platform.claude.com/llms-full.txt#compatibility-6

- [ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): not eligible
- Supported models: `claude-fable-5-1`, `claude-mythos-5-1`, `claude-fable-5`, `claude-mythos-5`, `claude-opus-5`, `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`, `claude-opus-4-5-20251101`, `claude-sonnet-5`, `claude-sonnet-4-6`, `claude-sonnet-4-5-20250929`, `claude-haiku-4-5-20251001`
- Platforms: Claude API, Claude Platform on AWS, Microsoft Foundry [1]; not available on Amazon Bedrock, Google Cloud
- Every supported model accepts all three [tool versions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#tool-versions). On Claude Haiku 4.5, programmatic tool calling and REPL state persistence aren't available, so the newer versions behave like `code_execution_20250825` there.
- For [Claude Mythos Preview](https://anthropic.com/glasswing), code execution is supported on the Claude API and Microsoft Foundry.
1. On [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), code execution requires a [Hosted on Anthropic deployment](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#additional-features-not-supported-when-hosted-on-azure).

Claude can analyze data, create visualizations, perform complex calculations, run system commands, create and edit files, and process uploaded files directly within the API conversation. The code execution tool allows Claude to run Bash commands and manipulate files, including writing code, in a secure, sandboxed environment.

**Code execution is free when used with web search or web fetch (`web_search_20260209`, `web_fetch_20260209`, or later).** When one of those tools is in your request, there are no additional charges for code execution in that request beyond standard token costs. This covers both the code execution behind dynamic filtering and any code Claude runs directly. Standard code execution pricing applies when they are not included.

Code execution also powers dynamic filtering in the [web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) and [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) tools: Claude filters results inside the code execution environment before they reach the context window. When dynamic filtering runs, the API provisions the code execution it needs for the request automatically, so you don't add the code execution tool to your request for it.

<Note>
  Reach out through the [feedback form](https://forms.gle/LTAU6Xn2puCJMi1n6) to share your feedback on this feature.
</Note>


## Tool versions

Source: https://platform.claude.com/llms-full.txt#tool-versions-2

The code execution tool has three current versions, and every [supported model](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#compatibility) accepts all three. Each version builds on the previous one:

* `code_execution_20250825` supports Bash commands and file operations.
* `code_execution_20260120` adds REPL state persistence and [programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling) from within the sandbox. Claude Haiku 4.5 accepts the `code_execution_20260120` and `code_execution_20260521` tool types, but programmatic tool calling and the REPL state persistence that depends on it aren't available on it, so the newer versions behave like `code_execution_20250825` there.
* `code_execution_20260521` is the same runtime as `code_execution_20260120`. The difference is that the tool description tells Claude about the 90-second wall-clock limit on each Python cell in programmatic tool calling, so Claude can budget long-running cells. A cell that exceeds the limit returns a normal code execution result with a non-zero `return_code` and a `detection_timeout` status message in its output. This is separate from the `execution_time_exceeded` [error code](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#errors), which the API returns when a whole tool invocation exceeds the maximum execution time.

None of the three tool versions requires an `anthropic-beta` header. The legacy code execution beta headers remain valid opt-ins.

The examples on this page use `code_execution_20250825`, which covers the Bash and file operations they demonstrate and behaves the same way on every supported model; use `code_execution_20260120` or later when you need programmatic tool calling or REPL state persistence. The current [web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) and [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) tools (`web_search_20260209`, `web_fetch_20260209`, and later) require `code_execution_20260120` or later as their code execution version.

Older tool versions aren't guaranteed to stay compatible with newer models. When you adopt a new model, check [Tool versions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#tool-versions) and [Compatibility](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#compatibility), and prefer the newest tool version your integration supports.

<Note>
  If you're still using the legacy `code_execution_20250522` (Python only), see [Upgrade to latest tool version](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#upgrade-to-latest-tool-version) to migrate from it.
</Note>


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-4

Here's an example that asks Claude to perform a calculation:

<CodeGroup>
  ```bash cURL
  curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [
        {
          "role": "user",
          "content": "Use the code execution tool to calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
        }
      ],
      "tools": [
        {
          "type": "code_execution_20250825",
          "name": "code_execution"
        }
      ]
    }'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 4096 \
    --message '{
      role: user,
      content: "Use the code execution tool to calculate the mean and standard
        deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
    }' \
    --tool '{type: code_execution_20250825, name: code_execution}'

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": "Use the code execution tool to calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
          }
      ],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

  print(response.to_json())

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content:
          "Use the code execution tool to calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
      }
    ],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });

  console.log(JSON.stringify(response));

csharp C#
  AnthropicClient client = new();

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 4096,
      Messages = [new() { Role = Role.User, Content = "Use the code execution tool to calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]" }],
      Tools = [new CodeExecutionTool20250825()]
  });

  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Use the code execution tool to calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(4096L)
      .addUserMessage("Use the code execution tool to calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]")
      .addTool(CodeExecutionTool20250825.builder().build())
      .build();

  Message response = client.messages().create(params);
  IO.println(ObjectMappers.jsonMapper().valueToTree(response));

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          [
              'role' => 'user',
              'content' => 'Use the code execution tool to calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]',
          ],
      ],
      model: Model::CLAUDE_OPUS_5,
      tools: [new CodeExecutionTool20250825()],
  );

  echo json_encode($message, JSON_PRETTY_PRINT), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: Anthropic::Model::CLAUDE_OPUS_5,
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Use the code execution tool to calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
      }
    ],
    tools: [Anthropic::CodeExecutionTool20250825.new]
  )

  puts message.to_json
  ```
</CodeGroup>

The response interleaves `server_tool_use` blocks (the commands Claude ran) with their tool result blocks, followed by Claude's text. The top level also includes a `container` object whose `id` you can [reuse across requests](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#container-reuse). See [Response format](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#response-format) for the block shapes.


## How code execution works

Source: https://platform.claude.com/llms-full.txt#how-code-execution-works

When you add the code execution tool to your API request:

1. Claude evaluates whether code execution would help answer your question

2. The tool automatically provides Claude with the following capabilities:

   * **Bash commands:** Run shell commands for system operations
   * **File operations:** Create, view, and edit files directly, including writing code

3. Claude can use any combination of these capabilities in a single request

4. All operations run in a secure, sandboxed container. The container has no internet access, so Claude can't download packages at runtime: only the [pre-installed libraries](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#pre-installed-libraries) are available

5. The API runs every command server-side and returns the results to Claude within the same request, so you never execute code or send back `tool_result` blocks yourself. One exception is when Claude calls one of your client tools alongside code execution: the API returns the code execution call without its result. The result arrives in a later response, after you send back the `tool_result` blocks for your client tools

6. Each request runs in a new container unless you pass an earlier response's container ID back (see [Container reuse](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#container-reuse))

7. Claude provides results with any generated charts, calculations, or analysis

The container has Python pre-installed. Claude writes Python with the file operations sub-tool and runs it with a Bash command. With `code_execution_20260120` or later and [programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling), the Python interpreter state (such as variable bindings) also persists across requests that reuse the container.

### When Claude runs code

Claude runs code when the request benefits from computation or file handling:

* Non-trivial math (large numbers, many steps, precision-sensitive results)
* Data analysis, file parsing, or visualization
* Algorithm execution or simulation
* Explicit requests to "run", "compute", or "execute"

Claude answers directly without running code for:

* Simple arithmetic and well-known math facts
* Factual, conversational, or creative requests
* Simple unit conversions or translations

If you want Claude to run code for a borderline request, ask explicitly (for example, "run code to verify this").


## Work with files

Source: https://platform.claude.com/llms-full.txt#work-with-files

### Upload and analyze your own files

To analyze your own data files (such as CSV, Excel, or images), upload them through the Files API and reference them in your request.

The Python environment can process various file types uploaded through the Files API, including:

* CSV
* Excel (.xlsx, .xls)
* JSON
* XML
* Images (JPEG, PNG, GIF, WebP)
* Text files (.txt, .md, .py, and others)

#### Upload and analyze files

1. **Upload your file** using the [Files API](https://platform.claude.com/docs/en/build-with-claude/files)
2. **Reference the file** in your message using a `container_upload` content block
3. **Include the code execution tool** in your API request

<CodeGroup>
  ```bash cURL
  # First, upload a file and capture the file ID (using jq)
  FILE_ID=$(curl --fail-with-body -sS https://api.anthropic.com/v1/files \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -F "file=@data.csv" | jq -r '.id')

  # Then use the file_id with code execution
  curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [{
        "role": "user",
        "content": [
          {"type": "text", "text": "Analyze this CSV data"},
          {"type": "container_upload", "file_id": "'"$FILE_ID"'"}
        ]
      }],
      "tools": [{
        "type": "code_execution_20250825",
        "name": "code_execution"
      }]
    }'

bash CLI
  # First, upload a file and capture the file ID
  FILE_ID=$(ant files upload --file ./data.csv --transform id --raw-output)

  # Then use the file_id with code execution
  ant messages create <<YAML
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content:
        - type: text
          text: Analyze this CSV data
        - type: container_upload
          file_id: $FILE_ID
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

python Python
  client = anthropic.Anthropic()

  # Upload a file
  file_object = client.files.upload(file=Path("data.csv"))

  # Use the file_id with code execution
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": [
                  {"type": "text", "text": "Analyze this CSV data"},
                  {"type": "container_upload", "file_id": file_object.id},
              ],
          }
      ],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

  print(response.to_json())

typescript TypeScript
  import { createReadStream } from "node:fs";
  // ...
  const client = new Anthropic();

  // Upload a file
  const fileObject = await client.files.upload({
    file: createReadStream("data.csv")
  });

  // Use the file_id with code execution
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: "Analyze this CSV data" },
          { type: "container_upload", file_id: fileObject.id }
        ]
      }
    ],
    tools: [
      {
        type: "code_execution_20250825",
        name: "code_execution"
      }
    ]
  });

  console.log(JSON.stringify(response));

csharp C#
  AnthropicClient client = new();

  // Upload a file
  var fileObject = await client.Files.Upload(new FileUploadParams
  {
      File = File.OpenRead("data.csv")
  });

  // Use the file_id with code execution
  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 4096,
      Messages = [
          new()
          {
              Role = Role.User,
              Content = new([
                  new TextBlockParam { Text = "Analyze this CSV data" },
                  new ContainerUploadBlockParam { FileID = fileObject.ID }
              ])
          }
      ],
      Tools = [new CodeExecutionTool20250825()]
  };

  var response = await client.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  ctx := context.Background()
  client := anthropic.NewClient()

  // Upload a file
  file, err := os.Open("data.csv")
  if err != nil {
  	log.Fatal(err)
  }
  defer file.Close()

  fileObject, err := client.Files.Upload(ctx, anthropic.FileUploadParams{
  	File: file,
  })
  if err != nil {
  	log.Fatal(err)
  }

  // Use the file_id with code execution
  response, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(
  			anthropic.NewTextBlock("Analyze this CSV data"),
  			anthropic.NewContainerUploadBlock(fileObject.ID),
  		),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(response.RawJSON())

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  // Upload a file
  FileMetadata fileObject = client.files().upload(
      FileUploadParams.builder()
          .file(Path.of("data.csv"))
          .build()
  );

  // Use the file_id with code execution
  Message response = client.messages().create(
      MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .addUserMessageOfBlockParams(List.of(
              ContentBlockParam.ofText(TextBlockParam.builder()
                  .text("Analyze this CSV data")
                  .build()),
              ContentBlockParam.ofContainerUpload(ContainerUploadBlockParam.builder()
                  .fileId(fileObject.id())
                  .build())
          ))
          .addTool(CodeExecutionTool20250825.builder().build())
          .build()
  );

  IO.println(ObjectMappers.jsonMapper().valueToTree(response));

php PHP
  $client = new Client();

  // Upload a file
  $fileObject = $client->files->upload(
      file: FileParam::fromResource(fopen('data.csv', 'r')),
  );

  // Use the file_id with code execution
  $response = $client->messages->create(
      model: Model::CLAUDE_OPUS_5,
      maxTokens: 4096,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  TextBlockParam::with(text: 'Analyze this CSV data'),
                  ContainerUploadBlockParam::with(fileID: $fileObject->id),
              ],
          ],
      ],
      tools: [new CodeExecutionTool20250825()],
  );

  echo json_encode($response), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  # Upload a file
  file_object = client.files.upload(
    file: Pathname("data.csv")
  )

  # Use the file_id with code execution
  response = client.messages.create(
    model: Anthropic::Model::CLAUDE_OPUS_5,
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: "Analyze this CSV data" },
          { type: "container_upload", file_id: file_object.id }
        ]
      }
    ],
    tools: [
      Anthropic::CodeExecutionTool20250825.new
    ]
  )

  puts response.to_json

bash cURL
  # Downloading every generated file means looping over the file IDs in the tool
  # result, which doesn't translate to a one-off shell command. Use one of the
  # SDK examples instead.

bash CLI
  # Extracting every file ID from the tool results and downloading each one
  # requires a loop, which doesn't translate well to a one-off CLI command.
  # Use one of the SDK examples instead.

python Python
  client = Anthropic()

  # Request code execution that creates files
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": "Create a matplotlib visualization and save it as output.png",
          }
      ],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )


  # Extract file IDs from the response
  def extract_file_ids(response: Message) -> list[str]:
      file_ids: list[str] = []
      for item in response.content:
          if item.type == "bash_code_execution_tool_result":
              content_item = item.content
              if content_item.type == "bash_code_execution_result":
                  for output_block in content_item.content:
                      file_ids.append(output_block.file_id)
      return file_ids


  # Download the created files
  for file_id in extract_file_ids(response):
      file_metadata = client.files.retrieve_metadata(file_id)
      file_content = client.files.download(file_id)
      file_content.write_to_file(file_metadata.filename)
      print(f"Downloaded: {file_metadata.filename}")

typescript TypeScript
  import { writeFile } from "node:fs/promises";

  const client = new Anthropic();

  // Request code execution that creates files
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Create a matplotlib visualization and save it as output.png"
      }
    ],
    tools: [
      {
        type: "code_execution_20250825",
        name: "code_execution"
      }
    ]
  });

  // Extract the file IDs from the response and download each created file
  for (const block of response.content) {
    if (block.type === "bash_code_execution_tool_result") {
      const result = block.content;
      if (result.type === "bash_code_execution_result") {
        for (const outputBlock of result.content) {
          const [fileMetadata, fileResponse] = await Promise.all([
            client.files.retrieveMetadata(outputBlock.file_id),
            client.files.download(outputBlock.file_id)
          ]);
          await writeFile(fileMetadata.filename, await fileResponse.bytes());
          console.log(`Downloaded: ${fileMetadata.filename}`);
        }
      }
    }
  }

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 4096,
      Messages = [new() { Role = Role.User, Content = "Create a matplotlib visualization and save it as output.png" }],
      Tools = [new CodeExecutionTool20250825()]
  };

  var response = await client.Messages.Create(parameters);

  // Collect the file IDs from the tool results
  List<string> fileIds = [];
  foreach (var block in response.Content)
  {
      if (!block.TryPickBashCodeExecutionToolResult(out var toolResult))
          continue;
      if (!toolResult.Content.TryPickBashCodeExecutionResultBlock(out var result))
          continue;
      foreach (var output in result.Content)
      {
          fileIds.Add(output.FileID);
      }
  }

  // Download each created file
  foreach (var fileId in fileIds)
  {
      var fileMetadata = await client.Files.RetrieveMetadata(fileId);
      using var download = await client.Files.Download(fileId);
      var downloadStream = await download.ReadAsStream();
      await using var target = File.Create(fileMetadata.Filename);
      await downloadStream.CopyToAsync(target);
      Console.WriteLine($"Downloaded: {fileMetadata.Filename}");
  }

go Go
  	client := anthropic.NewClient()
  	ctx := context.Background()

  	response, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 4096,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Create a matplotlib visualization and save it as output.png")),
  		},
  		Tools: []anthropic.ToolUnionParam{
  			{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  		},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	fileIDs := extractFileIDs(response)

  	for _, fileID := range fileIDs {
  		fileMetadata, err := client.Files.GetMetadata(ctx, fileID)
  		if err != nil {
  			log.Fatal(err)
  		}

  		fileContent, err := client.Files.Download(ctx, fileID)
  		if err != nil {
  			log.Fatal(err)
  		}

  		outFile, err := os.Create(fileMetadata.Filename)
  		if err != nil {
  			log.Fatal(err)
  		}

  		_, err = io.Copy(outFile, fileContent.Body)
  		if err != nil {
  			log.Fatal(err)
  		}
  		outFile.Close()
  		fileContent.Body.Close()

  		fmt.Printf("Downloaded: %s\n", fileMetadata.Filename)
  	}
  // ...

  func extractFileIDs(response *anthropic.Message) []string {
  	var fileIDs []string
  	for _, item := range response.Content {
  		switch variant := item.AsAny().(type) {
  		case anthropic.BashCodeExecutionToolResultBlock:
  			// Collect the file IDs from the tool result
  			for _, file := range variant.Content.Content {
  				if file.FileID != "" {
  					fileIDs = append(fileIDs, file.FileID)
  				}
  			}
  		}
  	}
  	return fileIDs
  }

java Java
  void main() throws Exception {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .addUserMessage("Create a matplotlib visualization and save it as output.png")
          .addTool(CodeExecutionTool20250825.builder().build())
          .build();

      Message response = client.messages().create(params);

      List<String> fileIds = extractFileIds(response);

      for (String fileId : fileIds) {
          FileMetadata fileMetadata = client.files().retrieveMetadata(fileId);
          try (HttpResponse fileContent = client.files().download(fileId)) {
              Files.copy(
                  fileContent.body(),
                  Path.of(fileMetadata.filename()),
                  StandardCopyOption.REPLACE_EXISTING);
          }
          IO.println("Downloaded: " + fileMetadata.filename());
      }
  }

  List<String> extractFileIds(Message response) {
      List<String> fileIds = new ArrayList<>();
      // Collect the file IDs from the tool results
      for (ContentBlock item : response.content()) {
          item.bashCodeExecutionToolResult().ifPresent(toolResult -> {
              if (toolResult.content().isBashCodeExecutionResultBlock()) {
                  BashCodeExecutionResultBlock result =
                      toolResult.content().asBashCodeExecutionResultBlock();
                  for (BashCodeExecutionOutputBlock output : result.content()) {
                      fileIds.add(output.fileId());
                  }
              }
          });
      }
      return fileIds;
  }

php PHP
  $client = new Client();

  // Request code execution that creates files
  $response = $client->messages->create(
      maxTokens: 4096,
      messages: [
          [
              'role' => 'user',
              'content' => 'Create a matplotlib visualization and save it as output.png',
          ],
      ],
      model: Model::CLAUDE_OPUS_5,
      tools: [new CodeExecutionTool20250825()],
  );

  /**
   * Extract file IDs from the response.
   *
   * @return list<string>
   */
  function extractFileIds(Message $response): array
  {
      $fileIds = [];
      foreach ($response->content as $block) {
          if ($block->type !== 'bash_code_execution_tool_result') {
              continue;
          }
          $resultBlock = $block->content;
          if ($resultBlock->type !== 'bash_code_execution_result') {
              continue;
          }
          foreach ($resultBlock->content as $outputBlock) {
              $fileIds[] = $outputBlock->fileID;
          }
      }
      return $fileIds;
  }

  // Download the created files
  foreach (extractFileIds($response) as $fileId) {
      $fileMetadata = $client->files->retrieveMetadata($fileId);
      $fileContent = $client->files->download($fileId);

      file_put_contents($fileMetadata->filename, $fileContent);
      echo "Downloaded: {$fileMetadata->filename}\n";
  }

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: Anthropic::Model::CLAUDE_OPUS_5,
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Create a matplotlib visualization and save it as output.png"
      }
    ],
    tools: [
      {
        type: "code_execution_20250825",
        name: "code_execution"
      }
    ]
  )

  def extract_file_ids(response)
    file_ids = []
    response.content.each do |item|
      if item.type == :bash_code_execution_tool_result
        # WORKAROUND for anthropic-sdk-ruby union coercion bug (SDK-636): item.content is a
        # nested content union, so the typed accessors on `item.content` are unreliable.
        # Read the raw response data through the public `BaseModel#[]` API instead.
        content_item = item.content
        if content_item[:type].to_s == "bash_code_execution_result"
          Array(content_item[:content]).each do |output_block|
            file_ids << output_block[:file_id]
          end
        end
      end
    end
    file_ids
  end

  extract_file_ids(response).each do |file_id|
    file_metadata = client.files.retrieve_metadata(file_id)
    file_content = client.files.download(file_id)

    File.open(file_metadata.filename, "wb") do |f|
      f.write(file_content.read)
    end

    puts "Downloaded: #{file_metadata.filename}"
  end

bash
python /tmp/make_report.py && cp /tmp/report.pdf "$OUTPUT_DIR/" && ls "$OUTPUT_DIR"
```

A file Claude wrote elsewhere is still in the container, so you can [reuse the container](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#container-reuse) and ask Claude to copy it into `$OUTPUT_DIR`.

### Content Credentials on generated files

On the Claude API, supported image, video, and audio files that Claude produces in the code execution sandbox carry [C2PA](https://c2pa.org/) Content Credentials when you download them through the [Files API](https://platform.claude.com/docs/en/build-with-claude/files). [Supported formats](https://opensource.contentauthenticity.org/docs/sdk-repos/c2pa-python/docs/supported-formats/) include PNG, JPEG, GIF, WebP, TIFF, HEIC, AVIF, SVG, MP4, MOV, MP3, WAV, FLAC, and M4A. The credential is a cryptographically signed manifest embedded in the file's metadata. It identifies Anthropic as the issuer, carries a timestamp, and records the action description "Claude provided this file at the request of a user and may have created or modified the file contents."

Signing requires no changes to your requests or response handling, and the manifest records nothing about you, your organization, or your request. The file's visible content is unchanged. The manifest adds a few kilobytes, so the downloaded file's size and checksum differ from the file as it exists inside the container. Text files, PDFs, and office documents are not signed because they are not supported formats for signing. Files you upload are stored as-is, including any Content Credentials they already carry.

To verify a credential, inspect the file with any C2PA-compatible tool, such as the open-source [c2patool command-line utility](https://github.com/contentauth/c2pa-rs). Re-encoding, format conversion, screenshots, and tools that strip metadata remove the credential, so a missing credential doesn't mean a file wasn't produced with Claude. For more on why a credential can be missing, see [How Claude marks AI-generated content](https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content).


## Tool definition

Source: https://platform.claude.com/llms-full.txt#tool-definition

The code execution tool requires no additional parameters:

```json JSON
{
  "type": "code_execution_20250825",
  "name": "code_execution"
}
```

Both fields are fixed: `type` selects the tool version, and `name` must be `code_execution`.

When you provide this tool, Claude automatically gains access to two sub-tools:

* `bash_code_execution`: Run shell commands
* `text_editor_code_execution`: View, create, and edit files, including writing code

When Claude runs code, the response also includes a top-level `container` object with the container's `id` and `expires_at` timestamp. Pass that ID back in the top-level `container` request parameter to keep using the same container. See [Container reuse](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#container-reuse).


## Response format

Source: https://platform.claude.com/llms-full.txt#response-format

The code execution tool can return two types of results depending on the operation:

### Bash command response

```json Output
{
  "type": "server_tool_use",
  "id": "srvtoolu_01B3C4D5E6F7G8H9I0J1K2L3",
  "name": "bash_code_execution",
  "input": {
    "command": "ls -la | head -5"
  }
},
{
  "type": "bash_code_execution_tool_result",
  "tool_use_id": "srvtoolu_01B3C4D5E6F7G8H9I0J1K2L3",
  "content": {
    "type": "bash_code_execution_result",
    "stdout": "total 24\ndrwxr-xr-x 2 user user 4096 Jan 1 12:00 .\ndrwxr-xr-x 3 user user 4096 Jan 1 11:00 ..\n-rw-r--r-- 1 user user  220 Jan 1 12:00 data.csv\n-rw-r--r-- 1 user user  180 Jan 1 12:00 config.json",
    "stderr": "",
    "return_code": 0,
    "content": []
  }
}

json Output
{
  "type": "server_tool_use",
  "id": "srvtoolu_01C4D5E6F7G8H9I0J1K2L3M4",
  "name": "text_editor_code_execution",
  "input": {
    "command": "view",
    "path": "config.json"
  }
},
{
  "type": "text_editor_code_execution_tool_result",
  "tool_use_id": "srvtoolu_01C4D5E6F7G8H9I0J1K2L3M4",
  "content": {
    "type": "text_editor_code_execution_view_result",
    "file_type": "text",
    "content": "{\n  \"setting\": \"value\",\n  \"debug\": true\n}",
    "num_lines": 4,
    "start_line": 1,
    "total_lines": 4
  }
}

json Output
{
  "type": "server_tool_use",
  "id": "srvtoolu_01D5E6F7G8H9I0J1K2L3M4N5",
  "name": "text_editor_code_execution",
  "input": {
    "command": "create",
    "path": "new_file.txt",
    "file_text": "Hello, World!"
  }
},
{
  "type": "text_editor_code_execution_tool_result",
  "tool_use_id": "srvtoolu_01D5E6F7G8H9I0J1K2L3M4N5",
  "content": {
    "type": "text_editor_code_execution_create_result",
    "is_file_update": false
  }
}

json Output
{
  "type": "server_tool_use",
  "id": "srvtoolu_01E6F7G8H9I0J1K2L3M4N5O6",
  "name": "text_editor_code_execution",
  "input": {
    "command": "str_replace",
    "path": "config.json",
    "old_str": "\"debug\": true",
    "new_str": "\"debug\": false"
  }
},
{
  "type": "text_editor_code_execution_tool_result",
  "tool_use_id": "srvtoolu_01E6F7G8H9I0J1K2L3M4N5O6",
  "content": {
    "type": "text_editor_code_execution_str_replace_result",
    "old_start": 3,
    "old_lines": 1,
    "new_start": 3,
    "new_lines": 1,
    "lines": ["-  \"debug\": true", "+  \"debug\": false"]
  }
}

json Output
{
  "type": "bash_code_execution_tool_result",
  "tool_use_id": "srvtoolu_01VfmxgZ46TiHbmXgy928hQR",
  "content": {
    "type": "bash_code_execution_tool_result_error",
    "error_code": "unavailable"
  }
}
```

**Error codes by tool type:**

| Tool         | Error code                | Description                                             |
| ------------ | ------------------------- | ------------------------------------------------------- |
| All tools    | `unavailable`             | The tool is temporarily unavailable                     |
| All tools    | `execution_time_exceeded` | The tool invocation exceeded the maximum execution time |
| All tools    | `invalid_tool_input`      | Invalid parameters provided to the tool                 |
| All tools    | `too_many_requests`       | Rate limit exceeded for tool usage                      |
| bash         | `output_file_too_large`   | Command output exceeded the maximum size                |
| text\_editor | `file_not_found`          | File doesn't exist (for view/edit operations)           |

An expired container can't be reused: requests that reference it return an error instead of restoring it. Send the request again without the `container` parameter to get a new container.

### `pause_turn` stop reason

The response might include a `pause_turn` stop reason, which indicates that the API paused a long-running turn. You may provide the response back as-is in a subsequent request to let Claude continue its turn, or modify the content if you want to interrupt the conversation.


## Containers

Source: https://platform.claude.com/llms-full.txt#containers

The code execution tool runs in a secure, containerized environment designed specifically for code execution, with a higher focus on Python.

### Runtime environment

* **Python version:** 3.11
* **Operating system:** Linux-based container
* **Architecture:** x86\_64 (AMD64)

### Resource limits

* **Memory:** 5 GiB RAM
* **Disk space:** 5 GiB workspace storage
* **CPU:** 1 CPU
* **Execution time:** A tool invocation that runs past the maximum execution time returns an `execution_time_exceeded` [error](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#errors). With [programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling), each REPL cell also has a 90-second wall-clock limit

### Networking and security

* **Internet access:** Completely disabled for security
* **External connections:** No outbound network requests permitted
* **Sandbox isolation:** Full isolation from host system and other containers
* **File access:** Limited to workspace directory only
* **Workspace scoping:** Like the [Files API](https://platform.claude.com/docs/en/build-with-claude/files), containers are scoped to the request's workspace
* **Expiration:** Containers expire 30 days after creation

### Pre-installed libraries

The sandboxed Python environment includes these commonly used libraries:

* **Data science:** pandas, numpy, scipy, scikit-learn, statsmodels
* **Visualization:** matplotlib, seaborn
* **File processing:** pyarrow, openpyxl, xlsxwriter, xlrd, pillow, python-pptx, python-docx, pypdf, pdfplumber, pypdfium2, pdf2image, pdfkit, tabula-py, reportlab\[pycairo], Img2pdf
* **Math and computing:** sympy, mpmath
* **Utilities:** tqdm, python-dateutil, pytz, joblib

The container also includes command-line tools such as unzip, unrar, 7zip, bc, rg (ripgrep), fd, and sqlite.

The container has no internet access, so Claude can't download or install additional packages at runtime: only the pre-installed libraries are available.


## Container reuse

Source: https://platform.claude.com/llms-full.txt#container-reuse

You can reuse an existing container across multiple API requests by providing the container ID from a previous response. This allows you to maintain created files between requests. With `code_execution_20260120` or later and [programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling), the Python interpreter state persists as well.

Containers expire 30 days after creation. After about 5 minutes of inactivity a container is checkpointed, and sending a request with its ID inside the 30-day window restores it. The `expires_at` timestamp in the response's `container` object is a shorter rolling value and doesn't report the 30-day limit. A container that has expired can't be reused. Send the request again without the `container` parameter to get a new container.

### Example

<CodeGroup>
  ```bash cURL
  # First request: Create a file with a random number, capturing the container ID (using jq)
  CONTAINER_ID=$(curl -s https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [{
        "role": "user",
        "content": "Write a file with a random number and save it to \"/tmp/number.txt\""
      }],
      "tools": [{
        "type": "code_execution_20250825",
        "name": "code_execution"
      }]
    }' | jq -r '.container.id')

  # Second request: Reuse the container to read the file
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "container": "'"$CONTAINER_ID"'",
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [{
        "role": "user",
        "content": "Read the number from \"/tmp/number.txt\" and calculate its square"
      }],
      "tools": [{
        "type": "code_execution_20250825",
        "name": "code_execution"
      }]
    }'

bash CLI
  # First request: Create a file with a random number
  CONTAINER_ID=$(ant messages create \
    --model claude-opus-5 \
    --max-tokens 4096 \
    --message '{role: user, content: Write a file with a random number and save it to "/tmp/number.txt"}' \
    --tool '{type: code_execution_20250825, name: code_execution}' \
    --transform container.id --raw-output)

  # Second request: Reuse the container to read the file
  ant messages create \
    --container "$CONTAINER_ID" \
    --model claude-opus-5 \
    --max-tokens 4096 \
    --message '{role: user, content: Read the number from "/tmp/number.txt" and calculate its square}' \
    --tool '{type: code_execution_20250825, name: code_execution}'

python Python
  client = anthropic.Anthropic()

  # First request: create a file with a random number in a new container
  response1 = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": "Write a file with a random number and save it to '/tmp/number.txt'",
          }
      ],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

  # Second request: pass the container ID back so Claude reuses the same container
  response2 = client.messages.create(
      container=response1.container.id,
      model="claude-opus-5",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": "Read the number from '/tmp/number.txt' and calculate its square",
          }
      ],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

  print(response2.to_json())

typescript TypeScript
  const client = new Anthropic();

  // First request: Claude creates a file inside a fresh code execution container
  const response1 = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Write a file with a random number and save it to '/tmp/number.txt'"
      }
    ],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });

  // The response includes the container once the code execution tool has run
  if (!response1.container) {
    throw new Error("Expected the first response to include a container");
  }

  // Second request: pass the container ID back so it reuses the same container
  const response2 = await client.messages.create({
    container: response1.container.id,
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      { role: "user", content: "Read the number from /tmp/number.txt and calculate its square" }
    ],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });

  console.log(JSON.stringify(response2));

csharp C#
  AnthropicClient client = new();

  // First request: Claude creates a file inside a fresh code execution container
  var response1 = await client.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 4096,
      Messages = [new() { Role = Role.User, Content = "Write a file with a random number and save it to '/tmp/number.txt'" }],
      Tools = [new CodeExecutionTool20250825()]
  });

  // Second request: pass the container ID back so Claude reuses the same container
  var response2 = await client.Messages.Create(new()
  {
      Container = response1.Container!.ID,
      Model = Model.ClaudeOpus5,
      MaxTokens = 4096,
      Messages = [new() { Role = Role.User, Content = "Read the number from '/tmp/number.txt' and calculate its square" }],
      Tools = [new CodeExecutionTool20250825()]
  });

  Console.WriteLine(response2);

go Go
  client := anthropic.NewClient()
  ctx := context.Background()

  codeExecution := []anthropic.ToolUnionParam{
  	{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  }

  // First request: create a file with a random number in a new container
  response1, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Write a file with a random number and save it to '/tmp/number.txt'")),
  	},
  	Tools: codeExecution,
  })
  if err != nil {
  	log.Fatal(err)
  }

  // Reuse the container from the first request so the file is still there.
  response2, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfString: anthropic.String(response1.Container.ID),
  	},
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Read the number from '/tmp/number.txt' and calculate its square")),
  	},
  	Tools: codeExecution,
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(response2.RawJSON())

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  // First request: create a file with a random number in a new container
  MessageCreateParams params1 = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(4096L)
      .addUserMessage("Write a file with a random number and save it to '/tmp/number.txt'")
      .addTool(CodeExecutionTool20250825.builder().build())
      .build();

  Message response1 = client.messages().create(params1);

  // Second request: pass the container ID back so it reuses the same container
  MessageCreateParams params2 = MessageCreateParams.builder()
      .container(response1.container().orElseThrow().id())
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(4096L)
      .addUserMessage("Read the number from '/tmp/number.txt' and calculate its square")
      .addTool(CodeExecutionTool20250825.builder().build())
      .build();

  Message response2 = client.messages().create(params2);
  IO.println(ObjectMappers.jsonMapper().valueToTree(response2));

php PHP
  $client = new Client();

  // First request: Claude writes the file inside a fresh code execution container
  $response1 = $client->messages->create(
      maxTokens: 4096,
      messages: [
          [
              'role' => 'user',
              'content' => "Write a file with a random number and save it to '/tmp/number.txt'",
          ],
      ],
      model: Model::CLAUDE_OPUS_5,
      tools: [new CodeExecutionTool20250825()],
  );

  // Second request: reuse the container so '/tmp/number.txt' is still there
  $response2 = $client->messages->create(
      container: $response1->container->id,
      maxTokens: 4096,
      messages: [
          [
              'role' => 'user',
              'content' => "Read the number from '/tmp/number.txt' and calculate its square",
          ],
      ],
      model: Model::CLAUDE_OPUS_5,
      tools: [new CodeExecutionTool20250825()],
  );

  echo json_encode($response2), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  # First request: Claude creates the file inside a fresh code execution container
  response1 = client.messages.create(
    model: Anthropic::Model::CLAUDE_OPUS_5,
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Write a file with a random number and save it to '/tmp/number.txt'"
      }
    ],
    tools: [Anthropic::CodeExecutionTool20250825.new]
  )

  # Second request: pass the container ID back so Claude reuses the same container
  response2 = client.messages.create(
    container: response1.container.id,
    model: Anthropic::Model::CLAUDE_OPUS_5,
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Read the number from '/tmp/number.txt' and calculate its square"
      }
    ],
    tools: [Anthropic::CodeExecutionTool20250825.new]
  )

  puts response2.to_json
  ```
</CodeGroup>


## Using code execution with other execution tools

Source: https://platform.claude.com/llms-full.txt#using-code-execution-with-other-execution-tools

When you provide code execution alongside client-provided tools that also run code (such as a [Bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool) or custom REPL), Claude is operating in a multicomputer environment. The code execution tool runs in Anthropic's sandboxed container, while your client-provided tools run in a separate environment that you control. Claude can sometimes confuse these environments, attempting to use the wrong tool or assuming state is shared between them.

To avoid this, add instructions to your system prompt that clarify the distinction:

```text wrap
When multiple code execution environments are available, be aware that:
- Variables, files, and state do NOT persist between different execution environments
- Use the code_execution tool for general-purpose computation in Anthropic's sandboxed environment
- Use client-provided execution tools (e.g., bash) when you need access to the user's local system, files, or data
- If you need to pass results between environments, explicitly include outputs in subsequent tool calls rather than assuming shared state
```

This is especially important when combining code execution with [web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) or [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool), which enable code execution automatically. If your application already provides a client-side shell tool, the automatic code execution creates a second execution environment that Claude needs to distinguish between.

When Claude calls one of your client tools alongside code execution, the API returns the code execution call without its result. The result arrives in a later response, after you send back the `tool_result` blocks for your client tools.


## Streaming

Source: https://platform.claude.com/llms-full.txt#streaming-2

With [streaming](https://platform.claude.com/docs/en/build-with-claude/streaming) enabled (`"stream": true`), you'll receive code execution events as they occur. The sub-tool input streams as `input_json_delta` events, and each result block arrives whole in a single `content_block_start` event:


## Batch requests

Source: https://platform.claude.com/llms-full.txt#batch-requests

You can include the code execution tool in the [Messages Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing). Code execution tool calls through the Messages Batches API are priced the same as those in regular Messages API requests.


## Usage and pricing

Source: https://platform.claude.com/llms-full.txt#usage-and-pricing

**Code execution is free when used with web search or web fetch.** When `web_search_20260209` (or later) or `web_fetch_20260209` (or later) is included in your API request, there are no additional charges for code execution tool calls beyond the standard input and output token costs.

When used without these tools, code execution is billed by execution time, tracked separately from token usage:

* Execution time has a minimum of 5 minutes
* Each organization receives **1,550 free hours** of usage per month
* Additional usage beyond 1,550 hours is billed at **$0.05 USD per hour, per container**
* If files are included in the request, execution time is billed even if the tool is not called, because files are preloaded onto the container

Code execution usage is tracked in the response:


## Upgrade to latest tool version

Source: https://platform.claude.com/llms-full.txt#upgrade-to-latest-tool-version

The latest tool version is `code_execution_20260521`. To move between the three current versions, update the `type` string in your request: all three return the response blocks documented in [Response format](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#response-format). See [Tool versions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#tool-versions) for what each version adds and [Compatibility](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#compatibility) for the models that support them.

The rest of this section covers migrating from the legacy Python-only `code_execution_20250522` to the current tool versions.

### What's changed

| Component      | Legacy                      | Current                                                             |
| -------------- | --------------------------- | ------------------------------------------------------------------- |
| Beta header    | `code-execution-2025-05-22` | None required                                                       |
| Tool type      | `code_execution_20250522`   | `code_execution_20250825` or later                                  |
| Capabilities   | Python only                 | Bash commands, file operations                                      |
| Response types | `code_execution_result`     | `bash_code_execution_result`, `text_editor_code_execution_*_result` |

### Backward compatibility

* All existing Python code execution continues to work exactly as before
* No changes required to existing Python-only workflows

### Upgrade steps

To upgrade, update the tool type in your API requests:

**Review response handling** (if parsing responses programmatically):

* The API no longer sends the previous blocks for Python execution responses
* Instead, the API sends new response types for Bash and file operations (see [Response format](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#response-format))


## Data retention

Source: https://platform.claude.com/llms-full.txt#data-retention-3

Code execution runs in server-side sandbox containers. Container data, including execution artifacts, uploaded files, and outputs, is retained for up to 30 days. This retention applies to all data processed within the container environment. Files that code execution creates in the [Files API](https://platform.claude.com/docs/en/build-with-claude/files) (retrievable with `client.files.download()`) persist until explicitly deleted.

For ZDR eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-27

<CardGroup cols={2}>
  <Card title="Advisor tool" icon="compass" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool">
    Pair a faster executor model with a higher-intelligence advisor model that provides strategic guidance mid-generation.
  </Card>

  <Card title="Programmatic tool calling" icon="code" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling">
    Call your own tools from code that runs inside the code execution container.
  </Card>

  <Card title="Files API" icon="file" href="https://platform.claude.com/docs/en/build-with-claude/files">
    Upload files for analysis and download the files that code execution creates.
  </Card>

  <Card title="Using Agent Skills with the API" icon="book" href="https://platform.claude.com/docs/en/build-with-claude/skills-guide">
    Learn how to use Agent Skills to extend Claude's capabilities through the API.
  </Card>
</CardGroup>


---
title: Computer use tool
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
description: Give Claude screenshot, mouse, and keyboard control of a desktop environment with the computer use tool, the computer_toolset_20260801 client toolset.
---


## Compatibility

Source: https://platform.claude.com/llms-full.txt#compatibility-7

- [ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): eligible (excludes [Covered Models](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements))
- Supported models: `claude-fable-5-1`, `claude-mythos-5-1`, `claude-fable-5`, `claude-mythos-5`, `claude-opus-5`, `claude-sonnet-5`, `claude-opus-4-8`
- Platforms: Claude API, Claude Platform on AWS (beta), Amazon Bedrock (beta), Google Cloud, Microsoft Foundry (beta)
- Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 4.6, and Claude Opus 4.5 support computer use only through the earlier `computer_20251124` tool version, which requires a beta header; see [Earlier tool versions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#earlier-tool-versions).
- Platforms other than the Claude API and Google Cloud currently offer only the [earlier beta tool versions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#earlier-tool-versions).

Claude can interact with computer environments through the computer use tool, which provides screenshot capabilities and mouse/keyboard control for autonomous desktop interaction.

The computer use tool is an Anthropic-defined [client toolset](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets): one `{"type": "computer_toolset_20260801"}` entry in `tools` gives Claude 17 member tools such as `screenshot`, `left_click`, `type`, and `zoom`, and your application runs every call in an environment you control. It isn't currently available in [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/tools). Claude's calls are `tool_use` blocks whose `name` is the member and which carry `"toolset_name": "computer"`, often several per turn (a [batch action](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#batch-actions)).

For tasks that stay inside webpages, the [browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) is the closer fit: its member tools read and act on the page itself, and it doesn't need a full desktop environment.

<Note>
  Computer use is available on the Claude API and [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai) as the `computer_toolset_20260801` toolset; see [Compatibility](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#compatibility) for the supported models.

  Existing `computer_20251124` integrations keep working, and earlier tool versions remain available in beta for models and platforms that don't support the toolset. See [Migrate from `computer_20251124`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#migrate-from-computer-20251124) to upgrade, or [Earlier tool versions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#earlier-tool-versions) for the beta headers.
</Note>


## Security considerations

Source: https://platform.claude.com/llms-full.txt#security-considerations-2

Computer use has unique risks distinct from standard API features. These risks are heightened when interacting with the internet.

<Warning>
  To minimize risks, consider taking precautions such as:

  1. Using a dedicated virtual machine or container with minimal privileges to prevent direct system attacks or accidents.
  2. Avoiding giving the model access to sensitive data, such as account login information, to prevent information theft.
  3. Limiting internet access to an allowlist of domains to reduce exposure to malicious content.
  4. Asking a human to confirm decisions that might result in meaningful real-world consequences and any tasks requiring affirmative consent, such as accepting cookies, completing financial transactions, or agreeing to terms of service.
</Warning>

In some circumstances, Claude will follow commands found in content even when they conflict with your instructions. For example, instructions on webpages or contained in images might override your instructions or cause Claude to make mistakes. Take precautions to isolate Claude from sensitive data and actions to avoid risks related to prompt injection.

Anthropic has trained the model to resist these prompt injections and has added an extra layer of defense. If you use the computer use tools, classifiers will automatically run on your prompts to flag potential instances of prompt injections. When these classifiers identify potential prompt injections in screenshots, they will automatically steer the model to ask for user confirmation before proceeding with the next action. This extra protection won't be ideal for every use case (for example, use cases without a human in the loop), so if you'd like to opt out and turn it off, [contact support](https://support.claude.com/en/).

These precautions remain important even with the classifier defense layer in place.

Inform end users of relevant risks and obtain their consent prior to enabling computer use in your own products.


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-5

Add the computer use toolset to the `tools` array of a [Messages API](https://platform.claude.com/docs/en/api/messages/create) request as `{"type": "computer_toolset_20260801"}`. The request needs no beta header. This example also declares the [text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool) and [bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool), which Claude typically uses alongside computer use:

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
          "type": "computer_toolset_20260801"
        },
        {
          "type": "text_editor_20250728",
          "name": "str_replace_based_edit_tool"
        },
        {
          "type": "bash_20250124",
          "name": "bash"
        }
      ],
      "messages": [
        {
          "role": "user",
          "content": "Save a picture of a cat to my desktop."
        }
      ]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tools:
    - type: computer_toolset_20260801
    - type: text_editor_20250728
      name: str_replace_based_edit_tool
    - type: bash_20250124
      name: bash
  messages:
    - role: user
      content: Save a picture of a cat to my desktop.
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[
          {"type": "computer_toolset_20260801"},
          {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"},
          {"type": "bash_20250124", "name": "bash"},
      ],
      messages=[{"role": "user", "content": "Save a picture of a cat to my desktop."}],
  )
  print(response)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [
      {
        type: "computer_toolset_20260801"
      },
      {
        type: "text_editor_20250728",
        name: "str_replace_based_edit_tool"
      },
      {
        type: "bash_20250124",
        name: "bash"
      }
    ],
    messages: [{ role: "user", content: "Save a picture of a cat to my desktop." }]
  });

  console.log(response);

csharp C#
  var client = new AnthropicClient();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools =
      [
          new ComputerToolset20260801(),
          new ToolTextEditor20250728(),
          new ToolBash20250124(),
      ],
      Messages =
      [
          new MessageParam
          {
              Role = Role.User,
              Content = "Save a picture of a cat to my desktop.",
          },
      ],
  };

  var response = await client.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{
  		{OfComputerToolset20260801: &anthropic.ComputerToolset20260801Param{}},
  		{OfTextEditor20250728: &anthropic.ToolTextEditor20250728Param{}},
  		{OfBashTool20250124: &anthropic.ToolBash20250124Param{}},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Save a picture of a cat to my desktop.")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  import com.anthropic.models.messages.ComputerToolset20260801;
  // ...
  import com.anthropic.models.messages.ToolBash20250124;
  import com.anthropic.models.messages.ToolTextEditor20250728;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addTool(ComputerToolset20260801.builder().build())
          .addTool(ToolTextEditor20250728.builder().build())
          .addTool(ToolBash20250124.builder().build())
          .addUserMessage("Save a picture of a cat to my desktop.")
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => 'Save a picture of a cat to my desktop.'],
      ],
      model: 'claude-opus-5',
      tools: [
          ['type' => 'computer_toolset_20260801'],
          [
              'type' => 'text_editor_20250728',
              'name' => 'str_replace_based_edit_tool',
          ],
          [
              'type' => 'bash_20250124',
              'name' => 'bash',
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
      { type: "computer_toolset_20260801" },
      {
        type: "text_editor_20250728",
        name: "str_replace_based_edit_tool"
      },
      {
        type: "bash_20250124",
        name: "bash"
      }
    ],
    messages: [
      { role: "user", content: "Save a picture of a cat to my desktop." }
    ]
  )

  puts response

json Output
{
  "id": "msg_01UZ3bXcQH8mTqNhVfL9eK2p",
  "type": "message",
  "role": "assistant",
  "model": "claude-opus-5",
  "content": [
    {
      "type": "text",
      "text": "I'll open the web browser to find a picture of a cat."
    },
    {
      "type": "tool_use",
      "id": "toolu_01WkoTUvSHDzTBu2xnGk8Ep8",
      "name": "left_click",
      "toolset_name": "computer",
      "input": { "coordinate": [512, 742] }
    },
    {
      "type": "tool_use",
      "id": "toolu_017nJn3RgSCkTMwuZDb4uUov",
      "name": "screenshot",
      "toolset_name": "computer",
      "input": {}
    }
  ],
  "stop_reason": "tool_use",
  "stop_sequence": null
}
```

Your application runs each call in order in your own environment, returns one `tool_result` block per `tool_use` block, and calls the API again; [How computer use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#how-computer-use-works) describes that loop, and the rest of this page shows how to implement it.

***
