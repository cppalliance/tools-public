# Vibe Coding Lessons

Every machine application of vibe coding creates technical debt - not sometimes, always. The metaphor is Ward Cunningham's: debt is the gap between the code and the team's current understanding of the problem. Cunningham required clean code from the start so refactoring would remain feasible [\[1\]](#ref-1). Vibe coding skips that precondition. Good prompting reduces the deposit; bad prompting amplifies it; there is no zero. The interest accrues from the first commit, and only deliberate work pays it down.

The data is blunt. Copy-paste rose from 8.3% to 12.3% of changed lines between 2020 and 2024, the first year copy-paste exceeded refactored code. Duplicated blocks grew eightfold. Every 25% rise in AI adoption associates with a 7.2% drop in delivery stability [\[3\]](#ref-3) [\[4\]](#ref-4). The golden rule for anything beyond a throwaway: do not commit code to your repository if you could not explain exactly what it does to someone else [\[2\]](#ref-2).

Three trajectories follow. Unskilled operators produce deteriorating code regardless of how clever the agent is. Skilled operators who do not periodically refactor produce deteriorating code anyway, because debt compounds faster than features [\[5\]](#ref-5). Skilled operators who weave refactoring into the cadence produce tight, durable work. The agent will not see what an unskilled operator does not point at. Vibe coding is a force multiplier on craft, not a substitute for it. Tests and documentation are integral, not optional. A change without a test is a guess that survived. Above tests and rules sits the architecture document: an explanation of the overall architecture, written so that both a human and a machine can read it. Without it, the rules stack drifts and locally clean changes fail globally.

The practice rests on two structural disciplines and one scheduling commitment.

**Rules carry the discipline.** Every short prompt in this document works because the discipline lives outside the prompt [\[6\]](#ref-6). A workspace rule says compile and fix all errors. A project file says tests use only public APIs. When you issue a two-word instruction and watch it produce a coherent multi-file result, the rules stack is doing the work. Anything you say out loud on a second session is a rule that wants to be promoted [\[7\]](#ref-7).

**Verification beats trust.** A randomized controlled trial of sixteen experienced maintainers found AI tools made them 19% slower while they self-reported being 20% faster - a 39-point gap [\[8\]](#ref-8). A 2025 survey: 96% of developers say they don't trust AI code, but only 48% always verify it [\[9\]](#ref-9). Stacking another model as reviewer doesn't save you: 62% of LLM-judge agreement is driven by shared rubric structure, not substantive assessment [\[10\]](#ref-10). The felt experience of speed is an unreliable sensor. Measure what ships.

**Debt must be scheduled away.** On a separate cadence from feature work, stop adding behavior and run a pure refactor pass [\[11\]](#ref-11) [\[12\]](#ref-12). Not woven into feature work. Not promised for later. A scheduled pass where the only output is structure that more accurately reflects the team's model of the problem.

## The Plan-Mode Loop

Plan mode is the default for any change that touches code. The only exceptions are trivial mechanical edits. The loop has four phases in fixed order.

1. **Collect** - gather the relevant files, rules stack, architecture document, and related code that defines invariants the change must respect.
2. **Update** - draft the plan, react to it, push back, refine until it survives scrutiny. Multiple rounds are expected. The session that produced three plans before execution ships cleaner work than the session that ran the first draft.
3. **Verify** - audit the plan for clarity, ambiguity, data-flow gaps, edge cases, combinable steps, parallelizable work. Only a plan that survives this sweep advances.
4. **Execute** - hand off to a fresh session. Do not edit the plan during execution. Work the to-dos in order, verify each step, end with the full test suite.

Skipping any phase has a named cost. Skipping collection produces a plan that hallucinates the codebase. Skipping update ships the first idea. Skipping verification runs with a known weakness. Skipping execution discipline produces work the operator cannot vouch for.

The plan is a standalone artifact on disk with a name, a path, and a structure execution follows to the letter. Treat it as a design document: overview, numbered steps, to-dos, artifacts, invariants, out-of-scope items. Anything that stays only in chat is something you will say again.

**Driving iteration.** Scope the plan to a folder so steps do not sprawl. Attach a methodology file and have the plan inherit its posture. Split into review-then-fix so diagnosis and repair stay separate. Spawn a research helper for prior art and have the plan absorb the compressed summary. Install a confirmation gate before structural edits. Demand a data-flow audit so each step is checked for whether it receives what the prior step emits. Autonomy is per task class - drive primary work yourself with tight feedback loops, delegate secondary tasks (guides, spikes, lint, docs) [\[15\]](#ref-15).

**When execution drifts.** Do not patch forward. Revert, reopen the plan, name what was wrong about the plan that produced the output, revise, re-audit, re-run from clean state [\[16\]](#ref-16). Patching stacks compromise context on top of the original mistake.

**Session rotation.** Long sessions degrade measurably. Accuracy drops 20-50% between 10K and 100K tokens [\[18\]](#ref-18). The lost-in-the-middle effect makes the planner use material near the start and end far better than the middle [\[17\]](#ref-17). Rotate when: the agent repeats the same mistake, effectiveness visibly decreases, or you finish a logical unit. State lives in files and git, not in the chat window. Re-inject the live to-do list periodically as a persistent north star [\[19\]](#ref-19).

**Reading the prompts.** Every blockquote below is a paste-ready prompt. The prose teaches the why; the blockquote is the what.

## 1. Search Before Creating

*If you are about to write a function, you are about to fail to find one.*

Before writing a new function, regex, normalizer, constant, or module, search the codebase for an existing equivalent. If one exists, use or extend it [\[20\]](#ref-20). The model is not naturally biased toward reuse - its training distribution overrepresents greenfield generation [\[21\]](#ref-21). The search-first prompt puts retrieval before generation, shifting behavior toward existing modules. Make this the first rule in your workspace tier; most duplicates that would grow into next year's debt never get planted.

> Before adding any new function, pattern, regex, or constant, grep this codebase for existing equivalents and report what you find. Do not write the new code until you have shown me the search.

> Audit the files changed in this session for duplication this work introduced. Propose a consolidation step.

## 2. Project-Specific Discipline

*Each studio has its own clay; the same gesture works here, fails next door.*

Discipline that only makes sense in one codebase but is non-negotiable inside it. "Styles live in a stylesheet." "All parser logic in one module." "Tests use only public APIs." "No naked throw at call sites." Each lives in the project tier of the rules stack.

Write them short, declarative, copy-pasteable. "ALWAYS X" or "NEVER Y" beats "Try to consider X." The model treats imperative grammar as a constraint and advisory prose as a suggestion. An analysis of 2,500+ public AGENTS.md files confirms: a three-tier boundary syntax (Always do / Ask first / Never do) outperforms prose, and one code snippet outperforms three paragraphs of style description [\[22\]](#ref-22). Rules buried mid-file show 30-50% lower compliance, with up to 61.8% performance variance from repositioning alone [\[23\]](#ref-23). Prune ruthlessly - a stale rule is worse than no rule.

> Read this project. Identify three to five conventions that are not obvious from the file names or imports. Propose them as project rules.

> Before you write code in this project, recite the project rules from AGENTS.md that apply to this change.

## 3. Promote Conventions Out of Chat

*A convention said twice has already asked you for soil.*

When you find yourself restating the same convention across two sessions, you have found a rule. A rule in chat decays when the session ends; a rule in AGENTS.md persists across every future session, every future agent, every future contributor [\[24\]](#ref-24). If you have said it twice, it is a rule. Distinguish rule candidates (norms, layout decisions, anti-patterns) from one-shot context (this specific bug in this specific file) [\[17\]](#ref-17).

> Scan our chat for any convention I restated more than once. For each, propose an addition to AGENTS.md and tell me where in the file it should land.

> Now apply the proposed additions to AGENTS.md. Show me the diff before saving.

## 4. The Rules Stack

*Every rule load-bearing; the rest is ornament.*

Three tiers. The **workspace** tier applies to every project: compile and fix errors, search before creating, honest functions, build-presets only. Install once, forget. The **project** tier sits in AGENTS.md at the project root: file map, public surface, tooling, trusted tests. The **project-specific** tier is the narrowest: architectural decisions an outsider would never guess from the imports.

### Authoring disciplines

Use `AGENTS.md` as the canonical filename - a study of 124 PRs measured 28.6% reduction in agent runtime and 16.6% reduction in tokens versus CLAUDE.md [\[7\]](#ref-7). Apply the **prune test**: would removing this rule cause the agent to make a mistake? If no, cut it [\[25\]](#ref-25). Use **emphasis keywords** (IMPORTANT, NEVER, ALWAYS) only on non-negotiables; spent everywhere, the signal flattens to baseline [\[25\]](#ref-25). **Order by criticality**: identity first, non-negotiable rules, format, domain context, examples; critical rules can repeat at the end (instruction sandwich) [\[23\]](#ref-23). Frame the file as a **tool-use runbook**, not a style guide: codify command preferences, sequencing, and parallelism [\[26\]](#ref-26). Watch for four anti-patterns: *The Novel* (500+ lines of generic advice), *The Paranoid Parent* (confirmation before every action), *The Copy-Paste Special* (someone else's file unmodified), *The Ghost Town* (too short to convey anything) [\[27\]](#ref-27). Hard budget for the project tier: under ~100 lines.

> Audit this project. List the conventions a fresh contributor would not guess from the file names. Propose them as AGENTS.md additions, and flag any that should be promoted to the workspace rules instead. Apply the prune test to anything already in the file.

> At session start, read the workspace rules and the project AGENTS.md. Confirm in one paragraph what is in scope, what is not, and what conventions apply.

> Reorder the AGENTS.md by criticality: identity at the top, then non-negotiable ALWAYS/NEVER rules, then format, then domain context, then examples. Move any buried critical rule to the top or repeat it at the end. Apply the prune test as you go.

## 5. Architecture Documentation as Foundation

*Nothing rises without a foundation that can carry it.*

A document at the project root that explains the system's coherence: what the codebase is, its public surface, internal seams, scope, pipelines, invariants. The rules stack tells the agent what never to do; the architecture document tells the agent what the project is. Write for two audiences - humans and machines. Declarative sentences, structural headings (`## Public Surface`, `## Pipelines`, `## Invariants`, `## Out of Scope`). The agent treats `##` headings as scaffolding for retrieval, so the section becomes a target the planner can hit directly rather than something to reconstruct from twenty source files [\[6\]](#ref-6) [\[28\]](#ref-28). Treat the document like code: update it in the same commit that invalidates it. A stale architecture document silently poisons every future plan.

> Generate an architecture document for this project. Include: one-paragraph purpose, the public surface, the major internal modules and how they relate, the pipelines or lifecycles, the invariants, what is OUT of scope. Write it so a fresh agent can read it cold and pick up work coherently.

> Diff the architecture document against the current code. List sections that have drifted. Propose updates.

## 6. Anchor with @-Mention Scope

*The boundary is already drawn by the folder; the anchor is the shortest way to point at it.*

The `@` token fences exploration before the model starts wandering. Frontier coding agents consistently over-fetch context, introducing substantial noise, and sophisticated scaffolding yields only marginal gains against the bias [\[29\]](#ref-29). Three anchor types: folder (`@{folder}/` for subsystem scope), file (ground truth), methodology (named recipe). Without an anchor, the agent constructs its own retrieval target and usually constructs it badly. A read-only planning subagent trained for file selection scored F1 0.790 versus 0.697 baseline while cutting planning back-and-forths from 8-10 to ~4 [\[30\]](#ref-30).

> @{folder}/

> @{methodology}.md @{folder}/

## 7. Lean on a Methodology File

*The same chair, made the same way, ten thousand times, each one good.*

A reusable recipe in a file, not a prompt. A methodology document says: for the given codebase, produce an artifact with findings under categories X, Y, Z. Attach by @-mention plus target folder. The next codebase gets the same recipe with no rewriting. A methodology file outperforms a clever prompt because a prompt asks the model to invent a process; a methodology gives it one to execute - inventing is harder, more variance-prone, and more expensive [\[32\]](#ref-32). After running on a new codebase, ask the agent to propose updates; a mature methodology has been run on three projects and edited after each.

Where prescriptions must be verifiable, use the EARS grammar (five sentence patterns: ubiquitous, event-driven, state-driven, conditional, optional-feature), now mandatory in spec-driven workflows like AWS Kiro [\[31\]](#ref-31).

> @{methodology}.md @{folder}/

> Run the methodology again on this codebase. After producing the artifact, propose updates to the methodology file based on cases where the recipe felt under-specified or wrong for this codebase.

## 8. The Two-Stage Loop

*A cell that finds the flaw, a cell that fixes it, and never the same hands on both jobs.*

Split plan-mode work into two passes. The first produces a review artifact listing findings, severity, file paths, line ranges, and acceptance criteria. The second is a fresh session that opens that file as a work order. The two passes want opposite temperaments: review is judgmental and prose-heavy; fix is mechanical and test-heavy. Mixing them produces sloppy fixes and shallow reviews, because the context that drafted a finding quietly retunes severity to match what it can comfortably fix [\[34\]](#ref-34). A session boundary is the cheapest reset; the serialized review transmits only the verdict, not the rhetorical compromises behind it. Lee et al. (ICML 2025) validate this architecture directly: dedicated planner + separate executor achieves state-of-the-art results (57.58% WebArena-Lite, 81.36% WebVoyager) [\[33\]](#ref-33).

> Run @{methodology}.md against @{folder}/. Output the review artifact to @{folder}/review.md. Do not modify any other file.

> Open a fresh plan-mode session. Read @{folder}/review.md. Plan the fix pass: every finding becomes a step, with the test that fails before the fix and passes after.

## 9. The Backlog as Contract

*A contract names what counts as proof, and nothing is finished until every claim it makes has been discharged.*

The review artifact is a ledger of obligations. Every entry carries three fields: **severity** (low/medium/high), **path** (file and line range - not prose gestures like "the error handler"), and **done-condition** (the test that goes red-to-green). Drop any field and the fix pass runs on vibes.

For done-conditions, adopt the EARS grammar [\[31\]](#ref-31): "WHEN `parse()` is called with malformed input THEN the system shall raise `ParseError` and the test in `test_parser.py::test_malformed` shall pass" is an obligation. "Improve error handling" is not. A structured finding with named fields concentrates the model's next-token distribution on schema-fitting tokens at the moments where scope drift normally begins; a paragraph of advice gives it none [\[35\]](#ref-35). The failure mode is a review treated as inspiration - the fix-pass agent extrapolates, invents a refactor, and lands a commit you did not approve.

> Fix every finding in @{project}/review.md. Each finding must be addressed by a code change and a test that fails before the fix and passes after. Stop after the last finding.

> Audit the review file for vague findings. Rewrite each with a concrete done-condition before we begin the fix pass.

## 10. Internet Research for Prior Art

*Look first; the move you were about to invent has probably been measured.*

Spawn a subagent to search the web, compress findings, and return only the curated summary to your main context [\[6\]](#ref-6). Raw pages never cross the boundary - the cost of letting them in is that your context fills with noise and your attention budget for the plan collapses. Use when the task is genuinely complex or domain-specific; skip on simple tasks where prior art adds noise. After the subagent returns, enrich the plan explicitly: new steps, new safeguards, new vocabulary.

> Spawn a subagent. Search the web for techniques related to the subject in this plan: existing practice, existing solutions, commentary on related techniques that could help, and warnings about pitfalls, known bugs, and gotchas. For anything that could be relevant, pass a compressed summary back to the main context. When the searches are finished, use the compressed summaries to enrich the plan.

> Spawn a subagent. Search the web for prior art on {specific technique} only. Compress the findings to one paragraph and pass it back. Enrich the relevant plan step if the findings apply.

## 11. Quality Gate: Think Deeply, Make No Mistakes

*Less but better; the gate is the moment the surplus falls away.*

The pushback prompt between plan and execution. Six checks: data-flow (each step receives what prior steps emit), combinability, parallelizability, clarity, edge cases, unstated assumptions. Language models are sycophantic by default [\[38\]](#ref-38); "be honest" measurably increases the rate at which they admit weaknesses. The closing line shifts the model's target from "please the user" to "produce the response the user is asking for, including the unflattering parts."

Do not stack an LLM-author with an LLM-reviewer - vendor leaderboard tools scored 82% on their own benchmark and 45% on independent re-runs [\[39\]](#ref-39). The single biggest upgrade: run the audit in a fresh context. Chain-of-Verification measured hallucinations dropping from ~18% to ~6%, but only when the verifier had no access to the original answer [\[35\]](#ref-35). Same-context self-critique under-performs because the model is biased to defend its own draft. If you need a CI signal, structural-fingerprint classifiers identify AI-authored hunks at 95%+ accuracy from dataflow and whitespace patterns alone [\[40\]](#ref-40).

> Review the plan, think deeply, make no mistakes, be honest. Check clarity, ambiguity, data-flow (does each step receive what prior steps emit), combinable steps, parallelizable work, and edge cases the plan doesn't cover. Report findings before we proceed.

> Same audit, but data-flow only: trace what each step emits and what each subsequent step requires; report any mismatch.

> Spawn a subagent. Give it the plan file with no other context. Ask it the following discrete verification questions, each in its own turn: does each step receive what prior steps emit; is any step doing two jobs; what edge case is missing; what assumption is unstated. Return the answers as a list. Do NOT show the subagent this conversation.

## 12. The Implement-the-Plan Handoff

*The runner does not improvise; the baton has its drill.*

Phase four of the loop. Fires only after the quality gate passes. Each clause exists for a reason: "implement as specified" sets the target; "do not edit the plan" closes a degree of freedom and is a security primitive - an isolated planner + hierarchical verifier drops indirect prompt-injection attack success from 72.8% to 0% [\[41\]](#ref-41); "use existing to-dos" anchors to an audited artifact; "verify each step" prevents rush-to-done; "end with the test suite" closes the gate [\[26\]](#ref-26). Keep the handoff short, identical every session - the same opening tokens hit the same cached prefix, delivering more consistent behavior and lower cost. Do not embellish. The handoff is a ritual, not a creative act.

> Implement the plan as specified. Do not edit the plan file. Use the existing to-dos. Verify each step before advancing. End with the full test suite.

> Resume execution. Do not edit the plan. Confirm which to-do is next, then proceed.

## 13. Verification Gate

*Verification is not a step; it is the wall the change must pass through.*

Three legs, three classes of bug, none redundant. The **test suite** catches regressions against behavior you wrote down [\[42\]](#ref-42). The **rendered artifact** (PDF, HTML, CLI, served page) catches integration bugs units never see. The **corpus replay** catches cases nobody wrote a test for. Most of the gate's value is anticipatory: a plan written under knowledge of a three-leg gate names test cases earlier, scopes changes more narrowly, and avoids speculative refactors [\[35\]](#ref-35).

Be aware: LLM-generated test oracles drop 8-9 accuracy points when the code under test is buggy, quoting the buggy implementation as ground truth [\[43\]](#ref-43). Coverage's correlation with mutation-detected effectiveness collapses once suite size is held constant [\[44\]](#ref-44). Mutation testing is the cheapest mechanical lever for AI-authored suites [\[45\]](#ref-45).

> Run the full test suite. Then run the real artifact pipeline on a real input. Then run the corpus replay against the saved baseline. Report any deviation.

> Corpus-scale verification: run the new code against every input in the saved corpus. List every input where the output differs from the baseline, and for each, classify the deviation as expected (scope of this change) or unexpected (regression). Stop on any unexpected deviation.

## 14. Audit the Test Suite

*Trust no green light without examining the apparatus.*

Tests passing is not tests being adequate. Named failure modes: happy-path-only suites, tautological tests (assert what the code does, so they can't detect the code is wrong [\[43\]](#ref-43)), structural-assertion tests (break on refactor), zero-test public functions, missing edge cases. The canonical taxonomy names 12 recurring test smells; the modern catalog has grown to ~200 [\[46\]](#ref-46).

Two mechanical levers. **Mutation testing** (Stryker, PIT, Mutmut) - surviving mutants are receipts of tautological assertions [\[45\]](#ref-45). **Property-based testing** (Hypothesis, QuickCheck) shifts the oracle from "expected outputs" to "invariants the implementation must satisfy," routinely surfacing concurrency and protocol bugs example-based suites miss [\[47\]](#ref-47). The cure for an LLM-authored happy-path suite is a different oracle shape.

The harvest hook: every gap found here feeds back into lesson 16 as a candidate rule. Patterns that recur become rules; rules that bind become CI checks.

> Read every test file under @{project}/tests/. For each public function and each public CLI entry point in @{project}/, list which tests exercise it and which do not. Flag every function with zero tests, only happy-path tests, tests that assert on internal structure rather than observable behavior, and tests that mirror the implementation's logic rather than its contract. For every change in the most recent commit, list the edge cases (empty input, malformed input, boundary conditions, error paths) that have no test. Propose specific new tests for each gap with one-line descriptions.

> For every line changed in the most recent commit, identify which test exercises that line under realistic input. List lines with no covering test. Propose one new test per gap.

> Read the tests added in this session. For each, write one sentence explaining what real failure mode the test would catch. If the explanation is "the implementation works the way the implementation works," flag the test as tautological and propose a contract-based replacement.

## 15. Read the Diff Yourself

*See what is on the canvas, not what you remember putting there.*

An eye-tracking study found developers regularly failed to identify machine-authored code without a provenance label; once told, search effort and cognitive workload measurably rose [\[48\]](#ref-48). Mark every AI-authored hunk. Defect discovery collapses above 500 LOC/hour; the empirical sweet spot is 200-400 LOC over 60-90 minutes [\[49\]](#ref-49). Cap AI-authored diffs at ~300 LOC. If larger, split before reviewing.

**AI-flavored failure modes to scan for:** hallucinated APIs, phantom validation, optimistic auth, tautological tests, cargo-culted patterns, happy-path-only error handling, comprehension debt, silent behavior changes, swallowed exceptions [\[50\]](#ref-50). The diagnostic: "if we regenerated this tomorrow, would the output differ materially?" If yes, the fragility is the bug.

Only ~15% of review comments address real defects [\[51\]](#ref-51) [\[52\]](#ref-52). Run linters, formatters, and static analysis first in CI; human attention is for logic, edge cases, and architectural fit.

> Show the unified diff grouped by file, sorted by lines changed descending. Cap the report at three hundred LOC; if the change is larger, split it into review chunks. For each file, list one risk and one thing a careful reviewer would check.

> List every file changed and one thing in each that I should manually verify before considering this done. Flag any of the named AI-failure-mode classes (hallucinated APIs, tautological tests, phantom validation, optimistic auth, swallowed exceptions, silent behavior change, comprehension debt) you can spot in the diff.

> Confirm the mechanical layer is green (lint, format, type-check, static analysis) before I read the diff. If anything is red, fix it first; do not ask me to read past style noise.

## 16. Harvest Bugs into New Rules

*Every bug you found this season is next year's compost rule.*

Every surprise from lessons 14 and 15, and every plan deviation caught in execution, is a candidate rule. If you find a class of bug twice, it becomes a rule [\[53\]](#ref-53) [\[54\]](#ref-54). A rule candidate prevents a class of mistake, not a single instance. Prune symmetrically: delete rules that no longer match reality the same day.

**Promote to executable form** when the rule has a syntactic shape. Custom Semgrep or CodeQL patterns can encode "tests must use only public APIs" or "no naked Exception raises" as CI checks [\[52\]](#ref-52). Three outcomes per finding: markdown rule (judgment-based), Semgrep rule (syntactic pattern), or static-analysis tightening. CI does not forget; markdown depends on attention [\[55\]](#ref-55).

> List every bug class and every plan-deviation found during this session. For each, propose either an AGENTS.md or workspace markdown rule, OR a Semgrep / static-analysis configuration that would have prevented it. Skip the ones already covered by an existing rule.

> Review the proposed rules for redundancy with the existing stack and for over-specificity (rules that match too narrow a case). Apply only the survivors. For any rule with a clean syntactic pattern, write the Semgrep rule as well. Then check whether the architecture document needs an update.

## 17. Refactor Cadence

*The building updates itself in the same hand that drew the plans.*

The last lesson because it requires the full vocabulary of every prior one. On a separate cadence from feature work, stop adding behavior and run a pure refactor pass. A recurring slot - weekly, biweekly, or every fifth ship - defended like a feature deadline.

The scope: consolidate duplicates (lesson 1), delete flagged dead code (lesson 16), tighten drifted public surfaces, regenerate the architecture document (lesson 5), prune stale rules (lesson 4). End with the verification gate (lesson 13) and test-suite audit (lesson 14).

Named taxonomies for the mechanics: Beck's *Tidy First?* separates structural from behavioral changes and sequences them deliberately [\[12\]](#ref-12). Shopify's 25% rule buckets debt by repayment cadence (daily/weekly/monthly/yearly) [\[56\]](#ref-56). The Mikado method attempts the end-state change, logs failures as prerequisite nodes, reverts, then works leaf nodes bottom-up in ~10-minute timeboxes [\[57\]](#ref-57). Prioritize by churn, not smell density - interest on technical debt is dominated by how often a module is touched [\[58\]](#ref-58).

Debt is contagious: a controlled experiment found high-debt environments cause developers to re-implement instead of reuse and introduce additional smells [\[5\]](#ref-5). Microsoft field study: modules refactored by a dedicated team saw significant reductions in dependencies and post-release defects [\[59\]](#ref-59). BlueOptima: maintainability anti-patterns predict elevated change-failure-rate at F1 = 0.79 [\[60\]](#ref-60).

> Refactor pass. No new features. Run the full lesson 1 audit (search before creating: list duplicates introduced since the last refactor pass), the full lesson 16 audit (rules and architecture-document drift), and propose a plan that only consolidates, deletes, tightens, or documents. End with the verification gate AND the test-suite audit from lesson 14.

> Install a recurring refactor-pass entry in this project's AGENTS.md: cadence, scope rules (no new behavior), exit conditions (verification gate green and test-suite audit clean), and the prompt template above.

The physics of the medium does not change. The loop is the practice that lets you live with the physics. Run them honestly, run the refactor week without flinching, and the codebase will still be a place a stranger could maintain a year from now.

## References

<a id="ref-1"></a>[1] Cunningham, W. "[The WyCash Portfolio Management System / The Debt Metaphor.](https://www.youtube.com/watch?v=pqeJFYwnkjE)" 1992; Fowler, M. "[TechnicalDebt.](https://martinfowler.com/bliki/TechnicalDebt.html)"

<a id="ref-2"></a>[2] Willison, S. "[What 'Vibe Coding' Actually Means.](https://simonwillison.net/2025/Mar/19/vibe-coding/)" 2025

<a id="ref-3"></a>[3] GitClear. "[AI Code Quality Report 2025.](https://gitclear.com/ai_assistant_code_quality_2025_research)" 2025

<a id="ref-4"></a>[4] Forsgren, N., Humble, J., Kim, G. "[Accelerate: The Science of Lean Software and DevOps - DORA Metrics.](https://itrevolution.com/product/accelerate/)" 2018; DORA 2024 State of DevOps Report

<a id="ref-5"></a>[5] "[Broken Windows Theory in Software Engineering: A Controlled Experiment.](https://link.springer.com/article/10.1007/s10664-024-10456-6)" Empirical Software Engineering, 2024

<a id="ref-6"></a>[6] Anthropic Engineering. "[Effective Context Engineering for AI Agents.](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)"

<a id="ref-7"></a>[7] Agentic AI Foundation. "[AGENTS.md Specification.](https://agents.md/)" 2025

<a id="ref-8"></a>[8] METR. "[Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity.](https://arxiv.org/abs/2507.09089)" 2025

<a id="ref-9"></a>[9] Sonar. "[Critical Verification Gap in AI Coding (96% don't trust, 48% verify).](https://www.sonarsource.com/company/press-releases/sonar-data-reveals-critical-verification-gap-in-ai-coding)" 2025

<a id="ref-10"></a>[10] "[The Evaluation Illusion: LLM Judges Anchor on Surface Form.](https://arxiv.org/abs/2603.11027)" 2026; "[Are LLMs Reliable Code Reviewers?](https://arxiv.org/abs/2603.00539)" 2026

<a id="ref-11"></a>[11] "[TD Interest Probability: Hotspot Prioritization in Technical Debt Repayment.](https://link.springer.com/article/10.1007/s42979-020-00406-6)" SN Computer Science, 2020

<a id="ref-12"></a>[12] Beck, K. "[Tidy First? A Personal Exercise in Empirical Software Design.](https://www.oreilly.com/library/view/tidy-first/9781098151232/part01.html)" O'Reilly, 2024

<a id="ref-13"></a>[13] Willison, S. "[Using LLMs for Code: Managing Context as the Craft.](https://simonwillison.net/2025/Mar/11/using-llms-for-code/)" 2025

<a id="ref-14"></a>[14] Willison, S. "[Using LLMs for Code: Managing Context as the Craft.](https://simonwillison.net/2025/Mar/11/using-llms-for-code/)" 2025

<a id="ref-15"></a>[15] Litt, G. "[Code Like a Surgeon: Per-Task Autonomy, Not Per-Developer.](https://www.geoffreylitt.com/2025/10/24/code-like-a-surgeon)" 2025

<a id="ref-16"></a>[16] Cursor. "[Agent Best Practices.](https://cursor.com/blog/agent-best-practices)" 2025

<a id="ref-17"></a>[17] Liu, N. F. et al. "[Lost in the Middle: How Language Models Use Long Contexts.](https://arxiv.org/abs/2307.03172)" 2023

<a id="ref-18"></a>[18] Chroma Research. "[Context Rot.](https://research.trychroma.com/context-rot)"

<a id="ref-19"></a>[19] Cline. "[Cline v3.25: Focus Chain and Auto Compact for Long-Horizon Agents.](https://cline.bot/blog/cline-v3-25)" 2025

<a id="ref-20"></a>[20] Hunt, A., Thomas, D. "[The Pragmatic Programmer (DRY).](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)" 1999, 20th Anniversary Edition 2019

<a id="ref-21"></a>[21] Mao et al. "[Large-Scale Empirical Study of AI-Generated Code in Real-World Repositories.](https://arxiv.org/abs/2603.27130)" 2026

<a id="ref-22"></a>[22] GitHub Blog. "[How to Write a Great AGENTS.md: Lessons from Over 2,500 Repositories.](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2,500-repositories/)"

<a id="ref-23"></a>[23] "[The Instruction Position Problem.](https://tianpan.co/blog/2026-04-14-the-instruction-position-problem)" 2026

<a id="ref-24"></a>[24] Cursor Documentation. "[Rules and AGENTS.md.](https://docs.cursor.com/context/rules)"

<a id="ref-25"></a>[25] Anthropic. "[Claude Code Best Practices.](https://docs.anthropic.com/en/docs/claude-code/best-practices)"

<a id="ref-26"></a>[26] OpenAI. "[Codex Prompting Guide (GPT-5 cookbook).](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide/)" 2025

<a id="ref-27"></a>[27] Claude World. "[CLAUDE.md Anti-Patterns.](https://claude-world.com/articles/claude-md-antipatterns)"

<a id="ref-28"></a>[28] Anthropic Engineering. "[Writing Tools for Agents.](https://www.anthropic.com/engineering/writing-tools-for-agents)"

<a id="ref-29"></a>[29] "[ContextBench: Evaluating Context Selection in Coding Agents.](https://arxiv.org/abs/2602.05892)" 2026; project page: https://contextbench.github.io/

<a id="ref-30"></a>[30] Cognition. "[Devin Annual Performance Review 2025 (read-only planning subagent, F1 0.790).](https://cognition.ai/blog/devin-annual-performance-review-2025)" 2025

<a id="ref-31"></a>[31] Mavin, A., Wilkinson, P., Harwood, A., Novak, M. "[Easy Approach to Requirements Syntax (EARS).](https://ieeexplore.ieee.org/abstract/document/5328509)" IEEE RE 2009

<a id="ref-32"></a>[32] Wang, L. et al. "[Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models.](https://aclanthology.org/2023.acl-long.147/)" ACL 2023

<a id="ref-33"></a>[33] Lee et al. "[Plan-and-Act: Improving Planning of Agents for Long-Horizon Tasks.](https://arxiv.org/abs/2503.09572)" ICML 2025

<a id="ref-34"></a>[34] Bacchelli, A., Bird, C. "[Expectations, Outcomes, and Challenges of Modern Code Review.](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/)" ICSE 2013

<a id="ref-35"></a>[35] Dhuliawala, S. et al. "[Chain-of-Verification Reduces Hallucination in Large Language Models.](https://arxiv.org/abs/2309.11495)" 2023

<a id="ref-36"></a>[36] Nakano, R. et al. "[WebGPT: Browser-assisted Question-answering with Human Feedback.](https://arxiv.org/abs/2112.09332)" 2021

<a id="ref-37"></a>[37] Xu, B. et al. "[ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models.](https://arxiv.org/abs/2305.18323)" 2023

<a id="ref-38"></a>[38] Sharma, M. et al. "[Towards Understanding Sycophancy in Language Models.](https://arxiv.org/abs/2310.13548)" 2023

<a id="ref-39"></a>[39] Greptile. "[AI Code Review Tool Competition (and independent re-runs by Augment, Martian, GitAutoReview).](https://www.greptile.com/competition)" 2025; "[AI Code Review Benchmark 2026.](https://gitautoreview.com/blog/ai-code-review-benchmark-2026)" 2026

<a id="ref-40"></a>[40] "[The Hidden DNA of LLM-Generated JavaScript.](https://arxiv.org/abs/2510.10493)" 2025; DCAN, "[Cross-Language Authorship Attribution of LLM-Generated Code.](https://arxiv.org/abs/2603.04212)" 2026

<a id="ref-41"></a>[41] Gong, Y., Deng, J. "[PlanGuard: Frozen Plans as Control-Flow Integrity Against Indirect Prompt Injection.](https://arxiv.org/abs/2604.10134)" 2026

<a id="ref-42"></a>[42] Beck, K. "[Test-Driven Development: By Example.](https://www.oreilly.com/library/view/test-driven-development/0321146530/)" 2003

<a id="ref-43"></a>[43] Konstantinou, M., Degiovanni, R., Papadakis, M. "[Do LLMs Generate Test Oracles That Capture the Actual or the Expected Program Behaviour?](https://arxiv.org/abs/2410.21136)" 2024

<a id="ref-44"></a>[44] Inozemtseva, L., Holmes, R. "[Coverage Is Not Strongly Correlated With Test Suite Effectiveness.](https://cs.uwaterloo.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf)" ICSE 2014

<a id="ref-45"></a>[45] Just, R., Jalali, D., Inozemtseva, L., Ernst, M. D., Holmes, R., Fraser, G. "[Are Mutants a Valid Substitute for Real Faults in Software Testing?](https://homes.cs.washington.edu/~mernst/pubs/mutants-real-faults-fse2014-abstract.html)" FSE 2014

<a id="ref-46"></a>[46] van Deursen, A., Moonen, L., van den Bergh, A., Kok, G. "[Refactoring Test Code.](http://www.xunitpatterns.com/vanDeursen.html)" XP 2001

<a id="ref-47"></a>[47] Hughes, J. "[Experiences with QuickCheck: Testing the Hard Stuff and Staying Sane.](https://research.chalmers.se/en/publication/232550)" 2016

<a id="ref-48"></a>[48] Tang et al. "[Provenance Blindness in AI-Authored Code Review (Eye-Tracking Study).](https://arxiv.org/abs/2405.16081)" 2024

<a id="ref-49"></a>[49] Cohen, J. (SmartBear / Cisco). "[Best Kept Secrets of Peer Code Review.](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/)" 2006

<a id="ref-50"></a>[50] Variant Systems. "[Vibe Code Anti-Patterns.](https://variantsystems.io/blog/vibe-code-anti-patterns)"; AppXLab. "[Reviewing AI-Generated Code Checklist.](https://blog.appxlab.io/2026/04/06/review-ai-generated-code-checklist/)" 2026

<a id="ref-51"></a>[51] Sadowski, C. et al. "[Modern Code Review: A Case Study at Google.](https://research.google/pubs/pub47025/)" ICSE-SEIP 2018

<a id="ref-52"></a>[52] Semgrep. "[Securing CodeQL with Semgrep / Custom Rule Authoring.](https://semgrep.dev/blog/2024/securing-codeql-with-semgrep/)" 2024

<a id="ref-53"></a>[53] Shinn, N. et al. "[Reflexion: Language Agents with Verbal Reinforcement Learning.](https://arxiv.org/abs/2303.11366)" 2023

<a id="ref-54"></a>[54] Anthropic Engineering. "[Building Effective Agents.](https://www.anthropic.com/engineering/building-effective-agents)"

<a id="ref-55"></a>[55] "[The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction.](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/)" 2017

<a id="ref-56"></a>[56] Shopify Engineering. "[The 25% Technical Debt Rule.](https://shopify.engineering/technical-debt-25-percent-rule)"

<a id="ref-57"></a>[57] Vinta Software. "[The Mikado Method.](https://www.vintasoftware.com/blog/the-mikado-method)"

<a id="ref-58"></a>[58] "[TD Interest Probability: Hotspot Prioritization in Technical Debt Repayment.](https://link.springer.com/article/10.1007/s42979-020-00406-6)" SN Computer Science, 2020

<a id="ref-59"></a>[59] Kim, M., Zimmermann, T., Nagappan, N. "[A Field Study of Refactoring Challenges and Benefits.](https://www.microsoft.com/en-us/research/publication/a-field-study-of-refactoring-challenges-and-benefits/)" FSE 2012

<a id="ref-60"></a>[60] BlueOptima. "[Shifting Left on DORA Change-Failure-Rate: Leading with Maintainability, Not Just Measuring Failure.](https://www.blueoptima.com/ai-access/shifting-left-on-dora-change-failure-rate-leading-with-maintainability-not-just-measuring-failure)" 2025
