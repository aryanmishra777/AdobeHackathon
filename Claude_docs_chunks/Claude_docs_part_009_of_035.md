# platform.claude.com Documentation (Part 9 of 35)

## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-46

<CardGroup cols={2}>
  <Card title="Tool reference" icon="book" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference">
    Full catalog of Anthropic-provided tools with type strings and parameters.
  </Card>

  <Card title="Tool use overview" icon="map" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview">
    How tool use works and when to use Anthropic tools versus defining your own.
  </Card>
</CardGroup>


---
title: Tool reference
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference
description: Directory of Anthropic-provided server tools, client tools, and client toolsets, plus reference for optional tool definition properties.
---

This page is a reference for the tools Anthropic provides and the optional properties you can set on any tool definition. For a conceptual introduction to tool use, see [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview). For guidance on implementing tool use in your application, see [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools).


## Anthropic-provided tools

Source: https://platform.claude.com/llms-full.txt#anthropic-provided-tools

Anthropic provides two kinds of tools: **server tools** that execute on Anthropic's infrastructure, and **client tools** where Anthropic defines the schema but your application handles execution. Both kinds appear in your request's `tools` array alongside any user-defined tools.

| Tool                                                                                                     | `type`                                                                              | Execution | [Beta header](https://platform.claude.com/docs/en/api/beta-headers) |
| -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------- |
| [Web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)         | `web_search_20260318` `web_search_20260209` `web_search_20250305`                   | Server    | None                                                                |
| [Web fetch tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool)           | `web_fetch_20260318` `web_fetch_20260309` `web_fetch_20260209` `web_fetch_20250910` | Server    | None                                                                |
| [Code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) | `code_execution_20260521` `code_execution_20260120` `code_execution_20250825`       | Server    | None                                                                |
| [Advisor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)               | `advisor_20260301`                                                                  | Server    | `advisor-tool-2026-03-01`                                           |
| [Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)       | `tool_search_tool_regex_20251119` `tool_search_tool_bm25_20251119`                  | Server    | None                                                                |
| [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)                      | `mcp_toolset`                                                                       | Server    | `mcp-client-2025-11-20`                                             |
| [Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)                 | `memory_20250818`                                                                   | Client    | None                                                                |
| [Bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool)                     | `bash_20250124`                                                                     | Client    | None                                                                |
| [Text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)       | `text_editor_20250728` `text_editor_20250124`                                       | Client    | None                                                                |
| [Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)     | `computer_toolset_20260801` `computer_20251124` `computer_20250124`                 | Client    | None `computer-use-2025-11-24` `computer-use-2025-01-24`            |
| [Browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool)       | `browser_toolset_20260801`                                                          | Client    | None                                                                |

For model compatibility, see each tool's page. Supported models vary by tool and by tool version.

<Note>
  The tool search `type` values also accept undated aliases: `tool_search_tool_regex` and `tool_search_tool_bm25`. These resolve to the latest dated version.
</Note>

### Tool versioning

Most Anthropic-provided tools carry a `_YYYYMMDD` suffix in the `type` string. A new version is released when the tool's behavior, schema, or model support changes. Older versions remain available so that existing integrations continue to work.

When a tool has multiple active versions, the relationship between them varies:

* **Capability-keyed:** `web_search_20260209` and `web_fetch_20260209` add dynamic content filtering over their predecessors; `web_fetch_20260309` adds a cache-bypass option; `web_search_20260318` and `web_fetch_20260318` add response-inclusion control. `code_execution_20260120` adds [programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling) from within the sandbox; `code_execution_20260521` discloses the per-cell time limit in the tool description. In each case, both the new and old versions are current; which one you use depends on whether you need the new capability.
* **Model-keyed:** `text_editor_20250728` is for Claude 4 and later models and `text_editor_20250124` is for earlier models. The version you use depends on the model you target.
* **Variant, not version:** `tool_search_tool_regex_20251119` and `tool_search_tool_bm25_20251119` are two search algorithms released together. Neither supersedes the other.
* **Legacy:** `code_execution_20250522` supports only Python. `code_execution_20250825` adds Bash and file operations.
* **Successor:** `computer_toolset_20260801` is the stable successor to the beta `computer_20251124` and `computer_20250124` versions, which remain available for existing integrations and for models that don't support the toolset ([Earlier tool versions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#earlier-tool-versions)). `browser_toolset_20260801` is the first version of the browser use tool. Both are [client toolsets](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets).

The `mcp_toolset` type is not date-versioned; versioning is carried in the `anthropic-beta` header instead.

### Client toolsets

The [computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) and [browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) are Anthropic-defined client toolsets: one entry in `tools` declares a fixed set of member tools whose names, descriptions, and input schemas Anthropic defines, and your application executes every call. The entry takes no `name`, because the dated `type` fixes the member names. `configs`, `cache_control`, and `allowed_callers` (which accepts only `["direct"]`) are optional.

Client toolsets are Messages API tools. They aren't currently available as agent tools in [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/tools), which provides its own built-in agent toolset, MCP toolsets, and custom tools.

`configs` adjusts individual members:

* Keys are member names, and each value accepts only `enabled` and `defer_loading`.
* A member you omit keeps its defaults. An absent value, `{}`, and a restated default are equivalent.
* An unknown member name or any other field in a member's value is rejected, as is a `configs` that disables every member (omit the entry instead).
* A disabled member is removed from the tools Claude sees. If Claude still names it, return an error `tool_result`.

Set `defer_loading` per member, never on the entry, and give every enabled member the same value: under [tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#deferred-tool-loading) the toolset loads and expands as one definition. When every enabled member defers, only a [tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) that isn't itself deferred can surface the toolset, so declare one in the same request. Don't put `cache_control` on a toolset entry whose members defer; set the breakpoint on a non-deferred tool instead, because deferred definitions are not part of the cached prefix.

`cache_control` goes on the entry only; to learn where the breakpoint lands, including markers inside a batch action, see [Tool use with prompt caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching#cache-control-on-tool-definitions).

**Handle member tool calls.** Claude calls a member with a `tool_use` block whose `name` is the member name and whose `toolset_name` is `computer` or `browser`; `input` holds that member's parameters and no `action` field. Dispatch on the `toolset_name` and `name` pair, because a custom tool may share a member's name and the two toolsets share names such as `screenshot`. Only member results echo `toolset_name`. Several member calls in one turn form a batch action that you run in order ([computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#batch-actions), [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#batch-actions)). New members arrive only with a new dated `type`.

**Not supported on toolset entries.** The API rejects each of these with an `invalid_request_error`:

* `strict: true` or `input_examples`.
* `defer_loading` on the entry, or enabled members whose `defer_loading` values differ (set it per member in `configs`, all to the same value).
* A code execution caller in `allowed_callers` (no [programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)).
* The legacy `fine-grained-tool-streaming-2025-05-14` beta header. When you stream, each member's `input` arrives as one complete `input_json_delta`.
* A `tool_choice` of type `tool` that names the toolset or a member (use `auto`, `any`, or `none`).
* Two entries of the same toolset, or another tool that carries that toolset's name: a tool named `computer` alongside `computer_toolset_20260801`, or a tool named `browser` alongside `browser_toolset_20260801`. The two toolsets can be declared together.


## Tool definition properties

Source: https://platform.claude.com/llms-full.txt#tool-definition-properties

Every tool in the `tools` array, including user-defined tools, accepts optional properties that control how the tool is loaded, who can call it, and how its inputs are validated. These properties compose: you can set `defer_loading` and `cache_control` and `strict` on the same tool.

| Property                | Purpose                                                                                                               | Available on                                                                                                                                                                                                                                                                                                                                                  | Detailed guide                                                                                                                                 |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `cache_control`         | Set a prompt-cache breakpoint at this tool definition                                                                 | All tools (on `computer_toolset_20260801` and `browser_toolset_20260801`, set it on the toolset entry itself, not inside member `configs`)                                                                                                                                                                                                                    | [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)                                                         |
| `strict`                | Guarantee schema validation on tool names and inputs                                                                  | All tools except `mcp_toolset`, `computer_toolset_20260801`, and `browser_toolset_20260801`                                                                                                                                                                                                                                                                   | [Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use)                                               |
| `defer_loading`         | Exclude the tool from the initial system prompt; load it on demand when tool search returns a `tool_reference` for it | All tools (for `mcp_toolset`, see [tool configuration](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector#mcp-toolset-configuration)). On the computer use and browser use toolsets, set it per member inside `configs`; see [Client toolsets](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets). | [Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)                                             |
| `allowed_callers`       | Restrict which callers can call the tool                                                                              | All tools except `mcp_toolset` (on `computer_toolset_20260801` and `browser_toolset_20260801`, only `["direct"]` is accepted; see [Client toolsets](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference#client-toolsets))                                                                                                            | [Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#the-allowed-callers-field) |
| `input_examples`        | Provide example input objects to help Claude understand how to call the tool                                          | User-defined and Anthropic-schema client tools, except `computer_toolset_20260801` and `browser_toolset_20260801`. Not available on server tools.                                                                                                                                                                                                             | [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools#providing-tool-use-examples)                         |
| `eager_input_streaming` | Enable fine-grained input streaming (`true`) or keep standard buffered streaming (`false`) for this tool              | User-defined tools only                                                                                                                                                                                                                                                                                                                                       | [Fine-grained tool streaming](https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming)                       |

### `allowed_callers` values

`allowed_callers` is an array that accepts any combination of:

| Value                       | Meaning                                                                                                           |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `"direct"`                  | The model can call this tool directly in a `tool_use` block. This is the default if `allowed_callers` is omitted. |
| `"code_execution_20260120"` | Code running inside a `code_execution_20260120` or later sandbox can call this tool.                              |

Both `"code_execution_20260120"` and `"code_execution_20260521"` are accepted in `allowed_callers` and are interchangeable: a request using either code-execution tool version satisfies tools that list either caller. Response blocks always tag the caller as `code_execution_20260120` regardless of which version the request declared.

Omitting `"direct"` from the array (for example, `"allowed_callers": ["code_execution_20260120"]`) guides Claude to call the tool only from within code execution. The response's `tool_use` block includes a `caller` field that identifies which caller called the tool. See [Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#the-allowed-callers-field) for the full treatment, including the `caller` response shape and error behavior.

### `defer_loading` and prompt caching

Tools with `defer_loading: true` are stripped from the rendered tools section before the cache key is computed. They don't appear in the system-prompt prefix at all. When tool search discovers a deferred tool and returns a `tool_reference` for it, the tool's full definition is expanded inline at that point in the conversation body, not in the prefix.

This means `defer_loading: true` preserves your prompt cache. You can add deferred tools to a request without invalidating an existing cache entry, and the cache remains valid across the turn where the tool is discovered and the turn where it's called.

To learn how to combine `defer_loading` with `cache_control` breakpoints, see the [Tool search tool prompt caching guidance](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#prompt-caching).


---
title: Tool use with prompt caching
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching
description: Cache tool definitions across turns and understand what invalidates your cache.
---

This page covers prompt caching for tool definitions: where to place `cache_control` breakpoints, how `defer_loading` preserves your cache, and what invalidates it. For general prompt caching, see [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).


## cache\_control on tool definitions

Source: https://platform.claude.com/llms-full.txt#cache-control-on-tool-definitions

Place `cache_control: {"type": "ephemeral"}` on the last tool in your `tools` array. This caches the entire tool-definitions prefix, from the first tool through the marked breakpoint:

For `mcp_toolset`, the `cache_control` breakpoint lands on the last tool in the set. You don't control tool order within an MCP toolset, so place the breakpoint on the `mcp_toolset` entry itself and the API applies it to the final expanded tool.

The [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) toolset entries follow the same rule: place `cache_control` on the toolset entry itself, and the breakpoint lands after the toolset's definition. It isn't accepted inside a member's `configs` entry, because the toolset's members load as one definition. Within a [batch action](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#batch-actions), a `cache_control` marker on any of the turn's member `tool_use` or `tool_result` blocks is accepted and takes effect at the end of that batch, so several markers in one batch act as a single breakpoint. Each marker still counts toward the request's limit of [four breakpoints](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#when-to-use-multiple-breakpoints), so use one per turn.


## defer\_loading and cache preservation

Source: https://platform.claude.com/llms-full.txt#defer-loading-and-cache-preservation

Deferred tools are not included in the system-prompt prefix. When the model discovers a deferred tool through [tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool), the definition is appended inline as a `tool_reference` block in the conversation history. The prefix is untouched, so prompt caching is preserved.

This means adding tools dynamically through tool search does not break your cache. You can start a conversation with a small set of always-loaded tools (cached), let the model discover additional tools as needed, and keep the same cache hit across every turn.

`defer_loading` also acts independently of grammar construction for [strict mode](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use). The grammar builds from the full toolset regardless of which tools are deferred, so prompt caching and grammar caching are both preserved when tools load dynamically.


## What invalidates your cache

Source: https://platform.claude.com/llms-full.txt#what-invalidates-your-cache

The cache follows a prefix hierarchy (`tools` → `system` → `messages`), so a change at one level invalidates that level and everything after it:

| Change                               | Invalidates                                                                                                                                                                                                              |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Modifying tool definitions           | Entire cache (tools, system, messages)                                                                                                                                                                                   |
| Toggling web search or citations     | System and messages caches                                                                                                                                                                                               |
| Changing `tool_choice`               | Messages cache                                                                                                                                                                                                           |
| Changing `disable_parallel_tool_use` | Messages cache                                                                                                                                                                                                           |
| Toggling images present/absent       | Messages cache                                                                                                                                                                                                           |
| Changing thinking parameters         | Messages cache always; tool and system caches too on models that render the thinking configuration ahead of them ([details](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-and-prompt-caching)) |
| Changing `output_config.effort`      | Same as thinking parameters; setting the model's default explicitly is equivalent to omitting it                                                                                                                         |

<Note>
  If you need to vary `tool_choice` mid-conversation, consider placing cache breakpoints before the variation point.
</Note>


## Server tool results are cached automatically

Source: https://platform.claude.com/llms-full.txt#server-tool-results-are-cached-automatically

When your request has prompt caching enabled and Claude uses a [server tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools) such as web search, web fetch, or code execution, the API automatically places a cache breakpoint on the server tool result before running the next iteration of the agentic loop. This lets later iterations within the same request read the growing prefix from cache instead of reprocessing it.

This automatic breakpoint always uses the default 5-minute TTL, independent of any TTL you set on your own `cache_control` markers. In the response `usage`, these writes appear under `cache_creation.ephemeral_5m_input_tokens`, so you may see 5-minute cache writes even when every `cache_control` you set uses a 1-hour TTL.

This behavior only applies when your request already has at least one `cache_control` marker. Requests without prompt caching do not receive the automatic breakpoint.


## Per-tool interaction table

Source: https://platform.claude.com/llms-full.txt#per-tool-interaction-table

| Tool                                                                                                | Caching considerations                                                                                                                                                                                                                                         |
| --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)         | Enabling or disabling invalidates the system and messages caches                                                                                                                                                                                               |
| [Web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool)           | Enabling or disabling invalidates the system and messages caches                                                                                                                                                                                               |
| [Code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) | Container state is independent of prompt cache                                                                                                                                                                                                                 |
| [Tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)       | Discovered tools load as `tool_reference` blocks, preserving prefix cache                                                                                                                                                                                      |
| [Computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)     | Screenshot presence affects messages cache; `cache_control` goes on the toolset entry (see [cache\_control on tool definitions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching#cache-control-on-tool-definitions)) |
| [Browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool)       | Screenshot presence affects messages cache; `cache_control` goes on the toolset entry (see [cache\_control on tool definitions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching#cache-control-on-tool-definitions)) |
| [Text editor](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)       | Standard client tool, no special caching interaction                                                                                                                                                                                                           |
| [Bash](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool)                     | Standard client tool, no special caching interaction                                                                                                                                                                                                           |
| [Memory](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)                 | Standard client tool, no special caching interaction                                                                                                                                                                                                           |


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-47

<CardGroup cols={3}>
  <Card title="Prompt caching" icon="database" href="https://platform.claude.com/docs/en/build-with-claude/prompt-caching">
    Learn the full prompt caching model, including TTLs and pricing.
  </Card>

  <Card title="Tool search" icon="magnifying-glass" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool">
    Load tools on demand without breaking your cache.
  </Card>

  <Card title="Tool reference" icon="book" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference">
    Browse all available tools and their parameters.
  </Card>
</CardGroup>


### Context management

---
title: Build an orchestration mode
url: https://platform.claude.com/docs/en/build-with-claude/mid-conversation-effort-example
description: Build a session-level mode that grants standing consent for multiagent fan-out, switched on and off with mid-conversation system messages.
---

An orchestration mode is a session-level switch: when it is on, the model puts maximum thoroughness behind every substantive request, scouting the task itself and then fanning work out to parallel subagents by default. When it is off, the same orchestration tool goes back to per-request opt-in.

The mode is not an API parameter. It is built entirely from documented pieces:

1. **An effort level:** requests run at a documented [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) value such as `xhigh`. There is no hidden level above the ones on that page. This example sets effort at the top level of each request, which needs no beta header.
2. **A mode reminder:** a [mid-conversation system message](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages) tells the model the mode is active, with a one-line refresher every several turns and an exit notice when the mode is turned off. The top-level `system` field never changes, so the cached prefix stays intact.
3. **Standing consent in the tool description:** the orchestration tool's description states that while the mode is on, the model should author and run a workflow for every substantive task without asking first.

<Note>
  This example uses mid-conversation system messages; for the models and platforms that support them, see [Mid-conversation system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages). The fan-out itself multiplies token usage: a single request can spawn many subagent conversations, so reserve the mode for work that justifies the cost.
</Note>


## Set up the loop

Source: https://platform.claude.com/llms-full.txt#set-up-the-loop

The example is a single file. The constants control the effort level, the fan-out shape, and how often the mode refresher is re-sent. `MAX_CONCURRENT` caps how many subagents run at the same time (the PHP port is sequential and ignores it); `MAX_TOTAL_SUBTASKS` caps how many the model may queue in a single Workflow call. Splitting the two lets the model plan a large backlog without launching it all at once. The `DOC_TEST_MODE` check caps the loops to a single turn when that environment variable is set, so the automated docs harness can validate that the file compiles and finishes quickly without running the full orchestration; leave it unset when running the example yourself.

<CodeGroup>
  ```python Python
  import atexit
  import concurrent.futures
  import hashlib
  import json
  import os
  import shutil
  import subprocess
  import sys
  import tempfile
  import threading

  import anthropic

  client = anthropic.Anthropic()

  MODEL = "claude-opus-5"
  EFFORT = "xhigh"

  SYSTEM_PROMPT = "You are a helpful general-purpose agent. Answer the user's request directly."

  REQUEST_TIMEOUT_SECONDS = 600
  BASH_TIMEOUT_SECONDS = 60
  TOOL_RESULT_MAX_CHARS = 8000
  MAX_CONCURRENT = 10
  DOC_TEST_MODE = bool(os.environ.get("DOC_TEST_MODE"))
  MAX_TOTAL_SUBTASKS = 2 if DOC_TEST_MODE else 200
  MAX_SUBAGENT_TURNS = 1 if DOC_TEST_MODE else 15
  MAX_MAIN_TURNS = 1 if DOC_TEST_MODE else 30
  TURNS_BETWEEN_REFRESHERS = 10
  JOURNAL_PATH = os.environ.get("ORCH_JOURNAL") or "orchestration_journal.json"

typescript TypeScript
  import { exec } from "node:child_process";
  import { createHash } from "node:crypto";
  import { rmSync } from "node:fs";
  import { mkdtemp, readFile, rename, writeFile } from "node:fs/promises";
  import { tmpdir } from "node:os";
  import { join } from "node:path";
  import { promisify } from "node:util";

  import Anthropic from "@anthropic-ai/sdk";

  const client = new Anthropic();

  const MODEL = "claude-opus-5";
  const EFFORT = "xhigh";

  const SYSTEM_PROMPT =
    "You are a helpful general-purpose agent. Answer the user's request directly.";

  const REQUEST_TIMEOUT_SECONDS = 600;
  const BASH_TIMEOUT_SECONDS = 60;
  const TOOL_RESULT_MAX_CHARS = 8000;
  const MAX_CONCURRENT = 10;
  const DOC_TEST_MODE = Boolean(process.env.DOC_TEST_MODE);
  const MAX_TOTAL_SUBTASKS = DOC_TEST_MODE ? 2 : 200;
  const MAX_SUBAGENT_TURNS = DOC_TEST_MODE ? 1 : 15;
  const MAX_MAIN_TURNS = DOC_TEST_MODE ? 1 : 30;
  const TURNS_BETWEEN_REFRESHERS = 10;
  const JOURNAL_PATH = process.env.ORCH_JOURNAL || "orchestration_journal.json";

csharp C#
  using System.Diagnostics;
  using System.Security.Cryptography;
  using System.Text;
  using System.Text.Json;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  const Model model = Model.ClaudeOpus5;
  var effort = Effort.Xhigh;

  const string systemPrompt = "You are a helpful general-purpose agent. Answer the user's request directly.";

  const int requestTimeoutSeconds = 600;
  // The other ports stream with max_tokens 64000. This port uses non-streaming
  // Messages.Create, and the API rejects non-streaming requests at that size.
  // 8192 is the non-streaming ceiling for Opus 4.0 and 4.1 and a conservative
  // choice for newer Opus models.
  const int requestMaxTokens = 8192;
  const int bashTimeoutSeconds = 60;
  const int toolResultMaxChars = 8000;
  const int maxConcurrent = 10;
  var docTestMode = Environment.GetEnvironmentVariable("DOC_TEST_MODE") is { Length: > 0 };
  int maxTotalSubtasks = docTestMode ? 2 : 200;
  int maxSubagentTurns = docTestMode ? 1 : 15;
  int maxMainTurns = docTestMode ? 1 : 30;
  const int turnsBetweenRefreshers = 10;
  var journalPath = Environment.GetEnvironmentVariable("ORCH_JOURNAL") is { Length: > 0 } p ? p : "orchestration_journal.json";

go Go
  import (
  	"bytes"
  	"cmp"
  	"context"
  	"crypto/sha256"
  	"encoding/hex"
  	"encoding/json"
  	"errors"
  	"fmt"
  	"log"
  	"os"
  	"os/exec"
  	"path/filepath"
  	"strings"
  	"sync"
  	"time"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  var client = anthropic.NewClient()

  const (
  	modelID = anthropic.ModelClaudeOpus5
  	effort  = anthropic.OutputConfigEffortXhigh

  	systemPrompt = "You are a helpful general-purpose agent. Answer the user's request directly."

  	requestTimeoutSeconds  = 600
  	bashTimeoutSeconds     = 60
  	toolResultMaxChars     = 8000
  	maxConcurrent          = 10
  	turnsBetweenRefreshers = 10
  )

  var (
  	docTestMode      = os.Getenv("DOC_TEST_MODE") != ""
  	maxTotalSubtasks = ifTest(2, 200)
  	maxSubagentTurns = ifTest(1, 15)
  	maxMainTurns     = ifTest(1, 30)
  	journalPath      = cmp.Or(os.Getenv("ORCH_JOURNAL"), "orchestration_journal.json")
  )

  func ifTest(test, normal int) int {
  	if docTestMode {
  		return test
  	}
  	return normal
  }

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.JsonValue;
  import com.anthropic.core.RequestOptions;
  import com.anthropic.helpers.MessageAccumulator;
  import com.anthropic.models.messages.ContentBlock;
  import com.anthropic.models.messages.ContentBlockParam;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.MessageParam;
  import com.anthropic.models.messages.Model;
  import com.anthropic.models.messages.OutputConfig;
  import com.anthropic.models.messages.StopReason;
  import com.anthropic.models.messages.TextBlock;
  import com.anthropic.models.messages.Tool;
  import com.anthropic.models.messages.ToolBash20250124;
  import com.anthropic.models.messages.ToolResultBlockParam;
  import com.anthropic.models.messages.ToolUseBlock;
  import com.fasterxml.jackson.core.JsonProcessingException;
  import com.fasterxml.jackson.core.type.TypeReference;
  import com.fasterxml.jackson.databind.JsonNode;
  import com.fasterxml.jackson.databind.ObjectMapper;
  import java.io.IOException;
  import java.io.UncheckedIOException;
  import java.nio.charset.StandardCharsets;
  import java.nio.file.Files;
  import java.nio.file.Path;
  import java.nio.file.StandardCopyOption;
  import java.security.MessageDigest;
  import java.time.Duration;
  import java.util.ArrayList;
  import java.util.Comparator;
  import java.util.HashMap;
  import java.util.HexFormat;
  import java.util.List;
  import java.util.Map;
  import java.util.Objects;
  import java.util.Optional;
  import java.util.concurrent.Callable;
  import java.util.concurrent.CancellationException;
  import java.util.concurrent.CompletableFuture;
  import java.util.concurrent.ExecutionException;
  import java.util.concurrent.ExecutorService;
  import java.util.concurrent.Executors;
  import java.util.concurrent.Future;
  import java.util.concurrent.TimeUnit;
  import java.util.concurrent.locks.ReentrantLock;
  import java.util.stream.Collectors;
  import java.util.stream.IntStream;

  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  static final Model MODEL = Model.CLAUDE_OPUS_5;
  static final boolean DOC_TEST_MODE =
          !Objects.requireNonNullElse(System.getenv("DOC_TEST_MODE"), "").isEmpty();
  static final OutputConfig.Effort EFFORT = OutputConfig.Effort.XHIGH;

  static final String SYSTEM_PROMPT =
          "You are a helpful general-purpose agent. Answer the user's request directly.";

  static final int REQUEST_TIMEOUT_SECONDS = 600;
  static final RequestOptions REQUEST_OPTIONS =
          RequestOptions.builder().timeout(Duration.ofSeconds(REQUEST_TIMEOUT_SECONDS)).build();
  static final int BASH_TIMEOUT_SECONDS = 60;
  static final int TOOL_RESULT_MAX_CHARS = 8000;
  static final int MAX_CONCURRENT = 10;
  static final int MAX_TOTAL_SUBTASKS = DOC_TEST_MODE ? 2 : 200;
  static final int MAX_SUBAGENT_TURNS = DOC_TEST_MODE ? 1 : 15;
  static final int MAX_MAIN_TURNS = DOC_TEST_MODE ? 1 : 30;
  static final int TURNS_BETWEEN_REFRESHERS = 10;
  static final Path JOURNAL_PATH = Path.of(Optional.ofNullable(System.getenv("ORCH_JOURNAL"))
          .filter(s -> !s.isEmpty()).orElse("orchestration_journal.json"));

php PHP
  use Anthropic\Client;
  use Anthropic\Messages\TextBlock;
  use Anthropic\Messages\ToolUseBlock;

  $client = new Client();

  const MODEL = 'claude-opus-5';
  define('DOC_TEST_MODE', (string) getenv('DOC_TEST_MODE') !== '');
  const EFFORT = 'xhigh';

  const SYSTEM_PROMPT = 'You are a helpful general-purpose agent. Answer the user\'s request directly.';

  const REQUEST_TIMEOUT_SECONDS = 600;
  const BASH_TIMEOUT_SECONDS = 60;
  const TOOL_RESULT_MAX_CHARS = 8000;
  const MAX_CONCURRENT = 10;
  define('MAX_TOTAL_SUBTASKS', DOC_TEST_MODE ? 2 : 200);
  define('MAX_SUBAGENT_TURNS', DOC_TEST_MODE ? 1 : 15);
  define('MAX_MAIN_TURNS', DOC_TEST_MODE ? 1 : 30);
  const TURNS_BETWEEN_REFRESHERS = 10;
  define('JOURNAL_PATH', getenv('ORCH_JOURNAL') ?: 'orchestration_journal.json');

ruby Ruby
  require "anthropic"
  require "digest"
  require "fileutils"
  require "json"
  require "open3"
  require "tmpdir"

  CLIENT = Anthropic::Client.new

  MODEL = "claude-opus-5"
  EFFORT = :xhigh

  SYSTEM_PROMPT = "You are a helpful general-purpose agent. Answer the user's request directly."

  REQUEST_TIMEOUT_SECONDS = 600
  BASH_TIMEOUT_SECONDS = 60
  TOOL_RESULT_MAX_CHARS = 8000
  MAX_CONCURRENT = 10
  DOC_TEST_MODE = !ENV["DOC_TEST_MODE"].to_s.empty?
  MAX_TOTAL_SUBTASKS = DOC_TEST_MODE ? 2 : 200
  MAX_SUBAGENT_TURNS = DOC_TEST_MODE ? 1 : 15
  MAX_MAIN_TURNS = DOC_TEST_MODE ? 1 : 30
  TURNS_BETWEEN_REFRESHERS = 10
  JOURNAL_PATH = ENV["ORCH_JOURNAL"].to_s.empty? ? "orchestration_journal.json" : ENV["ORCH_JOURNAL"]
  ```
</CodeGroup>


## Define the mode reminders

Source: https://platform.claude.com/llms-full.txt#define-the-mode-reminders

The reminders are short on purpose. They flip the mode and point at the tool description, where the heavyweight instructions live. The full text is sent once when the mode turns on, the refresher is re-sent only after several user turns, and the exit notice is sent once when the mode turns off.

<CodeGroup>
  ```python Python
  MODE_ENTER = (
      "Orchestration mode is on: optimize for the most exhaustive, correct answer rather than "
      "the fastest one. Use the Workflow tool on every substantive task, sized to the problem's "
      "natural decomposition rather than the maximum the tool allows. See the Workflow tool's "
      "description for standing consent, granularity guidance, and quality patterns. Work solo "
      "only on conversational or trivial turns."
  )
  MODE_REFRESH = (
      "Orchestration mode is still on. Use the Workflow tool; see its standing consent section."
  )
  MODE_EXIT = (
      "Orchestration mode is off. The Workflow tool's standard opt-in rule applies again."
  )

typescript TypeScript
  const MODE_ENTER =
    "Orchestration mode is on: optimize for the most exhaustive, correct answer rather than " +
    "the fastest one. Use the Workflow tool on every substantive task, sized to the problem's " +
    "natural decomposition rather than the maximum the tool allows. See the Workflow tool's " +
    "description for standing consent, granularity guidance, and quality patterns. Work solo " +
    "only on conversational or trivial turns.";
  const MODE_REFRESH =
    "Orchestration mode is still on. Use the Workflow tool; see its standing consent section.";
  const MODE_EXIT =
    "Orchestration mode is off. The Workflow tool's standard opt-in rule applies again.";

csharp C#
  const string modeEnter =
      "Orchestration mode is on: optimize for the most exhaustive, correct answer rather than "
      + "the fastest one. Use the Workflow tool on every substantive task, sized to the problem's "
      + "natural decomposition rather than the maximum the tool allows. See the Workflow tool's "
      + "description for standing consent, granularity guidance, and quality patterns. Work solo "
      + "only on conversational or trivial turns.";
  const string modeRefresh =
      "Orchestration mode is still on. Use the Workflow tool; see its standing consent section.";
  const string modeExit =
      "Orchestration mode is off. The Workflow tool's standard opt-in rule applies again.";

go Go
  const (
  	modeEnter = "Orchestration mode is on: optimize for the most exhaustive, correct answer rather than " +
  		"the fastest one. Use the Workflow tool on every substantive task, sized to the problem's " +
  		"natural decomposition rather than the maximum the tool allows. See the Workflow tool's " +
  		"description for standing consent, granularity guidance, and quality patterns. Work solo " +
  		"only on conversational or trivial turns."
  	modeRefresh = "Orchestration mode is still on. Use the Workflow tool; see its standing consent section."
  	modeExit    = "Orchestration mode is off. The Workflow tool's standard opt-in rule applies again."
  )

java Java
  static final String MODE_ENTER =
          "Orchestration mode is on: optimize for the most exhaustive, correct answer rather than "
                  + "the fastest one. Use the Workflow tool on every substantive task, sized to the problem's "
                  + "natural decomposition rather than the maximum the tool allows. See the Workflow tool's "
                  + "description for standing consent, granularity guidance, and quality patterns. Work solo "
                  + "only on conversational or trivial turns.";
  static final String MODE_REFRESH =
          "Orchestration mode is still on. Use the Workflow tool; see its standing consent section.";
  static final String MODE_EXIT =
          "Orchestration mode is off. The Workflow tool's standard opt-in rule applies again.";

php PHP
  const MODE_ENTER =
      'Orchestration mode is on: optimize for the most exhaustive, correct answer rather than '
      . 'the fastest one. Use the Workflow tool on every substantive task, sized to the problem\'s '
      . 'natural decomposition rather than the maximum the tool allows. See the Workflow tool\'s '
      . 'description for standing consent, granularity guidance, and quality patterns. Work solo '
      . 'only on conversational or trivial turns.';
  const MODE_REFRESH =
      'Orchestration mode is still on. Use the Workflow tool; see its standing consent section.';
  const MODE_EXIT =
      'Orchestration mode is off. The Workflow tool\'s standard opt-in rule applies again.';

ruby Ruby
  MODE_ENTER =
    "Orchestration mode is on: optimize for the most exhaustive, correct answer rather than " \
    "the fastest one. Use the Workflow tool on every substantive task, sized to the problem's " \
    "natural decomposition rather than the maximum the tool allows. See the Workflow tool's " \
    "description for standing consent, granularity guidance, and quality patterns. Work solo " \
    "only on conversational or trivial turns."
  MODE_REFRESH =
    "Orchestration mode is still on. Use the Workflow tool; see its standing consent section."
  MODE_EXIT =
    "Orchestration mode is off. The Workflow tool's standard opt-in rule applies again."
  ```
</CodeGroup>


## Grant standing consent in the tool description

Source: https://platform.claude.com/llms-full.txt#grant-standing-consent-in-the-tool-description

The Workflow tool carries the real behavioral contract: the opt-in rule, the standing consent that applies while the mode is on, granularity guidance for sizing the fan-out, and the quality patterns the model can reach for (a verification wave, a completeness critic, multiphase sequencing). Subagents also get a `report_findings` tool so their results come back as structured JSON instead of prose, and the bash tool is the Anthropic-defined `bash_20250124` tool run locally.

<CodeGroup>
  ```python Python
  WORKFLOW_TOOL = {
      "name": "Workflow",
      "description": (
          "Orchestrate a multiagent workflow: split a large task into independent subtasks "
          "and run them as parallel agents, then collect their results.\n\n"
          "Opt-in: only use this tool when the user explicitly asks for a workflow, or when a "
          "system message confirms that orchestration mode is on.\n\n"
          "Quality patterns: adversarial verification (a second wave of agents checks the first "
          "wave's findings against the source), a completeness critic (one agent hunts for what "
          "the others missed), and multiphase sequencing (understand, design, implement, and "
          "review as separate workflow calls, reading results between phases). A useful default "
          "is hybrid: scout inline first to discover the work-list, then fan out over it.\n\n"
          "Granularity: scope each subtask to a distinct concern, component, or question rather "
          "than per line or per file section. Scale the count to what the user asked for: a "
          "focused review of a module of a few hundred lines rarely needs more than about ten "
          "subtasks; a broad audit of a large codebase can justify more.\n\n"
          "Standing consent: while a system message confirms orchestration mode is on, that "
          "opt-in is standing. Author and run a workflow for every substantive task by default, "
          "and lean toward verifying findings adversarially. Work solo only on conversational "
          "turns or trivial mechanical edits. When a system message says the mode is off, "
          "revert to the opt-in rule above."
      ),
      "input_schema": {
          "type": "object",
          "properties": {
              "subtasks": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "Independent subtask prompts to run as parallel agents",
              }
          },
          "required": ["subtasks"],
      },
  }

  BASH_TOOL = {"type": "bash_20250124", "name": "bash"}

  REPORT_TOOL = {
      "name": "report_findings",
      "description": (
          "Report the final findings for your subtask. Call this exactly once, when you are "
          "done investigating; it ends your task."
      ),
      "input_schema": {
          "type": "object",
          "properties": {
              "summary": {"type": "string", "description": "Two or three sentences of synthesis"},
              "findings": {
                  "type": "array",
                  "items": {
                      "type": "object",
                      "properties": {
                          "claim": {"type": "string", "description": "The finding, one sentence"},
                          "evidence": {
                              "type": "string",
                              "description": "How it was verified (file, line, or command output)",
                          },
                          "severity": {"type": "string", "enum": ["high", "medium", "low", "info"]},
                      },
                      "required": ["claim", "evidence", "severity"],
                  },
              },
          },
          "required": ["summary", "findings"],
      },
  }

typescript TypeScript
  const WORKFLOW_TOOL: Anthropic.Tool = {
    name: "Workflow",
    description:
      "Orchestrate a multiagent workflow: split a large task into independent subtasks " +
      "and run them as parallel agents, then collect their results.\n\n" +
      "Opt-in: only use this tool when the user explicitly asks for a workflow, or when a " +
      "system message confirms that orchestration mode is on.\n\n" +
      "Quality patterns: adversarial verification (a second wave of agents checks the first " +
      "wave's findings against the source), a completeness critic (one agent hunts for what " +
      "the others missed), and multiphase sequencing (understand, design, implement, and " +
      "review as separate workflow calls, reading results between phases). A useful default " +
      "is hybrid: scout inline first to discover the work-list, then fan out over it.\n\n" +
      "Granularity: scope each subtask to a distinct concern, component, or question rather " +
      "than per line or per file section. Scale the count to what the user asked for: a " +
      "focused review of a module of a few hundred lines rarely needs more than about ten " +
      "subtasks; a broad audit of a large codebase can justify more.\n\n" +
      "Standing consent: while a system message confirms orchestration mode is on, that " +
      "opt-in is standing. Author and run a workflow for every substantive task by default, " +
      "and lean toward verifying findings adversarially. Work solo only on conversational " +
      "turns or trivial mechanical edits. When a system message says the mode is off, " +
      "revert to the opt-in rule above.",
    input_schema: {
      type: "object",
      properties: {
        subtasks: {
          type: "array",
          items: { type: "string" },
          description: "Independent subtask prompts to run as parallel agents",
        },
      },
      required: ["subtasks"],
    },
  };

  const BASH_TOOL: Anthropic.ToolBash20250124 = { type: "bash_20250124", name: "bash" };

  const REPORT_TOOL: Anthropic.Tool = {
    name: "report_findings",
    description:
      "Report the final findings for your subtask. Call this exactly once, when you are " +
      "done investigating; it ends your task.",
    input_schema: {
      type: "object",
      properties: {
        summary: { type: "string", description: "Two or three sentences of synthesis" },
        findings: {
          type: "array",
          items: {
            type: "object",
            properties: {
              claim: { type: "string", description: "The finding, one sentence" },
              evidence: {
                type: "string",
                description: "How it was verified (file, line, or command output)",
              },
              severity: { type: "string", enum: ["high", "medium", "low", "info"] },
            },
            required: ["claim", "evidence", "severity"],
          },
        },
      },
      required: ["summary", "findings"],
    },
  };

csharp C#
  Tool workflowTool = new()
  {
      Name = "Workflow",
      Description =
          "Orchestrate a multiagent workflow: split a large task into independent subtasks "
          + "and run them as parallel agents, then collect their results.\n\n"
          + "Opt-in: only use this tool when the user explicitly asks for a workflow, or when a "
          + "system message confirms that orchestration mode is on.\n\n"
          + "Quality patterns: adversarial verification (a second wave of agents checks the first "
          + "wave's findings against the source), a completeness critic (one agent hunts for what "
          + "the others missed), and multiphase sequencing (understand, design, implement, and "
          + "review as separate workflow calls, reading results between phases). A useful default "
          + "is hybrid: scout inline first to discover the work-list, then fan out over it.\n\n"
          + "Granularity: scope each subtask to a distinct concern, component, or question rather "
          + "than per line or per file section. Scale the count to what the user asked for: a "
          + "focused review of a module of a few hundred lines rarely needs more than about ten "
          + "subtasks; a broad audit of a large codebase can justify more.\n\n"
          + "Standing consent: while a system message confirms orchestration mode is on, that "
          + "opt-in is standing. Author and run a workflow for every substantive task by default, "
          + "and lean toward verifying findings adversarially. Work solo only on conversational "
          + "turns or trivial mechanical edits. When a system message says the mode is off, "
          + "revert to the opt-in rule above.",
      InputSchema = new InputSchema
      {
          Properties = new Dictionary<string, JsonElement>
          {
              ["subtasks"] = JsonSerializer.SerializeToElement(new
              {
                  type = "array",
                  items = new { type = "string" },
                  description = "Independent subtask prompts to run as parallel agents",
              }),
          },
          Required = ["subtasks"],
      },
  };

  ToolBash20250124 bashTool = new();

  Tool reportTool = new()
  {
      Name = "report_findings",
      Description =
          "Report the final findings for your subtask. Call this exactly once, when you are "
          + "done investigating; it ends your task.",
      InputSchema = new InputSchema
      {
          Properties = new Dictionary<string, JsonElement>
          {
              ["summary"] = JsonSerializer.SerializeToElement(new
              {
                  type = "string",
                  description = "Two or three sentences of synthesis",
              }),
              ["findings"] = JsonSerializer.SerializeToElement(new
              {
                  type = "array",
                  items = new
                  {
                      type = "object",
                      properties = new
                      {
                          claim = new { type = "string", description = "The finding, one sentence" },
                          evidence = new
                          {
                              type = "string",
                              description = "How it was verified (file, line, or command output)",
                          },
                          severity = new { type = "string", @enum = new[] { "high", "medium", "low", "info" } },
                      },
                      required = new[] { "claim", "evidence", "severity" },
                  },
              }),
          },
          Required = ["summary", "findings"],
      },
  };

go Go
  var workflowTool = anthropic.ToolUnionParam{
  	OfTool: &anthropic.ToolParam{
  		Name: "Workflow",
  		Description: anthropic.String("Orchestrate a multiagent workflow: split a large task into independent subtasks " +
  			"and run them as parallel agents, then collect their results.\n\n" +
  			"Opt-in: only use this tool when the user explicitly asks for a workflow, or when a " +
  			"system message confirms that orchestration mode is on.\n\n" +
  			"Quality patterns: adversarial verification (a second wave of agents checks the first " +
  			"wave's findings against the source), a completeness critic (one agent hunts for what " +
  			"the others missed), and multiphase sequencing (understand, design, implement, and " +
  			"review as separate workflow calls, reading results between phases). A useful default " +
  			"is hybrid: scout inline first to discover the work-list, then fan out over it.\n\n" +
  			"Granularity: scope each subtask to a distinct concern, component, or question rather " +
  			"than per line or per file section. Scale the count to what the user asked for: a " +
  			"focused review of a module of a few hundred lines rarely needs more than about ten " +
  			"subtasks; a broad audit of a large codebase can justify more.\n\n" +
  			"Standing consent: while a system message confirms orchestration mode is on, that " +
  			"opt-in is standing. Author and run a workflow for every substantive task by default, " +
  			"and lean toward verifying findings adversarially. Work solo only on conversational " +
  			"turns or trivial mechanical edits. When a system message says the mode is off, " +
  			"revert to the opt-in rule above."),
  		InputSchema: anthropic.ToolInputSchemaParam{
  			Properties: map[string]any{
  				"subtasks": map[string]any{
  					"type":        "array",
  					"items":       map[string]any{"type": "string"},
  					"description": "Independent subtask prompts to run as parallel agents",
  				},
  			},
  			Required: []string{"subtasks"},
  		},
  	},
  }

  var bashTool = anthropic.ToolUnionParam{
  	OfBashTool20250124: &anthropic.ToolBash20250124Param{},
  }

  var reportTool = anthropic.ToolUnionParam{
  	OfTool: &anthropic.ToolParam{
  		Name: "report_findings",
  		Description: anthropic.String("Report the final findings for your subtask. Call this exactly once, when you are " +
  			"done investigating; it ends your task."),
  		InputSchema: anthropic.ToolInputSchemaParam{
  			Properties: map[string]any{
  				"summary": map[string]any{"type": "string", "description": "Two or three sentences of synthesis"},
  				"findings": map[string]any{
  					"type": "array",
  					"items": map[string]any{
  						"type": "object",
  						"properties": map[string]any{
  							"claim": map[string]any{"type": "string", "description": "The finding, one sentence"},
  							"evidence": map[string]any{
  								"type":        "string",
  								"description": "How it was verified (file, line, or command output)",
  							},
  							"severity": map[string]any{"type": "string", "enum": []string{"high", "medium", "low", "info"}},
  						},
  						"required": []string{"claim", "evidence", "severity"},
  					},
  				},
  			},
  			Required: []string{"summary", "findings"},
  		},
  	},
  }

java Java
  static final Tool WORKFLOW_TOOL = Tool.builder()
          .name("Workflow")
          .description("Orchestrate a multiagent workflow: split a large task into independent subtasks "
                  + "and run them as parallel agents, then collect their results.\n\n"
                  + "Opt-in: only use this tool when the user explicitly asks for a workflow, or when a "
                  + "system message confirms that orchestration mode is on.\n\n"
                  + "Quality patterns: adversarial verification (a second wave of agents checks the first "
                  + "wave's findings against the source), a completeness critic (one agent hunts for what "
                  + "the others missed), and multiphase sequencing (understand, design, implement, and "
                  + "review as separate workflow calls, reading results between phases). A useful default "
                  + "is hybrid: scout inline first to discover the work-list, then fan out over it.\n\n"
                  + "Granularity: scope each subtask to a distinct concern, component, or question rather "
                  + "than per line or per file section. Scale the count to what the user asked for: a "
                  + "focused review of a module of a few hundred lines rarely needs more than about ten "
                  + "subtasks; a broad audit of a large codebase can justify more.\n\n"
                  + "Standing consent: while a system message confirms orchestration mode is on, that "
                  + "opt-in is standing. Author and run a workflow for every substantive task by default, "
                  + "and lean toward verifying findings adversarially. Work solo only on conversational "
                  + "turns or trivial mechanical edits. When a system message says the mode is off, "
                  + "revert to the opt-in rule above.")
          .inputSchema(Tool.InputSchema.builder()
                  .properties(JsonValue.from(Map.of(
                          "subtasks", Map.of(
                                  "type", "array",
                                  "items", Map.of("type", "string"),
                                  "description", "Independent subtask prompts to run as parallel agents"))))
                  .putAdditionalProperty("required", JsonValue.from(List.of("subtasks")))
                  .build())
          .build();

  static final ToolBash20250124 BASH_TOOL = ToolBash20250124.builder().build();

  static final Tool REPORT_TOOL = Tool.builder()
          .name("report_findings")
          .description("Report the final findings for your subtask. Call this exactly once, when you are "
                  + "done investigating; it ends your task.")
          .inputSchema(Tool.InputSchema.builder()
                  .properties(JsonValue.from(Map.of(
                          "summary", Map.of("type", "string", "description", "Two or three sentences of synthesis"),
                          "findings", Map.of(
                                  "type", "array",
                                  "items", Map.of(
                                          "type", "object",
                                          "properties", Map.of(
                                                  "claim", Map.of(
                                                          "type", "string",
                                                          "description", "The finding, one sentence"),
                                                  "evidence", Map.of(
                                                          "type", "string",
                                                          "description", "How it was verified (file, line, or command output)"),
                                                  "severity", Map.of(
                                                          "type", "string",
                                                          "enum", List.of("high", "medium", "low", "info"))),
                                          "required", List.of("claim", "evidence", "severity"))))))
                  .putAdditionalProperty("required", JsonValue.from(List.of("summary", "findings")))
                  .build())
          .build();

php PHP
  const WORKFLOW_TOOL = [
      'name' => 'Workflow',
      'description' =>
          'Orchestrate a multiagent workflow: split a large task into independent subtasks '
          . "and run them as parallel agents, then collect their results.\n\n"
          . 'Opt-in: only use this tool when the user explicitly asks for a workflow, or when a '
          . "system message confirms that orchestration mode is on.\n\n"
          . 'Quality patterns: adversarial verification (a second wave of agents checks the first '
          . 'wave\'s findings against the source), a completeness critic (one agent hunts for what '
          . 'the others missed), and multiphase sequencing (understand, design, implement, and '
          . 'review as separate workflow calls, reading results between phases). A useful default '
          . "is hybrid: scout inline first to discover the work-list, then fan out over it.\n\n"
          . 'Granularity: scope each subtask to a distinct concern, component, or question rather '
          . 'than per line or per file section. Scale the count to what the user asked for: a '
          . 'focused review of a module of a few hundred lines rarely needs more than about ten '
          . "subtasks; a broad audit of a large codebase can justify more.\n\n"
          . 'Standing consent: while a system message confirms orchestration mode is on, that '
          . 'opt-in is standing. Author and run a workflow for every substantive task by default, '
          . 'and lean toward verifying findings adversarially. Work solo only on conversational '
          . 'turns or trivial mechanical edits. When a system message says the mode is off, '
          . 'revert to the opt-in rule above.',
      'input_schema' => [
          'type' => 'object',
          'properties' => [
              'subtasks' => [
                  'type' => 'array',
                  'items' => ['type' => 'string'],
                  'description' => 'Independent subtask prompts to run as parallel agents',
              ],
          ],
          'required' => ['subtasks'],
      ],
  ];

  const BASH_TOOL = ['type' => 'bash_20250124', 'name' => 'bash'];

  const REPORT_TOOL = [
      'name' => 'report_findings',
      'description' =>
          'Report the final findings for your subtask. Call this exactly once, when you are '
          . 'done investigating; it ends your task.',
      'input_schema' => [
          'type' => 'object',
          'properties' => [
              'summary' => ['type' => 'string', 'description' => 'Two or three sentences of synthesis'],
              'findings' => [
                  'type' => 'array',
                  'items' => [
                      'type' => 'object',
                      'properties' => [
                          'claim' => ['type' => 'string', 'description' => 'The finding, one sentence'],
                          'evidence' => [
                              'type' => 'string',
                              'description' => 'How it was verified (file, line, or command output)',
                          ],
                          'severity' => ['type' => 'string', 'enum' => ['high', 'medium', 'low', 'info']],
                      ],
                      'required' => ['claim', 'evidence', 'severity'],
                  ],
              ],
          ],
          'required' => ['summary', 'findings'],
      ],
  ];

ruby Ruby
  WORKFLOW_TOOL = {
    name: "Workflow",
    description:
      "Orchestrate a multiagent workflow: split a large task into independent subtasks " \
      "and run them as parallel agents, then collect their results.\n\n" \
      "Opt-in: only use this tool when the user explicitly asks for a workflow, or when a " \
      "system message confirms that orchestration mode is on.\n\n" \
      "Quality patterns: adversarial verification (a second wave of agents checks the first " \
      "wave's findings against the source), a completeness critic (one agent hunts for what " \
      "the others missed), and multiphase sequencing (understand, design, implement, and " \
      "review as separate workflow calls, reading results between phases). A useful default " \
      "is hybrid: scout inline first to discover the work-list, then fan out over it.\n\n" \
      "Granularity: scope each subtask to a distinct concern, component, or question rather " \
      "than per line or per file section. Scale the count to what the user asked for: a " \
      "focused review of a module of a few hundred lines rarely needs more than about ten " \
      "subtasks; a broad audit of a large codebase can justify more.\n\n" \
      "Standing consent: while a system message confirms orchestration mode is on, that " \
      "opt-in is standing. Author and run a workflow for every substantive task by default, " \
      "and lean toward verifying findings adversarially. Work solo only on conversational " \
      "turns or trivial mechanical edits. When a system message says the mode is off, " \
      "revert to the opt-in rule above.",
    input_schema: {
      type: "object",
      properties: {
        subtasks: {
          type: "array",
          items: {type: "string"},
          description: "Independent subtask prompts to run as parallel agents"
        }
      },
      required: ["subtasks"]
    }
  }.freeze

  BASH_TOOL = {type: "bash_20250124", name: "bash"}.freeze

  REPORT_TOOL = {
    name: "report_findings",
    description:
      "Report the final findings for your subtask. Call this exactly once, when you are " \
      "done investigating; it ends your task.",
    input_schema: {
      type: "object",
      properties: {
        summary: {type: "string", description: "Two or three sentences of synthesis"},
        findings: {
          type: "array",
          items: {
            type: "object",
            properties: {
              claim: {type: "string", description: "The finding, one sentence"},
              evidence: {
                type: "string",
                description: "How it was verified (file, line, or command output)"
              },
              severity: {type: "string", enum: ["high", "medium", "low", "info"]}
            },
            required: ["claim", "evidence", "severity"]
          }
        }
      },
      required: ["summary", "findings"]
    }
  }.freeze
  ```
</CodeGroup>


## Run the bash tool locally

Source: https://platform.claude.com/llms-full.txt#run-the-bash-tool-locally

The bash handler runs the requested command with a timeout, captures combined stdout and stderr, and truncates the result so a runaway command can't flood the context window. Commands run in the directory you launch the example from, so pointing it at a project means starting it there; when `DOC_TEST_MODE` is set, the harness instead gives bash a small throwaway fixture directory that is removed on exit. There is no sandbox here: the command runs with the permissions of the process that launched the example. For clarity this example runs each call in a fresh subshell rather than maintaining the persistent session the `bash_20250124` contract describes; a production agent should back the tool with a long-lived shell so that working directory, environment, and the `restart` action behave as documented.

<CodeGroup>
  ```python Python
  # Run bash where the example was launched. In DOC_TEST_MODE the docs harness
  # points it at a throwaway fixture directory instead, removed on exit.
  if DOC_TEST_MODE:
      WORK_DIR = tempfile.mkdtemp(prefix="orchestration-")
      atexit.register(shutil.rmtree, WORK_DIR, ignore_errors=True)
      with open(os.path.join(WORK_DIR, "sample.py"), "w") as fixture:
          fixture.write(
              "def fib(n):\n"
              "    return n if n < 2 else fib(n - 1) + fib(n - 2)\n\n"
              "print(fib(10))\n"
          )
  else:
      WORK_DIR = os.getcwd()


  def run_bash(command: str) -> tuple[str, bool]:
      """Run a shell command and return (output, is_error). No sandbox: example code only."""
      print(f"[bash] {command}", file=sys.stderr)
      try:
          proc = subprocess.run(
              ["bash", "-c", command],
              cwd=WORK_DIR,
              capture_output=True,
              text=True,
              errors="replace",
              timeout=BASH_TIMEOUT_SECONDS,
          )
      except subprocess.TimeoutExpired:
          return f"command timed out after {BASH_TIMEOUT_SECONDS}s", True
      output = (proc.stdout + proc.stderr).strip() or "(no output)"
      if len(output) > TOOL_RESULT_MAX_CHARS:
          output = output[:TOOL_RESULT_MAX_CHARS] + f"\n(truncated at {TOOL_RESULT_MAX_CHARS} chars)"
      if proc.returncode != 0:
          output = f"(exit code {proc.returncode})\n{output}"
      return output, proc.returncode != 0


  def handle_bash_block(block) -> tuple[str, bool]:
      if block.input.get("restart") is True:
          return "Shell restarted.", False
      command = block.input.get("command")
      if not isinstance(command, str) or not command:
          return "bash error: no command was provided.", True
      return run_bash(command)

typescript TypeScript
  const execShell = promisify(exec);

  // Run bash where the example was launched. In DOC_TEST_MODE the docs harness
  // points it at a throwaway fixture directory instead, removed on exit.
  const WORK_DIR = DOC_TEST_MODE
    ? await mkdtemp(join(tmpdir(), "orchestration-"))
    : process.cwd();
  if (DOC_TEST_MODE) {
    await writeFile(
      join(WORK_DIR, "sample.py"),
      "def fib(n):\n" +
        "    return n if n < 2 else fib(n - 1) + fib(n - 2)\n\n" +
        "print(fib(10))\n",
    );
    process.on("exit", () => rmSync(WORK_DIR, { recursive: true, force: true }));
  }

  // Run a shell command and return its output. No sandbox: example code only.
  async function runBash(command: string): Promise<{ output: string; isError: boolean }> {
    console.error(`[bash] ${command}`);
    let stdout = "";
    let stderr = "";
    let exitCode = 0;
    try {
      ({ stdout, stderr } = await execShell(command, {
        shell: "/bin/bash",
        cwd: WORK_DIR,
        timeout: BASH_TIMEOUT_SECONDS * 1000,
        maxBuffer: 16 * 1024 * 1024,
      }));
    } catch (error) {
      const failure = error as {
        stdout?: string;
        stderr?: string;
        code?: number | string;
        killed?: boolean;
      };
      if (failure.killed && failure.code !== "ERR_CHILD_PROCESS_STDIO_MAXBUFFER") {
        return { output: `command timed out after ${BASH_TIMEOUT_SECONDS}s`, isError: true };
      }
      stdout = failure.stdout ?? "";
      stderr = failure.stderr ?? "";
      exitCode = typeof failure.code === "number" ? failure.code : 1;
    }
    let output = (stdout + stderr).trim() || "(no output)";
    const codePoints = [...output];
    if (codePoints.length > TOOL_RESULT_MAX_CHARS) {
      output =
        codePoints.slice(0, TOOL_RESULT_MAX_CHARS).join("") +
        `\n(truncated at ${TOOL_RESULT_MAX_CHARS} chars)`;
    }
    if (exitCode !== 0) {
      output = `(exit code ${exitCode})\n${output}`;
    }
    return { output, isError: exitCode !== 0 };
  }

  async function handleBashBlock(
    block: Anthropic.ToolUseBlock,
  ): Promise<{ output: string; isError: boolean }> {
    const input = block.input as { command?: string; restart?: boolean };
    if (input.restart === true) {
      return { output: "Shell restarted.", isError: false };
    }
    if (!input.command) {
      return { output: "bash error: no command was provided.", isError: true };
    }
    return runBash(input.command);
  }

csharp C#
  // Run bash where the example was launched. In DOC_TEST_MODE the docs harness
  // points it at a throwaway fixture directory instead, removed on exit.
  var workDir = Environment.CurrentDirectory;
  if (docTestMode)
  {
      workDir = Directory.CreateTempSubdirectory("orchestration-").FullName;
      File.WriteAllText(Path.Combine(workDir, "sample.py"),
          "def fib(n):\n" +
          "    return n if n < 2 else fib(n - 1) + fib(n - 2)\n\n" +
          "print(fib(10))\n");
      var fixtureDir = workDir;
      AppDomain.CurrentDomain.ProcessExit += (_, _) =>
      {
          try { Directory.Delete(fixtureDir, recursive: true); }
          catch { /* Best-effort cleanup; the OS tmp sweeper handles leftovers. */ }
      };
  }

  // Run a shell command and return its output plus an error flag. No sandbox: example code only.
  async Task<(string Output, bool IsError)> RunBash(string command)
  {
      Console.Error.WriteLine($"[bash] {command}");
      using var process = Process.Start(new ProcessStartInfo("bash")
      {
          ArgumentList = { "-c", command },
          WorkingDirectory = workDir,
          RedirectStandardOutput = true,
          RedirectStandardError = true,
      });
      if (process is null)
      {
          return ("bash error: the shell process failed to start.", true);
      }
      var stdoutTask = process.StandardOutput.ReadToEndAsync();
      var stderrTask = process.StandardError.ReadToEndAsync();
      using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(bashTimeoutSeconds));
      try
      {
          await process.WaitForExitAsync(timeout.Token);
      }
      catch (OperationCanceledException)
      {
          process.Kill(entireProcessTree: true);
          // Let the reader tasks finish before the process is disposed.
          try
          {
              await Task.WhenAll(stdoutTask, stderrTask);
          }
          catch
          {
              // The output is discarded on timeout, so reader failures are ignored too.
          }
          return ($"command timed out after {bashTimeoutSeconds}s", true);
      }
      var output = (await stdoutTask + await stderrTask).Trim();
      if (output.Length == 0)
      {
          output = "(no output)";
      }
      if (output.Length > toolResultMaxChars)
      {
          output = output[..toolResultMaxChars] + $"\n(truncated at {toolResultMaxChars} chars)";
      }
      if (process.ExitCode != 0)
      {
          output = $"(exit code {process.ExitCode})\n{output}";
      }
      return (output, process.ExitCode != 0);
  }

  // Execute one bash tool call requested by the model.
  async Task<(string Output, bool IsError)> HandleBashBlock(ToolUseBlock block)
  {
      if (block.Input.TryGetValue("restart", out var restart) && restart.ValueKind == JsonValueKind.True)
      {
          return ("Shell restarted.", false);
      }
      var command = block.Input.TryGetValue("command", out var rawCommand) && rawCommand.ValueKind == JsonValueKind.String
          ? rawCommand.GetString()!
          : "";
      if (command.Length == 0)
      {
          return ("bash error: no command was provided.", true);
      }
      return await RunBash(command);
  }

go Go
  // Run bash where the example was launched. In DOC_TEST_MODE the docs harness
  // points it at a throwaway fixture directory instead, removed on exit.
  var workDir = func() string {
  	if !docTestMode {
  		dir, err := os.Getwd()
  		if err != nil {
  			log.Fatal(err)
  		}
  		return dir
  	}
  	dir, err := os.MkdirTemp("", "orchestration-")
  	if err != nil {
  		log.Fatal(err)
  	}
  	fixture := "def fib(n):\n" +
  		"    return n if n < 2 else fib(n - 1) + fib(n - 2)\n\n" +
  		"print(fib(10))\n"
  	if err := os.WriteFile(filepath.Join(dir, "sample.py"), []byte(fixture), 0o644); err != nil {
  		log.Fatal(err)
  	}
  	return dir
  }()

  // runBash runs a shell command and returns its output plus an error flag.
  // No sandbox: example code only.
  func runBash(ctx context.Context, command string) (string, bool) {
  	fmt.Fprintf(os.Stderr, "[bash] %s\n", command)
  	ctx, cancel := context.WithTimeout(ctx, bashTimeoutSeconds*time.Second)
  	defer cancel()
  	cmd := exec.CommandContext(ctx, "bash", "-c", command)
  	cmd.Dir = workDir
  	combined, err := cmd.CombinedOutput()
  	if errors.Is(ctx.Err(), context.DeadlineExceeded) {
  		return fmt.Sprintf("command timed out after %ds", bashTimeoutSeconds), true
  	}
  	output := strings.TrimSpace(string(combined))
  	if output == "" {
  		output = "(no output)"
  	}
  	if runes := []rune(output); len(runes) > toolResultMaxChars {
  		output = string(runes[:toolResultMaxChars]) + fmt.Sprintf("\n(truncated at %d chars)", toolResultMaxChars)
  	}
  	if err == nil {
  		return output, false
  	}
  	var exitErr *exec.ExitError
  	if errors.As(err, &exitErr) {
  		return fmt.Sprintf("(exit code %d)\n%s", exitErr.ExitCode(), output), true
  	}
  	return fmt.Sprintf("(%s)\n%s", err, output), true
  }

  // handleBashBlock executes one bash tool call requested by the model.
  func handleBashBlock(ctx context.Context, block anthropic.ToolUseBlock) (string, bool) {
  	var input struct {
  		Command string `json:"command"`
  		Restart bool   `json:"restart"`
  	}
  	if err := json.Unmarshal(block.Input, &input); err != nil {
  		return fmt.Sprintf("bash error: could not parse input: %s", err), true
  	}
  	if input.Restart {
  		return "Shell restarted.", false
  	}
  	if input.Command == "" {
  		return "bash error: no command was provided.", true
  	}
  	return runBash(ctx, input.Command)
  }

java Java
  record ToolOutput(String output, boolean isError) {}

  // Run bash where the example was launched. In DOC_TEST_MODE the docs harness
  // points it at a throwaway fixture directory instead, removed on exit.
  static final Path WORK_DIR = createWorkDir();

  static Path createWorkDir() {
      if (!DOC_TEST_MODE) {
          return Path.of(System.getProperty("user.dir"));
      }
      try {
          var dir = Files.createTempDirectory("orchestration-");
          Files.writeString(dir.resolve("sample.py"), """
                  def fib(n):
                      return n if n < 2 else fib(n - 1) + fib(n - 2)

                  print(fib(10))
                  """);
          Runtime.getRuntime().addShutdownHook(new Thread(() -> {
              try (var paths = Files.walk(dir)) {
                  paths.sorted(Comparator.reverseOrder()).forEach(p -> {
                      try { Files.deleteIfExists(p); } catch (IOException ignored) {}
                  });
              } catch (IOException ignored) {
                  // Best-effort cleanup; the OS tmp sweeper handles leftovers.
              }
          }));
          return dir;
      } catch (IOException error) {
          throw new UncheckedIOException(error);
      }
  }

  // Run a shell command and return its output plus an error flag. No sandbox: example code only.
  ToolOutput runBash(String command) throws InterruptedException {
      System.err.println("[bash] " + command);
      Process process;
      try {
          process = new ProcessBuilder("bash", "-c", command)
                  .directory(WORK_DIR.toFile())
                  .redirectErrorStream(true)
                  .start();
      } catch (IOException error) {
          return new ToolOutput("(" + error + ")", true);
      }
      // Drain stdout on another thread so a filled pipe cannot stall the timeout wait below.
      CompletableFuture<String> outputReader = CompletableFuture.supplyAsync(() -> {
          try (var stdout = process.getInputStream()) {
              return new String(stdout.readAllBytes(), StandardCharsets.UTF_8);
          } catch (IOException error) {
              return "";
          }
      });
      if (!process.waitFor(BASH_TIMEOUT_SECONDS, TimeUnit.SECONDS)) {
          process.destroyForcibly();
          outputReader.cancel(true);
          return new ToolOutput("command timed out after " + BASH_TIMEOUT_SECONDS + "s", true);
      }
      String output = outputReader.join().trim();
      if (output.isEmpty()) {
          output = "(no output)";
      }
      if (output.length() > TOOL_RESULT_MAX_CHARS) {
          output = output.substring(0, TOOL_RESULT_MAX_CHARS)
                  + "\n(truncated at " + TOOL_RESULT_MAX_CHARS + " chars)";
      }
      int exitCode = process.exitValue();
      if (exitCode != 0) {
          return new ToolOutput("(exit code " + exitCode + ")\n" + output, true);
      }
      return new ToolOutput(output, false);
  }

  // Execute one bash tool call requested by the model.
  ToolOutput handleBashBlock(ToolUseBlock block) throws InterruptedException {
      Map<String, JsonValue> input = (Map<String, JsonValue>) block._input().asObject().orElse(Map.of());
      JsonValue restart = input.getOrDefault("restart", JsonValue.from(false));
      if (Boolean.TRUE.equals(restart.asBoolean().orElse(false))) {
          return new ToolOutput("Shell restarted.", false);
      }
      JsonValue raw = input.get("command");
      String command = raw != null && raw.asString().isPresent() ? raw.asStringOrThrow() : "";
      if (command.isEmpty()) {
          return new ToolOutput("bash error: no command was provided.", true);
      }
      return runBash(command);
  }

php PHP
  // Run bash where the example was launched. In DOC_TEST_MODE the docs harness
  // points it at a throwaway fixture directory instead, removed on exit.
  if (DOC_TEST_MODE) {
      $workDir = sys_get_temp_dir() . '/orchestration-' . bin2hex(random_bytes(8));
      if (!mkdir($workDir, 0700)) {
          throw new RuntimeException("could not create working directory {$workDir}");
      }
      file_put_contents(
          $workDir . '/sample.py',
          "def fib(n):\n"
          . "    return n if n < 2 else fib(n - 1) + fib(n - 2)\n\n"
          . "print(fib(10))\n",
      );
      register_shutdown_function(function () use ($workDir): void {
          foreach (glob($workDir . '/*') ?: [] as $entry) {
              @unlink($entry);
          }
          @rmdir($workDir);
      });
  } else {
      $workDir = getcwd() ?: '.';
  }
  define('WORK_DIR', $workDir);

  /**
   * Run a shell command and return [output, isError]. The coreutils timeout command
   * enforces the time limit. No sandbox: example code only.
   */
  function runBash(string $command): array
  {
      fwrite(STDERR, "[bash] {$command}\n");
      // Requires GNU coreutils 'timeout'. On macOS: brew install coreutils, or replace with gtimeout.
      exec(
          'cd ' . escapeshellarg(WORK_DIR) . ' && timeout ' . BASH_TIMEOUT_SECONDS
              . ' bash -c ' . escapeshellarg($command) . ' 2>&1',
          $outputLines,
          $exitCode,
      );
      if ($exitCode === 124) {
          return ['command timed out after ' . BASH_TIMEOUT_SECONDS . 's', true];
      }
      $output = trim(implode("\n", $outputLines));
      if ($output === '') {
          $output = '(no output)';
      }
      if (mb_strlen($output) > TOOL_RESULT_MAX_CHARS) {
          $output = mb_substr($output, 0, TOOL_RESULT_MAX_CHARS)
              . "\n(truncated at " . TOOL_RESULT_MAX_CHARS . ' chars)';
      }
      if ($exitCode !== 0) {
          $output = "(exit code {$exitCode})\n{$output}";
      }
      return [$output, $exitCode !== 0];
  }

  /** Execute one bash tool call requested by the model. */
  function handleBashBlock(ToolUseBlock $block): array
  {
      if (($block->input['restart'] ?? null) === true) {
          return ['Shell restarted.', false];
      }
      $command = $block->input['command'] ?? '';
      if (!is_string($command) || $command === '') {
          return ['bash error: no command was provided.', true];
      }
      return runBash($command);
  }

ruby Ruby
  # Run bash where the example was launched. In DOC_TEST_MODE the docs harness
  # points it at a throwaway fixture directory instead, removed on exit.
  WORK_DIR =
    if DOC_TEST_MODE
      Dir.mktmpdir("orchestration-").tap do |dir|
        File.write(File.join(dir, "sample.py"), <<~PYTHON)
          def fib(n):
              return n if n < 2 else fib(n - 1) + fib(n - 2)

          print(fib(10))
        PYTHON
        at_exit { FileUtils.remove_entry(dir, true) }
      end
    else
      Dir.pwd
    end

  # Tool input arrives as a Hash or as a raw JSON string from the streaming
  # accumulator; normalize either shape to a string-keyed Hash.
  def parse_tool_input(raw)
    return raw.transform_keys(&:to_s) if raw.is_a?(Hash)
    parsed = JSON.parse(raw.to_s) rescue nil
    parsed.is_a?(Hash) ? parsed : {}
  end

  # Run a shell command and return [output, is_error]. No sandbox: example code only.
  def run_bash(command)
    warn "[bash] #{command}"
    begin
      stdin, stdout_and_stderr, wait_thr = Open3.popen2e("bash", "-c", command, pgroup: true, chdir: WORK_DIR)
      stdin.close
      reader = Thread.new { stdout_and_stderr.read.scrub }
      # Enforce the time limit with a monotonic-clock deadline so a timed-out command is
      # terminated rather than left running in the background.
      deadline = Process.clock_gettime(Process::CLOCK_MONOTONIC) + BASH_TIMEOUT_SECONDS
      until wait_thr.join(0.1)
        next if Process.clock_gettime(Process::CLOCK_MONOTONIC) < deadline

        begin
          Process.kill("-TERM", wait_thr.pid)
        rescue Errno::ESRCH
        end
        unless wait_thr.join(2)
          begin
            Process.kill("-KILL", wait_thr.pid)
          rescue Errno::ESRCH
          end
        end
        wait_thr.join(5)
        reader.join(1) || reader.kill
        stdout_and_stderr.close rescue nil
        return ["command timed out after #{BASH_TIMEOUT_SECONDS}s", true]
      end
      status = wait_thr.value
      output = reader.value.strip
      stdout_and_stderr.close
      output = "(no output)" if output.empty?
      if output.length > TOOL_RESULT_MAX_CHARS
        output = "#{output[0, TOOL_RESULT_MAX_CHARS]}\n(truncated at #{TOOL_RESULT_MAX_CHARS} chars)"
      end
      output = "(exit code #{status.exitstatus})\n#{output}" unless status.success?
      [output, !status.success?]
    rescue Errno::ENOENT => e
      return ["bash error: #{e.message}", true]
    end
  end

  # Execute one bash tool call requested by the model.
  def handle_bash_block(block)
    input = parse_tool_input(block.input)
    return ["Shell restarted.", false] if input["restart"] == true

    command = input["command"]
    return ["bash error: no command was provided.", true] unless command.is_a?(String) && !command.empty?

    run_bash(command)
  end

  # Convert response content to request-shaped params. The streaming accumulator
  # returns tool_use input as a raw JSON string and includes response-only fields,
  # so reshape each block to the request schema before echoing it back.
  def assistant_content_param(content)
    content.map do |block|
      case block.type
      when :tool_use
        input = parse_tool_input(block.input)
        {type: "tool_use", id: block.id, name: block.name, input: input}
      when :text
        {type: "text", text: block.text}
      when :thinking
        {type: "thinking", thinking: block.thinking, signature: block.signature}
      when :redacted_thinking then {type: "redacted_thinking", data: block.data}
      else
        block.to_h
      end
    end
  end
  ```
</CodeGroup>


## Run one subagent

Source: https://platform.claude.com/llms-full.txt#run-one-subagent

Each workflow subtask becomes its own small agent loop with the bash tool, running at the same effort as the main loop. A per-request timeout bounds each API call so a dropped connection degrades one subagent instead of stalling the whole run.

<CodeGroup>
  ```python Python
  def run_subagent(model: str, prompt: str) -> str:
      """One subagent: a small nested agent loop with the bash tool plus report_findings.
      Subagents inherit the main loop's effort level."""
      subagent_system = (
          "You are one agent in a larger parallel fan-out, assigned a single subtask. "
          "Investigate it directly, using bash to check facts rather than guessing, and finish "
          "by calling report_findings exactly once. Return findings, not narration."
      )
      messages = [{"role": "user", "content": prompt}]
      for _ in range(MAX_SUBAGENT_TURNS):
          with client.messages.stream(
              model=model,
              max_tokens=64000,
              system=subagent_system,
              output_config={"effort": EFFORT},
              tools=[BASH_TOOL, REPORT_TOOL],
              messages=messages,
              timeout=REQUEST_TIMEOUT_SECONDS,
          ) as stream:
              response = stream.get_final_message()
          messages.append({"role": "assistant", "content": response.content})
          if response.stop_reason == "pause_turn":
              continue
          if response.stop_reason != "tool_use":
              text = "".join(block.text for block in response.content if block.type == "text")
              if response.stop_reason == "max_tokens":
                  text += "\n\n(warning: subagent response was truncated at max_tokens)"
              return text
          tool_results = []
          report = None
          for block in response.content:
              if block.type != "tool_use":
                  continue
              if block.name == "report_findings":
                  report = json.dumps(block.input, indent=2)
                  output, is_error = "Findings recorded.", False
              elif block.name == "bash":
                  output, is_error = handle_bash_block(block)
              else:
                  output, is_error = f"unknown tool: {block.name}", True
              tool_results.append(
                  {
                      "type": "tool_result",
                      "tool_use_id": block.id,
                      "content": output,
                      "is_error": is_error,
                  }
              )
          if report is not None:
              return report
          messages.append({"role": "user", "content": tool_results})
      return "(subagent hit the turn limit before finishing)"

typescript TypeScript
  // One subagent: a small nested agent loop with the bash tool plus report_findings.
  // Subagents inherit the main loop's effort level.
  async function runSubagent(model: string, prompt: string): Promise<string> {
    const subagentSystem =
      "You are one agent in a larger parallel fan-out, assigned a single subtask. " +
      "Investigate it directly, using bash to check facts rather than guessing, and finish " +
      "by calling report_findings exactly once. Return findings, not narration.";
    const messages: Anthropic.MessageParam[] = [{ role: "user", content: prompt }];
    for (let turn = 0; turn < MAX_SUBAGENT_TURNS; turn++) {
      const response = await client.messages
        .stream(
          {
            model,
            max_tokens: 64000,
            system: subagentSystem,
            output_config: { effort: EFFORT },
            tools: [BASH_TOOL, REPORT_TOOL],
            messages,
          },
          { signal: AbortSignal.timeout(REQUEST_TIMEOUT_SECONDS * 1000) },
        )
        .finalMessage();
      messages.push({ role: "assistant", content: response.content });
      if (response.stop_reason === "pause_turn") {
        continue;
      }
      if (response.stop_reason !== "tool_use") {
        let text = response.content
          .filter((block): block is Anthropic.TextBlock => block.type === "text")
          .map((block) => block.text)
          .join("");
        if (response.stop_reason === "max_tokens") {
          text += "\n\n(warning: subagent response was truncated at max_tokens)";
        }
        return text;
      }
      const toolResults: Anthropic.ToolResultBlockParam[] = [];
      let report: string | null = null;
      for (const block of response.content) {
        if (block.type !== "tool_use") {
          continue;
        }
        let output: string;
        let isError: boolean;
        if (block.name === "report_findings") {
          report = JSON.stringify(block.input, null, 2);
          output = "Findings recorded.";
          isError = false;
        } else if (block.name === "bash") {
          ({ output, isError } = await handleBashBlock(block));
        } else {
          output = `unknown tool: ${block.name}`;
          isError = true;
        }
        toolResults.push({
          type: "tool_result",
          tool_use_id: block.id,
          content: output,
          is_error: isError,
        });
      }
      if (report !== null) {
        return report;
      }
      messages.push({ role: "user", content: toolResults });
    }
    return "(subagent hit the turn limit before finishing)";
  }

csharp C#
  // One subagent: a small nested agent loop with the bash tool plus report_findings.
  // Subagents inherit the main loop's effort level.
  async Task<string> RunSubagent(string prompt)
  {
      const string subagentSystem =
          "You are one agent in a larger parallel fan-out, assigned a single subtask. "
          + "Investigate it directly, using bash to check facts rather than guessing, and finish "
          + "by calling report_findings exactly once. Return findings, not narration.";
      List<MessageParam> messages = [new() { Role = Role.User, Content = prompt }];
      for (var turn = 0; turn < maxSubagentTurns; turn++)
      {
          using var deadline = new CancellationTokenSource(TimeSpan.FromSeconds(requestTimeoutSeconds));
          var response = await client.Messages.Create(new MessageCreateParams
          {
              Model = model,
              MaxTokens = requestMaxTokens,
              System = subagentSystem,
              OutputConfig = new OutputConfig { Effort = effort },
              Tools = [bashTool, reportTool],
              Messages = messages,
          }, cancellationToken: deadline.Token);
          messages.Add(new()
          {
              Role = Role.Assistant,
              Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList(),
          });
          if (response.StopReason == StopReason.PauseTurn)
          {
              continue;
          }
          if (response.StopReason != StopReason.ToolUse)
          {
              var text = string.Concat(
                  response.Content.Select(block => block.TryPickText(out var textBlock) ? textBlock.Text : ""));
              if (response.StopReason == StopReason.MaxTokens)
              {
                  text += "\n\n(warning: subagent response was truncated at max_tokens)";
              }
              return text;
          }
          List<ContentBlockParam> toolResults = [];
          string? report = null;
          foreach (var block in response.Content)
          {
              if (!block.TryPickToolUse(out var toolUse))
              {
                  continue;
              }
              string output;
              bool isError;
              if (toolUse.Name == "report_findings")
              {
                  report = JsonSerializer.Serialize(
                      toolUse.Input, new JsonSerializerOptions { WriteIndented = true });
                  output = "Findings recorded.";
                  isError = false;
              }
              else if (toolUse.Name == "bash")
              {
                  (output, isError) = await HandleBashBlock(toolUse);
              }
              else
              {
                  output = $"unknown tool: {toolUse.Name}";
                  isError = true;
              }
              toolResults.Add(new ToolResultBlockParam(toolUse.ID) { Content = output, IsError = isError });
          }
          if (report is not null)
          {
              return report;
          }
          messages.Add(new() { Role = Role.User, Content = toolResults });
      }
      return "(subagent hit the turn limit before finishing)";
  }

go Go
  // runSubagent runs one subagent: a small nested agent loop with the bash tool plus
  // report_findings. Subagents inherit the main loop's effort level.
  func runSubagent(ctx context.Context, model string, prompt string) (string, error) {
  	subagentSystem := "You are one agent in a larger parallel fan-out, assigned a single subtask. " +
  		"Investigate it directly, using bash to check facts rather than guessing, and finish " +
  		"by calling report_findings exactly once. Return findings, not narration."
  	messages := []anthropic.MessageParam{anthropic.NewUserMessage(anthropic.NewTextBlock(prompt))}
  	for range maxSubagentTurns {
  		var response anthropic.Message
  		err := func() error {
  			ctx, cancel := context.WithTimeout(ctx, requestTimeoutSeconds*time.Second)
  			defer cancel()
  			stream := client.Messages.NewStreaming(ctx, anthropic.MessageNewParams{
  				Model:        model,
  				MaxTokens:    64000,
  				System:       []anthropic.TextBlockParam{{Text: subagentSystem}},
  				OutputConfig: anthropic.OutputConfigParam{Effort: effort},
  				Tools:        []anthropic.ToolUnionParam{bashTool, reportTool},
  				Messages:     messages,
  			})
  			defer stream.Close()
  			for stream.Next() {
  				if err := response.Accumulate(stream.Current()); err != nil {
  					return err
  				}
  			}
  			return stream.Err()
  		}()
  		if err != nil {
  			return "", err
  		}
  		messages = append(messages, response.ToParam())
  		if response.StopReason == anthropic.StopReasonPauseTurn {
  			continue
  		}
  		if response.StopReason != anthropic.StopReasonToolUse {
  			var text strings.Builder
  			for _, block := range response.Content {
  				if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  					text.WriteString(textBlock.Text)
  				}
  			}
  			if response.StopReason == anthropic.StopReasonMaxTokens {
  				text.WriteString("\n\n(warning: subagent response was truncated at max_tokens)")
  			}
  			return text.String(), nil
  		}
  		var toolResults []anthropic.ContentBlockParamUnion
  		var report string
  		var reportRecorded bool
  		for _, block := range response.Content {
  			toolUse, ok := block.AsAny().(anthropic.ToolUseBlock)
  			if !ok {
  				continue
  			}
  			var output string
  			var isError bool
  			switch toolUse.Name {
  			case "report_findings":
  				report = string(toolUse.Input)
  				var pretty bytes.Buffer
  				if err := json.Indent(&pretty, toolUse.Input, "", "  "); err == nil {
  					report = pretty.String()
  				}
  				reportRecorded = true
  				output = "Findings recorded."
  			case "bash":
  				output, isError = handleBashBlock(ctx, toolUse)
  			default:
  				output, isError = fmt.Sprintf("unknown tool: %s", toolUse.Name), true
  			}
  			toolResults = append(toolResults, anthropic.NewToolResultBlock(toolUse.ID, output, isError))
  		}
  		if reportRecorded {
  			return report, nil
  		}
  		messages = append(messages, anthropic.NewUserMessage(toolResults...))
  	}
  	return "(subagent hit the turn limit before finishing)", nil
  }

java Java
  // One subagent: a small nested agent loop with the bash tool plus report_findings.
  // Subagents inherit the main loop's effort level.
  String runSubagent(Model model, String prompt) throws InterruptedException {
      String subagentSystem = "You are one agent in a larger parallel fan-out, assigned a single subtask. "
              + "Investigate it directly, using bash to check facts rather than guessing, and finish "
              + "by calling report_findings exactly once. Return findings, not narration.";
      List<MessageParam> messages = new ArrayList<>();
      messages.add(MessageParam.builder().role(MessageParam.Role.USER).content(prompt).build());
      for (int turn = 0; turn < MAX_SUBAGENT_TURNS; turn++) {
          MessageCreateParams params = MessageCreateParams.builder()
                  .model(model)
                  .maxTokens(64000L)
                  .system(subagentSystem)
                  .outputConfig(OutputConfig.builder().effort(EFFORT).build())
                  .addTool(BASH_TOOL)
                  .addTool(REPORT_TOOL)
                  .messages(messages)
                  .build();
          MessageAccumulator accumulator = MessageAccumulator.create();
          try (var stream = client.messages().createStreaming(params, REQUEST_OPTIONS)) {
              stream.stream().forEach(accumulator::accumulate);
          }
          Message response = accumulator.message();
          messages.add(response.toParam());
          StopReason stopReason = response.stopReason().orElse(null);
          if (StopReason.PAUSE_TURN.equals(stopReason)) {
              continue;
          }
          if (!StopReason.TOOL_USE.equals(stopReason)) {
              String text = response.content().stream()
                      .flatMap(block -> block.text().stream())
                      .map(TextBlock::text)
                      .collect(Collectors.joining());
              if (StopReason.MAX_TOKENS.equals(stopReason)) {
                  text += "\n\n(warning: subagent response was truncated at max_tokens)";
              }
              return text;
          }
          List<ContentBlockParam> toolResults = new ArrayList<>();
          String report = null;
          for (ContentBlock block : response.content()) {
              if (block.toolUse().isEmpty()) {
                  continue;
              }
              ToolUseBlock toolUse = block.toolUse().get();
              ToolOutput result;
              if (toolUse.name().equals("report_findings")) {
                  report = toolUse._input().convert(JsonNode.class).toPrettyString();
                  result = new ToolOutput("Findings recorded.", false);
              } else if (toolUse.name().equals("bash")) {
                  result = handleBashBlock(toolUse);
              } else {
                  result = new ToolOutput("unknown tool: " + toolUse.name(), true);
              }
              toolResults.add(ContentBlockParam.ofToolResult(ToolResultBlockParam.builder()
                      .toolUseId(toolUse.id())
                      .content(result.output())
                      .isError(result.isError())
                      .build()));
          }
          if (report != null) {
              return report;
          }
          messages.add(MessageParam.builder()
                  .role(MessageParam.Role.USER)
                  .contentOfBlockParams(toolResults)
                  .build());
      }
      return "(subagent hit the turn limit before finishing)";
  }

php PHP
  /**
   * Consume a message stream and assemble the final assistant turn from its events:
   * the full content-block list plus the stop reason, equivalent to what a
   * non-streaming create call returns.
   */
  function drainMessageStream(iterable $events): array
  {
      $stringValue = fn ($value) => $value instanceof BackedEnum ? $value->value : $value;
      $blocks = [];
      $jsonBuffers = [];
      $stopReason = null;
      foreach ($events as $event) {
          $type = $stringValue($event->type);
          if ($type === 'content_block_start') {
              $blocks[$event->index] = $event->contentBlock;
              $jsonBuffers[$event->index] = '';
          } elseif ($type === 'content_block_delta') {
              $block = $blocks[$event->index];
              $delta = $event->delta;
              $deltaType = $stringValue($delta->type);
              if ($deltaType === 'text_delta') {
                  $blocks[$event->index] = $block->withText($block->text . $delta->text);
              } elseif ($deltaType === 'input_json_delta') {
                  $jsonBuffers[$event->index] .= $delta->partialJSON;
              } elseif ($deltaType === 'thinking_delta') {
                  $blocks[$event->index] = $block->withThinking($block->thinking . $delta->thinking);
              } elseif ($deltaType === 'signature_delta') {
                  $blocks[$event->index] = $block->withSignature($delta->signature);
              }
          } elseif ($type === 'message_delta') {
              $stopReason = $stringValue($event->delta->stopReason);
          }
      }
      foreach ($jsonBuffers as $index => $buffer) {
          if ($buffer !== '' && $blocks[$index] instanceof ToolUseBlock) {
              $decoded = json_decode($buffer, true);
              $blocks[$index] = $blocks[$index]->withInput(is_array($decoded) ? $decoded : []);
          }
      }
      return [array_values($blocks), $stopReason];
  }

  /**
   * One subagent: a small nested agent loop with the bash tool plus report_findings.
   * Subagents inherit the main loop's effort level.
   */
  function runSubagent(Client $client, string $model, string $prompt): string
  {
      $subagentSystem =
          'You are one agent in a larger parallel fan-out, assigned a single subtask. '
          . 'Investigate it directly, using bash to check facts rather than guessing, and finish '
          . 'by calling report_findings exactly once. Return findings, not narration.';
      $messages = [['role' => 'user', 'content' => $prompt]];
      for ($turn = 0; $turn < MAX_SUBAGENT_TURNS; $turn++) {
          $stream = $client->messages->createStream(
              model: $model,
              maxTokens: 64000,
              system: $subagentSystem,
              outputConfig: ['effort' => EFFORT],
              tools: [BASH_TOOL, REPORT_TOOL],
              messages: $messages,
              requestOptions: ['timeout' => REQUEST_TIMEOUT_SECONDS],
          );
          [$content, $stopReason] = drainMessageStream($stream);
          $messages[] = ['role' => 'assistant', 'content' => $content];
          if ($stopReason === 'pause_turn') {
              continue;
          }
          if ($stopReason !== 'tool_use') {
              $text = '';
              foreach ($content as $block) {
                  if ($block instanceof TextBlock) {
                      $text .= $block->text;
                  }
              }
              if ($stopReason === 'max_tokens') {
                  $text .= "\n\n(warning: subagent response was truncated at max_tokens)";
              }
              return $text;
          }
          $report = null;
          $toolResults = [];
          foreach ($content as $block) {
              if (!$block instanceof ToolUseBlock) {
                  continue;
              }
              if ($block->name === 'report_findings') {
                  $report = json_encode($block->input, JSON_PRETTY_PRINT);
                  $output = 'Findings recorded.';
                  $isError = false;
              } elseif ($block->name === 'bash') {
                  [$output, $isError] = handleBashBlock($block);
              } else {
                  $output = "unknown tool: {$block->name}";
                  $isError = true;
              }
              $toolResults[] = [
                  'type' => 'tool_result',
                  'tool_use_id' => $block->id,
                  'content' => $output,
                  'is_error' => $isError,
              ];
          }
          if ($report !== null) {
              return $report;
          }
          $messages[] = ['role' => 'user', 'content' => $toolResults];
      }
      return '(subagent hit the turn limit before finishing)';
  }

ruby Ruby
  # One subagent: a small nested agent loop with the bash tool plus report_findings.
  # Subagents inherit the main loop's effort level.
  def run_subagent(model, prompt)
    subagent_system =
      "You are one agent in a larger parallel fan-out, assigned a single subtask. " \
      "Investigate it directly, using bash to check facts rather than guessing, and finish " \
      "by calling report_findings exactly once. Return findings, not narration."
    messages = [{role: "user", content: prompt}]
    MAX_SUBAGENT_TURNS.times do
      stream = CLIENT.messages.stream(
        model: model,
        max_tokens: 64_000,
        system_: subagent_system,
        output_config: {effort: EFFORT},
        tools: [BASH_TOOL, REPORT_TOOL],
        messages: messages,
        request_options: {timeout: REQUEST_TIMEOUT_SECONDS}
      )
      response = stream.accumulated_message
      messages << {role: "assistant", content: assistant_content_param(response.content)}
      next if response.stop_reason == :pause_turn

      unless response.stop_reason == :tool_use
        text = response.content.select { |block| block.type == :text }.map(&:text).join
        text += "\n\n(warning: subagent response was truncated at max_tokens)" if response.stop_reason == :max_tokens
        return text
      end

      report = nil
      tool_results = []
      response.content.each do |block|
        next unless block.type == :tool_use

        input = parse_tool_input(block.input)
        case block.name
        when "report_findings"
          report = JSON.pretty_generate(input)
          output, is_error = "Findings recorded.", false
        when "bash"
          output, is_error = handle_bash_block(block)
        else
          output, is_error = "unknown tool: #{block.name}", true
        end
        tool_results << {
          type: "tool_result",
          tool_use_id: block.id,
          content: output,
          is_error: is_error
        }
      end
      return report unless report.nil?

      messages << {role: "user", content: tool_results}
    end
    "(subagent hit the turn limit before finishing)"
  end
  ```
</CodeGroup>


## Journal results so reruns resume

Source: https://platform.claude.com/llms-full.txt#journal-results-so-reruns-resume

A fan-out that spawns dozens of subagents is expensive to restart from scratch. A small content-addressed journal makes it idempotent: before dispatching a subagent, look up the SHA-256 of its prompt in a local JSON file, and return the recorded result if one exists. Interrupt the run, rerun it, and only the subtasks that never finished are recomputed. The journal deduplicates across runs, not within a single fan-out wave; delete the journal file to start fresh.

<CodeGroup>
  ```python Python
  _journal_lock = threading.Lock()


  def _load_journal() -> dict:
      try:
          with open(JOURNAL_PATH) as file:
              return json.load(file) or {}
      except (OSError, json.JSONDecodeError):
          return {}


  def journaled(prompt: str, compute) -> str:
      """Return a cached result for this exact prompt, or compute and persist it. This
      makes the fan-out resumable: interrupt the run, rerun it, and only the subtasks
      that never finished are recomputed. Delete the journal file to start fresh."""
      key = hashlib.sha256(prompt.encode()).hexdigest()
      cached = _load_journal().get(key)
      if cached is not None:
          print(f"[journal] cache hit for {key[:12]}", file=sys.stderr)
          return cached
      result = compute()
      try:
          with _journal_lock:  # fan-out writes from many threads
              journal = _load_journal()
              journal[key] = result
              temp = f"{JOURNAL_PATH}.tmp"
              with open(temp, "w") as file:
                  json.dump(journal, file)
              os.replace(temp, JOURNAL_PATH)  # atomic on POSIX and Windows
      except OSError as error:  # the journal is best-effort; never discard a computed result
          print(f"[journal] write failed: {error}", file=sys.stderr)
      return result

typescript TypeScript
  let journalWriteChain = Promise.resolve();

  async function loadJournal(): Promise<Record<string, string>> {
    try {
      return JSON.parse(await readFile(JOURNAL_PATH, "utf8")) ?? {};
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "ENOENT") {
        console.error(`[journal] discarding unreadable journal: ${error}`);
      }
      return {};
    }
  }

  // Return a cached result for this exact prompt, or compute and persist it. This
  // makes the fan-out resumable: interrupt the run, rerun it, and only the subtasks
  // that never finished are recomputed. Delete the journal file to start fresh.
  async function journaled(prompt: string, compute: () => Promise<string>): Promise<string> {
    const key = createHash("sha256").update(prompt).digest("hex");
    const cached = (await loadJournal())[key];
    if (cached !== undefined) {
      console.error(`[journal] cache hit for ${key.slice(0, 12)}`);
      return cached;
    }
    const result = await compute();
    // Chain writes so concurrent subagents do not clobber each other's entries.
    // The chain is kept settled so one failed write does not poison later ones.
    await (journalWriteChain = journalWriteChain
      .then(async () => {
        const journal = await loadJournal();
        journal[key] = result;
        const temp = `${JOURNAL_PATH}.tmp`;
        await writeFile(temp, JSON.stringify(journal));
        await rename(temp, JOURNAL_PATH);
      })
      .catch((error) => console.error(`[journal] write failed: ${error}`)));
    return result;
  }

csharp C#
  SemaphoreSlim journalLock = new(1, 1);

  async Task<Dictionary<string, string>> LoadJournal()
  {
      try
      {
          return JsonSerializer.Deserialize<Dictionary<string, string>>(await File.ReadAllTextAsync(journalPath)) ?? [];
      }
      catch (Exception error) when (error is IOException or UnauthorizedAccessException or JsonException)
      {
          return [];
      }
  }

  // Return a cached result for this exact prompt, or compute and persist it. This
  // makes the fan-out resumable: interrupt the run, rerun it, and only the subtasks
  // that never finished are recomputed. Delete the journal file to start fresh.
  async Task<string> Journaled(string prompt, Func<Task<string>> compute)
  {
      var key = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(prompt))).ToLowerInvariant();
      if ((await LoadJournal()).TryGetValue(key, out var cached))
      {
          Console.Error.WriteLine($"[journal] cache hit for {key[..12]}");
          return cached;
      }
      var result = await compute();
      await journalLock.WaitAsync(); // fan-out writes from many tasks
      try
      {
          var journal = await LoadJournal();
          journal[key] = result;
          var temp = journalPath + ".tmp";
          await File.WriteAllTextAsync(temp, JsonSerializer.Serialize(journal));
          File.Move(temp, journalPath, overwrite: true);
      }
      catch (Exception error) when (error is IOException or UnauthorizedAccessException or NotSupportedException)
      {
          // The journal is best-effort; never discard a computed result.
          Console.Error.WriteLine($"[journal] write failed: {error.Message}");
      }
      finally
      {
          journalLock.Release();
      }
      return result;
  }

go Go
  var journalMutex sync.Mutex

  func loadJournal() map[string]string {
  	data, err := os.ReadFile(journalPath)
  	if err != nil {
  		return map[string]string{}
  	}
  	var journal map[string]string
  	if err := json.Unmarshal(data, &journal); err != nil || journal == nil {
  		return map[string]string{}
  	}
  	return journal
  }

  // journaled returns a cached result for this exact prompt, or computes and persists
  // it. This makes the fan-out resumable: interrupt the run, rerun it, and only the
  // subtasks that never finished are recomputed. Delete the journal file to start fresh.
  func journaled(prompt string, compute func() (string, error)) (string, error) {
  	sum := sha256.Sum256([]byte(prompt))
  	key := hex.EncodeToString(sum[:])
  	if cached, ok := loadJournal()[key]; ok {
  		fmt.Fprintf(os.Stderr, "[journal] cache hit for %s\n", key[:12])
  		return cached, nil
  	}
  	result, err := compute()
  	if err != nil {
  		return "", err
  	}
  	journalMutex.Lock() // fan-out writes from many goroutines
  	defer journalMutex.Unlock()
  	journal := loadJournal()
  	journal[key] = result
  	data, _ := json.Marshal(journal)
  	temp := journalPath + ".tmp"
  	if err := os.WriteFile(temp, data, 0o644); err != nil {
  		fmt.Fprintf(os.Stderr, "[journal] write failed: %s\n", err)
  	} else if err := os.Rename(temp, journalPath); err != nil {
  		fmt.Fprintf(os.Stderr, "[journal] write failed: %s\n", err)
  		_ = os.Remove(temp)
  	}
  	return result, nil
  }

java Java
  static final ObjectMapper JOURNAL_MAPPER = new ObjectMapper();
  static final ReentrantLock JOURNAL_LOCK = new ReentrantLock();

  Map<String, String> loadJournal() {
      try {
          return Objects.requireNonNullElseGet(
                  JOURNAL_MAPPER.readValue(Files.readString(JOURNAL_PATH), new TypeReference<HashMap<String, String>>() {}),
                  HashMap::new);
      } catch (IOException error) {
          return new HashMap<>();
      }
  }

  // Return a cached result for this exact prompt, or compute and persist it. This
  // makes the fan-out resumable: interrupt the run, rerun it, and only the subtasks
  // that never finished are recomputed. Delete the journal file to start fresh.
  String journaled(String prompt, Callable<String> compute) throws Exception {
      var digest = MessageDigest.getInstance("SHA-256").digest(prompt.getBytes(StandardCharsets.UTF_8));
      String key = HexFormat.of().formatHex(digest);
      String cached = loadJournal().get(key);
      if (cached != null) {
          System.err.println("[journal] cache hit for " + key.substring(0, 12));
          return cached;
      }
      String result = compute.call();
      JOURNAL_LOCK.lock(); // fan-out writes from many threads
      try {
          Map<String, String> journal = loadJournal();
          journal.put(key, result);
          Path temp = JOURNAL_PATH.resolveSibling(JOURNAL_PATH.getFileName() + ".tmp");
          Files.writeString(temp, JOURNAL_MAPPER.writeValueAsString(journal));
          Files.move(temp, JOURNAL_PATH, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
      } catch (IOException error) {
          // The journal is best-effort; never discard a computed result.
          System.err.println("[journal] write failed: " + error);
      } finally {
          JOURNAL_LOCK.unlock();
      }
      return result;
  }

php PHP
  function loadJournal(): array
  {
      $raw = @file_get_contents(JOURNAL_PATH);
      if ($raw === false) {
          return [];
      }
      $decoded = json_decode($raw, true);
      return is_array($decoded) ? $decoded : [];
  }

  /**
   * Return a cached result for this exact prompt, or compute and persist it. This
   * makes the fan-out resumable: interrupt the run, rerun it, and only the subtasks
   * that never finished are recomputed. Delete the journal file to start fresh.
   */
  function journaled(string $prompt, callable $compute): string
  {
      $key = hash('sha256', $prompt);
      $journal = loadJournal();
      if (array_key_exists($key, $journal)) {
          fwrite(STDERR, '[journal] cache hit for ' . substr($key, 0, 12) . "\n");
          return $journal[$key];
      }
      $result = $compute();
      $journal = loadJournal();
      $journal[$key] = $result;
      $temp = JOURNAL_PATH . '.tmp';
      $encoded = json_encode($journal, JSON_INVALID_UTF8_SUBSTITUTE);
      if ($encoded === false || @file_put_contents($temp, $encoded) === false || !@rename($temp, JOURNAL_PATH)) {
          fwrite(STDERR, '[journal] write failed: ' . (error_get_last()['message'] ?? json_last_error_msg()) . "\n");
          @unlink($temp);
      }
      return $result;
  }

ruby Ruby
  JOURNAL_LOCK = Mutex.new

  def load_journal
    JSON.parse(File.read(JOURNAL_PATH)) || {}
  rescue SystemCallError, JSON::ParserError
    {}
  end

  # Return a cached result for this exact prompt, or compute and persist it. This
  # makes the fan-out resumable: interrupt the run, rerun it, and only the subtasks
  # that never finished are recomputed. Delete the journal file to start fresh.
  def journaled(prompt)
    key = Digest::SHA256.hexdigest(prompt)
    cached = load_journal[key]
    unless cached.nil?
      warn "[journal] cache hit for #{key[0, 12]}"
      return cached
    end
    result = yield
    begin
      JOURNAL_LOCK.synchronize do # fan-out writes from many threads
        journal = load_journal
        journal[key] = result
        temp = "#{JOURNAL_PATH}.tmp"
        File.write(temp, JSON.generate(journal))
        File.rename(temp, JOURNAL_PATH)
      end
    rescue SystemCallError => error # the journal is best-effort; never discard a computed result
      warn "[journal] write failed: #{error}"
    end
    result
  end
  ```
</CodeGroup>


## Fan out, then verify

Source: https://platform.claude.com/llms-full.txt#fan-out-then-verify

The fan-out accepts up to `MAX_TOTAL_SUBTASKS` prompts, runs them through the journal with at most `MAX_CONCURRENT` in flight (sequential in the PHP port), and isolates failures so one broken subagent degrades to an error string instead of ending the run. Once the first wave finishes, a second wave reuses the same subagent path to try to refute each result: every verifier re-derives the claims from the source, defaulting to refuted when uncertain. Both the original result and its verdict are returned to the orchestrator so it can weigh them together.

<CodeGroup>
  ```python Python
  def normalize_subtasks(raw) -> list[str]:
      """Accept the subtasks input in whatever shape the model emits: an array, the array
      JSON-encoded as a single string, or a newline-separated list."""
      if isinstance(raw, str):
          try:
              raw = json.loads(raw)
          except json.JSONDecodeError:
              raw = raw.splitlines() if "\n" in raw else [raw]
      if not isinstance(raw, list):
          return []
      return [task.strip() for task in raw if isinstance(task, str) and task.strip()]


  def verify_prompt_for(subtask: str, result: str) -> str:
      return (
          "Adversarially verify the subagent result below: try to REFUTE it. Re-derive the "
          "claims yourself with bash rather than trusting the result, and look for evidence "
          "that contradicts them. Default to refuted if uncertain. Call report_findings with "
          "summary 'refuted: <why>' or 'confirmed: <why>', citing the file:line or command "
          "output that decided it.\n\n"
          f"Subtask: {subtask}\n\nResult to verify:\n{result}"
      )


  def run_workflow(model: str, raw_subtasks) -> tuple[str, bool]:
      """Run subtasks as parallel subagents, then run a second verification wave over
      the results, and return both. MAX_TOTAL_SUBTASKS bounds how many the model can
      queue; MAX_CONCURRENT bounds how many run at once."""
      all_subtasks = normalize_subtasks(raw_subtasks)
      subtasks = all_subtasks[:MAX_TOTAL_SUBTASKS]
      dropped = len(all_subtasks) - len(subtasks)
      if not subtasks:
          return "Workflow error: no usable subtasks were provided.", True
      print(f"[workflow] fanning out {len(subtasks)} agents", file=sys.stderr)

      def run_one(prompt: str) -> str:
          try:
              return journaled(prompt, lambda: run_subagent(model, prompt))
          except Exception as error:  # isolation boundary: one bad subagent should not end the run
              return f"(subagent failed: {type(error).__name__}: {error})"

      with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as pool:
          results = list(pool.map(run_one, subtasks))
          print(f"[workflow] verifying {len(results)} results", file=sys.stderr)
          verify_prompts = [verify_prompt_for(task, result) for task, result in zip(subtasks, results)]
          verdicts = list(pool.map(run_one, verify_prompts))

      joined = "\n\n".join(
          f"[agent {index + 1}: {task}]\n{result}\n\n[verify {index + 1}]\n{verdict}"
          for index, (task, result, verdict) in enumerate(zip(subtasks, results, verdicts))
      )
      if dropped > 0:
          joined = (
              f"(note: {dropped} subtasks beyond MAX_TOTAL_SUBTASKS={MAX_TOTAL_SUBTASKS} were not "
              "run; rerun them in a follow-up Workflow call)\n\n" + joined
          )
      return joined, False

typescript TypeScript
  // Accept the subtasks input in whatever shape the model emits: an array, the array
  // JSON-encoded as a single string, or a newline-separated list.
  function normalizeSubtasks(raw: unknown): string[] {
    let value = raw;
    if (typeof raw === "string") {
      try {
        value = JSON.parse(raw);
      } catch {
        value = raw.includes("\n") ? raw.split("\n") : [raw];
      }
    }
    if (!Array.isArray(value)) {
      return [];
    }
    return value
      .filter((task): task is string => typeof task === "string")
      .map((task) => task.trim())
      .filter((task) => task.length > 0);
  }

  function verifyPromptFor(subtask: string, result: string): string {
    return (
      "Adversarially verify the subagent result below: try to REFUTE it. Re-derive the " +
      "claims yourself with bash rather than trusting the result, and look for evidence " +
      "that contradicts them. Default to refuted if uncertain. Call report_findings with " +
      "summary 'refuted: <why>' or 'confirmed: <why>', citing the file:line or command " +
      "output that decided it.\n\n" +
      `Subtask: ${subtask}\n\nResult to verify:\n${result}`
    );
  }

  // Map with a concurrency limit: at most `limit` tasks are in flight at once.
  async function mapWithLimit<In, Out>(
    items: readonly In[],
    limit: number,
    task: (item: In) => Promise<Out>,
  ): Promise<Out[]> {
    const results = new Array<Out>(items.length);
    let cursor = 0;
    const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
      while (cursor < items.length) {
        const index = cursor++;
        results[index] = await task(items[index]);
      }
    });
    await Promise.all(workers);
    return results;
  }

  // Run subtasks as parallel subagents, then run a second verification wave over
  // the results, and return both. MAX_TOTAL_SUBTASKS bounds how many the model can
  // queue; MAX_CONCURRENT bounds how many run at once.
  async function runWorkflow(
    model: string,
    rawSubtasks: unknown,
  ): Promise<{ output: string; isError: boolean }> {
    const allSubtasks = normalizeSubtasks(rawSubtasks);
    const subtasks = allSubtasks.slice(0, MAX_TOTAL_SUBTASKS);
    const dropped = allSubtasks.length - subtasks.length;
    if (subtasks.length === 0) {
      return { output: "Workflow error: no usable subtasks were provided.", isError: true };
    }
    console.error(`[workflow] fanning out ${subtasks.length} agents`);

    const runOne = async (prompt: string): Promise<string> => {
      try {
        return await journaled(prompt, () => runSubagent(model, prompt));
      } catch (error) {
        // Isolation boundary: one bad subagent should not end the run.
        const reason = error instanceof Error ? `${error.name}: ${error.message}` : String(error);
        return `(subagent failed: ${reason})`;
      }
    };

    const results = await mapWithLimit(subtasks, MAX_CONCURRENT, runOne);
    console.error(`[workflow] verifying ${results.length} results`);
    const verifyPrompts = subtasks.map((task, index) => verifyPromptFor(task, results[index]));
    const verdicts = await mapWithLimit(verifyPrompts, MAX_CONCURRENT, runOne);

    let joined = subtasks
      .map(
        (task, index) =>
          `[agent ${index + 1}: ${task}]\n${results[index]}\n\n[verify ${index + 1}]\n${verdicts[index]}`,
      )
      .join("\n\n");
    if (dropped > 0) {
      joined =
        `(note: ${dropped} subtasks beyond MAX_TOTAL_SUBTASKS=${MAX_TOTAL_SUBTASKS} were not ` +
        "run; rerun them in a follow-up Workflow call)\n\n" +
        joined;
    }
    return { output: joined, isError: false };
  }

csharp C#
  // Accept the subtasks input in whatever shape the model emits: an array, the array
  // JSON-encoded as a single string, or a newline-separated list.
  List<string> NormalizeSubtasks(JsonElement raw)
  {
      List<string> tasks = [];
      if (raw.ValueKind == JsonValueKind.Array)
      {
          tasks = raw.EnumerateArray()
              .Where(item => item.ValueKind == JsonValueKind.String)
              .Select(item => item.GetString()!)
              .ToList();
      }
      else if (raw.ValueKind == JsonValueKind.String)
      {
          var single = raw.GetString()!;
          try
          {
              tasks = JsonSerializer.Deserialize<List<string>>(single) ?? [];
          }
          catch (JsonException)
          {
              tasks = [.. single.Split('\n')];
          }
      }
      return tasks.Where(task => task != null).Select(task => task.Trim()).Where(task => task.Length > 0).ToList();
  }

  string VerifyPromptFor(string subtask, string result) =>
      "Adversarially verify the subagent result below: try to REFUTE it. Re-derive the "
      + "claims yourself with bash rather than trusting the result, and look for evidence "
      + "that contradicts them. Default to refuted if uncertain. Call report_findings with "
      + "summary 'refuted: <why>' or 'confirmed: <why>', citing the file:line or command "
      + "output that decided it.\n\n"
      + $"Subtask: {subtask}\n\nResult to verify:\n{result}";

  // Run subtasks as parallel subagents, then run a second verification wave over
  // the results, and return both. maxTotalSubtasks bounds how many the model can
  // queue; maxConcurrent bounds how many run at once.
  async Task<(string Output, bool IsError)> RunWorkflow(JsonElement rawSubtasks)
  {
      var allSubtasks = NormalizeSubtasks(rawSubtasks);
      var subtasks = allSubtasks.Take(maxTotalSubtasks).ToList();
      var dropped = allSubtasks.Count - subtasks.Count;
      if (subtasks.Count == 0)
      {
          return ("Workflow error: no usable subtasks were provided.", true);
      }
      Console.Error.WriteLine($"[workflow] fanning out {subtasks.Count} agents");

      using SemaphoreSlim gate = new(maxConcurrent);
      async Task<string> RunOne(string prompt)
      {
          await gate.WaitAsync();
          try
          {
              return await Journaled(prompt, () => RunSubagent(prompt));
          }
          catch (Exception error)
          {
              // Isolation boundary: one bad subagent should not end the run.
              return $"(subagent failed: {error.GetType().Name}: {error.Message})";
          }
          finally
          {
              gate.Release();
          }
      }

      var results = await Task.WhenAll(subtasks.Select(RunOne));
      Console.Error.WriteLine($"[workflow] verifying {results.Length} results");
      var verifyPrompts = subtasks.Select((task, index) => VerifyPromptFor(task, results[index])).ToList();
      var verdicts = await Task.WhenAll(verifyPrompts.Select(RunOne));

      var joined = string.Join(
          "\n\n",
          subtasks.Select((task, index) =>
              $"[agent {index + 1}: {task}]\n{results[index]}\n\n[verify {index + 1}]\n{verdicts[index]}"));
      if (dropped > 0)
      {
          joined = $"(note: {dropped} subtasks beyond maxTotalSubtasks={maxTotalSubtasks} were not run; "
              + "rerun them in a follow-up Workflow call)\n\n" + joined;
      }
      return (joined, false);
  }

go Go
  // normalizeSubtasks accepts the subtasks input in whatever shape the model emits: an
  // array, the array JSON-encoded as a single string, or a newline-separated list.
  func normalizeSubtasks(raw json.RawMessage) []string {
  	var tasks []string
  	if err := json.Unmarshal(raw, &tasks); err != nil {
  		var single string
  		if err := json.Unmarshal(raw, &single); err != nil {
  			return nil
  		}
  		if err := json.Unmarshal([]byte(single), &tasks); err != nil {
  			tasks = strings.Split(single, "\n")
  		}
  	}
  	cleaned := make([]string, 0, len(tasks))
  	for _, task := range tasks {
  		if trimmed := strings.TrimSpace(task); trimmed != "" {
  			cleaned = append(cleaned, trimmed)
  		}
  	}
  	return cleaned
  }

  func verifyPromptFor(subtask, result string) string {
  	return "Adversarially verify the subagent result below: try to REFUTE it. Re-derive the " +
  		"claims yourself with bash rather than trusting the result, and look for evidence " +
  		"that contradicts them. Default to refuted if uncertain. Call report_findings with " +
  		"summary 'refuted: <why>' or 'confirmed: <why>', citing the file:line or command " +
  		"output that decided it.\n\n" +
  		"Subtask: " + subtask + "\n\nResult to verify:\n" + result
  }

  // mapWithLimit runs task over items with at most limit goroutines in flight.
  func mapWithLimit(items []string, limit int, task func(string) string) []string {
  	results := make([]string, len(items))
  	semaphore := make(chan struct{}, limit)
  	var waitGroup sync.WaitGroup
  	for index, item := range items {
  		waitGroup.Add(1)
  		semaphore <- struct{}{}
  		go func() {
  			defer waitGroup.Done()
  			defer func() { <-semaphore }()
  			results[index] = task(item)
  		}()
  	}
  	waitGroup.Wait()
  	return results
  }

  // runWorkflow runs subtasks as parallel subagents, then runs a second verification wave
  // over the results, and returns both. maxTotalSubtasks bounds how many the model can
  // queue; maxConcurrent bounds how many run at once.
  func runWorkflow(ctx context.Context, model string, rawSubtasks json.RawMessage) (string, bool) {
  	allSubtasks := normalizeSubtasks(rawSubtasks)
  	subtasks := allSubtasks
  	if len(subtasks) > maxTotalSubtasks {
  		subtasks = subtasks[:maxTotalSubtasks]
  	}
  	dropped := len(allSubtasks) - len(subtasks)
  	if len(subtasks) == 0 {
  		return "Workflow error: no usable subtasks were provided.", true
  	}
  	fmt.Fprintf(os.Stderr, "[workflow] fanning out %d agents\n", len(subtasks))

  	runOne := func(prompt string) string {
  		report, err := journaled(prompt, func() (string, error) { return runSubagent(ctx, model, prompt) })
  		if err != nil {
  			// Isolation boundary: one bad subagent should not end the run.
  			return fmt.Sprintf("(subagent failed: %s)", err)
  		}
  		return report
  	}

  	results := mapWithLimit(subtasks, maxConcurrent, runOne)
  	fmt.Fprintf(os.Stderr, "[workflow] verifying %d results\n", len(results))
  	verifyPrompts := make([]string, len(subtasks))
  	for index, task := range subtasks {
  		verifyPrompts[index] = verifyPromptFor(task, results[index])
  	}
  	verdicts := mapWithLimit(verifyPrompts, maxConcurrent, runOne)

  	sections := make([]string, len(subtasks))
  	for index, task := range subtasks {
  		sections[index] = fmt.Sprintf("[agent %d: %s]\n%s\n\n[verify %d]\n%s",
  			index+1, task, results[index], index+1, verdicts[index])
  	}
  	joined := strings.Join(sections, "\n\n")
  	if dropped > 0 {
  		joined = fmt.Sprintf("(note: %d subtasks beyond maxTotalSubtasks=%d were not run; "+
  			"rerun them in a follow-up Workflow call)\n\n", dropped, maxTotalSubtasks) + joined
  	}
  	return joined, false
  }

java Java
  // Accept the subtasks input in whatever shape the model emits: an array, the array
  // JSON-encoded as a single string, or a newline-separated list.
  List<String> normalizeSubtasks(JsonValue raw) {
      List<String> tasks = new ArrayList<>();
      if (raw.asArray().isPresent()) {
          for (JsonValue item : (List<JsonValue>) raw.asArray().get()) {
              tasks.add(item.asString().isPresent() ? item.asStringOrThrow() : item.toString());
          }
      } else if (raw.asString().isPresent()) {
          String single = raw.asStringOrThrow();
          try {
              String[] parsed = new ObjectMapper().readValue(single, String[].class);
              if (parsed != null) {
                  for (String task : parsed) {
                      tasks.add(task);
                  }
              }
          } catch (JsonProcessingException error) {
              for (String task : single.split("\n")) {
                  tasks.add(task);
              }
          }
      }
      return tasks.stream()
              .filter(task -> task != null)
              .map(String::trim)
              .filter(task -> !task.isEmpty())
              .toList();
  }

  String verifyPromptFor(String subtask, String result) {
      return "Adversarially verify the subagent result below: try to REFUTE it. Re-derive the "
              + "claims yourself with bash rather than trusting the result, and look for evidence "
              + "that contradicts them. Default to refuted if uncertain. Call report_findings with "
              + "summary 'refuted: <why>' or 'confirmed: <why>', citing the file:line or command "
              + "output that decided it.\n\n"
              + "Subtask: " + subtask + "\n\nResult to verify:\n" + result;
  }

  List<String> runAll(ExecutorService pool, List<String> prompts, Model model) throws InterruptedException {
      List<Callable<String>> jobs = prompts.stream()
              .<Callable<String>>map(prompt -> () -> journaled(prompt, () -> runSubagent(model, prompt)))
              .toList();
      List<String> results = new ArrayList<>();
      for (Future<String> future : pool.invokeAll(jobs)) {
          try {
              results.add(future.get());
          } catch (ExecutionException | CancellationException error) {
              // Isolation boundary: one bad subagent should not end the run.
              Throwable cause = error.getCause() != null ? error.getCause() : error;
              results.add("(subagent failed: " + cause + ")");
          }
      }
      return results;
  }

  // Run subtasks as parallel subagents, then run a second verification wave over
  // the results, and return both. MAX_TOTAL_SUBTASKS bounds how many the model can
  // queue; MAX_CONCURRENT bounds how many run at once.
  ToolOutput runWorkflow(Model model, JsonValue rawSubtasks) throws InterruptedException {
      List<String> allSubtasks = normalizeSubtasks(rawSubtasks);
      List<String> subtasks = allSubtasks.stream().limit(MAX_TOTAL_SUBTASKS).toList();
      int dropped = allSubtasks.size() - subtasks.size();
      if (subtasks.isEmpty()) {
          return new ToolOutput("Workflow error: no usable subtasks were provided.", true);
      }
      System.err.println("[workflow] fanning out " + subtasks.size() + " agents");

      List<String> results;
      List<String> verdicts;
      try (ExecutorService pool = Executors.newFixedThreadPool(MAX_CONCURRENT, Thread.ofVirtual().factory())) {
          results = runAll(pool, subtasks, model);
          System.err.println("[workflow] verifying " + results.size() + " results");
          List<String> verifyPrompts = IntStream.range(0, subtasks.size())
                  .mapToObj(index -> verifyPromptFor(subtasks.get(index), results.get(index)))
                  .toList();
          verdicts = runAll(pool, verifyPrompts, model);
      }
      String joined = IntStream.range(0, subtasks.size())
              .mapToObj(index -> "[agent " + (index + 1) + ": " + subtasks.get(index) + "]\n" + results.get(index)
                      + "\n\n[verify " + (index + 1) + "]\n" + verdicts.get(index))
              .collect(Collectors.joining("\n\n"));
      if (dropped > 0) {
          joined = "(note: " + dropped + " subtasks beyond MAX_TOTAL_SUBTASKS=" + MAX_TOTAL_SUBTASKS
                  + " were not run; rerun them in a follow-up Workflow call)\n\n" + joined;
      }
      return new ToolOutput(joined, false);
  }

php PHP
  /**
   * Accept the subtasks input in whatever shape the model emits: an array, the array
   * JSON-encoded as a single string, or a newline-separated list.
   */
  function normalizeSubtasks(mixed $raw): array
  {
      if (is_string($raw)) {
          try {
              $raw = json_decode($raw, true, flags: JSON_THROW_ON_ERROR);
          } catch (JsonException) {
              $raw = str_contains($raw, "\n") ? explode("\n", $raw) : [$raw];
          }
      }
      if (!is_array($raw)) {
          return [];
      }
      $tasks = array_map('trim', array_filter($raw, 'is_string'));
      return array_values(array_filter($tasks, fn ($task) => $task !== ''));
  }

  function verifyPromptFor(string $subtask, string $result): string
  {
      return 'Adversarially verify the subagent result below: try to REFUTE it. Re-derive the '
          . 'claims yourself with bash rather than trusting the result, and look for evidence '
          . 'that contradicts them. Default to refuted if uncertain. Call report_findings with '
          . "summary 'refuted: <why>' or 'confirmed: <why>', citing the file:line or command "
          . "output that decided it.\n\n"
          . "Subtask: {$subtask}\n\nResult to verify:\n{$result}";
  }

  /**
   * Run subtasks through the journal, then run a second verification wave over the
   * results, and return both. PHP's standard runtime has no lightweight thread pool,
   * so both waves run sequentially here (MAX_CONCURRENT is unused); the SDK examples
   * in other languages fan them out in parallel.
   */
  function runWorkflow(Client $client, string $model, mixed $rawSubtasks): array
  {
      $allSubtasks = normalizeSubtasks($rawSubtasks);
      $subtasks = array_slice($allSubtasks, 0, MAX_TOTAL_SUBTASKS);
      $dropped = count($allSubtasks) - count($subtasks);
      if ($subtasks === []) {
          return ['Workflow error: no usable subtasks were provided.', true];
      }
      fwrite(STDERR, '[workflow] running ' . count($subtasks) . " agents\n");

      $runOne = function (string $prompt) use ($client, $model): string {
          try {
              return journaled($prompt, fn () => runSubagent($client, $model, $prompt));
          } catch (Throwable $error) {
              // Isolation boundary: one bad subagent should not end the run.
              return '(subagent failed: ' . $error::class . ': ' . $error->getMessage() . ')';
          }
      };

      $results = array_map($runOne, $subtasks);
      fwrite(STDERR, '[workflow] verifying ' . count($results) . " results\n");
      $verifyPrompts = array_map(verifyPromptFor(...), $subtasks, $results);
      $verdicts = array_map($runOne, $verifyPrompts);

      $sections = [];
      foreach ($subtasks as $index => $task) {
          $sections[] = '[agent ' . ($index + 1) . ": {$task}]\n{$results[$index]}"
              . "\n\n[verify " . ($index + 1) . "]\n{$verdicts[$index]}";
      }
      $joined = implode("\n\n", $sections);
      if ($dropped > 0) {
          $joined = '(note: ' . $dropped . ' subtasks beyond MAX_TOTAL_SUBTASKS=' . MAX_TOTAL_SUBTASKS
              . " were not run; rerun them in a follow-up Workflow call)\n\n" . $joined;
      }
      return [$joined, false];
  }

ruby Ruby
  # Accept the subtasks input in whatever shape the model emits: an array, the array
  # JSON-encoded as a single string, or a newline-separated list.
  def normalize_subtasks(raw)
    if raw.is_a?(String)
      begin
        raw = JSON.parse(raw)
      rescue JSON::ParserError
        raw = raw.include?("\n") ? raw.split("\n") : [raw]
      end
    end
    return [] unless raw.is_a?(Array)
    raw.select { |task| task.is_a?(String) }.map(&:strip).reject(&:empty?)
  end

  def verify_prompt_for(subtask, result)
    "Adversarially verify the subagent result below: try to REFUTE it. Re-derive the " \
      "claims yourself with bash rather than trusting the result, and look for evidence " \
      "that contradicts them. Default to refuted if uncertain. Call report_findings with " \
      "summary 'refuted: <why>' or 'confirmed: <why>', citing the file:line or command " \
      "output that decided it.\n\n" \
      "Subtask: #{subtask}\n\nResult to verify:\n#{result}"
  end

  # Map with a concurrency limit: at most `limit` threads are in flight at once.
  def map_with_limit(items, limit)
    results = Array.new(items.length)
    queue = Queue.new
    items.each_with_index { |item, index| queue << [index, item] }
    workers = Array.new([limit, items.length].min) do
      Thread.new do
        until queue.empty?
          index, item = queue.pop(true) rescue break
          results[index] = yield item
        end
      end
    end
    workers.each(&:join)
    results
  end

  # Run subtasks as parallel subagents, then run a second verification wave over
  # the results, and return both. MAX_TOTAL_SUBTASKS bounds how many the model can
  # queue; MAX_CONCURRENT bounds how many run at once.
  def run_workflow(model, raw_subtasks)
    all_subtasks = normalize_subtasks(raw_subtasks)
    subtasks = all_subtasks.first(MAX_TOTAL_SUBTASKS)
    dropped = all_subtasks.length - subtasks.length
    return ["Workflow error: no usable subtasks were provided.", true] if subtasks.empty?

    warn "[workflow] fanning out #{subtasks.length} agents"
    run_one = lambda do |prompt|
      journaled(prompt) { run_subagent(model, prompt) }
    rescue => error # isolation boundary: one bad subagent should not end the run
      "(subagent failed: #{error.class}: #{error.message})"
    end

    results = map_with_limit(subtasks, MAX_CONCURRENT, &run_one)
    warn "[workflow] verifying #{results.length} results"
    verify_prompts = subtasks.zip(results).map { |task, result| verify_prompt_for(task, result) }
    verdicts = map_with_limit(verify_prompts, MAX_CONCURRENT, &run_one)

    joined = subtasks.each_with_index.map do |task, index|
      "[agent #{index + 1}: #{task}]\n#{results[index]}\n\n[verify #{index + 1}]\n#{verdicts[index]}"
    end.join("\n\n")
    if dropped > 0
      joined =
        "(note: #{dropped} subtasks beyond MAX_TOTAL_SUBTASKS=#{MAX_TOTAL_SUBTASKS} were not " \
        "run; rerun them in a follow-up Workflow call)\n\n#{joined}"
    end
    [joined, false]
  end
  ```
</CodeGroup>


## Toggle the mode with mid-conversation system messages

Source: https://platform.claude.com/llms-full.txt#toggle-the-mode-with-mid-conversation-system-messages

The agent appends the user's message first, then any system messages that are due: the exit notice, the full mode text on entry, or the periodic refresher. Placing the system message after the user turn keeps every cached byte ahead of it untouched, and satisfies the placement rule that a system message follows a user turn.

<CodeGroup>
  ```bash cURL
  # One orchestration-mode turn: the mode reminder rides in the messages array as a
  # {"role": "system"} entry placed after the user turn it applies to. The response
  # stops at the first tool call. The agent loop that executes tool calls and fans
  # out subagents is shown in the SDK tabs; the Workflow description is condensed
  # here, the SDK examples carry the full standing-consent text.
  curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d @- <<'EOF'
  {
    "model": "claude-opus-5",
    "max_tokens": 64000,
    "system": "You are a helpful general-purpose agent. Answer the user's request directly.",
    "output_config": {"effort": "xhigh"},
    "tools": [
      {
        "name": "Workflow",
        "description": "Orchestrate a multiagent workflow: split a large task into independent subtasks and run them as parallel agents, then collect their results. Opt-in: only use this tool when the user explicitly asks for a workflow, or when a system message confirms that orchestration mode is on. Granularity: scope each subtask to a distinct concern rather than per line or file section; a review of a small module rarely needs more than about ten. Standing consent: while a system message confirms orchestration mode is on, author and run a workflow for every substantive task by default; work solo only on conversational turns or trivial mechanical edits.",
        "input_schema": {
          "type": "object",
          "properties": {
            "subtasks": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Independent subtask prompts to run as parallel agents"
            }
          },
          "required": ["subtasks"]
        }
      },
      {"type": "bash_20250124", "name": "bash"}
    ],
    "messages": [
      {
        "role": "user",
        "content": "Explore the current directory, then give a thorough review: what it does, code-quality issues, and concrete improvements."
      },
      {
        "role": "system",
        "content": "Orchestration mode is on: optimize for the most exhaustive, correct answer rather than the fastest one. Use the Workflow tool on every substantive task, sized to the problem's natural decomposition rather than the maximum the tool allows. See the Workflow tool's description for standing consent, granularity guidance, and quality patterns. Work solo only on conversational or trivial turns."
      }
    ]
  }
  EOF

bash CLI
  # One orchestration-mode turn: the mode reminder rides in the messages array as a
  # system-role entry placed after the user turn it applies to. The response stops
  # at the first tool call. The agent loop that executes tool calls and fans out
  # subagents is shown in the SDK tabs; the Workflow description is condensed here,
  # the SDK examples carry the full standing-consent text.
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 64000
  system: You are a helpful general-purpose agent. Answer the user's request directly.
  output_config: {effort: xhigh}
  tools:
    - name: Workflow
      description: >-
        Orchestrate a multiagent workflow: split a large task into independent
        subtasks and run them as parallel agents, then collect their results.
        Opt-in: only use this tool when the user explicitly asks for a workflow,
        or when a system message confirms that orchestration mode is on.
        Granularity: scope each subtask to a distinct concern rather than per
        line or file section; a review of a small module rarely needs more than
        about ten. Standing consent: while a system message confirms
        orchestration mode is on, author and run a workflow for every
        substantive task by default; work solo only on conversational turns or
        trivial mechanical edits.
      input_schema:
        type: object
        properties:
          subtasks:
            type: array
            items: {type: string}
            description: Independent subtask prompts to run as parallel agents
        required: [subtasks]
    - {type: bash_20250124, name: bash}
  messages:
    - role: user
      content: >-
        Explore the current directory, then give a thorough review: what it
        does, code-quality issues, and concrete improvements.
    - role: system
      content: >-
        Orchestration mode is on: optimize for the most exhaustive, correct
        answer rather than the fastest one. Use the Workflow tool on every
        substantive task, sized to the problem's natural decomposition rather
        than the maximum the tool allows. See the Workflow tool's description
        for standing consent, granularity guidance, and quality patterns. Work
        solo only on conversational or trivial turns.
  YAML

python Python
  class ModeAgent:
      """An agent loop whose orchestration mode is toggled with mid-conversation system messages."""

      def __init__(self, model: str, mode_on: bool = True):
          self.model = model
          self.mode_on = mode_on
          self.messages: list[dict] = []
          self._mode_announced = False
          self._exit_pending = False
          self._turns_since_reminder = 0

      def set_mode(self, mode_on: bool) -> None:
          """Turn the mode on or off. The notice is delivered with the next user turn."""
          if mode_on == self.mode_on:
              return
          if not mode_on:
              if self._mode_announced:
                  self._exit_pending = True
          else:
              self._exit_pending = False
          self.mode_on = mode_on

      def _due_system_messages(self) -> list[dict]:
          """System messages owed on this turn: an exit notice, the full mode text on entry,
          or a one-line refresher every TURNS_BETWEEN_REFRESHERS user turns."""
          due = []
          if self._exit_pending:
              self._exit_pending = False
              self._mode_announced = False
              due.append({"role": "system", "content": MODE_EXIT})
          if self.mode_on:
              if not self._mode_announced:
                  self._mode_announced = True
                  self._turns_since_reminder = 0
                  due.append({"role": "system", "content": MODE_ENTER})
              elif self._turns_since_reminder >= TURNS_BETWEEN_REFRESHERS:
                  self._turns_since_reminder = 0
                  due.append({"role": "system", "content": MODE_REFRESH})
          return due

      def turn(self, user_input: str) -> str:
          # Mid-conversation system messages follow the user turn they apply to, which keeps
          # the cached prefix ahead of them untouched.
          self.messages.append({"role": "user", "content": user_input})
          self.messages.extend(self._due_system_messages())
          self._turns_since_reminder += 1

          for _ in range(MAX_MAIN_TURNS):
              with client.messages.stream(
                  model=self.model,
                  max_tokens=64000,
                  system=SYSTEM_PROMPT,  # static for the whole session
                  output_config={"effort": EFFORT},
                  tools=[WORKFLOW_TOOL, BASH_TOOL],
                  messages=self.messages,
                  timeout=REQUEST_TIMEOUT_SECONDS,
              ) as stream:
                  response = stream.get_final_message()
              self.messages.append({"role": "assistant", "content": response.content})

              if response.stop_reason == "pause_turn":
                  continue
              if response.stop_reason != "tool_use":
                  text = "".join(block.text for block in response.content if block.type == "text")
                  if response.stop_reason == "max_tokens":
                      # Drop the truncated assistant message so later turns don't build on it.
                      self.messages.pop()
                      text += "\n\n(warning: response was truncated at max_tokens)"
                  return text

              tool_results = []
              for block in response.content:
                  if block.type != "tool_use":
                      continue
                  if block.name == "Workflow":
                      output, is_error = run_workflow(self.model, block.input.get("subtasks", []))
                  elif block.name == "bash":
                      output, is_error = handle_bash_block(block)
                  else:
                      output, is_error = f"unknown tool: {block.name}", True
                  tool_results.append(
                      {
                          "type": "tool_result",
                          "tool_use_id": block.id,
                          "content": output,
                          "is_error": is_error,
                      }
                  )
              self.messages.append({"role": "user", "content": tool_results})
          return "(hit the main loop turn limit before finishing)"

typescript TypeScript
  // An agent loop whose orchestration mode is toggled with mid-conversation system messages.
  class ModeAgent {
    private readonly model: string;
    private modeOn: boolean;
    private readonly messages: Anthropic.MessageParam[] = [];
    private modeAnnounced = false;
    private exitPending = false;
    private turnsSinceReminder = 0;

    constructor(model: string, modeOn = true) {
      this.model = model;
      this.modeOn = modeOn;
    }

    // Turn the mode on or off. The notice is delivered with the next user turn.
    setMode(modeOn: boolean): void {
      if (modeOn === this.modeOn) {
        return;
      }
      if (!modeOn) {
        if (this.modeAnnounced) {
          this.exitPending = true;
        }
      } else {
        this.exitPending = false;
      }
      this.modeOn = modeOn;
    }

    // System messages owed on this turn: an exit notice, the full mode text on entry,
    // or a one-line refresher every TURNS_BETWEEN_REFRESHERS user turns.
    private dueSystemMessages(): Anthropic.MessageParam[] {
      const due: Array<{ role: "system"; content: string }> = [];
      if (this.exitPending) {
        this.exitPending = false;
        this.modeAnnounced = false;
        due.push({ role: "system", content: MODE_EXIT });
      }
      if (this.modeOn) {
        if (!this.modeAnnounced) {
          this.modeAnnounced = true;
          this.turnsSinceReminder = 0;
          due.push({ role: "system", content: MODE_ENTER });
        } else if (this.turnsSinceReminder >= TURNS_BETWEEN_REFRESHERS) {
          this.turnsSinceReminder = 0;
          due.push({ role: "system", content: MODE_REFRESH });
        }
      }
      // The published SDK types message roles as "user" | "assistant"; typed support for
      // mid-conversation system messages ships with the SDK release that includes them.
      return due as unknown as Anthropic.MessageParam[];
    }

    async turn(userInput: string): Promise<string> {
      // Mid-conversation system messages follow the user turn they apply to, which keeps
      // the cached prefix ahead of them untouched.
      this.messages.push({ role: "user", content: userInput });
      this.messages.push(...this.dueSystemMessages());
      this.turnsSinceReminder += 1;

      for (let turn = 0; turn < MAX_MAIN_TURNS; turn++) {
        const response = await client.messages
          .stream(
            {
              model: this.model,
              max_tokens: 64000,
              system: SYSTEM_PROMPT, // static for the whole session
              output_config: { effort: EFFORT },
              tools: [WORKFLOW_TOOL, BASH_TOOL],
              messages: this.messages,
            },
            { signal: AbortSignal.timeout(REQUEST_TIMEOUT_SECONDS * 1000) },
          )
          .finalMessage();
        this.messages.push({ role: "assistant", content: response.content });

        if (response.stop_reason === "pause_turn") {
          continue;
        }
        if (response.stop_reason !== "tool_use") {
          let text = response.content
            .filter((block): block is Anthropic.TextBlock => block.type === "text")
            .map((block) => block.text)
            .join("");
          if (response.stop_reason === "max_tokens") {
            // Drop the truncated assistant message so later turns do not build on it.
            this.messages.pop();
            text += "\n\n(warning: response was truncated at max_tokens)";
          }
          return text;
        }

        const toolResults: Anthropic.ToolResultBlockParam[] = [];
        for (const block of response.content) {
          if (block.type !== "tool_use") {
            continue;
          }
          let output: string;
          let isError: boolean;
          if (block.name === "Workflow") {
            const input = block.input as { subtasks?: unknown };
            ({ output, isError } = await runWorkflow(this.model, input.subtasks ?? []));
          } else if (block.name === "bash") {
            ({ output, isError } = await handleBashBlock(block));
          } else {
            output = `unknown tool: ${block.name}`;
            isError = true;
          }
          toolResults.push({
            type: "tool_result",
            tool_use_id: block.id,
            content: output,
            is_error: isError,
          });
        }
        this.messages.push({ role: "user", content: toolResults });
      }
      return "(hit the main loop turn limit before finishing)";
    }
  }

csharp C#
  // An agent loop whose orchestration mode is toggled with mid-conversation system messages.
  List<MessageParam> messages = [];
  var modeOn = true;
  var modeAnnounced = false;
  var exitPending = false;
  var turnsSinceReminder = 0;

  // Turn the mode on or off. The notice is delivered with the next user turn.
  void SetMode(bool nextModeOn)
  {
      if (nextModeOn == modeOn)
      {
          return;
      }
      if (!nextModeOn)
      {
          if (modeAnnounced)
          {
              exitPending = true;
          }
      }
      else
      {
          exitPending = false;
      }
      modeOn = nextModeOn;
  }

  // The Role property is an open enum, so the mid-conversation "system" role can be assigned
  // as a raw string; a dedicated constant ships with the SDK release.
  MessageParam SystemMessage(string content) => new() { Role = "system", Content = content };

  // System messages owed on this turn: an exit notice, the full mode text on entry,
  // or a one-line refresher every turnsBetweenRefreshers user turns.
  List<MessageParam> DueSystemMessages()
  {
      List<MessageParam> due = [];
      if (exitPending)
      {
          exitPending = false;
          modeAnnounced = false;
          due.Add(SystemMessage(modeExit));
      }
      if (modeOn)
      {
          if (!modeAnnounced)
          {
              modeAnnounced = true;
              turnsSinceReminder = 0;
              due.Add(SystemMessage(modeEnter));
          }
          else if (turnsSinceReminder >= turnsBetweenRefreshers)
          {
              turnsSinceReminder = 0;
              due.Add(SystemMessage(modeRefresh));
          }
      }
      return due;
  }

  // Send one user turn through the loop, executing tool calls until the model stops.
  async Task<string> Turn(string userInput)
  {
      // Mid-conversation system messages follow the user turn they apply to, which keeps
      // the cached prefix ahead of them untouched.
      messages.Add(new() { Role = Role.User, Content = userInput });
      messages.AddRange(DueSystemMessages());
      turnsSinceReminder++;

      for (var turn = 0; turn < maxMainTurns; turn++)
      {
          using var deadline = new CancellationTokenSource(TimeSpan.FromSeconds(requestTimeoutSeconds));
          var response = await client.Messages.Create(new MessageCreateParams
          {
              Model = model,
              MaxTokens = requestMaxTokens,
              System = systemPrompt, // static for the whole session
              OutputConfig = new OutputConfig { Effort = effort },
              Tools = [workflowTool, bashTool],
              Messages = messages,
          }, cancellationToken: deadline.Token);
          messages.Add(new()
          {
              Role = Role.Assistant,
              Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList(),
          });

          if (response.StopReason == StopReason.PauseTurn)
          {
              continue;
          }
          if (response.StopReason != StopReason.ToolUse)
          {
              var text = string.Concat(
                  response.Content.Select(block => block.TryPickText(out var textBlock) ? textBlock.Text : ""));
              if (response.StopReason == StopReason.MaxTokens)
              {
                  // Drop the truncated assistant message so the next turn does not build on it.
                  messages.RemoveAt(messages.Count - 1);
                  text += "\n\n(warning: response was truncated at max_tokens)";
              }
              return text;
          }

          List<ContentBlockParam> toolResults = [];
          foreach (var block in response.Content)
          {
              if (!block.TryPickToolUse(out var toolUse))
              {
                  continue;
              }
              string output;
              bool isError;
              if (toolUse.Name == "Workflow")
              {
                  toolUse.Input.TryGetValue("subtasks", out var rawSubtasks);
                  (output, isError) = await RunWorkflow(rawSubtasks);
              }
              else if (toolUse.Name == "bash")
              {
                  (output, isError) = await HandleBashBlock(toolUse);
              }
              else
              {
                  output = $"unknown tool: {toolUse.Name}";
                  isError = true;
              }
              toolResults.Add(new ToolResultBlockParam(toolUse.ID) { Content = output, IsError = isError });
          }
          messages.Add(new() { Role = Role.User, Content = toolResults });
      }
      return "(hit the main loop turn limit before finishing)";
  }

go Go
  // modeAgent is an agent loop whose orchestration mode is toggled with mid-conversation
  // system messages.
  type modeAgent struct {
  	model              string
  	modeOn             bool
  	messages           []anthropic.MessageParam
  	modeAnnounced      bool
  	exitPending        bool
  	turnsSinceReminder int
  }

  func newModeAgent(model string) *modeAgent {
  	return &modeAgent{model: model, modeOn: true}
  }

  // setMode turns the mode on or off. The notice is delivered with the next user turn.
  func (agent *modeAgent) setMode(modeOn bool) {
  	if modeOn == agent.modeOn {
  		return
  	}
  	if !modeOn {
  		if agent.modeAnnounced {
  			agent.exitPending = true
  		}
  	} else {
  		agent.exitPending = false
  	}
  	agent.modeOn = modeOn
  }

  // dueSystemMessages returns the system messages owed on this turn: an exit notice, the
  // full mode text on entry, or a one-line refresher every turnsBetweenRefreshers user turns.
  func (agent *modeAgent) dueSystemMessages() []anthropic.MessageParam {
  	// MessageParamRole is an open string type, so the mid-conversation "system" role can
  	// be expressed directly; a dedicated constant ships with the SDK release.
  	systemMessage := func(content string) anthropic.MessageParam {
  		return anthropic.MessageParam{
  			Role:    anthropic.MessageParamRole("system"),
  			Content: []anthropic.ContentBlockParamUnion{anthropic.NewTextBlock(content)},
  		}
  	}
  	var due []anthropic.MessageParam
  	if agent.exitPending {
  		agent.exitPending = false
  		agent.modeAnnounced = false
  		due = append(due, systemMessage(modeExit))
  	}
  	if agent.modeOn {
  		if !agent.modeAnnounced {
  			agent.modeAnnounced = true
  			agent.turnsSinceReminder = 0
  			due = append(due, systemMessage(modeEnter))
  		} else if agent.turnsSinceReminder >= turnsBetweenRefreshers {
  			agent.turnsSinceReminder = 0
  			due = append(due, systemMessage(modeRefresh))
  		}
  	}
  	return due
  }

  // turn sends one user turn through the loop, executing tool calls until the model stops.
  func (agent *modeAgent) turn(ctx context.Context, userInput string) (string, error) {
  	// Mid-conversation system messages follow the user turn they apply to, which keeps
  	// the cached prefix ahead of them untouched.
  	agent.messages = append(agent.messages, anthropic.NewUserMessage(anthropic.NewTextBlock(userInput)))
  	agent.messages = append(agent.messages, agent.dueSystemMessages()...)
  	agent.turnsSinceReminder++

  	for range maxMainTurns {
  		var response anthropic.Message
  		err := func() error {
  			ctx, cancel := context.WithTimeout(ctx, requestTimeoutSeconds*time.Second)
  			defer cancel()
  			stream := client.Messages.NewStreaming(ctx, anthropic.MessageNewParams{
  				Model:        agent.model,
  				MaxTokens:    64000,
  				System:       []anthropic.TextBlockParam{{Text: systemPrompt}}, // static for the whole session
  				OutputConfig: anthropic.OutputConfigParam{Effort: effort},
  				Tools:        []anthropic.ToolUnionParam{workflowTool, bashTool},
  				Messages:     agent.messages,
  			})
  			defer stream.Close()
  			for stream.Next() {
  				if err := response.Accumulate(stream.Current()); err != nil {
  					return err
  				}
  			}
  			return stream.Err()
  		}()
  		if err != nil {
  			return "", err
  		}
  		agent.messages = append(agent.messages, response.ToParam())

  		if response.StopReason == anthropic.StopReasonPauseTurn {
  			continue
  		}
  		if response.StopReason != anthropic.StopReasonToolUse {
  			var text strings.Builder
  			for _, block := range response.Content {
  				if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  					text.WriteString(textBlock.Text)
  				}
  			}
  			if response.StopReason == anthropic.StopReasonMaxTokens {
  				// Drop the truncated assistant message rather than leave a clipped turn in history.
  				agent.messages = agent.messages[:len(agent.messages)-1]
  				text.WriteString("\n\n(warning: response was truncated at max_tokens)")
  			}
  			return text.String(), nil
  		}

  		var toolResults []anthropic.ContentBlockParamUnion
  		for _, block := range response.Content {
  			toolUse, ok := block.AsAny().(anthropic.ToolUseBlock)
  			if !ok {
  				continue
  			}
  			var output string
  			var isError bool
  			switch toolUse.Name {
  			case "Workflow":
  				var input struct {
  					Subtasks json.RawMessage `json:"subtasks"`
  				}
  				if err := json.Unmarshal(toolUse.Input, &input); err != nil {
  					output, isError = fmt.Sprintf("Workflow error: could not parse input: %s", err), true
  				} else {
  					output, isError = runWorkflow(ctx, agent.model, input.Subtasks)
  				}
  			case "bash":
  				output, isError = handleBashBlock(ctx, toolUse)
  			default:
  				output, isError = fmt.Sprintf("unknown tool: %s", toolUse.Name), true
  			}
  			toolResults = append(toolResults, anthropic.NewToolResultBlock(toolUse.ID, output, isError))
  		}
  		agent.messages = append(agent.messages, anthropic.NewUserMessage(toolResults...))
  	}
  	return "(hit the main loop turn limit before finishing)", nil
  }

java Java
  // An agent loop whose orchestration mode is toggled with mid-conversation system messages.
  class ModeAgent {
      private final Model model;
      private boolean modeOn;
      private final List<MessageParam> messages = new ArrayList<>();
      private boolean modeAnnounced = false;
      private boolean exitPending = false;
      private int turnsSinceReminder = 0;

      ModeAgent(Model model) {
          this(model, true);
      }

      ModeAgent(Model model, boolean modeOn) {
          this.model = model;
          this.modeOn = modeOn;
      }

      // Turn the mode on or off. The notice is delivered with the next user turn.
      void setMode(boolean modeOn) {
          if (modeOn == this.modeOn) {
              return;
          }
          if (!modeOn) {
              if (modeAnnounced) {
                  exitPending = true;
              }
          } else {
              exitPending = false;
          }
          this.modeOn = modeOn;
      }

      // System messages owed on this turn: an exit notice, the full mode text on entry,
      // or a one-line refresher every TURNS_BETWEEN_REFRESHERS user turns.
      private List<MessageParam> dueSystemMessages() {
          List<MessageParam> due = new ArrayList<>();
          if (exitPending) {
              exitPending = false;
              modeAnnounced = false;
              due.add(systemMessage(MODE_EXIT));
          }
          if (modeOn) {
              if (!modeAnnounced) {
                  modeAnnounced = true;
                  turnsSinceReminder = 0;
                  due.add(systemMessage(MODE_ENTER));
              } else if (turnsSinceReminder >= TURNS_BETWEEN_REFRESHERS) {
                  turnsSinceReminder = 0;
                  due.add(systemMessage(MODE_REFRESH));
              }
          }
          return due;
      }

      // MessageParam.Role is an open enum, so the mid-conversation "system" role can be
      // expressed with Role.of; a dedicated constant ships with the SDK release.
      private MessageParam systemMessage(String content) {
          return MessageParam.builder()
                  .role(MessageParam.Role.of("system"))
                  .content(content)
                  .build();
      }

      // Send one user turn through the loop, executing tool calls until the model stops.
      String turn(String userInput) throws InterruptedException {
          // Mid-conversation system messages follow the user turn they apply to, which keeps
          // the cached prefix ahead of them untouched.
          messages.add(MessageParam.builder().role(MessageParam.Role.USER).content(userInput).build());
          messages.addAll(dueSystemMessages());
          turnsSinceReminder++;

          for (int turn = 0; turn < MAX_MAIN_TURNS; turn++) {
              MessageCreateParams params = MessageCreateParams.builder()
                      .model(model)
                      .maxTokens(64000L)
                      .system(SYSTEM_PROMPT) // static for the whole session
                      .outputConfig(OutputConfig.builder().effort(EFFORT).build())
                      .addTool(WORKFLOW_TOOL)
                      .addTool(BASH_TOOL)
                      .messages(messages)
                      .build();
              MessageAccumulator accumulator = MessageAccumulator.create();
              try (var stream = client.messages().createStreaming(params, REQUEST_OPTIONS)) {
                  stream.stream().forEach(accumulator::accumulate);
              }
              Message response = accumulator.message();
              messages.add(response.toParam());

              StopReason stopReason = response.stopReason().orElse(null);
              if (StopReason.PAUSE_TURN.equals(stopReason)) {
                  continue;
              }
              if (!StopReason.TOOL_USE.equals(stopReason)) {
                  String text = response.content().stream()
                          .flatMap(block -> block.text().stream())
                          .map(TextBlock::text)
                          .collect(Collectors.joining());
                  if (StopReason.MAX_TOKENS.equals(stopReason)) {
                      // Drop the truncated assistant message so it does not poison later turns.
                      messages.removeLast();
                      text += "\n\n(warning: response was truncated at max_tokens)";
                  }
                  return text;
              }

              List<ContentBlockParam> toolResults = new ArrayList<>();
              for (ContentBlock block : response.content()) {
                  if (block.toolUse().isEmpty()) {
                      continue;
                  }
                  ToolUseBlock toolUse = block.toolUse().get();
                  ToolOutput result = switch (toolUse.name()) {
                      case "Workflow" -> {
                          Map<String, JsonValue> input =
                                  (Map<String, JsonValue>) toolUse._input().asObject().orElse(Map.of());
                          JsonValue rawSubtasks = input.getOrDefault("subtasks", JsonValue.from(List.of()));
                          yield runWorkflow(model, rawSubtasks);
                      }
                      case "bash" -> handleBashBlock(toolUse);
                      default -> new ToolOutput("unknown tool: " + toolUse.name(), true);
                  };
                  toolResults.add(ContentBlockParam.ofToolResult(ToolResultBlockParam.builder()
                          .toolUseId(toolUse.id())
                          .content(result.output())
                          .isError(result.isError())
                          .build()));
              }
              messages.add(MessageParam.builder()
                      .role(MessageParam.Role.USER)
                      .contentOfBlockParams(toolResults)
                      .build());
          }
          return "(hit the main loop turn limit before finishing)";
      }
  }

php PHP
  /** An agent loop whose orchestration mode is toggled with mid-conversation system messages. */
  class ModeAgent
  {
      private array $messages = [];
      private bool $modeAnnounced = false;
      private bool $exitPending = false;
      private int $turnsSinceReminder = 0;

      public function __construct(
          private readonly Client $client,
          private readonly string $model,
          private bool $modeOn = true,
      ) {
      }

      /** Turn the mode on or off. The notice is delivered with the next user turn. */
      public function setMode(bool $modeOn): void
      {
          if ($modeOn === $this->modeOn) {
              return;
          }
          if ($modeOn) {
              $this->exitPending = false;
          } elseif ($this->modeAnnounced) {
              $this->exitPending = true;
          }
          $this->modeOn = $modeOn;
      }

      public function turn(string $userInput): string
      {
          // Mid-conversation system messages follow the user turn they apply to, which keeps
          // the cached prefix ahead of them untouched.
          $this->messages[] = ['role' => 'user', 'content' => $userInput];
          array_push($this->messages, ...$this->dueSystemMessages());
          $this->turnsSinceReminder++;

          for ($turn = 0; $turn < MAX_MAIN_TURNS; $turn++) {
              $stream = $this->client->messages->createStream(
                  model: $this->model,
                  maxTokens: 64000,
                  system: SYSTEM_PROMPT, // static for the whole session
                  outputConfig: ['effort' => EFFORT],
                  tools: [WORKFLOW_TOOL, BASH_TOOL],
                  messages: $this->messages,
                  requestOptions: ['timeout' => REQUEST_TIMEOUT_SECONDS],
              );
              [$content, $stopReason] = drainMessageStream($stream);
              $this->messages[] = ['role' => 'assistant', 'content' => $content];

              if ($stopReason === 'pause_turn') {
                  continue;
              }
              if ($stopReason !== 'tool_use') {
                  $text = '';
                  foreach ($content as $block) {
                      if ($block instanceof TextBlock) {
                          $text .= $block->text;
                      }
                  }
                  if ($stopReason === 'max_tokens') {
                      // Drop the truncated assistant message so the next turn does not build on it.
                      array_pop($this->messages);
                      $text .= "\n\n(warning: response was truncated at max_tokens)";
                  }
                  return $text;
              }

              $toolResults = [];
              foreach ($content as $block) {
                  if (!$block instanceof ToolUseBlock) {
                      continue;
                  }
                  if ($block->name === 'Workflow') {
                      [$output, $isError] =
                          runWorkflow($this->client, $this->model, $block->input['subtasks'] ?? []);
                  } elseif ($block->name === 'bash') {
                      [$output, $isError] = handleBashBlock($block);
                  } else {
                      $output = "unknown tool: {$block->name}";
                      $isError = true;
                  }
                  $toolResults[] = [
                      'type' => 'tool_result',
                      'tool_use_id' => $block->id,
                      'content' => $output,
                      'is_error' => $isError,
                  ];
              }
              $this->messages[] = ['role' => 'user', 'content' => $toolResults];
          }
          return '(hit the main loop turn limit before finishing)';
      }

      /**
       * System messages owed on this turn: an exit notice, the full mode text on entry,
       * or a one-line refresher every TURNS_BETWEEN_REFRESHERS user turns.
       */
      private function dueSystemMessages(): array
      {
          $due = [];
          if ($this->exitPending) {
              $this->exitPending = false;
              $this->modeAnnounced = false;
              $due[] = ['role' => 'system', 'content' => MODE_EXIT];
          }
          if ($this->modeOn) {
              if (!$this->modeAnnounced) {
                  $this->modeAnnounced = true;
                  $this->turnsSinceReminder = 0;
                  $due[] = ['role' => 'system', 'content' => MODE_ENTER];
              } elseif ($this->turnsSinceReminder >= TURNS_BETWEEN_REFRESHERS) {
                  $this->turnsSinceReminder = 0;
                  $due[] = ['role' => 'system', 'content' => MODE_REFRESH];
              }
          }
          return $due;
      }
  }

ruby Ruby
  # An agent loop whose orchestration mode is toggled with mid-conversation system messages.
  class ModeAgent
    def initialize(model, mode_on: true)
      @model = model
      @mode_on = mode_on
      @messages = []
      @mode_announced = false
      @exit_pending = false
      @turns_since_reminder = 0
    end

    # Turn the mode on or off. The notice is delivered with the next user turn.
    def set_mode(mode_on)
      return if mode_on == @mode_on

      if mode_on
        @exit_pending = false
      else
        @exit_pending = true if @mode_announced
      end
      @mode_on = mode_on
    end

    def turn(user_input)
      # Mid-conversation system messages follow the user turn they apply to, which keeps
      # the cached prefix ahead of them untouched.
      @messages << {role: "user", content: user_input}
      @messages.concat(due_system_messages)
      @turns_since_reminder += 1

      MAX_MAIN_TURNS.times do
        stream = CLIENT.messages.stream(
          model: @model,
          max_tokens: 64_000,
          system_: SYSTEM_PROMPT, # static for the whole session
          output_config: {effort: EFFORT},
          tools: [WORKFLOW_TOOL, BASH_TOOL],
          messages: @messages,
          request_options: {timeout: REQUEST_TIMEOUT_SECONDS}
        )
        response = stream.accumulated_message
        @messages << {role: "assistant", content: assistant_content_param(response.content)}

        next if response.stop_reason == :pause_turn

        unless response.stop_reason == :tool_use
          text = response.content.select { |block| block.type == :text }.map(&:text).join
          if response.stop_reason == :max_tokens
            @messages.pop # drop the truncated assistant message from the history
            text += "\n\n(warning: response was truncated at max_tokens)"
          end
          return text
        end

        tool_results = []
        response.content.each do |block|
          next unless block.type == :tool_use

          input = parse_tool_input(block.input)
          case block.name
          when "Workflow"
            output, is_error = run_workflow(@model, input["subtasks"] || [])
          when "bash"
            output, is_error = handle_bash_block(block)
          else
            output, is_error = "unknown tool: #{block.name}", true
          end
          tool_results << {
            type: "tool_result",
            tool_use_id: block.id,
            content: output,
            is_error: is_error
          }
        end
        @messages << {role: "user", content: tool_results}
      end
      "(hit the main loop turn limit before finishing)"
    end

    private

    # System messages owed on this turn: an exit notice, the full mode text on entry,
    # or a one-line refresher every TURNS_BETWEEN_REFRESHERS user turns.
    def due_system_messages
      due = []
      if @exit_pending
        @exit_pending = false
        @mode_announced = false
        due << {role: "system", content: MODE_EXIT}
      end
      if @mode_on
        if !@mode_announced
          @mode_announced = true
          @turns_since_reminder = 0
          due << {role: "system", content: MODE_ENTER}
        elsif @turns_since_reminder >= TURNS_BETWEEN_REFRESHERS
          @turns_since_reminder = 0
          due << {role: "system", content: MODE_REFRESH}
        end
      end
      due
    end
  end
  ```
</CodeGroup>


## Run it

Source: https://platform.claude.com/llms-full.txt#run-it

<Warning>
  The bash tool in this example runs model-written commands directly on your machine with no sandbox, and the fan-out runs several of those agents in parallel. Run it in a directory and environment you are comfortable exposing, and add sandboxing before adapting it for anything beyond local experimentation.
</Warning>

<CodeGroup>
  ```python Python
  if __name__ == "__main__":
      task = (
          sys.argv[1]
          if len(sys.argv) > 1
          else "Explore the current directory, then give a thorough review: what it does, "
          "code-quality issues, and concrete improvements."
      )
      agent = ModeAgent(MODEL)
      print(agent.turn(task))
      agent.set_mode(False)
      print(agent.turn("Briefly summarize what you found above, no fan-out needed."))

typescript TypeScript
  const task =
    process.argv[2] ??
    "Explore the current directory, then give a thorough review: what it does, " +
      "code-quality issues, and concrete improvements.";
  const agent = new ModeAgent(MODEL);
  console.log(await agent.turn(task));
  agent.setMode(false);
  console.log(await agent.turn("Briefly summarize what you found above, no fan-out needed."));

csharp C#
  var task = args.Length > 0
      ? args[0]
      : "Explore the current directory, then give a thorough review: what it does, "
          + "code-quality issues, and concrete improvements.";
  Console.WriteLine(await Turn(task));
  SetMode(false);
  Console.WriteLine(await Turn("Briefly summarize what you found above, no fan-out needed."));

go Go
  func main() {
  	if err := run(context.Background()); err != nil {
  		log.Fatal(err)
  	}
  }

  func run(ctx context.Context) error {
  	if docTestMode {
  		defer os.RemoveAll(workDir)
  	}
  	task := "Explore the current directory, then give a thorough review: what it does, " +
  		"code-quality issues, and concrete improvements."
  	if len(os.Args) > 1 {
  		task = os.Args[1]
  	}
  	agent := newModeAgent(modelID)
  	answer, err := agent.turn(ctx, task)
  	if err != nil {
  		return err
  	}
  	fmt.Println(answer)

  	agent.setMode(false)
  	summary, err := agent.turn(ctx, "Briefly summarize what you found above, no fan-out needed.")
  	if err != nil {
  		return err
  	}
  	fmt.Println(summary)
  	return nil
  }

java Java
  void main(String[] args) throws InterruptedException {
      String task = args.length > 0
              ? args[0]
              : "Explore the current directory, then give a thorough review: what it does, "
                      + "code-quality issues, and concrete improvements.";
      ModeAgent agent = new ModeAgent(MODEL);
      IO.println(agent.turn(task));
      agent.setMode(false);
      IO.println(agent.turn("Briefly summarize what you found above, no fan-out needed."));
  }

php PHP
  $task = $argv[1] ??
      'Explore the current directory, then give a thorough review: what it does, '
      . 'code-quality issues, and concrete improvements.';
  $agent = new ModeAgent($client, MODEL);
  echo $agent->turn($task), PHP_EOL;
  $agent->setMode(false);
  echo $agent->turn('Briefly summarize what you found above, no fan-out needed.'), PHP_EOL;

ruby Ruby
  task = ARGV[0] ||
    "Explore the current directory, then give a thorough review: what it does, " \
    "code-quality issues, and concrete improvements."
  agent = ModeAgent.new(MODEL)
  puts agent.turn(task)
  agent.set_mode(false)
  puts agent.turn("Briefly summarize what you found above, no fan-out needed.")

bash
python orchestration_mode.py "Review this repository for flaky tests and propose fixes."
```

With the mode on, expect the model to scout with a few bash commands, dispatch the Workflow tool unprompted, and synthesize the subagent reports into a final answer. Trivial or conversational requests stay solo, as the reminder instructs.


## Toward a production harness

Source: https://platform.claude.com/llms-full.txt#toward-a-production-harness

This example is deliberately small. A harness meant for real workloads would typically add:

* **Sandboxed orchestration scripts:** let the model emit a short orchestration program (branching, loops, and reduce steps) and run it inside an isolated interpreter, rather than accepting only a flat list of subtask strings.
* **Durable journaling:** replace the local JSON file with a store that survives process restarts and is safe under concurrent writers across machines.
* **Budget enforcement:** track total subagents launched across the whole session, not just per Workflow call, and refuse to exceed a hard cap so a runaway plan cannot exhaust your quota.

The patterns in this example (the mode reminders, standing consent in the tool description, journaling, and a verification wave) carry over unchanged; only the execution substrate around them gets more robust.


## Related

Source: https://platform.claude.com/llms-full.txt#related

<CardGroup cols={2}>
  <Card title="Mid-conversation system messages" icon="message" href="https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages">
    The mechanism the mode reminders use, and how it interacts with prompt caching.
  </Card>

  <Card title="Effort" icon="gauge" href="https://platform.claude.com/docs/en/build-with-claude/effort">
    The effort levels the API accepts and how to choose one.
  </Card>

  <Card title="Tool use with Claude" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview">
    Defining tools, handling tool calls, and tool results.
  </Card>

  <Card title="Bash tool" icon="terminal" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool">
    The Anthropic-defined bash tool this example executes locally.
  </Card>
</CardGroup>


---
title: Cache diagnostics
url: https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics
description: Diagnose unexpected prompt cache misses by comparing consecutive requests and identifying exactly where the prompt prefix diverged.
---


## Compatibility

Source: https://platform.claude.com/llms-full.txt#compatibility-9

- Status: Beta
- [Beta header](https://platform.claude.com/docs/en/api/beta-headers): `cache-diagnosis-2026-04-07`
- [ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): eligible (excludes [Covered Models](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements))
- Platforms: Claude API (beta); not available on Claude Platform on AWS, Amazon Bedrock, Google Cloud, Microsoft Foundry

[Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) cuts latency and cost significantly, but only when the beginning of your prompt is byte-for-byte identical to a recent request. A reordered tool, a timestamp interpolated into your system prompt, or an edit to an earlier message can silently invalidate the cache. Without cache diagnostics, the only signal is `usage.cache_read_input_tokens` dropping to zero, with no indication of what changed.

Cache diagnostics closes that gap. Pass the `id` of your previous response, and the API compares the two requests and tells you where they diverged (the model, the system prompt, the tools, or the message history) so you can fix the root cause instead of guessing.


## How cache diagnostics works

Source: https://platform.claude.com/llms-full.txt#how-cache-diagnostics-works

When the beta header is present, the API stores a lightweight fingerprint of each request, keyed by the response `id`. On your next request, include that `id` as `diagnostics.previous_message_id`. The API rebuilds the fingerprint for the new request, compares it against the stored one, and attaches a `diagnostics` object to the response describing the first point of divergence.

The comparison is about request structure, independent of whether the cache actually hit. See [Reading diagnostics alongside usage](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics#reading-diagnostics-alongside-usage) for how to combine the `diagnostics` result with `usage.cache_read_input_tokens`.

Fingerprints contain only hashes and token-count estimates (never raw prompt content), are retained for a limited time, are scoped to your organization and workspace, and are not used for any other purpose.


## Basic usage

Source: https://platform.claude.com/llms-full.txt#basic-usage-4

Send the beta header on every turn. On the first turn, pass `"previous_message_id": null` to opt in without a prior message to compare against. On subsequent turns, pass the `id` from the previous response.

<CodeGroup>
  ```bash cURL
  # Turn 1: establish the cache and opt in to diagnostics
  response=$(curl -sS --fail-with-body https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: cache-diagnosis-2026-04-07" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "cache_control": {"type": "ephemeral"},
      "system": "You are an AI assistant analyzing a large document. <document>...</document>",
      "messages": [{"role": "user", "content": "Summarize section 1."}],
      "diagnostics": {"previous_message_id": null}
    }')
  jq '{id, diagnostics}' <<< "$response"
  message_id=$(jq -r '.id' <<< "$response")

  # Turn 2: reference the previous turn so the API can compare prefixes
  curl -sS --fail-with-body https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: cache-diagnosis-2026-04-07" \
    -H "content-type: application/json" \
    -d @- <<EOF | jq '{id, diagnostics}'  # diagnostics: null means no divergence was found
  {
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "cache_control": {"type": "ephemeral"},
    "system": "You are an AI assistant analyzing a large document. <document>...</document>",
    "messages": [
      {"role": "user", "content": "Summarize section 1."},
      {"role": "assistant", "content": "Section 1 covers..."},
      {"role": "user", "content": "Now summarize section 2."}
    ],
    "diagnostics": {"previous_message_id": "$message_id"}
  }
  EOF

bash CLI
  # Turn 1
  turn1=$(ant beta:messages create \
    --beta cache-diagnosis-2026-04-07 \
    --transform '{id,usage,diagnostics}' <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  cache_control:
    type: ephemeral
  system: "You are an AI assistant analyzing a large document. <document>...</document>"
  messages:
    - role: user
      content: Summarize section 1.
  diagnostics:
    previous_message_id: null
  YAML
  )
  printf '%s\n' "$turn1"

  # Turn 2: pass the id from turn 1 as previous_message_id
  message_id=$(jq -r '.id' <<<"$turn1")
  ant beta:messages create \
    --beta cache-diagnosis-2026-04-07 \
    --transform '{id,usage,diagnostics}' <<YAML
  model: claude-opus-5
  max_tokens: 1024
  cache_control:
    type: ephemeral
  system: "You are an AI assistant analyzing a large document. <document>...</document>"
  messages:
    - role: user
      content: Summarize section 1.
    - role: assistant
      content: Section 1 covers...
    - role: user
      content: Now summarize section 2.
  diagnostics:
    previous_message_id: $message_id
  YAML

python Python
  client = anthropic.Anthropic()

  SYSTEM = "You are an AI assistant analyzing a large document. <document>...</document>"

  # Turn 1: opt in with previous_message_id=None
  r1 = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      cache_control={"type": "ephemeral"},
      system=SYSTEM,
      messages=[{"role": "user", "content": "Summarize section 1."}],
      diagnostics={"previous_message_id": None},
      betas=["cache-diagnosis-2026-04-07"],
  )

  # Turn 2: reference the previous response id
  r2 = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      cache_control={"type": "ephemeral"},
      system=SYSTEM,
      messages=[
          {"role": "user", "content": "Summarize section 1."},
          {"role": "assistant", "content": r1.content},
          {"role": "user", "content": "Now summarize section 2."},
      ],
      diagnostics={"previous_message_id": r1.id},
      betas=["cache-diagnosis-2026-04-07"],
  )

  diagnostics = r2.diagnostics
  if diagnostics is None:
      print("No divergence detected.")
  elif diagnostics.cache_miss_reason is None:
      print("Comparison still pending.")
  else:
      print(f"cache_miss_reason: {diagnostics.cache_miss_reason.type}")

typescript TypeScript
  const client = new Anthropic();

  const SYSTEM = "You are an AI assistant analyzing a large document. <document>...</document>";

  // Turn 1: opt in with previous_message_id: null
  const r1 = await client.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    cache_control: { type: "ephemeral" },
    system: SYSTEM,
    messages: [{ role: "user", content: "Summarize section 1." }],
    diagnostics: { previous_message_id: null },
    betas: ["cache-diagnosis-2026-04-07"]
  });

  // Turn 2: reference the previous response id
  const r2 = await client.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    cache_control: { type: "ephemeral" },
    system: SYSTEM,
    messages: [
      { role: "user", content: "Summarize section 1." },
      { role: "assistant", content: r1.content },
      { role: "user", content: "Now summarize section 2." }
    ],
    diagnostics: { previous_message_id: r1.id },
    betas: ["cache-diagnosis-2026-04-07"]
  });

  if (r2.diagnostics === null) {
    console.log("No divergence detected.");
  } else if (r2.diagnostics.cache_miss_reason === null) {
    console.log("Comparison still pending.");
  } else {
    console.log(`cache_miss_reason: ${r2.diagnostics.cache_miss_reason.type}`);
  }

csharp C#
  AnthropicClient client = new();

  var system = "You are an AI assistant analyzing a large document. <document>...</document>";

  var r1 = await client.Beta.Messages.Create(
      new()
      {
          Model = Messages::Model.ClaudeOpus5,
          MaxTokens = 1024,
          CacheControl = new(),
          System = system,
          Messages =
          [
              new() { Role = Role.User, Content = "Summarize section 1." },
          ],
          Diagnostics = new() { PreviousMessageID = null },
          Betas = [AnthropicBeta.CacheDiagnosis2026_04_07],
      }
  );

  var r2 = await client.Beta.Messages.Create(
      new()
      {
          Model = Messages::Model.ClaudeOpus5,
          MaxTokens = 1024,
          CacheControl = new(),
          System = system,
          Messages =
          [
              new() { Role = Role.User, Content = "Summarize section 1." },
              new()
              {
                  Role = Role.Assistant,
                  Content = r1.Content.Select(block => new BetaContentBlockParam(block.Json)).ToList(),
              },
              new() { Role = Role.User, Content = "Now summarize section 2." },
          ],
          Diagnostics = new() { PreviousMessageID = r1.ID },
          Betas = [AnthropicBeta.CacheDiagnosis2026_04_07],
      }
  );

  Console.WriteLine(r2.Diagnostics switch
  {
      null => "No divergence detected.",
      { CacheMissReason: null } => "Comparison still pending.",
      { CacheMissReason.Type: var type } => $"cache_miss_reason: {type.GetString()}",
  });

go Go
  client := anthropic.NewClient()
  ctx := context.Background()

  system := []anthropic.BetaTextBlockParam{
  	{Text: "You are an AI assistant analyzing a large document. <document>...</document>"},
  }

  r1, err := client.Beta.Messages.New(ctx, anthropic.BetaMessageNewParams{
  	Model:        anthropic.ModelClaudeOpus5,
  	MaxTokens:    1024,
  	CacheControl: anthropic.BetaCacheControlEphemeralParam{},
  	System:       system,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Summarize section 1.")),
  	},
  	Diagnostics: anthropic.BetaDiagnosticsParam{
  		PreviousMessageID: param.Null[string](),
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaCacheDiagnosis2026_04_07},
  })
  if err != nil {
  	panic(err)
  }

  r2, err := client.Beta.Messages.New(ctx, anthropic.BetaMessageNewParams{
  	Model:        anthropic.ModelClaudeOpus5,
  	MaxTokens:    1024,
  	CacheControl: anthropic.BetaCacheControlEphemeralParam{},
  	System:       system,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Summarize section 1.")),
  		r1.ToParam(),
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Now summarize section 2.")),
  	},
  	Diagnostics: anthropic.BetaDiagnosticsParam{
  		PreviousMessageID: anthropic.String(r1.ID),
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaCacheDiagnosis2026_04_07},
  })
  if err != nil {
  	panic(err)
  }

  switch {
  case !r2.JSON.Diagnostics.Valid():
  	fmt.Println("No divergence detected.")
  case !r2.Diagnostics.JSON.CacheMissReason.Valid():
  	fmt.Println("Comparison still pending.")
  default:
  	fmt.Printf("cache_miss_reason: %s\n", r2.Diagnostics.CacheMissReason.Type)
  }

java Java
  var client = AnthropicOkHttpClient.fromEnv();

  var system = "You are an AI assistant analyzing a large document. <document>...</document>";

  var r1 = client.beta().messages().create(
      MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .cacheControl(BetaCacheControlEphemeral.builder().build())
          .system(system)
          .addUserMessage("Summarize section 1.")
          // Pass null on the first turn to opt in without a prior message to compare.
          .diagnostics(BetaDiagnosticsParam.builder().previousMessageId((String) null).build())
          .addBeta(AnthropicBeta.CACHE_DIAGNOSIS_2026_04_07)
          .build()
  );

  var r2 = client.beta().messages().create(
      MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .cacheControl(BetaCacheControlEphemeral.builder().build())
          .system(system)
          .addUserMessage("Summarize section 1.")
          .addMessage(r1)
          .addUserMessage("Now summarize section 2.")
          .diagnostics(BetaDiagnosticsParam.builder().previousMessageId(r1.id()).build())
          .addBeta(AnthropicBeta.CACHE_DIAGNOSIS_2026_04_07)
          .build()
  );

  if (r2.diagnostics().isEmpty()) {
      IO.println("No divergence detected.");
  } else if (r2.diagnostics().get().cacheMissReason().isEmpty()) {
      IO.println("Comparison still pending.");
  } else {
      var reason = r2.diagnostics().get().cacheMissReason().get();
      // CacheMissReason doesn't expose a typed .type() accessor; read it from the raw JSON.
      @SuppressWarnings("unchecked")
      var json = (Map<String, JsonValue>) reason._json().orElseThrow().asObject().orElseThrow();
      IO.println("cache_miss_reason: " + json.get("type").asStringOrThrow());
  }

php PHP
  $client = new Client();

  $system = 'You are an AI assistant analyzing a large document. <document>...</document>';

  $r1 = $client->beta->messages->create(
      model: Model::CLAUDE_OPUS_5,
      maxTokens: 1024,
      cacheControl: new BetaCacheControlEphemeral,
      system: $system,
      messages: [
          ['role' => 'user', 'content' => 'Summarize section 1.'],
      ],
      diagnostics: (new BetaDiagnosticsParam)->withPreviousMessageID(null),
      betas: [AnthropicBeta::CACHE_DIAGNOSIS_2026_04_07],
  );

  $r2 = $client->beta->messages->create(
      model: Model::CLAUDE_OPUS_5,
      maxTokens: 1024,
      cacheControl: new BetaCacheControlEphemeral,
      system: $system,
      messages: [
          ['role' => 'user', 'content' => 'Summarize section 1.'],
          ['role' => 'assistant', 'content' => $r1->content],
          ['role' => 'user', 'content' => 'Now summarize section 2.'],
      ],
      diagnostics: (new BetaDiagnosticsParam)->withPreviousMessageID($r1->id),
      betas: [AnthropicBeta::CACHE_DIAGNOSIS_2026_04_07],
  );

  echo match (true) {
      $r2->diagnostics === null => "No divergence detected.\n",
      $r2->diagnostics->cacheMissReason === null => "Comparison still pending.\n",
      default => "cache_miss_reason: {$r2->diagnostics->cacheMissReason->type}\n",
  };

ruby Ruby
  client = Anthropic::Client.new

  SYSTEM = "You are an AI assistant analyzing a large document. <document>...</document>"

  r1 = client.beta.messages.create(
    model: :"claude-opus-5",
    max_tokens: 1024,
    cache_control: {type: "ephemeral"},
    system_: SYSTEM,
    messages: [
      {role: "user", content: "Summarize section 1."}
    ],
    diagnostics: {previous_message_id: nil},
    betas: ["cache-diagnosis-2026-04-07"]
  )

  r2 = client.beta.messages.create(
    model: :"claude-opus-5",
    max_tokens: 1024,
    cache_control: {type: "ephemeral"},
    system_: SYSTEM,
    messages: [
      {role: "user", content: "Summarize section 1."},
      {role: "assistant", content: r1.content},
      {role: "user", content: "Now summarize section 2."}
    ],
    diagnostics: {previous_message_id: r1.id},
    betas: ["cache-diagnosis-2026-04-07"]
  )

  case r2.diagnostics
  in nil
    puts "No divergence detected."
  in {cache_miss_reason: nil}
    puts "Comparison still pending."
  in {cache_miss_reason: {type:}}
    puts "cache_miss_reason: #{type}"
  end
  ```
</CodeGroup>


## Streaming

Source: https://platform.claude.com/llms-full.txt#streaming-7

In streaming responses, `diagnostics` appears on the `message_start` event.

<CodeGroup>
  ```bash cURL
  # Turn 2: stream the response. diagnostics arrives on the message_start event;
  # a null value means no divergence was found.
  curl -sS --fail-with-body https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: cache-diagnosis-2026-04-07" \
    -H "content-type: application/json" \
    -d @- <<EOF | jq -R 'select(startswith("data: ")) | ltrimstr("data: ") | fromjson | select(.type == "message_start") | .message.diagnostics'
  {
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "stream": true,
    "cache_control": {"type": "ephemeral"},
    "system": "You are an AI assistant analyzing a large document. <document>...</document>",
    "messages": [
      {"role": "user", "content": "Summarize section 1."},
      {"role": "assistant", "content": "Section 1 covers..."},
      {"role": "user", "content": "Now summarize section 2."}
    ],
    "diagnostics": {"previous_message_id": "$message_id"}
  }
  EOF

bash CLI
  # Turn 2: stream. With --stream the CLI emits each SSE event as one JSON object.
  # diagnostics arrives on the message_start event; pick it out with jq.
  ant beta:messages create \
    --beta cache-diagnosis-2026-04-07 \
    --stream --format jsonl <<YAML |
  model: claude-opus-5
  max_tokens: 1024
  cache_control:
    type: ephemeral
  system: "You are an AI assistant analyzing a large document. <document>...</document>"
  messages:
    - role: user
      content: Summarize section 1.
    - role: assistant
      content: Section 1 covers...
    - role: user
      content: Now summarize section 2.
  diagnostics:
    previous_message_id: $message_id
  YAML
    jq -c 'select(.type == "message_start") | .message | {id,usage,diagnostics}'

python Python
  # Turn 2: stream, referencing the previous response id
  with client.beta.messages.stream(
      model="claude-opus-5",
      max_tokens=1024,
      cache_control={"type": "ephemeral"},
      system=SYSTEM,
      messages=[
          {"role": "user", "content": "Summarize section 1."},
          {"role": "assistant", "content": r1.content},
          {"role": "user", "content": "Now summarize section 2."},
      ],
      diagnostics={"previous_message_id": r1.id},
      betas=["cache-diagnosis-2026-04-07"],
  ) as stream:
      for text in stream.text_stream:
          print(text, end="", flush=True)
      print()
      r2 = stream.get_final_message()

  diagnostics = r2.diagnostics
  if diagnostics is None:
      print("No divergence detected.")
  elif diagnostics.cache_miss_reason is None:
      print("Comparison still pending.")
  else:
      print(f"cache_miss_reason: {diagnostics.cache_miss_reason.type}")

typescript TypeScript
  const stream = client.beta.messages.stream({
    model: "claude-opus-5",
    max_tokens: 1024,
    cache_control: { type: "ephemeral" },
    system: SYSTEM,
    messages: [
      { role: "user", content: "Summarize section 1." },
      { role: "assistant", content: r1.content },
      { role: "user", content: "Now summarize section 2." }
    ],
    diagnostics: { previous_message_id: r1.id },
    betas: ["cache-diagnosis-2026-04-07"]
  });

  for await (const event of stream) {
    if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
      process.stdout.write(event.delta.text);
    }
  }
  process.stdout.write("\n");

  // diagnostics arrives on message_start and is carried through to the final message
  const r2 = await stream.finalMessage();

  if (r2.diagnostics === null) {
    console.log("No divergence detected.");
  } else if (r2.diagnostics.cache_miss_reason === null) {
    console.log("Comparison still pending.");
  } else {
    console.log(`cache_miss_reason: ${r2.diagnostics.cache_miss_reason.type}`);
  }

csharp C#
  // Turn 2: stream, referencing the previous response id
  BetaDiagnostics? diagnostics = null;

  var stream = client.Beta.Messages.CreateStreaming(
      new()
      {
          Model = Messages::Model.ClaudeOpus5,
          MaxTokens = 1024,
          CacheControl = new(),
          System = system,
          Messages =
          [
              new() { Role = Role.User, Content = "Summarize section 1." },
              new()
              {
                  Role = Role.Assistant,
                  Content = r1.Content.Select(block => new BetaContentBlockParam(block.Json)).ToList(),
              },
              new() { Role = Role.User, Content = "Now summarize section 2." },
          ],
          Diagnostics = new() { PreviousMessageID = r1.ID },
          Betas = [AnthropicBeta.CacheDiagnosis2026_04_07],
      }
  );

  await foreach (var streamEvent in stream)
  {
      if (streamEvent.TryPickStart(out var start))
      {
          // diagnostics arrives on the message_start event
          diagnostics = start.Message.Diagnostics;
      }
      else if (streamEvent.TryPickContentBlockDelta(out var delta) && delta.Delta.TryPickText(out var textDelta))
      {
          Console.Write(textDelta.Text);
      }
  }
  Console.WriteLine();

  Console.WriteLine(diagnostics switch
  {
      null => "No divergence detected.",
      { CacheMissReason: null } => "Comparison still pending.",
      { CacheMissReason.Type: var type } => $"cache_miss_reason: {type.GetString()}",
  });

go Go
  // Turn 2: stream, referencing the previous response id
  stream := client.Beta.Messages.NewStreaming(ctx, anthropic.BetaMessageNewParams{
  	Model:        anthropic.ModelClaudeOpus5,
  	MaxTokens:    1024,
  	CacheControl: anthropic.BetaCacheControlEphemeralParam{},
  	System:       system,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Summarize section 1.")),
  		r1.ToParam(),
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Now summarize section 2.")),
  	},
  	Diagnostics: anthropic.BetaDiagnosticsParam{
  		PreviousMessageID: anthropic.String(r1.ID),
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaCacheDiagnosis2026_04_07},
  })
  defer stream.Close()

  // diagnostics arrives on message_start; Accumulate carries it into r2
  var r2 anthropic.BetaMessage
  for stream.Next() {
  	if err := r2.Accumulate(stream.Current()); err != nil {
  		panic(err)
  	}
  }
  if err := stream.Err(); err != nil {
  	panic(err)
  }

  switch {
  case !r2.JSON.Diagnostics.Valid():
  	fmt.Println("No divergence detected.")
  case !r2.Diagnostics.JSON.CacheMissReason.Valid():
  	fmt.Println("Comparison still pending.")
  default:
  	fmt.Printf("cache_miss_reason: %s\n", r2.Diagnostics.CacheMissReason.Type)
  }

java Java
  // Turn 2: stream, referencing the previous response id
  var params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024)
      .cacheControl(BetaCacheControlEphemeral.builder().build())
      .system(system)
      .addUserMessage("Summarize section 1.")
      .addMessage(r1)
      .addUserMessage("Now summarize section 2.")
      .diagnostics(BetaDiagnosticsParam.builder().previousMessageId(r1.id()).build())
      .addBeta(AnthropicBeta.CACHE_DIAGNOSIS_2026_04_07)
      .build();

  var accumulator = BetaMessageAccumulator.create();
  try (var streamResponse = client.beta().messages().createStreaming(params)) {
      streamResponse.stream()
          .peek(accumulator::accumulate)
          .flatMap(event -> event.contentBlockDelta().stream())
          .flatMap(deltaEvent -> deltaEvent.delta().text().stream())
          .forEach(textDelta -> IO.print(textDelta.text()));
      IO.println("");
  }

  // diagnostics arrives on message_start and is carried through to the accumulated message
  var diagnostics = accumulator.message().diagnostics();
  if (diagnostics.isEmpty()) {
      IO.println("No divergence detected.");
  } else if (diagnostics.get().cacheMissReason().isEmpty()) {
      IO.println("Comparison still pending.");
  } else {
      var reason = diagnostics.get().cacheMissReason().get();
      // CacheMissReason doesn't expose a typed .type() accessor; read it from the raw JSON.
      @SuppressWarnings("unchecked")
      var json = (Map<String, JsonValue>) reason._json().orElseThrow().asObject().orElseThrow();
      IO.println("cache_miss_reason: " + json.get("type").asStringOrThrow());
  }

php PHP
  // Turn 2: stream, referencing the previous response id
  $stream = $client->beta->messages->createStream(
      model: Model::CLAUDE_OPUS_5,
      maxTokens: 1024,
      cacheControl: new BetaCacheControlEphemeral,
      system: $system,
      messages: [
          ['role' => 'user', 'content' => 'Summarize section 1.'],
          ['role' => 'assistant', 'content' => $r1->content],
          ['role' => 'user', 'content' => 'Now summarize section 2.'],
      ],
      diagnostics: (new BetaDiagnosticsParam)->withPreviousMessageID($r1->id),
      betas: [AnthropicBeta::CACHE_DIAGNOSIS_2026_04_07],
  );

  $diagnostics = null;
  foreach ($stream as $event) {
      if ($event instanceof BetaRawMessageStartEvent) {
          // diagnostics arrives on the message_start event's embedded BetaMessage
          $diagnostics = $event->message->diagnostics;
      } elseif ($event instanceof BetaRawContentBlockDeltaEvent && $event->delta instanceof BetaTextDelta) {
          echo $event->delta->text;
      }
  }
  echo PHP_EOL;

  echo match (true) {
      $diagnostics === null => "No divergence detected.\n",
      $diagnostics->cacheMissReason === null => "Comparison still pending.\n",
      default => "cache_miss_reason: {$diagnostics->cacheMissReason->type}\n",
  };

ruby Ruby
  # Turn 2: stream, referencing the previous response id
  stream = client.beta.messages.stream(
    model: :"claude-opus-5",
    max_tokens: 1024,
    cache_control: {type: "ephemeral"},
    system_: SYSTEM,
    messages: [
      {role: "user", content: "Summarize section 1."},
      {role: "assistant", content: r1.content},
      {role: "user", content: "Now summarize section 2."}
    ],
    diagnostics: {previous_message_id: r1.id},
    betas: ["cache-diagnosis-2026-04-07"]
  )

  stream.each do |event|
    print(event.text) if event.is_a?(Anthropic::Streaming::TextEvent)
  end
  puts

  # diagnostics arrives on message_start and is retained on the accumulated message
  r2 = stream.accumulated_message

  case r2.diagnostics
  in nil
    puts "No divergence detected."
  in {cache_miss_reason: nil}
    puts "Comparison still pending."
  in {cache_miss_reason: {type:}}
    puts "cache_miss_reason: #{type}"
  end
  ```
</CodeGroup>

The `message_start` event carries the full `diagnostics` field; see [Response format](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics#response-format) for the possible values.


## Threading diagnostics through a conversation loop

Source: https://platform.claude.com/llms-full.txt#threading-diagnostics-through-a-conversation-loop

In a multi-turn conversation, carry the latest response `id` forward as `previous_message_id` on every turn. The first iteration passes `null` to opt in; each subsequent iteration passes the `id` from the previous response.

<Tabs>
  <Tab title="cURL">
    <Info>
      This workflow doesn't translate well to a one-off shell command. See the SDK tabs for the loop pattern; the per-turn HTTP request is identical to [Basic usage](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics#basic-usage).
    </Info>
  </Tab>

  <Tab title="CLI">
    <Info>
      This workflow doesn't translate well to a one-off shell command. See the SDK tabs for the loop pattern; the per-turn CLI invocation is identical to [Basic usage](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics#basic-usage).
    </Info>
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


## Response format

Source: https://platform.claude.com/llms-full.txt#response-format-4

The `diagnostics` field on the response `Message` has four possible states:

| Value                          | Meaning                                                                                                                                                                                         |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| field absent                   | The request did not include `diagnostics`, or the beta header was missing.                                                                                                                      |
| `null`                         | Either `previous_message_id` was `null` (first turn, nothing to compare), or a comparison ran and found no divergence.                                                                          |
| `{"cache_miss_reason": null}`  | The comparison was still running when the response was serialized. This can happen when the response starts very quickly. Treat it as inconclusive and check the next turn.                     |
| `{"cache_miss_reason": {...}}` | A `cache_miss_reason` is attached. For `*_changed` types this identifies the first divergence point; `previous_message_not_found` and `unavailable` are cases where no comparison was produced. |

When `cache_miss_reason` is non-null, it looks like this:


## Cache miss reason types

Source: https://platform.claude.com/llms-full.txt#cache-miss-reason-types

`cache_miss_reason` is a discriminated union on `type`. The response reports the earliest divergence only, so fix it first; later ones may be hidden behind it.

| Type                         | What it means                                                                                                                                                                                                                                                                                                                                                                                                                                   | What to change                                                                                                                                                                                                                                                                                                |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model_changed`              | The `model` differs from the previous request (for example, a router, A/B test, or fallback selected a different model). The cache is per-model.                                                                                                                                                                                                                                                                                                | Hold the model constant within a cached conversation.                                                                                                                                                                                                                                                         |
| `system_changed`             | The `system` parameter differs. Typically a timestamp, request ID, or other per-request value was interpolated into the system prompt.                                                                                                                                                                                                                                                                                                          | Make the system prompt a byte-stable constant and move dynamic data into the first `user` message after your cache breakpoint.                                                                                                                                                                                |
| `tools_changed`              | The `tools` array differs: tools were added, removed, or reordered between turns, or tool `input_schema` JSON was serialized non-deterministically.                                                                                                                                                                                                                                                                                             | Send the same tool list on every turn in a fixed order with deterministically serialized schemas (for example, sort keys).                                                                                                                                                                                    |
| `messages_changed`           | The model, system, and tools all match, but an earlier entry in `messages` was altered, reordered, or removed rather than appended to. Typically conversation history was truncated or edited, or assistant turns and `tool_result` blocks were re-serialized differently on resend.                                                                                                                                                            | Treat the history as append-only; echo assistant `content` and tool results back verbatim.                                                                                                                                                                                                                    |
| `previous_message_not_found` | No stored fingerprint exists for the supplied `previous_message_id`. This is not evidence that your request changed. Typically the previous request did not carry the beta header, it came from a different workspace, or too much time has passed since it was sent.                                                                                                                                                                           | Send the beta header on every turn and keep consecutive turns close together in time.                                                                                                                                                                                                                         |
| `unavailable`                | Diagnostic information was not available for this request. This includes the case where `model`, `system`, and `tools` match but another prompt-affecting request parameter (`tool_choice`, `thinking`, `context_management`, `output_config`, `output_format`, or the set of active `anthropic-beta` headers) differs, and very long conversations where the divergence is beyond the comparison horizon. Your request was processed normally. | Keep the prompt-affecting request parameters constant for the lifetime of a cached conversation. If persistent, apply the manual checks under [Troubleshooting common issues](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#troubleshooting-common-issues) on the prompt caching page. |

<Note>
  The four `*_changed` types also carry a `cache_missed_input_tokens` integer: an estimate of how many input tokens fell after the divergence point, giving you a sense of how much cacheable prefix was lost. It is derived from byte lengths before tokenization, so treat it as a magnitude indicator rather than a billing number. It can differ from (and occasionally exceed) `usage.input_tokens`.
</Note>


## Reading diagnostics alongside usage

Source: https://platform.claude.com/llms-full.txt#reading-diagnostics-alongside-usage

`diagnostics` answers "did my request change?" while `usage.cache_read_input_tokens` answers "did the cache hit?". Combining them tells you where to look.

This matrix applies to turns where you passed a real `previous_message_id`. On the first turn (`previous_message_id: null`), `diagnostics` is always `null` and `cache_read_input_tokens` is normally zero because the cache is being written, not read; no troubleshooting is needed. The matrix also does not apply when `cache_miss_reason` is `null` (the comparison is still pending; check the next turn) or when its `type` is `previous_message_not_found` or `unavailable` (no comparison was produced).

| Diagnostics result                        | Cache read tokens | Interpretation                                                                                                                                                                                                                       |
| ----------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `null`                                    | high              | Working as expected. Your prefix is stable and the cache hit.                                                                                                                                                                        |
| `null`                                    | low or zero       | Your requests match but the cache entry was no longer available. Consider shortening gaps between turns or using the [1-hour cache TTL](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#1-hour-cache-duration). |
| `cache_miss_reason` is a `*_changed` type | low or zero       | Your bug. The request changed; fix the cause indicated by `type`.                                                                                                                                                                    |
| `cache_miss_reason` is a `*_changed` type | high              | Rare. A change occurred late in the prompt but an earlier `cache_control` breakpoint still hit. Worth fixing, but low impact.                                                                                                        |


## Limitations

Source: https://platform.claude.com/llms-full.txt#limitations-5

* **Beta:** Field names and semantics may change while this feature is in beta.
* **Claude API only:** Not available on Amazon Bedrock or Google Cloud.
* **Limited retention:** Fingerprints for `previous_message_id` lookup expire after a short period. Run diagnostic comparisons between closely spaced requests.
* **Same workspace:** The previous request must have run in the same organization and workspace. To check, compare the `anthropic-workspace-id` [response header](https://platform.claude.com/docs/en/api/overview#response-headers) on the two responses.
* **Comparison horizon:** For very long conversations where the only change is deep in the message list, the response may be `unavailable` rather than a precise location.
* **Best-effort:** Diagnostics never blocks or fails your request. If diagnostic information is not available, the response returns `unavailable`, or `cache_miss_reason: null` when the comparison was still running.


## Data retention

Source: https://platform.claude.com/llms-full.txt#data-retention-7

Cache diagnostics is ZDR eligible (qualified). Anthropic does not store the raw text of your prompts or Claude's outputs for this feature.

The fingerprint stored for each request consists only of cryptographic hashes and token-count estimates, keyed by the response `id` and scoped to your organization and workspace. Fingerprints expire after a short period and are not used for any other purpose.

For ZDR eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).


## See also

Source: https://platform.claude.com/llms-full.txt#see-also

* [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
* [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
* [Beta headers](https://platform.claude.com/docs/en/api/beta-headers)


---
title: Compaction
url: https://platform.claude.com/docs/en/build-with-claude/compaction
description: Server-side context compaction for managing long conversations that approach context window limits.
---


## Compatibility

Source: https://platform.claude.com/llms-full.txt#compatibility-10

- Status: Beta
- [Beta header](https://platform.claude.com/docs/en/api/beta-headers): `compact-2026-01-12`
- [ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): eligible (excludes [Covered Models](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements))
- Supported models: `claude-fable-5-1`, `claude-mythos-5-1`, `claude-fable-5`, `claude-mythos-5`, `claude-mythos-preview`, `claude-opus-5`, `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`, `claude-sonnet-5`, `claude-sonnet-4-6`
- Platforms: Claude API (beta), Claude Platform on AWS (beta), Amazon Bedrock (beta), Google Cloud (beta), Microsoft Foundry (beta)

<Tip>
  Server-side compaction is the recommended strategy for managing context in long-running conversations and agentic workflows. It handles context management automatically, without client-side summarization code.
</Tip>

Compaction extends the effective context length for long-running conversations and tasks by automatically summarizing older context when approaching the context window limit. It also keeps the active context small: as a conversation grows, response quality degrades, so compaction replaces older content with a concise summary.

<Tip>
  For a deeper look at why long contexts degrade and how compaction helps, see [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
</Tip>

This is ideal for:

* Chat-based, multi-turn conversations where you want users to use one chat for a long period of time
* Task-oriented prompts that require a lot of follow-up work (often tool use) that might exceed the context window


## How compaction works

Source: https://platform.claude.com/llms-full.txt#how-compaction-works

When compaction is enabled, Claude automatically summarizes your conversation when it reaches the configured token threshold. The API:

1. Detects when input tokens reach your specified trigger threshold.
2. Generates a summary of the current conversation.
3. Creates a `compaction` block containing the summary.
4. Continues the response with the compacted context.

On subsequent requests, append the response to your messages. The API automatically drops all content blocks prior to the `compaction` block, continuing the conversation from the summary.

![Compaction flow: when input tokens reach the trigger, Claude writes a summary into a compaction block and continues](https://platform.claude.com/docs/images/compaction-flow.svg)


## Basic usage

Source: https://platform.claude.com/llms-full.txt#basic-usage-5

Enable compaction by adding the `compact_20260112` strategy to `context_management.edits` in your Messages API request.

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: compact-2026-01-12" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [
        {
          "role": "user",
          "content": "Help me build a website"
        }
      ],
      "context_management": {
        "edits": [
          {
            "type": "compact_20260112"
          }
        ]
      }
    }'

bash CLI
  ant beta:messages create --beta compact-2026-01-12 <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Help me build a website
  context_management:
    edits:
      - type: compact_20260112
  YAML

python Python
  client = anthropic.Anthropic()

  messages = [{"role": "user", "content": "Help me build a website"}]

  response = client.beta.messages.create(
      betas=["compact-2026-01-12"],
      model="claude-opus-5",
      max_tokens=4096,
      messages=messages,
      context_management={"edits": [{"type": "compact_20260112"}]},
  )

  # Append the response (including any compaction block) to continue the conversation
  messages.append({"role": "assistant", "content": response.content})

typescript TypeScript
  const client = new Anthropic();

  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [
    { role: "user", content: "Help me build a website" }
  ];

  const response = await client.beta.messages.create({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages,
    context_management: {
      edits: [
        {
          type: "compact_20260112"
        }
      ]
    }
  });

  // Append the response (including any compaction block) to continue the conversation
  messages.push({
    role: "assistant",
    content: response.content
  });

csharp C#
  AnthropicClient client = new();

  var messages = new List<BetaMessageParam>
  {
      new() { Role = Role.User, Content = "Help me build a website" }
  };

  var parameters = new MessageCreateParams
  {
      Betas = ["compact-2026-01-12"],
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Messages = messages,
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaCompact20260112Edit()]
      }
  };

  var response = await client.Beta.Messages.Create(parameters);

  // Append the response (including any compaction block) to continue the conversation
  messages.Add(new BetaMessageParam
  {
      Role = Role.Assistant,
      Content = response.Content.Select(block => new BetaContentBlockParam(block.Json)).ToList()
  });

  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  messages := []anthropic.BetaMessageParam{
  	anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Help me build a website")),
  }

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages:  messages,
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{}},
  		},
  	},
  	Betas: []anthropic.AnthropicBeta{"compact-2026-01-12"},
  })
  if err != nil {
  	log.Fatal(err)
  }

  // Append the response (including any compaction block) to continue the conversation
  messages = append(messages, response.ToParam())

  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaCompact20260112Edit;
  // ...
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          MessageCreateParams params = MessageCreateParams.builder()
              .addBeta("compact-2026-01-12")
              .model("claude-opus-5")
              .maxTokens(4096L)
              .addUserMessage("Help me build a website")
              .contextManagement(BetaContextManagementConfig.builder()
                  .addEdit(BetaCompact20260112Edit.builder().build())
                  .build())
              .build();

          BetaMessage response = client.beta().messages().create(params);

          // Append the response (including any compaction block) to continue the conversation
          // by including it in the next request's messages
          System.out.println(response);

php PHP
  $client = new Client();

  $messages = [
      ['role' => 'user', 'content' => 'Help me build a website']
  ];

  $response = $client->beta->messages->create(
      maxTokens: 4096,
      messages: $messages,
      model: 'claude-opus-5',
      betas: ['compact-2026-01-12'],
      contextManagement: [
          'edits' => [
              ['type' => 'compact_20260112']
          ]
      ]
  );

  // Append the response (including any compaction block) to continue the conversation
  $messages[] = ['role' => 'assistant', 'content' => $response->content];

  echo json_encode($response, JSON_PRETTY_PRINT), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  messages = [
    { role: "user", content: "Help me build a website" }
  ]

  response = client.beta.messages.create(
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: messages,
    context_management: {
      edits: [{ type: "compact_20260112" }]
    }
  )

  # Append the response (including any compaction block) to continue the conversation
  messages << { role: "assistant", content: response.content }

  puts response
  ```
</CodeGroup>


## Parameters

Source: https://platform.claude.com/llms-full.txt#parameters-2

| Parameter                | Type    | Default                                     | Description                                                                                                            |
| ------------------------ | ------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `type`                   | string  | Required                                    | Must be `"compact_20260112"`                                                                                           |
| `trigger`                | object  | `{"type": "input_tokens", "value": 150000}` | When to trigger compaction. `input_tokens` is the only supported trigger type. `value` must be at least 50,000 tokens. |
| `pause_after_compaction` | boolean | `false`                                     | Whether to pause after generating the compaction summary                                                               |
| `instructions`           | string  | `null`                                      | Custom summarization prompt. Completely replaces the default prompt when provided.                                     |

### Trigger configuration

Configure when compaction triggers using the `trigger` parameter:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: compact-2026-01-12" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [
        {
          "role": "user",
          "content": "Hello, Claude"
        }
      ],
      "context_management": {
        "edits": [
          {
            "type": "compact_20260112",
            "trigger": {
              "type": "input_tokens",
              "value": 150000
            }
          }
        ]
      }
    }'

bash CLI
  ant beta:messages create --beta compact-2026-01-12 <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Hello, Claude
  context_management:
    edits:
      - type: compact_20260112
        trigger:
          type: input_tokens
          value: 150000
  YAML

python Python
  client = anthropic.Anthropic()
  messages = [{"role": "user", "content": "Hello, Claude"}]
  response = client.beta.messages.create(
      betas=["compact-2026-01-12"],
      model="claude-opus-5",
      max_tokens=4096,
      messages=messages,
      context_management={
          "edits": [
              {
                  "type": "compact_20260112",
                  "trigger": {"type": "input_tokens", "value": 150000},
              }
          ]
      },
  )

typescript TypeScript
  const client = new Anthropic();
  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [
    { role: "user", content: "Hello, Claude" }
  ];

  const response = await client.beta.messages.create({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages,
    context_management: {
      edits: [
        {
          type: "compact_20260112",
          trigger: {
            type: "input_tokens",
            value: 150000
          }
        }
      ]
    }
  });

csharp C#
  AnthropicClient client = new();
  List<BetaMessageParam> messages = [new() { Role = Role.User, Content = "Hello" }];

  var parameters = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Betas = ["compact-2026-01-12"],
      Messages = messages,
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaCompact20260112Edit
          {
              Trigger = new BetaInputTokensTrigger(150000)
          }]
      }
  };

  var message = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()
  messages := []anthropic.BetaMessageParam{anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude"))}

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages:  messages,
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{
  				Trigger: anthropic.BetaInputTokensTriggerParam{Value: 150000},
  			}},
  		},
  	},
  	Betas: []anthropic.AnthropicBeta{"compact-2026-01-12"},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaCompact20260112Edit;
  import com.anthropic.models.beta.messages.BetaInputTokensTrigger;
  // ...
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          MessageCreateParams params = MessageCreateParams.builder()
              .model("claude-opus-5")
              .maxTokens(4096L)
              .addBeta("compact-2026-01-12")
              .addUserMessage("Hello, Claude")
              .contextManagement(BetaContextManagementConfig.builder()
                  .addEdit(BetaCompact20260112Edit.builder()
                      .trigger(BetaInputTokensTrigger.builder()
                          .value(150000L)
                          .build())
                      .build())
                  .build())
              .build();

          BetaMessage response = client.beta().messages().create(params);
          System.out.println(response);

php PHP
  $client = new Client();
  $messages = [['role' => 'user', 'content' => 'Hello, Claude']];

  $message = $client->beta->messages->create(
      maxTokens: 4096,
      messages: $messages,
      model: 'claude-opus-5',
      betas: ['compact-2026-01-12'],
      contextManagement: [
          'edits' => [
              [
                  'type' => 'compact_20260112',
                  'trigger' => [
                      'type' => 'input_tokens',
                      'value' => 150000
                  ]
              ]
          ]
      ]
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new
  messages = [{ role: "user", content: "Hello, Claude" }]

  response = client.beta.messages.create(
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: messages,
    context_management: {
      edits: [
        {
          type: "compact_20260112",
          trigger: {
            type: "input_tokens",
            value: 150000
          }
        }
      ]
    }
  )
  puts response

text wrap
You have written a partial transcript for the initial task above. Please write a summary of the transcript. The purpose of this summary is to provide continuity so you can continue to make progress towards solving the task in a future context, where the raw history above may not be accessible and will be replaced with this summary. Write down anything that would be helpful, including the state, next steps, learnings etc. You must wrap your summary in a <summary></summary> block.

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: compact-2026-01-12" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [
        {
          "role": "user",
          "content": "Hello, Claude"
        }
      ],
      "context_management": {
        "edits": [
          {
            "type": "compact_20260112",
            "instructions": "Focus on preserving code snippets, variable names, and technical decisions."
          }
        ]
      }
    }'

bash CLI
  ant beta:messages create --beta compact-2026-01-12 <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Hello, Claude
  context_management:
    edits:
      - type: compact_20260112
        instructions: >-
          Focus on preserving code snippets, variable names, and
          technical decisions.
  YAML

python Python
  client = anthropic.Anthropic()
  messages = [{"role": "user", "content": "Hello, Claude"}]
  response = client.beta.messages.create(
      betas=["compact-2026-01-12"],
      model="claude-opus-5",
      max_tokens=4096,
      messages=messages,
      context_management={
          "edits": [
              {
                  "type": "compact_20260112",
                  "instructions": "Focus on preserving code snippets, variable names, and technical decisions.",
              }
          ]
      },
  )

typescript TypeScript
  const client = new Anthropic();
  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [
    { role: "user", content: "Hello, Claude" }
  ];

  const response = await client.beta.messages.create({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages,
    context_management: {
      edits: [
        {
          type: "compact_20260112",
          instructions:
            "Focus on preserving code snippets, variable names, and technical decisions."
        }
      ]
    }
  });

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Betas = ["compact-2026-01-12"],
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Messages =
      [
          new BetaMessageParam { Role = Role.User, Content = "Help me build a Python web scraper" },
          new BetaMessageParam { Role = Role.Assistant, Content = "I'll help you build a web scraper..." },
          new BetaMessageParam { Role = Role.User, Content = "Add support for JavaScript-rendered pages" }
      ],
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaCompact20260112Edit
          {
              Instructions = "Focus on preserving code snippets, variable names, and technical decisions."
          }]
      }
  };

  var message = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Help me build a Python web scraper")),
  		{Role: anthropic.BetaMessageParamRoleAssistant, Content: []anthropic.BetaContentBlockParamUnion{anthropic.NewBetaTextBlock("I'll help you build a web scraper...")}},
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Add support for JavaScript-rendered pages")),
  	},
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{
  				Instructions: anthropic.String("Focus on preserving code snippets, variable names, and technical decisions."),
  			}},
  		},
  	},
  	Betas: []anthropic.AnthropicBeta{"compact-2026-01-12"},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaCompact20260112Edit;
  // ...
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          MessageCreateParams params = MessageCreateParams.builder()
              .addBeta("compact-2026-01-12")
              .model("claude-opus-5")
              .maxTokens(4096L)
              .addUserMessage("Help me build a Python web scraper")
              .addAssistantMessage("I'll help you build a web scraper...")
              .addUserMessage("Add support for JavaScript-rendered pages")
              .contextManagement(BetaContextManagementConfig.builder()
                  .addEdit(BetaCompact20260112Edit.builder()
                      .instructions("Focus on preserving code snippets, variable names, and technical decisions.")
                      .build())
                  .build())
              .build();

          BetaMessage response = client.beta().messages().create(params);
          System.out.println(response);

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Help me build a Python web scraper'],
          ['role' => 'assistant', 'content' => "I'll help you build a web scraper..."],
          ['role' => 'user', 'content' => 'Add support for JavaScript-rendered pages']
      ],
      model: 'claude-opus-5',
      betas: ['compact-2026-01-12'],
      contextManagement: [
          'edits' => [
              [
                  'type' => 'compact_20260112',
                  'instructions' => 'Focus on preserving code snippets, variable names, and technical decisions.'
              ]
          ]
      ]
  );

  echo json_encode($response, JSON_PRETTY_PRINT), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      { role: "user", content: "Help me build a Python web scraper" },
      { role: "assistant", content: "I'll help you build a web scraper..." },
      { role: "user", content: "Add support for JavaScript-rendered pages" }
    ],
    context_management: {
      edits: [
        {
          type: "compact_20260112",
          instructions:
            "Focus on preserving code snippets, variable names, and technical decisions."
        }
      ]
    }
  )

  puts response

bash cURL
  # pause_after_compaction stops the response right after the compaction
  # summary so you can adjust the messages before continuing. The continue
  # step doesn't translate well to a one-off shell command; see the SDK tabs
  # for the full pause-and-continue flow. Single paused request:
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: compact-2026-01-12" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [
        {
          "role": "user",
          "content": "Hello, Claude"
        }
      ],
      "context_management": {
        "edits": [
          {
            "type": "compact_20260112",
            "pause_after_compaction": true
          }
        ]
      }
    }'

bash CLI
  # pause_after_compaction stops the response right after the compaction
  # summary so you can adjust the messages before continuing. The continue
  # step doesn't translate well to a one-off CLI command; see the SDK tabs
  # for the full pause-and-continue flow. Single paused request:
  ant beta:messages create --beta compact-2026-01-12 --format jsonl <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Hello, Claude
  context_management:
    edits:
      - type: compact_20260112
        pause_after_compaction: true
  YAML

python Python
  client = anthropic.Anthropic()
  messages = [{"role": "user", "content": "Hello, Claude"}]
  response = client.beta.messages.create(
      betas=["compact-2026-01-12"],
      model="claude-opus-5",
      max_tokens=4096,
      messages=messages,
      context_management={
          "edits": [{"type": "compact_20260112", "pause_after_compaction": True}]
      },
  )

  # Check if compaction triggered a pause
  if response.stop_reason == "compaction":
      # Response contains only the compaction block
      messages.append({"role": "assistant", "content": response.content})

      # Continue the request
      response = client.beta.messages.create(
          betas=["compact-2026-01-12"],
          model="claude-opus-5",
          max_tokens=4096,
          messages=messages,
          context_management={"edits": [{"type": "compact_20260112"}]},
      )

typescript TypeScript
  const client = new Anthropic();
  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [
    { role: "user", content: "Hello, Claude" }
  ];

  let response = await client.beta.messages.create({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages,
    context_management: {
      edits: [
        {
          type: "compact_20260112",
          pause_after_compaction: true
        }
      ]
    }
  });

  // Check if compaction triggered a pause
  if (response.stop_reason === "compaction") {
    // Response contains only the compaction block
    messages.push({
      role: "assistant",
      content: response.content
    });

    // Continue the request
    response = await client.beta.messages.create({
      betas: ["compact-2026-01-12"],
      model: "claude-opus-5",
      max_tokens: 4096,
      messages,
      context_management: {
        edits: [{ type: "compact_20260112" }]
      }
    });
  }

csharp C#
  var client = new AnthropicClient();
  var messages = new List<BetaMessageParam>
  {
      new() { Role = Role.User, Content = "Hello, Claude" }
  };

  var parameters = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Betas = ["compact-2026-01-12"],
      Messages = messages,
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaCompact20260112Edit
          {
              PauseAfterCompaction = true
          }]
      }
  };

  var response = await client.Beta.Messages.Create(parameters);

  if (response.StopReason == BetaStopReason.Compaction)
  {
      messages.Add(new BetaMessageParam
      {
          Role = Role.Assistant,
          Content = response.Content.Select(block => new BetaContentBlockParam(block.Json)).ToList()
      });

      parameters = new()
      {
          Model = "claude-opus-5",
          MaxTokens = 4096,
          Betas = ["compact-2026-01-12"],
          Messages = messages,
          ContextManagement = new BetaContextManagementConfig
          {
              Edits = [new BetaCompact20260112Edit()]
          }
      };

      response = await client.Beta.Messages.Create(parameters);
  }

  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()
  messages := []anthropic.BetaMessageParam{anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude"))}

  compactEdit := anthropic.BetaContextManagementConfigParam{
  	Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  		{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{
  			PauseAfterCompaction: anthropic.Bool(true),
  		}},
  	},
  }

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:             anthropic.ModelClaudeOpus5,
  	MaxTokens:         4096,
  	Messages:          messages,
  	ContextManagement: compactEdit,
  	Betas:             []anthropic.AnthropicBeta{"compact-2026-01-12"},
  })
  if err != nil {
  	log.Fatal(err)
  }

  if response.StopReason == "compaction" {
  	messages = append(messages, response.ToParam())

  	response, err = client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 4096,
  		Messages:  messages,
  		ContextManagement: anthropic.BetaContextManagementConfigParam{
  			Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  				{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{}},
  			},
  		},
  		Betas: []anthropic.AnthropicBeta{"compact-2026-01-12"},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}
  }

  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaCompact20260112Edit;
  import com.anthropic.models.beta.messages.BetaStopReason;
  // ...
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          MessageCreateParams params = MessageCreateParams.builder()
              .model("claude-opus-5")
              .maxTokens(4096L)
              .addBeta("compact-2026-01-12")
              .addUserMessage("Help me build a website")
              .contextManagement(BetaContextManagementConfig.builder()
                  .addEdit(BetaCompact20260112Edit.builder()
                      .pauseAfterCompaction(true)
                      .build())
                  .build())
              .build();

          BetaMessage response = client.beta().messages().create(params);

          // Check if compaction triggered a pause
          if (response.stopReason().isPresent()
                  && response.stopReason().get().equals(BetaStopReason.COMPACTION)) {
              // Append the compaction block and continue the request
              // by building a new request with the compacted context
              MessageCreateParams continueParams = MessageCreateParams.builder()
                  .model("claude-opus-5")
                  .maxTokens(4096L)
                  .addBeta("compact-2026-01-12")
                  .addUserMessage("Help me build a website")
                  .addMessage(response)
                  .contextManagement(BetaContextManagementConfig.builder()
                      .addEdit(BetaCompact20260112Edit.builder().build())
                      .build())
                  .build();

              response = client.beta().messages().create(continueParams);
          }

          System.out.println(response);

php PHP
  $client = new Client();
  $messages = [['role' => 'user', 'content' => 'Hello, Claude']];

  $response = $client->beta->messages->create(
      maxTokens: 4096,
      messages: $messages,
      model: 'claude-opus-5',
      betas: ['compact-2026-01-12'],
      contextManagement: [
          'edits' => [
              [
                  'type' => 'compact_20260112',
                  'pause_after_compaction' => true
              ]
          ]
      ]
  );

  if ($response->stopReason === 'compaction') {
      $messages[] = [
          'role' => 'assistant',
          'content' => $response->content
      ];

      $response = $client->beta->messages->create(
          maxTokens: 4096,
          messages: $messages,
          model: 'claude-opus-5',
          betas: ['compact-2026-01-12'],
          contextManagement: [
              'edits' => [
                  ['type' => 'compact_20260112']
              ]
          ]
      );
  }

  echo $response;

ruby Ruby
  client = Anthropic::Client.new
  messages = [{ role: "user", content: "Hello, Claude" }]

  response = client.beta.messages.create(
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: messages,
    context_management: {
      edits: [
        {
          type: "compact_20260112",
          pause_after_compaction: true
        }
      ]
    }
  )

  if response.stop_reason == :compaction
    messages << { role: "assistant", content: response.content }

    response = client.beta.messages.create(
      betas: ["compact-2026-01-12"],
      model: "claude-opus-5",
      max_tokens: 4096,
      messages: messages,
      context_management: {
        edits: [{ type: "compact_20260112" }]
      }
    )
  end

  puts response

python Python
  client = anthropic.Anthropic()
  messages = [{"role": "user", "content": "Hello, Claude"}]
  TRIGGER_THRESHOLD = 100_000
  TOTAL_TOKEN_BUDGET = 3_000_000
  n_compactions = 0

  response = client.beta.messages.create(
      betas=["compact-2026-01-12"],
      model="claude-opus-5",
      max_tokens=4096,
      messages=messages,
      context_management={
          "edits": [
              {
                  "type": "compact_20260112",
                  "trigger": {"type": "input_tokens", "value": TRIGGER_THRESHOLD},
                  "pause_after_compaction": True,
              }
          ]
      },
  )

  if response.stop_reason == "compaction":
      n_compactions += 1
      messages.append({"role": "assistant", "content": response.content})

      # Estimate total tokens consumed; prompt wrap-up if over budget
      if n_compactions * TRIGGER_THRESHOLD >= TOTAL_TOKEN_BUDGET:
          messages.append(
              {
                  "role": "user",
                  "content": "Please wrap up your current work and summarize the final state.",
              }
          )

typescript TypeScript
  const client = new Anthropic();
  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [
    { role: "user", content: "Hello, Claude" }
  ];
  const TRIGGER_THRESHOLD = 100_000;
  const TOTAL_TOKEN_BUDGET = 3_000_000;
  let compactionCount = 0;

  const response = await client.beta.messages.create({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages,
    context_management: {
      edits: [
        {
          type: "compact_20260112",
          trigger: { type: "input_tokens", value: TRIGGER_THRESHOLD },
          pause_after_compaction: true
        }
      ]
    }
  });

  if (response.stop_reason === "compaction") {
    compactionCount += 1;
    messages.push({ role: "assistant", content: response.content });

    // Estimate total tokens consumed; prompt wrap-up if over budget
    if (compactionCount * TRIGGER_THRESHOLD >= TOTAL_TOKEN_BUDGET) {
      messages.push({
        role: "user",
        content: "Please wrap up your current work and summarize the final state."
      });
    }
  }

csharp C#
  AnthropicClient client = new();
  List<BetaMessageParam> messages = [new() { Role = Role.User, Content = "Hello, Claude" }];

  const int TriggerThreshold = 100_000;
  const int TotalTokenBudget = 3_000_000;
  int compactionCount = 0;

  var response = await client.Beta.Messages.Create(new()
  {
      Betas = ["compact-2026-01-12"],
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Messages = messages,
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaCompact20260112Edit
          {
              Trigger = new BetaInputTokensTrigger(TriggerThreshold),
              PauseAfterCompaction = true
          }]
      }
  });

  if (response.StopReason == BetaStopReason.Compaction)
  {
      compactionCount += 1;
      messages.Add(new()
      {
          Role = Role.Assistant,
          Content = response.Content.Select(b => new BetaContentBlockParam(b.Json)).ToList()
      });

      // Estimate total tokens consumed; prompt wrap-up if over budget
      if (compactionCount * TriggerThreshold >= TotalTokenBudget)
      {
          messages.Add(new()
          {
              Role = Role.User,
              Content = "Please wrap up your current work and summarize the final state."
          });
      }
  }

  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()
  messages := []anthropic.BetaMessageParam{anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude"))}

  const triggerThreshold = 100_000
  const totalTokenBudget = 3_000_000
  compactionCount := 0

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages:  messages,
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{
  				Trigger:              anthropic.BetaInputTokensTriggerParam{Value: triggerThreshold},
  				PauseAfterCompaction: anthropic.Bool(true),
  			}},
  		},
  	},
  	Betas: []anthropic.AnthropicBeta{"compact-2026-01-12"},
  })
  if err != nil {
  	log.Fatal(err)
  }

  if response.StopReason == "compaction" {
  	compactionCount++
  	messages = append(messages, response.ToParam())

  	// Estimate total tokens consumed; prompt wrap-up if over budget
  	if compactionCount*triggerThreshold >= totalTokenBudget {
  		messages = append(messages, anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Please wrap up your current work and summarize the final state.")))
  	}
  }

  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaCompact20260112Edit;
  import com.anthropic.models.beta.messages.BetaInputTokensTrigger;
  import com.anthropic.models.beta.messages.BetaStopReason;
  // ...
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          long triggerThreshold = 100_000;
          long totalTokenBudget = 3_000_000;
          int compactionCount = 0;

          List<BetaMessageParam> messages = new ArrayList<>();
          messages.add(BetaMessageParam.builder()
              .role(BetaMessageParam.Role.USER)
              .content("Hello, Claude")
              .build());

          MessageCreateParams params = MessageCreateParams.builder()
              .addBeta("compact-2026-01-12")
              .model("claude-opus-5")
              .maxTokens(4096L)
              .messages(messages)
              .contextManagement(BetaContextManagementConfig.builder()
                  .addEdit(BetaCompact20260112Edit.builder()
                      .trigger(BetaInputTokensTrigger.builder()
                          .value(triggerThreshold)
                          .build())
                      .pauseAfterCompaction(true)
                      .build())
                  .build())
              .build();

          BetaMessage response = client.beta().messages().create(params);

          if (response.stopReason().isPresent()
                  && response.stopReason().get().equals(BetaStopReason.COMPACTION)) {
              compactionCount += 1;
              messages.add(response.toParam());

              // Estimate total tokens consumed; prompt wrap-up if over budget
              if (compactionCount * triggerThreshold >= totalTokenBudget) {
                  messages.add(BetaMessageParam.builder()
                      .role(BetaMessageParam.Role.USER)
                      .content("Please wrap up your current work and summarize the final state.")
                      .build());
              }
          }

          System.out.println(response);

php PHP
  $client = new Client();

  $triggerThreshold = 100_000;
  $totalTokenBudget = 3_000_000;
  $compactionCount = 0;

  $messages = [['role' => 'user', 'content' => 'Hello, Claude']];

  $response = $client->beta->messages->create(
      maxTokens: 4096,
      messages: $messages,
      model: 'claude-opus-5',
      betas: ['compact-2026-01-12'],
      contextManagement: [
          'edits' => [
              [
                  'type' => 'compact_20260112',
                  'trigger' => ['type' => 'input_tokens', 'value' => $triggerThreshold],
                  'pause_after_compaction' => true
              ]
          ]
      ]
  );

  if ($response->stopReason === 'compaction') {
      $compactionCount += 1;
      $messages[] = ['role' => 'assistant', 'content' => $response->content];

      // Estimate total tokens consumed; prompt wrap-up if over budget
      if ($compactionCount * $triggerThreshold >= $totalTokenBudget) {
          $messages[] = [
              'role' => 'user',
              'content' => 'Please wrap up your current work and summarize the final state.'
          ];
      }
  }

ruby Ruby
  client = Anthropic::Client.new
  messages = [{ role: "user", content: "Hello, Claude" }]
  TRIGGER_THRESHOLD = 100_000
  TOTAL_TOKEN_BUDGET = 3_000_000
  compaction_count = 0

  response = client.beta.messages.create(
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: messages,
    context_management: {
      edits: [
        {
          type: "compact_20260112",
          trigger: { type: "input_tokens", value: TRIGGER_THRESHOLD },
          pause_after_compaction: true
        }
      ]
    }
  )

  if response.stop_reason == :compaction
    compaction_count += 1
    messages << { role: "assistant", content: response.content }

    # Estimate total tokens consumed; prompt wrap-up if over budget
    if compaction_count * TRIGGER_THRESHOLD >= TOTAL_TOKEN_BUDGET
      messages << {
        role: "user",
        content: "Please wrap up your current work and summarize the final state."
      }
    end
  end
  ```
</CodeGroup>


## Working with compaction blocks

Source: https://platform.claude.com/llms-full.txt#working-with-compaction-blocks

When compaction is triggered, the API returns a `compaction` block at the start of the assistant response.

A long-running conversation might result in multiple compactions. The last compaction block reflects the final state of the prompt, replacing content prior to it with the generated summary.

```json Output
{
  "content": [
    {
      "type": "compaction",
      "content": "Summary of the conversation: The user requested help building a web scraper..."
    },
    {
      "type": "text",
      "text": "Based on our conversation so far..."
    }
  ]
}

bash cURL
  # The response content, including the compaction block, must go back to the
  # API as the assistant turn of the next request. Managing that message list
  # doesn't translate well to a one-off shell command; see the CLI and SDK
  # tabs for the full flow. First request:
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: compact-2026-01-12" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [
        {
          "role": "user",
          "content": "Hello, Claude"
        }
      ],
      "context_management": {
        "edits": [
          {
            "type": "compact_20260112"
          }
        ]
      }
    }'

bash CLI
  ant beta:messages create \
    --beta compact-2026-01-12 \
    --transform content \
    --format jsonl <<'YAML' > content.json
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Hello, Claude
  context_management:
    edits:
      - type: compact_20260112
  YAML

  # After receiving a response with a compaction block, append it as the
  # assistant turn and continue the conversation
  ant beta:messages create --beta compact-2026-01-12 <<YAML
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Hello, Claude
    - role: assistant
      content: $(cat content.json)
    - role: user
      content: Now add error handling
  context_management:
    edits:
      - type: compact_20260112
  YAML

python Python
  client = anthropic.Anthropic()
  messages = [{"role": "user", "content": "Hello, Claude"}]
  response = client.beta.messages.create(
      betas=["compact-2026-01-12"],
      model="claude-opus-5",
      max_tokens=4096,
      messages=messages,
      context_management={"edits": [{"type": "compact_20260112"}]},
  )
  # After receiving a response with a compaction block
  messages.append({"role": "assistant", "content": response.content})

  # Continue the conversation
  messages.append({"role": "user", "content": "Now add error handling"})

  response = client.beta.messages.create(
      betas=["compact-2026-01-12"],
      model="claude-opus-5",
      max_tokens=4096,
      messages=messages,
      context_management={"edits": [{"type": "compact_20260112"}]},
  )

typescript TypeScript
  const client = new Anthropic();
  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [
    { role: "user", content: "Hello, Claude" }
  ];

  const response = await client.beta.messages.create({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages,
    context_management: {
      edits: [{ type: "compact_20260112" }]
    }
  });

  // After receiving a response with a compaction block
  messages.push({
    role: "assistant",
    content: response.content
  });

  // Continue the conversation
  messages.push({ role: "user", content: "Now add error handling" });

  const nextResponse = await client.beta.messages.create({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages,
    context_management: {
      edits: [{ type: "compact_20260112" }]
    }
  });

csharp C#
  AnthropicClient client = new();

  var messages = new List<BetaMessageParam>
  {
      new() { Role = Role.User, Content = "Help me build a web scraper" }
  };

  var response = await client.Beta.Messages.Create(new()
  {
      Betas = ["compact-2026-01-12"],
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Messages = messages,
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaCompact20260112Edit()]
      }
  });

  messages.Add(new BetaMessageParam
  {
      Role = Role.Assistant,
      Content = response.Content.Select(block => new BetaContentBlockParam(block.Json)).ToList()
  });

  messages.Add(new BetaMessageParam { Role = Role.User, Content = "Now add error handling" });

  var nextResponse = await client.Beta.Messages.Create(new()
  {
      Betas = ["compact-2026-01-12"],
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Messages = messages,
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaCompact20260112Edit()]
      }
  });

  Console.WriteLine(nextResponse);

go Go
  client := anthropic.NewClient()

  messages := []anthropic.BetaMessageParam{
  	anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Help me build a web scraper")),
  }

  compactEdit := anthropic.BetaContextManagementConfigParam{
  	Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  		{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{}},
  	},
  }

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:             anthropic.ModelClaudeOpus5,
  	MaxTokens:         4096,
  	Messages:          messages,
  	ContextManagement: compactEdit,
  	Betas:             []anthropic.AnthropicBeta{"compact-2026-01-12"},
  })
  if err != nil {
  	log.Fatal(err)
  }

  messages = append(messages, response.ToParam())

  messages = append(messages, anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Now add error handling")))

  nextResponse, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:             anthropic.ModelClaudeOpus5,
  	MaxTokens:         4096,
  	Messages:          messages,
  	ContextManagement: compactEdit,
  	Betas:             []anthropic.AnthropicBeta{"compact-2026-01-12"},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(nextResponse)

java Java
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaCompact20260112Edit;
  // ...
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          // First request
          BetaMessage response = client.beta().messages().create(
              MessageCreateParams.builder()
                  .addBeta("compact-2026-01-12")
                  .model("claude-opus-5")
                  .maxTokens(4096L)
                  .addUserMessage("Help me build a web scraper")
                  .contextManagement(BetaContextManagementConfig.builder()
                      .addEdit(BetaCompact20260112Edit.builder().build())
                      .build())
                  .build());

          // After receiving a response with a compaction block, append the full
          // content (including compaction blocks) and continue the conversation
          BetaMessage nextResponse = client.beta().messages().create(
              MessageCreateParams.builder()
                  .addBeta("compact-2026-01-12")
                  .model("claude-opus-5")
                  .maxTokens(4096L)
                  .addUserMessage("Help me build a web scraper")
                  .addMessage(response)
                  .addUserMessage("Now add error handling")
                  .contextManagement(BetaContextManagementConfig.builder()
                      .addEdit(BetaCompact20260112Edit.builder().build())
                      .build())
                  .build());

          System.out.println(nextResponse);

php PHP
  $client = new Client();

  $messages = [
      ['role' => 'user', 'content' => 'Help me build a web scraper']
  ];

  $response = $client->beta->messages->create(
      maxTokens: 4096,
      messages: $messages,
      model: 'claude-opus-5',
      betas: ['compact-2026-01-12'],
      contextManagement: [
          'edits' => [['type' => 'compact_20260112']]
      ]
  );

  $messages[] = ['role' => 'assistant', 'content' => $response->content];

  $messages[] = ['role' => 'user', 'content' => 'Now add error handling'];

  $nextResponse = $client->beta->messages->create(
      maxTokens: 4096,
      messages: $messages,
      model: 'claude-opus-5',
      betas: ['compact-2026-01-12'],
      contextManagement: [
          'edits' => [['type' => 'compact_20260112']]
      ]
  );

  echo json_encode($nextResponse, JSON_PRETTY_PRINT), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  messages = [
    { role: "user", content: "Help me build a web scraper" }
  ]

  response = client.beta.messages.create(
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: messages,
    context_management: {
      edits: [{ type: "compact_20260112" }]
    }
  )

  messages << { role: "assistant", content: response.content }

  messages << { role: "user", content: "Now add error handling" }

  next_response = client.beta.messages.create(
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: messages,
    context_management: {
      edits: [{ type: "compact_20260112" }]
    }
  )

  puts next_response.content

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: compact-2026-01-12" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "stream": true,
      "messages": [
        {
          "role": "user",
          "content": "Hello, Claude"
        }
      ],
      "context_management": {
        "edits": [
          {
            "type": "compact_20260112"
          }
        ]
      }
    }'

bash CLI
  ant beta:messages create \
    --stream \
    --beta compact-2026-01-12 \
    --format jsonl <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Hello, Claude
  context_management:
    edits:
      - type: compact_20260112
  YAML

python Python
  client = anthropic.Anthropic()
  messages = [{"role": "user", "content": "Hello, Claude"}]

  with client.beta.messages.stream(
      betas=["compact-2026-01-12"],
      model="claude-opus-5",
      max_tokens=4096,
      messages=messages,
      context_management={"edits": [{"type": "compact_20260112"}]},
  ) as stream:
      for event in stream:
          if event.type == "content_block_start":
              if event.content_block.type == "compaction":
                  print("Compaction started...")
              elif event.content_block.type == "text":
                  print("Text response started...")

          elif event.type == "content_block_delta":
              if event.delta.type == "compaction_delta":
                  print(f"Compaction complete: {len(event.delta.content or '')} chars")
              elif event.delta.type == "text_delta":
                  print(event.delta.text, end="", flush=True)

      # Get the final accumulated message
      message = stream.get_final_message()
      messages.append({"role": "assistant", "content": message.content})

typescript TypeScript
  const client = new Anthropic();
  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [
    { role: "user", content: "Hello, Claude" }
  ];

  const stream = await client.beta.messages.stream({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages,
    context_management: {
      edits: [{ type: "compact_20260112" }]
    }
  });

  for await (const event of stream) {
    if (event.type === "content_block_start") {
      if (event.content_block.type === "compaction") {
        console.log("Compaction started...");
      } else if (event.content_block.type === "text") {
        console.log("Text response started...");
      }
    } else if (event.type === "content_block_delta") {
      if (event.delta.type === "compaction_delta") {
        console.log(`Compaction complete: ${event.delta.content?.length ?? 0} chars`);
      } else if (event.delta.type === "text_delta") {
        process.stdout.write(event.delta.text);
      }
    }
  }

  // Get the final accumulated message
  const message = await stream.finalMessage();
  messages.push({
    role: "assistant",
    content: message.content
  });

csharp C#
  var client = new AnthropicClient();
  List<BetaMessageParam> messages = [new() { Role = Role.User, Content = "Hello" }];

  var parameters = new MessageCreateParams
  {
      Betas = ["compact-2026-01-12"],
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Messages = messages,
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaCompact20260112Edit()]
      }
  };

  await foreach (var streamEvent in client.Beta.Messages.CreateStreaming(parameters))
  {
      if (streamEvent.TryPickContentBlockStart(out var startEvent))
      {
          if (startEvent.ContentBlock.TryPickBetaCompaction(out _))
          {
              Console.WriteLine("Compaction started...");
          }
          else if (startEvent.ContentBlock.TryPickBetaText(out _))
          {
              Console.WriteLine("Text response started...");
          }
      }
      else if (streamEvent.TryPickContentBlockDelta(out var deltaEvent))
      {
          if (deltaEvent.Delta.TryPickCompaction(out var compactionDelta))
          {
              Console.WriteLine($"Compaction complete: {compactionDelta.Content?.Length ?? 0} chars");
          }
          else if (deltaEvent.Delta.TryPickText(out var textDelta))
          {
              Console.Write(textDelta.Text);
          }
      }
  }

go Go
  client := anthropic.NewClient()
  messages := []anthropic.BetaMessageParam{anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude"))}

  stream := client.Beta.Messages.NewStreaming(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages:  messages,
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{}},
  		},
  	},
  	Betas: []anthropic.AnthropicBeta{"compact-2026-01-12"},
  })

  for stream.Next() {
  	event := stream.Current()
  	switch eventVariant := event.AsAny().(type) {
  	case anthropic.BetaRawContentBlockStartEvent:
  		switch eventVariant.ContentBlock.AsAny().(type) {
  		case anthropic.BetaCompactionBlock:
  			fmt.Println("Compaction started...")
  		case anthropic.BetaTextBlock:
  			fmt.Println("Text response started...")
  		}
  	case anthropic.BetaRawContentBlockDeltaEvent:
  		switch deltaVariant := eventVariant.Delta.AsAny().(type) {
  		case anthropic.BetaCompactionContentBlockDelta:
  			fmt.Printf("Compaction complete: %d chars\n", len(deltaVariant.Content))
  		case anthropic.BetaTextDelta:
  			fmt.Print(deltaVariant.Text)
  		}
  	}
  }
  if err := stream.Err(); err != nil {
  	log.Fatal(err)
  }

java Java
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaCompact20260112Edit;
  // ...
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          MessageCreateParams params = MessageCreateParams.builder()
              .model("claude-opus-5")
              .maxTokens(4096L)
              .addBeta("compact-2026-01-12")
              .addUserMessage("Hello, Claude")
              .contextManagement(BetaContextManagementConfig.builder()
                  .addEdit(BetaCompact20260112Edit.builder().build())
                  .build())
              .build();

          try (var streamResponse = client.beta().messages().createStreaming(params)) {
              streamResponse.stream().forEach(event -> {
                  event.contentBlockStart().ifPresent(startEvent -> {
                      startEvent.contentBlock().compaction().ifPresent(c ->
                          System.out.println("Compaction started...")
                      );
                      startEvent.contentBlock().text().ifPresent(t ->
                          System.out.println("Text response started...")
                      );
                  });

                  event.contentBlockDelta().ifPresent(deltaEvent -> {
                      deltaEvent.delta().compaction().ifPresent(cd ->
                          System.out.println("Compaction complete: " + cd.content().map(String::length).orElse(0) + " chars")
                      );
                      deltaEvent.delta().text().ifPresent(td ->
                          System.out.print(td.text())
                      );
                  });
              });
          }

php PHP
  $client = new Client();
  $messages = [['role' => 'user', 'content' => 'Hello, Claude']];

  $stream = $client->beta->messages->createStream(
      maxTokens: 4096,
      messages: $messages,
      model: 'claude-opus-5',
      betas: ['compact-2026-01-12'],
      contextManagement: [
          'edits' => [
              ['type' => 'compact_20260112']
          ]
      ]
  );

  foreach ($stream as $event) {
      if ($event->type === 'content_block_start') {
          if ($event->contentBlock->type === 'compaction') {
              echo "Compaction started...\n";
          } elseif ($event->contentBlock->type === 'text') {
              echo "Text response started...\n";
          }
      } elseif ($event->type === 'content_block_delta') {
          if ($event->delta->type === 'compaction_delta') {
              echo "Compaction complete: " . strlen($event->delta->content ?? '') . " chars\n";
          } elseif ($event->delta->type === 'text_delta') {
              echo $event->delta->text;
          }
      }
  }

ruby Ruby
  client = Anthropic::Client.new
  messages = [{ role: "user", content: "Hello, Claude" }]

  stream = client.beta.messages.stream(
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: messages,
    context_management: {
      edits: [{ type: "compact_20260112" }]
    }
  )

  stream.each do |event|
    case event.type
    when :content_block_start
      if event.content_block.type == :compaction
        puts "Compaction started..."
      elsif event.content_block.type == :text
        puts "Text response started..."
      end
    when :content_block_delta
      if event.delta.type == :compaction_delta
        puts "Compaction complete: #{(event.delta.content || "").length} chars"
      elsif event.delta.type == :text_delta
        print event.delta.text
      end
    end
  end

json
{
  "role": "assistant",
  "content": [
    {
      "type": "compaction",
      "content": "[summary text]",
      "cache_control": { "type": "ephemeral" }
    },
    {
      "type": "text",
      "text": "Based on our conversation..."
    }
  ]
}

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: compact-2026-01-12" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "system": [
        {
          "type": "text",
          "text": "You are a helpful coding assistant...",
          "cache_control": {
            "type": "ephemeral"
          }
        }
      ],
      "messages": [
        {
          "role": "user",
          "content": "Hello, Claude"
        }
      ],
      "context_management": {
        "edits": [
          {
            "type": "compact_20260112"
          }
        ]
      }
    }'

bash CLI
  ant beta:messages create --beta compact-2026-01-12 <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  system:
    - type: text
      text: You are a helpful coding assistant...
      cache_control:
        type: ephemeral
  messages:
    - role: user
      content: Hello, Claude
  context_management:
    edits:
      - type: compact_20260112
  YAML

python Python
  client = anthropic.Anthropic()
  messages = [{"role": "user", "content": "Hello, Claude"}]
  response = client.beta.messages.create(
      betas=["compact-2026-01-12"],
      model="claude-opus-5",
      max_tokens=4096,
      system=[
          {
              "type": "text",
              "text": "You are a helpful coding assistant...",
              "cache_control": {
                  "type": "ephemeral"
              },  # Cache the system prompt separately
          }
      ],
      messages=messages,
      context_management={"edits": [{"type": "compact_20260112"}]},
  )

typescript TypeScript
  const client = new Anthropic();
  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [
    { role: "user", content: "Hello, Claude" }
  ];

  const response = await client.beta.messages.create({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    system: [
      {
        type: "text",
        text: "You are a helpful coding assistant...",
        cache_control: { type: "ephemeral" } // Cache the system prompt separately
      }
    ],
    messages,
    context_management: {
      edits: [{ type: "compact_20260112" }]
    }
  });

csharp C#
  var client = new AnthropicClient();

  var parameters = new MessageCreateParams
  {
      Betas = ["compact-2026-01-12"],
      Model = "claude-opus-5",
      MaxTokens = 4096,
      System = new List<BetaTextBlockParam>
      {
          new()
          {
              Text = "You are a helpful coding assistant...",
              CacheControl = new BetaCacheControlEphemeral()
          }
      },
      Messages = [new() { Role = Role.User, Content = "Hello, Claude" }],
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaCompact20260112Edit()]
      }
  };

  var response = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	System: []anthropic.BetaTextBlockParam{
  		{
  			Text:         "You are a helpful coding assistant...",
  			CacheControl: anthropic.NewBetaCacheControlEphemeralParam(),
  		},
  	},
  	Messages: []anthropic.BetaMessageParam{anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude"))},
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{}},
  		},
  	},
  	Betas: []anthropic.AnthropicBeta{"compact-2026-01-12"},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaCompact20260112Edit;
  import com.anthropic.models.beta.messages.BetaCacheControlEphemeral;
  // ...
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          MessageCreateParams params = MessageCreateParams.builder()
              .model("claude-opus-5")
              .maxTokens(4096L)
              .addBeta("compact-2026-01-12")
              .systemOfBetaTextBlockParams(List.of(
                  BetaTextBlockParam.builder()
                      .text("You are a helpful coding assistant...")
                      .cacheControl(BetaCacheControlEphemeral.builder().build())
                      .build()
              ))
              .addUserMessage("Hello, Claude")
              .contextManagement(BetaContextManagementConfig.builder()
                  .addEdit(BetaCompact20260112Edit.builder().build())
                  .build())
              .build();

          BetaMessage response = client.beta().messages().create(params);
          System.out.println(response);

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      maxTokens: 4096,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
      model: 'claude-opus-5',
      betas: ['compact-2026-01-12'],
      system: [
          [
              'type' => 'text',
              'text' => 'You are a helpful coding assistant...',
              'cache_control' => [
                  'type' => 'ephemeral'
              ]
          ]
      ],
      contextManagement: [
          'edits' => [
              ['type' => 'compact_20260112']
          ]
      ]
  );

  echo json_encode($response, JSON_PRETTY_PRINT), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    max_tokens: 4096,
    system: [
      {
        type: "text",
        text: "You are a helpful coding assistant...",
        cache_control: {
          type: "ephemeral"
        }
      }
    ],
    messages: [{ role: "user", content: "Hello, Claude" }],
    context_management: {
      edits: [{ type: "compact_20260112" }]
    }
  )
  puts response
  ```
</CodeGroup>

This keeps long system prompts cached across multiple compaction events throughout a conversation.


## Understanding usage

Source: https://platform.claude.com/llms-full.txt#understanding-usage

Compaction requires an additional sampling step, which contributes to rate limits and billing. The API returns detailed usage information in the response:

```json Output
{
  "usage": {
    "input_tokens": 23000,
    "output_tokens": 1000,
    "iterations": [
      {
        "type": "compaction",
        "input_tokens": 180000,
        "output_tokens": 3500
      },
      {
        "type": "message",
        "input_tokens": 23000,
        "output_tokens": 1000
      }
    ]
  }
}
```

The `iterations` array shows usage for each sampling iteration. When compaction occurs, you'll see a `compaction` iteration followed by the main `message` iteration. The top-level `input_tokens` and `output_tokens` match the `message` iteration exactly in this example because there is only one non-compaction iteration. The final iteration's token counts reflect the effective context size after compaction.

<Note>
  The top-level `input_tokens` and `output_tokens` do not include compaction iteration usage. They reflect the sum of all non-compaction iterations. To calculate total tokens consumed and billed for a request, sum across all entries in the `usage.iterations` array.

  If you previously relied on `usage.input_tokens` and `usage.output_tokens` for cost tracking or auditing, you'll need to update your tracking logic to aggregate across `usage.iterations` when compaction is enabled. With the compaction beta enabled, every response includes `usage.iterations`, even if no compaction occurred. A `compaction` entry appears only when a new compaction is triggered during the request. Re-applying a previous `compaction` block incurs no additional compaction cost, and the top-level usage fields remain accurate in that case.
</Note>


## Combining with other features

Source: https://platform.claude.com/llms-full.txt#combining-with-other-features

### Server tools

When using server tools (such as web search), the compaction trigger is checked at the start of each sampling iteration. Compaction might occur multiple times within a single request depending on your trigger threshold and the amount of output generated.

### Token counting

The token counting endpoint (`/v1/messages/count_tokens`) applies existing `compaction` blocks in your prompt but does not trigger new compactions. Use it to check your effective token count after previous compactions:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages/count_tokens \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: compact-2026-01-12" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "messages": [
        {
          "role": "user",
          "content": "Hello, Claude"
        }
      ],
      "context_management": {
        "edits": [
          {
            "type": "compact_20260112"
          }
        ]
      }
    }'

bash CLI
  cat > request.yaml <<'YAML'
  model: claude-opus-5
  messages:
    - role: user
      content: Hello, Claude
  context_management:
    edits:
      - type: compact_20260112
  YAML

  CURRENT=$(ant beta:messages count-tokens \
    --beta compact-2026-01-12 \
    --transform input_tokens \
    --raw-output < request.yaml)

  ORIGINAL=$(ant beta:messages count-tokens \
    --beta compact-2026-01-12 \
    --transform context_management.original_input_tokens \
    --raw-output < request.yaml)

  printf 'Current tokens: %s\n' "$CURRENT"
  printf 'Original tokens: %s\n' "$ORIGINAL"

python Python
  client = anthropic.Anthropic()
  messages = [{"role": "user", "content": "Hello, Claude"}]
  count_response = client.beta.messages.count_tokens(
      betas=["compact-2026-01-12"],
      model="claude-opus-5",
      messages=messages,
      context_management={"edits": [{"type": "compact_20260112"}]},
  )

  print(f"Current tokens: {count_response.input_tokens}")
  print(f"Original tokens: {count_response.context_management.original_input_tokens}")

typescript TypeScript
  const client = new Anthropic();
  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [
    { role: "user", content: "Summarize the key points of our conversation so far." }
  ];

  const countResponse = await client.beta.messages.countTokens({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    messages,
    context_management: {
      edits: [{ type: "compact_20260112" }]
    }
  });

  console.log(`Current tokens: ${countResponse.input_tokens}`);
  console.log(`Original tokens: ${countResponse.context_management!.original_input_tokens}`);

csharp C#
  AnthropicClient client = new();
  List<BetaMessageParam> messages = [new() { Role = Role.User, Content = "Hello" }];

  var countParams = new MessageCountTokensParams
  {
      Model = "claude-opus-5",
      Messages = messages,
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaCompact20260112Edit()]
      },
      Betas = ["compact-2026-01-12"]
  };

  var countResponse = await client.Beta.Messages.CountTokens(countParams);
  Console.WriteLine($"Current tokens: {countResponse.InputTokens}");
  Console.WriteLine($"Original tokens: {countResponse.ContextManagement?.OriginalInputTokens}");

go Go
  client := anthropic.NewClient()
  messages := []anthropic.BetaMessageParam{anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude"))}

  countResponse, err := client.Beta.Messages.CountTokens(context.TODO(), anthropic.BetaMessageCountTokensParams{
  	Model:    anthropic.ModelClaudeOpus5,
  	Messages: messages,
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{}},
  		},
  	},
  	Betas: []anthropic.AnthropicBeta{"compact-2026-01-12"},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Printf("Current tokens: %d\n", countResponse.InputTokens)
  fmt.Printf("Original tokens: %d\n", countResponse.ContextManagement.OriginalInputTokens)

java Java
  import com.anthropic.models.beta.messages.BetaMessageTokensCount;
  import com.anthropic.models.beta.messages.MessageCountTokensParams;
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaCompact20260112Edit;
  // ...
          AnthropicClient client = AnthropicOkHttpClient.fromEnv();

          MessageCountTokensParams params = MessageCountTokensParams.builder()
              .model("claude-opus-5")
              .addUserMessage("Hello, Claude")
              .contextManagement(BetaContextManagementConfig.builder()
                  .addEdit(BetaCompact20260112Edit.builder().build())
                  .build())
              .addBeta("compact-2026-01-12")
              .build();

          BetaMessageTokensCount countResponse = client.beta().messages().countTokens(params);
          System.out.println("Current tokens: " + countResponse.inputTokens());
          System.out.println("Original tokens: " + countResponse.contextManagement().get().originalInputTokens());

php PHP
  $client = new Client();
  $messages = [['role' => 'user', 'content' => 'Hello, Claude']];

  $countResponse = $client->beta->messages->countTokens(
      messages: $messages,
      model: 'claude-opus-5',
      betas: ['compact-2026-01-12'],
      contextManagement: [
          'edits' => [
              ['type' => 'compact_20260112']
          ]
      ]
  );

  echo "Current tokens: " . $countResponse->inputTokens . "\n";
  echo "Original tokens: " . $countResponse->contextManagement->originalInputTokens . "\n";

ruby Ruby
  client = Anthropic::Client.new
  messages = [{ role: "user", content: "Hello, Claude" }]

  count_response = client.beta.messages.count_tokens(
    betas: ["compact-2026-01-12"],
    model: "claude-opus-5",
    messages: messages,
    context_management: {
      edits: [{ type: "compact_20260112" }]
    }
  )

  puts "Current tokens: #{count_response.input_tokens}"
  puts "Original tokens: #{count_response.context_management.original_input_tokens}"
  ```
</CodeGroup>


## Examples

Source: https://platform.claude.com/llms-full.txt#examples

Here's a complete example of a long-running conversation with compaction:

<CodeGroup>
  ```bash cURL
  # curl sends individual requests; maintain the messages array in the
  # calling script. See the SDK tabs for the full chat() loop. Single-turn
  # request shape:
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: compact-2026-01-12" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [
        {
          "role": "user",
          "content": "Help me build a Python web scraper"
        }
      ],
      "context_management": {
        "edits": [
          {
            "type": "compact_20260112",
            "trigger": {
              "type": "input_tokens",
              "value": 100000
            }
          }
        ]
      }
    }'

bash CLI
  # The CLI handles individual turns; maintain the messages array in the
  # calling script. See the SDK tabs for the full chat() loop. Single-turn
  # request shape:
  ant beta:messages create \
    --beta compact-2026-01-12 \
    --transform 'content.#(type=="text").text' \
    --raw-output <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Help me build a Python web scraper
  context_management:
    edits:
      - type: compact_20260112
        trigger:
          type: input_tokens
          value: 100000
  YAML

python Python
  client = anthropic.Anthropic()

  messages: list[dict] = []


  def chat(user_message: str) -> str:
      messages.append({"role": "user", "content": user_message})

      response = client.beta.messages.create(
          betas=["compact-2026-01-12"],
          model="claude-opus-5",
          max_tokens=4096,
          messages=messages,
          context_management={
              "edits": [
                  {
                      "type": "compact_20260112",
                      "trigger": {"type": "input_tokens", "value": 100000},
                  }
              ]
          },
      )

      # Append response (compaction blocks are automatically included)
      messages.append({"role": "assistant", "content": response.content})

      # Return the text content
      return next(block.text for block in response.content if block.type == "text")


  # Run a long conversation
  print(chat("Help me build a Python web scraper"))
  print(chat("Add support for JavaScript-rendered pages"))
  print(chat("Now add rate limiting and error handling"))
  # Continue calling chat() for as long as the conversation needs

typescript TypeScript
  const client = new Anthropic();

  const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [];

  async function chat(userMessage: string): Promise<string> {
    messages.push({ role: "user", content: userMessage });

    const response = await client.beta.messages.create({
      betas: ["compact-2026-01-12"],
      model: "claude-opus-5",
      max_tokens: 4096,
      messages,
      context_management: {
        edits: [
          {
            type: "compact_20260112",
            trigger: { type: "input_tokens", value: 100000 }
          }
        ]
      }
    });

    // Append response (compaction blocks are automatically included)
    messages.push({ role: "assistant", content: response.content });

    // Return the text content
    const textBlock = response.content.find((block) => block.type === "text");
    return textBlock?.text ?? "";
  }

  // Run a long conversation
  console.log(await chat("Help me build a Python web scraper"));
  console.log(await chat("Add support for JavaScript-rendered pages"));
  console.log(await chat("Now add rate limiting and error handling"));
  // Continue calling chat() for as long as the conversation needs

csharp C#
  AnthropicClient client = new();
  List<BetaMessageParam> messages = new();

  Console.WriteLine(await Chat(client, messages, "Help me build a Python web scraper"));
  Console.WriteLine(await Chat(client, messages, "Add support for JavaScript-rendered pages"));
  Console.WriteLine(await Chat(client, messages, "Now add rate limiting and error handling"));

  static async Task<string> Chat(AnthropicClient client, List<BetaMessageParam> messages, string userMessage)
  {
      messages.Add(new() { Role = Role.User, Content = userMessage });

      var parameters = new MessageCreateParams
      {
          Betas = ["compact-2026-01-12"],
          Model = "claude-opus-5",
          MaxTokens = 4096,
          Messages = messages,
          ContextManagement = new BetaContextManagementConfig
          {
              Edits = [new BetaCompact20260112Edit
              {
                  Trigger = new BetaInputTokensTrigger(100000)
              }]
          }
      };

      var response = await client.Beta.Messages.Create(parameters);

      messages.Add(new()
      {
          Role = Role.Assistant,
          Content = response.Content.Select(block => new BetaContentBlockParam(block.Json)).ToList()
      });

      return response.Content
          .Select(block => block.Value)
          .OfType<BetaTextBlock>()
          .Select(tb => tb.Text)
          .FirstOrDefault() ?? "";
  }

go Go
  package main

  import (
  	"context"
  	"fmt"
  	"log"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  var (
  	client   = anthropic.NewClient()
  	messages []anthropic.BetaMessageParam
  )

  func chat(userMessage string) string {
  	messages = append(messages, anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock(userMessage)))

  	response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 4096,
  		Messages:  messages,
  		ContextManagement: anthropic.BetaContextManagementConfigParam{
  			Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  				{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{
  					Trigger: anthropic.BetaInputTokensTriggerParam{Value: 100000},
  				}},
  			},
  		},
  		Betas: []anthropic.AnthropicBeta{"compact-2026-01-12"},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	messages = append(messages, response.ToParam())

  	for _, block := range response.Content {
  		if variant, ok := block.AsAny().(anthropic.BetaTextBlock); ok {
  			return variant.Text
  		}
  	}
  	return ""
  }

  func main() {
  	fmt.Println(chat("Help me build a Python web scraper"))
  	fmt.Println(chat("Add support for JavaScript-rendered pages"))
  	fmt.Println(chat("Now add rate limiting and error handling"))
  }

java Java
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaCompact20260112Edit;
  import com.anthropic.models.beta.messages.BetaInputTokensTrigger;
  // ...
      private static final AnthropicClient client = AnthropicOkHttpClient.fromEnv();
      private static final List<BetaMessageParam> messages = new ArrayList<>();

      public static void main(String[] args) {
          System.out.println(chat("Help me build a Python web scraper"));
          System.out.println(chat("Add support for JavaScript-rendered pages"));
          System.out.println(chat("Now add rate limiting and error handling"));
      }

      private static String chat(String userMessage) {
          messages.add(BetaMessageParam.builder()
              .role(BetaMessageParam.Role.USER)
              .content(userMessage)
              .build());

          MessageCreateParams params = MessageCreateParams.builder()
              .addBeta("compact-2026-01-12")
              .model("claude-opus-5")
              .maxTokens(4096L)
              .messages(messages)
              .contextManagement(BetaContextManagementConfig.builder()
                  .addEdit(BetaCompact20260112Edit.builder()
                      .trigger(BetaInputTokensTrigger.builder()
                          .value(100000L)
                          .build())
                      .build())
                  .build())
              .build();

          BetaMessage response = client.beta().messages().create(params);

          // Append response (compaction blocks are automatically included)
          messages.add(response.toParam());

          return response.content().stream()
              .filter(block -> block.text().isPresent())
              .map(block -> block.text().get().text())
              .findFirst()
              .orElse("");
      }

php PHP
  $client = new Client();
  $messages = [];

  function chat($client, &$messages, $userMessage) {
      $messages[] = ['role' => 'user', 'content' => $userMessage];

      $response = $client->beta->messages->create(
          maxTokens: 4096,
          messages: $messages,
          model: 'claude-opus-5',
          betas: ['compact-2026-01-12'],
          contextManagement: [
              'edits' => [
                  [
                      'type' => 'compact_20260112',
                      'trigger' => ['type' => 'input_tokens', 'value' => 100000]
                  ]
              ]
          ]
      );

      $messages[] = ['role' => 'assistant', 'content' => $response->content];

      foreach ($response->content as $block) {
          if ($block->type === 'text') {
              return $block->text;
          }
      }
      return '';
  }

  echo chat($client, $messages, "Help me build a Python web scraper") . "\n";
  echo chat($client, $messages, "Add support for JavaScript-rendered pages") . "\n";
  echo chat($client, $messages, "Now add rate limiting and error handling") . "\n";

ruby Ruby
  client = Anthropic::Client.new
  messages = []

  def chat(client, messages, user_message)
    messages << { role: "user", content: user_message }

    response = client.beta.messages.create(
      betas: ["compact-2026-01-12"],
      model: "claude-opus-5",
      max_tokens: 4096,
      messages: messages,
      context_management: {
        edits: [
          {
            type: "compact_20260112",
            trigger: { type: "input_tokens", value: 100000 }
          }
        ]
      }
    )

    messages << { role: "assistant", content: response.content }

    response.content.find { |block| block.type == :text }&.text || ""
  end

  puts chat(client, messages, "Help me build a Python web scraper")
  puts chat(client, messages, "Add support for JavaScript-rendered pages")
  puts chat(client, messages, "Now add rate limiting and error handling")

bash cURL
  # curl sends individual requests; maintain the messages array in the
  # calling script. See the SDK tabs for the full chat() loop with
  # pause-and-preserve handling. Single-turn request shape:
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: compact-2026-01-12" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "messages": [
        {
          "role": "user",
          "content": "Help me build a Python web scraper"
        }
      ],
      "context_management": {
        "edits": [
          {
            "type": "compact_20260112",
            "trigger": {
              "type": "input_tokens",
              "value": 100000
            },
            "pause_after_compaction": true
          }
        ]
      }
    }'

bash CLI
  # The CLI handles individual turns; maintain the messages array in the
  # calling script. See the SDK tabs for the full chat() loop with
  # pause-and-preserve handling. Single-turn request shape:
  ant beta:messages create \
    --beta compact-2026-01-12 \
    --transform 'content.#(type=="text").text' \
    --raw-output <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Help me build a Python web scraper
  context_management:
    edits:
      - type: compact_20260112
        trigger:
          type: input_tokens
          value: 100000
        pause_after_compaction: true
  YAML

python Python
  from typing import Any

  client = anthropic.Anthropic()

  messages: list[dict[str, Any]] = []


  def chat(user_message: str) -> str:
      messages.append({"role": "user", "content": user_message})

      response = client.beta.messages.create(
          betas=["compact-2026-01-12"],
          model="claude-opus-5",
          max_tokens=4096,
          messages=messages,
          context_management={
              "edits": [
                  {
                      "type": "compact_20260112",
                      "trigger": {"type": "input_tokens", "value": 100000},
                      "pause_after_compaction": True,
                  }
              ]
          },
      )

      # Check if compaction occurred and paused
      if response.stop_reason == "compaction":
          # Get the compaction block from the response
          compaction_block = response.content[0]

          # Preserve the prior exchange + current user message (3 messages)
          # by including them after the compaction block
          preserved_messages = messages[-3:] if len(messages) >= 3 else messages

          # Build new message list: compaction + preserved messages
          new_assistant_content = [compaction_block]
          messages_after_compaction = [
              {"role": "assistant", "content": new_assistant_content}
          ] + preserved_messages

          # Continue the request with the compacted context + preserved messages
          response = client.beta.messages.create(
              betas=["compact-2026-01-12"],
              model="claude-opus-5",
              max_tokens=4096,
              messages=messages_after_compaction,
              context_management={"edits": [{"type": "compact_20260112"}]},
          )

          # Update the message list to reflect the compaction
          messages.clear()
          messages.extend(messages_after_compaction)

      # Append the final response
      messages.append({"role": "assistant", "content": response.content})

      # Return the text content
      return next(block.text for block in response.content if block.type == "text")


  # Run a long conversation
  print(chat("Help me build a Python web scraper"))
  print(chat("Add support for JavaScript-rendered pages"))
  print(chat("Now add rate limiting and error handling"))
  # Continue calling chat() for as long as the conversation needs

typescript TypeScript
  const client = new Anthropic();

  let messages: Anthropic.Beta.Messages.BetaMessageParam[] = [];

  async function chat(userMessage: string): Promise<string> {
    messages.push({ role: "user", content: userMessage });

    let response = await client.beta.messages.create({
      betas: ["compact-2026-01-12"],
      model: "claude-opus-5",
      max_tokens: 4096,
      messages,
      context_management: {
        edits: [
          {
            type: "compact_20260112",
            trigger: { type: "input_tokens", value: 100000 },
            pause_after_compaction: true
          }
        ]
      }
    });

    // Check if compaction occurred and paused
    if (response.stop_reason === "compaction") {
      // Get the compaction block from the response
      const compactionBlock = response.content[0];

      // Preserve the prior exchange + current user message (3 messages)
      // by including them after the compaction block
      const preservedMessages = messages.length >= 3 ? messages.slice(-3) : [...messages];

      // Build new message list: compaction + preserved messages
      const messagesAfterCompaction: Anthropic.Beta.Messages.BetaMessageParam[] = [
        { role: "assistant", content: [compactionBlock] },
        ...preservedMessages
      ];

      // Continue the request with the compacted context + preserved messages
      response = await client.beta.messages.create({
        betas: ["compact-2026-01-12"],
        model: "claude-opus-5",
        max_tokens: 4096,
        messages: messagesAfterCompaction,
        context_management: {
          edits: [{ type: "compact_20260112" }]
        }
      });

      // Update the message list to reflect the compaction
      messages = messagesAfterCompaction;
    }

    // Append the final response
    messages.push({ role: "assistant", content: response.content });

    // Return the text content
    const textBlock = response.content.find((block) => block.type === "text");
    return textBlock?.text ?? "";
  }

  // Run a long conversation
  console.log(await chat("Help me build a Python web scraper"));
  console.log(await chat("Add support for JavaScript-rendered pages"));
  console.log(await chat("Now add rate limiting and error handling"));
  // Continue calling chat() for as long as the conversation needs

csharp C#
  AnthropicClient client = new();
  List<BetaMessageParam> messages = new();

  Console.WriteLine(await Chat("Help me build a Python web scraper"));
  Console.WriteLine(await Chat("Add support for JavaScript-rendered pages"));
  Console.WriteLine(await Chat("Now add rate limiting and error handling"));

  async Task<string> Chat(string userMessage)
  {
      messages.Add(new() { Role = Role.User, Content = userMessage });

      var response = await client.Beta.Messages.Create(new()
      {
          Betas = ["compact-2026-01-12"],
          Model = "claude-opus-5",
          MaxTokens = 4096,
          Messages = messages,
          ContextManagement = new BetaContextManagementConfig
          {
              Edits = [new BetaCompact20260112Edit
              {
                  Trigger = new BetaInputTokensTrigger(100000),
                  PauseAfterCompaction = true
              }]
          }
      });

      if (response.StopReason == BetaStopReason.Compaction)
      {
          if (!response.Content[0].TryPickCompaction(out _))
              throw new InvalidOperationException("Expected compaction block");

          var preserved = messages.Count >= 3
              ? messages.Skip(messages.Count - 3).ToList()
              : new List<BetaMessageParam>(messages);

          var messagesAfterCompaction = new List<BetaMessageParam>
          {
              new()
              {
                  Role = Role.Assistant,
                  Content = new List<BetaContentBlockParam> { new BetaContentBlockParam(response.Content[0].Json) }
              }
          };
          messagesAfterCompaction.AddRange(preserved);

          response = await client.Beta.Messages.Create(new()
          {
              Betas = ["compact-2026-01-12"],
              Model = "claude-opus-5",
              MaxTokens = 4096,
              Messages = messagesAfterCompaction,
              ContextManagement = new BetaContextManagementConfig
              {
                  Edits = [new BetaCompact20260112Edit()]
              }
          });

          messages = messagesAfterCompaction;
      }

      messages.Add(new()
      {
          Role = Role.Assistant,
          Content = response.Content.Select(block => new BetaContentBlockParam(block.Json)).ToList()
      });

      return response.Content
          .Select(block => block.Value)
          .OfType<BetaTextBlock>()
          .Select(tb => tb.Text)
          .FirstOrDefault() ?? "";
  }

go Go
  package main

  import (
  	"context"
  	"fmt"
  	"log"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  var (
  	client   = anthropic.NewClient()
  	messages []anthropic.BetaMessageParam
  )

  func chat(userMessage string) string {
  	messages = append(messages, anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock(userMessage)))

  	compactEdit := anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{
  				Trigger:              anthropic.BetaInputTokensTriggerParam{Value: 100000},
  				PauseAfterCompaction: anthropic.Bool(true),
  			}},
  		},
  	}

  	response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  		Model:             anthropic.ModelClaudeOpus5,
  		MaxTokens:         4096,
  		Messages:          messages,
  		ContextManagement: compactEdit,
  		Betas:             []anthropic.AnthropicBeta{"compact-2026-01-12"},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	if response.StopReason == "compaction" {
  		compactionParam := response.Content[0].ToParam()

  		var preserved []anthropic.BetaMessageParam
  		if len(messages) >= 3 {
  			preserved = messages[len(messages)-3:]
  		} else {
  			preserved = messages
  		}

  		messagesAfterCompaction := []anthropic.BetaMessageParam{
  			{Role: anthropic.BetaMessageParamRoleAssistant, Content: []anthropic.BetaContentBlockParamUnion{compactionParam}},
  		}
  		messagesAfterCompaction = append(messagesAfterCompaction, preserved...)

  		response, err = client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  			Model:     anthropic.ModelClaudeOpus5,
  			MaxTokens: 4096,
  			Messages:  messagesAfterCompaction,
  			ContextManagement: anthropic.BetaContextManagementConfigParam{
  				Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  					{OfCompact20260112: &anthropic.BetaCompact20260112EditParam{}},
  				},
  			},
  			Betas: []anthropic.AnthropicBeta{"compact-2026-01-12"},
  		})
  		if err != nil {
  			log.Fatal(err)
  		}

  		messages = messagesAfterCompaction
  	}

  	messages = append(messages, response.ToParam())

  	for _, block := range response.Content {
  		if textBlock, ok := block.AsAny().(anthropic.BetaTextBlock); ok {
  			return textBlock.Text
  		}
  	}
  	return ""
  }

  func main() {
  	fmt.Println(chat("Help me build a Python web scraper"))
  	fmt.Println(chat("Add support for JavaScript-rendered pages"))
  	fmt.Println(chat("Now add rate limiting and error handling"))
  }

java Java
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaCompact20260112Edit;
  import com.anthropic.models.beta.messages.BetaInputTokensTrigger;
  import com.anthropic.models.beta.messages.BetaStopReason;
  // ...
      private static final AnthropicClient client = AnthropicOkHttpClient.fromEnv();
      private static final List<BetaMessageParam> messages = new ArrayList<>();

      public static String chat(String userMessage) {
          messages.add(BetaMessageParam.builder()
              .role(BetaMessageParam.Role.USER)
              .content(userMessage)
              .build());

          MessageCreateParams params = MessageCreateParams.builder()
              .addBeta("compact-2026-01-12")
              .model("claude-opus-5")
              .maxTokens(4096L)
              .messages(messages)
              .contextManagement(BetaContextManagementConfig.builder()
                  .addEdit(BetaCompact20260112Edit.builder()
                      .trigger(BetaInputTokensTrigger.builder()
                          .value(100000L)
                          .build())
                      .pauseAfterCompaction(true)
                      .build())
                  .build())
              .build();

          BetaMessage response = client.beta().messages().create(params);

          // Check if compaction occurred and paused
          if (response.stopReason().isPresent()
                  && response.stopReason().get().equals(BetaStopReason.COMPACTION)) {
              // Preserve the prior exchange + current user message (3 messages)
              List<BetaMessageParam> preservedMessages = messages.size() >= 3
                  ? new ArrayList<>(messages.subList(messages.size() - 3, messages.size()))
                  : new ArrayList<>(messages);

              // Build new message list: compaction + preserved messages
              List<BetaMessageParam> messagesAfterCompaction = new ArrayList<>();
              messagesAfterCompaction.add(response.toParam());
              messagesAfterCompaction.addAll(preservedMessages);

              // Continue the request with the compacted context + preserved messages
              MessageCreateParams continueParams = MessageCreateParams.builder()
                  .addBeta("compact-2026-01-12")
                  .model("claude-opus-5")
                  .maxTokens(4096L)
                  .messages(messagesAfterCompaction)
                  .contextManagement(BetaContextManagementConfig.builder()
                      .addEdit(BetaCompact20260112Edit.builder().build())
                      .build())
                  .build();

              response = client.beta().messages().create(continueParams);

              // Update the message list to reflect the compaction
              messages.clear();
              messages.addAll(messagesAfterCompaction);
          }

          // Append the final response
          messages.add(response.toParam());

          return response.content().stream()
              .filter(block -> block.text().isPresent())
              .map(block -> block.text().get().text())
              .findFirst()
              .orElse("");
      }

      public static void main(String[] args) {
          System.out.println(chat("Help me build a Python web scraper"));
          System.out.println(chat("Add support for JavaScript-rendered pages"));
          System.out.println(chat("Now add rate limiting and error handling"));
      }

php PHP
  $client = new Client();
  $messages = [];

  function chat($client, &$messages, $userMessage) {
      $messages[] = ['role' => 'user', 'content' => $userMessage];

      $response = $client->beta->messages->create(
          maxTokens: 4096,
          messages: $messages,
          model: 'claude-opus-5',
          betas: ['compact-2026-01-12'],
          contextManagement: [
              'edits' => [
                  [
                      'type' => 'compact_20260112',
                      'trigger' => ['type' => 'input_tokens', 'value' => 100000],
                      'pause_after_compaction' => true
                  ]
              ]
          ]
      );

      if ($response->stopReason === 'compaction') {
          $compactionBlock = $response->content[0];

          $preserved = count($messages) >= 3
              ? array_slice($messages, -3)
              : $messages;

          $messagesAfterCompaction = array_merge(
              [['role' => 'assistant', 'content' => [$compactionBlock]]],
              $preserved
          );

          $response = $client->beta->messages->create(
              maxTokens: 4096,
              messages: $messagesAfterCompaction,
              model: 'claude-opus-5',
              betas: ['compact-2026-01-12'],
              contextManagement: [
                  'edits' => [['type' => 'compact_20260112']]
              ]
          );

          $messages = $messagesAfterCompaction;
      }

      $messages[] = ['role' => 'assistant', 'content' => $response->content];

      foreach ($response->content as $block) {
          if ($block->type === 'text') {
              return $block->text;
          }
      }
      return '';
  }

  echo chat($client, $messages, "Help me build a Python web scraper") . "\n";
  echo chat($client, $messages, "Add support for JavaScript-rendered pages") . "\n";
  echo chat($client, $messages, "Now add rate limiting and error handling") . "\n";

ruby Ruby
  client = Anthropic::Client.new
  messages = []

  def chat(client, messages, user_message)
    messages << { role: "user", content: user_message }

    response = client.beta.messages.create(
      betas: ["compact-2026-01-12"],
      model: "claude-opus-5",
      max_tokens: 4096,
      messages: messages,
      context_management: {
        edits: [
          {
            type: "compact_20260112",
            trigger: { type: "input_tokens", value: 100000 },
            pause_after_compaction: true
          }
        ]
      }
    )

    if response.stop_reason == :compaction
      compaction_block = response.content[0]

      preserved = messages.length >= 3 ? messages[-3..-1] : messages.dup

      messages_after_compaction = [
        { role: "assistant", content: [compaction_block] }
      ] + preserved

      response = client.beta.messages.create(
        betas: ["compact-2026-01-12"],
        model: "claude-opus-5",
        max_tokens: 4096,
        messages: messages_after_compaction,
        context_management: {
          edits: [{ type: "compact_20260112" }]
        }
      )

      messages.clear
      messages.concat(messages_after_compaction)
    end

    messages << { role: "assistant", content: response.content }

    response.content.find { |block| block.type == :text }&.text || ""
  end

  puts chat(client, messages, "Help me build a Python web scraper")
  puts chat(client, messages, "Add support for JavaScript-rendered pages")
  puts chat(client, messages, "Now add rate limiting and error handling")
  ```
</CodeGroup>


## Current limitations

Source: https://platform.claude.com/llms-full.txt#current-limitations

* **Same model for summarization:** The model specified in your request is used for summarization. There is no option to use a different (for example, cheaper) model for the summary.

* **Compaction might fail when tools are defined:** When your request includes `tools`, the model occasionally calls a tool during the internal summarization step instead of writing a summary. When this occurs, the response contains a `compaction` block with `content: null`. To prevent this, set [`instructions`](https://platform.claude.com/docs/en/build-with-claude/compaction#custom-summarization-instructions) to a prompt that explicitly tells the model not to call tools, for example:

  ```text wrap
  Summarize the transcript inside <summary></summary> tags. Include relevant information in the summary for continuing the task in the next context window. Do not call any tools while writing this summary; respond with text only.
  ```


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-48

<CardGroup cols={3}>
  <Card title="Context editing" icon="edit" href="https://platform.claude.com/docs/en/build-with-claude/context-editing">
    Automatically manage conversation context as it grows with context editing.
  </Card>

  <Card title="Context windows" icon="arrows-left-right" href="https://platform.claude.com/docs/en/build-with-claude/context-windows">
    Learn about context window sizes and management strategies.
  </Card>

  <Card title="Session memory compaction cookbook" icon="book" href="https://platform.claude.com/cookbook/misc-session-memory-compaction">
    Explore a practical implementation that manages long-running conversations with instant session memory compaction using background threading and prompt caching.
  </Card>
</CardGroup>


---
title: Context editing
url: https://platform.claude.com/docs/en/build-with-claude/context-editing
description: Automatically manage conversation context as it grows with context editing.
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>


## Overview

Source: https://platform.claude.com/llms-full.txt#overview-2

<Note>
  For most use cases, [server-side compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) is the primary strategy for managing context in long-running conversations. The strategies on this page are useful for specific scenarios where you need more fine-grained control over what content is cleared.
</Note>

Context editing allows you to selectively clear specific content from conversation history as it grows. Beyond optimizing costs and staying within limits, this is about actively curating what Claude sees: context is a finite resource with diminishing returns, and irrelevant content degrades model focus. Context editing gives you fine-grained runtime control over that curation. For the broader principles behind context management, see [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). This page covers:

* **Tool result clearing** - Best for agentic workflows with heavy tool use where old tool results are no longer needed
* **Thinking block clearing** - For managing thinking blocks when using extended thinking, with options to preserve recent thinking for context continuity
* **Client-side SDK compaction** - An SDK-based alternative for summary-based context management (server-side compaction is generally preferred)

| Approach        | Where it runs | Strategies                                                                                            | How it works                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------- | ------------- | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Server-side** | API           | Tool result clearing (`clear_tool_uses_20250919`) Thinking block clearing (`clear_thinking_20251015`) | Applied before the prompt reaches Claude. Clears specific content from conversation history. Each strategy can be configured independently.                                                                                                                                                                                                                                                                 |
| **Client-side** | SDK           | Compaction                                                                                            | Available in [TypeScript and Ruby SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) when using [`tool_runner`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner). Generates a summary and replaces full conversation history. See [Client-side compaction](https://platform.claude.com/docs/en/build-with-claude/context-editing#client-side-compaction-sdk). |


## Server-side strategies

Source: https://platform.claude.com/llms-full.txt#server-side-strategies

<Note>
  Context editing is in beta with support for tool result clearing and thinking block clearing. To enable it, use the beta header `context-management-2025-06-27` in your API requests.

  Share feedback on this feature through the [feedback form](https://forms.gle/YXC2EKGMhjN1c4L88).
</Note>

### Tool result clearing

The `clear_tool_uses_20250919` strategy clears tool results when conversation context grows beyond your configured threshold. This is particularly useful for agentic workflows with heavy tool use. Older tool results (like file contents or search results) are no longer needed once Claude has processed them.

When activated, the API automatically clears the oldest tool results in chronological order. The API replaces each cleared result with placeholder text indicating to Claude that it was removed. By default, only tool results are cleared. You can optionally clear both tool results and tool calls (the tool use parameters) by setting `clear_tool_inputs` to true.

### Thinking block clearing

The `clear_thinking_20251015` strategy manages `thinking` blocks in conversations when extended thinking is enabled. This strategy gives you control over thinking preservation: you can choose to keep more thinking blocks to maintain reasoning continuity, or clear them more aggressively to save context space.

<Tip>
  **Default behavior:** The default varies by model class.

  | Model class      | Keep all prior thinking     | Keep only the last turn's thinking  |
  | ---------------- | --------------------------- | ----------------------------------- |
  | Opus             | Claude Opus 4.5 and later   | Claude Opus 4.1 and earlier         |
  | Sonnet           | Claude Sonnet 4.6 and later | Claude Sonnet 4.5 and earlier       |
  | Haiku            | (none)                      | All models through Claude Haiku 4.5 |
  | Fable and Mythos | All models                  | (none)                              |

  Use this strategy to override the default. If your code runs across multiple model tiers, set `keep` explicitly rather than relying on the per-model default.
</Tip>

An assistant conversation turn may include multiple content blocks (for example, when using tools) and multiple thinking blocks (for example, with [interleaved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#interleaved-thinking)).

### Context editing happens server-side

Context editing is applied server-side before the prompt reaches Claude. Your client application maintains the full, unmodified conversation history. You do not need to sync your client state with the edited version. Continue managing your full conversation history locally as you normally would.

On Claude Fable 5.1, server-side context management never invalidates thinking blocks. Client-side edits to earlier turns can invalidate the thinking blocks in every later assistant turn. For new accounts created on or after August 31, 2026, a request that replays an invalidated block is rejected unless you opt into dropping it. See [Preserved thinking](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-in-conversation).

### Context editing and prompt caching

Context editing's interaction with [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) varies by strategy:

* **Tool result clearing:** Invalidates cached prompt prefixes when content is cleared. To account for this, clear enough tokens to make the cache invalidation worthwhile. Use the `clear_at_least` parameter to ensure a minimum number of tokens is cleared each time. You'll incur cache write costs each time content is cleared, but subsequent requests can reuse the newly cached prefix.

* **Thinking block clearing:** When thinking blocks are **kept** in context (not cleared), the prompt cache is preserved, enabling cache hits and reducing input token costs. When thinking blocks are **cleared**, the cache is invalidated at the point where clearing occurs. Configure the `keep` parameter based on whether you want to prioritize cache performance or context window availability.


## Supported models

Source: https://platform.claude.com/llms-full.txt#supported-models-3

Context editing is available on all supported Claude models.


## Tool result clearing usage

Source: https://platform.claude.com/llms-full.txt#tool-result-clearing-usage

The simplest way to enable tool result clearing is to specify only the strategy type. All other [configuration options](https://platform.claude.com/docs/en/build-with-claude/context-editing#configuration-options-for-tool-result-clearing) use their default values:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --header "anthropic-beta: context-management-2025-06-27" \
      --data '{
          "model": "claude-opus-5",
          "max_tokens": 4096,
          "messages": [
              {
                  "role": "user",
                  "content": "Search for recent developments in AI"
              }
          ],
          "tools": [
              {
                  "type": "web_search_20250305",
                  "name": "web_search"
              }
          ],
          "context_management": {
              "edits": [
                  {"type": "clear_tool_uses_20250919"}
              ]
          }
      }'

bash CLI
  ant beta:messages create --beta context-management-2025-06-27 <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Search for recent developments in AI
  tools:
    - type: web_search_20250305
      name: web_search
  context_management:
    edits:
      - type: clear_tool_uses_20250919
  YAML

python Python
  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      messages=[{"role": "user", "content": "Search for recent developments in AI"}],
      tools=[{"type": "web_search_20250305", "name": "web_search"}],
      betas=["context-management-2025-06-27"],
      context_management={"edits": [{"type": "clear_tool_uses_20250919"}]},
  )

typescript TypeScript
  const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY
  });

  const response = await anthropic.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Search for recent developments in AI"
      }
    ],
    tools: [
      {
        type: "web_search_20250305",
        name: "web_search"
      }
    ],
    context_management: {
      edits: [{ type: "clear_tool_uses_20250919" }]
    },
    betas: ["context-management-2025-06-27"]
  });

csharp C#
  using Anthropic;
  using Anthropic.Models.Beta;
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Messages::Model.ClaudeOpus5,
      MaxTokens = 4096,
      Messages = [
          new() { Role = Role.User, Content = "Search for recent developments in AI" }
      ],
      Tools = [
          new BetaWebSearchTool20250305()
      ],
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaClearToolUses20250919Edit()]
      },
      Betas = [AnthropicBeta.ContextManagement2025_06_27]
  };

  var response = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Search for recent developments in AI")),
  	},
  	Tools: []anthropic.BetaToolUnionParam{
  		{OfWebSearchTool20250305: &anthropic.BetaWebSearchTool20250305Param{}},
  	},
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfClearToolUses20250919: &anthropic.BetaClearToolUses20250919EditParam{}},
  		},
  	},
  	Betas: []anthropic.AnthropicBeta{
  		anthropic.AnthropicBetaContextManagement2025_06_27,
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaWebSearchTool20250305;
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaClearToolUses20250919Edit;
  import com.anthropic.models.beta.AnthropicBeta;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .addUserMessage("Search for recent developments in AI")
          .addTool(BetaWebSearchTool20250305.builder().build())
          .contextManagement(BetaContextManagementConfig.builder()
              .addEdit(BetaClearToolUses20250919Edit.builder().build())
              .build())
          .addBeta(AnthropicBeta.CONTEXT_MANAGEMENT_2025_06_27)
          .build();

      BetaMessage response = client.beta().messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Search for recent developments in AI']
      ],
      model: 'claude-opus-5',
      betas: ['context-management-2025-06-27'],
      tools: [
          ['type' => 'web_search_20250305', 'name' => 'web_search']
      ],
      contextManagement: [
          'edits' => [
              ['type' => 'clear_tool_uses_20250919']
          ]
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      { role: "user", content: "Search for recent developments in AI" }
    ],
    tools: [
      { type: "web_search_20250305", name: "web_search" }
    ],
    context_management: {
      edits: [
        { type: "clear_tool_uses_20250919" }
      ]
    },
    betas: ["context-management-2025-06-27"]
  )
  puts response

bash cURL
  curl https://api.anthropic.com/v1/messages \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --header "anthropic-beta: context-management-2025-06-27" \
      --data '{
          "model": "claude-opus-5",
          "max_tokens": 4096,
          "messages": [
              {
                  "role": "user",
                  "content": "Create a simple command line calculator app using Python"
              }
          ],
          "tools": [
              {
                  "type": "text_editor_20250728",
                  "name": "str_replace_based_edit_tool",
                  "max_characters": 10000
              },
              {
                  "type": "web_search_20250305",
                  "name": "web_search",
                  "max_uses": 3
              }
          ],
          "context_management": {
              "edits": [
                  {
                      "type": "clear_tool_uses_20250919",
                      "trigger": {
                          "type": "input_tokens",
                          "value": 30000
                      },
                      "keep": {
                          "type": "tool_uses",
                          "value": 3
                      },
                      "clear_at_least": {
                          "type": "input_tokens",
                          "value": 5000
                      },
                      "exclude_tools": ["web_search"]
                  }
              ]
          }
      }'

bash CLI
  ant beta:messages create --beta context-management-2025-06-27 <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Create a simple command line calculator app using Python
  tools:
    - type: text_editor_20250728
      name: str_replace_based_edit_tool
      max_characters: 10000
    - type: web_search_20250305
      name: web_search
      max_uses: 3
  context_management:
    edits:
      - type: clear_tool_uses_20250919
        trigger:
          type: input_tokens
          value: 30000
        keep:
          type: tool_uses
          value: 3
        clear_at_least:
          type: input_tokens
          value: 5000
        exclude_tools:
          - web_search
  YAML

python Python
  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": "Create a simple command line calculator app using Python",
          }
      ],
      tools=[
          {
              "type": "text_editor_20250728",
              "name": "str_replace_based_edit_tool",
              "max_characters": 10000,
          },
          {"type": "web_search_20250305", "name": "web_search", "max_uses": 3},
      ],
      betas=["context-management-2025-06-27"],
      context_management={
          "edits": [
              {
                  "type": "clear_tool_uses_20250919",
                  # Trigger clearing when threshold is exceeded
                  "trigger": {"type": "input_tokens", "value": 30000},
                  # Number of tool uses to keep after clearing
                  "keep": {"type": "tool_uses", "value": 3},
                  # Optional: Clear at least this many tokens
                  "clear_at_least": {"type": "input_tokens", "value": 5000},
                  # Exclude these tools from being cleared
                  "exclude_tools": ["web_search"],
              }
          ]
      },
  )

typescript TypeScript
  const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY
  });

  const response = await anthropic.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Create a simple command line calculator app using Python"
      }
    ],
    tools: [
      {
        type: "text_editor_20250728",
        name: "str_replace_based_edit_tool",
        max_characters: 10000
      },
      {
        type: "web_search_20250305",
        name: "web_search",
        max_uses: 3
      }
    ],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_tool_uses_20250919",
          // Trigger clearing when threshold is exceeded
          trigger: {
            type: "input_tokens",
            value: 30000
          },
          // Number of tool uses to keep after clearing
          keep: {
            type: "tool_uses",
            value: 3
          },
          // Optional: Clear at least this many tokens
          clear_at_least: {
            type: "input_tokens",
            value: 5000
          },
          // Exclude these tools from being cleared
          exclude_tools: ["web_search"]
        }
      ]
    }
  });

csharp C#
  using Anthropic;
  using Anthropic.Models.Beta;
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Messages::Model.ClaudeOpus5,
      MaxTokens = 4096,
      Messages = [
          new() { Role = Role.User, Content = "Create a simple command line calculator app using Python" }
      ],
      Tools = [
          new BetaToolTextEditor20250728 { MaxCharacters = 10000 },
          new BetaWebSearchTool20250305 { MaxUses = 3 }
      ],
      Betas = [AnthropicBeta.ContextManagement2025_06_27],
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [
              new BetaClearToolUses20250919Edit
              {
                  Trigger = new BetaInputTokensTrigger(30000),
                  Keep = new BetaToolUsesKeep(3),
                  ClearAtLeast = new BetaInputTokensClearAtLeast(5000),
                  ExcludeTools = ["web_search"]
              }
          ]
      }
  };

  var response = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Create a simple command line calculator app using Python")),
  	},
  	Tools: []anthropic.BetaToolUnionParam{
  		{OfTextEditor20250728: &anthropic.BetaToolTextEditor20250728Param{
  			MaxCharacters: anthropic.Int(10000),
  		}},
  		{OfWebSearchTool20250305: &anthropic.BetaWebSearchTool20250305Param{
  			MaxUses: anthropic.Int(3),
  		}},
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaContextManagement2025_06_27},
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfClearToolUses20250919: &anthropic.BetaClearToolUses20250919EditParam{
  				Trigger: anthropic.BetaClearToolUses20250919EditTriggerUnionParam{
  					OfInputTokens: &anthropic.BetaInputTokensTriggerParam{
  						Value: 30000,
  					},
  				},
  				Keep: anthropic.BetaToolUsesKeepParam{
  					Value: 3,
  				},
  				ClearAtLeast: anthropic.BetaInputTokensClearAtLeastParam{
  					Value: 5000,
  				},
  				ExcludeTools: []string{"web_search"},
  			}},
  		},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaToolTextEditor20250728;
  import com.anthropic.models.beta.messages.BetaWebSearchTool20250305;
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaClearToolUses20250919Edit;
  import com.anthropic.models.beta.messages.BetaInputTokensTrigger;
  import com.anthropic.models.beta.messages.BetaInputTokensClearAtLeast;
  import com.anthropic.models.beta.messages.BetaToolUsesKeep;
  import com.anthropic.models.beta.AnthropicBeta;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .addUserMessage("Create a simple command line calculator app using Python")
          .addTool(BetaToolTextEditor20250728.builder()
              .maxCharacters(10000L)
              .build())
          .addTool(BetaWebSearchTool20250305.builder()
              .maxUses(3L)
              .build())
          .addBeta(AnthropicBeta.CONTEXT_MANAGEMENT_2025_06_27)
          .contextManagement(BetaContextManagementConfig.builder()
              .addEdit(BetaClearToolUses20250919Edit.builder()
                  .trigger(BetaInputTokensTrigger.builder()
                      .value(30000L)
                      .build())
                  .keep(BetaToolUsesKeep.builder()
                      .value(3L)
                      .build())
                  .clearAtLeast(BetaInputTokensClearAtLeast.builder()
                      .value(5000L)
                      .build())
                  .addExcludeTool("web_search")
                  .build())
              .build())
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
              'content' => 'Create a simple command line calculator app using Python'
          ]
      ],
      model: 'claude-opus-5',
      betas: ['context-management-2025-06-27'],
      tools: [
          [
              'type' => 'text_editor_20250728',
              'name' => 'str_replace_based_edit_tool',
              'max_characters' => 10000
          ],
          [
              'type' => 'web_search_20250305',
              'name' => 'web_search',
              'max_uses' => 3
          ]
      ],
      contextManagement: [
          'edits' => [
              [
                  'type' => 'clear_tool_uses_20250919',
                  'trigger' => [
                      'type' => 'input_tokens',
                      'value' => 30000
                  ],
                  'keep' => [
                      'type' => 'tool_uses',
                      'value' => 3
                  ],
                  'clear_at_least' => [
                      'type' => 'input_tokens',
                      'value' => 5000
                  ],
                  'exclude_tools' => ['web_search']
              ]
          ]
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Create a simple command line calculator app using Python"
      }
    ],
    tools: [
      {
        type: "text_editor_20250728",
        name: "str_replace_based_edit_tool",
        max_characters: 10000
      },
      {
        type: "web_search_20250305",
        name: "web_search",
        max_uses: 3
      }
    ],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_tool_uses_20250919",
          trigger: {
            type: "input_tokens",
            value: 30000
          },
          keep: {
            type: "tool_uses",
            value: 3
          },
          clear_at_least: {
            type: "input_tokens",
            value: 5000
          },
          exclude_tools: ["web_search"]
        }
      ]
    }
  )
  puts response
  ```
</CodeGroup>


## Thinking block clearing usage

Source: https://platform.claude.com/llms-full.txt#thinking-block-clearing-usage

Enable thinking block clearing to manage context and prompt caching effectively when extended thinking is enabled:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --header "anthropic-beta: context-management-2025-06-27" \
      --data '{
          "model": "claude-opus-5",
          "max_tokens": 16000,
          "messages": [{"role": "user", "content": "Hello"}],
          "context_management": {
              "edits": [
                  {
                      "type": "clear_thinking_20251015",
                      "keep": {
                          "type": "thinking_turns",
                          "value": 2
                      }
                  }
              ]
          }
      }'

bash CLI
  ant beta:messages create --beta context-management-2025-06-27 <<'YAML'
  model: claude-opus-5
  max_tokens: 16000
  messages:
    - role: user
      content: Hello
  context_management:
    edits:
      - type: clear_thinking_20251015
        keep:
          type: thinking_turns
          value: 2
  YAML

python Python
  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=16000,
      messages=[{"role": "user", "content": "Hello"}],
      betas=["context-management-2025-06-27"],
      context_management={
          "edits": [
              {
                  "type": "clear_thinking_20251015",
                  "keep": {"type": "thinking_turns", "value": 2},
              }
          ]
      },
  )

typescript TypeScript
  const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY
  });

  const response = await anthropic.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 16000,
    messages: [{ role: "user", content: "Hello" }],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_thinking_20251015",
          keep: {
            type: "thinking_turns",
            value: 2
          }
        }
      ]
    }
  });

csharp C#
  using Anthropic;
  using Anthropic.Models.Beta;
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Messages::Model.ClaudeOpus5,
      MaxTokens = 16000,
      Messages = [
          new() { Role = Role.User, Content = "Hello" }
      ],
      Betas = [AnthropicBeta.ContextManagement2025_06_27],
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [
              new BetaClearThinking20251015Edit
              {
                  Keep = new BetaThinkingTurns(2)
              }
          ]
      }
  };

  var response = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 16000,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello")),
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaContextManagement2025_06_27},
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfClearThinking20251015: &anthropic.BetaClearThinking20251015EditParam{
  				Keep: anthropic.BetaClearThinking20251015EditKeepUnionParam{
  					OfThinkingTurns: &anthropic.BetaThinkingTurnsParam{
  						Value: 2,
  					},
  				},
  			}},
  		},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaClearThinking20251015Edit;
  import com.anthropic.models.beta.messages.BetaThinkingTurns;
  import com.anthropic.models.beta.AnthropicBeta;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(16000L)
          .addUserMessage("Hello")
          .addBeta(AnthropicBeta.CONTEXT_MANAGEMENT_2025_06_27)
          .contextManagement(BetaContextManagementConfig.builder()
              .addEdit(BetaClearThinking20251015Edit.builder()
                  .keep(BetaThinkingTurns.builder()
                      .value(2L)
                      .build())
                  .build())
              .build())
          .build();

      BetaMessage response = client.beta().messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      maxTokens: 16000,
      messages: [
          ['role' => 'user', 'content' => 'Hello']
      ],
      model: 'claude-opus-5',
      betas: ['context-management-2025-06-27'],
      contextManagement: [
          'edits' => [
              [
                  'type' => 'clear_thinking_20251015',
                  'keep' => [
                      'type' => 'thinking_turns',
                      'value' => 2
                  ]
              ]
          ]
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 16000,
    messages: [{ role: "user", content: "Hello" }],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_thinking_20251015",
          keep: {
            type: "thinking_turns",
            value: 2
          }
        }
      ]
    }
  )
  puts response

bash cURL
  curl https://api.anthropic.com/v1/messages \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --header "anthropic-beta: context-management-2025-06-27" \
      --data '{
          "model": "claude-opus-5",
          "max_tokens": 16000,
          "messages": [{"role": "user", "content": "Hello"}],
          "context_management": {
              "edits": [
                  {
                      "type": "clear_thinking_20251015",
                      "keep": {
                          "type": "thinking_turns",
                          "value": 3
                      }
                  }
              ]
          }
      }'

bash CLI
  ant beta:messages create --beta context-management-2025-06-27 <<'YAML'
  model: claude-opus-5
  max_tokens: 16000
  messages:
    - role: user
      content: Hello
  context_management:
    edits:
      - type: clear_thinking_20251015
        keep:
          type: thinking_turns
          value: 3
  YAML

python Python
  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=16000,
      messages=[{"role": "user", "content": "Hello"}],
      betas=["context-management-2025-06-27"],
      context_management={
          "edits": [
              {
                  "type": "clear_thinking_20251015",
                  "keep": {"type": "thinking_turns", "value": 3},
              }
          ]
      },
  )

typescript TypeScript
  const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY
  });

  const response = await anthropic.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 16000,
    messages: [{ role: "user", content: "Hello" }],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_thinking_20251015",
          keep: {
            type: "thinking_turns",
            value: 3
          }
        }
      ]
    }
  });

csharp C#
  using Anthropic;
  using Anthropic.Models.Beta;
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Messages::Model.ClaudeOpus5,
      MaxTokens = 16000,
      Messages = [
          new() { Role = Role.User, Content = "Hello" }
      ],
      Betas = [AnthropicBeta.ContextManagement2025_06_27],
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [
              new BetaClearThinking20251015Edit
              {
                  Keep = new BetaThinkingTurns(3)
              }
          ]
      }
  };

  var response = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 16000,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello")),
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaContextManagement2025_06_27},
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfClearThinking20251015: &anthropic.BetaClearThinking20251015EditParam{
  				Keep: anthropic.BetaClearThinking20251015EditKeepUnionParam{
  					OfThinkingTurns: &anthropic.BetaThinkingTurnsParam{
  						Value: 3,
  					},
  				},
  			}},
  		},
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
      .maxTokens(16000L)
      .addUserMessage("Hello")
      .addBeta(AnthropicBeta.CONTEXT_MANAGEMENT_2025_06_27)
      .contextManagement(BetaContextManagementConfig.builder()
          .addEdit(BetaClearThinking20251015Edit.builder()
              .keep(BetaThinkingTurns.builder()
                  .value(3L)
                  .build())
              .build())
          .build())
      .build();

  BetaMessage response = client.beta().messages().create(params);
  IO.println(response);

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      maxTokens: 16000,
      messages: [
          ['role' => 'user', 'content' => 'Hello']
      ],
      model: 'claude-opus-5',
      betas: ['context-management-2025-06-27'],
      contextManagement: [
          'edits' => [
              [
                  'type' => 'clear_thinking_20251015',
                  'keep' => [
                      'type' => 'thinking_turns',
                      'value' => 3
                  ]
              ]
          ]
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 16000,
    messages: [{ role: "user", content: "Hello" }],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_thinking_20251015",
          keep: {
            type: "thinking_turns",
            value: 3
          }
        }
      ]
    }
  )
  puts response

bash cURL
  curl https://api.anthropic.com/v1/messages \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --header "anthropic-beta: context-management-2025-06-27" \
      --data '{
          "model": "claude-opus-5",
          "max_tokens": 16000,
          "messages": [{"role": "user", "content": "Hello"}],
          "context_management": {
              "edits": [
                  {
                      "type": "clear_thinking_20251015",
                      "keep": "all"
                  }
              ]
          }
      }'

bash CLI
  ant beta:messages create --beta context-management-2025-06-27 <<'YAML'
  model: claude-opus-5
  max_tokens: 16000
  messages:
    - role: user
      content: Hello
  context_management:
    edits:
      - type: clear_thinking_20251015
        keep: all
  YAML

python Python
  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=16000,
      messages=[{"role": "user", "content": "Hello"}],
      betas=["context-management-2025-06-27"],
      context_management={
          "edits": [
              {
                  "type": "clear_thinking_20251015",
                  "keep": "all",
              }
          ]
      },
  )

typescript TypeScript
  const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY
  });

  const response = await anthropic.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 16000,
    messages: [{ role: "user", content: "Hello" }],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_thinking_20251015",
          keep: "all"
        }
      ]
    }
  });

csharp C#
  using Anthropic;
  using Anthropic.Models.Beta;
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Messages::Model.ClaudeOpus5,
      MaxTokens = 16000,
      Messages = [
          new() { Role = Role.User, Content = "Hello" }
      ],
      Betas = [AnthropicBeta.ContextManagement2025_06_27],
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [
              new BetaClearThinking20251015Edit
              {
                  Keep = new All()
              }
          ]
      }
  };

  var response = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 16000,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello")),
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaContextManagement2025_06_27},
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfClearThinking20251015: &anthropic.BetaClearThinking20251015EditParam{
  				Keep: anthropic.BetaClearThinking20251015EditKeepUnionParam{
  					OfAll: constant.ValueOf[constant.All](),
  				},
  			}},
  		},
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
      .maxTokens(16000L)
      .addUserMessage("Hello")
      .addBeta(AnthropicBeta.CONTEXT_MANAGEMENT_2025_06_27)
      .contextManagement(BetaContextManagementConfig.builder()
          .addEdit(BetaClearThinking20251015Edit.builder()
              .keepAll()
              .build())
          .build())
      .build();

  BetaMessage response = client.beta().messages().create(params);
  IO.println(response);

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      maxTokens: 16000,
      messages: [
          ['role' => 'user', 'content' => 'Hello']
      ],
      model: 'claude-opus-5',
      betas: ['context-management-2025-06-27'],
      contextManagement: [
          'edits' => [
              [
                  'type' => 'clear_thinking_20251015',
                  'keep' => 'all'
              ]
          ]
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 16000,
    messages: [{ role: "user", content: "Hello" }],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_thinking_20251015",
          keep: "all"
        }
      ]
    }
  )
  puts response

bash cURL
  curl https://api.anthropic.com/v1/messages \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --header "anthropic-beta: context-management-2025-06-27" \
      --data '{
          "model": "claude-opus-5",
          "max_tokens": 16000,
          "messages": [
              {
                  "role": "user",
                  "content": "Search for the latest developments in quantum error correction and summarize the key breakthroughs."
              }
          ],
          "tools": [
              {
                  "type": "web_search_20250305",
                  "name": "web_search",
                  "max_uses": 5
              }
          ],
          "context_management": {
              "edits": [
                  {
                      "type": "clear_thinking_20251015",
                      "keep": {
                          "type": "thinking_turns",
                          "value": 2
                      }
                  },
                  {
                      "type": "clear_tool_uses_20250919",
                      "trigger": {
                          "type": "input_tokens",
                          "value": 50000
                      },
                      "keep": {
                          "type": "tool_uses",
                          "value": 5
                      }
                  }
              ]
          }
      }'

bash CLI
  ant beta:messages create --beta context-management-2025-06-27 <<'YAML'
  model: claude-opus-5
  max_tokens: 16000
  messages:
    - role: user
      content: Search for the latest developments in quantum error correction and summarize the key breakthroughs.
  tools:
    - type: web_search_20250305
      name: web_search
      max_uses: 5
  context_management:
    edits:
      - type: clear_thinking_20251015
        keep:
          type: thinking_turns
          value: 2
      - type: clear_tool_uses_20250919
        trigger:
          type: input_tokens
          value: 50000
        keep:
          type: tool_uses
          value: 5
  YAML

python Python
  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=16000,
      messages=[
          {
              "role": "user",
              "content": "Search for the latest developments in quantum error correction and summarize the key breakthroughs.",
          }
      ],
      tools=[
          {
              "type": "web_search_20250305",
              "name": "web_search",
              "max_uses": 5,
          }
      ],
      betas=["context-management-2025-06-27"],
      context_management={
          "edits": [
              {
                  "type": "clear_thinking_20251015",
                  "keep": {"type": "thinking_turns", "value": 2},
              },
              {
                  "type": "clear_tool_uses_20250919",
                  "trigger": {"type": "input_tokens", "value": 50000},
                  "keep": {"type": "tool_uses", "value": 5},
              },
          ]
      },
  )

  print(response)

typescript TypeScript
  const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY
  });

  const response = await anthropic.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 16000,
    messages: [
      {
        role: "user",
        content:
          "Search for the latest developments in quantum error correction and summarize the key breakthroughs."
      }
    ],
    tools: [
      {
        type: "web_search_20250305",
        name: "web_search",
        max_uses: 5
      }
    ],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_thinking_20251015",
          keep: {
            type: "thinking_turns",
            value: 2
          }
        },
        {
          type: "clear_tool_uses_20250919",
          trigger: {
            type: "input_tokens",
            value: 50000
          },
          keep: {
            type: "tool_uses",
            value: 5
          }
        }
      ]
    }
  });

  console.log(response);

csharp C#
  using Anthropic;
  using Anthropic.Models.Beta;
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Messages::Model.ClaudeOpus5,
      MaxTokens = 16000,
      Messages = [
          new() { Role = Role.User, Content = "Search for the latest developments in quantum error correction and summarize the key breakthroughs." }
      ],
      Tools = [
          new BetaWebSearchTool20250305 { MaxUses = 5 }
      ],
      Betas = [AnthropicBeta.ContextManagement2025_06_27],
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [
              new BetaClearThinking20251015Edit
              {
                  Keep = new BetaThinkingTurns(2)
              },
              new BetaClearToolUses20250919Edit
              {
                  Trigger = new BetaInputTokensTrigger(50000),
                  Keep = new BetaToolUsesKeep(5)
              }
          ]
      }
  };

  var response = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 16000,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Search for the latest developments in quantum error correction and summarize the key breakthroughs.")),
  	},
  	Tools: []anthropic.BetaToolUnionParam{
  		{OfWebSearchTool20250305: &anthropic.BetaWebSearchTool20250305Param{
  			MaxUses: anthropic.Int(5),
  		}},
  	},
  	Betas: []anthropic.AnthropicBeta{
  		anthropic.AnthropicBetaContextManagement2025_06_27,
  	},
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfClearThinking20251015: &anthropic.BetaClearThinking20251015EditParam{
  				Keep: anthropic.BetaClearThinking20251015EditKeepUnionParam{
  					OfThinkingTurns: &anthropic.BetaThinkingTurnsParam{
  						Value: 2,
  					},
  				},
  			}},
  			{OfClearToolUses20250919: &anthropic.BetaClearToolUses20250919EditParam{
  				Trigger: anthropic.BetaClearToolUses20250919EditTriggerUnionParam{
  					OfInputTokens: &anthropic.BetaInputTokensTriggerParam{
  						Value: 50000,
  					},
  				},
  				Keep: anthropic.BetaToolUsesKeepParam{
  					Value: 5,
  				},
  			}},
  		},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaWebSearchTool20250305;
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaClearThinking20251015Edit;
  import com.anthropic.models.beta.messages.BetaClearToolUses20250919Edit;
  import com.anthropic.models.beta.messages.BetaThinkingTurns;
  import com.anthropic.models.beta.messages.BetaInputTokensTrigger;
  import com.anthropic.models.beta.messages.BetaToolUsesKeep;
  import com.anthropic.models.beta.AnthropicBeta;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(16000L)
          .addUserMessage("Search for the latest developments in quantum error correction and summarize the key breakthroughs.")
          .addTool(BetaWebSearchTool20250305.builder()
              .maxUses(5L)
              .build())
          .addBeta(AnthropicBeta.CONTEXT_MANAGEMENT_2025_06_27)
          .contextManagement(BetaContextManagementConfig.builder()
              .addEdit(BetaClearThinking20251015Edit.builder()
                  .keep(BetaThinkingTurns.builder()
                      .value(2L)
                      .build())
                  .build())
              .addEdit(BetaClearToolUses20250919Edit.builder()
                  .trigger(BetaInputTokensTrigger.builder()
                      .value(50000L)
                      .build())
                  .keep(BetaToolUsesKeep.builder()
                      .value(5L)
                      .build())
                  .build())
              .build())
          .build();

      BetaMessage response = client.beta().messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      maxTokens: 16000,
      messages: [
          [
              'role' => 'user',
              'content' => 'Search for the latest developments in quantum error correction and summarize the key breakthroughs.'
          ]
      ],
      model: 'claude-opus-5',
      betas: ['context-management-2025-06-27'],
      tools: [
          [
              'type' => 'web_search_20250305',
              'name' => 'web_search',
              'max_uses' => 5
          ]
      ],
      contextManagement: [
          'edits' => [
              [
                  'type' => 'clear_thinking_20251015',
                  'keep' => [
                      'type' => 'thinking_turns',
                      'value' => 2
                  ]
              ],
              [
                  'type' => 'clear_tool_uses_20250919',
                  'trigger' => [
                      'type' => 'input_tokens',
                      'value' => 50000
                  ],
                  'keep' => [
                      'type' => 'tool_uses',
                      'value' => 5
                  ]
              ]
          ]
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 16000,
    messages: [
      {
        role: "user",
        content: "Search for the latest developments in quantum error correction and summarize the key breakthroughs."
      }
    ],
    tools: [
      {
        type: "web_search_20250305",
        name: "web_search",
        max_uses: 5
      }
    ],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_thinking_20251015",
          keep: {
            type: "thinking_turns",
            value: 2
          }
        },
        {
          type: "clear_tool_uses_20250919",
          trigger: {
            type: "input_tokens",
            value: 50000
          },
          keep: {
            type: "tool_uses",
            value: 5
          }
        }
      ]
    }
  )
  puts response
  ```
</CodeGroup>


## Configuration options for tool result clearing

Source: https://platform.claude.com/llms-full.txt#configuration-options-for-tool-result-clearing

| Configuration option | Default              | Description                                                                                                                                                                                                                                           |
| -------------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `trigger`            | 100,000 input tokens | Defines when the context editing strategy activates. Once the prompt exceeds this threshold, clearing begins. You can specify this value in either `input_tokens` or `tool_uses`.                                                                     |
| `keep`               | 3 tool uses          | Defines how many recent tool use/result pairs to keep after clearing occurs. The API removes the oldest tool interactions first, preserving the most recent ones.                                                                                     |
| `clear_at_least`     | None                 | Ensures a minimum number of tokens is cleared each time the strategy activates. If the API can't clear at least the specified amount, the strategy will not be applied. This helps determine if context clearing is worth breaking your prompt cache. |
| `exclude_tools`      | None                 | List of tool names whose tool uses and results should never be cleared. Useful for preserving important context.                                                                                                                                      |
| `clear_tool_inputs`  | `false`              | Controls whether the tool call parameters are cleared along with the tool results. By default, only the tool results are cleared while keeping Claude's original tool calls visible.                                                                  |


## Context editing response

Source: https://platform.claude.com/llms-full.txt#context-editing-response

You can see which context edits were applied to your request using the `context_management` response field, along with helpful statistics about the content and input tokens cleared.

```json Output
{
  "id": "msg_013Zva2CMHLNnXjNJJKqJ2EF",
  "type": "message",
  "role": "assistant",
  "content": [
    // ...
  ],
  "usage": {
    // ...
  },
  "context_management": {
    "applied_edits": [
      // When using `clear_thinking_20251015`
      {
        "type": "clear_thinking_20251015",
        "cleared_thinking_turns": 3,
        "cleared_input_tokens": 15000
      },
      // When using `clear_tool_uses_20250919`
      {
        "type": "clear_tool_uses_20250919",
        "cleared_tool_uses": 8,
        "cleared_input_tokens": 50000
      }
    ]
  }
}

json Streaming Response
{
  "type": "message_delta",
  "delta": {
    "stop_reason": "end_turn",
    "stop_sequence": null
  },
  "usage": {
    "output_tokens": 1024
  },
  "context_management": {
    "applied_edits": [
      // ...
    ]
  }
}
```


## Token counting

Source: https://platform.claude.com/llms-full.txt#token-counting

The [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) endpoint supports context management, allowing you to preview how many tokens your prompt will use after context editing is applied.

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages/count_tokens \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --header "anthropic-beta: context-management-2025-06-27" \
      --data '{
          "model": "claude-opus-5",
          "messages": [
              {
                  "role": "user",
                  "content": "Continue our conversation..."
              }
          ],
          "context_management": {
              "edits": [
                  {
                      "type": "clear_tool_uses_20250919",
                      "trigger": {
                          "type": "input_tokens",
                          "value": 30000
                      },
                      "keep": {
                          "type": "tool_uses",
                          "value": 5
                      }
                  }
              ]
          }
      }'

bash CLI
  cat > request.yaml <<'YAML'
  model: claude-opus-5
  messages:
    - role: user
      content: Continue our conversation...
  context_management:
    edits:
      - type: clear_tool_uses_20250919
        trigger:
          type: input_tokens
          value: 30000
        keep:
          type: tool_uses
          value: 5
  YAML

  ORIGINAL=$(ant beta:messages count-tokens \
    --beta context-management-2025-06-27 \
    --transform context_management.original_input_tokens \
    --raw-output < request.yaml)

  INPUT_TOKENS=$(ant beta:messages count-tokens \
    --beta context-management-2025-06-27 \
    --transform input_tokens --raw-output < request.yaml)

  printf 'Original tokens: %s\n' "$ORIGINAL"
  printf 'After clearing: %s\n' "$INPUT_TOKENS"
  printf 'Savings: %s tokens\n' "$((ORIGINAL - INPUT_TOKENS))"

python Python
  response = client.beta.messages.count_tokens(
      model="claude-opus-5",
      messages=[{"role": "user", "content": "Continue our conversation..."}],
      betas=["context-management-2025-06-27"],
      context_management={
          "edits": [
              {
                  "type": "clear_tool_uses_20250919",
                  "trigger": {"type": "input_tokens", "value": 30000},
                  "keep": {"type": "tool_uses", "value": 5},
              }
          ]
      },
  )

  print(f"Original tokens: {response.context_management.original_input_tokens}")
  print(f"After clearing: {response.input_tokens}")
  print(
      f"Savings: {response.context_management.original_input_tokens - response.input_tokens} tokens"
  )

typescript TypeScript
  const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY
  });

  const response = await anthropic.beta.messages.countTokens({
    model: "claude-opus-5",
    messages: [
      {
        role: "user",
        content: "Continue our conversation..."
      }
    ],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_tool_uses_20250919",
          trigger: {
            type: "input_tokens",
            value: 30000
          },
          keep: {
            type: "tool_uses",
            value: 5
          }
        }
      ]
    }
  });

  console.log(`Original tokens: ${response.context_management?.original_input_tokens}`);
  console.log(`After clearing: ${response.input_tokens}`);
  console.log(
    `Savings: ${
      (response.context_management?.original_input_tokens || 0) - response.input_tokens
    } tokens`
  );

csharp C#
  using Anthropic;
  using Anthropic.Models.Beta;
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCountTokensParams
  {
      Model = Messages::Model.ClaudeOpus5,
      Messages = [new() { Role = Role.User, Content = "Continue our conversation..." }],
      Betas = [AnthropicBeta.ContextManagement2025_06_27],
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [
              new BetaClearToolUses20250919Edit
              {
                  Trigger = new BetaInputTokensTrigger(30000),
                  Keep = new BetaToolUsesKeep(5)
              }
          ]
      }
  };

  var response = await client.Beta.Messages.CountTokens(parameters);

  Console.WriteLine($"Original tokens: {response.ContextManagement?.OriginalInputTokens}");
  Console.WriteLine($"After clearing: {response.InputTokens}");
  Console.WriteLine($"Savings: {(response.ContextManagement?.OriginalInputTokens ?? 0) - response.InputTokens} tokens");

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.CountTokens(context.TODO(), anthropic.BetaMessageCountTokensParams{
  	Model: anthropic.ModelClaudeOpus5,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Continue our conversation...")),
  	},
  	Betas: []anthropic.AnthropicBeta{
  		anthropic.AnthropicBetaContextManagement2025_06_27,
  	},
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfClearToolUses20250919: &anthropic.BetaClearToolUses20250919EditParam{
  				Trigger: anthropic.BetaClearToolUses20250919EditTriggerUnionParam{
  					OfInputTokens: &anthropic.BetaInputTokensTriggerParam{
  						Value: 30000,
  					},
  				},
  				Keep: anthropic.BetaToolUsesKeepParam{
  					Value: 5,
  				},
  			}},
  		},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Printf("Original tokens: %d\n", response.ContextManagement.OriginalInputTokens)
  fmt.Printf("After clearing: %d\n", response.InputTokens)
  fmt.Printf("Savings: %d tokens\n", response.ContextManagement.OriginalInputTokens-response.InputTokens)

java Java
  import com.anthropic.models.beta.messages.BetaMessageTokensCount;
  import com.anthropic.models.beta.messages.MessageCountTokensParams;
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaClearToolUses20250919Edit;
  import com.anthropic.models.beta.messages.BetaInputTokensTrigger;
  import com.anthropic.models.beta.messages.BetaToolUsesKeep;
  import com.anthropic.models.beta.AnthropicBeta;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCountTokensParams params = MessageCountTokensParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .addUserMessage("Continue our conversation...")
          .addBeta(AnthropicBeta.CONTEXT_MANAGEMENT_2025_06_27)
          .contextManagement(BetaContextManagementConfig.builder()
              .addEdit(BetaClearToolUses20250919Edit.builder()
                  .trigger(BetaInputTokensTrigger.builder()
                      .value(30000L)
                      .build())
                  .keep(BetaToolUsesKeep.builder()
                      .value(5L)
                      .build())
                  .build())
              .build())
          .build();

      BetaMessageTokensCount response = client.beta().messages().countTokens(params);

      IO.println("Original tokens: " + response.contextManagement().get().originalInputTokens());
      IO.println("After clearing: " + response.inputTokens());
      IO.println("Savings: " + (response.contextManagement().get().originalInputTokens() - response.inputTokens()) + " tokens");
  }

php PHP
  $client = new Client();

  $response = $client->beta->messages->countTokens(
      messages: [
          ['role' => 'user', 'content' => 'Continue our conversation...']
      ],
      model: 'claude-opus-5',
      betas: ['context-management-2025-06-27'],
      contextManagement: [
          'edits' => [
              [
                  'type' => 'clear_tool_uses_20250919',
                  'trigger' => [
                      'type' => 'input_tokens',
                      'value' => 30000
                  ],
                  'keep' => [
                      'type' => 'tool_uses',
                      'value' => 5
                  ]
              ]
          ]
      ],
  );

  echo "Original tokens: " . $response->contextManagement->originalInputTokens . "\n";
  echo "After clearing: " . $response->inputTokens . "\n";
  echo "Savings: " . ($response->contextManagement->originalInputTokens - $response->inputTokens) . " tokens\n";

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.count_tokens(
    model: "claude-opus-5",
    messages: [
      { role: "user", content: "Continue our conversation..." }
    ],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        {
          type: "clear_tool_uses_20250919",
          trigger: {
            type: "input_tokens",
            value: 30000
          },
          keep: {
            type: "tool_uses",
            value: 5
          }
        }
      ]
    }
  )

  puts "Original tokens: #{response.context_management.original_input_tokens}"
  puts "After clearing: #{response.input_tokens}"
  puts "Savings: #{response.context_management.original_input_tokens - response.input_tokens} tokens"

json Output
{
  "input_tokens": 25000,
  "context_management": {
    "original_input_tokens": 70000
  }
}
```

The response shows both the final token count after context management is applied (`input_tokens`) and the original token count before any clearing occurred (`original_input_tokens`).


## Using with the memory tool

Source: https://platform.claude.com/llms-full.txt#using-with-the-memory-tool

Context editing can be combined with the [memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool). When your conversation context approaches the configured clearing threshold, Claude receives an automatic warning to preserve important information. This enables Claude to save tool results or context to its memory files before they're cleared from the conversation history.

This combination allows you to:

* **Preserve important context:** Claude can write essential information from tool results to memory files before those results are cleared
* **Maintain long-running workflows:** Enable agentic workflows that would otherwise exceed context limits by offloading information to persistent storage
* **Access information on demand:** Claude can look up previously cleared information from memory files when needed, rather than keeping everything in the active context window

For example, in a file editing workflow where Claude performs many operations, Claude can summarize completed changes to memory files as the context grows. When tool results are cleared, Claude retains access to that information through its memory system and can continue working effectively.

To use both features together, enable them in your API request:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --header "anthropic-beta: context-management-2025-06-27" \
      --data '{
          "model": "claude-opus-5",
          "max_tokens": 4096,
          "messages": [
              {
                  "role": "user",
                  "content": "Hello"
              }
          ],
          "tools": [
              {
                  "type": "memory_20250818",
                  "name": "memory"
              }
          ],
          "context_management": {
              "edits": [
                  {"type": "clear_tool_uses_20250919"}
              ]
          }
      }'

bash CLI
  ant beta:messages create --beta context-management-2025-06-27 <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  messages:
    - role: user
      content: Hello
  tools:
    - type: memory_20250818
      name: memory
  context_management:
    edits:
      - type: clear_tool_uses_20250919
  YAML

python Python
  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      messages=[{"role": "user", "content": "Hello"}],
      tools=[{"type": "memory_20250818", "name": "memory"}],
      betas=["context-management-2025-06-27"],
      context_management={"edits": [{"type": "clear_tool_uses_20250919"}]},
  )

typescript TypeScript
  const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY
  });

  const response = await anthropic.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [{ role: "user", content: "Hello" }],
    tools: [
      {
        type: "memory_20250818",
        name: "memory"
      }
    ],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [{ type: "clear_tool_uses_20250919" }]
    }
  });

csharp C#
  using Anthropic;
  using Anthropic.Models.Beta;
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Messages::Model.ClaudeOpus5,
      MaxTokens = 4096,
      Messages = [
          new() { Role = Role.User, Content = "Hello" }
      ],
      Tools = [
          new BetaMemoryTool20250818()
      ],
      Betas = [AnthropicBeta.ContextManagement2025_06_27],
      ContextManagement = new BetaContextManagementConfig
      {
          Edits = [new BetaClearToolUses20250919Edit()]
      }
  };

  var response = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello")),
  	},
  	Tools: []anthropic.BetaToolUnionParam{
  		{OfMemoryTool20250818: &anthropic.BetaMemoryTool20250818Param{}},
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaContextManagement2025_06_27},
  	ContextManagement: anthropic.BetaContextManagementConfigParam{
  		Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
  			{OfClearToolUses20250919: &anthropic.BetaClearToolUses20250919EditParam{}},
  		},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaMemoryTool20250818;
  import com.anthropic.models.beta.messages.BetaContextManagementConfig;
  import com.anthropic.models.beta.messages.BetaClearToolUses20250919Edit;
  import com.anthropic.models.beta.AnthropicBeta;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .addUserMessage("Hello")
          .addTool(BetaMemoryTool20250818.builder().build())
          .addBeta(AnthropicBeta.CONTEXT_MANAGEMENT_2025_06_27)
          .contextManagement(BetaContextManagementConfig.builder()
              .addEdit(BetaClearToolUses20250919Edit.builder().build())
              .build())
          .build();

      BetaMessage response = client.beta().messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Hello']
      ],
      model: 'claude-opus-5',
      betas: ['context-management-2025-06-27'],
      tools: [
          [
              'type' => 'memory_20250818',
              'name' => 'memory'
          ]
      ],
      contextManagement: [
          'edits' => [
              ['type' => 'clear_tool_uses_20250919']
          ]
      ],
  );

  echo $response;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    messages: [{ role: "user", content: "Hello" }],
    tools: [
      {
        type: "memory_20250818",
        name: "memory"
      }
    ],
    betas: ["context-management-2025-06-27"],
    context_management: {
      edits: [
        { type: "clear_tool_uses_20250919" }
      ]
    }
  )
  puts response
  ```
</CodeGroup>

For the full memory tool reference including commands and examples, see [Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool).
