---
name: tighten-design-ledger
overview: Tighten Vibe Coder's commit ledger and queue workflow, then teach Debt Collector to consume that evidence without treating it as proof. Preserve both tools' current architecture and the fresh challenger subagent.
todos:
  - id: tighten-vibe-trailers
    content: Separate uncertainty, deferral, and evidenced repair trailers in Vibe Coder
    status: completed
  - id: repair-queue-workflow
    content: Render actionable queue entries and restore the human drain checkpoint
    status: completed
  - id: route-debt-evidence
    content: Teach Debt Collector to hydrate trailer leads without weakening admission
    status: completed
  - id: validate-ledger-flow
    content: Validate schema consistency, compatibility cases, and challenger preservation
    status: completed
isProject: false
---

# Tighten the Design Ledger and Debt Intake

## Product Requirements

- Problem and users: Agent-written commit messages currently encode uncertainty as violations, infer broad deferrals, and flood the architecture queue with structural observations; the human promotion checkpoint described by the workflow is not operational. Maintainers and the debt analysis pass need a smaller, trustworthy ledger.
- Goals:
  - Make commit trailers distinguish demonstrated facts, uncertainty, explicit deferral, and evidenced repair.
  - Make `vibe/archdoc-next.md` readable Markdown while preserving simple one-record-per-line processing.
  - Restore the human queue-disposition checkpoint at the end of a full plan.
  - Let debt analysis use ledger records for navigation without admitting them as proof.
  - Preserve the independent challenger subagent that reviews accepted debt findings.
- Non-goals:
  - Do not rewrite either tool or introduce another subagent protocol.
  - Do not modify existing repository queue files, migrate old records, or revise explanatory reports.
  - Do not let an agent edit or stage `vibe/archdoc.md`.
  - Do not add a `Debt:` trailer or make commit generation decide what constitutes technical debt.
- Success criteria:
  - New uncertainty never appears as `Violates:`.
  - New queue records render as Markdown list items and remain one physical line each.
  - Neutral, cheap-to-reverse, size-only, and uncertain observations do not enter the queue.
  - Full-plan Close waits for the operator to disposition relevant queue entries.
  - Debt findings still require corroborating diffs or current code and survive a fresh challenger.
- Constraints: Change only [vibe-coder.md](C:/Users/Vinnie/cursor/tools-public/coding/vibe-coder.md) and [debt-collector.md](C:/Users/Vinnie/cursor/tools-public/coding/debt-collector.md), preserve their voice and tagged instruction architecture, and keep old raw queue records readable.
- Open questions: None.

## Functional Specification

- Commit-message workflow:
  - Emit `Design:` for catalog facts and `Violates:` only for demonstrated invariant contradictions.
  - Emit `Uncertain: A<n> - <clause>` when the touched diff cannot establish whether an invariant holds.
  - Emit `Deferred:` only for an explicit TODO, FIXME, stub, unwired changed unit, plan-authorized deferral, or current-step deliverable left incomplete.
  - Emit optional `Repairs: <contract-or-invariant> @ <locus> - <observable failure corrected>` only when the diff repairs behavior and carries direct regression evidence.
- Queue input and output:
  - `vibe/archdoc-next.md` remains line-oriented: each queue record occupies exactly one physical line.
  - Readers accept legacy `N<id> | kind | text | refs` and new `- N<id> | kind | text | refs` records.
  - Writers emit only the Markdown bullet form and separate a newly appended bullet from a preceding non-list block with one blank line.
  - Automatic observations are limited to hard-to-reverse `Design:` facts, demonstrated `Violates:` facts, and unlisted dependency directions.
- Queue ownership:
  - The commit-message subagent is the sole automatic observation writer.
  - The operator alone promotes an entry, records it as decided against, or leaves it open.
- End-of-plan workflow:
  - Before Close, resolve the active plan path from `vibe/ACTIVE`, locate the current-ancestry commit that introduced that plan file, and compare its parent through `HEAD` for changes to `vibe/archdoc-next.md`.
  - Cross-check the added or changed queue records against `Pending:` trailers in commits carrying that exact `Plan:` value; include an ambiguous record rather than silently dropping it.
  - Present those lines with the three allowed dispositions and wait for the operator. Promotion or a decided-against disposition requires the operator's architecture commit; leaving an entry open requires explicit confirmation but no file change.
  - Proceed directly when no relevant entries exist; otherwise remove `vibe/ACTIVE` only after the operator confirms every disposition and any required architecture commit.
- Debt-analysis workflow:
  - Parse `Design:`, `Violates:`, `Uncertain:`, `Pending:`, `Deferred:`, `Repairs:`, and `Plan:` as grouping and navigation records.
  - Hydrate every trailer-derived lead from target diffs and current code before applying the existing debt admission criteria.
  - Resolve `Pending:` identifiers against the queue, use `Plan:` for attribution, treat `Deferred:` as an omission lead, and treat `Repairs:` as a possible verified paydown.
  - Normalize legacy `Violates: ... not determinable from diff` and new `Uncertain:` to one abstention state that proves neither violation nor conformance.
- Errors and recovery:
  - Record malformed trailers and missing queue references without inventing content.
  - Continue to analyze prose-only and legacy commit histories.
  - Leave unhydrated claims rejected or explicitly uncertain rather than counting them as debt.
  - Stop the drain checkpoint when the active plan or its introducing commit cannot be resolved; never guess the plan range.
- Acceptance criteria:
  - Repeated `Design:` or `Pending: compounds` records alone never satisfy the recurring-maintenance criterion.
  - Two corrective episodes count only after code confirms the same maintenance cause and unrelated work or another plan separates them.
  - The challenger phase receives accepted findings and can reject any finding whose trailer evidence was not corroborated.

## Technical Design

- Architecture:
  - [vibe-coder.md](C:/Users/Vinnie/cursor/tools-public/coding/vibe-coder.md) remains the producer of commit trailers and queue observations.
  - `vibe/archdoc-next.md` remains a machine-readable, human-dispositioned queue; `vibe/archdoc.md` remains human-owned.
  - [debt-collector.md](C:/Users/Vinnie/cursor/tools-public/coding/debt-collector.md) remains the consumer that corroborates ledger leads and dispatches a separate challenger.
- Vibe Coder interface changes:
  - Update invariant classification, trailer order, trailer schema, examples, queue matching, observation admission, hard rules, provenance return, and self-checks as one coherent vocabulary change.
  - Remove the duplicate main-session architecture-queue append instruction without changing the commit-message subagent dispatch.
  - Add the drain checkpoint to Run Mode before the existing Close action without creating a new XML instruction block.
- Debt Collector interface changes:
  - Add the trailer evidence hierarchy to Scope and Evidence.
  - Add trailer routing and legacy uncertainty normalization inside `<debt-analysis-instructions>`.
  - Add one reconciliation rule for trailer leads that do not hydrate to repository facts.
  - Leave `<debt-challenge-instructions>` and its dispatch substantively unchanged.
- Data flow:
  - Completed diff and regression evidence flow into factual commit trailers.
  - Actionable architecture facts flow into one-line Markdown queue records.
  - Active-plan queue changes flow to the operator for disposition before Close.
  - Commit history, queue records, plans, diffs, and current code flow into debt candidates.
  - Accepted candidates flow to the fresh challenger before removal-plan synthesis.
- Persistence and failure constraints:
  - Backward-compatible queue reads avoid a mandatory migration.
  - New bullet records preserve existing identifiers and references.
  - No automated path can promote, reject, delete, or rewrite an architecture decision.

## Testing Plan

- Static consistency:
  - Confirm every XML instruction tag still has exactly one opening and closing line.
  - Confirm trailer order and vocabulary agree across procedure, examples, queue insertion, self-check, hard rules, return contract, and schema.
  - Confirm the queue parser accepts raw legacy records and Markdown bullet records while the writer emits only bullets.
- Vibe Coder scenarios:
  - Walk a demonstrated violation, an indeterminate invariant, later-step work, an explicit deferred stub, an evidenced behavior repair, a cheap structural smell, and a hard-to-reverse architecture observation.
  - Verify only the demonstrated violation uses `Violates:`, only the evidenced repair uses `Repairs:`, and only the hard-to-reverse observation enters the queue.
  - Walk Close with no relevant entries and with relevant entries awaiting operator disposition.
- Debt Collector scenarios:
  - Walk legacy uncertainty, new uncertainty, an unsupported `Design:` label, a missing `Pending:` reference, an explicit deferral, a verified repair, a prose-only commit, and two genuinely separated corrective episodes.
  - Verify trailers route inspection but never satisfy admission without repository facts.
  - Verify a repair can reduce or close existing debt but cannot create an introduced-debt finding by itself.
- Exit criteria:
  - Both tools remain self-contained and retain their current high-level workflows.
  - The challenger dispatch and instruction block remain present and substantively unchanged.
  - No new queue output renders as one collapsed Markdown paragraph.

## Decision Record

- Decisions:
  - Keep `archdoc-next.md` line-oriented, meaning exactly one physical line per queue record; the user's concern that “the plan isn't clear” is resolved by naming the file and record shape explicitly.
  - Use Markdown bullets rather than a multi-line record format; this fixes rendering without replacing the parser.
  - Separate `Uncertain:` from `Violates:` because insufficient evidence is not a contradiction.
  - Add `Repairs:` as an optional factual trailer with a regression-evidence gate because verified corrective episodes help later historical analysis.
  - Keep promotion human-only and make the missing drain handoff operational; the user expected Vibe Coder to have “a workflow to promote.”
  - Keep the adversarial debt review in a fresh subagent; the user stated, “it should be in a subagent.”
- Rejected alternatives:
  - Do not emit a `Debt:` trailer because debt judgment belongs to analysis and challenge, not the commit author.
  - Do not use multi-line queue blocks because they add parser and mutation complexity without improving the evidence model.
  - Do not automatically promote queue entries because that would let the producer ratify its own architecture claims.
  - Do not migrate existing repository queues as part of these tool edits; backward-compatible reads isolate that cleanup.
- Assumptions, risks, and notes:
  - Old raw queue lines remain visually poor until separately migrated, but they remain readable by the updated workflow.
  - `Repairs:` may be overproduced unless regression evidence is mandatory; the self-check must enforce that gate.
  - Identifying active-plan queue changes depends on committed plan provenance and queue diffs; missing provenance must stop the drain rather than guess.
  - Known open review finding: Run Mode asks the operator to review every queue record instead of selecting only records associated with the active plan. The operator directed the run to report this finding without changing the implementation.
  - Confidence: high - each change closes an observed evidence or lifecycle gap without changing tool ownership.

## Project survey

- Build command:
  - There is no repository-wide build.
  - From `tools-wg21/slider/`, `uv build` builds the Slider package; `uv run slider <input.md> -o <output.pptx>` installs declared dependencies and runs it.
  - From `crates/png2jpg/`, `cargo build` builds the standalone image utility.
  - The Markdown artifacts and `tools/novelist/writer.py` have no declared build step.
- Focused test command pattern:
  - From `tools-wg21/slider/`, run `uv run pytest tests/test_<area>.py::<test_name>` for Slider.
  - From `tools-wg21/slider/`, run `uv run pytest ../../coding/tests/test_debt_collector.py::<test_name>` for one coding-protocol acceptance case.
  - From `crates/png2jpg/`, `cargo test <name>` is the focused Cargo pattern, though the crate currently defines no tests.
- Full-suite test command:
  - No single repository harness is declared.
  - From `tools-wg21/slider/`, `uv run pytest ../../coding/tests tests` runs all tracked Python tests.
  - From `crates/png2jpg/`, `cargo test` compiles and runs the Rust crate's test target, which currently contains zero tests.
- Linter and formatter commands:
  - No repository-wide or Python linter or formatter is declared.
  - From `crates/png2jpg/`, `cargo clippy` applies the manifest's Rust policy: unsafe code forbidden, Clippy `all` denied, and Clippy `pedantic` warned. No formatter command or configuration is declared.
- Test placement and naming conventions:
  - Coding-protocol acceptance tests live in `coding/tests/test_*.py`, use pytest functions named `test_*`, inspect exact prompt text and tag structure, and exercise Git behavior through disposable repositories.
  - Slider tests live in `tools-wg21/slider/tests/test_*.py`, use pytest functions named `test_*`, and share flat-module import setup through `tests/conftest.py`.
  - Slider golden inputs live under `tools-wg21/slider/tests/golden/`; `tools-wg21/slider/test.md` is a compatibility fixture.
  - The Rust utility and novelist runner have no tracked automated tests.
- Directory map:
  - Root files provide the catalog (`README.md`), repository rules (`AGENTS.md`), license, and ignore configuration.
  - `art/` holds illustrations not paired with a tool; `images/` holds root README section art.
  - `chats/` preserves design conversations; `lessons/` holds articles about prompt and agent craft.
  - `coding/` holds coding-workflow prompt tools, paired image sets, and protocol acceptance tests.
  - `crates/` holds the standalone Rust `png2jpg` utility.
  - `how-to/` holds human-readable guides and paired images.
  - `output/` holds generated examples rather than source tool definitions.
  - `retired/` holds superseded top-level artifacts; group-specific retired tools live in each group's `retired/` directory.
  - `rulebooks/` holds domain writing and implementation references with paired images.
  - `tools/` holds general prompt tools, grouped sub-tools, the novelist runner, and their assets.
  - `tools-wg21/` holds WG21-specific prompt tools, retired tools, and the independent Slider package.
  - `vibe/` holds dated design plans. No `vibe/archdoc.md` or other `archdoc*.md` exists.
- Component boundaries:
  - The main product is a catalog of self-contained Markdown prompt artifacts indexed by root `README.md`; content and image directories have no runtime dependency on the executable utilities.
  - `coding/` is a distinct prompt-protocol group. Its tools are leaf artifacts, while `coding/tests/` validates their textual contracts without importing Slider, novelist, or Rust code.
  - Slider is an independent Python package: `slider.py` calls `parser.py` and `style.py`, then `renderer.py` composes presentations through `draw.py` and `layout.py`. Tests import these flat modules through `conftest.py`.
  - `tools/novelist/writer.py` is a standalone Python runner that depends inward on `tools/novelist/lib/bible.py` and neighboring prompt files; it has no repository-level package integration.
  - `crates/png2jpg/` is an independent Rust binary depending on `image` and `anyhow`; no other repository component imports it.
- Conventions summary:
  - Adding, moving, or removing a tool requires a matching root README update. Retired tools move under a group-local `retired/` directory and disappear from the README.
  - Tool Markdown uses YAML `description` frontmatter, an H1 title, relative image links, compact imperative sections, self-contained instructions, a CC0 dedication, and a final date-model attribution.
  - Prompt subagent protocols use anchored XML tag lines exactly once and pass only bounded instruction blocks; acceptance tests may enforce exact phrases, section order, and tag counts.
  - Root `AGENTS.md` requires same-stem PNG images under a neighboring `images/` directory and paired movement. Existing `coding/` tools visibly use numbered same-stem JPG sets, so these text-only edits preserve their current assets and do not trigger a catalog update.
  - Python uses snake_case, type hints, dataclasses, and underscore-prefixed private helpers. Rust uses edition 2024, contextual `anyhow` errors, and forbids unsafe code.
  - `coding/vibe-coder.md` currently carries the intentional uncommitted partial design-ledger edit. Implementation must begin from the current worktree and preserve that edit rather than reconstructing the file from `HEAD`.
- Rules manifest: `C:\Users\Vinnie\cursor\tools-public\AGENTS.md` is the only `AGENTS.md` and governs the entire repository.

## Execution Instructions

### Step 1: Tighten the complete design-ledger workflow [completed]

Update [vibe-coder.md](C:/Users/Vinnie/cursor/tools-public/coding/vibe-coder.md) and [debt-collector.md](C:/Users/Vinnie/cursor/tools-public/coding/debt-collector.md) as one atomic change.

- In Vibe Coder, separate `Uncertain:` from demonstrated `Violates:`, restrict `Deferred:` to explicit current-step omissions, and add optional regression-backed `Repairs:`.
- Keep `vibe/archdoc-next.md` one physical line per record, read legacy raw and Markdown bullet records, emit only bullets, and queue only hard-to-reverse or demonstrated architecture facts.
- Make the commit-message subagent the sole automatic queue writer and restore the operator-only queue drain before Close without adding another XML block.
- In Debt Collector, route every ledger trailer as navigation that must hydrate from diffs or current code, normalize both uncertainty forms to abstention, resolve both queue formats, and preserve the fresh challenger subagent unchanged.
- Verify trailer order and vocabulary, queue compatibility and rendering, drain outcomes, legacy and new uncertainty, strict deferral and repair admission, evidence hydration, recurring-episode separation, and exactly one opening and closing line for every XML instruction tag.
- Commit the complete two-file change once. Do not create plan-seed, intermediate, bookkeeping, or Close commits.

Existing `archdoc-next.md` formatting and backlog disposition remain a separate repository-specific drain. Explanatory reports, historical plans, source repositories, architecture documents, and all files other than the two named tool files remain unchanged.