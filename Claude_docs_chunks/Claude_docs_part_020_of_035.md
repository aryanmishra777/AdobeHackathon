# platform.claude.com Documentation (Part 20 of 35)

## Use EKS projected service-account tokens

Source: https://platform.claude.com/llms-full.txt#use-eks-projected-service-account-tokens

If your workload runs in an EKS pod, you can skip the STS call and read a Kubernetes-projected service-account token directly from disk. Kubernetes natively projects an OIDC-compatible token into the pod, and the SDK can read it from a file path, so no token-provider callable is required. This path has two fewer AWS configuration steps than the STS path but only works inside a pod; the underlying mechanism is the same as the [generic Kubernetes integration](https://platform.claude.com/docs/en/manage-claude/wif-providers/kubernetes).

This path additionally requires an EKS cluster with an [IAM OIDC provider enabled](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html) and `kubectl` access to the cluster.

### Configure your EKS cluster

<Steps>
  <Step title="Find your cluster's OIDC issuer URL">
    Each EKS cluster has a unique OIDC issuer. Retrieve it with the AWS CLI:

    ```bash CLI
    aws eks describe-cluster \
      --name <cluster-name> \
      --query "cluster.identity.oidc.issuer" \
      --output text

yaml
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: inference-worker
      namespace: inference
      annotations:
        eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/inference-worker

yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: inference-worker
      namespace: inference
    spec:
      serviceAccountName: inference-worker
      volumes:
        - name: anthropic-token
          projected:
            sources:
              - serviceAccountToken:
                  audience: https://api.anthropic.com
                  expirationSeconds: 3600
                  path: token
      containers:
        - name: app
          image: your-registry/inference-worker:latest
          env:
            - name: ANTHROPIC_IDENTITY_TOKEN_FILE
              value: /var/run/secrets/anthropic.com/token
            - name: ANTHROPIC_FEDERATION_RULE_ID
              value: fdrl_...
            - name: ANTHROPIC_ORGANIZATION_ID
              value: 00000000-0000-0000-0000-000000000000
            - name: ANTHROPIC_SERVICE_ACCOUNT_ID
              value: svac_...
            - name: ANTHROPIC_WORKSPACE_ID  # required when the rule covers multiple workspaces
              value: wrkspc_...
          volumeMounts:
            - name: anthropic-token
              mountPath: /var/run/secrets/anthropic.com
              readOnly: true

json
    {
      "iss": "https://oidc.eks.us-west-2.amazonaws.com/id/6FA42E7BFDE8549CB...",
      "sub": "system:serviceaccount:inference:inference-worker",
      "aud": ["https://api.anthropic.com"],
      "kubernetes.io": {
        "namespace": "inference",
        "serviceaccount": { "name": "inference-worker", "uid": "..." }
      },
      "exp": 1775527120,
      "iat": 1775523520
    }

json
{
  "name": "prod-eks-uswest2",
  "issuer_url": "https://oidc.eks.us-west-2.amazonaws.com/id/6FA42E7BFDE8549CB...",
  "jwks": { "type": "discovery" }
}

json
{
  "name": "prod-inference",
  "issuer_id": "fdis_...",
  "match": {
    "subject_prefix": "system:serviceaccount:inference:inference-worker",
    "audience": "https://api.anthropic.com"
  },
  "target": { "type": "service_account", "service_account_id": "svac_..." },
  "workspace_id": "wrkspc_...",
  "oauth_scope": "workspace:developer",
  "token_lifetime_seconds": 600
}

bash cURL
  JWT=$(cat "$ANTHROPIC_IDENTITY_TOKEN_FILE")

  RESPONSE=$(curl -sS https://api.anthropic.com/v1/oauth/token \
    -H "content-type: application/json" \
    --data @- <<JSON
  {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": "$JWT",
    "federation_rule_id": "$ANTHROPIC_FEDERATION_RULE_ID",
    "organization_id": "$ANTHROPIC_ORGANIZATION_ID",
    "service_account_id": "$ANTHROPIC_SERVICE_ACCOUNT_ID",
    "workspace_id": "$ANTHROPIC_WORKSPACE_ID"
  }
  JSON
  )

  ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r .access_token)

  curl https://api.anthropic.com/v1/messages \
    -H "authorization: Bearer $ACCESS_TOKEN" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello from EKS"}]
    }' | jq -r '.content[] | select(.type == "text") | .text'

python Python
  import os

  import anthropic
  from anthropic import IdentityTokenFile, WorkloadIdentityCredentials

  client = anthropic.Anthropic(
      credentials=WorkloadIdentityCredentials(
          identity_token_provider=IdentityTokenFile(
              os.environ["ANTHROPIC_IDENTITY_TOKEN_FILE"]
          ),
          federation_rule_id=os.environ["ANTHROPIC_FEDERATION_RULE_ID"],
          organization_id=os.environ["ANTHROPIC_ORGANIZATION_ID"],
          service_account_id=os.environ["ANTHROPIC_SERVICE_ACCOUNT_ID"],
          workspace_id=os.environ.get("ANTHROPIC_WORKSPACE_ID"),
      ),
  )

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello from EKS"}],
  )
  print(next(block.text for block in message.content if block.type == "text"))

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";
  import { oidcFederationProvider } from "@anthropic-ai/sdk/lib/credentials/oidc-federation";
  import { identityTokenFromFile } from "@anthropic-ai/sdk/lib/credentials/identity-token";

  const client = new Anthropic({
    credentials: oidcFederationProvider({
      identityTokenProvider: identityTokenFromFile(process.env.ANTHROPIC_IDENTITY_TOKEN_FILE!),
      federationRuleId: process.env.ANTHROPIC_FEDERATION_RULE_ID!,
      organizationId: process.env.ANTHROPIC_ORGANIZATION_ID!,
      serviceAccountId: process.env.ANTHROPIC_SERVICE_ACCOUNT_ID,
      workspaceId: process.env.ANTHROPIC_WORKSPACE_ID,
      baseURL: "https://api.anthropic.com",
      fetch
    })
  });

  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello from EKS" }]
  });
  for (const block of message.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

go Go
  tokenPath := os.Getenv("ANTHROPIC_IDENTITY_TOKEN_FILE")

  readToken := option.IdentityTokenFunc(func(ctx context.Context) (string, error) {
  	raw, err := os.ReadFile(tokenPath)
  	if err != nil {
  		return "", fmt.Errorf("read identity token: %w", err)
  	}
  	return string(raw), nil
  })

  client := anthropic.NewClient(
  	option.WithFederationTokenProvider(readToken, option.FederationOptions{
  		FederationRuleID: os.Getenv("ANTHROPIC_FEDERATION_RULE_ID"),
  		OrganizationID:   os.Getenv("ANTHROPIC_ORGANIZATION_ID"),
  		ServiceAccountID: os.Getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"),
  		WorkspaceID:      os.Getenv("ANTHROPIC_WORKSPACE_ID"),
  	}),
  )

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello from EKS")),
  	},
  })
  if err != nil {
  	panic(err)
  }
  for _, block := range message.Content {
  	if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  		fmt.Println(textBlock.Text)
  		break
  	}
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  var message = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .addUserMessage("Hello from EKS")
          .build());

  IO.println(message.content());

csharp C#
  // Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  // ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  // from the pod's environment.
  using var client = new AnthropicClient();

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello from EKS" }],
  });
  foreach (var block in message.Content)
  {
      if (block.Value is TextBlock textBlock)
      {
          Console.WriteLine(textBlock.Text);
      }
  }

bash CLI
  # Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  # ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello from EKS"}'

php PHP
  use Anthropic\Client;

  // Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  // ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  $client = new Client();

  $message = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello from EKS']],
  );
  $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
  echo $textBlock->text, PHP_EOL;

ruby Ruby
  require "anthropic"

  # Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  # ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello from EKS"}]
  )
  puts message.content.find { it.type == :text }.text

bash cURL
JWT=$(cat "$ANTHROPIC_IDENTITY_TOKEN_FILE")

curl -sS https://api.anthropic.com/v1/oauth/token \
  -H "content-type: application/json" \
  -d "{
    \"grant_type\": \"urn:ietf:params:oauth:grant-type:jwt-bearer\",
    \"assertion\": \"$JWT\",
    \"federation_rule_id\": \"$ANTHROPIC_FEDERATION_RULE_ID\",
    \"organization_id\": \"$ANTHROPIC_ORGANIZATION_ID\",
    \"service_account_id\": \"$ANTHROPIC_SERVICE_ACCOUNT_ID\",
    \"workspace_id\": \"$ANTHROPIC_WORKSPACE_ID\"
  }" | jq
```

A successful exchange returns an `access_token` beginning with `sk-ant-oat01-` and an `expires_in` value in seconds. If the exchange fails with the opaque `401` `authentication_error` response (message `Authentication failed`), check the [authentication history page](https://platform.claude.com/settings/workload-identity-federation?tab=history) for the deny reason and see [Troubleshoot a failed exchange](https://platform.claude.com/docs/en/manage-claude/wif-reference#troubleshoot-a-failed-exchange); the most common EKS-side cause is the projected token's `aud` not matching the rule (project a token with `audience: https://api.anthropic.com`, not the IRSA default `sts.amazonaws.com`).


## Scope your rule

Source: https://platform.claude.com/llms-full.txt#scope-your-rule

<Warning>
  A `subject_prefix` of `arn:aws:iam::123456789012:role/*` matches every IAM role in the account. Any principal that can assume any matching role can obtain a federated Anthropic token.
</Warning>

Lock the rule's `match` block to the narrowest scope that fits your use case:

* **Pin the full role ARN:** Use `subject_prefix: "arn:aws:iam::<account>:role/<role-name>"` with no trailing `*` so other roles in the account do not match.
* **Pin the account ID:** Match the `aws_account` field of the token's `https://sts.amazonaws.com/` claim with the `claims` map or a CEL `condition` as a defense-in-depth check against a misconfigured prefix.
* **Pin namespace and service account on EKS:** Use the exact `system:serviceaccount:<namespace>:<name>` value with no `*` after the `system:serviceaccount:` prefix.
* **Use a separate rule per environment:** Create distinct rules for production, staging, and development workloads rather than widening one prefix to cover them all.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-81

* Review the [WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference) for the full credential precedence, profile configuration, and rule matching reference.
* For self-managed Kubernetes clusters that aren't on EKS, see [Use WIF with Kubernetes](https://platform.claude.com/docs/en/manage-claude/wif-providers/kubernetes).


---
title: Use WIF with GitHub Actions
url: https://platform.claude.com/docs/en/manage-claude/wif-providers/github-actions
description: Authenticate GitHub Actions workflows to the Claude API with short-lived identity tokens instead of long-lived API keys.
---

Every GitHub Actions workflow run can request a signed identity token from GitHub's hosted issuer at `https://token.actions.githubusercontent.com`. With Workload Identity Federation, your workflow exchanges that token for a short-lived Anthropic access token, so your CI jobs can call the Claude API without an `ANTHROPIC_API_KEY` secret stored in your repository.

The token's `sub` claim encodes the repository and trigger context. For a push to a branch it has the form `repo:<owner>/<repo>:ref:refs/heads/<branch>`. Pull-request runs use `repo:<owner>/<repo>:pull_request`, and environment-gated deployments use `repo:<owner>/<repo>:environment:<name>`. Your federation rule matches against this claim (and others, such as `repository_owner` and `ref`) to decide which workflow runs are allowed to authenticate.


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-11

* Familiarity with [WIF concepts](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#concepts): service accounts, federation issuers, and federation rules.
* A GitHub repository where you can edit workflow files and grant the `id-token: write` permission.
* Permission to create service accounts, federation issuers, and federation rules in the Claude Console for your Anthropic organization.
* Your Anthropic organization ID. You can find it in the Claude Console under **Settings → Organization**.


## Configure your workflow

Source: https://platform.claude.com/llms-full.txt#configure-your-workflow

GitHub only issues an identity token to jobs that explicitly request it. Add the `id-token: write` permission at the workflow or job level:

Inside the job, the runner exposes two environment variables: `ACTIONS_ID_TOKEN_REQUEST_URL` and `ACTIONS_ID_TOKEN_REQUEST_TOKEN`. Call the request URL with the request token as a bearer credential and your chosen audience as a query parameter, then write the returned JSON Web Token (JWT) to a file:

If you prefer JavaScript, `actions/github-script` exposes the same capability through `core.getIDToken(audience)`:

The decoded token carries claims that describe the workflow run. Your federation rule matches against these:

See [GitHub's OIDC subject claim reference](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#example-subject-claims) for the full list of `sub` formats.


## Configure Anthropic

Source: https://platform.claude.com/llms-full.txt#configure-anthropic

In the Claude Console, open **Settings → Workload identity**, click **Connect workload**, and select the **GitHub Actions** tile. The wizard walks you through registering the issuer, creating a service account, and creating a federation rule.

The wizard creates these resources for you. Use the following values whether you enter them in the wizard or send them to the [Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api):

**Federation issuer:** GitHub publishes its OIDC discovery document and JWKS publicly, so use discovery mode. Anthropic refreshes the keys automatically when GitHub rotates them.

**Federation rule:** Match only the workflow runs you intend to trust. See [Restrict which workflows can authenticate](https://platform.claude.com/docs/en/manage-claude/wif-providers/github-actions#restrict-which-workflows-can-authenticate) for how to scope these claims safely.

Be as specific as the workload allows. Loosen `subject_prefix` to `repo:your-org/your-repo:*` (paired with a `claims.ref` constraint) only if the rule must match multiple event types from the same repository, because the trailing segment of `sub` varies between `ref:...`, `environment:...`, and `pull_request` events.


## Acquire and use a token

Source: https://platform.claude.com/llms-full.txt#acquire-and-use-a-token

Set the federation environment variables on the job and call the SDK normally. `Anthropic()` reads `ANTHROPIC_IDENTITY_TOKEN_FILE`, exchanges the JWT on the first request, and refreshes the access token automatically before it expires.

<CodeGroup>
  ```yaml Workflow
  name: Call Claude
  on: push

  permissions:
    id-token: write
    contents: read

  jobs:
    call-claude:
      runs-on: ubuntu-latest
      env:
        ANTHROPIC_FEDERATION_RULE_ID: fdrl_...
        ANTHROPIC_ORGANIZATION_ID: 00000000-0000-0000-0000-000000000000
        ANTHROPIC_SERVICE_ACCOUNT_ID: svac_...
        ANTHROPIC_WORKSPACE_ID: wrkspc_...  # required when the rule covers multiple workspaces
        ANTHROPIC_IDENTITY_TOKEN_FILE: /tmp/gha-jwt
      steps:
        - uses: actions/checkout@v5
        - name: Fetch GitHub OIDC token
          run: |
            curl -sS -H "Authorization: Bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
              "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=https://api.anthropic.com" \
              | jq -r .value > "$ANTHROPIC_IDENTITY_TOKEN_FILE"
        - name: Run your script
          run: |
            pip install anthropic
            python your_script.py

bash cURL
  JWT=$(cat /tmp/gha-jwt)

  RESPONSE=$(curl -sS https://api.anthropic.com/v1/oauth/token \
    -H "content-type: application/json" \
    --data @- <<JSON
  {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": "$JWT",
    "federation_rule_id": "$ANTHROPIC_FEDERATION_RULE_ID",
    "organization_id": "$ANTHROPIC_ORGANIZATION_ID",
    "service_account_id": "$ANTHROPIC_SERVICE_ACCOUNT_ID",
    "workspace_id": "$ANTHROPIC_WORKSPACE_ID"
  }
  JSON
  )

  ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r .access_token)

  curl https://api.anthropic.com/v1/messages \
    -H "authorization: Bearer $ACCESS_TOKEN" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello, Claude"}]
    }' | jq -r '.content[] | select(.type == "text") | .text'

python Python
  import anthropic

  # Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  # ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  # from the job environment.
  client = anthropic.Anthropic()

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
  )
  print(next(block.text for block in message.content if block.type == "text"))

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";

  // Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  // ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  // from the job environment.
  const client = new Anthropic();

  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }]
  });
  for (const block of message.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

go Go
  // Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  // ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  // from the job environment.
  client := anthropic.NewClient()

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, Claude")),
  	},
  })
  if err != nil {
  	panic(err)
  }
  for _, block := range message.Content {
  	if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  		fmt.Println(textBlock.Text)
  		break
  	}
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  var message = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .addUserMessage("Hello, Claude")
          .build());

  IO.println(message.content());

csharp C#
  // Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  // ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  // from the job environment.
  using var client = new AnthropicClient();

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello, Claude" }],
  });
  foreach (var block in message.Content)
  {
      if (block.Value is TextBlock textBlock)
      {
          Console.WriteLine(textBlock.Text);
      }
  }

bash CLI
  # Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  # ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  # from the job environment.
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello, Claude"}'

php PHP
  use Anthropic\Client;

  // Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  // ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  // from the job environment.
  $client = new Client();

  $message = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
  );
  $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
  echo $textBlock->text, PHP_EOL;

ruby Ruby
  require "anthropic"

  # Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  # ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  # from the job environment.
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}]
  )
  puts message.content.find { it.type == :text }.text
  ```
</CodeGroup>

Each GitHub-issued identity token expires roughly five minutes after issuance. The token-request endpoint (`ACTIONS_ID_TOKEN_REQUEST_URL`) stays valid for the entire job, so you can fetch a fresh token at any point. The SDK exchanges the token on first use and caches the resulting Anthropic access token. For jobs that run longer than the Anthropic token's lifetime, the SDK re-reads `ANTHROPIC_IDENTITY_TOKEN_FILE` on each refresh, so re-run the fetch step periodically (or wrap it in a background loop) to keep the file current. Alternatively, pass a token-provider callback to the SDK that calls `ACTIONS_ID_TOKEN_REQUEST_URL` directly instead of using the file path.


## Verify the setup

Source: https://platform.claude.com/llms-full.txt#verify-the-setup

A successful exchange returns an `access_token` beginning with `sk-ant-oat01-` and an `expires_in` value in seconds. A denied exchange returns an opaque `401` `authentication_error` with the fixed message `Authentication failed`, whichever check failed; in most cases the deny reason is recorded on the attempt's entry in the [authentication history page](https://platform.claude.com/settings/workload-identity-federation?tab=history), and [Troubleshoot a failed exchange](https://platform.claude.com/docs/en/manage-claude/wif-reference#troubleshoot-a-failed-exchange) walks the checks in order. The most common GitHub Actions-side cause is the `sub` claim format not matching (its trailing segment varies between `ref:...`, `environment:...`, and `pull_request` events); the history entry shows reason `match_subject_prefix`.


## Restrict which workflows can authenticate

Source: https://platform.claude.com/llms-full.txt#restrict-which-workflows-can-authenticate

<Warning>
  A `subject_prefix` of `repo:your-org/*` alone matches every repository in your organization, and without a `ref` constraint it also matches `pull_request` runs triggered from forks. Anyone who can open a pull request against a matching repository could obtain a federated Anthropic token.
</Warning>

Lock the rule's `match` block to the narrowest scope that fits your use case:

* **Pin to a single repository:** Use `subject_prefix: "repo:your-org/your-repo:*"` so other repositories in the organization do not match.
* **Pin to a protected branch:** Add `"ref": "refs/heads/main"` (or your release branch) under `claims` so pull-request runs and feature branches do not match.
* **Pin the owner explicitly:** Add `"repository_owner": "your-org"` under `claims` as a defense-in-depth check against `sub` parsing edge cases.
* **Pin to a deployment environment:** For deploy jobs, match `subject_prefix: "repo:your-org/your-repo:environment:production"` and gate that environment with required reviewers in GitHub.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-82

* [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation): full setup walkthrough, environment variables, and credential precedence.
* [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication): how federation compares to API keys.


---
title: Use WIF with Google Cloud
url: https://platform.claude.com/docs/en/manage-claude/wif-providers/gcp
description: Federate Google Cloud workloads (Cloud Run, Cloud Functions, App Engine, GCE, GKE) to the Claude API using Google-signed identity tokens instead of static API keys.
---

Any Google Cloud compute environment with access to the instance metadata server (Cloud Run, Cloud Functions, App Engine, Compute Engine (GCE), and GKE with Workload Identity) can request a Google-signed identity token for its attached service account. The token's issuer is `https://accounts.google.com`, and Anthropic can validate it directly through standard OIDC discovery, with no extra Google Cloud configuration required.

This guide shows how to register the Google issuer with Anthropic, bind a Google service account to an Anthropic service account, and have your workload exchange its identity token for a short-lived Claude API access token.


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-12

* Familiarity with [WIF concepts](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#concepts): service accounts, federation issuers, and federation rules.
* A Google Cloud project with a workload running on Cloud Run, Cloud Functions, App Engine, Compute Engine, or GKE.
* A user-managed Google service account attached to that workload (not the Compute Engine default service account).
* Permission to create service accounts, federation issuers, and federation rules in the Claude Console for your Anthropic organization.


## Configure Google Cloud

Source: https://platform.claude.com/llms-full.txt#configure-google-cloud

Google issues identity tokens automatically to any workload with an attached service account. There is nothing to enable on the Google side beyond attaching the right service account, but the steps differ slightly between standard compute and GKE.

<Tabs>
  <Tab title="Cloud Run, Cloud Functions, App Engine, GCE">
    Attach a dedicated service account to your service or instance:

    ```bash CLI
    gcloud run deploy my-service \
      --service-account inference-worker@my-project.iam.gserviceaccount.com

text wrap
    GET http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://api.anthropic.com&format=full
    Metadata-Flavor: Google

bash CLI
    gcloud auth print-identity-token \
      --audiences="https://api.anthropic.com" \
      --include-email

json
    {
      "iss": "https://accounts.google.com",
      "aud": "https://api.anthropic.com",
      "sub": "104892...",
      "azp": "104892...",
      "email": "inference-worker@my-project.iam.gserviceaccount.com",
      "email_verified": true,
      "exp": 1775527120
    }

yaml
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: inference-worker
      namespace: prod
      annotations:
        iam.gke.io/gcp-service-account: inference-worker@my-project.iam.gserviceaccount.com
    ```

    With this binding in place, the GKE metadata server returns a Google-signed token identical to the Cloud Run and GCE case: same `https://accounts.google.com` issuer, same `email` claim, same fetch URL. Configure Anthropic exactly as in the next section.

    A `format=full` token from GKE additionally includes `google.compute_engine.project_id`, `google.compute_engine.zone`, and `google.compute_engine.instance_name` claims, which you can reference in a federation rule's `condition` matcher (a CEL expression like `claims.google.compute_engine.project_id == "my-project"`) to scope access to a specific cluster or node pool.

    <Note>
      If you do not want to bind Kubernetes service accounts to Google service accounts, GKE pods can instead use the cluster's own OIDC issuer (`https://container.googleapis.com/v1/projects/PROJECT/locations/REGION/clusters/CLUSTER`) with a projected `serviceAccountToken` volume. That path uses a per-cluster issuer rather than `accounts.google.com`. See [Use WIF with Kubernetes](https://platform.claude.com/docs/en/manage-claude/wif-providers/kubernetes) for that pattern.
    </Note>
  </Tab>
</Tabs>


## Configure Anthropic

Source: https://platform.claude.com/llms-full.txt#configure-anthropic-2

In the Claude Console, open **Settings → Workload identity**, click **Connect workload**, and select the **Google Cloud** tile. The wizard walks you through registering the issuer, creating a service account, and creating a federation rule.

The wizard creates these resources for you. Use the following values whether you enter them in the wizard or send them to the [Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api):

**Federation issuer:** Google publishes its OIDC discovery document publicly, so use discovery mode. This single issuer covers every Google Cloud surface (Cloud Run, GCE, Cloud Functions, App Engine, and GKE with Workload Identity). Differentiate workloads with rules, not issuers.

**Federation rule:** Match on both the `sub` and `email` claims. `email` is the readable service-account address; `sub` is the service account's numeric unique ID, which Google never reuses, so pinning it protects the rule if the service account is deleted and a new one is later created with the same email. Find the unique ID with `gcloud iam service-accounts describe SA_EMAIL --format='value(uniqueId)'`.


## Acquire and use the token

Source: https://platform.claude.com/llms-full.txt#acquire-and-use-the-token

Inside your Google Cloud workload, fetch the identity token from the metadata server, exchange it at `POST /v1/oauth/token`, and use the returned bearer token to call the Claude API. Each Anthropic SDK handles the exchange and refresh loop for you when you supply a token-provider callable that returns a fresh identity token from the metadata server, as shown in the following examples.

<CodeGroup>
  ```bash cURL
  # Fetch the Google-signed identity token from the metadata server
  JWT=$(curl -sS -H "Metadata-Flavor: Google" \
    "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://api.anthropic.com&format=full")

  # Exchange it for an Anthropic access token
  RESPONSE=$(curl -sS https://api.anthropic.com/v1/oauth/token \
    -H "content-type: application/json" \
    --data @- <<JSON
  {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": "$JWT",
    "federation_rule_id": "$ANTHROPIC_FEDERATION_RULE_ID",
    "organization_id": "$ANTHROPIC_ORGANIZATION_ID",
    "service_account_id": "$ANTHROPIC_SERVICE_ACCOUNT_ID",
    "workspace_id": "$ANTHROPIC_WORKSPACE_ID"
  }
  JSON
  )
  ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r .access_token)

  # Call the Claude API
  curl -sS https://api.anthropic.com/v1/messages \
    -H "authorization: Bearer $ACCESS_TOKEN" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello from Cloud Run"}]
    }' | jq -r '.content[] | select(.type == "text") | .text'

python Python
  import os
  import anthropic
  import google.auth.transport.requests
  import google.oauth2.id_token
  from anthropic import WorkloadIdentityCredentials

  AUDIENCE = "https://api.anthropic.com"


  def fetch_google_identity_token() -> str:
      request = google.auth.transport.requests.Request()
      return google.oauth2.id_token.fetch_id_token(request, AUDIENCE)


  client = anthropic.Anthropic(
      credentials=WorkloadIdentityCredentials(
          identity_token_provider=fetch_google_identity_token,
          federation_rule_id=os.environ["ANTHROPIC_FEDERATION_RULE_ID"],
          organization_id=os.environ["ANTHROPIC_ORGANIZATION_ID"],
          service_account_id=os.environ["ANTHROPIC_SERVICE_ACCOUNT_ID"],
          workspace_id=os.environ.get("ANTHROPIC_WORKSPACE_ID"),
      ),
  )

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello from Cloud Run"}],
  )
  print(next(block.text for block in message.content if block.type == "text"))

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";
  import { oidcFederationProvider } from "@anthropic-ai/sdk/lib/credentials/oidc-federation";

  const METADATA_URL =
    "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://api.anthropic.com&format=full";

  async function fetchGoogleIdentityToken(): Promise<string> {
    const response = await fetch(METADATA_URL, {
      headers: { "Metadata-Flavor": "Google" }
    });
    return response.text();
  }

  const client = new Anthropic({
    credentials: oidcFederationProvider({
      identityTokenProvider: fetchGoogleIdentityToken,
      federationRuleId: process.env.ANTHROPIC_FEDERATION_RULE_ID!,
      organizationId: process.env.ANTHROPIC_ORGANIZATION_ID!,
      serviceAccountId: process.env.ANTHROPIC_SERVICE_ACCOUNT_ID,
      workspaceId: process.env.ANTHROPIC_WORKSPACE_ID,
      baseURL: "https://api.anthropic.com",
      fetch
    })
  });

  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello from Cloud Run" }]
  });
  for (const block of message.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

go Go
  const audience = "https://api.anthropic.com"

  googleIDToken := func(ctx context.Context) (string, error) {
  	creds, err := idtoken.NewCredentials(&idtoken.Options{Audience: audience})
  	if err != nil {
  		return "", err
  	}
  	tok, err := creds.Token(ctx)
  	if err != nil {
  		return "", err
  	}
  	return tok.Value, nil
  }

  client := anthropic.NewClient(
  	option.WithFederationTokenProvider(googleIDToken, option.FederationOptions{
  		FederationRuleID: os.Getenv("ANTHROPIC_FEDERATION_RULE_ID"),
  		OrganizationID:   os.Getenv("ANTHROPIC_ORGANIZATION_ID"),
  		ServiceAccountID: os.Getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"),
  		WorkspaceID:      os.Getenv("ANTHROPIC_WORKSPACE_ID"),
  	}),
  )

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello from Cloud Run")),
  	},
  })
  if err != nil {
  	panic(err)
  }
  for _, block := range message.Content {
  	if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  		fmt.Println(textBlock.Text)
  		break
  	}
  }

java Java
  HttpClient http = HttpClient.newHttpClient();
  HttpRequest metadataRequest = HttpRequest.newBuilder()
          .uri(URI.create("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://api.anthropic.com&format=full"))
          .header("Metadata-Flavor", "Google")
          .build();

  IdentityTokenProvider fetchGoogleIdentityToken = () -> {
      try {
          return http.send(metadataRequest, HttpResponse.BodyHandlers.ofString()).body();
      } catch (Exception e) {
          throw new RuntimeException(e);
      }
  };

  AnthropicClient client = AnthropicOkHttpClient.builder()
          .federationTokenProvider(
                  fetchGoogleIdentityToken,
                  System.getenv("ANTHROPIC_FEDERATION_RULE_ID"),
                  System.getenv("ANTHROPIC_ORGANIZATION_ID"),
                  System.getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"))
          .build();

  var message = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .addUserMessage("Hello from Cloud Run")
          .build());

  IO.println(message.content());

csharp C#
  using Anthropic.Credentials;
  // ...

  var credentials = new WorkloadIdentityCredentials(new WorkloadIdentityOptions
  {
      FederationRuleId = Environment.GetEnvironmentVariable("ANTHROPIC_FEDERATION_RULE_ID")!,
      OrganizationId = Environment.GetEnvironmentVariable("ANTHROPIC_ORGANIZATION_ID"),
      ServiceAccountId = Environment.GetEnvironmentVariable("ANTHROPIC_SERVICE_ACCOUNT_ID"),
      WorkspaceId = Environment.GetEnvironmentVariable("ANTHROPIC_WORKSPACE_ID"),
      IdentityTokenProvider = new MetadataTokenProvider(),
  });
  using var client = new AnthropicClient(new ClientOptions { Credentials = credentials });

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello from Cloud Run" }],
  });
  foreach (var block in message.Content)
  {
      if (block.Value is TextBlock textBlock)
      {
          Console.WriteLine(textBlock.Text);
      }
  }

  class MetadataTokenProvider : IIdentityTokenProvider
  {
      private const string METADATA_URL =
          "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://api.anthropic.com&format=full";

      private static readonly HttpClient httpClient = new()
      {
          DefaultRequestHeaders = { { "Metadata-Flavor", "Google" } },
      };

      public async Task<string> GetIdentityTokenAsync(CancellationToken ct = default)
      {
          return await httpClient.GetStringAsync(METADATA_URL, ct);
      }
  }

bash CLI
  # Write the Google-signed identity token to a file the CLI can read
  ANTHROPIC_IDENTITY_TOKEN_FILE=$(mktemp)
  curl -sS -H "Metadata-Flavor: Google" \
    "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://api.anthropic.com&format=full" \
    > "$ANTHROPIC_IDENTITY_TOKEN_FILE"
  export ANTHROPIC_IDENTITY_TOKEN_FILE

  # ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID, and
  # ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID are read from the environment.
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello from Cloud Run"}'

php PHP
  use Anthropic\Client;
  use Anthropic\Credentials\WorkloadIdentityCredentials;

  const METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://api.anthropic.com&format=full';

  $context = stream_context_create([
      'http' => ['header' => "Metadata-Flavor: Google\r\n"],
  ]);

  $credentials = new WorkloadIdentityCredentials(
      identityTokenProvider: fn() => file_get_contents(METADATA_URL, false, $context),
      federationRuleId: getenv('ANTHROPIC_FEDERATION_RULE_ID'),
      organizationId: getenv('ANTHROPIC_ORGANIZATION_ID'),
      serviceAccountId: getenv('ANTHROPIC_SERVICE_ACCOUNT_ID'),
      workspaceId: getenv('ANTHROPIC_WORKSPACE_ID') ?: null,
  );
  $client = new Client(credentials: $credentials);

  $message = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello from Cloud Run']],
  );
  $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
  echo $textBlock->text, PHP_EOL;

ruby Ruby
  require "anthropic"
  require "net/http"

  METADATA_URL = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://api.anthropic.com&format=full"

  credentials = Anthropic::WorkloadIdentityCredentials.new(
    identity_token_provider: -> { Net::HTTP.get(URI(METADATA_URL), {"Metadata-Flavor" => "Google"}) },
    federation_rule_id: ENV.fetch("ANTHROPIC_FEDERATION_RULE_ID"),
    organization_id: ENV.fetch("ANTHROPIC_ORGANIZATION_ID"),
    service_account_id: ENV.fetch("ANTHROPIC_SERVICE_ACCOUNT_ID"),
    workspace_id: ENV["ANTHROPIC_WORKSPACE_ID"]
  )
  client = Anthropic::Client.new(credentials: credentials)

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello from Cloud Run"}]
  )
  puts message.content.find { it.type == :text }.text
  ```
</CodeGroup>

Google identity tokens expire after roughly one hour. The SDKs re-invoke the token provider and re-exchange automatically before expiry. For shell scripts that run longer than the access token's `expires_in`, refresh on a timer and repeat the exchange.


## Verify the setup

Source: https://platform.claude.com/llms-full.txt#verify-the-setup-2

From inside your workload, decode the identity token and confirm the claims match your rule:

```bash cURL
curl -sS -H "Metadata-Flavor: Google" \
  "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://api.anthropic.com&format=full" \
  | jq -rR 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson'
```

Check that `iss` is `https://accounts.google.com`, `aud` is `https://api.anthropic.com`, and `email` matches the value in your federation rule. Then run the exchange from the previous section. A successful exchange returns an `access_token` beginning with `sk-ant-oat01-` and an `expires_in` value in seconds. If the exchange fails with the opaque `401` `authentication_error` response (message `Authentication failed`), check the [authentication history page](https://platform.claude.com/settings/workload-identity-federation?tab=history) for the deny reason and see [Troubleshoot a failed exchange](https://platform.claude.com/docs/en/manage-claude/wif-reference#troubleshoot-a-failed-exchange); the most common Google Cloud-side cause is the `email` claim missing (request the token with `format=full` so it is included).


## Scope your rule

Source: https://platform.claude.com/llms-full.txt#scope-your-rule-2

<Warning>
  The Google `sub` claim is the service account's opaque numeric unique ID and has no stable prefix. A `subject_prefix` with a trailing `*` matches arbitrary service accounts across every Google Cloud project, and any of them could obtain a federated Anthropic token.
</Warning>

Lock the rule's `match` block to the narrowest scope that fits your use case:

* **Match `sub` exactly:** Set the full numeric unique ID in `claims.sub` and never use `subject_prefix` for Google tokens.
* **Pin the `email` claim:** Add `claims.email` alongside `sub` so both the stable ID and the readable address must match.
* **Pin the audience:** Set `audience` to the exact value you request from the metadata server so tokens minted for other consumers are rejected.
* **Pin the project on GKE:** For `format=full` tokens, add a `condition` such as `claims.google.compute_engine.project_id == "my-project"` to restrict the rule to one project's nodes.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-83

* Read the [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) page for the full resource model and SDK credential precedence.
* Add a separate federation rule per environment (production, staging) so you can revoke one without affecting the others.


---
title: Use WIF with Kubernetes
url: https://platform.claude.com/docs/en/manage-claude/wif-providers/kubernetes
description: Authenticate to the Claude API from self-managed Kubernetes clusters using projected service account tokens.
---

Self-managed Kubernetes clusters (kubeadm, k3s, OpenShift, and on-premises distributions) sign OIDC JSON Web Tokens (JWTs) for every pod through [projected service account tokens](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/#serviceaccount-token-volume-projection). The cluster's API server acts as the OIDC issuer, and each token's `sub` claim follows the form `system:serviceaccount:<namespace>:<service-account>`. You can find your cluster's issuer URL by reading its discovery document:

```bash cURL
kubectl get --raw /.well-known/openid-configuration | jq -r .issuer
```

<Note>
  The mechanism on this page (projected service-account token, cluster API server as the OIDC issuer) is native to Kubernetes itself, so it underlies every Kubernetes distribution. If you run on a managed Kubernetes service, the cloud provider guides walk through where to find the provider-managed issuer URL: [AWS (EKS)](https://platform.claude.com/docs/en/manage-claude/wif-providers/aws#use-eks-projected-service-account-tokens), [Google Cloud (GKE)](https://platform.claude.com/docs/en/manage-claude/wif-providers/gcp), or [Azure (AKS)](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure). If your cluster runs SPIRE, the SPIRE OIDC Discovery Provider is the issuer rather than the cluster API server; see [SPIFFE](https://platform.claude.com/docs/en/manage-claude/wif-providers/spiffe). For any other distribution or a managed provider not listed there, follow this guide and use the issuer URL your cluster reports.
</Note>


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-13

* Familiarity with [WIF concepts](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#concepts): service accounts, federation issuers, and federation rules.

* A Kubernetes cluster with the [`--service-account-issuer`](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/) flag configured on the API server. Most distributions set this by default; kubeadm clusters typically use `https://kubernetes.default.svc.cluster.local`. Your platform team can confirm the value if you don't have direct access to the API server configuration.

* One of the following so Anthropic can validate token signatures:

  * The issuer's JWKS endpoint is reachable from the public internet over HTTPS on port 443, or
  * You can fetch the JWKS from inside the cluster and register it in `inline` mode (covered in [Configure Anthropic](https://platform.claude.com/docs/en/manage-claude/wif-providers/kubernetes#configure-anthropic)).

* Permission to create service accounts, federation issuers, and federation rules in the Claude Console for your Anthropic organization.


## Configure Kubernetes

Source: https://platform.claude.com/llms-full.txt#configure-kubernetes

Project a service account token into your pod with the audience and lifetime that your federation rule expects. The `serviceAccountToken` projection writes a fresh JWT to the mount path and rotates it before `expirationSeconds` elapses.

```yaml Pod
apiVersion: v1
kind: Pod
metadata:
  name: inference-worker
  namespace: inference
spec:
  serviceAccountName: inference-worker
  volumes:
    - name: anthropic-token
      projected:
        sources:
          - serviceAccountToken:
              audience: https://api.anthropic.com
              expirationSeconds: 3600
              path: token
  containers:
    - name: app
      image: your-registry/inference-worker:latest
      env:
        - name: ANTHROPIC_IDENTITY_TOKEN_FILE
          value: /var/run/secrets/anthropic.com/token
        - name: ANTHROPIC_FEDERATION_RULE_ID
          value: fdrl_...
        - name: ANTHROPIC_ORGANIZATION_ID
          value: 00000000-0000-0000-0000-000000000000
        - name: ANTHROPIC_SERVICE_ACCOUNT_ID
          value: svac_...
        - name: ANTHROPIC_WORKSPACE_ID  # required when the rule covers multiple workspaces
          value: wrkspc_...
      volumeMounts:
        - name: anthropic-token
          mountPath: /var/run/secrets/anthropic.com
          readOnly: true
```

The token issued for this pod carries `sub: "system:serviceaccount:inference:inference-worker"` and `aud: ["https://api.anthropic.com"]`.


## Configure Anthropic

Source: https://platform.claude.com/llms-full.txt#configure-anthropic-3

In the Claude Console, open **Settings → Workload identity**, click **Connect workload**, and select the **Kubernetes** tile. The wizard walks you through registering the issuer, creating a service account, and creating a federation rule.

The wizard creates these resources for you. Use the following values whether you enter them in the wizard or send them to the [Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api):

**Federation issuer:** Many self-managed clusters use an issuer URL such as `https://kubernetes.default.svc.cluster.local` that is not reachable from the public internet. If that applies to your cluster, choose the **inline** JWKS source and paste the cluster's keys. Fetch them from inside the cluster:

```bash cURL
kubectl get --raw /openid/v1/jwks

json
{
  "name": "onprem-k8s",
  "issuer_url": "https://kubernetes.default.svc.cluster.local",
  "jwks": {
    "type": "inline",
    "keys": [{ "kty": "RSA", "kid": "...", "n": "...", "e": "AQAB" }]
  }
}

json
{
  "name": "onprem-inference",
  "issuer_id": "fdis_...",
  "match": {
    "subject_prefix": "system:serviceaccount:inference:inference-worker",
    "audience": "https://api.anthropic.com"
  },
  "target": {
    "type": "service_account",
    "service_account_id": "svac_..."
  },
  "workspace_id": "wrkspc_...",
  "oauth_scope": "workspace:developer",
  "token_lifetime_seconds": 600
}
```

Be as specific as the workload allows. Loosen `subject_prefix` to `system:serviceaccount:inference:*` (the trailing `*` makes it a prefix match) only if every service account in the namespace should map to the same Anthropic service account. Add the rule's `fdrl_...` ID to your pod's `ANTHROPIC_FEDERATION_RULE_ID` environment variable.


## Acquire and use the token

Source: https://platform.claude.com/llms-full.txt#acquire-and-use-the-token-2

The pod spec in [Configure Kubernetes](https://platform.claude.com/docs/en/manage-claude/wif-providers/kubernetes#configure-kubernetes) sets `ANTHROPIC_IDENTITY_TOKEN_FILE` to the projected mount path, along with `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`, `ANTHROPIC_SERVICE_ACCOUNT_ID`, and `ANTHROPIC_WORKSPACE_ID`. With those in place, the SDK reads the token from disk on every exchange and refreshes the Anthropic access token automatically.

<CodeGroup>
  ```bash cURL
  JWT=$(cat "$ANTHROPIC_IDENTITY_TOKEN_FILE")

  ACCESS_TOKEN=$(curl -sS https://api.anthropic.com/v1/oauth/token \
    -H "content-type: application/json" \
    --data @- <<JSON | jq -r .access_token
  {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": "$JWT",
    "federation_rule_id": "$ANTHROPIC_FEDERATION_RULE_ID",
    "organization_id": "$ANTHROPIC_ORGANIZATION_ID",
    "service_account_id": "$ANTHROPIC_SERVICE_ACCOUNT_ID",
    "workspace_id": "$ANTHROPIC_WORKSPACE_ID"
  }
  JSON
  )

  curl https://api.anthropic.com/v1/messages \
    -H "authorization: Bearer $ACCESS_TOKEN" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello, Claude"}]
    }' | jq -r '.content[] | select(.type == "text") | .text'

python Python
  import anthropic

  # Reads ANTHROPIC_IDENTITY_TOKEN_FILE, ANTHROPIC_FEDERATION_RULE_ID,
  # ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID
  # from the pod's environment.
  client = anthropic.Anthropic()

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
  )
  print(next(block.text for block in message.content if block.type == "text"))

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";

  // Reads ANTHROPIC_IDENTITY_TOKEN_FILE, ANTHROPIC_FEDERATION_RULE_ID,
  // ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID
  // from the pod's environment.
  const client = new Anthropic();

  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }]
  });
  for (const block of message.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

go Go
  // Reads ANTHROPIC_IDENTITY_TOKEN_FILE, ANTHROPIC_FEDERATION_RULE_ID,
  // ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID
  // from the pod's environment.
  client := anthropic.NewClient()

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, Claude")),
  	},
  })
  if err != nil {
  	panic(err)
  }
  for _, block := range message.Content {
  	if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  		fmt.Println(textBlock.Text)
  		break
  	}
  }

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  var message = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .addUserMessage("Hello, Claude")
          .build());

  IO.println(message.content());

csharp C#
  // Reads ANTHROPIC_IDENTITY_TOKEN_FILE, ANTHROPIC_FEDERATION_RULE_ID,
  // ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID
  // from the pod's environment.
  using var client = new AnthropicClient();

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello, Claude" }],
  });
  foreach (var block in message.Content)
  {
      if (block.Value is TextBlock textBlock)
      {
          Console.WriteLine(textBlock.Text);
      }
  }

bash CLI
  # Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  # ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello, Claude"}'

php PHP
  use Anthropic\Client;

  // Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  // ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  $client = new Client();

  $message = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
  );
  $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
  echo $textBlock->text, PHP_EOL;

ruby Ruby
  require "anthropic"

  # Reads ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  # ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and ANTHROPIC_IDENTITY_TOKEN_FILE
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}]
  )
  puts message.content.find { it.type == :text }.text
  ```
</CodeGroup>


## Verify the setup

Source: https://platform.claude.com/llms-full.txt#verify-the-setup-3

A successful exchange returns an `access_token` beginning with `sk-ant-oat01-` and an `expires_in` value in seconds. If the exchange fails with the opaque `401` `authentication_error` response (message `Authentication failed`), check the [authentication history page](https://platform.claude.com/settings/workload-identity-federation?tab=history) for the deny reason and see [Troubleshoot a failed exchange](https://platform.claude.com/docs/en/manage-claude/wif-reference#troubleshoot-a-failed-exchange); the most common Kubernetes-side cause is a JWKS key mismatch (for `inline` mode, re-fetch with `kubectl get --raw /openid/v1/jwks` and update the issuer).


## Scope your rule

Source: https://platform.claude.com/llms-full.txt#scope-your-rule-3

<Warning>
  A `subject_prefix` of `system:serviceaccount:*` matches every service account in the cluster, so any pod can obtain a federated Anthropic token. Without an `audience` matcher, the rule also matches the cluster's default-audience tokens, which every pod already has projected.
</Warning>

Lock the rule's `match` block to the narrowest scope that fits your use case:

* **Pin namespace and service-account name:** Use the full `system:serviceaccount:<namespace>:<name>` value with no trailing `*`.
* **Always set an audience:** Require `audience` on the rule and set the same value on the pod's `serviceAccountToken` projection so default-audience tokens are rejected.
* **Use a separate rule per namespace:** Create a distinct rule and Anthropic service account for each namespace rather than widening one rule.
* **Scope inline-JWKS issuers to one cluster:** When several clusters share an issuer URL, register each cluster's JWKS as its own federation issuer and bind rules to that issuer only.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-84

* [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation): concepts, the token-exchange flow, and SDK configuration options.
* [WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference): environment variables, JWKS source modes, and rule match modes.


---
title: Use WIF with Microsoft Entra ID
url: https://platform.claude.com/docs/en/manage-claude/wif-providers/azure
description: Federate Azure managed identities and Entra Workload Identity with the Claude API so your Azure workloads can call Claude without static API keys.
---

Azure workloads authenticate to the Claude API by presenting a JSON Web Token (JWT) issued by Microsoft Entra ID, then exchanging it for a short-lived Anthropic access token. The setup follows the same shape on every Azure platform:

1. **Register the token audience:** Create one app registration in your Microsoft Entra tenant to represent the Claude API audience. Every workload in the tenant requests Entra tokens for it.
2. **Set up the identity for your platform:** A managed identity on VMs, VM Scale Sets, App Service, Functions, and Container Apps, or Entra Workload Identity on AKS.
3. **Configure Anthropic:** Register your tenant's Entra issuer, create a service account, and write a federation rule that matches the token's claims.
4. **Exchange at runtime:** Your workload exchanges its Entra-issued token at `POST /v1/oauth/token` for an `sk-ant-oat01-...` Anthropic access token and calls Claude with it.

On both paths the token you present to Anthropic carries your tenant-specific Entra issuer and the managed identity's object ID in the `sub` and `oid` claims; only how the workload obtains that token differs. Pick the section for where your workload runs: [Use a managed identity](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#use-a-managed-identity) for VMs, VM Scale Sets, App Service, Functions, or Container Apps; [Use Entra Workload Identity on AKS](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#use-entra-workload-identity-on-aks) for AKS.


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-14

* Familiarity with [WIF concepts](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#concepts): service accounts, federation issuers, and federation rules.
* An Azure subscription with permission to assign managed identities (or configure Entra Workload Identity on AKS).
* Permission to create one app registration and service principal in your Microsoft Entra tenant (the shared Claude API audience). Entra only issues tokens for an audience that exists in the tenant, so the [Register the token audience](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#register-the-token-audience) step is required before any token request succeeds.
* Your Microsoft Entra tenant ID. Find it in the Azure portal under **Microsoft Entra ID → Overview → Tenant ID**.
* Permission to create service accounts, federation issuers, and federation rules in the Claude Console for your Anthropic organization.


## Register the token audience

Source: https://platform.claude.com/llms-full.txt#register-the-token-audience

Microsoft Entra ID only issues a token when the requested audience exists in your tenant as an app registration with a service principal. Create one app registration to represent the Claude API audience; every workload in the tenant can request tokens for it. Without this registration, token requests fail with a "resource not found in tenant" error (`AADSTS50001` from the managed identity endpoints, `AADSTS500011` from the Entra token endpoint).

<Note>
  Use the `api://<APP_ID>` identifier URI format. Entra restricts `https://` identifier URIs to verified domains of your own tenant, so a URI such as `https://api.anthropic.com` cannot be registered in most tenants; `api://<APP_ID>` is accepted everywhere. With `requestedAccessTokenVersion: 2`, tokens for this audience are v2.0, which is what this guide assumes. If you reuse an existing registration that emits v1.0 tokens, see [If your tokens are v1.0](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#if-your-tokens-are-v1-0).
</Note>


## Use a managed identity

Source: https://platform.claude.com/llms-full.txt#use-a-managed-identity

Use this path when your workload runs on a VM, a VM Scale Set, App Service, Functions, or Container Apps. The workload requests an Entra-issued JWT for its assigned managed identity from the platform's local token endpoint, then exchanges that JWT with Anthropic.

### Configure the managed identity

<Steps>
  <Step title="Attach a managed identity">
    Enable a system-assigned or user-assigned managed identity on your Azure resource. In the Azure portal, open the resource, go to **Identity**, and turn on **System assigned** (or attach a user-assigned identity).

    After the identity is created, note its **Object (principal) ID**. This GUID appears as both the `sub` and `oid` claims in the issued token, and your Anthropic federation rule will match on it. You can find it on the resource's **Identity** page; for a user-assigned identity, it is the **Object (principal) ID** on the managed identity resource's **Overview** page. (A managed identity has only a service principal in Microsoft Entra ID, not an app registration.)
  </Step>

  <Step title="Find the platform's token endpoint">
    The platform exposes a local token endpoint once the identity is attached:

    * **VMs and VM Scale Sets:** IMDS at `http://169.254.169.254/metadata/identity/oauth2/token` with the header `Metadata: true` and `api-version=2018-02-01`.
    * **App Service, Functions, and Container Apps:** The URL in the `IDENTITY_ENDPOINT` environment variable with the header `X-IDENTITY-HEADER` set to the value of `IDENTITY_HEADER`, and `api-version=2019-08-01`. IMDS is not reachable on these platforms.

    If the resource has more than one user-assigned managed identity, add `client_id=<IDENTITY_CLIENT_ID>` to the token request to select one. Azure recommends always specifying it. Without it, the outcome depends on whether the resource also has a system-assigned identity enabled: if it does, the request silently falls back to that identity and then fails your federation rule's `oid` match; if it does not, the request fails outright as soon as a second user-assigned identity is attached.
  </Step>

  <Step title="Decode a sample token">
    Request a token from the endpoint and decode its payload to confirm the claims your federation rule needs to match. (For the decode command, see [Troubleshoot a failed exchange](https://platform.claude.com/docs/en/manage-claude/wif-reference#troubleshoot-a-failed-exchange).) A v2.0 token for a managed identity carries these claims:

| Claim | Value                                                                                                                                                                                                 | Match this when                                                                                                                                                                                                    |
    | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
    | `oid` | The managed identity's object ID, identical to `sub`                                                                                                                                                  | You want to authorize one specific managed identity. This is the default; the rule in [Configure Anthropic](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#configure-anthropic) matches it. |
    | `azp` | The calling identity's client ID                                                                                                                                                                      | You want to authorize every workload that shares one app registration. For a managed identity, `azp` is unique to that identity, so it is equivalent to `oid`.                                                     |
    | `aud` | The audience app registration's client ID (the `<APP_ID>` GUID from [Register the token audience](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#register-the-token-audience)) | Always. The rule's `audience` field must equal the token's `aud` value exactly.                                                                                                                                    |
    | `tid` | Your tenant ID                                                                                                                                                                                        | You want defense in depth. The issuer URL already pins the tenant.                                                                                                                                                 |

    If the decoded token's `ver` claim is `1.0`, the claim names and values differ. See [If your tokens are v1.0](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#if-your-tokens-are-v1-0) before continuing.
  </Step>
</Steps>

### Configure Anthropic

In the Claude Console, open **Settings → Workload identity**, click **Connect workload**, and select the **Microsoft Entra** tile. The wizard walks you through registering the issuer, creating a service account, and creating a federation rule.

The wizard creates these resources for you. Use the following values whether you enter them in the wizard or send them to the [Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api):

**Federation issuer:** Choose **v2.0 (login.microsoftonline.com)** in the wizard's **Token issuer** selector. (The selector defaults to v1; that default exists for tenants reusing older registrations that still emit v1.0 tokens.) Entra publishes an OIDC discovery document at the per-tenant issuer URL, so use discovery mode. Each Microsoft Entra tenant you federate needs its own issuer record.

<Warning>
  Managed identity workloads need `max_jwt_lifetime_seconds: 86400`. Azure issues managed identity tokens with up to 24 hours between `iat` and `exp` because it caches each resource's token for that window and offers no way to force an early refresh, and the issuer's 1-hour default rejects those tokens, so the exchange fails with the opaque `401` `authentication_error` response (message `Authentication failed`). The Connect workload wizard's Microsoft Entra tile creates the issuer with `max_jwt_lifetime_seconds` set to `7500` and provides no field to change it during creation, so finish the wizard, then open **Settings → Workload identity → Issuers**, edit the issuer, and raise the value to `86400`. You can also update the issuer through the Admin API.
</Warning>

A longer accepted lifetime means a leaked Entra token stays exchangeable for longer. If a token leaks, the lever is disabling the federation rule; a tight `oid` match limits which identities can exchange a token in the first place, as described in [Scope your rule](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#scope-your-rule).

**Federation rule:** Match on the managed identity's object ID and your tenant ID. For the v2.0 tokens this guide configures, the `audience` value is the audience app registration's client ID (the `<APP_ID>` GUID from [Register the token audience](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#register-the-token-audience)). Use the exact `aud` value from your decoded token.

`token_lifetime_seconds` is the lifetime of the Anthropic access token the exchange returns, not of the Entra token; the SDK refreshes it for you.

### Acquire and use the token

At runtime your workload fetches its Entra token, exchanges it at `POST /v1/oauth/token`, and uses the returned bearer token to call Claude. Each Anthropic SDK handles the exchange and refresh loop when you supply a token-provider callable, as shown in the following examples. The cURL tab shows the raw flow.

The samples fetch the managed identity token from the platform's token endpoint: IMDS on VMs and VM Scale Sets, or the `IDENTITY_ENDPOINT` service on App Service, Functions, and Container Apps. Replace `<APP_ID>` in the `api://<APP_ID>` resource value with the audience app registration's client ID from [Register the token audience](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#register-the-token-audience).

<Tip>
  If your workload already uses the Azure Identity client library, pass its token acquisition (`DefaultAzureCredential` with the scope `api://<APP_ID>/.default`) as the identity token provider instead of calling the token endpoints directly. The library selects the correct endpoint on every Azure platform, including AKS with Entra Workload Identity.
</Tip>

<CodeGroup>
  ```bash cURL
  # 1. Fetch the Entra-issued token (managed identity).
  #    On a VM or VM Scale Set, use IMDS. With multiple user-assigned
  #    identities, append &client_id=<IDENTITY_CLIENT_ID>.
  ENTRA_TOKEN=$(curl -sS -H "Metadata: true" \
    "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=api://<APP_ID>" \
    | jq -r .access_token)

  #    On App Service, Functions, or Container Apps, use the local token
  #    service instead (IMDS is not reachable there):
  # ENTRA_TOKEN=$(curl -sS -H "X-IDENTITY-HEADER: $IDENTITY_HEADER" \
  #   "$IDENTITY_ENDPOINT?api-version=2019-08-01&resource=api://<APP_ID>" \
  #   | jq -r .access_token)

  #    For AKS with Entra Workload Identity, use the two-hop exchange in the
  #    "Use Entra Workload Identity on AKS" section instead.

  # 2. Exchange it for an Anthropic access token.
  RESPONSE=$(curl -sS https://api.anthropic.com/v1/oauth/token \
    -H "content-type: application/json" \
    -d @- <<JSON
  {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": "$ENTRA_TOKEN",
    "federation_rule_id": "$ANTHROPIC_FEDERATION_RULE_ID",
    "organization_id": "$ANTHROPIC_ORGANIZATION_ID",
    "service_account_id": "$ANTHROPIC_SERVICE_ACCOUNT_ID",
    "workspace_id": "$ANTHROPIC_WORKSPACE_ID"
  }
  JSON
  )

  ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r .access_token)

  # 3. Call the Claude API with the bearer token.
  curl https://api.anthropic.com/v1/messages \
    -H "authorization: Bearer $ACCESS_TOKEN" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello from Azure"}]
    }' | jq -r '.content[] | select(.type == "text") | .text'

python Python
  import os

  import anthropic
  import requests
  from anthropic import WorkloadIdentityCredentials

  # The audience app registration's identifier URI (see Register the token audience).
  AUDIENCE = "api://<APP_ID>"


  def fetch_entra_token() -> str:
      """Fetch a managed identity token from the platform's token endpoint."""
      # With multiple user-assigned identities, add client_id=<IDENTITY_CLIENT_ID>
      # to the request params to select one.
      if endpoint := os.environ.get("IDENTITY_ENDPOINT"):
          # App Service, Functions, Container Apps
          response = requests.get(
              endpoint,
              headers={"X-IDENTITY-HEADER": os.environ["IDENTITY_HEADER"]},
              params={"api-version": "2019-08-01", "resource": AUDIENCE},
              timeout=5,
          )
      else:
          # VM or VM Scale Set: Azure Instance Metadata Service (IMDS)
          response = requests.get(
              "http://169.254.169.254/metadata/identity/oauth2/token",
              headers={"Metadata": "true"},
              params={"api-version": "2018-02-01", "resource": AUDIENCE},
              timeout=5,
          )
      response.raise_for_status()
      return response.json()["access_token"]


  client = anthropic.Anthropic(
      credentials=WorkloadIdentityCredentials(
          identity_token_provider=fetch_entra_token,
          federation_rule_id=os.environ["ANTHROPIC_FEDERATION_RULE_ID"],
          organization_id=os.environ["ANTHROPIC_ORGANIZATION_ID"],
          service_account_id=os.environ["ANTHROPIC_SERVICE_ACCOUNT_ID"],
          workspace_id=os.environ.get("ANTHROPIC_WORKSPACE_ID"),
      ),
  )

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello from Azure"}],
  )
  print(next(block.text for block in message.content if block.type == "text"))

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";
  import { oidcFederationProvider } from "@anthropic-ai/sdk/lib/credentials/oidc-federation";

  // The audience app registration's identifier URI (see Register the token audience).
  const AUDIENCE = "api://<APP_ID>";

  async function fetchEntraToken(): Promise<string> {
    // App Service, Functions, and Container Apps inject IDENTITY_ENDPOINT;
    // VMs and VM Scale Sets use IMDS.
    // With multiple user-assigned identities, append &client_id=<IDENTITY_CLIENT_ID>.
    const identityEndpoint = process.env.IDENTITY_ENDPOINT;
    const url = identityEndpoint
      ? `${identityEndpoint}?api-version=2019-08-01&resource=${AUDIENCE}`
      : `http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=${AUDIENCE}`;
    const headers: Record<string, string> = identityEndpoint
      ? { "X-IDENTITY-HEADER": process.env.IDENTITY_HEADER! }
      : { Metadata: "true" };
    const response = await fetch(url, { headers });
    const body = (await response.json()) as { access_token: string };
    return body.access_token;
  }

  const client = new Anthropic({
    credentials: oidcFederationProvider({
      identityTokenProvider: fetchEntraToken,
      federationRuleId: process.env.ANTHROPIC_FEDERATION_RULE_ID!,
      organizationId: process.env.ANTHROPIC_ORGANIZATION_ID!,
      serviceAccountId: process.env.ANTHROPIC_SERVICE_ACCOUNT_ID,
      workspaceId: process.env.ANTHROPIC_WORKSPACE_ID,
      baseURL: "https://api.anthropic.com",
      fetch
    })
  });

  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello from Azure" }]
  });
  for (const block of message.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

go Go
  package main

  import (
  	"context"
  	"encoding/json"
  	"fmt"
  	"net/http"
  	"os"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/option"
  )

  // The audience app registration's identifier URI (see Register the token audience).
  const audience = "api://<APP_ID>"

  // fetchEntraToken fetches a managed identity token from the platform's token
  // endpoint: IMDS on VMs and VM Scale Sets, or the IDENTITY_ENDPOINT service
  // on App Service, Functions, and Container Apps.
  func fetchEntraToken(ctx context.Context) (string, error) {
  	// With multiple user-assigned identities, append &client_id=<IDENTITY_CLIENT_ID>.
  	tokenURL := "http://169.254.169.254/metadata/identity/oauth2/token" +
  		"?api-version=2018-02-01&resource=" + audience
  	header, value := "Metadata", "true"
  	if endpoint := os.Getenv("IDENTITY_ENDPOINT"); endpoint != "" {
  		tokenURL = endpoint + "?api-version=2019-08-01&resource=" + audience
  		header, value = "X-IDENTITY-HEADER", os.Getenv("IDENTITY_HEADER")
  	}
  	req, err := http.NewRequestWithContext(ctx, http.MethodGet, tokenURL, nil)
  	if err != nil {
  		return "", err
  	}
  	req.Header.Set(header, value)
  	resp, err := http.DefaultClient.Do(req)
  	if err != nil {
  		return "", fmt.Errorf("call token endpoint: %w", err)
  	}
  	defer resp.Body.Close()
  	var body struct {
  		AccessToken string `json:"access_token"`
  	}
  	if err := json.NewDecoder(resp.Body).Decode(&body); err != nil {
  		return "", fmt.Errorf("decode token response: %w", err)
  	}
  	return body.AccessToken, nil
  }

  func main() {
  	client := anthropic.NewClient(
  		option.WithFederationTokenProvider(fetchEntraToken, option.FederationOptions{
  			FederationRuleID: os.Getenv("ANTHROPIC_FEDERATION_RULE_ID"),
  			OrganizationID:   os.Getenv("ANTHROPIC_ORGANIZATION_ID"),
  			ServiceAccountID: os.Getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"),
  			WorkspaceID:      os.Getenv("ANTHROPIC_WORKSPACE_ID"),
  		}),
  	)

  	message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 1024,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hello from Azure")),
  		},
  	})
  	if err != nil {
  		panic(err)
  	}
  	for _, block := range message.Content {
  		if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  			fmt.Println(textBlock.Text)
  			break
  		}
  	}
  }

java Java
  HttpClient http = HttpClient.newHttpClient();
  // The audience app registration's identifier URI (see Register the token audience).
  String audience = "api://<APP_ID>";
  // App Service, Functions, and Container Apps inject IDENTITY_ENDPOINT;
  // VMs and VM Scale Sets use IMDS.
  // With multiple user-assigned identities, append &client_id=<IDENTITY_CLIENT_ID>.
  String identityEndpoint = System.getenv("IDENTITY_ENDPOINT");
  HttpRequest tokenRequest = identityEndpoint != null
          ? HttpRequest.newBuilder(URI.create(identityEndpoint + "?api-version=2019-08-01&resource=" + audience))
                  .header("X-IDENTITY-HEADER", System.getenv("IDENTITY_HEADER"))
                  .build()
          : HttpRequest.newBuilder(URI.create("http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=" + audience))
                  .header("Metadata", "true")
                  .build();

  IdentityTokenProvider fetchEntraToken = () -> {
      try {
          var response = http.send(tokenRequest, HttpResponse.BodyHandlers.ofString());
          return new ObjectMapper().readTree(response.body()).get("access_token").asText();
      } catch (Exception e) {
          throw new RuntimeException(e);
      }
  };

  AnthropicClient client = AnthropicOkHttpClient.builder()
          .federationTokenProvider(
                  fetchEntraToken,
                  System.getenv("ANTHROPIC_FEDERATION_RULE_ID"),
                  System.getenv("ANTHROPIC_ORGANIZATION_ID"),
                  System.getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"),
                  System.getenv("ANTHROPIC_WORKSPACE_ID"))
          .build();

  var message = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .addUserMessage("Hello from Azure")
          .build());

  IO.println(message.content());

csharp C#
  using Anthropic.Credentials;
  // ...

  var credentials = new WorkloadIdentityCredentials(new WorkloadIdentityOptions
  {
      FederationRuleId = Environment.GetEnvironmentVariable("ANTHROPIC_FEDERATION_RULE_ID")!,
      OrganizationId = Environment.GetEnvironmentVariable("ANTHROPIC_ORGANIZATION_ID"),
      ServiceAccountId = Environment.GetEnvironmentVariable("ANTHROPIC_SERVICE_ACCOUNT_ID"),
      WorkspaceId = Environment.GetEnvironmentVariable("ANTHROPIC_WORKSPACE_ID"),
      IdentityTokenProvider = new EntraTokenProvider(),
  });
  using var client = new AnthropicClient(new ClientOptions { Credentials = credentials });

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello from Azure" }],
  });
  foreach (var block in message.Content)
  {
      if (block.Value is TextBlock textBlock)
      {
          Console.WriteLine(textBlock.Text);
      }
  }

  class EntraTokenProvider : IIdentityTokenProvider
  {
      // The audience app registration's identifier URI (see Register the token audience).
      private const string Audience = "api://<APP_ID>";

      private static readonly HttpClient httpClient = new();

      public async Task<string> GetIdentityTokenAsync(CancellationToken ct = default)
      {
          // App Service, Functions, and Container Apps inject IDENTITY_ENDPOINT;
          // VMs and VM Scale Sets use IMDS.
          // With multiple user-assigned identities, append &client_id=<IDENTITY_CLIENT_ID>.
          var identityEndpoint = Environment.GetEnvironmentVariable("IDENTITY_ENDPOINT");
          using var request = identityEndpoint is not null
              ? new HttpRequestMessage(HttpMethod.Get,
                  $"{identityEndpoint}?api-version=2019-08-01&resource={Audience}")
              {
                  Headers = { { "X-IDENTITY-HEADER", Environment.GetEnvironmentVariable("IDENTITY_HEADER") } },
              }
              : new HttpRequestMessage(HttpMethod.Get,
                  $"http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource={Audience}")
              {
                  Headers = { { "Metadata", "true" } },
              };
          using var response = await httpClient.SendAsync(request, ct);
          response.EnsureSuccessStatusCode();
          using var json = await JsonDocument.ParseAsync(
              await response.Content.ReadAsStreamAsync(ct), default, ct);
          return json.RootElement.GetProperty("access_token").GetString()!;
      }
  }

php PHP
  use Anthropic\Client;
  use Anthropic\Credentials\WorkloadIdentityCredentials;

  // The audience app registration's identifier URI (see Register the token audience).
  const AUDIENCE = 'api://<APP_ID>';

  function fetchEntraToken(): string
  {
      // App Service, Functions, and Container Apps inject IDENTITY_ENDPOINT;
      // VMs and VM Scale Sets use IMDS.
      // With multiple user-assigned identities, append &client_id=<IDENTITY_CLIENT_ID>.
      $identityEndpoint = getenv('IDENTITY_ENDPOINT');
      if ($identityEndpoint !== false) {
          $url = $identityEndpoint . '?api-version=2019-08-01&resource=' . AUDIENCE;
          $header = 'X-IDENTITY-HEADER: ' . getenv('IDENTITY_HEADER');
      } else {
          $url = 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=' . AUDIENCE;
          $header = 'Metadata: true';
      }
      $context = stream_context_create([
          'http' => ['header' => $header . "\r\n"],
      ]);
      $body = json_decode(file_get_contents($url, false, $context), true);
      return $body['access_token'];
  }

  $credentials = new WorkloadIdentityCredentials(
      identityTokenProvider: fetchEntraToken(...),
      federationRuleId: getenv('ANTHROPIC_FEDERATION_RULE_ID'),
      organizationId: getenv('ANTHROPIC_ORGANIZATION_ID'),
      serviceAccountId: getenv('ANTHROPIC_SERVICE_ACCOUNT_ID'),
      workspaceId: getenv('ANTHROPIC_WORKSPACE_ID') ?: null,
  );
  $client = new Client(credentials: $credentials);

  $message = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello from Azure']],
  );
  $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
  echo $textBlock->text, PHP_EOL;

ruby Ruby
  require "anthropic"
  require "json"
  require "net/http"

  # The audience app registration's identifier URI (see Register the token audience).
  AUDIENCE = "api://<APP_ID>"

  def fetch_entra_token
    # App Service, Functions, and Container Apps inject IDENTITY_ENDPOINT;
    # VMs and VM Scale Sets use IMDS.
    # With multiple user-assigned identities, append &client_id=<IDENTITY_CLIENT_ID>.
    if (endpoint = ENV["IDENTITY_ENDPOINT"])
      url = "#{endpoint}?api-version=2019-08-01&resource=#{AUDIENCE}"
      headers = {"X-IDENTITY-HEADER" => ENV.fetch("IDENTITY_HEADER")}
    else
      url = "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=#{AUDIENCE}"
      headers = {"Metadata" => "true"}
    end
    response = Net::HTTP.get(URI(url), headers)
    JSON.parse(response).fetch("access_token")
  end

  credentials = Anthropic::WorkloadIdentityCredentials.new(
    identity_token_provider: -> { fetch_entra_token },
    federation_rule_id: ENV.fetch("ANTHROPIC_FEDERATION_RULE_ID"),
    organization_id: ENV.fetch("ANTHROPIC_ORGANIZATION_ID"),
    service_account_id: ENV.fetch("ANTHROPIC_SERVICE_ACCOUNT_ID"),
    workspace_id: ENV["ANTHROPIC_WORKSPACE_ID"]
  )
  client = Anthropic::Client.new(credentials: credentials)

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello from Azure"}]
  )
  puts message.content.find { it.type == :text }.text

bash CLI
  # Write the Entra-issued access token to a file the CLI can read.
  # Shown for a VM or VM Scale Set (IMDS). On App Service, Functions, or
  # Container Apps, fetch from "$IDENTITY_ENDPOINT?api-version=2019-08-01&resource=api://<APP_ID>"
  # with -H "X-IDENTITY-HEADER: $IDENTITY_HEADER" instead.
  # With multiple user-assigned identities, append &client_id=<IDENTITY_CLIENT_ID>.
  ANTHROPIC_IDENTITY_TOKEN_FILE=$(mktemp)
  trap 'rm -f "$ANTHROPIC_IDENTITY_TOKEN_FILE"' EXIT
  curl -sS -H "Metadata: true" \
    "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=api://<APP_ID>" \
    | jq -r .access_token > "$ANTHROPIC_IDENTITY_TOKEN_FILE"
  export ANTHROPIC_IDENTITY_TOKEN_FILE

  # ANTHROPIC_FEDERATION_RULE_ID, ANTHROPIC_ORGANIZATION_ID,
  # ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID are read from the environment.
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello from Azure"}'
  ```
</CodeGroup>

### Verify the setup

From your Azure resource, run the cURL exchange shown in [Acquire and use the token](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#acquire-and-use-the-token) and confirm that `POST /v1/oauth/token` returns a `200` with an `access_token` beginning with `sk-ant-oat01-` and an `expires_in` value in seconds. If the exchange fails with the opaque `401` `authentication_error` response (message `Authentication failed`), check the [authentication history page](https://platform.claude.com/settings/workload-identity-federation?tab=history) for the deny reason, then decode the Entra token (see [Troubleshoot a failed exchange](https://platform.claude.com/docs/en/manage-claude/wif-reference#troubleshoot-a-failed-exchange) for the command) and check the most common Azure-side causes:

* **Issuer mismatch:** The registered `issuer_url` must match the token's `iss` claim exactly. A v2.0 token carries `https://login.microsoftonline.com/<TENANT_ID>/v2.0`; if the decoded `ver` claim is `1.0`, see [If your tokens are v1.0](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#if-your-tokens-are-v1-0).
* **Token lifetime:** Managed identity tokens carry up to 24 hours between `iat` and `exp`. If the issuer still has the wizard's `7500` (or the 1-hour default), raise `max_jwt_lifetime_seconds` to `86400` as described in [Configure Anthropic](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#configure-anthropic).
* **Audience mismatch:** The rule's `audience` must equal the token's `aud` exactly: the audience app registration's client ID for the v2.0 tokens this guide configures.
* **Claim name mismatch:** A rule that matches on a claim the token does not carry never passes. v1.0 tokens carry the client ID in `appid`, not `azp`; see [If your tokens are v1.0](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#if-your-tokens-are-v1-0).


## Use Entra Workload Identity on AKS

Source: https://platform.claude.com/llms-full.txt#use-entra-workload-identity-on-aks

Use this path when your workload runs in an AKS pod. Entra Workload Identity federates a Kubernetes service account with a user-assigned managed identity: Kubernetes projects a service account token (signed by the AKS cluster's OIDC issuer) into the pod at the path in `AZURE_FEDERATED_TOKEN_FILE`. That projected token is not an Entra-issued token, so to stay on the Entra-mediated path described on this page, the workload performs a two-hop exchange: it first redeems the projected token at `https://login.microsoftonline.com/<TENANT_ID>/oauth2/v2.0/token` (federated `client_credentials` grant) for an Entra-issued access token, then passes that Entra token to the Anthropic SDK as the identity token.

<Tip>
  AKS pods can alternatively skip the Entra exchange and present the Kubernetes-projected service account token to Anthropic directly. That path registers your AKS cluster's OIDC issuer with Anthropic instead of your Entra tenant. See [Use WIF with Kubernetes](https://platform.claude.com/docs/en/manage-claude/wif-providers/kubernetes) for that flow.
</Tip>

### Configure Entra Workload Identity

<Steps>
  <Step title="Enable the OIDC issuer and workload identity on your cluster">
    Enabling workload identity installs the `azure-workload-identity` mutating webhook for you; deploy it manually only on non-AKS clusters. Capture the cluster's OIDC issuer URL for the federated credential you create in a later step.

</Step>

  <Step title="Create a user-assigned managed identity">
    Capture two values from the identity: the **Client ID** goes into the service account annotation (and is injected into the pod as `AZURE_CLIENT_ID`), and the **Object (principal) ID** appears as the `oid` claim that your Anthropic federation rule matches.

</Step>

  <Step title="Create the annotated Kubernetes service account">
    The `azure-workload-identity` webhook reads the `azure.workload.identity/client-id` annotation to inject `AZURE_CLIENT_ID` into the pod, which the samples in [Acquire and use the token](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#acquire-and-use-the-token-2) read from the environment.

</Step>

  <Step title="Create the federated credential on the managed identity">
    The federated credential trusts your cluster's OIDC issuer for that specific service account. The `--audience api://AzureADTokenExchange` value is Entra's fixed audience for incoming Kubernetes service account tokens; it is unrelated to the Claude API audience you registered earlier.

</Step>

  <Step title="Label the pod and set its service account">
    The pod must carry the `azure.workload.identity/use: "true"` label and run as the annotated service account. The webhook then injects `AZURE_FEDERATED_TOKEN_FILE`, `AZURE_CLIENT_ID`, and `AZURE_TENANT_ID` into the pod. The file at `AZURE_FEDERATED_TOKEN_FILE` contains the Kubernetes-projected service account token, signed by the AKS cluster's OIDC issuer.

</Step>

  <Step title="Decode a sample token">
    The token your Anthropic federation rule sees is not the projected file; it is the Entra-issued token returned by the `client_credentials` exchange. From inside a labeled pod, run step 1 of the cURL sample in [Acquire and use the token](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#acquire-and-use-the-token-2) and decode the result. It carries the same claim shape as the managed identity path:

`sub` and `oid` are the managed identity's object ID, `aud` is the audience app registration's client ID, and `azp` is the managed identity's client ID (the value of `AZURE_CLIENT_ID`). The lifetime differs from the managed identity path: `client_credentials` tokens default to a random 60 to 90 minute window between `iat` and `exp`, not 24 hours.
  </Step>
</Steps>

### Configure Anthropic

In the Claude Console, open **Settings → Workload identity**, click **Connect workload**, and select the **Microsoft Entra** tile. The wizard walks you through registering the issuer, creating a service account, and creating a federation rule.

The wizard creates these resources for you. Use the following values whether you enter them in the wizard or send them to the [Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api):

**Federation issuer:** Choose **v2.0 (login.microsoftonline.com)** in the wizard's **Token issuer** selector. (The selector defaults to v1; that default exists for tenants reusing older registrations that still emit v1.0 tokens.) Entra publishes an OIDC discovery document at the per-tenant issuer URL, so use discovery mode. Each Microsoft Entra tenant you federate needs its own issuer record.

<Warning>
  The Connect workload wizard's Microsoft Entra tile creates the issuer with `max_jwt_lifetime_seconds` set to `7500` (just over 2 hours), which covers the default 60 to 90 minute lifetime of `client_credentials` tokens. A tenant token-lifetime policy or Continuous Access Evaluation (CAE) can extend that lifetime. If your decoded token's `exp` minus `iat` exceeds 7500 seconds, edit the issuer in **Settings → Workload identity → Issuers** and raise `max_jwt_lifetime_seconds` to match, or exchanges fail with the opaque `401` `authentication_error` response (message `Authentication failed`). If your tenant also runs managed-identity workloads from [Use a managed identity](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#use-a-managed-identity), use that section's `86400` value, which covers both paths.
</Warning>

A longer accepted lifetime means a leaked Entra token stays exchangeable for longer. If a token leaks, the lever is disabling the federation rule; a tight `oid` match limits which identities can exchange a token in the first place, as described in [Scope your rule](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#scope-your-rule).

**Federation rule:** Match on the managed identity's object ID and your tenant ID. For the v2.0 tokens this guide configures, the `audience` value is the audience app registration's client ID (the `<APP_ID>` GUID from [Register the token audience](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#register-the-token-audience)). Use the exact `aud` value from your decoded token.

`token_lifetime_seconds` is the lifetime of the Anthropic access token the exchange returns, not of the Entra token; the SDK refreshes it for you.

### Acquire and use the token

At runtime the pod performs the two-hop exchange: it sends the Kubernetes-projected token (the file at `AZURE_FEDERATED_TOKEN_FILE`) to Entra's token endpoint as a federated `client_credentials` assertion, then exchanges the resulting Entra access token at `POST /v1/oauth/token`. Each Anthropic SDK handles the second exchange and the refresh loop when you supply the Entra fetch as a token-provider callable, as shown in the following examples. The cURL tab shows the raw flow.

Two different client IDs appear in the samples. `<APP_ID>` is the audience app registration's client ID from [Register the token audience](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#register-the-token-audience); the scope `api://<APP_ID>/.default` asks Entra for a token addressed to that audience. `$AZURE_CLIENT_ID` is the managed identity's client ID, injected by the webhook, and identifies the caller. Do not substitute one for the other.

<Tip>
  If your workload already uses the Azure Identity client library, pass its token acquisition (`DefaultAzureCredential` with the scope `api://<APP_ID>/.default`) as the identity token provider instead of performing the two-hop exchange yourself. The library reads the same `AZURE_FEDERATED_TOKEN_FILE`, `AZURE_CLIENT_ID`, and `AZURE_TENANT_ID` environment variables and handles the Entra exchange.
</Tip>

<CodeGroup>
  ```bash cURL
  # 1. Exchange the Kubernetes-projected token (at $AZURE_FEDERATED_TOKEN_FILE)
  #    for an Entra-issued JWT.
  ENTRA_JWT=$(curl -sS "https://login.microsoftonline.com/$AZURE_TENANT_ID/oauth2/v2.0/token" \
    -d grant_type=client_credentials \
    -d "client_id=$AZURE_CLIENT_ID" \
    --data-urlencode "scope=api://<APP_ID>/.default" \
    -d client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer \
    --data-urlencode "client_assertion@$AZURE_FEDERATED_TOKEN_FILE" \
    | jq -r .access_token)

  # 2. Exchange the Entra JWT for an Anthropic access token.
  ACCESS_TOKEN=$(curl -sS https://api.anthropic.com/v1/oauth/token \
    -H "content-type: application/json" \
    -d @- <<JSON | jq -r .access_token
  {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": "$ENTRA_JWT",
    "federation_rule_id": "$ANTHROPIC_FEDERATION_RULE_ID",
    "organization_id": "$ANTHROPIC_ORGANIZATION_ID",
    "service_account_id": "$ANTHROPIC_SERVICE_ACCOUNT_ID",
    "workspace_id": "$ANTHROPIC_WORKSPACE_ID"
  }
  JSON
  )

  # 3. Call the Claude API.
  curl -sS https://api.anthropic.com/v1/messages \
    -H "authorization: Bearer $ACCESS_TOKEN" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [{"role": "user", "content": "Hello from Azure"}]
    }' | jq -r '.content[] | select(.type == "text") | .text'

python Python
  import os
  from pathlib import Path

  import anthropic
  import requests
  from anthropic import WorkloadIdentityCredentials


  def fetch_entra_token_via_federation() -> str:
      federated_token = Path(os.environ["AZURE_FEDERATED_TOKEN_FILE"]).read_text()
      response = requests.post(
          f"https://login.microsoftonline.com/{os.environ['AZURE_TENANT_ID']}/oauth2/v2.0/token",
          data={
              "client_id": os.environ["AZURE_CLIENT_ID"],
              "grant_type": "client_credentials",
              "scope": "api://<APP_ID>/.default",
              "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
              "client_assertion": federated_token,
          },
          timeout=5,
      )
      response.raise_for_status()
      return response.json()["access_token"]


  client = anthropic.Anthropic(
      credentials=WorkloadIdentityCredentials(
          identity_token_provider=fetch_entra_token_via_federation,
          federation_rule_id=os.environ["ANTHROPIC_FEDERATION_RULE_ID"],
          organization_id=os.environ["ANTHROPIC_ORGANIZATION_ID"],
          service_account_id=os.environ["ANTHROPIC_SERVICE_ACCOUNT_ID"],
          workspace_id=os.environ.get("ANTHROPIC_WORKSPACE_ID"),
      ),
  )

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello from Azure"}],
  )
  print(next(block.text for block in message.content if block.type == "text"))

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";
  import { oidcFederationProvider } from "@anthropic-ai/sdk/lib/credentials/oidc-federation";
  import { readFile } from "node:fs/promises";

  async function fetchEntraTokenViaFederation(): Promise<string> {
    const federatedToken = await readFile(process.env.AZURE_FEDERATED_TOKEN_FILE!, "utf8");
    const response = await fetch(
      `https://login.microsoftonline.com/${process.env.AZURE_TENANT_ID}/oauth2/v2.0/token`,
      {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          client_id: process.env.AZURE_CLIENT_ID!,
          grant_type: "client_credentials",
          scope: "api://<APP_ID>/.default",
          client_assertion_type: "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
          client_assertion: federatedToken
        })
      }
    );
    const body = (await response.json()) as { access_token: string };
    return body.access_token;
  }

  const client = new Anthropic({
    credentials: oidcFederationProvider({
      identityTokenProvider: fetchEntraTokenViaFederation,
      federationRuleId: process.env.ANTHROPIC_FEDERATION_RULE_ID!,
      organizationId: process.env.ANTHROPIC_ORGANIZATION_ID!,
      serviceAccountId: process.env.ANTHROPIC_SERVICE_ACCOUNT_ID,
      workspaceId: process.env.ANTHROPIC_WORKSPACE_ID,
      baseURL: "https://api.anthropic.com",
      fetch
    })
  });

  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello from Azure" }]
  });
  for (const block of message.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

go Go
  package main

  import (
  	"context"
  	"encoding/json"
  	"fmt"
  	"net/http"
  	"net/url"
  	"os"
  	"strings"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/option"
  )

  func fetchEntraTokenViaFederation(ctx context.Context) (string, error) {
  	federatedToken, err := os.ReadFile(os.Getenv("AZURE_FEDERATED_TOKEN_FILE"))
  	if err != nil {
  		return "", err
  	}
  	form := url.Values{
  		"client_id":             {os.Getenv("AZURE_CLIENT_ID")},
  		"grant_type":            {"client_credentials"},
  		"scope":                 {"api://<APP_ID>/.default"},
  		"client_assertion_type": {"urn:ietf:params:oauth:client-assertion-type:jwt-bearer"},
  		"client_assertion":      {strings.TrimSpace(string(federatedToken))},
  	}
  	tokenURL := "https://login.microsoftonline.com/" + os.Getenv("AZURE_TENANT_ID") + "/oauth2/v2.0/token"
  	req, err := http.NewRequestWithContext(ctx, http.MethodPost, tokenURL, strings.NewReader(form.Encode()))
  	if err != nil {
  		return "", err
  	}
  	req.Header.Set("content-type", "application/x-www-form-urlencoded")
  	resp, err := http.DefaultClient.Do(req)
  	if err != nil {
  		return "", err
  	}
  	defer resp.Body.Close()
  	var body struct {
  		AccessToken string `json:"access_token"`
  	}
  	if err := json.NewDecoder(resp.Body).Decode(&body); err != nil {
  		return "", err
  	}
  	return body.AccessToken, nil
  }

  func main() {
  	client := anthropic.NewClient(
  		option.WithFederationTokenProvider(option.IdentityTokenFunc(fetchEntraTokenViaFederation), option.FederationOptions{
  			FederationRuleID: os.Getenv("ANTHROPIC_FEDERATION_RULE_ID"),
  			OrganizationID:   os.Getenv("ANTHROPIC_ORGANIZATION_ID"),
  			ServiceAccountID: os.Getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"),
  			WorkspaceID:      os.Getenv("ANTHROPIC_WORKSPACE_ID"),
  		}),
  	)
  	message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 1024,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hello from Azure")),
  		},
  	})
  	if err != nil {
  		panic(err)
  	}
  	for _, block := range message.Content {
  		if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  			fmt.Println(textBlock.Text)
  			break
  		}
  	}
  }

java Java
  IdentityTokenProvider fetchEntraTokenViaFederation = () -> {
      try {
          var form = Map.of(
                          "client_id", System.getenv("AZURE_CLIENT_ID"),
                          "grant_type", "client_credentials",
                          "scope", "api://<APP_ID>/.default",
                          "client_assertion_type", "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                          "client_assertion", Files.readString(Path.of(System.getenv("AZURE_FEDERATED_TOKEN_FILE"))))
                  .entrySet().stream()
                  .map(entry -> entry.getKey() + "=" + URLEncoder.encode(entry.getValue(), UTF_8))
                  .collect(Collectors.joining("&"));
          var request = HttpRequest.newBuilder(URI.create(
                          "https://login.microsoftonline.com/" + System.getenv("AZURE_TENANT_ID") + "/oauth2/v2.0/token"))
                  .header("content-type", "application/x-www-form-urlencoded")
                  .POST(HttpRequest.BodyPublishers.ofString(form))
                  .build();
          var response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
          return new ObjectMapper().readTree(response.body()).get("access_token").asText();
      } catch (Exception e) {
          throw new RuntimeException(e);
      }
  };

  AnthropicClient client = AnthropicOkHttpClient.builder()
          .federationTokenProvider(
                  fetchEntraTokenViaFederation,
                  System.getenv("ANTHROPIC_FEDERATION_RULE_ID"),
                  System.getenv("ANTHROPIC_ORGANIZATION_ID"),
                  System.getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"),
                  System.getenv("ANTHROPIC_WORKSPACE_ID"))
          .build();

  var message = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .addUserMessage("Hello from Azure")
          .build());

  IO.println(message.content());

csharp C#
  using Anthropic.Credentials;
  // ...

  var credentials = new WorkloadIdentityCredentials(new WorkloadIdentityOptions
  {
      FederationRuleId = Environment.GetEnvironmentVariable("ANTHROPIC_FEDERATION_RULE_ID")!,
      OrganizationId = Environment.GetEnvironmentVariable("ANTHROPIC_ORGANIZATION_ID"),
      ServiceAccountId = Environment.GetEnvironmentVariable("ANTHROPIC_SERVICE_ACCOUNT_ID"),
      WorkspaceId = Environment.GetEnvironmentVariable("ANTHROPIC_WORKSPACE_ID"),
      IdentityTokenProvider = new EntraFederationTokenProvider(),
  });
  using var client = new AnthropicClient(new ClientOptions { Credentials = credentials });

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello from Azure" }],
  });
  foreach (var block in message.Content)
  {
      if (block.Value is TextBlock textBlock)
      {
          Console.WriteLine(textBlock.Text);
      }
  }

  class EntraFederationTokenProvider : IIdentityTokenProvider
  {
      private static readonly HttpClient Http = new();

      public async Task<string> GetIdentityTokenAsync(CancellationToken ct = default)
      {
          var federatedToken = await File.ReadAllTextAsync(
              Environment.GetEnvironmentVariable("AZURE_FEDERATED_TOKEN_FILE")!, ct);
          var tenantId = Environment.GetEnvironmentVariable("AZURE_TENANT_ID");
          var form = new FormUrlEncodedContent(new Dictionary<string, string>
          {
              ["client_id"] = Environment.GetEnvironmentVariable("AZURE_CLIENT_ID")!,
              ["grant_type"] = "client_credentials",
              ["scope"] = "api://<APP_ID>/.default",
              ["client_assertion_type"] = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
              ["client_assertion"] = federatedToken,
          });
          var response = await Http.PostAsync(
              $"https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token", form, ct);
          response.EnsureSuccessStatusCode();
          using var json = await JsonDocument.ParseAsync(
              await response.Content.ReadAsStreamAsync(ct), default, ct);
          return json.RootElement.GetProperty("access_token").GetString()!;
      }
  }

php PHP
  use Anthropic\Client;
  use Anthropic\Credentials\WorkloadIdentityCredentials;

  function fetchEntraTokenViaFederation(): string
  {
      $ch = curl_init('https://login.microsoftonline.com/' . getenv('AZURE_TENANT_ID') . '/oauth2/v2.0/token');
      curl_setopt_array($ch, [
          CURLOPT_RETURNTRANSFER => true,
          CURLOPT_POSTFIELDS => http_build_query([
              'client_id' => getenv('AZURE_CLIENT_ID'),
              'grant_type' => 'client_credentials',
              'scope' => 'api://<APP_ID>/.default',
              'client_assertion_type' => 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
              'client_assertion' => file_get_contents(getenv('AZURE_FEDERATED_TOKEN_FILE')),
          ]),
      ]);
      $body = json_decode(curl_exec($ch), true);
      curl_close($ch);
      return $body['access_token'];
  }

  $client = new Client(
      credentials: new WorkloadIdentityCredentials(
          identityTokenProvider: fetchEntraTokenViaFederation(...),
          federationRuleId: getenv('ANTHROPIC_FEDERATION_RULE_ID'),
          organizationId: getenv('ANTHROPIC_ORGANIZATION_ID'),
          serviceAccountId: getenv('ANTHROPIC_SERVICE_ACCOUNT_ID'),
          workspaceId: getenv('ANTHROPIC_WORKSPACE_ID') ?: null,
      ),
  );

  $message = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello from Azure']],
  );
  $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
  echo $textBlock->text, PHP_EOL;

ruby Ruby
  require "anthropic"
  require "json"
  require "net/http"

  def fetch_entra_token_via_federation
    tenant_id = ENV.fetch("AZURE_TENANT_ID")
    federated_token = File.read(ENV.fetch("AZURE_FEDERATED_TOKEN_FILE"))
    response = Net::HTTP.post_form(
      URI("https://login.microsoftonline.com/#{tenant_id}/oauth2/v2.0/token"),
      "client_id" => ENV.fetch("AZURE_CLIENT_ID"),
      "grant_type" => "client_credentials",
      "scope" => "api://<APP_ID>/.default",
      "client_assertion_type" => "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
      "client_assertion" => federated_token
    )
    JSON.parse(response.body).fetch("access_token")
  end

  client = Anthropic::Client.new(
    credentials: Anthropic::WorkloadIdentityCredentials.new(
      identity_token_provider: -> { fetch_entra_token_via_federation },
      federation_rule_id: ENV.fetch("ANTHROPIC_FEDERATION_RULE_ID"),
      organization_id: ENV.fetch("ANTHROPIC_ORGANIZATION_ID"),
      service_account_id: ENV.fetch("ANTHROPIC_SERVICE_ACCOUNT_ID"),
      workspace_id: ENV["ANTHROPIC_WORKSPACE_ID"]
    )
  )

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello from Azure"}]
  )
  puts message.content.find { it.type == :text }.text

bash CLI
  # 1. Exchange the Kubernetes-projected token for an Entra-issued access
  # token and write it to a temp file the CLI can read.
  ANTHROPIC_IDENTITY_TOKEN_FILE=$(mktemp)
  trap 'rm -f "$ANTHROPIC_IDENTITY_TOKEN_FILE"' EXIT
  curl -sS "https://login.microsoftonline.com/$AZURE_TENANT_ID/oauth2/v2.0/token" \
    -d client_id="$AZURE_CLIENT_ID" \
    -d grant_type=client_credentials \
    --data-urlencode "scope=api://<APP_ID>/.default" \
    -d client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer \
    --data-urlencode client_assertion@"$AZURE_FEDERATED_TOKEN_FILE" \
    | jq -r .access_token > "$ANTHROPIC_IDENTITY_TOKEN_FILE"
  export ANTHROPIC_IDENTITY_TOKEN_FILE

  # 2. Call the Claude API. ANTHROPIC_FEDERATION_RULE_ID,
  # ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID are read
  # from the environment.
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello from Azure"}'
  ```
</CodeGroup>

### Verify the setup

From inside a labeled pod, run the cURL exchange shown in [Acquire and use the token](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#acquire-and-use-the-token-2) and confirm that `POST /v1/oauth/token` returns a `200` with an `access_token` beginning with `sk-ant-oat01-` and an `expires_in` value in seconds. If the exchange fails with the opaque `401` `authentication_error` response (message `Authentication failed`), check the [authentication history page](https://platform.claude.com/settings/workload-identity-federation?tab=history) for the deny reason, then decode the Entra-issued token from step 1 (see [Troubleshoot a failed exchange](https://platform.claude.com/docs/en/manage-claude/wif-reference#troubleshoot-a-failed-exchange) for the command) and check the most common Azure-side causes:

* **Issuer mismatch:** The registered `issuer_url` must match the token's `iss` claim exactly. A v2.0 token carries `https://login.microsoftonline.com/<TENANT_ID>/v2.0`; if the decoded `ver` claim is `1.0`, see [If your tokens are v1.0](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#if-your-tokens-are-v1-0).
* **Token lifetime:** If a tenant token-lifetime policy or CAE extends the `client_credentials` token past 7500 seconds, raise the issuer's `max_jwt_lifetime_seconds` as described in [Configure Anthropic](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#configure-anthropic-2).
* **Audience mismatch:** The rule's `audience` must equal the token's `aud` exactly: the audience app registration's client ID for the v2.0 tokens this guide configures.
* **Claim name mismatch:** A rule that matches on a claim the token does not carry never passes. v1.0 tokens carry the client ID in `appid`, not `azp`; see [If your tokens are v1.0](https://platform.claude.com/docs/en/manage-claude/wif-providers/azure#if-your-tokens-are-v1-0).


## If your tokens are v1.0

Source: https://platform.claude.com/llms-full.txt#if-your-tokens-are-v1-0

This guide configures the audience app registration with `api.requestedAccessTokenVersion: 2`, so every token it shows is v2.0. If you reuse an existing registration that leaves `requestedAccessTokenVersion` unset, Entra issues v1.0 tokens instead. Decode a sample token and check its `ver` claim; if it is `1.0`, four things change:

* **Issuer:** The `iss` claim is `https://sts.windows.net/<TENANT_ID>/` instead of `https://login.microsoftonline.com/<TENANT_ID>/v2.0`. Register the issuer URL exactly as your token's `iss` claim carries it. The two URLs share the same JWKS, so discovery mode works for either.
* **Wizard selector:** Pick **v1 (sts.windows.net)** in the Connect workload wizard's **Token issuer** selector instead of **v2.0 (login.microsoftonline.com)**.
* **Audience:** The `aud` claim is the identifier URI you passed as `resource` (for example, `api://<APP_ID>`), not the registration's client ID. Set the federation rule's `audience` to the exact `aud` value from your decoded token.
* **Client ID claim:** The calling identity's client ID appears in `appid`, not `azp`. The two claims never appear in the same token, so a rule that matches on `azp` never passes against a v1.0 token.

The `oid`, `sub`, and `tid` claims carry the same values in both versions, so the rest of this guide applies unchanged.


## Scope your rule

Source: https://platform.claude.com/llms-full.txt#scope-your-rule-4

A federation rule can match the token's subject with `subject_prefix` in addition to (or instead of) the `claims` map; see [Rule matching semantics](https://platform.claude.com/docs/en/manage-claude/wif-reference#rule-matching-semantics) for how the fields combine. Entra `sub` values for these identities are fixed-length canonical GUIDs, so a `subject_prefix` containing the full 36-character object ID matches only that subject; this is a property of Entra's subject format, not of `subject_prefix` in general.

<Warning>
  Every identity in your tenant can request a token for the registered audience, so `audience` and `tid` alone do not identify a specific workload. A rule that omits an `oid` (or `azp`/`appid`) match, or that uses a wildcard or partial-GUID `subject_prefix`, authorizes every managed identity and service principal in the tenant.
</Warning>

Lock the rule's `match` block to the narrowest scope that fits your use case:

* **Match `oid` as an exact value:** Set `claims.oid` to the managed identity's full object ID. A `subject_prefix` set to that full object ID is equivalent (the Console wizard sets both); never use a wildcard or partial-GUID `subject_prefix`, which matches more identities than you intend.
* **Pin `tid` as defense in depth:** The issuer URL already pins your tenant, but adding `claims.tid` guards against configuration drift if the issuer record is later edited.
* **Pin the audience:** Set `audience` to the exact `aud` value from your decoded token so tokens minted for other applications are rejected.
* **Use a separate rule for each managed identity:** Create one rule for each identity rather than one rule that authorizes several, so you can revoke a single workload's access without affecting others.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-85

* Review the full configuration model in [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation).
* See the [provider guides](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#identity-providers) for AWS, Google Cloud, GitHub Actions, and Kubernetes.
* For environment variables, profile files, and credential precedence, see the [WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference).


---
title: Use WIF with Okta
url: https://platform.claude.com/docs/en/manage-claude/wif-providers/okta
description: Federate Okta service application identities to the Claude API with Workload Identity Federation.
---

Okta can act as a workload identity provider by issuing OIDC access tokens to a **service application** through the OAuth 2.0 `client_credentials` grant. Your workload authenticates to Okta (typically with `private_key_jwt`, so no shared secret is stored), receives a signed JSON Web Token (JWT), and exchanges that JWT with Anthropic for a short-lived access token.

The Okta authorization server's issuer URL takes the form `https://<your-domain>.okta.com/oauth2/<auth-server-id>`. If you use the built-in default server, the path is `/oauth2/default`.

<Note>
  You must use an Okta **custom authorization server** (including the `default` one). Tokens issued directly by the Okta org authorization server (the `/oauth2/v1/token` endpoint with no authorization server ID in the path) cannot be validated by external parties because Okta does not publish signing keys for them.
</Note>

There are many ways to configure and authenticate to Okta that are outside the scope of this documentation. Ensure that your configuration and authentication mechanisms follow your company's guidance and security practices.


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-15

* Familiarity with [WIF concepts](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#concepts): service accounts, federation issuers, and federation rules.
* An Okta organization with API Access Management enabled (required for custom authorization servers).
* Permission to create service accounts, federation issuers, and federation rules in the Claude Console for your Anthropic organization.
* A workload that can request a token from Okta's `/v1/token` endpoint and reach `api.anthropic.com`.


## Configure Okta

Source: https://platform.claude.com/llms-full.txt#configure-okta

At a high level you need to:

1. Create an Okta service application.
2. Configure your default authorization server (or create a new custom authorization server) with an audience, a scope, an access policy, and any custom claims you want to match on.

The exact navigation depends on your Okta org configuration and admin console version. The following numbered steps walk through one common path:

1. **Create a service app integration.** In the Okta Admin Console, create a new app integration of type **API Services** (OIDC, machine-to-machine). Note the generated **Client ID**.
2. **Configure client authentication.** For a keyless setup, choose **Public key / Private key** (`private_key_jwt`) and register your workload's public JWK. Alternatively, use a client secret if your environment can store one securely. For the following example you may need to disable the DPoP requirement on the application; ensure that your production setup adheres to your organization's security requirements.
3. **Set the audience.** On your custom authorization server, set the audience to `https://api.anthropic.com` so issued access tokens carry that `aud` claim. Anthropic validates `aud` against this fixed value.
4. **Grant a scope.** On your custom authorization server, ensure at least one scope exists that the service app is allowed to request (for example, `anthropic.access`). Okta rejects `client_credentials` requests that do not include a granted scope.
5. **Create an access policy.** On your custom authorization server, create an access policy with at least one rule that allows your service app to request the scope you granted in step 4.
6. **(Optional) Add custom claims.** If you want to match on something other than the client ID, add a claim to the access token in your authorization server's **Claims** tab.

For a service app using `client_credentials`, Okta sets the `sub` claim of the issued access token to the application's **Client ID**, and `iss` to the authorization server's issuer URL.


## Configure Anthropic

Source: https://platform.claude.com/llms-full.txt#configure-anthropic-4

In the Claude Console, open **Settings → Workload identity**, click **Connect workload**, and select **Custom OIDC**. The wizard walks you through registering the issuer, creating a service account, and creating a federation rule.

The wizard creates these resources for you. Use the following values whether you enter them in the wizard or send them to the [Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api):

**Federation issuer:** Use your Okta custom authorization server URL and discovery mode. Anthropic reads Okta's `.well-known/openid-configuration` discovery document and fetches the JWKS from the `jwks_uri` it advertises.

**Federation rule:** Match on the Okta `sub` claim, which is the service app's Client ID. If you defined custom claims in Okta, you can match on those instead with the `claims` map or a CEL `condition`.


## Acquire a token and call the Claude API

Source: https://platform.claude.com/llms-full.txt#acquire-a-token-and-call-the-claude-api

Unlike platform-native providers (AWS, Google Cloud, Kubernetes), which make a token available inside the workload's runtime (through a projected file or local metadata endpoint), Okta does not. Your workload must call Okta's token endpoint to obtain a JWT, then pass that JWT to the Anthropic SDK as the identity token.

<CodeGroup>
  ```bash cURL
  # 1. Request an access token from Okta (client_credentials with private_key_jwt).
  OKTA_JWT=$(curl -sS "https://acme.okta.com/oauth2/aus1a2b3c4d5e6f7g8h9/v1/token" \
    -d grant_type=client_credentials \
    -d scope=anthropic.access \
    -d client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer \
    --data-urlencode client_assertion="$SIGNED_CLIENT_ASSERTION" \
    | jq -r .access_token)

  # 2. Exchange the Okta JWT for an Anthropic access token.
  ACCESS_TOKEN=$(curl -sS https://api.anthropic.com/v1/oauth/token \
    -H "content-type: application/json" \
    -d @- <<JSON | jq -r .access_token
  {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": "$OKTA_JWT",
    "federation_rule_id": "$ANTHROPIC_FEDERATION_RULE_ID",
    "organization_id": "$ANTHROPIC_ORGANIZATION_ID",
    "service_account_id": "$ANTHROPIC_SERVICE_ACCOUNT_ID",
    "workspace_id": "$ANTHROPIC_WORKSPACE_ID"
  }
  JSON
  )

  # 3. Call the Claude API.
  curl https://api.anthropic.com/v1/messages \
    -H "authorization: Bearer $ACCESS_TOKEN" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{"model": "claude-opus-5", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hello, Claude"}]}' \
    | jq -r '.content[] | select(.type == "text") | .text'

python Python
  import os
  import httpx2
  import anthropic
  from anthropic import WorkloadIdentityCredentials


  def fetch_okta_token() -> str:
      response = httpx2.post(
          f"{os.environ['OKTA_ISSUER']}/v1/token",
          data={
              "grant_type": "client_credentials",
              "scope": "anthropic.access",
              "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
              # Build the RFC 7523 client_assertion JWT signed with your Okta app's private key
              "client_assertion": build_signed_client_assertion(),
          },
      )
      response.raise_for_status()
      return response.json()["access_token"]


  client = anthropic.Anthropic(
      credentials=WorkloadIdentityCredentials(
          identity_token_provider=fetch_okta_token,
          federation_rule_id=os.environ["ANTHROPIC_FEDERATION_RULE_ID"],
          organization_id=os.environ["ANTHROPIC_ORGANIZATION_ID"],
          service_account_id=os.environ["ANTHROPIC_SERVICE_ACCOUNT_ID"],
          workspace_id=os.environ.get("ANTHROPIC_WORKSPACE_ID"),
      ),
  )

  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Hello, Claude"}],
  )
  print(next(block.text for block in message.content if block.type == "text"))

typescript TypeScript
  import Anthropic from "@anthropic-ai/sdk";
  import { oidcFederationProvider } from "@anthropic-ai/sdk/lib/credentials/oidc-federation";

  async function fetchOktaToken(): Promise<string> {
    const response = await fetch(`${process.env.OKTA_ISSUER}/v1/token`, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "client_credentials",
        scope: "anthropic.access",
        client_assertion_type: "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        // Build the RFC 7523 client_assertion JWT signed with your Okta app's private key
        client_assertion: buildSignedClientAssertion()
      })
    });
    const body = (await response.json()) as { access_token: string };
    return body.access_token;
  }

  const client = new Anthropic({
    credentials: oidcFederationProvider({
      identityTokenProvider: fetchOktaToken,
      federationRuleId: process.env.ANTHROPIC_FEDERATION_RULE_ID!,
      organizationId: process.env.ANTHROPIC_ORGANIZATION_ID!,
      serviceAccountId: process.env.ANTHROPIC_SERVICE_ACCOUNT_ID,
      workspaceId: process.env.ANTHROPIC_WORKSPACE_ID,
      baseURL: "https://api.anthropic.com",
      fetch
    })
  });

  const message = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }]
  });
  for (const block of message.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }

go Go
  package main

  import (
  	"context"
  	"encoding/json"
  	"fmt"
  	"net/http"
  	"net/url"
  	"os"
  	"strings"

  	"github.com/anthropics/anthropic-sdk-go"
  	"github.com/anthropics/anthropic-sdk-go/option"
  )

  func fetchOktaToken(ctx context.Context) (string, error) {
  	form := url.Values{
  		"grant_type":            {"client_credentials"},
  		"scope":                 {"anthropic.access"},
  		"client_assertion_type": {"urn:ietf:params:oauth:client-assertion-type:jwt-bearer"},
  		// Build the RFC 7523 client_assertion JWT signed with your Okta app's private key
  		"client_assertion": {buildSignedClientAssertion()},
  	}
  	req, err := http.NewRequestWithContext(ctx, http.MethodPost,
  		os.Getenv("OKTA_ISSUER")+"/v1/token", strings.NewReader(form.Encode()))
  	if err != nil {
  		return "", err
  	}
  	req.Header.Set("content-type", "application/x-www-form-urlencoded")
  	resp, err := http.DefaultClient.Do(req)
  	if err != nil {
  		return "", err
  	}
  	defer resp.Body.Close()
  	var body struct {
  		AccessToken string `json:"access_token"`
  	}
  	if err := json.NewDecoder(resp.Body).Decode(&body); err != nil {
  		return "", err
  	}
  	return body.AccessToken, nil
  }

  func main() {
  	client := anthropic.NewClient(
  		option.WithFederationTokenProvider(option.IdentityTokenFunc(fetchOktaToken), option.FederationOptions{
  			FederationRuleID: os.Getenv("ANTHROPIC_FEDERATION_RULE_ID"),
  			OrganizationID:   os.Getenv("ANTHROPIC_ORGANIZATION_ID"),
  			ServiceAccountID: os.Getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"),
  			WorkspaceID:      os.Getenv("ANTHROPIC_WORKSPACE_ID"),
  		}),
  	)
  	message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 1024,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, Claude")),
  		},
  	})
  	if err != nil {
  		panic(err)
  	}
  	for _, block := range message.Content {
  		if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
  			fmt.Println(textBlock.Text)
  			break
  		}
  	}
  }

java Java
  IdentityTokenProvider fetchOktaToken = () -> {
      try {
          var form = Map.of(
                          "grant_type", "client_credentials",
                          "scope", "anthropic.access",
                          "client_assertion_type", "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                          // Build the RFC 7523 client_assertion JWT signed with your Okta app's private key
                          "client_assertion", buildSignedClientAssertion())
                  .entrySet().stream()
                  .map(entry -> entry.getKey() + "=" + URLEncoder.encode(entry.getValue(), UTF_8))
                  .collect(Collectors.joining("&"));
          var request = HttpRequest.newBuilder(URI.create(System.getenv("OKTA_ISSUER") + "/v1/token"))
                  .header("content-type", "application/x-www-form-urlencoded")
                  .POST(HttpRequest.BodyPublishers.ofString(form))
                  .build();
          var response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
          return new ObjectMapper().readTree(response.body()).get("access_token").asText();
      } catch (Exception e) {
          throw new RuntimeException(e);
      }
  };

  AnthropicClient client = AnthropicOkHttpClient.builder()
          .federationTokenProvider(
                  fetchOktaToken,
                  System.getenv("ANTHROPIC_FEDERATION_RULE_ID"),
                  System.getenv("ANTHROPIC_ORGANIZATION_ID"),
                  System.getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"))
          .build();

  var message = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(1024)
          .addUserMessage("Hello, Claude")
          .build());

  IO.println(message.content());

csharp C#
  using Anthropic.Credentials;
  // ...

  var credentials = new WorkloadIdentityCredentials(new WorkloadIdentityOptions
  {
      FederationRuleId = Environment.GetEnvironmentVariable("ANTHROPIC_FEDERATION_RULE_ID")!,
      OrganizationId = Environment.GetEnvironmentVariable("ANTHROPIC_ORGANIZATION_ID"),
      ServiceAccountId = Environment.GetEnvironmentVariable("ANTHROPIC_SERVICE_ACCOUNT_ID"),
      WorkspaceId = Environment.GetEnvironmentVariable("ANTHROPIC_WORKSPACE_ID"),
      IdentityTokenProvider = new OktaTokenProvider(),
  });
  using var client = new AnthropicClient(new ClientOptions { Credentials = credentials });

  var message = await client.Messages.Create(new()
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages = [new() { Role = Role.User, Content = "Hello, Claude" }],
  });
  foreach (var block in message.Content)
  {
      if (block.Value is TextBlock textBlock)
      {
          Console.WriteLine(textBlock.Text);
      }
  }

  class OktaTokenProvider : IIdentityTokenProvider
  {
      private static readonly HttpClient Http = new();

      public async Task<string> GetIdentityTokenAsync(CancellationToken ct = default)
      {
          var form = new FormUrlEncodedContent(new Dictionary<string, string>
          {
              ["grant_type"] = "client_credentials",
              ["scope"] = "anthropic.access",
              ["client_assertion_type"] = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
              // Build the RFC 7523 client_assertion JWT signed with your Okta app's private key
              ["client_assertion"] = BuildSignedClientAssertion(),
          });
          var response = await Http.PostAsync(
              $"{Environment.GetEnvironmentVariable("OKTA_ISSUER")}/v1/token", form, ct);
          response.EnsureSuccessStatusCode();
          using var json = await JsonDocument.ParseAsync(
              await response.Content.ReadAsStreamAsync(ct), default, ct);
          return json.RootElement.GetProperty("access_token").GetString()!;
      }
  }

bash CLI
  # 1. Request an access token from Okta and write it to a temp file.
  ANTHROPIC_IDENTITY_TOKEN_FILE=$(mktemp)
  curl -sS "$OKTA_ISSUER/v1/token" \
    -d grant_type=client_credentials \
    -d scope=anthropic.access \
    -d client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer \
    --data-urlencode client_assertion="$SIGNED_CLIENT_ASSERTION" \
    | jq -r .access_token > "$ANTHROPIC_IDENTITY_TOKEN_FILE"
  export ANTHROPIC_IDENTITY_TOKEN_FILE

  # 2. Call the Claude API. The CLI reads ANTHROPIC_FEDERATION_RULE_ID,
  # ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, ANTHROPIC_WORKSPACE_ID, and
  # ANTHROPIC_IDENTITY_TOKEN_FILE and performs the exchange.
  ant messages create \
    --model claude-opus-5 \
    --max-tokens 1024 \
    --message '{role: user, content: "Hello, Claude"}'

php PHP
  use Anthropic\Client;
  use Anthropic\Credentials\WorkloadIdentityCredentials;

  function fetchOktaToken(): string
  {
      $ch = curl_init(getenv('OKTA_ISSUER') . '/v1/token');
      curl_setopt_array($ch, [
          CURLOPT_RETURNTRANSFER => true,
          CURLOPT_POSTFIELDS => http_build_query([
              'grant_type' => 'client_credentials',
              'scope' => 'anthropic.access',
              'client_assertion_type' => 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
              // Build the RFC 7523 client_assertion JWT signed with your Okta app's private key
              'client_assertion' => buildSignedClientAssertion(),
          ]),
      ]);
      $body = json_decode(curl_exec($ch), true);
      curl_close($ch);
      return $body['access_token'];
  }

  $client = new Client(
      credentials: new WorkloadIdentityCredentials(
          identityTokenProvider: fetchOktaToken(...),
          federationRuleId: getenv('ANTHROPIC_FEDERATION_RULE_ID'),
          organizationId: getenv('ANTHROPIC_ORGANIZATION_ID'),
          serviceAccountId: getenv('ANTHROPIC_SERVICE_ACCOUNT_ID'),
          workspaceId: getenv('ANTHROPIC_WORKSPACE_ID') ?: null,
      ),
  );

  $message = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 1024,
      messages: [['role' => 'user', 'content' => 'Hello, Claude']],
  );
  echo array_find($message->content, static fn ($block): bool => $block->type === 'text')->text, PHP_EOL;

ruby Ruby
  require "anthropic"
  require "json"
  require "net/http"

  def fetch_okta_token
    uri = URI("#{ENV.fetch('OKTA_ISSUER')}/v1/token")
    response = Net::HTTP.post_form(
      uri,
      "grant_type" => "client_credentials",
      "scope" => "anthropic.access",
      "client_assertion_type" => "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
      # Build the RFC 7523 client_assertion JWT signed with your Okta app's private key
      "client_assertion" => build_signed_client_assertion
    )
    JSON.parse(response.body).fetch("access_token")
  end

  client = Anthropic::Client.new(
    credentials: Anthropic::WorkloadIdentityCredentials.new(
      identity_token_provider: -> { fetch_okta_token },
      federation_rule_id: ENV.fetch("ANTHROPIC_FEDERATION_RULE_ID"),
      organization_id: ENV.fetch("ANTHROPIC_ORGANIZATION_ID"),
      service_account_id: ENV.fetch("ANTHROPIC_SERVICE_ACCOUNT_ID"),
      workspace_id: ENV["ANTHROPIC_WORKSPACE_ID"]
    )
  )

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}]
  )
  puts message.content.find { it.type == :text }.text
  ```
</CodeGroup>

Each SDK tab shows the callable pattern: the Anthropic SDK calls your identity-token provider again whenever the Anthropic access token approaches expiry, so your Okta fetcher should return a fresh token on each call rather than caching one indefinitely. The `ant` CLI re-reads `ANTHROPIC_IDENTITY_TOKEN_FILE` on each exchange, so refresh that file on a timer for long-running shells.


## Verify the setup

Source: https://platform.claude.com/llms-full.txt#verify-the-setup-4

A successful exchange returns an `access_token` beginning with `sk-ant-oat01-` and an `expires_in` value in seconds. If the exchange fails with the opaque `401` `authentication_error` response (message `Authentication failed`), check the [authentication history page](https://platform.claude.com/settings/workload-identity-federation?tab=history) for the deny reason and see [Troubleshoot a failed exchange](https://platform.claude.com/docs/en/manage-claude/wif-reference#troubleshoot-a-failed-exchange); the most common Okta-side cause is an `issuer_url` mismatch (it must include the `/oauth2/<auth-server-id>` path; the Okta org authorization server is not usable).


## Scope your rule

Source: https://platform.claude.com/llms-full.txt#scope-your-rule-5

<Warning>
  Multiple service apps under the same Okta authorization server share the same issuer. A rule that omits `subject_prefix` matches every service app on that server, so any team that can register one could obtain a federated Anthropic token.
</Warning>

Lock the rule's `match` block to the narrowest scope that fits your use case:

* **Pin the exact Client ID:** Set `subject_prefix` to the service app's full Client ID with no trailing `*`.
* **Pin the audience:** Match the `audience` value you configured on the authorization server so tokens minted for a different audience are rejected.
* **Match on custom claims:** For finer-grained scoping, add claims in the authorization server's **Claims** tab and match them with the rule's `claims` map or a CEL `condition`.
* **Use one rule per service app:** Create a separate federation rule for each service app rather than sharing one rule across apps.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-86

* Review the [WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference) for the full credential resolution order and profile configuration.
* See the [WIF reference](https://platform.claude.com/docs/en/manage-claude/wif-reference#rule-matching-semantics) to match on custom Okta claims with CEL expressions.


---
title: Use WIF with SPIFFE
url: https://platform.claude.com/docs/en/manage-claude/wif-providers/spiffe
description: Authenticate SPIFFE workloads to the Claude API using JWT-SVIDs from SPIRE or any other SPIFFE-conformant issuer.
---

[SPIFFE](https://spiffe.io/) is the CNCF standard for issuing identity to workloads. [SPIRE](https://spiffe.io/docs/latest/spire-about/) is its open-source reference implementation, and several commercial products also issue SPIFFE-conformant identities. Anthropic federates with any SPIFFE implementation that emits OIDC-compatible JWT-SVIDs. For a current list of implementations, see [Commercial software that implements SPIFFE](https://spiffe.io/docs/latest/spiffe-about/overview/#commercial-software-that-implements-spiffe) on the SPIFFE project site.

Federation works either through an OIDC discovery document at a public HTTPS URL (`discovery` mode, subject to the [URL constraints](https://platform.claude.com/docs/en/manage-claude/wif-reference#url-fields)) or by registering the JWKS directly (`inline` mode).

The JWT-SVID spec defines `sub` as the workload's SPIFFE ID, and the SPIFFE Workload API requires the caller to supply `aud` at fetch time, so those claims are the same across implementations. Anthropic additionally requires `iss` and `iat`, neither of which the JWT-SVID spec mandates, so configure your implementation to populate both (in SPIRE, `iss` is the `jwt_issuer` server setting and `iat` is set automatically). With those in place, the [Configure Anthropic](https://platform.claude.com/docs/en/manage-claude/wif-providers/spiffe#configure-anthropic), [Acquire and use the token](https://platform.claude.com/docs/en/manage-claude/wif-providers/spiffe#acquire-and-use-the-token), and [Scope your rule](https://platform.claude.com/docs/en/manage-claude/wif-providers/spiffe#scope-your-rule) sections of this guide apply to any SPIFFE implementation.

SPIFFE assigns every workload a stable identity URI of the form `spiffe://<trust-domain>/<path>`, and SPIRE issues that identity as a JWT-SVID on demand through the Workload API. A JWT-SVID is an ordinary signed JWT whose `sub` claim is the workload's SPIFFE ID and whose `aud` claim is supplied by the workload at fetch time.

The bridge from a SPIRE trust domain to standard OIDC is the [SPIRE OIDC Discovery Provider](https://github.com/spiffe/spire/blob/main/support/oidc-discovery-provider/README.md), a standalone helper that publishes `/.well-known/openid-configuration` and a JWKS endpoint for the trust domain's JWT signing keys. With the discovery provider running, a JWT-SVID validates like any other OIDC token: register the discovery URL as a federation issuer, write a federation rule that matches the workload's SPIFFE ID, and have the workload present its JWT-SVID to Anthropic's token-exchange endpoint.

This page's examples use SPIRE and apply anywhere SPIRE Agent runs: Kubernetes pods, virtual machines, and bare-metal hosts.

<Note>
  If your Kubernetes cluster does not run SPIRE and you want to authenticate with the cluster's native projected service-account tokens instead, see [Use WIF with Kubernetes](https://platform.claude.com/docs/en/manage-claude/wif-providers/kubernetes).
</Note>


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-16

* Familiarity with [WIF concepts](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation#concepts): service accounts, federation issuers, and federation rules.
* A SPIFFE deployment with workload identities issued (the examples on this page use SPIRE Server and Agent), and registration entries for the workloads that need to call the Claude API.
* An OIDC discovery endpoint for the trust domain (in SPIRE, the [OIDC Discovery Provider](https://github.com/spiffe/spire/blob/main/support/oidc-discovery-provider/README.md)) running with a publicly reachable HTTPS endpoint, or the JWKS exported for `inline` registration.
* Your SPIFFE issuer configured to set the `iss` claim on JWT-SVIDs to the value you will register as the federation issuer's `issuer_url`. For `discovery` mode, this is the discovery endpoint's public URL (in SPIRE, the `jwt_issuer` server setting).
* JWT-SVIDs available to your workloads. WIF accepts JWT-SVIDs only, not X.509-SVIDs.
* Permission to create service accounts, federation issuers, and federation rules in the Claude Console for your Anthropic organization.

The audience value to request when fetching a JWT-SVID is always `https://api.anthropic.com`. Use this value in spiffe-helper's `jwt_audience`, the Workload API `FetchJWTSVID` call, and the federation rule's `audience` matcher.


## Configure SPIRE

Source: https://platform.claude.com/llms-full.txt#configure-spire

The instructions in this section are SPIRE-specific. If you use a different SPIFFE issuer, configure its OIDC discovery endpoint and JWT-SVID retrieval according to its own documentation, then continue at [Configure Anthropic](https://platform.claude.com/docs/en/manage-claude/wif-providers/spiffe#configure-anthropic).

If you already run SPIRE with the OIDC Discovery Provider, federating with Anthropic requires three things on the SPIRE side: a `jwt_issuer` that matches the discovery URL, a registration entry for the workload that will call the Claude API, and a way for that workload to fetch a JWT-SVID with the Anthropic audience. The following subsections walk through each. The configuration snippets show only the settings relevant to Anthropic federation, not complete SPIRE deployment configs.

<Tip>
  Setting up SPIRE for the first time? Deploy SPIRE Server and Agent following the [SPIRE quickstart](https://spiffe.io/docs/latest/try/), then add the [OIDC Discovery Provider](https://github.com/spiffe/spire/blob/main/support/oidc-discovery-provider/README.md) as a separate service alongside SPIRE Server. Discovery-mode federation depends on the provider being deployed and publicly reachable. The provider is not part of a default SPIRE install.
</Tip>

### Verify the JWT issuer

Anthropic validates a JWT-SVID by matching its `iss` claim against a registered federation issuer and fetching the JWKS from that issuer's discovery document. Two SPIRE settings must agree on the same URL: SPIRE Server's `jwt_issuer` (which becomes the `iss` claim in every minted JWT-SVID) and the OIDC Discovery Provider's `domains` list (which determines the host the discovery document and JWKS are served from). That shared URL is what you register with Anthropic.

The trust domain and the issuer URL are independent. The trust domain (`spiffe://prod.example.com`) scopes the `sub` claim. The issuer URL (`https://oidc-discovery.prod.example.com`) is where Anthropic fetches signing keys. They do not need to share a hostname.

Confirm `jwt_issuer` is set in SPIRE Server's configuration and points at the discovery provider's public URL. The following example also shows a default JWT-SVID lifetime. SPIRE's built-in default is 5 minutes, which is short enough that continuous rotation is required (see [Run spiffe-helper](https://platform.claude.com/docs/en/manage-claude/wif-providers/spiffe#run-spiffe-helper)). Anthropic's token-exchange endpoint rejects any identity token whose lifetime exceeds the federation issuer's configured maximum, which is 1 hour by default (see [Validation rules](https://platform.claude.com/docs/en/manage-claude/wif-reference#validation-rules)). This check applies to every SPIFFE implementation, not only SPIRE, so keep `default_jwt_svid_ttl` (or any per-entry override) at or below that maximum.

```text server.conf
server {
    trust_domain         = "prod.example.com"
    jwt_issuer           = "https://oidc-discovery.prod.example.com"
    default_jwt_svid_ttl = "5m"
    # ...
}

text oidc-discovery-provider.conf
domains = ["oidc-discovery.prod.example.com"]

server_api {
    address = "unix:///run/spire/sockets/private/api.sock"
}

acme {
    email        = "platform@example.com"
    tos_accepted = true
}

bash CLI
# Replace NODE_UID with the node's UID:
#   kubectl get node <node-name> -o jsonpath='{.metadata.uid}'
spire-server entry create \
    -spiffeID spiffe://prod.example.com/ns/inference/sa/worker \
    -parentID spiffe://prod.example.com/spire/agent/k8s_psat/prod-cluster/NODE_UID \
    -selector k8s:ns:inference \
    -selector k8s:sa:worker

text helper.conf
agent_address = "/run/spire/sockets/agent.sock"
# The JWT-SVID file is written under cert_dir
cert_dir      = "/var/run/secrets/anthropic.com"
daemon_mode   = true

jwt_svids = [{
    jwt_audience       = "https://api.anthropic.com"
    jwt_svid_file_name = "token"
}]
```

In Kubernetes, run spiffe-helper as a sidecar container that shares a memory-backed `emptyDir` volume (`medium: Memory`) with your application container so the bearer SVID never lands on the node's disk. Mount the SPIRE Agent socket from the host into the sidecar, mount the shared volume at `/var/run/secrets/anthropic.com` in both containers, and set `ANTHROPIC_IDENTITY_TOKEN_FILE=/var/run/secrets/anthropic.com/token` on the application container. On VMs and bare metal, run spiffe-helper as a system service alongside the workload and point both at a shared directory.


## Configure Anthropic

Source: https://platform.claude.com/llms-full.txt#configure-anthropic-5

In the Claude Console, open **Settings → Workload identity**, click **Connect workload**, and select **Custom OIDC**. The wizard walks you through registering the issuer, creating a service account, and creating a federation rule.

The wizard creates these resources for you. Use the following values whether you enter them in the wizard or send them to the [Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api):

**Federation issuer:** Register the OIDC Discovery Provider's public URL in `discovery` mode. Anthropic fetches `/.well-known/openid-configuration` from this URL and follows the returned `jwks_uri` to retrieve the trust domain's signing keys.

If the discovery provider is not reachable from the public internet, fetch the JWKS yourself (`curl https://oidc-discovery.prod.example.com/keys`) and register the issuer with `"jwks": {"type": "inline", "keys": [...]}` using the contents of the returned `keys` array. In `inline` mode the `issuer_url` is only compared against the JWT-SVID's `iss` claim. Anthropic never attempts to reach it.

<Warning>
  SPIRE rotates JWT signing keys frequently, by default on the same cadence as the CA (`ca_ttl`, 24 hours). If you register the issuer with an inline JWKS instead of a discovery URL, you must update the JWKS every time SPIRE rotates: add the new key before workloads start presenting it, and **remove superseded keys** once tokens signed with them have expired. Stale keys left in an inline JWKS remain trusted indefinitely.
</Warning>

To automate JWKS updates without exposing a public discovery endpoint, configure a SPIRE Server [BundlePublisher](https://spiffe.io/docs/latest/deploying/spire_server/#built-in-plugins) plugin (`aws_s3`, `gcp_cloudstorage`, or `k8s_configmap`) with `format = "jwks"` to push the JWT signing keys to external storage on every rotation, then update the issuer's inline keys through the [Admin API](https://platform.claude.com/docs/en/manage-claude/wif-admin-api#federation-issuers).

**Federation rule:** Match the JWT-SVID's `sub` (the SPIFFE ID) and the `aud` you configured spiffe-helper to request. SPIFFE IDs are URI strings and `subject_prefix` matches them as opaque text, so an exact value or a trailing-`*` prefix match both work against them. For more complex patterns, use a CEL `condition`.

`token_lifetime_seconds` is the lifetime of the Anthropic access token the exchange returns, not of the JWT-SVID. The SDK refreshes the access token automatically.

Be as specific as the workload allows. Loosen `subject_prefix` to `spiffe://prod.example.com/ns/inference/*` only if every workload registered under that path should map to the same Anthropic service account. Add the rule's `fdrl_...` ID to the workload's `ANTHROPIC_FEDERATION_RULE_ID` environment variable.


## Acquire and use the token

Source: https://platform.claude.com/llms-full.txt#acquire-and-use-the-token-3

The Anthropic SDKs can either read the JWT-SVID from the file that spiffe-helper maintains or call the SPIFFE Workload API directly through a token-provider callable. The file path is the simplest integration and works in every SDK language. The callable path removes the sidecar but requires a SPIFFE Workload API client in your application's language.

<Tabs>
  <Tab title="File-based with spiffe-helper">
    With spiffe-helper writing a fresh JWT-SVID to `/var/run/secrets/anthropic.com/token`, set `ANTHROPIC_IDENTITY_TOKEN_FILE` to that path along with `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`, `ANTHROPIC_SERVICE_ACCOUNT_ID`, and `ANTHROPIC_WORKSPACE_ID`. The SDK reads the file on every token exchange, so it always picks up the most recently rotated SVID, and refreshes the Anthropic access token automatically before it expires. See [Environment variables](https://platform.claude.com/docs/en/manage-claude/wif-reference#environment-variables) for where each value comes from.

    <CodeGroup>
      ```bash cURL
      JWT=$(cat "$ANTHROPIC_IDENTITY_TOKEN_FILE")

      ACCESS_TOKEN=$(curl -sS https://api.anthropic.com/v1/oauth/token \
        -H "content-type: application/json" \
        --data @- <<JSON | jq -r .access_token
      {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": "$JWT",
        "federation_rule_id": "$ANTHROPIC_FEDERATION_RULE_ID",
        "organization_id": "$ANTHROPIC_ORGANIZATION_ID",
        "service_account_id": "$ANTHROPIC_SERVICE_ACCOUNT_ID",
        "workspace_id": "$ANTHROPIC_WORKSPACE_ID"
      }
      JSON
      )

      curl https://api.anthropic.com/v1/messages \
        -H "authorization: Bearer $ACCESS_TOKEN" \
        -H "anthropic-version: 2023-06-01" \
        -H "content-type: application/json" \
        -d '{
          "model": "claude-opus-5",
          "max_tokens": 1024,
          "messages": [{"role": "user", "content": "Hello, Claude"}]
        }' | jq -r '.content[] | select(.type == "text") | .text'

bash CLI
      # Reads the JWT-SVID that spiffe-helper writes to
      # ANTHROPIC_IDENTITY_TOKEN_FILE, plus ANTHROPIC_FEDERATION_RULE_ID,
      # ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID.
      ant messages create \
        --model claude-opus-5 \
        --max-tokens 1024 \
        --message '{role: user, content: "Hello, Claude"}'

python Python
      import anthropic

      # Reads the JWT-SVID that spiffe-helper writes to
      # ANTHROPIC_IDENTITY_TOKEN_FILE, plus ANTHROPIC_FEDERATION_RULE_ID,
      # ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID.
      client = anthropic.Anthropic()

      message = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          messages=[{"role": "user", "content": "Hello, Claude"}],
      )
      print(next(block.text for block in message.content if block.type == "text"))

typescript TypeScript
      import Anthropic from "@anthropic-ai/sdk";

      // Reads the JWT-SVID that spiffe-helper writes to
      // ANTHROPIC_IDENTITY_TOKEN_FILE, plus ANTHROPIC_FEDERATION_RULE_ID,
      // ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID.
      const client = new Anthropic();

      const message = await client.messages.create({
        model: "claude-opus-5",
        max_tokens: 1024,
        messages: [{ role: "user", content: "Hello, Claude" }]
      });
      for (const block of message.content) {
        if (block.type === "text") {
          console.log(block.text);
        }
      }

csharp C#
      // Reads the JWT-SVID that spiffe-helper writes to
      // ANTHROPIC_IDENTITY_TOKEN_FILE, plus ANTHROPIC_FEDERATION_RULE_ID,
      // ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID.
      using var client = new AnthropicClient();

      var message = await client.Messages.Create(new()
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 1024,
          Messages = [new() { Role = Role.User, Content = "Hello, Claude" }],
      });
      foreach (var block in message.Content)
      {
          if (block.Value is TextBlock textBlock)
          {
              Console.WriteLine(textBlock.Text);
          }
      }

go Go
      // Reads the JWT-SVID that spiffe-helper writes to
      // ANTHROPIC_IDENTITY_TOKEN_FILE, plus ANTHROPIC_FEDERATION_RULE_ID,
      // ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID.
      client := anthropic.NewClient()

      message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
      	Model:     anthropic.ModelClaudeOpus5,
      	MaxTokens: 1024,
      	Messages: []anthropic.MessageParam{
      		anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, Claude")),
      	},
      })
      if err != nil {
      	panic(err)
      }
      for _, block := range message.Content {
      	if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
      		fmt.Println(textBlock.Text)
      		break
      	}
      }

java Java
      // Reads the JWT-SVID that spiffe-helper writes to
      // ANTHROPIC_IDENTITY_TOKEN_FILE, plus ANTHROPIC_FEDERATION_RULE_ID,
      // ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID.
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      var message = client.messages().create(MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024)
              .addUserMessage("Hello, Claude")
              .build());

      IO.println(message.content());

php PHP
      use Anthropic\Client;

      // Reads the JWT-SVID that spiffe-helper writes to
      // ANTHROPIC_IDENTITY_TOKEN_FILE, plus ANTHROPIC_FEDERATION_RULE_ID,
      // ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID.
      $client = new Client();

      $message = $client->messages->create(
          model: 'claude-opus-5',
          maxTokens: 1024,
          messages: [['role' => 'user', 'content' => 'Hello, Claude']],
      );
      $textBlock = array_find($message->content, static fn ($block): bool => $block->type === 'text');
      echo $textBlock->text, PHP_EOL;

ruby Ruby
      require "anthropic"

      # Reads the JWT-SVID that spiffe-helper writes to
      # ANTHROPIC_IDENTITY_TOKEN_FILE, plus ANTHROPIC_FEDERATION_RULE_ID,
      # ANTHROPIC_ORGANIZATION_ID, ANTHROPIC_SERVICE_ACCOUNT_ID, and ANTHROPIC_WORKSPACE_ID.
      client = Anthropic::Client.new

      message = client.messages.create(
        model: "claude-opus-5",
        max_tokens: 1024,
        messages: [{role: "user", content: "Hello, Claude"}]
      )
      puts message.content.find { it.type == :text }.text

python Python
      import os
      import anthropic
      from anthropic import WorkloadIdentityCredentials
      from spiffe import JwtSource

      AUDIENCE = "https://api.anthropic.com"

      # Connects to the SPIRE Agent socket at SPIFFE_ENDPOINT_SOCKET.
      jwt_source = JwtSource()


      def fetch_jwt_svid() -> str:
          svid = jwt_source.fetch_svid(audience={AUDIENCE})  # audience is a set of strings
          return svid.token


      client = anthropic.Anthropic(
          credentials=WorkloadIdentityCredentials(
              identity_token_provider=fetch_jwt_svid,
              federation_rule_id=os.environ["ANTHROPIC_FEDERATION_RULE_ID"],
              organization_id=os.environ["ANTHROPIC_ORGANIZATION_ID"],
              service_account_id=os.environ["ANTHROPIC_SERVICE_ACCOUNT_ID"],
              workspace_id=os.environ.get("ANTHROPIC_WORKSPACE_ID"),
          ),
      )

      message = client.messages.create(
          model="claude-opus-5",
          max_tokens=1024,
          messages=[{"role": "user", "content": "Hello, Claude"}],
      )
      print(next(block.text for block in message.content if block.type == "text"))

go Go
      import (
      	"context"
      	"fmt"
      	"os"

      	"github.com/anthropics/anthropic-sdk-go"
      	"github.com/anthropics/anthropic-sdk-go/option"
      	"github.com/spiffe/go-spiffe/v2/svid/jwtsvid"
      	"github.com/spiffe/go-spiffe/v2/workloadapi"
      )
      // ...
      	const audience = "https://api.anthropic.com"

      	ctx := context.Background()
      	source, err := workloadapi.NewJWTSource(ctx)
      	if err != nil {
      		panic(err)
      	}
      	defer source.Close()

      	fetchJWTSVID := func(ctx context.Context) (string, error) {
      		svid, err := source.FetchJWTSVID(ctx, jwtsvid.Params{Audience: audience})
      		if err != nil {
      			return "", err
      		}
      		return svid.Marshal(), nil
      	}

      	client := anthropic.NewClient(
      		option.WithFederationTokenProvider(fetchJWTSVID, option.FederationOptions{
      			FederationRuleID: os.Getenv("ANTHROPIC_FEDERATION_RULE_ID"),
      			OrganizationID:   os.Getenv("ANTHROPIC_ORGANIZATION_ID"),
      			ServiceAccountID: os.Getenv("ANTHROPIC_SERVICE_ACCOUNT_ID"),
      			WorkspaceID:      os.Getenv("ANTHROPIC_WORKSPACE_ID"),
      		}),
      	)

      	message, err := client.Messages.New(ctx, anthropic.MessageNewParams{
      		Model:     anthropic.ModelClaudeOpus5,
      		MaxTokens: 1024,
      		Messages: []anthropic.MessageParam{
      			anthropic.NewUserMessage(anthropic.NewTextBlock("Hello, Claude")),
      		},
      	})
      	if err != nil {
      		panic(err)
      	}
      	for _, block := range message.Content {
      		if textBlock, ok := block.AsAny().(anthropic.TextBlock); ok {
      			fmt.Println(textBlock.Text)
      			break
      		}
      	}
      ```
    </CodeGroup>

    <Note>
      For other languages, fetch the JWT-SVID with your runtime's SPIFFE Workload API client (or shell out to `spire-agent api fetch jwt`), write it to a file, and set `ANTHROPIC_IDENTITY_TOKEN_FILE` to that path as in the file-based tab.
    </Note>
  </Tab>
</Tabs>


## Verify the setup

Source: https://platform.claude.com/llms-full.txt#verify-the-setup-5

Before wiring the SDK in, fetch a JWT-SVID directly from SPIRE Agent and confirm the claims match what your federation rule expects. If you use a different SPIFFE implementation, fetch a JWT-SVID with its CLI or Workload API client and decode the payload the same way.

<Note>
  The Workload API attests the calling process. For a Kubernetes registration entry, run this command inside a pod that satisfies the entry's selectors and has the agent socket mounted (for example, by using `kubectl exec`). On VMs and bare metal, run it as the user or process that matches the entry's `unix:` selectors. Running from an unattested host shell returns `no identity issued`, which is the most common verify-step failure.
</Note>

```bash CLI
spire-agent api fetch jwt \
    -audience https://api.anthropic.com \
    -socketPath /run/spire/sockets/agent.sock \
    -output json \
  | jq -r '.[0].svids[0].svid' \
  | jq -rR 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson'
```

The `-output json` flag returns the SVID response and bundle response as a two-element JSON array, so `jq -r '.[0].svids[0].svid'` extracts the bare token. On older SPIRE versions without `-output`, the command prints a labeled block instead. In that case, pipe the default output through `awk '/^[[:space:]]*eyJ/{print $1; exit}'` to extract the token line. Check that `iss` is the OIDC Discovery Provider URL you registered, `sub` is the workload's SPIFFE ID, and `aud` contains `https://api.anthropic.com`. Then run the cURL example from [Acquire and use the token](https://platform.claude.com/docs/en/manage-claude/wif-providers/spiffe#acquire-and-use-the-token). A successful exchange returns an `access_token` beginning with `sk-ant-oat01-`. If the exchange fails with the opaque `401` `authentication_error` response (message `Authentication failed`), check the [authentication history page](https://platform.claude.com/settings/workload-identity-federation?tab=history) for the deny reason and see [Troubleshoot a failed exchange](https://platform.claude.com/docs/en/manage-claude/wif-reference#troubleshoot-a-failed-exchange). The most common SPIRE-side cause is a mismatch between SPIRE Server's `jwt_issuer` and the URL registered as the federation issuer.


## Scope your rule

Source: https://platform.claude.com/llms-full.txt#scope-your-rule-6

SPIFFE ID path conventions are operator-defined, so the federation rule's `subject_prefix` matcher should reflect the path scheme your registration entries use. Common schemes include `spiffe://<trust-domain>/ns/<namespace>/sa/<service-account>` (the default emitted by the `ClusterSPIFFEID` resource in spire-controller-manager) and `spiffe://<trust-domain>/host/<hostname>/<service>` for VM and bare-metal workloads.

<Warning>
  A `subject_prefix` of `spiffe://prod.example.com/*` matches every workload in the trust domain. Without an `audience` matcher, the rule also accepts JWT-SVIDs minted for any audience, including ones the workload requested for unrelated relying parties.
</Warning>

Lock the rule's `match` block to the narrowest scope that fits your use case:

* **Pin to one workload:** Set `subject_prefix` to the full SPIFFE ID with no trailing `*`.
* **Always set an audience:** Require `audience` on the rule and configure spiffe-helper (or the Workload API call) with the same value so SVIDs minted for other relying parties are rejected.
* **Scope by path segment:** Use `spiffe://prod.example.com/ns/inference/*` to grant every workload registered under a namespace, and create a separate rule and Anthropic service account per namespace rather than widening one rule.
* **One issuer per trust domain:** Each SPIRE trust domain has its own signing keys and OIDC Discovery Provider. Register each as a separate federation issuer and bind rules to the issuer that owns the SPIFFE IDs they match.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-87

<CardGroup cols={2}>
  <Card title="Use WIF with Okta" icon="lock" href="https://platform.claude.com/docs/en/manage-claude/wif-providers/okta">
    Federate Okta service application identities to the Claude API with Workload Identity Federation.
  </Card>

  <Card title="Workload Identity Federation" icon="cloud" href="https://platform.claude.com/docs/en/manage-claude/workload-identity-federation">
    Authenticate workloads to the Claude API with short-lived identity tokens from your own identity provider instead of long-lived static API keys.
  </Card>

  <Card title="WIF reference" icon="book" href="https://platform.claude.com/docs/en/manage-claude/wif-reference">
    Environment variables, validation rules, profile configuration, and error reference for Workload Identity Federation.
  </Card>

  <Card title="Use WIF with Kubernetes" icon="cube" href="https://platform.claude.com/docs/en/manage-claude/wif-providers/kubernetes">
    Authenticate to the Claude API from self-managed Kubernetes clusters using projected service account tokens.
  </Card>
</CardGroup>


### Monitoring

---
title: Analytics APIs
url: https://platform.claude.com/docs/en/manage-claude/analytics-api
description: Understand which analytics API and API key your organization needs, then provision access to Claude Code productivity metrics or Claude Enterprise engagement and adoption data.
---

Anthropic provides two analytics APIs, and which one you use depends on which Claude product your organization manages:

* The **Claude Code Analytics API** reports daily Claude Code productivity metrics for organizations that use the Claude Platform. It is part of the [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api) and uses an Admin API key.
* The **Claude Enterprise Analytics API** reports organization-wide engagement, adoption, and cost data across Claude products (chat, projects, Claude Code, and more) for Claude Enterprise organizations. It uses an Analytics API key created in claude.ai.

The two APIs use different key types, created in different places by different roles. This page describes which API fits your organization and how to create the right key.


## Which API do you need?

Source: https://platform.claude.com/llms-full.txt#which-api-do-you-need

| API                                 | Key type                             | Created in                                                                                | Who can create it  | What it covers                                                                                                                                     |
| ----------------------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Claude Code Analytics API**       | Admin API key (`sk-ant-admin01-...`) | [Claude Console > Settings > Admin keys](https://platform.claude.com/settings/admin-keys) | Organization admin | Daily Claude Code metrics per user: sessions, lines of code, commits, pull requests, tool acceptance, and estimated cost by model                  |
| **Claude Enterprise Analytics API** | Analytics API key                    | [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access)    | Primary owner      | Organization-wide engagement and adoption (user activity, active-user summaries, project, skill, and connector usage), plus cost and usage reports |

The key types are not interchangeable: an Admin API key cannot call the Claude Enterprise Analytics API, and an Analytics API key cannot call the Admin API. Both APIs appear under the [Admin API reference](https://platform.claude.com/docs/en/api/admin), but they are separate APIs with separate key types. If your organization uses both the Claude Platform and Claude Enterprise, you can provision both keys and use each API for its own data.

<Note>
  Looking for API usage and cost data rather than product analytics? See the [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api), which explains the right path for both Claude Console and Claude Enterprise organizations.
</Note>

<Note>
  If you want to view engagement and adoption data in the product rather than programmatically, use the [Analytics dashboard](https://claude.ai/analytics/activity) in claude.ai. For governance and auditing use cases (individual user actions, raw activity events, conversation content), see the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).
</Note>


## Get access to the Claude Code Analytics API

Source: https://platform.claude.com/llms-full.txt#get-access-to-the-claude-code-analytics-api

The Claude Code Analytics API is available to every organization with access to the [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api), and is free to use.

<Steps>
  <Step title="Create an Admin API key">
    Follow the steps in [Create an Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys#create-a-key-for-a-claude-console-organization).
  </Step>

  <Step title="Call the API">
    Pass the key in the `x-api-key` header:

</Step>
</Steps>

For the available metrics, request parameters, and response schema, see the [Claude Code Analytics API guide](https://platform.claude.com/docs/en/manage-claude/claude-code-analytics-api) and the [API reference](https://platform.claude.com/docs/en/api/admin/usage_report/retrieve_claude_code).


## Get access to the Claude Enterprise Analytics API

Source: https://platform.claude.com/llms-full.txt#get-access-to-the-claude-enterprise-analytics-api

The Claude Enterprise Analytics API is available to Claude Enterprise organizations. Engagement and adoption data is available on all Enterprise plans. The cost and usage endpoints apply to usage-based Enterprise plans; for seat-based Enterprise plans, they reflect usage credits only.

<Steps>
  <Step title="Sign in as the primary owner">
    Only the primary owner of the organization can enable API access and create Analytics API keys.
  </Step>

  <Step title="Enable API access and create a key">
    Go to [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access) and enable public API access, then create an Analytics API key. Keys carry the `read:analytics` scope. Copy the displayed secret and store it in your secrets manager.
  </Step>

  <Step title="Call the API">
    Pass the key in the `x-api-key` header and include the [`anthropic-version`](https://platform.claude.com/docs/en/api/versioning) header on every request. Endpoints live under `https://api.anthropic.com/v1/organizations/analytics/`. For request examples, parameters, and response schemas, see the [Claude Enterprise Analytics API reference](https://platform.claude.com/docs/en/api/admin/analytics).
  </Step>
</Steps>

The Claude Enterprise Analytics API provides:

* **User activity:** per-user daily metrics across chat (conversations, messages, projects, files, artifacts), Claude Code (sessions, commits, pull requests, lines of code, tool actions), and other Claude products
* **Activity summaries:** organization-level daily, weekly, and monthly active users, seat counts, and pending invites
* **Project, skill, and connector usage:** adoption breakdowns for chat projects, skills, and connectors
* **Cost and usage reports:** per-user and organization-level token usage and cost over time (usage-based Enterprise plans)

For endpoint details, parameters, and response schemas, see the [Claude Enterprise Analytics API reference](https://platform.claude.com/docs/en/api/admin/analytics). The following sections cover data freshness, metric definitions, and operational guidance that apply across those endpoints.


## Data availability and freshness

Source: https://platform.claude.com/llms-full.txt#data-availability-and-freshness

Claude Enterprise Analytics API data is available for dates on or after January 1, 2026.

**Engagement and adoption endpoints** (user activity, summaries, projects, skills, connectors) return a per-day snapshot for the date you specify. Data for a given day is typically available from about 17:00 UTC the following day (a 1-day lag); until then, the most recent available day is usually two days before the current UTC date. Data occasionally arrives later, and exact freshness varies by query, so rather than assuming a fixed time, check the error response: requesting a date that is not yet available returns a 400 error naming the most recent available day. If data is not available well past the typical lag, it usually indicates a data pipeline failure on Anthropic's side; contact support if the gap persists.

**Cost and usage endpoints** follow a different freshness model. Data is typically available within four hours of the underlying usage but may take up to 24 hours. Values for a given date can be revised for up to 30 days as late events arrive and reconciliation runs. For invoicing-grade totals, query dates at least 30 days in the past.

<Note>
  Cost and usage responses include a `data_refreshed_at` timestamp. When `ending_at` is omitted (the default is the current time), the response includes a tail of data after `data_refreshed_at` that is incomplete. For stable results across repeated calls, set `ending_at` to a value at or before a previously returned `data_refreshed_at`.
</Note>


## How metrics are defined

Source: https://platform.claude.com/llms-full.txt#how-metrics-are-defined

**Active users.** A user counts as active for a day if any of the following is true: they sent at least one chat message in Claude, they had at least one Claude Code session (local or remote) associated with your Claude Enterprise organization that included tool use or git activity, or they had at least one Cowork session with tool use or message activity.

**Per-product metric blocks.** Per-product metric objects (for example, Office Agent or Cowork metrics on a user-activity record) are always present on every record. Organizations without usage of that product see all-zero values rather than `null`.

**Connector names.** Connector names are normalized across sources. For example, `Atlassian MCP server`, `mcp-atlassian`, and `atlassian_MCP` all appear as `atlassian` in the connector usage endpoint.
