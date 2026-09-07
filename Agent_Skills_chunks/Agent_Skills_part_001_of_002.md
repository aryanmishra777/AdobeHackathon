# agentskills.io Documentation (Part 1 of 2)

## How to add skills support to your agent

Source: https://agentskills.io/llms-full.txt#how-to-add-skills-support-to-your-agent

Source: https://agentskills.io/client-implementation/adding-skills-support

A guide for adding Agent Skills support to an AI agent or development tool.

This guide walks through how to add Agent Skills support to an AI agent or development tool. It covers the full lifecycle: discovering skills, telling the model about them, loading their content into context, and keeping that content effective over time.

The core integration is the same regardless of your agent's architecture. The implementation details vary based on two factors:

* **Where do skills live?** A locally-running agent can scan the user's filesystem for skill directories. A cloud-hosted or sandboxed agent will need an alternative discovery mechanism — an API, a remote registry, or bundled assets.
* **How does the model access skill content?** If the model has file-reading capabilities, it can read `SKILL.md` files directly. Otherwise, you'll provide a dedicated tool or inject skill content into the prompt programmatically.

The guide notes where these differences matter. You don't need to support every scenario — follow the path that fits your agent.

**Prerequisites**: Familiarity with the [Agent Skills specification](/specification), which defines the `SKILL.md` file format, frontmatter fields, and directory conventions.


## The core principle: progressive disclosure

Source: https://agentskills.io/llms-full.txt#the-core-principle-progressive-disclosure

Every skills-compatible agent follows the same three-tier loading strategy:

| Tier            | What's loaded               | When                                 | Token cost                  |
| --------------- | --------------------------- | ------------------------------------ | --------------------------- |
| 1. Catalog      | Name + description          | Session start                        | \~50-100 tokens per skill   |
| 2. Instructions | Full `SKILL.md` body        | When the skill is activated          | \<5000 tokens (recommended) |
| 3. Resources    | Scripts, references, assets | When the instructions reference them | Varies                      |

The model sees the catalog from the start, so it knows what skills are available. When it decides a skill is relevant, it loads the full instructions. If those instructions reference supporting files, the model loads them individually as needed.

This keeps the base context small while giving the model access to specialized knowledge on demand. An agent with 20 installed skills doesn't pay the token cost of 20 full instruction sets upfront — only the ones actually used in a given conversation.


## Step 1: Discover skills

Source: https://agentskills.io/llms-full.txt#step-1-discover-skills

At session startup, find all available skills and load their metadata.

### Where to scan

Which directories you scan depends on your agent's environment. Most locally-running agents scan at least two scopes:

* **Project-level** (relative to the working directory): Skills specific to a project or repository.
* **User-level** (relative to the home directory): Skills available across all projects for a given user.

Other scopes are possible too — for example, organization-wide skills deployed by an admin, or skills bundled with the agent itself. The right set of scopes depends on your agent's deployment model.

Within each scope, consider scanning both a **client-specific directory** and the **`.agents/skills/` convention**:

| Scope   | Path                               | Purpose                       |
| ------- | ---------------------------------- | ----------------------------- |
| Project | `<project>/.<your-client>/skills/` | Your client's native location |
| Project | `<project>/.agents/skills/`        | Cross-client interoperability |
| User    | `~/.<your-client>/skills/`         | Your client's native location |
| User    | `~/.agents/skills/`                | Cross-client interoperability |

The `.agents/skills/` paths have emerged as a widely-adopted convention for cross-client skill sharing. While the Agent Skills specification does not mandate where skill directories live (it only defines what goes inside them), scanning `.agents/skills/` means skills installed by other compliant clients are automatically visible to yours, and vice versa.

<Note>
  Some implementations also scan `.claude/skills/` (both project-level and user-level) for pragmatic compatibility, since many existing skills are installed there. Other additional locations include ancestor directories up to the git root (useful for monorepos), [XDG](https://specifications.freedesktop.org/basedir-spec/latest/) config directories, and user-configured paths.
</Note>

### What to scan for

Within each skills directory, look for **subdirectories containing a file named exactly `SKILL.md`**:

Practical scanning rules:

* Skip directories that won't contain skills, such as `.git/` and `node_modules/`
* Optionally respect `.gitignore` to avoid scanning build artifacts
* Set reasonable bounds (e.g., max depth of 4-6 levels, max 2000 directories) to prevent runaway scanning in large directory trees

### Handling name collisions

When two skills share the same `name`, apply a deterministic precedence rule.

The universal convention across existing implementations: **project-level skills override user-level skills.**

Within the same scope (e.g., two skills named `code-review` found under both `<project>/.agents/skills/` and `<project>/.<your-client>/skills/`), either first-found or last-found is acceptable — pick one and be consistent. Log a warning when a collision occurs so the user knows a skill was shadowed.

### Trust considerations

Project-level skills come from the repository being worked on, which may be untrusted (e.g., a freshly cloned open-source project). Consider gating project-level skill loading on a trust check — only load them if the user has marked the project folder as trusted. This prevents untrusted repositories from silently injecting instructions into the agent's context.

### Cloud-hosted and sandboxed agents

If your agent runs in a container or on a remote server, it won't have access to the user's local filesystem. Discovery needs to work differently depending on the skill scope:

* **Project-level skills** are often the easiest case. If the agent operates on a cloned repository (even inside a sandbox), project-level skills travel with the code and can be scanned from the repo's directory tree.
* **User-level and organization-level skills** don't exist in the sandbox. You'll need to provision them from an external source — for example, cloning a configuration repository, accepting skill URLs or packages through your agent's settings, or letting users upload skill directories through a web UI.
* **Built-in skills** can be packaged as static assets within the agent's deployment artifact, making them available in every session without external fetching.

Once skills are available to the agent, the rest of the lifecycle — parsing, disclosure, activation — works the same.


## Step 2: Parse `SKILL.md` files

Source: https://agentskills.io/llms-full.txt#step-2-parse-skill-md-files

For each discovered `SKILL.md`, extract the metadata and body content.

### Frontmatter extraction

A `SKILL.md` file has two parts: YAML frontmatter between `---` delimiters, and a markdown body after the closing delimiter. To parse:

1. Find the opening `---` at the start of the file and the closing `---` after it.
2. Parse the YAML block between them. Extract `name` and `description` (required), plus any optional fields.
3. Everything after the closing `---`, trimmed, is the skill's body content.

See the [specification](/specification) for the full set of frontmatter fields and their constraints.

### Handling malformed YAML

Skill files authored for other clients may contain technically invalid YAML that their parsers happen to accept. The most common issue is unquoted values containing colons:

```yaml theme={null}
# Technically invalid YAML — the colon breaks parsing
description: Use this skill when: the user asks about PDFs
```

Consider a fallback that wraps such values in quotes or converts them to YAML block scalars before retrying. This improves cross-client compatibility at minimal cost.

### Lenient validation

Warn on issues but still load the skill when possible:

* Name doesn't match the parent directory name → warn, load anyway
* Name exceeds 64 characters → warn, load anyway
* Description is missing or empty → skip the skill (a description is essential for disclosure), log the error
* YAML is completely unparseable → skip the skill, log the error

Record diagnostics so they can be surfaced to the user (in a debug command, log file, or UI), but don't block skill loading on cosmetic issues.

<Note>
  The [specification](/specification) defines strict constraints on the `name` field (matching the parent directory, character set, max length). The lenient approach above deliberately relaxes these to improve compatibility with skills authored for other clients.
</Note>

### What to store

At minimum, each skill record needs three fields:

| Field         | Description                          |
| ------------- | ------------------------------------ |
| `name`        | From frontmatter                     |
| `description` | From frontmatter                     |
| `location`    | Absolute path to the `SKILL.md` file |

Store these in an in-memory map keyed by `name` for fast lookup during activation.

You can also store the **body** (the markdown content after the frontmatter) at discovery time, or read it from `location` at activation time. Storing it makes activation faster; reading it at activation time uses less memory in aggregate and picks up changes to skill files between activations.

The skill's **base directory** (the parent directory of `location`) is needed later to resolve relative paths and enumerate bundled resources — derive it from `location` when needed.


## Step 3: Disclose available skills to the model

Source: https://agentskills.io/llms-full.txt#step-3-disclose-available-skills-to-the-model

Tell the model what skills exist without loading their full content. This is [tier 1 of progressive disclosure](#the-core-principle-progressive-disclosure).

### Building the skill catalog

For each discovered skill, include `name`, `description`, and optionally `location` (the path to the `SKILL.md` file) in whatever structured format suits your stack — XML, JSON, or a bulleted list all work:

```xml theme={null}
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extract PDF text, fill forms, merge files. Use when handling PDFs.</description>
    <location>/home/user/.agents/skills/pdf-processing/SKILL.md</location>
  </skill>
  <skill>
    <name>data-analysis</name>
    <description>Analyze datasets, generate charts, and create summary reports.</description>
    <location>/home/user/project/.agents/skills/data-analysis/SKILL.md</location>
  </skill>
</available_skills>

The following skills provide specialized instructions for specific tasks.
When a task matches a skill's description, use your file-read tool to load
the SKILL.md at the listed location before proceeding.
When a skill references relative paths, resolve them against the skill's
directory (the parent of SKILL.md) and use absolute paths in tool calls.

The following skills provide specialized instructions for specific tasks.
When a task matches a skill's description, call the activate_skill tool
with the skill's name to load its full instructions.
```

Keep these instructions concise. The goal is to tell the model that skills exist and how to load them — the skill content itself provides the detailed instructions once loaded.

### Filtering

Some skills should be excluded from the catalog. Common reasons:

* The user has disabled the skill in settings
* A permission system denies access to the skill
* The skill has opted out of model-driven activation (e.g., via a `disable-model-invocation` flag)

**Hide filtered skills entirely** from the catalog rather than listing them and blocking at activation time. This prevents the model from wasting turns attempting to load skills it can't use.

### When no skills are available

If no skills are discovered, omit the catalog and behavioral instructions entirely. Don't show an empty `<available_skills/>` block or register a skill tool with no valid options — this would confuse the model.


## Step 4: Activate skills

Source: https://agentskills.io/llms-full.txt#step-4-activate-skills

When the model or user selects a skill, deliver the full instructions into the conversation context. This is [tier 2 of progressive disclosure](#the-core-principle-progressive-disclosure).

### Model-driven activation

Most implementations rely on the model's own judgment as the activation mechanism, rather than implementing harness-side trigger matching or keyword detection. The model reads the catalog (from [Step 3](#step-3-disclose-available-skills-to-the-model)), decides a skill is relevant to the current task, and loads it.

Two implementation patterns:

**File-read activation**: The model calls its standard file-read tool with the `SKILL.md` path from the catalog. No special infrastructure needed — the agent's existing file-reading capability is sufficient. The model receives the file content as a tool result. This is the simplest approach when the model has file access.

**Dedicated tool activation**: Register a tool (e.g., `activate_skill`) that takes a skill name and returns the content. This is required when the model can't read files directly, and optional (but useful) even when it can. Advantages over raw file reads:

* Control what content is returned — e.g., strip YAML frontmatter or preserve it (see [What the model receives](#what-the-model-receives) below)
* Wrap content in structured tags for identification during context management
* List bundled resources (e.g., `references/*`) alongside the instructions
* Enforce permissions or prompt for user consent
* Track activation for analytics

<Tip>
  If you use a dedicated activation tool, constrain the `name` parameter to the set of valid skill names (e.g., as an enum in the tool schema). This prevents the model from hallucinating nonexistent skill names. If no skills are available, don't register the tool at all.
</Tip>

### User-explicit activation

Users should also be able to activate skills directly, without waiting for the model to decide. The most common pattern is a **slash command or mention syntax** (`/skill-name` or `$skill-name`) that the harness intercepts. The specific syntax is up to you — the key idea is that the harness handles the lookup and injection, so the model receives skill content without needing to take an activation action itself.

An autocomplete widget (listing available skills as the user types) can also make this discoverable.

### What the model receives

When a skill is activated, the model receives the skill's instructions. Two options for what exactly that content looks like:

**Full file**: The model sees the entire `SKILL.md` including YAML frontmatter. This is the natural outcome with file-read activation, where the model reads the raw file. It's also a valid choice for dedicated tools. The frontmatter may contain fields useful at activation time — for example, [`compatibility`](/specification#compatibility-field) notes environment requirements that could inform how the model executes the skill's instructions.

**Body only (frontmatter stripped)**: The harness parses and removes the YAML frontmatter, returning only the markdown instructions. Among existing implementations with dedicated activation tools, most take this approach — stripping the frontmatter after extracting `name` and `description` during discovery.

Both approaches work in practice.

### Structured wrapping

If you use a dedicated activation tool, consider wrapping skill content in identifying tags. For example:

```xml theme={null}
<skill_content name="pdf-processing">
# PDF Processing


## When to use this skill

Source: https://agentskills.io/llms-full.txt#when-to-use-this-skill

Use this skill when the user needs to work with PDF files...

[rest of SKILL.md body]

Skill directory: /home/user/.agents/skills/pdf-processing
Relative paths in this skill are relative to the skill directory.

<skill_resources>
  <file>scripts/extract.py</file>
  <file>scripts/merge.py</file>
  <file>references/pdf-spec-summary.md</file>
</skill_resources>
</skill_content>
```

This has practical benefits:

* The model can clearly distinguish skill instructions from other conversation content
* The harness can identify skill content during context compaction ([Step 5](#step-5-manage-skill-context-over-time))
* Bundled resources are surfaced to the model without being eagerly loaded

### Listing bundled resources

When a dedicated activation tool returns skill content, it can also enumerate supporting files (scripts, references, assets) in the skill directory — but it should **not eagerly read them**. The model loads specific files on demand using its file-read tools when the skill's instructions reference them.

For large skill directories, consider capping the listing and noting that it may be incomplete.

### Permission allowlisting

If your agent has a permission system that gates file access, **allowlist skill directories** so the model can read bundled resources without triggering user confirmation prompts. Without this, every reference to a bundled script or reference file results in a permission dialog, breaking the flow for skills that include resources beyond the `SKILL.md` itself.


## Step 5: Manage skill context over time

Source: https://agentskills.io/llms-full.txt#step-5-manage-skill-context-over-time

Once skill instructions are in the conversation context, keep them effective for the duration of the session.

### Protect skill content from context compaction

If your agent truncates or summarizes older messages when the context window fills up, **exempt skill content from pruning**. Skill instructions are durable behavioral guidance — losing them mid-conversation silently degrades the agent's performance without any visible error. The model continues operating but without the specialized instructions the skill provided.

Common approaches:

* Flag skill tool outputs as protected so the pruning algorithm skips them
* Use the [structured tags](#structured-wrapping) from Step 4 to identify skill content and preserve it during compaction

### Deduplicate activations

Consider tracking which skills have been activated in the current session. If the model (or user) attempts to load a skill that's already in context, you can skip the re-injection to avoid the same instructions appearing multiple times in the conversation.

### Subagent delegation (optional)

This is an advanced pattern only supported by some clients. Instead of injecting skill instructions into the main conversation, the skill is run in a **separate subagent session**. The subagent receives the skill instructions, performs the task, and returns a summary of its work to the main conversation.

This pattern is useful when a skill's workflow is complex enough to benefit from a dedicated, focused session.


# Client Showcase
Source: https://agentskills.io/clients

Agent products that support the Agent Skills format.

<ClientShowcase />


# Agent Skills Overview
Source: https://agentskills.io/home

A standardized way to give AI agents new capabilities and expertise.


## What are Agent Skills?

Source: https://agentskills.io/llms-full.txt#what-are-agent-skills

Agent Skills are a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows.

At its core, a skill is a folder containing a `SKILL.md` file. This file includes metadata (`name` and `description`, at minimum) and instructions that tell an agent how to perform a specific task. Skills can also bundle scripts, reference materials, templates, and other resources.


## Why Agent Skills?

Source: https://agentskills.io/llms-full.txt#why-agent-skills

Agents are increasingly capable, but often don't have the context they need to do real work reliably. Skills solve this by packaging procedural knowledge and company-, team-, and user-specific context into portable, version-controlled folders that agents load on demand. This gives agents:

* **Domain expertise**: Capture specialized knowledge — from legal review processes to data analysis pipelines to presentation formatting — as reusable instructions and resources.
* **Repeatable workflows**: Turn multi-step tasks into consistent, auditable procedures.
* **Cross-product reuse**: Build a skill once and use it across any skills-compatible agent.


## How do Agent Skills work?

Source: https://agentskills.io/llms-full.txt#how-do-agent-skills-work

Agents load skills through **progressive disclosure**, in three stages:

1. **Discovery**: At startup, agents load only the name and description of each available skill, just enough to know when it might be relevant.

2. **Activation**: When a task matches a skill's description, the agent reads the full `SKILL.md` instructions into context.

3. **Execution**: The agent follows the instructions, optionally executing bundled code or loading referenced files as needed.

Full instructions load only when a task calls for them, so agents can keep many skills on hand with only a small context footprint.


## Where can I use Agent Skills?

Source: https://agentskills.io/llms-full.txt#where-can-i-use-agent-skills

Agent Skills are supported by a large number of AI tools and agentic clients — see the [Client Showcase](/clients) to explore some of them!

<LogoCarousel />


## Open development

Source: https://agentskills.io/llms-full.txt#open-development

The Agent Skills format was originally developed by [Anthropic](https://www.anthropic.com/), released as an open standard, and has been adopted by a growing number of agent products. The standard is open to contributions from the broader ecosystem.

Come join the discussion on [GitHub](https://github.com/agentskills/agentskills) or [Discord](https://discord.gg/MKPE9g8aUy)!


## Get started with Agent Skills

Source: https://agentskills.io/llms-full.txt#get-started-with-agent-skills

<CardGroup>
  <Card title="Quickstart" icon="rocket" href="/skill-creation/quickstart">
    Create your first Agent Skill and see it in action.
  </Card>

  <Card title="Specification" icon="file-code" href="/specification">
    The complete format specification for Agent Skills.
  </Card>
</CardGroup>


# Best practices for skill creators
Source: https://agentskills.io/skill-creation/best-practices

How to write skills that are well-scoped and calibrated to the task.


## Start from real expertise

Source: https://agentskills.io/llms-full.txt#start-from-real-expertise

A common pitfall in skill creation is asking an LLM to generate a skill without providing domain-specific context — relying solely on the LLM's general training knowledge. The result is vague, generic procedures ("handle errors appropriately," "follow best practices for authentication") rather than the specific API patterns, edge cases, and project conventions that make a skill valuable.

Effective skills are grounded in real expertise. The key is feeding domain-specific context into the creation process.

### Extract from a hands-on task

Complete a real task in conversation with an agent, providing context, corrections, and preferences along the way. Then extract the reusable pattern into a skill. Pay attention to:

* **Steps that worked** — the sequence of actions that led to success
* **Corrections you made** — places where you steered the agent's approach (e.g., "use library X instead of Y," "check for edge case Z")
* **Input/output formats** — what the data looked like going in and coming out
* **Context you provided** — project-specific facts, conventions, or constraints the agent didn't already know

### Synthesize from existing project artifacts

When you have a body of existing knowledge, you can feed it into an LLM and ask it to synthesize a skill. A data-pipeline skill synthesized from your team's actual incident reports and runbooks will outperform one synthesized from a generic "data engineering best practices" article, because it captures *your* schemas, failure modes, and recovery procedures. The key is project-specific material, not generic references.

Good source material includes:

* Internal documentation, runbooks, and style guides
* API specifications, schemas, and configuration files
* Code review comments and issue trackers (captures recurring concerns and reviewer expectations)
* Version control history, especially patches and fixes (reveals patterns through what actually changed)
* Real-world failure cases and their resolutions


## Refine with real execution

Source: https://agentskills.io/llms-full.txt#refine-with-real-execution

The first draft of a skill usually needs refinement. Run the skill against real tasks, then feed the results — all of them, not just failures — back into the creation process. Ask: what triggered false positives? What was missed? What could be cut?

Even a single pass of execute-then-revise noticeably improves quality, and complex domains often benefit from several.

<Tip>
  Read agent execution traces, not just final outputs. If the agent wastes time on unproductive steps, common causes include instructions that are too vague (the agent tries several approaches before finding one that works), instructions that don't apply to the current task (the agent follows them anyway), or too many options presented without a clear default.
</Tip>

For a more structured approach to iteration, including test cases, assertions, and grading, see [Evaluating skill output quality](/skill-creation/evaluating-skills).


## Spending context wisely

Source: https://agentskills.io/llms-full.txt#spending-context-wisely

Once a skill activates, its full `SKILL.md` body loads into the agent's context window alongside conversation history, system context, and other active skills. Every token in your skill competes for the agent's attention with everything else in that window.

### Add what the agent lacks, omit what it knows

Focus on what the agent *wouldn't* know without your skill: project-specific conventions, domain-specific procedures, non-obvious edge cases, and the particular tools or APIs to use. You don't need to explain what a PDF is, how HTTP works, or what a database migration does.

````markdown theme={null}
<!-- Too verbose — the agent already knows what PDFs are -->


## Extract PDF text

Source: https://agentskills.io/llms-full.txt#extract-pdf-text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. pdfplumber is recommended because it handles most cases well.

<!-- Better — jumps straight to what the agent wouldn't know on its own -->


## Extract PDF text

Source: https://agentskills.io/llms-full.txt#extract-pdf-text-2

Use pdfplumber for text extraction. For scanned documents, fall back to
pdf2image with pytesseract.

````

Ask yourself about each piece of content: "Would the agent get this wrong without this instruction?" If the answer is no, cut it. If you're unsure, test it. And if the agent already handles the entire task well without the skill, the skill may not be adding value. See [Evaluating skill output quality](/skill-creation/evaluating-skills) for how to test this systematically.

### Design coherent units

Deciding what a skill should cover is like deciding what a function should do: you want it to encapsulate a coherent unit of work that composes well with other skills. Skills scoped too narrowly force multiple skills to load for a single task, risking overhead and conflicting instructions. Skills scoped too broadly become hard to activate precisely. A skill for querying a database and formatting the results may be one coherent unit, while a skill that also covers database administration is probably trying to do too much.

### Aim for moderate detail

Overly comprehensive skills can hurt more than they help — the agent struggles to extract what's relevant and may pursue unproductive paths triggered by instructions that don't apply to the current task. Concise, stepwise guidance with a working example tends to outperform exhaustive documentation. When you find yourself covering every edge case, consider whether most are better handled by the agent's own judgment.

### Structure large skills with progressive disclosure

The [specification](/specification#progressive-disclosure) recommends keeping `SKILL.md` under 500 lines and 5,000 tokens — just the core instructions the agent needs on every run. When a skill legitimately needs more content, move detailed reference material to separate files in `references/` or similar directories.

The key is telling the agent *when* to load each file. "Read `references/api-errors.md` if the API returns a non-200 status code" is more useful than a generic "see references/ for details." This lets the agent load context on demand rather than up front, which is how [progressive disclosure](/specification#progressive-disclosure) is designed to work.


## Calibrating control

Source: https://agentskills.io/llms-full.txt#calibrating-control

Not every part of a skill needs the same level of prescriptiveness. Match the specificity of your instructions to the fragility of the task.

### Match specificity to fragility

**Give the agent freedom** when multiple approaches are valid and the task tolerates variation. For flexible instructions, explaining *why* can be more effective than rigid directives — an agent that understands the purpose behind an instruction makes better context-dependent decisions. A code review skill can describe what to look for without prescribing exact steps:

```markdown theme={null}


## Code review process

Source: https://agentskills.io/llms-full.txt#code-review-process

1. Check all database queries for SQL injection (use parameterized queries)
2. Verify authentication checks on every endpoint
3. Look for race conditions in concurrent code paths
4. Confirm error messages don't leak internal details

`markdown theme={null}


## Database migration

Source: https://agentskills.io/llms-full.txt#database-migration

Run exactly this sequence:

Do not modify the command or add additional flags.
`

`markdown theme={null}
<!-- Too many options -->
You can use pypdf, pdfplumber, PyMuPDF, or pdf2image...

<!-- Clear default with escape hatch -->
Use pdfplumber for text extraction:

For scanned PDFs requiring OCR, use pdf2image with pytesseract instead.
`

markdown theme={null}
<!-- Specific answer — only useful for this exact task -->
Join the `orders` table to `customers` on `customer_id`, filter where
`region = 'EMEA'`, and sum the `amount` column.

<!-- Reusable method — works for any analytical query -->
1. Read the schema from `references/schema.yaml` to find relevant tables
2. Join tables using the `_id` foreign key convention
3. Apply any filters from the user's request as WHERE clauses
4. Aggregate numeric columns as needed and format as a markdown table
```

This doesn't mean skills can't include specific details — output format templates (see [Templates for output format](#templates-for-output-format)), constraints like "never output PII," and tool-specific instructions are all valuable. The point is that the *approach* should generalize even when individual details are specific.


## Patterns for effective instructions

Source: https://agentskills.io/llms-full.txt#patterns-for-effective-instructions

These are reusable techniques for structuring skill content. Not every skill needs all of them — use the ones that fit your task.

### Gotchas sections

The highest-value content in many skills is a list of gotchas — environment-specific facts that defy reasonable assumptions. These aren't general advice ("handle errors appropriately") but concrete corrections to mistakes the agent will make without being told otherwise:

```markdown theme={null}


## Gotchas

Source: https://agentskills.io/llms-full.txt#gotchas

- The `users` table uses soft deletes. Queries must include
  `WHERE deleted_at IS NULL` or results will include deactivated accounts.
- The user ID is `user_id` in the database, `uid` in the auth service,
  and `accountId` in the billing API. All three refer to the same value.
- The `/health` endpoint returns 200 as long as the web server is running,
  even if the database connection is down. Use `/ready` to check full
  service health.

`markdown theme={null}


## Report structure

Source: https://agentskills.io/llms-full.txt#report-structure

Use this template, adapting sections as needed for the specific analysis:

```markdown
# [Analysis Title]


## Executive summary

Source: https://agentskills.io/llms-full.txt#executive-summary

[One-paragraph overview of key findings]


## Key findings

Source: https://agentskills.io/llms-full.txt#key-findings

- Finding 1 with supporting data
- Finding 2 with supporting data


## Recommendations

Source: https://agentskills.io/llms-full.txt#recommendations

1. Specific actionable recommendation
2. Specific actionable recommendation

`

### Checklists for multi-step workflows

An explicit checklist helps the agent track progress and avoid skipping steps, especially when steps have dependencies or validation gates.

```markdown theme={null}


## Form processing workflow

Source: https://agentskills.io/llms-full.txt#form-processing-workflow

Progress:
- [ ] Step 1: Analyze the form (run `scripts/analyze_form.py`)
- [ ] Step 2: Create field mapping (edit `fields.json`)
- [ ] Step 3: Validate mapping (run `scripts/validate_fields.py`)
- [ ] Step 4: Fill the form (run `scripts/fill_form.py`)
- [ ] Step 5: Verify output (run `scripts/verify_output.py`)

markdown theme={null}


## Editing workflow

Source: https://agentskills.io/llms-full.txt#editing-workflow

1. Make your edits
2. Run validation: `python scripts/validate.py output/`
3. If validation fails:
   - Review the error message
   - Fix the issues
   - Run validation again
4. Only proceed when validation passes

markdown theme={null}


## PDF form filling

Source: https://agentskills.io/llms-full.txt#pdf-form-filling

1. Extract form fields: `python scripts/analyze_form.py input.pdf` → `form_fields.json`
   (lists every field name, type, and whether it's required)
2. Create `field_values.json` mapping each field name to its intended value
3. Validate: `python scripts/validate_fields.py form_fields.json field_values.json`
   (checks that every field name exists in the form, types are compatible, and
   required fields aren't missing)
4. If validation fails, revise `field_values.json` and re-validate
5. Fill the form: `python scripts/fill_form.py input.pdf field_values.json output.pdf`
```

The key ingredient is step 3: a validation script that checks the plan (`field_values.json`) against the source of truth (`form_fields.json`). Errors like "Field 'signature\_date' not found — available fields: customer\_name, order\_total, signature\_date\_signed" give the agent enough information to self-correct.

### Bundling reusable scripts

When [iterating on a skill](/skill-creation/evaluating-skills), compare the agent's execution traces across test cases. If you notice the agent independently reinventing the same logic each run — building charts, parsing a specific format, validating output — that's a signal to write a tested script once and bundle it in `scripts/`.

For more on designing and bundling scripts, see [Using scripts in skills](/skill-creation/using-scripts).


## Next steps

Source: https://agentskills.io/llms-full.txt#next-steps

Once you have a working skill, two guides can help you refine it further:

* **[Evaluating skill output quality](/skill-creation/evaluating-skills)** — Set up test cases, grade results, and iterate systematically.
* **[Optimizing skill descriptions](/skill-creation/optimizing-descriptions)** — Test and improve your skill's `description` field so it triggers on the right prompts.


# Evaluating skill output quality
Source: https://agentskills.io/skill-creation/evaluating-skills

How to test whether your skill produces good outputs using eval-driven iteration.

You wrote a skill, tried it on a prompt, and it seemed to work. But does it work reliably — across varied prompts, in edge cases, better than no skill at all? Running structured evaluations (evals) answers these questions and gives you a feedback loop for improving the skill systematically.


## Designing test cases

Source: https://agentskills.io/llms-full.txt#designing-test-cases

A test case has three parts:

* **Prompt**: a realistic user message — the kind of thing someone would actually type.
* **Expected output**: a human-readable description of what success looks like.
* **Input files** (optional): files the skill needs to work with.

Store test cases in `evals/evals.json` inside your skill directory:

```json evals/evals.json theme={null}
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": 1,
      "prompt": "I have a CSV of monthly sales data in data/sales_2025.csv. Can you find the top 3 months by revenue and make a bar chart?",
      "expected_output": "A bar chart image showing the top 3 months by revenue, with labeled axes and values.",
      "files": ["evals/files/sales_2025.csv"]
    },
    {
      "id": 2,
      "prompt": "there's a csv in my downloads called customers.csv, some rows have missing emails — can you clean it up and tell me how many were missing?",
      "expected_output": "A cleaned CSV with missing emails handled, plus a count of how many were missing.",
      "files": ["evals/files/customers.csv"]
    }
  ]
}
```

**Tips for writing good test prompts:**

* **Start with 2-3 test cases.** Don't over-invest before you've seen your first round of results. You can expand the set later.
* **Vary the prompts.** Use different phrasings, levels of detail, and formality. Some prompts should be casual ("hey can you clean up this csv"), others precise ("Parse the CSV at data/input.csv, drop rows where column B is null, and write the result to data/output.csv").
* **Cover edge cases.** Include at least one prompt that tests a boundary condition — a malformed input, an unusual request, or a case where the skill's instructions might be ambiguous.
* **Use realistic context.** Real users mention file paths, column names, and personal context. Prompts like "process this data" are too vague to test anything useful.

Don't worry about defining specific pass/fail checks yet — just the prompts and expected outputs. You'll add detailed checks (called assertions) after you see what the first run produces.


## Running evals

Source: https://agentskills.io/llms-full.txt#running-evals

The core pattern is to run each test case twice: once **with the skill** and once **without it** (or with a previous version). This gives you a baseline to compare against.

### Workspace structure

Organize eval results in a workspace directory alongside your skill directory. Each pass through the full eval loop gets its own `iteration-N/` directory. Within that, each test case gets an eval directory with `with_skill/` and `without_skill/` subdirectories:

The main file you author by hand is `evals/evals.json`. The other JSON files (`grading.json`, `timing.json`, `benchmark.json`) are produced during the eval process — by the agent, by scripts, or by you.

### Spawning runs

Each eval run should start with a clean context — no leftover state from previous runs or from the skill development process. This ensures the agent follows only what the `SKILL.md` tells it. In environments that support subagents (Claude Code, for example), this isolation comes naturally: each child task starts fresh. Without subagents, use a separate session for each run.

For each run, provide:

* The skill path (or no skill for the baseline)
* The test prompt
* Any input files
* The output directory

Here's an example of the instructions you'd give the agent for a single with-skill run:

For the baseline, use the same prompt but without the skill path, saving to `without_skill/outputs/`.

When improving an existing skill, use the previous version as your baseline. Snapshot it before editing (`cp -r <skill-path> <workspace>/skill-snapshot/`), point the baseline run at the snapshot, and save to `old_skill/outputs/` instead of `without_skill/`.

### Capturing timing data

Timing data lets you compare how much time and tokens the skill costs relative to the baseline — a skill that dramatically improves output quality but triples token usage is a different trade-off than one that's both better and cheaper. When each run completes, record the token count and duration:

```json timing.json theme={null}
{
  "total_tokens": 84852,
  "duration_ms": 23332
}
```

<Tip>
  In Claude Code, when a subagent task finishes, the [task completion notification](https://platform.claude.com/docs/en/agent-sdk/typescript#sdk-task-notification-message) includes `total_tokens` and `duration_ms`. Save these values immediately — they aren't persisted anywhere else.
</Tip>


## Writing assertions

Source: https://agentskills.io/llms-full.txt#writing-assertions

Assertions are verifiable statements about what the output should contain or achieve. Add them after you see your first round of outputs — you often don't know what "good" looks like until the skill has run.

Good assertions:

* `"The output file is valid JSON"` — programmatically verifiable.
* `"The bar chart has labeled axes"` — specific and observable.
* `"The report includes at least 3 recommendations"` — countable.

Weak assertions:

* `"The output is good"` — too vague to grade.
* `"The output uses exactly the phrase 'Total Revenue: $X'"` — too brittle; correct output with different wording would fail.

Not everything needs an assertion. Some qualities — writing style, visual design, whether the output "feels right" — are hard to decompose into pass/fail checks. These are better caught during [human review](#reviewing-results-with-a-human). Reserve assertions for things that can be checked objectively.

Add assertions to each test case in `evals/evals.json`:

```json evals/evals.json highlight={9-14} theme={null}
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": 1,
      "prompt": "I have a CSV of monthly sales data in data/sales_2025.csv. Can you find the top 3 months by revenue and make a bar chart?",
      "expected_output": "A bar chart image showing the top 3 months by revenue, with labeled axes and values.",
      "files": ["evals/files/sales_2025.csv"],
      "assertions": [
        "The output includes a bar chart image file",
        "The chart shows exactly 3 months",
        "Both axes are labeled",
        "The chart title or caption mentions revenue"
      ]
    }
  ]
}
```


## Grading outputs

Source: https://agentskills.io/llms-full.txt#grading-outputs

Grading means evaluating each assertion against the actual outputs and recording **PASS** or **FAIL** with specific evidence. The evidence should quote or reference the output, not just state an opinion.

The simplest approach is to give the outputs and assertions to an LLM and ask it to evaluate each one. For assertions that can be checked by code (valid JSON, correct row count, file exists with expected dimensions), use a verification script — scripts are more reliable than LLM judgment for mechanical checks and reusable across iterations.

```json grading.json theme={null}
{
  "assertion_results": [
    {
      "text": "The output includes a bar chart image file",
      "passed": true,
      "evidence": "Found chart.png (45KB) in outputs directory"
    },
    {
      "text": "The chart shows exactly 3 months",
      "passed": true,
      "evidence": "Chart displays bars for March, July, and November"
    },
    {
      "text": "Both axes are labeled",
      "passed": false,
      "evidence": "Y-axis is labeled 'Revenue ($)' but X-axis has no label"
    },
    {
      "text": "The chart title or caption mentions revenue",
      "passed": true,
      "evidence": "Chart title reads 'Top 3 Months by Revenue'"
    }
  ],
  "summary": {
    "passed": 3,
    "failed": 1,
    "total": 4,
    "pass_rate": 0.75
  }
}
```

### Grading principles

* **Require concrete evidence for a PASS.** Don't give the benefit of the doubt. If an assertion says "includes a summary" and the output has a section titled "Summary" with one vague sentence, that's a FAIL — the label is there but the substance isn't.
* **Review the assertions themselves, not just the results.** While grading, notice when assertions are too easy (always pass regardless of skill quality), too hard (always fail even when the output is good), or unverifiable (can't be checked from the output alone). Fix these for the next iteration.

<Tip>
  For comparing two skill versions, try **blind comparison**: present both outputs to an LLM judge without revealing which came from which version. The judge scores holistic qualities — organization, formatting, usability, polish — on its own rubric, free from bias about which version "should" be better. This complements assertion grading: two outputs might both pass all assertions but differ significantly in overall quality.
</Tip>


## Aggregating results

Source: https://agentskills.io/llms-full.txt#aggregating-results

Once every run in the iteration is graded, compute summary statistics per configuration and save them to `benchmark.json` alongside the eval directories (e.g., `csv-analyzer-workspace/iteration-1/benchmark.json`):

```json benchmark.json theme={null}
{
  "run_summary": {
    "with_skill": {
      "pass_rate": { "mean": 0.83, "stddev": 0.06 },
      "time_seconds": { "mean": 45.0, "stddev": 12.0 },
      "tokens": { "mean": 3800, "stddev": 400 }
    },
    "without_skill": {
      "pass_rate": { "mean": 0.33, "stddev": 0.10 },
      "time_seconds": { "mean": 32.0, "stddev": 8.0 },
      "tokens": { "mean": 2100, "stddev": 300 }
    },
    "delta": {
      "pass_rate": 0.50,
      "time_seconds": 13.0,
      "tokens": 1700
    }
  }
}
```

The `delta` tells you what the skill costs (more time, more tokens) and what it buys (higher pass rate). A skill that adds 13 seconds but improves pass rate by 50 percentage points is probably worth it. A skill that doubles token usage for a 2-point improvement might not be.

<Note>
  Standard deviation (`stddev`) is only meaningful with multiple runs per eval. In early iterations with just 2-3 test cases and single runs, focus on the raw pass counts and the delta — the statistical measures become useful as you expand the test set and run each eval multiple times.
</Note>


## Analyzing patterns

Source: https://agentskills.io/llms-full.txt#analyzing-patterns

Aggregate statistics can hide important patterns. After computing the benchmarks:

* **Remove or replace assertions that always pass in both configurations.** These don't tell you anything useful — the model handles them fine without the skill. They inflate the with-skill pass rate without reflecting actual skill value.
* **Investigate assertions that always fail in both configurations.** Either the assertion is broken (asking for something the model can't do), the test case is too hard, or the assertion is checking for the wrong thing. Fix these before the next iteration.
* **Study assertions that pass with the skill but fail without.** This is where the skill is clearly adding value. Understand *why* — which instructions or scripts made the difference?
* **Tighten instructions when results are inconsistent across runs.** If the same eval passes sometimes and fails others (reflected as high `stddev` in the benchmark), the eval may be flaky (sensitive to model randomness), or the skill's instructions may be ambiguous enough that the model interprets them differently each time. Add examples or more specific guidance to reduce ambiguity.
* **Check time and token outliers.** If one eval takes 3x longer than the others, read its execution transcript (the full log of what the model did during the run) to find the bottleneck.


## Reviewing results with a human

Source: https://agentskills.io/llms-full.txt#reviewing-results-with-a-human

Assertion grading and pattern analysis catch a lot, but they only check what you thought to write assertions for. A human reviewer brings a fresh perspective — catching issues you didn't anticipate, noticing when the output is technically correct but misses the point, or spotting problems that are hard to express as pass/fail checks. For each test case, review the actual outputs alongside the grades.

Record specific feedback for each test case and save it in the workspace (e.g., as a `feedback.json` alongside the eval directories):

```json feedback.json theme={null}
{
  "eval-top-months-chart": "The chart is missing axis labels and the months are in alphabetical order instead of chronological.",
  "eval-clean-missing-emails": ""
}
```

"The chart is missing axis labels" is actionable; "looks bad" is not. Empty feedback means the output looked fine — that test case passed your review. During the [iteration step](#iterating-on-the-skill), focus your improvements on the test cases where you had specific complaints.


## Iterating on the skill

Source: https://agentskills.io/llms-full.txt#iterating-on-the-skill

After grading and reviewing, you have three sources of signal:

* **Failed assertions** point to specific gaps — a missing step, an unclear instruction, or a case the skill doesn't handle.
* **Human feedback** points to broader quality issues — the approach was wrong, the output was poorly structured, or the skill produced a technically correct but unhelpful result.
* **Execution transcripts** reveal *why* things went wrong. If the agent ignored an instruction, the instruction may be ambiguous. If the agent spent time on unproductive steps, those instructions may need to be simplified or removed.

The most effective way to turn these signals into skill improvements is to give all three — along with the current `SKILL.md` — to an LLM and ask it to propose changes. The LLM can synthesize patterns across failed assertions, reviewer complaints, and transcript behavior that would be tedious to connect manually. When prompting the LLM, include these guidelines:

* **Generalize from feedback.** The skill will be used across many different prompts, not just the test cases. Fixes should address underlying issues broadly rather than adding narrow patches for specific examples.
* **Keep the skill lean.** Fewer, better instructions often outperform exhaustive rules. If transcripts show wasted work (unnecessary validation, unneeded intermediate outputs), remove those instructions. If pass rates plateau despite adding more rules, the skill may be over-constrained — try removing instructions and see if results hold or improve.
* **Explain the why.** Reasoning-based instructions ("Do X because Y tends to cause Z") work better than rigid directives ("ALWAYS do X, NEVER do Y"). Models follow instructions more reliably when they understand the purpose.
* **Bundle repeated work.** If every test run independently wrote a similar helper script (a chart builder, a data parser), that's a signal to bundle the script into the skill's `scripts/` directory. See [Using scripts](/skill-creation/using-scripts) for how to do this.

### The loop

1. Give the eval signals and current `SKILL.md` to an LLM and ask it to propose improvements.
2. Review and apply the changes.
3. Rerun all test cases in a new `iteration-<N+1>/` directory.
4. Grade and aggregate the new results.
5. Review with a human. Repeat.

Stop when you're satisfied with the results, feedback is consistently empty, or you're no longer seeing meaningful improvement between iterations.

<Tip>
  The [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) Skill automates much of this workflow — running evals, grading assertions, aggregating benchmarks, and presenting results for human review.
</Tip>


# Optimizing skill descriptions
Source: https://agentskills.io/skill-creation/optimizing-descriptions

How to improve your skill's description so it triggers reliably on relevant prompts.

A skill only helps if it gets activated. The `description` field in your `SKILL.md` frontmatter is the primary mechanism agents use to decide whether to load a skill for a given task. An under-specified description means the skill won't trigger when it should; an over-broad description means it triggers when it shouldn't.

This guide covers how to systematically test and improve your skill's description for triggering accuracy.


## How skill triggering works

Source: https://agentskills.io/llms-full.txt#how-skill-triggering-works

Agents use [progressive disclosure](/specification#progressive-disclosure) to manage context. At startup, they load only the `name` and `description` of each available skill — just enough to decide when a skill might be relevant. When a user's task matches a description, the agent reads the full `SKILL.md` into context and follows its instructions.

This means the description carries the entire burden of triggering. If the description doesn't convey when the skill is useful, the agent won't know to reach for it.

One important nuance: agents typically only consult skills for tasks that require knowledge or capabilities beyond what they can handle alone. A simple, one-step request like "read this PDF" may not trigger a PDF skill even if the description matches perfectly, because the agent can handle it with basic tools. Tasks that involve specialized knowledge — an unfamiliar API, a domain-specific workflow, or an uncommon format — are where a well-written description can make the difference.


## Writing effective descriptions

Source: https://agentskills.io/llms-full.txt#writing-effective-descriptions

Before testing, it helps to know what a good description looks like. A few principles:

* **Use imperative phrasing.** Frame the description as an instruction to the agent: "Use this skill when..." rather than "This skill does..." The agent is deciding whether to act, so tell it when to act.
* **Focus on user intent, not implementation.** Describe what the user is trying to achieve, not the skill's internal mechanics. The agent matches against what the user asked for.
* **Err on the side of being pushy.** Explicitly list contexts where the skill applies, including cases where the user doesn't name the domain directly: "even if they don't explicitly mention 'CSV' or 'analysis.'"
* **Keep it concise.** A few sentences to a short paragraph is usually right — long enough to cover the skill's scope, short enough that it doesn't bloat the agent's context across many skills. The [specification](/specification#description-field) enforces a hard limit of 1024 characters.


## Designing trigger eval queries

Source: https://agentskills.io/llms-full.txt#designing-trigger-eval-queries

To test triggering, you need a set of eval queries — realistic user prompts labeled with whether they should or shouldn't trigger your skill.

```json eval_queries.json theme={null}
[
  { "query": "I've got a spreadsheet in ~/data/q4_results.xlsx with revenue in col C and expenses in col D — can you add a profit margin column and highlight anything under 10%?", "should_trigger": true },
  { "query": "whats the quickest way to convert this json file to yaml", "should_trigger": false }
]
```

Aim for about 20 queries: 8-10 that should trigger and 8-10 that shouldn't.

### Should-trigger queries

These test whether the description captures the skill's scope. Vary them along several axes:

* **Phrasing**: some formal, some casual, some with typos or abbreviations.
* **Explicitness**: some name the skill's domain directly ("analyze this CSV"), others describe the need without naming it ("my boss wants a chart from this data file").
* **Detail**: mix terse prompts with context-heavy ones — a short "analyze my sales CSV and make a chart" alongside a longer message with file paths, column names, and backstory.
* **Complexity**: vary the number of steps and decision points. Include single-step tasks alongside multi-step workflows to test whether the agent can discern the skill is relevant when the task it addresses is buried in a larger chain.

The most useful should-trigger queries are ones where the skill would help but the connection isn't obvious from the query alone. These are the cases where description wording makes the difference — if the query already asks for exactly what the skill does, any reasonable description would trigger.

### Should-not-trigger queries

The most valuable negative test cases are **near-misses** — queries that share keywords or concepts with your skill but actually need something different. These test whether the description is precise, not just broad.

For a CSV analysis skill, weak negative examples would be:

* `"Write a fibonacci function"` — obviously irrelevant, tests nothing.
* `"What's the weather today?"` — no keyword overlap, too easy.

Strong negative examples:

* `"I need to update the formulas in my Excel budget spreadsheet"` — shares "spreadsheet" and "data" concepts, but needs Excel editing, not CSV analysis.
* `"can you write a python script that reads a csv and uploads each row to our postgres database"` — involves CSV, but the task is database ETL, not analysis.

### Tips for realism

Real user prompts contain context that generic test queries lack. Include:

* File paths (`~/Downloads/report_final_v2.xlsx`)
* Personal context (`"my manager asked me to..."`)
* Specific details (column names, company names, data values)
* Casual language, abbreviations, and occasional typos


## Testing whether a description triggers

Source: https://agentskills.io/llms-full.txt#testing-whether-a-description-triggers

The basic approach: run each query through your agent with the skill installed and observe whether the agent invokes it. Make sure the skill is registered and discoverable by your agent — how this works varies by client (e.g., a skills directory, a configuration file, or a CLI flag).

Most agent clients provide some form of observability — execution logs, tool call histories, or verbose output — that lets you see which skills were consulted during a run. Check your client's documentation for details. The skill triggered if the agent loaded your skill's `SKILL.md`; it didn't trigger if the agent proceeded without consulting it.

A query "passes" if:

* `should_trigger` is `true` and the skill was invoked, or
* `should_trigger` is `false` and the skill was not invoked.

### Running multiple times

Model behavior is nondeterministic — the same query might trigger the skill on one run but not the next. Run each query multiple times (3 is a reasonable starting point) and compute a **trigger rate**: the fraction of runs where the skill was invoked.

A should-trigger query passes if its trigger rate is above a threshold (0.5 is a reasonable default). A should-not-trigger query passes if its trigger rate is below that threshold.

With 20 queries at 3 runs each, that's 60 invocations. You'll want to script this. Here's the general structure — replace the `claude` invocation and detection logic in `check_triggered` with whatever your agent client provides:

```bash theme={null}
#!/bin/bash
QUERIES_FILE="${1:?Usage: $0 <queries.json>}"
SKILL_NAME="my-skill"
RUNS=3

# This example uses Claude Code's JSON output to check for Skill tool calls.
# Replace this function with detection logic for your agent client.
# Should return 0 (success) if the skill was invoked, 1 otherwise.
check_triggered() {
  local query="$1"
  claude -p "$query" --output-format json 2>/dev/null \
    | jq -e --arg skill "$SKILL_NAME" \
      'any(.messages[].content[]; .type == "tool_use" and .name == "Skill" and .input.skill == $skill)' \
      > /dev/null 2>&1
}

count=$(jq length "$QUERIES_FILE")
for i in $(seq 0 $((count - 1))); do
  query=$(jq -r ".[$i].query" "$QUERIES_FILE")
  should_trigger=$(jq -r ".[$i].should_trigger" "$QUERIES_FILE")
  triggers=0

  for run in $(seq 1 $RUNS); do
    check_triggered "$query" && triggers=$((triggers + 1))
  done

  jq -n \
    --arg query "$query" \
    --argjson should_trigger "$should_trigger" \
    --argjson triggers "$triggers" \
    --argjson runs "$RUNS" \
    '{query: $query, should_trigger: $should_trigger, triggers: $triggers, runs: $runs, trigger_rate: ($triggers / $runs)}'
done | jq -s '.'
```

<Tip>
  If your agent client supports it, you can stop a run early once the outcome is clear — the agent either consulted the skill or started working without it. This can significantly reduce the time and cost of running the full eval set.
</Tip>


## Avoiding overfitting with train/validation splits

Source: https://agentskills.io/llms-full.txt#avoiding-overfitting-with-train-validation-splits

If you optimize the description against all your queries, you risk overfitting — crafting a description that works for these specific phrasings but fails on new ones.

The solution is to split your query set:

* **Train set (\~60%)**: the queries you use to identify failures and guide improvements.
* **Validation set (\~40%)**: queries you set aside and only use to check whether improvements generalize.

Make sure both sets contain a proportional mix of should-trigger and should-not-trigger queries — don't accidentally put all the positives in one set. Shuffle randomly and keep the split fixed across iterations so you're comparing apples to apples.

If you're using a script like the one [above](#running-multiple-times), you can split your queries into two files — `train_queries.json` and `validation_queries.json` — and run the script against each one separately.


## The optimization loop

Source: https://agentskills.io/llms-full.txt#the-optimization-loop

1. **Evaluate** the current description on both *train and validation sets*. The train results guide your changes; the validation results tell you whether those changes are generalizing.
2. **Identify failures** in the *train set*: which should-trigger queries didn't trigger? Which should-not-trigger queries did?
   * Only use train set failures to guide your changes — whether you're revising the description yourself or prompting an LLM, keep validation set results out of the process.
3. **Revise the description.** Focus on generalizing:
   * If should-trigger queries are failing, the description may be too narrow. Broaden the scope or add context about when the skill is useful.
   * If should-not-trigger queries are false-triggering, the description may be too broad. Add specificity about what the skill does *not* do, or clarify the boundary between this skill and adjacent capabilities.
   * Avoid adding specific keywords from failed queries — that's overfitting. Instead, find the general category or concept those queries represent and address that.
   * If you're stuck after several iterations, try a structurally different approach to the description rather than incremental tweaks. A different framing or sentence structure may break through where refinement can't.
   * Check that the description stays under the 1024-character limit — descriptions tend to grow during optimization.
4. **Repeat** steps 1-3 until all *train set* queries pass or you stop seeing meaningful improvement.
5. **Select the best iteration** by its validation pass rate — the fraction of queries in the *validation set* that passed. Note that the best description may not be the last one you produced; an earlier iteration might have a higher validation pass rate than later ones that overfit to the train set.

Five iterations is usually enough. If performance isn't improving, the issue may be with the queries (too easy, too hard, or poorly labeled) rather than the description.

<Tip>
  The [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) Skill automates this loop end-to-end: it splits the eval set, evaluates trigger rates in parallel, proposes description improvements using Claude, and generates a live HTML report you can watch as it runs.
</Tip>


## Applying the result

Source: https://agentskills.io/llms-full.txt#applying-the-result

Once you've selected the best description:

1. Update the `description` field in your `SKILL.md` frontmatter.
2. Verify the description is under the [1024-character limit](/specification#description-field).
3. Verify the description triggers as expected. Try a few prompts manually as a quick sanity check. For a more rigorous test, write 5-10 fresh queries (a mix of should-trigger and should-not-trigger) and run them through the eval script — since these queries were never part of the optimization process, they give you an honest check on whether the description generalizes.

Before and after:

```yaml theme={null}
# Before
description: Process CSV files.

# After
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use this
  skill when the user has a CSV, TSV, or Excel file and wants to
  explore, transform, or visualize the data, even if they don't
  explicitly mention "CSV" or "analysis."
```

The improved description is more specific about what the skill does (summary stats, derived columns, charts, cleaning) and broader about when it applies (CSV, TSV, Excel; even without explicit keywords).


## Next steps

Source: https://agentskills.io/llms-full.txt#next-steps-2

Once your skill triggers reliably, you'll want to evaluate whether it produces good outputs. See [Evaluating skill output quality](/skill-creation/evaluating-skills) for how to set up test cases, grade results, and iterate.


# Quickstart
Source: https://agentskills.io/skill-creation/quickstart

Create your first Agent Skill and see it work in VS Code.

In this tutorial, you'll create a skill that gives an agent the capability to roll dice using a random number generator.


## Prerequisites

Source: https://agentskills.io/llms-full.txt#prerequisites

* [VS Code](https://code.visualstudio.com/) with [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)

<Note>
  This tutorial uses VS Code, but Agent Skills are an open format. The same skill works in any compatible agent, including Claude Code and OpenAI Codex.
</Note>


## Create the skill

Source: https://agentskills.io/llms-full.txt#create-the-skill

A skill is a folder containing a `SKILL.md` file. VS Code looks for skills in `.agents/skills/` by default. Create `.agents/skills/roll-dice/SKILL.md` in your project:

````markdown .agents/skills/roll-dice/SKILL.md theme={null}
---
name: roll-dice
description: Roll dice using a random number generator. Use when asked to roll a die (d6, d20, etc.), roll dice, or generate a random dice roll.
---

To roll a die, use the following command that generates a random number from 1
to the given number of sides:

Replace `<sides>` with the number of sides on the die (e.g., 6 for a standard
die, 20 for a d20).
````

That's it — one file, under 20 lines. Here's what each part does:

* **`name`** — A short identifier for the skill. Must match the folder name.
* **`description`** — Tells the agent when to use this skill. This is how the agent decides whether to activate it.
* **The body** — Instructions the agent follows when the skill activates. Here, the agent is instructed to generate a random number using a terminal command, substituting the number of sides from the user's request.
