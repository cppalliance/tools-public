# Single-Crate SPA Servers in Rust: What the Field Does and What to Steal

Report type: evaluation / review. It judges the promptforge-ws-server crate (single axum crate serving an embedded TypeScript SPA via rust-embed) against ten popular Rust codebases sharing the same technique, surveyed across five domains (file/media, dashboards, dev tools, chat/LLM UIs, networking), and prescribes fixes in severity order. It is the third study in a series: compare-ui-stack-human-idioms covered the frontend and shell, compare-server-delivery-human-idioms covered server delivery. Where a finding here merely repeats a recommendation from those two, it is recorded as a confirmation, not restated as new.

## Executive summary

The verdict: the crate has two genuine holes that no amount of decomposition planning excuses deferring - any webpage the user visits can talk to the localhost server, and a crash mid-write can truncate a user's workspace file - and both fixes are small, certain, and independent of the pending chat_ws.rs refactor. Below those two, the field supplies precise upgrades for the gateway path (deadlines, backoff discipline, streaming-delta conformance) and confirms, with sharper templates, the decomposition and test-harness program the prior server report already prescribed. The survey also validated more of the subject than it indicted: broadcast-lag handling, drop-guard cancellation, the shutdown watchdog, path-traversal defenses, and the build scheme all match or beat the field. The ten references ran the full spectrum from a 5,138-line god module to a codebase with no file over 26KB, and the god modules appeared in human and AI-assisted projects alike; the lesson is the ratchet, not the author.

### Key findings

1. **Critical: the server accepts cross-site requests; sql-studio's same-day security sweep shows the fix.** A `Sec-Fetch-Site` filter, an Origin allowlist on WebSocket upgrade, and a JSON content-type guard close CSRF and DNS-rebinding against a localhost tool. Confidence: high.
2. **Critical: workspace.rs writes files non-atomically while menu.rs in the same crate already does temp+rename; RustyFile shows the full pattern.** Temp file, `sync_data()`, rename, orphan sweep at startup. Confidence: high.
3. **The crate has no request timeouts anywhere; RustyFile, rqbit, and scanopy converge on tiered deadlines.** The gateway HTTP client is the live hang risk. Confidence: high.
4. **aichat's delta decoder handles three reasoning-channel transitions and two tool-call quirks our gateway should be tested against.** Small, certain conformance fixes. Confidence: high.
5. **rqbit's backoff resets on useful work, not on connect - the anti-flap detail for gateway.rs.** Jittered exponential with an exhaustion budget. Confidence: high.
6. **Progress belongs in atomics sampled at fixed rate, and events should not be produced when nobody listens.** rqbit and taxy converge independently. Confidence: high.
7. **scanopy generates its TypeScript error tables and API types from the Rust enums - the concrete mechanism for the wire-type codegen the UI report recommended at medium confidence.** Upgraded to high: two studies now want it and one shows how. Confidence: high.
8. **The decomposition program from the prior server report is confirmed by three more references, and mistral.rs supplies the missing template: a generic Stream-implementing relay core with session logic as callbacks.** Confirmation with new detail. Confidence: high.
9. **cratery's in-crate application-layer tests with mocked services add the missing middle layer to the prior report's harness plan; sql-studio at 3,685 stars has zero tests and paid with a five-security-fix day.** Confirmation with new detail. Confidence: high.
10. **mistral.rs's three-way stream-end taxonomy (Completed, Error, ClientDisconnected) is the cheap diagnostic our WS teardown concerns need.** Ride it on the chat_ws.rs decomposition. Confidence: medium-high.

## Method

Five parallel researchers each surveyed one domain of Rust projects serving their own SPA from a single crate, rejected candidates that broke the pattern (workspaces, server-rendered templates, separate UI repos), and analyzed two survivors per domain from shallow clones with file-and-line citations, characterizing authorship from commit history and repo artifacts. This consolidation merged duplicate findings across the five surveys, deduplicated against the two prior sibling studies (2026-08-26 UI stack, 2026-08-27 server delivery), and ranked by severity and certainty: a small fix with high certainty outranks a large idea with medium certainty. Citations below are file:line into each project's clone at survey date (2026-08-27); they are carried verbatim from the domain surveys and were not independently re-verified in this consolidation pass.

## The ten references

| Project | Stars | Domain | Authorship character |
|---|---|---|---|
| mistral.rs | 7,632 | chat/LLM UI | Heavily AI-assisted (CLAUDE.md, AGENTS.md, CodeRabbit); real test discipline, ~110 inline tests |
| aichat | ~10,400 | chat/LLM UI | Single human maintainer, terse commits, thin tests except property-tested stream parser |
| scanopy | 5,596 | dashboards/monitoring | Effectively one author; no AI trailers but rationale-dense comments; unknown-leaning-assisted under review |
| sql-studio | 3,685 | dev tools | Human solo (frectonz); conventional commits, one batch-push day |
| Parseable | 2,447 | dashboards/observability | Multiple human contributors, no AI markers |
| rqbit | 1,711 | networking (torrent) | Human, maintainer plus community PRs, terse incremental commits |
| Urocissa | 294 | file/media gallery | Single author, AI-agent-assisted (AGENTS.md, .opencode), 30+ releases |
| taxy | 201 | networking (reverse proxy) | Human solo, changelog-driven small commits, dormant since 2025 |
| cratery | 183 | dev tools (cargo registry) | Human corporate (Cénotélie), hand-scale refactor commits |
| RustyFile | 7 | file manager | Five squashed mega-commits, the shape of AI-batch development; high internal quality |

## Detailed findings, ranked by severity and payoff

### Finding 1 (Critical): block cross-site requests to the localhost server

sql-studio shipped this on 2026-08-26 as part of a five-fix security day (commit 0009ac0): a `same_site()` filter rejecting any request carrying `Sec-Fetch-Site: cross-site` across the whole API (main.rs:5403-5413, applied at 5479), plus a `json_content_type()` guard requiring `application/json` on POST bodies (main.rs:5415-5431). Together these defeat CSRF and DNS-rebinding against a localhost server. A grep of promptforge-ws-server finds no origin or Sec-Fetch checks at all: the chat and voice WebSockets and the workspace write endpoints are reachable by any webpage the user has open. WebSocket upgrades bypass Sec-Fetch in older browsers, so an explicit Origin allowlist on WS upgrade is needed as well. Fold in the adjacent input-hygiene item from the same sweep: URL-decode path parameters before use (`decode_name`, main.rs:5518-5522; commit 29bb755), which applies directly to our workspace path params.

Fix: one middleware layer (Sec-Fetch-Site filter plus content-type guard) on the API router, an Origin allowlist in both WS upgrade handlers, and URL-decoding on workspace path params. Confidence: high - small, mechanical, and the threat model (a browser on the same machine) is exactly ours.

### Finding 2 (Critical): atomic workspace writes with orphan cleanup

Our `workspace.rs:312` does a bare `fs::write`; a crash mid-write truncates the user's file. `menu.rs:463` in the same crate already writes temp-then-rename - classic scaffolding duplication where the same crate holds both the right and the wrong pattern. RustyFile shows the complete idiom: write to `.rustyfile_tmp_<uuid>` with mode 0o600, `sync_data()`, then `rename`, removing the temp on rename failure (src/services/file_ops.rs:266-299), with a startup sweep for orphaned temp files (src/main.rs:287-313).

Fix: extract one atomic-write helper, use it from both workspace.rs and menu.rs, add the startup orphan sweep. Confidence: high - the failure mode is data loss on the user's own files, and half the fix already exists in-crate.

### Finding 3 (High): deadlines everywhere - the crate has no request timeouts

Three references converge. RustyFile layers a 30s default timeout with 300s overrides for long routes and no timeout on SSE, composed by merging separately-layered sub-routers (src/api/mod.rs:33-36,205-229). rqbit adds a per-request `Timeout<const DEFAULT_MS, const MAX_MS>` axum extractor reading `?timeout_ms=` or a header, clamped to a server cap (librqbit/src/http_api/timeout.rs:10-49). scanopy bounds every readiness-path probe with an explicit `tokio::time::timeout` shorter than the caller's patience, and keeps the liveness endpoint dependency-free (bin/server.rs:427-485, rationale at 448-451). promptforge-ws-server has no TimeoutLayer at all; the gateway.rs HTTP calls to the LLM gateway are the analogous hang risk.

Fix: a default TimeoutLayer on the router with per-group overrides (none on the WS/SSE paths), an explicit timeout on gateway HTTP calls, and bounded probes in heartbeat.rs. Confidence: high - three independent references, small cost, and the hang risk is live today.

### Finding 4 (High): streaming-delta conformance fixes for the gateway decoder

aichat's OpenAI decoder (src/client/openai.rs:100-198) handles cases our gateway should be tested against: it accepts both `delta.reasoning_content` and `delta.reasoning` (openai.rs:138-140); the reasoning-to-content transition closes the think block (openai.rs:133-136); the reasoning-to-tool-call transition also closes it (openai.rs:156-159) - the case that is easy to miss when a model goes straight from thinking to a tool call; and empty-string deltas are filtered before state transitions (openai.rs:131,141) so the common `content: ""` role-announcement chunk cannot prematurely close a reasoning block. Its tool-call accumulation keys identity on `"{id}/{index}"` with a length-monotonicity check (openai.rs:160-161), handles providers that resend the full function name each delta versus fragment-senders (openai.rs:180-186), defaults empty accumulated arguments to `"{}"` (openai.rs:113-115), and flushes a trailing call on `[DONE]` (openai.rs:111-126). aichat's test technique transfers too: split input at random byte offsets, including mid-UTF-8-codepoint (src/client/stream.rs:151-165, 248-296).

Fix: audit gateway.rs against each transition, add the missing guards, and adopt the random-split test technique for the SSE delta decoder. Confidence: high - each item is a small, testable conformance fix against known provider behavior.

### Finding 5 (High): backoff that resets on useful work, not on connect

rqbit's upstream flap handling is the anti-flap discipline for gateway.rs and heartbeat.rs: `backon::ExponentialBuilder` with min 10s, factor 6, jitter, 1h max delay, and a 24h total-delay budget instead of an attempt cap (librqbit/src/torrent_state/live/peer/stats/atomic.rs:52-61); reconnect scheduled by `backoff.next()`, with the peer dropped entirely when the budget exhausts (torrent_state/live/mod.rs:1348-1407); and the load-bearing detail - backoff resets on a successfully verified piece, not merely on connect (live/mod.rs:1956), so an upstream that connects but never delivers keeps escalating. The companion shape is an explicit connection state machine (`Queued/Connecting/Live/Dead/NotNeeded`, diagram at live/mod.rs:27-33) with duplicate connections rejected by state (live/peer/mod.rs:210-214) and all transitions routed through aggregate counters so UI totals cannot drift.

Fix: in gateway reconnect logic, reset backoff only on a delivered token or successful completion; add jitter and a total budget. Adopt the enum-plus-counters shape if gateway liveness is tracked as ad-hoc booleans. Confidence: high on the reset rule and jitter; medium on the state-machine refactor (ride it on the decomposition).

### Finding 6 (High): progress via atomics plus a fixed-rate sampler, and listener-gated production

Two independent codebases avoid per-event progress pushes. rqbit's producers only bump atomic counters; a single 1Hz task feeds windowed speed estimators (librqbit/src/session_stats/mod.rs:49-72), and initial-check progress is a plain `AtomicU64` the API polls (torrent_state/initializing.rs:33,59-62,166) - there is no progress event stream to flood. Both rqbit and taxy also gate production on listeners: taxy counts SSE subscribers and disables broadcast event generation when the last one drops (taxy/src/admin/mod.rs:220-266), and rqbit gates its JSON log-formatting layer on `receiver_count() > 0` (librqbit/src/tracing_subscriber_config_utils.rs:94-97), so the cost is zero with no client connected.

Fix: in provision.rs, producers write atomics and one sampler emits to the WebSocket at fixed cadence; audit whether gateway heartbeats and provision progress are computed with no session connected, and gate them. The related scanopy patterns - invalidation-signal push for snapshot state (topology/handlers.rs:583-615) and per-subscriber debounce windows (events/traits.rs:486-554, which are unbounded as shipped, see the messes) - are deferred variants for menu/catalog state, not immediate work. Confidence: high on atomics-plus-sampler and listener gating; medium on the deferred variants.

### Finding 7 (High): generate the TypeScript wire types from the Rust enums

The UI-stack report recommended killing the hand-mirrored TS message types at medium confidence; scanopy supplies the mechanism and upgrades it. A dedicated bin iterates the Rust `ErrorCode` enum and writes `ui/src/lib/generated/error-codes.ts` plus i18n message templates (backend/src/bin/generate-error-codes.rs:13-46), and API types are generated from the utoipa OpenAPI spec via a cargo test wired into `make generate-types` (Makefile:353,358). The Rust type is the single source of truth; the UI copy is a build artifact. Our protocol.rs (27KB of wire types plus the delivery contract) is hand-mirrored in TypeScript - exactly the scaffolding duplication per-diff review cannot see.

Fix: a `generate-types` bin iterating our protocol enums, run in build or CI with a diff check. Ride it on the protocol-module extraction the prior reports already scheduled, so the types move once. Confidence: high - two studies converge on the deficit and one reference shows a contained retrofit.

### Finding 8 (High, confirmation): the chat_ws.rs decomposition is re-confirmed, and mistral.rs supplies the template

The prior server report prescribed the split (Rustpad loop, thin routes, per-feature files); this survey adds three independent confirmations and the missing carve-out template. mistral.rs splits exactly what chat_ws.rs fuses: persistence in ui/chat.rs (3.5KB), REST handlers in ui/handlers/api.rs, wire conversion in chat_completion.rs, and a generic `BaseStreamer<R, C, D>` relay core with a `DoneState { Running, SendingDone, Done }` machine making the done-then-close sequencing explicit (server-core/src/streaming.rs:129-159); four protocol frontends each implement only `poll_next` over that shared core. cratery proves the thin-handler split works inside one crate: every handler is 1-3 lines delegating to an `Application` layer that re-checks auth itself (routes.rs:466,483-484, state at 57-64). taxy shows the flattest field result - no file over 26KB, one tiny file per API resource - via a type-erased RPC command pattern (taxy/src/admin/mod.rs:333-358). The counter-evidence is equally useful: cratery's application.rs grew to 63KB, proving the layer split relocates rather than eliminates god-module risk; the decomposition needs the size ratchet the prior report already mandated.

Fix: when decomposing chat_ws.rs, carve the token-relay loop out as a Stream-implementing struct with session logic reduced to callbacks, per the mistral.rs shape. Confidence: high on the direction (three more references converge); the template itself is guidance for the already-planned refactor, not new scope.

### Finding 9 (High, confirmation): application-layer tests with mocks, plus the spawn harness

The prior server report scheduled a typed WS client and spawn fixture. Two references add the layers around it. cratery tests business logic in-crate with mocked services and zero HTTP setup: `async_test(|application, admin_auth| ...)` exercises auth invariants directly (src/tests/security.rs:36-133, module wiring at main.rs:35-36) - the layout that would make menu/workspace/gateway logic testable without sockets. RustyFile's `TestApp::spawn()` builds the real router on port 0 with tempdir roots and exposes the DB pool for state manipulation (tests/helpers/mod.rs:28-100), backing nine black-box integration files including one asserting embedded-asset behavior. The cautionary tale is sql-studio: 3,685 stars, zero tests, five security fixes in one day. Confidence: high; this extends an already-accepted plan rather than opening a new one.

### Finding 10 (Medium-high): stream end-state taxonomy and early-error handshake

mistral.rs wraps the SSE body in an `ObservedBody` that marks normal and error endings in `poll_frame` (metrics.rs:522-540) and fires `ClientDisconnected` from `Drop` only if the body never ended (metrics.rs:551-557), feeding a three-way `StreamEnd { Completed, Error, ClientDisconnected }` outcome counter (metrics.rs:403-427) plus TTFT and inter-token-latency histograms guarded so control events do not pollute ITL (streaming.rs:80-94), with a test enforcing the taxonomy (metrics.rs:1007-1017). Our status machinery cannot currently distinguish "client vanished mid-stream" from "stream completed". Two adjacent gateway-lifecycle items ride along: aichat's first-event handshake returns a real HTTP error when the first pipeline event is an error instead of a 200 plus SSE-framed error (src/serve.rs:410-414, 619-624), with mistral.rs showing the complementary mid-stream form (OpenAI-shaped `data:` error events, streaming.rs:105-123) - early upstream failures like auth or model-not-found should surface as protocol-level errors, not tokens; and mistral.rs treats relay-channel closure as authoritative cancellation checked at every pipeline stage (engine/add_request.rs:137 et al., default_scheduler.rs:332-338) - we have explicit cancel frames, but auditing that dropping the per-chat future truly closes everything upstream observes is a cheap belt-and-suspenders pass. Confidence: medium-high; diagnostic value is certain, and all three fit naturally into the decomposition.

## Confirmed already right

Patterns the survey validated in the subject, each against a named reference:

- **Broadcast lag handling.** chat_ws.rs:164-197 handles `RecvError::Lagged` on all three receivers with a test; scanopy does the same (discovery/handlers.rs:647-674), taxy treats Lagged as a logged warning (admin/mod.rs:201-215).
- **Drop-guard cancellation of upstream on client disconnect.** aichat's pipeline keeps draining the provider after the browser is gone (serve.rs:336,341,344); our drop-guard design is strictly better. Explicit cancel frames plus closure-observation is the right combination for a multiplexed WS.
- **Shutdown.** scanopy has no graceful shutdown at all (bin/server.rs:492-500), rqbit cancels then sleeps a flat 1s with an apologetic comment (session.rs:1072-1074); our serve.rs watchdog is ahead of both. RustyFile's uniform CancellationToken across all seven background loops (src/main.rs:188-251) matches our shape.
- **Path traversal defenses.** cratery's dev-mode asset serving joins raw client path segments with no `..` rejection (routes.rs:84-87); our lexical-check plus canonicalize plus prefix-match in workspace.rs is the right design. One action item: verify the debug disk-serving path gives the same guarantee as the release embed path.
- **Asset embedding and build.** rqbit's npm-in-build.rs with `rerun-if-changed` behind a cargo feature (librqbit/build.rs:42-55) is equivalent to our esbuild-in-build.rs; the feature gate is the one adoptable extra, and the prior server report already covers gating for the gateway merge. Our rust-embed fallback beats rqbit's four hardcoded `include_str!` routes (http_api/webui.rs:3-41).
- **Composition root.** scanopy builds everything in one 655-line entry file; our app.rs plus serve.rs split is at least as clean.
- **Standing decision re-tested and upheld.** Two surveys re-recommend Cache-Control headers on embedded assets (RustyFile frontend.rs:54-75; taxy static_file.rs:12-73 adds ETag/304 and pre-gzipped embeds). The server-delivery report's 2026-08-27 decision stands: the workshop UI is a windowed SPA served from the local process, nothing is cacheable by design, and filenames are unhashed. The field convergence is noted; the rationale for rejection is unchanged. Likewise RustyFile's SPA-fallback extension heuristic (frontend.rs:22-36) is not applicable: assets.rs registers explicit per-file routes with no catch-all.

## Messes observed in the field - do not copy

- **God modules are author-agnostic.** Urocissa's tree/state.rs is 5,138 lines; human-solo sql-studio's main.rs is 5,665 lines with a 9-variant enum dispatched by ~150 lines of hand-written match boilerplate (main.rs:365-480); human rqbit carries a 76.7KB live/mod.rs whose two-lock deadlock discipline lives in a prose comment (live/mod.rs:35-39); AI-assisted mistral.rs's chat_completion.rs is drifting the same way at 62KB. And cratery's 63KB application.rs shows the layer split relocating the risk. The ratchet from the prior report is the answer; per-diff review demonstrably does not catch accretion (sql-studio's own history proves it).
- **Hand-rolled protocol framing.** cratery's custom SSE body writes the `id:` line from the wrong field (utils/axum/sse.rs:45-47) - a silent bug a library would have prevented. Parseable's SSE broadcaster has a read-lock/write-lock race that silently drops clients registered between the locks (src/sse/mod.rs:80-104) and awaits per-client sends so one slow consumer stretches every broadcast.
- **Unbounded buffering.** aichat runs unbounded channels end to end with no backpressure (serve.rs:324,327); scanopy's debounce buffers grow without limit if a subscriber is slower than its window (events/traits.rs:501,513-533) - cap them if adopting the pattern; mistral.rs's 10,000-message bound is backpressure in name only.
- **Side effects and panics in the wrong places.** Urocissa fires a Discord notification inside the HTTP error responder (public/error.rs:152) and `expect()`s on config load (router/builder.rs:56); rqbit keeps a test hook `cfg!(feature = "_disable_reconnect_test")` inside the production reconnect scheduler (live/mod.rs:1354) and compares passwords non-constant-time with an open TODO (http_api/mod.rs:73); mistral.rs encodes cross-module invariants as `unreachable!` panics with no enforcing test (chat_completion.rs:492-499).
- **Copy-paste at route scale.** Urocissa has 20+ copy-pasted per-route index.html handlers (router/get/get_page.rs:101-243); scanopy has ten near-identical hand-rolled interval loops in main despite a scheduler crate in its dependency list (bin/server.rs:103-231); sql-studio string-replaces every asset body per request (main.rs:291-296).
- **Miscellany.** taxy funnels all admin state through one hot `Arc<Mutex<Data>>` (admin/mod.rs:326-330); scanopy compiles 194.7KB of demo seed data into the server module tree; aichat polls its abort signal every 25ms and mints collision-prone nanosecond completion IDs (serve.rs:632-635).

## Recommended execution order

**Immediate fixes** (independent of the refactor, do now):

1. Cross-site blocking: Sec-Fetch-Site filter, WS Origin allowlist, JSON content-type guard, URL-decode workspace path params (Finding 1).
2. Atomic write helper shared by workspace.rs and menu.rs, plus the startup orphan sweep (Finding 2).
3. TimeoutLayer tiers on the router, an explicit gateway HTTP timeout, bounded heartbeat probes (Finding 3).
4. Gateway delta-decoder conformance audit and fixes, with random-split tests (Finding 4).
5. Backoff reset-on-useful-work, jitter, and a total budget in gateway reconnect (Finding 5, first half).
6. Verify the debug disk-serving path enforces the same traversal guarantee as the release embed path (from the cratery counter-example).

**Refactor-riders** (fold into the already-planned chat_ws.rs decomposition, so files move once):

7. Carve the token relay as a generic Stream core with callbacks, per the mistral.rs template (Finding 8).
8. Stream end-state taxonomy, first-event error handshake, and the channel-closure cancellation audit (Finding 10).
9. Progress atomics plus fixed-rate sampler in provision.rs, and listener-gating on heartbeat/progress production (Finding 6).
10. Rust-to-TS codegen bin when the protocol module is extracted (Finding 7).
11. Application-layer test module with mocks, alongside the planned spawn harness (Finding 9).
12. Gateway liveness as an explicit state enum with aggregate counters (Finding 5, second half).
13. 5xx body redaction with server-side detail logging (RustyFile error.rs:158-193), using rqbit's 219-line api_error.rs as the shrink benchmark for our 18KB error.rs; this rides the two-error split the prior report scheduled.

**Deferred ideas** (recorded, not scheduled):

- Invalidation-signal push and capped per-subscriber debounce for menu/catalog snapshot state (scanopy F1/F2).
- A typed event-bus abstraction collapsing the status/menu/catalog channel triplication (scanopy bus.rs:19-30); revisit after the decomposition shows what remains.
- Runtime isolation for whisper inference and model downloads off the request runtime (Urocissa main.rs:61-66).
- Write-behind drain-with-deadline for per-profile persistence (Urocissa write_behind.rs:21-118).
- Digest-pinned download with checksum cache for provision.rs model fetches (Parseable build.rs:67-158).
- UI-triggered shutdown endpoint gated by a flag (sql-studio main.rs:212-226).
- cratery's counter-heartbeat plus select_all teardown as an alternative shape if heartbeat.rs is ever rewritten (routes.rs:528-639).
- debug-embed parity so tests exercise the embed path (scanopy Cargo.toml:63-68); weigh against the disk-in-debug iteration speed the prior reports endorsed.
- Startup phase timing macro (Urocissa performance/mod.rs:6-11); message tree with parent_id/tail if message editing ever lands (mistral.rs ui/chat.rs:34-49).

## Sources

- Domain surveys of 2026-08-27 covering ten projects: Urocissa (294 stars), RustyFile (7), scanopy (5,596), Parseable (2,447), sql-studio (3,685), cratery (183), mistral.rs (7,632), aichat (~10,400), rqbit (1,711), taxy (201). Shallow clones analyzed 2026-08-27; star counts from GitHub the same day. Citations are file:line at each clone's HEAD on that date.
- Prior sibling studies deduplicated against: compare-ui-stack-human-idioms (2026-08-26) and compare-server-delivery-human-idioms (2026-08-27).
- Subject: promptforge-ws-server, profiled in the prior studies; this consolidation adds no new self-profile.

*2026-08-27 21:15 - claude-fable-5-thinking*
