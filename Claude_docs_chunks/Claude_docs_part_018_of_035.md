# platform.claude.com Documentation (Part 18 of 35)

## Limits

Source: https://platform.claude.com/llms-full.txt#limits

| Limit                 | Value                                                                                                           |
| --------------------- | --------------------------------------------------------------------------------------------------------------- |
| Sessions per dream    | 100                                                                                                             |
| `instructions` length | 4,096 characters                                                                                                |
| Supported models      | `claude-opus-5`, `claude-fable-5`, `claude-opus-4-8`, `claude-opus-4-7`, `claude-sonnet-5`, `claude-sonnet-4-6` |

Default rate limits apply to dream creation while this feature is in research preview. [Contact support](https://support.claude.com) if you need higher limits.


---
title: Using agent memory
url: https://platform.claude.com/docs/en/managed-agents/memory
description: Give your agents persistent memory that survives across sessions using memory stores.
---

Each Managed Agents session starts with a fresh context by default. When a session ends, any state the agent built up is gone. Memory stores let the agent carry information across sessions: user preferences, project conventions, prior mistakes, and domain context.

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>

<Note>
  Don't combine `agent-memory-2026-07-22` with `managed-agents-2026-04-01` on a memory store request: sending both returns a `400` error. If your code sets beta headers explicitly, replace `managed-agents-2026-04-01` with `agent-memory-2026-07-22` on memory store calls rather than adding a second value. Session endpoints, including attaching a memory store to a session, still use `managed-agents-2026-04-01`.

  `GET /v1/memory_stores/{memory_store_id}/memories` behaves the same under either header: results come back in a stable, server-defined order, and `path_prefix` and `depth` apply the same way.
</Note>


## Overview

Source: https://platform.claude.com/llms-full.txt#overview-4

A **memory store** is a workspace-scoped collection of text documents optimized for Claude. When you attach a store to a session, it is mounted as a directory inside the session's sandbox. The agent reads and writes it with the same file tools it uses for the rest of the filesystem, and a note describing each mount is automatically added to the system prompt, telling the agent where to look. The [agent toolset](https://platform.claude.com/docs/en/managed-agents/tools) is required for these interactions; make sure to enable it during [agent creation](https://platform.claude.com/docs/en/managed-agents/agent-setup). On [self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores), that directory is not a live mount. Instead, the SDK's environment worker downloads each attached store into your sandbox before the agent's tools run and keeps that copy in sync with the store.

Each **memory** in a store is addressed by a path and can be read and edited directly through the API or the Claude Console, allowing for tuning, importing, and exporting.

Every change to a memory creates an immutable **memory version**, giving you an audit trail and point-in-time recovery for everything the agent writes.


## Create a memory store

Source: https://platform.claude.com/llms-full.txt#create-a-memory-store

Give the store a `name` and a `description`. The description is passed to the agent, telling it what the store contains.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  store=$(curl -s https://api.anthropic.com/v1/memory_stores \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22" \
    -H "content-type: application/json" \
    -d '{"name": "User Preferences", "description": "Per-user preferences and project context."}')
  store_id=$(jq -r '.id' <<< "$store")
  echo "$store_id"  # memstore_01Hx...

bash CLI
  store_id=$(ant beta:memory-stores create \
    --name "User Preferences" \
    --description "Per-user preferences and project context." \
    --transform id --raw-output)

python Python
  store = client.beta.memory_stores.create(
      name="User Preferences",
      description="Per-user preferences and project context.",
  )
  print(store.id)  # memstore_01Hx...

typescript TypeScript
  const store = await client.beta.memoryStores.create({
    name: "User Preferences",
    description: "Per-user preferences and project context."
  });
  console.log(store.id); // memstore_01Hx...

csharp C#
  var store = await client.Beta.MemoryStores.Create(new()
  {
      Name = "User Preferences",
      Description = "Per-user preferences and project context.",
  });
  Console.WriteLine(store.ID);  // memstore_01Hx...

go Go
  store, err := client.Beta.MemoryStores.New(ctx, anthropic.BetaMemoryStoreNewParams{
  	Name:        "User Preferences",
  	Description: anthropic.String("Per-user preferences and project context."),
  })
  if err != nil {
  	panic(err)
  }
  fmt.Println(store.ID) // memstore_01Hx...

java Java
  var store = client.beta().memoryStores().create(
      MemoryStoreCreateParams.builder()
          .name("User Preferences")
          .description("Per-user preferences and project context.")
          .build()
  );
  IO.println(store.id());  // memstore_01Hx...

php PHP
  use Anthropic\Client;

  $client = new Client();

  $store = $client->beta->memoryStores->create(
      name: 'User Preferences',
      description: 'Per-user preferences and project context.',
  );
  echo "{$store->id}\n"; // memstore_01Hx...

ruby Ruby
  require "anthropic"

  client = Anthropic::Client.new

  store = client.beta.memory_stores.create(
    name: "User Preferences",
    description: "Per-user preferences and project context."
  )
  puts store.id # memstore_01Hx...

bash cURL
  curl -s "https://api.anthropic.com/v1/memory_stores/$store_id/memories" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22" \
    -H "content-type: application/json" \
    -d '{"path": "/formatting_standards.md", "content": "All reports use GAAP formatting. Dates are ISO-8601..."}' > /dev/null

bash CLI
  ant beta:memory-stores:memories create \
    --memory-store-id "$store_id" \
    --path "/formatting_standards.md" \
    --content "All reports use GAAP formatting. Dates are ISO-8601..." \
    > /dev/null

python Python
  client.beta.memory_stores.memories.create(
      store.id,
      path="/formatting_standards.md",
      content="All reports use GAAP formatting. Dates are ISO-8601...",
  )

typescript TypeScript
  await client.beta.memoryStores.memories.create(store.id, {
    path: "/formatting_standards.md",
    content: "All reports use GAAP formatting. Dates are ISO-8601..."
  });

csharp C#
  await client.Beta.MemoryStores.Memories.Create(store.ID, new()
  {
      Path = "/formatting_standards.md",
      Content = "All reports use GAAP formatting. Dates are ISO-8601...",
  });

go Go
  _, err = client.Beta.MemoryStores.Memories.New(ctx, store.ID, anthropic.BetaMemoryStoreMemoryNewParams{
  	Path:    "/formatting_standards.md",
  	Content: anthropic.String("All reports use GAAP formatting. Dates are ISO-8601..."),
  })
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().memoryStores().memories().create(
      store.id(),
      MemoryCreateParams.builder()
          .path("/formatting_standards.md")
          .content("All reports use GAAP formatting. Dates are ISO-8601...")
          .build()
  );

php PHP
  $client->beta->memoryStores->memories->create(
      $store->id,
      path: '/formatting_standards.md',
      content: 'All reports use GAAP formatting. Dates are ISO-8601...',
  );

ruby Ruby
  client.beta.memory_stores.memories.create(
    store.id,
    path: "/formatting_standards.md",
    content: "All reports use GAAP formatting. Dates are ISO-8601..."
  )
  ```
</CodeGroup>

<Tip>
  Individual memories within the store are capped at 100 kB (\~25k tokens). A store holds a maximum of 10,000 memories. Structure memory as many small focused files, not a few large ones.
</Tip>


## Attach a memory store to a session

Source: https://platform.claude.com/llms-full.txt#attach-a-memory-store-to-a-session

Memory stores are attached in the session's `resources[]` array when the [session is created](https://platform.claude.com/docs/en/managed-agents/sessions#creating-a-session). Unlike file resources, memory stores can only be attached at session creation time; adding or removing one from a running session is not supported. You attach memory stores the same way for sessions on cloud and [self-hosted environments](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores); self-hosted environments accept only `memory_store` resources.

Optionally include `instructions` to provide session-specific guidance for how the agent should use this store. It is shown to the agent alongside the store's `name` and `description`, and is capped at 4,096 characters.

You can configure `access` as well. It defaults to `read_write` (shown explicitly in the following example), but `read_only` is also supported.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
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
      {
        "type": "memory_store",
        "memory_store_id": "$store_id",
        "access": "read_write",
        "instructions": "User preferences and project context. Check before starting any task."
      }
    ]
  }
  EOF

bash CLI
  ant beta:sessions create <<YAML
  agent: $agent_id
  environment_id: $environment_id
  resources:
    - type: memory_store
      memory_store_id: $store_id
      access: read_write
      instructions: User preferences and project context. Check before starting any task.
  YAML

python Python
  session = client.beta.sessions.create(
      agent=agent.id,
      environment_id=environment.id,
      resources=[
          {
              "type": "memory_store",
              "memory_store_id": store.id,
              "access": "read_write",
              "instructions": "User preferences and project context. Check before starting any task.",
          }
      ],
  )

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: agent.id,
    environment_id: environment.id,
    resources: [
      {
        type: "memory_store",
        memory_store_id: store.id,
        access: "read_write",
        instructions: "User preferences and project context. Check before starting any task."
      }
    ]
  });

csharp C#
  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = agent.ID,
      EnvironmentID = environment.ID,
      Resources =
      [
          new BetaManagedAgentsMemoryStoreResourceParam
          {
              Type = "memory_store",
              MemoryStoreID = store.ID,
              Access = "read_write",
              Instructions = "User preferences and project context. Check before starting any task.",
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
  		OfMemoryStore: &anthropic.BetaManagedAgentsMemoryStoreResourceParam{
  			Type:          anthropic.BetaManagedAgentsMemoryStoreResourceParamTypeMemoryStore,
  			MemoryStoreID: store.ID,
  			Access:        anthropic.BetaManagedAgentsMemoryStoreResourceParamAccessReadWrite,
  			Instructions:  anthropic.String("User preferences and project context. Check before starting any task."),
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
              BetaManagedAgentsMemoryStoreResourceParam.builder()
                  .type(BetaManagedAgentsMemoryStoreResourceParam.Type.MEMORY_STORE)
                  .memoryStoreId(store.id())
                  .access(BetaManagedAgentsMemoryStoreResourceParam.Access.READ_WRITE)
                  .instructions("User preferences and project context. Check before starting any task.")
                  .build()
          )
          .build()
  );

php PHP
  $session = $client->beta->sessions->create(
      agent: $agent->id,
      environmentID: $environment->id,
      resources: [
          [
              'type' => 'memory_store',
              'memory_store_id' => $store->id,
              'access' => 'read_write',
              'instructions' => 'User preferences and project context. Check before starting any task.',
          ],
      ],
  );

ruby Ruby
  session = client.beta.sessions.create(
    agent: agent.id,
    environment_id: environment.id,
    resources: [
      {
        type: "memory_store",
        memory_store_id: store.id,
        access: "read_write",
        instructions: "User preferences and project context. Check before starting any task."
      }
    ]
  )
  ```
</CodeGroup>

<Warning>
  Memory stores attach with `read_write` access by default. If the agent processes untrusted input (user-supplied prompts, fetched web content, or third-party tool output), a successful prompt injection could write malicious content into the store. Later sessions then read that content as trusted memory. Use `read_only` for reference material, shared lookups, and any store the agent does not need to modify.
</Warning>

A maximum of **8 memory stores** are supported per session. Attach multiple stores when different parts of memory have different owners or access rules. Common reasons:

* **Shared reference material:** one read-only store attached to many sessions (standards, conventions, domain knowledge), kept separate from each session's own read-write store.
* **Mapping to your product's structure:** one store per end user, per team, or per project, while sharing a single agent configuration.
* **Different lifecycles:** a store that outlives any single session, or one you want to archive on its own schedule.

### How the agent accesses memory

Each attached store is mounted inside the session's sandbox as a directory under `/mnt/memory/`. The directory name is the store's display name sanitized to a filesystem-safe slug (lowercased; non-alphanumeric runs become a single hyphen), so a store named "Demo Memory" mounts at `/mnt/memory/demo-memory/`. The exact path is returned in the `mount_path` field on the session's memory-store resource; read it from there rather than constructing it yourself. The agent reads and writes the store with the standard [agent toolset](https://platform.claude.com/docs/en/managed-agents/tools). Writes under the mount path are persisted back to the store and stay in sync across sessions that share it; writes to any other path under `/mnt/memory/` fail, because the sandbox mounts that parent directory read-only. A short description of each mount (display name, mount path, access mode, store `description`, and any `instructions`) is automatically added to the system prompt.

`access` is enforced at the filesystem level: a `read_only` mount rejects writes, while writes to a `read_write` mount produce [memory versions](https://platform.claude.com/docs/en/managed-agents/memory#audit-memory-changes) attributed to the session.

<Note>
  On [self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores), each store's directory is a local copy that the SDK worker manages rather than a live mount. The worker reconciles each copy with its store after tool calls, at most once per sync interval (15 seconds by default), and once more when the session ends. The agent's `write` and `edit` tools change only the local copy; the worker uploads those changes at its next sync, so another session running on a self-hosted sandbox sees a change only after both workers have synced. Paths under `/mnt/memory/` outside the store directories are not scratch space there: the worker's file tools refuse to write to them, and anything a shell command writes there is never synced to a store.

  For a `read_only` store, the worker's `write` and `edit` tools refuse changes under that directory and the worker never uploads anything from it. To learn how the worker resolves write conflicts, and what the `bash` tool can still change in a read-only store's local copy, see [Read-only stores and conflicts](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#read-only-stores-and-conflicts).
</Note>

The agent's reads and writes appear in the [event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming) as ordinary `agent.tool_use` and `agent.tool_result` events for whichever tool touched the mount.


## View and edit memories

Source: https://platform.claude.com/llms-full.txt#view-and-edit-memories

Memory stores can be managed directly through the API. Use this for building review workflows, correcting bad memories, or seeding stores before any session runs.

### List memories

List the memories in a store. Results are returned in a stable, server-defined order.

* `path_prefix` scopes the list to one directory. It must end with `/` and matches whole path segments, so `path_prefix=/notes/` returns `/notes/todo.md` but not `/notes-archive/todo.md`.
* `depth` controls how deep the listing goes below `path_prefix`: omit it (or pass `0`) to list the whole subtree, or pass `1` to list only the immediate children. Other values return a `400` error.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl -s "https://api.anthropic.com/v1/memory_stores/$store_id/memories?path_prefix=/" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22" | jq -r '.data[] | "\(.type)  \(.path)"'

bash CLI
  ant beta:memory-stores:memories list \
    --memory-store-id "$store_id" \
    --path-prefix "/"

python Python
  page = client.beta.memory_stores.memories.list(
      store.id,
      path_prefix="/",
  )
  for item in page.data:
      print(item.type, item.path)

typescript TypeScript
  const page = await client.beta.memoryStores.memories.list(store.id, {
    path_prefix: "/"
  });
  for (const item of page.data) {
    console.log(item.type, item.path);
  }

csharp C#
  var page = await client.Beta.MemoryStores.Memories.List(store.ID, new()
  {
      PathPrefix = "/",
  });
  await foreach (var item in page.Paginate())
  {
      var line = item.Match(m => $"memory  {m.Path}", p => $"memory_prefix  {p.Path}");
      Console.WriteLine(line);
  }

go Go
  page, err := client.Beta.MemoryStores.Memories.List(ctx, store.ID, anthropic.BetaMemoryStoreMemoryListParams{
  	PathPrefix: anthropic.String("/"),
  })
  if err != nil {
  	panic(err)
  }
  for _, item := range page.Data {
  	fmt.Println(item.Type, item.Path)
  }

java Java
  var page = client.beta().memoryStores().memories().list(
      store.id(),
      MemoryListParams.builder()
          .pathPrefix("/")
          .build()
  );
  for (var item : page.data()) {
      item.memory().ifPresent(m -> IO.println("memory  " + m.path()));
      item.memoryPrefix().ifPresent(p -> IO.println("memory_prefix  " + p.path()));
  }

php PHP
  $page = $client->beta->memoryStores->memories->list(
      $store->id,
      pathPrefix: '/',
  );
  foreach ($page->data as $item) {
      echo "{$item->type}  {$item->path}\n";
  }

ruby Ruby
  page = client.beta.memory_stores.memories.list(
    store.id,
    path_prefix: "/"
  )
  page.data.each do |entry|
    puts "#{entry.type}  #{entry.path}"
  end

bash cURL
  curl -s "https://api.anthropic.com/v1/memory_stores/$store_id/memories/$mem_id" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22" | jq -r '.content'

bash CLI
  ant beta:memory-stores:memories retrieve \
    --memory-store-id "$store_id" \
    --memory-id "$mem_id"

python Python
  retrieved = client.beta.memory_stores.memories.retrieve(
      mem.id,
      memory_store_id=store.id,
  )
  print(retrieved.content)

typescript TypeScript
  const retrieved = await client.beta.memoryStores.memories.retrieve(mem.id, {
    memory_store_id: store.id
  });
  console.log(retrieved.content);

csharp C#
  var retrieved = await client.Beta.MemoryStores.Memories.Retrieve(mem.ID, new()
  {
      MemoryStoreID = store.ID,
  });
  Console.WriteLine(retrieved.Content);

go Go
  retrieved, err := client.Beta.MemoryStores.Memories.Get(ctx, mem.ID, anthropic.BetaMemoryStoreMemoryGetParams{
  	MemoryStoreID: store.ID,
  })
  if err != nil {
  	panic(err)
  }
  fmt.Println(retrieved.Content)

java Java
  var retrieved = client.beta().memoryStores().memories().retrieve(
      mem.id(),
      MemoryRetrieveParams.builder().memoryStoreId(store.id()).build()
  );
  IO.println(retrieved.content().orElseThrow());

php PHP
  $retrieved = $client->beta->memoryStores->memories->retrieve($mem->id, memoryStoreID: $store->id);
  echo "{$retrieved->content}\n";

ruby Ruby
  retrieved = client.beta.memory_stores.memories.retrieve(
    mem.id,
    memory_store_id: store.id
  )
  puts retrieved.content

bash cURL
  mem=$(curl -s "https://api.anthropic.com/v1/memory_stores/$store_id/memories" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22" \
    -H "content-type: application/json" \
    -d '{"path": "/preferences/formatting.md", "content": "Always use tabs, not spaces."}')
  mem_id=$(jq -r '.id' <<< "$mem")
  mem_sha=$(jq -r '.content_sha256' <<< "$mem")

bash CLI
  mem=$(ant beta:memory-stores:memories create \
    --memory-store-id "$store_id" \
    --path "/preferences/formatting.md" \
    --content "Always use tabs, not spaces." \
    --format json)
  mem_id=$(jq -r '.id' <<< "$mem")
  mem_sha=$(jq -r '.content_sha256' <<< "$mem")

python Python
  mem = client.beta.memory_stores.memories.create(
      store.id,
      path="/preferences/formatting.md",
      content="Always use tabs, not spaces.",
  )

typescript TypeScript
  const mem = await client.beta.memoryStores.memories.create(store.id, {
    path: "/preferences/formatting.md",
    content: "Always use tabs, not spaces."
  });

csharp C#
  var mem = await client.Beta.MemoryStores.Memories.Create(store.ID, new()
  {
      Path = "/preferences/formatting.md",
      Content = "Always use tabs, not spaces.",
  });

go Go
  mem, err := client.Beta.MemoryStores.Memories.New(ctx, store.ID, anthropic.BetaMemoryStoreMemoryNewParams{
  	Path:    "/preferences/formatting.md",
  	Content: anthropic.String("Always use tabs, not spaces."),
  })
  if err != nil {
  	panic(err)
  }

java Java
  var mem = client.beta().memoryStores().memories().create(
      store.id(),
      MemoryCreateParams.builder()
          .path("/preferences/formatting.md")
          .content("Always use tabs, not spaces.")
          .build()
  );

php PHP
  $mem = $client->beta->memoryStores->memories->create(
      $store->id,
      path: '/preferences/formatting.md',
      content: 'Always use tabs, not spaces.',
  );

ruby Ruby
  mem = client.beta.memory_stores.memories.create(
    store.id,
    path: "/preferences/formatting.md",
    content: "Always use tabs, not spaces."
  )

bash cURL
  curl -s -X POST "https://api.anthropic.com/v1/memory_stores/$store_id/memories/$mem_id" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22" \
    -H "content-type: application/json" \
    -d '{"path": "/archive/2026_q1_formatting.md"}' > /dev/null

bash CLI
  ant beta:memory-stores:memories update \
    --memory-store-id "$store_id" \
    --memory-id "$mem_id" \
    --path "/archive/2026_q1_formatting.md" \
    > /dev/null

python Python
  client.beta.memory_stores.memories.update(
      mem.id,
      memory_store_id=store.id,
      path="/archive/2026_q1_formatting.md",
  )

typescript TypeScript
  await client.beta.memoryStores.memories.update(mem.id, {
    memory_store_id: store.id,
    path: "/archive/2026_q1_formatting.md"
  });

csharp C#
  await client.Beta.MemoryStores.Memories.Update(mem.ID, new()
  {
      MemoryStoreID = store.ID,
      Path = "/archive/2026_q1_formatting.md",
  });

go Go
  _, err = client.Beta.MemoryStores.Memories.Update(ctx, mem.ID, anthropic.BetaMemoryStoreMemoryUpdateParams{
  	MemoryStoreID: store.ID,
  	Path:          anthropic.String("/archive/2026_q1_formatting.md"),
  })
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().memoryStores().memories().update(
      mem.id(),
      MemoryUpdateParams.builder()
          .memoryStoreId(store.id())
          .path("/archive/2026_q1_formatting.md")
          .build()
  );

php PHP
  $client->beta->memoryStores->memories->update(
      $mem->id,
      memoryStoreID: $store->id,
      path: '/archive/2026_q1_formatting.md',
  );

ruby Ruby
  client.beta.memory_stores.memories.update(
    mem.id,
    memory_store_id: store.id,
    path: "/archive/2026_q1_formatting.md"
  )

bash cURL
  curl -s -X POST "https://api.anthropic.com/v1/memory_stores/$store_id/memories/$mem_id" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22" \
    -H "content-type: application/json" \
    --data @- > /dev/null <<EOF
  {
    "content": "CORRECTED: Always use 2-space indentation.",
    "precondition": {"type": "content_sha256", "content_sha256": "$mem_sha"}
  }
  EOF

bash CLI
  ant beta:memory-stores:memories update \
    --memory-store-id "$store_id" \
    --memory-id "$mem_id" \
    --content "CORRECTED: Always use 2-space indentation." \
    --precondition "{type: content_sha256, content_sha256: $mem_sha}" \
    > /dev/null

python Python
  client.beta.memory_stores.memories.update(
      memory_id=mem.id,
      memory_store_id=store.id,
      content="CORRECTED: Always use 2-space indentation.",
      precondition={"type": "content_sha256", "content_sha256": mem.content_sha256},
  )

typescript TypeScript
  await client.beta.memoryStores.memories.update(mem.id, {
    memory_store_id: store.id,
    content: "CORRECTED: Always use 2-space indentation.",
    precondition: { type: "content_sha256", content_sha256: mem.content_sha256 }
  });

csharp C#
  await client.Beta.MemoryStores.Memories.Update(mem.ID, new()
  {
      MemoryStoreID = store.ID,
      Content = "CORRECTED: Always use 2-space indentation.",
      Precondition = new BetaManagedAgentsPrecondition
      {
          Type = "content_sha256",
          ContentSha256 = mem.ContentSha256,
      },
  });

go Go
  _, err = client.Beta.MemoryStores.Memories.Update(ctx, mem.ID, anthropic.BetaMemoryStoreMemoryUpdateParams{
  	MemoryStoreID: store.ID,
  	Content:       anthropic.String("CORRECTED: Always use 2-space indentation."),
  	Precondition: anthropic.BetaManagedAgentsPreconditionParam{
  		Type:          anthropic.BetaManagedAgentsPreconditionTypeContentSha256,
  		ContentSha256: anthropic.String(mem.ContentSha256),
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().memoryStores().memories().update(
      mem.id(),
      MemoryUpdateParams.builder()
          .memoryStoreId(store.id())
          .content("CORRECTED: Always use 2-space indentation.")
          .precondition(
              BetaManagedAgentsPrecondition.builder()
                  .type(BetaManagedAgentsPrecondition.Type.CONTENT_SHA256)
                  .contentSha256(mem.contentSha256())
                  .build()
          )
          .build()
  );

php PHP
  $client->beta->memoryStores->memories->update(
      $mem->id,
      memoryStoreID: $store->id,
      content: 'CORRECTED: Always use 2-space indentation.',
      precondition: ['type' => 'content_sha256', 'content_sha256' => $mem->contentSha256],
  );

ruby Ruby
  client.beta.memory_stores.memories.update(
    mem.id,
    memory_store_id: store.id,
    content: "CORRECTED: Always use 2-space indentation.",
    precondition: {type: "content_sha256", content_sha256: mem.content_sha256}
  )

bash cURL
  curl -s -X DELETE "https://api.anthropic.com/v1/memory_stores/$store_id/memories/$mem_id" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22" > /dev/null

bash CLI
  ant beta:memory-stores:memories delete \
    --memory-store-id "$store_id" \
    --memory-id "$mem_id" \
    > /dev/null

python Python
  client.beta.memory_stores.memories.delete(
      mem.id,
      memory_store_id=store.id,
  )

typescript TypeScript
  await client.beta.memoryStores.memories.delete(mem.id, {
    memory_store_id: store.id
  });

csharp C#
  await client.Beta.MemoryStores.Memories.Delete(mem.ID, new()
  {
      MemoryStoreID = store.ID,
  });

go Go
  _, err = client.Beta.MemoryStores.Memories.Delete(ctx, mem.ID, anthropic.BetaMemoryStoreMemoryDeleteParams{
  	MemoryStoreID: store.ID,
  })
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().memoryStores().memories().delete(
      mem.id(),
      MemoryDeleteParams.builder().memoryStoreId(store.id()).build()
  );

php PHP
  $client->beta->memoryStores->memories->delete($mem->id, memoryStoreID: $store->id);

ruby Ruby
  client.beta.memory_stores.memories.delete(
    mem.id,
    memory_store_id: store.id
  )
  ```
</CodeGroup>

See the [Delete a memory reference](https://platform.claude.com/docs/en/api/beta/memory_stores/memories/delete) for full parameters and response schema.


## Audit memory changes

Source: https://platform.claude.com/llms-full.txt#audit-memory-changes

Every mutation to a memory creates an immutable **memory version** (`memver_...`). Use the version endpoints to audit who changed what and when, to inspect or restore a prior snapshot, and to scrub sensitive content out of history with redact.

Versions belong to the store (not the individual memory) and are not deleted when the memory itself is deleted, so the audit trail also covers deleted memories, subject to the retention described below. Versions are retained for 30 days after they are written; however, the recent versions of a live memory are always kept regardless of age, so memories that change infrequently might retain history beyond 30 days. The live `memories.retrieve` call always returns the latest version; the version endpoints give you the retained history.

There is no dedicated restore endpoint; to roll back, retrieve the version you want and write its `content` back with `memories.update` (or `memories.create` if the parent memory has been deleted, provided the version you want is still retained).

Past memory versions might be deleted after 30 days. To preserve memory history for longer, export versions through the API.

### List versions

List version history for a store, newest first. The example filters to a single memory's history:

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  versions=$(curl -s "https://api.anthropic.com/v1/memory_stores/$store_id/memory_versions?memory_id=$mem_id" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22")
  jq -r '.data[] | "\(.id): \(.operation)"' <<< "$versions"
  version_id=$(jq -r '.data[1].id' <<< "$versions")

bash CLI
  versions=$(ant beta:memory-stores:memory-versions list \
    --memory-store-id "$store_id" \
    --memory-id "$mem_id" \
    --format json)
  # `list --format json` emits one JSON object per item.
  jq -r '"\(.id): \(.operation)"' <<< "$versions"
  version_id=$(jq -rs '.[1].id' <<< "$versions")

python Python
  versions = client.beta.memory_stores.memory_versions.list(
      store.id,
      memory_id=mem.id,
  )
  for version in versions:
      print(f"{version.id}: {version.operation}")

  version_id = versions.data[1].id

typescript TypeScript
  const versions = await client.beta.memoryStores.memoryVersions.list(store.id, {
    memory_id: mem.id
  });
  for await (const v of versions) {
    console.log(`${v.id}: ${v.operation}`);
  }

  const versionId = versions.data[1].id;

csharp C#
  var versions = await client.Beta.MemoryStores.MemoryVersions.List(store.ID, new()
  {
      MemoryID = mem.ID,
  });
  var versionIds = new List<string>();
  await foreach (var v in versions.Paginate())
  {
      Console.WriteLine($"{v.ID}: {v.Operation.Raw()}");
      versionIds.Add(v.ID);
  }

  var versionId = versionIds[1];

go Go
  versions := client.Beta.MemoryStores.MemoryVersions.ListAutoPaging(ctx, store.ID, anthropic.BetaMemoryStoreMemoryVersionListParams{
  	MemoryID: anthropic.String(mem.ID),
  })
  for versions.Next() {
  	v := versions.Current()
  	fmt.Printf("%s: %s\n", v.ID, v.Operation)
  }
  if err := versions.Err(); err != nil {
  	panic(err)
  }

  vpage, err := client.Beta.MemoryStores.MemoryVersions.List(ctx, store.ID, anthropic.BetaMemoryStoreMemoryVersionListParams{
  	MemoryID: anthropic.String(mem.ID),
  })
  if err != nil {
  	panic(err)
  }
  versionID := vpage.Data[1].ID

java Java
  var versions = client.beta().memoryStores().memoryVersions().list(
      store.id(),
      MemoryVersionListParams.builder().memoryId(mem.id()).build()
  );
  for (var v : versions.autoPager()) {
      IO.println(v.id() + ": " + v.operation());
  }

  var versionId = versions.data().get(1).id();

php PHP
  $versions = $client->beta->memoryStores->memoryVersions->list(
      $store->id,
      memoryID: $mem->id,
  );
  foreach ($versions->pagingEachItem() as $v) {
      echo "{$v->id}: {$v->operation}\n";
  }

  $versionId = $versions->data[1]->id;

ruby Ruby
  versions = client.beta.memory_stores.memory_versions.list(
    store.id,
    memory_id: mem.id
  )
  versions.auto_paging_each do |version|
    puts "#{version.id}: #{version.operation}"
  end

  version_id = versions.data[1].id

bash cURL
  curl -s "https://api.anthropic.com/v1/memory_stores/$store_id/memory_versions/$version_id" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22"

bash CLI
  ant beta:memory-stores:memory-versions retrieve \
    --memory-store-id "$store_id" \
    --memory-version-id "$version_id"

python Python
  version = client.beta.memory_stores.memory_versions.retrieve(
      version_id,
      memory_store_id=store.id,
  )
  print(version.content)

typescript TypeScript
  const version = await client.beta.memoryStores.memoryVersions.retrieve(versionId, {
    memory_store_id: store.id
  });
  console.log(version.content);

csharp C#
  var version = await client.Beta.MemoryStores.MemoryVersions.Retrieve(versionId, new()
  {
      MemoryStoreID = store.ID,
  });
  Console.WriteLine(version.Content);

go Go
  version, err := client.Beta.MemoryStores.MemoryVersions.Get(ctx, versionID, anthropic.BetaMemoryStoreMemoryVersionGetParams{
  	MemoryStoreID: store.ID,
  })
  if err != nil {
  	panic(err)
  }
  fmt.Println(version.Content)

java Java
  var version = client.beta().memoryStores().memoryVersions().retrieve(
      versionId,
      MemoryVersionRetrieveParams.builder().memoryStoreId(store.id()).build()
  );
  IO.println(version.content().orElseThrow());

php PHP
  $version = $client->beta->memoryStores->memoryVersions->retrieve(
      $versionId,
      memoryStoreID: $store->id,
  );
  echo "{$version->content}\n";

ruby Ruby
  version = client.beta.memory_stores.memory_versions.retrieve(
    version_id,
    memory_store_id: store.id
  )
  puts version.content

bash cURL
  curl -s -X POST "https://api.anthropic.com/v1/memory_stores/$store_id/memory_versions/$version_id/redact" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22" \
    -H "content-type: application/json" \
    -d '{}'

bash CLI
  ant beta:memory-stores:memory-versions redact \
    --memory-store-id "$store_id" \
    --memory-version-id "$version_id"

python Python
  client.beta.memory_stores.memory_versions.redact(
      version_id,
      memory_store_id=store.id,
  )

typescript TypeScript
  await client.beta.memoryStores.memoryVersions.redact(versionId, {
    memory_store_id: store.id
  });

csharp C#
  await client.Beta.MemoryStores.MemoryVersions.Redact(versionId, new()
  {
      MemoryStoreID = store.ID,
  });

go Go
  _, err = client.Beta.MemoryStores.MemoryVersions.Redact(ctx, versionID, anthropic.BetaMemoryStoreMemoryVersionRedactParams{
  	MemoryStoreID: store.ID,
  })
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().memoryStores().memoryVersions().redact(
      versionId,
      MemoryVersionRedactParams.builder().memoryStoreId(store.id()).build()
  );

php PHP
  $client->beta->memoryStores->memoryVersions->redact(
      $versionId,
      memoryStoreID: $store->id,
  );

ruby Ruby
  client.beta.memory_stores.memory_versions.redact(
    version_id,
    memory_store_id: store.id
  )
  ```
</CodeGroup>

See the [Redact a memory version reference](https://platform.claude.com/docs/en/api/beta/memory_stores/memory_versions/redact) for full parameters and response schema.


## Manage memory stores

Source: https://platform.claude.com/llms-full.txt#manage-memory-stores

In addition to [`create`](https://platform.claude.com/docs/en/api/beta/memory_stores/create), memory stores support [`retrieve`](https://platform.claude.com/docs/en/api/beta/memory_stores/retrieve), [`update`](https://platform.claude.com/docs/en/api/beta/memory_stores/update), [`list`](https://platform.claude.com/docs/en/api/beta/memory_stores/list), [`archive`](https://platform.claude.com/docs/en/api/beta/memory_stores/archive), and [`delete`](https://platform.claude.com/docs/en/api/beta/memory_stores/delete).

### List stores

List stores in the workspace. Archived stores are excluded by default; pass `include_archived: true` to include them.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl -s "https://api.anthropic.com/v1/memory_stores?include_archived=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22" | jq '.data[] | {id, name, archived_at}'

bash CLI
  ant beta:memory-stores list --include-archived

python Python
  for memory_store in client.beta.memory_stores.list(include_archived=True):
      print(memory_store.id, memory_store.name, memory_store.archived_at)

typescript TypeScript
  for await (const s of client.beta.memoryStores.list({ include_archived: true })) {
    console.log(s.id, s.name, s.archived_at);
  }

csharp C#
  var stores = await client.Beta.MemoryStores.List(new() { IncludeArchived = true });
  await foreach (var s in stores.Paginate())
  {
      Console.WriteLine($"{s.ID} {s.Name} {s.ArchivedAt}");
  }

go Go
  stores := client.Beta.MemoryStores.ListAutoPaging(ctx, anthropic.BetaMemoryStoreListParams{
  	IncludeArchived: anthropic.Bool(true),
  })
  for stores.Next() {
  	s := stores.Current()
  	fmt.Println(s.ID, s.Name, s.ArchivedAt)
  }
  if err := stores.Err(); err != nil {
  	panic(err)
  }

java Java
  for (var s : client.beta().memoryStores().list(
      MemoryStoreListParams.builder().includeArchived(true).build()
  ).autoPager()) {
      IO.println(s.id() + " " + s.name() + " " + s.archivedAt());
  }

php PHP
  foreach ($client->beta->memoryStores->list(includeArchived: true)->pagingEachItem() as $s) {
      // archivedAt is only set on archived stores.
      $archivedAt = isset($s->archivedAt) ? $s->archivedAt->format(DATE_ATOM) : '';
      echo "{$s->id} {$s->name} {$archivedAt}\n";
  }

ruby Ruby
  client.beta.memory_stores.list(include_archived: true).auto_paging_each do |memory_store|
    puts "#{memory_store.id} #{memory_store.name} #{memory_store.archived_at}"
  end

bash cURL
  curl -s -X POST "https://api.anthropic.com/v1/memory_stores/$store_id/archive" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: agent-memory-2026-07-22" > /dev/null

bash CLI
  ant beta:memory-stores archive --memory-store-id "$store_id"

python Python
  client.beta.memory_stores.archive(store.id)

typescript TypeScript
  await client.beta.memoryStores.archive(store.id);

csharp C#
  await client.Beta.MemoryStores.Archive(store.ID);

go Go
  _, err = client.Beta.MemoryStores.Archive(ctx, store.ID, anthropic.BetaMemoryStoreArchiveParams{})
  if err != nil {
  	panic(err)
  }

java Java
  client.beta().memoryStores().archive(store.id());

php PHP
  $client->beta->memoryStores->archive($store->id);

ruby Ruby
  client.beta.memory_stores.archive(store.id)
  ```
</CodeGroup>

See the [Archive a memory store reference](https://platform.claude.com/docs/en/api/beta/memory_stores/archive) for full parameters and response schema.

To permanently remove a store along with all of its memories and versions, use [`memory_stores.delete`](https://platform.claude.com/docs/en/api/beta/memory_stores/delete).


## Best practices for memory management

Source: https://platform.claude.com/llms-full.txt#best-practices-for-memory-management

When a store reaches its 10,000-memory limit, writes to new memories fail: both direct `memories.create` calls and the agent's file writes to unmapped paths. Existing memories remain readable and editable. The following practices help you stay well under the limit and recover gracefully if you reach it.

* **Use focused stores.** Rather than one large general-purpose store, use smaller purpose-built stores: one per user, one for shared domain knowledge, and one for project-specific context. Each store has its own 10,000-memory limit, so keeping stores scoped reduces the chance any single one fills up.

* **Condense or prune before the store fills up.** Delete stale or redundant memories with `memories.delete`. You can also run a [dreaming session](https://platform.claude.com/docs/en/managed-agents/dreams), which consolidates fragmented content into a separate new output store rather than modifying the original. Switch your sessions over to that output store, then archive or delete the original.

* **Attach a new store when it makes sense.** If a store has grown beyond its useful scope, attach a fresh one for new content and attach the original with `read_only` access. The agent can read from both while only writing to the new one.

* **Limit write access where appropriate.** Sessions that only read shared reference material don't need `read_write`. Keeping write access scoped to sessions that actually add new memories makes it easier to track where growth is coming from.


### Advanced orchestration

---
title: Multiagent orchestration
url: https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration
description: Coordinate multiple agents within a single session.
---

Multiagent orchestration lets one agent coordinate with others to complete complex work. Agents can act in parallel with their own isolated context, which helps improve output quality and can also improve time to completion.

Not sure a multiagent setup fits your problem? See [when to use multiagent systems (and when not to)](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them).

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## How it works

Source: https://platform.claude.com/llms-full.txt#how-it-works-10

All agents share the same sandbox, filesystem, and [vault credentials](https://platform.claude.com/docs/en/managed-agents/vaults), but each agent runs in its own **session thread**, a context-isolated event stream with its own conversation history. The coordinator reports activity in the **primary thread** (which is the same as the session-level [event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming)); additional threads are spawned at runtime when the coordinator delegates work.

Threads are persistent: the coordinator can send a follow-up to an agent it called earlier, and that agent retains everything from its previous turns.

Each agent uses its own configuration: model, system prompt, tools, MCP servers, and skills. Session-level [agent configuration overrides](https://platform.claude.com/docs/en/managed-agents/sessions#override-agent-configuration-for-a-session) are the exception; they apply to the coordinator and its `self` copies. Tools, MCP servers, and context are not shared.

### What to delegate

Multiagent coordination is best suited for complex tasks that either require work across a variety of surfaces, or where multiple well-scoped tasks contribute to an overall goal.

Patterns that work well:

* **Parallelization:** Fan out independent subtasks simultaneously (searching multiple sources, analyzing separate files) and have the coordinator synthesize the results.
* **Specialization:** Route to agents with domain-focused system prompts and tools, such as a security agent or a documentation agent, rather than loading a single agent with every capability.
* **Escalation:** Consult a more capable agent or model for a subset of complex subtasks.


## Configure the coordinator

Source: https://platform.claude.com/llms-full.txt#configure-the-coordinator

When [defining your agent](https://platform.claude.com/docs/en/managed-agents/agent-setup), set `multiagent` to declare the roster of agents the coordinator can delegate to:

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  coordinator=$(curl -fsS https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "name": "Engineering Lead",
    "model": "claude-opus-5",
    "system": "You coordinate engineering work. Delegate code review to the reviewer agent and test writing to the test agent.",
    "tools": [
      {
        "type": "agent_toolset_20260401"
      }
    ],
    "multiagent": {
      "type": "coordinator",
      "agents": [
        {"type": "agent", "id": "$REVIEWER_AGENT_ID"},
        {"type": "agent", "id": "$TEST_WRITER_AGENT_ID"}
      ]
    }
  }
  EOF
  )

bash CLI
    ant beta:agents create < coordinator.agent.yaml

yaml
      name: Engineering Lead
      model: claude-opus-5
      system: You coordinate engineering work. Delegate code review to the reviewer agent and test writing to the test agent.
      tools:
        - type: agent_toolset_20260401
      multiagent:
        type: coordinator
        agents:
          - type: agent
            id: $REVIEWER_AGENT_ID # replace before running command
          - type: agent
            id: $TEST_WRITER_AGENT_ID # replace before running command

python Python
  coordinator = client.beta.agents.create(
      name="Engineering Lead",
      model="claude-opus-5",
      system="You coordinate engineering work. Delegate code review to the reviewer agent and test writing to the test agent.",
      tools=[
          {"type": "agent_toolset_20260401"},
      ],
      multiagent={
          "type": "coordinator",
          "agents": [
              {"type": "agent", "id": reviewer_agent.id},
              {"type": "agent", "id": test_writer_agent.id},
          ],
      },
  )

typescript TypeScript
  const coordinator = await client.beta.agents.create({
    name: "Engineering Lead",
    model: "claude-opus-5",
    system:
      "You coordinate engineering work. Delegate code review to the reviewer agent and test writing to the test agent.",
    tools: [{ type: "agent_toolset_20260401" }],
    multiagent: {
      type: "coordinator",
      agents: [
        { type: "agent", id: reviewerAgent.id },
        { type: "agent", id: testWriterAgent.id },
      ],
    },
  });

csharp C#
  var coordinator = await client.Beta.Agents.Create(new()
  {
      Name = "Engineering Lead",
      Model = BetaManagedAgentsModel.ClaudeOpus5,
      System = "You coordinate engineering work. Delegate code review to the reviewer agent and test writing to the test agent.",
      Tools =
      [
          new BetaManagedAgentsAgentToolset20260401Params
          {
              Type = BetaManagedAgentsAgentToolset20260401ParamsType.AgentToolset20260401,
          },
      ],
      Multiagent = new BetaManagedAgentsMultiagentParams
      {
          Type = BetaManagedAgentsMultiagentParamsType.Coordinator,
          Agents = [reviewerAgent.ID, testWriterAgent.ID],
      },
  });

go Go
  coordinator, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name:   "Engineering Lead",
  	Model:  anthropic.BetaManagedAgentsModelConfigParams{ID: anthropic.BetaManagedAgentsModelClaudeOpus5},
  	System: anthropic.String("You coordinate engineering work. Delegate code review to the reviewer agent and test writing to the test agent."),
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{{
  		OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  			Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  		},
  	}},
  	Multiagent: anthropic.BetaManagedAgentsMultiagentParams{
  		Type: anthropic.BetaManagedAgentsMultiagentParamsTypeCoordinator,
  		Agents: []anthropic.BetaManagedAgentsMultiagentRosterEntryParamsUnion{
  			{OfString: anthropic.String(reviewerAgent.ID)},
  			{OfString: anthropic.String(testWriterAgent.ID)},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  var coordinator = client.beta().agents().create(
      AgentCreateParams.builder()
          .name("Engineering Lead")
          .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
          .system("You coordinate engineering work. Delegate code review to the reviewer agent and test writing to the test agent.")
          .addTool(
              BetaManagedAgentsAgentToolset20260401Params.builder()
                  .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
                  .build()
          )
          .multiagent(BetaManagedAgentsMultiagentParams.builder()
              .type(BetaManagedAgentsMultiagentParams.Type.COORDINATOR)
              .addAgent(BetaManagedAgentsAgentParams.builder()
                  .type(BetaManagedAgentsAgentParams.Type.AGENT)
                  .id(reviewerAgent.id())
                  .build())
              .addAgent(BetaManagedAgentsAgentParams.builder()
                  .type(BetaManagedAgentsAgentParams.Type.AGENT)
                  .id(testWriterAgent.id())
                  .build())
              .build())
          .build()
  );

php PHP
  $coordinator = $client->beta->agents->create(
      name: 'Engineering Lead',
      model: 'claude-opus-5',
      system: 'You coordinate engineering work. Delegate code review to the reviewer agent and test writing to the test agent.',
      tools: [
          ['type' => 'agent_toolset_20260401'],
      ],
      multiagent: [
          'type' => 'coordinator',
          'agents' => [
              ['type' => 'agent', 'id' => $reviewerAgent->id],
              ['type' => 'agent', 'id' => $testWriterAgent->id],
          ],
      ],
  );

ruby Ruby
  coordinator = client.beta.agents.create(
    name: "Engineering Lead",
    model: "claude-opus-5",
    system: "You coordinate engineering work. Delegate code review to the reviewer agent and test writing to the test agent.",
    tools: [
      {type: "agent_toolset_20260401"}
    ],
    multiagent: {
      type: "coordinator",
      agents: [
        {type: "agent", id: reviewer_agent.id},
        {type: "agent", id: test_writer_agent.id}
      ]
    }
  )

bash cURL
curl -fsS https://api.anthropic.com/v1/agents \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  -d '{
    "name": "Backend engineer",
    "model": "claude-sonnet-5",
    "system": "You implement backend features end to end. Consult the advisor before major backend design decisions.",
    "multiagent": {
      "type": "coordinator",
      "agents": [
        {"type": "advisor", "model": "claude-opus-5"}
      ]
    }
  }'
```

A roster can contain at most one advisor entry, alongside any of the other roster forms. The entry occupies the reserved roster name `anthropic.advisor`: a roster that lists both an advisor entry and a member literally named `anthropic.advisor` is rejected with a 400 validation error. In responses, the advisor entry is echoed last in the roster regardless of the position it was submitted in.

The advisor model must meet a minimum capability bar, and the agent's own model must not be more capable than its advisor; models of equal capability can pair. An invalid pairing is rejected with a 400 validation error when the agent is saved. Valid pairings follow the advisor tool's [model compatibility](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#model-compatibility) table.

The advisor is also available as a [server tool on the Messages API](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool). The Managed Agents surface differs in configuration and delivery: the roster entry has no `max_uses`, `max_tokens`, or `caching` fields, and advice arrives through thread events rather than `advisor_tool_result` blocks.

#### How consultations work

Each consultation runs as a platform-spawned thread named `anthropic.advisor` that terminates itself when the consultation completes, and the advice is delivered to the primary thread as an `agent.thread_message_received` event. A consultation emits the standard thread events, identified by the reserved name `anthropic.advisor` (the thread lifecycle events carry it as `agent_name`, and the advice delivery carries it as `from_agent_name`), typically in this order:

1. `session.thread_created`
2. `session.thread_status_running`
3. `agent.thread_message_received` (the advice)
4. `session.thread_status_idle` (`stop_reason: end_turn`)
5. `session.thread_status_terminated`

No `agent.tool_use` events are emitted for a consultation, and no `agent.thread_message_sent` event appears on the session's event stream, because the consultation input is composed by the platform rather than sent by the agent. If you list the advisor thread's own events, the advice also appears there as an `agent.thread_message_sent` event. The advice delivery (event 3) is not guaranteed to arrive before the advisor thread's idle and terminated events, so don't treat those as a signal that the advice has already been delivered.

Whether your client can read the advice is the advisor model's policy, and it mirrors the [result variants](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#result-variants) split on the Messages API advisor tool. Advisor models that return plaintext results there deliver the advice as readable text content here; advisor models that return redacted results there deliver a `[{"type": "redacted"}]` placeholder as the message content on every client surface, while the agent itself still reads the full advice server-side. In the preceding example, Claude Opus 5 is a redacted-result advisor, so your client sees the placeholder while the agent reads the full advice; choose Claude Opus 4.8 as the advisor instead if you want the advice readable on the event stream. Advisor thinking is never surfaced. Clients cannot send `redacted` blocks themselves; an event containing one is rejected with a 400 validation error.

A failed or interrupted consultation never fails the agent's turn: the agent continues after a generic notice that the consultation failed. A session-level `user.interrupt` during a consultation terminates the advisor thread with no advice delivered; a `user.interrupt` with the advisor thread's `session_thread_id` abandons only that consultation.

#### Advisor threads

The advisor is not a roster agent: it is invisible to the coordinator's `list_agents` tool, it cannot be messaged with `send_to_agent`, and only the session's primary thread can consult it. Roster agents cannot.

Advisor threads are exempt from the concurrent-thread limit. They appear in the session's [thread list](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration#threads) with `agent` set to the advisor form exactly as configured (`{"type": "advisor", "model": ...}`) and `parent_thread_id` set to the primary thread.

Prompt caching on the advisor's side is automatic; there is nothing to configure. Consultations are billed at the advisor model's rates, and their tokens appear in the advisor thread's usage and in the session's usage totals.

#### Removing the advisor

To remove the advisor, [update the agent](https://platform.claude.com/docs/en/managed-agents/agent-setup#update-an-agent) with a roster that no longer includes the advisor entry. If the advisor is the roster's only entry, clear the roster entirely by setting `"multiagent": null`.


## Create the session

Source: https://platform.claude.com/llms-full.txt#create-the-session

Create a session referencing the coordinator. The coordinator delegates to the agents in its roster as needed.

<CodeGroup>
  ```bash cURL
  session=$(curl -fsSL https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "agent": "$COORDINATOR_ID",
    "environment_id": "$ENVIRONMENT_ID"
  }
  EOF
  )
  SESSION_ID=$(jq -r '.id' <<< "$session")

bash CLI
  ant beta:sessions create \
    --agent "$COORDINATOR_ID" \
    --environment-id "$ENVIRONMENT_ID"

python Python
  session = client.beta.sessions.create(
      agent=coordinator.id,
      environment_id=environment.id,
  )

typescript TypeScript
  const session = await client.beta.sessions.create({
    agent: coordinator.id,
    environment_id: environment.id,
  });

csharp C#
  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = coordinator.ID,
      EnvironmentID = environment.ID,
  });

go Go
  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfString: anthropic.String(coordinator.ID),
  	},
  	EnvironmentID: environment.ID,
  })
  if err != nil {
  	panic(err)
  }

java Java
  var session = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(coordinator.id())
      .environmentId(environment.id())
      .build());

php PHP
  $session = $client->beta->sessions->create(
      agent: $coordinator->id,
      environmentID: $environment->id,
  );

ruby Ruby
  session = client.beta.sessions.create(
    agent: coordinator.id,
    environment_id: environment.id
  )
  ```
</CodeGroup>


## Connect agents to MCP servers

Source: https://platform.claude.com/llms-full.txt#connect-agents-to-mcp-servers

MCP servers are agent-scoped (each agent definition declares its own servers and tools), while vault credentials are session-scoped (`vault_ids` passed at session creation apply to every thread). Two implications for your integration:

* To authenticate MCP servers, include a vault credential for every MCP server used across all agents.
* To limit an agent's access, declare only the servers it needs in its agent definition.

[Agent configuration overrides](https://platform.claude.com/docs/en/managed-agents/sessions#override-agent-configuration-for-a-session) at session creation can replace the coordinator's MCP servers and those of its `self` copies.

<CodeGroup>
  ```bash cURL
  research_agent_id=$(curl --fail-with-body -sS "$BASE/v1/agents" "${H[@]}" --data @- <<'EOF' | jq -er '.id'
  {
    "name": "researcher",
    "model": "claude-haiku-4-5",
    "mcp_servers": [{"type": "url", "name": "github", "url": "https://api.githubcopilot.com/mcp/"}],
    "tools": [{"type": "mcp_toolset", "mcp_server_name": "github"}]
  }
  EOF
  )

  coordinator_id=$(curl --fail-with-body -sS "$BASE/v1/agents" "${H[@]}" --data @- <<EOF | jq -er '.id'
  {
    "name": "coordinator",
    "model": "claude-opus-5",
    "tools": [{"type": "agent_toolset_20260401"}],
    "multiagent": {
      "type": "coordinator",
      "agents": [{"type": "agent", "id": "$research_agent_id"}]
    }
  }
  EOF
  )

  session_id=$(curl --fail-with-body -sS "$BASE/v1/sessions" "${H[@]}" --data @- <<EOF | jq -er '.id'
  {
    "agent": "$coordinator_id",
    "environment_id": "$environment_id",
    "vault_ids": ["$vault_id"]
  }
  EOF
  )
  echo "$session_id"

bash CLI
    research_agent_id=$(ant beta:agents create --transform id --raw-output < researcher.agent.yaml)

yaml
      name: researcher
      model: claude-haiku-4-5
      mcp_servers:
        - type: url
          name: github
          url: https://api.githubcopilot.com/mcp/
      tools:
        - type: mcp_toolset
          mcp_server_name: github

yaml
      name: coordinator
      model: claude-opus-5
      tools:
        - type: agent_toolset_20260401
      multiagent:
        type: coordinator
        agents:
          - type: agent
            id: $research_agent_id # replace before running command

bash CLI
    coordinator_id=$(ant beta:agents create --transform id --raw-output < subagent-coordinator.agent.yaml)

    session_id=$(ant beta:sessions create \
      --agent "$coordinator_id" \
      --environment-id "$environment_id" \
      --vault-id "$vault_id" \
      --transform id --raw-output)
    echo "$session_id"

python Python
  research_agent = client.beta.agents.create(
      name="researcher",
      model="claude-haiku-4-5",
      mcp_servers=[
          {"type": "url", "name": "github", "url": "https://api.githubcopilot.com/mcp/"},
      ],
      tools=[{"type": "mcp_toolset", "mcp_server_name": "github"}],
  )

  coordinator = client.beta.agents.create(
      name="coordinator",
      model="claude-opus-5",
      tools=[{"type": "agent_toolset_20260401"}],
      multiagent={
          "type": "coordinator",
          "agents": [{"type": "agent", "id": research_agent.id}],
      },
  )

  session = client.beta.sessions.create(
      agent=coordinator.id,
      environment_id=environment.id,
      vault_ids=[vault.id],
  )
  print(session.id)

typescript TypeScript
  const researchAgent = await client.beta.agents.create({
    name: "researcher",
    model: "claude-haiku-4-5",
    mcp_servers: [
      { type: "url", name: "github", url: "https://api.githubcopilot.com/mcp/" },
    ],
    tools: [{ type: "mcp_toolset", mcp_server_name: "github" }],
  });

  const coordinator = await client.beta.agents.create({
    name: "coordinator",
    model: "claude-opus-5",
    tools: [{ type: "agent_toolset_20260401" }],
    multiagent: {
      type: "coordinator",
      agents: [{ type: "agent", id: researchAgent.id }],
    },
  });

  const session = await client.beta.sessions.create({
    agent: coordinator.id,
    environment_id: environment.id,
    vault_ids: [vault.id],
  });
  console.log(session.id);

csharp C#
  var researchAgent = await client.Beta.Agents.Create(new()
  {
      Name = "researcher",
      Model = BetaManagedAgentsModel.ClaudeHaiku4_5,
      McpServers =
      [
          new()
          {
              Type = BetaManagedAgentsUrlMcpServerParamsType.Url,
              Name = "github",
              Url = "https://api.githubcopilot.com/mcp/",
          },
      ],
      Tools =
      [
          new BetaManagedAgentsMcpToolsetParams
          {
              Type = BetaManagedAgentsMcpToolsetParamsType.McpToolset,
              McpServerName = "github",
          },
      ],
  });

  var coordinator = await client.Beta.Agents.Create(new()
  {
      Name = "coordinator",
      Model = BetaManagedAgentsModel.ClaudeOpus5,
      Tools =
      [
          new BetaManagedAgentsAgentToolset20260401Params
          {
              Type = BetaManagedAgentsAgentToolset20260401ParamsType.AgentToolset20260401,
          },
      ],
      Multiagent = new()
      {
          Type = BetaManagedAgentsMultiagentParamsType.Coordinator,
          Agents =
          [
              new BetaManagedAgentsAgentParams
              {
                  Type = BetaManagedAgentsAgentParamsType.Agent,
                  ID = researchAgent.ID,
              },
          ],
      },
  });

  var session = await client.Beta.Sessions.Create(new()
  {
      Agent = coordinator.ID,
      EnvironmentID = environment.ID,
      VaultIds = [vault.ID],
  });
  Console.WriteLine(session.ID);

go Go
  researcher, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name:  "researcher",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{ID: anthropic.BetaManagedAgentsModelClaudeHaiku4_5},
  	MCPServers: []anthropic.BetaManagedAgentsURLMCPServerParams{{
  		Type: anthropic.BetaManagedAgentsURLMCPServerParamsTypeURL,
  		Name: "github",
  		URL:  "https://api.githubcopilot.com/mcp/",
  	}},
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{{
  		OfMCPToolset: &anthropic.BetaManagedAgentsMCPToolsetParams{
  			Type:          anthropic.BetaManagedAgentsMCPToolsetParamsTypeMCPToolset,
  			MCPServerName: "github",
  		},
  	}},
  })
  if err != nil {
  	panic(err)
  }

  coordinator, err := client.Beta.Agents.New(ctx, anthropic.BetaAgentNewParams{
  	Name:  "coordinator",
  	Model: anthropic.BetaManagedAgentsModelConfigParams{ID: anthropic.BetaManagedAgentsModelClaudeOpus5},
  	Tools: []anthropic.BetaAgentNewParamsToolUnion{{
  		OfAgentToolset20260401: &anthropic.BetaManagedAgentsAgentToolset20260401Params{
  			Type: anthropic.BetaManagedAgentsAgentToolset20260401ParamsTypeAgentToolset20260401,
  		},
  	}},
  	Multiagent: anthropic.BetaManagedAgentsMultiagentParams{
  		Type: anthropic.BetaManagedAgentsMultiagentParamsTypeCoordinator,
  		Agents: []anthropic.BetaManagedAgentsMultiagentRosterEntryParamsUnion{{
  			OfBetaManagedAgentsAgents: &anthropic.BetaManagedAgentsAgentParams{
  				Type: anthropic.BetaManagedAgentsAgentParamsTypeAgent,
  				ID:   researcher.ID,
  			},
  		}},
  	},
  })
  if err != nil {
  	panic(err)
  }

  session, err := client.Beta.Sessions.New(ctx, anthropic.BetaSessionNewParams{
  	Agent: anthropic.BetaSessionNewParamsAgentUnion{
  		OfString: anthropic.String(coordinator.ID),
  	},
  	EnvironmentID: environment.ID,
  	VaultIDs:      []string{vault.ID},
  })
  if err != nil {
  	panic(err)
  }
  fmt.Println(session.ID)

java Java
  var researcher = client.beta().agents().create(
      AgentCreateParams.builder()
          .name("researcher")
          .model(BetaManagedAgentsModel.CLAUDE_HAIKU_4_5)
          .addMcpServer(BetaManagedAgentsUrlMcpServerParams.builder()
              .name("github")
              .type(BetaManagedAgentsUrlMcpServerParams.Type.URL)
              .url("https://api.githubcopilot.com/mcp/")
              .build())
          .addTool(BetaManagedAgentsMcpToolsetParams.builder()
              .type(BetaManagedAgentsMcpToolsetParams.Type.MCP_TOOLSET)
              .mcpServerName("github")
              .build())
          .build()
  );

  var coordinator = client.beta().agents().create(
      AgentCreateParams.builder()
          .name("coordinator")
          .model(BetaManagedAgentsModel.CLAUDE_OPUS_5)
          .addTool(BetaManagedAgentsAgentToolset20260401Params.builder()
              .type(BetaManagedAgentsAgentToolset20260401Params.Type.AGENT_TOOLSET_20260401)
              .build())
          .multiagent(BetaManagedAgentsMultiagentParams.builder()
              .type(BetaManagedAgentsMultiagentParams.Type.COORDINATOR)
              .addAgent(BetaManagedAgentsAgentParams.builder()
                  .type(BetaManagedAgentsAgentParams.Type.AGENT)
                  .id(researcher.id())
                  .build())
              .build())
          .build()
  );

  var session = client.beta().sessions().create(SessionCreateParams.builder()
      .agent(coordinator.id())
      .environmentId(environment.id())
      .vaultIds(List.of(vault.id()))
      .build());
  IO.println(session.id());

php PHP
  $researchAgent = $client->beta->agents->create(
      name: 'researcher',
      model: 'claude-haiku-4-5',
      mcpServers: [
          ['type' => 'url', 'name' => 'github', 'url' => 'https://api.githubcopilot.com/mcp/'],
      ],
      tools: [
          ['type' => 'mcp_toolset', 'mcp_server_name' => 'github'],
      ],
  );

  $coordinator = $client->beta->agents->create(
      name: 'coordinator',
      model: 'claude-opus-5',
      tools: [
          ['type' => 'agent_toolset_20260401'],
      ],
      multiagent: [
          'type' => 'coordinator',
          'agents' => [
              ['type' => 'agent', 'id' => $researchAgent->id],
          ],
      ],
  );

  $session = $client->beta->sessions->create(
      agent: $coordinator->id,
      environmentID: $environment->id,
      vaultIDs: [$vault->id],
  );
  echo "{$session->id}\n";

ruby Ruby
  research_agent = client.beta.agents.create(
    name: "researcher",
    model: "claude-haiku-4-5",
    mcp_servers: [
      {type: "url", name: "github", url: "https://api.githubcopilot.com/mcp/"}
    ],
    tools: [
      {type: "mcp_toolset", mcp_server_name: "github"}
    ]
  )

  coordinator = client.beta.agents.create(
    name: "coordinator",
    model: "claude-opus-5",
    tools: [
      {type: "agent_toolset_20260401"}
    ],
    multiagent: {
      type: "coordinator",
      agents: [
        {type: "agent", id: research_agent.id}
      ]
    }
  )

  session = client.beta.sessions.create(
    agent: coordinator.id,
    environment_id: environment.id,
    vault_ids: [vault.id]
  )
  puts session.id
  ```
</CodeGroup>

In this example, only the researcher declares the GitHub MCP server, so the coordinator does not have access. The session's `vault_ids` supply the GitHub credential to the researcher's thread.

<Tip>
  If an agent's MCP calls fail to authenticate after you declare the server, confirm the credential's `mcp_server_url` refers to the same server as the agent's `mcp_servers[].url`. Both URLs are normalized before matching (scheme and host lowercased, default ports and trailing slashes stripped), so differences in host casing, a default port, or a trailing slash don't prevent a match; a different path, subdomain, or non-default port does.
</Tip>


## Threads

Source: https://platform.claude.com/llms-full.txt#threads

The **session-level event stream** (`/v1/sessions/{session_id}/events/stream`) is considered the **primary thread**, containing a condensed view of all activity across all threads. You don't see the full activity from subagents, but you do see the start and end of their work, and blocking events such as tool permission requests.

**Session threads** are where you drill into a specific agent's activity.

The session `status` is an aggregation of all agent activity; if at least one thread is `running`, then the overall session status is `running` as well.

A [session budget](https://platform.claude.com/docs/en/managed-agents/budgets) is a single shared cap across all of a session's threads. As the cap is reached, threads pause independently, and each thread's cost is priced at the thread's own served model.

<Note>
  A maximum of 25 concurrent threads is supported. The coordinator can call multiple copies of a single agent in the roster, creating multiple threads associated with one `agent`. [Advisor](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration#give-the-session-an-advisor) consultation threads are exempt from this limit.
</Note>

<Tabs>
  <Tab title="List threads">
    List all threads associated with a session as follows:

    <CodeGroup>
      ```bash cURL
      curl -fsS "https://api.anthropic.com/v1/sessions/$SESSION_ID/threads" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        | jq -r '.data[] | "[\(.agent.name)] \(.status)"'

bash CLI
      ant beta:sessions:threads list --session-id "$SESSION_ID"

python Python
      for thread in client.beta.sessions.threads.list(session.id):
          print(f"[{thread.agent.name}] {thread.status}")

typescript TypeScript
      for await (const thread of client.beta.sessions.threads.list(session.id)) {
        console.log(`[${thread.agent.name}] ${thread.status}`);
      }

csharp C#
      await foreach (var thread in (await client.Beta.Sessions.Threads.List(session.ID)).Paginate())
      {
          Console.WriteLine($"[{thread.Agent.Name}] {thread.Status}");
      }

go Go
      threads := client.Beta.Sessions.Threads.ListAutoPaging(ctx, session.ID, anthropic.BetaSessionThreadListParams{})
      for threads.Next() {
      	thread := threads.Current()
      	fmt.Printf("[%s] %s\n", thread.Agent.Name, thread.Status)
      }
      if err := threads.Err(); err != nil {
      	panic(err)
      }

java Java
      for (var thread : client.beta().sessions().threads().list(session.id()).autoPager()) {
          var name = thread.agent().isAgent() ? thread.agent().asAgent().name() : "advisor";
          IO.println("[" + name + "] " + thread.status());
      }

php PHP
      foreach ($client->beta->sessions->threads->list($session->id)->pagingEachItem() as $thread) {
          echo "[{$thread->agent->name}] {$thread->status}\n";
      }

ruby Ruby
      client.beta.sessions.threads.list(session.id).auto_paging_each do |thread|
        puts "[#{thread.agent.name}] #{thread.status}"
      end

bash cURL
      curl -fsS "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        -H "content-type: application/json" \
        -d "{\"events\": [{\"type\": \"user.interrupt\", \"session_thread_id\": \"$THREAD_ID\"}]}"

bash CLI
      ant beta:sessions:events send \
        --session-id "$SESSION_ID" \
        --event "{type: user.interrupt, session_thread_id: $THREAD_ID}"

python Python
      client.beta.sessions.events.send(
          session.id,
          events=[{"type": "user.interrupt", "session_thread_id": thread.id}],
      )

typescript TypeScript
      await client.beta.sessions.events.send(session.id, {
        events: [{ type: "user.interrupt", session_thread_id: thread.id }],
      });

csharp C#
      await client.Beta.Sessions.Events.Send(session.ID, new()
      {
          Events =
          [
              new BetaManagedAgentsUserInterruptEventParams
              {
                  Type = BetaManagedAgentsUserInterruptEventParamsType.UserInterrupt,
                  SessionThreadID = thread.ID,
              },
          ],
      });

go Go
      if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
      	Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
      		OfUserInterrupt: &anthropic.BetaManagedAgentsUserInterruptEventParams{
      			Type:            anthropic.BetaManagedAgentsUserInterruptEventParamsTypeUserInterrupt,
      			SessionThreadID: anthropic.String(thread.ID),
      		},
      	}},
      }); err != nil {
      	panic(err)
      }

java Java
      client.beta().sessions().events().send(
          session.id(),
          EventSendParams.builder()
              .addEvent(BetaManagedAgentsUserInterruptEventParams.builder()
                  .type(BetaManagedAgentsUserInterruptEventParams.Type.USER_INTERRUPT)
                  .sessionThreadId(thread.id())
                  .build())
              .build());

php PHP
      $client->beta->sessions->events->send(
          $session->id,
          events: [
              ['type' => 'user.interrupt', 'session_thread_id' => $thread->id],
          ],
      );

ruby Ruby
      client.beta.sessions.events.send_(
        session.id,
        events: [{type: "user.interrupt", session_thread_id: thread.id}]
      )

bash cURL
      curl -fsS -X POST "https://api.anthropic.com/v1/sessions/$SESSION_ID/threads/$THREAD_ID/archive" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
      ant beta:sessions:threads archive \
        --session-id "$SESSION_ID" \
        --thread-id "$THREAD_ID"

python Python
      archived = client.beta.sessions.threads.archive(thread.id, session_id=session.id)
      print(archived.status, archived.archived_at)

typescript TypeScript
      const archived = await client.beta.sessions.threads.archive(thread.id, {
        session_id: session.id,
      });
      console.log(archived.status, archived.archived_at);

csharp C#
      var archived = await client.Beta.Sessions.Threads.Archive(thread.ID, new() { SessionID = session.ID });
      Console.WriteLine($"{archived.Status} {archived.ArchivedAt}");

go Go
      archived, err := client.Beta.Sessions.Threads.Archive(ctx, thread.ID, anthropic.BetaSessionThreadArchiveParams{
      	SessionID: session.ID,
      })
      if err != nil {
      	panic(err)
      }
      fmt.Println(archived.Status, archived.ArchivedAt)

java Java
      var archived = client.beta().sessions().threads().archive(
          thread.id(),
          ThreadArchiveParams.builder()
              .sessionId(session.id())
              .build());
      IO.println(archived.status() + " " + archived.archivedAt().orElseThrow());

php PHP
      $archived = $client->beta->sessions->threads->archive($thread->id, sessionID: $session->id);
      echo "{$archived->status} {$archived->archivedAt->format(DATE_ATOM)}\n";

ruby Ruby
      archived = client.beta.sessions.threads.archive(thread.id, session_id: session.id)
      puts "#{archived.status} #{archived.archived_at}"

bash cURL
      # Interrupt the thread, then archive it
      curl -fsS "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        -H "content-type: application/json" \
        -d "{\"events\": [{\"type\": \"user.interrupt\", \"session_thread_id\": \"$THREAD_ID\"}]}"

      curl -fsS -X POST "https://api.anthropic.com/v1/sessions/$SESSION_ID/threads/$THREAD_ID/archive" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
      ant beta:sessions:events send \
        --session-id "$SESSION_ID" \
        --event "{type: user.interrupt, session_thread_id: $THREAD_ID}"

      ant beta:sessions:threads archive \
        --session-id "$SESSION_ID" \
        --thread-id "$THREAD_ID"

python Python
      client.beta.sessions.events.send(
          session.id,
          events=[{"type": "user.interrupt", "session_thread_id": thread.id}],
      )
      archived = client.beta.sessions.threads.archive(thread.id, session_id=session.id)
      print(archived.status, archived.archived_at)

typescript TypeScript
      await client.beta.sessions.events.send(session.id, {
        events: [{ type: "user.interrupt", session_thread_id: thread.id }],
      });
      const archived = await client.beta.sessions.threads.archive(thread.id, {
        session_id: session.id,
      });
      console.log(archived.status, archived.archived_at);

csharp C#
      await client.Beta.Sessions.Events.Send(session.ID, new()
      {
          Events =
          [
              new BetaManagedAgentsUserInterruptEventParams
              {
                  Type = BetaManagedAgentsUserInterruptEventParamsType.UserInterrupt,
                  SessionThreadID = thread.ID,
              },
          ],
      });
      archived = await client.Beta.Sessions.Threads.Archive(thread.ID, new() { SessionID = session.ID });
      Console.WriteLine($"{archived.Status} {archived.ArchivedAt}");

go Go
      if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
      	Events: []anthropic.BetaManagedAgentsEventParamsUnion{{
      		OfUserInterrupt: &anthropic.BetaManagedAgentsUserInterruptEventParams{
      			Type:            anthropic.BetaManagedAgentsUserInterruptEventParamsTypeUserInterrupt,
      			SessionThreadID: anthropic.String(thread.ID),
      		},
      	}},
      }); err != nil {
      	panic(err)
      }

      archived, err := client.Beta.Sessions.Threads.Archive(ctx, thread.ID, anthropic.BetaSessionThreadArchiveParams{
      	SessionID: session.ID,
      })
      if err != nil {
      	panic(err)
      }
      fmt.Println(archived.Status, archived.ArchivedAt)

java Java
      client.beta().sessions().events().send(
          session.id(),
          EventSendParams.builder()
              .addEvent(BetaManagedAgentsUserInterruptEventParams.builder()
                  .type(BetaManagedAgentsUserInterruptEventParams.Type.USER_INTERRUPT)
                  .sessionThreadId(thread.id())
                  .build())
              .build());

      archived = client.beta().sessions().threads().archive(
          thread.id(),
          ThreadArchiveParams.builder()
              .sessionId(session.id())
              .build());
      IO.println(archived.status() + " " + archived.archivedAt().orElseThrow());

php PHP
      $client->beta->sessions->events->send(
          $session->id,
          events: [['type' => 'user.interrupt', 'session_thread_id' => $thread->id]],
      );
      $archived = $client->beta->sessions->threads->archive($thread->id, sessionID: $session->id);
      echo "{$archived->status} {$archived->archivedAt->format(DATE_ATOM)}\n";

ruby Ruby
      client.beta.sessions.events.send_(
        session.id,
        events: [{type: "user.interrupt", session_thread_id: thread.id}]
      )
      archived = client.beta.sessions.threads.archive(thread.id, session_id: session.id)
      puts "#{archived.status} #{archived.archived_at}"

bash cURL
      curl -fsSN "https://api.anthropic.com/v1/sessions/$SESSION_ID/threads/$THREAD_ID/stream?beta=true" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" |
        while IFS= read -r line; do
          [[ $line == data:* ]] || continue
          json=${line#data: }
          case $(jq -r '.type' <<<"$json") in
            agent.message)
              printf '%s' "$(jq -j '.content[] | select(.type == "text") | .text' <<<"$json")"
              ;;
            session.thread_status_idle)
              break
              ;;
          esac
        done

bash CLI
      ant beta:sessions:threads:events stream \
        --session-id "$SESSION_ID" \
        --thread-id "$THREAD_ID"

python Python
      with client.beta.sessions.threads.events.stream(
          thread.id,
          session_id=session.id,
      ) as stream:
          for event in stream:
              match event.type:
                  case "agent.message":
                      for block in event.content:
                          if block.type == "text":
                              print(block.text, end="")
                  case "session.thread_status_idle":
                      break

typescript TypeScript
      const stream = await client.beta.sessions.threads.events.stream(thread.id, {
        session_id: session.id,
      });

      for await (const event of stream) {
        if (event.type === "agent.message") {
          for (const block of event.content) {
            if (block.type === "text") {
              process.stdout.write(block.text);
            }
          }
        } else if (event.type === "session.thread_status_idle") {
          break;
        }
      }

csharp C#
      await foreach (var evt in client.Beta.Sessions.Threads.Events.StreamStreaming(thread.ID, new() { SessionID = session.ID }))
      {
          if (evt.Value is BetaManagedAgentsAgentMessageEvent message)
          {
              foreach (var block in message.Content)
              {
                  if (block.Type == "text")
                  {
                      Console.Write(block.Text);
                  }
              }
          }
          else if (evt.Value is BetaManagedAgentsSessionThreadStatusIdleEvent)
          {
              break;
          }
      }

go Go
      	stream := client.Beta.Sessions.Threads.Events.StreamEvents(ctx, thread.ID, anthropic.BetaSessionThreadEventStreamParams{
      		SessionID: session.ID,
      	})
      	defer stream.Close()

      loop:
      	for stream.Next() {
      		event := stream.Current()
      		switch event.Type {
      		case "agent.message":
      			for _, block := range event.AsAgentMessage().Content {
      				if block.Type == "text" {
      					fmt.Print(block.Text)
      				}
      			}
      		case "session.thread_status_idle":
      			break loop
      		}
      	}
      	if err := stream.Err(); err != nil {
      		panic(err)
      	}

java Java
      try (var streamResponse = client.beta().sessions().threads().events().streamStreaming(
          thread.id(),
          EventStreamParams.builder().sessionId(session.id()).build()
      )) {
          for (var event : (Iterable<BetaManagedAgentsStreamSessionThreadEvents>) streamResponse.stream()::iterator) {
              if (event.isAgentMessage()) {
                  for (var block : event.asAgentMessage().content()) {
                      block.text().ifPresent(textBlock -> IO.print(textBlock.text()));
                  }
              } else if (event.isSessionThreadStatusIdle()) {
                  break;
              }
          }
      }

php PHP
      $stream = $client->beta->sessions->threads->events->streamStream(
          $thread->id,
          sessionID: $session->id,
      );

      foreach ($stream as $event) {
          if ($event->type === 'agent.message') {
              foreach ($event->content as $block) {
                  if ($block->type === 'text') {
                      echo $block->text;
                  }
              }
          } elseif ($event->type === 'session.thread_status_idle') {
              break;
          }
      }

ruby Ruby
      client.beta.sessions.threads.events.stream_events(thread.id, session_id: session.id).each do |event|
        case event.type
        when :"agent.message"
          event.content.each do |block|
            print block.text if block.type == :text
          end
        when :"session.thread_status_idle"
          break
        end
      end

bash cURL
      curl -fsS "https://api.anthropic.com/v1/sessions/$SESSION_ID/threads/$THREAD_ID/events" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        | jq -r '.data[] | "[\(.type)] \(.processed_at)"'

bash CLI
      ant beta:sessions:threads:events list \
        --session-id "$SESSION_ID" \
        --thread-id "$THREAD_ID"

python Python
      for event in client.beta.sessions.threads.events.list(
          thread.id,
          session_id=session.id,
      ):
          print(f"[{event.type}] {event.processed_at}")

typescript TypeScript
      for await (const event of client.beta.sessions.threads.events.list(thread.id, {
        session_id: session.id,
      })) {
        console.log(`[${event.type}] ${event.processed_at}`);
      }

csharp C#
      var page = await client.Beta.Sessions.Threads.Events.List(thread.ID, new() { SessionID = session.ID });
      await foreach (var evt in page.Paginate())
      {
          Console.WriteLine($"[{evt.Type}] {evt.ProcessedAt}");
      }

go Go
      pager := client.Beta.Sessions.Threads.Events.ListAutoPaging(ctx, thread.ID, anthropic.BetaSessionThreadEventListParams{
      	SessionID: session.ID,
      })
      for pager.Next() {
      	event := pager.Current()
      	fmt.Printf("[%s] %s\n", event.Type, event.ProcessedAt)
      }
      if err := pager.Err(); err != nil {
      	panic(err)
      }

java Java
      for (var event : client.beta().sessions().threads().events().list(
              thread.id(),
              EventListParams.builder().sessionId(session.id()).build()
          ).autoPager()) {
          var type = event._json().orElseThrow() instanceof JsonObject json
              ? json.values().get("type").asStringOrThrow()
              : "unknown";
          var processedAt = event.processedAt().map(OffsetDateTime::toString).orElse("pending");
          IO.println("[" + type + "] " + processedAt);
      }

php PHP
      foreach (
          $client->beta->sessions->threads->events->list(
              $thread->id,
              sessionID: $session->id,
          )->pagingEachItem() as $event
      ) {
          echo "[{$event->type}] {$event->processedAt->format(DATE_RFC3339)}\n";
      }

ruby Ruby
      client.beta.sessions.threads.events.list(
        thread.id,
        session_id: session.id
      ).auto_paging_each do |event|
        puts "[#{event.type}] #{event.processed_at}"
      end

json
{
  "type": "session.thread_status_idle",
  "id": "sevt_01ABC...",
  "session_thread_id": "sth_01DEF...",
  "agent_name": "code-reviewer",
  "stop_reason": {
    "type": "requires_action",
    "event_ids": ["sevt_01XYZ..."]
  }
}

bash cURL
  while IFS= read -r event_id; do
    jq -n --arg id "$event_id" \
      '{events: [{type: "user.tool_confirmation", tool_use_id: $id, result: "allow"}]}' |
      curl -fsS "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?beta=true" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "anthropic-beta: managed-agents-2026-04-01" \
        -H "content-type: application/json" \
        -d @-
  done < <(jq -r '.stop_reason.event_ids[]' <<<"$data")

bash CLI
  # This workflow does not translate well to a one-off shell command.
  # Use one of the SDK examples in this code group instead.

python Python
  for event_id in stop.event_ids:
      client.beta.sessions.events.send(
          session.id,
          events=[
              {
                  "type": "user.tool_confirmation",
                  "tool_use_id": event_id,
                  "result": "allow",
              }
          ],
      )

typescript TypeScript
  for (const eventId of stop.event_ids) {
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

csharp C#
  foreach (var eventId in requiresAction.EventIds)
  {
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

go Go
  for _, eventID := range stopReason.EventIDs {
  	params := anthropic.BetaManagedAgentsUserToolConfirmationEventParams{
  		Type:      anthropic.BetaManagedAgentsUserToolConfirmationEventParamsTypeUserToolConfirmation,
  		ToolUseID: eventID,
  		Result:    anthropic.BetaManagedAgentsUserToolConfirmationEventParamsResultAllow,
  	}
  	if _, err := client.Beta.Sessions.Events.Send(ctx, session.ID, anthropic.BetaSessionEventSendParams{
  		Events: []anthropic.BetaManagedAgentsEventParamsUnion{{OfUserToolConfirmation: &params}},
  	}); err != nil {
  		panic(err)
  	}
  }

java Java
  for (var eventId : pendingToolUseIds) {
      client.beta().sessions().events().send(
          session.id(),
          EventSendParams.builder()
              .addEvent(BetaManagedAgentsUserToolConfirmationEventParams.builder()
                  .toolUseId(eventId)
                  .result(BetaManagedAgentsUserToolConfirmationEventParams.Result.ALLOW)
                  .build())
              .build()
      );
  }

php PHP
  foreach ($event->stopReason->eventIDs as $eventId) {
      $client->beta->sessions->events->send($session->id, events: [[
          'type' => 'user.tool_confirmation',
          'tool_use_id' => $eventId,
          'result' => 'allow',
      ]]);
  }

ruby Ruby
  event_ids.each do |event_id|
    client.beta.sessions.events.send_(session.id, events: [{
      type: "user.tool_confirmation",
      tool_use_id: event_id,
      result: "allow"
    }])
  end
  ```
</CodeGroup>


---
title: Scheduled deployments
url: https://platform.claude.com/docs/en/managed-agents/scheduled-deployments
description: "Create and manage deployments with the Claude API: run an agent on a recurring cron schedule and inspect its run history."
---

A **scheduled deployment** allows an [agent](https://platform.claude.com/docs/en/managed-agents/agent-setup) to start [sessions](https://platform.claude.com/docs/en/managed-agents/sessions) autonomously, enabling task completion over a predictable cadence. You create and manage deployments with the Deployments API, part of the Claude API.

For the launch context and examples of what teams run on schedules, see [scheduled deployments and vaults in Claude Managed Agents](https://claude.com/blog/whats-new-in-claude-managed-agents) on the blog.

<Note>
  All Managed Agents API requests require the `managed-agents-2026-04-01` beta header. The SDK sets the beta header automatically.
</Note>


## Create a scheduled deployment

Source: https://platform.claude.com/llms-full.txt#create-a-scheduled-deployment

When creating a deployment, you pass the [session configurations](https://platform.claude.com/docs/en/managed-agents/sessions) required for execution, in addition to a `schedule`.

* Deployments require [agent configuration](https://platform.claude.com/docs/en/managed-agents/agent-setup) and [environment configuration](https://platform.claude.com/docs/en/managed-agents/environments), and optionally accept [files](https://platform.claude.com/docs/en/managed-agents/files), [GitHub](https://platform.claude.com/docs/en/managed-agents/github), [memory stores](https://platform.claude.com/docs/en/managed-agents/memory), and [vaults](https://platform.claude.com/docs/en/managed-agents/vaults). A deployment that targets a [self-hosted environment](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores) can attach memory stores; `file` and `github_repository` resources require a cloud environment. The Claude Console deployment form does not currently offer memory stores for self-hosted environments; attach them through the API or an SDK instead.
* Deployments also require at least one initial event, a `user.message` or `user.define_outcome`, that starts each session's work.
* In the `schedule`, you define a cron `expression` and a `timezone`. Maximum granularity supported is at the minute level.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  DEPLOYMENT_ID=$(
    curl --fail-with-body -sS "https://api.anthropic.com/v1/deployments?beta=true" \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "anthropic-beta: managed-agents-2026-04-01" \
      -H "content-type: application/json" \
      -d @- <<EOF | jq -er '.id'
  {
    "name": "Weekly compliance scan",
    "agent": "$AGENT_ID",
    "environment_id": "$ENVIRONMENT_ID",
    "initial_events": [
      {"type": "user.message", "content": [{"type": "text", "text": "Run the weekly compliance scan."}]}
    ],
    "schedule": {
      "type": "cron",
      "expression": "0 20 * * 5",
      "timezone": "America/New_York"
    }
  }
  EOF
  )

bash CLI
  DEPLOYMENT_ID=$(ant beta:deployments create <<YAML | jq -er '.id'
  name: Weekly compliance scan
  agent: $AGENT_ID
  environment_id: $ENVIRONMENT_ID
  initial_events:
    - type: user.message
      content:
        - type: text
          text: Run the weekly compliance scan.
  schedule:
    type: cron
    expression: "0 20 * * 5"
    timezone: America/New_York
  YAML
  )

python Python
  deployment = client.beta.deployments.create(
      name="Weekly compliance scan",
      agent=agent.id,
      environment_id=environment.id,
      initial_events=[
          {
              "type": "user.message",
              "content": [{"type": "text", "text": "Run the weekly compliance scan."}],
          },
      ],
      schedule={
          "type": "cron",
          "expression": "0 20 * * 5",
          "timezone": "America/New_York",
      },
  )

typescript TypeScript
  const deployment = await client.beta.deployments.create({
    name: "Weekly compliance scan",
    agent: agent.id,
    environment_id: environment.id,
    initial_events: [
      {
        type: "user.message",
        content: [{ type: "text", text: "Run the weekly compliance scan." }],
      },
    ],
    schedule: {
      type: "cron",
      expression: "0 20 * * 5",
      timezone: "America/New_York",
    },
  });

csharp C#
  var deployment = await client.Beta.Deployments.Create(new()
  {
      Name = "Weekly compliance scan",
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
                      Text = "Run the weekly compliance scan.",
                  },
              ],
          },
      ],
      Schedule = new BetaManagedAgentsScheduleParams
      {
          Type = BetaManagedAgentsScheduleParamsType.Cron,
          Expression = "0 20 * * 5",
          Timezone = "America/New_York",
      },
  });

go Go
  deployment, err := client.Beta.Deployments.New(ctx, anthropic.BetaDeploymentNewParams{
  	Name:          "Weekly compliance scan",
  	Agent:         anthropic.BetaDeploymentNewParamsAgentUnion{OfString: anthropic.String(agent.ID)},
  	EnvironmentID: environment.ID,
  	InitialEvents: []anthropic.BetaManagedAgentsDeploymentInitialEventParamsUnion{{
  		OfUserMessage: &anthropic.BetaManagedAgentsUserMessageEventParams{
  			Type: anthropic.BetaManagedAgentsUserMessageEventParamsTypeUserMessage,
  			Content: []anthropic.BetaManagedAgentsUserMessageEventParamsContentUnion{{
  				OfText: &anthropic.BetaManagedAgentsTextBlockParam{
  					Type: anthropic.BetaManagedAgentsTextBlockTypeText,
  					Text: "Run the weekly compliance scan.",
  				},
  			}},
  		},
  	}},
  	Schedule: anthropic.BetaManagedAgentsScheduleParams{
  		Type:       anthropic.BetaManagedAgentsScheduleParamsTypeCron,
  		Expression: "0 20 * * 5",
  		Timezone:   "America/New_York",
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  var deployment = client.beta().deployments().create(
      DeploymentCreateParams.builder()
          .name("Weekly compliance scan")
          .agent(agent.id())
          .environmentId(environment.id())
          .addInitialEvent(
              BetaManagedAgentsUserMessageEventParams.builder()
                  .type(BetaManagedAgentsUserMessageEventParams.Type.USER_MESSAGE)
                  .addTextContent("Run the weekly compliance scan.")
                  .build()
          )
          .schedule(
              BetaManagedAgentsScheduleParams.builder()
                  .type(BetaManagedAgentsScheduleParams.Type.CRON)
                  .expression("0 20 * * 5")
                  .timezone("America/New_York")
                  .build()
          )
          .build()
  );

php PHP
  $deployment = $client->beta->deployments->create(
      name: 'Weekly compliance scan',
      agent: $agent->id,
      environmentID: $environment->id,
      initialEvents: [
          [
              'type' => 'user.message',
              'content' => [['type' => 'text', 'text' => 'Run the weekly compliance scan.']],
          ],
      ],
      schedule: [
          'type' => 'cron',
          'expression' => '0 20 * * 5',
          'timezone' => 'America/New_York',
      ],
  );

ruby Ruby
  deployment = client.beta.deployments.create(
    name: "Weekly compliance scan",
    agent: agent.id,
    environment_id: environment.id,
    initial_events: [
      {
        type: "user.message",
        content: [{type: "text", text: "Run the weekly compliance scan."}]
      }
    ],
    schedule: {
      type: "cron",
      expression: "0 20 * * 5",
      timezone: "America/New_York"
    }
  )

json
{
  "id": "depl_01xyz",
  "status": "active",
  "paused_reason": null,
  "schedule": {
    "type": "cron",
    "expression": "0 20 * * 5",
    "timezone": "America/New_York",
    "last_run_at": null,
    "upcoming_runs_at": [
      "2026-05-09T00:00:00Z",
      "2026-05-16T00:00:00Z",
      "2026-05-23T00:00:00Z"
    ]
  }
}

bash cURL
curl --fail-with-body -sS "https://api.anthropic.com/v1/deployments/$DEPLOYMENT_ID?beta=true" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  -d @- <<'EOF'
{
  "budget": {
    "type": "limit",
    "max_list_cost": {"amount": "2000", "currency": "USD"}
  }
}
EOF
```


## Deployment runs

Source: https://platform.claude.com/llms-full.txt#deployment-runs

Deployments can fail to trigger for a variety of reasons: for example, if the `environment` resource has been archived, or if session creation is rate-limited. Each attempt at executing a deployment generates a **deployment run** record, allowing you to track successes and failures independent of the session lifecycle.

Successful deployments generate active sessions, and a successful deployment run contains the associated `session_id`. To follow a session's lifecycle, track the session events through the [event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming) or [webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks). Deployment lifecycle changes and the outcome of each scheduled run are also delivered as webhook events, listed in the Deployment events and Deployment run events tabs of [Supported event types](https://platform.claude.com/docs/en/managed-agents/webhooks#supported-event-types).

List all deployment runs for a deployment as follows:

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl --fail-with-body -sS "https://api.anthropic.com/v1/deployment_runs?beta=true&deployment_id=$DEPLOYMENT_ID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
  ant beta:deployment-runs list --deployment-id "$DEPLOYMENT_ID"

python Python
  for run in client.beta.deployment_runs.list(
      deployment_id=deployment.id,
  ):
      print(run.created_at, run.session_id or run.error.type)

typescript TypeScript
  for await (const run of client.beta.deploymentRuns.list({
    deployment_id: deployment.id,
  })) {
    console.log(run.created_at, run.session_id ?? run.error?.type);
  }

csharp C#
  var runs = await client.Beta.DeploymentRuns.List(
      new() { DeploymentID = deployment.ID }
  );
  await foreach (var run in runs.Paginate())
  {
      // The Error union exposes .Message directly; the discriminator is read
      // from .Json until a common .Type accessor is added.
      var outcome = run.SessionID ?? run.Error!.Json.GetProperty("type").GetString();
      Console.WriteLine($"{run.CreatedAt} {outcome}");
  }

go Go
  runs := client.Beta.DeploymentRuns.ListAutoPaging(ctx, anthropic.BetaDeploymentRunListParams{
  	DeploymentID: anthropic.String(deployment.ID),
  })
  for runs.Next() {
  	run := runs.Current()
  	if run.SessionID != "" {
  		fmt.Println(run.CreatedAt.Format(time.RFC3339), run.SessionID)
  	} else {
  		fmt.Println(run.CreatedAt.Format(time.RFC3339), run.Error.Type)
  	}
  }
  if err := runs.Err(); err != nil {
  	panic(err)
  }

java Java
  for (var run : client.beta().deploymentRuns().list(
          DeploymentRunListParams.builder()
              .deploymentId(deployment.id())
              .build()).autoPager()) {
      // The Error union does not yet expose common .type()/.message()
      // accessors; .toString() includes both.
      IO.println(run.createdAt() + " "
          + run.sessionId().orElseGet(() -> run.error().orElseThrow().toString()));
  }

php PHP
  foreach ($client->beta->deploymentRuns->list(
      deploymentID: $deployment->id,
  )->pagingEachItem() as $run) {
      $outcome = $run->sessionID ?? $run->error->type;
      echo "{$run->createdAt->format(DATE_ATOM)} {$outcome}\n";
  }

ruby Ruby
  client.beta.deployment_runs.list(
    deployment_id: deployment.id
  ).auto_paging_each do
    puts "#{it.created_at} #{it.session_id || it.error.type}"
  end

bash cURL
  curl --fail-with-body -sS "https://api.anthropic.com/v1/deployment_runs?beta=true&deployment_id=$DEPLOYMENT_ID&has_error=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
  ant beta:deployment-runs list --deployment-id "$DEPLOYMENT_ID" --has-error

python Python
  for run in client.beta.deployment_runs.list(
      deployment_id=deployment.id,
      has_error=True,
  ):
      print(run.created_at, run.error.type, run.error.message)

typescript TypeScript
  for await (const run of client.beta.deploymentRuns.list({
    deployment_id: deployment.id,
    has_error: true,
  })) {
    console.log(run.created_at, run.error?.type, run.error?.message);
  }

csharp C#
  var failedRuns = await client.Beta.DeploymentRuns.List(
      new() { DeploymentID = deployment.ID, HasError = true }
  );
  await foreach (var failedRun in failedRuns.Paginate())
  {
      var error = failedRun.Error!;
      var errorType = error.Json.GetProperty("type").GetString();
      Console.WriteLine($"{failedRun.CreatedAt} {errorType} {error.Message}");
  }

go Go
  failedRuns := client.Beta.DeploymentRuns.ListAutoPaging(ctx, anthropic.BetaDeploymentRunListParams{
  	DeploymentID: anthropic.String(deployment.ID),
  	HasError:     anthropic.Bool(true),
  })
  for failedRuns.Next() {
  	failedRun := failedRuns.Current()
  	fmt.Println(failedRun.CreatedAt.Format(time.RFC3339), failedRun.Error.Type, failedRun.Error.Message)
  }
  if err := failedRuns.Err(); err != nil {
  	panic(err)
  }

java Java
  for (var run : client.beta().deploymentRuns().list(
          DeploymentRunListParams.builder()
              .deploymentId(deployment.id())
              .hasError(true)
              .build()).autoPager()) {
      IO.println(run.createdAt() + " " + run.error().orElseThrow());
  }

php PHP
  foreach ($client->beta->deploymentRuns->list(
      deploymentID: $deployment->id,
      hasError: true,
  )->pagingEachItem() as $run) {
      echo "{$run->createdAt->format(DATE_ATOM)} {$run->error->type} {$run->error->message}\n";
  }

ruby Ruby
  client.beta.deployment_runs.list(
    deployment_id: deployment.id,
    has_error: true
  ).auto_paging_each do
    puts "#{it.created_at} #{it.error.type} #{it.error.message}"
  end

json
{
  "type": "deployment_run",
  "id": "drun_01abc124",
  "deployment_id": "depl_01xyz",
  "trigger_context": { "type": "schedule", "scheduled_at": "2026-05-09T00:00:00Z" },
  "session_id": null,
  "error": {
    "type": "environment_archived_error",
    "message": "environment `env_01abc` is archived"
  },
  "agent": { "type": "agent", "id": "agent_01ghi789", "version": 3 },
  "created_at": "2026-05-09T00:00:01Z"
}
```

To retrieve a single run by ID, call [`GET /v1/deployment_runs/{deployment_run_id}`](https://platform.claude.com/docs/en/api/beta/deployment_runs/retrieve). A [`deployment_run` webhook event](https://platform.claude.com/docs/en/managed-agents/webhooks#supported-event-types) carries the run ID as its `data.id`.


## Managing deployment lifecycle

Source: https://platform.claude.com/llms-full.txt#managing-deployment-lifecycle

Each lifecycle change emits a [webhook event](https://platform.claude.com/docs/en/managed-agents/webhooks#supported-event-types), so you can react to a paused, unpaused, or archived deployment without polling; see the Deployment events tab.

**Pause** suppresses scheduled triggers on a go-forward basis; running sessions from a prior deployment run continue to execute. Manual runs through the `run` endpoint are still allowed while paused. Pausing sets `paused_reason` to `{"type": "manual"}`; unpausing clears it.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl --fail-with-body -sS -X POST "https://api.anthropic.com/v1/deployments/$DEPLOYMENT_ID/pause?beta=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
  ant beta:deployments pause --deployment-id "$DEPLOYMENT_ID"

python Python
  client.beta.deployments.pause(deployment.id)

typescript TypeScript
  await client.beta.deployments.pause(deployment.id);

csharp C#
  await client.Beta.Deployments.Pause(deployment.ID);

go Go
  if _, err := client.Beta.Deployments.Pause(ctx, deployment.ID, anthropic.BetaDeploymentPauseParams{}); err != nil {
  	panic(err)
  }

java Java
  client.beta().deployments().pause(deployment.id());

php PHP
  $client->beta->deployments->pause($deployment->id);

ruby Ruby
  client.beta.deployments.pause(deployment.id)

bash cURL
  curl --fail-with-body -sS -X POST "https://api.anthropic.com/v1/deployments/$DEPLOYMENT_ID/unpause?beta=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
  ant beta:deployments unpause --deployment-id "$DEPLOYMENT_ID"

python Python
  client.beta.deployments.unpause(deployment.id)

typescript TypeScript
  await client.beta.deployments.unpause(deployment.id);

csharp C#
  await client.Beta.Deployments.Unpause(deployment.ID);

go Go
  if _, err := client.Beta.Deployments.Unpause(ctx, deployment.ID, anthropic.BetaDeploymentUnpauseParams{}); err != nil {
  	panic(err)
  }

java Java
  client.beta().deployments().unpause(deployment.id());

php PHP
  $client->beta->deployments->unpause($deployment->id);

ruby Ruby
  client.beta.deployments.unpause(deployment.id)

bash cURL
  curl --fail-with-body -sS -X POST "https://api.anthropic.com/v1/deployments/$DEPLOYMENT_ID/archive?beta=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
  ant beta:deployments archive --deployment-id "$DEPLOYMENT_ID"

python Python
  client.beta.deployments.archive(deployment.id)

typescript TypeScript
  await client.beta.deployments.archive(deployment.id);

csharp C#
  await client.Beta.Deployments.Archive(deployment.ID);

go Go
  if _, err := client.Beta.Deployments.Archive(ctx, deployment.ID, anthropic.BetaDeploymentArchiveParams{}); err != nil {
  	panic(err)
  }

java Java
  client.beta().deployments().archive(deployment.id());

php PHP
  $client->beta->deployments->archive($deployment->id);

ruby Ruby
  client.beta.deployments.archive(deployment.id)
  ```
</CodeGroup>

### Failure behavior

Session creation rate-limit responses are recorded immediately as a `session_rate_limited_error` run without retry; the schedule attempts again at the next scheduled occurrence. Rate limits on underlying API calls within a session are handled by the session itself.

If a deployment's agent has been archived, the deployment is automatically archived in the same operation. If the agent has been deleted, the next scheduled trigger detects the missing agent and automatically archives the deployment. In both cases no deployment run is recorded. If a subagent referenced by the agent has been archived, the next trigger records a failed run with `error.type: "agent_archived_error"` and the deployment is automatically paused so you can update the agent and resume. Other unrecoverable session-creation errors, such as an archived environment or vault, behave the same way: the trigger records a failed run and the deployment is automatically paused. The deployment's `paused_reason.error.type` mirrors the failed run's `error.type`.


## Trigger a manual run

Source: https://platform.claude.com/llms-full.txt#trigger-a-manual-run

To run a deployment outside its schedule, call the [`run` endpoint](https://platform.claude.com/docs/en/api/beta/deployments/run). This creates a session immediately and writes a deployment run with `trigger_context.type: "manual"`. This allows you to test a deployment before committing to the schedule.

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  curl --fail-with-body -sS -X POST "https://api.anthropic.com/v1/deployments/$DEPLOYMENT_ID/run?beta=true" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"

bash CLI
  ant beta:deployments run --deployment-id "$DEPLOYMENT_ID"

python Python
  run = client.beta.deployments.run(deployment.id)

typescript TypeScript
  const run = await client.beta.deployments.run(deployment.id);

csharp C#
  var manualRun = await client.Beta.Deployments.Run(deployment.ID);

go Go
  manualRun, err := client.Beta.Deployments.Run(ctx, deployment.ID, anthropic.BetaDeploymentRunParams{})
  if err != nil {
  	panic(err)
  }

java Java
  var run = client.beta().deployments().run(deployment.id());

php PHP
  $run = $client->beta->deployments->run($deployment->id);

ruby Ruby
  run = client.beta.deployments.run(deployment.id)
  ```
</CodeGroup>


### Reference

---
title: Reference
url: https://platform.claude.com/docs/en/managed-agents/reference
description: Event types, self-hosted worker CLI flags, supported MCP server types, rate limits, and branding guidelines for Claude Managed Agents.
---

This page collects reference material for Claude Managed Agents. For task-oriented guides, follow the links in each section. For the operations on the session resource, see [Session operations](https://platform.claude.com/docs/en/managed-agents/session-operations).

<Note>
  Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See [Beta headers](https://platform.claude.com/docs/en/api/beta-headers#endpoint-specific-headers).
</Note>


## Event types

Source: https://platform.claude.com/llms-full.txt#event-types-3

Persisted event type strings follow a `{domain}.{action}` naming convention; the stream-only event deltas (see the Event deltas tab) are the exception. See [Session event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming) for sending, streaming, and listing events. Webhook event types are listed separately in [Subscribe to webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks#supported-event-types), and some of their names differ from the stream's (for example, `session.status_idled` rather than `session.status_idle`).

<Tabs>
  <Tab title="User events">
    | Type                      | Description                                                                                                                                                                                                                                          |
    | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `user.message`            | A user message with text, image, or document content.                                                                                                                                                                                                |
    | `user.interrupt`          | Stop the agent mid-execution.                                                                                                                                                                                                                        |
    | `user.custom_tool_result` | Response to a custom tool call from the agent.                                                                                                                                                                                                       |
    | `user.tool_confirmation`  | Approve or deny an agent or MCP tool call when a permission policy requires confirmation.                                                                                                                                                            |
    | `user.define_outcome`     | Define an [outcome](https://platform.claude.com/docs/en/managed-agents/define-outcomes) for the agent to work toward.                                                                                                                                |
    | `user.tool_result`        | For sessions with `self_hosted` [environments](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) only, your integration is responsible for providing `agent_toolset` results. The SDK helpers and CLI do this automatically. |
  </Tab>

  <Tab title="Agent events">
    | Type                             | Description                                                                                                                                                                                                                                                                    |
    | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
    | `agent.message`                  | Agent response content blocks.                                                                                                                                                                                                                                                 |
    | `agent.thinking`                 | Signals the agent is making forward progress through extended thinking. This is a progress signal only and does not carry the thinking content.                                                                                                                                |
    | `agent.tool_use`                 | Agent invokes a pre-built agent tool (bash, file operations, and so on).                                                                                                                                                                                                       |
    | `agent.tool_result`              | Result of a pre-built agent tool execution.                                                                                                                                                                                                                                    |
    | `agent.mcp_tool_use`             | Agent invokes an MCP server tool.                                                                                                                                                                                                                                              |
    | `agent.mcp_tool_result`          | Result of an MCP tool execution.                                                                                                                                                                                                                                               |
    | `agent.custom_tool_use`          | Agent invokes one of your custom tools. Respond with a `user.custom_tool_result` event.                                                                                                                                                                                        |
    | `agent.thread_context_compacted` | Conversation history was compacted to fit the context window.                                                                                                                                                                                                                  |
    | `agent.thread_message_received`  | In a [multiagent](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration) session, a message from another thread arrived on the thread whose stream carries this event; on the primary thread, an agent sent a report or question to the coordinator.     |
    | `agent.thread_message_sent`      | In a [multiagent](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration) session, the thread whose stream carries this event sent a message to another thread; on the primary thread, the coordinator sent a task or follow-up message to another agent. |

    Message content in these events can include a `redacted` content block, `{"type": "redacted"}`: a placeholder for content withheld by Anthropic model policy. The block carries no other fields. Redacted blocks appear only in content the platform emits; a user event that includes one is rejected with a 400 error.
  </Tab>

  <Tab title="Session events">
    | Type                                | Description                                                                                                                                                                                                                                                     |
    | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `session.status_running`            | Agent is actively processing.                                                                                                                                                                                                                                   |
    | `session.status_idle`               | Agent finished its current task and is waiting for input. Includes a `stop_reason` indicating why the agent stopped.                                                                                                                                            |
    | `session.status_rescheduled`        | A transient error occurred and the session is retrying automatically.                                                                                                                                                                                           |
    | `session.status_terminated`         | Session ended, either because of an unrecoverable error or because it was archived.                                                                                                                                                                             |
    | `session.deleted`                   | Session was deleted. Terminates any active event stream; no further events are emitted for this session.                                                                                                                                                        |
    | `session.updated`                   | Session update request changed at least one field. Includes only the fields that changed. Updates apply on the next turn.                                                                                                                                       |
    | `session.error`                     | An error occurred during processing. Includes a typed `error` object with a `retry_status`.                                                                                                                                                                     |
    | `session.usage`                     | Snapshot of the session's cumulative usage and tracked list cost. Carries the session's usage totals and an echo of the session's [budget](https://platform.claude.com/docs/en/managed-agents/budgets), or `null` when the session has none.                    |
    | `session.thread_created`            | A [multiagent](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration) thread was created.                                                                                                                                                 |
    | `session.thread_status_running`     | A session thread began executing. Every session emits this for its primary thread; in [multiagent](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration) sessions, child-thread transitions are also cross-posted to the primary stream. |
    | `session.thread_status_idle`        | A session thread finished its turn and is awaiting input. Includes `stop_reason`.                                                                                                                                                                               |
    | `session.thread_status_rescheduled` | A session thread hit a transient error and is retrying automatically.                                                                                                                                                                                           |
    | `session.thread_status_terminated`  | A session thread was archived or reached a terminal error.                                                                                                                                                                                                      |
  </Tab>

  <Tab title="Span events">
    Span events are observability markers that wrap activity for timing and usage tracking.

    | Type                              | Description                                                                                                                                                                                                                                              |
    | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `span.model_request_start`        | A model inference call has started.                                                                                                                                                                                                                      |
    | `span.model_request_end`          | A model inference call has completed. Includes `model_usage` with token counts.                                                                                                                                                                          |
    | `span.outcome_evaluation_start`   | [Outcome](https://platform.claude.com/docs/en/managed-agents/define-outcomes) evaluation has started.                                                                                                                                                    |
    | `span.outcome_evaluation_ongoing` | Heartbeat during an ongoing [outcome](https://platform.claude.com/docs/en/managed-agents/define-outcomes) evaluation.                                                                                                                                    |
    | `span.outcome_evaluation_end`     | An [outcome](https://platform.claude.com/docs/en/managed-agents/define-outcomes) evaluation cycle has completed. A `needs_revision` result means another cycle follows; `satisfied`, `max_iterations_reached`, `failed`, and `interrupted` are terminal. |
  </Tab>

  <Tab title="System events">
    | Type             | Description                                                                                                                                                                                                                                                                                                                                |
    | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
    | `system.message` | Append privileged system-level context that applies to the accompanying turn and all subsequent turns. Supported on Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5, Claude Mythos 5, Claude Opus 5, and Claude Opus 4.8. On an unsupported primary model the event is rejected with `model_does_not_support_mid_conversation_system`. |
  </Tab>

  <Tab title="Event deltas">
    Event deltas are stream-only preview events. They are emitted on stream connections (session-level or per-thread) that opt in with the `event_deltas[]` parameter, and they are never persisted to the session's event history. See [Event deltas](https://platform.claude.com/docs/en/managed-agents/events-and-streaming#event-deltas) for opting in, accumulating, and reconciling them.

    | Type          | Description                                                                                                              |
    | ------------- | ------------------------------------------------------------------------------------------------------------------------ |
    | `event_start` | A previewed event has started generating. Carries the upcoming event's `type` and `id`. Stream-only and never persisted. |
    | `event_delta` | Incremental content for a previewed event, identified by `event_id`. Stream-only and never persisted.                    |
  </Tab>
</Tabs>


## Self-hosted worker

Source: https://platform.claude.com/llms-full.txt#self-hosted-worker

These are the `ant beta:worker` CLI flags for the pre-built worker that drives a `self_hosted` environment. See [Self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) for setting up the environment, running a worker, and the SDK helper options.

| Flag                   | Description                                                                                                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--environment-id`     | The environment to poll for work. Also reads from `ANTHROPIC_ENVIRONMENT_ID`.                                                                                                         |
| `--environment-key`    | Authenticates the worker with this environment. Also reads from `ANTHROPIC_ENVIRONMENT_KEY`.                                                                                          |
| `--workdir`            | Directory where skills are downloaded and tools read and write files. Defaults to `.` (the current directory); the system default working directory is `/workspace`.                  |
| `--on-work`            | Script to call for each claimed work item instead of running tools in-process. Receives session details as environment variables.                                                     |
| `--unrestricted-paths` | Allow the file tools to read and write paths outside `--workdir`. The workdir check is a guardrail for the file tools only, not a sandbox; it does not constrain bash.                |
| `--max-idle`           | How long to wait after the session goes idle with an `end_turn` [stop reason](https://platform.claude.com/docs/en/api/handling-stop-reasons) before shutting down. Defaults to `60s`. |
| `--log-format`         | Log output format. Use `json` for structured log ingestion. Defaults to `text`.                                                                                                       |

The CLI worker does not mount [memory stores](https://platform.claude.com/docs/en/managed-agents/memory): a session that attaches one still runs, but the agent finds nothing at the store's `mount_path` and no changes sync back to the store. To use memory stores in sessions on a self-hosted environment, run the SDK worker instead; see [Use memory stores](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes#use-memory-stores).


## Supported MCP server types

Source: https://platform.claude.com/llms-full.txt#supported-mcp-server-types

Claude Managed Agents connects to [remote MCP servers](https://platform.claude.com/docs/en/agents-and-tools/remote-mcp-servers) that expose an HTTP endpoint, or to private MCP servers through [MCP tunnels](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview). The server should support the MCP protocol's streamable HTTP transport; servers that only support the deprecated SSE transport still work through an automatic fallback. See [MCP connector](https://platform.claude.com/docs/en/managed-agents/mcp-connector) for declaring servers on an agent.

For more information on MCP and building MCP servers, see the [MCP documentation](https://modelcontextprotocol.io).


## Rate limits

Source: https://platform.claude.com/llms-full.txt#rate-limits-2

Managed Agents endpoints are rate-limited per organization:

| Operation                                                     | Limit                     |
| ------------------------------------------------------------- | ------------------------- |
| Create endpoints (such as agents, sessions, and environments) | 300 requests per minute   |
| Read endpoints (such as retrieve, list, and stream)           | 1,200 requests per minute |

Organization-level [spend limits and usage-tier rate limits](https://platform.claude.com/docs/en/api/rate-limits) also apply.


## Branding guidelines

Source: https://platform.claude.com/llms-full.txt#branding-guidelines

For partners integrating Claude Managed Agents, use of Claude branding is optional. When referencing Claude in your product:

**Allowed:**

* "Claude Agent" (preferred for dropdown menus)
* "Claude" (when within a menu already labeled "Agents")
* "\{YourAgentName} Powered by Claude" (if you have an existing agent name)

**Not permitted:**

* "Claude Code" or "Claude Code Agent"
* "Claude Cowork" or "Claude Cowork Agent"
* Claude Code-branded ASCII art or visual elements that mimic Claude Code

Your product should maintain its own branding and not appear to be Claude Code, Claude Cowork, or any other Anthropic product. For questions about branding compliance, contact the Anthropic [sales team](https://www.anthropic.com/contact-sales).


## Admin

Source: https://platform.claude.com/llms-full.txt#admin

### Organization

---
title: Admin API
url: https://platform.claude.com/docs/en/manage-claude/admin-api
description: Manage organization members, workspaces, invites, and API keys programmatically with the Admin API, using an Admin API key, an `org:admin` OAuth token, or a personal or service account key.
---

<Tip>
  **The Admin API is unavailable for individual accounts.** To collaborate with teammates and add members, set up your organization in **Console → Settings → Organization**.
</Tip>

The [Admin API](https://platform.claude.com/docs/en/api/admin) lets you manage your organization's members, workspaces, invites, and API keys programmatically instead of by hand in the [Claude Console](https://platform.claude.com/).

<Check>
  **The Admin API requires special access**

  The Admin API accepts three credentials:

  * An **Admin API key** (starting with `sk-ant-admin...`) sent in the `x-api-key` header. Only organization members with the admin role can provision one. See [Create an Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys).
  * An **OAuth bearer token** with the `org:admin` scope sent in the `authorization: Bearer` header. Only members with the admin, owner, or primary owner role can obtain one. See [Obtain an OAuth bearer token](https://platform.claude.com/docs/en/manage-claude/admin-api#oauth-bearer-token).
  * A **personal key** or **service account key** that isn't scoped to a specific workspace, sent in the `x-api-key` header. The key has the same permissions as the linked account. See [Key types](https://platform.claude.com/docs/en/manage-claude/authentication#key-types).
</Check>

<Note>
  **Claude Enterprise:** Claude Enterprise (claude.ai) organizations call the Admin API with a scoped API key created in claude.ai. From this page, only the members and invites endpoints apply to them. They also get Enterprise-only endpoints: group and custom-role reads, and [spend limits](https://platform.claude.com/docs/en/manage-claude/spend-limits-api). See [User management](https://platform.claude.com/docs/en/manage-claude/user-management).
</Note>

<Note>
  **Claude Platform on AWS:** Only the workspace endpoints (create, get, list, update, and archive on `/v1/organizations/workspaces`) and the external key endpoints (register, get, list, update, and delete on `/v1/organizations/external_keys`, for [CMEK](https://platform.claude.com/docs/en/manage-claude/cmek-aws-kms#claude-platform-on-aws); there is no validate endpoint, because keys are validated when attached to a workspace) are available on Claude Platform on AWS. Organization members, workspace members, invites, API keys, and the usage, cost, and rate limit reports aren't. See [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws).
</Note>


## Authentication

Source: https://platform.claude.com/llms-full.txt#authentication-5

Authenticate with any of the three credentials. An Admin API key covers most endpoints. The service-account, federation-issuer, and federation-rule endpoints accept only an `org:admin` OAuth token. Send a personal key or service account key in the `x-api-key` header, as you would an Admin API key. The following examples call the [organization info endpoint](https://platform.claude.com/docs/en/manage-claude/admin-api#accessing-organization-info) with an OAuth token and with an Admin API key.

### OAuth bearer token

Log in with the [`ant` CLI](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/quickstart) under a dedicated profile, requesting the `org:admin` scope (see [Admin access](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/authentication#admin-access)), then export the bearer token. A dedicated profile keeps your routine commands from running with elevated access:

```bash CLI
ant auth login --profile admin --scope "org:admin"
export ANTHROPIC_AUTH_TOKEN=$(ant auth print-credentials --profile admin --access-token)

bash cURL
curl --fail-with-body -sS "https://api.anthropic.com/v1/organizations/me" \
  --header "anthropic-version: 2023-06-01" \
  --header "authorization: Bearer $ANTHROPIC_AUTH_TOKEN"

bash cURL
curl --fail-with-body -sS "https://api.anthropic.com/v1/organizations/me" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```


## How the Admin API works

Source: https://platform.claude.com/llms-full.txt#how-the-admin-api-works

Authenticate with any credential from [Authentication](https://platform.claude.com/docs/en/manage-claude/admin-api#authentication), then manage the following resources:

* Organization members and their roles
* Organization invites
* Workspaces and their members
* API keys
* Service accounts, federation issuers, and federation rules (`org:admin` OAuth token only)

Common uses include automating onboarding and offboarding, managing workspace access, and auditing API keys.


## Organization roles and permissions

Source: https://platform.claude.com/llms-full.txt#organization-roles-and-permissions

There are five organization-level roles. For details, see [API Console roles and permissions](https://support.claude.com/en/articles/10186004-api-console-roles-and-permissions).

| Role               | Permissions                                                                    |
| ------------------ | ------------------------------------------------------------------------------ |
| user               | Can use playground                                                             |
| claude\_code\_user | Can use playground and [Claude Code](https://code.claude.com/docs/en/overview) |
| developer          | Can use playground and manage API keys                                         |
| billing            | Can use playground and manage billing details                                  |
| admin              | Can do all of the preceding, plus manage users                                 |

Organization owners and primary owners have all admin permissions and can also manage admins. All references to the admin role on this page also apply to owners and primary owners.


## Key concepts

Source: https://platform.claude.com/llms-full.txt#key-concepts

### Organization members

List [organization members](https://platform.claude.com/docs/en/api/admin-api/users/get-user), update their roles, and remove them.

<CodeGroup>
  ```bash cURL
  # List organization members
  curl "https://api.anthropic.com/v1/organizations/users?limit=10" \
    --header "anthropic-version: 2023-06-01" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

  # Update member role
  curl "https://api.anthropic.com/v1/organizations/users/{user_id}" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
    --data '{"role": "developer"}'

  # Remove member
  curl --request DELETE "https://api.anthropic.com/v1/organizations/users/{user_id}" \
    --header "anthropic-version: 2023-06-01" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

bash cURL
  # Create invite
  curl --request POST "https://api.anthropic.com/v1/organizations/invites" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
    --data '{
      "email": "newuser@domain.com",
      "role": "developer"
    }'

  # List invites
  curl "https://api.anthropic.com/v1/organizations/invites?limit=10" \
    --header "anthropic-version: 2023-06-01" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

  # Delete invite
  curl --request DELETE "https://api.anthropic.com/v1/organizations/invites/{invite_id}" \
    --header "anthropic-version: 2023-06-01" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

bash cURL
  # Add member to workspace
  curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
    --data '{
      "user_id": "user_xxx",
      "workspace_role": "workspace_developer"
    }'

  # List workspace members
  curl "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members?limit=10" \
    --header "anthropic-version: 2023-06-01" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

  # Update member role
  curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
    --data '{
      "workspace_role": "workspace_admin"
    }'

  # Remove member from workspace
  curl --request DELETE "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
    --header "anthropic-version: 2023-06-01" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

bash cURL
  # List API keys
  curl "https://api.anthropic.com/v1/organizations/api_keys?limit=10&status=active&workspace_id=wrkspc_xxx" \
    --header "anthropic-version: 2023-06-01" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

  # Update API key
  curl --request POST "https://api.anthropic.com/v1/organizations/api_keys/{api_key_id}" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
    --data '{
      "status": "inactive",
      "name": "New Key Name"
    }'
  ```
</CodeGroup>

### Service accounts

Create and manage service accounts (`svac_...`), the non-human identities that [service account keys](https://platform.claude.com/docs/en/manage-claude/authentication#key-types) and [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) tokens act as. These endpoints, like the federation-issuer and federation-rule endpoints, require an `org:admin` OAuth token. See [Manage WIF with the Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api#service-accounts).

### Federation issuers

Register the OIDC identity providers (`fdis_...`) whose tokens may assert workload identity for your organization. See [Manage WIF with the Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api#federation-issuers).

### Federation rules

Manage the rules (`fdrl_...`) that map issuer tokens to service accounts and scopes. See [Manage WIF with the Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api#federation-rules).


## Accessing organization info

Source: https://platform.claude.com/llms-full.txt#accessing-organization-info

The `/v1/organizations/me` endpoint returns the organization that your credential belongs to:

```bash cURL
curl "https://api.anthropic.com/v1/organizations/me" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

json
{
  "id": "12345678-1234-5678-1234-567812345678",
  "type": "organization",
  "name": "Organization Name"
}
```

For parameter details and response schemas, see the [Organization Info API reference](https://platform.claude.com/docs/en/api/admin-api/organization/get-me).


## Usage and cost reports

Source: https://platform.claude.com/llms-full.txt#usage-and-cost-reports

Track your organization's usage and costs with the [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api).


## Claude Code analytics

Source: https://platform.claude.com/llms-full.txt#claude-code-analytics

Monitor developer productivity and Claude Code adoption with the [Claude Code Analytics API](https://platform.claude.com/docs/en/manage-claude/claude-code-analytics-api).


## Rate limits

Source: https://platform.claude.com/llms-full.txt#rate-limits-3

Read the rate limits configured for your organization and its workspaces with the [Rate Limits API](https://platform.claude.com/docs/en/manage-claude/rate-limits-api).


## Compliance API

Source: https://platform.claude.com/llms-full.txt#compliance-api

Retrieve audit and activity data for your organization with the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api). Admin API keys can read only the Activity Feed. For full access, see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).


## Best practices

Source: https://platform.claude.com/llms-full.txt#best-practices-9

* Use meaningful names and descriptions for workspaces and API keys
* Handle errors from failed operations
* Regularly audit member roles and permissions
* Clean up unused workspaces and expired invites
* Monitor API key usage, audit each key's [`expires_at`](https://platform.claude.com/docs/en/manage-claude/authentication#key-expiration), and rotate keys periodically


## FAQ

Source: https://platform.claude.com/llms-full.txt#faq-7

<AccordionGroup>
  <Accordion title="What permissions are needed to use the Admin API?">
    The Admin API accepts an Admin API key (starting with `sk-ant-admin`), an OAuth bearer token with the `org:admin` scope, or a personal key or service account key that isn't scoped to a specific workspace. Only organization members with the admin role can provision Admin API keys, and only members with the admin, owner, or primary owner role can obtain `org:admin` tokens. A personal key or service account key has the same permissions as the linked account. See [Authentication](https://platform.claude.com/docs/en/manage-claude/admin-api#authentication).
  </Accordion>

  <Accordion title="Can I create new API keys through the Admin API?">
    No. You create API keys in the Claude Console. The Admin API can only read, rename, and change the status of existing keys.
  </Accordion>

  <Accordion title="What happens to API keys when removing a user?">
    Behavior depends on the [key type](https://platform.claude.com/docs/en/manage-claude/authentication#key-types).

    Personal keys stop working when their user is removed from the organization. Service account keys stop working if their service account is archived, but continue to work even if the user that created them is removed. Workspace API keys continue to work. In the [Claude Code workspace](https://platform.claude.com/docs/en/manage-claude/workspaces#claude-code-workspace), each key is bound to the member who created it and stops working when that member is removed.
  </Accordion>

  <Accordion title="Can organization admins be removed through the API?">
    No. The API can't remove members with the admin role.
  </Accordion>

  <Accordion title="How long do organization invites last?">
    Invites expire after 21 days. The expiration period isn't configurable.
  </Accordion>
</AccordionGroup>

For workspace-specific questions, see the [Workspaces FAQ](https://platform.claude.com/docs/en/manage-claude/workspaces#faq).


---
title: User management
url: https://platform.claude.com/docs/en/manage-claude/user-management
description: "Manage the people in your Claude Enterprise organization with the Admin API: list members and change roles, send and withdraw invites, manage groups, and read custom roles."
---

This page covers managing the people in your **Claude Enterprise** (claude.ai) organization programmatically, using the [Admin API](https://platform.claude.com/docs/en/api/admin): list members and look them up by email address, change a member's role, remove members, send and withdraw invites, manage your enterprise's groups and their membership, and read your organization's custom roles. For Claude Console (Claude Platform) organizations, see the [Admin API guide for Claude Console](https://platform.claude.com/docs/en/manage-claude/admin-api).

<Note>
  Group and custom-role requests don't require the `anthropic-beta: ce-user-management-2026-07-13` [beta header](https://platform.claude.com/docs/en/api/beta-headers). Requests that still send it are accepted and behave identically.
</Note>


## Which endpoints can your organization use?

Source: https://platform.claude.com/llms-full.txt#which-endpoints-can-your-organization-use

The Admin API is a single set of endpoints under `https://api.anthropic.com/v1/organizations/`. Claude Console and Claude Enterprise organizations authenticate with [different keys](https://platform.claude.com/docs/en/manage-claude/admin-api-keys) and each have access to a different subset of the endpoints:

| Endpoints                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Claude Console (Claude Platform)                                                                  | Claude Enterprise (claude.ai)    |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | -------------------------------- |
| [Members](https://platform.claude.com/docs/en/manage-claude/user-management#members) and [invites](https://platform.claude.com/docs/en/manage-claude/user-management#invites)                                                                                                                                                                                                                                                                             | Available; see the [Admin API guide](https://platform.claude.com/docs/en/manage-claude/admin-api) | Available (this page)            |
| [Groups](https://platform.claude.com/docs/en/manage-claude/user-management#groups)                                                                                                                                                                                                                                                                                                                                                                        | Not available                                                                                     | Available (this page)            |
| [Custom roles](https://platform.claude.com/docs/en/manage-claude/user-management#custom-roles)                                                                                                                                                                                                                                                                                                                                                            | Not available                                                                                     | Available, read-only (this page) |
| [Spend limits](https://platform.claude.com/docs/en/manage-claude/spend-limits-api)                                                                                                                                                                                                                                                                                                                                                                        | Not available                                                                                     | Available                        |
| [Workspaces](https://platform.claude.com/docs/en/manage-claude/workspaces), [API keys](https://platform.claude.com/docs/en/manage-claude/admin-api#api-keys), [usage and cost reports](https://platform.claude.com/docs/en/manage-claude/usage-cost-api), [rate limits](https://platform.claude.com/docs/en/manage-claude/rate-limits-api), and the other endpoints in the [Admin API guide](https://platform.claude.com/docs/en/manage-claude/admin-api) | Available                                                                                         | Not available                    |

Members and invites are the same endpoints for both organization types; this page documents their Claude Enterprise behavior, including the Claude Enterprise [organization roles](https://platform.claude.com/docs/en/manage-claude/user-management#organization-roles). The group and custom-role endpoints exist only for Claude Enterprise.

<Check>
  **Scoped Admin API key required**

  These endpoints require an Admin API key with the `read:members` scope (member and invite `GET` endpoints, and all custom-role endpoints; there is no separate role scope), the `write:members` scope (member and invite `POST` and `DELETE` endpoints), the `read:rbac_groups` scope (group `GET` endpoints), or the `write:rbac_groups` scope (group `POST` and `DELETE` endpoints). A key carrying the `read:org_audit` scope (a read-only scope for security-audit integrations) can also call every `GET` endpoint on this page and the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) read endpoints. See [Create an Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys#create-a-key-for-a-claude-enterprise-organization) for where your primary owner creates one and which scopes to select. Pass the key in the `x-api-key` header on every request, together with the [`anthropic-version`](https://platform.claude.com/docs/en/api/versioning) header.
</Check>


## Overview

Source: https://platform.claude.com/llms-full.txt#overview-5

This page covers five resources:

| Resource          | Endpoints                                                                                                                                                                                                                 | Use for                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Members**       | `GET /v1/organizations/users` `GET /v1/organizations/users/{user_id}` `POST /v1/organizations/users/{user_id}` `DELETE /v1/organizations/users/{user_id}`                                                                 | List the organization's members or look one up by email; change a member's role; remove a member.          |
| **Invites**       | `POST /v1/organizations/invites` `GET /v1/organizations/invites` `GET /v1/organizations/invites/{invite_id}` `DELETE /v1/organizations/invites/{invite_id}`                                                               | Invite a person to the organization, track the invitation's status, and withdraw it before it is accepted. |
| **Groups**        | `GET /v1/organizations/rbac_groups` `GET /v1/organizations/rbac_groups/{group_id}` `POST /v1/organizations/rbac_groups` `POST /v1/organizations/rbac_groups/{group_id}` `DELETE /v1/organizations/rbac_groups/{group_id}` | Read your enterprise's groups and the custom roles attached to each; create, rename, and delete groups.    |
| **Group members** | `GET /v1/organizations/rbac_groups/{group_id}/members` `POST /v1/organizations/rbac_groups/{group_id}/members` `DELETE /v1/organizations/rbac_groups/{group_id}/members/{user_id}`                                        | Read a group's members; add and remove members.                                                            |
| **Custom roles**  | `GET /v1/organizations/rbac_roles` `GET /v1/organizations/rbac_roles/{role_id}` `GET /v1/organizations/rbac_roles/{role_id}/permissions`                                                                                  | Read your organization's custom roles and the permissions each role grants.                                |

Custom roles and their group attachments are managed in [claude.ai organization settings](https://claude.ai/admin-settings); the API reads them but cannot change them.


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-11

List the organization's members, newest first:

```bash cURL
curl "https://api.anthropic.com/v1/organizations/users?limit=20" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

json
{
  "data": [
    {
      "type": "user",
      "id": "user_01AbCdEfGhIjKlMnOpQrSt",
      "email": "jane@example.com",
      "name": "Jane Smith",
      "role": "user",
      "added_at": "2026-06-12T09:14:03Z"
    }
  ],
  "has_more": false,
  "first_id": "user_01AbCdEfGhIjKlMnOpQrSt",
  "last_id": "user_01AbCdEfGhIjKlMnOpQrSt"
}
```


## Key concepts

Source: https://platform.claude.com/llms-full.txt#key-concepts-2

### Organization roles

Every member has exactly one organization role. Reads return the member's role as one of five values:

| Role               | Meaning                                                                                   |
| ------------------ | ----------------------------------------------------------------------------------------- |
| `user`             | A standard member.                                                                        |
| `managed`          | A member whose permissions are granted through the custom roles attached to their groups. |
| `owner`            | An organization owner.                                                                    |
| `membership_admin` | A member who can manage the organization's members.                                       |
| `primary_owner`    | The organization's primary owner. There is exactly one.                                   |

The API can assign only the `user` and `managed` roles, on invite creation and on role updates. The administrative roles (`owner`, `membership_admin`, and `primary_owner`) are assigned in claude.ai organization settings, and members holding them cannot be modified or removed through this API.

### Members and invites

A person becomes a member by accepting an invite (or through your organization's single sign-on, where configured). Creating an invite sends an invitation email; the invite then reads as `pending` until the recipient accepts (`accepted`) or its server-assigned `expires_at` passes (`expired`). Only a `pending` invite can be withdrawn. To change a pending invitation's email address or role, withdraw it and create a new one.

If your organization's plan draws members from a finite pool of purchased seats, a pending invite consumes a seat. The create-invite endpoint does not take a seat or tier parameter: the seat is assigned automatically from the lowest tier that has availability. Creating an invite when no seat is free fails with a 400 error rather than purchasing a seat. Withdrawing the invite, letting it expire, or removing the member later returns the seat to the pool.

### Groups and roles

Groups connect members to custom roles (role-based access control, the `rbac` in the endpoint paths and scope names). Groups are owned by your enterprise as a whole (the parent organization together with every organization under it) rather than by a single organization, so the group scopes (`read:rbac_groups` and `write:rbac_groups`) require a key created for all linked organizations. Each group carries a `source_type`: `direct` for groups created in claude.ai, `scim` for groups provisioned by your identity provider. A group's `roles` field lists the IDs of the custom roles attached to it; resolve them to names and permissions with the [custom role endpoints](https://platform.claude.com/docs/en/manage-claude/user-management#custom-roles), noting that the role catalog is per-organization while groups are enterprise-wide, so fetching a role that belongs to a different organization of your enterprise returns 404 for your key. The field is `null` (rather than `[]`) when role data was temporarily unavailable, so retry to distinguish a degraded read from a group with no roles.


## Versioning

Source: https://platform.claude.com/llms-full.txt#versioning

Send the `anthropic-version` header on every request; see [API versions](https://platform.claude.com/docs/en/api/versioning) for the available versions.


## Rate limits

Source: https://platform.claude.com/llms-full.txt#rate-limits-4

Admin API endpoints share a per-organization limit of **100 requests per minute**; invite creation has its own limit of **1,200 requests per hour** instead. Requests over a limit return **429 Too Many Requests**.


## Pagination

Source: https://platform.claude.com/llms-full.txt#pagination

Member and invite lists use ID-based pagination: pass `limit` (default 20, max 1000) plus at most one of `before_id` or `after_id`, and page using the `first_id` and `last_id` fields of each response until `has_more` is `false`. Group and custom-role lists use an **opaque cursor** instead: the response's `next_page` value is passed unchanged as the `page` parameter on the next request, until `next_page` is `null`.


## Error responses

Source: https://platform.claude.com/llms-full.txt#error-responses

Error responses follow the standard shape documented in [Errors](https://platform.claude.com/docs/en/api/errors).


## Members

Source: https://platform.claude.com/llms-full.txt#members

### List members

`GET /v1/organizations/users` returns the organization's members, most recently added first. Filter by `email` to look up a specific member; the match is case-insensitive and tolerates common variants of the same address (for example, `jane+hiring@example.com` matches `jane@example.com`). Requires the `read:members` scope.

For complete parameter details and response schemas, see [List users](https://platform.claude.com/docs/en/api/admin/users/list) in the API reference.

```bash cURL
curl "https://api.anthropic.com/v1/organizations/users?email=jane@example.com" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

bash cURL
curl "https://api.anthropic.com/v1/organizations/users/user_01AbCdEfGhIjKlMnOpQrSt" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

bash cURL
curl -X POST "https://api.anthropic.com/v1/organizations/users/user_01AbCdEfGhIjKlMnOpQrSt" \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"role": "managed"}'

bash cURL
curl -X DELETE "https://api.anthropic.com/v1/organizations/users/user_01AbCdEfGhIjKlMnOpQrSt" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

json
{
  "type": "user_deleted",
  "id": "user_01AbCdEfGhIjKlMnOpQrSt"
}
```


## Invites

Source: https://platform.claude.com/llms-full.txt#invites

### Create an invite

`POST /v1/organizations/invites` sends an invitation email and returns the invite with a server-assigned `expires_at`. `role` must be `user` or `managed`. If a pending invite already exists for the email address, or the address already belongs to a member, the request returns 400 naming the existing resource. Organizations whose identity provider provisions users automatically (JIT or SCIM) cannot create invites through the API. Requires the `write:members` scope.

On plans that draw members from a finite seat pool, the invite automatically takes a seat from the lowest tier that has availability; the API does not take a tier parameter. If no seat is free, the request fails with a 400 error rather than purchasing a seat. Add seats through the organization's plan management and retry.

The optional `rbac_group_ids` field lists groups (by `rbac_group_`-prefixed ID) to assign to the member when they accept. Passing a non-empty `rbac_group_ids` additionally requires the key to carry the `write:rbac_groups` scope, because group assignment can grant the permissions attached to the group's roles.

For complete parameter details and response schemas, see [Create invite](https://platform.claude.com/docs/en/api/admin/invites/create) in the API reference.

```bash cURL
curl -X POST "https://api.anthropic.com/v1/organizations/invites" \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "email": "newhire@example.com",
    "role": "managed",
    "rbac_group_ids": ["rbac_group_01UvWxYzAbCdEfGhIjKlMn"]
  }'

json
{
  "type": "invite",
  "id": "invite_01QrStUvWxYzAbCdEfGhIj",
  "email": "newhire@example.com",
  "role": "managed",
  "invited_at": "2026-07-06T16:20:11Z",
  "expires_at": "2026-07-27T16:20:11Z",
  "accepted_at": null,
  "status": "pending",
  "rbac_group_ids": ["rbac_group_01UvWxYzAbCdEfGhIjKlMn"]
}

bash cURL
curl "https://api.anthropic.com/v1/organizations/invites?limit=20" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

bash cURL
curl "https://api.anthropic.com/v1/organizations/invites/invite_01QrStUvWxYzAbCdEfGhIj" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

bash cURL
curl -X DELETE "https://api.anthropic.com/v1/organizations/invites/invite_01QrStUvWxYzAbCdEfGhIj" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"
```


## Groups

Source: https://platform.claude.com/llms-full.txt#groups

Groups your enterprise creates directly, in [claude.ai organization settings](https://claude.ai/admin-settings) or through this API (`source_type: "direct"`), support every endpoint in this section. Groups provisioned by your identity provider (`source_type: "scim"`) can be read but not modified: renaming or deleting a SCIM group, or changing its membership, returns 400, because your identity provider owns it.

### List groups

`GET /v1/organizations/rbac_groups` returns your enterprise's groups, including identity-provider-managed (`scim`) groups. Requires the `read:rbac_groups` scope.

For complete parameter details and response schemas, see [List groups](https://platform.claude.com/docs/en/api/admin/rbac_groups/list) in the API reference.

```bash cURL
curl "https://api.anthropic.com/v1/organizations/rbac_groups?limit=20" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

json
{
  "data": [
    {
      "type": "rbac_group",
      "id": "rbac_group_01UvWxYzAbCdEfGhIjKlMn",
      "name": "Engineering",
      "source_type": "direct",
      "roles": ["rbac_role_01CdEfGhIjKlMnOpQrStUv"],
      "created_at": "2026-03-18T10:01:42Z",
      "updated_at": "2026-05-02T08:55:09Z"
    }
  ],
  "has_more": false,
  "next_page": null
}

bash cURL
curl "https://api.anthropic.com/v1/organizations/rbac_groups/rbac_group_01UvWxYzAbCdEfGhIjKlMn" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

bash cURL
curl -X POST "https://api.anthropic.com/v1/organizations/rbac_groups" \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"name": "Engineering"}'

json
{
  "type": "rbac_group",
  "id": "rbac_group_01UvWxYzAbCdEfGhIjKlMn",
  "name": "Engineering",
  "source_type": "direct",
  "roles": [],
  "created_at": "2026-07-09T18:00:00Z",
  "updated_at": "2026-07-09T18:00:00Z"
}

bash cURL
curl -X POST "https://api.anthropic.com/v1/organizations/rbac_groups/rbac_group_01UvWxYzAbCdEfGhIjKlMn" \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"name": "Platform Engineering"}'

bash cURL
curl -X DELETE "https://api.anthropic.com/v1/organizations/rbac_groups/rbac_group_01UvWxYzAbCdEfGhIjKlMn" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

json
{
  "id": "rbac_group_01UvWxYzAbCdEfGhIjKlMn",
  "type": "rbac_group_deleted"
}

bash cURL
curl "https://api.anthropic.com/v1/organizations/rbac_groups/rbac_group_01UvWxYzAbCdEfGhIjKlMn/members?limit=100" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

json
{
  "data": [
    {
      "type": "rbac_group_member",
      "group_id": "rbac_group_01UvWxYzAbCdEfGhIjKlMn",
      "user_id": "user_01AbCdEfGhIjKlMnOpQrSt",
      "email": "jane@example.com",
      "created_at": "2026-04-07T12:30:00Z"
    }
  ],
  "has_more": false,
  "next_page": null
}

bash cURL
curl -X POST "https://api.anthropic.com/v1/organizations/rbac_groups/rbac_group_01UvWxYzAbCdEfGhIjKlMn/members" \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"user_id": "user_01AbCdEfGhIjKlMnOpQrSt"}'

json
{
  "type": "rbac_group_member",
  "group_id": "rbac_group_01UvWxYzAbCdEfGhIjKlMn",
  "user_id": "user_01AbCdEfGhIjKlMnOpQrSt",
  "email": "jane@example.com",
  "created_at": "2026-07-09T18:00:00Z"
}

bash cURL
curl -X DELETE "https://api.anthropic.com/v1/organizations/rbac_groups/rbac_group_01UvWxYzAbCdEfGhIjKlMn/members/user_01AbCdEfGhIjKlMnOpQrSt" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

json
{
  "group_id": "rbac_group_01UvWxYzAbCdEfGhIjKlMn",
  "user_id": "user_01AbCdEfGhIjKlMnOpQrSt",
  "type": "rbac_group_member_deleted"
}
```


## Custom roles

Source: https://platform.claude.com/llms-full.txt#custom-roles

Custom roles are read-only through the API: these endpoints catalog your organization's custom roles (defined in [claude.ai organization settings](https://claude.ai/admin-settings) or provisioned by Anthropic) and the permissions each role grants. Custom-role reads use the `read:members` scope (there is no separate role scope) and work with an organization-level key: unlike the group endpoints, they do not require a key created for all linked organizations, and the catalog returned is your organization's own.

### List roles

`GET /v1/organizations/rbac_roles` returns your organization's custom roles. Requires the `read:members` scope.

For complete parameter details and response schemas, see [List roles](https://platform.claude.com/docs/en/api/admin/rbac_roles/list) in the API reference.

```bash cURL
curl "https://api.anthropic.com/v1/organizations/rbac_roles?limit=20" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

json
{
  "data": [
    {
      "type": "rbac_role",
      "id": "rbac_role_01CdEfGhIjKlMnOpQrStUv",
      "name": "Engineering base",
      "created_at": "2026-03-18T10:01:42Z",
      "updated_at": "2026-05-02T08:55:09Z"
    }
  ],
  "has_more": false,
  "next_page": null
}

bash cURL
curl "https://api.anthropic.com/v1/organizations/rbac_roles/rbac_role_01CdEfGhIjKlMnOpQrStUv" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

bash cURL
curl "https://api.anthropic.com/v1/organizations/rbac_roles/rbac_role_01CdEfGhIjKlMnOpQrStUv/permissions?limit=20" \
  -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01"

json
{
  "data": [
    {
      "type": "rbac_role_permission",
      "resource": {
        "type": "organization",
        "organization_id": "12345678-1234-5678-1234-567812345678"
      },
      "action": "capability_access_all_ga"
    },
    {
      "type": "rbac_role_permission",
      "resource": {
        "type": "connector_tool",
        "connector_id": "mcpsrv_01WxYzAbCdEfGhIjKlMnOp",
        "tool_name": "search_tickets"
      },
      "action": "use"
    }
  ],
  "has_more": false,
  "next_page": null
}
```


## Example workflows

Source: https://platform.claude.com/llms-full.txt#example-workflows

### Offboard a departing employee

1. Look up the member by email:

   ```bash cURL
   curl "https://api.anthropic.com/v1/organizations/users?email=departing@example.com" \
     -H "x-api-key: $ANTHROPIC_ADMIN_KEY" \
     -H "anthropic-version: 2023-06-01"
   ```

2. Remove them with `DELETE /v1/organizations/users/{user_id}`, using the `id` from the response. Their seat, if any, returns to the pool.

3. If the person had not yet joined, the lookup returns no member; list invites and withdraw their `pending` invite instead.

### Audit group membership

1. List groups and record each group's `id`, `name`, and `roles`.

2. For each group that carries sensitive roles, page through `GET /v1/organizations/rbac_groups/{group_id}/members` and compare the member emails against your identity provider's roster.

3. Remove members who should no longer be in the group with `DELETE /v1/organizations/rbac_groups/{group_id}/members/{user_id}`. For `scim` groups, make the change in your identity provider instead.

For a workflow that combines group membership with a temporary spend limit raise, see [Temporarily raise a member's spend limit during an incident](https://platform.claude.com/docs/en/manage-claude/spend-limits-api#temporarily-raise-a-members-spend-limit-during-an-incident) on the Spend Limits API page.


## Frequently asked questions

Source: https://platform.claude.com/llms-full.txt#frequently-asked-questions

### Is this a different API from the Admin API?

No. The member and invite endpoints are the same `/v1/organizations/` endpoints that Claude Console organizations use; this page documents their Claude Enterprise behavior. The group and custom-role endpoints are part of the same API and exist only for Claude Enterprise organizations. The [availability table](https://platform.claude.com/docs/en/manage-claude/user-management#which-endpoints-can-your-organization-use) shows which endpoints each organization type can call.

### Can I assign the owner or membership admin role through the API?

No. The API assigns only `user` and `managed`, on invite creation and role updates. Administrative roles are assigned in claude.ai organization settings, and members holding them cannot be modified or removed through the API.

### Can I create or modify groups through the API?

Yes, with the `write:rbac_groups` scope: create, rename, and delete groups, and add or remove their members. Two things the API cannot change: groups provisioned by your identity provider (`source_type: "scim"`), whose name and membership are owned by the identity provider, and custom roles, which are managed in claude.ai organization settings (the API [reads them](https://platform.claude.com/docs/en/manage-claude/user-management#custom-roles)).

### Does an unaccepted invite consume a seat?

On plans with a finite seat pool, yes: a `pending` invite holds a seat. Withdrawing the invite or letting it expire frees the seat. On plans without a seat pool, invites consume nothing.

### My organization uses single sign-on. Which operations work?

If your identity provider provisions users automatically (JIT or SCIM), invite creation returns 400. If it manages roles (advanced SSO or advanced SCIM provisioning), role updates return 400. If it manages membership (SCIM provisioning), member removals return 400. Reads work regardless.

### What happens to an Admin API key when the person who created it leaves?

The key keeps working. Admin API keys are scoped to the organization, not to individual users, and a key created in claude.ai does not expire. Removing the creator from the organization or deprovisioning them through your identity provider ends their own access, but not the keys they created. Downgrading their role does not change the keys either: each key stays active with its original scopes. When you offboard someone who created Admin API keys, delete those keys in the **Keys** section of [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access) and create replacements.


## See also

Source: https://platform.claude.com/llms-full.txt#see-also-3

<CardGroup cols={2}>
  <Card title="Create an Admin API key" href="https://platform.claude.com/docs/en/manage-claude/admin-api-keys">
    Where your primary owner creates a scoped key and which scopes to select.
  </Card>

  <Card title="Compliance API" href="https://platform.claude.com/docs/en/manage-claude/compliance-api">
    Audit activity and retrieve or delete user content across your organization.
  </Card>

  <Card title="Analytics APIs" href="https://platform.claude.com/docs/en/manage-claude/analytics-api">
    Per-user and time-bucketed usage and cost reporting for Claude Enterprise.
  </Card>

  <Card title="Spend Limits API" href="https://platform.claude.com/docs/en/manage-claude/spend-limits-api">
    Set per-member spend limits and review increase requests.
  </Card>
</CardGroup>


---
title: Workspaces
url: https://platform.claude.com/docs/en/manage-claude/workspaces
description: Organize API keys, manage team access, and control costs with workspaces.
---

Workspaces provide a way to organize your API usage within an organization. Use workspaces to separate different projects, environments, or teams while maintaining centralized billing and administration.


## How workspaces work

Source: https://platform.claude.com/llms-full.txt#how-workspaces-work

Every organization has a **Default Workspace** that cannot be renamed, archived, or deleted. When you create additional workspaces, you can assign members, service accounts, API keys, and resource limits to each one.

Key characteristics:

* **Workspace identifiers** use the `wrkspc_` prefix (for example, `wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ`)
* **Maximum 100 workspaces** per organization by default (archived workspaces don't count); contact your account team if you need more
* **Default Workspace** has a `wrkspc_` ID like any other workspace (returned in the [`anthropic-workspace-id` response header](https://platform.claude.com/docs/en/manage-claude/workspaces#identify-the-workspace-behind-an-api-response) and accepted by [Get Workspace](https://platform.claude.com/docs/en/api/admin/workspaces/retrieve)), but it doesn't appear in [List Workspaces](https://platform.claude.com/docs/en/api/admin/workspaces/list) results, and API keys, usage reports, and cost reports show `null` for its `workspace_id`, as do all-workspaces API keys (an API key's `scope` field tells them apart; for a key bound to the Default Workspace it carries the real ID)
* **API keys** can be scoped to a single workspace. In this case, they can only access resources within that workspace. Some API keys can be granted permissions across multiple workspaces, and provide a [workspace ID header](https://platform.claude.com/docs/en/manage-claude/authentication#select-a-workspace) to access resources within that workspace

### Claude Code workspace

When a member of your organization first signs in to [Claude Code](https://code.claude.com/docs/en/overview) with their Claude Console account, Anthropic automatically creates a **Claude Code** workspace in the organization and adds that member to it. Every subsequent member who signs in to Claude Code is added the same way.

The Claude Code workspace keeps Claude Code traffic separate from your other API workloads:

* Claude Code mints a per-user API key in this workspace at sign-in. You cannot create keys in it manually from the Console.
* A Claude Code key stops working if its owner is removed from the workspace or organization, unlike a workspace key.
* Claude Code usage is rate-limited separately, and admins can cap its share of the organization's limits under [Settings > Workspaces](https://platform.claude.com/settings/workspaces).
* It is the only workspace that supports per-user monthly spend limits.

<Warning>
  Archiving the Claude Code workspace disables Claude Code sign-in through Console billing for the whole organization.
</Warning>
