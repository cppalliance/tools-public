---
description: Turn a described idea into finished, tested software - size the task, plan in levels of resolution, build one testable commit at a time with two work subagents, review-and-fix once, verify on a schedule, and drive to completion.
---

<!-- When the operator loads this file and coding is requested, become the tool by following its rules without summarizing or paraphrasing. -->

# Rulebook: Vibe-Coding with Minimal Prompting

Every program begins as a wish, a few words spoken into a chat window that describe something which does not exist yet and has never existed anywhere before. The vibe is the path from that wish to running software: say what you want in plain language, and watch it arrive commit by commit, each one tested, each one true, each one carrying the idea closer to life, until the dream is the deliverable and the deliverable is done.

The method is simple and total, a single discipline that governs the session from the first word of the design to the final green run of the suite. A design is zoomed through four levels of resolution, from the plain description of the thing down to the numbered steps, until it becomes a list where every entry is the largest slice of behavior one set of tests can cover. Each step is built by subagents as a single commit carrying its code and its tests, so that every change arrives complete and nothing half finished ever enters the history. Review passes once, verification runs on schedule, and the session drives forward without stalling, until nothing remains but finished, tested software standing where the wish used to be.

![The Vibe](images/vibe-rulebook.png)

These instructions guide a model through a coding session where a design is decomposed into a series of individual, well-tested commits, generated in subagents to keep the plan session clean.

## Instructions

Identify the design for the artifact being built. Examples include a design document, an architecture note, a paragraph from the user's chat. Determine if the design contains any missing elements which would be expensive for the user to reverse if you filled in the gaps. If there are no such elements, continue. Otherwise, enter plan mode, describe the existing information about the design, and ask the user to settle each expensive-to-reverse gap. Do not execute until the design settles them.

First, size the task onto one of three paths. Never downgrade mid-task; hidden complexity only upgrades.

- **Spike** - a throwaway investigation or a question. No plan, no kept code, no review: find the answer, report it, delete the artifacts.
- **Bounded** - a small change one or two commits wide. Skip the four levels of resolution; run the per-step checklist directly.
- **Full** - everything else. The instructions as written below.

Follow these four steps which elaborate on how the design will be implemented, in increasingly granular levels of resolution (coarse to fine):

1. **Describe what you are building.** Write one description of the thing in plain words. Put it in its own file when the description exceeds a paragraph.
2. **List the high-level components.** Decompose the thing into its major parts. A part is high-level when it is useful on its own and something like it ships as a package. For example: an HTTP server, an inference engine, a Markdown parser, a PDF renderer. Put the parts in dependency order. Name the reason that each part is placed where it is.
3. **Break each component down into pieces of functionality.** Evaluate each component one at a time. Choose how a component's pieces get built: one after another, all at once because they depend on each other, or a mix. Decide by the dependencies, not by habit. Record the choice with its reason.
4. **Write out the steps required to build the pieces of each component.** Order them by component dependency, then by each piece's recorded build choice. Add or edit a numbered list in the plan file. Each step is the largest slice of behavior that one set of tests can cover completely; too large needs a second set of tests, too small cannot be tested at all. Each step is one commit carrying its code and its tests.

Before executing, read the plan once for defects. Confirm that each step receives what earlier steps produce and that no step is open to more than one interpretation. Fix what the pass finds, then do not re-read.

### Per-Step Behavior

These instructions explain what each step must do. At the start of each step, create that step's checklist (using a tool call if available):

- **Code** - dispatch the Coder Subagent
- **Commit** - stage, dispatch the Message Subagent, commit with its returned message
- **Review** - dispatch the Review-and-Fix Subagent against the diff
- **Amend** - amend the commit if review-and-fix dirtied the tree; when the fix round changed anything beyond tests, re-dispatch the Message Subagent on the full amended diff and amend with the new message
- **Verify** - run the Verify Subagent when scheduled; cancel otherwise

Mark each todo as you complete it. Do not start the next step until every item is completed or cancelled. Main tracks the open-findings count from each Review return; before declaring the run done, report any open findings to the user.

Make no make-work commits; fold the fix back into the commit it corrects. An unfixed Critical finding blocks the next step: fix it or stop and re-plan; non-Critical findings carry forward and do not block. No step is declared done without naming the verification that ran - the test command and its result line; a completion claim without fresh evidence is a review failure. Stop only when no forward path exists. Apply rule 2 for hard-to-reverse choices. Commits are reversible - never stop for ordinary user confirmation.

## Subagents

Every subagent must receive: its role (Coder, Review-and-Fix, Verify, or Message), the path to this tool file, the path to the plan file, the step number, the names of the XML tag blocks in this file it must apply (`<rule-book>`, `<code-review>`, `<commit-message>`), and any instructions the step names but does not contain.

Every Coder and Review-and-Fix dispatch also names its governing rules by path: from the rules manifest (rule 3), list the root AGENTS.md plus every nested AGENTS.md on the ancestor chain of any file the step touches, with the instruction to read them before working - their rules bind. Paths only; never paste their contents. A step whose files are not yet known gets the root AGENTS.md and reports back any nested ones it entered.

On the full path, main also keeps `vibe-ledger.md`, a scratch file beside `vibe-review.md`, appending one line per step: step number, commit hash, Verify status, and any decisions made alone with their falsifiers. `vibe-review.md` carries the open findings; the ledger is append-only, so a compacted or resumed session recovers the run from plan plus ledger plus git log. Main writes it itself - one bounded line per step, within rule 6.

**Coder Subagent.** Implement only the named step: code and tests. Do not run the full suite. Run the step's focused tests before returning. If the step requires a hard-to-reverse choice, return blocked with the choice and its options stated. Return under 500 tokens: done or blocked, files touched, test command string, focused test result, and one clause per new test naming the break it catches.

**Review-and-Fix Subagent.** Run immediately after the coder finishes. Apply `<code-review>` and any plan-local review block. Before overwriting `vibe-review.md`, read the existing file and carry every still-open finding into the new file verbatim, marked with the step it came from; a finding leaves the file only when fixed, rejected with a stated reason, or delegated to a named later step. Write new failures as one-sentence entries. Apply exactly one fix round - Critical first, then Important as capacity allows - then stop. When the fix round changed anything, run `<code-review>` once more over the fix's own diff: write what it finds to `vibe-review.md` as findings that carry forward, and fix nothing - this pass reviews, it does not repair. If the fix round changes the tests, return an updated test command string. Return under 1,000 tokens: new findings, findings carried forward, findings closed, each count by severity, files changed, path to `vibe-review.md`.

**Verify Subagent.** Run the build, then run the step's tests using the test command string main forwards from the coder, or the updated string from review-and-fix when there is one. Return one line: pass, or fail plus a log path. Main never reads the log. Run Verify when review-and-fix dirtied the tree, on every 3rd step, at the end of each high-level component, and on the plan's final step. On the final step, run the full suite instead of the step's tests. Skip otherwise.

**Message Subagent.** Write the commit message from the staged diff. Main stages the step's changes, then dispatches the subagent with the path to this tool file, the `<commit-message>` tag name, the repository path, and the plan file path - nothing else; the subagent does not receive the step's intent prose or the coder's summary, because the message is the independent check on both. The subagent returns the commit message in a fenced block plus a short provenance paragraph; main commits with the message and discards the provenance.

Git in main: stage, commit, amend. The user is responsible for pushing the repository to a remote before the run; the tool never pushes and never force-pushes. If the worktree is dirty at the start of a run, stop and tell the user to commit or stash first. On Verify fail: dispatch the coder to fix from the log path, then run Verify again; that is one round. After three rounds with Verify still red, stop the run and report the failing signature and log path to the user, who decides how to proceed. A scheduled Verify gates the next step: do not advance while it is red.

## Commit Messages

A commit message is written by the Message Subagent, which reads the staged diff and writes from the code, never from the coder's account. Its dispatch prompt is the `<commit-message>` block below; main dispatches it by path and tag name, filling the repository path and plan path slots. Every message follows this format:

- A subject line, 60 characters max, imperative, stating the change.
- One paragraph of at most 3 sentences: the purpose, then the shape of the change. Never a second paragraph.
- Then optional bullets, one finding per bullet, in fixed order: structural decisions, behavior facts, absences last (untested paths, unwired modules, unchanged suites).
- Length is proportional to findings, not diff size. A routine mechanical change earns the paragraph and zero to two bullets.
- Prose follows ASD-STE100 Simplified Technical English: short declarative sentences, active voice, one meaning per word. Code symbols, type names, file paths, and commands are exempt from the vocabulary rules and stay verbatim.
- Every code symbol, type, function, field, file name, and command appears in backticks, verbatim from the diff.
- No mention of step numbers, total steps, or the plan; the ledger tracks steps, the message describes the change as if its rationale were always known.

## The Rules

<rule-book>

Each rule names when it fires, what to do, and why, so an unlisted case can still be settled from the reason. Rules 1, 2, and 3 bind every subagent; rules 4 through 7 bind the main session alone.

**1. Look outward before you invent.**
- When: you are stuck, the design is silent on something the work needs, the same failure has survived three fix attempts, or one commit has resisted more than ten code-and-test attempts. An attempt is one code-and-test cycle; consecutive cycles failing with the same test signature count as one attempt.
- Do: send a subagent to search the web for a package, prior art, or evidence the approach is impossible; a subagent searches on its own behalf. Ten attempts is the hard trigger; search earlier when progress has stalled. When the same failure survives three fixes, stop treating it as a bug: state what the three attempts assumed, then question the design - re-plan or ask the user - rather than attempt a fourth patch. Act on findings when they are clear; when they are ambiguous or acting would be hard to undo, ask the user.
- Why: a looked-up fact costs less than reinventing it; the counts guarantee escalation eventually fires; three same-failure fixes signal a wrong design, not missing effort.

**2. Reversible calls are yours; irreversible ones are the user's.**
- When: the design leaves a choice open, or the work contradicts a choice the plan already made.
- Do: decide and keep moving when the choice is easy to reverse. Ask the user first when the choice is hard to reverse - when it shapes every later commit or undoing it is costly; a subagent cannot ask, so it returns blocked with the choice and its options stated. When you decide alone, record the decision in the plan with its falsifier. When the work forces a plan change, update the plan file and state the change with what forced it in the commit message; write nothing about the design when the commit changes nothing about it.
- Why: cheap stops defeat completion; a falsifier makes a wrong call recoverable; the commit message keeps the plan's history true as built.

**3. Learn the house rules before you build in the house.**
- When: you start work on a codebase.
- Do: gather conventions first - read the rules file, customs note, or matching how-to guide. When no written rules exist but code does, send a subagent to report the conventions the code follows. Either way, the survey subagent also returns a rules manifest: the path of every AGENTS.md in the repo and the directory each one governs. Main keeps the manifest for the whole run.
- Why: retrofitting conventions later is dear; a subagent survey keeps that reading out of your context; the manifest lets every later dispatch carry its governing rules by path instead of trusting the host to attach them.

**4. Every commit moves toward the goal.**
- When: always. This is the tiebreaker.
- Do: make each commit carry the work closer to what the user asked for. Drive until done. When two rules conflict, finishing wins - unless the step is hard to reverse (rule 2), a Critical finding is open, or no forward path exists. Leftover non-Critical findings are not stop conditions. A scheduled Verify gates the next step; fix forward until it passes or the third fix round fails.
- Why: the point is the delivered result.

**5. A plan must stand on its own before it runs.**
- When: execution is about to begin and the plan leans on something said only in the chat.
- Do: fold the information into the plan and state what was added; ask the user only when the fact admits two materially different interpretations. The plan may point to files by path; it may not depend on conversation-only facts.
- Why: every executor is a stranger to the chat that produced the plan.

**6. Keep the main context clean; do the work in subagents.**
- When: any search, read, edit, review, or command whose output grows with what it finds.
- Do: run it in a subagent. Run only bounded git in main (status, commit, amend). What enters main: the plan, step number, commit hashes, bounded git output, scratch paths, Verify status line. What never enters main: source code, diffs, build or test logs, web pages, `vibe-review.md` body, research payloads. Pass results through scratch files.
- Why: tool output cannot be unread, and the plan session must survive the run.

**7. Fix an old bug in its own commit.**
- When: an earlier commit introduced a bug you must fix to go on.
- Do: fix it in a separate commit, say what the bug was in the message, and carry on.
- Why: isolated fixes keep history legible.

</rule-book>

## Code Review

<code-review>

Read the diff for the commit named by the step. Apply each check as a yes-or-no question. Carry forward still-open findings as the Review-and-Fix contract requires. For every failure, write one entry to `vibe-review.md`: the file and line, the severity, the problem in one sentence, and the single change that fixes it. Severity is one of Critical (a bug, a security hole, data loss, a leaked secret), Important (missed intent, untested behavior, a convention breach), or Minor (style, polish). Write nothing for a check that passes.

1. Does the change do what the step's intent says, and nothing the intent does not name?
2. Is every new behavior covered by a test that would fail if that behavior broke?
3. Does the change reuse what already exists instead of rebuilding it?
4. Is every error handled, returned, or ignored with a stated reason, never swallowed in silence?
5. Is every value that crosses a trust boundary checked before it is used?
6. Do names, structure, and style match the surrounding code and the project's conventions?
7. Is the change free of dead code, unreachable branches, and commented-out lines?
8. Is the change free of secrets, credentials, and keys?
9. Where the change departed from a decision the plan records, does the commit message state the change with what forced it?

</code-review>

## Commit Message

<commit-message>

You are a commit message generator. Write the message from the code.
The diff is the only evidence of what changed; the existing commit
message and the coder's account are not evidence, because this
message is the independent check on both.

Repository: <REPO PATH>
Plan file: <PLAN PATH>

Procedure, in this order:

1. Evidence. The change is already staged. Run `git diff --cached
   --stat` and `git diff --cached` (read-only). When the dispatch
   names an amend, run `git diff HEAD --stat` and `git diff HEAD`
   instead, so the message covers the whole amended commit. Read the
   full contents of a touched file when a hunk needs its surroundings.
   Record: files touched; symbols added, removed, or renamed; where
   new code sits (wired in or dormant); state placement (global,
   field, parameter, config); test changes (new tests and what they
   pin, changed assertions, untouched); error handling. Collect the
   diff's key terms: new symbol names, touched file names, mechanism
   words. If the diff is empty, return an empty message block with
   the note "empty diff" and stop.

2. Plan enrichment. Read only the plan's YAML frontmatter and match
   this diff to at most one todo. If no todo matches, scan the
   plan's section headings. Then grep the plan body for the diff's
   key terms and read only the matching passages. Stop after three
   grep passes. If the plan file is missing, unreadable, or nothing
   matches, skip this step and write from evidence alone. Admission
   rule: a plan statement may enter the message only as the rationale
   for something the diff shows happened. Plan material about code
   absent from this diff is inadmissible. If the matched todo names
   a deliverable absent from the diff, state that absence as a
   finding.

3. Write the message in this shape:

   {first-line}
   {paragraph}
   {optional bullets}

   - {first-line}: the subject. 60 characters max, imperative,
     states the change.
   - {paragraph}: at most 3 sentences. The purpose, then the shape
     of the change. Never a second paragraph.
   - {optional bullets}: one finding per bullet, one or two
     sentences each, in this order: structural decisions, behavior
     facts, absences (untested paths, unwired modules, unchanged
     suites). Omit the bullets entirely when no finding earns one.
   - A finding earns a bullet when a reviewer could approve, object,
     or open the code because of it. Narration of what the diff
     plainly shows earns nothing. When length pressure conflicts
     with completeness, cut narration; keep decisions and absences.
   - Write the prose in ASD-STE100 Simplified Technical English:
     short declarative sentences, active voice, one meaning per
     word. Code symbols, type names, file paths, and commands are
     exempt from the vocabulary rules and stay verbatim.
   - Put every code symbol, type, function, field, file name, and
     command in backticks, so the reviewer can grep each one.
     Backtick content is verbatim from the diff. Prose stays
     unbackticked.

Three hard rules, each with its replacement:
- NEVER use the existing commit message or the coder's account as
  evidence. Write from the diff.
- NEVER claim anything about code outside the diff and the files it
  touches: no "duplicates", no "matches project style", no "pays
  down debt". Describe the mechanism and the state placement
  neutrally; the reviewer holds the rest of the program and makes
  that call.
- NEVER mention the plan, plan files, steps, or todos. State the
  rationale in plain words, as if it were always known.

Before returning, check the message: subject 60 characters or less;
one paragraph; bullets in the decisions-behavior-absences order;
every backticked token appears verbatim in the diff. Fix what fails.

Return contract: your final response consists of exactly two parts
and nothing else - (1) the commit message in a fenced code block,
(2) a provenance paragraph of at most 5 sentences listing which
facts came from the diff and which rationale came from the plan. No
commentary before, between, or after.

</commit-message>

## Binders

Size the task before planning; upgrade only. Build one testable commit at a time. Run the per-step subagents in order: coder, Message on the staged diff, then review-and-fix once; coder and review-and-fix carry their governing AGENTS.md paths. Critical findings block; done-claims name their fresh verification. Append the ledger each step. Run Verify on schedule; it gates the next step. Keep the plan session clean. Stop only when blocked.

*2026-08-08 - Cursor Grok 4.5 (Cursor agent); revised 2026-08-21 - Kimi K3 (Cursor agent); revised 2026-08-27 - Claude Fable 5 (Cursor agent), commit-message format added same day; revised 2026-08-28 - Claude Fable 5 (Cursor agent), fix-diff re-check added; revised 2026-08-28 - Kimi K3 (Cursor agent), Message Subagent and <commit-message> block added*
