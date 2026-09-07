# agentskills.io Documentation (Part 2 of 2)

## Try it out

Source: https://agentskills.io/llms-full.txt#try-it-out

1. Open your project in VS Code.
2. Open the Copilot Chat panel.
3. Select **Agent** mode from the mode dropdown at the bottom of the chat panel.
4. Type `/skills` to confirm that `roll-dice` appears in the list. If it doesn't, check that the file is at `.agents/skills/roll-dice/SKILL.md` relative to your project root.
5. Ask: **"Roll a d20"**

The agent should activate the `roll-dice` skill. It may ask for permission to run a terminal command — allow it. It will run the command and return a random number between 1 and 20.

<Note>
  Tool-use reliability varies across models — some follow skill instructions and run commands consistently, while others may attempt to answer on their own. If the agent responds without running a terminal command, try selecting a different model from the model dropdown.
</Note>


## How it works

Source: https://agentskills.io/llms-full.txt#how-it-works

Here's what happened behind the scenes:

1. **Discovery** — When the chat session started, the agent scanned default skill directories and found your skill. It read only the `name` and `description`, just enough to know when the skill might be relevant.

2. **Activation** — When you asked about rolling dice, the agent matched your question to the skill's description and loaded the full `SKILL.md` body into context.

3. **Execution** — The agent followed the instructions in the body, adapting the terminal command to the number of sides in your request.

This process uses **progressive disclosure** to let the agent access many skills without loading all their instructions up front.


## Next steps

Source: https://agentskills.io/llms-full.txt#next-steps-3

You've created a working Agent Skill. From here:

* **[Best practices](/skill-creation/best-practices)** — How to write skills that are well-scoped and effective.
* **[Optimizing skill descriptions](/skill-creation/optimizing-descriptions)** — Test and improve your skill's description so it activates on the right prompts.
* **[Specification](/specification)** — The complete format reference for `SKILL.md` files.
* **[Example skills](https://github.com/anthropics/skills)** — Browse real-world skills on GitHub.


# Using scripts in skills
Source: https://agentskills.io/skill-creation/using-scripts

How to run commands and bundle executable scripts in your skills.

Skills can instruct agents to run shell commands and bundle reusable scripts in a `scripts/` directory. This guide covers one-off commands, self-contained scripts with their own dependencies, and how to design script interfaces for agentic use.


## One-off commands

Source: https://agentskills.io/llms-full.txt#one-off-commands

When an existing package already does what you need, you can reference it directly in your `SKILL.md` instructions without a `scripts/` directory. Many ecosystems provide tools that auto-resolve dependencies at runtime.

<Tabs>
  <Tab title="uvx">
    [uvx](https://docs.astral.sh/uv/guides/tools/) runs Python packages in isolated environments with aggressive caching. It ships with [uv](https://docs.astral.sh/uv/).

    ```bash theme={null}
    uvx ruff@0.8.0 check .
    uvx black@24.10.0 .

bash theme={null}
    pipx run 'black==24.10.0' .
    pipx run 'ruff==0.8.0' check .

bash theme={null}
    npx eslint@9 --fix .
    npx create-vite@6 my-app

bash theme={null}
    bunx eslint@9 --fix .
    bunx create-vite@6 my-app

bash theme={null}
    deno run npm:create-vite@6 my-app
    deno run --allow-read npm:eslint@9 -- --fix .

bash theme={null}
    go run golang.org/x/tools/cmd/goimports@v0.28.0 .
    go run github.com/golangci/golangci-lint/cmd/golangci-lint@v1.62.0 run
    ```

    * Built into Go — no extra tooling needed.
    * Pin versions or use `@latest` to make the command explicit.
  </Tab>
</Tabs>

**Tips for one-off commands in skills:**

* **Pin versions** (e.g., `npx eslint@9.0.0`) so the command behaves the same over time.
* **State prerequisites** in your `SKILL.md` (e.g., "Requires Node.js 18+") rather than assuming the agent's environment has them. For runtime-level requirements, use the [`compatibility` frontmatter field](/specification#compatibility-field).
* **Move complex commands into scripts.** A one-off command works well when you're invoking a tool with a few flags. When a command grows complex enough that it's hard to get right on the first try, a tested script in `scripts/` is more reliable.


## Referencing scripts from `SKILL.md`

Source: https://agentskills.io/llms-full.txt#referencing-scripts-from-skill-md

Use **relative paths from the skill directory root** to reference bundled files. The agent resolves these paths automatically — no absolute paths needed.

List available scripts in your `SKILL.md` so the agent knows they exist:

```markdown SKILL.md theme={null}


## Available scripts

Source: https://agentskills.io/llms-full.txt#available-scripts

- **`scripts/validate.sh`** — Validates configuration files
- **`scripts/process.py`** — Processes input data

`markdown SKILL.md theme={null}


## Workflow

Source: https://agentskills.io/llms-full.txt#workflow

1. Run the validation script:

2. Process the results:

````

<Note>
  The same relative-path convention works in support files like `references/*.md` — script execution paths (in code blocks) are relative to the **skill directory root**, because the agent runs commands from there.
</Note>


## Self-contained scripts

Source: https://agentskills.io/llms-full.txt#self-contained-scripts

When you need reusable logic, bundle a script in `scripts/` that declares its own dependencies inline. The agent can run the script with a single command — no separate manifest file or install step required.

Several languages support inline dependency declarations:

<Tabs>
  <Tab title="Python">
    [PEP 723](https://peps.python.org/pep-0723/) defines a standard format for inline script metadata. Declare dependencies in a TOML block inside `# ///` markers:

    ```python scripts/extract.py theme={null}
    # /// script
    # dependencies = [
    #   "beautifulsoup4",
    # ]
    # ///

    from bs4 import BeautifulSoup

    html = '<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>'
    print(BeautifulSoup(html, "html.parser").select_one("p.info").get_text())

bash theme={null}
    uv run scripts/extract.py

typescript scripts/extract.ts theme={null}
    #!/usr/bin/env -S deno run

    import * as cheerio from "npm:cheerio@1.0.0";

    const html = `<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>`;
    const $ = cheerio.load(html);
    console.log($("p.info").text());

bash theme={null}
    deno run scripts/extract.ts

typescript scripts/extract.ts theme={null}
    #!/usr/bin/env bun

    import * as cheerio from "cheerio@1.0.0";

    const html = `<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>`;
    const $ = cheerio.load(html);
    console.log($("p.info").text());

bash theme={null}
    bun run scripts/extract.ts

ruby scripts/extract.rb theme={null}
    require 'bundler/inline'

    gemfile do
      source 'https://rubygems.org'
      gem 'nokogiri'
    end

    html = '<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>'
    doc = Nokogiri::HTML(html)
    puts doc.at_css('p.info').text

bash theme={null}
    ruby scripts/extract.rb
    ```

    * Pin versions explicitly (`gem 'nokogiri', '~> 1.16'`) — there is no lockfile.
    * An existing `Gemfile` or `BUNDLE_GEMFILE` env var in the working directory can interfere.
  </Tab>
</Tabs>


## Designing scripts for agentic use

Source: https://agentskills.io/llms-full.txt#designing-scripts-for-agentic-use

When an agent runs your script, it reads stdout and stderr to decide what to do next. A few design choices make scripts dramatically easier for agents to use.

### Avoid interactive prompts

This is a hard requirement of the agent execution environment. Agents operate in non-interactive shells — they cannot respond to TTY prompts, password dialogs, or confirmation menus. A script that blocks on interactive input will hang indefinitely.

Accept all input via command-line flags, environment variables, or stdin:

### Document usage with `--help`

`--help` output is the primary way an agent learns your script's interface. Include a brief description, available flags, and usage examples:

Keep it concise — the output enters the agent's context window alongside everything else it's working with.

### Write helpful error messages

When an agent gets an error, the message directly shapes its next attempt. An opaque "Error: invalid input" wastes a turn. Instead, say what went wrong, what was expected, and what to try:

### Use structured output

Prefer structured formats — JSON, CSV, TSV — over free-form text. Structured formats can be consumed by both the agent and standard tools (`jq`, `cut`, `awk`), making your script composable in pipelines.

**Separate data from diagnostics:** send structured data to stdout and progress messages, warnings, and other diagnostics to stderr. This lets the agent capture clean, parseable output while still having access to diagnostic information when needed.

### Further considerations

* **Idempotency.** Agents may retry commands. "Create if not exists" is safer than "create and fail on duplicate."
* **Input constraints.** Reject ambiguous input with a clear error rather than guessing. Use enums and closed sets where possible.
* **Dry-run support.** For destructive or stateful operations, a `--dry-run` flag lets the agent preview what will happen.
* **Meaningful exit codes.** Use distinct exit codes for different failure types (not found, invalid arguments, auth failure) and document them in your `--help` output so the agent knows what each code means.
* **Safe defaults.** Consider whether destructive operations should require explicit confirmation flags (`--confirm`, `--force`) or other safeguards appropriate to the risk level.
* **Predictable output size.** Many agent harnesses automatically truncate tool output beyond a threshold (e.g., 10-30K characters), potentially losing critical information. If your script might produce large output, default to a summary or a reasonable limit, and support flags like `--offset` so the agent can request more information when needed. Alternatively, if output is large and not amenable to pagination, require agents to pass an `--output` flag that specifies either an output file or `-` to explicitly opt in to stdout.


# Specification
Source: https://agentskills.io/specification

The complete format specification for Agent Skills.


## Directory structure

Source: https://agentskills.io/llms-full.txt#directory-structure

A skill is a directory containing, at minimum, a `SKILL.md` file:


## `SKILL.md` format

Source: https://agentskills.io/llms-full.txt#skill-md-format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Frontmatter

| Field           | Required | Constraints                                                                                                       |
| --------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| `name`          | Yes      | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen.             |
| `description`   | Yes      | Max 1024 characters. Non-empty. Describes what the skill does and when to use it.                                 |
| `license`       | No       | License name or reference to a bundled license file.                                                              |
| `compatibility` | No       | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.). |
| `metadata`      | No       | Arbitrary key-value mapping for additional metadata (a map from string keys to string values).                    |
| `allowed-tools` | No       | Space-separated string of pre-approved tools the skill may use. (Experimental)                                    |

<Card>
  **Minimal example:**

  ```markdown SKILL.md theme={null}
  ---
  name: skill-name
  description: A description of what this skill does and when to use it.
  ---

markdown SKILL.md theme={null}
  ---
  name: pdf-processing
  description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
  license: Apache-2.0
  metadata:
    author: example-org
    version: "1.0"
  ---

yaml theme={null}
  name: pdf-processing

yaml theme={null}
  name: data-analysis

yaml theme={null}
  name: code-review

yaml theme={null}
  name: PDF-Processing  # uppercase not allowed

yaml theme={null}
  name: -pdf  # cannot start with hyphen

yaml theme={null}
  name: pdf--processing  # consecutive hyphens not allowed

yaml theme={null}
  description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.

yaml theme={null}
  description: Helps with PDFs.

yaml theme={null}
  license: Proprietary. LICENSE.txt has complete terms

yaml theme={null}
  compatibility: Designed for Claude Code (or similar products)

yaml theme={null}
  compatibility: Requires git, docker, jq, and access to the internet

yaml theme={null}
  compatibility: Requires Python 3.14+ and uv

yaml theme={null}
  metadata:
    author: example-org
    version: "1.0"

yaml theme={null}
  allowed-tools: Bash(git:*) Bash(jq:*) Read
  ```
</Card>

### Body content

The Markdown body after the frontmatter contains the skill instructions. There are no format restrictions. Write whatever helps agents perform the task effectively.

Recommended sections:

* Step-by-step instructions
* Examples of inputs and outputs
* Common edge cases

Note that the agent will load this entire file once it's decided to activate a skill. Consider splitting longer `SKILL.md` content into referenced files.


## Optional directories

Source: https://agentskills.io/llms-full.txt#optional-directories

A skill directory may contain any files and directories beyond the required `SKILL.md`. The conventions below are recommendations for organizing common types of content.

### `scripts/`

Contains executable code that agents can run. Scripts should:

* Be self-contained or clearly document dependencies
* Include helpful error messages
* Handle edge cases gracefully

Supported languages depend on the agent implementation. Common options include Python, Bash, and JavaScript.

### `references/`

Contains additional documentation that agents can read when needed:

* `REFERENCE.md` - Detailed technical reference
* `FORMS.md` - Form templates or structured data formats
* Domain-specific files (`finance.md`, `legal.md`, etc.)

Keep individual [reference files](#file-references) focused. Agents load these on demand, so smaller files mean less use of context.

### `assets/`

Contains static resources:

* Templates (document templates, configuration templates)
* Images (diagrams, examples)
* Data files (lookup tables, schemas)


## Progressive disclosure

Source: https://agentskills.io/llms-full.txt#progressive-disclosure

Agents load skills *progressively*, pulling in more detail only as a task calls for it. Skills should be structured to take advantage of this:

1. **Metadata** (\~100 tokens): The `name` and `description` fields are loaded at startup for all skills
2. **Instructions** (\< 5000 tokens recommended): The full `SKILL.md` body is loaded when the skill is activated
3. **Resources** (as needed): Files (e.g. those in `scripts/`, `references/`, or `assets/`) are loaded only when required

Keep your main `SKILL.md` under 500 lines. Move detailed reference material to separate files.


## File references

Source: https://agentskills.io/llms-full.txt#file-references

When referencing other files in your skill, use relative paths from the skill root:

```markdown SKILL.md theme={null}
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains.


## Validation

Source: https://agentskills.io/llms-full.txt#validation

Use the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) reference library to validate your skills:

```bash theme={null}
skills-ref validate ./my-skill
```

This checks that your `SKILL.md` frontmatter is valid and follows all naming conventions.
