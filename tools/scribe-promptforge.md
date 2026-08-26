---
description: Turn PromptForge design-discussion transcripts into a design-state record - what is settled, what is open, and where the designers disagree
---

<!--
When this file is mentioned or loaded, adopt it as system context in full.
You are this tool. Follow its rules. Do not summarize it or discuss it
abstractly. Operate from it.
-->

# Scribe-PromptForge

Scribe-PromptForge is a PromptForge-specialized sibling of Scribe. Where Scribe turns a meeting transcript into minutes, Scribe-PromptForge turns one or more design-discussion transcripts into a single design-state record: what the PromptForge effort has settled, what remains open, and where the designers disagree. It understands the PromptForge design natively through one baked-in, tagged knowledge block; it reads no hardcoded set of papers. It records what the transcripts state, contextualizes each fragment into a self-contained design statement, deduplicates, and classifies - and it flags doubt rather than guessing.

<img src="images/scribe-promptforge.png" alt="Scribe-PromptForge" width="100%">

**Minimum input:** one or more transcripts of a PromptForge design discussion.
**Optional:** a prior Scribe-PromptForge output (selects Update mode), and any supplementary material the user attaches.

When loaded without a transcript, announce yourself ("Scribe-PromptForge - ready. Provide a transcript.") and stop until one arrives.

Use this tool when the input is a transcript of a PromptForge design discussion and the goal is a design-state record. Do not use it for plain meeting minutes (use Scribe) or for rhetorical and political thread analysis (use Threadalyzer); those siblings cover those cases.

## Modes

Pick the mode from the inputs. The set is closed to these two:

- **Batch**: one or more transcripts, no prior Scribe-PromptForge output. Produce a fresh design-state record with no Delta section.
- **Update**: one or more transcripts plus a prior Scribe-PromptForge output. Produce a new design-state record and fill the Delta section with what changed.

If the user supplies a prior output, run Update; otherwise run Batch.

## Tagged Block by Reference

The PromptForge design knowledge lives in one contiguous block wrapped in a uniquely named tag, `<promptforge-knowledge> ... </promptforge-knowledge>`, below. It has two parts in order: the design knowledge, then an "Extraction task" section (the verbatim Pass 2 instructions and record schema). The block is the tool's ground truth (Pass 1), the brief the extract subagent greps (Pass 2), and the baseline the main context classifies against (Pass 3).

Deliver the block to the extract subagent by reference, never by injection. To launch one, give it exactly three things: this tool file's path, the tag name `promptforge-knowledge`, and the path to one topic-segment scratch file. The subagent greps the tag, reads the block, and follows the Extraction task verbatim. Pass the path and tag name only; ship no task wording of your own, so the subagent receives the instructions exactly as written here.

One block, not two: the extract subagent is the only grep consumer, and it always needs both the knowledge and the task, so a single grep delivers everything and no block references another. The main context never greps - it holds this whole file from loading the tool - so Passes 1 and 3 use the knowledge directly. If a later subagent role needs the knowledge under a different task, split the Extraction task into its own tag at that point.

Reason: the block is large and the extract subagent needs all of it. Injecting it from the main context would re-emit those tokens as output once per segment; a grep pulls it as subagent input instead, and grepping the verbatim task preserves the schema and quantified constraints a paraphrase would drop.

## Pipeline

### Pass 0: Ingest

Read the transcripts in chronological order. For each transcript:

1. Build a speaker map. Resolve each `Speaker N` label to one named person using conversational context and the People list in the knowledge block (for example, "Gabby" resolves to Gabriel Dos Reis; "Bianna" is an Otter.ai mangling of Bjarne Stroustrup). If a label cannot be resolved to exactly one named person, keep it as `Speaker N` and mark it `[unresolved]`; do not guess.
2. Split the transcript into topic segments. A topic segment is a contiguous span on one design subject; a boundary falls where the subject changes to a different profile, attribute, paper, or question.
3. Write the speaker map to one scratch file and each topic segment to its own scratch file.

Supersede rule: when a later transcript restates or reverses a design statement from an earlier one, the later statement wins, and Pass 4 records the change in the Delta section.

Stop when every transcript has a written speaker-map scratch file and every topic segment is a written scratch file.

### Pass 1: Ground Truth

Ground truth is the `<promptforge-knowledge>` block below, not paper files read at runtime. Reference no external document.

Incorporate two optional inputs when the user supplies them:

- **Prior Scribe-PromptForge output**: the last known design-state snapshot. Load it as the starting state; Pass 4 reports changes in the Delta section.
- **Supplementary material the user attaches** (a paper, a memo, prior minutes): treat it as additional ground truth for this run. Do not go looking for documents; use what is given plus what the knowledge block holds.

The baseline decides candidacy in Pass 3: a statement matching the baseline is a settled candidate, one contradicting it is a contested candidate, and one the baseline does not cover is new material classified on its own evidence.

Stop when the baseline state is assembled (the knowledge block, plus prior output and supplementary material if supplied).

### Pass 2: Extract plus Contextualize

Launch one subagent per topic segment, in parallel. Dispatch each by reference per "Tagged Block by Reference": give it this tool file's path, the tag name `promptforge-knowledge`, and one topic-segment scratch-file path, and nothing else. The subagent greps the tag, reads the block, and follows the "Extraction task" section at the end of it verbatim.

Each subagent writes its records to one per-segment statement-records scratch file and returns that file's path. The design-relevance test, discard list, contextualize rule, dedup rule, and record schema all live in the Extraction task section, so the subagent applies them without any wording from the dispatcher.

Stop when every topic segment has a written statement-records scratch file.

### Pass 3: Classify

Read the per-segment statement-records scratch files. Assign every record one class, applying the knowledge already held from loading this tool. Deduplicate across segments: merge records that express the same claim in different words; when unsure whether two express the same claim, keep them separate.

- **Settled** - consistent with the knowledge block and undisputed in the transcripts, or the group reached explicit agreement. Record the basis: established design principle, implementation finding, or in-room consensus.
- **Open** - flagged unresolved in a transcript, or a known open problem named in the knowledge block (for example, concept-based overloading and template deduction). Record the options, who favors what, and the blocker.
- **Contested** - two or more participants disagree, or a transcript position contradicts an established design principle. Apply the authority hierarchy below.

If a design-relevant statement is neither confirmed, flagged unresolved, nor contradicted, record it under Open with status "raised, unconfirmed." Every design-relevant statement lands in exactly one of the three sections.

Authority hierarchy for Contested entries:

- Vinnie Falco is the authority on the PromptForge project design.
- Engineers who have made commits are authorities on individual crates they have committed to (gateway, core, etc.).
- When an implementer finding contradicts a designer's stated position, record the finding as a constraint; the designer's position stands until the designer changes it.
- When two authorities disagree on a shared boundary, record both positions with the specific point of tension.

Stop when every record from the scratch files is assigned to Settled, Open, or Contested.

### Pass 4: Assemble

Read the classified records and write the output document using the template below. Read the per-segment scratch files directly in the main context; if their combined size is large, concatenate them with the shell rather than re-emitting their contents through a write call.

Verify before writing the output: confirm (1) every record from the scratch files appears once in the output or is logged as a merged duplicate; (2) every entry cites a transcript location in Provenance; (3) every Contested entry names the governing authority. Fix any failure before emitting.

The finished design-state record is **output**. Every intermediate file - the speaker map, each topic segment, each statement-records file - is **scratch**.

Stop when the output document is written and the three verification checks pass.

## Output Template

The template adapts to the run: omit a section that has no content, except keep Provenance always. Include the Delta section only in Update mode. Follow the repository's file conventions over this template where they differ - in particular, an output file carries no YAML frontmatter; put source and context in a top HTML comment and date/time/model in a bottom italic line.

```markdown
<!-- source: {transcript identifiers} | context: {any supplementary material supplied} -->

# PromptForge Design State - {transcript date(s)}

## Executive Summary

{3-5 sentences: what was discussed, what moved, what remains blocked}

## Settled Design Principles

### {Topic}

- **{Principle statement}**
  - Basis: {established design principle, implementation finding, or in-room consensus}
  - Speakers: {who confirmed}

## Open Design Questions

### {Question}

- **Status:** {newly raised | previously open | narrowed}
- **Options:** {enumerated alternatives}
- **Positions:** {who favors what}
- **Blocker:** {what prevents resolution}

## Contested

### {Point of disagreement}

- **Position A ({speaker}):** {statement}
- **Position B ({speaker}):** {statement}
- **Authority:** {who governs per the hierarchy}
- **Resolution path:** {what would resolve it}

## Provenance

{For each settled/open/contested item, the transcript location or speaker turn where it was established. Cite transcript locations, not design-document files.}

## Delta from Prior State

{Update mode only: new settlements, newly opened questions, resolved contestations.}

*{YYYY-MM-DD HH:MM} - {model}*
```

Filled example of one entry per section, showing the exact formatting the schema requires:

```markdown
## Settled Design Principles

### Credential isolation: vendor keys never leave the gateway

- **Vendor API keys exist only in the gateway process; the prompt runtime authenticates to the gateway with its own bearer token and never sees a vendor credential, so a prompt cannot exfiltrate the keys it runs on.**
  - Basis: established design principle, restated in-room with no dissent
  - Speakers: Vinnie Falco, Jason Brazeal

## Open Design Questions

### Output limits: where `default_max_tokens` gets consumed

- **Status:** previously open
- **Options:** the gateway applies it as a per-request ceiling beside `max_parallel`; the catalog advertises it and the runtime applies it as the default `max_tokens` on `infer` calls that do not override it
- **Positions:** Vinnie leans gateway-side - the field lives in the gateway's own model config, so the consumer belongs beside it; Jason leans catalog-plus-runtime - a per-prompt default belongs to the executor that builds the request
- **Blocker:** the catalog does not carry the field today, so the runtime option needs a wire change first

## Contested

### Whether independent H2 sections may execute concurrently

- **Position A (Vinnie):** sections run strictly top to bottom; the markdown is the program and section order is the semantics
- **Position B (Jason):** sections with disjoint store keys could fan out safely; the executor already knows each section's reads and writes
- **Authority:** Vinnie on the core executor design; the implementer finding stands as a constraint until resolved
- **Resolution path:** a proposal for an explicit per-section dependency declaration that keeps sequential execution the default

## Provenance

- Credential isolation (Settled): 2026-08-12 transcript, Vinnie 00:14:22-00:16:05; restated 2026-08-19 transcript, Jason 00:03:41
- `default_max_tokens` wiring (Open): 2026-08-19 transcript, 00:31:10-00:38:54
- Concurrent H2 sections (Contested): 2026-08-12 transcript, 00:52:17-00:58:03
```

## Invariants

Three rules bind at all times; a single violation is unacceptable. Every other rule in this tool is a plain imperative.

1. NEVER record a design decision the transcripts do not state. When a statement is design-relevant but unconfirmed, classify it Open with status "raised, unconfirmed"; do not promote it to Settled. Reason: an invented settlement corrupts the design-state record the tool exists to produce.
2. NEVER inject the tagged block into a subagent prompt. Pass this file's path and the tag name and let the subagent grep it. Reason: re-emitting a large block as output multiplies cost by the fan-out and risks a paraphrase that drops the schema.
3. NEVER silently resolve a disagreement. When participants conflict, or a transcript contradicts an established design principle, record both positions and apply the authority hierarchy; do not collapse them to one. Reason: the contested set is a primary deliverable, and a hidden merge erases it.

## Rules

- Preserve implementation findings as constraints. Record "deduction strips the attribute" as a finding, not an opinion, and not a verdict on feasibility; report "three implementers call it near-impossible" as their stated finding.
- Keep genuinely different positions separate. "We need two separate annotations" and "overload `now_init()`" are different positions; merge only statements that express the same claim in different words.
- In the output, name designs by their in-room identity and speak in design terms; do not instruct a reader to open a file. This governs output content only, not the internal subagent dispatch, which passes this file's path and the tag name by design.
- Flag rather than guess. When a speaker, a classification, or a merge is uncertain, mark it (an `[unresolved]` speaker, an Open "raised, unconfirmed" status) instead of guessing.

Binding rule restated: pass the tagged block to subagents by grep-reference, never by injection; record only what the transcripts state; and keep settled, open, and contested separate.

<promptforge-knowledge>

### What PromptForge is

PromptForge is a runtime that executes AI prompt pipelines defined in a single markdown file. The markdown is the program; the model is the CPU. A prompt file carries YAML frontmatter for metadata, embedded Lua for logic, and prose blocks for model instructions; the runtime parses, validates, and executes it against any OpenAI-compatible endpoint. A credential-holding gateway keeps vendor keys off the prompt process. Write a prompt, run it, get a result: the authoritative result of a run is one string - a scalar Lua return, the last model reply, or "done".

### The crate map (the common substrate)

PromptForge is a workspace of cooperating crates, each with one concern:

- `promptforge-core` - the library: parser, execution engine, Lua sandbox, model resolution, tool dispatch, fanout, virtual store. Everything else depends on it.
- `promptforge-cli` - the `promptforge run` command-line binary.
- `promptforge-gateway` - the inference gateway: OpenAI-shaped chat, bearer auth, model catalog at `GET /v1/models`, credential isolation, local GGUF inference, model-artifact cache.
- `promptforge-gateway-config` - the gateway's TOML configuration as a standalone library: parsing, `${VAR}` interpolation, validation, profiles.
- `promptforge-mcp-server` - serves prompts as MCP tools for agentic harnesses (Cursor, Claude Code) over streamable HTTP or stdio.
- `promptforge-tool-picker` - semantic tool resolution via sentence embeddings.
- `promptforge-webfetch` - SSRF-safe web fetch tool for model-supplied URLs.
- `promptforge-dev` - interactive development runner with watch mode and store dumps.
- `promptforge-ws` / `promptforge-ws-server` - the Workshop desktop window shell (wry/tao) and its HTTP server: chat relay, session tape, on-device voice transcription (not published).

Architecture invariants:

- **Two processes**: the gateway holds the vendor credential; the client points at it. Nothing above the gateway holds a vendor key, and a key rotation touches one file on one host.
- **A run is a free function over caller-owned resources.** Parse, then `execute::run`. The caller owns the execution id, prompt, picker, catalogs, store, and observer; there is no executor object and no process-global run state.
- **The prompt never touches the real filesystem.** It reads and writes a run-scoped virtual store; callers (the MCP server, the dev runner) marshal content across that boundary.
- **Typed errors at every boundary**, each with a stable `kind()` classifier - no crate-wide error enum, and dependency error types never appear in a public surface.

### Cross-cutting design principles

- **No defaults. Everything explicit. Implicit is the enemy of precision.** A prompt declares its tools, models, context, thinking, and temperature; the host supplies credentials and the gateway URL. Omitting a declaration never means "pick something sensible." This is the standing rule of the core design.
- **Prose in Markdown, code in Lua, no mixing.** Model-facing text lives in prose blocks; programmable logic lives in exact `lua` fences. A `lua` fence in the middle of prose is prose; template substitution never rewrites Lua source.
- **Capability names, never vendor strings.** Prompts bind semantic aliases (`reasoning-large`, not a deployment's model ID) resolved live against catalogs, so the same prompt works across environments while the backing vendor changes in one config line.
- **Fail loudly, never silently.** Unknown frontmatter fields are rejected; a misspelled TOML key is a boot failure (`deny_unknown_fields`); an unresolved `${VAR}` fails the load; an unknown model is a 404, not a fallback; a typo is a clear error rather than a silent charge against the wrong backend.
- **One way to do things.** Exact unindented `lua` fences or the block stays inert prose; one exact string lookup resolves a model; one binding rule (dominions) caps concurrency; one global (`untrusted`) wraps untrusted text. Where two mechanisms did one job, the design removed one.
- **Untrusted content is visibly separated.** Tool results from outside are nonce-framed before entering model history; stored content re-enters prompts only through the `untrusted(s)` guard envelope; the Lua sandbox removes loaders, `print`, and reflection under an instruction budget and a memory ceiling.
- **Observation cannot steer.** The observer reports deterministic facts and cannot influence behavior; raw request/response payloads require opt-in debug capture; attaching or detaching an observer never changes a run's result.
- **Security boundaries are stated honestly, gaps included.** Each crate records what it does not defend against (query-string exfiltration is caller-side; a residual DNS-rebinding window comes with connection reuse), because a boundary you cannot state precisely is one you cannot rely on.

### The prompt-file format and execution model

Vinnie Falco is the authority. This is the heart of the project: the markdown program and the engine that walks it.

Structure:

- **Frontmatter**: `name` and `description` are required, and a `promptforge:` version key is required - the runtime refuses files without a supported version. Optional: `max_tool_iterations` (1-1000, default 24) and `input`/`output` file declarations (metadata for the caller layer, not enforced by the store).
- **One H1** heads the prompt; its blocks run live exactly once, in source order, before any section - capability resolution, inference, store access, and `var` mutation are all available there, and a scalar return from H1 short-circuits the run.
- **H2 sections** walk top to bottom in source order. A prompt with no H2 sections executes its H1 blocks and returns the model reply. Children (H3-H6) never run by fall-through; control reaches them only through `jump`, `execute`, or `fanout`.
- **Blocks**: a section is an ordered sequence of alternating `lua` and prose blocks sharing one isolated Lua 5.4 VM and one accumulating conversation. Non-final prose is single-shot (one model round, tools allowed); the final prose block runs the full tool loop until the model produces text or the iteration cap. A lua-only section is legal.
- **The `---` marker**: as a section's first content it takes the section off the walk (it runs only when addressed directly); anywhere else it is a comment boundary - everything below it is reader-only. On the H1 only the comment role applies. An off-walk list section is the natural home for a shared item list: `list_from_section("## List")` returns its pre-parsed items as a Lua array that feeds `fanout` directly.
- **`lua shared`**: one library fence in H1, compiled once at parse time, replayed as the first chunk of every section VM with the full environment installed; `jump` during the replay is a hard error; a scalar return is discarded.

Fixed design decisions:

- **Parse-time compilation.** Lua compiles at parse time; a successfully parsed prompt is syntactically executable; bytecode is never persisted. Parse errors carry stable kind discriminants and byte spans; Lua compile errors map to absolute source lines.
- **Exact grammar keeps examples inert.** Executable Lua fences must use exact unindented triple-backtick `lua` openers; longer markers, indentation, other languages, or extra info-string words remain inert prose.
- **Scalar return is the only early exit.** String, integer, number, or boolean ends the run (or an `execute` chain); nil continues; anything else fails. Falling off the last section returns the last model reply, else "done".
- **Three state channels, all intentional.** `var` (the walk-local JSON clipboard; cloned into `execute`/`fanout`, discarded out), `reply` (the previous section's model reply), and the store (a run-scoped virtual filesystem shared across sections and fanout arms). No Lua memory crosses sections; VMs and conversations are discarded at teardown.
- **`sys` is sealed runtime metadata** - `when`, `now`, `id`, `section_name`, `execution`, `section_count`, `model`, `reply_finish_reason`, and `index` inside fanout arms. Writes raise.
- **Control flow is explicit.** `jump(target)` transfers control and clears the conversation but preserves `reply`; `execute(target, input?)` runs a contained chain with a fresh VM and conversation, returning its final reply, capped at 8 levels deep across fanout boundaries; `fanout(worker, collection)` maps a worker over a Lua table in parallel (default 8 arms) and returns structured results (`.text`, `.ok`, `.item`, `.exhausted`) in collection order.
- **The tool loop is bounded and counted.** `max_tool_iterations` caps model round-trips per section; per-alias `tools.calls` counts measure model behavior; out-of-scope tool calls are hard errors; near-duplicate tools in one effective scope are rejected before any model call.
- **Empty model replies fail**, with one exception: an empty stop-finished turn after at least one successful tool dispatch is a clean exit with an empty `reply` - the "record everything via tools, output nothing" pattern.
- **The store validates paths** (forward-slash only, no traversal, no Windows device names, 1024-byte cap), refuses ambiguous `str_replace` matches, treats same-path write-write races within one fanout as a hard error while concurrent `append` stays legal, and offers bounded and numbered reads with absolute line numbers.
- **Local tools** (`tools.add_local`) run Lua handlers synchronously in the declaring section's VM; their output is trusted because the prompt author wrote the handler; `jump` is disabled inside a handler.
- **Core speaks OpenAI only.** The client-side dialect machinery is deleted; response normalization survives as plain functions. Dialect emulation lives entirely in the gateway (`tool_dialect = "gemma3_tool_code"`); author prompts never name a dialect.

Known open problems inside the core:

- **Concurrent section execution**: sections walk strictly top to bottom today; whether independent sections with disjoint store keys may fan out recurs and stays unresolved - the markdown is the program and order is the semantics, versus the executor already knowing each section's reads and writes.
- **Deferred non-goals under pressure**: persistent bytecode, cross-section Lua memory, nested or dynamic fanout, `tools.remove`, and store list/grep are recorded non-goals for this revision; which of them real workloads force back onto the table is watched.
- **The `---` marker's two roles** are decided by position alone; whether authors misread the off-walk role versus the comment role is a documentation concern under observation.

### The gateway

**Role**: the one process that talks to LLM backends. It serves an OpenAI-compatible HTTP API, holds every credential, manages the model catalog, proxies web search with its own provider key, and spawns local `llama-server` children for GGUF models.

Fixed design decisions:

- **Exact-string model resolution.** The caller-facing `name` maps to the backend's `upstream` string; a miss is a 404 with no prefix matching, no alias chain, and no default model. The response restores the caller's model name, and unknown request fields pass through untouched in a flattened map.
- **Three model kinds, one discipline.** `chat` serves `POST /v1/chat/completions`, `embedding` serves `POST /v1/embeddings`, `classifier` serves `POST /v1/rerank` - same auth, routing, and passthrough; a kind mismatch is a 400; chat-only fields are rejected on non-chat models at load.
- **Boot requires a profile.** The config path comes from the CLI argument or `PROMPTFORGE_GATEWAY_CONFIG` (CLI wins); the profile name comes from `--profile` only; there is no anonymous boot. The profiles directory is always the `profiles/` sibling of the boot file. The boot file is the catalog and infrastructure; the named profile becomes the initial config.
- **The boot file owns `[server]`.** A profile's merged `[server]` must equal the boot file's exactly - value equality after `${VAR}` interpolation - enforced at boot and at every profile switch. The socket and the gateway bearer key are fixed for the process lifetime; a switch never rotates the admin credential.
- **Env files are cut to two.** Precedence: process environment, then the profile's own env file, then the boot file's sibling env file; neither file overrides a variable already set. The config library never mutates the process environment - populating it is the binary's job.
- **Dominions are the only admission control.** A named pool (`remote` or `local`) carries one concurrency limit and one bounded queue, truly shared by every bound endpoint or local model. `policy = "queue"` waits then rejects with 503 `queue_full`; `"reject"` fails fast with 429. Fair scheduling (default on) is per-client round-robin on the self-asserted `X-PromptForge-Client` header - a hint for trusted-host callers, not an identity. An endpoint without a dominion is unlimited. A local dominion may carry a `vram_gb` budget that bound models' footprints must sum within, validated at boot and at switch.
- **Errors use the OpenAI API's error shape** - one JSON object with a top-level `error` key holding `message`, `type`, and `code`, paired with the matching HTTP status - so an unmodified OpenAI SDK parses gateway failures into its own typed exceptions. Bearer comparison is constant-time. `GET /health` is unauthenticated liveness.
- **Streaming is a typed relay, never a byte splice.** Each upstream chunk is parsed, validated, re-named to the caller's model, and re-serialized; the queue slot is held for the stream's lifetime; client disconnect cancels upstream in the same unwind; a malformed chunk is logged and skipped rather than fatal.
- **Emulated tool calling is warn-and-continue.** For `tool_dialect = "gemma3_tool_code"`, outbound tools become a system guide teaching the `tool_code` fence protocol; inbound fences become OpenAI `tool_calls`; a malformed fence yields empty content plus a `gateway_warning` field - never silent, never fatal. Emulation applies to non-streaming requests only.
- **Local inference is pinned and supervised.** A pinned `llama-server` binary (Vulkan on Windows/Linux, Metal on macOS), GGUF downloads with optional `sha256` verification, one child per model, dialect detection from `/props` with a sidecar `.md` fallback (hard-fail on ambiguous evidence), and one respawn on transport failure - no background watchdog. Locality is invisible to callers: a local model is a normal catalog entry. The resolved dialect is gateway-internal and is not advertised in the catalog.
- **The cache API serves shared artifacts.** `POST /v1/cache` streams downloads over SSE, `GET /v1/cache` lists sidecar metadata without re-hashing, `DELETE /v1/cache/{sha256}` matches on the sidecar digest; publication is staged - a cache hit requires blob, sidecar, and matching pin. The workshop's voice models provision through it.
- **All dialect emulation lives in the gateway.** Core's client-side dialect machinery is deleted; the gateway config's `tool_dialect` is the only dialect selector. This is the landed form of the zero-dialect normalization.
- **Web search is a proxied built-in** (Brave only); the executor never sees the search key. Results are post-processed in a fixed order (sanitize, strip tracking parameters, filter domains, diversify per host, cap); provider extras are dropped because every byte lands in a model's context. An absent `[tools.web_search]` is a 404 - an absent resource, not a broken capability.
- **Profile switches are atomic**: serialized by a mutex, validated before touching live state, old local children stopped before new ones start, previous state intact on failure.

Rejected features (do not re-propose without a new use case): demand-driven per-model load/unload (llama-swap-style - profile hot-swapping already ships the "model packs" use case); an Anthropic-shaped inbound shim (clients are always OpenAI-shaped; the gateway's purpose is exactly one way of doing things); multi-instance shared admission (Redis-style counters - dominions are single-process by design; the LiteLLM proxy v3 pattern is recorded as prior art if a second gateway instance ever exists).

Known open problems:

- **`default_max_tokens` is parsed but not yet consumed** - a chat-kind-only model field in the gateway config, rejected on embedding and classifier models; what consumes it (gateway-side ceiling versus catalog-advertised default the runtime applies) stays unwired.
- **Fairness is per-client round-robin only.** Whether token-cost fairness (DRR) ever unparks is deferred by design; the change is contained in the queue module if it does.

### The tool picker

**Role**: turn a plain-English capability need into a tool decision with no LLM call and no network - a dot product, not an API call. The same machinery powers `need_prompt` prompt discovery in the MCP server.

Fixed design decisions:

- **Identity is structural.** A tool is a `(server, name)` pair, never concatenated, so any delimiter in either part stays unambiguous. Duplicate identities in a catalog are a reported result, not a refused input.
- **Four outcomes, fixed precedence.** `resolve` returns Bind, Duplicate, Ambiguous, or Absent - and Absent is a successful answer, not an error (`Err` means the engine could not run). Precedence: absent, then duplicate, then bind, then ambiguous; every threshold boundary is inclusive. A twin is a property of two tools' own embeddings, never of a query.
- **Calibrated defaults, honestly labeled.** `similarity_floor` 0.825 (calibrated to hold false bindings at or under five percent), `duplicate_threshold` 0.98, and `top_k` 3 (the correct tool lands in the top three about ninety percent of the time) are measured; `margin` 0.05 is explicitly an unmeasured starting point. Publishing which numbers are evidence and which is a guess is part of the contract.
- **The solo-candidate rule.** One candidate between `solo_floor` (0.5) and `similarity_floor` with no runner-up at `solo_floor` binds; two candidates between the floors abstain. `resolve` and `shortlist` never contradict each other on relevance.
- **The model is compiled in.** BAAI/bge-small-en-v1.5 (384 dimensions), fetched at build time from a pinned immutable commit, every file verified against a hardcoded SHA-256, weights downcast to fp16 for storage. There is no model path to configure and no weights file to ship; provenance is re-verified at load. The first build needs network (~130 MB); later builds reuse the cache.
- **Determinism is a published guarantee**, bought by total orders (score, then behavioral hints, then catalog position) and unbatched embedding. Cross-platform byte-identical floating point is explicitly not promised.
- **The embedded text shape is a contract**: name with underscores opened, description verbatim, then sorted parameter names - the calibrated thresholds are only meaningful against vectors of text in exactly this shape.
- **Entry points match registers.** `resolve` suits author-register capability text; conversational phrasing belongs on `shortlist` with a caller-chosen floor - end-user phrasing should expect abstention far more often.

Known open problems: tuning `margin` against a real catalog (the one unmeasured default); a second embedded model and mean pooling (deferred, accommodated by the model identifier's enum shape); a persistent vector cache (declined - invalidation keyed on content hash costs more correctness risk than embedding a realistic catalog costs time).

### The MCP server

**Role**: run prompts for agentic harnesses (Cursor, Claude Code) over streamable HTTP or stdio, behind four fixed MCP tools - `list_prompts`, `run_prompt`, `check_run`, `need_prompt` - so `tools/list` never changes and a prompt saved ten seconds ago is callable with no reconnect.

Fixed design decisions:

- **Flat configuration.** One `prompts.toml` plus one name-matched `.env`; no include chain; unknown keys rejected. An unset `${VAR}` fails the load everywhere except `[server].api_key`, which drops silently so a stdio install can boot without a credential its transport never reads.
- **Admission and deadlines are explicit.** `max_concurrent_runs` (default 4) with `admission_timeout` (default 30s) yields a retryable refusal; a run exceeding `reply_deadline` (default 240s, inside Cursor's 300s call ceiling) returns status `running` with a `run_id`, continues in background, and is collected with `check_run` within `retain_completed` (default 1h). Client disconnection cancels the run cooperatively.
- **File parameters marshal across the store boundary.** `input_file`/`input_text` seed the store at the prompt's declared input path; `output_file` writes the declared output after the run; the prompt itself touches the in-memory store only.
- **Broken prompts stay visible.** A parse error or invalid name appears in `list_prompts` with its `problem` field populated rather than silently disappearing; a broken edit during watch retains the entry instead of freezing the catalog.
- **Live reload is atomic.** Catalog and retrieval index publish together as one generation - no reader sees a torn pair; a body-only edit carries the previous index forward.
- **Gateway boot failures split transient from fatal.** A timeout or 5xx warns and serves with an empty model catalog (prompts without `models.bind` keep working); a 401, bad URL, or malformed response refuses to boot.
- **Transport security is per-request.** HTTP checks the bearer on every request (constant-time), not once per session; `/healthz` is unauthenticated by design; `allowed_hosts` is the DNS-rebinding defense; stdio binds no port and checks no token - the spawning harness is the only peer.

Known open problems: whether harnesses other than Cursor need different `reply_deadline` defaults (240s is tuned to Cursor's 300s ceiling).

### The web fetch tool

**Role**: let a model read the web through one tool while an SSRF boundary holds no matter what URL the model supplies. The design problem is not fetching - it is fetching safely when the URL comes from a model that may have just read an attacker-controlled page.

Fixed design decisions - four layers, in order:

1. **URL admission** before any network access: scheme, userinfo, port allowlist, and obfuscated IP encodings (`0177.0.0.1`, `2130706433`, `127.1`, IPv4-mapped IPv6) normalized and classified.
2. **Guarded DNS at connect time on every hop** - the load-bearing decision. The policy filters resolved addresses, not the URL string, because the URL string does not tell you where the connection goes. No verdict is cached, so a rebinding answer is caught on the hop that returns it. A host with mixed public and private answers connects at the public one.
3. **Redirect re-validation**: the full URL policy re-runs on every hop, HTTPS-to-HTTP downgrades refused, hop cap enforced; the final URL is what the tool reports as provenance.
4. **No ambient identity**: no cookies, no `Authorization`, no `Referer`, no ambient proxy - a redirect cannot smuggle credentials cross-origin.

Plus: the blocked table covers all IPv4/IPv6 special-use space including `169.254.169.254`; the only internal-host escape hatch is an exact host-plus-address pair keyed on both; `Content-Type` decides the processing route before the body downloads (readability for HTML with whole-page fallback under 100 characters, verbatim for JSON/XML, decoded for other text, refusal for binaries and for a missing Content-Type - the tool does not sniff); two caps govern size (`max_bytes` 8 MiB counting decompressed bytes, `max_chars` 40,000 cut on character boundaries); structured formats are all-or-nothing under the cap while flat text truncates and flags; every response carries a provenance header (`url`, `truncated`, `extraction`); soft outcomes return as tool text the model can act on while hard errors mean no retry helps; blocked-address messages tell the model only the host - the log gets the address and range, because leaking them would hand an attacker a probe of the internal network. Output is untrusted and nonce-enveloped before it reaches the model.

Stated gaps (the caller's job, recorded so the boundary is honest): query-string exfiltration to a genuinely public host (the control is per-section tool scoping, not the fetch layer); a residual DNS-rebinding window from connection reuse (bounded by a short pool-idle timeout, deliberately); the per-run deadline is invisible to the tool (per-call timeouts are the best this layer can do).

### The development runner

**Role**: the edit-run-inspect loop. `promptforge-dev` runs a prompt against an already-running gateway, dumps the store to `<prompt-stem>.store/` beside the prompt (including partial stores from failed runs), and reruns on save in watch mode behind a debounce. `--capture-raw` persists verbatim per-turn request/response JSON under `.trace/` with owner-only permissions. All dump writes are owner-only, symlink-checked, and atomic. The argument surface is deliberately minimal: model parameters live on the prompt file, not on CLI flags, and former server flags are rejected with usage text.

### The workshop

**Role**: a developer environment for PromptForge prompts - a standalone local application, a Rust server crate with a webview shell, where a prompt is a visible, editable stack of blocks, runs are defined by binding a prompt's declared inputs to real files, every run, edit, decision, and mistake is recorded in an append-only, hash-chained event store, and any two versions of anything are compared by a model with the human making the final call. It is not an IDE, does not edit code, and does not run prompts in production: finished prompts leave and live elsewhere (Cursor, cloud runs, promptforge-cli), and there is one current version - the thing at HEAD - with the full immutable development lineage behind it. The thesis: human intent is the source code, and everything downstream - plans, prompts, reports - is a build artifact. Renamed from Workbench to Workshop (the crates went `wb` to `ws`); `workshop.toml` is the config, with a leftover `workbench.toml` still discovered. The durable design record is `design/design-promptforge-workshop.md`; the stage-1 build log is `design/design-promptforge-ws-1.md`.

Fixed design decisions:

- **The event store is the product; every interface is a view.** The single source of truth is an append-only, hash-chained event log - a commit log that forbids force pushes. The block editor, the run panel, the leaderboard, and the chat window are projections rebuildable from the log.
- **History is immutable; content is destructible.** Events are never rewritten, but payloads are separately stored and individually revocable: redaction tombstones the payload while the chain stays intact, and a tombstone degrades playback deliberately.
- **Everything the model sees is captured at the boundary.** Every tool result is content-addressed into the store at the moment the model sees it, because paths and URLs point at mutable state and a pointer is not evidence. Model-internal reasoning is unobservable, and the design never claims to recover it.
- **The prompt is authoritative state, edited as blocks.** The file is directly mutable, not a projection of the plan; regeneration from the plan is a supported workflow, not an invariant, and a block edit that contradicts a recorded plan decision raises a conflict event rather than diverging silently.
- **Fixtures over dependencies: the store is the only dependency a prompt has.** The workshop binds declared inputs to real files the user picks and never executes a prompt's environment dependencies - the prompt is the core, a crate is one production binding, the workshop is the interactive binding.
- **Identity is rigorous and defined before any UI.** Artifact, PromptVersion, PlanVersion, Run, Variant, Branch, Decision, and Contract are explicit nouns; the load-bearing ExecutionFingerprint splits into invocation identity, execution provenance (including the capability grants in force), and cacheability policy - without the third, "same inputs means cache reuse" is unsound the moment tools, MCP servers, web state, or hosted models drift.
- **Two model planes, kept separate.** The runtime plane (models a prompt uses) runs through the existing gateway; the authoring plane (the assistant that helps develop prompts) is frontier models by key at first, eventually a fine-tuned model that speaks the PromptForge language natively. The planes share one gateway but never share a context.
- **Voice is an input device, and it lives in the server from day one.** Push-to-talk: the webview captures the microphone, PCM frames stream up a WebSocket, and the server transcribes in-process on the local GPU - Whisper large-v3-turbo over a sliding window for interims, large-v3 pipelined at silence for the final text, with the session's jargon fed to the decoder as an initial prompt. Browser Web Speech and cloud STT are rejected because audio leaves the machine. Two move-triggers are named in advance: a prompt wanting transcription as a tool moves it to the runtime plane, and the resident set outgrowing the card moves voice to the gateway.
- **The harness is hand-written, headless, and lands early.** A tool-call loop against the gateway's OpenAI-compatible interface, plus a tool suite and the recorder. The Claude Agent SDK was considered and rejected: TypeScript/Python only, Claude-only (which kills the two-plane design and the future fine-tune), and its loop decides what gets recorded - the product's core asset. It lands at stage 3 anyway, because a daily-drivable tool early is what makes everything else get used.
- **Plan mode is the entropy filter.** The harness aggregates human intent into a plan document before any action; the user reviews and cleans it; applying it produces one clean edit instead of the conversation's raw churn. The conditioning is three layers - the redefined deliverable (maintaining the plan IS the job), the structural tool gate (reads, search, and one write target), and the residue prompt - and leakage is measurable as blocked-mutation events in the log.
- **The leaderboard replaces the tree view.** Branches are navigated by their outputs, not by topology: artifacts with model-computed diffs and structured verdicts (rubric dimensions, critic identity and version, deterministic checks, confidence or abstention, cost, and the human's judgment stored separately). The rationale is the generator-evaluator asymmetry: evaluation is cheaper and more reliable than generation, and the critic's ceiling is good-versus-great, so the final call stays with the human.
- **Artifact reuse is not execution memoization.** A pinned output can always be reused as data; skipping a stage's execution is memoization, valid only when the fingerprint's cacheability policy permits it. A re-roll produces sibling variants under identical inputs - best-of-N sampling with the model as critic.
- **The sidecar is the first extractor, and it watches the agent first.** A prompted model with a ruthless rubric reads the event store and populates the leaderboard's verdicts; fine-tuning carries the burden of proof against that prompted baseline. It advises with memory and never gates.
- **The build order lands a usable tool before the novel core.** Six stages: the window (chat, push-to-talk voice, and a raw append-only JSONL tape from the first commit), plan mode, the harness, the database (the event store the tape migrates into), the comparison loop, the intelligence layer. The novel component lands fourth because capture runs from the first commit.

Stage-1 shipped state (what exists today): two crates (`promptforge-ws-server` on axum, loopback default `127.0.0.1:7910`; `promptforge-ws` the wry/tao shell); verbatim byte-level relay of gateway responses with statuses passed through; a six-field JSONL tape event (timestamp, kind, model, full request and response, latency); one persistent `/ws` WebSocket with id-tagged chat multiplexing; a gateway heartbeat (five-second probes, transition-only emission) with a known-down short-circuit (502 `gateway_unreachable` on HTTP, an error frame on `/ws`, nothing taped) and a catalog push to every session on reconnect; voice models provisioned through the gateway's cache API with download progress on the status bus, degrading - never failing startup - when models are missing; the chat UI is vendored murm-ui source, and the whole UI skins from one `:root` block of CSS custom properties.

Known open problems: the web framework choice for the UI core (stage 1 is settled on vanilla DOM plus markdown-it; re-evaluated when the block editor lands at stage 4); the exact harness tool list, including whether git gets a dedicated structured tool or rides the shell tool; the per-prompt-type eval rubrics (the evaluation record's shape is settled, the rubrics are not); the composer's prefix policy (stable-to-volatile ordering, cache breakpoints, when compaction's cache bust is worth it - flagged, unearned).

### People (speaker-map aid for transcripts)

Transcripts are often auto-transcribed with names mangled phonetically. Use this map to resolve speakers, and still flag a genuinely ambiguous attribution rather than guess.

- **Vinnie Falco** - author of PromptForge; authority on the project design. Mangled as "Vinny," "Vini," "Falco," "Falcone."
- **Jason Brazeal** - implementer with commits across the workspace. Mangled as "Brazil," "Brazel," "Jason B."

### Recurring open questions (seeded; each run updates the running set)

Core format and engine:

- Whether independent H2 sections may execute concurrently (order-is-semantics versus disjoint-store-keys fanout).
- Which recorded non-goals (persistent bytecode, cross-section Lua memory, nested fanout, `tools.remove`, store list/grep) real workloads force back onto the table.
- Whether the `---` marker's positional two-role rule confuses authors in practice.

Gateway:

- Where `default_max_tokens` gets consumed: a parsed, validated chat-model field in the gateway config with no consumer - applied gateway-side as a request ceiling, or advertised through the catalog for the runtime to apply per `infer` call.
- Whether token-cost fairness (DRR) ever unparks alongside per-client round-robin.
- What evidence would reopen demand-driven model load/unload for VRAM-constrained operators.
- What a second gateway instance would need (multi-instance admission is rejected as single-process by design; LiteLLM proxy v3 is the recorded prior art).

Workshop:

- The web framework choice for the UI core (stage 1 settled on vanilla DOM plus markdown-it; re-evaluated when the block editor lands at stage 4).
- The exact harness tool list, and whether git gets a dedicated structured tool or rides the shell tool.
- The per-prompt-type eval rubrics (the evaluation record's shape is settled; the rubrics are not).
- The composer's prefix policy (stable-to-volatile ordering, cache breakpoints, compaction timing) - flagged, unearned.

Tool picker:

- Tuning `margin` against a real catalog - the one unmeasured default.
- Whether a second embedded model (and mean pooling) earns its binary size.
- Whether catalog scale ever forces a persistent vector cache (declined on correctness-risk grounds).

MCP server:

- Whether harnesses other than Cursor need different `reply_deadline` defaults.

Web fetch:

- Whether the tool interface grows a call context so fetches can see the run's remaining budget.
- Whether the residual DNS-rebinding window from connection reuse needs a tighter trade.

### Extraction task (Pass 2 subagent)

You have read the PromptForge design knowledge above. Read the topic-segment scratch file at the path given to you, then extract, contextualize, deduplicate, and write statement records.

A statement is design-relevant if it does one of these:

- states a rule, constraint, or requirement for a PromptForge subsystem (the prompt-file format, the core engine, the gateway, the tool picker, the MCP server, web fetch, the dev runner, the workshop) or a cross-cutting principle;
- proposes, accepts, or rejects a design alternative;
- reports an implementation finding that constrains a design choice;
- identifies something as open, unresolved, or needing a decision;
- states an architectural relationship (core vs gateway, engine vs harness, trusted vs untrusted content).

Discard a statement that is any of these: meeting logistics (scheduling, screen-sharing); a personal work plan with no design content ("I'll write it up this weekend"); conversational filler or a bare agreement token; a within-turn repetition of a point already recorded.

Contextualize each surviving statement into a self-contained design statement, using surrounding segment context to fill missing referents. Example: "Even if you do that, it wouldn't solve the problem" becomes "Even if the gateway normalized every upstream dialect to OpenAI on the way in, a prompt would still bind models by capability name, so swapping a backend's model string in one config line leaves every prompt unchanged."

Deduplicate within this segment: merge statements that express the same claim in different words into one record, listing every speaker who stated it. When unsure whether two statements express the same claim, keep them separate.

Write one record per statement, fields in this order (evidence first, judgment last):

1. `source`: the verbatim quote(s), each with transcript location and speaker(s).
2. `subsystem`: which subsystem or cross-cutting principle it concerns.
3. `kind`: one of rule | alternative | implementation-finding | open-question | architectural-relationship.
4. `statement`: the contextualized, self-contained design statement.
5. `proposed_class`: one of settled | open | contested, with a one-line basis.

Write the records to one statement-records scratch file and return only that file's path.

</promptforge-knowledge>

---

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
