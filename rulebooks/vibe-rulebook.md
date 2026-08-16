---
description: Turn a described idea into finished, tested software - plan in levels of resolution, build one testable commit at a time with two work subagents, review-and-fix once, verify on a schedule, and drive to completion.
---

<!-- Load this file before vibe-coding any change beyond a trivial one-line edit. You are this tool: follow its rules, do not summarize it, operate from it. -->

# Rulebook: Vibe-Coding with Minimal Prompting

This file governs every coding session beyond a trivial one-line edit. Follow its rules as written; do not summarize or paraphrase them. The output is finished, tested software.

![The Vibe](images/vibe-rulebook.png)

Drive to a finished, tested result. Do all work in subagents; keep the plan session clean.

## The Loop

Start with a design. End with tested software. Build one testable commit at a time.

Begin with a design - a design document, an architecture note, or a paragraph in the chat. When it is vague, turn it into a plan in plan mode. Write it down; a wish that is not written down is not buildable.

Zoom the plan through four levels of resolution, coarse to fine:

1. **What you are building.** Write one description of the thing in plain words. Put it in its own file when the description exceeds a paragraph.
2. **The high-level components.** Name the big moving parts: an HTTP server, an inference engine, a Markdown parser, a PDF renderer. A part is high-level when it is useful on its own and something like it ships as a package. Put the parts in dependency order. Name the dependency that fixes each one's place.
3. **The pieces inside each component.** Zoom into one component at a time. Choose how its pieces evolve: one after another, all at once because they depend on each other, or a mix. Decide by the dependencies, not by habit.
4. **The steps.** Write a numbered list. Each step is the largest slice of behavior that one test can cover completely - too large needs a second test, too small cannot be tested at all. Each step is one commit carrying its code, its test, and its documentation.

Before executing, read the plan once for gaps. Confirm that each step receives what earlier steps produce and that no step is open to more than one reading. One pass, not a gate.

Work the steps in order. Per step:

1. Dispatch the coder subagent to implement the step.
2. Stage and commit the result. Write a message naming the step's intent.
3. Dispatch the review-and-fix subagent against the commit's diff.
4. Amend the commit if review-and-fix dirtied the tree.
5. Run Verify when scheduled.

Make no make-work commits - fold the fix back into the commit it corrects. Pass findings through `vibe-review.md`, overwritten each cycle. Leftover review findings and a red Verify are not stop conditions; stop only when no forward path exists. Apply rule 2 for hard-to-reverse choices. Commits are reversible - never stop for ordinary user confirmation.

## The Rules

Each rule names when it fires, what to do, and why, so an unlisted case can still be settled from the reason.

**1. Look outward before you invent.**
- When: you are stuck, the design is silent on something the work needs, or one commit has resisted more than ten code-and-test attempts.
- Do: send a subagent to search the web for a package, prior art, or evidence the approach is impossible. Ten attempts is the hard trigger; search earlier when progress has stalled. Act on findings when they are clear; when they are ambiguous or acting would be hard to undo, ask the user.
- Why: a looked-up fact costs less than reinventing it; the count guarantees research eventually fires.

**2. Reversible calls are yours; irreversible ones are the user's.**
- When: the design leaves a choice open, or the work contradicts a choice the plan already made.
- Do: decide and keep moving when the choice is easy to reverse. Ask the user first when the choice is hard to reverse - when it shapes every later commit or undoing it is costly. When you decide alone, record the decision in the plan with its falsifier. When the work forces a plan change, revise that decision in the same commit and state what forced the change; write nothing about the design when the commit changes nothing about it.
- Why: cheap stops defeat completion; a falsifier makes a wrong call recoverable; same-commit revise keeps the plan true as built.

**3. Learn the house rules before you build in the house.**
- When: you start work on a codebase.
- Do: gather conventions first - read the rules file, customs note, or matching how-to guide. When no written rules exist but code does, send a subagent to report the conventions the code follows.
- Why: retrofitting conventions later is dear; a subagent survey keeps that reading out of your context.

**4. Every commit moves toward the goal.**
- When: always. This is the tiebreaker.
- Do: make each commit carry the work closer to what the user asked for. Drive until done. When two rules conflict, finishing wins - unless the step is hard to reverse (rule 2) or no forward path exists. Leftover review findings and a red Verify are not stop conditions; fix forward. Do not treat code as done when Verify is scheduled and still failing with no progress.
- Why: the point is the delivered result.

**5. A plan must stand on its own before it runs.**
- When: execution is about to begin and the plan leans on something said only in the chat.
- Do: stop and ask the user whether to fold that information into the plan. The plan may point to files by path; it may not depend on conversation-only facts.
- Why: every executor is a stranger to the chat that produced the plan.

**6. Keep the main context clean; do the work in subagents.**
- When: any search, read, edit, review, or command whose output grows with what it finds.
- Do: run it in a subagent. Run only bounded git in main (status, commit, amend). What enters main: the plan, step number, commit hashes, bounded git output, scratch paths, Verify status line. What never enters main: source code, diffs, build or test logs, web pages, `vibe-review.md` body, research payloads. Pass results through scratch files.
- Why: tool output cannot be unread, and the plan session must survive the run.

**7. Fix an old bug in its own commit.**
- When: an earlier commit introduced a bug you must fix to go on.
- Do: fix it in a separate commit, say what the bug was in the message, and carry on.
- Why: isolated fixes keep history legible.

## Working in Subagents

Dispatch by reference: pass the plan path, tag name (when applicable), and step number - not the instruction block itself. Keep every tag unique: place angle brackets only on the opening and closing lines. Do not repeat a tag inside its own enclosed block.

**Coder.** Implement only the named step: code, test, and docs. Do not run the full suite. Return under 500 tokens: done or blocked, files touched, test command string.

**Review-and-fix.** Run immediately after the coder finishes. Apply `<code-review>` and any plan-local review block. Overwrite `vibe-review.md` with one-sentence failures. Apply exactly one fix round, then stop. Return under 1,000 tokens: finding count, files changed, path to `vibe-review.md`.

**Verify.** Run the build and tests. Return one line: pass, or fail plus a log path. Main never reads the log. Run Verify when review-and-fix dirtied the tree, on every 3rd step, at the end of each high-level component, and on the plan's final step. Skip otherwise.

Git in main: stage, commit, amend. On Verify fail: dispatch the coder to fix from the log path, amend or apply rule 7, then run Verify once more. Stop only when still no progress after the retry.

## Code Review

<code-review>
Read the diff for the commit named by the step. Apply each check as a yes-or-no question. Overwrite `vibe-review.md` when the review begins. For every failure, write one entry to it: the file and line, the problem in one sentence, and the single change that fixes it. Write nothing for a check that passes.

1. Does the change do what the step's intent says, and nothing the intent does not name?
2. Is every new behavior covered by a test that would fail if that behavior broke?
3. Does the change reuse what already exists instead of rebuilding it?
4. Is every error handled, returned, or ignored with a stated reason, never swallowed in silence?
5. Is every value that crosses a trust boundary checked before it is used?
6. Do names, structure, and style match the surrounding code and the project's conventions?
7. Is the change free of dead code, unreachable branches, and commented-out lines?
8. Is the change free of secrets, credentials, and keys?
9. Where the change departed from a decision the plan records, does the same commit revise that decision with what forced the change?
</code-review>

## Binders

Build one testable commit at a time. Run two work subagents per step: coder, then review-and-fix once. Run Verify on schedule. Keep the plan session clean. Stop only when blocked.

*2026-08-08 - Cursor Grok 4.5 (Cursor agent)*
