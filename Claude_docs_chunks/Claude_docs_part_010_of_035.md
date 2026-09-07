# platform.claude.com Documentation (Part 10 of 35)

## Client-side compaction (SDK)

Source: https://platform.claude.com/llms-full.txt#client-side-compaction-sdk

<Warning>
  **Anthropic recommends server-side compaction over SDK compaction.** [Server-side compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) handles context management automatically with less integration complexity, better token usage calculation, and no client-side limitations. Use SDK compaction only if you specifically need client-side control over the summarization process.

  The `compaction_control` parameter is deprecated in the TypeScript and Ruby SDKs and will be removed in a future version. The SDKs emit a deprecation warning when it is enabled. The Python SDK removed it in v1.0. To use server-side compaction with a tool runner, pass the `compact_20260112` edit in the request's `context_management` parameter.
</Warning>

<Note>
  Compaction is available in the [TypeScript and Ruby SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) when using the [`tool_runner` method](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner).
</Note>

Compaction is an SDK feature that automatically manages conversation context by generating summaries when token usage grows too large. Unlike server-side context editing strategies that clear content, compaction instructs Claude to summarize the conversation history, then replaces the full history with that summary. This allows Claude to continue working on long-running tasks that would otherwise exceed the [context window](https://platform.claude.com/docs/en/build-with-claude/context-windows).

### How compaction works

When compaction is enabled, the SDK monitors token usage after each model response:

1. **Threshold check:** The SDK calculates total tokens as `input_tokens + cache_creation_input_tokens + cache_read_input_tokens + output_tokens` (see [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) for the cache token fields).
2. **Summary generation:** When the threshold is exceeded, a summary prompt is injected as a user turn, and Claude generates a structured summary wrapped in `<summary></summary>` tags.
3. **Context replacement:** The SDK extracts the summary and replaces the entire message history with it.
4. **Continuation:** The conversation resumes from the summary, with Claude picking up where it left off.

### Using compaction

Add `compaction_control` to your `tool_runner` call to enable automatic summarization when token usage exceeds the threshold.

<Tabs>
  <Tab title="cURL">
    <Note>
      Compaction runs client-side in the SDK `tool_runner` helpers, so it has no direct HTTP equivalent. Use [server-side compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) instead, which handles compaction on Anthropic's servers.
    </Note>
  </Tab>

  <Tab title="CLI">
    <Note>
      The CLI does not include a `tool_runner` helper. Use [server-side compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) instead, which handles compaction on Anthropic's servers without SDK-side integration.
    </Note>
  </Tab>

  <Tab title="Python">
    <Note>
      In v1.0 and later, the Python SDK's tool runner does not support client-side `compaction_control`. Use [server-side compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) instead: it works with the tool runner by passing the `compact_20260112` edit in the request's `context_management` parameter.
    </Note>
  </Tab>

  <Tab title="TypeScript">
    ```typescript TypeScript
    const client = new Anthropic();

    const runner = client.beta.messages.toolRunner({
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: [readFile],
      messages: [{ role: "user", content: "What's in config.json?" }],
      compactionControl: { enabled: true, contextTokenThreshold: 100000 }
    });

    for await (const message of runner) {
      console.log(`Tokens used: ${message.usage.input_tokens}`);
    }

ruby Ruby
    client = Anthropic::Client.new

    runner = client.beta.messages.tool_runner(
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: [ReadFile.new],
      messages: [{ role: "user", content: "What's in config.json?" }],
      compaction_control: { enabled: true, context_token_threshold: 100000 }
    )

    runner.each_message do |message|
      puts "Tokens used: #{message.usage.input_tokens}"
    end

json
[
  { "role": "user", "content": "Analyze all files and write a report..." },
  { "role": "assistant", "content": "I'll help. Let me start by reading..." },
  {
    "role": "user",
    "content": [{ "type": "tool_result", "tool_use_id": "...", "content": "..." }]
  },
  { "role": "assistant", "content": "Based on file1.txt, I see..." },
  {
    "role": "user",
    "content": [{ "type": "tool_result", "tool_use_id": "...", "content": "..." }]
  },
  { "role": "assistant", "content": "After analyzing file2.txt..." }
  // ... 50 more exchanges like this ...
]

json
[
  {
    "role": "assistant",
    "content": "# Task Overview\nThe user requested analysis of directory files to produce a summary report...\n\n# Current State\nAnalyzed 52 files across 3 subdirectories. Key findings documented in report.md...\n\n# Important Discoveries\n- Configuration files use YAML format\n- Found 3 deprecated dependencies\n- Test coverage at 67%\n\n# Next Steps\n1. Analyze remaining files in /src/legacy\n2. Complete final report sections...\n\n# Context to Preserve\nUser prefers markdown format with executive summary first..."
  }
]

typescript TypeScript
    const client = new Anthropic();

    const runner = client.beta.messages.toolRunner({
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: [readFile],
      messages: [{ role: "user", content: "What's in config.json?" }],
      // Lower values compact more often; raise to 150000 when the task needs more context
      compactionControl: { enabled: true, contextTokenThreshold: 50000 }
    });

    for await (const message of runner) {
      console.log(`Tokens used: ${message.usage.input_tokens}`);
    }

ruby Ruby
    client = Anthropic::Client.new

    runner = client.beta.messages.tool_runner(
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: [ReadFile.new],
      messages: [{ role: "user", content: "What's in config.json?" }],
      # Lower values compact more often; raise to 150000 when the task needs more context
      compaction_control: { enabled: true, context_token_threshold: 50000 }
    )

    runner.each_message do |message|
      puts "Tokens used: #{message.usage.input_tokens}"
    end

typescript TypeScript
    const client = new Anthropic();

    const runner = client.beta.messages.toolRunner({
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: [readFile],
      messages: [{ role: "user", content: "What's in config.json?" }],
      compactionControl: {
        enabled: true,
        contextTokenThreshold: 100000,
        model: "claude-haiku-4-5"
      }
    });

    for await (const message of runner) {
      console.log(`Tokens used: ${message.usage.input_tokens}`);
    }

ruby Ruby
    client = Anthropic::Client.new

    runner = client.beta.messages.tool_runner(
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: [ReadFile.new],
      messages: [{ role: "user", content: "What's in config.json?" }],
      compaction_control: {
        enabled: true,
        context_token_threshold: 100000,
        model: "claude-haiku-4-5"
      }
    )

    runner.each_message do |message|
      puts "Tokens used: #{message.usage.input_tokens}"
    end

typescript TypeScript
    const client = new Anthropic();

    const runner = client.beta.messages.toolRunner({
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: [readFile],
      messages: [{ role: "user", content: "What's in config.json?" }],
      compactionControl: {
        enabled: true,
        contextTokenThreshold: 100000,
        summaryPrompt: `Summarize the research conducted so far, including:
    - Sources consulted and key findings
    - Questions answered and remaining unknowns
    - Recommended next steps

    Wrap your summary in <summary></summary> tags.`
      }
    });

    for await (const message of runner) {
      console.log(`Tokens used: ${message.usage.input_tokens}`);
    }

ruby Ruby
    client = Anthropic::Client.new

    runner = client.beta.messages.tool_runner(
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: [ReadFile.new],
      messages: [{ role: "user", content: "What's in config.json?" }],
      compaction_control: {
        enabled: true,
        context_token_threshold: 100000,
        summary_prompt: <<~PROMPT
          Summarize the research conducted so far, including:
          - Sources consulted and key findings
          - Questions answered and remaining unknowns
          - Recommended next steps

          Wrap your summary in <summary></summary> tags.
        PROMPT
      }
    )

    runner.each_message do |message|
      puts "Tokens used: #{message.usage.input_tokens}"
    end

text wrap
  You have been working on the task described above but have not yet completed it. Write a continuation summary that will allow you (or another instance of yourself) to resume work efficiently in a future context window where the conversation history will be replaced with this summary. Your summary should be structured, concise, and actionable. Include:

  1. Task Overview
  The user's core request and success criteria
  Any clarifications or constraints they specified

  2. Current State
  What has been completed so far
  Files created, modified, or analyzed (with paths if relevant)
  Key outputs or artifacts produced

  3. Important Discoveries
  Technical constraints or requirements uncovered
  Decisions made and their rationale
  Errors encountered and how they were resolved
  What approaches were tried that didn't work (and why)

  4. Next Steps
  Specific actions needed to complete the task
  Any blockers or open questions to resolve
  Priority order if multiple steps remain

  5. Context to Preserve
  User preferences or style requirements
  Domain-specific details that aren't obvious
  Any promises made to the user

  Be concise but complete—err on the side of including information that would prevent duplicate work or repeated mistakes. Write in a way that enables immediate resumption of the task.

  Wrap your summary in <summary></summary> tags.

json Output
{
  "usage": {
    "input_tokens": 63000,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 270000,
    "output_tokens": 1400
  }
}

typescript TypeScript
    let prevMsgCount = 0;
    for await (const message of runner) {
      const currMsgCount = runner.params.messages.length;
      if (currMsgCount < prevMsgCount) {
        console.log(`Compaction occurred: ${prevMsgCount} -> ${currMsgCount} messages`);
        console.log(`Input tokens after compaction: ${message.usage.input_tokens}`);
      }
      prevMsgCount = currMsgCount;
    }

ruby Ruby
    client = Anthropic::Client.new

    runner = client.beta.messages.tool_runner(
      model: "claude-opus-5",
      max_tokens: 1024,
      tools: [ReadFile.new],
      messages: [{ role: "user", content: "What's in config.json?" }],
      compaction_control: {
        enabled: true,
        context_token_threshold: 100000,
        on_compact: ->(tokens_before, tokens_after) do
          puts "Compaction occurred: #{tokens_before} -> #{tokens_after} tokens"
        end
      }
    )

    runner.each_message do |message|
      puts "Tokens: #{message.usage.input_tokens}"
    end
    ```
  </Tab>
</Tabs>

### When to use compaction

**Good use cases:**

* Long-running agent tasks that process many files or data sources
* Research workflows that accumulate large amounts of information
* Multistep tasks with clear, measurable progress
* Tasks that produce artifacts (files, reports) that persist outside the conversation

**Less ideal use cases:**

* Tasks requiring precise recall of early conversation details
* Workflows using server-side tools extensively
* Tasks that need to maintain exact state across many variables


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-49

<CardGroup cols={2}>
  <Card title="Compaction" icon="arrows-clockwise" href="https://platform.claude.com/docs/en/build-with-claude/compaction">
    Manage long conversations with server-side compaction, the recommended strategy for most use cases.
  </Card>

  <Card title="Prompt caching" icon="database" href="https://platform.claude.com/docs/en/build-with-claude/prompt-caching">
    Reduce cost and latency by caching prompt prefixes, and learn how context editing interacts with the cache.
  </Card>
</CardGroup>


---
title: Context windows
url: https://platform.claude.com/docs/en/build-with-claude/context-windows
description: Understand how the context window works, how extended thinking and tool use count toward it, and how to manage context as conversations grow.
---

As conversations grow, you'll eventually approach context window limits. For long-running conversations and agentic workflows, [server-side compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) is the primary strategy for context management.


## How the context window works

Source: https://platform.claude.com/llms-full.txt#how-the-context-window-works

The "context window" refers to all the text a language model can reference when generating a response, including the response itself. This is different from the large corpus of data the language model was trained on, and instead represents a "working memory" for the model. A larger context window allows the model to handle more complex and lengthy prompts, but more context isn't automatically better. As token count grows, accuracy and recall degrade, a phenomenon known as *context rot*. This makes curating what's in context just as important as how much space is available.

<Tip>
  For more on why long contexts degrade and how to engineer around it, see [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
</Tip>

The following diagram illustrates the standard context window behavior for API requests1:

![Diagram of turns accumulating in the context window until the conversation approaches the token limit](https://platform.claude.com/docs/images/context-window.svg)

*1 Chat interfaces such as [claude.ai](https://claude.ai/) can also manage the context window on a rolling "first in, first out" basis.*

* **Progressive token accumulation:** As the conversation advances through turns, each user message and assistant response accumulates within the context window, and previous turns are preserved completely.

* **Context window capacity:** The context window ([up to 1M tokens, depending on the model](https://platform.claude.com/docs/en/build-with-claude/context-windows#context-window-sizes-by-model)) holds the conversation history plus the new output Claude generates.

* **Input-output flow:** Each turn consists of:

  * **Input phase:** Contains all previous conversation history plus the current user message
  * **Output phase:** Generates a text response that becomes part of the input for the next turn

Everything in the request counts toward the context window: the system prompt, every message in `messages` (including tool results, images, and documents), and your tool definitions. The output Claude generates for the turn, including its extended thinking, counts too. Every response reports what the request consumed in its `usage` field. If you use [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), the input count is split across `input_tokens`, `cache_read_input_tokens`, and `cache_creation_input_tokens`, and all three count toward the window. To estimate a request before you send it, use the [token counting API](https://platform.claude.com/docs/en/build-with-claude/token-counting).


## Context window sizes by model

Source: https://platform.claude.com/llms-full.txt#context-window-sizes-by-model

Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, Claude Opus 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, Claude Sonnet 4.6, and [Claude Mythos Preview](https://anthropic.com/glasswing) have a 1M-token context window. A single request to any of them can generate up to 128k output tokens (`max_tokens`). Other Claude models, including Claude Sonnet 4.5, have a 200k-token context window.

For every model with a 1M-token context window, 1M is the default: you don't need a beta header, and long-context requests are billed at [standard pricing](https://platform.claude.com/docs/en/about-claude/pricing#long-context-pricing).

A single request can include up to 600 images or PDF pages (100 for models with a 200k-token context window). If you send many images or large documents, you might reach [request size limits](https://platform.claude.com/docs/en/api/overview#request-size-limits) before the token limit.

See the [model comparison](https://platform.claude.com/docs/en/models/overview#latest-models-comparison) table for a list of context window sizes by model.


## The context window with thinking

Source: https://platform.claude.com/llms-full.txt#the-context-window-with-thinking

With [thinking](https://platform.claude.com/docs/en/build-with-claude/thinking), all input and output tokens, including thinking tokens, count toward the context window limit, with a few nuances in multi-turn situations.

Thinking tokens are a subset of your `max_tokens` parameter, are billed as output tokens, and count toward rate limits. With [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking), Claude determines its thinking allocation dynamically, so thinking token usage varies from request to request.

Whether thinking blocks from previous assistant turns stay in the context window depends on the model. On Claude Opus 4.5 and later Opus models, Claude Sonnet 4.6 and later Sonnet models, Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, and Claude Mythos Preview, the API keeps previous thinking blocks by default, and they count toward the context window like any other input tokens. On earlier Opus and Sonnet models and all Haiku models, the API automatically strips previous thinking blocks from the conversation history when you pass them back, which preserves token capacity for conversation content. For the per-model defaults, see [thinking block preservation by model](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-block-preservation-by-model). To override the default in either direction, use [thinking block clearing](https://platform.claude.com/docs/en/build-with-claude/context-editing#thinking-block-clearing).

The following diagram shows how tokens are managed when thinking is enabled on a model that strips previous thinking blocks:

![Diagram of thinking on a model that strips previous thinking blocks: each turn's thinking block is generated in the output and not carried into later turns' input](https://platform.claude.com/docs/images/context-window-thinking.svg)

* **Stripping thinking blocks:** On models that strip previous thinking blocks, thinking blocks (shown in dark gray) are generated during each turn's output phase but are not carried forward as input tokens for subsequent turns. You do not need to strip the thinking blocks yourself: if you pass them back, the Claude API strips them automatically.
* **Billing:** Thinking tokens are billed as output tokens once, when they are generated. On models that keep previous thinking blocks, the kept blocks are then part of later requests' input and are billed as input tokens, like the rest of the conversation history.

<Note>
  You can read more about the context window and thinking in the [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) guide.
</Note>


## The context window with thinking and tool use

Source: https://platform.claude.com/llms-full.txt#the-context-window-with-thinking-and-tool-use

The following diagram illustrates how tokens are managed when you combine thinking with tool use on a model that strips previous thinking blocks:

![Diagram of thinking with tool use: thinking is kept with its tool result, then dropped on the next user turn on models that strip previous thinking blocks](https://platform.claude.com/docs/images/context-window-thinking-tools.svg)

<Steps>
  <Step title="First turn architecture">
    * **Input components:** Tools configuration and user message
    * **Output components:** Thinking + text response + tool use request
    * **Token calculation:** All input and output components count toward the context window, and all output components are billed as output tokens.
  </Step>

  <Step title="Tool result handling (turn 2)">
    * **Input components:** Every block in the first turn and the `tool_result`. You must return the thinking block with the corresponding tool results. This is the only case where you have to return thinking blocks.
    * **Output components:** After tool results have been passed back to Claude, Claude responds with only text (no additional thinking until the next `user` message, unless [interleaved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#interleaved-thinking) is enabled).
    * **Token calculation:** All input and output components count toward the context window, and all output components are billed as output tokens.
  </Step>

  <Step title="New user turn (turn 3)">
    * **Input components:** All inputs and the output from the previous turn are carried forward. The thinking block from the completed tool use cycle no longer has to stay in context: on models that strip previous thinking blocks, the API drops it automatically when you pass it back, and on models that keep previous thinking blocks, it stays unless you clear it with [thinking block clearing](https://platform.claude.com/docs/en/build-with-claude/context-editing#thinking-block-clearing). This is also where you add the next `user` turn.
    * **Output components:** Because there is a new `user` turn outside the tool use cycle, Claude generates a new thinking block and continues from there.
    * **Token calculation:** On models that strip previous thinking blocks, the previous thinking tokens no longer count toward the context window. All other previous blocks still count toward the context window, as does the thinking block in the current `assistant` turn.
  </Step>
</Steps>

* **Considerations for tool use with thinking:**

  * When you post tool results, you must include the entire unmodified thinking block that accompanies that tool request, including its signature.
  * The API uses cryptographic signatures to verify thinking block authenticity. If you modify a thinking block, the API returns an error.

<Note>
  Most current Claude models support [interleaved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#interleaved-thinking), which lets Claude think between tool calls, including after it receives tool results. It is automatic on models with adaptive thinking; Claude Opus 4.5, Claude Sonnet 4.5, and earlier Claude 4 models require the `interleaved-thinking-2025-05-14` beta header, and Claude Haiku 4.5 does not support it.

  For more information about using tools with thinking, see [Thinking with tool use](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-with-tool-use).
</Note>

To reduce the context consumed by the tool definitions themselves, see [Manage tool context](https://platform.claude.com/docs/en/agents-and-tools/tool-use/manage-tool-context), or defer tool definitions with the [tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool).


## Context awareness

Source: https://platform.claude.com/llms-full.txt#context-awareness

Claude Sonnet 5, Claude Sonnet 4.6, Claude Sonnet 4.5, and Claude Haiku 4.5 have **context awareness:** these models track their remaining context window (their "token budget") throughout a conversation. This lets the model manage long-running tasks against the space that remains rather than guess how many tokens are left. Context awareness is automatic: there is nothing for you to enable, and you never send the tags shown in this section yourself. The API injects them.

### How it works

In the system prompt of every request, the API gives Claude its total context window:

The budget matches the context window available to your request: 1M tokens for Claude Sonnet 5 and Claude Sonnet 4.6, and 200k tokens for Claude Sonnet 4.5 and Claude Haiku 4.5. The examples in this section show a model with a 200k-token context window.

After each tool call, the API gives Claude an update on its remaining capacity:

Image tokens are included in these budgets.

Claude Opus 4.7 and later Opus models, Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, and Claude Mythos 5 don't receive these injected tags. On these models, you can give the model an explicit budget with [task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets), which are in beta.

<Tip>
  For agents that span multiple sessions, design your state artifacts so that context recovery is fast when a new session starts. The [memory tool's multisession pattern](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool#multisession-software-development-pattern) walks through a concrete approach. See also [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).
</Tip>

For prompting guidance on using context awareness, see [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#context-awareness-and-multiwindow-workflows).


## Manage context with compaction

Source: https://platform.claude.com/llms-full.txt#manage-context-with-compaction

If your conversations regularly approach context window limits, use [server-side compaction](https://platform.claude.com/docs/en/build-with-claude/compaction). Compaction automatically summarizes earlier parts of the conversation on the server, so the conversation can continue past the context window limit. It is available in beta for Claude 4.6 and later models and [Claude Mythos Preview](https://anthropic.com/glasswing).

For more specialized needs, [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) offers additional strategies:

* **Tool result clearing:** Clear old tool results in agentic workflows
* **Thinking block clearing:** Manage thinking blocks when you use extended thinking

Cached prompt prefixes still occupy the context window: [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) changes what you pay for those tokens, not whether they count.


## Context window overflow behavior

Source: https://platform.claude.com/llms-full.txt#context-window-overflow-behavior

If the input alone already exceeds the model's context window, the API returns a 400 `invalid_request_error` ("prompt is too long") on every model.

On Claude 4.5 models and newer, if input tokens plus `max_tokens` exceeds the context window size, the API accepts the request. If generation then reaches the context window limit, it stops with `stop_reason: "model_context_window_exceeded"`. On earlier models, the API returns a [validation error](https://platform.claude.com/docs/en/api/errors) instead. To opt in to the `model_context_window_exceeded` behavior on those models, use the `model-context-window-exceeded-2025-08-26` beta header. See [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons) for details.

To stay within context window limits, use the [token counting API](https://platform.claude.com/docs/en/build-with-claude/token-counting) to estimate token usage before sending messages to Claude.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-50

<CardGroup cols={2}>
  <Card title="Compaction" icon="stack" href="https://platform.claude.com/docs/en/build-with-claude/compaction">
    Server-side context compaction for managing long conversations that approach context window limits.
  </Card>

  <Card title="Context editing" icon="edit" href="https://platform.claude.com/docs/en/build-with-claude/context-editing">
    Automatically manage conversation context as it grows with context editing.
  </Card>

  <Card title="Model comparison table" icon="scales" href="https://platform.claude.com/docs/en/models/overview#latest-models-comparison">
    See the model comparison table for a list of context window sizes and input/output token pricing by model.
  </Card>

  <Card title="Thinking" icon="settings" href="https://platform.claude.com/docs/en/build-with-claude/thinking">
    Give Claude enhanced reasoning for complex tasks and control how thinking content is returned.
  </Card>
</CardGroup>


---
title: Mid-conversation system messages and tool changes
url: https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages
description: Change system instructions or tool availability partway through a conversation without invalidating the cached prefix that came before them.
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

System instructions normally live in the top-level `system` field, ahead of every message in the conversation. That position is great for [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching): the system prompt is part of the stable prefix, so subsequent turns hit the cache. It is a poor position for instructions you only discover you need partway through a session, because editing the top-level `system` field changes the very beginning of the prompt and invalidates the cache for everything that follows.

Mid-conversation system messages close that gap. You append a `{"role": "system"}` message at the point in the conversation where the new instruction becomes relevant, instead of editing the top-level `system` field. The cached prefix stays the same, so the next request still reads it from cache, and the new instruction is still applied as a system instruction rather than as ordinary user text.

<Note>
  Mid-conversation system messages are available on the Claude API, [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), and [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai).

  This feature is available on Claude Fable 5.1, [Claude Mythos 5.1](https://anthropic.com/glasswing), Claude Fable 5, [Claude Mythos 5](https://anthropic.com/glasswing), Claude Opus 4.8, and Claude Opus 5. No beta header is required for mid-conversation system messages. This feature is not available on Claude Sonnet 5. Use the top-level `system` field there instead.

  [Mid-conversation tool changes](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#mid-conversation-tool-changes) are in beta and require the `mid-conversation-tool-changes-2026-07-01` beta header. They are available on the same models, on the Claude API, Amazon Bedrock, and Google Cloud.

  [Turn-scoped system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#turn-scoped-system-messages) (`clear_at`) are in beta and require the `mid-conversation-system-clear-at-2026-08-21` beta header, on the same models and platforms as mid-conversation system messages.
</Note>


## Mid-conversation tool changes

Source: https://platform.claude.com/llms-full.txt#mid-conversation-tool-changes

The `tools` array sits even earlier in the hashed request prefix than the top-level `system` field, so editing it invalidates the [prompt cache](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) for the entire conversation. Mid-conversation tool changes are the tools counterpart to mid-conversation system messages. Instead of fixing the tool list for the lifetime of the conversation, you change which tools are offered to the model between turns: declare the full tool set in `tools` up front, then use `tool_addition` and `tool_removal` blocks to offer a tool to the model, or withdraw it, from a specific point in the conversation onward. The `tools` array itself never changes, so the cached prefix stays intact.

`tool_addition` and `tool_removal` are content blocks in the `content` array of a `role: "system"` message, and they can be mixed with `text` blocks in the same message. The message follows the same placement rules as any mid-conversation system message (see [Limitations](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#limitations)), and the change applies from that point in the conversation onward. Each block's `tool` field references a tool rather than defining one: `{"type": "tool_reference", "name": "..."}` names a tool declared in the request's `tools` array, and [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector) tools can be referenced individually with `mcp_tool_reference` (`server_name` and `name`) or as a whole toolset with `mcp_toolset_reference` (`server_name`). Referencing a name that is not declared in `tools` returns a 400 error.

Every tool declared in `tools` is offered to the model from the start of the conversation unless it is declared with `defer_loading: true`, which keeps it withheld until a `tool_addition` block surfaces it. `tool_addition` also re-offers a tool that an earlier `tool_removal` withdrew.

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: mid-conversation-tool-changes-2026-07-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "tools": [
        {
          "name": "get_weather",
          "description": "Get the current weather for a location.",
          "input_schema": {
            "type": "object",
            "properties": {
              "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
          }
        }
      ],
      "messages": [
        {
          "role": "user",
          "content": "Say OK."
        },
        {
          "role": "system",
          "content": [
            {
              "type": "tool_removal",
              "tool": {"type": "tool_reference", "name": "get_weather"}
            }
          ]
        }
      ]
    }'

bash CLI
  ant beta:messages create --beta mid-conversation-tool-changes-2026-07-01 \
    --transform 'content.#(type=="text").text' --raw-output <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  tools:
    - name: get_weather
      description: Get the current weather for a location.
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
      content: Say OK.
    - role: system
      content:
        - type: tool_removal
          tool:
            type: tool_reference
            name: get_weather
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      betas=["mid-conversation-tool-changes-2026-07-01"],
      # The full tool set is declared up front and never changes, so the
      # cached prefix stays intact.
      tools=[
          {
              "name": "get_weather",
              "description": "Get the current weather for a location.",
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "location": {"type": "string", "description": "City name"},
                  },
                  "required": ["location"],
              },
          },
      ],
      messages=[
          {
              "role": "user",
              "content": "Say OK.",
          },
          # Withdraw get_weather from this point onward. The block references
          # the tool by name instead of editing `tools`, so earlier turns stay
          # byte-identical and the cache still hits.
          {
              "role": "system",
              "content": [
                  {
                      "type": "tool_removal",
                      "tool": {"type": "tool_reference", "name": "get_weather"},
                  },
              ],
          },
      ],
  )

  for block in response.content:
      if block.type == "text":
          print(block.text)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    betas: ["mid-conversation-tool-changes-2026-07-01"],
    // The full tool set is declared up front and never changes, so the
    // cached prefix stays intact.
    tools: [
      {
        name: "get_weather",
        description: "Get the current weather for a location.",
        input_schema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "City name"
            }
          },
          required: ["location"]
        }
      }
    ],
    messages: [
      { role: "user", content: "Say OK." },
      // Withdraw get_weather from this point onward. The block references the
      // tool by name instead of editing `tools`, so earlier turns stay
      // byte-identical and the cache still hits.
      {
        role: "system",
        content: [
          {
            type: "tool_removal",
            tool: { type: "tool_reference", name: "get_weather" }
          }
        ]
      }
    ]
  });

  for (const block of response.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

csharp C#
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  AnthropicClient client = new();

  var response = await client.Beta.Messages.Create(new MessageCreateParams
  {
      Model = Messages::Model.ClaudeOpus5,
      MaxTokens = 1024,
      Betas = ["mid-conversation-tool-changes-2026-07-01"],
      // The full tool set is declared up front and never changes, so the
      // cached prefix stays intact.
      Tools =
      [
          new BetaTool
          {
              Name = "get_weather",
              Description = "Get the current weather for a location.",
              InputSchema = new InputSchema
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["location"] = JsonSerializer.SerializeToElement(new { type = "string", description = "City name" }),
                  },
                  Required = ["location"],
              },
          },
      ],
      Messages =
      [
          new() { Role = Role.User, Content = "Say OK." },
          // Withdraw get_weather from this point onward. The block references
          // the tool by name instead of editing `Tools`, so earlier turns stay
          // byte-identical and the cache still hits.
          new()
          {
              Role = Role.System,
              Content = new(
              [
                  new BetaRequestToolRemovalBlock
                  {
                      Tool = new BetaToolChangeToolReference { Name = "get_weather" },
                  },
              ]),
          },
      ],
  });

  foreach (var block in response.Content)
  {
      if (block.TryPickText(out var text))
      {
          Console.WriteLine(text.Text);
      }
  }

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Betas:     []anthropic.AnthropicBeta{"mid-conversation-tool-changes-2026-07-01"},
  	// The full tool set is declared up front and never changes, so the
  	// cached prefix stays intact.
  	Tools: []anthropic.BetaToolUnionParam{
  		{OfTool: &anthropic.BetaToolParam{
  			Name:        "get_weather",
  			Description: anthropic.String("Get the current weather for a location."),
  			InputSchema: anthropic.BetaToolInputSchemaParam{
  				Properties: map[string]any{
  					"location": map[string]any{
  						"type":        "string",
  						"description": "City name",
  					},
  				},
  				Required: []string{"location"},
  			},
  		}},
  	},
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Say OK.")),
  		// Withdraw get_weather from this point onward. The block references
  		// the tool by name instead of editing Tools, so earlier turns stay
  		// byte-identical and the cache still hits.
  		{
  			Role: anthropic.BetaMessageParamRoleSystem,
  			Content: []anthropic.BetaContentBlockParamUnion{
  				anthropic.NewBetaToolRemovalBlock(anthropic.BetaToolChangeToolReferenceParam{
  					Name: "get_weather",
  				}),
  			},
  		},
  	},
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
  import com.anthropic.models.beta.messages.BetaContentBlockParam;
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.BetaMessageParam;
  import com.anthropic.models.beta.messages.BetaRequestToolRemovalBlock;
  import com.anthropic.models.beta.messages.BetaTool;
  import com.anthropic.models.beta.messages.MessageCreateParams;
  // ...
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      // The full tool set is declared up front and never changes, so the
      // cached prefix stays intact.
      BetaTool weatherTool = BetaTool.builder()
          .name("get_weather")
          .description("Get the current weather for a location.")
          .inputSchema(BetaTool.InputSchema.builder()
              .properties(BetaTool.InputSchema.Properties.builder()
                  .putAdditionalProperty("location", JsonValue.from(Map.of(
                      "type", "string",
                      "description", "City name")))
                  .build())
              .addRequired("location")
              .build())
          .build();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .addBeta("mid-conversation-tool-changes-2026-07-01")
          .addTool(weatherTool)
          .addUserMessage("Say OK.")
          // Withdraw get_weather from this point onward. The block references
          // the tool by name instead of editing `tools`, so earlier turns stay
          // byte-identical and the cache still hits.
          .addMessage(BetaMessageParam.builder()
              .role(BetaMessageParam.Role.SYSTEM)
              .contentOfBetaContentBlockParams(List.of(
                  BetaContentBlockParam.ofToolRemoval(BetaRequestToolRemovalBlock.builder()
                      .referenceTool("get_weather")
                      .build())))
              .build())
          .build();

      BetaMessage response = client.beta().messages().create(params);
      response.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      betas: ['mid-conversation-tool-changes-2026-07-01'],
      // The full tool set is declared up front and never changes, so the
      // cached prefix stays intact.
      tools: [
          [
              'name' => 'get_weather',
              'description' => 'Get the current weather for a location.',
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'location' => [
                          'type' => 'string',
                          'description' => 'City name',
                      ],
                  ],
                  'required' => ['location'],
              ],
          ],
      ],
      messages: [
          ['role' => 'user', 'content' => 'Say OK.'],
          // Withdraw get_weather from this point onward. The block references
          // the tool by name instead of editing `tools`, so earlier turns stay
          // byte-identical and the cache still hits.
          [
              'role' => 'system',
              'content' => [
                  [
                      'type' => 'tool_removal',
                      'tool' => ['type' => 'tool_reference', 'name' => 'get_weather'],
                  ],
              ],
          ],
      ],
  );

  foreach ($response->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, PHP_EOL;
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    betas: ["mid-conversation-tool-changes-2026-07-01"],
    # The full tool set is declared up front and never changes, so the
    # cached prefix stays intact.
    tools: [
      {
        name: "get_weather",
        description: "Get the current weather for a location.",
        input_schema: {
          type: "object",
          properties: {
            location: { type: "string", description: "City name" }
          },
          required: ["location"]
        }
      }
    ],
    messages: [
      { role: "user", content: "Say OK." },
      # Withdraw get_weather from this point onward. The block references
      # the tool by name instead of editing `tools`, so earlier turns stay
      # byte-identical and the cache still hits.
      {
        role: "system",
        content: [
          {
            type: "tool_removal",
            tool: { type: "tool_reference", name: "get_weather" }
          }
        ]
      }
    ]
  )

  response.content.each do |block|
    puts block.text if block.type == :text
  end
  ```
</CodeGroup>

Mid-conversation tool changes are in beta. To use them, include the beta header `mid-conversation-tool-changes-2026-07-01` in your requests.


## When to use a mid-conversation system message

Source: https://platform.claude.com/llms-full.txt#when-to-use-a-mid-conversation-system-message

[Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) hashes the request prefix in order: `tools`, then `system`, then `messages`. A cache hit requires the prefix to match a recent request exactly, byte for byte, up to the cache breakpoint.

That ordering means the top-level `system` field sits near the very start of the hashed prefix. Any change to it, even appending a sentence, produces a different hash, and the request misses the cache for the system prompt and every cached message after it.

Mid-conversation system messages let you add the instruction at the **end** of the message history instead. Everything before the new instruction is unchanged, so the existing cache entry still matches, and only the new message is processed as fresh input.

A few situations where this matters:

* **Mid-session policy or persona changes.** A long agentic session needs a new constraint ("from now on, write all SQL as parameterized queries") after dozens of cached turns. Adding it to the top-level `system` field would re-process the entire history.
* **Per-turn context that must be authoritative.** You want to inject a freshness note, a session deadline, or a tool-availability change with system-level weight, and it changes too often to live in the cached prefix.
* **Per-turn reminders that shouldn't pile up.** A harness nudges the model after each batch of tool results ("request independent reads together", "the user hasn't heard from you in a while") and wants the model to see only the newest copy. A [turn-scoped system message](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#turn-scoped-system-messages) renders for one turn and then costs nothing, without deleting anything from the history.
* **State changes your application observes.** Your application notices something Claude should treat as an operator-level fact: files changed on disk, the user toggled an auto-approve setting, available tools changed, or the remaining token budget dropped below a threshold.
* **User input that should not interrupt an agentic loop.** A user types a follow-up while Claude is still executing tools for the previous request. Relaying it as a system message after the next tool result lets Claude fold the new input into the work it is already doing, instead of treating it as a fresh request to switch to. See [Placement after tool results](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#placement-after-tool-results).
* **Mode switches that grant standing permissions.** A session-level mode can use a mid-conversation system message to grant standing consent to an expensive capability, such as automatically launching multiagent workflows, with a short refresher every several turns and an exit notice when the mode is turned off. For a worked example, see [Build an orchestration mode](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-effort-example).

In all of these cases you could put the instruction in a regular `user` message, and Claude does follow instructions that arrive in user turns. The difference is priority: a `user` message is treated as coming from the end user, while a `system` message is treated as coming from you, the application operator. When the two conflict, system instructions take precedence, so use the `system` role for operator-level facts and constraints that should hold even if the end user asks for something different. A mid-conversation system message keeps that operator-level priority without paying the cache-miss cost of editing the top-level `system` field.


## How it works

Source: https://platform.claude.com/llms-full.txt#how-it-works-6

Add a message with `"role": "system"` to the `messages` array. Use a plain string or content blocks for `content`, the same as a `user` or `assistant` turn. The instruction applies from that point in the conversation onward. When instructions conflict, later system messages take precedence over earlier ones, and mid-conversation system messages take precedence over the top-level `system` field for the turns that follow them.

You can still set the top-level `system` field for instructions that should apply to the entire conversation. Reserve mid-conversation system messages for instructions that only become relevant later, or that you want to add without invalidating the cached prefix.

A `role: "system"` message can also carry `output_config.effort` to change the [effort](https://platform.claude.com/docs/en/build-with-claude/effort) level from the next `user` turn on. This is in beta on Claude Fable 5.1, Claude Mythos 5.1, and Claude Opus 5 on the Claude API and requires the `mid-conversation-output-config-2026-07-01` beta header. See [Per-message effort](https://platform.claude.com/docs/en/build-with-claude/effort#change-effort-mid-conversation-beta).

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "cache_control": {"type": "ephemeral"},
      "system": "You are a code review assistant. Be concise.",
      "messages": [
        {
          "role": "user",
          "content": "Review process() in utils.py for performance issues."
        },
        {
          "role": "assistant",
          "content": "The list comprehension is fine for small inputs. For large inputs, consider a generator to avoid materializing the full list."
        },
        {
          "role": "user",
          "content": "Now review the calling code that invokes process()."
        },
        {
          "role": "system",
          "content": "From now on, every suggestion must include explicit type annotations."
        }
      ]
    }'

bash CLI
  ant messages create --transform 'content.#(type=="text").text' --raw-output <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  cache_control:
    type: ephemeral
  system: You are a code review assistant. Be concise.
  messages:
    - role: user
      content: Review process() in utils.py for performance issues.
    - role: assistant
      content: >-
        The list comprehension is fine for small inputs. For large inputs,
        consider a generator to avoid materializing the full list.
    - role: user
      content: Now review the calling code that invokes process().
    - role: system
      content: From now on, every suggestion must include explicit type annotations.
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      # Automatic prompt caching: each request caches the conversation so far,
      # and the next request reads the unchanged prefix from cache.
      cache_control={"type": "ephemeral"},
      system="You are a code review assistant. Be concise.",
      messages=[
          {
              "role": "user",
              "content": "Review process() in utils.py for performance issues.",
          },
          {
              "role": "assistant",
              "content": "The list comprehension is fine for small inputs. For large inputs, consider a generator to avoid materializing the full list.",
          },
          {
              "role": "user",
              "content": "Now review the calling code that invokes process().",
          },
          # The reviewer realizes mid-session that all suggestions must
          # also pass the team's strict typing policy. Appending the
          # instruction here keeps earlier turns byte-identical, so the
          # prefix cached by the previous request is still read from cache.
          {
              "role": "system",
              "content": "From now on, every suggestion must include explicit type annotations.",
          },
      ],
  )

  for block in response.content:
      if block.type == "text":
          print(block.text)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    // Automatic prompt caching: each request caches the conversation so far,
    // and the next request reads the unchanged prefix from cache.
    cache_control: { type: "ephemeral" },
    system: "You are a code review assistant. Be concise.",
    messages: [
      {
        role: "user",
        content: "Review process() in utils.py for performance issues."
      },
      {
        role: "assistant",
        content:
          "The list comprehension is fine for small inputs. For large inputs, consider a generator to avoid materializing the full list."
      },
      {
        role: "user",
        content: "Now review the calling code that invokes process()."
      },
      // The reviewer realizes mid-session that all suggestions must also pass
      // the team's strict typing policy. Appending the instruction here keeps
      // earlier turns byte-identical, so the prefix cached by the previous
      // request is still read from cache.
      {
        role: "system",
        content: "From now on, every suggestion must include explicit type annotations."
      }
    ]
  });

  const textBlock = response.content.find(
    (block): block is Anthropic.TextBlock => block.type === "text"
  );
  console.log(textBlock?.text);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      // Automatic prompt caching: each request caches the conversation so far,
      // and the next request reads the unchanged prefix from cache.
      CacheControl = new CacheControlEphemeral(),
      System = "You are a code review assistant. Be concise.",
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = "Review process() in utils.py for performance issues."
          },
          new()
          {
              Role = Role.Assistant,
              Content = "The list comprehension is fine for small inputs. For large inputs, consider a generator to avoid materializing the full list."
          },
          new()
          {
              Role = Role.User,
              Content = "Now review the calling code that invokes process()."
          },
          // The reviewer realizes mid-session that all suggestions must also pass
          // the team's strict typing policy. Appending the instruction here keeps
          // earlier turns byte-identical, so the prefix cached by the previous
          // request is still read from cache.
          new()
          {
              Role = Role.System,
              Content = "From now on, every suggestion must include explicit type annotations."
          }
      ]
  };

  var response = await client.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	// Automatic prompt caching: each request caches the conversation so far,
  	// and the next request reads the unchanged prefix from cache.
  	CacheControl: anthropic.NewCacheControlEphemeralParam(),
  	System: []anthropic.TextBlockParam{
  		{Text: "You are a code review assistant. Be concise."},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Review process() in utils.py for performance issues.")),
  		anthropic.NewAssistantMessage(anthropic.NewTextBlock("The list comprehension is fine for small inputs. For large inputs, consider a generator to avoid materializing the full list.")),
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Now review the calling code that invokes process().")),
  		// The reviewer realizes mid-session that all suggestions must also
  		// pass the team's strict typing policy. Appending the instruction
  		// here keeps earlier turns byte-identical, so the prefix cached by
  		// the previous request is still read from cache.
  		{
  			Role: anthropic.MessageParamRoleSystem,
  			Content: []anthropic.ContentBlockParamUnion{
  				anthropic.NewTextBlock("From now on, every suggestion must include explicit type annotations."),
  			},
  		},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  for _, block := range response.Content {
  	if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  		fmt.Println(textBlock.Text)
  	}
  }

java Java
  import com.anthropic.models.messages.CacheControlEphemeral;
  // ...
  import com.anthropic.models.messages.MessageParam;
  // ...
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          // Automatic prompt caching: each request caches the conversation so far,
          // and the next request reads the unchanged prefix from cache.
          .cacheControl(CacheControlEphemeral.builder().build())
          .system("You are a code review assistant. Be concise.")
          .addUserMessage("Review process() in utils.py for performance issues.")
          .addAssistantMessage("The list comprehension is fine for small inputs. For large inputs, consider a generator to avoid materializing the full list.")
          .addUserMessage("Now review the calling code that invokes process().")
          // The reviewer realizes mid-session that all suggestions must also pass
          // the team's strict typing policy. Appending the instruction here keeps
          // earlier turns byte-identical, so the prefix cached by the previous
          // request is still read from cache.
          .addMessage(MessageParam.builder()
              .role(MessageParam.Role.SYSTEM)
              .content("From now on, every suggestion must include explicit type annotations.")
              .build())
          .build();

      Message response = client.messages().create(params);
      response.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));

php PHP
  use Anthropic\Messages\CacheControlEphemeral;
  // ...
  $client = new Client();

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => 'Review process() in utils.py for performance issues.'],
          ['role' => 'assistant', 'content' => 'The list comprehension is fine for small inputs. For large inputs, consider a generator to avoid materializing the full list.'],
          ['role' => 'user', 'content' => 'Now review the calling code that invokes process().'],
          // The reviewer realizes mid-session that all suggestions must also pass
          // the team's strict typing policy. Appending the instruction here keeps
          // earlier turns byte-identical, so the prefix cached by the previous
          // request is still read from cache.
          ['role' => 'system', 'content' => 'From now on, every suggestion must include explicit type annotations.']
      ],
      model: 'claude-opus-5',
      // Automatic prompt caching: each request caches the conversation so far,
      // and the next request reads the unchanged prefix from cache.
      cacheControl: CacheControlEphemeral::with(),
      system: 'You are a code review assistant. Be concise.',
  );

  foreach ($response->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, PHP_EOL;
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    # Automatic prompt caching: each request caches the conversation so far,
    # and the next request reads the unchanged prefix from cache.
    cache_control: { type: "ephemeral" },
    system: "You are a code review assistant. Be concise.",
    messages: [
      { role: "user", content: "Review process() in utils.py for performance issues." },
      { role: "assistant", content: "The list comprehension is fine for small inputs. For large inputs, consider a generator to avoid materializing the full list." },
      { role: "user", content: "Now review the calling code that invokes process()." },
      # The reviewer realizes mid-session that all suggestions must also pass
      # the team's strict typing policy. Appending the instruction here keeps
      # earlier turns byte-identical, so the prefix cached by the previous
      # request is still read from cache.
      { role: "system", content: "From now on, every suggestion must include explicit type annotations." }
    ]
  )

  response.content.each do |block|
    puts block.text if block.type == :text
  end

json
[
  { "role": "user", "content": "Run the test suite and fix any failures." },
  {
    "role": "assistant",
    "content": [{ "type": "tool_use", "id": "toolu_01", "name": "run_tests", "input": {} }]
  },
  {
    "role": "user",
    "content": [
      { "type": "tool_result", "tool_use_id": "toolu_01", "content": "12 passed, 0 failed" }
    ]
  },
  {
    "role": "system",
    "content": "The user sent the following message while you were working: also update the changelog before you finish."
  }
]

json
{
  "role": "system",
  "clear_at": "next_user_message",
  "content": "First privately list what you need next; then request every item that doesn't depend on another's result in this one response."
}

json
{
  "model": "claude-fable-5-1",
  "max_tokens": 16000,
  "messages": [
    { "role": "user", "content": "Fix the failing test." },
    {
      "role": "assistant",
      "content": [
        { "type": "thinking", "thinking": "", "signature": "..." },
        {
          "type": "tool_use",
          "id": "toolu_01",
          "name": "read_file",
          "input": { "path": "test_auth.py" }
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
      "content": "Request independent reads in one turn."
    },
    {
      "role": "assistant",
      "content": [
        { "type": "thinking", "thinking": "", "signature": "..." },
        {
          "type": "tool_use",
          "id": "toolu_02",
          "name": "read_file",
          "input": { "path": "auth.py" }
        },
        {
          "type": "tool_use",
          "id": "toolu_03",
          "name": "read_file",
          "input": { "path": "tokens.py" }
        }
      ]
    },
    {
      "role": "user",
      "content": [
        { "type": "tool_result", "tool_use_id": "toolu_02", "content": "..." },
        {
          "type": "tool_result",
          "tool_use_id": "toolu_03",
          "content": "...",
          "cache_control": { "type": "ephemeral" }
        }
      ]
    },
    {
      "role": "system",
      "clear_at": "next_user_message",
      "content": "Request independent reads in one turn."
    },
    {
      "role": "system",
      "clear_at": "next_user_message",
      "content": "The shell exited with status 137."
    }
  ]
}

text wrap
messages.3.clear_at: Extra inputs are not permitted
messages.3.clear_at: clear_at is only permitted on role 'system' messages
messages.3.clear_at: Input should be 'next_user_message' or 'never'
messages.3: a turn-scoped system message supports text blocks only (clear_at: 'next_user_message')
messages.3: output_config is not permitted on a turn-scoped system message (clear_at: 'next_user_message')
messages.3.content.0: cache_control is not permitted on a turn-scoped system message (clear_at: 'next_user_message')

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: mid-conversation-system-clear-at-2026-08-21" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-fable-5-1",
      "max_tokens": 4096,
      "messages": [
        {"role": "user", "content": "Draft a short status update on the database migration for the team channel."},
        {"role": "system", "clear_at": "next_user_message", "content": "The reader is on call: keep this reply under 50 words."}
      ]
    }'

bash CLI
  ant beta:messages create --beta mid-conversation-system-clear-at-2026-08-21 \
    --transform 'content.#(type=="text").text' --raw-output <<'YAML'
  model: claude-fable-5-1
  max_tokens: 4096
  messages:
    - role: user
      content: Draft a short status update on the database migration for the team channel.
    # Turn-scoped reminder: renders for this turn, then clears once a later user message exists.
    - role: system
      clear_at: next_user_message
      content: "The reader is on call: keep this reply under 50 words."
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.beta.messages.create(
      model="claude-fable-5-1",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": "Draft a short status update on the database migration for the team channel.",
          },
          # Turn-scoped reminder: renders for this turn, then clears once a later user message exists.
          {
              "role": "system",
              "clear_at": "next_user_message",
              "content": "The reader is on call: keep this reply under 50 words.",
          },
      ],
      betas=["mid-conversation-system-clear-at-2026-08-21"],
  )

  for block in response.content:
      if block.type == "text":
          print(block.text)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.beta.messages.create({
    model: "claude-fable-5-1",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Draft a short status update on the database migration for the team channel."
      },
      // Turn-scoped reminder: renders for this turn, then clears once a later user message exists.
      {
        role: "system",
        clear_at: "next_user_message",
        content: "The reader is on call: keep this reply under 50 words."
      }
    ],
    betas: ["mid-conversation-system-clear-at-2026-08-21"]
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
      Messages =
      [
          new() { Role = Role.User, Content = "Draft a short status update on the database migration for the team channel." },
          // Turn-scoped reminder: renders for this turn, then clears once a later user message exists.
          new()
          {
              Role = Role.System,
              ClearAt = ClearAt.NextUserMessage,
              Content = "The reader is on call: keep this reply under 50 words.",
          },
      ],
      Betas = [AnthropicBeta.MidConversationSystemClearAt2026_08_21],
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
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Draft a short status update on the database migration for the team channel.")),
  		// Turn-scoped reminder: renders for this turn, then clears once a later user message exists.
  		{
  			Role:    anthropic.BetaMessageParamRoleSystem,
  			ClearAt: anthropic.BetaMessageParamClearAtNextUserMessage,
  			Content: []anthropic.BetaContentBlockParamUnion{anthropic.NewBetaTextBlock("The reader is on call: keep this reply under 50 words.")},
  		},
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaMidConversationSystemClearAt2026_08_21},
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
  import com.anthropic.models.beta.messages.MessageCreateParams;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model("claude-fable-5-1")
          .maxTokens(4096L)
          .addBeta(AnthropicBeta.MID_CONVERSATION_SYSTEM_CLEAR_AT_2026_08_21)
          .addUserMessage("Draft a short status update on the database migration for the team channel.")
          // Turn-scoped reminder: renders for this turn, then clears once a later user message exists.
          .addMessage(BetaMessageParam.builder()
              .role(BetaMessageParam.Role.SYSTEM)
              .clearAt(BetaMessageParam.ClearAt.NEXT_USER_MESSAGE)
              .content("The reader is on call: keep this reply under 50 words.")
              .build())
          .build();

      BetaMessage response = client.beta().messages().create(params);
      response.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  use Anthropic\Beta\AnthropicBeta;
  use Anthropic\Beta\Messages\BetaMessageParam;
  use Anthropic\Client;

  $client = new Client();

  $response = $client->beta->messages->create(
      model: 'claude-fable-5-1',
      maxTokens: 4096,
      messages: [
          BetaMessageParam::with(role: 'user', content: 'Draft a short status update on the database migration for the team channel.'),
          // Turn-scoped reminder: renders for this turn, then clears once a later user message exists.
          BetaMessageParam::with(
              role: 'system',
              clearAt: 'next_user_message',
              content: 'The reader is on call: keep this reply under 50 words.',
          ),
      ],
      betas: [AnthropicBeta::MID_CONVERSATION_SYSTEM_CLEAR_AT_2026_08_21],
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
    messages: [
      {role: "user", content: "Draft a short status update on the database migration for the team channel."},
      # Turn-scoped reminder: renders for this turn, then clears once a later user message exists.
      {role: "system", clear_at: :next_user_message, content: "The reader is on call: keep this reply under 50 words."}
    ],
    betas: [Anthropic::AnthropicBeta::MID_CONVERSATION_SYSTEM_CLEAR_AT_2026_08_21]
  )

  response.content.each do |block|
    puts block.text if block.type == :text
  end
  ```
</CodeGroup>


## Combining with prompt caching

Source: https://platform.claude.com/llms-full.txt#combining-with-prompt-caching

Mid-conversation system messages and [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) are designed to be used together:

* **Enable caching explicitly.** Caching only happens when the request includes `cache_control`, either the top-level [automatic caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#automatic-caching) field or an [explicit breakpoint](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#explicit-cache-breakpoints) on a content block. A mid-conversation system message does not create a cache entry on its own, and without caching enabled there are no savings to preserve.
* **Cache the stable prefix as usual.** Place `cache_control` on the last block that stays the same across requests, whether that is the end of the top-level `system` field, the end of your tool definitions, or a stable point in the message history.
* **Append the system message after the breakpoint.** Because it comes after the cached prefix, it does not change the prefix hash and the cache still hits.
* **A mid-conversation system message is itself cacheable.** Once it is in the conversation, it becomes part of the stable history. On the next turn you can move your cache breakpoint past it (or rely on [automatic caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#automatic-caching) to do so) and the system message is read from cache like any other turn.

Avoid editing or removing a mid-conversation system message that has already been sent. Like any other change to earlier messages, that invalidates the cache from that point forward. On Claude Fable 5.1 it also invalidates the [thinking blocks](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-in-conversation) in every later assistant turn. For guidance that should apply to one turn only, use a [turn-scoped system message](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#turn-scoped-system-messages) and leave it in place. If the instruction needs to evolve, append a new system message rather than rewriting the old one. Consecutive system messages are accepted and treated as a single system section, which follows the same placement rule as a whole.


## Limitations

Source: https://platform.claude.com/llms-full.txt#limitations-6

* **Not for the first message.** A `system` message that carries content cannot be the first entry in `messages`. Use the top-level `system` field for instructions that apply from the very start.
* **Placement is constrained.** A `system` message that carries content (`text`, `tool_addition`, or `tool_removal` blocks) must immediately follow a `user` turn (including a `user` turn that carries `tool_result` blocks) or an `assistant` turn ending in a server tool result, and must precede an `assistant` turn or end the array. It cannot sit between a `tool_use` block and its `tool_result`. Placing it elsewhere returns a 400 error. One exception: `tool_addition` and `tool_removal` blocks are not accepted immediately after a [paused](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#pause-turn) `assistant` turn (one ending in a server tool result), though `text` blocks are; resume the paused turn first, then send the tool change in the next `system` message. A message with empty `content` that only sets [`output_config.effort`](https://platform.claude.com/docs/en/build-with-claude/effort#change-effort-mid-conversation-beta) renders nothing at its position and is accepted anywhere in `messages`, including first or between an `assistant` turn and a `user` turn. Consecutive `system` messages are judged together, so adding a text-carrying message next to an effort-only one makes the whole group follow the content rule.
* **Turn-scoped messages are text-only and re-sent verbatim.** A `clear_at: "next_user_message"` message carries no `tool_addition`, `tool_removal`, `output_config`, or `cache_control`, and once cleared it must stay in `messages` byte-for-byte on later requests. See [Turn-scoped system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#turn-scoped-system-messages).
* **Not a place for untrusted content.** Claude treats system content as operator instructions and follows it. Do not place text from outside the conversation, such as raw tool output, retrieved documents, or web content, directly in a system message; doing so gives that text operator-level authority. Keep that data in `tool_result` blocks and continue to follow [Mitigate jailbreaks and prompt injections](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks).


## Related

Source: https://platform.claude.com/llms-full.txt#related-2

<CardGroup cols={2}>
  <Card title="Prompt caching" icon="bolt" href="https://platform.claude.com/docs/en/build-with-claude/prompt-caching">
    How caching works, where to place breakpoints, and how to read cache usage fields.
  </Card>

  <Card title="Cache diagnostics" icon="magnifying-glass" href="https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics">
    Find out exactly where two requests diverged when a cache hit you expected does not happen.
  </Card>

  <Card title="Using the Messages API" icon="message" href="https://platform.claude.com/docs/en/build-with-claude/working-with-messages">
    Message structure, multi-turn conversations, and the `system` field.
  </Card>

  <Card title="Prompting best practices" icon="text" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices">
    Writing effective prompts and system instructions.
  </Card>

  <Card title="Tool use with Claude" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview">
    How `tool_use` and `tool_result` blocks are structured in the `messages` array.
  </Card>
</CardGroup>


---
title: Prompt caching
url: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
description: Cache prompt prefixes with `cache_control` to cut costs and latency, using automatic caching or explicit breakpoints with 5-minute or 1-hour TTLs.
---

Prompt caching optimizes your API usage by allowing resuming from specific prefixes in your prompts. This significantly reduces processing time and costs for repetitive tasks or prompts with consistent elements.

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>

There are two ways to enable prompt caching:

* **[Automatic caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#automatic-caching)**: Add a single `cache_control` field at the top level of your request. The system automatically applies the cache breakpoint to the last cacheable block and moves it forward as conversations grow. Best for multi-turn conversations where the growing message history should be cached automatically.
* **[Explicit cache breakpoints](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#explicit-cache-breakpoints)**: Place `cache_control` directly on individual content blocks for fine-grained control over exactly what gets cached.

The simplest way to start is with automatic caching:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "cache_control": {"type": "ephemeral"},
      "system": "You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style.",
      "messages": [
        {
          "role": "user",
          "content": "Analyze the major themes in Pride and Prejudice."
        }
      ]
    }'

bash CLI
  ant messages create --transform usage <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  cache_control:
    type: ephemeral
  system: >-
    You are an AI assistant tasked with analyzing literary works. Your goal is
    to provide insightful commentary on themes, characters, and writing style.
  messages:
    - role: user
      content: Analyze the major themes in Pride and Prejudice.
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      cache_control={"type": "ephemeral"},
      system="You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style.",
      messages=[
          {
              "role": "user",
              "content": "Analyze the major themes in 'Pride and Prejudice'.",
          }
      ],
  )
  print(response.usage.model_dump_json())

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    cache_control: { type: "ephemeral" },
    system:
      "You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style.",
    messages: [
      {
        role: "user",
        content: "Analyze the major themes in 'Pride and Prejudice'."
      }
    ]
  });
  console.log(response.usage);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      CacheControl = new CacheControlEphemeral(),
      System = "You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style.",
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = "Analyze the major themes in 'Pride and Prejudice'."
          }
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message.Usage);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:        anthropic.ModelClaudeOpus5,
  	MaxTokens:    1024,
  	CacheControl: anthropic.NewCacheControlEphemeralParam(),
  	System: []anthropic.TextBlockParam{
  		{Text: "You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style."},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Analyze the major themes in 'Pride and Prejudice'.")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.Usage.RawJSON())

java Java
  import com.anthropic.models.messages.CacheControlEphemeral;
  // ...
  public class PromptCachingExample {

    public static void main(String[] args) {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .cacheControl(CacheControlEphemeral.builder().build())
          .system("You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style.")
          .addUserMessage("Analyze the major themes in 'Pride and Prejudice'.")
          .build();

      Message message = client.messages().create(params);
      System.out.println(message.usage());
    }
  }

php PHP
  use Anthropic\Messages\CacheControlEphemeral;
  // ...
  $client = new Client();

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => "Analyze the major themes in 'Pride and Prejudice'."]
      ],
      model: 'claude-opus-5',
      cacheControl: CacheControlEphemeral::with(),
      system: "You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style.",
  );
  echo json_encode($response->usage);

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    cache_control: {type: "ephemeral"},
    system: "You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style.",
    messages: [
      {
        role: "user",
        content: "Analyze the major themes in 'Pride and Prejudice'."
      }
    ]
  )
  puts response.usage
  ```
</CodeGroup>

With automatic caching, the system caches all content up to and including the last cacheable block. On subsequent requests with the same prefix, cached content is reused automatically.

***


## How prompt caching works

Source: https://platform.claude.com/llms-full.txt#how-prompt-caching-works

When you send a request with prompt caching enabled:

1. The system checks if a prompt prefix, up to a specified cache breakpoint, is already cached from a recent query.
2. If found, it uses the cached version, reducing processing time and costs.
3. Otherwise, it processes the full prompt and caches the prefix once the response begins.

This is especially useful for:

* Prompts with many examples
* Large amounts of context or background information
* Repetitive tasks with consistent instructions
* Long multi-turn conversations

By default, the cache has a 5-minute lifetime. The cache is refreshed for no additional cost each time the cached content is used.

The lifetime is measured from the start of the request that writes or reads the cache entry, not from the end of its response. Time spent generating a response counts against the lifetime: if a response takes 4 minutes to stream, a follow-up request that reuses the same cached prefix must start within about 1 minute of that response completing.

<Note>
  If you find that 5 minutes is too short, Anthropic also offers a 1-hour cache duration [at additional cost](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing).

  For more information, see [1-hour cache duration](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#1-hour-cache-duration).
</Note>

<Tip>
  **Prompt caching caches the full prefix**

  Prompt caching references the entire prompt - `tools`, `system`, and `messages` (in that order) up to and including the block designated with `cache_control`.
</Tip>

***


## Pricing

Source: https://platform.claude.com/llms-full.txt#pricing-8

Prompt caching introduces a new pricing structure. The following table shows the price per million tokens for each supported model:

| Model                                                                                                                                 | Base input tokens | 5m cache writes | 1h cache writes | Cache hits and refreshes | Output tokens |
| ------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | --------------- | --------------- | ------------------------ | ------------- |
| Claude Fable 5.1                                                                                                                      | $10 / MTok        | $12.50 / MTok   | $20 / MTok      | $0.25 / MTok1            | $50 / MTok    |
| Claude Mythos 5.1 ([limited availability](https://anthropic.com/glasswing))                                                           | $10 / MTok        | $12.50 / MTok   | $20 / MTok      | $0.25 / MTok1            | $50 / MTok    |
| Claude Fable 5                                                                                                                        | $10 / MTok        | $12.50 / MTok   | $20 / MTok      | $1 / MTok                | $50 / MTok    |
| Claude Mythos 5 ([limited availability](https://anthropic.com/glasswing))                                                             | $10 / MTok        | $12.50 / MTok   | $20 / MTok      | $1 / MTok                | $50 / MTok    |
| Claude Opus 5                                                                                                                         | $5 / MTok         | $6.25 / MTok    | $10 / MTok      | $0.50 / MTok             | $25 / MTok    |
| Claude Opus 4.8                                                                                                                       | $5 / MTok         | $6.25 / MTok    | $10 / MTok      | $0.50 / MTok             | $25 / MTok    |
| Claude Opus 4.7                                                                                                                       | $5 / MTok         | $6.25 / MTok    | $10 / MTok      | $0.50 / MTok             | $25 / MTok    |
| Claude Opus 4.6                                                                                                                       | $5 / MTok         | $6.25 / MTok    | $10 / MTok      | $0.50 / MTok             | $25 / MTok    |
| Claude Opus 4.5                                                                                                                       | $5 / MTok         | $6.25 / MTok    | $10 / MTok      | $0.50 / MTok             | $25 / MTok    |
| Claude Opus 4.1 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations))  | $15 / MTok        | $18.75 / MTok   | $30 / MTok      | $1.50 / MTok             | $75 / MTok    |
| Claude Opus 4 ([retired, except on Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations))                | $15 / MTok        | $18.75 / MTok   | $30 / MTok      | $1.50 / MTok             | $75 / MTok    |
| Claude Sonnet 5                                                                                                                       | $2 / MTok         | $2.50 / MTok    | $4 / MTok       | $0.20 / MTok             | $10 / MTok    |
| Claude Sonnet 4.6                                                                                                                     | $3 / MTok         | $3.75 / MTok    | $6 / MTok       | $0.30 / MTok             | $15 / MTok    |
| Claude Sonnet 4.5                                                                                                                     | $3 / MTok         | $3.75 / MTok    | $6 / MTok       | $0.30 / MTok             | $15 / MTok    |
| Claude Sonnet 4 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations))  | $3 / MTok         | $3.75 / MTok    | $6 / MTok       | $0.30 / MTok             | $15 / MTok    |
| Claude Haiku 4.5                                                                                                                      | $1 / MTok         | $1.25 / MTok    | $2 / MTok       | $0.10 / MTok             | $5 / MTok     |
| Claude Haiku 3.5 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)) | $0.80 / MTok      | $1 / MTok       | $1.60 / MTok    | $0.08 / MTok             | $4 / MTok     |

*1 Cache hits and refreshes on Claude Fable 5.1 and Claude Mythos 5.1 are priced at 0.025x the base input price. All other models use the standard 0.1x multiplier.*

<Note>
  The previous table reflects the following pricing multipliers for prompt caching:

  * 5-minute cache write tokens are 1.25 times the base input tokens price
  * 1-hour cache write tokens are 2 times the base input tokens price
  * Cache read tokens are 0.1 times the base input tokens price (see the table footnote for per-model exceptions)

  These multipliers stack with other pricing modifiers such as the Batch API discount and data residency. See [pricing](https://platform.claude.com/docs/en/about-claude/pricing) for full details.
</Note>

***


## Supported models

Source: https://platform.claude.com/llms-full.txt#supported-models-4

Prompt caching (both automatic and explicit) is supported on all [active Claude models](https://platform.claude.com/docs/en/models/overview).

***


## Automatic caching

Source: https://platform.claude.com/llms-full.txt#automatic-caching

Automatic caching is the simplest way to enable prompt caching. Instead of placing `cache_control` on individual content blocks, add a single `cache_control` field at the top level of your request body. The system automatically applies the cache breakpoint to the last cacheable block.

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "cache_control": {"type": "ephemeral"},
      "system": "You are a helpful assistant that remembers our conversation.",
      "messages": [
        {"role": "user", "content": "My name is Alex. I work on machine learning."},
        {"role": "assistant", "content": "Nice to meet you, Alex! How can I help with your ML work today?"},
        {"role": "user", "content": "What did I say I work on?"}
      ]
    }'

bash CLI
  ant messages create --transform usage <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  cache_control:
    type: ephemeral
  system: You are a helpful assistant that remembers our conversation.
  messages:
    - role: user
      content: My name is Alex. I work on machine learning.
    - role: assistant
      content: Nice to meet you, Alex! How can I help with your ML work today?
    - role: user
      content: What did I say I work on?
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      cache_control={"type": "ephemeral"},
      system="You are a helpful assistant that remembers our conversation.",
      messages=[
          {"role": "user", "content": "My name is Alex. I work on machine learning."},
          {
              "role": "assistant",
              "content": "Nice to meet you, Alex! How can I help with your ML work today?",
          },
          {"role": "user", "content": "What did I say I work on?"},
      ],
  )
  print(response.usage.model_dump_json())

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    cache_control: { type: "ephemeral" },
    system: "You are a helpful assistant that remembers our conversation.",
    messages: [
      { role: "user", content: "My name is Alex. I work on machine learning." },
      {
        role: "assistant",
        content: "Nice to meet you, Alex! How can I help with your ML work today?"
      },
      { role: "user", content: "What did I say I work on?" }
    ]
  });
  console.log(response.usage);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      CacheControl = new CacheControlEphemeral(),
      System = "You are a helpful assistant that remembers our conversation.",
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = "My name is Alex. I work on machine learning."
          },
          new()
          {
              Role = Role.Assistant,
              Content = "Nice to meet you, Alex! How can I help with your ML work today?"
          },
          new()
          {
              Role = Role.User,
              Content = "What did I say I work on?"
          }
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message.Usage);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:        anthropic.ModelClaudeOpus5,
  	MaxTokens:    1024,
  	CacheControl: anthropic.NewCacheControlEphemeralParam(),
  	System: []anthropic.TextBlockParam{
  		{Text: "You are a helpful assistant that remembers our conversation."},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("My name is Alex. I work on machine learning.")),
  		anthropic.NewAssistantMessage(anthropic.NewTextBlock("Nice to meet you, Alex! How can I help with your ML work today?")),
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What did I say I work on?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.Usage.RawJSON())

java Java
  import com.anthropic.models.messages.CacheControlEphemeral;
  // ...
  public class AutomaticCachingExample {

      public static void main(String[] args) {
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          MessageCreateParams params = MessageCreateParams.builder()
                  .model(Model.CLAUDE_OPUS_5)
                  .maxTokens(1024)
                  .cacheControl(CacheControlEphemeral.builder().build())
                  .system("You are a helpful assistant that remembers our conversation.")
                  .addUserMessage("My name is Alex. I work on machine learning.")
                  .addAssistantMessage("Nice to meet you, Alex! How can I help with your ML work today?")
                  .addUserMessage("What did I say I work on?")
                  .build();

          Message message = client.messages().create(params);
          System.out.println(message.usage());
      }
  }

php PHP
  use Anthropic\Messages\CacheControlEphemeral;
  // ...
  $client = new Client();

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [
          ['role' => 'user', 'content' => 'My name is Alex. I work on machine learning.'],
          ['role' => 'assistant', 'content' => 'Nice to meet you, Alex! How can I help with your ML work today?'],
          ['role' => 'user', 'content' => 'What did I say I work on?'],
      ],
      model: 'claude-opus-5',
      cacheControl: CacheControlEphemeral::with(),
      system: 'You are a helpful assistant that remembers our conversation.',
  );
  echo json_encode($response->usage);

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    cache_control: {type: "ephemeral"},
    system: "You are a helpful assistant that remembers our conversation.",
    messages: [
      {role: "user", content: "My name is Alex. I work on machine learning."},
      {role: "assistant", content: "Nice to meet you, Alex! How can I help with your ML work today?"},
      {role: "user", content: "What did I say I work on?"}
    ]
  )
  puts response.usage

json
{ "cache_control": { "type": "ephemeral", "ttl": "1h" } }

json
{
  "model": "claude-opus-5",
  "max_tokens": 1024,
  "cache_control": { "type": "ephemeral" },
  "system": [
    {
      "type": "text",
      "text": "You are a helpful assistant.",
      "cache_control": { "type": "ephemeral" }
    }
  ],
  "messages": [{ "role": "user", "content": "What are the key terms?" }]
}
```

### What stays the same

Automatic caching uses the same underlying caching infrastructure. Pricing, minimum token thresholds, context ordering requirements, and the 20-block lookback window all apply the same as with explicit breakpoints.

### Edge cases

* If the last block already has an explicit `cache_control` with the same TTL, automatic caching is a no-op.
* If the last block has an explicit `cache_control` with a different TTL, the API returns a 400 error.
* If 4 explicit block-level breakpoints already exist, the API returns a 400 error (no slots left for automatic caching).
* If the last block is not eligible as an automatic cache breakpoint target, the system silently walks backwards to find the nearest eligible block. If none is found, caching is skipped.

<Note>
  Automatic caching is available on every platform except the legacy [Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy) integration. On that integration, the API returns a 400 error for a top-level `cache_control` field, so use [explicit cache breakpoints](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#explicit-cache-breakpoints) instead.
</Note>

***


## Explicit cache breakpoints

Source: https://platform.claude.com/llms-full.txt#explicit-cache-breakpoints

For more control over caching, you can place `cache_control` directly on individual content blocks. This is useful when you need to cache different sections that change at different frequencies, or need fine-grained control over exactly what gets cached.

### Structuring your prompt

Place static content (tool definitions, system instructions, context, examples) at the beginning of your prompt. Mark the end of the reusable content for caching using the `cache_control` parameter.

Cache prefixes are created in the following order: `tools`, `system`, then `messages`. This order forms a hierarchy where each level builds upon the previous ones.

#### How automatic prefix checking works

You can use just one cache breakpoint at the end of your static content, and the system will automatically find the longest prefix that a prior request already wrote to the cache. Understanding how this works helps you optimize your caching strategy.

**Three core principles:**

1. **Cache writes happen only at your breakpoint.** Marking a block with `cache_control` writes exactly one cache entry: a hash of the prefix ending at that block. The system does not write entries for any earlier position. Because the hash is cumulative, covering everything up to and including the breakpoint, changing any block at or before the breakpoint produces a different hash on the next request.

2. **Cache reads look backward for entries that prior requests wrote.** On each request the system computes the prefix hash at your breakpoint and checks for a matching cache entry. If none exists, it walks backward one block at a time, checking whether the prefix hash at each earlier position matches something already in the cache. It is looking for prior writes, not for stable content.

3. **The lookback window is 20 blocks.** The system checks at most 20 positions per breakpoint, counting the breakpoint itself as the first. If the system finds no matching entry in that window, checking stops (or resumes from the next explicit breakpoint, if any). On the Claude API, a run of consecutive `tool_use` blocks counts as one position, and so does a run of consecutive `tool_result` blocks, so a turn with many parallel tool calls doesn't push the previous request's entry out of the window on its own.

**Example: Lookback in a growing conversation**

You append new blocks each turn and set `cache_control` on the final block of each request:

* **Turn 1:** 10 blocks, breakpoint on block 10. No prior cache entries exist. The system writes an entry at block 10.
* **Turn 2:** 15 blocks, breakpoint on block 15. Block 15 has no entry, so the system walks back to block 10 and finds the turn-1 entry. Cache hit at block 10; the system processes only blocks 11 through 15 fresh and writes a new entry at block 15.
* **Turn 3:** 35 blocks, breakpoint on block 35. The system checks 20 positions (blocks 35 through 16) and finds nothing. The turn-2 entry at block 15 is one position outside the window, so there is no cache hit. Adding a second breakpoint at block 15 starts a second lookback window there, which finds the turn-2 entry.

**Common mistake: Breakpoint on content that changes every request**

Your prompt has a large static system context (blocks 1 through 5) followed by a per-request block containing a timestamp and the user message (block 6). You set `cache_control` on block 6:

* **Request 1:** Cache write at block 6. The hash includes the timestamp.
* **Request 2:** The timestamp differs, so the prefix hash at block 6 differs. The lookback walks through blocks 5, 4, 3, 2, and 1, but the system never wrote an entry at any of those positions. No cache hit. You pay for a fresh cache write on every request and never get a read.

The lookback does not find stable content behind your breakpoint and cache it. It finds entries that prior requests already wrote, and writes happen only at breakpoints. Move `cache_control` to block 5, the last block that stays the same across requests, and every subsequent request reads the cached prefix. [Automatic caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#automatic-caching) hits the same trap: it places the breakpoint on the last cacheable block, which in this structure is the one that changes every request, so use an explicit breakpoint on block 5 instead.

**Key takeaway:** Place `cache_control` on the last block whose prefix is identical across the requests you want to share a cache. In a growing conversation the final block works as long as each turn adds fewer than 20 blocks: earlier content never changes, so the next request's lookback finds the prior write. For a prompt with a varying suffix (timestamps, per-request context, the incoming message), place the breakpoint at the end of the static prefix, not on the varying block.

#### When to use multiple breakpoints

You can define up to 4 cache breakpoints if you want to:

* Cache different sections that change at different frequencies (for example, tools rarely change, but context updates daily)
* Have more control over exactly what gets cached
* Ensure a cache hit when a growing conversation pushes your breakpoint 20 or more blocks past the last cache write

<Note>
  **Important limitation:** The lookback can only find entries that earlier requests already wrote. If a growing conversation pushes your breakpoint 20 or more blocks past the last write, the lookback window misses it. Add a second breakpoint closer to that position from the start so a write accumulates there before you need it.
</Note>

### Understanding cache breakpoint costs

**Cache breakpoints themselves don't add any cost.** You are only charged for:

* **Cache writes:** When new content is written to the cache (25% more than base input tokens for 5-minute TTL)
* **Cache reads:** When cached content is used (10% of base input token price, or 2.5% on Claude Fable 5.1 and Claude Mythos 5.1)
* **Regular input tokens:** For any uncached content

Adding more `cache_control` breakpoints doesn't increase your costs - you still pay the same amount based on what content is actually cached and read. The breakpoints give you control over what sections can be cached independently.

***


## Caching strategies and considerations

Source: https://platform.claude.com/llms-full.txt#caching-strategies-and-considerations

### Cache limitations

On the Claude API, [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), and [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), the minimum cacheable prompt length is:

* 512 tokens for Claude Fable 5.1, Claude Mythos 5.1, Claude Opus 5, Claude Fable 5, and [Claude Mythos 5](https://anthropic.com/glasswing)
* 2,048 tokens for [Claude Mythos Preview](https://anthropic.com/glasswing) and Claude Opus 4.7
* 4,096 tokens for Claude Opus 4.6 and Claude Opus 4.5
* 1,024 tokens for Claude Opus 4.8, Claude Sonnet 5, Claude Sonnet 4.6, Claude Sonnet 4.5, Claude Opus 4.1 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)), Claude Opus 4 ([retired, except on Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)), and Claude Sonnet 4 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations))
* 4,096 tokens for Claude Haiku 4.5
* 2,048 tokens for Claude Haiku 3.5 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations))

These minimums apply on every platform where each model is available.

Shorter prompts cannot be cached, even if marked with `cache_control`. Any requests to cache fewer than this number of tokens will be processed without caching, and no error is returned. To verify whether a prompt was cached, check the [response usage fields](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#tracking-cache-performance): if both `cache_creation_input_tokens` and `cache_read_input_tokens` are 0, the prompt was not cached (likely because it did not meet the minimum length requirement).

If your prompt falls just short of the minimum for your model and platform, expanding the cached content to reach the threshold is often worthwhile. Cache reads cost significantly less than uncached input tokens, so reaching the minimum can reduce costs for frequently reused prompts.

<Note>
  [Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) is an AWS-operated platform. On Bedrock, see the [Bedrock prompt caching documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) for the per-model minimums, failure behavior, and usage-field names that apply.
</Note>

For concurrent requests, note that a cache entry only becomes available after the first response begins. If you need cache hits for parallel requests, wait for the first response before sending subsequent requests.

Currently, "ephemeral" is the only supported cache type, which by default has a 5-minute lifetime.

### What can be cached

Most blocks in the request can be cached. This includes:

* Tools: Tool definitions in the `tools` array
* System messages: Content blocks in the `system` array
* Text messages: Content blocks in the `messages.content` array, for both user and assistant turns
* Images & Documents: Content blocks in the `messages.content` array, in user turns
* Tool use and tool results: Content blocks in the `messages.content` array, in both user and assistant turns

Each of these elements can be cached, either automatically or by marking them with `cache_control`.

### What cannot be cached

While most request blocks can be cached, there are some exceptions:

* Thinking blocks cannot be cached directly with `cache_control`. However, thinking blocks CAN be cached alongside other content when they appear in previous assistant turns. When cached this way, they DO count as input tokens when read from cache.

* Sub-content blocks (like [citations](https://platform.claude.com/docs/en/build-with-claude/citations)) themselves cannot be cached directly. Instead, cache the top-level block.

  In the case of citations, the top-level document content blocks that serve as the source material for citations can be cached. This allows you to use prompt caching with citations effectively by caching the documents that citations will reference.

* Empty text blocks cannot be cached.

### What invalidates the cache

Modifications to cached content can invalidate some or all of the cache.

As described in [Structuring your prompt](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#structuring-your-prompt), the cache follows the hierarchy: `tools` → `system` → `messages`. Changes at each level invalidate that level and all subsequent levels.

The following table shows which parts of the cache are invalidated by different types of changes. ✘ indicates that the cache is invalidated, while ✓ indicates that the cache remains valid.

| What changes                                              | Tools cache    | System cache   | Messages cache | Impact                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| --------------------------------------------------------- | -------------- | -------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tool definitions**                                      | ✘              | ✘              | ✘              | Modifying tool definitions (names, descriptions, parameters) invalidates the entire cache                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Web search toggle**                                     | ✓              | ✘              | ✘              | Enabling/disabling web search modifies the system prompt                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **Citations toggle**                                      | ✓              | ✘              | ✘              | Enabling/disabling citations modifies the system prompt                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **Speed setting**                                         | ✓              | ✘              | ✘              | Switching between [`speed: "fast"` and standard speed](https://platform.claude.com/docs/en/build-with-claude/fast-mode) invalidates system and message caches                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **Tool choice**                                           | ✓              | ✓              | ✘              | Changes to `tool_choice` parameter only affect message blocks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **Images**                                                | ✓              | ✓              | ✘              | Adding/removing images anywhere in the prompt affects message blocks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Thinking parameters**                                   | Model-specific | Model-specific | ✘              | The thinking configuration (mode, and `budget_tokens` in extended mode) is rendered into the prompt, so changing it always invalidates message blocks; tool and system caches are also invalidated on models that render the configuration ahead of them. See [Thinking and prompt caching](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-prompt-caching).                                                                                                                                                                                                           |
| **Effort setting**                                        | Model-specific | Model-specific | ✘              | Changing the [`output_config.effort`](https://platform.claude.com/docs/en/build-with-claude/effort) value always invalidates message blocks, with the same model-specific effect on tool and system caches as thinking parameters. Setting effort explicitly to the model's default is equivalent to omitting it and does not invalidate. On models that support [per-message effort](https://platform.claude.com/docs/en/build-with-claude/effort#change-effort-mid-conversation-beta), an effort change carried in a `role: "system"` message inside `messages` leaves the cached prefix intact. |
| **Non-tool results passed to extended thinking requests** | ✓              | ✓              | Model-specific | On Opus 4.5+ and Sonnet 4.6+, thinking blocks are preserved by default, so the cache remains valid (✓). On earlier Opus/Sonnet models and all Haiku models, all previously-cached thinking blocks are stripped from context, and any messages that follow those thinking blocks are removed from the cache (✘). For more details, see [Caching with thinking blocks](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#caching-with-thinking-blocks).                                                                                                                           |
| **Dropped thinking blocks**                               | ✓              | ✓              | ✘              | When the API drops a Claude Fable 5.1 or Claude Mythos 5.1 thinking block that isn't [preserved](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-thinking) on that request (for example, one you replay to an earlier model), the cached prefix changes from that block's position onward on that request. Blocks the receiving model can read, passed back unchanged, keep the cache intact.                                                                                                                                                                             |

<Note>
  On Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, [Claude Mythos 5](https://anthropic.com/glasswing), Claude Opus 4.8, and Claude Opus 5, you can add a new system instruction partway through a conversation without invalidating the system or message caches. Append a `{"role": "system"}` message to `messages` instead of editing the top-level `system` field, so the cached prefix stays unchanged. This feature is not available on Claude Sonnet 5. Use the top-level `system` field instead. See [Mid-conversation system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages).
</Note>

### Tracking cache performance

Monitor cache performance using these API response fields, within `usage` in the response (or `message_start` event if [streaming](https://platform.claude.com/docs/en/build-with-claude/streaming)):

* `cache_creation_input_tokens`: Number of tokens written to the cache when creating a new entry.
* `cache_read_input_tokens`: Number of tokens retrieved from the cache for this request.
* `input_tokens`: Number of input tokens which were not read from or used to create a cache (that is, tokens after the last cache breakpoint).

<Note>
  **Understanding the token breakdown**

  The `input_tokens` field represents only the tokens that come **after the last cache breakpoint** in your request - not all the input tokens you sent.

  To calculate total input tokens:

  ```text wrap
  total_input_tokens = cache_read_input_tokens + cache_creation_input_tokens + input_tokens

text wrap
Request 1: User: "What's the weather in Paris?"
Response: [thinking_block_1] + [tool_use block 1]

Request 2:
User: ["What's the weather in Paris?"],
Assistant: [thinking_block_1] + [tool_use block 1],
User: [tool_result_1, cache=True]
Response: [thinking_block_2] + [text block 2]
# Request 2 caches its request content (not the response)
# The cache includes: user message, thinking_block_1, tool_use block 1, and tool_result_1

Request 3:
User: ["What's the weather in Paris?"],
Assistant: [thinking_block_1] + [tool_use block 1],
User: [tool_result_1, cache=True],
Assistant: [thinking_block_2] + [text block 2],
User: [Text response, cache=True]
# On earlier Opus/Sonnet and all Haiku models, non-tool-result user block causes prior thinking blocks to be stripped; on Opus 4.5+/Sonnet 4.6+ they are kept
```

On earlier Opus/Sonnet models and all Haiku models, all previous thinking blocks are removed from context at this point. On Opus 4.5+ and Sonnet 4.6+, prior thinking blocks are kept by default and remain part of the cached prefix.

For more detailed information, see [Thinking and prompt caching](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-prompt-caching).

### Cache storage and sharing

<Warning>
  Prompt caching uses [workspace](https://platform.claude.com/docs/en/manage-claude/workspaces)-level isolation. Caches are isolated per workspace, ensuring data separation between workspaces within the same organization. This applies to the Claude API, Claude Platform on AWS, and Microsoft Foundry; Bedrock and Google Cloud maintain organization-level cache isolation. If you use multiple workspaces, review your caching strategy to account for this difference.
</Warning>

* **Organization and workspace isolation:** Caches are isolated between organizations. Different organizations never share caches, even if they use identical prompts. Caches are also isolated per workspace within an organization on the Claude API, Claude Platform on AWS, and Microsoft Foundry; Bedrock and Google Cloud use organization-level isolation only.

* **Exact matching:** Cache hits require 100% identical prompt segments, including all text and images up to and including the block marked with cache control.

* **Output token generation:** Prompt caching has no effect on output token generation. The response you receive is identical to what you would get if prompt caching were not used.

### Best practices for effective caching

To optimize prompt caching performance:

* Start with [automatic caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#automatic-caching) for multi-turn conversations. It handles breakpoint management automatically.
* Use [explicit block-level breakpoints](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#explicit-cache-breakpoints) when you need to cache different sections with different change frequencies.
* Cache stable, reusable content like system instructions, background information, large contexts, or frequent tool definitions.
* Place cached content at the prompt's beginning for best performance.
* Use cache breakpoints strategically to separate different cacheable prefix sections.
* Place the breakpoint on the last block that stays identical across requests. For a prompt with a static prefix and a varying suffix (timestamps, per-request context, the incoming message), that is the end of the prefix, not the varying block.
* Regularly analyze cache hit rates and adjust your strategy as needed.

### Optimizing for different use cases

Tailor your prompt caching strategy to your scenario:

* Conversational agents: Reduce cost and latency for extended conversations, especially those with long instructions or uploaded documents.
* Coding assistants: Improve autocomplete and codebase Q\&A by keeping relevant sections or a summarized version of the codebase in the prompt.
* Large document processing: Incorporate complete long-form material including images in your prompt without increasing response latency.
* Detailed instruction sets: Share extensive lists of instructions, procedures, and examples to fine-tune Claude's responses. Developers often include an example or two in the prompt, but with prompt caching you can get even better performance by including 20+ diverse examples of high quality answers.
* Agentic tool use: Enhance performance for scenarios involving multiple tool calls and iterative code changes, where each step typically requires a new API call.
* Talk to books, papers, documentation, podcast transcripts, and other longform content: Bring any knowledge base alive by embedding the entire document(s) into the prompt, and letting users ask it questions.

### Troubleshooting common issues

If experiencing unexpected behavior:

<Tip>
  [Cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics) (beta) has the API compare consecutive requests and report exactly where the prompt prefix diverged, which automatically handles many of the steps in this list.
</Tip>

* Ensure cached sections are identical across calls. For explicit breakpoints, verify that `cache_control` markers are in the same locations
* Check that calls are made within the cache lifetime (5 minutes by default)
* Verify that `tool_choice`, image usage, the thinking configuration, and `output_config.effort` remain consistent between calls
* Validate that you are caching at least the minimum number of tokens for your model and platform (see [Cache limitations](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#cache-limitations))
* Confirm your breakpoint is on a block that stays identical across requests. Cache writes happen only at the breakpoint, and if that block changes (timestamps, per-request context, the incoming message), the prefix hash never matches. The lookback does not find stable content behind the breakpoint; it only finds entries that earlier requests wrote at their own breakpoints
* Verify that the keys in your `tool_use` content blocks have stable ordering as some languages (for example, Swift, Go) randomize key order during JSON conversion, breaking caches
* Use [cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics) to have the API compare consecutive requests and report which part of the prompt diverged

<Note>
  Changes to `tool_choice` or the presence/absence of images anywhere in the prompt will invalidate the cache, requiring a new cache entry to be created. For more details on cache invalidation, see [What invalidates the cache](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#what-invalidates-the-cache).
</Note>

***


## 1-hour cache duration

Source: https://platform.claude.com/llms-full.txt#1-hour-cache-duration

If you find that 5 minutes is too short, Anthropic also offers a 1-hour cache duration [at additional cost](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing).

<Note>
  The 1-hour cache duration is available on the Claude API, [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy), [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), and [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry).
</Note>

To use the extended cache, include `ttl` in the `cache_control` definition like this:

The response includes detailed cache information like the following:

```json Output
{
  "usage": {
    "input_tokens": 2048,
    "cache_read_input_tokens": 1800,
    "cache_creation_input_tokens": 248,
    "output_tokens": 503,

    "cache_creation": {
      "ephemeral_5m_input_tokens": 148,
      "ephemeral_1h_input_tokens": 100
    }
  }
}
```

Note that the current `cache_creation_input_tokens` field equals the sum of the values in the `cache_creation` object.

If you see `ephemeral_5m_input_tokens` writes you didn't request while using server tools such as web search, see [Tool use with prompt caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching#server-tool-results-are-cached-automatically).

### When to use the 1-hour cache

If you have prompts that are used at a regular cadence (that is, system prompts that are used more frequently than every 5 minutes), continue to use the 5-minute cache, because this will continue to be refreshed at no additional charge.

The 1-hour cache is best used in the following scenarios:

* When you have prompts that are likely used less frequently than 5 minutes, but more frequently than every hour. For example, when an agentic side-agent will take longer than 5 minutes, or when storing a long chat conversation with a user and you generally expect that user may not respond in the next 5 minutes.
* When latency is important and your follow up prompts may be sent beyond 5 minutes.
* When you want to improve your rate limit utilization, because cache hits are not deducted against your rate limit.

<Note>
  The 5-minute and 1-hour cache behave the same with respect to latency. You will generally see improved time-to-first-token for long documents.
</Note>

### Mixing different TTLs

You can use both 1-hour and 5-minute cache controls in the same request, but with an important constraint: Cache entries with longer TTL must appear before shorter TTLs (that is, a 1-hour cache entry must appear before any 5-minute cache entries).

When mixing TTLs, the API determines three billing locations in your prompt:

1. Position `A`: The token count at the highest cache hit (or 0 if no hits).
2. Position `B`: The token count at the highest 1-hour `cache_control` block after `A` (or equals `A` if none exist).
3. Position `C`: The token count at the last `cache_control` block.

<Note>
  If `B` or `C` is larger than `A`, it is necessarily a cache miss, because `A` is the highest cache hit.
</Note>

You'll be charged for:

1. Cache read tokens for `A`.
2. 1-hour cache write tokens for `(B - A)`.
3. 5-minute cache write tokens for `(C - B)`.

Here are three examples. This depicts the input tokens of 3 requests, each of which has different cache hits and cache misses. Each has a different calculated pricing, shown in the colored boxes, as a result. ![Mixing TTLs Diagram](https://platform.claude.com/docs/images/prompt-cache-mixed-ttl.svg)

***


## Pre-warming the cache

Source: https://platform.claude.com/llms-full.txt#pre-warming-the-cache

Cache pre-warming lets you load your system prompt or tool definitions into the prompt cache before a user triggers a real request. This eliminates the cache-miss latency penalty on the first user interaction, reducing time-to-first-token (TTFT) for latency-sensitive applications.

### How it works

Set `max_tokens: 0` in your request. The API reads your prompt into the model and writes the cache at any `cache_control` breakpoint, then returns immediately without generating any output. The response has an empty `content` array, `stop_reason: "max_tokens"`, and a fully populated `usage` block.

Place the `cache_control` breakpoint on the last block that is shared with the follow-up request (typically your system prompt or tool definitions), not on the placeholder user message. Otherwise the cache entry is keyed to the placeholder and the follow-up request won't hit it. Use the same thinking configuration and `output_config.effort` as your follow-up requests too: those values are rendered into the prompt (see [What invalidates the cache](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#what-invalidates-the-cache)), so a pre-warm with a different configuration can write an entry your real traffic never hits. This means using an [explicit cache breakpoint](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#explicit-cache-breakpoints) rather than [automatic caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#automatic-caching), since automatic caching places the breakpoint on the last block, which here is the placeholder. The placeholder user message can be any string with non-whitespace content (the examples here use `"warmup"`); its content is read into the model but never answered.

<Note>
  A pre-warm request incurs a **cache write** charge if the prefix is not already cached, the same as any other request. Check `usage.cache_creation_input_tokens` in the response to confirm a write occurred. Zero output tokens are billed.
</Note>

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 0,
      "system": [
        {
          "type": "text",
          "text": "You are an expert software engineer with deep knowledge of distributed systems...",
          "cache_control": {"type": "ephemeral"}
        }
      ],
      "messages": [{"role": "user", "content": "warmup"}]
    }'

bash CLI
  ant messages create \
    --transform '{stop_reason,content,usage}' --format yaml <<'YAML'
  model: claude-opus-5
  max_tokens: 0
  system:
    - type: text
      text: >-
        You are an expert software engineer with deep knowledge of
        distributed systems...
      cache_control:
        type: ephemeral
  messages:
    - role: user
      content: warmup
  YAML

python Python
  client = anthropic.Anthropic()

  # Fire this before users arrive to warm the shared system-prompt cache.
  prewarm = client.messages.create(
      model="claude-opus-5",
      max_tokens=0,
      system=[
          {
              "type": "text",
              "text": "You are an expert software engineer with deep knowledge of distributed systems...",
              "cache_control": {"type": "ephemeral"},
          }
      ],
      messages=[{"role": "user", "content": "warmup"}],
  )
  print(prewarm.stop_reason)  # "max_tokens"
  print(prewarm.content)  # []
  print(prewarm.usage)

typescript TypeScript
  const client = new Anthropic();

  // Fire this before users arrive to warm the shared system-prompt cache.
  const prewarm = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 0,
    system: [
      {
        type: "text",
        text: "You are an expert software engineer with deep knowledge of distributed systems...",
        cache_control: { type: "ephemeral" }
      }
    ],
    messages: [{ role: "user", content: "warmup" }]
  });
  console.log(prewarm.stop_reason); // "max_tokens"
  console.log(prewarm.content); // []
  console.log(prewarm.usage);

csharp C#
  AnthropicClient client = new();

  var prewarm = await client.Messages.Create(
      new()
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 0,
          System = new(
              [
                  new TextBlockParam
                  {
                      Text = "You are an expert software engineer with deep knowledge of distributed systems...",
                      CacheControl = new(),
                  },
              ]
          ),
          Messages = [new() { Role = Role.User, Content = "warmup" }],
      }
  );

  Console.WriteLine(prewarm.StopReason?.Raw()); // "max_tokens"
  Console.WriteLine(prewarm.Content.Count); // 0
  Console.WriteLine(prewarm.Usage);

go Go
  client := anthropic.NewClient()

  prewarm, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 0,
  	System: []anthropic.TextBlockParam{
  		{
  			Text:         "You are an expert software engineer with deep knowledge of distributed systems...",
  			CacheControl: anthropic.NewCacheControlEphemeralParam(),
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("warmup")),
  	},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Println(prewarm.StopReason) // "max_tokens"
  fmt.Println(prewarm.Content)    // []
  fmt.Println(prewarm.Usage.RawJSON())

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  Message prewarm = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(0)
          .systemOfTextBlockParams(List.of(TextBlockParam.builder()
                  .text("You are an expert software engineer with deep knowledge of distributed systems...")
                  .cacheControl(CacheControlEphemeral.builder().build())
                  .build()))
          .addUserMessage("warmup")
          .build());

  IO.println(prewarm.stopReason()); // Optional[max_tokens]
  IO.println(prewarm.content());    // []
  IO.println(prewarm.usage());

php PHP
  $client = new Client();

  $prewarm = $client->messages->create(
      model: Model::CLAUDE_OPUS_5,
      maxTokens: 0,
      system: [
          [
              'type' => 'text',
              'text' => 'You are an expert software engineer with deep knowledge of distributed systems...',
              'cache_control' => ['type' => 'ephemeral'],
          ],
      ],
      messages: [['role' => 'user', 'content' => 'warmup']],
  );

  echo $prewarm->stopReason->value, PHP_EOL; // "max_tokens"
  echo json_encode($prewarm->content), PHP_EOL; // []
  echo json_encode($prewarm->usage), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  prewarm = client.messages.create(
    model: Anthropic::Model::CLAUDE_OPUS_5,
    max_tokens: 0,
    system_: [
      {
        type: "text",
        text: "You are an expert software engineer with deep knowledge of distributed systems...",
        cache_control: {type: "ephemeral"}
      }
    ],
    messages: [{role: "user", content: "warmup"}]
  )

  puts prewarm.stop_reason # :max_tokens
  puts prewarm.content # []
  puts prewarm.usage

json Output
{
  "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "content": [],
  "model": "claude-opus-5",
  "stop_reason": "max_tokens",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 8,
    "cache_creation_input_tokens": 5120,
    "cache_read_input_tokens": 0,
    "cache_creation": {
      "ephemeral_5m_input_tokens": 5120,
      "ephemeral_1h_input_tokens": 0
    },
    "iterations": [
      {
        "input_tokens": 8,
        "output_tokens": 0,
        "cache_read_input_tokens": 0,
        "cache_creation_input_tokens": 5120,
        "cache_creation": {
          "ephemeral_5m_input_tokens": 5120,
          "ephemeral_1h_input_tokens": 0
        },
        "type": "message"
      }
    ],
    "output_tokens": 0,
    "service_tier": "standard",
    "inference_geo": "global"
  }
}

bash cURL
  # Warm the cache at application startup or on a scheduled interval.
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 0,
      "system": [
        {
          "type": "text",
          "text": "You are an expert software engineer with deep knowledge of distributed systems...",
          "cache_control": {"type": "ephemeral"}
        }
      ],
      "messages": [{"role": "user", "content": "warmup"}]
    }'

  # Later, when the user submits a message, the system-prompt prefix is already cached.
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "system": [
        {
          "type": "text",
          "text": "You are an expert software engineer with deep knowledge of distributed systems...",
          "cache_control": {"type": "ephemeral"}
        }
      ],
      "messages": [{"role": "user", "content": "How do I implement a binary search tree?"}]
    }'

bash CLI
  # Warm the cache at application startup or on a scheduled interval.
  ant messages create --transform usage <<'YAML'
  model: claude-opus-5
  max_tokens: 0
  system:
    - type: text
      text: >-
        You are an expert software engineer with deep knowledge of
        distributed systems...
      cache_control:
        type: ephemeral
  messages:
    - role: user
      content: warmup
  YAML

  # Later, when the user submits a message, the system-prompt prefix is already cached.
  ant messages create --transform 'content.#(type=="text").text' --raw-output <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  system:
    - type: text
      text: >-
        You are an expert software engineer with deep knowledge of
        distributed systems...
      cache_control:
        type: ephemeral
  messages:
    - role: user
      content: How do I implement a binary search tree?
  YAML

python Python
  client = anthropic.Anthropic()

  SYSTEM_PROMPT = [
      {
          "type": "text",
          "text": "You are an expert software engineer with deep knowledge of distributed systems...",
          "cache_control": {"type": "ephemeral"},
      }
  ]


  def prewarm_cache() -> None:
      """Call this at application startup or on a scheduled interval."""
      client.messages.create(
          model="claude-opus-5",
          max_tokens=0,
          system=SYSTEM_PROMPT,
          messages=[{"role": "user", "content": "warmup"}],
      )


  def respond(user_message: str) -> anthropic.types.Message:
      """The real user request; benefits from a warm cache."""
      return client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          system=SYSTEM_PROMPT,
          messages=[{"role": "user", "content": user_message}],
      )


  # Warm the cache before any user traffic arrives.
  prewarm_cache()

  # Later, when the user submits a message, the system-prompt prefix is already cached.
  response = respond("How do I implement a binary search tree?")
  for block in response.content:
      if block.type == "text":
          print(block.text)

typescript TypeScript
  const client = new Anthropic();

  const SYSTEM_PROMPT: Anthropic.TextBlockParam[] = [
    {
      type: "text",
      text: "You are an expert software engineer with deep knowledge of distributed systems...",
      cache_control: { type: "ephemeral" }
    }
  ];

  // Call this at application startup or on a scheduled interval.
  async function prewarmCache(): Promise<void> {
    await client.messages.create({
      model: "claude-opus-5",
      max_tokens: 0,
      system: SYSTEM_PROMPT,
      messages: [{ role: "user", content: "warmup" }]
    });
  }

  // The real user request; benefits from a warm cache.
  async function respond(userMessage: string): Promise<Anthropic.Message> {
    return client.messages.create({
      model: "claude-opus-5",
      max_tokens: 1024,
      system: SYSTEM_PROMPT,
      messages: [{ role: "user", content: userMessage }]
    });
  }

  // Warm the cache before any user traffic arrives.
  await prewarmCache();

  // Later, when the user submits a message, the system-prompt prefix is already cached.
  const response = await respond("How do I implement a binary search tree?");
  const textBlock = response.content.find(
    (block): block is Anthropic.TextBlock => block.type === "text"
  );
  console.log(textBlock?.text);

csharp C#
  AnthropicClient client = new();

  List<TextBlockParam> systemPrompt =
  [
      new TextBlockParam
      {
          Text = "You are an expert software engineer with deep knowledge of distributed systems...",
          CacheControl = new(),
      },
  ];

  // Call this at application startup or on a scheduled interval.
  async Task PrewarmCache() =>
      await client.Messages.Create(
          new()
          {
              Model = Model.ClaudeOpus5,
              MaxTokens = 0,
              System = new(systemPrompt),
              Messages = [new() { Role = Role.User, Content = "warmup" }],
          }
      );

  // The real user request; benefits from a warm cache.
  async Task<Message> Respond(string userMessage) =>
      await client.Messages.Create(
          new()
          {
              Model = Model.ClaudeOpus5,
              MaxTokens = 1024,
              System = new(systemPrompt),
              Messages = [new() { Role = Role.User, Content = userMessage }],
          }
      );

  // Warm the cache before any user traffic arrives.
  await PrewarmCache();

  // Later, when the user submits a message, the system-prompt prefix is already cached.
  var response = await Respond("How do I implement a binary search tree?");
  foreach (var block in response.Content)
  {
      if (block.TryPickText(out var textBlock))
      {
          Console.WriteLine(textBlock.Text);
      }
  }

go Go
  var client = anthropic.NewClient()

  var systemPrompt = []anthropic.TextBlockParam{
  	{
  		Text:         "You are an expert software engineer with deep knowledge of distributed systems...",
  		CacheControl: anthropic.NewCacheControlEphemeralParam(),
  	},
  }

  // Call this at application startup or on a scheduled interval.
  func prewarmCache() error {
  	_, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 0,
  		System:    systemPrompt,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("warmup")),
  		},
  	})
  	return err
  }

  // The real user request; benefits from a warm cache.
  func respond(userMessage string) (*anthropic.Message, error) {
  	return client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 1024,
  		System:    systemPrompt,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock(userMessage)),
  		},
  	})
  }

  func main() {
  	// Warm the cache before any user traffic arrives.
  	if err := prewarmCache(); err != nil {
  		log.Fatal(err)
  	}

  	// Later, when the user submits a message, the system-prompt prefix is already cached.
  	response, err := respond("How do I implement a binary search tree?")
  	if err != nil {
  		log.Fatal(err)
  	}
  	for _, block := range response.Content {
  		if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  			fmt.Println(textBlock.Text)
  		}
  	}
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  List<TextBlockParam> systemPrompt = List.of(TextBlockParam.builder()
          .text("You are an expert software engineer with deep knowledge of distributed systems...")
          .cacheControl(CacheControlEphemeral.builder().build())
          .build());

  // Call this at application startup or on a scheduled interval.
  void prewarmCache() {
      client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(0)
              .systemOfTextBlockParams(systemPrompt)
              .addUserMessage("warmup")
              .build());
  }

  // The real user request; benefits from a warm cache.
  Message respond(String userMessage) {
      return client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024)
              .systemOfTextBlockParams(systemPrompt)
              .addUserMessage(userMessage)
              .build());
  }

  void main() {
      // Warm the cache before any user traffic arrives.
      prewarmCache();

      // Later, when the user submits a message, the system-prompt prefix is already cached.
      Message response = respond("How do I implement a binary search tree?");
      response.content().stream()
              .flatMap(block -> block.text().stream())
              .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  $client = new Client();

  $systemPrompt = [
      [
          'type' => 'text',
          'text' => 'You are an expert software engineer with deep knowledge of distributed systems...',
          'cache_control' => ['type' => 'ephemeral'],
      ],
  ];

  // Call this at application startup or on a scheduled interval.
  $prewarmCache = fn () => $client->messages->create(
      model: Model::CLAUDE_OPUS_5,
      maxTokens: 0,
      system: $systemPrompt,
      messages: [['role' => 'user', 'content' => 'warmup']],
  );

  // The real user request; benefits from a warm cache.
  $respond = fn (string $userMessage) => $client->messages->create(
      model: Model::CLAUDE_OPUS_5,
      maxTokens: 1024,
      system: $systemPrompt,
      messages: [['role' => 'user', 'content' => $userMessage]],
  );

  // Warm the cache before any user traffic arrives.
  $prewarmCache();

  // Later, when the user submits a message, the system-prompt prefix is already cached.
  $response = $respond('How do I implement a binary search tree?');
  foreach ($response->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, PHP_EOL;
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  SYSTEM_PROMPT = [
    {
      type: "text",
      text: "You are an expert software engineer with deep knowledge of distributed systems...",
      cache_control: {type: "ephemeral"}
    }
  ]

  # Call this at application startup or on a scheduled interval.
  def prewarm_cache(client)
    client.messages.create(
      model: Anthropic::Model::CLAUDE_OPUS_5,
      max_tokens: 0,
      system_: SYSTEM_PROMPT,
      messages: [{role: "user", content: "warmup"}]
    )
  end

  # The real user request; benefits from a warm cache.
  def respond(client, user_message)
    client.messages.create(
      model: Anthropic::Model::CLAUDE_OPUS_5,
      max_tokens: 1024,
      system_: SYSTEM_PROMPT,
      messages: [{role: "user", content: user_message}]
    )
  end

  # Warm the cache before any user traffic arrives.
  prewarm_cache(client)

  # Later, when the user submits a message, the system-prompt prefix is already cached.
  response = respond(client, "How do I implement a binary search tree?")
  response.content.each do |block|
    puts block.text if block.type == :text
  end
  ```
</CodeGroup>

Keep in mind that the cache TTL still applies. For the default 5-minute cache, send a new pre-warm request at least every 5 minutes to keep the cache warm. For longer gaps between user requests, use the [1-hour cache duration](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#1-hour-cache-duration) instead.

### Limitations

A `max_tokens: 0` request is rejected with an `invalid_request_error` if any of the following are set, since each implies output that a zero-token budget cannot produce:

* `stream: true`
* [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) (`thinking.type: "enabled"`)
* [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) (`output_config.format`)
* `tool_choice` of `{"type": "tool", ...}` or `{"type": "any"}`

`max_tokens: 0` is also rejected inside a [Message Batches](https://platform.claude.com/docs/en/build-with-claude/batch-processing) request. Pre-warming targets time-to-first-token, which does not apply to batch processing, and a cache entry written during batch processing would likely expire before the follow-up request runs.

### Replacing the max\_tokens=1 workaround

Before `max_tokens: 0` was available, some applications used `max_tokens: 1` warm-up calls to achieve the same effect. The `max_tokens: 0` approach is preferred: no output is produced, so there is no single-token reply to discard, no output tokens are billed, and the intent of the request is unambiguous.

***


## Prompt caching examples

Source: https://platform.claude.com/llms-full.txt#prompt-caching-examples

To help you get started with prompt caching, the [prompt caching cookbook](https://platform.claude.com/cookbook/misc-prompt-caching) provides detailed examples and best practices.

The following code snippets showcase various prompt caching patterns. These examples demonstrate how to implement caching in different scenarios, helping you understand the practical applications of this feature:

<AccordionGroup>
  <Accordion title="Large context caching example">
    <CodeGroup>
      ```bash cURL
      curl https://api.anthropic.com/v1/messages \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "content-type: application/json" \
        -d '{
          "model": "claude-opus-5",
          "max_tokens": 1024,
          "system": [
            {
              "type": "text",
              "text": "You are an AI assistant tasked with analyzing legal documents."
            },
            {
              "type": "text",
              "text": "Here is the full text of a complex legal agreement: [Insert full text of a 50-page legal agreement here]",
              "cache_control": {"type": "ephemeral"}
            }
          ],
          "messages": [
            {
              "role": "user",
              "content": "What are the key terms and conditions in this agreement?"
            }
          ]
        }'

bash CLI
      ant messages create --transform usage <<'YAML'
      model: claude-opus-5
      max_tokens: 1024
      system:
        - type: text
          text: You are an AI assistant tasked with analyzing legal documents.
        - type: text
          text: >-
            Here is the full text of a complex legal agreement:
            [Insert full text of a 50-page legal agreement here]
          cache_control:
            type: ephemeral
      messages:
        - role: user
          content: What are the key terms and conditions in this agreement?
      YAML

python Python
      client = anthropic.Anthropic()

      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          system=[
              {
                  "type": "text",
                  "text": "You are an AI assistant tasked with analyzing legal documents.",
              },
              {
                  "type": "text",
                  "text": "Here is the full text of a complex legal agreement: [Insert full text of a 50-page legal agreement here]",
                  "cache_control": {"type": "ephemeral"},
              },
          ],
          messages=[
              {
                  "role": "user",
                  "content": "What are the key terms and conditions in this agreement?",
              }
          ],
      )
      print(response.usage.model_dump_json())

typescript TypeScript
      const client = new Anthropic();

      const response = await client.messages.create({
        model: "claude-opus-5",
        max_tokens: 1024,
        system: [
          {
            type: "text",
            text: "You are an AI assistant tasked with analyzing legal documents."
          },
          {
            type: "text",
            text: "Here is the full text of a complex legal agreement: [Insert full text of a 50-page legal agreement here]",
            cache_control: { type: "ephemeral" }
          }
        ],
        messages: [
          {
            role: "user",
            content: "What are the key terms and conditions in this agreement?"
          }
        ]
      });
      console.log(response.usage);

csharp C#
      AnthropicClient client = new()
      {
          ApiKey = Environment.GetEnvironmentVariable("ANTHROPIC_API_KEY")
      };

      var parameters = new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          System = new MessageCreateParamsSystem(new List<TextBlockParam>
          {
              new TextBlockParam()
              {
                  Text = "You are an AI assistant tasked with analyzing legal documents.",
              },
              new TextBlockParam()
              {
                  Text = "Here is the full text of a complex legal agreement: [Insert full text of a 50-page legal agreement here]",
                  CacheControl = new CacheControlEphemeral(),
              },
          }),
          Messages =
          [
              new()
              {
                  Role = Role.User,
                  Content = "What are the key terms and conditions in this agreement?"
              }
          ]
      };

      var message = await client.Messages.Create(parameters);
      Console.WriteLine(message.Usage);

go Go
      client := anthropic.NewClient()

      response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
      	Model:     anthropic.ModelClaudeOpus5,
      	MaxTokens: 1024,
      	System: []anthropic.TextBlockParam{
      		{
      			Text: "You are an AI assistant tasked with analyzing legal documents.",
      		},
      		{
      			Text:         "Here is the full text of a complex legal agreement: [Insert full text of a 50-page legal agreement here]",
      			CacheControl: anthropic.NewCacheControlEphemeralParam(),
      		},
      	},
      	Messages: []anthropic.MessageParam{
      		anthropic.NewUserMessage(anthropic.NewTextBlock("What are the key terms and conditions in this agreement?")),
      	},
      })
      if err != nil {
      	log.Fatal(err)
      }
      fmt.Println(response.Usage.RawJSON())

java Java
      import com.anthropic.models.messages.CacheControlEphemeral;
      // ...
      public class LegalDocumentAnalysisExample {

        public static void main(String[] args) {
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          MessageCreateParams params = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_5)
            .maxTokens(1024)
            .systemOfTextBlockParams(
              List.of(
                TextBlockParam.builder()
                  .text("You are an AI assistant tasked with analyzing legal documents.")
                  .build(),
                TextBlockParam.builder()
                  .text(
                    "Here is the full text of a complex legal agreement: [Insert full text of a 50-page legal agreement here]"
                  )
                  .cacheControl(CacheControlEphemeral.builder().build())
                  .build()
              )
            )
            .addUserMessage("What are the key terms and conditions in this agreement?")
            .build();

          Message message = client.messages().create(params);
          System.out.println(message.usage());
        }
      }

php PHP
      $client = new Client();

      $message = $client->messages->create(
          maxTokens: 1024,
          messages: [
              [
                  'role' => 'user',
                  'content' => 'What are the key terms and conditions in this agreement?'
              ]
          ],
          model: 'claude-opus-5',
          system: [
              [
                  'type' => 'text',
                  'text' => 'You are an AI assistant tasked with analyzing legal documents.'
              ],
              [
                  'type' => 'text',
                  'text' => 'Here is the full text of a complex legal agreement: [Insert full text of a 50-page legal agreement here]',
                  'cache_control' => ['type' => 'ephemeral']
              ]
          ],
      );

      echo json_encode($message->usage), PHP_EOL;

ruby Ruby
      client = Anthropic::Client.new

      message = client.messages.create(
        model: "claude-opus-5",
        max_tokens: 1024,
        system: [
          {
            type: "text",
            text: "You are an AI assistant tasked with analyzing legal documents."
          },
          {
            type: "text",
            text: "Here is the full text of a complex legal agreement: [Insert full text of a 50-page legal agreement here]",
            cache_control: { type: "ephemeral" }
          }
        ],
        messages: [
          {
            role: "user",
            content: "What are the key terms and conditions in this agreement?"
          }
        ]
      )
      puts message.usage

json
    {
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "tools": [
        {
          "name": "get_weather",
          "description": "Get the current weather in a given location",
          "input_schema": {
            "type": "object",
            "properties": { "location": { "type": "string" } },
            "required": ["location"]
          }
        },
        {
          "name": "get_time",
          "description": "Get the current time in a given time zone",
          "input_schema": {
            "type": "object",
            "properties": { "timezone": { "type": "string" } },
            "required": ["timezone"]
          },
          "cache_control": { "type": "ephemeral" }
        }
      ],
      "messages": [{ "role": "user", "content": "What is the weather and time in New York?" }]
    }

bash cURL
      curl https://api.anthropic.com/v1/messages \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "content-type: application/json" \
        -d '{
          "model": "claude-opus-5",
          "max_tokens": 1024,
          "system": [
            {
              "type": "text",
              "text": "...long system prompt",
              "cache_control": {"type": "ephemeral"}
            }
          ],
          "messages": [
            {
              "role": "user",
              "content": [
                {
                  "type": "text",
                  "text": "Hello, can you tell me more about the solar system?"
                }
              ]
            },
            {
              "role": "assistant",
              "content": "Certainly! The solar system is the collection of celestial bodies that orbit our Sun. It consists of eight planets, numerous moons, asteroids, comets, and other objects. The planets, in order from closest to farthest from the Sun, are: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Each planet has its own unique characteristics and features. Is there a specific aspect of the solar system you would like to know more about?"
            },
            {
              "role": "user",
              "content": [
                {
                  "type": "text",
                  "text": "Good to know."
                },
                {
                  "type": "text",
                  "text": "Tell me more about Mars.",
                  "cache_control": {"type": "ephemeral"}
                }
              ]
            }
          ]
        }'

bash CLI
      ant messages create --transform usage <<'YAML'
      model: claude-opus-5
      max_tokens: 1024
      system:
        - type: text
          text: "...long system prompt"
          cache_control:
            type: ephemeral
      messages:
        - role: user
          content:
            - type: text
              text: Hello, can you tell me more about the solar system?
        - role: assistant
          content: >-
            Certainly! The solar system is the collection of celestial bodies that
            orbit our Sun. It consists of eight planets, numerous moons, asteroids,
            comets, and other objects. The planets, in order from closest to farthest
            from the Sun, are: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus,
            and Neptune. Each planet has its own unique characteristics and features.
            Is there a specific aspect of the solar system you would like to know
            more about?
        - role: user
          content:
            - type: text
              text: Good to know.
            - type: text
              text: Tell me more about Mars.
              cache_control:
                type: ephemeral
      YAML

python Python
      client = anthropic.Anthropic()

      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          system=[
              {
                  "type": "text",
                  "text": "...long system prompt",
                  "cache_control": {"type": "ephemeral"},
              }
          ],
          messages=[
              # ...long conversation so far
              {
                  "role": "user",
                  "content": [
                      {
                          "type": "text",
                          "text": "Hello, can you tell me more about the solar system?",
                      }
                  ],
              },
              {
                  "role": "assistant",
                  "content": "Certainly! The solar system is the collection of celestial bodies that orbit our Sun. It consists of eight planets, numerous moons, asteroids, comets, and other objects. The planets, in order from closest to farthest from the Sun, are: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Each planet has its own unique characteristics and features. Is there a specific aspect of the solar system you'd like to know more about?",
              },
              {
                  "role": "user",
                  "content": [
                      {"type": "text", "text": "Good to know."},
                      {
                          "type": "text",
                          "text": "Tell me more about Mars.",
                          "cache_control": {"type": "ephemeral"},
                      },
                  ],
              },
          ],
      )
      print(response.usage.model_dump_json())

typescript TypeScript
      const client = new Anthropic();

      const response = await client.messages.create({
        model: "claude-opus-5",
        max_tokens: 1024,
        system: [
          {
            type: "text",
            text: "...long system prompt",
            cache_control: { type: "ephemeral" }
          }
        ],
        messages: [
          // ...long conversation so far
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Hello, can you tell me more about the solar system?"
              }
            ]
          },
          {
            role: "assistant",
            content:
              "Certainly! The solar system is the collection of celestial bodies that orbit our Sun. It consists of eight planets, numerous moons, asteroids, comets, and other objects. The planets, in order from closest to farthest from the Sun, are: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Each planet has its own unique characteristics and features. Is there a specific aspect of the solar system you'd like to know more about?"
          },
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Good to know."
              },
              {
                type: "text",
                text: "Tell me more about Mars.",
                cache_control: { type: "ephemeral" }
              }
            ]
          }
        ]
      });
      console.log(response.usage);

csharp C#
      AnthropicClient client = new();

      var parameters = new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          System = new MessageCreateParamsSystem(new List<TextBlockParam>
          {
              new TextBlockParam()
              {
                  Text = "...long system prompt",
                  CacheControl = new CacheControlEphemeral(),
              },
          }),
          Messages =
          [
              new()
              {
                  Role = Role.User,
                  Content = new MessageParamContent(new List<ContentBlockParam>
                  {
                      new ContentBlockParam(new TextBlockParam("Hello, can you tell me more about the solar system?")),
                  }),
              },
              new()
              {
                  Role = Role.Assistant,
                  Content = "Certainly! The solar system is the collection of celestial bodies that orbit our Sun. It consists of eight planets, numerous moons, asteroids, comets, and other objects. The planets, in order from closest to farthest from the Sun, are: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Each planet has its own unique characteristics and features. Is there a specific aspect of the solar system you would like to know more about?"
              },
              new()
              {
                  Role = Role.User,
                  Content = new MessageParamContent(new List<ContentBlockParam>
                  {
                      new ContentBlockParam(new TextBlockParam("Good to know.")),
                      new ContentBlockParam(new TextBlockParam()
                      {
                          Text = "Tell me more about Mars.",
                          CacheControl = new CacheControlEphemeral(),
                      }),
                  })
              }
          ]
      };

      var message = await client.Messages.Create(parameters);
      Console.WriteLine(message.Usage);

go Go
      client := anthropic.NewClient()

      response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
      	Model:     anthropic.ModelClaudeOpus5,
      	MaxTokens: 1024,
      	System: []anthropic.TextBlockParam{
      		{
      			Text:         "...long system prompt",
      			CacheControl: anthropic.NewCacheControlEphemeralParam(),
      		},
      	},
      	Messages: []anthropic.MessageParam{
      		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, can you tell me more about the solar system?")),
      		anthropic.NewAssistantMessage(anthropic.NewTextBlock("Certainly! The solar system is the collection of celestial bodies that orbit our Sun. It consists of eight planets, numerous moons, asteroids, comets, and other objects. The planets, in order from closest to farthest from the Sun, are: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Each planet has its own unique characteristics and features. Is there a specific aspect of the solar system you would like to know more about?")),
      		{
      			Role: anthropic.MessageParamRoleUser,
      			Content: []anthropic.ContentBlockParamUnion{
      				anthropic.NewTextBlock("Good to know."),
      				{OfText: &anthropic.TextBlockParam{
      					Text:         "Tell me more about Mars.",
      					CacheControl: anthropic.NewCacheControlEphemeralParam(),
      				}},
      			},
      		},
      	},
      })
      if err != nil {
      	log.Fatal(err)
      }
      fmt.Println(response.Usage.RawJSON())

java Java
      import com.anthropic.models.messages.CacheControlEphemeral;
      // ...
      public class ConversationWithCacheControlExample {

        public static void main(String[] args) {
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          // Create ephemeral system prompt
          TextBlockParam systemPrompt = TextBlockParam.builder()
            .text("...long system prompt")
            .cacheControl(CacheControlEphemeral.builder().build())
            .build();

          // Create message params
          MessageCreateParams params = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_5)
            .maxTokens(1024)
            .systemOfTextBlockParams(List.of(systemPrompt))
            // First user message (without cache control)
            .addUserMessage("Hello, can you tell me more about the solar system?")
            // Assistant response
            .addAssistantMessage(
              "Certainly! The solar system is the collection of celestial bodies that orbit our Sun. It consists of eight planets, numerous moons, asteroids, comets, and other objects. The planets, in order from closest to farthest from the Sun, are: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Each planet has its own unique characteristics and features. Is there a specific aspect of the solar system you would like to know more about?"
            )
            // Second user message (with cache control)
            .addUserMessageOfBlockParams(
              List.of(
                ContentBlockParam.ofText(TextBlockParam.builder().text("Good to know.").build()),
                ContentBlockParam.ofText(
                  TextBlockParam.builder()
                    .text("Tell me more about Mars.")
                    .cacheControl(CacheControlEphemeral.builder().build())
                    .build()
                )
              )
            )
            .build();

          Message message = client.messages().create(params);
          System.out.println(message.usage());
        }
      }

php PHP
      $client = new Client();

      $message = $client->messages->create(
          maxTokens: 1024,
          messages: [
              [
                  'role' => 'user',
                  'content' => [
                      [
                          'type' => 'text',
                          'text' => 'Hello, can you tell me more about the solar system?'
                      ]
                  ]
              ],
              [
                  'role' => 'assistant',
                  'content' => "Certainly! The solar system is the collection of celestial bodies that orbit our Sun. It consists of eight planets, numerous moons, asteroids, comets, and other objects. The planets, in order from closest to farthest from the Sun, are: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Each planet has its own unique characteristics and features. Is there a specific aspect of the solar system you would like to know more about?"
              ],
              [
                  'role' => 'user',
                  'content' => [
                      ['type' => 'text', 'text' => 'Good to know.'],
                      [
                          'type' => 'text',
                          'text' => 'Tell me more about Mars.',
                          'cache_control' => ['type' => 'ephemeral']
                      ]
                  ]
              ]
          ],
          model: 'claude-opus-5',
          system: [
              [
                  'type' => 'text',
                  'text' => '...long system prompt',
                  'cache_control' => ['type' => 'ephemeral']
              ]
          ],
      );

      echo json_encode($message->usage), PHP_EOL;

ruby Ruby
      client = Anthropic::Client.new

      message = client.messages.create(
        model: "claude-opus-5",
        max_tokens: 1024,
        system: [
          {
            type: "text",
            text: "...long system prompt",
            cache_control: { type: "ephemeral" }
          }
        ],
        messages: [
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Hello, can you tell me more about the solar system?"
              }
            ]
          },
          {
            role: "assistant",
            content: "Certainly! The solar system is the collection of celestial bodies that orbit our Sun. It consists of eight planets, numerous moons, asteroids, comets, and other objects. The planets, in order from closest to farthest from the Sun, are: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Each planet has its own unique characteristics and features. Is there a specific aspect of the solar system you would like to know more about?"
          },
          {
            role: "user",
            content: [
              { type: "text", text: "Good to know." },
              {
                type: "text",
                text: "Tell me more about Mars.",
                cache_control: { type: "ephemeral" }
              }
            ]
          }
        ]
      )
      puts message.usage

bash cURL
      curl https://api.anthropic.com/v1/messages \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "content-type: application/json" \
        -d '{
          "model": "claude-opus-5",
          "max_tokens": 1024,
          "tools": [
            {
              "name": "search_documents",
              "description": "Search through the knowledge base",
              "input_schema": {
                "type": "object",
                "properties": {
                  "query": {
                    "type": "string",
                    "description": "Search query"
                  }
                },
                "required": ["query"]
              }
            },
            {
              "name": "get_document",
              "description": "Retrieve a specific document by ID",
              "input_schema": {
                "type": "object",
                "properties": {
                  "doc_id": {
                    "type": "string",
                    "description": "Document ID"
                  }
                },
                "required": ["doc_id"]
              },
              "cache_control": {"type": "ephemeral"}
            }
          ],
          "system": [
            {
              "type": "text",
              "text": "You are a helpful research assistant with access to a document knowledge base.\n\n# Instructions\n- Always search for relevant documents before answering\n- Provide citations for your sources\n- Be objective and accurate in your responses\n- If multiple documents contain relevant information, synthesize them\n- Acknowledge when information is not available in the knowledge base",
              "cache_control": {"type": "ephemeral"}
            },
            {
              "type": "text",
              "text": "# Knowledge Base Context\n\nHere are the relevant documents for this conversation:\n\n## Document 1: Solar System Overview\nThe solar system consists of the Sun and all objects that orbit it...\n\n## Document 2: Planetary Characteristics\nEach planet has unique features. Mercury is the smallest planet...\n\n## Document 3: Mars Exploration\nMars has been a target of exploration for decades...\n\n[Additional documents...]",
              "cache_control": {"type": "ephemeral"}
            }
          ],
          "messages": [
            {
              "role": "user",
              "content": "Can you search for information about Mars rovers?"
            },
            {
              "role": "assistant",
              "content": [
                {
                  "type": "tool_use",
                  "id": "tool_1",
                  "name": "search_documents",
                  "input": {"query": "Mars rovers"}
                }
              ]
            },
            {
              "role": "user",
              "content": [
                {
                  "type": "tool_result",
                  "tool_use_id": "tool_1",
                  "content": "Found 3 relevant documents: Document 3 (Mars Exploration), Document 7 (Rover Technology), Document 9 (Mission History)"
                }
              ]
            },
            {
              "role": "assistant",
              "content": [
                {
                  "type": "text",
                  "text": "I found 3 relevant documents about Mars rovers. Let me get more details from the Mars Exploration document."
                }
              ]
            },
            {
              "role": "user",
              "content": [
                {
                  "type": "text",
                  "text": "Yes, please tell me about the Perseverance rover specifically.",
                  "cache_control": {"type": "ephemeral"}
                }
              ]
            }
          ]
        }'

bash CLI
      ant messages create --transform usage <<'YAML'
      model: claude-opus-5
      max_tokens: 1024
      tools:
        - name: search_documents
          description: Search through the knowledge base
          input_schema:
            type: object
            properties:
              query:
                type: string
                description: Search query
            required: [query]
        - name: get_document
          description: Retrieve a specific document by ID
          input_schema:
            type: object
            properties:
              doc_id:
                type: string
                description: Document ID
            required: [doc_id]
          cache_control:
            type: ephemeral
      system:
        - type: text
          text: |-
            You are a helpful research assistant with access to a document knowledge base.

            # Instructions
            - Always search for relevant documents before answering
            - Provide citations for your sources
            - Be objective and accurate in your responses
            - If multiple documents contain relevant information, synthesize them
            - Acknowledge when information is not available in the knowledge base
          cache_control:
            type: ephemeral
        - type: text
          text: |-
            # Knowledge Base Context

            Here are the relevant documents for this conversation:

            ## Document 1: Solar System Overview
            The solar system consists of the Sun and all objects that orbit it...

            ## Document 2: Planetary Characteristics
            Each planet has unique features. Mercury is the smallest planet...

            ## Document 3: Mars Exploration
            Mars has been a target of exploration for decades...

            [Additional documents...]
          cache_control:
            type: ephemeral
      messages:
        - role: user
          content: Can you search for information about Mars rovers?
        - role: assistant
          content:
            - type: tool_use
              id: tool_1
              name: search_documents
              input:
                query: Mars rovers
        - role: user
          content:
            - type: tool_result
              tool_use_id: tool_1
              content: >-
                Found 3 relevant documents: Document 3 (Mars Exploration),
                Document 7 (Rover Technology), Document 9 (Mission History)
        - role: assistant
          content:
            - type: text
              text: >-
                I found 3 relevant documents about Mars rovers. Let me get more
                details from the Mars Exploration document.
        - role: user
          content:
            - type: text
              text: Yes, please tell me about the Perseverance rover specifically.
              cache_control:
                type: ephemeral
      YAML

python Python
      client = anthropic.Anthropic()

      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          tools=[
              {
                  "name": "search_documents",
                  "description": "Search through the knowledge base",
                  "input_schema": {
                      "type": "object",
                      "properties": {
                          "query": {"type": "string", "description": "Search query"}
                      },
                      "required": ["query"],
                  },
              },
              {
                  "name": "get_document",
                  "description": "Retrieve a specific document by ID",
                  "input_schema": {
                      "type": "object",
                      "properties": {
                          "doc_id": {"type": "string", "description": "Document ID"}
                      },
                      "required": ["doc_id"],
                  },
                  "cache_control": {"type": "ephemeral"},
              },
          ],
          system=[
              {
                  "type": "text",
                  "text": "You are a helpful research assistant with access to a document knowledge base.\n\n# Instructions\n- Always search for relevant documents before answering\n- Provide citations for your sources\n- Be objective and accurate in your responses\n- If multiple documents contain relevant information, synthesize them\n- Acknowledge when information is not available in the knowledge base",
                  "cache_control": {"type": "ephemeral"},
              },
              {
                  "type": "text",
                  "text": "# Knowledge Base Context\n\nHere are the relevant documents for this conversation:\n\n## Document 1: Solar System Overview\nThe solar system consists of the Sun and all objects that orbit it...\n\n## Document 2: Planetary Characteristics\nEach planet has unique features. Mercury is the smallest planet...\n\n## Document 3: Mars Exploration\nMars has been a target of exploration for decades...\n\n[Additional documents...]",
                  "cache_control": {"type": "ephemeral"},
              },
          ],
          messages=[
              {
                  "role": "user",
                  "content": "Can you search for information about Mars rovers?",
              },
              {
                  "role": "assistant",
                  "content": [
                      {
                          "type": "tool_use",
                          "id": "tool_1",
                          "name": "search_documents",
                          "input": {"query": "Mars rovers"},
                      }
                  ],
              },
              {
                  "role": "user",
                  "content": [
                      {
                          "type": "tool_result",
                          "tool_use_id": "tool_1",
                          "content": "Found 3 relevant documents: Document 3 (Mars Exploration), Document 7 (Rover Technology), Document 9 (Mission History)",
                      }
                  ],
              },
              {
                  "role": "assistant",
                  "content": [
                      {
                          "type": "text",
                          "text": "I found 3 relevant documents about Mars rovers. Let me get more details from the Mars Exploration document.",
                      }
                  ],
              },
              {
                  "role": "user",
                  "content": [
                      {
                          "type": "text",
                          "text": "Yes, please tell me about the Perseverance rover specifically.",
                          "cache_control": {"type": "ephemeral"},
                      }
                  ],
              },
          ],
      )
      print(response.usage.model_dump_json())

typescript TypeScript
      const client = new Anthropic();

      const response = await client.messages.create({
        model: "claude-opus-5",
        max_tokens: 1024,
        tools: [
          {
            name: "search_documents",
            description: "Search through the knowledge base",
            input_schema: {
              type: "object",
              properties: {
                query: {
                  type: "string",
                  description: "Search query"
                }
              },
              required: ["query"]
            }
          },
          {
            name: "get_document",
            description: "Retrieve a specific document by ID",
            input_schema: {
              type: "object",
              properties: {
                doc_id: {
                  type: "string",
                  description: "Document ID"
                }
              },
              required: ["doc_id"]
            },
            cache_control: { type: "ephemeral" }
          }
        ],
        system: [
          {
            type: "text",
            text: "You are a helpful research assistant with access to a document knowledge base.\n\n# Instructions\n- Always search for relevant documents before answering\n- Provide citations for your sources\n- Be objective and accurate in your responses\n- If multiple documents contain relevant information, synthesize them\n- Acknowledge when information is not available in the knowledge base",
            cache_control: { type: "ephemeral" }
          },
          {
            type: "text",
            text: "# Knowledge Base Context\n\nHere are the relevant documents for this conversation:\n\n## Document 1: Solar System Overview\nThe solar system consists of the Sun and all objects that orbit it...\n\n## Document 2: Planetary Characteristics\nEach planet has unique features. Mercury is the smallest planet...\n\n## Document 3: Mars Exploration\nMars has been a target of exploration for decades...\n\n[Additional documents...]",
            cache_control: { type: "ephemeral" }
          }
        ],
        messages: [
          {
            role: "user",
            content: "Can you search for information about Mars rovers?"
          },
          {
            role: "assistant",
            content: [
              {
                type: "tool_use",
                id: "tool_1",
                name: "search_documents",
                input: { query: "Mars rovers" }
              }
            ]
          },
          {
            role: "user",
            content: [
              {
                type: "tool_result",
                tool_use_id: "tool_1",
                content:
                  "Found 3 relevant documents: Document 3 (Mars Exploration), Document 7 (Rover Technology), Document 9 (Mission History)"
              }
            ]
          },
          {
            role: "assistant",
            content: [
              {
                type: "text",
                text: "I found 3 relevant documents about Mars rovers. Let me get more details from the Mars Exploration document."
              }
            ]
          },
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Yes, please tell me about the Perseverance rover specifically.",
                cache_control: { type: "ephemeral" }
              }
            ]
          }
        ]
      });
      console.log(response.usage);

csharp C#
      AnthropicClient client = new()
      {
          ApiKey = Environment.GetEnvironmentVariable("ANTHROPIC_API_KEY")
      };

      var parameters = new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Tools =
          [
              new ToolUnion(new Tool()
              {
                  Name = "search_documents",
                  Description = "Search through the knowledge base",
                  InputSchema = new InputSchema()
                  {
                      Properties = new Dictionary<string, JsonElement>
                      {
                          ["query"] = JsonSerializer.SerializeToElement(new { type = "string", description = "Search query" }),
                      },
                      Required = ["query"],
                  },
              }),
              new ToolUnion(new Tool()
              {
                  Name = "get_document",
                  Description = "Retrieve a specific document by ID",
                  InputSchema = new InputSchema()
                  {
                      Properties = new Dictionary<string, JsonElement>
                      {
                          ["doc_id"] = JsonSerializer.SerializeToElement(new { type = "string", description = "Document ID" }),
                      },
                      Required = ["doc_id"],
                  },
                  CacheControl = new CacheControlEphemeral(),
              }),
          ],
          System = new MessageCreateParamsSystem(new List<TextBlockParam>
          {
              new TextBlockParam()
              {
                  Text = "You are a helpful research assistant with access to a document knowledge base.\n\n# Instructions\n- Always search for relevant documents before answering\n- Provide citations for your sources\n- Be objective and accurate in your responses\n- If multiple documents contain relevant information, synthesize them\n- Acknowledge when information is not available in the knowledge base",
                  CacheControl = new CacheControlEphemeral(),
              },
              new TextBlockParam()
              {
                  Text = "# Knowledge Base Context\n\nHere are the relevant documents for this conversation:\n\n## Document 1: Solar System Overview\nThe solar system consists of the Sun and all objects that orbit it...\n\n## Document 2: Planetary Characteristics\nEach planet has unique features. Mercury is the smallest planet...\n\n## Document 3: Mars Exploration\nMars has been a target of exploration for decades...\n\n[Additional documents...]",
                  CacheControl = new CacheControlEphemeral(),
              },
          }),
          Messages =
          [
              new() { Role = Role.User, Content = "Can you search for information about Mars rovers?" },
              new()
              {
                  Role = Role.Assistant,
                  Content = new MessageParamContent(new List<ContentBlockParam>
                  {
                      new ContentBlockParam(new ToolUseBlockParam()
                      {
                          ID = "tool_1",
                          Name = "search_documents",
                          Input = new Dictionary<string, JsonElement>
                          {
                              ["query"] = JsonSerializer.SerializeToElement("Mars rovers"),
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
                          ToolUseID = "tool_1",
                          Content = "Found 3 relevant documents: Document 3 (Mars Exploration), Document 7 (Rover Technology), Document 9 (Mission History)",
                      }),
                  }),
              },
              new()
              {
                  Role = Role.Assistant,
                  Content = "I found 3 relevant documents about Mars rovers. Let me get more details from the Mars Exploration document.",
              },
              new()
              {
                  Role = Role.User,
                  Content = new MessageParamContent(new List<ContentBlockParam>
                  {
                      new ContentBlockParam(new TextBlockParam()
                      {
                          Text = "Yes, please tell me about the Perseverance rover specifically.",
                          CacheControl = new CacheControlEphemeral(),
                      }),
                  }),
              },
          ]
      };

      var message = await client.Messages.Create(parameters);
      Console.WriteLine(message.Usage);

go Go
      client := anthropic.NewClient()

      response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
      	Model:     anthropic.ModelClaudeOpus5,
      	MaxTokens: 1024,
      	Tools: []anthropic.ToolUnionParam{
      		{OfTool: &anthropic.ToolParam{
      			Name:        "search_documents",
      			Description: anthropic.String("Search through the knowledge base"),
      			InputSchema: anthropic.ToolInputSchemaParam{
      				Properties: map[string]any{
      					"query": map[string]any{
      						"type":        "string",
      						"description": "Search query",
      					},
      				},
      				Required: []string{"query"},
      			},
      		}},
      		{OfTool: &anthropic.ToolParam{
      			Name:        "get_document",
      			Description: anthropic.String("Retrieve a specific document by ID"),
      			InputSchema: anthropic.ToolInputSchemaParam{
      				Properties: map[string]any{
      					"doc_id": map[string]any{
      						"type":        "string",
      						"description": "Document ID",
      					},
      				},
      				Required: []string{"doc_id"},
      			},
      			CacheControl: anthropic.NewCacheControlEphemeralParam(),
      		}},
      	},
      	System: []anthropic.TextBlockParam{
      		{
      			Text:         "You are a helpful research assistant with access to a document knowledge base.\n\n# Instructions\n- Always search for relevant documents before answering\n- Provide citations for your sources\n- Be objective and accurate in your responses\n- If multiple documents contain relevant information, synthesize them\n- Acknowledge when information is not available in the knowledge base",
      			CacheControl: anthropic.NewCacheControlEphemeralParam(),
      		},
      		{
      			Text:         "# Knowledge Base Context\n\nHere are the relevant documents for this conversation:\n\n## Document 1: Solar System Overview\nThe solar system consists of the Sun and all objects that orbit it...\n\n## Document 2: Planetary Characteristics\nEach planet has unique features. Mercury is the smallest planet...\n\n## Document 3: Mars Exploration\nMars has been a target of exploration for decades...\n\n[Additional documents...]",
      			CacheControl: anthropic.NewCacheControlEphemeralParam(),
      		},
      	},
      	Messages: []anthropic.MessageParam{
      		anthropic.NewUserMessage(anthropic.NewTextBlock("Can you search for information about Mars rovers?")),
      		anthropic.NewAssistantMessage(anthropic.NewToolUseBlock(
      			"tool_1",
      			map[string]any{"query": "Mars rovers"},
      			"search_documents",
      		)),
      		anthropic.NewUserMessage(anthropic.NewToolResultBlock(
      			"tool_1",
      			"Found 3 relevant documents: Document 3 (Mars Exploration), Document 7 (Rover Technology), Document 9 (Mission History)",
      			false,
      		)),
      		anthropic.NewAssistantMessage(anthropic.NewTextBlock("I found 3 relevant documents about Mars rovers. Let me get more details from the Mars Exploration document.")),
      		{
      			Role: anthropic.MessageParamRoleUser,
      			Content: []anthropic.ContentBlockParamUnion{
      				{OfText: &anthropic.TextBlockParam{
      					Text:         "Yes, please tell me about the Perseverance rover specifically.",
      					CacheControl: anthropic.NewCacheControlEphemeralParam(),
      				}},
      			},
      		},
      	},
      })
      if err != nil {
      	log.Fatal(err)
      }
      fmt.Println(response.Usage.RawJSON())

java Java
      import com.anthropic.models.messages.CacheControlEphemeral;
      // ...
      public class MultipleCacheBreakpointsExample {

        public static void main(String[] args) {
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          // Search tool schema
          InputSchema searchSchema = InputSchema.builder()
            .properties(
              JsonValue.from(
                Map.of("query", Map.of("type", "string", "description", "Search query"))
              )
            )
            .putAdditionalProperty("required", JsonValue.from(List.of("query")))
            .build();

          // Get document tool schema
          InputSchema getDocSchema = InputSchema.builder()
            .properties(
              JsonValue.from(
                Map.of("doc_id", Map.of("type", "string", "description", "Document ID"))
              )
            )
            .putAdditionalProperty("required", JsonValue.from(List.of("doc_id")))
            .build();

          MessageCreateParams params = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_5)
            .maxTokens(1024)
            // Tools with cache control on the last one
            .addTool(
              Tool.builder()
                .name("search_documents")
                .description("Search through the knowledge base")
                .inputSchema(searchSchema)
                .build()
            )
            .addTool(
              Tool.builder()
                .name("get_document")
                .description("Retrieve a specific document by ID")
                .inputSchema(getDocSchema)
                .cacheControl(CacheControlEphemeral.builder().build())
                .build()
            )
            // System prompts with cache control on instructions and context separately
            .systemOfTextBlockParams(
              List.of(
                TextBlockParam.builder()
                  .text(
                    "You are a helpful research assistant with access to a document knowledge base.\n\n# Instructions\n- Always search for relevant documents before answering\n- Provide citations for your sources\n- Be objective and accurate in your responses\n- If multiple documents contain relevant information, synthesize them\n- Acknowledge when information is not available in the knowledge base"
                  )
                  .cacheControl(CacheControlEphemeral.builder().build())
                  .build(),
                TextBlockParam.builder()
                  .text(
                    "# Knowledge Base Context\n\nHere are the relevant documents for this conversation:\n\n## Document 1: Solar System Overview\nThe solar system consists of the Sun and all objects that orbit it...\n\n## Document 2: Planetary Characteristics\nEach planet has unique features. Mercury is the smallest planet...\n\n## Document 3: Mars Exploration\nMars has been a target of exploration for decades...\n\n[Additional documents...]"
                  )
                  .cacheControl(CacheControlEphemeral.builder().build())
                  .build()
              )
            )
            // Conversation history
            .addUserMessage("Can you search for information about Mars rovers?")
            .addAssistantMessageOfBlockParams(
              List.of(
                ContentBlockParam.ofToolUse(
                  ToolUseBlockParam.builder()
                    .id("tool_1")
                    .name("search_documents")
                    .input(JsonValue.from(Map.of("query", "Mars rovers")))
                    .build()
                )
              )
            )
            .addUserMessageOfBlockParams(
              List.of(
                ContentBlockParam.ofToolResult(
                  ToolResultBlockParam.builder()
                    .toolUseId("tool_1")
                    .content(
                      "Found 3 relevant documents: Document 3 (Mars Exploration), Document 7 (Rover Technology), Document 9 (Mission History)"
                    )
                    .build()
                )
              )
            )
            .addAssistantMessageOfBlockParams(
              List.of(
                ContentBlockParam.ofText(
                  TextBlockParam.builder()
                    .text(
                      "I found 3 relevant documents about Mars rovers. Let me get more details from the Mars Exploration document."
                    )
                    .build()
                )
              )
            )
            .addUserMessageOfBlockParams(
              List.of(
                ContentBlockParam.ofText(
                  TextBlockParam.builder()
                    .text("Yes, please tell me about the Perseverance rover specifically.")
                    .cacheControl(CacheControlEphemeral.builder().build())
                    .build()
                )
              )
            )
            .build();

          Message message = client.messages().create(params);
          System.out.println(message.usage());
        }
      }

php PHP
      $client = new Client();

      $message = $client->messages->create(
          maxTokens: 1024,
          messages: [
              [
                  'role' => 'user',
                  'content' => 'Can you search for information about Mars rovers?'
              ],
              [
                  'role' => 'assistant',
                  'content' => [
                      [
                          'type' => 'tool_use',
                          'id' => 'tool_1',
                          'name' => 'search_documents',
                          'input' => ['query' => 'Mars rovers']
                      ]
                  ]
              ],
              [
                  'role' => 'user',
                  'content' => [
                      [
                          'type' => 'tool_result',
                          'tool_use_id' => 'tool_1',
                          'content' => 'Found 3 relevant documents: Document 3 (Mars Exploration), Document 7 (Rover Technology), Document 9 (Mission History)'
                      ]
                  ]
              ],
              [
                  'role' => 'assistant',
                  'content' => [
                      [
                          'type' => 'text',
                          'text' => 'I found 3 relevant documents about Mars rovers. Let me get more details from the Mars Exploration document.'
                      ]
                  ]
              ],
              [
                  'role' => 'user',
                  'content' => [
                      [
                          'type' => 'text',
                          'text' => 'Yes, please tell me about the Perseverance rover specifically.',
                          'cache_control' => ['type' => 'ephemeral']
                      ]
                  ]
              ]
          ],
          model: 'claude-opus-5',
          system: [
              [
                  'type' => 'text',
                  'text' => "You are a helpful research assistant with access to a document knowledge base.\n\n# Instructions\n- Always search for relevant documents before answering\n- Provide citations for your sources\n- Be objective and accurate in your responses\n- If multiple documents contain relevant information, synthesize them\n- Acknowledge when information is not available in the knowledge base",
                  'cache_control' => ['type' => 'ephemeral']
              ],
              [
                  'type' => 'text',
                  'text' => "# Knowledge Base Context\n\nHere are the relevant documents for this conversation:\n\n## Document 1: Solar System Overview\nThe solar system consists of the Sun and all objects that orbit it...\n\n## Document 2: Planetary Characteristics\nEach planet has unique features. Mercury is the smallest planet...\n\n## Document 3: Mars Exploration\nMars has been a target of exploration for decades...\n\n[Additional documents...]",
                  'cache_control' => ['type' => 'ephemeral']
              ]
          ],
          tools: [
              [
                  'name' => 'search_documents',
                  'description' => 'Search through the knowledge base',
                  'input_schema' => [
                      'type' => 'object',
                      'properties' => [
                          'query' => [
                              'type' => 'string',
                              'description' => 'Search query'
                          ]
                      ],
                      'required' => ['query']
                  ]
              ],
              [
                  'name' => 'get_document',
                  'description' => 'Retrieve a specific document by ID',
                  'input_schema' => [
                      'type' => 'object',
                      'properties' => [
                          'doc_id' => [
                              'type' => 'string',
                              'description' => 'Document ID'
                          ]
                      ],
                      'required' => ['doc_id']
                  ],
                  'cache_control' => ['type' => 'ephemeral']
              ]
          ],
      );

      echo json_encode($message->usage), PHP_EOL;

ruby Ruby
      client = Anthropic::Client.new

      message = client.messages.create(
        model: "claude-opus-5",
        max_tokens: 1024,
        tools: [
          {
            name: "search_documents",
            description: "Search through the knowledge base",
            input_schema: {
              type: "object",
              properties: {
                query: {
                  type: "string",
                  description: "Search query"
                }
              },
              required: ["query"]
            }
          },
          {
            name: "get_document",
            description: "Retrieve a specific document by ID",
            input_schema: {
              type: "object",
              properties: {
                doc_id: {
                  type: "string",
                  description: "Document ID"
                }
              },
              required: ["doc_id"]
            },
            cache_control: { type: "ephemeral" }
          }
        ],
        system: [
          {
            type: "text",
            text: "You are a helpful research assistant with access to a document knowledge base.\n\n# Instructions\n- Always search for relevant documents before answering\n- Provide citations for your sources\n- Be objective and accurate in your responses\n- If multiple documents contain relevant information, synthesize them\n- Acknowledge when information is not available in the knowledge base",
            cache_control: { type: "ephemeral" }
          },
          {
            type: "text",
            text: "# Knowledge Base Context\n\nHere are the relevant documents for this conversation:\n\n## Document 1: Solar System Overview\nThe solar system consists of the Sun and all objects that orbit it...\n\n## Document 2: Planetary Characteristics\nEach planet has unique features. Mercury is the smallest planet...\n\n## Document 3: Mars Exploration\nMars has been a target of exploration for decades...\n\n[Additional documents...]",
            cache_control: { type: "ephemeral" }
          }
        ],
        messages: [
          {
            role: "user",
            content: "Can you search for information about Mars rovers?"
          },
          {
            role: "assistant",
            content: [
              {
                type: "tool_use",
                id: "tool_1",
                name: "search_documents",
                input: { query: "Mars rovers" }
              }
            ]
          },
          {
            role: "user",
            content: [
              {
                type: "tool_result",
                tool_use_id: "tool_1",
                content: "Found 3 relevant documents: Document 3 (Mars Exploration), Document 7 (Rover Technology), Document 9 (Mission History)"
              }
            ]
          },
          {
            role: "assistant",
            content: [
              {
                type: "text",
                text: "I found 3 relevant documents about Mars rovers. Let me get more details from the Mars Exploration document."
              }
            ]
          },
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Yes, please tell me about the Perseverance rover specifically.",
                cache_control: { type: "ephemeral" }
              }
            ]
          }
        ]
      )
      puts message.usage
      ```
    </CodeGroup>

    This comprehensive example demonstrates how to use all 4 available cache breakpoints to optimize different parts of your prompt:

    1. **Tools cache** (cache breakpoint 1): The `cache_control` parameter on the last tool definition caches all tool definitions.

    2. **Reusable instructions cache** (cache breakpoint 2): The static instructions in the system prompt are cached separately. These instructions rarely change between requests.

    3. **RAG context cache** (cache breakpoint 3): The knowledge base documents are cached independently, allowing you to update the RAG documents without invalidating the tools or instructions cache.

    4. **Conversation history cache** (cache breakpoint 4): The final user message is marked with `cache_control` to enable incremental caching of the conversation as it progresses.

    This approach provides maximum flexibility:

    * If you append a new turn to the conversation without changing earlier content, all four cache segments are reused
    * If you update the RAG documents but keep the same tools and instructions, the first two cache segments are reused
    * If you change the conversation but keep the same tools, instructions, and documents, the first three segments are reused
    * Changes at any breakpoint invalidate that segment and everything after it, while earlier cached segments remain valid

    For the first request:

    * `input_tokens`: Minimal (tokens after the final cache breakpoint, near 0 in this example)
    * `cache_creation_input_tokens`: Tokens in all cached segments (tools + instructions + RAG documents + conversation history)
    * `cache_read_input_tokens`: 0 (no cache hits)

    For subsequent requests with only a new user message (and the fourth breakpoint moved to that new final message, as in the example):

    * `input_tokens`: Minimal (tokens after the final cache breakpoint, near 0 in this example)
    * `cache_creation_input_tokens`: Tokens in the new user message and the previous assistant turn (the new conversation segment being cached)
    * `cache_read_input_tokens`: All previously cached tokens (tools + instructions + RAG documents + previous conversation)

    This pattern is especially powerful for:

    * RAG applications with large document contexts
    * Agent systems that use multiple tools
    * Long-running conversations that need to maintain context
    * Applications that need to optimize different parts of the prompt independently
  </Accordion>
</AccordionGroup>


## Data retention

Source: https://platform.claude.com/llms-full.txt#data-retention-8

Prompt caching (both automatic and explicit) is ZDR eligible. Anthropic does not store the raw text of your prompts or Claude's responses.

KV (key-value) cache representations and cryptographic hashes of cached content are held in memory only and are not stored at rest. Cached entries have a minimum lifetime of 5 minutes (standard) or 1 hour (extended), after which they are promptly, though not immediately, deleted. Cache entries are isolated between organizations and, on the Claude API, Claude Platform on AWS, and Microsoft Foundry, between workspaces within an organization.

For ZDR eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).

***


## FAQ

Source: https://platform.claude.com/llms-full.txt#faq-4

<AccordionGroup>
  <Accordion title="Do I need multiple cache breakpoints or is one at the end sufficient?">
    **In most cases, a single cache breakpoint at the end of your static content is sufficient.** Cache writes happen only at the block you mark. Place it on the last block that stays identical across requests, and every subsequent request reads that same entry. If a later block varies per request (a timestamp, the incoming message), keep the breakpoint before it, on the last stable block.

    You only need multiple breakpoints if:

    * A growing conversation pushes your breakpoint 20 or more blocks past the last cache write, putting the prior entry outside the lookback window
    * You want to cache sections that update at different frequencies independently
    * You need explicit control over what gets cached for cost optimization

    Example: If you have system instructions (rarely change) and RAG context (changes daily), you might use two breakpoints to cache them separately.
  </Accordion>

  <Accordion title="Do cache breakpoints add extra cost?">
    No, cache breakpoints themselves are free. You only pay for:

    * Writing content to cache (25% more than base input tokens for 5-minute TTL)
    * Reading from cache (a fraction of the base input token price, see [Pricing](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing))
    * Regular input tokens for uncached content

    The number of breakpoints doesn't affect pricing - only the amount of content cached and read matters.
  </Accordion>

  <Accordion title="How do I calculate total input tokens from the usage fields?">
    The usage response includes three separate input token fields that together represent your total input:

    ```text wrap
    total_input_tokens = cache_read_input_tokens + cache_creation_input_tokens + input_tokens

python Python
      client.beta.prompt_caching.messages.create(**params)

python Python
      client.messages.create(**params)

typescript TypeScript
    client.beta.promptCaching.messages.create(/* ... */);

typescript
    client.messages.create(/* ... */);
    ```
  </Accordion>
</AccordionGroup>


---
title: Token counting
url: https://platform.claude.com/docs/en/build-with-claude/token-counting
description: Count the tokens in a message before you send it to Claude. Use token counts to manage rate limits and costs, make model routing decisions, and fit prompts to a target length.
---


## Compatibility

Source: https://platform.claude.com/llms-full.txt#compatibility-11

- [ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): eligible (excludes [Covered Models](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements))
- Platforms: Claude API, Claude Platform on AWS, Amazon Bedrock, Google Cloud, Microsoft Foundry

Token counting lets you determine the number of tokens in a message before you send it to Claude. This helps you make informed decisions about your prompts and usage. With token counting, you can:

* Proactively manage rate limits and costs
* Make smart model routing decisions
* Optimize prompts to a specific length

***


## How to count message tokens

Source: https://platform.claude.com/llms-full.txt#how-to-count-message-tokens

The [token counting](https://platform.claude.com/docs/en/api/messages-count-tokens) endpoint accepts the same structured list of inputs for creating a message, including support for system prompts, [tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview), [images](https://platform.claude.com/docs/en/build-with-claude/vision), and [PDFs](https://platform.claude.com/docs/en/build-with-claude/pdf-support). The response contains the total number of input tokens.

<Note>
  The token count is an **estimate**. In some cases, the actual number of input tokens used when creating a message might differ by a small amount.

  Token counts may include tokens added automatically by Anthropic for system optimizations. **You are not billed for system-added tokens**. Billing reflects only your content.
</Note>

### Supported models

All [active models](https://platform.claude.com/docs/en/models/overview) support token counting.

<Note>
  Claude 4.7 and later models and Claude Mythos Preview use a newer tokenizer. The same input text produces approximately 30 percent more tokens than on earlier models. The exact increase depends on the content and workload shape. Recount prompts against the model you plan to use rather than reusing counts measured against earlier models.
</Note>

### Count tokens in basic messages

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages/count_tokens \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "content-type: application/json" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "system": "You are a scientist",
      "messages": [{
        "role": "user",
        "content": "Hello, Claude"
      }]
    }'

bash CLI
  ant messages count-tokens \
    --model claude-opus-5 \
    --system "You are a scientist" \
    --message '{role: user, content: "Hello, Claude"}'

python Python
  client = anthropic.Anthropic()

  response = client.messages.count_tokens(
      model="claude-opus-5",
      system="You are a scientist",
      messages=[{"role": "user", "content": "Hello, Claude"}],
  )

  print(response.json())

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.countTokens({
    model: "claude-opus-5",
    system: "You are a scientist",
    messages: [
      {
        role: "user",
        content: "Hello, Claude"
      }
    ]
  });

  console.log(response);

csharp C#
  using System;
  using System.Threading.Tasks;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCountTokensParams
  {
      Model = Model.ClaudeOpus5,
      System = "You are a scientist",
      Messages = [new() { Role = Role.User, Content = "Hello, Claude" }]
  };

  var response = await client.Messages.CountTokens(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.CountTokens(context.TODO(), anthropic.MessageCountTokensParams{
  	Model: anthropic.ModelClaudeOpus5,
  	System: anthropic.MessageCountTokensParamsSystemUnion{
  		OfString: anthropic.String("You are a scientist"),
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, Claude")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(response)

java Java
  import com.anthropic.models.messages.MessageCountTokensParams;
  import com.anthropic.models.messages.MessageTokensCount;
  // ...

  public class CountTokensExample {

    public static void main(String[] args) {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCountTokensParams params = MessageCountTokensParams.builder()
        .model(Model.CLAUDE_OPUS_5)
        .system("You are a scientist")
        .addUserMessage("Hello, Claude")
        .build();

      MessageTokensCount count = client.messages().countTokens(params);
      System.out.println(count);
    }
  }

php PHP
  $client = new Client();

  $response = $client->messages->countTokens(
      messages: [
          ['role' => 'user', 'content' => 'Hello, Claude']
      ],
      model: 'claude-opus-5',
      system: 'You are a scientist',
  );

  echo json_encode($response);

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.count_tokens(
    model: "claude-opus-5",
    system: "You are a scientist",
    messages: [
      { role: "user", content: "Hello, Claude" }
    ]
  )

  puts response

json Output
{ "input_tokens": 14 }

bash cURL
  curl https://api.anthropic.com/v1/messages/count_tokens \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "content-type: application/json" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
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
      "messages": [
        {
          "role": "user",
          "content": "What'\''s the weather like in San Francisco?"
        }
      ]
    }'

bash CLI
  ant messages count-tokens <<'YAML'
  model: claude-opus-5
  tools:
    - name: get_weather
      description: Get the current weather in a given location
      input_schema:
        type: object
        properties:
          location:
            type: string
            description: The city and state, e.g. San Francisco, CA
        required:
          - location
  messages:
    - role: user
      content: What's the weather like in San Francisco?
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.count_tokens(
      model="claude-opus-5",
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
      messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}],
  )

  print(response.json())

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.countTokens({
    model: "claude-opus-5",
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
    messages: [{ role: "user", content: "What's the weather like in San Francisco?" }]
  });

  console.log(response);

csharp C#
  using System;
  using System.Collections.Generic;
  using System.Text.Json;
  using System.Threading.Tasks;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCountTokensParams
  {
      Model = Model.ClaudeOpus5,
      Tools =
      [
          new MessageCountTokensTool(new Tool()
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
      Messages = [new() { Role = Role.User, Content = "What's the weather like in San Francisco?" }]
  };

  var count = await client.Messages.CountTokens(parameters);
  Console.WriteLine(count);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.CountTokens(context.TODO(), anthropic.MessageCountTokensParams{
  	Model: anthropic.ModelClaudeOpus5,
  	Tools: []anthropic.MessageCountTokensToolUnionParam{
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
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather like in San Francisco?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  jsonData, _ := json.MarshalIndent(response, "", "  ")
  fmt.Println(string(jsonData))

java Java
  import com.anthropic.models.messages.MessageCountTokensParams;
  import com.anthropic.models.messages.MessageTokensCount;
  // ...
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      InputSchema schema = InputSchema.builder()
        .properties(
          JsonValue.from(
            Map.of(
              "location",
              Map.of(
                "type",
                "string",
                "description",
                "The city and state, e.g. San Francisco, CA"
              )
            )
          )
        )
        .putAdditionalProperty("required", JsonValue.from(List.of("location")))
        .build();

      MessageCountTokensParams params = MessageCountTokensParams.builder()
        .model(Model.CLAUDE_OPUS_5)
        .addTool(
          Tool.builder()
            .name("get_weather")
            .description("Get the current weather in a given location")
            .inputSchema(schema)
            .build()
        )
        .addUserMessage("What's the weather like in San Francisco?")
        .build();

      MessageTokensCount count = client.messages().countTokens(params);
      System.out.println(count);

php PHP
  $client = new Client();

  $response = $client->messages->countTokens(
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
                      ]
                  ],
                  'required' => ['location']
              ]
          ]
      ],
  );

  echo json_encode($response, JSON_PRETTY_PRINT);

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.count_tokens(
    model: "claude-opus-5",
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
    messages: [
      { role: "user", content: "What's the weather like in San Francisco?" }
    ]
  )

  puts response

json Output
{ "input_tokens": 403 }

bash cURL
  #!/bin/sh

  IMAGE_URL="https://platform.claude.com/docs/images/vision-example.jpg"
  IMAGE_MEDIA_TYPE="image/jpeg"
  IMAGE_BASE64=$(curl -s "$IMAGE_URL" | base64 | tr -d '\n')

  curl https://api.anthropic.com/v1/messages/count_tokens \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "model": "claude-opus-5",
    "messages": [
      {"role": "user", "content": [
        {"type": "image", "source": {
          "type": "base64",
          "media_type": "$IMAGE_MEDIA_TYPE",
          "data": "$IMAGE_BASE64"
        }},
        {"type": "text", "text": "Describe this image"}
      ]}
    ]
  }
  EOF

bash CLI
  IMAGE_URL="https://platform.claude.com/docs/images/vision-example.jpg"
  curl -s "$IMAGE_URL" -o ./vision-example.jpg

  ant messages count-tokens <<'YAML'
  model: claude-opus-5
  messages:
    - role: user
      content:
        - type: image
          source:
            type: base64
            media_type: image/jpeg
            data: "@./vision-example.jpg"
        - type: text
          text: Describe this image
  YAML

python Python
  import base64
  import httpx2

  image_url = "https://platform.claude.com/docs/images/vision-example.jpg"
  image_media_type = "image/jpeg"
  image_data = base64.standard_b64encode(httpx2.get(image_url).content).decode("utf-8")

  client = anthropic.Anthropic()

  response = client.messages.count_tokens(
      model="claude-opus-5",
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "image",
                      "source": {
                          "type": "base64",
                          "media_type": image_media_type,
                          "data": image_data,
                      },
                  },
                  {"type": "text", "text": "Describe this image"},
              ],
          }
      ],
  )
  print(response.json())

typescript TypeScript
  const anthropic = new Anthropic();

  const imageUrl = "https://platform.claude.com/docs/images/vision-example.jpg";
  const imageMediaType = "image/jpeg";
  const imageArrayBuffer = await (await fetch(imageUrl)).arrayBuffer();
  const imageData = Buffer.from(imageArrayBuffer).toString("base64");

  const response = await anthropic.messages.countTokens({
    model: "claude-opus-5",
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: {
              type: "base64",
              media_type: imageMediaType,
              data: imageData
            }
          },
          {
            type: "text",
            text: "Describe this image"
          }
        ]
      }
    ]
  });
  console.log(response);

csharp C#
  using System;
  using System.Collections.Generic;
  using System.Net.Http;
  using System.Threading.Tasks;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  string imageUrl = "https://platform.claude.com/docs/images/vision-example.jpg";

  using HttpClient httpClient = new();
  byte[] imageBytes = await httpClient.GetByteArrayAsync(imageUrl);
  string imageData = Convert.ToBase64String(imageBytes);

  var parameters = new MessageCountTokensParams
  {
      Model = Model.ClaudeOpus5,
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = new MessageParamContent(new List<ContentBlockParam>
              {
                  new ContentBlockParam(new ImageBlockParam(
                      new ImageBlockParamSource(new Base64ImageSource()
                      {
                          Data = imageData,
                          MediaType = MediaType.ImageJpeg,
                      })
                  )),
                  new ContentBlockParam(new TextBlockParam("Describe this image")),
              }),
          }
      ]
  };

  var count = await client.Messages.CountTokens(parameters);
  Console.WriteLine(count);

go Go
  imageURL := "https://platform.claude.com/docs/images/vision-example.jpg"

  req, err := http.NewRequest("GET", imageURL, nil)
  if err != nil {
  	log.Fatal(err)
  }
  req.Header.Set("User-Agent", "AnthropicDocsBot/1.0")

  resp, err := http.DefaultClient.Do(req)
  if err != nil {
  	log.Fatal(err)
  }
  defer resp.Body.Close()

  imageBytes, err := io.ReadAll(resp.Body)
  if err != nil {
  	log.Fatal(err)
  }
  imageData := base64.StdEncoding.EncodeToString(imageBytes)

  client := anthropic.NewClient()

  response, err := client.Messages.CountTokens(context.TODO(), anthropic.MessageCountTokensParams{
  	Model: anthropic.ModelClaudeOpus5,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(
  			anthropic.NewImageBlockBase64("image/jpeg", imageData),
  			anthropic.NewTextBlock("Describe this image"),
  		),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(response)

java Java
  import com.anthropic.models.messages.Base64ImageSource;
  // ...
  import com.anthropic.models.messages.MessageCountTokensParams;
  import com.anthropic.models.messages.MessageTokensCount;
  // ...
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      String imageUrl =
        "https://platform.claude.com/docs/images/vision-example.jpg";
      String imageMediaType = "image/jpeg";

      HttpClient httpClient = HttpClient.newHttpClient();
      HttpRequest request = HttpRequest.newBuilder().uri(URI.create(imageUrl)).build();
      byte[] imageBytes = httpClient
        .send(request, HttpResponse.BodyHandlers.ofByteArray())
        .body();
      String imageBase64 = Base64.getEncoder().encodeToString(imageBytes);

      ContentBlockParam imageBlock = ContentBlockParam.ofImage(
        ImageBlockParam.builder()
          .source(
            Base64ImageSource.builder()
              .mediaType(Base64ImageSource.MediaType.IMAGE_JPEG)
              .data(imageBase64)
              .build()
          )
          .build()
      );

      ContentBlockParam textBlock = ContentBlockParam.ofText(
        TextBlockParam.builder().text("Describe this image").build()
      );

      MessageCountTokensParams params = MessageCountTokensParams.builder()
        .model(Model.CLAUDE_OPUS_5)
        .addUserMessageOfBlockParams(List.of(imageBlock, textBlock))
        .build();

      MessageTokensCount count = client.messages().countTokens(params);
      System.out.println(count);

php PHP
  $imageUrl = "https://platform.claude.com/docs/images/vision-example.jpg";
  $imageMediaType = "image/jpeg";
  $imageData = base64_encode(file_get_contents($imageUrl));

  $client = new Client();

  $response = $client->messages->countTokens(
      messages: [
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'image',
                      'source' => [
                          'type' => 'base64',
                          'media_type' => $imageMediaType,
                          'data' => $imageData
                      ]
                  ],
                  ['type' => 'text', 'text' => 'Describe this image']
              ]
          ]
      ],
      model: 'claude-opus-5',
  );
  print_r($response);

ruby Ruby
  require "base64"
  require "net/http"

  image_url = "https://platform.claude.com/docs/images/vision-example.jpg"
  image_media_type = "image/jpeg"

  uri = URI(image_url)
  image_data = Base64.strict_encode64(Net::HTTP.get(uri))

  client = Anthropic::Client.new

  response = client.messages.count_tokens(
    model: "claude-opus-5",
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: {
              type: "base64",
              media_type: image_media_type,
              data: image_data
            }
          },
          { type: "text", text: "Describe this image" }
        ]
      }
    ]
  )
  puts response

json Output
{ "input_tokens": 1028 }

bash cURL
  curl https://api.anthropic.com/v1/messages/count_tokens \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "content-type: application/json" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "thinking": {
        "type": "adaptive"
      },
      "messages": [
        {
          "role": "user",
          "content": "Are there an infinite number of prime numbers such that n mod 4 == 3?"
        },
        {
          "role": "assistant",
          "content": [
            {
              "type": "thinking",
              "thinking": "This is a nice number theory question. Lets think about it step by step...",
              "signature": "EuYBCkQYAiJAgCs1le6/Pol5Z4/JMomVOouGrWdhYNsH3ukzUECbB6iWrSQtsQuRHJID6lWV..."
            },
            {
              "type": "text",
              "text": "Yes, there are infinitely many prime numbers p such that p mod 4 = 3..."
            }
          ]
        },
        {
          "role": "user",
          "content": "Can you write a formal proof?"
        }
      ]
    }'

bash CLI
  ant messages count-tokens <<'YAML'
  model: claude-opus-5
  thinking:
    type: adaptive
  messages:
    - role: user
      content: Are there an infinite number of prime numbers such that n mod 4 == 3?
    - role: assistant
      content:
        - type: thinking
          thinking: >-
            This is a nice number theory question. Lets think about it step by step...
          signature: >-
            EuYBCkQYAiJAgCs1le6/Pol5Z4/JMomVOouGrWdhYNsH3ukzUECbB6iWrSQtsQuRHJID6lWV...
        - type: text
          text: Yes, there are infinitely many prime numbers p such that p mod 4 = 3...
    - role: user
      content: Can you write a formal proof?
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.count_tokens(
      model="claude-opus-5",
      thinking={"type": "adaptive"},
      messages=[
          {
              "role": "user",
              "content": "Are there an infinite number of prime numbers such that n mod 4 == 3?",
          },
          {
              "role": "assistant",
              "content": [
                  {
                      "type": "thinking",
                      "thinking": "This is a nice number theory question. Let's think about it step by step...",
                      "signature": "EuYBCkQYAiJAgCs1le6/Pol5Z4/JMomVOouGrWdhYNsH3ukzUECbB6iWrSQtsQuRHJID6lWV...",
                  },
                  {
                      "type": "text",
                      "text": "Yes, there are infinitely many prime numbers p such that p mod 4 = 3...",
                  },
              ],
          },
          {"role": "user", "content": "Can you write a formal proof?"},
      ],
  )

  print(response.json())

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.countTokens({
    model: "claude-opus-5",
    thinking: { type: "adaptive" },
    messages: [
      {
        role: "user",
        content: "Are there an infinite number of prime numbers such that n mod 4 == 3?"
      },
      {
        role: "assistant",
        content: [
          {
            type: "thinking",
            thinking:
              "This is a nice number theory question. Let's think about it step by step...",
            signature:
              "EuYBCkQYAiJAgCs1le6/Pol5Z4/JMomVOouGrWdhYNsH3ukzUECbB6iWrSQtsQuRHJID6lWV..."
          },
          {
            type: "text",
            text: "Yes, there are infinitely many prime numbers p such that p mod 4 = 3..."
          }
        ]
      },
      {
        role: "user",
        content: "Can you write a formal proof?"
      }
    ]
  });

  console.log(response);

csharp C#
  using System;
  using System.Threading.Tasks;
  using System.Collections.Generic;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCountTokensParams
  {
      Model = Model.ClaudeOpus5,
      Thinking = new ThinkingConfigAdaptive(),
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = "Are there an infinite number of prime numbers such that n mod 4 == 3?"
          },
          new()
          {
              Role = Role.Assistant,
              Content = new MessageParamContent(new List<ContentBlockParam>
              {
                  new ContentBlockParam(new ThinkingBlockParam()
                  {
                      Thinking = "This is a nice number theory question. Let's think about it step by step...",
                      Signature = "EuYBCkQYAiJAgCs1le6/Pol5Z4/JMomVOouGrWdhYNsH3ukzUECbB6iWrSQtsQuRHJID6lWV...",
                  }),
                  new ContentBlockParam(new TextBlockParam("Yes, there are infinitely many prime numbers p such that p mod 4 = 3...")),
              }),
          },
          new()
          {
              Role = Role.User,
              Content = "Can you write a formal proof?"
          }
      ]
  };

  var response = await client.Messages.CountTokens(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  thinkingBlock := anthropic.NewThinkingBlock(
  	"EuYBCkQYAiJAgCs1le6/Pol5Z4/JMomVOouGrWdhYNsH3ukzUECbB6iWrSQtsQuRHJID6lWV...",
  	"This is a nice number theory question. Let's think about it step by step...",
  )

  textBlock := anthropic.NewTextBlock(
  	"Yes, there are infinitely many prime numbers p such that p mod 4 = 3...",
  )

  response, err := client.Messages.CountTokens(context.TODO(), anthropic.MessageCountTokensParams{
  	Model: anthropic.ModelClaudeOpus5,
  	Thinking: anthropic.ThinkingConfigParamUnion{
  		OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Are there an infinite number of prime numbers such that n mod 4 == 3?")),
  		anthropic.NewAssistantMessage(thinkingBlock, textBlock),
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Can you write a formal proof?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Printf("%+v\n", response)

java Java
  import com.anthropic.models.messages.MessageCountTokensParams;
  import com.anthropic.models.messages.MessageTokensCount;
  // ...
  import com.anthropic.models.messages.ThinkingBlockParam;
  import com.anthropic.models.messages.ThinkingConfigAdaptive;
  // ...
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      List<ContentBlockParam> assistantBlocks = List.of(
        ContentBlockParam.ofThinking(
          ThinkingBlockParam.builder()
            .thinking(
              "This is a nice number theory question. Let's think about it step by step..."
            )
            .signature(
              "EuYBCkQYAiJAgCs1le6/Pol5Z4/JMomVOouGrWdhYNsH3ukzUECbB6iWrSQtsQuRHJID6lWV..."
            )
            .build()
        ),
        ContentBlockParam.ofText(
          TextBlockParam.builder()
            .text("Yes, there are infinitely many prime numbers p such that p mod 4 = 3...")
            .build()
        )
      );

      MessageCountTokensParams params = MessageCountTokensParams.builder()
        .model(Model.CLAUDE_OPUS_5)
        .thinking(ThinkingConfigAdaptive.builder().build())
        .addUserMessage("Are there an infinite number of prime numbers such that n mod 4 == 3?")
        .addAssistantMessageOfBlockParams(assistantBlocks)
        .addUserMessage("Can you write a formal proof?")
        .build();

      MessageTokensCount count = client.messages().countTokens(params);
      System.out.println(count);

php PHP
  $client = new Client();

  $response = $client->messages->countTokens(
      messages: [
          [
              'role' => 'user',
              'content' => 'Are there an infinite number of prime numbers such that n mod 4 == 3?'
          ],
          [
              'role' => 'assistant',
              'content' => [
                  [
                      'type' => 'thinking',
                      'thinking' => 'This is a nice number theory question. Let\'s think about it step by step...',
                      'signature' => 'EuYBCkQYAiJAgCs1le6/Pol5Z4/JMomVOouGrWdhYNsH3ukzUECbB6iWrSQtsQuRHJID6lWV...'
                  ],
                  [
                      'type' => 'text',
                      'text' => 'Yes, there are infinitely many prime numbers p such that p mod 4 = 3...'
                  ]
              ]
          ],
          [
              'role' => 'user',
              'content' => 'Can you write a formal proof?'
          ]
      ],
      model: 'claude-opus-5',
      thinking: ['type' => 'adaptive'],
  );

  echo json_encode($response);

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.count_tokens(
    model: "claude-opus-5",
    thinking: {
      type: "adaptive"
    },
    messages: [
      {
        role: "user",
        content: "Are there an infinite number of prime numbers such that n mod 4 == 3?"
      },
      {
        role: "assistant",
        content: [
          {
            type: "thinking",
            thinking: "This is a nice number theory question. Let's think about it step by step...",
            signature: "EuYBCkQYAiJAgCs1le6/Pol5Z4/JMomVOouGrWdhYNsH3ukzUECbB6iWrSQtsQuRHJID6lWV..."
          },
          {
            type: "text",
            text: "Yes, there are infinitely many prime numbers p such that p mod 4 = 3..."
          }
        ]
      },
      {
        role: "user",
        content: "Can you write a formal proof?"
      }
    ]
  )

  puts response

json Output
{ "input_tokens": 88 }

bash cURL
  curl https://api.anthropic.com/v1/messages/count_tokens \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "content-type: application/json" \
    -H "anthropic-version: 2023-06-01" \
    -d @- <<EOF
  {
    "model": "claude-opus-5",
    "messages": [{
      "role": "user",
      "content": [
        {
          "type": "document",
          "source": {
            "type": "base64",
            "media_type": "application/pdf",
            "data": "$PDF_BASE64"
          }
        },
        {
          "type": "text",
          "text": "Please summarize this document."
        }
      ]
    }]
  }
  EOF

bash CLI
  ant messages count-tokens <<'YAML'
  model: claude-opus-5
  messages:
    - role: user
      content:
        - type: document
          source:
            type: base64
            media_type: application/pdf
            data: "@./document.pdf"
        - type: text
          text: Please summarize this document.
  YAML

python Python
  import base64
  import anthropic

  client = anthropic.Anthropic()

  with open("/path/to/document.pdf", "rb") as pdf_file:
      pdf_base64 = base64.standard_b64encode(pdf_file.read()).decode("utf-8")

  response = client.messages.count_tokens(
      model="claude-opus-5",
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "document",
                      "source": {
                          "type": "base64",
                          "media_type": "application/pdf",
                          "data": pdf_base64,
                      },
                  },
                  {"type": "text", "text": "Please summarize this document."},
              ],
          }
      ],
  )

  print(response.json())

typescript TypeScript
  import { readFile } from "node:fs/promises";

  const client = new Anthropic();

  const pdfBase64 = await readFile("/path/to/document.pdf", { encoding: "base64" });

  const response = await client.messages.countTokens({
    model: "claude-opus-5",
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: {
              type: "base64",
              media_type: "application/pdf",
              data: pdfBase64
            }
          },
          {
            type: "text",
            text: "Please summarize this document."
          }
        ]
      }
    ]
  });

  console.log(response);

csharp C#
  using System;
  using System.IO;
  using System.Threading.Tasks;
  using System.Collections.Generic;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  byte[] pdfBytes = await File.ReadAllBytesAsync("/path/to/document.pdf");
  string pdfBase64 = Convert.ToBase64String(pdfBytes);

  var parameters = new MessageCountTokensParams
  {
      Model = Model.ClaudeOpus5,
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = new MessageParamContent(new List<ContentBlockParam>
              {
                  new ContentBlockParam(new DocumentBlockParam(
                      new DocumentBlockParamSource(new Base64PdfSource()
                      {
                          Data = pdfBase64,
                      })
                  )),
                  new ContentBlockParam(new TextBlockParam("Please summarize this document.")),
              }),
          }
      ]
  };

  var count = await client.Messages.CountTokens(parameters);
  Console.WriteLine(count);

go Go
  client := anthropic.NewClient()

  pdfBytes, err := os.ReadFile("/path/to/document.pdf")
  if err != nil {
  	log.Fatal(err)
  }
  pdfBase64 := base64.StdEncoding.EncodeToString(pdfBytes)

  response, err := client.Messages.CountTokens(context.TODO(), anthropic.MessageCountTokensParams{
  	Model: anthropic.ModelClaudeOpus5,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(
  			anthropic.NewDocumentBlock(anthropic.Base64PDFSourceParam{
  				Data: pdfBase64,
  			}),
  			anthropic.NewTextBlock("Please summarize this document."),
  		),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(response)

java Java
  import com.anthropic.models.messages.Base64PdfSource;
  // ...
  import com.anthropic.models.messages.DocumentBlockParam;
  import com.anthropic.models.messages.MessageCountTokensParams;
  import com.anthropic.models.messages.MessageTokensCount;
  // ...
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      byte[] fileBytes = Files.readAllBytes(Path.of("/path/to/document.pdf"));
      String pdfBase64 = Base64.getEncoder().encodeToString(fileBytes);

      ContentBlockParam documentBlock = ContentBlockParam.ofDocument(
        DocumentBlockParam.builder()
          .source(Base64PdfSource.builder().data(pdfBase64).build())
          .build()
      );

      ContentBlockParam textBlock = ContentBlockParam.ofText(
        TextBlockParam.builder().text("Please summarize this document.").build()
      );

      MessageCountTokensParams params = MessageCountTokensParams.builder()
        .model(Model.CLAUDE_OPUS_5)
        .addUserMessageOfBlockParams(List.of(documentBlock, textBlock))
        .build();

      MessageTokensCount count = client.messages().countTokens(params);
      System.out.println(count);

php PHP
  $client = new Client();

  $pdfBase64 = base64_encode(file_get_contents("/path/to/document.pdf"));

  $response = $client->messages->countTokens(
      messages: [
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'document',
                      'source' => [
                          'type' => 'base64',
                          'media_type' => 'application/pdf',
                          'data' => $pdfBase64
                      ]
                  ],
                  [
                      'type' => 'text',
                      'text' => 'Please summarize this document.'
                  ]
              ]
          ]
      ],
      model: 'claude-opus-5',
  );

  echo json_encode($response);

ruby Ruby
  require "base64"

  client = Anthropic::Client.new

  pdf_base64 = Base64.strict_encode64(File.binread("/path/to/document.pdf"))

  response = client.messages.count_tokens(
    model: "claude-opus-5",
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: {
              type: "base64",
              media_type: "application/pdf",
              data: pdf_base64
            }
          },
          {
            type: "text",
            text: "Please summarize this document."
          }
        ]
      }
    ]
  )

  puts response

json Output
{ "input_tokens": 2188 }
```

***


## Token counts on Claude Fable and Claude Mythos models

Source: https://platform.claude.com/llms-full.txt#token-counts-on-claude-fable-and-claude-mythos-models

Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, and Claude Mythos 5 share the tokenizer introduced with Claude Opus 4.7. A prompt counts the same on all four, and roughly 30 percent higher than on models before Claude Opus 4.7 (the exact increase depends on the content). The token counting endpoint counts under the tokenizer of the `model` you pass. To measure the difference for your workload, count the same request twice, once with your current model and once with the model you plan to move to, and compare the two `input_tokens` values.

<Note>
  **Billing and migration:** Usage and billing on these models reflect this tokenizer's counts. When migrating from a model before Claude Opus 4.7, don't reuse token counts measured on the older model to estimate costs or context window fit. Count your prompts with the `model` ID you plan to use (for example, `"claude-fable-5-1"`).
</Note>

***


## Pricing and rate limits

Source: https://platform.claude.com/llms-full.txt#pricing-and-rate-limits

Token counting is **free to use** but subject to requests per minute rate limits based on your [usage tier](https://platform.claude.com/docs/en/api/rate-limits#rate-limits). If you need higher limits, use **Request rate limit increase** on the [Rate limits](https://platform.claude.com/settings/limits) page.

| Usage tier | Requests per minute (RPM) |
| ---------- | ------------------------- |
| Start      | 5,000                     |
| Build      | 10,000                    |
| Scale      | 20,000                    |

<Note>
  Token counting and message creation have separate and independent rate limits. Usage of one does not count against the limits of the other.
</Note>

***


## FAQ

Source: https://platform.claude.com/llms-full.txt#faq-5

<AccordionGroup>
  <Accordion title="Does token counting use prompt caching?">
    No, token counting provides an estimate without using caching logic. Although you may provide `cache_control` blocks in your token counting request, prompt caching only occurs during actual message creation.
  </Accordion>
</AccordionGroup>

***


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-51

<CardGroup cols={2}>
  <Card title="Count message tokens" icon="code" href="https://platform.claude.com/docs/en/api/messages-count-tokens">
    Read the full API reference for the token counting endpoint.
  </Card>

  <Card title="Context windows" icon="arrows-maximize" href="https://platform.claude.com/docs/en/build-with-claude/context-windows">
    Use token counts to keep prompts within a model's context window.
  </Card>

  <Card title="Rate limits" icon="gauge" href="https://platform.claude.com/docs/en/api/rate-limits">
    Check token counts before you send a request to stay within your usage tier.
  </Card>

  <Card title="Prompt caching" icon="database" href="https://platform.claude.com/docs/en/build-with-claude/prompt-caching">
    Reduce cost and latency on repeated prompts by caching prompt prefixes.
  </Card>
</CardGroup>


### Working with files

---
title: Files API
url: https://platform.claude.com/docs/en/build-with-claude/files
description: Upload files once, reference them by file_id in Messages requests, and download outputs created by skills or the code execution tool.
---


## Compatibility

Source: https://platform.claude.com/llms-full.txt#compatibility-12

- [ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): not eligible
- Platforms: Claude API, Claude Platform on AWS (beta), Microsoft Foundry (beta) [1]; not available on Amazon Bedrock, Google Cloud
1. On [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), the Files API requires a [Hosted on Anthropic deployment](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#additional-features-not-supported-when-hosted-on-azure).

The Files API lets you upload and manage files to use with the Claude API without re-uploading content with each request. This is particularly useful when using the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) to provide inputs (for example, datasets and documents) and then download outputs (for example, charts). You can [explore the API reference directly](https://platform.claude.com/docs/en/api/files/upload), in addition to this guide.


## File type support

Source: https://platform.claude.com/llms-full.txt#file-type-support

Referencing a `file_id` in a Messages request is supported on all models that support the given file type. [Images](https://platform.claude.com/docs/en/build-with-claude/vision) are supported on all current Claude models. For [PDFs](https://platform.claude.com/docs/en/build-with-claude/pdf-support) and [other file types with the code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#compatibility), see the linked pages for model support.


## How the Files API works

Source: https://platform.claude.com/llms-full.txt#how-the-files-api-works

The Files API provides a create-once, use-many-times approach for working with files:

* **Upload files** to Anthropic's secure storage and receive a unique `file_id`
* **Download files** that are created by skills or the code execution tool
* **Reference files** in [Messages](https://platform.claude.com/docs/en/api/messages/create) requests using the `file_id` instead of re-uploading content
* **Manage your files** with list, retrieve, and delete operations

<Warning id="workspace-scoped-access">
  **Uploaded files are accessible to your entire workspace, not scoped to an end user, conversation, or session.** Any API key with access to a workspace can access any files uploaded to that workspace. Every service account, and every user whose organization role allows API access, can use the Default Workspace in addition to any workspace you add them to, so keep files that must stay separate in their own [workspace](https://platform.claude.com/docs/en/manage-claude/workspaces#api-keys-and-resource-scoping) and access them only with keys scoped to that workspace. Never accept `file_id` values from end users or other untrusted sources: a user-supplied file ID would let one user of your application read content that another user uploaded. Treat file IDs as server-side references, and keep the mapping between your users and their files in your application.

  If you are building a multi-tenant application on the Files API, create a separate [workspace](https://platform.claude.com/docs/en/manage-claude/workspaces) for each tenant. The workspace is the isolation boundary for files, so a workspace per tenant gives each tenant's data hard isolation from every other tenant. Each organization can have up to 100 workspaces; contact your account team if you need more.
</Warning>


## How to use the Files API

Source: https://platform.claude.com/llms-full.txt#how-to-use-the-files-api

### Uploading a file

Upload a file to be referenced in future API calls:

<CodeGroup>
  ```bash cURL
  FILE_ID=$(curl -X POST https://api.anthropic.com/v1/files \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -F "file=@/path/to/document.pdf" | jq -r '.id')
  echo "$FILE_ID"

bash CLI
  FILE_ID=$(ant files upload \
    --file /path/to/document.pdf \
    --transform id \
    --raw-output)
  echo "$FILE_ID"

python Python
  uploaded = client.files.upload(
      file=("document.pdf", open("/path/to/document.pdf", "rb"), "application/pdf"),
  )
  file_id = uploaded.id
  print(file_id)

typescript TypeScript
  const uploaded = await client.files.upload({
    file: await toFile(
      fs.createReadStream("/path/to/document.pdf"),
      undefined,
      { type: "application/pdf" },
    ),
  });
  console.log(uploaded.id);

csharp C#
  var uploaded = await client.Files.Upload(
      new FileUploadParams
      {
          File = new BinaryContent
          {
              Stream = File.OpenRead("/path/to/document.pdf"),
              FileName = "document.pdf",
              ContentType = new("application/pdf")
          }
      });

  var fileId = uploaded.ID;
  Console.WriteLine(fileId);

go Go
  f, err := os.Open("/path/to/document.pdf")
  if err != nil {
  	log.Fatal(err)
  }
  defer f.Close()

  response, err := client.Files.Upload(context.Background(),
  	anthropic.FileUploadParams{
  		File: anthropic.File(f, "document.pdf", "application/pdf"),
  	})
  if err != nil {
  	log.Fatal(err)
  }

  fileID := response.ID
  fmt.Println(fileID)

java Java
  FileMetadata file = client.files().upload(
      FileUploadParams.builder()
          .file(MultipartField.<InputStream>builder()
              .value(Files.newInputStream(Path.of("/path/to/document.pdf")))
              .filename("document.pdf")
              .contentType("application/pdf")
              .build())
          .build()
  );

  String fileId = file.id();
  System.out.println(fileId);

php PHP
  $file = $client->files->upload(
      file: FileParam::fromResource(fopen('/path/to/document.pdf', 'rb'), contentType: 'application/pdf'),
  );

  $fileId = $file->id;
  echo $fileId;

ruby Ruby
  file = client.files.upload(
    file: Anthropic::FilePart.new(
      Pathname("/path/to/document.pdf"),
      content_type: "application/pdf"
    )
  )

  file_id = file.id
  puts file_id

json Response
{
  "id": "file_011CNha8iCJcU1wXNR6q4V8w",
  "type": "file",
  "filename": "document.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 1024000,
  "created_at": "2025-01-01T00:00:00Z",
  "downloadable": false,
  "expires_at": null
}

bash cURL
  curl -X POST https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Please summarize this document for me."
          },
          {
            "type": "document",
            "source": {
              "type": "file",
              "file_id": "$FILE_ID"
            }
          }
        ]
      }
    ]
  }
  EOF

bash CLI
  ant messages create <<YAML
  model: claude-opus-5
  max_tokens: 1024
  messages:
    - role: user
      content:
        - type: text
          text: Please summarize this document for me.
        - type: document
          source:
            type: file
            file_id: $FILE_ID
  YAML

python Python
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  {"type": "text", "text": "Please summarize this document for me."},
                  {
                      "type": "document",
                      "source": {
                          "type": "file",
                          "file_id": file_id,
                      },
                  },
              ],
          }
      ],
  )
  print(response)

typescript TypeScript
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "text",
            text: "Please summarize this document for me.",
          },
          {
            type: "document",
            source: {
              type: "file",
              file_id: uploaded.id,
            },
          },
        ],
      },
    ],
  });

  console.log(response);

csharp C#
  var response = await client.Messages.Create(
      new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages =
          [
              new MessageParam
              {
                  Role = Role.User,
                  Content = new List<ContentBlockParam>
                  {
                      new TextBlockParam { Text = "Please summarize this document for me." },
                      new DocumentBlockParam
                      {
                          Source = new FileDocumentSource { FileID = fileId }
                      }
                  }
              }
          ]
      });

  Console.WriteLine(response);

go Go
  msg, err := client.Messages.New(context.Background(),
  	anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 1024,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(
  				anthropic.NewTextBlock("Please summarize this document for me."),
  				anthropic.NewDocumentBlock(anthropic.FileDocumentSourceParam{
  					FileID: fileID,
  				}),
  			),
  		},
  	})
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(msg)

java Java
  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024)
      .addUserMessageOfBlockParams(List.of(
          ContentBlockParam.ofText(TextBlockParam.builder()
              .text("Please summarize this document for me.")
              .build()),
          ContentBlockParam.ofDocument(DocumentBlockParam.builder()
              .fileSource(fileId)
              .build())
      ))
      .build();

  Message message = client.messages().create(params);
  System.out.println(message);

php PHP
  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  ['type' => 'text', 'text' => 'Please summarize this document for me.'],
                  [
                      'type' => 'document',
                      'source' => [
                          'type' => 'file',
                          'fileID' => $fileId,
                      ],
                  ],
              ],
          ],
      ],
      model: 'claude-opus-5',
  );

  echo $response;

ruby Ruby
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: "Please summarize this document for me." },
          {
            type: "document",
            source: {
              type: "file",
              file_id: file_id
            }
          }
        ]
      }
    ]
  )

  puts response

json
{
  "type": "document",
  "source": {
    "type": "file",
    "file_id": "file_011CNha8iCJcU1wXNR6q4V8w"
  },
  "title": "Document Title", // Optional
  "context": "Context about the document", // Optional
  "citations": { "enabled": true } // Optional, enables citations
}

json
{
  "type": "image",
  "source": {
    "type": "file",
    "file_id": "file_011CPMxVD3fHLUhvTqtsQA5w"
  }
}

json
{
  "type": "container_upload",
  "file_id": "file_011CNha8iCJcU1wXNR6q4V8w"
}

bash cURL
  # Read the text file
  # Note: For files with special characters, consider base64 encoding
  TEXT_CONTENT=$(cat document.txt)

  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d @- <<EOF
  {
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Here's the document content:\n\n${TEXT_CONTENT}\n\nPlease summarize this document."
          }
        ]
      }
    ]
  }
  EOF

bash CLI
  # The "@./path" reference inlines the file contents directly into the field.
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --transform 'content.#(type=="text").text' \
    --raw-output <<'YAML'
  messages:
    - role: user
      content:
        - type: text
          text: "Here's the document content:"
        - type: text
          text: "@./document.txt"
        - type: text
          text: "Please summarize this document."
  YAML

python Python
  client = anthropic.Anthropic()

  # Read the text file
  with open("document.txt") as f:
      text_content = f.read()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "text",
                      "text": f"Here's the document content:\n\n{text_content}\n\nPlease summarize this document.",
                  }
              ],
          }
      ],
  )

  for block in response.content:
      if block.type == "text":
          print(block.text)

typescript TypeScript
  import fs from "node:fs/promises";
  // ...
  const client = new Anthropic();

  // Read the text file
  const textContent = await fs.readFile("document.txt", "utf-8");

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "text",
            text: `Here's the document content:\n\n${textContent}\n\nPlease summarize this document.`
          }
        ]
      }
    ]
  });

  const textBlock = response.content.find(
    (block): block is Anthropic.TextBlock => block.type === "text"
  );
  console.log(textBlock?.text);

csharp C#
  AnthropicClient client = new();

  // Read the text file
  string textContent = await File.ReadAllTextAsync("document.txt");

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new()
      {
          Role = Role.User,
          Content = $"Here's the document content:\n\n{textContent}\n\nPlease summarize this document."
      }]
  };

  var message = await client.Messages.Create(parameters);
  foreach (var block in message.Content)
  {
      if (block.TryPickText(out var textBlock))
      {
          Console.WriteLine(textBlock.Text);
      }
  }

go Go
  client := anthropic.NewClient()

  // Read the text file
  textContent, err := os.ReadFile("document.txt")
  if err != nil {
  	log.Fatal(err)
  }

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock(
  			fmt.Sprintf("Here's the document content:\n\n%s\n\nPlease summarize this document.", string(textContent)),
  		)),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  for _, block := range response.Content {
  	if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  		fmt.Println(textBlock.Text)
  	}
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  // Read the text file
  String textContent = Files.readString(Path.of("document.txt"));

  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024L)
      .addUserMessage("Here's the document content:\n\n" + textContent + "\n\nPlease summarize this document.")
      .build();

  Message response = client.messages().create(params);
  response.content().stream()
      .flatMap(block -> block.text().stream())
      .forEach(textBlock -> System.out.println(textBlock.text()));

php PHP
  $client = new Client();

  // Read the text file
  $textContent = file_get_contents("document.txt");

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'text',
                      'text' => "Here's the document content:\n\n{$textContent}\n\nPlease summarize this document."
                  ]
              ]
          ]
      ],
      model: 'claude-opus-5',
  );

  foreach ($message->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, PHP_EOL;
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  # Read the text file
  text_content = File.read("document.txt")

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "text",
            text: "Here's the document content:\n\n#{text_content}\n\nPlease summarize this document."
          }
        ]
      }
    ]
  )

  message.content.each do |block|
    puts block.text if block.type == :text
  end

bash cURL
  curl https://api.anthropic.com/v1/files \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"

bash CLI
  ant files list --max-items 10

python Python
  client = anthropic.Anthropic()
  files = client.files.list()
  print(files)

typescript TypeScript
  const client = new Anthropic();
  const files = await client.files.list();
  console.log(files);

csharp C#
  AnthropicClient client = new();

  var files = await client.Files.List();
  Console.WriteLine(files);

go Go
  client := anthropic.NewClient()

  files, err := client.Files.List(context.TODO(), anthropic.FileListParams{})
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(files)

java Java
  import com.anthropic.models.files.FileListPage;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      FileListPage files = client.files().list();
      System.out.println(files);
  }

php PHP
  $client = new Client();

  $files = $client->files->list();
  echo $files;

ruby Ruby
  client = Anthropic::Client.new

  files = client.files.list
  puts files

bash cURL
  curl "https://api.anthropic.com/v1/files/$FILE_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"

bash CLI
  ant files retrieve-metadata \
    --file-id "$FILE_ID"

python Python
  file = client.files.retrieve_metadata(file_id)
  print(file)

typescript TypeScript
  const file = await client.files.retrieveMetadata(uploaded.id);
  console.log(file);

csharp C#
  var file = await client.Files.RetrieveMetadata(fileId);
  Console.WriteLine(file);

go Go
  metadata, err := client.Files.GetMetadata(context.TODO(), fileID)
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(metadata)

java Java
  FileMetadata metadata = client.files().retrieveMetadata(fileId);

  System.out.println(metadata);

php PHP
  $file = $client->files->retrieveMetadata($fileId);
  echo $file;

ruby Ruby
  file = client.files.retrieve_metadata(file_id)
  puts file

bash cURL
  curl -X DELETE "https://api.anthropic.com/v1/files/$FILE_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"

bash CLI
  ant files delete \
    --file-id "$FILE_ID"

python Python
  client.files.delete(file_id)

typescript TypeScript
  await client.files.delete(uploaded.id);

csharp C#
  await client.Files.Delete(fileId);

go Go
  _, err = client.Files.Delete(context.TODO(), fileID)
  if err != nil {
  	log.Fatal(err)
  }

java Java
  client.files().delete(fileId);

php PHP
  $client->files->delete($fileId);

ruby Ruby
  client.files.delete(file_id)

bash cURL
  curl -X GET "https://api.anthropic.com/v1/files/$FILE_ID/content" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    --output downloaded_file.txt

bash CLI
  ant files download \
    --file-id "$FILE_ID" \
    --output downloaded_file.txt

python Python
  file_content = client.files.download(file_id)

  file_content.write_to_file("downloaded_file.txt")

typescript TypeScript
  const content = await client.files.download(uploaded.id);

  const bytes = Buffer.from(await content.arrayBuffer());
  await fsp.writeFile("downloaded_file.txt", bytes);

csharp C#
  using var fileContent = await client.Files.Download(fileId);
  await using var source = await fileContent.ReadAsStream();
  await using var destination = File.Create("downloaded_file.txt");
  await source.CopyToAsync(destination);

go Go
  func downloadFile(client anthropic.Client, fileID string) error {
  	resp, err := client.Files.Download(context.TODO(), fileID)
  	if err != nil {
  		return err
  	}
  	defer resp.Body.Close()

  	out, err := os.Create("downloaded_file.txt")
  	if err != nil {
  		return err
  	}
  	defer out.Close()

  	_, err = io.Copy(out, resp.Body)
  	return err
  }

java Java
  try (HttpResponse response = client.files().download(fileId)) {
      try (InputStream body = response.body()) {
          Files.copy(body, Path.of("downloaded_file.txt"),
              StandardCopyOption.REPLACE_EXISTING);
      }
  }

php PHP
  $fileContent = $client->files->download($fileId);

  file_put_contents('downloaded_file.txt', $fileContent);

ruby Ruby
  file_content = client.files.download(file_id)

  File.binwrite("downloaded_file.txt", file_content.read)
  ```
</CodeGroup>

<Note>
  A file is downloadable only when its metadata shows `"downloadable": true`, which is the case for files created by skills or the code execution tool. Downloading a file you uploaded returns a 400 error.
</Note>

On the Claude API, supported image, video, and audio files that Claude produces with the code execution tool, including files created by skills, carry signed C2PA Content Credentials when you download them. See [Content Credentials on generated files](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#content-credentials-on-generated-files) for what the credential contains and how to verify it.


## File storage and limits

Source: https://platform.claude.com/llms-full.txt#file-storage-and-limits

### Storage limits

* **Maximum file size:** 500 MB per file
* **Total storage:** 1 TB per organization

### File lifecycle

* Files are scoped to the workspace they were uploaded in. Any request in the same workspace can reference them; never accept file IDs from untrusted sources (see the [workspace access warning](https://platform.claude.com/docs/en/build-with-claude/files#workspace-scoped-access))
* Files cannot be modified or renamed after upload. To change a file's content, upload a new file and delete the old one
* Files persist until you delete them with the `DELETE /v1/files/{file_id}` endpoint or they reach their `expires_at`
* Deleted files cannot be recovered
* Files are inaccessible through the API shortly after deletion, but they may persist in active Messages API calls and associated tool uses
* Files that users delete will be deleted in accordance with Anthropic's [data retention policy](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data). For ZDR eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)

### File expiration

To have a file expire automatically, include an `expires_in_seconds` form field when you upload it. The value is an integer number of seconds between 3,600 (1 hour) and 7,776,000 (90 days). The resulting `expires_at` timestamp (RFC 3339) appears on every file response and is `null` for files uploaded without an expiration. Expiration is set once at upload and cannot be changed.

When a file reaches its `expires_at`:

* Downloading its content (`GET /v1/files/{file_id}/content`) returns a 404 error
* A Messages request that references the file fails before inference
* Its metadata (`GET /v1/files/{file_id}`) remains readable for up to 30 days, with `expires_at` in the past
* It continues to appear in list responses during that window; compare `expires_at` to the current time to filter expired files

Deleting an expired file with `DELETE /v1/files/{file_id}` removes its metadata immediately instead of waiting for the 30-day window to elapse.

<Note>
  Expiration is a lifecycle feature, not a guaranteed-deletion control. After `expires_at`, file content is no longer retrievable through the API and is released from your storage quota; the underlying content may be retained for a limited period thereafter for safety review before permanent deletion, and file metadata remains visible for up to 30 days after expiration. To remove a file before its scheduled expiration, use `DELETE /v1/files/{file_id}`.
</Note>

### Audit logging

If your organization has the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) enabled, its [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) records Files API operations made with a Claude API key or from the Claude Console: each upload (`POST /v1/files`), content download (`GET /v1/files/{file_id}/content`), and deletion (`DELETE /v1/files/{file_id}`) appears as a `platform_file_uploaded`, `platform_file_content_downloaded`, or `platform_file_deleted` activity. Listing files and retrieving file metadata are not recorded. Operations that occur while the Compliance API is off are not recorded and cannot be recovered later, so [set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access) before you rely on this audit trail. On [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#monitoring-and-logging), audit file operations with AWS CloudTrail data events instead.


## Error handling

Source: https://platform.claude.com/llms-full.txt#error-handling-4

Common errors when using the Files API include:

* **File not found (404):** The specified `file_id` doesn't exist or you don't have access to it
* **Invalid file type (400):** The file type doesn't match the content block type (for example, using an image file in a document block)
* **Not downloadable (400):** Files you upload have `"downloadable": false` and cannot be downloaded. Only files created by skills or the code execution tool can be downloaded
* **Exceeds context window size (400):** The file is larger than the context window size (for example, using a 500 MB plain text file in a `/v1/messages` request)
* **Invalid filename (400):** The file name doesn't meet the length requirements (1-255 characters) or contains forbidden characters (`<`, `>`, `:`, `"`, `|`, `?`, `*`, `\`, `/`, or Unicode characters 0-31)
* **File too large (413):** File exceeds the 500 MB limit
* **Storage limit exceeded (400):** Your organization has reached the 1 TB storage limit

```json Output
{
  "type": "error",
  "error": {
    "type": "not_found_error",
    "message": "File `file_011CNha8iCJcU1wXNR6q4V8w` not found."
  },
  "request_id": "req_011CQFYcrRp7mCHLDsAYT8Qt"
}
```


## Usage and billing

Source: https://platform.claude.com/llms-full.txt#usage-and-billing-2

Files API operations are free:

* Uploading files
* Downloading files
* Listing files
* Getting file metadata
* Deleting files

File content used in Messages requests is priced as input tokens.

### Rate limits

File-related API calls are limited to approximately 500 requests per minute. To request a higher limit, [contact sales](mailto:sales@anthropic.com).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-52

<CardGroup cols={3}>
  <Card title="PDF support" icon="file" href="https://platform.claude.com/docs/en/build-with-claude/pdf-support">
    Process PDFs with Claude. Extract text, analyze charts, and understand visual content from your documents.
  </Card>

  <Card title="Code execution tool" icon="terminal" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool">
    Run Python and bash code in a sandboxed container to analyze data, generate files, and iterate on solutions.
  </Card>

  <Card title="Vision" icon="image" href="https://platform.claude.com/docs/en/build-with-claude/vision">
    Process and analyze visual input and generate text and code from images.
  </Card>
</CardGroup>


---
title: PDF support
url: https://platform.claude.com/docs/en/build-with-claude/pdf-support
description: "Process PDFs with Claude: extract text, analyze charts, and understand visual content from your documents."
---


## Compatibility

Source: https://platform.claude.com/llms-full.txt#compatibility-13

- [ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): eligible (excludes [Covered Models](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements))
- Platforms: Claude API, Claude Platform on AWS, Amazon Bedrock, Google Cloud, Microsoft Foundry

You can ask Claude about any text, pictures, charts, and tables in PDFs you provide. Some sample use cases:

* Analyzing financial reports and understanding charts/tables
* Extracting key information from legal documents
* Assisting with document translation
* Converting document information into structured formats


## Before you begin

Source: https://platform.claude.com/llms-full.txt#before-you-begin

### Check PDF requirements

Claude works with any standard PDF. Ensure your request size meets these requirements:

| Requirement               | Limit                                                                                              |
| ------------------------- | -------------------------------------------------------------------------------------------------- |
| Maximum request size      | 32 MB ([varies by platform](https://platform.claude.com/docs/en/api/overview#request-size-limits)) |
| Maximum pages per request | 600 (100 when the request's context window is under 1M tokens)                                     |
| Format                    | Standard PDF (no passwords/encryption)                                                             |

Both limits are on the entire request payload, including any other content sent alongside PDFs. For large PDFs, consider uploading with the [Files API](https://platform.claude.com/docs/en/build-with-claude/files) and referencing by `file_id` to keep request payloads small.

<Tip>
  Dense PDFs (many small-font pages, complex tables, or heavy graphics) can fill the context window before reaching the page limit. Requests with large PDFs can also fail before reaching the page limit, even when using the Files API. Try splitting the document into sections; for large files, because each page is processed as an image, downsampling embedded images can also help.
</Tip>

Because PDF support relies on Claude's vision capabilities, it is subject to the same [limitations and considerations](https://platform.claude.com/docs/en/build-with-claude/vision#limitations) as other vision tasks.

### Supported platforms and models

All [active models](https://platform.claude.com/docs/en/models/overview) support PDF processing. For PDF support through Amazon Bedrock's Converse API, see [Amazon Bedrock PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support#amazon-bedrock-pdf-support).

### Amazon Bedrock PDF support

When using PDF support through the Converse API, part of [Claude on Amazon Bedrock (Opus 4.6 and earlier)](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy), there are two distinct document processing modes:

<Note>
  **Important:** To access Claude's full visual PDF understanding capabilities in the Converse API, you must enable citations. Without citations enabled, the API falls back to basic text extraction only. Learn more about [working with citations](https://platform.claude.com/docs/en/build-with-claude/citations).
</Note>

#### Document processing modes

1. **Converse Document Chat** (Original mode - Text extraction only)

   * Provides basic text extraction from PDFs
   * Cannot analyze images, charts, or visual layouts within PDFs
   * Uses approximately 1,000 tokens for a 3-page PDF
   * Automatically used when citations are not enabled

2. **Claude PDF Chat** (New mode - Full visual understanding)

   * Provides complete visual analysis of PDFs
   * Can understand and analyze charts, graphs, images, and visual layouts
   * Processes each page as both text and image for comprehensive understanding
   * Uses approximately 7,000 tokens for a 3-page PDF
   * **Requires citations to be enabled** in the Converse API

#### Key limitations

* **Converse API:** Visual PDF analysis requires citations to be enabled. There is currently no option to use visual analysis without citations (unlike the InvokeModel API).
* **InvokeModel API:** Provides full control over PDF processing without forced citations.

#### Common issues

If Claude isn't seeing images or charts in your PDFs when using the Converse API, you likely need to enable the citations flag. Without it, Converse falls back to basic text extraction only.

<Note>
  This is a known constraint with the Converse API. For applications that require visual PDF analysis without citations, consider using the InvokeModel API instead.
</Note>

<Note>
  Plain text files such as .txt, .csv, or .md can be used directly in document blocks: upload them to the Files API with MIME type `text/plain` and reference them by `file_id`. Binary formats such as .xlsx or .docx are not supported in document blocks and must be converted to text or PDF first. See [Working with other file formats](https://platform.claude.com/docs/en/build-with-claude/files#working-with-other-file-formats).
</Note>


## Process PDFs with Claude

Source: https://platform.claude.com/llms-full.txt#process-pdfs-with-claude

### Send your first PDF request

Start with a simple example using the Messages API. You can provide PDFs to Claude in three ways:

1. As a URL reference to a PDF hosted online
2. As a base64-encoded PDF in `document` content blocks
3. By a `file_id` from the [Files API](https://platform.claude.com/docs/en/build-with-claude/files)

<Note>
  On Amazon Bedrock and Google Cloud, only base64-encoded sources are currently available. On Microsoft Foundry, the Files API is not supported for deployments hosted on Azure.
</Note>

#### Option 1: URL-based PDF document

The simplest approach is to reference a PDF directly from a URL:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{
          "role": "user",
          "content": [{
              "type": "document",
              "source": {
                  "type": "url",
                  "url": "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
              }
          },
          {
              "type": "text",
              "text": "What are the key findings in this document?"
          }]
      }]
  }'

bash CLI
  ant messages create --transform content --format yaml <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  messages:
    - role: user
      content:
        - type: document
          source:
            type: url
            url: https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf
        - type: text
          text: What are the key findings in this document?
  YAML

python Python
  client = anthropic.Anthropic()
  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "document",
                      "source": {
                          "type": "url",
                          "url": "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf",
                      },
                  },
                  {"type": "text", "text": "What are the key findings in this document?"},
              ],
          }
      ],
  )

  print(message.content)

typescript TypeScript
  const anthropic = new Anthropic();

  const response = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: {
              type: "url",
              url: "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
            }
          },
          {
            type: "text",
            text: "What are the key findings in this document?"
          }
        ]
      }
    ]
  });

  console.log(response);

csharp C#
  var client = new AnthropicClient();

  // Create document block with URL
  var documentParam = new DocumentBlockParam
  {
      Source = new UrlPdfSource
      {
          Url = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf",
      },
  };

  // Create a message with document and text content blocks
  var message = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = new List<ContentBlockParam>
              {
                  documentParam,
                  new TextBlockParam("What are the key findings in this document?"),
              },
          },
      ],
  });

  Console.WriteLine(string.Join("\n", message.Content));

go Go
  client := anthropic.NewClient()

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(
  			anthropic.NewDocumentBlock(anthropic.URLPDFSourceParam{
  				URL: "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf",
  			}),
  			anthropic.NewTextBlock("What are the key findings in this document?"),
  		),
  	},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Printf("%+v\n", message.Content)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  // Create document block with URL
  DocumentBlockParam documentParam = DocumentBlockParam.builder()
    .source(
      UrlPdfSource.builder()
        .url(
          "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
        )
        .build()
    )
    .build();

  // Create a message with document and text content blocks
  MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_5)
    .maxTokens(1024)
    .addUserMessageOfBlockParams(
      List.of(
        ContentBlockParam.ofDocument(documentParam),
        ContentBlockParam.ofText(
          TextBlockParam.builder()
            .text("What are the key findings in this document?")
            .build()
        )
      )
    )
    .build();

  Message message = client.messages().create(params);
  System.out.println(message.content());

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'document',
                      'source' => [
                          'type' => 'url',
                          'url' => 'https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf',
                      ],
                  ],
                  [
                      'type' => 'text',
                      'text' => 'What are the key findings in this document?',
                  ],
              ],
          ],
      ],
      model: 'claude-opus-5',
  );

  echo $message;

ruby Ruby
  anthropic = Anthropic::Client.new

  message = anthropic.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: {
              type: "url",
              url: "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
            }
          },
          {type: "text", text: "What are the key findings in this document?"}
        ]
      }
    ]
  )

  puts(message.content)

json Output
{
  "id": "msg_01Hfp8YuFjQ55VgWbpdHDehB",
  "type": "message",
  "role": "assistant",
  "model": "claude-opus-5",
  "content": [
    {
      "type": "text",
      "text": "This document is an addendum to the Claude 3 model card, reporting updated evaluation results. The key findings include..."
    }
  ],
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 45000,
    "output_tokens": 300
  }
}

bash cURL
  # Method 1: Fetch and encode a remote PDF
  curl -sL "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf" | base64 | tr -d '\n' > pdf_base64.txt

  # Method 2: Encode a local PDF file
  # base64 document.pdf | tr -d '\n' > pdf_base64.txt

  # Create a JSON request file using the pdf_base64.txt content
  jq -n --rawfile PDF_BASE64 pdf_base64.txt '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{
          "role": "user",
          "content": [{
              "type": "document",
              "source": {
                  "type": "base64",
                  "media_type": "application/pdf",
                  "data": $PDF_BASE64
              }
          },
          {
              "type": "text",
              "text": "What are the key findings in this document?"
          }]
      }]
  }' > request.json

  # Send the API request using the JSON file
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d @request.json

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --transform content \
    --format yaml <<'YAML'
  messages:
    - role: user
      content:
        - type: document
          source:
            type: base64
            media_type: application/pdf
            data: "@./document.pdf"
        - type: text
          text: What are the key findings in this document?
  YAML

python Python
  import base64
  import httpx2

  # First, load and encode the PDF
  pdf_url = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
  pdf_data = base64.standard_b64encode(
      httpx2.get(pdf_url, follow_redirects=True).content
  ).decode("utf-8")

  # Alternative: Load from a local file
  # with open("document.pdf", "rb") as f:
  #     pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

  # Send to Claude using base64 encoding
  client = anthropic.Anthropic()
  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "document",
                      "source": {
                          "type": "base64",
                          "media_type": "application/pdf",
                          "data": pdf_data,
                      },
                  },
                  {"type": "text", "text": "What are the key findings in this document?"},
              ],
          }
      ],
  )

  print(message.content)

typescript TypeScript
  // Method 1: Fetch and encode a remote PDF
  const pdfURL =
    "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf";
  const pdfResponse = await fetch(pdfURL);
  const arrayBuffer = await pdfResponse.arrayBuffer();
  const pdfBase64 = Buffer.from(arrayBuffer).toString("base64");

  // Method 2: Load from a local file
  // import { readFile } from "node:fs/promises";
  // const pdfBase64 = (await readFile('document.pdf')).toString('base64');

  // Send the API request with base64-encoded PDF
  const anthropic = new Anthropic();
  const response = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: {
              type: "base64",
              media_type: "application/pdf",
              data: pdfBase64
            }
          },
          {
            type: "text",
            text: "What are the key findings in this document?"
          }
        ]
      }
    ]
  });

  console.log(response);

csharp C#
  var client = new AnthropicClient();

  // Method 1: Download and encode a remote PDF
  var pdfUrl = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf";
  using var httpClient = new HttpClient();
  var pdfBase64 = Convert.ToBase64String(await httpClient.GetByteArrayAsync(pdfUrl));

  // Method 2: Load from a local file
  // var pdfBase64 = Convert.ToBase64String(await File.ReadAllBytesAsync("document.pdf"));

  // Create document block with base64 data
  var documentParam = new DocumentBlockParam
  {
      Source = new Base64PdfSource { Data = pdfBase64 },
  };

  // Create a message with document and text content blocks
  var message = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = new List<ContentBlockParam>
              {
                  documentParam,
                  new TextBlockParam("What are the key findings in this document?"),
              },
          },
      ],
  });

  Console.WriteLine(string.Join("\n", message.Content));

go Go
  // First, load and encode the PDF
  pdfURL := "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
  resp, err := http.Get(pdfURL)
  if err != nil {
  	panic(err)
  }
  defer resp.Body.Close()
  pdfBytes, err := io.ReadAll(resp.Body)
  if err != nil {
  	panic(err)
  }
  pdfBase64 := base64.StdEncoding.EncodeToString(pdfBytes)

  // Alternative: Load from a local file (add "os" to the imports)
  // pdfBytes, err := os.ReadFile("document.pdf")
  // pdfBase64 := base64.StdEncoding.EncodeToString(pdfBytes)

  // Send to Claude using base64 encoding
  client := anthropic.NewClient()
  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(
  			anthropic.NewDocumentBlock(anthropic.Base64PDFSourceParam{
  				Data: pdfBase64,
  			}),
  			anthropic.NewTextBlock("What are the key findings in this document?"),
  		),
  	},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Printf("%+v\n", message.Content)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  // Method 1: Download and encode a remote PDF
  String pdfUrl =
    "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf";
  HttpClient httpClient = HttpClient.newBuilder().followRedirects(HttpClient.Redirect.NORMAL).build();
  HttpRequest request = HttpRequest.newBuilder().uri(URI.create(pdfUrl)).GET().build();

  HttpResponse<byte[]> response = httpClient.send(
    request,
    HttpResponse.BodyHandlers.ofByteArray()
  );
  String pdfBase64 = Base64.getEncoder().encodeToString(response.body());

  // Method 2: Load from a local file
  // byte[] fileBytes = Files.readAllBytes(Path.of("document.pdf"));
  // String pdfBase64 = Base64.getEncoder().encodeToString(fileBytes);

  // Create document block with base64 data
  DocumentBlockParam documentParam = DocumentBlockParam.builder()
    .source(Base64PdfSource.builder().data(pdfBase64).build())
    .build();

  // Create a message with document and text content blocks
  MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_5)
    .maxTokens(1024)
    .addUserMessageOfBlockParams(
      List.of(
        ContentBlockParam.ofDocument(documentParam),
        ContentBlockParam.ofText(
          TextBlockParam.builder()
            .text("What are the key findings in this document?")
            .build()
        )
      )
    )
    .build();

  Message message = client.messages().create(params);
  System.out.println(message.content());

php PHP
  $client = new Client();

  // First, load and encode the PDF
  $pdf_url = 'https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf';
  $pdf_data = base64_encode(file_get_contents($pdf_url));

  // Alternative: Load from a local file
  // $pdf_data = base64_encode(file_get_contents('document.pdf'));

  // Send to Claude using base64 encoding
  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'document',
                      'source' => [
                          'type' => 'base64',
                          'media_type' => 'application/pdf',
                          'data' => $pdf_data,
                      ],
                  ],
                  [
                      'type' => 'text',
                      'text' => 'What are the key findings in this document?',
                  ],
              ],
          ],
      ],
      model: 'claude-opus-5',
  );

  echo $message;

ruby Ruby
  require "open-uri"

  # First, load and encode the PDF
  pdf_url = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
  pdf_bytes = URI.open(pdf_url, "rb") { |f| f.read }
  pdf_data = [pdf_bytes].pack("m0") # Base64-encode without newlines

  # Alternative: Load from a local file
  # pdf_data = [File.binread("document.pdf")].pack("m0")

  # Send to Claude using base64 encoding
  anthropic = Anthropic::Client.new
  message = anthropic.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: {
              type: "base64",
              media_type: "application/pdf",
              data: pdf_data
            }
          },
          {type: "text", text: "What are the key findings in this document?"}
        ]
      }
    ]
  )

  puts(message.content)

bash cURL
  # First, upload your PDF to the Files API
  FILE_ID=$(curl -sS -X POST https://api.anthropic.com/v1/files \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -F "file=@document.pdf" | jq -r '.id')

  # Then use the returned file_id in your message
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d @- <<EOF
  {
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "messages": [{
      "role": "user",
      "content": [{
        "type": "document",
        "source": {
          "type": "file",
          "file_id": "$FILE_ID"
        }
      },
      {
        "type": "text",
        "text": "What are the key findings in this document?"
      }]
    }]
  }
  EOF

bash CLI
  # First, upload your PDF to the Files API
  FILE_ID=$(ant files upload \
    --file ./document.pdf \
    --transform id \
    --raw-output)

  # Then use the returned file_id in your message
  ant messages create \
    --transform content \
    --format yaml <<YAML
  model: claude-opus-5
  max_tokens: 1024
  messages:
    - role: user
      content:
        - type: document
          source:
            type: file
            file_id: $FILE_ID
        - type: text
          text: What are the key findings in this document?
  YAML

python Python
  client = anthropic.Anthropic()

  # Upload the PDF file
  with open("/path/to/document.pdf", "rb") as f:
      file_upload = client.files.upload(file=("document.pdf", f, "application/pdf"))

  # Use the uploaded file in a message
  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "document",
                      "source": {"type": "file", "file_id": file_upload.id},
                  },
                  {"type": "text", "text": "What are the key findings in this document?"},
              ],
          }
      ],
  )

  print(message.content)

typescript TypeScript
  import Anthropic, { toFile } from "@anthropic-ai/sdk";
  import fs from "node:fs";

  const anthropic = new Anthropic();

  // Upload the PDF file
  const fileUpload = await anthropic.files.upload({
    file: await toFile(fs.createReadStream("/path/to/document.pdf"), undefined, {
      type: "application/pdf"
    })
  });

  // Use the uploaded file in a message
  const response = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: {
              type: "file",
              file_id: fileUpload.id
            }
          },
          {
            type: "text",
            text: "What are the key findings in this document?"
          }
        ]
      }
    ]
  });

  console.log(response);

csharp C#
  var client = new AnthropicClient();

  // Upload the PDF file
  var fileUpload = await client.Files.Upload(new FileUploadParams
  {
      File = new BinaryContent
      {
          Stream = File.OpenRead("/path/to/document.pdf"),
          FileName = "document.pdf",
          ContentType = new("application/pdf"),
      },
  });

  // Use the uploaded file in a message
  var message = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = new List<ContentBlockParam>
              {
                  new DocumentBlockParam
                  {
                      Source = new FileDocumentSource { FileID = fileUpload.ID },
                  },
                  new TextBlockParam("What are the key findings in this document?"),
              },
          },
      ],
  });

  Console.WriteLine(string.Join("\n", message.Content));

go Go
  client := anthropic.NewClient()

  // Upload the PDF file
  pdfFile, err := os.Open("/path/to/document.pdf")
  if err != nil {
  	panic(err)
  }
  defer pdfFile.Close()

  fileUpload, err := client.Files.Upload(context.TODO(), anthropic.FileUploadParams{
  	File: anthropic.File(pdfFile, "document.pdf", "application/pdf"),
  })
  if err != nil {
  	panic(err)
  }

  // Use the uploaded file in a message
  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(
  			anthropic.NewDocumentBlock(anthropic.FileDocumentSourceParam{
  				FileID: fileUpload.ID,
  			}),
  			anthropic.NewTextBlock("What are the key findings in this document?"),
  		),
  	},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Printf("%+v\n", message.Content)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  // Upload the PDF file
  FileMetadata file = client
    .files()
    .upload(FileUploadParams.builder().file(Path.of("/path/to/document.pdf")).build());

  // Use the uploaded file in a message
  MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_5)
    .maxTokens(1024)
    .addUserMessageOfBlockParams(
      List.of(
        ContentBlockParam.ofDocument(
          DocumentBlockParam.builder().fileSource(file.id()).build()
        ),
        ContentBlockParam.ofText(
          TextBlockParam.builder()
            .text("What are the key findings in this document?")
            .build()
        )
      )
    )
    .build();

  Message message = client.messages().create(params);
  System.out.println(message.content());

php PHP
  use Anthropic\Core\FileParam;

  $client = new Client();

  // Upload the PDF file
  $file_upload = $client->files->upload(
      file: FileParam::fromResource(fopen('/path/to/document.pdf', 'r'), contentType: 'application/pdf'),
  );

  // Use the uploaded file in a message
  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'document',
                      'source' => [
                          'type' => 'file',
                          'fileID' => $file_upload->id,
                      ],
                  ],
                  [
                      'type' => 'text',
                      'text' => 'What are the key findings in this document?',
                  ],
              ],
          ],
      ],
      model: 'claude-opus-5',
  );

  echo $message;

ruby Ruby
  anthropic = Anthropic::Client.new

  # Upload the PDF file
  file_upload = File.open("/path/to/document.pdf", "rb") do |f|
    anthropic.files.upload(
      file: Anthropic::FilePart.new(f, filename: "document.pdf", content_type: "application/pdf")
    )
  end

  # Use the uploaded file in a message
  message = anthropic.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: {type: "file", file_id: file_upload.id}
          },
          {type: "text", text: "What are the key findings in this document?"}
        ]
      }
    ]
  )

  puts(message.content)
  ```
</CodeGroup>

### How PDF support works

When you send a PDF to Claude, the following steps occur:

<Steps>
  <Step title="The system extracts the contents of the document.">
    * The system converts each page of the document into an image.
    * The text from each page is extracted and provided alongside each page's image.
  </Step>

  <Step title="Claude analyzes both the text and images to better understand the document.">
    * Documents are provided as a combination of text and images for analysis.
    * This allows users to ask for insights on visual elements of a PDF, such as charts, diagrams, and other non-textual content.
  </Step>

  <Step title="Claude responds, referencing the PDF's contents if relevant.">
    Claude can reference both textual and visual content when it responds. You can further improve performance by integrating PDF support with:

    * [Use prompt caching](https://platform.claude.com/docs/en/build-with-claude/pdf-support#use-prompt-caching): To improve performance for repeated analysis.
    * [Process document batches](https://platform.claude.com/docs/en/build-with-claude/pdf-support#process-document-batches): For high-volume document processing.
    * [Tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview): To extract specific information from documents for use as tool inputs.
  </Step>
</Steps>

### Estimate your costs

The token count of a PDF file depends on the total text extracted from the document and the number of pages:

* Text token costs: Each page typically uses 1,500–3,000 tokens per page depending on content density. Standard API pricing applies with no additional PDF fees.
* Image token costs: Because each page is converted into an image, the same [image-based cost calculations](https://platform.claude.com/docs/en/build-with-claude/vision#evaluate-image-size) are applied.

You can use [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) to estimate costs for your specific PDFs.


## Optimize PDF processing

Source: https://platform.claude.com/llms-full.txt#optimize-pdf-processing

### Improve performance

Follow these best practices for optimal results:

* Place PDFs before text in your requests
* Use standard fonts
* Ensure text is clear and legible
* Rotate pages to proper upright orientation
* Use logical page numbers (from PDF viewer) in prompts
* Split large PDFs into chunks when needed
* Enable prompt caching for repeated analysis

### Scale your implementation

For high-volume processing, consider these approaches:

#### Use prompt caching

Cache PDFs with [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) to improve performance on repeated queries:

<CodeGroup>
  ```bash cURL
  curl -sL "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf" | base64 | tr -d '\n' > pdf_base64.txt
  # Create a JSON request file using the pdf_base64.txt content
  jq -n --rawfile PDF_BASE64 pdf_base64.txt '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{
          "role": "user",
          "content": [{
              "type": "document",
              "source": {
                  "type": "base64",
                  "media_type": "application/pdf",
                  "data": $PDF_BASE64
              },
              "cache_control": {
                  "type": "ephemeral"
              }
          },
          {
              "type": "text",
              "text": "Which model has the highest human preference win rates across each use-case?"
          }]
      }]
  }' > request.json

  # Then make the API call using the JSON file
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d @request.json

bash CLI
  ant messages create --transform content --format yaml <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  messages:
    - role: user
      content:
        - type: document
          source:
            type: base64
            media_type: application/pdf
            data: "@./document.pdf"
          cache_control:
            type: ephemeral
        - type: text
          text: Which model has the highest human preference win rates across each use-case?
  YAML

python Python
  import base64
  import httpx2

  # First, load and encode the PDF
  pdf_url = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
  pdf_data = base64.standard_b64encode(
      httpx2.get(pdf_url, follow_redirects=True).content
  ).decode("utf-8")

  # Create a message with the cached document
  client = anthropic.Anthropic()
  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "document",
                      "source": {
                          "type": "base64",
                          "media_type": "application/pdf",
                          "data": pdf_data,
                      },
                      "cache_control": {"type": "ephemeral"},
                  },
                  {
                      "type": "text",
                      "text": "Which model has the highest human preference win rates across each use-case?",
                  },
              ],
          }
      ],
  )

  print(message.content)

typescript TypeScript
  // First, load and encode the PDF
  const pdfURL =
    "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf";
  const pdfResponse = await fetch(pdfURL);
  const arrayBuffer = await pdfResponse.arrayBuffer();
  const pdfBase64 = Buffer.from(arrayBuffer).toString("base64");

  // Create a message with the cached document
  const anthropic = new Anthropic();
  const response = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: {
              type: "base64",
              media_type: "application/pdf",
              data: pdfBase64
            },
            cache_control: { type: "ephemeral" }
          },
          {
            type: "text",
            text: "Which model has the highest human preference win rates across each use-case?"
          }
        ]
      }
    ]
  });

  console.log(response);

csharp C#
  var client = new AnthropicClient();

  // Download and encode the PDF
  var pdfUrl = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf";
  using var httpClient = new HttpClient();
  var pdfBase64 = Convert.ToBase64String(await httpClient.GetByteArrayAsync(pdfUrl));

  var message = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = new List<ContentBlockParam>
              {
                  new DocumentBlockParam
                  {
                      Source = new Base64PdfSource { Data = pdfBase64 },
                      CacheControl = new CacheControlEphemeral(),
                  },
                  new TextBlockParam("Which model has the highest human preference win rates across each use-case?"),
              },
          },
      ],
  });

  Console.WriteLine(message);

go Go
  // First, load and encode the PDF
  pdfURL := "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
  resp, err := http.Get(pdfURL)
  if err != nil {
  	panic(err)
  }
  defer resp.Body.Close()
  pdfBytes, err := io.ReadAll(resp.Body)
  if err != nil {
  	panic(err)
  }
  pdfBase64 := base64.StdEncoding.EncodeToString(pdfBytes)

  // Create a document block with cache control
  client := anthropic.NewClient()
  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(
  			anthropic.ContentBlockParamUnion{
  				OfDocument: &anthropic.DocumentBlockParam{
  					Source: anthropic.DocumentBlockParamSourceUnion{
  						OfBase64: &anthropic.Base64PDFSourceParam{
  							Data: pdfBase64,
  						},
  					},
  					CacheControl: anthropic.NewCacheControlEphemeralParam(),
  				},
  			},
  			anthropic.NewTextBlock("Which model has the highest human preference win rates across each use-case?"),
  		),
  	},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Printf("%+v\n", message.Content)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  // Download and encode the PDF
  String pdfUrl =
    "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf";
  HttpClient httpClient = HttpClient.newBuilder().followRedirects(HttpClient.Redirect.NORMAL).build();
  HttpRequest request = HttpRequest.newBuilder().uri(URI.create(pdfUrl)).GET().build();

  HttpResponse<byte[]> response = httpClient.send(
    request,
    HttpResponse.BodyHandlers.ofByteArray()
  );
  String pdfBase64 = Base64.getEncoder().encodeToString(response.body());

  MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_5)
    .maxTokens(1024)
    .addUserMessageOfBlockParams(
      List.of(
        ContentBlockParam.ofDocument(
          DocumentBlockParam.builder()
            .source(Base64PdfSource.builder().data(pdfBase64).build())
            .cacheControl(CacheControlEphemeral.builder().build())
            .build()
        ),
        ContentBlockParam.ofText(
          TextBlockParam.builder()
            .text(
              "Which model has the highest human preference win rates across each use-case?"
            )
            .build()
        )
      )
    )
    .build();

  Message message = client.messages().create(params);
  System.out.println(message);

php PHP
  $client = new Client();

  // Load and encode the PDF
  $pdf_url = 'https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf';
  $pdf_data = base64_encode(file_get_contents($pdf_url));

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'document',
                      'source' => [
                          'type' => 'base64',
                          'media_type' => 'application/pdf',
                          'data' => $pdf_data,
                      ],
                      'cache_control' => ['type' => 'ephemeral'],
                  ],
                  [
                      'type' => 'text',
                      'text' => 'Which model has the highest human preference win rates across each use-case?',
                  ],
              ],
          ],
      ],
      model: 'claude-opus-5',
  );

  echo $message;

ruby Ruby
  require "open-uri"

  # Load and encode the PDF
  pdf_url = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
  pdf_bytes = URI.open(pdf_url, "rb") { |f| f.read }
  pdf_data = [pdf_bytes].pack("m0") # Base64-encode without newlines

  anthropic = Anthropic::Client.new

  message = anthropic.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: {
              type: "base64",
              media_type: "application/pdf",
              data: pdf_data
            },
            cache_control: {type: "ephemeral"}
          },
          {
            type: "text",
            text: "Which model has the highest human preference win rates across each use-case?"
          }
        ]
      }
    ]
  )

  puts(message.content)

bash cURL
  curl -sL "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf" | base64 | tr -d '\n' > pdf_base64.txt
  # Create a JSON request file using the pdf_base64.txt content
  jq -n --rawfile PDF_BASE64 pdf_base64.txt '{
      "requests": [
      {
          "custom_id": "my-first-request",
          "params": {
              "model": "claude-opus-5",
              "max_tokens": 1024,
              "messages": [{
                  "role": "user",
                  "content": [{
                      "type": "document",
                      "source": {
                          "type": "base64",
                          "media_type": "application/pdf",
                          "data": $PDF_BASE64
                      }
                  },
                  {
                      "type": "text",
                      "text": "Which model has the highest human preference win rates across each use-case?"
                  }]
              }]
          }
      },
      {
          "custom_id": "my-second-request",
          "params": {
              "model": "claude-opus-5",
              "max_tokens": 1024,
              "messages": [{
                  "role": "user",
                  "content": [{
                      "type": "document",
                      "source": {
                          "type": "base64",
                          "media_type": "application/pdf",
                          "data": $PDF_BASE64
                      }
                  },
                  {
                      "type": "text",
                      "text": "Extract 5 key insights from this document."
                  }]
              }]
          }
      }]
  }' > request.json

  # Then make the API call using the JSON file
  curl https://api.anthropic.com/v1/messages/batches \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d @request.json

bash CLI
  ant messages:batches create <<'YAML'
  requests:
    - custom_id: my-first-request
      params:
        model: claude-opus-5
        max_tokens: 1024
        messages:
          - role: user
            content:
              - type: document
                source:
                  type: base64
                  media_type: application/pdf
                  data: "@./document.pdf"
              - type: text
                text: >-
                  Which model has the highest human preference win rates
                  across each use-case?
    - custom_id: my-second-request
      params:
        model: claude-opus-5
        max_tokens: 1024
        messages:
          - role: user
            content:
              - type: document
                source:
                  type: base64
                  media_type: application/pdf
                  data: "@./document.pdf"
              - type: text
                text: Extract 5 key insights from this document.
  YAML

python Python
  import base64
  import httpx2

  # First, load and encode the PDF
  pdf_url = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
  pdf_data = base64.standard_b64encode(
      httpx2.get(pdf_url, follow_redirects=True).content
  ).decode("utf-8")

  # Create a batch of requests that use the document
  client = anthropic.Anthropic()
  message_batch = client.messages.batches.create(
      requests=[
          {
              "custom_id": "my-first-request",
              "params": {
                  "model": "claude-opus-5",
                  "max_tokens": 1024,
                  "messages": [
                      {
                          "role": "user",
                          "content": [
                              {
                                  "type": "document",
                                  "source": {
                                      "type": "base64",
                                      "media_type": "application/pdf",
                                      "data": pdf_data,
                                  },
                              },
                              {
                                  "type": "text",
                                  "text": "Which model has the highest human preference win rates across each use-case?",
                              },
                          ],
                      }
                  ],
              },
          },
          {
              "custom_id": "my-second-request",
              "params": {
                  "model": "claude-opus-5",
                  "max_tokens": 1024,
                  "messages": [
                      {
                          "role": "user",
                          "content": [
                              {
                                  "type": "document",
                                  "source": {
                                      "type": "base64",
                                      "media_type": "application/pdf",
                                      "data": pdf_data,
                                  },
                              },
                              {
                                  "type": "text",
                                  "text": "Extract 5 key insights from this document.",
                              },
                          ],
                      }
                  ],
              },
          },
      ]
  )

  print(message_batch)

typescript TypeScript
  // First, load and encode the PDF
  const pdfURL =
    "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf";
  const pdfResponse = await fetch(pdfURL);
  const arrayBuffer = await pdfResponse.arrayBuffer();
  const pdfBase64 = Buffer.from(arrayBuffer).toString("base64");

  // Create a batch of requests that use the document
  const anthropic = new Anthropic();
  const response = await anthropic.messages.batches.create({
    requests: [
      {
        custom_id: "my-first-request",
        params: {
          model: "claude-opus-5",
          max_tokens: 1024,
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "document",
                  source: {
                    type: "base64",
                    media_type: "application/pdf",
                    data: pdfBase64
                  }
                },
                {
                  type: "text",
                  text: "Which model has the highest human preference win rates across each use-case?"
                }
              ]
            }
          ]
        }
      },
      {
        custom_id: "my-second-request",
        params: {
          model: "claude-opus-5",
          max_tokens: 1024,
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "document",
                  source: {
                    type: "base64",
                    media_type: "application/pdf",
                    data: pdfBase64
                  }
                },
                {
                  type: "text",
                  text: "Extract 5 key insights from this document."
                }
              ]
            }
          ]
        }
      }
    ]
  });

  console.log(response);

csharp C#
  var client = new AnthropicClient();

  // Download and encode the PDF
  var pdfUrl = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf";
  using var httpClient = new HttpClient();
  var pdfBase64 = Convert.ToBase64String(await httpClient.GetByteArrayAsync(pdfUrl));

  var batch = await client.Messages.Batches.Create(new BatchCreateParams
  {
      Requests =
      [
          new()
          {
              CustomID = "my-first-request",
              Params = new()
              {
                  Model = Model.ClaudeOpus5,
                  MaxTokens = 1024,
                  Messages =
                  [
                      new()
                      {
                          Role = Role.User,
                          Content = new List<ContentBlockParam>
                          {
                              new DocumentBlockParam
                              {
                                  Source = new Base64PdfSource { Data = pdfBase64 },
                              },
                              new TextBlockParam("Which model has the highest human preference win rates across each use-case?"),
                          },
                      },
                  ],
              },
          },
          new()
          {
              CustomID = "my-second-request",
              Params = new()
              {
                  Model = Model.ClaudeOpus5,
                  MaxTokens = 1024,
                  Messages =
                  [
                      new()
                      {
                          Role = Role.User,
                          Content = new List<ContentBlockParam>
                          {
                              new DocumentBlockParam
                              {
                                  Source = new Base64PdfSource { Data = pdfBase64 },
                              },
                              new TextBlockParam("Extract 5 key insights from this document."),
                          },
                      },
                  ],
              },
          },
      ],
  });

  Console.WriteLine(batch);

go Go
  // First, load and encode the PDF
  pdfURL := "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
  resp, err := http.Get(pdfURL)
  if err != nil {
  	panic(err)
  }
  defer resp.Body.Close()
  pdfBytes, err := io.ReadAll(resp.Body)
  if err != nil {
  	panic(err)
  }
  pdfBase64 := base64.StdEncoding.EncodeToString(pdfBytes)

  // Create a batch of requests that use the document
  client := anthropic.NewClient()
  batch, err := client.Messages.Batches.New(context.TODO(), anthropic.MessageBatchNewParams{
  	Requests: []anthropic.MessageBatchNewParamsRequest{
  		{
  			CustomID: "my-first-request",
  			Params: anthropic.MessageBatchNewParamsRequestParams{
  				Model:     anthropic.ModelClaudeOpus5,
  				MaxTokens: 1024,
  				Messages: []anthropic.MessageParam{
  					anthropic.NewUserMessage(
  						anthropic.NewDocumentBlock(anthropic.Base64PDFSourceParam{
  							Data: pdfBase64,
  						}),
  						anthropic.NewTextBlock("Which model has the highest human preference win rates across each use-case?"),
  					),
  				},
  			},
  		},
  		{
  			CustomID: "my-second-request",
  			Params: anthropic.MessageBatchNewParamsRequestParams{
  				Model:     anthropic.ModelClaudeOpus5,
  				MaxTokens: 1024,
  				Messages: []anthropic.MessageParam{
  					anthropic.NewUserMessage(
  						anthropic.NewDocumentBlock(anthropic.Base64PDFSourceParam{
  							Data: pdfBase64,
  						}),
  						anthropic.NewTextBlock("Extract 5 key insights from this document."),
  					),
  				},
  			},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Printf("%+v\n", batch)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  // Download and encode the PDF
  String pdfUrl =
    "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf";
  HttpClient httpClient = HttpClient.newBuilder().followRedirects(HttpClient.Redirect.NORMAL).build();
  HttpRequest request = HttpRequest.newBuilder().uri(URI.create(pdfUrl)).GET().build();

  HttpResponse<byte[]> response = httpClient.send(
    request,
    HttpResponse.BodyHandlers.ofByteArray()
  );
  String pdfBase64 = Base64.getEncoder().encodeToString(response.body());

  BatchCreateParams params = BatchCreateParams.builder()
    .addRequest(
      BatchCreateParams.Request.builder()
        .customId("my-first-request")
        .params(
          BatchCreateParams.Request.Params.builder()
            .model(Model.CLAUDE_OPUS_5)
            .maxTokens(1024)
            .addUserMessageOfBlockParams(
              List.of(
                ContentBlockParam.ofDocument(
                  DocumentBlockParam.builder()
                    .source(Base64PdfSource.builder().data(pdfBase64).build())
                    .build()
                ),
                ContentBlockParam.ofText(
                  TextBlockParam.builder()
                    .text(
                      "Which model has the highest human preference win rates across each use-case?"
                    )
                    .build()
                )
              )
            )
            .build()
        )
        .build()
    )
    .addRequest(
      BatchCreateParams.Request.builder()
        .customId("my-second-request")
        .params(
          BatchCreateParams.Request.Params.builder()
            .model(Model.CLAUDE_OPUS_5)
            .maxTokens(1024)
            .addUserMessageOfBlockParams(
              List.of(
                ContentBlockParam.ofDocument(
                  DocumentBlockParam.builder()
                    .source(Base64PdfSource.builder().data(pdfBase64).build())
                    .build()
                ),
                ContentBlockParam.ofText(
                  TextBlockParam.builder()
                    .text("Extract 5 key insights from this document.")
                    .build()
                )
              )
            )
            .build()
        )
        .build()
    )
    .build();

  MessageBatch batch = client.messages().batches().create(params);
  System.out.println(batch);

php PHP
  $client = new Client();

  // Load and encode the PDF
  $pdf_url = 'https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf';
  $pdf_data = base64_encode(file_get_contents($pdf_url));

  $batch = $client->messages->batches->create(
      requests: [
          [
              'custom_id' => 'my-first-request',
              'params' => [
                  'model' => 'claude-opus-5',
                  'max_tokens' => 1024,
                  'messages' => [
                      [
                          'role' => 'user',
                          'content' => [
                              [
                                  'type' => 'document',
                                  'source' => [
                                      'type' => 'base64',
                                      'media_type' => 'application/pdf',
                                      'data' => $pdf_data,
                                  ],
                              ],
                              [
                                  'type' => 'text',
                                  'text' => 'Which model has the highest human preference win rates across each use-case?',
                              ],
                          ],
                      ],
                  ],
              ],
          ],
          [
              'custom_id' => 'my-second-request',
              'params' => [
                  'model' => 'claude-opus-5',
                  'max_tokens' => 1024,
                  'messages' => [
                      [
                          'role' => 'user',
                          'content' => [
                              [
                                  'type' => 'document',
                                  'source' => [
                                      'type' => 'base64',
                                      'media_type' => 'application/pdf',
                                      'data' => $pdf_data,
                                  ],
                              ],
                              [
                                  'type' => 'text',
                                  'text' => 'Extract 5 key insights from this document.',
                              ],
                          ],
                      ],
                  ],
              ],
          ],
      ],
  );

  echo $batch;

ruby Ruby
  require "open-uri"

  # Load and encode the PDF
  pdf_url = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
  pdf_bytes = URI.open(pdf_url, "rb") { |f| f.read }
  pdf_data = [pdf_bytes].pack("m0") # Base64-encode without newlines

  anthropic = Anthropic::Client.new

  message_batch = anthropic.messages.batches.create(
    requests: [
      {
        custom_id: "my-first-request",
        params: {
          model: "claude-opus-5",
          max_tokens: 1024,
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "document",
                  source: {
                    type: "base64",
                    media_type: "application/pdf",
                    data: pdf_data
                  }
                },
                {
                  type: "text",
                  text: "Which model has the highest human preference win rates across each use-case?"
                }
              ]
            }
          ]
        }
      },
      {
        custom_id: "my-second-request",
        params: {
          model: "claude-opus-5",
          max_tokens: 1024,
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "document",
                  source: {
                    type: "base64",
                    media_type: "application/pdf",
                    data: pdf_data
                  }
                },
                {
                  type: "text",
                  text: "Extract 5 key insights from this document."
                }
              ]
            }
          ]
        }
      }
    ]
  )

  puts(message_batch)
  ```
</CodeGroup>

Batches process asynchronously. To check progress and retrieve results once processing ends, see [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-53

<CardGroup cols={2}>
  <Card title="Vision" icon="image" href="https://platform.claude.com/docs/en/build-with-claude/vision">
    Claude's vision capabilities allow it to understand and analyze images, opening up exciting possibilities for multimodal interaction.
  </Card>

  <Card title="Try PDF examples" icon="file" href="https://platform.claude.com/cookbook/multimodal-getting-started-with-vision">
    Explore practical examples of PDF processing in the Claude Cookbook recipe.
  </Card>

  <Card title="View API reference" icon="code" href="https://platform.claude.com/docs/en/api/messages/create">
    See complete API documentation for PDF support.
  </Card>
</CardGroup>


### Working with files > Images and vision

---
title: Coordinates and bounding boxes
url: https://platform.claude.com/docs/en/build-with-claude/vision-coordinates
description: How Claude resizes images, and how to work with the pixel coordinates it returns for bounding boxes, points, and UI elements.
---

Claude can locate and label regions of an image (for example, returning bounding boxes for tables, form fields, chart elements, or UI components). This guide covers how Claude resizes images before processing them and how to work with the pixel coordinates it returns, so that boxes and points line up with your original image.

You'll need this for OCR pipelines, form extraction, chart parsing, UI element location, and any task where you act on a specific region of an image. For sending images, supported formats, and per-model resolution limits, see [Vision](https://platform.claude.com/docs/en/build-with-claude/vision).

<Note>
  **Claude works best with absolute pixel coordinates.** Ask for them explicitly in your prompt. For example: *"Return the bounding box of each table as `[x1, y1, x2, y2]` (top-left and bottom-right corners) in pixel coordinates."* Claude does not work well when you ask for normalized coordinates, for example: *"Return bounding box coordinates between `0` and `1000`."* Always ask for pixel coordinates and normalize in your own code if you need to. To get coordinates as machine-readable JSON instead of prose, define a schema with [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), for example an object with an `[x1, y1, x2, y2]` array per detected element.
</Note>

Coordinates follow the standard image convention: the origin `(0, 0)` is the top-left corner of the image, with x increasing to the right and y increasing downward. The coordinates Claude returns are pixel positions in the image Claude sees: your image after Claude resizes it to fit the model's native resolution (see [How Claude resizes and pads images](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#how-claude-resizes-and-pads-images)). To get coordinates you can use directly, either pre-resize your image so the coordinates map one-to-one onto the image you have (see [Resize your image before uploading](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#resize-your-image-before-uploading)), or rescale the coordinates Claude returns (see [Rescale coordinates when you cannot pre-resize](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#rescale-coordinates-when-you-cannot-pre-resize)).

<Note>
  Claude's spatial reasoning has limits (see [Limitations](https://platform.claude.com/docs/en/build-with-claude/vision#limitations)). Coordinate accuracy is best when you state the expected coordinate format in your prompt and spot-check results visually before processing at scale. Small elements lose precision when an image is downscaled: for fine targets, crop the region of interest and send the crop (offset returned coordinates by the crop origin), or use a high-resolution-tier model. For [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support), pages are rasterized to images server-side at dimensions you don't control, so the returned coordinates can't be reliably mapped back onto the page. To work with coordinates on PDF content, rasterize the pages to images yourself and use the pre-resize approach.
</Note>


## How Claude resizes and pads images

Source: https://platform.claude.com/llms-full.txt#how-claude-resizes-and-pads-images

Claude finds the largest aspect-preserving size that satisfies both of the model's image limits:

1. **Edge limit:** neither side exceeds the maximum edge length (1568 px on the standard tier, 2576 px on the high-resolution tier).
2. **Visual token limit:** the image's token cost `⌈width / 28⌉ × ⌈height / 28⌉` does not exceed the model's visual token budget (1568 tokens on the standard tier, 4784 on the high-resolution tier).

See [Resolution and token cost](https://platform.claude.com/docs/en/build-with-claude/vision#evaluate-image-size) for which models are in which tier.

For nearly all photos and screenshots, the visual token limit is what determines the final size. The edge limit takes over only for elongated images such as panoramas or tall phone screenshots. Compute the size with the [reference implementation](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#resize-your-image-before-uploading) rather than scaling to the edge length by hand: a 1920×1080 screenshot resizes to 1456×819, not 1568×882, and assuming the edge limit puts every coordinate noticeably off target.

The token limit can also trigger a resize when neither side exceeds the edge limit. Overlooking this is the most common cause of misaligned coordinates. For example, an A4 page scanned at 130 DPI is 1075×1520 pixels: both sides are under 1568 px, but it costs `39 × 55 = 2145` visual tokens, so Claude resizes it to 924×1307.

<Note>
  This example assumes a model on the standard resolution tier. A high-resolution-tier model doesn't resize the same scan: 2145 tokens is within its 4784-token budget, so the coordinates it returns map directly onto the 1075×1520 original. Model tiers are listed in [Resolution and token cost](https://platform.claude.com/docs/en/build-with-claude/vision#evaluate-image-size).
</Note>

Claude then pads every image, resized or not, up to the next multiple of 28 pixels on the bottom and right edges (924×1307 becomes 924×1316 in the example). The padding contains no content: Claude perceives the padded image, but the page content only ever occupies the un-padded resized region. **Always normalize or rescale by the resized dimensions, not the padded dimensions**; dividing by the padded dimensions scales every coordinate by a small amount.


## Resize your image before uploading

Source: https://platform.claude.com/llms-full.txt#resize-your-image-before-uploading

The most reliable approach is to resize your image yourself before uploading, so the image you have is exactly the image Claude sees and the coordinates Claude returns need no conversion.

First check which resolution tier your model is on (see [Resolution and token cost](https://platform.claude.com/docs/en/build-with-claude/vision#evaluate-image-size)) and pass the matching edge and token limits. The following reference implementation computes the exact size Claude resizes an image to:

<CodeGroup>
  ```bash cURL
  # This reference implementation is local math that makes no API request, so
  # there's nothing to show for cURL. See the SDK tabs.

bash CLI
  # This reference implementation is local math that makes no API request, so
  # there's nothing to show for the CLI. See the SDK tabs.

python Python
  import math


  def count_image_tokens(width: int, height: int) -> int:
      """Visual tokens consumed by an image: one token per 28x28 pixel patch."""
      return math.ceil(width / 28) * math.ceil(height / 28)


  def resized_size(
      width: int,
      height: int,
      max_edge: int = 1568,
      max_tokens: int = 1568,
  ) -> tuple[int, int]:
      """The size Claude resizes an image to before padding.

      Defaults are for the standard resolution tier. For high-resolution-tier
      models, use max_edge=2576 and max_tokens=4784. Returns (width, height).
      Images that already fit within the limits are returned unchanged.
      """

      def fits(w: int, h: int) -> bool:
          return (
              math.ceil(w / 28) * 28 <= max_edge
              and math.ceil(h / 28) * 28 <= max_edge
              and count_image_tokens(w, h) <= max_tokens
          )

      if fits(width, height):
          return (width, height)
      if height > width:
          resized_h, resized_w = resized_size(height, width, max_edge, max_tokens)
          return (resized_w, resized_h)

      # Binary search along the long edge for the largest aspect-preserving
      # size that fits.
      aspect_ratio = width / height
      lo, hi = 1, width  # lo always fits; hi never fits
      while lo + 1 < hi:
          mid = (lo + hi) // 2
          if fits(mid, max(round(mid / aspect_ratio), 1)):
              lo = mid
          else:
              hi = mid
      return (lo, max(round(lo / aspect_ratio), 1))


  # The A4 example from "How Claude resizes and pads images":
  print(resized_size(1075, 1520))  # (924, 1307)

  # To apply the resize, use your image library, for example Pillow:
  # image.resize(resized_size(*image.size))

typescript TypeScript
  /** Visual tokens consumed by an image: one token per 28x28 pixel patch. */
  function countImageTokens(width: number, height: number): number {
    return Math.ceil(width / 28) * Math.ceil(height / 28);
  }

  /**
   * Round half to even (banker's rounding), matching Python's round(). The
   * live API resolves exact .5 ties toward the even neighbor, so Math.round
   * (which rounds halves up) would compute a different size for some images.
   */
  function roundTiesToEven(value: number): number {
    const floor = Math.floor(value);
    if (value - floor !== 0.5) return Math.round(value);
    return floor % 2 === 0 ? floor : floor + 1;
  }

  /**
   * The size Claude resizes an image to before padding.
   *
   * Defaults are for the standard resolution tier. For high-resolution-tier
   * models, use maxEdge = 2576 and maxTokens = 4784. Returns [width, height].
   * Images that already fit within the limits are returned unchanged.
   */
  function resizedSize(
    width: number,
    height: number,
    maxEdge = 1568,
    maxTokens = 1568
  ): [number, number] {
    const fits = (w: number, h: number): boolean =>
      Math.ceil(w / 28) * 28 <= maxEdge &&
      Math.ceil(h / 28) * 28 <= maxEdge &&
      countImageTokens(w, h) <= maxTokens;

    if (fits(width, height)) return [width, height];
    if (height > width) {
      const [resizedH, resizedW] = resizedSize(height, width, maxEdge, maxTokens);
      return [resizedW, resizedH];
    }

    // Binary search along the long edge for the largest aspect-preserving
    // size that fits.
    const aspectRatio = width / height;
    let lo = 1; // lo always fits
    let hi = width; // hi never fits
    while (lo + 1 < hi) {
      const mid = Math.floor((lo + hi) / 2);
      if (fits(mid, Math.max(roundTiesToEven(mid / aspectRatio), 1))) {
        lo = mid;
      } else {
        hi = mid;
      }
    }
    return [lo, Math.max(roundTiesToEven(lo / aspectRatio), 1)];
  }

  // The A4 example from "How Claude resizes and pads images":
  console.log(resizedSize(1075, 1520)); // [ 924, 1307 ]

  // To apply the resize, use your image library, for example sharp:
  // await sharp(input).resize(width, height).toBuffer()

csharp C#
  // Visual tokens consumed by an image: one token per 28x28 pixel patch.
  static int CountImageTokens(int width, int height)
  {
      return (width + 27) / 28 * ((height + 27) / 28); // ceil(w/28) * ceil(h/28)
  }

  // The size Claude resizes an image to before padding. Defaults are for the
  // standard resolution tier; for high-resolution-tier models, pass
  // maxEdge: 2576, maxTokens: 4784. Images that already fit within the limits
  // are returned unchanged.
  static (int Width, int Height) ResizedSize(
      int width, int height, int maxEdge = 1568, int maxTokens = 1568)
  {
      bool Fits(int w, int h) =>
          (w + 27) / 28 * 28 <= maxEdge
          && (h + 27) / 28 * 28 <= maxEdge
          && CountImageTokens(w, h) <= maxTokens;

      if (Fits(width, height))
      {
          return (width, height);
      }
      if (height > width)
      {
          (int resizedH, int resizedW) = ResizedSize(height, width, maxEdge, maxTokens);
          return (resizedW, resizedH);
      }

      // Binary search along the long edge for the largest aspect-preserving
      // size that fits. The short edge rounds half to even, matching the live
      // API at exact .5 ties (MidpointRounding.ToEven, Math.Round's default).
      double aspectRatio = (double)width / height;
      int lo = 1; // lo always fits
      int hi = width; // hi never fits
      while (lo + 1 < hi)
      {
          int mid = (lo + hi) / 2;
          if (Fits(mid, ShortEdge(mid)))
          {
              lo = mid;
          }
          else
          {
              hi = mid;
          }
      }
      return (lo, ShortEdge(lo));

      int ShortEdge(int longEdge) =>
          Math.Max((int)Math.Round(longEdge / aspectRatio, MidpointRounding.ToEven), 1);
  }

  // The A4 example from "How Claude resizes and pads images":
  Console.WriteLine(ResizedSize(1075, 1520)); // (924, 1307)

go Go
  // countImageTokens is the visual tokens consumed by an image: one token per
  // 28x28 pixel patch.
  func countImageTokens(width, height int) int {
  	return ((width + 27) / 28) * ((height + 27) / 28) // ceil(w/28) * ceil(h/28)
  }

  // resizedSize is the size Claude resizes an image to before padding, as
  // (width, height). Pass maxEdge 1568 and maxTokens 1568 for the standard
  // resolution tier, or 2576 and 4784 for the high-resolution tier. Images
  // that already fit within the limits are returned unchanged.
  // The A4 example from "How Claude resizes and pads images":
  // resizedSize(1075, 1520, 1568, 1568) returns (924, 1307).
  func resizedSize(width, height, maxEdge, maxTokens int) (int, int) {
  	fits := func(w, h int) bool {
  		return ((w+27)/28)*28 <= maxEdge &&
  			((h+27)/28)*28 <= maxEdge &&
  			countImageTokens(w, h) <= maxTokens
  	}

  	if fits(width, height) {
  		return width, height
  	}
  	if height > width {
  		resizedH, resizedW := resizedSize(height, width, maxEdge, maxTokens)
  		return resizedW, resizedH
  	}

  	// Binary search along the long edge for the largest aspect-preserving
  	// size that fits. The short edge rounds half to even (math.RoundToEven),
  	// matching the live API at exact .5 ties; math.Round would round them up.
  	aspectRatio := float64(width) / float64(height)
  	lo, hi := 1, width // lo always fits; hi never fits
  	for lo+1 < hi {
  		mid := (lo + hi) / 2
  		short := max(int(math.RoundToEven(float64(mid)/aspectRatio)), 1)
  		if fits(mid, short) {
  			lo = mid
  		} else {
  			hi = mid
  		}
  	}
  	return lo, max(int(math.RoundToEven(float64(lo)/aspectRatio)), 1)
  }

java Java
  /** A resized image size, as returned by resizedSize. */
  record Size(int width, int height) {}

  /** Visual tokens consumed by an image: one token per 28x28 pixel patch. */
  static int countImageTokens(int width, int height) {
      return Math.ceilDiv(width, 28) * Math.ceilDiv(height, 28);
  }

  /**
   * The size Claude resizes an image to before padding.
   *
   * <p>Pass maxEdge 1568 and maxTokens 1568 for the standard resolution tier,
   * or 2576 and 4784 for the high-resolution tier. Images that already fit
   * within the limits are returned unchanged.
   *
   * <p>The A4 example from "How Claude resizes and pads images":
   * resizedSize(1075, 1520, 1568, 1568) returns new Size(924, 1307).
   */
  static Size resizedSize(int width, int height, int maxEdge, int maxTokens) {
      if (fits(width, height, maxEdge, maxTokens)) {
          return new Size(width, height);
      }
      if (height > width) {
          Size rotated = resizedSize(height, width, maxEdge, maxTokens);
          return new Size(rotated.height(), rotated.width());
      }

      // Binary search along the long edge for the largest aspect-preserving
      // size that fits. The short edge rounds half to even (Math.rint),
      // matching the live API at exact .5 ties; Math.round would round them up.
      double aspectRatio = (double) width / height;
      int lo = 1; // lo always fits
      int hi = width; // hi never fits
      while (lo + 1 < hi) {
          int mid = (lo + hi) / 2;
          if (fits(mid, shortEdge(mid, aspectRatio), maxEdge, maxTokens)) {
              lo = mid;
          } else {
              hi = mid;
          }
      }
      return new Size(lo, shortEdge(lo, aspectRatio));
  }

  private static boolean fits(int width, int height, int maxEdge, int maxTokens) {
      return Math.ceilDiv(width, 28) * 28 <= maxEdge
              && Math.ceilDiv(height, 28) * 28 <= maxEdge
              && countImageTokens(width, height) <= maxTokens;
  }

  private static int shortEdge(int longEdge, double aspectRatio) {
      return Math.max((int) Math.rint(longEdge / aspectRatio), 1);
  }

php PHP
  // Visual tokens consumed by an image: one token per 28x28 pixel patch.
  function countImageTokens(int $width, int $height): int
  {
      return intdiv($width + 27, 28) * intdiv($height + 27, 28);
  }

  /**
   * The size Claude resizes an image to before padding, as [width, height].
   *
   * Defaults are for the standard resolution tier. For high-resolution-tier
   * models, pass maxEdge: 2576, maxTokens: 4784. Images that already fit
   * within the limits are returned unchanged.
   */
  function resizedSize(int $width, int $height, int $maxEdge = 1568, int $maxTokens = 1568): array
  {
      $fits = fn (int $w, int $h): bool =>
          intdiv($w + 27, 28) * 28 <= $maxEdge
          && intdiv($h + 27, 28) * 28 <= $maxEdge
          && countImageTokens($w, $h) <= $maxTokens;

      if ($fits($width, $height)) {
          return [$width, $height];
      }
      if ($height > $width) {
          [$resizedH, $resizedW] = resizedSize($height, $width, $maxEdge, $maxTokens);
          return [$resizedW, $resizedH];
      }

      // Binary search along the long edge for the largest aspect-preserving
      // size that fits. The short edge rounds half to even
      // (PHP_ROUND_HALF_EVEN), matching the live API at exact .5 ties.
      $aspectRatio = $width / $height;
      $lo = 1; // lo always fits
      $hi = $width; // hi never fits
      while ($lo + 1 < $hi) {
          $mid = intdiv($lo + $hi, 2);
          $short = max((int) round($mid / $aspectRatio, 0, PHP_ROUND_HALF_EVEN), 1);
          if ($fits($mid, $short)) {
              $lo = $mid;
          } else {
              $hi = $mid;
          }
      }

      return [$lo, max((int) round($lo / $aspectRatio, 0, PHP_ROUND_HALF_EVEN), 1)];
  }

  // The A4 example from "How Claude resizes and pads images":
  [$resizedWidth, $resizedHeight] = resizedSize(1075, 1520);
  echo "({$resizedWidth}, {$resizedHeight})\n"; // (924, 1307)

ruby Ruby
  # Visual tokens consumed by an image: one token per 28x28 pixel patch.
  def count_image_tokens(width, height)
    width.ceildiv(28) * height.ceildiv(28)
  end

  # The size Claude resizes an image to before padding, as [width, height].
  #
  # Defaults are for the standard resolution tier. For high-resolution-tier
  # models, pass max_edge: 2576, max_tokens: 4784. Images that already fit
  # within the limits are returned unchanged.
  def resized_size(width, height, max_edge = 1568, max_tokens = 1568)
    fits = lambda do |w, h|
      w.ceildiv(28) * 28 <= max_edge &&
        h.ceildiv(28) * 28 <= max_edge &&
        count_image_tokens(w, h) <= max_tokens
    end

    return [width, height] if fits.call(width, height)

    if height > width
      resized_h, resized_w = resized_size(height, width, max_edge, max_tokens)
      return [resized_w, resized_h]
    end

    # Binary search along the long edge for the largest aspect-preserving
    # size that fits. The short edge rounds half to even (round(half: :even)),
    # matching the live API at exact .5 ties.
    aspect_ratio = width.fdiv(height)
    lo = 1      # lo always fits
    hi = width  # hi never fits
    while lo + 1 < hi
      mid = (lo + hi) / 2
      short = [(mid / aspect_ratio).round(half: :even), 1].max
      if fits.call(mid, short)
        lo = mid
      else
        hi = mid
      end
    end

    [lo, [(lo / aspect_ratio).round(half: :even), 1].max]
  end

  # The A4 example from "How Claude resizes and pads images":
  p resized_size(1075, 1520) # => [924, 1307]
  ```
</CodeGroup>

1. Resize the image to the dimensions returned by the resize helper. If the image already fits within the model's limits, the helper returns its dimensions unchanged and no resize is needed.
2. [Send the resized image](https://platform.claude.com/docs/en/build-with-claude/vision#send-images-to-claude) to the API. Don't pad it yourself. Claude handles padding, and padding doesn't shift the coordinate origin.
3. In your prompt, ask explicitly for pixel coordinates. For example: *"Return the click point for the Submit button as `[x, y]` in pixel coordinates."*
4. Use the returned coordinates directly against the image you sent. If you need normalized coordinates, divide by the dimensions of the image you sent, not by the original image's dimensions and not by the padded dimensions.

<Note>
  The [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) endpoint estimates an image's token cost from its dimensions without fully processing it, so a successful count doesn't mean the image is within the Messages API's [request limits](https://platform.claude.com/docs/en/build-with-claude/vision#request-limits). An image can count successfully and still be rejected when you send it.
</Note>


## Turn resizing into an error with `transformations`

Source: https://platform.claude.com/llms-full.txt#turn-resizing-into-an-error-with-transformations

Pre-resizing only protects your coordinates while your pipeline keeps producing the right sizes. A new image source or a switch to a model on a different resolution tier can quietly reintroduce server-side resizing. To turn that silent drift into a visible error, set the optional `transformations` field on an image content block in a [Messages](https://platform.claude.com/docs/en/api/messages) request:

A request whose marked image (any block that sets `"oversized_image": "error"`) would be resized is rejected with a 400 `invalid_request_error` naming the image's dimensions and the largest dimensions that fit. Whether an image triggers the rejection depends on the [limits of every model the request names](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#how-claude-resizes-and-pads-images): the 1920×1080 example below is rejected by a standard-tier model but fits within the high-resolution tier:

```text wrap
messages.0.content.0: image dimensions 1920x1080 exceed the maximum image size of a model named on this request and would be downsized to 1456x819; scale the image to at most 1456x819 or set the image's oversized_image setting to "downsize"
```

Rescale to the reported target and resend: the target is the largest size, at your image's aspect ratio, that every model named on the request accepts. How marked images interact with the [server-side fallback beta](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#server-side-fallback) is described with that feature; in every mode, a marked image is never served resized.

The setting is per image. `"oversized_image": "downsize"` (the default when the field is omitted) keeps automatic resizing as described on this page. Each image block is checked only against its own setting, so one request can mix images whose dimensions are load-bearing (a screenshot you'll click on) with images where resizing is harmless (a logo). What the setting does and does not change:

* Padding ([which never discards content](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#how-claude-resizes-and-pads-images)), format conversion, and orientation correction proceed as usual.
* The hard limits (8000 px on the longest side, and the stricter per-image limit on [many-image requests](https://platform.claude.com/docs/en/build-with-claude/vision#request-limits)) are separate rejections; this setting never lets an image past them.
* Images supplied by URL or file ID are checked once their bytes have been fetched; those rejections carry the same message without the leading position, so they don't identify which image failed; only embedded base64 images are named by position in the error.
* [PDF pages](https://platform.claude.com/docs/en/build-with-claude/pdf-support) are rasterized server-side at dimensions you don't control; the `document` block does not accept the field (an image block nested inside a document's content accepts it like any other).
* A marked image whose dimensions cannot be determined is rejected rather than passed through: that rejection reports that the image's source dimensions could not be determined, not the resize message quoted above. No image that sets `"error"` reaches the model resized.

The [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) endpoint honors `transformations` too, rejecting an embedded image exactly as the Messages API would, so you can check whether an embedded image fits without being resized, before running inference. Counting never fetches images supplied by URL or file ID, so a marked image from those sources is checked only at Messages time, as described above.


## Rescale coordinates when you cannot pre-resize

Source: https://platform.claude.com/llms-full.txt#rescale-coordinates-when-you-cannot-pre-resize

If you cannot pre-resize (for example, when the image comes from an upstream system you can't modify), use the resize helper from [Resize your image before uploading](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#resize-your-image-before-uploading) to recover the dimensions Claude saw, then map the coordinates Claude returns into normalized coordinates or back onto your original image. Unless an image [opts into an error instead](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#oversized-image-error), Claude resizes oversized images rather than rejecting them, up to the API's [request limits](https://platform.claude.com/docs/en/build-with-claude/vision#request-limits). Beyond those limits the request fails with a validation error instead. Pass the tier limits that match the model you called: the wrong tier's limits recover the wrong resized dimensions and silently shift every coordinate. This approach requires knowing the pixel dimensions of the image you uploaded, so it does not apply to PDF uploads.

Screenshots and zoom images that you return to the [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#handle-coordinate-scaling-for-higher-resolutions) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#targets-and-coordinates) toolsets are an exception to automatic resizing. The API rejects a `tool_result` image that exceeds the model's limits with a validation error instead of resizing it. Resize those images in your application before returning them, then scale the coordinates Claude returns back to your screen's dimensions.

<CodeGroup>
  ```bash cURL
  # This local coordinate conversion makes no API request, so there's nothing
  # to show for cURL. See the SDK tabs.

bash CLI
  # This local coordinate conversion makes no API request, so there's nothing
  # to show for the CLI. See the SDK tabs.

python Python
  # This helper calls resized_size from the resize example on this page.
  def to_relative_coordinates(
      x: float,
      y: float,
      original_width: int,
      original_height: int,
      max_edge: int = 1568,
      max_tokens: int = 1568,
  ) -> tuple[float, float]:
      """Map a pixel coordinate returned by Claude to relative coordinates in [0, 1].

      Pass the dimensions of the image you uploaded. For high-resolution-tier
      models, use max_edge=2576 and max_tokens=4784.
      """
      resized_w, resized_h = resized_size(
          original_width, original_height, max_edge, max_tokens
      )
      return (x / resized_w, y / resized_h)


  # A table corner Claude returns at (462, 653.5) on the resized A4 page maps
  # back onto the 1075x1520 original like this:
  rel_x, rel_y = to_relative_coordinates(462, 653.5, 1075, 1520)
  print((rel_x * 1075, rel_y * 1520))  # (537.5, 760.0)

typescript TypeScript
  // This helper calls resizedSize from the resize example on this page.
  /**
   * Map a pixel coordinate returned by Claude to relative coordinates in [0, 1].
   *
   * Pass the dimensions of the image you uploaded. For high-resolution-tier
   * models, use maxEdge = 2576 and maxTokens = 4784.
   */
  function toRelativeCoordinates(
    x: number,
    y: number,
    originalWidth: number,
    originalHeight: number,
    maxEdge = 1568,
    maxTokens = 1568
  ): [number, number] {
    const [resizedW, resizedH] = resizedSize(
      originalWidth,
      originalHeight,
      maxEdge,
      maxTokens
    );
    return [x / resizedW, y / resizedH];
  }

  // A table corner Claude returns at (462, 653.5) on the resized A4 page maps
  // back onto the 1075x1520 original like this:
  const [relX, relY] = toRelativeCoordinates(462, 653.5, 1075, 1520);
  console.log([relX * 1075, relY * 1520]); // [ 537.5, 760 ]

csharp C#
  // This helper calls ResizedSize from the resize example on this page.
  // Map a pixel coordinate returned by Claude to relative coordinates in
  // [0, 1]. Pass the dimensions of the image you uploaded, and the same tier
  // limits used for ResizedSize.
  static (double X, double Y) ToRelativeCoordinates(
      double x, double y, int originalWidth, int originalHeight,
      int maxEdge = 1568, int maxTokens = 1568)
  {
      (int resizedW, int resizedH) =
          ResizedSize(originalWidth, originalHeight, maxEdge, maxTokens);
      return (x / resizedW, y / resizedH);
  }

  // A table corner Claude returns at (462, 653.5) on the resized A4 page maps
  // back onto the 1075x1520 original like this:
  (double relX, double relY) = ToRelativeCoordinates(462, 653.5, 1075, 1520);
  Console.WriteLine((relX * 1075, relY * 1520)); // (537.5, 760)

go Go
  // This helper calls resizedSize from the resize example on this page.

  // toRelativeCoordinates maps a pixel coordinate returned by Claude to
  // relative coordinates in [0, 1]. Pass the dimensions of the image you
  // uploaded, and the same tier limits used for resizedSize.
  func toRelativeCoordinates(
  	x, y float64,
  	originalWidth, originalHeight, maxEdge, maxTokens int,
  ) (float64, float64) {
  	resizedW, resizedH := resizedSize(originalWidth, originalHeight, maxEdge, maxTokens)
  	return x / float64(resizedW), y / float64(resizedH)
  }

  // To map back to your original image's pixel space, multiply by the original
  // dimensions: a table corner returned at (462, 653.5) on the resized A4 page
  // is (relX*1075, relY*1520) = (537.5, 760) on the 1075x1520 original.

java Java
  // This helper calls resizedSize from the resize example on this page.
  /** A coordinate scaled into the [0, 1] range on both axes. */
  record RelativeCoordinate(double x, double y) {}

  /**
   * Map a pixel coordinate returned by Claude to relative coordinates in
   * [0, 1]. Pass the dimensions of the image you uploaded, and the same tier
   * limits used for resizedSize.
   */
  static RelativeCoordinate toRelativeCoordinates(
          double x, double y, int originalWidth, int originalHeight, int maxEdge, int maxTokens) {
      Size resized = resizedSize(originalWidth, originalHeight, maxEdge, maxTokens);
      return new RelativeCoordinate(x / resized.width(), y / resized.height());
  }

  // To map back to your original image's pixel space, multiply by the original
  // dimensions: a table corner returned at (462, 653.5) on the resized A4 page
  // is (relative.x() * 1075, relative.y() * 1520) = (537.5, 760) on the
  // 1075x1520 original.

php PHP
  // This helper calls resizedSize() from the resize example on this page.
  /**
   * Map a pixel coordinate returned by Claude to relative coordinates in
   * [0, 1], as [x, y]. Pass the dimensions of the image you uploaded, and the
   * same tier limits used for resizedSize.
   */
  function toRelativeCoordinates(
      float $x,
      float $y,
      int $originalWidth,
      int $originalHeight,
      int $maxEdge = 1568,
      int $maxTokens = 1568,
  ): array {
      [$resizedW, $resizedH] = resizedSize($originalWidth, $originalHeight, $maxEdge, $maxTokens);

      return [$x / $resizedW, $y / $resizedH];
  }

  // A table corner Claude returns at (462, 653.5) on the resized A4 page maps
  // back onto the 1075x1520 original like this:
  [$relX, $relY] = toRelativeCoordinates(462, 653.5, 1075, 1520);
  echo '(' . $relX * 1075 . ', ' . $relY * 1520 . ")\n"; // (537.5, 760)

ruby Ruby
  # This helper calls resized_size from the resize example on this page.
  # Map a pixel coordinate returned by Claude to relative coordinates in
  # [0, 1], as [x, y]. Pass the dimensions of the image you uploaded, and the
  # same tier limits used for resized_size.
  def to_relative_coordinates(
    x, y, original_width, original_height, max_edge = 1568, max_tokens = 1568
  )
    resized_w, resized_h = resized_size(original_width, original_height, max_edge, max_tokens)
    [x.fdiv(resized_w), y.fdiv(resized_h)]
  end

  # A table corner Claude returns at (462, 653.5) on the resized A4 page maps
  # back onto the 1075x1520 original like this:
  rel_x, rel_y = to_relative_coordinates(462, 653.5, 1075, 1520)
  p [rel_x * 1075, rel_y * 1520] # => [537.5, 760.0]
  ```
</CodeGroup>

Padding is applied only to the bottom and right edges, so the origin doesn't shift and a per-axis linear rescale is sufficient. Clamp returned coordinates to the resized dimensions before rescaling, so a point slightly outside the image can't map outside your original.

The relative coordinates multiply against whatever surface you act on: the original image, a full-resolution scan, or a screen. When you act on a screen and screenshot pixels differ from logical coordinates (HiDPI displays), also divide by the display scale factor. The [Computer use tool's scaling guidance](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#handle-coordinate-scaling-for-higher-resolutions) covers that pattern.
