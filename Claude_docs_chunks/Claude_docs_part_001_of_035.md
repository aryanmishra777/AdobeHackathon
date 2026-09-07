# platform.claude.com Documentation (Part 1 of 35)

## Anthropic Developer Documentation - Full Content

Source: https://platform.claude.com/llms-full.txt#anthropic-developer-documentation-full-content

This file provides comprehensive documentation with full rendered content.


## Root URL

Source: https://platform.claude.com/llms-full.txt#root-url

Claude Developer Platform Console (Requires login)

https://platform.claude.com


## Available Languages on Website

Source: https://platform.claude.com/llms-full.txt#available-languages-on-website

The full documentation is available in the following languages on https://platform.claude.com/docs:

- English (en) - 699 pages - ✓ Full content included below
- German (Deutsch) (de) - 249 pages - Visit website for content
- Spanish (Español) (es) - 249 pages - Visit website for content
- French (Français) (fr) - 249 pages - Visit website for content
- Italian (Italiano) (it) - 249 pages - Visit website for content
- Japanese (日本語) (ja) - 249 pages - Visit website for content
- Korean (한국어) (ko) - 249 pages - Visit website for content
- Portuguese (Português) (pt-BR) - 249 pages - Visit website for content
- Russian (Русский) (ru) - 249 pages - Visit website for content
- Chinese Simplified (简体中文) (zh-CN) - 249 pages - Visit website for content
- Chinese Traditional (繁體中文) (zh-TW) - 249 pages - Visit website for content
- Indonesian (Bahasa Indonesia) (id) - 249 pages - Visit website for content

---

# English Documentation - Full Content


## Docs home

Source: https://platform.claude.com/llms-full.txt#docs-home

---
title: Documentation
url: https://platform.claude.com/docs/en/home
description: Claude API Documentation
---

<HomePage>
  <HomeHero
    eyebrow="Claude Platform"
    title="Start building
with Claude"
    subtitle="Everything you need to integrate Claude into your applications. From first API call to production."
  >
    <HomeQuickChip icon="Play" href="https://platform.claude.com/docs/en/get-started">
      Quickstart
    </HomeQuickChip>

    <HomeQuickChip icon="Key" href="https://platform.claude.com/settings/keys">
      Get API key
    </HomeQuickChip>

    <HomeQuickChip icon="CodeBrackets" href="https://platform.claude.com/docs/en/api/overview">
      API reference
    </HomeQuickChip>
  </HomeHero>

  <HomeSection>
    <HomeSectionHeader label="Platform" title="Choose how you build" description="Pick the developer surface that matches your approach, and the infrastructure that fits your stack." />

    <HomePlatformCards>
      <HomePlatformCard title="Messages" description="Direct model access. You construct every turn, manage conversation state, and write your own tool loop." pictogram="code-terminal">
        <HomeCardLink icon="play" href="https://platform.claude.com/docs/en/get-started">
          Quickstart
        </HomeCardLink>

        <HomeCardLink icon="book" href="https://platform.claude.com/docs/en/api/messages/create">
          API reference
        </HomeCardLink>

        <HomeCardLink icon="code-brackets" href="https://platform.claude.com/docs/en/cli-sdks-libraries/overview">
          Client SDKs
        </HomeCardLink>
      </HomePlatformCard>

      <HomePlatformCard title="Managed Agents" description="Fully managed agent infrastructure. Deploy and manage autonomous agents in stateful sessions with persistent event history." pictogram="clouds">
        <HomeCardLink icon="play" href="https://platform.claude.com/docs/en/managed-agents/quickstart">
          Quickstart
        </HomeCardLink>

        <HomeCardLink icon="book" href="https://platform.claude.com/docs/en/api/beta/sessions">
          API reference
        </HomeCardLink>

        <HomeCardLink icon="brain" href="https://platform.claude.com/docs/en/managed-agents/agent-setup">
          Define your agent
        </HomeCardLink>
      </HomePlatformCard>
    </HomePlatformCards>

    <HomePartnerLinks label="Claude is also available on these cloud platforms:">
      <HomeCloudPartnerLink icon="cloud" href="https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock">
        Amazon Bedrock
      </HomeCloudPartnerLink>

      <HomeCloudPartnerLink icon="cloud" href="https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai">
        Google Cloud
      </HomeCloudPartnerLink>

      <HomeCloudPartnerLink icon="cloud" href="https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry">
        Microsoft Foundry
      </HomeCloudPartnerLink>
    </HomePartnerLinks>
  </HomeSection>

  <HomeSection>
    <HomeSectionHeader label="Developer journey" title="From idea to production" description="Follow the lifecycle or jump to what you need." />

    <HomeJourney>
      <HomeJourneyTab label="Messages">
        <HomeJourneyStep title="Get started">
          <HomeJourneyLink icon="play" href="https://platform.claude.com/docs/en/get-started">
            Quickstart
          </HomeJourneyLink>

          <HomeJourneyLink icon="lock" href="https://platform.claude.com/settings/keys">
            Get API key
          </HomeJourneyLink>

          <HomeJourneyLink icon="settings" href="https://platform.claude.com/docs/en/models/overview">
            Choose a model
          </HomeJourneyLink>

          <HomeJourneyLink icon="code-brackets" href="https://platform.claude.com/docs/en/cli-sdks-libraries/overview">
            Install an SDK
          </HomeJourneyLink>

          <HomeJourneyLink icon="message" href="https://platform.claude.com/playground">
            Try the API in playground
          </HomeJourneyLink>
        </HomeJourneyStep>

        <HomeJourneyStep title="Build">
          <HomeJourneyLink icon="message" href="https://platform.claude.com/docs/en/api/messages/create">
            Messages API
          </HomeJourneyLink>

          <HomeJourneyLink icon="brain" href="https://platform.claude.com/docs/en/build-with-claude/thinking">
            Thinking
          </HomeJourneyLink>

          <HomeJourneyLink icon="image" href="https://platform.claude.com/docs/en/build-with-claude/vision">
            Vision
          </HomeJourneyLink>

          <HomeJourneyLink icon="tool" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview">
            Tool use
          </HomeJourneyLink>

          <HomeJourneyLink icon="compass" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool">
            Web search
          </HomeJourneyLink>

          <HomeJourneyLink icon="code" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool">
            Code execution
          </HomeJourneyLink>

          <HomeJourneyLink icon="database" href="https://platform.claude.com/docs/en/build-with-claude/structured-outputs">
            Structured outputs
          </HomeJourneyLink>

          <HomeJourneyLink icon="lightning" href="https://platform.claude.com/docs/en/build-with-claude/prompt-caching">
            Prompt caching
          </HomeJourneyLink>

          <HomeJourneyLink icon="wifi-high" href="https://platform.claude.com/docs/en/build-with-claude/streaming">
            Streaming
          </HomeJourneyLink>
        </HomeJourneyStep>

        <HomeJourneyStep title="Evaluate and ship">
          <HomeJourneyLink icon="lightbulb" href="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview">
            Prompting best practices
          </HomeJourneyLink>

          <HomeJourneyLink icon="chart" href="https://platform.claude.com/docs/en/test-and-evaluate/develop-tests">
            Run evals
          </HomeJourneyLink>

          <HomeJourneyLink icon="stack" href="https://platform.claude.com/docs/en/build-with-claude/batch-processing">
            Batch testing
          </HomeJourneyLink>

          <HomeJourneyLink icon="verified" href="https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency">
            Safety and guardrails
          </HomeJourneyLink>

          <HomeJourneyLink icon="bolt" href="https://platform.claude.com/docs/en/api/rate-limits">
            Rate limits and errors
          </HomeJourneyLink>

          <HomeJourneyLink icon="calculator" href="https://platform.claude.com/docs/en/about-claude/pricing">
            Cost optimization
          </HomeJourneyLink>
        </HomeJourneyStep>

        <HomeJourneyStep title="Operate">
          <HomeJourneyLink icon="settings" href="https://platform.claude.com/docs/en/build-with-claude/workspaces">
            Workspaces and admin
          </HomeJourneyLink>

          <HomeJourneyLink icon="lock" href="https://platform.claude.com/settings/keys">
            API key management
          </HomeJourneyLink>

          <HomeJourneyLink icon="chart" href="https://platform.claude.com/docs/en/build-with-claude/usage-cost-api">
            Usage monitoring
          </HomeJourneyLink>

          <HomeJourneyLink icon="settings" href="https://platform.claude.com/docs/en/about-claude/models/migration-guide">
            Model migration
          </HomeJourneyLink>
        </HomeJourneyStep>
      </HomeJourneyTab>

      <HomeJourneyTab label="Managed Agents">
        <HomeJourneyStep title="Get started">
          <HomeJourneyLink icon="play" href="https://platform.claude.com/docs/en/managed-agents/quickstart">
            Quickstart
          </HomeJourneyLink>

          <HomeJourneyLink icon="lock" href="https://platform.claude.com/settings/keys">
            Get API key
          </HomeJourneyLink>

          <HomeJourneyLink icon="message" href="https://platform.claude.com/docs/en/managed-agents/onboarding">
            Build in Console
          </HomeJourneyLink>
        </HomeJourneyStep>

        <HomeJourneyStep title="Define your agent">
          <HomeJourneyLink icon="brain" href="https://platform.claude.com/docs/en/managed-agents/agent-setup">
            Agent setup
          </HomeJourneyLink>

          <HomeJourneyLink icon="tool" href="https://platform.claude.com/docs/en/managed-agents/tools">
            Tools
          </HomeJourneyLink>

          <HomeJourneyLink icon="lock" href="https://platform.claude.com/docs/en/managed-agents/permission-policies">
            Tool permissions
          </HomeJourneyLink>
        </HomeJourneyStep>

        <HomeJourneyStep title="Run sessions">
          <HomeJourneyLink icon="wifi-high" href="https://platform.claude.com/docs/en/managed-agents/events-and-streaming">
            Streaming and events
          </HomeJourneyLink>

          <HomeJourneyLink icon="code-brackets" href="https://platform.claude.com/docs/en/api/beta/sessions">
            Sessions API reference
          </HomeJourneyLink>
        </HomeJourneyStep>

        <HomeJourneyStep title="Operate">
          <HomeJourneyLink icon="settings" href="https://platform.claude.com/docs/en/build-with-claude/workspaces">
            Workspaces and admin
          </HomeJourneyLink>

          <HomeJourneyLink icon="lock" href="https://platform.claude.com/settings/keys">
            API key management
          </HomeJourneyLink>

          <HomeJourneyLink icon="chart" href="https://platform.claude.com/docs/en/build-with-claude/usage-cost-api">
            Usage monitoring
          </HomeJourneyLink>
        </HomeJourneyStep>
      </HomeJourneyTab>
    </HomeJourney>
  </HomeSection>

  <HomeSection>
    <HomeSectionHeader label="Models" title="The Claude model family" description="Choose the right model for your use case." />

    * [Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/overview) (`claude-fable-5-1`) — New — *For demanding reasoning and long-horizon agentic work* — Most capable · Research · Multi-day tasks
    * [Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/overview) (`claude-opus-5`) — *For complex agentic coding and enterprise work* — Complex projects · Agents · Coding
    * [Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/overview) (`claude-sonnet-5`) — *The best combination of speed and intelligence* — Everyday tasks · Writing · Cost-efficient
    * [Claude Haiku 4.5](https://platform.claude.com/docs/en/models/haiku-4-5/overview) (`claude-haiku-4-5`) — *The fastest model with near-frontier intelligence* — Fastest · Lowest cost · High volume
  </HomeSection>

  <HomeSection last>
    <HomeSectionHeader label="Resources" title="Keep learning" />

    <CardGroup cols={3}>
      <Card icon="graduation-cap" title="Courses" href="https://academy.claude.com/courses">
        Interactive courses to master Claude.
      </Card>

      <Card icon="book" title="Cookbook" href="https://platform.claude.com/cookbook">
        Code samples and patterns.
      </Card>

      <Card icon="play" title="Quickstarts" href="https://github.com/anthropics/anthropic-quickstarts">
        Deployable starter apps.
      </Card>

      <Card icon="star" title="What's new" href="https://platform.claude.com/docs/en/release-notes/overview">
        Latest features and updates.
      </Card>

      <Card icon="terminal" title="Claude Code" href="https://code.claude.com/docs">
        An agentic coding assistant in your terminal.
      </Card>
    </CardGroup>
  </HomeSection>
</HomePage>


## Messages

Source: https://platform.claude.com/llms-full.txt#messages

### First steps

---
title: Get started with Claude
url: https://platform.claude.com/docs/en/get-started
description: Make your first API call to Claude and build a simple web search assistant.
---


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites

* A [Claude Console account](https://platform.claude.com)
* An [API key](https://platform.claude.com/settings/keys)


## Call the API

Source: https://platform.claude.com/llms-full.txt#call-the-api

<Tabs>
  <Tab title="cURL">
    <Steps>
      <Step title="Set your API key">
        Export your API key as an environment variable. The cURL command below reads it from `$ANTHROPIC_API_KEY`.

</Step>

      <Step title="Make your first API call">
        Send a `POST` request to the Messages API:

        ```bash cURL
        curl https://api.anthropic.com/v1/messages \
          -H "content-type: application/json" \
          -H "x-api-key: $ANTHROPIC_API_KEY" \
          -H "anthropic-version: 2023-06-01" \
          -d '{
            "model": "claude-opus-5",
            "max_tokens": 1000,
            "messages": [
              {
                "role": "user",
                "content": "What should I search for to find the latest developments in renewable energy?"
              }
            ]
          }'

json Output
        {
          "model": "claude-opus-5",
          "id": "msg_013mHbppMPd2PrVJzGMZPt2D",
          "type": "message",
          "role": "assistant",
          "content": [
            {
              "type": "text",
              "text": "Here are some effective search strategies to find the latest developments in renewable energy:\n\n## General Search Terms\n- \"Renewable energy news 2025\"\n- ..."
            }
          ],
          "stop_reason": "end_turn",
          "stop_sequence": null,
          "stop_details": null,
          "usage": {
            "input_tokens": 21,
            "output_tokens": 305
          }
        }

bash
        brew install anthropics/tap/ant

bash
        ant auth login

bash
        ant auth status

bash CLI
        ant messages create \
          --model claude-opus-5 \
          --max-tokens 1000 \
          --message '{
            role: user,
            content: "What should I search for to find the latest developments in renewable energy?"
          }'

json Output
        {
          "model": "claude-opus-5",
          "id": "msg_01N1ycuCkM5Mzd7WhTU4fwST",
          "type": "message",
          "role": "assistant",
          "content": [
            {
              "type": "text",
              "text": "Here are some effective search strategies to find the latest developments in renewable energy:\n\n## General Search Terms\n- \"Renewable energy news 2025\"\n- ..."
            }
          ],
          "stop_reason": "end_turn",
          "stop_sequence": null,
          "stop_details": null,
          "usage": { "input_tokens": 21, "output_tokens": 305 }
        }

bash
        export ANTHROPIC_API_KEY="your-api-key-here"

bash
        mkdir claude-quickstart && cd claude-quickstart
        python3 -m venv .venv && source .venv/bin/activate
        pip install anthropic

python Python
        import anthropic

        client = anthropic.Anthropic()

        message = client.messages.create(
            model="claude-opus-5",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": "What should I search for to find the latest developments in renewable energy?",
                }
            ],
        )

        for block in message.content:
            if block.type == "text":
                print(block.text)

bash
        python quickstart.py

text Output wrap
        Here are some effective search strategies to find the latest developments in renewable energy:

        ## General Search Terms
        - "Renewable energy news 2025"
        - ...

bash
        export ANTHROPIC_API_KEY="your-api-key-here"

bash
        mkdir claude-quickstart && cd claude-quickstart
        npm init -y
        npm pkg set type=module
        npm install @anthropic-ai/sdk

typescript TypeScript
        import Anthropic from "@anthropic-ai/sdk";

        const client = new Anthropic();

        const message = await client.messages.create({
          model: "claude-opus-5",
          max_tokens: 1000,
          messages: [
            {
              role: "user",
              content: "What should I search for to find the latest developments in renewable energy?"
            }
          ]
        });

        for (const block of message.content) {
          if (block.type === "text") {
            console.log(block.text);
          }
        }

bash
        npx tsx quickstart.ts

text Output wrap
        Here are some effective search strategies to find the latest developments in renewable energy:

        ## General Search Terms
        - "Renewable energy news 2025"
        - ...

bash
        export ANTHROPIC_API_KEY="your-api-key-here"

bash
        dotnet new console -n ClaudeQuickstart
        cd ClaudeQuickstart
        dotnet add package Anthropic

csharp C#
        using Anthropic;
        using Anthropic.Models.Messages;

        var client = new AnthropicClient();

        var message = await client.Messages.Create(new MessageCreateParams
        {
            Model = Model.ClaudeOpus5,
            MaxTokens = 1000,
            Messages =
            [
                new()
                {
                    Role = Role.User,
                    Content = "What should I search for to find the latest developments in renewable energy?",
                },
            ],
        });

        foreach (var block in message.Content)
        {
            if (block.TryPickText(out var textBlock))
            {
                Console.WriteLine(textBlock.Text);
            }
        }

bash
        dotnet run

text Output wrap
        Here are some effective search strategies to find the latest developments in renewable energy:

        ## General Search Terms
        - "Renewable energy news 2025"
        - ...

bash
        export ANTHROPIC_API_KEY="your-api-key-here"

bash
        mkdir claude-quickstart && cd claude-quickstart
        go mod init claude-quickstart
        go get github.com/anthropics/anthropic-sdk-go

go Go
        package main

        import (
        	"context"
        	"fmt"
        	"log"

        	"github.com/anthropics/anthropic-sdk-go"
        )

        func main() {
        	client := anthropic.NewClient()

        	message, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
        		Model:     anthropic.ModelClaudeOpus5,
        		MaxTokens: 1000,
        		Messages: []anthropic.MessageParam{
        			anthropic.NewUserMessage(anthropic.NewTextBlock("What should I search for to find the latest developments in renewable energy?")),
        		},
        	})
        	if err != nil {
        		log.Fatal(err)
        	}

        	for _, block := range message.Content {
        		if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
        			fmt.Println(textBlock.Text)
        		}
        	}
        }

bash
        go run .

text Output wrap
        Here are some effective search strategies to find the latest developments in renewable energy:

        ## General Search Terms
        - "Renewable energy news 2025"
        - ...

bash
        export ANTHROPIC_API_KEY="your-api-key-here"

bash
        mkdir -p claude-quickstart/src/main/java && cd claude-quickstart

kotlin
            plugins {
                application
            }

            repositories {
                mavenCentral()
            }

            java {
                toolchain {
                    languageVersion = JavaLanguageVersion.of(25)
                }
            }

            dependencies {
                implementation("com.anthropic:anthropic-java:2.60.0")
            }

            application {
                mainClass = "QuickStart"
            }

xml
            <project xmlns="http://maven.apache.org/POM/4.0.0">
              <modelVersion>4.0.0</modelVersion>
              <groupId>com.example</groupId>
              <artifactId>quickstart</artifactId>
              <version>1.0-SNAPSHOT</version>
              <properties>
                <maven.compiler.release>25</maven.compiler.release>
                <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
              </properties>
              <dependencies>
                <dependency>
                  <groupId>com.anthropic</groupId>
                  <artifactId>anthropic-java</artifactId>
                  <version>2.60.0</version>
                </dependency>
              </dependencies>
            </project>

java Java
        import com.anthropic.client.okhttp.AnthropicOkHttpClient;
        import com.anthropic.models.messages.Message;
        import com.anthropic.models.messages.MessageCreateParams;
        import com.anthropic.models.messages.Model;

        static void main() {
            var client = AnthropicOkHttpClient.fromEnv();

            var params = MessageCreateParams.builder()
                .model(Model.CLAUDE_OPUS_5)
                .maxTokens(1000)
                .addUserMessage(
                    "What should I search for to find the latest developments in renewable energy?"
                )
                .build();

            Message message = client.messages().create(params);
            for (var block : message.content()) {
                block.text().ifPresent(textBlock -> IO.println(textBlock.text()));
            }
        }

bash
            gradle run

bash
            mvn compile exec:java -Dexec.mainClass=QuickStart

text Output wrap
        Here are some effective search strategies to find the latest developments in renewable energy:

        ## General Search Terms
        - "Renewable energy news 2025"
        - ...

bash
        export ANTHROPIC_API_KEY="your-api-key-here"

bash
        mkdir claude-quickstart && cd claude-quickstart
        composer require "anthropic-ai/sdk" "guzzlehttp/guzzle:^7"

php PHP
        <?php
        require 'vendor/autoload.php';

        use Anthropic\Client;
        use Anthropic\Messages\Model;
        use Anthropic\Messages\TextBlock;

        $client = new Client();

        $message = $client->messages->create(
            model: Model::CLAUDE_OPUS_5,
            maxTokens: 1000,
            messages: [
                [
                    'role' => 'user',
                    'content' => 'What should I search for to find the latest developments in renewable energy?',
                ],
            ],
        );

        foreach ($message->content as $block) {
            if ($block instanceof TextBlock) {
                echo $block->text . PHP_EOL;
            }
        }

bash
        php quickstart.php

text Output wrap
        Here are some effective search strategies to find the latest developments in renewable energy:

        ## General Search Terms
        - "Renewable energy news 2025"
        - ...

bash
        export ANTHROPIC_API_KEY="your-api-key-here"

bash
        mkdir claude-quickstart && cd claude-quickstart
        bundle init
        bundle add anthropic

ruby Ruby
        require "anthropic"

        client = Anthropic::Client.new

        message = client.messages.create(
          model: Anthropic::Model::CLAUDE_OPUS_5,
          max_tokens: 1000,
          messages: [
            {
              role: "user",
              content: "What should I search for to find the latest developments in renewable energy?"
            }
          ]
        )

        message.content.each do |block|
          puts block.text if block.type == :text
        end

bash
        bundle exec ruby quickstart.rb

text Output wrap
        Here are some effective search strategies to find the latest developments in renewable energy:

        ## General Search Terms
        - "Renewable energy news 2025"
        - ...
        ```
      </Step>
    </Steps>
  </Tab>
</Tabs>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps

You made your first API call. Next, learn the Messages API patterns you'll use in every Claude integration.

<Card title="Working with the Messages API" icon="messages" href="https://platform.claude.com/docs/en/build-with-claude/working-with-messages">
  Learn multi-turn conversations, system prompts, stop reasons, and other core patterns.
</Card>

Once you're comfortable with the basics, explore further:

<CardGroup cols={2}>
  <Card title="Models overview" icon="brain" href="https://platform.claude.com/docs/en/models/overview">
    Compare Claude models by capability and cost.
  </Card>

  <Card title="Features overview" icon="list" href="https://platform.claude.com/docs/en/build-with-claude/overview">
    Browse all Claude capabilities: tools, context management, structured outputs, and more.
  </Card>

  <Card title="Client SDKs" icon="code-brackets" href="https://platform.claude.com/docs/en/cli-sdks-libraries/overview">
    Reference documentation for Python, TypeScript, C#, and other client libraries.
  </Card>

  <Card title="Authentication" icon="lock" href="https://platform.claude.com/docs/en/manage-claude/authentication">
    Compare API keys and Workload Identity Federation, and set key expiration.
  </Card>
</CardGroup>


---
title: Intro to Claude
url: https://platform.claude.com/docs/en/intro
description: Claude is a highly performant, trustworthy, and intelligent AI platform built by Anthropic. Claude excels at tasks involving language, reasoning, analysis, coding, and more.
---

<Note>
  Looking to chat with Claude? Visit [claude.ai](https://claude.ai).
</Note>

Anthropic offers two ways to build with Claude, each suited to different use cases:

|                | Messages API                                | Claude Managed Agents                                                     |
| -------------- | ------------------------------------------- | ------------------------------------------------------------------------- |
| **What it is** | Direct model prompting access               | Pre-built, configurable agent harness that runs in managed infrastructure |
| **Best for**   | Custom agent loops and fine-grained control | Long-running tasks and asynchronous work                                  |

To learn more about each, see [Using the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) and the [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview).


## Explore the latest generation of Claude models

Source: https://platform.claude.com/llms-full.txt#explore-the-latest-generation-of-claude-models

If you're unsure which model to use, start with [Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/overview) for most workloads. Use [Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/overview) for demanding reasoning and long-horizon agentic work, or when your evals on Claude Opus 5 at higher effort still fall short. All current models support text and image input, text output, multilingual capabilities, vision, and tool use. Each model's page lists the platforms it's available on.

* [Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/overview) (`claude-fable-5-1`) — New — *For demanding reasoning and long-horizon agentic work* — Most capable · Research · Multi-day tasks
* [Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/overview) (`claude-opus-5`) — *For complex agentic coding and enterprise work* — Complex projects · Agents · Coding
* [Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/overview) (`claude-sonnet-5`) — *The best combination of speed and intelligence* — Everyday tasks · Writing · Cost-efficient
* [Claude Haiku 4.5](https://platform.claude.com/docs/en/models/haiku-4-5/overview) (`claude-haiku-4-5`) — *The fastest model with near-frontier intelligence* — Fastest · Lowest cost · High volume

[Compare models](https://platform.claude.com/docs/en/models/overview)

***


## Recommended path for new developers

Source: https://platform.claude.com/llms-full.txt#recommended-path-for-new-developers

Follow these steps to go from zero to a working Claude integration.

<Steps>
  <Step title="Make your first API call">
    Set up your environment, install an SDK, and send your first message to Claude.

    [Go to the quickstart](https://platform.claude.com/docs/en/get-started)
  </Step>

  <Step title="Secure your credentials">
    Set an expiration when you create your API key. Keep the key out of source control, client-side code, and prompts. Check whether your workload can use Workload Identity Federation instead of a static key.

    [Read the authentication guide](https://platform.claude.com/docs/en/manage-claude/authentication)
  </Step>

  <Step title="Understand the Messages API">
    Learn the core request and response structure, including multi-turn conversations, system prompts, and stop reasons.

    [Read the Messages API guide](https://platform.claude.com/docs/en/build-with-claude/working-with-messages)
  </Step>

  <Step title="Choose the right model">
    Compare Claude models by capability and cost to pick the best fit for your use case.

    [See the models overview](https://platform.claude.com/docs/en/models/overview)
  </Step>

  <Step title="Explore features and tools">
    Discover what Claude can do: extended thinking, web search, file handling, structured outputs, and more.

    [Browse the features overview](https://platform.claude.com/docs/en/build-with-claude/overview)
  </Step>
</Steps>

***


## Develop with Claude

Source: https://platform.claude.com/llms-full.txt#develop-with-claude

Anthropic provides developer tools to help you build and scale applications with Claude.

<CardGroup cols={3}>
  <Card title="Developer Console" icon="computer" href="https://platform.claude.com/">
    Explore and understand the API in your browser with playground.
  </Card>

  <Card title="API Reference" icon="code" href="https://platform.claude.com/docs/en/api/overview">
    Explore the full Claude API and client SDK documentation.
  </Card>

  <Card title="Claude Cookbook" icon="chef-hat" href="https://platform.claude.com/cookbook">
    Learn with interactive Jupyter notebooks covering PDFs, embeddings, and more.
  </Card>
</CardGroup>

***


## Key capabilities

Source: https://platform.claude.com/llms-full.txt#key-capabilities

Claude can assist with many tasks that involve text, code, and images.

<CardGroup cols={2}>
  <Card title="Text and code generation" icon="text-aa" href="https://platform.claude.com/docs/en/build-with-claude/overview">
    Summarize text, answer questions, extract data, translate text, and explain and generate code.
  </Card>

  <Card title="Vision" icon="image" href="https://platform.claude.com/docs/en/build-with-claude/vision">
    Process and analyze visual input and generate text and code from images.
  </Card>
</CardGroup>

***


## Support

Source: https://platform.claude.com/llms-full.txt#support

<CardGroup cols={2}>
  <Card title="Help Center" icon="help" href="https://support.claude.com/en/">
    Find answers to frequently asked account and billing questions.
  </Card>

  <Card title="Service Status" icon="chart" href="https://status.claude.com">
    Check the status of Anthropic services.
  </Card>
</CardGroup>


---
title: Authentication
url: https://platform.claude.com/docs/en/manage-claude/authentication
description: Authenticate to the Claude API with API keys, Workload Identity Federation, or App Attest.
---

The Claude API supports three ways to authenticate requests:

| Method                                                                                                                        | Credential                                                                                              | Best for                                                                                                                                        |
| ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [API key](https://platform.claude.com/docs/en/manage-claude/authentication#api-keys)                                          | Static `sk-ant-api...` secret sent as a bearer token in the `Authorization` header                      | Local development, prototyping, scripts, and servers where you control secret storage                                                           |
| [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/authentication#workload-identity-federation) | Short-lived bearer token exchanged from your identity provider's identity token                         | Production workloads on cloud platforms (AWS, Google Cloud, Azure), CI/CD pipelines, and Kubernetes, where you want to eliminate static secrets |
| [App Attest](https://platform.claude.com/docs/en/manage-claude/authentication#app-attest)                                     | Short-lived access token issued to a genuine, attested installation of your registered iOS or macOS app | iOS and macOS apps distributed to end users, where the app calls the Claude API directly with no back end or proxy                              |

API keys and Workload Identity Federation grant the same access to Claude API endpoints. Choose API keys to get started quickly: a personal key for your own development, or a service account key for anything shared. Move to Workload Identity Federation when your workload already has a platform-issued identity you can federate. Use App Attest for iOS and macOS apps you distribute to end users.


## API keys

Source: https://platform.claude.com/llms-full.txt#api-keys

API keys are static secrets that you generate in the Claude Console and send on every request as a bearer token in the `Authorization` header.

### Key types

When you create a key, you choose its type, which determines what the key can do, where it works, and when it stops working:

| Key type                   | Acts as                                                                                                              | Works in                                                                                                                                                                                              | Stops working when                                                                                                                                                                                                                   |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Personal key**           | You, the user, with your roles and permissions                                                                       | Either a single workspace or the workspaces where your role allows API use, chosen when the key is created                                                                                            | You lose access to the organization or, for a single-workspace key, to that workspace. Personal keys are archived when you are removed from the organization. If you are re-invited, create new keys; archived keys are not restored |
| **Service account key**    | A [service account](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#service-accounts) | Either a single workspace or anything the service account has access to, chosen when the key is created. A service account has access to the Default Workspace and to workspaces it has been added to | The service account is archived or, for a single-workspace key, is removed from that workspace                                                                                                                                       |
| **Workspace key** (legacy) | No one: it belongs to the workspace it was created in                                                                | That workspace                                                                                                                                                                                        | It expires, is disabled or deleted, or its workspace is archived, regardless of whether its creator leaves the organization                                                                                                          |

Personal keys and service account keys are identity-backed: each belongs to a user or service account your organization already manages, and every request acts as that identity. When that identity is removed from the organization, the key stops working. This means that keys won't accidentally outlive the people or workloads that own them. Prefer them over workspace keys for new integrations.

Use a personal key for your own development and scripts. A shared personal key acts as one person and breaks when they leave. For shared or automated workloads (CI, production services), have an organization admin create a service account so the workload has its own identity.

Workspace API keys still work but should be considered legacy; identity-backed keys or [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) are preferred. To migrate, see [Replacing workspace API keys](https://platform.claude.com/docs/en/manage-claude/authentication#replacing-workspace-api-keys).

### Create and use a key

* **Create a key:** Go to [Settings → API keys](https://platform.claude.com/settings/keys) in the Claude Console and click **Create key**. Name the key and choose an [expiration](https://platform.claude.com/docs/en/manage-claude/authentication#key-expiration). Set **Linked account** to yourself for a personal key, or to a service account for a key shared across multiple users. You can also scope the key to a specific workspace, which lets you skip setting a workspace ID manually in future requests.
* **Use the key:** Send it as `Authorization: Bearer <key>` on direct HTTP requests, or set the `ANTHROPIC_API_KEY` environment variable and the [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) pick it up automatically.

The legacy `x-api-key: YOUR_API_KEY` header is still supported in place of `Authorization`.

Store API keys in a secrets manager, rotate them periodically, and disable or delete any key you suspect has leaked. On the [API keys page](https://platform.claude.com/settings/keys), **Disable** is reversible (the Admin API reports the key's `status` as `"inactive"`, and **Re-enable** returns it to `"active"`), while **Delete** is permanent: the key is archived and still appears in [List API Keys](https://platform.claude.com/docs/en/api/admin/api_keys/list) with `status: "archived"`. Expired keys can only be deleted. You can also set an [expiration](https://platform.claude.com/docs/en/manage-claude/authentication#key-expiration) when you create a key to limit how long a leaked credential stays usable.

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello, Claude"}]
    }'

python Python
  client = Anthropic(api_key="my-anthropic-api-key")
  # or, with ANTHROPIC_API_KEY set in the environment:
  client = Anthropic()

typescript TypeScript
  const client = new Anthropic({ apiKey: "my-anthropic-api-key" });
  // or, with ANTHROPIC_API_KEY set in the environment:
  // const client = new Anthropic();

go Go
  client := anthropic.NewClient(
  	option.WithAPIKey("sk-ant-api03-..."), // defaults to os.LookupEnv("ANTHROPIC_API_KEY")
  )

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;

  // Explicit
  AnthropicClient client = AnthropicOkHttpClient.builder()
    .apiKey("my-anthropic-api-key")
    .build();

  // From ANTHROPIC_API_KEY (or anthropic.apiKey system property)
  AnthropicClient clientFromEnv = AnthropicOkHttpClient.fromEnv();

csharp C#
  using Anthropic;

  AnthropicClient client = new() { ApiKey = "my-anthropic-api-key" };
  // Or, with ANTHROPIC_API_KEY set in the environment:
  // AnthropicClient client = new();

php PHP
  // Reads ANTHROPIC_API_KEY from the environment
  $client = new Client();
  // Or pass the key explicitly:
  $client = new Client(apiKey: 'my-anthropic-api-key');

ruby Ruby
  anthropic = Anthropic::Client.new(api_key: "my-anthropic-api-key")
  # or, with ANTHROPIC_API_KEY set in the environment:
  anthropic = Anthropic::Client.new

bash CLI
  # See /docs/en/cli-sdks-libraries/cli/authentication#api-key for zsh, bash, and Windows variants
  export ANTHROPIC_API_KEY=sk-ant-api03-...

bash cURL
  # Required on every request for a multi-workspace key.
  # Omit the anthropic-workspace-id header for a single-workspace key.
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-workspace-id: wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello, Claude"}]
    }'

bash CLI
  # Required on every command for a multi-workspace key.
  # Omit --workspace-id for a single-workspace key.
  ant messages create \
    --workspace-id wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello, Claude"}'

python Python
  client = Anthropic()  # reads ANTHROPIC_API_KEY

  # Required on every request for a multi-workspace key.
  # Omit extra_headers for a single-workspace key.
  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
      extra_headers={"anthropic-workspace-id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ"},
  )
  print(message.content)

  # Or set it once for every request from this client:
  workspace_client = Anthropic(
      default_headers={"anthropic-workspace-id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ"},
  )

typescript TypeScript
  const client = new Anthropic(); // reads ANTHROPIC_API_KEY

  // Required on every request for a multi-workspace key.
  // Omit the second argument for a single-workspace key.
  const message = await client.messages.create(
    {
      model: "claude-opus-5",
      max_tokens: 1024,
      messages: [{ role: "user", content: "Hello, Claude" }]
    },
    { headers: { "anthropic-workspace-id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ" } }
  );
  console.log(message.content);

  // Or set it once for every request from this client:
  const workspaceClient = new Anthropic({
    defaultHeaders: { "anthropic-workspace-id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ" }
  });

csharp C#
  AnthropicClient client = new(); // reads ANTHROPIC_API_KEY

  MessageCreateParams parameters = new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello, Claude" }],
  };

  // Required on every request for a multi-workspace key.
  // Call client.Messages.Create(parameters) directly for a single-workspace key.
  var message = await client
      .WithOptions(options =>
          options with
          {
              ExtraHeaders = new Dictionary<string, string>
              {
                  ["anthropic-workspace-id"] = "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ",
              },
          }
      )
      .Messages.Create(parameters);
  Console.WriteLine(message);

  // Or set it once for every request from this client:
  AnthropicClient workspaceClient = new(new ClientOptions
  {
      ExtraHeaders = new Dictionary<string, string>
      {
          ["anthropic-workspace-id"] = "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ",
      },
  });

go Go
  client := anthropic.NewClient() // reads ANTHROPIC_API_KEY

  // Required on every request for a multi-workspace key.
  // Omit the option for a single-workspace key.
  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, Claude")),
  	},
  }, option.WithHeader("anthropic-workspace-id", "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ"))
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(message.Content)

  // Or set it once for every request from this client:
  workspaceClient := anthropic.NewClient(
  	option.WithHeader("anthropic-workspace-id", "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ"),
  )

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv(); // reads ANTHROPIC_API_KEY

  // Required on every request for a multi-workspace key.
  // Omit putAdditionalHeader for a single-workspace key.
  Message message = client.messages().create(MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024)
      .addUserMessage("Hello, Claude")
      .putAdditionalHeader("anthropic-workspace-id", "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ")
      .build());

  IO.println(message.content());

  // Or set it once for every request from this client:
  AnthropicClient workspaceClient = AnthropicOkHttpClient.builder()
      .fromEnv()
      .putHeader("anthropic-workspace-id", "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ")
      .build();

php PHP
  $client = new Client(); // reads ANTHROPIC_API_KEY

  // Required on every request for a multi-workspace key.
  // Omit requestOptions for a single-workspace key.
  $message = $client->messages->create(
      model: Model::CLAUDE_OPUS_5,
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
      requestOptions: [
          'extraHeaders' => ['anthropic-workspace-id' => 'wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ'],
      ],
  );

  echo json_encode($message->content), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new # reads ANTHROPIC_API_KEY

  # Required on every request for a multi-workspace key.
  # Omit request_options for a single-workspace key.
  message = client.messages.create(
    model: Anthropic::Model::CLAUDE_OPUS_5,
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}],
    request_options: {extra_headers: {"anthropic-workspace-id" => "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ"}}
  )

  puts message.content

json JSON
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "anthropic-workspace-id is required when authenticating with an identity-linked API key; send the id of the workspace this request acts in."
  },
  "request_id": "req_011CSHoEeqs5C35K2UUqR7Fy"
}
```

A header value that isn't a valid workspace ID returns a 400 `invalid_request_error` with the message `anthropic-workspace-id header must be a valid workspace ID.` If the workspace doesn't exist, or the key's user or service account doesn't have access to it, the API returns a 404 `not_found_error` with the message ``Workspace `<id>` not found.``, the same response as for any unknown workspace.

Workload Identity Federation selects a workspace at token exchange instead; see the [WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference) for details.

### Key expiration

When you create an API key from the [API keys page](https://platform.claude.com/settings/keys) in the Claude Console, you choose an expiration: a preset (3 hours, 1 day, 7 days, or 30 days), a custom duration, or **Never** for keys you store in a secrets manager and rotate yourself. If your organization has a maximum expiration policy, the Console limits presets and custom durations to the policy maximum, and **Never** is unavailable. Existing keys keep their current behavior; expiration is set at creation time and cannot be changed afterward. The same expiration choice applies when you [create an Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys) in the Claude Console.

Anthropic emails the key's creator as the expiration approaches: 7 days before expiration for keys created with a lifetime of at least 14 days, and 1 day before for keys with a lifetime of at least 7 days. Keys with shorter lifetimes expire without a warning email.

After a key expires, requests made with it return a `401 authentication_error`. Create a new key to restore access; expired keys cannot be reactivated.

The Console API keys table shows each key's expiration, and the Admin API reports each key's `expires_at` timestamp on the [List API Keys](https://platform.claude.com/docs/en/api/admin/api_keys/list) and [Retrieve API Key](https://platform.claude.com/docs/en/api/admin/api_keys/retrieve) endpoints, so you can audit and rotate keys before they expire. The field is `null` for keys without an expiration.

Expiration limits the lifetime of a leaked credential, but it is not a substitute for secret hygiene. Regardless of expiration, store keys in a secrets manager and disable or delete any key you suspect has leaked.

### Replacing workspace API keys

If you have a workspace key, you may want to replace it with [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/wif-reference) or a personal or service account key. This provides better security and observability.

See [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/wif-reference) for details on configuring Workload Identity Federation, which is preferred over long-lived keys.

To replace a workspace key with a personal or service account key:

1. **Decide the key type.** Your own tooling should use a personal key. A shared or unattended workload should use a service account key.
2. **Create a service account** if necessary. You may have to ask an organization admin to create one in [Settings → Service accounts](https://platform.claude.com/settings/service-accounts) and add it to the relevant workspace.
3. **Create the new key.** Create it specifically for the integration's workspace unless multiple workspaces are needed.
4. **Deploy the new key.** Replace the old key wherever the integration reads it, typically the `ANTHROPIC_API_KEY` environment variable or a secrets manager entry. For a multi-workspace key, also send the `anthropic-workspace-id` header as shown in [Select a workspace](https://platform.claude.com/docs/en/manage-claude/authentication#select-a-workspace).
5. **Delete the old key.** Confirm that requests succeed, then delete the workspace key on the [API keys page](https://platform.claude.com/settings/keys).


## Workload Identity Federation

Source: https://platform.claude.com/llms-full.txt#workload-identity-federation

Workload Identity Federation (WIF) lets a workload authenticate with a short-lived identity token issued by an identity provider (IdP) you already trust, such as AWS IAM, Google Cloud, or any standards-compliant OIDC issuer (such as GitHub Actions, Kubernetes service accounts, SPIFFE, Microsoft Entra ID, or Okta). The workload exchanges its IdP-issued JWT at `POST /v1/oauth/token` for a short-lived Claude API access token, and the SDK refreshes that token automatically before it expires. There is no `sk-ant-api...` string to mint, distribute, or rotate.

Federation removes long-lived Claude API keys from your environment, which shrinks the blast radius of a leaked credential and lets you manage access with the same IdP controls you already use for cloud resources. It does not, on its own, guarantee end-to-end security: the trust chain is only as strong as your identity provider's configuration, and a long-lived secret one hop upstream (for example, a static cloud credential that can mint IdP tokens) can still undermine it. Pair federation with your provider's controls, such as IP allowlists, MFA, and audit logging.

To configure federation, you create three resources in the Claude Console (a service account, a federation issuer, and a federation rule) and then point your SDK at the rule. See [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) for the full setup walkthrough.


## App Attest

Source: https://platform.claude.com/llms-full.txt#app-attest

App Attest authenticates iOS and macOS apps that call the Claude API directly from the device. Each installation proves that it is a genuine, unmodified build of an app you registered in the Claude Console, using Apple's App Attest service. Anthropic then issues the device a short-lived access token that bills usage to your workspace. Tokens are scoped to your workspace, expire after one hour, and authorize only [Messages API](https://platform.claude.com/docs/en/api/messages/create) calls.

To register your app and get a client ID, see [App Attest for iOS and macOS apps](https://platform.claude.com/docs/en/manage-claude/app-attest).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-2

<CardGroup cols={2}>
  <Card title="Set up Workload Identity Federation" icon="lock" href="https://platform.claude.com/docs/en/manage-claude/workload-identity-federation">
    Configure issuers, rules, and service accounts, then exchange tokens
  </Card>

  <Card title="Identity provider guides" icon="cloud" href="https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#identity-providers">
    Step-by-step guides for AWS, Google Cloud, Azure, GitHub Actions, Kubernetes, SPIFFE, and Okta
  </Card>

  <Card title="WIF reference" icon="book" href="https://platform.claude.com/docs/en/manage-claude/wif-reference">
    Environment variables, validation rules, profile configuration, and error reference
  </Card>

  <Card title="App Attest for iOS and macOS apps" icon="fingerprint" href="https://platform.claude.com/docs/en/manage-claude/app-attest">
    Let genuine installations of your app call the Claude API without shipping an API key
  </Card>

  <Card title="Client SDKs" icon="code" href="https://platform.claude.com/docs/en/cli-sdks-libraries/overview">
    Python, TypeScript, C#, Go, Java, PHP, Ruby, and the CLI
  </Card>
</CardGroup>


---
title: Get your Claude API key
url: https://platform.claude.com/docs/en/get-api-key
description: Find, create, and manage your API keys for the Claude API in the Claude Console.
---

API keys for the Claude API (also called Anthropic API keys) live in the Claude Console. To view your existing keys or create a new one, go to [Settings → API keys](https://platform.claude.com/settings/keys).


## Choose a key type

Source: https://platform.claude.com/llms-full.txt#choose-a-key-type

When you create a key, you choose its type, which determines what the key can do, where it works, and when it stops working. A **personal key** acts as you, and stops working if you leave an organization. A **service account key** represents a [service account](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#service-accounts) which can be used by workloads such as CI pipelines, production services, or agents. Use a personal key for your own development, and a service account key for anything shared.

You can also create a **workspace key**, a legacy key without an owner: it belongs to the workspace you create it in and keeps working after its creator leaves. It is preferable to use a personal or service account key, as these stop working automatically when their associated account is removed from the organization.


## Create an API key

Source: https://platform.claude.com/llms-full.txt#create-an-api-key

<Steps>
  <Step title="Sign in to the Claude Console">
    Go to [platform.claude.com](https://platform.claude.com/) and sign in, or create an account if you don't have one yet.
  </Step>

  <Step title="Open the API keys page">
    Go to [Settings → API keys](https://platform.claude.com/settings/keys).
  </Step>

  <Step title="Create a key">
    Click **Create key**, name the key, choose an [expiration](https://platform.claude.com/docs/en/manage-claude/authentication#key-expiration), and set **Linked account** to yourself or a service account. You can also choose a [workspace](https://platform.claude.com/settings/workspaces) to scope the key to.
  </Step>

  <Step title="Copy and store the key">
    The Console shows the full key, which starts with `sk-ant-`, only once, at creation. Copy it and store it somewhere safe, such as a secrets manager. If you lose a key, you can't view it again in the Console. Create a new key instead.
  </Step>
</Steps>

If the **Create key** button on the API keys page is disabled, your role may not allow you to create keys there. Ask an organization admin to change your role, or to create a service account key for your workload.


## Use your API key

Source: https://platform.claude.com/llms-full.txt#use-your-api-key

Set the key as an environment variable:

The [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) read `ANTHROPIC_API_KEY` automatically. Direct HTTP requests send the key in the `x-api-key` header. If your API key works on multiple workspaces, you must also send the `anthropic-workspace-id` header on each Claude API request, as shown in [Select a workspace](https://platform.claude.com/docs/en/manage-claude/authentication#select-a-workspace). For the Admin API, see [API keys and the Admin API](https://platform.claude.com/docs/en/get-api-key#api-keys-and-the-admin-api).

To make your first request, follow the [Quickstart](https://platform.claude.com/docs/en/get-started), and see [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication) for the full picture, including short-lived credentials with Workload Identity Federation.


## API keys and the Admin API

Source: https://platform.claude.com/llms-full.txt#api-keys-and-the-admin-api

The [Admin API](https://platform.claude.com/docs/en/api/admin) includes endpoints for managing your organization's API keys programmatically, such as [Retrieve API Key](https://platform.claude.com/docs/en/api/admin/api_keys/retrieve) and [List API Keys](https://platform.claude.com/docs/en/api/admin/api_keys/list). These endpoints are for organization admins automating key management. They accept an [Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys), an OAuth token with the `org:admin` scope, or a personal or service account key that isn't scoped to a specific workspace; workspace keys don't work there. They never return a key's secret value, only a partially redacted hint.

<Note>
  The Admin API can't recover a lost key or give you a key to call the Claude API with. To get a usable API key, create one in [Settings → API keys](https://platform.claude.com/settings/keys) in the Claude Console.
</Note>


### Building with Claude

---
title: Features overview
url: https://platform.claude.com/docs/en/build-with-claude/overview
description: Explore Claude's advanced features and capabilities.
---

Claude's API surface is organized into five areas:

* **Model capabilities:** Control how Claude reasons and formats responses.
* **Tools:** Let Claude take actions on the web or in your environment.
* **Tool infrastructure:** Handles discovery and orchestration at scale.
* **Context management:** Keeps long-running sessions efficient.
* **Files and assets:** Manage the documents and data you provide to Claude.

If you're new, start with [model capabilities](https://platform.claude.com/docs/en/build-with-claude/overview#model-capabilities) and [tools](https://platform.claude.com/docs/en/build-with-claude/overview#tools). Return to the other sections when you're ready to optimize cost, latency, or scale.

For administration and governance, see the [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api), the [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api), and the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api).


## Feature availability

Source: https://platform.claude.com/llms-full.txt#feature-availability

The Availability column in each of the following tables lists the platforms that offer a feature. A platform listed without a label offers the feature as stable, fully supported, and recommended for production use, with no beta header and with standard API [versioning](https://platform.claude.com/docs/en/api/versioning) guarantees. A label after a platform name marks one of the following classifications on that platform. Not all features pass through every stage, and a feature may enter at any stage or skip stages.

| Classification | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Beta**       | Preview features used for gathering feedback and iterating on a less mature use case. Availability may be limited, including through sign-up requirements or waitlists, and may not be publicly announced. Features may change significantly or be discontinued based on feedback. Not guaranteed for ongoing production use. Breaking changes are possible with notice, and some platform-specific limitations may apply. Beta features on the Claude API and [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) have a [beta header](https://platform.claude.com/docs/en/api/beta-headers). |
| **Deprecated** | Feature is still functional but no longer recommended. A migration path and removal timeline are provided.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **Retired**    | Feature is no longer available.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

**Platform labels:** Claude API (Anthropic first-party) · [Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) (AWS-operated) · [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) (Anthropic-operated on AWS) · [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai) (Google-operated) · [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry) (Anthropic-operated on Azure)


## Model capabilities

Source: https://platform.claude.com/llms-full.txt#model-capabilities

Ways to steer Claude and Claude's direct outputs, including response format, reasoning depth, and input modalities.

<Tip>
  You can discover which capabilities a model supports programmatically. The [Models API](https://platform.claude.com/docs/en/api/models/list) returns `max_input_tokens`, `max_tokens`, and a `capabilities` object for every available model.
</Tip>

The ZDR column indicates whether a feature is available under a Zero Data Retention arrangement. For most features this depends only on what the feature mechanism retains; for features tied to specific models, model-level ZDR availability also applies. See [Model-specific data retention requirements](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements).

| Feature                                                                                             | Description                                                                                                                                                                                                                                                                                                                                  | Zero Data Retention (ZDR)                                                                                             | Availability                                                                                      |
| --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)            | Up to 1M tokens for processing large documents, extensive code bases, and long conversations.                                                                                                                                                                                                                                                | ZDR eligible                                                                                                          | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |
| [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)                 | Let Claude dynamically decide when and how much to think. The only thinking mode on Claude 4.7 and later models. Use the effort parameter to control thinking depth.                                                                                                                                                                         | ZDR eligible                                                                                                          | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |
| [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)          | Process large volumes of requests asynchronously for cost savings. Send batches with a large number of queries per batch. Batch API calls cost 50% less than standard API calls.                                                                                                                                                             | Not ZDR eligible                                                                                                      | <PlatformAvailability claudeApi claudePlatformAws />                                              |
| [Citations](https://platform.claude.com/docs/en/build-with-claude/citations)                        | Ground Claude's responses in source documents. With Citations, Claude can provide detailed references to the exact sentences and passages it uses to generate responses, leading to more verifiable, trustworthy outputs.                                                                                                                    | ZDR eligible                                                                                                          | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |
| [Data residency](https://platform.claude.com/docs/en/manage-claude/data-residency)                  | Control where model inference runs using geographic controls. Specify `"global"` or `"us"` routing per request through the `inference_geo` parameter.                                                                                                                                                                                        | ZDR eligible                                                                                                          | <PlatformAvailability claudeApi claudePlatformAws />                                              |
| [Effort](https://platform.claude.com/docs/en/build-with-claude/effort)                              | Control how many tokens Claude uses when responding with the effort parameter, trading off between response thoroughness and token efficiency.                                                                                                                                                                                               | ZDR eligible                                                                                                          | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |
| [Fallback credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit)            | Avoid paying the prompt-cache cost twice when you retry a refused request on another model. The refusal carries a credit token, and echoing it on the retry bills the retry as though the conversation had been on the new model all along. Message Batches results do not include fallback credit tokens.                                   | Not ZDR eligible\*                                                                                                    | <PlatformAvailability claudeApiBeta claudePlatformAwsBeta bedrockBeta vertexAiBeta azureAiBeta /> |
| [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support)                    | Process and analyze text and visual content from PDF documents.                                                                                                                                                                                                                                                                              | ZDR eligible                                                                                                          | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |
| [Search results](https://platform.claude.com/docs/en/build-with-claude/search-results)              | Enable natural citations for RAG applications by providing search results with proper source attribution. Achieve web search-quality citations for custom knowledge bases and tools.                                                                                                                                                         | ZDR eligible                                                                                                          | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |
| [Server-side fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) | Retry a refused request inside a single API call. Use the `"default"` mode to apply Anthropic's recommended fallback models, or name up to three models of your own; when the requested model declines, the API runs the next model in the chain on the same request. The `fallbacks` parameter is not available in the Message Batches API. | Not ZDR eligible\*                                                                                                    | <PlatformAvailability claudeApiBeta />                                                            |
| [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)      | Guarantee schema conformance with two approaches: JSON outputs for structured data responses, and strict tool use for validated tool inputs.                                                                                                                                                                                                 | [ZDR eligible (qualified)](https://platform.claude.com/docs/en/build-with-claude/structured-outputs#data-retention)\* | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |
| [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)                          | Enhanced reasoning capabilities for complex tasks, providing transparency into Claude's step-by-step thought process before delivering its final answer.                                                                                                                                                                                     | ZDR eligible                                                                                                          | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |


## Tools

Source: https://platform.claude.com/llms-full.txt#tools

Built-in tools that Claude invokes through `tool_use`. Server-side tools are run by the platform; client-side tools are implemented and executed by you.

### Server-side tools

| Feature                                                                                             | Description                                                                                                                                               | ZDR              | Availability                                                          |
| --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | --------------------------------------------------------------------- |
| [Advisor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)          | Pair a faster executor model with a higher-intelligence advisor model that provides strategic guidance mid-generation for long-horizon agentic workloads. | ZDR eligible     | <PlatformAvailability claudeApiBeta claudePlatformAwsBeta />          |
| [Code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) | Run code in a sandboxed environment for advanced data analysis, calculations, and file processing. Free when used with web search or web fetch.           | Not ZDR eligible | <PlatformAvailability claudeApi claudePlatformAws azureAi />†         |
| [Web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool)           | Retrieve full content from specified web pages and PDF documents for in-depth analysis.                                                                   | ZDR eligible\*   | <PlatformAvailability claudeApi claudePlatformAws azureAi />          |
| [Web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)         | Augment Claude's comprehensive knowledge with current, real-world data from across the web.                                                               | ZDR eligible\*   | <PlatformAvailability claudeApi claudePlatformAws vertexAi azureAi /> |

### Client-side tools

| Feature                                                                                         | Description                                                                                                                                                        | ZDR          | Availability                                                                              |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ----------------------------------------------------------------------------------------- |
| [Bash](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool)                 | Execute bash commands and scripts to interact with the system shell and perform command-line operations.                                                           | ZDR eligible | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />             |
| [Browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool)   | Navigate, read, and interact with webpages in your own browser environment.                                                                                        | ZDR eligible | <PlatformAvailability claudeApi vertexAi />                                               |
| [Computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) | Control computer interfaces by taking screenshots and issuing mouse and keyboard commands.                                                                         | ZDR eligible | <PlatformAvailability claudeApi claudePlatformAwsBeta bedrockBeta vertexAi azureAiBeta /> |
| [Memory](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)             | Enable Claude to store and retrieve information across conversations. Build knowledge bases over time, maintain project context, and learn from past interactions. | ZDR eligible | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />             |
| [Text editor](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)   | Create and edit text files with a built-in text editor interface for file manipulation tasks.                                                                      | ZDR eligible | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />             |


## Tool infrastructure

Source: https://platform.claude.com/llms-full.txt#tool-infrastructure

Infrastructure that supports discovering, orchestrating, and scaling tool use.

| Feature                                                                                                                  | Description                                                                                                                                                                                                           | ZDR              | Availability                                                                  |
| ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------------------------------------------------------------------------- |
| [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)                               | Extend Claude's capabilities with Skills. Use pre-built Skills (PowerPoint, Excel, Word, PDF) or create custom Skills with instructions and scripts. Skills use progressive disclosure to efficiently manage context. | Not ZDR eligible | <PlatformAvailability claudeApi claudePlatformAwsBeta azureAiBeta />†         |
| [Fine-grained tool streaming](https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming) | Stream tool use parameters without buffering/JSON validation, reducing latency for receiving large parameters.                                                                                                        | ZDR eligible     | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi /> |
| [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)                                      | Connect to remote [MCP](https://platform.claude.com/docs/en/mcp) servers directly from the Messages API without a separate MCP client.                                                                                | Not ZDR eligible | <PlatformAvailability claudeApiBeta claudePlatformAwsBeta azureAiBeta />      |
| [Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)     | Enable Claude to call your tools programmatically from within code execution containers, reducing latency and token consumption for multi-tool workflows.                                                             | Not ZDR eligible | <PlatformAvailability claudeApi claudePlatformAws azureAi />†                 |
| [Tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)                            | Scale to thousands of tools by dynamically discovering and loading tools on-demand using regex- and BM25-based search, optimizing context usage and improving tool selection accuracy.                                | ZDR eligible     | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi /> |


## Context management

Source: https://platform.claude.com/llms-full.txt#context-management

Infrastructure for controlling and optimizing Claude's context window.

| Feature                                                                                                            | Description                                                                                                                                                                                           | ZDR          | Availability                                                                                      |
| ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------- |
| [Compaction](https://platform.claude.com/docs/en/build-with-claude/compaction)                                     | Server-side context summarization for long-running conversations. When context approaches the window limit, the API automatically summarizes earlier parts of the conversation.                       | ZDR eligible | <PlatformAvailability claudeApiBeta claudePlatformAwsBeta bedrockBeta vertexAiBeta azureAiBeta /> |
| [Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing)                           | Automatically manage conversation context with configurable strategies. Supports clearing tool results when approaching token limits and managing thinking blocks in extended thinking conversations. | ZDR eligible | <PlatformAvailability claudeApiBeta claudePlatformAwsBeta bedrockBeta vertexAiBeta azureAiBeta /> |
| [Automatic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#automatic-caching) | Simplify prompt caching to a single API parameter. The system automatically caches the last cacheable block in your request, moving the cache point forward as conversations grow.                    | ZDR eligible | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |
| [Prompt caching (5m)](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)                        | Provide Claude with more background knowledge and example outputs to reduce costs and latency.                                                                                                        | ZDR eligible | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |
| [Prompt caching (1hr)](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#1-hour-cache-duration) | Extended 1-hour cache duration for less frequently accessed but important context, complementing the standard 5-minute cache.                                                                         | ZDR eligible | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |
| [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)                             | Token counting enables you to determine the number of tokens in a message before sending it to Claude, helping you make informed decisions about your prompts and usage.                              | ZDR eligible | <PlatformAvailability claudeApi claudePlatformAws bedrock vertexAi azureAi />                     |


## Files and assets

Source: https://platform.claude.com/llms-full.txt#files-and-assets

Manage files and assets for use with Claude.

| Feature                                                                  | Description                                                                                                                       | ZDR              | Availability                                                          |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- | ---------------- | --------------------------------------------------------------------- |
| [Files API](https://platform.claude.com/docs/en/build-with-claude/files) | Upload and manage files to use with Claude without re-uploading content with each request. Supports PDFs, images, and text files. | Not ZDR eligible | <PlatformAvailability claudeApi claudePlatformAwsBeta azureAiBeta />† |

\* **Structured outputs:** Your prompts and Claude's outputs are not stored. Only JSON schemas are cached, for up to 24 hours since last use. **Web search and web fetch:** ZDR-eligible except when [dynamic filtering](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool#dynamic-filtering) is enabled. **Fallback credit and server-side fallback:** The features retain no message content, but they handle refusals from the Claude Fable models, which [are not available under ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements). See [ZDR details](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#feature-eligibility).

† On Microsoft Foundry, feature availability differs by [hosting option](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#hosting-options). These features are available on Hosted on Anthropic deployments, and not on Hosted on Azure deployments.


---
title: Fallback credit
url: https://platform.claude.com/docs/en/build-with-claude/fallback-credit
description: Avoid paying the prompt-cache cost twice when you retry a refused request on another model.
---

Prompt caches are per-model. When a model declines a request and you retry on another model, the conversation prefix already cached for the first model must be written into the new model's cache from scratch. Cache writes cost more than cache reads. Fallback credit removes that extra cost. The refusal carries a credit token, you echo the token on the retry, and the retry is billed as though the conversation had been on the new model all along.

You need this page only when you build the retry yourself: over raw HTTP or with custom retry logic. [Server-side fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#server-side-fallback) and the [SDK middleware](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#client-side-fallback) apply fallback credit automatically. If you use either, skip this page.

[Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) covers detecting refusals and choosing a fallback approach. [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) explains cache reads and cache writes if those terms are new.


## The basic flow

Source: https://platform.claude.com/llms-full.txt#the-basic-flow

<Steps>
  <Step title="Opt in with the beta header">
    Send the request that may be refused with the `anthropic-beta: fallback-credit-2026-07-01` header. The `server-side-fallback-2026-07-01` header also grants the same fields, and the earlier `fallback-credit-2026-06-01` header remains accepted and grants the same fields.
  </Step>

  <Step title="Read two fields from the refusal">
    On a refusal, `stop_details` includes two fields:

    * **`fallback_credit_token`:** an opaque string that represents the credit.
    * **`fallback_has_prefill_claim`:** a Boolean that tells you which retry body shape to use.

    Both are `null` when no credit is available for the refusal.
  </Step>

  <Step title="Build the retry">
    Start from the refused request body. Set `model` to the fallback model and add the token as the top-level `fallback_credit_token` parameter. Pick the body shape from the following table.
  </Step>

  <Step title="Send the retry with the same header">
    Send the retry with the same `fallback-credit-2026-07-01` beta header. The retry needs the header to redeem the token.
  </Step>
</Steps>

The `fallback_has_prefill_claim` field tells you whether the retry can continue the refused model's partial output instead of starting over:

| `fallback_has_prefill_claim` | Retry body                                                                                                                                                                                                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `true`                       | The refused request body, unchanged, plus one appended assistant message whose `content` echoes the refused response's `content`. The retry model continues the response from where the refused model stopped, and completed server tool calls are not re-executed. |
| `false`                      | The refused request body, unchanged.                                                                                                                                                                                                                                |


## Example

Source: https://platform.claude.com/llms-full.txt#example

The following example makes a request that may be refused and redeems the credit token on a retry against Claude Opus 4.8. When a retry attempt is rejected, the example degrades through the rejection ladder: the sequence of progressively simpler retry shapes covered in [When a retry is rejected](https://platform.claude.com/docs/en/build-with-claude/fallback-credit#when-a-retry-is-rejected).

<CodeGroup>
  ```bash cURL
  # Initial request (may be refused)
  response=$(curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: fallback-credit-2026-07-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-fable-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello, Claude"}]
    }')

  # A refusal carries a one-time credit token in stop_details
  token=$(jq -r '.stop_details.fallback_credit_token // empty' <<<"${response}")

  if [[ -n "${token}" ]]; then
    # Retry on the fallback model with the credit token (same body)
    response=$(curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "anthropic-beta: fallback-credit-2026-07-01" \
      -H "content-type: application/json" \
      -d "$(jq -n --arg token "${token}" '{
        model: "claude-opus-4-8",
        max_tokens: 1024,
        messages: [{"role": "user", "content": "Hello, Claude"}],
        fallback_credit_token: $token
      }')")
  fi

  # See the SDK examples for the full rejection-handling ladder.
  jq -c '{stop_reason, model}' <<<"${response}"

bash CLI
  # Initial request (may be refused)
  response=$(ant beta:messages create \
    --model claude-fable-5 \
    --max-tokens 1024 \
    --message '{"role":"user","content":"Hello, Claude"}' \
    --beta fallback-credit-2026-07-01 \
    --format json)

  # A refusal carries a one-time credit token in stop_details
  token=$(jq -r '.stop_details.fallback_credit_token // empty' <<<"${response}")

  if [[ -n "${token}" ]]; then
    # Retry on the fallback model with the credit token
    response=$(ant beta:messages create \
      --model claude-opus-4-8 \
      --max-tokens 1024 \
      --message '{"role":"user","content":"Hello, Claude"}' \
      --fallback-credit-token "${token}" \
      --beta fallback-credit-2026-07-01 \
      --format json)
  fi

  # See the SDK examples for the full rejection-handling ladder.
  jq -c '{stop_reason, model}' <<<"${response}"

python Python
  client = Anthropic()

  request = {
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello, Claude"}],
  }


  def send(model: str, body: dict[str, object]) -> BetaMessage:
      return client.beta.messages.create(
          model=model, betas=["fallback-credit-2026-07-01"], **body
      )


  response = send("claude-fable-5", request)

  if (
      response.stop_reason == "refusal"
      and (details := response.stop_details)
      and (token := details.fallback_credit_token)
  ):
      exact_body = request | {"fallback_credit_token": token}
      # Prefer the continuation shape unless the claim is False
      if details.fallback_has_prefill_claim is not False:
          echoed = [block.model_dump() for block in response.content]
          match echoed:
              case [*_, {"type": "text"} as final_block]:
                  final_block["text"] = final_block["text"].rstrip()
          attempt = exact_body | {
              "messages": [
                  *request["messages"],
                  {"role": "assistant", "content": echoed},
              ]
          }
      else:
          attempt = exact_body

      try:
          response = send("claude-opus-4-8", attempt)
      except BadRequestError as error:
          if "redemption temporarily unavailable" in error.message:
              raise  # Transient: retry with the token within its five-minute window
          try:
              # Fall back to the unchanged body, still with the token
              response = send("claude-opus-4-8", exact_body)
          except BadRequestError as retry_error:
              if "redemption temporarily unavailable" in retry_error.message:
                  raise  # Transient: retry with the token within its five-minute window
              # The token itself was rejected: forfeit it and retry without.
              response = send("claude-opus-4-8", request)

  print(json.dumps({"stop_reason": response.stop_reason, "model": response.model}))

typescript TypeScript
  const client = new Anthropic();

  const request: Anthropic.Beta.MessageCreateParamsNonStreaming = {
    model: "claude-fable-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }],
    betas: ["fallback-credit-2026-07-01"]
  };

  let response = await client.beta.messages.create(request);

  if (
    response.stop_reason === "refusal" &&
    response.stop_details?.type === "refusal" &&
    response.stop_details.fallback_credit_token
  ) {
    const { fallback_credit_token, fallback_has_prefill_claim } = response.stop_details;
    const fallbackModel = "claude-opus-4-8";

    const exactRetry: Anthropic.Beta.MessageCreateParamsNonStreaming = {
      ...request,
      model: fallbackModel,
      fallback_credit_token
    };

    // Richest shape first, degrading on each rejection: the continuation
    // shape (unless the claim is false), the unchanged body still carrying
    // the token, and finally forfeiting the token.
    let attempt = exactRetry;
    if (fallback_has_prefill_claim !== false) {
      const finalBlock = response.content.at(-1);
      const echoed: Anthropic.Beta.BetaContentBlockParam[] =
        finalBlock?.type === "text"
          ? [
              ...response.content.slice(0, -1),
              { ...finalBlock, text: finalBlock.text.trimEnd() }
            ]
          : response.content;
      attempt = {
        ...exactRetry,
        messages: [...request.messages, { role: "assistant", content: echoed }]
      };
    }

    try {
      response = await client.beta.messages.create(attempt);
    } catch (error) {
      // Degrade only on a shape-related 400. "redemption temporarily
      // unavailable" is transient: retry the same way within the token's
      // five-minute window instead.
      if (
        !(error instanceof Anthropic.BadRequestError) ||
        error.message.includes("redemption temporarily unavailable")
      ) {
        throw error;
      }
      try {
        response = await client.beta.messages.create(exactRetry);
      } catch (retryError) {
        if (
          !(retryError instanceof Anthropic.BadRequestError) ||
          retryError.message.includes("redemption temporarily unavailable")
        ) {
          throw retryError;
        }
        response = await client.beta.messages.create({ ...request, model: fallbackModel });
      }
    }
  }

  const { stop_reason, model } = response;
  console.log(JSON.stringify({ stop_reason, model }));

csharp C#
  var client = new AnthropicClient();
  const string beta = "fallback-credit-2026-07-01";

  List<BetaMessageParam> requestMessages =
  [
      new() { Role = Role.User, Content = "Hello, Claude" },
  ];
  MessageCreateParams Request(string model) => new()
  {
      Model = model,
      MaxTokens = 1024,
      Messages = requestMessages,
      Betas = [beta],
  };
  var response = await client.Beta.Messages.Create(Request("claude-fable-5"));

  if (
      response.StopReason == BetaStopReason.Refusal
      && response.StopDetails is { FallbackCreditToken: string token } details
  )
  {
      var exactBody = Request("claude-opus-4-8") with { FallbackCreditToken = token };
      var attempt = exactBody;
      // Prefer the continuation shape unless the claim is false
      if (details.FallbackHasPrefillClaim is not false)
      {
          var echoed = JsonArray.Create(response.RawData["content"])!;
          if (
              echoed is [.., JsonObject lastBlock]
              && lastBlock["type"]?.GetValue<string>() is "text"
              && lastBlock["text"]?.GetValue<string>() is string text
          )
          {
              lastBlock["text"] = text.TrimEnd();
          }
          attempt = exactBody with
          {
              Messages =
              [
                  .. requestMessages,
                  new()
                  {
                      Role = Role.Assistant,
                      Content = new BetaMessageParamContent(
                          JsonSerializer.SerializeToElement(echoed)
                      ),
                  },
              ],
          };
      }
      // A transient "redemption temporarily unavailable" rejection propagates out of
      // each of the following catch filters: retry with the token within its five-minute window.
      try
      {
          response = await client.Beta.Messages.Create(attempt);
      }
      catch (AnthropicBadRequestException e)
          when (!e.Message.Contains("redemption temporarily unavailable"))
      {
          try
          {
              // Fall back to the unchanged body, still with the token
              response = await client.Beta.Messages.Create(exactBody);
          }
          catch (AnthropicBadRequestException retryError)
              when (!retryError.Message.Contains("redemption temporarily unavailable"))
          {
              // The token itself was rejected: forfeit it and retry without.
              response = await client.Beta.Messages.Create(Request("claude-opus-4-8"));
          }
      }
  }

  Console.WriteLine(
      JsonSerializer.Serialize(
          new { stop_reason = response.StopReason?.Raw(), model = response.Model.Raw() }
      )
  );

go Go
  ctx := context.Background()
  client := anthropic.NewClient()

  request := anthropic.BetaMessageNewParams{
  	MaxTokens: 1024,
  	Betas:     []anthropic.AnthropicBeta{anthropic.AnthropicBetaFallbackCredit2026_07_01},
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude")),
  	},
  }

  send := func(model anthropic.Model, body anthropic.BetaMessageNewParams) (*anthropic.BetaMessage, error) {
  	body.Model = model
  	return client.Beta.Messages.New(ctx, body)
  }
  // A non-transient 400 means this attempt shape or token was rejected and
  // the next rung of the ladder should run. "redemption temporarily
  // unavailable" is transient: surface it and retry with the token within
  // its five-minute window.
  canFallBack := func(err error) bool {
  	apiErr, ok := errors.AsType[*anthropic.Error](err)
  	return ok && apiErr.StatusCode == 400 &&
  		!strings.Contains(apiErr.Error(), "redemption temporarily unavailable")
  }

  response, err := send(anthropic.ModelClaudeFable5, request)
  if err != nil {
  	log.Fatal(err)
  }

  if response.StopReason == anthropic.BetaStopReasonRefusal {
  	details := response.StopDetails
  	if token := details.FallbackCreditToken; token != "" {
  		exactBody := request
  		exactBody.FallbackCreditToken = anthropic.BetaMessageNewParamsFallbackCreditTokenUnion{
  			OfString: anthropic.String(token),
  		}
  		attempt := exactBody
  		// Prefer the continuation shape unless the claim is false
  		if details.FallbackHasPrefillClaim || !details.JSON.FallbackHasPrefillClaim.Valid() {
  			echoed := response.ToParam()
  			if len(echoed.Content) > 0 {
  				if text := echoed.Content[len(echoed.Content)-1].OfText; text != nil {
  					text.Text = strings.TrimRightFunc(text.Text, unicode.IsSpace)
  				}
  			}
  			attempt.Messages = append(slices.Clone(request.Messages), echoed)
  		}
  		response, err = send(anthropic.ModelClaudeOpus4_8, attempt)
  		if err != nil && canFallBack(err) {
  			// Fall back to the unchanged body, still with the token
  			response, err = send(anthropic.ModelClaudeOpus4_8, exactBody)
  			if err != nil && canFallBack(err) {
  				// The token itself was rejected: forfeit it and retry without.
  				response, err = send(anthropic.ModelClaudeOpus4_8, request)
  			}
  		}
  		if err != nil {
  			log.Fatal(err)
  		}
  	}
  }

  summary, err := json.Marshal(struct {
  	StopReason anthropic.BetaStopReason `json:"stop_reason"`
  	Model      anthropic.Model          `json:"model"`
  }{response.StopReason, response.Model})
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(string(summary))

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  MessageCreateParams.Builder request() {
      return MessageCreateParams.builder()
          .maxTokens(1024L)
          .addUserMessage("Hello, Claude")
          .addBeta(AnthropicBeta.FALLBACK_CREDIT_2026_07_01);
  }

  BetaMessage send(Model model, MessageCreateParams.Builder body) {
      return client.beta().messages().create(body.model(model).build());
  }

  void main() {
      BetaMessage response = send(Model.CLAUDE_FABLE_5, request());

      if (response.stopReason().map(BetaStopReason.REFUSAL::equals).orElse(false)
              && response.stopDetails().orElse(null) instanceof BetaRefusalStopDetails details
              && details.fallbackCreditToken().orElse(null) instanceof String creditToken) {
          MessageCreateParams.Builder attempt = request().fallbackCreditToken(creditToken);
          // Prefer the continuation shape unless the claim is false
          if (details.fallbackHasPrefillClaim().orElse(true)) {
              List<BetaContentBlockParam> echoed = new ArrayList<>(
                  response.content().stream().map(BetaContentBlock::toParam).toList());
              if (!echoed.isEmpty() && echoed.getLast().isText()) {
                  var lastText = echoed.removeLast().asText();
                  echoed.addLast(BetaContentBlockParam.ofText(
                      lastText.toBuilder().text(lastText.text().stripTrailing()).build()));
              }
              attempt.addAssistantMessageOfBetaContentBlockParams(echoed);
          }
          try {
              response = send(Model.CLAUDE_OPUS_4_8, attempt);
          } catch (BadRequestException badRequest) {
              // Transient: retry with the token within its five-minute window
              if (badRequest.getMessage().contains("redemption temporarily unavailable")) {
                  throw badRequest;
              }
              try {
                  // Fall back to the unchanged body, still with the token
                  response = send(Model.CLAUDE_OPUS_4_8, request().fallbackCreditToken(creditToken));
              } catch (BadRequestException retryBadRequest) {
                  if (retryBadRequest.getMessage().contains("redemption temporarily unavailable")) {
                      throw retryBadRequest;
                  }
                  // The token itself was rejected: forfeit it and retry without.
                  response = send(Model.CLAUDE_OPUS_4_8, request());
              }
          }
      }

      IO.println("""
          {"stop_reason": "%s", "model": "%s"}"""
          .formatted(response.stopReason().orElseThrow(), response.model()));
  }

php PHP
  $client = new Client();
  $beta = 'fallback-credit-2026-07-01';
  $messages = [['role' => 'user', 'content' => 'Hello, Claude']];

  $send = fn (string $model, array $messages, ?string $token = null) => $client->beta->messages->create(
      maxTokens: 1024,
      messages: $messages,
      model: $model,
      fallbackCreditToken: $token,
      betas: [$beta],
  );
  $response = $send('claude-fable-5', $messages);

  $token = $response->stopReason === 'refusal'
      ? $response->stopDetails?->fallbackCreditToken
      : null;

  if ($token !== null) {
      $attemptMessages = $messages;
      // Prefer the continuation shape unless the claim is false
      if ($response->stopDetails->fallbackHasPrefillClaim !== false) {
          $echoed = $response->content
              |> json_encode(...)
              |> (fn (string $json): array => json_decode($json, associative: true));
          $lastIndex = array_key_last($echoed);
          if ($lastIndex !== null && $echoed[$lastIndex]['type'] === 'text') {
              $echoed[$lastIndex]['text'] = rtrim($echoed[$lastIndex]['text']);
          }
          $attemptMessages[] = ['role' => 'assistant', 'content' => $echoed];
      }
      // Transient: retry with the token within its five-minute window
      $isTransientRedemption = fn (BadRequestException $error): bool =>
          str_contains($error->getMessage(), 'redemption temporarily unavailable');
      try {
          $response = $send('claude-opus-4-8', $attemptMessages, $token);
      } catch (BadRequestException $error) {
          if ($isTransientRedemption($error)) {
              throw $error;
          }
          try {
              // Fall back to the unchanged body, still with the token
              $response = $send('claude-opus-4-8', $messages, $token);
          } catch (BadRequestException $retryError) {
              if ($isTransientRedemption($retryError)) {
                  throw $retryError;
              }
              // The token itself was rejected: forfeit it and retry without.
              $response = $send('claude-opus-4-8', $messages);
          }
      }
  }

  echo json_encode(['stop_reason' => $response->stopReason, 'model' => $response->model]), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  request = {
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}]
  }

  send_message = ->(model, body) do
    client.beta.messages.create(model:, betas: ["fallback-credit-2026-07-01"], **body)
  end

  response = send_message.call("claude-fable-5", request)

  if response in {stop_reason: :refusal,
                  stop_details: {fallback_credit_token: String => credit_token} => details}
    exact_body = request.merge(fallback_credit_token: credit_token)

    # Prefer the continuation shape unless the claim is false
    attempt = if details.fallback_has_prefill_claim != false
      echoed = response.content.map(&:to_h)
      if echoed.last in {type: :text, text: String => final_text}
        echoed[-1] = echoed.last.merge(text: final_text.rstrip)
      end
      exact_body.merge(
        messages: [*request[:messages], {role: "assistant", content: echoed}]
      )
    else
      exact_body
    end

    begin
      response = send_message.call("claude-opus-4-8", attempt)
    rescue Anthropic::Errors::BadRequestError => error
      # Transient: retry with the token within its five-minute window
      raise if error.message.include?("redemption temporarily unavailable")
      begin
        # Fall back to the unchanged body, still with the token
        response = send_message.call("claude-opus-4-8", exact_body)
      rescue Anthropic::Errors::BadRequestError => error
        # Transient: retry with the token within its five-minute window
        raise if error.message.include?("redemption temporarily unavailable")
        # The token itself was rejected: forfeit it and retry without.
        response = send_message.call("claude-opus-4-8", request)
      end
    end
  end

  puts JSON.generate({stop_reason: response.stop_reason, model: response.model})
  ```
</CodeGroup>


## Where it works

Source: https://platform.claude.com/llms-full.txt#where-it-works

Fallback credit is in beta on the Claude API, Amazon Bedrock, Claude Platform on AWS, Google Cloud, and Microsoft Foundry. Refusals in [Message Batches](https://platform.claude.com/docs/en/build-with-claude/batch-processing) don't mint credit tokens, and redemption applies only to direct Messages API requests: a token passed on a batch request is accepted but ignored.

The retry model must be one of the refused model's permitted fallback targets. For Claude Fable 5.1 and Claude Fable 5, those are Claude Opus 4.8 (`claude-opus-4-8`) and Claude Opus 5 (`claude-opus-5`).

<Accordion title="Looking up permitted fallback targets programmatically">
  On the Claude API and Claude Platform on AWS, the target list is published as `allowed_fallback_models` on each model's entry in the [Models API](https://platform.claude.com/docs/en/api/models/list) when the `server-side-fallback-2026-07-01` beta header is set. The list is not yet visible under the `fallback-credit-*` header alone. It is not exposed on Amazon Bedrock, Google Cloud, or Microsoft Foundry.
</Accordion>


## Checking that the credit applied

Source: https://platform.claude.com/llms-full.txt#checking-that-the-credit-applied

The refund is visible in the retry's `usage`. Compared with what the same request would report without the token, `cache_creation_input_tokens` is lower, and `cache_read_input_tokens` is higher by the same amount. A shift of zero means the token was honored but there was nothing to reprice, for example because the retry model's cache was already warm.


## When a retry is rejected

Source: https://platform.claude.com/llms-full.txt#when-a-retry-is-rejected

Most retries redeem on the first attempt. When one does not, the API returns a 400 error that tells you what to try next.

<Steps>
  <Step title="Continuation rejected: resend the unchanged body">
    If the retry that appends the assistant message is rejected with a 400 error, resend the refused request body unchanged, still with the token.
  </Step>

  <Step title="Token rejected: drop the token">
    If the unchanged body is also rejected with a 400 error whose message names `fallback_credit_token`, retry without the token. The credit is forfeited, but the retry itself goes through.
  </Step>
</Steps>

<Note>
  If the refused request executed server tools, a tokenless retry re-runs and re-bills those tools. In that case, surface the 400 error to your caller instead of falling through to a tokenless retry.
</Note>

<Accordion title="If the error says 'redemption temporarily unavailable'">
  This rejection is transient, not a verdict on your retry shape. Retry the same request, with the same token, within the token's five-minute window. Do not move to the next step of the ladder.
</Accordion>


## Reference

Source: https://platform.claude.com/llms-full.txt#reference

The following sections cover edge cases and the complete redemption rules. Most integrations do not need them.

<Accordion title="Fields that must match the refused request">
  Redemption compares the retry against the refused request. Every field that shapes the prompt must match exactly. Fields that do not shape the prompt may change on the retry.

  | Rule                    | Fields                                                                                                                                                                      |
  | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Must match exactly      | `system`, `messages`, `tools`, `tool_choice`, `thinking`, and `cache_control`, plus `output_config`, `mcp_servers`, `context_management`, and `container` when you use them |
  | May change on the retry | `model`, `max_tokens`, `stop_sequences`, `temperature`, `top_p`, `top_k`, `stream`, `metadata`, and `service_tier`                                                          |

  The continuation shape (`fallback_has_prefill_claim: true`) is the one exception to the `messages` match: it adds exactly one assistant message at the end of `messages`.

  Do not strip `thinking` or `redacted_thinking` blocks from earlier turns on the retry, even though a plain retry without a token usually strips them. The body must match the refused request, and the server handles those blocks itself.
</Accordion>

<Accordion title="Beta headers must match too">
  Send the same `anthropic-beta` headers on the retry as on the refused request. A beta header present on one of the two requests but not the other can fail the match even when the bodies are identical. The resulting 400 error carries the same `request body ... does not match` message as a body difference, so a header difference is easy to misread as a body problem. In particular, do not add or drop beta headers based on which model the request targets.

  Two header families are exempt from the match, for the retry's sake:

  * **`server-side-fallback-*`:** a retry must drop the `fallbacks` parameter, and dropping this header along with it does not cause a mismatch.
  * **`fallback-credit-*`:** keep this header on both requests. The retry needs it to redeem the token.

  <Note>
    On models that include the 1M token context window by default, such as Claude Fable 5.1, Claude Fable 5, Claude Opus 5, and Claude Opus 4.8, the `context-1m-2025-08-07` beta header has no effect. To keep the two requests identical, omit that header on both rather than sending it on one and not the other.
  </Note>
</Accordion>

<Accordion title="When fallback_has_prefill_claim is absent">
  The field is `null` only when the token is also `null`, so a value you observe while holding a token is never `null`. It can still be absent (`None` in the typed SDKs) on Amazon Bedrock, Google Cloud, and Microsoft Foundry while their support for the field rolls out. In that case, treat the retry shape as unknown rather than as `false`. Try the appended-assistant-message shape first, and rely on the rejection handling in [When a retry is rejected](https://platform.claude.com/docs/en/build-with-claude/fallback-credit#when-a-retry-is-rejected), which falls back to the unchanged body.
</Accordion>

<Accordion title="Echoing the refused response's content">
  When a refusal's token supports the continuation shape, the response `content` carries only the model's own output, and the refusal explanation is delivered in `stop_details.explanation`. You can therefore echo `content` into the appended assistant message as-is.

  Two adjustments may still be needed before sending:

  * If the final block you send is a `text` block, strip its trailing whitespace.
  * Omit any client-side `tool_use` block that has no matching `tool_result`.

  If the echoed content includes a `fallback` block from an earlier [server-side fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#server-side-fallback), keep the block exactly where it appeared. It is accepted on any request without a beta header. The API uses its position to validate the thinking blocks around it, so a request that echoes thinking blocks from both sides of that boundary is rejected if the block is omitted or moved.
</Accordion>

<Accordion title="Token scope and lifetime">
  The token redeems only from the organization and workspace that received the refusal, including on Microsoft Foundry. On Amazon Bedrock and Google Cloud, which do not have workspaces, the token is bound to the platform's caller identity instead.

  The token expires five minutes after the refusal. After that, send the retry without it. The token is also stateless: the server stores nothing about it, and there is no endpoint to inspect or revoke it.
</Accordion>

<Accordion title="When a token cannot be redeemed by either shape">
  When the refusal arrived after server tools had already executed within the request, the token redeems only by continuing the partial response. That restriction is what prevents the completed tool calls from running, and billing, again.

  One combination can therefore leave the token unredeemable by either shape, when both of the following are true:

  * The request used `output_config.format` or a `tool_choice` that forces tool use. Either one rules out the appended-assistant-message shape.
  * The refusal arrived after server tools had executed. That rules out the unchanged body.

  If the unchanged-body retry is rejected with a 400 error saying the token must be redeemed by continuing the partial response, discard the token. A retry without it goes through, but it re-runs and re-bills the completed server tools. Surface the cost or the error to your caller rather than retrying silently.
</Accordion>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-3

<CardGroup>
  <Card title="Refusals and fallback" icon="shield" href="https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback">
    Detect refusals and choose between server-side fallback, the SDK middleware, and a manual retry.
  </Card>

  <Card title="Prompt caching" icon="bolt" href="https://platform.claude.com/docs/en/build-with-claude/prompt-caching">
    How cache reads and cache writes are billed.
  </Card>

  <Card title="Stop reasons and fallback" icon="code" href="https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons">
    Every `stop_reason` value and how to handle it.
  </Card>

  <Card title="SDK middleware" icon="settings" href="https://platform.claude.com/docs/en/cli-sdks-libraries/middleware">
    The SDK helper that applies fallback credit automatically.
  </Card>
</CardGroup>


---
title: Refusals and fallback
url: https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback
description: How Claude Fable and Claude Opus models return classifier refusals and how to retry refused requests on a fallback model.
---

Claude Fable 5.1, Claude Fable 5, and Claude Opus 5 include safety classifiers that can decline a request. When that happens, you receive a normal response, not an error, with `stop_reason: "refusal"`. Its `stop_details.category` names the policy area (see [What a refusal looks like](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#refusal-response)). You can usually still get an answer by sending the same request to another Claude model. This page shows you how to recognize a refusal and how to set up that retry.

Read this page when you build on any of these models and want declined requests to fall through to another model automatically. It also applies when you have seen `"refusal"` in a response and want to know what to do next.

Related pages:

* [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons): the full list of `stop_reason` values.
* [Fallback credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit): how to avoid paying the prompt-cache cost twice when you build the retry yourself.
* [SDK middleware](https://platform.claude.com/docs/en/cli-sdks-libraries/middleware): the SDK helper that wraps all of this.
* [Fallback and billing cookbook](https://platform.claude.com/cookbook/fable-5-fallback-billing-guide): a worked end-to-end example.

The simplest setup, in beta on the Claude API: set `fallbacks` to `"default"`, and the API retries a declined request on the fallback model Anthropic recommends for its refusal category. For categories with no recommended fallback, the refusal stands.

<CodeGroup>
  ```bash cURL
  curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: server-side-fallback-2026-07-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-fable-5",
      "max_tokens": 1024,
      "fallbacks": "default",
      "messages": [{"role": "user", "content": "Hello, Claude"}]
    }' | jq -r '.model'

bash CLI
  ant beta:messages create \
    --model claude-fable-5 \
    --max-tokens 1024 \
    --message '{"role":"user","content":"Hello, Claude"}' \
    --fallbacks default \
    --beta server-side-fallback-2026-07-01 \
    --transform model --raw-output

python Python
  client = Anthropic()

  response = client.beta.messages.create(
      model="claude-fable-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
      fallbacks="default",
      betas=["server-side-fallback-2026-07-01"],
  )
  print(response.model)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.beta.messages.create({
    model: "claude-fable-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }],
    fallbacks: "default",
    betas: ["server-side-fallback-2026-07-01"]
  });
  console.log(response.model);

csharp C#
  AnthropicClient client = new();

  BetaMessage response = await client.Beta.Messages.Create(
      new()
      {
          Model = Messages::Model.ClaudeFable5,
          MaxTokens = 1024,
          Messages = [new() { Content = "Hello, Claude", Role = Role.User }],
          Fallbacks = new Default(),
          Betas = [AnthropicBeta.ServerSideFallback2026_07_01],
      }
  );

  Console.WriteLine(response.Model.Raw());

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.Background(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeFable5,
  	MaxTokens: 1024,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude")),
  	},
  	Fallbacks: anthropic.BetaFallbacksParamOfDefault(),
  	Betas:     []anthropic.AnthropicBeta{anthropic.AnthropicBetaServerSideFallback2026_07_01},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Println(response.Model)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  BetaMessage response = client.beta().messages().create(MessageCreateParams.builder()
      .model(Model.CLAUDE_FABLE_5)
      .maxTokens(1024L)
      .addUserMessage("Hello, Claude")
      .fallbacksDefault()
      .addBeta(AnthropicBeta.SERVER_SIDE_FALLBACK_2026_07_01)
      .build());

  IO.println(response.model().asString());

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      model: 'claude-fable-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
      fallbacks: 'default',
      betas: ['server-side-fallback-2026-07-01'],
  );

  echo $response->model, PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-fable-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}],
    fallbacks: :default,
    betas: ["server-side-fallback-2026-07-01"]
  )

  puts response.model
  ```
</CodeGroup>

The following sections cover what a refusal response contains, when to use server-side or client-side fallback, and how each is billed.


## What a refusal looks like

Source: https://platform.claude.com/llms-full.txt#what-a-refusal-looks-like

A refusal is a successful HTTP 200 response with `stop_reason: "refusal"`:

The `stop_details` object explains the decline:

* **`category`:** names the policy area that triggered the classifier.
* **`explanation`:** a human-readable description. The text is not stable, so display it rather than parse it.
* **`recommended_model`:** present only on requests that set `fallbacks` ([server-side fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#server-side-fallback), beta). It names a model to retry directly when the API skipped the fallback attempt (for example, the fallback model was rate limited), and is `null` otherwise. It's a hint, not a guarantee.
* `category` and `explanation` are both `null` when the refusal does not map to a named category. That `null` is a normal, permanent value, not a placeholder.
* `stop_details` itself is `null` for every stop reason other than `refusal`.

| `category`               | What it means                                                                                                                                                                                                                             |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `"cyber"`                | The request could enable cyber harm, such as malware or exploit development. Benign cybersecurity work can also trigger this category.                                                                                                    |
| `"bio"`                  | The request could enable biological harm, such as dangerous lab methods. Beneficial life sciences work can also trigger this category.                                                                                                    |
| `"frontier_llm"`         | The request could assist the development of competing AI models, which is restricted under [Anthropic's commercial terms](https://www.anthropic.com/legal/commercial-terms). Benign machine learning work can also trigger this category. |
| `"reasoning_extraction"` | The request asks the model to reproduce its internal reasoning in the response text. To get reasoning in a structured form instead, use [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking).              |
| `"general_harms"`        | The request falls under a usage-policy area outside the four named categories. Benign work can also trigger this category.                                                                                                                |

A refusal can arrive before any output, or mid-stream after partial output. In either case, treat any partial output as incomplete and discard it.

<Note>
  **How refusals are billed:** You are not billed for a refusal that arrives before any output. `content` is empty, and token counts appear in `usage` but are not charged. The request still counts against your rate limits. A mid-stream refusal bills the input tokens and the output already streamed at normal rates.
</Note>


## Picking a fallback approach

Source: https://platform.claude.com/llms-full.txt#picking-a-fallback-approach

There are three ways to retry a refused request on another model. The right one depends on where you are running and how much control you need.

| Your situation                       | Use                                                                                                                                                                                                      | Why                                                         |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Claude API, simplest setup           | [Server-side fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#server-side-fallback)                                                                                 | One request, one response. The API handles the retry.       |
| Any platform, using an Anthropic SDK | [The SDK middleware](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#client-side-fallback)                                                                                   | Configure once on the client. Retries happen automatically. |
| Raw HTTP or custom retry logic       | [A manual retry](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#manual-retry) with [fallback credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit) | Full control. Fallback credit keeps the cost down.          |

Server-side fallback and the SDK middleware apply fallback credit for you. You only need the [Fallback credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit) page when you build the retry yourself.


## Server-side fallback

Source: https://platform.claude.com/llms-full.txt#server-side-fallback

Server-side fallback retries a refused request inside a single API call. In the default mode, when the primary model declines and the refusal category has a recommended fallback, the API runs the same request on the model Anthropic recommends for that category. You can instead [name up to three fallback models of your own](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#naming-your-own-fallback-models). Either way, you get back one response that names the model that answered, so your user gets an answer in one round trip.

<Note>
  Server-side fallback is in beta on the Claude API. The `fallbacks` parameter is not supported on the [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing) (a batch item that includes it comes back as an errored result) and is not available on Amazon Bedrock, Google Cloud, or Microsoft Foundry. On those platforms, use [client-side fallback with the SDK middleware](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#client-side-fallback) instead.
</Note>

### Making the request

Set the `fallbacks` parameter to the string `"default"` and send the `server-side-fallback-2026-07-01` beta header. The API then applies the requested model's server-defined default routing, which selects a recommended fallback model based on the refusal category the classifier reports, so refused requests are served without you maintaining a model list as recommendations change.

Default routing never draws the up-front [oversized-image rejection](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#oversized-image-error) for models you did not choose: a routed model that would resize an image marked `"oversized_image": "error"` is dropped from the routing instead, so a marked image is never served resized.

<CodeGroup>
  ```bash cURL
  curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: server-side-fallback-2026-07-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-fable-5",
      "max_tokens": 1024,
      "fallbacks": "default",
      "messages": [{"role": "user", "content": "Hello, Claude"}]
    }' |
    jq -c '{
      stop_reason,
      model,
      # A fallback_message entry in usage.iterations means a fallback model ran;
      # pair it with stop_reason to confirm the fallback served the response.
      served_by_fallback: (
        any(.usage.iterations[]?; .type == "fallback_message")
        and .stop_reason != "refusal"
      )
    }'

bash CLI
  ant beta:messages create \
    --model claude-fable-5 \
    --max-tokens 1024 \
    --message '{"role":"user","content":"Hello, Claude"}' \
    --fallbacks default \
    --beta server-side-fallback-2026-07-01 \
    --format json |
    jq -c '{
      stop_reason,
      model,
      # A fallback_message entry in usage.iterations means a fallback model ran;
      # pair it with stop_reason to confirm the fallback served the response.
      served_by_fallback: (
        any(.usage.iterations[]?; .type == "fallback_message")
        and .stop_reason != "refusal"
      )
    }'

python Python
  client = Anthropic()

  response = client.beta.messages.create(
      model="claude-fable-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
      fallbacks="default",
      betas=["server-side-fallback-2026-07-01"],
  )

  # A fallback_message entry in usage.iterations means a fallback model ran;
  # pair it with stop_reason to confirm the fallback served the response.
  fallback_ran = any(
      iteration.type == "fallback_message"
      for iteration in response.usage.iterations or []
  )
  served_by_fallback = fallback_ran and response.stop_reason != "refusal"

  print(
      json.dumps(
          {
              "stop_reason": response.stop_reason,
              "model": response.model,
              "served_by_fallback": served_by_fallback,
          }
      )
  )

typescript TypeScript
  const client = new Anthropic();

  const response = await client.beta.messages.create({
    model: "claude-fable-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }],
    fallbacks: "default",
    betas: ["server-side-fallback-2026-07-01"]
  });

  // A fallback_message entry in usage.iterations means a fallback model ran;
  // pair it with stop_reason to confirm the fallback served the response.
  const { stop_reason, model, usage } = response;
  const servedByFallback =
    (usage.iterations ?? []).some((entry) => entry.type === "fallback_message") &&
    stop_reason !== "refusal";

  console.log(
    JSON.stringify({
      stop_reason,
      model,
      served_by_fallback: servedByFallback
    })
  );

csharp C#
  AnthropicClient client = new();

  var response = await client.Beta.Messages.Create(
      new()
      {
          Model = Messages::Model.ClaudeFable5,
          MaxTokens = 1024,
          Messages =
          [
              new() { Content = "Hello, Claude", Role = Role.User },
          ],
          Fallbacks = new Default(),
          Betas = [AnthropicBeta.ServerSideFallback2026_07_01],
      }
  );

  // A fallback_message entry in usage.iterations means a fallback model ran;
  // pair it with stop_reason to confirm the fallback served the response.
  bool fallbackRan = (response.Usage.Iterations ?? []).Any(iteration =>
      iteration.TryPickBetaFallbackMessageIterationUsage(out _)
  );
  bool servedByFallback =
      fallbackRan && response.StopReason?.Value() != BetaStopReason.Refusal;

  Console.WriteLine(
      JsonSerializer.Serialize(
          new
          {
              stop_reason = response.StopReason?.Raw(),
              model = response.Model.Raw(),
              served_by_fallback = servedByFallback,
          }
      )
  );

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.Background(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeFable5,
  	MaxTokens: 1024,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude")),
  	},
  	Fallbacks: anthropic.BetaFallbacksParamOfDefault(),
  	Betas:     []anthropic.AnthropicBeta{anthropic.AnthropicBetaServerSideFallback2026_07_01},
  })
  if err != nil {
  	panic(err)
  }

  // A fallback_message entry in usage.iterations means a fallback model ran;
  // pair it with stop_reason to confirm the fallback served the response.
  fallbackRan := slices.ContainsFunc(
  	response.Usage.Iterations,
  	func(iteration anthropic.BetaIterationsUsageItemUnion) bool {
  		_, isFallback := iteration.AsAny().(anthropic.BetaFallbackMessageIterationUsage)
  		return isFallback
  	},
  )
  servedByFallback := fallbackRan && response.StopReason != anthropic.BetaStopReasonRefusal

  summary, err := json.Marshal(struct {
  	StopReason       anthropic.BetaStopReason `json:"stop_reason"`
  	Model            anthropic.Model          `json:"model"`
  	ServedByFallback bool                     `json:"served_by_fallback"`
  }{response.StopReason, response.Model, servedByFallback})
  if err != nil {
  	panic(err)
  }
  fmt.Println(string(summary))

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  BetaMessage response = client.beta().messages().create(
      MessageCreateParams.builder()
          .model(Model.CLAUDE_FABLE_5)
          .maxTokens(1024L)
          .addUserMessage("Hello, Claude")
          .fallbacksDefault()
          .addBeta(AnthropicBeta.SERVER_SIDE_FALLBACK_2026_07_01)
          .build()
  );

  // A fallback_message usage entry means a fallback model produced the
  // response; a refusal stop reason means no model served it.
  List<BetaUsage.Iteration> iterations =
      response.usage().iterations().orElse(List.of());
  boolean servedByFallback =
      iterations.stream().anyMatch(BetaUsage.Iteration::isFallbackMessage)
          && response.stopReason().filter(BetaStopReason.REFUSAL::equals).isEmpty();

  IO.println("""
      {"stop_reason":"%s","model":"%s","served_by_fallback":%b}\
      """.formatted(
          response.stopReason().map(BetaStopReason::asString).orElse("null"),
          response.model().asString(),
          servedByFallback));

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
      model: 'claude-fable-5',
      fallbacks: 'default',
      betas: ['server-side-fallback-2026-07-01'],
  );

  // A fallback_message entry in usage.iterations means a fallback model ran;
  // pair it with stop_reason to confirm the fallback served the response.
  $iterations = $response->usage->iterations ?? [];
  $servedByFallback = array_any($iterations, fn($entry) => $entry->type === 'fallback_message')
      && $response->stopReason !== 'refusal';

  echo json_encode([
      'stop_reason' => $response->stopReason,
      'model' => $response->model,
      'served_by_fallback' => $servedByFallback,
  ]), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-fable-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}],
    fallbacks: :default,
    betas: ["server-side-fallback-2026-07-01"]
  )

  # A fallback_message entry in usage.iterations means a fallback model ran;
  # pair it with stop_reason to confirm the fallback served the response.
  iterations = response.usage.iterations || []
  served_by_fallback = iterations.any? { it.type == :fallback_message } &&
    response.stop_reason != :refusal

  stop_reason = response.stop_reason
  model = response.model
  puts JSON.generate({stop_reason:, model:, served_by_fallback:})

bash cURL
  curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: server-side-fallback-2026-07-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-fable-5",
      "max_tokens": 1024,
      "fallbacks": [{"model": "claude-opus-4-8"}],
      "messages": [{"role": "user", "content": "Hello, Claude"}]
    }' | jq -r '.model'

bash CLI
  ant beta:messages create \
    --model claude-fable-5 \
    --max-tokens 1024 \
    --message '{"role":"user","content":"Hello, Claude"}' \
    --fallbacks '[{"model":"claude-opus-4-8"}]' \
    --beta server-side-fallback-2026-07-01 \
    --transform model --raw-output

python Python
  client = Anthropic()

  response = client.beta.messages.create(
      model="claude-fable-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
      fallbacks=[{"model": "claude-opus-4-8"}],
      betas=["server-side-fallback-2026-07-01"],
  )
  print(response.model)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.beta.messages.create({
    model: "claude-fable-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }],
    fallbacks: [{ model: "claude-opus-4-8" }],
    betas: ["server-side-fallback-2026-07-01"]
  });
  console.log(response.model);

csharp C#
  AnthropicClient client = new();

  BetaMessage response = await client.Beta.Messages.Create(
      new()
      {
          Model = Messages::Model.ClaudeFable5,
          MaxTokens = 1024,
          Messages = [new() { Content = "Hello, Claude", Role = Role.User }],
          Fallbacks = new([new(Messages::Model.ClaudeOpus4_8)]),
          Betas = [AnthropicBeta.ServerSideFallback2026_07_01],
      }
  );

  Console.WriteLine(response.Model.Raw());

go Go
  client := anthropic.NewClient()

  response, err := client.Beta.Messages.New(context.Background(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeFable5,
  	MaxTokens: 1024,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude")),
  	},
  	Fallbacks: anthropic.BetaFallbacksParamUnion{
  		OfBetaFallbackArray: []anthropic.BetaFallbackParam{{Model: anthropic.ModelClaudeOpus4_8}},
  	},
  	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaServerSideFallback2026_07_01},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Println(response.Model)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  BetaMessage response = client.beta().messages().create(MessageCreateParams.builder()
      .model(Model.CLAUDE_FABLE_5)
      .maxTokens(1024L)
      .addUserMessage("Hello, Claude")
      .fallbacksOfFallbackParams(List.of(BetaFallbackParam.builder()
          .model(Model.CLAUDE_OPUS_4_8)
          .build()))
      .addBeta(AnthropicBeta.SERVER_SIDE_FALLBACK_2026_07_01)
      .build());

  IO.println(response.model().asString());

php PHP
  $client = new Client();

  $response = $client->beta->messages->create(
      model: 'claude-fable-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
      fallbacks: [['model' => 'claude-opus-4-8']],
      betas: ['server-side-fallback-2026-07-01'],
  );

  echo $response->model, PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  response = client.beta.messages.create(
    model: "claude-fable-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}],
    fallbacks: [{model: "claude-opus-4-8"}],
    betas: ["server-side-fallback-2026-07-01"]
  )

  puts response.model

json
{
  "id": "msg_01XFUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "model": "claude-opus-4-8",
  "content": [
    {
      "type": "fallback",
      "from": { "model": "claude-fable-5" },
      "to": { "model": "claude-opus-4-8" }
    },
    { "type": "text", "text": "Hi! How can I help you today?" }
  ],
  "stop_reason": "end_turn",
  "stop_details": null,
  "usage": {
    "input_tokens": 412,
    "output_tokens": 264,
    "cache_read_input_tokens": 0,
    "cache_creation_input_tokens": 0,
    "iterations": [
      {
        "type": "message",
        "model": "claude-fable-5",
        "input_tokens": 535,
        "output_tokens": 0,
        "cache_read_input_tokens": 0,
        "cache_creation_input_tokens": 0
      },
      {
        "type": "fallback_message",
        "model": "claude-opus-4-8",
        "input_tokens": 412,
        "output_tokens": 264,
        "cache_read_input_tokens": 0,
        "cache_creation_input_tokens": 0
      }
    ]
  }
}
```

The `usage.iterations` array records every attempt. A model that declined appears as an ordinary `message` entry, and the model that served the turn appears as a `fallback_message` entry. If every model in the chain declines, the response is the last model's refusal, with a `message` entry for each earlier hop and a `fallback_message` entry for the last.

[Sticky routing](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#sticky-routing) can send a later turn straight to the fallback model. Such a turn carries no `fallback` content block, because no model declined that turn. Identify it by the `fallback_message` entry in `usage.iterations`, the absence of a `message` entry for the requested model, and the response's `model` field.

### Continuing the conversation

On the next turn, send the assistant content back as you received it. After a mid-output fallback, `content` can include block types the declining model produced before the handoff. The following table covers which to keep and which to drop when you echo the turn.

| Block type                                                                             | On the next turn                                                                                                                                                                                                               |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `fallback`                                                                             | Keep it exactly where it appeared. The API uses its position to validate the thinking blocks around it, so a request that echoes thinking blocks from both sides of the boundary is rejected if the block is omitted or moved. |
| `text`                                                                                 | Keep.                                                                                                                                                                                                                          |
| Any block after the final `fallback` block                                             | Keep.                                                                                                                                                                                                                          |
| `thinking`, `redacted_thinking`, or `connector_text` before the final `fallback` block | Drop.                                                                                                                                                                                                                          |
| Client-side `tool_use` before the final `fallback` block                               | Drop.                                                                                                                                                                                                                          |
| `server_tool_use` before the final `fallback` block                                    | Keep when paired with its result. Drop when it has no matching result.                                                                                                                                                         |

<Note>
  A `connector_text` block carries narration text that some tool-using responses include between tool calls.
</Note>

### Streaming

On a streaming request, the retry happens on the same stream, and nothing you have already received is invalidated. What you see depends on when the decline happens.

**When the decline happens before any output:**

* `message_start` names the fallback model, and the `fallback` block is the first content block.
* Because `message_start` waits for the fallback attempt to start, time to first byte includes the declined attempt.

**When the decline happens mid-output:**

* The open content block closes, and the `fallback` block (an ordinary `content_block_start` and `content_block_stop` pair with no deltas) marks the boundary.
* The fallback model continues from the partial output. Only the partial output's `text` blocks are passed to the fallback model as context. Other block types remain in `content`.
* `message_start` already named the requested model, so read the serving model from the `fallback` block's `to.model` and from the `fallback_message` entry in the final `message_delta`'s `usage.iterations`.

### Non-streaming responses

On a non-streaming request, a mid-output decline behaves differently: the response omits the declined model's partial output, and the fallback model answers from scratch. The result looks like a decline before any output, with the `fallback` block first. The declined attempt and its output tokens still appear in `usage.iterations`.

<Note>
  **Declines during tool use:** completed tool work does not block fallback. When a decline fires after server tools (for example, web search or code execution) have finished executing within a request, the fallback attempt proceeds: the completed tool results carry over, and the fallback model can keep invoking server tools. The one case that does not retry is a streaming decline that fires while a tool-use block of any type (a client tool, a server tool, or an MCP tool call) is still open on the stream: that refusal is returned directly, and if the `fallback-credit-2026-07-01` header is set it still carries a credit token redeemable by continuing the partial response. Non-streaming requests are unaffected; the API clears the partial work and retries before responding.
</Note>

### Billing and rate limits

An attempt that declined before producing any output is not billed: its tokens are reported on its `usage.iterations` entry but not charged. Every attempt that produced output, including one that declined partway through its response, is billed separately at the rates of the model that ran it. The `usage.iterations` array is the per-attempt record of what you're billed. The top-level `usage` counts describe only the attempt that produced the returned message. Tokens from different models are never summed into one field.

Every attempt that runs, including one that declined, counts against its own model's rate limits.

### Sticky routing

After a conversation falls back, the API records which model served it. Later requests for that conversation that include `fallbacks` go directly to that fallback model, without running the requested model. This avoids paying for an attempt that would predictably be declined again on every turn.

A few properties of the routing decision:

* It is retained for approximately 1 hour and is scoped to your organization.
* It is stored as a content hash of the conversation prefix plus the model that served it. The message content itself is not stored.
* It is best-effort, so your code must handle the requested model being tried again at any time.

Sticky routing applies to both streaming and non-streaming requests. On a streaming request, the routing decision is made before the stream opens, so the `message_start` event's `model` field already carries the fallback model's ID.


## Client-side fallback with the SDK middleware

Source: https://platform.claude.com/llms-full.txt#client-side-fallback-with-the-sdk-middleware

Every Anthropic SDK includes a refusal-fallback middleware. You configure it once on the client with your list of fallback models. Calls through `client.beta.messages` then retry refused requests automatically, on any platform. The middleware also sends the `fallback-credit-2026-07-01` beta header on every request it handles, so retries are repriced without per-request setup.

### Setting it up

Pass the middleware to the client constructor, and share one `BetaFallbackState` instance across the requests of a conversation.

<CodeGroup>
  ```bash cURL
  # The refusal-fallback middleware is an SDK feature. See the
  # server-side fallback section for the equivalent single-request approach,
  # or the fallback credit page for the raw HTTP retry pattern.

bash CLI
  # The refusal-fallback middleware is an SDK feature. See the
  # server-side fallback section for the equivalent single-request approach,
  # or the fallback credit page for the raw HTTP retry pattern.

python Python
  from anthropic import Anthropic, BetaFallbackState, BetaRefusalFallbackMiddleware

  # On a refusal, the middleware retries on the listed fallback model and
  # automatically sends the fallback-credit beta header on every request it handles.
  client = Anthropic(
      middleware=[BetaRefusalFallbackMiddleware([{"model": "claude-opus-4-8"}])],
  )

  state = BetaFallbackState()  # pins follow-ups to the model that accepted

  # Streaming: on a refusal the middleware retries on the fallback model and
  # splices its events onto the open stream.
  with (
      state,
      client.beta.messages.stream(
          max_tokens=1024,
          model="claude-fable-5",
          messages=[{"role": "user", "content": "Hello, Claude"}],
      ) as stream,
  ):
      for text in stream.text_stream:
          print(text, end="", flush=True)
      final_message = stream.get_final_message()
  print(f"\nserved by: {final_message.model}")

  # Non-streaming: reusing the state keeps the conversation pinned.
  with state:
      message = client.beta.messages.create(
          max_tokens=1024,
          model="claude-fable-5",
          messages=[{"role": "user", "content": "Hello, Claude"}],
      )
  print(f"served by: {message.model}")

typescript TypeScript
  import { BetaFallbackState, betaRefusalFallbackMiddleware } from "@anthropic-ai/sdk";

  // On a refusal, the middleware retries on the listed fallback model and
  // automatically sends the fallback-credit beta header on every request it handles.
  const client = new Anthropic({
    middleware: [betaRefusalFallbackMiddleware([{ model: "claude-opus-4-8" }])]
  });

  // Share one state across the conversation so follow-up requests stay
  // pinned to the model that accepted.
  const fallbackState = new BetaFallbackState();

  // Streaming: on a refusal the middleware retries on the fallback model and
  // splices its events onto the open stream.
  const stream = client.beta.messages
    .stream(
      {
        max_tokens: 1024,
        model: "claude-fable-5",
        messages: [{ role: "user", content: "Hello, Claude" }]
      },
      { fallbackState }
    )
    .on("text", (text) => process.stdout.write(text));

  const finalMessage = await stream.finalMessage();
  console.log("\nserved by:", finalMessage.model);

  // Non-streaming: reusing the state keeps the conversation pinned.
  const message = await client.beta.messages.create(
    {
      max_tokens: 1024,
      model: "claude-fable-5",
      messages: [{ role: "user", content: "Hello, Claude" }]
    },
    { fallbackState }
  );
  console.log("served by:", message.model);

csharp C#
  using Anthropic;
  using Anthropic.Helpers;
  using Anthropic.Models.Beta.Messages;
  using Messages = Anthropic.Models.Messages;

  // On a refusal, the handler retries on the listed fallback model and
  // automatically sends the fallback-credit beta header on every request it handles.
  AnthropicClient client = new()
  {
      Handlers =
      [
          new BetaRefusalFallbackHandler { Fallbacks = [new(Messages::Model.ClaudeOpus4_8)] },
      ],
  };

  // Pins follow-up requests sharing this state to the model that accepted.
  BetaFallbackState fallbackState = BetaFallbackState.Create();

  MessageCreateParams parameters = new()
  {
      Model = Messages::Model.ClaudeFable5,
      MaxTokens = 1024,
      Messages = [new() { Content = "Hello, Claude", Role = Role.User }],
  };

  // Streaming: if the stream ends in a refusal, the handler splices the fallback
  // model's events onto the still-open stream.
  BetaMessageContentAggregator aggregator = new();
  using (fallbackState.Use())
  {
      var responseUpdates = client.Beta.Messages.CreateStreaming(parameters);
      await foreach (BetaRawMessageStreamEvent rawEvent in responseUpdates.CollectAsync(aggregator))
      {
          if (
              rawEvent.TryPickContentBlockDelta(out var deltaEvent)
              && deltaEvent.Delta.TryPickText(out var textDelta)
          )
          {
              Console.Write(textDelta.Text);
          }
      }
  }
  BetaMessage streamedMessage = aggregator.Message();
  Console.WriteLine($"\nserved by: {streamedMessage.Model.Raw()}");

  // Non-streaming: reusing the state keeps the conversation pinned to the model that accepted.
  using (fallbackState.Use())
  {
      BetaMessage message = await client.Beta.Messages.Create(parameters);
      Console.WriteLine($"served by: {message.Model.Raw()}");
  }

go Go
  import (
  // ...
  	"github.com/anthropics/anthropic-sdk-go/lib/betafallback"
  // ...
  )

  func main() {
  	ctx := context.Background()

  	// The middleware retries a refused request on each fallback model in
  	// turn, and opts requests into the fallback-credit beta automatically.
  	client := anthropic.NewClient(
  		option.WithMiddleware(betafallback.BetaRefusalFallbackMiddleware(
  			[]anthropic.BetaFallbackParam{{Model: anthropic.ModelClaudeOpus4_8}},
  		)),
  	)

  	// One state per conversation: requests sharing it stay pinned to the
  	// model that accepted, so a follow-up never re-asks a model that refused.
  	state := &betafallback.BetaFallbackState{}
  	conversation := betafallback.WithBetaFallbackState(state)

  	params := anthropic.BetaMessageNewParams{
  		MaxTokens: 1024,
  		Model:     anthropic.ModelClaudeFable5,
  		Messages: []anthropic.BetaMessageParam{
  			anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Hello, Claude")),
  		},
  	}

  	// Streaming: on a refusal the middleware retries in place, splicing the
  	// fallback model's events onto the open stream as one continuous message.
  	stream := client.Beta.Messages.NewStreaming(ctx, params, conversation)
  	defer stream.Close()
  	var streamed anthropic.BetaMessage
  	for stream.Next() {
  		event := stream.Current()
  		if err := streamed.Accumulate(event); err != nil {
  			panic(err)
  		}
  		switch eventVariant := event.AsAny().(type) {
  		case anthropic.BetaRawContentBlockDeltaEvent:
  			if textDelta, ok := eventVariant.Delta.AsAny().(anthropic.BetaTextDelta); ok {
  				fmt.Print(textDelta.Text)
  			}
  		}
  	}
  	if err := stream.Err(); err != nil {
  		panic(err)
  	}
  	fmt.Println("\nserved by:", streamed.Model)

  	// Non-streaming: the shared state pins this follow-up to the model that
  	// served the streamed turn.
  	message, err := client.Beta.Messages.New(ctx, params, conversation)
  	if err != nil {
  		panic(err)
  	}
  	fmt.Println("served by:", message.Model)
  }

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.RequestOptions;
  import com.anthropic.core.http.StreamResponse;
  import com.anthropic.helpers.BetaFallbackState;
  import com.anthropic.helpers.BetaMessageAccumulator;
  import com.anthropic.helpers.BetaRefusalFallbackInterceptor;
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.BetaRawMessageStreamEvent;
  import com.anthropic.models.beta.messages.MessageCreateParams;
  import com.anthropic.models.messages.Model;

  void main() {
      // The interceptor retries refused requests on the fallback model. It automatically
      // adds the fallback-credit beta header to every request it handles.
      AnthropicClient client = AnthropicOkHttpClient.builder()
          .fromEnv()
          .addInterceptor(BetaRefusalFallbackInterceptor.builder()
              .addFallback(Model.CLAUDE_OPUS_4_8)
              .build())
          .build();

      // Share one state across requests so follow-ups stay pinned to the model that accepted.
      BetaFallbackState state = BetaFallbackState.create();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_FABLE_5)
          .maxTokens(1024)
          .addUserMessage("Hello, Claude")
          .build();

      // Streaming: on a refusal, the fallback model's events are spliced onto the open stream.
      BetaMessageAccumulator accumulator = BetaMessageAccumulator.create();
      try (StreamResponse<BetaRawMessageStreamEvent> streamResponse = client.beta()
              .messages()
              .createStreaming(params, RequestOptions.builder().fallbackState(state).build())) {
          streamResponse.stream()
              .peek(accumulator::accumulate)
              .forEach(event -> event.contentBlockDelta()
                  .flatMap(deltaEvent -> deltaEvent.delta().text())
                  .ifPresent(textDelta -> IO.print(textDelta.text())));
      }
      IO.println("\nserved by: " + accumulator.message().model().asString());

      // Non-streaming: reusing the same state keeps the conversation pinned.
      BetaMessage message = client.beta()
          .messages()
          .create(params, RequestOptions.builder().fallbackState(state).build());
      IO.println("served by: " + message.model().asString());
  }

php PHP
  use Anthropic\Beta\Messages\BetaRawContentBlockDeltaEvent;
  use Anthropic\Beta\Messages\BetaTextDelta;
  use Anthropic\Client;
  use Anthropic\Lib\Middleware\BetaFallbackState;
  use Anthropic\Lib\Middleware\RefusalFallbackMiddleware;
  use Anthropic\Lib\Streaming\MessageAccumulator;

  // Configure the fallback chain once. On a refusal, the middleware retries the
  // request down the chain and sends the fallback-credit beta header for you.
  $client = new Client(
      requestOptions: [
          'middleware' => [new RefusalFallbackMiddleware([['model' => 'claude-opus-4-8']])],
      ],
  );

  // Share one state across the conversation so follow-up requests stay pinned
  // to the model that accepted.
  $state = new BetaFallbackState();

  // Streaming: on a refusal the middleware splices the fallback model's events
  // onto the still-open stream. The accumulator's model is the serving model.
  $stream = $client->beta->messages->createStream(
      model: 'claude-fable-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
      requestOptions: ['fallbackState' => $state],
  );
  $accumulator = MessageAccumulator::forBetaMessages();
  foreach ($stream as $event) {
      $accumulator->accumulate($event);
      if ($event instanceof BetaRawContentBlockDeltaEvent
          && $event->delta instanceof BetaTextDelta) {
          echo $event->delta->text;
      }
  }
  echo "\nserved by: {$accumulator->message()->model}\n";

  // Non-streaming: same middleware. Reusing the state keeps the conversation
  // pinned to the model that accepted.
  $message = $client->beta->messages->create(
      model: 'claude-fable-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
      requestOptions: ['fallbackState' => $state],
  );
  echo "served by: {$message->model}\n";

ruby Ruby
  # On a refusal, the middleware retries the request down the fallback chain.
  # It sends the fallback-credit beta header on every request it handles.
  client = Anthropic::Client.new(
    middleware: [Anthropic::BetaRefusalFallbackMiddleware.new([{model: "claude-opus-4-8"}])]
  )

  # Share one state across the conversation so follow-up requests stay
  # pinned to the model that accepted.
  state = Anthropic::BetaFallbackState.new

  # Streaming: on a refusal the middleware splices the fallback model's
  # events onto the still-open stream.
  stream = client.beta.messages.stream(
    model: "claude-fable-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}],
    request_options: {fallback_state: state}
  )
  stream.text.each { print it }
  puts "\nserved by: #{stream.accumulated_message.model}"

  # Non-streaming: reusing the state keeps the conversation pinned to the model that accepted.
  message = client.beta.messages.create(
    model: "claude-fable-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}],
    request_options: {fallback_state: state}
  )
  puts "served by: #{message.model}"
  ```
</CodeGroup>

### How it behaves

* Retries walk your fallback list in order. A fallback model that itself refuses passes the request to the next entry.
* When every model in the list has declined, the middleware returns the final refusal (the last model's refusal response) rather than raising an error.
* Thinking blocks from Claude Fable 5.1 or Claude Fable 5 pass through unchanged. Each retry re-sends your original request body, and the only blocks the middleware removes from conversation history on later requests are the `fallback` boundary blocks it added itself. The fallback model can't read Claude Fable 5.1 blocks, which are [preserved only for that model or a newer one](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-for-model), so the API drops them.
* Responses served through the middleware include a `fallback` content block at each model boundary, the same as server-side fallback responses. The middleware manages those blocks for you on later requests.
* The model that accepted is recorded in `BetaFallbackState`, so follow-up requests that share the state stay pinned to it rather than re-asking a model that refused.

<Note>
  The middleware and the server-side `fallbacks` parameter do the same job. Configure one or the other, never both on the same request. To send a server-side `fallbacks` request from an application that installs the middleware, use a separate client instance without it.
</Note>


## Writing the retry yourself

Source: https://platform.claude.com/llms-full.txt#writing-the-retry-yourself

Over raw HTTP or with custom retry logic, implement the pattern the middleware wraps:

<Steps>
  <Step title="Detect the refusal">
    Check the response for `stop_reason: "refusal"`.
  </Step>

  <Step title="Re-send on a fallback model">
    Send the same request with `model` set to a fallback model, such as Claude Opus 4.8. Another model can normally serve a request that Claude Fable 5.1 or Claude Fable 5 declines. How you handle the conversation history depends on whether you redeem a [fallback credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit):

    * **Not redeeming a credit:** you can leave the earlier `thinking` and `redacted_thinking` blocks in place or strip them to save input tokens. The fallback model cannot use them either way: it ignores Claude Fable 5 blocks, and Claude Fable 5.1 blocks are [preserved only for that model or a newer one](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-for-model), so the API drops them.
    * **Redeeming a credit:** send the body unchanged, because redemption requires an exact match. The server handles the earlier model's thinking blocks on a redemption, so do not strip them (see [Fields that must match the refused request](https://platform.claude.com/docs/en/build-with-claude/fallback-credit#reference)).
  </Step>

  <Step title="Stay on the fallback model">
    For multi-turn conversations, keep using the fallback model for subsequent turns rather than switching back.
  </Step>
</Steps>

A manual retry writes the fallback model's prompt cache from scratch, which costs more than reading an existing cache. [Fallback credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit) refunds that cost; redeem it on every retry you build yourself.


## Refusals in Message Batches

Source: https://platform.claude.com/llms-full.txt#refusals-in-message-batches

A refused request in a [Message Batch](https://platform.claude.com/docs/en/build-with-claude/batch-processing) comes back as `result.type: "succeeded"` with `stop_reason: "refusal"`. Batch results carry the same `stop_details` object as synchronous responses, so you can detect refusals through either `stop_reason` or `stop_details.type`. One difference: batch refusals don't mint fallback credits, so `stop_details` on a batch result never includes a `fallback_credit_token`.

Server-side fallback is not available for batches (a batch request that includes `fallbacks` produces a per-item errored result). To retry refused batch items:

1. Collect the refused items from the results.
2. Strip the Claude Fable 5.1 or Claude Fable 5 thinking blocks from any multi-turn histories.
3. Resubmit them on a fallback model as a new batch or as direct requests.


## Common pitfalls

Source: https://platform.claude.com/llms-full.txt#common-pitfalls

* **Retry on a different model.** Re-sending a refused request to the same model usually earns another refusal. Point the retry at the fallback model.
* **Budget retries per request, not per turn or per session.** A single turn can produce several refusals, for example an agent plus its sub-agents.
* **Configure fallback on every request path.** Retry handlers, error-recovery branches, and background workers all need it. A handler that re-issues a request without fallback loses the protection on exactly the requests most likely to need it.
* **Give sub-agent calls their own fallback.** The `fallbacks` parameter does not propagate into model calls made from inside tool execution.
* **Make fallback a property of the request, not of ambient state.** A shared flag, cached config value, or global toggle can drift out of sync and silently leave a request unprotected. When you cannot confirm fallback is active, configure it rather than assume it is on.
* **Instrument refusals as their own signal.** A refusal is an HTTP 200, so monitoring built on error rates or 5xx responses never sees it. Emit one event per refusal and one per fallback-served response (the `fallback_message` entry in `usage.iterations` marks the latter), then alert on the gap between the two counts.
* **Branch on `stop_reason` or `stop_details.type`, not on `content` or the inner `stop_details` fields.** The `stop_details` object is always present on a refusal, but its `category` and `explanation` fields can be `null`. Check for `stop_reason` equal to `"refusal"` directly.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-4

<CardGroup>
  <Card title="Fallback credit" icon="scales" href="https://platform.claude.com/docs/en/build-with-claude/fallback-credit">
    Avoid paying the prompt-cache cost twice when you build the retry yourself.
  </Card>

  <Card title="Stop reasons and fallback" icon="code" href="https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons">
    Every `stop_reason` value and how to handle it.
  </Card>

  <Card title="SDK middleware" icon="settings" href="https://platform.claude.com/docs/en/cli-sdks-libraries/middleware">
    How SDK middleware works, including the refusal-fallback helper.
  </Card>

  <Card title="Migration guide" icon="arrow-right" href="https://platform.claude.com/docs/en/models/fable-5-1/migration-guide">
    Move an existing application to Claude Fable 5.1.
  </Card>
</CardGroup>


---
title: Stop reasons and fallback
url: https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons
description: Learn what each stop_reason value means and how to handle truncation, tool use, paused turns, and refusals in your application.
---

Every Messages API response includes a `stop_reason` field that tells you why Claude stopped generating. Check this field to decide whether to use the response as-is, continue the conversation, retry, or fall back to another model.

For the full response schema, see the [Messages API reference](https://platform.claude.com/docs/en/api/messages/create).


## Quick reference

Source: https://platform.claude.com/llms-full.txt#quick-reference

| Value                                                                                                                                        | When it occurs                                  | What to do                                                                                                                                              |
| -------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`end_turn`](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#end-turn)                                           | Claude finished its response naturally.         | Use the response.                                                                                                                                       |
| [`max_tokens`](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#max-tokens)                                       | The response reached your `max_tokens` limit.   | Raise `max_tokens` or [continue the response](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#ensuring-complete-responses). |
| [`stop_sequence`](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#stop-sequence)                                 | Claude emitted one of your `stop_sequences`.    | Read `stop_sequence` to see which one fired.                                                                                                            |
| [`tool_use`](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#tool-use)                                           | Claude is calling a tool.                       | Run the tool and return the result. A server tool call still missing its result block completes in a later response.                                    |
| [`pause_turn`](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#pause-turn)                                       | A server-tool loop reached its iteration limit. | Send the assistant content back to continue.                                                                                                            |
| [`refusal`](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#refusal)                                             | Claude declined to respond.                     | Read `stop_details` and [retry on a fallback model](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback).                       |
| [`model_context_window_exceeded`](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#model-context-window-exceeded) | The response filled the model's context window. | Treat the response as truncated.                                                                                                                        |


## The stop\_reason field

Source: https://platform.claude.com/llms-full.txt#the-stop-reason-field

The `stop_reason` field is part of every successful Messages API response. Unlike errors, which indicate failures in processing your request, `stop_reason` tells you why Claude completed its response generation.

```json Example response
{
  "id": "msg_01234",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Here's the answer to your question..."
    }
  ],
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "stop_details": null,
  "usage": {
    "input_tokens": 100,
    "output_tokens": 50
  }
}
```


## Stop reason values

Source: https://platform.claude.com/llms-full.txt#stop-reason-values

### end\_turn

The most common stop reason. Indicates Claude finished its response naturally.

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello!"}]
    }' | jq 'if .stop_reason == "end_turn" then (.content[] | select(.type == "text") | .text) else . end'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello!"}' \
    --format json | jq 'if .stop_reason == "end_turn" then (.content[] | select(.type == "text") | .text) else . end'

python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello!"}],
  )
  if response.stop_reason == "end_turn":
      # Process the complete response
      for block in response.content:
          if block.type == "text":
              print(block.text)

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello!" }]
  });

  if (response.stop_reason === "end_turn") {
    // Process the complete response
    const textBlock = response.content.find(
      (block): block is Anthropic.TextBlock => block.type === "text"
    );
    console.log(textBlock?.text);
  }

csharp C#
  AnthropicClient client = new();

  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello!" }]
  });

  if (response.StopReason == "end_turn")
  {
      // Process the complete response
      foreach (var block in response.Content)
      {
          if (block.TryPickText(out var textBlock))
          {
              Console.WriteLine(textBlock.Text);
          }
      }
  }

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello!")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  if response.StopReason == "end_turn" {
  	// Process the complete response
  	for _, block := range response.Content {
  		if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  			fmt.Println(textBlock.Text)
  		}
  	}
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  Message response = client.messages().create(
      MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addUserMessage("Hello!")
          .build()
  );

  if (response.stopReason().map(StopReason.END_TURN::equals).orElse(false)) {
      // Process the complete response
      response.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }

php PHP
  $client = new Client();

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello!']],
      model: 'claude-opus-5',
  );

  if ($response->stopReason === 'end_turn') {
      // Process the complete response
      foreach ($response->content as $block) {
          if ($block->type === 'text') {
              echo $block->text, PHP_EOL;
          }
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello!" }]
  )

  if response.stop_reason == :end_turn
    # Process the complete response
    response.content.each do |block|
      puts block.text if block.type == :text
    end
  end

python Python
    # INCORRECT: Adding text immediately after tool_result
    messages = [
        {"role": "user", "content": "Calculate the sum of 1234 and 5678"},
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": "toolu_123",
                    "name": "calculator",
                    "input": {"operation": "add", "a": 1234, "b": 5678},
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "toolu_123", "content": "6912"},
                {
                    "type": "text",
                    "text": "Here's the result",  # Don't add text after tool_result
                },
            ],
        },
    ]

    # CORRECT: Send tool results directly without additional text
    messages = [
        {"role": "user", "content": "Calculate the sum of 1234 and 5678"},
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": "toolu_123",
                    "name": "calculator",
                    "input": {"operation": "add", "a": 1234, "b": 5678},
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "toolu_123", "content": "6912"}
            ],
        },  # Just the tool_result, no additional text
    ]

typescript TypeScript
    // INCORRECT: Adding text immediately after tool_result
    let messages: Anthropic.MessageParam[] = [
      { role: "user", content: "Calculate the sum of 1234 and 5678" },
      {
        role: "assistant",
        content: [
          {
            type: "tool_use",
            id: "toolu_123",
            name: "calculator",
            input: { operation: "add", a: 1234, b: 5678 }
          }
        ]
      },
      {
        role: "user",
        content: [
          { type: "tool_result", tool_use_id: "toolu_123", content: "6912" },
          { type: "text", text: "Here's the result" } // Don't add text after tool_result
        ]
      }
    ];

    // CORRECT: Send tool results directly without additional text
    messages = [
      { role: "user", content: "Calculate the sum of 1234 and 5678" },
      {
        role: "assistant",
        content: [
          {
            type: "tool_use",
            id: "toolu_123",
            name: "calculator",
            input: { operation: "add", a: 1234, b: 5678 }
          }
        ]
      },
      {
        role: "user",
        // Just the tool_result, no additional text
        content: [{ type: "tool_result", tool_use_id: "toolu_123", content: "6912" }]
      }
    ];

csharp C#
    using System.Text.Json;
    using Anthropic.Models.Messages;

    var input = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(
        """{"operation":"add","a":1234,"b":5678}"""
    )!;

    // INCORRECT: Adding text immediately after tool_result
    List<MessageParam> messages =
    [
        new() { Role = Role.User, Content = "Calculate the sum of 1234 and 5678" },
        new()
        {
            Role = Role.Assistant,
            Content = new List<ContentBlockParam>
            {
                new ToolUseBlockParam { ID = "toolu_123", Name = "calculator", Input = input }
            }
        },
        new()
        {
            Role = Role.User,
            Content = new List<ContentBlockParam>
            {
                new ToolResultBlockParam { ToolUseID = "toolu_123", Content = "6912" },
                new TextBlockParam { Text = "Here's the result" } // Don't add text after tool_result
            }
        }
    ];

    // CORRECT: Send tool results directly without additional text
    messages =
    [
        new() { Role = Role.User, Content = "Calculate the sum of 1234 and 5678" },
        new()
        {
            Role = Role.Assistant,
            Content = new List<ContentBlockParam>
            {
                new ToolUseBlockParam { ID = "toolu_123", Name = "calculator", Input = input }
            }
        },
        new()
        {
            Role = Role.User,
            // Just the tool_result, no additional text
            Content = new List<ContentBlockParam>
            {
                new ToolResultBlockParam { ToolUseID = "toolu_123", Content = "6912" }
            }
        }
    ];

go Go
    input := map[string]any{"operation": "add", "a": 1234, "b": 5678}

    // INCORRECT: Adding text immediately after tool_result
    messages := []anthropic.MessageParam{
    	anthropic.NewUserMessage(anthropic.NewTextBlock("Calculate the sum of 1234 and 5678")),
    	anthropic.NewAssistantMessage(
    		anthropic.NewToolUseBlock("toolu_123", input, "calculator"),
    	),
    	anthropic.NewUserMessage(
    		anthropic.NewToolResultBlock("toolu_123", "6912", false),
    		anthropic.NewTextBlock("Here's the result"), // Don't add text after tool_result
    	),
    }

    // CORRECT: Send tool results directly without additional text
    messages = []anthropic.MessageParam{
    	anthropic.NewUserMessage(anthropic.NewTextBlock("Calculate the sum of 1234 and 5678")),
    	anthropic.NewAssistantMessage(
    		anthropic.NewToolUseBlock("toolu_123", input, "calculator"),
    	),
    	// Just the tool_result, no additional text
    	anthropic.NewUserMessage(
    		anthropic.NewToolResultBlock("toolu_123", "6912", false),
    	),
    }

java Java
    ToolUseBlockParam toolUse = ToolUseBlockParam.builder()
        .id("toolu_123")
        .name("calculator")
        .input(ToolUseBlockParam.Input.builder()
            .putAdditionalProperty("operation", JsonValue.from("add"))
            .putAdditionalProperty("a", JsonValue.from(1234))
            .putAdditionalProperty("b", JsonValue.from(5678))
            .build())
        .build();

    // INCORRECT: Adding text immediately after tool_result
    List<MessageParam> messages = List.of(
        MessageParam.builder().role(MessageParam.Role.USER)
            .content("Calculate the sum of 1234 and 5678").build(),
        MessageParam.builder().role(MessageParam.Role.ASSISTANT)
            .contentOfBlockParams(List.of(ContentBlockParam.ofToolUse(toolUse))).build(),
        MessageParam.builder().role(MessageParam.Role.USER)
            .contentOfBlockParams(List.of(
                ContentBlockParam.ofToolResult(
                    ToolResultBlockParam.builder().toolUseId("toolu_123").content("6912").build()),
                // Don't add text after tool_result
                ContentBlockParam.ofText(TextBlockParam.builder().text("Here's the result").build())
            )).build()
    );

    // CORRECT: Send tool results directly without additional text
    messages = List.of(
        MessageParam.builder().role(MessageParam.Role.USER)
            .content("Calculate the sum of 1234 and 5678").build(),
        MessageParam.builder().role(MessageParam.Role.ASSISTANT)
            .contentOfBlockParams(List.of(ContentBlockParam.ofToolUse(toolUse))).build(),
        // Just the tool_result, no additional text
        MessageParam.builder().role(MessageParam.Role.USER)
            .contentOfBlockParams(List.of(
                ContentBlockParam.ofToolResult(
                    ToolResultBlockParam.builder().toolUseId("toolu_123").content("6912").build())
            )).build()
    );

php PHP
    // INCORRECT: Adding text immediately after tool_result
    $messages = [
        ['role' => 'user', 'content' => 'Calculate the sum of 1234 and 5678'],
        [
            'role' => 'assistant',
            'content' => [
                [
                    'type' => 'tool_use',
                    'id' => 'toolu_123',
                    'name' => 'calculator',
                    'input' => ['operation' => 'add', 'a' => 1234, 'b' => 5678],
                ],
            ],
        ],
        [
            'role' => 'user',
            'content' => [
                ['type' => 'tool_result', 'tool_use_id' => 'toolu_123', 'content' => '6912'],
                // Don't add text after tool_result
                ['type' => 'text', 'text' => "Here's the result"],
            ],
        ],
    ];

    // CORRECT: Send tool results directly without additional text
    $messages = [
        ['role' => 'user', 'content' => 'Calculate the sum of 1234 and 5678'],
        [
            'role' => 'assistant',
            'content' => [
                [
                    'type' => 'tool_use',
                    'id' => 'toolu_123',
                    'name' => 'calculator',
                    'input' => ['operation' => 'add', 'a' => 1234, 'b' => 5678],
                ],
            ],
        ],
        [
            'role' => 'user',
            // Just the tool_result, no additional text
            'content' => [
                ['type' => 'tool_result', 'tool_use_id' => 'toolu_123', 'content' => '6912'],
            ],
        ],
    ];

ruby Ruby
    # INCORRECT: Adding text immediately after tool_result
    messages = [
      { role: "user", content: "Calculate the sum of 1234 and 5678" },
      {
        role: "assistant",
        content: [
          {
            type: "tool_use",
            id: "toolu_123",
            name: "calculator",
            input: { operation: "add", a: 1234, b: 5678 }
          }
        ]
      },
      {
        role: "user",
        content: [
          { type: "tool_result", tool_use_id: "toolu_123", content: "6912" },
          # Don't add text after tool_result
          { type: "text", text: "Here's the result" }
        ]
      }
    ]

    # CORRECT: Send tool results directly without additional text
    messages = [
      { role: "user", content: "Calculate the sum of 1234 and 5678" },
      {
        role: "assistant",
        content: [
          {
            type: "tool_use",
            id: "toolu_123",
            name: "calculator",
            input: { operation: "add", a: 1234, b: 5678 }
          }
        ]
      },
      {
        role: "user",
        # Just the tool_result, no additional text
        content: [
          { type: "tool_result", tool_use_id: "toolu_123", content: "6912" }
        ]
      }
    ]

python Python
    def handle_empty_response(client, messages):
        response = client.messages.create(
            model="claude-opus-5", max_tokens=1024, messages=messages
        )

        # Check if response is empty
        if response.stop_reason == "end_turn" and not response.content:
            # INCORRECT: Don't just retry with the empty response
            # This won't work because Claude already decided it's done

            # CORRECT: Add a continuation prompt in a NEW user message
            messages.append({"role": "user", "content": "Please continue"})

            response = client.messages.create(
                model="claude-opus-5", max_tokens=1024, messages=messages
            )

        return response

typescript TypeScript
    async function handleEmptyResponse(
      client: Anthropic,
      messages: Anthropic.MessageParam[]
    ): Promise<Anthropic.Message> {
      let response = await client.messages.create({
        model: "claude-opus-5",
        max_tokens: 1024,
        messages
      });

      // Check if response is empty
      if (response.stop_reason === "end_turn" && response.content.length === 0) {
        // INCORRECT: Don't just retry with the empty response
        // This won't work because Claude already decided it's done

        // CORRECT: Add a continuation prompt in a NEW user message
        messages.push({ role: "user", content: "Please continue" });

        response = await client.messages.create({
          model: "claude-opus-5",
          max_tokens: 1024,
          messages
        });
      }

      return response;
    }

csharp C#
    static async Task<Message> HandleEmptyResponse(AnthropicClient client, List<MessageParam> messages)
    {
        var response = await client.Messages.Create(new MessageCreateParams
        {
            Model = Model.ClaudeOpus5,
            MaxTokens = 1024,
            Messages = messages
        });

        // Check if response is empty
        if (response.StopReason == "end_turn" && response.Content.Count == 0)
        {
            // CORRECT: Add a continuation prompt in a NEW user message
            messages.Add(new() { Role = Role.User, Content = "Please continue" });

            response = await client.Messages.Create(new MessageCreateParams
            {
                Model = Model.ClaudeOpus5,
                MaxTokens = 1024,
                Messages = messages
            });
        }

        return response;
    }

go Go
    func handleEmptyResponse(client anthropic.Client, messages []anthropic.MessageParam) (*anthropic.Message, error) {
    	response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
    		Model:     anthropic.ModelClaudeOpus5,
    		MaxTokens: 1024,
    		Messages:  messages,
    	})
    	if err != nil {
    		return nil, err
    	}

    	// Check if response is empty
    	if response.StopReason == "end_turn" && len(response.Content) == 0 {
    		// CORRECT: Add a continuation prompt in a NEW user message
    		messages = append(messages, anthropic.NewUserMessage(anthropic.NewTextBlock("Please continue")))

    		response, err = client.Messages.New(context.TODO(), anthropic.MessageNewParams{
    			Model:     anthropic.ModelClaudeOpus5,
    			MaxTokens: 1024,
    			Messages:  messages,
    		})
    		if err != nil {
    			return nil, err
    		}
    	}

    	return response, nil
    }

java Java
    static Message handleEmptyResponse(AnthropicClient client, List<MessageParam> messages) {
        Message response = client.messages().create(
            MessageCreateParams.builder()
                .model(Model.CLAUDE_OPUS_5)
                .maxTokens(1024L)
                .messages(messages)
                .build()
        );

        // Check if response is empty
        boolean isEndTurn = response.stopReason().map(StopReason.END_TURN::equals).orElse(false);
        if (isEndTurn && response.content().isEmpty()) {
            // CORRECT: Add a continuation prompt in a NEW user message
            List<MessageParam> extended = new ArrayList<>(messages);
            extended.add(MessageParam.builder()
                .role(MessageParam.Role.USER)
                .content("Please continue")
                .build());

            response = client.messages().create(
                MessageCreateParams.builder()
                    .model(Model.CLAUDE_OPUS_5)
                    .maxTokens(1024L)
                    .messages(extended)
                    .build()
            );
        }

        return response;
    }

php PHP
    function handle_empty_response(Client $client, array $messages)
    {
        $response = $client->messages->create(
            maxTokens: 1024,
            messages: $messages,
            model: 'claude-opus-5',
        );

        // Check if response is empty
        if ($response->stopReason === 'end_turn' && count($response->content) === 0) {
            // CORRECT: Add a continuation prompt in a NEW user message
            $messages[] = ['role' => 'user', 'content' => 'Please continue'];

            $response = $client->messages->create(
                maxTokens: 1024,
                messages: $messages,
                model: 'claude-opus-5',
            );
        }

        return $response;
    }

ruby Ruby
    def handle_empty_response(client, messages)
      response = client.messages.create(
        model: "claude-opus-5",
        max_tokens: 1024,
        messages: messages
      )

      # Check if response is empty
      if response.stop_reason == :end_turn && response.content.empty?
        # CORRECT: Add a continuation prompt in a NEW user message
        messages << { role: "user", content: "Please continue" }

        response = client.messages.create(
          model: "claude-opus-5",
          max_tokens: 1024,
          messages: messages
        )
      end

      response
    end

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 10,
      "messages": [{"role": "user", "content": "Explain quantum physics"}]
    }' | jq '.stop_reason'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 10 \
    --message '{role: user, content: "Explain quantum physics"}' \
    --format json | jq '.stop_reason'

python Python
  client = anthropic.Anthropic()
  # Request with limited tokens
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=10,
      messages=[{"role": "user", "content": "Explain quantum physics"}],
  )

  if response.stop_reason == "max_tokens":
      # Response was truncated
      print("Response was cut off at token limit")
      # Consider making another request to continue

typescript TypeScript
  const client = new Anthropic();

  // Request with limited tokens
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 10,
    messages: [{ role: "user", content: "Explain quantum physics" }]
  });

  if (response.stop_reason === "max_tokens") {
    // Response was truncated
    console.log("Response was cut off at token limit");
    // Consider making another request to continue
  }

csharp C#
  AnthropicClient client = new();

  // Request with limited tokens
  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 10,
      Messages = [new() { Role = Role.User, Content = "Explain quantum physics" }]
  });

  if (response.StopReason == "max_tokens")
  {
      // Response was truncated
      Console.WriteLine("Response was cut off at token limit");
      // Consider making another request to continue
  }

go Go
  client := anthropic.NewClient()

  // Request with limited tokens
  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 10,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Explain quantum physics")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  if response.StopReason == "max_tokens" {
  	// Response was truncated
  	fmt.Println("Response was cut off at token limit")
  	// Consider making another request to continue
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  // Request with limited tokens
  Message response = client.messages().create(
      MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(10L)
          .addUserMessage("Explain quantum physics")
          .build()
  );

  if (response.stopReason().map(StopReason.MAX_TOKENS::equals).orElse(false)) {
      // Response was truncated
      IO.println("Response was cut off at token limit");
      // Consider making another request to continue
  }

php PHP
  $client = new Client();

  // Request with limited tokens
  $response = $client->messages->create(
      maxTokens: 10,
      messages: [['role' => 'user', 'content' => 'Explain quantum physics']],
      model: 'claude-opus-5',
  );

  if ($response->stopReason === 'max_tokens') {
      // Response was truncated
      echo 'Response was cut off at token limit', PHP_EOL;
      // Consider making another request to continue
  }

ruby Ruby
  client = Anthropic::Client.new

  # Request with limited tokens
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 10,
    messages: [{ role: "user", content: "Explain quantum physics" }]
  )

  if response.stop_reason == :max_tokens
    # Response was truncated
    puts "Response was cut off at token limit"
    # Consider making another request to continue
  end

bash CLI
    RESPONSE=$(ant messages create --max-tokens 1024 --format jsonl < request.yaml)

    # Check if the response was truncated mid tool use
    STOP_REASON=$(jq -r '.stop_reason' <<<"$RESPONSE")
    LAST_TYPE=$(jq -r '.content[-1].type' <<<"$RESPONSE")
    if [ "$STOP_REASON" = "max_tokens" ] && [ "$LAST_TYPE" = "tool_use" ]; then
      # Retry with a higher max_tokens
      ant messages create --max-tokens 4096 < request.yaml
    fi

python Python
    # Check if response was truncated during tool use
    if response.stop_reason == "max_tokens":
        # Check if the last content block is an incomplete tool_use
        last_block = response.content[-1]
        if last_block.type == "tool_use":
            # Send the request with higher max_tokens
            response = client.messages.create(
                model="claude-opus-5",
                max_tokens=4096,  # Increased limit
                messages=messages,
                tools=tools,
            )

typescript TypeScript
    // Check if response was truncated during tool use
    if (response.stop_reason === "max_tokens") {
      // Check if the last content block is an incomplete tool_use
      const lastBlock = response.content[response.content.length - 1];
      if (lastBlock.type === "tool_use") {
        // Send the request with higher max_tokens
        response = await client.messages.create({
          model: "claude-opus-5",
          max_tokens: 4096, // Increased limit
          messages: messages,
          tools: tools
        });
      }
    }

csharp C#
    using System.Linq;
    using Anthropic;
    using Anthropic.Models.Messages;

    AnthropicClient client = new();

    var parameters = new MessageCreateParams
    {
        Model = Model.ClaudeOpus5,
        MaxTokens = 1024,
        Messages = messages,
        Tools = tools
    };

    var response = await client.Messages.Create(parameters);

    if (response.StopReason == "max_tokens")
    {
        var lastBlock = response.Content.Last();
        if (lastBlock.TryPickToolUse(out _))
        {
            response = await client.Messages.Create(parameters with { MaxTokens = 4096 });
        }
    }

go Go
    response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
    	Model:     anthropic.ModelClaudeOpus5,
    	MaxTokens: 1024,
    	Messages:  messages,
    	Tools:     tools,
    })
    if err != nil {
    	log.Fatal(err)
    }

    if response.StopReason == "max_tokens" {
    	lastBlock := response.Content[len(response.Content)-1]
    	switch lastBlock.AsAny().(type) {
    	case anthropic.ToolUseBlock:
    		response, err = client.Messages.New(context.TODO(), anthropic.MessageNewParams{
    			Model:     anthropic.ModelClaudeOpus5,
    			MaxTokens: 4096,
    			Messages:  messages,
    			Tools:     tools,
    		})
    		if err != nil {
    			log.Fatal(err)
    		}
    	}
    }

java Java
    // Check if response was truncated during tool use
    if (response.stopReason().isPresent() && response.stopReason().get().equals(StopReason.MAX_TOKENS)) {
        ContentBlock lastBlock = response.content().get(response.content().size() - 1);
        if (lastBlock.toolUse().isPresent()) {
            // Send the request with higher max_tokens
            response = client.messages().create(
                MessageCreateParams.builder()
                    .model(Model.CLAUDE_OPUS_5)
                    .maxTokens(4096L) // Increased limit
                    .messages(messages)
                    .tools(tools)
                    .build()
            );
        }
    }

php PHP
    $response = $client->messages->create(
        maxTokens: 1024,
        messages: $messages,
        model: 'claude-opus-5',
        tools: $tools,
    );

    if ($response->stopReason === 'max_tokens') {
        $lastBlock = end($response->content);
        if ($lastBlock->type === 'tool_use') {
            $response = $client->messages->create(
                maxTokens: 4096,
                messages: $messages,
                model: 'claude-opus-5',
                tools: $tools,
            );
        }
    }

ruby Ruby
    response = client.messages.create(
      model: "claude-opus-5",
      max_tokens: 1024,
      messages: messages,
      tools: tools
    )

    if response.stop_reason == :max_tokens
      last_block = response.content.last
      if last_block.type == :tool_use
        response = client.messages.create(
          model: "claude-opus-5",
          max_tokens: 4096,
          messages: messages,
          tools: tools
        )
      end
    end

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "stop_sequences": ["END", "STOP"],
      "messages": [{"role": "user", "content": "Generate text until you say END"}]
    }' | jq '{stop_reason, stop_sequence}'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --stop-sequence END --stop-sequence STOP \
    --message '{role: user, content: "Generate text until you say END"}' \
    --format json | jq '{stop_reason, stop_sequence}'

python Python
  client = anthropic.Anthropic()
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      stop_sequences=["END", "STOP"],
      messages=[{"role": "user", "content": "Generate text until you say END"}],
  )

  if response.stop_reason == "stop_sequence":
      print(f"Stopped at sequence: {response.stop_sequence}")

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    stop_sequences: ["END", "STOP"],
    messages: [{ role: "user", content: "Generate text until you say END" }]
  });

  if (response.stop_reason === "stop_sequence") {
    console.log(`Stopped at sequence: ${response.stop_sequence}`);
  }

csharp C#
  AnthropicClient client = new();

  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      StopSequences = ["END", "STOP"],
      Messages = [new() { Role = Role.User, Content = "Generate text until you say END" }]
  });

  if (response.StopReason == "stop_sequence")
  {
      Console.WriteLine($"Stopped at sequence: {response.StopSequence}");
  }

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:         anthropic.ModelClaudeOpus5,
  	MaxTokens:     1024,
  	StopSequences: []string{"END", "STOP"},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Generate text until you say END")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  if response.StopReason == "stop_sequence" {
  	fmt.Printf("Stopped at sequence: %s\n", response.StopSequence)
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  Message response = client.messages().create(
      MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addStopSequence("END")
          .addStopSequence("STOP")
          .addUserMessage("Generate text until you say END")
          .build()
  );

  if (response.stopReason().map(StopReason.STOP_SEQUENCE::equals).orElse(false)) {
      IO.println("Stopped at sequence: " + response.stopSequence().orElse(""));
  }

php PHP
  $client = new Client();

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Generate text until you say END']],
      model: 'claude-opus-5',
      stopSequences: ['END', 'STOP'],
  );

  if ($response->stopReason === 'stop_sequence') {
      echo "Stopped at sequence: {$response->stopSequence}", PHP_EOL;
  }

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    stop_sequences: ["END", "STOP"],
    messages: [{ role: "user", content: "Generate text until you say END" }]
  )

  if response.stop_reason == :stop_sequence
    puts "Stopped at sequence: #{response.stop_sequence}"
  end

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "tools": [{
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
          "type": "object",
          "properties": {"location": {"type": "string", "description": "City and state"}},
          "required": ["location"]
        }
      }],
      "messages": [{"role": "user", "content": "What is the weather in San Francisco?"}]
    }' | jq '.stop_reason, (.content[] | select(.type == "tool_use"))'

bash CLI
  ant messages create --format json <<'YAML' | jq '.stop_reason, (.content[] | select(.type == "tool_use"))'
  model: claude-opus-5
  max_tokens: 1024
  messages:
    - role: user
      content: What is the weather in San Francisco?
  tools:
    - name: get_weather
      description: Get the current weather in a given location
      input_schema:
        type: object
        properties:
          location: {type: string, description: City and state}
        required: [location]
  YAML

python Python
  client = anthropic.Anthropic()
  weather_tool = {
      "name": "get_weather",
      "description": "Get the current weather in a given location",
      "input_schema": {
          "type": "object",
          "properties": {
              "location": {"type": "string", "description": "City and state"},
          },
          "required": ["location"],
      },
  }


  def execute_tool(name, tool_input):
      """Execute a tool and return the result."""
      return f"Weather in {tool_input.get('location', 'unknown')}: 72°F"


  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      tools=[weather_tool],
      messages=[{"role": "user", "content": "What is the weather in San Francisco?"}],
  )

  if response.stop_reason == "tool_use":
      # Extract and execute the tool
      for block in response.content:
          if block.type == "tool_use":
              result = execute_tool(block.name, block.input)
              # Return result to Claude for final response

typescript TypeScript
  const client = new Anthropic();
  const weatherTool: Anthropic.Tool = {
    name: "get_weather",
    description: "Get the current weather in a given location",
    input_schema: {
      type: "object",
      properties: {
        location: { type: "string", description: "City and state" }
      },
      required: ["location"]
    }
  };

  function executeTool(name: string, input: Record<string, string>): string {
    return `Weather in ${input.location ?? "unknown"}: 72°F`;
  }

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [weatherTool],
    messages: [{ role: "user", content: "What is the weather in San Francisco?" }]
  });

  if (response.stop_reason === "tool_use") {
    // Extract and execute the tool
    for (const block of response.content) {
      if (block.type === "tool_use") {
        const result = executeTool(block.name, block.input as Record<string, string>);
        // Return result to Claude for final response
      }
    }
  }

csharp C#
  AnthropicClient client = new();

  var weatherTool = new Tool
  {
      Name = "get_weather",
      Description = "Get the current weather in a given location",
      InputSchema = new InputSchema
      {
          Properties = new Dictionary<string, JsonElement>
          {
              ["location"] = JsonSerializer.SerializeToElement(
                  new { type = "string", description = "City and state" }
              ),
          },
          Required = ["location"]
      }
  };

  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Tools = [weatherTool],
      Messages = [new() { Role = Role.User, Content = "What is the weather in San Francisco?" }]
  });

  if (response.StopReason == "tool_use")
  {
      // Extract and execute the tool
      foreach (var block in response.Content)
      {
          if (block.TryPickToolUse(out var toolUse))
          {
              // Execute toolUse.Name with toolUse.Input and return the result to Claude
          }
      }
  }

go Go
  client := anthropic.NewClient()

  weatherTool := anthropic.ToolParam{
  	Name:        "get_weather",
  	Description: anthropic.String("Get the current weather in a given location"),
  	InputSchema: anthropic.ToolInputSchemaParam{
  		Properties: map[string]any{
  			"location": map[string]string{"type": "string", "description": "City and state"},
  		},
  		Required: []string{"location"},
  	},
  }

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Tools:     []anthropic.ToolUnionParam{{OfTool: &weatherTool}},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What is the weather in San Francisco?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  if response.StopReason == "tool_use" {
  	// Extract and execute the tool
  	for _, block := range response.Content {
  		if toolUse, ok := block.AsAny().(anthropic.ToolUseBlock); ok {
  			fmt.Println(toolUse.Name, toolUse.Input)
  			// Return result to Claude for final response
  		}
  	}
  }

java Java
  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      Tool weatherTool = Tool.builder()
          .name("get_weather")
          .description("Get the current weather in a given location")
          .inputSchema(Tool.InputSchema.builder()
              .properties(JsonValue.from(Map.of(
                  "location", Map.of("type", "string", "description", "City and state")
              )))
              .putAdditionalProperty("required", JsonValue.from(List.of("location")))
              .build())
          .build();

      Message response = client.messages().create(
          MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024L)
              .addTool(weatherTool)
              .addUserMessage("What is the weather in San Francisco?")
              .build()
      );

      if (response.stopReason().map(StopReason.TOOL_USE::equals).orElse(false)) {
          // Extract and execute the tool
          for (ContentBlock block : response.content()) {
              block.toolUse().ifPresent(toolUse -> {
                  // Execute toolUse.name() with toolUse.input() and return the result to Claude
              });
          }
      }

php PHP
  $client = new Client();

  $weatherTool = [
      'name' => 'get_weather',
      'description' => 'Get the current weather in a given location',
      'input_schema' => [
          'type' => 'object',
          'properties' => [
              'location' => ['type' => 'string', 'description' => 'City and state'],
          ],
          'required' => ['location'],
      ],
  ];

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'What is the weather in San Francisco?']],
      model: 'claude-opus-5',
      tools: [$weatherTool],
  );

  if ($response->stopReason === 'tool_use') {
      // Extract and execute the tool
      foreach ($response->content as $block) {
          if ($block->type === 'tool_use') {
              // Execute $block->name with $block->input and return the result to Claude
          }
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  weather_tool = {
    name: "get_weather",
    description: "Get the current weather in a given location",
    input_schema: {
      type: "object",
      properties: {
        location: { type: "string", description: "City and state" }
      },
      required: ["location"]
    }
  }

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    tools: [weather_tool],
    messages: [{ role: "user", content: "What is the weather in San Francisco?" }]
  )

  if response.stop_reason == :tool_use
    # Extract and execute the tool
    response.content.each do |block|
      next unless block.type == :tool_use
      # Execute block.name with block.input and return the result to Claude
    end
  end

json A mixed tool_use response
{
  "stop_reason": "tool_use",
  "content": [
    {
      "type": "server_tool_use",
      "id": "srvtoolu_01HxbWnMRmbWyMfUtJKC45rA",
      "name": "web_search",
      "input": { "query": "example article" }
    },
    {
      "type": "tool_use",
      "id": "toolu_01PjgRJLbXrXEMZwDNYLnBqk",
      "name": "run_command",
      "input": { "command": "uname -a" }
    }
  ]
}

json The follow-up user message
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01PjgRJLbXrXEMZwDNYLnBqk",
      "content": "Linux demo-host 6.8.0-52-generic x86_64 GNU/Linux"
    }
  ]
}

text wrap
`web_search` tool use with id `srvtoolu_01HxbWnMRmbWyMfUtJKC45rA` was found without a corresponding `web_search_tool_result` block

bash cURL
  # The SDKs handle continuation directly. With cURL, inspect stop_reason
  # on the response and re-POST with the assistant content appended.
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 4096,
      "tools": [{"type": "web_search_20250305", "name": "web_search"}],
      "messages": [{"role": "user", "content": "Search for latest AI news"}]
    }' | jq '{stop_reason, content}'

bash CLI
  # Inspect stop_reason; if it is pause_turn, re-run with the assistant
  # response appended to --message.
  ant messages create --format json <<'YAML' | jq '{stop_reason, content}'
  model: claude-opus-5
  max_tokens: 4096
  tools:
    - {type: web_search_20250305, name: web_search}
  messages:
    - {role: user, content: "Search for latest AI news"}
  YAML

python Python
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=4096,
      tools=[{"type": "web_search_20250305", "name": "web_search"}],
      messages=[{"role": "user", "content": "Search for latest AI news"}],
  )

  if response.stop_reason == "pause_turn":
      # Continue the conversation by sending the response back
      messages = [
          {"role": "user", "content": "Search for latest AI news"},
          {"role": "assistant", "content": response.content},
      ]
      continuation = client.messages.create(
          model="claude-opus-5",
          max_tokens=4096,
          messages=messages,
          tools=[{"type": "web_search_20250305", "name": "web_search"}],
      )

typescript TypeScript
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 4096,
    tools: [{ type: "web_search_20250305", name: "web_search" }],
    messages: [{ role: "user", content: "Search for latest AI news" }]
  });

  if (response.stop_reason === "pause_turn") {
    // Continue the conversation by sending the response back
    const continuation = await client.messages.create({
      model: "claude-opus-5",
      max_tokens: 4096,
      tools: [{ type: "web_search_20250305", name: "web_search" }],
      messages: [
        { role: "user", content: "Search for latest AI news" },
        { role: "assistant", content: response.content }
      ]
    });
  }

csharp C#
  List<ToolUnion> tools = [new ToolUnion(new WebSearchTool20250305())];
  MessageParam userMessage = new() { Role = Role.User, Content = "Search for latest AI news" };

  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 4096,
      Tools = tools,
      Messages = [userMessage]
  });

  if (response.StopReason == "pause_turn")
  {
      // Continue the conversation by sending the response back
      var continuation = await client.Messages.Create(new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 4096,
          Tools = tools,
          Messages =
          [
              userMessage,
              new()
              {
                  Role = Role.Assistant,
                  Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList()
              }
          ]
      });
  }

go Go
  tools := []anthropic.ToolUnionParam{
  	{OfWebSearchTool20250305: &anthropic.WebSearchTool20250305Param{}},
  }
  userMessage := anthropic.NewUserMessage(anthropic.NewTextBlock("Search for latest AI news"))

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 4096,
  	Tools:     tools,
  	Messages:  []anthropic.MessageParam{userMessage},
  })
  if err != nil {
  	log.Fatal(err)
  }

  if response.StopReason == "pause_turn" {
  	// Continue the conversation by sending the response back
  	var contentParams []anthropic.ContentBlockParamUnion
  	for _, block := range response.Content {
  		contentParams = append(contentParams, block.ToParam())
  	}
  	continuation, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 4096,
  		Tools:     tools,
  		Messages:  []anthropic.MessageParam{userMessage, anthropic.NewAssistantMessage(contentParams...)},
  	})
  	if err != nil {
  		log.Fatal(err)
  	}
  	_ = continuation
  }

java Java
  Message response = client.messages().create(
      MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(4096L)
          .addTool(WebSearchTool20250305.builder().build())
          .addUserMessage("Search for latest AI news")
          .build()
  );

  if (response.stopReason().map(StopReason.PAUSE_TURN::equals).orElse(false)) {
      // Continue the conversation by sending the response back
      Message continuation = client.messages().create(
          MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(4096L)
              .addTool(WebSearchTool20250305.builder().build())
              .addUserMessage("Search for latest AI news")
              .addMessage(response)
              .build()
      );
  }

php PHP
  $tools = [['type' => 'web_search_20250305', 'name' => 'web_search']];
  $userMessage = ['role' => 'user', 'content' => 'Search for latest AI news'];

  $response = $client->messages->create(
      maxTokens: 4096,
      messages: [$userMessage],
      model: 'claude-opus-5',
      tools: $tools,
  );

  if ($response->stopReason === 'pause_turn') {
      // Continue the conversation by sending the response back
      $continuation = $client->messages->create(
          maxTokens: 4096,
          messages: [
              $userMessage,
              ['role' => 'assistant', 'content' => $response->content],
          ],
          model: 'claude-opus-5',
          tools: $tools,
      );
  }

ruby Ruby
  tools = [{ type: "web_search_20250305", name: "web_search" }]
  user_message = { role: "user", content: "Search for latest AI news" }

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 4096,
    tools: tools,
    messages: [user_message]
  )

  if response.stop_reason == :pause_turn
    # Continue the conversation by sending the response back
    continuation = client.messages.create(
      model: "claude-opus-5",
      max_tokens: 4096,
      tools: tools,
      messages: [user_message, { role: "assistant", content: response.content }]
    )
  end

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "[Unsafe request]"}]
    }' | jq '{stop_reason, stop_details}'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "[Unsafe request]"}' \
    --format json | jq '{stop_reason, stop_details}'

python Python
  client = anthropic.Anthropic()
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "[Unsafe request]"}],
  )

  if response.stop_reason == "refusal":
      # Claude declined to respond
      print("Claude was unable to process this request")
      # Consider rephrasing or modifying the request

typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "[Unsafe request]" }]
  });

  if (response.stop_reason === "refusal") {
    // Claude declined to respond
    console.log("Claude was unable to process this request");
    // Consider rephrasing or modifying the request
  }

csharp C#
  AnthropicClient client = new();

  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "[Unsafe request]" }]
  });

  if (response.StopReason == "refusal")
  {
      // Claude declined to respond
      Console.WriteLine("Claude was unable to process this request");
      // Consider rephrasing or modifying the request
  }

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("[Unsafe request]")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  if response.StopReason == "refusal" {
  	// Claude declined to respond
  	fmt.Println("Claude was unable to process this request")
  	// Consider rephrasing or modifying the request
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  Message response = client.messages().create(
      MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024L)
          .addUserMessage("[Unsafe request]")
          .build()
  );

  if (response.stopReason().map(StopReason.REFUSAL::equals).orElse(false)) {
      // Claude declined to respond
      IO.println("Claude was unable to process this request");
      // Consider rephrasing or modifying the request
  }

php PHP
  $client = new Client();

  $response = $client->messages->create(
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => '[Unsafe request]']],
      model: 'claude-opus-5',
  );

  if ($response->stopReason === 'refusal') {
      // Claude declined to respond
      echo 'Claude was unable to process this request', PHP_EOL;
      // Consider rephrasing or modifying the request
  }

ruby Ruby
  client = Anthropic::Client.new

  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "[Unsafe request]" }]
  )

  if response.stop_reason == :refusal
    # Claude declined to respond
    puts "Claude was unable to process this request"
    # Consider rephrasing or modifying the request
  end

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 20000,
      "messages": [{"role": "user", "content": "Large input that uses most of context window..."}]
    }' | jq '.stop_reason'

bash CLI
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 20000 \
    --message '{role: user, content: "Large input that uses most of context window..."}' \
    --format json | jq '.stop_reason'

python Python
  # Request with maximum tokens to get as much as possible
  response = client.beta.messages.create(
      model="claude-opus-5",
      max_tokens=20000,  # Python SDK requires streaming for max_tokens above ~21k
      messages=[
          {"role": "user", "content": "Large input that uses most of context window..."}
      ],
  )

  if response.stop_reason == "model_context_window_exceeded":
      # Response hit context window limit before max_tokens
      print("Response reached model's context window limit")
      # The response is still valid but was limited by context window

typescript TypeScript
  // Request with maximum tokens to get as much as possible
  const response = await client.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 20000,
    messages: [{ role: "user", content: "Large input that uses most of context window..." }]
  });

  if (response.stop_reason === "model_context_window_exceeded") {
    // Response hit context window limit before max_tokens
    console.log("Response reached model's context window limit");
    // The response is still valid but was limited by context window
  }

csharp C#
  using Anthropic.Models.Beta.Messages;
  using Model = Anthropic.Models.Messages.Model;

  // Request with maximum tokens to get as much as possible
  var response = await client.Beta.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 20000,
      Messages = [new() { Role = Role.User, Content = "Large input that uses most of context window..." }]
  });

  if (response.StopReason?.Value() == BetaStopReason.ModelContextWindowExceeded)
  {
      // Response hit context window limit before max_tokens
      Console.WriteLine("Response reached model's context window limit");
      // The response is still valid but was limited by context window
  }

go Go
  // Request with maximum tokens to get as much as possible
  response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 20000,
  	Messages: []anthropic.BetaMessageParam{
  		anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("Large input that uses most of context window...")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  if response.StopReason == anthropic.BetaStopReasonModelContextWindowExceeded {
  	// Response hit context window limit before max_tokens
  	fmt.Println("Response reached model's context window limit")
  	// The response is still valid but was limited by context window
  }

java Java
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.BetaStopReason;
  import com.anthropic.models.beta.messages.MessageCreateParams;

  // Request with maximum tokens to get as much as possible
  BetaMessage response = client.beta().messages().create(
      MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(20000L)
          .addUserMessage("Large input that uses most of context window...")
          .build()
  );

  if (response.stopReason().map(BetaStopReason.MODEL_CONTEXT_WINDOW_EXCEEDED::equals).orElse(false)) {
      // Response hit context window limit before max_tokens
      IO.println("Response reached model's context window limit");
      // The response is still valid but was limited by context window
  }

php PHP
  // Request with maximum tokens to get as much as possible
  $response = $client->beta->messages->create(
      maxTokens: 20000,
      messages: [['role' => 'user', 'content' => 'Large input that uses most of context window...']],
      model: 'claude-opus-5',
  );

  if ($response->stopReason === 'model_context_window_exceeded') {
      // Response hit context window limit before max_tokens
      echo 'Response reached model\'s context window limit', PHP_EOL;
      // The response is still valid but was limited by context window
  }

ruby Ruby
  # Request with maximum tokens to get as much as possible
  response = client.beta.messages.create(
    model: "claude-opus-5",
    max_tokens: 20000,
    messages: [{ role: "user", content: "Large input that uses most of context window..." }]
  )

  if response.stop_reason == :model_context_window_exceeded
    # Response hit context window limit before max_tokens
    puts "Response reached model's context window limit"
    # The response is still valid but was limited by context window
  end
  ```
</CodeGroup>


## Best practices for handling stop reasons

Source: https://platform.claude.com/llms-full.txt#best-practices-for-handling-stop-reasons

### Always check stop\_reason

Make it a habit to check the `stop_reason` in your response handling logic:

<CodeGroup exclude="shell">
  ```python Python
  def handle_response(response):
      if response.stop_reason == "tool_use":
          return handle_tool_use(response)
      elif response.stop_reason == "max_tokens":
          return handle_truncation(response)
      elif response.stop_reason == "model_context_window_exceeded":
          return handle_context_limit(response)
      elif response.stop_reason == "pause_turn":
          return handle_pause(response)
      elif response.stop_reason == "refusal":
          return handle_refusal(response)
      else:
          # Handle end_turn and other cases
          return next(
              (block.text for block in response.content if block.type == "text"), ""
          )

typescript TypeScript
  function handleResponse(response: Anthropic.Beta.BetaMessage): string {
    switch (response.stop_reason) {
      case "tool_use":
        return handleToolUse(response);
      case "max_tokens":
        return handleTruncation(response);
      case "model_context_window_exceeded":
        return handleContextLimit(response);
      case "pause_turn":
        return handlePause(response);
      case "refusal":
        return handleRefusal(response);
      default: {
        // Handle end_turn and other cases
        const textBlock = response.content.find(
          (block): block is Anthropic.Beta.BetaTextBlock => block.type === "text"
        );
        return textBlock?.text ?? "";
      }
    }
  }

csharp C#
  static string HandleResponse(BetaMessage response)
  {
      return response.StopReason?.Value() switch
      {
          BetaStopReason.ToolUse => HandleToolUse(response),
          BetaStopReason.MaxTokens => HandleTruncation(response),
          BetaStopReason.ModelContextWindowExceeded => HandleContextLimit(response),
          BetaStopReason.PauseTurn => HandlePause(response),
          BetaStopReason.Refusal => HandleRefusal(response),
          // Handle end_turn and other cases
          _ => response.Content.Select(b => b.Value).OfType<BetaTextBlock>().FirstOrDefault()?.Text ?? "",
      };
  }

go Go
  func handleResponse(response *anthropic.BetaMessage) string {
  	switch response.StopReason {
  	case anthropic.BetaStopReasonToolUse:
  		return handleToolUse(response)
  	case anthropic.BetaStopReasonMaxTokens:
  		return handleTruncation(response)
  	case anthropic.BetaStopReasonModelContextWindowExceeded:
  		return handleContextLimit(response)
  	case anthropic.BetaStopReasonPauseTurn:
  		return handlePause(response)
  	case anthropic.BetaStopReasonRefusal:
  		return handleRefusal(response)
  	default:
  		// Handle end_turn and other cases
  		for _, block := range response.Content {
  			if textBlock, ok := block.AsAny().(anthropic.BetaTextBlock); ok {
  				return textBlock.Text
  			}
  		}
  		return ""
  	}
  }

java Java
  static String handleResponse(BetaMessage response) {
      BetaStopReason reason = response.stopReason().orElse(BetaStopReason.END_TURN);
      if (reason.equals(BetaStopReason.TOOL_USE)) {
          return handleToolUse(response);
      } else if (reason.equals(BetaStopReason.MAX_TOKENS)) {
          return handleTruncation(response);
      } else if (reason.equals(BetaStopReason.MODEL_CONTEXT_WINDOW_EXCEEDED)) {
          return handleContextLimit(response);
      } else if (reason.equals(BetaStopReason.PAUSE_TURN)) {
          return handlePause(response);
      } else if (reason.equals(BetaStopReason.REFUSAL)) {
          return handleRefusal(response);
      }
      // Handle end_turn and other cases
      return response.content().stream()
          .filter(BetaContentBlock::isText)
          .findFirst()
          .map(block -> block.asText().text())
          .orElse("");
  }

php PHP
  function handle_response($response): string
  {
      return match ($response->stopReason) {
          'tool_use' => handle_tool_use($response),
          'max_tokens' => handle_truncation($response),
          'model_context_window_exceeded' => handle_context_limit($response),
          'pause_turn' => handle_pause($response),
          'refusal' => handle_refusal($response),
          // Handle end_turn and other cases
          default => array_find($response->content, static fn ($block): bool => $block->type === 'text')?->text ?? '',
      };
  }

ruby Ruby
  def handle_response(response)
    case response.stop_reason
    when :tool_use then handle_tool_use(response)
    when :max_tokens then handle_truncation(response)
    when :model_context_window_exceeded then handle_context_limit(response)
    when :pause_turn then handle_pause(response)
    when :refusal then handle_refusal(response)
    else
      # Handle end_turn and other cases
      response.content.find { it.type == :text }&.text
    end
  end

python Python
  def handle_truncated_response(response):
      text = next((block.text for block in response.content if block.type == "text"), "")
      if response.stop_reason in ["max_tokens", "model_context_window_exceeded"]:
          if response.stop_reason == "max_tokens":
              note = "[Response truncated due to max_tokens limit]"
          else:
              note = "[Response truncated due to context window limit]"
          return f"{text}\n\n{note}"
      return text

typescript TypeScript
  function handleTruncatedResponse(response: Anthropic.Beta.BetaMessage): string {
    const textBlock = response.content.find(
      (block): block is Anthropic.Beta.BetaTextBlock => block.type === "text"
    );
    const text = textBlock?.text ?? "";

    if (
      response.stop_reason === "max_tokens" ||
      response.stop_reason === "model_context_window_exceeded"
    ) {
      const note =
        response.stop_reason === "max_tokens"
          ? "[Response truncated due to max_tokens limit]"
          : "[Response truncated due to context window limit]";
      return `${text}\n\n${note}`;
    }
    return text;
  }

csharp C#
  static string HandleTruncatedResponse(BetaMessage response)
  {
      var text = response.Content.Select(b => b.Value).OfType<BetaTextBlock>().FirstOrDefault()?.Text ?? "";
      var reason = response.StopReason?.Value();

      if (reason is BetaStopReason.MaxTokens or BetaStopReason.ModelContextWindowExceeded)
      {
          var note = reason == BetaStopReason.MaxTokens
              ? "[Response truncated due to max_tokens limit]"
              : "[Response truncated due to context window limit]";
          return $"{text}\n\n{note}";
      }
      return text;
  }

go Go
  func handleTruncatedResponse(response *anthropic.BetaMessage) string {
  	text := ""
  	for _, block := range response.Content {
  		if textBlock, ok := block.AsAny().(anthropic.BetaTextBlock); ok {
  			text = textBlock.Text
  			break
  		}
  	}

  	if response.StopReason == anthropic.BetaStopReasonMaxTokens ||
  		response.StopReason == anthropic.BetaStopReasonModelContextWindowExceeded {
  		note := "[Response truncated due to context window limit]"
  		if response.StopReason == anthropic.BetaStopReasonMaxTokens {
  			note = "[Response truncated due to max_tokens limit]"
  		}
  		return text + "\n\n" + note
  	}
  	return text
  }

java Java
  static String handleTruncatedResponse(BetaMessage response) {
      String text = response.content().stream()
          .filter(BetaContentBlock::isText)
          .findFirst()
          .map(block -> block.asText().text())
          .orElse("");
      BetaStopReason reason = response.stopReason().orElse(BetaStopReason.END_TURN);

      if (reason.equals(BetaStopReason.MAX_TOKENS)
              || reason.equals(BetaStopReason.MODEL_CONTEXT_WINDOW_EXCEEDED)) {
          String note = reason.equals(BetaStopReason.MAX_TOKENS)
              ? "[Response truncated due to max_tokens limit]"
              : "[Response truncated due to context window limit]";
          return text + "\n\n" + note;
      }
      return text;
  }

php PHP
  function handle_truncated_response($response): string
  {
      $text = array_find($response->content, static fn ($block): bool => $block->type === 'text')?->text ?? '';

      if (in_array($response->stopReason, ['max_tokens', 'model_context_window_exceeded'], true)) {
          $note = $response->stopReason === 'max_tokens'
              ? '[Response truncated due to max_tokens limit]'
              : '[Response truncated due to context window limit]';
          return "{$text}\n\n{$note}";
      }
      return $text;
  }

ruby Ruby
  def handle_truncated_response(response)
    text = response.content.find { it.type == :text }&.text

    if [:max_tokens, :model_context_window_exceeded].include?(response.stop_reason)
      note = if response.stop_reason == :max_tokens
        "[Response truncated due to max_tokens limit]"
      else
        "[Response truncated due to context window limit]"
      end
      return "#{text}\n\n#{note}"
    end
    text
  end

python Python
  def handle_server_tool_conversation(client, user_query, tools, max_continuations=5):
      """
      Handle server tool conversations that may require multiple continuations.

      The server runs a sampling loop when executing server tools. If the loop
      reaches its iteration limit, the API returns pause_turn. Continue the
      conversation by sending the response back to let Claude finish.
      """
      messages = [{"role": "user", "content": user_query}]

      for _ in range(max_continuations):
          response = client.messages.create(
              model="claude-opus-5", max_tokens=4096, messages=messages, tools=tools
          )

          if response.stop_reason != "pause_turn":
              # Claude finished processing - return the final response
              return response

          # pause_turn: replace the full message list to maintain alternating roles
          messages = [
              {"role": "user", "content": user_query},
              {"role": "assistant", "content": response.content},
          ]

      # Reached max continuations - return the last response
      return response

typescript TypeScript
  async function handleServerToolConversation(
    client: Anthropic,
    userQuery: string,
    tools: Anthropic.ToolUnion[],
    maxContinuations = 5
  ): Promise<Anthropic.Message> {
    let messages: Anthropic.MessageParam[] = [{ role: "user", content: userQuery }];
    let response: Anthropic.Message;

    for (let i = 0; i < maxContinuations; i++) {
      response = await client.messages.create({
        model: "claude-opus-5",
        max_tokens: 4096,
        messages,
        tools
      });

      if (response.stop_reason !== "pause_turn") {
        // Claude finished processing - return the final response
        return response;
      }

      // pause_turn: replace the full message list to maintain alternating roles
      messages = [
        { role: "user", content: userQuery },
        { role: "assistant", content: response.content }
      ];
    }

    // Reached max continuations - return the last response
    return response!;
  }

csharp C#
  static async Task<Message> HandleServerToolConversation(
      AnthropicClient client,
      string userQuery,
      List<ToolUnion> tools,
      int maxContinuations = 5)
  {
      List<MessageParam> messages = [new() { Role = Role.User, Content = userQuery }];
      Message response = null!;

      for (var i = 0; i < maxContinuations; i++)
      {
          response = await client.Messages.Create(new MessageCreateParams
          {
              Model = Model.ClaudeOpus5,
              MaxTokens = 4096,
              Messages = messages,
              Tools = tools
          });

          if (response.StopReason != "pause_turn")
          {
              // Claude finished processing - return the final response
              return response;
          }

          // pause_turn: replace the full message list to maintain alternating roles
          messages =
          [
              new() { Role = Role.User, Content = userQuery },
              new()
              {
                  Role = Role.Assistant,
                  Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList()
              }
          ];
      }

      // Reached max continuations - return the last response
      return response;
  }

go Go
  func handleServerToolConversation(
  	client anthropic.Client,
  	userQuery string,
  	tools []anthropic.ToolUnionParam,
  	maxContinuations int,
  ) (*anthropic.Message, error) {
  	messages := []anthropic.MessageParam{anthropic.NewUserMessage(anthropic.NewTextBlock(userQuery))}
  	var response *anthropic.Message
  	var err error

  	for range maxContinuations {
  		response, err = client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  			Model:     anthropic.ModelClaudeOpus5,
  			MaxTokens: 4096,
  			Messages:  messages,
  			Tools:     tools,
  		})
  		if err != nil {
  			return nil, err
  		}

  		if response.StopReason != "pause_turn" {
  			// Claude finished processing - return the final response
  			return response, nil
  		}

  		// pause_turn: replace the full message list to maintain alternating roles
  		var contentParams []anthropic.ContentBlockParamUnion
  		for _, block := range response.Content {
  			contentParams = append(contentParams, block.ToParam())
  		}
  		messages = []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock(userQuery)),
  			anthropic.NewAssistantMessage(contentParams...),
  		}
  	}

  	// Reached max continuations - return the last response
  	return response, nil
  }

java Java
  static Message handleServerToolConversation(
      AnthropicClient client,
      String userQuery,
      List<Tool> tools,
      int maxContinuations
  ) {
      Message response = null;

      for (int i = 0; i < maxContinuations; i++) {
          // Rebuild the params each iteration so messages aren't accumulated
          MessageCreateParams.Builder params = MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(4096L)
              .addUserMessage(userQuery);
          tools.forEach(params::addTool);
          if (response != null) {
              params.addMessage(response);
          }

          response = client.messages().create(params.build());

          if (!response.stopReason().map(StopReason.PAUSE_TURN::equals).orElse(false)) {
              // Claude finished processing - return the final response
              return response;
          }
          // pause_turn: loop again and send the response back
      }

      // Reached max continuations - return the last response
      return response;
  }

php PHP
  function handle_server_tool_conversation(
      Client $client,
      string $userQuery,
      array $tools,
      int $maxContinuations = 5
  ) {
      $messages = [['role' => 'user', 'content' => $userQuery]];
      $response = null;

      for ($i = 0; $i < $maxContinuations; $i++) {
          $response = $client->messages->create(
              maxTokens: 4096,
              messages: $messages,
              model: 'claude-opus-5',
              tools: $tools,
          );

          if ($response->stopReason !== 'pause_turn') {
              // Claude finished processing - return the final response
              return $response;
          }

          // pause_turn: replace the full message list to maintain alternating roles
          $messages = [
              ['role' => 'user', 'content' => $userQuery],
              ['role' => 'assistant', 'content' => $response->content],
          ];
      }

      // Reached max continuations - return the last response
      return $response;
  }

ruby Ruby
  def handle_server_tool_conversation(client, user_query, tools, max_continuations: 5)
    messages = [{ role: "user", content: user_query }]
    response = nil

    max_continuations.times do
      response = client.messages.create(
        model: "claude-opus-5",
        max_tokens: 4096,
        messages: messages,
        tools: tools
      )

      # Claude finished processing - return the final response
      return response unless response.stop_reason == :pause_turn

      # pause_turn: replace the full message list to maintain alternating roles
      messages = [
        { role: "user", content: user_query },
        { role: "assistant", content: response.content }
      ]
    end

    # Reached max continuations - return the last response
    response
  end
  ```
</CodeGroup>


## Stop reasons vs. errors

Source: https://platform.claude.com/llms-full.txt#stop-reasons-vs-errors

It's important to distinguish between `stop_reason` values and actual errors:

### Stop reasons (successful responses)

* Part of the response body
* Indicate why generation stopped normally
* Response contains valid content

### Errors (failed requests)

* HTTP status codes 4xx or 5xx
* Indicate request processing failures
* Response contains error details

<CodeGroup>
  ```bash cURL
  # cURL exits non-zero on HTTP errors with --fail-with-body; inspect
  # $? for errors and stop_reason for successful responses.
  curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello!"}]
    }' | jq '.stop_reason'

bash CLI
  # The CLI exits non-zero on API errors; stop_reason appears on success.
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello!"}' \
    --format json | jq '.stop_reason'

python Python
  client = anthropic.Anthropic()

  try:
      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          messages=[{"role": "user", "content": "Hello!"}],
      )

      # Handle successful response with stop_reason
      if response.stop_reason == "max_tokens":
          print("Response was truncated")

  except anthropic.APIStatusError as e:
      # Handle actual errors
      if e.status_code == 429:
          print("Rate limit exceeded")
      elif e.status_code == 500:
          print("Server error")

typescript TypeScript
  const client = new Anthropic();

  try {
    const response = await client.messages.create({
      model: "claude-opus-5",
      max_tokens: 1024,
      messages: [{ role: "user", content: "Hello!" }]
    });

    // Handle successful response with stop_reason
    if (response.stop_reason === "max_tokens") {
      console.log("Response was truncated");
    }
  } catch (err) {
    // Handle actual errors
    if (err instanceof Anthropic.APIError) {
      if (err.status === 429) {
        console.log("Rate limit exceeded");
      } else if (err.status === 500) {
        console.log("Server error");
      }
    } else {
      throw err;
    }
  }

csharp C#
  AnthropicClient client = new();

  try
  {
      var response = await client.Messages.Create(new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages = [new() { Role = Role.User, Content = "Hello!" }]
      });

      // Handle successful response with stop_reason
      if (response.StopReason == "max_tokens")
      {
          Console.WriteLine("Response was truncated");
      }
  }
  catch (AnthropicRateLimitException)
  {
      // Handle actual errors
      Console.WriteLine("Rate limit exceeded");
  }
  catch (Anthropic5xxException)
  {
      Console.WriteLine("Server error");
  }

go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello!")),
  	},
  })
  if err != nil {
  	// Handle actual errors
  	var apiErr *anthropic.Error
  	if errors.As(err, &apiErr) {
  		switch apiErr.StatusCode {
  		case 429:
  			fmt.Println("Rate limit exceeded")
  		case 500:
  			fmt.Println("Server error")
  		}
  	}
  	log.Fatal(err)
  }

  // Handle successful response with stop_reason
  if response.StopReason == "max_tokens" {
  	fmt.Println("Response was truncated")
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  try {
      Message response = client.messages().create(
          MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024L)
              .addUserMessage("Hello!")
              .build()
      );

      // Handle successful response with stop_reason
      if (response.stopReason().map(StopReason.MAX_TOKENS::equals).orElse(false)) {
          IO.println("Response was truncated");
      }
  } catch (RateLimitException e) {
      // Handle actual errors
      IO.println("Rate limit exceeded");
  } catch (AnthropicServiceException e) {
      if (e.statusCode() == 500) {
          IO.println("Server error");
      }
  }

php PHP
  $client = new Client();

  try {
      $response = $client->messages->create(
          maxTokens: 1024,
          messages: [['role' => 'user', 'content' => 'Hello!']],
          model: 'claude-opus-5',
      );

      // Handle successful response with stop_reason
      if ($response->stopReason === 'max_tokens') {
          echo 'Response was truncated', PHP_EOL;
      }
  } catch (RateLimitException $e) {
      // Handle actual errors
      echo 'Rate limit exceeded', PHP_EOL;
  } catch (InternalServerException $e) {
      echo 'Server error', PHP_EOL;
  }

ruby Ruby
  client = Anthropic::Client.new

  begin
    response = client.messages.create(
      model: "claude-opus-5",
      max_tokens: 1024,
      messages: [{ role: "user", content: "Hello!" }]
    )

    # Handle successful response with stop_reason
    if response.stop_reason == :max_tokens
      puts "Response was truncated"
    end
  rescue Anthropic::Errors::RateLimitError
    # Handle actual errors
    puts "Rate limit exceeded"
  rescue Anthropic::Errors::APIStatusError => e
    puts "Server error" if e.status == 500
  end
  ```
</CodeGroup>


## Streaming considerations

Source: https://platform.claude.com/llms-full.txt#streaming-considerations

When using streaming, `stop_reason` is:

* `null` in the initial `message_start` event
* Provided in the `message_delta` event
* Not provided in any other events

<CodeGroup>
  ```bash cURL
  # The message_delta event in the SSE stream carries stop_reason.
  curl --no-buffer https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "stream": true,
      "messages": [{"role": "user", "content": "Hello!"}]
    }'

bash CLI
  # stop_reason appears in the message_delta event.
  ant messages create --stream --format jsonl \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello!"}' |
    jq -c 'select(.type == "message_delta") | .delta.stop_reason'

python Python
  client = anthropic.Anthropic()

  with client.messages.stream(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello!"}],
  ) as stream:
      for event in stream:
          if event.type == "message_delta":
              stop_reason = event.delta.stop_reason
              if stop_reason:
                  print(f"Stream ended with: {stop_reason}")

typescript TypeScript
  const client = new Anthropic();

  const stream = client.messages.stream({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello!" }]
  });

  for await (const event of stream) {
    if (event.type === "message_delta" && event.delta.stop_reason) {
      console.log(`Stream ended with: ${event.delta.stop_reason}`);
    }
  }

csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello!" }]
  };

  await foreach (var streamEvent in client.Messages.CreateStreaming(parameters))
  {
      switch (streamEvent.Value)
      {
          case RawMessageDeltaEvent deltaEvent when deltaEvent.Delta.StopReason is not null:
              Console.WriteLine($"Stream ended with: {deltaEvent.Delta.StopReason}");
              break;
      }
  }

go Go
  client := anthropic.NewClient()

  stream := client.Messages.NewStreaming(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello!")),
  	},
  })

  // Accumulate events into the final Message, which carries stop_reason.
  message := anthropic.Message{}
  for stream.Next() {
  	if err := message.Accumulate(stream.Current()); err != nil {
  		log.Fatal(err)
  	}
  }
  if err := stream.Err(); err != nil {
  	log.Fatal(err)
  }

  if message.StopReason != "" {
  	fmt.Printf("Stream ended with: %s\n", message.StopReason)
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  MessageCreateParams params = MessageCreateParams.builder()
      .model(Model.CLAUDE_OPUS_5)
      .maxTokens(1024L)
      .addUserMessage("Hello!")
      .build();

  // Accumulate events into the final Message, which carries stop_reason.
  MessageAccumulator accumulator = MessageAccumulator.create();
  try (StreamResponse<RawMessageStreamEvent> streamResponse =
          client.messages().createStreaming(params)) {
      streamResponse.stream().forEach(accumulator::accumulate);
  }

  accumulator.message().stopReason().ifPresent(stopReason ->
      IO.println("Stream ended with: " + stopReason)
  );

php PHP
  $client = new Client();

  $stream = $client->messages->createStream(
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello!']],
      model: 'claude-opus-5',
  );

  foreach ($stream as $event) {
      if ($event instanceof RawMessageDeltaEvent && $event->delta->stopReason !== null) {
          echo "Stream ended with: {$event->delta->stopReason}", PHP_EOL;
      }
  }

ruby Ruby
  client = Anthropic::Client.new

  stream = client.messages.stream(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello!" }]
  )

  stream.each do |event|
    next unless event.type == :message_delta
    stop_reason = event.delta.stop_reason
    puts "Stream ended with: #{stop_reason}" if stop_reason
  end
  ```
</CodeGroup>


## Common patterns

Source: https://platform.claude.com/llms-full.txt#common-patterns

### Handling tool use workflows

<Tip>
  **Simpler with tool runner:** The following example shows manual tool handling. For most use cases, the [tool runner](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner) automatically handles tool execution with much less code.
</Tip>

<CodeGroup exclude="shell">
  ```python Python
  def complete_tool_workflow(client, user_query, tools):
      messages = [{"role": "user", "content": user_query}]

      while True:
          response = client.messages.create(
              model="claude-opus-5", max_tokens=1024, messages=messages, tools=tools
          )

          if response.stop_reason == "tool_use":
              # Execute tools and continue
              tool_results = execute_tools(response.content)
              messages.append({"role": "assistant", "content": response.content})
              messages.append({"role": "user", "content": tool_results})
          else:
              # Final response
              return response

typescript TypeScript
  async function completeToolWorkflow(
    client: Anthropic,
    userQuery: string,
    tools: Anthropic.ToolUnion[]
  ): Promise<Anthropic.Message> {
    const messages: Anthropic.MessageParam[] = [{ role: "user", content: userQuery }];

    while (true) {
      const response = await client.messages.create({
        model: "claude-opus-5",
        max_tokens: 1024,
        messages,
        tools
      });

      if (response.stop_reason === "tool_use") {
        // Execute tools and continue
        const toolResults = executeTools(response.content);
        messages.push({ role: "assistant", content: response.content });
        messages.push({ role: "user", content: toolResults });
      } else {
        // Final response
        return response;
      }
    }
  }

csharp C#
  static async Task<Message> CompleteToolWorkflow(
      AnthropicClient client,
      string userQuery,
      List<ToolUnion> tools)
  {
      List<MessageParam> messages = [new() { Role = Role.User, Content = userQuery }];

      while (true)
      {
          var response = await client.Messages.Create(new MessageCreateParams
          {
              Model = Model.ClaudeOpus5,
              MaxTokens = 1024,
              Messages = messages,
              Tools = tools
          });

          if (response.StopReason == "tool_use")
          {
              // Execute tools and continue
              var toolResults = ExecuteTools(response.Content);
              messages.Add(new()
              {
                  Role = Role.Assistant,
                  Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList()
              });
              messages.Add(new() { Role = Role.User, Content = toolResults });
          }
          else
          {
              // Final response
              return response;
          }
      }
  }

go Go
  func completeToolWorkflow(
  	client anthropic.Client,
  	userQuery string,
  	tools []anthropic.ToolUnionParam,
  ) (*anthropic.Message, error) {
  	messages := []anthropic.MessageParam{anthropic.NewUserMessage(anthropic.NewTextBlock(userQuery))}

  	for {
  		response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  			Model:     anthropic.ModelClaudeOpus5,
  			MaxTokens: 1024,
  			Messages:  messages,
  			Tools:     tools,
  		})
  		if err != nil {
  			return nil, err
  		}

  		if response.StopReason != "tool_use" {
  			// Final response
  			return response, nil
  		}

  		// Execute tools and continue
  		toolResults := executeTools(response.Content)
  		var contentParams []anthropic.ContentBlockParamUnion
  		for _, block := range response.Content {
  			contentParams = append(contentParams, block.ToParam())
  		}
  		messages = append(messages, anthropic.NewAssistantMessage(contentParams...))
  		messages = append(messages, anthropic.NewUserMessage(toolResults...))
  	}
  }

java Java
  static Message completeToolWorkflow(
      AnthropicClient client,
      String userQuery,
      List<Tool> tools
  ) {
      List<MessageParam> messages = new ArrayList<>();
      messages.add(MessageParam.builder().role(MessageParam.Role.USER).content(userQuery).build());

      while (true) {
          MessageCreateParams.Builder params = MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024L)
              .messages(messages);
          tools.forEach(params::addTool);

          Message response = client.messages().create(params.build());

          if (!response.stopReason().map(StopReason.TOOL_USE::equals).orElse(false)) {
              // Final response
              return response;
          }

          // Execute tools and continue
          List<ToolResultBlockParam> toolResults = executeTools(response.content());
          messages.add(response.toParam());
          messages.add(MessageParam.builder()
              .role(MessageParam.Role.USER)
              .contentOfBlockParams(toolResults.stream().map(ContentBlockParam::ofToolResult).toList())
              .build());
      }
  }

php PHP
  function complete_tool_workflow(Client $client, string $userQuery, array $tools)
  {
      $messages = [['role' => 'user', 'content' => $userQuery]];

      while (true) {
          $response = $client->messages->create(
              maxTokens: 1024,
              messages: $messages,
              model: 'claude-opus-5',
              tools: $tools,
          );

          if ($response->stopReason !== 'tool_use') {
              // Final response
              return $response;
          }

          // Execute tools and continue
          $toolResults = execute_tools($response->content);
          $messages[] = ['role' => 'assistant', 'content' => $response->content];
          $messages[] = ['role' => 'user', 'content' => $toolResults];
      }
  }

ruby Ruby
  def complete_tool_workflow(client, user_query, tools)
    messages = [{ role: "user", content: user_query }]

    loop do
      response = client.messages.create(
        model: "claude-opus-5",
        max_tokens: 1024,
        messages: messages,
        tools: tools
      )

      # Final response
      return response unless response.stop_reason == :tool_use

      # Execute tools and continue
      tool_results = execute_tools(response.content)
      messages << { role: "assistant", content: response.content }
      messages << { role: "user", content: tool_results }
    end
  end

python Python
  def get_complete_response(client, prompt, max_attempts=3):
      messages = [{"role": "user", "content": prompt}]
      full_response = ""

      for _ in range(max_attempts):
          response = client.messages.create(
              model="claude-opus-5", messages=messages, max_tokens=4096
          )

          full_response += next(
              (block.text for block in response.content if block.type == "text"), ""
          )

          if response.stop_reason != "max_tokens":
              break

          # Continue from where it left off
          messages = [
              {"role": "user", "content": prompt},
              {"role": "assistant", "content": full_response},
              {"role": "user", "content": "Please continue from where you left off."},
          ]

      return full_response

typescript TypeScript
  async function getCompleteResponse(
    client: Anthropic,
    prompt: string,
    maxAttempts = 3
  ): Promise<string> {
    let messages: Anthropic.MessageParam[] = [{ role: "user", content: prompt }];
    let fullResponse = "";

    for (let i = 0; i < maxAttempts; i++) {
      const response = await client.messages.create({
        model: "claude-opus-5",
        max_tokens: 4096,
        messages
      });

      const textBlock = response.content.find(
        (block): block is Anthropic.TextBlock => block.type === "text"
      );
      fullResponse += textBlock?.text ?? "";

      if (response.stop_reason !== "max_tokens") {
        break;
      }

      // Continue from where it left off
      messages = [
        { role: "user", content: prompt },
        { role: "assistant", content: fullResponse },
        { role: "user", content: "Please continue from where you left off." }
      ];
    }

    return fullResponse;
  }

csharp C#
  static async Task<string> GetCompleteResponse(AnthropicClient client, string prompt, int maxAttempts = 3)
  {
      List<MessageParam> messages = [new() { Role = Role.User, Content = prompt }];
      var fullResponse = "";

      for (var i = 0; i < maxAttempts; i++)
      {
          var response = await client.Messages.Create(new MessageCreateParams
          {
              Model = Model.ClaudeOpus5,
              MaxTokens = 4096,
              Messages = messages
          });

          foreach (var block in response.Content)
          {
              if (block.TryPickText(out var textBlock))
              {
                  fullResponse += textBlock.Text;
                  break;
              }
          }

          if (response.StopReason != "max_tokens")
          {
              break;
          }

          // Continue from where it left off
          messages =
          [
              new() { Role = Role.User, Content = prompt },
              new() { Role = Role.Assistant, Content = fullResponse },
              new() { Role = Role.User, Content = "Please continue from where you left off." }
          ];
      }

      return fullResponse;
  }

go Go
  func getCompleteResponse(client anthropic.Client, prompt string, maxAttempts int) (string, error) {
  	messages := []anthropic.MessageParam{anthropic.NewUserMessage(anthropic.NewTextBlock(prompt))}
  	fullResponse := ""

  	for range maxAttempts {
  		response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  			Model:     anthropic.ModelClaudeOpus5,
  			MaxTokens: 4096,
  			Messages:  messages,
  		})
  		if err != nil {
  			return "", err
  		}

  		for _, block := range response.Content {
  			if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  				fullResponse += textBlock.Text
  				break
  			}
  		}

  		if response.StopReason != "max_tokens" {
  			break
  		}

  		// Continue from where it left off
  		messages = []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock(prompt)),
  			anthropic.NewAssistantMessage(anthropic.NewTextBlock(fullResponse)),
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Please continue from where you left off.")),
  		}
  	}

  	return fullResponse, nil
  }

java Java
  static String getCompleteResponse(AnthropicClient client, String prompt, int maxAttempts) {
      List<MessageParam> messages = List.of(
          MessageParam.builder().role(MessageParam.Role.USER).content(prompt).build()
      );
      StringBuilder fullResponse = new StringBuilder();

      for (int i = 0; i < maxAttempts; i++) {
          Message response = client.messages().create(
              MessageCreateParams.builder()
                  .model(Model.CLAUDE_OPUS_5)
                  .maxTokens(4096L)
                  .messages(messages)
                  .build()
          );

          response.content().stream()
              .filter(ContentBlock::isText)
              .findFirst()
              .ifPresent(block -> fullResponse.append(block.asText().text()));

          if (!response.stopReason().map(StopReason.MAX_TOKENS::equals).orElse(false)) {
              break;
          }

          // Continue from where it left off
          messages = List.of(
              MessageParam.builder().role(MessageParam.Role.USER).content(prompt).build(),
              MessageParam.builder().role(MessageParam.Role.ASSISTANT).content(fullResponse.toString()).build(),
              MessageParam.builder().role(MessageParam.Role.USER).content("Please continue from where you left off.").build()
          );
      }

      return fullResponse.toString();
  }

php PHP
  function get_complete_response(Client $client, string $prompt, int $maxAttempts = 3): string
  {
      $messages = [['role' => 'user', 'content' => $prompt]];
      $fullResponse = '';

      for ($i = 0; $i < $maxAttempts; $i++) {
          $response = $client->messages->create(
              maxTokens: 4096,
              messages: $messages,
              model: 'claude-opus-5',
          );

          $fullResponse .= array_find($response->content, static fn ($block): bool => $block->type === 'text')?->text ?? '';

          if ($response->stopReason !== 'max_tokens') {
              break;
          }

          // Continue from where it left off
          $messages = [
              ['role' => 'user', 'content' => $prompt],
              ['role' => 'assistant', 'content' => $fullResponse],
              ['role' => 'user', 'content' => 'Please continue from where you left off.'],
          ];
      }

      return $fullResponse;
  }

ruby Ruby
  def get_complete_response(client, prompt, max_attempts: 3)
    messages = [{ role: "user", content: prompt }]
    full_response = +""

    max_attempts.times do
      response = client.messages.create(
        model: "claude-opus-5",
        max_tokens: 4096,
        messages: messages
      )

      full_response << response.content.find { it.type == :text }&.text.to_s

      break unless response.stop_reason == :max_tokens

      # Continue from where it left off
      messages = [
        { role: "user", content: prompt },
        { role: "assistant", content: full_response },
        { role: "user", content: "Please continue from where you left off." }
      ]
    end

    full_response
  end

python Python
  def get_max_possible_tokens(client, prompt):
      """
      Get as many tokens as possible within the model's context window
      without needing to calculate input token count
      """
      response = client.beta.messages.create(
          model="claude-opus-5",
          messages=[{"role": "user", "content": prompt}],
          max_tokens=20000,  # Python SDK requires streaming for max_tokens above ~21k
      )

      if response.stop_reason == "model_context_window_exceeded":
          # Got the maximum possible tokens given input size
          print(
              f"Generated {response.usage.output_tokens} tokens (context limit reached)"
          )
      elif response.stop_reason == "max_tokens":
          # Got exactly the requested tokens
          print(f"Generated {response.usage.output_tokens} tokens (max_tokens reached)")
      else:
          # Natural completion
          print(f"Generated {response.usage.output_tokens} tokens (natural completion)")

      return next((block.text for block in response.content if block.type == "text"), "")

typescript TypeScript
  async function getMaxPossibleTokens(client: Anthropic, prompt: string): Promise<string> {
    const response = await client.beta.messages.create({
      model: "claude-opus-5",
      max_tokens: 20000,
      messages: [{ role: "user", content: prompt }]
    });

    const tokens = response.usage.output_tokens;
    if (response.stop_reason === "model_context_window_exceeded") {
      // Got the maximum possible tokens given input size
      console.log(`Generated ${tokens} tokens (context limit reached)`);
    } else if (response.stop_reason === "max_tokens") {
      // Got exactly the requested tokens
      console.log(`Generated ${tokens} tokens (max_tokens reached)`);
    } else {
      // Natural completion
      console.log(`Generated ${tokens} tokens (natural completion)`);
    }

    const textBlock = response.content.find(
      (block): block is Anthropic.Beta.BetaTextBlock => block.type === "text"
    );
    return textBlock?.text ?? "";
  }

csharp C#
  using Anthropic.Models.Beta.Messages;
  using Model = Anthropic.Models.Messages.Model;

  static async Task<string> GetMaxPossibleTokens(AnthropicClient client, string prompt)
  {
      var response = await client.Beta.Messages.Create(new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 20000,
          Messages = [new() { Role = Role.User, Content = prompt }]
      });

      var tokens = response.Usage.OutputTokens;
      var reason = response.StopReason?.Value();
      if (reason == BetaStopReason.ModelContextWindowExceeded)
      {
          // Got the maximum possible tokens given input size
          Console.WriteLine($"Generated {tokens} tokens (context limit reached)");
      }
      else if (reason == BetaStopReason.MaxTokens)
      {
          // Got exactly the requested tokens
          Console.WriteLine($"Generated {tokens} tokens (max_tokens reached)");
      }
      else
      {
          // Natural completion
          Console.WriteLine($"Generated {tokens} tokens (natural completion)");
      }

      return response.Content.Select(b => b.Value).OfType<BetaTextBlock>().FirstOrDefault()?.Text ?? "";
  }

go Go
  func getMaxPossibleTokens(client anthropic.Client, prompt string) (string, error) {
  	response, err := client.Beta.Messages.New(context.TODO(), anthropic.BetaMessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 20000,
  		Messages: []anthropic.BetaMessageParam{
  			anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock(prompt)),
  		},
  	})
  	if err != nil {
  		return "", err
  	}

  	tokens := response.Usage.OutputTokens
  	switch response.StopReason {
  	case anthropic.BetaStopReasonModelContextWindowExceeded:
  		// Got the maximum possible tokens given input size
  		fmt.Printf("Generated %d tokens (context limit reached)\n", tokens)
  	case anthropic.BetaStopReasonMaxTokens:
  		// Got exactly the requested tokens
  		fmt.Printf("Generated %d tokens (max_tokens reached)\n", tokens)
  	default:
  		// Natural completion
  		fmt.Printf("Generated %d tokens (natural completion)\n", tokens)
  	}

  	for _, block := range response.Content {
  		if textBlock, ok := block.AsAny().(anthropic.BetaTextBlock); ok {
  			return textBlock.Text, nil
  		}
  	}
  	return "", nil
  }

java Java
  import com.anthropic.models.beta.messages.BetaContentBlock;
  import com.anthropic.models.beta.messages.BetaMessage;
  import com.anthropic.models.beta.messages.BetaStopReason;
  import com.anthropic.models.beta.messages.MessageCreateParams;

  static String getMaxPossibleTokens(AnthropicClient client, String prompt) {
      BetaMessage response = client.beta().messages().create(
          MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(20000L)
              .addUserMessage(prompt)
              .build()
      );

      long tokens = response.usage().outputTokens();
      BetaStopReason reason = response.stopReason().orElse(BetaStopReason.END_TURN);
      if (reason.equals(BetaStopReason.MODEL_CONTEXT_WINDOW_EXCEEDED)) {
          // Got the maximum possible tokens given input size
          IO.println("Generated " + tokens + " tokens (context limit reached)");
      } else if (reason.equals(BetaStopReason.MAX_TOKENS)) {
          // Got exactly the requested tokens
          IO.println("Generated " + tokens + " tokens (max_tokens reached)");
      } else {
          // Natural completion
          IO.println("Generated " + tokens + " tokens (natural completion)");
      }

      return response.content().stream()
          .filter(BetaContentBlock::isText)
          .findFirst()
          .map(block -> block.asText().text())
          .orElse("");
  }

php PHP
  function get_max_possible_tokens(Client $client, string $prompt): string
  {
      $response = $client->beta->messages->create(
          maxTokens: 20000,
          messages: [['role' => 'user', 'content' => $prompt]],
          model: 'claude-opus-5',
      );

      $tokens = $response->usage->outputTokens;
      echo match ($response->stopReason) {
          // Got the maximum possible tokens given input size
          'model_context_window_exceeded' => "Generated {$tokens} tokens (context limit reached)",
          // Got exactly the requested tokens
          'max_tokens' => "Generated {$tokens} tokens (max_tokens reached)",
          // Natural completion
          default => "Generated {$tokens} tokens (natural completion)",
      }, PHP_EOL;

      return array_find($response->content, static fn ($block): bool => $block->type === 'text')?->text ?? '';
  }

ruby Ruby
  def get_max_possible_tokens(client, prompt)
    response = client.beta.messages.create(
      model: "claude-opus-5",
      max_tokens: 20000,
      messages: [{ role: "user", content: prompt }]
    )

    tokens = response.usage.output_tokens
    case response.stop_reason
    when :model_context_window_exceeded
      # Got the maximum possible tokens given input size
      puts "Generated #{tokens} tokens (context limit reached)"
    when :max_tokens
      # Got exactly the requested tokens
      puts "Generated #{tokens} tokens (max_tokens reached)"
    else
      # Natural completion
      puts "Generated #{tokens} tokens (natural completion)"
    end

    response.content.find { it.type == :text }.text
  end
  ```
</CodeGroup>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-5

<CardGroup cols={2}>
  <Card title="Refusals and fallback" icon="arrows-clockwise" href="https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback">
    Retry refused requests on a fallback model, server-side or in your client.
  </Card>

  <Card title="Tool Runner (SDK)" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner">
    Let the SDK manage the `tool_use` loop, result formatting, and retries for you.
  </Card>

  <Card title="Streaming messages" icon="lightning" href="https://platform.claude.com/docs/en/build-with-claude/streaming">
    Read `stop_reason` from the `message_delta` event when streaming.
  </Card>

  <Card title="Errors" icon="info" href="https://platform.claude.com/docs/en/api/errors">
    Handle 4xx and 5xx HTTP errors, which are distinct from stop reasons.
  </Card>
</CardGroup>


---
title: Using the Messages API
url: https://platform.claude.com/docs/en/build-with-claude/working-with-messages
description: Practical patterns and examples for using the Messages API effectively
---

Anthropic offers two ways to build with Claude, each suited to different use cases:

|                | Messages API                                | Claude Managed Agents                                                     |
| -------------- | ------------------------------------------- | ------------------------------------------------------------------------- |
| **What it is** | Direct model prompting access               | Pre-built, configurable agent harness that runs in managed infrastructure |
| **Best for**   | Custom agent loops and fine-grained control | Long-running tasks and asynchronous work                                  |

This guide covers common patterns for working with the Messages API, including basic requests, multi-turn conversations, prefill techniques, and vision capabilities. For complete API specifications, see the [Messages API reference](https://platform.claude.com/docs/en/api/messages/create). For the managed agent harness instead, see the [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview).

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>
