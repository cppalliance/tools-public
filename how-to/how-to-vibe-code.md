---
description: Drive a design document to a complete tested implementation through hierarchical plans, subagent-only execution, and a review-and-amend cycle on every commit
---

<!-- Load this file before planning or implementing any change beyond a single-file mechanical edit. Run the Protocol (section 1). -->

# Vibe-Coding Planner

Rules for taking a design document to a finished, tested implementation without accumulating debt on the way. This file governs any change to code beyond a single-file mechanical edit. Sections run in execution order and are consulted one at a time, so the length of this file is never the number of rules you hold at once.

![The Practice](images/how-to-vibe-code.png)

Terms hold one sense throughout. The **design document** is the input written before any code, immutable once it passes admission. A **`design.md`** is an append-only log written during implementation; the design document and `design.md` are different files with different lifetimes. A **check** is one review criterion inside a criteria block; a **test** is executable code in the repository. A **criteria block** is a tag-delimited block dispatched to a subagent by name. The **main context** is the session holding the plan. A **work subagent** edits files; a **review subagent** reads and reports.

## 1. Protocol

Execute these steps in order:

1. Confirm the design document passes the admission test of section 3. If it does not exist or fails, name what is missing and stop.
2. Write `plan/L1.md` (section 4).
3. Write one L2 plan per L1 step (section 5).
4. Run the plan-audit gate (section 6). Advance only when it returns no findings.
5. Execute one step at a time (section 7), opening each with research (section 8) and closing it with code, tests, and a checkpoint (section 9).
6. Run the commit cycle after every commit (section 10).
7. Append to the decision log as decisions arise (section 11).
8. Run the Checklist (section 14) before reporting the work complete.

## 2. Two standing rules

These two bind every phase. Every other rule in this file is phase-local and binds only inside its own section. They are restated at the end.

**Subagent discipline.** The main context holds the plan, dispatches work, and records outcomes. It does not read source files and it does not write code. Reason: context accumulation degrades every model measurably, with degradation beginning well before the window fills, and the plan is the artifact that has to survive the whole run. Dispatch in parallel when no dispatch in the batch reads a file another writes; otherwise dispatch in order. If the same step fails dispatch twice, read the one file named in the failure, then re-dispatch.

**The commit cycle.** Author the commit, review it in fresh-context subagents, verify the findings, fix the survivors, confirm the suite dispatch returns pass, amend the commit. One commit per step, with the fix folded in rather than following behind. Reason for reviewing in a separate context: a model asked to review its own work in the context that produced it does worse than not reviewing at all, moving GPT-4 on GSM8K from 95.5% to 91.5% after one round and 89.0% after two, and models favor their own output when they can see it. Reason for amending rather than adding a commit: rewriting is safe before publishing and unsafe after, and a fix folded into the commit it fixes keeps one concern per commit. The amend choice rests on convention, not measurement; no study has compared it.

### What the main context may run

**The test: bounded output.** Run a command in the main context only when the command bounds its own output independent of the state it reads. Dispatch everything whose output size depends on whether something went wrong. Reason: tool output cannot be unread, so a command returning two lines on success and four hundred on failure has already spent the attention budget by the time the caller learns which case it got. Classification happens before the command runs.

The two lists below are examples of the test applied, not an exhaustive enumeration, because an exhaustive list needs a new entry for every new command while the test already decides them all.

Permitted, examples: read and write the plan files and both `design.md` files; dispatch subagents; `git add`, `git commit`, `git commit --amend`; the fixed-size query forms `git rev-parse`, `git branch --show-current`, and `git log --oneline -n <k>`; record findings that subagents return.

Dispatched, examples: the build and the test suite, because a red run is unbounded; the parent-commit replay of section 9; `git diff` and every command that emits the diff, since the diff is the review subagents' input and reading it in the main context defeats the cycle it feeds; `git checkout` and `git status`, whose output scales with conflicts and working-tree state; reading any source file; writing any code; searching the codebase; web research.

Classify a command on neither list by the test, not by resemblance to a listed one. When its bound is genuinely unknown, dispatch it: a needless dispatch costs one subagent, a wrong guess costs the run.

**Inspection without loading.** Where the main context needs a fact about something large, dispatch a query for the fact rather than the thing: the count of failing tests rather than the suite output, the paths a diff touches rather than the diff, whether a symbol exists rather than the file defining it. Reason: almost any question about a large artifact has a bounded form, and this is what keeps the bounded-output test from becoming a wall.

**When a permitted command overruns anyway.** Finish the current step, write `plan/state.md`, and start a fresh main context that reads that record cold. Move the offending command to the dispatched list for the rest of the run and record the reclassification in the root `design.md`, creating that file if it does not exist yet. Reason: the context is already polluted and cannot be cleaned, so the remedy is recovery rather than a rule that pretends otherwise.

### Artifact paths

Use these paths. Reason: a path the agent has to search for is a path it will not find, and a name that states its purpose costs nothing.

- `plan/L1.md` - the ordered step list.
- `plan/L2-<NN>-<slug>.md` - one per L1 step, numbered so the order is visible in a directory listing.
- `plan/state.md` - progress, decisions taken, problems open, and the working set of file paths. The sole run-state record.
- `design.md` at each package root, and at the repository root for cross-package decisions.

### Compaction

Compact the main context at 70% of the window. Write `plan/state.md` first, then restart from it.

What survives: the decisions taken, the problems still open, the current L2 step, and the working set of file paths. What does not: tool results already acted on, superseded findings, and the text of any file still on disk. Clear consumed tool results before anything else, because a tool result already acted on is the cheapest thing to drop. Where recall and brevity conflict in a compaction, recall wins; dropped context is unrecoverable while superfluous content only costs tokens.

### Technique choice

This design runs on notes plus subagents. The work has clear milestones, one commit per L2 step, so state belongs in files at the paths above; exploration parallelizes, so it belongs in subagents. Compaction is the fallback for a main context that grows anyway, not the primary mechanism. Reason for naming the choice: the three techniques combine, and leaving the choice unstated invites all three at once.

Pre-load the rules and retrieve the data. The two standing rules and the current L2 step stay in context and are re-injected on the interval in section 7. Source files, diffs, and research arrive through a dispatch at the moment of use. Reason: an agent that loads instructions on demand can act before it has read the rule governing the step.

### How task text travels

A task travels by reference when any one of these holds:

- The task text runs over 10 lines.
- The task carries a quantified constraint, an enumerated list, or an output schema.
- The task is dispatched more than once per run.

A task meeting none of the three inlines in the prompt. Travel by reference takes one of two routes, and the prompt carries only the pointer:

- Fixed text goes in a criteria block in this file, and the prompt carries this file's path plus the tag name.
- Run-specific text goes in the L2 plan on disk, and the prompt carries the plan path plus the step number.

Reason: under context pressure a dispatcher compresses a large inline prompt, and the summary drops exactly the quantified constraints and ordered steps that carry the task's value. A prompt with no block in it cannot be compressed into one, which is a structural guarantee that an instruction not to paraphrase cannot match.

### The subagent contract

Every dispatch supplies all six elements, because what a task omits the subagent invents.

- **Objective** - one sentence.
- **Output format** - the findings schema below for review dispatches; a named artifact path for work dispatches.
- **Sources and tools** - this file's path and the tag name, plus the diff or the files in scope.
- **Boundaries** - review dispatches read and report, editing nothing; work dispatches edit only the files their L2 step names.
- **Effort budget** - the number stated in the dispatching section.
- **Return cap** - 1,000 to 2,000 tokens of distilled result, however many the subagent consumed internally. When the result does not compress that far, return the summary plus a path to the full text.

Every check and every dispatch defines its behavior on the empty, missing, and malformed case. Where a section below does not name one, the default is to report the condition and stop rather than to proceed on an assumption.

A dispatched prompt takes this form:

```
Read tools-public/how-to/how-to-vibe-code.md, grep it for
<defect-review>, and apply every check in that block to the diff of
HEAD. Intent of this change: <one line from the L2 step>. Read and
report only, editing nothing. Return the findings schema.
```

Review dispatches return this schema, evidence before verdict so the verdict is not written first and justified after:

```
- check: <block name>/<check number>
  evidence: <file>:<line range> and the quoted construct
  verdict: fail
  fix: <the one change that clears the check>
```

Three filled examples, one per evidence shape the review blocks produce:

```
- check: defect-review/2
  evidence: src/store.rs:88-91, `Err(_) => Ok(Default::default())`
  verdict: fail
  fix: return the error to the caller; the default masks a missing key
       and a corrupt value identically

- check: semantic-review/1
  evidence: src/parse.rs:12-40 `split_fields` duplicates
    src/lex.rs:88-120 `tokenize_row`; searched split, field, tokenize
  verdict: fail
  fix: call tokenize_row and delete split_fields

- check: test-review/4
  evidence: tests/store.rs:31, expected value is `store.encode(k)`,
    the same call the assertion is testing
  verdict: fail
  fix: assert the literal wire bytes the format requires
```

Findings return in the response, not as a file, so the main context holds them for the fix dispatch and no extra artifact drifts out of sync with the commit. Identifiers travel and payloads do not: a finding carries `file:line` and one quoted construct, never the surrounding function.

## 3. The design document

Write no code without one. It holds every decision the implementer would otherwise invent, so implementation is execution rather than design.

Required elements:

- An executive summary closing on a recommendation and a confidence level.
- A prior-art survey naming the closest existing systems and what each one lacks.
- An architecture section with a diagram, stating what each layer owns and what it does not.
- A primitives list, where every mechanism named later in the document is a composition of the listed primitives. Name any mechanism that is not.
- One section per design decision.
- Worked examples, each with four parts: the artifact itself, the signatures it calls, the expected execution trace, and the tests.
- Explicit non-goals.
- A build path naming the riskiest assumption and the fastest way to retire it.
- A confidence level per area.
- References.

A decision section takes this shape:

```
The decision, stated as already made. The evidence, with specific
numbers and a citation. The tension the choice creates, named rather
than hidden.
```

**Admission test.** Every decision the implementer would otherwise invent is already made. An open choice is a gap, not latitude. Where the document leaves one open, name it and stop; do not close it by writing code.

## 4. The L1 plan

One file, `plan/L1.md`. One ordered step per package or independently checkpointable subsystem.

Order steps by dependency and name the dependency that forces each position, so the ordering is auditable rather than asserted: crate B before crate A when A depends on B. Each step declares the functionality that exists at its checkpoint and the path of its L2 plan.

```
# L1

## 1. store - no dependencies
Checkpoint: a keyed value round-trips through the on-disk format.
L2: plan/L2-01-store.md

## 2. index - depends on store for the key type
Checkpoint: a query returns matching keys from a populated store.
L2: plan/L2-02-index.md
```

## 5. L2 plans

One file per L1 step. Decompose until each step is the smallest unit of functionality that produces something testable.

**Stop condition.** A step is small enough when you can name the one test that goes red before it and green after. A step that still fails the stop condition gets an L3 plan. Cap the depth at L3: if an L3 step still fails the stop condition, split its L1 step in two and re-plan rather than adding an L4, because unbounded recursion is the failure mode here.

Each step carries four named fields. The intent field is quoted verbatim into every review dispatch, so write it as one line a reviewer can test against.

```
## 3. Encode the key prefix

intent: a key encodes to its length-prefixed bytes and decodes back
        to the same key.
files: src/key.rs, tests/key.rs
test: tests/key.rs::roundtrip_prefix
research: none - the format is fixed in the design document
```

## 6. The plan-audit gate

Dispatch to a review subagent given the plan files and no conversation history. Reason for a separate context: an audit run in the context that wrote the plan defends the plan.

Effort budget: one pass over the plan tree, no web access.

Fix findings in the plan files and re-run the audit. The tree does not advance while a finding stands. Stop on no progress: an audit returning no findings, or failing to reduce the open count, ends the loop. Hard cap of three audits, then report and stop.

Reason this is a gate and not a formality: across 16,991 coding-agent trajectories, a subpar plan hurt success more than supplying no plan at all. An unaudited plan is worse than the absence of one.

<plan-audit>
Objective: audit a plan tree for defects that would surface during execution. You have the plan files and nothing else. Read and report only.

Apply all six checks and report every failure.

1. Data flow. For every artifact a step names as an input, does some earlier step create it by an explicit instruction? Report any artifact referenced but never commanded into existence.
2. Ordering. Does any step depend on something a later step builds?
3. Grain. Does any step do two jobs? Does any step resist naming the one test that goes red before it and green after?
4. Combining and parallelism. Can any two adjacent steps merge into one? Which steps touch disjoint file sets and can run in parallel?
5. Design coverage. Is every decision in the design document traced into some L2 step? Report decisions with no step.
6. Ambiguity. Is any step open to two readings? Quote both.

Output format, one entry per failure:

- check: plan-audit/<number>
  evidence: <plan file>:<step number> and the quoted text
  verdict: fail
  fix: <the one edit that clears the check>

Report "no findings" when all six pass. Return at most 2,000 tokens.
</plan-audit>

## 7. Execution

Execute one step at a time, in order, dispatching per section 2. Execution does not edit the plan files. Reason: a plan edited mid-execution stops being the artifact the audit approved.

The rule is narrower than freezing the plan, and the difference matters: execution cannot revise the plan, and a step that discovers the plan is wrong halts and re-enters the audit gate of section 6. That is a replanning path, run through an audit rather than through the executor's own judgment.

**Re-inject the plan every 5 steps.** Restate the current L2 step and the two standing rules into the working context at least once every five steps. Reason: periodic plan re-injection is the one intervention measured to reduce plan violations and improve success across every model tested, over 16,991 coding-agent trajectories.

**This ordering is a bet under test, not a settled result.** The comparison of a plan-then-execute discipline against mid-execution replanning has never been run on a coding benchmark. Where the ablation exists in other domains, replanning wins, by 10.31 points on one web-navigation benchmark and 8 points on one planning benchmark. Against that, 81.28% of tasks in one corpus were solvable by fully static plans with none requiring runtime replanning, so task shape may drive the gap, and the affirmative case for pre-committed control flow is integrity rather than accuracy, bought at roughly 7 points of utility in the one system that measured the trade.

On drift, revert and take the failure back to the plan rather than patching forward, because a patch stacks compromise on the original mistake.

## 8. Research before each step

Dispatch 1 to 3 subagents to search the web about the specific thing the step is about to do, one per research question the L2 step names.

Effort budget: 3 to 8 searches per question, compressed summaries only, raw pages stay in the subagent.

**Skip decision rule.** Search when the step uses an external package, API, protocol, or file format. Skip when it touches only code the plan already specifies, and record the skip in one line so it is auditable.

**When the budget runs out unanswered.** Record the question as unresolved in the package's `design.md` and proceed with the step. Do not search past the budget and do not drop the question silently, because an unresolved question that leaves a trace can be revisited while one that vanishes reads as answered.

**Priority against section 7.** A finding that invalidates a step is a plan defect, so it returns through the audit gate rather than being absorbed inline.

<research-task>
Objective: find what a developer would want to know before writing this step, and return only what changes the step.

Search for each of these, in this order:

1. Whether every package, module, or API the step names actually exists, at the version the step would pin.
2. Known bugs, advisories, and CVEs against what the step would use.
3. A better-suited alternative that is already established for this job.
4. Breaking changes between the pinned version and the one the step assumes.
5. The idiomatic pattern for this job in the current version, where it differs from the obvious one.

Effort budget: 3 to 8 searches. Follow a lead when it bears on one of the five items above; stop when it does not.

Output format, 1 to 5 entries, highest impact first:

- item: <which of the five>
  finding: <2 to 4 sentences, with the version numbers and dates>
  source: <url>
  changes_the_step: yes or no, and if yes, what

Report "nothing that changes the step" when that is the answer; it is a valid and useful result. Return at most 2,000 tokens. Raw pages stay with you.
</research-task>

Reason the first item leads: hallucinated package references run 4.62% to 6.10% across five frontier models released between October 2025 and March 2026, with 127 names invented identically by all five, so a package that does not exist is a live risk rather than a hypothetical.

## 9. Code, tests, checkpoint

Every commit that changes behavior carries tests for that change.

**The parent-commit replay.** One dispatch that checks out the parent, applies only the test files, runs them, and returns how the new test failed.

**The gate is an assertion failure, not any failure.** A test counts as failing on any thrown error, including a syntax error, so "it fails against the parent" is trivially satisfied: one measurement found 55.4% of attempts reaching any-failure against 10.1% reaching a genuine red-to-green. The discriminator is the failure class. A test failing on the parent with an assertion failure is a valid test 50.4% of the time; one failing with an import, module, or type error 9.1% of the time; one that passes on the parent 0%. An error-class failure does not satisfy the gate.

What the gate buys when enforced this way: tests satisfying it reached 0.91 to 0.96 change coverage of the fix's own lines, indistinguishable from developer-written tests at 0.93 to 0.99, while tests failing it reached 0.49 to 0.59. It stays necessary rather than sufficient, which is why `<test-review>` also checks what the assertion says.

Reason for making it blocking: across 86,156 agent-authored test patches from 33,596 pull requests spanning five coding agents, 80.2% carried weak or no explicit oracle signal.

Three edge cases:

- The test does not compile against the parent because it calls a new API. Stub the new symbols in the parent working tree, confirm the assertion still fails, and record that the replay used stubs. Reason: an uncompilable test is an error-class failure in the 9.1% band, and stubbing is what converts it into the 50.4% assertion band.
- The commit changes no behavior, meaning formatting, comments, or a pure rename. Record "no behavior change" in the commit body and skip the replay. The suite still has to pass.
- The replay contradicts expectation, passing where it should fail or failing where it should pass. Re-run it once before treating the result as authoritative. Reason: one harness marked a known-correct patch incorrect on 30 of 300 instances, a 10% non-deterministic rate erring in both directions.

**Checkpoint.** The commit itself, once the build dispatch and the suite dispatch both return pass and the test named in the L2 step's test field passes. The step named one test; that test is the checkpoint's evidence.

## 10. The commit cycle

Four stages: review, verify, fix, amend.

**Review.** Dispatch four review subagents in parallel, one per tag: `<redundancy-review>`, `<defect-review>`, `<test-review>`, `<semantic-review>`. Each receives the diff, the L2 step's intent field, this file's path, and its tag name. None receives the authoring transcript, which is the mechanism the cycle depends on. Effort budget: one pass per block.

**Verify.** Dispatch one verifier against `<finding-verification>`. It receives the collected findings and the diff, and nothing else. Effort budget: one pass. Reason this stage exists: a critic validating every finding against the source before synthesis cut false positives 40%, raised line-number accuracy from 67% to 92%, and dropped hallucination from 32% to 18%. Without it the fix stage acts on line numbers that do not exist.

**Fix.** Dispatch one work subagent per file the surviving findings touch, in parallel when no two findings touch the same file. Effort budget: one pass per finding, editing only the files that finding names.

**Amend.** Confirm the suite dispatch and the parent-commit replay both still pass, then amend.

**Loop control.** Re-run the cycle on the amended commit. Stop on no progress: a cycle producing no surviving findings, or failing to reduce the count of open findings, ends the loop. Hard cap of three cycles, then report and stop. Reason for a progress test rather than a recurrence test: marginal gain per round in an unassisted loop runs 266.7%, then 92.2%, then 11.5%, but a loop fed new execution facts each round climbed from 73.8% to 84.1% over twenty rounds, so the knee tracks how much new information a round carries rather than the round number.

Refinement is not monotonic: a fix cycle can introduce findings the previous state did not have. The amended commit's predecessor stays recoverable from the reflog, so a regressive cycle can be dropped rather than built on.

### The review blocks

These are audit criteria applied one at a time, so their count is not a constraint budget. Every check is a question with a pass or fail answer.

Three blocks hold checks decidable from the diff alone with no project configuration. One block holds checks needing evidence from outside the diff, capped at 4 and dispatched on its own. Reason for splitting by what a check must read rather than by count: judge agreement is governed by criterion evidence type at nine times the weight of how the criteria are batched, and a batch of 20 to 35 binary items costs nothing while four evidence-heavy items over a long trajectory costs double digits.

**Routing rule for a new check.** Decide by what the check must read to answer, in this order: if it needs evidence from outside the diff, `<semantic-review>`; if it is about a test file, `<test-review>`; if a failing answer means the code is wrong, `<defect-review>`; otherwise `<redundancy-review>`. Reason: subject overlaps across blocks, but what a check must read does not.

**One assumption to hold loosely.** Splitting review across parallel specialists is supported: five role-specialized agents reached F1 0.892 against 0.754 for one agent holding all criteria, with precision rising to 0.901 from 0.741 rather than trading away, because specialization decorrelates error modes where repeated identical passes do not. Overlap measured lower than expected, median pairwise Jaccard about 0.37, with 56.5% of confirmed defects found by exactly one reviewer. But those studies split by role across a whole artifact; none splits a fixed criteria list into disjoint blocks the way this design does, so the transfer is an inference. The counterweight: 36.94% of failures in multi-agent systems trace to misalignment between agents, a surface that exists only because the work was split, which is the second reason the verify stage is not optional.

<redundancy-review>
Objective: find work this diff duplicates or does not need. Read and report only. Apply all 15 checks to the diff and report every failure.

1. Does any block of 6 or more consecutive statements appear twice in the diff, or once in the diff and once already in the repository?
2. Does the diff add the same literal in two or more places without one referencing the other? Count any number other than -1, 0, 1, 2; any string longer than 2 characters; any regex; any schema, field, route, or error-code name.
3. Does the diff implement a hash, checksum, encoding, serialization format, comparison ordering, validation rule, or ID scheme that is already implemented elsewhere in the repository?
4. Does the same set of case labels or type discriminants appear in 2 or more switch, match, or if-else-if chains after this diff?
5. Does the same set of 3 or more parameter or field names appear together in 2 or more signatures or declarations?
6. Does the diff add a function, variable, parameter, field, import, or type with zero references, or a statement that cannot be reached?
7. Does the diff add a comment whose content is commented-out code?
8. Does any comment the diff adds consist only of words already present in the adjacent identifiers and the statement itself?
9. Does the diff add an interface, abstract class, factory, wrapper, middleware, adapter, or generic parameter having exactly one implementation and one call site?
10. Does the diff add a method whose entire body forwards its own parameters to another object, with no transformation, validation, or added logic?
11. Does the diff add a boolean or enum parameter whose only purpose is selecting which caller's behavior runs?
12. Does the diff add a configuration knob, feature flag, or environment variable with no second value it could take today?
13. Does the diff extract a shared helper on its first or second occurrence, or leave a third occurrence unextracted?
14. Does any identifier the diff adds consist solely of a type name, a single letter outside a loop index, or a filler word: data, info, manager, helper, util, handler, process, temp, obj, val, result?
15. Does the diff introduce a second name for a concept that already has one in this scope, or reuse an existing name for a different concept?

Return the findings schema. Report "no findings" when all 15 pass. Return at most 2,000 tokens.
</redundancy-review>

<defect-review>
Objective: find what is wrong in this diff. Read and report only. Apply all 14 checks and report every failure.

1. Does every package the diff adds to a manifest or lockfile resolve to a name that exists in its registry, at the pinned version?
2. Does every error branch the diff adds either handle the error, wrap and return it, log it with context, or carry a comment stating why ignoring it is safe? Count catch, except, rescue, an error return check, an unwrap, an expect, and an ignored return code.
3. Does every value crossing a trust boundary get checked at runtime, rather than only carrying a declared type or a cast?
4. Does every authorization check the diff adds deny by default and verify ownership of the specific object, rather than only that the caller is authenticated?
5. At every sink the diff touches, is output encoded, are queries parameterized, is logged input sanitized, and is no broken cryptographic algorithm used?
6. Is the diff free of credentials, API keys, tokens, and private keys?
7. Does the diff add a sleep, delay, or fixed timeout used to sequence two operations rather than to rate-limit or back off?
8. Does the diff add a public method reading a field that only another public method assigns, with no state check or type-level guard forcing the order?
9. Does the diff add a mutable global, singleton, or module-level variable written from more than one module?
10. Does the diff reference a name that is private, internal, underscore-prefixed, or unexported, from outside the module declaring it?
11. Does the diff add a field assigned in exactly one method and read only from that method, rather than initialized at construction?
12. Does any function the diff adds read the clock, a random source, an environment variable, the filesystem, the network, or mutable global state without receiving it as a parameter?
13. Does every non-obvious construct carry a comment stating its reason? Require one for a tuned constant, a swallowed handler, a sleep or retry, a workaround for an external bug, a deliberate departure from a nearby idiom, an ordering requirement, and a performance-motivated construction.
14. Does any header comment or docstring the diff adds name a private field, a local variable, or an internal algorithm that a caller does not need?

Return the findings schema. Report "no findings" when all 14 pass. Return at most 2,000 tokens.
</defect-review>

<test-review>
Objective: determine whether these tests could fail if the code were wrong. Read and report only. Apply all 10 checks and report every failure.

1. Does the new test fail against the parent commit with an assertion failure, rather than passing or failing with an import, module, type, or syntax error?
2. Does every test the diff adds contain at least one assertion on an observable output or side effect?
3. Do the assertions compare a value, rather than only checking non-nullness, truthiness, or type?
4. Is every expected value a literal or a constant derived independently, rather than something computed by calling the code under test?
5. Do the assertions verify something beyond the mocks the test itself configured?
6. Is each test body free of conditionals, loops, and try-catch that could route execution around its assertions?
7. Is the test free of wall-clock sleeps and timing dependence?
8. Does the test pass when run alone and under randomized order?
9. Where a snapshot or golden file backs an assertion, was it written from the specification rather than regenerated from the current output?
10. Does every conditional branch and error path the diff adds execute under at least one test?

For check 4, the operative question is whether the test would still pass if the implementation were wrong in a self-consistent way. If it would, it fails.

Return the findings schema. Report "no findings" when all 10 pass. Return at most 2,000 tokens.
</test-review>

<semantic-review>
Objective: answer four questions that require reading beyond the diff. Read and report only. Search the repository to answer them, budgeting 3 to 6 searches per check; when a budget runs out, report the check as unresolved with the terms you tried rather than reporting it as passing.

Every finding names the search terms used, because a search obligation is only checkable when the searcher says what it searched.

1. Does every function this diff adds do something no existing function already does? Search the repository by the function's purpose, not its name. Name the terms searched and the closest existing function found.
2. Is every behavioral claim in the step's intent covered by a test that would fail if that claim were violated? Name each claim and the test covering it, and report any claim with none.
3. Is every behavior change in this diff either required by the step's intent or called out in it? Report any change the intent does not account for.
4. Where this diff supersedes existing code, is the old path removed or consolidated rather than left live beside the new one?

Check 1 carries the most weight: the redundancy models produce most is semantically equivalent code written in different words, measured at 1.87 times the human rate in agent-authored changes, and no text-matching tool detects it. Reading for it is the only method available.

Return the findings schema. Report "no findings" when all 4 pass. Return at most 2,000 tokens.
</semantic-review>

<finding-verification>
Objective: separate findings whose evidence holds from findings whose evidence does not. You have the collected findings and the diff, and nothing else. Read and report only. Do not add findings of your own.

Apply all five checks to each finding.

1. Does the cited file exist in the diff, and does the cited line range fall inside it?
2. Does the quoted construct appear at that location, character for character?
3. Is the finding about code the diff changed, rather than code it only sits near?
4. Does the named check exist in its block, and does the evidence answer that check rather than a different one?
5. Do two or more findings name the same construct? Merge them, keeping the most specific fix.

Output format, two lists, both in the findings schema:

surviving:
  <every finding passing all five checks, merges applied>

dropped:
  <every finding failing one or more, each with one line naming which check it failed and why>

Report an empty surviving list when that is the answer. Return at most 2,000 tokens.
</finding-verification>

## 11. The decision log

Two artifacts with different lifetimes. The design document stays immutable. A `design.md` is append-only.

Create them: on the first step that touches a package, create `design.md` at that package's root; on the first cross-package decision, create `design.md` at the repository root. Routing rule: a decision touching more than one package goes to the root file, otherwise to the package's own.

Log a decision the implementation forced that the design document did not settle. Do not restate the design document. Record any departure from the design document here with its reason, and leave the design document itself unedited, because it is the record of what was decided up front and editing it destroys the comparison.

```
## Retry budget on the store client

Decision: 3 attempts, 100ms base, full jitter.
Alternatives: no retry, which drops writes on a single blip;
unbounded retry, which masks a dead backend as latency.
Why: the design document requires at-least-once delivery but sets no
budget; 3 attempts covers the observed single-node restart window.
Constrains: callers must be idempotent, so the write path stays keyed.
```

## 12. Comments

Comment the surprising only. Two tests, both operational:

- Remove the comment. Does the reader lose a rationale, a constraint, a unit, a range, a precondition, or an external reference? If nothing is lost, delete it.
- Check the trigger list for a missing reason: a tuned constant, a swallowed handler, a sleep or retry, a workaround for an external bug, a deliberate departure from a nearby idiom, an ordering requirement, a performance-motivated construction. Each one earns a comment stating why.

Reason: a comment that restates the code goes stale and then lies, while a comment carrying a reason stays true as long as the reason holds.

WRONG, a comment that restates the statement above it:

```
// increment by one
x = x + 1;
```

RIGHT, the same line with nothing to say, and a nearby line that does:

```
x = x + 1;

// The server rejects a batch of 501 or more, undocumented, found by
// bisecting. Keep this at 500 even though the client allows more.
const BATCH: usize = 500;
```

## 13. What this rulebook does not test

A criterion whose violation is unobservable is decoration an agent can always claim to satisfy. These are left out deliberately.

Untestable as stated, each with the reason: the single-responsibility principle, because "one reason to change" is not enumerable; open-closed, because it cannot be evaluated without knowing which changes arrive, and its usual proxy contradicts check 9 of `<redundancy-review>`; Liskov substitution, because the syntactic half is the compiler's job and the behavioral half is undecidable; dependency inversion, because "depend on abstractions" has no mechanical form; the CUPID properties, designed as directions to move rather than gates; don't-repeat-yourself in its full form, because the violation is a counterfactual about a future change; the Law of Demeter in its object form, undecidable by its own authors; and "functions should be two to four lines", which its author states he cannot justify.

Excluded as needing per-language calibration: cyclomatic and cognitive complexity, function length, file length, class cohesion, and class size. Published limits for function length alone run 150, 60, 50, 24, and 4 lines, and a limit applied inconsistently becomes a rhetorical device rather than a gate. A project wanting them sets one number per language, records where the number came from, and applies it identically to every diff.

Excluded as undecidable by tooling, with a reading agent covering it instead: detection of semantically equivalent code, which `<semantic-review>` check 1 handles, and mutation score as a gate, since the largest deployment of mutation testing abandoned the absolute score as neither concrete nor actionable and surfaced surviving mutants at review time instead.

## Emission Discipline

Every plan, `design.md`, and source file this rulebook emits passes these constraints before it is written. The generated file never refers to any source document for these rules; they appear only by substance.

- Subagent-only exploration. The main context holds the plan, the state, and the outcomes; every search, read, and edit is dispatched.
- Bounded state. `plan/state.md` is the sole run-state write.
- Every check a question with a pass or fail answer, every quantity a number or a range, every loop capped with a progress test.
- Every hard rule carries one defined action for when its precondition fails.
- Every subagent task carries all six contract elements, and its return is capped.

## 14. Checklist

Run these on the finished work. Each answers yes or no; each no returns to its section.

- The design document existed and passed admission before any code was written. (3)
- Every L1 step names the dependency that forces its position. (4)
- Every L2 step names one test that went red before it and green after. (5)
- The plan-audit gate returned no findings before execution began. (6)
- No plan file was edited during execution. (7)
- Every step either researched or recorded why it skipped. (8)
- Every behavior-changing commit carries a test that failed on the parent with an assertion failure. (9)
- Every commit ran the four review blocks, the verifier, and the fixes before being amended. (10)
- Every review loop and audit loop ended on no progress or at its cap of three. (6, 10)
- Every decision the design document did not settle is logged in a `design.md`. (11)
- Every comment states a reason the code cannot state itself. (12)
- Every quantity in the emitted plans is a number or a range. (2)
- Every hard rule in the emitted plans has one defined action for when its precondition fails. (2)
- Every subagent dispatch carried all six contract elements and a return cap. (2)
- Every command run in the main context bounds its own output. (2)
- `plan/state.md` is current, and every compaction wrote it first. (2)
- Every emitted file states its rules as substance and names no source document for them. (Emission Discipline)
- No claim in this run rests on a threshold that has no source and no label as a bet. (7, 10)

Restated: the main context holds the plan, dispatches work, and records outcomes, reading no source and writing no code. Every commit is reviewed in a fresh context, verified, fixed, and amended before the next step begins.

## References

- Intrinsic self-correction degrading accuracy without an external signal: Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet", ICLR 2024.
- Verification in a context that cannot see the draft outperforming verification that can: Dhuliawala et al., "Chain-of-Verification Reduces Hallucination in Large Language Models", 2023.
- Judges favoring their own output: Zheng et al., NeurIPS 2023; Panickssery et al., NeurIPS 2024.
- Accuracy declining with context length independent of retrieval: Chroma Research, "Context Rot", 2025.
- Weak oracle signals in agent-authored tests: Banik et al., "All Smoke, No Alarm: Oracle Signals in Agent-Authored Test Code", 2026.
- Any-failure against genuine red-to-green: Mündler et al., "SWT-Bench", 2024. Failure-class validity rates: "Execution-Feedback Driven Test Generation", 2025. Change coverage of fail-to-pass tests: "TDD-Bench Verified", 2024.
- Non-deterministic harness results: ScalingIntelligence, SWE-bench Lite evaluation notes.
- Plan re-injection, and a subpar plan harming more than no plan: "Evaluating Plan Compliance in Autonomous Programming Agents", 2026.
- Replanning ablations: Lee et al., "Plan-and-Act", ICML 2025; "TAPE", 2026. Static-plan sufficiency: "Web Agents Should Adopt the Plan-Then-Execute Paradigm", 2026.
- Repair-loop convergence by iteration: "Is Three the Magic Number?", 2026; Zhong et al., "LDB", 2024; Madaan et al., "Self-Refine", 2023.
- Criterion type outweighing batching: "RuVerBench", 2026; "CheckEval", EMNLP 2025.
- Specialized reviewer splits and the verification pass: "CodeGenie", 2026; "Agentic Code Review", 2026. Reviewer complementarity: "A Single LLM Is an Incomplete Code Reviewer", 2026. Coordination failures: "Why Do Multi-Agent LLM Systems Fail?", NeurIPS 2025.
- Semantic redundancy in agent-authored changes: "More Code, Less Reuse", 2026. Duplication and error-masking trends: GitClear, "The Maintainability Gap", 2026.
- Package hallucination rates: Spracklen et al., USENIX Security 2025; "The Range Shrinks, the Threat Remains", 2026.
- Secure-generation rates by weakness class: Veracode, GenAI Code Security Report, 2025.
- Mutation score rejected as a gate: Petrović and Ivanković, "Practical Mutation Testing at Scale: A View from Google", TSE 2021.
- Commit hygiene before publishing: `gitworkflows(7)`. Change decomposition in review: Di Biase et al., PeerJ CS 2019.

*2026-07-25 - Claude Opus 5 (Cursor agent)*
