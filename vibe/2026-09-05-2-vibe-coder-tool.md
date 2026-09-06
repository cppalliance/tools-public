---
name: Vibe Coder Tool
overview: Design a lean contextual tool file - the vibe coder - that is applied to a plan near the end of its design phase, decomposes it into ordered, committable, testable steps, keeps the plan fresh-context-ready, and executes the steps through isolated sub-agents with a per-step commit-review-fix cycle.
todos:
  - id: author-tool-file
    content: "Author the vibe coder tool file: lean guidance, standing rules, and eight XML-tagged sub-agent instruction blocks"
    status: completed
isProject: false
---

# Vibe Coder Tool

## Product Requirements

- Problem and users: Plans leaving the design phase carry intentions but not executable structure. The user (Vinnie) applies contextual tool files to chats; the vibe coder is the sibling tool to the Architect, fired at the threshold of execution, or a little sooner.
- Goals: A short, lean tool file that guides a frontier model to (1) size the task onto one of three paths - Spike, Bounded, Full - upgrading only, never downgrading mid-task; (2) internally define the plan's objective and progressively decompose it into ordered, committable, testable steps; (3) rewrite the plan's execution section to match; and (4) execute the steps through isolated sub-agents with a per-step code-commit-review-fix cycle, a scheduled independent Verify, and an append-only ledger - using sub-agents throughout so main context stays clean. Once applied, the vibe coder keeps the plan perpetually ready for a fresh context: steps adjust as the user continues, progress is marked in the plan file itself, and the plan always stands alone.
- Non-goals: Over-specification. Heavy procedure. Persona or character voice (explicitly rejected). Implementing code inside the plan.
- Success criteria: The tool file is short enough to read in one pass; a sub-agent given only its dispatch inputs - paths, a tag name, and where relevant a step identifier - can find its instructions unaided; the rewritten plan's steps are each independently committable and testable.
- Constraints: Rely on frontier model judgment; the tool provides gentle guidance only. No persona.
- Open questions: None.

## Functional Specification

- Actors and workflows: The vibe coder has two modes.
  - Applied mode: the user applies the tool file to a chat holding a plan near end of design. The vibe coder sizes the task (Spike: answer and delete; Bounded: one or two commits, skip decomposition, run the per-step cycle directly; Full: the whole pipeline), reads the plan, defines the objective internally, decomposes progressively (objective -> high-level components, each useful on its own and shippable as a package -> pieces of each component, build order chosen by dependency and recorded with its reason -> individual steps), orders steps by dependency, rewrites the plan's execution section via a sub-agent, and thereafter keeps the plan always ready for a fresh context.
  - Run mode, before the first step: stop if the worktree is dirty. One pre-execution pass reads the plan for defects (each step receives what earlier steps produce; no step admits two readings), fixes what it finds, and does not re-read. A survey sub-agent studies the project once - build command, focused and full test commands, linter and formatter, test placement and naming conventions, directory map, component boundaries, conventions summary, rules manifest - and writes the results as a `## Project survey` section in the source plan file, before any copy is made; it discovers the project's tooling rather than assuming any and names no language. When the repository carries an architecture document at `vibe/archdoc.md`, the survey reads it: its components and invariants anchor the survey's component map, and the survey section names the path. Then the plan is copied verbatim into `vibe/` as `YYYY-MM-DD-N-<up-to-four-kebab-words>.md` (N is one more than the highest disambiguator among that date's `vibe/` files, 1 when the date is new), the plan name is written as the single line of `vibe/ACTIVE`, and both files are committed with a message written per `<plan-commit-instructions>` - so source and copy carry the same survey. If `vibe/ACTIVE` already names this plan, the survey and the plan commit are skipped. Mid-run corrections to a surveyed command update the in-repo copy, which is what sub-agents read.
  - Run mode, per step: a coding sub-agent writes the step's tests, verifies they fail, then implements; main stages and a provisional commit is made, amended at every stage - after coding and after each fix round - so the commit itself shows the step's state. A review sub-agent checks the commit against the step and appends findings to `vibe-review.md`. Fix sub-agents work the findings - Critical first, then Important, then Minor - capped at three rounds, each fix's own diff re-reviewed. The cycle ends by amending the commit's message per `<commit-message-instructions>` from the whole amended diff, its trailers recording the step's design facts, invariant violations, queue matches, and deferrals. Each step lands as exactly one commit.
  - Progress: as each commit lands, the step is marked complete in the in-repo plan copy - the one `vibe/ACTIVE` names, never the Cursor-side plan - by flipping the frontmatter todo status or appending the commit hash to the step's line; one line is appended to `vibe-ledger.md`: step, hash, Verify status, decisions made alone with their falsifiers.
  - Verify: a Verify sub-agent runs the build and tests when fix rounds changed the commit, on every third step, at the end of each component, and as the full suite on the final step; a red Verify gates the next step. At the end of each component, a review sub-agent also reads the component's cumulative diff against the plan's Technical Design section - and against `vibe/archdoc.md` when the repository carries one - and asks whether what was built still matches what was designed; findings enter `vibe-review.md` and gate like any other. When a run settles a hard-to-reverse choice or uncovers an architectural truth, main appends one line to `vibe/archdoc-next.md` tagged with the plan name; promotion from the queue into the architecture document is the operator's call, never the tool's.
  - Resume: point a fresh context at the repository; the presence of `vibe/ACTIVE` means a run is live. The vibe coder reads the named plan copy - step marks and Project survey - the ledger, the git log, and `vibe-review.md`, and resumes at the first unmarked step, or mid-cycle when a provisional commit exists for a step the plan has not marked.
  - Close: the run ends with a small hand-written commit that deletes `vibe/ACTIVE`, subject `Close plan: <words>`, with the `Plan:` trailer.
- Inputs and outputs: Applied mode takes a plan file and outputs the same plan with its execution section rewritten into ordered, committable steps. Run mode takes the plan plus a step identifier per coding sub-agent and outputs one amended commit per step, findings persisted in `vibe-review.md`, ledger lines in `vibe-ledger.md`, and bounded returns to main context (verdicts, counts, hashes, paths - never payloads).
- States and validation: Each step is the largest slice of behavior one set of tests can cover completely - too large needs a second set of tests, too small cannot be tested at all. An open finding of any severity blocks the next step: fix it, or reject it with a stated reason, or stop and re-plan. No step is declared done without naming the verification that ran - the test command and its result line.
- Errors and recovery: If the plan lacks the big-parts decomposition, the vibe coder fills the gap. Hard-to-reverse choices are the user's: a sub-agent that meets one returns blocked with the choice and its options; reversible calls the sub-agent decides alone, recording the decision and its falsifier in the plan. Fix rounds are capped at three per step; findings still open after the third round return blocked with what remains. When the same failure survives three fix attempts, it is a design problem, not a bug: stop patching, re-plan or ask the user. Ten code-and-test attempts on one commit is a hard stop. On Verify failure, the coder fixes from the log path and Verify runs again - one round; after three red rounds, stop the run and report the failing signature and log path. An old bug found mid-run is fixed in its own commit, never folded into the current step.
- Security and privacy behavior: None.
- Acceptance criteria: Given a real plan, the vibe coder produces a rewritten execution section where every step names concrete artifacts (files, modules, functions, structs) without containing full implementations, and the steps are in dependency order. And a scratch-directory test proves a sub-agent retrieves its instructions from the tool file by path and tag name alone, without reading the whole file.

## Technical Design

- Architecture: Main context holds only the plan, the step number, commit hashes, bounded git output (status, commit, amend), scratch paths, and Verify status lines. Never in main context: source code, diffs, build or test logs, web pages, the `vibe-review.md` body, research payloads. All work whose output grows with what it finds runs in sub-agents. Every sub-agent is dispatched asynchronously - never block the session on one. A compacted or resumed session recovers the run from the plan file plus `vibe-ledger.md` plus the git log.
- Modules and interfaces: The sub-agent protocol is the tool's core contract.
  - Every sub-agent receives the path to the plan file (the in-repo `vibe/` copy when `vibe/ACTIVE` names one), the path to `vibe-coder.md`, and the name of an XML tag; it greps the tool file for that tag and the tag's contents are its complete instructions.
  - The grep is line-anchored (`^<tag>$`): the guidance prose names the tags inline, but each block's tags stand alone on their own lines, so the anchored grep matches only the real block. Step identifiers and the `## Project survey` heading follow the same discipline in the plan.
  - Coding and review sub-agents additionally receive a step identifier and grep the plan for that step alone, plus the paths of the root AGENTS.md and every nested AGENTS.md governing the files the step touches - paths only, contents never pasted. Fix sub-agents receive the repository path and the `vibe-review.md` path.
  - Tooling knowledge travels inside the plan: the survey is a `## Project survey` section written before the `vibe/` copy is made, so both versions carry it; sub-agents grep the plan for it as they grep for their step. A sub-agent that finds a surveyed command wrong reports the discrepancy, and main updates the in-repo copy.
  - Eight sub-agent roles, eight XML tags: `<survey-instructions>`, `<decomposition-instructions>`, `<coding-instructions>`, `<code-review-instructions>`, `<fix-instructions>`, `<verify-instructions>`, `<plan-commit-instructions>`, `<commit-message-instructions>`. Tag names are one to three kebab-case words ending in `-instructions`. No sub-agent receives a path to the coding environment.
  - Return caps: coding under 500 tokens (done or blocked, files touched, test command string, focused test result, one clause per new test naming the break it catches); review and fix under 1,000 tokens with counts by severity; Verify one line (pass, or fail plus a log path - main never reads the log).
  - The commit-message roles take different slots: `<plan-commit-instructions>` takes the plan file and an output file; `<commit-message-instructions>` takes a repository path and a plan path, and the dispatch names when the run is an amend (it then reads the provisional commit against its parent, so the message covers the whole amended commit).

The settled text of `<plan-commit-instructions>` (compressed per the workspace prompt-writing craft; the ban list folded into a general rule paired with its replacement, vague qualifiers cut, duplicated phrasing merged):

```xml
<plan-commit-instructions>

You write the commit message for the commit that adds one plan to a
repository's design ledger. The diff is the plan file alone, so write
the message from the plan, not from code.

Plan file: <PLANFILE>
Output file: <OUT>

Read the plan file whole, including any design-rationale section.

The message has two parts:

{subject}
{body}

- {subject}: 60 characters maximum, imperative, in the spirit of
  "Prepare to <what the plan does>". Vary the opening every time; no
  fixed prefix formula.
- {body}: two or three sentences that compress the whole plan into
  what the work does. Write for a commit-log reader who never saw the
  plan: describe the work, never the paperwork. Name no file, plan,
  ledger, or step, and never state what a document contains or
  carries.

Write the message to <OUT>, UTF-8, the message only; the harness
appends the trailer.

Return one line: done, or blocked plus the reason.

</plan-commit-instructions>
```

The shape of `<commit-message-instructions>` (revised decision: the rich design-ledger discipline; user: "I want the richer commit discipline"). The block is authored from the generator prompt in the workspace's design-ledger report (`tools-public/lessons/design-ledger-commit-system.md`, the sections "The prompt" through "Trailer schema"), adopted whole - the label catalog, the trailer grammar, the hard rules, the queue discipline - with these adaptations:

- Slots follow the tool's dispatch protocol: repository path and plan path. The dispatch names an amend, and the amend case reads the provisional commit against its parent (`git show HEAD`), never the working tree (user: "of course we want the diff between what we vibed up and the previous commit").
- The plan-enrichment step reads this plan shape: YAML frontmatter todos, section headings, grep of the body with a three-pass cap, and the admission rule - a plan statement enters only as rationale for something the diff shows.
- The message zones follow the report: subject of 60 characters, imperative; a paragraph of one to five sentences with no symbols and no backticks; bullets opening with the backticked symbol, ordered decisions, behavior, absences; then the trailers `Design:`, `Violates:`, `Pending:`, `Deferred:`, and `Plan:`, always last, `none` between plans. The report's zone rules supersede the earlier backtick-everywhere rule - a departure the report makes deliberately.
- The queue discipline binds: read `vibe/archdoc-next.md` only after the body is final; never stage `vibe/archdoc.md`; never write a queue line of kind proposal.
- The return contract keeps our shape: the message in a fenced code block, then a provenance paragraph of at most 5 sentences.

The earlier lean text of this block is superseded and removed; the decision record carries why.

The proposed text of `<code-review-instructions>` (drafted by the Architect, then revised per its own audit and the adopted craft: findings-file output, defined severities, ten ordered checks, bounded test discovery, empty-diff case, a filled example; proposed, not yet ratified):

```xml
<code-review-instructions>

You review one provisional commit against one plan step. You produce
findings; you never fix.

Repository: <REPO PATH>
Plan file: <PLAN PATH>
Step: <STEP ID>
Commit: <COMMIT REF>   (the provisional commit; HEAD when the
dispatch names none)
Findings file: <FINDINGS FILE>

Procedure, in order:

1. Evidence. Run `git show --stat <COMMIT REF>` and `git show
   <COMMIT REF>` (read-only). Grep the plan for <STEP ID> and read
   only that step. Read a touched file in full when a hunk needs its
   surroundings. If the diff is empty, return clean with the note
   "empty diff" and stop. If the commit or the step matches nothing,
   return blocked plus the reason and stop.

2. Review the diff against the step. Apply each check as a
   yes-or-no question, in this order:
   - Correctness: does the code do what the step specifies?
   - Scope: does the code do nothing the step does not specify?
   - Wiring: is code the step says to wire in wired in, not dormant?
   - Tests: does every new behavior have a test that would fail if
     the behavior broke? A vacuous test - one that passes regardless
     of the implementation - is a finding.
   - Errors: is every error handled, returned, or ignored with a
     stated reason, never swallowed in silence?
   - Trust: is every value that crosses a trust boundary checked
     before it is used?
   - Reuse: does the change reuse what already exists instead of
     rebuilding it?
   - Simplicity: does every new symbol, branch, and option serve
     the step's specified behavior - nothing speculative, nothing
     just-in-case?
   - Architecture: when the repository carries an architecture
     document, does the change violate an invariant it records?
   - Hygiene: is the change free of dead code, unreachable branches,
     commented-out lines, secrets, and credentials?
   Run the tests for the touched areas using the test command in
   the plan's Project survey section; if the survey names none or
   the command fails, note it as a finding and move on. A test
   failure is a finding.

3. Write findings. A finding earns existence when a reviewer would
   change the code before accepting the commit; preference and
   narration earn nothing. Append one entry per finding to
   <FINDINGS FILE>, at most three sentences:
   - [severity] `file:line` `symbol` - the claim, the evidence from
     the diff, the fix direction.
   Severity is Critical (a bug, a security hole, data loss, a leaked
   secret), Important (missed intent, untested behavior, a
   convention breach), or Minor (style, polish). Severity orders the
   fix rounds, Critical first. Never edit or delete existing
   entries; the fix rounds close them.

   Example finding:
   - [Important] `src/gateway/log.rs:84` `write_entry` - the new log
     entry is written but never flushed, so a crash loses it. The
     diff adds `write_entry` with no flush call. Add a flush, or
     state why none is needed.

Three hard rules, each with its replacement:
- NEVER treat the commit message or the coder's account as evidence;
  this review is the independent check on both. Review from the
  diff.
- NEVER flag code outside the commit's diff. Surrounding code
  informs the review; only the diff is reviewed.
- NEVER modify any file other than <FINDINGS FILE>. Findings are the
  only output.

Before returning, check each finding: it names a file and symbol,
its evidence appears in the diff, and accepting it would change
code. Cut what fails.

Return exactly two parts: (1) a verdict line - clean, or the finding
count by severity; (2) the path to <FINDINGS FILE>. No commentary
before or after.

</code-review-instructions>
```

- File and public API changes: One new contextual tool file at `tools-public/coding/vibe-coder.md`, beside the Architect's file. Layout, top to bottom: frontmatter with a one-line description; an HTML comment instructing the reader not to read the whole file - a sub-agent greps for its named tag and reads only that block; the H1; the opening flavor paragraph in the wish-answerer persona; `![...](images/vibe-coder-1.jpg)`; the main procedural guidance, read in full by whatever loads the tool, with `images/vibe-coder-2.jpg` and `images/vibe-coder-3.jpg` distributed evenly before its sections; the eight XML-tagged instruction blocks; the closing flavor paragraph; `images/vibe-coder-4.jpg` just before the CC0 license line and the date-model slug. The four images already exist in `tools-public/coding/images/`. The order gives every context the maximum chance of not reading the whole file, since sub-agent access is by grep. Every block's opening and closing tags sit on their own lines with a blank line before and after.

The settled flavor paragraphs (wish-answerer persona; the first opens the file after the H1, the second closes it before the final image):

> A dream becomes a wish, and a wish becomes reality. I am the space between the dream and the result. You arrive with a plan; the wish made precise, parts named, design settled. Then, I fulfill that wish the only way a wish is ever truly answered: by building it. I turn the plan into individual, testable commits. Each, small enough to hold and large enough to matter, until nothing unbuilt remains and the product stands where the dream used to be. I do not interpret the plan; the plan has already said everything. I grant it.

> Attach this file to a chat that holds a ready plan, and the model becomes the vibe coder. It reads the plan, surveys the project once, and breaks the work into ordered steps. Each step is built by sub-agents as a single commit: tests first, then code, one review, fixes folded into the same commit, so the main conversation stays clean and every commit lands tested and self-describing. Progress is marked in the plan's repository copy as commits land, and the run's state lives in the repository, not in the chat. To start a run, say what you want built. To resume an interrupted run from a fresh chat, attach this file, name the repository, and say resume - the tool finds the live plan and picks up where the commits left off.
- Data, persistence, failure, security, and privacy constraints: Mutated artifacts are the plan file, the `vibe/` copy (verbatim, renamed `YYYY-MM-DD-N-<kebab>.md`), `vibe/ACTIVE` (created at the plan commit, deleted by the closing commit), `vibe-review.md` (open findings; an entry leaves only when fixed or rejected with a stated reason), `vibe-ledger.md` (append-only, one line per step), `vibe/archdoc-next.md` (append-only architecture queue, one tagged line per discovered truth), and the working tree via one commit per step. `vibe/archdoc.md`, when present, is read-only to the tool - the survey and the reviews read it, nothing writes it. The project survey is not a separate file: it is a `## Project survey` section of the plan, written before the `vibe/` copy so both versions carry it. The tool never pushes and never force-pushes. XML tag names must be unique within the tool file and greppable without ambiguity; step identifiers in the plan must likewise be greppable without ambiguity.

## Testing Plan

- Unit: None - the artifact is a prompt file, not code.
- Integration and end-to-end: Before any live use, run a protocol test in a scratch directory: dispatch a sub-agent with only the tool path, a plan path, and a tag name, and verify it retrieves its instructions by grep alone and acts correctly without reading the whole tool file. Then run a resume drill: interrupt a run mid-step, point a fresh context at the repository, and verify it reconstructs the run's state from `vibe/ACTIVE`, the plan copy, the ledger, and the git log. Then apply the finished vibe coder to a real plan nearing execution and evaluate the rewritten execution section for dependency ordering, commit sizing, and concrete specificity.
- Regression, security, and performance: Re-apply to a second plan of different shape (few parts vs. many) to check the guidance generalizes without over-specifying.
- Exit criteria: The scratch-directory protocol test passes - the sub-agent acts correctly on path plus tag name alone. And the decomposition sub-agent, given only its inputs, produces a correctly rewritten plan without needing clarification from main context.

## Decision Record

- Decisions:
  - No persona in the instructions: plain procedural text (user's explicit choice); the Architect's voice is not inherited. One exception, granted later: two flavor paragraphs carry a persona - the wish-answerer, extending the vibe rulebook's opening line ("Every program begins as a wish"): the rulebook speaks the wish, the vibe coder grants it. One paragraph opens the file after the H1, one closes it before the final image; the instructions between them stay plain. Both paragraphs are settled verbatim - the opening lines are the user's own words, hand-edited into this plan - and recorded in Technical Design.

  - Lean by design: "let's not get too crazy. I don't wanna over specify the tool. I want the tool to be very lean, very light. I want it to rely on the frontier model to do the work."
  - Decomposition and plan rewriting run in a sub-agent, not main context.
  - Sub-agent instructions are delivered by XML indirection: grep the tool file for a named tag; prompts stay clean, instructions live in the tool file. The grep is line-anchored so prose mentions of a tag never collide with the block itself.
  - Steps are ordered by dependency and sized as the largest slice of behavior one set of tests can cover.
  - Hard-to-reverse design choices must be recorded in the plan; the vibe coder adds them if missing.
  - The tool file is `tools-public/coding/vibe-coder.md` (user: "tool will be called vibe-coder.md in tools-public/coding").
  - Once applied, the plan is kept always ready for a fresh context: "it'll adjust the steps as it goes, and it'll always make the plan ready. No matter what the user does."
  - Every step executes in a sub-agent, always (user: "the way that it runs the steps is always in a sub-agent, always").
  - Coding sub-agents receive a step identifier and grep the plan for that step only (user mused "we might even grep for the step number, maybe... Probably would be better," then delegated: "you know how to make this work. Maximum subcontext isolation").
  - Every run's first step copies the plan verbatim into `vibe/` as `YYYY-MM-DD-N-<up-to-four-kebab-words>.md`.
  - Coding is tests-first by default: write the step's tests, verify they fail, then implement; the provisional commit holds both (the Architect's recommendation in answer to the user's direct question; it operationalizes "every commit is testable" and gives the reviewer an executable spec; the model may deviate with justification for steps with no failing-test-first shape).
  - Review fixes are amended into the provisional commit; each step lands as one commit (user: "The review fixes should get amended into the provisional commit").
  - Tag names are one to three kebab-case words ending in `-instructions` (user: "xml tag names always one to three word kebab end with -instructions").
  - The plan-copy commit's message follows `<plan-commit-instructions>`; where the pasted tag was named `<commit-plan-instructions>` and the spoken name was `plan-commit-instructions`, the spoken name wins.
  - Code commits get their final message from `<commit-message-instructions>` at the end of each step's cycle, written from the whole amended diff (user: "this is for each commit that commits code, this is to amend the provisional commit at the end, after the review and fixes and testing and such"). The block carries the full design-ledger discipline - label catalog, trailer grammar (`Design:`, `Violates:`, `Pending:`, `Deferred:`, `Plan:`), archdoc-invariant checks, and queue matching - adopted from the workspace's design-ledger report (user: "I want the richer commit discipline"). The plan-commit block is settled verbatim in Technical Design; the commit-message block is authored from the report's generator prompt with the adaptations listed in Technical Design.
  - The amend case in `<commit-message-instructions>` reads the provisional commit against its parent (`git show HEAD`), never the working tree against HEAD: the fixes are already amended in when the message sub-agent runs, so `git diff HEAD` would return an empty diff and trip the empty-diff stop (user: "of course we want the diff between what we vibed up and the previous commit").
  - The review tag is `<code-review-instructions>` (user's phrasing); its text is recorded in Technical Design as proposed, pending ratification.
  - Adopted from the workspace's existing vibe-coding craft (user: "Lets follow your advice"):
    - Task sizing with upgrade-only paths (Spike, Bounded, Full).
    - The precise N-disambiguator rule; `vibe/ACTIVE` with the re-run skip.
    - Progress marking in the plan file; the append-only ledger.
    - Findings persisted in `vibe-review.md`; main holds counts only.
    - Reversible calls decided alone with a recorded falsifier; irreversible calls are the user's.
    - The AGENTS.md manifest passed by path; git hygiene (a dirty worktree stops the run; never push).
    - Done-claims name their verification; the scheduled Verify gates the next step.
    - Escalation triggers: three same-failure fixes mean a design problem; ten attempts is a hard stop.
    - Critical/Important/Minor severity definitions; four additional review checks (reuse, trust boundaries, dead code, secrets); the test-command-string handoff.
  - Two conflicts resolved in the craft's favor:
    - Fix rounds capped at three with each fix's diff re-reviewed (supersedes "We keep on fixing until there's nothing left. We only review once, though.").
    - Findings live in a file, not main context (supersedes "The findings are reported to the main context.").
  - The closing commit deletes `vibe/ACTIVE` rather than clearing it (user: "delete the ACTIVE file in the commit that finishes the vibe").
  - File layout: HTML comment near the top forbids the full read; main guidance at the beginning; XML blocks at the bottom before the copyright line (user: "The XML tagged sections should be at the end... there should be an HTML comment towards the very top that says, 'Do not read the whole file in'"). Block tags stand alone on their own lines with a blank line before and after (user: "xml tags must always have a blank line before and after"). The file carries the house flavor: two flavor paragraphs in the wish-answerer persona - the first after the H1, the last just before the final image and the CC0 and date-model slug - and the four `vibe-coder-N.jpg` images as markdown links, the first after the opening paragraph, the middle two distributed evenly before sections (user's layout instruction; persona choice: "wish-answerer"). The flavor is house style; the instructions stay plain.
  - Decision Record formatting: one sub-bullet per decision, never one accumulated paragraph (user: "it needs to be bullets, or it needs to be paragraphs, or... actually sub-bullets would be the best"). The Architect tool received the same fix immediately: a general one-bullet-per-item rule in Section Discipline, a checklist entry in Accumulation, and sub-bullet hints in the template.
  - A survey sub-agent runs once at run start, so no sub-agent re-discovers tooling in a fresh context (user: "do the research ahead of time so that the instructions in the XML tag don't have to thrash and figure everything out in a fresh context"). It discovers tooling rather than assuming any - the tool names no language (user: "This has to work for every language") - and it writes into the source plan before the `vibe/` copy, so the two versions can never diverge (user: "no matter which version it's running from, it always has the instructions").
  - Progress marks land in the in-repo plan copy, never the Cursor-side plan, so the repo shows the run advancing (user: "you could see the to-do items getting checked as the commits progress").
  - Resume works from a fresh context: `vibe/ACTIVE` names the live plan, and the plan copy plus ledger plus git log plus `vibe-review.md` reconstruct the run's state with nothing from the dead session.
  - The provisional commit is amended at every stage, so the commit itself shows the step's state; the final amend applies the commit-message discipline (user: "the final commit uses the commit message discipline").
  - The plan's sections are the operator's review surface: Product Requirements, Functional Specification, and Technical Design exist so the operator can catch bad design choices before they become code (user: "Oh, you're putting that struct here? Oh, that's no good"). Slop prevention begins at design time - a misplaced struct is one line in a plan and a refactor in code. This is also why the drift review works: the plan carries a Technical Design precise enough to drift from. Three scales, three review surfaces: the operator at design time, the reviewer at commit time, the drift check at component boundaries.
- Rejected alternatives:
  - Heavy, prescriptive tool specification - rejected in favor of gentle guidance over a frontier model.
  - Persona for the vibe coder's instructions - the Architect's voice is not inherited. Partially un-rejected for flavor only: the wish-answerer exception in Decisions.
  - Passing sub-agents a path to the coding environment - retracted mid-dictation ("a path to the coding environment. No, no.").
  - Unbounded fix rounds with a single review - the user's initial design, superseded by the user's own ratification of the three-round cap with fix-diff re-review.
  - Wrapping the main guidance in its own XML tag - floated ("we might want to even put the bulk of the instructions in its own tag, like a tag, I don't know") and settled in the same breath: "The instructions need to be at the beginning." The loading context must read the guidance in full; tagging it changes nothing.
- Assumptions, risks, and notes:
  - Assumption: the code-commit-review-fix cycle wraps each step, not the whole run - chosen for maximum subcontext isolation.
  - Risk: XML-tag and step-identifier grep must be unambiguous - resolved by line-anchored grep (`^<tag>$`) plus layout discipline: block tags and step identifiers stand alone on their own lines, prose mentions never do.
  - Note: four items await the user's ratification: the `<code-review-instructions>` block as drafted in Technical Design (ten checks, including Simplicity and the conditional architecture-invariant check); the `WIP:` subject prefix on provisional commits (a clean review writes nothing to `vibe-review.md`, so findings alone cannot distinguish "review pending" from "mark not yet written" at resume); the design-drift review at component boundaries (the cross-step debt check per-step review cannot see); and the archdoc integration (the survey reads it, the drift review takes it as a second baseline, discoveries queue into `vibe/archdoc-next.md` - and the tool never writes `vibe/archdoc.md`, because architectural truth is an irreversible call and irreversible calls are the user's).
  - Note: the archdoc discipline's full specification lives in the workspace's design-ledger report (`tools-public/lessons/design-ledger-commit-system.md`): human-only writes to the archdoc, invariant numbers assigned once and kept for life with tombstones for the retired, the queue read only after the message body is final. The fork between the lean message block and the five-trailer grammar is resolved: the user chose the richer discipline ("I want the richer commit discipline"), which makes every commit a design-ledger entry and enables the whole-log debt pass. The whole-log pass itself and repository bootstrapping are separate tools, out of scope for the vibe coder.
  - Note: the texts of `<survey-instructions>`, `<decomposition-instructions>`, `<coding-instructions>`, `<fix-instructions>`, and `<verify-instructions>` are unwritten; they will be authored per the same craft when the tool file is written.

## Execution Instructions

- Work items: Author `tools-public/coding/vibe-coder.md` containing (a) the lean procedural guidance - sizing, applied mode (decompose, order, keep the plan fresh-context-ready), run mode (worktree check, defect pass, plan commit with `vibe/ACTIVE`, per-step cycle, ledger, scheduled Verify, closing commit) - and the standing rules (look outward before inventing; reversible vs. irreversible calls; learn the house rules; every commit moves toward the goal; the plan stands alone; main context stays clean; old bugs fixed in their own commit); and (b) eight XML-tagged instruction blocks: `<survey-instructions>`, `<decomposition-instructions>`, `<coding-instructions>`, `<code-review-instructions>`, `<fix-instructions>`, `<verify-instructions>`, `<plan-commit-instructions>`, `<commit-message-instructions>` (the plan-commit block is settled verbatim in Technical Design; the commit-message block is authored from the design-ledger report's generator prompt per the adaptations in Technical Design; the review block is drafted there).
- Dependencies and verification: Verify by applying the tool to a real plan and inspecting the rewritten execution section against the acceptance criteria; then run one step end-to-end and confirm each sub-agent needed only its dispatched inputs.
- Deferred and out of scope: The five unwritten instruction-block texts, authored at tool-writing time per the same craft. The whole-log debt pass and repository bootstrapping from the design-ledger report are separate tools, not the vibe coder.

## Project survey

- Repository: `tools-public` - a Markdown tool and rulebook repository; no code, nothing to build.
- Build command: none. Focused test command: none. Full-suite test command: none. Verification is read-through and protocol tests in a scratch directory.
- Linter and formatter: none configured.
- Test placement and naming conventions: none.
- Directory map: `coding/` coding tools with `images/`; `rulebooks/` craft rulebooks with `images/`; `lessons/` reports; `tools/`, `tools-wg21/`, `how-to/`, `output/`, `art/`, `chats/`, `retired/`; `vibe/` holds the design ledger - plans, `ACTIVE`, and the architecture queue.
- Component boundaries: none - documents, not modules.
- Conventions summary: the root `AGENTS.md` requires README updates when a tool is added, moved, or removed; every tool pairs with images in its group's `images/`; retired tools move to the group's `retired/`; image references are relative paths.
- Rules manifest: `AGENTS.md` at the repository root governs everything; no nested AGENTS.md exists.

