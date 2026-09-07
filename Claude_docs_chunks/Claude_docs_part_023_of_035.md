# platform.claude.com Documentation (Part 23 of 35)

## Get a first verdict round trip

Source: https://platform.claude.com/llms-full.txt#get-a-first-verdict-round-trip

The smallest working integration is a server that reads each request and allows it. Run one of the following servers, expose it at a public `https://` URL (for example, behind a TLS-terminating reverse proxy on a host you control, not a reverse-tunnel service; see [Receive a request](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#receive-a-request)), then have your administrator [set it as the endpoint and test the connection](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration): the **Test connection** result reports the allow verdict your server returned.

<CodeGroup exclude="shell">
  ```python Python
  # Run with: python server.py
  from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


  class VerdictHandler(BaseHTTPRequestHandler):
      protocol_version = "HTTP/1.1"  # keep the connection open between verdicts

      def do_POST(self):
          # Drain the body; transcripts can be megabytes.
          self.rfile.read(int(self.headers.get("Content-Length", 0)))
          verdict = b'{"action": "allow"}'
          self.send_response(200)
          self.send_header("Content-Type", "application/json")
          self.send_header("Content-Length", str(len(verdict)))
          self.end_headers()
          self.wfile.write(verdict)


  ThreadingHTTPServer(("", 8000), VerdictHandler).serve_forever()

typescript TypeScript
  // Run with: node server.ts
  import { createServer } from "node:http";

  createServer((request, response) => {
    // Drain the body before answering; transcripts can be megabytes.
    request.resume();
    request.on("end", () => {
      response.writeHead(200, { "Content-Type": "application/json" });
      response.end('{"action": "allow"}');
    });
  }).listen(8000);

csharp C#
  #:sdk Microsoft.NET.Sdk.Web
  #:property PublishAot=false
  // Run with: dotnet run server.cs

  var app = WebApplication.Create();

  app.MapPost("/{**path}", async (HttpRequest request) =>
  {
      // Drain the body; transcripts can be megabytes.
      await request.Body.CopyToAsync(Stream.Null);
      return Results.Text("""{"action": "allow"}""", "application/json");
  });

  app.Run("http://0.0.0.0:8000");

go Go
  // Run with: go run server.go
  package main

  import (
  	"io"
  	"log"
  	"net/http"
  )

  func main() {
  	http.HandleFunc("POST /", func(writer http.ResponseWriter, request *http.Request) {
  		// Drain the body so the connection can be reused; transcripts can be megabytes.
  		io.Copy(io.Discard, request.Body)
  		writer.Header().Set("Content-Type", "application/json")
  		writer.Write([]byte(`{"action": "allow"}`))
  	})
  	log.Fatal(http.ListenAndServe(":8000", nil))
  }

java Java
  // Run with: java VerdictServer.java
  import com.sun.net.httpserver.HttpServer;

  void main() throws IOException {
      HttpServer server = HttpServer.create(new InetSocketAddress(8000), 0);
      server.createContext("/", exchange -> {
          // Drain the body without buffering it; transcripts can be megabytes.
          exchange.getRequestBody().transferTo(OutputStream.nullOutputStream());
          byte[] verdict = "{\"action\": \"allow\"}".getBytes(StandardCharsets.UTF_8);
          exchange.getResponseHeaders().set("Content-Type", "application/json");
          exchange.sendResponseHeaders(200, verdict.length);
          try (OutputStream responseBody = exchange.getResponseBody()) {
              responseBody.write(verdict);
          }
      });
      server.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
      server.start();
  }

php PHP
  <?php
  // Run with: php -S 0.0.0.0:8000 server.php

  // Drain the body; transcripts can be megabytes.
  file_get_contents('php://input');

  http_response_code(200);
  header('Content-Type: application/json');
  echo '{"action": "allow"}';

ruby Ruby
  # webrick is a regular gem in Ruby 3.4: gem install webrick, or add gem "webrick".
  # Run with: ruby server.rb
  require "webrick"

  server = WEBrick::HTTPServer.new(Port: 8000)
  server.mount_proc("/") do |request, response|
    request.body # Drain the body; transcripts can be megabytes.
    response.status = 200
    response["Content-Type"] = "application/json"
    response.body = '{"action": "allow"}'
  end
  server.start
  ```
</CodeGroup>

<Note>
  These servers accept every request, including unsigned ones. Add [signature verification](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#verify-the-signature) before you enforce.
</Note>


## Receive a request

Source: https://platform.claude.com/llms-full.txt#receive-a-request

Anthropic sends an HTTPS `POST` to the URL your administrator configures. The whole configured URL is the endpoint: there is no fixed path suffix, so choose any path that suits your server.

Host your AI security server where Anthropic can reach it: an `https://` URL on port 443, on a publicly routable host (private, loopback, and carrier-grade NAT ranges are refused at connect time), with a certificate that validates against the public CA trust store, responding without redirects. The configured URL must be the final destination. Reverse-tunnel hosts (ngrok and similar tunnel services) are not supported: Anthropic's network policy blocks them. Host your server on a domain you control. [Configure Inference hooks](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration) covers how your administrator sets and tests the URL.

Every request carries these fixed headers, along with any [custom request headers](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration) your administrator configured and, once your organization has a signing secret, the `webhook-*` signature headers described in [Verify the signature](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#verify-the-signature):

| Header            | Value              |
| ----------------- | ------------------ |
| `Content-Type`    | `application/json` |
| `User-Agent`      | `anthropic-dlp/1`  |
| `Accept-Encoding` | `identity`         |

There is one hook event today: the prompt frame, sent once per governed inference request, before inference begins. Anthropic holds the request until your AI security server responds or the verdict timeout elapses.


## The prompt frame

Source: https://platform.claude.com/llms-full.txt#the-prompt-frame

The request body is a JSON object with these fields:

| Field        | Type           | Description                                                                                                                                                                                                                                                              |
| ------------ | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `type`       | string         | The hook event. Always `"prompt"` today; other event types will be introduced in the future, so handle an unrecognized value gracefully (see [Forward compatibility](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#forward-compatibility)). |
| `request_id` | string         | Opaque per-inference-call identifier for correlation. Equals the `webhook-id` header.                                                                                                                                                                                    |
| `tenant_id`  | string or null | Opaque identifier for the organization the request belongs to.                                                                                                                                                                                                           |
| `actor`      | object         | The principal the request is attributed to, discriminated on `type` (`"user"` is the only value sent today): `id` (a tagged identifier, stable across requests for the same account) and `email_address` (when available). Both `id` and `email_address` can be null.    |
| `source`     | object         | The originating application: `application` (see [Source values](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#source-values)).                                                                                                              |
| `messages`   | array          | The conversation transcript up to the point of inference. See [Content blocks](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#content-blocks).                                                                                               |
| `session_id` | string or null | Opaque conversation identifier, when one exists. Don't parse it. For Claude Code it is a best-effort, client-asserted session identifier.                                                                                                                                |
| `model`      | string or null | Public model identifier for this request, when available.                                                                                                                                                                                                                |
| `metadata`   | object         | Reserved extension map of string keys to string values, sent empty today. Require nothing from it, and tolerate its absence, its presence, and any keys that appear.                                                                                                     |

<Note>
  Requests currently also carry deprecated legacy aliases of some of these fields. Read the field names documented on this page and ignore any others; the aliases exist only for earlier integrations.
</Note>

An example request body:

### Content blocks

Each entry in `messages` has a `role` of `user` or `assistant` (tool results appear under the `user` role, matching the public Messages API content model) and a `content` array of blocks discriminated by `type`:

| Block `type`  | Fields                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `text`        | `text`: the text content.                                                                                                                                                                                                                                                                                                                                                                    |
| `tool_use`    | `id`: the identifier the matching tool result references. `tool_name`: the tool's name. `input`: the arguments the model passed to the tool.                                                                                                                                                                                                                                                 |
| `tool_result` | `content`: the tool's output as text, with parts joined by newlines; binary parts such as images are replaced by placeholder markers, and raw bytes are never sent. `is_error`: whether the tool call failed. `tool_name`: the tool's name, so a policy can condition on tool identity without cross-referencing an earlier block. `tool_use_id`: the `id` of the matching `tool_use` block. |
| `attachment`  | `file_name`: the original file name or path. `media_type`: the attachment's media type. `size_bytes`: the size of the original file. `text`: the text content of the attachment when available, such as extracted document text, an audio transcript, or link metadata. Raw attachment bytes are never sent.                                                                                 |

A block whose `type` you don't recognize is a forward-compatible addition. The only field it guarantees is `type`; your policy may inspect whatever other fields are present, but must not reject the request because of an unrecognized type.

### What the transcript contains

The transcript is the conversation as the end user sees it, up to the point of inference: transcript text, tool calls and their results, extracted attachment text, and prior turns. It never includes system prompts, tool definitions, Anthropic-internal context, Claude's hidden reasoning, or raw file bytes.

A turn whose every block is excluded is omitted entirely, so don't assume strict user and assistant alternation.

Transcripts are sent untruncated, so a long conversation with large attachments produces a large request body, up to an upper bound of 10 MB. Raise your server's body limit to accept that ceiling. Several common defaults are much smaller, including nginx `client_max_body_size` at 1 MB and Express `express.json()` at 100 kB, and a rejected body counts as a webhook failure, so under **Allow the request** failure handling an oversized prompt would reach the model uninspected.

### Source values

`source.application` is an open string, not a closed enum. Known values are `claude-ai` and `claude-code`; [connection tests](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration) use `config-test`. New values may appear, and your server must not reject a request because of one it doesn't recognize.

Treat `source.application` as advisory routing metadata, not a trust boundary: don't rest a security-critical policy decision on it alone.


## Return a verdict

Source: https://platform.claude.com/llms-full.txt#return-a-verdict

Respond with HTTP 200 and a JSON verdict body for both outcomes; the `action` field discriminates. To allow the request:

To deny it:

| Field          | Constraints                                                     | Semantics                                                                                                                                                                                                                                                                                           |
| -------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `action`       | `"allow"` or `"deny"`; required                                 | `allow` lets inference proceed; `deny` rejects it.                                                                                                                                                                                                                                                  |
| `deny_reason`  | string or null; at most 500 characters, longer values truncated | Shown to the end user when `action` is `deny`; ignored on `allow`.                                                                                                                                                                                                                                  |
| `reference_id` | string or null; at most 50 characters from `[A-Za-z0-9._:/-]`   | Your own identifier for this evaluation. It's recorded on the denial's `inference_hooks_request_denied` [compliance activity](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) and never shown to the end user. Keep it opaque: no request content and no personal data. |

A deny is never discarded over a formatting problem: an oversize `deny_reason` is truncated, a malformed `reference_id` is silently dropped, and the `action` is still honored.

The reverse doesn't hold. Anything other than HTTP 200 with a parseable verdict is a webhook failure, and your organization's [failure handling](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration) applies instead of a verdict. In particular:

* Don't signal a deny with an error status. A non-200 response is a failure, not a deny.
* Any `action` value other than `allow` or `deny` is treated as a webhook failure.

Anthropic reads at most 64 KiB of the response body, and the body must be uncompressed. Redirects are not followed, and cookies are ignored. Unknown fields in the verdict body are ignored, so you can return a richer object alongside the fields documented here.


## Verify the signature

Source: https://platform.claude.com/llms-full.txt#verify-the-signature-2

Requests are signed per the [Standard Webhooks](https://www.standardwebhooks.com/) specification, using three headers. Anthropic sends the header names in lowercase, and proxies are free to re-case them, so look them up case-insensitively.

| Header              | Contents                                                                                                                                                                                                         |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `webhook-id`        | Unique identifier for this delivery. Equals the body's `request_id`. Use it as an idempotency key and as the first component of the signed payload.                                                              |
| `webhook-timestamp` | Unix time in seconds, as a decimal string, when the request was signed. Reject a timestamp more than five minutes from your server's clock, in either direction.                                                 |
| `webhook-signature` | One or more space-separated `v1,<base64>` values, each an HMAC-SHA256 over `{webhook-id}.{webhook-timestamp}.{raw body bytes}`. Accept the request if any value matches yours, using a constant-time comparison. |

Two details cause most verification bugs:

* **Verify raw bytes.** Compute the HMAC over the body exactly as received, before any JSON parsing or re-encoding.
* **Decode the secret with a standard base64 decoder.** The signing secret is the value after the `whsec_` prefix, encoded with the standard base64 alphabet (`+` and `/`), as is the signature in the header. A URL-safe decoder derives the wrong key bytes whenever the secret contains `+` or `/`, which is most of the time.

Once your organization has a signing secret, every request Anthropic sends is signed, and [enabling Inference hooks requires one](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration), so reject any request that arrives unsigned. One exception: a connection test sent before your organization's first save arrives unsigned, because the signing secret doesn't exist yet. Accept unsigned requests until your administrator confirms the secret exists, then reject them.

[Rotating the secret](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration#rotate-your-signing-secret) is an immediate cutover, but requests signed with the previous secret can still arrive for about a minute afterward, plus anything already in flight. Have your AI security server accept signatures from both secrets during the switchover so those stragglers aren't rejected.

The following samples are server implementations, so there is no shell tab: an AI security server is a long-running HTTPS service rather than a one-shot request. Each sample uses only the language's standard library; the [Standard Webhooks](https://www.standardwebhooks.com/) project also publishes verification libraries for most languages.

<CodeGroup exclude="shell">
  ```python Python
  import base64
  import hashlib
  import hmac
  import time

  TOLERANCE_SECONDS = 300


  def verify(secret: str, headers: dict[str, str], body: bytes) -> bool:
      """Return True if the body was signed by Anthropic for this organization.

      Anthropic sends header names in lowercase, but proxies are free to
      re-case them, so normalize the lookup to lowercase.
      """
      lowercased = {name.lower(): value for name, value in headers.items()}
      try:
          message_id = lowercased["webhook-id"]
          timestamp = lowercased["webhook-timestamp"]
          signatures = lowercased["webhook-signature"]
      except KeyError:
          return False  # unsigned request: not from Anthropic

      try:
          signed_at = int(timestamp)
      except ValueError:
          return False
      if abs(time.time() - signed_at) > TOLERANCE_SECONDS:
          return False  # replayed, or the clocks disagree

      try:
          key = base64.b64decode(secret.removeprefix("whsec_"), validate=True)
      except ValueError:
          return False  # misconfigured secret: reject rather than crash

      payload = f"{message_id}.{timestamp}.".encode() + body
      expected = b"v1," + base64.b64encode(
          hmac.new(key, payload, hashlib.sha256).digest()
      )

      # Compare bytes: compare_digest on str raises on non-ASCII input.
      return any(
          hmac.compare_digest(expected, candidate.encode())
          for candidate in signatures.split()
      )

typescript TypeScript
  import { createHmac, timingSafeEqual } from "node:crypto";
  import type { IncomingHttpHeaders } from "node:http";

  const TOLERANCE_SECONDS = 300;

  /**
   * Returns true if the body was signed by Anthropic for this organization.
   *
   * Node lowercases incoming header names, matching how Anthropic sends
   * them, so look them up in lowercase.
   */
  export function verify(secret: string, headers: IncomingHttpHeaders, body: Buffer): boolean {
    const messageId = headers["webhook-id"];
    const timestamp = headers["webhook-timestamp"];
    const signatures = headers["webhook-signature"];
    if (
      typeof messageId !== "string" ||
      typeof timestamp !== "string" ||
      typeof signatures !== "string"
    ) {
      return false; // unsigned request: not from Anthropic
    }

    const signedAt = Number(timestamp);
    if (
      !Number.isFinite(signedAt) ||
      Math.abs(Date.now() / 1000 - signedAt) > TOLERANCE_SECONDS
    ) {
      return false; // replayed, or the clocks disagree
    }

    const key = Buffer.from(secret.replace(/^whsec_/, ""), "base64");
    const payload = Buffer.concat([Buffer.from(`${messageId}.${timestamp}.`), body]);
    const expected = Buffer.from(
      "v1," + createHmac("sha256", key).update(payload).digest("base64")
    );

    return signatures.split(" ").some((candidate) => {
      const candidateBytes = Buffer.from(candidate);
      return (
        candidateBytes.length === expected.length && timingSafeEqual(candidateBytes, expected)
      );
    });
  }

csharp C#
  using System.Security.Cryptography;
  using System.Text;

  static class InferenceHooks
  {
      private const int ToleranceSeconds = 300;

      /// <summary>
      /// Returns true if the body was signed by Anthropic for this organization.
      /// Anthropic sends header names in lowercase, but proxies are free to
      /// re-case them, so match them case-insensitively.
      /// </summary>
      public static bool Verify(string secret, IReadOnlyDictionary<string, string> headers, byte[] body)
      {
          // TryAdd keeps the first value if a proxy delivered case-duplicate
          // names; the copying constructor would throw on them instead.
          var lookup = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
          foreach (var (name, value) in headers)
          {
              lookup.TryAdd(name, value);
          }

          if (!lookup.TryGetValue("webhook-id", out var messageId) ||
              !lookup.TryGetValue("webhook-timestamp", out var timestamp) ||
              !lookup.TryGetValue("webhook-signature", out var signatures))
          {
              return false; // unsigned request: not from Anthropic
          }

          if (!long.TryParse(timestamp, out var signedAt) ||
              Math.Abs(DateTimeOffset.UtcNow.ToUnixTimeSeconds() - signedAt) > ToleranceSeconds)
          {
              return false; // replayed, or the clocks disagree
          }

          // Standard base64 alphabet: a URL-safe decoder derives the wrong key bytes.
          var encodedKey = secret.StartsWith("whsec_") ? secret["whsec_".Length..] : secret;
          byte[] key;
          try
          {
              key = Convert.FromBase64String(encodedKey);
          }
          catch (FormatException)
          {
              return false; // misconfigured secret: reject rather than crash
          }

          byte[] payload = [.. Encoding.UTF8.GetBytes($"{messageId}.{timestamp}."), .. body];
          var expected = Encoding.UTF8.GetBytes(
              "v1," + Convert.ToBase64String(HMACSHA256.HashData(key, payload)));

          // FixedTimeEquals is constant-time and returns false on a length mismatch.
          return signatures.Split(' ', StringSplitOptions.RemoveEmptyEntries).Any(candidate =>
              CryptographicOperations.FixedTimeEquals(Encoding.UTF8.GetBytes(candidate), expected));
      }
  }

go Go
  package hooks

  import (
  	"crypto/hmac"
  	"crypto/sha256"
  	"encoding/base64"
  	"net/http"
  	"strconv"
  	"strings"
  	"time"
  )

  const toleranceSeconds = 300

  // verify reports whether body was signed by Anthropic for this organization.
  // net/http canonicalizes header names on lookup, so re-cased names still match.
  func verify(secret string, header http.Header, body []byte) bool {
  	messageID := header.Get("webhook-id")
  	timestamp := header.Get("webhook-timestamp")
  	signatures := header.Get("webhook-signature")
  	if messageID == "" || timestamp == "" || signatures == "" {
  		return false // unsigned request: not from Anthropic
  	}

  	signedAt, err := strconv.ParseInt(timestamp, 10, 64)
  	if err != nil {
  		return false
  	}
  	age := time.Now().Unix() - signedAt
  	if age > toleranceSeconds || age < -toleranceSeconds {
  		return false // replayed, or the clocks disagree
  	}

  	// Standard base64 alphabet: a URL-safe decoder derives the wrong key bytes.
  	key, err := base64.StdEncoding.DecodeString(strings.TrimPrefix(secret, "whsec_"))
  	if err != nil {
  		return false
  	}

  	mac := hmac.New(sha256.New, key)
  	mac.Write([]byte(messageID + "." + timestamp + "."))
  	mac.Write(body)
  	expected := "v1," + base64.StdEncoding.EncodeToString(mac.Sum(nil))

  	for _, candidate := range strings.Fields(signatures) {
  		if hmac.Equal([]byte(candidate), []byte(expected)) { // constant-time
  			return true
  		}
  	}
  	return false
  }

java Java
  import java.nio.charset.StandardCharsets;
  import java.security.GeneralSecurityException;
  import java.security.MessageDigest;
  import java.time.Instant;
  import java.util.Base64;
  import java.util.HashMap;
  import java.util.Locale;
  import java.util.Map;
  import javax.crypto.Mac;
  import javax.crypto.spec.SecretKeySpec;

  public final class InferenceHookVerifier {
      private static final long TOLERANCE_SECONDS = 300;

      /**
       * Returns true if the body was signed by Anthropic for this organization.
       *
       * <p>Anthropic sends header names in lowercase, but proxies are free to
       * re-case them, so normalize the lookup to lowercase.
       */
      public static boolean verify(String secret, Map<String, String> headers, byte[] body) {
          Map<String, String> lowercased = new HashMap<>();
          headers.forEach((name, value) -> lowercased.put(name.toLowerCase(Locale.ROOT), value));

          String messageId = lowercased.get("webhook-id");
          String timestamp = lowercased.get("webhook-timestamp");
          String signatures = lowercased.get("webhook-signature");
          if (messageId == null || timestamp == null || signatures == null) {
              return false; // unsigned request: not from Anthropic
          }

          long signedAt;
          try {
              signedAt = Long.parseLong(timestamp);
          } catch (NumberFormatException _) {
              return false;
          }
          if (Math.abs(Instant.now().getEpochSecond() - signedAt) > TOLERANCE_SECONDS) {
              return false; // replayed, or the clocks disagree
          }

          // Standard base64 alphabet: a URL-safe decoder derives the wrong key bytes.
          byte[] key;
          try {
              key = Base64.getDecoder().decode(
                      secret.startsWith("whsec_") ? secret.substring("whsec_".length()) : secret);
          } catch (IllegalArgumentException _) {
              return false; // misconfigured secret: reject rather than crash
          }

          byte[] expected;
          try {
              Mac mac = Mac.getInstance("HmacSHA256");
              mac.init(new SecretKeySpec(key, "HmacSHA256"));
              mac.update((messageId + "." + timestamp + ".").getBytes(StandardCharsets.UTF_8));
              expected = ("v1," + Base64.getEncoder().encodeToString(mac.doFinal(body)))
                      .getBytes(StandardCharsets.UTF_8);
          } catch (GeneralSecurityException impossible) {
              // Every JVM ships HmacSHA256, so this never fires at runtime.
              throw new IllegalStateException(impossible);
          }

          for (String candidate : signatures.split(" ")) {
              if (MessageDigest.isEqual(candidate.getBytes(StandardCharsets.UTF_8), expected)) {
                  return true; // MessageDigest.isEqual is constant-time
              }
          }
          return false;
      }
  }

php PHP
  const TOLERANCE_SECONDS = 300;

  /**
   * Returns true if the body was signed by Anthropic for this organization.
   *
   * Anthropic sends header names in lowercase, but proxies are free to
   * re-case them, so normalize the lookup to lowercase.
   */
  function verify(string $secret, array $headers, string $body): bool
  {
      $lowercased = array_change_key_case($headers, CASE_LOWER);
      $messageId = $lowercased['webhook-id'] ?? null;
      $timestamp = $lowercased['webhook-timestamp'] ?? null;
      $signatures = $lowercased['webhook-signature'] ?? null;
      if ($messageId === null || $timestamp === null || $signatures === null) {
          return false; // unsigned request: not from Anthropic
      }

      $signedAt = filter_var($timestamp, FILTER_VALIDATE_INT);
      if ($signedAt === false || abs(time() - $signedAt) > TOLERANCE_SECONDS) {
          return false; // replayed, or the clocks disagree
      }

      // Standard base64 alphabet: a URL-safe decoder derives the wrong key bytes.
      $encodedKey = str_starts_with($secret, 'whsec_') ? substr($secret, strlen('whsec_')) : $secret;
      $key = base64_decode($encodedKey, strict: true);
      if ($key === false) {
          return false;
      }

      $payload = "{$messageId}.{$timestamp}." . $body;
      $expected = 'v1,' . base64_encode(hash_hmac('sha256', $payload, $key, binary: true));

      foreach (explode(' ', $signatures) as $candidate) {
          if (hash_equals($expected, $candidate)) { // constant-time
              return true;
          }
      }
      return false;
  }

ruby Ruby
  # base64 is a bundled gem in Ruby 3.4: Bundler-managed apps add gem "base64".
  require "base64"
  require "openssl"

  TOLERANCE_SECONDS = 300

  # Returns true if the body was signed by Anthropic for this organization.
  #
  # Anthropic sends header names in lowercase, but proxies are free to
  # re-case them, so normalize the lookup to lowercase.
  def verify(secret, headers, body)
    lowercased = headers.transform_keys(&:downcase)
    message_id = lowercased["webhook-id"]
    timestamp = lowercased["webhook-timestamp"]
    signatures = lowercased["webhook-signature"]
    if message_id.nil? || timestamp.nil? || signatures.nil?
      return false # unsigned request: not from Anthropic
    end

    signed_at = Integer(timestamp, exception: false)
    if signed_at.nil? || (Time.now.to_i - signed_at).abs > TOLERANCE_SECONDS
      return false # replayed, or the clocks disagree
    end

    # Standard base64 alphabet: a URL-safe decoder derives the wrong key bytes.
    begin
      key = Base64.strict_decode64(secret.delete_prefix("whsec_"))
    rescue ArgumentError
      return false # misconfigured secret: reject rather than crash
    end

    # Feed the body separately so its encoding never has to match the prefix's.
    hmac = OpenSSL::HMAC.new(key, "SHA256")
    hmac.update("#{message_id}.#{timestamp}.")
    hmac.update(body)
    expected = "v1," + Base64.strict_encode64(hmac.digest)

    signatures.split(" ").any? do |candidate|
      # fixed_length_secure_compare raises on a length mismatch, so screen lengths first.
      candidate.bytesize == expected.bytesize &&
        OpenSSL.fixed_length_secure_compare(candidate, expected)
    end
  end
  ```
</CodeGroup>


## Operational semantics

Source: https://platform.claude.com/llms-full.txt#operational-semantics

### Timeout and retry

Your administrator sets a verdict timeout between 1 and 10,000ms (5,000ms by default). The budget covers the entire exchange: connection, TLS handshake, request, and response.

Anthropic retries exactly once, after a 100ms delay, and only when the connection attempt fails. The retry shares the same timeout budget and carries the same `webhook-id` and the same signature. Once your AI security server has responded, the exchange is never retried.

### Webhook failures

Timeouts, non-200 statuses (redirects included), unparseable or oversized response bodies, and unreachable endpoints are all webhook failures. A webhook failure never becomes a deny; instead, your organization's [failure handling](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration) setting decides whether the affected request is blocked or proceeds without inspection.

### Circuit breaker

Sustained webhook failures attributable to your AI security server trip a circuit breaker that stops enforcement: Anthropic stops contacting your server, and failure handling applies to every request.

Starting 10 minutes after the trip, Anthropic tests whether your server has recovered: at most about once per minute, one request, carried by your organization's own traffic, is delivered to your server for inspection, signed and shaped like any other. Respond to it normally. A valid verdict, allow or deny, resets the breaker and enforcement resumes. A webhook failure leaves the breaker tripped, and testing continues. Either way, the test request itself proceeds for its user: its verdict is not enforced, and a failed test does not block it, even under **Block the request**. An administrator can also reset the breaker at any time, and administrator configuration changes stop the automatic testing; see [Circuit breaker](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration#circuit-breaker).

Each trip is recorded as an `inference_hooks_circuit_breaker_tripped` activity in the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed), one activity per trip. While the breaker is tripped, no per-request Inference hooks activities are recorded, so the trip activity is the feed's only record of the tripped window.

### Latency

Enforcement adds your AI security server's round trip to the latency of every governed request in your organization. Keep the verdict fast, and load-test your server before rolling it out to a large organization.

### Source IP addresses

Requests to your AI security server originate from `160.79.106.0/24`, part of Anthropic's published [outbound IP ranges](https://platform.claude.com/docs/en/api/ip-addresses). Allowlist that block, not the inbound ranges on the same page, which don't cover it. Allowlisting narrows your server's exposure, but it is not a substitute for signature verification: the block carries Anthropic egress traffic beyond Inference hooks.


## Forward compatibility

Source: https://platform.claude.com/llms-full.txt#forward-compatibility

The protocol grows without breaking correctly written servers. Your server must ignore:

* Unknown top-level fields on the prompt frame.
* Unknown keys in `metadata`.
* New `source.application` values.
* New `actor.type` values. `actor` is a union discriminated on `type`, and `"user"` is the only kind sent today; a future kind guarantees only that `type` is present.
* Content blocks with an unrecognized `type`.

Never reject a request because of an unrecognized block type or field; read the fields you know and skip the rest.

Other hook event types will be introduced in the future. A new event type is an addition your server can't handle by skipping a field: the request still needs a verdict. When the top-level `type` is a value you don't recognize, return an allow verdict rather than an error status; an error response is a [webhook failure](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#webhook-failures), and sustained failures trip the [circuit breaker](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#circuit-breaker).


## Design your integration

Source: https://platform.claude.com/llms-full.txt#design-your-integration

A production AI security server makes a few design choices beyond the wire protocol.

**Deduplicate on `webhook-id`.** The `webhook-id` header is unique per delivery and equals the body's `request_id`, and a connection-failure retry reuses it, so it works as an idempotency key. If you record verdicts, key the records on it.

**Record verdicts and join denials.** Store each verdict you return along with its `reference_id`. Every denial is recorded as an `inference_hooks_request_denied` compliance activity carrying the `reference_id` your server returned, so you can join denials in the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) to the matching records in your own system.

**Archive with an always-allow server.** To capture transcripts in real time without policing them, return `{"action": "allow"}` unconditionally and persist the frame after responding. This is a push-based alternative to polling the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api), and answering before you persist keeps your round trip out of the user's critical path.

**Write `deny_reason` for the end user.** The text you return is what the user sees when their request is blocked, truncated at 500 characters. Tell them what to change, such as which kind of content to remove, rather than emitting a scanner code that only your team can interpret.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-91

<CardGroup cols={2}>
  <Card title="Configure Inference hooks" href="https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration">
    Enable Inference hooks, connect and test your endpoint, and control enforcement, failure handling, and rollout.
  </Card>

  <Card title="Inference hooks overview" href="https://platform.claude.com/docs/en/manage-claude/inference-hooks">
    What Inference hooks are, how the verdict round trip works, and when to use them.
  </Card>
</CardGroup>


---
title: Inference hooks
url: https://platform.claude.com/docs/en/manage-claude/inference-hooks
description: Send each governed prompt to your organization's AI security server for an allow or deny verdict before inference proceeds.
---

<Note>
  Inference hooks are in beta and available to Claude Enterprise organizations. Configuring them requires the `organization:manage` permission in claude.ai, which the built-in Admin, Owner, and Primary owner roles hold; see [Configure Inference hooks](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration).
</Note>

Inference hooks let a Claude Enterprise organization route every governed prompt through an AI security server, an HTTPS service that the organization or its security vendor operates, before inference runs. When a user submits a prompt, Anthropic sends the conversation transcript to your AI security server and waits for an allow or deny verdict; a denied request never reaches the model. Security and compliance teams use Inference hooks to enforce data policies inline, and developers build the AI security server that evaluates each request.

Because the hook runs on Anthropic's servers, after the request leaves the client and before the model runs, it applies to every governed request uniformly, with nothing to install or deploy on user devices.

Today the only hook event is `prompt`, which fires once per governed inference request, before inference begins. Response-side enforcement is planned as a later event.

***


## How Inference hooks work

Source: https://platform.claude.com/llms-full.txt#how-inference-hooks-work

1. A user submits a prompt on a governed surface.
2. Anthropic sends an HTTPS `POST` to your organization's configured AI security server endpoint. The request body carries the conversation transcript, and each request is signed according to the [Standard Webhooks](https://www.standardwebhooks.com/) specification once your organization generates its signing secret, so your server can verify it came from Anthropic.
3. Your AI security server evaluates the content and responds with a verdict within the verdict timeout your organization configures (5 seconds by default).
4. On `allow`, inference proceeds normally. On `deny`, the request is rejected and the user sees a blocked-by-policy message assembled from two parts: the per-request reason your AI security server supplied in the verdict's `deny_reason` field, followed by a standing message your administrators configure (for example, who to contact or where to request an exception). If your administrators haven't configured one, a built-in default directs the user to contact them. Each denial is also recorded in your organization's [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed).

The following diagram traces one example (a Cowork request where Claude also calls an O365 tool) to illustrate which parts of the flow are hooked. The hooked points are the diagram's steps 1 and 5, where the prompt arrives and the tool result returns; each results in the validation exchange with your AI security server shown in steps 2 and 6.

![Flow diagram: the AI security server validates both the prompt and the tool result before inference proceeds](https://platform.claude.com/docs/images/inference-hooks-flow.svg)

A verdict is a small JSON object: `{"action": "allow"}` lets the request proceed, and a deny carries the user-facing reason. For the full verdict schema, see [Return a verdict](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint#return-a-verdict).

Your AI security server sees what the user sees: transcript text, tool calls and their results, and text extracted from attachments. It never receives raw file or image bytes, system prompts, or Anthropic-internal context. Anthropic doesn't store prompt or response content as part of Inference hooks; it records only metadata about hook activity, such as verdicts, timestamps, and request identifiers.

If your AI security server is unreachable, returns an error, or doesn't respond within the timeout, your organization's failure handling setting decides the outcome: block the request, or allow it to proceed without inspection.

Enforcement can roll out at your pace, so nobody has to be blocked on day one: shadow mode observes verdicts on live traffic without blocking anything, a rollout percentage inspects a chosen fraction of requests, and exclusions exempt members of chosen roles entirely. See [Configure Inference hooks](https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration).

For the full request and response schemas, signature verification, and operational details, see [Develop an integration](https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint).

***


## Use cases

Source: https://platform.claude.com/llms-full.txt#use-cases-4

* **Data loss prevention (DLP).** Forward the transcript to your DLP scanner and deny prompts that carry regulated or classified material. This is the most common deployment.
* **Real-time transcript archival.** Archive each transcript as it arrives and always return `allow`, as a push-based alternative to polling the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api).
* **Prompt telemetry.** Measure how your organization uses Claude, at the moment of use.
* **Policy engines.** Enforce your own rules before inference: model allowlists, project-scoped restrictions, or working-hours controls.

***


## Current limitations

Source: https://platform.claude.com/llms-full.txt#current-limitations-3

* Attachments are represented by metadata and extracted text. Raw file and image bytes are never sent, so image-only content (for example, a screenshot of a document) is not inspected.
* Verdicts are allow or deny. Rewriting or redacting a prompt is not supported.
* Platform organizations (API access through the Claude Platform) are out of scope.

***


## Availability

Source: https://platform.claude.com/llms-full.txt#availability

Inference hooks are available to Claude Enterprise organizations. Configuring them requires the `organization:manage` permission, which the built-in Admin, Owner, and Primary owner roles hold, as does any custom role granted it.

One hook governs conversations across claude.ai, Cowork, and Claude Code sessions in your Claude Enterprise organization, whether they run on the web, in the desktop or mobile apps, or in the CLI. Inference hooks are not available on Amazon Bedrock or Google Cloud.

Governed requests are the inference requests behind the user's conversation. Ancillary requests, such as conversation title generation, aren't sent to your endpoint, and system prompts and tool definitions are never included in what is sent. Voice mode is not covered.

***


## Inference hooks versus the Compliance API

Source: https://platform.claude.com/llms-full.txt#inference-hooks-versus-the-compliance-api

Both features serve security, legal, and compliance teams at Claude Enterprise organizations.

|              | Inference hooks                                     | Compliance API                                                                                  |
| ------------ | --------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| When it acts | Inline, before inference runs                       | After the fact                                                                                  |
| What it does | Allows or denies each governed request in real time | Retrieves activity, chats, files, projects, session transcripts, and users for audit and export |
| Direction    | Anthropic calls your AI security server             | You call Anthropic's API                                                                        |

Use Inference hooks to stop a request before it reaches the model, and the [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) to audit what happened afterward.

***


## In this section

Source: https://platform.claude.com/llms-full.txt#in-this-section

<CardGroup>
  <Card href="https://platform.claude.com/docs/en/manage-claude/inference-hooks-configuration" title="Configure Inference hooks">
    Allow Inference hooks for your organization, set up and test your AI security server, choose failure handling, and enforce verdicts.
  </Card>

  <Card href="https://platform.claude.com/docs/en/manage-claude/inference-hooks-endpoint" title="Develop an Inference hooks integration">
    The request and verdict schemas, signature verification, operational semantics, and integration patterns for building the AI security server.
  </Card>
</CardGroup>


### Compliance API

---
title: Compliance API
url: https://platform.claude.com/docs/en/manage-claude/compliance-api
description: Programmatic access to your organization's Claude activity, chats, files, projects, sessions in Claude apps, and users for compliance, audit, and governance.
---

The Compliance API gives Claude Enterprise and Claude Console customers programmatic access to their organization's Activity Feed. For Claude Enterprise organizations, it also covers the directory of users, roles, and groups across every linked organization; the effective settings in force for each organization; the underlying chats, files, and projects in claude.ai organizations; and Cowork, Claude Code, Claude Science, and Claude for Microsoft 365 sessions. Security, legal, and compliance teams use it to audit activity, retrieve or delete content, and feed events into downstream tooling.

<Note>
  Two key types unlock the Compliance API. A **Compliance Access Key** (created in claude.ai) reaches every endpoint, and an **Admin API key** (created in Claude Console) reaches the Activity Feed only. See [Which key do you need?](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#which-key-do-you-need) for the full key-type comparison.
</Note>

The following call returns the most recent activity event in your organization. Any key with the `read:compliance_activities` scope can make it. To create a key and grant it that scope, see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).

```bash cURL
curl --fail-with-body -sS \
  "https://api.anthropic.com/v1/compliance/activities?limit=1" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01"

json Response
{
  "data": [
    {
      "id": "activity_01XyDMpzjS89pFZXqSFUBDr6",
      "created_at": "2026-04-10T08:09:10Z",
      "organization_id": "org_01Wv6QeBcDfGhJkLmNpQrSt8",
      "organization_uuid": "abcdef01-2345-6789-abcd-ef0123456789",
      "actor": {
        "type": "user_actor",
        "email_address": "user@example.com",
        "user_id": "user_01TuVwXyZaBcDeFgH2JkLmN4",
        "ip_address": "192.0.2.34",
        "user_agent": "Mozilla/5.0..."
      },
      "type": "claude_chat_created",
      "claude_chat_id": "claude_chat_01XyDMpzjS89pFZXqSFUBDr6",
      "claude_project_id": "claude_proj_01KGp4eZNug9ri4kE35RSppq"
    }
  ],
  "has_more": true,
  "first_id": "activity_01XyDMpzjS89pFZXqSFUBDr6",
  "last_id": "activity_01XyDMpzjS89pFZXqSFUBDr6"
}
```

***


## How the Compliance API works

Source: https://platform.claude.com/llms-full.txt#how-the-compliance-api-works

Every endpoint lives under `/v1/compliance/*` on `https://api.anthropic.com`, authenticates through the `x-api-key` header, and takes the [`anthropic-version`](https://platform.claude.com/docs/en/api/versioning) header on every request. To provision a key, see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).

The Activity Feed (`GET /v1/compliance/activities`) is available to any key that carries the `read:compliance_activities` scope; see [Query the Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) for filters, pagination, and the full `Activity` object. The remaining endpoints require a Compliance Access Key carrying the relevant scope.

A Claude Enterprise tenant has one parent organization (the top-level container that centralizes identity) with linked organizations of two kinds: claude.ai organizations, where users chat and store content, and Claude Console organizations, where users manage Claude API workloads. For a key that covers the parent organization, the directory endpoints (organizations, users, roles, and groups) return data from every linked organization of either kind. The content endpoints (chats, files, projects, project attachments, and sessions) serve Claude Enterprise data only. The chat, file, and project endpoints return claude.ai chats, files, and projects. The session endpoints return transcripts of Cowork, Claude Code, Claude Science, and Claude for Microsoft 365 sessions on users' machines (local sessions), captured while users are signed in with their Claude Enterprise account. They also return transcripts of Cowork sessions started on claude.ai web or mobile, which run in the cloud in Anthropic-managed environments (remote sessions). A standalone Claude Console organization (one with no parent organization) is not part of a Claude Enterprise tenant; it uses Admin API keys and can query the Activity Feed only.

All `/v1/compliance/*` endpoints share a rate limit of 600 requests per minute per parent organization (for a standalone Claude Console organization, per organization). The local session endpoints count only against that shared limit, and the remote session endpoints carry a second request budget on top. See [429 Too Many Requests](https://platform.claude.com/docs/en/manage-claude/compliance-errors#429-too-many-requests) for the response headers and retry contract.

***


## Versioning

Source: https://platform.claude.com/llms-full.txt#versioning-4

Send the `anthropic-version` header on every request; see [API versions](https://platform.claude.com/docs/en/api/versioning) for the available versions.

***


## Compliance API versus related features

Source: https://platform.claude.com/llms-full.txt#compliance-api-versus-related-features

A few adjacent features overlap with the Compliance API; here is how to choose.

### Export audit logs

The audit log export is a separate feature in [claude.ai > Organization settings > Data and privacy](https://claude.ai/admin-settings/data-privacy-controls) that lets owners and primary owners download a CSV of organization events. It's significantly narrower than the Compliance API: a capped lookback window, CSV download only, and no access to chat, file, or project content. Standardize on the Compliance API for ongoing programmatic use.

### Analytics API

Anthropic provides two analytics APIs: the Claude Enterprise Analytics API and the [Claude Code Analytics API](https://platform.claude.com/docs/en/manage-claude/claude-code-analytics-api). Both return aggregated usage and cost figures for IT, FinOps, and platform teams, whereas the Compliance API returns per-event records for security, legal, and compliance teams. The two API families answer different questions, use different keys, and are provisioned separately.

### OpenTelemetry logging

[Cowork's OpenTelemetry logging](https://support.claude.com/en/articles/14477985-monitor-claude-cowork-activity-with-opentelemetry) and [Claude Code monitoring](https://code.claude.com/docs/en/monitoring-usage) stream per-event telemetry, including token, cost, and host metadata, to a collector you run as activity happens, whereas the Compliance API returns retained per-session transcripts from Anthropic on request and works with your existing Compliance Access Key. OpenTelemetry logging can also capture prompts and responses, but Anthropic recommends the Compliance API for retrieving the content of Cowork and Claude Code sessions. For a table comparing local sessions, remote sessions, and OpenTelemetry logging, see the introduction to [Retrieve session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions).

### Inference hooks

[Inference hooks](https://platform.claude.com/docs/en/manage-claude/inference-hooks) (beta) act inline: your organization's AI security server receives each governed prompt before inference and can deny it in real time, whereas the Compliance API retrieves records after the fact and returns richer data, such as organization settings and full non-text files.

***


## In this section

Source: https://platform.claude.com/llms-full.txt#in-this-section-2

<CardGroup>
  <Card href="https://platform.claude.com/docs/en/manage-claude/compliance-api-access" title="Set up the Compliance API">
    Enable the Compliance API for your organization, then create a Compliance Access Key (with scoped permissions) or an Admin API key, and learn which to use.
  </Card>

  <Card href="https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed" title="Query the Activity Feed">
    Retrieve, filter, and paginate the shared Activity Feed. Supported by both key types.
  </Card>

  <Card href="https://platform.claude.com/docs/en/manage-claude/compliance-content-data" title="Retrieve and delete chats, files, and projects">
    Read chat content, files, and project attachments; delete chats, files, and projects on demand. Compliance Access Key required.
  </Card>

  <Card href="https://platform.claude.com/docs/en/manage-claude/compliance-sessions" title="Retrieve session transcripts">
    List the sessions your users run in Claude apps and agents, such as Cowork and Claude Code, and retrieve their transcripts. Compliance Access Key required.
  </Card>

  <Card href="https://platform.claude.com/docs/en/manage-claude/compliance-org-data" title="List organizations, users, roles, groups, and settings">
    Enumerate linked organizations, members, roles, and directory groups, and read each organization's effective settings.
  </Card>

  <Card href="https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns" title="Design your compliance integration">
    Choose a feed-consumption pattern, plan SIEM correlation, and decide your retention approach.
  </Card>

  <Card href="https://platform.claude.com/docs/en/manage-claude/compliance-errors" title="Handle Compliance API errors">
    Every 400, 401, 403, 404, 409, 429, and 5xx response the Compliance API returns, with the fix for each.
  </Card>

  <Card href="https://platform.claude.com/docs/en/api/compliance" title="API reference">
    Endpoint paths, parameters, and response schemas for every Compliance API call.
  </Card>

  <Card href="https://platform.claude.com/docs/en/manage-claude/compliance-faq" title="Compliance API FAQ">
    Answers to common key, scope, availability, and integration questions.
  </Card>
</CardGroup>


---
title: Compliance API FAQ
url: https://platform.claude.com/docs/en/manage-claude/compliance-faq
description: Answers to common questions about Compliance API access, scopes, retention, and integration.
---

<Note>
  To enable the Compliance API, see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).
</Note>


## Access and scopes

Source: https://platform.claude.com/llms-full.txt#access-and-scopes

<AccordionGroup>
  <Accordion title="Who can enable the Compliance API?">
    For a Claude Enterprise organization, the primary owner enables the Compliance API at [claude.ai > Organization settings > API](https://claude.ai/admin-settings/api-access), and enablement cascades from the parent organization to every linked organization. For an eligible standalone Claude Console organization (one with no parent organization), an organization admin enables it at [Claude Console > Settings > Security](https://platform.claude.com/settings/security). A Claude Console organization that is linked to a parent organization does not enable the Compliance API itself; it is enabled from the parent organization. See [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#set-up-the-compliance-api) for the steps.
  </Accordion>

  <Accordion title="Can I turn the Compliance API off after enabling it in Claude Console?">
    Yes. For a standalone Claude Console organization, an organization admin can turn the **Compliance API** toggle off at [Claude Console > Settings > Security](https://platform.claude.com/settings/security), the same place it is turned on. While the Compliance API is off, no activity events are recorded for your organization, so the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) receives no new events. If your organization is enrolled in [Access Transparency](https://platform.claude.com/docs/en/manage-claude/access-transparency), turning the Compliance API off also stops Access Transparency event delivery. Activity that is not recorded while the Compliance API is off cannot be recovered later. Turning the Compliance API back on resumes recording from that point forward; activity that was already recorded is not deleted.
  </Accordion>

  <Accordion title="Does turning the Compliance API off delete events that were already captured?">
    No. Turning the Compliance API off stops new activity events from being recorded, but it does not delete events that were already captured while it was on. Recording resumes from the point the Compliance API is turned back on.
  </Accordion>

  <Accordion title="Is turning the Compliance API off in Claude Console recorded anywhere?">
    Yes. When the Compliance API is turned off (or back on) in Claude Console, the change is recorded as an `org_compliance_api_settings_updated` activity in the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed), so your audit trail shows who changed the setting and when. This activity is an exception to the recording stop: the disable is recorded even though no other activity is recorded while the Compliance API is off.
  </Accordion>

  <Accordion title="Why doesn't my parent organization appear in Claude Console when creating an Admin API key?">
    This is expected. A Claude Enterprise parent organization centralizes identity across all linked organizations; it does not carry workloads, and it does not appear in Claude Console at all. Claude Console only ever shows the Claude Console organizations linked beneath the parent.

    To call the Compliance API, you create one of two key types instead:

    * **For full Compliance API access ([Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) plus chats, files, projects, sessions, users, organization metadata, and organization settings),** the primary owner of the parent organization (or an organization owner, for a key restricted to their own organization only) creates a [Compliance Access Key](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#set-up-the-compliance-api) in claude.ai.
    * **For Activity Feed access only,** an organization admin in your Claude Console organization creates an [Admin API key](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#create-an-admin-api-key) in Claude Console. The Compliance API must already be enabled for the organization, and the admin must create the Admin API key while the Compliance API is enabled for it to carry the `read:compliance_activities` scope.
  </Accordion>

  <Accordion title="Can I use my regular Claude API key with the Compliance API?">
    No. A Claude API key (`sk-ant-api03-...`) authenticates calls to Claude models on the Claude API; it does not authenticate calls to `/v1/compliance/*`. The Compliance API accepts only Compliance Access Keys (`sk-ant-api01-...`) and Admin API keys (`sk-ant-admin01-...`). See [Which key do you need?](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#which-key-do-you-need) for the full mapping.
  </Accordion>

  <Accordion title="Why does my Admin API key return 403 on chat or file endpoints?">
    Admin API keys carry a fixed `read:compliance_activities` scope, which authorizes the Activity Feed only. Every other Compliance API endpoint requires a scope that only a Compliance Access Key created in claude.ai can carry. Calling a content or directory endpoint with an Admin API key returns a 403 naming the scope that endpoint family requires: `read:compliance_user_data` for chats, files, projects, project attachments, sessions, users, and group members, and `read:compliance_org_data` for organizations, roles, groups, and effective organization settings. For example, listing chats returns the following response.

    ```json Response
    {
      "error": {
        "type": "permission_error",
        "message": "Missing required scopes. Got: ['read:compliance_activities'] Needed: ['read:compliance_user_data']"
      }
    }
    ```

    To access content endpoints, the primary owner of your parent organization (or an organization owner, for their own organization only) must [create a Compliance Access Key](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#set-up-the-compliance-api) with `read:compliance_user_data` (and `delete:compliance_user_data` for deletes), or `read:compliance_org_data` for organization, role, group, and effective-settings endpoints. A standalone Claude Console organization (one with no parent organization) cannot create a Compliance Access Key, so the content endpoints are not available to it; it can query the Activity Feed only. See [Handle Compliance API errors](https://platform.claude.com/docs/en/manage-claude/compliance-errors#403-forbidden) for the full per-endpoint catalog.
  </Accordion>
</AccordionGroup>


## Data coverage and retention

Source: https://platform.claude.com/llms-full.txt#data-coverage-and-retention

<AccordionGroup>
  <Accordion title="How far back does the Activity Feed go?">
    The Activity Feed retains 6 years of organization activity, and new events are queryable within 1 minute of occurring. The feed reaches back at most to the point the Compliance API was first enabled for your organization: recording is not retroactive, and activity from before enablement is not backfilled. Activity Feed retention is independent of your organization's content retention policy: chat, file, and project content follows the retention rules configured for your organization (indefinite by default), unless a user deletes it sooner.
  </Accordion>

  <Accordion title="Does the Activity Feed include prompt or message content?">
    No. The Activity Feed records who did what and when (authentication, chat creation, file uploads, project changes, administrative actions, and similar resource events), but it does not capture the prompt text or model responses inside chats or messages.

    To retrieve message bodies and file contents, use the chat, message, and file endpoints with a Compliance Access Key carrying `read:compliance_user_data`. The same key and scope retrieve transcripts of sessions on users' machines (such as Cowork and Claude Code sessions) through the [local session endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions), and transcripts of Cowork sessions in the cloud through the [remote session endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-remote-sessions). These endpoints serve Claude Enterprise content only; Claude Console workloads, and Claude API workloads authenticated with an API key, expose administrative and resource events through the Activity Feed but do not expose prompt text or model responses through the Compliance API.
  </Accordion>

  <Accordion title="Do Cowork, Claude Code, Claude Science, and Claude for Microsoft 365 sessions appear in the Compliance API?">
    Yes. Cowork sessions in Claude Desktop that run on users' machines, Claude Code sessions (in the terminal, in Claude Desktop, or in an IDE extension), sessions in the Claude Science desktop app, and Claude for Microsoft 365 sessions in Excel, PowerPoint, Word, and Outlook are captured while users are signed in with their Claude Enterprise account and are available through the [local session endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions). Cowork sessions started on claude.ai web or mobile, which run in the cloud in Anthropic-managed environments, are available through the [remote session endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-remote-sessions). Each family has a list endpoint that returns session metadata and a messages endpoint that returns the session transcript (user prompts, assistant responses, and tool calls and results). The local family adds a third endpoint that retrieves one session's metadata. All of these endpoints use your existing Compliance Access Key with `read:compliance_user_data`; no new key or scope is needed.

    Local sessions are captured as their requests reach the Claude API, so nothing is installed on the device, and on-device activity that never reaches the API is not captured. Claude Code sessions authenticated with a Claude Console API key, Claude Code sessions run through a third-party cloud platform (Amazon Bedrock, Google Cloud, or Microsoft Foundry), and Claude Code on the web are not captured. Claude Code on the web also runs in the cloud in Anthropic-managed environments, but it is not a remote session; the remote session endpoints return Cowork sessions only. Organizations with [HIPAA readiness](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#hipaa-readiness) enabled get no local session data, and sessions for which [zero data retention (ZDR)](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#zero-data-retention-zdr-scope) is in effect are excluded.

    The local and remote session endpoints are stable for Cowork and Claude Code sessions; coverage of Claude Science and Claude for Microsoft 365 sessions is in beta.
  </Accordion>

  <Accordion title="What do session transcripts include?">
    Local and remote session transcripts both carry user prompts, assistant responses, and tool calls and results. For local sessions (on users' machines), that is what Claude was asked to do and what it returned, not what happened on the device.

    | Data                              | Local sessions (on users' machines)                                                                                                                                                                                                                    | Remote sessions (in the cloud)                                                                                                                                                                           |
    | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | User prompts                      | Yes; returned as `text` blocks.                                                                                                                                                                                                                        | Yes; returned as `text` blocks.                                                                                                                                                                          |
    | Assistant responses               | Yes; text output only.                                                                                                                                                                                                                                 | Yes; text output only.                                                                                                                                                                                   |
    | Tool calls and results            | Yes; each `tool_use` input and each `text` entry in a `tool_result` is truncated to 10,000 bytes by default (up to about 1 MiB each on request).                                                                                                       | Yes; each `tool_use` input and each `text` entry in a `tool_result` is truncated to 10,000 bytes by default (up to about 1 MiB each on request).                                                         |
    | File contents and file names      | Yes; text that Claude reads through tools appears in the transcript, subject to the same truncation. Images, PDFs, and other binary or structured content appear only as placeholder `text` blocks. File names appear in tool-call inputs and outputs. | Yes; file contents and file names appear in the transcript through tool-call inputs and outputs (text only; other content is omitted).                                                                   |
    | Artifacts                         | Yes; generated content appears inside tool-call inputs in the transcript.                                                                                                                                                                              | Yes; generated content appears inside tool-call inputs in the transcript.                                                                                                                                |
    | Skills                            | Yes; skill content appears when the client sends it as message content, and it is not distinguished from other user text.                                                                                                                              | Yes; skill content appears in the transcript.                                                                                                                                                            |
    | Session metadata                  | Yes; owner (`user.id` and email address), organization, workspace, `product_surface`, `created_at`, and `updated_at`, from the list and retrieve endpoints. Local sessions carry no `status`.                                                          | Yes; owner, organization, status, timestamps, and `product_surface`, from the list endpoint.                                                                                                             |
    | Thinking blocks                   | No.                                                                                                                                                                                                                                                    | No.                                                                                                                                                                                                      |
    | Images and other non-text content | No; each image, PDF, or other binary or structured block appears as a placeholder `text` block (for example, `[image content not shown]`) with `truncated` set to `true`. Raw file bytes are never returned.                                           | No; non-text blocks are omitted, and raw file bytes are never returned.                                                                                                                                  |
    | Token usage, cost, and latency    | No; token usage and cost are available through the [Claude Enterprise Analytics API](https://platform.claude.com/docs/en/manage-claude/analytics-api#get-access-to-the-claude-enterprise-analytics-api).                                               | No; token usage and cost are available through the [Claude Enterprise Analytics API](https://platform.claude.com/docs/en/manage-claude/analytics-api#get-access-to-the-claude-enterprise-analytics-api). |

    See [Sessions on users' machines](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions) and [Sessions in the cloud](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-remote-sessions) for the endpoints and parameters.
  </Accordion>

  <Accordion title="How does session coverage compare with OpenTelemetry logging (OTEL) for Cowork and Claude Code?">
    [Cowork's OpenTelemetry logging](https://support.claude.com/en/articles/14477985-monitor-claude-cowork-activity-with-opentelemetry) and [Claude Code monitoring](https://code.claude.com/docs/en/monitoring-usage) overlap with the session endpoints but answer different needs: OTEL streams per-event telemetry to infrastructure you run as activity happens, whereas the Compliance API lets you retrieve retained per-session transcripts from Anthropic after the fact. OTEL can also capture prompts and responses, but Anthropic recommends the Compliance API for retrieving the content of Cowork and Claude Code sessions. For a table comparing local sessions, remote sessions, and OTEL, see the introduction to [Retrieve session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions).

    OTEL events and Compliance API records share organization and user identifiers, so you can join them.
  </Accordion>

  <Accordion title="Is deleted content recoverable through the Compliance API?">
    No. Deletes performed through the Compliance API are immediate, permanent, and not recoverable. The content of a chat that a user deletes in claude.ai is not recoverable either: the Compliance API still returns the chat and its messages, with `deleted_at` populated, but not their content. A remote session that a user deletes is likewise not recoverable, and the remote session endpoints no longer return it. Pull any content you need to retain (for legal hold or archival) while it is still available. See [Plan content retention](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns#plan-content-retention) for when to export content to your own archive.
  </Accordion>

  <Accordion title="What does the Compliance API not capture?">
    The Compliance API has known coverage boundaries: the Activity Feed records resource events but not prompt or response text, Claude Console and Claude API workloads authenticated with an API key expose no message content at all, and content removed by your retention policy, deleted by a user in claude.ai, or hard-deleted through the Compliance API is not recoverable. For the full coverage boundaries and delivery contract, see [Delivery guarantees and completeness](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns#delivery-guarantees-and-completeness).

    Session transcripts have boundaries of their own. Local sessions are captured only as their requests reach the Claude API, so on-device activity that never reaches the API is not captured. Claude Code sessions authenticated with a Claude Console API key, Claude Code sessions run through a third-party cloud platform (Amazon Bedrock, Google Cloud, or Microsoft Foundry), and Claude Code on the web are not captured either; organizations with HIPAA readiness enabled get no local session data; and sessions for which zero data retention is in effect are excluded. No session transcript, local or remote, includes thinking blocks or tool definitions. Organizations that use [customer-managed encryption keys](https://platform.claude.com/docs/en/manage-claude/cmek) receive local session transcripts as usual. While the key cannot be used, the messages endpoint returns [503 Service Unavailable](https://platform.claude.com/docs/en/manage-claude/compliance-errors#local-sessions-temporarily-unavailable) instead of transcript content, and session metadata is still listed.
  </Accordion>
</AccordionGroup>


## Integration and pagination

Source: https://platform.claude.com/llms-full.txt#integration-and-pagination

<AccordionGroup>
  <Accordion title="How do I correlate Compliance API records with my SIEM?">
    Join `Activity` records to your SIEM on `actor.user_id`, `actor.email_address`, `actor.ip_address`, `actor.user_agent`, and `created_at`. See [Design your compliance integration](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns#correlate-with-your-siem) for the join-key table and consumption patterns.
  </Accordion>

  <Accordion title="Can one customer have multiple organizations under one parent?">
    Yes. A Claude Enterprise parent organization can have many linked organizations, including a mix of claude.ai organizations and Claude Console organizations (for example, separate production and staging Claude Console organizations). Identity, SSO, and SCIM are shared across the parent; billing, members, projects, and API keys remain separate for each organization. Compliance API enablement happens at the parent organization level and cascades to all linked organizations, and a Compliance Access Key that covers the parent organization and carries `read:compliance_org_data` can enumerate every organization beneath the parent through `GET /v1/compliance/organizations`.
  </Accordion>

  <Accordion title="Are activities returned in order, and how do I detect when I have caught up to real time?">
    Activities are returned newest first, with ties in `created_at` broken by activity ID. To catch up, walk pages forward by `before_id` until `has_more` is `false`; that final response's `first_id` is your new cursor and you have reached the present. The full loop, including initial backfill and the safety conditions on cursor persistence, is in [Cursor-driven incremental reads](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns#cursor-driven-incremental-reads).
  </Accordion>

  <Accordion title="How do I get a sandbox to test the Compliance API?">
    To test only the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed), you do not need a Claude Enterprise organization: an organization admin can [enable the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#set-up-the-compliance-api) on an eligible standalone Claude Console test organization and query the feed with a new Admin API key. If the **Compliance API** section is not visible in that organization's Security settings, the organization is not eligible for self-service enablement.

    To test every endpoint, set up a Claude Enterprise sandbox organization linked to a Claude Console organization under the same parent. This lets the sandbox exercise both the Activity Feed (through an Admin API key) and the chat, file, project, and session endpoints (through a Compliance Access Key).

    1. **Provision the Claude Enterprise organization.** Contact your Anthropic representative to set up a Claude Enterprise sandbox organization. On an existing Claude Enterprise organization, the primary owner can [enable the Compliance API directly in claude.ai](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#set-up-the-compliance-api).
    2. **Create the Claude Console organization.** Create a Claude Console organization yourself at `platform.claude.com` using the same email address.
    3. **Link the two organizations.** Sign in as the primary owner of the Claude Enterprise organization, go to [claude.ai > Organization settings > Identity and access](https://claude.ai/admin-settings/identity), and use **Merge Organizations** to link the two under a shared parent.

    Once linked, follow [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access) to create keys and start querying. Test organizations use the same enablement process as production organizations.
  </Accordion>
</AccordionGroup>


---
title: Design your compliance integration
url: https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns
description: Choose between polling and cursor-driven Activity Feed consumption, correlate Compliance API events with your SIEM, and plan retention.
---

<Note>
  To enable the Compliance API, see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).
</Note>

<Check>
  **Required scope:** `read:compliance_activities` on the Compliance Access Key or Admin API key.
</Check>

A production Compliance API integration makes three design choices: how it consumes the Activity Feed, how its output correlates with your security information and event management (SIEM) system, and where long-term copies of activity and content live. These choices are independent of the endpoints themselves; this page helps you evaluate the tradeoffs.

This page assumes you have read the following pages:

* [Query the Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed), which defines the parameters and pagination contract referenced throughout.
* [Retrieve and delete chats, files, and projects](https://platform.claude.com/docs/en/manage-claude/compliance-content-data), which defines the chat, file, and project endpoints and the `deleted_at` semantics referenced in [Plan content retention](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns#plan-content-retention).
* [Retrieve session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions), which defines the local and remote session endpoints.


## Choose a feed-consumption pattern

Source: https://platform.claude.com/llms-full.txt#choose-a-feed-consumption-pattern

The Activity Feed supports two consumption patterns: periodic window polling bounded by `created_at.gte` and `created_at.lt`, and cursor-driven incremental reads that persist a cursor from one response and pass it on the next request. Both return identical `Activity` objects; the difference is the state your client persists between calls.

Both patterns share these constraints:

* Activities are queryable within 1 minute of occurring and retained for 6 years. Recording is not retroactive: it begins when the Compliance API is first enabled for your organization, and activity from before enablement is not backfilled.
* The maximum `limit` for each page is 5,000.
* Cursor values are opaque strings that you must not parse.
* Requests are limited to 600 per minute per [parent organization](https://platform.claude.com/docs/en/manage-claude/compliance-api#how-the-compliance-api-works), shared across every key, every linked organization, and every `/v1/compliance/*` endpoint; unlike the local session endpoints, the remote session endpoints carry a second request budget on top. See [429 Too Many Requests](https://platform.claude.com/docs/en/manage-claude/compliance-errors#429-too-many-requests) for the response headers and retry contract.

| Pattern                         | Choose when                                                                                                                                                                                                     |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Window polling                  | Your pipeline runs on a fixed schedule, you prefer stateless workers, and you can tolerate replaying or overlapping windows                                                                                     |
| Cursor-driven incremental reads | You want the lowest latency between an activity occurring and your pipeline ingesting it, you want to avoid re-reading pages you already drained, and you have a durable place to persist a cursor between runs |

### Window polling

Set `created_at.lt` at least 1 minute in the past so that every activity in the window is already queryable. Use `created_at.gte` for the lower bound and `created_at.lt` for the upper bound so that consecutive windows tile without gaps or overlap; reuse the previous window's `lt` value as the next window's `gte`.

```bash cURL
curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/activities" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --data-urlencode "created_at.gte=2026-04-20T07:00:00Z" \
  --data-urlencode "created_at.lt=2026-04-20T08:00:00Z" \
  --data-urlencode "limit=5000"

bash cURL
first_id="activity_01XyDMpzjS89pFZXqSFUBDr6"  # first_id from a previous response

curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/activities" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --data-urlencode "limit=5000" \
  --data-urlencode "before_id=$first_id"

text
cursor = stored_cursor
loop:
  page = GET /v1/compliance/activities?before_id={cursor}&limit=5000
  store(page.data)
  if page.first_id is not null:
    cursor = page.first_id
  if not page.has_more: break
persist(cursor)
```

Cursors survive key rotation; see [Manage and rotate keys](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#manage-and-rotate-keys).

<Warning>
  Each page is adjacent to the cursor you pass: the loop walks forward toward the present, one page at a time. Do not treat a single response as caught up while `has_more` is `true`. Persist the cursor only after `has_more` is `false`; the unfetched pages are the newer ones between this response's `first_id` and the present, and they stay unread until you finish the loop or run again.
</Warning>


## Correlate with your SIEM

Source: https://platform.claude.com/llms-full.txt#correlate-with-your-siem

Each `Activity` carries fields you can join against events already in your SIEM (Splunk, Datadog, Microsoft Sentinel, Cribl, or similar):

| Compliance API field  | Join target                                                             |
| --------------------- | ----------------------------------------------------------------------- |
| `actor.user_id`       | Your identity provider's stable user identifier                         |
| `actor.email_address` | Directory email when a stable ID is unavailable                         |
| `actor.ip_address`    | Network, VPN, and endpoint logs                                         |
| `actor.user_agent`    | Endpoint and device inventory, and the client app that made the request |
| `created_at`          | Time-window correlation across any source                               |

`actor.user_id` and `actor.email_address` are present when `actor.type` is `user_actor`. `actor.ip_address` and `actor.user_agent` are absent on some actor types, such as `anthropic_actor` and `scim_directory_sync_actor`. Check the discriminator before reading any of these fields. `user_id` is a stable, opaque identifier for the user account: it is consistent across every Compliance API endpoint and activity payload, and it does not change when the user's email or display name changes. Use `user_id`, not `email_address`, as the primary join key.

Calls to the Compliance API itself emit `compliance_api_accessed` activities. Ingest these alongside other activity types so your SIEM records who queried compliance data, and when. Pass `activity_types[]=compliance_api_accessed` to scope the query, then in your client, read `actor.api_key_id` from each activity whose `actor.type` is `api_actor` to attribute the access to a specific Compliance Access Key or Admin API key.


## Plan content retention

Source: https://platform.claude.com/llms-full.txt#plan-content-retention

Five retention horizons govern what you can retrieve later:

| Data                                                    | Retained for                                                                                             | Controlled by                                                        |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Activity Feed records                                   | 6 years                                                                                                  | Anthropic                                                            |
| Chat, file, and project content                         | Your organization's claude.ai retention policy, unless a user deletes it sooner                          | Your organization                                                    |
| Local session transcripts (sessions on users' machines) | 6 years by default, or your organization's custom conversation retention period when a finite one is set | Anthropic by default; your organization when it sets a custom period |
| Remote session transcripts (sessions in the cloud)      | 6 years, unless a user deletes the session sooner                                                        | Anthropic                                                            |
| Content hard-deleted through the Compliance API         | Not retained; deletion is immediate and permanent                                                        | The caller of the `DELETE` endpoint                                  |

To learn how the rest of the Claude Platform handles retention, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).

Decide between export-and-archive and on-demand API retrieval as follows:

* If your legal-hold or audit horizon exceeds 6 years for activity metadata or session transcripts, export Activity Feed pages and session transcripts to your own archive as you ingest them.
* If your content-retention policy is shorter than your eDiscovery horizon, export chat and file content before the retention window expires; the Compliance API cannot return content that retention has already removed. The same applies to local session transcripts, which follow your organization's custom conversation retention period when a finite one is set, even when that period is shorter than 6 years. The local session endpoints stop returning messages older than your organization's current period as soon as the setting changes, and lengthening the period later does not restore transcripts that have already expired, so export any transcript you must keep beyond it.
* If you must retain chat content or remote session transcripts after users delete them in claude.ai (for example, under a legal hold), export chat, file, artifact, and remote session content to your own archive as you ingest it; the Compliance API cannot return content that a user has already deleted.
* If a workflow might issue a Compliance API hard-delete (for example, DLP enforcement), retrieve and archive the target content first. There is no recovery window after a hard-delete.

In every other case, rely on direct API retrieval and avoid maintaining a parallel copy.

### Delivery guarantees and completeness

Treat the Activity Feed as **at-least-once**: a correctly paginated traversal returns every activity at least once, but a retry after a partial failure can re-deliver activities you already stored. Deduplicate on the activity `id` field.

The list endpoints do not return a `total_count` field or a checksum. To attest that an export run is complete, log:

* The starting cursor and the terminal `last_id`.
* The number of records exported.
* The run timestamp and the `request-id` of the final page.

Activity volume is not a completeness check. The `claude_*_viewed` activity types, such as `claude_chat_viewed`, follow each app's loading pattern (see [Understand the Activity object](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed#understand-the-activity-object)). A period with chat messages but no `claude_chat_viewed` activities does not on its own indicate missing data. Rely on the traversal and the overlap or reconciliation pass described in [Window polling](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns#window-polling) instead.

The content endpoints (chats, files, projects, project attachments, and local and remote session transcripts) serve Claude Enterprise data only. The Activity Feed surfaces administrative and resource events organization-wide. The Compliance API does not include:

* Prompt text or model responses from Claude Console, or from Claude API workloads authenticated with an API key.
* On-device activity in local sessions that is never sent to Anthropic, such as local files that Claude did not read.
* Claude Code usage authenticated with a Claude Console API key, run through a third-party cloud platform (Amazon Bedrock, Google Cloud, or Microsoft Foundry), or run in Claude Code on the web.
* Local sessions from organizations with [HIPAA readiness](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#hipaa-readiness) enabled, and local sessions for which [zero data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#zero-data-retention-zdr-scope) is in effect.
* Thinking blocks, and images or other binary content, inside session transcripts (transcripts carry user prompts, assistant responses, and tool activity only; local session transcripts show a placeholder `text` block where binary content was omitted).
* The original file for a chat attachment that claude.ai stored as extracted text, such as some Word, PowerPoint, and PDF uploads (the file content endpoint returns the extracted text; see [Retrieve files and artifacts](https://platform.claude.com/docs/en/manage-claude/compliance-content-data#retrieve-files-and-artifacts)).
* The system prompt of local sessions (a marker message stands in for it).
* Tool definitions and MCP server configuration in session transcripts (local or remote), and citation metadata on `text` blocks in local session transcripts.
* Local session transcript content in an organization whose [customer-managed encryption key](https://platform.claude.com/docs/en/manage-claude/cmek) cannot currently be used. Those requests return [503 Service Unavailable](https://platform.claude.com/docs/en/manage-claude/compliance-errors#local-sessions-temporarily-unavailable), and session metadata is still listed.
* Content removed by your organization's retention policy.
* Content of chats that users delete in claude.ai (the chats are still listed, with `deleted_at` populated).
* Remote sessions that users delete (deleted sessions are no longer listed, and the messages endpoint returns 404 for them).
* Content hard-deleted through the Compliance API.

See the [Compliance API FAQ](https://platform.claude.com/docs/en/manage-claude/compliance-faq#data-coverage-and-retention) for more on what the Compliance API does and does not capture.

For chain of custody, store the exported records with provenance metadata: source endpoint, query parameters, run timestamp, and a content hash of each record.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-92

<CardGroup cols={2}>
  <Card title="Query the Activity Feed" href="https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed">
    Filter parameters, pagination, and the `Activity` object schema.
  </Card>

  <Card title="Retrieve and delete chats, files, and projects" href="https://platform.claude.com/docs/en/manage-claude/compliance-content-data">
    The chat, file, and project endpoints, including hard delete.
  </Card>

  <Card title="Retrieve session transcripts" href="https://platform.claude.com/docs/en/manage-claude/compliance-sessions">
    List the sessions your users run in Claude apps and agents, such as Cowork and Claude Code, and retrieve their transcripts.
  </Card>
</CardGroup>


---
title: Handle Compliance API errors
url: https://platform.claude.com/docs/en/manage-claude/compliance-errors
description: Every Compliance API error message with cause and fix, organized by HTTP status code.
---

<Note>
  To enable the Compliance API, see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).
</Note>

This page lists the response messages each documented Compliance API endpoint returns, the cause, and the fix.

The Compliance API returns errors in the standard [Anthropic error format](https://platform.claude.com/docs/en/api/errors): a non-2xx status code, a `request-id` response header, and a JSON body with an `error` object containing `type` and `message`. Include the `request-id` header value when you escalate to support.

On this page, local sessions run on users' machines and remote sessions run in the cloud; see [Retrieve session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions).

Match on `error.type`, not on the message string. Messages are stable enough to copy into runbooks but might be reworded over time; the type values are part of the API contract. The local session endpoints have a few documented exceptions where responses that share a type are told apart by their message; each is called out where it applies.

The following table tells you at a glance whether to retry. Each section that follows shows the verbatim error body and the fix.

| Status                                                                                                                     | Retry?                      | When                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| -------------------------------------------------------------------------------------------------------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [400 Bad Request](https://platform.claude.com/docs/en/manage-claude/compliance-errors#400-bad-request)                     | No                          | Fix the request and resend.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| [401 Unauthorized](https://platform.claude.com/docs/en/manage-claude/compliance-errors#401-unauthorized)                   | No                          | Fix or rotate the key, then resend.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| [403 Forbidden](https://platform.claude.com/docs/en/manage-claude/compliance-errors#403-forbidden)                         | No                          | Add the missing scope or use the right key type, then resend.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| [404 Not Found](https://platform.claude.com/docs/en/manage-claude/compliance-errors#404-not-found)                         | Usually no                  | The resource was deleted or never existed; remove it from your queue. Exceptions: on the local session endpoints, the message `Local sessions are not available.` (returned on every call, including the list) means the endpoints are currently unavailable to your parent organization, not that a session is gone; keep your queued IDs and see [Local session not found](https://platform.claude.com/docs/en/manage-claude/compliance-errors#local-session-not-found). A remote session still in `pending` status 404s on its messages endpoint until it starts; see [Remote session not found](https://platform.claude.com/docs/en/manage-claude/compliance-errors#remote-session-not-found). |
| [409 Conflict](https://platform.claude.com/docs/en/manage-claude/compliance-errors#409-conflict)                           | No                          | The request conflicts with the resource's current state; resolve the conflict (such as detaching child resources), then retry.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| [429 Too Many Requests](https://platform.claude.com/docs/en/manage-claude/compliance-errors#429-too-many-requests)         | Yes, after `retry-after`    | Wait the seconds in `retry-after`, then retry; do not advance your cursor.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| [500 Internal Server Error](https://platform.claude.com/docs/en/manage-claude/compliance-errors#500-internal-server-error) | Depends on `x-should-retry` | Check the `x-should-retry` response header before retrying.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| [502, 503, 504, 529](https://platform.claude.com/docs/en/manage-claude/compliance-errors#500-internal-server-error)        | Yes, with backoff           | Transient; retry with exponential backoff. Exception: some local session 503s are not transient. See [Local sessions temporarily unavailable](https://platform.claude.com/docs/en/manage-claude/compliance-errors#local-sessions-temporarily-unavailable).                                                                                                                                                                                                                                                                                                                                                                                                                                         |


## 400 Bad Request

Source: https://platform.claude.com/llms-full.txt#400-bad-request

The request was syntactically valid but contained a parameter the server rejected. Fix the parameter and retry.

### Invalid timestamp format

**Type:** `invalid_request_error`

```text wrap
The `created_at.gte` parameter contains an invalid timestamp format. Timestamps must be provided in RFC 3339 format e.g., "2024-03-01T00:00:00Z". Got "2024-01-01".

text wrap
created_at.lt must be strictly after created_at.gte.

text wrap
The limit parameter must be between 1 and 1000, inclusive. Got 1500.

text wrap
Invalid `after_id`. No activity found for `after_id` "activity_invalid123"

text wrap
The page parameter is not a valid cursor for this request.

text wrap
The page cursor has expired. Restart the walk without a page parameter; results will reflect the current retention boundary.
```

For the first body, resend the unmodified `next_page` value from the previous response to the endpoint and session that issued it. For an expired cursor, restart without a `page` parameter; the new walk reflects the retention boundary in effect when it starts, so messages that aged out of the retention period in the meantime are no longer returned (see [Retrieve a local session transcript](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-a-local-session-transcript)).


## 401 Unauthorized

Source: https://platform.claude.com/llms-full.txt#401-unauthorized

The `x-api-key` header was missing or did not match a known key. A valid key with the wrong scopes returns [403 Forbidden](https://platform.claude.com/docs/en/manage-claude/compliance-errors#403-forbidden) instead.

### Invalid API key

**Type:** `authentication_error`

```text wrap
The API key provided is invalid or has been revoked.
```

**Cause:** The key in `x-api-key` does not exist, has been deleted, or has been disabled. A missing or empty `x-api-key` header returns the same body, so check both your secret store and the key's revocation status.

**Fix:** Confirm the key value, check that it has not been deleted in claude.ai (Compliance Access Keys) or Claude Console (Admin API keys), and confirm it is enabled. See [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).


## 403 Forbidden

Source: https://platform.claude.com/llms-full.txt#403-forbidden

The key in `x-api-key` is valid but does not carry the scope the endpoint requires. The verbatim message lists the scopes the key carries (`Got:`) and the scopes the endpoint requires (`Needed:`), so you can confirm what the key carries without rechecking Claude Console or claude.ai. Compliance Access Key scopes are immutable after creation, so each insufficient-scope fix directs you to create a new key rather than edit the existing one. A standalone Claude Console organization (one with no parent organization) cannot create a Compliance Access Key, so fixes that require one do not apply to it; it can query the Activity Feed only.

### Insufficient scope: Activity Feed

**Type:** `permission_error`

```text wrap
Missing required scopes. Got: ['read:compliance_user_data'] Needed: ['read:compliance_activities']

text wrap
Missing required scopes. Got: ['read:compliance_user_data'] Needed: ['read:compliance_org_data']

text wrap
Missing required scopes. Got: ['read:compliance_org_settings'] Needed: ['read:compliance_org_data']

text wrap
Missing required scopes. Got: ['read:compliance_activities'] Needed: ['read:compliance_user_data']

text wrap
Missing required scopes. Got: ['read:compliance_user_data'] Needed: ['delete:compliance_user_data']
```

**Cause:** A Compliance Access Key without `delete:compliance_user_data` was used to call a `DELETE` endpoint on chats, files, or projects.

**Fix:** [Create a new Compliance Access Key](https://platform.claude.com/docs/en/manage-claude/compliance-api-access#set-up-the-compliance-api) with `delete:compliance_user_data` selected. The delete scope is separate from `read:compliance_user_data` so that read-only audit keys cannot delete content.


## 404 Not Found

Source: https://platform.claude.com/llms-full.txt#404-not-found

The endpoint resolved but the resource ID does not exist or has already been deleted. Compliance API deletes are immediate and permanent, so a 404 on a previously known ID usually means the content was hard-deleted through a Compliance API delete call or removed by a retention policy. The session endpoints add two cases. On the local session endpoints, a separate 404 message, `Local sessions are not available.`, is returned on every call (including the list) while the endpoints are unavailable to your parent organization; it does not depend on the session ID and can be temporary. See [Local session not found](https://platform.claude.com/docs/en/manage-claude/compliance-errors#local-session-not-found). On the remote session endpoints, a session that is still being provisioned (`status` of `pending`) has no transcript yet, so its messages endpoint 404s until the session starts. See [Remote session not found](https://platform.claude.com/docs/en/manage-claude/compliance-errors#remote-session-not-found). The activity-type strings cited in each Fix (for example, `claude_chat_created`) are values you can pass to the Activity Feed `activity_types[]` filter; see [Query compliance activities](https://platform.claude.com/docs/en/api/compliance/activities/list) for every supported value.

### Chat not found

**Type:** `not_found_error`

```text wrap
Chat claude_chat_01H5CWunD7RpVJ5bHa8RCkja not found.

text wrap
No file found with provided id, or it has already been deleted.

text wrap
No project is found with the provided id.

text wrap
No project document found with provided id, or it has already been deleted.

text wrap
Local session not found.

text wrap
Remote session not found.

text wrap
The "ce86b5f3-7c16-48b3-a9f3-e1d2c4b8a0f1" organization does not exist or the requester is not authorized to access it.

text wrap
organization `91012d09-e48b-438e-a489-1bebfd8fa6f9` not found in this organization's hierarchy
```

**Cause:** `GET /v1/compliance/organizations/{organization_id}/settings` returns this 404 in three cases that intentionally share the same body so the response does not reveal whether an organization exists: the `organization_id` is not one of your parent's linked organizations, the value is not a valid UUID, or the settings endpoint is not yet enabled for your parent organization.

**Fix:** Verify the ID against [List organizations](https://platform.claude.com/docs/en/api/compliance/organizations/list). If a known-good organization ID still returns 404, the settings endpoint is not yet enabled for your parent organization; contact your Anthropic representative.


## 409 Conflict

Source: https://platform.claude.com/llms-full.txt#409-conflict

The request is well-formed and authorized but conflicts with the resource's current state.

### Project has attached chats

**Type:** `conflict_error`

```text wrap
The "claude_proj_01KGp4eZNug9ri4kE35RSppq" project cannot be deleted as it has chats attached to it. Delete or detach all chats, and try deleting the project again.
```

**Cause:** `DELETE /v1/compliance/apps/projects/{project_id}` was called on a project that still has chats attached.

**Fix:** List the project's chats with `GET /v1/compliance/apps/chats?user_ids[]={user_id}&project_ids[]={project_id}` (the `project_ids[]` filter requires at least one `user_ids[]` value; enumerate IDs through [List organization users](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#list-organization-users)), delete each one with `DELETE /v1/compliance/apps/chats/{claude_chat_id}`, and then retry the project delete.


## 429 Too Many Requests

Source: https://platform.claude.com/llms-full.txt#429-too-many-requests

Requests to the Compliance API are limited to **600 requests per minute per [parent organization](https://platform.claude.com/docs/en/manage-claude/compliance-api#how-the-compliance-api-works)**. The limit is one budget shared across every key under the parent (Compliance Access Keys and the Admin API keys of all linked organizations) and across every `/v1/compliance/*` endpoint; the remote session endpoints carry a second request budget on top. For a standalone Claude Console organization, which has no parent organization, the same budget applies to the organization itself and is shared across its Admin API keys. Contact your Anthropic representative if your integration needs a higher limit.

Once your API key authenticates, Compliance API responses report the shared budget through the standard [rate-limit response headers](https://platform.claude.com/docs/en/api/rate-limits#response-headers) so your client can throttle proactively instead of waiting for a 429:

* `anthropic-ratelimit-requests-limit` is the per-minute request budget.
* `anthropic-ratelimit-requests-remaining` is the budget left in the current window.
* `anthropic-ratelimit-requests-reset` is the RFC 3339 timestamp when the window resets and the full budget is restored.

A 429 response also carries a `retry-after` header with the number of seconds to wait before sending the next request. This value might include a small safety margin beyond `anthropic-ratelimit-requests-reset`; honor `retry-after`.

**Cause:** Your parent organization (or standalone Claude Console organization) sent more than 600 requests to `/v1/compliance/*` in a 1-minute window, across all of the keys that share its budget, or it exhausted the remote session endpoints' second request budget (described later in this section).

**Fix:** Wait the number of seconds in the `retry-after` header, then retry. If the header is absent (for example, stripped by an intermediary), fall back to exponential backoff (start at 1 second, double up to 60 seconds). Do not advance your pagination cursor on a 429: the failed request returned no data, so the cursor from the last successful page is still correct.

Requests that fail authentication (a missing or unrecognized key, or a Claude API key rather than a Compliance Access Key or Admin API key) are rejected before the rate limiter and do not consume quota. A valid key that lacks the endpoint's required scope consumes one quota unit before the 403 is returned.

The [local session endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions) count only against the shared limit. The [remote session endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-remote-sessions) also carry a second request budget, keyed to your parent organization like the shared limit, on top of it. A 429 from that budget carries a `retry-after` header that is always `1` (a minimum wait, not the actual reset time); any `anthropic-ratelimit-*` headers on that response describe the shared limit rather than this budget, so back off exponentially if the 429 repeats.

If you poll the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) on a schedule, budget your aggregate request rate (across all keys, linked organizations, and concurrent workers) below the shared limit. Watch `anthropic-ratelimit-requests-remaining` to slow down before you reach it. See [Design your compliance integration](https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns#choose-a-feed-consumption-pattern) for choosing between window-polling and cursor-driven ingestion.


## 500 Internal Server Error

Source: https://platform.claude.com/llms-full.txt#500-internal-server-error

A 500 from the Compliance API carries an `x-should-retry: false` response header when the failure is deterministic. Anthropic SDKs honor this header automatically. If you use a generic HTTP retry library that retries on every 5xx, suppress retries when `x-should-retry` is `false`; retrying this error fails identically on every attempt.

A 500 without the `x-should-retry: false` header is transient: retry with exponential backoff (start at 1 second, double up to 60 seconds). The same applies to 502, 503, 504, and 529 responses. The exception is a small set of local session 503s, described next, that depend on an organization's settings or encryption key rather than on load. See [Errors](https://platform.claude.com/docs/en/api/errors) for the platform-wide retry semantics.

### Local sessions temporarily unavailable

**Type:** `overloaded_error`

```text wrap
The local-sessions index is temporarily unavailable. Try again shortly.

text wrap
Captured content is temporarily unavailable. Try again shortly.

text wrap
The local-sessions index cannot currently evaluate retention overrides for this page. Try again later.
```

**Cause:** The [local session endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions) return 503 with one of these bodies. All three share the `overloaded_error` type, so this is one of the few errors on this page where you need the message text, not `error.type`, to tell the conditions apart:

* The `index is temporarily unavailable` body means session listings are briefly unavailable because of load or a backend condition. This is transient.
* The `Captured content` body means a session's transcript content cannot be returned right now. This is usually transient too. In organizations that use [customer-managed encryption keys](https://platform.claude.com/docs/en/manage-claude/cmek), the messages endpoint also returns this body for every page that contains content your customer-managed key cannot decrypt, for example because you disabled, revoked, or destroyed the key, or because the key cannot be reached. In that case the error persists for as long as the key cannot be used. The message text is the same either way, so the only signal that the key is the cause is that the error keeps recurring for that organization. An unusable key is never reported as `not_captured`.
* The `retention overrides` body means a retention or data-handling setting that applies to one or more sessions in the requested range could not be evaluated yet. On the retrieve and messages endpoints it reads `for this session` instead of `for this page`. It depends on the data and settings of the organization that ran the session rather than on load, and it can persist for an extended period.

**Fix:** Handle each body as follows:

* For the two `Try again shortly.` bodies, retry with exponential backoff and do not advance your `page` cursor, because the failed request returned no data.
* If the `Captured content` body keeps recurring on the messages endpoint for an organization that uses a customer-managed key, treat it as persistent: stop walking that organization's transcripts and check the key's status in your key management service. Transcripts in other linked organizations, and session metadata everywhere, are unaffected. If you retry on a later run, restart each session's walk without `page`, because messages page cursors expire 24 hours after the walk's first page.
* For the `Try again later.` body, do not hold a walk open waiting for it to clear. On the list endpoint, either retry later by restarting without the `page` parameter (a list page token older than 24 hours is still accepted but is re-evaluated against the current retention boundary, so a parked walk can skip sessions), or narrow the `created_at.gte` and `created_at.lt` window until the request succeeds and export the skipped range separately on a later run. On the retrieve and messages endpoints, skip that session ID, continue with the rest of your export, and retry the session on a later run. Messages page cursors expire 24 hours after the walk's first page, so restart that session's walk without `page` when you return to it.

If any of these conditions recurs across runs, contact your Anthropic representative and include the `request-id` response header. For the customer-managed key case, do this only if the error continues while that key is usable.

For service-wide incidents, check [status.anthropic.com](https://status.anthropic.com).


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-93

<CardGroup cols={2}>
  <Card title="Compliance API FAQ" href="https://platform.claude.com/docs/en/manage-claude/compliance-faq">
    Common questions about access, scopes, retention, and integration.
  </Card>

  <Card title="Errors" href="https://platform.claude.com/docs/en/api/errors">
    The platform-wide error catalog and retry semantics.
  </Card>
</CardGroup>


---
title: List organizations, users, roles, groups, and settings
url: https://platform.claude.com/docs/en/manage-claude/compliance-org-data
description: Enumerate organizations under your parent organization (their users, roles, and groups) and read each organization's effective settings through the Compliance API.
---

<Note>
  To enable the Compliance API, see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).
</Note>

<Check>
  **Required scope:** `read:compliance_org_data` on the Compliance Access Key. The user and group-member endpoints require `read:compliance_user_data` instead.

  Compliance Access Keys (`sk-ant-api01-...`) created in claude.ai are the only key type accepted; see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access) to provision one. Calls authenticated with an Admin API key (`sk-ant-admin01-...`) return [403 Forbidden](https://platform.claude.com/docs/en/manage-claude/compliance-errors#403-forbidden).
</Check>

The endpoints on this page expose the directory side of a Claude Enterprise organization: its linked organizations, the users in each one, the roles defined on each, and its role-based access control (RBAC) or SCIM (System for Cross-domain Identity Management)-provisioned groups and their members. Use them to seed eDiscovery user lists, build reporting dashboards, and reconcile group membership against an external system of record. A Compliance Access Key that covers the parent organization returns data from every linked organization underneath, so a single key reaches the entire tree. The [effective-settings endpoint](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#get-effective-organization-settings) complements the directory: it returns the data-privacy, security, and capability settings actually in force for one organization.


## List organizations

Source: https://platform.claude.com/llms-full.txt#list-organizations

The [List organizations](https://platform.claude.com/docs/en/api/compliance/organizations/list) endpoint returns every organization under the parent the key is bound to.

The following call lists every organization under your parent. The response is a `data` array of organization records sorted by `created_at` ascending, plus `has_more` and `next_page` for pagination. When `has_more` is `true`, pass the returned `next_page` token back unchanged as the `page` query parameter on your next request. See [List organizations](https://platform.claude.com/docs/en/api/compliance/organizations/list) in the API reference for the `limit` and `page` parameter defaults and ranges.

```bash cURL
curl --fail-with-body -sS \
  "https://api.anthropic.com/v1/compliance/organizations" \
  -H "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  -H "anthropic-version: 2023-06-01"

json Response
{
  "data": [
    {
      "uuid": "91012d09-e48b-438e-a489-1bebfd8fa6f9",
      "name": "Acme Engineering",
      "created_at": "2025-06-01T10:00:00Z"
    },
    {
      "uuid": "5a1b2c3d-4e5f-6789-abcd-ef0123456789",
      "name": "Acme Legal",
      "created_at": "2025-07-15T14:30:00Z"
    }
  ],
  "has_more": false,
  "next_page": null
}
```

The `uuid` field is the canonical identifier for downstream lookups. The following table maps it to the other organization identifiers across the Compliance API:

| Field                | Where                                                                                                                                                                                                                                                                                                                                                                                                                                    | Relationship to `uuid`                                                                                                                                    |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `{org_uuid}`         | Path parameter on per-organization endpoints on this page                                                                                                                                                                                                                                                                                                                                                                                | Same value                                                                                                                                                |
| `organization_uuid`  | Activity Feed, chat, project, and session records                                                                                                                                                                                                                                                                                                                                                                                        | Same value; join on these two fields directly                                                                                                             |
| `organization_id`    | Activity Feed, chat, and project records                                                                                                                                                                                                                                                                                                                                                                                                 | Same organization, `org_`-prefixed. Deprecated on chat and project records; use `organization_uuid` instead.                                              |
| `organization_ids[]` | Filter on [Query the Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed), [Retrieve chats and messages](https://platform.claude.com/docs/en/manage-claude/compliance-content-data#retrieve-chats-and-messages), and the [remote session list](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-remote-sessions) (the local session list has no organization filter) | Accepts `uuid` or the `org_`-prefixed form                                                                                                                |
| `organization_id`    | [Effective organization settings](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#get-effective-organization-settings) response                                                                                                                                                                                                                                                                                    | Same value, bare UUID; this response does **not** use the `org_`-prefixed form that `organization_id` carries on Activity Feed, chat, and project records |

Most other Anthropic APIs use the `org_`-prefixed form.

To track organization-membership changes over time, relist this endpoint periodically, following the `next_page` token through every page on each pass. The Activity Feed also surfaces membership events through the `org_deletion_requested`, `org_deleted_via_bulk`, `org_parent_join_proposal_created`, and `org_join_proposal_decided` activity types; see [Query the Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed).


## List organization users

Source: https://platform.claude.com/llms-full.txt#list-organization-users

The [List organization users](https://platform.claude.com/docs/en/api/compliance/organizations/users/list) endpoint returns a paginated list of user records for one organization.

This endpoint requires `read:compliance_user_data`, not `read:compliance_org_data`. Create the Compliance Access Key with both scopes when you intend to use it for directory enumeration; otherwise the call returns [403 Forbidden](https://platform.claude.com/docs/en/manage-claude/compliance-errors#403-forbidden).

See [List organization users](https://platform.claude.com/docs/en/api/compliance/organizations/users/list) in the API reference for the `limit` and `page` query parameter defaults and ranges.

Results are sorted by organization join date ascending. Unlike the Activity Feed's `before_id`/`after_id` cursors (see [Paginate results](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed#paginate-results)), the directory endpoints paginate with a `next_page` token: when `has_more` is `true`, pass `next_page` back unchanged as the `page` query parameter on the next request.

```bash cURL
org_uuid="91012d09-e48b-438e-a489-1bebfd8fa6f9"

curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/organizations/$org_uuid/users" \
  -H "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  -H "anthropic-version: 2023-06-01" \
  --data-urlencode "limit=500"

json Response
{
  "data": [
    {
      "id": "user_01XyDMpzjS89pFZXqSFUBDr6",
      "full_name": "Priya Sharma",
      "email": "priya@example.com",
      "organization_role": "admin",
      "created_at": "2025-06-01T10:00:00Z"
    }
  ],
  "has_more": true,
  "next_page": "page_8aW5kZXgicG9zaXRpb25fdG9rZW5fOTE0"
}
```

The user IDs returned here are the same `user_...` identifiers accepted by the [Query the Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed) `actor_ids[]` filter and the `user_ids[]` filters on [Retrieve chats and messages](https://platform.claude.com/docs/en/manage-claude/compliance-content-data#retrieve-chats-and-messages) and the [remote session list](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-remote-sessions); the [local session list](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions) has no user filter, so attribute local sessions by the `user.id` on each session object. The `organization_role` field carries the user's built-in membership level within the listed organization (one of `admin`, `billing`, `claude_code_user`, `developer`, `managed`, `membership_admin`, `owner`, `primary_owner`, or `user`), an axis independent of any custom RBAC role assignments returned by [List roles](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#list-roles). A typical eDiscovery flow lists users for one or more organizations, filters against your own external records, and feeds the resulting IDs into chat and project queries.

A user only appears here while they are an active member of the organization. Removed users are dropped from the list immediately. Their historical activity remains queryable through the Activity Feed for the full retention window, indexed by the same `user_...` ID.


## List roles

Source: https://platform.claude.com/llms-full.txt#list-roles

The [List Compliance Roles](https://platform.claude.com/docs/en/api/compliance/organizations/roles/list) endpoint returns a paginated list of role records defined on one organization, and [Get Compliance Role](https://platform.claude.com/docs/en/api/compliance/organizations/roles/retrieve) returns one role by ID.

Both role endpoints require `read:compliance_org_data`. The list endpoint accepts the same `limit` and `page` parameters as the [organization users endpoint](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#list-organization-users).

```bash cURL
org_uuid="91012d09-e48b-438e-a489-1bebfd8fa6f9"

curl --fail-with-body -sS \
  "https://api.anthropic.com/v1/compliance/organizations/${org_uuid}/roles" \
  -H "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  -H "anthropic-version: 2023-06-01"

json Response
{
  "data": [
    {
      "id": "rbac_role_01N2pQrS8tUvWxYz5AbCdEfGh",
      "name": "Compliance Reviewer",
      "description": "Read-only access to chat and project content for legal review.",
      "created_at": "2025-06-01T10:00:00Z",
      "updated_at": "2025-06-15T14:30:00Z"
    }
  ],
  "has_more": false,
  "next_page": null
}
```

See the [List Compliance Roles](https://platform.claude.com/docs/en/api/compliance/organizations/roles/list) response schema for the full role record shape. To list the permissions currently granted to a role, use [List Compliance Role Permissions](https://platform.claude.com/docs/en/api/compliance/organizations/roles/permissions/list). To audit historical role assignments and permission changes, query the RBAC activity types (for example, `rbac_role_assigned` and `rbac_role_permission_added`) through the Activity Feed; see [Filter activities](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed#filter-activities).


## List groups and members

Source: https://platform.claude.com/llms-full.txt#list-groups-and-members

The [List Compliance Groups](https://platform.claude.com/docs/en/api/compliance/groups/list) endpoint returns a paginated list of RBAC and SCIM-provisioned groups, and [Get Compliance Group](https://platform.claude.com/docs/en/api/compliance/groups/retrieve) returns one group by ID. The [List Compliance Group Members](https://platform.claude.com/docs/en/api/compliance/groups/members/list) endpoint returns the members of one group.

The group list and retrieval endpoints require `read:compliance_org_data`. The members endpoint requires `read:compliance_user_data`. Create the key with both scopes to walk groups end to end. Both list endpoints accept the same `limit` and `page` parameters as the [organization users endpoint](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#list-organization-users).

See the [List Compliance Groups](https://platform.claude.com/docs/en/api/compliance/groups/list) response schema for the full group record shape. The `roles` array lists role IDs assigned to the group, matching IDs from [List roles](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#list-roles). `source_type` is the discriminator between groups created manually through claude.ai (`direct`) and groups synced from an external identity provider through SCIM (`scim`).

List groups, then for each group list its members:

```bash cURL
curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/groups" \
  -H "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  -H "anthropic-version: 2023-06-01"

json Response
{
  "data": [
    {
      "id": "rbac_group_01P9qRsTuVwXyZa2BcDeFgHjK",
      "name": "Engineering",
      "description": "Engineering team members",
      "source_type": "scim",
      "roles": ["rbac_role_01N2pQrS8tUvWxYz5AbCdEfGh"],
      "created_at": "2025-06-01T10:00:00Z",
      "updated_at": "2025-06-15T14:30:00Z"
    }
  ],
  "has_more": false,
  "next_page": null
}

bash cURL
group_id="rbac_group_01P9qRsTuVwXyZa2BcDeFgHjK"

curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/groups/$group_id/members" \
  -H "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  -H "anthropic-version: 2023-06-01"

json Response
{
  "data": [
    {
      "user_id": "user_01XyDMpzjS89pFZXqSFUBDr6",
      "email": "priya@example.com",
      "created_at": "2025-06-01T10:00:00Z",
      "updated_at": "2025-06-15T14:30:00Z"
    }
  ],
  "has_more": false,
  "next_page": null
}
```

See the [List Compliance Group Members](https://platform.claude.com/docs/en/api/compliance/groups/members/list) response schema for the full member record shape. The `user_id` field is the same `user_...` identifier that the Activity Feed, chat list, and remote session list accept; it also matches `user.id` on local session objects and on user-owned remote session objects (agent-owned remote sessions carry the human's ID in `started_by_user.id` instead). To get a member's full name, look it up through the organization users list.


## Get effective organization settings

Source: https://platform.claude.com/llms-full.txt#get-effective-organization-settings

The [Get effective organization settings](https://platform.claude.com/docs/en/api/compliance/organizations/settings/retrieve) endpoint returns the settings in force for one organization under your parent: the enforced state after regulatory restrictions (such as HIPAA), feature-availability rules, organization-type defaults, and inter-feature dependencies are applied, which can differ from what an administrator configured. Use it to attest that retention windows, content redaction, single sign-on enforcement, the IP allowlist, and session-duration controls match your documented baseline, without administrator Console access.

This endpoint requires `read:compliance_org_data`; a key without that scope returns [403 Forbidden](https://platform.claude.com/docs/en/manage-claude/compliance-errors#403-forbidden). The target must be one of the parent's linked organizations: the parent organization itself is not a valid target. An unknown organization, an organization ID that is not a valid UUID, an organization outside your parent's tree, and a parent organization that does not yet have access to this endpoint all return the same [404 Not Found](https://platform.claude.com/docs/en/manage-claude/compliance-errors#404-not-found), so a 404 does not reveal whether an organization exists. The settings endpoint is enabled per parent organization separately from the rest of the Compliance API; if every request returns 404, contact your Anthropic representative.

<Note>
  Before June 30, 2026, this endpoint required the separate `read:compliance_org_settings` scope. That scope has been retired: it can no longer be selected or granted when creating a key, and a key that carries only the retired scope returns [403 Forbidden](https://platform.claude.com/docs/en/manage-claude/compliance-errors#403-forbidden). Create a new Compliance Access Key with `read:compliance_org_data` instead.
</Note>

```bash cURL
org_uuid="91012d09-e48b-438e-a489-1bebfd8fa6f9"

curl --fail-with-body -sS \
  "https://api.anthropic.com/v1/compliance/organizations/$org_uuid/settings" \
  -H "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  -H "anthropic-version: 2023-06-01"

json Response
{
  "type": "effective_organization_settings",
  "organization_id": "91012d09-e48b-438e-a489-1bebfd8fa6f9",
  "settings": [
    {
      "name": "data_retention_periods",
      "type": "data_retention",
      "value": {
        "chat": {
          "type": "fixed",
          "timescale": "day",
          "duration": 90
        }
      }
    },
    {
      "name": "content_redaction_enabled",
      "type": "boolean",
      "value": true
    },
    {
      "name": "ip_allowlist_ip_ranges",
      "type": "string_list",
      "value": ["10.0.0.0/8", "203.0.113.0/24"]
    }
  ],
  "api_keys": [
    {
      "type": "compliance_api_key",
      "id": "apikey_01Hx7k2mP9nQ4rS6tU8vW0xY",
      "name": "Compliance Export Key",
      "scopes": ["read:compliance_activities", "read:compliance_org_data"],
      "is_active": true,
      "created_at": "2026-03-14T09:30:00Z",
      "created_by_id": "user_01Jz3a4bC5dE6fG7hI8jK9lM",
      "expires_at": null
    }
  ]
}
```

Each row carries `name`, `type`, and `value`; the `type` field (`boolean`, `integer`, `string_list`, `provisioning_mode`, or `data_retention`) tells you the shape of `value`. The full list of setting names, and the `value` schema for each type, is in [Get effective organization settings](https://platform.claude.com/docs/en/api/compliance/organizations/settings/retrieve) in the API reference.

The `api_keys` array lists every Compliance Access Key configured for your parent organization, so the same list is returned regardless of which linked organization you query. Each entry carries the key's `type` (`compliance_api_key`), `id`, `name`, `scopes`, `is_active` flag, `created_at` and `expires_at` timestamps, and `created_by_id` (the ID of the user who created the key; may be `null`). The key's secret value is never returned. Deactivated keys are included with `is_active: false` so you can review keys that previously had access, and keys that carry only the retired `read:compliance_org_settings` scope remain in the list for audit and cleanup visibility even though that scope no longer grants access.

The top-level `organization_id` is the organization's bare UUID: the same value as `uuid` in the organizations list, not the `org_`-prefixed form that `organization_id` carries on Activity Feed, chat, and project records (see the [organization identifier table](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#list-organizations)).

Rows reflect the enforced state rather than the last-stored configuration: for example, `sso_provisioning_mode` reports a configured SCIM mode only while directory sync is enabled, `ip_allowlist_enabled` is `true` only while the allowlist is on and has at least one active range, and `code_execution_network_egress_enabled` is `false` whenever code execution is off.

The response reflects the state at read time; nothing is snapshotted. Changes to most of these settings surface as events in the [Activity Feed](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed); use this endpoint for the current resolved state and the feed to audit who changed what, and when.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-94

<CardGroup cols={2}>
  <Card title="Compliance organizations API reference" href="https://platform.claude.com/docs/en/api/compliance/organizations">
    The full request and response schema for every organization, user, role, group, and settings endpoint.
  </Card>

  <Card title="Handle Compliance API errors" href="https://platform.claude.com/docs/en/manage-claude/compliance-errors">
    Verbatim error payloads and the fix for each.
  </Card>
</CardGroup>


---
title: Query the Activity Feed
url: https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed
description: Retrieve, filter, and paginate your organization's Compliance API Activity Feed.
---

<Note>
  To enable the Compliance API, see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).
</Note>

<Check>
  **Required scope:** `read:compliance_activities` on the Compliance Access Key or Admin API key.

  Both Compliance Access Keys (`sk-ant-api01-...`) carrying this scope and Admin API keys (`sk-ant-admin01-...`) can call the Activity Feed. See [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access) for the conditions under which each key type carries the scope.
</Check>

The Activity Feed records authentication, chat, file, project, administrative, and platform activity across your organization and returns it in reverse chronological order. Activities are queryable within 1 minute of occurring and are retained for 6 years. Recording is not retroactive: it begins when the Compliance API is first enabled for your organization, and activity from before enablement is not backfilled.

```bash cURL
curl --fail-with-body -sS \
  "https://api.anthropic.com/v1/compliance/activities?limit=1" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01"

json Response
{
  "data": [
    {
      "id": "activity_01XyDMpzjS89pFZXqSFUBDr6",
      "created_at": "2026-04-10T08:09:10Z",
      "organization_id": "org_01Wv6QeBcDfGhJkLmNpQrSt8",
      "organization_uuid": "abcdef01-2345-6789-abcd-ef0123456789",
      "actor": {
        "type": "user_actor",
        "email_address": "user@example.com",
        "user_id": "user_01TuVwXyZaBcDeFgH2JkLmN4",
        "ip_address": "192.0.2.34",
        "user_agent": "Mozilla/5.0..."
      },
      "type": "claude_chat_created",
      "claude_chat_id": "claude_chat_01XyDMpzjS89pFZXqSFUBDr6",
      "claude_project_id": "claude_proj_01KGp4eZNug9ri4kE35RSppq"
    }
  ],
  "has_more": true,
  "first_id": "activity_01XyDMpzjS89pFZXqSFUBDr6",
  "last_id": "activity_01XyDMpzjS89pFZXqSFUBDr6"
}
```


## Filter activities

Source: https://platform.claude.com/llms-full.txt#filter-activities

Filter by organization, actor, activity type, or a `created_at` time window using the dotted sub-parameters `created_at.gte`, `.gt`, `.lte`, and `.lt`. See the [API reference](https://platform.claude.com/docs/en/api/compliance/activities/list) for each parameter's type and accepted values.

Repeatable parameters use array-bracket query syntax: pass `activity_types[]=...`, `actor_ids[]=...`, or `organization_ids[]=...` once for each value.

```bash cURL
curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/activities" \
  --data-urlencode "activity_types[]=claude_file_uploaded" \
  --data-urlencode "activity_types[]=claude_chat_created" \
  --data-urlencode "created_at.gte=2026-04-01T00:00:00Z" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01"
```

The Activity Feed produces hundreds of distinct activity types. See [Query compliance activities](https://platform.claude.com/docs/en/api/compliance/activities/list) in the API reference for the full list of values that `activity_types[]` accepts.


## Paginate results

Source: https://platform.claude.com/llms-full.txt#paginate-results

Activities are returned newest first, with ties in `created_at` broken by activity ID, and capped at `limit` results in each response (default 100, max 5,000). See the [API reference](https://platform.claude.com/docs/en/api/compliance/activities/list) for the full response schema.

The Compliance API uses two pagination schemes depending on the endpoint family:

| Endpoint family                                                                                     | Sort order                                              | Scheme     | Parameters                                                  |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | ---------- | ----------------------------------------------------------- |
| Activities                                                                                          | Newest first                                            | Cursor     | `after_id`, `before_id` (returned as `first_id`, `last_id`) |
| Chats and chat messages                                                                             | Oldest first                                            | Cursor     | `after_id`, `before_id` (returned as `first_id`, `last_id`) |
| Organizations, projects, project attachments, users, roles, role permissions, groups, group members | Endpoint-specific                                       | Page token | `page` (returned as `next_page`)                            |
| Local and remote sessions and session messages                                                      | Sessions newest first; messages oldest first by default | Page token | `page` (returned as `next_page`)                            |

Files do not paginate: they are retrieved individually by ID.

Pagination cursors and page tokens are opaque strings: pass them back unchanged. Their internal format is not stable, and parsing them will break without notice. Only one of `after_id` or `before_id` may be set in each request, and both schemes return `has_more` so you know when to stop. The session endpoints (local and remote) are the exception: they return `next_page` without `has_more`, so stop when `next_page` is `null`.

To page through activities:

* Pass the response's `last_id` as `after_id` to advance to the next page in result order. With activities sorted newest first, the next page contains older entries.
* Pass `first_id` as `before_id` to return to the previous page.
* Stop when `has_more` is `false`.

The cursor parameter sets the page direction; the endpoint's sort order sets the time direction. The same `after_id` parameter reaches older activities here. Chats sort oldest first; see [Retrieve and delete chats, files, and projects](https://platform.claude.com/docs/en/manage-claude/compliance-content-data) for the cursor semantics there.

<Note>
  **Cursors are safe to reuse on retry.** A cursor or page token from a successfully returned page remains valid; a request that fails (5xx, timeout, network error) does not advance your position. Retry the same request with the same cursor. Only move to the next cursor after you have stored the page it points past.

  Page tokens on the local session endpoints are the exception over longer pauses. On the [local session messages endpoint](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-a-local-session-transcript), a walk's `page` tokens expire 24 hours after its first page (a walk is one pass through the pages), so finish or resume within that window, or restart without the `page` parameter. On the [local session list](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions), an older `page` token is still accepted but is re-evaluated against the current retention boundary and can skip sessions, so complete list walks within 24 hours as well.
</Note>

```bash cURL
# Fetch the first page (newest activities first) and capture its trailing cursor.
last_id=$(curl --fail-with-body -sS \
  "https://api.anthropic.com/v1/compliance/activities?limit=2" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01" | jq -er '.last_id')

# Pass the cursor back unchanged to fetch the next (older) page.
curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/activities" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --data-urlencode "limit=2" \
  --data-urlencode "after_id=${last_id}"

text
cursor = stored_cursor
loop:
  if cursor is not null:
    page = GET /v1/compliance/activities?after_id={cursor}&limit=100
  else:
    page = GET /v1/compliance/activities?limit=100
  store(page.data)
  if page.last_id is not null:
    cursor = page.last_id
  if not page.has_more: break
persist(cursor)
```


## Understand the Activity object

Source: https://platform.claude.com/llms-full.txt#understand-the-activity-object

Every entry in `data` is an Activity with this top-level shape:

| Field               | Type            | Description                                                                                                                                                                                                                                             |
| ------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                | string          | Unique identifier for the activity.                                                                                                                                                                                                                     |
| `created_at`        | RFC 3339 string | When the activity occurred.                                                                                                                                                                                                                             |
| `organization_id`   | string or null  | Organization where the activity occurred, or `null` for events not tied to an organization (sign-in, sign-out, Compliance API calls).                                                                                                                   |
| `organization_uuid` | string or null  | Same scoping as `organization_id`, expressed as a UUID.                                                                                                                                                                                                 |
| `actor`             | Actor union     | Who or what performed the activity. See the following actor table.                                                                                                                                                                                      |
| `type`              | string          | The activity type, for example `claude_chat_created`.                                                                                                                                                                                                   |
| *additional fields* | varies          | Type-specific fields, for example `claude_chat_id` on chat events or `filename` on file events. See [Query compliance activities](https://platform.claude.com/docs/en/api/compliance/activities/list) in the API reference for the per-type field list. |

The `actor` field is a discriminated union. The `type` discriminator tells you which other fields are present:

| `actor.type`                 | When it appears                                                                                                                                                                        | Key fields                                                                                                                                            |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `user_actor`                 | A signed-in claude.ai or Claude Console user took the action.                                                                                                                          | `email_address`, `user_id`, `ip_address`, `user_agent`                                                                                                |
| `api_actor`                  | A request called the Claude API or the Compliance API with a customer-issued API key. Compliance API calls produce this actor type for both Compliance Access Keys and Admin API keys. | `api_key_id`, `ip_address`, `user_agent`                                                                                                              |
| `admin_api_key_actor`        | An organization admin used an Admin API key to manage users, invites, workspaces, or API keys.                                                                                         | `admin_api_key_id`, `ip_address`, `user_agent`                                                                                                        |
| `unauthenticated_user_actor` | An action occurred before sign-in completed, for example `sso_login_initiated`.                                                                                                        | `unauthenticated_email_address`, `ip_address`, `user_agent`                                                                                           |
| `anthropic_actor`            | Anthropic acted on the organization, for example through internal tooling.                                                                                                             | `email_address` (always `null`; present for shape consistency with `user_actor`, because Anthropic operators are not represented by individual email) |
| `scim_directory_sync_actor`  | An identity provider (such as Okta, Microsoft Entra ID, or JumpCloud) pushed a change through SCIM directory sync.                                                                     | `workos_event_id`, `directory_id`, `idp_connection_type` (nullable; for example `OktaSCIMV2`, `AzureSCIMV2`)                                          |

A `claude_*_viewed` activity means a Claude app loaded content, not that a person viewed it. Types such as `claude_chat_viewed`, `claude_file_viewed`, and `claude_project_viewed` are recorded each time a Claude app loads the chat, file, or project from Anthropic's servers. Repeated loads are not deduplicated. The web, desktop, and mobile apps load content at different moments, sometimes in the background, and can display a cached copy without loading it. Counts of these activities vary by platform as a result, and they do not correspond to messages sent or screens viewed.

<Note>
  **Build forward-compatible handlers.** Pass through unrecognized `type` and `actor.type` values, and ignore fields your handler does not expect, so your integration keeps working when new activity types ship.
</Note>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-95

<CardGroup cols={2}>
  <Card title="API reference" href="https://platform.claude.com/docs/en/api/compliance/activities/list">
    The full request and response schema for `GET /v1/compliance/activities`, including every supported `activity_types[]` value.
  </Card>

  <Card title="Retrieve and delete chats, files, and projects" href="https://platform.claude.com/docs/en/manage-claude/compliance-content-data">
    Query and delete the underlying content for activities you find in the feed (Compliance Access Key required).
  </Card>

  <Card title="Design your compliance integration" href="https://platform.claude.com/docs/en/manage-claude/compliance-integration-patterns">
    Choose a polling or batch consumption pattern and plan SIEM correlation.
  </Card>

  <Card title="Handle Compliance API errors" href="https://platform.claude.com/docs/en/manage-claude/compliance-errors">
    The full error catalog.
  </Card>
</CardGroup>


---
title: Retrieve and delete chats, files, and projects
url: https://platform.claude.com/docs/en/manage-claude/compliance-content-data
description: Access chat content, file attachments, and projects for claude.ai organizations through the Compliance API.
---

<Note>
  The endpoints on this page are available only to Claude Enterprise organizations. They retrieve and delete claude.ai chats, files, and projects; transcripts of sessions in apps such as Cowork and Claude Code are covered on [Retrieve session transcripts](https://platform.claude.com/docs/en/manage-claude/compliance-sessions). See [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).
</Note>

<Check>
  **Required scope:** `read:compliance_user_data` on the Compliance Access Key. The delete endpoints also require `delete:compliance_user_data`.

  **Prerequisite:** None for listing chats organization-wide. To filter the chat list to specific users, you need user IDs from [List organization users](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#list-organization-users). The other endpoints on this page take resource IDs directly.
</Check>

The endpoints on this page expose Claude Enterprise chat content, file uploads, projects, and project attachments to compliance reviewers. They support eDiscovery (electronic discovery) exports, data loss prevention (DLP) enforcement, and account-deletion responses. Chat, file, and project content is retained for as long as your organization's retention policy allows. When a user deletes a chat in claude.ai, its message content, attached files, tool-generated files, and artifacts are deleted with it. The Compliance API still lists the chat, with `deleted_at` populated and an empty `name`, and returns its messages without their content. Chats that have been hard-deleted (through the Compliance API itself, or after the organization's retention window expires) are not retrievable.

Both scopes are granted only on Compliance Access Keys (`sk-ant-api01-...`) created in claude.ai; see [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access) to provision one. The `read:compliance_user_data` scope covers retrieval; `delete:compliance_user_data` is required only for the delete endpoints. The chat, file, project, and attachment endpoints are not available to Admin API keys (`sk-ant-admin01-...`); calls authenticated with an Admin API key return [403 Forbidden](https://platform.claude.com/docs/en/manage-claude/compliance-errors#403-forbidden).

Endpoints on this page paginate two ways; see [Paginate results](https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed#paginate-results) for the full reference. Each section notes which scheme applies.


## Retrieve chats and messages

Source: https://platform.claude.com/llms-full.txt#retrieve-chats-and-messages

Use [List chats](https://platform.claude.com/docs/en/api/compliance/apps/chats/list) to page through chat metadata, then [Get chat messages](https://platform.claude.com/docs/en/api/compliance/apps/chats/messages/list) to fetch the full message content of one chat.

The chat list endpoint defaults to organization-wide scope: leave off `user_ids[]` to include every chat under your parent organization. Add `order_by=updated_at` to sort by last update time. This combination is the recommended way to export chats and keep an export current, because one paginated loop picks up new chats, modified chats, and chats deleted in claude.ai for every user without enumerating users first. The following request lists chats updated since a given date.

```bash cURL
curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/apps/chats" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --data-urlencode "order_by=updated_at" \
  --data-urlencode "updated_at.gte=2025-06-01T00:00:00Z" \
  --data-urlencode "limit=100"

json Response
{
  "data": [
    {
      "id": "claude_chat_01H5CWunD7RpVJ5bHa8RCkja",
      "name": "Product Requirements Discussion",
      "created_at": "2026-04-10T08:09:10Z",
      "updated_at": "2026-04-10T09:10:11Z",
      "deleted_at": null,
      "href": "https://claude.ai/chat/abcdef01-2345-6789-abcd-ef0123456789",
      "model": "claude-opus-5",
      "organization_uuid": "91012d09-e48b-438e-a489-1bebfd8fa6f9",
      "project_id": "claude_proj_01KGp4eZNug9ri4kE35RSppq",
      "user": {
        "id": "user_01XyDMpzjS89pFZXqSFUBDr6",
        "email_address": "user@example.com"
      }
    }
  ],
  "has_more": true,
  "first_id": "eyJrIjogInVwZGF0ZWRfYXQiLCAidCI6ICIyMDI2LTA0LTEwVDA5OjEwOjExKzAwOjAwIiwgImlkIjogImFiY2RlZjAxLS4uLiJ9",
  "last_id": "eyJrIjogInVwZGF0ZWRfYXQiLCAidCI6ICIyMDI2LTA0LTEwVDA5OjEwOjExKzAwOjAwIiwgImlkIjogImFiY2RlZjAxLS4uLiJ9"
}

bash cURL
curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/apps/chats" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --data-urlencode "user_ids[]=user_01XyDMpzjS89pFZXqSFUBDr6" \
  --data-urlencode "created_at.gte=2025-06-01T00:00:00Z" \
  --data-urlencode "limit=100"

bash cURL
chat_id="claude_chat_01H5CWunD7RpVJ5bHa8RCkja"

curl --fail-with-body -sS \
  "https://api.anthropic.com/v1/compliance/apps/chats/$chat_id/messages" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01"

json Response
{
  "id": "claude_chat_01H5CWunD7RpVJ5bHa8RCkja",
  "name": "Product Requirements Discussion",
  "created_at": "2026-04-10T08:09:10Z",
  "updated_at": "2026-04-10T09:10:11Z",
  "deleted_at": null,
  "href": "https://claude.ai/chat/abcdef01-2345-6789-abcd-ef0123456789",
  "model": "claude-opus-5",
  "organization_uuid": "91012d09-e48b-438e-a489-1bebfd8fa6f9",
  "project_id": "claude_proj_01KGp4eZNug9ri4kE35RSppq",
  "user": {
    "id": "user_01XyDMpzjS89pFZXqSFUBDr6",
    "email_address": "user@example.com"
  },
  "chat_messages": [
    {
      "id": "claude_chat_msg_01VnBPkLmtj7YdW5QrXKEA8c",
      "role": "user",
      "created_at": "2026-04-10T08:09:10Z",
      "content": [
        {
          "type": "text",
          "text": "Can you help me draft requirements for our new dashboard feature?"
        }
      ],
      "files": [
        {
          "id": "claude_file_01UaT9wBcDfGhJkLmNpQrSv7",
          "filename": "dashboard_mockup_v1.pdf",
          "mime_type": "application/pdf",
          "size_bytes": 482133,
          "md5": "56367e4d2705cc9c025ad07424e944f0",
          "created_at": "2026-04-10T08:09:10Z"
        }
      ]
    },
    {
      "id": "claude_chat_msg_01M8tFcHwbQ2kY6NpEjRZv4D",
      "role": "assistant",
      "created_at": "2026-04-10T08:09:11Z",
      "content": [
        {
          "type": "text",
          "text": "I'd be happy to help you draft requirements for your dashboard feature..."
        }
      ],
      "generated_files": [
        {
          "id": "claude_gen_file_01TbR8wAcCeFhJkLnPqStUvX",
          "filename": "requirements_summary.csv",
          "mime_type": "text/csv",
          "size_bytes": 2048,
          "md5": "89968669461d95416549937168269d6b"
        }
      ],
      "artifacts": [
        {
          "id": "claude_artifact_01HqRsTuVwXyZa2BcDeFgH4J",
          "version_id": "claude_artifact_version_01KmNpQrSt3UvWxYz5AbCdEfG",
          "title": "Dashboard Requirements Draft",
          "artifact_type": "text/markdown"
        }
      ]
    }
  ],
  "has_more": false,
  "first_id": "eyJtc2dfdXVpZCI6ICIwZjcwYjA2Ni0uLi4ifQ==",
  "last_id": "eyJtc2dfdXVpZCI6ICJhNGUwYjE3Mi0uLi4ifQ=="
}
```

`files`, `generated_files`, and `artifacts` can each be `null` on a given message. `files` are the files and text attachments (for example, PDFs, images, spreadsheets, documents, and pasted text) the user attached to the message, as claude.ai stored them. `generated_files` are binary files the assistant created during the conversation through tool use (for example, PDFs, spreadsheets, or slide decks). `artifacts` are versioned documents (for example, code or markdown) the assistant generated or updated in its response; an artifact can be revised across multiple assistant turns in the same chat, and each revision appears as a new `version_id` under the same artifact `id`. Pass each entry's `id` (or `version_id` for artifacts) to the matching content endpoint in [Retrieve files and artifacts](https://platform.claude.com/docs/en/manage-claude/compliance-content-data#retrieve-files-and-artifacts) to download it.


## Retrieve files and artifacts

Source: https://platform.claude.com/llms-full.txt#retrieve-files-and-artifacts

Files and artifacts are downloaded by ID, not listed independently. The IDs come from the chat messages endpoint in [Retrieve chats and messages](https://platform.claude.com/docs/en/manage-claude/compliance-content-data#retrieve-chats-and-messages) (the `files`, `generated_files`, and `artifacts` arrays on each message) or, for project-level uploads, from the [project attachments endpoint](https://platform.claude.com/docs/en/manage-claude/compliance-content-data#retrieve-projects-and-attachments).

Pick the endpoint that matches your ID type and the data you need. The same file content endpoint serves both chat files and project files.

| You have                       | You want                                | Use this endpoint                                                                                                          |
| ------------------------------ | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `claude_file_*` ID             | The file's content                      | [Download file content](https://platform.claude.com/docs/en/api/compliance/apps/chats/files/download)                      |
| `claude_file_*` ID             | The file's metadata only                | [Get file metadata](https://platform.claude.com/docs/en/api/compliance/apps/chats/files/retrieve)                          |
| `claude_gen_file_*` ID         | A tool-generated file's binary content  | [Download a Claude-generated file](https://platform.claude.com/docs/en/api/compliance/apps/chats/generated_files/download) |
| `claude_gen_file_*` ID         | A tool-generated file's metadata only   | [Get generated-file metadata](https://platform.claude.com/docs/en/api/compliance/apps/chats/generated_files/retrieve)      |
| `claude_artifact_version_*` ID | One artifact version's text             | [Download artifact content](https://platform.claude.com/docs/en/api/compliance/apps/artifacts/download)                    |
| `claude_artifact_version_*` ID | The artifact version's metadata only    | [Get artifact metadata](https://platform.claude.com/docs/en/api/compliance/apps/artifacts/retrieve)                        |
| `claude_proj_doc_*` ID         | A project document's plain-text content | [Get project document content](https://platform.claude.com/docs/en/api/compliance/apps/projects/documents/retrieve)        |
| `claude_proj_doc_*` ID         | A project document's metadata only      | [Get project document metadata](https://platform.claude.com/docs/en/api/compliance/apps/projects/documents/metadata)       |

The file content endpoint streams the content that claude.ai stored for the file as a chunked binary response. That content is not always identical to the file the user uploaded. Images can be served as a processed copy rather than the uploaded bytes. Some documents attached to chats (for example, Word files, PowerPoint files, and some PDFs) are stored as the text claude.ai extracted from them. For these documents, the endpoint returns the extracted text under the original file name, and the original document is not available through the Compliance API. The `size_bytes` and `md5` fields describe the stored content rather than the uploaded file. The file name and `mime_type` can still name the uploaded document's format. Identify a file's format from the returned bytes, not from its name or declared type.

The response carries these headers:

* `Content-Disposition: attachment; filename*=utf-8''<percent-encoded filename>` carries the original upload file name in RFC 5987 extended form. The extended form is used for every file name, not only non-ASCII ones.
* `Content-Type` carries the MIME type recorded for the stored content, which for a document stored as extracted text can still name the original document format.
* `Content-MD5` carries the MD5 digest of the served bytes, base64-encoded as specified in RFC 1864.
* `Transfer-Encoding: chunked` is always set.

```bash cURL
file_id="claude_file_01UaT9wBcDfGhJkLmNpQrSv7"

curl --fail-with-body -sS -OJ \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01" \
  "https://api.anthropic.com/v1/compliance/apps/chats/files/$file_id/content"
```

The `-OJ` flags tell curl to save the response under the file name from `Content-Disposition`, which is the original file name the user uploaded.

The artifact content endpoint returns the text body of one artifact version. Pass the `version_id` from one of the entries in an assistant message's `artifacts` array, not the artifact's stable `id`. Each new version of an artifact has its own `version_id`, and the Compliance API serves the exact bytes of that version.


## Retrieve projects and attachments

Source: https://platform.claude.com/llms-full.txt#retrieve-projects-and-attachments

Projects bundle related chats together with custom instructions, knowledge base content, and attached files or text documents. The Compliance API exposes project metadata, project details, and the list of attachments belonging to a project.

* [List projects](https://platform.claude.com/docs/en/api/compliance/apps/projects/list)
* [Get project details](https://platform.claude.com/docs/en/api/compliance/apps/projects/retrieve)
* [List project attachments](https://platform.claude.com/docs/en/api/compliance/apps/projects/attachments/list)
* [Get project document content](https://platform.claude.com/docs/en/api/compliance/apps/projects/documents/retrieve)

Project results are sorted by creation date ascending. Attachment results are sorted by `created_at` ascending, with ties broken by `id`. Project list and attachment list responses paginate with an opaque `next_page` page token instead of the `first_id`/`last_id` cursors used by chats and the Activity Feed. Pass the token back as the `page` query parameter on the next request.

### Project files versus project documents

A project attachment is one of two distinct shapes, identified by the `type` discriminator on each entry:

Entries with `type` of `project_file` are file uploads (PDFs, images, spreadsheets) whose IDs start with `claude_file_`; download them with [Download file content](https://platform.claude.com/docs/en/api/compliance/apps/chats/files/download). Entries with `type` of `project_doc` are plain-text documents (always `text/plain`) whose IDs start with `claude_proj_doc_`, including documents such as Word files that claude.ai converts to text when they are added to a project; fetch them with [Get project document content](https://platform.claude.com/docs/en/api/compliance/apps/projects/documents/retrieve).

A consumer that walks the attachment list must branch on `type` and call the matching content endpoint for each entry. The following request lists one page of attachments; paginate by passing `next_page` back as the `page` parameter until `has_more` is `false`.

```bash cURL
project_id="claude_proj_01KGp4eZNug9ri4kE35RSppq"

curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/apps/projects/$project_id/attachments" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01"

json Response
{
  "data": [
    {
      "id": "claude_file_01UaT9wBcDfGhJkLmNpQrSv7",
      "created_at": "2026-04-10T08:09:10Z",
      "filename": "dashboard_mockup_v1.pdf",
      "mime_type": "application/pdf",
      "size_bytes": 482133,
      "md5": "56367e4d2705cc9c025ad07424e944f0",
      "type": "project_file"
    },
    {
      "id": "claude_proj_doc_01YnT8sBcWvUtXzQpMkRfDgH",
      "created_at": "2026-04-10T08:09:11Z",
      "filename": "requirements.md",
      "mime_type": "text/plain",
      "type": "project_doc"
    }
  ],
  "has_more": false,
  "next_page": null
}
```


## Delete content

Source: https://platform.claude.com/llms-full.txt#delete-content

<Warning>
  Every successful delete is permanent and immediate. There is no recovery window.
</Warning>

The Compliance API exposes hard-delete endpoints for chats, files, project documents, and entire projects. A hard-deleted chat cannot be restored, and it stops appearing in list responses afterward.

* [Delete chat](https://platform.claude.com/docs/en/api/compliance/apps/chats/delete): also removes the chat's messages and any files attached to those messages.
* [Delete file](https://platform.claude.com/docs/en/api/compliance/apps/chats/files/delete): handles both chat files and project files.
* [Delete project document](https://platform.claude.com/docs/en/api/compliance/apps/projects/documents/delete): removes a single project document by ID.
* [Delete project](https://platform.claude.com/docs/en/api/compliance/apps/projects/delete): see [Detach chats before deleting a project](https://platform.claude.com/docs/en/manage-claude/compliance-content-data#detach-chats-before-deleting-a-project).

All four endpoints require the `delete:compliance_user_data` scope, which is granted separately from the read scope when the Compliance Access Key is created.

The following request deletes one chat. The same pattern applies to the other delete endpoints; only the URL changes.

```bash cURL
# WARNING: This operation PERMANENTLY deletes the chat, all of its messages,
# and any attached files. Deletion is immediate and cannot be undone. It
# requires the `delete:compliance_user_data` scope, which is granted separately
# from `read:compliance_user_data` when the Compliance Access Key is created.
# Ensure you have explicit authorization before running this.

chat_id="claude_chat_01H5CWunD7RpVJ5bHa8RCkja"

curl --fail-with-body -sS -X DELETE \
  "https://api.anthropic.com/v1/compliance/apps/chats/$chat_id" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01"

json Response
{
  "id": "claude_chat_01H5CWunD7RpVJ5bHa8RCkja",
  "type": "claude_chat_deleted"
}

json
{
  "error": {
    "type": "conflict_error",
    "message": "The \"claude_proj_01KGp4eZNug9ri4kE35RSppq\" project cannot be deleted as it has chats attached to it. Delete or detach all chats, and try deleting the project again."
  }
}
```

To resolve, list the project's chats with `GET /v1/compliance/apps/chats?user_ids[]={user_id}&project_ids[]={project_id}` (the `project_ids[]` filter requires at least one `user_ids[]` value; enumerate IDs through [List organization users](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#list-organization-users)), delete each one with `DELETE /v1/compliance/apps/chats/{claude_chat_id}` (or move it out of the project from claude.ai), and then retry the project delete.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-96

<CardGroup cols={2}>
  <Card title="API reference" href="https://platform.claude.com/docs/en/api/compliance/apps">
    The full request and response schema for every chat, file, project, and artifact endpoint.
  </Card>

  <Card title="Retrieve session transcripts" href="https://platform.claude.com/docs/en/manage-claude/compliance-sessions">
    List the sessions your users run in Claude apps and agents, such as Cowork and Claude Code, and retrieve their transcripts.
  </Card>

  <Card title="List organizations, users, roles, groups, and settings" href="https://platform.claude.com/docs/en/manage-claude/compliance-org-data">
    Enumerate the people and teams associated with the chats and projects on this page.
  </Card>
</CardGroup>


---
title: Retrieve session transcripts
url: https://platform.claude.com/docs/en/manage-claude/compliance-sessions
description: List the sessions your users run in Claude apps and agents, such as Claude Cowork and Claude Code, and retrieve their transcripts through the Compliance API.
---

<Note>
  The endpoints on this page are available only to Claude Enterprise organizations. The local and remote session endpoints are stable for Cowork and Claude Code sessions; coverage of Claude Science and Claude for Microsoft 365 sessions is in beta. The endpoints work with the same Compliance Access Key and `read:compliance_user_data` scope as the [chat, file, and project endpoints](https://platform.claude.com/docs/en/manage-claude/compliance-content-data); no new key, scope, setting, or client update is required. See [Set up the Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api-access).
</Note>

<Check>
  **Required scope:** `read:compliance_user_data` on the Compliance Access Key.

  **Prerequisite:** None for listing sessions organization-wide. To filter the remote session list (sessions in the cloud) to specific users, you need user IDs from [List organization users](https://platform.claude.com/docs/en/manage-claude/compliance-org-data#list-organization-users); the local session list has no user filter.
</Check>

The endpoints on this page expose transcripts of the sessions your users run in Claude apps and agents (today: Cowork, Claude Code, Claude Science, and Claude for Microsoft 365) from your Claude Enterprise organizations to compliance reviewers. Each session is a single conversation with Claude; its transcript is the sequence of user prompts, assistant responses, and tool calls and results in that conversation. The endpoints support eDiscovery (electronic discovery) exports and data loss prevention (DLP) enforcement.

The Compliance API groups sessions into two endpoint families according to where they run: local session endpoints for sessions on users' machines, and remote session endpoints for sessions that run in the cloud in Anthropic-managed environments. Both families are read-only, and neither is available to Admin API keys (`sk-ant-admin01-...`): calls authenticated with an Admin API key return [403 Forbidden](https://platform.claude.com/docs/en/manage-claude/compliance-errors#403-forbidden).

The following table maps each product, and where it runs, to the endpoint family that returns its sessions and the `product_surface` value that identifies them in responses. Products are added to this table as coverage expands.

| Product and where it runs                                                                                                                | Endpoint family                                                  | `product_surface`                                                                                                                                    |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cowork in Claude Desktop, running on the user's machine                                                                                  | Local session endpoints (`/v1/compliance/apps/sessions/local`)   | `cowork`                                                                                                                                             |
| Claude Code in the terminal, in Claude Desktop, or in an IDE extension, running on the user's machine                                    | Local session endpoints                                          | `claude_code`                                                                                                                                        |
| Claude Science desktop app, running on the user's machine                                                                                | Local session endpoints                                          | `claude_science`                                                                                                                                     |
| Claude for Microsoft 365 (the Claude add-ins for Excel, PowerPoint, Word, and Outlook), running in the Microsoft 365 desktop or web apps | Local session endpoints                                          | `office_agents/excel`, `office_agents/powerpoint`, `office_agents/word`, or `office_agents/outlook` (`office_agents` when the app is not identified) |
| Cowork sessions started on claude.ai web or mobile, running in the cloud in Anthropic-managed environments                               | Remote session endpoints (`/v1/compliance/apps/sessions/remote`) | `cowork_remote`                                                                                                                                      |

Capture of local sessions is tied to the Compliance API being enabled for your organization and applies while users are signed in with their Claude Enterprise account. The session endpoints do not return the following:

* Claude Code sessions authenticated with a Claude Console API key, or run through a third-party cloud platform such as Amazon Bedrock, Google Cloud, or Microsoft Foundry.
* Claude Code on the web. It also runs in the cloud in Anthropic-managed environments, but it is not a remote session; the remote session endpoints return Cowork sessions only.
* Local sessions in organizations with [HIPAA readiness](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#hipaa-readiness) enabled. No local session data is captured, so the local session endpoints return no sessions for those organizations.
* Local sessions for which [zero data retention (ZDR)](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#zero-data-retention-zdr-scope) is in effect. These sessions are excluded from list results, and the retrieve and messages endpoints return 404 for them.

Anthropic recommends the Compliance API for retrieving session content. The following table compares [local sessions](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions) and [remote sessions](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-remote-sessions) with the OpenTelemetry-based alternatives available for Cowork and Claude Code, [Cowork's OpenTelemetry logging](https://support.claude.com/en/articles/14477985-monitor-claude-cowork-activity-with-opentelemetry) and [Claude Code monitoring](https://code.claude.com/docs/en/monitoring-usage).

|                                                           | Local sessions (on users' machines)                                                                                                                                            | Remote sessions (in the cloud)                                                                                                                                                 | OpenTelemetry logging                                                                                         |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| Delivery                                                  | Pull: query and export over HTTPS                                                                                                                                              | Pull: query and export over HTTPS                                                                                                                                              | Push: streamed to your OTLP collector                                                                         |
| Setup                                                     | Works with your existing Compliance Access Key                                                                                                                                 | Works with your existing Compliance Access Key                                                                                                                                 | Admin configures an OTLP endpoint and content-capture settings                                                |
| Infrastructure                                            | Anthropic-hosted                                                                                                                                                               | Anthropic-hosted                                                                                                                                                               | You run the collector and storage                                                                             |
| ID prefix                                                 | `clls_`                                                                                                                                                                        | `cse_`                                                                                                                                                                         | N/A                                                                                                           |
| `product_surface` values                                  | `cowork`, `claude_code`, `claude_science`, and values beginning with `office_agents`                                                                                           | `cowork_remote`                                                                                                                                                                | N/A                                                                                                           |
| Retention                                                 | 6 years by default, or your organization's custom conversation retention period when a finite one is set; held by Anthropic                                                    | 6 years, unless a user deletes the session sooner; held by Anthropic                                                                                                           | Your infrastructure, your policies                                                                            |
| User prompts and assistant responses                      | Yes                                                                                                                                                                            | Yes                                                                                                                                                                            | Yes, subject to content-capture settings                                                                      |
| Tool inputs                                               | Truncated to 10,000 bytes per input by default; up to about 1 MiB on request                                                                                                   | Truncated to 10,000 bytes per input by default; up to about 1 MiB on request                                                                                                   | Truncated summaries                                                                                           |
| Tool result content                                       | Each text entry truncated to 10,000 bytes by default; up to about 1 MiB on request                                                                                             | Each text entry truncated to 10,000 bytes by default; up to about 1 MiB on request                                                                                             | Metadata such as size and success; Claude Code can also capture content with an optional, size-capped setting |
| File contents                                             | Yes, through transcript tool calls (text only; other content appears as a placeholder)                                                                                         | Yes, through transcript tool calls (text only; other content is omitted)                                                                                                       | File paths; Claude Code can also capture contents with an optional, size-capped setting                       |
| Host and device metadata (terminal type, workspace paths) | No                                                                                                                                                                             | No                                                                                                                                                                             | Yes                                                                                                           |
| Token usage and cost                                      | No; available through the [Claude Enterprise Analytics API](https://platform.claude.com/docs/en/manage-claude/analytics-api#get-access-to-the-claude-enterprise-analytics-api) | No; available through the [Claude Enterprise Analytics API](https://platform.claude.com/docs/en/manage-claude/analytics-api#get-access-to-the-claude-enterprise-analytics-api) | Yes                                                                                                           |


## Sessions on users' machines (local sessions)

Source: https://platform.claude.com/llms-full.txt#sessions-on-users-machines-local-sessions

Local sessions run on users' machines while they are signed in with their Claude Enterprise account: today, Cowork in Claude Desktop, Claude Code (in the terminal, in Claude Desktop, or in an IDE extension), the Claude Science desktop app, and Claude for Microsoft 365 in Excel, PowerPoint, Word, and Outlook.

The Compliance API exposes local sessions through three endpoints: `GET /v1/compliance/apps/sessions/local` lists session metadata, `GET /v1/compliance/apps/sessions/local/{session_id}` retrieves one session's metadata, and `GET /v1/compliance/apps/sessions/local/{session_id}/messages` returns one session's transcript. All three require the `read:compliance_user_data` scope and count only against the shared Compliance API rate limit; they are not subject to the second request budget that applies to the remote session endpoints. See [429 Too Many Requests](https://platform.claude.com/docs/en/manage-claude/compliance-errors#429-too-many-requests). If local sessions are not available to your parent organization, all three endpoints return 404 with the message `Local sessions are not available.` (see [Local session not found](https://platform.claude.com/docs/en/manage-claude/compliance-errors#local-session-not-found)); while session listings or captured content are temporarily unavailable, they return 503 (see [Local sessions temporarily unavailable](https://platform.claude.com/docs/en/manage-claude/compliance-errors#local-sessions-temporarily-unavailable)).

For local sessions, Anthropic records each conversation server-side as its requests reach the Claude API; nothing is installed on the device, and nothing is collected beyond the requests the client already sends to the Claude API. Local session transcripts show what Claude was asked to do and what it returned, not what happened on the device. File and network activity is visible only through the tool calls and tool results in the transcript, so activity that never reaches the API (for example, local files the session never sent) is not captured.

In organizations that use [customer-managed encryption keys](https://platform.claude.com/docs/en/manage-claude/cmek), local session transcripts are encrypted under your customer-managed key and returned as usual. While that key cannot be used (for example, because you disabled or revoked it, or because it cannot be reached), the messages endpoint returns [503 Service Unavailable](https://platform.claude.com/docs/en/manage-claude/compliance-errors#local-sessions-temporarily-unavailable) for the affected pages instead of transcript content. Those messages are never reported as `not_captured` (see [Retrieve a local session transcript](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-a-local-session-transcript)). Listing sessions and retrieving session metadata are not affected.

The list endpoint returns session metadata, with no transcript content, for every linked organization your key can read. Unlike the remote session list, it has no organization or user filters: bound the results in time with the `created_at.gte` and `created_at.lt` parameters. Both take RFC 3339 timestamps with a required UTC offset, and when both are supplied, `created_at.lt` must be strictly after `created_at.gte` or the request returns [400 Bad Request](https://platform.claude.com/docs/en/manage-claude/compliance-errors#400-bad-request). A third time filter, `updated_at.gte`, bounds by last activity instead of first: it returns sessions whose last inference call is at or after the given time and combines with the `created_at` filters without changing the ordering or pagination. Use it to poll for sessions active since a previous pass, as described later in this section. New sessions and messages appear in results after a short processing delay, typically within minutes; a session that is missing immediately after it starts is not necessarily uncaptured. The following request lists sessions created since a given date.

```bash cURL
curl --fail-with-body -sS -G \
  "https://api.anthropic.com/v1/compliance/apps/sessions/local" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --data-urlencode "created_at.gte=2026-07-01T00:00:00Z" \
  --data-urlencode "limit=100"

json Response
{
  "data": [
    {
      "type": "compliance_local_session",
      "id": "clls_01HxKpLmNoPqRsTuVwXyZaBc",
      "organization_uuid": "9a1e0000-0000-0000-0000-000000000000",
      "workspace_id": "wrkspc_01SvYKoWVRVHoEbwESNvzYdR",
      "user": {
        "id": "user_01GpKpLmNoPqRsTuVwXyZaBc",
        "email_address": "engineer@example.com"
      },
      "product_surface": "cowork",
      "created_at": "2026-07-09T14:02:11Z",
      "updated_at": "2026-07-09T14:02:38Z"
    },
    {
      "type": "compliance_local_session",
      "id": "clls_01HyLqMnOpQrStUvWxYzAbCd",
      "organization_uuid": "9a1e0000-0000-0000-0000-000000000000",
      "workspace_id": null,
      "user": {
        "id": "user_01HqRsTuVwXyZaBcDeFgHiJk",
        "email_address": null
      },
      "product_surface": "claude_code",
      "created_at": "2026-07-08T09:15:43Z",
      "updated_at": "2026-07-08T09:52:10Z"
    }
  ],
  "next_page": "page_AAEfQx7mPdLkq9Rt2VwHbZk"
}

bash cURL
session_id="clls_01HxKpLmNoPqRsTuVwXyZaBc"

curl --fail-with-body -sS \
  "https://api.anthropic.com/v1/compliance/apps/sessions/local/$session_id/messages" \
  --header "x-api-key: $ANTHROPIC_COMPLIANCE_ACCESS_KEY" \
  --header "anthropic-version: 2023-06-01"

json Response
{
  "session": {
    "type": "compliance_local_session",
    "id": "clls_01HxKpLmNoPqRsTuVwXyZaBc",
    "organization_uuid": "9a1e0000-0000-0000-0000-000000000000",
    "workspace_id": "wrkspc_01SvYKoWVRVHoEbwESNvzYdR",
    "user": {
      "id": "user_01GpKpLmNoPqRsTuVwXyZaBc",
      "email_address": null
    },
    "product_surface": "cowork",
    "created_at": "2026-07-09T14:02:11Z",
    "updated_at": "2026-07-09T14:02:38Z"
  },
  "data": [
    {
      "type": "compliance_local_session_message",
      "id": "clsm_01J4KpLmNoPqRsTuVwXyZaBa",
      "role": "user",
      "model": null,
      "created_at": "2026-07-09T14:02:11Z",
      "provenance": {
        "type": "synthetic_marker"
      },
      "content": [
        {
          "type": "text",
          "text": "[system prompt content not shown]",
          "truncated": true
        }
      ]
    },
    {
      "type": "compliance_local_session_message",
      "id": "clsm_01J4KpLmNoPqRsTuVwXyZaBc",
      "role": "user",
      "model": null,
      "created_at": "2026-07-09T14:02:11Z",
      "provenance": null,
      "content": [
        {
          "type": "text",
          "text": "Fix the failing test in tests/auth_test.py",
          "truncated": false
        }
      ]
    },
    {
      "type": "compliance_local_session_message",
      "id": "clsm_01J4KpLmNoPqRsTuVwXyZaBd",
      "role": "assistant",
      "model": "claude-opus-5",
      "created_at": "2026-07-09T14:02:11Z",
      "provenance": null,
      "content": [
        {
          "type": "text",
          "text": "I'll read the test file first.",
          "truncated": false
        },
        {
          "type": "tool_use",
          "id": "toolu_01AbCdEfGhIjKlMnOpQrSt",
          "name": "Read",
          "input": "{\"file_path\":\"tests/auth_test.py\"}",
          "truncated": false
        }
      ]
    },
    {
      "type": "compliance_local_session_message",
      "id": "clsm_01J4KpLmNoPqRsTuVwXyZaBe",
      "role": "user",
      "model": null,
      "created_at": "2026-07-09T14:02:38Z",
      "provenance": null,
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01AbCdEfGhIjKlMnOpQrSt",
          "name": "Read",
          "is_error": false,
          "content": [
            {
              "type": "text",
              "text": "def test_login_expiry():\n    ..."
            }
          ],
          "truncated": false
        }
      ]
    },
    {
      "type": "compliance_local_session_message",
      "id": "clsm_01J4KpLmNoPqRsTuVwXyZaBf",
      "role": "assistant",
      "model": "claude-opus-5",
      "created_at": "2026-07-09T14:02:38Z",
      "provenance": null,
      "content": [
        {
          "type": "text",
          "text": "The test was asserting on a stale expiry timestamp. I've updated it.",
          "truncated": false
        }
      ]
    }
  ],
  "next_page": null
}
```

The response embeds a `session` envelope alongside the paginated `data` array. The first record in this example is the marker that stands in for the request's system prompt; its `provenance` is described later in this section. On this endpoint `user.email_address` is always `null`: the messages endpoint does not resolve email addresses, so a `null` here does not mean the user's account was deleted. To attribute a session to an email address, join `user.id` against the [list endpoint](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions) or the retrieve endpoint (`GET /v1/compliance/apps/sessions/local/{session_id}`).

Messages are returned oldest first by default; pass `order=desc` to reverse. Pagination uses the same `page`/`next_page` scheme as the list endpoint, with a `limit` default of 100 and a max of 1,000. A page can end early when the response reaches its size limit, so a page with fewer than `limit` messages does not mean you have reached the end; keep paginating until `next_page` is `null`. Page cursors are bound to the session and sort order they were issued under, and a walk's cursors expire 24 hours after its first page: an expired cursor returns [400 Bad Request](https://platform.claude.com/docs/en/manage-claude/compliance-errors#400-bad-request) telling you to restart without the `page` parameter, and the restarted walk reflects the current retention boundary. A cursor issued for a different session or `order` also returns 400, as an invalid cursor.

Each message carries a `role` (`user` or `assistant`) and a `content` array of `text`, `tool_use`, and `tool_result` blocks. It also carries a `model`: on an assistant turn captured from the Claude API this is the model that served the turn, and it is `null` on user messages and on any assistant message whose `provenance` is set, because client-asserted history and synthetic markers were not produced by a model and the serving model is unknown for unavailable content. A `text` block carries `text` and `truncated`. A `tool_use` block carries `id`, `name`, `input`, and `truncated`, where `input` is a JSON-encoded string rather than an object. A `tool_result` block carries `tool_use_id`, `name`, `is_error`, a `content` array of `text` entries, and `truncated`. MCP tool calls and results, and most server tool calls and results, are normalized into these same `tool_use` and `tool_result` shapes; any other block type appears as a `[<block type> content not shown]` placeholder. A message `id` is stable while the turn is retained. Every message reconstructed from the same inference call carries that call's timestamp, so consecutive messages often share a `created_at` value; preserve the returned order rather than re-sorting by timestamp.

Each message also carries a `provenance` field describing how its content was captured. `provenance` is `null` for verified content captured by the Claude API, which is the common case. Otherwise it is an object whose `type` marks the exception:

* `content_unavailable` means the content cannot be returned. The `content` array is empty, and `provenance.reason` states why. `not_captured` means no content is available for the turn. It does not prove that no record was stored: content that Anthropic's data-handling policies withhold from the Compliance API is reported with the same reason, and so are individual turns within an otherwise captured session that are unavailable for such reasons. An unusable customer-managed key is the one exception and returns [503 Service Unavailable](https://platform.claude.com/docs/en/manage-claude/compliance-errors#local-sessions-temporarily-unavailable) instead. `client_aborted` means the client closed the connection or cancelled the request before the response completed, so the turn's response was not captured; any partial output already streamed to the client is not included, and this reason applies to assistant-role turns only. `cmek_key_revoked` is reserved for content encrypted under your organization's customer-managed key when that key is unavailable (for example, revoked). It is not currently returned, because an unusable key produces a 503 instead, but handle it for forward compatibility. `retention_elapsed` means the content aged past retention. `oversize` means a single message exceeded the per-message size bound; the message is still returned, with an empty `content` array.
* `client_asserted` marks assistant messages that the client supplied as conversation history and that could not be matched to a captured response; their authorship is not verified.
* `synthetic_marker` marks records generated by the endpoint itself, such as the marker that stands in for the system prompt. When the client rewrites or compacts its conversation history mid-session (for example, after context compaction), the transcript inserts a marker message at that point and continues with the new content the client sent; when your organization has a finite retention period, the rewritten history itself is withheld (a second marker notes this) and only the latest user turn and what follows are shown.

Marker and client-asserted messages begin with a bracketed explanatory `text` block flagged `truncated: true`, for example `[system prompt content not shown]`. Treat these records as present but unavailable or unverified rather than missing, and tolerate unrecognized `provenance` types and reasons.

Two parameters cap how many bytes of each tool block are returned: `tool_use_input_max_bytes` and `tool_result_max_bytes`, both defaulting to 10,000 bytes. Pass `-1` for the server maximum (about 1 MiB per string); `0` returns [400 Bad Request](https://platform.claude.com/docs/en/manage-claude/compliance-errors#400-bad-request), and values above the maximum are clamped to it. A string cut off by either cap is cut on a character boundary and has an in-band suffix appended (for example, `…[truncated; pass tool_result_max_bytes=-1 for the server max]`), and its block carries `"truncated": true`. A truncated `tool_use` `input` is therefore no longer valid JSON, so parse tool inputs only from untruncated blocks (or raise the cap and refetch). Blocks of type `text` are always capped at the same server maximum of about 1 MiB; no parameter raises it, and a `text` block at the bound also carries `"truncated": true`.

Transcript content honors the retention period described under [Sessions on users' machines](https://platform.claude.com/docs/en/manage-claude/compliance-sessions#retrieve-local-sessions). When the start of a session has aged past it, the transcript begins with a single `content_unavailable` placeholder with `reason` of `retention_elapsed`, and the retained messages follow. When every call in a session has aged out, the messages endpoint returns [404 Not Found](https://platform.claude.com/docs/en/manage-claude/compliance-errors#404-not-found), as it does for sessions in organizations your key cannot read, sessions that do not exist, and sessions for which zero data retention is in effect. A malformed session ID returns [400 Bad Request](https://platform.claude.com/docs/en/manage-claude/compliance-errors#400-bad-request).
