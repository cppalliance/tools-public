# PromptForge Gateway

PromptForge Gateway is a standalone Rust binary that sits between your callers and any LLM backend. Point any OpenAI SDK or curl command at it by changing one base URL, and the gateway handles routing, concurrency, local model hosting, and web search - all from a single TOML file. Models are named by capability (`reasoning-large`, not `gpt-4o`), so the same prompt works across deployments while the backing vendor changes in one config line. This guide walks you through every feature, from first request to full production config.

## Drop-In Compatibility

Send a chat completion to the gateway exactly the way you would send one to OpenAI:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Authorization: Bearer $GATEWAY_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "reasoning-large",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7,
    "max_tokens": 256
  }'
```

Change only the base URL. Every sampling parameter - `temperature`, `max_tokens`, and any future parameter the gateway has never seen - passes through to the backend untouched. No gateway release is needed when a provider adds new parameters.

List every model in the active profile:

```bash
curl http://127.0.0.1:8080/v1/models \
  -H "Authorization: Bearer $GATEWAY_KEY"
```

All data-bearing routes require a bearer token. Credentials are compared in constant time to prevent timing attacks. A separate health endpoint needs no credentials:

```bash
curl http://127.0.0.1:8080/health
```

Load balancers and monitors use `/health` to verify the gateway is running.

## Configuration

### Minimal working config

```toml
[server]
bind = "127.0.0.1:8080"
key = "${GATEWAY_KEY}"

[[endpoint]]
id = "openai-prod"
protocol = "openai"
base_url = "https://api.openai.com"
api_key = "${OPENAI_API_KEY}"

[[model]]
name = "reasoning-large"
description = "GPT-4o for reasoning tasks"
context = 128000
thinking = "switchable"
upstream = "gpt-4o"
endpoints = ["openai-prod"]
default_max_tokens = 4096
```

Start the gateway with a direct path:

```bash
promptforge-gateway serve gateway.toml
```

Or with a named profile from a profiles directory:

```bash
promptforge-gateway serve --profiles-dir ./profiles --profile analytical
```

### Environment variables

Any TOML string value can reference environment variables with `${VAR}` syntax. The gateway fails at boot if a referenced variable is missing. For a literal dollar sign, write `$$`. Interpolation runs after TOML parsing, so it cannot corrupt TOML structure.

### Profile inheritance

Profiles support `include` directives for composable configs. A child profile inherits everything from its parents, with depth-first merge:

```toml
include = ["base.toml"]

[server]
key = "${STAGING_KEY}"

[[model]]
name = "reasoning-large"
upstream = "gpt-4o-mini"
description = "Budget reasoning for staging"
context = 128000
endpoints = ["openai-prod"]
```

Arrays append; entries with the same `id` or `name` replace the inherited version. Device lane entries in a child attach to an inherited device without redeclaring the whole device. Scalar values like the server key override cleanly.

Include chains are limited to 16 levels deep. Circular includes are detected and rejected. Profile names are validated against path traversal - names like `../secrets` or `a/b` are rejected. Dotted names like `analysis.v2` are fine as long as they are a single path component.

### Validation

Unknown fields in any config section cause an immediate error, catching typos before the gateway starts. All validation runs at load time, so every error surfaces before the gateway accepts traffic. Merge errors produce file:line diagnostics showing exactly where the conflict is.

## Routing and Models

### Endpoints

Each backend gets an endpoint declaration with its own URL, credentials, and optional concurrency limit:

```toml
[[endpoint]]
id = "openai-prod"
protocol = "openai"
base_url = "https://api.openai.com"
api_key = "${OPENAI_API_KEY}"
concurrency = 10
```

### Model aliases

Models map a caller-facing name to a backend endpoint. The `upstream` field sets the model identifier sent to the provider:

```toml
[[model]]
name = "reasoning-large"
description = "GPT-4o for reasoning tasks"
context = 128000
thinking = "switchable"
upstream = "gpt-4o"
endpoints = ["openai-prod"]
default_max_tokens = 4096
```

Callers always request `reasoning-large`. When you switch providers, change `upstream` and `endpoints` - callers never know. Multiple models can route to different endpoints, each with its own URL and credentials.

### Thinking mode

Control whether a model uses thinking tokens with three settings:

- `"never"` - thinking tokens are suppressed
- `"always"` - thinking tokens are always used
- `"switchable"` - the caller controls per request

### Local and remote together

Local models merge into the same routing table as remote models. Callers address them through the same API. The gateway rejects duplicate model names across remote and local declarations - you get an error at config time, not at request time.

## Concurrency and Queuing

Set per-endpoint concurrency limits to prevent backend overload:

```toml
[[endpoint]]
id = "openai-prod"
protocol = "openai"
base_url = "https://api.openai.com"
api_key = "${OPENAI_API_KEY}"
concurrency = 10
```

Excess requests wait in a fair queue. Configure the queue globally:

```toml
[queue]
max_depth = 100
fair_scheduling = true
```

When the queue is full, callers receive a 503 with a machine-readable `queue_full` error code.

### Fair scheduling

Fair round-robin scheduling is on by default. Instead of pure FIFO, the gateway interleaves requests from different clients. Clients identify themselves with the `X-PromptForge-Client` header:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Authorization: Bearer $GATEWAY_KEY" \
  -H "X-PromptForge-Client: batch-pipeline" \
  -H "Content-Type: application/json" \
  -d '{"model": "reasoning-large", "messages": [{"role": "user", "content": "Hello"}]}'
```

The label is alphanumeric plus `-`, `_`, `.`, `:` (max 64 bytes). The gateway tracks up to 32 distinct client labels; excess labels fold into a shared default bucket. Cancelled requests automatically free their queue slot.

To run without concurrency limits, omit the `concurrency` setting on the endpoint.

## Local Models

### Simplest local model

Declare a local GGUF model and the gateway handles everything else:

```toml
[[local_model]]
name = "local-reasoning"
description = "Local Qwen model"
source = "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf"
sha256 = "abc123..."
context = 4096
gpu_layers = 99
```

On first use, the gateway downloads a pinned GPU-capable `llama-server` binary for your platform and downloads the GGUF file with SHA-256 verification. Six platform targets work out of the box: Windows x86_64 (Vulkan), Windows arm64 (CPU fallback), Linux x86_64 (Vulkan), Linux arm64 (Vulkan), macOS x86_64 (Metal), and macOS arm64 (Metal).

The gateway starts with no downloads or child processes when no local models are declared.

### Full local model config

```toml
[[local_model]]
name = "local-reasoning"
description = "Local Qwen model"
source = "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf"
sha256 = "abc123..."
context = 4096
gpu_layers = 99
flash_attention = true
cache_type_k = "q8_0"
cache_type_v = "q4_0"
n_predict = 2048
chat_template_file = "templates/tool-capable.jinja"
lane = "default"
```

Per-model tuning knobs:

- `context` - context window size
- `gpu_layers` - number of layers offloaded to GPU
- `flash_attention` - enable flash attention
- `cache_type_k` / `cache_type_v` - KV-cache quantization (defaults: q8_0 for K, q4_0 for V)
- `n_predict` - generation ceiling
- `chat_template_file` - external Jinja chat template, useful for quants that need a tool-capable override
- `lane` - assigns the model to a device lane for GPU concurrency control

### Device lanes

GPU concurrency for local models is managed through named lanes on device declarations:

```toml
[[device]]
id = "local-gpu"
kind = "local"

[[device.lane]]
id = "default"
concurrency = 1
```

Endpoint concurrency inherits from a shared device when the endpoint omits its own limit.

### Resilience

Each local model runs as a dedicated child process. If a child crashes, the gateway respawns it on the same port with one retry and a 3-second cooldown. When a port is already occupied, the gateway retries on a fresh port up to 4 times. Each child is authenticated with a per-attempt cryptographic bearer token so rogue localhost processes cannot impersonate it. The correct tool-calling dialect is detected automatically by probing the model after startup.

### Model files from disk

GGUF files can also be local filesystem paths with tilde expansion:

```toml
[[local_model]]
name = "local-small"
description = "Local model from disk"
source = "~/models/small.gguf"
sha256 = "def456..."
context = 2048
gpu_layers = 0
```

### Cache and Hugging Face

A custom cache directory replaces the default `~/.promptforge`:

```toml
[local]
cache_dir = "/mnt/fast-ssd/promptforge-cache"
```

Gated Hugging Face model downloads authenticate automatically using `HF_TOKEN` or `HUGGING_FACE_HUB_TOKEN` from the environment.

A long startup sequence with multiple local models can be interrupted with Ctrl-C for a clean exit.

## Artifact Security

When you declare remote model sources, the gateway enforces several protections automatically:

- **HTTPS required.** Remote sources must use HTTPS. HTTP URLs are rejected at config validation.
- **SHA-256 pins mandatory.** Every remote source must carry a SHA-256 pin. The gateway streams the download through SHA-256 comparison and reports both expected and actual digests on mismatch.
- **Cache lockdown.** The artifact cache directory is set to owner-only access on first use (chmod 0700 on Unix, icacls DACL restriction on Windows). World-readable cache directories trigger a privacy enforcement error with remediation instructions.
- **Symlink rejection.** Symlink and reparse-point components in cache paths are detected and rejected to prevent write-redirection attacks.
- **Atomic downloads.** Artifacts are staged then renamed, so a crash never leaves a half-written file. Stale staging files from interrupted downloads are cleaned up automatically.
- **Concurrent safety.** Multiple threads provisioning the same model converge on a single correct cached artifact via per-artifact file locks.
- **Archive safety.** Archive extraction rejects path traversal, symlinks, hardlinks, and device entries. Unix file permissions are preserved so `llama-server` retains its executable bit.
- **Tamper detection.** Post-install tampering of the extracted `llama-server` tree is detectable via a whole-tree digest.

Downloads are capped at 256 GiB and bounded by a 2-hour timeout. A live progress bar shows percentage, throughput, and ETA on TTY; structured log lines appear in non-interactive mode.

## Web Search

Web search is optional. Enable it by adding a `[tools.web_search]` section:

```toml
[tools.web_search]
provider = "brave"
api_key = "${BRAVE_API_KEY}"
```

Call the endpoint:

```bash
curl -X POST http://127.0.0.1:8080/v1/tools/web_search \
  -H "Authorization: Bearer $GATEWAY_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "Rust async runtime comparison"}'
```

Results come back in a structured format with `title`, `url`, `description`, `site_name`, and `extra_snippets` fields. The gateway proxies to Brave without exposing your search API key to callers. When web search is not configured, the endpoint returns 404.

### Filtering and defaults

Set server-wide defaults and per-request overrides:

```toml
[tools.web_search]
provider = "brave"
api_key = "${BRAVE_API_KEY}"
base_url = "https://api.search.brave.com"
default_count = 5
max_count = 20
max_per_host = 2
default_freshness = "pw"
default_safesearch = "moderate"
strip_tracking = true
```

Per-request fields override server defaults:

- `count` - number of results (clamped to `max_count`)
- `freshness` - `pd` (past day), `pw` (past week), `pm` (past month), `py` (past year), or `YYYY-MM-DDtoYYYY-MM-DD`
- `safesearch` - `off`, `moderate`, or `strict`
- `include_domains` / `exclude_domains` - domain filtering with subdomain matching (filtering on `example.com` also catches `sub.example.com`)
- `country` - 2-character country code
- `search_lang` - 2-3 character language code

The gateway over-fetches from Brave (up to 3x) to ensure enough candidates survive domain filtering and per-host caps. Text fields are sanitized by stripping control characters, collapsing whitespace, and decoding HTML entities. Non-navigable and over-length URLs cause the whole result to be dropped. Extra snippets are capped at 8 per result, 1024 characters each.

## Administration

### List profiles

```bash
curl http://127.0.0.1:8080/admin/profiles \
  -H "Authorization: Bearer $GATEWAY_KEY"
```

### Check status

```bash
curl http://127.0.0.1:8080/admin/status \
  -H "Authorization: Bearer $GATEWAY_KEY"
```

Returns the current profile name and active model list.

### Switch profiles at runtime

```bash
curl -X POST http://127.0.0.1:8080/admin/switch-profile \
  -H "Authorization: Bearer $GATEWAY_KEY" \
  -H "Content-Type: application/json" \
  -d '{"profile": "beta"}'
```

A profile switch rebuilds the routing table, stops old local model children (freeing VRAM), starts new ones, and atomically swaps all state. If the switch fails - for example, the profile does not exist - the current profile and catalog remain intact.

Admin routes use the same bearer token as the data routes.

### Graceful shutdown

The gateway shuts down gracefully on Ctrl-C, completing in-flight requests before exiting. Local model children are terminated within a 5-second deadline.

## Error Handling

Every error from the gateway uses the OpenAI error envelope format:

```json
{
  "error": {
    "message": "model 'nonexistent' not found",
    "type": "invalid_request_error",
    "code": "model_not_found"
  }
}
```

Unmodified SDKs surface gateway errors as their own error types. Common error codes:

| Situation | HTTP Status | `code` |
|---|---|---|
| Model not found | 404 | `model_not_found` |
| Bad or missing token | 401 | `unauthorized` |
| Queue full | 503 | `queue_full` |
| Profile not found | 404 | `profile_not_found` |

The gateway validates request boundaries at the wire level: empty model names, empty message arrays, unsupported roles, and malformed choice structures are rejected before reaching the backend.

API keys are protected from accidental logging by a redacting type that displays `redacted` in both debug and display output. Caller credentials are stripped before forwarding, so your bearer token never leaks to upstream providers.

Outbound calls have a 10-second connect timeout and a 120-second request timeout, so stalled backends cannot pin concurrency slots forever. Upstream response bodies are capped at 4 MB for success and 64 KB for error diagnostics.

## Constraints Reference

| Constraint | Limit |
|---|---|
| Include chain depth | 16 levels |
| Default queue depth | 100 per endpoint |
| Distinct client labels (fair scheduling) | 32 |
| Upstream response body (success) | 4 MB |
| Upstream response body (error) | 64 KB |
| Connect timeout | 10 seconds |
| Request timeout | 120 seconds |
| Artifact download size | 256 GiB |
| Artifact download timeout | 2 hours |
| Extra snippets per search result | 8 (1024 chars each) |
| Respawn cooldown | 3 seconds |
| Child termination deadline | 5 seconds |
| Port collision retries | 4 attempts |
| KV-cache defaults | K: q8_0, V: q4_0 |
