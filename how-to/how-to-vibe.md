---
description: Turn a described idea into finished, tested software - plan in levels of resolution, build one testable commit at a time, review each commit in a fresh context, and drive the whole thing to completion.
---

<!-- Load this file before vibe-coding any change beyond a trivial one-line edit. You are this tool: follow its rules, do not summarize it, operate from it. -->

# How to Vibe

Everyone carries something they wish existed: an app, a website, a tool, a small machine that does one useful thing well. For most of history the road from wanting it to running it was paved with years of craft, and most dreams never made the trip.

This file shortens that road to a conversation. Describe what you want to build, in whatever words you have, and the discipline in these pages turns the description into a plan, the plan into working and tested software, and the wish into something real you can open and use. It demands no credential: a seasoned engineer and a first-time builder start the same way, by saying what they want. You bring the vision and the judgment; the method brings the rigor and the thousand small steps, and it keeps working while you rest. Come back to something finished, and then build the next thing.

![The Practice](images/how-to-vibe-code.png)

Two things hold this whole file together: drive the work to a finished, tested result, and keep the session that holds the plan clean by doing the work in subagents. Everything below serves those two.

## The Loop

Vibe-coding has a fixed shape. You start with a design and end with tested software, and you cross the distance one testable commit at a time.

Begin with a design. A design document, an architecture note, a paragraph in the chat - anything that says what to build. When it is vague, fleshing it out is the work itself: turn it into a plan, and let plan mode be where you do that. A wish becomes buildable only once it is written down.

Zoom the plan through levels of resolution, coarse to fine:

1. What you are building. One description of the thing, in plain words. It may live in its own file.
2. The high-level components. The big moving parts: an HTTP server, an inference engine, a Markdown parser, a PDF renderer. A part is high-level when it passes a bright line - it is useful on its own, and something like it ships as a package. Put the parts in dependency order, and name the dependency that fixes each one's place.
3. The pieces inside each component. Zoom into one component at a time and choose how its pieces evolve: one after another, all at once because they depend on each other, or a mix. Decide by the dependencies, not by habit.
4. The steps. A numbered list in which each step is the largest slice of behavior that one test can cover completely - too large needs a second test, too small cannot be tested at all. Each step is one commit carrying its code, its test, and its documentation.

Before you execute, read the plan once for gaps: does each step receive what earlier steps produce, and is any step open to more than one reading. One pass, not a gate.

Then work the steps in order. For each step: write the code, commit it, review the commit, fix what the review finds, amend the commit, confirm it builds and passes, and move on. Make no make-work commits - the fix folds back into the commit it corrects. Write the code in one subagent, review it in a second with a fresh view, and apply the fixes in a third, passing the review's findings through a scratch file you overwrite each cycle, never through the session that holds the plan.

## The Rules

These bind every step. Read them before you act. Each names when it fires, what to do, and why, so that a situation the instruction does not spell out is still one the reason can settle.

**1. Look outward before you invent.**
- When: you are stuck, the design is silent on something the work needs, or one commit has resisted more than ten code-and-test attempts.
- Do: send a subagent to search the web for the missing piece - a package that already does it, prior art to follow, or evidence the approach is impossible and should be dropped. Ten attempts is the hard trigger; go earlier when the difficulty surprises you, when it has stopped feeling like an ordinary bug. Act on the findings when they leave you confident; when they do not, or when acting would be hard to undo, ask the user.
- Why: a fact you can look up costs less to find than to reinvent, and searching first spares you from rebuilding a package or walking a path already known to end nowhere. The count guarantees research eventually fires; the surprise judgment lets it fire sooner, and stating the reason is what tells an ordinary bug from a wall worth researching.

**2. Reversible calls are yours; irreversible ones are the user's.**
- When: the design leaves a choice open.
- Do: if the choice is easy to reverse, make it and keep moving; do not stop to ask. If it is hard to reverse - it would shape every later commit, or undoing it would be costly - ask the user first. Whenever you decide on your own, record the decision in the plan and name its falsifier, the one thing that would later show it was wrong.
- Why: the goal is a finished result the user wakes to, so stopping for cheap choices defeats it, while a costly-to-undo choice earns the one interruption. A logged decision with a falsifier turns a wrong call into something the user can find and reverse, instead of a silent trap sprung later.

**3. Learn the house rules before you build in the house.**
- When: you start work on a codebase.
- Do: gather its conventions first. Look for a rules file or a short customs-and-conventions note. Look in the how-to directory for a guide that matches the language or the project, and load whatever matches. If there are no written rules but there is code, send a subagent to read the codebase and report the conventions it actually follows.
- Why: conventions honored from the first commit keep your work of a piece with what is already there, and retrofitting them later is dear. A matching guide hands you the lay of the land that reading the source cold would take far longer to learn, and surveying by subagent keeps that reading out of your own context.

**4. Every commit moves toward the goal.**
- When: always. This is the tiebreaker.
- Do: make each commit carry the work closer to what the user asked for, and drive until it is done. When two rules pull against each other, finishing the goal wins - unless finishing would take a hard-to-reverse step, which belongs to rule 2, or would ship unverified code, which the build and the tests forbid.
- Why: the point is the delivered result. A commit that does not move toward it is motion without progress.

**5. A plan must stand on its own before it runs.**
- When: execution is about to begin and the plan leans on something said only in the chat, never written into the plan.
- Do: stop and ask the user whether to fold that information into the plan so it stands alone. The plan may point to other files by path; it may not depend on anything that exists only in the conversation.
- Why: a plan run in a fresh context, or by a subagent, cannot see the chat that produced it, so anything left there quietly vanishes. A self-contained plan is the only kind a stranger can run correctly, and every executor is a stranger.

**6. Keep the main context clean; do the work in subagents.**
- When: any search, read, edit, review, or command whose output grows with what it finds.
- Do: run it in a subagent, not in the session that holds the plan. Run a command yourself only when its output is bounded no matter what it finds - a commit, a status line, a fixed query - and dispatch everything else. Pass results between subagents through a scratch file, not through your own context. Do not ask yourself to read source, a diff, or any large artifact; when the file never names the read, the read never happens.
- Why: the main context holds the plan and has to survive the whole run, and tool output cannot be unread - a command that prints two lines on success and four hundred on failure has already spent your attention by the time you learn which one you got. A read you never ask for is one nothing can tempt you into.

**7. Fix an old bug in its own commit.**
- When: you find that an earlier commit introduced a bug you must fix to go on.
- Do: fix it in a separate commit, say what the bug was in the message, and carry on.
- Why: an isolated, documented fix keeps the history legible and keeps the correction from tangling with unrelated work.

## Working in Subagents

Rule 6 says keep the main context clean. This is how.

Dispatch by reference, never by copy. A subagent's prompt carries only what it cannot reconstruct: the path to the file it must read, the name of the tag to find inside it, an instruction to grep for that tag and read the lines it encloses, and the one value that changes per run, the step number. Never spend output writing the instructions themselves into the prompt. A prompt that carries no instruction block cannot be shortened under pressure into one that drops half its constraints; a prompt that inlines the block can, and eventually will.

Keep every tag unique. A tag's angle brackets appear on exactly two lines, its opening and its closing, and nowhere else, and the enclosed block never writes its own tag again. Then a grep for the tag finds precisely the two lines that bound it. Stray angle brackets elsewhere would pull the grep to the wrong place, so keep them out.

To build a step, hand the subagent the whole plan by path and the step number, and tell it to implement only that step. The whole plan gives it the shape of the work; the scope line keeps it from wandering into the next step. Do not wrap each step in its own tag - that bloats the plan and breaks tag uniqueness.

To review a commit, the reviewer reads two things: the general checks in the code-review block below, and any project-specific checks the plan carries in its own review block. It reads the diff, and it writes what it finds to `vibe-review.md`, overwritten each cycle. That file is what the fixer reads.

Keep git in the main context, where its output is bounded: stage, commit, amend. The subagents only edit, review, and fix. So the cycle runs: a subagent writes the code, you commit, a reviewer writes findings to `vibe-review.md`, you send the fixer to that file, the fixer edits, you re-run the build and the tests, and you amend.

Before you dispatch, run it once in your head. Resolve exactly what the subagent will receive - the path, the tag, the step number, and the lines the grep will return - and check it is right. A subagent gets only what the dispatch names, so a dispatch that names the wrong thing fails silently, and this preview is the cheapest place to catch it.

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
</code-review>

## In One Breath

Describe the thing, turn it into a plan, and drive the plan to finished, tested software one testable commit at a time. Plan in levels: what you are building, then the high-level parts in dependency order, then the pieces, then steps each sized to a single test. Work every step in subagents - write, review with a fresh view, fix - and land one clean commit. Look outward when blocked, make the reversible calls yourself and escalate the irreversible ones, learn the house rules first, keep every commit pointed at the goal, and keep your own context clean by doing the work somewhere else.

*2026-07-29 06:58 - Opus 4.8 (Cursor agent)*
