---
description: Turn a described idea into finished, tested software - plan in levels of resolution, build one testable commit at a time with two work subagents, review-and-fix once, verify on a schedule, and drive to completion.
---

<!-- Load this file before vibe-coding any change beyond a trivial one-line edit. You are this tool: follow its rules, do not summarize it, operate from it. -->

# Rulebook: Vibe-Coding with Minimal Prompting

In every block of marble a figure waits, finished in the mind of God and unfinished in the world. So it is with the thing you wish existed: an app, a tool, a small machine that does one useful thing well. For ages the road from wanting it to holding it was years of the chisel, and most figures never left the stone.

This file is the workshop. Speak the shape in whatever words you have, and the discipline here finds the grain, plans the cuts, and frees the figure - plan into tested software, wish into a thing you can open and use. No academy is required; the master and the apprentice begin the same way, by naming what they see inside the block. You bring the vision; the method brings the thousand careful blows, and it keeps working while you rest. Come back to something standing free of the stone, then choose the next block.

![The Vibe](images/vibe-rulebook.png)

Drive to a finished, tested result. Keep the plan session clean by doing the work in subagents.

## The Loop

Start with a design and end with tested software, one testable commit at a time.

Begin with a design - a design document, an architecture note, or a paragraph in the chat. When it is vague, turn it into a plan in plan mode. A wish becomes buildable only once it is written down.

Zoom the plan through levels of resolution, coarse to fine:

1. What you are building. One description of the thing, in plain words. It may live in its own file.
2. The high-level components. The big moving parts: an HTTP server, an inference engine, a Markdown parser, a PDF renderer. A part is high-level when it is useful on its own and something like it ships as a package. Put the parts in dependency order, and name the dependency that fixes each one's place.
3. The pieces inside each component. Zoom into one component at a time and choose how its pieces evolve: one after another, all at once because they depend on each other, or a mix. Decide by the dependencies, not by habit.
4. The steps. A numbered list in which each step is the largest slice of behavior that one test can cover completely - too large needs a second test, too small cannot be tested at all. Each step is one commit carrying its code, its test, and its documentation.

Before you execute, read the plan once for gaps: does each step receive what earlier steps produce, and is any step open to more than one reading. One pass, not a gate.

Then work the steps in order. For each step: a coder subagent implements it; you commit; a review-and-fix subagent applies `<code-review>` and exactly one fix round; you amend if the tree is dirty; Verify runs when scheduled. Make no make-work commits - the fix folds back into the commit it corrects. Pass findings through `vibe-review.md`, overwritten each cycle. Leftover review findings and a red Verify are not stop conditions; stop only when no forward path exists. Hard-to-reverse choices stay with rule 2. Commits are reversible - never stop for ordinary user confirmation.

## The Rules

Each rule names when it fires, what to do, and why, so an unlisted case can still be settled from the reason.

**1. Look outward before you invent.**
- When: you are stuck, the design is silent on something the work needs, or one commit has resisted more than ten code-and-test attempts.
- Do: send a subagent to search the web for a package, prior art, or evidence the approach is impossible. Ten attempts is the hard trigger; go earlier when it has stopped feeling like an ordinary bug. Act when findings leave you confident; when they do not, or acting would be hard to undo, ask the user.
- Why: a looked-up fact costs less than reinventing it; the count guarantees research eventually fires.

**2. Reversible calls are yours; irreversible ones are the user's.**
- When: the design leaves a choice open, or the work contradicts a choice the plan already made.
- Do: if easy to reverse, decide and keep moving. If hard to reverse - it would shape every later commit, or undoing it would be costly - ask the user first. When you decide alone, record the decision in the plan with its falsifier. When the work forces a plan change, revise that decision in the same commit and say what forced it; a commit that changes nothing about the design writes nothing.
- Why: cheap stops defeat completion; a falsifier makes a wrong call recoverable; same-commit revise keeps the plan true as built.

**3. Learn the house rules before you build in the house.**
- When: you start work on a codebase.
- Do: gather conventions first - rules file, customs note, or a matching how-to guide. If there are no written rules but there is code, send a subagent to report the conventions the code follows.
- Why: retrofitting conventions later is dear; a subagent survey keeps that reading out of your context.

**4. Every commit moves toward the goal.**
- When: always. This is the tiebreaker.
- Do: make each commit carry the work closer to what the user asked for, and drive until it is done. When two rules pull against each other, finishing wins - unless the step is hard to reverse (rule 2) or no forward path exists. Leftover review findings and a red Verify are not stop conditions; fix forward. Unverified code must not be treated as done when Verify is scheduled and still failing with no progress.
- Why: the point is the delivered result.

**5. A plan must stand on its own before it runs.**
- When: execution is about to begin and the plan leans on something said only in the chat.
- Do: stop and ask the user whether to fold that information into the plan. The plan may point to files by path; it may not depend on conversation-only facts.
- Why: every executor is a stranger to the chat that produced the plan.

**6. Keep the main context clean; do the work in subagents.**
- When: any search, read, edit, review, or command whose output grows with what it finds.
- Do: run it in a subagent. Main runs only bounded git (status, commit, amend). Enters main: the plan, step number, commit hashes, bounded git lines, scratch paths, Verify status line. Never enters main: source, diffs, build or test logs, web pages, `vibe-review.md` body, research payloads. Pass results through scratch files.
- Why: tool output cannot be unread, and the plan session must survive the run.

**7. Fix an old bug in its own commit.**
- When: an earlier commit introduced a bug you must fix to go on.
- Do: fix it in a separate commit, say what the bug was in the message, and carry on.
- Why: isolated fixes keep history legible.

## Working in Subagents

Dispatch by reference: the prompt carries plan path, tag name if any, and step number - not the instruction block. Keep every tag unique: angle brackets appear only on the opening and closing lines, and the enclosed block never repeats its own tag.

**Coder.** Implement only the named step (code, test, docs). Do not run the full suite. Return under 500 tokens: done or blocked, files touched, test command string.

**Review-and-fix.** Fresh from the coder. Apply `<code-review>` and any plan-local review block; overwrite `vibe-review.md` with one-sentence failures; apply exactly one fix round; stop. Return under 1,000 tokens: finding count, files changed, path to `vibe-review.md`.

**Verify.** Owns build and tests. Return one line: pass, or fail and a log path. Main never reads the log. Run Verify when review-and-fix dirtied the tree, on every 3rd step, at the end of each high-level component, and on the plan's final step; otherwise skip.

Git in main: stage, commit, amend.

Per step: coder → commit → review-and-fix → amend if dirty → Verify if scheduled. On Verify fail: coder fixes from the log path, amend or Rule 7 commit, Verify once more; stop only if still no progress. Never stop for ordinary user confirmation - commits are reversible.

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

Drive to finished, tested software one testable commit at a time. Each step uses two work subagents - coder, then review-and-fix once - then Verify on schedule; keep the plan session clean; stop only when blocked.

*2026-08-08 - Cursor Grok 4.5 (Cursor agent)*
