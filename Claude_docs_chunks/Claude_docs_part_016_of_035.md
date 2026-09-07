# platform.claude.com Documentation (Part 16 of 35)

## Attach skills to an agent

Source: https://platform.claude.com/llms-full.txt#attach-skills-to-an-agent

Attach skills when creating an agent. Each [session](https://platform.claude.com/docs/en/managed-agents/sessions) supports up to 500 skills, counted as the deduplicated set across every agent in the session (see [Multiagent orchestration](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration)).

<Note>
  Mounting more skills increases the time it takes for the session's sandbox to start. Attach only the skills each agent needs for its task.
</Note>

Each entry in the `skills` array uses the following fields:

| Field      | Description                                                                                                                                                                                                                                                        |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `type`     | Either `anthropic` for pre-built skills or `custom` for workspace-authored skills.                                                                                                                                                                                 |
| `skill_id` | The skill identifier. For Anthropic skills, use the short name (for example, `xlsx`). For custom skills, use the `skill_*` ID returned at creation (see [Create a custom skill](https://platform.claude.com/docs/en/managed-agents/skills#create-a-custom-skill)). |
| `version`  | Pin to a specific version or use `latest`. Optional. Defaults to `latest` when omitted. Applies to both Anthropic and custom skills.                                                                                                                               |

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  agent=$(curl -sS https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    --json @- <<'EOF'
  {
    "name": "Financial Analyst",
    "model": "claude-opus-5",
    "system": "You are a financial analysis agent.",
    "skills": [
      {"type": "anthropic", "skill_id": "xlsx"},
      {"type": "custom", "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv", "version": "latest"}
    ]
  }
  EOF
  )

bash CLI
    ant beta:agents create < agent.yaml

yaml
      name: Financial Analyst
      model: claude-opus-5
      system: You are a financial analysis agent.
      skills:
        - type: anthropic
          skill_id: xlsx
        - type: custom
          skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
          version: latest

python Python
  agent = client.beta.agents.create(
      name="Financial Analyst",
      model="claude-opus-5",
      system="You are a financial analysis agent.",
      skills=[
          {
              "type": "anthropic",
              "skill_id": "xlsx",
          },
          {
              "type": "custom",
              "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
              "version": "latest",
          },
      ],
  )

typescript TypeScript
  const agent = await client.beta.agents.create({
    name: "Financial Analyst",
    model: "claude-opus-5",
    system: "You are a financial analysis agent.",
    skills: [
      {
        type: "anthropic",
        skill_id: "xlsx"
      },
      {
        type: "custom",
        skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv",
        version: "latest"
      }
    ]
  });

csharp C#
  using Anthropic.Models.Beta.Agents;

  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "Financial Analyst",
      Model = BetaManagedAgentsModel.ClaudeOpus5,
      System = "You are a financial analysis agent.",
      Skills =
      [
          new BetaManagedAgentsAnthropicSkillParams { Type = BetaManagedAgentsAnthropicSkillParamsType.Anthropic, SkillID = "xlsx" },
          new BetaManagedAgentsCustomSkillParams { Type = BetaManagedAgentsCustomSkillParamsType.Custom, SkillID = "skill_01AbCdEfGhIjKlMnOpQrStUv", Version = "latest" },
      ],
  });

go Go
  agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name: "Financial Analyst",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID: anthropic.BetaManagedAgentsModelClaudeOpus5,
  	},
  	System: anthropic.String("You are a financial analysis agent."),
  	Skills: []anthropic.BetaManagedAgentsSkillParamsUnion{
  		{OfAnthropic: &anthropic.BetaManagedAgentsAnthropicSkillParams{
  			SkillID: "xlsx",
  			Type:    anthropic.BetaManagedAgentsAnthropicSkillParamsTypeAnthropic,
  		}},
  		{OfCustom: &anthropic.BetaManagedAgentsCustomSkillParams{
  			SkillID: "skill_01AbCdEfGhIjKlMnOpQrStUv",
  			Type:    anthropic.BetaManagedAgentsCustomSkillParamsTypeCustom,
  			Version: anthropic.String("latest"),
  		}},
  	},
  })
  if err != nil {
  	panic(err)
  }
  _ = agent

java Java
  import com.anthropic.models.beta.agents.*;

  var agent = client.beta().agents().create(
      AgentCreateParams.builder()
          .name("Financial Analyst")
          .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
          .system("You are a financial analysis agent.")
          .addSkill(
              BetaManagedAgentsAnthropicSkillParams.builder()
                  .type(BetaManagedAgentsAnthropicSkillParams.Type.ANTHROPIC)
                  .skillId("xlsx")
                  .build()
          )
          .addSkill(
              BetaManagedAgentsCustomSkillParams.builder()
                  .type(BetaManagedAgentsCustomSkillParams.Type.CUSTOM)
                  .skillId("skill_01AbCdEfGhIjKlMnOpQrStUv")
                  .version("latest")
                  .build()
          )
          .build()
  );

php PHP
  $agent = $client->beta->agents->create(
      name: 'Financial Analyst',
      model: 'claude-opus-5',
      system: 'You are a financial analysis agent.',
      skills: [
          ['type' => 'anthropic', 'skillID' => 'xlsx'],
          ['type' => 'custom', 'skillID' => 'skill_01AbCdEfGhIjKlMnOpQrStUv', 'version' => 'latest'],
      ],
  );

ruby Ruby
  agent = client.beta.agents.create(
    name: "Financial Analyst",
    model: "claude-opus-5",
    system_: "You are a financial analysis agent.",
    skills: [
      {type: "anthropic", skill_id: "xlsx"},
      {type: "custom", skill_id: "skill_01AbCdEfGhIjKlMnOpQrStUv", version: "latest"}
    ]
  )
  ```
</CodeGroup>


## Load skills from a GitHub repository

Source: https://platform.claude.com/llms-full.txt#load-skills-from-a-github-repository

Skills can also live in your codebase. When a session mounts a repository through the [`github_repository` resource](https://platform.claude.com/docs/en/managed-agents/github), the repository's root `.claude/skills` directory is scanned at session start, and each skill found there becomes available to the agent. No upload and no entry in the agent's `skills` array are required. The agent sees each discovered skill's name, description, and path in the sandbox, and reads the skill's `SKILL.md` when a task matches, including any scripts and resources the skill ships. Discovery relies on the agent's `read` tool from the [agent toolset](https://platform.claude.com/docs/en/managed-agents/tools), which is enabled by default; an agent with `read` disabled doesn't load repository skills.

<Warning>
  Repository skills are agent instructions, so a mounted repository is part of your agent's trust boundary. Anyone who can commit to the repository (a merged external pull request, a compromised dependency, a contributor) can add or change a skill, the platform loads it at session start without a review step, and session tools such as `bash` and `web_fetch` give those instructions real reach. Mount only repositories you trust, and review `.claude/skills` before mounting a repository that accepts outside contributions.
</Warning>

<Note>
  Repository skill discovery runs in cloud sandboxes. [Self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) don't support GitHub repository resources.
</Note>

Discovery finds skills at exactly `.claude/skills/<skill-name>/SKILL.md`, one directory level deep at the repository root:

* `your-repo/`

  * `.claude/`

    * `skills/`

      * `code-review/`
        * `SKILL.md`

      * `release-process/`

        * `SKILL.md`
        * `scripts/`
          * `run_checks.sh`

  * `src/`

Locations that don't match this layout aren't discovered at session start:

* `.claude/skills/SKILL.md`: a `SKILL.md` with no skill directory around it
* `.claude/skills/tools/code-review/SKILL.md`: nested more than one directory level deep
* `skills/code-review/SKILL.md`: a `skills` directory outside `.claude`

A `.claude/skills` directory elsewhere in the repository, such as inside a package subdirectory, isn't announced at session start; those skills can still surface when the agent reads files under that subtree.

Repository skills use the same `SKILL.md` format as the custom skills you upload. For the format and authoring guidance, see [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) and [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

To load skills from a repository, create a session that mounts it. This is the same request shown in [Accessing GitHub](https://platform.claude.com/docs/en/managed-agents/github#token-permissions); `mount_path` is optional and defaults to `/workspace/<repo-name>`:

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  session_id=$(curl -fsS https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    --data @- <<JSON | jq -r '.id'
  {
    "agent": "$agent_id",
    "environment_id": "$environment_id",
    "resources": [
      {
        "type": "github_repository",
        "url": "https://github.com/org/repo",
        "mount_path": "/workspace/repo",
        "authorization_token": "ghp_your_github_token"
      }
    ]
  }
  JSON
  )

bash CLI
  SESSION_ID=$(ant beta:sessions create \
    --agent "$AGENT_ID" \
    --environment-id "$ENVIRONMENT_ID" \
    --transform id --raw-output <<'EOF'
  resources:
    - type: github_repository
      url: https://github.com/org/repo
      mount_path: /workspace/repo
      authorization_token: ghp_your_github_token
  EOF
  )

python Python
  session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
      resources=[
          {
              "type": "github_repository",
              "url": "https://github.com/org/repo",
              "mount_path": "/workspace/repo",
              "authorization_token": "ghp_your_github_token",
          },
      ],
  )

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id,
    resources: [
      {
        type: "github_repository",
        url: "https://github.com/org/repo",
        mount_path: "/workspace/repo",
        authorization_token: "ghp_your_github_token",
      },
    ],
  });

csharp C#
  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = agent.ID,
      EnvironmentID = environment.ID,
      Resources =
      [
          new BetaManagedAgentsGitHubRepositoryResourceParams
          {
              Type = "github_repository",
              Url = "https://github.com/org/repo",
              MountPath = "/workspace/repo",
              AuthorizationToken = "ghp_your_github_token",
          },
      ],
  });

go Go
  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent:         anthropic.BetaSessionNewParamsAgentUnion{OfString: anthropic.String(agent.ID)},
  	EnvironmentID: environment.ID,
  	Resources: []anthropic.BetaSessionNewParamsResourceUnion{
  		{
  			OfGitHubRepository: &anthropic.BetaManagedAgentsGitHubRepositoryResourceParams{
  				Type:               anthropic.BetaManagedAgentsGitHubRepositoryResourceParamsTypeGitHubRepository,
  				URL:                "https://github.com/org/repo",
  				MountPath:          anthropic.String("/workspace/repo"),
  				AuthorizationToken: "ghp_your_github_token",
  			},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  var session = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(agent.id())
      .environmentId(environment.id())
      .addResource(BetaManagedAgentsGitHubRepositoryResourceParams.builder()
          .type(BetaManagedAgentsGitHubRepositoryResourceParams.Type.GITHUB_REPOSITORY)
          .url("https://github.com/org/repo")
          .mountPath("/workspace/repo")
          .authorizationToken("ghp_your_github_token")
          .build())
      .build());

php PHP
  $session = $client->beta->sessions->create(
      agent: $agent->id,
      environmentID: $environment->id,
      resources: [
          [
              'type' => 'github_repository',
              'url' => 'https://github.com/org/repo',
              'mountPath' => '/workspace/repo',
              'authorizationToken' => 'ghp_your_github_token',
          ],
      ],
  );

ruby Ruby
  session = client.beta.sessions.create(
    agent: agent.id,
    environment_id: environment.id,
    resources: [
      {
        type: "github_repository",
        url: "https://github.com/org/repo",
        mount_path: "/workspace/repo",
        authorization_token: "ghp_your_github_token"
      }
    ]
  )
  ```
</CodeGroup>

For private repositories, the resource's `authorization_token` must have access to the repository. This is the same personal access token flow used for any repository mount; see [Accessing GitHub](https://platform.claude.com/docs/en/managed-agents/github#token-permissions).

Discovered skills follow the checked-out state of the repository: the `checkout` branch or commit when the resource sets one, otherwise the repository's default branch. The scan runs once, when the session starts. Commits pushed mid-session are not picked up; to load updated skills, start a new session.

Repository skills work alongside skills attached through the agent's `skills` array. If a repository skill shares a name with an attached skill, or with a skill from another mounted repository, both are available; each is announced with its own path.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-72

<CardGroup cols={2}>
  <Card title="Cloud environment setup" icon="settings" href="https://platform.claude.com/docs/en/managed-agents/environments">
    Customize cloud sandboxes for your sessions.
  </Card>

  <Card title="Using Agent Skills with the API" icon="code" href="https://platform.claude.com/docs/en/build-with-claude/skills-guide">
    Learn how to use Agent Skills to extend Claude's capabilities through the API.
  </Card>

  <Card title="Files API" icon="file" href="https://platform.claude.com/docs/en/build-with-claude/files">
    Upload files once and reference them across API requests.
  </Card>

  <Card title="Get started with Agent Skills in the API" icon="graduation-cap" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart">
    Learn how to use Agent Skills to create documents with the Claude API in under 10 minutes.
  </Card>
</CardGroup>


---
title: Tools
url: https://platform.claude.com/docs/en/managed-agents/tools
description: Configure tools available to your agent.
---

Claude Managed Agents provides a set of built-in tools that Claude can use autonomously within a [session](https://platform.claude.com/docs/en/managed-agents/sessions). You control which tools are available by specifying them in the agent configuration.

Claude Managed Agents also supports custom, user-defined tools. Your application executes these tools separately and returns the results to Claude, which uses them to continue the task. To give the agent tools from an MCP server, use the [MCP connector](https://platform.claude.com/docs/en/managed-agents/mcp-connector) instead.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Available tools

Source: https://platform.claude.com/llms-full.txt#available-tools

The agent toolset includes the following tools. All are enabled by default when you include the toolset in your agent configuration. Each entry in the `configs` array is identified by its `name`, using the values in the Name column, and accepts an optional `type` field with the same value. The `web_search` and `web_fetch` entries accept additional settings; see [Restrict web search and web fetch domains](https://platform.claude.com/docs/en/managed-agents/tools#restrict-web-search-and-web-fetch-domains).

| Tool       | Name         | Description                                    |
| ---------- | ------------ | ---------------------------------------------- |
| Bash       | `bash`       | Execute bash commands in a shell session       |
| Read       | `read`       | Read a file from the sandbox filesystem        |
| Write      | `write`      | Write a file to the sandbox filesystem         |
| Edit       | `edit`       | Perform string replacement in a file           |
| Glob       | `glob`       | Fast file pattern matching using glob patterns |
| Grep       | `grep`       | Text search using regex patterns               |
| Web fetch  | `web_fetch`  | Fetch content from a URL                       |
| Web search | `web_search` | Search the web for information                 |

When a tool output exceeds 100,000 characters (about 25,000 tokens), it is automatically written to a file in the [sandbox](https://platform.claude.com/docs/en/managed-agents/environments). The model receives a truncated preview with the file path and can read the full content from there.


## Configuring the toolset

Source: https://platform.claude.com/llms-full.txt#configuring-the-toolset

Enable the full toolset with `agent_toolset_20260401` when creating an agent. Use the `configs` array to disable specific tools or override their settings. Each config entry can also set a `permission_policy` that controls whether the tool's calls are auto-approved or require confirmation. See [Permission policies](https://platform.claude.com/docs/en/managed-agents/permission-policies) for the available policy types.

Config entries for `web_search` and `web_fetch` also accept domain filters and other web settings; see [Restrict web search and web fetch domains](https://platform.claude.com/docs/en/managed-agents/tools#restrict-web-search-and-web-fetch-domains).

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  agent=$(curl -fsSL https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<'EOF'
  {
    "name": "Coding Assistant",
    "model": "claude-opus-5",
    "tools": [
      {
        "type": "agent_toolset_20260401",
        "configs": [
          {"name": "web_fetch", "enabled": false}
        ]
      }
    ]
  }
  EOF
  )

bash CLI
  ant beta:agents create <<'YAML'
  name: Coding Assistant
  model: claude-opus-5
  tools:
    - type: agent_toolset_20260401
      configs:
        - name: web_fetch
          enabled: false
  YAML

python Python
  agent = client.beta.agents.create(
      name="Coding Assistant",
      model="claude-opus-5",
      tools=[
          {
              "type": "agent_toolset_20260401",
              "configs": [
                  {"name": "web_fetch", "enabled": False},
              ],
          },
      ],
  )

typescript TypeScript
  const agent = await client.beta.agents.create({
    name: "Coding Assistant",
    model: "claude-opus-5",
    tools: [
      {
        type: "agent_toolset_20260401",
        configs: [{ name: "web_fetch", enabled: false }]
      }
    ]
  });

csharp C#
  using Anthropic.Models.Beta.Agents;

  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "Coding Assistant",
      Model = new("claude-opus-5"),
      Tools =
      [
          new BetaManagedAgentsAgentToolset20260401Params
          {
              Type = "agent_toolset_20260401",
              Configs =
              [
                  new BetaManagedAgentsWebFetchToolConfigParams { Enabled = false },
              ],
          },
      ],
  });

go Go
  agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name: "Coding Assistant",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID: "claude-opus-5",
  	},
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{{
  		OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  			Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  			Configs: []anthropic.BetaManagedAgentsAgentToolConfigParamsUnion{{
  				OfWebFetch: &anthropic.BetaManagedAgentsWebFetchToolConfigParams{
  					Enabled: anthropic.Bool(false),
  				},
  			}},
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }
  _ = agent

java Java
  import com.anthropic.models.beta.agents.*;

  var agent = client.beta().agents().create(AgentCreateParams.builder()
      .name("Coding Assistant")
      .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
      .addTool(BetaManagedAgentsAgentToolset20260401Params.builder()
          .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
          .addConfig(BetaManagedAgentsWebFetchToolConfigParams.builder()
              .enabled(false)
              .build())
          .build())
      .build());

php PHP
  use Anthropic\Beta\Agents\BetaManagedAgentsAgentToolset20260401Params;
  use Anthropic\Beta\Agents\BetaManagedAgentsWebFetchToolConfigParams;

  $agent = $client->beta->agents->create(
      name: 'Coding Assistant',
      model: 'claude-opus-5',
      tools: [
          BetaManagedAgentsAgentToolset20260401Params::with(
              type: 'agent_toolset_20260401',
              configs: [
                  BetaManagedAgentsWebFetchToolConfigParams::with(enabled: false),
              ],
          ),
      ],
  );

ruby Ruby
  agent = client.beta.agents.create(
    name: "Coding Assistant",
    model: "claude-opus-5",
    tools: [
      {
        type: :agent_toolset_20260401,
        configs: [
          {name: :web_fetch, enabled: false}
        ]
      }
    ]
  )

json
{
  "type": "agent_toolset_20260401",
  "configs": [
    { "name": "web_fetch", "enabled": false },
    { "name": "web_search", "enabled": false }
  ]
}

json
{
  "type": "agent_toolset_20260401",
  "default_config": { "enabled": false },
  "configs": [
    { "name": "bash", "enabled": true },
    { "name": "read", "enabled": true },
    { "name": "write", "enabled": true }
  ]
}

json
{
  "type": "agent_toolset_20260401",
  "configs": [
    {
      "type": "web_search",
      "name": "web_search",
      "allowed_domains": ["docs.example.com", "arxiv.org"],
      "user_location": {
        "type": "approximate",
        "country": "US",
        "timezone": "America/Los_Angeles"
      }
    },
    {
      "type": "web_fetch",
      "name": "web_fetch",
      "blocked_domains": ["ads.example.com"],
      "max_content_tokens": 50000
    }
  ]
}

bash cURL
  agent=$(curl -fsSL https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<'EOF'
  {
    "name": "Research Agent",
    "model": "claude-opus-5",
    "tools": [
      {
        "type": "agent_toolset_20260401",
        "configs": [
          {
            "type": "web_search",
            "name": "web_search",
            "allowed_domains": ["docs.example.com", "arxiv.org"],
            "user_location": {
              "type": "approximate",
              "country": "US",
              "timezone": "America/Los_Angeles"
            }
          },
          {
            "type": "web_fetch",
            "name": "web_fetch",
            "blocked_domains": ["ads.example.com"],
            "max_content_tokens": 50000
          }
        ]
      }
    ]
  }
  EOF
  )
  jq '.tools[0].configs' <<< "$agent"

bash CLI
  ant beta:agents create --transform tools.0.configs <<'YAML'
  name: Research Agent
  model: claude-opus-5
  tools:
    - type: agent_toolset_20260401
      configs:
        - type: web_search
          name: web_search
          allowed_domains: [docs.example.com, arxiv.org]
          user_location:
            type: approximate
            country: US
            timezone: America/Los_Angeles
        - type: web_fetch
          name: web_fetch
          blocked_domains: [ads.example.com]
          max_content_tokens: 50000
  YAML

python Python
  client = Anthropic()

  agent = client.beta.agents.create(
      name="Research Agent",
      model="claude-opus-5",
      tools=[
          {
              "type": "agent_toolset_20260401",
              "configs": [
                  {
                      "name": "web_search",
                      "allowed_domains": ["docs.example.com", "arxiv.org"],
                      "user_location": {
                          "type": "approximate",
                          "country": "US",
                          "timezone": "America/Los_Angeles",
                      },
                  },
                  {
                      "name": "web_fetch",
                      "blocked_domains": ["ads.example.com"],
                      "max_content_tokens": 50_000,
                  },
              ],
          }
      ],
  )

  for tool in agent.tools:
      if tool.type == "agent_toolset_20260401":
          print(json.dumps([config.to_dict() for config in tool.configs], indent=2))

typescript TypeScript
  const client = new Anthropic();

  const agent = await client.beta.agents.create({
    name: "Research Agent",
    model: "claude-opus-5",
    tools: [
      {
        type: "agent_toolset_20260401",
        configs: [
          {
            name: "web_search",
            allowed_domains: ["docs.example.com", "arxiv.org"],
            user_location: {
              type: "approximate",
              country: "US",
              timezone: "America/Los_Angeles"
            }
          },
          {
            name: "web_fetch",
            blocked_domains: ["ads.example.com"],
            max_content_tokens: 50_000
          }
        ]
      }
    ]
  });

  for (const tool of agent.tools) {
    if (tool.type === "agent_toolset_20260401") {
      console.log(JSON.stringify(tool.configs, null, 2));
    }
  }

csharp C#
  using Anthropic.Models.Beta.Agents;

  AnthropicClient client = new();

  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "Research Agent",
      Model = BetaManagedAgentsModel.ClaudeOpus5,
      Tools =
      [
          new BetaManagedAgentsAgentToolset20260401Params
          {
              Type = BetaManagedAgentsAgentToolset20260401ParamsType.AgentToolset20260401,
              Configs =
              [
                  new BetaManagedAgentsWebSearchToolConfigParams
                  {
                      AllowedDomains = ["docs.example.com", "arxiv.org"],
                      UserLocation = new()
                      {
                          Country = "US",
                          Timezone = "America/Los_Angeles",
                      },
                  },
                  new BetaManagedAgentsWebFetchToolConfigParams
                  {
                      BlockedDomains = ["ads.example.com"],
                      MaxContentTokens = 50_000,
                  },
              ],
          },
      ],
  });

  JsonSerializerOptions jsonOptions = new() { WriteIndented = true };
  foreach (var tool in agent.Tools)
  {
      if (tool.TryPickBetaManagedAgentsAgentToolset20260401(out var toolset))
      {
          Console.WriteLine(JsonSerializer.Serialize(toolset.Configs, jsonOptions));
      }
  }

go Go
  client := anthropic.NewClient()
  ctx := context.Background()

  agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name: "Research Agent",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID: anthropic.BetaManagedAgentsModelClaudeOpus5,
  	},
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{{
  		OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  			Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  			Configs: []anthropic.BetaManagedAgentsAgentToolConfigParamsUnion{
  				{OfWebSearch: &anthropic.BetaManagedAgentsWebSearchToolConfigParams{
  					AllowedDomains: []string{"docs.example.com", "arxiv.org"},
  					UserLocation: anthropic.BetaManagedAgentsUserLocationParam{
  						Country:  anthropic.String("US"),
  						Timezone: anthropic.String("America/Los_Angeles"),
  					},
  				}},
  				{OfWebFetch: &anthropic.BetaManagedAgentsWebFetchToolConfigParams{
  					BlockedDomains:   []string{"ads.example.com"},
  					MaxContentTokens: anthropic.Int(50000),
  				}},
  			},
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }

  for _, tool := range agent.Tools {
  	switch toolset := tool.AsAny().(type) {
  	case anthropic.BetaManagedAgentsAgentToolset20260401:
  		configs := make([]json.RawMessage, len(toolset.Configs))
  		for i, config := range toolset.Configs {
  			configs[i] = json.RawMessage(config.RawJSON())
  		}
  		output, err := json.MarshalIndent(configs, "", "  ")
  		if err != nil {
  			panic(err)
  		}
  		fmt.Println(string(output))
  	}
  }

java Java
  import com.anthropic.models.beta.agents.AgentCreateParams;
  import com.anthropic.models.beta.agents.BetaManagedAgentsAgentToolset20260401Params;
  import com.anthropic.models.beta.agents.BetaManagedAgentsModel;
  import com.anthropic.models.beta.agents.BetaManagedAgentsUserLocation;
  import com.anthropic.models.beta.agents.BetaManagedAgentsWebFetchToolConfigParams;
  import com.anthropic.models.beta.agents.BetaManagedAgentsWebSearchToolConfigParams;

  void main() {
      var client = AnthropicOkHttpClient.fromEnv();

      var agent = client.beta().agents().create(AgentCreateParams.builder()
          .name("Research Agent")
          .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
          .addTool(BetaManagedAgentsAgentToolset20260401Params.builder()
              .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
              .addConfig(BetaManagedAgentsWebSearchToolConfigParams.builder()
                  .allowedDomains(List.of("docs.example.com", "arxiv.org"))
                  .userLocation(BetaManagedAgentsUserLocation.builder()
                      .country("US")
                      .timezone("America/Los_Angeles")
                      .build())
                  .build())
              .addConfig(BetaManagedAgentsWebFetchToolConfigParams.builder()
                  .blockedDomains(List.of("ads.example.com"))
                  .maxContentTokens(50_000)
                  .build())
              .build())
          .build());

      for (var tool : agent.tools()) {
          if (tool.isAgentToolset20260401()) {
              var configs = tool.asAgentToolset20260401().configs();
              IO.println(ObjectMappers.jsonMapper().valueToTree(configs));
          }
      }
  }

php PHP
  use Anthropic\Beta\Agents\BetaManagedAgentsAgentToolset20260401;
  use Anthropic\Beta\Agents\BetaManagedAgentsAgentToolset20260401Params;
  use Anthropic\Beta\Agents\BetaManagedAgentsUserLocation;
  use Anthropic\Beta\Agents\BetaManagedAgentsWebFetchToolConfigParams;
  use Anthropic\Beta\Agents\BetaManagedAgentsWebSearchToolConfigParams;
  // ...

  $client = new Client();

  $agent = $client->beta->agents->create(
      name: 'Research Agent',
      model: 'claude-opus-5',
      tools: [
          BetaManagedAgentsAgentToolset20260401Params::with(
              type: 'agent_toolset_20260401',
              configs: [
                  BetaManagedAgentsWebSearchToolConfigParams::with(
                      allowedDomains: ['docs.example.com', 'arxiv.org'],
                      userLocation: BetaManagedAgentsUserLocation::with(
                          country: 'US',
                          timezone: 'America/Los_Angeles',
                      ),
                  ),
                  BetaManagedAgentsWebFetchToolConfigParams::with(
                      blockedDomains: ['ads.example.com'],
                      maxContentTokens: 50_000,
                  ),
              ],
          ),
      ],
  );

  foreach ($agent->tools as $tool) {
      if ($tool instanceof BetaManagedAgentsAgentToolset20260401) {
          echo json_encode($tool->configs, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), PHP_EOL;
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  agent = client.beta.agents.create(
    name: "Research Agent",
    model: "claude-opus-5",
    tools: [
      {
        type: :agent_toolset_20260401,
        configs: [
          {
            name: :web_search,
            allowed_domains: ["docs.example.com", "arxiv.org"],
            user_location: {type: :approximate, country: "US", timezone: "America/Los_Angeles"}
          },
          {
            name: :web_fetch,
            blocked_domains: ["ads.example.com"],
            max_content_tokens: 50_000
          }
        ]
      }
    ]
  )

  case agent.tools.first
  in Anthropic::Models::Beta::BetaManagedAgentsAgentToolset20260401 => toolset
    puts JSON.pretty_generate(toolset.configs.map(&:to_h))
  end
  ```
</CodeGroup>

In the Claude Console, set allowed or blocked domains from the `web_search` and `web_fetch` rows of the **Built-in tools** card on the agent form; set `max_content_tokens` and `user_location` in the **Raw** view of the agent's configuration.

In addition to `enabled` and `permission_policy`, the web tool entries accept the following settings:

| Setting              | Applies to                | Description                                                                                                                                                                                                     |
| -------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `allowed_domains`    | `web_search`, `web_fetch` | The only hosts the tool can reach. Cannot be combined with `blocked_domains` on the same entry.                                                                                                                 |
| `blocked_domains`    | `web_search`, `web_fetch` | Hosts the tool cannot reach.                                                                                                                                                                                    |
| `max_content_tokens` | `web_fetch`               | Caps the amount of fetched page content included in the context. Must be a positive integer. See [content limits](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool#content-limits). |
| `user_location`      | `web_search`              | Localizes search results. An object with the same fields as the Messages API [`user_location`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool#localization) parameter.           |

<Note>
  An environment's [`networking`](https://platform.claude.com/docs/en/managed-agents/environments#networking) settings control the sandbox's own outbound traffic. They do not affect `web_search` or `web_fetch`, which run on Anthropic's servers whether the environment is a cloud or self-hosted sandbox. The per-tool `allowed_domains` and `blocked_domains` lists are the way to restrict what these tools can reach.
</Note>

<Note>
  Organization-level web search and web fetch settings in the Claude Console apply to the Messages API and do not apply to Managed Agents sessions. To restrict an agent's web tools, configure `allowed_domains` or `blocked_domains` on its toolset instead.
</Note>

#### Domain list rules

* Set either `allowed_domains` or `blocked_domains` on an entry, not both. An entry that sets both is rejected.
* Each list holds 1 to 64 domains, each 1 to 255 characters. An empty list is rejected: to apply no restriction, omit the field or send `null`.
* Each domain is a registrable domain name, or a subdomain of one, written as a plain hostname: ASCII letters, digits, hyphens, underscores, and dots, with no scheme, port, credentials, wildcard, or whitespace, no label that begins or ends with a hyphen, and no path other than the optional `web_search` path suffix described later in this list. Use `example.com`, not `https://example.com`, `example.com:443`, or `*.example.com`. Hostnames are compared without regard to case, and a single trailing `/` is ignored.
* A listed domain matches that host and its subdomains: `example.com` covers `docs.example.com`, but `docs.example.com` does not cover `example.com` or `api.example.com`. A leading `www.` is a subdomain like any other, so `www.example.com` does not cover `example.com`; list the bare domain to cover both.
* IP addresses are not accepted in any form, whether IPv4, IPv6, bracketed, or numeric shorthand such as `127.1`. List the site's domain name instead.
* A bare top-level domain or registry suffix such as `com`, `co.uk`, or `gov.uk` is rejected, and so is a single-label name such as `intranet`. List a full domain such as `example.co.uk`.
* `localhost` and hosts ending in `.localhost`, `.local`, `.internal`, `.localdomain`, or `.invalid` are rejected.
* Use the `xn--` (Punycode) form for internationalized domain names; a domain that contains non-ASCII characters is rejected.
* A `web_fetch` domain cannot include a path: use `example.com`, not `example.com/*`. A `web_search` domain can carry a path suffix such as `example.com/blog`, in which the path cannot contain spaces, `?`, `#`, or any of the characters `$ , | ^ !`. Prefer plain hostnames for `web_search` too, because the search provider matches path suffixes as URL patterns rather than as strict host rules.
* Duplicate domains within a list are rejected. `www.example.com` and `example.com` count as different domains; see the earlier matching rule for what each covers.

#### When settings are validated

Format and limit violations are rejected with a 400 `invalid_request_error` when you [create an agent](https://platform.claude.com/docs/en/managed-agents/agent-setup#create-an-agent) or [update an agent](https://platform.claude.com/docs/en/managed-agents/agent-setup#update-an-agent), and when you create or update a session that supplies `tools`. For example, the message for an entry that sets both lists includes `Only one of allowed_domains or blocked_domains may be set.`, and the message for an empty list includes `allowed_domains: Empty list of domains is ambiguous. Provide at least one domain or null.` The message for a domain that breaks a format rule names its list and zero-based position, for example `allowed_domains.0: IP addresses are not supported; provide a plain hostname like "example.com"`.

The same requests also reject three settings that depend on the search and fetch providers: a domain in `allowed_domains` that Anthropic's crawler is not permitted to access, a `user_location.country` that the search provider does not support (the message ends in `user_location.country: not a country the search provider supports`), and a `user_location.timezone` that is not a valid IANA name. The session checks the configuration again when it first initializes the tool; if a setting that was accepted earlier is no longer valid at that point, the session emits a [`session.error`](https://platform.claude.com/docs/en/managed-agents/events-and-streaming) event and returns to `idle` without retrying. Fix the setting by [updating the session's tools](https://platform.claude.com/docs/en/managed-agents/session-operations#updating-the-agent-configuration), update the agent as well so that new sessions start with the corrected configuration, then send a new `user.message` to continue.

#### Multiagent sessions, outcomes, and mid-session updates

In a [multiagent session](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration), every domain list that applies to a thread is enforced at the same time: an agent in the roster of the coordinator is bound by its own `allowed_domains` and `blocked_domains`, by those of any agent that called it, and by the coordinator's current lists.

* Allowlists combine to the domains that all of them cover, and blocklists add together, so a roster agent can narrow what a tool reaches but never widen it. For example, a roster agent that sets `blocked_domains` keeps the coordinator's `allowed_domains` and blocks those hosts within it, and a roster agent that sets its own `allowed_domains` can reach only the hosts that both its list and the coordinator's list cover.
* If the combined allowlists have no domain in common, the tool stays available to that agent but every call fails with a `url_not_allowed` error stating that no domain is permitted, and the tool description tells the model so. Keep each roster agent's allowlist inside the coordinator's to avoid this.
* `max_content_tokens` and `user_location` are not combined: a thread uses the value from its own tool configuration if set, otherwise from the agent that called it, otherwise from the coordinator's current configuration.
* A `{"type": "self"}` roster entry has no web settings of its own and follows the coordinator's current settings.
* The grader in [outcome-driven sessions](https://platform.claude.com/docs/en/managed-agents/define-outcomes) runs without `web_search` and `web_fetch`, regardless of these settings.
* You can change the lists on an idle session by [updating its tools](https://platform.claude.com/docs/en/managed-agents/session-operations#updating-the-agent-configuration). The new lists apply to the rest of the session; in a multiagent session, every thread applies them from its next turn, while a roster agent's own lists stay as its agent definition set them when the session was created.

#### Differences from the Messages API tools

These settings use the same `allowed_domains` and `blocked_domains` vocabulary as [domain filtering](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#domain-filtering) on the Messages API server tools, with the following differences on Managed Agents:

* Each list is capped at 64 domains.
* Domains listed for `web_fetch` cannot include a path.
* Domains must be ASCII: use the `xn--` (Punycode) form for internationalized domain names. The Messages API accepts Unicode entries, though it recommends against them.
* `max_uses`, `citations`, and `cache_control` are not available on the toolset.


## Custom tools

Source: https://platform.claude.com/llms-full.txt#custom-tools-2

In addition to built-in tools, you can define custom tools. Custom tools are analogous to [user-defined client tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works#user-defined-tools-client-executed) in the Messages API.

Each custom tool defines a contract: you specify what operations are available and what they return, and Claude determines when and how to call them. The model never executes anything on its own. It emits a structured request, your code runs the operation, and the result flows back into the conversation. See [Session event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#handling-custom-tool-calls) for how to receive custom tool calls and return results during a session.

If your sessions run in a self-hosted sandbox, the environment worker can [serve custom tools from your sandbox](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#serve-custom-tools-from-your-sandbox), including tools that wrap an MCP server inside your network.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  agent=$(curl -fsSL https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<'EOF'
  {
    "name": "Weather Agent",
    "model": "claude-opus-5",
    "tools": [
      {
        "type": "agent_toolset_20260401"
      },
      {
        "type": "custom",
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {"type": "string", "description": "City name"}
          },
          "required": ["location"]
        }
      }
    ]
  }
  EOF
  )

bash CLI
    ant beta:agents create < agent.yaml

yaml
      name: Weather Agent
      model: claude-opus-5
      tools:
        - type: agent_toolset_20260401
        - type: custom
          name: get_weather
          description: Get current weather for a location
          input_schema:
            type: object
            properties:
              location:
                type: string
                description: City name
            required:
              - location

python Python
  agent = client.beta.agents.create(
      name="Weather Agent",
      model="claude-opus-5",
      tools=[
          {
              "type": "agent_toolset_20260401",
          },
          {
              "type": "custom",
              "name": "get_weather",
              "description": "Get current weather for a location",
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "location": {"type": "string", "description": "City name"},
                  },
                  "required": ["location"],
              },
          },
      ],
  )

typescript TypeScript
  const agent = await client.beta.agents.create({
    name: "Weather Agent",
    model: "claude-opus-5",
    tools: [
      { type: "agent_toolset_20260401" },
      {
        type: "custom",
        name: "get_weather",
        description: "Get current weather for a location",
        input_schema: {
          type: "object",
          properties: { location: { type: "string", description: "City name" } },
          required: ["location"]
        }
      }
    ]
  });

csharp C#
  using System.Text.Json;
  using Anthropic.Models.Beta.Agents;

  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "Weather Agent",
      Model = new("claude-opus-5"),
      Tools =
      [
          new BetaManagedAgentsAgentToolset20260401Params
          {
              Type = "agent_toolset_20260401",
          },
          new BetaManagedAgentsCustomToolParams
          {
              Type = "custom",
              Name = "get_weather",
              Description = "Get current weather for a location",
              InputSchema = new()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["location"] = JsonSerializer.SerializeToElement(
                          new { type = "string", description = "City name" }
                      ),
                  },
                  Required = ["location"],
              },
          },
      ],
  });

go Go
  agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name: "Weather Agent",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID: "claude-opus-5",
  	},
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{{
  		OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  			Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  		},
  	}, {
  		OfCustom: &anthropic.BetaManagedAgentsCustomToolParams{
  			Type:        anthropic.BetaManagedAgentsCustomToolParamsTypeCustom,
  			Name:        "get_weather",
  			Description: "Get current weather for a location",
  			InputSchema: anthropic.BetaManagedAgentsCustomToolInputSchemaParam{
  				Properties: map[string]any{
  					"location": map[string]any{
  						"type":        "string",
  						"description": "City name",
  					},
  				},
  				Required: []string{"location"},
  			},
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }
  _ = agent

java Java
  import com.anthropic.models.beta.agents.*;
  import java.util.Map;

  var agent = client.beta().agents().create(AgentCreateParams.builder()
      .name("Weather Agent")
      .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
      .addTool(BetaManagedAgentsAgentToolset20260401Params.builder()
          .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
          .build())
      .addTool(BetaManagedAgentsCustomToolParams.builder()
          .type(BetaManagedAgentsCustomToolParams.Type.CUSTOM)
          .name("get_weather")
          .description("Get current weather for a location")
          .inputSchema(BetaManagedAgentsCustomToolInputSchema.builder()
              .properties(BetaManagedAgentsCustomToolInputSchema.Properties.builder()
                  .putAdditionalProperty("location", JsonValue.from(Map.of(
                      "type", "string",
                      "description", "City name")))
                  .build())
              .addRequired("location")
              .build())
          .build())
      .build());

php PHP
  use Anthropic\Beta\Agents\BetaManagedAgentsAgentToolset20260401Params;
  use Anthropic\Beta\Agents\BetaManagedAgentsCustomToolInputSchema;
  use Anthropic\Beta\Agents\BetaManagedAgentsCustomToolParams;

  $agent = $client->beta->agents->create(
      name: 'Weather Agent',
      model: 'claude-opus-5',
      tools: [
          BetaManagedAgentsAgentToolset20260401Params::with(
              type: 'agent_toolset_20260401',
          ),
          BetaManagedAgentsCustomToolParams::with(
              type: 'custom',
              name: 'get_weather',
              description: 'Get current weather for a location',
              inputSchema: BetaManagedAgentsCustomToolInputSchema::with(
                  properties: ['location' => ['type' => 'string', 'description' => 'City name']],
                  required: ['location'],
              ),
          ),
      ],
  );

ruby Ruby
  agent = client.beta.agents.create(
    name: "Weather Agent",
    model: "claude-opus-5",
    tools: [
      {type: :agent_toolset_20260401},
      {
        type: :custom,
        name: "get_weather",
        description: "Get current weather for a location",
        input_schema: {
          type: :object,
          properties: {location: {type: "string", description: "City name"}},
          required: ["location"]
        }
      }
    ]
  )
  ```
</CodeGroup>

Once you've defined custom tools on the agent, the agent invokes them during a session.

### Best practices for custom tool definitions

* **Provide extremely detailed descriptions.** This is by far the most important factor in tool performance. Your descriptions should explain what the tool does and when to use it (and when not to). Explain what each parameter means and how it affects the tool's behavior. Call out any important caveats or limitations. The more context you can give Claude about your tools, the better it is at determining when and how to use them. Aim for three to four sentences for each tool description, more if the tool is complex.
* **Consolidate related operations into fewer tools.** Rather than creating a separate tool for every action (`create_pr`, `review_pr`, `merge_pr`), group them into a single tool with an `action` parameter. Fewer, more capable tools reduce selection ambiguity and make your tool surface easier for Claude to navigate.
* **Use meaningful namespacing in tool names.** When your tools span multiple services or resources, prefix names with the resource (for example, `db_query` or `storage_read`). This makes tool selection unambiguous as your library grows.
* **Design tool responses to return only high-signal information.** Return semantic, stable identifiers (for example, slugs or UUIDs) rather than opaque internal references, and include only the fields Claude needs to determine its next step. Bloated responses waste context and make it harder for Claude to extract what matters.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-73

<CardGroup cols={2}>
  <Card title="MCP connector" icon="link" href="https://platform.claude.com/docs/en/managed-agents/mcp-connector">
    Connect MCP servers to your agents for access to external tools and data sources.
  </Card>

  <Card title="Permission policies" icon="lock" href="https://platform.claude.com/docs/en/managed-agents/permission-policies">
    Control when agent and MCP tools execute.
  </Card>

  <Card title="Session event stream" icon="lightning" href="https://platform.claude.com/docs/en/managed-agents/events-and-streaming">
    Send events, stream responses, and interrupt or redirect your session mid-execution.
  </Card>
</CardGroup>


### Configure agent environment

---
title: Cloud environment setup
url: https://platform.claude.com/docs/en/managed-agents/environments
description: Customize cloud sandboxes for your sessions.
---

Environments define the sandbox configuration where your agent runs. You create an environment once, then reference its ID each time you start a session. Multiple sessions can share the same environment, but each session gets its own isolated sandbox (a fresh Linux container).

This page covers `type: cloud` environments. To run sandboxes on your own infrastructure, see [Self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes).

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Create an environment

Source: https://platform.claude.com/llms-full.txt#create-an-environment

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  environment=$(curl -fsS https://api.anthropic.com/v1/environments \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    --data @- <<'EOF'
  {
    "name": "python-dev",
    "config": {
      "type": "cloud",
      "networking": {"type": "unrestricted"}
    }
  }
  EOF
  )
  environment_id=$(jq -r '.id' <<< "$environment")

  echo "Environment ID: $environment_id"

bash CLI
    ant beta:environments create < python-dev.environment.yaml

yaml
      name: python-dev
      config:
        type: cloud
        networking:
          type: unrestricted

python Python
  environment = client.beta.environments.create(
      name="python-dev",
      config={
          "type": "cloud",
          "networking": {"type": "unrestricted"},
      },
  )

  print(f"Environment ID: {environment.id}")

typescript TypeScript
  const environment = await client.beta.environments.create({
    name: "python-dev",
    config: {
      type: "cloud",
      networking: { type: "unrestricted" },
    },
  });

  console.log(`Environment ID: ${environment.id}`);

csharp C#
  var environment = await client.Beta.Environments.Create(new()
  {
      Name = "python-dev",
      Config = new BetaCloudConfigParams
      {
          Networking = new BetaUnrestrictedNetwork(),
      },
  });

  Console.WriteLine($"Environment ID: {environment.ID}");

go Go
  environment, err := client.Beta.Environments.New(ctx, anthropic.BetaEnvironmentNewParams{
  	Name: "python-dev",
  	Config: anthropic.BetaEnvironmentNewParamsConfigUnion{
  		OfCloud: &anthropic.BetaCloudConfigParams{
  			Networking: anthropic.BetaCloudConfigParamsNetworkingUnion{
  				OfUnrestricted: &anthropic.BetaUnrestrictedNetworkParam{},
  			},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Printf("Environment ID: %s\n", environment.ID)

java Java
  var environment = client.beta().environments().create(EnvironmentCreateParams.builder()
      .name("python-dev")
      .config(BetaCloudConfigParams.builder()
          .networking(BetaUnrestrictedNetwork.builder().build())
          .build())
      .build());
  IO.println("Environment ID: " + environment.id());

php PHP
  $environment = $client->beta->environments->create(
      name: 'python-dev',
      config: ['type' => 'cloud', 'networking' => ['type' => 'unrestricted']],
  );
  echo "Environment ID: {$environment->id}\n";

ruby Ruby
  environment = client.beta.environments.create(
    name: "python-dev",
    config: {
      type: "cloud",
      networking: {type: "unrestricted"}
    }
  )

  puts "Environment ID: #{environment.id}"
  ```
</CodeGroup>

Use a unique, descriptive `name` so you can tell environments apart.


## Use the environment in a session

Source: https://platform.claude.com/llms-full.txt#use-the-environment-in-a-session

Pass the environment ID as a string when [creating a session](https://platform.claude.com/docs/en/managed-agents/sessions).

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  session=$(curl -fsS https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    --data @- <<EOF
  {
    "agent": "$agent_id",
    "environment_id": "$environment_id"
  }
  EOF
  )

bash CLI
  ant beta:sessions create --agent "$AGENT_ID" --environment-id "$ENVIRONMENT_ID"

python Python
  session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
  )

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id,
  });

csharp C#
  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = agent.ID,
      EnvironmentID = environment.ID,
  });

go Go
  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfString: anthropic.String(agent.ID),
  	},
  	EnvironmentID: environment.ID,
  })
  if err != nil {
  	panic(err)
  }

java Java
  var session = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(agent.id())
      .environmentId(environment.id())
      .build());

php PHP
  $session = $client->beta->sessions->create(
      agent: $agent->id,
      environmentID: $environment->id,
  );

ruby Ruby
  session = client.beta.sessions.create(
    agent: agent.id,
    environment_id: environment.id
  )
  ```
</CodeGroup>


## Configuration options

Source: https://platform.claude.com/llms-full.txt#configuration-options

### Packages

The `packages` field pre-installs packages into the sandbox before the agent starts. Packages are installed by their respective package managers and cached across sessions that share the same environment. When multiple package managers are specified, they run in alphabetical order (apt, cargo, gem, go, npm, pip). You can optionally pin specific versions. Unpinned packages install the latest version. If the environment uses `limited` [networking](https://platform.claude.com/docs/en/managed-agents/environments#networking), also set `networking.allow_package_managers` to `true`; otherwise the request is rejected with a 400 error.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  environment=$(curl -fsS https://api.anthropic.com/v1/environments \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    --data @- <<'EOF'
  {
    "name": "data-analysis",
    "config": {
      "type": "cloud",
      "packages": {
        "pip": ["pandas", "numpy", "scikit-learn"],
        "npm": ["express"]
      },
      "networking": {"type": "unrestricted"}
    }
  }
  EOF
  )

bash CLI
    ant beta:environments create < environment.yaml

yaml
      name: data-analysis
      config:
        type: cloud
        packages:
          pip:
            - pandas
            - numpy
            - scikit-learn
          npm:
            - express
        networking:
          type: unrestricted

python Python
  environment = client.beta.environments.create(
      name="data-analysis",
      config={
          "type": "cloud",
          "packages": {
              "pip": ["pandas", "numpy", "scikit-learn"],
              "npm": ["express"],
          },
          "networking": {"type": "unrestricted"},
      },
  )

typescript TypeScript
  const environment = await client.beta.environments.create({
    name: "data-analysis",
    config: {
      type: "cloud",
      packages: {
        pip: ["pandas", "numpy", "scikit-learn"],
        npm: ["express"]
      },
      networking: { type: "unrestricted" }
    }
  });

csharp C#
  using Anthropic.Models.Beta.Environments;

  var environment = await client.Beta.Environments.Create(new()
  {
      Name = "data-analysis",
      Config = new BetaCloudConfigParams
      {
          Packages = new()
          {
              Pip = ["pandas", "numpy", "scikit-learn"],
              Npm = ["express"],
          },
          Networking = new BetaUnrestrictedNetwork(),
      },
  });

go Go
  environment, err := client.Beta.Environments.New(ctx, anthropic.BetaEnvironmentNewParams{
  	Name: "data-analysis",
  	Config: anthropic.BetaEnvironmentNewParamsConfigUnion{
  		OfCloud: &anthropic.BetaCloudConfigParams{
  			Packages: anthropic.BetaPackagesParams{
  				Pip: []string{"pandas", "numpy", "scikit-learn"},
  				Npm: []string{"express"},
  			},
  			Networking: anthropic.BetaCloudConfigParamsNetworkingUnion{
  				OfUnrestricted: &anthropic.BetaUnrestrictedNetworkParam{},
  			},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }
  _ = environment

java Java
  import com.anthropic.models.beta.environments.*;
  import java.util.List;

  var environment = client.beta().environments().create(EnvironmentCreateParams.builder()
      .name("data-analysis")
      .config(BetaCloudConfigParams.builder()
          .packages(BetaPackagesParams.builder()
              .pip(List.of("pandas", "numpy", "scikit-learn"))
              .npm(List.of("express"))
              .build())
          .networking(BetaUnrestrictedNetwork.builder().build())
          .build())
      .build());

php PHP
  $environment = $client->beta->environments->create(
      name: 'data-analysis',
      config: [
          'type' => 'cloud',
          'packages' => [
              'pip' => ['pandas', 'numpy', 'scikit-learn'],
              'npm' => ['express'],
          ],
          'networking' => ['type' => 'unrestricted'],
      ],
  );

ruby Ruby
  environment = client.beta.environments.create(
    name: "data-analysis",
    config: {
      type: "cloud",
      packages: {
        pip: %w[pandas numpy scikit-learn],
        npm: %w[express]
      },
      networking: {type: "unrestricted"}
    }
  )

bash cURL
  curl -fsS https://api.anthropic.com/v1/environments \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d '{
      "name": "api-access",
      "config": {
        "type": "cloud",
        "networking": {
          "type": "limited",
          "allowed_hosts": ["api.example.com"],
          "allow_mcp_servers": true,
          "allow_package_managers": true
        }
      }
    }'

bash CLI
    ant beta:environments create < environment.yaml

yaml
      name: api-access
      config:
        type: cloud
        networking:
          type: limited
          allowed_hosts:
            - api.example.com
          allow_mcp_servers: true
          allow_package_managers: true

python Python
  environment = client.beta.environments.create(
      name="api-access",
      config={
          "type": "cloud",
          "networking": {
              "type": "limited",
              "allowed_hosts": ["api.example.com"],
              "allow_mcp_servers": True,
              "allow_package_managers": True,
          },
      },
  )

typescript TypeScript
  const environment = await client.beta.environments.create({
    name: "api-access",
    config: {
      type: "cloud",
      networking: {
        type: "limited",
        allowed_hosts: ["api.example.com"],
        allow_mcp_servers: true,
        allow_package_managers: true
      }
    }
  });

csharp C#
  using Anthropic.Models.Beta.Environments;

  var environment = await client.Beta.Environments.Create(new()
  {
      Name = "api-access",
      Config = new BetaCloudConfigParams
      {
          Networking = new BetaLimitedNetworkParams
          {
              AllowedHosts = ["api.example.com"],
              AllowMcpServers = true,
              AllowPackageManagers = true,
          },
      },
  });

go Go
  environment, err := client.Beta.Environments.New(ctx, anthropic.BetaEnvironmentNewParams{
  	Name: "api-access",
  	Config: anthropic.BetaEnvironmentNewParamsConfigUnion{
  		OfCloud: &anthropic.BetaCloudConfigParams{
  			Networking: anthropic.BetaCloudConfigParamsNetworkingUnion{
  				OfLimited: &anthropic.BetaLimitedNetworkParams{
  					AllowedHosts:         []string{"api.example.com"},
  					AllowMCPServers:      anthropic.Bool(true),
  					AllowPackageManagers: anthropic.Bool(true),
  				},
  			},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }
  _ = environment

java Java
  import com.anthropic.models.beta.environments.*;
  import java.util.List;

  var environment = client.beta().environments().create(EnvironmentCreateParams.builder()
      .name("api-access")
      .config(BetaCloudConfigParams.builder()
          .networking(BetaLimitedNetworkParams.builder()
              .allowedHosts(List.of("api.example.com"))
              .allowMcpServers(true)
              .allowPackageManagers(true)
              .build())
          .build())
      .build());

php PHP
  $environment = $client->beta->environments->create(
      name: 'api-access',
      config: [
          'type' => 'cloud',
          'networking' => [
              'type' => 'limited',
              'allowed_hosts' => ['api.example.com'],
              'allow_mcp_servers' => true,
              'allow_package_managers' => true,
          ],
      ],
  );

ruby Ruby
  environment = client.beta.environments.create(
    name: "api-access",
    config: {
      type: "cloud",
      networking: {
        type: "limited",
        allowed_hosts: %w[api.example.com],
        allow_mcp_servers: true,
        allow_package_managers: true
      }
    }
  )
  ```
</CodeGroup>

<Info>
  For production deployments, use `limited` networking with an explicit `allowed_hosts` list. Follow the principle of least privilege by granting only the minimum network access your agent requires, and regularly audit your allowed domains.
</Info>

When using `limited` networking:

* `allowed_hosts` specifies domains the sandbox can reach. Specify bare hostnames or wildcard patterns (such as `*.example.com`). Do not include a URL scheme, port, or path.
* `allow_mcp_servers` allows outbound access to MCP server endpoints configured on the agent, beyond those listed in the `allowed_hosts` array. Defaults to `false`.
* `allow_package_managers` allows outbound access to public package registries (such as PyPI and npm) beyond those listed in the `allowed_hosts` array. Defaults to `false`. Set it to `true` whenever the environment specifies `packages`; otherwise the request is rejected with a 400 error, even if the registry hosts are listed in `allowed_hosts`.


## Environment lifecycle

Source: https://platform.claude.com/llms-full.txt#environment-lifecycle

* Environments persist until explicitly archived or deleted.
* Each session gets its own sandbox instance, even when multiple sessions reference the same environment. Sessions do not share filesystem state.
* Environments are not versioned. If you update an environment frequently, keep your own record of the changes so you can tell which configuration each session used.


## Manage environments

Source: https://platform.claude.com/llms-full.txt#manage-environments

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  # List environments
  environments=$(curl -fsS https://api.anthropic.com/v1/environments \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01")

  # Retrieve a specific environment
  env=$(curl -fsS "https://api.anthropic.com/v1/environments/$environment_id" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01")

  # Archive an environment (read-only, existing sessions continue)
  curl -fsS -X POST "https://api.anthropic.com/v1/environments/$environment_id/archive" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

  # Delete an environment (only if no sessions reference it)
  curl -fsS -X DELETE "https://api.anthropic.com/v1/environments/$environment_id" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
  # List environments
  ant beta:environments list

  # Retrieve a specific environment
  ant beta:environments retrieve --environment-id "$ENVIRONMENT_ID"

  # Archive an environment (read-only, existing sessions continue)
  ant beta:environments archive --environment-id "$ENVIRONMENT_ID"

  # Delete an environment (only if no sessions reference it)
  ant beta:environments delete --environment-id "$ENVIRONMENT_ID"

python Python
  # List environments
  environments = client.beta.environments.list()

  # Retrieve a specific environment
  env = client.beta.environments.retrieve(environment.id)

  # Archive an environment (read-only, existing sessions continue)
  client.beta.environments.archive(environment.id)

  # Delete an environment (only if no sessions reference it)
  client.beta.environments.delete(environment.id)

typescript TypeScript
  // List environments
  const environments = await client.beta.environments.list();

  // Retrieve a specific environment
  const env = await client.beta.environments.retrieve(environment.id);

  // Archive an environment (read-only, existing sessions continue)
  await client.beta.environments.archive(environment.id);

  // Delete an environment (only if no sessions reference it)
  await client.beta.environments.delete(environment.id);

csharp C#
  // List environments
  var environments = await client.Beta.Environments.List();

  // Retrieve a specific environment
  var env = await client.Beta.Environments.Retrieve(environment.ID);

  // Archive an environment (read-only, existing sessions continue)
  await client.Beta.Environments.Archive(environment.ID);

  // Delete an environment (only if no sessions reference it)
  await client.Beta.Environments.Delete(environment.ID);

go Go
  // List environments
  environments, err := client.Beta.Environments.List(ctx, anthropic.BetaEnvironmentListParams{})
  // ...

  // Retrieve a specific environment
  env, err := client.Beta.Environments.Get(ctx, environment.ID, anthropic.BetaEnvironmentGetParams{})
  // ...

  // Archive an environment (read-only, existing sessions continue)
  _, err = client.Beta.Environments.Archive(ctx, environment.ID, anthropic.BetaEnvironmentArchiveParams{})
  // ...

  // Delete an environment (only if no sessions reference it)
  _, err = client.Beta.Environments.Delete(ctx, environment.ID, anthropic.BetaEnvironmentDeleteParams{})

java Java
  // List environments
  var environments = client.beta().environments().list();
  // Retrieve a specific environment
  var env = client.beta().environments().retrieve(environment.id());
  // Archive an environment (read-only, existing sessions continue)
  client.beta().environments().archive(environment.id());
  // Delete an environment (only if no sessions reference it)
  client.beta().environments().delete(environment.id());

php PHP
  // List environments
  $environments = $client->beta->environments->list();
  // Retrieve a specific environment
  $env = $client->beta->environments->retrieve($environment->id);
  // Archive an environment (read-only, existing sessions continue)
  $client->beta->environments->archive($environment->id);
  // Delete an environment (only if no sessions reference it)
  $client->beta->environments->delete($environment->id);

ruby Ruby
  # List environments
  environments = client.beta.environments.list

  # Retrieve a specific environment
  env = client.beta.environments.retrieve(environment.id)

  # Archive an environment (read-only, existing sessions continue)
  client.beta.environments.archive(environment.id)

  # Delete an environment (only if no sessions reference it)
  client.beta.environments.delete(environment.id)
  ```
</CodeGroup>


## Pre-installed runtimes

Source: https://platform.claude.com/llms-full.txt#pre-installed-runtimes

Cloud sandboxes include common language runtimes, databases, and command-line tools out of the box. See [Cloud sandbox reference](https://platform.claude.com/docs/en/managed-agents/cloud-sandboxes-reference) for the full list.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-74

<CardGroup cols={2}>
  <Card title="Cloud sandbox reference" icon="book" href="https://platform.claude.com/docs/en/managed-agents/cloud-sandboxes-reference">
    Pre-installed packages, databases, and utilities available in cloud sandboxes.
  </Card>

  <Card title="Start a session" icon="play" href="https://platform.claude.com/docs/en/managed-agents/sessions">
    Create a session to run your agent and start running tasks.
  </Card>
</CardGroup>


---
title: Cloud sandbox reference
url: https://platform.claude.com/docs/en/managed-agents/cloud-sandboxes-reference
description: Pre-installed packages, databases, and utilities available in cloud sandboxes.
---

Cloud sandboxes run as isolated Linux containers on Anthropic-managed infrastructure. They come pre-installed with a comprehensive set of programming languages, databases, and utilities. The agent can use these immediately without any installation steps.

These specifications apply to `cloud` environments. Self-hosted sandboxes run on your infrastructure with whatever your worker provides.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Programming languages

Source: https://platform.claude.com/llms-full.txt#programming-languages

| Language | Version                     | Package manager      |
| -------- | --------------------------- | -------------------- |
| Python   | 3.10, 3.11, 3.12, and 3.13  | pip, uv, poetry      |
| Node.js  | 20, 21, and 22 (default)    | npm, yarn, pnpm, bun |
| Go       | 1.24 (default) and 1.25     | go modules           |
| Rust     | Stable toolchain (rustup)   | cargo                |
| Java     | OpenJDK 21                  | maven, gradle        |
| Ruby     | 3.1, 3.2, and 3.3 (default) | bundler, gem         |
| PHP      | 8.3                         | composer             |
| C/C++    | GCC 13 and Clang            | make, cmake, ninja   |

Common Python data and document libraries, including NumPy, pandas, Matplotlib, openpyxl, python-docx, python-pptx, and pypdf, are installed for the `python3` interpreter.


## Databases

Source: https://platform.claude.com/llms-full.txt#databases

| Database      | Description                                                                   |
| ------------- | ----------------------------------------------------------------------------- |
| PostgreSQL 16 | Server and `psql` client are installed. The server is not running by default. |
| Redis 7       | Server and `redis-cli` are installed. The server is not running by default.   |
| SQLite        | Available through language bindings, such as Python's `sqlite3` module.       |


## Utilities

Source: https://platform.claude.com/llms-full.txt#utilities

### System tools

* `git` - Version control
* `curl`, `wget` - HTTP clients
* `jq`, `yq` - JSON and YAML processing
* `tar`, `zip`, `unzip` - Archive tools
* `tmux` - Terminal multiplexer

### Development tools

* `make`, `cmake` - Build systems
* `docker` - Container management (limited availability)
* `ripgrep` (`rg`) - Fast file search

### Text processing

* `sed`, `awk`, `grep` - Stream editors
* `vim`, `nano` - Text editors
* `diff`, `patch` - File comparison

### Document and media processing

* `ffmpeg` - Audio and video processing
* ImageMagick (`convert`, `identify`) - Image manipulation
* `pandoc` - Document conversion
* LibreOffice (headless) - Office document conversion
* Poppler utilities (`pdftotext`, `pdftoppm`) and `qpdf` - PDF processing
* `tesseract` - Optical character recognition (English language data)
* TeX Live (`pdflatex`, `xelatex`, `latexmk`) - Typesetting

### Browser automation

* Playwright (Python and Node.js) - Browser automation library
* Chromium (`/opt/pw-browsers/chromium`) - Browser used by Playwright, not on `PATH`

The sandbox sets `PLAYWRIGHT_BROWSERS_PATH` to `/opt/pw-browsers`, so the pre-installed Playwright packages find Chromium there without configuration. The Python package is installed for the `python3` interpreter. Use the pre-installed packages rather than installing another Playwright version, which would look for a browser build that is not present. Firefox and WebKit are not installed.


## Sandbox specifications

Source: https://platform.claude.com/llms-full.txt#sandbox-specifications

| Property         | Value                                                                                                                                                                                                         |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Operating system | Ubuntu 24.04 LTS                                                                                                                                                                                              |
| Architecture     | x86\_64 (amd64)                                                                                                                                                                                               |
| Memory           | Up to 8 GB                                                                                                                                                                                                    |
| Disk space       | Up to 10 GB                                                                                                                                                                                                   |
| Network          | API-created environments default to [`unrestricted` networking](https://platform.claude.com/docs/en/managed-agents/environments#networking); sandboxes provisioned through Claude Studio default to `limited` |


### Configure agent environment > Self-hosted sandboxes

---
title: Security model
url: https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes-security
description: Shared responsibility model for self-hosted sandbox environments.
---

Anthropic secures the control plane across all environments: session and work queue integrity, multitenant isolation, and agent-context minimization. When you self-host, the following responsibilities fall to you.


## What you own

Source: https://platform.claude.com/llms-full.txt#what-you-own

* **Sandbox image quality and runtime hardening.** Anthropic does not inspect or verify your sandbox image. Follow best practices such as dropping unnecessary Linux capabilities, running as a non-root user, and using a read-only root filesystem.
* **Network egress controls.** Your sandbox's network access is determined by your VPC and firewall rules. Without egress restrictions, a compromised tool execution can reach arbitrary external hosts. Restrict outbound traffic to only the endpoints your tools require.
* **Service key storage and rotation.** The environment service key (`ANTHROPIC_ENVIRONMENT_KEY`) authorizes polling your environment's work queue and submitting results back to sessions. Store it in a secrets manager, not in environment files or sandbox images. Rotate it immediately if you suspect exposure.
* **Isolating untrusted workloads.** The environment service key is scoped to one environment's work queue. If you run untrusted code inside your sandbox, consider provisioning a separate workspace and environment for each trust boundary. This limits each key to a single user's sessions instead of a shared pool.
* **Per-session credentials.** Each work item your worker claims can carry a per-session `secret`, which the SDK worker uses in place of the environment service key. Access to [memory stores](https://platform.claude.com/docs/en/managed-agents/memory) requires the `secret`: the memory store endpoints reject the environment key (see [Use memory stores](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores)). Pass the `secret` only into the sandbox that serves that session, keep it out of images and shared volumes, and never log it.
* **Tool-execution blast radius.** Tools run inside your sandbox with whatever permissions your process has. Apply least privilege to the process user and mount only the directories your tools require.
* **Log retention and session content.** Conversation content and tool outputs pass through your worker and stay in your environment. You are responsible for retaining, redacting, or deleting that data in compliance with your own policies. Anthropic has no visibility into what your worker does with session content once delivered.
* **Memory store contents.** [Memory stores](https://platform.claude.com/docs/en/managed-agents/memory) remain hosted by Anthropic, including their version history. When a session attaches one, the worker keeps a working copy under `/mnt/memory/` in your sandbox for the session's duration and syncs changes back. The worker deletes that copy when the session ends, but a worker that exits without running its teardown leaves it behind. Cleaning up leftover copies, the permissions on that path, and isolation between sessions that share a filesystem are your responsibility.
* **Read-only memory stores.** A store attached with `read_only` access is protected from upload, not from local modification. The worker's `write` and `edit` tools refuse to write under its directory, nothing there syncs back, and the memory store endpoints reject writes to it made with the session's `secret`. Other processes in the sandbox can still change the local copy: commands the agent runs through the `bash` tool, and [custom tools](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#serve-custom-tools-from-your-sandbox) or MCP servers you serve from the sandbox, which run with the worker's permissions. Later tool calls in that session read the changed copy until that memory next changes in the store. If the agent must not be able to alter even its local view of such a store, disable the `bash` tool for that agent and give it no custom tool that writes to the sandbox's filesystem.


## What Anthropic cannot do for you

Source: https://platform.claude.com/llms-full.txt#what-anthropic-cannot-do-for-you

* **Know that your key leaked.** Anthropic can detect anomalous usage patterns, but cannot know your key was compromised. If you suspect `ANTHROPIC_ENVIRONMENT_KEY` leaked, revoke it and generate a replacement immediately. Revocation is validated on every request, so it takes effect on the worker's next call.
* **Verify your worker build.** Anthropic does not inspect your sandbox image or runtime. A supply-chain compromise in your image is not detectable from the control plane.
* **Isolate tools inside your sandbox.** Anthropic's security boundary stops at the sandbox. How you isolate individual tool executions from each other inside that boundary is entirely your responsibility.
* **Enforce data retention in your environment.** Once session content reaches your worker, it is outside Anthropic's data lifecycle controls.


---
title: Self-hosted sandboxes
url: https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes
description: Run Claude Managed Agents sessions in self-hosted sandboxes, keeping tool execution, files, and network egress in your own infrastructure.
---

By default, Managed Agents executes tools and code inside [Anthropic-managed cloud sandboxes](https://platform.claude.com/docs/en/managed-agents/cloud-sandboxes-reference). Self-hosted sandboxes keep the orchestration on Anthropic's side but move tool execution into infrastructure you control, so the agent's code, filesystem, and network egress never leave your environment.

Tool execution stays on your host: the filesystem the agent reads and writes, the processes it spawns, and the network it can reach are all under your control. Tool inputs and outputs still flow to Anthropic's control plane (where Claude runs) so the model can see results and determine what to do next. The agent's [skills](https://platform.claude.com/docs/en/managed-agents/skills) and the contents of any [memory stores](https://platform.claude.com/docs/en/managed-agents/memory) attached to the session are stored by Anthropic and copied into your sandbox for the session; changes the agent makes to memory files sync back to the store. See the [security model](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes-security) for the full data-flow boundary.

<Note>
  Self-hosted sandboxes support all Claude models available in Managed Agents, including Claude Opus 4.8 and Claude Opus 5. The model is configured on the [agent](https://platform.claude.com/docs/en/managed-agents/agent-setup), not the environment.
</Note>


## How it differs from cloud environments

Source: https://platform.claude.com/llms-full.txt#how-it-differs-from-cloud-environments

|                               | Cloud environment                      | Self-hosted sandbox                                       |
| ----------------------------- | -------------------------------------- | --------------------------------------------------------- |
| Where tools run               | Anthropic-managed sandboxes            | Your infrastructure                                       |
| Network reach                 | Anthropic's egress controls            | Your network policy                                       |
| File and GitHub repo mounting | Managed by Anthropic                   | Managed by you                                            |
| Memory stores                 | Mounted by Anthropic at `/mnt/memory/` | Downloaded to `/mnt/memory/` and synced by the SDK worker |
| Lifecycle                     | Managed by Anthropic                   | Managed by you                                            |

Self-hosting is a good fit when the agent needs to operate on data that cannot leave your network boundary, reach internal services that are not publicly routable, or run under your organization's own compliance and audit controls.

For Zero Data Retention and HIPAA BAA eligibility, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility).


## When to combine with MCP tunnels

Source: https://platform.claude.com/llms-full.txt#when-to-combine-with-mcp-tunnels

Self-hosting controls *where the agent's code executes*. [MCP tunnels](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview) control *how Anthropic reaches MCP servers in your network*. They are independent: a session running in Anthropic's cloud sandboxes can still reach private MCP servers through a tunnel, and a self-hosted session can use either tunneled or public MCP servers. Use both when you want execution and tool access to stay inside your boundary. To give the agent tools from an MCP server inside your network without running a tunnel, you can also [wrap the server as custom tools](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#wrap-an-mcp-server-as-custom-tools) served by your worker.


## Environment worker

Source: https://platform.claude.com/llms-full.txt#environment-worker

<Tip>
  This guide describes how to build a worker with any generic sandboxing platform. Additional, platform-specific guides are available for [AWS Lambda MicroVMs](https://docs.aws.amazon.com/lambda/latest/dg/microvms-integrations-claude-managed-agents.html), [Blaxel](https://docs.blaxel.ai/Tutorials/Claude-Managed-Agents), [Cloudflare](https://developers.cloudflare.com/sandbox/claude-managed-agents/), [Daytona](https://www.daytona.io/docs/en/guides/claude/claude-managed-agents), [E2B](https://e2b.dev/docs/agents/claude-managed-agents), [Fly.io](https://docs.sprites.dev/integrations/claude-managed-agents/), [GKE Agent Sandbox](https://github.com/GoogleCloudPlatform/kubernetes-engine-samples/tree/main/ai-ml/anthropic-agent-sandbox), [Modal](https://github.com/modal-labs/claude-managed-agents-modal-sandbox), [Namespace](https://namespace.so/docs/integrations/claude), [Superserve](https://docs.superserve.ai/integrations/managed-agents/claude-managed-agents), and [Vercel](https://vercel.com/kb/guide/run-claude-managed-agent-tools-with-vercel-sandbox).
</Tip>

An environment worker is a process you run on your own infrastructure. It receives tool execution requests from Anthropic and runs them locally. The `self_hosted` environment acts as a work queue: when a [session](https://platform.claude.com/docs/en/managed-agents/sessions) is assigned to it, Anthropic enqueues the session as a work item. Your worker claims work items from that queue, spawns an execution context for each one, downloads the agent's [skills](https://platform.claude.com/docs/en/managed-agents/skills) (reusable, filesystem-based resources that give the agent domain-specific expertise), runs the tool calls, and posts the results back.

Work items are claimed by polling the environment's queue: either by an **always-on worker** that polls continuously, or a **webhook-triggered handler** that wakes on `session.status_run_started` and starts polling.

The CLI and SDK both ship pre-built workers. The `ant` CLI supports the always-on pattern only; the SDK supports both always-on and webhook-triggered. Both are configurable: see [Self-hosted worker](https://platform.claude.com/docs/en/managed-agents/reference#self-hosted-worker) in the reference for CLI flags, and [SDK helpers](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#sdk-helpers) on this page for the SDK options. For more control, call the [Environments Work endpoints](https://platform.claude.com/docs/en/api/beta/environments/work) directly and implement your own worker.

### Sandbox filesystem

* **`/workspace`:** the system default working directory for tool execution and skill download. The CLI's `--workdir` flag defaults to the current directory; pass `--workdir /workspace` to match the system default. Skills are downloaded to `<workdir>/skills/<name>/`. If you use a different working directory, update your agent's system prompt so Claude can locate the skill files.
* **Outputs:** on self-hosted environments the session's system prompt omits the `/mnt/session/outputs` instruction used on Anthropic-managed sandboxes, so final deliverables land wherever the agent writes them in your sandbox filesystem, typically under the working directory.
* **`/mnt/memory/`:** memory stores attached to the session are materialized here by the SDK worker, one directory per store at the store's `mount_path` (for example, `/mnt/memory/user-preferences/`). The worker creates these directories when it claims the session and removes them when the session ends; see [Use memory stores](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores).


## Before you begin

Source: https://platform.claude.com/llms-full.txt#before-you-begin-4

You need:

* **An existing agent.** If you don't have one, complete the [Quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart) first and note its agent ID.
* **A Linux host** with `/bin/bash` at that exact path. The worker's bash tool invokes it directly, without consulting `PATH`. The TypeScript SDK additionally requires `unzip` and `tar` on the `PATH` and Node.js 22 or later; the Python and Go SDKs use their standard libraries for archive extraction and have no additional binary requirements.
* **The `ant` CLI or an Anthropic SDK** (Python, TypeScript, or Go) on the worker host.
* **Credentials:** an environment key (generated in the Console in the steps that follow) authenticates the worker to its queue; your Claude API key creates sessions and reads queue stats from outside the worker host. Key generation is Console-only. Claimed work items also carry a per-session `secret` that the worker uses to mount [memory stores](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores); you don't generate it, but in the sandbox-per-session pattern you forward it into the sandbox yourself (see [Run one sandbox per session](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#run-one-sandbox-per-session)).
* **For memory stores, a prepared host.** If sessions on this environment will attach memory stores, prepare `/mnt/memory` on the worker host before you start the worker; see [Prepare the host](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#prepare-the-host).

<Note>
  On [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), the worker authenticates with AWS IAM (SigV4) or an [API key generated in the AWS Console](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws#api-key-authentication), not an environment key. Attach the [`AnthropicSelfHostedEnvironmentAccess`](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions#managed-policies) managed policy to the IAM principal your worker runs as. Environment keys generated in the Claude Console don't work with the Claude Platform on AWS endpoint.

  Memory stores cannot be attached to sessions on self-hosted environments on Claude Platform on AWS.
</Note>

<Steps>
  <Step title="Create a self-hosted environment">
    In the [Console](https://platform.claude.com/workspaces/default/environments): **Workspace > Environments > New > Self-hosted**

    Or through the API:

    <CodeGroup>
      ```bash cURL
      curl -sS --fail-with-body https://api.anthropic.com/v1/environments \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        -H "content-type: application/json" \
        -d '{
          "name": "self-hosted",
          "config": {"type": "self_hosted"}
        }'

bash CLI
        ant beta:environments create < environment.yaml

yaml
          name: self-hosted
          config:
            type: self_hosted

python Python
      client = anthropic.Anthropic()

      environment = client.beta.environments.create(
          name="self-hosted", config={"type": "self_hosted"}
      )
      print(environment.id)

typescript TypeScript
      const client = new Anthropic();

      const environment = await client.beta.environments.create({
        name: "self-hosted",
        config: { type: "self_hosted" }
      });
      console.log(environment.id);

csharp C#
      using Anthropic.Models.Beta.Environments;

      var client = new AnthropicClient();

      var environment = await client.Beta.Environments.Create(
          new EnvironmentCreateParams
          {
              Name = "self-hosted",
              Config = new BetaSelfHostedConfigParams(),
          }
      );
      Console.WriteLine(environment.ID);

go Go
      client := anthropic.NewClient()

      environment, err := client.Beta.Environments.New(context.Background(), anthropic.BetaEnvironmentNewParams{
      	Name: "self-hosted",
      	Config: anthropic.BetaEnvironmentNewParamsConfigUnion{
      		OfSelfHosted: &anthropic.BetaSelfHostedConfigParams{},
      	},
      })
      if err != nil {
      	panic(err)
      }
      fmt.Println(environment.ID)

java Java
      import com.anthropic.models.beta.environments.BetaSelfHostedConfigParams;
      import com.anthropic.models.beta.environments.EnvironmentCreateParams;

      void main() {
          var client = AnthropicOkHttpClient.fromEnv();

          var environment = client.beta().environments().create(
              EnvironmentCreateParams.builder()
                  .name("self-hosted")
                  .config(BetaSelfHostedConfigParams.builder().build())
                  .build()
          );
          IO.println(environment.id());
      }

php PHP
      $client = new Anthropic\Client();

      $environment = $client->beta->environments->create(
          name: 'self-hosted',
          config: ['type' => 'self_hosted'],
      );
      echo $environment->id, PHP_EOL;

ruby Ruby
      client = Anthropic::Client.new

      environment = client.beta.environments.create(
        name: "self-hosted",
        config: {type: :self_hosted}
      )
      puts environment.id

bash
    export ANTHROPIC_ENVIRONMENT_KEY="sk-ant-oat01-..."
    export ANTHROPIC_ENVIRONMENT_ID="env_..."
    ```
  </Step>
</Steps>

<Note>
  Skills can include executables that the agent may run directly. The CLI and SDK workers preserve the executable permissions recorded in the skill bundle when they extract it. If you implement skills download manually, you are responsible for setting executable permissions.
</Note>


## Run a worker

Source: https://platform.claude.com/llms-full.txt#run-a-worker

Choose **always-on** for the simplest setup: a long-running process polls the queue continuously and needs only outbound HTTPS. Choose **webhook-triggered** to avoid running an idle poller; it requires a webhook endpoint that Anthropic can reach (see [Webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks) for endpoint setup and signature verification).

<Tabs>
  <Tab title="Always-on (ant CLI)">
    <Steps>
      <Step title="Install the ant CLI">
        Run this on the worker host.

        <Tabs>
          <Tab title="curl (Linux/WSL)">
            For Linux environments, download the release binary directly.

You can find all releases on the [GitHub releases page](https://github.com/anthropics/anthropic-cli/releases).
          </Tab>

          <Tab title="Homebrew (macOS)">

</Tab>
        </Tabs>
      </Step>

      <Step title="Run the worker">
        **In-process**

        `ant beta:worker poll` claims work items assigned to the environment, downloads skills, executes tool calls in the working directory, and posts results back. It reads `ANTHROPIC_ENVIRONMENT_KEY` and `ANTHROPIC_ENVIRONMENT_ID` from the environment.

The worker exits cleanly on SIGTERM or SIGINT: it cancels any in-flight tool call, posts its error result, and releases the work item before stopping.

        **Sandbox per session**

        If you need stronger isolation (a fresh filesystem, resource limits, or per-session network controls), run each session in its own sandbox. Build an image with `ant` installed and `ant beta:worker run` as the entrypoint. The base image must provide `/bin/bash`; `curl` is only used at build time. When a sandbox starts, it reads session details from environment variables, handles that session, and exits:

Then write a spawn script that forwards session details into a fresh sandbox. The poller injects `ANTHROPIC_SESSION_ID`, `ANTHROPIC_WORK_ID`, `ANTHROPIC_ENVIRONMENT_ID`, and `ANTHROPIC_ENVIRONMENT_KEY` into the script's environment, and writes the claimed work item to the script's standard input as JSON, including the work item's per-session `secret` when Anthropic issued one. `ANTHROPIC_BASE_URL` is optional and is passed through only if it was set on the poller host; it overrides the default API endpoint. In the example, `/host/outputs` is a host directory you choose; it is bind-mounted to the sandbox's working directory (`/workspace`) so you can retrieve session deliverables after the sandbox exits. On self-hosted environments the agent writes deliverables under the working directory rather than `/mnt/session/outputs` (see [Sandbox filesystem](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#sandbox-filesystem)), so mounting the working directory is what captures them; the mount also picks up the downloaded `skills/` tree and any intermediate files the agent creates.

The `ant beta:worker run` entrypoint does not mount [memory stores](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores). If sessions on this environment attach memory stores, keep the poller, but build the per-session image around the SDK worker and extend the spawn script to forward the work item's `secret` into the sandbox, as shown in [Run one sandbox per session](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#run-one-sandbox-per-session).

        Start the poller pointing at the script:

</Step>
    </Steps>
  </Tab>

  <Tab title="Always-on (SDK)">
    <Steps>
      <Step title="Run the worker">
        `EnvironmentWorker` claims work items assigned to the environment, downloads skills, executes tool calls in the working directory, and posts results back. Authenticate with the environment key you generated in [Before you begin](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#before-you-begin).

        <CodeGroup exclude="shell">
          ```python Python
          import asyncio
          import contextlib
          import os
          import signal
          from anthropic import AsyncAnthropic
          from anthropic.lib.environments import EnvironmentWorker


          async def main() -> None:
              environment_key = os.environ["ANTHROPIC_ENVIRONMENT_KEY"]
              environment_id = os.environ["ANTHROPIC_ENVIRONMENT_ID"]
              async with AsyncAnthropic(auth_token=environment_key) as client:
                  worker = EnvironmentWorker(
                      client,
                      environment_id=environment_id,
                      environment_key=environment_key,
                      workdir="/workspace",
                  )
                  task = asyncio.create_task(worker.run())
                  # Cancelling the task, rather than killing the process, lets the worker stop its
                  # in-flight work item and upload changed memory files before it exits.
                  loop = asyncio.get_running_loop()
                  for signum in (signal.SIGINT, signal.SIGTERM):
                      loop.add_signal_handler(signum, task.cancel)
                  with contextlib.suppress(asyncio.CancelledError):
                      await task


          asyncio.run(main())

typescript TypeScript
          import Anthropic from "@anthropic-ai/sdk";
          import { EnvironmentWorker } from "@anthropic-ai/sdk/helpers/beta/environments";

          const environmentKey = process.env.ANTHROPIC_ENVIRONMENT_KEY!;
          const environmentId = process.env.ANTHROPIC_ENVIRONMENT_ID!;
          const client = new Anthropic({ authToken: environmentKey });
          const controller = new AbortController();
          // Aborting on either signal lets the worker upload changed memory files and remove its
          // store directories before the process exits.
          process.once("SIGINT", () => controller.abort());
          process.once("SIGTERM", () => controller.abort());

          await new EnvironmentWorker({
            client,
            environmentId,
            environmentKey,
            workdir: "/workspace",
            signal: controller.signal
          }).run();

csharp C#
          // EnvironmentWorker is not currently available in the C# SDK. See the Always-on (ant CLI) tab.

go Go
          package main

          import (
          	"context"
          	"log"
          	"os"
          	"os/signal"
          	"syscall"

          	"github.com/anthropics/anthropic-sdk-go"
          	"github.com/anthropics/anthropic-sdk-go/lib/environments"
          	"github.com/anthropics/anthropic-sdk-go/option"
          )

          func main() {
          	environmentKey := os.Getenv("ANTHROPIC_ENVIRONMENT_KEY")
          	environmentID := os.Getenv("ANTHROPIC_ENVIRONMENT_ID")

          	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
          	defer stop()

          	client := anthropic.NewClient(option.WithAuthToken(environmentKey))

          	worker := environments.NewEnvironmentWorker(client, environments.EnvironmentWorkerOptions{
          		EnvironmentID:  environmentID,
          		EnvironmentKey: environmentKey,
          		Workdir:        "/workspace",
          	})
          	if err := worker.Run(ctx); err != nil {
          		log.Fatalf("worker: %v", err)
          	}
          }

java Java
          // EnvironmentWorker is not currently available in the Java SDK. See the Always-on (ant CLI) tab.

php PHP
          // EnvironmentWorker is not currently available in the PHP SDK. See the Always-on (ant CLI) tab.

ruby Ruby
          # EnvironmentWorker is not currently available in the Ruby SDK. See the Always-on (ant CLI) tab.

bash
        export ANTHROPIC_WEBHOOK_SIGNING_KEY="whsec_..."

python Python
          import asyncio
          import os
          import anthropic
          import standardwebhooks  # installed by the anthropic[webhooks] extra

          environment_key = os.environ["ANTHROPIC_ENVIRONMENT_KEY"]
          environment_id = os.environ["ANTHROPIC_ENVIRONMENT_ID"]
          client = anthropic.AsyncAnthropic(
              auth_token=environment_key,
          )
          # Cancelled by shutdown() so an in-flight work item can upload changed memory files and
          # remove its store directories before the process exits.
          inflight: set[asyncio.Task[None]] = set()


          # Await this from the host's shutdown hook, such as an ASGI lifespan shutdown (the code after
          # `yield` in a FastAPI lifespan), which uvicorn runs on SIGTERM. uvicorn lets open requests
          # finish before that hook runs, so set --timeout-graceful-shutdown to bound the wait.
          async def shutdown() -> None:
              for task in inflight:
                  task.cancel()
              await asyncio.gather(*inflight, return_exceptions=True)


          async def handle(raw: bytes, headers: dict[str, str]) -> tuple[dict[str, str], int]:
              try:
                  event = client.beta.webhooks.unwrap(raw.decode(), headers=headers)
              except standardwebhooks.WebhookVerificationError:
                  return {"error": "signature verification failed"}, 401
              if event.data.type != "session.status_run_started":
                  return {"status": "ignored"}, 200
              task = asyncio.create_task(run_queued_work())
              inflight.add(task)
              task.add_done_callback(inflight.discard)
              try:
                  # Shielded: a dropped or timed-out delivery must not cancel the item; shutdown() does.
                  await asyncio.shield(task)
              except asyncio.CancelledError:
                  return {"status": "shutting down"}, 503
              return {"status": "ok"}, 200


          async def run_queued_work() -> None:
              async for work in client.beta.environments.work.poller(
                  environment_id=environment_id,
                  environment_key=environment_key,
                  block_ms=None,
                  reclaim_older_than_ms=2000,
                  drain=True,
                  auto_stop=False,
              ):
                  await client.beta.environments.work.worker(workdir="/workspace").handle_item(
                      work_id=work.id,
                      environment_id=environment_id,
                      session_id=work.data.id,
                      environment_key=environment_key,
                      # The per-session secret is what lets the worker mount the session's memory stores.
                      work_secret=work.secret,
                  )

typescript TypeScript
          import Anthropic from "@anthropic-ai/sdk";

          const environmentKey = process.env.ANTHROPIC_ENVIRONMENT_KEY!;
          const environmentId = process.env.ANTHROPIC_ENVIRONMENT_ID!;
          const client = new Anthropic({
            authToken: environmentKey
          });
          // Call shutdown.abort() from the host's SIGTERM/SIGINT handler, alongside closing the server,
          // then wait for in-flight handle() calls before exiting: the abort lets a running work item
          // upload changed memory files and remove its store directories first.
          export const shutdown = new AbortController();

          export async function handle(req: Request): Promise<Response> {
            // Never acknowledge a delivery whose work will not run here; a 503 makes the sender retry.
            if (shutdown.signal.aborted) {
              return Response.json({ status: "shutting down" }, { status: 503 });
            }
            const body = await req.text();
            let event;
            try {
              event = client.beta.webhooks.unwrap(body, { headers: Object.fromEntries(req.headers) });
            } catch {
              return new Response("signature verification failed", { status: 401 });
            }
            if (event.data.type !== "session.status_run_started") {
              return Response.json({ status: "ignored" });
            }

            for await (const work of client.beta.environments.work.poller({
              environmentId,
              environmentKey,
              blockMs: null,
              reclaimOlderThanMs: 2000,
              drain: true,
              autoStop: false,
              signal: shutdown.signal
            })) {
              await client.beta.environments.work.worker({ workdir: "/workspace" }).handleItem({
                workId: work.id,
                environmentId,
                sessionId: work.data.id,
                environmentKey,
                // The per-session secret is what lets the worker mount the session's memory stores.
                workSecret: work.secret ?? undefined,
                signal: shutdown.signal
              });
            }
            // The poller and handleItem return quietly on abort, so a drain cut short lands here.
            if (shutdown.signal.aborted) {
              return Response.json({ status: "shutting down" }, { status: 503 });
            }
            return Response.json({ status: "ok" });
          }

csharp C#
          // EnvironmentWorker is not currently available in the C# SDK.
          // To handle work items directly, see the Environments Work endpoints.

go Go
          package main

          import (
          	"context"
          	"encoding/json"
          	"errors"
          	"io"
          	"log/slog"
          	"net/http"
          	"os"
          	"os/signal"
          	"syscall"

          	"github.com/anthropics/anthropic-sdk-go"
          	"github.com/anthropics/anthropic-sdk-go/lib/environments"
          	"github.com/anthropics/anthropic-sdk-go/option"
          	"github.com/anthropics/anthropic-sdk-go/packages/param"
          )

          var (
          	environmentKey = os.Getenv("ANTHROPIC_ENVIRONMENT_KEY")
          	environmentID  = os.Getenv("ANTHROPIC_ENVIRONMENT_ID")
          	client         = anthropic.NewClient(
          		option.WithAuthToken(environmentKey),
          		option.WithWebhookKey(os.Getenv("ANTHROPIC_WEBHOOK_SIGNING_KEY")),
          	)
          	worker = environments.NewEnvironmentWorker(client, environments.EnvironmentWorkerOptions{
          		Workdir: "/workspace",
          	})
          	// Cancelled on SIGINT or SIGTERM (set in main) so an in-flight work item can
          	// upload changed memory files and remove its store directories before exit.
          	shutdown context.Context
          )

          func handle(w http.ResponseWriter, r *http.Request) {
          	body, err := io.ReadAll(r.Body)
          	if err != nil {
          		http.Error(w, "bad request", http.StatusBadRequest)
          		return
          	}
          	event, err := client.Beta.Webhooks.Unwrap(body, r.Header)
          	if err != nil {
          		http.Error(w, "signature verification failed", http.StatusUnauthorized)
          		return
          	}
          	if event.Data.Type != "session.status_run_started" {
          		json.NewEncoder(w).Encode(map[string]string{"status": "ignored"})
          		return
          	}

          	// The Go SDK does not provide a RunOne convenience: drain pending items
          	// with WorkPoller and run each one with HandleItem.
          	// Detach from r.Context(): the session can outlive the webhook delivery timeout.
          	// The process-wide shutdown context still ends the item cleanly on SIGTERM.
          	ctx := shutdown
          	poller := environments.NewWorkPoller(ctx, client, environments.WorkPollerOptions{
          		EnvironmentID:      environmentID,
          		EnvironmentKey:     environmentKey,
          		BlockMs:            param.Null[int64](),
          		ReclaimOlderThanMs: param.NewOpt[int64](2000),
          		Drain:              true,
          		AutoStop:           param.NewOpt(false),
          	})
          	defer poller.Close()
          	for poller.Next() {
          		item := poller.Current()
          		if err := worker.HandleItem(ctx, environments.HandleItemOptions{
          			WorkID:         item.ID,
          			EnvironmentID:  item.EnvironmentID,
          			SessionID:      item.Data.ID,
          			EnvironmentKey: environmentKey,
          			// The per-session secret is what lets the worker mount the session's memory stores.
          			WorkSecret: item.Secret,
          		}); err != nil {
          			slog.Error("handle work item", "work_id", item.ID, "err", err)
          			http.Error(w, "internal error", http.StatusInternalServerError)
          			return
          		}
          	}
          	if err := poller.Err(); err != nil {
          		slog.Error("poll work queue", "err", err)
          		http.Error(w, "internal error", http.StatusInternalServerError)
          		return
          	}
          	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
          }

          func main() {
          	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
          	defer stop()
          	shutdown = ctx

          	server := &http.Server{Addr: ":8080"}
          	http.HandleFunc("POST /webhook", handle)
          	go func() {
          		if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
          			slog.Error("http server", "err", err)
          			os.Exit(1)
          		}
          	}()
          	// On a signal, stop accepting deliveries and return only after in-flight
          	// handlers, and therefore their work items' memory teardown, have finished.
          	<-ctx.Done()
          	if err := server.Shutdown(context.Background()); err != nil {
          		slog.Error("http shutdown", "err", err)
          	}
          }

java Java
          // EnvironmentWorker is not currently available in the Java SDK.
          // To handle work items directly, see the Environments Work endpoints.

php PHP
          // EnvironmentWorker is not currently available in the PHP SDK.
          // To handle work items directly, see the Environments Work endpoints.

ruby Ruby
          # EnvironmentWorker is not currently available in the Ruby SDK.
          # To handle work items directly, see the Environments Work endpoints.

bash cURL
  # The work poller is an SDK helper (Python, TypeScript, Go), not a raw
  # endpoint. From the shell, use `ant beta:worker poll --on-work` instead;
  # see the Always-on (ant CLI) tab.

bash CLI
  # The work poller is an SDK helper (Python, TypeScript, Go), not a raw
  # endpoint. From the shell, use `ant beta:worker poll --on-work` instead;
  # see the Always-on (ant CLI) tab.

python Python
  import asyncio
  import os

  from anthropic import AsyncAnthropic
  from anthropic.types.beta.environments import BetaSelfHostedWork

  SANDBOX_ENV = (
      "ANTHROPIC_ENVIRONMENT_ID",
      "ANTHROPIC_ENVIRONMENT_KEY",
      "ANTHROPIC_WORK_ID",
      "ANTHROPIC_SESSION_ID",
      "ANTHROPIC_WORK_SECRET",
      "ANTHROPIC_BASE_URL",  # forwarded only when set on this host
  )


  async def launch_container(work: BetaSelfHostedWork) -> None:
      print(f"claimed session {work.data.id}")
      # Replace `docker run` with your own sandbox launcher. Forward the environment
      # key (never your API key) and the work item's per-session secret: the worker
      # inside needs the secret to mount the session's memory stores.
      env = os.environ | {
          "ANTHROPIC_WORK_ID": work.id,
          "ANTHROPIC_SESSION_ID": work.data.id,
          "ANTHROPIC_WORK_SECRET": work.secret or "",
      }
      forward = [arg for name in SANDBOX_ENV for arg in ("-e", name)]
      launcher = await asyncio.create_subprocess_exec(
          "docker", "run", "--rm", "--detach", *forward, "your-sdk-worker-image", env=env
      )
      await launcher.wait()


  async def main() -> None:
      environment_key = os.environ["ANTHROPIC_ENVIRONMENT_KEY"]
      environment_id = os.environ["ANTHROPIC_ENVIRONMENT_ID"]
      async with AsyncAnthropic(auth_token=environment_key) as client:
          async for work in client.beta.environments.work.poller(
              environment_id=environment_id,
              environment_key=environment_key,
              auto_stop=False,  # the launched sandbox owns the stop call
          ):
              await launch_container(work)


  asyncio.run(main())

typescript TypeScript
  import { spawn } from "node:child_process";
  import { once } from "node:events";
  import Anthropic from "@anthropic-ai/sdk";
  import { WorkPoller } from "@anthropic-ai/sdk/helpers/beta/environments";
  import type { BetaSelfHostedWork } from "@anthropic-ai/sdk/resources/beta/environments";

  const SANDBOX_ENV = [
    "ANTHROPIC_ENVIRONMENT_ID",
    "ANTHROPIC_ENVIRONMENT_KEY",
    "ANTHROPIC_WORK_ID",
    "ANTHROPIC_SESSION_ID",
    "ANTHROPIC_WORK_SECRET",
    "ANTHROPIC_BASE_URL" // forwarded only when set on this host
  ];

  const environmentKey = process.env.ANTHROPIC_ENVIRONMENT_KEY!;
  const environmentId = process.env.ANTHROPIC_ENVIRONMENT_ID!;
  const client = new Anthropic({ authToken: environmentKey });

  async function launchContainer(work: BetaSelfHostedWork): Promise<void> {
    console.log(`claimed session ${work.data.id}`);
    // Replace `docker run` with your own sandbox launcher. Forward the environment
    // key (never your API key) and the work item's per-session secret: the worker
    // inside needs the secret to mount the session's memory stores.
    const env = {
      ...process.env,
      ANTHROPIC_WORK_ID: work.id,
      ANTHROPIC_SESSION_ID: work.data.id,
      ANTHROPIC_WORK_SECRET: work.secret ?? ""
    };
    const forward = SANDBOX_ENV.flatMap((name) => ["-e", name]);
    const launcher = spawn(
      "docker",
      ["run", "--rm", "--detach", ...forward, "your-sdk-worker-image"],
      { env, stdio: "inherit" }
    );
    await once(launcher, "close");
  }

  const poller = new WorkPoller({
    client,
    environmentId,
    environmentKey,
    autoStop: false // the launched sandbox owns the stop call
  });

  for await (const work of poller) {
    await launchContainer(work);
  }

csharp C#
  // A work-polling helper is not currently available in the C# SDK.
  // To claim work directly, see the Environments Work endpoints.

go Go
  package main

  import (
  	"context"
  	"fmt"
  	"log"
  	"os"
  	"os/exec"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/lib/environments"
  	"github.com/anthropics/anthropic-sdk-go/option"
  	"github.com/anthropics/anthropic-sdk-go/packages/param"
  )

  var sandboxEnv = []string{
  	"ANTHROPIC_ENVIRONMENT_ID",
  	"ANTHROPIC_ENVIRONMENT_KEY",
  	"ANTHROPIC_WORK_ID",
  	"ANTHROPIC_SESSION_ID",
  	"ANTHROPIC_WORK_SECRET",
  	"ANTHROPIC_BASE_URL", // forwarded only when set on this host
  }

  func launchContainer(ctx context.Context, work *anthropic.BetaSelfHostedWork) error {
  	fmt.Printf("claimed session %s\n", work.Data.ID)
  	// Replace `docker run` with your own sandbox launcher. Forward the environment
  	// key (never your API key) and the work item's per-session secret: the worker
  	// inside needs the secret to mount the session's memory stores.
  	args := []string{"run", "--rm", "--detach"}
  	for _, name := range sandboxEnv {
  		args = append(args, "-e", name)
  	}
  	launcher := exec.CommandContext(ctx, "docker", append(args, "your-sdk-worker-image")...)
  	launcher.Env = append(os.Environ(),
  		"ANTHROPIC_WORK_ID="+work.ID,
  		"ANTHROPIC_SESSION_ID="+work.Data.ID,
  		"ANTHROPIC_WORK_SECRET="+work.Secret,
  	)
  	launcher.Stdout, launcher.Stderr = os.Stdout, os.Stderr
  	return launcher.Run()
  }

  func main() {
  	environmentID := os.Getenv("ANTHROPIC_ENVIRONMENT_ID")
  	environmentKey := os.Getenv("ANTHROPIC_ENVIRONMENT_KEY")

  	client := anthropic.NewClient(option.WithAuthToken(environmentKey))

  	ctx := context.Background()

  	poller := environments.NewWorkPoller(ctx, client, environments.WorkPollerOptions{
  		EnvironmentID:  environmentID,
  		EnvironmentKey: environmentKey,
  		AutoStop:       param.NewOpt(false), // the launched sandbox owns the stop call
  	})
  	defer poller.Close()

  	for work, err := range poller.All() {
  		if err != nil {
  			log.Fatal(err)
  		}
  		if err := launchContainer(ctx, work); err != nil {
  			log.Fatal(err)
  		}
  	}
  }

java Java
  // A work-polling helper is not currently available in the Java SDK.
  // To claim work directly, see the Environments Work endpoints.

php PHP
  // A work-polling helper is not currently available in the PHP SDK.
  // To claim work directly, see the Environments Work endpoints.

ruby Ruby
  # A work-polling helper is not currently available in the Ruby SDK.
  # To claim work directly, see the Environments Work endpoints.

python Python
  EnvironmentWorker(client, ..., tools=lambda env: [beta_bash_tool(env), my_custom_tool])

typescript TypeScript
  new EnvironmentWorker({
    client,
    environmentId,
    environmentKey,
    tools: (ctx) => [betaBashTool(ctx), myCustomTool]
  });

csharp C#
  // EnvironmentWorker is not currently available in the C# SDK.
  // To answer custom tool calls directly, see the session event stream.

go Go
  worker := environments.NewEnvironmentWorker(client, environments.EnvironmentWorkerOptions{
  	EnvironmentID:  environmentID,
  	EnvironmentKey: environmentKey,
  	ToolsFunc: func(env *agenttoolset.AgentToolContext) []anthropic.BetaTool {
  		return []anthropic.BetaTool{agenttoolset.BetaBashTool(env), myCustomTool}
  	},
  })

java Java
  // EnvironmentWorker is not currently available in the Java SDK.
  // To answer custom tool calls directly, see the session event stream.

php PHP
  // EnvironmentWorker is not currently available in the PHP SDK.
  // To answer custom tool calls directly, see the session event stream.

ruby Ruby
  # EnvironmentWorker is not currently available in the Ruby SDK.
  # To answer custom tool calls directly, see the session event stream.

python Python
  from anthropic.lib.tools.agent_toolset import (
      AgentToolContext,
      beta_agent_toolset_20260401,
  )

  async with AgentToolContext(
      workdir="/workspace", client=client, session_id=work.data.id
  ) as env:
      # skills downloaded to /workspace/skills/<name>/
      tools = beta_agent_toolset_20260401(env)

typescript TypeScript
  import {
    setupSkills,
    betaAgentToolset20260401
  } from "@anthropic-ai/sdk/tools/agent-toolset/node";

  const ctx = { workdir: "/workspace", client, sessionId: work.data.id };
  await setupSkills(ctx);
  const tools = betaAgentToolset20260401(ctx);

csharp C#
  // AgentToolContext is not currently available in the C# SDK.

go Go
  env := &agenttoolset.AgentToolContext{Workdir: "/workspace"}
  if err := env.SetupSkills(ctx, client, work.Data.ID); err != nil {
  	panic(err)
  }
  // skills downloaded to /workspace/skills/<name>/
  tools := agenttoolset.BetaAgentToolset20260401(env)

java Java
  // AgentToolContext is not currently available in the Java SDK.

php PHP
  // AgentToolContext is not currently available in the PHP SDK.

ruby Ruby
  # AgentToolContext is not currently available in the Ruby SDK.

bash
ant beta:environments:work stats --environment-id "$ANTHROPIC_ENVIRONMENT_ID"
```

If `workers_polling` stays at 0, the worker isn't reaching the queue: confirm `ANTHROPIC_ENVIRONMENT_KEY` and `ANTHROPIC_ENVIRONMENT_ID` are set on the worker host. See [Read queue depth](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#read-queue-depth) for the full stats response and other language examples.


## Start a session

Source: https://platform.claude.com/llms-full.txt#start-a-session

Once your worker is running, create a session that targets the environment. Set `AGENT_ID` to the agent ID you noted in [Before you begin](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#before-you-begin). The session enters the environment's work queue and waits there until a worker claims it; if no worker is connected, the session stays queued rather than failing.

Anthropic doesn't mount files or GitHub repositories into self-hosted sandboxes. To make session-specific files available, pass file references (such as an S3 path or commit SHA) in the session `metadata` field. The claimed work item doesn't carry the session's metadata, but it does carry the session ID: your spawn script or `--on-work` handler retrieves the session (`GET /v1/sessions/{session_id}`) to read the `metadata` field, then stages the files into the working directory before tool execution begins.

<CodeGroup>
  ```bash cURL
  curl -sS --fail-with-body https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "agent": "$AGENT_ID",
    "environment_id": "$ANTHROPIC_ENVIRONMENT_ID",
    "metadata": {"input_file": "s3://my-bucket/data.csv"}
  }
  EOF

bash CLI
  ant beta:sessions create \
    --agent "$AGENT_ID" \
    --environment-id "$ANTHROPIC_ENVIRONMENT_ID" \
    --metadata '{"input_file": "s3://my-bucket/data.csv"}'

python Python
  session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
      metadata={"input_file": "s3://my-bucket/data.csv"},
  )

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id,
    metadata: { input_file: "s3://my-bucket/data.csv" }
  });

csharp C#
  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = agent.ID,
      EnvironmentID = environment.ID,
      Metadata = new Dictionary<string, string> { ["input_file"] = "s3://my-bucket/data.csv" },
  });

go Go
  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent:         anthropic.BetaSessionNewParamsAgentUnion{OfString: anthropic.String(agent.ID)},
  	EnvironmentID: environment.ID,
  	Metadata: map[string]string{
  		"input_file": "s3://my-bucket/data.csv",
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  var session = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(agent.id())
      .environmentId(environment.id())
      .metadata(SessionCreateParams.Metadata.builder()
          .putAdditionalProperty("input_file", JsonValue.from("s3://my-bucket/data.csv"))
          .build())
      .build());

php PHP
  $session = $client->beta->sessions->create(
      agent: $agent->id,
      environmentID: $environment->id,
      metadata: ['input_file' => 's3://my-bucket/data.csv'],
  );

ruby Ruby
  session = client.beta.sessions.create(
    agent: agent.id,
    environment_id: environment.id,
    metadata: {input_file: "s3://my-bucket/data.csv"}
  )

text wrap
  Environment env_... is a self-hosted environment. `resources` are not supported with self-hosted environments.
  ```

  [Deployments](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments) that target a self-hosted environment follow the same rule.
</Note>

See [Self-hosted worker](https://platform.claude.com/docs/en/managed-agents/reference#self-hosted-worker) in the reference for the full list of CLI flags, and [SDK helpers](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#sdk-helpers) for the SDK helper options.


## Use memory stores

Source: https://platform.claude.com/llms-full.txt#use-memory-stores

Sessions on a self-hosted environment attach [memory stores](https://platform.claude.com/docs/en/managed-agents/memory) exactly as sessions on cloud environments do: list them in `resources` when you create the session, as shown in [Attach a memory store to a session](https://platform.claude.com/docs/en/managed-agents/memory#attach-a-memory-store-to-a-session). A session accepts up to 8 memory stores. On a self-hosted environment the SDK worker, rather than Anthropic's infrastructure, materializes each store for the agent, so memory stores there require `EnvironmentWorker` (or its `handle_item()` method) from the Python, TypeScript, or Go SDK.

The `ant` CLI worker (`ant beta:worker poll` and `ant beta:worker run`) does not mount memory stores. To combine the CLI poller with memory stores, run the SDK worker inside a per-session sandbox as described in [Run one sandbox per session](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#run-one-sandbox-per-session).

Memory stores cannot be attached to sessions on self-hosted environments on [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws).

### How the worker handles memory

When the worker claims a work item whose session has memory stores attached, it:

1. Downloads each attached store to its `mount_path` on the worker host, authenticating with the work item's per-session `secret`. The `mount_path` is the same directory under `/mnt/memory/` that cloud sessions use (for example, `/mnt/memory/user-preferences/` for a store named "User Preferences"), and the session's system prompt describes it to the agent.
2. Adds those directories to the file tools' allowed roots, and the directories of stores attached with `access: "read_only"` to their read-only roots, so the agent works on memories with the same `read`, `write`, `edit`, `glob`, and `grep` tools it uses in the working directory.
3. Reconciles local and remote changes after tool calls, at most once per sync interval (15 seconds by default): memories that changed in the store are written to disk, and files the agent changed are uploaded to the store.
4. Runs a final sync when the session ends, flushes any uploads still pending for up to 30 seconds, and then removes the directories it created. A worker that is cancelled while a session runs skips the final sync but still uploads changed files and removes the directories before it exits.

The memory store on Anthropic's side remains the source of truth. [Memory versions](https://platform.claude.com/docs/en/managed-agents/memory#audit-memory-changes), redaction, and viewing or editing memories in the Console work as they do for cloud sessions, and the agent's memory reads and writes appear in the [event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming) as ordinary tool events. Because each worker syncs on an interval, a change written in one session becomes visible to another running session only after both have synced, typically well under a minute at the default interval; sessions on cloud sandboxes see each other's changes almost immediately.

Each store directory contains a marker file named `.anthropic-memory-store` that ties the directory to its store. Leave it in place: the worker does not sync a directory whose marker is missing or altered.

### Prepare the host

Memory stores on self-hosted sandboxes need a POSIX filesystem on the worker host (the Linux host from [Before you begin](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#before-you-begin)); Windows hosts are not supported, because the worker requires `O_NOFOLLOW` when it opens memory files. A case-sensitive filesystem is recommended, so that memory paths that differ only in case do not collide.

Before you start the worker, create the parent directory and make it writable by the user the worker runs as:

Do not create the per-store directories yourself. The worker creates each store's `mount_path` directory (for example, `/mnt/memory/user-preferences`) when a session starts, refuses to start the session's work if something already exists at that path, and removes the directory when the session ends. Two operating rules follow:

* **Run one session per filesystem when sessions attach the same store.** Two sessions cannot mount the same store on one host at the same time, because both need the same path. Giving each session its own sandbox, as described in [Run one sandbox per session](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#run-one-sandbox-per-session), satisfies this rule.
* **Stop workers gracefully.** When you stop a worker while a session runs, `EnvironmentWorker` uploads the session's changed memory files and removes its store directories only if it is cancelled rather than killed: a killed process runs no teardown, and the worker does not install signal handlers itself. Wire SIGTERM and SIGINT to cancellation in the process that runs it: abort the `signal` you pass to the worker in TypeScript, cancel the context in Go, and in Python cancel the task that runs `run()` or `handle_item()`. Do that from a signal handler when your worker is the process, as the standalone workers on this page do, or from your server's own shutdown hook when the worker runs inside a webhook handler, which must not take over the server's signals. Then stop workers with SIGTERM and give them at least 30 seconds to exit before any hard kill, because the final upload can take that long. If a worker is killed before its teardown runs, remove the leftover store directory under `/mnt/memory/` before the next session that attaches that store; any edits in it that had not synced are lost.

### Run one sandbox per session

The sandbox-per-session pattern in [Run a worker](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#run-a-worker) gives each session a fresh filesystem, which is what [Prepare the host](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#prepare-the-host) calls for when sessions attach the same store. Keep `ant beta:worker poll --on-work` (or the SDK's work poller) as the poller on the host.

The `ant beta:worker run` entrypoint shown there does not mount memory stores, so build the per-session image around the SDK worker instead: its entrypoint constructs `EnvironmentWorker` and calls `handle_item()` (`handleItem` in TypeScript, `HandleItem` in Go), which reads the session, work, and environment identifiers from the `ANTHROPIC_*` variables and the work item's per-session `secret` from `ANTHROPIC_WORK_SECRET`. You can also pass the secret explicitly as `work_secret` (`workSecret` in TypeScript, `WorkSecret` in Go).

<CodeGroup exclude="shell">
  ```python Python
  import asyncio
  import contextlib
  import os
  import signal
  from anthropic import AsyncAnthropic
  from anthropic.lib.environments import EnvironmentWorker


  async def main() -> None:
      async with AsyncAnthropic(auth_token=os.environ["ANTHROPIC_ENVIRONMENT_KEY"]) as client:
          worker = EnvironmentWorker(client, workdir="/workspace")
          # With no arguments, handle_item() reads the ANTHROPIC_* variables the spawn
          # script forwarded, including ANTHROPIC_WORK_SECRET.
          task = asyncio.create_task(worker.handle_item())
          # Cancelling the task when the container is stopped lets the worker upload
          # changed memory files and remove the store directories before it exits.
          loop = asyncio.get_running_loop()
          for signum in (signal.SIGINT, signal.SIGTERM):
              loop.add_signal_handler(signum, task.cancel)
          with contextlib.suppress(asyncio.CancelledError):
              await task


  asyncio.run(main())

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";
  import { EnvironmentWorker } from "@anthropic-ai/sdk/helpers/beta/environments";

  const client = new Anthropic({ authToken: process.env.ANTHROPIC_ENVIRONMENT_KEY });
  const controller = new AbortController();
  // Aborting when the container is stopped lets the worker upload changed memory
  // files and remove the store directories before it exits.
  process.once("SIGTERM", () => controller.abort());
  process.once("SIGINT", () => controller.abort());

  // With no arguments, handleItem() reads the ANTHROPIC_* variables the spawn
  // script forwarded, including ANTHROPIC_WORK_SECRET.
  await new EnvironmentWorker({
    client,
    workdir: "/workspace",
    signal: controller.signal
  }).handleItem();

csharp C#
  // EnvironmentWorker is not currently available in the C# SDK.

go Go
  package main

  import (
  	"context"
  	"log"
  	"os"
  	"os/signal"
  	"syscall"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/lib/environments"
  	"github.com/anthropics/anthropic-sdk-go/option"
  )

  func main() {
  	// Cancelling the context when the container is stopped lets the worker upload
  	// changed memory files and remove the store directories before it exits.
  	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
  	defer stop()

  	client := anthropic.NewClient(option.WithAuthToken(os.Getenv("ANTHROPIC_ENVIRONMENT_KEY")))
  	worker := environments.NewEnvironmentWorker(client, environments.EnvironmentWorkerOptions{
  		Workdir: "/workspace",
  	})
  	// With zero-value options, HandleItem reads the ANTHROPIC_* variables the spawn
  	// script forwarded, including ANTHROPIC_WORK_SECRET.
  	if err := worker.HandleItem(ctx, environments.HandleItemOptions{}); err != nil {
  		log.Fatalf("worker: %v", err)
  	}
  }

java Java
  // EnvironmentWorker is not currently available in the Java SDK.

php PHP
  // EnvironmentWorker is not currently available in the PHP SDK.

ruby Ruby
  # EnvironmentWorker is not currently available in the Ruby SDK.

bash
#!/bin/bash
# spawn.sh: called once per claimed work item
# The claimed work item arrives as JSON on stdin. Its secret is the
# per-session credential that the memory store endpoints require.
ANTHROPIC_WORK_SECRET="$(jq -r '.secret // empty')"
export ANTHROPIC_WORK_SECRET
mkdir -p "/host/outputs/$ANTHROPIC_SESSION_ID"
exec docker run --rm \
  -e ANTHROPIC_SESSION_ID -e ANTHROPIC_ENVIRONMENT_KEY \
  -e ANTHROPIC_WORK_ID -e ANTHROPIC_ENVIRONMENT_ID -e ANTHROPIC_BASE_URL \
  -e ANTHROPIC_WORK_SECRET \
  -v "/host/outputs/$ANTHROPIC_SESSION_ID":/workspace \
  your-sdk-worker-image

python Python
  worker = EnvironmentWorker(
      client,
      environment_id=environment_id,
      environment_key=environment_key,
      workdir="/workspace",
      memory_sync_interval=10,  # seconds
      memory_sync_deletions="log_only",
  )

typescript TypeScript
  const worker = new EnvironmentWorker({
    client,
    environmentId,
    environmentKey,
    workdir: "/workspace",
    memorySyncIntervalMs: 10_000,
    memorySyncDeletions: "log_only"
  });

csharp C#
  // EnvironmentWorker is not currently available in the C# SDK.

go Go
  worker := environments.NewEnvironmentWorker(client, environments.EnvironmentWorkerOptions{
  	EnvironmentID:       environmentID,
  	EnvironmentKey:      environmentKey,
  	Workdir:             "/workspace",
  	MemorySyncInterval:  10 * time.Second,
  	MemorySyncDeletions: environments.MemorySyncDeletionsLogOnly,
  })

java Java
  // EnvironmentWorker is not currently available in the Java SDK.

php PHP
  // EnvironmentWorker is not currently available in the PHP SDK.

ruby Ruby
  # EnvironmentWorker is not currently available in the Ruby SDK.
  ```
</CodeGroup>

### Read-only stores and conflicts

For a store attached with `access: "read_only"`, the `write` and `edit` tools refuse to change files inside its directory, and the worker never uploads anything from it. Changes made through `bash`, or through a custom tool or MCP server you serve from the sandbox, are not blocked locally: they are never synced to the store, and the next remote change to that memory overwrites them. If you need the local copy itself to stay unchanged during the session, disable the `bash` tool for that agent and give it no custom tool that writes to the sandbox's filesystem; do not mount the store path read-only, because the worker itself must create the directory and write the downloaded memories into it.

Conflicts resolve in favor of the store. When the agent changes a memory file that also changed in the store since the session last synced it, the worker keeps the store's version at the next sync, overwrites the local file with it, and logs a warning; the `write` and `edit` tools themselves succeed and no error reaches the agent. If the agent's change still applies, it can re-read the file after the sync and make the change again.

### Troubleshoot memory mounts

The worker logs mount and background sync failures rather than reporting them to the session; only read-only refusals reach the agent, as tool errors (see [Read-only stores and conflicts](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#read-only-stores-and-conflicts)). If a memory store cannot be mounted when the worker claims a session, the worker fails the work item: the session emits no error event and stays idle.

| Symptom                                                                                                                                 | Cause                                                                                                                                                                                                          | Fix                                                                                                                                                                                                                                                                                                                              |
| --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The worker log contains `the work item carried no sessions token` (in Go, the `ErrSessionMemoryNoToken` error) and the work item fails. | The work item's per-session `secret` did not reach the worker: memory stores on self-hosted sandboxes are not enabled for your organization, or your spawn script did not forward the secret into the sandbox. | In the sandbox-per-session pattern, forward `ANTHROPIC_WORK_SECRET` into the sandbox as shown in [Run one sandbox per session](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#run-one-sandbox-per-session). If the worker polls and runs sessions in one process and still logs this, contact support. |
| The worker log contains `something already exists at the memory store's path`.                                                          | A directory left over from a previous session, usually one whose worker was killed before its teardown ran.                                                                                                    | Remove the leftover directory that the log line names. Edits in it that had not synced are lost.                                                                                                                                                                                                                                 |
| The worker log contains `cannot create the memory store's folder` and `the worker host must make this mount path writable`.             | The user the worker runs as cannot create directories under `/mnt/memory`.                                                                                                                                     | Create `/mnt/memory` and `chown` it to that user; see [Prepare the host](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#prepare-the-host).                                                                                                                                                             |
| The session sits `idle` with a `requires_action` stop reason and no error event shortly after a worker claimed it.                      | The worker failed the work item because it could not mount a memory store, for one of the preceding reasons.                                                                                                   | Fix the cause on the host, then send a [`user.interrupt`](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#integrating-events) event: the session's work is queued again and the next worker that claims it retries the mount.                                                                            |


## Serve custom tools from your sandbox

Source: https://platform.claude.com/llms-full.txt#serve-custom-tools-from-your-sandbox

[Custom tools](https://platform.claude.com/docs/en/managed-agents/tools#custom-tools) are tools your own code executes: the agent emits an `agent.custom_tool_use` event and waits for a matching `user.custom_tool_result`. The worker can be that code, and because it runs inside your sandbox, the tool reaches the internal services, credentials, and network egress you configured for the sandbox, and nothing more. The environment key authorizes posting custom tool results, so your Claude API key stays off the worker host.

<Note>
  Serving custom tools requires the SDK worker: the `ant` CLI worker has no way to register a custom tool implementation. In the sandbox-per-session pattern, run `EnvironmentWorker` inside the sandbox with `handle_item()` (`handleItem` in TypeScript, `HandleItem` in Go) in place of `ant beta:worker run`.
</Note>

<Steps>
  <Step title="Declare the tool on the agent">
    Add a `custom` entry to the agent's `tools` whose `name` matches the tool your worker registers. See [Custom tools](https://platform.claude.com/docs/en/managed-agents/tools#custom-tools) for the full declaration shape.

</Step>

  <Step title="Register the implementation with the worker">
    Pass the tool through the worker's `tools` factory (see [SDK helpers](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#sdk-helpers)), alongside the built-in toolset:

    <CodeGroup exclude="shell">
      ```python Python
      import asyncio
      import os
      from anthropic import AsyncAnthropic, beta_async_tool
      from anthropic.lib.environments import EnvironmentWorker
      from anthropic.lib.tools.agent_toolset import beta_agent_toolset_20260401


      @beta_async_tool
      async def get_order_status(order_id: str) -> str:
          """Look up an order in the internal fulfillment system by order ID."""
          # Runs on the worker host: call anything the sandbox can reach.
          return f"Order {order_id}: shipped"


      async def main() -> None:
          environment_key = os.environ["ANTHROPIC_ENVIRONMENT_KEY"]
          environment_id = os.environ["ANTHROPIC_ENVIRONMENT_ID"]
          async with AsyncAnthropic(auth_token=environment_key) as client:
              await EnvironmentWorker(
                  client,
                  environment_id=environment_id,
                  environment_key=environment_key,
                  workdir="/workspace",
                  tools=lambda env: [*beta_agent_toolset_20260401(env), get_order_status],
              ).run()


      asyncio.run(main())

typescript TypeScript
      import Anthropic from "@anthropic-ai/sdk";
      import { EnvironmentWorker } from "@anthropic-ai/sdk/helpers/beta/environments";
      import { betaTool } from "@anthropic-ai/sdk/helpers/beta/json-schema";
      import { betaAgentToolset20260401 } from "@anthropic-ai/sdk/tools/agent-toolset/node";

      const getOrderStatus = betaTool({
        name: "get_order_status",
        description: "Look up an order in the internal fulfillment system by order ID.",
        inputSchema: {
          type: "object",
          properties: { order_id: { type: "string", description: "The order ID" } },
          required: ["order_id"]
        },
        // Runs on the worker host: call anything the sandbox can reach.
        run: async ({ order_id }) => `Order ${order_id}: shipped`
      });

      const environmentKey = process.env.ANTHROPIC_ENVIRONMENT_KEY!;
      const environmentId = process.env.ANTHROPIC_ENVIRONMENT_ID!;
      const client = new Anthropic({ authToken: environmentKey });
      const controller = new AbortController();
      process.once("SIGTERM", () => controller.abort());

      await new EnvironmentWorker({
        client,
        environmentId,
        environmentKey,
        workdir: "/workspace",
        signal: controller.signal,
        tools: (ctx) => [...betaAgentToolset20260401(ctx), getOrderStatus]
      }).run();

csharp C#
      // EnvironmentWorker is not currently available in the C# SDK.
      // To answer custom tool calls directly, see the session event stream.

go Go
      package main

      import (
      	"context"
      	"log"
      	"os"
      	"os/signal"
      	"syscall"

      	"github.com/anthropics/anthropic-sdk-go"
      	"github.com/anthropics/anthropic-sdk-go/lib/environments"
      	"github.com/anthropics/anthropic-sdk-go/option"
      	"github.com/anthropics/anthropic-sdk-go/toolrunner"
      	"github.com/anthropics/anthropic-sdk-go/tools/agenttoolset"
      )

      type orderStatusInput struct {
      	OrderID string `json:"order_id"`
      }

      func main() {
      	environmentKey := os.Getenv("ANTHROPIC_ENVIRONMENT_KEY")
      	environmentID := os.Getenv("ANTHROPIC_ENVIRONMENT_ID")

      	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
      	defer stop()

      	getOrderStatus := toolrunner.NewBetaTool(
      		"get_order_status",
      		"Look up an order in the internal fulfillment system by order ID.",
      		anthropic.BetaToolInputSchemaParam{
      			Properties: map[string]any{
      				"order_id": map[string]any{"type": "string", "description": "The order ID"},
      			},
      			Required: []string{"order_id"},
      		},
      		// Runs on the worker host: call anything the sandbox can reach.
      		func(ctx context.Context, input orderStatusInput) (anthropic.BetaToolResultBlockParamContentUnion, error) {
      			return anthropic.BetaToolResultBlockParamContentUnion{
      				OfText: &anthropic.BetaTextBlockParam{Text: "Order " + input.OrderID + ": shipped"},
      			}, nil
      		},
      	)

      	client := anthropic.NewClient(option.WithAuthToken(environmentKey))

      	worker := environments.NewEnvironmentWorker(client, environments.EnvironmentWorkerOptions{
      		EnvironmentID:  environmentID,
      		EnvironmentKey: environmentKey,
      		Workdir:        "/workspace",
      		ToolsFunc: func(env *agenttoolset.AgentToolContext) []anthropic.BetaTool {
      			return append(agenttoolset.BetaAgentToolset20260401(env), getOrderStatus)
      		},
      	})
      	if err := worker.Run(ctx); err != nil {
      		log.Fatalf("worker: %v", err)
      	}
      }

java Java
      // EnvironmentWorker is not currently available in the Java SDK.
      // To answer custom tool calls directly, see the session event stream.

php PHP
      // EnvironmentWorker is not currently available in the PHP SDK.
      // To answer custom tool calls directly, see the session event stream.

ruby Ruby
      # EnvironmentWorker is not currently available in the Ruby SDK.
      # To answer custom tool calls directly, see the session event stream.

python Python
      import asyncio
      from typing import Any, cast
      from anthropic import AsyncAnthropic
      from anthropic.types.beta import BetaManagedAgentsCustomToolParams
      from mcp import ClientSession, types
      # Requires mcp >= 1.24, which renamed streamablehttp_client to streamable_http_client.
      from mcp.client.streamable_http import streamable_http_client

      MCP_SERVER_URL = "http://mcp.internal.example.com:8000/mcp"


      def to_custom_tool(tool: types.Tool) -> BetaManagedAgentsCustomToolParams:
          # The MCP fields map one to one onto a custom tool declaration. The cast
          # hands the schema dictionary to the SDK's typed parameter unchanged.
          return {
              "type": "custom",
              "name": tool.name,
              "description": tool.description or tool.name,
              "input_schema": cast(Any, tool.inputSchema),
          }


      async def main() -> None:
          # Run this wherever you create agents, not on the worker host: it
          # authenticates with your Claude API key (ANTHROPIC_API_KEY).
          async with (
              streamable_http_client(MCP_SERVER_URL) as (read, write, _),
              ClientSession(read, write) as mcp_session,
              AsyncAnthropic() as client,
          ):
              await mcp_session.initialize()
              listed = await mcp_session.list_tools()
              agent = await client.beta.agents.create(
                  name="Internal tools agent",
                  model="claude-opus-5",
                  tools=[
                      {"type": "agent_toolset_20260401"},
                      *[to_custom_tool(tool) for tool in listed.tools],
                  ],
              )
              print(agent.id)


      asyncio.run(main())

typescript TypeScript
      import Anthropic from "@anthropic-ai/sdk";
      import { Client } from "@modelcontextprotocol/sdk/client/index.js";
      import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

      const MCP_SERVER_URL = "http://mcp.internal.example.com:8000/mcp";

      // Run this wherever you create agents, not on the worker host: it
      // authenticates with your Claude API key (ANTHROPIC_API_KEY).
      const client = new Anthropic();

      const mcpClient = new Client({ name: "declare-agent-tools", version: "1.0.0" });
      await mcpClient.connect(new StreamableHTTPClientTransport(new URL(MCP_SERVER_URL)));
      const { tools } = await mcpClient.listTools();

      const agent = await client.beta.agents.create({
        name: "Internal tools agent",
        model: "claude-opus-5",
        tools: [
          { type: "agent_toolset_20260401" },
          // The MCP fields map one to one onto a custom tool declaration.
          ...tools.map((tool) => ({
            type: "custom" as const,
            name: tool.name,
            description: tool.description || tool.name,
            input_schema: tool.inputSchema
          }))
        ]
      });
      console.log(agent.id);

      await mcpClient.close();

csharp C#
      // See the Python, TypeScript, and Go tabs. Declaring custom tools from
      // C# works the same way once you list the server's tools with an MCP client.

go Go
      package main

      import (
      	"context"
      	"encoding/json"
      	"fmt"
      	"log"

      	"github.com/anthropics/anthropic-sdk-go"
      	mcpsdk "github.com/modelcontextprotocol/go-sdk/mcp"
      )

      const mcpServerURL = "http://mcp.internal.example.com:8000/mcp"

      // toCustomTool maps one MCP tool definition onto a custom tool declaration.
      // The fields map one to one: the typed parameter carries `properties` and
      // `required`, and every other JSON Schema keyword the server emits travels in
      // ExtraFields so the declared schema matches the server's schema.
      func toCustomTool(tool *mcpsdk.Tool) (anthropic.BetaAgentNewParamsToolUnion, error) {
      	raw, err := json.Marshal(tool.InputSchema)
      	if err != nil {
      		return anthropic.BetaAgentNewParamsToolUnion{}, err
      	}
      	var schema map[string]any
      	if err := json.Unmarshal(raw, &schema); err != nil {
      		return anthropic.BetaAgentNewParamsToolUnion{}, err
      	}

      	inputSchema := anthropic.BetaManagedAgentsCustomToolInputSchemaParam{ExtraFields: map[string]any{}}
      	for keyword, value := range schema {
      		switch keyword {
      		case "type":
      			// The parameter type always marshals "type": "object".
      		case "properties":
      			properties, _ := value.(map[string]any)
      			inputSchema.Properties = properties
      		case "required":
      			entries, _ := value.([]any)
      			for _, entry := range entries {
      				if name, isString := entry.(string); isString {
      					inputSchema.Required = append(inputSchema.Required, name)
      				}
      			}
      		default:
      			inputSchema.ExtraFields[keyword] = value
      		}
      	}

      	description := tool.Description
      	if description == "" {
      		description = tool.Name
      	}
      	return anthropic.BetaAgentNewParamsToolUnion{
      		OfCustom: &anthropic.BetaManagedAgentsCustomToolParams{
      			Type:        anthropic.BetaManagedAgentsCustomToolParamsTypeCustom,
      			Name:        tool.Name,
      			Description: description,
      			InputSchema: inputSchema,
      		},
      	}, nil
      }

      func main() {
      	ctx := context.Background()

      	// Run this wherever you create agents, not on the worker host: it
      	// authenticates with your Claude API key (ANTHROPIC_API_KEY).
      	client := anthropic.NewClient()

      	mcpClient := mcpsdk.NewClient(&mcpsdk.Implementation{Name: "declare-agent-tools", Version: "1.0.0"}, nil)
      	session, err := mcpClient.Connect(ctx, &mcpsdk.StreamableClientTransport{Endpoint: mcpServerURL}, nil)
      	if err != nil {
      		log.Fatalf("connect to MCP server: %v", err)
      	}
      	defer session.Close()

      	listed, err := session.ListTools(ctx, nil)
      	if err != nil {
      		log.Fatalf("list MCP tools: %v", err)
      	}

      	tools := []anthropic.BetaAgentNewParamsToolUnion{
      		{OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
      			Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
      		}},
      	}
      	for _, tool := range listed.Tools {
      		custom, err := toCustomTool(tool)
      		if err != nil {
      			log.Fatalf("convert MCP tool %s: %v", tool.Name, err)
      		}
      		tools = append(tools, custom)
      	}

      	agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
      		Name:  "Internal tools agent",
      		Model: anthropic.BetaManagedAgentsModelConfigParams{ID: anthropic.BetaManagedAgentsModelClaudeOpus5},
      		Tools: tools,
      	})
      	if err != nil {
      		log.Fatalf("create agent: %v", err)
      	}
      	fmt.Println(agent.ID)
      }

java Java
      // See the Python, TypeScript, and Go tabs. Declaring custom tools from
      // Java works the same way once you list the server's tools with an MCP client.

php PHP
      // See the Python, TypeScript, and Go tabs. Declaring custom tools from
      // PHP works the same way once you list the server's tools with an MCP client.

ruby Ruby
      # See the Python, TypeScript, and Go tabs. Declaring custom tools from
      # Ruby works the same way once you list the server's tools with an MCP client.

python Python
      import asyncio
      import os
      from datetime import timedelta
      from anthropic import AsyncAnthropic
      from anthropic.lib.environments import EnvironmentWorker
      from anthropic.lib.tools.agent_toolset import beta_agent_toolset_20260401
      from anthropic.lib.tools.mcp import async_mcp_tool
      from mcp import ClientSession
      # Requires mcp >= 1.24, which renamed streamablehttp_client to streamable_http_client.
      from mcp.client.streamable_http import streamable_http_client

      MCP_SERVER_URL = "http://mcp.internal.example.com:8000/mcp"


      async def main() -> None:
          environment_key = os.environ["ANTHROPIC_ENVIRONMENT_KEY"]
          environment_id = os.environ["ANTHROPIC_ENVIRONMENT_ID"]
          # Connect to the MCP server once at startup and keep the session open for
          # the life of the worker. The timeout turns a hung tool call into an error
          # result instead of a stalled call.
          async with (
              streamable_http_client(MCP_SERVER_URL) as (read, write, _),
              ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as mcp_session,
              AsyncAnthropic(auth_token=environment_key) as client,
          ):
              await mcp_session.initialize()
              listed = await mcp_session.list_tools()
              mcp_tools = [async_mcp_tool(tool, mcp_session) for tool in listed.tools]
              await EnvironmentWorker(
                  client,
                  environment_id=environment_id,
                  environment_key=environment_key,
                  workdir="/workspace",
                  tools=lambda env: [*beta_agent_toolset_20260401(env), *mcp_tools],
              ).run()


      asyncio.run(main())

typescript TypeScript
      import Anthropic from "@anthropic-ai/sdk";
      import { EnvironmentWorker } from "@anthropic-ai/sdk/helpers/beta/environments";
      import {
        mcpTools,
        type MCPCallToolResultLike,
        type MCPClientLike
      } from "@anthropic-ai/sdk/helpers/beta/mcp";
      import { betaAgentToolset20260401 } from "@anthropic-ai/sdk/tools/agent-toolset/node";
      import { Client } from "@modelcontextprotocol/sdk/client/index.js";
      import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

      const MCP_SERVER_URL = "http://mcp.internal.example.com:8000/mcp";

      const environmentKey = process.env.ANTHROPIC_ENVIRONMENT_KEY!;
      const environmentId = process.env.ANTHROPIC_ENVIRONMENT_ID!;
      const client = new Anthropic({ authToken: environmentKey });
      const controller = new AbortController();
      process.once("SIGTERM", () => controller.abort());

      // Connect to the MCP server once at startup and keep the connection open for
      // the life of the worker.
      const mcpClient = new Client({ name: "sandbox-worker", version: "1.0.0" });
      await mcpClient.connect(new StreamableHTTPClientTransport(new URL(MCP_SERVER_URL)));
      const { tools } = await mcpClient.listTools();

      // The MCP SDK's callTool return type still includes a legacy result shape that
      // mcpTools does not accept; narrow it. Drop this once MCPClientLike widens.
      const mcpClientForTools: MCPClientLike = {
        callTool: (params) => mcpClient.callTool(params) as Promise<MCPCallToolResultLike>
      };

      await new EnvironmentWorker({
        client,
        environmentId,
        environmentKey,
        workdir: "/workspace",
        signal: controller.signal,
        tools: (ctx) => [...betaAgentToolset20260401(ctx), ...mcpTools(tools, mcpClientForTools)]
      }).run();

csharp C#
      // EnvironmentWorker is not currently available in the C# SDK.

go Go
      package main

      import (
      	"context"
      	"log"
      	"os"
      	"os/signal"
      	"syscall"

      	"github.com/anthropics/anthropic-sdk-go"
      	"github.com/anthropics/anthropic-sdk-go/lib/environments"
      	"github.com/anthropics/anthropic-sdk-go/mcp"
      	"github.com/anthropics/anthropic-sdk-go/option"
      	"github.com/anthropics/anthropic-sdk-go/tools/agenttoolset"
      	mcpsdk "github.com/modelcontextprotocol/go-sdk/mcp"
      )

      const mcpServerURL = "http://mcp.internal.example.com:8000/mcp"

      func main() {
      	environmentKey := os.Getenv("ANTHROPIC_ENVIRONMENT_KEY")
      	environmentID := os.Getenv("ANTHROPIC_ENVIRONMENT_ID")

      	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
      	defer stop()

      	client := anthropic.NewClient(option.WithAuthToken(environmentKey))

      	// Connect to the MCP server once at startup and keep the session open for
      	// the life of the worker.
      	mcpClient := mcpsdk.NewClient(&mcpsdk.Implementation{Name: "sandbox-worker", Version: "1.0.0"}, nil)
      	session, err := mcpClient.Connect(ctx, &mcpsdk.StreamableClientTransport{Endpoint: mcpServerURL}, nil)
      	if err != nil {
      		log.Fatalf("connect to MCP server: %v", err)
      	}
      	defer session.Close()

      	listed, err := session.ListTools(ctx, nil)
      	if err != nil {
      		log.Fatalf("list MCP tools: %v", err)
      	}
      	mcpTools, err := mcp.NewBetaTools(listed.Tools, session)
      	if err != nil {
      		log.Fatalf("convert MCP tools: %v", err)
      	}

      	worker := environments.NewEnvironmentWorker(client, environments.EnvironmentWorkerOptions{
      		EnvironmentID:  environmentID,
      		EnvironmentKey: environmentKey,
      		Workdir:        "/workspace",
      		ToolsFunc: func(env *agenttoolset.AgentToolContext) []anthropic.BetaTool {
      			return append(agenttoolset.BetaAgentToolset20260401(env), mcpTools...)
      		},
      	})
      	if err := worker.Run(ctx); err != nil {
      		log.Fatalf("worker: %v", err)
      	}
      }

java Java
      // EnvironmentWorker is not currently available in the Java SDK.

php PHP
      // EnvironmentWorker is not currently available in the PHP SDK.

ruby Ruby
      # EnvironmentWorker is not currently available in the Ruby SDK.
      ```
    </CodeGroup>
  </Step>
</Steps>

Keep the following in mind when you wrap an MCP server:

* **Tools are declared, not discovered at runtime.** The worker lists the MCP server's tools once at startup and cannot add tools to a running session. When the server's tools change, declare them again, on the agent or on an idle session through [Updating the agent configuration](https://platform.claude.com/docs/en/managed-agents/session-operations#updating-the-agent-configuration), and restart the worker.
* **Names and descriptions must fit the Managed Agents API.** Custom tool names are unique per agent and use letters, digits, underscores, and hyphens (1–128 characters); a non-empty description is required; and an agent's `tools` array takes at most 128 entries (each wrapped tool is one entry, and the built-in toolset is one more). The API rejects a declaration that reuses a tool name, names a custom tool after a built-in agent tool such as `bash` or `read`, or uses the reserved `mcp__` prefix. The MCP helpers keep the server's names and descriptions, so rename or trim where needed. When two servers expose the same tool name, define the wrapper yourself under a prefixed name and have it call the server's original tool name.
* **Most schemas pass through unchanged.** The API accepts the JSON Schema keywords MCP servers commonly emit, such as `additionalProperties` and `title`. It rejects reference keywords such as `$ref` anywhere in a custom tool's `input_schema`, so inline the schemas that generators such as pydantic factor into `$defs`. It also rejects top-level `oneOf`, `anyOf`, and `allOf`, and property names outside letters, digits, underscores, dots, and hyphens (1–64 characters).
* **Tool failures surface as error tool results.** When the MCP server reports a tool error, the worker posts an error tool result the model can react to. MCP content with no tool result equivalent, such as audio blocks and resource links, also surfaces as an error. Set a timeout on the MCP client for a faster and clearer failure, as the Python worker example does with `read_timeout_seconds`. Without one, a hung call becomes an error result only when the TypeScript MCP SDK's default request timeout fires (about a minute) or when the worker's own backstop does: about two and a half minutes in Python, and two minutes in Go, where the worker cancels a tool call that outlives its 120-second default and posts an error result.
* **Wrap servers you operate or trust.** A wrapped tool's name, description, and results enter the model's context like any other tool's: untrusted input that can influence what the agent does with its other tools, including `bash` on the worker host. Declare only the tools you intend the agent to use.
* **Permission policies do not apply to custom tools.** [Permission policies](https://platform.claude.com/docs/en/managed-agents/permission-policies#custom-tools) govern the built-in and MCP toolsets; the worker executes every wrapped tool call the model makes, so put any approval step in your own tool code.


## Monitoring and operations

Source: https://platform.claude.com/llms-full.txt#monitoring-and-operations

These calls run from your monitoring or operations tooling, authenticated with your Claude API key, to observe and manage the worker fleet. The claim and keep-alive loop is handled inside the worker helpers, so you don't call those endpoints directly.

<Warning>
  These endpoints accept either your organization API key or the environment key. Call them from outside the worker host with your organization API key. Setting `ANTHROPIC_API_KEY` on the worker host exposes an organization-scoped credential to agent tool calls.
</Warning>

### Read queue depth

`work.stats` returns the queue state for an environment:

* `depth` is the number of items waiting to be claimed. Scale your worker fleet or alert on backlog based on this value.
* `pending` is the number of items claimed by a worker but not yet acknowledged. The worker helpers acknowledge each item before processing it, so this value stays near zero in normal operation; a sustained non-zero value means a worker stalled between claiming and acknowledging.
* `oldest_queued_at` is the timestamp of the oldest item still in the queue, waiting to be claimed or claimed but not yet acknowledged, or `null` when there is none.
* `workers_polling` is the number of workers that have polled in the last 30 seconds. Use this for liveness alerting.

<CodeGroup>
  ```bash cURL
  curl -sS "https://api.anthropic.com/v1/environments/$ANTHROPIC_ENVIRONMENT_ID/work/stats" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "anthropic-version: 2023-06-01"

bash CLI
  ant beta:environments:work stats --environment-id "$ANTHROPIC_ENVIRONMENT_ID"

python Python
  import os

  import anthropic

  client = anthropic.Anthropic()

  stats = client.beta.environments.work.stats(os.environ["ANTHROPIC_ENVIRONMENT_ID"])
  print(f"depth={stats.depth} pending={stats.pending}")

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";

  const client = new Anthropic();

  const stats = await client.beta.environments.work.stats(process.env.ANTHROPIC_ENVIRONMENT_ID!);

  console.log(`depth=${stats.depth} pending=${stats.pending}`);

csharp C#
  using Anthropic;

  var client = new AnthropicClient();

  var environmentId = Environment.GetEnvironmentVariable("ANTHROPIC_ENVIRONMENT_ID")!;

  var stats = await client.Beta.Environments.Work.Stats(environmentId);

  Console.WriteLine($"depth={stats.Depth} pending={stats.Pending}");

go Go
  package main

  import (
  	"context"
  	"fmt"
  	"os"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  func main() {
  	client := anthropic.NewClient()
  	environmentID := os.Getenv("ANTHROPIC_ENVIRONMENT_ID")

  	stats, err := client.Beta.Environments.Work.Stats(
  		context.Background(),
  		environmentID,
  		anthropic.BetaEnvironmentWorkStatsParams{},
  	)
  	if err != nil {
  		panic(err)
  	}

  	fmt.Printf("depth=%d pending=%d\n", stats.Depth, stats.Pending)
  }

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.models.beta.environments.work.BetaSelfHostedWorkQueueStats;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      BetaSelfHostedWorkQueueStats stats = client.beta()
          .environments()
          .work()
          .stats(System.getenv("ANTHROPIC_ENVIRONMENT_ID"));

      IO.println("depth=" + stats.depth() + " pending=" + stats.pending());
  }

php PHP
  <?php

  use Anthropic\Client;

  $client = new Client();

  $stats = $client->beta->environments->work->stats(getenv('ANTHROPIC_ENVIRONMENT_ID'));

  printf("depth=%d pending=%d\n", $stats->depth, $stats->pending);

ruby Ruby
  require "anthropic"

  client = Anthropic::Client.new

  stats = client.beta.environments.work.stats(ENV.fetch("ANTHROPIC_ENVIRONMENT_ID"))

  puts "depth=#{stats.depth} pending=#{stats.pending}"

text wrap
{
  "type": "work_queue_stats",
  "depth": 0,
  "pending": 0,
  "oldest_queued_at": null,
  "workers_polling": 0
}

bash cURL
  curl -sS "https://api.anthropic.com/v1/environments/$ANTHROPIC_ENVIRONMENT_ID/work/$ANTHROPIC_WORK_ID/stop" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{}'

bash CLI
  ant beta:environments:work stop \
    --environment-id "$ANTHROPIC_ENVIRONMENT_ID" \
    --work-id "$ANTHROPIC_WORK_ID"

python Python
  import os

  import anthropic

  client = anthropic.Anthropic()

  work = client.beta.environments.work.stop(
      os.environ["ANTHROPIC_WORK_ID"],
      environment_id=os.environ["ANTHROPIC_ENVIRONMENT_ID"],
  )
  print(work.state)

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";

  const client = new Anthropic();

  const work = await client.beta.environments.work.stop(process.env.ANTHROPIC_WORK_ID!, {
    environment_id: process.env.ANTHROPIC_ENVIRONMENT_ID!
  });

  console.log(work.state);

csharp C#
  using Anthropic;

  var client = new AnthropicClient();

  var work = await client.Beta.Environments.Work.Stop(
      Environment.GetEnvironmentVariable("ANTHROPIC_WORK_ID")!,
      new()
      {
          EnvironmentID = Environment.GetEnvironmentVariable("ANTHROPIC_ENVIRONMENT_ID")!
      }
  );

  Console.WriteLine(work.State);

go Go
  package main

  import (
  	"context"
  	"fmt"
  	"os"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  func main() {
  	client := anthropic.NewClient()

  	work, err := client.Beta.Environments.Work.Stop(
  		context.Background(),
  		os.Getenv("ANTHROPIC_WORK_ID"),
  		anthropic.BetaEnvironmentWorkStopParams{
  			EnvironmentID: os.Getenv("ANTHROPIC_ENVIRONMENT_ID"),
  		},
  	)
  	if err != nil {
  		panic(err)
  	}
  	fmt.Println(work.State)
  }

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.models.beta.environments.work.BetaSelfHostedWork;
  import com.anthropic.models.beta.environments.work.BetaSelfHostedWorkStopRequest;
  import com.anthropic.models.beta.environments.work.WorkStopParams;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      BetaSelfHostedWork work = client.beta().environments().work().stop(
          WorkStopParams.builder()
              .environmentId(System.getenv("ANTHROPIC_ENVIRONMENT_ID"))
              .workId(System.getenv("ANTHROPIC_WORK_ID"))
              .betaSelfHostedWorkStopRequest(BetaSelfHostedWorkStopRequest.builder().build())
              .build()
      );

      IO.println(work.state());
  }

php PHP
  <?php

  use Anthropic\Client;

  $client = new Client();

  $work = $client->beta->environments->work->stop(
      getenv('ANTHROPIC_WORK_ID'),
      environmentID: getenv('ANTHROPIC_ENVIRONMENT_ID'),
  );

  echo $work->state . "\n";

ruby Ruby
  require "anthropic"

  client = Anthropic::Client.new

  work = client.beta.environments.work.stop(
    ENV.fetch("ANTHROPIC_WORK_ID"),
    environment_id: ENV.fetch("ANTHROPIC_ENVIRONMENT_ID")
  )

  puts work.state
  ```
</CodeGroup>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-75

<CardGroup cols={2}>
  <Card title="Security model" icon="lock" href="https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes-security">
    Shared responsibility model for self-hosted sandbox environments.
  </Card>

  <Card title="Start a session" icon="settings" href="https://platform.claude.com/docs/en/managed-agents/sessions">
    Create a session to run your agent and begin executing tasks.
  </Card>

  <Card title="MCP tunnels" icon="bolt" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview">
    Securely connect Claude to MCP servers running in your private network without opening inbound ports or exposing services to the public internet.
  </Card>
</CardGroup>


### Delegate work to your agent

---
title: Authenticate with vaults
url: https://platform.claude.com/docs/en/managed-agents/vaults
description: Register per-user credentials when creating sessions.
---

Vaults and credentials are authentication primitives that let you register credentials for third-party services once and reference them by ID at session creation. This means you don't need to run your own secret store, transmit tokens on every call, or lose track of which end user an agent acted on behalf of.

The vault reference is a per-session parameter, so you can manage your product at the `agent` resource granularity and your users at the `session` resource granularity.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Create a vault

Source: https://platform.claude.com/llms-full.txt#create-a-vault

<Warning>
  Vaults and credentials are workspace-scoped, meaning any API key with workspace access can reference them when creating a session. To revoke access, delete the vault or credential.
</Warning>

A vault is the collection of `credentials` associated with an end user. Give it a `display_name` and optionally tag it with `metadata` so you can map it back to your own user records.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  vault_id=$(curl --fail-with-body -sS https://api.anthropic.com/v1/vaults \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    --data @- <<'EOF' | jq -r '.id'
  {
    "display_name": "Alice",
    "metadata": {"external_user_id": "usr_abc123"}
  }
  EOF
  )
  echo "$vault_id"  # "vlt_01ABC..."

bash CLI
    VAULT_ID=$(ant beta:vaults create --transform id --raw-output < alice.vault.yaml)
    echo "$VAULT_ID"  # "vlt_01ABC..."

yaml
      display_name: Alice
      metadata:
        external_user_id: usr_abc123

python Python
  vault = client.beta.vaults.create(
      display_name="Alice",
      metadata={"external_user_id": "usr_abc123"},
  )
  print(vault.id)  # "vlt_01ABC..."

typescript TypeScript
  const vault = await client.beta.vaults.create({
    display_name: "Alice",
    metadata: { external_user_id: "usr_abc123" },
  });
  console.log(vault.id); // "vlt_01ABC..."

csharp C#
  var vault = await client.Beta.Vaults.Create(new()
  {
      DisplayName = "Alice",
      Metadata = new Dictionary<string, string> { ["external_user_id"] = "usr_abc123" },
  });
  Console.WriteLine(vault.ID); // "vlt_01ABC..."

go Go
  vault, err := client.Beta.Vaults.New(ctx, anthropic.BetaVaultNewParams{
  	DisplayName: "Alice",
  	Metadata:    map[string]string{"external_user_id": "usr_abc123"},
  })
  if err != nil {
  	panic(err)
  }
  fmt.Println(vault.ID) // "vlt_01ABC..."

java Java
  var vault = client.beta().vaults().create(VaultCreateParams.builder()
      .displayName("Alice")
      .metadata(VaultCreateParams.Metadata.builder()
          .putAdditionalProperty("external_user_id", JsonValue.from("usr_abc123"))
          .build())
      .build());
  IO.println(vault.id()); // "vlt_01ABC..."

php PHP
  $vault = $client->beta->vaults->create(
      displayName: 'Alice',
      metadata: ['external_user_id' => 'usr_abc123'],
  );
  echo $vault->id . "\n"; // "vlt_01ABC..."

ruby Ruby
  vault = client.beta.vaults.create(
    display_name: "Alice",
    metadata: {external_user_id: "usr_abc123"}
  )
  puts vault.id # "vlt_01ABC..."

json
{
  "type": "vault",
  "id": "vlt_01ABC...",
  "display_name": "Alice",
  "metadata": { "external_user_id": "usr_abc123" },
  "created_at": "2026-03-18T10:00:00Z",
  "updated_at": "2026-03-18T10:00:00Z",
  "archived_at": null
}
```


## Add a credential

Source: https://platform.claude.com/llms-full.txt#add-a-credential

Two credential categories are supported:

* **MCP credentials** (`mcp_oauth`, `static_bearer`): each credential is keyed by an `mcp_server_url`. When the agent connects to a server at that URL at session runtime, the token is injected automatically.
* **Environment variables** (`environment_variable`): each credential is keyed by a `secret_name` (the environment variable name) and stored in the sandbox as an opaque placeholder. When the agent initiates an outbound request, the opaque placeholder is substituted with the real secret at egress. The agent never sees the secret value. Use this for any service that authenticates through an environment variable, such as CLIs, SDKs, or direct API calls.

The actual credential values you supply (`token`, `access_token`, `refresh_token`, `client_secret`, `secret_value`) are treated as sensitive, write-only fields and never returned in API responses.

<Note>
  Environment variable credentials (`environment_variable`) are not yet supported with [self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes).
</Note>

<Tabs>
  <Tab title="MCP OAuth">
    Use `mcp_oauth` when the MCP server uses OAuth 2.0. If you supply a `refresh` block, Anthropic refreshes the access token on your behalf when it expires.

    The `refresh.token_endpoint_auth.type` field indicates how to authenticate the refresh call:

    * `none`: public client
    * `client_secret_basic`: HTTP Basic authentication with the client secret
    * `client_secret_post`: client secret in the POST body

    <CodeGroup defaultLanguage="CLI">
      ```bash cURL
      credential_id=$(curl --fail-with-body -sS "https://api.anthropic.com/v1/vaults/$vault_id/credentials" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        -H "content-type: application/json" \
        --data @- <<'EOF' | jq -r '.id'
      {
        "display_name": "Alice's Slack",
        "auth": {
          "type": "mcp_oauth",
          "mcp_server_url": "https://mcp.slack.com/mcp",
          "access_token": "xoxp-...",
          "expires_at": "2099-12-31T23:59:59Z",
          "refresh": {
            "token_endpoint": "https://slack.com/api/oauth.v2.access",
            "client_id": "1234567890.0987654321",
            "scope": "channels:read chat:write",
            "refresh_token": "xoxe-1-...",
            "token_endpoint_auth": {"type": "client_secret_post", "client_secret": "abc123..."}
          }
        }
      }
      EOF
      )

bash CLI
      CREDENTIAL_ID=$(ant beta:vaults:credentials create \
        --vault-id "$VAULT_ID" \
        --display-name "Alice's Slack" \
        --transform id --raw-output <<'YAML'
      auth:
        type: mcp_oauth
        mcp_server_url: https://mcp.slack.com/mcp
        access_token: xoxp-...
        expires_at: "2099-12-31T23:59:59Z"
        refresh:
          token_endpoint: https://slack.com/api/oauth.v2.access
          client_id: "1234567890.0987654321"
          scope: channels:read chat:write
          refresh_token: xoxe-1-...
          token_endpoint_auth:
            type: client_secret_post
            client_secret: abc123...
      YAML
      )

python Python
      credential = client.beta.vaults.credentials.create(
          vault_id=vault.id,
          display_name="Alice's Slack",
          auth={
              "type": "mcp_oauth",
              "mcp_server_url": "https://mcp.slack.com/mcp",
              "access_token": "xoxp-...",
              "expires_at": "2099-12-31T23:59:59Z",
              "refresh": {
                  "token_endpoint": "https://slack.com/api/oauth.v2.access",
                  "client_id": "1234567890.0987654321",
                  "scope": "channels:read chat:write",
                  "refresh_token": "xoxe-1-...",
                  "token_endpoint_auth": {"type": "client_secret_post", "client_secret": "abc123..."},
              },
          },
      )

typescript TypeScript
      const credential = await client.beta.vaults.credentials.create(vault.id, {
        display_name: "Alice's Slack",
        auth: {
          type: "mcp_oauth",
          mcp_server_url: "https://mcp.slack.com/mcp",
          access_token: "xoxp-...",
          expires_at: "2099-12-31T23:59:59Z",
          refresh: {
            token_endpoint: "https://slack.com/api/oauth.v2.access",
            client_id: "1234567890.0987654321",
            scope: "channels:read chat:write",
            refresh_token: "xoxe-1-...",
            token_endpoint_auth: {
              type: "client_secret_post",
              client_secret: "abc123...",
            },
          },
        },
      });

csharp C#
      var credential = await client.Beta.Vaults.Credentials.Create(vault.ID, new()
      {
          DisplayName = "Alice's Slack",
          Auth = new BetaManagedAgentsMcpOAuthCreateParams
          {
              Type = BetaManagedAgentsMcpOAuthCreateParamsType.McpOAuth,
              McpServerUrl = "https://mcp.slack.com/mcp",
              AccessToken = "xoxp-...",
              ExpiresAt = DateTimeOffset.Parse("2099-12-31T23:59:59Z"),
              Refresh = new()
              {
                  TokenEndpoint = "https://slack.com/api/oauth.v2.access",
                  ClientID = "1234567890.0987654321",
                  Scope = "channels:read chat:write",
                  RefreshToken = "xoxe-1-...",
                  TokenEndpointAuth = new BetaManagedAgentsTokenEndpointAuthPostParam
                  {
                      Type = BetaManagedAgentsTokenEndpointAuthPostParamType.ClientSecretPost,
                      ClientSecret = "abc123...",
                  },
              },
          },
      });

go Go
      credential, err := client.Beta.Vaults.Credentials.New(ctx, vault.ID, anthropic.BetaVaultCredentialNewParams{
      	DisplayName: anthropic.String("Alice's Slack"),
      	Auth: anthropic.BetaVaultCredentialNewParamsAuthUnion{
      		OfMCPOAuth: &anthropic.BetaManagedAgentsMCPOAuthCreateParams{
      			Type:         anthropic.BetaManagedAgentsMCPOAuthCreateParamsTypeMCPOAuth,
      			MCPServerURL: "https://mcp.slack.com/mcp",
      			AccessToken:  "xoxp-...",
      			ExpiresAt:    anthropic.Time(time.Date(2099, time.December, 31, 23, 59, 59, 0, time.UTC)),
      			Refresh: anthropic.BetaManagedAgentsMCPOAuthRefreshParams{
      				TokenEndpoint: "https://slack.com/api/oauth.v2.access",
      				ClientID:      "1234567890.0987654321",
      				Scope:         anthropic.String("channels:read chat:write"),
      				RefreshToken:  "xoxe-1-...",
      				TokenEndpointAuth: anthropic.BetaManagedAgentsMCPOAuthRefreshParamsTokenEndpointAuthUnion{
      					OfClientSecretPost: &anthropic.BetaManagedAgentsTokenEndpointAuthPostParam{
      						Type:         anthropic.BetaManagedAgentsTokenEndpointAuthPostParamTypeClientSecretPost,
      						ClientSecret: "abc123...",
      					},
      				},
      			},
      		},
      	},
      })
      if err != nil {
      	panic(err)
      }

java Java
      var credential = client.beta().vaults().credentials().create(vault.id(),
          CredentialCreateParams.builder()
              .displayName("Alice's Slack")
              .auth(BetaManagedAgentsMcpOAuthCreateParams.builder()
                  .type(BetaManagedAgentsMcpOAuthCreateParams.Type.MCP_OAUTH)
                  .mcpServerUrl("https://mcp.slack.com/mcp")
                  .accessToken("xoxp-...")
                  .expiresAt(OffsetDateTime.parse("2099-12-31T23:59:59Z"))
                  .refresh(BetaManagedAgentsMcpOAuthRefreshParams.builder()
                      .tokenEndpoint("https://slack.com/api/oauth.v2.access")
                      .clientId("1234567890.0987654321")
                      .scope("channels:read chat:write")
                      .refreshToken("xoxe-1-...")
                      .clientSecretPostTokenEndpointAuth("abc123...")
                      .build())
                  .build())
              .build());

php PHP
      $credential = $client->beta->vaults->credentials->create(
          vaultID: $vault->id,
          displayName: "Alice's Slack",
          auth: ManagedAgentsMCPOAuthCreateParams::with(
              type: 'mcp_oauth',
              mcpServerURL: 'https://mcp.slack.com/mcp',
              accessToken: 'xoxp-...',
              expiresAt: new DateTimeImmutable('2099-12-31T23:59:59Z'),
              refresh: ManagedAgentsMCPOAuthRefreshParams::with(
                  tokenEndpoint: 'https://slack.com/api/oauth.v2.access',
                  clientID: '1234567890.0987654321',
                  scope: 'channels:read chat:write',
                  refreshToken: 'xoxe-1-...',
                  tokenEndpointAuth: ManagedAgentsTokenEndpointAuthPostParam::with(
                      type: 'client_secret_post',
                      clientSecret: 'abc123...',
                  ),
              ),
          ),
      );

ruby Ruby
      credential = client.beta.vaults.credentials.create(
        vault.id,
        display_name: "Alice's Slack",
        auth: {
          type: "mcp_oauth",
          mcp_server_url: "https://mcp.slack.com/mcp",
          access_token: "xoxp-...",
          expires_at: "2099-12-31T23:59:59Z",
          refresh: {
            token_endpoint: "https://slack.com/api/oauth.v2.access",
            client_id: "1234567890.0987654321",
            scope: "channels:read chat:write",
            refresh_token: "xoxe-1-...",
            token_endpoint_auth: {
              type: "client_secret_post",
              client_secret: "abc123..."
            }
          }
        }
      )

bash cURL
      curl --fail-with-body -sS "https://api.anthropic.com/v1/vaults/$vault_id/credentials" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        -H "content-type: application/json" \
        --data @- <<'EOF'
      {
        "display_name": "Linear API key",
        "auth": {
          "type": "static_bearer",
          "mcp_server_url": "https://mcp.linear.app/mcp",
          "token": "lin_api_your_linear_key"
        }
      }
      EOF

bash CLI
      ant beta:vaults:credentials create --vault-id "$VAULT_ID" <<'YAML'
      display_name: Linear API key
      auth:
        type: static_bearer
        mcp_server_url: https://mcp.linear.app/mcp
        token: lin_api_your_linear_key
      YAML

python Python
      bearer_credential = client.beta.vaults.credentials.create(
          vault_id=vault.id,
          display_name="Linear API key",
          auth={
              "type": "static_bearer",
              "mcp_server_url": "https://mcp.linear.app/mcp",
              "token": "lin_api_your_linear_key",
          },
      )

typescript TypeScript
      const bearerCredential = await client.beta.vaults.credentials.create(vault.id, {
        display_name: "Linear API key",
        auth: {
          type: "static_bearer",
          mcp_server_url: "https://mcp.linear.app/mcp",
          token: "lin_api_your_linear_key",
        },
      });

csharp C#
      var bearerCredential = await client.Beta.Vaults.Credentials.Create(vault.ID, new()
      {
          DisplayName = "Linear API key",
          Auth = new BetaManagedAgentsStaticBearerCreateParams
          {
              Type = BetaManagedAgentsStaticBearerCreateParamsType.StaticBearer,
              McpServerUrl = "https://mcp.linear.app/mcp",
              Token = "lin_api_your_linear_key",
          },
      });

go Go
      bearerCredential, err := client.Beta.Vaults.Credentials.New(ctx, vault.ID, anthropic.BetaVaultCredentialNewParams{
      	DisplayName: anthropic.String("Linear API key"),
      	Auth: anthropic.BetaVaultCredentialNewParamsAuthUnion{
      		OfStaticBearer: &anthropic.BetaManagedAgentsStaticBearerCreateParams{
      			Type:         anthropic.BetaManagedAgentsStaticBearerCreateParamsTypeStaticBearer,
      			MCPServerURL: "https://mcp.linear.app/mcp",
      			Token:        "lin_api_your_linear_key",
      		},
      	},
      })
      if err != nil {
      	panic(err)
      }
      _ = bearerCredential

java Java
      var bearerCredential = client.beta().vaults().credentials().create(vault.id(),
          CredentialCreateParams.builder()
              .displayName("Linear API key")
              .auth(BetaManagedAgentsStaticBearerCreateParams.builder()
                  .type(BetaManagedAgentsStaticBearerCreateParams.Type.STATIC_BEARER)
                  .mcpServerUrl("https://mcp.linear.app/mcp")
                  .token("lin_api_your_linear_key")
                  .build())
              .build());

php PHP
      $bearerCredential = $client->beta->vaults->credentials->create(
          vaultID: $vault->id,
          displayName: 'Linear API key',
          auth: ManagedAgentsStaticBearerCreateParams::with(
              type: 'static_bearer',
              mcpServerURL: 'https://mcp.linear.app/mcp',
              token: 'lin_api_your_linear_key',
          ),
      );

ruby Ruby
      bearer_credential = client.beta.vaults.credentials.create(
        vault.id,
        display_name: "Linear API key",
        auth: {
          type: "static_bearer",
          mcp_server_url: "https://mcp.linear.app/mcp",
          token: "lin_api_your_linear_key"
        }
      )

bash cURL
      curl --fail-with-body -sS "https://api.anthropic.com/v1/vaults/$vault_id/credentials" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        -H "content-type: application/json" \
        --data @- <<'EOF' | jq '.auth.injection_location'
      {
        "auth": {
          "type": "environment_variable",
          "secret_name": "NOTION_API_KEY",
          "secret_value": "ntn_your-secret-here",
          "networking": {
            "type": "limited",
            "allowed_hosts": ["api.notion.com"]
          },
          "injection_location": {"header": true}
        },
        "display_name": "Notion API key for sandbox"
      }
      EOF

bash CLI
      ant beta:vaults:credentials create \
        --vault-id "$VAULT_ID" \
        --transform 'auth.injection_location' --format json <<'YAML'
      display_name: Notion API key for sandbox
      auth:
        type: environment_variable
        secret_name: NOTION_API_KEY
        secret_value: ntn_your-secret-here
        injection_location:
          header: true
        networking:
          type: limited
          allowed_hosts: [api.notion.com]
      YAML

python Python
      env_credential = client.beta.vaults.credentials.create(
          vault_id=vault.id,
          display_name="Notion API key for sandbox",
          auth={
              "type": "environment_variable",
              "secret_name": "NOTION_API_KEY",
              "secret_value": "ntn_your-secret-here",
              "networking": {
                  "type": "limited",
                  "allowed_hosts": ["api.notion.com"],
              },
              "injection_location": {"header": True},
          },
      )
      if env_credential.auth.type == "environment_variable":
          location = env_credential.auth.injection_location
          print(f"header: {location.header}, body: {location.body}")  # header: True, body: False

typescript TypeScript
      const envVarCredential = await client.beta.vaults.credentials.create(vault.id, {
        display_name: "Notion API key for sandbox",
        auth: {
          type: "environment_variable",
          secret_name: "NOTION_API_KEY",
          secret_value: "ntn_your-secret-here",
          networking: {
            type: "limited",
            allowed_hosts: ["api.notion.com"],
          },
          injection_location: { header: true },
        },
      });
      if (envVarCredential.auth.type === "environment_variable") {
        console.log(envVarCredential.auth.injection_location); // { header: true, body: false }
      }

csharp C#
      var envVarCredential = await client.Beta.Vaults.Credentials.Create(vault.ID, new()
      {
          DisplayName = "Notion API key for sandbox",
          Auth = new BetaManagedAgentsEnvironmentVariableCreateParams
          {
              Type = BetaManagedAgentsEnvironmentVariableCreateParamsType.EnvironmentVariable,
              SecretName = "NOTION_API_KEY",
              SecretValue = "ntn_your-secret-here",
              Networking = new BetaManagedAgentsLimitedCredentialNetworkingParams
              {
                  Type = BetaManagedAgentsLimitedCredentialNetworkingParamsType.Limited,
                  AllowedHosts = ["api.notion.com"],
              },
              InjectionLocation = new() { Header = true },
          },
      });
      if (envVarCredential.Auth.TryPickBetaManagedAgentsEnvironmentVariableAuthResponse(out var envVarAuth))
      {
          var injectionLocation = envVarAuth.InjectionLocation;
          Console.WriteLine($"Header: {injectionLocation.Header}, Body: {injectionLocation.Body}"); // "Header: True, Body: False"
      }

go Go
      envVarCredential, err := client.Beta.Vaults.Credentials.New(ctx, vault.ID, anthropic.BetaVaultCredentialNewParams{
      	DisplayName: anthropic.String("Notion API key for sandbox"),
      	Auth: anthropic.BetaVaultCredentialNewParamsAuthUnion{
      		OfEnvironmentVariable: &anthropic.BetaManagedAgentsEnvironmentVariableCreateParams{
      			Type:        anthropic.BetaManagedAgentsEnvironmentVariableCreateParamsTypeEnvironmentVariable,
      			SecretName:  "NOTION_API_KEY",
      			SecretValue: "ntn_your-secret-here",
      			Networking: anthropic.BetaManagedAgentsCredentialNetworkingParamsUnion{
      				OfLimited: &anthropic.BetaManagedAgentsLimitedCredentialNetworkingParams{
      					Type:         anthropic.BetaManagedAgentsLimitedCredentialNetworkingParamsTypeLimited,
      					AllowedHosts: []string{"api.notion.com"},
      				},
      			},
      			InjectionLocation: anthropic.BetaManagedAgentsInjectionLocationParams{
      				Header: anthropic.Bool(true),
      			},
      		},
      	},
      })
      if err != nil {
      	panic(err)
      }
      if envVarAuth, ok := envVarCredential.Auth.AsAny().(anthropic.BetaManagedAgentsEnvironmentVariableAuthResponse); ok {
      	injectionLocation := envVarAuth.InjectionLocation
      	fmt.Printf("Header:%t Body:%t\n", injectionLocation.Header, injectionLocation.Body) // "Header:true Body:false"
      }

java Java
      var envVarCredential = client.beta().vaults().credentials().create(vault.id(),
          CredentialCreateParams.builder()
              .displayName("Notion API key for sandbox")
              .auth(BetaManagedAgentsEnvironmentVariableCreateParams.builder()
                  .type(BetaManagedAgentsEnvironmentVariableCreateParams.Type.ENVIRONMENT_VARIABLE)
                  .secretName("NOTION_API_KEY")
                  .secretValue("ntn_your-secret-here")
                  .limitedNetworking(List.of("api.notion.com"))
                  .injectionLocation(BetaManagedAgentsInjectionLocationParams.builder()
                      .header(true)
                      .build())
                  .build())
              .build());
      envVarCredential.auth().environmentVariable().ifPresent(envVarAuth -> {
          var injectionLocation = envVarAuth.injectionLocation();
          IO.println("header=" + injectionLocation.header() + " body=" + injectionLocation.body()); // header=true body=false
      });

php PHP
      $envVarCredential = $client->beta->vaults->credentials->create(
          vaultID: $vault->id,
          displayName: 'Notion API key for sandbox',
          auth: ManagedAgentsEnvironmentVariableCreateParams::with(
              type: ManagedAgentsEnvironmentVariableCreateParams\Type::ENVIRONMENT_VARIABLE,
              secretName: 'NOTION_API_KEY',
              secretValue: 'ntn_your-secret-here',
              networking: ManagedAgentsLimitedCredentialNetworkingParams::with(
                  type: ManagedAgentsLimitedCredentialNetworkingParams\Type::LIMITED,
                  allowedHosts: ['api.notion.com'],
              ),
              injectionLocation: ManagedAgentsInjectionLocationParams::with(header: true),
          ),
      );
      if ($envVarCredential->auth instanceof ManagedAgentsEnvironmentVariableAuthResponse) {
          $injectionLocation = $envVarCredential->auth->injectionLocation;
          echo 'header: ' . json_encode($injectionLocation->header) . "\n"; // header: true
          echo 'body: ' . json_encode($injectionLocation->body) . "\n"; // body: false
      }

ruby Ruby
      env_credential = client.beta.vaults.credentials.create(
        vault.id,
        display_name: "Notion API key for sandbox",
        auth: {
          type: "environment_variable",
          secret_name: "NOTION_API_KEY",
          secret_value: "ntn_your-secret-here",
          networking: {
            type: "limited",
            allowed_hosts: ["api.notion.com"]
          },
          injection_location: {header: true}
        }
      )
      if env_credential.auth.type == :environment_variable
        env_credential.auth.injection_location => {header:, body:}
        puts "header: #{header}, body: #{body}" # header: true, body: false
      end
      ```
    </CodeGroup>

    Request payloads are often assembled from content the agent is working with, so the request body is the broader exposure surface. Most services read an API key from a request header, so enabling only `header` is the narrower configuration. It scopes substitution to request header values for that credential.

    The credential's `injection_location` controls which parts of an outbound request the secret is substituted into. It is an optional object, a sibling of `networking`, with two Boolean fields: `header` (request headers) and `body` (request body). `injection_location` is independent of `networking.allowed_hosts`: `allowed_hosts` scopes which hosts the secret is substituted for, and `injection_location` scopes which parts of the request it is substituted into.

    `injection_location` behaves differently on create and on update:

    | Operation         | `injection_location` behavior                                                                                                                                                              |
    | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
    | Create credential | If you provide the object, any field you omit inside it defaults to `false`: `{"header": true}` creates a header-only credential. Omit the object entirely and both locations are enabled. |
    | Update credential | Fields merge individually: `{"body": false}` disables body substitution and leaves `header` unchanged.                                                                                     |

    A credential must have at least one location enabled, so a create or update that would disable both locations returns a 400 error. Passing an explicit `null` for the `injection_location` object or for either field also returns a 400 error ("omit the field instead"). The response always returns both fields with their resolved values.

    A placeholder in a disabled location is neither substituted nor stripped. The request is sent to the third party with the literal opaque placeholder string in that location. If a request arrives at the third party containing the literal placeholder string, either that location is disabled for the credential or the destination host is not covered by the credential's `networking.allowed_hosts`.

    <Note>
      Credentials created in the Console enable header injection only. If your client sends the secret in the request body, such as a form-encoded token request, the placeholder passes through literally and the service rejects it with its own authentication error. Enable body injection in the Console form when you create the credential, or update the credential with `{"injection_location": {"body": true}}`.
    </Note>

    The substitution happens at egress, not inside the sandbox. Anything that processes the credential locally sees the opaque placeholder, not the real value: clients that validate the credential format at startup may reject it, and clients that compute a request signature from the secret (for example, AWS SigV4) produce an invalid signature. Environment variable credentials work for clients that send the secret value verbatim in an outbound request, in a location the credential's `injection_location` enables.

    Substitution is outbound only. If a client uses the stored secret to fetch a session token (for example, an OAuth client-credentials grant), the returned token arrives in the sandbox unredacted. For exchange-based flows, perform the exchange yourself and store the resulting token in the vault instead.

    <Tip>
      Scope the API key to only the permissions the agent needs. The agent can do anything the key allows, so a key with broader permissions than necessary increases the blast radius if the agent behaves unexpectedly.
    </Tip>
  </Tab>
</Tabs>

Credentials are stored as provided and are not validated until session runtime. An invalid credential surfaces as an authentication or downstream error during the session, which is emitted but does not block the session from continuing.

Constraints:

* **Unique key per vault.** `mcp_server_url` (MCP credentials) and `secret_name` (environment variable credentials) must be unique among active credentials in a vault. Creating a duplicate returns a 409.
* **Keys are immutable.** To change `mcp_server_url` or `secret_name`, archive the credential and create a new one.
* **Maximum 20 credentials per vault.**


## Reference the vault at session creation

Source: https://platform.claude.com/llms-full.txt#reference-the-vault-at-session-creation

Pass `vault_ids` when creating a session:

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  session_id=$(curl --fail-with-body -sS https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    --data @- <<EOF | jq -r '.id'
  {
    "agent": "$agent_id",
    "environment_id": "$environment_id",
    "vault_ids": ["$vault_id"],
    "title": "Alice's Slack digest"
  }
  EOF
  )

bash CLI
  SESSION_ID=$(ant beta:sessions create \
    --agent "$AGENT_ID" \
    --environment-id "$ENVIRONMENT_ID" \
    --vault-id "$VAULT_ID" \
    --title "Alice's Slack digest" \
    --transform id --raw-output)

python Python
  session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
      vault_ids=[vault.id],
      title="Alice's Slack digest",
  )

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id,
    vault_ids: [vault.id],
    title: "Alice's Slack digest",
  });

csharp C#
  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = agent.ID,
      EnvironmentID = environment.ID,
      VaultIds = [vault.ID],
      Title = "Alice's Slack digest",
  });

go Go
  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfString: anthropic.String(agent.ID),
  	},
  	EnvironmentID: environment.ID,
  	VaultIDs:      []string{vault.ID},
  	Title:         anthropic.String("Alice's Slack digest"),
  })
  if err != nil {
  	panic(err)
  }

java Java
  var session = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(agent.id())
      .environmentId(environment.id())
      .vaultIds(List.of(vault.id()))
      .title("Alice's Slack digest")
      .build());

php PHP
  $session = $client->beta->sessions->create(
      agent: $agent->id,
      environmentID: $environment->id,
      vaultIDs: [$vault->id],
      title: "Alice's Slack digest",
  );

ruby Ruby
  session = client.beta.sessions.create(
    agent: agent.id,
    environment_id: environment.id,
    vault_ids: [vault.id],
    title: "Alice's Slack digest"
  )
  ```
</CodeGroup>

Runtime behavior:

* When no MCP credential matches by `mcp_server_url`, the connection is attempted unauthenticated and will error if the server requires authentication.
* When multiple vaults contain a matching credential, the first vault with a match wins.
* In [multiagent sessions](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration), vault credentials apply to every thread. An agent whose own definition declares the matching MCP server authenticates with these credentials. See [Connect agents to MCP servers](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration#connect-agents-to-mcp-servers).


## Rotate a credential

Source: https://platform.claude.com/llms-full.txt#rotate-a-credential

Secret values, `display_name`, and (on environment variable credentials) `injection_location` can be updated. `injection_location` updates merge per field, as described in the Environment variable tab of [Add a credential](https://platform.claude.com/docs/en/managed-agents/vaults#add-a-credential). For a running session, an `injection_location` update propagates the same way as a secret rotation: the session's credentials are re-resolved without a restart, as described in [Credential lifecycle](https://platform.claude.com/docs/en/managed-agents/vaults#credential-lifecycle), and the updated locations apply to the session's subsequent outbound requests. Structural fields (`mcp_server_url`, `secret_name`, `token_endpoint`, `client_id`) are locked after creation. To change them, archive the credential and create a new one.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl --fail-with-body -sS \
    "https://api.anthropic.com/v1/vaults/$vault_id/credentials/$credential_id" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    --data @- <<'EOF' > /dev/null
  {
    "auth": {
      "type": "mcp_oauth",
      "access_token": "xoxp-new-...",
      "expires_at": "2099-12-31T23:59:59Z",
      "refresh": {"refresh_token": "xoxe-1-new-..."}
    }
  }
  EOF

bash CLI
  ant beta:vaults:credentials update \
    --vault-id "$VAULT_ID" \
    --credential-id "$CREDENTIAL_ID" <<'YAML'
  auth:
    type: mcp_oauth
    access_token: xoxp-new-...
    expires_at: "2099-12-31T23:59:59Z"
    refresh:
      refresh_token: xoxe-1-new-...
  YAML

python Python
  client.beta.vaults.credentials.update(
      credential.id,
      vault_id=vault.id,
      auth={
          "type": "mcp_oauth",
          "access_token": "xoxp-new-...",
          "expires_at": "2099-12-31T23:59:59Z",
          "refresh": {"refresh_token": "xoxe-1-new-..."},
      },
  )

typescript TypeScript
  await client.beta.vaults.credentials.update(credential.id, {
    vault_id: vault.id,
    auth: {
      type: "mcp_oauth",
      access_token: "xoxp-new-...",
      expires_at: "2099-12-31T23:59:59Z",
      refresh: {
        refresh_token: "xoxe-1-new-...",
      },
    },
  });

csharp C#
  await client.Beta.Vaults.Credentials.Update(credential.ID, new()
  {
      VaultID = vault.ID,
      Auth = new BetaManagedAgentsMcpOAuthUpdateParams
      {
          Type = BetaManagedAgentsMcpOAuthUpdateParamsType.McpOAuth,
          AccessToken = "xoxp-new-...",
          ExpiresAt = DateTimeOffset.Parse("2099-12-31T23:59:59Z"),
          Refresh = new() { RefreshToken = "xoxe-1-new-..." },
      },
  });

go Go
  _, err = client.Beta.Vaults.Credentials.Update(ctx, credential.ID, anthropic.BetaVaultCredentialUpdateParams{
  	VaultID: vault.ID,
  	Auth: anthropic.BetaVaultCredentialUpdateParamsAuthUnion{
  		OfMCPOAuth: &anthropic.BetaManagedAgentsMCPOAuthUpdateParams{
  			Type:        anthropic.BetaManagedAgentsMCPOAuthUpdateParamsTypeMCPOAuth,
  			AccessToken: anthropic.String("xoxp-new-..."),
  			ExpiresAt:   anthropic.Time(time.Date(2099, time.December, 31, 23, 59, 59, 0, time.UTC)),
  			Refresh: anthropic.BetaManagedAgentsMCPOAuthRefreshUpdateParams{
  				RefreshToken: anthropic.String("xoxe-1-new-..."),
  			},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().vaults().credentials().update(credential.id(),
      CredentialUpdateParams.builder()
          .vaultId(vault.id())
          .auth(BetaManagedAgentsMcpOAuthUpdateParams.builder()
              .type(BetaManagedAgentsMcpOAuthUpdateParams.Type.MCP_OAUTH)
              .accessToken("xoxp-new-...")
              .expiresAt(OffsetDateTime.parse("2099-12-31T23:59:59Z"))
              .refresh(BetaManagedAgentsMcpOAuthRefreshUpdateParams.builder()
                  .refreshToken("xoxe-1-new-...")
                  .build())
              .build())
          .build());

php PHP
  $client->beta->vaults->credentials->update(
      $credential->id,
      vaultID: $vault->id,
      auth: ManagedAgentsMCPOAuthUpdateParams::with(
          type: 'mcp_oauth',
          accessToken: 'xoxp-new-...',
          expiresAt: new DateTimeImmutable('2099-12-31T23:59:59Z'),
          refresh: ManagedAgentsMCPOAuthRefreshUpdateParams::with(refreshToken: 'xoxe-1-new-...'),
      ),
  );

ruby Ruby
  client.beta.vaults.credentials.update(
    credential.id,
    vault_id: vault.id,
    auth: {
      type: "mcp_oauth",
      access_token: "xoxp-new-...",
      expires_at: "2099-12-31T23:59:59Z",
      refresh: {refresh_token: "xoxe-1-new-..."}
    }
  )
  ```
</CodeGroup>


## Credential lifecycle

Source: https://platform.claude.com/llms-full.txt#credential-lifecycle

Credentials are re-resolved periodically, both during a session and during the vault lifecycle. This ensures that credential rotation, archival, or deletion propagates to running sessions without a restart.

To be notified if a credential is archived, deleted, or fails to refresh, you can subscribe to the vault and credential [webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks) associated with those lifecycle changes.

| Event                             | Trigger                                                                                                              |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `vault.archived`                  | Vault archived. A `vault_credential.archived` event is also emitted for each underlying credential.                  |
| `vault.deleted`                   | Vault deleted. A `vault_credential.deleted` event is also emitted for each underlying credential.                    |
| `vault_credential.archived`       | Credential archived, either directly or as a result of vault archival.                                               |
| `vault_credential.deleted`        | Credential deleted, either directly or as a result of vault deletion.                                                |
| `vault_credential.refresh_failed` | An `mcp_oauth` credential cannot be refreshed (invalid refresh token, or irrecoverable error from the OAuth server). |

<Note>
  This is a non-exhaustive list of webhooks; see [Subscribe to webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks) for the complete list.
</Note>

For `mcp_oauth` credentials, re-resolution also refreshes the access token if it has expired. If the refresh fails, a `vault_credential.refresh_failed` event is emitted.

### Diagnose an OAuth refresh failure

To diagnose why a refresh failed, call `POST /v1/vaults/{vault_id}/credentials/{credential_id}/mcp_oauth_validate` (or `client.beta.vaults.credentials.mcp_oauth_validate(...)` in the SDK). This lets you decide how to handle the failure; the right action depends on the error type.

The top-level `status` tells you what to do next:

* `valid`: the token works; no action needed.
* `invalid`: the grant is gone or the OAuth server rejected the refresh with a 4xx. Prompt the end user to re-authorize.
* `unknown`: a transient error (5xx, 429, or network failure). Wait and retry.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl --fail-with-body -sS -X POST \
    "https://api.anthropic.com/v1/vaults/$vault_id/credentials/$credential_id/mcp_oauth_validate?beta=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
  ant beta:vaults:credentials mcp-oauth-validate \
    --vault-id "$VAULT_ID" \
    --credential-id "$CREDENTIAL_ID" \
    --transform status --raw-output  # "valid", "invalid", or "unknown"

python Python
  validation = client.beta.vaults.credentials.mcp_oauth_validate(
      credential.id,
      vault_id=vault.id,
  )
  print(validation.status)  # "valid", "invalid", or "unknown"

typescript TypeScript
  const validation = await client.beta.vaults.credentials.mcpOAuthValidate(
    credential.id,
    { vault_id: vault.id },
  );
  console.log(validation.status); // "valid", "invalid", or "unknown"

csharp C#
  var validation = await client.Beta.Vaults.Credentials.McpOAuthValidate(credential.ID, new()
  {
      VaultID = vault.ID,
  });
  Console.WriteLine(validation.Status.Raw()); // "valid", "invalid", or "unknown"

go Go
  validation, err := client.Beta.Vaults.Credentials.MCPOAuthValidate(ctx, credential.ID, anthropic.BetaVaultCredentialMCPOAuthValidateParams{
  	VaultID: vault.ID,
  })
  if err != nil {
  	panic(err)
  }
  fmt.Println(validation.Status) // "valid", "invalid", or "unknown"

java Java
  var validation = client.beta().vaults().credentials().mcpOAuthValidate(credential.id(),
      CredentialMcpOAuthValidateParams.builder()
          .vaultId(vault.id())
          .build());
  IO.println(validation.status()); // valid, invalid, or unknown

php PHP
  $validation = $client->beta->vaults->credentials->mcpOAuthValidate(
      $credential->id,
      vaultID: $vault->id,
  );
  echo $validation->status . "\n"; // "valid", "invalid", or "unknown"

ruby Ruby
  validation = client.beta.vaults.credentials.mcp_oauth_validate(
    credential.id,
    vault_id: vault.id
  )
  puts validation.status # :valid, :invalid, or :unknown

json
{
  "type": "vault_credential_validation",
  "credential_id": "vcrd_01ABC...",
  "vault_id": "vlt_01XYZ...",
  "validated_at": "2026-04-29T17:12:00Z",
  "has_refresh_token": false,
  "status": "invalid",
  "mcp_probe": {
    "method": "initialize",
    "http_response": {
      "status_code": 401,
      "content_type": "application/json",
      "body": "{\"error\":\"invalid_token\"}",
      "body_truncated": false
    }
  },
  "refresh": {
    "status": "no_refresh_token",
    "http_response": null
  }
}
```


## Other operations

Source: https://platform.claude.com/llms-full.txt#other-operations

* **List vaults or credentials:** Paginated, newest first. Archived records are excluded by default (pass `include_archived=true` to include them).
* **Archive a vault:** `POST /v1/vaults/{id}/archive`. Cascades to all credentials. Secrets are purged; records are retained for auditing. Future sessions referencing this vault fail; running sessions continue.
* **Archive a credential:** `POST /v1/vaults/{id}/credentials/{cred_id}/archive`. Purges the secret payload; the credential key (`mcp_server_url` or `secret_name`) remains visible and is freed for a replacement credential.
* **Delete a vault or credential:** Hard delete. The record is not retained. Use archive if you need an audit trail.


---
title: Define outcomes
url: https://platform.claude.com/docs/en/managed-agents/define-outcomes
description: Tell the agent what 'done' looks like, and let it iterate until it gets there.
---

An outcome tells the session what the end result should look like and how to measure its quality. The agent works toward that target, self-evaluating and iterating until the outcome is met.

When you define an outcome, the harness automatically provisions a *grader* to evaluate the artifact against a rubric. The grader uses a separate context window to avoid being influenced by the main agent's implementation choices.

The grader returns an explanation summarizing which criteria passed or failed, or confirming that the artifact satisfies the rubric. That feedback is handed back to the agent for the next iteration.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Create a rubric

Source: https://platform.claude.com/llms-full.txt#create-a-rubric

A rubric is a markdown document describing per-criterion scoring. The rubric is required.

<Accordion title="Tips for writing effective rubrics">
  Structure the rubric as explicit, gradeable criteria, such as "The CSV contains a price column with numeric values" rather than "The data looks good." The grader scores each criterion independently, so vague criteria produce noisy evaluations.

  If you don't have a rubric on hand, try giving Claude an example of a known-good artifact and asking it to analyze what makes that content good, then turn that analysis into a rubric. This middle-ground approach often produces better results than writing criteria from scratch.
</Accordion>

Example rubric:

```markdown
# DCF Model Rubric


## Revenue Projections

Source: https://platform.claude.com/llms-full.txt#revenue-projections

- Uses historical revenue data from the last 5 fiscal years
- Projects revenue for at least 5 years forward
- Growth rate assumptions are explicitly stated and reasonable


## Cost Structure

Source: https://platform.claude.com/llms-full.txt#cost-structure

- COGS and operating expenses are modeled separately
- Margins are consistent with historical trends or deviations are justified


## Discount Rate

Source: https://platform.claude.com/llms-full.txt#discount-rate

- WACC is calculated with stated assumptions for cost of equity and cost of debt
- Beta, risk-free rate, and equity risk premium are sourced or justified


## Terminal Value

Source: https://platform.claude.com/llms-full.txt#terminal-value

- Uses either perpetuity growth or exit multiple method (stated which)
- Terminal growth rate does not exceed long-term GDP growth


## Output Quality

Source: https://platform.claude.com/llms-full.txt#output-quality

- All figures are in a single .xlsx file with clearly labeled sheets
- Key assumptions are on a separate "Assumptions" sheet
- Sensitivity analysis on WACC and terminal growth rate is included

bash cURL
  rubric=$(curl -fsSL https://api.anthropic.com/v1/files \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -F file=@/tmp/rubric.md)
  rubric_id=$(jq -r '.id' <<<"$rubric")
  printf 'Uploaded rubric: %s\n' "$rubric_id"

bash CLI
  RUBRIC_ID=$(ant files upload \
    --file /tmp/rubric.md \
    --transform id --raw-output)

python Python
  import time
  from pathlib import Path

  from anthropic import Anthropic

  client = Anthropic()

  RUBRIC = """# DCF Model Rubric

  ## Revenue Projections
  - Uses historical revenue data from the last 5 fiscal years
  - Projects revenue for at least 5 years forward

  ## Output Quality
  - All figures are in a single .xlsx file with clearly labeled sheets
  """
  Path("/tmp/rubric.md").write_text(RUBRIC)

  rubric = client.files.upload(file=Path("/tmp/rubric.md"))
  print(f"Uploaded rubric: {rubric.id}")

typescript TypeScript
  import { writeFile, readFile } from "node:fs/promises";

  import Anthropic from "@anthropic-ai/sdk";
  import { toFile } from "@anthropic-ai/sdk";

  const client = new Anthropic();

  const RUBRIC = `# DCF Model Rubric

  ## Revenue Projections
  - Uses historical revenue data from the last 5 fiscal years
  - Projects revenue for at least 5 years forward

  ## Output Quality
  - All figures are in a single .xlsx file with clearly labeled sheets
  `;
  await writeFile("/tmp/rubric.md", RUBRIC);

  const rubric = await client.files.upload({
    file: await toFile(readFile("/tmp/rubric.md"), "/tmp/rubric.md"),
  });
  console.log(`Uploaded rubric: ${rubric.id}`);

csharp C#
  using Anthropic;
  using Anthropic.Models.Beta.Agents;
  using Anthropic.Models.Beta.Environments;
  using Anthropic.Models.Beta.Sessions;
  using Anthropic.Models.Beta.Sessions.Events;
  using Anthropic.Models.Files;

  var client = new AnthropicClient();

  const string Rubric = """
      # DCF Model Rubric

      ## Revenue Projections
      - Uses historical revenue data from the last 5 fiscal years
      - Projects revenue for at least 5 years forward

      ## Output Quality
      - All figures are in a single .xlsx file with clearly labeled sheets
      """;
  await File.WriteAllTextAsync("/tmp/rubric.md", Rubric);

  var rubric = await client.Files.Upload(new()
  {
      File = File.OpenRead("/tmp/rubric.md"),
  });
  Console.WriteLine($"Uploaded rubric: {rubric.ID}");

go Go
  package main

  import (
  	"context"
  	"fmt"
  	"io"
  	"os"
  	"time"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  const rubric = `# DCF Model Rubric

  ## Revenue Projections
  - Uses historical revenue data from the last 5 fiscal years
  - Projects revenue for at least 5 years forward

  ## Output Quality
  - All figures are in a single .xlsx file with clearly labeled sheets
  `

  func main() {
  	ctx := context.Background()
  	client := anthropic.NewClient()

  	if err := os.WriteFile("/tmp/rubric.md", []byte(rubric), 0o644); err != nil {
  		panic(err)
  	}

  	f, err := os.Open("/tmp/rubric.md")
  	if err != nil {
  		panic(err)
  	}

  	uploaded, err := client.Files.Upload(ctx, anthropic.FileUploadParams{
  		File: anthropic.File(f, "rubric.md", "text/markdown"),
  	})
  	if err != nil {
  		panic(err)
  	}
  	fmt.Printf("Uploaded rubric: %s\n", uploaded.ID)

java Java
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.http.HttpResponse;
  import com.anthropic.models.beta.AnthropicBeta;
  import com.anthropic.models.beta.agents.AgentCreateParams;
  import com.anthropic.models.beta.agents.BetaManagedAgentsAgentToolset20260401Params;
  import com.anthropic.models.beta.agents.BetaManagedAgentsModel;
  import com.anthropic.models.beta.environments.BetaCloudConfigParams;
  import com.anthropic.models.beta.environments.EnvironmentCreateParams;
  import com.anthropic.models.beta.files.FileListParams;
  import com.anthropic.models.beta.sessions.SessionCreateParams;
  import com.anthropic.models.beta.sessions.events.BetaManagedAgentsTextRubricParams;
  import com.anthropic.models.beta.sessions.events.BetaManagedAgentsUserDefineOutcomeEventParams;
  import com.anthropic.models.beta.sessions.events.BetaManagedAgentsUserInterruptEventParams;
  import com.anthropic.models.beta.sessions.events.EventSendParams;
  import com.anthropic.models.files.FileUploadParams;

  import java.io.InputStream;
  import java.nio.file.Files;
  import java.nio.file.Path;
  import java.nio.file.StandardCopyOption;

  void main() throws Exception {
      var client = AnthropicOkHttpClient.fromEnv();

      var RUBRIC = """
          # DCF Model Rubric

          ## Revenue Projections
          - Uses historical revenue data from the last 5 fiscal years
          - Projects revenue for at least 5 years forward

          ## Output Quality
          - All figures are in a single .xlsx file with clearly labeled sheets
          """;
      Files.writeString(Path.of("/tmp/rubric.md"), RUBRIC);

      var rubric = client.files().upload(
          FileUploadParams.builder()
              .file(Path.of("/tmp/rubric.md"))
              .build());
      IO.println("Uploaded rubric: " + rubric.id());

php PHP
  use Anthropic\Client;
  use Anthropic\Core\FileParam;

  $client = new Client();

  $rubricText = <<<'MD'
  # DCF Model Rubric

  ## Revenue Projections
  - Uses historical revenue data from the last 5 fiscal years
  - Projects revenue for at least 5 years forward

  ## Output Quality
  - All figures are in a single .xlsx file with clearly labeled sheets
  MD;
  file_put_contents('/tmp/rubric.md', $rubricText);

  $rubric = $client->files->upload(
      file: FileParam::fromResource(fopen('/tmp/rubric.md', 'r'), contentType: 'text/markdown'),
  );
  echo "Uploaded rubric: {$rubric->id}\n";

ruby Ruby
  require "anthropic"
  require "pathname"

  client = Anthropic::Client.new

  RUBRIC = <<~MD
    # DCF Model Rubric

    ## Revenue Projections
    - Uses historical revenue data from the last 5 fiscal years
    - Projects revenue for at least 5 years forward

    ## Output Quality
    - All figures are in a single .xlsx file with clearly labeled sheets
  MD
  File.write("/tmp/rubric.md", RUBRIC)

  rubric = client.files.upload(file: Pathname.new("/tmp/rubric.md"))
  puts "Uploaded rubric: #{rubric.id}"
  ```
</CodeGroup>


## Create a session with an outcome

Source: https://platform.claude.com/llms-full.txt#create-a-session-with-an-outcome

The following examples create a [session](https://platform.claude.com/docs/en/managed-agents/sessions) for an existing [agent](https://platform.claude.com/docs/en/managed-agents/agent-setup) and [environment](https://platform.claude.com/docs/en/managed-agents/environments) (both created separately), then send a `user.define_outcome` event. The agent begins work immediately. No additional user message event is required.

<CodeGroup>
  ```bash cURL
  # Create a session
  session=$(curl -fsSL https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    --json @- <<EOF
  {
    "agent": "$agent_id",
    "environment_id": "$environment_id",
    "title": "Financial analysis on Costco"
  }
  EOF
  )
  session_id=$(jq -r '.id' <<<"$session")

  # Define the outcome — agent starts working on receipt
  curl -fsSL "https://api.anthropic.com/v1/sessions/$session_id/events" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    --json @- >/dev/null <<EOF
  {
    "events": [
      {
        "type": "user.define_outcome",
        "description": "Build a DCF model for Costco in .xlsx",
        "rubric": {"type": "text", "content": "# DCF Model Rubric\n..."},
        "max_iterations": 5
      }
    ]
  }
  EOF
  # or: "rubric": {"type": "file", "file_id": "$rubric_id"}
  # "max_iterations" is optional; default 3, max 20

bash CLI
  # Create a session
  SESSION_ID=$(ant beta:sessions create \
    --agent "$AGENT_ID" \
    --environment-id "$ENVIRONMENT_ID" \
    --title "Financial analysis on Costco" \
    --transform id --raw-output)

  # Define the outcome — agent starts working on receipt
  ant beta:sessions:events send --session-id "$SESSION_ID" <<YAML
  events:
    - type: user.define_outcome
      description: Build a DCF model for Costco in .xlsx
      rubric: {type: file, file_id: $RUBRIC_ID}
      # or: rubric: {type: text, content: "..."}
      max_iterations: 5  # optional; default 3, max 20
  YAML

python Python
  # Create a session
  session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
      title="Financial analysis on Costco",
  )

  # Define the outcome — agent starts working on receipt
  client.beta.sessions.events.send(
      session_id=session.id,
      events=[
          {
              "type": "user.define_outcome",
              "description": "Build a DCF model for Costco in .xlsx",
              "rubric": {"type": "text", "content": RUBRIC},
              # or: "rubric": {"type": "file", "file_id": rubric.id},
              "max_iterations": 5,  # optional; default 3, max 20
          }
      ],
  )

typescript TypeScript
  // Create a session
  const session = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id,
    title: "Financial analysis on Costco",
  });

  // Define the outcome — agent starts working on receipt
  await client.beta.sessions.events.send(session.id, {
    events: [
      {
        type: "user.define_outcome",
        description: "Build a DCF model for Costco in .xlsx",
        rubric: { type: "text", content: RUBRIC },
        // or: rubric: { type: "file", file_id: rubric.id },
        max_iterations: 5, // optional; default 3, max 20
      },
    ],
  });

csharp C#
  // Create a session
  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = agent.ID,
      EnvironmentID = environment.ID,
      Title = "Financial analysis on Costco",
  });

  // Define the outcome — agent starts working on receipt
  await client.Beta.Sessions.Events.Send(session.ID, new()
  {
      Events =
      [
          new BetaManagedAgentsUserDefineOutcomeEventParams
          {
              Type = BetaManagedAgentsUserDefineOutcomeEventParamsType.UserDefineOutcome,
              Description = "Build a DCF model for Costco in .xlsx",
              Rubric = new BetaManagedAgentsTextRubricParams
              {
                  Type = BetaManagedAgentsTextRubricParamsType.Text,
                  Content = Rubric,
              },
              // or: Rubric = new BetaManagedAgentsFileRubricParams
              //     { Type = BetaManagedAgentsFileRubricParamsType.File, FileID = rubric.ID },
              MaxIterations = 5, // optional; default 3, max 20
          },
      ],
  });

go Go
  // Create a session
  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfString: anthropic.String(agent.ID),
  	},
  	EnvironmentID: environment.ID,
  	Title:         anthropic.String("Financial analysis on Costco"),
  })
  if err != nil {
  	panic(err)
  }

  // Define the outcome — agent starts working on receipt
  _, err = client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  	Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  		OfUserDefineOutcome: &anthropic.BetaManagedAgentsUserDefineOutcomeEventParams{
  			Type:        anthropic.BetaManagedAgentsUserDefineOutcomeEventParamsTypeUserDefineOutcome,
  			Description: "Build a DCF model for Costco in .xlsx",
  			Rubric: anthropic.BetaManagedAgentsUserDefineOutcomeEventParamsRubricUnion{
  				OfText: &anthropic.BetaManagedAgentsTextRubricParams{
  					Type:    anthropic.BetaManagedAgentsTextRubricParamsTypeText,
  					Content: rubric,
  				},
  			},
  			// or: OfFile: &anthropic.BetaManagedAgentsFileRubricParams{
  			//     Type: anthropic.BetaManagedAgentsFileRubricParamsTypeFile, FileID: uploaded.ID},
  			MaxIterations: anthropic.Int(5), // optional; default 3, max 20
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }

java Java
  // Create a session
  var session = client.beta().sessions().create(
      SessionCreateParams.builder()
          .agent(agent.id())
          .environmentId(environment.id())
          .title("Financial analysis on Costco")
          .build());

  // Define the outcome — agent starts working on receipt
  client.beta().sessions().events().send(
      session.id(),
      EventSendParams.builder()
          .addEvent(BetaManagedAgentsUserDefineOutcomeEventParams.builder()
              .type(BetaManagedAgentsUserDefineOutcomeEventParams.Type.USER_DEFINE_OUTCOME)
              .description("Build a DCF model for Costco in .xlsx")
              .rubric(BetaManagedAgentsTextRubricParams.builder()
                  .type(BetaManagedAgentsTextRubricParams.Type.TEXT)
                  .content(RUBRIC)
                  .build())
              // or: .rubric(BetaManagedAgentsFileRubricParams.builder()
              //     .type(BetaManagedAgentsFileRubricParams.Type.FILE).fileId(rubric.id()).build())
              .maxIterations(5) // optional; default 3, max 20
              .build())
          .build());

php PHP
  // Create a session
  $session = $client->beta->sessions->create(
      agent: $agent->id,
      environmentID: $environment->id,
      title: 'Financial analysis on Costco',
  );

  // Define the outcome — agent starts working on receipt
  $client->beta->sessions->events->send(
      $session->id,
      events: [
          [
              'type' => 'user.define_outcome',
              'description' => 'Build a DCF model for Costco in .xlsx',
              'rubric' => ['type' => 'text', 'content' => $rubricText],
              // or: 'rubric' => ['type' => 'file', 'file_id' => $rubric->id],
              'max_iterations' => 5, // optional; default 3, max 20
          ],
      ],
  );

ruby Ruby
  # Create a session
  session = client.beta.sessions.create(
    agent: agent.id,
    environment_id: environment.id,
    title: "Financial analysis on Costco"
  )

  # Define the outcome — agent starts working on receipt
  client.beta.sessions.events.send_(
    session.id,
    events: [
      {
        type: "user.define_outcome",
        description: "Build a DCF model for Costco in .xlsx",
        rubric: {type: "text", content: RUBRIC},
        # or: rubric: {type: "file", file_id: rubric.id},
        max_iterations: 5 # optional; default 3, max 20
      }
    ]
  )
  ```
</CodeGroup>

<Note>
  You can also define the outcome in the create request itself: pass a single `user.define_outcome` event in [`initial_events`](https://platform.claude.com/docs/en/managed-agents/sessions#seed-the-session-with-initial-events) to create the session and start work toward the outcome in one call.
</Note>


## Outcome events

Source: https://platform.claude.com/llms-full.txt#outcome-events

Progress on an outcome-oriented session is surfaced on the events [stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming).

* `agent.*` events (such as messages and tool use) show progress toward the outcome.
* `span.outcome_evaluation_*` events are only emitted for outcome-oriented sessions and show the number of iteration loops and the grader's feedback process.
* You can also send `user.message` [events](https://platform.claude.com/docs/en/managed-agents/reference#event-types) to an outcome-oriented session to direct the agent's work as it progresses, but it isn't required: the agent works toward the outcome on its own, iterating until it succeeds or runs out of iterations.
* A `user.interrupt` event pauses work on the current outcome and marks the `span.outcome_evaluation_end.result` as `interrupted`, allowing you to kick off a new outcome.
* After the final outcome evaluation, the session can be continued as a conversational session, or a new outcome can be started. The session retains history of the prior outcome.

### Define outcome user event

<Note>
  Only one outcome is supported at a time, but you may chain outcomes in sequence. To do this, send a new `user.define_outcome` event after the terminal `span.outcome_evaluation_end` event of the previous outcome.
</Note>

This is the event you send to initiate an outcome. It is echoed back on receipt, including a `processed_at` timestamp and `outcome_id`.

### Outcome evaluation start

Emitted once the grader starts an evaluation over one iteration loop. The `iteration` field is a 0-indexed revision counter: `0` is the first evaluation, `1` is the re-evaluation after the first revision, and so on.

### Outcome evaluation ongoing

Heartbeat emitted while the grader runs. The grader's internal reasoning is opaque: you see that it's working, not what it's thinking.

### Outcome evaluation end

Emitted when an outcome evaluation cycle ends: after the grader finishes evaluating one iteration, or when the session is interrupted while an outcome is active. The `result` field indicates what happens next.

| Result                   | Next                                                                                                                                                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `satisfied`              | Session transitions to `idle`.                                                                                                                                                                                            |
| `needs_revision`         | Agent starts a new iteration cycle.                                                                                                                                                                                       |
| `max_iterations_reached` | One final acknowledgment turn follows before the session transitions to `idle`. No further evaluation runs.                                                                                                               |
| `failed`                 | Session transitions to `idle`. Returned when the rubric does not apply to the deliverables, for example if the description and rubric contradict each other.                                                              |
| `interrupted`            | Emitted when the session is interrupted while an outcome is active, even if evaluation hadn't started yet. If no `outcome_evaluation_start` fired before the interrupt, `outcome_evaluation_start_id` is an empty string. |


## Check outcome status

Source: https://platform.claude.com/llms-full.txt#check-outcome-status

You can either listen on the [event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming) for `span.outcome_evaluation_end`, or poll `GET /v1/sessions/{session_id}` and read `outcome_evaluations[].result`. Until an evaluation completes, `result` reports `pending`, `running`, or `evaluating`:

<CodeGroup>
  ```bash cURL
  session=$(curl -fsSL "https://api.anthropic.com/v1/sessions/$session_id" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01")

  jq -r '.outcome_evaluations[] | "\(.outcome_id): \(.result)"' <<<"$session"
  # outc_01a...: satisfied

bash CLI
  ant beta:sessions retrieve --session-id "$SESSION_ID" \
    --transform 'outcome_evaluations' --format yaml

python Python
  session = client.beta.sessions.retrieve(session.id)

  for outcome in session.outcome_evaluations:
      print(f"{outcome.outcome_id}: {outcome.result}")
      # outc_01a...: satisfied

typescript TypeScript
  const retrieved = await client.beta.sessions.retrieve(session.id);

  for (const outcome of retrieved.outcome_evaluations) {
    console.log(`${outcome.outcome_id}: ${outcome.result}`);
    // outc_01a...: satisfied
  }

csharp C#
  session = await client.Beta.Sessions.Retrieve(session.ID);

  foreach (var outcome in session.OutcomeEvaluations)
  {
      Console.WriteLine($"{outcome.OutcomeID}: {outcome.Result}");
      // outc_01a...: satisfied
  }

go Go
  session, err = client.Beta.Sessions.Get(ctx, session.ID, anthropic.BetaSessionGetParams{})
  if err != nil {
  	panic(err)
  }

  for _, outcome := range session.OutcomeEvaluations {
  	fmt.Printf("%s: %s\n", outcome.OutcomeID, outcome.Result)
  	// outc_01a...: satisfied
  }

java Java
  var retrieved = client.beta().sessions().retrieve(session.id());

  for (var outcome : retrieved.outcomeEvaluations()) {
      IO.println(outcome.outcomeId() + ": " + outcome.result());
      // outc_01a...: satisfied
  }

php PHP
  $session = $client->beta->sessions->retrieve($session->id);

  foreach ($session->outcomeEvaluations as $outcome) {
      echo "{$outcome->outcomeID}: {$outcome->result}\n";
      // outc_01a...: satisfied
  }

ruby Ruby
  session = client.beta.sessions.retrieve(session.id)

  session.outcome_evaluations.each do
    puts "#{it.outcome_id}: #{it.result}"
    # outc_01a...: satisfied
  end
  ```
</CodeGroup>


## Retrieve deliverables

Source: https://platform.claude.com/llms-full.txt#retrieve-deliverables

The agent writes output files to `/mnt/session/outputs/` inside the sandbox. To retrieve them, list files through the [Files API](https://platform.claude.com/docs/en/build-with-claude/files) with the session ID as the `scope_id`, then download them by ID. Filtering by `scope_id` requires the `managed-agents-2026-04-01` beta header on the list request, so the SDK and CLI examples make that call through the `beta` namespace and pass the header explicitly. Files appear in the list shortly after the agent finishes writing them, sometimes a few seconds after the session goes idle. If a file you expect is not listed yet, list again after a short delay; once it appears in the list, its upload has finished.

<CodeGroup>
  ```bash cURL
  # List files produced by this session
  # scope_id filtering requires the managed-agents beta
  files=$(curl -fsSL "https://api.anthropic.com/v1/files?scope_id=$session_id" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01")
  jq -r '.data[] | "\(.id) \(.filename)"' <<<"$files"

  # Download a file
  file_id=$(jq -r '.data[0].id // empty' <<<"$files")
  if [[ -n $file_id ]]; then
    curl -fsSL "https://api.anthropic.com/v1/files/$file_id/content" \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "anthropic-beta: managed-agents-2026-04-01" \
      -o /tmp/output.txt
  fi

bash CLI
  # List files produced by this session
  # scope_id filtering requires the managed-agents beta on the files request
  ant beta:files list --scope-id "$SESSION_ID" --beta managed-agents-2026-04-01

  # Download a file
  FILE_ID=$(ant beta:files list --scope-id "$SESSION_ID" \
    --beta managed-agents-2026-04-01 \
    --transform 'data[0].id' --raw-output)
  if [[ -n $FILE_ID ]]; then
    ant files download --file-id "$FILE_ID" --output /tmp/output.txt
  fi

python Python
  # List files produced by this session
  # scope_id filtering requires the managed-agents beta on the files request
  files = client.beta.files.list(scope_id=session.id, betas=["managed-agents-2026-04-01"])
  for file in files:
      print(file.id, file.filename)

  # Download a file
  if files.data:
      content = client.files.download(files.data[0].id)
      content.write_to_file("/tmp/output.txt")

typescript TypeScript
  // List files produced by this session
  // scope_id filtering requires the managed-agents beta on the files request
  const files = await client.beta.files.list({
    scope_id: session.id,
    betas: ["managed-agents-2026-04-01"],
  });
  for (const file of files.data) {
    console.log(file.id, file.filename);
  }

  // Download a file
  if (files.data.length > 0) {
    const content = await client.files.download(files.data[0].id);
    await writeFile("/tmp/output.txt", new Uint8Array(await content.arrayBuffer()));
  }

csharp C#
  // List files produced by this session
  // (scope_id filtering requires the managed-agents beta on the files request)
  var files = await client.Beta.Files.List(new()
  {
      ScopeID = session.ID,
      Betas = ["managed-agents-2026-04-01"],
  });
  foreach (var file in files.Items)
  {
      Console.WriteLine($"{file.ID} {file.Filename}");
  }

  // Download a file
  if (files.Items.Count > 0)
  {
      using var download = await client.Files.Download(files.Items[0].ID);
      await using var output = File.Create("/tmp/output.txt");
      await (await download.ReadAsStream()).CopyToAsync(output);
  }

go Go
  // List files produced by this session
  // (scope_id filtering requires the managed-agents beta on the files request)
  files, err := client.Beta.Files.List(ctx, anthropic.BetaFileListParams{
  	ScopeID: anthropic.String(session.ID),
  	Betas:   []anthropic.AnthropicBeta{anthropic.AnthropicBetaManagedAgents2026_04_01},
  })
  if err != nil {
  	panic(err)
  }
  for _, file := range files.Data {
  	fmt.Println(file.ID, file.Filename)
  }

  // Download a file
  if len(files.Data) > 0 {
  	resp, err := client.Files.Download(ctx, files.Data[0].ID)
  	if err != nil {
  		panic(err)
  	}
  	defer resp.Body.Close()
  	out, err := os.Create("/tmp/output.txt")
  	if err != nil {
  		panic(err)
  	}
  	defer out.Close()
  	if _, err := io.Copy(out, resp.Body); err != nil {
  		panic(err)
  	}
  }

java Java
  // List files produced by this session
  // (scope_id filtering requires the managed-agents beta on the files request)
  var files = client.beta().files().list(
      FileListParams.builder()
          .scopeId(session.id())
          .addBeta(AnthropicBeta.MANAGED_AGENTS_2026_04_01)
          .build());
  for (var file : files.data()) {
      IO.println(file.id() + " " + file.filename());
  }

  // Download a file
  if (!files.data().isEmpty()) {
      try (HttpResponse response = client.files().download(files.data().getFirst().id())) {
          try (InputStream body = response.body()) {
              Files.copy(body, Path.of("/tmp/output.txt"), StandardCopyOption.REPLACE_EXISTING);
          }
      }
  }

php PHP
  // List files produced by this session
  // scope_id filtering requires the managed-agents beta on the files request
  $files = $client->beta->files->list(scopeID: $session->id, betas: ['managed-agents-2026-04-01']);
  foreach ($files->getItems() as $file) {
      echo "{$file->id} {$file->filename}\n";
  }

  // Download a file
  if (count($files->getItems()) > 0) {
      $content = $client->files->download($files->getItems()[0]->id);
      file_put_contents('/tmp/output.txt', $content);
  }

ruby Ruby
  # List files produced by this session
  # scope_id filtering requires the managed-agents beta on the files request
  files = client.beta.files.list(scope_id: session.id, betas: ["managed-agents-2026-04-01"])
  files.data.each { |file| puts "#{file.id} #{file.filename}" }

  # Download a file
  if (first = files.data.first)
    content = client.files.download(first.id)
    File.binwrite("/tmp/output.txt", content.read)
  end
  ```
</CodeGroup>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-76

<CardGroup cols={3}>
  <Card title="Authenticate with vaults" icon="fingerprint" href="https://platform.claude.com/docs/en/managed-agents/vaults">
    Register per-user credentials when creating sessions.
  </Card>

  <Card title="Session event stream" icon="lightning" href="https://platform.claude.com/docs/en/managed-agents/events-and-streaming">
    Send events, stream responses, and interrupt or redirect your session mid-execution.
  </Card>

  <Card title="Adding files" icon="file" href="https://platform.claude.com/docs/en/managed-agents/files">
    Upload files and mount them in your sandbox for reading and processing.
  </Card>
</CardGroup>


---
title: Session budgets
url: https://platform.claude.com/docs/en/managed-agents/budgets
description: Cap a session's spend with a hard dollar budget enforced at public list rates.
---

A session budget is an optional hard spend ceiling you set when you [create a session](https://platform.claude.com/docs/en/managed-agents/sessions). The platform continuously prices everything the session consumes at public list rates (the session's **list cost**) and stops issuing new model requests once that cost reaches the budget. The request in flight when the cap is crossed still finishes, so the final list cost can land [a fraction past the budget](https://platform.claude.com/docs/en/managed-agents/budgets#when-a-session-reaches-its-budget). A session at its budget pauses and goes [idle](https://platform.claude.com/docs/en/managed-agents/session-operations#session-statuses) rather than terminating; changing or removing the budget resumes its work automatically. Deployments accept the same budget and apply it to each session they start; see [Budgets on deployments](https://platform.claude.com/docs/en/managed-agents/budgets#budgets-on-deployments).

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Set a budget at session creation

Source: https://platform.claude.com/llms-full.txt#set-a-budget-at-session-creation

Pass the optional `budget` field when you create the session:

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  session=$(curl -sS --fail-with-body https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "agent": "$AGENT_ID",
    "environment_id": "$ENVIRONMENT_ID",
    "budget": {
      "type": "limit",
      "max_list_cost": {"amount": "125", "currency": "USD"}
    }
  }
  EOF
  )
  SESSION_ID=$(jq -r '.id' <<< "$session")

bash CLI
  # Keep the amount quoted so it is sent as a string, not a number.
  SESSION_ID=$(ant beta:sessions create \
    --agent "$AGENT_ID" \
    --environment-id "$ENVIRONMENT_ID" \
    --budget '{type: limit, max_list_cost: {amount: "125", currency: USD}}' \
    --transform id --raw-output)

python Python
  session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
      budget={
          "type": "limit",
          "max_list_cost": {"amount": "125", "currency": "USD"},
      },
  )
  print(session.id, session.budget.max_list_cost.amount)  # sesn_01... 125

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id,
    budget: {
      type: "limit",
      max_list_cost: { amount: "125", currency: "USD" }
    }
  });
  console.log(session.id, session.budget?.max_list_cost.amount); // sesn_01... 125

csharp C#
  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = agent.ID,
      EnvironmentID = environment.ID,
      Budget = new()
      {
          Type = BetaManagedAgentsBudgetLimitType.Limit,
          MaxListCost = new() { Amount = "125", Currency = BetaCurrency.Usd },
      },
  });
  Console.WriteLine($"{session.ID} {session.Budget?.MaxListCost.Amount}");  // sesn_01... 125

go Go
  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfString: anthropic.String(agent.ID),
  	},
  	EnvironmentID: environment.ID,
  	Budget: anthropic.BetaManagedAgentsBudgetLimitParam{
  		Type: anthropic.BetaManagedAgentsBudgetLimitTypeLimit,
  		MaxListCost: anthropic.BetaMonetaryAmountParam{
  			Amount:   "125",
  			Currency: anthropic.BetaCurrencyUsd,
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }
  fmt.Println(session.ID, session.Budget.MaxListCost.Amount) // sesn_01... 125

java Java
  var session = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(agent.id())
      .environmentId(environment.id())
      .budget(BetaManagedAgentsBudgetLimit.builder()
          .type(BetaManagedAgentsBudgetLimit.Type.LIMIT)
          .maxListCost(BetaMonetaryAmount.builder()
              .amount("125")
              .currency(BetaCurrency.USD)
              .build())
          .build())
      .build());
  IO.println(session.id() + " " + session.budget().orElseThrow().maxListCost().amount());  // sesn_01... 125

php PHP
  $session = $client->beta->sessions->create(
      agent: $agent->id,
      environmentID: $environment->id,
      budget: [
          'type' => 'limit',
          'max_list_cost' => ['amount' => '125', 'currency' => 'USD'],
      ],
  );
  echo "{$session->id} {$session->budget->maxListCost->amount}\n"; // sesn_01... 125

ruby Ruby
  session = client.beta.sessions.create(
    agent: agent.id,
    environment_id: environment.id,
    budget: {
      type: "limit",
      max_list_cost: {amount: "125", currency: "USD"}
    }
  )
  puts "#{session.id} #{session.budget.max_list_cost.amount}" # sesn_01... 125
  ```
</CodeGroup>

The `budget` object has two fields:

* `type` is always `"limit"`.
* `max_list_cost` is the cap itself: `amount` is a whole number of US cents written as a string with no leading zeros (`"125"` is $1.25 and `"50"` is 50 cents) and must be greater than zero. Decimal forms such as `"25.00"` are rejected. The amount is a string rather than a number so no float rounding is ever applied to it. `currency` is an uppercase ISO-4217 currency code; `USD` is the only supported currency.

A budget can only be attached when the session is created. Adding a budget to an existing session that doesn't have one is rejected with a 400 error. A budgeted session's cap can be [changed](https://platform.claude.com/docs/en/managed-agents/budgets#change-the-budget) or [removed](https://platform.claude.com/docs/en/managed-agents/budgets#remove-the-budget) at any time.


## How list cost is measured

Source: https://platform.claude.com/llms-full.txt#how-list-cost-is-measured

The platform prices what the session consumes, continuously, at public list rates:

* **Model tokens**, at each served model's list price
* **Web searches**, at $10 per 1,000 searches
* **Session running time**, at $0.08 per hour

This running dollar total is the session's **list cost**, and it is what the budget compares against. List cost is not your contracted price: if your organization has negotiated discounts, the session reaches its cap when the list-price total does, and your billed spend might be lower than the cap.

Enforcement uses the exact, unrounded list cost. The `list_cost` figures reported on the session and its events are whole cents, rounded to the nearest cent, so a reported figure can read up to half a cent either side of the exact amount enforcement uses.


## When a session reaches its budget

Source: https://platform.claude.com/llms-full.txt#when-a-session-reaches-its-budget

The cap is enforced between model requests, not mid-request. Before each model request, the platform checks the session's consumed list cost, and once that total reaches the cap every thread pauses before its next request. The request that carried the total past the cap was admitted while the session was still under it and runs to completion, so a paused session's recorded `list_cost` reads at or a fraction past `max_list_cost`: a session capped at `"50"` (50 cents) can pause with a `list_cost` of `"53"`. This is expected, not a billing error, and the overshoot is bounded by one model request per thread. Treat the budget as a bound on new work rather than an exact stopping point, and size the cap with that one-request margin in mind.

A session that reaches its budget goes idle with a `stop_reason` of `budget_reached`; it is not terminated, and its history and sandbox are preserved like any other idle session's. On the [event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming) you'll see, in order:

1. A `session.thread_status_idle` event with a `stop_reason` of `budget_reached` as each thread pauses.
2. A [`session.usage`](https://platform.claude.com/docs/en/managed-agents/budgets#monitor-spend) event with the session's cumulative usage and list cost.
3. A `session.status_idle` event with a `stop_reason` of `budget_reached`. The usage event always immediately precedes this idle event.

A thread whose final request both crosses the cap and completes its turn reports `end_turn` on its own `session.thread_status_idle` event while the session still reports `budget_reached`; treat the session-level `stop_reason` as the signal that the session paused at its budget.

### Events accepted at the cap

While the session is at or over its budget, it accepts only events that settle work already in progress:

* `user.tool_confirmation`
* `user.tool_result`
* `user.custom_tool_result`
* `user.interrupt`

Any event that would start new work, such as `user.message`, is rejected with a 400 error naming this list. Settled results are recorded without triggering a new model request; the session stays paused at its budget.

A `user.interrupt` sent while the session is paused at its budget (all threads paused at the cap) is accepted and ignored: it does not appear in the event list and changes nothing. Change or remove the budget to continue.
