# platform.claude.com Documentation (Part 17 of 35)

## Resume a session at its budget

Source: https://platform.claude.com/llms-full.txt#resume-a-session-at-its-budget

Change or remove the budget with a session update. An accepted update resumes the session's paused work automatically; no further client action is needed.

### Change the budget

Update the session with a new `max_list_cost`. The new value can be higher or lower than the current cap, but it must be strictly greater than the session's consumed list cost; otherwise the update is rejected with a 400 error: `budget.max_list_cost must be greater than the session's consumed list cost`. Because the consumed cost usually sits [a fraction past the old cap](https://platform.claude.com/docs/en/managed-agents/budgets#when-a-session-reaches-its-budget) when the session pauses, base the new value on the session's reported `usage.list_cost`, not on the old `max_list_cost`. Set it a cent or more above that figure: the reported value is rounded and can sit a fraction below the exact consumed cost the check uses.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl -sS --fail-with-body "https://api.anthropic.com/v1/sessions/$SESSION_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d '{
      "budget": {
        "type": "limit",
        "max_list_cost": {"amount": "500", "currency": "USD"}
      }
    }'

bash CLI
  ant beta:sessions update \
    --session-id "$SESSION_ID" \
    --budget '{type: limit, max_list_cost: {amount: "500", currency: USD}}'

python Python
  updated_session = client.beta.sessions.update(
      session.id,
      budget={
          "type": "limit",
          "max_list_cost": {"amount": "500", "currency": "USD"},
      },
  )
  print(updated_session.budget.max_list_cost.amount)  # 500

typescript TypeScript
  const updatedSession = await client.beta.sessions.update(session.id, {
    budget: {
      type: "limit",
      max_list_cost: { amount: "500", currency: "USD" }
    }
  });
  console.log(updatedSession.budget?.max_list_cost.amount); // 500

csharp C#
  var updatedSession = await client.Beta.Sessions.Update(session.ID, new()
  {
      Budget = new()
      {
          Type = BetaManagedAgentsBudgetLimitType.Limit,
          MaxListCost = new() { Amount = "500", Currency = BetaCurrency.Usd },
      },
  });
  Console.WriteLine(updatedSession.Budget?.MaxListCost.Amount);  // 500

go Go
  updatedSession, err := client.Beta.Sessions.Update(ctx, session.ID, anthropic.BetaSessionUpdateParams{
  	Budget: anthropic.BetaManagedAgentsBudgetLimitParam{
  		Type: anthropic.BetaManagedAgentsBudgetLimitTypeLimit,
  		MaxListCost: anthropic.BetaMonetaryAmountParam{
  			Amount:   "500",
  			Currency: anthropic.BetaCurrencyUsd,
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }
  fmt.Println(updatedSession.Budget.MaxListCost.Amount) // 500

java Java
  var updatedSession = client.beta().sessions().update(session.id(), SessionUpdateParams.builder()
      .budget(BetaManagedAgentsBudgetLimit.builder()
          .type(BetaManagedAgentsBudgetLimit.Type.LIMIT)
          .maxListCost(BetaMonetaryAmount.builder()
              .amount("500")
              .currency(BetaCurrency.USD)
              .build())
          .build())
      .build());
  IO.println(updatedSession.budget().orElseThrow().maxListCost().amount());  // 500

php PHP
  $updatedSession = $client->beta->sessions->update(
      $session->id,
      budget: [
          'type' => 'limit',
          'max_list_cost' => ['amount' => '500', 'currency' => 'USD'],
      ],
  );
  echo "{$updatedSession->budget->maxListCost->amount}\n"; // 500

ruby Ruby
  updated_session = client.beta.sessions.update(
    session.id,
    budget: {
      type: "limit",
      max_list_cost: {amount: "500", currency: "USD"}
    }
  )
  puts updated_session.budget.max_list_cost.amount # 500

bash cURL
  curl -sS --fail-with-body "https://api.anthropic.com/v1/sessions/$SESSION_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d '{"budget": null}'

bash CLI
  ant beta:sessions update --session-id "$SESSION_ID" --budget null

python Python
  unbudgeted_session = client.beta.sessions.update(session.id, budget=None)
  print(unbudgeted_session.budget)  # None

typescript TypeScript
  const unbudgetedSession = await client.beta.sessions.update(session.id, { budget: null });
  console.log(unbudgetedSession.budget); // null

csharp C#
  // Assigning null sends an explicit null; leaving Budget unset would omit the field.
  var unbudgetedSession = await client.Beta.Sessions.Update(session.ID, new() { Budget = null });
  Console.WriteLine(unbudgetedSession.Budget is null);  // True: the session no longer has a budget

go Go
  // A zero-value Budget is omitted from the request; param.NullStruct (from
  // github.com/anthropics/anthropic-sdk-go/packages/param) sends an explicit null.
  unbudgetedSession, err := client.Beta.Sessions.Update(ctx, session.ID, anthropic.BetaSessionUpdateParams{
  	Budget: param.NullStruct[anthropic.BetaManagedAgentsBudgetLimitParam](),
  })
  if err != nil {
  	panic(err)
  }
  fmt.Println(unbudgetedSession.JSON.Budget.Valid()) // false: the session no longer has a budget

java Java
  // An empty Optional sends an explicit null; leaving budget unset would omit the field.
  var unbudgetedSession = client.beta().sessions().update(session.id(), SessionUpdateParams.builder()
      .budget(Optional.empty())
      .build());
  IO.println(unbudgetedSession.budget().isPresent());  // false: the session no longer has a budget

php PHP
  // update(budget: null) omits the field, so send the explicit null through the raw client.
  $unbudgetedSession = $client->beta->sessions->raw
      ->update($session->id, ['budget' => null])
      ->parse();
  echo json_encode($unbudgetedSession->budget), "\n"; // null

ruby Ruby
  unbudgeted_session = client.beta.sessions.update(session.id, budget: nil)
  p unbudgeted_session.budget # nil
  ```
</CodeGroup>

<Warning>
  Removing a session's budget is one-way: a session whose budget has been removed cannot be given a new one. To keep a cap on the session, change the budget instead.
</Warning>


## Monitor spend

Source: https://platform.claude.com/llms-full.txt#monitor-spend

The session object carries its `budget` and a `usage` object with the tracked spend: `usage.list_cost` is the session's consumed list cost, and `usage.active_seconds` is the running time its runtime cost is priced on. On a session paused at `budget_reached`, expect `usage.list_cost` to read at or a fraction past `max_list_cost`: the [request that crossed the cap](https://platform.claude.com/docs/en/managed-agents/budgets#when-a-session-reaches-its-budget) finished before the pause. Session-level `active_seconds` counts overlapping activity from concurrent threads once. Thread retrieval responses carry the same two fields on the thread's own `usage`, priced per thread. Per-thread figures are rounded independently and exclude the session's running-time cost, so they don't sum exactly to the session's `list_cost`; the session figure is the one the budget is enforced against.

The `session.usage` event is a snapshot of the session's cumulative usage and tracked list cost. It carries the session's token totals, `list_cost`, `active_seconds`, `server_tool_use` request counts (`web_search_requests`, priced into list cost per request, and `web_fetch_requests`, which reads `0` because web fetch requests carry no per-request charge and aren't metered), and an echo of the session's `budget`, or `null` when the session has none. It appears in the events list and the session stream. The session emits one immediately before it goes idle, whatever the stop reason, so a session that reaches its budget always emits one immediately before the budget-reached idle event.

To read usage from the stream and the session object, see [Tracking usage](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#tracking-usage).


## Budgets in multiagent sessions

Source: https://platform.claude.com/llms-full.txt#budgets-in-multiagent-sessions

A [multiagent](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration) session has a single budget shared across all of its threads; there are no per-thread caps. Each thread's consumption is priced at its own served model, and threads pause independently as the shared cap is reached. [Advisor](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration#give-the-session-an-advisor) consultations count against the same budget, priced at the advisor model's rates. One thread can pause at `budget_reached` while another finishes its in-flight request.

A pending ask outranks the cap: a session with one thread waiting on `requires_action` and another paused at `budget_reached` reports `requires_action` at the session level. The pending request still needs an answer, and answering it is a [settle event](https://platform.claude.com/docs/en/managed-agents/budgets#events-accepted-at-the-cap) the budget doesn't block.


## Budgets on deployments

Source: https://platform.claude.com/llms-full.txt#budgets-on-deployments

A [deployment](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments) accepts the same `budget` object when you create or update it:

The cap is copied onto each session the deployment starts, so it bounds each run separately rather than the deployment's cumulative spend. Changing the deployment's budget applies to sessions the deployment starts afterward, not to sessions already running. Unlike a session, a deployment's budget can be cleared with `null` and set again later. See [Set a budget on each run](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments#set-a-budget-on-each-run).


## Models without a list price

Source: https://platform.claude.com/llms-full.txt#models-without-a-list-price

A budget can only track consumption the platform can price. Creating a budgeted session whose agent, or any agent or advisor on its [multiagent roster](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration), uses a model with no public list price is rejected with a 400 error stating that no list price is available for the model.

If a budgeted session's usage comes to include a model with no list price, the budget can no longer measure the session's spend: the session can pause with a `stop_reason` of `budget_reached`, and changing the budget is rejected. Remove the budget to resume the session.


## Error reference

Source: https://platform.claude.com/llms-full.txt#error-reference

Budget-related requests are rejected in the following cases:

| Condition                                                                                                                                                                                                                                   | Status |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| A work-starting event (for example, `user.message`) is sent while the session is at or over its budget; the error names the [accepted settle events](https://platform.claude.com/docs/en/managed-agents/budgets#events-accepted-at-the-cap) | 400    |
| The budget is set to a value at or below the session's consumed list cost                                                                                                                                                                   | 400    |
| A budget is added to a session created without one, or re-added after removal                                                                                                                                                               | 400    |
| `amount` is not a whole number of cents (for example, `"25.00"`), is zero or negative, or `currency` is not `USD`                                                                                                                           | 400    |
| A budgeted create references a model with [no public list price](https://platform.claude.com/docs/en/managed-agents/budgets#models-without-a-list-price)                                                                                    | 400    |

<Note>
  Session budgets are hard caps in US dollars (written in cents) on a single session, enforced by the platform. They are distinct from the Messages API's [task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets), which are advisory, token-denominated budgets the model uses to self-regulate within one agentic loop.
</Note>


---
title: Session event stream
url: https://platform.claude.com/docs/en/managed-agents/events-and-streaming
description: Send events, stream responses, and interrupt or redirect your session mid-execution.
---

Communication with Claude Managed Agents is event-based. You send user events to the agent, and receive agent and session events back to track status.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Event types

Source: https://platform.claude.com/llms-full.txt#event-types-2

Events flow in two directions.

* **User events** and **system events** are what you send to the agent: `user.*` events start a session and steer it as it progresses; `system.message` appends system-level context that applies to the accompanying turn and all subsequent turns.
* **Session events**, **span events**, and **agent events** are sent to you for observability into your session state and agent progress. Stream connections that opt in also receive [event deltas](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#event-deltas).

Session, span, agent, user, and system event type strings follow a `{domain}.{action}` naming convention. The stream-only delta preview events (`event_start`, `event_delta`) are the exception. See [Event types](https://platform.claude.com/docs/en/managed-agents/reference#event-types) in the reference for the full catalog. [Webhook event types](https://platform.claude.com/docs/en/managed-agents/webhooks#supported-event-types) are separate, and some of their names differ from the stream's (for example, `session.status_idled` rather than `session.status_idle`).

Every persisted event includes a `processed_at` timestamp set when the event finishes processing. On events you send, `processed_at` is null while the event is still queued behind earlier events. The exceptions are `user.define_outcome`, `user.custom_tool_result`, and `user.tool_result`, which are processed on receipt and echoed back with `processed_at` already populated.


## Integrating events

Source: https://platform.claude.com/llms-full.txt#integrating-events

<Tabs>
  <Tab title="Sending events">
    Send a `user.message` event to start or continue the agent's work:

    <CodeGroup>
      ```bash cURL
      curl --fail-with-body -sS "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        -H "content-type: application/json" \
        -d @- <<'EOF'
      {
        "events": [
          {
            "type": "user.message",
            "content": [
              {"type": "text", "text": "Analyze the performance of the sort function in utils.py"}
            ]
          }
        ]
      }
      EOF

bash CLI
      ant beta:sessions:events send --session-id "$SESSION_ID" <<'YAML'
      events:
        - type: user.message
          content:
            - type: text
              text: Analyze the performance of the sort function in utils.py
      YAML

python Python
      client.beta.sessions.events.send(
          session.id,
          events=[
              {
                  "type": "user.message",
                  "content": [
                      {
                          "type": "text",
                          "text": "Analyze the performance of the sort function in utils.py",
                      },
                  ],
              },
          ],
      )

typescript TypeScript
      await client.beta.sessions.events.send(session.id, {
        events: [
          {
            type: "user.message",
            content: [
              {
                type: "text",
                text: "Analyze the performance of the sort function in utils.py",
              },
            ],
          },
        ],
      });

csharp C#
      await client.Beta.Sessions.Events.Send(session.ID, new()
      {
          Events =
          [
              new BetaManagedAgentsUserMessageEventParams
              {
                  Type = BetaManagedAgentsUserMessageEventParamsType.UserMessage,
                  Content =
                  [
                      new BetaManagedAgentsTextBlock
                      {
                          Type = BetaManagedAgentsTextBlockType.Text,
                          Text = "Analyze the performance of the sort function in utils.py",
                      },
                  ],
              },
          ],
      });

go Go
      if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
      	Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
      		OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
      			Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
      			Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{{
      				OfText: &anthropic.BetaManagedAgentsTextBlockParam{
      					Type: anthropic.BetaManagedAgentsTextBlockTypeText,
      					Text: "Analyze the performance of the sort function in utils.py",
      				},
      			}},
      		},
      	}},
      }); err != nil {
      	panic(err)
      }

java Java
      client.beta().sessions().events().send(
          session.id(),
          EventSendParams.builder()
              .addEvent(BetaManagedAgentsUserMessageEventParams.builder()
                  .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
                  .addTextContent("Analyze the performance of the sort function in utils.py")
                  .build())
              .build());

php PHP
      $client->beta->sessions->events->send(
          $session->id,
          events: [
              [
                  'type' => 'user.message',
                  'content' => [
                      [
                          'type' => 'text',
                          'text' => 'Analyze the performance of the sort function in utils.py',
                      ],
                  ],
              ],
          ],
      );

ruby Ruby
      client.beta.sessions.events.send_(
        session.id,
        events: [
          {
            type: "user.message",
            content: [
              {
                type: "text",
                text: "Analyze the performance of the sort function in utils.py"
              }
            ]
          }
        ]
      )

bash cURL
      # Agent is currently analyzing a file...
      # Interrupt with a new direction:
      curl --fail-with-body -sS "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        -H "content-type: application/json" \
        -d @- <<'EOF'
      {
        "events": [
          {"type": "user.interrupt"},
          {
            "type": "user.message",
            "content": [
              {"type": "text", "text": "Instead, focus on fixing the bug in line 42."}
            ]
          }
        ]
      }
      EOF

bash CLI
      # Agent is currently analyzing a file...
      # Interrupt with a new direction:
      ant beta:sessions:events send --session-id "$SESSION_ID" <<'YAML'
      events:
        - type: user.interrupt
        - type: user.message
          content:
            - type: text
              text: Instead, focus on fixing the bug in line 42.
      YAML

python Python
      # Agent is currently analyzing a file...
      # Interrupt with a new direction:
      client.beta.sessions.events.send(
          session.id,
          events=[
              {"type": "user.interrupt"},
              {
                  "type": "user.message",
                  "content": [
                      {
                          "type": "text",
                          "text": "Instead, focus on fixing the bug in line 42.",
                      },
                  ],
              },
          ],
      )

typescript TypeScript
      // Agent is currently analyzing a file...
      // Interrupt with a new direction:
      await client.beta.sessions.events.send(session.id, {
        events: [
          { type: "user.interrupt" },
          {
            type: "user.message",
            content: [
              {
                type: "text",
                text: "Instead, focus on fixing the bug in line 42.",
              },
            ],
          },
        ],
      });

csharp C#
      // Agent is currently analyzing a file...
      // Interrupt with a new direction:
      await client.Beta.Sessions.Events.Send(session.ID, new()
      {
          Events =
          [
              new BetaManagedAgentsUserInterruptEventParams
              {
                  Type = BetaManagedAgentsUserInterruptEventParamsType.UserInterrupt,
              },
              new BetaManagedAgentsUserMessageEventParams
              {
                  Type = BetaManagedAgentsUserMessageEventParamsType.UserMessage,
                  Content =
                  [
                      new BetaManagedAgentsTextBlock
                      {
                          Type = BetaManagedAgentsTextBlockType.Text,
                          Text = "Instead, focus on fixing the bug in line 42.",
                      },
                  ],
              },
          ],
      });

go Go
      // Agent is currently analyzing a file...
      // Interrupt with a new direction:
      if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
      	Events: []anthropic.BetaManagedAgentsEventParamsUnion{
      		{
      			OfUserInterrupt: &anthropic.BetaManagedAgentsUserInterruptEventParams{
      				Type: anthropic.BetaManagedAgentsUserInterruptEventParamsTypeUserInterrupt,
      			},
      		},
      		{
      			OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
      				Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
      				Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{{
      					OfText: &anthropic.BetaManagedAgentsTextBlockParam{
      						Type: anthropic.BetaManagedAgentsTextBlockTypeText,
      						Text: "Instead, focus on fixing the bug in line 42.",
      					},
      				}},
      			},
      		},
      	},
      }); err != nil {
      	panic(err)
      }

java Java
      // Agent is currently analyzing a file...
      // Interrupt with a new direction:
      client.beta().sessions().events().send(
          session.id(),
          EventSendParams.builder()
              .addEvent(BetaManagedAgentsUserInterruptEventParams.builder()
                  .type(BetaManagedAgentsUserInterruptEventParams.Type.USER_INTERRUPT)
                  .build())
              .addEvent(BetaManagedAgentsUserMessageEventParams.builder()
                  .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
                  .addTextContent("Instead, focus on fixing the bug in line 42.")
                  .build())
              .build());

php PHP
      // Agent is currently analyzing a file...
      // Interrupt with a new direction:
      $client->beta->sessions->events->send(
          $session->id,
          events: [
              ['type' => 'user.interrupt'],
              [
                  'type' => 'user.message',
                  'content' => [
                      [
                          'type' => 'text',
                          'text' => 'Instead, focus on fixing the bug in line 42.',
                      ],
                  ],
              ],
          ],
      );

ruby Ruby
      # Agent is currently analyzing a file...
      # Interrupt with a new direction:
      client.beta.sessions.events.send_(
        session.id,
        events: [
          {type: "user.interrupt"},
          {
            type: "user.message",
            content: [
              {type: "text", text: "Instead, focus on fixing the bug in line 42."}
            ]
          }
        ]
      )

bash cURL
      # Open the stream first, then send the user message
      exec {stream}< <(
        curl --fail-with-body -sS -N \
          "https://api.anthropic.com/v1/sessions/$SESSION_ID/events/stream?beta=true" \
          -H "x-api-key: $ANTHROPIC_API_KEY" \
          -H "anthropic-version: 2023-06-01" \
          -H "anthropic-beta: managed-agents-2026-04-01" \
          -H "content-type: application/json" \
          -H "accept: text/event-stream"
      )

      curl --fail-with-body -sS \
        "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        -H "content-type: application/json" \
        -d @- >/dev/null <<'EOF'
      {
        "events": [
          {
            "type": "user.message",
            "content": [{"type": "text", "text": "Summarize the repo README"}]
          }
        ]
      }
      EOF

      while IFS= read -r -u "$stream" event_line; do
        [[ $event_line == data:* ]] || continue
        event_json=${event_line#data: }
        case $(jq -r '.type' <<<"$event_json") in
          agent.message)
            jq -j '.content[] | select(.type == "text") | .text' <<<"$event_json"
            ;;
          session.status_idle)
            break
            ;;
          session.error)
            printf '\n[Error: %s]\n' "$(jq -r '.error.message // "unknown"' <<<"$event_json")"
            break
            ;;
        esac
      done
      exec {stream}<&-

bash CLI
      # This workflow does not translate well to a one-off shell command.
      # Use one of the SDK examples in this code group instead.

python Python
      # Open the stream first, then send the user message
      with client.beta.sessions.events.stream(session.id) as stream:
          client.beta.sessions.events.send(
              session.id,
              events=[
                  {
                      "type": "user.message",
                      "content": [{"type": "text", "text": "Summarize the repo README"}],
                  },
              ],
          )

          for event in stream:
              match event.type:
                  case "agent.message":
                      for block in event.content:
                          if block.type == "text":
                              print(block.text, end="")
                  case "session.status_idle":
                      break
                  case "session.error":
                      error_message = event.error.message if event.error else "unknown"
                      print(f"\n[Error: {error_message}]")
                      break

typescript TypeScript
      // Open the stream first, then send the user message
      const stream = await client.beta.sessions.events.stream(session.id);
      await client.beta.sessions.events.send(session.id, {
        events: [
          {
            type: "user.message",
            content: [{ type: "text", text: "Summarize the repo README" }]
          }
        ]
      });

      for await (const event of stream) {
        if (event.type === "agent.message") {
          for (const block of event.content) {
            if (block.type === "text") {
              process.stdout.write(block.text);
            }
          }
        } else if (event.type === "session.status_idle") {
          break;
        } else if (event.type === "session.error") {
          console.log(`\n[Error: ${event.error?.message ?? "unknown"}]`);
          break;
        }
      }

csharp C#
      // Open the stream first, then send the user message
      using var stream = await client.Beta.Sessions.Events.WithRawResponse.StreamStreaming(session.ID);
      await client.Beta.Sessions.Events.Send(session.ID, new()
      {
          Events =
          [
              new BetaManagedAgentsUserMessageEventParams
              {
                  Type = BetaManagedAgentsUserMessageEventParamsType.UserMessage,
                  Content =
                  [
                      new BetaManagedAgentsTextBlock
                      {
                          Type = BetaManagedAgentsTextBlockType.Text,
                          Text = "Summarize the repo README",
                      },
                  ],
              },
          ],
      });

      await foreach (var streamEvent in stream.Enumerate())
      {
          if (streamEvent.Value is BetaManagedAgentsAgentMessageEvent message)
          {
              foreach (var block in message.Content)
              {
                  Console.Write(block.Text);
              }
          }
          else if (streamEvent.Value is BetaManagedAgentsSessionStatusIdleEvent)
          {
              break;
          }
          else if (streamEvent.Value is BetaManagedAgentsSessionErrorEvent error)
          {
              Console.WriteLine($"\n[Error: {error.Error?.Message ?? "unknown"}]");
              break;
          }
      }

go Go
      	// Open the stream first, then send the user message
      	stream := client.Beta.Sessions.Events.StreamEvents(ctx, session.ID, anthropic.BetaSessionEventStreamParams{})
      	defer stream.Close()

      	if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
      		Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
      			OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
      				Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
      				Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{{
      					OfText: &anthropic.BetaManagedAgentsTextBlockParam{
      						Type: anthropic.BetaManagedAgentsTextBlockTypeText,
      						Text: "Summarize the repo README",
      					},
      				}},
      			},
      		}},
      	}); err != nil {
      		panic(err)
      	}

      events:
      	for stream.Next() {
      		switch event := stream.Current().AsAny().(type) {
      		case anthropic.BetaManagedAgentsAgentMessageEvent:
      			// concrete-typed list: BetaManagedAgentsTextBlock
      			for _, block := range event.Content {
      				fmt.Print(block.Text)
      			}
      		case anthropic.BetaManagedAgentsSessionStatusIdleEvent:
      			break events
      		case anthropic.BetaManagedAgentsSessionErrorEvent:
      			fmt.Printf("\n[Error: %s]\n", cmp.Or(event.Error.Message, "unknown"))
      			break events
      		}
      	}
      	if err := stream.Err(); err != nil {
      		panic(err)
      	}

java Java
      // Open the stream first, then send the user message
      try (var stream = client.beta().sessions().events().streamStreaming(session.id())) {
          client.beta().sessions().events().send(
              session.id(),
              EventSendParams.builder()
                  .addEvent(BetaManagedAgentsUserMessageEventParams.builder()
                      .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
                      .addTextContent("Summarize the repo README")
                      .build())
                  .build()
          );

          Iterable<BetaManagedAgentsStreamSessionEvents> events = stream.stream()::iterator;
          for (var event : events) {
              if (event.isAgentMessage()) {
                  event.asAgentMessage().content().forEach(block -> block.text().ifPresent(textBlock -> IO.print(textBlock.text())));
              } else if (event.isSessionStatusIdle()) {
                  break;
              } else if (event.isSessionError()) {
                  // The `message` field spans all error variants; read it from the raw JSON.
                  var errorMessage =
                      event.asSessionError().error()._json().orElse(null) instanceof JsonObject json
                          ? json.values().get("message").asStringOrThrow()
                          : "unknown";
                  IO.println("\n[Error: " + errorMessage + "]");
                  break;
              }
          }
      }

php PHP
      // Open the stream first, then send the user message
      $stream = $client->beta->sessions->events->streamStream($session->id);
      $client->beta->sessions->events->send(
          $session->id,
          events: [
              [
                  'type' => 'user.message',
                  'content' => [['type' => 'text', 'text' => 'Summarize the repo README']],
              ],
          ],
      );

      foreach ($stream as $event) {
          match ($event->type) {
              'agent.message' => array_walk(
                  $event->content,
                  static fn ($block) => $block->type === 'text' ? print($block->text) : null,
              ),
              'session.error' => printf("\n[Error: %s]", $event->error?->message ?? 'unknown'),
              default => null,
          };
          if ($event->type === 'session.status_idle' || $event->type === 'session.error') {
              break;
          }
      }
      $stream->close();

ruby Ruby
      # Open the stream first, then send the user message
      stream = client.beta.sessions.events.stream_events(session.id)

      client.beta.sessions.events.send_(
        session.id,
        events: [{
          type: "user.message",
          content: [{type: "text", text: "Summarize the repo README"}]
        }]
      )

      stream.each do |event|
        case event.type
        in :"agent.message"
          event.content.each { print it.text }
        in :"session.status_idle"
          break
        in :"session.error"
          puts "\n[Error: #{event.error&.message || "unknown"}]"
          break
        else
          # ignore other event types
        end
      end

bash cURL
      exec {stream}< <(
        curl --fail-with-body -sS -N \
          "https://api.anthropic.com/v1/sessions/$SESSION_ID/events/stream?beta=true" \
          -H "x-api-key: $ANTHROPIC_API_KEY" \
          -H "anthropic-version: 2023-06-01" \
          -H "anthropic-beta: managed-agents-2026-04-01" \
          -H "content-type: application/json" \
          -H "accept: text/event-stream"
      )

      # Stream is open and buffering. List history before tailing live.
      declare -A seen_event_ids
      while IFS= read -r event_id; do
        seen_event_ids[$event_id]=1
      done < <(
        curl --fail-with-body -sS \
          "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
          -H "x-api-key: $ANTHROPIC_API_KEY" \
          -H "anthropic-version: 2023-06-01" \
          -H "anthropic-beta: managed-agents-2026-04-01" \
          -H "content-type: application/json" | jq -r '.data[].id'
      )

      # Tail live events, skipping anything already seen
      while IFS= read -r -u "$stream" event_line; do
        [[ $event_line == data:* ]] || continue
        event_json=${event_line#data: }
        event_id=$(jq -r '.id' <<<"$event_json")
        [[ -n ${seen_event_ids[$event_id]+seen} ]] && continue
        seen_event_ids[$event_id]=1
        case $(jq -r '.type' <<<"$event_json") in
          agent.message)
            jq -j '.content[] | select(.type == "text") | .text' <<<"$event_json"
            ;;
          session.status_idle)
            break
            ;;
        esac
      done
      exec {stream}<&-

bash CLI
      # This workflow does not translate well to a one-off shell command.
      # Use one of the SDK examples in this code group instead.

python Python
      with client.beta.sessions.events.stream(session.id) as stream:
          # Stream is open and buffering. List history before tailing live.
          history = client.beta.sessions.events.list(session.id)
          seen_event_ids = {past_event.id for past_event in history}

          # Tail live events, skipping anything already seen
          for event in stream:
              if event.type == "event_start" or event.type == "event_delta":
                  # Delta previews aren't enabled on this connection.
                  continue
              if event.id in seen_event_ids:
                  continue
              seen_event_ids.add(event.id)
              match event.type:
                  case "agent.message":
                      for block in event.content:
                          if block.type == "text":
                              print(block.text, end="")
                  case "session.status_idle":
                      break

typescript TypeScript
      const seenEventIds = new Set<string>();
      const stream = await client.beta.sessions.events.stream(session.id);

      // Stream is open and buffering. List history before tailing live.
      for await (const event of client.beta.sessions.events.list(session.id)) {
        seenEventIds.add(event.id);
      }

      // Tail live events, skipping anything already seen
      for await (const event of stream) {
        // Preview events (event_start/event_delta) carry no top-level id
        if (event.type === "event_start" || event.type === "event_delta") continue;
        if (seenEventIds.has(event.id)) continue;
        seenEventIds.add(event.id);
        if (event.type === "agent.message") {
          for (const block of event.content) {
            if (block.type === "text") {
              process.stdout.write(block.text);
            }
          }
        } else if (event.type === "session.status_idle") {
          break;
        }
      }

csharp C#
      using var stream = await client.Beta.Sessions.Events.WithRawResponse.StreamStreaming(session.ID);

      // Stream is open and buffering. List history before tailing live.
      HashSet<string> seenEventIds = [];
      var history = await client.Beta.Sessions.Events.List(session.ID);
      await foreach (var pastEvent in history.Paginate())
      {
          seenEventIds.Add(pastEvent.ID);
      }

      // Tail live events, skipping anything already seen
      await foreach (var streamEvent in stream.Enumerate())
      {
          if (!seenEventIds.Add(streamEvent.ID))
          {
              continue;
          }
          if (streamEvent.Value is BetaManagedAgentsAgentMessageEvent message)
          {
              foreach (var block in message.Content)
              {
                  Console.Write(block.Text);
              }
          }
          else if (streamEvent.Value is BetaManagedAgentsSessionStatusIdleEvent)
          {
              break;
          }
      }

go Go
      	stream := client.Beta.Sessions.Events.StreamEvents(ctx, session.ID, anthropic.BetaSessionEventStreamParams{})
      	defer stream.Close()

      	// Stream is open and buffering. List history before tailing live.
      	seenEventIDs := map[string]struct{}{}
      	history := client.Beta.Sessions.Events.ListAutoPaging(ctx, session.ID, anthropic.BetaSessionEventListParams{})
      	for history.Next() {
      		seenEventIDs[history.Current().ID] = struct{}{}
      	}
      	if err := history.Err(); err != nil {
      		panic(err)
      	}

      	// Tail live events, skipping anything already seen
      tail:
      	for stream.Next() {
      		event := stream.Current()
      		if _, seen := seenEventIDs[event.ID]; seen {
      			continue
      		}
      		seenEventIDs[event.ID] = struct{}{}
      		switch event := event.AsAny().(type) {
      		case anthropic.BetaManagedAgentsAgentMessageEvent:
      			// concrete-typed list: BetaManagedAgentsTextBlock
      			for _, block := range event.Content {
      				fmt.Print(block.Text)
      			}
      		case anthropic.BetaManagedAgentsSessionStatusIdleEvent:
      			break tail
      		}
      	}
      	if err := stream.Err(); err != nil {
      		panic(err)
      	}

java Java
      try (var stream = client.beta().sessions().events().streamStreaming(session.id())) {
          // Stream is open and buffering. List history before tailing live.
          // Every event variant carries `id`; read it from the raw JSON to dedup across variants.
          var seenEventIds = new HashSet<String>();
          for (var pastEvent : client.beta().sessions().events().list(session.id()).autoPager()) {
              if (pastEvent._json().orElseThrow() instanceof JsonObject json) {
                  seenEventIds.add(json.values().get("id").asStringOrThrow());
              }
          }

          // Tail live events; Set.add returns false for already-seen IDs, skipping the replay.
          stream.stream()
              .filter(event -> event._json().orElseThrow() instanceof JsonObject json
                  && seenEventIds.add(json.values().get("id").asStringOrThrow()))
              .takeWhile(event -> !event.isSessionStatusIdle())
              .filter(BetaManagedAgentsStreamSessionEvents::isAgentMessage)
              .forEach(event -> event.asAgentMessage().content()
                  .forEach(block -> block.text().ifPresent(textBlock -> IO.print(textBlock.text()))));
      }

php PHP
      $stream = $client->beta->sessions->events->streamStream($session->id);

      // Stream is open and buffering. List history before tailing live.
      $seenEventIds = [];
      foreach ($client->beta->sessions->events->list($session->id)->pagingEachItem() as $event) {
          $seenEventIds[$event->id] = true;
      }

      // Tail live events, skipping anything already seen
      foreach ($stream as $event) {
          if (isset($seenEventIds[$event->id])) {
              continue;
          }
          $seenEventIds[$event->id] = true;
          match ($event->type) {
              'agent.message' => array_walk(
                  $event->content,
                  static fn ($block) => $block->type === 'text' ? print($block->text) : null,
              ),
              default => null,
          };
          if ($event->type === 'session.status_idle') {
              break;
          }
      }
      $stream->close();

ruby Ruby
      stream = client.beta.sessions.events.stream_events(session.id)

      # Stream is open and buffering. List history before tailing live.
      seen_event_ids = Set.new
      client.beta.sessions.events.list(session.id).auto_paging_each { seen_event_ids << it.id }

      # Tail live events, skipping anything already seen — Set#add? returns nil for duplicates
      stream.each do |event|
        next unless seen_event_ids.add?(event.id)
        case event.type
        in :"agent.message"
          event.content.each { print it.text }
        in :"session.status_idle"
          break
        else
          # ignore other event types
        end
      end

bash cURL
      curl --fail-with-body -sS "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        -H "content-type: application/json" \
        | jq -r '.data[] | "[\(.type)] \(.processed_at)"'

bash CLI
      ant beta:sessions:events list --session-id "$SESSION_ID" \
        --format jsonl --transform '{type,processed_at}'

python Python
      events = client.beta.sessions.events.list(session.id)
      for event in events.data:
          print(f"[{event.type}] {event.processed_at}")

typescript TypeScript
      const events = await client.beta.sessions.events.list(session.id);
      for (const event of events.data) {
        console.log(`[${event.type}] ${event.processed_at}`);
      }

csharp C#
      var events = await client.Beta.Sessions.Events.List(session.ID);
      foreach (var sessionEvent in events.Items)
      {
          Console.WriteLine($"[{sessionEvent.Json.GetProperty("type").GetString()}] {sessionEvent.ProcessedAt}");
      }

go Go
      events, err := client.Beta.Sessions.Events.List(ctx, session.ID, anthropic.BetaSessionEventListParams{})
      if err != nil {
      	panic(err)
      }
      for _, event := range events.Data {
      	fmt.Printf("[%s] %s\n", event.Type, event.ProcessedAt)
      }

java Java
      var events = client.beta().sessions().events().list(session.id());
      for (var event : events.data()) {
          var eventJson = event._json().orElseThrow().convert(JsonNode.class);
          var processedAt = eventJson.path("processed_at");
          IO.println("[" + eventJson.get("type").asText() + "] "
              + (processedAt.isTextual() ? processedAt.asText() : "null"));
      }

php PHP
      $events = $client->beta->sessions->events->list($session->id);
      foreach ($events->data as $event) {
          $processedAt = ($event->processedAt ?? null)?->format(DATE_RFC3339) ?? 'null';
          echo "[{$event->type}] {$processedAt}\n";
      }

ruby Ruby
      events = client.beta.sessions.events.list(session.id)
      events.data.each { puts "[#{it.type}] #{it.processed_at}" }

bash cURL
      curl --fail-with-body -sS "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true&types[]=agent.tool_use&types[]=agent.tool_result" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        | jq -r '.data[] | "[\(.type)] \(.processed_at)"'

bash CLI
      ant beta:sessions:events list --session-id "$SESSION_ID" \
        --type agent.tool_use --type agent.tool_result \
        --format jsonl --transform '{type,processed_at}'

python Python
      events = client.beta.sessions.events.list(
          session.id,
          types=["agent.tool_use", "agent.tool_result"],
      )
      for event in events.data:
          print(f"[{event.type}] {event.processed_at}")

typescript TypeScript
      const events = await client.beta.sessions.events.list(session.id, {
        types: ["agent.tool_use", "agent.tool_result"],
      });
      for (const event of events.data) {
        console.log(`[${event.type}] ${event.processed_at}`);
      }

csharp C#
      var events = await client.Beta.Sessions.Events.List(session.ID, new()
      {
          Types = ["agent.tool_use", "agent.tool_result"],
      });
      foreach (var sessionEvent in events.Items)
      {
          Console.WriteLine($"[{sessionEvent.Json.GetProperty("type").GetString()}] {sessionEvent.ProcessedAt}");
      }

go Go
      events, err := client.Beta.Sessions.Events.List(ctx, session.ID, anthropic.BetaSessionEventListParams{
      	Types: []string{"agent.tool_use", "agent.tool_result"},
      })
      if err != nil {
      	panic(err)
      }
      for _, event := range events.Data {
      	fmt.Printf("[%s] %s\n", event.Type, event.ProcessedAt)
      }

java Java
      var events = client.beta().sessions().events().list(
          session.id(),
          EventListParams.builder()
              .addType("agent.tool_use")
              .addType("agent.tool_result")
              .build());
      for (var event : events.data()) {
          event.agentToolUse().ifPresent(toolUse ->
              IO.println("[" + toolUse.type() + "] " + toolUse.processedAt()));
          event.agentToolResult().ifPresent(toolResult ->
              IO.println("[" + toolResult.type() + "] " + toolResult.processedAt()));
      }

php PHP
      // In PHP, pass the types you want on EventListParams; see the Anthropic PHP SDK.

ruby Ruby
      events = client.beta.sessions.events.list(
        session.id,
        types: ["agent.tool_use", "agent.tool_result"]
      )
      events.data.each { puts "[#{it.type}] #{it.processed_at}" }
      ```
    </CodeGroup>
  </Tab>
</Tabs>


## Event deltas

Source: https://platform.claude.com/llms-full.txt#event-deltas

By default, the agent's response text reaches the stream as buffered `agent.message` events, each emitted only after the model request that produced it finishes. Event deltas let you render that text incrementally, as a live preview, while the model is still generating it. A preview is not the response: previews are a best-effort display aid, and the buffered `agent.message` is always the authoritative record. A client that ignores previews still receives a complete, correct stream.

### Opt in to previews

Previews are opt-in per stream connection. Add the `event_deltas[]` query parameter to the stream you're reading, repeating it once for each event type you want previewed. Because `[]` is a shell glob pattern, quote the URL whenever you build the request in a shell; the examples percent-encode the brackets as `%5B%5D`, which also works. Both stream endpoints accept the parameter: the session-level stream at `GET /v1/sessions/{session_id}/events/stream`, and each [session thread](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration)'s own stream at `GET /v1/sessions/{session_id}/threads/{thread_id}/stream`. The accepted values are `agent.message` and `agent.thinking`; any other value returns a 400 error, as does a request with more than 100 values. A subagent's previews appear on [that subagent's own thread stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#preview-session-thread-events).

When a previewed event begins, the stream emits an `event_start` carrying the upcoming event's type and `id`:

For `agent.message`, the start is followed by `event_delta` events carrying incremental text. Each delta names the event it extends in `event_id` and the content block it extends in `delta.index`:

When an `agent.thinking` event is previewed, only the `event_start` is emitted. No `event_delta` events follow, and the buffered `agent.thinking` event that concludes the preview carries no thinking content; it is a progress signal, not a content carrier.

Unlike persisted events, `event_start` and `event_delta` have no `id` or `processed_at` of their own. The only identifier they carry is the `id` of the event they preview.

<Note>
  Event deltas use a different wire format from [Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming), and the difference is intentional. A previewed `agent.message` gets a single `event_start` followed only by `event_delta` events. There are no per-content-block start or stop events and no stop event for the previewed event itself. The delta type is `content_delta`, not `content_block_delta`. Accumulator code written for the Messages API does not carry over unchanged.
</Note>

### Accumulate and reconcile

Every SDK that supports event deltas includes an accumulator helper that handles the `index` bookkeeping for you. The Go, Java, Ruby, and C# helpers also key the accumulating preview by the event's `id`; with the Python, TypeScript, and PHP helpers you keep that map yourself and fold each delta into the entry for its `id`. The manual pattern also works in every language when you need custom bookkeeping: apply it to the generated event types.

In the manual pattern, treat the preview as a scratch buffer and the buffered event as the record. Key the buffer by `(event_id, index)`. Reconcile per model request: a turn opens with a single `session.status_running` event, then on a turn that completes normally each model request produces, in order, `span.model_request_start`, `event_start`, the `event_delta` events, the buffered `agent.message`, and finally [`span.model_request_end`](https://platform.claude.com/docs/en/managed-agents/reference#event-types) (in the Span events tab). On the wire, this is the previewed portion of that sequence, interleaved with the connection's other buffered events:

```text wrap
event_start     {"event": {"type": "agent.message", "id": "sevt_01abc..."}}
event_delta     {"event_id": "sevt_01abc...", "delta": {"type": "content_delta", "index": 0, "content": {"type": "text", "text": "..."}}}
...
agent.message   {"id": "sevt_01abc...", "content": [...]}

bash cURL
  # Opt in to agent.message previews via event_deltas, then accumulate manually.
  exec {stream}< <(
    curl --fail-with-body -sS -N \
      "https://api.anthropic.com/v1/sessions/$SESSION_ID/events/stream?beta=true&event_deltas%5B%5D=agent.message" \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "anthropic-beta: managed-agents-2026-04-01" \
      -H "accept: text/event-stream"
  )

  curl --fail-with-body -sS \
    "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- >/dev/null <<'EOF'
  {
    "events": [
      {
        "type": "user.message",
        "content": [{"type": "text", "text": "In one short sentence, describe what an event delta is."}]
      }
    ]
  }
  EOF

  # Accumulate deltas keyed by (message id, content index); the final
  # agent.message carries the full text, so it replaces every preview for that id.
  declare -A preview
  while IFS= read -r -u "$stream" event_line; do
    [[ $event_line == data:* ]] || continue
    event_json=${event_line#data: }
    case $(jq -r '.type' <<<"$event_json") in
      event_start)
        preview_id=$(jq -r '.event.id' <<<"$event_json")
        printf '[event_start id=%s]\n' "$preview_id"
        ;;
      event_delta)
        preview_key=$(jq -r '.event_id + ":" + (.delta.index | tostring)' <<<"$event_json")
        preview[$preview_key]+=$(jq -r '.delta.content.text' <<<"$event_json")
        printf '[event_delta] %s\n' "${preview[$preview_key]}"
        ;;
      agent.message)
        msg_id=$(jq -r '.id' <<<"$event_json")
        for preview_key in "${!preview[@]}"; do
          [[ $preview_key == "$msg_id":* ]] && unset "preview[$preview_key]"
        done
        printf '[agent.message id=%s] ' "$msg_id"
        jq -j '.content[] | select(.type == "text") | .text' <<<"$event_json"
        printf '\n'
        ;;
      span.model_request_end)
        for preview_key in "${!preview[@]}"; do
          printf '[closing unreconciled preview for %s]\n' "${preview_key%%:*}"
        done
        preview=()
        ;;
      session.status_idle)
        break
        ;;
    esac
  done
  exec {stream}<&-

bash CLI
  # This workflow does not translate well to a one-off shell command.
  # Use one of the SDK examples in this code group instead.

python Python
  # Preview snapshots, keyed by event id. accumulate_managed_agents_event folds each
  # event_start / event_delta into an agent.message snapshot; the buffered
  # agent.message replaces it.
  previews: dict[str, BetaManagedAgentsAgentMessageEvent] = {}

  # Opt in to agent.message previews on this connection
  with client.beta.sessions.events.stream(
      session.id, event_deltas=["agent.message"]
  ) as stream:
      client.beta.sessions.events.send(
          session.id,
          events=[
              {
                  "type": "user.message",
                  "content": [{"type": "text", "text": "Describe the repo in one sentence."}],
              },
          ],
      )

      for event in stream:
          match event.type:
              case "event_start":
                  snapshot = accumulate_managed_agents_event(None, event)
                  if snapshot is not None:
                      previews[event.event.id] = snapshot
                  print(f"event_start             {event.event.type} {event.event.id}")
              case "event_delta":
                  preview = accumulate_managed_agents_event(previews.get(event.event_id), event)
                  if preview is not None:
                      previews[event.event_id] = preview
                      text = "".join(block.text for block in preview.content)
                      print(f"event_delta             preview: {text!r}")
              case "agent.message":
                  # The buffered event is the record: it replaces and closes the preview
                  preview = accumulate_managed_agents_event(previews.pop(event.id, None), event)
                  text = "".join(block.text for block in preview.content)
                  print(f"agent.message           {event.id} {text!r}")
              case "span.model_request_end":
                  # No more deltas are coming. Close any preview whose
                  # buffered event never arrived.
                  for event_id in previews:
                      print(f"span.model_request_end  closing preview for {event_id}")
                  previews.clear()
              case "session.status_idle":
                  break

typescript TypeScript
  // Preview snapshots, keyed by event id. `accumulateManagedAgentsEvent`
  // folds event_start / event_delta previews into an agent.message snapshot.
  const previews = new Map<string, BetaManagedAgentsAgentMessageEvent>();

  // Opt in to agent.message previews for this connection only
  const stream = await client.beta.sessions.events.stream(session.id, {
    event_deltas: ["agent.message"],
  });
  await client.beta.sessions.events.send(session.id, {
    events: [
      {
        type: "user.message",
        content: [{ type: "text", text: "Summarize the repo README" }]
      }
    ]
  });

  for await (const event of stream) {
    if (event.type === "event_start") {
      // 1. Note the announced id and open the snapshot. Deltas and the
      //    buffered event carry the same id.
      const preview = accumulateManagedAgentsEvent(undefined, event);
      if (preview) previews.set(event.event.id, preview);
      console.log(`event_start             ${event.event.type} ${event.event.id}`);
    } else if (event.type === "event_delta") {
      // 2. Fold the fragment into the snapshot and render it
      const preview = accumulateManagedAgentsEvent(previews.get(event.event_id), event);
      if (preview) {
        previews.set(event.event_id, preview);
        const text = preview.content.map((block) => block.text).join("");
        console.log(`event_delta             preview: ${JSON.stringify(text)}`);
      }
    } else if (event.type === "agent.message") {
      // 3. The buffered event is the record: it replaces and closes the preview
      const message = accumulateManagedAgentsEvent(previews.get(event.id), event);
      previews.delete(event.id);
      const text = message.content.map((block) => block.text).join("");
      console.log(`agent.message           ${event.id} ${JSON.stringify(text)}`);
    } else if (event.type === "span.model_request_end") {
      // 4. No more deltas are coming. Close any preview that was never reconciled.
      for (const eventId of previews.keys()) {
        console.log(`span.model_request_end  closing preview for ${eventId}`);
      }
      previews.clear();
    } else if (event.type === "session.status_idle") {
      break;
    }
  }
  stream.controller.abort();

csharp C#
  // Opt in to event deltas: agent.message events are previewed as they are produced.
  using var stream = await client.Beta.Sessions.Events.WithRawResponse.StreamStreaming(
      session.ID,
      new() { EventDeltas = [BetaManagedAgentsDeltaType.AgentMessage] }
  );
  await client.Beta.Sessions.Events.Send(session.ID, new()
  {
      Events =
      [
          new BetaManagedAgentsUserMessageEventParams
          {
              Type = BetaManagedAgentsUserMessageEventParamsType.UserMessage,
              Content =
              [
                  new BetaManagedAgentsTextBlock
                  {
                      Type = BetaManagedAgentsTextBlockType.Text,
                      Text = "Write a haiku about event streams.",
                  },
              ],
          },
      ],
  });

  // Accumulate preview fragments per (event id, content index). The buffered
  // agent.message that follows carries the complete content, so it replaces the
  // accumulated preview rather than appending to it.
  Dictionary<string, SortedDictionary<long, string>> previews = [];

  await foreach (var streamEvent in stream.Enumerate())
  {
      if (streamEvent.TryPickStartEvent(out var start))
      {
          // A preview opened for the event with this id. This stream only opts in
          // to agent.message deltas; TryPick* returns false instead of throwing,
          // so other preview types (including ones added later) are skipped.
          if (start.Event.TryPickAgentMessage(out var preview))
          {
              Console.WriteLine($"event_start             {preview.Type.Raw()} {preview.ID}");
          }
      }
      else if (streamEvent.TryPickDeltaEvent(out var delta))
      {
          // Insert at a new index, append at an existing one
          if (!previews.TryGetValue(delta.EventID, out var fragments))
          {
              previews[delta.EventID] = fragments = [];
          }
          var index = delta.Delta.Index ?? 0;
          fragments[index] = fragments.GetValueOrDefault(index, "") + delta.Delta.Content.Text;
          Console.WriteLine($"event_delta             preview: {fragments[index]}");
      }
      else if (streamEvent.TryPickAgentMessageEvent(out var message))
      {
          // Deltas are best-effort: discard the preview and use the buffered event
          previews.Remove(message.ID);
          Console.WriteLine($"agent.message           {message.ID} {string.Concat(message.Content.Select(block => block.Text))}");
      }
      else if (streamEvent.TryPickSpanModelRequestEndEvent(out _))
      {
          // No more deltas are coming; close any preview that was never reconciled.
          foreach (var eventId in previews.Keys)
          {
              Console.WriteLine($"span.model_request_end  closing preview for {eventId}");
          }
          previews.Clear();
      }
      else if (streamEvent.TryPickSessionStatusIdleEvent(out _))
      {
          break;
      }
  }

go Go
  	// Opt in to incremental previews of agent.message events
  	stream := client.Beta.Sessions.Events.StreamEvents(ctx, session.ID, anthropic.BetaSessionEventStreamParams{
  		EventDeltas: []anthropic.BetaManagedAgentsDeltaType{
  			anthropic.BetaManagedAgentsDeltaTypeAgentMessage,
  		},
  	})

  	if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  		Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  			OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
  				Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
  				Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{{
  					OfText: &anthropic.BetaManagedAgentsTextBlockParam{
  						Type: anthropic.BetaManagedAgentsTextBlockTypeText,
  						Text: "Write a haiku about the ocean.",
  					},
  				}},
  			},
  		}},
  	}); err != nil {
  		panic(err)
  	}

  	// The accumulator folds event_start / event_delta fragments into
  	// per-event-id agent.message snapshots. The zero value is ready to use.
  	var previews anthropic.BetaManagedAgentsEventAccumulator

  deltas:
  	for stream.Next() {
  		event := stream.Current()
  		previews.Accumulate(event)

  		switch event := event.AsAny().(type) {
  		case anthropic.BetaManagedAgentsStartEvent:
  			fmt.Printf("event_start             %s %s\n", event.Event.Type, event.Event.ID)
  		case anthropic.BetaManagedAgentsDeltaEvent:
  			fmt.Printf("event_delta             preview: %q\n", previews.AgentMessageText(event.EventID))
  		case anthropic.BetaManagedAgentsAgentMessageEvent:
  			// The buffered event carries the complete content: the accumulator
  			// replaces the preview with it
  			fmt.Printf("agent.message           %s %q\n", event.ID, previews.AgentMessageText(event.ID))
  		case anthropic.BetaManagedAgentsSpanModelRequestEndEvent:
  			// No more deltas are coming for this request. The accumulator
  			// drops its snapshots here, closing any preview that was never
  			// reconciled by a buffered agent.message.
  			fmt.Println("span.model_request_end  no more deltas for this request")
  		case anthropic.BetaManagedAgentsSessionStatusIdleEvent:
  			break deltas
  		}
  	}
  	if err := stream.Err(); err != nil {
  		panic(err)
  	}
  	stream.Close()

java Java
  // Preview text, keyed by event ID then content index. The buffered agent.message replaces it.
  Map<String, Map<Long, StringBuilder>> previews = new HashMap<>();

  // Opt in to agent.message previews on this connection
  try (var stream = client.beta().sessions().events().streamStreaming(
          session.id(),
          EventStreamParams.builder()
              .addEventDelta(BetaManagedAgentsDeltaType.AGENT_MESSAGE)
              .build()
  )) {
      client.beta().sessions().events().send(
          session.id(),
          EventSendParams.builder()
              .addEvent(BetaManagedAgentsUserMessageEventParams.builder()
                  .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
                  .addTextContent("Describe the repo in one sentence.")
                  .build())
              .build()
      );

      Iterable<BetaManagedAgentsStreamSessionEvents> events = stream.stream()::iterator;
      for (var event : events) {
          if (event.isEventStart() && event.asEventStart().event().isAgentMessage()) {
              var preview = event.asEventStart().event().asAgentMessage();
              IO.println("event_start             " + preview.type().asString() + " " + preview.id());
          } else if (event.isEventDelta()) {
              var eventDelta = event.asEventDelta();
              var fragment = eventDelta.delta();
              var buffer = previews
                  .computeIfAbsent(eventDelta.eventId(), _ -> new HashMap<>())
                  .computeIfAbsent(fragment.index().orElse(0L), _ -> new StringBuilder());
              buffer.append(fragment.content().text());
              IO.println("event_delta             preview: " + buffer);
          } else if (event.isAgentMessage()) {
              // The buffered event is the record: drop its preview, render its content
              var message = event.asAgentMessage();
              previews.remove(message.id());
              var text = message.content().stream()
                  .flatMap(block -> block.text().stream())
                  .map(textBlock -> textBlock.text())
                  .collect(Collectors.joining());
              IO.println("agent.message           " + message.id() + " " + text);
          } else if (event.isSpanModelRequestEnd()) {
              // No more deltas are coming. Close any preview whose buffered event never arrived.
              previews.keySet().forEach(eventId ->
                  IO.println("span.model_request_end  closing preview for " + eventId));
              previews.clear();
          } else if (event.isSessionStatusIdle()) {
              break;
          }
      }
  }

php PHP
  // In PHP, set eventDeltas on EventStreamParams and accumulate with Anthropic\Lib\Sessions\EventAccumulator.

ruby Ruby
  # Opt in to event deltas: agent.message previews stream as incremental fragments.
  stream = client.beta.sessions.events.stream_events(
    session.id,
    event_deltas: [Anthropic::Beta::BetaManagedAgentsDeltaType::AGENT_MESSAGE]
  )

  client.beta.sessions.events.send_(
    session.id,
    events: [{
      type: "user.message",
      content: [{type: "text", text: "Give a one-sentence project tagline."}]
    }]
  )

  # Accumulate preview fragments by (event_id, index) into explicitly mutable
  # (`+""`) buffers so `<<` can append in place. The buffered agent.message with
  # the same id is authoritative and replaces whatever the deltas built up.
  buffers = Hash.new do |by_event, event_id|
    by_event[event_id] = Hash.new { |fragments, index| fragments[index] = +"" }
  end

  stream.each do |event|
    case event.type
    in :event_start
      puts "event_start             #{event.event.type} #{event.event.id}"
    in :event_delta
      delta = event.delta
      fragment = delta.content.text
      buffers[event.event_id][delta.index || 0] << fragment
      puts "event_delta             preview: #{buffers[event.event_id][delta.index || 0].inspect}"
    in :"agent.message"
      # Replace: drop the accumulated preview and render the complete event.
      buffers.delete(event.id)
      puts "agent.message           #{event.id} #{event.content.map(&:text).join.inspect}"
    in :"span.model_request_end"
      # No more deltas are coming. Close any preview that was never reconciled.
      buffers.each_key { |event_id| puts "span.model_request_end  closing preview for #{event_id}" }
      buffers.clear
    in :"session.status_idle"
      break
    else
      # ignore other event types
    end
  end

bash cURL
  # List the session's threads and pick a child: child threads carry a non-null
  # parent_thread_id, and the primary thread's parent_thread_id is null.
  THREAD_ID=$(
    curl --fail-with-body -sS \
      "https://api.anthropic.com/v1/sessions/$SESSION_ID/threads?beta=true" \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "anthropic-beta: managed-agents-2026-04-01" |
      jq -er 'first(.data[] | select(.parent_thread_id != null)).id'
  )

  # The child thread's stream takes the same event_deltas[] parameter as the
  # session stream. Percent-encode the brackets (%5B%5D) and quote the URL.
  exec {stream}< <(
    curl --fail-with-body -sS -N \
      "https://api.anthropic.com/v1/sessions/$SESSION_ID/threads/$THREAD_ID/stream?beta=true&event_deltas%5B%5D=agent.message" \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "anthropic-beta: managed-agents-2026-04-01" \
      -H "accept: text/event-stream"
  )

  while IFS= read -r -u "$stream" event_line; do
    [[ $event_line == data:* ]] || continue
    event_json=${event_line#data: }
    case $(jq -r '.type' <<<"$event_json") in
      event_delta)
        jq -j '.delta.content.text' <<<"$event_json"
        ;;
      agent.message)
        # The buffered event is the authoritative record; render its content.
        printf '\n'
        jq -j '.content[] | select(.type == "text") | .text' <<<"$event_json"
        printf '\n'
        ;;
      session.thread_status_idle)
        break
        ;;
    esac
  done
  exec {stream}<&-

bash CLI
  # List the session's threads and pick a child: child threads carry a non-null
  # parent_thread_id, and the primary thread's parent_thread_id is null
  # (--transform's #(parent_thread_id!=~null) query matches non-null values).
  THREAD_ID=$(ant beta:sessions:threads list \
    --session-id "$SESSION_ID" \
    --format raw --transform 'data.#(parent_thread_id!=~null).id' --raw-output)

  # The child thread's stream takes the same event_deltas parameter as the
  # session stream, one --event-delta flag per event type to preview. @tostr
  # re-encodes each text field as a JSON string, so every value stays on one
  # YAML line and jq's fromjson recovers the original text.
  transform='{type,frag:delta.content.text|@tostr,text:content.#(type=="text").text|@tostr}'
  exec {stream}< <(ant beta:sessions:threads:events stream \
    --session-id "$SESSION_ID" \
    --thread-id "$THREAD_ID" \
    --event-delta agent.message \
    --transform "$transform" \
    --format yaml)

  type=
  while IFS= read -r -u "$stream" line; do
    case "$line" in
      type:\ session.thread_status_idle) break ;;
      type:\ *) type=${line#type: } ;;
      frag:*)
        [[ $type == event_delta ]] || continue
        jq -j fromjson <<<"${line#frag: }" ;;
      text:*)
        [[ $type == agent.message ]] || continue
        # The buffered event is the authoritative record; render its content.
        printf '\n'
        jq -r fromjson <<<"${line#text: }" ;;
    esac
  done
  exec {stream}<&-

python Python
  # List the session's threads and pick a child: child threads carry a non-null
  # parent_thread_id, and the primary thread's parent_thread_id is null.
  child_thread = next(
      thread
      for thread in client.beta.sessions.threads.list(session.id)
      if thread.parent_thread_id is not None
  )

  # The child thread's stream takes the same event_deltas parameter as the
  # session stream.
  with client.beta.sessions.threads.events.stream(
      child_thread.id,
      session_id=session.id,
      event_deltas=["agent.message"],
  ) as stream:
      for event in stream:
          match event.type:
              case "event_delta":
                  print(event.delta.content.text, end="")
              case "agent.message":
                  # The buffered event is the authoritative record; render its content
                  print()
                  for block in event.content:
                      if block.type == "text":
                          print(block.text, end="")
                  print()
              case "session.thread_status_idle":
                  break

typescript TypeScript
  // List the session's threads and pick a child: child threads carry a non-null
  // parent_thread_id, and the primary thread's parent_thread_id is null.
  let childThreadId: string | undefined;
  for await (const thread of client.beta.sessions.threads.list(session.id)) {
    if (thread.parent_thread_id !== null) {
      childThreadId = thread.id;
      break;
    }
  }
  if (!childThreadId) throw new Error("No child thread found");

  // The child thread's stream takes the same event_deltas parameter as the
  // session stream.
  const stream = await client.beta.sessions.threads.events.stream(childThreadId, {
    session_id: session.id,
    event_deltas: ["agent.message"],
  });

  for await (const event of stream) {
    if (event.type === "event_delta") {
      process.stdout.write(event.delta.content.text);
    } else if (event.type === "agent.message") {
      // The buffered event is the authoritative record; render its content.
      process.stdout.write("\n");
      const text = event.content.map((block) => block.text).join("");
      console.log(text);
    } else if (event.type === "session.thread_status_idle") {
      break;
    }
  }
  stream.controller.abort();

csharp C#
  // List the session's threads and pick a child: child threads carry a non-null
  // parent_thread_id, and the primary thread's parent_thread_id is null.
  var threads = await client.Beta.Sessions.Threads.List(session.ID);
  var childThread = threads.Items.First(thread => thread.ParentThreadID is not null);

  // The child thread's stream takes the same event_deltas parameter as the
  // session stream.
  using var stream = await client.Beta.Sessions.Threads.Events.WithRawResponse.StreamStreaming(
      childThread.ID,
      new() { SessionID = session.ID, EventDeltas = [BetaManagedAgentsDeltaType.AgentMessage] }
  );

  await foreach (var streamEvent in stream.Enumerate())
  {
      if (streamEvent.TryPickDeltaEvent(out var delta))
      {
          Console.Write(delta.Delta.Content.Text);
      }
      else if (streamEvent.TryPickAgentMessageEvent(out var message))
      {
          // The buffered event is the authoritative record; render its content.
          Console.WriteLine();
          Console.WriteLine(string.Concat(message.Content.Select(block => block.Text)));
      }
      else if (streamEvent.TryPickSessionThreadStatusIdleEvent(out _))
      {
          break;
      }
  }

go Go
  	// List the session's threads and pick a child: child threads carry a non-null
  	// parent_thread_id, and the primary thread's parent_thread_id is null.
  	var childThreadID string
  	threads := client.Beta.Sessions.Threads.ListAutoPaging(ctx, session.ID, anthropic.BetaSessionThreadListParams{})
  	for threads.Next() {
  		if thread := threads.Current(); thread.ParentThreadID != "" {
  			childThreadID = thread.ID
  			break
  		}
  	}
  	if err := threads.Err(); err != nil {
  		panic(err)
  	}

  	// The child thread's stream takes the same event_deltas parameter as the
  	// session stream; run one read loop per stream connection.
  	stream := client.Beta.Sessions.Threads.Events.StreamEvents(ctx, childThreadID, anthropic.BetaSessionThreadEventStreamParams{
  		SessionID: session.ID,
  		EventDeltas: []anthropic.BetaManagedAgentsDeltaType{
  			anthropic.BetaManagedAgentsDeltaTypeAgentMessage,
  		},
  	})

  threadDeltas:
  	for stream.Next() {
  		switch event := stream.Current().AsAny().(type) {
  		case anthropic.BetaManagedAgentsDeltaEvent:
  			fmt.Print(event.Delta.Content.Text)
  		case anthropic.BetaManagedAgentsAgentMessageEvent:
  			// The buffered event is the authoritative record; render its content.
  			fmt.Println()
  			// concrete-typed list: BetaManagedAgentsTextBlock
  			for _, block := range event.Content {
  				fmt.Print(block.Text)
  			}
  			fmt.Println()
  		case anthropic.BetaManagedAgentsSessionThreadStatusIdleEvent:
  			break threadDeltas
  		}
  	}
  	if err := stream.Err(); err != nil {
  		panic(err)
  	}
  	stream.Close()

java Java
  // List the session's threads and pick a child: child threads carry a non-null
  // parent_thread_id, and the primary thread's parent_thread_id is null.
  var childThread = client.beta().sessions().threads().list(session.id()).autoPager().stream()
      .filter(thread -> thread.parentThreadId().isPresent())
      .findFirst()
      .orElseThrow();

  // The child thread's stream takes the same event_deltas parameter as the session
  // stream. Its params class shares the session-level one's simple name, so qualify it.
  try (var stream = client.beta().sessions().threads().events().streamStreaming(
          childThread.id(),
          com.anthropic.models.beta.sessions.threads.events.EventStreamParams.builder()
              .sessionId(session.id())
              .addEventDelta(BetaManagedAgentsDeltaType.AGENT_MESSAGE)
              .build()
  )) {
      Iterable<BetaManagedAgentsStreamSessionThreadEvents> events = stream.stream()::iterator;
      for (var event : events) {
          if (event.isEventDelta()) {
              IO.print(event.asEventDelta().delta().content().text());
          } else if (event.isAgentMessage()) {
              // The buffered event is the authoritative record; render its content.
              IO.println();
              event.asAgentMessage().content().forEach(block -> block.text().ifPresent(textBlock -> IO.print(textBlock.text())));
              IO.println();
          } else if (event.isSessionThreadStatusIdle()) {
              break;
          }
      }
  }

php PHP
  // In PHP, set eventDeltas on the thread EventStreamParams and accumulate with Anthropic\Lib\Sessions\EventAccumulator.

ruby Ruby
  # List the session's threads and pick a child: child threads carry a non-null
  # parent_thread_id, and the primary thread's parent_thread_id is null.
  child_thread = client.beta.sessions.threads.list(session.id).to_enum.find { it.parent_thread_id }

  # The child thread's stream takes the same event_deltas parameter as the
  # session stream.
  stream = client.beta.sessions.threads.events.stream_events(
    child_thread.id,
    session_id: session.id,
    event_deltas: [Anthropic::Beta::BetaManagedAgentsDeltaType::AGENT_MESSAGE]
  )

  stream.each do |event|
    case event.type
    in :event_delta
      print event.delta.content.text
    in :"agent.message"
      # The buffered event is the authoritative record; render its content.
      puts
      event.content.each { print it.text }
      puts
    in :"session.thread_status_idle"
      break
    else
      # ignore other event types
    end
  end
  ```
</CodeGroup>

The read loop exits on [`session.thread_status_idle`](https://platform.claude.com/docs/en/managed-agents/reference#event-types), the event emitted when the session thread's turn finishes and the thread goes idle.

### Limitations

Previews are tuned for responsiveness. Build against these constraints:

* **Best effort:** Under load, the server might shed deltas for an event. When it does, you receive a contiguous prefix of the text and then no further deltas for that event. The buffered `agent.message` still arrives complete. Never treat an accumulated preview as final.
* **No replay on reconnect:** Deltas are delivered only to the connection that opted in, while it is open. This applies to the session-level stream and to each session thread stream alike, and a connection opened after a model request started receives no deltas for that in-flight event. If the stream drops, follow the [reconnect procedure](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#integrating-events) in the Streaming events tab: reopen the stream and list the event history. The history includes any buffered events emitted while you were disconnected, including the `agent.message` your preview was waiting for. There is no way to re-request missed deltas.
* **One thread, text only:** Previews cover assistant text on the thread the connection is reading. Tool use, tool results, MCP results, and activity on any other [session thread](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration) are never previewed on that connection.
* **Start-only `agent.thinking`:** An `agent.thinking` preview emits only the `event_start` as a signal that a thinking block has started; no `event_delta` events follow it.
* **Never persisted:** `event_start` and `event_delta` exist only on the live stream. They do not appear in the session's event history (`GET /v1/sessions/{session_id}/events`) or in any session thread's event history.

### Troubleshoot previews

If the stream doesn't behave as you expect:

| You see                                                             | What it means                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A stream with buffered events but no `event_start` or `event_delta` | The connection you're reading didn't opt in (`event_deltas[]` applies per connection, not per session), or the turn never touched the thread you're streaming. Previews are thread-scoped, so list the session's threads (`GET /v1/sessions/{session_id}/threads`) to find which one ran. |
| A 404 on the stream URL                                             | The path or an ID is wrong, or the request carries no managed-agents beta header at all. The thread endpoints are beta-gated, so without the header they don't exist.                                                                                                                     |
| A 400 naming `event_deltas`                                         | Only `agent.message` and `agent.thinking` are accepted.                                                                                                                                                                                                                                   |


## Additional scenarios

Source: https://platform.claude.com/llms-full.txt#additional-scenarios

### Handling custom tool calls

When the agent invokes a [custom tool](https://platform.claude.com/docs/en/managed-agents/tools#custom-tools):

1. The session emits an `agent.custom_tool_use` event containing the tool name and input.
2. The session pauses with a `session.status_idle` event containing `stop_reason: requires_action`. The blocking event IDs are in the `stop_reason.event_ids` array.
3. Execute the tool in your system and send a `user.custom_tool_result` event for each, passing the event ID in the `custom_tool_use_id` parameter along with the result content.
4. Once all blocking events are resolved, the session transitions back to `running`.

<CodeGroup>
  ```bash cURL
  exec {stream_fd}< <(curl --fail-with-body -sS -N \
    "https://api.anthropic.com/v1/sessions/$SESSION_ID/events/stream?beta=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -H "accept: text/event-stream")

  while IFS= read -r -u "$stream_fd" line; do
    [[ $line == data:* ]] || continue
    event_json="${line#data: }"
    stop_reason=$(jq -r 'select(.type == "session.status_idle") | .stop_reason.type // empty' <<<"$event_json")
    case "$stop_reason" in
      requires_action)
        while IFS= read -r event_id; do
          # Execute the tool and send the result back
          result=$(call_tool "$event_id")
          jq -n --arg id "$event_id" --arg result "$result" \
            '{events: [{type: "user.custom_tool_result", custom_tool_use_id: $id, content: [{type: "text", text: $result}]}]}' |
            curl --fail-with-body -sS \
              "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
              -H "x-api-key: $ANTHROPIC_API_KEY" \
              -H "anthropic-version: 2023-06-01" \
              -H "anthropic-beta: managed-agents-2026-04-01" \
              -H "content-type: application/json" \
              -d @-
        done < <(jq -r '.stop_reason.event_ids[]' <<<"$event_json")
        ;;
      end_turn)
        break
        ;;
    esac
  done
  exec {stream_fd}<&-

bash CLI
  # This workflow does not translate well to a one-off shell command.
  # Use one of the SDK examples in this code group instead.

python Python
  with client.beta.sessions.events.stream(session.id) as stream:
      for event in stream:
          if event.type == "session.status_idle" and (stop_reason := event.stop_reason):
              match stop_reason.type:
                  case "requires_action":
                      for event_id in stop_reason.event_ids:
                          # Look up the custom tool use event and execute it
                          tool_event = events_by_id[event_id]
                          result = call_tool(tool_event.name, tool_event.input)

                          # Send the result back
                          client.beta.sessions.events.send(
                              session.id,
                              events=[
                                  {
                                      "type": "user.custom_tool_result",
                                      "custom_tool_use_id": event_id,
                                      "content": [{"type": "text", "text": result}],
                                  },
                              ],
                          )
                  case "end_turn":
                      break

typescript TypeScript
  const stream = await client.beta.sessions.events.stream(session.id);

  for await (const event of stream) {
    if (event.type !== "session.status_idle") continue;
    if (event.stop_reason.type === "end_turn") break;
    if (event.stop_reason.type !== "requires_action") continue;

    for (const eventId of event.stop_reason.event_ids) {
      // Look up the custom tool use event and execute it
      const toolEvent = eventsById.get(eventId);
      if (!toolEvent) continue;
      const result = await callTool(toolEvent.name, toolEvent.input);

      // Send the result back
      await client.beta.sessions.events.send(session.id, {
        events: [
          {
            type: "user.custom_tool_result",
            custom_tool_use_id: eventId,
            content: [{ type: "text", text: result }],
          },
        ],
      });
    }
  }

csharp C#
  await foreach (var streamEvent in client.Beta.Sessions.Events.StreamStreaming(session.ID))
  {
      if (streamEvent.Value is not BetaManagedAgentsSessionStatusIdleEvent idle) continue;

      if (idle.StopReason?.Value is BetaManagedAgentsSessionRequiresAction requiresAction)
      {
          foreach (var eventId in requiresAction.EventIds)
          {
              // Look up the custom tool use event and execute it
              var toolEvent = eventsById[eventId];
              var result = await CallTool(toolEvent.Name, toolEvent.Input);

              // Send the result back
              await client.Beta.Sessions.Events.Send(session.ID, new()
              {
                  Events =
                  [
                      new BetaManagedAgentsUserCustomToolResultEventParams
                      {
                          Type = BetaManagedAgentsUserCustomToolResultEventParamsType.UserCustomToolResult,
                          CustomToolUseID = eventId,
                          Content =
                          [
                              new BetaManagedAgentsTextBlock
                              {
                                  Type = BetaManagedAgentsTextBlockType.Text,
                                  Text = result,
                              },
                          ],
                      },
                  ],
              });
          }
      }
      else if (idle.StopReason?.Value is BetaManagedAgentsSessionEndTurn)
      {
          break;
      }
  }

go Go
  	stream := client.Beta.Sessions.Events.StreamEvents(ctx, session.ID, anthropic.BetaSessionEventStreamParams{})
  	defer stream.Close()

  loop:
  	for stream.Next() {
  		event, ok := stream.Current().AsAny().(anthropic.BetaManagedAgentsSessionStatusIdleEvent)
  		if !ok {
  			continue
  		}
  		switch stopReason := event.StopReason.AsAny().(type) {
  		case anthropic.BetaManagedAgentsSessionRequiresAction:
  			for _, eventID := range stopReason.EventIDs {
  				// Look up the custom tool use event and execute it
  				toolEvent := eventsByID[eventID]
  				result := callTool(toolEvent.Name, toolEvent.Input)
  				// Send the result back
  				if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  					Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  						OfUserCustomToolResult: &anthropic.BetaManagedAgentsUserCustomToolResultEventParams{
  							Type:            anthropic.BetaManagedAgentsUserCustomToolResultEventParamsTypeUserCustomToolResult,
  							CustomToolUseID: eventID,
  							Content: []anthropic.BetaManagedAgentsUserCustomToolResultEventParamsContentUnion{{
  								OfText: &anthropic.BetaManagedAgentsTextBlockParam{
  									Type: anthropic.BetaManagedAgentsTextBlockTypeText,
  									Text: result,
  								},
  							}},
  						},
  					}},
  				}); err != nil {
  					panic(err)
  				}
  			}
  		case anthropic.BetaManagedAgentsSessionEndTurn:
  			break loop
  		}
  	}
  	if err := stream.Err(); err != nil {
  		panic(err)
  	}

java Java
  try (var stream = client.beta().sessions().events().streamStreaming(session.id())) {
      stream.stream()
          .filter(BetaManagedAgentsStreamSessionEvents::isSessionStatusIdle)
          .map(idleEvent -> idleEvent.asSessionStatusIdle().stopReason())
          .takeWhile(stopReason -> !stopReason.isEndTurn())
          .filter(stopReason -> stopReason.isRequiresAction())
          .flatMap(stopReason -> stopReason.asRequiresAction().eventIds().stream())
          .forEach(eventId -> {
              // Look up the custom tool use event and execute it
              var toolEvent = eventsById.get(eventId);
              var result = callTool(toolEvent.name(), toolEvent.input());

              // Send the result back
              client.beta().sessions().events().send(
                  session.id(),
                  EventSendParams.builder()
                      .addEvent(BetaManagedAgentsUserCustomToolResultEventParams.builder()
                          .type(BetaManagedAgentsUserCustomToolResultEventParams.Type.USER_CUSTOM_TOOL_RESULT)
                          .customToolUseId(eventId)
                          .addTextContent(result)
                          .build())
                      .build());
          });
  }

php PHP
  $stream = $client->beta->sessions->events->streamStream($session->id);

  foreach ($stream as $event) {
      if ($event->type === 'session.status_idle' && $event->stopReason) {
          if ($event->stopReason->type === 'requires_action') {
              foreach ($event->stopReason->eventIDs as $eventId) {
                  // Look up the custom tool use event and execute it
                  $toolEvent = $eventsById[$eventId];
                  $result = callTool($toolEvent->name, $toolEvent->input);

                  // Send the result back
                  $client->beta->sessions->events->send(
                      $session->id,
                      events: [
                          [
                              'type' => 'user.custom_tool_result',
                              'custom_tool_use_id' => $eventId,
                              'content' => [['type' => 'text', 'text' => $result]],
                          ],
                      ],
                  );
              }
          } elseif ($event->stopReason->type === 'end_turn') {
              break;
          }
      }
  }

ruby Ruby
  client.beta.sessions.events.stream_events(session.id).each do |event|
    case event
    in {type: :"session.status_idle", stop_reason: {type: :requires_action, event_ids:}}
      event_ids.each do |event_id|
        # Look up the custom tool use event and execute it
        tool_event = events_by_id[event_id]
        result = call_tool.call(tool_event.name, tool_event.input)
        # Send the result back
        client.beta.sessions.events.send_(
          session.id,
          events: [
            {
              type: "user.custom_tool_result",
              custom_tool_use_id: event_id,
              content: [{type: "text", text: result}]
            }
          ]
        )
      end
    in {type: :"session.status_idle", stop_reason: {type: :end_turn}}
      break
    else
    end
  end

bash cURL
  exec {stream_fd}< <(curl --fail-with-body -sS -N \
    "https://api.anthropic.com/v1/sessions/$SESSION_ID/events/stream?beta=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -H "accept: text/event-stream")

  while IFS= read -r -u "$stream_fd" line; do
    [[ $line == data:* ]] || continue
    event_json="${line#data: }"
    stop_reason=$(jq -r 'select(.type == "session.status_idle") | .stop_reason.type // empty' <<<"$event_json")
    case "$stop_reason" in
      requires_action)
        while IFS= read -r event_id; do
          # Approve the pending tool call
          jq -n --arg id "$event_id" \
            '{events: [{type: "user.tool_confirmation", tool_use_id: $id, result: "allow"}]}' |
            curl --fail-with-body -sS \
              "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
              -H "x-api-key: $ANTHROPIC_API_KEY" \
              -H "anthropic-version: 2023-06-01" \
              -H "anthropic-beta: managed-agents-2026-04-01" \
              -H "content-type: application/json" \
              -d @-
        done < <(jq -r '.stop_reason.event_ids[]' <<<"$event_json")
        ;;
      end_turn)
        break
        ;;
    esac
  done
  exec {stream_fd}<&-

bash CLI
  # This workflow does not translate well to a one-off shell command.
  # Use one of the SDK examples in this code group instead.

python Python
  with client.beta.sessions.events.stream(session.id) as stream:
      for event in stream:
          if event.type == "session.status_idle" and (stop_reason := event.stop_reason):
              match stop_reason.type:
                  case "requires_action":
                      for event_id in stop_reason.event_ids:
                          # Approve the pending tool call
                          client.beta.sessions.events.send(
                              session.id,
                              events=[
                                  {
                                      "type": "user.tool_confirmation",
                                      "tool_use_id": event_id,
                                      "result": "allow",
                                  },
                              ],
                          )
                  case "end_turn":
                      break

typescript TypeScript
  const stream = await client.beta.sessions.events.stream(session.id);

  for await (const event of stream) {
    if (event.type !== "session.status_idle") continue;
    if (event.stop_reason.type === "end_turn") break;
    if (event.stop_reason.type !== "requires_action") continue;

    for (const eventId of event.stop_reason.event_ids) {
      // Approve the pending tool call
      await client.beta.sessions.events.send(session.id, {
        events: [
          {
            type: "user.tool_confirmation",
            tool_use_id: eventId,
            result: "allow",
          },
        ],
      });
    }
  }

csharp C#
  await foreach (var streamEvent in client.Beta.Sessions.Events.StreamStreaming(session.ID))
  {
      if (streamEvent.Value is not BetaManagedAgentsSessionStatusIdleEvent idle) continue;

      if (idle.StopReason?.Value is BetaManagedAgentsSessionRequiresAction requiresAction)
      {
          foreach (var eventId in requiresAction.EventIds)
          {
              // Approve the pending tool call
              await client.Beta.Sessions.Events.Send(session.ID, new()
              {
                  Events =
                  [
                      new BetaManagedAgentsUserToolConfirmationEventParams
                      {
                          Type = BetaManagedAgentsUserToolConfirmationEventParamsType.UserToolConfirmation,
                          ToolUseID = eventId,
                          Result = BetaManagedAgentsUserToolConfirmationEventParamsResult.Allow,
                      },
                  ],
              });
          }
      }
      else if (idle.StopReason?.Value is BetaManagedAgentsSessionEndTurn)
      {
          break;
      }
  }

go Go
  	stream := client.Beta.Sessions.Events.StreamEvents(ctx, session.ID, anthropic.BetaSessionEventStreamParams{})
  	defer stream.Close()

  loop:
  	for stream.Next() {
  		event, ok := stream.Current().AsAny().(anthropic.BetaManagedAgentsSessionStatusIdleEvent)
  		if !ok {
  			continue
  		}
  		switch stopReason := event.StopReason.AsAny().(type) {
  		case anthropic.BetaManagedAgentsSessionRequiresAction:
  			for _, eventID := range stopReason.EventIDs {
  				// Approve the pending tool call
  				if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  					Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  						OfUserToolConfirmation: &anthropic.BetaManagedAgentsUserToolConfirmationEventParams{
  							Type:      anthropic.BetaManagedAgentsUserToolConfirmationEventParamsTypeUserToolConfirmation,
  							ToolUseID: eventID,
  							Result:    anthropic.BetaManagedAgentsUserToolConfirmationEventParamsResultAllow,
  						},
  					}},
  				}); err != nil {
  					panic(err)
  				}
  			}
  		case anthropic.BetaManagedAgentsSessionEndTurn:
  			break loop
  		}
  	}
  	if err := stream.Err(); err != nil {
  		panic(err)
  	}

java Java
  try (var stream = client.beta().sessions().events().streamStreaming(session.id())) {
      stream.stream()
          .filter(BetaManagedAgentsStreamSessionEvents::isSessionStatusIdle)
          .map(idleEvent -> idleEvent.asSessionStatusIdle().stopReason())
          .takeWhile(stopReason -> !stopReason.isEndTurn())
          .filter(stopReason -> stopReason.isRequiresAction())
          .flatMap(stopReason -> stopReason.asRequiresAction().eventIds().stream())
          // Approve each pending tool call
          .forEach(toolUseId -> client.beta().sessions().events().send(
              session.id(),
              EventSendParams.builder()
                  .addEvent(BetaManagedAgentsUserToolConfirmationEventParams.builder()
                      .type(BetaManagedAgentsUserToolConfirmationEventParams.Type.USER_TOOL_CONFIRMATION)
                      .toolUseId(toolUseId)
                      .result(BetaManagedAgentsUserToolConfirmationEventParams.Result.ALLOW)
                      .build())
                  .build()));
  }

php PHP
  $stream = $client->beta->sessions->events->streamStream($session->id);

  foreach ($stream as $event) {
      if ($event->type === 'session.status_idle' && $event->stopReason) {
          if ($event->stopReason->type === 'requires_action') {
              foreach ($event->stopReason->eventIDs as $eventId) {
                  // Approve the pending tool call
                  $client->beta->sessions->events->send(
                      $session->id,
                      events: [
                          [
                              'type' => 'user.tool_confirmation',
                              'tool_use_id' => $eventId,
                              'result' => 'allow',
                          ],
                      ],
                  );
              }
          } elseif ($event->stopReason->type === 'end_turn') {
              break;
          }
      }
  }

ruby Ruby
  client.beta.sessions.events.stream_events(session.id).each do |event|
    case event
    in {type: :"session.status_idle", stop_reason: {type: :requires_action, event_ids:}}
      event_ids.each do |event_id|
        # Approve the pending tool call
        client.beta.sessions.events.send_(
          session.id,
          events: [
            {type: "user.tool_confirmation", tool_use_id: event_id, result: "allow"}
          ]
        )
      end
    in {type: :"session.status_idle", stop_reason: {type: :end_turn}}
      break
    else
    end
  end

bash cURL
  # In production, pass the stored ID of the session you want to resume.
  curl --fail-with-body -sS "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<'EOF'
  {
    "events": [
      {
        "type": "user.message",
        "content": [
          {"type": "text", "text": "Now run the tests against the changes you made earlier."}
        ]
      }
    ]
  }
  EOF

bash CLI
  # In production, pass the stored ID of the session you want to resume.
  ant beta:sessions:events send --session-id "$SESSION_ID" <<'YAML'
  events:
    - type: user.message
      content:
        - type: text
          text: Now run the tests against the changes you made earlier.
  YAML

python Python
  # Resume a previously created session by sending it a new user.message event.
  # In production, pass the stored ID of the session you want to resume.
  client.beta.sessions.events.send(
      session.id,
      events=[
          {
              "type": "user.message",
              "content": [
                  {
                      "type": "text",
                      "text": "Now run the tests against the changes you made earlier.",
                  },
              ],
          },
      ],
  )

typescript TypeScript
  // Resume a previously created session by sending it a new user event.
  // In production, pass the stored ID of the session you want to resume.
  await client.beta.sessions.events.send(session.id, {
    events: [
      {
        type: "user.message",
        content: [
          {
            type: "text",
            text: "Now run the tests against the changes you made earlier.",
          },
        ],
      },
    ],
  });

csharp C#
  // Resume a previously created session by ID. In production, pass the
  // session ID you stored when the session was created.
  await client.Beta.Sessions.Events.Send(session.ID, new()
  {
      Events =
      [
          new BetaManagedAgentsUserMessageEventParams
          {
              Type = BetaManagedAgentsUserMessageEventParamsType.UserMessage,
              Content =
              [
                  new BetaManagedAgentsTextBlock
                  {
                      Type = BetaManagedAgentsTextBlockType.Text,
                      Text = "Now run the tests against the changes you made earlier.",
                  },
              ],
          },
      ],
  });

go Go
  // Resume a previously created session by sending it a new user.message
  // event. In production, pass the stored ID of the session to resume.
  if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  	Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  		OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
  			Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
  			Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{{
  				OfText: &anthropic.BetaManagedAgentsTextBlockParam{
  					Type: anthropic.BetaManagedAgentsTextBlockTypeText,
  					Text: "Now run the tests against the changes you made earlier.",
  				},
  			}},
  		},
  	}},
  }); err != nil {
  	panic(err)
  }

java Java
  // Resume a previously created session by ID. In production, pass the
  // session ID you stored when the session was created.
  client.beta().sessions().events().send(
      session.id(),
      EventSendParams.builder()
          .addEvent(BetaManagedAgentsUserMessageEventParams.builder()
              .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
              .addTextContent("Now run the tests against the changes you made earlier.")
              .build())
          .build());

php PHP
  // Resume a previously created session by sending it a new user.message event.
  // In production, pass the session ID you stored when the session was created.
  $client->beta->sessions->events->send(
      $session->id,
      events: [
          [
              'type' => 'user.message',
              'content' => [
                  [
                      'type' => 'text',
                      'text' => 'Now run the tests against the changes you made earlier.',
                  ],
              ],
          ],
      ],
  );

ruby Ruby
  # Resuming a session is just sending the next event to it. In production,
  # pass the session ID you stored when the session was created.
  client.beta.sessions.events.send_(
    session.id,
    events: [
      {
        type: "user.message",
        content: [
          {type: "text", text: "Now run the tests against the changes you made earlier."}
        ]
      }
    ]
  )

bash cURL
  curl --fail-with-body -sS "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<'EOF'
  {
    "events": [
      {
        "type": "system.message",
        "content": [
          {"type": "text", "text": "The user's current timezone is America/New_York."}
        ]
      }
    ]
  }
  EOF

bash CLI
  ant beta:sessions:events send --session-id "$SESSION_ID" <<'YAML'
  events:
    - type: system.message
      content:
        - type: text
          text: "The user's current timezone is America/New_York."
  YAML

python Python
  client.beta.sessions.events.send(
      session.id,
      events=[
          {
              "type": "system.message",
              "content": [
                  {
                      "type": "text",
                      "text": "The user's current timezone is America/New_York.",
                  },
              ],
          },
      ],
  )

typescript TypeScript
  await client.beta.sessions.events.send(session.id, {
    events: [
      {
        type: "system.message",
        content: [
          {
            type: "text",
            text: "The user's current timezone is America/New_York.",
          },
        ],
      },
    ],
  });

csharp C#
  await client.Beta.Sessions.Events.Send(session.ID, new()
  {
      Events =
      [
          new BetaManagedAgentsSystemMessageEventParams
          {
              Type = BetaManagedAgentsSystemMessageEventParamsType.SystemMessage,
              Content =
              [
                  new BetaManagedAgentsSystemContentBlock
                  {
                      Type = BetaManagedAgentsSystemContentBlockType.Text,
                      Text = "The user's current timezone is America/New_York.",
                  },
              ],
          },
      ],
  });

go Go
  if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  	Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  		OfSystemMessage: &anthropic.BetaManagedAgentsSystemMessageEventParams{
  			Type: anthropic.BetaManagedAgentsSystemMessageEventParamsTypeSystemMessage,
  			Content: []anthropic.BetaManagedAgentsSystemContentBlockParam{{
  				Type: anthropic.BetaManagedAgentsSystemContentBlockTypeText,
  				Text: "The user's current timezone is America/New_York.",
  			}},
  		},
  	}},
  }); err != nil {
  	panic(err)
  }

java Java
  client.beta().sessions().events().send(
      session.id(),
      EventSendParams.builder()
          .addEvent(BetaManagedAgentsSystemMessageEventParams.builder()
              .type(BetaManagedAgentsSystemMessageEventParams.Type.SYSTEM_MESSAGE)
              .addTextContent("The user's current timezone is America/New_York.")
              .build())
          .build());

php PHP
  $client->beta->sessions->events->send(
      $session->id,
      events: [
          [
              'type' => 'system.message',
              'content' => [
                  [
                      'type' => 'text',
                      'text' => "The user's current timezone is America/New_York.",
                  ],
              ],
          ],
      ],
  );

ruby Ruby
  client.beta.sessions.events.send_(
    session.id,
    events: [
      {
        type: "system.message",
        content: [
          {type: "text", text: "The user's current timezone is America/New_York."}
        ]
      }
    ]
  )

json
{
  "id": "sesn_01...",
  "status": "idle",
  "usage": {
    "input_tokens": 5000,
    "output_tokens": 3200,
    "cache_read_input_tokens": 20000,
    "cache_creation": {
      "ephemeral_5m_input_tokens": 2000,
      "ephemeral_1h_input_tokens": 0
    },
    "list_cost": {
      "amount": "187",
      "currency": "USD"
    },
    "active_seconds": 342.5,
    "server_tool_use": {
      "web_search_requests": 3,
      "web_fetch_requests": 0
    }
  }
}
```

`input_tokens` reports uncached input tokens and `output_tokens` reports total output tokens across all model calls in the session. The `cache_read_input_tokens` field reports tokens read from the prompt cache, and the `cache_creation` object breaks down cache-creation tokens by cache lifetime (`ephemeral_5m_input_tokens` and `ephemeral_1h_input_tokens`). Cache entries use a 5-minute TTL by default, so back-to-back turns within that window benefit from cache reads, which reduce per-token cost.

`list_cost` is the session's cumulative consumption priced at public list rates, as a whole number of cents in a string, with a currency code. `active_seconds` is the cumulative time during which the session had at least one thread running; overlapping activity from concurrent threads is counted once, unlike the `active_seconds` in the session's `stats` object, which sums each thread's own active time. This deduplicated figure is the duration the session's runtime cost is priced on. `server_tool_use` counts server-executed tool requests for pricing: web search requests are priced into list cost per request, and web fetch requests carry no per-request charge and aren't metered, so `web_fetch_requests` reads `0`. Each [session thread](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration)'s own `usage` carries `list_cost` and `active_seconds` too. Per-thread figures are rounded independently and exclude the session's running-time cost, so they don't sum exactly to the session's `list_cost`; the session figure is the authoritative one.

You don't have to poll the session to observe these totals. The `session.usage` event carries the same cumulative snapshot (the `usage` object, plus the session's `budget`, which is `null` when the session has none) on the session stream and in the event history. It is emitted on idle transitions rather than on a timer: the session emits one immediately before it goes idle, whatever the stop reason, and one when a thread pauses at a [session budget](https://platform.claude.com/docs/en/managed-agents/budgets). A stream reader therefore sees the final cost of a turn, or of the work that hit a budget, without an extra fetch.

To enforce a spend limit, set a [session budget](https://platform.claude.com/docs/en/managed-agents/budgets) rather than polling usage and stopping the session yourself. The platform prices the session's consumption continuously and pauses each thread before its next model request once the session's list cost reaches the cap; see [Reaching a session budget](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#reaching-a-session-budget) for what that looks like on the stream.


## Console observability

Source: https://platform.claude.com/llms-full.txt#console-observability

The Claude Console includes a session viewer for inspecting what an agent did without writing any code. In the Console sidebar, under **Managed Agents**, select **Sessions** to see every session in the workspace with its status, agent, token usage, cost, and creation time, then select a session to open it. The session viewer is only accessible to Developers and Admins. It shows:

* **Timeline minimap:** A zoomable overview of the session's activity over time, with one lane per thread in [multiagent](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration) sessions. Select a lane to view that thread, or select a mark to jump to its event.

* **Transcript:** The conversation grouped by model request, including thinking, tool calls with their inputs and results, and message text as it streams. You can filter the events and copy or download them as JSON.

* **Inspector:** A resizable side panel with details about the session, in five tabs:

  * **Session** shows the session's details and metadata, its cumulative cost over time, and spend against the session's [budget](https://platform.claude.com/docs/en/managed-agents/budgets) when one is set.
  * **Events** lists every raw event on the current thread in the order the server sent it; select an event to see its JSON. A message that streamed while the page was open also has a **Deltas** view of its [event deltas](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#event-deltas).
  * **Tools** lists the tools the session's agents are configured with, along with call counts, failures, and median duration; select a tool to see its calls and jump to one in the transcript.
  * **Resources** lists mounted [files](https://platform.claude.com/docs/en/managed-agents/files), [repositories](https://platform.claude.com/docs/en/managed-agents/github), and [memory stores](https://platform.claude.com/docs/en/managed-agents/memory) at their container paths, including the memories in each store and the changes this session made to them, plus files the agent wrote to `/mnt/session/outputs` and the [skills](https://platform.claude.com/docs/en/managed-agents/skills) attached to the session's agents.
  * **Threads** lists every thread with its status, context size, and cost. Select a thread to view its details, such as the agent, model, context usage, and cost.

Append `?event={event_id}` to a session URL to open the session at a specific event.


## Debugging tips

Source: https://platform.claude.com/llms-full.txt#debugging-tips

* **Check session events:** Session errors are conveyed through the `session.error` event
* **Review tool results:** Tool execution failures often explain unexpected agent behavior
* **Track token usage:** Monitor token consumption to optimize prompts and reduce costs
* **Use system prompts:** Add logging instructions to the system prompt to make the agent explain its reasoning
* **Troubleshoot previews:** If a stream that opts in to event deltas doesn't behave as you expect, see [Troubleshoot previews](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#troubleshoot-previews)


---
title: Session operations
url: https://platform.claude.com/docs/en/managed-agents/session-operations
description: Retrieve, list, update, archive, and delete Claude Managed Agents sessions.
---

Once a session exists, use these operations to read, update, archive, or delete it. See [Start a session](https://platform.claude.com/docs/en/managed-agents/sessions) for creating a session and sending it work.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Session statuses

Source: https://platform.claude.com/llms-full.txt#session-statuses

Sessions progress through these statuses. See [Start a session](https://platform.claude.com/docs/en/managed-agents/sessions) for the session lifecycle.

| Status         | Description                                                                                                                                             |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `idle`         | Agent is waiting for input, including user messages or tool confirmations. Sessions created without `initial_events` start in `idle`.                   |
| `running`      | Agent is actively executing.                                                                                                                            |
| `rescheduling` | Transient error occurred, retrying automatically.                                                                                                       |
| `terminated`   | Session has ended, either because of an unrecoverable error or because it was archived. A session that finishes its work goes `idle`, not `terminated`. |


## Updating the agent configuration

Source: https://platform.claude.com/llms-full.txt#updating-the-agent-configuration

You can update a session's `agent.tools` and `agent.mcp_servers`, including permission policies and per-tool web settings such as [domain filters](https://platform.claude.com/docs/en/managed-agents/tools#restrict-web-search-and-web-fetch-domains), mid-session without creating a new agent version. Updates are session-local and do not propagate back to the underlying agent. Updated `allowed_domains` and `blocked_domains` apply to the rest of the session.

Only the agent's `tools` and `mcp_servers` can change after a session is created. To run a session with `model`, `system`, or `skills` values other than the agent's, use [agent configuration overrides](https://platform.claude.com/docs/en/managed-agents/sessions#override-agent-configuration-for-a-session) when you create the session. The agent's model configuration, including its [`inference_geo`](https://platform.claude.com/docs/en/manage-claude/data-residency) pin, also can't change mid-session: set the pin when you save the agent, or set or clear it for a single session with a `model` override when you create it. The agent's configured `system` field is fixed for the session's lifetime. On models that support it, you can still append system-level guidance mid-session by sending a [`system.message` event](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#sending-system-messages).

The semantics of a `tools` or `mcp_servers` update are full replacement: the provided array is the new value. To preserve existing entries, `GET` the session, modify the array, and `POST` it back.

The session must be `idle` to update the agent. To update the agent while the session is running, send a [`user.interrupt` event](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#integrating-events) by itself and wait for the session to become `idle`.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl -sS --fail-with-body "https://api.anthropic.com/v1/sessions/$SESSION_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "agent": {
      "tools": [
        {"type": "agent_toolset_20260401"},
        {"type": "mcp_toolset", "mcp_server_name": "linear"}
      ],
      "mcp_servers": [
        {"type": "url", "name": "linear", "url": "https://mcp.linear.app/sse"}
      ]
    }
  }
  EOF

bash CLI
  ant beta:sessions update --session-id "$SESSION_ID" <<'YAML'
  agent:
    tools:
      - type: agent_toolset_20260401
      - type: mcp_toolset
        mcp_server_name: linear
    mcp_servers:
      - type: url
        name: linear
        url: https://mcp.linear.app/sse
  YAML

python Python
  client.beta.sessions.update(
      session.id,
      agent={
          "tools": [
              {"type": "agent_toolset_20260401"},
              {"type": "mcp_toolset", "mcp_server_name": "linear"},
          ],
          "mcp_servers": [
              {"type": "url", "name": "linear", "url": "https://mcp.linear.app/sse"}
          ],
      },
  )

typescript TypeScript
  await client.beta.sessions.update(session.id, {
    agent: {
      tools: [
        { type: "agent_toolset_20260401" },
        { type: "mcp_toolset", mcp_server_name: "linear" }
      ],
      mcp_servers: [{ type: "url", name: "linear", url: "https://mcp.linear.app/sse" }]
    }
  });

csharp C#
  await client.Beta.Sessions.Update(session.ID, new()
  {
      Agent = new()
      {
          Tools =
          [
              new BetaManagedAgentsAgentToolset20260401Params
              {
                  Type = BetaManagedAgentsAgentToolset20260401ParamsType.AgentToolset20260401,
              },
              new BetaManagedAgentsMcpToolsetParams
              {
                  Type = BetaManagedAgentsMcpToolsetParamsType.McpToolset,
                  McpServerName = "linear",
              },
          ],
          McpServers =
          [
              new()
              {
                  Type = BetaManagedAgentsUrlMcpServerParamsType.Url,
                  Name = "linear",
                  Url = "https://mcp.linear.app/sse",
              },
          ],
      },
  });

go Go
  _, err = client.Beta.Sessions.Update(ctx, session.ID, anthropic.BetaSessionUpdateParams{
  	Agent: anthropic.BetaManagedAgentsSessionAgentUpdateParam{
  		Tools: []anthropic.BetaManagedAgentsSessionAgentUpdateToolUnionParam{
  			{
  				OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  					Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  				},
  			},
  			{
  				OfMCPToolset: &anthropic.BetaManagedAgentsMCPToolsetParams{
  					Type:          anthropic.BetaManagedAgentsMCPToolsetParamsTypeMCPToolset,
  					MCPServerName: "linear",
  				},
  			},
  		},
  		MCPServers: []anthropic.BetaManagedAgentsURLMCPServerParams{
  			{
  				Type: anthropic.BetaManagedAgentsURLMCPServerParamsTypeURL,
  				Name: "linear",
  				URL:  "https://mcp.linear.app/sse",
  			},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().sessions().update(
      session.id(),
      SessionUpdateParams.builder()
          .agent(BetaManagedAgentsSessionAgentUpdate.builder()
              .addTool(BetaManagedAgentsAgentToolset20260401Params.builder()
                  .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
                  .build())
              .addTool(BetaManagedAgentsMcpToolsetParams.builder()
                  .type(BetaManagedAgentsMcpToolsetParams.Type.MCP_TOOLSET)
                  .mcpServerName("linear")
                  .build())
              .addMcpServer(BetaManagedAgentsUrlMcpServerParams.builder()
                  .type(BetaManagedAgentsUrlMcpServerParams.Type.URL)
                  .name("linear")
                  .url("https://mcp.linear.app/sse")
                  .build())
              .build())
          .build()
  );

php PHP
  $client->beta->sessions->update(
      $session->id,
      agent: BetaManagedAgentsSessionAgentUpdate::with(
          tools: [
              BetaManagedAgentsAgentToolset20260401Params::with(type: 'agent_toolset_20260401'),
              BetaManagedAgentsMCPToolsetParams::with(mcpServerName: 'linear', type: 'mcp_toolset'),
          ],
          mcpServers: [
              BetaManagedAgentsURLMCPServerParams::with(
                  name: 'linear',
                  type: 'url',
                  url: 'https://mcp.linear.app/sse',
              ),
          ],
      ),
  );

ruby Ruby
  client.beta.sessions.update(
    session.id,
    agent: {
      tools: [
        {type: :agent_toolset_20260401},
        {type: :mcp_toolset, mcp_server_name: "linear"}
      ],
      mcp_servers: [
        {type: :url, name: "linear", url: "https://mcp.linear.app/sse"}
      ]
    }
  )
  ```
</CodeGroup>


## Updating the session budget

Source: https://platform.claude.com/llms-full.txt#updating-the-session-budget

A session [created with a budget](https://platform.claude.com/docs/en/managed-agents/sessions#set-a-session-budget) accepts two kinds of budget update: replacing the cap with a new `max_list_cost`, and removing it by setting `budget` to `null`. Both automatically resume work that paused when the session reached its cap. A replacement cap can be higher or lower than the current one, but it must be strictly greater than the session's consumed list cost, and removal is one-way: a non-null `budget` is accepted only on a session that currently has one, so you can't re-add a removed budget or add one to a session created without it. See [Session budgets](https://platform.claude.com/docs/en/managed-agents/budgets#resume-a-session-at-its-budget) for request examples, the error behaviors, and what counts toward list cost.


## Retrieving a session

Source: https://platform.claude.com/llms-full.txt#retrieving-a-session

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  retrieved=$(curl -fsSL "https://api.anthropic.com/v1/sessions/$SESSION_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01")
  echo "Status: $(jq -r '.status' <<< "$retrieved")"

bash CLI
  ant beta:sessions retrieve --session-id "$SESSION_ID"

python Python
  retrieved = client.beta.sessions.retrieve(session.id)
  print(f"Status: {retrieved.status}")

typescript TypeScript
  const retrieved = await client.beta.sessions.retrieve(session.id);
  console.log(`Status: ${retrieved.status}`);

csharp C#
  var retrieved = await client.Beta.Sessions.Retrieve(session.ID);
  Console.WriteLine($"Status: {retrieved.Status.Raw()}");

go Go
  retrieved, err := client.Beta.Sessions.Get(ctx, session.ID, anthropic.BetaSessionGetParams{})
  if err != nil {
  	panic(err)
  }
  fmt.Printf("Status: %s\n", retrieved.Status)

java Java
  var retrieved = client.beta().sessions().retrieve(session.id());
  IO.println("Status: " + retrieved.status());

php PHP
  $retrieved = $client->beta->sessions->retrieve($session->id);
  echo "Status: {$retrieved->status}\n";

ruby Ruby
  retrieved = client.beta.sessions.retrieve(session.id)
  puts "Status: #{retrieved.status}"
  ```
</CodeGroup>


## Listing sessions

Source: https://platform.claude.com/llms-full.txt#listing-sessions

Results from `GET /v1/sessions` are paginated. Use the `limit` query parameter to control the page size. Each response includes a `next_page` cursor; pass it as the `page` parameter on the next request to fetch the following page. `next_page` is `null` when there are no more results.

To go back a page, pass `prev_page` as the `page` parameter. `prev_page` is `null` when you're on the first page.

A `page` cursor is opaque and encodes the `order` of the request that produced it. The `order` query parameter sets the sort direction of the results, `asc` or `desc` by creation time; the default is `desc` (newest first). Reusing a cursor with a different `order` returns a 400 error, as does changing a `created_at` filter so that it excludes the cursor's position. Other query parameters, including the remaining filters and `limit`, can change between paginated requests. For the pagination fields shared across list endpoints, see [Pagination](https://platform.claude.com/docs/en/api/overview#pagination).

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  first_page=$(curl -sS --fail-with-body \
    "https://api.anthropic.com/v1/sessions?agent_id=$AGENT_ID&limit=1" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01")
  jq '{prev_page, next_page}' <<< "$first_page"  # prev_page is null on the first page

  next_cursor=$(jq -r '.next_page' <<< "$first_page")
  second_page=$(curl -sS --fail-with-body \
    "https://api.anthropic.com/v1/sessions?agent_id=$AGENT_ID&limit=1&page=$next_cursor" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01")

  prev_cursor=$(jq -r '.prev_page' <<< "$second_page")
  curl -sS --fail-with-body \
    "https://api.anthropic.com/v1/sessions?agent_id=$AGENT_ID&limit=1&page=$prev_cursor" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    | jq '{prev_page, next_page}'

bash CLI
  # --format raw returns one page envelope with its prev_page and next_page
  # cursors; the default output auto-paginates and emits only the sessions.
  cursors=$(ant beta:sessions list \
    --agent-id "$AGENT_ID" \
    --limit 1 \
    --format raw \
    --transform '{prev_page,next_page}')
  printf '%s\n' "$cursors"

  # Pass the next_page cursor back as --page to fetch the next page.
  NEXT_PAGE=$(jq -r '.next_page' <<< "$cursors")
  ant beta:sessions list \
    --agent-id "$AGENT_ID" \
    --limit 1 \
    --page "$NEXT_PAGE" \
    --format raw \
    --transform '{prev_page,next_page}'
  # Pass that response's prev_page as --page to go back the same way.

python Python
  # Set `limit` low so the results span more than one page.
  first_page = client.beta.sessions.list(limit=1, agent_id=agent.id)
  # `prev_page` is None on the first page; `next_page` is None on the last.
  print(f"prev_page: {first_page.prev_page}")
  print(f"next_page: {first_page.next_page}")

  # Pass `next_page` back as `page` to fetch the next page.
  second_page = client.beta.sessions.list(
      limit=1, agent_id=agent.id, page=first_page.next_page
  )
  for listed_session in second_page.data:
      print(f"{listed_session.id}: {listed_session.status}")

  # Pass `prev_page` back as `page` to return to the previous page.
  previous_page = client.beta.sessions.list(
      limit=1, agent_id=agent.id, page=second_page.prev_page
  )
  for listed_session in previous_page.data:
      print(f"{listed_session.id}: {listed_session.status}")
  # For forward-only iteration, the page object is also directly iterable.

typescript TypeScript
  const firstPage = await client.beta.sessions.list({ limit: 1, agent_id: agent.id });
  // prev_page is null on the first page; next_page is set when more sessions exist.
  console.log(`prev_page: ${firstPage.prev_page}`);
  console.log(`next_page: ${firstPage.next_page}`);

  // Pass next_page as the `page` cursor to fetch the second page.
  const secondPage = await client.beta.sessions.list({
    limit: 1,
    agent_id: agent.id,
    page: firstPage.next_page
  });
  for (const listedSession of secondPage.data) {
    console.log(`Page 2 has ${listedSession.id}: ${listedSession.status}`);
  }

  // Pass the second page's prev_page cursor to step back to the first page.
  const previousPage = await client.beta.sessions.list({
    limit: 1,
    agent_id: agent.id,
    page: secondPage.prev_page
  });
  for (const listedSession of previousPage.data) {
    console.log(`Back on page 1: ${listedSession.id} is ${listedSession.status}`);
  }
  // For forward-only iteration, the page object is also directly iterable.

csharp C#
  // The SessionListPage that `List` returns exposes the items but not the
  // pagination cursors. To read `prev_page` / `next_page`, deserialize the raw
  // response into SessionListPageResponse instead.
  using var page1Response = await client.Beta.Sessions.WithRawResponse.List(
      new SessionListParams { Limit = 1, AgentID = agent.ID }
  );
  var page1 = await page1Response.Deserialize<SessionListPageResponse>();
  Console.WriteLine($"prev_page: {page1.PrevPage ?? "null"}");
  Console.WriteLine($"next_page: {page1.NextPage ?? "null"}");

  // Advance: pass `next_page` from page 1 as the `page` cursor.
  using var page2Response = await client.Beta.Sessions.WithRawResponse.List(
      new SessionListParams { Limit = 1, AgentID = agent.ID, Page = page1.NextPage }
  );
  var page2 = await page2Response.Deserialize<SessionListPageResponse>();
  foreach (var listedSession in page2.Data ?? [])
  {
      Console.WriteLine($"Page 2: {listedSession.ID}: {listedSession.Status.Raw()}");
  }

  // Go back: pass `prev_page` from page 2 as the same `page` cursor.
  using var previousPageResponse = await client.Beta.Sessions.WithRawResponse.List(
      new SessionListParams { Limit = 1, AgentID = agent.ID, Page = page2.PrevPage }
  );
  var previousPage = await previousPageResponse.Deserialize<SessionListPageResponse>();
  foreach (var listedSession in previousPage.Data ?? [])
  {
      Console.WriteLine($"Back to page 1: {listedSession.ID}: {listedSession.Status.Raw()}");
  }
  // For forward-only iteration, (await client.Beta.Sessions.List(...)).Paginate() returns an IAsyncEnumerable that auto-follows next_page.

go Go
  // Page 1: prev_page is empty because nothing precedes the first page.
  firstPage, err := client.Beta.Sessions.List(ctx, anthropic.BetaSessionListParams{
  	AgentID: anthropic.String(agent.ID),
  	Limit:   anthropic.Int(1),
  })
  if err != nil {
  	panic(err)
  }
  fmt.Printf("Page 1 prev_page: %q\n", firstPage.PrevPage)
  fmt.Printf("Page 1 next_page: %q\n", firstPage.NextPage)

  // Advance: pass next_page as the Page cursor to fetch page 2.
  secondPage, err := client.Beta.Sessions.List(ctx, anthropic.BetaSessionListParams{
  	AgentID: anthropic.String(agent.ID),
  	Limit:   anthropic.Int(1),
  	Page:    anthropic.String(firstPage.NextPage),
  })
  if err != nil {
  	panic(err)
  }
  for _, listedSession := range secondPage.Data {
  	fmt.Printf("Page 2: %s: %s\n", listedSession.ID, listedSession.Status)
  }

  // Go back: page 2's prev_page is the cursor for the page before it.
  previousPage, err := client.Beta.Sessions.List(ctx, anthropic.BetaSessionListParams{
  	AgentID: anthropic.String(agent.ID),
  	Limit:   anthropic.Int(1),
  	Page:    anthropic.String(secondPage.PrevPage),
  })
  if err != nil {
  	panic(err)
  }
  for _, listedSession := range previousPage.Data {
  	fmt.Printf("Back to page 1: %s: %s\n", listedSession.ID, listedSession.Status)
  }
  // For forward-only iteration, use ListAutoPaging to auto-follow next_page.

java Java
  var params = SessionListParams.builder()
      .agentId(agent.id())
      .limit(1)
      .build();
  var firstPage = client.beta().sessions().list(params);
  for (var listedSession : firstPage.data()) {
      IO.println(listedSession.id() + ": " + listedSession.status());
  }
  // prev_page is an empty Optional on the first page; next_page points to page 2.
  IO.println("prev_page: " + firstPage.response().prevPage());
  IO.println("next_page: " + firstPage.response().nextPage());

  // Advance by passing next_page as the page cursor.
  var nextCursor = firstPage.response().nextPage().orElseThrow();
  var secondPage = client.beta().sessions().list(params.toBuilder().page(nextCursor).build());

  // Go back by passing prev_page as the same page cursor.
  var prevCursor = secondPage.response().prevPage().orElseThrow();
  var previousPage = client.beta().sessions().list(params.toBuilder().page(prevCursor).build());
  // Back on the first page, so prev_page is empty again.
  IO.println("prev_page: " + previousPage.response().prevPage());
  // For forward-only iteration, page.autoPager() returns an Iterable that auto-follows next_page.

php PHP
  // Page 1: prevPage is null because nothing precedes the first page.
  $firstPage = $client->beta->sessions->list(agentID: $agent->id, limit: 1);
  echo 'Page 1 prev_page: ' . ($firstPage->prevPage ?? 'null') . "\n";
  echo 'Page 1 next_page: ' . ($firstPage->nextPage ?? 'null') . "\n";

  // Advance: pass nextPage back as the `page` cursor to fetch page 2.
  $secondPage = $client->beta->sessions->list(
      agentID: $agent->id,
      limit: 1,
      page: $firstPage->nextPage,
  );
  foreach ($secondPage->getItems() as $listedSession) {
      echo "Page 2: {$listedSession->id}: {$listedSession->status}\n";
  }

  // Go back: page 2's prevPage is the cursor for the page before it.
  $previousPage = $client->beta->sessions->list(
      agentID: $agent->id,
      limit: 1,
      page: $secondPage->prevPage,
  );
  foreach ($previousPage->getItems() as $listedSession) {
      echo "Back to page 1: {$listedSession->id}: {$listedSession->status}\n";
  }
  // For forward-only iteration, $page->pagingEachItem() yields every session across pages.

ruby Ruby
  first_page = client.beta.sessions.list(agent_id: agent.id, limit: 1)
  first_page.data.each do |listed_session|
    puts "#{listed_session.id}: #{listed_session.status}"
  end

  # `prev_page` is nil on the first page. The next-page cursor is exposed as
  # `next_page_` (trailing underscore) because plain `next_page` is the helper
  # method that fetches the next page object for you.
  puts "prev_page: #{first_page.prev_page.inspect}"
  puts "next_page: #{first_page.next_page_.inspect}"

  # Pass either cursor back as `page` to move through the list in both directions.
  second_page = client.beta.sessions.list(
    agent_id: agent.id,
    limit: 1,
    page: first_page.next_page_
  )
  back_to_first = client.beta.sessions.list(
    agent_id: agent.id,
    limit: 1,
    page: second_page.prev_page
  )
  back_to_first.data.each do |listed_session|
    puts "#{listed_session.id}: #{listed_session.status}"
  end
  # For forward-only iteration, page.auto_paging_each auto-follows next_page.
  ```
</CodeGroup>


## Archiving a session

Source: https://platform.claude.com/llms-full.txt#archiving-a-session

Archive a session to prevent new events from being sent while preserving its history. A `running` session cannot be archived; to archive one, send a [`user.interrupt` event](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#integrating-events) by itself and wait for the session to become `idle`.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl -fsSL -X POST "https://api.anthropic.com/v1/sessions/$SESSION_ID/archive" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
  ant beta:sessions archive \
    --session-id "$SESSION_ID"

python Python
  client.beta.sessions.archive(session.id)

typescript TypeScript
  await client.beta.sessions.archive(session.id);

csharp C#
  await client.Beta.Sessions.Archive(session.ID);

go Go
  _, err = client.Beta.Sessions.Archive(ctx, session.ID, anthropic.BetaSessionArchiveParams{})
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().sessions().archive(session.id());

php PHP
  $client->beta->sessions->archive($session->id);

ruby Ruby
  client.beta.sessions.archive(session.id)
  ```
</CodeGroup>


## Deleting a session

Source: https://platform.claude.com/llms-full.txt#deleting-a-session

Delete a session to permanently remove its record, events, and associated sandbox. A `running` session cannot be deleted; to delete one, send a [`user.interrupt` event](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#integrating-events) by itself and wait for the session to become `idle`.

Memory stores, vaults, skills, environments, and agents are independent resources and are not affected by session deletion. Files you uploaded through the Files API are also unaffected, but files the session itself produced are scoped to it and are permanently deleted along with its filesystem. Download anything you need to keep before deleting the session. An output file written at the end of the last turn can take a few seconds after the session goes idle to appear in the [session's file list](https://platform.claude.com/docs/en/managed-agents/files#listing-and-downloading-session-files), so check that the files you expect are listed first.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl -fsSL -X DELETE "https://api.anthropic.com/v1/sessions/$SESSION_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
  ant beta:sessions delete \
    --session-id "$SESSION_ID"

python Python
  client.beta.sessions.delete(session.id)

typescript TypeScript
  await client.beta.sessions.delete(session.id);

csharp C#
  await client.Beta.Sessions.Delete(session.ID);

go Go
  _, err = client.Beta.Sessions.Delete(ctx, session.ID, anthropic.BetaSessionDeleteParams{})
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().sessions().delete(session.id());

php PHP
  $client->beta->sessions->delete($session->id);

ruby Ruby
  client.beta.sessions.delete(session.id)
  ```
</CodeGroup>


---
title: Start a session
url: https://platform.claude.com/docs/en/managed-agents/sessions
description: Create a session to run your agent and begin executing tasks.
---

A session is an agent instance within an environment. Each session references an [agent](https://platform.claude.com/docs/en/managed-agents/agent-setup) and an [environment](https://platform.claude.com/docs/en/managed-agents/environments) (both created separately), and maintains conversation history across multiple interactions. Sessions follow a two-step lifecycle: first [create the session](https://platform.claude.com/docs/en/managed-agents/sessions#creating-a-session), then [send a user event](https://platform.claude.com/docs/en/managed-agents/sessions#starting-the-session) to start work. You can also collapse both steps into one call with [`initial_events`](https://platform.claude.com/docs/en/managed-agents/sessions#seed-the-session-with-initial-events).

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Creating a session

Source: https://platform.claude.com/llms-full.txt#creating-a-session

A session requires an `agent` ID and an `environment` ID. Agents are versioned resources; passing in the `agent` ID as a string creates the session with the latest agent version.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  session=$(curl -fsSL https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "agent": "$AGENT_ID",
    "environment_id": "$ENVIRONMENT_ID"
  }
  EOF
  )
  SESSION_ID=$(jq -r '.id' <<< "$session")

bash CLI
  ant beta:sessions create \
    --agent "$AGENT_ID" \
    --environment-id "$ENVIRONMENT_ID"

python Python
  session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
  )

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id
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

bash cURL
  pinned_session=$(curl -fsSL https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "agent": {"type": "agent", "id": "$AGENT_ID", "version": 1},
    "environment_id": "$ENVIRONMENT_ID"
  }
  EOF
  )
  PINNED_SESSION_ID=$(jq -r '.id' <<< "$pinned_session")

bash CLI
  ant beta:sessions create <<YAML
  agent:
    type: agent
    id: $AGENT_ID
    version: 1
  environment_id: $ENVIRONMENT_ID
  YAML

python Python
  pinned_session = client.beta.sessions.create(
      agent={"type": "agent", "id": agent.id, "version": 1},
      environment_id=environment.id,
  )

typescript TypeScript
  const pinnedSession = await client.beta.sessions.create({
    agent: { type: "agent", id: agent.id, version: 1 },
    environment_id: environment.id
  });

csharp C#
  var pinnedSession = await client.Beta.Sessions.Create(new()
  {
      Agent = new BetaManagedAgentsAgentParams
      {
          Type = BetaManagedAgentsAgentParamsType.Agent,
          ID = agent.ID,
          Version = 1,
      },
      EnvironmentID = environment.ID,
  });

go Go
  pinnedSession, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfBetaManagedAgentsAgents: &anthropic.BetaManagedAgentsAgentParams{
  			Type:    anthropic.BetaManagedAgentsAgentParamsTypeAgent,
  			ID:      agent.ID,
  			Version: anthropic.Int(1),
  		},
  	},
  	EnvironmentID: environment.ID,
  })
  if err != nil {
  	panic(err)
  }

java Java
  var pinnedSession = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(BetaManagedAgentsAgentParams.builder()
          .type(BetaManagedAgentsAgentParams.Type.AGENT)
          .id(agent.id())
          .version(1)
          .build())
      .environmentId(environment.id())
      .build());

php PHP
  $pinnedSession = $client->beta->sessions->create(
      agent: ['type' => 'agent', 'id' => $agent->id, 'version' => 1],
      environmentID: $environment->id,
  );

ruby Ruby
  pinned_session = client.beta.sessions.create(
    agent: {type: :agent, id: agent.id, version: 1},
    environment_id: environment.id
  )

bash cURL
  seeded_session=$(curl -fsSL https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "agent": "$AGENT_ID",
    "environment_id": "$ENVIRONMENT_ID",
    "initial_events": [
      {
        "type": "user.message",
        "content": [{"type": "text", "text": "List the files in the working directory."}]
      }
    ]
  }
  EOF
  )
  SEEDED_SESSION_ID=$(jq -r '.id' <<< "$seeded_session")

  # initial_events aren't echoed on the create response; list the session's
  # events to see the seeded message.
  seeded_events=$(curl -fsSL \
    "https://api.anthropic.com/v1/sessions/$SEEDED_SESSION_ID/events" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01")
  echo "Seeded event: $(jq -r \
    '.data[] | select(.type == "user.message") | .content[0].text' <<< "$seeded_events")"

bash CLI
  SEEDED_SESSION_ID=$(ant beta:sessions create \
    --transform id --raw-output <<YAML
  agent: $AGENT_ID
  environment_id: $ENVIRONMENT_ID
  initial_events:
    - type: user.message
      content:
        - type: text
          text: List the files in the working directory.
  YAML
  )

  # initial_events aren't echoed on the create response; list the session's
  # events to see the seeded message.
  echo "Seeded event: $(ant beta:sessions:events list \
    --session-id "$SEEDED_SESSION_ID" \
    --format raw \
    --transform 'data.#(type=="user.message").content.0.text' --raw-output)"

python Python
  seeded_session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
      initial_events=[
          {
              "type": "user.message",
              "content": [
                  {"type": "text", "text": "List the files in the working directory."}
              ],
          },
      ],
  )
  # initial_events are not echoed on the create response; read them back
  # from the session's event list.
  for event in client.beta.sessions.events.list(seeded_session.id):
      if event.type == "user.message":
          for block in event.content:
              if block.type == "text":
                  print(f"Seeded event: {block.text}")

typescript TypeScript
  const seededSession = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id,
    initial_events: [
      {
        type: "user.message",
        content: [{ type: "text", text: "List the files in the working directory." }]
      }
    ]
  });

  // initial_events are not echoed on the create response; list the session's
  // events to read the seeded message back.
  for await (const event of client.beta.sessions.events.list(seededSession.id)) {
    if (event.type === "user.message") {
      for (const block of event.content) {
        if (block.type === "text") {
          console.log(`Seeded event: ${block.text}`);
        }
      }
    }
  }

csharp C#
  var seededSession = await client.Beta.Sessions.Create(new()
  {
      Agent = agent.ID,
      EnvironmentID = environment.ID,
      InitialEvents =
      [
          new BetaManagedAgentsUserMessageEventParams
          {
              Type = BetaManagedAgentsUserMessageEventParamsType.UserMessage,
              Content =
              [
                  new BetaManagedAgentsTextBlock
                  {
                      Type = BetaManagedAgentsTextBlockType.Text,
                      Text = "List the files in the working directory.",
                  },
              ],
          },
      ],
  });
  // initial_events are not echoed on the create response; read them back
  // from the session's event list.
  var seededEvents = await client.Beta.Sessions.Events.List(seededSession.ID);
  await foreach (var sessionEvent in seededEvents.Paginate())
  {
      if (sessionEvent.TryPickUserMessage(out var userMessage))
      {
          foreach (var contentBlock in userMessage.Content)
          {
              if (contentBlock.TryPickBetaManagedAgentsTextBlock(out var textBlock))
              {
                  Console.WriteLine($"Seeded event: {textBlock.Text}");
              }
          }
      }
  }

go Go
  seededSession, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfString: anthropic.String(agent.ID),
  	},
  	EnvironmentID: environment.ID,
  	InitialEvents: []anthropic.BetaSessionNewParamsInitialEventUnion{{
  		OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
  			Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
  			Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{{
  				OfText: &anthropic.BetaManagedAgentsTextBlockParam{
  					Type: anthropic.BetaManagedAgentsTextBlockTypeText,
  					Text: "List the files in the working directory.",
  				},
  			}},
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }
  // initial_events are not echoed on the create response, so list the
  // session's events to read the seeded user.message back.
  seededEvents, err := client.Beta.Sessions.Events.List(ctx, seededSession.ID, anthropic.BetaSessionEventListParams{})
  if err != nil {
  	panic(err)
  }
  for _, event := range seededEvents.Data {
  	if event.Type != "user.message" {
  		continue
  	}
  	for _, contentBlock := range event.AsUserMessage().Content {
  		if contentBlock.Type == "text" {
  			fmt.Printf("Seeded event: %s\n", contentBlock.AsText().Text)
  		}
  	}
  }

java Java
  var seededSession = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(agent.id())
      .environmentId(environment.id())
      .addInitialEvent(BetaManagedAgentsUserMessageEventParams.builder()
          .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
          .addTextContent("List the files in the working directory.")
          .build())
      .build());
  // initial_events are not echoed on the create response; list the
  // session's events to read the seeded user.message back.
  for (var event : client.beta().sessions().events().list(seededSession.id()).autoPager()) {
      if (event.isUserMessage()) {
          for (var contentBlock : event.asUserMessage().content()) {
              if (contentBlock.isText()) {
                  IO.println("Seeded event: " + contentBlock.asText().text());
              }
          }
      }
  }

php PHP
  $seededSession = $client->beta->sessions->create(
      agent: $agent->id,
      environmentID: $environment->id,
      initialEvents: [
          [
              'type' => 'user.message',
              'content' => [['type' => 'text', 'text' => 'List the files in the working directory.']],
          ],
      ],
  );

  // initial_events are not echoed on the create response; read them back
  // from the session's event list.
  $seededEvents = $client->beta->sessions->events->list($seededSession->id);
  foreach ($seededEvents->getItems() as $event) {
      if ($event->type === 'user.message') {
          echo "Seeded event: {$event->content[0]->text}\n";
      }
  }

ruby Ruby
  seeded_session = client.beta.sessions.create(
    agent: agent.id,
    environment_id: environment.id,
    initial_events: [
      {
        type: :"user.message",
        content: [{type: :text, text: "List the files in the working directory."}]
      }
    ]
  )

  # initial_events are not echoed on the create response; read them back from
  # the session's event list.
  client.beta.sessions.events.list(seeded_session.id).auto_paging_each do |event|
    next unless event.type == :"user.message"
    event.content.each do |block|
      puts "Seeded event: #{block.text}" if block.type == :text
    end
  end

bash cURL
  override_session=$(curl -fsSL https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "agent": {
      "type": "agent_with_overrides",
      "id": "$AGENT_ID",
      "model": {"id": "claude-sonnet-5"},
      "system": null
    },
    "environment_id": "$ENVIRONMENT_ID"
  }
  EOF
  )
  jq '.agent | {id, version, model, system}' <<< "$override_session"
  OVERRIDE_SESSION_ID=$(jq -r '.id' <<< "$override_session")

bash CLI
  # The response's `agent` is the resolved snapshot: each override replaces that
  # field for this session only, and the agent resource keeps its id and version.
  ant beta:sessions create \
    --transform 'agent.{id,version,model,system}' \
    --format json <<YAML
  agent:
    type: agent_with_overrides
    id: $AGENT_ID
    model:
      id: claude-sonnet-5
    system: null
  environment_id: $ENVIRONMENT_ID
  YAML

python Python
  override_session = client.beta.sessions.create(
      agent={
          "type": "agent_with_overrides",
          "id": agent.id,
          "model": {"id": "claude-sonnet-5"},
          "system": None,  # clear the agent's system prompt for this session
      },
      environment_id=environment.id,
  )
  # The response's agent is the resolved snapshot with the overrides applied.
  print(f"Model: {override_session.agent.model.id}")
  print(f"System: {override_session.agent.system}")

typescript TypeScript
  const overrideSession = await client.beta.sessions.create({
    agent: {
      type: "agent_with_overrides",
      id: agent.id,
      model: { id: "claude-sonnet-5" },
      system: null // clear the agent's system prompt for this session
    },
    environment_id: environment.id
  });
  // The response's agent is the resolved snapshot with the overrides applied.
  console.log(`Model: ${overrideSession.agent.model.id}`);
  console.log(`System: ${overrideSession.agent.system}`);

csharp C#
  var overrideSession = await client.Beta.Sessions.Create(new()
  {
      Agent = new BetaManagedAgentsAgentWithOverridesParams
      {
          Type = BetaManagedAgentsAgentWithOverridesParamsType.AgentWithOverrides,
          ID = agent.ID,
          Model = new BetaManagedAgentsModelConfigParams
          {
              ID = BetaManagedAgentsModel.ClaudeSonnet5,
          },
          System = null, // clear the agent's system prompt for this session
      },
      EnvironmentID = environment.ID,
  });
  // The response's agent is the resolved snapshot with the overrides applied.
  Console.WriteLine($"Model: {overrideSession.Agent.Model.ID.Raw()}");
  Console.WriteLine($"System: {overrideSession.Agent.System ?? "null"}");

go Go
  overrideSession, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfBetaManagedAgentsAgentWithOverridess: &anthropic.BetaManagedAgentsAgentWithOverridesParams{
  			Type: anthropic.BetaManagedAgentsAgentWithOverridesParamsTypeAgentWithOverrides,
  			ID:   agent.ID,
  			Model: anthropic.BetaManagedAgentsModelConfigParams{
  				ID: anthropic.BetaManagedAgentsModelClaudeSonnet5,
  			},
  			// Clear the agent's system prompt for this session.
  			System: param.Null[string](),
  		},
  	},
  	EnvironmentID: environment.ID,
  })
  if err != nil {
  	panic(err)
  }
  // The response's agent is the resolved snapshot with the overrides applied.
  fmt.Printf("Model: %s\n", overrideSession.Agent.Model.ID)
  fmt.Printf("System: %q\n", overrideSession.Agent.System)

java Java
  var overrideSession = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(BetaManagedAgentsAgentWithOverridesParams.builder()
          .type(BetaManagedAgentsAgentWithOverridesParams.Type.AGENT_WITH_OVERRIDES)
          .id(agent.id())
          .model(BetaManagedAgentsModelConfigParams.builder()
              .id(BetaManagedAgentsModel.CLAUDE_SONNET_5)
              .build())
          .system((String) null) // clear the agent's system prompt for this session
          .build())
      .environmentId(environment.id())
      .build());
  // The response's agent is the resolved snapshot with the overrides applied.
  IO.println("Model: " + overrideSession.agent().model().id());
  IO.println("System: " + overrideSession.agent().system().orElse("null"));

php PHP
  $overrides = BetaManagedAgentsAgentWithOverridesParams::with(
      id: $agent->id,
      type: 'agent_with_overrides',
      model: ['id' => 'claude-sonnet-5'],
  );
  // Clear the system prompt for this session. Array access is load-bearing here:
  // create() strips nulls from raw arrays and ::with() treats null args as omitted.
  $overrides['system'] = null;

  $overrideSession = $client->beta->sessions->create(
      agent: $overrides,
      environmentID: $environment->id,
  );
  // The response's agent is the resolved snapshot with the overrides applied.
  echo "Model: {$overrideSession->agent->model->id}\n";
  echo 'System: ' . ($overrideSession->agent->system ?? 'null') . "\n";

ruby Ruby
  # The system prompt override is `system_` (trailing underscore) because plain
  # `system` is Ruby's Kernel#system. Setting it to nil clears the prompt.
  override_session = client.beta.sessions.create(
    agent: Anthropic::Beta::BetaManagedAgentsAgentWithOverridesParams.new(
      type: :agent_with_overrides,
      id: agent.id,
      model: {id: "claude-sonnet-5"},
      system_: nil
    ),
    environment_id: environment.id
  )
  # The response's agent is the resolved snapshot with the overrides applied.
  puts "Model: #{override_session.agent.model.id}"
  puts "System: #{override_session.agent.system_.inspect}"

bash cURL
  # Replaces the agent's `model` in full: restate `id`, add `inference_geo` to pin.
  session=$(curl -fsSL https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "agent": {
      "type": "agent_with_overrides",
      "id": "$AGENT_ID",
      "model": {"id": "claude-opus-5", "inference_geo": "us"}
    },
    "environment_id": "$ENVIRONMENT_ID"
  }
  EOF
  )
  echo "Inference geo: $(jq -r '.agent.model.inference_geo' <<< "$session")"

bash CLI
  # Replaces the agent's `model` in full: restate `id`, add `inference_geo` to pin.
  session=$(ant beta:sessions create <<YAML
  agent:
    type: agent_with_overrides
    id: $AGENT_ID
    model:
      id: claude-opus-5
      inference_geo: us
  environment_id: $ENVIRONMENT_ID
  YAML
  )
  echo "Inference geo: $(jq -r '.agent.model.inference_geo' <<< "$session")"

python Python
  session = client.beta.sessions.create(
      agent={
          "type": "agent_with_overrides",
          "id": agent.id,
          # Replaces the agent's `model` in full: restate `id`, add `inference_geo` to pin.
          "model": {"id": "claude-opus-5", "inference_geo": "us"},
      },
      environment_id=environment.id,
  )
  print(f"Inference geo: {session.agent.model.inference_geo}")

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: {
      type: "agent_with_overrides",
      id: agent.id,
      // Replaces the agent's `model` in full: restate `id`, add `inference_geo` to pin.
      model: { id: "claude-opus-5", inference_geo: "us" }
    },
    environment_id: environment.id
  });
  console.log(`Inference geo: ${session.agent.model.inference_geo}`);

csharp C#
  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = new BetaManagedAgentsAgentWithOverridesParams
      {
          Type = BetaManagedAgentsAgentWithOverridesParamsType.AgentWithOverrides,
          ID = agent.ID,
          // Replaces the agent's `model` in full: restate `id`, add `inference_geo` to pin.
          Model = new BetaManagedAgentsModelConfigParams
          {
              ID = BetaManagedAgentsModel.ClaudeOpus5,
              InferenceGeo = "us",
          },
      },
      EnvironmentID = environment.ID,
  });
  Console.WriteLine($"Inference geo: {session.Agent.Model.InferenceGeo}");

go Go
  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfBetaManagedAgentsAgentWithOverridess: &anthropic.BetaManagedAgentsAgentWithOverridesParams{
  			Type: anthropic.BetaManagedAgentsAgentWithOverridesParamsTypeAgentWithOverrides,
  			ID:   agent.ID,
  			// Replaces the agent's `model` in full: restate `id`, add `inference_geo` to pin.
  			Model: anthropic.BetaManagedAgentsModelConfigParams{
  				ID:           anthropic.BetaManagedAgentsModelClaudeOpus5,
  				InferenceGeo: anthropic.String("us"),
  			},
  		},
  	},
  	EnvironmentID: environment.ID,
  })
  if err != nil {
  	panic(err)
  }
  fmt.Printf("Inference geo: %s\n", session.Agent.Model.InferenceGeo)

java Java
  var session = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(BetaManagedAgentsAgentWithOverridesParams.builder()
          .type(BetaManagedAgentsAgentWithOverridesParams.Type.AGENT_WITH_OVERRIDES)
          .id(agent.id())
          // Replaces the agent's `model` in full: restate `id`, add `inference_geo` to pin.
          .model(BetaManagedAgentsModelConfigParams.builder()
              .id(BetaManagedAgentsModel.CLAUDE_OPUS_5)
              .inferenceGeo("us")
              .build())
          .build())
      .environmentId(environment.id())
      .build());
  IO.println("Inference geo: " + session.agent().model().inferenceGeo().orElseThrow());

php PHP
  $session = $client->beta->sessions->create(
      agent: BetaManagedAgentsAgentWithOverridesParams::with(
          id: $agent->id,
          type: 'agent_with_overrides',
          // Replaces the agent's `model` in full: restate `id`, add `inference_geo` to pin.
          model: BetaManagedAgentsModelConfigParams::with(
              id: 'claude-opus-5',
              inferenceGeo: 'us',
          ),
      ),
      environmentID: $environment->id,
  );
  echo "Inference geo: {$session->agent->model->inferenceGeo}\n";

ruby Ruby
  session = client.beta.sessions.create(
    agent: {
      type: :agent_with_overrides,
      id: agent.id,
      # Replaces the agent's `model` in full: restate `id`, add `inference_geo` to pin.
      model: {id: "claude-opus-5", inference_geo: "us"}
    },
    environment_id: environment.id
  )
  puts "Inference geo: #{session.agent.model.inference_geo}"

bash cURL
curl -fsSL https://api.anthropic.com/v1/sessions \
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
    "max_list_cost": {"amount": "2500", "currency": "USD"}
  }
}
EOF
```

See [Session budgets](https://platform.claude.com/docs/en/managed-agents/budgets) for how enforcement works, what counts toward list cost, and how budgets behave in multiagent sessions.


## MCP authentication through vaults

Source: https://platform.claude.com/llms-full.txt#mcp-authentication-through-vaults

If your agent uses MCP tools that require authentication, pass `vault_ids` at session creation to reference a vault containing stored OAuth credentials. Anthropic manages token refresh on your behalf. See [Authenticate with vaults](https://platform.claude.com/docs/en/managed-agents/vaults) for how to create vaults and register credentials.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  vault_session=$(curl -fsSL https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "agent": "$AGENT_ID",
    "environment_id": "$ENVIRONMENT_ID",
    "vault_ids": ["$VAULT_ID"]
  }
  EOF
  )
  VAULT_SESSION_ID=$(jq -r '.id' <<< "$vault_session")

bash CLI
  ant beta:sessions create <<YAML
  agent: $AGENT_ID
  environment_id: $ENVIRONMENT_ID
  vault_ids:
    - $VAULT_ID
  YAML

python Python
  vault_session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
      vault_ids=[vault.id],
  )

typescript TypeScript
  const vaultSession = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id,
    vault_ids: [vault.id]
  });

csharp C#
  var vaultSession = await client.Beta.Sessions.Create(new()
  {
      Agent = agent.ID,
      EnvironmentID = environment.ID,
      VaultIds = [vault.ID],
  });

go Go
  vaultSession, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfString: anthropic.String(agent.ID),
  	},
  	EnvironmentID: environment.ID,
  	VaultIDs:      []string{vault.ID},
  })
  if err != nil {
  	panic(err)
  }

java Java
  var vaultSession = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(agent.id())
      .environmentId(environment.id())
      .addVaultId(vault.id())
      .build());

php PHP
  $vaultSession = $client->beta->sessions->create(
      agent: $agent->id,
      environmentID: $environment->id,
      vaultIDs: [$vault->id],
  );

ruby Ruby
  vault_session = client.beta.sessions.create(
    agent: agent.id,
    environment_id: environment.id,
    vault_ids: [vault.id]
  )
  ```
</CodeGroup>


## Starting the session

Source: https://platform.claude.com/llms-full.txt#starting-the-session

Creating a session without `initial_events` registers the session but does not start any work; the environment's sandbox begins provisioning as soon as the session is created, so the first tool call does not wait on it. To delegate a task, send events to the session using a [user event](https://platform.claude.com/docs/en/managed-agents/reference#event-types). To supply the first event in the create request instead, see [Seed the session with initial events](https://platform.claude.com/docs/en/managed-agents/sessions#seed-the-session-with-initial-events). The session acts as a state machine that tracks progress while events drive the actual execution.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl -fsSL "https://api.anthropic.com/v1/sessions/$SESSION_ID/events" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<'EOF'
  {
    "events": [
      {
        "type": "user.message",
        "content": [{"type": "text", "text": "List the files in the working directory."}]
      }
    ]
  }
  EOF

bash CLI
  ant beta:sessions:events send \
    --session-id "$SESSION_ID" <<'YAML'
  events:
    - type: user.message
      content:
        - type: text
          text: List the files in the working directory.
  YAML

python Python
  client.beta.sessions.events.send(
      session.id,
      events=[
          {
              "type": "user.message",
              "content": [
                  {"type": "text", "text": "List the files in the working directory."}
              ],
          },
      ],
  )

typescript TypeScript
  await client.beta.sessions.events.send(session.id, {
    events: [
      {
        type: "user.message",
        content: [{ type: "text", text: "List the files in the working directory." }]
      }
    ]
  });

csharp C#
  await client.Beta.Sessions.Events.Send(session.ID, new()
  {
      Events =
      [
          new BetaManagedAgentsUserMessageEventParams
          {
              Type = BetaManagedAgentsUserMessageEventParamsType.UserMessage,
              Content =
              [
                  new BetaManagedAgentsTextBlock
                  {
                      Type = BetaManagedAgentsTextBlockType.Text,
                      Text = "List the files in the working directory.",
                  },
              ],
          },
      ],
  });

go Go
  if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  	Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
  		OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
  			Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
  			Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{{
  				OfText: &anthropic.BetaManagedAgentsTextBlockParam{
  					Type: anthropic.BetaManagedAgentsTextBlockTypeText,
  					Text: "List the files in the working directory.",
  				},
  			}},
  		},
  	}},
  }); err != nil {
  	panic(err)
  }

java Java
  client.beta().sessions().events().send(
      session.id(),
      EventSendParams.builder()
          .addEvent(BetaManagedAgentsUserMessageEventParams.builder()
              .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
              .addTextContent("List the files in the working directory.")
              .build())
          .build());

php PHP
  $client->beta->sessions->events->send(
      $session->id,
      events: [
          [
              'type' => 'user.message',
              'content' => [['type' => 'text', 'text' => 'List the files in the working directory.']],
          ],
      ],
  );

ruby Ruby
  client.beta.sessions.events.send_(
    session.id,
    events: [
      {
        type: :"user.message",
        content: [{type: :text, text: "List the files in the working directory."}]
      }
    ]
  )
  ```
</CodeGroup>

See [Session event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming) for how to stream the agent's responses and handle tool confirmations.

See [Session statuses](https://platform.claude.com/docs/en/managed-agents/session-operations#session-statuses) for the statuses a session moves through.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-77

<CardGroup cols={3}>
  <Card title="Session operations" icon="settings" href="https://platform.claude.com/docs/en/managed-agents/session-operations">
    Retrieve, list, update, archive, and delete Claude Managed Agents sessions.
  </Card>

  <Card title="Session event stream" icon="lightning" href="https://platform.claude.com/docs/en/managed-agents/events-and-streaming">
    Send events, stream responses, and interrupt or redirect your session mid-execution.
  </Card>

  <Card title="Scheduled deployments" icon="arrows-clockwise" href="https://platform.claude.com/docs/en/managed-agents/scheduled-deployments">
    Create and manage deployments with the Claude API: run an agent on a recurring cron schedule and inspect its run history.
  </Card>
</CardGroup>


---
title: Subscribe to webhooks
url: https://platform.claude.com/docs/en/managed-agents/webhooks
description: Get notified when major events happen without polling.
---

Sessions are long-running interactions. While most real-time interactions happen through the [SSE event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming), webhooks notify you of major state changes.

Webhook events return the event `type` and `id`, not the full object. When you receive a webhook event, you need to fetch the object directly with a `GET` call. This avoids delivering stale data on retries and keeps every delivery small.


## Supported event types

Source: https://platform.claude.com/llms-full.txt#supported-event-types

<Tabs>
  <Tab title="Session events">
    Some of these events are named differently from the matching events on the session's [event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming). For example, the stream's `session.status_idle` and `session.status_running` correspond to the `session.status_idled` and `session.status_run_started` webhook events.

    | Event                              | Trigger                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
    | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `session.status_run_started`       | Agent execution started. This triggers at every session status transition to `running`.                                                                                                                                                                                                                                                                                                                                                                                                  |
    | `session.status_idled`             | Agent awaiting input, for example, a tool permission approval or a new user message.                                                                                                                                                                                                                                                                                                                                                                                                     |
    | `session.budget_reached`           | The session reached its [budget](https://platform.claude.com/docs/en/managed-agents/budgets) and paused. Fires at most once for each budget value you set; changing the budget arms it again.                                                                                                                                                                                                                                                                                            |
    | `session.status_rescheduled`       | A transient error occurred and the session is retrying automatically.                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | `session.status_terminated`        | The session terminated, either because of an unrecoverable error or because it was archived.                                                                                                                                                                                                                                                                                                                                                                                             |
    | `session.thread_created`           | New [multiagent thread](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration) opened: an additional agent called by the coordinator is starting work, or the session's [advisor](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration#give-the-session-an-advisor) is being consulted.                                                                                                                                                     |
    | `session.thread_idled`             | An agent in a [multiagent interaction](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration) is waiting for input.                                                                                                                                                                                                                                                                                                                                                |
    | `session.thread_terminated`        | A [multiagent thread](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration) terminated, either because the thread was archived or because it exhausted its retries. A coordinator-spawned child that finishes its work goes `idle`, not `terminated` (an advisor thread terminates once its consultation completes). Fires for child threads only; the primary thread's end, including archiving the whole session, surfaces only as `session.status_terminated`. |
    | `session.outcome_evaluation_ended` | [Outcome evaluation](https://platform.claude.com/docs/en/managed-agents/define-outcomes) for a single iteration completed.                                                                                                                                                                                                                                                                                                                                                               |
    | `session.updated`                  | Session properties changed (for example, its name or configuration was updated).                                                                                                                                                                                                                                                                                                                                                                                                         |
    | `session.deleted`                  | Session permanently deleted. There is no object left to fetch, so treat the event itself as final.                                                                                                                                                                                                                                                                                                                                                                                       |
  </Tab>

  <Tab title="Vault events">
    | Event                             | Trigger                                                                                                                                                                 |
    | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `vault.created`                   | Vault created.                                                                                                                                                          |
    | `vault.archived`                  | Vault archived. A `vault_credential.archived` event is also emitted for each underlying credential.                                                                     |
    | `vault.deleted`                   | Vault deleted. A `vault_credential.deleted` event is also emitted for each underlying credential. There is no object left to fetch, so treat the event itself as final. |
    | `vault_credential.created`        | Credential created.                                                                                                                                                     |
    | `vault_credential.archived`       | Credential archived, either directly or as a result of vault archival.                                                                                                  |
    | `vault_credential.deleted`        | Credential deleted, either directly or as a result of vault deletion. There is no object left to fetch, so treat the event itself as final.                             |
    | `vault_credential.refresh_failed` | An `mcp_oauth` credential cannot be refreshed (invalid refresh token, or irrecoverable error from the OAuth server).                                                    |
  </Tab>

  <Tab title="Agent events">
    These events track the lifecycle of the agent resources in your workspace, and are distinct from the agent events delivered on a session's event stream.

    | Event            | Trigger                                                                                                                                                                                         |
    | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `agent.created`  | Agent created.                                                                                                                                                                                  |
    | `agent.updated`  | A [new version of the agent](https://platform.claude.com/docs/en/managed-agents/agent-setup#update-an-agent) was published. Updates that do not create a new version do not trigger this event. |
    | `agent.archived` | Agent archived.                                                                                                                                                                                 |
    | `agent.deleted`  | Agent permanently deleted. There is no object left to fetch, so treat the event itself as final.                                                                                                |
  </Tab>

  <Tab title="Deployment events">
    | Event                 | Trigger                                                                                                                                                                                                                                                                                                                                                            |
    | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
    | `deployment.created`  | [Scheduled deployment](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments) created.                                                                                                                                                                                                                                                          |
    | `deployment.updated`  | Deployment properties changed (for example, its schedule was updated).                                                                                                                                                                                                                                                                                             |
    | `deployment.paused`   | Deployment paused, either by request or automatically when a scheduled run fails with an unrecoverable error, such as an archived subagent or an archived environment. Recoverable failures, including rate limits, don't pause the deployment. See [Failure behavior](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments#failure-behavior). |
    | `deployment.unpaused` | Deployment unpaused, resuming its schedule.                                                                                                                                                                                                                                                                                                                        |
    | `deployment.archived` | Deployment archived, either directly or because its agent was archived. If the agent is deleted instead, a scheduled deployment is archived at its next scheduled run; a deployment without a schedule is not archived automatically.                                                                                                                              |
    | `deployment.deleted`  | Deployment permanently deleted. There is no object left to fetch, so treat the event itself as final.                                                                                                                                                                                                                                                              |
  </Tab>

  <Tab title="Deployment run events">
    | Event                      | Trigger                                                                                                                                                                                                                                                                                                                                                                   |
    | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `deployment_run.started`   | A scheduled run started. Only scheduled runs emit `deployment_run` events; [manual runs](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments#trigger-a-manual-run) do not.                                                                                                                                                                           |
    | `deployment_run.succeeded` | A scheduled run created its session. The event carries the same `data.id` (the run ID) as the run's `deployment_run.started` event. To follow the session's work, subscribe to its session events (the Session events tab), or fetch the [deployment run](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments#deployment-runs) for its `session_id`. |
    | `deployment_run.failed`    | A scheduled run did not create a session. The event carries the same `data.id` as the run's `deployment_run.started` event. Fetch the [deployment run](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments#deployment-runs) for the error details.                                                                                                   |
  </Tab>

  <Tab title="Environment events">
    | Event                  | Trigger                                                                                                                                         |
    | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
    | `environment.created`  | Environment created.                                                                                                                            |
    | `environment.updated`  | Environment updated with at least one changed field. A no-op update emits nothing.                                                              |
    | `environment.archived` | Environment archived. Re-archiving an already-archived environment emits nothing.                                                               |
    | `environment.deleted`  | Environment deleted, including delete of an already-archived environment. There is no object left to fetch, so treat the event itself as final. |

    An environment's [work items](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) emit no webhook events.
  </Tab>

  <Tab title="Memory store events">
    | Event                   | Trigger                                                                                                                                                                                                                                                                                             |
    | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `memory_store.created`  | Memory store created, either by you or by an Anthropic-operated process that clones one of your existing stores.                                                                                                                                                                                    |
    | `memory_store.archived` | Memory store archived. Re-archiving an already-archived store emits nothing.                                                                                                                                                                                                                        |
    | `memory_store.deleted`  | Memory store deleted, including delete of an already-archived store. Deleting a store cascades to its memories and memory versions without emitting per-memory events; the single `memory_store.deleted` event is the signal. There is no object left to fetch, so treat the event itself as final. |

    Individual [memories](https://platform.claude.com/docs/en/managed-agents/memory) and memory versions emit no webhook events.
  </Tab>
</Tabs>


## Register an endpoint

Source: https://platform.claude.com/llms-full.txt#register-an-endpoint

Visit **Manage > Webhooks** in the [Claude Console](https://platform.claude.com/settings/workspaces/default/webhooks).

A webhook endpoint consists of:

* **URL:** Must be HTTPS on port 443 with a publicly resolvable hostname.
* **Event types:** The list of `data.type` values this endpoint receives. An endpoint only receives events it's subscribed to.
* **Signing secret:** A 32-byte `whsec_`-prefixed secret generated at creation. It's shown only once, so store it securely to verify webhook deliveries.


## Verify the signature

Source: https://platform.claude.com/llms-full.txt#verify-the-signature

Every delivery carries the `webhook-id`, `webhook-timestamp`, and `webhook-signature` headers. Use the SDK's `unwrap()` helper to verify the signature and parse the event in one step. It throws if the signature is invalid or the payload is more than 5 minutes old.

Set `ANTHROPIC_WEBHOOK_SIGNING_KEY` to the `whsec_`-prefixed secret shown at endpoint creation.

<CodeGroup>
  ```python Python
  from flask import Flask, request
  import anthropic

  client = anthropic.Anthropic()  # reads ANTHROPIC_WEBHOOK_SIGNING_KEY from env
  app = Flask(__name__)


  @app.route("/webhook", methods=["POST"])
  def webhook():
      try:
          # unwrap() raises if the signature is invalid or the payload is stale
          event = client.beta.webhooks.unwrap(
              request.get_data(as_text=True),
              headers=dict(request.headers),
          )
      except Exception:
          return "invalid signature", 400

      if event.data.type == "session.status_idled":
          print("session idled:", event.data.id)
      # handle other event types

      return "", 200

typescript TypeScript
  import express from "express";
  import Anthropic from "@anthropic-ai/sdk";

  const client = new Anthropic(); // reads ANTHROPIC_WEBHOOK_SIGNING_KEY from env
  const app = express();

  // IMPORTANT: use express.raw(), not express.json(). The signature is computed over raw bytes.
  app.post("/webhook", express.raw({ type: "application/json" }), (req, res) => {
    let event;
    try {
      // unwrap() throws if the signature is invalid or the payload is stale
      event = client.beta.webhooks.unwrap(req.body.toString("utf8"), {
        headers: req.headers as Record<string, string>
      });
    } catch {
      return res.status(400).send("invalid signature");
    }

    switch (event.data.type) {
      case "session.status_idled":
        console.log("session idled:", event.data.id);
        break;
      // handle other event types
    }

    res.sendStatus(200);
  });

csharp C#
  using Anthropic;

  var client = new AnthropicClient(); // reads ANTHROPIC_WEBHOOK_SIGNING_KEY from env
  var app = WebApplication.Create(args);

  app.MapPost("/webhook", async (HttpRequest request) =>
  {
      using var reader = new StreamReader(request.Body);
      var body = await reader.ReadToEndAsync();
      var headers = request.Headers.ToDictionary(header => header.Key, header => header.Value.ToString());

      UnwrapWebhookEvent webhookEvent;
      try
      {
          // Unwrap() throws if the signature is invalid or the payload is stale
          webhookEvent = client.Beta.Webhooks.Unwrap(body, headers);
      }
      catch
      {
          return Results.BadRequest("invalid signature");
      }

      if (webhookEvent.Data.TryPickSessionStatusIdled(out var idled))
      {
          Console.WriteLine($"session idled: {idled.ID}");
      }
      // handle other event types

      return Results.Ok();
  });

go Go
  package main

  import (
  	"fmt"
  	"io"
  	"net/http"

  	"github.com/anthropics/anthropic-sdk-go"
  )

  var client = anthropic.NewClient() // reads ANTHROPIC_WEBHOOK_SIGNING_KEY from env

  func webhook(w http.ResponseWriter, r *http.Request) {
  	body, err := io.ReadAll(r.Body)
  	if err != nil {
  		http.Error(w, "could not read body", http.StatusBadRequest)
  		return
  	}

  	// Unwrap returns an error if the signature is invalid or the payload is stale
  	event, err := client.Beta.Webhooks.Unwrap(body, r.Header)
  	if err != nil {
  		http.Error(w, "invalid signature", http.StatusBadRequest)
  		return
  	}

  	switch event.Data.Type {
  	case "session.status_idled":
  		fmt.Println("session idled:", event.Data.ID)
  		// handle other event types
  	}

  	w.WriteHeader(http.StatusOK)
  }

  func main() {
  	http.HandleFunc("/webhook", webhook)
  }

java Java
  import com.anthropic.client.AnthropicClient;
  import com.anthropic.client.okhttp.AnthropicOkHttpClient;
  import com.anthropic.core.UnwrapWebhookParams;
  import com.anthropic.core.http.Headers;
  import com.sun.net.httpserver.HttpServer;

  // reads ANTHROPIC_WEBHOOK_SIGNING_KEY from env
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  void main() throws Exception {
      var server = HttpServer.create(new InetSocketAddress(8000), 0);
      server.createContext("/webhook", exchange -> {
          var body = new String(exchange.getRequestBody().readAllBytes());
          var headers = Headers.builder();
          exchange.getRequestHeaders().forEach(headers::put);

          try {
              // unwrap() throws if the signature is invalid or the payload is stale
              var event = client.beta().webhooks().unwrap(
                  UnwrapWebhookParams.builder()
                      .body(body)
                      .headers(headers.build())
                      .build());

              event.data().sessionStatusIdled().ifPresent(idled ->
                  IO.println("session idled: " + idled.id()));
              // handle other event types

              exchange.sendResponseHeaders(200, -1);
          } catch (Exception _) {
              exchange.sendResponseHeaders(400, -1);
          }
          exchange.close();
      });
  }

php PHP
  use Anthropic\Client;
  use Anthropic\Core\Exceptions\WebhookException;

  $client = new Client(); // reads ANTHROPIC_WEBHOOK_SIGNING_KEY from env

  $body = file_get_contents('php://input');
  $headers = getallheaders();

  try {
      // unwrap() throws if the signature is invalid or the payload is stale
      $event = $client->beta->webhooks->unwrap($body, headers: $headers);
  } catch (WebhookException) {
      http_response_code(400);
      exit('invalid signature');
  }

  match ($event->data->type) {
      'session.status_idled' => print "session idled: {$event->data->id}\n",
      // handle other event types
      default => null,
  };

  http_response_code(200);

ruby Ruby
  require "sinatra"
  require "anthropic"

  client = Anthropic::Client.new # reads ANTHROPIC_WEBHOOK_SIGNING_KEY from env

  post "/webhook" do
    headers = request.env
      .select { |key, _| key.start_with?("HTTP_") }
      .transform_keys { it.delete_prefix("HTTP_").downcase.tr("_", "-") }

    begin
      # unwrap raises if the signature is invalid or the payload is stale
      event = client.beta.webhooks.unwrap(request.body.read, headers: headers)
    rescue StandardError
      halt 400, "invalid signature"
    end

    if event.data.type == :"session.status_idled"
      puts "session idled: #{event.data.id}"
    end
    # handle other event types

    status 200
  end
  ```
</CodeGroup>


## Handle an event

Source: https://platform.claude.com/llms-full.txt#handle-an-event

Parse the body, switch on `data.type`, and fetch the resource by ID. Return any `2xx` to acknowledge. Any other response counts against the endpoint: a `3xx` disables it immediately (redirects are never followed), while other failures are retried; see [Delivery behavior](https://platform.claude.com/docs/en/managed-agents/webhooks#delivery-behavior) for the retry and auto-disable rules.

Every event payload has the same structure, including the event type, identifier, and the timestamp of when the event occurred.

<CodeGroup>
  ```python Python
  if event.data.type == "session.status_idled":
      session = client.beta.sessions.retrieve(event.data.id)
      notify_user(session)
  return "", 204

typescript TypeScript
  if (event.data.type === "session.status_idled") {
    const session = await client.beta.sessions.retrieve(event.data.id);
    notifyUser(session);
  }
  res.sendStatus(204);

csharp C#
  if (webhookEvent.Data.TryPickSessionStatusIdled(out var idled))
  {
      var session = await client.Beta.Sessions.Retrieve(idled.ID);
      NotifyUser(session);
  }
  return Results.StatusCode(204);

go Go
  if event.Data.Type == "session.status_idled" {
  	session, err := client.Beta.Sessions.Get(r.Context(), event.Data.ID, anthropic.BetaSessionGetParams{})
  	if err != nil {
  		panic(err)
  	}
  	notifyUser(session)
  }
  w.WriteHeader(http.StatusNoContent)

java Java
  event.data().sessionStatusIdled().ifPresent(idled -> {
      var session = client.beta().sessions().retrieve(idled.id());
      notifyUser(session);
  });
  exchange.sendResponseHeaders(204, -1);

php PHP
  if ($event->data->type === 'session.status_idled') {
      $session = $client->beta->sessions->retrieve($event->data->id);
      notifyUser($session);
  }
  http_response_code(204);

ruby Ruby
  if event.data.type == :"session.status_idled"
    session = client.beta.sessions.retrieve(event.data.id)
    notify_user(session)
  end
  status 204
  ```
</CodeGroup>

The top-level `event.id` is unique per event, not per delivery. If you receive the same `event.id` twice, it's a retry and you can discard it.


## Delivery behavior

Source: https://platform.claude.com/llms-full.txt#delivery-behavior

* **Duplicates:** An endpoint can receive the same event more than once, and every attempt delivers the same top-level `event.id` (the same value as the `webhook-id` header). Deduplicate on it.

* **Subscription scope:** An event is delivered only to endpoints subscribed to its type at the moment it's emitted. An event emitted while no endpoint is subscribed to its type is never delivered, and subscribing later doesn't backfill it, so subscribe to an event type before you need it.

* **Ordering is not guaranteed.** Events aren't delivered in the order they occurred: `session.status_idled` might arrive before `session.outcome_evaluation_ended` even if the outcome was produced first, and a `.deleted` event can arrive before the `.archived` event for the same resource. Drive your state from the resource you fetch, not from the order events arrive in.

* **Retries:** For each endpoint and event, Anthropic makes up to three delivery attempts (a response that triggers auto-disable, described later in this section, is never retried) with jittered exponential backoff between 5 and 120 seconds. Every attempt delivers the same `event.id`. After the last attempt fails, the event is dropped: it isn't queued for later delivery and there's no signal that it was lost. Webhooks aren't a durable log, so if you need to observe every transition, reconcile by listing or fetching the resource through the API.

* **Timestamps:** The `webhook-timestamp` header is stamped when a delivery attempt is signed and is regenerated on every retry, so retries aren't rejected by the SDK's freshness check. It's the clock for the delivery attempt, not for the event: use the event payload's `created_at` for when the event occurred.

* **Auto-disable:** An endpoint is automatically set to `disabled` with a machine-readable `disabled_reason` in three cases:

  * The endpoint returns a `3xx` response. Redirects are never followed; this disables the endpoint immediately, on the first attempt, with the reason `auto-disabled: endpoint URL returned a redirect (3xx)`. If your endpoint moves, update the URL in Console and re-enable the endpoint.
  * The endpoint's URL resolves to a non-public IP address when Anthropic connects. This disables the endpoint immediately, with the reason `auto-disabled: endpoint URL resolved to an invalid address`.
  * Deliveries to the endpoint fail continuously for a sustained period, with the reason `auto-disabled after sustained delivery failures`. The trigger is how long the endpoint has been failing without interruption, not a delivery count. A single `2xx` resets the window, so one flaky event can't disable the endpoint.

  All three are reversible: re-enable the endpoint in Console after you resolve the issue. Events emitted while the endpoint was disabled aren't replayed.


### Manage agent context

---
title: Accessing GitHub
url: https://platform.claude.com/docs/en/managed-agents/github
description: Connect your agent to GitHub repositories for cloning, reading, and creating pull requests.
---

You can mount a GitHub repository to your session sandbox and connect to the GitHub MCP for making pull requests.

GitHub repositories are cached, so future sessions that use the same repository start faster.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## GitHub MCP and session resources

Source: https://platform.claude.com/llms-full.txt#github-mcp-and-session-resources

First, create an agent that declares the GitHub MCP server. The agent definition holds the server URL but no authentication token:

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  agent_id=$(curl -fsS https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    --data @- <<JSON | jq -r '.id'
  {
    "name": "Code Reviewer",
    "model": "claude-opus-5",
    "system": "You are a code review assistant with access to GitHub.",
    "mcp_servers": [
      {
        "type": "url",
        "name": "github",
        "url": "https://api.githubcopilot.com/mcp/"
      }
    ],
    "tools": [
      {"type": "agent_toolset_20260401"},
      {
        "type": "mcp_toolset",
        "mcp_server_name": "github"
      }
    ]
  }
  JSON
  )

bash CLI
    AGENT_ID=$(ant beta:agents create --transform id --raw-output < code-reviewer.agent.yaml)

yaml
      name: Code Reviewer
      model:
        id: claude-opus-5
      system: You are a code review assistant with access to GitHub.
      mcp_servers:
        - type: url
          name: github
          url: https://api.githubcopilot.com/mcp/
      tools:
        - type: agent_toolset_20260401
        - type: mcp_toolset
          mcp_server_name: github

python Python
  agent = client.beta.agents.create(
      name="Code Reviewer",
      model="claude-opus-5",
      system="You are a code review assistant with access to GitHub.",
      mcp_servers=[
          {
              "type": "url",
              "name": "github",
              "url": "https://api.githubcopilot.com/mcp/",
          },
      ],
      tools=[
          {"type": "agent_toolset_20260401"},
          {
              "type": "mcp_toolset",
              "mcp_server_name": "github",
          },
      ],
  )

typescript TypeScript
  const agent = await client.beta.agents.create({
    name: "Code Reviewer",
    model: "claude-opus-5",
    system: "You are a code review assistant with access to GitHub.",
    mcp_servers: [
      {
        type: "url",
        name: "github",
        url: "https://api.githubcopilot.com/mcp/",
      },
    ],
    tools: [
      { type: "agent_toolset_20260401" },
      {
        type: "mcp_toolset",
        mcp_server_name: "github",
      },
    ],
  });

csharp C#
  var agent = await client.Beta.Agents.Create(new()
  {
      Name = "Code Reviewer",
      Model = BetaManagedAgentsModel.ClaudeOpus5,
      System = "You are a code review assistant with access to GitHub.",
      McpServers =
      [
          new() { Type = "url", Name = "github", Url = "https://api.githubcopilot.com/mcp/" },
      ],
      Tools =
      [
          new BetaManagedAgentsAgentToolset20260401Params
          {
              Type = "agent_toolset_20260401",
          },
          new BetaManagedAgentsMcpToolsetParams
          {
              Type = "mcp_toolset",
              McpServerName = "github",
          },
      ],
  });

go Go
  agent, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name: "Code Reviewer",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{
  		ID: anthropic.BetaManagedAgentsModelClaudeOpus5,
  	},
  	System: anthropic.String("You are a code review assistant with access to GitHub."),
  	MCPServers: []anthropic.BetaManagedAgentsURLMCPServerParams{
  		{
  			Type: anthropic.BetaManagedAgentsURLMCPServerParamsTypeURL,
  			Name: "github",
  			URL:  "https://api.githubcopilot.com/mcp/",
  		},
  	},
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{
  		{
  			OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  				Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  			},
  		},
  		{
  			OfMCPToolset: &anthropic.BetaManagedAgentsMCPToolsetParams{
  				Type:          anthropic.BetaManagedAgentsMCPToolsetParamsTypeMCPToolset,
  				MCPServerName: "github",
  			},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  var agent = client.beta().agents().create(AgentCreateParams.builder()
      .name("Code Reviewer")
      .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
      .system("You are a code review assistant with access to GitHub.")
      .addMcpServer(BetaManagedAgentsUrlMcpServerParams.builder()
          .type(BetaManagedAgentsUrlMcpServerParams.Type.URL)
          .name("github")
          .url("https://api.githubcopilot.com/mcp/")
          .build())
      .addTool(BetaManagedAgentsAgentToolset20260401Params.builder()
          .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
          .build())
      .addTool(BetaManagedAgentsMcpToolsetParams.builder()
          .type(BetaManagedAgentsMcpToolsetParams.Type.MCP_TOOLSET)
          .mcpServerName("github")
          .build())
      .build());

php PHP
  $agent = $client->beta->agents->create(
      name: 'Code Reviewer',
      model: 'claude-opus-5',
      system: 'You are a code review assistant with access to GitHub.',
      mcpServers: [
          [
              'type' => 'url',
              'name' => 'github',
              'url' => 'https://api.githubcopilot.com/mcp/',
          ],
      ],
      tools: [
          ['type' => 'agent_toolset_20260401'],
          [
              'type' => 'mcp_toolset',
              'mcpServerName' => 'github',
          ],
      ],
  );

ruby Ruby
  agent = client.beta.agents.create(
    name: "Code Reviewer",
    model: "claude-opus-5",
    system_: "You are a code review assistant with access to GitHub.",
    mcp_servers: [
      {
        type: "url",
        name: "github",
        url: "https://api.githubcopilot.com/mcp/"
      }
    ],
    tools: [
      {type: "agent_toolset_20260401"},
      {
        type: "mcp_toolset",
        mcp_server_name: "github"
      }
    ]
  )

bash cURL
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

A `github_repository` resource accepts the following fields:

| Field                 | Description                                                                                                                                                                                       |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                | Required. Must be `"github_repository"`.                                                                                                                                                          |
| `url`                 | Required. The repository's HTTPS URL in the form `https://github.com/<owner>/<repo>`, without a `.git` suffix. Other forms, including SSH URLs, are rejected with an `invalid_request_error`.     |
| `authorization_token` | Required. The GitHub token used to clone the repository. It is not echoed in API responses. See [Token permissions](https://platform.claude.com/docs/en/managed-agents/github#token-permissions). |
| `mount_path`          | Optional. The directory under `/workspace` to clone the repository into. Defaults to `/workspace/<repo-name>`.                                                                                    |
| `checkout`            | Optional. A branch (`{"type": "branch", "name": "main"}`) or commit (`{"type": "commit", "sha": "..."}`) to check out. Defaults to the repository's default branch.                               |

Mounting a repository also loads any skills stored in its root `.claude/skills` directory. Skills are discovered once per session, from the repository state checked out at session start. See [Load skills from a GitHub repository](https://platform.claude.com/docs/en/managed-agents/skills#load-skills-from-a-github-repository).


## Token permissions

Source: https://platform.claude.com/llms-full.txt#token-permissions

When providing a GitHub token, use the minimum required permissions:

| Action              | Required scopes                   |
| ------------------- | --------------------------------- |
| Clone private repos | `repo`                            |
| Create PRs          | `repo`                            |
| Read issues         | `repo` (private) or `public_repo` |
| Create issues       | `repo` (private) or `public_repo` |

<Warning>
  Use fine-grained personal access tokens with minimum required permissions. Avoid using tokens with broad access to your GitHub account.
</Warning>


## Multiple repositories

Source: https://platform.claude.com/llms-full.txt#multiple-repositories

Mount multiple repositories by adding entries to the `resources` array:

<CodeGroup>
  ```bash cURL
  resources='[
    {
      "type": "github_repository",
      "url": "https://github.com/org/frontend",
      "mount_path": "/workspace/frontend",
      "authorization_token": "ghp_your_github_token"
    },
    {
      "type": "github_repository",
      "url": "https://github.com/org/backend",
      "mount_path": "/workspace/backend",
      "authorization_token": "ghp_your_github_token"
    }
  ]'

bash CLI
  RESOURCES_BODY=$(cat <<'EOF'
  resources:
    - type: github_repository
      url: https://github.com/org/frontend
      mount_path: /workspace/frontend
      authorization_token: ghp_your_github_token
    - type: github_repository
      url: https://github.com/org/backend
      mount_path: /workspace/backend
      authorization_token: ghp_your_github_token
  EOF
  )

python Python
  resources = [
      {
          "type": "github_repository",
          "url": "https://github.com/org/frontend",
          "mount_path": "/workspace/frontend",
          "authorization_token": "ghp_your_github_token",
      },
      {
          "type": "github_repository",
          "url": "https://github.com/org/backend",
          "mount_path": "/workspace/backend",
          "authorization_token": "ghp_your_github_token",
      },
  ]

typescript TypeScript
  const resources = [
    {
      type: "github_repository",
      url: "https://github.com/org/frontend",
      mount_path: "/workspace/frontend",
      authorization_token: "ghp_your_github_token",
    },
    {
      type: "github_repository",
      url: "https://github.com/org/backend",
      mount_path: "/workspace/backend",
      authorization_token: "ghp_your_github_token",
    },
  ];

csharp C#
  BetaManagedAgentsGitHubRepositoryResourceParams[] resources =
  [
      new()
      {
          Type = "github_repository",
          Url = "https://github.com/org/frontend",
          MountPath = "/workspace/frontend",
          AuthorizationToken = "ghp_your_github_token",
      },
      new()
      {
          Type = "github_repository",
          Url = "https://github.com/org/backend",
          MountPath = "/workspace/backend",
          AuthorizationToken = "ghp_your_github_token",
      },
  ];

go Go
  resources := []anthropic.BetaSessionNewParamsResourceUnion{
  	{
  		OfGitHubRepository: &anthropic.BetaManagedAgentsGitHubRepositoryResourceParams{
  			Type:               anthropic.BetaManagedAgentsGitHubRepositoryResourceParamsTypeGitHubRepository,
  			URL:                "https://github.com/org/frontend",
  			MountPath:          anthropic.String("/workspace/frontend"),
  			AuthorizationToken: "ghp_your_github_token",
  		},
  	},
  	{
  		OfGitHubRepository: &anthropic.BetaManagedAgentsGitHubRepositoryResourceParams{
  			Type:               anthropic.BetaManagedAgentsGitHubRepositoryResourceParamsTypeGitHubRepository,
  			URL:                "https://github.com/org/backend",
  			MountPath:          anthropic.String("/workspace/backend"),
  			AuthorizationToken: "ghp_your_github_token",
  		},
  	},
  }

java Java
  var resources = List.of(
      BetaManagedAgentsGitHubRepositoryResourceParams.builder()
          .type(BetaManagedAgentsGitHubRepositoryResourceParams.Type.GITHUB_REPOSITORY)
          .url("https://github.com/org/frontend")
          .mountPath("/workspace/frontend")
          .authorizationToken("ghp_your_github_token")
          .build(),
      BetaManagedAgentsGitHubRepositoryResourceParams.builder()
          .type(BetaManagedAgentsGitHubRepositoryResourceParams.Type.GITHUB_REPOSITORY)
          .url("https://github.com/org/backend")
          .mountPath("/workspace/backend")
          .authorizationToken("ghp_your_github_token")
          .build());

php PHP
  $resources = [
      [
          'type' => 'github_repository',
          'url' => 'https://github.com/org/frontend',
          'mountPath' => '/workspace/frontend',
          'authorizationToken' => 'ghp_your_github_token',
      ],
      [
          'type' => 'github_repository',
          'url' => 'https://github.com/org/backend',
          'mountPath' => '/workspace/backend',
          'authorizationToken' => 'ghp_your_github_token',
      ],
  ];

ruby Ruby
  resources = [
    {
      type: "github_repository",
      url: "https://github.com/org/frontend",
      mount_path: "/workspace/frontend",
      authorization_token: "ghp_your_github_token"
    },
    {
      type: "github_repository",
      url: "https://github.com/org/backend",
      mount_path: "/workspace/backend",
      authorization_token: "ghp_your_github_token"
    }
  ]
  ```
</CodeGroup>


## Managing repositories on a running session

Source: https://platform.claude.com/llms-full.txt#managing-repositories-on-a-running-session

After a session is created, you can list its repository resources and rotate their authorization tokens. Each resource has an `id` returned at session creation time (or through `resources.list`) that you use for updates. Repositories are attached for the lifetime of the session; to change which repositories are mounted, create a new session.

<CodeGroup>
  ```bash cURL
  # List resources on the session
  repo_resource_id=$(curl -fsS "https://api.anthropic.com/v1/sessions/$session_id/resources" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" | jq -r '.data[0].id')
  echo "$repo_resource_id"  # "sesrsc_01ABC..."

  # Rotate the authorization token
  curl -fsS "https://api.anthropic.com/v1/sessions/$session_id/resources/$repo_resource_id" \
  # ...
    -o /dev/null \
    --data @- <<JSON
  {
    "authorization_token": "ghp_your_new_github_token"
  }
  JSON

bash CLI
  # List resources on the session
  ant beta:sessions:resources list --session-id "$SESSION_ID"

  # Rotate the authorization token on a specific resource
  ant beta:sessions:resources update \
    --session-id "$SESSION_ID" \
    --resource-id "$RESOURCE_ID" \
    --authorization-token "ghp_your_new_github_token"

python Python
  # List resources on the session
  listed = client.beta.sessions.resources.list(session.id)
  repo_resource_id = listed.data[0].id
  print(repo_resource_id)  # "sesrsc_01ABC..."

  # Rotate the authorization token
  client.beta.sessions.resources.update(
      repo_resource_id,
      session_id=session.id,
      authorization_token="ghp_your_new_github_token",
  )

typescript TypeScript
  // List resources on the session
  const listed = await client.beta.sessions.resources.list(session.id);
  const repoResource = listed.data.find(
    (entry) => entry.type === "github_repository",
  );
  if (!repoResource) {
    throw new Error("No GitHub repository resource on the session");
  }
  const repoResourceId = repoResource.id;
  console.log(repoResourceId); // "sesrsc_01ABC..."

  // Rotate the authorization token
  await client.beta.sessions.resources.update(repoResourceId, {
    session_id: session.id,
    authorization_token: "ghp_your_new_github_token",
  });

csharp C#
  // List resources on the session
  var listed = await client.Beta.Sessions.Resources.List(session.ID);
  var repoResourceId = (await listed.Paginate().FirstAsync()).ID;
  Console.WriteLine(repoResourceId); // "sesrsc_01ABC..."

  // Rotate the authorization token
  await client.Beta.Sessions.Resources.Update(repoResourceId, new()
  {
      SessionID = session.ID,
      AuthorizationToken = "ghp_your_new_github_token",
  });

go Go
  // List resources on the session
  listed, err := client.Beta.Sessions.Resources.List(ctx, session.ID, anthropic.BetaSessionResourceListParams{})
  if err != nil {
  	panic(err)
  }
  repoResourceID := listed.Data[0].ID
  fmt.Println(repoResourceID) // "sesrsc_01ABC..."

  // Rotate the authorization token
  _, err = client.Beta.Sessions.Resources.Update(ctx, repoResourceID, anthropic.BetaSessionResourceUpdateParams{
  	SessionID:          session.ID,
  	AuthorizationToken: "ghp_your_new_github_token",
  })
  if err != nil {
  	panic(err)
  }

java Java
  // List resources on the session
  var listed = client.beta().sessions().resources().list(session.id());
  var repoResourceId = listed.data().getFirst().asGitHubRepository().id();
  IO.println(repoResourceId);  // "sesrsc_01ABC..."

  // Rotate the authorization token
  client.beta().sessions().resources().update(repoResourceId, ResourceUpdateParams.builder()
      .sessionId(session.id())
      .authorizationToken("ghp_your_new_github_token")
      .build());

php PHP
  // List resources on the session
  $listed = $client->beta->sessions->resources->list($session->id);
  $repoResourceId = $listed->data[0]->id;
  echo $repoResourceId, PHP_EOL; // "sesrsc_01ABC..."

  // Rotate the authorization token
  $client->beta->sessions->resources->update(
      $repoResourceId,
      sessionID: $session->id,
      authorizationToken: 'ghp_your_new_github_token',
  );

ruby Ruby
  # List resources on the session
  listed = client.beta.sessions.resources.list(session.id)
  repo_resource_id = listed.data.first.id
  puts repo_resource_id # "sesrsc_01ABC..."

  # Rotate the authorization token
  client.beta.sessions.resources.update(
    repo_resource_id,
    session_id: session.id,
    authorization_token: "ghp_your_new_github_token"
  )
  ```
</CodeGroup>


## Creating pull requests

Source: https://platform.claude.com/llms-full.txt#creating-pull-requests

With the GitHub MCP server, the agent can create branches, commit changes, and push them:

<CodeGroup>
  ```bash cURL
  curl -fsS "https://api.anthropic.com/v1/sessions/$session_id/events" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -o /dev/null \
    --data @- <<JSON
  {
    "events": [
      {
        "type": "user.message",
        "content": [
          {
            "type": "text",
            "text": "Fix the type error in src/utils.ts, commit it to a new branch, and push it."
          }
        ]
      }
    ]
  }
  JSON

bash CLI
  ant beta:sessions:events send --session-id "$SESSION_ID" > /dev/null <<'EOF'
  events:
    - type: user.message
      content:
        - type: text
          text: Fix the type error in src/utils.ts, commit it to a new branch, and push it.
  EOF

python Python
  client.beta.sessions.events.send(
      session.id,
      events=[
          {
              "type": "user.message",
              "content": [
                  {
                      "type": "text",
                      "text": "Fix the type error in src/utils.ts, commit it to a new branch, and push it.",
                  },
              ],
          },
      ],
  )

typescript TypeScript
  await client.beta.sessions.events.send(session.id, {
    events: [
      {
        type: "user.message",
        content: [
          {
            type: "text",
            text: "Fix the type error in src/utils.ts, commit it to a new branch, and push it.",
          },
        ],
      },
    ],
  });

csharp C#
  await client.Beta.Sessions.Events.Send(session.ID, new()
  {
      Events =
      [
          new BetaManagedAgentsUserMessageEventParams
          {
              Type = "user.message",
              Content =
              [
                  new BetaManagedAgentsTextBlock
                  {
                      Type = "text",
                      Text = "Fix the type error in src/utils.ts, commit it to a new branch, and push it.",
                  },
              ],
          },
      ],
  });

go Go
  _, err = client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  	Events: []anthropic.BetaManagedAgentsEventParamsUnion{
  		{
  			OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
  				Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
  				Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{
  					{
  						OfText: &anthropic.BetaManagedAgentsTextBlockParam{
  							Type: anthropic.BetaManagedAgentsTextBlockTypeText,
  							Text: "Fix the type error in src/utils.ts, commit it to a new branch, and push it.",
  						},
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
  client.beta().sessions().events().send(session.id(), EventSendParams.builder()
      .addEvent(BetaManagedAgentsUserMessageEventParams.builder()
          .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
          .addContent(BetaManagedAgentsTextBlock.builder()
              .type(BetaManagedAgentsTextBlock.Type.TEXT)
              .text("Fix the type error in src/utils.ts, commit it to a new branch, and push it.")
              .build())
          .build())
      .build());

php PHP
  $client->beta->sessions->events->send(
      $session->id,
      events: [
          [
              'type' => 'user.message',
              'content' => [
                  [
                      'type' => 'text',
                      'text' => 'Fix the type error in src/utils.ts, commit it to a new branch, and push it.',
                  ],
              ],
          ],
      ],
  );

ruby Ruby
  client.beta.sessions.events.send_(
    session.id,
    events: [
      {
        type: "user.message",
        content: [
          {
            type: "text",
            text: "Fix the type error in src/utils.ts, commit it to a new branch, and push it."
          }
        ]
      }
    ]
  )
  ```
</CodeGroup>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-78

<CardGroup cols={2}>
  <Card title="Session event stream" icon="lightning" href="https://platform.claude.com/docs/en/managed-agents/events-and-streaming">
    Stream events and steer the agent while it opens the pull request
  </Card>

  <Card title="MCP connector" icon="link" href="https://platform.claude.com/docs/en/managed-agents/mcp-connector">
    Connect more MCP servers to give the agent additional tools
  </Card>

  <Card title="Adding files" icon="file" href="https://platform.claude.com/docs/en/managed-agents/files">
    Mount files in the sandbox alongside your repositories
  </Card>
</CardGroup>


---
title: Adding files
url: https://platform.claude.com/docs/en/managed-agents/files
description: Upload files and mount them in your sandbox for reading and processing.
---

You can provide files to your agent by uploading them through the Files API and mounting them in the session's sandbox.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Uploading files

Source: https://platform.claude.com/llms-full.txt#uploading-files

First, upload a file using the [Files API](https://platform.claude.com/docs/en/build-with-claude/files):

<CodeGroup>
  ```bash cURL
  file=$(curl --fail-with-body -sS "${auth[@]}" \
    "${base_url}/files" \
    -F file=@data.csv)
  file_id=$(jq -er '.id' <<<"${file}")
  printf 'File ID: %s\n' "${file_id}"

bash CLI
  FILE_ID=$(ant files upload --file data.csv --transform id --raw-output)

python Python
  file = client.files.upload(file=Path("data.csv"))
  print(f"File ID: {file.id}")

typescript TypeScript
  const file = await client.files.upload({
    file: await toFile(readFile("data.csv"), "data.csv", { type: "text/csv" }),
  });
  console.log(`File ID: ${file.id}`);

csharp C#
  await using var stream = File.OpenRead(csvPath);
  var file = await client.Files.Upload(new() { File = stream });
  Console.WriteLine($"File ID: {file.ID}");

go Go
  csvFile, err := os.Open("data.csv")
  if err != nil {
  	panic(err)
  }
  defer csvFile.Close()

  file, err := client.Files.Upload(ctx, anthropic.FileUploadParams{
  	File: csvFile,
  })
  if err != nil {
  	panic(err)
  }
  fmt.Printf("File ID: %s\n", file.ID)

java Java
  var file = client.files().upload(
      FileUploadParams.builder().file(dataCsv).build()
  );
  IO.println("File ID: " + file.id());

php PHP
  $file = $client->files->upload(
      file: FileParam::fromResource(fopen($csvPath, 'r'), filename: 'data.csv', contentType: 'text/csv'),
  );
  echo "File ID: {$file->id}\n";

ruby Ruby
  file = client.files.upload(file: Pathname(csv_path))
  puts "File ID: #{file.id}"
  ```
</CodeGroup>


## Mounting files in a session

Source: https://platform.claude.com/llms-full.txt#mounting-files-in-a-session

Mount uploaded files into the sandbox by adding them to the `resources` array when creating a session:

<Tip>
  The `mount_path` is optional, but make sure the uploaded file has a descriptive name so the agent can identify it.
</Tip>

<CodeGroup>
  ```bash cURL
  session=$(
    jq -n \
      --arg agent_id "${agent_id}" \
      --arg environment_id "${environment_id}" \
      --arg file_id "${file_id}" \
      '{
        agent: $agent_id,
        environment_id: $environment_id,
        resources: [
          {
            type: "file",
            file_id: $file_id,
            mount_path: "/data.csv"
          }
        ]
      }' | curl --fail-with-body -sS "${auth[@]}" "${base_url}/sessions" --json @-
  )
  session_id=$(jq -er '.id' <<<"${session}")

bash CLI
  SESSION_ID=$(ant beta:sessions create \
    --agent "$AGENT_ID" \
    --environment-id "$ENVIRONMENT_ID" \
    --transform id --raw-output <<EOF
  resources:
    - type: file
      file_id: $FILE_ID
      mount_path: /data.csv
  EOF
  )

python Python
  session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
      resources=[
          {
              "type": "file",
              "file_id": file.id,
              "mount_path": "/data.csv",
          },
      ],
  )

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id,
    resources: [
      {
        type: "file",
        file_id: file.id,
        mount_path: "/data.csv",
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
          new BetaManagedAgentsFileResourceParams
          {
              Type = "file",
              FileID = file.ID,
              MountPath = "/data.csv",
          },
      ],
  });

go Go
  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfString: anthropic.String(agent.ID),
  	},
  	EnvironmentID: environment.ID,
  	Resources: []anthropic.BetaSessionNewParamsResourceUnion{{
  		OfFile: &anthropic.BetaManagedAgentsFileResourceParams{
  			Type:      anthropic.BetaManagedAgentsFileResourceParamsTypeFile,
  			FileID:    file.ID,
  			MountPath: anthropic.String("/data.csv"),
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }

java Java
  var session = client.beta().sessions().create(
      SessionCreateParams.builder()
          .agent(agent.id())
          .environmentId(environment.id())
          .addResource(
              BetaManagedAgentsFileResourceParams.builder()
                  .type(BetaManagedAgentsFileResourceParams.Type.FILE)
                  .fileId(file.id())
                  .mountPath("/data.csv")
                  .build()
          )
          .build()
  );

php PHP
  $session = $client->beta->sessions->create(
      agent: $agent->id,
      environmentID: $environment->id,
      resources: [
          BetaManagedAgentsFileResourceParams::with(
              type: 'file',
              fileID: $file->id,
              mountPath: '/data.csv',
          ),
      ],
  );

ruby Ruby
  session = client.beta.sessions.create(
    agent: agent.id,
    environment_id: environment.id,
    resources: [
      {
        type: "file",
        file_id: file.id,
        mount_path: "/data.csv"
      }
    ]
  )
  ```
</CodeGroup>

With the preceding `mount_path`, the agent reads the file at `/mnt/session/uploads/data.csv` (see [File paths](https://platform.claude.com/docs/en/managed-agents/files#file-paths)).

A new `file_id` is created that references the instance of the file in the session. These copies do not count against your [storage limits](https://platform.claude.com/docs/en/build-with-claude/files).


## Multiple files

Source: https://platform.claude.com/llms-full.txt#multiple-files

Mount multiple files by adding entries to the `resources` array:

<CodeGroup>
  ```json cURL
  "resources": [
    { "type": "file", "file_id": "file_abc123", "mount_path": "/data.csv" },
    { "type": "file", "file_id": "file_def456", "mount_path": "/config.json" },
    { "type": "file", "file_id": "file_ghi789", "mount_path": "/src/main.py" }
  ]

yaml CLI
  resources:
    - type: file
      file_id: file_abc123
      mount_path: /data.csv
    - type: file
      file_id: file_def456
      mount_path: /config.json
    - type: file
      file_id: file_ghi789
      mount_path: /src/main.py

python Python
  resources = [
      {"type": "file", "file_id": "file_abc123", "mount_path": "/data.csv"},
      {"type": "file", "file_id": "file_def456", "mount_path": "/config.json"},
      {"type": "file", "file_id": "file_ghi789", "mount_path": "/src/main.py"},
  ]

typescript TypeScript
  resources: [
    { type: "file", file_id: "file_abc123", mount_path: "/data.csv" },
    { type: "file", file_id: "file_def456", mount_path: "/config.json" },
    { type: "file", file_id: "file_ghi789", mount_path: "/src/main.py" }
  ]

csharp C#
  using Anthropic.Models.Beta.Sessions;

  var resources = new[]
  {
      new BetaManagedAgentsFileResourceParams { Type = BetaManagedAgentsFileResourceParamsType.File, FileID = "file_abc123", MountPath = "/data.csv" },
      new BetaManagedAgentsFileResourceParams { Type = BetaManagedAgentsFileResourceParamsType.File, FileID = "file_def456", MountPath = "/config.json" },
      new BetaManagedAgentsFileResourceParams { Type = BetaManagedAgentsFileResourceParamsType.File, FileID = "file_ghi789", MountPath = "/src/main.py" },
  };

go Go
  resources := []anthropic.BetaSessionNewParamsResourceUnion{
  	{OfFile: &anthropic.BetaManagedAgentsFileResourceParams{Type: "file", FileID: "file_abc123", MountPath: anthropic.String("/data.csv")}},
  	{OfFile: &anthropic.BetaManagedAgentsFileResourceParams{Type: "file", FileID: "file_def456", MountPath: anthropic.String("/config.json")}},
  	{OfFile: &anthropic.BetaManagedAgentsFileResourceParams{Type: "file", FileID: "file_ghi789", MountPath: anthropic.String("/src/main.py")}},
  }

java Java
  import com.anthropic.models.beta.sessions.*;
  import java.util.List;

  var resources = List.of(
      BetaManagedAgentsFileResourceParams.builder()
          .type(BetaManagedAgentsFileResourceParams.Type.FILE).fileId("file_abc123").mountPath("/data.csv").build(),
      BetaManagedAgentsFileResourceParams.builder()
          .type(BetaManagedAgentsFileResourceParams.Type.FILE).fileId("file_def456").mountPath("/config.json").build(),
      BetaManagedAgentsFileResourceParams.builder()
          .type(BetaManagedAgentsFileResourceParams.Type.FILE).fileId("file_ghi789").mountPath("/src/main.py").build()
  );

php PHP
  $resources = [
      ['type' => 'file', 'fileID' => 'file_abc123', 'mountPath' => '/data.csv'],
      ['type' => 'file', 'fileID' => 'file_def456', 'mountPath' => '/config.json'],
      ['type' => 'file', 'fileID' => 'file_ghi789', 'mountPath' => '/src/main.py'],
  ];

ruby Ruby
  resources = [
    {type: "file", file_id: "file_abc123", mount_path: "/data.csv"},
    {type: "file", file_id: "file_def456", mount_path: "/config.json"},
    {type: "file", file_id: "file_ghi789", mount_path: "/src/main.py"}
  ]
  ```
</CodeGroup>

A maximum of 500 files is supported per session.


## Managing files on a running session

Source: https://platform.claude.com/llms-full.txt#managing-files-on-a-running-session

You can add or remove files from a session after creation using the session resources API. Each resource has an `id` returned when it is added (or listed), which you use for deletes.

<CodeGroup>
  ```bash cURL
  resource=$(
    jq -n --arg file_id "${file_id}" '{type: "file", file_id: $file_id}' \
      | curl --fail-with-body -sS "${auth[@]}" \
          "${base_url}/sessions/${session_id}/resources" --json @-
  )
  resource_id=$(jq -er '.id' <<<"${resource}")
  printf '%s\n' "${resource_id}"  # "sesrsc_01ABC..."

bash CLI
  RESOURCE_ID=$(ant beta:sessions:resources add \
    --session-id "$SESSION_ID" \
    --type file \
    --file-id "$FILE_ID" \
    --transform id --raw-output)

python Python
  resource = client.beta.sessions.resources.add(
      session.id,
      type="file",
      file_id=file.id,
  )
  print(resource.id)  # "sesrsc_01ABC..."

typescript TypeScript
  const resource = await client.beta.sessions.resources.add(session.id, {
    type: "file",
    file_id: file.id,
  });
  if (resource.type !== "file") {
    throw new Error(`Unexpected resource type: ${resource.type}`);
  }
  console.log(resource.id); // "sesrsc_01ABC..."

csharp C#
  var resource = await client.Beta.Sessions.Resources.Add(session.ID, new()
  {
      Type = "file",
      FileID = file.ID,
  });
  Console.WriteLine(resource.ID);  // "sesrsc_01ABC..."

go Go
  resource, err := client.Beta.Sessions.Resources.Add(ctx, session.ID, anthropic.BetaSessionResourceAddParams{
  	BetaManagedAgentsFileResourceParams: anthropic.BetaManagedAgentsFileResourceParams{
  		Type:   anthropic.BetaManagedAgentsFileResourceParamsTypeFile,
  		FileID: file.ID,
  	},
  })
  if err != nil {
  	panic(err)
  }
  fmt.Println(resource.ID) // "sesrsc_01ABC..."

java Java
  var resource = client.beta().sessions().resources().add(
      session.id(),
      ResourceAddParams.builder()
          .betaManagedAgentsFileResourceParams(
              BetaManagedAgentsFileResourceParams.builder()
                  .type(BetaManagedAgentsFileResourceParams.Type.FILE)
                  .fileId(file.id())
                  .build()
          )
          .build()
  );
  IO.println(resource.id()); // "sesrsc_01ABC..."

php PHP
  $resource = $client->beta->sessions->resources->add(
      $session->id,
      type: 'file',
      fileID: $file->id,
  );
  echo "{$resource->id}\n";  // "sesrsc_01ABC..."

ruby Ruby
  resource = client.beta.sessions.resources.add(
    session.id,
    type: "file",
    file_id: file.id
  )
  puts resource.id # "sesrsc_01ABC..."

bash cURL
  curl --fail-with-body -sS "${auth[@]}" \
    "${base_url}/sessions/${session_id}/resources" \
    | jq -r '.data[] | "\(.id) \(.type)"'

  curl --fail-with-body -sS "${auth[@]}" -X DELETE \
    "${base_url}/sessions/${session_id}/resources/${resource_id}" >/dev/null

bash CLI
  ant beta:sessions:resources list --session-id "$SESSION_ID"

  ant beta:sessions:resources delete \
    --session-id "$SESSION_ID" \
    --resource-id "$RESOURCE_ID"

python Python
  listed = client.beta.sessions.resources.list(session.id)
  for entry in listed.data:
      print(entry.id, entry.type)

  client.beta.sessions.resources.delete(resource.id, session_id=session.id)

typescript TypeScript
  const listed = await client.beta.sessions.resources.list(session.id);
  for (const entry of listed.data) {
    if (entry.type !== "memory_store") {
      console.log(entry.id, entry.type);
    }
  }

  await client.beta.sessions.resources.delete(resource.id, {
    session_id: session.id,
  });

csharp C#
  var listed = await client.Beta.Sessions.Resources.List(session.ID);
  await foreach (var entry in listed.Paginate())
  {
      var type = entry.Match<string>(repo => repo.Type, fileRes => fileRes.Type, memoryStore => memoryStore.Type);
      Console.WriteLine($"{entry.ID} {type}");
  }

  await client.Beta.Sessions.Resources.Delete(resource.ID, new() { SessionID = session.ID });

go Go
  listed, err := client.Beta.Sessions.Resources.List(ctx, session.ID, anthropic.BetaSessionResourceListParams{})
  if err != nil {
  	panic(err)
  }
  for _, entry := range listed.Data {
  	fmt.Println(entry.ID, entry.Type)
  }

  if _, err := client.Beta.Sessions.Resources.Delete(ctx, resource.ID, anthropic.BetaSessionResourceDeleteParams{
  	SessionID: session.ID,
  }); err != nil {
  	panic(err)
  }

java Java
  var listed = client.beta().sessions().resources().list(session.id());
  for (var entry : listed.data()) {
      if (entry.isFile()) {
          var fileResource = entry.asFile();
          IO.println(fileResource.id() + " " + fileResource.type());
      } else if (entry.isGitHubRepository()) {
          var repoResource = entry.asGitHubRepository();
          IO.println(repoResource.id() + " " + repoResource.type());
      }
  }

  client.beta().sessions().resources().delete(
      resource.id(),
      ResourceDeleteParams.builder().sessionId(session.id()).build()
  );

php PHP
  $listed = $client->beta->sessions->resources->list($session->id);
  foreach ($listed->data as $entry) {
      echo "{$entry->id} {$entry->type}\n";
  }

  $client->beta->sessions->resources->delete($resource->id, sessionID: $session->id);

ruby Ruby
  listed = client.beta.sessions.resources.list(session.id)
  listed.data.each { puts "#{it.id} #{it.type}" }

  client.beta.sessions.resources.delete(resource.id, session_id: session.id)
  ```
</CodeGroup>


## Listing and downloading session files

Source: https://platform.claude.com/llms-full.txt#listing-and-downloading-session-files

Use the [Files API](https://platform.claude.com/docs/en/build-with-claude/files) to list files scoped to a session and download them. Files the agent writes to `/mnt/session/outputs/` appear in the list shortly after the agent finishes writing them, sometimes a few seconds after the session goes idle. If an output file you expect is missing, list again after a short delay; once it appears in the list, its upload has finished.

Filtering by `scope_id` requires the `managed-agents-2026-04-01` beta header, so the list examples use the `beta` files namespace and pass that header explicitly.

<CodeGroup>
  ```bash cURL
  # List files associated with a session
  curl -fsSL "https://api.anthropic.com/v1/files?scope_id=sesn_abc123" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

  # Download a file
  curl -fsSL "https://api.anthropic.com/v1/files/$FILE_ID/content" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -o output.txt

bash CLI
  # List files associated with a session
  ant beta:files list --scope-id sesn_abc123 --beta managed-agents-2026-04-01

  # Download a file
  ant files download --file-id "$FILE_ID" --output output.txt

python Python
  # List files associated with a session
  files = client.beta.files.list(
      scope_id="sesn_abc123",
      betas=["managed-agents-2026-04-01"],
  )
  for file in files:
      print(file.id, file.filename)

  # Download a file
  content = client.files.download(files.data[0].id)
  content.write_to_file("output.txt")

typescript TypeScript
  import { writeFile } from "node:fs/promises";

  // List files associated with a session
  const files = await client.beta.files.list({
    scope_id: "sesn_abc123",
    betas: ["managed-agents-2026-04-01"]
  });
  for (const file of files.data) {
    console.log(file.id, file.filename);
  }

  // Download a file
  const content = await client.files.download(files.data[0].id);
  await writeFile("output.txt", new Uint8Array(await content.arrayBuffer()));

csharp C#
  // List files associated with a session
  var files = await client.Beta.Files.List(new()
  {
      ScopeID = "sesn_abc123",
      Betas = ["managed-agents-2026-04-01"],
  });

  // Download a file
  using var content = await client.Files.Download(files.Items[0].ID);
  await using var output = File.Create("output.txt");
  await (await content.ReadAsStream()).CopyToAsync(output);

go Go
  // List files associated with a session
  files, err := client.Beta.Files.List(ctx, anthropic.BetaFileListParams{
  	ScopeID: anthropic.String("sesn_abc123"),
  	Betas:   []anthropic.AnthropicBeta{"managed-agents-2026-04-01"},
  })
  if err != nil {
  	panic(err)
  }

  // Download a file
  resp, err := client.Files.Download(ctx, files.Data[0].ID)
  if err != nil {
  	panic(err)
  }
  defer resp.Body.Close()
  out, err := os.Create("output.txt")
  if err != nil {
  	panic(err)
  }
  defer out.Close()
  if _, err := io.Copy(out, resp.Body); err != nil {
  	panic(err)
  }

java Java
  // List files associated with a session
  var files = client.beta().files().list(FileListParams.builder()
      .scopeId("sesn_abc123")
      .addBeta(AnthropicBeta.of("managed-agents-2026-04-01"))
      .build());

  // Download a file
  try (HttpResponse response = client.files().download(files.data().get(0).id())) {
      try (InputStream body = response.body()) {
          Files.copy(body, Path.of("output.txt"), StandardCopyOption.REPLACE_EXISTING);
      }
  }

php PHP
  // List files associated with a session
  $files = $client->beta->files->list(
      scopeID: 'sesn_abc123',
      betas: ['managed-agents-2026-04-01'],
  );
  foreach ($files->getItems() as $file) {
      echo "{$file->id} {$file->filename}\n";
  }

  // Download a file
  $content = $client->files->download($files->getItems()[0]->id);
  file_put_contents('output.txt', $content);

ruby Ruby
  # List files associated with a session
  files = client.beta.files.list(
    scope_id: "sesn_abc123",
    betas: ["managed-agents-2026-04-01"]
  )

  # Download a file
  content = client.files.download(files.data[0].id)
  File.binwrite("output.txt", content.read)
  ```
</CodeGroup>


## Supported file types

Source: https://platform.claude.com/llms-full.txt#supported-file-types

The agent can work with any file type, including:

* Source code (`.py`, `.js`, `.ts`, `.go`, `.rs`, and others)
* Data files (`.csv`, `.json`, `.xml`, `.yaml`)
* Documents (`.txt`, `.md`)
* Archives (`.zip`, `.tar.gz`) - the agent can extract these using bash
* Binary files - the agent can process these with appropriate tools


## File paths

Source: https://platform.claude.com/llms-full.txt#file-paths

<Note>
  Files mounted in the sandbox are read-only copies. The agent can read them but cannot modify the original uploaded file. To work with modified versions, the agent writes to new paths within the sandbox.
</Note>

* The path you specify is rooted under the session's uploads directory: a `mount_path` of `/data.csv` places the file at `/mnt/session/uploads/data.csv` in the sandbox
* If you omit `mount_path`, the file is placed at `/mnt/session/uploads/<file_id>`
* Parent directories are created automatically
* Paths should be absolute (starting with `/`)
* Files the agent writes to `/mnt/session/outputs/` become available through the Files API, scoped to the session; see [Listing and downloading session files](https://platform.claude.com/docs/en/managed-agents/files#listing-and-downloading-session-files)


### Manage agent context > Build persistent memory

---
title: Dreams
url: https://platform.claude.com/docs/en/managed-agents/dreams
description: Let Claude reflect on past sessions to curate an agent's memory and surface new insights.
---

<Tip>
  Dreaming is a research preview feature. [Request access](https://claude.com/form/claude-managed-agents) to try it.
</Tip>

Agents write to their [memory stores](https://platform.claude.com/docs/en/managed-agents/memory) as they work, but these writes are local and incremental: over many sessions a memory store accumulates duplicates, contradictions, and stale entries.

**Dreams** let Claude clean that up. A dream reads an existing memory store alongside past session transcripts, then produces a new, reorganized memory store: duplicates merged, stale or contradicted entries replaced with the latest value, and new insights surfaced.

The input store is never modified, so you can review the output and discard it if you don't like the result.

<Note>
  Dream endpoints are gated by the `dreaming-2026-04-21` beta header; the `managed-agents-2026-04-01` header on its own doesn't grant access to dreams. The dream-endpoint examples on this page send both headers; session and memory-store calls need only `managed-agents-2026-04-01`. The SDK sets these automatically.
</Note>


## How it works

Source: https://platform.claude.com/llms-full.txt#how-it-works-9

A **dream** is an asynchronous job that takes:

* a pre-existing **memory store:** the store Claude verifies, deduplicates, and reorganizes, and
* 1 to 100 **sessions:** past transcripts Claude mines for patterns and insights to fold into the output.

The dream produces another **output memory store**, separate from the input. The output store ID appears in the dream's `outputs[]` shortly after the dream starts `running`, once the workflow has cloned the input store; a `running` dream can briefly report an empty `outputs[]`.


## Create a dream

Source: https://platform.claude.com/llms-full.txt#create-a-dream

<CodeGroup>
  ```bash cURL
  dream=$(curl -s https://api.anthropic.com/v1/dreams \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01,dreaming-2026-04-21" \
    -H "content-type: application/json" \
    --data @- <<EOF
  {
    "inputs": [
      { "type": "memory_store", "memory_store_id": "$store_id" },
      { "type": "sessions", "session_ids": ["$session_a", "$session_b"] }
    ],
    "model": "claude-opus-4-8",
    "instructions": "Focus on coding-style preferences; ignore one-off debugging notes."
  }
  EOF
  )
  dream_id=$(jq -r '.id' <<< "$dream")
  echo "$dream_id"  # drm_01...

bash CLI
  dream_id=$(ant beta:dreams create --transform id --raw-output <<YAML
  inputs:
    - type: memory_store
      memory_store_id: $store_id
    - type: sessions
      session_ids: [$session_a, $session_b]
  model: claude-opus-4-8
  instructions: Focus on coding-style preferences; ignore one-off debugging notes.
  YAML
  )

python Python
  dream = client.beta.dreams.create(
      inputs=[
          {"type": "memory_store", "memory_store_id": store_id},
          {"type": "sessions", "session_ids": [session_a, session_b]},
      ],
      model="claude-opus-4-8",
      instructions="Focus on coding-style preferences; ignore one-off debugging notes.",
  )
  print(dream.id)  # drm_01...

typescript TypeScript
  let dream = await client.beta.dreams.create({
    inputs: [
      { type: "memory_store", memory_store_id: storeId },
      { type: "sessions", session_ids: [sessionA, sessionB] },
    ],
    model: "claude-opus-4-8",
    instructions: "Focus on coding-style preferences; ignore one-off debugging notes.",
  });
  console.log(dream.id); // drm_01...

csharp C#
  var dream = await client.Beta.Dreams.Create(new()
  {
      Inputs =
      [
          new BetaDreamMemoryStoreInput
          {
              Type = BetaDreamMemoryStoreInputType.MemoryStore,
              MemoryStoreID = storeID,
          },
          new BetaDreamSessionsInput
          {
              Type = BetaDreamSessionsInputType.Sessions,
              SessionIds = [sessionA, sessionB],
          },
      ],
      Model = "claude-opus-4-8",
      Instructions = "Focus on coding-style preferences; ignore one-off debugging notes.",
  });
  Console.WriteLine(dream.ID);  // drm_01...

go Go
  dream, err := client.Beta.Dreams.New(ctx, anthropic.BetaDreamNewParams{
  	Inputs: []anthropic.BetaDreamInputUnionParam{
  		anthropic.BetaDreamInputParamOfMemoryStore(storeID),
  		anthropic.BetaDreamInputParamOfSessions([]string{sessionA, sessionB}),
  	},
  	Model: anthropic.BetaDreamModelParamsUnion{
  		OfString: anthropic.String("claude-opus-4-8"),
  	},
  	Instructions: anthropic.String("Focus on coding-style preferences; ignore one-off debugging notes."),
  })
  if err != nil {
  	panic(err)
  }
  fmt.Println(dream.ID) // drm_01...

java Java
  var dream = client.beta().dreams().create(
      DreamCreateParams.builder()
          .addMemoryStoreInput(storeId)
          .addSessionsInput(List.of(sessionA, sessionB))
          .model("claude-opus-4-8")
          .instructions("Focus on coding-style preferences; ignore one-off debugging notes.")
          .build()
  );
  IO.println(dream.id());  // drm_01...

php PHP
  $dream = $client->beta->dreams->create(
      inputs: [
          ['type' => 'memory_store', 'memory_store_id' => $storeId],
          ['type' => 'sessions', 'session_ids' => [$sessionA, $sessionB]],
      ],
      model: 'claude-opus-4-8',
      instructions: 'Focus on coding-style preferences; ignore one-off debugging notes.',
  );
  echo "{$dream->id}\n"; // drm_01...

ruby Ruby
  dream = client.beta.dreams.create(
    inputs: [
      {type: "memory_store", memory_store_id: store_id},
      {type: "sessions", session_ids: [session_a, session_b]}
    ],
    model: "claude-opus-4-8",
    instructions: "Focus on coding-style preferences; ignore one-off debugging notes."
  )
  puts dream.id # drm_01...

json
{
  "type": "dream",
  "id": "drm_01AbCDefGhIjKlMnOpQrStUv",
  "status": "pending",
  "inputs": [
    { "type": "memory_store", "memory_store_id": "memstore_01Hx..." },
    { "type": "sessions", "session_ids": ["sesn_01...", "sesn_02..."] }
  ],
  "outputs": [],
  "model": { "id": "claude-opus-4-8" },
  "instructions": "Focus on coding-style preferences; ignore one-off debugging notes.",
  "session_id": null,
  "created_at": "2026-04-29T17:04:10Z",
  "ended_at": null,
  "archived_at": null,
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read_input_tokens": 0,
    "cache_creation_input_tokens": 0
  },
  "error": null
}
```

<Tip>
  If you only have session transcripts and no existing store, [create an empty memory store](https://platform.claude.com/docs/en/managed-agents/memory#create-a-memory-store) first and pass it as the `memory_store` input.
</Tip>

### Steer with instructions

The optional `instructions` field steers what the dreaming pipeline synthesizes. It is applied throughout the pipeline: what to read closely, what to merge or drop, and how to structure the output store.

Use `instructions` for high-level synthesis guidance such as focus areas ("focus on coding-style preferences"), content to preserve unchanged, or output conventions you want applied across the store. The pipeline is a synthesis pass over the inputs, not an editor applied to the text of the store, so imperative directives that target specific lines ("change sentence X to Y", "fix the count in section Z") generally produce no change. To make targeted edits to individual memories, use the [Memory Stores API](https://platform.claude.com/docs/en/managed-agents/memory#view-and-edit-memories) on the output store directly.


## Track progress

Source: https://platform.claude.com/llms-full.txt#track-progress

Dreams run asynchronously and typically take minutes to a few hours, driven by the number of input transcripts. Poll the dream by ID to check status:

<CodeGroup>
  ```bash cURL
  while true; do
    dream=$(curl -s "https://api.anthropic.com/v1/dreams/$dream_id" \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "anthropic-beta: managed-agents-2026-04-01,dreaming-2026-04-21")
    status=$(jq -r '.status' <<< "$dream")
    echo "status=$status input_tokens=$(jq -r '.usage.input_tokens' <<< "$dream")"
    [[ "$status" == "pending" || "$status" == "running" ]] || break
    sleep 10
  done

bash CLI
  ant beta:dreams retrieve --dream-id "$dream_id"

python Python
  while dream.status in ("pending", "running"):
      time.sleep(10)
      dream = client.beta.dreams.retrieve(dream.id)
      print(f"status={dream.status} input_tokens={dream.usage.input_tokens}")

typescript TypeScript
  while (dream.status === "pending" || dream.status === "running") {
    await sleep(10_000);
    dream = await client.beta.dreams.retrieve(dream.id);
    console.log(`status=${dream.status} input_tokens=${dream.usage.input_tokens}`);
  }

csharp C#
  while (dream.Status.Value() is BetaDreamStatus.Pending or BetaDreamStatus.Running)
  {
      await Task.Delay(TimeSpan.FromSeconds(10));
      dream = await client.Beta.Dreams.Retrieve(dream.ID);
      Console.WriteLine($"status={dream.Status.Raw()} input_tokens={dream.Usage.InputTokens}");
  }

go Go
  for dream.Status == anthropic.BetaDreamStatusPending || dream.Status == anthropic.BetaDreamStatusRunning {
  	time.Sleep(10 * time.Second)
  	dream, err = client.Beta.Dreams.Get(ctx, dream.ID, anthropic.BetaDreamGetParams{})
  	if err != nil {
  		panic(err)
  	}
  	fmt.Printf("status=%s input_tokens=%d\n", dream.Status, dream.Usage.InputTokens)
  }

java Java
  while (dream.status().equals(BetaDreamStatus.PENDING)
          || dream.status().equals(BetaDreamStatus.RUNNING)) {
      Thread.sleep(10_000);
      dream = client.beta().dreams().retrieve(dream.id());
      IO.println("status=" + dream.status() + " input_tokens=" + dream.usage().inputTokens());
  }

php PHP
  while (in_array($dream->status, [BetaDreamStatus::PENDING->value, BetaDreamStatus::RUNNING->value], true)) {
      sleep(10);
      $dream = $client->beta->dreams->retrieve($dream->id);
      echo "status={$dream->status} input_tokens={$dream->usage->inputTokens}\n";
  }

ruby Ruby
  while %i[pending running].include?(dream.status)
    sleep 10
    dream = client.beta.dreams.retrieve(dream.id)
    puts "status=#{dream.status} input_tokens=#{dream.usage.input_tokens}"
  end
  ```
</CodeGroup>

### Lifecycle

| `status`    | Meaning                                                                                                           |
| ----------- | ----------------------------------------------------------------------------------------------------------------- |
| `pending`   | Dream successfully created and queued.                                                                            |
| `running`   | The pipeline is processing. `usage` updates as work progresses.                                                   |
| `completed` | Finished successfully. The `outputs[]` value is the new memory store.                                             |
| `failed`    | Dreaming run ended with an error. The output memory store is left as-is with whatever was written before failure. |
| `canceled`  | Dreaming run canceled. The output memory store is left as-is.                                                     |

### Watch the pipeline run

Once a dream is `running`, its `session_id` field points at the underlying [session](https://platform.claude.com/docs/en/managed-agents/sessions) running the pipeline. You can stream that session's [events](https://platform.claude.com/docs/en/managed-agents/events-and-streaming) to observe what the dream is reading and writing in real time. The session is archived (not deleted) when the dream reaches a terminal state, so the transcript remains available afterward.


## Use the output

Source: https://platform.claude.com/llms-full.txt#use-the-output

When `status` reaches `completed`, the `memory_store` entry in `outputs[]` references a fully populated store. It's an ordinary memory store in your workspace. Review it with the [Memory Stores API](https://platform.claude.com/docs/en/managed-agents/memory#view-and-edit-memories) or in the Console, then either:

* **Leverage it:** attach it to future sessions as a `memory_store` resource in place of (or alongside) the input memory store, or
* **Discard it:** [delete the memory store](https://platform.claude.com/docs/en/api/beta/memory_stores/delete) or [archive the memory store](https://platform.claude.com/docs/en/api/beta/memory_stores/archive).

<CodeGroup>
  ```bash cURL
  # After the dream ends, the memory_store output holds the rebuilt store
  output_store_id=$(jq -r 'first(.outputs[] | select(.type == "memory_store")).memory_store_id' <<< "$dream")

  curl -s https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    --data @- <<EOF
  {
    "agent": "$agent_id",
    "environment_id": "$environment_id",
    "resources": [
      { "type": "memory_store", "memory_store_id": "$output_store_id" }
    ]
  }
  EOF

bash CLI
  output_store_id=$(ant beta:dreams retrieve --dream-id "$dream_id" --format json |
    jq -r 'first(.outputs[] | select(.type == "memory_store")).memory_store_id')

  ant beta:sessions create <<YAML
  agent: $agent_id
  environment_id: $environment_id
  resources:
    - type: memory_store
      memory_store_id: $output_store_id
  YAML

python Python
  # After the dream ends, the output holds the rebuilt memory store
  output_store_id = next(
      output.memory_store_id for output in dream.outputs if output.type == "memory_store"
  )

  session = client.beta.sessions.create(
      agent=agent_id,
      environment_id=environment_id,
      resources=[
          {"type": "memory_store", "memory_store_id": output_store_id},
      ],
  )

typescript TypeScript
  // After the dream ends, the output holds the rebuilt memory store
  const output = dream.outputs.find((entry) => entry.type === "memory_store");
  const outputStoreId = output!.memory_store_id;

  await client.beta.sessions.create({
    agent: agentId,
    environment_id: environmentId,
    resources: [
      { type: "memory_store", memory_store_id: outputStoreId },
    ],
  });

csharp C#
  var output = dream.Outputs.FirstOrDefault(entry => entry.Type == "memory_store");
  if (output is { MemoryStoreID: var outputStoreID })
  {
      await client.Beta.Sessions.Create(new()
      {
          Agent = agentID,
          EnvironmentID = environmentID,
          Resources =
          [
              new BetaManagedAgentsMemoryStoreResourceParam
              {
                  Type = BetaManagedAgentsMemoryStoreResourceParamType.MemoryStore,
                  MemoryStoreID = outputStoreID,
              },
          ],
      });
  }

go Go
  for _, output := range dream.Outputs {
  	if output.Type != "memory_store" {
  		continue
  	}
  	outputStoreID := output.MemoryStoreID

  	session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  		Agent: anthropic.BetaSessionNewParamsAgentUnion{
  			OfString: anthropic.String(agentID),
  		},
  		EnvironmentID: environmentID,
  		Resources: []anthropic.BetaSessionNewParamsResourceUnion{{
  			OfMemoryStore: &anthropic.BetaManagedAgentsMemoryStoreResourceParam{
  				MemoryStoreID: outputStoreID,
  			},
  		}},
  	})
  	if err != nil {
  		panic(err)
  	}
  	fmt.Println(session.ID)
  	break
  }

java Java
  var output = dream.outputs().stream()
      .filter(entry -> entry.type().equals(BetaDreamOutput.Type.MEMORY_STORE))
      .findFirst();
  if (output.isPresent()) {
      var outputStoreId = output.get().memoryStoreId();

      var session = client.beta().sessions().create(
          SessionCreateParams.builder()
              .agent(agentId)
              .environmentId(environmentId)
              .addMemoryStoreResource(outputStoreId)
              .build()
      );
  }

php PHP
  $matches = array_filter($dream->outputs, fn($output) => $output->type === 'memory_store');
  $output = $matches ? reset($matches) : null;
  if ($output !== null) {
      $session = $client->beta->sessions->create(
          agent: $agentId,
          environmentID: $environmentId,
          resources: [
              ['type' => 'memory_store', 'memory_store_id' => $output->memoryStoreID],
          ],
      );
  }

ruby Ruby
  output = dream.outputs.find { it.type == :memory_store }
  if output
    client.beta.sessions.create(
      agent: agent_id,
      environment_id: environment_id,
      resources: [
        {type: "memory_store", memory_store_id: output.memory_store_id}
      ]
    )
  end
  ```
</CodeGroup>

The dream itself never deletes or modifies its inputs. On `failed` or `canceled` the output store persists with partial contents so you can inspect what was produced before stopping; clean it up through the Memory Stores API if you don't need it.

<Warning>
  While a dream is `pending` or `running`, the 400 guard applies to archiving the dream itself, not its stores. Archiving or deleting an *input* memory store mid-run (or deleting an input session) will cause the dream to fail with `input_memory_store_unavailable` or `input_session_unavailable`.
</Warning>


## Cancel a dream

Source: https://platform.claude.com/llms-full.txt#cancel-a-dream

Cancel moves a `pending` or `running` dream to `canceled` immediately. Canceling an already-`canceled` dream is an idempotent no-op; canceling a `completed` or `failed` dream returns 400.

<Note>
  After cancellation, the dream's `usage` fields might continue to update for a few seconds while in-flight work winds down. Poll the dream until `usage` stabilizes if you need the final count.
</Note>

<CodeGroup>
  ```bash cURL
  curl -s -X POST "https://api.anthropic.com/v1/dreams/$dream_id/cancel" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01,dreaming-2026-04-21"

bash CLI
  ant beta:dreams cancel --dream-id "$dream_id"

python Python
  client.beta.dreams.cancel(dream.id)

typescript TypeScript
  await client.beta.dreams.cancel(dream.id);

csharp C#
  await client.Beta.Dreams.Cancel(dream.ID);

go Go
  dream, err = client.Beta.Dreams.Cancel(ctx, dream.ID, anthropic.BetaDreamCancelParams{})
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().dreams().cancel(dream.id());

php PHP
  $client->beta->dreams->cancel($dream->id);

ruby Ruby
  client.beta.dreams.cancel(dream.id)
  ```
</CodeGroup>


## Archive a dream

Source: https://platform.claude.com/llms-full.txt#archive-a-dream

Archive sets `archived_at` on a dream that has reached a terminal state (`completed`, `failed`, or `canceled`); `status` is left unchanged. Archived dreams are excluded from default list responses but remain readable by ID. Archiving an already-archived dream is an idempotent no-op. Archiving a `pending` or `running` dream returns 400; cancel it first. There is no unarchive.

<CodeGroup>
  ```bash cURL
  curl -s -X POST "https://api.anthropic.com/v1/dreams/$dream_id/archive" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01,dreaming-2026-04-21"

bash CLI
  ant beta:dreams archive --dream-id "$dream_id"

python Python
  client.beta.dreams.archive(dream.id)

typescript TypeScript
  await client.beta.dreams.archive(dream.id);

csharp C#
  await client.Beta.Dreams.Archive(dream.ID);

go Go
  dream, err = client.Beta.Dreams.Archive(ctx, dream.ID, anthropic.BetaDreamArchiveParams{})
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().dreams().archive(dream.id());

php PHP
  $client->beta->dreams->archive($dream->id);

ruby Ruby
  client.beta.dreams.archive(dream.id)
  ```
</CodeGroup>

Archiving a dream does not touch its output memory store; manage that separately through the [Memory Stores API](https://platform.claude.com/docs/en/managed-agents/memory#view-and-edit-memories).


## List dreams

Source: https://platform.claude.com/llms-full.txt#list-dreams

Returns all non-archived dreams in the workspace, newest first. Use `limit` (default 20, max 100) and the `page` cursor to paginate. Pass `include_archived=true` to include archived dreams.

<CodeGroup>
  ```bash cURL
  curl -s "https://api.anthropic.com/v1/dreams?limit=20" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01,dreaming-2026-04-21"

bash CLI
  ant beta:dreams list --limit 20

python Python
  for listed_dream in client.beta.dreams.list(limit=20):
      print(listed_dream.id, listed_dream.status)

typescript TypeScript
  for await (const listedDream of client.beta.dreams.list({ limit: 20 })) {
    console.log(listedDream.id, listedDream.status);
  }

csharp C#
  var page = await client.Beta.Dreams.List(new() { Limit = 20 });
  await foreach (var listed in page.Paginate())
  {
      Console.WriteLine($"{listed.ID} {listed.Status.Raw()}");
  }

go Go
  dreams := client.Beta.Dreams.ListAutoPaging(ctx, anthropic.BetaDreamListParams{
  	Limit: anthropic.Int(20),
  })
  for dreams.Next() {
  	listed := dreams.Current()
  	fmt.Println(listed.ID, listed.Status)
  }
  if err := dreams.Err(); err != nil {
  	panic(err)
  }

java Java
  for (var listedDream : client.beta().dreams().list(
      DreamListParams.builder().limit(20).build()
  ).autoPager()) {
      IO.println(listedDream.id() + " " + listedDream.status());
  }

php PHP
  foreach ($client->beta->dreams->list(limit: 20)->pagingEachItem() as $dream) {
      echo "{$dream->id} {$dream->status}\n";
  }

ruby Ruby
  client.beta.dreams.list(limit: 20).auto_paging_each do
    puts "#{it.id} #{it.status}"
  end
  ```
</CodeGroup>


## Errors

Source: https://platform.claude.com/llms-full.txt#errors

A non-exhaustive list of possible dreaming errors follows.

| `error.type`                      | When                                                                                            |
| --------------------------------- | ----------------------------------------------------------------------------------------------- |
| `timeout`                         | The pipeline exceeded its runtime budget.                                                       |
| `internal_error`                  | Unclassified pipeline failure.                                                                  |
| `memory_store_org_limit_exceeded` | Your organization hit its memory-store cap while the pipeline was provisioning working storage. |
| `input_memory_store_too_large`    | The input memory store exceeds the pipeline's size limit.                                       |
| `input_memory_store_unavailable`  | The input memory store was archived or deleted after the dream was created.                     |
| `input_session_unavailable`       | An input session was deleted after the dream was created.                                       |


## Billing

Source: https://platform.claude.com/llms-full.txt#billing-3

Dreams are billed at standard API token rates for the model you select; `usage` on the resource reports the exact totals. Cost scales roughly linearly with the number and length of input sessions. Start with a small batch of sessions and scale up once you're satisfied with the curation quality.
