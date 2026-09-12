# Human Code Organization vs PromptForge Workshop: What to Steal

Report type: evaluation / review. It judges the PromptForge Workshop crates (promptforge-ws, promptforge-ws-server, and their embedded TypeScript UI) against five popular human-organized codebases that share the same stack, and prescribes fixes in severity order.

## Executive summary

The verdict: our code is structurally weaker than the human references in five specific places, but it is not uniformly bad, and our test coverage intent beats three of the five references outright. The weaknesses are fixable with known idioms, listed below in payoff order. Every finding cites the reference codebase it comes from and carries a confidence tag; the detailed findings section holds the evidence.

### Key findings

1. **Our UI has no dependency rule; VS Code's one-way layer imports (base -> services -> ui, lint-enforced) are the single highest-value idiom to adopt.** Any VS Code file's legal imports are decidable from its path alone. Confidence: high.
2. **We keep shared state in module-level mutable variables (`main.ts`); VS Code keeps none, and SilverBullet's 1374-line `Client` god class shows where our drift ends.** The fix is a small service class with a change emitter, passed through constructors. Confidence: high.
3. **We clean up listeners ad hoc; VS Code routes every listener, emitter, and child widget through a `Disposable`/`_register` lifecycle, making leaks structurally hard.** Dockview panel churn makes this relevant to us now. Confidence: high.
4. **Our 30-50KB Rust server modules mix protocol, policy, and helpers; the human norm splits by role, not byte count.** Weylus keeps a pure-types `protocol.rs` with direction-named serde enums, and our `chat_ws`/`voice` duplication is the first extraction target. Confidence: high.
5. **Our 27KB `style.css` concentrates all shell chrome; VS Code spreads 450 CSS files, each colocated with and imported by its owning widget.** The refactor is mechanical under our existing esbuild setup. Confidence: high.
6. **Our tests run as a hand-ordered chain of 14 scripts plus a 44KB god-test; all three TS-heavy references use one glob-discovering runner with tests colocated next to source.** Confidence: high for the runner swap, medium for dismantling `smoke.mjs`.

## Method

We characterized our stack first: tao + wry used directly (no Tauri), a local axum server with WebSocket multiplexing and rust-embed assets, and a framework-free vanilla TypeScript UI built with esbuild, CodeMirror 6, dockview, and marked. Search subagents then ranked open-source projects sharing the stack or the technique by popularity. We selected five, verified authorship through the GitHub commits API (scanning the last 100 commits of each for Co-authored-by AI trailers, "Generated with" markers, and bot authors), shallow-cloned each, and analyzed its organization in depth. We profiled our own three codebases the same way for an honest baseline.

## Reference projects: four of five are verifiably human-authored

| Project | Stars | Why chosen | AI-commit check (last 100 commits) |
|---|---|---|---|
| VS Code | ~165k | Canonical framework-free TS UI: custom docking, services, disposables | ~85 of 100 recent commits are Copilot co-authored, but the architecture studied here (layering, Disposable, DI, dom helpers) dates to 2015-2020 and is human-designed |
| SiYuan | ~35k | Framework-free TS, hand-built docking, WebSocket push, Go server serving the UI; closest overall architecture match | Clean; 3 keyword hits, all false positives; two human core authors |
| Dioxus | ~39k | Largest production consumer of wry + tao outside Tauri; shell-side reference | 3 of 100 commits carry Devin AI co-author trailers on human-merged PRs; core idioms predate them |
| Weylus | ~9.5k | Rust local server, embedded vanilla frontend, WebSocket media streaming; our exact technique with a media pipeline analogous to whisper | Clean; started 2019, 74 of 100 commits by the maintainer |
| SilverBullet | ~4k | CodeMirror 6 + esbuild + local Rust server (v2); closest editor-stack analog | Clean; 0 of 100 flagged |

VS Code carries one instructive caveat: the largest and least disciplined files in its repo today are the recent AI-era ones, including a 368KB agent file. The guardrails (layering lint, disposable lint, size-by-role norms) are what kept the historical codebase coherent, and AI contributions degrade even that codebase where the guardrails do not reach.

## Baseline: our weaknesses cluster in five places

The self-profile found the shell crate (promptforge-ws, roughly 1.3K lines over 5 files) genuinely well organized: one concern per module, documented failure modes in the OLE drop target, degrade-not-crash startup. Our test discipline exceeds three of the five references; Weylus has zero tests, the Dioxus desktop crate has two, and SiYuan tests only extracted pure logic. The structural weaknesses concentrate in: flat 30-50KB Rust server modules mixing protocol and policy (`transcribe.rs`, `chat_ws.rs`, `voice.rs`, `app.rs`); WebSocket session scaffolding copied between `chat_ws` and `voice` rather than abstracted; module-level mutable state in `main.ts` (`modelCatalog`, `currentModel`); one 27KB `style.css` plus two indent conventions split between vendored and workshop code; and a 44KB serial god-test (`smoke.mjs`) atop a hand-ordered chain of 14 test scripts.

## Detailed findings, ranked by payoff

### Finding 1: one-way layer imports are the missing load-bearing rule

VS Code governs its entire codebase with lint-enforced unidirectional dependencies: base (generic utilities that know nothing of the app) may not import platform/services (no DOM), which may not import workbench/ui (features). The rule makes any file's legal imports decidable from its path alone and keeps DOM-free code trivially unit-testable. Our UI has no such rule; workshop code, vendored chat code, and shared utilities import each other ad hoc.

Fix: introduce three UI folders (`base/`, `services/`, `ui/`) with the rule "ui may import services may import base, never the reverse". The convention pays even unenforced; a 20-line eslint rule enforces it. Confidence: high, because it is the load-bearing rule of the most successful codebase in this study.

### Finding 2: shared state belongs in services, not module globals

Nothing in VS Code's UI reads shared mutable module globals. Shared state lives in a service class behind an interface with an `onDidChange` emitter, instantiated once at the composition root and passed to component constructors. SilverBullet shows the failure mode we are drifting toward: a 1374-line `Client` god class plus a `globalThis.client` escape hatch, which its own STYLE.md flags as a mess.

Fix: replace the `main.ts` module variables (`modelCatalog`, `currentModel`) with a small ModelService owning the data and an emitter, handed to `AgentController` and the menu code via constructors. Skip DI decorator machinery; a plain services object built in `main.ts` gets most of the benefit at our scale. Confidence: high, because it fixes an identified smell with a proven pattern.

### Finding 3: a Disposable lifecycle prevents the leaks our panel churn invites

Every VS Code widget extends `Disposable` and routes every listener, emitter, and child through `_register`, so teardown is one `dispose()` call up the tree. Their test harness fails any suite that leaks disposables. Our panels and socket handlers manage cleanup ad hoc, and dockview creates and destroys panels dynamically, which makes ad hoc cleanup our most likely source of slow leaks.

Fix: add a roughly 60-line `lifecycle.ts` (IDisposable, DisposableStore, a Disposable base with `_register`) to `base/` and adopt it in every panel and plugin. Confidence: high; the cost is small and the payoff structural.

### Finding 4: split Rust modules by role and extract the duplicated socket scaffolding

The human norm is not small files at any cost; VS Code tolerates a 42KB `markersView.ts`, and SiYuan carries a 4867-line editor file it regrets. The norm is splitting by role: VS Code's markers feature separates registration, public interface, data model, view, renderers, actions, and strings into named files. Weylus, the closest analog to our server, keeps `protocol.rs` as a pure-types module with serde enums named by direction (`MessageInbound`/`MessageOutbound`) and zero I/O, and hides the transport behind two traits so session logic never touches the websocket library.

Fixes, in order: extract the session scaffolding duplicated between `chat_ws.rs` and `voice.rs` (outbox channel, writer task, session id counter) into one module or trait (confidence: high, because it is literal duplication today); pull the wire types out of both files into a pure protocol module mirroring the TS message types (confidence: high); split `transcribe.rs` along its engine/workers/VoiceSlot seam (confidence: medium, because tests pin working behavior, so do it opportunistically).

### Finding 5: per-component CSS replaces the 27KB skin file

VS Code has 450 CSS files and no monolith; each widget colocates its CSS and imports it (`import './button.css'`), scoped under a root class, with theming through CSS variables only. SiYuan partitions SCSS into generic component partials (`b3-` prefix) and feature partials mirroring the TS features. Our `style.css` is well sectioned but remains one 27KB file that every UI change touches.

Fix: split `style.css` into per-component files colocated with the owning TS module and imported from it; esbuild already aggregates CSS imports into `app.css`. Keep one small base file for resets and design tokens. Confidence: high; the refactor is mechanical.

### Finding 6: one glob-discovering test runner replaces the 14-script chain

All three TS-heavy references use a single runner (Mocha glob discovery, vitest, or the bare node runner) with tests colocated next to source and named in plain English; none chain scripts by hand. SiYuan's cheapest-viable strategy fits us exactly: extract pure decision logic from DOM-heavy classes into tiny sibling modules and test only those. VS Code adds a leak check in shared suite setup rather than per-script boilerplate.

Fix: replace the serial chain in `package.json` with glob discovery, begin carving `smoke.mjs` into per-feature colocated tests, and add a shared setup helper with a disposable-leak check once Finding 3 lands. Confidence: high for the runner swap; medium for fully dismantling `smoke.mjs`, which has real end-to-end value and should shrink, not disappear.

### Finding 7: the socket layer should absorb four proven refinements

SiYuan queues pushes that arrive before the app is ready and flushes them after init, killing a class of startup races (confidence: high, cheap). SiYuan's server exposes intent-named push helpers (`PushReloadFiletree`-style) so business code never constructs frames; port as methods on a Push struct in Rust (confidence: high). SiYuan also shows the anti-lesson: its command vocabulary exists twice, once in Go and once in TS, checked by no tool; we should generate the TS message types from the Rust serde enums or keep one annotated contract file both sides cite (confidence: medium, payoff grows with protocol size). Weylus delimits binary streams with an explicit JSON control frame announcing each new stream generation, directly applicable to our voice socket (confidence: high). SilverBullet's `realtime_events.ts` is a textbook 257-line reconnect client with capped exponential backoff, event coalescing, and heartbeat-TTL health; adopt pieces when touching our backoff (confidence: medium, ours works today).

### Finding 8: SilverBullet's CodeMirror idioms fit our editor-plus-server shape exactly

SilverBullet keeps 56 CM extensions in one flat `codemirror/` directory, one file per concern, each exporting a function that takes the app object and returns an Extension, all assembled in a single `createEditorState()` function. Two idioms matter most for us: compartments stored on the app object for anything reconfigurable at runtime, with heavy modes lazy-loaded then reconfigured in; and an `Annotation` (`externalUpdate`) tagging transactions that came from the server, so autosave logic distinguishes remote edits from local typing. Adopt both as the editor panel grows. Confidence: high; the idioms were built for exactly this shape.

### Finding 9: the shell is close to Dioxus's shape, with three upgrades available

Dioxus converts every foreign callback (menus, hotkeys, signals, IPC) to a `proxy.send_event` at the edge, so a single exhaustive `UserWindowEvent` enum re-enters through one match and the event loop stays a pure dispatch table (confidence: high). Its stated two-zone error policy, panic on construction and never in steady state, matches what we mostly do; writing it down prevents drift (confidence: high). Every platform workaround carries its upstream issue URL (tao#889, wry#830); extend that convention everywhere (confidence: high, trivial). On drag-drop, Dioxus avoids COM by forwarding wry's native events to JS glue that re-synthesizes HTML5 events; our custom OLE target preserves real HTML5 semantics and is defensible, but their pattern is the proven fallback if COM maintenance ever bites (confidence: medium on ever needing to switch).

### Finding 10: a written comment policy would prune our over-narration

The references comment less than we do and only for cause. SilverBullet's STYLE.md permits comments only for a non-obvious why, an invisible constraint, an external-bug workaround, or a subtle ordering requirement, and the codebase follows it. SiYuan's density is 3.7 percent, and 588 comments cite a GitHub issue URL inline. Our Rust module docs are good domain documentation, but our file prologues over-narrate.

Fix: adopt a short STYLE.md with SilverBullet's comment policy and SiYuan's issue-URL convention; trim narration-only prologues opportunistically. Confidence: medium-high; our comments are an asset overall, so this is a pruning rule, not a purge.

## Where we already match or beat the references

Our Rust server test volume and specificity (behavior-named async tests with stub gateways) exceed Weylus, the Dioxus desktop crate, and SiYuan; VS Code and SilverBullet beat us on infrastructure, not coverage intent. The vendored chat UI's PROVENANCE.md documents provenance more clearly than any studied project. Degrade-not-crash voice provisioning matches the best human practice. Our esbuild build-as-a-plain-script and our disk-in-debug, embed-in-release asset serving match SilverBullet's patterns exactly; keep both.

## Human messes we should explicitly not copy

SiYuan: the 4867-line editor file, the stringly-typed WS vocabulary duplicated across languages, instanceof-ladder component lookup, index-poking into the layout tree, and a six-positional-parameter callback fetch wrapper. Weylus: the 1130-line single-file frontend, DOM-as-state, a four-primitive shutdown choreography that a CancellationToken replaces today, an `unsafe impl Send` with no safety comment, and unwraps on cross-thread sends with undocumented lifetime invariants. SilverBullet: the `Client` god class, post-build bundle string-patching, broad `any` tolerance, and a decorator stack deep enough that event origin becomes unpredictable. Dioxus: payload-in-header IPC, format-string JS injection without one escaped eval helper, and "just for now" clippy allows that became permanent.

## Recommended execution order

1. `lifecycle.ts` plus a ModelService replacing `main.ts` module state (Findings 2, 3): small and immediate.
2. Split `style.css` into colocated per-component files (Finding 5): mechanical.
3. Swap the test runner to glob discovery and start carving `smoke.mjs` (Finding 6).
4. Extract the shared WS session scaffolding and a pure protocol module in the server (Finding 4).
5. Introduce the `base/services/ui` layer folders with the one-way import rule (Finding 1), together with steps 1 and 2 since files move anyway.
6. Socket refinements: boot queue, push helpers, stream-delimiting control frames (Finding 7).
7. Editor compartments and the `externalUpdate` annotation when the editor panel next grows (Finding 8).
8. STYLE.md with the comment policy and issue-URL convention (Finding 10).

## Refactor notes

Guidance for wrapping this report in a long-horizon refactor plan. The report ranks the findings; these notes carry the constraints a plan needs that the findings do not.

**Separate pure-structure moves from behavior changes.** Findings 1-6 and 10 are refactors: files move and code is extracted, but wire behavior and rendered output stay identical. Findings 7 and 8 (boot queue, push helpers, stream-delimiting frames, CM compartments, externalUpdate) are behavior changes wearing a refactor costume. Scope the plan to the pure refactor and make Findings 7-9 an explicit second phase, so every phase-one step shares the same done-criterion: all existing tests pass unchanged.

**Make the existing test suite the invariant, and touch it last.** The execution order puts the test-runner swap (Finding 6) at step 3, but smoke.mjs and the 14-script chain are the safety net for everything else in the plan. The runner swap changes discovery only; no test is rewritten or deleted while other refactor steps are in flight; smoke.mjs stays green and intact until the end, then gets carved as the final step. Confidence: high - refactoring the net while standing on it is the classic long-horizon failure.

**Declare the vendored boundary.** ui/src/chat/ is vendored murm-ui with a PROVENANCE.md. The layer rule (Finding 1), the CSS split (Finding 5), and any indent normalization apply to workshop-owned code only; treat chat/ as an opaque dependency. Without this line in the plan, an agent will restructure 12K lines of vendored code and destroy the upgrade path. Confidence: high.

**Do-not-touch guardrails.** drop_target.rs (dense COM code, working, documented); the wire protocol semantics during the protocol.rs extraction (move types, do not redesign them); the murm plugin seam.

**Per-step verification and commits.** Each step ends with cargo test, npm run typecheck, and npm test, then a commit, so a failed step rolls back one commit rather than unwinding accumulated drift.

**Merge the steps that move the same files.** Step 5 (layer folders) moves the same files as steps 1-2 (lifecycle.ts, ModelService, CSS split). Either merge steps 1, 2, and 5 into one restructure-the-UI-tree step, or have step 1 create base/ and services/ in their final locations from the start, so files move once.

**Global stop condition.** If a step's tests fail twice, stop and re-plan. An enormous refactor is exactly where pushing through failures does compounding damage.

## Sources

- microsoft/vscode, siyuan-note/siyuan, DioxusLabs/dioxus, H-M-H/Weylus, silverbulletmd/silverbullet: shallow clones analyzed 2026-08-26; authorship verified against the GitHub commits API the same day.
- PromptForge Workshop crates promptforge-ws and promptforge-ws-server, including the embedded UI, profiled 2026-08-26.

*2026-08-26 18:10 - claude-fable-5-thinking*
