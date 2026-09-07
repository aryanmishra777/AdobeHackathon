# platform.claude.com Documentation (Part 12 of 35)

## Old patterns

Source: https://platform.claude.com/llms-full.txt#old-patterns

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>

The v1 API used: `api.example.com/v1/messages`

This endpoint is no longer supported.
</details>
```

The old patterns section provides historical context without cluttering the main content.

### Use consistent terminology

Choose one term and use it throughout the Skill:

**Good - Consistent:**

* Always "API endpoint"
* Always "field"
* Always "extract"

**Bad - Inconsistent:**

* Mix "API endpoint", "URL", "API route", "path"
* Mix "field", "box", "element", "control"
* Mix "extract", "pull", "get", "retrieve"

Consistency helps Claude parse and follow instructions.


## Common patterns

Source: https://platform.claude.com/llms-full.txt#common-patterns-3

### Template pattern

Provide templates for output format. Match the level of strictness to your needs.

**For strict requirements** (such as API responses or data formats):

````markdown


## Report structure

Source: https://platform.claude.com/llms-full.txt#report-structure

ALWAYS use this exact template structure:

```markdown
# [Analysis Title]


## Executive summary

Source: https://platform.claude.com/llms-full.txt#executive-summary

[One-paragraph overview of key findings]


## Key findings

Source: https://platform.claude.com/llms-full.txt#key-findings

- Finding 1 with supporting data
- Finding 2 with supporting data
- Finding 3 with supporting data


## Recommendations

Source: https://platform.claude.com/llms-full.txt#recommendations

1. Specific actionable recommendation
2. Specific actionable recommendation

`

**For flexible guidance** (when adaptation is useful):

````markdown


## Report structure

Source: https://platform.claude.com/llms-full.txt#report-structure-2

Here is a sensible default format, but use your best judgment based on the analysis:

```markdown
# [Analysis Title]


## Executive summary

Source: https://platform.claude.com/llms-full.txt#executive-summary-2

[Overview]


## Key findings

Source: https://platform.claude.com/llms-full.txt#key-findings-2

[Adapt sections based on what you discover]


## Recommendations

Source: https://platform.claude.com/llms-full.txt#recommendations-2

[Tailor to the specific context]

`

### Examples pattern

For Skills where output quality depends on seeing examples, provide input/output pairs just like in regular prompting:

````markdown


## Commit message format

Source: https://platform.claude.com/llms-full.txt#commit-message-format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:

**Example 3:**
Input: Updated dependencies and refactored error handling
Output:

Follow this style: type(scope): brief description, then detailed explanation.
`

markdown


## Document modification workflow

Source: https://platform.claude.com/llms-full.txt#document-modification-workflow

1. Determine the modification type:

   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow:
   - Use docx-js library
   - Build document from scratch
   - Export to .docx format

3. Editing workflow:
   - Unpack existing document
   - Modify XML directly
   - Validate after each change
   - Repack when complete
```

<Tip>
  If workflows become large or complicated with many steps, consider pushing them into separate files and tell Claude to read the appropriate file based on the task at hand.
</Tip>


## Evaluation and iteration

Source: https://platform.claude.com/llms-full.txt#evaluation-and-iteration

### Build evaluations first

**Create evaluations BEFORE writing extensive documentation.** This ensures your Skill solves real problems rather than documenting imagined ones.

**Evaluation-driven development:**

1. **Identify gaps:** Run Claude on representative tasks without a Skill. Document specific failures or missing context
2. **Create evaluations:** Build three scenarios that test these gaps
3. **Establish baseline:** Measure Claude's performance without the Skill
4. **Write minimal instructions:** Create just enough content to address the gaps and pass evaluations
5. **Iterate:** Execute evaluations, compare against baseline, and refine

This approach ensures you're solving actual problems rather than anticipating requirements that may never materialize.

**Evaluation structure:**

<Note>
  This example demonstrates a data-driven evaluation with a simple testing rubric. There is not currently a built-in way to run these evaluations. Users can create their own evaluation system. Evaluations are your source of truth for measuring Skill effectiveness.
</Note>

### Develop Skills iteratively with Claude

The most effective Skill development process involves Claude itself. Work with one instance of Claude ("Claude A") to create a Skill that is used by other instances ("Claude B"). Claude A helps you design and refine instructions, while Claude B tests them in real tasks. This works because Claude models understand both how to write effective agent instructions and what information agents need.

**Creating a new Skill:**

1. **Complete a task without a Skill:** Work through a problem with Claude A using normal prompting. As you work, you'll naturally provide context, explain preferences, and share procedural knowledge. Notice what information you repeatedly provide.

2. **Identify the reusable pattern:** After completing the task, identify what context you provided that would be useful for similar future tasks.

   **Example:** If you worked through a BigQuery analysis, you might have provided table names, field definitions, filtering rules (such as "always exclude test accounts"), and common query patterns.

3. **Ask Claude A to create a Skill:** "Create a Skill that captures this BigQuery analysis pattern we just used. Include the table schemas, naming conventions, and the rule about filtering test accounts."

   <Tip>
     Claude models understand the Skill format and structure natively. You don't need special system prompts or a "writing skills" skill to get Claude to help create Skills. Simply ask Claude to create a Skill and it generates properly structured SKILL.md content with appropriate frontmatter and body content.
   </Tip>

4. **Review for conciseness:** Check that Claude A hasn't added unnecessary explanations. Ask: "Remove the explanation about what win rate means - Claude already knows that."

5. **Improve information architecture:** Ask Claude A to organize the content more effectively. For example: "Organize this so the table schema is in a separate reference file. We might add more tables later."

6. **Test on similar tasks:** Use the Skill with Claude B (a fresh instance with the Skill loaded) on related use cases. Observe whether Claude B finds the right information, applies rules correctly, and handles the task successfully.

7. **Iterate based on observation:** If Claude B struggles or misses something, return to Claude A with specifics: "When Claude used this Skill, it forgot to filter by date for Q4. Should we add a section about date filtering patterns?"

**Iterating on existing Skills:**

The same hierarchical pattern continues when improving Skills. You alternate between:

* **Working with Claude A** (the expert who helps refine the Skill)
* **Testing with Claude B** (the agent using the Skill to perform real work)
* **Observing Claude B's behavior** and bringing insights back to Claude A

1. **Use the Skill in real workflows:** Give Claude B (with the Skill loaded) actual tasks, not test scenarios

2. **Observe Claude B's behavior:** Note where it struggles, succeeds, or makes unexpected choices

   **Example observation:** "When I asked Claude B for a regional sales report, it wrote the query but forgot to filter out test accounts, even though the Skill mentions this rule."

3. **Return to Claude A for improvements:** Share the current SKILL.md and describe what you observed. Ask: "I noticed Claude B forgot to filter test accounts when I asked for a regional report. The Skill mentions filtering, but maybe it's not prominent enough?"

4. **Review Claude A's suggestions:** Claude A might suggest reorganizing to make rules more prominent, using stronger language such as "MUST filter" instead of "always filter," or restructuring the workflow section.

5. **Apply and test changes:** Update the Skill with Claude A's refinements, then test again with Claude B on similar requests

6. **Repeat based on usage:** Continue this observe-refine-test cycle as you encounter new scenarios. Each iteration improves the Skill based on real agent behavior, not assumptions.

**Gathering team feedback:**

1. Share Skills with teammates and observe their usage
2. Ask: Does the Skill activate when expected? Are instructions clear? What's missing?
3. Incorporate feedback to address gaps in your own usage patterns

**Why this approach works:** Claude A understands agent needs, you provide domain expertise, Claude B reveals gaps through real usage, and iterative refinement improves Skills based on observed behavior rather than assumptions.

### Observe how Claude navigates Skills

As you iterate on Skills, pay attention to how Claude actually uses them in practice. Watch for:

* **Unexpected exploration paths:** Does Claude read files in an order you didn't anticipate? This might indicate your structure isn't as intuitive as you thought
* **Missed connections:** Does Claude fail to follow references to important files? Your links might need to be more explicit or prominent
* **Overreliance on certain sections:** If Claude repeatedly reads the same file, consider whether that content should be in the main SKILL.md instead
* **Ignored content:** If Claude never accesses a bundled file, it might be unnecessary or poorly signaled in the main instructions

Iterate based on these observations rather than assumptions. The 'name' and 'description' in your Skill's metadata are particularly critical. Claude uses these when determining whether to trigger the Skill in response to the current task. Make sure they clearly describe what the Skill does and when it should be used.


## Anti-patterns to avoid

Source: https://platform.claude.com/llms-full.txt#anti-patterns-to-avoid

### Avoid Windows-style paths

Always use forward slashes in file paths, even on Windows:

* ✓ **Good:** `scripts/helper.py`, `reference/guide.md`
* ✗ **Avoid:** `scripts\helper.py`, `reference\guide.md`

Unix-style paths work across all platforms, while Windows-style paths cause errors on Unix systems.

### Avoid offering too many options

Don't present multiple approaches unless necessary:

`

python
import pdfplumber

`


## Advanced: Skills with executable code

Source: https://platform.claude.com/llms-full.txt#advanced-skills-with-executable-code

The following sections focus on Skills that include executable scripts. If your Skill uses only markdown instructions, skip to [Checklist for effective Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#checklist-for-effective-skills).

### Solve, don't defer

When writing scripts for Skills, handle error conditions rather than deferring to Claude.

**Good example: Handle errors explicitly:**

**Bad example: Defer to Claude:**

Configuration parameters should also be justified and documented to avoid "voodoo constants" (Ousterhout's law). If you don't know the right value, how will Claude determine it?

**Good example: Self-documenting:**

**Bad example: Magic numbers:**

### Provide utility scripts

Even if Claude could write a script, pre-made scripts offer advantages:

**Benefits of utility scripts:**

* More reliable than generated code
* Save tokens (no need to include code in context)
* Save time (no code generation required)
* Ensure consistency across uses

![Bundling executable scripts alongside instruction files](https://platform.claude.com/docs/images/agent-skills-executable-scripts.png)

The preceding diagram shows how executable scripts work alongside instruction files. The instruction file (forms.md) references the script, and Claude can execute it without loading its contents into context.

**Important distinction:** Make clear in your instructions whether Claude should:

* **Execute the script** (most common): "Run `analyze_form.py` to extract fields"
* **Read it as reference** (for complex logic): "See `analyze_form.py` for the field extraction algorithm"

For most utility scripts, execution is preferred because it's more reliable and efficient. See the following [Runtime environment](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#runtime-environment) section for details on how script execution works.

**Example:**

````markdown


## Utility scripts

Source: https://platform.claude.com/llms-full.txt#utility-scripts

**analyze_form.py**: Extract all form fields from PDF

Output format:

**validate_boxes.py**: Check for overlapping bounding boxes

**fill_form.py**: Apply field values to PDF

`

`markdown


## Form layout analysis

Source: https://platform.claude.com/llms-full.txt#form-layout-analysis

1. Convert PDF to images:

2. Analyze each page image to identify form fields
3. Claude can see field locations and types visually
`

markdown
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
Use the GitHub:create_issue tool to create issues.

`markdown
**Bad example: Assumes installation**:
"Use the pdf library to process the file."

**Good example: Explicit about dependencies**:
"Install required package: `pip install pypdf`

Then use it:

"
````


## Technical notes

Source: https://platform.claude.com/llms-full.txt#technical-notes

### YAML frontmatter requirements

The SKILL.md frontmatter requires `name` and `description` fields with specific validation rules:

* `name`: Maximum 64 characters, lowercase letters/numbers/hyphens only, no XML tags, no reserved words
* `description`: Maximum 1,024 characters, non-empty, no XML tags

See the [Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure) for complete structure details.

### Token budgets

Keep SKILL.md body under 500 lines for optimal performance. If your content exceeds this, split it into separate files using the progressive disclosure patterns described earlier. For architectural details, see the [Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work).


## Checklist for effective Skills

Source: https://platform.claude.com/llms-full.txt#checklist-for-effective-skills

Before sharing a Skill, verify:

### Core quality

* [ ] Description is specific and includes key terms
* [ ] Description includes both what the Skill does and when to use it
* [ ] SKILL.md body is under 500 lines
* [ ] Additional details are in separate files (if needed)
* [ ] No time-sensitive information (or in "old patterns" section)
* [ ] Consistent terminology throughout
* [ ] Examples are concrete, not abstract
* [ ] File references are one level deep
* [ ] Progressive disclosure used appropriately
* [ ] Workflows have clear steps

### Code and scripts

* [ ] Scripts solve problems rather than defer to Claude
* [ ] Error handling is explicit and helpful
* [ ] No "voodoo constants" (all values justified)
* [ ] Required packages listed in instructions and verified as available
* [ ] Scripts have clear documentation
* [ ] No Windows-style paths (all forward slashes)
* [ ] Validation/verification steps for critical operations
* [ ] Feedback loops included for quality-critical tasks

### Testing

* [ ] At least three evaluations created
* [ ] Tested with Haiku, Sonnet, and Opus
* [ ] Tested with real usage scenarios
* [ ] Team feedback incorporated (if applicable)


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-58

<CardGroup cols={2}>
  <Card title="Get started with Agent Skills" icon="rocket" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart">
    Create your first Skill
  </Card>

  <Card title="Use Skills in Claude Code" icon="terminal" href="https://code.claude.com/docs/en/skills">
    Create and manage Skills in Claude Code
  </Card>

  <Card title="Use Skills with the API" icon="code" href="https://platform.claude.com/docs/en/build-with-claude/skills-guide">
    Upload and use Skills programmatically
  </Card>
</CardGroup>


---
title: Skills for enterprise
url: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise
description: Governance, security review, evaluation, and organizational guidance for deploying Agent Skills at enterprise scale.
---

This guide is for enterprise admins and architects who need to govern Agent Skills across an organization. It covers how to vet, evaluate, deploy, and manage Skills at scale. For authoring guidance, see [best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). For architecture details, see the [Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).


## Security review and vetting

Source: https://platform.claude.com/llms-full.txt#security-review-and-vetting

Deploying Skills in an enterprise requires answering two distinct questions:

1. **Are Skills safe in general?** See the [security considerations](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#security-considerations) section in the overview for platform-level security details.
2. **How do I vet a specific Skill?** Use the following risk assessment and review checklist.

### Risk tier assessment

Evaluate each Skill against these risk indicators before approving deployment:

| Risk indicator           | What to look for                                                                                     | Concern level                                           |
| ------------------------ | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Code execution           | Scripts in the Skill directory (`*.py`, `*.sh`, `*.js`)                                              | High: scripts run with full environment access          |
| Instruction manipulation | Directives to ignore safety rules, hide actions from users, or alter Claude's behavior conditionally | High: can bypass security controls                      |
| MCP server references    | Instructions referencing MCP tools (`ServerName:tool_name`)                                          | High: extends access beyond the Skill itself            |
| Network access patterns  | URLs, API endpoints, `fetch`, `curl`, or `requests` calls                                            | High: potential data exfiltration vector                |
| Hardcoded credentials    | API keys, tokens, or passwords in Skill files or scripts                                             | High: secrets exposed in Git history and context window |
| Filesystem access scope  | Paths outside the Skill directory, broad glob patterns, path traversal (`../`)                       | Medium: may access unintended data                      |
| Tool invocations         | Instructions directing Claude to use bash, file operations, or other tools                           | Medium: review what operations are performed            |

### Review checklist

Before deploying any Skill from a third party or internal contributor, complete these steps:

1. **Read all Skill directory content.** Review SKILL.md, all referenced markdown files, and any bundled scripts or resources.
2. **Verify script behavior matches stated purpose.** Run scripts in a sandboxed environment and confirm outputs align with the Skill's description.
3. **Check for adversarial instructions.** Look for directives that tell Claude to ignore safety rules, hide actions from users, exfiltrate data through responses, or alter behavior based on specific inputs.
4. **Check for external URL fetches or network calls.** Search scripts and instructions for network access patterns (`http`, `requests.get`, `urllib`, `curl`, `fetch`).
5. **Verify no hardcoded credentials.** Check for API keys, tokens, or passwords in Skill files. Credentials should use environment variables or secure credential stores, never appear in Skill content.
6. **Identify tools and commands the Skill instructs Claude to invoke.** List all bash commands, file operations, and tool references. Consider the combined risk when a Skill uses both file-read and network tools together.
7. **Confirm redirect destinations.** If the Skill references external URLs, verify they point to expected domains.
8. **Verify no data exfiltration patterns.** Look for instructions that read sensitive data and then write, send, or encode it for external transmission, including through Claude's conversational responses.

<Warning>
  Never deploy Skills from untrusted sources without a full audit. A malicious Skill can direct Claude to execute arbitrary code, access sensitive files, or transmit data externally. Treat Skill installation with the same rigor as installing software on production systems.
</Warning>

### Skill content scanning

Claude Enterprise organizations can turn on automated security scanning for custom Skills in claude.ai and Claude Cowork. After you turn on **Skill and plugin security scanning** at [claude.ai > Organization settings > Skills](https://claude.ai/admin-settings/skills), Skills that members then upload or edit in claude.ai or Cowork are scanned for signs of malicious behavior, such as hidden code execution, sending your data to an outside service, or instructions that tamper with Claude's safeguards. A Skill that fails the scan, or whose scan hasn't finished, is blocked from use. A Skill that passes with a warning stays usable behind a caution notice. If scanning is available to your organization, turn it on. It complements, but doesn't replace, the [review checklist](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise#review-checklist).

Scanning doesn't cover the Claude API. Skills you upload through the Skills API (`/v1/skills`), including from the Claude Console, aren't scanned, so for API deployments, rely on the review checklist and [version pinning](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise#versioning-strategy). Scanning also doesn't apply to Skills that were already in your organization when you turned it on, or to organizations with certain data handling configurations, such as customer-managed encryption keys (CMEK), zero data retention (ZDR), or HIPAA readiness. For setup steps, exclusions, and result types, see [Get started with skill and plugin scanning](https://support.claude.com/en/articles/15927065-get-started-with-skill-and-plugin-scanning) in the Claude Help Center.


## Evaluating Skills before deployment

Source: https://platform.claude.com/llms-full.txt#evaluating-skills-before-deployment

Skills can degrade agent performance if they trigger incorrectly, conflict with other Skills, or provide poor instructions. Require evaluation before any production deployment.

### What to evaluate

Establish approval gates for these dimensions before deploying any Skill:

| Dimension             | What it measures                                                                    | Example failure                                                                            |
| --------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Triggering accuracy   | Does the Skill activate for the right queries and stay inactive for unrelated ones? | Skill triggers on every spreadsheet mention, even when the user just wants to discuss data |
| Isolation behavior    | Does the Skill work correctly on its own?                                           | Skill references files that don't exist in its directory                                   |
| Coexistence           | Does adding this Skill degrade other Skills?                                        | New Skill's description is too broad, stealing triggers from existing Skills               |
| Instruction following | Does Claude follow the Skill's instructions accurately?                             | Claude skips validation steps or uses wrong libraries                                      |
| Output quality        | Does the Skill produce correct, useful results?                                     | Generated reports have formatting errors or missing data                                   |

### Evaluation requirements

Require Skill authors to submit evaluation suites with 3–5 representative queries per Skill, covering cases where the Skill should trigger, should not trigger, and ambiguous edge cases. Require testing across the models your organization uses (Haiku, Sonnet, Opus), because Skill effectiveness varies by model.

For detailed guidance on building evaluations, see [evaluation and iteration](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#evaluation-and-iteration) in best practices. For general evaluation methodology, see [develop test cases](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests).

### Using evaluations for lifecycle decisions

Evaluation results signal when to act:

* **Declining trigger accuracy:** Update the Skill's description or instructions
* **Coexistence conflicts:** Consolidate overlapping Skills or narrow descriptions
* **Consistently low output quality:** Rewrite instructions or add validation steps
* **Persistent failures across updates:** Deprecate the Skill


## Skill lifecycle management

Source: https://platform.claude.com/llms-full.txt#skill-lifecycle-management

<Steps>
  <Step title="Plan">
    Identify workflows that are repetitive, error-prone, or require specialized knowledge. Map these to organizational roles and determine which are candidates for Skills.
  </Step>

  <Step title="Create and review">
    Ensure the Skill author follows [best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). Require a security review using the [review checklist](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise#review-checklist). Require an evaluation suite before approval. Establish separation of duties: Skill authors should not be their own reviewers.
  </Step>

  <Step title="Test">
    Require evaluations in isolation (Skill alone) and alongside existing Skills (coexistence testing). Verify triggering accuracy, output quality, and absence of regressions across your active Skill set before approving for production.
  </Step>

  <Step title="Deploy">
    Upload through the Skills API for workspace-wide access. See [Using Skills with the API](https://platform.claude.com/docs/en/build-with-claude/skills-guide) for upload and version management. Document the Skill in your internal registry with purpose, owner, and version.
  </Step>

  <Step title="Monitor">
    Track usage patterns and collect feedback from users. Rerun evaluations periodically to detect drift or regressions as workflows and models evolve. Usage analytics are not currently available through the Skills API. Implement application-level logging to track which Skills are included in requests.
  </Step>

  <Step title="Iterate or deprecate">
    Require the full evaluation suite to pass before promoting new versions. Update Skills when workflows change or evaluation scores decline. Deprecate Skills when evaluations consistently fail or the workflow is retired.
  </Step>
</Steps>


## Organizing Skills at scale

Source: https://platform.claude.com/llms-full.txt#organizing-skills-at-scale

### Recall limits

As a general guideline, limit the number of Skills loaded simultaneously to maintain reliable recall accuracy. Each Skill's metadata (name and description) competes for attention in the system prompt. With too many Skills active, Claude may fail to select the right Skill or miss relevant ones entirely. Use your evaluation suite to measure recall accuracy as you add Skills, and stop adding when performance degrades.

Note that API requests support a maximum of 20 Skills for each request (see [Using Skills with the API](https://platform.claude.com/docs/en/build-with-claude/skills-guide)). If a role requires more Skills than a single request supports, consider consolidating narrow Skills into broader ones or routing requests to different Skill sets based on task type.

### Start specific, consolidate later

Encourage teams to start with narrow, workflow-specific Skills rather than broad, multipurpose ones. As patterns emerge across your organization, consolidate related Skills into role-based bundles.

<Tip>
  Use evaluations to decide when to consolidate. Merge narrow Skills into a broader one only when the consolidated Skill's evaluations confirm equivalent performance to the individual Skills it replaces.
</Tip>

**Example progression:**

* Start: `formatting-sales-reports`, `querying-pipeline-data`, `updating-crm-records`
* Consolidate: `sales-operations` (when evals confirm equivalent performance)

### Naming and cataloging

Use consistent naming conventions across your organization. The [naming conventions](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#naming-conventions) section in best practices provides formatting guidance.

Maintain an internal registry for each Skill with:

* **Purpose:** What workflow the Skill supports
* **Owner:** Team or individual responsible for maintenance
* **Version:** Current deployed version
* **Dependencies:** MCP servers, packages, or external services required
* **Evaluation status:** Last evaluation date and results

### Role-based bundles

Group Skills by organizational role to keep each user's active Skill set focused:

* **Sales team:** CRM operations, pipeline reporting, proposal generation
* **Engineering:** Code review, deployment workflows, incident response
* **Finance:** Report generation, data validation, audit preparation

Each role-based bundle should contain only the Skills relevant to that role's daily workflows.


## Distribution and version control

Source: https://platform.claude.com/llms-full.txt#distribution-and-version-control

### Source control

Store Skill directories in Git for history tracking, code review through pull requests, and rollback capability. Each Skill directory (containing SKILL.md and any bundled files) maps naturally to a Git-tracked folder.

### API-based distribution

The Skills API provides workspace-scoped distribution. Skills uploaded through the API are available to all workspace members. See [Using Skills with the API](https://platform.claude.com/docs/en/build-with-claude/skills-guide) for upload, versioning, and management endpoints.

### Versioning strategy

* **Production:** Pin Skills to specific versions. If you omit `version`, requests use the latest version, so a new version uploaded by anyone in the workspace immediately changes what production agents run. Run the full evaluation suite before promoting a new version. Treat every update as a new deployment requiring full security review.
* **Development and testing:** Use latest versions to validate changes before production promotion.
* **Rollback plan:** Maintain the previous version as a fallback. If a new version fails evaluations in production, revert to the last known-good version immediately.
* **Integrity verification:** Compute checksums of reviewed Skills and verify them at deployment time. Use signed commits in your Skill repository to ensure provenance.

### Cross-surface considerations

<Warning>
  Custom Skills do not sync across surfaces. Skills uploaded to the API are not available on claude.ai or in Claude Code, and vice versa. Each surface requires separate uploads and management.
</Warning>

Maintain Skill source files in Git as the single source of truth. If your organization deploys Skills across multiple surfaces, implement your own synchronization process to keep them consistent. For full details, see [cross-surface availability](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#cross-surface-availability).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-59

<CardGroup cols={2}>
  <Card title="Agent Skills overview" icon="book-open" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview">
    Architecture and platform details
  </Card>

  <Card title="Best practices" icon="lightbulb" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices">
    Authoring guidance for Skill creators
  </Card>

  <Card title="Using Skills with the API" icon="code" href="https://platform.claude.com/docs/en/build-with-claude/skills-guide">
    Upload and manage Skills programmatically
  </Card>
</CardGroup>


---
title: Using Agent Skills with the API
url: https://platform.claude.com/docs/en/build-with-claude/skills-guide
description: Learn how to use Agent Skills to extend Claude's capabilities through the API.
---

Agent Skills extend Claude's capabilities through organized folders of instructions, scripts, and resources. This guide shows you how to use both pre-built and custom Skills with the Claude API.

<Note>
  For complete API reference including request/response schemas and all parameters, see:

  * [Skill Management API Reference](https://platform.claude.com/docs/en/api/skills/list) - CRUD operations for Skills
  * [Skill Versions API Reference](https://platform.claude.com/docs/en/api/skills/versions/list) - Version management
</Note>

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>


## Quick links

Source: https://platform.claude.com/llms-full.txt#quick-links

<CardGroup cols={2}>
  <Card title="Get started with Agent Skills in the API" icon="rocket" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart">
    Learn how to use Agent Skills to create documents with the Claude API in under 10 minutes.
  </Card>

  <Card title="Skill authoring best practices" icon="hammer" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices">
    Learn how to write effective Skills that Claude can discover and use successfully.
  </Card>
</CardGroup>


## Overview

Source: https://platform.claude.com/llms-full.txt#overview-3

<Note>
  For a detailed look at the architecture and real-world applications of Agent Skills, read the engineering blog post: [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).
</Note>

Skills integrate with the Messages API through the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool). Whether using pre-built Skills managed by Anthropic or custom Skills you've uploaded, the integration shape is identical: both require code execution and use the same `container` structure.

### Using Skills

Skills integrate identically in the Messages API regardless of source. You specify Skills in the `container` parameter with a `skill_id`, `type`, and optional `version`, and they run in the code execution environment.

You can use Skills from two sources:

| Aspect             | Anthropic Skills                           | Custom Skills                                                                                     |
| ------------------ | ------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| **Type value**     | `anthropic`                                | `custom`                                                                                          |
| **Skill IDs**      | Short names: `pptx`, `xlsx`, `docx`, `pdf` | Generated: `skill_01AbCdEfGhIjKlMnOpQrStUv`                                                       |
| **Version format** | Date-based: `20251013` or `latest`         | Version ID: `skver_01AbCdEfGhIjKlMnOpQrStUv` or `latest`                                          |
| **Management**     | Pre-built and maintained by Anthropic      | Upload and manage through the [Skills API](https://platform.claude.com/docs/en/api/skills/create) |
| **Availability**   | Available to all users                     | Private to your workspace                                                                         |

Both skill sources are returned by the [List Skills endpoint](https://platform.claude.com/docs/en/api/skills/list) (use the `source` parameter to filter). The integration shape and execution environment are identical. The only difference is where the Skills come from and how they're managed.

### Prerequisites

To use Skills, you need:

1. **Claude API key** from the [Claude Console](https://platform.claude.com/settings/keys)
2. **[Code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)** enabled in your requests

Skills require the code execution tool, so use a model from its [model compatibility list](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#compatibility).

***


## Using Skills in Messages

Source: https://platform.claude.com/llms-full.txt#using-skills-in-messages

### Container parameter

Skills are specified using the `container` parameter in the Messages API. You can include up to 20 Skills for each request.

The structure is identical for both Anthropic and custom Skills. Specify the required `type` and `skill_id`, and optionally include `version` to pin to a specific version:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "container": {
        "skills": [
          {
            "type": "anthropic",
            "skill_id": "pptx",
            "version": "latest"
          }
        ]
      },
      "messages": [{
        "role": "user",
        "content": "Create a presentation about renewable energy"
      }],
      "tools": [{
        "type": "code_execution_20250825",
        "name": "code_execution"
      }]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: anthropic
        skill_id: pptx
        version: latest
  messages:
    - role: user
      content: Create a presentation about renewable energy
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container={
          "skills": [{"type": "anthropic", "skill_id": "pptx", "version": "latest"}]
      },
      messages=[
          {"role": "user", "content": "Create a presentation about renewable energy"}
      ],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [
        {
          type: "anthropic",
          skill_id: "pptx",
          version: "latest"
        }
      ]
    },
    messages: [
      {
        role: "user",
        content: "Create a presentation about renewable energy"
      }
    ],
    tools: [
      {
        type: "code_execution_20250825",
        name: "code_execution"
      }
    ]
  });

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Container = new ContainerParams
      {
          Skills =
          [
              new SkillParams
              {
                  Type = SkillParamsType.Anthropic,
                  SkillID = "pptx",
                  Version = "latest",
              },
          ],
      },
      Messages = [new() { Role = Role.User, Content = "Create a presentation about renewable energy" }],
      Tools = [new CodeExecutionTool20250825()],
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     "claude-opus-5",
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "pptx",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Create a presentation about renewable energy")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.messages.ContainerParams;
  import com.anthropic.models.messages.SkillParams;
  import com.anthropic.models.messages.CodeExecutionTool20250825;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .container(ContainerParams.builder()
              .addSkill(SkillParams.builder()
                  .type(SkillParams.Type.ANTHROPIC)
                  .skillId("pptx")
                  .version("latest")
                  .build())
              .build())
          .addUserMessage("Create a presentation about renewable energy")
          .addTool(CodeExecutionTool20250825.builder().build())
          .build();

      Message response = client.messages().create(params);
      System.out.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Create a presentation about renewable energy']
      ],
      model: 'claude-opus-5',
      container: [
          'skills' => [
              [
                  'type' => 'anthropic',
                  'skillID' => 'pptx',
                  'version' => 'latest'
              ]
          ]
      ],
      tools: [
          ['type' => 'code_execution_20250825', 'name' => 'code_execution']
      ]
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [
        {
          type: "anthropic",
          skill_id: "pptx",
          version: "latest"
        }
      ]
    },
    messages: [
      { role: "user", content: "Create a presentation about renewable energy" }
    ],
    tools: [
      { type: "code_execution_20250825", name: "code_execution" }
    ]
  )
  puts message

bash cURL
  # Step 1: Use a Skill to create a file
  RESPONSE=$(curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "container": {
        "skills": [
          {"type": "anthropic", "skill_id": "xlsx", "version": "latest"}
        ]
      },
      "messages": [{
        "role": "user",
        "content": "Create an Excel file with a simple budget spreadsheet"
      }],
      "tools": [{
        "type": "code_execution_20250825",
        "name": "code_execution"
      }]
    }')

  # Step 2: Extract file_id from response (using jq)
  FILE_ID=$(echo "$RESPONSE" | jq -r '.content[] | select(.type=="bash_code_execution_tool_result") | .content | select(.type=="bash_code_execution_result") | .content[] | select(.file_id) | .file_id')

  # Step 3: Get filename from metadata
  FILENAME=$(curl "https://api.anthropic.com/v1/files/$FILE_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" | jq -r '.filename')

  # Step 4: Download the file using Files API
  curl "https://api.anthropic.com/v1/files/$FILE_ID/content" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    --output "$FILENAME"

  echo "Downloaded: $FILENAME"

bash CLI
  # Step 1: Use the xlsx Skill to create a file
  # Step 2: Extract file_id from the response with --transform (GJSON path)
  FILE_ID=$(ant messages create \
    --transform 'content.#.content.content.#.file_id|@flatten|0' \
    --raw-output <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: anthropic
        skill_id: xlsx
        version: latest
  messages:
    - role: user
      content: Create an Excel file with a simple budget spreadsheet
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML
  )

  # Step 3: Get the filename from file metadata
  FILENAME=$(ant files retrieve-metadata \
    --file-id "$FILE_ID" \
    --transform filename \
    --raw-output)

  # Step 4: Download the file using Files API
  ant files download --file-id "$FILE_ID" --output "$FILENAME" > /dev/null

  printf 'Downloaded: %s\n' "$FILENAME"

python Python
  client = anthropic.Anthropic()

  # Step 1: Use a Skill to create a file
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container={
          "skills": [{"type": "anthropic", "skill_id": "xlsx", "version": "latest"}]
      },
      messages=[
          {
              "role": "user",
              "content": "Create an Excel file with a simple budget spreadsheet",
          }
      ],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )


  # Step 2: Extract file IDs from the response
  def extract_file_ids(response):
      file_ids = []
      for item in response.content:
          if item.type == "bash_code_execution_tool_result":
              content_item = item.content
              if content_item.type == "bash_code_execution_result":
                  # each content item is a bash_code_execution_output block carrying a file_id
                  for file in content_item.content:
                      file_ids.append(file.file_id)
      return file_ids


  # Step 3: Download the file using Files API
  for file_id in extract_file_ids(response):
      file_metadata = client.files.retrieve_metadata(file_id=file_id)
      file_content = client.files.download(file_id=file_id)

      # Step 4: Save to disk
      file_content.write_to_file(file_metadata.filename)
      print(f"Downloaded: {file_metadata.filename}")

typescript TypeScript
  import { writeFile } from "node:fs/promises";

  const client = new Anthropic();

  // Step 1: Use a Skill to create a file
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [{ type: "anthropic", skill_id: "xlsx", version: "latest" }]
    },
    messages: [
      {
        role: "user",
        content: "Create an Excel file with a simple budget spreadsheet"
      }
    ],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });

  // Step 2: Extract file IDs from the response
  const fileIds: string[] = [];
  for (const block of response.content) {
    if (
      block.type === "bash_code_execution_tool_result" &&
      block.content.type === "bash_code_execution_result"
    ) {
      for (const outputBlock of block.content.content) {
        fileIds.push(outputBlock.file_id);
      }
    }
  }

  // Step 3: Download each file and save to disk
  for (const fileId of fileIds) {
    const fileMetadata = await client.files.retrieveMetadata(fileId);
    const fileResponse = await client.files.download(fileId);

    await writeFile(fileMetadata.filename, Buffer.from(await fileResponse.arrayBuffer()));
    console.log(`Downloaded: ${fileMetadata.filename}`);
  }

csharp C#
  AnthropicClient client = new();

  // Step 1: Use a Skill to create a file
  var parameters = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Container = new ContainerParams
      {
          Skills =
          [
              new SkillParams
              {
                  Type = SkillParamsType.Anthropic,
                  SkillID = "xlsx",
                  Version = "latest",
              },
          ],
      },
      Messages = [new() { Role = Role.User, Content = "Create an Excel file with a simple budget spreadsheet" }],
      Tools = [new CodeExecutionTool20250825()],
  };

  var response = await client.Messages.Create(parameters);

  // Step 2: Extract file IDs from the response
  List<string> fileIds = [];
  foreach (var block in response.Content)
  {
      if (block.TryPickBashCodeExecutionToolResult(out var toolResult)
          && toolResult.Content.TryPickBashCodeExecutionResultBlock(out var result))
      {
          foreach (var output in result.Content)
          {
              fileIds.Add(output.FileID);
          }
      }
  }

  // Step 3: Download each file and save to disk
  foreach (var fileId in fileIds)
  {
      var fileMetadata = await client.Files.RetrieveMetadata(fileId);
      using var download = await client.Files.Download(fileId);
      using var downloadStream = await download.ReadAsStream();
      using var outputFile = File.Create(fileMetadata.Filename);
      await downloadStream.CopyToAsync(outputFile);
      Console.WriteLine($"Downloaded: {fileMetadata.Filename}");
  }

go Go
  func main() {
  	client := anthropic.NewClient()

  	// Step 1: Use a Skill to create a file
  	response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  		Model:     "claude-opus-5",
  		MaxTokens: 4096,
  		Container: anthropic.MessageCreateParamsContainerUnion{
  			OfContainers: &anthropic.ContainerParams{
  				Skills: []anthropic.SkillParams{
  					{
  						Type:    anthropic.SkillParamsTypeAnthropic,
  						SkillID: "xlsx",
  						Version: anthropic.String("latest"),
  					},
  				},
  			},
  		},
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Create an Excel file with a simple budget spreadsheet")),
  		},
  		Tools: []anthropic.ToolUnionParam{
  			{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  		},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}

  	// Step 2: Extract file IDs from the response
  	fileIDs := extractFileIDs(response)

  	// Step 3: Download the file using Files API
  	for _, fileID := range fileIDs {
  		fileMetadata, err := client.Files.GetMetadata(context.TODO(), fileID)
  		if err != nil {
  			log.Fatal(err)
  		}

  		fileContent, err := client.Files.Download(context.TODO(), fileID)
  		if err != nil {
  			log.Fatal(err)
  		}

  		// Step 4: Save to disk
  		out, err := os.Create(fileMetadata.Filename)
  		if err != nil {
  			log.Fatal(err)
  		}
  		if _, err := io.Copy(out, fileContent.Body); err != nil {
  			log.Fatal(err)
  		}
  		out.Close()
  		fileContent.Body.Close()
  		fmt.Printf("Downloaded: %s\n", fileMetadata.Filename)
  	}
  }

  func extractFileIDs(response *anthropic.Message) []string {
  	var fileIDs []string
  	for _, item := range response.Content {
  		switch v := item.AsAny().(type) {
  		case anthropic.BashCodeExecutionToolResultBlock:
  			if v.Content.Type == "bash_code_execution_result" {
  				for _, output := range v.Content.Content {
  					fileIDs = append(fileIDs, output.FileID)
  				}
  			}
  		}
  	}
  	return fileIDs
  }

java Java
  import com.anthropic.models.messages.ContainerParams;
  import com.anthropic.models.messages.SkillParams;
  import com.anthropic.models.messages.CodeExecutionTool20250825;
  import com.anthropic.models.messages.ContentBlock;
  import com.anthropic.models.files.FileMetadata;
  import com.anthropic.core.http.HttpResponse;
  // ...
  void main() throws Exception {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      // Step 1: Use a Skill to create a file
      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .container(ContainerParams.builder()
              .addSkill(SkillParams.builder()
                  .type(SkillParams.Type.ANTHROPIC)
                  .skillId("xlsx")
                  .version("latest")
                  .build())
              .build())
          .addUserMessage("Create an Excel file with a simple budget spreadsheet")
          .addTool(CodeExecutionTool20250825.builder().build())
          .build();

      Message response = client.messages().create(params);

      // Step 2: Extract file IDs from the response
      List<String> fileIds = new ArrayList<>();
      for (ContentBlock block : response.content()) {
          if (block.isBashCodeExecutionToolResult()) {
              var content = block.asBashCodeExecutionToolResult().content();
              if (content.isBashCodeExecutionResultBlock()) {
                  for (var outputBlock : content.asBashCodeExecutionResultBlock().content()) {
                      fileIds.add(outputBlock.fileId());
                  }
              }
          }
      }

      // Step 3: Download the file using Files API
      for (String fileId : fileIds) {
          FileMetadata fileMetadata = client.files().retrieveMetadata(fileId);
          HttpResponse fileContent = client.files().download(fileId);

          // Step 4: Save to disk
          try (InputStream is = fileContent.body();
               FileOutputStream fos = new FileOutputStream(fileMetadata.filename())) {
              is.transferTo(fos);
          }
          System.out.println("Downloaded: " + fileMetadata.filename());
      }
  }

php PHP
  $client = new Client();

  // Step 1: Use a Skill to create a file
  $response = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Create an Excel file with a simple budget spreadsheet']
      ],
      model: 'claude-opus-5',
      container: [
          'skills' => [
              ['type' => 'anthropic', 'skillID' => 'xlsx', 'version' => 'latest']
          ]
      ],
      tools: [
          ['type' => 'code_execution_20250825', 'name' => 'code_execution']
      ]
  );

  // Step 2: Extract file IDs from the response
  function extractFileIds($response) {
      $fileIds = [];
      foreach ($response->content as $item) {
          if ($item->type === 'bash_code_execution_tool_result') {
              $contentItem = $item->content;
              if ($contentItem->type === 'bash_code_execution_result') {
                  foreach ($contentItem->content as $file) {
                      $fileIds[] = $file->fileID;
                  }
              }
          }
      }
      return $fileIds;
  }

  // Step 3: Download the file using Files API
  foreach (extractFileIds($response) as $fileId) {
      $fileMetadata = $client->files->retrieveMetadata($fileId);
      $fileContent = $client->files->download($fileId);

      // Step 4: Save to disk
      file_put_contents($fileMetadata->filename, $fileContent);
      echo "Downloaded: {$fileMetadata->filename}\n";
  }

ruby Ruby
  client = Anthropic::Client.new

  # Step 1: Use a Skill to create a file
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [{ type: "anthropic", skill_id: "xlsx", version: "latest" }]
    },
    messages: [
      {
        role: "user",
        content: "Create an Excel file with a simple budget spreadsheet"
      }
    ],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  )

  # Step 2: Extract file IDs from the response
  def extract_file_ids(response)
    file_ids = []
    response.content.each do |item|
      if item.type == :bash_code_execution_tool_result
        content_item = item.content
        if content_item.type == :bash_code_execution_result
          content_item.content.each do |file|
            file_ids << file.file_id
          end
        end
      end
    end
    file_ids
  end

  # Step 3: Download the file using Files API
  extract_file_ids(response).each do |file_id|
    file_metadata = client.files.retrieve_metadata(file_id)

    file_content = client.files.download(file_id)

    # Step 4: Save to disk
    File.binwrite(file_metadata.filename, file_content.read)
    puts "Downloaded: #{file_metadata.filename}"
  end

bash cURL
  # Get file metadata
  curl "https://api.anthropic.com/v1/files/$FILE_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"

  # List all files
  curl "https://api.anthropic.com/v1/files" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"

  # Delete a file
  curl -X DELETE "https://api.anthropic.com/v1/files/$FILE_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"

bash CLI
  # Get file metadata
  ant files retrieve-metadata \
    --file-id "$FILE_ID" \
    --transform '{filename,size_bytes}' \
    --format yaml

  # List all files
  ant files list --transform '{filename,created_at}' --format yaml

  # Delete a file
  ant files delete --file-id "$FILE_ID" >/dev/null

python Python
  client = anthropic.Anthropic()
  file_id = "file_011CNha8iCJcU1wXNR6q4V8w"
  # Get file metadata
  file_info = client.files.retrieve_metadata(file_id=file_id)
  print(f"Filename: {file_info.filename}, Size: {file_info.size_bytes} bytes")

  # List all files
  for file in client.files.list():
      print(f"{file.filename} - {file.created_at}")

  # Delete a file
  client.files.delete(file_id=file_id)

typescript TypeScript
  const client = new Anthropic();
  const fileId = "file_011CNha8iCJcU1wXNR6q4V8w";

  // Get file metadata
  const fileInfo = await client.files.retrieveMetadata(fileId);
  console.log(`Filename: ${fileInfo.filename}, Size: ${fileInfo.size_bytes} bytes`);

  // List all files
  for await (const file of client.files.list()) {
    console.log(`${file.filename} - ${file.created_at}`);
  }

  // Delete a file
  await client.files.delete(fileId);

csharp C#
  AnthropicClient client = new();

  var fileId = "file_011CNha8iCJcU1wXNR6q4V8w";

  // Get file metadata
  var fileInfo = await client.Files.RetrieveMetadata(fileId);
  Console.WriteLine($"Filename: {fileInfo.Filename}, Size: {fileInfo.SizeBytes} bytes");

  // List files
  await foreach (var file in (await client.Files.List()).Paginate())
  {
      Console.WriteLine($"{file.Filename} - {file.CreatedAt}");
  }

  // Delete the file
  await client.Files.Delete(fileId);

go Go
  client := anthropic.NewClient()
  fileID := "file_011CNha8iCJcU1wXNR6q4V8w"

  // Get file metadata
  fileInfo, err := client.Files.GetMetadata(context.TODO(), fileID)
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Printf("Filename: %s, Size: %d bytes\n", fileInfo.Filename, fileInfo.SizeBytes)

  // List all files
  files := client.Files.ListAutoPaging(context.TODO(), anthropic.FileListParams{})
  for files.Next() {
  	file := files.Current()
  	fmt.Printf("%s - %s\n", file.Filename, file.CreatedAt)
  }
  if files.Err() != nil {
  	log.Fatal(files.Err())
  }

  // Delete a file
  _, err = client.Files.Delete(context.TODO(), fileID)
  if err != nil {
  	log.Fatal(err)
  }

java Java
  import com.anthropic.models.files.FileMetadata;
  import com.anthropic.models.files.FileListPage;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();
      String fileId = "file_011CNha8iCJcU1wXNR6q4V8w";

      // Get file metadata
      FileMetadata fileInfo = client.files().retrieveMetadata(fileId);
      System.out.println("Filename: " + fileInfo.filename() + ", Size: " + fileInfo.sizeBytes() + " bytes");

      // List files (first page)
      FileListPage files = client.files().list();
      for (var file : files.data()) {
          System.out.println(file.filename() + " - " + file.createdAt());
      }

      // Delete a file
      client.files().delete(fileId);
  }

php PHP
  $client = new Client();
  $fileId = 'file_011CNha8iCJcU1wXNR6q4V8w';

  // Get file metadata
  $fileInfo = $client->files->retrieveMetadata($fileId);
  echo "Filename: {$fileInfo->filename}, Size: {$fileInfo->sizeBytes} bytes\n";

  // List files (first page)
  foreach ($client->files->list()->getItems() as $file) {
      echo "{$file->filename} - {$file->createdAt->format(DATE_ATOM)}\n";
  }

  // Delete a file
  $client->files->delete($fileId);

ruby Ruby
  client = Anthropic::Client.new
  file_id = "file_011CNha8iCJcU1wXNR6q4V8w"

  # Get file metadata
  file_info = client.files.retrieve_metadata(file_id)
  puts "Filename: #{file_info.filename}, Size: #{file_info.size_bytes} bytes"

  # List all files
  client.files.list.auto_paging_each do |file|
    puts "#{file.filename} - #{file.created_at}"
  end

  # Delete a file
  client.files.delete(file_id)

bash cURL
  # Multi-turn container reuse doesn't translate well to a one-off shell
  # command; one of the SDK options would be a better fit. Capture
  # container.id from the first response, then pass it in the next request as
  # "container": {"id": "...", "skills": [...]} with the conversation history.

bash CLI
  # First request creates container
  CONTAINER_ID=$(ant messages create \
    --transform container.id \
    --raw-output <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - {type: anthropic, skill_id: xlsx, version: latest}
  messages:
    - role: user
      content: Create a sample sales dataset and analyze it
  tools:
    - {type: code_execution_20250825, name: code_execution}
  YAML
  )

  # Continue conversation with same container
  ant messages create <<YAML
  model: claude-opus-5
  max_tokens: 4096
  container:
    id: $CONTAINER_ID  # Reuse container
    skills:
      - {type: anthropic, skill_id: xlsx, version: latest}
  messages:
    - role: user
      content: Create a sample sales dataset and analyze it
    - role: assistant
      content: []  # the assistant's text from the first response
    - role: user
      content: What was the total revenue?
  tools:
    - {type: code_execution_20250825, name: code_execution}
  YAML

python Python
  client = anthropic.Anthropic()

  # First request creates container
  response1 = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container={
          "skills": [{"type": "anthropic", "skill_id": "xlsx", "version": "latest"}]
      },
      messages=[
          {"role": "user", "content": "Create a sample sales dataset and analyze it"}
      ],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

  # Continue conversation with same container
  messages = [
      {"role": "user", "content": "Create a sample sales dataset and analyze it"},
      {
          # Carry the assistant's text forward; container.id carries the execution state
          "role": "assistant",
          "content": "\n".join(
              block.text for block in response1.content if block.type == "text"
          ),
      },
      {"role": "user", "content": "What was the total revenue?"},
  ]

  response2 = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container={
          "id": response1.container.id,  # Reuse container
          "skills": [{"type": "anthropic", "skill_id": "xlsx", "version": "latest"}],
      },
      messages=messages,
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

typescript TypeScript
  const client = new Anthropic();

  // First request creates container
  const response1 = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [{ type: "anthropic", skill_id: "xlsx", version: "latest" }]
    },
    messages: [{ role: "user", content: "Create a sample sales dataset and analyze it" }],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });

  // Continue conversation with same container
  const messages: Anthropic.MessageParam[] = [
    { role: "user", content: "Create a sample sales dataset and analyze it" },
    {
      role: "assistant",
      // Carry the assistant's text forward; container.id carries the execution state
      content: response1.content
        .filter((block) => block.type === "text")
        .map((block) => block.text)
        .join("\n")
    },
    { role: "user", content: "What was the total revenue?" }
  ];

  const response2 = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      id: response1.container!.id, // Reuse container
      skills: [{ type: "anthropic", skill_id: "xlsx", version: "latest" }]
    },
    messages,
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });

csharp C#
  AnthropicClient client = new();

  // First request with a Skill
  var parameters1 = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Container = new ContainerParams
      {
          Skills =
          [
              new SkillParams
              {
                  Type = SkillParamsType.Anthropic,
                  SkillID = "xlsx",
                  Version = "latest",
              },
          ],
      },
      Messages = [new() { Role = Role.User, Content = "Create a sample sales dataset and analyze it" }],
      Tools = [new CodeExecutionTool20250825()],
  };

  var response1 = await client.Messages.Create(parameters1);

  // Continue the conversation in the same container
  // Carry the assistant's text forward; container.id carries the execution state
  var assistantText = string.Join(
      "\n",
      response1.Content.Select(block => block.TryPickText(out var text) ? text.Text : null).Where(text => text is not null)
  );

  var parameters2 = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Container = new ContainerParams
      {
          ID = response1.Container!.ID,
          Skills =
          [
              new SkillParams
              {
                  Type = SkillParamsType.Anthropic,
                  SkillID = "xlsx",
                  Version = "latest",
              },
          ],
      },
      Messages =
      [
          new() { Role = Role.User, Content = "Create a sample sales dataset and analyze it" },
          new() { Role = Role.Assistant, Content = assistantText },
          new() { Role = Role.User, Content = "What was the total revenue?" },
      ],
      Tools = [new CodeExecutionTool20250825()],
  };

  var response2 = await client.Messages.Create(parameters2);
  Console.WriteLine(response2);

go Go
  client := anthropic.NewClient()

  response1, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     "claude-opus-5",
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "xlsx",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Create a sample sales dataset and analyze it")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  // Carry the assistant's text forward; container.id carries the execution state
  var textParts []string
  for _, block := range response1.Content {
  	if block.Type == "text" {
  		textParts = append(textParts, block.Text)
  	}
  }
  assistantText := strings.Join(textParts, "\n")

  response2, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     "claude-opus-5",
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			ID: anthropic.String(response1.Container.ID), // Reuse container
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "xlsx",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Create a sample sales dataset and analyze it")),
  		{
  			Role:    anthropic.MessageParamRoleAssistant,
  			Content: []anthropic.ContentBlockParamUnion{anthropic.NewTextBlock(assistantText)},
  		},
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What was the total revenue?")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(response2)

java Java
  import com.anthropic.models.messages.ContainerParams;
  import com.anthropic.models.messages.SkillParams;
  import com.anthropic.models.messages.CodeExecutionTool20250825;
  import com.anthropic.models.messages.ContentBlock;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params1 = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .container(ContainerParams.builder()
              .addSkill(SkillParams.builder()
                  .type(SkillParams.Type.ANTHROPIC)
                  .skillId("xlsx")
                  .version("latest")
                  .build())
              .build())
          .addUserMessage("Create a sample sales dataset and analyze it")
          .addTool(CodeExecutionTool20250825.builder().build())
          .build();

      Message response1 = client.messages().create(params1);

      MessageCreateParams params2 = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .container(ContainerParams.builder()
              .id(response1.container().get().id())
              .addSkill(SkillParams.builder()
                  .type(SkillParams.Type.ANTHROPIC)
                  .skillId("xlsx")
                  .version("latest")
                  .build())
              .build())
          .addUserMessage("Create a sample sales dataset and analyze it")
          // Carry the assistant's text forward; container.id carries the execution state
          .addAssistantMessage(response1.content().stream()
              .filter(ContentBlock::isText)
              .map(block -> block.asText().text())
              .collect(Collectors.joining("\n")))
          .addUserMessage("What was the total revenue?")
          .addTool(CodeExecutionTool20250825.builder().build())
          .build();

      Message response2 = client.messages().create(params2);
      System.out.println(response2);
  }

php PHP
  $client = new Client();

  $response1 = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Create a sample sales dataset and analyze it']
      ],
      model: 'claude-opus-5',
      container: [
          'skills' => [
              ['type' => 'anthropic', 'skillID' => 'xlsx', 'version' => 'latest']
          ]
      ],
      tools: [
          ['type' => 'code_execution_20250825', 'name' => 'code_execution']
      ]
  );

  $messages = [
      ['role' => 'user', 'content' => 'Create a sample sales dataset and analyze it'],
      // Carry the assistant's text forward; container.id carries the execution state
      ['role' => 'assistant', 'content' => implode("\n", array_map(
          fn ($block) => $block->text,
          array_filter($response1->content, fn ($block) => $block->type === 'text'),
      ))],
      ['role' => 'user', 'content' => 'What was the total revenue?']
  ];

  $response2 = $client->messages->create(
      maxTokens: 4096,
      messages: $messages,
      model: 'claude-opus-5',
      container: [
          'id' => $response1->container->id,
          'skills' => [
              ['type' => 'anthropic', 'skillID' => 'xlsx', 'version' => 'latest']
          ]
      ],
      tools: [
          ['type' => 'code_execution_20250825', 'name' => 'code_execution']
      ]
  );

  echo $response2;

ruby Ruby
  client = Anthropic::Client.new

  response1 = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [{ type: "anthropic", skill_id: "xlsx", version: "latest" }]
    },
    messages: [
      { role: "user", content: "Create a sample sales dataset and analyze it" }
    ],
    tools: [
      { type: "code_execution_20250825", name: "code_execution" }
    ]
  )

  messages = [
    { role: "user", content: "Create a sample sales dataset and analyze it" },
    {
      # Carry the assistant's text forward; container.id carries the execution state
      role: "assistant",
      content: response1.content.filter_map { |block| block.text if block.type == :text }.join("\n")
    },
    { role: "user", content: "What was the total revenue?" }
  ]

  response2 = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      id: response1.container.id,
      skills: [
        { type: "anthropic", skill_id: "xlsx", version: "latest" }
      ]
    },
    messages: messages,
    tools: [
      { type: "code_execution_20250825", name: "code_execution" }
    ]
  )

  puts response2

bash cURL
  # Initial request
  RESPONSE=$(curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "container": {
        "skills": [
          {
            "type": "custom",
            "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
            "version": "latest"
          }
        ]
      },
      "messages": [{
        "role": "user",
        "content": "Generate and process a large sample dataset"
      }],
      "tools": [{
        "type": "code_execution_20250825",
        "name": "code_execution"
      }]
    }')

  # If stop_reason is "pause_turn", continue in the same container, appending
  # the prior response's content array to messages as the assistant turn.
  # Repeat this continuation request until stop_reason is no longer "pause_turn".
  STOP_REASON=$(echo "$RESPONSE" | jq -r '.stop_reason')
  CONTAINER_ID=$(echo "$RESPONSE" | jq -r '.container.id')

  RESPONSE=$(curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "{
      \"model\": \"claude-opus-5\",
      \"max_tokens\": 4096,
      \"container\": {
        \"id\": \"$CONTAINER_ID\",
        \"skills\": [{
          \"type\": \"custom\",
          \"skill_id\": \"skill_01AbCdEfGhIjKlMnOpQrStUv\",
          \"version\": \"latest\"
        }]
      },
      \"messages\": [],
      \"tools\": [{
        \"type\": \"code_execution_20250825\",
        \"name\": \"code_execution\"
      }]
    }")

bash CLI
  RESP=$(mktemp)

  # Initial request: capture the full JSON response to a temp file
  ant messages create > "$RESP" <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: custom
        skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
        version: latest
  messages:
    - role: user
      content: Generate and process a large sample dataset
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

  # If stop_reason is "pause_turn", continue in the same container,
  # appending the prior response's content array to messages as the
  # assistant turn. Repeat until stop_reason is no longer "pause_turn".
  CONTAINER_ID=$(jq -r '.container.id' "$RESP")

  ant messages create > "$RESP" <<YAML
  model: claude-opus-5
  max_tokens: 4096
  container:
    id: $CONTAINER_ID
    skills:
      - type: custom
        skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
        version: latest
  messages: [] # replace with conversation history + prior assistant content
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

python Python
  client = anthropic.Anthropic()

  messages = [{"role": "user", "content": "Generate and process a large sample dataset"}]
  max_retries = 10

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container={
          "skills": [
              {
                  "type": "custom",
                  "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
                  "version": "latest",
              }
          ]
      },
      messages=messages,
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

  # Handle pause_turn for long operations
  for _ in range(max_retries):
      if response.stop_reason != "pause_turn":
          break

      messages.append({"role": "assistant", "content": response.content})
      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=4096,
          container={
              "id": response.container.id,
              "skills": [
                  {
                      "type": "custom",
                      "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
                      "version": "latest",
                  }
              ],
          },
          messages=messages,
          tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
      )

typescript TypeScript
  const client = new Anthropic();
  const messages: Anthropic.MessageParam[] = [
    { role: "user", content: "Generate and process a large sample dataset" }
  ];
  const maxRetries = 10;

  let response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [{ type: "custom", skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv", version: "latest" }]
    },
    messages,
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });

  // Handle pause_turn for long operations
  for (let i = 0; i < maxRetries; i++) {
    if (response.stop_reason !== "pause_turn") {
      break;
    }

    messages.push({
      role: "assistant",
      content: response.content as Anthropic.ContentBlockParam[]
    });
    response = await client.messages.create({
      model: "claude-opus-5",
      max_tokens: 4096,
      container: {
        id: response.container!.id,
        skills: [
          { type: "custom", skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv", version: "latest" }
        ]
      },
      messages,
      tools: [{ type: "code_execution_20250825", name: "code_execution" }]
    });
  }

csharp C#
  using System.Text.Json;
  // ...
  AnthropicClient client = new();

  List<MessageParam> messages =
  [
      new() { Role = Role.User, Content = "Generate and process a large sample dataset" },
  ];

  var maxRetries = 10;
  string? containerId = null;
  Message? response = null;

  for (var i = 0; i < maxRetries; i++)
  {
      var parameters = new MessageCreateParams
      {
          Model = "claude-opus-5",
          MaxTokens = 4096,
          Container = containerId is null
              ? new ContainerParams
              {
                  Skills =
                  [
                      new SkillParams
                      {
                          Type = SkillParamsType.Custom,
                          SkillID = "skill_01AbCdEfGhIjKlMnOpQrStUv",
                          Version = "latest",
                      },
                  ],
              }
              : new ContainerParams
              {
                  ID = containerId,
                  Skills =
                  [
                      new SkillParams
                      {
                          Type = SkillParamsType.Custom,
                          SkillID = "skill_01AbCdEfGhIjKlMnOpQrStUv",
                          Version = "latest",
                      },
                  ],
              },
          Messages = messages,
          Tools = [new CodeExecutionTool20250825()],
      };

      response = await client.Messages.Create(parameters);
      containerId = response.Container!.ID;

      if (response.StopReason != StopReason.PauseTurn)
      {
          break;
      }

      // Append the paused turn's content and continue
      var assistantContent = JsonSerializer.SerializeToElement(
          response.Content.Select(block => block.Json).ToArray()
      );
      messages.Add(new() { Role = Role.Assistant, Content = new MessageParamContent(assistantContent) });
  }

go Go
  client := anthropic.NewClient()

  messages := []anthropic.MessageParam{
  	anthropic.NewUserMessage(anthropic.NewTextBlock("Generate and process a large sample dataset")),
  }
  maxRetries := 10

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     "claude-opus-5",
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeCustom,
  					SkillID: "skill_01AbCdEfGhIjKlMnOpQrStUv",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: messages,
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  for i := 0; i < maxRetries; i++ {
  	if response.StopReason != anthropic.StopReasonPauseTurn {
  		break
  	}

  	messages = append(messages, response.ToParam())

  	response, err = client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  		Model:     "claude-opus-5",
  		MaxTokens: 4096,
  		Container: anthropic.MessageCreateParamsContainerUnion{
  			OfContainers: &anthropic.ContainerParams{
  				ID: anthropic.String(response.Container.ID), // Reuse container
  				Skills: []anthropic.SkillParams{
  					{
  						Type:    anthropic.SkillParamsTypeCustom,
  						SkillID: "skill_01AbCdEfGhIjKlMnOpQrStUv",
  						Version: anthropic.String("latest"),
  					},
  				},
  			},
  		},
  		Messages: messages,
  		Tools: []anthropic.ToolUnionParam{
  			{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  		},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}
  }

  fmt.Println(response)

java Java
  import com.anthropic.models.messages.ContainerParams;
  import com.anthropic.models.messages.SkillParams;
  import com.anthropic.models.messages.CodeExecutionTool20250825;
  import com.anthropic.models.messages.StopReason;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      List<MessageParam> messages = new ArrayList<>();
      messages.add(
          MessageParam.builder()
              .role(MessageParam.Role.USER)
              .content("Generate and process a large sample dataset")
              .build()
      );
      int maxRetries = 10;

      Message response = client.messages().create(
          MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(4096L)
              .container(ContainerParams.builder()
                  .addSkill(SkillParams.builder()
                      .type(SkillParams.Type.CUSTOM)
                      .skillId("skill_01AbCdEfGhIjKlMnOpQrStUv")
                      .version("latest")
                      .build())
                  .build())
              .messages(messages)
              .addTool(CodeExecutionTool20250825.builder().build())
              .build());

      for (int i = 0; i < maxRetries; i++) {
          if (!response.stopReason().isPresent()
                  || !response.stopReason().get().equals(StopReason.PAUSE_TURN)) {
              break;
          }

          messages.add(response.toParam());

          response = client.messages().create(
              MessageCreateParams.builder()
                  .model(Model.CLAUDE_OPUS_5)
                  .maxTokens(4096L)
                  .container(ContainerParams.builder()
                      .id(response.container().get().id())
                      .addSkill(SkillParams.builder()
                          .type(SkillParams.Type.CUSTOM)
                          .skillId("skill_01AbCdEfGhIjKlMnOpQrStUv")
                          .version("latest")
                          .build())
                      .build())
                  .messages(messages)
                  .addTool(CodeExecutionTool20250825.builder().build())
                  .build());
      }
  }

php PHP
  $client = new Client();

  $messages = [
      ['role' => 'user', 'content' => 'Generate and process a large sample dataset']
  ];
  $maxRetries = 10;

  $response = $client->messages->create(
      maxTokens: 4096,
      messages: $messages,
      model: 'claude-opus-5',
      container: [
          'skills' => [
              [
                  'type' => 'custom',
                  'skillID' => 'skill_01AbCdEfGhIjKlMnOpQrStUv',
                  'version' => 'latest'
              ]
          ]
      ],
      tools: [['type' => 'code_execution_20250825', 'name' => 'code_execution']]
  );

  for ($i = 0; $i < $maxRetries; $i++) {
      if ($response->stopReason !== 'pause_turn') {
          break;
      }

      $messages[] = ['role' => 'assistant', 'content' => $response->content];

      $response = $client->messages->create(
          maxTokens: 4096,
          messages: $messages,
          model: 'claude-opus-5',
          container: [
              'id' => $response->container->id,
              'skills' => [
                  [
                      'type' => 'custom',
                      'skillID' => 'skill_01AbCdEfGhIjKlMnOpQrStUv',
                      'version' => 'latest'
                  ]
              ]
          ],
          tools: [['type' => 'code_execution_20250825', 'name' => 'code_execution']]
      );
  }

ruby Ruby
  client = Anthropic::Client.new

  messages = [
    { role: "user", content: "Generate and process a large sample dataset" }
  ]
  max_retries = 10

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [
        {
          type: "custom",
          skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
          version: "latest"
        }
      ]
    },
    messages: messages,
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  )

  max_retries.times do
    break if response.stop_reason != :pause_turn

    messages << { role: "assistant", content: response.content }

    response = client.messages.create(
      model: "claude-opus-5",
      max_tokens: 4096,
      container: {
        id: response.container.id,
        skills: [
          {
            type: "custom",
            skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
            version: "latest"
          }
        ]
      },
      messages: messages,
      tools: [{ type: "code_execution_20250825", name: "code_execution" }]
    )
  end

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "container": {
        "skills": [
          {
            "type": "anthropic",
            "skill_id": "xlsx",
            "version": "latest"
          },
          {
            "type": "anthropic",
            "skill_id": "pptx",
            "version": "latest"
          },
          {
            "type": "custom",
            "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
            "version": "latest"
          }
        ]
      },
      "messages": [{
        "role": "user",
        "content": "Analyze sales data and create a presentation"
      }],
      "tools": [{
        "type": "code_execution_20250825",
        "name": "code_execution"
      }]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: anthropic
        skill_id: xlsx
        version: latest
      - type: anthropic
        skill_id: pptx
        version: latest
      - type: custom
        skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
        version: latest
  messages:
    - role: user
      content: Analyze sales data and create a presentation
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container={
          "skills": [
              {"type": "anthropic", "skill_id": "xlsx", "version": "latest"},
              {"type": "anthropic", "skill_id": "pptx", "version": "latest"},
              {
                  "type": "custom",
                  "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
                  "version": "latest",
              },
          ]
      },
      messages=[
          {"role": "user", "content": "Analyze sales data and create a presentation"}
      ],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [
        {
          type: "anthropic",
          skill_id: "xlsx",
          version: "latest"
        },
        {
          type: "anthropic",
          skill_id: "pptx",
          version: "latest"
        },
        {
          type: "custom",
          skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
          version: "latest"
        }
      ]
    },
    messages: [
      {
        role: "user",
        content: "Analyze sales data and create a presentation"
      }
    ],
    tools: [
      {
        type: "code_execution_20250825",
        name: "code_execution"
      }
    ]
  });

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Container = new ContainerParams
      {
          Skills =
          [
              new SkillParams
              {
                  Type = SkillParamsType.Anthropic,
                  SkillID = "xlsx",
                  Version = "latest",
              },
              new SkillParams
              {
                  Type = SkillParamsType.Anthropic,
                  SkillID = "pptx",
                  Version = "latest",
              },
              new SkillParams
              {
                  Type = SkillParamsType.Custom,
                  SkillID = "skill_01AbCdEfGhIjKlMnOpQrStUv",
                  Version = "latest",
              },
          ],
      },
      Messages = [new() { Role = Role.User, Content = "Analyze sales data and create a presentation" }],
      Tools = [new CodeExecutionTool20250825()],
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     "claude-opus-5",
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "xlsx",
  					Version: anthropic.String("latest"),
  				},
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "pptx",
  					Version: anthropic.String("latest"),
  				},
  				{
  					Type:    anthropic.SkillParamsTypeCustom,
  					SkillID: "skill_01AbCdEfGhIjKlMnOpQrStUv",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Analyze sales data and create a presentation")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.messages.ContainerParams;
  import com.anthropic.models.messages.SkillParams;
  import com.anthropic.models.messages.CodeExecutionTool20250825;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .container(ContainerParams.builder()
              .skills(List.of(
                  SkillParams.builder()
                      .type(SkillParams.Type.ANTHROPIC)
                      .skillId("xlsx")
                      .version("latest")
                      .build(),
                  SkillParams.builder()
                      .type(SkillParams.Type.ANTHROPIC)
                      .skillId("pptx")
                      .version("latest")
                      .build(),
                  SkillParams.builder()
                      .type(SkillParams.Type.CUSTOM)
                      .skillId("skill_01AbCdEfGhIjKlMnOpQrStUv")
                      .version("latest")
                      .build()
              ))
              .build())
          .addUserMessage("Analyze sales data and create a presentation")
          .addTool(CodeExecutionTool20250825.builder().build())
          .build();

      Message response = client.messages().create(params);
      System.out.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Analyze sales data and create a presentation']
      ],
      model: 'claude-opus-5',
      container: [
          'skills' => [
              [
                  'type' => 'anthropic',
                  'skillID' => 'xlsx',
                  'version' => 'latest'
              ],
              [
                  'type' => 'anthropic',
                  'skillID' => 'pptx',
                  'version' => 'latest'
              ],
              [
                  'type' => 'custom',
                  'skillID' => 'skill_01AbCdEfGhIjKlMnOpQrStUv',
                  'version' => 'latest'
              ]
          ]
      ],
      tools: [
          ['type' => 'code_execution_20250825', 'name' => 'code_execution']
      ]
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [
        {
          type: "anthropic",
          skill_id: "xlsx",
          version: "latest"
        },
        {
          type: "anthropic",
          skill_id: "pptx",
          version: "latest"
        },
        {
          type: "custom",
          skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
          version: "latest"
        }
      ]
    },
    messages: [
      { role: "user", content: "Analyze sales data and create a presentation" }
    ],
    tools: [
      { type: "code_execution_20250825", name: "code_execution" }
    ]
  )
  puts message
  ```
</CodeGroup>

***


## Managing custom Skills

Source: https://platform.claude.com/llms-full.txt#managing-custom-skills

<Warning id="workspace-scoped-access">
  **Custom Skills are accessible to your entire workspace, not scoped to an end user, conversation, or session.** Any API key with access to a workspace can read, invoke, and delete every custom Skill uploaded to that workspace. Every service account, and every user whose organization role allows API access, can use the Default Workspace in addition to any workspace you add them to, so keep Skills that must stay separate in their own [workspace](https://platform.claude.com/docs/en/manage-claude/workspaces#api-keys-and-resource-scoping) and access them only with keys scoped to that workspace.

  If you are building a multi-tenant platform on the Skills API, create a separate [workspace](https://platform.claude.com/docs/en/manage-claude/workspaces) for each tenant. The workspace is the isolation boundary for custom Skills, so a workspace per tenant gives each tenant's Skills hard isolation from every other tenant. Each organization can have up to 100 workspaces by default (see [How workspaces work](https://platform.claude.com/docs/en/manage-claude/workspaces#how-workspaces-work)); if you need more for tenant isolation, contact your account team.
</Warning>

### Creating a Skill

A Skill bundle is a directory containing a `SKILL.md` file at the top level with `name` and `description` YAML frontmatter, plus any supporting scripts or resources. See [Get started with Agent Skills in the API](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart) to author one, and the **Requirements** list following the examples for the full constraints.

Upload your custom Skill to make it available in your workspace. You can upload a zip archive or individual file objects. The Python SDK also provides a `files_from_dir` helper that accepts a directory path.

Files are identified by the filename you attach (the `;filename=` suffix in the cURL example and the filename arguments in the SDK examples). For the walkthrough's skill, create a zip with `zip -r financial_skill.zip financial_skill/` and substitute it for the `example_skill.zip` placeholder in the zip-upload options.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl -X POST "https://api.anthropic.com/v1/skills" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -F "files[]=@financial_skill/SKILL.md;filename=financial_skill/SKILL.md" \
    -F "files[]=@financial_skill/analyze.py;filename=financial_skill/analyze.py"

bash CLI
    zip -r financial_skill.zip financial_skill/
    ant skills create --file financial_skill.zip

markdown
      ---
      name: financial-skill
      description: Docs example skill.
      ---

python
      print("financial analysis helper")

python Python
  from anthropic.lib import files_from_dir

  client = anthropic.Anthropic()

  # Option 1: Using a zip file
  skill = client.skills.create(
      files=[open("example_skill.zip", "rb")],
  )

  # Option 2: Using file tuples (filename, file_content, mime_type)
  skill = client.skills.create(
      files=[
          (
              "financial_skill/SKILL.md",
              open("financial_skill/SKILL.md", "rb"),
              "text/markdown",
          ),
          (
              "financial_skill/analyze.py",
              open("financial_skill/analyze.py", "rb"),
              "text/x-python",
          ),
      ],
  )

  # Option 3: Using the files_from_dir helper (Python only)
  skill = client.skills.create(
      files=files_from_dir("financial_skill"),
  )

  print(f"Created skill: {skill.id}")
  print(f"Latest version: {skill.latest_version_id}")

typescript TypeScript
  import { toFile } from "@anthropic-ai/sdk";
  import fs from "node:fs";
  // ...

  const client = new Anthropic();

  // Option 1: Using a zip file
  const skillFromZip = await client.skills.create({
    files: [await toFile(fs.createReadStream("example_skill.zip"), "example_skill.zip")]
  });

  // Option 2: Using individual file objects
  const skill = await client.skills.create({
    files: [
      await toFile(fs.createReadStream("financial_skill/SKILL.md"), "financial_skill/SKILL.md", {
        type: "text/markdown"
      }),
      await toFile(
        fs.createReadStream("financial_skill/analyze.py"),
        "financial_skill/analyze.py",
        { type: "text/x-python" }
      )
    ]
  });

  console.log(`Created skill: ${skill.id}`);
  console.log(`Latest version: ${skill.latest_version_id}`);

csharp C#
  using Anthropic.Core;
  // ...

  AnthropicClient client = new();

  // Option 1: Using a zip file
  var parameters = new SkillCreateParams
  {
      Files = [File.OpenRead("example_skill.zip")],
  };

  var skill = await client.Skills.Create(parameters);

  // Option 2: Using individual files (path-qualified filenames preserve the Skill's directory layout)
  var parameters2 = new SkillCreateParams
  {
      Files =
      [
          new BinaryContent
          {
              Stream = File.OpenRead("financial_skill/SKILL.md"),
              FileName = "financial_skill/SKILL.md",
          },
          new BinaryContent
          {
              Stream = File.OpenRead("financial_skill/analyze.py"),
              FileName = "financial_skill/analyze.py",
          },
      ],
  };

  var skill2 = await client.Skills.Create(parameters2);

  Console.WriteLine($"Created skill: {skill.ID}");
  Console.WriteLine($"Latest version: {skill.LatestVersionID}");
  Console.WriteLine($"Created skill 2: {skill2.ID}");

go Go
  client := anthropic.NewClient()

  // Option 1: Using a zip file
  zipFile, err := os.Open("example_skill.zip")
  if err != nil {
  	log.Fatal(err)
  }
  defer zipFile.Close()

  skill, err := client.Skills.New(context.TODO(), anthropic.SkillNewParams{
  	Files: []io.Reader{zipFile},
  })
  if err != nil {
  	log.Fatal(err)
  }

  // Option 2: Using individual files
  skillMd, err := os.Open("financial_skill/SKILL.md")
  if err != nil {
  	log.Fatal(err)
  }
  defer skillMd.Close()

  analyzePy, err := os.Open("financial_skill/analyze.py")
  if err != nil {
  	log.Fatal(err)
  }
  defer analyzePy.Close()

  skill2, err := client.Skills.New(context.TODO(), anthropic.SkillNewParams{
  	Files: []io.Reader{
  		anthropic.File(skillMd, "financial_skill/SKILL.md", "text/markdown"),
  		anthropic.File(analyzePy, "financial_skill/analyze.py", "text/x-python"),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Printf("Created skill: %s\n", skill.ID)
  fmt.Printf("Latest version: %s\n", skill.LatestVersionID)
  fmt.Printf("Created skill 2: %s\n", skill2.ID)

java Java
  import com.anthropic.core.MultipartField;
  import com.anthropic.models.skills.SkillCreateParams;
  import com.anthropic.models.skills.Skill;
  // ...
  void main() throws Exception {
  // ...
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      // Option 1: Using a zip file
      SkillCreateParams params = SkillCreateParams.builder()
          .addFile(MultipartField.<InputStream>builder()
              .value(Files.newInputStream(Path.of("example_skill.zip")))
              .filename("example_skill.zip")
              .contentType("application/zip")
              .build())
          .build();

      Skill skill = client.skills().create(params);

      // Option 2: Using individual files (path-qualified filenames preserve the Skill's directory layout)
      SkillCreateParams params2 = SkillCreateParams.builder()
          .addFile(MultipartField.<InputStream>builder()
              .value(Files.newInputStream(Path.of("financial_skill/SKILL.md")))
              .filename("financial_skill/SKILL.md")
              .contentType("text/markdown")
              .build())
          .addFile(MultipartField.<InputStream>builder()
              .value(Files.newInputStream(Path.of("financial_skill/analyze.py")))
              .filename("financial_skill/analyze.py")
              .contentType("text/x-python")
              .build())
          .build();

      Skill skill2 = client.skills().create(params2);

      System.out.println("Created skill: " + skill.id());
      System.out.println("Latest version: " + skill.latestVersionId());
      System.out.println("Created skill 2: " + skill2.id());
  }

php PHP
  use Anthropic\Core\FileParam;
  // ...

  $client = new Client();

  // Option 1: Using a zip file
  $skill = $client->skills->create(
      files: [
          FileParam::fromResource(fopen('example_skill.zip', 'r')),
      ],
  );

  // Option 2: Using individual files
  $skill = $client->skills->create(
      files: [
          FileParam::fromResource(
              fopen('financial_skill/SKILL.md', 'r'),
              filename: 'financial_skill/SKILL.md',
              contentType: 'text/markdown',
          ),
          FileParam::fromResource(
              fopen('financial_skill/analyze.py', 'r'),
              filename: 'financial_skill/analyze.py',
              contentType: 'text/x-python',
          ),
      ],
  );

  echo "Created skill: {$skill->id}\n";
  echo "Latest version: {$skill->latestVersionID}\n";

ruby Ruby
  client = Anthropic::Client.new

  # Option 1: Using a zip file
  skill = client.skills.create(
    files: [
      File.open("example_skill.zip", "rb")
    ]
  )

  # Option 2: Using individual files
  skill = client.skills.create(
    files: [
      Anthropic::FilePart.new(
        Pathname("financial_skill/SKILL.md"),
        filename: "financial_skill/SKILL.md",
        content_type: "text/markdown"
      ),
      Anthropic::FilePart.new(
        Pathname("financial_skill/analyze.py"),
        filename: "financial_skill/analyze.py",
        content_type: "text/x-python"
      )
    ]
  )

  puts "Created skill: #{skill.id}"
  puts "Latest version: #{skill.latest_version_id}"

bash cURL
  # List all Skills
  curl "https://api.anthropic.com/v1/skills" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"

  # List only custom Skills
  curl "https://api.anthropic.com/v1/skills?source=custom" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"

bash CLI
  # List all Skills
  ant skills list

  # List only custom Skills
  ant skills list --source custom

python Python
  client = anthropic.Anthropic()

  # List all Skills
  for skill in client.skills.list():
      print(f"{skill.id}: {skill.display_name} (source: {skill.source.type})")

  # List only custom Skills
  custom_skills = client.skills.list(source="custom")

typescript TypeScript
  const client = new Anthropic();

  // List all Skills
  for await (const skill of client.skills.list()) {
    console.log(`${skill.id}: ${skill.display_name} (source: ${skill.source.type})`);
  }

  // List only custom Skills
  const customSkills = await client.skills.list({
    source: "custom"
  });

csharp C#
  AnthropicClient client = new();

  // List all Skills
  await foreach (var skill in (await client.Skills.List()).Paginate())
  {
      Console.WriteLine($"{skill.ID}: {skill.DisplayName} (source: {skill.Source.Type})");
  }

  // List only custom Skills
  var customSkills = await client.Skills.List(new SkillListParams { Source = "custom" });

go Go
  client := anthropic.NewClient()

  // List all Skills
  skills := client.Skills.ListAutoPaging(context.TODO(), anthropic.SkillListParams{})

  for skills.Next() {
  	skill := skills.Current()
  	fmt.Printf("%s: %s (source: %s)\n", skill.ID, skill.DisplayName, skill.Source.Type)
  }
  if skills.Err() != nil {
  	log.Fatal(skills.Err())
  }

  // List only custom Skills
  customSkills := client.Skills.ListAutoPaging(context.TODO(), anthropic.SkillListParams{
  	Source: anthropic.String("custom"),
  })

  for customSkills.Next() {
  	skill := customSkills.Current()
  	fmt.Printf("%s: %s (source: %s)\n", skill.ID, skill.DisplayName, skill.Source.Type)
  }
  if customSkills.Err() != nil {
  	log.Fatal(customSkills.Err())
  }

java Java
  import com.anthropic.models.skills.SkillListParams;
  import com.anthropic.models.skills.SkillListPage;
  import com.anthropic.models.skills.Skill;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      // List Skills (first page)
      SkillListPage skills = client.skills().list();

      for (Skill skill : skills.data()) {
          System.out.println(skill.id() + ": " + skill.displayName() + " (source: " + skill.source().type() + ")");
      }

      // List only custom Skills
      SkillListParams customParams = SkillListParams.builder()
          .source("custom")
          .build();

      SkillListPage customSkills = client.skills().list(customParams);
  }

php PHP
  $client = new Client();

  // List Skills (first page)
  foreach ($client->skills->list()->getItems() as $skill) {
      echo "{$skill->id}: {$skill->displayName} (source: {$skill->source->type})\n";
  }

  // List only custom Skills
  $customSkills = $client->skills->list(
      source: 'custom',
  );

ruby Ruby
  client = Anthropic::Client.new

  # List all Skills
  client.skills.list.auto_paging_each do |skill|
    puts "#{skill.id}: #{skill.display_name} (source: #{skill.source.type})"
  end

  # List only custom Skills
  custom_skills = client.skills.list(
    source: "custom"
  )

bash cURL
  curl "https://api.anthropic.com/v1/skills/skill_01AbCdEfGhIjKlMnOpQrStUv" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"

bash CLI
  ant skills retrieve --skill-id skill_01AbCdEfGhIjKlMnOpQrStUv

python Python
  client = anthropic.Anthropic()

  skill = client.skills.retrieve(skill_id="skill_01AbCdEfGhIjKlMnOpQrStUv")

  print(f"Skill: {skill.display_name}")
  print(f"Latest version: {skill.latest_version_id}")
  print(f"Created: {skill.created_at}")

typescript TypeScript
  const client = new Anthropic();

  const skill = await client.skills.retrieve("skill_01AbCdEfGhIjKlMnOpQrStUv");

  console.log(`Skill: ${skill.display_name}`);
  console.log(`Latest version: ${skill.latest_version_id}`);
  console.log(`Created: ${skill.created_at}`);

csharp C#
  AnthropicClient client = new();

  var skill = await client.Skills.Retrieve("skill_01AbCdEfGhIjKlMnOpQrStUv");

  Console.WriteLine($"Skill: {skill.DisplayName}");
  Console.WriteLine($"Latest version: {skill.LatestVersionID}");
  Console.WriteLine($"Created: {skill.CreatedAt}");

go Go
  client := anthropic.NewClient()

  skill, err := client.Skills.Get(
  	context.TODO(),
  	"skill_01AbCdEfGhIjKlMnOpQrStUv",
  )
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Printf("Skill: %s\n", skill.DisplayName)
  fmt.Printf("Latest version: %s\n", skill.LatestVersionID)
  fmt.Printf("Created: %s\n", skill.CreatedAt)

java Java
  import com.anthropic.models.skills.Skill;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      Skill skill = client.skills().retrieve("skill_01AbCdEfGhIjKlMnOpQrStUv");

      System.out.println("Skill: " + skill.displayName());
      System.out.println("Latest version: " + skill.latestVersionId());
      System.out.println("Created: " + skill.createdAt());
  }

php PHP
  $client = new Client();

  $skill = $client->skills->retrieve('skill_01AbCdEfGhIjKlMnOpQrStUv');

  echo "Skill: {$skill->displayName}\n";
  echo "Latest version: {$skill->latestVersionID}\n";
  echo "Created: {$skill->createdAt->format(DATE_ATOM)}\n";

ruby Ruby
  client = Anthropic::Client.new

  skill = client.skills.retrieve("skill_01AbCdEfGhIjKlMnOpQrStUv")

  puts "Skill: #{skill.display_name}"
  puts "Latest version: #{skill.latest_version_id}"
  puts "Created: #{skill.created_at}"

bash cURL
  curl -X DELETE "https://api.anthropic.com/v1/skills/skill_01AbCdEfGhIjKlMnOpQrStUv" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"

bash CLI
  ant skills delete --skill-id skill_01AbCdEfGhIjKlMnOpQrStUv >/dev/null

python Python
  client = anthropic.Anthropic()

  client.skills.delete(skill_id="skill_01AbCdEfGhIjKlMnOpQrStUv")

typescript TypeScript
  const client = new Anthropic();

  await client.skills.delete("skill_01AbCdEfGhIjKlMnOpQrStUv");

csharp C#
  AnthropicClient client = new();

  await client.Skills.Delete("skill_01AbCdEfGhIjKlMnOpQrStUv");

go Go
  client := anthropic.NewClient()

  _, err := client.Skills.Delete(
  	context.TODO(),
  	"skill_01AbCdEfGhIjKlMnOpQrStUv",
  )
  if err != nil {
  	log.Fatal(err)
  }

java Java
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      client.skills().delete("skill_01AbCdEfGhIjKlMnOpQrStUv");
  }

php PHP
  $client = new Client();

  $client->skills->delete('skill_01AbCdEfGhIjKlMnOpQrStUv');

ruby Ruby
  client = Anthropic::Client.new

  client.skills.delete("skill_01AbCdEfGhIjKlMnOpQrStUv")

bash cURL
  # Create a new version
  NEW_VERSION=$(curl -X POST "https://api.anthropic.com/v1/skills/skill_01AbCdEfGhIjKlMnOpQrStUv/versions" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -F "files[]=@financial_skill/SKILL.md;filename=financial_skill/SKILL.md" \
    -F "files[]=@financial_skill/analyze.py;filename=financial_skill/analyze.py")

  VERSION_ID=$(echo "$NEW_VERSION" | jq -r '.id')

  # Use specific version
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "{
      \"model\": \"claude-opus-5\",
      \"max_tokens\": 4096,
      \"container\": {
        \"skills\": [{
          \"type\": \"custom\",
          \"skill_id\": \"skill_01AbCdEfGhIjKlMnOpQrStUv\",
          \"version\": \"$VERSION_ID\"
        }]
      },
      \"messages\": [{\"role\": \"user\", \"content\": \"Use updated Skill\"}],
      \"tools\": [{\"type\": \"code_execution_20250825\", \"name\": \"code_execution\"}]
    }"

  # Use latest version
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "container": {
        "skills": [{
          "type": "custom",
          "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
          "version": "latest"
        }]
      },
      "messages": [{"role": "user", "content": "Use latest Skill version"}],
      "tools": [{"type": "code_execution_20250825", "name": "code_execution"}]
    }'

bash CLI
  # Create a new version
  VERSION_ID=$(ant skills:versions create \
    --skill-id skill_01AbCdEfGhIjKlMnOpQrStUv \
    --file financial_skill.zip \
    --transform id \
    --raw-output)

  # Use specific version
  ant messages create <<YAML
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: custom
        skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
        version: "$VERSION_ID"
  messages:
    - role: user
      content: Use updated Skill
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

  # Use latest version
  ant messages create <<YAML
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: custom
        skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
        version: latest
  messages:
    - role: user
      content: Use latest Skill version
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

python Python
  from anthropic.lib import files_from_dir

  client = anthropic.Anthropic()

  # Create a new version

  new_version = client.skills.versions.create(
      skill_id="skill_01AbCdEfGhIjKlMnOpQrStUv",
      files=files_from_dir("financial_skill"),
  )

  # Use specific version
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container={
          "skills": [
              {
                  "type": "custom",
                  "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
                  "version": new_version.id,
              }
          ]
      },
      messages=[{"role": "user", "content": "Use updated Skill"}],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

  # Use latest version
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container={
          "skills": [
              {
                  "type": "custom",
                  "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
                  "version": "latest",
              }
          ]
      },
      messages=[{"role": "user", "content": "Use latest Skill version"}],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

typescript TypeScript
  import fs from "node:fs";

  const client = new Anthropic();

  // Create a new version from a zip of the complete financial_skill/ bundle
  const newVersion = await client.skills.versions.create("skill_01AbCdEfGhIjKlMnOpQrStUv", {
    files: [fs.createReadStream("financial_skill.zip")]
  });

  // Use specific version
  const specificVersionResponse = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [
        {
          type: "custom",
          skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
          version: newVersion.id
        }
      ]
    },
    messages: [{ role: "user", content: "Use updated Skill" }],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });

  // Use latest version
  const latestVersionResponse = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [
        {
          type: "custom",
          skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
          version: "latest"
        }
      ]
    },
    messages: [{ role: "user", content: "Use latest Skill version" }],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });

csharp C#
  using Anthropic.Core;
  using Anthropic.Models.Skills.Versions;
  // ...
  AnthropicClient client = new();

  // Create a new version
  var versionParams = new VersionCreateParams
  {
      Files =
      [
          new BinaryContent
          {
              Stream = File.OpenRead("financial_skill/SKILL.md"),
              FileName = "financial_skill/SKILL.md",
          },
          new BinaryContent
          {
              Stream = File.OpenRead("financial_skill/analyze.py"),
              FileName = "financial_skill/analyze.py",
          },
      ],
  };

  var newVersion = await client.Skills.Versions.Create("skill_01AbCdEfGhIjKlMnOpQrStUv", versionParams);

  // Use specific version
  var specificVersionParams = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Container = new ContainerParams
      {
          Skills =
          [
              new SkillParams
              {
                  Type = SkillParamsType.Custom,
                  SkillID = "skill_01AbCdEfGhIjKlMnOpQrStUv",
                  Version = newVersion.ID,
              },
          ],
      },
      Messages = [new() { Role = Role.User, Content = "Use updated Skill" }],
      Tools = [new CodeExecutionTool20250825()],
  };

  var response = await client.Messages.Create(specificVersionParams);
  Console.WriteLine(response);

  // Use latest version
  var latestVersionParams = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Container = new ContainerParams
      {
          Skills =
          [
              new SkillParams
              {
                  Type = SkillParamsType.Custom,
                  SkillID = "skill_01AbCdEfGhIjKlMnOpQrStUv",
                  Version = "latest",
              },
          ],
      },
      Messages = [new() { Role = Role.User, Content = "Use latest Skill version" }],
      Tools = [new CodeExecutionTool20250825()],
  };

  var latestResponse = await client.Messages.Create(latestVersionParams);
  Console.WriteLine(latestResponse);

go Go
  client := anthropic.NewClient()

  // Create a new version
  skillMd, err := os.Open("financial_skill/SKILL.md")
  if err != nil {
  	log.Fatal(err)
  }
  defer skillMd.Close()
  analyzePy, err := os.Open("financial_skill/analyze.py")
  if err != nil {
  	log.Fatal(err)
  }
  defer analyzePy.Close()

  newVersion, err := client.Skills.Versions.New(
  	context.TODO(),
  	"skill_01AbCdEfGhIjKlMnOpQrStUv",
  	anthropic.SkillVersionNewParams{
  		Files: []io.Reader{
  			anthropic.File(skillMd, "financial_skill/SKILL.md", "text/markdown"),
  			anthropic.File(analyzePy, "financial_skill/analyze.py", "text/x-python"),
  		},
  	},
  )
  if err != nil {
  	log.Fatal(err)
  }

  // Use specific version
  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     "claude-opus-5",
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeCustom,
  					SkillID: "skill_01AbCdEfGhIjKlMnOpQrStUv",
  					Version: anthropic.String(newVersion.ID),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Use updated Skill")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

  // Use latest version
  latestResponse, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     "claude-opus-5",
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeCustom,
  					SkillID: "skill_01AbCdEfGhIjKlMnOpQrStUv",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Use latest Skill version")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(latestResponse)

java Java
  import com.anthropic.models.messages.MessageCreateParams;
  import com.anthropic.models.messages.Message;
  import com.anthropic.models.messages.Model;
  import com.anthropic.core.MultipartField;
  import com.anthropic.models.messages.ContainerParams;
  import com.anthropic.models.messages.SkillParams;
  import com.anthropic.models.messages.CodeExecutionTool20250825;
  import com.anthropic.models.skills.versions.VersionCreateParams;
  import com.anthropic.models.skills.versions.SkillVersion;
  import java.io.InputStream;
  import java.nio.file.Files;
  import java.nio.file.Path;

  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  // Create a new version from a zip of the complete financial_skill/ bundle
  VersionCreateParams versionParams = VersionCreateParams.builder()
      .addFile(MultipartField.<InputStream>builder()
          .value(Files.newInputStream(Path.of("financial_skill.zip")))
          .filename("financial_skill.zip")
          .contentType("application/zip")
          .build())
      .build();

  SkillVersion newVersion = client.skills().versions()
      .create("skill_01AbCdEfGhIjKlMnOpQrStUv", versionParams);

  // Use specific version
  MessageCreateParams specificVersionParams = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(4096L)
      .container(ContainerParams.builder()
          .addSkill(SkillParams.builder()
              .type(SkillParams.Type.CUSTOM)
              .skillId("skill_01AbCdEfGhIjKlMnOpQrStUv")
              .version(newVersion.id())
              .build())
          .build())
      .addUserMessage("Use updated Skill")
      .addTool(CodeExecutionTool20250825.builder().build())
      .build();

  Message response = client.messages().create(specificVersionParams);
  System.out.println(response);

  // Use latest version
  MessageCreateParams latestVersionParams = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(4096L)
      .container(ContainerParams.builder()
          .addSkill(SkillParams.builder()
              .type(SkillParams.Type.CUSTOM)
              .skillId("skill_01AbCdEfGhIjKlMnOpQrStUv")
              .version("latest")
              .build())
          .build())
      .addUserMessage("Use latest Skill version")
      .addTool(CodeExecutionTool20250825.builder().build())
      .build();

  Message latestResponse = client.messages().create(latestVersionParams);
  System.out.println(latestResponse);

php PHP
  use Anthropic\Core\FileParam;
  // ...

  $client = new Client();

  // Create a new version
  $newVersion = $client->skills->versions->create(
      skillID: 'skill_01AbCdEfGhIjKlMnOpQrStUv',
      files: [
          FileParam::fromResource(
              fopen('financial_skill/SKILL.md', 'r'),
              filename: 'financial_skill/SKILL.md',
              contentType: 'text/markdown',
          ),
          FileParam::fromResource(
              fopen('financial_skill/analyze.py', 'r'),
              filename: 'financial_skill/analyze.py',
              contentType: 'text/x-python',
          ),
      ],
  );

  // Use specific version
  $response = $client->messages->create(
      maxTokens: 4096,
      messages: [['role' => 'user', 'content' => 'Use updated Skill']],
      model: 'claude-opus-5',
      container: [
          'skills' => [[
              'type' => 'custom',
              'skillID' => 'skill_01AbCdEfGhIjKlMnOpQrStUv',
              'version' => $newVersion->id
          ]]
      ],
      tools: [['type' => 'code_execution_20250825', 'name' => 'code_execution']]
  );
  echo $response;

  // Use latest version
  $latestResponse = $client->messages->create(
      maxTokens: 4096,
      messages: [['role' => 'user', 'content' => 'Use latest Skill version']],
      model: 'claude-opus-5',
      container: [
          'skills' => [[
              'type' => 'custom',
              'skillID' => 'skill_01AbCdEfGhIjKlMnOpQrStUv',
              'version' => 'latest'
          ]]
      ],
      tools: [['type' => 'code_execution_20250825', 'name' => 'code_execution']]
  );
  echo $latestResponse;

ruby Ruby
  client = Anthropic::Client.new

  # Create a new version
  new_version = client.skills.versions.create(
    "skill_01AbCdEfGhIjKlMnOpQrStUv",
    files: [
      Anthropic::FilePart.new(
        Pathname("financial_skill/SKILL.md"),
        filename: "financial_skill/SKILL.md",
        content_type: "text/markdown"
      ),
      Anthropic::FilePart.new(
        Pathname("financial_skill/analyze.py"),
        filename: "financial_skill/analyze.py",
        content_type: "text/x-python"
      )
    ]
  )

  # Use specific version
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [{
        type: "custom",
        skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
        version: new_version.id
      }]
    },
    messages: [{ role: "user", content: "Use updated Skill" }],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  )
  puts response

  # Use latest version
  latest_response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [{
        type: "custom",
        skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
        version: "latest"
      }]
    },
    messages: [{ role: "user", content: "Use latest Skill version" }],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  )
  puts latest_response
  ```
</CodeGroup>

See the [Create Skill Version API reference](https://platform.claude.com/docs/en/api/skills/versions/create) for complete details.

***


## How Skills are loaded

Source: https://platform.claude.com/llms-full.txt#how-skills-are-loaded

When you specify Skills in a container:

1. **Metadata discovery:** Claude sees metadata for each Skill (name, description) in the system prompt.
2. **File loading:** Skill files are copied into the container at `/skills/{skill-name}/`. The directory is the Skill's name (`pptx` for an Anthropic Skill, the `SKILL.md` `name` for a custom Skill), not its `skill_01...` ID.
3. **Automatic use:** Claude automatically loads and uses Skills when relevant to your request.
4. **Composition:** Multiple Skills compose together for complex workflows.

Claude loads full Skill instructions only when needed.

***


## Use cases

Source: https://platform.claude.com/llms-full.txt#use-cases-3

Skills fit both organizational and personal work. Organizations use them to apply brand formatting to documents, structure notes and reports around company templates, and run company-specific analytical procedures. Individuals use them for custom document templates, specialized data pipelines, and code generation or deployment conventions.

### Example: financial modeling

Combine Excel and custom DCF analysis Skills:

<CodeGroup>
  ```bash cURL
  # Create custom DCF analysis Skill
  DCF_SKILL=$(curl -X POST "https://api.anthropic.com/v1/skills" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -F "files[]=@dcf_skill/SKILL.md;filename=dcf_skill/SKILL.md")

  DCF_SKILL_ID=$(echo "$DCF_SKILL" | jq -r '.id')

  # Use with Excel to create financial model
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "{
      \"model\": \"claude-opus-5\",
      \"max_tokens\": 4096,
      \"container\": {
        \"skills\": [
          {
            \"type\": \"anthropic\",
            \"skill_id\": \"xlsx\",
            \"version\": \"latest\"
          },
          {
            \"type\": \"custom\",
            \"skill_id\": \"$DCF_SKILL_ID\",
            \"version\": \"latest\"
          }
        ]
      },
      \"messages\": [{
        \"role\": \"user\",
        \"content\": \"Build a DCF valuation model for a SaaS company\"
      }],
      \"tools\": [{
        \"type\": \"code_execution_20250825\",
        \"name\": \"code_execution\"
      }]
    }"

bash CLI
  # Create custom DCF analysis Skill
  DCF_SKILL_ID=$(ant skills create \
    --file dcf_skill.zip \
    --transform id \
    --raw-output)

  # Use with Excel to create financial model
  ant messages create <<YAML
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: anthropic
        skill_id: xlsx
        version: latest
      - type: custom
        skill_id: $DCF_SKILL_ID
        version: latest
  messages:
    - role: user
      content: Build a DCF valuation model for a SaaS company
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

python Python
  from anthropic.lib import files_from_dir

  client = anthropic.Anthropic()

  # Create custom DCF analysis Skill

  dcf_skill = client.skills.create(
      files=files_from_dir("/path/to/dcf_skill"),
  )

  # Use with Excel to create financial model
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container={
          "skills": [
              {"type": "anthropic", "skill_id": "xlsx", "version": "latest"},
              {"type": "custom", "skill_id": dcf_skill.id, "version": "latest"},
          ]
      },
      messages=[
          {
              "role": "user",
              "content": "Build a DCF valuation model for a SaaS company",
          }
      ],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )
  print(response)

typescript TypeScript
  import Anthropic, { toFile } from "@anthropic-ai/sdk";
  import fs from "node:fs";

  const client = new Anthropic();

  // Create custom DCF analysis Skill
  const dcfSkill = await client.skills.create({
    files: [await toFile(fs.createReadStream("dcf_skill.zip"), "dcf_skill.zip")]
  });

  // Use with Excel to create financial model
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [
        { type: "anthropic", skill_id: "xlsx", version: "latest" },
        { type: "custom", skill_id: dcfSkill.id, version: "latest" }
      ]
    },
    messages: [
      {
        role: "user",
        content: "Build a DCF valuation model for a SaaS company"
      }
    ],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });
  console.log(response);

csharp C#
  using Anthropic.Core;
  // ...
  AnthropicClient client = new();

  // Create custom DCF analysis Skill
  var dcfSkill = await client.Skills.Create(new SkillCreateParams
  {
      Files =
      [
          new BinaryContent
          {
              Stream = File.OpenRead("dcf_skill/SKILL.md"),
              FileName = "dcf_skill/SKILL.md",
          },
      ],
  });

  // Use with Excel to create financial model
  var parameters = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Container = new ContainerParams
      {
          Skills =
          [
              new SkillParams
              {
                  Type = SkillParamsType.Anthropic,
                  SkillID = "xlsx",
                  Version = "latest",
              },
              new SkillParams
              {
                  Type = SkillParamsType.Custom,
                  SkillID = dcfSkill.ID,
                  Version = "latest",
              },
          ],
      },
      Messages = [new() { Role = Role.User, Content = "Build a DCF valuation model for a SaaS company" }],
      Tools = [new CodeExecutionTool20250825()],
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  // Custom DCF analysis Skill (ID obtained from Skills API create response)
  dcfSkillID := "skill_01AbCdEfGhIjKlMnOpQrStUv"

  // Use with Excel to create financial model
  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     "claude-opus-5",
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "xlsx",
  					Version: anthropic.String("latest"),
  				},
  				{
  					Type:    anthropic.SkillParamsTypeCustom,
  					SkillID: dcfSkillID,
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Build a DCF valuation model for a SaaS company")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.messages.ContainerParams;
  import com.anthropic.models.messages.SkillParams;
  import com.anthropic.models.messages.CodeExecutionTool20250825;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      // Custom DCF analysis Skill (ID obtained from Skills API create response)
      String dcfSkillId = "skill_01AbCdEfGhIjKlMnOpQrStUv";

      // Use with Excel Skill to create financial model
      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .container(ContainerParams.builder()
              .skills(List.of(
                  SkillParams.builder()
                      .type(SkillParams.Type.ANTHROPIC)
                      .skillId("xlsx")
                      .version("latest")
                      .build(),
                  SkillParams.builder()
                      .type(SkillParams.Type.CUSTOM)
                      .skillId(dcfSkillId)
                      .version("latest")
                      .build()
              ))
              .build())
          .addUserMessage("Build a DCF valuation model for a SaaS company")
          .addTool(CodeExecutionTool20250825.builder().build())
          .build();

      Message response = client.messages().create(params);
      System.out.println(response);
  }

php PHP
  $client = new Client();

  // Custom DCF analysis Skill (ID obtained from Skills API create response)
  $dcfSkillId = 'skill_01AbCdEfGhIjKlMnOpQrStUv';

  // Use with Excel to create financial model
  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Build a DCF valuation model for a SaaS company']
      ],
      model: 'claude-opus-5',
      container: [
          'skills' => [
              ['type' => 'anthropic', 'skillID' => 'xlsx', 'version' => 'latest'],
              ['type' => 'custom', 'skillID' => $dcfSkillId, 'version' => 'latest']
          ]
      ],
      tools: [
          ['type' => 'code_execution_20250825', 'name' => 'code_execution']
      ]
  );
  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  # Create custom DCF analysis Skill
  dcf_skill = client.skills.create(
    files: [
      Anthropic::FilePart.new(
        Pathname("dcf_skill/SKILL.md"),
        filename: "dcf_skill/SKILL.md",
        content_type: "text/markdown"
      )
    ]
  )

  # Use with Excel to create financial model
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [
        { type: "anthropic", skill_id: "xlsx", version: "latest" },
        { type: "custom", skill_id: dcf_skill.id, version: "latest" }
      ]
    },
    messages: [
      { role: "user", content: "Build a DCF valuation model for a SaaS company" }
    ],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  )
  puts response
  ```
</CodeGroup>

***


## Limits and constraints

Source: https://platform.claude.com/llms-full.txt#limits-and-constraints

### Request limits

* **Maximum Skills per request:** 20

* **Maximum Skill upload size:** 30 MB (all files combined, uncompressed)

* **YAML frontmatter requirements:**

  * `name`: Maximum 64 characters, lowercase letters/numbers/hyphens only, no XML tags, no reserved words ("anthropic", "claude")
  * `description`: Maximum 1024 characters, non-empty, no XML tags

### Environment constraints

Skills run in the code execution container with these limitations:

* **No network access:** Cannot make external API calls
* **No runtime package installation:** Only pre-installed packages available
* **Isolated environment:** A fresh container is created unless you specify an existing container ID

See [Code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) for available packages.

***


## Best practices

Source: https://platform.claude.com/llms-full.txt#best-practices-7

### When to use multiple Skills

Combine Skills when tasks involve multiple document types or domains:

**Good use cases:**

* Data analysis (Excel) + presentation creation (PowerPoint)
* Report generation (Word) + export to PDF
* Custom domain logic + document generation

**Avoid:**

* Including unused Skills (impacts performance)

### Version management strategy

The SDK tabs in this section show the `container` value to include in a Messages request. The cURL and CLI tabs show the full request.

**For production:** pin a specific version, so Skill updates never change your deployed behavior. If you omit `version` or set it to `"latest"`, requests use the newest version of the Skill, so a version uploaded by anyone in the [workspace](https://platform.claude.com/docs/en/build-with-claude/skills-guide#workspace-scoped-access) immediately changes what your production agents run. The version ID comes from the create-version response in [Versioning](https://platform.claude.com/docs/en/build-with-claude/skills-guide#versioning) or from the [List Skill Versions API](https://platform.claude.com/docs/en/api/skills/versions/list). The ID is always a string, so quote it in JSON or YAML even when it looks numeric.

<CodeGroup>
  ```bash cURL
  # Pin to specific versions for stability
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "container": {
        "skills": [{
          "type": "custom",
          "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
          "version": "skver_01AbCdEfGhIjKlMnOpQrStUv"
        }]
      },
      "messages": [{"role": "user", "content": "Analyze the sales data"}],
      "tools": [{"type": "code_execution_20250825", "name": "code_execution"}]
    }'

bash CLI
  # Pin to specific versions for stability
  ant messages create <<YAML
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: custom
        skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
        version: "skver_01AbCdEfGhIjKlMnOpQrStUv"
  messages:
    - role: user
      content: Analyze the sales data
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

python Python
  # Pin to specific versions for stability
  container = {
      "skills": [
          {
              "type": "custom",
              "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
              "version": "skver_01AbCdEfGhIjKlMnOpQrStUv",
          }
      ]
  }

typescript TypeScript
  // Pin to specific versions for stability
  const container: Anthropic.ContainerParams = {
    skills: [
      {
        type: "custom",
        skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
        version: "skver_01AbCdEfGhIjKlMnOpQrStUv"
      }
    ]
  };

csharp C#
  using Anthropic.Models.Messages;

  // Pin to specific versions for stability
  var container = new ContainerParams
  {
      Skills =
      [
          new SkillParams
          {
              Type = SkillParamsType.Custom,
              SkillID = "skill_01AbCdEfGhIjKlMnOpQrStUv",
              Version = "skver_01AbCdEfGhIjKlMnOpQrStUv",
          },
      ],
  };

go Go
  // Pin to specific versions for stability
  container := anthropic.MessageCreateParamsContainerUnion{
  	OfContainers: &anthropic.ContainerParams{
  		Skills: []anthropic.SkillParams{
  			{
  				Type:    anthropic.SkillParamsTypeCustom,
  				SkillID: "skill_01AbCdEfGhIjKlMnOpQrStUv",
  				Version: anthropic.String("skver_01AbCdEfGhIjKlMnOpQrStUv"),
  			},
  		},
  	},
  }

java Java
  import com.anthropic.models.messages.ContainerParams;
  import com.anthropic.models.messages.SkillParams;

  void main() {
      // Pin to specific versions for stability
      ContainerParams container = ContainerParams.builder()
          .addSkill(SkillParams.builder()
              .type(SkillParams.Type.CUSTOM)
              .skillId("skill_01AbCdEfGhIjKlMnOpQrStUv")
              .version("skver_01AbCdEfGhIjKlMnOpQrStUv")
              .build())
          .build();
  }

php PHP
  // Pin to specific versions for stability
  $container = [
      'skills' => [[
          'type' => 'custom',
          'skillID' => 'skill_01AbCdEfGhIjKlMnOpQrStUv',
          'version' => 'skver_01AbCdEfGhIjKlMnOpQrStUv'
      ]]
  ];

ruby Ruby
  # Pin to specific versions for stability
  container = {
    skills: [{
      type: "custom",
      skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
      version: "skver_01AbCdEfGhIjKlMnOpQrStUv"
    }]
  }

bash cURL
  # Use latest for active development
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "container": {
        "skills": [{
          "type": "custom",
          "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
          "version": "latest"
        }]
      },
      "messages": [{"role": "user", "content": "Analyze the sales data"}],
      "tools": [{"type": "code_execution_20250825", "name": "code_execution"}]
    }'

bash CLI
  # Use latest for active development
  ant messages create <<YAML
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: custom
        skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
        version: latest
  messages:
    - role: user
      content: Analyze the sales data
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

python Python
  # Use latest for active development
  container = {
      "skills": [
          {
              "type": "custom",
              "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
              "version": "latest",
          }
      ]
  }

typescript TypeScript
  // Use latest for active development
  const container: Anthropic.ContainerParams = {
    skills: [
      {
        type: "custom",
        skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
        version: "latest"
      }
    ]
  };

csharp C#
  using Anthropic.Models.Messages;

  // Use latest for active development
  var container = new ContainerParams
  {
      Skills =
      [
          new SkillParams
          {
              Type = SkillParamsType.Custom,
              SkillID = "skill_01AbCdEfGhIjKlMnOpQrStUv",
              Version = "latest",
          },
      ],
  };

go Go
  // Use latest for active development
  container := anthropic.MessageCreateParamsContainerUnion{
  	OfContainers: &anthropic.ContainerParams{
  		Skills: []anthropic.SkillParams{
  			{
  				Type:    anthropic.SkillParamsTypeCustom,
  				SkillID: "skill_01AbCdEfGhIjKlMnOpQrStUv",
  				Version: anthropic.String("latest"),
  			},
  		},
  	},
  }

java Java
  import com.anthropic.models.messages.ContainerParams;
  import com.anthropic.models.messages.SkillParams;

  void main() {
      // Use latest for active development
      ContainerParams container = ContainerParams.builder()
          .addSkill(SkillParams.builder()
              .type(SkillParams.Type.CUSTOM)
              .skillId("skill_01AbCdEfGhIjKlMnOpQrStUv")
              .version("latest")
              .build())
          .build();
  }

php PHP
  // Use latest for active development
  $container = [
      'skills' => [[
          'type' => 'custom',
          'skillID' => 'skill_01AbCdEfGhIjKlMnOpQrStUv',
          'version' => 'latest'
      ]]
  ];

ruby Ruby
  # Use latest for active development
  container = {
    skills: [{
      type: "custom",
      skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
      version: "latest"
    }]
  }

bash cURL
  # Skills render into the system prompt in a fixed, cache-friendly order
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "container": {
        "skills": [
          {"type": "anthropic", "skill_id": "xlsx", "version": "latest"}
        ]
      },
      "messages": [{"role": "user", "content": "Analyze sales data"}],
      "tools": [{"type": "code_execution_20250825", "name": "code_execution"}]
    }'

  # Changing the Skills list ([xlsx] vs [xlsx, pptx]) changes the prefix: a cache miss, while an identical list is a cache hit
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "container": {
        "skills": [
          {"type": "anthropic", "skill_id": "xlsx", "version": "latest"},
          {"type": "anthropic", "skill_id": "pptx", "version": "latest"}
        ]
      },
      "messages": [{"role": "user", "content": "Create a presentation"}],
      "tools": [{"type": "code_execution_20250825", "name": "code_execution"}]
    }'

bash CLI
  # Skills render into the system prompt in a fixed, cache-friendly order
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: anthropic
        skill_id: xlsx
        version: latest
  messages:
    - role: user
      content: Analyze sales data
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

  # Changing the Skills list ([xlsx] vs [xlsx, pptx]) changes the prefix: a cache miss, while an identical list is a cache hit
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: anthropic
        skill_id: xlsx
        version: latest
      - type: anthropic
        skill_id: pptx
        version: latest
  messages:
    - role: user
      content: Create a presentation
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML

python Python
  client = anthropic.Anthropic()

  # Skills render into the system prompt in a fixed, cache-friendly order
  response1 = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container={
          "skills": [{"type": "anthropic", "skill_id": "xlsx", "version": "latest"}]
      },
      messages=[{"role": "user", "content": "Analyze sales data"}],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

  # Changing the Skills list ([xlsx] vs [xlsx, pptx]) changes the prefix: a cache miss, while an identical list is a cache hit
  response2 = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      container={
          "skills": [
              {"type": "anthropic", "skill_id": "xlsx", "version": "latest"},
              {
                  "type": "anthropic",
                  "skill_id": "pptx",
                  "version": "latest",
              },  # prefix change: cache miss
          ]
      },
      messages=[{"role": "user", "content": "Create a presentation"}],
      tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
  )

typescript TypeScript
  const client = new Anthropic();

  // Skills render into the system prompt in a fixed, cache-friendly order
  const response1 = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [{ type: "anthropic", skill_id: "xlsx", version: "latest" }]
    },
    messages: [{ role: "user", content: "Analyze sales data" }],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });

  // Changing the Skills list ([xlsx] vs [xlsx, pptx]) changes the prefix: a cache miss, while an identical list is a cache hit
  const response2 = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [
        { type: "anthropic", skill_id: "xlsx", version: "latest" },
        { type: "anthropic", skill_id: "pptx", version: "latest" } // prefix change: cache miss
      ]
    },
    messages: [{ role: "user", content: "Create a presentation" }],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  });

csharp C#
  AnthropicClient client = new();

  // Skills render into the system prompt in a fixed, cache-friendly order
  var parameters1 = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Container = new ContainerParams
      {
          Skills =
          [
              new SkillParams
              {
                  Type = SkillParamsType.Anthropic,
                  SkillID = "xlsx",
                  Version = "latest",
              },
          ],
      },
      Messages = [new() { Role = Role.User, Content = "Analyze sales data" }],
      Tools = [new CodeExecutionTool20250825()],
  };

  var response1 = await client.Messages.Create(parameters1);
  Console.WriteLine(response1);

  // Different Skill set ([xlsx] vs [xlsx, pptx]) = a different prefix: a cache miss (an identical set is a cache hit)
  var parameters2 = new MessageCreateParams
  {
      Model = "claude-opus-5",
      MaxTokens = 4096,
      Container = new ContainerParams
      {
          Skills =
          [
              new SkillParams
              {
                  Type = SkillParamsType.Anthropic,
                  SkillID = "xlsx",
                  Version = "latest",
              },
              new SkillParams
              {
                  Type = SkillParamsType.Anthropic,
                  SkillID = "pptx",
                  Version = "latest",
              },
          ],
      },
      Messages = [new() { Role = Role.User, Content = "Create a presentation" }],
      Tools = [new CodeExecutionTool20250825()],
  };

  var response2 = await client.Messages.Create(parameters2);
  Console.WriteLine(response2);

go Go
  client := anthropic.NewClient()

  // Skills render into the system prompt in a fixed, cache-friendly order
  response1, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     "claude-opus-5",
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "xlsx",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Analyze sales data")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response1)

  // Changing the Skills list ([xlsx] vs [xlsx, pptx]) changes the prefix: a cache miss, while an identical list is a cache hit
  response2, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     "claude-opus-5",
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "xlsx",
  					Version: anthropic.String("latest"),
  				},
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "pptx",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Create a presentation")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response2)

java Java
  import com.anthropic.models.messages.ContainerParams;
  import com.anthropic.models.messages.SkillParams;
  import com.anthropic.models.messages.CodeExecutionTool20250825;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      // Skills render into the system prompt in a fixed, cache-friendly order
      MessageCreateParams params1 = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .container(ContainerParams.builder()
              .skills(List.of(
                  SkillParams.builder()
                      .type(SkillParams.Type.ANTHROPIC)
                      .skillId("xlsx")
                      .version("latest")
                      .build()
              ))
              .build())
          .addUserMessage("Analyze sales data")
          .addTool(CodeExecutionTool20250825.builder().build())
          .build();

      Message response1 = client.messages().create(params1);
      System.out.println(response1);

      // Changing the Skills list ([xlsx] vs [xlsx, pptx]) changes the prefix: a cache miss, while an identical list is a cache hit
      MessageCreateParams params2 = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .container(ContainerParams.builder()
              .skills(List.of(
                  SkillParams.builder()
                      .type(SkillParams.Type.ANTHROPIC)
                      .skillId("xlsx")
                      .version("latest")
                      .build(),
                  SkillParams.builder()
                      .type(SkillParams.Type.ANTHROPIC)
                      .skillId("pptx")
                      .version("latest")
                      .build()
              ))
              .build())
          .addUserMessage("Create a presentation")
          .addTool(CodeExecutionTool20250825.builder().build())
          .build();

      Message response2 = client.messages().create(params2);
      System.out.println(response2);
  }

php PHP
  $client = new Client();

  // Skills render into the system prompt in a fixed, cache-friendly order
  $response1 = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Analyze sales data']
      ],
      model: 'claude-opus-5',
      container: [
          'skills' => [
              ['type' => 'anthropic', 'skillID' => 'xlsx', 'version' => 'latest']
          ]
      ],
      tools: [
          ['type' => 'code_execution_20250825', 'name' => 'code_execution']
      ]
  );
  echo $response1;

  // Changing the Skills list ([xlsx] vs [xlsx, pptx]) changes the prefix: a cache miss, while an identical list is a cache hit
  $response2 = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Create a presentation']
      ],
      model: 'claude-opus-5',
      container: [
          'skills' => [
              ['type' => 'anthropic', 'skillID' => 'xlsx', 'version' => 'latest'],
              ['type' => 'anthropic', 'skillID' => 'pptx', 'version' => 'latest']
          ]
      ],
      tools: [
          ['type' => 'code_execution_20250825', 'name' => 'code_execution']
      ]
  );
  echo $response2;

ruby Ruby
  client = Anthropic::Client.new

  # Skills render into the system prompt in a fixed, cache-friendly order
  response1 = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [{ type: "anthropic", skill_id: "xlsx", version: "latest" }]
    },
    messages: [{ role: "user", content: "Analyze sales data" }],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  )
  puts response1

  # Changing the Skills list ([xlsx] vs [xlsx, pptx]) changes the prefix: a cache miss, while an identical list is a cache hit
  response2 = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    container: {
      skills: [
        { type: "anthropic", skill_id: "xlsx", version: "latest" },
        { type: "anthropic", skill_id: "pptx", version: "latest" } # prefix change: cache miss
      ]
    },
    messages: [{ role: "user", content: "Create a presentation" }],
    tools: [{ type: "code_execution_20250825", name: "code_execution" }]
  )
  puts response2

bash cURL
  # This error-handling flow doesn't translate well to a one-off shell
  # command; one of the SDK options would be a better fit. A failing request
  # returns HTTP 400 with an error JSON whose .error.message names the
  # Skill problem.

bash CLI
  if ! RESULT=$(ant messages create \
    --transform-error error.message \
    --format-error yaml 2>&1 <<'YAML'
  model: claude-opus-5
  max_tokens: 4096
  container:
    skills:
      - type: custom
        skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
        version: latest
  messages:
    - role: user
      content: Process data
  tools:
    - type: code_execution_20250825
      name: code_execution
  YAML
  ); then
    case "$RESULT" in
      *skill*)
        printf 'Skill error: %s\n' "$RESULT"
        # Handle skill-specific errors
        ;;
      *)
        printf '%s\n' "$RESULT" >&2
        exit 1
        ;;
    esac
  fi

python Python
  client = anthropic.Anthropic()

  try:
      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=4096,
          container={
              "skills": [
                  {
                      "type": "custom",
                      "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
                      "version": "latest",
                  }
              ]
          },
          messages=[{"role": "user", "content": "Process data"}],
          tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
      )
  except anthropic.BadRequestError as e:
      if "skill" in str(e):
          print(f"Skill error: {e}")
          # Handle skill-specific errors
      else:
          raise

typescript TypeScript
  const client = new Anthropic();

  try {
    const response = await client.messages.create({
      model: "claude-opus-5",
      max_tokens: 4096,
      container: {
        skills: [
          { type: "custom", skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv", version: "latest" }
        ]
      },
      messages: [{ role: "user", content: "Process data" }],
      tools: [{ type: "code_execution_20250825", name: "code_execution" }]
    });
    console.log(response);
  } catch (error) {
    if (error instanceof Anthropic.BadRequestError && error.message.includes("skill")) {
      console.error(`Skill error: ${error.message}`);
      // Handle skill-specific errors
    } else {
      throw error;
    }
  }

csharp C#
  using Anthropic.Exceptions;
  // ...
  AnthropicClient client = new();

  try
  {
      var parameters = new MessageCreateParams
      {
          Model = "claude-opus-5",
          MaxTokens = 4096,
          Container = new ContainerParams
          {
              Skills =
              [
                  new SkillParams
                  {
                      Type = SkillParamsType.Custom,
                      SkillID = "skill_01AbCdEfGhIjKlMnOpQrStUv",
                      Version = "latest",
                  },
              ],
          },
          Messages = [new() { Role = Role.User, Content = "Process data" }],
          Tools = [new CodeExecutionTool20250825()],
      };

      var response = await client.Messages.Create(parameters);
      Console.WriteLine(response);
  }
  catch (AnthropicBadRequestException e) when (e.Message.Contains("skill"))
  {
      Console.WriteLine($"Skill error: {e.Message}");
  }

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     "claude-opus-5",
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeCustom,
  					SkillID: "skill_01AbCdEfGhIjKlMnOpQrStUv",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Process data")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20250825: &anthropic.CodeExecutionTool20250825Param{}},
  	},
  })

  if err != nil {
  	var apierr *anthropic.Error
  	if errors.As(err, &apierr) && apierr.Type() == anthropic.ErrorTypeInvalidRequestError &&
  		strings.Contains(apierr.Error(), "skill") {
  		fmt.Printf("Skill error: %v\n", apierr)
  	} else {
  		log.Fatal(err)
  	}
  	return
  }
  fmt.Println(response)

java Java
  import com.anthropic.errors.BadRequestException;
  import com.anthropic.models.messages.ContainerParams;
  import com.anthropic.models.messages.SkillParams;
  import com.anthropic.models.messages.CodeExecutionTool20250825;
  // ...
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      try {
          MessageCreateParams params = MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(4096L)
              .container(ContainerParams.builder()
                  .addSkill(SkillParams.builder()
                      .type(SkillParams.Type.CUSTOM)
                      .skillId("skill_01AbCdEfGhIjKlMnOpQrStUv")
                      .version("latest")
                      .build())
                  .build())
              .addUserMessage("Process data")
              .addTool(CodeExecutionTool20250825.builder().build())
              .build();

          Message response = client.messages().create(params);
          System.out.println(response);
      } catch (BadRequestException e) {
          if (e.getMessage().contains("skill")) {
              System.err.println("Skill error: " + e.getMessage());
          } else {
              throw e;
          }
      }
  }

php PHP
  use Anthropic\Core\Exceptions\BadRequestException;

  $client = new Client();

  try {
      $message = $client->messages->create(
          maxTokens: 4096,
          messages: [
              ['role' => 'user', 'content' => 'Process data']
          ],
          model: 'claude-opus-5',
          container: [
              'skills' => [
                  [
                      'type' => 'custom',
                      'skillID' => 'skill_01AbCdEfGhIjKlMnOpQrStUv',
                      'version' => 'latest'
                  ]
              ]
          ],
          tools: [
              ['type' => 'code_execution_20250825', 'name' => 'code_execution']
          ]
      );
      echo $message;
  } catch (BadRequestException $e) {
      if (str_contains($e->getMessage(), 'skill')) {
          echo "Skill error: " . $e->getMessage();
      } else {
          throw $e;
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  begin
    response = client.messages.create(
      model: "claude-opus-5",
      max_tokens: 4096,
      container: {
        skills: [
          {
            type: "custom",
            skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
            version: "latest"
          }
        ]
      },
      messages: [{ role: "user", content: "Process data" }],
      tools: [{ type: "code_execution_20250825", name: "code_execution" }]
    )
  rescue Anthropic::Errors::BadRequestError => e
    if e.message.include?("skill")
      puts "Skill error: #{e.message}"
    else
      raise
    end
  end
  ```
</CodeGroup>

***


## Data retention

Source: https://platform.claude.com/llms-full.txt#data-retention-10

Agent Skills are not covered by ZDR arrangements. Skill definitions and execution data are retained according to Anthropic's standard data retention policy.

For ZDR eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).


## Audit logging

Source: https://platform.claude.com/llms-full.txt#audit-logging

If your organization has the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) enabled, its [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) records the creation and deletion of Skills and Skill versions made with a Claude API key or from the Claude Console. Operations that occur while the Compliance API is off are not recorded and cannot be recovered later, so [set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access) before you rely on this audit trail.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-60

<CardGroup cols={3}>
  <Card title="API reference" icon="book" href="https://platform.claude.com/docs/en/api/skills/create">
    Complete API reference with all endpoints
  </Card>

  <Card title="Skill authoring best practices" icon="edit" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices">
    Learn how to write effective Skills that Claude can discover and use successfully.
  </Card>

  <Card title="Code execution tool" icon="terminal" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool">
    Run Python and bash code in a sandboxed container to analyze data, generate files, and iterate on solutions.
  </Card>
</CardGroup>


### MCP

---
title: MCP connector
url: https://platform.claude.com/docs/en/agents-and-tools/mcp-connector
description: Connect to remote MCP servers directly from the Messages API without an MCP client, and allowlist, denylist, or configure individual tools.
---


## Compatibility

Source: https://platform.claude.com/llms-full.txt#compatibility-14

- Status: Beta
- [Beta header](https://platform.claude.com/docs/en/api/beta-headers): `mcp-client-2025-11-20`
- [ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): not eligible
- Platforms: Claude API (beta), Claude Platform on AWS (beta), Microsoft Foundry (beta); not available on Amazon Bedrock, Google Cloud

Claude's Model Context Protocol (MCP) connector feature enables you to connect to remote MCP servers directly from the Messages API without a separate MCP client.

<Note>
  The previous version of this feature (`mcp-client-2025-04-04`) is deprecated. See [Deprecated version: mcp-client-2025-04-04](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector#deprecated-version-mcp-client-2025-04-04).
</Note>


## Key features

Source: https://platform.claude.com/llms-full.txt#key-features

* **Direct API integration:** Connect to MCP servers without implementing an MCP client
* **Tool calling support:** Access MCP tools through the Messages API
* **Flexible tool configuration:** Enable all tools, allowlist specific tools, or denylist unwanted tools
* **Per-tool configuration:** Configure individual tools with custom settings
* **OAuth authentication:** Support for OAuth Bearer tokens for authenticated servers
* **Multiple servers:** Connect to multiple MCP servers in a single request


## When Claude uses MCP tools

Source: https://platform.claude.com/llms-full.txt#when-claude-uses-mcp-tools

Once an MCP server is connected, Claude calls its tools when the user's request maps to a tool's described capability, either explicitly ("search Jira for open bugs") or implicitly ("what's blocking the release?" with a Jira server attached).

Claude does **not** call an MCP tool for general knowledge questions about a connected service. Asking "how do Notion databases work?" with a Notion server attached is answered directly; asking "what's in my Projects database?" triggers the tool.

You can steer how readily Claude calls MCP tools through your system prompt. See [When Claude uses tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview#when-claude-uses-tools) for general guidance and example phrasings.


## Limitations

Source: https://platform.claude.com/llms-full.txt#limitations-8

* Of the feature set of the [MCP specification](https://modelcontextprotocol.io/introduction#explore-mcp), only [tool calls](https://modelcontextprotocol.io/docs/concepts/tools) are currently supported.
* The server must be publicly exposed through HTTP (supports both Streamable HTTP and SSE transports). Local STDIO servers cannot be connected directly.


## Using the MCP connector in the Messages API

Source: https://platform.claude.com/llms-full.txt#using-the-mcp-connector-in-the-messages-api

The MCP connector uses two components:

1. **MCP server definition** (`mcp_servers` array): Defines server connection details (URL, authentication)
2. **MCP toolset** (`tools` array): Configures which tools to enable and how to configure them

### Basic example

This example enables all tools from an MCP server with default configuration:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: mcp-client-2025-11-20" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1000,
      "messages": [{"role": "user", "content": "What tools do you have available?"}],
      "mcp_servers": [
        {
          "type": "url",
          "url": "https://example-server.modelcontextprotocol.io/sse",
          "name": "example-mcp",
          "authorization_token": "YOUR_TOKEN"
        }
      ],
      "tools": [
        {
          "type": "mcp_toolset",
          "mcp_server_name": "example-mcp"
        }
      ]
    }'

bash CLI
  ant beta:messages create --beta mcp-client-2025-11-20 <<'YAML'
  model: claude-opus-5
  max_tokens: 1000
  messages:
    - role: user
      content: What tools do you have available?
  mcp_servers:
    - type: url
      url: https://example-server.modelcontextprotocol.io/sse
      name: example-mcp
      authorization_token: YOUR_TOKEN
  tools:
    - type: mcp_toolset
      mcp_server_name: example-mcp
  YAML

python Python
  client = anthropic.Anthropic()

  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=1000,
      messages=[{"role": "user", "content": "What tools do you have available?"}],
      mcp_servers=[
          {
              "type": "url",
              "url": "https://example-server.modelcontextprotocol.io/sse",
              "name": "example-mcp",
              "authorization_token": "YOUR_TOKEN",
          }
      ],
      tools=[{"type": "mcp_toolset", "mcp_server_name": "example-mcp"}],
      betas=["mcp-client-2025-11-20"],
  )

  print(response)

typescript TypeScript
  const anthropic = new Anthropic();

  const response = await anthropic.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 1000,
    messages: [
      {
        role: "user",
        content: "What tools do you have available?"
      }
    ],
    mcp_servers: [
      {
        type: "url",
        url: "https://example-server.modelcontextprotocol.io/sse",
        name: "example-mcp",
        authorization_token: "YOUR_TOKEN"
      }
    ],
    tools: [
      {
        type: "mcp_toolset",
        mcp_server_name: "example-mcp"
      }
    ],
    betas: ["mcp-client-2025-11-20"]
  });

  console.log(response);

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1000,
      Messages = new List<BetaMessageParam>
      {
          new() { Role = Role.User, Content = "What tools do you have available?" }
      },
      McpServers = new List<BetaRequestMcpServerUrlDefinition>
      {
          new()
          {
              Url = "https://example-server.modelcontextprotocol.io/sse",
              Name = "example-mcp",
              AuthorizationToken = "YOUR_TOKEN"
          }
      },
      Tools = new List<BetaToolUnion>
      {
          new BetaMcpToolset("example-mcp")
      },
      Betas = [AnthropicBeta.McpClient2025_11_20]
  };

  var message = await client.Beta.Messages.Create(parameters);
  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1000,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("What tools do you have available?")),
  	},
  	MCPServers: []anthropic.BetaRequestMCPServerURLDefinitionParam{
  		{
  			URL:                "https://example-server.modelcontextprotocol.io/sse",
  			Name:               "example-mcp",
  			AuthorizationToken: anthropic.String("YOUR_TOKEN"),
  		},
  	},
  	Tools: []anthropic.BetaToolUnionParam{
  		{OfMCPToolset: &anthropic.BetaMCPToolsetParam{
  			MCPServerName: "example-mcp",
  		}},
  	},
  	Betas: []anthropic.AnthropicBeta{
  		anthropic.AnthropicBetaMCPClient2025_11_20,
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response)

java Java
  import com.anthropic.models.beta.messages.BetaMcpToolset;
  // ...
  import com.anthropic.models.beta.messages.BetaRequestMcpServerUrlDefinition;
  // ...

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1000L)
          .addUserMessage("What tools do you have available?")
          .addMcpServer(BetaRequestMcpServerUrlDefinition.builder()
              .url("https://example-server.modelcontextprotocol.io/sse")
              .name("example-mcp")
              .authorizationToken("YOUR_TOKEN")
              .build())
          .addTool(BetaMcpToolset.builder()
              .mcpServerName("example-mcp")
              .build())
          .addBeta(AnthropicBeta.MCP_CLIENT_2025_11_20)
          .build();

      BetaMessage response = client.beta().messages().create(params);
      IO.println(response);
  }

php PHP
  $client = new Client();

  $message = $client->beta->messages->create(
      maxTokens: 1000,
      messages: [
          ['role' => 'user', 'content' => 'What tools do you have available?']
      ],
      model: 'claude-opus-5',
      mcpServers: [
          [
              'type' => 'url',
              'url' => 'https://example-server.modelcontextprotocol.io/sse',
              'name' => 'example-mcp',
              'authorization_token' => 'YOUR_TOKEN',
          ],
      ],
      tools: [
          [
              'type' => 'mcp_toolset',
              'mcp_server_name' => 'example-mcp',
          ],
      ],
      betas: ['mcp-client-2025-11-20'],
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 1000,
    messages: [
      { role: "user", content: "What tools do you have available?" }
    ],
    mcp_servers: [
      {
        type: "url",
        url: "https://example-server.modelcontextprotocol.io/sse",
        name: "example-mcp",
        authorization_token: "YOUR_TOKEN"
      }
    ],
    tools: [
      {
        type: "mcp_toolset",
        mcp_server_name: "example-mcp"
      }
    ],
    betas: ["mcp-client-2025-11-20"]
  )

  puts response
  ```
</CodeGroup>


## MCP server configuration

Source: https://platform.claude.com/llms-full.txt#mcp-server-configuration

Each MCP server in the `mcp_servers` array defines the connection details:

### Field descriptions

| Property              | Type   | Required | Description                                                                                                                                                                                                                                                                                                            |
| --------------------- | ------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                | string | Yes      | Currently only "url" is supported.                                                                                                                                                                                                                                                                                     |
| `url`                 | string | Yes      | The URL of the MCP server. Must start with https\://.                                                                                                                                                                                                                                                                  |
| `name`                | string | Yes      | A unique identifier for this MCP server. Must be referenced by exactly one MCPToolset in the `tools` array.                                                                                                                                                                                                            |
| `authorization_token` | string | No       | OAuth authorization token if required by the MCP server. See [Authentication](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector#authentication) for how to obtain one, or the [MCP specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) for protocol details. |


## MCP toolset configuration

Source: https://platform.claude.com/llms-full.txt#mcp-toolset-configuration

The MCPToolset lives in the `tools` array and configures which tools from the MCP server are enabled and how they should be configured.

### Basic structure

### Field descriptions

| Property          | Type   | Required | Description                                                                                                                             |
| ----------------- | ------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `type`            | string | Yes      | Must be "mcp\_toolset".                                                                                                                 |
| `mcp_server_name` | string | Yes      | Must match a server name defined in the `mcp_servers` array.                                                                            |
| `default_config`  | object | No       | Default configuration applied to all tools in this set. Individual tool configs in `configs` override these defaults.                   |
| `configs`         | object | No       | Per-tool configuration overrides. Keys are tool names, values are configuration objects.                                                |
| `cache_control`   | object | No       | [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) cache breakpoint configuration for this toolset. |

### Tool configuration options

Each tool (whether configured in `default_config` or in `configs`) supports the following fields:

| Property        | Type    | Default | Description                                                                                                                                                                 |
| --------------- | ------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `enabled`       | boolean | `true`  | Whether this tool is enabled.                                                                                                                                               |
| `defer_loading` | boolean | `false` | If true, tool description is not sent to the model initially. Used with [Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool). |

For the full directory of Anthropic-provided tools and optional properties such as `defer_loading`, see the [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference). To search across large tool sets, see [Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool).

### Configuration merging

Configuration values merge with this precedence (highest to lowest):

1. Tool-specific settings in `configs`
2. Set-level `default_config`
3. System defaults

Example:

Results in:

* `search_events`: `enabled: false` (from configs), `defer_loading: true` (from default\_config)
* All other tools: `enabled: true` (system default), `defer_loading: true` (from default\_config)


## Common configuration patterns

Source: https://platform.claude.com/llms-full.txt#common-configuration-patterns

### Enable all tools with default configuration

The simplest pattern: enable all tools from a server:

### Allowlist: enable only specific tools

Set `enabled: false` as the default, then explicitly enable specific tools:

### Denylist: disable specific tools

Enable all tools by default, then explicitly disable unwanted tools. Denylisting write or destructive tools is recommended when building read-only assistants, or when you want a human confirmation step before state changes:

### Mixed: allowlist with per-tool configuration

Combine allowlisting with custom configuration for each tool:

In this example:

* `search_events` is enabled with `defer_loading: false`
* `list_events` is enabled with `defer_loading: true` (inherited from default\_config)
* All other tools are disabled


## Validation rules

Source: https://platform.claude.com/llms-full.txt#validation-rules

The API enforces these validation rules:

* **Server must exist:** The `mcp_server_name` in an MCPToolset must match a server defined in the `mcp_servers` array
* **Server must be used:** Every MCP server defined in `mcp_servers` must be referenced by exactly one MCPToolset
* **Unique toolset per server:** Each MCP server can only be referenced by one MCPToolset
* **Unknown tool names:** If a tool name in `configs` doesn't exist on the MCP server, a backend warning is logged but no error is returned (MCP servers may have dynamic tool availability)


## Response content types

Source: https://platform.claude.com/llms-full.txt#response-content-types

When Claude uses MCP tools, the response includes two new content block types:

### MCP tool use block

### MCP tool result block


## Multiple MCP servers

Source: https://platform.claude.com/llms-full.txt#multiple-mcp-servers

You can connect to multiple MCP servers by including multiple server definitions in `mcp_servers` and a corresponding MCPToolset for each in the `tools` array:

With many tools available, Claude selects based on tool names and descriptions. Clear, specific tool descriptions improve selection accuracy. For large tool sets (dozens of tools across several servers), consider enabling [`defer_loading`](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector#tool-configuration-options) with the [Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) so only relevant tools are surfaced per query.


## Authentication

Source: https://platform.claude.com/llms-full.txt#authentication

For MCP servers that require OAuth authentication, you'll need to obtain an access token. The MCP connector beta supports passing an `authorization_token` parameter in the MCP server definition. API consumers are expected to handle the OAuth flow and obtain the access token prior to making the API call, and to refresh the token as needed.

### Obtaining an access token for testing

The MCP inspector can guide you through the process of obtaining an access token for testing purposes.

1. Run the inspector with the following command. You need Node.js installed on your machine.

2. In the sidebar on the left, for **Transport type**, select either **SSE** or **Streamable HTTP**.

3. Enter the URL of the MCP server.

4. In the right area, click **Open Auth Settings** after **Need to configure authentication?**.

5. Click **Quick OAuth Flow** and authorize on the OAuth screen.

6. Follow the steps in the **OAuth Flow Progress** section of the inspector and click **Continue** until you reach **Authentication complete**.

7. Copy the `access_token` value.

8. Paste it into the `authorization_token` field in your MCP server configuration.

### Using the access token

Once you've obtained an access token using either of the preceding OAuth flows, you can use it in your MCP server configuration:

For detailed explanations of the OAuth flow, refer to the [Authorization section](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) in the MCP specification.


## Client-side MCP helpers

Source: https://platform.claude.com/llms-full.txt#client-side-mcp-helpers

If you manage your own MCP client connection (for example, with local stdio servers, MCP prompts, or MCP resources), the SDKs provide helper functions that convert between MCP types and Claude API types. This eliminates manual conversion code when using an MCP SDK for your language (for example, the [TypeScript MCP SDK](https://github.com/modelcontextprotocol/typescript-sdk)) alongside the Anthropic SDK.

<Note>
  Use the [`mcp_servers` API parameter](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector#using-the-mcp-connector-in-the-messages-api) when you have remote servers accessible by URL and only need tool support. Use the client-side helpers when you need local servers, prompts, resources, or more control over the connection with the base SDK.
</Note>

### Installation

Install both the Anthropic SDK and the MCP SDK:

<Tabs>
  <Tab title="Python">
    The MCP helpers are included in the `mcp` extra, which requires Python 3.10 or later:

</Tab>

  <Tab title="TypeScript">

</Tab>

  <Tab title="C#">
    The helpers live in the separate `Anthropic.Mcp` package; the MCP client itself comes from the official [ModelContextProtocol package](https://www.nuget.org/packages/ModelContextProtocol):

</Tab>

  <Tab title="Go">
    The helpers live in the `mcp` subpackage of the Go SDK, which builds on the [MCP Go SDK](https://github.com/modelcontextprotocol/go-sdk):

</Tab>

  <Tab title="Java">
    The helpers live in the separate `anthropic-java-mcp` artifact, which requires Java 17 or later (the core SDK supports Java 8):

    <Tabs>
      <Tab title="Gradle">

</Tab>

      <Tab title="Maven">

</Tab>
    </Tabs>
  </Tab>

  <Tab title="PHP">
    The helpers use the official [MCP PHP SDK](https://packagist.org/packages/mcp/sdk):

</Tab>

  <Tab title="Ruby">
    The helpers use the official [`mcp` gem](https://rubygems.org/gems/mcp):

</Tab>
</Tabs>

### Available helpers

Import the helpers for your language:

<CodeGroup exclude="shell">
  ```python Python
  from anthropic.lib.tools.mcp import (
      async_mcp_tool,
      mcp_message,
      mcp_resource_to_content,
      mcp_resource_to_file,
  )

typescript TypeScript
  import {
    mcpTools,
    mcpMessages,
    mcpResourceToContent,
    mcpResourceToFile
  } from "@anthropic-ai/sdk/helpers/beta/mcp";

csharp C#
  using Anthropic.Helpers.Beta;
  using Anthropic.Helpers.Beta.Mcp;

go Go
  import (
  	"github.com/anthropics/anthropic-sdk-go/mcp"
  )

java Java
  import com.anthropic.helpers.McpBetaTool;
  import com.anthropic.mcp.BetaMcp;

php PHP
  use Anthropic\Lib\Tools\BetaMcp;

ruby Ruby
  require "anthropic"

  # The helpers are exposed on the Anthropic::Mcp module

python Python
  from anthropic.lib.tools.mcp import async_mcp_tool
  from mcp import ClientSession
  from mcp.client.stdio import StdioServerParameters, stdio_client

  client = AsyncAnthropic()


  async def main() -> None:
      # Connect to an MCP server
      server_params = StdioServerParameters(command="mcp-server")
      async with stdio_client(server_params) as (read, write):
          async with ClientSession(read, write) as mcp_client:
              await mcp_client.initialize()

              # List tools and convert them for the Claude API
              tools_result = await mcp_client.list_tools()
              runner = client.beta.messages.tool_runner(
                  model="claude-opus-5",
                  max_tokens=1024,
                  messages=[
                      {"role": "user", "content": "What tools do you have available?"},
                  ],
                  tools=[async_mcp_tool(tool, mcp_client) for tool in tools_result.tools],
              )

              final_message = await runner.until_done()
              print(final_message)


  asyncio.run(main())

typescript TypeScript
  import {
    mcpTools,
    type MCPCallToolResultLike,
    type MCPClientLike
  } from "@anthropic-ai/sdk/helpers/beta/mcp";
  import { Client } from "@modelcontextprotocol/sdk/client/index.js";
  import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

  const anthropic = new Anthropic();

  // Connect to an MCP server
  const transport = new StdioClientTransport({ command: "mcp-server", args: [] });
  const mcpClient = new Client({ name: "my-client", version: "1.0.0" });
  await mcpClient.connect(transport);

  // List tools and convert them for the Claude API
  const { tools } = await mcpClient.listTools();

  // The MCP SDK's callTool return type still includes a legacy result shape that
  // mcpTools does not accept; narrow it. Drop this once MCPClientLike widens.
  const mcpClientForTools: MCPClientLike = {
    callTool: (params) => mcpClient.callTool(params) as Promise<MCPCallToolResultLike>
  };

  const finalMessage = await anthropic.beta.messages.toolRunner({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "What tools do you have available?" }],
    tools: mcpTools(tools, mcpClientForTools)
  });

  console.log(finalMessage);

csharp C#
  using Anthropic.Helpers.Beta;
  using Anthropic.Helpers.Beta.Mcp;
  using Anthropic.Models.Beta.Messages;
  using ModelContextProtocol.Client;
  using Messages = Anthropic.Models.Messages;

  var anthropic = new AnthropicClient();

  // Connect to an MCP server
  await using var mcpClient = await McpClient.CreateAsync(
      new StdioClientTransport(new StdioClientTransportOptions { Command = "mcp-server" })
  );

  // List tools and convert them for the Claude API
  var tools = await BetaMcp.ListToolsAsync(mcpClient);
  var runner = anthropic.Beta.Messages.ToolRunner(
      new MessageCreateParams
      {
          Model = Messages::Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages =
          [
              new BetaMessageParam
              {
                  Role = Role.User,
                  Content = "What tools do you have available?",
              },
          ],
      },
      tools
  );

  var finalMessage = await runner.RunUntilDoneAsync();
  Console.WriteLine(finalMessage);

go Go
  import (
  // ...

  // ...
  	"github.com/anthropics/anthropic-sdk-go/mcp"
  	mcpsdk "github.com/modelcontextprotocol/go-sdk/mcp"
  )

  func main() {
  	client := anthropic.NewClient()
  	ctx := context.Background()

  	// Connect to an MCP server
  	mcpClient := mcpsdk.NewClient(&mcpsdk.Implementation{Name: "my-client", Version: "1.0.0"}, nil)
  	session, err := mcpClient.Connect(ctx, &mcpsdk.CommandTransport{Command: exec.Command("mcp-server")}, nil)
  	if err != nil {
  		log.Fatal(err)
  	}
  	defer session.Close()

  	// List tools and convert them for the Claude API
  	toolsResult, err := session.ListTools(ctx, nil)
  	if err != nil {
  		log.Fatal(err)
  	}
  	betaTools, err := mcp.NewBetaTools(toolsResult.Tools, session)
  	if err != nil {
  		log.Fatal(err)
  	}

  	runner := client.Beta.Messages.NewToolRunner(betaTools, anthropic.BetaToolRunnerParams{
  		BetaMessageNewParams: anthropic.BetaMessageNewParams{
  			Model:     anthropic.ModelClaudeOpus5,
  			MaxTokens: 1024,
  			Messages: []anthropic.BetaMessageParam{
  				anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("What tools do you have available?")),
  			},
  		},
  	})

  	finalMessage, err := runner.RunToCompletion(ctx)
  	if err != nil {
  		log.Fatal(err)
  	}
  	fmt.Println(finalMessage.RawJSON())
  }

java Java
  import com.anthropic.helpers.BetaToolRunner;
  import com.anthropic.helpers.McpBetaTool;
  import com.anthropic.mcp.BetaMcp;
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;
  import io.modelcontextprotocol.client.McpClient;
  import io.modelcontextprotocol.client.McpSyncClient;
  import io.modelcontextprotocol.client.transport.ServerParameters;
  import io.modelcontextprotocol.client.transport.StdioClientTransport;
  import io.modelcontextprotocol.json.McpJsonDefaults;
  import io.modelcontextprotocol.spec.McpSchema;
  // ...

  void main() throws Exception {
      AnthropicClient anthropic = AnthropicOkHttpClient.fromEnv();

      // Connect to an MCP server
      StdioClientTransport transport = new StdioClientTransport(
              ServerParameters.builder("mcp-server").build(), McpJsonDefaults.getMapper());

      try (McpSyncClient mcpClient = McpClient.sync(transport)
              .clientInfo(new McpSchema.Implementation("my-client", "1.0.0"))
              .build()) {

          mcpClient.initialize();

          // List tools and convert them for the Claude API
          List<McpBetaTool> betaTools = BetaMcp.mcpTools(mcpClient.listTools().tools(), mcpClient);

          MessageCreateParams params = MessageCreateParams.builder()
                  .model(Model.CLAUDE_OPUS_5)
                  .maxTokens(1024L)
                  .addUserMessage("What tools do you have available?")
                  .addTools(betaTools)
                  .build();

          // The runner yields one message per assistant turn; the last is the final response
          BetaToolRunner runner = anthropic.beta().messages().toolRunner(params);
          BetaMessage finalMessage = null;
          for (BetaMessage message : runner) {
              finalMessage = message;
          }
          IO.println(finalMessage);
      }
  }

php PHP
  use Anthropic\Lib\Tools\BetaMcp;
  use Mcp\Client;
  use Mcp\Client\Transport\HttpTransport;

  $anthropic = new Anthropic();

  // Connect to an MCP server. The PHP MCP client connects over HTTP; point this
  // at your server's endpoint.
  $mcp = Client::builder()->build();
  $mcp->connect(new HttpTransport('http://localhost:8000/mcp'));

  // List tools and convert them for the Claude API
  $runner = $anthropic->beta->messages->toolRunner(
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'What tools do you have available?']],
      model: 'claude-opus-5',
      tools: BetaMcp::tools($mcp->listTools()->tools, $mcp),
  );

  echo $runner->runUntilDone(), "\n";

ruby Ruby
  require "mcp"

  anthropic = Anthropic::Client.new

  # Connect to an MCP server
  transport = MCP::Client::Stdio.new(command: "mcp-server")
  mcp_client = MCP::Client.new(transport: transport)
  mcp_client.connect

  # List tools and convert them for the Claude API
  runner = anthropic.beta.messages.tool_runner(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "What tools do you have available?" }],
    tools: Anthropic::Mcp.tools(mcp_client.tools, mcp_client)
  )

  final_message = runner.run_until_finished.last
  puts final_message

python Python
  from anthropic.lib.tools.mcp import mcp_message

  prompt = await mcp_client.get_prompt(name="my-prompt")
  response = await client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[mcp_message(message) for message in prompt.messages],
  )

  print(response)

typescript TypeScript
  import { mcpMessages } from "@anthropic-ai/sdk/helpers/beta/mcp";

  const { messages } = await mcpClient.getPrompt({ name: "my-prompt" });
  const response = await anthropic.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: mcpMessages(messages)
  });

  console.log(response);

csharp C#
  var prompt = await mcpClient.GetPromptAsync("my-prompt");
  var response = await anthropic.Beta.Messages.Create(
      new MessageCreateParams
      {
          Model = Messages::Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages = BetaMcp.Messages(prompt.Messages),
      }
  );

  Console.WriteLine(response);

go Go
  prompt, err := session.GetPrompt(ctx, &mcpsdk.GetPromptParams{Name: "my-prompt"})
  if err != nil {
  	log.Fatal(err)
  }

  messages := make([]anthropic.BetaMessageParam, 0, len(prompt.Messages))
  for _, promptMessage := range prompt.Messages {
  	message, err := mcp.ToMessage(promptMessage)
  	if err != nil {
  		log.Fatal(err)
  	}
  	messages = append(messages, message)
  }

  response, err := client.Beta.Messages.New(ctx, anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages:  messages,
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

java Java
  McpSchema.GetPromptResult prompt = mcpClient.getPrompt(
          new McpSchema.GetPromptRequest("my-prompt", Map.of()));

  BetaMessage response = anthropic.beta().messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .messages(BetaMcp.mcpMessages(prompt.messages()))
          .build());

  IO.println(response);

php PHP
  $prompt = $mcp->getPrompt('my-prompt');

  $response = $anthropic->beta->messages->create(
      maxTokens: 1024,
      messages: array_map(BetaMcp::message(...), $prompt->messages),
      model: 'claude-opus-5',
  );

  echo $response, "\n";

ruby Ruby
  prompt = mcp_client.get_prompt(name: "my-prompt")

  response = anthropic.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: prompt["messages"].map { |message| Anthropic::Mcp.message(message) }
  )

  puts response

python Python
  from anthropic.lib.tools.mcp import (
      mcp_resource_to_content,
      mcp_resource_to_file,
  )

  # As a content block in a message
  resource = await mcp_client.read_resource(uri="file:///path/to/doc.txt")
  response = await client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  mcp_resource_to_content(resource),
                  {"type": "text", "text": "Summarize this document"},
              ],
          }
      ],
  )
  print(response)

  # As a file upload
  file_resource = await mcp_client.read_resource(
      uri="file:///path/to/data.json",
  )
  uploaded = await client.files.upload(
      file=mcp_resource_to_file(file_resource),
  )
  print(uploaded.id)

typescript TypeScript
  import { mcpResourceToContent, mcpResourceToFile } from "@anthropic-ai/sdk/helpers/beta/mcp";

  // As a content block in a message
  const resource = await mcpClient.readResource({ uri: "file:///path/to/doc.txt" });
  const response = await anthropic.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          mcpResourceToContent(resource),
          { type: "text", text: "Summarize this document" }
        ]
      }
    ]
  });
  console.log(response);

  // As a file upload
  const fileResource = await mcpClient.readResource({ uri: "file:///path/to/data.json" });
  const uploaded = await anthropic.files.upload({ file: mcpResourceToFile(fileResource) });
  console.log(uploaded.id);

csharp C#
  // As a content block in a message
  var resource = await mcpClient.ReadResourceAsync("file:///path/to/doc.txt");
  var response = await anthropic.Beta.Messages.Create(
      new MessageCreateParams
      {
          Model = Messages::Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages =
          [
              new BetaMessageParam
              {
                  Role = Role.User,
                  Content = new BetaMessageParamContent(
                      [
                          BetaMcp.ResourceToContent(resource),
                          new BetaTextBlockParam { Text = "Summarize this document" },
                      ]
                  ),
              },
          ],
      }
  );

  Console.WriteLine(response);

  // As a file upload
  var fileResource = await mcpClient.ReadResourceAsync("file:///path/to/data.json");
  var (filename, data, mediaType) = BetaMcp.ResourceToFile(fileResource);

  // Build the file part explicitly so the resource's filename and MIME type
  // carry through to the upload.
  var file = new BinaryContent { Stream = new MemoryStream(data), FileName = filename };
  if (mediaType is not null)
  {
      file.ContentType = new(mediaType);
  }

  var uploaded = await anthropic.Files.Upload(new FileUploadParams { File = file });
  Console.WriteLine(uploaded.ID);

go Go
  // As a content block in a message
  resource, err := session.ReadResource(ctx, &mcpsdk.ReadResourceParams{URI: "file:///path/to/doc.txt"})
  if err != nil {
  	log.Fatal(err)
  }
  block, err := mcp.ResourceToBlock(resource)
  if err != nil {
  	log.Fatal(err)
  }

  response, err := client.Beta.Messages.New(ctx, anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(
  			// ResourceToBlock returns the tool-result content union; message
  			// content is a separate union type, so re-wrap the shared variants
  			// (mcp.ToMessage does the same internally).
  			anthropic.BetaContentBlockParamUnion{
  				OfText:     block.OfText,
  				OfImage:    block.OfImage,
  				OfDocument: block.OfDocument,
  			},
  			anthropic.NewBetaTextBlock("Summarize this document"),
  		),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())

  // As a file upload
  fileResult, err := session.ReadResource(ctx, &mcpsdk.ReadResourceParams{URI: "file:///path/to/data.json"})
  if err != nil {
  	log.Fatal(err)
  }
  fileReader, err := mcp.ResourceToFile(fileResult)
  if err != nil {
  	log.Fatal(err)
  }
  uploaded, err := client.Files.Upload(ctx, anthropic.FileUploadParams{File: fileReader})
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(uploaded.ID)

java Java
  // As a content block in a message
  McpSchema.ReadResourceResult resource = mcpClient.readResource(
          new McpSchema.ReadResourceRequest("file:///path/to/doc.txt"));

  List<BetaContentBlockParam> content =
          new ArrayList<>(BetaMcp.mcpResourceContents(resource));
  content.add(BetaContentBlockParam.ofText(
          BetaTextBlockParam.builder().text("Summarize this document").build()));

  BetaMessage response = anthropic.beta().messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addUserMessageOfBetaContentBlockParams(content)
          .build());

  IO.println(response);

  // As a file upload
  McpSchema.ReadResourceResult fileResource = mcpClient.readResource(
          new McpSchema.ReadResourceRequest("file:///path/to/data.json"));

  McpResourceFile resourceFile = BetaMcp.mcpResourceFiles(fileResource).getFirst();

  // Build the file part explicitly so the resource's filename and MIME type
  // carry through to the upload.
  MultipartField.Builder<InputStream> fileField = MultipartField.<InputStream>builder()
          .value(new ByteArrayInputStream(resourceFile.content()))
          .filename(resourceFile.filename());
  if (resourceFile.mimeType() != null) {
      fileField.contentType(resourceFile.mimeType());
  }

  var uploaded = anthropic.files().upload(FileUploadParams.builder()
          .file(fileField.build())
          .build());

  IO.println(uploaded.id());

php PHP
  // As a content block in a message
  $resource = $mcp->readResource('file:///path/to/doc.txt');

  $response = $anthropic->beta->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  BetaMcp::resourceToContent($resource),
                  ['type' => 'text', 'text' => 'Summarize this document'],
              ],
          ],
      ],
      model: 'claude-opus-5',
  );

  echo $response, "\n";

  // As a file upload
  $fileResource = $mcp->readResource('file:///path/to/data.json');
  $file = $anthropic->files->upload(file: BetaMcp::resourceToFile($fileResource));
  echo $file->id, "\n";

ruby Ruby
  # As a content block in a message
  resource = mcp_client.read_resource(uri: "file:///path/to/doc.txt")

  response = anthropic.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          *Anthropic::Mcp.resource_to_contents(resource),
          { type: "text", text: "Summarize this document" }
        ]
      }
    ]
  )

  puts response

  # As a file upload
  file_resource = mcp_client.read_resource(uri: "file:///path/to/data.json")
  file = Anthropic::Mcp.resource_to_files(file_resource).first
  uploaded_file = anthropic.files.upload(file: file)
  puts uploaded_file.id
  ```
</CodeGroup>

### Error handling

The conversion functions throw `UnsupportedMCPValueError` if an MCP value isn't supported by the Claude API (in Go, the helpers return an `UnsupportedValueError`; in Java and C#, they throw `AnthropicInvalidDataException`). This can happen with unsupported content types, MIME types, or resource links (resolve resource links with your MCP client before converting).
