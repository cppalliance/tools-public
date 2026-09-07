---
name: debt-collector-tool
overview: Create a lean planning-mode tool that identifies technical debt attributable to new work, delegates repository-history analysis to a subagent, and leaves a self-contained plan for removing the debt.
todos:
  - id: author-debt-collector
    content: Author the lean debt-collector tool and anchored analysis instructions
    status: completed
  - id: create-debt-collector-images
    content: Inspect and name the four supplied debt-collector images
    status: completed
  - id: document-and-verify
    content: Update the README and run prompt protocol verification
    status: completed
isProject: false
---

# Debt Collector Tool

## Product Requirements

- Problem and users: New work can accumulate architectural and mechanical debt across commits that remains invisible in any one diff. The user needs a planning tool that identifies that debt and leaves an executable removal plan.
- Goals: Accept a repository, one commit, or a commit range; infer the target work when needed; inspect its history, code, and available design records; identify debt introduced, worsened, or exposed by the target work; and plan its removal.
- Non-goals: Modify source code, execute the debt-removal plan, perform a generic code review, catalog unrelated legacy defects, rewrite architecture records, or rewrite and grade commit messages.
- Success criteria: The resulting plan shows each debt item, its evidence and consequence, the selected remediation, the resulting tradeoff, and the verification needed to prove removal. A fresh implementation context can execute the plan without this conversation.
- Constraints: Keep the tool lean, self-contained, and judgment-oriented. Enter Plan mode before analysis. Use ordinary agent chat for genuinely expensive-to-reverse architecture choices and never invoke a question tool. Execute this implementation plan under the Vibe Coder discipline without copying that discipline into the finished tool.
- Open questions: None.

## Functional Specification

- Actors and workflows:
  - Resolve an explicit commit or range exactly. For a repository-only request, infer new work from the tracked upstream and current worktree; when no upstream exists, choose the most defensible baseline and record the assumption.
  - Concatenate every complete commit message in reachable history through the selected endpoint into one scratch file, in chronological order, with enough metadata to distinguish commits and mark the target set.
  - Dispatch a debt-analysis subagent by path and one anchored XML instruction tag. Give it the repository, resolved scope, commit-log scratch path, and available design-record paths. Keep raw history, diffs, and source payloads out of the main context.
  - Use commit-message content to reconstruct intent, locate affected code, follow design-plan and queue references, recognize explicit deferrals, and form debt hypotheses. Do not rewrite or assess the quality of the messages.
  - When `vibe/` exists, read `archdoc.md` and `archdoc-next.md` as read-only evidence. Resolve `Plan:` trailers from target commits to their corresponding plan files; include the active plan when uncommitted target work belongs to it. Record missing or malformed references instead of inventing their contents.
  - Inspect the actual target diffs and current code before accepting commit-message claims. Classify findings as introduced, worsened, exposed, or unrelated pre-existing debt; keep unrelated debt out of the removal work.
  - Let the analysis subagent choose how to examine the scratch log according to its size and contents. It writes detailed findings to scratch and returns only a bounded summary plus the findings path.
  - Decide reversible remediations autonomously and record each decision and consequence. Raise only choices whose reversal would materially affect public interfaces, persisted or wire formats, component ownership, dependency direction, or trust boundaries, using ordinary chat.
- Inputs and outputs: Input is a repository path plus an optional commit or revision range. Output is one self-contained debt-removal plan.
- States and validation: Resolve and state the baseline, endpoint, target commits, worktree inclusion, available design records, and analysis limits before drafting findings. Stop with a concise chat explanation when the repository or requested revision cannot be read.
- Errors and recovery: Missing upstreams use a stated inferred baseline. Missing `vibe/` data reduces available evidence but does not block analysis. Empty target work produces a plan stating that no new work was found and no removal work is proposed.
- Security and privacy behavior: Keep repository material in local scratch artifacts and pass paths rather than payloads to subagents.
- Acceptance criteria: Trial runs cover a branch ahead of upstream, one commit, and an explicit range; each preserves full commit messages, uses available `vibe/` evidence, distinguishes target debt from unrelated debt, and emits the required plan shape.

## Technical Design

- Architecture: Add one contextual tool at [tools-public/coding/debt-collector.md](tools-public/coding/debt-collector.md). It orchestrates scope resolution, scratch evidence creation, one or more isolated analysis calls as evidence volume requires, and final plan synthesis in the main context.
- Modules and interfaces: Include one compact `<debt-analysis-instructions>` block whose tags occupy unique unindented lines. Dispatch it by tool path, tag name, repository path, scope, scratch-log path, and discovered `vibe/` paths. Cap its return to a status, finding counts, and output path.
- File and public API changes: Add the tool file together with its four supplied image assets and add a Coding entry in [tools-public/README.md](tools-public/README.md). The images travel with the generated tool as one artifact set. Follow the established frontmatter, two opening flavor paragraphs, distributed image placement, XML block, short restatement, CC0 line, and date-model attribution while keeping procedural prose plain.
- Data, persistence, failure, security, and privacy constraints: Treat the concatenated log and detailed analysis as scratch. Do not modify the inspected repository. Do not write `vibe/archdoc.md` or `vibe/archdoc-next.md`. Keep the tool independent of build-time guidance files at runtime.
- Settled flavor text, reproduced verbatim except for the required italic markup:
  > A clean diff can shake your hand while hiding a knife behind its back, *capisce*. One new function looks innocent. Four commits later, its parameter tuple has cousins in three modules. Shared state says it is only visiting, then becomes a *made man* with dependents throughout the family. A compatibility shim invokes *omerta* and refuses to name the day it will retire. Meanwhile, every plan swears the arrangement is temporary, and *cosa nostro* quietly becomes the permanent shape of the system. Nothing fails today, which is how the debt survives. Tomorrow, every caller votes, every persisted byte has seniority, and every wire contract tells refactoring to *va fa Napoli*. The Debt Collector reads beyond the friendly subject lines. It follows the pattern across the whole ledger until coincidence confesses.
  >
  > The tool accepts a repository, single commit, or commit range and identifies the new crew on the street. It binds every full commit message into one scratch dossier and gives it to a subagent that knows how to follow aliases, plans, deferrals, and architectural obligations. The corresponding design records provide testimony, while the actual diffs and source establish the facts. Reversible debts are paid immediately and entered in the ledger with their consequences. Expensive architecture choices go upstairs to the user in chat. Then the Collector slides one final document across the table: an offer the model cannot refuse, containing the complete plan for removing the debt.
- Image links and distribution:
  - Place `![The Debt Collector](images/debt-collector-1.jpg)` after the two opening flavor paragraphs.
  - Place `![The Collection](images/debt-collector-2.jpg)` after the scope and evidence-gathering guidance.
  - Place `![The Settlement](images/debt-collector-3.jpg)` after the analysis and judgment guidance.
  - Place `![The Final Account](images/debt-collector-4.jpg)` after the closing restatement and immediately before the CC0 line.
- Emitted plan template:
  - `## Product Requirements`: Scope, target work, goals, non-goals, and success criteria for the cleanup.
  - `## Debt Inventory`: Stable debt IDs with evidence, relationship to target work, impact, reversal cost, and target state.
  - `## Technical Design`: Consequential module, interface, data, protocol, security, failure, and lifecycle changes needed to remove the listed debt.
  - `## Testing Plan`: Focused, integration, regression, architecture, and exit checks tied to debt IDs.
  - `## Decision Record`: Autonomous reversible decisions with consequences, user-resolved architecture choices, rejected alternatives, assumptions, and risks.
  - `## Execution Instructions`: Unordered work items tied to debt IDs, dependencies, verification expectations, and explicit exclusions.

## Testing Plan

- Unit: Audit the finished prompt line by line for load-bearing behavior, single readings, consistent terminology, and unnecessary constraints.
- Integration and end-to-end: Apply the tool to disposable repositories representing repository-only, single-commit, and revision-range inputs. Include one fixture with `vibe/` records and one without them.
- Regression, security, and performance: Verify complete multiline commit bodies and trailers survive concatenation; large histories remain file-backed; message content directs inspection without becoming an object of rewriting or grading; no raw payload returns to main; no question-tool invocation appears in the tool.
- Exit criteria: The protocol tests produce self-contained plans with all six sections, every finding traces to evidence, cheap decisions include consequences, hard architecture forks appear in ordinary chat, and the finished tool remains materially shorter than its design inputs.

## Decision Record

- Decisions:
  - Use a single canonical full-message scratch log and let the analysis subagent decide how to examine it. This preserves all intent, rationale, design facts, plan links, queue links, and deferrals without prescribing a rigid analysis algorithm.
  - Treat commit messages as materially useful evidence and a navigation index, never as text to rewrite or grade.
  - Treat actual diffs and current code as authoritative and commit messages as historical evidence. This prevents an inaccurate message from becoming a false debt finding.
  - Analyze reachable history for patterns while marking the narrower target set. This allows the tool to attribute debt to new work without losing cross-commit context.
  - Keep one primary analysis instruction block and allow additional subagents only when evidence volume requires partitioning. This preserves simplicity while avoiding context overload.
  - Preserve the six-section handoff shape while replacing the generic functional section with `Debt Inventory`. This makes debt visible immediately and remains compatible with plan execution.
  - Use the two settled flavor paragraphs exactly, including italic markup.
  - Use the four supplied images with the settled names and distribution.
  - Treat the tool file and its four images as one generated tool. The supplied untracked images are authorized inputs to this plan, not unrelated dirty-worktree changes.
  - Apply the Vibe Coder discipline to implementation only. The Debt Collector's runtime instructions remain limited to debt analysis and plan production.
- Rejected alternatives:
  - Analyze only the target diff. Rejected because cross-commit debt patterns and prior design intent would disappear; revisit for an explicit fast mode after real usage demonstrates a need.
  - Load the complete raw log into main context. Rejected because its size scales with repository history and weakens synthesis; revisit only for trivially small histories.
  - Encode a comprehensive debt taxonomy and rigid scoring system. Rejected because it would bloat the tool and constrain model judgment; add only categories justified by observed failures.
- Assumptions, risks, and notes:
  - The default repository-only baseline is usually the tracked upstream; unusual topologies may require a stated model-chosen baseline.
  - Commit messages may lack structured trailers. The tool still analyzes prose, diffs, code, and available design records.
  - The debt plan is a remediation plan, not an architecture-document update. Any later architecture-record change remains a separate human-controlled action.

## Project survey

- Build command:
  - There is no repository-wide build.
  - From `crates/png2jpg/`, `cargo.exe build` builds the standalone Rust image utility.
  - From `tools-wg21/slider/`, `uv run slider <input.md> -o <output.pptx>` installs declared dependencies as needed and runs the Python slide renderer without a separate build step.
- Focused test command pattern: From `tools-wg21/slider/`, run `uv run pytest tests/test_<area>.py`; append a pytest node ID to target one test.
- Full-suite test command: From `tools-wg21/slider/`, run `uv run pytest`. This is the only declared automated suite.
- Linter and formatter commands: None are declared at repository or component level. `crates/png2jpg/Cargo.toml` does declare Rust lint policy with unsafe code forbidden, Clippy `all` denied, and Clippy `pedantic` warned.
- Test placement and naming conventions:
  - Slider tests live in `tools-wg21/slider/tests/test_*.py`, use pytest functions named `test_*`, and share import-path setup through `tests/conftest.py`.
  - Golden inputs live under `tools-wg21/slider/tests/golden/`; `tools-wg21/slider/test.md` is a compatibility fixture.
  - The Rust utility and novelist helper have no tracked automated tests.
- Directory map:
  - `art/` holds illustrations that do not pair with a specific tool.
  - `chats/` holds preserved design conversations.
  - `coding/` holds coding-workflow prompt tools and their image sets; the Debt Collector belongs here.
  - `crates/` holds the standalone Rust `png2jpg` support utility.
  - `how-to/` holds human-readable guides and paired images.
  - `images/` holds section art used by the root README.
  - `lessons/` holds articles on prompt and agent craft.
  - `output/` holds generated examples rather than tool definitions.
  - `retired/` holds superseded top-level artifacts.
  - `rulebooks/` holds domain writing and implementation references with paired images.
  - `tools/` holds general prompt tools, grouped sub-tools, the novelist helper script, and their images.
  - `tools-wg21/` holds WG21-specific prompt tools, retired tools, and the Slider Python package.
  - `vibe/` holds dated design records. No `vibe/archdoc.md` or other `archdoc*.md` exists.
- Component boundaries:
  - The main product is a catalog of self-contained Markdown prompt artifacts. Root `README.md` indexes them, and each prompt refers only to relative assets or host-agent mechanisms.
  - `coding/` is a distinct workflow group. Its prompt files are leaf artifacts indexed by the README and do not depend on the executable utilities.
  - Slider is an independent Python package: `slider.py` drives `parser.py` and `style.py`, then `renderer.py` composes output through `draw.py` and `layout.py`. Tests import these flat modules through `conftest.py`.
  - `crates/png2jpg/` is an independent Rust binary whose single source file depends only on `image` and `anyhow`; no other repository component imports it.
  - `tools/novelist/writer.py` is a standalone Python runner that depends inward on `tools/novelist/lib/bible.py` and the neighboring prompt files; it has no repository-level package or test integration.
- Conventions summary:
  - Adding, moving, or removing a tool requires a matching root README update. Retired tools live under a group-local `retired/` directory and are omitted from the README.
  - Tool Markdown uses YAML `description` frontmatter, an H1 title, relative image links, a CC0 dedication, and a final date-model attribution.
  - Tool images live in a neighboring `images/` directory and travel with the tool. The root rule describes one same-name PNG, while the established `coding/architect.md` artifact visibly uses four distributed JPG images; this plan explicitly authorizes the same four-image JPG shape for Debt Collector.
  - Markdown tools favor direct imperative prose, compact sections, and self-contained execution instructions. Python code uses snake_case, type hints, dataclasses, and underscore-prefixed private helpers; Rust uses edition 2024, contextual `anyhow` errors, and no unsafe code.
- Rules manifest: `C:\Users\Vinnie\cursor\tools-public\AGENTS.md` is the only `AGENTS.md` and governs the entire repository tree.

## Execution Instructions

- Work items: Generate the complete Debt Collector artifact set: author [tools-public/coding/debt-collector.md](tools-public/coding/debt-collector.md) with lean orchestration, the debt-plan template, one anchored analysis block, reversible-choice handling, ordinary-chat escalation, the settled flavor text, and the four settled image links; include the supplied `debt-collector-N.jpg` files in the same change.
- Work items: Add the tool to [tools-public/README.md](tools-public/README.md) with a one-sentence description.
- Dependencies and verification: Apply the Bounded path from [tools-public/coding/vibe-coder.md](tools-public/coding/vibe-coder.md): accept the four supplied images as part of the authorized starting change, survey the repository, run one implementation cycle without decomposition, place the complete tool and README update in one provisional commit, review and fix that commit, verify it, and finalize its message.
- Dependencies and verification: The scope resolver creates the marked full-message scratch log; its contents direct the subagent to relevant intent, code, plans, queue entries, and deferrals; target diffs and current code corroborate the resulting hypotheses; the analysis subagent creates detailed findings; main synthesizes only those findings into the final plan. README wording depends on the finished tool behavior.
- Dependencies and verification: Run the three disposable-repository protocol cases, inspect the subagent dispatch for exact tag-by-reference loading, and perform a final prompt audit and structural search.
- Deferred and out of scope: Automated debt-plan execution, architecture-record promotion, a persistent debt database, and a rigid smell catalog.
