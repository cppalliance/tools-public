# promptforge-gateway

promptforge-gateway is an OpenAI-compatible API gateway that routes chat completion requests to any combination of cloud providers and locally-run GGUF models - all from a single TOML config. Point your existing OpenAI SDK client at it, swap backends without changing a line of client code, and run local inference on your own GPU with zero external dependencies. This guide walks you through every feature, from a one-endpoint proxy to multi-profile, multi-GPU deployments with managed llama-server processes and built-in web search.

## What the Gateway Does

The gateway accepts `POST /v1/chat/completions` requests in the standard OpenAI format and forwards them to a configured backend. Unknown fields like `temperature` and `top_p` pass through verbatim. Model names are aliased: the caller asks for `reasoning-large`, the gateway maps it to the right upstream model, and the response echoes back `reasoning-large` - not the provider's internal name. Every error comes back in an OpenAI-compatible envelope, so existing SDK error handling works unchanged.

## Getting Started

A minimal config needs one endpoint and one model. Create `gateway.toml`:

```toml
[gateway]
bearer_token = "${GATEWAY_TOKEN}"
listen = "127.0.0.1:8080"

[endpoints.openai]
base_url = "https://api.openai.com/v1"
api_key = "${OPENAI_API_KEY}"

[models.gpt4]
name = "gpt-4o"
endpoint = "openai"
upstream_model = "gpt-4o"
```

Start the gateway:

```bash
promptforge-gateway serve gateway.toml
```

Test with curl:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Authorization: Bearer $GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

The gateway validates the entire TOML at boot. A misspelled key is a startup failure, not a silent misconfiguration.

## Configuration

The gateway is configured entirely from TOML with eager validation. Every key is checked at load time - there are no "unknown field ignored" surprises.

Environment variable interpolation works in any string value using `${VAR}` syntax. Use `$$` to produce a literal dollar sign. Any unresolved variable fails at startup, so you know immediately when an environment is misconfigured.

```toml
[endpoints.anthropic]
base_url = "https://api.anthropic.com/v1"
api_key = "${ANTHROPIC_API_KEY}"
```

Secrets are redacted throughout the system. API keys and bearer tokens use a `Secret` type that has no `Serialize` implementation and redacts through both `Debug` and `Display`, so credentials never leak into logs or debug output.

## Models and the Catalog

Model names are capability aliases. Name them by what they do - `reasoning-large`, `fast-draft` - so the same client prompt works unchanged when you swap the underlying provider between development and production.

The gateway exposes a model catalog at `GET /v1/models`, authenticated with the same bearer token as completions. Each entry advertises:

- **name** and **description**
- **context size**
- **thinking mode** - `never`, `always`, or `switchable`
- **tool-calling dialect** and **tools mode**

Clients can query this catalog to discover available models and adapt their behavior. Set `default_max_tokens` on a model so the gateway supplies `max_tokens` when the caller omits one.

```bash
curl http://127.0.0.1:8080/v1/models \
  -H "Authorization: Bearer $GATEWAY_TOKEN"
```

## Multiple Backends

Each endpoint has its own base URL, API key, and concurrency setting. Route different models through different providers under a single gateway:

```toml
[endpoints.openai]
base_url = "https://api.openai.com/v1"
api_key = "${OPENAI_API_KEY}"

[endpoints.anthropic]
base_url = "https://api.anthropic.com/v1"
api_key = "${ANTHROPIC_API_KEY}"

[models.reasoning]
name = "reasoning-large"
endpoint = "anthropic"
upstream_model = "claude-sonnet-4-20250514"

[models.fast]
name = "fast-draft"
endpoint = "openai"
upstream_model = "gpt-4o-mini"
```

Callers see `reasoning-large` and `fast-draft`. They never know which provider sits behind each name.

## Concurrency and Queuing

Each endpoint can have a concurrency limit that caps in-flight requests. When the limit is reached, additional requests enter a bounded waiting queue. If the queue overflows, the gateway returns `503`.

Fair round-robin scheduling distributes queue slots across callers. Identify your caller by sending the `X-PromptForge-Client` header (bounded to 64 characters, at most 32 distinct labels).

Set a whole-request timeout so a stalled backend times out as a transport error rather than hanging the caller.

```toml
[endpoints.openai]
base_url = "https://api.openai.com/v1"
api_key = "${OPENAI_API_KEY}"
concurrency = 10
```

## Profiles

Profiles let you organize configurations into named TOML files under `~/.promptforge/profiles/`. Start the gateway with a profile name instead of a config path:

```bash
promptforge-gateway serve --profile production
```

This loads `~/.promptforge/profiles/production.toml`. The `--profile` flag and a positional config path are mutually exclusive.

Profiles compose through `include` chains. A leaf profile includes a base profile, and values merge depth-first up to 16 levels, with cycle detection. Override individual endpoints, models, or local models by id/name across included profiles, and factor shared definitions into base profiles.

```toml
# ~/.promptforge/profiles/base.toml
[endpoints.openai]
base_url = "https://api.openai.com/v1"
api_key = "${OPENAI_API_KEY}"
```

```toml
# ~/.promptforge/profiles/production.toml
include = ["base.toml"]

[models.reasoning]
name = "reasoning-large"
endpoint = "openai"
upstream_model = "o1"
```

Include paths resolve relative to the including file's directory, or as absolute paths.

## Runtime Profile Switching

Switch the active profile without restarting the gateway:

```bash
curl -X POST http://127.0.0.1:8080/admin/switch-profile \
  -H "Authorization: Bearer $GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"profile": "staging"}'
```

List available profiles:

```bash
curl http://127.0.0.1:8080/admin/profiles \
  -H "Authorization: Bearer $GATEWAY_TOKEN"
```

Inspect the active profile:

```bash
curl http://127.0.0.1:8080/admin/status \
  -H "Authorization: Bearer $GATEWAY_TOKEN"
```

Profile switches are atomic and serialized. A failed switch leaves the previous profile fully operational - catalog, credentials, and routing are unchanged. When local models are involved, old llama-server children stop before new ones start, so the two never hold VRAM simultaneously.

## Devices and Lanes

Devices model your physical compute resources. Each device entry has a type - `local` for hardware on the machine, `remote` for cloud endpoints - and its own concurrency setting.

Concurrency lanes let multiple local models share a GPU with per-lane admission control. Endpoints and local models bind to devices, inheriting concurrency from remote devices or using lane-level control on local devices.

```toml
[devices.gpu0]
type = "local"

[devices.cloud-anthropic]
type = "remote"
```

## Local Models

Run GGUF models locally via managed llama-server subprocesses with no external provider needed. Point a local model source at a Hugging Face HTTPS URL or a local file path:

```toml
[local_models.codegen]
name = "local-codegen"
source = "https://huggingface.co/TheBloke/CodeLlama-7B-GGUF/resolve/main/codellama-7b.Q4_K_M.gguf"
```

On first use, the gateway auto-provisions a pinned, GPU-capable llama-server binary - Vulkan on Windows and Linux, Metal on macOS - with deterministic tree-digest tamper detection. No manual llama.cpp installation required.

For gated Hugging Face repos, set `HF_TOKEN` in the environment. Local paths work directly:

```toml
[local_models.codegen]
name = "local-codegen"
source = "/models/codellama-7b.Q4_K_M.gguf"
```

You can run multiple `local_model` entries simultaneously, each backed by its own managed llama-server child registered as normal routes in the gateway.

## Local Model Tuning

Tune inference parameters per model:

```toml
[local_models.codegen]
name = "local-codegen"
source = "https://huggingface.co/TheBloke/CodeLlama-7B-GGUF/resolve/main/codellama-7b.Q4_K_M.gguf"
context = 8192
n_predict = 4096
gpu_layers = 35
flash_attention = true
cache_type_k = "f16"
cache_type_v = "f16"
```

If the GGUF's embedded Jinja chat template lacks tool-calling support, override it with `chat_template_file` pointing to a custom template. The gateway auto-detects the tool-calling dialect by probing the child's `/props` and `/v1/models` endpoints, falling back to a locally cached Hugging Face metadata sidecar.

## Local Model Operations

Managed llama-server children auto-respawn after a crash with cooldown. If a child dies between requests, the gateway detects it on the next request and respawns. On port bind collision, it retries on fresh ports up to 4 attempts.

Downloads show interactive progress bars on TTY stderr, or structured tracing log lines in non-TTY environments. Pin remote artifacts by SHA-256 digest so downloads are integrity-verified and corrupted or tampered files are rejected.

Cache management:

- Set `local.cache_dir` or `cache_dir` to relocate the artifact cache and llama.cpp install from the default `~/.promptforge`
- Artifact cache permissions are owner-private (Unix 0700, Windows per-user DACL)
- Archive path-traversal entries (`..`, symlinks, reparse points) are rejected
- Concurrent provisioning of the same artifact is serialized via per-artifact file locks
- Artifact downloads are bounded at 256 GiB

Ctrl-C during a slow local model startup triggers a clean abort rather than hanging on the readiness loop.

## Web Search

The gateway includes a Brave-backed web search tool, configured independently of the chat completion pipeline:

```toml
[tools.web_search]
api_key = "${BRAVE_SEARCH_API_KEY}"
default_count = 5
max_count = 20
max_per_host = 3
strip_tracking = true
safesearch = "moderate"
```

Query it directly:

```bash
curl -X POST http://127.0.0.1:8080/v1/tools/web_search \
  -H "Authorization: Bearer $GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "rust async runtime comparison",
    "count": 5
  }'
```

Per-request filtering supports `include_domains`, `exclude_domains`, `freshness`, `country`, `search_lang`, and `safesearch`. The gateway clamps requested result count to the configured maximum while over-fetching from Brave and trimming to the requested count. Host diversity is enforced via `max_per_host`, and tracking query parameters are stripped from result URLs by default.

All inputs are validated at the boundary. Output is bounded and sanitized: titles, descriptions, URLs, snippets, and age strings are length-capped and control-character-stripped. Non-HTTPS URLs are dropped.

## Authentication and Security

Every `/v1/*` and `/admin/*` request requires a bearer token, compared in constant time. The caller's token is never forwarded to upstream backends.

The gateway holds provider API keys and the Brave Search credential server-side, so clients never need direct access to upstream credentials.

Additional security measures for local model operations:

- Each llama-server child gets a cryptographically random per-attempt bearer token, preventing adjacent host processes from hijacking the local endpoint
- Artifact cache directories enforce owner-private permissions
- Archive extraction rejects path-traversal entries

## Health and Observability

An unauthenticated `GET /health` endpoint returns 200 whenever the gateway is serving - suitable for load balancer liveness probes. The gateway emits structured tracing output, with interactive progress bars on TTY stderr and structured log lines in non-TTY environments.

## Library API

The `promptforge-gateway` crate exposes a library API for programmatic assembly. Build a `Gateway` from a `Config` and `ProfilesContext`, then serve on a caller-owned `TcpListener` with a custom shutdown signal. This is the integration-testing seam: bind to port 0, get the assigned address, run your test client, then signal shutdown.

*2026-08-10 21:24 - claude-opus-4-6-medium-thinking*
